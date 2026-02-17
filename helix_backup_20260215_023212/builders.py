"""
ButterflyFX Builders - Fluent Object Construction

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

Attribution required: Kenneth Bingham - https://butterflyfx.us

---

Fluent builders for constructing complex ButterflyFX objects.

Builders:
    - TokenBuilder: Build tokens with fluent API
    - StateBuilder: Build helix states
    - ManifoldBuilder: Build manifold configurations
    - QueryBuilder: Build complex queries
    - PathBuilder: Build helix paths
"""

from __future__ import annotations
from typing import Any, Dict, List, Union, Optional, Set, Callable, TypeVar
from dataclasses import dataclass, field
import uuid
from datetime import datetime

from .kernel import HelixState, HelixKernel, LEVEL_NAMES
from .substrate import Token, PayloadSource, GeometricProperty, ManifoldSubstrate


T = TypeVar('T')


# =============================================================================
# TOKEN BUILDER
# =============================================================================

class TokenBuilder:
    """
    Fluent builder for creating tokens.
    
    Usage:
        token = TokenBuilder() \
            .id("user_123") \
            .at(0, 3) \
            .levels(3, 4, 5) \
            .payload({"name": "Alice"}) \
            .build()
    """
    
    def __init__(self):
        self._id: Optional[str] = None
        self._location: tuple = (0, 0, 0)
        self._signature: Set[int] = {0, 1, 2, 3, 4, 5, 6}
        self._payload: Any = None
        self._payload_fn: Optional[Callable] = None
        self._spiral_affinity: Optional[int] = None
        self._payload_source: PayloadSource = PayloadSource.STORED
        self._geometric_property: Optional[GeometricProperty] = None
    
    def id(self, token_id: str) -> 'TokenBuilder':
        """Set token ID"""
        self._id = token_id
        return self
    
    def auto_id(self, prefix: str = "token") -> 'TokenBuilder':
        """Generate automatic ID"""
        self._id = f"{prefix}_{uuid.uuid4().hex[:8]}"
        return self
    
    def at(self, spiral: int, level: int, z: float = 0) -> 'TokenBuilder':
        """Set location as (spiral, level, z)"""
        self._location = (spiral, level, z)
        return self
    
    def location(self, *coords) -> 'TokenBuilder':
        """Set location with arbitrary coordinates"""
        self._location = tuple(coords)
        return self
    
    def xyz(self, x: float, y: float, z: float) -> 'TokenBuilder':
        """Set location as (x, y, z)"""
        self._location = (x, y, z)
        return self
    
    def levels(self, *levels: int) -> 'TokenBuilder':
        """Set which levels this token can inhabit"""
        self._signature = set(levels)
        return self
    
    def level(self, level: int) -> 'TokenBuilder':
        """Set single level"""
        self._signature = {level}
        return self
    
    def all_levels(self) -> 'TokenBuilder':
        """Token inhabits all levels"""
        self._signature = {0, 1, 2, 3, 4, 5, 6}
        return self
    
    def level_range(self, min_level: int, max_level: int) -> 'TokenBuilder':
        """Token inhabits range of levels"""
        self._signature = set(range(min_level, max_level + 1))
        return self
    
    def payload(self, data: Any) -> 'TokenBuilder':
        """Set static payload data"""
        self._payload = data
        self._payload_source = PayloadSource.STORED
        return self
    
    def payload_fn(self, fn: Callable[[], Any]) -> 'TokenBuilder':
        """Set lazy payload function"""
        self._payload_fn = fn
        self._payload_source = PayloadSource.STORED
        return self
    
    def computed(self, fn: Callable[[int, int], Any]) -> 'TokenBuilder':
        """Set computed payload (function of spiral, level)"""
        self._payload_fn = fn
        self._payload_source = PayloadSource.COMPUTED
        return self
    
    def geometric(self, prop: Union[str, GeometricProperty]) -> 'TokenBuilder':
        """Derive payload from manifold geometry"""
        self._payload_source = PayloadSource.GEOMETRIC
        if isinstance(prop, str):
            self._geometric_property = GeometricProperty(prop)
        else:
            self._geometric_property = prop
        return self
    
    def spiral(self, spiral: int) -> 'TokenBuilder':
        """Set spiral affinity"""
        self._spiral_affinity = spiral
        return self
    
    def build(self) -> Token:
        """Build the token"""
        if self._id is None:
            self._id = f"token_{uuid.uuid4().hex[:8]}"
        
        if self._payload_fn:
            payload = self._payload_fn
        elif self._payload is not None:
            payload = lambda p=self._payload: p
        else:
            payload = lambda: None
        
        token = Token(
            id=self._id,
            location=self._location,
            signature=self._signature,
            payload=payload,
            spiral_affinity=self._spiral_affinity,
            payload_source=self._payload_source,
            geometric_property=self._geometric_property
        )
        
        return token


# =============================================================================
# BATCH TOKEN BUILDER
# =============================================================================

class BatchTokenBuilder:
    """
    Build multiple tokens at once.
    
    Usage:
        tokens = BatchTokenBuilder() \
            .base_level(3) \
            .from_items([
                {"id": "a", "value": 1},
                {"id": "b", "value": 2}
            ]) \
            .build()
    """
    
    def __init__(self):
        self._items: List[Dict] = []
        self._base_level: int = 3
        self._base_spiral: int = 0
        self._id_field: str = "id"
        self._payload_fields: Optional[List[str]] = None
    
    def from_items(self, items: List[Any]) -> 'BatchTokenBuilder':
        """Set items to convert to tokens"""
        self._items = items
        return self
    
    def from_dicts(self, dicts: List[Dict]) -> 'BatchTokenBuilder':
        """Set dictionaries to convert to tokens"""
        self._items = dicts
        return self
    
    def base_level(self, level: int) -> 'BatchTokenBuilder':
        """Set base level for all tokens"""
        self._base_level = level
        return self
    
    def base_spiral(self, spiral: int) -> 'BatchTokenBuilder':
        """Set base spiral for all tokens"""
        self._base_spiral = spiral
        return self
    
    def id_field(self, field: str) -> 'BatchTokenBuilder':
        """Set which field to use as token ID"""
        self._id_field = field
        return self
    
    def payload_fields(self, *fields: str) -> 'BatchTokenBuilder':
        """Set which fields to include in payload"""
        self._payload_fields = list(fields)
        return self
    
    def build(self) -> List[Token]:
        """Build all tokens"""
        tokens = []
        
        for i, item in enumerate(self._items):
            builder = TokenBuilder() \
                .at(self._base_spiral, self._base_level) \
                .level(self._base_level)
            
            # Set ID
            if isinstance(item, dict) and self._id_field in item:
                builder.id(str(item[self._id_field]))
            else:
                builder.auto_id(f"batch_{i}")
            
            # Set payload
            if isinstance(item, dict):
                if self._payload_fields:
                    payload = {k: item.get(k) for k in self._payload_fields}
                else:
                    payload = item
                builder.payload(payload)
            else:
                builder.payload(item)
            
            tokens.append(builder.build())
        
        return tokens


# =============================================================================
# STATE BUILDER
# =============================================================================

class StateBuilder:
    """
    Fluent builder for helix states.
    
    Usage:
        state = StateBuilder().spiral(1).level(4).build()
        state = StateBuilder.at_level(3)
    """
    
    def __init__(self):
        self._spiral: int = 0
        self._level: int = 0
    
    def spiral(self, spiral: int) -> 'StateBuilder':
        """Set spiral"""
        self._spiral = spiral
        return self
    
    def level(self, level: int) -> 'StateBuilder':
        """Set level"""
        if not 0 <= level <= 6:
            raise ValueError(f"Level must be 0-6, got {level}")
        self._level = level
        return self
    
    def by_name(self, name: str) -> 'StateBuilder':
        """Set level by name (Potential, Point, Length, etc.)"""
        name_to_level = {v.lower(): k for k, v in LEVEL_NAMES.items()}
        if name.lower() not in name_to_level:
            raise ValueError(f"Unknown level name: {name}")
        self._level = name_to_level[name.lower()]
        return self
    
    def potential(self) -> 'StateBuilder':
        return self.level(0)
    
    def point(self) -> 'StateBuilder':
        return self.level(1)
    
    def length(self) -> 'StateBuilder':
        return self.level(2)
    
    def width(self) -> 'StateBuilder':
        return self.level(3)
    
    def plane(self) -> 'StateBuilder':
        return self.level(4)
    
    def volume(self) -> 'StateBuilder':
        return self.level(5)
    
    def whole(self) -> 'StateBuilder':
        return self.level(6)
    
    def build(self) -> HelixState:
        """Build the state"""
        return HelixState(self._spiral, self._level)
    
    @classmethod
    def at_level(cls, level: int, spiral: int = 0) -> HelixState:
        """Quick state construction"""
        return cls().spiral(spiral).level(level).build()
    
    @classmethod
    def origin(cls) -> HelixState:
        """Return origin state (0, 0)"""
        return HelixState(0, 0)


# =============================================================================
# MANIFOLD BUILDER
# =============================================================================

class ManifoldBuilder:
    """
    Build manifold substrate with tokens.
    
    Usage:
        manifold = ManifoldBuilder() \
            .add_token(token1) \
            .add_token(token2) \
            .scoped_to_spiral(0) \
            .build()
    """
    
    def __init__(self):
        self._tokens: List[Token] = []
        self._scoped_spiral: Optional[int] = None
    
    def add_token(self, token: Token) -> 'ManifoldBuilder':
        """Add a token"""
        self._tokens.append(token)
        return self
    
    def add_tokens(self, tokens: List[Token]) -> 'ManifoldBuilder':
        """Add multiple tokens"""
        self._tokens.extend(tokens)
        return self
    
    def add(self, token_id: str, level: int, payload: Any, spiral: int = 0) -> 'ManifoldBuilder':
        """Quick-add token"""
        token = TokenBuilder() \
            .id(token_id) \
            .at(spiral, level) \
            .level(level) \
            .payload(payload) \
            .build()
        self._tokens.append(token)
        return self
    
    def scoped_to_spiral(self, spiral: int) -> 'ManifoldBuilder':
        """Scope manifold to a specific spiral"""
        self._scoped_spiral = spiral
        return self
    
    def build(self) -> ManifoldSubstrate:
        """Build the manifold"""
        manifold = ManifoldSubstrate(scoped_spiral=self._scoped_spiral)
        for token in self._tokens:
            manifold.place(token)
        return manifold


# =============================================================================
# PATH BUILDER
# =============================================================================

class PathBuilder:
    """
    Build helix paths fluently.
    
    Usage:
        path = PathBuilder() \
            .segment(6, "root") \
            .segment(5, "child") \
            .segment(4, "leaf") \
            .build()
    """
    
    def __init__(self):
        self._segments: List[tuple] = []
    
    def segment(self, level: int, name: str) -> 'PathBuilder':
        """Add a path segment"""
        self._segments.append((level, name))
        return self
    
    def whole(self, name: str) -> 'PathBuilder':
        return self.segment(6, name)
    
    def volume(self, name: str) -> 'PathBuilder':
        return self.segment(5, name)
    
    def plane(self, name: str) -> 'PathBuilder':
        return self.segment(4, name)
    
    def width(self, name: str) -> 'PathBuilder':
        return self.segment(3, name)
    
    def length(self, name: str) -> 'PathBuilder':
        return self.segment(2, name)
    
    def point(self, name: str) -> 'PathBuilder':
        return self.segment(1, name)
    
    def potential(self, name: str) -> 'PathBuilder':
        return self.segment(0, name)
    
    def descend(self, names: List[str], start_level: int = 6) -> 'PathBuilder':
        """Add descending segments"""
        for i, name in enumerate(names):
            level = max(0, start_level - i)
            self._segments.append((level, name))
        return self
    
    def build(self) -> str:
        """Build path string"""
        return '/'.join(f"{level}.{name}" for level, name in self._segments)
    
    @classmethod
    def from_parts(cls, *names: str, start_level: int = 6) -> str:
        """Quick path from names"""
        return cls().descend(list(names), start_level).build()


# =============================================================================
# KERNEL BUILDER
# =============================================================================

class KernelBuilder:
    """
    Build and configure a HelixKernel.
    
    Usage:
        kernel = KernelBuilder() \
            .with_manifold(manifold) \
            .at_state(0, 3) \
            .build()
    """
    
    def __init__(self):
        self._manifold: Optional[ManifoldSubstrate] = None
        self._initial_spiral: int = 0
        self._initial_level: int = 0
    
    def with_manifold(self, manifold: ManifoldSubstrate) -> 'KernelBuilder':
        """Set the manifold substrate"""
        self._manifold = manifold
        return self
    
    def at_state(self, spiral: int, level: int) -> 'KernelBuilder':
        """Set initial state"""
        self._initial_spiral = spiral
        self._initial_level = level
        return self
    
    def at_level(self, level: int) -> 'KernelBuilder':
        """Set initial level (spiral 0)"""
        self._initial_level = level
        return self
    
    def build(self) -> HelixKernel:
        """Build the kernel"""
        kernel = HelixKernel(substrate=self._manifold)
        if self._initial_level > 0:
            kernel.invoke(self._initial_level)
        return kernel


# =============================================================================
# QUICK BUILDERS
# =============================================================================

def token(
    id: str = None,
    level: int = 3,
    spiral: int = 0,
    payload: Any = None
) -> Token:
    """Quick token creation"""
    builder = TokenBuilder().at(spiral, level).level(level)
    if id:
        builder.id(id)
    else:
        builder.auto_id()
    if payload is not None:
        builder.payload(payload)
    return builder.build()


def tokens_from_list(items: List[Any], level: int = 3) -> List[Token]:
    """Quick token list creation"""
    return BatchTokenBuilder().from_items(items).base_level(level).build()


def state(spiral: int = 0, level: int = 0) -> HelixState:
    """Quick state creation"""
    return StateBuilder.at_level(level, spiral)


def manifold(*token_tuples) -> ManifoldSubstrate:
    """
    Quick manifold creation.
    
    Usage:
        m = manifold(
            ("user_1", 3, {"name": "Alice"}),
            ("user_2", 3, {"name": "Bob"})
        )
    """
    builder = ManifoldBuilder()
    for t in token_tuples:
        if len(t) == 3:
            builder.add(t[0], t[1], t[2])
        elif len(t) == 4:
            builder.add(t[0], t[1], t[2], spiral=t[3])
    return builder.build()
