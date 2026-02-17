"""
ButterflyFX Dimensional IP Addressing

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

Part of ButterflyFX - Open source infrastructure.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

IP ADDRESSES AS DIMENSIONAL COORDINATES

Traditional IP:  192.168.1.1
Dimensional:     (x=192, y=168, z=1, m=1) or substrate position r=xyzm

The manifold IS the network. The OSI model IS the geometry.
Each octet maps to a dimensional axis:
    x: First octet (0-255)  - Spiral position
    y: Second octet (0-255) - Level position  
    z: Third octet (0-255)  - Radial position
    m: Fourth octet (0-255) - Meta/Branch

This creates a 4-dimensional address space where routing
becomes geometric pathfinding through the manifold.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Union
import struct
import time
import math
import hashlib
import ipaddress


# =============================================================================
# DIMENSIONAL IP ADDRESS
# =============================================================================

@dataclass(frozen=True)
class DimensionalIP:
    """
    An IP address encoded as dimensional coordinates.
    
    192.168.1.1 becomes (x=192, y=168, z=1, m=1)
    
    This is NOT just a mapping — the geometry IS the network topology.
    Subnets become regions. Routing becomes pathfinding.
    """
    x: int  # First octet: 0-255
    y: int  # Second octet: 0-255
    z: int  # Third octet: 0-255
    m: int  # Fourth octet: 0-255
    
    def __post_init__(self):
        """Validate ranges"""
        for name, val in [('x', self.x), ('y', self.y), ('z', self.z), ('m', self.m)]:
            if not 0 <= val <= 255:
                raise ValueError(f"{name} must be 0-255, got {val}")
    
    @classmethod
    def from_ip(cls, ip: str) -> 'DimensionalIP':
        """Convert traditional IP string to dimensional coordinates"""
        try:
            addr = ipaddress.IPv4Address(ip)
            packed = addr.packed
            return cls(x=packed[0], y=packed[1], z=packed[2], m=packed[3])
        except Exception as e:
            raise ValueError(f"Invalid IP address: {ip}") from e
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'DimensionalIP':
        """Create from 4 bytes"""
        if len(data) < 4:
            raise ValueError("DimensionalIP requires 4 bytes")
        return cls(x=data[0], y=data[1], z=data[2], m=data[3])
    
    def to_ip(self) -> str:
        """Convert back to traditional IP string"""
        return f"{self.x}.{self.y}.{self.z}.{self.m}"
    
    def to_bytes(self) -> bytes:
        """Compact 4-byte serialization"""
        return bytes([self.x, self.y, self.z, self.m])
    
    @property
    def as_tuple(self) -> Tuple[int, int, int, int]:
        """As XYZM tuple"""
        return (self.x, self.y, self.z, self.m)
    
    @property
    def as_vec4(self) -> Dict[str, float]:
        """As normalized Vec4 (0.0 to 1.0 range)"""
        return {
            'x': self.x / 255.0,
            'y': self.y / 255.0,
            'z': self.z / 255.0,
            'w': self.m / 255.0  # m maps to w for 4D
        }
    
    @property
    def substrate_position(self) -> str:
        """As substrate r=xyzm notation"""
        return f"r={self.x},{self.y},{self.z},{self.m}"
    
    def distance_to(self, other: 'DimensionalIP') -> float:
        """
        Calculate 4D Euclidean distance to another IP.
        This IS the network distance in manifold space.
        """
        return math.sqrt(
            (self.x - other.x) ** 2 +
            (self.y - other.y) ** 2 +
            (self.z - other.z) ** 2 +
            (self.m - other.m) ** 2
        )
    
    def is_same_subnet(self, other: 'DimensionalIP', prefix_length: int = 24) -> bool:
        """
        Check if in same subnet.
        In dimensional terms: are they in the same manifold region?
        """
        mask_bytes = prefix_length // 8
        coords1 = [self.x, self.y, self.z, self.m]
        coords2 = [other.x, other.y, other.z, other.m]
        return coords1[:mask_bytes] == coords2[:mask_bytes]
    
    def to_manifold_uri(self) -> str:
        """Convert to manifold URI format"""
        return f"manifold://{self.x}.{self.y}.{self.z}.{self.m}"
    
    def __str__(self) -> str:
        return f"D({self.x}, {self.y}, {self.z}, {self.m})"
    
    def __repr__(self) -> str:
        return f"DimensionalIP(x={self.x}, y={self.y}, z={self.z}, m={self.m})"


# =============================================================================
# DIMENSIONAL SUBNET
# =============================================================================

@dataclass
class DimensionalSubnet:
    """
    A subnet in dimensional space.
    
    A /24 network like 192.168.1.0/24 becomes a z-axis slice:
    All IPs where x=192, y=168, z=1, m varies 0-255
    
    This is a LINE in 4D space (1 degree of freedom).
    A /16 would be a PLANE (2 degrees of freedom).
    A /8 would be a VOLUME (3 degrees of freedom).
    """
    base: DimensionalIP
    prefix_length: int
    
    @classmethod
    def from_cidr(cls, cidr: str) -> 'DimensionalSubnet':
        """Parse CIDR notation like 192.168.1.0/24"""
        network = ipaddress.IPv4Network(cidr, strict=False)
        base_ip = DimensionalIP.from_ip(str(network.network_address))
        return cls(base=base_ip, prefix_length=network.prefixlen)
    
    @property
    def dimensionality(self) -> int:
        """
        How many dimensions vary in this subnet.
        /32 = 0D (point)
        /24 = 1D (line)
        /16 = 2D (plane)
        /8 = 3D (volume)
        /0 = 4D (full 4D space)
        """
        return (32 - self.prefix_length) // 8
    
    @property
    def helix_level(self) -> str:
        """Map subnet dimensionality to helix level"""
        levels = ['POINT', 'LINE', 'PLANE', 'VOLUME']
        return levels[min(self.dimensionality, 3)]
    
    def contains(self, ip: DimensionalIP) -> bool:
        """Check if IP is in this subnet (region of manifold)"""
        mask_bytes = self.prefix_length // 8
        base_coords = [self.base.x, self.base.y, self.base.z, self.base.m]
        ip_coords = [ip.x, ip.y, ip.z, ip.m]
        return base_coords[:mask_bytes] == ip_coords[:mask_bytes]
    
    def __str__(self) -> str:
        return f"{self.base.to_ip()}/{self.prefix_length} ({self.helix_level})"


# =============================================================================
# DIMENSIONAL PACKET
# =============================================================================

@dataclass
class DimensionalPacket:
    """
    A network packet with dimensional addressing.
    
    Instead of:
        src_ip: 192.168.1.10
        dst_ip: 192.168.1.20
        
    We have:
        src: D(192, 168, 1, 10)
        dst: D(192, 168, 1, 20)
        
    The header IS the geometry. The payload IS the mathematics.
    """
    source: DimensionalIP
    destination: DimensionalIP
    payload_type: int  # 0=raw, 1=function, 2=coordinate, 3=transform
    payload: bytes
    timestamp: float = field(default_factory=time.time)
    ttl: int = 64
    sequence: int = 0
    
    # Payload types
    TYPE_RAW = 0
    TYPE_FUNCTION = 1
    TYPE_COORDINATE = 2
    TYPE_TRANSFORM = 3
    
    @property
    def route_distance(self) -> float:
        """Distance this packet must travel in manifold space"""
        return self.source.distance_to(self.destination)
    
    @property
    def is_local(self) -> bool:
        """Is this packet within the same /24 region?"""
        return self.source.is_same_subnet(self.destination, 24)
    
    def serialize(self) -> bytes:
        """
        Serialize to wire format.
        
        Format:
            [version:1][src:4][dst:4][type:1][ttl:1][seq:4][timestamp:8][payload_len:4][payload:N][checksum:4]
        """
        header = struct.pack(
            '>B4s4sBBId',
            1,  # version
            self.source.to_bytes(),
            self.destination.to_bytes(),
            self.payload_type,
            self.ttl,
            self.sequence,
            self.timestamp
        )
        
        payload_part = struct.pack('>I', len(self.payload)) + self.payload
        
        # Checksum
        checksum = self._checksum(header + payload_part)
        
        return header + payload_part + struct.pack('>I', checksum)
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'DimensionalPacket':
        """Deserialize from wire format with validation"""
        if len(data) < 27:
            raise ValueError(f"DimensionalPacket requires at least 27 bytes, got {len(data)}")
        
        version, src_bytes, dst_bytes, ptype, ttl, seq, ts = struct.unpack('>B4s4sBBId', data[:23])
        
        if version != 1:
            raise ValueError(f"Unsupported packet version: {version}")
        
        payload_len = struct.unpack('>I', data[23:27])[0]
        
        # Validate payload length
        if payload_len > 10 * 1024 * 1024:  # 10MB max
            raise ValueError(f"Payload too large: {payload_len} bytes")
        
        if len(data) < 31 + payload_len:
            raise ValueError(f"Truncated packet: need {31 + payload_len} bytes, got {len(data)}")
        
        payload = data[27:27+payload_len]
        received_checksum = struct.unpack('>I', data[27+payload_len:31+payload_len])[0]
        
        # Verify checksum
        expected_checksum = cls._checksum(data[:27+payload_len])
        if received_checksum != expected_checksum:
            raise ValueError(f"Checksum mismatch: {received_checksum} != {expected_checksum}")
        
        return cls(
            source=DimensionalIP.from_bytes(src_bytes),
            destination=DimensionalIP.from_bytes(dst_bytes),
            payload_type=ptype,
            payload=payload,
            timestamp=ts,
            ttl=ttl,
            sequence=seq
        )
    
    @staticmethod
    def _checksum(data: bytes) -> int:
        """Simple checksum"""
        return sum(data) & 0xFFFFFFFF
    
    def __str__(self) -> str:
        return f"Packet({self.source} -> {self.destination}, {len(self.payload)} bytes)"


# =============================================================================
# DIMENSIONAL ROUTER
# =============================================================================

class DimensionalRouter:
    """
    Routes packets through dimensional space.
    
    Routing is geometric pathfinding. The shortest path in 4D space
    IS the optimal route. No routing tables needed — just geometry.
    """
    
    def __init__(self, local_ip: DimensionalIP):
        self.local_ip = local_ip
        self.routing_cache: Dict[str, List[DimensionalIP]] = {}
        self.metrics = {
            'packets_routed': 0,
            'bytes_routed': 0,
            'avg_route_distance': 0.0,
            'cache_hits': 0
        }
    
    @classmethod
    def from_ip_string(cls, ip: str) -> 'DimensionalRouter':
        """Create router from IP string"""
        return cls(DimensionalIP.from_ip(ip))
    
    def route(self, packet: DimensionalPacket) -> List[DimensionalIP]:
        """
        Calculate route from source to destination.
        
        In manifold space, the route is the geodesic (shortest path).
        For now, we use direct routing. Future: manifold curvature.
        """
        cache_key = f"{packet.source}->{packet.destination}"
        
        if cache_key in self.routing_cache:
            self.metrics['cache_hits'] += 1
            return self.routing_cache[cache_key]
        
        # Direct route through dimensional space
        route = [packet.source, packet.destination]
        
        # Update metrics
        self.metrics['packets_routed'] += 1
        self.metrics['bytes_routed'] += len(packet.payload)
        
        # Running average of route distance
        n = self.metrics['packets_routed']
        old_avg = self.metrics['avg_route_distance']
        self.metrics['avg_route_distance'] = old_avg + (packet.route_distance - old_avg) / n
        
        self.routing_cache[cache_key] = route
        return route
    
    def is_local(self, ip: DimensionalIP) -> bool:
        """Check if IP is in local subnet region"""
        return self.local_ip.is_same_subnet(ip, 24)
    
    def distance_to(self, ip: DimensionalIP) -> float:
        """Distance from local IP to target"""
        return self.local_ip.distance_to(ip)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get routing metrics"""
        return {
            **self.metrics,
            'local_ip': str(self.local_ip),
            'local_subnet': f"{self.local_ip.x}.{self.local_ip.y}.{self.local_ip.z}.0/24",
            'cache_size': len(self.routing_cache)
        }


# =============================================================================
# BENCHMARKING
# =============================================================================

@dataclass
class ManifoldBenchmark:
    """Benchmark results for manifold networking"""
    operation: str
    iterations: int
    total_time_ms: float
    avg_time_us: float
    min_time_us: float
    max_time_us: float
    throughput: float  # operations per second
    bytes_processed: int = 0
    bandwidth_mbps: float = 0.0


def benchmark_dimensional_encoding(iterations: int = 10000) -> ManifoldBenchmark:
    """Benchmark IP to dimensional coordinate encoding"""
    import random
    
    # Generate random IPs
    ips = [f"{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}" 
           for _ in range(iterations)]
    
    times = []
    start_total = time.perf_counter()
    
    for ip in ips:
        start = time.perf_counter()
        dim_ip = DimensionalIP.from_ip(ip)
        _ = dim_ip.as_vec4
        _ = dim_ip.substrate_position
        end = time.perf_counter()
        times.append((end - start) * 1_000_000)  # microseconds
    
    end_total = time.perf_counter()
    total_ms = (end_total - start_total) * 1000
    
    return ManifoldBenchmark(
        operation="IP → Dimensional Encoding",
        iterations=iterations,
        total_time_ms=total_ms,
        avg_time_us=sum(times) / len(times),
        min_time_us=min(times),
        max_time_us=max(times),
        throughput=iterations / (total_ms / 1000)
    )


def benchmark_packet_serialization(iterations: int = 10000) -> ManifoldBenchmark:
    """Benchmark packet serialization/deserialization"""
    # Create test packet
    src = DimensionalIP(192, 168, 1, 10)
    dst = DimensionalIP(192, 168, 1, 20)
    payload = b"Hello, Manifold!" * 10
    packet = DimensionalPacket(source=src, destination=dst, payload_type=1, payload=payload)
    
    times = []
    total_bytes = 0
    start_total = time.perf_counter()
    
    for _ in range(iterations):
        start = time.perf_counter()
        serialized = packet.serialize()
        deserialized = DimensionalPacket.deserialize(serialized)
        end = time.perf_counter()
        times.append((end - start) * 1_000_000)
        total_bytes += len(serialized)
    
    end_total = time.perf_counter()
    total_ms = (end_total - start_total) * 1000
    
    return ManifoldBenchmark(
        operation="Packet Serialization Roundtrip",
        iterations=iterations,
        total_time_ms=total_ms,
        avg_time_us=sum(times) / len(times),
        min_time_us=min(times),
        max_time_us=max(times),
        throughput=iterations / (total_ms / 1000),
        bytes_processed=total_bytes,
        bandwidth_mbps=(total_bytes * 8) / (total_ms / 1000) / 1_000_000
    )


def benchmark_routing(iterations: int = 10000) -> ManifoldBenchmark:
    """Benchmark dimensional routing"""
    import random
    
    router = DimensionalRouter.from_ip_string("192.168.1.1")
    
    # Generate random packets
    packets = []
    for _ in range(iterations):
        src = DimensionalIP(192, 168, random.randint(0,255), random.randint(0,255))
        dst = DimensionalIP(10, random.randint(0,255), random.randint(0,255), random.randint(0,255))
        packets.append(DimensionalPacket(source=src, destination=dst, payload_type=0, payload=b"test"))
    
    times = []
    start_total = time.perf_counter()
    
    for packet in packets:
        start = time.perf_counter()
        route = router.route(packet)
        end = time.perf_counter()
        times.append((end - start) * 1_000_000)
    
    end_total = time.perf_counter()
    total_ms = (end_total - start_total) * 1000
    
    return ManifoldBenchmark(
        operation="Dimensional Routing",
        iterations=iterations,
        total_time_ms=total_ms,
        avg_time_us=sum(times) / len(times),
        min_time_us=min(times),
        max_time_us=max(times),
        throughput=iterations / (total_ms / 1000)
    )


def run_all_benchmarks(iterations: int = 10000) -> Dict[str, ManifoldBenchmark]:
    """Run all benchmarks and return results"""
    return {
        'encoding': benchmark_dimensional_encoding(iterations),
        'serialization': benchmark_packet_serialization(iterations),
        'routing': benchmark_routing(iterations)
    }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def ip_to_dimensional(ip: str) -> Dict[str, Any]:
    """
    Convert IP address to full dimensional representation.
    Useful for API responses.
    """
    dim_ip = DimensionalIP.from_ip(ip)
    return {
        'ip': ip,
        'dimensional': {
            'x': dim_ip.x,
            'y': dim_ip.y,
            'z': dim_ip.z,
            'm': dim_ip.m
        },
        'substrate_r': dim_ip.substrate_position,
        'vec4_normalized': dim_ip.as_vec4,
        'manifold_uri': dim_ip.to_manifold_uri(),
        'tuple': dim_ip.as_tuple
    }


def dimensional_to_ip(x: int, y: int, z: int, m: int) -> str:
    """Convert dimensional coordinates back to IP"""
    dim_ip = DimensionalIP(x, y, z, m)
    return dim_ip.to_ip()


# =============================================================================
# TESTS
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ButterflyFX Dimensional IP Addressing")
    print("=" * 60)
    
    # Test basic encoding
    print("\n1. IP to Dimensional Encoding:")
    test_ips = ["192.168.1.1", "10.0.0.1", "172.16.0.100", "255.255.255.255"]
    for ip in test_ips:
        dim = DimensionalIP.from_ip(ip)
        print(f"   {ip} -> {dim} -> r={dim.substrate_position}")
    
    # Test subnet analysis
    print("\n2. Subnet Dimensional Analysis:")
    subnets = ["192.168.0.0/16", "10.0.0.0/8", "172.16.1.0/24", "192.168.1.100/32"]
    for cidr in subnets:
        subnet = DimensionalSubnet.from_cidr(cidr)
        print(f"   {subnet}")
    
    # Test distance calculation
    print("\n3. Dimensional Distance (Network Distance):")
    ip1 = DimensionalIP.from_ip("192.168.1.1")
    ip2 = DimensionalIP.from_ip("192.168.1.100")
    ip3 = DimensionalIP.from_ip("10.0.0.1")
    print(f"   {ip1} to {ip2}: {ip1.distance_to(ip2):.2f}")
    print(f"   {ip1} to {ip3}: {ip1.distance_to(ip3):.2f}")
    
    # Test packet serialization
    print("\n4. Dimensional Packet:")
    packet = DimensionalPacket(
        source=ip1,
        destination=ip2,
        payload_type=DimensionalPacket.TYPE_FUNCTION,
        payload=b'{"function": "sin", "params": {"freq": 440}}'
    )
    print(f"   {packet}")
    print(f"   Route distance: {packet.route_distance:.2f}")
    print(f"   Is local: {packet.is_local}")
    
    serialized = packet.serialize()
    print(f"   Serialized size: {len(serialized)} bytes")
    
    restored = DimensionalPacket.deserialize(serialized)
    print(f"   Deserialized: {restored}")
    
    # Run benchmarks
    print("\n5. Benchmarks (1000 iterations):")
    benchmarks = run_all_benchmarks(1000)
    for name, bench in benchmarks.items():
        print(f"\n   {bench.operation}:")
        print(f"      Throughput: {bench.throughput:,.0f} ops/sec")
        print(f"      Avg latency: {bench.avg_time_us:.2f} μs")
        print(f"      Min/Max: {bench.min_time_us:.2f} / {bench.max_time_us:.2f} μs")
        if bench.bandwidth_mbps > 0:
            print(f"      Bandwidth: {bench.bandwidth_mbps:.2f} Mbps")
    
    print("\n" + "=" * 60)
    print("THE MANIFOLD IS THE NETWORK. THE OSI MODEL IS THE GEOMETRY.")
    print("=" * 60)
