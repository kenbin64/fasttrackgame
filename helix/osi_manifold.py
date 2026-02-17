"""
ButterflyFX OSI-Manifold Transport Layer

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

Part of ButterflyFX - Open source infrastructure.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

THE MODEL IS THE PAYLOAD. THE NETWORK IS THE MANIFOLD.

This module implements the revolutionary insight: the OSI 7-layer model and the
ButterflyFX 7-level helix are isomorphic. We don't just map them — we unify them.

The manifold coordinate system (spiral, level, position) becomes the addressing
scheme. Traversing the network IS traversing the manifold surface.

OSI Layer     Helix Level    Function
─────────     ───────────    ────────
Physical      POINT (0)      Raw signal, the atomic bit
Data Link     LINE (1)       Frame structure, sequence
Network       PLANE (2)      2D routing coordinates
Transport     VOLUME (3)     3D flow control, reliability
Session       TIME (4)       Temporal state, connection
Presentation  PARALLEL (5)   Alternative encodings
Application   META (6)       User-level abstraction

KEY INSIGHT:
Traditional networking sends data ABOUT the world.
Manifold networking sends the MATHEMATICS of the world.
The receiver evaluates the math locally — any computer can decipher math.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Callable, Generator, Union
from enum import Enum, IntEnum
import struct
import zlib
import json
import time
import math
import hashlib
from abc import ABC, abstractmethod


# =============================================================================
# OSI-HELIX UNIFIED LAYER DEFINITIONS
# =============================================================================

class OSIHelixLayer(IntEnum):
    """
    The unified OSI-Helix layers.
    Each layer expands upon the previous, forming a helix structure.
    """
    PHYSICAL = 0       # POINT: Atomic signal, raw bits
    DATA_LINK = 1      # LINE: Sequential frames, packet structure
    NETWORK = 2        # PLANE: 2D coordinate addressing (spiral × position)
    TRANSPORT = 3      # VOLUME: 3D flow control (spiral × level × position)
    SESSION = 4        # TIME: Connection state over time
    PRESENTATION = 5   # PARALLEL: Alternative representations
    APPLICATION = 6    # META: User-level abstraction
    

# Layer metadata
LAYER_INFO = {
    OSIHelixLayer.PHYSICAL: {
        "helix": "POINT",
        "dimension": "0D",
        "unit": "bit",
        "expansion": "singular atomic value"
    },
    OSIHelixLayer.DATA_LINK: {
        "helix": "LINE", 
        "dimension": "1D",
        "unit": "frame",
        "expansion": "point expands to sequence"
    },
    OSIHelixLayer.NETWORK: {
        "helix": "PLANE",
        "dimension": "2D",
        "unit": "coordinate",
        "expansion": "line expands to grid"
    },
    OSIHelixLayer.TRANSPORT: {
        "helix": "VOLUME",
        "dimension": "3D",
        "unit": "segment",
        "expansion": "plane expands to space"
    },
    OSIHelixLayer.SESSION: {
        "helix": "TIME",
        "dimension": "4D",
        "unit": "state",
        "expansion": "volume animated through time"
    },
    OSIHelixLayer.PRESENTATION: {
        "helix": "PARALLEL",
        "dimension": "5D",
        "unit": "encoding",
        "expansion": "timeline branches to alternatives"
    },
    OSIHelixLayer.APPLICATION: {
        "helix": "META",
        "dimension": "6D",
        "unit": "abstraction",
        "expansion": "parallel collapses to overview"
    },
}


# =============================================================================
# MANIFOLD ADDRESS - The Network IS the Coordinate System
# =============================================================================

@dataclass(frozen=True)
class ManifoldAddress:
    """
    A network address in manifold space.
    
    This replaces IP addresses with dimensional coordinates.
    The address IS the location on the manifold surface.
    
    Coordinates:
        spiral: Which dimension/channel (like network ID)
        level: Which OSI layer / helix level (0-6)
        position: Position along that level
        
    Additional coordinates for higher dimensions:
        time: Temporal offset (for TIME/SESSION layer)
        branch: Alternative branch (for PARALLEL/PRESENTATION layer)
        meta_key: Abstraction key (for META/APPLICATION layer)
    """
    spiral: int = 0
    level: int = 0
    position: int = 0
    time: float = 0.0
    branch: int = 0
    meta_key: str = ""
    
    @property
    def as_tuple(self) -> Tuple[int, int, int]:
        """Basic 3D coordinate"""
        return (self.spiral, self.level, self.position)
    
    @property
    def full_coordinate(self) -> Tuple:
        """Full 6D coordinate"""
        return (self.spiral, self.level, self.position, self.time, self.branch, self.meta_key)
    
    @property
    def layer(self) -> OSIHelixLayer:
        """Get OSI-Helix layer for this address"""
        return OSIHelixLayer(min(self.level, 6))
    
    def to_uri(self) -> str:
        """
        Convert to manifold URI format.
        
        Format: manifold://<spiral>.<level>.<position>[/time/branch/meta]
        Example: manifold://0.3.42 (spiral 0, level 3, position 42)
        """
        base = f"manifold://{self.spiral}.{self.level}.{self.position}"
        if self.time or self.branch or self.meta_key:
            return f"{base}/{self.time}/{self.branch}/{self.meta_key}"
        return base
    
    @classmethod
    def from_uri(cls, uri: str) -> 'ManifoldAddress':
        """Parse a manifold URI"""
        if not uri.startswith("manifold://"):
            raise ValueError(f"Invalid manifold URI: {uri}")
        
        parts = uri[11:].split("/")
        coords = parts[0].split(".")
        
        spiral = int(coords[0]) if len(coords) > 0 else 0
        level = int(coords[1]) if len(coords) > 1 else 0
        position = int(coords[2]) if len(coords) > 2 else 0
        
        time_val = float(parts[1]) if len(parts) > 1 else 0.0
        branch = int(parts[2]) if len(parts) > 2 else 0
        meta_key = parts[3] if len(parts) > 3 else ""
        
        return cls(spiral, level, position, time_val, branch, meta_key)
    
    def serialize(self) -> bytes:
        """Compact binary serialization"""
        # Format: [spiral:2][level:1][position:4][time:8][branch:2][meta_len:2][meta:N]
        meta_bytes = self.meta_key.encode('utf-8')
        return struct.pack(
            '>HBIQHH',
            self.spiral,
            self.level,
            self.position,
            int(self.time * 1000),  # ms precision
            self.branch,
            len(meta_bytes)
        ) + meta_bytes
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'ManifoldAddress':
        """Deserialize from binary with bounds checking"""
        # Minimum size: 17 bytes header
        if len(data) < 17:
            raise ValueError(f"ManifoldAddress requires at least 17 bytes, got {len(data)}")
        
        spiral, level, position, time_ms, branch, meta_len = struct.unpack('>HBIQHH', data[:17])
        
        # Validate meta_len doesn't exceed remaining data
        if meta_len > len(data) - 17:
            raise ValueError(f"Meta length {meta_len} exceeds available data")
        
        # Limit meta_key size to prevent memory exhaustion
        if meta_len > 10000:
            raise ValueError(f"Meta key too large: {meta_len} bytes")
        
        meta_key = data[17:17+meta_len].decode('utf-8') if meta_len > 0 else ""
        return cls(spiral, level, position, time_ms / 1000.0, branch, meta_key)
    
    def distance_to(self, other: 'ManifoldAddress') -> float:
        """Calculate manifold distance between addresses"""
        # Euclidean distance in manifold space
        d_spiral = (self.spiral - other.spiral) ** 2
        d_level = (self.level - other.level) ** 2
        d_position = (self.position - other.position) ** 2
        return math.sqrt(d_spiral + d_level + d_position)
    
    def __str__(self) -> str:
        return f"({self.spiral}, {self.level}, {self.position})"


# =============================================================================
# MANIFOLD DATAGRAM - The Payload IS the Model
# =============================================================================

@dataclass
class ManifoldDatagram:
    """
    The fundamental unit of manifold networking.
    
    This replaces IP packets with manifold datagrams.
    The payload is NOT raw data — it's a mathematical description.
    
    Structure on wire:
        [version:1][flags:1][src_addr:17+][dst_addr:17+][payload_type:1][payload_len:4][payload:N][checksum:4]
    """
    source: ManifoldAddress
    destination: ManifoldAddress
    payload_type: int    # What kind of math is in payload
    payload: bytes       # The mathematical description
    sequence: int = 0
    flags: int = 0
    ttl: int = 64        # Time-to-live (hops through manifold)
    timestamp: float = field(default_factory=time.time)
    
    # Payload types (what kind of math)
    TYPE_FUNCTION = 0x01      # Mathematical function f(x)
    TYPE_COORDINATE = 0x02    # Point on manifold surface
    TYPE_GRADIENT = 0x03      # Slope/direction at point
    TYPE_CURVATURE = 0x04     # Curvature tensor
    TYPE_TRANSFORM = 0x05     # Transformation matrix
    TYPE_WAVEFORM = 0x06      # Wave equation
    TYPE_MESH = 0x07          # Parametric surface
    TYPE_CONTENT = 0x08       # Dimensional content (presentation)
    TYPE_QUERY = 0x09         # Manifold query
    TYPE_RESPONSE = 0x0A      # Query response
    
    # Flags
    FLAG_FRAGMENT = 0x01
    FLAG_LAST_FRAGMENT = 0x02
    FLAG_COMPRESSED = 0x04
    FLAG_ENCRYPTED = 0x08
    FLAG_PRIORITY = 0x10
    FLAG_RELIABLE = 0x20
    
    VERSION = 1
    
    @property
    def checksum(self) -> int:
        """CRC32 of payload"""
        return zlib.crc32(self.payload) & 0xFFFFFFFF
    
    def serialize(self) -> bytes:
        """Serialize for wire transmission"""
        src_bytes = self.source.serialize()
        dst_bytes = self.destination.serialize()
        
        header = struct.pack(
            '>BBHBI',
            self.VERSION,
            self.flags,
            self.sequence,
            self.payload_type,
            len(self.payload)
        )
        
        # [header:9][src_len:2][src][dst_len:2][dst][payload][checksum:4]
        result = header
        result += struct.pack('>H', len(src_bytes)) + src_bytes
        result += struct.pack('>H', len(dst_bytes)) + dst_bytes
        result += self.payload
        result += struct.pack('>I', self.checksum)
        
        return result
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'ManifoldDatagram':
        """Deserialize from wire format with bounds checking"""
        # Minimum size: 9 byte header + 2 src_len + 2 dst_len + 4 checksum = 17 bytes minimum
        if len(data) < 17:
            raise ValueError(f"ManifoldDatagram requires at least 17 bytes, got {len(data)}")
        
        version, flags, sequence, payload_type, payload_len = struct.unpack('>BBHBI', data[:9])
        
        # Validate version
        if version != cls.VERSION:
            raise ValueError(f"Unsupported datagram version: {version}")
        
        # Validate payload_len is reasonable (max 100MB)
        if payload_len > 100 * 1024 * 1024:
            raise ValueError(f"Payload too large: {payload_len} bytes")
        
        offset = 9
        
        # Check bounds for src_len read
        if offset + 2 > len(data):
            raise ValueError("Truncated data: cannot read source length")
        src_len = struct.unpack('>H', data[offset:offset+2])[0]
        offset += 2
        
        # Check bounds for source address
        if offset + src_len > len(data):
            raise ValueError("Truncated data: cannot read source address")
        source = ManifoldAddress.deserialize(data[offset:offset+src_len])
        offset += src_len
        
        # Check bounds for dst_len read
        if offset + 2 > len(data):
            raise ValueError("Truncated data: cannot read destination length")
        dst_len = struct.unpack('>H', data[offset:offset+2])[0]
        offset += 2
        
        # Check bounds for destination address
        if offset + dst_len > len(data):
            raise ValueError("Truncated data: cannot read destination address")
        destination = ManifoldAddress.deserialize(data[offset:offset+dst_len])
        offset += dst_len
        
        # Check bounds for payload
        if offset + payload_len > len(data):
            raise ValueError("Truncated data: cannot read payload")
        payload = data[offset:offset+payload_len]
        offset += payload_len
        
        # Check bounds for checksum
        if offset + 4 > len(data):
            raise ValueError("Truncated data: cannot read checksum")
        received_checksum = struct.unpack('>I', data[offset:offset+4])[0]
        actual_checksum = zlib.crc32(payload) & 0xFFFFFFFF
        
        if received_checksum != actual_checksum:
            raise ValueError("Checksum mismatch")
        
        return cls(
            source=source,
            destination=destination,
            payload_type=payload_type,
            payload=payload,
            sequence=sequence,
            flags=flags
        )


# =============================================================================
# MANIFOLD ROUTER - Routing Through Mathematical Space
# =============================================================================

class ManifoldRouter:
    """
    Routes datagrams through manifold space.
    
    Instead of IP routing tables, we have manifold navigation.
    The "shortest path" is the geodesic on the manifold surface.
    """
    
    def __init__(self):
        # Routing table: destination_pattern -> handler
        self.routes: Dict[Tuple[int, int, int], Callable] = {}
        
        # Content at each coordinate
        self.content: Dict[Tuple[int, int, int], Any] = {}
        
        # Level handlers (for OSI layer processing)
        self.layer_handlers: Dict[OSIHelixLayer, Callable] = {}
    
    def register_route(self, spiral: int, level: int, position: int, handler: Callable):
        """Register a handler for a manifold coordinate"""
        self.routes[(spiral, level, position)] = handler
    
    def register_content(self, spiral: int, level: int, position: int, content: Any):
        """Place content at a manifold coordinate"""
        self.content[(spiral, level, position)] = content
    
    def register_layer_handler(self, layer: OSIHelixLayer, handler: Callable):
        """Register handler for an OSI-Helix layer"""
        self.layer_handlers[layer] = handler
    
    def route(self, datagram: ManifoldDatagram) -> Optional[Any]:
        """
        Route a datagram to its destination.
        
        Processing follows the helix upward:
        1. Physical: Receive raw bits
        2. Data Link: Verify frame integrity
        3. Network: Route by coordinates
        4. Transport: Handle flow/reliability
        5. Session: Manage connection state
        6. Presentation: Decode payload
        7. Application: Deliver to handler
        """
        dest = datagram.destination
        
        # Process through each layer up to destination level
        for layer_num in range(dest.level + 1):
            layer = OSIHelixLayer(layer_num)
            if layer in self.layer_handlers:
                result = self.layer_handlers[layer](datagram, layer)
                if result is False:  # Handler rejected
                    return None
        
        # Look up handler for destination coordinate
        coord = dest.as_tuple
        
        # Exact match
        if coord in self.routes:
            return self.routes[coord](datagram)
        
        # Content at coordinate
        if coord in self.content:
            return self.content[coord]
        
        # Wildcard routing (any position at this spiral/level)
        wildcard = (dest.spiral, dest.level, -1)
        if wildcard in self.routes:
            return self.routes[wildcard](datagram)
        
        return None
    
    def calculate_geodesic(self, src: ManifoldAddress, dst: ManifoldAddress) -> List[ManifoldAddress]:
        """
        Calculate the geodesic (shortest path) between two points.
        On a helix manifold, this follows the spiral structure.
        """
        path = [src]
        
        # Move vertically through levels first (helix axis)
        current_level = src.level
        while current_level != dst.level:
            step = 1 if dst.level > current_level else -1
            current_level += step
            path.append(ManifoldAddress(src.spiral, current_level, src.position))
        
        # Then move along position (spiral rotation)
        current_pos = src.position
        while current_pos != dst.position:
            step = 1 if dst.position > current_pos else -1
            current_pos += step
            path.append(ManifoldAddress(src.spiral, dst.level, current_pos))
        
        # Finally change spiral if needed
        if src.spiral != dst.spiral:
            path.append(dst)
        
        return path


# =============================================================================
# OSI-MANIFOLD STACK - Full Protocol Stack
# =============================================================================

class OSIManifoldStack:
    """
    The complete OSI-Manifold protocol stack.
    
    Data encapsulation follows the helix structure:
    - Going DOWN: Add headers at each level
    - Going UP: Process and strip headers
    
    Each layer adds dimensional meaning.
    """
    
    def __init__(self, local_address: ManifoldAddress):
        self.local_address = local_address
        self.router = ManifoldRouter()
        self.sequence = 0
        
        # Statistics per layer
        self.layer_stats = {layer: {"tx": 0, "rx": 0} for layer in OSIHelixLayer}
        
        # Register default layer handlers
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Set up default processing at each layer"""
        
        def physical_handler(dg, layer):
            """Layer 0: Raw signal validation"""
            self.layer_stats[layer]["rx"] += 1
            return True
        
        def datalink_handler(dg, layer):
            """Layer 1: Frame integrity check"""
            self.layer_stats[layer]["rx"] += 1
            return dg.checksum == (zlib.crc32(dg.payload) & 0xFFFFFFFF)
        
        def network_handler(dg, layer):
            """Layer 2: Coordinate routing"""
            self.layer_stats[layer]["rx"] += 1
            return dg.ttl > 0
        
        def transport_handler(dg, layer):
            """Layer 3: Flow control"""
            self.layer_stats[layer]["rx"] += 1
            return True
        
        def session_handler(dg, layer):
            """Layer 4: Connection state"""
            self.layer_stats[layer]["rx"] += 1
            return True
        
        def presentation_handler(dg, layer):
            """Layer 5: Decode payload format"""
            self.layer_stats[layer]["rx"] += 1
            if dg.flags & ManifoldDatagram.FLAG_COMPRESSED:
                # Would decompress here
                pass
            return True
        
        def application_handler(dg, layer):
            """Layer 6: Application delivery"""
            self.layer_stats[layer]["rx"] += 1
            return True
        
        self.router.register_layer_handler(OSIHelixLayer.PHYSICAL, physical_handler)
        self.router.register_layer_handler(OSIHelixLayer.DATA_LINK, datalink_handler)
        self.router.register_layer_handler(OSIHelixLayer.NETWORK, network_handler)
        self.router.register_layer_handler(OSIHelixLayer.TRANSPORT, transport_handler)
        self.router.register_layer_handler(OSIHelixLayer.SESSION, session_handler)
        self.router.register_layer_handler(OSIHelixLayer.PRESENTATION, presentation_handler)
        self.router.register_layer_handler(OSIHelixLayer.APPLICATION, application_handler)
    
    def send(self, destination: ManifoldAddress, payload_type: int, payload: bytes, 
             flags: int = 0) -> ManifoldDatagram:
        """
        Send data to a manifold address.
        
        Encapsulation happens automatically based on destination level.
        """
        self.sequence += 1
        
        datagram = ManifoldDatagram(
            source=self.local_address,
            destination=destination,
            payload_type=payload_type,
            payload=payload,
            sequence=self.sequence,
            flags=flags
        )
        
        # Track TX at each layer
        for layer_num in range(destination.level + 1):
            self.layer_stats[OSIHelixLayer(layer_num)]["tx"] += 1
        
        return datagram
    
    def receive(self, datagram: ManifoldDatagram) -> Optional[Any]:
        """
        Receive and process a datagram.
        Routes through all appropriate layers.
        """
        return self.router.route(datagram)
    
    def send_function(self, destination: ManifoldAddress, 
                      func_type: str, params: Dict[str, float]) -> ManifoldDatagram:
        """
        Send a mathematical function.
        
        Example: send_function(addr, "sin", {"freq": 440, "amp": 1.0})
        The receiver evaluates: f(t) = amp * sin(2π * freq * t)
        """
        payload = json.dumps({"t": func_type, "p": params}).encode('utf-8')
        return self.send(destination, ManifoldDatagram.TYPE_FUNCTION, payload)
    
    def send_coordinate(self, destination: ManifoldAddress,
                        point: Tuple[float, float, float]) -> ManifoldDatagram:
        """Send a point on the manifold surface"""
        payload = struct.pack('>fff', *point)
        return self.send(destination, ManifoldDatagram.TYPE_COORDINATE, payload)
    
    def send_content(self, destination: ManifoldAddress, 
                     content: Dict[str, Any]) -> ManifoldDatagram:
        """Send dimensional content (presentation, etc)"""
        payload = json.dumps(content).encode('utf-8')
        return self.send(destination, ManifoldDatagram.TYPE_CONTENT, payload)


# =============================================================================
# HTTP-TO-MANIFOLD BRIDGE - Traditional Web to Dimensional
# =============================================================================

class HTTPManifoldBridge:
    """
    Bridge between HTTP requests and manifold addresses.
    
    Maps URL paths to manifold coordinates:
        /                    -> (0, 0, 0)   # Home = origin
        /level/3             -> (0, 3, 0)   # Jump to level
        /spiral/1/level/2    -> (1, 2, 0)   # Specific spiral
        /s/0/l/3/p/42        -> (0, 3, 42)  # Full coordinate
        
    Query params can add higher dimensions:
        ?t=1.5&b=2           -> time=1.5, branch=2
    """
    
    @staticmethod
    def url_to_address(path: str, query: Dict[str, str] = None) -> ManifoldAddress:
        """Convert URL path to manifold address"""
        query = query or {}
        
        spiral = 0
        level = 0
        position = 0
        
        # Parse path segments
        parts = [p for p in path.split('/') if p]
        
        i = 0
        while i < len(parts):
            key = parts[i].lower()
            value = parts[i + 1] if i + 1 < len(parts) else None
            
            if key in ('s', 'spiral') and value:
                spiral = int(value)
                i += 2
            elif key in ('l', 'level') and value:
                level = int(value)
                i += 2
            elif key in ('p', 'position', 'pos') and value:
                position = int(value)
                i += 2
            else:
                # Could be just a level number
                try:
                    level = int(key)
                except ValueError:
                    pass
                i += 1
        
        # Parse query params for higher dimensions
        time_val = float(query.get('t', query.get('time', 0)))
        branch = int(query.get('b', query.get('branch', 0)))
        meta_key = query.get('m', query.get('meta', ''))
        
        return ManifoldAddress(spiral, level, position, time_val, branch, meta_key)
    
    @staticmethod
    def address_to_url(addr: ManifoldAddress) -> str:
        """Convert manifold address to URL path"""
        url = f"/s/{addr.spiral}/l/{addr.level}/p/{addr.position}"
        params = []
        if addr.time:
            params.append(f"t={addr.time}")
        if addr.branch:
            params.append(f"b={addr.branch}")
        if addr.meta_key:
            params.append(f"m={addr.meta_key}")
        if params:
            url += "?" + "&".join(params)
        return url


# =============================================================================
# CONTENT TYPES - Mathematical Payloads
# =============================================================================

def encode_sine_wave(frequency: float, amplitude: float = 1.0, phase: float = 0.0) -> bytes:
    """
    Encode a sine wave as mathematical description.
    
    Instead of 44100 samples/second, we send:
    {type: "sin", freq: 440, amp: 1.0, phase: 0}  = ~40 bytes
    
    Any computer can evaluate: f(t) = amp * sin(2π * freq * t + phase)
    """
    payload = {
        "type": "sin",
        "freq": frequency,
        "amp": amplitude,
        "phase": phase
    }
    return json.dumps(payload).encode('utf-8')


def encode_parametric_surface(u_expr: str, v_expr: str, u_range: Tuple, v_range: Tuple) -> bytes:
    """
    Encode a 3D surface as parametric equations.
    
    Instead of millions of vertices, we send:
    {u: "cos(u)*sin(v)", v: "sin(u)*sin(v)", w: "cos(v)", u_range: [0, 2π], v_range: [0, π]}
    
    Any computer can evaluate the mesh locally.
    """
    payload = {
        "type": "parametric_surface",
        "u_expr": u_expr,
        "v_expr": v_expr,
        "u_range": list(u_range),
        "v_range": list(v_range)
    }
    return json.dumps(payload).encode('utf-8')


def encode_transformation(matrix: List[List[float]]) -> bytes:
    """
    Encode a transformation matrix.
    
    16 floats = 64 bytes of pure mathematics.
    Can represent any 3D transformation: rotate, scale, translate, project.
    """
    flat = [v for row in matrix for v in row]
    return struct.pack('>16f', *flat)


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def create_dimensional_server_content() -> Dict[ManifoldAddress, bytes]:
    """
    Create the content structure for the dimensional landing page.
    
    Each level of the helix is a different depth of content.
    Navigating the manifold IS navigating the website.
    """
    content = {}
    
    # Level 0: POINT - The core insight (origin of all)
    content[ManifoldAddress(0, 0, 0)] = json.dumps({
        "title": "Any Computer Can Decipher Math",
        "insight": "Math is the universal language. Send the equation, not the data.",
        "level": "POINT",
        "dimension": "0D"
    }).encode('utf-8')
    
    # Level 1: LINE - The paradigm
    content[ManifoldAddress(0, 1, 0)] = json.dumps({
        "title": "The Manifold Paradigm",
        "content": "Instead of sending data as bytes, ButterflyFX sends the mathematical description that generates that data.",
        "level": "LINE",
        "dimension": "1D"
    }).encode('utf-8')
    
    # Level 2: PLANE - The helix structure
    content[ManifoldAddress(0, 2, 0)] = json.dumps({
        "title": "The 7-Level Helix",
        "levels": [
            {"level": 0, "name": "POINT", "dim": "0D", "purpose": "Core value"},
            {"level": 1, "name": "LINE", "dim": "1D", "purpose": "Sequence"},
            {"level": 2, "name": "PLANE", "dim": "2D", "purpose": "Grid"},
            {"level": 3, "name": "VOLUME", "dim": "3D", "purpose": "Spatial"},
            {"level": 4, "name": "TIME", "dim": "4D", "purpose": "Animation"},
            {"level": 5, "name": "PARALLEL", "dim": "5D", "purpose": "Alternatives"},
            {"level": 6, "name": "META", "dim": "6D", "purpose": "Abstraction"},
        ],
        "level": "PLANE",
        "dimension": "2D"
    }).encode('utf-8')
    
    # Level 3: VOLUME - Architecture
    content[ManifoldAddress(0, 3, 0)] = json.dumps({
        "title": "The Architecture",
        "layers": [
            "APPLICATION: Presentations, 3D, Data Explorer",
            "SERVER: DimensionalServer, ManifoldProtocol, REST",
            "TRANSPORT: HelixPacket, AudioTransport, ManifoldServer",
            "FOUNDATION: HelixDB, HelixFS, HelixStore, HelixGraph",
            "PRIMITIVES: DimensionalType, LazyValue, HelixContext",
            "CORE: HelixKernel, ManifoldSubstrate, GenerativeManifold"
        ],
        "level": "VOLUME",
        "dimension": "3D"
    }).encode('utf-8')
    
    # Level 4: TIME - Demo (animation/interaction)
    content[ManifoldAddress(0, 4, 0)] = json.dumps({
        "title": "See It In Action",
        "demos": [
            {"name": "Dimensional Navigator", "url": "/dimensional_demo.html"},
            {"name": "3D Graphics Engine", "url": "/graphics3d_demo.html"},
            {"name": "Timeline Presentations", "url": "/presentation_demo.html"}
        ],
        "level": "TIME",
        "dimension": "4D"
    }).encode('utf-8')
    
    # Level 5: PARALLEL - Open source repos (alternative paths)
    content[ManifoldAddress(0, 5, 0)] = json.dumps({
        "title": "Open Source Infrastructure",
        "repos": [
            {"name": "butterfly", "url": "https://github.com/kenbin64/butterfly.git", "desc": "Mathematical kernel"},
            {"name": "dimensionsos", "url": "https://github.com/kenbin64/dimensionsos.git", "desc": "Networking layer"},
            {"name": "butterflyfxpython", "url": "https://github.com/kenbin64/butterflyfxpython.git", "desc": "Complete framework"}
        ],
        "license": "CC BY 4.0",
        "attribution": "Kenneth Bingham",
        "level": "PARALLEL",
        "dimension": "5D"
    }).encode('utf-8')
    
    # Level 6: META - Get started (overview/abstraction)
    content[ManifoldAddress(0, 6, 0)] = json.dumps({
        "title": "Get Started",
        "install": "git clone https://github.com/kenbin64/butterflyfxpython.git",
        "quickstart": "from helix import HelixKernel, GenerativeManifold",
        "tagline": "ButterflyFX — Because any computer can decipher math.",
        "level": "META",
        "dimension": "6D"
    }).encode('utf-8')
    
    return content


if __name__ == "__main__":
    # Demo: Create stack and route content
    local_addr = ManifoldAddress(0, 0, 0)
    stack = OSIManifoldStack(local_addr)
    
    # Register dimensional content
    for addr, content in create_dimensional_server_content().items():
        stack.router.register_content(addr.spiral, addr.level, addr.position, content)
    
    # Test routing
    print("OSI-Manifold Transport Demo")
    print("=" * 50)
    
    # Navigate through levels
    for level in range(7):
        dest = ManifoldAddress(0, level, 0)
        dg = stack.send(dest, ManifoldDatagram.TYPE_CONTENT, b'')
        result = stack.receive(dg)
        
        if result:
            data = json.loads(result.decode('utf-8'))
            print(f"Level {level} ({LAYER_INFO[OSIHelixLayer(level)]['helix']}): {data['title']}")
    
    print()
    
    # Demo URL to address conversion
    print("HTTP-to-Manifold Bridge:")
    urls = ["/", "/level/3", "/s/0/l/5/p/0", "/2"]
    for url in urls:
        addr = HTTPManifoldBridge.url_to_address(url)
        print(f"  {url} -> {addr.to_uri()}")
