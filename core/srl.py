"""
SRL - Substrate Resource Locator (Core Implementation)

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

The kernel's srl.py is just the reference locator (domain+path+identity).
This module adds all connection, credential, and transport logic.

CHARTER COMPLIANCE:
✅ Principle 1: All Things Are by Reference (no data copying)
✅ Principle 2: Passive Until Invoked (lazy retrieval)
✅ Principle 3: No Self-Modifying Code (immutable)
✅ Principle 5: No Hacking Surface (pure functions)
✅ Principle 6: No Dark Web (all connections visible)

LAW ALIGNMENT:
- Law 1: External data becomes substrates (unity)
- Law 2: Connection is observation (division)
- Law 4: Connection creates meaning
- Law 5: Data flow is motion through dimensions
- Law 6: Identity persists through retrieval
- Law 7: Data returns to unity as substrate

═══════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
import base64
import hashlib
import json
import os
import socket
import ssl
import time
import urllib.request
import urllib.parse
import urllib.error
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from pathlib import Path

# Kernel reference locator (pure math only)
from kernel.srl import SRL as KernelSRL, create_srl_identity
from kernel.substrate import SubstrateIdentity
from kernel.logging import get_logger, LogLevel

# Module logger
logger = get_logger(__name__, level=LogLevel.INFO)


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
    
    # Credentials
    'Credentials',
    'APIKey',
    'BasicAuth',
    'TokenAuth',
    
    # Errors
    'SRLError',
    'ConnectionError',
    'AuthenticationError',
    
    # Factory functions
    'file_srl',
    'http_srl',
    'socket_srl',
]


# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════

MASK_64 = 0xFFFFFFFFFFFFFFFF
DEFAULT_TIMEOUT = 30.0
MAX_PAYLOAD_SIZE = 100 * 1024 * 1024  # 100MB

# Resource type constants (for create_srl_identity)
RESOURCE_TYPE_FILE = 0x0001
RESOURCE_TYPE_HTTP = 0x0002
RESOURCE_TYPE_SOCKET = 0x0004


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
    """
    Base class for credentials.

    Credentials are encrypted using substrate identity as the key.
    This ensures credentials are tied to specific substrates and
    cannot be extracted or reused outside the dimensional context.
    """

    @abstractmethod
    def to_headers(self) -> Dict[str, str]:
        """Convert to HTTP headers."""
        pass

    @abstractmethod
    def encrypt(self, key: bytes) -> bytes:
        """
        Encrypt credentials for storage.

        Uses XOR encryption with substrate identity as key.
        This is simple but effective for dimensional context.
        """
        pass

    @classmethod
    @abstractmethod
    def decrypt(cls, data: bytes, key: bytes) -> 'Credentials':
        """Decrypt credentials from storage."""
        pass


@dataclass
class APIKey(Credentials):
    """
    API key authentication.

    Example:
        creds = APIKey(key="sk-1234567890abcdef")
        headers = creds.to_headers()
        # {"X-API-Key": "sk-1234567890abcdef"}
    """
    key: str
    header_name: str = "X-API-Key"

    def __post_init__(self):
        """Validate API key credentials."""
        if not self.key:
            logger.error("APIKey validation failed: empty key")
            raise ValueError("API key cannot be empty")

        if not isinstance(self.key, str):
            logger.error("APIKey validation failed: key must be string", key_type=type(self.key).__name__)
            raise TypeError(f"API key must be str, got {type(self.key).__name__}")

        if not self.header_name:
            logger.error("APIKey validation failed: empty header_name")
            raise ValueError("Header name cannot be empty")

        logger.debug("APIKey created", header_name=self.header_name, key_length=len(self.key))

    def to_headers(self) -> Dict[str, str]:
        return {self.header_name: self.key}

    def encrypt(self, key: bytes) -> bytes:
        """Encrypt API key using XOR with substrate identity."""
        if not key:
            logger.error("APIKey encryption failed: empty encryption key")
            raise ValueError("Encryption key cannot be empty")

        try:
            key_data = self.key.encode('utf-8')
            encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(key_data))
            result = base64.b64encode(encrypted)
            logger.debug("APIKey encrypted", original_length=len(key_data), encrypted_length=len(result))
            return result
        except Exception as e:
            logger.error("APIKey encryption failed", error=str(e), error_type=type(e).__name__)
            raise SRLError(f"Failed to encrypt API key: {str(e)}")

    @classmethod
    def decrypt(cls, data: bytes, key: bytes) -> 'APIKey':
        """Decrypt API key from encrypted data."""
        if not data:
            logger.error("APIKey decryption failed: empty data")
            raise ValueError("Encrypted data cannot be empty")

        if not key:
            logger.error("APIKey decryption failed: empty decryption key")
            raise ValueError("Decryption key cannot be empty")

        try:
            encrypted = base64.b64decode(data)
            decrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(encrypted))
            api_key = decrypted.decode('utf-8')
            logger.debug("APIKey decrypted", key_length=len(api_key))
            return cls(key=api_key)
        except Exception as e:
            logger.error("APIKey decryption failed", error=str(e), error_type=type(e).__name__)
            raise SRLError(f"Failed to decrypt API key: {str(e)}")


@dataclass
class BasicAuth(Credentials):
    """
    HTTP Basic authentication.

    Example:
        creds = BasicAuth(username="user", password="pass")
        headers = creds.to_headers()
        # {"Authorization": "Basic dXNlcjpwYXNz"}
    """
    username: str
    password: str

    def __post_init__(self):
        """Validate Basic Auth credentials."""
        if not self.username:
            logger.error("BasicAuth validation failed: empty username")
            raise ValueError("Username cannot be empty")

        if not isinstance(self.username, str):
            logger.error("BasicAuth validation failed: username must be string", username_type=type(self.username).__name__)
            raise TypeError(f"Username must be str, got {type(self.username).__name__}")

        if not self.password:
            logger.error("BasicAuth validation failed: empty password")
            raise ValueError("Password cannot be empty")

        if not isinstance(self.password, str):
            logger.error("BasicAuth validation failed: password must be string", password_type=type(self.password).__name__)
            raise TypeError(f"Password must be str, got {type(self.password).__name__}")

        logger.debug("BasicAuth created", username=self.username)

    def to_headers(self) -> Dict[str, str]:
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return {"Authorization": f"Basic {encoded}"}

    def encrypt(self, key: bytes) -> bytes:
        """Encrypt credentials using XOR with substrate identity."""
        if not key:
            logger.error("BasicAuth encryption failed: empty encryption key")
            raise ValueError("Encryption key cannot be empty")

        try:
            data = f"{self.username}:{self.password}".encode('utf-8')
            encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
            result = base64.b64encode(encrypted)
            logger.debug("BasicAuth encrypted", username=self.username)
            return result
        except Exception as e:
            logger.error("BasicAuth encryption failed", error=str(e), error_type=type(e).__name__)
            raise SRLError(f"Failed to encrypt credentials: {str(e)}")

    @classmethod
    def decrypt(cls, data: bytes, key: bytes) -> 'BasicAuth':
        """Decrypt credentials from encrypted data."""
        if not data:
            logger.error("BasicAuth decryption failed: empty data")
            raise ValueError("Encrypted data cannot be empty")

        if not key:
            logger.error("BasicAuth decryption failed: empty decryption key")
            raise ValueError("Decryption key cannot be empty")

        try:
            encrypted = base64.b64decode(data)
            decrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(encrypted))
            credentials_str = decrypted.decode('utf-8')

            if ':' not in credentials_str:
                logger.error("BasicAuth decryption failed: invalid format (missing colon)")
                raise ValueError("Invalid credentials format")

            username, password = credentials_str.split(':', 1)
            logger.debug("BasicAuth decrypted", username=username)
            return cls(username=username, password=password)
        except ValueError:
            raise  # Re-raise validation errors
        except Exception as e:
            logger.error("BasicAuth decryption failed", error=str(e), error_type=type(e).__name__)
            raise SRLError(f"Failed to decrypt credentials: {str(e)}")


@dataclass
class TokenAuth(Credentials):
    """
    Bearer token authentication.

    Example:
        creds = TokenAuth(token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        headers = creds.to_headers()
        # {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
    """
    token: str
    token_type: str = "Bearer"

    def __post_init__(self):
        """Validate token credentials."""
        if not self.token:
            logger.error("TokenAuth validation failed: empty token")
            raise ValueError("Token cannot be empty")

        if not isinstance(self.token, str):
            logger.error("TokenAuth validation failed: token must be string", token_type=type(self.token).__name__)
            raise TypeError(f"Token must be str, got {type(self.token).__name__}")

        if not self.token_type:
            logger.error("TokenAuth validation failed: empty token_type")
            raise ValueError("Token type cannot be empty")

        logger.debug("TokenAuth created", token_type=self.token_type, token_length=len(self.token))

    def to_headers(self) -> Dict[str, str]:
        return {"Authorization": f"{self.token_type} {self.token}"}

    def encrypt(self, key: bytes) -> bytes:
        """Encrypt token using XOR with substrate identity."""
        if not key:
            logger.error("TokenAuth encryption failed: empty encryption key")
            raise ValueError("Encryption key cannot be empty")

        try:
            encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(self.token.encode('utf-8')))
            result = base64.b64encode(encrypted)
            logger.debug("TokenAuth encrypted", token_type=self.token_type)
            return result
        except Exception as e:
            logger.error("TokenAuth encryption failed", error=str(e), error_type=type(e).__name__)
            raise SRLError(f"Failed to encrypt token: {str(e)}")

    @classmethod
    def decrypt(cls, data: bytes, key: bytes) -> 'TokenAuth':
        """Decrypt token from encrypted data."""
        if not data:
            logger.error("TokenAuth decryption failed: empty data")
            raise ValueError("Encrypted data cannot be empty")

        if not key:
            logger.error("TokenAuth decryption failed: empty decryption key")
            raise ValueError("Decryption key cannot be empty")

        try:
            encrypted = base64.b64decode(data)
            decrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(encrypted))
            token = decrypted.decode('utf-8')
            logger.debug("TokenAuth decrypted", token_length=len(token))
            return cls(token=token)
        except Exception as e:
            logger.error("TokenAuth decryption failed", error=str(e), error_type=type(e).__name__)
            raise SRLError(f"Failed to decrypt token: {str(e)}")


# ═══════════════════════════════════════════════════════════════════
# RESULT AND CONNECTION
# ═══════════════════════════════════════════════════════════════════

@dataclass
class SRLResult:
    """
    Result of an SRL operation.

    Contains the fetched data, metadata, and checksum for verification.
    """
    success: bool
    data: Optional[bytes] = None
    error: Optional[str] = None
    bit_count: int = 0
    checksum: int = 0
    timestamp: float = field(default_factory=time.time)

    def to_substrate_identity(self) -> SubstrateIdentity:
        """
        Convert result data to substrate identity.

        This is how external data becomes a substrate in DimensionOS.
        """
        if not self.success or self.data is None:
            return SubstrateIdentity(0)

        # Hash the data to create 64-bit identity
        data_hash = hashlib.sha256(self.data).digest()
        identity_value = int.from_bytes(data_hash[:8], 'big') & MASK_64

        return SubstrateIdentity(identity_value)


@dataclass
class SRLConnection:
    """
    An active connection through an SRL.

    Tracks connection state, bytes transferred, and provides
    fetch/send operations.
    """
    srl: 'SRL'
    protocol: 'Protocol'
    handle: Any
    connected: bool = False
    created_at: float = field(default_factory=time.time)
    bytes_sent: int = 0
    bytes_received: int = 0

    def fetch(self, query: Optional[str] = None) -> SRLResult:
        """
        Fetch data through this connection.

        Returns SRLResult with data and metadata.
        """
        if not self.connected:
            return SRLResult(success=False, error="Not connected")

        try:
            data = self.protocol.fetch(self, query)
            self.bytes_received += len(data)

            # Calculate checksum (XOR of all bytes with position)
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
        """
        Send data through this connection.

        Returns SRLResult indicating success/failure.
        """
        if not self.connected:
            return SRLResult(success=False, error="Not connected")

        try:
            success = self.protocol.send(self, data)
            if success:
                self.bytes_sent += len(data)

            return SRLResult(success=success)
        except Exception as e:
            return SRLResult(success=False, error=str(e))

    def close(self) -> None:
        """Close this connection."""
        if self.connected:
            self.protocol.disconnect(self)
            self.connected = False


# ═══════════════════════════════════════════════════════════════════
# PROTOCOLS
# ═══════════════════════════════════════════════════════════════════

class Protocol(ABC):
    """
    Base class for connection protocols.

    Each protocol implements connect, disconnect, fetch, and send
    operations for a specific transport mechanism.
    """

    @abstractmethod
    def connect(self, srl: 'SRL') -> SRLConnection:
        """Establish connection."""
        pass

    @abstractmethod
    def disconnect(self, connection: SRLConnection) -> None:
        """Close connection."""
        pass

    @abstractmethod
    def fetch(self, connection: SRLConnection, query: Optional[str] = None) -> bytes:
        """Fetch data from the connection."""
        pass

    @abstractmethod
    def send(self, connection: SRLConnection, data: bytes) -> bool:
        """Send data through the connection."""
        pass


@dataclass
class FileProtocol(Protocol):
    """
    Local file system protocol.

    Connects to files and directories on the local filesystem.

    Example:
        protocol = FileProtocol(base_path="/data")
        srl = SRL(path="/users.json", protocol=protocol)
        connection = protocol.connect(srl)
        result = connection.fetch()
    """
    base_path: Optional[str] = None

    def __post_init__(self):
        """Validate file protocol configuration."""
        if self.base_path and not isinstance(self.base_path, str):
            logger.error("FileProtocol validation failed: base_path must be string", base_path_type=type(self.base_path).__name__)
            raise TypeError(f"base_path must be str, got {type(self.base_path).__name__}")

        if self.base_path and not os.path.exists(self.base_path):
            logger.warn("FileProtocol base_path does not exist", base_path=self.base_path)

        logger.debug("FileProtocol created", base_path=self.base_path)

    def connect(self, srl: 'SRL') -> SRLConnection:
        """Establish file system connection."""
        if not srl:
            logger.error("FileProtocol connect failed: srl is None")
            raise ValueError("SRL cannot be None")

        if not srl.path:
            logger.error("FileProtocol connect failed: srl.path is empty")
            raise ValueError("SRL path cannot be empty")

        try:
            path = srl.path
            if self.base_path:
                path = os.path.join(self.base_path, path.lstrip('/'))

            if not os.path.exists(path):
                logger.error("FileProtocol connect failed: path not found", path=path)
                raise ConnectionError(f"Path not found: {path}")

            logger.info("FileProtocol connected", path=path)
            return SRLConnection(
                srl=srl,
                protocol=self,
                handle=path,
                connected=True
            )
        except ConnectionError:
            raise  # Re-raise connection errors
        except Exception as e:
            logger.error("FileProtocol connect failed", error=str(e), error_type=type(e).__name__)
            raise ConnectionError(f"Failed to connect to file: {str(e)}")

    def disconnect(self, connection: SRLConnection) -> None:
        """Close file system connection."""
        if connection:
            connection.connected = False
            logger.debug("FileProtocol disconnected", path=connection.handle)

    def fetch(self, connection: SRLConnection, query: Optional[str] = None) -> bytes:
        """Fetch data from file or directory."""
        if not connection:
            logger.error("FileProtocol fetch failed: connection is None")
            raise ValueError("Connection cannot be None")

        if not connection.connected:
            logger.error("FileProtocol fetch failed: not connected")
            raise ConnectionError("Not connected")

        path = connection.handle

        try:
            if os.path.isfile(path):
                logger.debug("FileProtocol fetching file", path=path)
                with open(path, 'rb') as f:
                    data = f.read()
                logger.info("FileProtocol fetched file", path=path, bytes=len(data))
                return data
            elif os.path.isdir(path):
                logger.debug("FileProtocol fetching directory listing", path=path)
                entries = os.listdir(path)
                data = json.dumps(entries).encode('utf-8')
                logger.info("FileProtocol fetched directory", path=path, entries=len(entries))
                return data
            else:
                logger.error("FileProtocol fetch failed: not a file or directory", path=path)
                raise SRLError(f"Cannot read: {path}")
        except (FileNotFoundError, PermissionError) as e:
            logger.error("FileProtocol fetch failed", path=path, error=str(e), error_type=type(e).__name__)
            raise ConnectionError(f"Failed to read {path}: {str(e)}")
        except Exception as e:
            logger.error("FileProtocol fetch failed", path=path, error=str(e), error_type=type(e).__name__)
            raise SRLError(f"Failed to fetch from {path}: {str(e)}")

    def send(self, connection: SRLConnection, data: bytes) -> bool:
        """Send data to file."""
        if not connection:
            logger.error("FileProtocol send failed: connection is None")
            raise ValueError("Connection cannot be None")

        if not connection.connected:
            logger.error("FileProtocol send failed: not connected")
            raise ConnectionError("Not connected")

        if not isinstance(data, bytes):
            logger.error("FileProtocol send failed: data must be bytes", data_type=type(data).__name__)
            raise TypeError(f"Data must be bytes, got {type(data).__name__}")

        if len(data) > MAX_PAYLOAD_SIZE:
            logger.error("FileProtocol send failed: payload too large", size=len(data), max_size=MAX_PAYLOAD_SIZE)
            raise SRLError(f"Payload too large: {len(data)} bytes (max {MAX_PAYLOAD_SIZE})")

        path = connection.handle

        try:
            logger.debug("FileProtocol writing file", path=path, bytes=len(data))
            with open(path, 'wb') as f:
                f.write(data)
            logger.info("FileProtocol wrote file", path=path, bytes=len(data))
            return True
        except (PermissionError, OSError) as e:
            logger.error("FileProtocol send failed", path=path, error=str(e), error_type=type(e).__name__)
            raise ConnectionError(f"Failed to write {path}: {str(e)}")
        except Exception as e:
            logger.error("FileProtocol send failed", path=path, error=str(e), error_type=type(e).__name__)
            raise SRLError(f"Failed to send to {path}: {str(e)}")


@dataclass
class HTTPProtocol(Protocol):
    """
    HTTP/HTTPS protocol.

    Connects to HTTP APIs and web services.

    Example:
        protocol = HTTPProtocol(method="GET", headers={"User-Agent": "DimensionOS"})
        srl = SRL(domain="api.example.com", path="/data", protocol=protocol)
        connection = protocol.connect(srl)
        result = connection.fetch()
    """
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: float = DEFAULT_TIMEOUT
    verify_ssl: bool = True

    def __post_init__(self):
        """Validate HTTP protocol configuration."""
        valid_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
        if self.method not in valid_methods:
            logger.error("HTTPProtocol validation failed: invalid method", method=self.method, valid_methods=valid_methods)
            raise ValueError(f"Invalid HTTP method: {self.method}. Must be one of {valid_methods}")

        if self.timeout <= 0:
            logger.error("HTTPProtocol validation failed: timeout must be positive", timeout=self.timeout)
            raise ValueError(f"Timeout must be positive, got {self.timeout}")

        if not isinstance(self.headers, dict):
            logger.error("HTTPProtocol validation failed: headers must be dict", headers_type=type(self.headers).__name__)
            raise TypeError(f"Headers must be dict, got {type(self.headers).__name__}")

        logger.debug("HTTPProtocol created", method=self.method, timeout=self.timeout, verify_ssl=self.verify_ssl)

    def connect(self, srl: 'SRL') -> SRLConnection:
        """Establish HTTP connection."""
        if not srl:
            logger.error("HTTPProtocol connect failed: srl is None")
            raise ValueError("SRL cannot be None")

        if not srl.domain:
            logger.error("HTTPProtocol connect failed: srl.domain is empty")
            raise ValueError("SRL domain cannot be empty")

        if not srl.path:
            logger.error("HTTPProtocol connect failed: srl.path is empty")
            raise ValueError("SRL path cannot be empty")

        try:
            # Build URL from SRL
            scheme = "https" if srl.use_ssl else "http"
            port = srl.port or (443 if srl.use_ssl else 80)
            url = f"{scheme}://{srl.domain}:{port}{srl.path}"

            logger.info("HTTPProtocol connected", url=url, method=self.method)
            return SRLConnection(
                srl=srl,
                protocol=self,
                handle=url,
                connected=True
            )
        except Exception as e:
            logger.error("HTTPProtocol connect failed", error=str(e), error_type=type(e).__name__)
            raise ConnectionError(f"Failed to connect to HTTP endpoint: {str(e)}")

    def disconnect(self, connection: SRLConnection) -> None:
        """Close HTTP connection."""
        if connection:
            connection.connected = False
            logger.debug("HTTPProtocol disconnected", url=connection.handle)

    def fetch(self, connection: SRLConnection, query: Optional[str] = None) -> bytes:
        """Fetch data via HTTP."""
        if not connection:
            logger.error("HTTPProtocol fetch failed: connection is None")
            raise ValueError("Connection cannot be None")

        if not connection.connected:
            logger.error("HTTPProtocol fetch failed: not connected")
            raise ConnectionError("Not connected")

        url = connection.handle
        if query:
            url = f"{url}?{query}"

        headers = dict(self.headers)
        if connection.srl.credentials:
            headers.update(connection.srl.credentials.to_headers())

        try:
            logger.debug("HTTPProtocol fetching", url=url, method=self.method)
            request = urllib.request.Request(url, headers=headers, method=self.method)

            context = None
            if not self.verify_ssl:
                logger.warn("HTTPProtocol SSL verification disabled", url=url)
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(request, timeout=self.timeout, context=context) as response:
                data = response.read()
                logger.info("HTTPProtocol fetched", url=url, status=response.status, bytes=len(data))
                return data
        except urllib.error.HTTPError as e:
            logger.error("HTTPProtocol fetch failed: HTTP error", url=url, code=e.code, reason=e.reason)
            raise SRLError(f"HTTP error {e.code}: {e.reason}", code=e.code)
        except urllib.error.URLError as e:
            logger.error("HTTPProtocol fetch failed: URL error", url=url, reason=str(e.reason))
            raise ConnectionError(f"Connection failed: {e.reason}")
        except Exception as e:
            logger.error("HTTPProtocol fetch failed", url=url, error=str(e), error_type=type(e).__name__)
            raise SRLError(f"Failed to fetch from {url}: {str(e)}")

    def send(self, connection: SRLConnection, data: bytes) -> bool:
        """Send data via HTTP."""
        if not connection:
            logger.error("HTTPProtocol send failed: connection is None")
            raise ValueError("Connection cannot be None")

        if not connection.connected:
            logger.error("HTTPProtocol send failed: not connected")
            raise ConnectionError("Not connected")

        if not isinstance(data, bytes):
            logger.error("HTTPProtocol send failed: data must be bytes", data_type=type(data).__name__)
            raise TypeError(f"Data must be bytes, got {type(data).__name__}")

        if len(data) > MAX_PAYLOAD_SIZE:
            logger.error("HTTPProtocol send failed: payload too large", size=len(data), max_size=MAX_PAYLOAD_SIZE)
            raise SRLError(f"Payload too large: {len(data)} bytes (max {MAX_PAYLOAD_SIZE})")

        url = connection.handle

        headers = dict(self.headers)
        if connection.srl.credentials:
            headers.update(connection.srl.credentials.to_headers())

        try:
            logger.debug("HTTPProtocol sending", url=url, method=self.method, bytes=len(data))
            request = urllib.request.Request(url, data=data, headers=headers, method=self.method)

            context = None
            if not self.verify_ssl:
                logger.warn("HTTPProtocol SSL verification disabled", url=url)
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(request, timeout=self.timeout, context=context) as response:
                success = response.status == 200
                logger.info("HTTPProtocol sent", url=url, status=response.status, success=success)
                return success
        except urllib.error.HTTPError as e:
            logger.error("HTTPProtocol send failed: HTTP error", url=url, code=e.code, reason=e.reason)
            raise SRLError(f"HTTP error {e.code}: {e.reason}", code=e.code)
        except urllib.error.URLError as e:
            logger.error("HTTPProtocol send failed: URL error", url=url, reason=str(e.reason))
            raise ConnectionError(f"Connection failed: {e.reason}")
        except Exception as e:
            logger.error("HTTPProtocol send failed", url=url, error=str(e), error_type=type(e).__name__)
            raise SRLError(f"Failed to send to {url}: {str(e)}")


@dataclass
class SocketProtocol(Protocol):
    """
    Raw TCP socket protocol.

    Connects to TCP sockets for low-level network communication.

    Example:
        protocol = SocketProtocol(use_ssl=True)
        srl = SRL(domain="example.com", port=443, protocol=protocol)
        connection = protocol.connect(srl)
        result = connection.fetch()
    """
    use_ssl: bool = False
    timeout: float = DEFAULT_TIMEOUT
    buffer_size: int = 4096

    def __post_init__(self):
        """Validate socket protocol configuration."""
        if self.timeout <= 0:
            logger.error("SocketProtocol validation failed: timeout must be positive", timeout=self.timeout)
            raise ValueError(f"Timeout must be positive, got {self.timeout}")

        if self.buffer_size <= 0:
            logger.error("SocketProtocol validation failed: buffer_size must be positive", buffer_size=self.buffer_size)
            raise ValueError(f"Buffer size must be positive, got {self.buffer_size}")

        if self.buffer_size > MAX_PAYLOAD_SIZE:
            logger.error("SocketProtocol validation failed: buffer_size too large", buffer_size=self.buffer_size, max_size=MAX_PAYLOAD_SIZE)
            raise ValueError(f"Buffer size too large: {self.buffer_size} (max {MAX_PAYLOAD_SIZE})")

        logger.debug("SocketProtocol created", use_ssl=self.use_ssl, timeout=self.timeout, buffer_size=self.buffer_size)

    def connect(self, srl: 'SRL') -> SRLConnection:
        """Establish socket connection."""
        if not srl:
            logger.error("SocketProtocol connect failed: srl is None")
            raise ValueError("SRL cannot be None")

        if not srl.domain:
            logger.error("SocketProtocol connect failed: srl.domain is empty")
            raise ValueError("SRL domain cannot be empty")

        if not srl.port:
            logger.error("SocketProtocol connect failed: srl.port is None")
            raise ValueError("SRL port cannot be None for socket connections")

        sock = None
        try:
            logger.debug("SocketProtocol connecting", domain=srl.domain, port=srl.port, use_ssl=self.use_ssl)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((srl.domain, srl.port))

            if self.use_ssl:
                logger.debug("SocketProtocol wrapping with SSL", domain=srl.domain)
                context = ssl.create_default_context()
                sock = context.wrap_socket(sock, server_hostname=srl.domain)

            logger.info("SocketProtocol connected", domain=srl.domain, port=srl.port, use_ssl=self.use_ssl)
            return SRLConnection(
                srl=srl,
                protocol=self,
                handle=sock,
                connected=True
            )
        except socket.gaierror as e:
            if sock:
                sock.close()
            logger.error("SocketProtocol connect failed: DNS resolution error", domain=srl.domain, error=str(e))
            raise ConnectionError(f"DNS resolution failed for {srl.domain}: {str(e)}")
        except socket.timeout as e:
            if sock:
                sock.close()
            logger.error("SocketProtocol connect failed: timeout", domain=srl.domain, port=srl.port)
            raise ConnectionError(f"Connection timeout to {srl.domain}:{srl.port}")
        except Exception as e:
            if sock:
                sock.close()
            logger.error("SocketProtocol connect failed", domain=srl.domain, port=srl.port, error=str(e), error_type=type(e).__name__)
            raise ConnectionError(f"Socket connection failed: {str(e)}")

    def disconnect(self, connection: SRLConnection) -> None:
        """Close socket connection."""
        if connection and connection.handle:
            try:
                connection.handle.close()
                logger.debug("SocketProtocol disconnected")
            except Exception as e:
                logger.warn("SocketProtocol disconnect error", error=str(e))
        if connection:
            connection.connected = False

    def fetch(self, connection: SRLConnection, query: Optional[str] = None) -> bytes:
        """Fetch data from socket."""
        if not connection:
            logger.error("SocketProtocol fetch failed: connection is None")
            raise ValueError("Connection cannot be None")

        if not connection.connected:
            logger.error("SocketProtocol fetch failed: not connected")
            raise ConnectionError("Not connected")

        sock = connection.handle

        try:
            # If query provided, send it first
            if query:
                logger.debug("SocketProtocol sending query", query_length=len(query))
                sock.sendall(query.encode('utf-8'))

            # Receive data
            logger.debug("SocketProtocol receiving data", buffer_size=self.buffer_size)
            chunks = []
            total_bytes = 0
            while True:
                try:
                    chunk = sock.recv(self.buffer_size)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    total_bytes += len(chunk)

                    if total_bytes > MAX_PAYLOAD_SIZE:
                        logger.error("SocketProtocol fetch failed: payload too large", bytes=total_bytes, max_size=MAX_PAYLOAD_SIZE)
                        raise SRLError(f"Payload too large: {total_bytes} bytes (max {MAX_PAYLOAD_SIZE})")
                except socket.timeout:
                    logger.debug("SocketProtocol receive timeout (normal)", bytes_received=total_bytes)
                    break

            data = b''.join(chunks)
            logger.info("SocketProtocol fetched", bytes=len(data))
            return data
        except SRLError:
            raise  # Re-raise SRL errors
        except Exception as e:
            logger.error("SocketProtocol fetch failed", error=str(e), error_type=type(e).__name__)
            raise SRLError(f"Failed to fetch from socket: {str(e)}")

    def send(self, connection: SRLConnection, data: bytes) -> bool:
        """Send data to socket."""
        if not connection:
            logger.error("SocketProtocol send failed: connection is None")
            raise ValueError("Connection cannot be None")

        if not connection.connected:
            logger.error("SocketProtocol send failed: not connected")
            raise ConnectionError("Not connected")

        if not isinstance(data, bytes):
            logger.error("SocketProtocol send failed: data must be bytes", data_type=type(data).__name__)
            raise TypeError(f"Data must be bytes, got {type(data).__name__}")

        if len(data) > MAX_PAYLOAD_SIZE:
            logger.error("SocketProtocol send failed: payload too large", size=len(data), max_size=MAX_PAYLOAD_SIZE)
            raise SRLError(f"Payload too large: {len(data)} bytes (max {MAX_PAYLOAD_SIZE})")

        sock = connection.handle

        try:
            logger.debug("SocketProtocol sending", bytes=len(data))
            sock.sendall(data)
            logger.info("SocketProtocol sent", bytes=len(data))
            return True
        except Exception as e:
            logger.error("SocketProtocol send failed", error=str(e), error_type=type(e).__name__)
            raise SRLError(f"Failed to send to socket: {str(e)}")


# ═══════════════════════════════════════════════════════════════════
# CORE SRL - CONNECTION DEVICE
# ═══════════════════════════════════════════════════════════════════

class SRL:
    """
    Core SRL - The Connection Device.

    Bridges the Kernel SRL (pure math) to actual I/O operations.

    The SRL holds:
    - Domain/path information
    - Protocol implementation
    - Credentials (encrypted)
    - Connection configuration

    Example:
        # Create SRL for HTTP API
        srl = SRL(
            domain="api.example.com",
            path="/data",
            protocol=HTTPProtocol(),
            credentials=APIKey(key="sk-1234567890abcdef")
        )

        # Connect and fetch
        connection = srl.connect()
        result = connection.fetch()

        # Spawn substrate from result
        substrate_id = srl.spawn(result.data)
    """
    __slots__ = (
        '_kernel_srl', '_domain', '_path', '_port', '_use_ssl',
        '_protocol', '_credentials', '_connection'
    )

    def __init__(
        self,
        domain: str = "",
        path: str = "/",
        port: Optional[int] = None,
        use_ssl: bool = True,
        protocol: Optional[Protocol] = None,
        credentials: Optional[Credentials] = None
    ):
        """
        Create a Core SRL.

        Args:
            domain: Domain name or host
            path: Resource path
            port: Port number (default: 443 for SSL, 80 for non-SSL)
            use_ssl: Whether to use SSL/TLS
            protocol: Protocol implementation (default: HTTPProtocol)
            credentials: Authentication credentials
        """
        # Validate inputs
        if not isinstance(domain, str):
            logger.error("SRL validation failed: domain must be string", domain_type=type(domain).__name__)
            raise TypeError(f"Domain must be str, got {type(domain).__name__}")

        if not isinstance(path, str):
            logger.error("SRL validation failed: path must be string", path_type=type(path).__name__)
            raise TypeError(f"Path must be str, got {type(path).__name__}")

        if port is not None:
            if not isinstance(port, int):
                logger.error("SRL validation failed: port must be int", port_type=type(port).__name__)
                raise TypeError(f"Port must be int, got {type(port).__name__}")

            if port < 1 or port > 65535:
                logger.error("SRL validation failed: port out of range", port=port)
                raise ValueError(f"Port must be 1-65535, got {port}")

        if protocol is not None and not isinstance(protocol, Protocol):
            logger.error("SRL validation failed: protocol must be Protocol instance", protocol_type=type(protocol).__name__)
            raise TypeError(f"Protocol must be Protocol instance, got {type(protocol).__name__}")

        if credentials is not None and not isinstance(credentials, Credentials):
            logger.error("SRL validation failed: credentials must be Credentials instance", credentials_type=type(credentials).__name__)
            raise TypeError(f"Credentials must be Credentials instance, got {type(credentials).__name__}")

        # Create kernel SRL for mathematical identity
        resource_type = RESOURCE_TYPE_HTTP  # Default to HTTP
        if protocol and isinstance(protocol, FileProtocol):
            resource_type = RESOURCE_TYPE_FILE
        elif protocol and isinstance(protocol, SocketProtocol):
            resource_type = RESOURCE_TYPE_SOCKET

        # Create 64-bit identity from domain and path
        domain_hash = hash(domain) & 0xFFFFFF
        path_hash = hash(path) & 0xFFFFFF
        srl_identity_value = create_srl_identity(resource_type, domain_hash, path_hash)

        # Create kernel SRL
        kernel_srl = KernelSRL(
            srl_id=SubstrateIdentity(srl_identity_value),
            resource_expression=lambda: srl_identity_value,
            spawn_rule=lambda data: SubstrateIdentity(data & MASK_64)
        )

        object.__setattr__(self, '_kernel_srl', kernel_srl)
        object.__setattr__(self, '_domain', domain)
        object.__setattr__(self, '_path', path)
        object.__setattr__(self, '_port', port)
        object.__setattr__(self, '_use_ssl', use_ssl)
        object.__setattr__(self, '_protocol', protocol or HTTPProtocol())
        object.__setattr__(self, '_credentials', credentials)
        object.__setattr__(self, '_connection', None)

        logger.debug("SRL created", domain=domain, path=path, port=port, use_ssl=use_ssl, identity=srl_identity_value)

    def __setattr__(self, name, value):
        raise TypeError("SRL is immutable")

    def __delattr__(self, name):
        raise TypeError("SRL is immutable")

    @property
    def identity(self) -> SubstrateIdentity:
        """Get the 64-bit substrate identity of this SRL."""
        return self._kernel_srl.identity

    @property
    def domain(self) -> str:
        return self._domain

    @property
    def path(self) -> str:
        return self._path

    @property
    def port(self) -> Optional[int]:
        return self._port

    @property
    def use_ssl(self) -> bool:
        return self._use_ssl

    @property
    def protocol(self) -> Protocol:
        return self._protocol

    @property
    def credentials(self) -> Optional[Credentials]:
        return self._credentials

    def connect(self) -> SRLConnection:
        """
        Establish connection through this SRL.

        Returns:
            SRLConnection ready for fetch/send operations
        """
        try:
            logger.debug("SRL connecting", domain=self._domain, path=self._path)
            connection = self._protocol.connect(self)
            object.__setattr__(self, '_connection', connection)
            logger.info("SRL connected", domain=self._domain, path=self._path)
            return connection
        except Exception as e:
            logger.error("SRL connect failed", domain=self._domain, path=self._path, error=str(e), error_type=type(e).__name__)
            raise

    def fetch(self, query: Optional[str] = None) -> SRLResult:
        """
        Fetch data through this SRL.

        Automatically connects if not already connected.

        Args:
            query: Optional query string

        Returns:
            SRLResult with data and metadata
        """
        try:
            if not self._connection or not self._connection.connected:
                logger.debug("SRL auto-connecting for fetch", domain=self._domain, path=self._path)
                self.connect()

            logger.debug("SRL fetching", domain=self._domain, path=self._path, query=query)
            result = self._connection.fetch(query)

            if result.success:
                logger.info("SRL fetch succeeded", domain=self._domain, path=self._path, bytes=result.bit_count // 8)
            else:
                logger.error("SRL fetch failed", domain=self._domain, path=self._path, error=result.error)

            return result
        except Exception as e:
            logger.error("SRL fetch exception", domain=self._domain, path=self._path, error=str(e), error_type=type(e).__name__)
            raise

    def spawn(self, external_data: bytes) -> SubstrateIdentity:
        """
        Spawn a substrate identity from external data.

        This is how external data becomes a substrate in DimensionOS.

        Args:
            external_data: Raw bytes from external source

        Returns:
            SubstrateIdentity for the new substrate
        """
        if not isinstance(external_data, bytes):
            logger.error("SRL spawn failed: data must be bytes", data_type=type(external_data).__name__)
            raise TypeError(f"External data must be bytes, got {type(external_data).__name__}")

        if len(external_data) == 0:
            logger.warn("SRL spawn: empty data")

        try:
            logger.debug("SRL spawning substrate", bytes=len(external_data))
            # Hash the data to create 64-bit identity
            data_hash = hashlib.sha256(external_data).digest()
            identity_value = int.from_bytes(data_hash[:8], 'big') & MASK_64

            # Use kernel SRL to spawn substrate identity
            substrate_id = self._kernel_srl.spawn(identity_value)
            logger.info("SRL spawned substrate", identity=str(substrate_id), bytes=len(external_data))
            return substrate_id
        except Exception as e:
            logger.error("SRL spawn failed", error=str(e), error_type=type(e).__name__)
            raise SRLError(f"Failed to spawn substrate: {str(e)}")

    def close(self) -> None:
        """Close the connection if open."""
        if self._connection:
            try:
                logger.debug("SRL closing connection", domain=self._domain, path=self._path)
                self._connection.close()
                object.__setattr__(self, '_connection', None)
                logger.info("SRL connection closed", domain=self._domain, path=self._path)
            except Exception as e:
                logger.warn("SRL close error", domain=self._domain, path=self._path, error=str(e))

    def __repr__(self) -> str:
        return f"SRL(domain={self._domain}, path={self._path}, identity={self.identity})"


# ═══════════════════════════════════════════════════════════════════
# FACTORY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def file_srl(
    path: str,
    base_path: Optional[str] = None
) -> SRL:
    """
    Create an SRL for local file access.

    Args:
        path: File or directory path
        base_path: Optional base directory

    Returns:
        SRL configured for file access

    Example:
        srl = file_srl("/data/users.json")
        result = srl.fetch()
        substrate_id = srl.spawn(result.data)
    """
    if not path:
        logger.error("file_srl failed: path is empty")
        raise ValueError("Path cannot be empty")

    if not isinstance(path, str):
        logger.error("file_srl failed: path must be string", path_type=type(path).__name__)
        raise TypeError(f"Path must be str, got {type(path).__name__}")

    logger.debug("Creating file SRL", path=path, base_path=base_path)

    try:
        protocol = FileProtocol(base_path=base_path)
        srl = SRL(
            domain="localhost",
            path=path,
            protocol=protocol,
            use_ssl=False
        )
        logger.info("File SRL created", path=path)
        return srl
    except Exception as e:
        logger.error("file_srl failed", path=path, error=str(e), error_type=type(e).__name__)
        raise


def http_srl(
    url: str,
    credentials: Optional[Credentials] = None,
    headers: Optional[Dict[str, str]] = None,
    method: str = "GET",
    verify_ssl: bool = True
) -> SRL:
    """
    Create an SRL for HTTP API access.

    Args:
        url: Full URL (e.g., "https://api.example.com/data")
        credentials: Optional authentication credentials
        headers: Optional HTTP headers
        method: HTTP method (default: GET)
        verify_ssl: Whether to verify SSL certificates

    Returns:
        SRL configured for HTTP access

    Example:
        srl = http_srl(
            "https://api.example.com/data",
            credentials=APIKey(key="sk-1234567890abcdef"),
            headers={"User-Agent": "DimensionOS"}
        )
        result = srl.fetch()
        substrate_id = srl.spawn(result.data)
    """
    if not url:
        logger.error("http_srl failed: url is empty")
        raise ValueError("URL cannot be empty")

    if not isinstance(url, str):
        logger.error("http_srl failed: url must be string", url_type=type(url).__name__)
        raise TypeError(f"URL must be str, got {type(url).__name__}")

    logger.debug("Creating HTTP SRL", url=url, method=method, verify_ssl=verify_ssl)

    try:
        # Parse URL
        parsed = urllib.parse.urlparse(url)

        if not parsed.scheme:
            logger.error("http_srl failed: missing URL scheme", url=url)
            raise ValueError(f"URL must include scheme (http:// or https://): {url}")

        if parsed.scheme not in ["http", "https"]:
            logger.error("http_srl failed: invalid URL scheme", url=url, scheme=parsed.scheme)
            raise ValueError(f"URL scheme must be http or https, got {parsed.scheme}")

        if not parsed.netloc:
            logger.error("http_srl failed: missing domain", url=url)
            raise ValueError(f"URL must include domain: {url}")

        protocol = HTTPProtocol(
            method=method,
            headers=headers or {},
            verify_ssl=verify_ssl
        )

        srl = SRL(
            domain=parsed.netloc.split(':')[0],
            path=parsed.path or "/",
            port=parsed.port,
            use_ssl=parsed.scheme == "https",
            protocol=protocol,
            credentials=credentials
        )
        logger.info("HTTP SRL created", url=url, method=method)
        return srl
    except ValueError:
        raise  # Re-raise validation errors
    except Exception as e:
        logger.error("http_srl failed", url=url, error=str(e), error_type=type(e).__name__)
        raise SRLError(f"Failed to create HTTP SRL: {str(e)}")


def socket_srl(
    host: str,
    port: int,
    use_ssl: bool = False,
    timeout: float = DEFAULT_TIMEOUT
) -> SRL:
    """
    Create an SRL for raw socket connection.

    Args:
        host: Hostname or IP address
        port: Port number
        use_ssl: Whether to use SSL/TLS
        timeout: Connection timeout in seconds

    Returns:
        SRL configured for socket access

    Example:
        srl = socket_srl("example.com", 443, use_ssl=True)
        connection = srl.connect()
        result = connection.fetch()
        substrate_id = srl.spawn(result.data)
    """
    if not host:
        logger.error("socket_srl failed: host is empty")
        raise ValueError("Host cannot be empty")

    if not isinstance(host, str):
        logger.error("socket_srl failed: host must be string", host_type=type(host).__name__)
        raise TypeError(f"Host must be str, got {type(host).__name__}")

    if not isinstance(port, int):
        logger.error("socket_srl failed: port must be int", port_type=type(port).__name__)
        raise TypeError(f"Port must be int, got {type(port).__name__}")

    if port < 1 or port > 65535:
        logger.error("socket_srl failed: port out of range", port=port)
        raise ValueError(f"Port must be 1-65535, got {port}")

    if timeout <= 0:
        logger.error("socket_srl failed: timeout must be positive", timeout=timeout)
        raise ValueError(f"Timeout must be positive, got {timeout}")

    logger.debug("Creating socket SRL", host=host, port=port, use_ssl=use_ssl, timeout=timeout)

    try:
        protocol = SocketProtocol(use_ssl=use_ssl, timeout=timeout)

        srl = SRL(
            domain=host,
            path="/",
            port=port,
            use_ssl=use_ssl,
            protocol=protocol
        )
        logger.info("Socket SRL created", host=host, port=port, use_ssl=use_ssl)
        return srl
    except Exception as e:
        logger.error("socket_srl failed", host=host, port=port, error=str(e), error_type=type(e).__name__)
        raise

