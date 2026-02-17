"""
Dimensional Foundation - Base Classes for Universal Invoke Pattern

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

This mathematical kernel belongs to all humanity.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

FOUNDATIONAL PRINCIPLE:
    Every object in the dimensional paradigm can be INVOKED.
    Creating an object COMPLETES it through dimensional instantiation.
    All classes are INTERFACES with generic type support.
    Instantiation happens at RUNTIME.

This module provides:
    - Dimensional: Base class with invoke() for all objects
    - DimensionalInterface: Generic interface protocol
    - DimensionalFactory: Runtime instantiation
    - Auto-completion on construction
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    Any, Dict, List, Optional, TypeVar, Generic, Type, Callable,
    Protocol, runtime_checkable, ClassVar, Set, Tuple, Union,
    Iterator, Mapping, get_type_hints, get_origin, get_args
)
from abc import ABC, abstractmethod
from functools import wraps, cached_property
from weakref import WeakSet
from enum import Enum, auto
from threading import RLock
import inspect
import uuid


# =============================================================================
# TYPE VARIABLES
# =============================================================================

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')
R = TypeVar('R')  # Return type
P = TypeVar('P')  # Payload type
S = TypeVar('S', bound='Dimensional')


# =============================================================================
# DIMENSIONAL LEVELS
# =============================================================================

class Level(Enum):
    """The seven dimensional levels."""
    POTENTIAL = 0  # Unmanifested possibility
    POINT = 1      # Identity, existence
    LENGTH = 2     # Relationship, connection  
    WIDTH = 3      # Area, surface
    PLANE = 4      # Structure, organization
    VOLUME = 5     # Mass, substance
    WHOLE = 6      # Completeness, unity


LEVEL_NAMES = tuple(l.name for l in Level)


# =============================================================================
# DIMENSIONAL STATE
# =============================================================================

@dataclass(frozen=True, slots=True)
class DimensionalState:
    """
    Immutable state of a dimensional object.
    
    spiral: Which iteration (can be negative for ancestral spirals)
    level: Current dimensional level (0-6)
    """
    spiral: int = 0
    level: int = 0
    
    def __post_init__(self):
        if not 0 <= self.level <= 6:
            object.__setattr__(self, 'level', max(0, min(6, self.level)))
    
    @property
    def level_enum(self) -> Level:
        return Level(self.level)
    
    @property
    def level_name(self) -> str:
        return LEVEL_NAMES[self.level]
    
    @property
    def is_potential(self) -> bool:
        return self.level == 0
    
    @property
    def is_complete(self) -> bool:
        return self.level == 6
    
    def at_level(self, level: int) -> 'DimensionalState':
        """Return new state at specified level."""
        return DimensionalState(self.spiral, level)
    
    def next_spiral(self) -> 'DimensionalState':
        """Return state at beginning of next spiral."""
        return DimensionalState(self.spiral + 1, 0)
    
    def prev_spiral(self) -> 'DimensionalState':
        """Return state at end of previous spiral."""
        return DimensionalState(self.spiral - 1, 6)
    
    def __repr__(self) -> str:
        return f"({self.spiral}.{self.level}:{self.level_name})"


# =============================================================================
# INVOKE RESULT
# =============================================================================

@dataclass(slots=True)
class InvokeResult(Generic[T]):
    """
    Result of invoking a dimensional object to a level.
    
    Contains the materialized value and metadata about the invocation.
    """
    value: T
    state: DimensionalState
    source: str
    cached: bool = False
    
    @property
    def level(self) -> int:
        return self.state.level
    
    def map(self, fn: Callable[[T], U]) -> 'InvokeResult[U]':
        """Transform the value while preserving metadata."""
        return InvokeResult(
            value=fn(self.value),
            state=self.state,
            source=self.source,
            cached=self.cached
        )


# =============================================================================
# DIMENSIONAL PROTOCOL (Interface)
# =============================================================================

@runtime_checkable
class Invokable(Protocol[T]):
    """
    Protocol for any object that can be invoked to a dimensional level.
    
    This is THE fundamental interface of the paradigm.
    """
    
    @property
    def state(self) -> DimensionalState:
        """Current dimensional state."""
        ...
    
    def invoke(self, level: int) -> InvokeResult[T]:
        """
        Invoke this object to the specified dimensional level.
        
        This is the core operation that materializes the object's
        representation at a given level of abstraction.
        """
        ...


@runtime_checkable
class Completable(Protocol):
    """Protocol for objects that can be completed through dimensional traversal."""
    
    def complete(self) -> None:
        """Complete the object by invoking through all levels to WHOLE."""
        ...
    
    @property
    def is_complete(self) -> bool:
        """Whether this object has been completed."""
        ...


@runtime_checkable
class Collapsible(Protocol):
    """Protocol for objects that can collapse back to potential."""
    
    def collapse(self) -> None:
        """Collapse to POTENTIAL level."""
        ...


# =============================================================================
# DIMENSIONAL BASE CLASS
# =============================================================================

class Dimensional(Generic[T]):
    """
    Base class for ALL dimensional objects.
    
    Every object that inherits from Dimensional:
        - Has invoke() as its core operation
        - Auto-completes on construction (if auto_complete=True)
        - Maintains dimensional state
        - Supports generic type parameters
        - Is an interface (can be composed)
    
    The invoke() method is the universal way to access an object
    at different levels of abstraction.
    
    Example:
        class MyData(Dimensional[dict]):
            def _materialize(self, level: int) -> dict:
                return {"level": level, "data": self._data}
        
        obj = MyData({"x": 1})
        result = obj.invoke(3)  # Get dict at level 3
    """
    
    # Class-level settings
    _auto_complete: ClassVar[bool] = False
    _default_level: ClassVar[int] = 0
    _cache_materializations: ClassVar[bool] = True
    
    # Instance tracking for GC and debugging
    _instances: ClassVar[WeakSet] = WeakSet()
    _instance_count: ClassVar[int] = 0
    
    __slots__ = (
        '_id', '_spiral', '_level', '_payload', 
        '_materialization_cache', '_lock', '_completed',
        '_observers', '_metadata'
    )
    
    def __init__(
        self,
        payload: Any = None,
        *,
        level: Optional[int] = None,
        spiral: int = 0,
        auto_complete: Optional[bool] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a dimensional object.
        
        Args:
            payload: The wrapped value/data
            level: Initial level (defaults to class default)
            spiral: Initial spiral (default 0)
            auto_complete: Whether to complete on init (defaults to class setting)
            metadata: Optional metadata dict
        """
        self._id = str(uuid.uuid4())
        self._spiral = spiral
        self._level = level if level is not None else self._default_level
        self._payload = payload
        self._materialization_cache: Dict[int, Any] = {}
        self._lock = RLock()
        self._completed = False
        self._observers: Set[Callable] = set()
        self._metadata = metadata or {}
        
        # Track instance
        Dimensional._instances.add(self)
        Dimensional._instance_count += 1
        
        # Auto-complete if enabled
        should_complete = auto_complete if auto_complete is not None else self._auto_complete
        if should_complete:
            self.complete()
    
    # -------------------------------------------------------------------------
    # Core Properties
    # -------------------------------------------------------------------------
    
    @property
    def id(self) -> str:
        """Unique identifier for this instance."""
        return self._id
    
    @property
    def state(self) -> DimensionalState:
        """Current dimensional state."""
        return DimensionalState(self._spiral, self._level)
    
    @property
    def level(self) -> int:
        """Current level (0-6)."""
        return self._level
    
    @property
    def spiral(self) -> int:
        """Current spiral."""
        return self._spiral
    
    @property
    def payload(self) -> Any:
        """The wrapped payload."""
        return self._payload
    
    @property
    def is_complete(self) -> bool:
        """Whether invoke(6) has been called."""
        return self._completed
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Metadata dictionary."""
        return self._metadata
    
    # -------------------------------------------------------------------------
    # INVOKE - The Core Operation
    # -------------------------------------------------------------------------
    
    def invoke(self, level: int) -> InvokeResult[T]:
        """
        INVOKE(k): Materialize this object at dimensional level k.
        
        This is THE fundamental operation. Every dimensional object
        can be invoked to reveal its representation at any level.
        
        Transition: (s, l) -> (s, k)
        
        Args:
            level: Target level (0-6)
            
        Returns:
            InvokeResult containing the materialized value
        """
        if not 0 <= level <= 6:
            raise ValueError(f"Level must be 0-6, got {level}")
        
        with self._lock:
            old_level = self._level
            self._level = level
            
            # Check cache
            if self._cache_materializations and level in self._materialization_cache:
                return InvokeResult(
                    value=self._materialization_cache[level],
                    state=self.state,
                    source=type(self).__name__,
                    cached=True
                )
            
            # Materialize
            value = self._materialize(level)
            
            # Cache
            if self._cache_materializations:
                self._materialization_cache[level] = value
            
            # Mark complete if level 6
            if level == 6:
                self._completed = True
            
            # Notify observers
            self._notify_observers(old_level, level, value)
            
            return InvokeResult(
                value=value,
                state=self.state,
                source=type(self).__name__,
                cached=False
            )
    
    def _materialize(self, level: int) -> T:
        """
        Override this to define what the object looks like at each level.
        
        Default implementation returns the payload at all levels.
        """
        return self._payload
    
    # -------------------------------------------------------------------------
    # Convenience Invoke Methods
    # -------------------------------------------------------------------------
    
    def __call__(self, level: int) -> T:
        """Shorthand: obj(3) == obj.invoke(3).value"""
        return self.invoke(level).value
    
    def __getitem__(self, level: int) -> T:
        """Shorthand: obj[3] == obj.invoke(3).value"""
        return self.invoke(level).value
    
    @property
    def potential(self) -> T:
        """Invoke to POTENTIAL (level 0)."""
        return self.invoke(0).value
    
    @property
    def point(self) -> T:
        """Invoke to POINT (level 1)."""
        return self.invoke(1).value
    
    @property
    def length(self) -> T:
        """Invoke to LENGTH (level 2)."""
        return self.invoke(2).value
    
    @property
    def width(self) -> T:
        """Invoke to WIDTH (level 3)."""
        return self.invoke(3).value
    
    @property
    def plane(self) -> T:
        """Invoke to PLANE (level 4)."""
        return self.invoke(4).value
    
    @property
    def volume(self) -> T:
        """Invoke to VOLUME (level 5)."""
        return self.invoke(5).value
    
    @property
    def whole(self) -> T:
        """Invoke to WHOLE (level 6)."""
        return self.invoke(6).value
    
    # -------------------------------------------------------------------------
    # Completable Interface
    # -------------------------------------------------------------------------
    
    def complete(self) -> 'Dimensional[T]':
        """
        Complete this object by invoking to WHOLE (level 6).
        
        Returns self for chaining.
        """
        self.invoke(6)
        return self
    
    # -------------------------------------------------------------------------
    # Collapsible Interface
    # -------------------------------------------------------------------------
    
    def collapse(self) -> 'Dimensional[T]':
        """
        Collapse back to POTENTIAL (level 0).
        
        Clears materialization cache.
        Returns self for chaining.
        """
        with self._lock:
            self._level = 0
            self._materialization_cache.clear()
            self._completed = False
        return self
    
    # -------------------------------------------------------------------------
    # Spiral Navigation
    # -------------------------------------------------------------------------
    
    def spiral_up(self) -> 'Dimensional[T]':
        """
        Move to next spiral (requires level=6).
        
        Transition: (s, 6) -> (s+1, 0)
        """
        if self._level != 6:
            raise RuntimeError(f"SPIRAL_UP requires level 6, currently at {self._level}")
        
        with self._lock:
            self._spiral += 1
            self._level = 0
            self._materialization_cache.clear()
        return self
    
    def spiral_down(self) -> 'Dimensional[T]':
        """
        Move to previous spiral (requires level=0).
        
        Transition: (s, 0) -> (s-1, 6)
        """
        if self._level != 0:
            raise RuntimeError(f"SPIRAL_DOWN requires level 0, currently at {self._level}")
        
        with self._lock:
            self._spiral -= 1
            self._level = 6
            self._materialization_cache.clear()
        return self
    
    # -------------------------------------------------------------------------
    # Observer Pattern
    # -------------------------------------------------------------------------
    
    def observe(self, callback: Callable[[int, int, Any], None]) -> None:
        """
        Add an observer that's called on invoke.
        
        Callback receives: (old_level, new_level, value)
        """
        self._observers.add(callback)
    
    def unobserve(self, callback: Callable) -> bool:
        """Remove an observer."""
        try:
            self._observers.discard(callback)
            return True
        except KeyError:
            return False
    
    def _notify_observers(self, old_level: int, new_level: int, value: Any) -> None:
        """Notify all observers of a level change."""
        for callback in self._observers:
            try:
                callback(old_level, new_level, value)
            except Exception:
                pass
    
    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            '_type': type(self).__name__,
            'id': self._id,
            'spiral': self._spiral,
            'level': self._level,
            'payload': self._payload,
            'completed': self._completed,
            'metadata': self._metadata,
        }
    
    @classmethod
    def from_dict(cls: Type[S], data: Dict[str, Any]) -> S:
        """Reconstruct from dictionary."""
        obj = cls(
            payload=data.get('payload'),
            level=data.get('level', 0),
            spiral=data.get('spiral', 0),
            metadata=data.get('metadata', {}),
            auto_complete=False
        )
        obj._id = data.get('id', obj._id)
        obj._completed = data.get('completed', False)
        return obj
    
    # -------------------------------------------------------------------------
    # String Representation
    # -------------------------------------------------------------------------
    
    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.state}, payload={self._payload!r})"
    
    def __str__(self) -> str:
        return f"{type(self).__name__}{self.state}"


# =============================================================================
# DIMENSIONAL INTERFACE (Generic Interface Pattern)
# =============================================================================

class DimensionalInterface(Generic[T], ABC):
    """
    Abstract interface for dimensional types.
    
    Every dimensional interface:
        - Defines what invoke() returns at each level
        - Supports generic type parameters
        - Can be composed with other interfaces
        - Is instantiated at runtime via factory
    
    This is the "interface" pattern - define the contract,
    implementation comes from the factory.
    """
    
    @abstractmethod
    def invoke(self, level: int) -> InvokeResult[T]:
        """The core invoke operation."""
        ...
    
    @abstractmethod
    def _materialize(self, level: int) -> T:
        """What this interface produces at each level."""
        ...
    
    @classmethod
    def __subclasshook__(cls, C):
        """Check if a class implements this interface."""
        if cls is DimensionalInterface:
            return (
                hasattr(C, 'invoke') and callable(getattr(C, 'invoke'))
            )
        return NotImplemented


# =============================================================================
# DIMENSIONAL FACTORY (Runtime Instantiation)
# =============================================================================

class DimensionalFactory(Generic[T]):
    """
    Factory for runtime instantiation of dimensional objects.
    
    Features:
        - Type registration
        - Generic instantiation
        - Lazy initialization
        - Pooled instances
        - Configuration injection
    
    Example:
        factory = DimensionalFactory[MyData]()
        factory.register('mydata', MyData)
        obj = factory.create('mydata', payload={'x': 1})
    """
    
    def __init__(self):
        self._registry: Dict[str, Type[Dimensional]] = {}
        self._pool: Dict[str, List[Dimensional]] = {}
        self._config: Dict[str, Any] = {}
        self._lock = RLock()
    
    def register(
        self,
        name: str,
        cls: Type[Dimensional],
        *,
        pool_size: int = 0
    ) -> 'DimensionalFactory[T]':
        """
        Register a type for instantiation.
        
        Args:
            name: Type name for lookup
            cls: The Dimensional subclass
            pool_size: Pre-create this many instances
        """
        with self._lock:
            self._registry[name] = cls
            
            if pool_size > 0:
                self._pool[name] = [cls(auto_complete=False) for _ in range(pool_size)]
        
        return self
    
    def create(
        self,
        name: str,
        payload: Any = None,
        *,
        auto_complete: bool = True,
        **kwargs
    ) -> Dimensional[T]:
        """
        Instantiate a registered type at runtime.
        
        Checks pool first, creates new if needed.
        """
        with self._lock:
            if name not in self._registry:
                raise KeyError(f"Type not registered: {name}")
            
            # Try pool first
            if name in self._pool and self._pool[name]:
                obj = self._pool[name].pop()
                obj._payload = payload
                for k, v in kwargs.items():
                    if hasattr(obj, f'_{k}'):
                        setattr(obj, f'_{k}', v)
                if auto_complete:
                    obj.complete()
                return obj
            
            # Create new
            cls = self._registry[name]
            return cls(payload, auto_complete=auto_complete, **kwargs)
    
    def release(self, obj: Dimensional) -> None:
        """Return an object to the pool."""
        name = type(obj).__name__.lower()
        with self._lock:
            if name in self._pool:
                obj.collapse()
                self._pool[name].append(obj)
    
    def configure(self, config: Dict[str, Any]) -> 'DimensionalFactory[T]':
        """Set configuration for factory."""
        self._config.update(config)
        return self


# =============================================================================
# AUTO-COMPLETING DIMENSIONAL
# =============================================================================

class AutoDimensional(Dimensional[T]):
    """
    Dimensional subclass that auto-completes on construction.
    
    Use this when you want objects to be fully materialized at creation.
    """
    _auto_complete: ClassVar[bool] = True


# =============================================================================
# DIMENSIONAL VALUE (Simple Wrapper)
# =============================================================================

class DimensionalValue(Dimensional[T]):
    """
    Simple dimensional wrapper for any value.
    
    Each level progressively reveals more information:
        0: Type hint
        1: Existence (True/False)
        2: String representation
        3: Type name
        4: Full repr
        5: Dict representation (if applicable)
        6: The actual value
    """
    
    def _materialize(self, level: int) -> Any:
        """Progressive revelation of value."""
        v = self._payload
        
        if level == 0:
            return type(v).__name__ if v is not None else "None"
        elif level == 1:
            return v is not None
        elif level == 2:
            return str(v) if v is not None else "None"
        elif level == 3:
            return f"{type(v).__module__}.{type(v).__name__}"
        elif level == 4:
            return repr(v)
        elif level == 5:
            if hasattr(v, '__dict__'):
                return v.__dict__
            elif isinstance(v, dict):
                return v
            return {'value': v}
        else:  # level 6
            return v


# =============================================================================
# DIMENSIONAL LIST
# =============================================================================

class DimensionalList(Dimensional[List[T]]):
    """
    Dimensional wrapper for lists.
    
    Each level reveals more elements:
        0: Empty list
        1: First element
        2: First 2 elements
        ...
        6: All elements
    """
    
    def __init__(self, items: List[T] = None, **kwargs):
        super().__init__(items or [], **kwargs)
    
    def _materialize(self, level: int) -> List[T]:
        """Reveal elements based on level."""
        items = self._payload
        if level == 0:
            return []
        elif level == 6:
            return items
        else:
            # Progressive reveal: level 1 = 1 item, level 2 = 2 items, etc.
            # Up to level 5 = 5 items, level 6 = all
            count = min(level, len(items))
            return items[:count]
    
    def append(self, item: T) -> 'DimensionalList[T]':
        """Add an item (invalidates cache)."""
        self._payload.append(item)
        self._materialization_cache.clear()
        return self
    
    def __len__(self) -> int:
        return len(self._payload)
    
    def __iter__(self) -> Iterator[T]:
        return iter(self._payload)


# =============================================================================
# DIMENSIONAL DICT
# =============================================================================

class DimensionalDict(Dimensional[Dict[str, V]]):
    """
    Dimensional wrapper for dictionaries.
    
    Each level reveals more detail:
        0: Empty dict
        1: Keys only
        2: Key count
        3: Key-value types
        4: First few items
        5: Most items
        6: All items
    """
    
    def __init__(self, data: Dict[str, V] = None, **kwargs):
        super().__init__(data or {}, **kwargs)
    
    def _materialize(self, level: int) -> Any:
        """Reveal dict based on level."""
        d = self._payload
        
        if level == 0:
            return {}
        elif level == 1:
            return list(d.keys())
        elif level == 2:
            return len(d)
        elif level == 3:
            return {k: type(v).__name__ for k, v in d.items()}
        elif level == 4:
            items = list(d.items())[:3]
            return dict(items)
        elif level == 5:
            items = list(d.items())[:-1] if len(d) > 1 else list(d.items())
            return dict(items)
        else:  # level 6
            return d
    
    def __getitem__(self, key: str) -> V:
        return self._payload[key]
    
    def __setitem__(self, key: str, value: V) -> None:
        self._payload[key] = value
        self._materialization_cache.clear()
    
    def __contains__(self, key: str) -> bool:
        return key in self._payload


# =============================================================================
# DIMENSIONAL DECORATOR
# =============================================================================

def dimensional(cls: Type[T] = None, *, auto_complete: bool = False, level: int = 0):
    """
    Class decorator to make any class dimensional.
    
    Adds invoke(), complete(), collapse() methods.
    
    Example:
        @dimensional(auto_complete=True)
        class MyClass:
            def __init__(self, data):
                self.data = data
    """
    def decorator(cls: Type[T]) -> Type[T]:
        # Store original __init__
        original_init = cls.__init__
        
        def new_init(self, *args, **kwargs):
            # Initialize dimensional state
            self._d_spiral = 0
            self._d_level = level
            self._d_completed = False
            self._d_cache = {}
            
            # Call original init
            original_init(self, *args, **kwargs)
            
            # Auto-complete if enabled
            if auto_complete:
                self.complete()
        
        def invoke(self, level: int) -> Any:
            """Invoke to level."""
            if not 0 <= level <= 6:
                raise ValueError(f"Level must be 0-6, got {level}")
            
            self._d_level = level
            
            if hasattr(self, '_materialize'):
                return self._materialize(level)
            return self
        
        def complete(self):
            """Complete to level 6."""
            self.invoke(6)
            self._d_completed = True
            return self
        
        def collapse(self):
            """Collapse to level 0."""
            self._d_level = 0
            self._d_completed = False
            self._d_cache.clear()
            return self
        
        @property
        def state(self):
            """Dimensional state."""
            return DimensionalState(self._d_spiral, self._d_level)
        
        @property
        def is_complete(self):
            return self._d_completed
        
        # Attach methods
        cls.__init__ = new_init
        cls.invoke = invoke
        cls.complete = complete
        cls.collapse = collapse
        cls.state = state
        cls.is_complete = is_complete
        
        # Mark as dimensional
        cls._is_dimensional = True
        
        return cls
    
    if cls is not None:
        return decorator(cls)
    return decorator


# =============================================================================
# GENERIC INTERFACE GENERATOR
# =============================================================================

def interface(
    *type_vars: TypeVar,
    methods: Optional[List[str]] = None
) -> Type[Protocol]:
    """
    Generate a generic interface protocol.
    
    Example:
        MyInterface = interface(T, U, methods=['process', 'transform'])
        
        class Impl(MyInterface[int, str]):
            def process(self, x: int) -> str: ...
            def transform(self, x: int) -> str: ...
    """
    # Build method stubs
    method_stubs = {}
    for method_name in (methods or ['invoke']):
        def method_stub(self, *args, **kwargs) -> Any:
            ...
        method_stubs[method_name] = method_stub
    
    # Create protocol class
    if len(type_vars) == 0:
        base = Protocol
    elif len(type_vars) == 1:
        base = Protocol[type_vars[0]]
    else:
        base = Protocol[tuple(type_vars)]
    
    interface_cls = type('GeneratedInterface', (base,), method_stubs)
    interface_cls = runtime_checkable(interface_cls)
    
    return interface_cls


# =============================================================================
# COMPOSE MULTIPLE INTERFACES
# =============================================================================

def compose(*interfaces: Type) -> Type:
    """
    Compose multiple interfaces into one.
    
    Example:
        Combined = compose(Invokable, Completable, Collapsible)
    """
    
    class ComposedInterface(*interfaces):
        pass
    
    return ComposedInterface


# =============================================================================
# GLOBAL FACTORY INSTANCE
# =============================================================================

# Default factory for convenience
_global_factory: DimensionalFactory = DimensionalFactory()


def register(name: str, cls: Type[Dimensional]) -> None:
    """Register a type with the global factory."""
    _global_factory.register(name, cls)


def create(name: str, payload: Any = None, **kwargs) -> Dimensional:
    """Create an instance using the global factory."""
    return _global_factory.create(name, payload, **kwargs)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def dim(value: T, *, complete: bool = True) -> Dimensional[T]:
    """
    Wrap any value in a Dimensional.
    
    Example:
        d = dim([1, 2, 3])
        d.invoke(3)  # Get representation at level 3
    """
    obj = DimensionalValue(value, auto_complete=False)
    if complete:
        obj.complete()
    return obj


def dimlist(items: List[T] = None, *, complete: bool = True) -> DimensionalList[T]:
    """Create a dimensional list."""
    obj = DimensionalList(items or [], auto_complete=False)
    if complete:
        obj.complete()
    return obj


def dimdict(data: Dict[str, V] = None, *, complete: bool = True) -> DimensionalDict[V]:
    """Create a dimensional dict."""
    obj = DimensionalDict(data or {}, auto_complete=False)
    if complete:
        obj.complete()
    return obj


# =============================================================================
# SRL INTEGRATION
# =============================================================================

def srl(spiral: int, level: int, path: str = '') -> str:
    """Create an SRL reference."""
    return f"srl://{spiral}.{level}/{path}"


def invoke_srl(obj: Dimensional, srl_ref: str) -> Any:
    """
    Invoke an object using an SRL reference.
    
    Example:
        result = invoke_srl(obj, "srl://0.3/data")
    """
    if not srl_ref.startswith('srl://'):
        raise ValueError(f"Invalid SRL: {srl_ref}")
    
    # Parse: srl://spiral.level/path
    rest = srl_ref[6:]  # Remove 'srl://'
    
    if '/' in rest:
        state_part, path = rest.split('/', 1)
    else:
        state_part, path = rest, ''
    
    parts = state_part.split('.')
    spiral = int(parts[0])
    level = int(parts[1]) if len(parts) > 1 else 6
    
    # Navigate to spiral if needed
    while obj.spiral < spiral:
        obj.invoke(6).value
        obj.spiral_up()
    while obj.spiral > spiral:
        obj.invoke(0).value
        obj.spiral_down()
    
    # Invoke to level
    result = obj.invoke(level)
    
    # If path specified, navigate into result
    if path and isinstance(result.value, dict):
        for key in path.split('/'):
            if key:
                result = InvokeResult(
                    value=result.value.get(key),
                    state=result.state,
                    source=f"{result.source}/{key}",
                    cached=False
                )
    
    return result


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # State
    'Level',
    'LEVEL_NAMES',
    'DimensionalState',
    'InvokeResult',
    
    # Protocols
    'Invokable',
    'Completable',
    'Collapsible',
    
    # Base Classes
    'Dimensional',
    'AutoDimensional',
    'DimensionalInterface',
    
    # Concrete Types
    'DimensionalValue',
    'DimensionalList',
    'DimensionalDict',
    
    # Factory
    'DimensionalFactory',
    'register',
    'create',
    
    # Decorator
    'dimensional',
    
    # Interface Generation
    'interface',
    'compose',
    
    # Convenience
    'dim',
    'dimlist',
    'dimdict',
    
    # SRL
    'srl',
    'invoke_srl',
]
