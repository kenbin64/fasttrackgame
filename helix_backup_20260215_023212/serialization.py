"""
Dimensional Serialization & Transport Layer

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

This mathematical kernel belongs to all humanity.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

High-performance serialization formats:
    - Binary: Compact wire format for transport
    - JSON: Human-readable interchange format
    - MessagePack: Fast binary JSON alternative
    - SRL: Structured Reference Language format

Transport protocols:
    - UDP: Low-latency unreliable transport
    - TCP: Reliable stream transport
    - WebSocket: Web-compatible bidirectional
    - Memory: In-process shared memory

Features:
    - Zero-copy where possible
    - Streaming support for large payloads
    - Compression options
    - Schema versioning
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    Any, Dict, List, Optional, Union, Type, TypeVar, Generic,
    Callable, Iterator, Tuple, Protocol, BinaryIO, TextIO
)
from enum import Enum, auto
from abc import ABC, abstractmethod
import struct
import json
import zlib
import base64
import hashlib
import io
import threading
from collections import deque


# =============================================================================
# TYPE VARIABLES
# =============================================================================

T = TypeVar('T')


# =============================================================================
# MAGIC NUMBERS AND CONSTANTS
# =============================================================================

# File/message signatures
BINARY_MAGIC = b'BFXD'  # ButterflyFX Dimensional
JSON_MAGIC = '{"_bfx":'
SRL_MAGIC = 'srl://'

# Version
FORMAT_VERSION = 1

# Type codes for binary format
class TypeCode(Enum):
    """Type identification codes for binary serialization."""
    NULL = 0x00
    BOOL = 0x01
    INT8 = 0x02
    INT16 = 0x03
    INT32 = 0x04
    INT64 = 0x05
    FLOAT32 = 0x06
    FLOAT64 = 0x07
    STRING = 0x08
    BYTES = 0x09
    LIST = 0x0A
    DICT = 0x0B
    
    # Dimensional types
    HELIX_STATE = 0x20
    TOKEN = 0x21
    VECTOR2D = 0x22
    VECTOR3D = 0x23
    QUATERNION = 0x24
    TRANSFORM = 0x25
    COLOR = 0x26
    DURATION = 0x27
    TIMEPOINT = 0x28
    
    # Complex types
    SUBSTRATE = 0x40
    MANIFOLD = 0x41
    SPIRAL = 0x42


# Compression modes
class Compression(Enum):
    """Compression algorithms."""
    NONE = 0
    ZLIB = 1
    GZIP = 2
    LZ4 = 3  # Requires lz4 library


# =============================================================================
# SERIALIZATION PROTOCOL
# =============================================================================

class Serializable(Protocol):
    """Protocol for types that can be serialized."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        ...
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Reconstruct from dictionary representation."""
        ...


# =============================================================================
# BINARY SERIALIZER
# =============================================================================

class BinarySerializer:
    """
    High-performance binary serialization.
    
    Format:
        [MAGIC:4][VERSION:1][FLAGS:1][LENGTH:4][CHECKSUM:4][PAYLOAD:...]
    
    Flags:
        bit 0-1: compression (00=none, 01=zlib, 10=gzip, 11=lz4)
        bit 2: has checksum
        bit 3: streaming
        bit 4-7: reserved
    """
    
    # Struct formats for efficiency
    HEADER = struct.Struct('<4sBBIH')  # magic, version, flags, length, checksum
    INT8 = struct.Struct('<b')
    INT16 = struct.Struct('<h')
    INT32 = struct.Struct('<i')
    INT64 = struct.Struct('<q')
    UINT32 = struct.Struct('<I')
    FLOAT32 = struct.Struct('<f')
    FLOAT64 = struct.Struct('<d')
    
    def __init__(
        self,
        compression: Compression = Compression.NONE,
        include_checksum: bool = True
    ):
        self.compression = compression
        self.include_checksum = include_checksum
    
    def serialize(self, obj: Any) -> bytes:
        """Serialize an object to bytes."""
        buffer = io.BytesIO()
        self._write_value(buffer, obj)
        payload = buffer.getvalue()
        
        # Compress if needed
        if self.compression == Compression.ZLIB:
            payload = zlib.compress(payload, level=6)
        elif self.compression == Compression.GZIP:
            import gzip
            payload = gzip.compress(payload, compresslevel=6)
        
        # Build flags
        flags = self.compression.value & 0x03
        if self.include_checksum:
            flags |= 0x04
        
        # Calculate checksum (CRC16)
        checksum = zlib.crc32(payload) & 0xFFFF if self.include_checksum else 0
        
        # Build header
        header = self.HEADER.pack(
            BINARY_MAGIC,
            FORMAT_VERSION,
            flags,
            len(payload),
            checksum
        )
        
        return header + payload
    
    def deserialize(self, data: bytes) -> Any:
        """Deserialize bytes to an object."""
        if len(data) < self.HEADER.size:
            raise ValueError("Data too short for header")
        
        # Parse header
        magic, version, flags, length, checksum = self.HEADER.unpack(
            data[:self.HEADER.size]
        )
        
        if magic != BINARY_MAGIC:
            raise ValueError(f"Invalid magic: {magic}")
        
        if version > FORMAT_VERSION:
            raise ValueError(f"Unsupported version: {version}")
        
        payload = data[self.HEADER.size:]
        
        if len(payload) != length:
            raise ValueError(f"Length mismatch: expected {length}, got {len(payload)}")
        
        # Verify checksum
        if flags & 0x04:
            actual = zlib.crc32(payload) & 0xFFFF
            if actual != checksum:
                raise ValueError(f"Checksum mismatch: {checksum} != {actual}")
        
        # Decompress
        compression = Compression(flags & 0x03)
        if compression == Compression.ZLIB:
            payload = zlib.decompress(payload)
        elif compression == Compression.GZIP:
            import gzip
            payload = gzip.decompress(payload)
        
        # Parse payload
        buffer = io.BytesIO(payload)
        return self._read_value(buffer)
    
    def _write_value(self, buffer: BinaryIO, value: Any) -> None:
        """Write a value to buffer."""
        if value is None:
            buffer.write(bytes([TypeCode.NULL.value]))
        elif isinstance(value, bool):
            buffer.write(bytes([TypeCode.BOOL.value, 1 if value else 0]))
        elif isinstance(value, int):
            self._write_int(buffer, value)
        elif isinstance(value, float):
            buffer.write(bytes([TypeCode.FLOAT64.value]))
            buffer.write(self.FLOAT64.pack(value))
        elif isinstance(value, str):
            encoded = value.encode('utf-8')
            buffer.write(bytes([TypeCode.STRING.value]))
            self._write_length(buffer, len(encoded))
            buffer.write(encoded)
        elif isinstance(value, bytes):
            buffer.write(bytes([TypeCode.BYTES.value]))
            self._write_length(buffer, len(value))
            buffer.write(value)
        elif isinstance(value, (list, tuple)):
            buffer.write(bytes([TypeCode.LIST.value]))
            self._write_length(buffer, len(value))
            for item in value:
                self._write_value(buffer, item)
        elif isinstance(value, dict):
            buffer.write(bytes([TypeCode.DICT.value]))
            self._write_length(buffer, len(value))
            for k, v in value.items():
                self._write_value(buffer, k)
                self._write_value(buffer, v)
        elif hasattr(value, 'to_dict'):
            # Serializable object
            self._write_dimensional(buffer, value)
        else:
            raise TypeError(f"Cannot serialize type: {type(value)}")
    
    def _write_int(self, buffer: BinaryIO, value: int) -> None:
        """Write an integer with optimal size."""
        if -128 <= value <= 127:
            buffer.write(bytes([TypeCode.INT8.value]))
            buffer.write(self.INT8.pack(value))
        elif -32768 <= value <= 32767:
            buffer.write(bytes([TypeCode.INT16.value]))
            buffer.write(self.INT16.pack(value))
        elif -2147483648 <= value <= 2147483647:
            buffer.write(bytes([TypeCode.INT32.value]))
            buffer.write(self.INT32.pack(value))
        else:
            buffer.write(bytes([TypeCode.INT64.value]))
            buffer.write(self.INT64.pack(value))
    
    def _write_length(self, buffer: BinaryIO, length: int) -> None:
        """Write a variable-length integer (varint)."""
        while length >= 0x80:
            buffer.write(bytes([(length & 0x7F) | 0x80]))
            length >>= 7
        buffer.write(bytes([length]))
    
    def _write_dimensional(self, buffer: BinaryIO, obj: Any) -> None:
        """Write a dimensional object."""
        type_name = type(obj).__name__
        
        # Map types to codes
        type_map = {
            'HelixState': TypeCode.HELIX_STATE,
            'Token': TypeCode.TOKEN,
            'Vector2D': TypeCode.VECTOR2D,
            'Vector3D': TypeCode.VECTOR3D,
            'Quaternion': TypeCode.QUATERNION,
            'Transform': TypeCode.TRANSFORM,
            'Color': TypeCode.COLOR,
            'Duration': TypeCode.DURATION,
            'TimePoint': TypeCode.TIMEPOINT,
        }
        
        code = type_map.get(type_name, TypeCode.DICT)
        buffer.write(bytes([code.value]))
        
        # Write type name for generic objects
        if code == TypeCode.DICT:
            encoded = type_name.encode('utf-8')
            self._write_length(buffer, len(encoded))
            buffer.write(encoded)
        
        # Write as dict
        data = obj.to_dict() if hasattr(obj, 'to_dict') else {}
        self._write_length(buffer, len(data))
        for k, v in data.items():
            self._write_value(buffer, k)
            self._write_value(buffer, v)
    
    def _read_value(self, buffer: BinaryIO) -> Any:
        """Read a value from buffer."""
        type_byte = buffer.read(1)
        if not type_byte:
            raise ValueError("Unexpected end of data")
        
        type_code = TypeCode(type_byte[0])
        
        if type_code == TypeCode.NULL:
            return None
        elif type_code == TypeCode.BOOL:
            return buffer.read(1)[0] != 0
        elif type_code == TypeCode.INT8:
            return self.INT8.unpack(buffer.read(1))[0]
        elif type_code == TypeCode.INT16:
            return self.INT16.unpack(buffer.read(2))[0]
        elif type_code == TypeCode.INT32:
            return self.INT32.unpack(buffer.read(4))[0]
        elif type_code == TypeCode.INT64:
            return self.INT64.unpack(buffer.read(8))[0]
        elif type_code == TypeCode.FLOAT32:
            return self.FLOAT32.unpack(buffer.read(4))[0]
        elif type_code == TypeCode.FLOAT64:
            return self.FLOAT64.unpack(buffer.read(8))[0]
        elif type_code == TypeCode.STRING:
            length = self._read_length(buffer)
            return buffer.read(length).decode('utf-8')
        elif type_code == TypeCode.BYTES:
            length = self._read_length(buffer)
            return buffer.read(length)
        elif type_code == TypeCode.LIST:
            length = self._read_length(buffer)
            return [self._read_value(buffer) for _ in range(length)]
        elif type_code == TypeCode.DICT:
            length = self._read_length(buffer)
            return {self._read_value(buffer): self._read_value(buffer) for _ in range(length)}
        elif type_code.value >= 0x20:
            # Dimensional type
            return self._read_dimensional(buffer, type_code)
        else:
            raise ValueError(f"Unknown type code: {type_code}")
    
    def _read_length(self, buffer: BinaryIO) -> int:
        """Read a variable-length integer."""
        result = 0
        shift = 0
        while True:
            byte = buffer.read(1)[0]
            result |= (byte & 0x7F) << shift
            if not (byte & 0x80):
                break
            shift += 7
        return result
    
    def _read_dimensional(self, buffer: BinaryIO, type_code: TypeCode) -> Dict[str, Any]:
        """Read a dimensional object as a dictionary."""
        # For dimensional types, read the dict data
        if type_code == TypeCode.DICT:
            # Has type name prefix
            name_len = self._read_length(buffer)
            type_name = buffer.read(name_len).decode('utf-8')
        
        length = self._read_length(buffer)
        data = {}
        for _ in range(length):
            key = self._read_value(buffer)
            value = self._read_value(buffer)
            data[key] = value
        
        # Add type info
        data['_type'] = type_code.name
        return data


# =============================================================================
# JSON SERIALIZER
# =============================================================================

class JSONSerializer:
    """
    JSON serialization with dimensional extensions.
    
    Special keys:
        _bfx: ButterflyFX marker with version
        _type: Type name for reconstruction
        _srl: SRL reference for deferred loading
    """
    
    def __init__(
        self,
        indent: Optional[int] = None,
        ensure_ascii: bool = False,
        sort_keys: bool = False
    ):
        self.indent = indent
        self.ensure_ascii = ensure_ascii
        self.sort_keys = sort_keys
    
    def serialize(self, obj: Any) -> str:
        """Serialize to JSON string."""
        data = {
            '_bfx': FORMAT_VERSION,
            'data': self._encode(obj)
        }
        return json.dumps(
            data,
            indent=self.indent,
            ensure_ascii=self.ensure_ascii,
            sort_keys=self.sort_keys,
            default=self._default_encoder
        )
    
    def deserialize(self, text: str) -> Any:
        """Deserialize from JSON string."""
        data = json.loads(text)
        
        if isinstance(data, dict) and '_bfx' in data:
            return self._decode(data.get('data'))
        return self._decode(data)
    
    def serialize_to_file(self, obj: Any, path: str) -> None:
        """Serialize to a JSON file."""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.serialize(obj))
    
    def deserialize_from_file(self, path: str) -> Any:
        """Deserialize from a JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            return self.deserialize(f.read())
    
    def _encode(self, obj: Any) -> Any:
        """Encode an object for JSON."""
        if obj is None or isinstance(obj, (bool, int, float, str)):
            return obj
        elif isinstance(obj, bytes):
            return {'_type': 'bytes', 'data': base64.b64encode(obj).decode('ascii')}
        elif isinstance(obj, (list, tuple)):
            return [self._encode(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._encode(v) for k, v in obj.items()}
        elif hasattr(obj, 'to_dict'):
            data = obj.to_dict()
            data['_type'] = type(obj).__name__
            return {k: self._encode(v) for k, v in data.items()}
        else:
            return str(obj)
    
    def _decode(self, data: Any) -> Any:
        """Decode JSON data."""
        if data is None or isinstance(data, (bool, int, float, str)):
            return data
        elif isinstance(data, list):
            return [self._decode(item) for item in data]
        elif isinstance(data, dict):
            if '_type' in data:
                type_name = data['_type']
                if type_name == 'bytes':
                    return base64.b64decode(data['data'])
                # For other types, return as dict with metadata
            return {k: self._decode(v) for k, v in data.items()}
        return data
    
    def _default_encoder(self, obj: Any) -> Any:
        """Default encoder for unknown types."""
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        raise TypeError(f"Cannot serialize type: {type(obj)}")


# =============================================================================
# SRL (STRUCTURED REFERENCE LANGUAGE) SERIALIZER
# =============================================================================

class SRLSerializer:
    """
    SRL serialization - ButterflyFX's native reference format.
    
    Format: srl://[spiral].[level]/[path]?[query]#[fragment]
    
    Examples:
        srl://0.3/manifold/tokens/circle
        srl://-1.6/data/user?filter=active
        srl://0.0..0.6/traverse  (range)
    """
    
    @staticmethod
    def encode(
        spiral: int,
        level: int,
        path: str = '',
        query: Optional[Dict[str, str]] = None,
        fragment: Optional[str] = None
    ) -> str:
        """Encode to SRL format."""
        srl = f"srl://{spiral}.{level}"
        
        if path:
            srl += f"/{path}"
        
        if query:
            pairs = '&'.join(f"{k}={v}" for k, v in query.items())
            srl += f"?{pairs}"
        
        if fragment:
            srl += f"#{fragment}"
        
        return srl
    
    @staticmethod
    def encode_range(
        start_spiral: int,
        start_level: int,
        end_spiral: int,
        end_level: int,
        path: str = ''
    ) -> str:
        """Encode a state range to SRL."""
        return f"srl://{start_spiral}.{start_level}..{end_spiral}.{end_level}/{path}"
    
    @staticmethod
    def decode(srl: str) -> Dict[str, Any]:
        """Decode an SRL string."""
        if not srl.startswith('srl://'):
            raise ValueError(f"Invalid SRL: must start with 'srl://'")
        
        # Strip prefix
        rest = srl[6:]
        
        result: Dict[str, Any] = {
            'spiral': 0,
            'level': 0,
            'path': '',
            'query': {},
            'fragment': None,
            'is_range': False
        }
        
        # Parse fragment
        if '#' in rest:
            rest, fragment = rest.rsplit('#', 1)
            result['fragment'] = fragment
        
        # Parse query
        if '?' in rest:
            rest, query = rest.split('?', 1)
            result['query'] = dict(pair.split('=') for pair in query.split('&') if '=' in pair)
        
        # Parse path
        if '/' in rest:
            state_part, path = rest.split('/', 1)
            result['path'] = path
        else:
            state_part = rest
        
        # Parse state (may be range)
        if '..' in state_part:
            result['is_range'] = True
            start, end = state_part.split('..')
            s1, l1 = start.split('.')
            s2, l2 = end.split('.')
            result['start_spiral'] = int(s1)
            result['start_level'] = int(l1)
            result['end_spiral'] = int(s2)
            result['end_level'] = int(l2)
        else:
            parts = state_part.split('.')
            result['spiral'] = int(parts[0])
            result['level'] = int(parts[1]) if len(parts) > 1 else 0
        
        return result
    
    @staticmethod
    def to_tokens(srl: str) -> List[str]:
        """Convert SRL path to tokens."""
        decoded = SRLSerializer.decode(srl)
        path = decoded.get('path', '')
        return [t for t in path.split('/') if t]


# =============================================================================
# TRANSPORT ABSTRACTION
# =============================================================================

class TransportMessage:
    """A message for transport."""
    
    __slots__ = ('id', 'type', 'payload', 'timestamp', 'metadata')
    
    def __init__(
        self,
        msg_type: str,
        payload: bytes,
        msg_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ):
        import uuid
        self.id = msg_id or str(uuid.uuid4())
        self.type = msg_type
        self.payload = payload
        self.timestamp = __import__('time').time()
        self.metadata = metadata or {}
    
    def to_bytes(self) -> bytes:
        """Serialize message to bytes."""
        # Format: [ID:36][TYPE_LEN:1][TYPE][META_LEN:2][META_JSON][PAYLOAD]
        id_bytes = self.id.encode('ascii')
        type_bytes = self.type.encode('utf-8')
        meta_bytes = json.dumps(self.metadata).encode('utf-8')
        
        header = struct.pack('<36sB', id_bytes, len(type_bytes))
        return header + type_bytes + struct.pack('<H', len(meta_bytes)) + meta_bytes + self.payload
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'TransportMessage':
        """Deserialize from bytes."""
        id_bytes, type_len = struct.unpack('<36sB', data[:37])
        msg_id = id_bytes.decode('ascii').strip()
        
        offset = 37
        msg_type = data[offset:offset + type_len].decode('utf-8')
        offset += type_len
        
        meta_len = struct.unpack('<H', data[offset:offset + 2])[0]
        offset += 2
        
        metadata = json.loads(data[offset:offset + meta_len].decode('utf-8'))
        offset += meta_len
        
        payload = data[offset:]
        
        return cls(msg_type, payload, msg_id, metadata)


class Transport(ABC):
    """Abstract transport interface."""
    
    @abstractmethod
    def send(self, message: TransportMessage) -> None:
        """Send a message."""
        ...
    
    @abstractmethod
    def receive(self, timeout: Optional[float] = None) -> Optional[TransportMessage]:
        """Receive a message (blocking)."""
        ...
    
    @abstractmethod
    def close(self) -> None:
        """Close the transport."""
        ...


# =============================================================================
# IN-MEMORY TRANSPORT
# =============================================================================

class MemoryTransport(Transport):
    """In-process transport using queues."""
    
    def __init__(self, buffer_size: int = 1000):
        self._inbox: deque = deque(maxlen=buffer_size)
        self._lock = threading.Lock()
        self._event = threading.Event()
        self._closed = False
    
    def send(self, message: TransportMessage) -> None:
        if self._closed:
            raise RuntimeError("Transport is closed")
        
        with self._lock:
            self._inbox.append(message)
            self._event.set()
    
    def receive(self, timeout: Optional[float] = None) -> Optional[TransportMessage]:
        if self._closed:
            return None
        
        # Wait for message
        if not self._inbox:
            self._event.clear()
            if not self._event.wait(timeout):
                return None
        
        with self._lock:
            if self._inbox:
                return self._inbox.popleft()
            return None
    
    def close(self) -> None:
        self._closed = True
        self._event.set()


# =============================================================================
# MESSAGE CHANNEL (Bidirectional)
# =============================================================================

class MessageChannel:
    """Bidirectional message channel between two endpoints."""
    
    def __init__(self, buffer_size: int = 1000):
        self._a = MemoryTransport(buffer_size)
        self._b = MemoryTransport(buffer_size)
    
    @property
    def endpoint_a(self) -> Tuple[Transport, Transport]:
        """Get (send, receive) transports for endpoint A."""
        return (self._b, self._a)  # A sends to B's inbox
    
    @property
    def endpoint_b(self) -> Tuple[Transport, Transport]:
        """Get (send, receive) transports for endpoint B."""
        return (self._a, self._b)  # B sends to A's inbox
    
    def close(self) -> None:
        self._a.close()
        self._b.close()


# =============================================================================
# STREAMING SERIALIZER
# =============================================================================

class StreamingSerializer:
    """
    Chunk-based streaming serializer for large payloads.
    
    Breaks data into chunks for streaming transmission.
    """
    
    def __init__(
        self,
        chunk_size: int = 64 * 1024,  # 64KB chunks
        serializer: Optional[BinarySerializer] = None
    ):
        self.chunk_size = chunk_size
        self.serializer = serializer or BinarySerializer()
    
    def serialize_chunks(self, obj: Any) -> Iterator[bytes]:
        """Serialize object and yield chunks."""
        data = self.serializer.serialize(obj)
        total = len(data)
        
        # First chunk includes total size
        header = struct.pack('<Q', total)
        
        offset = 0
        chunk_num = 0
        while offset < total:
            chunk_data = data[offset:offset + self.chunk_size]
            
            # Chunk format: [CHUNK_NUM:4][CHUNK_LEN:4][DATA]
            chunk_header = struct.pack('<II', chunk_num, len(chunk_data))
            
            if chunk_num == 0:
                yield header + chunk_header + chunk_data
            else:
                yield chunk_header + chunk_data
            
            offset += self.chunk_size
            chunk_num += 1
    
    def deserialize_chunks(self, chunks: Iterator[bytes]) -> Any:
        """Reassemble chunks and deserialize."""
        buffer = io.BytesIO()
        expected_size = None
        received = 0
        
        for chunk in chunks:
            if expected_size is None:
                # First chunk has total size
                expected_size = struct.unpack('<Q', chunk[:8])[0]
                chunk = chunk[8:]
            
            # Parse chunk header
            chunk_num, chunk_len = struct.unpack('<II', chunk[:8])
            chunk_data = chunk[8:]
            
            buffer.write(chunk_data)
            received += len(chunk_data)
            
            if received >= expected_size:
                break
        
        buffer.seek(0)
        return self.serializer.deserialize(buffer.read())


# =============================================================================
# SCHEMA REGISTRY
# =============================================================================

class SchemaRegistry:
    """
    Registry for type schemas to support versioned serialization.
    """
    
    def __init__(self):
        self._schemas: Dict[str, Dict[int, Dict[str, Any]]] = {}
        self._current_versions: Dict[str, int] = {}
    
    def register(
        self,
        type_name: str,
        version: int,
        schema: Dict[str, Any]
    ) -> None:
        """Register a schema version."""
        if type_name not in self._schemas:
            self._schemas[type_name] = {}
        
        self._schemas[type_name][version] = schema
        
        # Update current version if higher
        if version > self._current_versions.get(type_name, 0):
            self._current_versions[type_name] = version
    
    def get_schema(
        self,
        type_name: str,
        version: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Get a schema, optionally for a specific version."""
        if type_name not in self._schemas:
            return None
        
        if version is None:
            version = self._current_versions.get(type_name)
        
        return self._schemas[type_name].get(version)
    
    def migrations(
        self,
        type_name: str,
        from_version: int,
        to_version: Optional[int] = None
    ) -> List[Callable[[Dict], Dict]]:
        """Get migration functions between versions."""
        # This would be extended to support actual migrations
        return []


# =============================================================================
# HIGH-LEVEL API
# =============================================================================

@dataclass
class SerializationConfig:
    """Configuration for serialization operations."""
    format: str = 'binary'  # 'binary', 'json', 'srl'
    compression: Compression = Compression.NONE
    include_checksum: bool = True
    json_indent: Optional[int] = None
    chunk_size: int = 64 * 1024


class DimensionalSerializer:
    """
    Unified serialization interface for dimensional objects.
    """
    
    def __init__(self, config: Optional[SerializationConfig] = None):
        self.config = config or SerializationConfig()
        
        self._binary = BinarySerializer(
            compression=self.config.compression,
            include_checksum=self.config.include_checksum
        )
        self._json = JSONSerializer(indent=self.config.json_indent)
        self._srl = SRLSerializer()
        self._streaming = StreamingSerializer(
            chunk_size=self.config.chunk_size,
            serializer=self._binary
        )
    
    def serialize(self, obj: Any, format: Optional[str] = None) -> Union[bytes, str]:
        """Serialize an object."""
        fmt = format or self.config.format
        
        if fmt == 'binary':
            return self._binary.serialize(obj)
        elif fmt == 'json':
            return self._json.serialize(obj)
        else:
            raise ValueError(f"Unknown format: {fmt}")
    
    def deserialize(self, data: Union[bytes, str], format: Optional[str] = None) -> Any:
        """Deserialize data."""
        # Auto-detect format
        if format is None:
            if isinstance(data, bytes):
                if data.startswith(BINARY_MAGIC):
                    format = 'binary'
                else:
                    format = 'json'
                    data = data.decode('utf-8')
            else:
                format = 'json'
        
        if format == 'binary':
            return self._binary.deserialize(data)
        elif format == 'json':
            return self._json.deserialize(data)
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def to_file(self, obj: Any, path: str, format: Optional[str] = None) -> None:
        """Serialize to file."""
        fmt = format or self.config.format
        data = self.serialize(obj, fmt)
        
        mode = 'wb' if isinstance(data, bytes) else 'w'
        with open(path, mode) as f:
            f.write(data)
    
    def from_file(self, path: str, format: Optional[str] = None) -> Any:
        """Deserialize from file."""
        # Try binary first
        try:
            with open(path, 'rb') as f:
                data = f.read()
            
            if data.startswith(BINARY_MAGIC):
                return self.deserialize(data, 'binary')
            
            # Try as JSON
            return self.deserialize(data.decode('utf-8'), 'json')
        except Exception:
            with open(path, 'r', encoding='utf-8') as f:
                return self.deserialize(f.read(), 'json')
    
    def to_srl(
        self,
        spiral: int,
        level: int,
        path: str = '',
        **kwargs
    ) -> str:
        """Create an SRL reference."""
        return self._srl.encode(spiral, level, path, **kwargs)
    
    def from_srl(self, srl: str) -> Dict[str, Any]:
        """Parse an SRL reference."""
        return self._srl.decode(srl)
    
    def stream_serialize(self, obj: Any) -> Iterator[bytes]:
        """Streaming serialization."""
        return self._streaming.serialize_chunks(obj)
    
    def stream_deserialize(self, chunks: Iterator[bytes]) -> Any:
        """Streaming deserialization."""
        return self._streaming.deserialize_chunks(chunks)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

# Global default serializer
_default_serializer = DimensionalSerializer()


def serialize(obj: Any, format: str = 'binary') -> Union[bytes, str]:
    """Serialize an object using default serializer."""
    return _default_serializer.serialize(obj, format)


def deserialize(data: Union[bytes, str]) -> Any:
    """Deserialize data using default serializer."""
    return _default_serializer.deserialize(data)


def to_srl(spiral: int, level: int, path: str = '', **kwargs) -> str:
    """Create an SRL reference."""
    return _default_serializer.to_srl(spiral, level, path, **kwargs)


def from_srl(srl: str) -> Dict[str, Any]:
    """Parse an SRL reference."""
    return _default_serializer.from_srl(srl)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Serializers
    'BinarySerializer',
    'JSONSerializer',
    'SRLSerializer',
    'StreamingSerializer',
    'DimensionalSerializer',
    
    # Config
    'SerializationConfig',
    'Compression',
    'TypeCode',
    
    # Transport
    'Transport',
    'TransportMessage',
    'MemoryTransport',
    'MessageChannel',
    
    # Schema
    'SchemaRegistry',
    
    # Protocols
    'Serializable',
    
    # Functions
    'serialize',
    'deserialize',
    'to_srl',
    'from_srl',
    
    # Constants
    'FORMAT_VERSION',
    'BINARY_MAGIC',
]
