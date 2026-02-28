"""
Connection Substrate - Dimensional Socket Management

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)

Manages socket connections as points on a dimensional manifold.
O(1) connection lookup, lazy manifestation, geometric composition.
"""

from __future__ import annotations
import time
import hashlib
from dataclasses import dataclass, field
from typing import Dict, Set, Optional, Any, Tuple
from collections import OrderedDict
import socket as sock
import threading


# =============================================================================
# CONNECTION POINT - A socket as a dimensional coordinate
# =============================================================================

@dataclass
class ConnectionPoint:
    """
    A connection represented as a point on the manifold.
    
    Coordinates:
        spiral: Connection pool index
        layer: Connection state (1=new, 2=handshake, 3=active, 4=idle, 5=closing, 6=closed, 7=archived)
        position: Connection priority/weight
    """
    connection_id: str
    socket: sock.socket
    address: Tuple[str, int]
    spiral: int = 0  # Connection pool
    layer: int = 1   # State (1-7)
    position: float = 0.0  # Priority
    
    # Metadata
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)
    bytes_sent: int = 0
    bytes_received: int = 0
    request_count: int = 0
    
    # Identity vector for z = x·y composition
    identity_vector: Tuple[float, float] = field(default_factory=lambda: (1.0, 1.0))
    
    def __post_init__(self):
        # Calculate identity vector from address
        ip_hash = hashlib.md5(self.address[0].encode()).digest()
        x = int.from_bytes(ip_hash[:4], 'big') / (2**32)
        y = 1.0 / (x + 0.001)  # Reciprocal for neutral binding
        self.identity_vector = (x, y)
    
    @property
    def z_value(self) -> float:
        """Compute z = x·y for geometric composition"""
        return self.identity_vector[0] * self.identity_vector[1]
    
    @property
    def state_name(self) -> str:
        """Human-readable state name"""
        states = {
            1: "new",
            2: "handshake",
            3: "active",
            4: "idle",
            5: "closing",
            6: "closed",
            7: "archived"
        }
        return states.get(self.layer, "unknown")
    
    @property
    def age_seconds(self) -> float:
        """Connection age in seconds"""
        return time.time() - self.created_at
    
    @property
    def idle_seconds(self) -> float:
        """Seconds since last activity"""
        return time.time() - self.last_active
    
    def touch(self):
        """Update last active timestamp"""
        self.last_active = time.time()
    
    def transition_to(self, new_layer: int):
        """Transition to new state (layer)"""
        if 1 <= new_layer <= 7:
            self.layer = new_layer
            self.touch()


# =============================================================================
# DIMENSIONAL INDEX - O(1) connection lookup
# =============================================================================

class DimensionalConnectionIndex:
    """
    Index connections by (spiral, layer) for O(1) access.
    Like a database index, but for dimensional coordinates.
    """
    
    def __init__(self):
        self._index: Dict[Tuple[int, int], Set[str]] = {}  # (spiral, layer) -> Set[connection_id]
        self._reverse: Dict[str, Tuple[int, int]] = {}  # connection_id -> (spiral, layer)
        self._connections: Dict[str, ConnectionPoint] = {}  # connection_id -> ConnectionPoint
        self._lock = threading.RLock()
    
    def add(self, connection: ConnectionPoint):
        """Add connection to index - O(1)"""
        with self._lock:
            key = (connection.spiral, connection.layer)
            if key not in self._index:
                self._index[key] = set()
            
            self._index[key].add(connection.connection_id)
            self._reverse[connection.connection_id] = key
            self._connections[connection.connection_id] = connection
    
    def get_at(self, spiral: int, layer: int) -> Set[ConnectionPoint]:
        """Get all connections at (spiral, layer) - O(1)"""
        with self._lock:
            key = (spiral, layer)
            connection_ids = self._index.get(key, set())
            return {self._connections[cid] for cid in connection_ids if cid in self._connections}
    
    def get_by_id(self, connection_id: str) -> Optional[ConnectionPoint]:
        """Get connection by ID - O(1)"""
        with self._lock:
            return self._connections.get(connection_id)
    
    def move(self, connection_id: str, new_spiral: int, new_layer: int):
        """Move connection to new coordinates - O(1)"""
        with self._lock:
            if connection_id not in self._reverse:
                return
            
            # Remove from old position
            old_key = self._reverse[connection_id]
            if old_key in self._index:
                self._index[old_key].discard(connection_id)
                if not self._index[old_key]:
                    del self._index[old_key]
            
            # Add to new position
            new_key = (new_spiral, new_layer)
            if new_key not in self._index:
                self._index[new_key] = set()
            self._index[new_key].add(connection_id)
            self._reverse[connection_id] = new_key
            
            # Update connection object
            if connection_id in self._connections:
                self._connections[connection_id].spiral = new_spiral
                self._connections[connection_id].layer = new_layer
    
    def remove(self, connection_id: str):
        """Remove connection from index - O(1)"""
        with self._lock:
            if connection_id not in self._reverse:
                return
            
            # Remove from index
            key = self._reverse[connection_id]
            if key in self._index:
                self._index[key].discard(connection_id)
                if not self._index[key]:
                    del self._index[key]
            
            # Remove from reverse index and connections
            del self._reverse[connection_id]
            if connection_id in self._connections:
                del self._connections[connection_id]
    
    def count_at(self, spiral: int, layer: int) -> int:
        """Count connections at coordinates - O(1)"""
        with self._lock:
            key = (spiral, layer)
            return len(self._index.get(key, set()))
    
    def total_connections(self) -> int:
        """Total number of connections - O(1)"""
        with self._lock:
            return len(self._connections)
    
    def get_all_active(self) -> Set[ConnectionPoint]:
        """Get all active connections (layer 3) - O(1)"""
        return self.get_at(0, 3)
    
    def get_all_idle(self) -> Set[ConnectionPoint]:
        """Get all idle connections (layer 4) - O(1)"""
        return self.get_at(0, 4)


# =============================================================================
# CONNECTION SUBSTRATE - Lazy manifestation
# =============================================================================

class ConnectionSubstrate:
    """
    Manages connections as a dimensional substrate.
    
    Features:
        - O(1) connection lookup by coordinates
        - Lazy manifestation (create only when needed)
        - Geometric composition (z = x·y)
        - Automatic state transitions
        - Connection pooling by spiral
    """
    
    def __init__(self, max_connections_per_pool: int = 1000):
        self.index = DimensionalConnectionIndex()
        self.max_connections_per_pool = max_connections_per_pool
        self._lock = threading.RLock()
        
        # Statistics
        self.total_created = 0
        self.total_closed = 0
        self.total_bytes_sent = 0
        self.total_bytes_received = 0
    
    def manifest(self, socket: sock.socket, address: Tuple[str, int]) -> ConnectionPoint:
        """
        Manifest a new connection (lazy creation).
        
        Returns ConnectionPoint at (spiral=0, layer=1) - new connection
        """
        with self._lock:
            # Generate connection ID
            connection_id = hashlib.md5(
                f"{address[0]}:{address[1]}:{time.time()}".encode()
            ).hexdigest()[:16]
            
            # Create connection point
            connection = ConnectionPoint(
                connection_id=connection_id,
                socket=socket,
                address=address,
                spiral=0,  # Default pool
                layer=1,   # New connection
                position=0.0
            )
            
            # Add to index
            self.index.add(connection)
            self.total_created += 1
            
            return connection
    
    def transition(self, connection_id: str, new_layer: int):
        """
        Transition connection to new state.
        
        Layer meanings:
            1: new (just created)
            2: handshake (WebSocket upgrade, etc.)
            3: active (processing requests)
            4: idle (keep-alive)
            5: closing (graceful shutdown)
            6: closed (socket closed)
            7: archived (logged, can be removed)
        """
        with self._lock:
            connection = self.index.get_by_id(connection_id)
            if connection:
                old_layer = connection.layer
                self.index.move(connection_id, connection.spiral, new_layer)
                connection.transition_to(new_layer)
                
                # Auto-cleanup archived connections
                if new_layer == 7:
                    self._archive_connection(connection)
    
    def _archive_connection(self, connection: ConnectionPoint):
        """Archive and remove connection"""
        with self._lock:
            # Update statistics
            self.total_bytes_sent += connection.bytes_sent
            self.total_bytes_received += connection.bytes_received
            self.total_closed += 1
            
            # Remove from index
            self.index.remove(connection.connection_id)
    
    def get_connection(self, connection_id: str) -> Optional[ConnectionPoint]:
        """Get connection by ID - O(1)"""
        return self.index.get_by_id(connection_id)
    
    def get_active_connections(self) -> Set[ConnectionPoint]:
        """Get all active connections - O(1)"""
        return self.index.get_all_active()
    
    def get_idle_connections(self) -> Set[ConnectionPoint]:
        """Get all idle connections - O(1)"""
        return self.index.get_all_idle()
    
    def cleanup_idle(self, max_idle_seconds: float = 300):
        """
        Clean up idle connections older than threshold.
        Transitions idle → closing → closed → archived
        """
        with self._lock:
            idle_connections = self.get_idle_connections()
            for connection in idle_connections:
                if connection.idle_seconds > max_idle_seconds:
                    # Transition through states
                    self.transition(connection.connection_id, 5)  # closing
                    try:
                        connection.socket.close()
                    except:
                        pass
                    self.transition(connection.connection_id, 6)  # closed
                    self.transition(connection.connection_id, 7)  # archived
    
    def compose(self, conn1_id: str, conn2_id: str) -> Optional[float]:
        """
        Geometric composition: z = x·y
        
        Composes two connections to compute relationship strength.
        Useful for load balancing, affinity routing, etc.
        """
        conn1 = self.get_connection(conn1_id)
        conn2 = self.get_connection(conn2_id)
        
        if not conn1 or not conn2:
            return None
        
        # z = x1·y1 * x2·y2 (multiplicative composition)
        z1 = conn1.z_value
        z2 = conn2.z_value
        return z1 * z2
    
    def get_stats(self) -> Dict[str, Any]:
        """Get substrate statistics"""
        with self._lock:
            return {
                "total_connections": self.index.total_connections(),
                "active_connections": len(self.get_active_connections()),
                "idle_connections": len(self.get_idle_connections()),
                "total_created": self.total_created,
                "total_closed": self.total_closed,
                "total_bytes_sent": self.total_bytes_sent,
                "total_bytes_received": self.total_bytes_received,
                "connections_by_layer": {
                    layer: self.index.count_at(0, layer)
                    for layer in range(1, 8)
                }
            }


# =============================================================================
# CONNECTION POOL MANIFOLD - Multiple pools as spirals
# =============================================================================

class ConnectionPoolManifold:
    """
    Manages multiple connection pools as spirals.
    
    Each spiral is a separate connection pool:
        spiral 0: HTTP connections
        spiral 1: WebSocket connections
        spiral 2: API connections
        spiral 3: Admin connections
        etc.
    """
    
    def __init__(self):
        self.substrates: Dict[int, ConnectionSubstrate] = {}
        self._lock = threading.RLock()
    
    def get_substrate(self, spiral: int) -> ConnectionSubstrate:
        """Get or create substrate for spiral - lazy manifestation"""
        with self._lock:
            if spiral not in self.substrates:
                self.substrates[spiral] = ConnectionSubstrate()
            return self.substrates[spiral]
    
    def manifest_connection(
        self,
        socket: sock.socket,
        address: Tuple[str, int],
        pool_type: str = "http"
    ) -> ConnectionPoint:
        """
        Manifest connection in appropriate pool.
        
        Pool types map to spirals:
            http -> spiral 0
            websocket -> spiral 1
            api -> spiral 2
            admin -> spiral 3
        """
        pool_map = {
            "http": 0,
            "websocket": 1,
            "api": 2,
            "admin": 3
        }
        spiral = pool_map.get(pool_type, 0)
        
        substrate = self.get_substrate(spiral)
        connection = substrate.manifest(socket, address)
        connection.spiral = spiral  # Set correct spiral
        
        return connection
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all pools"""
        with self._lock:
            return {
                f"spiral_{spiral}": substrate.get_stats()
                for spiral, substrate in self.substrates.items()
            }


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Create connection pool manifold
    manifold = ConnectionPoolManifold()
    
    # Simulate connections
    import socket
    
    # HTTP connection
    http_sock = socket.socket()
    http_conn = manifold.manifest_connection(http_sock, ("192.168.1.100", 8080), "http")
    print(f"HTTP connection: {http_conn.connection_id} at ({http_conn.spiral}, {http_conn.layer})")
    
    # WebSocket connection
    ws_sock = socket.socket()
    ws_conn = manifold.manifest_connection(ws_sock, ("192.168.1.101", 8080), "websocket")
    print(f"WebSocket connection: {ws_conn.connection_id} at ({ws_conn.spiral}, {ws_conn.layer})")
    
    # Transition HTTP to active
    http_substrate = manifold.get_substrate(0)
    http_substrate.transition(http_conn.connection_id, 3)  # active
    print(f"HTTP transitioned to: {http_conn.state_name}")
    
    # Get statistics
    stats = manifold.get_all_stats()
    print(f"\nStatistics: {stats}")
    
    # Geometric composition
    z = http_substrate.compose(http_conn.connection_id, http_conn.connection_id)
    print(f"\nComposition z = x·y: {z}")
