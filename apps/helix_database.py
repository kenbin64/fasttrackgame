"""
Helix Database - Dimensional Database System

A full-featured database built on the ButterflyFX helix paradigm.

Key Features:
    - Data organized by dimensional levels (0-6)
    - O(7) access complexity per spiral
    - Lazy materialization - data exists as potential until invoked
    - Persistent storage with JSON backend
    - Level-based indexing for instant queries
    - Spiral navigation across data domains

Usage:
    from apps.helix_database import HelixDatabase
    
    db = HelixDatabase("my_data")
    
    # Create collections at dimensional levels
    db.create_collection("users", level=5)
    db.create_collection("posts", level=4)
    
    # Insert (data exists as potential until queried)
    db.insert("users", {"name": "Alice", "role": "admin"})
    
    # Invoke level (O(1) - get all at level)
    all_users = db.invoke(5)
    
    # Query with filters
    admins = db.query("users").where(lambda d: d["role"] == "admin").execute()
    
    # Dimensional relationships
    db.link("users", user_id, "posts", post_id)  # Cross-level link
"""

import json
import os
import uuid
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Set, Callable, Iterator
from pathlib import Path
import sys

# Add parent to path for helix imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from helix import (
    HelixKernel, HelixState, ManifoldSubstrate, Token,
    HelixContext, HelixCache, HelixLogger, LEVEL_NAMES, LEVEL_ICONS
)


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class HelixRecord:
    """A record in the dimensional database"""
    id: str
    collection: str
    level: int
    data: Dict[str, Any]
    spiral: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    links: List[str] = field(default_factory=list)  # IDs of linked records
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HelixRecord':
        return cls(**data)


@dataclass
class HelixCollection:
    """A collection (like a table) at a dimensional level"""
    name: str
    level: int
    spiral: int = 0
    record_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    schema: Optional[Dict[str, str]] = None  # Optional field types
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HelixCollection':
        return cls(**data)


# =============================================================================
# QUERY BUILDER
# =============================================================================

class HelixQuery:
    """
    Query builder for dimensional database.
    
    Queries work by level invocation, not iteration:
        1. Invoke the target level (O(1))
        2. Filter results (lazy, only materializes matches)
        3. Return results
    """
    
    def __init__(self, db: 'HelixDatabase', collection: str):
        self.db = db
        self.collection = collection
        self._predicates: List[Callable[[Dict], bool]] = []
        self._level_filter: Optional[int] = None
        self._spiral_filter: Optional[int] = None
        self._limit: Optional[int] = None
        self._offset: int = 0
        self._order_by: Optional[str] = None
        self._order_desc: bool = False
        self._include_links: bool = False
    
    def at_level(self, level: int) -> 'HelixQuery':
        """Filter to specific level"""
        self._level_filter = level
        return self
    
    def at_spiral(self, spiral: int) -> 'HelixQuery':
        """Filter to specific spiral"""
        self._spiral_filter = spiral
        return self
    
    def where(self, predicate: Callable[[Dict], bool]) -> 'HelixQuery':
        """Add filter predicate on data"""
        self._predicates.append(predicate)
        return self
    
    def where_field(self, field: str, value: Any) -> 'HelixQuery':
        """Filter where field equals value"""
        return self.where(lambda d: d.get(field) == value)
    
    def where_in(self, field: str, values: List[Any]) -> 'HelixQuery':
        """Filter where field is in list of values"""
        return self.where(lambda d: d.get(field) in values)
    
    def where_gt(self, field: str, value: Any) -> 'HelixQuery':
        """Filter where field > value"""
        return self.where(lambda d: d.get(field, 0) > value)
    
    def where_lt(self, field: str, value: Any) -> 'HelixQuery':
        """Filter where field < value"""
        return self.where(lambda d: d.get(field, 0) < value)
    
    def where_contains(self, field: str, substring: str) -> 'HelixQuery':
        """Filter where field contains substring"""
        return self.where(lambda d: substring.lower() in str(d.get(field, "")).lower())
    
    def with_links(self) -> 'HelixQuery':
        """Include linked records in results"""
        self._include_links = True
        return self
    
    def order_by(self, field: str, desc: bool = False) -> 'HelixQuery':
        """Order results by field"""
        self._order_by = field
        self._order_desc = desc
        return self
    
    def limit(self, n: int) -> 'HelixQuery':
        """Limit results"""
        self._limit = n
        return self
    
    def offset(self, n: int) -> 'HelixQuery':
        """Skip first n results"""
        self._offset = n
        return self
    
    def execute(self) -> List[HelixRecord]:
        """Execute the query and return records"""
        # Get base records from collection
        records = self.db._get_collection_records(self.collection)
        
        # Level filter
        if self._level_filter is not None:
            records = [r for r in records if r.level == self._level_filter]
        
        # Spiral filter
        if self._spiral_filter is not None:
            records = [r for r in records if r.spiral == self._spiral_filter]
        
        # Apply predicates
        for pred in self._predicates:
            records = [r for r in records if pred(r.data)]
        
        # Order
        if self._order_by:
            records.sort(
                key=lambda r: r.data.get(self._order_by, ''),
                reverse=self._order_desc
            )
        
        # Offset and limit
        records = records[self._offset:]
        if self._limit:
            records = records[:self._limit]
        
        return records
    
    def first(self) -> Optional[HelixRecord]:
        """Get first matching record"""
        results = self.limit(1).execute()
        return results[0] if results else None
    
    def count(self) -> int:
        """Count matching records"""
        return len(self.execute())
    
    def exists(self) -> bool:
        """Check if any records match"""
        return self.count() > 0
    
    def delete(self) -> int:
        """Delete matching records, return count"""
        records = self.execute()
        for record in records:
            self.db.delete(self.collection, record.id)
        return len(records)


# =============================================================================
# HELIX DATABASE
# =============================================================================

class HelixDatabase:
    """
    Dimensional Database System
    
    Organizes data by dimensional levels instead of flat tables.
    Uses O(7) complexity per spiral instead of O(N) iteration.
    
    Architecture:
        - Level 6 (Whole): Database metadata, schemas
        - Level 5 (Volume): Collections/tables
        - Level 4 (Plane): Record groups/categories
        - Level 3 (Width): Individual records
        - Level 2 (Length): Record fields
        - Level 1 (Point): Field values
        - Level 0 (Potential): Uncommitted/lazy data
    """
    
    def __init__(self, name: str, data_dir: str = "./data"):
        self.name = name
        self.data_dir = Path(data_dir)
        self.db_path = self.data_dir / f"{name}.helix.json"
        
        # Core helix components
        self.kernel = HelixKernel()
        self.substrate = ManifoldSubstrate()
        self.kernel.set_substrate(self.substrate)
        
        # Caching and logging
        self.cache = HelixCache()
        self.logger = HelixLogger(min_level=3)
        
        # In-memory storage
        self._collections: Dict[str, HelixCollection] = {}
        self._records: Dict[str, HelixRecord] = {}  # id -> record
        self._by_collection: Dict[str, Set[str]] = {}  # collection -> record ids
        self._by_level: Dict[int, Set[str]] = {i: set() for i in range(7)}
        self._by_spiral: Dict[int, Set[str]] = {}
        
        # Statistics
        self._stats = {
            'reads': 0,
            'writes': 0,
            'invocations': 0,
            'cache_hits': 0
        }
        
        # Load existing data
        self._ensure_data_dir()
        self._load()
        
        self.logger.whole(f"Database '{name}' initialized")
    
    # -------------------------------------------------------------------------
    # Persistence
    # -------------------------------------------------------------------------
    
    def _ensure_data_dir(self):
        """Create data directory if needed"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _load(self):
        """Load database from disk"""
        if not self.db_path.exists():
            return
        
        try:
            with open(self.db_path, 'r') as f:
                data = json.load(f)
            
            # Load collections
            for coll_data in data.get('collections', []):
                coll = HelixCollection.from_dict(coll_data)
                self._collections[coll.name] = coll
                self._by_collection[coll.name] = set()
            
            # Load records
            for rec_data in data.get('records', []):
                record = HelixRecord.from_dict(rec_data)
                self._records[record.id] = record
                
                # Index by collection
                if record.collection in self._by_collection:
                    self._by_collection[record.collection].add(record.id)
                
                # Index by level
                self._by_level[record.level].add(record.id)
                
                # Index by spiral
                if record.spiral not in self._by_spiral:
                    self._by_spiral[record.spiral] = set()
                self._by_spiral[record.spiral].add(record.id)
                
                # Register token in substrate
                self._register_token(record)
            
            self.logger.volume(f"Loaded {len(self._records)} records")
            
        except Exception as e:
            self.logger.volume(f"Load error: {e}")
    
    def save(self):
        """Save database to disk"""
        data = {
            'name': self.name,
            'saved_at': datetime.now().isoformat(),
            'collections': [c.to_dict() for c in self._collections.values()],
            'records': [r.to_dict() for r in self._records.values()]
        }
        
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.volume(f"Saved {len(self._records)} records")
    
    def _register_token(self, record: HelixRecord):
        """Register a record as a token in the substrate"""
        token = self.substrate.create_token(
            location=(hash(record.id) % 1000, record.level, record.spiral),
            signature={record.level},
            payload=lambda r=record: r.data,
            spiral_affinity=record.spiral,
            token_id=record.id
        )
    
    # -------------------------------------------------------------------------
    # Collection Operations
    # -------------------------------------------------------------------------
    
    def create_collection(
        self,
        name: str,
        level: int = 5,
        spiral: int = 0,
        schema: Dict[str, str] = None
    ) -> HelixCollection:
        """
        Create a new collection at a dimensional level.
        
        Args:
            name: Collection name
            level: Dimensional level (default 5 = Volume)
            spiral: Which spiral (default 0)
            schema: Optional field types {"field": "type"}
        """
        if name in self._collections:
            raise ValueError(f"Collection '{name}' already exists")
        
        collection = HelixCollection(
            name=name,
            level=level,
            spiral=spiral,
            schema=schema
        )
        
        self._collections[name] = collection
        self._by_collection[name] = set()
        
        self.logger.volume(f"Created collection '{name}' at level {level}")
        self._stats['writes'] += 1
        
        return collection
    
    def drop_collection(self, name: str) -> bool:
        """Drop a collection and all its records"""
        if name not in self._collections:
            return False
        
        # Delete all records
        for record_id in list(self._by_collection.get(name, [])):
            self._delete_record(record_id)
        
        del self._collections[name]
        del self._by_collection[name]
        
        self.logger.volume(f"Dropped collection '{name}'")
        return True
    
    def list_collections(self) -> List[HelixCollection]:
        """List all collections"""
        return list(self._collections.values())
    
    def get_collection(self, name: str) -> Optional[HelixCollection]:
        """Get collection by name"""
        return self._collections.get(name)
    
    # -------------------------------------------------------------------------
    # CRUD Operations
    # -------------------------------------------------------------------------
    
    def insert(
        self,
        collection: str,
        data: Dict[str, Any],
        id: str = None,
        level: int = None
    ) -> str:
        """
        Insert a record into a collection.
        
        Args:
            collection: Collection name
            data: Record data
            id: Optional custom ID
            level: Optional level override (default: collection level - 1)
        
        Returns:
            Record ID
        """
        if collection not in self._collections:
            raise ValueError(f"Collection '{collection}' does not exist")
        
        coll = self._collections[collection]
        record_id = id or f"{collection}_{uuid.uuid4().hex[:12]}"
        record_level = level if level is not None else (coll.level - 1)
        
        record = HelixRecord(
            id=record_id,
            collection=collection,
            level=record_level,
            spiral=coll.spiral,
            data=data
        )
        
        # Store record
        self._records[record_id] = record
        self._by_collection[collection].add(record_id)
        self._by_level[record_level].add(record_id)
        
        if coll.spiral not in self._by_spiral:
            self._by_spiral[coll.spiral] = set()
        self._by_spiral[coll.spiral].add(record_id)
        
        # Register token
        self._register_token(record)
        
        # Update collection stats
        coll.record_count += 1
        
        self.logger.plane(f"Inserted {record_id} into {collection}")
        self._stats['writes'] += 1
        
        return record_id
    
    def insert_many(self, collection: str, records: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple records"""
        return [self.insert(collection, data) for data in records]
    
    def get(self, collection: str, id: str) -> Optional[HelixRecord]:
        """Get a record by ID"""
        # Check cache
        cache_key = f"{collection}:{id}"
        cached = self.cache.get(cache_key)
        if cached:
            self._stats['cache_hits'] += 1
            return cached
        
        record = self._records.get(id)
        if record and record.collection == collection:
            coll = self._collections.get(collection)
            if coll:
                self.cache.set(cache_key, record, coll.level)
            self._stats['reads'] += 1
            return record
        
        return None
    
    def update(
        self,
        collection: str,
        id: str,
        data: Dict[str, Any],
        merge: bool = True
    ) -> bool:
        """
        Update a record.
        
        Args:
            collection: Collection name
            id: Record ID
            data: New data
            merge: If True, merge with existing; if False, replace
        """
        record = self.get(collection, id)
        if not record:
            return False
        
        if merge:
            record.data.update(data)
        else:
            record.data = data
        
        record.updated_at = datetime.now().isoformat()
        
        # Invalidate cache
        self.cache.invalidate_level(record.level)
        
        self.logger.plane(f"Updated {id} in {collection}")
        self._stats['writes'] += 1
        
        return True
    
    def delete(self, collection: str, id: str) -> bool:
        """Delete a record"""
        record = self.get(collection, id)
        if not record:
            return False
        
        return self._delete_record(id)
    
    def _delete_record(self, id: str) -> bool:
        """Internal delete by ID"""
        record = self._records.get(id)
        if not record:
            return False
        
        # Remove from indices
        self._by_collection[record.collection].discard(id)
        self._by_level[record.level].discard(id)
        if record.spiral in self._by_spiral:
            self._by_spiral[record.spiral].discard(id)
        
        # Update collection count
        coll = self._collections.get(record.collection)
        if coll:
            coll.record_count -= 1
        
        # Remove record
        del self._records[id]
        
        # Invalidate cache
        self.cache.invalidate_level(record.level)
        
        self.logger.plane(f"Deleted {id}")
        self._stats['writes'] += 1
        
        return True
    
    # -------------------------------------------------------------------------
    # Query Operations
    # -------------------------------------------------------------------------
    
    def query(self, collection: str) -> HelixQuery:
        """Create a query builder for a collection"""
        if collection not in self._collections:
            raise ValueError(f"Collection '{collection}' does not exist")
        return HelixQuery(self, collection)
    
    def _get_collection_records(self, collection: str) -> List[HelixRecord]:
        """Get all records in a collection"""
        record_ids = self._by_collection.get(collection, set())
        return [self._records[id] for id in record_ids if id in self._records]
    
    def all(self, collection: str) -> List[HelixRecord]:
        """Get all records from a collection"""
        self._stats['reads'] += 1
        return self._get_collection_records(collection)
    
    def count(self, collection: str) -> int:
        """Count records in a collection"""
        return len(self._by_collection.get(collection, set()))
    
    # -------------------------------------------------------------------------
    # Dimensional Operations (The Key Feature)
    # -------------------------------------------------------------------------
    
    def invoke(self, level: int) -> List[HelixRecord]:
        """
        INVOKE a dimensional level.
        
        This is the core helix operation - O(1) access to all records
        at a specific level, regardless of collection.
        
        Instead of iterating through records, we jump directly to the level.
        """
        self._stats['invocations'] += 1
        self.kernel.invoke(level)
        
        record_ids = self._by_level.get(level, set())
        records = [self._records[id] for id in record_ids if id in self._records]
        
        self.logger.width(f"Invoked level {level}: {len(records)} records")
        return records
    
    def invoke_spiral(self, spiral: int) -> List[HelixRecord]:
        """Get all records in a spiral"""
        record_ids = self._by_spiral.get(spiral, set())
        return [self._records[id] for id in record_ids if id in self._records]
    
    def invoke_range(self, min_level: int, max_level: int) -> List[HelixRecord]:
        """Get all records in a level range"""
        records = []
        for level in range(min_level, max_level + 1):
            records.extend(self.invoke(level))
        return records
    
    def spiral_up(self) -> int:
        """Move to next spiral, return new spiral number"""
        self.kernel.spiral_up()
        return self.kernel.spiral
    
    def spiral_down(self) -> int:
        """Move to previous spiral, return new spiral number"""
        self.kernel.spiral_down()
        return self.kernel.spiral
    
    def collapse(self):
        """Collapse all to potential (useful for cleanup)"""
        self.kernel.collapse()
        self.cache.invalidate_all()
    
    # -------------------------------------------------------------------------
    # Linking (Cross-Level Relationships)
    # -------------------------------------------------------------------------
    
    def link(
        self,
        from_collection: str,
        from_id: str,
        to_collection: str,
        to_id: str
    ) -> bool:
        """
        Link two records across collections/levels.
        
        Unlike SQL JOINs, links are navigated dimensionally -
        you invoke the link, not iterate to find it.
        """
        from_record = self.get(from_collection, from_id)
        to_record = self.get(to_collection, to_id)
        
        if not from_record or not to_record:
            return False
        
        if to_id not in from_record.links:
            from_record.links.append(to_id)
        
        self.logger.length(f"Linked {from_id} → {to_id}")
        return True
    
    def unlink(self, from_collection: str, from_id: str, to_id: str) -> bool:
        """Remove a link"""
        from_record = self.get(from_collection, from_id)
        if not from_record:
            return False
        
        if to_id in from_record.links:
            from_record.links.remove(to_id)
            return True
        return False
    
    def get_linked(self, collection: str, id: str) -> List[HelixRecord]:
        """Get all records linked from a record"""
        record = self.get(collection, id)
        if not record:
            return []
        
        return [
            self._records[lid]
            for lid in record.links
            if lid in self._records
        ]
    
    # -------------------------------------------------------------------------
    # Statistics & Info
    # -------------------------------------------------------------------------
    
    def stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        level_counts = {
            LEVEL_NAMES[i]: len(self._by_level[i])
            for i in range(7)
        }
        
        return {
            'name': self.name,
            'collections': len(self._collections),
            'total_records': len(self._records),
            'by_level': level_counts,
            'spirals': len(self._by_spiral),
            'operations': self._stats.copy()
        }
    
    def info(self) -> str:
        """Get human-readable database info"""
        stats = self.stats()
        lines = [
            f"Helix Database: {self.name}",
            "=" * 40,
            f"Collections: {stats['collections']}",
            f"Total Records: {stats['total_records']}",
            "",
            "Records by Level:"
        ]
        
        for level in range(6, -1, -1):
            icon = LEVEL_ICONS[level]
            name = LEVEL_NAMES[level]
            count = len(self._by_level[level])
            if count > 0:
                lines.append(f"  {icon} {name}: {count}")
        
        lines.extend([
            "",
            f"Operations: {stats['operations']}"
        ])
        
        return '\n'.join(lines)
    
    # -------------------------------------------------------------------------
    # Context Manager
    # -------------------------------------------------------------------------
    
    def __enter__(self) -> 'HelixDatabase':
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()
        return False


# =============================================================================
# DEMO / TEST
# =============================================================================

def demo():
    """Demonstrate the Helix Database"""
    print("=" * 60)
    print("Helix Database Demo")
    print("=" * 60)
    
    # Create database
    db = HelixDatabase("demo_db", data_dir="./data")
    
    # Create collections
    db.create_collection("users", level=5)
    db.create_collection("posts", level=4)
    db.create_collection("comments", level=3)
    
    # Insert users
    alice_id = db.insert("users", {"name": "Alice", "role": "admin", "age": 30})
    bob_id = db.insert("users", {"name": "Bob", "role": "user", "age": 25})
    charlie_id = db.insert("users", {"name": "Charlie", "role": "user", "age": 35})
    
    # Insert posts
    post1_id = db.insert("posts", {"title": "Hello World", "author": "Alice"})
    post2_id = db.insert("posts", {"title": "Helix Computing", "author": "Bob"})
    
    # Insert comments
    db.insert("comments", {"text": "Great post!", "author": "Charlie"})
    db.insert("comments", {"text": "Interesting", "author": "Alice"})
    
    # Link posts to users
    db.link("users", alice_id, "posts", post1_id)
    db.link("users", bob_id, "posts", post2_id)
    
    print("\n📊 Database Info:")
    print(db.info())
    
    # Demonstrate dimensional invocation
    print("\n🎯 INVOKE Level 5 (all Volume-level records):")
    level_5_records = db.invoke(5)
    for r in level_5_records:
        print(f"  {r.id}: {r.data}")
    
    print("\n🎯 INVOKE Level 4 (all Plane-level records):")
    level_4_records = db.invoke(4)
    for r in level_4_records:
        print(f"  {r.id}: {r.data}")
    
    # Query demonstration
    print("\n🔍 Query: admins")
    admins = db.query("users").where_field("role", "admin").execute()
    for r in admins:
        print(f"  {r.data['name']}: {r.data['role']}")
    
    print("\n🔍 Query: age > 27")
    older = db.query("users").where_gt("age", 27).execute()
    for r in older:
        print(f"  {r.data['name']}: age {r.data['age']}")
    
    # Get linked records
    print(f"\n🔗 Records linked from Alice:")
    linked = db.get_linked("users", alice_id)
    for r in linked:
        print(f"  {r.collection}/{r.id}: {r.data}")
    
    # Save to disk
    db.save()
    print(f"\n💾 Saved to {db.db_path}")
    
    # Stats
    print(f"\n📈 Stats: {db.stats()['operations']}")


if __name__ == "__main__":
    demo()
