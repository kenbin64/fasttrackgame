"""
Universal Hard Drive - Dimensional Storage Interface

A web-based dimensional file system that organizes any data
by dimensional levels with visual navigation.

Key Features:
    - Web UI for dimensional navigation
    - Integrates HelixDatabase + UniversalConnector
    - Visual representation of 7 dimensional levels
    - Store/retrieve any data dimensionally
    - FastAPI backend with HTMX frontend

Dimensional Structure:
    Level 6 (Whole):    The entire hard drive
    Level 5 (Volume):   Collections/Categories
    Level 4 (Plane):    Individual items
    Level 3 (Width):    Item properties
    Level 2 (Length):   Property values
    Level 1 (Point):    Atomic values
    Level 0 (Potential): Uncommitted data

Usage:
    from apps.universal_harddrive import UniversalHardDrive, run_server
    
    # Create hard drive
    uhd = UniversalHardDrive()
    
    # Store data dimensionally
    uhd.store("documents", "report.txt", "Hello World", level=4)
    
    # Retrieve by level
    all_collections = uhd.invoke(5)  # Get collections
    
    # Start web server
    run_server(port=8000)
"""

import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import sys

# Add parent to path for helix imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from helix import (
    HelixKernel, ManifoldSubstrate, Token,
    HelixCache, HelixLogger, HelixSerializer,
    LEVEL_NAMES, LEVEL_ICONS
)

# Import sibling apps
from .helix_database import HelixDatabase
from .universal_connector import UniversalConnector


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class DimensionalItem:
    """An item stored in the hard drive"""
    id: str
    name: str
    collection: str
    level: int
    data: Any
    mime_type: str = "application/json"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Collection:
    """A collection of dimensional items"""
    name: str
    icon: str = "📁"
    description: str = ""
    item_count: int = 0
    level: int = 5


# =============================================================================
# UNIVERSAL HARD DRIVE
# =============================================================================

class UniversalHardDrive:
    """
    Universal Hard Drive - Store Anything Dimensionally
    
    A unified storage interface that combines:
    - Local file storage
    - HelixDatabase for structured data
    - UniversalConnector for live API data
    
    Everything organized by dimensional levels.
    """
    
    def __init__(self, data_dir: str = "data/uhd"):
        # Initialize helix components
        self.kernel = HelixKernel()
        self.substrate = ManifoldSubstrate()
        self.kernel.set_substrate(self.substrate)
        
        self.cache = HelixCache()
        self.logger = HelixLogger(min_level=3)
        self.serializer = HelixSerializer()
        
        # Data directory
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Collections (Level 5)
        self._collections: Dict[str, Collection] = {}
        
        # Items by collection (Level 4)
        self._items: Dict[str, Dict[str, DimensionalItem]] = {}
        
        # Items by level
        self._by_level: Dict[int, Set[str]] = {i: set() for i in range(7)}
        
        # Integrated apps
        self._database: Optional[HelixDatabase] = None
        self._connector: Optional[UniversalConnector] = None
        
        # Stats
        self._stats = {
            'collections': 0,
            'items': 0,
            'reads': 0,
            'writes': 0,
            'invocations': 0
        }
        
        # Load existing data
        self._load()
        
        self.logger.whole("Universal Hard Drive initialized")
    
    # -------------------------------------------------------------------------
    # Persistence
    # -------------------------------------------------------------------------
    
    def _index_path(self) -> Path:
        return self.data_dir / "uhd_index.json"
    
    def _load(self):
        """Load index from disk"""
        index_path = self._index_path()
        if index_path.exists():
            try:
                with open(index_path, 'r') as f:
                    data = json.load(f)
                
                # Load collections
                for coll_data in data.get('collections', []):
                    coll = Collection(**coll_data)
                    self._collections[coll.name] = coll
                    self._items[coll.name] = {}
                
                # Load items
                for item_data in data.get('items', []):
                    item = DimensionalItem(**item_data)
                    if item.collection in self._items:
                        self._items[item.collection][item.id] = item
                        self._by_level[item.level].add(item.id)
                
                self._update_stats()
                self.logger.width(f"Loaded {self._stats['items']} items")
                
            except Exception as e:
                self.logger.plane(f"Error loading index: {e}")
    
    def _save(self):
        """Save index to disk"""
        data = {
            'collections': [
                {
                    'name': c.name,
                    'icon': c.icon,
                    'description': c.description,
                    'item_count': c.item_count,
                    'level': c.level
                }
                for c in self._collections.values()
            ],
            'items': [
                {
                    'id': item.id,
                    'name': item.name,
                    'collection': item.collection,
                    'level': item.level,
                    'data': item.data,
                    'mime_type': item.mime_type,
                    'created_at': item.created_at,
                    'updated_at': item.updated_at,
                    'tags': item.tags,
                    'metadata': item.metadata
                }
                for items in self._items.values()
                for item in items.values()
            ]
        }
        
        with open(self._index_path(), 'w') as f:
            json.dump(data, f, indent=2)
    
    def _update_stats(self):
        """Update statistics"""
        self._stats['collections'] = len(self._collections)
        self._stats['items'] = sum(len(items) for items in self._items.values())
    
    # -------------------------------------------------------------------------
    # Collection Operations
    # -------------------------------------------------------------------------
    
    def create_collection(self, name: str, icon: str = "📁", description: str = "") -> Collection:
        """Create a new collection (Level 5)"""
        if name in self._collections:
            return self._collections[name]
        
        coll = Collection(
            name=name,
            icon=icon,
            description=description
        )
        self._collections[name] = coll
        self._items[name] = {}
        
        self._stats['writes'] += 1
        self._update_stats()
        self._save()
        
        return coll
    
    def get_collection(self, name: str) -> Optional[Collection]:
        """Get a collection by name"""
        self._stats['reads'] += 1
        return self._collections.get(name)
    
    def list_collections(self) -> List[Collection]:
        """List all collections"""
        self._stats['reads'] += 1
        return list(self._collections.values())
    
    def delete_collection(self, name: str) -> bool:
        """Delete a collection and all its items"""
        if name not in self._collections:
            return False
        
        # Remove items from level index
        for item in self._items[name].values():
            self._by_level[item.level].discard(item.id)
        
        del self._collections[name]
        del self._items[name]
        
        self._stats['writes'] += 1
        self._update_stats()
        self._save()
        
        return True
    
    # -------------------------------------------------------------------------
    # Item Operations
    # -------------------------------------------------------------------------
    
    def _generate_id(self) -> str:
        """Generate unique item ID"""
        import random
        return f"item_{random.randint(10000, 99999)}_{datetime.now().strftime('%H%M%S')}"
    
    def store(
        self,
        collection: str,
        name: str,
        data: Any,
        level: int = 4,
        mime_type: str = "application/json",
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> DimensionalItem:
        """
        Store data dimensionally.
        
        Args:
            collection: Collection name (Level 5)
            name: Item name
            data: The data to store
            level: Dimensional level (default 4 - Plane)
            mime_type: MIME type for data
            tags: Optional tags
            metadata: Optional metadata
        """
        # Create collection if needed
        if collection not in self._collections:
            self.create_collection(collection)
        
        # Create item
        item = DimensionalItem(
            id=self._generate_id(),
            name=name,
            collection=collection,
            level=level,
            data=data,
            mime_type=mime_type,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Store item
        self._items[collection][item.id] = item
        self._by_level[level].add(item.id)
        
        # Update collection count
        self._collections[collection].item_count = len(self._items[collection])
        
        # Register in substrate
        self.substrate.create_token(
            location=(hash(item.id) % 1000, level, 0),
            signature={level},
            payload=lambda i=item: i.data,
            token_id=item.id
        )
        
        self._stats['writes'] += 1
        self._update_stats()
        self._save()
        
        return item
    
    def retrieve(self, item_id: str) -> Optional[Any]:
        """Retrieve an item's data by ID"""
        self._stats['reads'] += 1
        
        for items in self._items.values():
            if item_id in items:
                return items[item_id].data
        return None
    
    def get_item(self, item_id: str) -> Optional[DimensionalItem]:
        """Get full item by ID"""
        self._stats['reads'] += 1
        
        for items in self._items.values():
            if item_id in items:
                return items[item_id]
        return None
    
    def update(self, item_id: str, data: Any) -> bool:
        """Update an item's data"""
        for items in self._items.values():
            if item_id in items:
                items[item_id].data = data
                items[item_id].updated_at = datetime.now().isoformat()
                self._stats['writes'] += 1
                self._save()
                return True
        return False
    
    def delete_item(self, item_id: str) -> bool:
        """Delete an item"""
        for coll_name, items in self._items.items():
            if item_id in items:
                item = items[item_id]
                self._by_level[item.level].discard(item_id)
                del items[item_id]
                self._collections[coll_name].item_count = len(items)
                self._stats['writes'] += 1
                self._update_stats()
                self._save()
                return True
        return False
    
    def list_items(self, collection: str = None) -> List[DimensionalItem]:
        """List items, optionally filtered by collection"""
        self._stats['reads'] += 1
        
        if collection:
            if collection in self._items:
                return list(self._items[collection].values())
            return []
        
        return [
            item
            for items in self._items.values()
            for item in items.values()
        ]
    
    # -------------------------------------------------------------------------
    # Dimensional Operations
    # -------------------------------------------------------------------------
    
    def invoke(self, level: int) -> List[Any]:
        """
        Invoke a dimensional level.
        
        Level 6: Hard drive summary
        Level 5: All collections
        Level 4: All items
        Level 3-1: Items at specific levels
        """
        self._stats['invocations'] += 1
        self.kernel.invoke(level)
        
        if level == 6:
            return [{
                'name': 'Universal Hard Drive',
                'collections': self._stats['collections'],
                'items': self._stats['items'],
                'reads': self._stats['reads'],
                'writes': self._stats['writes']
            }]
        
        elif level == 5:
            return list(self._collections.values())
        
        elif level == 4:
            return self.list_items()
        
        else:
            # Return items at specific level
            return [
                self.get_item(item_id)
                for item_id in self._by_level.get(level, [])
            ]
    
    def spiral_down(self, collection: str) -> List[DimensionalItem]:
        """Spiral down from collection to its items"""
        self.kernel.spiral_down()
        return list(self._items.get(collection, {}).values())
    
    def spiral_up(self, item_id: str) -> Optional[Collection]:
        """Spiral up from item to its collection"""
        self.kernel.spiral_up()
        
        for coll_name, items in self._items.items():
            if item_id in items:
                return self._collections[coll_name]
        return None
    
    # -------------------------------------------------------------------------
    # Integration
    # -------------------------------------------------------------------------
    
    def attach_database(self, db: HelixDatabase):
        """Attach a HelixDatabase for structured data"""
        self._database = db
        self.logger.width("Database attached")
    
    def attach_connector(self, connector: UniversalConnector):
        """Attach a UniversalConnector for live API data"""
        self._connector = connector
        self.logger.width("Connector attached")
    
    def import_from_database(self, collection_name: str):
        """Import data from attached database"""
        if not self._database:
            return
        
        records = self._database.invoke(4)  # Get all records
        for record in records:
            self.store(
                collection=collection_name,
                name=record.id,
                data=record.data,
                level=4,
                tags=['imported', 'database']
            )
    
    def import_from_connector(self, api_name: str, collection_name: str = None):
        """Import data from attached connector"""
        if not self._connector:
            return None
        
        result = self._connector.connect(api_name)
        if result.success:
            coll = collection_name or api_name
            return self.store(
                collection=coll,
                name=f"{api_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                data=result.data,
                level=4,
                tags=['imported', 'api', api_name]
            )
        return None
    
    # -------------------------------------------------------------------------
    # Info & Stats
    # -------------------------------------------------------------------------
    
    def stats(self) -> Dict[str, Any]:
        """Get hard drive statistics"""
        return {
            **self._stats,
            'by_level': {
                level: len(items)
                for level, items in self._by_level.items()
            }
        }
    
    def info(self) -> str:
        """Get human-readable info"""
        lines = [
            "Universal Hard Drive",
            "=" * 50,
            f"Collections: {self._stats['collections']}",
            f"Items: {self._stats['items']}",
            f"Reads: {self._stats['reads']}",
            f"Writes: {self._stats['writes']}",
            "",
            "Collections:"
        ]
        
        for coll in self._collections.values():
            lines.append(f"  {coll.icon} {coll.name}: {coll.item_count} items")
        
        return '\n'.join(lines)


# =============================================================================
# WEB SERVER
# =============================================================================

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Universal Hard Drive</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header {
            background: linear-gradient(90deg, #662d91 0%, #9d4edd 100%);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        h1 { font-size: 2em; margin-bottom: 10px; }
        .subtitle { opacity: 0.9; }
        
        .levels {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .level-btn {
            background: #2a2a4e;
            border: 2px solid #4a4a6e;
            color: #e0e0e0;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .level-btn:hover { background: #3a3a5e; border-color: #9d4edd; }
        .level-btn.active { background: #662d91; border-color: #9d4edd; }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        .card {
            background: #2a2a4e;
            border-radius: 10px;
            padding: 20px;
            border: 1px solid #4a4a6e;
            transition: transform 0.3s, border-color 0.3s;
        }
        .card:hover { transform: translateY(-2px); border-color: #9d4edd; }
        .card-icon { font-size: 2em; margin-bottom: 10px; }
        .card-title { font-size: 1.2em; margin-bottom: 10px; color: #fff; }
        .card-meta { font-size: 0.9em; opacity: 0.7; }
        .card-data {
            background: #1a1a2e;
            border-radius: 5px;
            padding: 10px;
            margin-top: 10px;
            font-family: monospace;
            font-size: 0.85em;
            max-height: 150px;
            overflow-y: auto;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat {
            background: #2a2a4e;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value { font-size: 2em; color: #9d4edd; }
        .stat-label { font-size: 0.9em; opacity: 0.7; }
        
        .actions {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .btn {
            background: #662d91;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .btn:hover { background: #7d3db1; }
        
        .empty-state {
            text-align: center;
            padding: 50px;
            opacity: 0.7;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🦋 Universal Hard Drive</h1>
            <p class="subtitle">Dimensional Storage Interface</p>
        </header>
        
        <div class="stats">
            %%STATS%%
        </div>
        
        <div class="levels">
            <button class="level-btn" onclick="location.href='/?level=6'">🌌 Level 6 - Whole</button>
            <button class="level-btn" onclick="location.href='/?level=5'">📦 Level 5 - Collections</button>
            <button class="level-btn" onclick="location.href='/?level=4'">📄 Level 4 - Items</button>
        </div>
        
        <div class="grid">
            %%CONTENT%%
        </div>
    </div>
</body>
</html>
"""


class UHDHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for Universal Hard Drive"""
    
    uhd: UniversalHardDrive = None  # Set by server
    
    def log_message(self, format, *args):
        pass  # Suppress default logging
    
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if parsed.path == '/':
            self.serve_home(params)
        elif parsed.path == '/api/stats':
            self.serve_json(self.uhd.stats())
        elif parsed.path == '/api/collections':
            self.serve_json([
                {'name': c.name, 'icon': c.icon, 'items': c.item_count}
                for c in self.uhd.list_collections()
            ])
        elif parsed.path == '/api/items':
            coll = params.get('collection', [None])[0]
            items = self.uhd.list_items(coll)
            self.serve_json([
                {'id': i.id, 'name': i.name, 'level': i.level}
                for i in items
            ])
        else:
            self.send_error(404)
    
    def serve_home(self, params):
        level = int(params.get('level', [5])[0])
        
        # Get stats
        stats = self.uhd.stats()
        stats_html = f"""
            <div class="stat">
                <div class="stat-value">{stats['collections']}</div>
                <div class="stat-label">Collections</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats['items']}</div>
                <div class="stat-label">Items</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats['reads']}</div>
                <div class="stat-label">Reads</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats['writes']}</div>
                <div class="stat-label">Writes</div>
            </div>
        """
        
        # Get content based on level
        data = self.uhd.invoke(level)
        
        if not data:
            content_html = '<div class="empty-state">No data at this level. Store some items first!</div>'
        elif level == 6:
            # Whole view
            d = data[0]
            content_html = f"""
                <div class="card">
                    <div class="card-icon">🌌</div>
                    <div class="card-title">{d['name']}</div>
                    <div class="card-data">
                        Collections: {d['collections']}<br>
                        Items: {d['items']}<br>
                        Total Reads: {d['reads']}<br>
                        Total Writes: {d['writes']}
                    </div>
                </div>
            """
        elif level == 5:
            # Collections view
            cards = []
            for coll in data:
                cards.append(f"""
                    <div class="card">
                        <div class="card-icon">{coll.icon}</div>
                        <div class="card-title">{coll.name}</div>
                        <div class="card-meta">{coll.item_count} items</div>
                        <div class="card-meta">{coll.description or 'No description'}</div>
                    </div>
                """)
            content_html = ''.join(cards) if cards else '<div class="empty-state">No collections yet</div>'
        elif level == 4:
            # Items view
            cards = []
            for item in data:
                data_preview = json.dumps(item.data, indent=2)[:200]
                if len(json.dumps(item.data)) > 200:
                    data_preview += '...'
                cards.append(f"""
                    <div class="card">
                        <div class="card-icon">{LEVEL_ICONS.get(item.level, '📄')}</div>
                        <div class="card-title">{item.name}</div>
                        <div class="card-meta">Collection: {item.collection} | Level {item.level}</div>
                        <div class="card-data"><pre>{data_preview}</pre></div>
                    </div>
                """)
            content_html = ''.join(cards) if cards else '<div class="empty-state">No items yet</div>'
        else:
            content_html = '<div class="empty-state">Navigate to a level</div>'
        
        html = HTML_TEMPLATE.replace('%%STATS%%', stats_html).replace('%%CONTENT%%', content_html)
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


def run_server(uhd: UniversalHardDrive = None, host: str = '127.0.0.1', port: int = 8000):
    """Run the web server"""
    if uhd is None:
        uhd = UniversalHardDrive()
    
    UHDHandler.uhd = uhd
    
    server = HTTPServer((host, port), UHDHandler)
    print(f"🦋 Universal Hard Drive Server")
    print(f"   Running at http://{host}:{port}")
    print(f"   Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        server.shutdown()


# =============================================================================
# DEMO
# =============================================================================

def demo():
    """Demonstrate the Universal Hard Drive"""
    print("=" * 60)
    print("Universal Hard Drive Demo")
    print("=" * 60)
    
    # Create hard drive
    uhd = UniversalHardDrive(data_dir="data/uhd_demo")
    
    # Create collections
    print("\n📁 Creating collections...")
    uhd.create_collection("documents", "📄", "Text documents and notes")
    uhd.create_collection("images", "🖼️", "Image references")
    uhd.create_collection("config", "⚙️", "Configuration data")
    uhd.create_collection("api_cache", "🌐", "Cached API responses")
    
    # Store some items
    print("\n💾 Storing items...")
    
    uhd.store("documents", "readme.txt", {
        "title": "Welcome",
        "content": "This is the Universal Hard Drive demo."
    })
    
    uhd.store("documents", "notes.txt", {
        "title": "My Notes",
        "items": ["Buy milk", "Write code", "Sleep"]
    })
    
    uhd.store("config", "settings.json", {
        "theme": "dark",
        "language": "en",
        "notifications": True
    })
    
    uhd.store("images", "avatar.png", {
        "url": "https://example.com/avatar.png",
        "width": 256,
        "height": 256
    })
    
    # Show info
    print("\n📊 Hard Drive Info:")
    print(uhd.info())
    
    # Invoke levels
    print("\n🎯 INVOKE Level 6 (Whole):")
    whole = uhd.invoke(6)
    print(f"  {whole[0]}")
    
    print("\n🎯 INVOKE Level 5 (Collections):")
    collections = uhd.invoke(5)
    for coll in collections:
        print(f"  {coll.icon} {coll.name}: {coll.item_count} items")
    
    print("\n🎯 INVOKE Level 4 (Items):")
    items = uhd.invoke(4)
    for item in items:
        print(f"  📄 {item.name} ({item.collection})")
    
    # Attach connector and import
    print("\n🔌 Attaching Universal Connector...")
    connector = UniversalConnector()
    uhd.attach_connector(connector)
    
    print("📥 Importing live data from ISS API...")
    uhd.import_from_connector("iss_location", "api_cache")
    
    print("📥 Importing random joke...")
    uhd.import_from_connector("joke", "api_cache")
    
    # Final stats
    print("\n📈 Final Stats:")
    stats = uhd.stats()
    print(f"  Collections: {stats['collections']}")
    print(f"  Items: {stats['items']}")
    print(f"  Reads: {stats['reads']}")
    print(f"  Writes: {stats['writes']}")
    
    print("\n✨ Demo complete! Data saved to: data/uhd_demo/")
    print("   Run 'run_server()' to start web interface")


if __name__ == "__main__":
    demo()
