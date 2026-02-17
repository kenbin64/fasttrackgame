"""
Dimensional Primitives - Atomic Building Blocks for ButterflyFX

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)

DEFINITION: A primitive is an atomic lens or substrate needed in most/all conditions.
These are the irreducible building blocks from which all larger structures emerge.

PRIMITIVES vs ADD-ONS:
    PRIMITIVES (this module):
        - Atomic, universally needed
        - Keep kernel pure and pristine
        - Zero overhead for unused features
        - Part of the core product
        
    ADD-ONS (separate modules):
        - Lightweight, app-specific
        - Not universally needed
        - Marketable extensions
        - Developer ecosystem opportunity

CATEGORIES:
    1. Dimensional Operations - creation, ingestion, traversal
    2. Collections (no iteration) - lists, sets, maps, queues, stacks
    3. Functional - lambdas, streams, composition
    4. Concurrency - threads, async, anti-race
    5. Validation - type checking, constraints
    6. Math Expressions - operations, formulas
    7. Sensory - color, sound, light, pixels
"""

from __future__ import annotations
from typing import (
    Any, Callable, Dict, Generic, Iterator, List, 
    Optional, Set, Tuple, TypeVar, Union
)
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import reduce
import threading
import asyncio
import math
import time


# =============================================================================
# TYPE VARIABLES
# =============================================================================

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')
A = TypeVar('A')
B = TypeVar('B')


# =============================================================================
# 1. DIMENSIONAL OPERATIONS - Creation, Ingestion, Traversal
# =============================================================================

class Level(Enum):
    """The 7 levels of dimensional existence."""
    VOID = 0      # Nothing - pure potential
    POINT = 1     # Singularity - identity
    LINE = 2      # Connection - relationship  
    WIDTH = 3     # Surface - boundary
    PLANE = 4     # Area - context
    VOLUME = 5    # Space - manifestation
    WHOLE = 6     # Complete - integration


@dataclass
class Dimension:
    """
    A dimension is a substrate with a level.
    
    The address IS the location (O(1) access).
    No iteration needed - dimensions are addressed directly.
    """
    level: Level
    spiral: int = 0
    value: Any = None
    _children: Dict[str, 'Dimension'] = field(default_factory=dict, repr=False)
    
    @property
    def address(self) -> str:
        """Unique address for this dimension."""
        return f"{self.spiral}.{self.level.value}"
    
    def at(self, key: str) -> 'Dimension':
        """Access child dimension directly (O(1))."""
        if key not in self._children:
            # Auto-create child dimension at same level
            self._children[key] = Dimension(level=self.level, spiral=self.spiral)
        return self._children[key]
    
    def up(self) -> 'Dimension':
        """Move up one level."""
        if self.level.value < 6:
            return Dimension(
                level=Level(self.level.value + 1),
                spiral=self.spiral,
                value=self.value
            )
        return self
    
    def down(self) -> 'Dimension':
        """Move down one level."""
        if self.level.value > 0:
            return Dimension(
                level=Level(self.level.value - 1),
                spiral=self.spiral,
                value=self.value
            )
        return self
    
    def next_spiral(self) -> 'Dimension':
        """Move to next spiral (Fibonacci progression)."""
        return Dimension(
            level=self.level,
            spiral=self.spiral + 1,
            value=self.value
        )


def ingest(what: Any, level: Level = Level.WHOLE) -> Dimension:
    """
    Ingest anything into a dimension.
    
    This is the primary creation primitive - taking raw input
    and placing it naturally on the substrate.
    
    Usage:
        car = ingest("Car")
        data = ingest({"x": 1, "y": 2}, Level.PLANE)
    """
    return Dimension(level=level, value=what)


def traverse(dim: Dimension, path: str) -> Dimension:
    """
    Traverse dimensions by path (O(1) for each segment).
    
    Path format: "key1.key2.key3"
    
    NO ITERATION - direct addressing at each level.
    """
    current = dim
    for key in path.split('.'):
        current = current.at(key)
    return current


# =============================================================================
# 2. COLLECTIONS WITHOUT ITERATION
# =============================================================================

@dataclass
class DList(Generic[T]):
    """
    Dimensional List - O(1) access, no iteration needed.
    
    Uses dimensional addressing instead of index iteration.
    The address IS the position.
    """
    _data: Dict[int, T] = field(default_factory=dict)
    _size: int = 0
    
    def put(self, index: int, value: T) -> 'DList[T]':
        """Put value at index (O(1))."""
        self._data[index] = value
        if index >= self._size:
            self._size = index + 1
        return self
    
    def get(self, index: int, default: T = None) -> T:
        """Get value at index (O(1))."""
        return self._data.get(index, default)
    
    def append(self, value: T) -> 'DList[T]':
        """Append value."""
        self._data[self._size] = value
        self._size += 1
        return self
    
    @property
    def size(self) -> int:
        return self._size
    
    def map(self, fn: Callable[[T], A]) -> 'DList[A]':
        """Apply function to all elements (creates new list)."""
        result = DList[A]()
        result._data = {k: fn(v) for k, v in self._data.items()}
        result._size = self._size
        return result
    
    def filter(self, pred: Callable[[T], bool]) -> 'DList[T]':
        """Filter elements by predicate."""
        result = DList[T]()
        for k, v in self._data.items():
            if pred(v):
                result.append(v)
        return result
    
    def reduce(self, fn: Callable[[A, T], A], initial: A) -> A:
        """Reduce to single value."""
        acc = initial
        for i in range(self._size):
            if i in self._data:
                acc = fn(acc, self._data[i])
        return acc
    
    def slice(self, start: int, end: int) -> 'DList[T]':
        """Get slice (O(n) for n items in slice, not whole list)."""
        result = DList[T]()
        for i in range(start, min(end, self._size)):
            if i in self._data:
                result.append(self._data[i])
        return result


@dataclass
class DSet(Generic[T]):
    """
    Dimensional Set - Using actual set theory.
    
    Operations are mathematical set operations.
    """
    _data: Set[T] = field(default_factory=set)
    
    def add(self, value: T) -> 'DSet[T]':
        """Add element."""
        self._data.add(value)
        return self
    
    def remove(self, value: T) -> 'DSet[T]':
        """Remove element."""
        self._data.discard(value)
        return self
    
    def contains(self, value: T) -> bool:
        """Check membership (O(1))."""
        return value in self._data
    
    @property
    def cardinality(self) -> int:
        """Set size."""
        return len(self._data)
    
    # Set Theory Operations
    
    def union(self, other: 'DSet[T]') -> 'DSet[T]':
        """A ∪ B - elements in either set."""
        result = DSet[T]()
        result._data = self._data | other._data
        return result
    
    def intersection(self, other: 'DSet[T]') -> 'DSet[T]':
        """A ∩ B - elements in both sets."""
        result = DSet[T]()
        result._data = self._data & other._data
        return result
    
    def difference(self, other: 'DSet[T]') -> 'DSet[T]':
        """A - B - elements in A but not B."""
        result = DSet[T]()
        result._data = self._data - other._data
        return result
    
    def symmetric_difference(self, other: 'DSet[T]') -> 'DSet[T]':
        """A △ B - elements in exactly one set."""
        result = DSet[T]()
        result._data = self._data ^ other._data
        return result
    
    def is_subset(self, other: 'DSet[T]') -> bool:
        """A ⊆ B - all elements of A in B."""
        return self._data <= other._data
    
    def is_superset(self, other: 'DSet[T]') -> bool:
        """A ⊇ B - all elements of B in A."""
        return self._data >= other._data
    
    def is_disjoint(self, other: 'DSet[T]') -> bool:
        """A ∩ B = ∅ - no common elements."""
        return self._data.isdisjoint(other._data)
    
    def power_set(self) -> 'DSet[frozenset]':
        """P(A) - set of all subsets."""
        from itertools import combinations
        result = DSet[frozenset]()
        data_list = list(self._data)
        for r in range(len(data_list) + 1):
            for subset in combinations(data_list, r):
                result.add(frozenset(subset))
        return result


@dataclass
class DMap(Generic[K, V]):
    """
    Dimensional Map - O(1) key-value access.
    
    Keys are addresses, values are at those addresses.
    """
    _data: Dict[K, V] = field(default_factory=dict)
    
    def put(self, key: K, value: V) -> 'DMap[K, V]':
        """Put key-value pair."""
        self._data[key] = value
        return self
    
    def get(self, key: K, default: V = None) -> V:
        """Get value by key (O(1))."""
        return self._data.get(key, default)
    
    def has(self, key: K) -> bool:
        """Check key exists."""
        return key in self._data
    
    def remove(self, key: K) -> 'DMap[K, V]':
        """Remove key."""
        if key in self._data:
            del self._data[key]
        return self
    
    def keys(self) -> DSet[K]:
        """Get all keys as DSet."""
        result = DSet[K]()
        result._data = set(self._data.keys())
        return result
    
    def values(self) -> DList[V]:
        """Get all values as DList."""
        result = DList[V]()
        for v in self._data.values():
            result.append(v)
        return result
    
    def map_values(self, fn: Callable[[V], A]) -> 'DMap[K, A]':
        """Transform all values."""
        result = DMap[K, A]()
        result._data = {k: fn(v) for k, v in self._data.items()}
        return result
    
    def filter(self, pred: Callable[[K, V], bool]) -> 'DMap[K, V]':
        """Filter entries."""
        result = DMap[K, V]()
        result._data = {k: v for k, v in self._data.items() if pred(k, v)}
        return result
    
    def merge(self, other: 'DMap[K, V]') -> 'DMap[K, V]':
        """Merge two maps."""
        result = DMap[K, V]()
        result._data = {**self._data, **other._data}
        return result


@dataclass
class DHash(Generic[K, V]):
    """
    Dimensional Hash - Consistent hashing for distributed data.
    
    Values are placed at their natural position on the substrate.
    """
    _data: Dict[int, List[Tuple[K, V]]] = field(default_factory=dict)
    _buckets: int = 256
    
    def _hash(self, key: K) -> int:
        """Hash key to bucket."""
        return hash(key) % self._buckets
    
    def put(self, key: K, value: V) -> 'DHash[K, V]':
        """Put key-value pair."""
        bucket = self._hash(key)
        if bucket not in self._data:
            self._data[bucket] = []
        # Update or append
        for i, (k, v) in enumerate(self._data[bucket]):
            if k == key:
                self._data[bucket][i] = (key, value)
                return self
        self._data[bucket].append((key, value))
        return self
    
    def get(self, key: K, default: V = None) -> V:
        """Get value by key (O(1) average)."""
        bucket = self._hash(key)
        if bucket in self._data:
            for k, v in self._data[bucket]:
                if k == key:
                    return v
        return default


@dataclass
class DQueue(Generic[T]):
    """
    Dimensional Queue - FIFO without iteration.
    
    Head and tail are addressed directly.
    """
    _data: Dict[int, T] = field(default_factory=dict)
    _head: int = 0
    _tail: int = 0
    
    def enqueue(self, value: T) -> 'DQueue[T]':
        """Add to end."""
        self._data[self._tail] = value
        self._tail += 1
        return self
    
    def dequeue(self) -> T:
        """Remove from front."""
        if self.is_empty:
            raise IndexError("Queue is empty")
        value = self._data.pop(self._head)
        self._head += 1
        return value
    
    def peek(self) -> T:
        """Look at front without removing."""
        if self.is_empty:
            raise IndexError("Queue is empty")
        return self._data[self._head]
    
    @property
    def size(self) -> int:
        return self._tail - self._head
    
    @property
    def is_empty(self) -> bool:
        return self._head >= self._tail


@dataclass
class DStack(Generic[T]):
    """
    Dimensional Stack - LIFO without iteration.
    
    Top is addressed directly.
    """
    _data: List[T] = field(default_factory=list)
    
    def push(self, value: T) -> 'DStack[T]':
        """Push onto stack."""
        self._data.append(value)
        return self
    
    def pop(self) -> T:
        """Pop from stack."""
        if self.is_empty:
            raise IndexError("Stack is empty")
        return self._data.pop()
    
    def peek(self) -> T:
        """Look at top without removing."""
        if self.is_empty:
            raise IndexError("Stack is empty")
        return self._data[-1]
    
    @property
    def size(self) -> int:
        return len(self._data)
    
    @property
    def is_empty(self) -> bool:
        return len(self._data) == 0


@dataclass
class DLinkedNode(Generic[T]):
    """Node in a dimensional linked list."""
    value: T
    next: Optional['DLinkedNode[T]'] = None
    prev: Optional['DLinkedNode[T]'] = None


@dataclass
class DLinkedList(Generic[T]):
    """
    Dimensional Linked List - Traversal without iteration.
    
    Each node knows its neighbors (dimensional adjacency).
    """
    head: Optional[DLinkedNode[T]] = None
    tail: Optional[DLinkedNode[T]] = None
    _size: int = 0
    
    def append(self, value: T) -> 'DLinkedList[T]':
        """Add to end."""
        node = DLinkedNode(value)
        if self.tail is None:
            self.head = self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        self._size += 1
        return self
    
    def prepend(self, value: T) -> 'DLinkedList[T]':
        """Add to beginning."""
        node = DLinkedNode(value)
        if self.head is None:
            self.head = self.tail = node
        else:
            node.next = self.head
            self.head.prev = node
            self.head = node
        self._size += 1
        return self
    
    def at(self, index: int) -> Optional[T]:
        """Access by index (O(n) but direct traversal)."""
        if index < 0 or index >= self._size:
            return None
        # Traverse from closer end
        if index < self._size // 2:
            node = self.head
            for _ in range(index):
                node = node.next
        else:
            node = self.tail
            for _ in range(self._size - 1 - index):
                node = node.prev
        return node.value if node else None
    
    @property
    def size(self) -> int:
        return self._size


# =============================================================================
# 3. FUNCTIONAL PRIMITIVES - Lambdas, Streams, Composition
# =============================================================================

@dataclass
class DLambda(Generic[A, B]):
    """
    Dimensional Lambda - First-class function with metadata.
    
    Functions are values that can be composed, curried, and cached.
    """
    fn: Callable[[A], B]
    name: str = "lambda"
    _cache: Dict[Any, B] = field(default_factory=dict, repr=False)
    memoize: bool = False
    
    def __call__(self, arg: A) -> B:
        """Apply the lambda."""
        if self.memoize:
            key = str(arg)
            if key not in self._cache:
                self._cache[key] = self.fn(arg)
            return self._cache[key]
        return self.fn(arg)
    
    def compose(self, other: 'DLambda[B, Any]') -> 'DLambda[A, Any]':
        """f.compose(g) = g(f(x))"""
        return DLambda(
            fn=lambda x: other(self(x)),
            name=f"{other.name}∘{self.name}"
        )
    
    def and_then(self, other: 'DLambda[B, Any]') -> 'DLambda[A, Any]':
        """f.and_then(g) = g(f(x)) - alias for compose"""
        return self.compose(other)
    
    def map(self, fn: Callable[[B], Any]) -> 'DLambda[A, Any]':
        """Transform the output."""
        return DLambda(
            fn=lambda x: fn(self(x)),
            name=f"map({self.name})"
        )


def curry(fn: Callable) -> Callable:
    """
    Curry a function for partial application.
    
    Usage:
        @curry
        def add(a, b, c):
            return a + b + c
        
        add(1)(2)(3)  # => 6
        add(1, 2)(3)  # => 6
    """
    import inspect
    sig = inspect.signature(fn)
    param_count = len(sig.parameters)
    
    def curried(*args):
        if len(args) >= param_count:
            return fn(*args[:param_count])
        return lambda *more: curried(*args, *more)
    
    return curried


@dataclass
class DStream(Generic[T]):
    """
    Dimensional Stream - Lazy sequence of values.
    
    Operations are deferred until terminal operation.
    """
    
    def __init__(self, source: Callable[[], Iterator[T]], operations: List[Tuple] = None):
        self.source = source
        self.operations = operations if operations is not None else []
    
    @classmethod
    def of(cls, *values: T) -> 'DStream[T]':
        """Create stream from values."""
        return cls(source=lambda: iter(values))
    
    @classmethod
    def from_list(cls, lst: DList[T]) -> 'DStream[T]':
        """Create stream from DList."""
        return cls(source=lambda: (lst.get(i) for i in range(lst.size)))
    
    @classmethod
    def generate(cls, fn: Callable[[int], T], count: int) -> 'DStream[T]':
        """Generate stream from function."""
        return cls(source=lambda: (fn(i) for i in range(count)))
    
    @classmethod
    def infinite(cls, fn: Callable[[int], T]) -> 'DStream[T]':
        """Create infinite stream (use .take() to limit)."""
        def gen():
            i = 0
            while True:
                yield fn(i)
                i += 1
        return cls(source=gen)
    
    def map(self, fn: Callable[[T], A]) -> 'DStream[A]':
        """Map values (lazy)."""
        new_ops = list(self.operations) + [('map', fn)]
        return DStream[A](source=self.source, operations=new_ops)
    
    def filter(self, pred: Callable[[T], bool]) -> 'DStream[T]':
        """Filter values (lazy)."""
        new_ops = list(self.operations) + [('filter', pred)]
        return DStream[T](source=self.source, operations=new_ops)
    
    def take(self, n: int) -> 'DStream[T]':
        """Take first n values (lazy)."""
        new_ops = list(self.operations) + [('take', n)]
        return DStream[T](source=self.source, operations=new_ops)
    
    def skip(self, n: int) -> 'DStream[T]':
        """Skip first n values (lazy)."""
        new_ops = list(self.operations) + [('skip', n)]
        return DStream[T](source=self.source, operations=new_ops)
    
    # Terminal Operations
    
    def collect(self) -> DList[T]:
        """Collect to DList (terminal)."""
        result = DList[T]()
        for item in self._execute():
            result.append(item)
        return result
    
    def reduce(self, fn: Callable[[A, T], A], initial: A) -> A:
        """Reduce to single value (terminal)."""
        acc = initial
        for item in self._execute():
            acc = fn(acc, item)
        return acc
    
    def count(self) -> int:
        """Count elements (terminal)."""
        return sum(1 for _ in self._execute())
    
    def first(self) -> Optional[T]:
        """Get first element (terminal)."""
        for item in self._execute():
            return item
        return None
    
    def _execute(self) -> Iterator:
        """Execute the stream pipeline."""
        # Convert to list first to avoid generator exhaustion issues
        current = list(self.source())
        
        for op_type, op_arg in self.operations:
            if op_type == 'map':
                current = [op_arg(x) for x in current]
            elif op_type == 'filter':
                current = [x for x in current if op_arg(x)]
            elif op_type == 'take':
                current = current[:op_arg]
            elif op_type == 'skip':
                current = current[op_arg:]
        
        return iter(current)


# =============================================================================
# 4. CONCURRENCY PRIMITIVES - Threads, Async, Anti-Race
# =============================================================================

@dataclass
class DAtomic(Generic[T]):
    """
    Dimensional Atomic - Thread-safe value with atomic operations.
    
    Anti-race condition primitive.
    """
    _value: T
    _lock: threading.RLock = field(default_factory=threading.RLock, repr=False)
    
    def get(self) -> T:
        """Get value atomically."""
        with self._lock:
            return self._value
    
    def set(self, value: T) -> None:
        """Set value atomically."""
        with self._lock:
            self._value = value
    
    def update(self, fn: Callable[[T], T]) -> T:
        """Update atomically and return new value."""
        with self._lock:
            self._value = fn(self._value)
            return self._value
    
    def compare_and_set(self, expected: T, new_value: T) -> bool:
        """Set only if current value equals expected."""
        with self._lock:
            if self._value == expected:
                self._value = new_value
                return True
            return False


@dataclass
class DMutex:
    """
    Dimensional Mutex - Mutual exclusion lock.
    
    Ensures only one thread accesses a resource.
    """
    _lock: threading.RLock = field(default_factory=threading.RLock, repr=False)
    _owner: Optional[int] = field(default=None, repr=False)
    
    def acquire(self) -> None:
        """Acquire lock."""
        self._lock.acquire()
        self._owner = threading.get_ident()
    
    def release(self) -> None:
        """Release lock."""
        self._owner = None
        self._lock.release()
    
    def __enter__(self):
        self.acquire()
        return self
    
    def __exit__(self, *args):
        self.release()
    
    @property
    def is_locked(self) -> bool:
        """Check if locked."""
        return self._owner is not None


@dataclass
class DSemaphore:
    """
    Dimensional Semaphore - Limit concurrent access.
    """
    _sem: threading.Semaphore = field(default=None, repr=False)
    permits: int = 1
    
    def __post_init__(self):
        self._sem = threading.Semaphore(self.permits)
    
    def acquire(self) -> None:
        self._sem.acquire()
    
    def release(self) -> None:
        self._sem.release()
    
    def __enter__(self):
        self.acquire()
        return self
    
    def __exit__(self, *args):
        self.release()


@dataclass
class DChannel(Generic[T]):
    """
    Dimensional Channel - Thread-safe communication.
    
    Send/receive between threads without races.
    """
    _queue: 'asyncio.Queue[T]' = field(default=None, repr=False)
    capacity: int = 0  # 0 = unbounded
    
    def __post_init__(self):
        if self.capacity > 0:
            self._queue = asyncio.Queue(maxsize=self.capacity)
        else:
            self._queue = asyncio.Queue()
    
    async def send(self, value: T) -> None:
        """Send value to channel."""
        await self._queue.put(value)
    
    async def receive(self) -> T:
        """Receive value from channel."""
        return await self._queue.get()
    
    def send_sync(self, value: T) -> None:
        """Synchronous send (blocking)."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.send(value))
    
    @property
    def is_empty(self) -> bool:
        return self._queue.empty()


class DFuture(Generic[T]):
    """
    Dimensional Future - Represents a value that will be available later.
    
    Async primitive for deferred computation.
    """
    
    def __init__(self, fn: Callable[[], T] = None):
        self._value: Optional[T] = None
        self._error: Optional[Exception] = None
        self._done = threading.Event()
        self._fn = fn
        
    def complete(self, value: T) -> None:
        """Complete the future with a value."""
        self._value = value
        self._done.set()
    
    def fail(self, error: Exception) -> None:
        """Fail the future with an error."""
        self._error = error
        self._done.set()
    
    def get(self, timeout: float = None) -> T:
        """Block until value is ready."""
        self._done.wait(timeout)
        if self._error:
            raise self._error
        return self._value
    
    def is_done(self) -> bool:
        """Check if future is complete."""
        return self._done.is_set()
    
    def map(self, fn: Callable[[T], A]) -> 'DFuture[A]':
        """Transform the result when ready."""
        result = DFuture[A]()
        
        def transform():
            try:
                value = self.get()
                result.complete(fn(value))
            except Exception as e:
                result.fail(e)
        
        threading.Thread(target=transform).start()
        return result
    
    @classmethod
    def run(cls, fn: Callable[[], T]) -> 'DFuture[T]':
        """Run function in background and return future."""
        future = cls()
        
        def execute():
            try:
                result = fn()
                future.complete(result)
            except Exception as e:
                future.fail(e)
        
        threading.Thread(target=execute).start()
        return future


async def parallel(*tasks: Callable[[], T]) -> List[T]:
    """
    Run tasks in parallel and collect results.
    
    Anti-race: all tasks complete independently.
    """
    async def wrap(fn):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, fn)
    
    results = await asyncio.gather(*[wrap(t) for t in tasks])
    return list(results)


# =============================================================================
# 5. VALIDATION PRIMITIVES
# =============================================================================

@dataclass
class DResult(Generic[T]):
    """
    Dimensional Result - Success or failure with value.
    
    Replaces exceptions with values.
    """
    _value: Optional[T] = None
    _error: Optional[str] = None
    
    @classmethod
    def ok(cls, value: T) -> 'DResult[T]':
        """Create success result."""
        return cls(_value=value)
    
    @classmethod
    def err(cls, error: str) -> 'DResult[T]':
        """Create error result."""
        return cls(_error=error)
    
    @property
    def is_ok(self) -> bool:
        return self._error is None
    
    @property
    def is_error(self) -> bool:
        return self._error is not None
    
    def unwrap(self) -> T:
        """Get value or raise."""
        if self._error:
            raise ValueError(self._error)
        return self._value
    
    def unwrap_or(self, default: T) -> T:
        """Get value or default."""
        return self._value if self.is_ok else default
    
    def map(self, fn: Callable[[T], A]) -> 'DResult[A]':
        """Transform success value."""
        if self.is_ok:
            try:
                return DResult.ok(fn(self._value))
            except Exception as e:
                return DResult.err(str(e))
        return DResult.err(self._error)
    
    def and_then(self, fn: Callable[[T], 'DResult[A]']) -> 'DResult[A]':
        """Chain operations that might fail."""
        if self.is_ok:
            try:
                return fn(self._value)
            except Exception as e:
                return DResult.err(str(e))
        return DResult.err(self._error)


@dataclass
class DOption(Generic[T]):
    """
    Dimensional Option - Maybe a value, maybe not.
    
    Replaces null checks with explicit optionality.
    """
    _value: Optional[T] = None
    _has_value: bool = False
    
    @classmethod
    def some(cls, value: T) -> 'DOption[T]':
        """Create option with value."""
        return cls(_value=value, _has_value=True)
    
    @classmethod
    def none(cls) -> 'DOption[T]':
        """Create empty option."""
        return cls(_has_value=False)
    
    @classmethod
    def from_nullable(cls, value: Optional[T]) -> 'DOption[T]':
        """Create from nullable value."""
        if value is None:
            return cls.none()
        return cls.some(value)
    
    @property
    def is_some(self) -> bool:
        return self._has_value
    
    @property
    def is_none(self) -> bool:
        return not self._has_value
    
    def unwrap(self) -> T:
        """Get value or raise."""
        if not self._has_value:
            raise ValueError("Option is None")
        return self._value
    
    def unwrap_or(self, default: T) -> T:
        """Get value or default."""
        return self._value if self._has_value else default
    
    def map(self, fn: Callable[[T], A]) -> 'DOption[A]':
        """Transform value if present."""
        if self._has_value:
            return DOption.some(fn(self._value))
        return DOption.none()
    
    def filter(self, pred: Callable[[T], bool]) -> 'DOption[T]':
        """Keep value only if predicate passes."""
        if self._has_value and pred(self._value):
            return self
        return DOption.none()


@dataclass
class DValidator(Generic[T]):
    """
    Dimensional Validator - Composable validation rules.
    """
    rules: List[Tuple[Callable[[T], bool], str]] = field(default_factory=list)
    
    def add_rule(self, check: Callable[[T], bool], message: str) -> 'DValidator[T]':
        """Add validation rule."""
        self.rules.append((check, message))
        return self
    
    def required(self, message: str = "Value is required") -> 'DValidator[T]':
        """Add required check."""
        return self.add_rule(lambda x: x is not None, message)
    
    def min_length(self, length: int, message: str = None) -> 'DValidator[T]':
        """Add minimum length check."""
        msg = message or f"Minimum length is {length}"
        return self.add_rule(lambda x: len(x) >= length, msg)
    
    def max_length(self, length: int, message: str = None) -> 'DValidator[T]':
        """Add maximum length check."""
        msg = message or f"Maximum length is {length}"
        return self.add_rule(lambda x: len(x) <= length, msg)
    
    def pattern(self, regex: str, message: str = "Invalid format") -> 'DValidator[T]':
        """Add regex pattern check."""
        import re
        return self.add_rule(lambda x: bool(re.match(regex, str(x))), message)
    
    def validate(self, value: T) -> DResult[T]:
        """Validate value against all rules."""
        errors = []
        for check, message in self.rules:
            try:
                if not check(value):
                    errors.append(message)
            except Exception as e:
                errors.append(f"{message}: {e}")
        
        if errors:
            return DResult.err("; ".join(errors))
        return DResult.ok(value)


# =============================================================================
# 6. MATH EXPRESSIONS
# =============================================================================

@dataclass
class DScalar:
    """
    Dimensional Scalar - A single numeric value with operations.
    """
    value: float
    
    def __add__(self, other: Union['DScalar', float]) -> 'DScalar':
        v = other.value if isinstance(other, DScalar) else other
        return DScalar(self.value + v)
    
    def __sub__(self, other: Union['DScalar', float]) -> 'DScalar':
        v = other.value if isinstance(other, DScalar) else other
        return DScalar(self.value - v)
    
    def __mul__(self, other: Union['DScalar', float]) -> 'DScalar':
        v = other.value if isinstance(other, DScalar) else other
        return DScalar(self.value * v)
    
    def __truediv__(self, other: Union['DScalar', float]) -> 'DScalar':
        v = other.value if isinstance(other, DScalar) else other
        return DScalar(self.value / v)
    
    def __pow__(self, other: Union['DScalar', float]) -> 'DScalar':
        v = other.value if isinstance(other, DScalar) else other
        return DScalar(self.value ** v)
    
    def sqrt(self) -> 'DScalar':
        return DScalar(math.sqrt(self.value))
    
    def abs(self) -> 'DScalar':
        return DScalar(abs(self.value))
    
    def sin(self) -> 'DScalar':
        return DScalar(math.sin(self.value))
    
    def cos(self) -> 'DScalar':
        return DScalar(math.cos(self.value))
    
    def tan(self) -> 'DScalar':
        return DScalar(math.tan(self.value))
    
    def log(self, base: float = math.e) -> 'DScalar':
        return DScalar(math.log(self.value, base))
    
    def exp(self) -> 'DScalar':
        return DScalar(math.exp(self.value))


@dataclass
class DVec2:
    """Dimensional 2D Vector."""
    x: float = 0.0
    y: float = 0.0
    
    def __add__(self, other: 'DVec2') -> 'DVec2':
        return DVec2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'DVec2') -> 'DVec2':
        return DVec2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> 'DVec2':
        return DVec2(self.x * scalar, self.y * scalar)
    
    def dot(self, other: 'DVec2') -> float:
        return self.x * other.x + self.y * other.y
    
    def magnitude(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def normalize(self) -> 'DVec2':
        mag = self.magnitude()
        return DVec2(self.x / mag, self.y / mag) if mag > 0 else DVec2()
    
    def angle(self) -> float:
        return math.atan2(self.y, self.x)
    
    def rotate(self, radians: float) -> 'DVec2':
        c, s = math.cos(radians), math.sin(radians)
        return DVec2(self.x * c - self.y * s, self.x * s + self.y * c)


@dataclass
class DVec3:
    """Dimensional 3D Vector."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other: 'DVec3') -> 'DVec3':
        return DVec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: 'DVec3') -> 'DVec3':
        return DVec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float) -> 'DVec3':
        return DVec3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def dot(self, other: 'DVec3') -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other: 'DVec3') -> 'DVec3':
        return DVec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def magnitude(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def normalize(self) -> 'DVec3':
        mag = self.magnitude()
        return DVec3(self.x / mag, self.y / mag, self.z / mag) if mag > 0 else DVec3()


@dataclass  
class DMatrix:
    """
    Dimensional Matrix - 2D array with operations.
    """
    rows: int
    cols: int
    _data: List[List[float]] = field(default=None)
    
    def __post_init__(self):
        if self._data is None:
            self._data = [[0.0] * self.cols for _ in range(self.rows)]
    
    def get(self, row: int, col: int) -> float:
        return self._data[row][col]
    
    def set(self, row: int, col: int, value: float) -> None:
        self._data[row][col] = value
    
    def __add__(self, other: 'DMatrix') -> 'DMatrix':
        result = DMatrix(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols):
                result.set(i, j, self.get(i, j) + other.get(i, j))
        return result
    
    def __mul__(self, other: Union['DMatrix', float]) -> 'DMatrix':
        if isinstance(other, (int, float)):
            result = DMatrix(self.rows, self.cols)
            for i in range(self.rows):
                for j in range(self.cols):
                    result.set(i, j, self.get(i, j) * other)
            return result
        else:
            # Matrix multiplication
            result = DMatrix(self.rows, other.cols)
            for i in range(self.rows):
                for j in range(other.cols):
                    s = sum(self.get(i, k) * other.get(k, j) for k in range(self.cols))
                    result.set(i, j, s)
            return result
    
    @classmethod
    def identity(cls, size: int) -> 'DMatrix':
        m = cls(size, size)
        for i in range(size):
            m.set(i, i, 1.0)
        return m


@dataclass
class DExpression:
    """
    Dimensional Expression - composable math expression.
    
    Build complex expressions from simple parts.
    """
    fn: Callable[[Dict[str, float]], float]
    variables: Set[str] = field(default_factory=set)
    
    @classmethod
    def var(cls, name: str) -> 'DExpression':
        """Create variable expression."""
        return cls(fn=lambda ctx: ctx[name], variables={name})
    
    @classmethod
    def const(cls, value: float) -> 'DExpression':
        """Create constant expression."""
        return cls(fn=lambda ctx: value, variables=set())
    
    def evaluate(self, **values: float) -> float:
        """Evaluate expression with variable values."""
        return self.fn(values)
    
    def __add__(self, other: Union['DExpression', float]) -> 'DExpression':
        if isinstance(other, (int, float)):
            return DExpression(
                fn=lambda ctx: self.fn(ctx) + other,
                variables=self.variables
            )
        return DExpression(
            fn=lambda ctx: self.fn(ctx) + other.fn(ctx),
            variables=self.variables | other.variables
        )
    
    def __mul__(self, other: Union['DExpression', float]) -> 'DExpression':
        if isinstance(other, (int, float)):
            return DExpression(
                fn=lambda ctx: self.fn(ctx) * other,
                variables=self.variables
            )
        return DExpression(
            fn=lambda ctx: self.fn(ctx) * other.fn(ctx),
            variables=self.variables | other.variables
        )
    
    def __pow__(self, other: Union['DExpression', float]) -> 'DExpression':
        if isinstance(other, (int, float)):
            return DExpression(
                fn=lambda ctx: self.fn(ctx) ** other,
                variables=self.variables
            )
        return DExpression(
            fn=lambda ctx: self.fn(ctx) ** other.fn(ctx),
            variables=self.variables | other.variables
        )


# =============================================================================
# 7. SENSORY PRIMITIVES - Color, Sound, Light, Pixels
# =============================================================================

@dataclass
class DColor:
    """
    Dimensional Color - RGBA with conversions.
    
    Values are on the substrate - inherent properties.
    """
    r: float = 0.0  # 0-1
    g: float = 0.0
    b: float = 0.0
    a: float = 1.0
    
    @classmethod
    def from_rgb(cls, r: int, g: int, b: int, a: int = 255) -> 'DColor':
        """Create from 0-255 RGB values."""
        return cls(r / 255, g / 255, b / 255, a / 255)
    
    @classmethod
    def from_hex(cls, hex_str: str) -> 'DColor':
        """Create from hex string (#RRGGBB or #RRGGBBAA)."""
        h = hex_str.lstrip('#')
        if len(h) == 6:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return cls.from_rgb(r, g, b)
        elif len(h) == 8:
            r, g, b, a = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16)
            return cls.from_rgb(r, g, b, a)
        raise ValueError(f"Invalid hex color: {hex_str}")
    
    @classmethod
    def from_hsl(cls, h: float, s: float, l: float) -> 'DColor':
        """Create from HSL (hue 0-360, sat 0-1, light 0-1)."""
        h = h / 360
        if s == 0:
            return cls(l, l, l)
        
        def hue_to_rgb(p, q, t):
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1/6: return p + (q - p) * 6 * t
            if t < 1/2: return q
            if t < 2/3: return p + (q - p) * (2/3 - t) * 6
            return p
        
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)
        return cls(r, g, b)
    
    def to_hex(self) -> str:
        """Convert to hex string."""
        r, g, b = int(self.r * 255), int(self.g * 255), int(self.b * 255)
        if self.a < 1:
            a = int(self.a * 255)
            return f"#{r:02x}{g:02x}{b:02x}{a:02x}"
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def to_hsl(self) -> Tuple[float, float, float]:
        """Convert to HSL."""
        max_c = max(self.r, self.g, self.b)
        min_c = min(self.r, self.g, self.b)
        l = (max_c + min_c) / 2
        
        if max_c == min_c:
            return (0, 0, l)
        
        d = max_c - min_c
        s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
        
        if max_c == self.r:
            h = (self.g - self.b) / d + (6 if self.g < self.b else 0)
        elif max_c == self.g:
            h = (self.b - self.r) / d + 2
        else:
            h = (self.r - self.g) / d + 4
        
        return (h * 60, s, l)
    
    def blend(self, other: 'DColor', amount: float = 0.5) -> 'DColor':
        """Blend with another color."""
        return DColor(
            r=self.r + (other.r - self.r) * amount,
            g=self.g + (other.g - self.g) * amount,
            b=self.b + (other.b - self.b) * amount,
            a=self.a + (other.a - self.a) * amount
        )
    
    def lighten(self, amount: float) -> 'DColor':
        """Lighten color."""
        h, s, l = self.to_hsl()
        return DColor.from_hsl(h, s, min(1, l + amount))
    
    def darken(self, amount: float) -> 'DColor':
        """Darken color."""
        h, s, l = self.to_hsl()
        return DColor.from_hsl(h, s, max(0, l - amount))
    
    @property
    def luminance(self) -> float:
        """Get perceived luminance (0-1)."""
        return 0.299 * self.r + 0.587 * self.g + 0.114 * self.b


@dataclass
class DSound:
    """
    Dimensional Sound - Frequency, amplitude, waveform.
    
    Sound exists on the substrate at its natural position.
    """
    frequency: float = 440.0  # Hz
    amplitude: float = 1.0    # 0-1
    phase: float = 0.0        # radians
    waveform: str = "sine"    # sine, square, triangle, sawtooth
    
    def at_time(self, t: float) -> float:
        """Get sample value at time t."""
        angle = 2 * math.pi * self.frequency * t + self.phase
        
        if self.waveform == "sine":
            return self.amplitude * math.sin(angle)
        elif self.waveform == "square":
            return self.amplitude * (1 if math.sin(angle) >= 0 else -1)
        elif self.waveform == "triangle":
            return self.amplitude * (2 * abs(2 * ((t * self.frequency) % 1) - 1) - 1)
        elif self.waveform == "sawtooth":
            return self.amplitude * (2 * ((t * self.frequency) % 1) - 1)
        return 0
    
    def note(self, name: str) -> 'DSound':
        """Create sound at musical note frequency."""
        notes = {
            'C': 261.63, 'D': 293.66, 'E': 329.63, 'F': 349.23,
            'G': 392.00, 'A': 440.00, 'B': 493.88
        }
        freq = notes.get(name.upper(), 440.0)
        return DSound(frequency=freq, amplitude=self.amplitude, waveform=self.waveform)
    
    def harmonics(self, count: int) -> List['DSound']:
        """Generate harmonic series."""
        return [
            DSound(
                frequency=self.frequency * (i + 1),
                amplitude=self.amplitude / (i + 1),
                waveform=self.waveform
            )
            for i in range(count)
        ]
    
    def octave_up(self) -> 'DSound':
        """Move up one octave."""
        return DSound(
            frequency=self.frequency * 2,
            amplitude=self.amplitude,
            waveform=self.waveform
        )
    
    def octave_down(self) -> 'DSound':
        """Move down one octave."""
        return DSound(
            frequency=self.frequency / 2,
            amplitude=self.amplitude,
            waveform=self.waveform
        )


@dataclass
class DLight:
    """
    Dimensional Light - Wavelength, intensity, direction.
    
    Light as electromagnetic radiation on the spectrum.
    """
    wavelength: float = 550.0  # nm (green)
    intensity: float = 1.0      # 0-1
    direction: DVec3 = field(default_factory=lambda: DVec3(0, 0, 1))
    
    @property
    def frequency(self) -> float:
        """Frequency in THz."""
        c = 299792458  # m/s
        return c / (self.wavelength * 1e-9) / 1e12
    
    @property
    def energy(self) -> float:
        """Photon energy in eV."""
        h = 4.135667696e-15  # eV·s
        return h * self.frequency * 1e12
    
    def to_color(self) -> DColor:
        """Convert wavelength to visible color."""
        # Simplified wavelength to RGB
        w = self.wavelength
        if w < 380 or w > 780:
            return DColor(0, 0, 0)  # Invisible
        
        if w < 440:
            r, g, b = -(w - 440) / 60, 0, 1
        elif w < 490:
            r, g, b = 0, (w - 440) / 50, 1
        elif w < 510:
            r, g, b = 0, 1, -(w - 510) / 20
        elif w < 580:
            r, g, b = (w - 510) / 70, 1, 0
        elif w < 645:
            r, g, b = 1, -(w - 645) / 65, 0
        else:
            r, g, b = 1, 0, 0
        
        return DColor(max(0, r) * self.intensity, 
                     max(0, g) * self.intensity, 
                     max(0, b) * self.intensity)
    
    @classmethod
    def red(cls) -> 'DLight':
        return cls(wavelength=700)
    
    @classmethod
    def green(cls) -> 'DLight':
        return cls(wavelength=550)
    
    @classmethod
    def blue(cls) -> 'DLight':
        return cls(wavelength=450)
    
    @classmethod
    def white(cls) -> 'DLight':
        """White light (broad spectrum approximation)."""
        return cls(wavelength=550, intensity=1.0)


@dataclass 
class DPixel:
    """
    Dimensional Pixel - A point on a 2D substrate with color.
    
    Pixels are addressable points with inherent color values.
    """
    x: int
    y: int
    color: DColor = field(default_factory=lambda: DColor(0, 0, 0))
    
    @property
    def address(self) -> Tuple[int, int]:
        """Direct address of this pixel."""
        return (self.x, self.y)
    
    def blend_with(self, other: 'DPixel', amount: float = 0.5) -> 'DPixel':
        """Blend with another pixel's color."""
        return DPixel(self.x, self.y, self.color.blend(other.color, amount))


@dataclass
class DCanvas:
    """
    Dimensional Canvas - 2D grid of pixels.
    
    Direct addressing to any pixel (O(1)).
    """
    width: int
    height: int
    _pixels: Dict[Tuple[int, int], DPixel] = field(default_factory=dict, repr=False)
    background: DColor = field(default_factory=lambda: DColor(0, 0, 0))
    
    def get_pixel(self, x: int, y: int) -> DPixel:
        """Get pixel at position (O(1))."""
        addr = (x, y)
        if addr not in self._pixels:
            self._pixels[addr] = DPixel(x, y, self.background)
        return self._pixels[addr]
    
    def set_pixel(self, x: int, y: int, color: DColor) -> None:
        """Set pixel at position (O(1))."""
        self._pixels[(x, y)] = DPixel(x, y, color)
    
    def fill(self, color: DColor) -> None:
        """Fill entire canvas."""
        self.background = color
        self._pixels.clear()
    
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, color: DColor) -> None:
        """Draw line using Bresenham's algorithm."""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        while True:
            self.set_pixel(x1, y1, color)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
    
    def draw_rect(self, x: int, y: int, w: int, h: int, color: DColor, fill: bool = False) -> None:
        """Draw rectangle."""
        if fill:
            for py in range(y, y + h):
                for px in range(x, x + w):
                    self.set_pixel(px, py, color)
        else:
            self.draw_line(x, y, x + w - 1, y, color)
            self.draw_line(x + w - 1, y, x + w - 1, y + h - 1, color)
            self.draw_line(x + w - 1, y + h - 1, x, y + h - 1, color)
            self.draw_line(x, y + h - 1, x, y, color)


# =============================================================================
# EXPORTS - All primitives are atomic building blocks
# =============================================================================

__all__ = [
    # Dimensional Operations
    'Level',
    'Dimension', 
    'ingest',
    'traverse',
    
    # Collections (no iteration)
    'DList',
    'DSet',
    'DMap',
    'DHash',
    'DQueue',
    'DStack',
    'DLinkedNode',
    'DLinkedList',
    
    # Functional
    'DLambda',
    'curry',
    'DStream',
    
    # Concurrency
    'DAtomic',
    'DMutex',
    'DSemaphore',
    'DChannel',
    'DFuture',
    'parallel',
    
    # Validation
    'DResult',
    'DOption',
    'DValidator',
    
    # Math
    'DScalar',
    'DVec2',
    'DVec3',
    'DMatrix',
    'DExpression',
    
    # Sensory
    'DColor',
    'DSound',
    'DLight',
    'DPixel',
    'DCanvas',
]
