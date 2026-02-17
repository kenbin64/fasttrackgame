"""
ButterflyFX Primitives - Fundamental Building Blocks

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

This mathematical kernel belongs to all humanity.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

Layer 1: Primitives
    The atomic operations and types that everything else builds on.
    
Primitives:
    - HelixState: Immutable (spiral, level) tuple
    - Token: Entity with location, signature, lazy payload
    - HelixKernel: The state machine (4 operations)
    - ManifoldSubstrate: Token storage with materialization
    - DimensionalType: Type wrapper for dimensional data
    - HelixContext: Context manager for helix operations

GENERATIVE PRINCIPLE:
    Data can be derived from manifold geometry instead of stored.
    The mathematical surface contains all possible values.
"""

from .kernel import HelixKernel, HelixState, LEVEL_NAMES, LEVEL_ICONS
from .substrate import ManifoldSubstrate, Token, PayloadSource, GeometricProperty

from dataclasses import dataclass, field
from typing import Any, Callable, Set, Optional, TypeVar, Generic, Iterator, Union, List, Tuple, Dict
from contextlib import contextmanager
import uuid

T = TypeVar('T')


# =============================================================================
# DIMENSIONAL TYPE - Enhanced with Generative Capabilities
# =============================================================================

@dataclass(frozen=True)
class DimensionalType(Generic[T]):
    """
    A value with dimensional metadata.
    
    Wraps any Python value with:
        - The helix level it exists at
        - Optional spiral affinity
        - Lazy evaluation support
    
    GENERATIVE ENHANCEMENT:
        Can derive value from manifold geometry instead of storing it.
        Use DimensionalType.from_geometry() for values pulled from mathematics.
    """
    value: T
    level: int
    spiral: int = 0
    _is_generative: bool = field(default=False, repr=False, compare=False)
    _geometric_property: Optional[str] = field(default=None, repr=False, compare=False)
    
    def __post_init__(self):
        if not 0 <= self.level <= 6:
            raise ValueError(f"Level must be 0-6, got {self.level}")
    
    @classmethod
    def from_geometry(
        cls,
        spiral: int,
        level: int,
        geometric_property: str = 'sin'
    ) -> 'DimensionalType':
        """
        Create a DimensionalType that derives its value from manifold geometry.
        
        Instead of storing a value, pulls it from the mathematical surface.
        
        Args:
            spiral: Which spiral turn
            level: Which level (0-6)
            geometric_property: Which property to extract (sin, cos, slope, curvature, etc.)
        
        Example:
            d = DimensionalType.from_geometry(0, 3, 'sin')
            print(d.value)  # 1.0 (sin of angle at level 3 = π/2)
        """
        from .manifold import GenerativeManifold
        manifold = GenerativeManifold()
        point = manifold.at(spiral, level)
        value = getattr(point, geometric_property)
        
        # Use object.__setattr__ since dataclass is frozen
        obj = cls(value=value, level=level, spiral=spiral)
        object.__setattr__(obj, '_is_generative', True)
        object.__setattr__(obj, '_geometric_property', geometric_property)
        return obj
    
    @classmethod
    def sin(cls, spiral: int, level: int) -> 'DimensionalType[float]':
        """Create DimensionalType with sin value at position"""
        return cls.from_geometry(spiral, level, 'sin')
    
    @classmethod
    def cos(cls, spiral: int, level: int) -> 'DimensionalType[float]':
        """Create DimensionalType with cos value at position"""
        return cls.from_geometry(spiral, level, 'cos')
    
    @classmethod
    def slope(cls, spiral: int, level: int) -> 'DimensionalType[float]':
        """Create DimensionalType with slope at position"""
        return cls.from_geometry(spiral, level, 'slope')
    
    @classmethod
    def curvature(cls, spiral: int, level: int) -> 'DimensionalType[float]':
        """Create DimensionalType with curvature at position"""
        return cls.from_geometry(spiral, level, 'curvature')
    
    @classmethod
    def position(cls, spiral: int, level: int) -> 'DimensionalType[tuple]':
        """Create DimensionalType with (x,y,z) position"""
        return cls.from_geometry(spiral, level, 'position')
    
    @property
    def is_generative(self) -> bool:
        """True if value was derived from manifold geometry"""
        return self._is_generative
    
    @property
    def level_name(self) -> str:
        return LEVEL_NAMES[self.level]
    
    @property
    def level_icon(self) -> str:
        return LEVEL_ICONS[self.level]
    
    def promote(self, new_level: int) -> 'DimensionalType[T]':
        """Promote to a higher level"""
        if new_level < self.level:
            raise ValueError(f"Cannot demote from {self.level} to {new_level}")
        return DimensionalType(self.value, new_level, self.spiral)
    
    def to_spiral(self, new_spiral: int) -> 'DimensionalType[T]':
        """Move to a different spiral"""
        return DimensionalType(self.value, self.level, new_spiral)
    
    def rederive(self, new_property: str = None) -> 'DimensionalType':
        """
        Re-derive value from geometry (for generative types).
        Can optionally change the property being extracted.
        """
        if not self._is_generative and new_property is None:
            return self
        
        prop = new_property or self._geometric_property or 'sin'
        return DimensionalType.from_geometry(self.spiral, self.level, prop)
    
    def __repr__(self) -> str:
        if self._is_generative:
            return f"D{self.level}[{self._geometric_property}={self.value}]"
        return f"D{self.level}[{self.value}]"


# =============================================================================
# LAZY VALUE - Enhanced with Geometric Derivation
# =============================================================================

class LazyValue(Generic[T]):
    """
    A value that isn't computed until accessed.
    
    Implements the "potential until invoked" principle.
    
    GENERATIVE ENHANCEMENT:
        Can derive value from manifold geometry using from_geometry().
    """
    __slots__ = ('_factory', '_value', '_computed', '_is_geometric', '_geo_params')
    
    def __init__(self, factory: Callable[[], T]):
        self._factory = factory
        self._value: Optional[T] = None
        self._computed = False
        self._is_geometric = False
        self._geo_params = None
    
    @classmethod
    def from_geometry(
        cls,
        spiral: int,
        level: int,
        geometric_property: str = 'sin'
    ) -> 'LazyValue':
        """
        Create a LazyValue that derives its value from manifold geometry.
        
        Value is not computed until .value is accessed.
        """
        def factory():
            from .manifold import GenerativeManifold
            manifold = GenerativeManifold()
            point = manifold.at(spiral, level)
            return getattr(point, geometric_property)
        
        lazy = cls(factory)
        lazy._is_geometric = True
        lazy._geo_params = (spiral, level, geometric_property)
        return lazy
    
    @classmethod
    def from_function(cls, spiral: int, level: int, fn: Callable) -> 'LazyValue':
        """
        Create a LazyValue from a function of surface point.
        
        The function receives a SurfacePoint and returns any value.
        """
        def factory():
            from .manifold import GenerativeManifold
            manifold = GenerativeManifold()
            point = manifold.at(spiral, level)
            return fn(point)
        
        return cls(factory)
    
    @property
    def value(self) -> T:
        """Materialize the value (compute on first access)"""
        if not self._computed:
            self._value = self._factory()
            self._computed = True
        return self._value
    
    @property
    def is_materialized(self) -> bool:
        return self._computed
    
    @property
    def is_geometric(self) -> bool:
        return self._is_geometric
    
    def reset(self) -> None:
        """Return to potential state"""
        self._value = None
        self._computed = False
    
    def __repr__(self) -> str:
        if self._computed:
            return f"Lazy({self._value})"
        if self._is_geometric:
            return f"Lazy(<geometric:{self._geo_params}>)"
        return "Lazy(<potential>)"


# =============================================================================
# HELIX CONTEXT - Context manager for dimensional operations
# =============================================================================

class HelixContext:
    """
    Context manager for helix operations.
    
    Provides:
        - Automatic kernel + substrate setup
        - Token registration helpers (stored and generative)
        - Direct geometric derivation
        - State tracking
        - Cleanup on exit
    
    Usage:
        with HelixContext() as ctx:
            # Traditional: store data
            ctx.register("car", level=6, data={"name": "Tesla"})
            
            # Generative: derive from mathematics
            sin_val = ctx.derive(0, 3, 'sin')  # Pull sin from surface
            ctx.register_geometric("my_sin", 0, 3, 'sin')  # Geometric token
    """
    
    def __init__(self):
        self.kernel = HelixKernel()
        self.substrate = ManifoldSubstrate()
        self.kernel.set_substrate(self.substrate)
        self._token_map: dict[str, Token] = {}
    
    def __enter__(self) -> 'HelixContext':
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.kernel.collapse()
        return False
    
    # -------------------------------------------------------------------------
    # GENERATIVE ACCESS - Pull values from mathematics
    # -------------------------------------------------------------------------
    
    def derive(self, spiral: int, level: int, property: str = 'sin') -> Any:
        """
        Derive a value directly from manifold geometry.
        
        No storage - just pulls the value from mathematics.
        
        Args:
            spiral: Which spiral turn
            level: Which level (0-6)
            property: Geometric property (sin, cos, slope, curvature, etc.)
        
        Example:
            sin_val = ctx.derive(0, 3, 'sin')  # 1.0 (sin(π/2))
            slope = ctx.derive(1, 4, 'slope')
        """
        from .substrate import GeometricProperty
        prop = GeometricProperty(property)
        return self.substrate.derive_value(spiral, level, prop)
    
    def derive_matrix(
        self,
        spiral_range: tuple,
        level_range: tuple,
        property: str = 'sin'
    ) -> list:
        """Derive a 2D matrix of values from the manifold surface"""
        from .substrate import GeometricProperty
        prop = GeometricProperty(property)
        return self.substrate.derive_matrix(spiral_range, level_range, prop)
    
    def derive_wave(
        self,
        wave_type: str = 'sin',
        frequency: float = 1.0,
        amplitude: float = 1.0
    ) -> Callable[[float], float]:
        """Get a wave function derived from manifold geometry"""
        return self.substrate.derive_wave(wave_type, frequency, amplitude)
    
    def derive_spectrum(self, spiral_range: tuple, level_range: tuple) -> dict:
        """Extract frequency spectrum from a region"""
        return self.substrate.derive_spectrum(spiral_range, level_range)
    
    def derive_probability(self, spiral_range: tuple, level_range: tuple) -> Callable:
        """Generate a probability distribution from geometry"""
        return self.substrate.derive_probability(spiral_range, level_range)
    
    def derive_graph(self, spiral_range: tuple, level_range: tuple) -> dict:
        """Generate a graph structure from topology"""
        return self.substrate.derive_graph(spiral_range, level_range)
    
    @property
    def manifold(self):
        """Direct access to the underlying GenerativeManifold"""
        return self.substrate.manifold
    
    def surface_point(self, spiral: int, level: int):
        """Get a SurfacePoint with all geometric properties"""
        return self.substrate.manifold.at(spiral, level)
    
    # -------------------------------------------------------------------------
    # GENERATIVE TOKEN REGISTRATION
    # -------------------------------------------------------------------------
    
    def register_geometric(
        self,
        name: str,
        spiral: int,
        level: int,
        property: str = 'sin'
    ) -> Token:
        """
        Register a geometric token that derives value from manifold surface.
        
        NO DATA STORED - value computed from geometry when materialized.
        """
        from .substrate import GeometricProperty
        prop = GeometricProperty(property)
        token = self.substrate.create_geometric_token(spiral, level, prop)
        self._token_map[name] = token
        return token
    
    def register_computed(
        self,
        name: str,
        spiral: int,
        level: int,
        compute_fn: Callable[[int, int], Any]
    ) -> Token:
        """
        Register a computed token with a function of position.
        
        The compute_fn receives (spiral, level) and returns the value.
        """
        token = self.substrate.create_computed_token(
            location=(spiral, level),
            compute_fn=compute_fn,
            signature={level},
            spiral_affinity=spiral
        )
        self._token_map[name] = token
        return token
    
    def populate_geometric(
        self,
        spiral_range: tuple,
        level_range: tuple,
        properties: list
    ) -> list:
        """
        Populate a region with geometric tokens.
        
        Creates tokens for all positions × properties combinations.
        All values derived from mathematics, nothing stored.
        """
        from .substrate import GeometricProperty
        props = [GeometricProperty(p) for p in properties]
        return self.substrate.populate_with_geometry(spiral_range, level_range, props)
    
    # -------------------------------------------------------------------------
    # Token Registration (Traditional - Stored Data)
    # -------------------------------------------------------------------------
    
    def register(
        self,
        name: str,
        level: int,
        data: Any,
        location: tuple = None,
        spiral: int = None
    ) -> Token:
        """
        Register a token with automatic ID and location.
        
        Args:
            name: Human-readable identifier
            level: Dimensional level (0-6)
            data: The payload data
            location: Optional manifold coordinates
            spiral: Optional spiral affinity
        
        Returns:
            The created token
        """
        token_id = f"{name}_{uuid.uuid4().hex[:8]}"
        loc = location or (hash(name) % 1000, level, 0)
        
        token = self.substrate.create_token(
            location=loc,
            signature={level},
            payload=lambda d=data: d,
            spiral_affinity=spiral,
            token_id=token_id
        )
        
        self._token_map[name] = token
        return token
    
    def register_hierarchy(
        self,
        name: str,
        data: dict,
        level: int = 6
    ) -> Token:
        """
        Register a hierarchical structure as tokens at multiple levels.
        
        Each nested dict becomes a token at a lower level.
        """
        def process_level(obj: Any, current_level: int, parent_name: str) -> Token:
            token_name = f"{parent_name}"
            
            if isinstance(obj, dict):
                # Register the container
                token = self.register(token_name, current_level, obj)
                
                # Process children at lower level
                if current_level > 0:
                    for key, value in obj.items():
                        if isinstance(value, dict):
                            process_level(value, current_level - 1, f"{parent_name}.{key}")
                
                return token
            else:
                return self.register(token_name, current_level, obj)
        
        return process_level(data, level, name)
    
    # -------------------------------------------------------------------------
    # Ingestion - O(1) External Data Assimilation
    # -------------------------------------------------------------------------
    
    def ingest(self, spiral: int, level: int, value: Any) -> None:
        """
        Ingest external data into the manifold at (spiral, level) coordinates.
        O(1) storage via direct hash table.
        
        Args:
            spiral: Which spiral (dimension) to store in
            level: Which level (0-6) within the spiral
            value: Any data to assimilate
        """
        self.substrate.ingest(spiral, level, value)
    
    def extract(self, spiral: int, level: int, default: Any = None) -> Any:
        """
        Extract ingested data from (spiral, level) coordinates.
        O(1) retrieval via direct hash lookup.
        
        Args:
            spiral: Which spiral to extract from
            level: Which level within the spiral
            default: Value to return if nothing ingested at coordinates
            
        Returns:
            The ingested value or default
        """
        return self.substrate.extract(spiral, level, default)
    
    def ingest_keyed(self, spiral: int, level: int, key: str, value: Any) -> None:
        """
        Ingest with additional key for multiple values at same coordinate.
        O(1) storage.
        
        Args:
            spiral: Which spiral
            level: Which level
            key: Additional key for disambiguation
            value: Data to assimilate
        """
        self.substrate.ingest_keyed(spiral, level, key, value)
    
    def extract_keyed(self, spiral: int, level: int, key: str, default: Any = None) -> Any:
        """
        Extract keyed data from coordinates.
        O(1) retrieval.
        """
        return self.substrate.extract_keyed(spiral, level, key, default)
    
    def ingest_batch(self, data_list: List[Any], start_spiral: int = 0, start_level: int = 0) -> List[Tuple[int, int]]:
        """
        Batch ingest multiple items sequentially along the helix.
        
        Data is placed incrementing level then spiral: (0,0), (0,1)...
        (0,6), (1,0), (1,1)...
        
        Args:
            data_list: List of data items to ingest
            start_spiral: Starting spiral (default 0)
            start_level: Starting level (default 0)
            
        Returns:
            List of (spiral, level) coordinates where data was placed
        """
        return self.substrate.ingest_batch(data_list, start_spiral, start_level)
    
    def ingest_dict(self, data: Dict[str, Any], spiral: int = 0, level: int = 6) -> Dict[str, Tuple[int, int, str]]:
        """
        Ingest a dictionary using keys as keyed storage.
        
        All key-value pairs stored at same (spiral, level) with key differentiator.
        
        Args:
            data: Dictionary to ingest
            spiral: Which spiral to use (default 0)
            level: Which level to use (default 6)
            
        Returns:
            Dict mapping keys to their full (spiral, level, key) coordinates
        """
        return self.substrate.ingest_dict(data, spiral, level)
    
    def has_ingested(self, spiral: int, level: int) -> bool:
        """Check if data exists at coordinates."""
        return self.substrate.has(spiral, level)
    
    def ingested_count(self) -> int:
        """Total number of ingested values."""
        return self.substrate.ingested_count
    
    # -------------------------------------------------------------------------
    # Operations
    # -------------------------------------------------------------------------
    
    def invoke(self, level: int) -> Set[Token]:
        """Invoke a level, returning materialized tokens"""
        return self.kernel.invoke(level)
    
    def spiral_up(self) -> None:
        """Spiral up (must be at level 6)"""
        self.kernel.spiral_up()
    
    def spiral_down(self) -> None:
        """Spiral down (must be at level 0)"""
        self.kernel.spiral_down()
    
    def collapse(self) -> None:
        """Collapse to potential"""
        self.kernel.collapse()
    
    # -------------------------------------------------------------------------
    # State Access
    # -------------------------------------------------------------------------
    
    @property
    def state(self) -> HelixState:
        return self.kernel.state
    
    @property
    def spiral(self) -> int:
        return self.kernel.spiral
    
    @property
    def level(self) -> int:
        return self.kernel.level
    
    def get_token(self, name: str) -> Optional[Token]:
        """Get a registered token by name"""
        return self._token_map.get(name)


# =============================================================================
# DIMENSIONAL ITERATOR - Iterate by level, not by item
# =============================================================================

class DimensionalIterator:
    """
    Iterator that works by dimensional levels, not items.
    
    Instead of:
        for item in items:  # O(N) iterations
    
    Use:
        for level in DimensionalIterator(6, 1):  # O(6) iterations
            tokens = ctx.invoke(level)
    """
    
    def __init__(self, start_level: int = 6, end_level: int = 0, step: int = -1):
        self.start = start_level
        self.end = end_level
        self.step = step
        self.current = start_level
    
    def __iter__(self) -> Iterator[int]:
        self.current = self.start
        return self
    
    def __next__(self) -> int:
        if self.step < 0 and self.current < self.end:
            raise StopIteration
        if self.step > 0 and self.current > self.end:
            raise StopIteration
        
        level = self.current
        self.current += self.step
        return level


# =============================================================================
# HELIX COLLECTION - Collection that uses dimensional access
# =============================================================================

class HelixCollection(Generic[T]):
    """
    A collection that organizes items by dimensional level.
    
    Instead of a flat list, items are grouped by their level.
    Access is by level invocation, not iteration.
    """
    
    def __init__(self):
        self._by_level: dict[int, list[T]] = {i: [] for i in range(7)}
        self._ctx = HelixContext()
    
    def add(self, item: T, level: int) -> None:
        """Add an item at a specific level"""
        if not 0 <= level <= 6:
            raise ValueError(f"Level must be 0-6, got {level}")
        self._by_level[level].append(item)
        self._ctx.register(f"item_{id(item)}", level, item)
    
    def invoke(self, level: int) -> list[T]:
        """Get all items at a level (single operation)"""
        return self._by_level.get(level, [])
    
    def invoke_range(self, start: int, end: int) -> list[T]:
        """Get items across a range of levels"""
        result = []
        for level in range(start, end + 1):
            result.extend(self._by_level.get(level, []))
        return result
    
    def __len__(self) -> int:
        return sum(len(items) for items in self._by_level.values())
    
    @property
    def level_counts(self) -> dict[int, int]:
        return {level: len(items) for level, items in self._by_level.items()}


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # From kernel
    'HelixKernel',
    'HelixState',
    'LEVEL_NAMES',
    'LEVEL_ICONS',
    
    # From substrate
    'ManifoldSubstrate',
    'Token',
    
    # New primitives
    'DimensionalType',
    'LazyValue',
    'HelixContext',
    'DimensionalIterator',
    'HelixCollection',
]
