"""
ButterflyFX Decorators - Python Decorators for Dimensional Operations

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

Attribution required: Kenneth Bingham - https://butterflyfx.us

---

Decorators for enhancing functions with dimensional capabilities.

Decorators:
    - @dimensional: Mark a function as dimensional
    - @at_level: Execute at a specific level
    - @cached_by_level: Cache results by level
    - @spiral_scoped: Scope execution to a spiral
    - @materialize: Auto-materialize token results
    - @trace_helix: Log helix state transitions
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional, Set, TypeVar, Union
from functools import wraps
import time
from datetime import datetime

from .kernel import HelixState, HelixKernel, LEVEL_NAMES


F = TypeVar('F', bound=Callable)


# =============================================================================
# DIMENSIONAL DECORATOR
# =============================================================================

def dimensional(
    min_level: int = 0,
    max_level: int = 6,
    required_level: Optional[int] = None
) -> Callable[[F], F]:
    """
    Mark a function as dimensional.
    
    Attaches dimensional metadata to the function and optionally
    validates the execution level.
    
    Usage:
        @dimensional(min_level=3)
        def process_data(data):
            return transform(data)
    """
    def decorator(func: F) -> F:
        # Attach metadata
        func._dimensional = True
        func._min_level = min_level
        func._max_level = max_level
        func._required_level = required_level
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract kernel if passed
            kernel = kwargs.get('_kernel') or kwargs.get('kernel')
            
            if kernel and required_level is not None:
                if kernel.level != required_level:
                    raise ValueError(
                        f"Function requires level {required_level}, "
                        f"current level is {kernel.level}"
                    )
            
            if kernel and (kernel.level < min_level or kernel.level > max_level):
                raise ValueError(
                    f"Function requires level {min_level}-{max_level}, "
                    f"current level is {kernel.level}"
                )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def at_level(level: int) -> Callable[[F], F]:
    """
    Execute function at a specific helix level.
    
    Temporarily invokes the kernel to the specified level,
    executes the function, then restores the original state.
    
    Usage:
        @at_level(4)
        def process_plane_data(kernel, data):
            return data
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Find kernel argument
            kernel = None
            for arg in args:
                if isinstance(arg, HelixKernel):
                    kernel = arg
                    break
            if not kernel:
                kernel = kwargs.get('kernel')
            
            if not kernel:
                # No kernel, just execute
                return func(*args, **kwargs)
            
            # Save state
            original_level = kernel.level
            
            # Invoke to target level
            kernel.invoke(level)
            
            try:
                result = func(*args, **kwargs)
            finally:
                # Restore state
                kernel.invoke(original_level)
            
            return result
        
        wrapper._at_level = level
        return wrapper
    return decorator


# =============================================================================
# CACHING DECORATORS
# =============================================================================

def cached_by_level(maxsize: int = 128) -> Callable[[F], F]:
    """
    Cache function results by helix level.
    
    Different levels may produce different results, so cache
    separately per level.
    
    Usage:
        @cached_by_level()
        def expensive_computation(kernel, data):
            return compute(data)
    """
    def decorator(func: F) -> F:
        cache: Dict[tuple, Any] = {}
        cache_hits = 0
        cache_misses = 0
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal cache_hits, cache_misses
            
            # Find kernel to get level
            kernel = None
            for arg in args:
                if isinstance(arg, HelixKernel):
                    kernel = arg
                    break
            
            level = kernel.level if kernel else 0
            
            # Create cache key
            key = (level, args[1:] if kernel else args, tuple(sorted(kwargs.items())))
            
            if key in cache:
                cache_hits += 1
                return cache[key]
            
            cache_misses += 1
            result = func(*args, **kwargs)
            
            # Evict oldest if full
            if len(cache) >= maxsize:
                oldest_key = next(iter(cache))
                del cache[oldest_key]
            
            cache[key] = result
            return result
        
        wrapper.cache = cache
        wrapper.cache_info = lambda: {'hits': cache_hits, 'misses': cache_misses, 'size': len(cache)}
        wrapper.cache_clear = lambda: cache.clear()
        
        return wrapper
    return decorator


def cached_by_spiral(maxsize: int = 128) -> Callable[[F], F]:
    """
    Cache function results by spiral.
    
    Usage:
        @cached_by_spiral()
        def get_spiral_data(kernel):
            return load_data()
    """
    def decorator(func: F) -> F:
        cache: Dict[int, Any] = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            kernel = None
            for arg in args:
                if isinstance(arg, HelixKernel):
                    kernel = arg
                    break
            
            spiral = kernel.spiral if kernel else 0
            
            if spiral in cache:
                return cache[spiral]
            
            result = func(*args, **kwargs)
            
            if len(cache) >= maxsize:
                oldest = next(iter(cache))
                del cache[oldest]
            
            cache[spiral] = result
            return result
        
        wrapper.cache = cache
        wrapper.cache_clear = lambda: cache.clear()
        return wrapper
    return decorator


# =============================================================================
# SCOPING DECORATORS
# =============================================================================

def spiral_scoped(spiral: int) -> Callable[[F], F]:
    """
    Scope function execution to a specific spiral.
    
    Usage:
        @spiral_scoped(1)
        def process_future_data(data):
            return data
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Add spiral context
            kwargs['_spiral'] = spiral
            result = func(*args, **kwargs)
            return result
        
        wrapper._spiral_scoped = spiral
        return wrapper
    return decorator


def level_guard(min_level: int = 0, max_level: int = 6) -> Callable[[F], F]:
    """
    Guard function execution to specific level range.
    Raises error if kernel is outside range.
    
    Usage:
        @level_guard(min_level=4)  # Only plane and above
        def high_level_operation(kernel):
            ...
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            kernel = None
            for arg in args:
                if isinstance(arg, HelixKernel):
                    kernel = arg
                    break
            if not kernel:
                kernel = kwargs.get('kernel')
            
            if kernel:
                if kernel.level < min_level:
                    raise PermissionError(
                        f"Operation requires at least level {min_level} "
                        f"({LEVEL_NAMES[min_level]}), current is {kernel.level}"
                    )
                if kernel.level > max_level:
                    raise PermissionError(
                        f"Operation requires at most level {max_level} "
                        f"({LEVEL_NAMES[max_level]}), current is {kernel.level}"
                    )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# =============================================================================
# TIMING DECORATORS
# =============================================================================

def timed(func: F) -> F:
    """
    Time function execution and attach timing info.
    
    Usage:
        @timed
        def slow_function():
            time.sleep(1)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        wrapper._last_elapsed = elapsed
        return result
    
    wrapper._last_elapsed = 0.0
    wrapper.elapsed = lambda: wrapper._last_elapsed
    return wrapper


def timed_by_level(func: F) -> F:
    """
    Track timing per helix level.
    
    Usage:
        @timed_by_level
        def process(kernel, data):
            ...
        
        print(process.timings)  # {0: 0.1, 1: 0.2, ...}
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        kernel = None
        for arg in args:
            if isinstance(arg, HelixKernel):
                kernel = arg
                break
        
        level = kernel.level if kernel else 0
        
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        
        if level not in wrapper._timings:
            wrapper._timings[level] = []
        wrapper._timings[level].append(elapsed)
        
        return result
    
    wrapper._timings = {}
    wrapper.timings = lambda: {
        k: sum(v) / len(v) for k, v in wrapper._timings.items()
    }
    return wrapper


# =============================================================================
# TRACING DECORATORS
# =============================================================================

def trace_helix(func: F) -> F:
    """
    Log helix state transitions during function execution.
    
    Usage:
        @trace_helix
        def complex_operation(kernel):
            kernel.invoke(3)
            kernel.spiral_up()
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        kernel = None
        for arg in args:
            if isinstance(arg, HelixKernel):
                kernel = arg
                break
        
        if kernel:
            initial_state = (kernel.spiral, kernel.level)
            print(f"[HELIX] {func.__name__} START: ({initial_state[0]}, {initial_state[1]})")
        
        result = func(*args, **kwargs)
        
        if kernel:
            final_state = (kernel.spiral, kernel.level)
            if final_state != initial_state:
                print(f"[HELIX] {func.__name__} END: {initial_state} -> {final_state}")
            else:
                print(f"[HELIX] {func.__name__} END: (no state change)")
        
        return result
    
    return wrapper


def log_operations(func: F) -> F:
    """
    Log all helix operations during function execution.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        kernel = None
        for arg in args:
            if isinstance(arg, HelixKernel):
                kernel = arg
                break
        
        op_count = kernel._operation_count if kernel else 0
        result = func(*args, **kwargs)
        
        if kernel:
            new_ops = kernel._operation_count - op_count
            print(f"[OPS] {func.__name__}: {new_ops} operations")
        
        return result
    
    return wrapper


# =============================================================================
# MATERIALIZATION DECORATORS
# =============================================================================

def materialize_result(func: F) -> F:
    """
    Auto-materialize token results.
    
    If function returns a Token, materialize it.
    If returns list of Tokens, materialize all.
    
    Usage:
        @materialize_result
        def get_user(kernel, user_id):
            return find_token(user_id)
    """
    from .substrate import Token
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        if isinstance(result, Token):
            return result.materialize()
        
        if isinstance(result, (list, tuple)):
            return [
                t.materialize() if isinstance(t, Token) else t
                for t in result
            ]
        
        if isinstance(result, set):
            return {
                t.materialize() if isinstance(t, Token) else t
                for t in result
            }
        
        return result
    
    return wrapper


def lazy_result(func: F) -> F:
    """
    Wrap result in a lazy evaluator.
    Result is computed only when accessed.
    
    Usage:
        @lazy_result
        def expensive():
            return compute()
        
        result = expensive()  # Not computed yet
        value = result()  # Now computed
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        computed = False
        cached_result = None
        
        def lazy():
            nonlocal computed, cached_result
            if not computed:
                cached_result = func(*args, **kwargs)
                computed = True
            return cached_result
        
        return lazy
    
    return wrapper


# =============================================================================
# RETRY DECORATORS
# =============================================================================

def retry_on_level_change(max_retries: int = 3, backoff_levels: int = 1) -> Callable[[F], F]:
    """
    Retry function if level changed during execution.
    
    Useful for operations that depend on stable state.
    
    Usage:
        @retry_on_level_change()
        def atomic_operation(kernel, data):
            ...
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            kernel = None
            for arg in args:
                if isinstance(arg, HelixKernel):
                    kernel = arg
                    break
            
            for attempt in range(max_retries):
                initial_state = (kernel.spiral, kernel.level) if kernel else None
                
                try:
                    result = func(*args, **kwargs)
                    
                    if kernel:
                        current_state = (kernel.spiral, kernel.level)
                        if current_state != initial_state:
                            raise RuntimeError("State changed during execution")
                    
                    return result
                    
                except RuntimeError:
                    if attempt == max_retries - 1:
                        raise
                    # Wait and retry
                    time.sleep(0.01 * (attempt + 1))
            
        return wrapper
    return decorator


# =============================================================================
# COMPOSITION HELPERS
# =============================================================================

def compose(*decorators):
    """
    Compose multiple decorators into one.
    
    Usage:
        @compose(timed, trace_helix, at_level(3))
        def complex_function(kernel):
            ...
    """
    def decorator(func):
        for dec in reversed(decorators):
            func = dec(func)
        return func
    return decorator


def with_kernel(kernel: HelixKernel) -> Callable[[F], F]:
    """
    Pre-bind a kernel to a function.
    
    Usage:
        kernel = HelixKernel()
        
        @with_kernel(kernel)
        def process(data):
            ...
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(kernel, *args, **kwargs)
        return wrapper
    return decorator
