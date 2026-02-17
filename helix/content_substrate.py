"""
ButterflyFX Content Substrate - Application to Transport Layer

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

Part of ButterflyFX - Open source infrastructure.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

THE CONTENT SUBSTRATE: Where Application Meets Transport

This module unifies:
    - APPLICATION layer (user requests)
    - SUBSTRATE (content storage/generation)
    - MANIFOLD (dimensional addressing)
    - TRANSPORT layer (reliable delivery)

The substrate IS the content. The manifold IS the network.
Content is organized dimensionally and served through the OSI-Helix stack.

Content Flow:
    USER REQUEST → APPLICATION (6D META) → SUBSTRATE → MANIFOLD ADDRESS → TRANSPORT (3D VOLUME) → DELIVERY

Dimensional Content Organization:
    Level 0 (POINT):   Single values, atomic facts
    Level 1 (LINE):    Sequences, lists, arrays
    Level 2 (PLANE):   Tables, grids, 2D structures
    Level 3 (VOLUME):  Records, documents, 3D objects
    Level 4 (TIME):    Animations, timelines, histories
    Level 5 (NETWORK): Connected systems, APIs
    Level 6 (META):    Abstractions, indexes, overviews
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from enum import Enum, IntEnum
import json
import time
import zlib
from functools import cached_property

from .osi_manifold import (
    OSIHelixLayer, ManifoldAddress, ManifoldDatagram, 
    OSIManifoldStack, HTTPManifoldBridge, LAYER_INFO
)
from .substrate import ManifoldSubstrate, Token, PayloadSource, GeometricProperty


# =============================================================================
# CONTENT TYPES - Different dimensional content structures
# =============================================================================

class ContentDimension(IntEnum):
    """Content organized by dimensional complexity"""
    POINT = 0      # Atomic value (number, bool, key)
    LINE = 1       # Sequence (list, array, row)
    PLANE = 2      # Grid (table, matrix, 2D array)
    VOLUME = 3     # Document (record, object, 3D)
    TIME = 4       # Timeline (animation, history, changes)
    NETWORK = 5    # Connected (API, graph, links)
    META = 6       # Abstract (index, summary, overview)


# =============================================================================
# CONTENT ITEM - A piece of dimensional content
# =============================================================================

@dataclass
class ContentItem:
    """
    A unit of dimensional content.
    
    Content is dimensional - it has structure that maps to helix levels.
    """
    id: str
    dimension: ContentDimension
    title: str
    data: Any
    mime_type: str = "application/json"
    created: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Lazy loading
    _loaded: bool = field(default=False, repr=False)
    _loader: Optional[Callable] = field(default=None, repr=False)
    
    def to_bytes(self) -> bytes:
        """Serialize content for transport"""
        envelope = {
            "id": self.id,
            "dimension": self.dimension.value,
            "title": self.title,
            "mime_type": self.mime_type,
            "created": self.created,
            "metadata": self.metadata,
            "data": self.data
        }
        return json.dumps(envelope).encode('utf-8')
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'ContentItem':
        """Deserialize from transport"""
        envelope = json.loads(data.decode('utf-8'))
        return cls(
            id=envelope["id"],
            dimension=ContentDimension(envelope["dimension"]),
            title=envelope["title"],
            data=envelope["data"],
            mime_type=envelope.get("mime_type", "application/json"),
            created=envelope.get("created", time.time()),
            metadata=envelope.get("metadata", {})
        )
    
    @property
    def size(self) -> int:
        """Approximate byte size of content"""
        return len(self.to_bytes())


# =============================================================================
# CONTENT SUBSTRATE - Content organized on the manifold
# =============================================================================

class ContentSubstrate:
    """
    The Content Substrate - Application layer content organized dimensionally.
    
    This bridges:
        - APPLICATION: User-facing content items
        - SUBSTRATE: Lazy evaluation, geometric derivation
        - MANIFOLD: Dimensional addressing
        - TRANSPORT: Reliable delivery via OSI stack
    
    Usage:
        substrate = ContentSubstrate()
        
        # Store content at dimensional address
        substrate.store(0, 3, "doc1", ContentItem(
            id="doc1", 
            dimension=ContentDimension.VOLUME,
            title="User Profile",
            data={"name": "Alice", "level": 42}
        ))
        
        # Retrieve and serve
        content = substrate.retrieve(0, 3, "doc1")
        datagram = substrate.serve(ManifoldAddress(0, 3, 0), "doc1")
    """
    
    def __init__(self):
        # Content storage: (spiral, level, key) -> ContentItem
        self._content: Dict[Tuple[int, int, str], ContentItem] = {}
        
        # Index by dimension
        self._by_dimension: Dict[ContentDimension, List[str]] = {
            dim: [] for dim in ContentDimension
        }
        
        # OSI-Manifold stack for transport
        self._stack: Optional[OSIManifoldStack] = None
        
        # Statistics
        self._store_count = 0
        self._retrieve_count = 0
        self._serve_count = 0
        
        # Underlying math substrate for geometric values
        self._math_substrate = ManifoldSubstrate()
    
    # =========================================================================
    # APPLICATION LAYER - Store and organize content
    # =========================================================================
    
    def store(self, spiral: int, level: int, key: str, content: ContentItem) -> Tuple[int, int, str]:
        """
        Store content at a manifold coordinate.
        
        Content dimension should match level:
            Level 0 → POINT (atomic values)
            Level 1 → LINE (sequences)
            Level 2 → PLANE (tables)
            Level 3 → VOLUME (documents)
            Level 4 → TIME (animations)
            Level 5 → NETWORK (connections)
            Level 6 → META (abstractions)
        
        Args:
            spiral: Which spiral (namespace/channel)
            level: Which dimensional level (0-6)
            key: Content identifier
            content: The content item
        
        Returns:
            The coordinate tuple (spiral, level, key)
        """
        coord = (spiral, level, key)
        self._content[coord] = content
        self._by_dimension[content.dimension].append(f"{spiral}:{level}:{key}")
        self._store_count += 1
        return coord
    
    def retrieve(self, spiral: int, level: int, key: str) -> Optional[ContentItem]:
        """
        Retrieve content from a coordinate.
        
        O(1) lookup by coordinate.
        """
        coord = (spiral, level, key)
        self._retrieve_count += 1
        return self._content.get(coord)
    
    def list_at_level(self, level: int) -> List[ContentItem]:
        """List all content at a dimensional level"""
        return [
            content for coord, content in self._content.items()
            if coord[1] == level
        ]
    
    def list_in_spiral(self, spiral: int) -> List[ContentItem]:
        """List all content in a spiral (namespace)"""
        return [
            content for coord, content in self._content.items()
            if coord[0] == spiral
        ]
    
    def search(self, query: str) -> List[ContentItem]:
        """Search content by title (simple substring match)"""
        query_lower = query.lower()
        return [
            content for content in self._content.values()
            if query_lower in content.title.lower()
        ]
    
    # =========================================================================
    # TRANSPORT LAYER - Serve content via OSI-Manifold stack
    # =========================================================================
    
    def init_transport(self, local_spiral: int = 0):
        """Initialize the transport layer"""
        local_addr = ManifoldAddress(local_spiral, OSIHelixLayer.APPLICATION, 0)
        self._stack = OSIManifoldStack(local_addr)
        
        # Register content handler at application layer
        def content_handler(datagram: ManifoldDatagram, layer: OSIHelixLayer):
            """Handle incoming content requests"""
            if datagram.payload_type == ManifoldDatagram.TYPE_QUERY:
                # Parse query
                query = json.loads(datagram.payload.decode('utf-8'))
                key = query.get('key', '')
                
                # Look up content
                coord = (
                    datagram.destination.spiral,
                    datagram.destination.level,
                    key
                )
                content = self._content.get(coord)
                
                if content:
                    # Return content
                    return content.to_bytes()
                else:
                    return json.dumps({"error": "not_found"}).encode('utf-8')
            return True
        
        self._stack.router.register_layer_handler(
            OSIHelixLayer.APPLICATION, content_handler
        )
    
    def serve(self, destination: ManifoldAddress, key: str, 
              flags: int = 0) -> Optional[ManifoldDatagram]:
        """
        Serve content to a destination address.
        
        This is the FULL APPLICATION → TRANSPORT flow:
        1. APPLICATION: Look up content in substrate
        2. PRESENTATION: Serialize to bytes
        3. SESSION: Track request (optional)
        4. TRANSPORT: Create reliable datagram
        5. NETWORK: Address via manifold coordinate
        6. DATA_LINK: Frame the data
        7. PHYSICAL: Ready for transmission
        
        Args:
            destination: Where to send content
            key: Content key to serve
            flags: Datagram flags (compression, etc)
        
        Returns:
            ManifoldDatagram ready for transmission
        """
        if not self._stack:
            self.init_transport()
        
        # Retrieve from substrate
        content = self.retrieve(destination.spiral, destination.level, key)
        self._serve_count += 1
        
        if not content:
            return None
        
        # Serialize content (PRESENTATION layer)
        payload = content.to_bytes()
        
        # Optional compression
        if len(payload) > 1024:
            compressed = zlib.compress(payload)
            if len(compressed) < len(payload):
                payload = compressed
                flags |= ManifoldDatagram.FLAG_COMPRESSED
        
        # Create datagram through stack (TRANSPORT layer)
        return self._stack.send(
            destination=destination,
            payload_type=ManifoldDatagram.TYPE_CONTENT,
            payload=payload,
            flags=flags
        )
    
    def receive(self, datagram: ManifoldDatagram) -> Optional[ContentItem]:
        """
        Receive and process a content datagram.
        
        TRANSPORT → APPLICATION flow:
        1. PHYSICAL: Receive bits
        2. DATA_LINK: Verify frame
        3. NETWORK: Check routing
        4. TRANSPORT: Handle reliability
        5. SESSION: Update state
        6. PRESENTATION: Decompress/decode
        7. APPLICATION: Return content item
        """
        if not self._stack:
            self.init_transport()
        
        # Process through stack
        result = self._stack.receive(datagram)
        
        if result is None:
            return None
        
        # Handle compressed content
        payload = datagram.payload
        if datagram.flags & ManifoldDatagram.FLAG_COMPRESSED:
            payload = zlib.decompress(payload)
        
        # Parse content item
        return ContentItem.from_bytes(payload)
    
    # =========================================================================
    # HTTP BRIDGE - Serve content via traditional HTTP
    # =========================================================================
    
    def handle_http_request(self, path: str, query: Dict[str, str] = None) -> Tuple[bytes, str, int]:
        """
        Handle an HTTP request and return content.
        
        Maps URL to manifold address, retrieves from substrate, serves.
        
        Args:
            path: URL path (e.g., /level/3/key/doc1)
            query: Query parameters
        
        Returns:
            (content_bytes, mime_type, status_code)
        """
        query = query or {}
        
        # Parse address from URL
        addr = HTTPManifoldBridge.url_to_address(path, query)
        key = query.get('key', query.get('k', 'index'))
        
        # Retrieve content
        content = self.retrieve(addr.spiral, addr.level, key)
        
        if content:
            return content.to_bytes(), content.mime_type, 200
        else:
            # Check for index at this level
            index_content = self.retrieve(addr.spiral, addr.level, 'index')
            if index_content:
                return index_content.to_bytes(), index_content.mime_type, 200
            
            error = json.dumps({
                "error": "not_found",
                "address": addr.to_uri(),
                "key": key
            }).encode('utf-8')
            return error, "application/json", 404
    
    # =========================================================================
    # DIMENSIONAL CONTENT HELPERS
    # =========================================================================
    
    def store_point(self, spiral: int, key: str, value: Any, title: str = "") -> ContentItem:
        """Store a 0D point value"""
        content = ContentItem(
            id=f"{spiral}:0:{key}",
            dimension=ContentDimension.POINT,
            title=title or str(key),
            data=value
        )
        self.store(spiral, 0, key, content)
        return content
    
    def store_line(self, spiral: int, key: str, sequence: List[Any], title: str = "") -> ContentItem:
        """Store a 1D sequence"""
        content = ContentItem(
            id=f"{spiral}:1:{key}",
            dimension=ContentDimension.LINE,
            title=title or str(key),
            data=sequence
        )
        self.store(spiral, 1, key, content)
        return content
    
    def store_plane(self, spiral: int, key: str, grid: List[List[Any]], title: str = "") -> ContentItem:
        """Store a 2D grid/table"""
        content = ContentItem(
            id=f"{spiral}:2:{key}",
            dimension=ContentDimension.PLANE,
            title=title or str(key),
            data=grid
        )
        self.store(spiral, 2, key, content)
        return content
    
    def store_volume(self, spiral: int, key: str, document: Dict[str, Any], title: str = "") -> ContentItem:
        """Store a 3D document/record"""
        content = ContentItem(
            id=f"{spiral}:3:{key}",
            dimension=ContentDimension.VOLUME,
            title=title or str(key),
            data=document
        )
        self.store(spiral, 3, key, content)
        return content
    
    def store_timeline(self, spiral: int, key: str, events: List[Dict[str, Any]], title: str = "") -> ContentItem:
        """Store a 4D timeline"""
        content = ContentItem(
            id=f"{spiral}:4:{key}",
            dimension=ContentDimension.TIME,
            title=title or str(key),
            data=events
        )
        self.store(spiral, 4, key, content)
        return content
    
    def store_network(self, spiral: int, key: str, graph: Dict[str, Any], title: str = "") -> ContentItem:
        """Store a 5D network/graph"""
        content = ContentItem(
            id=f"{spiral}:5:{key}",
            dimension=ContentDimension.NETWORK,
            title=title or str(key),
            data=graph
        )
        self.store(spiral, 5, key, content)
        return content
    
    def store_meta(self, spiral: int, key: str, overview: Dict[str, Any], title: str = "") -> ContentItem:
        """Store a 6D meta/overview"""
        content = ContentItem(
            id=f"{spiral}:6:{key}",
            dimension=ContentDimension.META,
            title=title or str(key),
            data=overview
        )
        self.store(spiral, 6, key, content)
        return content
    
    # =========================================================================
    # STATS & DEBUG
    # =========================================================================
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get substrate statistics"""
        return {
            "total_content": len(self._content),
            "by_dimension": {
                dim.name: len(keys) 
                for dim, keys in self._by_dimension.items()
            },
            "stores": self._store_count,
            "retrievals": self._retrieve_count,
            "serves": self._serve_count,
            "stack_stats": self._stack.layer_stats if self._stack else None
        }
    
    def __repr__(self) -> str:
        return f"ContentSubstrate(items={len(self._content)})"


# =============================================================================
# EXAMPLE: Build the dimensional website content
# =============================================================================

def create_butterflyfx_content() -> ContentSubstrate:
    """
    Create the ButterflyFX website as dimensional content.
    
    Each level holds different depth of information.
    Navigating levels = navigating from simple to complex.
    """
    substrate = ContentSubstrate()
    
    # Level 0 - POINT: Core insight
    substrate.store_point(0, "core", 
        "Any computer can decipher math",
        title="The Core Insight"
    )
    
    # Level 1 - LINE: Key concepts
    substrate.store_line(0, "concepts", [
        "Send equations, not data",
        "Math is universal language",
        "Receivers evaluate locally",
        "Bandwidth → zero (math only)",
        "Any computer can decode"
    ], title="Key Concepts")
    
    # Level 2 - PLANE: The 7 levels
    substrate.store_plane(0, "levels", [
        ["Level", "Name",     "Dimension", "Purpose"],
        [0,       "POINT",    "0D",        "Core value"],
        [1,       "LINE",     "1D",        "Sequence"],
        [2,       "PLANE",    "2D",        "Grid/Table"],
        [3,       "VOLUME",   "3D",        "Document"],
        [4,       "TIME",     "4D",        "Animation"],
        [5,       "NETWORK",  "5D",        "Connections"],
        [6,       "META",     "6D",        "Abstraction"],
    ], title="The 7 Helix Levels")
    
    # Level 3 - VOLUME: Architecture document
    substrate.store_volume(0, "architecture", {
        "name": "ButterflyFX",
        "tagline": "Because any computer can decipher math",
        "layers": {
            "application": ["Presentations", "3D Engine", "Explorer"],
            "server": ["DimensionalServer", "ManifoldProtocol"],
            "transport": ["OSI-Manifold", "HelixPacket"],
            "foundation": ["HelixKernel", "ManifoldSubstrate"]
        },
        "author": "Kenneth Bingham",
        "license": "CC BY 4.0"
    }, title="Architecture Overview")
    
    # Level 4 - TIME: Development timeline
    substrate.store_timeline(0, "history", [
        {"time": "2024-01", "event": "Initial concept: math as payload"},
        {"time": "2024-06", "event": "HelixKernel mathematical core"},
        {"time": "2024-09", "event": "GenerativeManifold: derive, don't store"},
        {"time": "2025-01", "event": "OSI-Manifold: network IS manifold"},
        {"time": "2025-06", "event": "ContentSubstrate: app↔transport bridge"},
        {"time": "2026-02", "event": "Production deployment ready"}
    ], title="Development Timeline")
    
    # Level 5 - NETWORK: Connected resources
    substrate.store_network(0, "resources", {
        "nodes": [
            {"id": "github", "url": "https://github.com/kenbin64/butterflyfxpython"},
            {"id": "docs", "url": "https://butterflyfx.us/docs"},
            {"id": "api", "url": "https://api.butterflyfx.us"},
            {"id": "demo", "url": "https://butterflyfx.us/demo"}
        ],
        "edges": [
            {"from": "github", "to": "docs", "type": "generates"},
            {"from": "api", "to": "demo", "type": "powers"},
            {"from": "docs", "to": "demo", "type": "explains"}
        ]
    }, title="Connected Resources")
    
    # Level 6 - META: Complete overview
    substrate.store_meta(0, "index", {
        "title": "ButterflyFX",
        "subtitle": "The Mathematical Operating System",
        "navigation": {
            "0": "Core Insight",
            "1": "Key Concepts",
            "2": "The 7 Levels",
            "3": "Architecture",
            "4": "History",
            "5": "Resources",
            "6": "Overview (you are here)"
        },
        "quick_start": "from helix import ContentSubstrate",
        "insight": "The substrate delivers content. The manifold addresses it. One unified system from app to transport."
    }, title="ButterflyFX Overview")
    
    return substrate


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("Content Substrate Demo")
    print("=" * 60)
    print()
    
    # Create substrate with content
    substrate = create_butterflyfx_content()
    
    print("Dimensional Content Structure:")
    print("-" * 60)
    
    for level in range(7):
        items = substrate.list_at_level(level)
        dim_name = ContentDimension(level).name
        print(f"\nLevel {level} ({dim_name}):")
        for item in items:
            print(f"  • {item.title}")
            if level == 0:  # Show point value
                print(f"    = {item.data}")
            elif level == 1:  # Show first few items
                print(f"    = {item.data[:3]}...")
    
    print()
    print("=" * 60)
    print("Transport Demo:")
    print("-" * 60)
    
    # Initialize transport
    substrate.init_transport()
    
    # Serve content via transport layer
    dest = ManifoldAddress(spiral=0, level=3, position=0)
    datagram = substrate.serve(dest, "architecture")
    
    if datagram:
        print(f"\nServed datagram:")
        print(f"  Source: {datagram.source}")
        print(f"  Destination: {datagram.destination}")
        print(f"  Payload type: {hex(datagram.payload_type)}")
        print(f"  Payload size: {len(datagram.payload)} bytes")
        print(f"  Flags: {bin(datagram.flags)}")
    
    print()
    print("=" * 60)
    print("HTTP Bridge Demo:")
    print("-" * 60)
    
    # Simulate HTTP requests
    requests = [
        ("/level/0", {"key": "core"}),
        ("/level/3", {"key": "architecture"}),
        ("/level/6", {"key": "index"}),
    ]
    
    for path, query in requests:
        data, mime, status = substrate.handle_http_request(path, query)
        content = json.loads(data.decode('utf-8'))
        print(f"\n{path}?key={query['key']}")
        print(f"  Status: {status}")
        print(f"  Title: {content.get('title', 'N/A')}")
    
    print()
    print("=" * 60)
    print("Substrate Statistics:")
    print("-" * 60)
    print(json.dumps(substrate.stats, indent=2))
