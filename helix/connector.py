"""
SRL Connector - Lazy Loading with Credential Validation

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)

SRLs are PASSIVE LIBRARY CARDS:
    - They hold location + credentials + protocol
    - They DON'T connect until invoked (lazy loading)
    - They only connect to what they have permission for
    
The connector validates credentials and establishes connections
only when data is actually requested.

EXAMPLE:
    # Create SRL - NO connection yet
    db = srl("db.mysql/users", host="localhost", user="admin", password="xxx")
    
    # Still no connection - just a reference
    user_query = db.child("admins")
    
    # NOW connects, validates credentials, returns data
    data = user_query.get()
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Callable, Protocol
from dataclasses import dataclass, field
from enum import Enum, auto
import time


# =============================================================================
# CONNECTION STATE
# =============================================================================

class ConnectionState(Enum):
    """State of an SRL connection."""
    PENDING = auto()      # Never connected (lazy - default state)
    CONNECTING = auto()   # Currently establishing connection
    CONNECTED = auto()    # Active connection
    DISCONNECTED = auto() # Was connected, now closed
    FAILED = auto()       # Connection attempt failed
    UNAUTHORIZED = auto() # Credentials invalid


# =============================================================================
# CONNECTOR PROTOCOL
# =============================================================================

class DataSourceConnector(Protocol):
    """Protocol for data source connectors."""
    
    def connect(self, credentials: Dict[str, Any]) -> bool:
        """Establish connection. Returns True if successful."""
        ...
    
    def disconnect(self) -> None:
        """Close connection."""
        ...
    
    def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Validate credentials without connecting."""
        ...
    
    def get(self, path: str) -> Any:
        """Get data at path."""
        ...
    
    def set(self, path: str, value: Any) -> None:
        """Set data at path."""
        ...
    
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        ...


# =============================================================================
# LOCAL CONNECTOR - In-memory storage
# =============================================================================

class LocalConnector:
    """Connector for local in-memory storage."""
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._connected = True  # Always connected for local
    
    def connect(self, credentials: Dict[str, Any]) -> bool:
        return True  # Local always succeeds
    
    def disconnect(self) -> None:
        pass  # No-op for local
    
    def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        return True  # Local doesn't need credentials
    
    def get(self, path: str) -> Any:
        return self._data.get(path)
    
    def set(self, path: str, value: Any) -> None:
        self._data[path] = value
    
    def exists(self, path: str) -> bool:
        return path in self._data


# =============================================================================
# LAZY SRL - Passive library card with lazy connection
# =============================================================================

@dataclass
class LazySRL:
    """
    A lazy SRL that only connects when data is accessed.
    
    This is the "library card" - it holds all info needed to
    access data, but doesn't actually connect until invoked.
    
    Usage:
        # Create SRL - NO connection yet
        srl = LazySRL.create("db.mysql/users", host="localhost", password="xxx")
        
        # Check if we COULD connect (validates credentials)
        if srl.can_access:
            # NOW actually connect and get data
            data = srl.get()
    """
    
    # Address components
    domain: str = "local"
    spiral: int = 0
    level: int = 6
    path: str = ""
    
    # Credentials (stored but not used until invoked)
    credentials: Dict[str, Any] = field(default_factory=dict)
    protocol: str = "internal"
    
    # Lazy state
    _state: ConnectionState = field(default=ConnectionState.PENDING, repr=False)
    _connector: Optional[DataSourceConnector] = field(default=None, repr=False)
    _last_access: Optional[float] = field(default=None, repr=False)
    _cache: Optional[Any] = field(default=None, repr=False)
    _cache_ttl: float = field(default=60.0, repr=False)  # Cache TTL in seconds
    
    @classmethod
    def create(cls, address: str, **credentials) -> 'LazySRL':
        """
        Create a lazy SRL from address string.
        
        NO CONNECTION IS MADE - this is just creating a reference.
        """
        # Parse address
        parts = address.replace("srl://", "").split("/")
        domain = parts[0] if parts else "local"
        
        rest = parts[1] if len(parts) > 1 else ""
        path_parts = rest.split(".")
        
        spiral = int(path_parts[0]) if path_parts and path_parts[0].isdigit() else 0
        level = int(path_parts[1]) if len(path_parts) > 1 and path_parts[1].isdigit() else 6
        path = ".".join(path_parts[2:]) if len(path_parts) > 2 else ""
        
        return cls(
            domain=domain,
            spiral=spiral,
            level=level,
            path=path,
            credentials=credentials,
        )
    
    @property
    def address(self) -> str:
        """Full SRL address string."""
        base = f"srl://{self.domain}/{self.spiral}.{self.level}"
        if self.path:
            base += f".{self.path}"
        return base
    
    @property
    def state(self) -> ConnectionState:
        """Current connection state."""
        return self._state
    
    @property
    def is_connected(self) -> bool:
        """True if currently connected."""
        return self._state == ConnectionState.CONNECTED
    
    @property
    def is_lazy(self) -> bool:
        """True if never connected (still in lazy/pending state)."""
        return self._state == ConnectionState.PENDING
    
    # =========================================================================
    # CREDENTIAL VALIDATION
    # =========================================================================
    
    @property
    def has_credentials(self) -> bool:
        """Check if credentials are provided."""
        # Local domain doesn't need credentials
        if self.domain == "local":
            return True
        
        # Check for required credential fields
        return bool(self.credentials)
    
    @property
    def can_access(self) -> bool:
        """
        Check if we COULD access this resource.
        
        Validates credentials WITHOUT actually connecting.
        """
        if self.domain == "local":
            return True
        
        if not self.has_credentials:
            return False
        
        # Get connector and validate
        connector = self._get_connector()
        return connector.validate_credentials(self.credentials)
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate credentials and return (success, message).
        
        Does NOT connect - just validates.
        """
        if self.domain == "local":
            return (True, "Local access always permitted")
        
        if not self.has_credentials:
            return (False, "No credentials provided")
        
        connector = self._get_connector()
        if connector.validate_credentials(self.credentials):
            return (True, "Credentials valid")
        else:
            return (False, "Invalid credentials")
    
    # =========================================================================
    # LAZY CONNECTION
    # =========================================================================
    
    def _get_connector(self) -> DataSourceConnector:
        """Get or create connector for this domain."""
        if self._connector is not None:
            return self._connector
        
        # Create connector based on domain
        if self.domain == "local":
            self._connector = LocalConnector()
        else:
            # For external domains, use the connector registry
            self._connector = ConnectorRegistry.get_connector(self.domain)
            if self._connector is None:
                self._connector = LocalConnector()  # Fallback
        
        return self._connector
    
    def _ensure_connected(self) -> bool:
        """
        Ensure we're connected. Returns True if connected.
        
        This is where the LAZY connection happens.
        """
        if self._state == ConnectionState.CONNECTED:
            return True
        
        if self._state == ConnectionState.UNAUTHORIZED:
            return False
        
        self._state = ConnectionState.CONNECTING
        connector = self._get_connector()
        
        try:
            if connector.connect(self.credentials):
                self._state = ConnectionState.CONNECTED
                return True
            else:
                self._state = ConnectionState.FAILED
                return False
        except PermissionError:
            self._state = ConnectionState.UNAUTHORIZED
            return False
        except Exception:
            self._state = ConnectionState.FAILED
            return False
    
    # =========================================================================
    # DATA ACCESS - Connection happens HERE
    # =========================================================================
    
    def get(self, default: Any = None) -> Any:
        """
        Get data at this SRL location.
        
        THIS IS WHERE LAZY LOADING HAPPENS.
        Connection is established on first access.
        """
        # Check cache first
        if self._cache is not None and self._last_access is not None:
            if time.time() - self._last_access < self._cache_ttl:
                return self._cache
        
        # Ensure connected (lazy connection)
        if not self._ensure_connected():
            return default
        
        # Get data
        connector = self._get_connector()
        try:
            value = connector.get(self.path)
            self._cache = value
            self._last_access = time.time()
            return value if value is not None else default
        except Exception:
            return default
    
    def set(self, value: Any) -> bool:
        """
        Set data at this SRL location.
        
        Connection established if needed.
        """
        if not self._ensure_connected():
            return False
        
        connector = self._get_connector()
        try:
            connector.set(self.path, value)
            self._cache = value
            self._last_access = time.time()
            return True
        except Exception:
            return False
    
    def exists(self) -> bool:
        """Check if data exists at this location."""
        if not self._ensure_connected():
            return False
        
        return self._get_connector().exists(self.path)
    
    # =========================================================================
    # NAVIGATION - Returns new lazy SRLs (no connection)
    # =========================================================================
    
    def child(self, name: str) -> 'LazySRL':
        """
        Get child SRL. NO CONNECTION - just creates a new lazy reference.
        """
        new_path = f"{self.path}.{name}" if self.path else name
        return LazySRL(
            domain=self.domain,
            spiral=self.spiral,
            level=self.level,
            path=new_path,
            credentials=self.credentials,
            protocol=self.protocol,
        )
    
    def at_level(self, level: int) -> 'LazySRL':
        """Get SRL at different level. NO CONNECTION."""
        return LazySRL(
            domain=self.domain,
            spiral=self.spiral,
            level=level,
            path=self.path,
            credentials=self.credentials,
            protocol=self.protocol,
        )
    
    def at_spiral(self, spiral: int) -> 'LazySRL':
        """Get SRL at different spiral. NO CONNECTION."""
        return LazySRL(
            domain=self.domain,
            spiral=spiral,
            level=self.level,
            path=self.path,
            credentials=self.credentials,
            protocol=self.protocol,
        )
    
    def with_credentials(self, **creds) -> 'LazySRL':
        """Add/update credentials. NO CONNECTION."""
        new_creds = {**self.credentials, **creds}
        return LazySRL(
            domain=self.domain,
            spiral=self.spiral,
            level=self.level,
            path=self.path,
            credentials=new_creds,
            protocol=self.protocol,
        )
    
    # =========================================================================
    # CONNECTION MANAGEMENT
    # =========================================================================
    
    def disconnect(self) -> None:
        """Explicitly disconnect."""
        if self._connector is not None:
            self._connector.disconnect()
            self._state = ConnectionState.DISCONNECTED
    
    def clear_cache(self) -> None:
        """Clear cached data."""
        self._cache = None
        self._last_access = None
    
    def __str__(self) -> str:
        return f"{self.address} [{self._state.name}]"


# =============================================================================
# CONNECTOR REGISTRY - Manages connectors for different domains
# =============================================================================

class ConnectorRegistry:
    """
    Registry of connectors for different domains.
    
    Developers can register custom connectors for external data sources.
    """
    
    _connectors: Dict[str, type] = {}
    _instances: Dict[str, DataSourceConnector] = {}
    
    # Default local connector
    _local = LocalConnector()
    
    @classmethod
    def register(cls, domain: str, connector_class: type) -> None:
        """
        Register a connector class for a domain.
        
        Usage:
            ConnectorRegistry.register("db.mysql", MySQLConnector)
            ConnectorRegistry.register("api.stripe", StripeConnector)
        """
        cls._connectors[domain] = connector_class
    
    @classmethod
    def get_connector(cls, domain: str) -> DataSourceConnector:
        """Get connector for domain."""
        if domain == "local":
            return cls._local
        
        # Check for existing instance
        if domain in cls._instances:
            return cls._instances[domain]
        
        # Create new instance
        if domain in cls._connectors:
            instance = cls._connectors[domain]()
            cls._instances[domain] = instance
            return instance
        
        # Fallback to local
        return cls._local
    
    @classmethod
    def list_domains(cls) -> list:
        """List registered domains."""
        return ["local"] + list(cls._connectors.keys())


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def lazy_srl(address: str, **credentials) -> LazySRL:
    """
    Create a lazy SRL.
    
    NO CONNECTION is made - this is just creating a reference.
    Connection happens when .get() is called.
    
    Usage:
        # Create reference (no connection)
        db = lazy_srl("db.mysql/users", host="localhost", password="xxx")
        
        # Check credentials (no connection)
        if db.can_access:
            # NOW connects and gets data
            users = db.get()
    """
    return LazySRL.create(address, **credentials)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'ConnectionState',
    'DataSourceConnector',
    'LocalConnector',
    'LazySRL',
    'ConnectorRegistry',
    'lazy_srl',
]
