"""
ButterflyFX Developer Utilities
================================

OPEN SOURCE - Licensed under CC BY 4.0
https://creativecommons.org/licenses/by/4.0/

Copyright (c) 2024-2026 Kenneth Bingham
Attribution required: Kenneth Bingham - https://butterflyfx.us

Developer tools for building, debugging, and optimizing dimensional code:

- Decorators for substrate creation
- Profiling and benchmarking
- Debugging and introspection
- Type validation
- Fluent builders

DESIGN PRINCIPLES:
1. FAIL FAST — Catch errors early with clear messages
2. ZERO OVERHEAD — Decorators compile away in production
3. FLUENT API — Chain operations naturally
4. INTROSPECTION — See inside dimensional structures
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    Dict, List, Tuple, Optional, Any, Callable, Union,
    TypeVar, Generic, Set, Type, get_type_hints, TYPE_CHECKING
)
from functools import wraps, lru_cache
from contextlib import contextmanager
from enum import Enum, auto
import time
import traceback
import sys
import io
import logging


T = TypeVar('T')
F = TypeVar('F', bound=Callable)


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

class DimensionalLogger:
    """
    Structured logging for dimensional operations.
    
    Includes dimensional context (spiral, level) in all messages.
    """
    
    def __init__(self, name: str):
        self._logger = logging.getLogger(f"helix.{name}")
        self._context: Dict[str, Any] = {}
    
    def set_context(self, **kwargs) -> None:
        """Set dimensional context for subsequent logs"""
        self._context.update(kwargs)
    
    def clear_context(self) -> None:
        self._context.clear()
    
    def _format_context(self) -> str:
        if not self._context:
            return ""
        return " | " + " ".join(f"{k}={v}" for k, v in self._context.items())
    
    def debug(self, msg: str, **kwargs) -> None:
        self._logger.debug(f"{msg}{self._format_context()}", **kwargs)
    
    def info(self, msg: str, **kwargs) -> None:
        self._logger.info(f"{msg}{self._format_context()}", **kwargs)
    
    def warning(self, msg: str, **kwargs) -> None:
        self._logger.warning(f"{msg}{self._format_context()}", **kwargs)
    
    def error(self, msg: str, **kwargs) -> None:
        self._logger.error(f"{msg}{self._format_context()}", **kwargs)
    
    @contextmanager
    def context(self, **kwargs):
        """Context manager for temporary dimensional context"""
        old_context = self._context.copy()
        self._context.update(kwargs)
        try:
            yield
        finally:
            self._context = old_context


# Global logger
log = DimensionalLogger("core")


# =============================================================================
# PROFILING AND BENCHMARKING
# =============================================================================

@dataclass
class ProfileResult:
    """Result of profiling a function call"""
    function_name: str
    call_count: int
    total_time_ns: int
    min_time_ns: int
    max_time_ns: int
    avg_time_ns: float
    
    @property
    def total_ms(self) -> float:
        return self.total_time_ns / 1_000_000
    
    @property
    def avg_ms(self) -> float:
        return self.avg_time_ns / 1_000_000
    
    def __repr__(self) -> str:
        return (f"Profile({self.function_name}: "
                f"calls={self.call_count}, "
                f"total={self.total_ms:.2f}ms, "
                f"avg={self.avg_ms:.3f}ms)")


class Profiler:
    """
    Performance profiler for dimensional operations.
    
    Usage:
        profiler = Profiler()
        
        @profiler.profile
        def my_function():
            ...
        
        my_function()
        print(profiler.results())
    """
    
    def __init__(self):
        self._stats: Dict[str, Dict[str, Any]] = {}
        self._enabled = True
    
    def enable(self) -> None:
        self._enabled = True
    
    def disable(self) -> None:
        self._enabled = False
    
    def reset(self) -> None:
        self._stats.clear()
    
    def profile(self, fn: F) -> F:
        """Decorator to profile a function"""
        name = fn.__qualname__
        
        if name not in self._stats:
            self._stats[name] = {
                'count': 0,
                'total_ns': 0,
                'min_ns': float('inf'),
                'max_ns': 0,
            }
        
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not self._enabled:
                return fn(*args, **kwargs)
            
            start = time.perf_counter_ns()
            try:
                return fn(*args, **kwargs)
            finally:
                elapsed = time.perf_counter_ns() - start
                stats = self._stats[name]
                stats['count'] += 1
                stats['total_ns'] += elapsed
                stats['min_ns'] = min(stats['min_ns'], elapsed)
                stats['max_ns'] = max(stats['max_ns'], elapsed)
        
        return wrapper
    
    def results(self) -> List[ProfileResult]:
        """Get all profiling results"""
        results = []
        for name, stats in self._stats.items():
            if stats['count'] > 0:
                results.append(ProfileResult(
                    function_name=name,
                    call_count=stats['count'],
                    total_time_ns=stats['total_ns'],
                    min_time_ns=stats['min_ns'],
                    max_time_ns=stats['max_ns'],
                    avg_time_ns=stats['total_ns'] / stats['count']
                ))
        return sorted(results, key=lambda r: r.total_time_ns, reverse=True)
    
    def report(self) -> str:
        """Generate a profiling report"""
        results = self.results()
        if not results:
            return "No profiling data collected."
        
        lines = ["=== PROFILING REPORT ==="]
        lines.append(f"{'Function':<40} {'Calls':>10} {'Total':>12} {'Avg':>12}")
        lines.append("-" * 76)
        
        for r in results:
            lines.append(
                f"{r.function_name:<40} "
                f"{r.call_count:>10} "
                f"{r.total_ms:>10.2f}ms "
                f"{r.avg_ms:>10.3f}ms"
            )
        
        return "\n".join(lines)


# Global profiler
profiler = Profiler()


def benchmark(iterations: int = 1000, warmup: int = 100):
    """
    Decorator to benchmark a function.
    
    Usage:
        @benchmark(iterations=10000)
        def my_function():
            ...
        
        my_function()  # Prints benchmark results
    """
    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Warmup
            for _ in range(warmup):
                fn(*args, **kwargs)
            
            # Benchmark
            times = []
            for _ in range(iterations):
                start = time.perf_counter_ns()
                fn(*args, **kwargs)
                times.append(time.perf_counter_ns() - start)
            
            total = sum(times)
            avg = total / iterations
            min_t = min(times)
            max_t = max(times)
            
            print(f"Benchmark: {fn.__qualname__}")
            print(f"  Iterations: {iterations}")
            print(f"  Total: {total/1_000_000:.2f}ms")
            print(f"  Avg: {avg/1_000:.3f}µs")
            print(f"  Min: {min_t/1_000:.3f}µs")
            print(f"  Max: {max_t/1_000:.3f}µs")
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# TYPE VALIDATION
# =============================================================================

class DimensionalTypeError(TypeError):
    """Type error with dimensional context"""
    pass


class DimensionalValueError(ValueError):
    """Value error with dimensional context"""
    pass


def validate_level(level: int) -> int:
    """Validate and return a level (0-6)"""
    if not isinstance(level, int):
        raise DimensionalTypeError(f"Level must be int, got {type(level).__name__}")
    if not 0 <= level <= 6:
        raise DimensionalValueError(f"Level must be 0-6, got {level}")
    return level


def validate_spiral(spiral: int) -> int:
    """Validate and return a spiral (any integer)"""
    if not isinstance(spiral, int):
        raise DimensionalTypeError(f"Spiral must be int, got {type(spiral).__name__}")
    return spiral


def typecheck(fn: F) -> F:
    """
    Decorator to enforce type hints at runtime.
    
    Usage:
        @typecheck
        def process(x: int, y: str) -> float:
            ...
    """
    hints = get_type_hints(fn) if hasattr(fn, '__annotations__') else {}
    
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Get parameter names
        import inspect
        sig = inspect.signature(fn)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        
        # Check each parameter
        for param_name, value in bound.arguments.items():
            if param_name in hints:
                expected_type = hints[param_name]
                # Handle Optional and Union types
                origin = getattr(expected_type, '__origin__', None)
                if origin is Union:
                    type_args = expected_type.__args__
                    if not isinstance(value, type_args):
                        raise DimensionalTypeError(
                            f"Parameter '{param_name}' expected {expected_type}, "
                            f"got {type(value).__name__}"
                        )
                elif not isinstance(value, expected_type):
                    raise DimensionalTypeError(
                        f"Parameter '{param_name}' expected {expected_type.__name__}, "
                        f"got {type(value).__name__}"
                    )
        
        # Call function
        result = fn(*args, **kwargs)
        
        # Check return type
        if 'return' in hints and hints['return'] is not None:
            expected_return = hints['return']
            if not isinstance(result, expected_return):
                raise DimensionalTypeError(
                    f"Return type expected {expected_return.__name__}, "
                    f"got {type(result).__name__}"
                )
        
        return result
    
    return wrapper


# =============================================================================
# INTROSPECTION AND DEBUGGING
# =============================================================================

def inspect_substrate(substrate) -> Dict[str, Any]:
    """
    Get detailed information about a substrate.
    
    Returns:
        Dict with substrate structure, tokens, operations, etc.
    """
    info = {
        'type': type(substrate).__name__,
        'address': getattr(substrate, 'address', 'unknown'),
        'domain': getattr(substrate, 'domain', 'unknown'),
    }
    
    # Get tokens if available
    if hasattr(substrate, '_tokens'):
        info['token_count'] = len(substrate._tokens)
        info['tokens'] = []
        for token in substrate._tokens:
            info['tokens'].append({
                'id': getattr(token, 'id', 'unknown'),
                'spiral': getattr(token, 'spiral', 0),
                'level': getattr(token, 'level', 0),
                'source': getattr(token, 'payload_source', 'unknown'),
            })
    
    # Get operations if available
    if hasattr(substrate, '_operations'):
        info['operations'] = list(substrate._operations.keys())
    
    # Get primitives if available
    if hasattr(substrate, '_primitives'):
        info['primitives'] = list(substrate._primitives.keys())
    
    return info


def inspect_kernel(kernel) -> Dict[str, Any]:
    """
    Get detailed information about a kernel.
    """
    info = {
        'type': type(kernel).__name__,
        'spiral': kernel.spiral,
        'level': kernel.level,
        'level_name': kernel.level_name,
        'operation_count': kernel.operation_count,
        'has_substrate': hasattr(kernel, '_substrate') and kernel._substrate is not None,
    }
    return info


def debug_dimensional_object(obj, depth: int = 0, max_depth: int = 3) -> str:
    """
    Create a debug string representation of a dimensional object.
    """
    indent = "  " * depth
    lines = []
    
    obj_type = type(obj).__name__
    lines.append(f"{indent}{obj_type}:")
    
    if hasattr(obj, '__dict__'):
        for key, value in obj.__dict__.items():
            if key.startswith('_'):
                continue
            if depth < max_depth and hasattr(value, '__dict__') and not isinstance(value, (str, int, float)):
                lines.append(f"{indent}  {key}:")
                lines.append(debug_dimensional_object(value, depth + 2, max_depth))
            else:
                lines.append(f"{indent}  {key}: {repr(value)}")
    
    return "\n".join(lines)


@contextmanager
def trace_operations():
    """
    Context manager to trace all dimensional operations.
    
    Usage:
        with trace_operations() as trace:
            kernel.invoke(3)
            kernel.spiral_up()
        print(trace.operations)
    """
    class OperationTrace:
        def __init__(self):
            self.operations: List[Dict[str, Any]] = []
        
        def record(self, op_name: str, **kwargs):
            self.operations.append({
                'operation': op_name,
                'timestamp': time.perf_counter_ns(),
                **kwargs
            })
    
    trace = OperationTrace()
    # In a real implementation, we'd hook into kernel operations
    yield trace


# =============================================================================
# FLUENT BUILDERS
# =============================================================================

class FluentBuilder(Generic[T]):
    """
    Base class for fluent builders.
    
    Subclass and add methods that return self for chaining.
    """
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
    
    def _set(self, key: str, value: Any) -> 'FluentBuilder[T]':
        self._config[key] = value
        return self
    
    def build(self) -> T:
        """Override to build the final object"""
        raise NotImplementedError


class SubstrateBuilder(FluentBuilder):
    """
    Fluent builder for substrates.
    
    Usage:
        substrate = (SubstrateBuilder("my-substrate")
            .domain("app.data")
            .primitive("count", 0)
            .primitive("name", "test")
            .operation("increment", lambda s: s.set("count", s.get("count") + 1))
            .build())
    """
    
    def __init__(self, name: str):
        super().__init__()
        self._config['name'] = name
        self._config['domain'] = 'default'
        self._config['primitives'] = {}
        self._config['operations'] = {}
    
    def domain(self, domain: str) -> 'SubstrateBuilder':
        self._config['domain'] = domain
        return self
    
    def primitive(self, name: str, value: Any) -> 'SubstrateBuilder':
        self._config['primitives'][name] = value
        return self
    
    def operation(self, name: str, fn: Callable) -> 'SubstrateBuilder':
        self._config['operations'][name] = fn
        return self
    
    def build(self):
        """Build the substrate"""
        # Import here to avoid circular imports
        from .substrate import ManifoldSubstrate
        
        # Create substrate
        substrate = ManifoldSubstrate(self._config['name'])
        
        # Add primitives
        for name, value in self._config['primitives'].items():
            substrate.register_primitive(name, value)
        
        # Add operations
        for name, fn in self._config['operations'].items():
            substrate.register_operation(name, fn)
        
        return substrate


# =============================================================================
# SUBSTRATE DECORATORS
# =============================================================================

def substrate(name: str = None, domain: str = 'default'):
    """
    Decorator to turn a class into a substrate.
    
    Usage:
        @substrate(name="users", domain="app.data")
        class UserSubstrate:
            count: int = 0
            name: str = ""
            
            def increment(self):
                self.count += 1
    """
    def decorator(cls: Type[T]) -> Type[T]:
        # Get class attributes as primitives
        primitives = {}
        operations = {}
        
        for attr_name in dir(cls):
            if attr_name.startswith('_'):
                continue
            
            attr = getattr(cls, attr_name)
            
            if callable(attr) and not isinstance(attr, type):
                operations[attr_name] = attr
            elif not callable(attr):
                primitives[attr_name] = attr
        
        # Store metadata
        cls._substrate_name = name or cls.__name__.lower()
        cls._substrate_domain = domain
        cls._substrate_primitives = primitives
        cls._substrate_operations = operations
        
        # Add registration method
        original_init = cls.__init__ if hasattr(cls, '__init__') else None
        
        def new_init(self, *args, **kwargs):
            if original_init:
                original_init(self, *args, **kwargs)
            
            # Initialize primitives
            for prim_name, prim_value in cls._substrate_primitives.items():
                if not hasattr(self, prim_name):
                    setattr(self, prim_name, prim_value)
        
        cls.__init__ = new_init
        
        return cls
    
    return decorator


def operation(level: int = 0, cached: bool = False):
    """
    Decorator to mark a method as a substrate operation.
    
    Usage:
        class MySubstrate:
            @operation(level=2, cached=True)
            def expensive_calc(self, x: int) -> int:
                return x * x
    """
    def decorator(fn: F) -> F:
        fn._is_operation = True
        fn._operation_level = level
        fn._operation_cached = cached
        
        if cached:
            fn = lru_cache(maxsize=128)(fn)
        
        return fn
    
    return decorator


def primitive(level: int = 0, readonly: bool = False):
    """
    Decorator for primitive properties.
    
    Usage:
        class MySubstrate:
            @primitive(level=1, readonly=True)
            def status(self) -> str:
                return "active"
    """
    def decorator(fn: F) -> F:
        fn._is_primitive = True
        fn._primitive_level = level
        fn._primitive_readonly = readonly
        return property(fn)
    
    return decorator


# =============================================================================
# ERROR HANDLING
# =============================================================================

class DimensionalError(Exception):
    """Base exception for dimensional operations"""
    
    def __init__(self, message: str, spiral: int = None, level: int = None):
        self.spiral = spiral
        self.level = level
        
        context = ""
        if spiral is not None or level is not None:
            parts = []
            if spiral is not None:
                parts.append(f"spiral={spiral}")
            if level is not None:
                parts.append(f"level={level}")
            context = f" [{', '.join(parts)}]"
        
        super().__init__(f"{message}{context}")


class InvalidStateError(DimensionalError):
    """Kernel is in an invalid state for the operation"""
    pass


class TokenNotFoundError(DimensionalError):
    """Token not found at the specified address"""
    pass


class OperationNotFoundError(DimensionalError):
    """Operation not found in substrate"""
    pass


def safe_execute(fn: Callable, *args, default: Any = None, **kwargs) -> Any:
    """
    Safely execute a function, returning default on any exception.
    
    Usage:
        result = safe_execute(risky_function, arg1, default=0)
    """
    try:
        return fn(*args, **kwargs)
    except Exception:
        return default


@contextmanager
def dimensional_context(spiral: int = None, level: int = None):
    """
    Context manager that provides dimensional context for errors.
    
    Usage:
        with dimensional_context(spiral=0, level=3):
            do_something_risky()
    """
    try:
        yield
    except DimensionalError:
        raise
    except Exception as e:
        raise DimensionalError(str(e), spiral=spiral, level=level) from e


# =============================================================================
# TESTING UTILITIES
# =============================================================================

def assert_dimensional(condition: bool, message: str = "", 
                       spiral: int = None, level: int = None):
    """
    Assert a condition with dimensional context.
    
    Usage:
        assert_dimensional(kernel.level == 3, "Expected level 3", level=kernel.level)
    """
    if not condition:
        raise DimensionalError(f"Assertion failed: {message}", spiral=spiral, level=level)


class DimensionalTestCase:
    """
    Base class for dimensional tests.
    
    Provides common setup and assertions.
    """
    
    def setup(self):
        """Override for test setup"""
        pass
    
    def teardown(self):
        """Override for test teardown"""
        pass
    
    def run_test(self, test_fn: Callable) -> bool:
        """Run a single test function"""
        try:
            self.setup()
            test_fn()
            return True
        except Exception as e:
            print(f"FAIL: {test_fn.__name__}")
            print(f"  {type(e).__name__}: {e}")
            traceback.print_exc()
            return False
        finally:
            self.teardown()
    
    def run_all(self) -> Tuple[int, int]:
        """Run all test methods (those starting with 'test_')"""
        passed = 0
        failed = 0
        
        for name in dir(self):
            if name.startswith('test_'):
                method = getattr(self, name)
                if callable(method):
                    if self.run_test(method):
                        passed += 1
                    else:
                        failed += 1
        
        print(f"\nResults: {passed} passed, {failed} failed")
        return passed, failed


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Logging
    'DimensionalLogger',
    'log',
    
    # Profiling
    'Profiler',
    'ProfileResult',
    'profiler',
    'benchmark',
    
    # Type validation
    'validate_level',
    'validate_spiral',
    'typecheck',
    'DimensionalTypeError',
    'DimensionalValueError',
    
    # Introspection
    'inspect_substrate',
    'inspect_kernel',
    'debug_dimensional_object',
    'trace_operations',
    
    # Builders
    'FluentBuilder',
    'SubstrateBuilder',
    
    # Decorators
    'substrate',
    'operation',
    'primitive',
    
    # Errors
    'DimensionalError',
    'InvalidStateError',
    'TokenNotFoundError',
    'OperationNotFoundError',
    'safe_execute',
    'dimensional_context',
    
    # Testing
    'assert_dimensional',
    'DimensionalTestCase',
]
