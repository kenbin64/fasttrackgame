"""
SRL - Substrate Reference Locator (Core Implementation)

═══════════════════════════════════════════════════════════════════
                    CONNECTION DEVICE
═══════════════════════════════════════════════════════════════════

SRL is a CORE function, NOT a kernel function.

The kernel only contains pure math - it cannot be a server or
connector because it is pure mathematical substrate.

SRL is a connection device that:
    - Holds credentials, keys, protocols, queries
    - Is bit-counted and encrypted
    - Connects to internal datasources (files, folders)
    - Connects to external datasources (APIs, databases, streams)
    
FLOW:
    1. SRL specification is ingested as a substrate (the data)
    2. Core creates the SRL connection device
    3. Core acts as server (socket, HTTP)
    4. SRL transmits and makes connections
    5. On return, data goes through ingest() into kernel as substrate

The kernel's _srl.py is just the reference locator (domain+path+identity).
This module adds all connection, credential, and transport logic.

═══════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
import hashlib
import hmac
import json
import socket
import ssl
import struct
import threading
import time
import urllib.request
import urllib.parse
from typing import (
    Any, Dict, List, Optional, Union, Callable, 
    Tuple, BinaryIO, Iterator, TypeVar
)
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum, auto
from pathlib import Path
import os
import base64

# Kernel reference locator (pure math only)
from kernel_v2 import SRL as KernelSRL, create_srl_identity, SubstrateIdentity


__all__ = [
    # Connection device
    'SRL',
    'SRLConnection',
    'SRLResult',
    
    # Protocols
    'Protocol',
    'FileProtocol',
    'HTTPProtocol',
    'SocketProtocol',
    'DatabaseProtocol',
    
    # Credentials
    'Credentials',
    'APIKey',
    'BasicAuth',
    'TokenAuth',
    'CertAuth',
    
    # Configuration
    'SRLConfig',
    
    # Errors
    'SRLError',
    'ConnectionError',
    'AuthenticationError',
]


# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════

MASK_64 = 0xFFFFFFFFFFFFFFFF
DEFAULT_TIMEOUT = 30.0
MAX_PAYLOAD_SIZE = 100 * 1024 * 1024  # 100MB


# ═══════════════════════════════════════════════════════════════════
# ERRORS
# ═══════════════════════════════════════════════════════════════════

class SRLError(Exception):
    """Base error for SRL operations."""
    def __init__(self, message: str, code: int = 0):
        super().__init__(message)
        self.code = code


class ConnectionError(SRLError):
    """Connection failed."""
    pass


class AuthenticationError(SRLError):
    """Authentication failed."""
    pass


# ═══════════════════════════════════════════════════════════════════
# CREDENTIALS
# ═══════════════════════════════════════════════════════════════════

@dataclass
class Credentials(ABC):
    """Base class for credentials."""
    
    @abstractmethod
    def to_headers(self) -> Dict[str, str]:
        """Convert to HTTP headers."""
        pass
    
    @abstractmethod
    def encrypt(self, key: bytes) -> bytes:
        """Encrypt credentials for storage."""
        pass
    
    @classmethod
    @abstractmethod
    def decrypt(cls, data: bytes, key: bytes) -> 'Credentials':
        """Decrypt credentials from storage."""
        pass


@dataclass
class APIKey(Credentials):
    """API key authentication."""
    key: str
    header_name: str = "X-API-Key"
    
    def to_headers(self) -> Dict[str, str]:
        return {self.header_name: self.key}
    
    def encrypt(self, key: bytes) -> bytes:
        # Simple XOR encryption for demonstration
        key_data = self.key.encode('utf-8')
        encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(key_data))
        return base64.b64encode(encrypted)
    
    @classmethod
    def decrypt(cls, data: bytes, key: bytes) -> 'APIKey':
        encrypted = base64.b64decode(data)
        decrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(encrypted))
        return cls(key=decrypted.decode('utf-8'))


@dataclass
class BasicAuth(Credentials):
    """HTTP Basic authentication."""
    username: str
    password: str
    
    def to_headers(self) -> Dict[str, str]:
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return {"Authorization": f"Basic {encoded}"}
    
    def encrypt(self, key: bytes) -> bytes:
        data = f"{self.username}:{self.password}".encode('utf-8')
        encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
        return base64.b64encode(encrypted)
    
    @classmethod
    def decrypt(cls, data: bytes, key: bytes) -> 'BasicAuth':
        encrypted = base64.b64decode(data)
        decrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(encrypted))
        username, password = decrypted.decode('utf-8').split(':', 1)
        return cls(username=username, password=password)


@dataclass
class TokenAuth(Credentials):
    """Bearer token authentication."""
    token: str
    token_type: str = "Bearer"
    
    def to_headers(self) -> Dict[str, str]:
        return {"Authorization": f"{self.token_type} {self.token}"}
    
    def encrypt(self, key: bytes) -> bytes:
        encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(self.token.encode('utf-8')))
        return base64.b64encode(encrypted)
    
    @classmethod
    def decrypt(cls, data: bytes, key: bytes) -> 'TokenAuth':
        encrypted = base64.b64decode(data)
        decrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(encrypted))
        return cls(token=decrypted.decode('utf-8'))


@dataclass
class CertAuth(Credentials):
    """Certificate-based authentication."""
    cert_path: str
    key_path: str
    ca_path: Optional[str] = None
    
    def to_headers(self) -> Dict[str, str]:
        return {}  # Certs are used at connection level
    
    def encrypt(self, key: bytes) -> bytes:
        data = f"{self.cert_path}|{self.key_path}|{self.ca_path or ''}".encode('utf-8')
        encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
        return base64.b64encode(encrypted)
    
    @classmethod
    def decrypt(cls, data: bytes, key: bytes) -> 'CertAuth':
        encrypted = base64.b64decode(data)
        decrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(encrypted))
        parts = decrypted.decode('utf-8').split('|')
        return cls(cert_path=parts[0], key_path=parts[1], ca_path=parts[2] or None)


# ═══════════════════════════════════════════════════════════════════
# PROTOCOLS
# ═══════════════════════════════════════════════════════════════════

class Protocol(ABC):
    """Base class for connection protocols."""
    
    @abstractmethod
    def connect(self, srl: 'SRL') -> 'SRLConnection':
        """Establish connection."""
        pass
    
    @abstractmethod
    def disconnect(self, connection: 'SRLConnection') -> None:
        """Close connection."""
        pass
    
    @abstractmethod
    def fetch(self, connection: 'SRLConnection', query: Optional[str] = None) -> bytes:
        """Fetch data from the connection."""
        pass
    
    @abstractmethod
    def send(self, connection: 'SRLConnection', data: bytes) -> bool:
        """Send data through the connection."""
        pass


@dataclass
class FileProtocol(Protocol):
    """Local file system protocol."""
    base_path: Optional[str] = None
    
    def connect(self, srl: 'SRL') -> 'SRLConnection':
        path = srl.path
        if self.base_path:
            path = os.path.join(self.base_path, path.lstrip('/'))
        
        if not os.path.exists(path):
            raise ConnectionError(f"Path not found: {path}")
        
        return SRLConnection(
            srl=srl,
            protocol=self,
            handle=path,
            connected=True
        )
    
    def disconnect(self, connection: 'SRLConnection') -> None:
        connection.connected = False
    
    def fetch(self, connection: 'SRLConnection', query: Optional[str] = None) -> bytes:
        path = connection.handle
        
        if os.path.isfile(path):
            with open(path, 'rb') as f:
                return f.read()
        elif os.path.isdir(path):
            # Return directory listing as JSON
            entries = os.listdir(path)
            return json.dumps(entries).encode('utf-8')
        else:
            raise SRLError(f"Cannot read: {path}")
    
    def send(self, connection: 'SRLConnection', data: bytes) -> bool:
        path = connection.handle
        with open(path, 'wb') as f:
            f.write(data)
        return True


@dataclass
class HTTPProtocol(Protocol):
    """HTTP/HTTPS protocol."""
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: float = DEFAULT_TIMEOUT
    verify_ssl: bool = True
    
    def connect(self, srl: 'SRL') -> 'SRLConnection':
        # Build URL from SRL
        scheme = "https" if srl.config.use_ssl else "http"
        port = srl.config.port or (443 if srl.config.use_ssl else 80)
        url = f"{scheme}://{srl.domain}:{port}{srl.path}"
        
        return SRLConnection(
            srl=srl,
            protocol=self,
            handle=url,
            connected=True
        )
    
    def disconnect(self, connection: 'SRLConnection') -> None:
        connection.connected = False
    
    def fetch(self, connection: 'SRLConnection', query: Optional[str] = None) -> bytes:
        url = connection.handle
        if query:
            url = f"{url}?{query}"
        
        headers = dict(self.headers)
        if connection.srl.credentials:
            headers.update(connection.srl.credentials.to_headers())
        
        request = urllib.request.Request(url, headers=headers, method=self.method)
        
        context = None
        if not self.verify_ssl:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        
        try:
            with urllib.request.urlopen(request, timeout=self.timeout, context=context) as response:
                return response.read()
        except urllib.error.HTTPError as e:
            raise SRLError(f"HTTP error {e.code}: {e.reason}", code=e.code)
        except urllib.error.URLError as e:
            raise ConnectionError(f"Connection failed: {e.reason}")
    
    def send(self, connection: 'SRLConnection', data: bytes) -> bool:
        url = connection.handle
        
        headers = dict(self.headers)
        headers['Content-Type'] = 'application/octet-stream'
        headers['Content-Length'] = str(len(data))
        
        if connection.srl.credentials:
            headers.update(connection.srl.credentials.to_headers())
        
        request = urllib.request.Request(url, data=data, headers=headers, method="POST")
        
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return response.status == 200 or response.status == 201
        except Exception as e:
            raise SRLError(f"Send failed: {e}")


@dataclass
class SocketProtocol(Protocol):
    """Raw TCP socket protocol."""
    timeout: float = DEFAULT_TIMEOUT
    buffer_size: int = 8192
    use_ssl: bool = False
    
    def connect(self, srl: 'SRL') -> 'SRLConnection':
        port = srl.config.port or 8089
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        
        try:
            sock.connect((srl.domain, port))
            
            if self.use_ssl:
                context = ssl.create_default_context()
                sock = context.wrap_socket(sock, server_hostname=srl.domain)
            
            return SRLConnection(
                srl=srl,
                protocol=self,
                handle=sock,
                connected=True
            )
        except Exception as e:
            sock.close()
            raise ConnectionError(f"Socket connection failed: {e}")
    
    def disconnect(self, connection: 'SRLConnection') -> None:
        if connection.handle:
            try:
                connection.handle.close()
            except:
                pass
        connection.connected = False
    
    def fetch(self, connection: 'SRLConnection', query: Optional[str] = None) -> bytes:
        sock = connection.handle
        
        # Send query as length-prefixed message
        if query:
            query_bytes = query.encode('utf-8')
            sock.sendall(struct.pack('!I', len(query_bytes)))
            sock.sendall(query_bytes)
        else:
            # Send empty query
            sock.sendall(struct.pack('!I', 0))
        
        # Receive length-prefixed response
        length_bytes = self._recv_exact(sock, 4)
        if not length_bytes:
            raise SRLError("Connection closed")
        
        length = struct.unpack('!I', length_bytes)[0]
        if length > MAX_PAYLOAD_SIZE:
            raise SRLError(f"Response too large: {length} bytes")
        
        return self._recv_exact(sock, length)
    
    def send(self, connection: 'SRLConnection', data: bytes) -> bool:
        sock = connection.handle
        
        # Send length-prefixed data
        sock.sendall(struct.pack('!I', len(data)))
        sock.sendall(data)
        
        # Wait for acknowledgment
        ack = self._recv_exact(sock, 1)
        return ack == b'\x01'
    
    def _recv_exact(self, sock: socket.socket, n: int) -> bytes:
        data = b''
        while len(data) < n:
            chunk = sock.recv(n - len(data))
            if not chunk:
                return data
            data += chunk
        return data


@dataclass
class DatabaseProtocol(Protocol):
    """Database connection protocol (abstract)."""
    driver: str = "generic"
    connection_string: Optional[str] = None
    
    def connect(self, srl: 'SRL') -> 'SRLConnection':
        # This would integrate with database drivers
        # For now, just return a placeholder
        return SRLConnection(
            srl=srl,
            protocol=self,
            handle=self.connection_string or srl.path,
            connected=True
        )
    
    def disconnect(self, connection: 'SRLConnection') -> None:
        connection.connected = False
    
    def fetch(self, connection: 'SRLConnection', query: Optional[str] = None) -> bytes:
        # Execute query and return results
        # This would be implemented with actual database drivers
        raise NotImplementedError("Database protocol requires driver implementation")
    
    def send(self, connection: 'SRLConnection', data: bytes) -> bool:
        raise NotImplementedError("Database protocol requires driver implementation")


# ═══════════════════════════════════════════════════════════════════
# SRL CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

@dataclass
class SRLConfig:
    """Configuration for an SRL connection."""
    port: Optional[int] = None
    use_ssl: bool = True
    timeout: float = DEFAULT_TIMEOUT
    retry_count: int = 3
    retry_delay: float = 1.0
    max_payload: int = MAX_PAYLOAD_SIZE
    compression: bool = False
    encryption_key: Optional[bytes] = None


# ═══════════════════════════════════════════════════════════════════
# SRL RESULT
# ═══════════════════════════════════════════════════════════════════

@dataclass
class SRLResult:
    """Result from an SRL operation."""
    success: bool
    data: Optional[bytes] = None
    error: Optional[str] = None
    bit_count: int = 0
    checksum: int = 0
    timestamp: float = field(default_factory=time.time)
    
    @property
    def size(self) -> int:
        return len(self.data) if self.data else 0
    
    def to_substrate_identity(self) -> int:
        """Hash the result data to a 64-bit identity for ingestion."""
        if not self.data:
            return 0
        
        # FNV-1a hash
        FNV_PRIME = 0x100000001b3
        FNV_OFFSET = 0xcbf29ce484222325
        
        h = FNV_OFFSET
        for byte in self.data:
            h ^= byte
            h = (h * FNV_PRIME) & MASK_64
        
        return h


# ═══════════════════════════════════════════════════════════════════
# SRL CONNECTION
# ═══════════════════════════════════════════════════════════════════

@dataclass
class SRLConnection:
    """An active connection through an SRL."""
    srl: 'SRL'
    protocol: Protocol
    handle: Any
    connected: bool = False
    created_at: float = field(default_factory=time.time)
    bytes_sent: int = 0
    bytes_received: int = 0
    
    def fetch(self, query: Optional[str] = None) -> SRLResult:
        """Fetch data through this connection."""
        if not self.connected:
            return SRLResult(success=False, error="Not connected")
        
        try:
            data = self.protocol.fetch(self, query)
            self.bytes_received += len(data)
            
            # Calculate checksum
            checksum = 0
            for i, b in enumerate(data):
                checksum ^= (b << (i % 8))
            checksum &= MASK_64
            
            return SRLResult(
                success=True,
                data=data,
                bit_count=len(data) * 8,
                checksum=checksum
            )
        except Exception as e:
            return SRLResult(success=False, error=str(e))
    
    def send(self, data: bytes) -> SRLResult:
        """Send data through this connection."""
        if not self.connected:
            return SRLResult(success=False, error="Not connected")
        
        try:
            success = self.protocol.send(self, data)
            if success:
                self.bytes_sent += len(data)
            return SRLResult(
                success=success,
                bit_count=len(data) * 8 if success else 0
            )
        except Exception as e:
            return SRLResult(success=False, error=str(e))
    
    def close(self) -> None:
        """Close the connection."""
        self.protocol.disconnect(self)


# ═══════════════════════════════════════════════════════════════════
# SRL - THE CONNECTION DEVICE
# ═══════════════════════════════════════════════════════════════════

class SRL:
    """
    Substrate Reference Locator - Connection Device.
    
    SRL is a Core function that connects to datasources.
    It holds credentials, keys, protocols, queries, and is encrypted.
    
    The kernel's SRL is just a reference locator (pure math).
    This Core SRL adds all connection capabilities.
    
    FLOW:
        1. Create SRL with domain, path, credentials, protocol
        2. Connect to datasource
        3. Fetch or send data
        4. Data returned goes through ingest() to become substrate
    
    Example:
        srl = SRL(
            domain="api.example.com",
            path="/v1/data",
            credentials=TokenAuth(token="..."),
            protocol=HTTPProtocol()
        )
        
        with srl.connect() as conn:
            result = conn.fetch(query="id=42")
            # result.data goes through ingest() to become substrate
    """
    
    __slots__ = (
        '_domain', '_path', '_identity', 
        '_credentials', '_protocol', '_config',
        '_kernel_srl', '_encrypted_credentials'
    )
    
    def __init__(
        self,
        domain: str,
        path: str,
        credentials: Optional[Credentials] = None,
        protocol: Optional[Protocol] = None,
        config: Optional[SRLConfig] = None,
        identity: Optional[int] = None
    ):
        """
        Create an SRL connection device.
        
        Args:
            domain: Target domain (e.g., "api.example.com", "localhost")
            path: Resource path (e.g., "/v1/users", "/data/file.txt")
            credentials: Authentication credentials
            protocol: Connection protocol (auto-detected if None)
            config: Connection configuration
            identity: Optional explicit identity (auto-generated if None)
        """
        self._domain = domain
        self._path = path
        self._credentials = credentials
        self._config = config or SRLConfig()
        
        # Auto-detect protocol if not specified
        if protocol is None:
            protocol = self._auto_detect_protocol()
        self._protocol = protocol
        
        # Generate identity
        if identity is not None:
            self._identity = SubstrateIdentity(identity)
        else:
            self._identity = create_srl_identity(domain, path)
        
        # Create kernel SRL (pure math reference)
        self._kernel_srl = KernelSRL(domain, path, self._identity)
        
        # Encrypt credentials for storage
        self._encrypted_credentials: Optional[bytes] = None
        if credentials and self._config.encryption_key:
            self._encrypted_credentials = credentials.encrypt(self._config.encryption_key)
    
    def _auto_detect_protocol(self) -> Protocol:
        """Auto-detect protocol based on domain/path."""
        if self._domain in ('localhost', '127.0.0.1', '.'):
            return FileProtocol()
        elif self._path.startswith('/db/') or 'database' in self._domain:
            return DatabaseProtocol()
        else:
            return HTTPProtocol()
    
    @property
    def domain(self) -> str:
        return self._domain
    
    @property
    def path(self) -> str:
        return self._path
    
    @property
    def identity(self) -> SubstrateIdentity:
        return self._identity
    
    @property
    def credentials(self) -> Optional[Credentials]:
        return self._credentials
    
    @property
    def config(self) -> SRLConfig:
        return self._config
    
    @property
    def protocol(self) -> Protocol:
        return self._protocol
    
    @property
    def kernel_srl(self) -> KernelSRL:
        """Get the kernel's pure-math SRL reference."""
        return self._kernel_srl
    
    def uri(self) -> str:
        """Get the SRL URI string."""
        return self._kernel_srl.to_uri()
    
    def connect(self) -> SRLConnection:
        """
        Establish connection to the datasource.
        
        Returns:
            SRLConnection for fetching/sending data
        """
        retry_count = self._config.retry_count
        last_error = None
        
        for attempt in range(retry_count):
            try:
                return self._protocol.connect(self)
            except Exception as e:
                last_error = e
                if attempt < retry_count - 1:
                    time.sleep(self._config.retry_delay)
        
        raise ConnectionError(f"Failed to connect after {retry_count} attempts: {last_error}")
    
    def fetch(self, query: Optional[str] = None) -> SRLResult:
        """
        Fetch data from the datasource (convenience method).
        
        Opens connection, fetches, closes.
        For repeated operations, use connect() context manager.
        """
        conn = self.connect()
        try:
            return conn.fetch(query)
        finally:
            conn.close()
    
    def send(self, data: bytes) -> SRLResult:
        """
        Send data to the datasource (convenience method).
        """
        conn = self.connect()
        try:
            return conn.send(data)
        finally:
            conn.close()
    
    @classmethod
    def from_uri(cls, uri: str, **kwargs) -> 'SRL':
        """
        Create SRL from URI string.
        
        Args:
            uri: SRL URI (e.g., "srl://domain/path#identity")
            **kwargs: Additional options (credentials, protocol, config)
        """
        kernel_srl = KernelSRL.from_uri(uri)
        return cls(
            domain=kernel_srl.domain,
            path=kernel_srl.path,
            identity=kernel_srl.identity.value,
            **kwargs
        )
    
    def to_substrate_data(self) -> Dict[str, Any]:
        """
        Convert SRL to data for ingestion as substrate.
        
        The SRL specification itself can be stored as a substrate.
        """
        return {
            'type': 'srl',
            'domain': self._domain,
            'path': self._path,
            'identity': self._identity.value,
            'protocol': type(self._protocol).__name__,
            'config': {
                'port': self._config.port,
                'use_ssl': self._config.use_ssl,
                'timeout': self._config.timeout
            }
        }
    
    def __repr__(self) -> str:
        return f"SRL({self.uri()})"
    
    def __enter__(self) -> SRLConnection:
        """Context manager: connect."""
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager: disconnect handled by connection."""
        pass


# ═══════════════════════════════════════════════════════════════════
# FACTORY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def file_srl(path: str, base_path: Optional[str] = None) -> SRL:
    """Create an SRL for local file access."""
    # Ensure path starts with /
    if not path.startswith('/'):
        path = '/' + path
    return SRL(
        domain="localhost",
        path=path,
        protocol=FileProtocol(base_path=base_path)
    )


def http_srl(
    url: str, 
    credentials: Optional[Credentials] = None,
    headers: Optional[Dict[str, str]] = None
) -> SRL:
    """Create an SRL for HTTP API access."""
    # Parse URL
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc
    path = parsed.path or '/'
    use_ssl = parsed.scheme == 'https'
    
    return SRL(
        domain=domain,
        path=path,
        credentials=credentials,
        protocol=HTTPProtocol(headers=headers or {}),
        config=SRLConfig(use_ssl=use_ssl)
    )


def socket_srl(
    host: str, 
    port: int,
    use_ssl: bool = False,
    credentials: Optional[Credentials] = None
) -> SRL:
    """Create an SRL for raw socket connection."""
    return SRL(
        domain=host,
        path='/',
        credentials=credentials,
        protocol=SocketProtocol(use_ssl=use_ssl),
        config=SRLConfig(port=port, use_ssl=use_ssl)
    )
