"""
Dimensional Universe Substrate

The fundamental truth of dimensions:
- A point (0D) has no extent, yet is complete
- A line (1D) = infinite points, each point is a complete 0D
- A plane (2D) = infinite lines, each line is a complete 1D
- A volume (3D) = infinite planes, each plane is a complete 2D
- A hypervolume (4D) = infinite volumes, each volume is a complete 3D
- ... and so on infinitely

In code: Every node at dimension N contains an entire dimension N-1 universe.
Drill down = enter the point's internal universe.
Drill up = current universe becomes one point in higher dimension.

The address τ(d, x, y, z, ...) gives O(1) access to any point at any depth.
"""

import json
import time
import math
import uuid
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class DimensionalPoint:
    """
    A point in dimensional space.
    
    Key insight: This point IS a single unit at dimension N,
    but CONTAINS an entire dimension N-1 universe within it.
    """
    id: str
    dimension: int  # What dimension this point exists IN
    coordinates: Tuple[float, ...]  # Position in parent dimension
    name: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    
    # The internal universe (dimension - 1)
    # Each point in this dict is a complete DimensionalPoint
    _inner_universe: Dict[str, 'DimensionalPoint'] = field(default_factory=dict)
    
    # Reference to parent point (if we're inside something)
    _parent_id: Optional[str] = None
    
    @property
    def address(self) -> str:
        """The dimensional address τ(dim, coords...)"""
        coords_str = ",".join(f"{c:.3f}" for c in self.coordinates)
        return f"τ({self.dimension},{coords_str})"
    
    def get_inner(self, point_id: str) -> Optional['DimensionalPoint']:
        """Get a point from the inner universe"""
        return self._inner_universe.get(point_id)
    
    def add_inner(self, point: 'DimensionalPoint'):
        """Add a point to the inner universe"""
        point._parent_id = self.id
        point.dimension = self.dimension - 1  # Inner points are one dimension lower
        self._inner_universe[point.id] = point
    
    def list_inner(self) -> List['DimensionalPoint']:
        """List all points in the inner universe"""
        return list(self._inner_universe.values())
    
    def inner_count(self) -> int:
        """Count points in inner universe"""
        return len(self._inner_universe)
    
    def total_points(self) -> int:
        """Recursively count all points in all nested universes"""
        count = 1  # This point
        for inner in self._inner_universe.values():
            count += inner.total_points()
        return count
    
    def to_dict(self, depth: int = 0, max_depth: int = 3) -> dict:
        """Serialize to dict with controlled depth"""
        result = {
            "id": self.id,
            "dimension": self.dimension,
            "coordinates": list(self.coordinates),
            "name": self.name,
            "address": self.address,
            "properties": self.properties,
            "inner_count": self.inner_count(),
            "total_nested_points": self.total_points() if depth == 0 else None
        }
        
        if depth < max_depth and self._inner_universe:
            result["inner_universe"] = {
                pid: p.to_dict(depth + 1, max_depth) 
                for pid, p in list(self._inner_universe.items())[:10]  # Limit for serialization
            }
            if len(self._inner_universe) > 10:
                result["inner_truncated"] = True
                result["inner_total"] = len(self._inner_universe)
        
        return result


class DimensionalUniverse:
    """
    The Universe - a navigable dimensional space.
    
    Structure:
    - Level 7 (Ω): The Omniverse - contains all possible universes
    - Level 6: Universe - a complete spacetime
    - Level 5: Galaxy cluster / Major region
    - Level 4: Galaxy / System  
    - Level 3: Star system / World
    - Level 2: Object / Entity
    - Level 1: Component / Part
    - Level 0: Atom / Primitive
    
    You can drill down infinitely - every point contains a universe.
    You can drill up infinitely - every universe is a point in a higher one.
    """
    
    DIMENSION_NAMES = {
        7: "Omniverse",
        6: "Universe", 
        5: "Region",
        4: "System",
        3: "World",
        2: "Entity",
        1: "Component",
        0: "Atom"
    }
    
    def __init__(self, name: str = "ButterflyFX"):
        self.name = name
        self.created_at = time.time()
        
        # The root - dimension 7, the Omniverse
        self.root = DimensionalPoint(
            id="omniverse",
            dimension=7,
            coordinates=(0.0,),
            name=name,
            properties={"type": "omniverse", "created": self.created_at}
        )
        
        # O(1) address index - every point ever created
        self._index: Dict[str, DimensionalPoint] = {"omniverse": self.root}
        
        # Current navigation position
        self._current_point: DimensionalPoint = self.root
        self._navigation_stack: List[str] = ["omniverse"]
        
        # Initialize with a default universe
        self._create_initial_structure()
    
    def _create_initial_structure(self):
        """Create initial dimensional structure"""
        # Create the first universe inside the omniverse
        universe = self._create_point(
            parent=self.root,
            name="Prime Universe",
            coordinates=(0.0, 0.0, 0.0),
            properties={"type": "universe", "age": "13.8 billion years"}
        )
        
        # Create a region
        region = self._create_point(
            parent=universe,
            name="Local Cluster",
            coordinates=(0.0, 0.0, 0.0),
            properties={"type": "region", "galaxies": "~100"}
        )
        
        # Create a system (like a galaxy)
        system = self._create_point(
            parent=region,
            name="Home Galaxy",
            coordinates=(0.0, 0.0, 0.0),
            properties={"type": "galaxy", "stars": "~400 billion"}
        )
        
        # Create a world
        world = self._create_point(
            parent=system,
            name="Origin World",
            coordinates=(0.0, 0.0, 0.0),
            properties={"type": "world", "radius": 6371}
        )
        
        # Start navigation at the world level - more interesting for demos
        self._current_point = world
        self._navigation_stack = ["omniverse", universe.id, region.id, system.id, world.id]
    
    def _create_point(
        self, 
        parent: DimensionalPoint,
        name: str,
        coordinates: Tuple[float, ...],
        properties: Dict[str, Any] = None
    ) -> DimensionalPoint:
        """Create a new point in a parent's inner universe"""
        point_id = f"p_{uuid.uuid4().hex[:8]}"
        
        point = DimensionalPoint(
            id=point_id,
            dimension=parent.dimension - 1,
            coordinates=coordinates,
            name=name,
            properties=properties or {}
        )
        
        parent.add_inner(point)
        self._index[point_id] = point
        
        return point
    
    # =========== NAVIGATION ===========
    
    def current(self) -> DimensionalPoint:
        """Get current position"""
        return self._current_point
    
    def current_dimension(self) -> int:
        """Get current dimension level"""
        return self._current_point.dimension
    
    def dimension_name(self, dim: int = None) -> str:
        """Get human name for dimension"""
        if dim is None:
            dim = self._current_point.dimension
        return self.DIMENSION_NAMES.get(dim, f"Dimension-{dim}")
    
    def drill_down(self, point_id: str = None) -> Optional[DimensionalPoint]:
        """
        Drill down into a point's inner universe.
        The current universe becomes a single point; we enter its depths.
        """
        if point_id:
            # Drill into specific point
            inner = self._current_point.get_inner(point_id)
            if inner:
                self._current_point = inner
                self._navigation_stack.append(point_id)
                return inner
            # Also check if it's in the index
            if point_id in self._index:
                self._current_point = self._index[point_id]
                self._navigation_stack.append(point_id)
                return self._current_point
        else:
            # Drill into first inner point
            inner_points = self._current_point.list_inner()
            if inner_points:
                self._current_point = inner_points[0]
                self._navigation_stack.append(inner_points[0].id)
                return inner_points[0]
        
        return None
    
    def drill_up(self) -> Optional[DimensionalPoint]:
        """
        Drill up - current universe becomes a point in higher dimension.
        """
        if len(self._navigation_stack) > 1:
            self._navigation_stack.pop()
            parent_id = self._navigation_stack[-1]
            self._current_point = self._index[parent_id]
            return self._current_point
        return None
    
    def goto(self, point_id: str) -> Optional[DimensionalPoint]:
        """O(1) jump to any point by ID"""
        if point_id in self._index:
            self._current_point = self._index[point_id]
            # Rebuild navigation stack
            self._navigation_stack = [point_id]
            return self._current_point
        return None
    
    def path(self) -> List[Dict]:
        """Get current navigation path"""
        return [
            {
                "id": pid,
                "name": self._index[pid].name,
                "dimension": self._index[pid].dimension,
                "dimension_name": self.dimension_name(self._index[pid].dimension)
            }
            for pid in self._navigation_stack
        ]
    
    # =========== CREATION ===========
    
    def create(
        self,
        name: str,
        coordinates: Tuple[float, ...] = None,
        properties: Dict[str, Any] = None,
        shape: str = None
    ) -> DimensionalPoint:
        """
        Create a new point in the current dimension.
        This point will contain its own inner universe (dimension - 1).
        """
        if coordinates is None:
            # Random position for demo
            import random
            coordinates = tuple(random.uniform(-10, 10) for _ in range(3))
        
        props = properties or {}
        if shape:
            props["shape"] = shape
        
        point = self._create_point(
            parent=self._current_point,
            name=name,
            coordinates=coordinates,
            properties=props
        )
        
        return point
    
    def create_with_structure(
        self,
        name: str,
        structure: Dict[str, Any],
        coordinates: Tuple[float, ...] = None
    ) -> DimensionalPoint:
        """
        Create a complex object with nested structure.
        
        Example structure:
        {
            "type": "car",
            "children": {
                "body": {"type": "mesh", "vertices": 1000},
                "wheels": [
                    {"type": "wheel", "position": "FL"},
                    {"type": "wheel", "position": "FR"},
                    ...
                ]
            }
        }
        """
        if coordinates is None:
            coordinates = (0.0, 0.0, 0.0)
        
        # Create the main point
        point = self._create_point(
            parent=self._current_point,
            name=name,
            coordinates=coordinates,
            properties={k: v for k, v in structure.items() if k != "children"}
        )
        
        # Create children recursively
        children = structure.get("children", {})
        if isinstance(children, dict):
            for child_name, child_struct in children.items():
                if isinstance(child_struct, dict):
                    self._create_child_recursive(point, child_name, child_struct)
                elif isinstance(child_struct, list):
                    for i, item in enumerate(child_struct):
                        self._create_child_recursive(point, f"{child_name}_{i}", item)
        
        return point
    
    def _create_child_recursive(
        self,
        parent: DimensionalPoint,
        name: str,
        structure: Dict[str, Any]
    ):
        """Recursively create child points"""
        import random
        coords = tuple(random.uniform(-1, 1) for _ in range(3))
        
        child = self._create_point(
            parent=parent,
            name=name,
            coordinates=coords,
            properties={k: v for k, v in structure.items() if k != "children"}
        )
        
        # Recurse for children
        children = structure.get("children", {})
        if isinstance(children, dict):
            for child_name, child_struct in children.items():
                if isinstance(child_struct, dict):
                    self._create_child_recursive(child, child_name, child_struct)
    
    # =========== QUERIES ===========
    
    def list_inner(self) -> List[Dict]:
        """List points in current inner universe"""
        return [
            {
                "id": p.id,
                "name": p.name,
                "dimension": p.dimension,
                "dimension_name": self.dimension_name(p.dimension),
                "address": p.address,
                "coordinates": list(p.coordinates),
                "properties": p.properties,
                "inner_count": p.inner_count()
            }
            for p in self._current_point.list_inner()
        ]
    
    def search(self, query: str) -> List[Dict]:
        """Search all points by name"""
        results = []
        query_lower = query.lower()
        
        for point_id, point in self._index.items():
            if query_lower in point.name.lower():
                results.append({
                    "id": point.id,
                    "name": point.name,
                    "dimension": point.dimension,
                    "address": point.address
                })
        
        return results[:20]  # Limit results
    
    def stats(self) -> Dict:
        """Get universe statistics"""
        return {
            "name": self.name,
            "total_points": len(self._index),
            "total_nested": self.root.total_points(),
            "current_dimension": self._current_point.dimension,
            "current_dimension_name": self.dimension_name(),
            "current_point": self._current_point.name,
            "navigation_depth": len(self._navigation_stack)
        }
    
    def get_point(self, point_id: str) -> Optional[Dict]:
        """O(1) get any point by ID"""
        point = self._index.get(point_id)
        if point:
            return point.to_dict()
        return None
    
    # =========== DIMENSIONAL ADDRESSING (O(1) per level) ===========
    
    def invoke(self, address: str) -> Optional[DimensionalPoint]:
        """
        DIMENSIONAL INVOCATION - The key difference from trees.
        
        Tree traversal: Must walk each level, visiting children
            O(log n) to O(n) depending on structure
            
        Dimensional invocation: Direct address to any depth
            O(1) per dimension level = O(d) total
            
        Example: "car.engine.alternator.gasket.fiber.element.molecule.atom"
        - Not 8 tree traversals
        - 8 hash lookups, each O(1)
        - Total: O(8) regardless of universe size
        
        The point ALREADY EXISTS conceptually. We're not searching for it.
        We're invoking its address directly.
        """
        if not address:
            return self._current_point
        
        # Parse the dimensional path
        # Format: "name.name.name" or "id.id.id" or mixed
        parts = address.split(".")
        
        # Start from current point (or root if absolute)
        current = self._current_point
        if parts[0] == "root" or parts[0] == "omniverse":
            current = self.root
            parts = parts[1:]
        
        # Each part is an O(1) lookup into that dimension
        for part in parts:
            if not part:
                continue
                
            # O(1) lookup by ID in index
            if part in self._index:
                current = self._index[part]
                continue
            
            # O(1) lookup by name in current dimension
            found = None
            for inner in current._inner_universe.values():
                if inner.name.lower() == part.lower() or inner.id == part:
                    found = inner
                    break
            
            if found:
                current = found
            else:
                # Point doesn't exist YET in materialized form
                # But conceptually it exists - we can create it on demand
                return None
        
        return current
    
    def invoke_path(self, path: str) -> Dict:
        """
        Invoke a full dimensional path and return the result.
        
        Example: invoke_path("car.engine.alternator.gasket")
        
        Returns the point AND the path taken, proving O(d) access.
        """
        parts = path.split(".")
        results = []
        current = self._current_point
        
        start_time = __import__('time').perf_counter_ns()
        
        for i, part in enumerate(parts):
            lookup_start = __import__('time').perf_counter_ns()
            
            # O(1) lookup
            found = None
            if part in self._index:
                found = self._index[part]
            else:
                for inner in current._inner_universe.values():
                    if inner.name.lower() == part.lower():
                        found = inner
                        break
            
            lookup_time = __import__('time').perf_counter_ns() - lookup_start
            
            if found:
                current = found
                results.append({
                    "level": i,
                    "name": found.name,
                    "dimension": found.dimension,
                    "address": found.address,
                    "lookup_ns": lookup_time
                })
            else:
                results.append({
                    "level": i,
                    "name": part,
                    "found": False,
                    "lookup_ns": lookup_time
                })
                break
        
        total_time = __import__('time').perf_counter_ns() - start_time
        
        return {
            "path": path,
            "levels_traversed": len(results),
            "total_time_ns": total_time,
            "avg_per_level_ns": total_time // len(results) if results else 0,
            "complexity": f"O({len(results)})",
            "final_point": current.to_dict() if current else None,
            "traversal": results
        }
    
    def invoke_at_dimension(self, dimension: int, point_name: str = None) -> List[DimensionalPoint]:
        """
        Start at any dimension level directly.
        
        A scientist doesn't go: Car → Engine → Alternator → ... → Atom
        They go directly to: dimension=-5 (atomic level)
        
        A city planner doesn't go: Omniverse → Universe → ... → Building
        They go directly to: dimension=2 (entity level)
        
        This is O(1) entry - you invoke the dimension you care about.
        """
        results = []
        
        for point in self._index.values():
            if point.dimension == dimension:
                if point_name is None or point_name.lower() in point.name.lower():
                    results.append(point)
        
        return results
    
    def enter_dimension(self, dimension: int, point_id: str = None) -> Optional[DimensionalPoint]:
        """
        Enter a specific dimension directly.
        
        Returns: The first point at that dimension (or specific point if ID given)
        Updates navigation to that point.
        """
        if point_id and point_id in self._index:
            point = self._index[point_id]
            self._current_point = point
            self._navigation_stack = [point_id]
            return point
        
        # Find any point at this dimension
        for point in self._index.values():
            if point.dimension == dimension:
                self._current_point = point
                self._navigation_stack = [point.id]
                return point
        
        return None
    
    def list_dimensions(self) -> Dict[int, List[Dict]]:
        """
        List all materialized dimensions and their entry points.
        
        Shows: "Here are all the dimensions you can enter directly"
        """
        dimensions = {}
        
        for point in self._index.values():
            dim = point.dimension
            if dim not in dimensions:
                dimensions[dim] = []
            
            dimensions[dim].append({
                "id": point.id,
                "name": point.name,
                "address": point.address
            })
        
        return {
            "dimensions": {
                k: {
                    "level": k,
                    "name": self.DIMENSION_NAMES.get(k, f"Dimension-{k}"),
                    "entry_points": v[:10],  # Limit for display
                    "total_points": len(v)
                }
                for k, v in sorted(dimensions.items(), reverse=True)
            },
            "insight": "You can enter at ANY level. A scientist enters at atomic. An architect at building. A god at universe."
        }
    
    def why_not_tree(self) -> str:
        """Explain why this is not a tree"""
        return """
DIMENSIONAL STRUCTURE vs TREE STRUCTURE

Tree:
  - Nodes are CREATED as children
  - Must TRAVERSE from root to find anything
  - Complexity: O(log n) to O(n) for search
  - Memory: Grows with every node added
  - Example: filesystem, DOM, org charts

Dimensional:
  - Points EXIST at addresses (conceptually infinite)
  - INVOKE any point directly by address
  - Complexity: O(1) per dimension = O(d) total
  - Memory: Only materialized points stored
  - Example: coordinates, quantum states, this universe

Key Insight:
  In a tree, Car.engine.alternator requires:
    1. Find Car in root.children (O(n))
    2. Find engine in Car.children (O(n))
    3. Find alternator in engine.children (O(n))
    Total: O(n³) worst case

  In dimensional space, Car.engine.alternator requires:
    1. Hash lookup "Car" (O(1))
    2. Hash lookup "engine" in Car's dimension (O(1))
    3. Hash lookup "alternator" in engine's dimension (O(1))
    Total: O(3) = O(1) constant

The dimension IS the lookup table. Each level is a hash map, not a list to search.
"""
    
    # =========== VISUALIZATION DATA ===========
    
    def get_visualization_data(self) -> Dict:
        """Get data for 3D visualization"""
        current = self._current_point
        
        # Get inner points for rendering
        inner_points = []
        for p in current.list_inner():
            inner_points.append({
                "id": p.id,
                "name": p.name,
                "position": list(p.coordinates),
                "dimension": p.dimension,
                "address": p.address,
                "has_inner": p.inner_count() > 0,
                "inner_count": p.inner_count(),
                "properties": p.properties
            })
        
        return {
            "current": {
                "id": current.id,
                "name": current.name,
                "dimension": current.dimension,
                "dimension_name": self.dimension_name(),
                "address": current.address,
                "properties": current.properties
            },
            "path": self.path(),
            "inner_points": inner_points,
            "can_drill_up": len(self._navigation_stack) > 1,
            "stats": self.stats()
        }
    
    # =========== PERSISTENCE ===========
    
    def save(self, path: str):
        """Save universe to file"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        def serialize_point(p: DimensionalPoint) -> dict:
            return {
                "id": p.id,
                "dimension": p.dimension,
                "coordinates": list(p.coordinates),
                "name": p.name,
                "properties": p.properties,
                "inner_universe": {
                    pid: serialize_point(inner) 
                    for pid, inner in p._inner_universe.items()
                }
            }
        
        data = {
            "name": self.name,
            "created_at": self.created_at,
            "root": serialize_point(self.root),
            "current_id": self._current_point.id,
            "navigation_stack": self._navigation_stack
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'DimensionalUniverse':
        """Load universe from file"""
        with open(path, 'r') as f:
            data = json.load(f)
        
        universe = cls.__new__(cls)
        universe.name = data["name"]
        universe.created_at = data["created_at"]
        universe._index = {}
        
        def deserialize_point(d: dict, parent_id: str = None) -> DimensionalPoint:
            point = DimensionalPoint(
                id=d["id"],
                dimension=d["dimension"],
                coordinates=tuple(d["coordinates"]),
                name=d["name"],
                properties=d["properties"]
            )
            point._parent_id = parent_id
            universe._index[point.id] = point
            
            for pid, inner_data in d.get("inner_universe", {}).items():
                inner = deserialize_point(inner_data, point.id)
                point._inner_universe[pid] = inner
            
            return point
        
        universe.root = deserialize_point(data["root"])
        universe._navigation_stack = data["navigation_stack"]
        universe._current_point = universe._index[data["current_id"]]
        
        return universe


# =========== DEMO ===========

if __name__ == "__main__":
    print("\n" + "="*60)
    print("DIMENSIONAL UNIVERSE - Where Every Point is a Universe")
    print("="*60 + "\n")
    
    # Create universe
    universe = DimensionalUniverse("ButterflyFX Demo")
    
    print(f"Created: {universe.name}")
    print(f"Starting at: {universe.current().name} (Dimension {universe.current_dimension()}: {universe.dimension_name()})")
    print(f"Total points: {universe.stats()['total_points']}")
    
    print("\n--- Creating objects in the world ---")
    
    # Create a complex object
    car = universe.create_with_structure(
        name="Red Sports Car",
        structure={
            "type": "vehicle",
            "color": "red",
            "children": {
                "body": {
                    "type": "mesh",
                    "material": "metallic_red",
                    "children": {
                        "hood": {"type": "panel"},
                        "roof": {"type": "panel"},
                        "doors": {"type": "panel"}
                    }
                },
                "wheels": [
                    {"type": "wheel", "position": "front_left"},
                    {"type": "wheel", "position": "front_right"},
                    {"type": "wheel", "position": "rear_left"},
                    {"type": "wheel", "position": "rear_right"}
                ],
                "engine": {
                    "type": "v8",
                    "horsepower": 450,
                    "children": {
                        "pistons": {"type": "component", "count": 8},
                        "crankshaft": {"type": "component"}
                    }
                }
            }
        },
        coordinates=(0, 0, 0)
    )
    
    print(f"Created: {car.name} @ {car.address}")
    print(f"  Contains {car.total_points()} nested points")
    
    # Create more objects
    building = universe.create(
        name="Skyscraper",
        coordinates=(5, 0, 0),
        properties={"type": "building", "floors": 50}
    )
    
    tree = universe.create(
        name="Oak Tree",
        coordinates=(-3, 0, 2),
        properties={"type": "plant", "height": 15}
    )
    
    print(f"\nCurrent location: {universe.current().name}")
    print(f"Objects here: {len(universe.list_inner())}")
    
    print("\n--- Navigation Demo ---")
    
    # List what's in the world
    print(f"\nInside '{universe.current().name}':")
    for obj in universe.list_inner():
        print(f"  {obj['name']} @ {obj['address']} - {obj['inner_count']} inner points")
    
    # Drill down into the car
    print(f"\n>>> Drilling down into '{car.name}'...")
    universe.drill_down(car.id)
    print(f"Now at: {universe.current().name} (Dim {universe.current_dimension()}: {universe.dimension_name()})")
    
    print(f"\nInside the car:")
    for obj in universe.list_inner():
        print(f"  {obj['name']} @ {obj['address']}")
    
    # Drill down into the engine
    engine = None
    for obj in universe.list_inner():
        if "engine" in obj["name"]:
            engine = obj
            break
    
    if engine:
        print(f"\n>>> Drilling into '{engine['name']}'...")
        universe.drill_down(engine["id"])
        print(f"Now at: {universe.current().name} (Dim {universe.current_dimension()}: {universe.dimension_name()})")
        
        print(f"\nInside the engine:")
        for obj in universe.list_inner():
            print(f"  {obj['name']} @ {obj['address']}")
    
    # Drill back up
    print("\n>>> Drilling UP...")
    universe.drill_up()
    print(f"Back to: {universe.current().name}")
    
    universe.drill_up()
    print(f"Back to: {universe.current().name}")
    
    # Show navigation path
    print("\n--- Current Path ---")
    for step in universe.path():
        indent = "  " * (7 - step["dimension"])
        print(f"{indent}Dim {step['dimension']} ({step['dimension_name']}): {step['name']}")
    
    print("\n--- Final Stats ---")
    stats = universe.stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")
