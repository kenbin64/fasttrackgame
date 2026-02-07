"""
Persistence Layer - Internal and External Data Storage

═══════════════════════════════════════════════════════════════════
                    SUBSTRATE PERSISTENCE VIA SRL
═══════════════════════════════════════════════════════════════════

The Core needs persistence for substrates:
    - INTERNAL (LocalStore):  Single-user, file-based, edge compute
    - EXTERNAL (CentralStore): Multi-user, server-based, shared state

All persistence is SRL-addressed:
    - Every substrate has an SRL identity
    - Store operations go through ingest()/invoke()
    - The kernel sees only 64-bit math - no storage details

ARCHITECTURE:
    ┌─────────────────────────────────────────────────────────┐
    │                    OUTSIDE WORLD                        │
    │                 (applications, users)                   │
    └─────────────────────────┬───────────────────────────────┘
                              │
    ┌─────────────────────────▼───────────────────────────────┐
    │                      CORE                               │
    │  ┌───────────────────────────────────────────────────┐  │
    │  │               PERSISTENCE LAYER                   │  │
    │  │  ┌─────────────────┐  ┌─────────────────────────┐ │  │
    │  │  │  LocalStore     │  │  CentralStore           │ │  │
    │  │  │  (file/sqlite)  │  │  (redis/postgres/api)   │ │  │
    │  │  └────────┬────────┘  └────────────┬────────────┘ │  │
    │  │           │                        │              │  │
    │  │           └───────────┬────────────┘              │  │
    │  │                       │                           │  │
    │  │                  ┌────▼────┐                      │  │
    │  │                  │  SRL    │                      │  │
    │  │                  │ Address │                      │  │
    │  │                  └────┬────┘                      │  │
    │  └───────────────────────┼───────────────────────────┘  │
    │                          │                              │
    │               ┌──────────▼──────────┐                   │
    │               │  ingest() / invoke() │                   │
    │               └──────────┬──────────┘                   │
    └──────────────────────────┼──────────────────────────────┘
                               │
    ┌──────────────────────────▼──────────────────────────────┐
    │                      KERNEL                             │
    │               (pure 64-bit math only)                   │
    └─────────────────────────────────────────────────────────┘

USAGE:
    from core_v2 import Persistence, LocalStore, CentralStore
    
    # Single user / edge
    local = LocalStore("~/.butterflyfx/data")
    
    # Central server
    central = CentralStore("redis://localhost:6379")
    
    # Persistence manager
    persist = Persistence(internal=local, external=central)
    
    # Save substrate (gets SRL identity)
    srl = persist.save(substrate)
    
    # Load substrate (by SRL)
    substrate = persist.load(srl)
    
    # Sync local to central
    persist.sync()

═══════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
import hashlib
import json
import os
import sqlite3
import struct
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, Iterator, Tuple
from enum import Enum, auto
import base64

# Kernel imports
from kernel_v2 import (
    Substrate, 
    SubstrateIdentity, 
    create_srl_identity
)


__all__ = [
    # Core classes
    'Persistence',
    'Store',
    'LocalStore',
    'CentralStore',
    
    # SRL utilities
    'StoreSRL',
    'SRLReference',
    
    # Types
    'StoreType',
    'SyncMode',
    
    # Errors
    'PersistenceError',
    'StoreNotFoundError',
    'SubstrateNotFoundError',
]


# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════

MASK_64 = 0xFFFFFFFFFFFFFFFF
SCHEMA_VERSION = 1
DEFAULT_LOCAL_PATH = Path.home() / ".butterflyfx" / "data"


# ═══════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════

class StoreType(Enum):
    """Type of data store."""
    LOCAL = auto()      # Single-user, file-based
    CENTRAL = auto()    # Multi-user, server-based
    MEMORY = auto()     # In-memory (ephemeral)


class SyncMode(Enum):
    """Synchronization mode between stores."""
    NONE = auto()           # No sync
    LOCAL_TO_CENTRAL = auto()   # Push local to central
    CENTRAL_TO_LOCAL = auto()   # Pull central to local
    BIDIRECTIONAL = auto()      # Full sync


# ═══════════════════════════════════════════════════════════════════
# ERRORS
# ═══════════════════════════════════════════════════════════════════

class PersistenceError(Exception):
    """Base error for persistence operations."""
    pass


class StoreNotFoundError(PersistenceError):
    """Store not found or not configured."""
    pass


class SubstrateNotFoundError(PersistenceError):
    """Substrate not found in store."""
    pass


# ═══════════════════════════════════════════════════════════════════
# SRL REFERENCE
# ═══════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class SRLReference:
    """
    Reference to a persisted substrate.
    
    This is the SRL address - the way to locate a substrate
    in storage without exposing storage details.
    """
    identity: int               # 64-bit substrate identity
    store_type: StoreType       # Where it's stored
    namespace: str              # Logical grouping
    version: int = 1            # Version for optimistic locking
    created_at: float = field(default_factory=time.time)
    
    @property
    def srl_id(self) -> int:
        """Generate SRL identity from components."""
        # Pack: store_type (8 bits) + namespace_hash (24 bits) + identity (32 bits)
        store_bits = (self.store_type.value & 0xFF) << 56
        namespace_hash = hash(self.namespace) & 0xFFFFFF
        namespace_bits = namespace_hash << 32
        identity_bits = self.identity & 0xFFFFFFFF
        return store_bits | namespace_bits | identity_bits
    
    def to_bytes(self) -> bytes:
        """Serialize reference to bytes."""
        data = {
            'identity': self.identity,
            'store_type': self.store_type.value,
            'namespace': self.namespace,
            'version': self.version,
            'created_at': self.created_at,
        }
        return json.dumps(data).encode('utf-8')
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'SRLReference':
        """Deserialize reference from bytes."""
        obj = json.loads(data.decode('utf-8'))
        return cls(
            identity=obj['identity'],
            store_type=StoreType(obj['store_type']),
            namespace=obj['namespace'],
            version=obj.get('version', 1),
            created_at=obj.get('created_at', time.time()),
        )


@dataclass
class StoreSRL:
    """
    SRL for store connections.
    
    Encodes how to connect to a store without exposing credentials.
    """
    store_type: StoreType
    connection_hash: int    # Hash of connection string (no raw strings)
    namespace: str = "default"
    
    def __post_init__(self):
        """Create SRL identity."""
        self._srl_id = create_srl_identity(
            resource_type=self.store_type.value,
            resource_namespace=hash(self.namespace) & 0xFFFFFF,
            resource_path=self.connection_hash & 0xFFFFFF
        )
    
    @property
    def identity(self) -> int:
        return self._srl_id


# ═══════════════════════════════════════════════════════════════════
# ABSTRACT STORE
# ═══════════════════════════════════════════════════════════════════

class Store(ABC):
    """
    Abstract base class for substrate storage.
    
    Implementations handle the actual storage mechanism.
    All operations return/accept SRL references.
    """
    
    @property
    @abstractmethod
    def store_type(self) -> StoreType:
        """Return the store type."""
        pass
    
    @abstractmethod
    def save(self, identity: int, data: bytes, namespace: str = "default") -> SRLReference:
        """
        Save substrate data to store.
        
        Args:
            identity: 64-bit substrate identity
            data: Serialized substrate data
            namespace: Logical grouping
            
        Returns:
            SRL reference to the stored substrate
        """
        pass
    
    @abstractmethod
    def load(self, ref: SRLReference) -> Optional[bytes]:
        """
        Load substrate data from store.
        
        Args:
            ref: SRL reference
            
        Returns:
            Serialized substrate data or None if not found
        """
        pass
    
    @abstractmethod
    def delete(self, ref: SRLReference) -> bool:
        """
        Delete substrate from store.
        
        Args:
            ref: SRL reference
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists(self, ref: SRLReference) -> bool:
        """Check if substrate exists in store."""
        pass
    
    @abstractmethod
    def list_namespace(self, namespace: str) -> Iterator[SRLReference]:
        """List all substrates in a namespace."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close store connection."""
        pass


# ═══════════════════════════════════════════════════════════════════
# LOCAL STORE (File/SQLite based)
# ═══════════════════════════════════════════════════════════════════

class LocalStore(Store):
    """
    Local file-based storage for single-user scenarios.
    
    Uses SQLite for indexing and file system for data.
    Suitable for:
        - Single user applications
        - Edge/embedded deployments
        - Offline-capable applications
        - Development and testing
    """
    
    def __init__(self, path: Union[str, Path] = DEFAULT_LOCAL_PATH):
        """
        Initialize local store.
        
        Args:
            path: Path to storage directory
        """
        self._path = Path(path).expanduser()
        self._path.mkdir(parents=True, exist_ok=True)
        
        # SQLite for index
        self._db_path = self._path / "substrates.db"
        self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        self._lock = threading.Lock()
        
        self._init_schema()
        
        # Hash for SRL
        self._connection_hash = hash(str(self._path)) & MASK_64
    
    @property
    def store_type(self) -> StoreType:
        return StoreType.LOCAL
    
    @property
    def srl(self) -> StoreSRL:
        """Get SRL for this store."""
        return StoreSRL(
            store_type=StoreType.LOCAL,
            connection_hash=self._connection_hash,
        )
    
    def _init_schema(self):
        """Initialize database schema."""
        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS substrates (
                    identity INTEGER PRIMARY KEY,
                    namespace TEXT NOT NULL,
                    version INTEGER DEFAULT 1,
                    created_at REAL,
                    updated_at REAL,
                    data_path TEXT,
                    size_bytes INTEGER,
                    checksum TEXT
                )
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_namespace 
                ON substrates(namespace)
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            # Store schema version
            cursor.execute('''
                INSERT OR REPLACE INTO metadata (key, value)
                VALUES ('schema_version', ?)
            ''', (str(SCHEMA_VERSION),))
            self._conn.commit()
    
    def _data_path(self, identity: int, namespace: str) -> Path:
        """Get path for substrate data file."""
        ns_path = self._path / namespace
        ns_path.mkdir(exist_ok=True)
        return ns_path / f"{identity:016x}.substrate"
    
    def save(self, identity: int, data: bytes, namespace: str = "default") -> SRLReference:
        """Save substrate to local storage."""
        data_path = self._data_path(identity, namespace)
        checksum = hashlib.sha256(data).hexdigest()
        now = time.time()
        
        # Write data file
        with open(data_path, 'wb') as f:
            f.write(data)
        
        # Update index
        with self._lock:
            cursor = self._conn.cursor()
            
            # Check if exists (for versioning)
            cursor.execute(
                'SELECT version FROM substrates WHERE identity = ?',
                (identity,)
            )
            row = cursor.fetchone()
            version = (row[0] + 1) if row else 1
            
            cursor.execute('''
                INSERT OR REPLACE INTO substrates 
                (identity, namespace, version, created_at, updated_at, 
                 data_path, size_bytes, checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                identity, namespace, version, 
                now if not row else row[0], now,
                str(data_path), len(data), checksum
            ))
            self._conn.commit()
        
        return SRLReference(
            identity=identity,
            store_type=StoreType.LOCAL,
            namespace=namespace,
            version=version,
            created_at=now,
        )
    
    def load(self, ref: SRLReference) -> Optional[bytes]:
        """Load substrate from local storage."""
        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute(
                'SELECT data_path FROM substrates WHERE identity = ? AND namespace = ?',
                (ref.identity, ref.namespace)
            )
            row = cursor.fetchone()
        
        if not row:
            return None
        
        data_path = Path(row[0])
        if not data_path.exists():
            return None
        
        with open(data_path, 'rb') as f:
            return f.read()
    
    def delete(self, ref: SRLReference) -> bool:
        """Delete substrate from local storage."""
        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute(
                'SELECT data_path FROM substrates WHERE identity = ? AND namespace = ?',
                (ref.identity, ref.namespace)
            )
            row = cursor.fetchone()
            
            if not row:
                return False
            
            # Delete data file
            data_path = Path(row[0])
            if data_path.exists():
                data_path.unlink()
            
            # Delete from index
            cursor.execute(
                'DELETE FROM substrates WHERE identity = ? AND namespace = ?',
                (ref.identity, ref.namespace)
            )
            self._conn.commit()
        
        return True
    
    def exists(self, ref: SRLReference) -> bool:
        """Check if substrate exists."""
        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute(
                'SELECT 1 FROM substrates WHERE identity = ? AND namespace = ?',
                (ref.identity, ref.namespace)
            )
            return cursor.fetchone() is not None
    
    def list_namespace(self, namespace: str) -> Iterator[SRLReference]:
        """List all substrates in namespace."""
        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute(
                'SELECT identity, version, created_at FROM substrates WHERE namespace = ?',
                (namespace,)
            )
            rows = cursor.fetchall()
        
        for identity, version, created_at in rows:
            yield SRLReference(
                identity=identity,
                store_type=StoreType.LOCAL,
                namespace=namespace,
                version=version,
                created_at=created_at,
            )
    
    def close(self) -> None:
        """Close database connection."""
        self._conn.close()


# ═══════════════════════════════════════════════════════════════════
# CENTRAL STORE (Server-based)
# ═══════════════════════════════════════════════════════════════════

class CentralStore(Store):
    """
    Central server-based storage for multi-user scenarios.
    
    Supports multiple backends:
        - Redis (in-memory, fast)
        - PostgreSQL (relational, ACID)
        - HTTP API (remote service)
        - SQLite (network-mounted)
    
    Suitable for:
        - Multi-user applications
        - Shared state across instances
        - Server deployments
        - Collaborative systems
    """
    
    def __init__(
        self, 
        connection_string: str,
        namespace: str = "default"
    ):
        """
        Initialize central store.
        
        Args:
            connection_string: Connection URL (redis://, postgres://, http://, sqlite://)
            namespace: Default namespace
        """
        self._connection_string = connection_string
        self._namespace = namespace
        self._connection_hash = hash(connection_string) & MASK_64
        
        # Parse connection type
        if connection_string.startswith('redis://'):
            self._backend = 'redis'
            self._init_redis(connection_string)
        elif connection_string.startswith('postgres://'):
            self._backend = 'postgres'
            self._init_postgres(connection_string)
        elif connection_string.startswith('http://') or connection_string.startswith('https://'):
            self._backend = 'http'
            self._init_http(connection_string)
        elif connection_string.startswith('sqlite://'):
            self._backend = 'sqlite'
            self._init_sqlite(connection_string[9:])  # Strip sqlite://
        elif connection_string.startswith('memory://'):
            self._backend = 'memory'
            self._init_memory()
        else:
            raise PersistenceError(f"Unknown connection type: {connection_string}")
    
    @property
    def store_type(self) -> StoreType:
        return StoreType.CENTRAL
    
    @property
    def srl(self) -> StoreSRL:
        """Get SRL for this store."""
        return StoreSRL(
            store_type=StoreType.CENTRAL,
            connection_hash=self._connection_hash,
            namespace=self._namespace,
        )
    
    def _init_redis(self, url: str):
        """Initialize Redis connection."""
        try:
            import redis
            self._redis = redis.from_url(url)
        except ImportError:
            # Fallback to memory if redis not available
            self._backend = 'memory'
            self._init_memory()
    
    def _init_postgres(self, url: str):
        """Initialize PostgreSQL connection."""
        try:
            import psycopg2
            self._pg_conn = psycopg2.connect(url)
            self._init_pg_schema()
        except ImportError:
            # Fallback to memory
            self._backend = 'memory'
            self._init_memory()
    
    def _init_pg_schema(self):
        """Initialize PostgreSQL schema."""
        cursor = self._pg_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS substrates (
                identity BIGINT PRIMARY KEY,
                namespace TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                data BYTEA,
                checksum TEXT
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_substrates_namespace 
            ON substrates(namespace)
        ''')
        self._pg_conn.commit()
    
    def _init_http(self, url: str):
        """Initialize HTTP client."""
        self._http_base_url = url.rstrip('/')
    
    def _init_sqlite(self, path: str):
        """Initialize SQLite (shared file)."""
        self._sqlite_conn = sqlite3.connect(path, check_same_thread=False)
        self._sqlite_lock = threading.Lock()
        cursor = self._sqlite_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS substrates (
                identity INTEGER PRIMARY KEY,
                namespace TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                created_at REAL,
                updated_at REAL,
                data BLOB,
                checksum TEXT
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_namespace 
            ON substrates(namespace)
        ''')
        self._sqlite_conn.commit()
    
    def _init_memory(self):
        """Initialize in-memory store."""
        self._memory_store: Dict[Tuple[int, str], Tuple[bytes, int, float]] = {}
        self._memory_lock = threading.Lock()
    
    def save(self, identity: int, data: bytes, namespace: str = "default") -> SRLReference:
        """Save to central store."""
        now = time.time()
        
        if self._backend == 'redis':
            return self._save_redis(identity, data, namespace, now)
        elif self._backend == 'postgres':
            return self._save_postgres(identity, data, namespace, now)
        elif self._backend == 'http':
            return self._save_http(identity, data, namespace, now)
        elif self._backend == 'sqlite':
            return self._save_sqlite(identity, data, namespace, now)
        else:  # memory
            return self._save_memory(identity, data, namespace, now)
    
    def _save_memory(self, identity: int, data: bytes, namespace: str, now: float) -> SRLReference:
        """Save to in-memory store."""
        key = (identity, namespace)
        with self._memory_lock:
            existing = self._memory_store.get(key)
            version = (existing[1] + 1) if existing else 1
            self._memory_store[key] = (data, version, now)
        
        return SRLReference(
            identity=identity,
            store_type=StoreType.CENTRAL,
            namespace=namespace,
            version=version,
            created_at=now,
        )
    
    def _save_redis(self, identity: int, data: bytes, namespace: str, now: float) -> SRLReference:
        """Save to Redis."""
        key = f"{namespace}:{identity}"
        version_key = f"{key}:version"
        
        pipe = self._redis.pipeline()
        pipe.incr(version_key)
        pipe.set(key, data)
        pipe.set(f"{key}:created", now)
        results = pipe.execute()
        version = results[0]
        
        return SRLReference(
            identity=identity,
            store_type=StoreType.CENTRAL,
            namespace=namespace,
            version=version,
            created_at=now,
        )
    
    def _save_sqlite(self, identity: int, data: bytes, namespace: str, now: float) -> SRLReference:
        """Save to SQLite."""
        checksum = hashlib.sha256(data).hexdigest()
        
        with self._sqlite_lock:
            cursor = self._sqlite_conn.cursor()
            
            cursor.execute(
                'SELECT version FROM substrates WHERE identity = ? AND namespace = ?',
                (identity, namespace)
            )
            row = cursor.fetchone()
            version = (row[0] + 1) if row else 1
            
            cursor.execute('''
                INSERT OR REPLACE INTO substrates 
                (identity, namespace, version, created_at, updated_at, data, checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (identity, namespace, version, now, now, data, checksum))
            self._sqlite_conn.commit()
        
        return SRLReference(
            identity=identity,
            store_type=StoreType.CENTRAL,
            namespace=namespace,
            version=version,
            created_at=now,
        )
    
    def _save_postgres(self, identity: int, data: bytes, namespace: str, now: float) -> SRLReference:
        """Save to PostgreSQL."""
        cursor = self._pg_conn.cursor()
        cursor.execute('''
            INSERT INTO substrates (identity, namespace, data, checksum)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (identity) DO UPDATE SET
                data = EXCLUDED.data,
                version = substrates.version + 1,
                updated_at = NOW()
            RETURNING version
        ''', (identity, namespace, data, hashlib.sha256(data).hexdigest()))
        version = cursor.fetchone()[0]
        self._pg_conn.commit()
        
        return SRLReference(
            identity=identity,
            store_type=StoreType.CENTRAL,
            namespace=namespace,
            version=version,
            created_at=now,
        )
    
    def _save_http(self, identity: int, data: bytes, namespace: str, now: float) -> SRLReference:
        """Save via HTTP API."""
        import urllib.request
        
        url = f"{self._http_base_url}/substrates/{namespace}/{identity}"
        request = urllib.request.Request(
            url,
            data=data,
            method='PUT',
            headers={'Content-Type': 'application/octet-stream'}
        )
        
        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read())
            version = result.get('version', 1)
        
        return SRLReference(
            identity=identity,
            store_type=StoreType.CENTRAL,
            namespace=namespace,
            version=version,
            created_at=now,
        )
    
    def load(self, ref: SRLReference) -> Optional[bytes]:
        """Load from central store."""
        if self._backend == 'memory':
            return self._load_memory(ref)
        elif self._backend == 'redis':
            return self._load_redis(ref)
        elif self._backend == 'sqlite':
            return self._load_sqlite(ref)
        elif self._backend == 'postgres':
            return self._load_postgres(ref)
        else:
            return self._load_http(ref)
    
    def _load_memory(self, ref: SRLReference) -> Optional[bytes]:
        """Load from memory."""
        key = (ref.identity, ref.namespace)
        with self._memory_lock:
            entry = self._memory_store.get(key)
            return entry[0] if entry else None
    
    def _load_redis(self, ref: SRLReference) -> Optional[bytes]:
        """Load from Redis."""
        key = f"{ref.namespace}:{ref.identity}"
        return self._redis.get(key)
    
    def _load_sqlite(self, ref: SRLReference) -> Optional[bytes]:
        """Load from SQLite."""
        with self._sqlite_lock:
            cursor = self._sqlite_conn.cursor()
            cursor.execute(
                'SELECT data FROM substrates WHERE identity = ? AND namespace = ?',
                (ref.identity, ref.namespace)
            )
            row = cursor.fetchone()
            return row[0] if row else None
    
    def _load_postgres(self, ref: SRLReference) -> Optional[bytes]:
        """Load from PostgreSQL."""
        cursor = self._pg_conn.cursor()
        cursor.execute(
            'SELECT data FROM substrates WHERE identity = %s AND namespace = %s',
            (ref.identity, ref.namespace)
        )
        row = cursor.fetchone()
        return bytes(row[0]) if row else None
    
    def _load_http(self, ref: SRLReference) -> Optional[bytes]:
        """Load via HTTP API."""
        import urllib.request
        import urllib.error
        
        url = f"{self._http_base_url}/substrates/{ref.namespace}/{ref.identity}"
        request = urllib.request.Request(url, method='GET')
        
        try:
            with urllib.request.urlopen(request) as response:
                return response.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise
    
    def delete(self, ref: SRLReference) -> bool:
        """Delete from central store."""
        if self._backend == 'memory':
            key = (ref.identity, ref.namespace)
            with self._memory_lock:
                return self._memory_store.pop(key, None) is not None
        elif self._backend == 'redis':
            key = f"{ref.namespace}:{ref.identity}"
            return bool(self._redis.delete(key))
        elif self._backend == 'sqlite':
            with self._sqlite_lock:
                cursor = self._sqlite_conn.cursor()
                cursor.execute(
                    'DELETE FROM substrates WHERE identity = ? AND namespace = ?',
                    (ref.identity, ref.namespace)
                )
                self._sqlite_conn.commit()
                return cursor.rowcount > 0
        elif self._backend == 'postgres':
            cursor = self._pg_conn.cursor()
            cursor.execute(
                'DELETE FROM substrates WHERE identity = %s AND namespace = %s',
                (ref.identity, ref.namespace)
            )
            self._pg_conn.commit()
            return cursor.rowcount > 0
        else:
            import urllib.request
            url = f"{self._http_base_url}/substrates/{ref.namespace}/{ref.identity}"
            request = urllib.request.Request(url, method='DELETE')
            with urllib.request.urlopen(request) as response:
                return response.status == 200
    
    def exists(self, ref: SRLReference) -> bool:
        """Check if substrate exists."""
        if self._backend == 'memory':
            return (ref.identity, ref.namespace) in self._memory_store
        elif self._backend == 'redis':
            return bool(self._redis.exists(f"{ref.namespace}:{ref.identity}"))
        elif self._backend == 'sqlite':
            with self._sqlite_lock:
                cursor = self._sqlite_conn.cursor()
                cursor.execute(
                    'SELECT 1 FROM substrates WHERE identity = ? AND namespace = ?',
                    (ref.identity, ref.namespace)
                )
                return cursor.fetchone() is not None
        elif self._backend == 'postgres':
            cursor = self._pg_conn.cursor()
            cursor.execute(
                'SELECT 1 FROM substrates WHERE identity = %s AND namespace = %s',
                (ref.identity, ref.namespace)
            )
            return cursor.fetchone() is not None
        else:
            import urllib.request
            import urllib.error
            url = f"{self._http_base_url}/substrates/{ref.namespace}/{ref.identity}"
            request = urllib.request.Request(url, method='HEAD')
            try:
                with urllib.request.urlopen(request):
                    return True
            except urllib.error.HTTPError:
                return False
    
    def list_namespace(self, namespace: str) -> Iterator[SRLReference]:
        """List all substrates in namespace."""
        if self._backend == 'memory':
            with self._memory_lock:
                for (identity, ns), (_, version, created) in self._memory_store.items():
                    if ns == namespace:
                        yield SRLReference(identity, StoreType.CENTRAL, namespace, version, created)
        elif self._backend == 'redis':
            pattern = f"{namespace}:*"
            for key in self._redis.scan_iter(pattern):
                key_str = key.decode() if isinstance(key, bytes) else key
                if ':version' not in key_str and ':created' not in key_str:
                    identity = int(key_str.split(':')[1])
                    yield SRLReference(identity, StoreType.CENTRAL, namespace)
        elif self._backend == 'sqlite':
            with self._sqlite_lock:
                cursor = self._sqlite_conn.cursor()
                cursor.execute(
                    'SELECT identity, version, created_at FROM substrates WHERE namespace = ?',
                    (namespace,)
                )
                for identity, version, created in cursor.fetchall():
                    yield SRLReference(identity, StoreType.CENTRAL, namespace, version, created)
        elif self._backend == 'postgres':
            cursor = self._pg_conn.cursor()
            cursor.execute(
                'SELECT identity, version, EXTRACT(EPOCH FROM created_at) FROM substrates WHERE namespace = %s',
                (namespace,)
            )
            for identity, version, created in cursor.fetchall():
                yield SRLReference(identity, StoreType.CENTRAL, namespace, version, created)
    
    def close(self) -> None:
        """Close connection."""
        if self._backend == 'redis' and hasattr(self, '_redis'):
            self._redis.close()
        elif self._backend == 'postgres' and hasattr(self, '_pg_conn'):
            self._pg_conn.close()
        elif self._backend == 'sqlite' and hasattr(self, '_sqlite_conn'):
            self._sqlite_conn.close()


# ═══════════════════════════════════════════════════════════════════
# PERSISTENCE MANAGER
# ═══════════════════════════════════════════════════════════════════

class Persistence:
    """
    Unified persistence manager for substrates.
    
    Manages both internal (local) and external (central) stores.
    All operations go through SRL addressing.
    
    USAGE:
        # Create stores
        local = LocalStore("~/.butterflyfx/data")
        central = CentralStore("memory://")  # or redis://, postgres://
        
        # Create persistence manager
        persist = Persistence(internal=local, external=central)
        
        # Save substrate
        ref = persist.save(my_substrate, namespace="cars")
        
        # Load substrate
        data = persist.load(ref)
        
        # Sync between stores
        persist.sync(SyncMode.LOCAL_TO_CENTRAL)
    """
    
    def __init__(
        self,
        internal: Optional[LocalStore] = None,
        external: Optional[CentralStore] = None,
        default_store: StoreType = StoreType.LOCAL
    ):
        """
        Initialize persistence manager.
        
        Args:
            internal: Local store for single-user data
            external: Central store for shared data
            default_store: Which store to use by default
        """
        self._internal = internal
        self._external = external
        self._default_store = default_store
        
        # Create default local store if none provided
        if internal is None and default_store == StoreType.LOCAL:
            self._internal = LocalStore()
    
    @property
    def internal(self) -> Optional[LocalStore]:
        """Get internal (local) store."""
        return self._internal
    
    @property
    def external(self) -> Optional[CentralStore]:
        """Get external (central) store."""
        return self._external
    
    def _get_store(self, store_type: Optional[StoreType] = None) -> Store:
        """Get the appropriate store."""
        store_type = store_type or self._default_store
        
        if store_type == StoreType.LOCAL:
            if self._internal is None:
                raise StoreNotFoundError("Local store not configured")
            return self._internal
        else:
            if self._external is None:
                raise StoreNotFoundError("Central store not configured")
            return self._external
    
    def save(
        self,
        substrate: Substrate,
        namespace: str = "default",
        store_type: Optional[StoreType] = None
    ) -> SRLReference:
        """
        Save substrate to store.
        
        Args:
            substrate: The substrate to save
            namespace: Logical grouping
            store_type: Which store to use (default: configured default)
            
        Returns:
            SRL reference to the stored substrate
        """
        store = self._get_store(store_type)
        
        # Serialize substrate
        identity = int(substrate.identity)
        data = self._serialize_substrate(substrate)
        
        return store.save(identity, data, namespace)
    
    def save_raw(
        self,
        identity: int,
        data: bytes,
        namespace: str = "default",
        store_type: Optional[StoreType] = None
    ) -> SRLReference:
        """
        Save raw data to store.
        
        Args:
            identity: 64-bit substrate identity
            data: Raw bytes to store
            namespace: Logical grouping
            store_type: Which store to use
            
        Returns:
            SRL reference
        """
        store = self._get_store(store_type)
        return store.save(identity, data, namespace)
    
    def load(self, ref: SRLReference) -> Optional[bytes]:
        """
        Load substrate data by SRL reference.
        
        Args:
            ref: SRL reference to load
            
        Returns:
            Raw bytes or None if not found
        """
        store = self._get_store(ref.store_type)
        return store.load(ref)
    
    def load_substrate(self, ref: SRLReference) -> Optional[Substrate]:
        """
        Load and deserialize substrate.
        
        Args:
            ref: SRL reference
            
        Returns:
            Substrate or None if not found
        """
        data = self.load(ref)
        if data is None:
            return None
        return self._deserialize_substrate(data)
    
    def delete(self, ref: SRLReference) -> bool:
        """Delete substrate by reference."""
        store = self._get_store(ref.store_type)
        return store.delete(ref)
    
    def exists(self, ref: SRLReference) -> bool:
        """Check if substrate exists."""
        store = self._get_store(ref.store_type)
        return store.exists(ref)
    
    def list(
        self,
        namespace: str = "default",
        store_type: Optional[StoreType] = None
    ) -> Iterator[SRLReference]:
        """List all substrates in namespace."""
        store = self._get_store(store_type)
        return store.list_namespace(namespace)
    
    def sync(
        self,
        mode: SyncMode = SyncMode.BIDIRECTIONAL,
        namespace: str = "default"
    ) -> Dict[str, int]:
        """
        Synchronize between internal and external stores.
        
        Args:
            mode: Sync direction
            namespace: Namespace to sync
            
        Returns:
            Stats dict with counts of synced items
        """
        if self._internal is None or self._external is None:
            raise PersistenceError("Both internal and external stores required for sync")
        
        stats = {'uploaded': 0, 'downloaded': 0, 'conflicts': 0}
        
        if mode in (SyncMode.LOCAL_TO_CENTRAL, SyncMode.BIDIRECTIONAL):
            # Push local to central
            for ref in self._internal.list_namespace(namespace):
                data = self._internal.load(ref)
                if data:
                    self._external.save(ref.identity, data, namespace)
                    stats['uploaded'] += 1
        
        if mode in (SyncMode.CENTRAL_TO_LOCAL, SyncMode.BIDIRECTIONAL):
            # Pull central to local
            for ref in self._external.list_namespace(namespace):
                data = self._external.load(ref)
                if data:
                    self._internal.save(ref.identity, data, namespace)
                    stats['downloaded'] += 1
        
        return stats
    
    def _serialize_substrate(self, substrate: Substrate) -> bytes:
        """Serialize substrate to bytes."""
        identity = int(substrate.identity)
        value = substrate()
        
        # Simple serialization: 8 bytes identity + JSON value
        identity_bytes = struct.pack('>Q', identity)
        value_bytes = json.dumps(value).encode('utf-8')
        
        return identity_bytes + value_bytes
    
    def _deserialize_substrate(self, data: bytes) -> Substrate:
        """Deserialize substrate from bytes."""
        identity_int = struct.unpack('>Q', data[:8])[0]
        value = json.loads(data[8:].decode('utf-8'))
        
        identity = SubstrateIdentity(identity_int)
        return Substrate(identity, lambda v=value: v)
    
    def close(self) -> None:
        """Close all stores."""
        if self._internal:
            self._internal.close()
        if self._external:
            self._external.close()


# ═══════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def create_local_store(path: Union[str, Path] = DEFAULT_LOCAL_PATH) -> LocalStore:
    """Create a local store instance."""
    return LocalStore(path)


def create_central_store(connection_string: str) -> CentralStore:
    """Create a central store instance."""
    return CentralStore(connection_string)


def create_memory_store() -> CentralStore:
    """Create an in-memory central store (for testing)."""
    return CentralStore("memory://")
