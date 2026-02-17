"""
ButterflyFX Foundational Library

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

Part of ButterflyFX Infrastructure - Open source foundation layer.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

Layer 3: Foundation
    Reusable components that can be used in many applications.
    Built on primitives and utilities layers.
    
Components:
    - HelixDB: In-memory dimensional database
    - HelixFS: Virtual filesystem using dimensional model
    - HelixAPI: API client with dimensional caching
    - HelixStore: Key-value store with dimensional organization
    - HelixGraph: Graph structure using helix navigation
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Set, Optional, List, Dict, Iterator, TypeVar, Generic
from .primitives import (
    HelixContext, DimensionalType, HelixKernel, 
    ManifoldSubstrate, Token, LEVEL_NAMES
)
from .utilities import (
    HelixPath, HelixQuery, HelixCache, 
    HelixSerializer, HelixLogger
)
import uuid
from datetime import datetime
from pathlib import Path
import json

T = TypeVar('T')


# =============================================================================
# HELIX DB - In-memory dimensional database
# =============================================================================

@dataclass
class HelixRecord:
    """A record in the dimensional database"""
    id: str
    table: str
    level: int
    data: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class HelixDB:
    """
    In-memory dimensional database.
    
    Instead of tables with rows, data is organized by dimensional levels:
        - Level 6: Entire database state
        - Level 5: Tables/collections
        - Level 4: Record groups (categories)
        - Level 3: Individual records
        - Level 2: Record fields
        - Level 1: Field values
        - Level 0: Raw data
    
    Queries work by level invocation, not row iteration.
    
    Usage:
        db = HelixDB()
        db.create_table('users', level=5)
        db.insert('users', {'name': 'Alice', 'age': 30})
        users = db.query('users').where(lambda r: r['age'] > 25).execute()
    """
    
    def __init__(self, name: str = "helix_db"):
        self.name = name
        self.ctx = HelixContext()
        self.tables: Dict[str, Dict[str, HelixRecord]] = {}
        self.table_levels: Dict[str, int] = {}
        self.logger = HelixLogger(min_level=4)
    
    # -------------------------------------------------------------------------
    # Schema Operations
    # -------------------------------------------------------------------------
    
    def create_table(self, name: str, level: int = 5) -> None:
        """Create a table at a specific level"""
        if name in self.tables:
            raise ValueError(f"Table '{name}' already exists")
        
        self.tables[name] = {}
        self.table_levels[name] = level
        self.logger.volume(f"Created table '{name}' at level {level}")
    
    def drop_table(self, name: str) -> None:
        """Drop a table"""
        if name in self.tables:
            del self.tables[name]
            del self.table_levels[name]
            self.logger.volume(f"Dropped table '{name}'")
    
    def list_tables(self) -> List[str]:
        """List all tables"""
        return list(self.tables.keys())
    
    # -------------------------------------------------------------------------
    # CRUD Operations
    # -------------------------------------------------------------------------
    
    def insert(self, table: str, data: Dict[str, Any], id: str = None) -> str:
        """Insert a record"""
        if table not in self.tables:
            raise ValueError(f"Table '{table}' does not exist")
        
        record_id = id or f"{table}_{uuid.uuid4().hex[:8]}"
        level = self.table_levels[table]
        
        record = HelixRecord(
            id=record_id,
            table=table,
            level=level - 1,  # Records are one level below table
            data=data
        )
        
        self.tables[table][record_id] = record
        
        # Register as token
        self.ctx.register(
            name=record_id,
            level=record.level,
            data=data
        )
        
        self.logger.plane(f"Inserted record {record_id} into {table}")
        return record_id
    
    def get(self, table: str, id: str) -> Optional[HelixRecord]:
        """Get a record by ID"""
        if table not in self.tables:
            return None
        return self.tables[table].get(id)
    
    def update(self, table: str, id: str, data: Dict[str, Any]) -> bool:
        """Update a record"""
        record = self.get(table, id)
        if not record:
            return False
        
        record.data.update(data)
        record.updated_at = datetime.now()
        self.logger.plane(f"Updated record {id} in {table}")
        return True
    
    def delete(self, table: str, id: str) -> bool:
        """Delete a record"""
        if table in self.tables and id in self.tables[table]:
            del self.tables[table][id]
            self.logger.plane(f"Deleted record {id} from {table}")
            return True
        return False
    
    # -------------------------------------------------------------------------
    # Query Operations
    # -------------------------------------------------------------------------
    
    def query(self, table: str) -> 'HelixDBQuery':
        """Create a query builder for a table"""
        return HelixDBQuery(self, table)
    
    def all(self, table: str) -> List[HelixRecord]:
        """Get all records from a table"""
        if table not in self.tables:
            return []
        return list(self.tables[table].values())
    
    def count(self, table: str) -> int:
        """Count records in a table"""
        if table not in self.tables:
            return 0
        return len(self.tables[table])
    
    # -------------------------------------------------------------------------
    # Dimensional Operations
    # -------------------------------------------------------------------------
    
    def invoke_level(self, level: int) -> List[HelixRecord]:
        """Get all records at a specific level"""
        results = []
        for table_records in self.tables.values():
            for record in table_records.values():
                if record.level == level:
                    results.append(record)
        return results
    
    def invoke_range(self, min_level: int, max_level: int) -> List[HelixRecord]:
        """Get all records in a level range"""
        results = []
        for table_records in self.tables.values():
            for record in table_records.values():
                if min_level <= record.level <= max_level:
                    results.append(record)
        return results
    
    # -------------------------------------------------------------------------
    # Persistence
    # -------------------------------------------------------------------------
    
    def to_json(self) -> str:
        """Export database to JSON"""
        return json.dumps({
            'name': self.name,
            'tables': {
                name: {
                    'level': self.table_levels[name],
                    'records': {
                        id: {
                            'id': r.id,
                            'level': r.level,
                            'data': r.data,
                            'created_at': r.created_at.isoformat(),
                            'updated_at': r.updated_at.isoformat()
                        }
                        for id, r in records.items()
                    }
                }
                for name, records in self.tables.items()
            }
        }, indent=2)
    
    @classmethod
    def from_json(cls, data: str) -> 'HelixDB':
        """Import database from JSON"""
        parsed = json.loads(data)
        db = cls(name=parsed.get('name', 'helix_db'))
        
        for table_name, table_data in parsed.get('tables', {}).items():
            db.create_table(table_name, level=table_data['level'])
            
            for record_id, record_data in table_data.get('records', {}).items():
                record = HelixRecord(
                    id=record_data['id'],
                    table=table_name,
                    level=record_data['level'],
                    data=record_data['data'],
                    created_at=datetime.fromisoformat(record_data['created_at']),
                    updated_at=datetime.fromisoformat(record_data['updated_at'])
                )
                db.tables[table_name][record_id] = record
        
        return db


class HelixDBQuery:
    """Query builder for HelixDB"""
    
    def __init__(self, db: HelixDB, table: str):
        self.db = db
        self.table = table
        self._predicates: List[Callable[[HelixRecord], bool]] = []
        self._limit: Optional[int] = None
        self._offset: int = 0
        self._order_by: Optional[str] = None
        self._order_desc: bool = False
    
    def where(self, predicate: Callable[[Dict], bool]) -> 'HelixDBQuery':
        """Add a filter predicate"""
        self._predicates.append(lambda r: predicate(r.data))
        return self
    
    def limit(self, n: int) -> 'HelixDBQuery':
        """Limit results"""
        self._limit = n
        return self
    
    def offset(self, n: int) -> 'HelixDBQuery':
        """Skip first n results"""
        self._offset = n
        return self
    
    def order_by(self, field: str, desc: bool = False) -> 'HelixDBQuery':
        """Order results by field"""
        self._order_by = field
        self._order_desc = desc
        return self
    
    def execute(self) -> List[HelixRecord]:
        """Execute the query"""
        results = self.db.all(self.table)
        
        # Apply filters
        for pred in self._predicates:
            results = [r for r in results if pred(r)]
        
        # Apply ordering
        if self._order_by:
            results.sort(
                key=lambda r: r.data.get(self._order_by, ''),
                reverse=self._order_desc
            )
        
        # Apply offset and limit
        results = results[self._offset:]
        if self._limit:
            results = results[:self._limit]
        
        return results
    
    def first(self) -> Optional[HelixRecord]:
        """Get first result"""
        results = self.limit(1).execute()
        return results[0] if results else None
    
    def count(self) -> int:
        """Count matching results"""
        return len(self.execute())


# =============================================================================
# HELIX FS - Virtual dimensional filesystem
# =============================================================================

@dataclass
class HelixFile:
    """A file in the dimensional filesystem"""
    path: HelixPath
    content: Any
    level: int
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class HelixFS:
    """
    Virtual filesystem using dimensional model.
    
    Instead of:
        /home/user/documents/project/file.txt (5 traversals)
    
    Use:
        helix:6.home/5.documents/4.project/3.file.txt (4 level invocations)
    
    Key insight: Path depth = dimensional level, so navigation is O(levels) not O(depth).
    
    Usage:
        fs = HelixFS()
        fs.write('6.data/5.users/4.alice.json', {'name': 'Alice'})
        data = fs.read('6.data/5.users/4.alice.json')
    """
    
    def __init__(self):
        self.files: Dict[str, HelixFile] = {}
        self.cache = HelixCache()
        self.logger = HelixLogger(min_level=3)
    
    # -------------------------------------------------------------------------
    # Basic Operations
    # -------------------------------------------------------------------------
    
    def write(self, path: str, content: Any, metadata: Dict = None) -> HelixFile:
        """Write content to a path"""
        helix_path = HelixPath.parse(path)
        
        file = HelixFile(
            path=helix_path,
            content=content,
            level=helix_path.target_level,
            metadata=metadata or {}
        )
        
        self.files[str(helix_path)] = file
        self.cache.set(path, content, helix_path.target_level)
        self.logger.width(f"Wrote to {path}")
        
        return file
    
    def read(self, path: str) -> Optional[Any]:
        """Read content from a path"""
        # Check cache first
        cached = self.cache.get(path)
        if cached is not None:
            return cached
        
        helix_path = HelixPath.parse(path)
        file = self.files.get(str(helix_path))
        
        if file:
            self.cache.set(path, file.content, file.level)
            return file.content
        
        return None
    
    def exists(self, path: str) -> bool:
        """Check if path exists"""
        helix_path = HelixPath.parse(path)
        return str(helix_path) in self.files
    
    def delete(self, path: str) -> bool:
        """Delete a path"""
        helix_path = HelixPath.parse(path)
        key = str(helix_path)
        
        if key in self.files:
            level = self.files[key].level
            del self.files[key]
            self.cache.invalidate_level(level)
            self.logger.width(f"Deleted {path}")
            return True
        return False
    
    # -------------------------------------------------------------------------
    # Directory-like Operations
    # -------------------------------------------------------------------------
    
    def list_at_level(self, level: int) -> List[HelixFile]:
        """List all files at a specific level"""
        return [f for f in self.files.values() if f.level == level]
    
    def list_children(self, path: str) -> List[HelixFile]:
        """List children of a path (one level below)"""
        helix_path = HelixPath.parse(path)
        parent_str = str(helix_path)
        target_level = helix_path.target_level - 1
        
        children = []
        for key, file in self.files.items():
            if key.startswith(parent_str + '/') and file.level == target_level:
                children.append(file)
        
        return children
    
    def walk(self, start_level: int = 6, end_level: int = 0) -> Iterator[tuple[int, List[HelixFile]]]:
        """Walk through levels, yielding files at each level"""
        for level in range(start_level, end_level - 1, -1):
            files = self.list_at_level(level)
            if files:
                yield level, files
    
    # -------------------------------------------------------------------------
    # Dimensional Operations
    # -------------------------------------------------------------------------
    
    def invoke(self, level: int) -> List[HelixFile]:
        """Invoke a level, returning all files"""
        return self.list_at_level(level)
    
    def promote(self, path: str, new_level: int) -> bool:
        """Move a file to a higher level"""
        helix_path = HelixPath.parse(path)
        key = str(helix_path)
        
        if key not in self.files:
            return False
        
        file = self.files[key]
        if new_level <= file.level:
            return False
        
        file.level = new_level
        return True
    
    # -------------------------------------------------------------------------
    # Persistence
    # -------------------------------------------------------------------------
    
    def to_json(self) -> str:
        """Export filesystem to JSON"""
        return json.dumps({
            'files': {
                path: {
                    'path': str(f.path),
                    'content': f.content,
                    'level': f.level,
                    'created_at': f.created_at.isoformat(),
                    'modified_at': f.modified_at.isoformat(),
                    'metadata': f.metadata
                }
                for path, f in self.files.items()
            }
        }, indent=2)


# =============================================================================
# HELIX STORE - Key-value store with dimensional organization
# =============================================================================

class HelixStore(Generic[T]):
    """
    Key-value store organized by dimensional levels.
    
    Keys are organized by level, enabling:
        - O(1) lookup by key
        - O(1) lookup by level
        - Level-based invalidation
        - Dimensional iteration
    
    Usage:
        store = HelixStore[dict]()
        store.set('user:alice', {'name': 'Alice'}, level=4)
        store.set('config:app', {'debug': True}, level=6)
        configs = store.get_level(6)  # All level-6 items
    """
    
    def __init__(self):
        self._data: Dict[str, tuple[T, int]] = {}  # key -> (value, level)
        self._by_level: Dict[int, Set[str]] = {i: set() for i in range(7)}
        self.cache = HelixCache()
    
    def set(self, key: str, value: T, level: int = 3) -> None:
        """Set a value at a level"""
        if not 0 <= level <= 6:
            raise ValueError(f"Level must be 0-6, got {level}")
        
        # Remove from old level if exists
        if key in self._data:
            old_level = self._data[key][1]
            self._by_level[old_level].discard(key)
        
        self._data[key] = (value, level)
        self._by_level[level].add(key)
        self.cache.set(key, value, level)
    
    def get(self, key: str) -> Optional[T]:
        """Get a value by key"""
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        
        if key in self._data:
            value, level = self._data[key]
            self.cache.set(key, value, level)
            return value
        return None
    
    def delete(self, key: str) -> bool:
        """Delete a key"""
        if key in self._data:
            _, level = self._data[key]
            del self._data[key]
            self._by_level[level].discard(key)
            return True
        return False
    
    def get_level(self, level: int) -> Dict[str, T]:
        """Get all values at a level"""
        result = {}
        for key in self._by_level.get(level, set()):
            if key in self._data:
                result[key] = self._data[key][0]
        return result
    
    def keys_at_level(self, level: int) -> Set[str]:
        """Get all keys at a level"""
        return self._by_level.get(level, set()).copy()
    
    def invalidate_level(self, level: int) -> int:
        """Invalidate all entries at level and below"""
        count = 0
        for l in range(level + 1):
            for key in list(self._by_level[l]):
                if self.delete(key):
                    count += 1
        return count
    
    def __len__(self) -> int:
        return len(self._data)
    
    def __contains__(self, key: str) -> bool:
        return key in self._data


# =============================================================================
# HELIX GRAPH - Graph structure using helix navigation
# =============================================================================

@dataclass
class HelixNode:
    """A node in the helix graph"""
    id: str
    level: int
    data: Any
    edges: Set[str] = field(default_factory=set)


class HelixGraph:
    """
    Graph structure using helix navigation.
    
    Nodes exist at dimensional levels.
    Edges connect nodes across the helix.
    Traversal is level-based, not node-by-node.
    
    Usage:
        graph = HelixGraph()
        graph.add_node('system', level=6, data={'name': 'System'})
        graph.add_node('module_a', level=5, data={'name': 'Module A'})
        graph.add_edge('system', 'module_a')
        modules = graph.children('system')  # Level-5 children
    """
    
    def __init__(self):
        self.nodes: Dict[str, HelixNode] = {}
        self._by_level: Dict[int, Set[str]] = {i: set() for i in range(7)}
    
    # -------------------------------------------------------------------------
    # Node Operations
    # -------------------------------------------------------------------------
    
    def add_node(self, id: str, level: int, data: Any = None) -> HelixNode:
        """Add a node at a level"""
        node = HelixNode(id=id, level=level, data=data)
        self.nodes[id] = node
        self._by_level[level].add(id)
        return node
    
    def get_node(self, id: str) -> Optional[HelixNode]:
        """Get a node by ID"""
        return self.nodes.get(id)
    
    def remove_node(self, id: str) -> bool:
        """Remove a node"""
        node = self.nodes.get(id)
        if node:
            self._by_level[node.level].discard(id)
            del self.nodes[id]
            
            # Remove edges to this node
            for other in self.nodes.values():
                other.edges.discard(id)
            
            return True
        return False
    
    # -------------------------------------------------------------------------
    # Edge Operations
    # -------------------------------------------------------------------------
    
    def add_edge(self, from_id: str, to_id: str) -> bool:
        """Add an edge between nodes"""
        if from_id in self.nodes and to_id in self.nodes:
            self.nodes[from_id].edges.add(to_id)
            return True
        return False
    
    def remove_edge(self, from_id: str, to_id: str) -> bool:
        """Remove an edge"""
        if from_id in self.nodes:
            self.nodes[from_id].edges.discard(to_id)
            return True
        return False
    
    # -------------------------------------------------------------------------
    # Traversal
    # -------------------------------------------------------------------------
    
    def nodes_at_level(self, level: int) -> List[HelixNode]:
        """Get all nodes at a level"""
        return [self.nodes[id] for id in self._by_level.get(level, set())]
    
    def children(self, node_id: str) -> List[HelixNode]:
        """Get child nodes (connected nodes at lower level)"""
        node = self.nodes.get(node_id)
        if not node:
            return []
        
        children = []
        for edge_id in node.edges:
            edge_node = self.nodes.get(edge_id)
            if edge_node and edge_node.level < node.level:
                children.append(edge_node)
        return children
    
    def parents(self, node_id: str) -> List[HelixNode]:
        """Get parent nodes (connected nodes at higher level)"""
        node = self.nodes.get(node_id)
        if not node:
            return []
        
        parents = []
        for other_id, other in self.nodes.items():
            if node_id in other.edges and other.level > node.level:
                parents.append(other)
        return parents
    
    def siblings(self, node_id: str) -> List[HelixNode]:
        """Get sibling nodes (same level, same parents)"""
        node = self.nodes.get(node_id)
        if not node:
            return []
        
        parent_ids = {p.id for p in self.parents(node_id)}
        siblings = []
        
        for other in self.nodes_at_level(node.level):
            if other.id != node_id:
                other_parent_ids = {p.id for p in self.parents(other.id)}
                if parent_ids & other_parent_ids:
                    siblings.append(other)
        
        return siblings
    
    def walk_down(self, start_id: str) -> Iterator[tuple[int, List[HelixNode]]]:
        """Walk down from a node, yielding level and nodes"""
        visited = set()
        current = [self.nodes[start_id]] if start_id in self.nodes else []
        
        while current:
            level = current[0].level if current else -1
            yield level, current
            
            next_level = []
            for node in current:
                visited.add(node.id)
                for child in self.children(node.id):
                    if child.id not in visited:
                        next_level.append(child)
            
            current = next_level
    
    # -------------------------------------------------------------------------
    # Analysis
    # -------------------------------------------------------------------------
    
    def level_counts(self) -> Dict[int, int]:
        """Count nodes at each level"""
        return {level: len(ids) for level, ids in self._by_level.items()}
    
    def edge_count(self) -> int:
        """Total number of edges"""
        return sum(len(node.edges) for node in self.nodes.values())


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Database
    'HelixDB',
    'HelixDBQuery',
    'HelixRecord',
    
    # Filesystem
    'HelixFS',
    'HelixFile',
    
    # Store
    'HelixStore',
    
    # Graph
    'HelixGraph',
    'HelixNode',
]
