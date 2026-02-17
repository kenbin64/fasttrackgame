"""
Optimized Helix Kernel - Performance-Enhanced State Machine

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

This mathematical kernel belongs to all humanity.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

Performance optimizations:
    - LRU caching for materialization results
    - State transition memoization
    - Batch operations for bulk processing
    - Async support for non-blocking operations
    - Event hooks for extensions
    - Snapshot/restore for state management
    - Connection pooling for substrate access
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    Set, Dict, List, Any, Callable, Optional, TypeVar, Generic,
    Protocol, Iterator, Tuple, Awaitable, TYPE_CHECKING
)
from collections import OrderedDict
from functools import lru_cache
from threading import RLock
from weakref import WeakSet
from enum import Enum, auto
import asyncio
import time

if TYPE_CHECKING:
    from .substrate import Token


# =============================================================================
# TYPE VARIABLES
# =============================================================================

T = TypeVar('T')
S = TypeVar('S', bound='SubstrateProtocol')


# =============================================================================
# LEVEL DEFINITIONS (cached for performance)
# =============================================================================

LEVEL_NAMES: tuple = (
    "Potential",
    "Point", 
    "Length",
    "Width",
    "Plane",
    "Volume",
    "Whole"
)

LEVEL_ICONS: tuple = (
    "○",
    "•",
    "━",
    "▭",
    "▦",
    "▣",
    "◉"
)

MAX_LEVEL = 6
MIN_LEVEL = 0


# =============================================================================
# HELIX STATE (Optimized)
# =============================================================================

@dataclass(frozen=True, slots=True)
class HelixState:
    """
    Immutable helix state (s, l) with cached properties.
    
    spiral: int - Which turn of the helix (can be negative)
    level: int - Dimensional level within spiral (0-6)
    """
    spiral: int
    level: int
    
    def __post_init__(self):
        if not MIN_LEVEL <= self.level <= MAX_LEVEL:
            raise ValueError(f"Level must be {MIN_LEVEL}-{MAX_LEVEL}, got {self.level}")
    
    @property
    def level_name(self) -> str:
        return LEVEL_NAMES[self.level]
    
    @property
    def level_icon(self) -> str:
        return LEVEL_ICONS[self.level]
    
    @property
    def key(self) -> Tuple[int, int]:
        """Hashable key for caching"""
        return (self.spiral, self.level)
    
    def __repr__(self) -> str:
        return f"({self.spiral}, {self.level}:{self.level_name})"


# =============================================================================
# LRU CACHE WITH SIZE LIMIT AND TTL
# =============================================================================

class TimedLRUCache(Generic[T]):
    """Thread-safe LRU cache with time-to-live support."""
    
    __slots__ = ('_capacity', '_ttl', '_cache', '_timestamps', '_lock', '_hits', '_misses')
    
    def __init__(self, capacity: int = 1024, ttl_seconds: float = 60.0):
        self._capacity = capacity
        self._ttl = ttl_seconds
        self._cache: OrderedDict[Any, T] = OrderedDict()
        self._timestamps: Dict[Any, float] = {}
        self._lock = RLock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: Any) -> Optional[T]:
        """Get value if exists and not expired."""
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            # Check TTL
            if time.time() - self._timestamps[key] > self._ttl:
                self._evict(key)
                self._misses += 1
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return self._cache[key]
    
    def put(self, key: Any, value: T) -> None:
        """Store value with current timestamp."""
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            else:
                if len(self._cache) >= self._capacity:
                    # Evict oldest
                    oldest_key = next(iter(self._cache))
                    self._evict(oldest_key)
                self._cache[key] = value
            
            self._timestamps[key] = time.time()
    
    def _evict(self, key: Any) -> None:
        """Remove a key from cache."""
        if key in self._cache:
            del self._cache[key]
        if key in self._timestamps:
            del self._timestamps[key]
    
    def invalidate(self, key: Any) -> bool:
        """Invalidate a specific key."""
        with self._lock:
            if key in self._cache:
                self._evict(key)
                return True
            return False
    
    def invalidate_spiral(self, spiral: int) -> int:
        """Invalidate all entries for a spiral."""
        count = 0
        with self._lock:
            keys_to_remove = [
                k for k in self._cache.keys()
                if isinstance(k, tuple) and len(k) >= 1 and k[0] == spiral
            ]
            for key in keys_to_remove:
                self._evict(key)
                count += 1
        return count
    
    def clear(self) -> None:
        """Clear entire cache."""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
            self._hits = 0
            self._misses = 0
    
    @property
    def hit_rate(self) -> float:
        """Cache hit rate (0-1)."""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Cache statistics."""
        return {
            'size': len(self._cache),
            'capacity': self._capacity,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': self.hit_rate,
            'ttl': self._ttl
        }


# =============================================================================
# STATE TRANSITION MEMOIZATION
# =============================================================================

class TransitionMemo:
    """Memoization for state transitions."""
    
    __slots__ = ('_memo', '_lock')
    
    def __init__(self):
        self._memo: Dict[Tuple[int, int, str, Optional[int]], HelixState] = {}
        self._lock = RLock()
    
    def get_or_compute(
        self,
        current_spiral: int,
        current_level: int,
        operation: str,
        target_level: Optional[int] = None
    ) -> HelixState:
        """Get memoized transition or compute it."""
        key = (current_spiral, current_level, operation, target_level)
        
        with self._lock:
            if key in self._memo:
                return self._memo[key]
            
            result = self._compute(current_spiral, current_level, operation, target_level)
            self._memo[key] = result
            return result
    
    def _compute(
        self,
        spiral: int,
        level: int,
        operation: str,
        target: Optional[int]
    ) -> HelixState:
        """Compute state transition."""
        if operation == 'INVOKE':
            return HelixState(spiral, target or 0)
        elif operation == 'SPIRAL_UP':
            return HelixState(spiral + 1, 0)
        elif operation == 'SPIRAL_DOWN':
            return HelixState(spiral - 1, 6)
        elif operation == 'COLLAPSE':
            return HelixState(spiral, 0)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def clear(self) -> None:
        """Clear memoization cache."""
        with self._lock:
            self._memo.clear()


# =============================================================================
# EVENT SYSTEM
# =============================================================================

class KernelEvent(Enum):
    """Kernel lifecycle events."""
    PRE_INVOKE = auto()
    POST_INVOKE = auto()
    PRE_SPIRAL_UP = auto()
    POST_SPIRAL_UP = auto()
    PRE_SPIRAL_DOWN = auto()
    POST_SPIRAL_DOWN = auto()
    PRE_COLLAPSE = auto()
    POST_COLLAPSE = auto()
    STATE_CHANGE = auto()
    CACHE_HIT = auto()
    CACHE_MISS = auto()


EventHandler = Callable[['OptimizedHelixKernel', KernelEvent, Dict[str, Any]], None]


class EventEmitter:
    """Event emission system for kernel hooks."""
    
    __slots__ = ('_handlers', '_lock')
    
    def __init__(self):
        self._handlers: Dict[KernelEvent, List[EventHandler]] = {e: [] for e in KernelEvent}
        self._lock = RLock()
    
    def on(self, event: KernelEvent, handler: EventHandler) -> None:
        """Register an event handler."""
        with self._lock:
            self._handlers[event].append(handler)
    
    def off(self, event: KernelEvent, handler: EventHandler) -> bool:
        """Unregister an event handler."""
        with self._lock:
            try:
                self._handlers[event].remove(handler)
                return True
            except ValueError:
                return False
    
    def emit(self, kernel: 'OptimizedHelixKernel', event: KernelEvent, data: Dict[str, Any]) -> None:
        """Emit an event to all handlers."""
        with self._lock:
            handlers = list(self._handlers[event])
        
        for handler in handlers:
            try:
                handler(kernel, event, data)
            except Exception:
                pass  # Don't let handler errors break kernel
    
    def clear(self) -> None:
        """Clear all handlers."""
        with self._lock:
            for event in self._handlers:
                self._handlers[event].clear()


# =============================================================================
# SUBSTRATE PROTOCOL
# =============================================================================

class SubstrateProtocol(Protocol):
    """Interface that any substrate must implement."""
    
    def tokens_for_state(self, spiral: int, level: int) -> Set['Token']:
        """Return tokens materialized at this helix state (μ function)."""
        ...
    
    def release_materialized(self, spiral: int) -> None:
        """Release all materialized tokens for a spiral."""
        ...


# =============================================================================
# KERNEL SNAPSHOT
# =============================================================================

@dataclass(frozen=True, slots=True)
class KernelSnapshot:
    """Immutable snapshot of kernel state for checkpointing."""
    spiral: int
    level: int
    operation_count: int
    timestamp: float
    
    def restore_to(self, kernel: 'OptimizedHelixKernel') -> None:
        """Restore this snapshot to a kernel."""
        kernel._spiral = self.spiral
        kernel._level = self.level


# =============================================================================
# BATCH OPERATION RESULT
# =============================================================================

@dataclass(slots=True)
class BatchResult:
    """Result of a batch operation."""
    states: List[HelixState]
    tokens: List[Set['Token']]
    duration_ns: int
    operations: int
    
    @property
    def duration_ms(self) -> float:
        return self.duration_ns / 1_000_000


# =============================================================================
# OPTIMIZED HELIX KERNEL
# =============================================================================

class OptimizedHelixKernel:
    """
    Performance-enhanced Helix Kernel with caching, memoization, and events.
    
    Features:
        - LRU caching for materialization results
        - State transition memoization
        - Batch operations
        - Async support
        - Event hooks
        - Snapshot/restore
        - Thread-safe operations
    """
    
    __slots__ = (
        '_spiral', '_level', '_substrate', '_operation_count',
        '_cache', '_transition_memo', '_events', '_lock',
        '_cache_enabled', '_events_enabled'
    )
    
    def __init__(
        self,
        substrate: Optional[SubstrateProtocol] = None,
        cache_capacity: int = 1024,
        cache_ttl: float = 60.0,
        enable_cache: bool = True,
        enable_events: bool = True
    ):
        self._spiral = 0
        self._level = 0
        self._substrate = substrate
        self._operation_count = 0
        
        self._cache: TimedLRUCache[Set['Token']] = TimedLRUCache(cache_capacity, cache_ttl)
        self._transition_memo = TransitionMemo()
        self._events = EventEmitter()
        self._lock = RLock()
        
        self._cache_enabled = enable_cache
        self._events_enabled = enable_events
    
    # -------------------------------------------------------------------------
    # State Access
    # -------------------------------------------------------------------------
    
    @property
    def state(self) -> HelixState:
        """Current helix state."""
        return HelixState(self._spiral, self._level)
    
    @property
    def spiral(self) -> int:
        return self._spiral
    
    @property
    def level(self) -> int:
        return self._level
    
    @property
    def level_name(self) -> str:
        return LEVEL_NAMES[self._level]
    
    @property
    def operation_count(self) -> int:
        return self._operation_count
    
    # -------------------------------------------------------------------------
    # Core Operators (Optimized)
    # -------------------------------------------------------------------------
    
    def invoke(self, k: int, *, bypass_cache: bool = False) -> Set['Token']:
        """
        INVOKE(k): Jump directly to level k within current spiral.
        
        Uses cached results when available and cache_enabled=True.
        """
        if not MIN_LEVEL <= k <= MAX_LEVEL:
            raise ValueError(f"Level must be {MIN_LEVEL}-{MAX_LEVEL}, got {k}")
        
        with self._lock:
            old_state = self.state
            
            if self._events_enabled:
                self._events.emit(self, KernelEvent.PRE_INVOKE, {'target': k})
            
            # Get new state from memoization
            new_state = self._transition_memo.get_or_compute(
                self._spiral, self._level, 'INVOKE', k
            )
            self._level = new_state.level
            self._operation_count += 1
            
            # Get tokens (possibly cached)
            tokens = self._get_tokens_cached(bypass_cache)
            
            if self._events_enabled:
                self._events.emit(self, KernelEvent.POST_INVOKE, {
                    'old_state': old_state,
                    'new_state': self.state,
                    'tokens': tokens
                })
                self._events.emit(self, KernelEvent.STATE_CHANGE, {
                    'old': old_state,
                    'new': self.state
                })
            
            return tokens
    
    def spiral_up(self) -> None:
        """
        SPIRAL_UP: Move from Whole to Potential of next spiral.
        
        Precondition: l = 6 (must be at Whole)
        """
        with self._lock:
            if self._level != MAX_LEVEL:
                raise RuntimeError(
                    f"SPIRAL_UP requires level {MAX_LEVEL} (Whole), currently at {self._level}"
                )
            
            old_state = self.state
            
            if self._events_enabled:
                self._events.emit(self, KernelEvent.PRE_SPIRAL_UP, {})
            
            self._spiral += 1
            self._level = 0
            self._operation_count += 1
            
            if self._events_enabled:
                self._events.emit(self, KernelEvent.POST_SPIRAL_UP, {
                    'old_state': old_state,
                    'new_state': self.state
                })
    
    def spiral_down(self) -> None:
        """
        SPIRAL_DOWN: Move from Potential to Whole of previous spiral.
        
        Precondition: l = 0 (must be at Potential)
        """
        with self._lock:
            if self._level != MIN_LEVEL:
                raise RuntimeError(
                    f"SPIRAL_DOWN requires level {MIN_LEVEL} (Potential), currently at {self._level}"
                )
            
            old_state = self.state
            
            if self._events_enabled:
                self._events.emit(self, KernelEvent.PRE_SPIRAL_DOWN, {})
            
            self._spiral -= 1
            self._level = MAX_LEVEL
            self._operation_count += 1
            
            if self._events_enabled:
                self._events.emit(self, KernelEvent.POST_SPIRAL_DOWN, {
                    'old_state': old_state,
                    'new_state': self.state
                })
    
    def collapse(self, *, release_substrate: bool = True) -> None:
        """
        COLLAPSE: Return all levels to Potential.
        
        This is idempotent: COLLAPSE(COLLAPSE(s,l)) = COLLAPSE(s,l)
        """
        with self._lock:
            old_state = self.state
            
            if self._events_enabled:
                self._events.emit(self, KernelEvent.PRE_COLLAPSE, {})
            
            self._level = 0
            self._operation_count += 1
            
            if release_substrate and self._substrate:
                self._substrate.release_materialized(self._spiral)
            
            # Invalidate cache for this spiral
            if self._cache_enabled:
                self._cache.invalidate_spiral(self._spiral)
            
            if self._events_enabled:
                self._events.emit(self, KernelEvent.POST_COLLAPSE, {
                    'old_state': old_state,
                    'new_state': self.state
                })
    
    # -------------------------------------------------------------------------
    # Cached Token Retrieval
    # -------------------------------------------------------------------------
    
    def _get_tokens_cached(self, bypass_cache: bool = False) -> Set['Token']:
        """Get tokens for current state, using cache if available."""
        if not self._substrate:
            return set()
        
        cache_key = (self._spiral, self._level)
        
        if self._cache_enabled and not bypass_cache:
            cached = self._cache.get(cache_key)
            if cached is not None:
                if self._events_enabled:
                    self._events.emit(self, KernelEvent.CACHE_HIT, {'key': cache_key})
                return cached
        
        if self._events_enabled and self._cache_enabled:
            self._events.emit(self, KernelEvent.CACHE_MISS, {'key': cache_key})
        
        tokens = self._substrate.tokens_for_state(self._spiral, self._level)
        
        if self._cache_enabled:
            self._cache.put(cache_key, tokens)
        
        return tokens
    
    # -------------------------------------------------------------------------
    # Batch Operations
    # -------------------------------------------------------------------------
    
    def batch_invoke(self, levels: List[int], *, collect_tokens: bool = True) -> BatchResult:
        """
        Invoke multiple levels in sequence efficiently.
        
        Returns states and tokens for each level.
        """
        start = time.time_ns()
        states: List[HelixState] = []
        tokens: List[Set['Token']] = []
        
        for level in levels:
            self.invoke(level)
            states.append(self.state)
            if collect_tokens:
                tokens.append(self._get_tokens_cached())
            else:
                tokens.append(set())
        
        return BatchResult(
            states=states,
            tokens=tokens,
            duration_ns=time.time_ns() - start,
            operations=len(levels)
        )
    
    def scan_spiral(self, *, ascending: bool = True, collect_tokens: bool = True) -> BatchResult:
        """
        Scan all levels within current spiral.
        
        Args:
            ascending: If True, scan 0->6. If False, scan 6->0.
            collect_tokens: Whether to collect tokens at each level.
        """
        levels = list(range(0, 7)) if ascending else list(range(6, -1, -1))
        return self.batch_invoke(levels, collect_tokens=collect_tokens)
    
    def traverse_range(
        self,
        start_spiral: int,
        start_level: int,
        end_spiral: int,
        end_level: int,
        *,
        collect_tokens: bool = True
    ) -> BatchResult:
        """
        Traverse from one state to another, collecting results.
        """
        start_time = time.time_ns()
        states: List[HelixState] = []
        tokens: List[Set['Token']] = []
        
        # Reset to start position
        self._spiral = start_spiral
        self._level = start_level
        
        while (self._spiral, self._level) != (end_spiral, end_level):
            states.append(self.state)
            if collect_tokens:
                tokens.append(self._get_tokens_cached())
            else:
                tokens.append(set())
            
            # Move towards target
            if self._spiral < end_spiral:
                if self._level < MAX_LEVEL:
                    self.invoke(self._level + 1)
                else:
                    self.spiral_up()
            elif self._spiral > end_spiral:
                if self._level > MIN_LEVEL:
                    self.invoke(self._level - 1)
                else:
                    self.spiral_down()
            else:
                # Same spiral
                if self._level < end_level:
                    self.invoke(self._level + 1)
                elif self._level > end_level:
                    self.invoke(self._level - 1)
        
        # Add final state
        states.append(self.state)
        if collect_tokens:
            tokens.append(self._get_tokens_cached())
        else:
            tokens.append(set())
        
        return BatchResult(
            states=states,
            tokens=tokens,
            duration_ns=time.time_ns() - start_time,
            operations=len(states)
        )
    
    # -------------------------------------------------------------------------
    # Async Operations
    # -------------------------------------------------------------------------
    
    async def invoke_async(self, k: int) -> Set['Token']:
        """Async version of invoke()."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.invoke, k)
    
    async def batch_invoke_async(
        self,
        levels: List[int],
        *,
        collect_tokens: bool = True
    ) -> BatchResult:
        """Async version of batch_invoke()."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.batch_invoke(levels, collect_tokens=collect_tokens)
        )
    
    # -------------------------------------------------------------------------
    # Snapshot/Restore
    # -------------------------------------------------------------------------
    
    def snapshot(self) -> KernelSnapshot:
        """Create a snapshot of current state."""
        return KernelSnapshot(
            spiral=self._spiral,
            level=self._level,
            operation_count=self._operation_count,
            timestamp=time.time()
        )
    
    def restore(self, snapshot: KernelSnapshot) -> None:
        """Restore kernel state from snapshot."""
        with self._lock:
            snapshot.restore_to(self)
    
    # -------------------------------------------------------------------------
    # Event Hooks
    # -------------------------------------------------------------------------
    
    def on(self, event: KernelEvent, handler: EventHandler) -> None:
        """Register an event handler."""
        self._events.on(event, handler)
    
    def off(self, event: KernelEvent, handler: EventHandler) -> bool:
        """Unregister an event handler."""
        return self._events.off(event, handler)
    
    # -------------------------------------------------------------------------
    # Cache Management
    # -------------------------------------------------------------------------
    
    def cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self._cache.stats
    
    def clear_cache(self) -> None:
        """Clear the materialization cache."""
        self._cache.clear()
    
    def invalidate_cache(self, spiral: Optional[int] = None) -> int:
        """
        Invalidate cache entries.
        
        If spiral is provided, only invalidate that spiral.
        Otherwise, clear all.
        """
        if spiral is not None:
            return self._cache.invalidate_spiral(spiral)
        else:
            self._cache.clear()
            return -1
    
    # -------------------------------------------------------------------------
    # Configuration
    # -------------------------------------------------------------------------
    
    def configure(
        self,
        *,
        enable_cache: Optional[bool] = None,
        enable_events: Optional[bool] = None,
        cache_ttl: Optional[float] = None
    ) -> 'OptimizedHelixKernel':
        """Configure kernel options. Returns self for chaining."""
        if enable_cache is not None:
            self._cache_enabled = enable_cache
        if enable_events is not None:
            self._events_enabled = enable_events
        if cache_ttl is not None:
            self._cache._ttl = cache_ttl
        return self
    
    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------
    
    def reset(self) -> None:
        """Reset to initial state (0, 0)."""
        with self._lock:
            self._spiral = 0
            self._level = 0
            self._operation_count = 0
            self._cache.clear()
    
    def set_substrate(self, substrate: SubstrateProtocol) -> None:
        """Attach a substrate to this kernel."""
        self._substrate = substrate
        self._cache.clear()  # Clear cache since substrate changed
    
    def __repr__(self) -> str:
        cache_info = f", cache_hit_rate={self._cache.hit_rate:.2%}" if self._cache_enabled else ""
        return f"OptimizedHelixKernel(state={self.state}, ops={self._operation_count}{cache_info})"


# =============================================================================
# KERNEL POOL (Connection Pooling Pattern)
# =============================================================================

class KernelPool:
    """
    Pool of pre-initialized kernels for high-throughput scenarios.
    
    Avoids kernel creation overhead in hot paths.
    """
    
    __slots__ = ('_pool', '_substrate', '_lock', '_size', '_created')
    
    def __init__(
        self,
        substrate: Optional[SubstrateProtocol] = None,
        pool_size: int = 10
    ):
        self._substrate = substrate
        self._size = pool_size
        self._lock = RLock()
        self._created = 0
        self._pool: List[OptimizedHelixKernel] = []
        
        # Pre-create kernels
        for _ in range(pool_size):
            self._pool.append(self._create_kernel())
    
    def _create_kernel(self) -> OptimizedHelixKernel:
        """Create a new kernel."""
        self._created += 1
        return OptimizedHelixKernel(
            substrate=self._substrate,
            enable_events=False  # Disable events for pooled kernels
        )
    
    def acquire(self) -> OptimizedHelixKernel:
        """Acquire a kernel from the pool."""
        with self._lock:
            if self._pool:
                kernel = self._pool.pop()
                kernel.reset()
                return kernel
            else:
                # Pool exhausted, create new
                return self._create_kernel()
    
    def release(self, kernel: OptimizedHelixKernel) -> None:
        """Return a kernel to the pool."""
        with self._lock:
            if len(self._pool) < self._size:
                kernel.reset()
                self._pool.append(kernel)
    
    def __enter__(self) -> OptimizedHelixKernel:
        return self.acquire()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Note: Can't release without kernel reference in context manager
        pass
    
    @property
    def available(self) -> int:
        """Number of available kernels in pool."""
        return len(self._pool)
    
    @property
    def total_created(self) -> int:
        """Total kernels created (including overflow)."""
        return self._created


# =============================================================================
# KERNEL CONTEXT MANAGER
# =============================================================================

class KernelContext:
    """Context manager for kernel with automatic cleanup."""
    
    __slots__ = ('_kernel', '_snapshot', '_restore_on_exit')
    
    def __init__(
        self,
        kernel: OptimizedHelixKernel,
        *,
        restore_on_exit: bool = False
    ):
        self._kernel = kernel
        self._snapshot: Optional[KernelSnapshot] = None
        self._restore_on_exit = restore_on_exit
    
    def __enter__(self) -> OptimizedHelixKernel:
        if self._restore_on_exit:
            self._snapshot = self._kernel.snapshot()
        return self._kernel
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._restore_on_exit and self._snapshot:
            self._kernel.restore(self._snapshot)
        return False


# =============================================================================
# INVARIANT VERIFICATION
# =============================================================================

def verify_invariants(kernel: OptimizedHelixKernel) -> bool:
    """Verify all kernel invariants hold."""
    # I1: Valid level
    if not MIN_LEVEL <= kernel.level <= MAX_LEVEL:
        return False
    
    return True


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_kernel(
    substrate: Optional[SubstrateProtocol] = None,
    *,
    optimized: bool = True,
    **kwargs
) -> OptimizedHelixKernel:
    """Factory function to create a kernel with sensible defaults."""
    return OptimizedHelixKernel(substrate=substrate, **kwargs)


def create_pool(
    substrate: Optional[SubstrateProtocol] = None,
    pool_size: int = 10
) -> KernelPool:
    """Factory function to create a kernel pool."""
    return KernelPool(substrate=substrate, pool_size=pool_size)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # State
    'HelixState',
    'LEVEL_NAMES',
    'LEVEL_ICONS',
    
    # Kernel
    'OptimizedHelixKernel',
    'SubstrateProtocol',
    
    # Events
    'KernelEvent',
    'EventHandler',
    'EventEmitter',
    
    # Caching
    'TimedLRUCache',
    'TransitionMemo',
    
    # Pooling
    'KernelPool',
    'KernelContext',
    
    # Results
    'BatchResult',
    'KernelSnapshot',
    
    # Factory
    'create_kernel',
    'create_pool',
    
    # Utilities
    'verify_invariants',
]
