"""
ButterflyFX Helix Transport - Network Transport Over Dimensional Structure

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

Part of DimensionsOS - Open source networking layer.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

The helix IS the transport format. Data flows through 7 levels that mirror
the OSI model's 7 layers. No conversion to original file needed - stream
the dimensional representation directly.

OSI Model ↔ Helix Level Mapping:
    Level 0: Physical    → Binary/Bits (raw signal)
    Level 1: Data Link   → Frame/Packet structure
    Level 2: Network     → Addressing/Routing coordinates
    Level 3: Transport   → Segments/Flow control
    Level 4: Session     → Connection state
    Level 5: Presentation→ Encoding/Format (structured data)
    Level 6: Application → User payload

The Fibonacci spiral nature means:
    - Each level builds on the previous
    - Data can be processed level-by-level
    - Partial transmission is meaningful
    - Natural error boundaries per level

PRINCIPLE:
    Don't reconstruct the file - stream the helix.
    The receiver understands dimensional coordinates.
    The wire carries (spiral, level, payload) tuples.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Iterator, Tuple, Callable, Generator
from enum import Enum, auto
import struct
import zlib
import base64
import hashlib
import time


# =============================================================================
# TRANSPORT LAYER DEFINITIONS - Helix ↔ OSI Mapping
# =============================================================================

class TransportLevel(Enum):
    """
    Helix levels mapped to OSI model layers.
    The helix naturally provides the transport stack.
    """
    PHYSICAL = 0      # Raw bits, signals - Level 0
    DATA_LINK = 1     # Frames, MAC addressing - Level 1
    NETWORK = 2       # IP addressing, routing - Level 2
    TRANSPORT = 3     # TCP/UDP segments, flow - Level 3
    SESSION = 4       # Connection management - Level 4
    PRESENTATION = 5  # Encoding, encryption - Level 5
    APPLICATION = 6   # User data payload - Level 6


# Level names for display
TRANSPORT_NAMES = {
    0: "PHYSICAL",
    1: "DATA_LINK", 
    2: "NETWORK",
    3: "TRANSPORT",
    4: "SESSION",
    5: "PRESENTATION",
    6: "APPLICATION",
}


# =============================================================================
# HELIX PACKET - The unit of transport
# =============================================================================

@dataclass
class HelixPacket:
    """
    A packet in the helix transport model.
    
    This is what goes "down the wire" - not a file, but a dimensional coordinate
    with its payload. The receiver understands helix structure.
    
    Structure:
        [spiral:4][level:1][seq:4][flags:1][len:4][payload:N][checksum:4]
    """
    spiral: int           # Which dimension/channel
    level: int            # Which OSI-mapped layer (0-6)
    sequence: int         # Packet sequence number
    payload: bytes        # The actual data
    flags: int = 0        # Control flags
    timestamp: float = field(default_factory=time.time)
    
    # Flag constants
    FLAG_FRAGMENT = 0x01      # This is a fragment
    FLAG_LAST_FRAGMENT = 0x02 # Last fragment in sequence
    FLAG_COMPRESSED = 0x04    # Payload is compressed
    FLAG_ENCRYPTED = 0x08     # Payload is encrypted
    FLAG_PRIORITY = 0x10      # High priority packet
    FLAG_ACK_REQUIRED = 0x20  # Requires acknowledgment
    
    @property
    def transport_level(self) -> TransportLevel:
        return TransportLevel(self.level)
    
    @property
    def level_name(self) -> str:
        return TRANSPORT_NAMES.get(self.level, f"LEVEL_{self.level}")
    
    @property
    def checksum(self) -> int:
        """CRC32 checksum of payload"""
        return zlib.crc32(self.payload) & 0xFFFFFFFF
    
    def serialize(self) -> bytes:
        """
        Serialize packet for wire transmission.
        
        Format: [spiral:4][level:1][seq:4][flags:1][len:4][payload:N][checksum:4]
        Total header: 14 bytes + payload + 4 byte checksum
        """
        header = struct.pack(
            '>IBIB I',  # Big-endian: uint32, uint8, uint32, uint8, uint32
            self.spiral,
            self.level,
            self.sequence,
            self.flags,
            len(self.payload)
        )
        checksum = struct.pack('>I', self.checksum)
        return header + self.payload + checksum
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'HelixPacket':
        """Deserialize packet from wire format with bounds checking"""
        # Minimum size: 14 byte header + 4 byte checksum = 18 bytes
        if len(data) < 18:
            raise ValueError(f"HelixPacket requires at least 18 bytes, got {len(data)}")
        
        # Parse header (14 bytes)
        spiral, level, sequence, flags, payload_len = struct.unpack('>IBIB I', data[:14])
        
        # Validate payload_len is reasonable (max 100MB)
        if payload_len > 100 * 1024 * 1024:
            raise ValueError(f"Payload too large: {payload_len} bytes")
        
        # Check we have enough data for payload and checksum
        required_len = 14 + payload_len + 4
        if len(data) < required_len:
            raise ValueError(f"Truncated packet: need {required_len} bytes, got {len(data)}")
        
        # Extract payload
        payload = data[14:14 + payload_len]
        
        # Verify checksum
        received_checksum = struct.unpack('>I', data[14 + payload_len:18 + payload_len])[0]
        actual_checksum = zlib.crc32(payload) & 0xFFFFFFFF
        
        if received_checksum != actual_checksum:
            raise ValueError(f"Checksum mismatch: {received_checksum} != {actual_checksum}")
        
        return cls(
            spiral=spiral,
            level=level,
            sequence=sequence,
            payload=payload,
            flags=flags
        )
    
    @property
    def wire_size(self) -> int:
        """Total size on wire including headers"""
        return 18 + len(self.payload)  # 14 header + payload + 4 checksum
    
    def compress(self) -> 'HelixPacket':
        """Return compressed version of packet"""
        compressed = zlib.compress(self.payload, level=6)
        return HelixPacket(
            spiral=self.spiral,
            level=self.level,
            sequence=self.sequence,
            payload=compressed,
            flags=self.flags | self.FLAG_COMPRESSED,
            timestamp=self.timestamp
        )
    
    def decompress(self) -> 'HelixPacket':
        """Return decompressed version of packet"""
        if not (self.flags & self.FLAG_COMPRESSED):
            return self
        decompressed = zlib.decompress(self.payload)
        return HelixPacket(
            spiral=self.spiral,
            level=self.level,
            sequence=self.sequence,
            payload=decompressed,
            flags=self.flags & ~self.FLAG_COMPRESSED,
            timestamp=self.timestamp
        )
    
    def __repr__(self) -> str:
        return f"HelixPacket(spiral={self.spiral}, level={self.level}/{self.level_name}, seq={self.sequence}, {len(self.payload)} bytes)"


# =============================================================================
# HELIX STREAM - Continuous dimensional data flow
# =============================================================================

class HelixStream:
    """
    A stream of helix packets flowing through dimensional coordinates.
    
    Think of this as a "dimensional pipe" - data flows through levels,
    each level processing its portion of the stack.
    
    Usage:
        stream = HelixStream(spiral=0)
        
        # Send data at application level
        stream.send(level=6, data=b"Hello World")
        
        # Data flows down through levels
        for packet in stream.drain():
            wire.transmit(packet.serialize())
    """
    
    def __init__(self, spiral: int = 0, mtu: int = 1500):
        self.spiral = spiral
        self.mtu = mtu  # Maximum transmission unit per packet
        self._sequence = 0
        self._outbound: List[HelixPacket] = []
        self._inbound: Dict[int, List[HelixPacket]] = {i: [] for i in range(7)}
        self._reassembly: Dict[Tuple[int, int], List[HelixPacket]] = {}
    
    def send(self, level: int, data: bytes, compress: bool = False) -> List[HelixPacket]:
        """
        Send data at a specific level.
        
        Data is packetized and queued for transmission.
        Large data is fragmented across multiple packets.
        
        Args:
            level: Which OSI-mapped level (0-6)
            data: Raw bytes to send
            compress: Whether to compress payload
            
        Returns:
            List of packets created
        """
        packets = []
        
        # Fragment if needed
        max_payload = self.mtu - 18  # Reserve for headers
        fragments = [data[i:i+max_payload] for i in range(0, len(data), max_payload)]
        
        for i, fragment in enumerate(fragments):
            flags = 0
            if len(fragments) > 1:
                flags |= HelixPacket.FLAG_FRAGMENT
                if i == len(fragments) - 1:
                    flags |= HelixPacket.FLAG_LAST_FRAGMENT
            
            packet = HelixPacket(
                spiral=self.spiral,
                level=level,
                sequence=self._sequence,
                payload=fragment,
                flags=flags
            )
            
            if compress:
                packet = packet.compress()
            
            packets.append(packet)
            self._outbound.append(packet)
            self._sequence += 1
        
        return packets
    
    def receive(self, packet: HelixPacket) -> Optional[bytes]:
        """
        Receive a packet and potentially reassemble.
        
        Returns complete payload if reassembly is done, None if waiting for fragments.
        """
        # Decompress if needed
        if packet.flags & HelixPacket.FLAG_COMPRESSED:
            packet = packet.decompress()
        
        # Handle fragmentation
        if packet.flags & HelixPacket.FLAG_FRAGMENT:
            key = (packet.spiral, packet.level)
            if key not in self._reassembly:
                self._reassembly[key] = []
            self._reassembly[key].append(packet)
            
            if packet.flags & HelixPacket.FLAG_LAST_FRAGMENT:
                # Reassemble
                fragments = sorted(self._reassembly[key], key=lambda p: p.sequence)
                complete = b''.join(f.payload for f in fragments)
                del self._reassembly[key]
                return complete
            return None
        
        # Non-fragmented packet
        self._inbound[packet.level].append(packet)
        return packet.payload
    
    def drain(self) -> Iterator[HelixPacket]:
        """Drain all outbound packets"""
        while self._outbound:
            yield self._outbound.pop(0)
    
    def get_level(self, level: int) -> List[bytes]:
        """Get all received data at a level"""
        return [p.payload for p in self._inbound[level]]
    
    @property
    def stats(self) -> Dict[str, Any]:
        return {
            'spiral': self.spiral,
            'sequence': self._sequence,
            'outbound_queued': len(self._outbound),
            'inbound_per_level': {TRANSPORT_NAMES[i]: len(self._inbound[i]) for i in range(7)},
            'reassembly_pending': len(self._reassembly),
        }


# =============================================================================
# HELIX TRANSPORT - Full transport protocol
# =============================================================================

class HelixTransport:
    """
    Full helix transport protocol.
    
    This is the complete model for sending data "down the wire" using
    the 7-level helix structure as the transport stack.
    
    The helix IS the protocol:
        - Level 0 (Physical): Raw bits
        - Level 1 (Data Link): Framing
        - Level 2 (Network): Routing via spiral coordinates
        - Level 3 (Transport): Sequencing, flow control
        - Level 4 (Session): Connection state
        - Level 5 (Presentation): Encoding (no file conversion needed!)
        - Level 6 (Application): User payload
    
    Usage:
        transport = HelixTransport()
        
        # Ingest data directly - no file conversion
        transport.ingest(image_bytes, content_type='image/png', spiral=0)
        
        # Stream packets
        for packet in transport.stream():
            network.send(packet.serialize())
        
        # Receive and reconstruct
        for wire_data in network.receive():
            packet = HelixPacket.deserialize(wire_data)
            transport.receive(packet)
        
        # Get data - still in helix form, or assemble if needed
        data = transport.extract(spiral=0)
    """
    
    def __init__(self, mtu: int = 1500):
        self.mtu = mtu
        self._streams: Dict[int, HelixStream] = {}
        self._storage: Dict[Tuple[int, int], bytes] = {}  # (spiral, level) -> data
        self._metadata: Dict[int, Dict] = {}  # spiral -> metadata
        self._sequence = 0
    
    def _get_stream(self, spiral: int) -> HelixStream:
        """Get or create stream for spiral"""
        if spiral not in self._streams:
            self._streams[spiral] = HelixStream(spiral=spiral, mtu=self.mtu)
        return self._streams[spiral]
    
    # -------------------------------------------------------------------------
    # Ingestion - Data enters the helix
    # -------------------------------------------------------------------------
    
    def ingest(
        self,
        data: bytes,
        spiral: int = 0,
        level: int = 6,
        content_type: Optional[str] = None,
        compress: bool = True
    ) -> List[HelixPacket]:
        """
        Ingest data into the transport layer.
        
        Data is NOT converted to a file - it remains in helix form.
        It's packetized for transmission through the 7-level stack.
        
        Args:
            data: Raw bytes to transport
            spiral: Dimensional channel
            level: OSI-mapped level (default: APPLICATION)
            content_type: Optional MIME type for metadata
            compress: Whether to compress
            
        Returns:
            List of packets created
        """
        # Store metadata
        self._metadata[spiral] = {
            'content_type': content_type,
            'size': len(data),
            'level': level,
            'timestamp': time.time(),
            'hash': hashlib.sha256(data).hexdigest()[:16],
        }
        
        # Store raw data
        self._storage[(spiral, level)] = data
        
        # Create packets via stream
        stream = self._get_stream(spiral)
        return stream.send(level, data, compress=compress)
    
    def ingest_layered(
        self,
        layers: Dict[int, bytes],
        spiral: int = 0
    ) -> List[HelixPacket]:
        """
        Ingest data with explicit layer separation.
        
        Different data for different levels - true OSI separation.
        
        Args:
            layers: Dict mapping level -> data
            spiral: Dimensional channel
            
        Returns:
            All packets created
        """
        all_packets = []
        stream = self._get_stream(spiral)
        
        for level, data in layers.items():
            self._storage[(spiral, level)] = data
            packets = stream.send(level, data)
            all_packets.extend(packets)
        
        return all_packets
    
    # -------------------------------------------------------------------------
    # Streaming - Data flows through the helix
    # -------------------------------------------------------------------------
    
    def stream(self, spiral: Optional[int] = None) -> Generator[HelixPacket, None, None]:
        """
        Stream packets from the transport.
        
        This is what goes "down the wire" - helix packets, not files.
        
        Args:
            spiral: Specific spiral, or all if None
        
        Yields:
            HelixPacket objects ready for transmission
        """
        if spiral is not None:
            stream = self._streams.get(spiral)
            if stream:
                yield from stream.drain()
        else:
            for stream in self._streams.values():
                yield from stream.drain()
    
    def stream_level(self, level: int) -> Generator[HelixPacket, None, None]:
        """
        Stream all packets at a specific level.
        
        This allows level-by-level processing - just like the OSI model.
        """
        for stream in self._streams.values():
            for packet in list(stream._outbound):
                if packet.level == level:
                    stream._outbound.remove(packet)
                    yield packet
    
    # -------------------------------------------------------------------------
    # Reception - Data arrives from the wire
    # -------------------------------------------------------------------------
    
    def receive(self, packet: HelixPacket) -> Optional[bytes]:
        """
        Receive a packet from the wire.
        
        Handles reassembly and stores at coordinates.
        
        Returns:
            Complete data if reassembly done, None if waiting
        """
        stream = self._get_stream(packet.spiral)
        data = stream.receive(packet)
        
        if data:
            self._storage[(packet.spiral, packet.level)] = data
        
        return data
    
    def receive_wire(self, wire_data: bytes) -> Optional[bytes]:
        """Receive raw wire data"""
        packet = HelixPacket.deserialize(wire_data)
        return self.receive(packet)
    
    # -------------------------------------------------------------------------
    # Extraction - Get data from helix (no file conversion!)
    # -------------------------------------------------------------------------
    
    def extract(self, spiral: int, level: int = 6) -> Optional[bytes]:
        """
        Extract data at coordinates.
        
        Returns raw bytes - NOT converted to a file format.
        The data stays in its dimensional form.
        """
        return self._storage.get((spiral, level))
    
    def extract_all(self, spiral: int) -> Dict[int, bytes]:
        """Extract all levels for a spiral"""
        return {
            level: data 
            for (s, level), data in self._storage.items() 
            if s == spiral
        }
    
    # -------------------------------------------------------------------------
    # Display/Render - Use data without file conversion
    # -------------------------------------------------------------------------
    
    def as_data_url(self, spiral: int, level: int = 6) -> Optional[str]:
        """
        Get data as a data URL for direct display.
        
        This is how you display an image WITHOUT converting to a file:
            <img src="{data_url}" />
        
        The browser renders directly from the helix data.
        """
        data = self._storage.get((spiral, level))
        if not data:
            return None
        
        meta = self._metadata.get(spiral, {})
        content_type = meta.get('content_type', 'application/octet-stream')
        
        encoded = base64.b64encode(data).decode('utf-8')
        return f"data:{content_type};base64,{encoded}"
    
    def as_stream_chunk(self, spiral: int, level: int = 6, chunk_size: int = 8192) -> Generator[bytes, None, None]:
        """
        Yield data as streaming chunks.
        
        For streaming to clients without file materialization:
            for chunk in transport.as_stream_chunk(spiral=0):
                response.write(chunk)
        """
        data = self._storage.get((spiral, level))
        if data:
            for i in range(0, len(data), chunk_size):
                yield data[i:i+chunk_size]
    
    # -------------------------------------------------------------------------
    # Metrics
    # -------------------------------------------------------------------------
    
    @property
    def stats(self) -> Dict[str, Any]:
        total_stored = sum(len(d) for d in self._storage.values())
        return {
            'spirals': len(self._streams),
            'coordinates_used': len(self._storage),
            'total_bytes_stored': total_stored,
            'metadata_entries': len(self._metadata),
            'streams': {s: stream.stats for s, stream in self._streams.items()},
        }
    
    def __repr__(self) -> str:
        return f"HelixTransport({len(self._streams)} spirals, {len(self._storage)} coordinates)"


# =============================================================================
# HELIX WIRE FORMAT - Compact binary representation
# =============================================================================

class HelixWire:
    """
    Compact wire format for helix data.
    
    The entire helix state can be serialized and sent over any transport:
        - TCP/UDP socket
        - WebSocket
        - HTTP chunk
        - File (if persistence needed)
    
    Format:
        [MAGIC:4][VERSION:2][FLAGS:2][COUNT:4][PACKETS...]
        
    Where each packet is:
        [SPIRAL:4][LEVEL:1][SEQ:4][FLAGS:1][LEN:4][DATA:N][CRC:4]
    """
    
    MAGIC = b'HXTP'  # Helix Transport Protocol
    VERSION = 1
    
    @classmethod
    def encode(cls, transport: HelixTransport) -> bytes:
        """Encode entire transport state to wire format"""
        packets_data = []
        
        for (spiral, level), data in transport._storage.items():
            packet = HelixPacket(
                spiral=spiral,
                level=level,
                sequence=0,
                payload=data
            )
            packets_data.append(packet.serialize())
        
        # Build wire format
        header = struct.pack(
            '>4sHHI',
            cls.MAGIC,
            cls.VERSION,
            0,  # flags
            len(packets_data)
        )
        
        body = b''.join(
            struct.pack('>I', len(p)) + p 
            for p in packets_data
        )
        
        return header + body
    
    @classmethod
    def decode(cls, wire_data: bytes) -> HelixTransport:
        """Decode wire format to transport state"""
        # Parse header
        magic, version, flags, count = struct.unpack('>4sHHI', wire_data[:12])
        
        if magic != cls.MAGIC:
            raise ValueError(f"Invalid magic: {magic}")
        if version > cls.VERSION:
            raise ValueError(f"Unsupported version: {version}")
        
        # Parse packets
        transport = HelixTransport()
        offset = 12
        
        for _ in range(count):
            pkt_len = struct.unpack('>I', wire_data[offset:offset+4])[0]
            offset += 4
            
            packet = HelixPacket.deserialize(wire_data[offset:offset+pkt_len])
            transport._storage[(packet.spiral, packet.level)] = packet.payload
            offset += pkt_len
        
        return transport
    
    @classmethod
    def wire_stats(cls, wire_data: bytes) -> Dict[str, Any]:
        """Get stats about wire data without full decode"""
        magic, version, flags, count = struct.unpack('>4sHHI', wire_data[:12])
        return {
            'magic': magic.decode(),
            'version': version,
            'flags': flags,
            'packet_count': count,
            'total_bytes': len(wire_data),
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'TransportLevel',
    'TRANSPORT_NAMES',
    'HelixPacket',
    'HelixStream',
    'HelixTransport',
    'HelixWire',
]
