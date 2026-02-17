"""
ButterflyFX Utilities - Practical Tools Using Primitives

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

Part of ButterflyFX Infrastructure - Open source utility layer.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

Layer 2: Utilities
    Small, focused tools that use the primitives layer.
    Each utility solves one problem well.
    
Utilities:
    - HelixPath: Navigate dimensional paths (like filesystem paths)
    - HelixQuery: Query tokens by criteria
    - HelixCache: Level-aware caching
    - HelixSerializer: Serialize/deserialize helix structures
    - HelixDiff: Compare two helix states
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Set, Optional, List, Dict, Union
from .primitives import (
    HelixContext, DimensionalType, LazyValue,
    HelixKernel, HelixState, ManifoldSubstrate, Token,
    LEVEL_NAMES
)
import json
import hashlib
from datetime import datetime


# =============================================================================
# HELIX PATH - Navigate dimensional structures like paths
# =============================================================================

@dataclass
class HelixPath:
    """
    A path through dimensional space.
    
    Instead of: /cars/tesla/model_s/doors/driver/handle
    Use:        helix:6.tesla/5.doors/4.driver/3.handle
    
    The level is explicit in the path, making navigation O(1) per level.
    """
    segments: List[tuple[int, str]]  # [(level, name), ...]
    
    @classmethod
    def parse(cls, path: str) -> 'HelixPath':
        """
        Parse a helix path string.
        
        Format: "level.name/level.name/..."
        Example: "6.car/5.parts/4.engine"
        """
        segments = []
        for part in path.split('/'):
            if '.' in part:
                level_str, name = part.split('.', 1)
                segments.append((int(level_str), name))
            else:
                # Default to level 6 if not specified
                segments.append((6, part))
        return cls(segments)
    
    @classmethod
    def from_traditional(cls, path: str) -> 'HelixPath':
        """
        Convert traditional path to helix path.
        Infers levels from depth (deeper = lower level).
        """
        parts = [p for p in path.split('/') if p]
        segments = []
        start_level = min(6, len(parts) - 1)
        
        for i, part in enumerate(parts):
            level = max(0, start_level - i)
            segments.append((level, part))
        
        return cls(segments)
    
    def __str__(self) -> str:
        return '/'.join(f"{level}.{name}" for level, name in self.segments)
    
    def __truediv__(self, other: Union[str, 'HelixPath']) -> 'HelixPath':
        """Path concatenation with /"""
        if isinstance(other, str):
            other = HelixPath.parse(other)
        return HelixPath(self.segments + other.segments)
    
    @property
    def depth(self) -> int:
        """Number of segments"""
        return len(self.segments)
    
    @property
    def target_level(self) -> int:
        """The level of the final segment"""
        return self.segments[-1][0] if self.segments else 6
    
    @property
    def target_name(self) -> str:
        """The name of the final segment"""
        return self.segments[-1][1] if self.segments else ""
    
    def levels_traversed(self) -> Set[int]:
        """All levels this path touches"""
        return {level for level, _ in self.segments}
    
    def walk(self, context: HelixContext) -> List[Set[Token]]:
        """
        Walk the path, collecting tokens at each level.
        Returns list of token sets for each segment.
        """
        results = []
        for level, name in self.segments:
            tokens = context.invoke(level)
            # Filter by name (in real impl, would use substrate query)
            matching = {t for t in tokens if name in str(t.payload)}
            results.append(matching)
        return results


# =============================================================================
# HELIX QUERY - Query tokens by criteria
# =============================================================================

@dataclass
class HelixQuery:
    """
    Query builder for helix tokens.
    
    Instead of SQL or complex filters, queries work dimensionally:
    - Filter by level (O(1))
    - Filter by spiral (O(1))  
    - Filter by signature (O(1))
    
    Then materialize only what matches.
    """
    levels: Optional[Set[int]] = None
    spirals: Optional[Set[int]] = None
    signature_match: Optional[Set[int]] = None
    payload_predicate: Optional[Callable[[Any], bool]] = None
    limit: Optional[int] = None
    
    def at_level(self, *levels: int) -> 'HelixQuery':
        """Filter to specific levels"""
        self.levels = set(levels)
        return self
    
    def at_spiral(self, *spirals: int) -> 'HelixQuery':
        """Filter to specific spirals"""
        self.spirals = set(spirals)
        return self
    
    def with_signature(self, *signature: int) -> 'HelixQuery':
        """Filter by signature levels"""
        self.signature_match = set(signature)
        return self
    
    def where(self, predicate: Callable[[Any], bool]) -> 'HelixQuery':
        """Filter by payload (evaluated lazily)"""
        self.payload_predicate = predicate
        return self
    
    def take(self, n: int) -> 'HelixQuery':
        """Limit results"""
        self.limit = n
        return self
    
    def execute(self, substrate: ManifoldSubstrate) -> List[Token]:
        """
        Execute the query against a substrate.
        
        Returns matching tokens, materialized.
        """
        results = []
        
        # Get all tokens (in real impl, would use indices)
        all_tokens = substrate._tokens.values()
        
        for token in all_tokens:
            # Level filter
            if self.levels is not None:
                if not any(l in self.levels for l in token.signature):
                    continue
            
            # Spiral filter
            if self.spirals is not None:
                if token.spiral_affinity not in self.spirals:
                    continue
            
            # Signature filter
            if self.signature_match is not None:
                if not self.signature_match.issubset(token.signature):
                    continue
            
            # Payload filter (lazy - only evaluate if other filters pass)
            if self.payload_predicate is not None:
                payload = token.payload
                if callable(payload):
                    payload = payload()
                if not self.payload_predicate(payload):
                    continue
            
            results.append(token)
            
            # Limit check
            if self.limit and len(results) >= self.limit:
                break
        
        return results


# =============================================================================
# HELIX CACHE - Level-aware caching
# =============================================================================

class HelixCache:
    """
    Cache that understands dimensional levels.
    
    Higher levels (6-5) change less often → longer cache TTL
    Lower levels (0-1) change more often → shorter cache TTL
    
    Invalidation cascades: invalidating level N also invalidates 0..N-1
    """
    
    DEFAULT_TTL_BY_LEVEL = {
        6: 3600,   # Whole: 1 hour
        5: 1800,   # Volume: 30 min
        4: 900,    # Plane: 15 min
        3: 300,    # Width: 5 min
        2: 60,     # Length: 1 min
        1: 10,     # Point: 10 sec
        0: 1,      # Potential: 1 sec
    }
    
    def __init__(self, ttl_by_level: Dict[int, int] = None):
        self._cache: Dict[str, Dict] = {}  # key -> {value, level, timestamp}
        self._ttl = ttl_by_level or self.DEFAULT_TTL_BY_LEVEL
    
    def get(self, key: str) -> Optional[Any]:
        """Get a cached value if not expired"""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        age = (datetime.now() - entry['timestamp']).total_seconds()
        ttl = self._ttl.get(entry['level'], 60)
        
        if age > ttl:
            del self._cache[key]
            return None
        
        return entry['value']
    
    def set(self, key: str, value: Any, level: int) -> None:
        """Cache a value at a specific level"""
        self._cache[key] = {
            'value': value,
            'level': level,
            'timestamp': datetime.now()
        }
    
    def invalidate_level(self, level: int) -> int:
        """
        Invalidate all entries at level and below.
        Returns count of invalidated entries.
        """
        to_remove = [
            key for key, entry in self._cache.items()
            if entry['level'] <= level
        ]
        for key in to_remove:
            del self._cache[key]
        return len(to_remove)
    
    def invalidate_all(self) -> None:
        """Clear entire cache"""
        self._cache.clear()
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Cache statistics"""
        by_level = {i: 0 for i in range(7)}
        for entry in self._cache.values():
            by_level[entry['level']] += 1
        
        return {
            'total_entries': len(self._cache),
            'by_level': by_level
        }


# =============================================================================
# HELIX SERIALIZER - Serialize/deserialize helix structures
# =============================================================================

class HelixSerializer:
    """
    Serialize helix structures to portable formats.
    
    Preserves:
        - Dimensional levels
        - Spiral positions
        - Token signatures
        - Lazy payload factories (as serialized data)
    """
    
    @staticmethod
    def token_to_dict(token: Token) -> Dict:
        """Serialize a token"""
        payload = token.payload
        if callable(payload):
            payload = payload()
        
        return {
            'id': token.id,
            'location': list(token.location),
            'signature': list(token.signature),
            'payload': payload,
            'spiral_affinity': token.spiral_affinity
        }
    
    @staticmethod
    def dict_to_token(data: Dict) -> Token:
        """Deserialize a token"""
        return Token(
            id=data['id'],
            location=tuple(data['location']),
            signature=frozenset(data['signature']),
            payload=data['payload'],
            spiral_affinity=data.get('spiral_affinity')
        )
    
    @staticmethod
    def to_json(substrate: ManifoldSubstrate) -> str:
        """Serialize a substrate to JSON"""
        tokens = [
            HelixSerializer.token_to_dict(t)
            for t in substrate._tokens.values()
        ]
        return json.dumps({
            'version': '1.0',
            'tokens': tokens
        }, indent=2)
    
    @staticmethod
    def from_json(data: str) -> ManifoldSubstrate:
        """Deserialize a substrate from JSON"""
        parsed = json.loads(data)
        substrate = ManifoldSubstrate()
        
        for token_data in parsed.get('tokens', []):
            token = HelixSerializer.dict_to_token(token_data)
            substrate.register_token(token)
        
        return substrate
    
    @staticmethod
    def hash_token(token: Token) -> str:
        """Create a content hash of a token"""
        payload = token.payload
        if callable(payload):
            payload = payload()
        
        content = json.dumps({
            'location': token.location,
            'signature': sorted(token.signature),
            'payload': str(payload)
        }, sort_keys=True)
        
        return hashlib.sha256(content.encode()).hexdigest()[:16]


# =============================================================================
# HELIX DIFF - Compare helix states
# =============================================================================

@dataclass
class HelixDiffResult:
    """Result of comparing two helix structures"""
    added: List[Token]
    removed: List[Token]
    modified: List[tuple[Token, Token]]  # (old, new)
    unchanged: int
    
    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.modified)
    
    def summary(self) -> str:
        return (
            f"+{len(self.added)} added, "
            f"-{len(self.removed)} removed, "
            f"~{len(self.modified)} modified, "
            f"={self.unchanged} unchanged"
        )


class HelixDiff:
    """
    Compare two helix substrate states.
    
    Works level-by-level for O(7) complexity instead of O(N).
    """
    
    @staticmethod
    def compare(
        old_substrate: ManifoldSubstrate,
        new_substrate: ManifoldSubstrate
    ) -> HelixDiffResult:
        """Compare two substrates"""
        old_ids = set(old_substrate._tokens.keys())
        new_ids = set(new_substrate._tokens.keys())
        
        added_ids = new_ids - old_ids
        removed_ids = old_ids - new_ids
        common_ids = old_ids & new_ids
        
        added = [new_substrate._tokens[id] for id in added_ids]
        removed = [old_substrate._tokens[id] for id in removed_ids]
        
        modified = []
        unchanged = 0
        
        for id in common_ids:
            old_hash = HelixSerializer.hash_token(old_substrate._tokens[id])
            new_hash = HelixSerializer.hash_token(new_substrate._tokens[id])
            
            if old_hash != new_hash:
                modified.append((
                    old_substrate._tokens[id],
                    new_substrate._tokens[id]
                ))
            else:
                unchanged += 1
        
        return HelixDiffResult(
            added=added,
            removed=removed,
            modified=modified,
            unchanged=unchanged
        )
    
    @staticmethod
    def compare_by_level(
        old_substrate: ManifoldSubstrate,
        new_substrate: ManifoldSubstrate
    ) -> Dict[int, HelixDiffResult]:
        """Compare substrates level by level"""
        results = {}
        
        for level in range(7):
            # Get tokens at this level
            old_at_level = ManifoldSubstrate()
            new_at_level = ManifoldSubstrate()
            
            for id, token in old_substrate._tokens.items():
                if level in token.signature:
                    old_at_level.register_token(token)
            
            for id, token in new_substrate._tokens.items():
                if level in token.signature:
                    new_at_level.register_token(token)
            
            results[level] = HelixDiff.compare(old_at_level, new_at_level)
        
        return results


# =============================================================================
# HELIX LOGGER - Dimensional logging
# =============================================================================

class HelixLogger:
    """
    Logger that organizes entries by dimensional level.
    
    - Level 6 (Whole): System events
    - Level 5 (Volume): Module events
    - Level 4 (Plane): Function events
    - Level 3 (Width): Loop iterations
    - Level 2 (Length): Line executions
    - Level 1 (Point): Variable changes
    - Level 0 (Potential): Debug traces
    """
    
    LEVEL_IMPORTANCE = {
        6: 'CRITICAL',
        5: 'ERROR',
        4: 'WARNING',
        3: 'INFO',
        2: 'DEBUG',
        1: 'TRACE',
        0: 'VERBOSE'
    }
    
    def __init__(self, min_level: int = 3):
        self.min_level = min_level
        self.entries: List[Dict] = []
    
    def log(self, level: int, message: str, data: Any = None) -> None:
        """Log at a specific dimensional level"""
        if level < self.min_level:
            return
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'level_name': LEVEL_NAMES[level],
            'importance': self.LEVEL_IMPORTANCE[level],
            'message': message,
            'data': data
        }
        self.entries.append(entry)
    
    def whole(self, message: str, data: Any = None) -> None:
        self.log(6, message, data)
    
    def volume(self, message: str, data: Any = None) -> None:
        self.log(5, message, data)
    
    def plane(self, message: str, data: Any = None) -> None:
        self.log(4, message, data)
    
    def width(self, message: str, data: Any = None) -> None:
        self.log(3, message, data)
    
    def length(self, message: str, data: Any = None) -> None:
        self.log(2, message, data)
    
    def point(self, message: str, data: Any = None) -> None:
        self.log(1, message, data)
    
    def potential(self, message: str, data: Any = None) -> None:
        self.log(0, message, data)
    
    def get_by_level(self, level: int) -> List[Dict]:
        """Get all entries at a specific level"""
        return [e for e in self.entries if e['level'] == level]
    
    def get_range(self, min_level: int, max_level: int) -> List[Dict]:
        """Get entries in a level range"""
        return [e for e in self.entries if min_level <= e['level'] <= max_level]


# =============================================================================
# MANIFOLD SAMPLER - Sample values from manifold geometry
# =============================================================================

class ManifoldSampler:
    """
    Utility for sampling values from the generative manifold.
    
    Instead of storing data, pull any value you need from mathematics:
    - Trigonometric values at any position
    - Slopes, curvatures, inflections
    - Generated matrices, vectors, spectra
    - Statistical distributions
    
    Usage:
        sampler = ManifoldSampler()
        
        # Single value
        val = sampler.at(0, 3).sin
        
        # Matrix of values
        matrix = sampler.matrix((0, 2), (0, 6), 'curvature')
        
        # Wave function
        wave = sampler.wave('sin', frequency=2.0)
    """
    
    def __init__(self):
        from .manifold import GenerativeManifold
        self._manifold = GenerativeManifold()
    
    def at(self, spiral: int, level: int):
        """Get a SurfacePoint with all geometric properties"""
        return self._manifold.at(spiral, level)
    
    def value(self, spiral: int, level: int, property: str) -> Any:
        """Get a specific property value at a position"""
        point = self._manifold.at(spiral, level)
        return getattr(point, property)
    
    def matrix(
        self,
        spiral_range: tuple,
        level_range: tuple,
        property: str = 'sin'
    ) -> List[List[float]]:
        """
        Generate a matrix of values from the manifold surface.
        
        Rows = spirals, Cols = levels
        """
        region = self._manifold.region(
            spiral_range[0], level_range[0],
            spiral_range[1], level_range[1]
        )
        return self._manifold.as_matrix(region, lambda p: getattr(p, property))
    
    def vector(
        self,
        spiral_range: tuple,
        level_range: tuple,
        property: str = 'sin'
    ) -> List[float]:
        """Generate a 1D vector from the manifold"""
        region = self._manifold.region(
            spiral_range[0], level_range[0],
            spiral_range[1], level_range[1]
        )
        return self._manifold.as_vector(region, lambda p: getattr(p, property))
    
    def wave(
        self,
        wave_type: str = 'sin',
        frequency: float = 1.0,
        amplitude: float = 1.0,
        phase: float = 0.0
    ) -> Callable[[float], float]:
        """Generate a wave function from manifold geometry"""
        return self._manifold.as_wave(wave_type, frequency, amplitude, phase)
    
    def spectrum(
        self,
        spiral_range: tuple,
        level_range: tuple,
        num_harmonics: int = 7
    ) -> Dict[int, complex]:
        """Extract frequency spectrum from a region"""
        region = self._manifold.region(
            spiral_range[0], level_range[0],
            spiral_range[1], level_range[1]
        )
        return self._manifold.as_spectrum(region, num_harmonics)
    
    def probability(
        self,
        spiral_range: tuple,
        level_range: tuple,
        property: str = 'sin'
    ) -> Callable[[int, int], float]:
        """Generate a probability distribution from geometry"""
        region = self._manifold.region(
            spiral_range[0], level_range[0],
            spiral_range[1], level_range[1]
        )
        return self._manifold.as_probability(region, lambda p: abs(getattr(p, property)))
    
    def function(self, property: str = 'sin') -> Callable[[float], float]:
        """Generate a continuous function f(t) -> value"""
        return self._manifold.as_function(lambda p: getattr(p, property))
    
    def parametric(self) -> Callable[[float], tuple]:
        """Generate the parametric curve (x, y, z) = f(t)"""
        return self._manifold.as_parametric_function()
    
    def graph(
        self,
        spiral_range: tuple,
        level_range: tuple
    ) -> Dict[tuple, List[tuple]]:
        """Generate a graph structure from helix topology"""
        region = self._manifold.region(
            spiral_range[0], level_range[0],
            spiral_range[1], level_range[1]
        )
        return self._manifold.as_graph(region)
    
    def domain(
        self,
        spiral_range: tuple,
        level_range: tuple
    ) -> tuple:
        """Get the t-parameter domain of a region"""
        region = self._manifold.region(
            spiral_range[0], level_range[0],
            spiral_range[1], level_range[1]
        )
        return self._manifold.as_domain(region)
    
    def range(
        self,
        spiral_range: tuple,
        level_range: tuple,
        property: str = 'sin'
    ) -> tuple:
        """Get the value range of a property over a region"""
        region = self._manifold.region(
            spiral_range[0], level_range[0],
            spiral_range[1], level_range[1]
        )
        return self._manifold.as_range(region, lambda p: getattr(p, property))
    
    def span(
        self,
        spiral_range: tuple,
        level_range: tuple
    ) -> Dict[str, tuple]:
        """Get all geometric spans (x, y, z, angle, t ranges)"""
        region = self._manifold.region(
            spiral_range[0], level_range[0],
            spiral_range[1], level_range[1]
        )
        return self._manifold.as_span(region)


# =============================================================================
# MANIFOLD QUERY - Query derived values instead of stored data
# =============================================================================

class ManifoldQuery:
    """
    Query builder for manifold-derived values.
    
    Instead of querying stored data, queries specify:
    - What geometric property to extract
    - What region of the manifold to sample
    - What transformations to apply
    
    Usage:
        query = ManifoldQuery()
        result = (query
            .property('sin')
            .region((0, 2), (0, 6))
            .transform(lambda x: x ** 2)
            .as_matrix())
    """
    
    def __init__(self):
        from .manifold import GenerativeManifold
        self._manifold = GenerativeManifold()
        self._property = 'sin'
        self._spiral_range = (0, 0)
        self._level_range = (0, 6)
        self._transform = None
        self._filter = None
    
    def property(self, prop: str) -> 'ManifoldQuery':
        """Set the geometric property to extract"""
        self._property = prop
        return self
    
    def region(
        self,
        spiral_range: tuple,
        level_range: tuple
    ) -> 'ManifoldQuery':
        """Set the region to sample"""
        self._spiral_range = spiral_range
        self._level_range = level_range
        return self
    
    def spirals(self, start: int, end: int) -> 'ManifoldQuery':
        """Set spiral range"""
        self._spiral_range = (start, end)
        return self
    
    def levels(self, start: int, end: int) -> 'ManifoldQuery':
        """Set level range"""
        self._level_range = (start, end)
        return self
    
    def transform(self, fn: Callable[[float], float]) -> 'ManifoldQuery':
        """Apply a transformation to extracted values"""
        self._transform = fn
        return self
    
    def where(self, predicate: Callable[[float], bool]) -> 'ManifoldQuery':
        """Filter values by predicate"""
        self._filter = predicate
        return self
    
    def _get_region(self):
        return self._manifold.region(
            self._spiral_range[0], self._level_range[0],
            self._spiral_range[1], self._level_range[1]
        )
    
    def _extract(self, point) -> float:
        val = getattr(point, self._property)
        if self._transform:
            val = self._transform(val)
        return val
    
    def as_matrix(self) -> List[List[float]]:
        """Execute query and return matrix"""
        region = self._get_region()
        matrix = self._manifold.as_matrix(region, self._extract)
        
        if self._filter:
            # Filter: replace non-matching with None or 0
            matrix = [
                [v if self._filter(v) else 0.0 for v in row]
                for row in matrix
            ]
        
        return matrix
    
    def as_vector(self) -> List[float]:
        """Execute query and return vector"""
        region = self._get_region()
        vector = self._manifold.as_vector(region, self._extract)
        
        if self._filter:
            vector = [v for v in vector if self._filter(v)]
        
        return vector
    
    def as_aggregate(self, agg: str = 'sum') -> float:
        """
        Execute query and return aggregate.
        
        agg: 'sum', 'mean', 'min', 'max', 'count'
        """
        vector = self.as_vector()
        if not vector:
            return 0.0
        
        if agg == 'sum':
            return sum(vector)
        elif agg == 'mean':
            return sum(vector) / len(vector)
        elif agg == 'min':
            return min(vector)
        elif agg == 'max':
            return max(vector)
        elif agg == 'count':
            return float(len(vector))
        else:
            raise ValueError(f"Unknown aggregate: {agg}")
    
    def as_function(self) -> Callable[[int, int], float]:
        """Return a function f(spiral, level) -> transformed value"""
        def f(spiral: int, level: int) -> float:
            point = self._manifold.at(spiral, level)
            return self._extract(point)
        return f


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'HelixPath',
    'HelixQuery',
    'HelixCache',
    'HelixSerializer',
    'HelixDiff',
    'HelixDiffResult',
    'HelixLogger',
    'ManifoldSampler',
    'ManifoldQuery',
]
