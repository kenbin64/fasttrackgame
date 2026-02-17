"""
ButterflyFX Enhanced Primitives — Advanced Building Blocks
============================================================

OPEN SOURCE - Licensed under CC BY 4.0
https://creativecommons.org/licenses/by/4.0/

Copyright (c) 2024-2026 Kenneth Bingham
Attribution required: Kenneth Bingham - https://butterflyfx.us

This module extends the kernel primitives with:
- Performance-optimized operations (cached, lazy, SIMD-style)
- Reactive bindings for automatic propagation
- Fluent API for chaining operations
- Enhanced type safety with runtime validation
- Serialization for dimensional transport

DESIGN PRINCIPLES:
1. O(1) LOOKUP — All operations use direct addressing
2. LAZY EVALUATION — Compute only when observed
3. IMMUTABLE BY DEFAULT — Functional transformations
4. DIMENSIONAL AWARENESS — Every primitive knows its level
5. REACTIVE BINDING — Changes propagate automatically
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    Dict, List, Tuple, Optional, Any, Callable, Union, 
    TypeVar, Generic, Iterator, Set, Protocol, runtime_checkable
)
from enum import Enum, auto
from abc import ABC, abstractmethod
from functools import lru_cache, cached_property
from weakref import WeakSet
import math
import hashlib
import struct
import time


T = TypeVar('T')
V = TypeVar('V')


# =============================================================================
# REACTIVE BINDING SYSTEM — Changes Propagate Automatically
# =============================================================================

@runtime_checkable
class Observable(Protocol):
    """Protocol for observable values"""
    def subscribe(self, observer: 'Observer') -> None: ...
    def unsubscribe(self, observer: 'Observer') -> None: ...


@runtime_checkable  
class Observer(Protocol):
    """Protocol for observers"""
    def on_change(self, source: Observable, old_value: Any, new_value: Any) -> None: ...


class ReactiveValue(Generic[T]):
    """
    A value that notifies observers when changed.
    
    Use Cases:
        - UI bindings
        - Cascading calculations
        - Dimensional state synchronization
    
    Example:
        position = ReactiveValue(Vector3D(0, 0, 0))
        position.subscribe(my_observer)
        position.set(Vector3D(1, 0, 0))  # Observer notified
    """
    __slots__ = ('_value', '_observers', '_name', '_level', '_frozen')
    
    def __init__(self, initial: T, name: str = "", level: int = 1):
        self._value = initial
        self._observers: WeakSet[Observer] = WeakSet()
        self._name = name
        self._level = level
        self._frozen = False
    
    @property
    def value(self) -> T:
        return self._value
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def level(self) -> int:
        return self._level
    
    @property
    def is_frozen(self) -> bool:
        return self._frozen
    
    def set(self, new_value: T) -> 'ReactiveValue[T]':
        """Set value and notify observers"""
        if self._frozen:
            raise RuntimeError(f"Cannot modify frozen ReactiveValue '{self._name}'")
        
        old_value = self._value
        self._value = new_value
        
        if old_value != new_value:
            self._notify(old_value, new_value)
        
        return self
    
    def transform(self, fn: Callable[[T], T]) -> 'ReactiveValue[T]':
        """Apply transformation and update value"""
        return self.set(fn(self._value))
    
    def freeze(self) -> 'ReactiveValue[T]':
        """Make immutable"""
        self._frozen = True
        return self
    
    def subscribe(self, observer: Observer) -> None:
        self._observers.add(observer)
    
    def unsubscribe(self, observer: Observer) -> None:
        self._observers.discard(observer)
    
    def _notify(self, old_value: T, new_value: T) -> None:
        for observer in self._observers:
            observer.on_change(self, old_value, new_value)
    
    def map(self, fn: Callable[[T], V]) -> 'ComputedValue[V]':
        """Create derived computed value"""
        return ComputedValue(lambda: fn(self._value), [self])
    
    def __repr__(self) -> str:
        return f"Reactive[L{self._level}]({self._value})"


class ComputedValue(Generic[T]):
    """
    A value computed from other reactive values.
    
    Automatically invalidates when dependencies change.
    Lazy evaluation — only computes when accessed.
    
    Example:
        x = ReactiveValue(3.0)
        y = ReactiveValue(4.0)
        hypotenuse = ComputedValue(lambda: math.sqrt(x.value**2 + y.value**2), [x, y])
        print(hypotenuse.value)  # 5.0
        x.set(5.0)
        print(hypotenuse.value)  # Recomputes: 6.4
    """
    __slots__ = ('_compute', '_dependencies', '_cached', '_cache_valid', '_observers')
    
    def __init__(self, compute: Callable[[], T], dependencies: List[ReactiveValue]):
        self._compute = compute
        self._dependencies = dependencies
        self._cached: Optional[T] = None
        self._cache_valid = False
        self._observers: WeakSet[Observer] = WeakSet()
        
        # Subscribe to all dependencies
        invalidator = _CacheInvalidator(self)
        for dep in dependencies:
            dep.subscribe(invalidator)
    
    @property
    def value(self) -> T:
        if not self._cache_valid:
            old = self._cached
            self._cached = self._compute()
            self._cache_valid = True
            if old != self._cached:
                self._notify(old, self._cached)
        return self._cached
    
    def invalidate(self) -> None:
        self._cache_valid = False
    
    def subscribe(self, observer: Observer) -> None:
        self._observers.add(observer)
    
    def unsubscribe(self, observer: Observer) -> None:
        self._observers.discard(observer)
    
    def _notify(self, old_value: T, new_value: T) -> None:
        for observer in self._observers:
            observer.on_change(self, old_value, new_value)


class _CacheInvalidator:
    """Internal observer that invalidates computed value cache"""
    __slots__ = ('_computed',)
    
    def __init__(self, computed: ComputedValue):
        self._computed = computed
    
    def on_change(self, source: Observable, old_value: Any, new_value: Any) -> None:
        self._computed.invalidate()


# =============================================================================
# LAZY EVALUATION SYSTEM — Compute Only When Observed
# =============================================================================

class Lazy(Generic[T]):
    """
    Lazy evaluation wrapper — computes value only when first accessed.
    
    Example:
        expensive = Lazy(lambda: heavy_computation())
        # ... later ...
        result = expensive.value  # NOW it computes
    """
    __slots__ = ('_factory', '_value', '_computed', '_compute_time_ns')
    
    def __init__(self, factory: Callable[[], T]):
        self._factory = factory
        self._value: Optional[T] = None
        self._computed = False
        self._compute_time_ns: int = 0
    
    @property
    def value(self) -> T:
        if not self._computed:
            start = time.perf_counter_ns()
            self._value = self._factory()
            self._compute_time_ns = time.perf_counter_ns() - start
            self._computed = True
        return self._value
    
    @property
    def is_computed(self) -> bool:
        return self._computed
    
    @property
    def compute_time_ns(self) -> int:
        """Time spent computing (0 if not yet computed)"""
        return self._compute_time_ns
    
    def map(self, fn: Callable[[T], V]) -> 'Lazy[V]':
        """Create new Lazy with transformed value"""
        return Lazy(lambda: fn(self.value))
    
    def __repr__(self) -> str:
        if self._computed:
            return f"Lazy({self._value})"
        return "Lazy(<not computed>)"


# =============================================================================
# ENHANCED VECTOR PRIMITIVES — Performance Optimized
# =============================================================================

@dataclass(frozen=True, slots=True)
class Vector3D:
    """
    Immutable 3D vector with optimized operations.
    
    Performance Features:
        - __slots__ for memory efficiency
        - frozen for hashability
        - cached_property for expensive computations
        - SIMD-style batch operations
    """
    x: float
    y: float
    z: float
    
    # -------------------------------------------------------------------------
    # Factory Methods
    # -------------------------------------------------------------------------
    
    @classmethod
    def zero(cls) -> 'Vector3D':
        return cls(0.0, 0.0, 0.0)
    
    @classmethod
    def one(cls) -> 'Vector3D':
        return cls(1.0, 1.0, 1.0)
    
    @classmethod
    def up(cls) -> 'Vector3D':
        return cls(0.0, 1.0, 0.0)
    
    @classmethod
    def down(cls) -> 'Vector3D':
        return cls(0.0, -1.0, 0.0)
    
    @classmethod
    def forward(cls) -> 'Vector3D':
        return cls(0.0, 0.0, -1.0)
    
    @classmethod
    def back(cls) -> 'Vector3D':
        return cls(0.0, 0.0, 1.0)
    
    @classmethod
    def right(cls) -> 'Vector3D':
        return cls(1.0, 0.0, 0.0)
    
    @classmethod
    def left(cls) -> 'Vector3D':
        return cls(-1.0, 0.0, 0.0)
    
    @classmethod
    def from_tuple(cls, t: Tuple[float, float, float]) -> 'Vector3D':
        return cls(t[0], t[1], t[2])
    
    @classmethod
    def from_spherical(cls, r: float, theta: float, phi: float) -> 'Vector3D':
        """Create from spherical coordinates (r, theta, phi)"""
        sin_phi = math.sin(phi)
        return cls(
            r * sin_phi * math.cos(theta),
            r * math.cos(phi),
            r * sin_phi * math.sin(theta)
        )
    
    # -------------------------------------------------------------------------
    # Properties (Cached)
    # -------------------------------------------------------------------------
    
    @cached_property
    def magnitude(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    @cached_property
    def magnitude_squared(self) -> float:
        """Faster when you don't need exact distance"""
        return self.x * self.x + self.y * self.y + self.z * self.z
    
    @cached_property
    def normalized(self) -> 'Vector3D':
        m = self.magnitude
        if m < 1e-10:
            return Vector3D.zero()
        return Vector3D(self.x / m, self.y / m, self.z / m)
    
    @cached_property
    def tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)
    
    # -------------------------------------------------------------------------
    # Operations (All Return New Vectors)
    # -------------------------------------------------------------------------
    
    def dot(self, other: 'Vector3D') -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def distance_to(self, other: 'Vector3D') -> float:
        dx, dy, dz = self.x - other.x, self.y - other.y, self.z - other.z
        return math.sqrt(dx * dx + dy * dy + dz * dz)
    
    def distance_squared_to(self, other: 'Vector3D') -> float:
        """Faster distance comparison"""
        dx, dy, dz = self.x - other.x, self.y - other.y, self.z - other.z
        return dx * dx + dy * dy + dz * dz
    
    def lerp(self, other: 'Vector3D', t: float) -> 'Vector3D':
        """Linear interpolation"""
        return Vector3D(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
            self.z + (other.z - self.z) * t
        )
    
    def slerp(self, other: 'Vector3D', t: float) -> 'Vector3D':
        """Spherical linear interpolation"""
        dot = max(-1.0, min(1.0, self.normalized.dot(other.normalized)))
        theta = math.acos(dot) * t
        relative = (other - self * dot).normalized
        return self * math.cos(theta) + relative * math.sin(theta)
    
    def reflect(self, normal: 'Vector3D') -> 'Vector3D':
        """Reflect vector off surface with given normal"""
        d = 2 * self.dot(normal)
        return Vector3D(
            self.x - d * normal.x,
            self.y - d * normal.y,
            self.z - d * normal.z
        )
    
    def project_onto(self, other: 'Vector3D') -> 'Vector3D':
        """Project this vector onto another"""
        denom = other.magnitude_squared
        if denom < 1e-10:
            return Vector3D.zero()
        scalar = self.dot(other) / denom
        return Vector3D(other.x * scalar, other.y * scalar, other.z * scalar)
    
    def clamp_magnitude(self, max_mag: float) -> 'Vector3D':
        """Clamp vector to maximum magnitude"""
        if self.magnitude_squared > max_mag * max_mag:
            return self.normalized * max_mag
        return self
    
    def rotate_around_axis(self, axis: 'Vector3D', angle: float) -> 'Vector3D':
        """Rotate this vector around an axis (Rodrigues' formula)"""
        k = axis.normalized
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        return self * cos_a + k.cross(self) * sin_a + k * (k.dot(self)) * (1 - cos_a)
    
    # -------------------------------------------------------------------------
    # Operators
    # -------------------------------------------------------------------------
    
    def __add__(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float) -> 'Vector3D':
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __rmul__(self, scalar: float) -> 'Vector3D':
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar: float) -> 'Vector3D':
        return Vector3D(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def __neg__(self) -> 'Vector3D':
        return Vector3D(-self.x, -self.y, -self.z)
    
    def __repr__(self) -> str:
        return f"Vec3({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"


# =============================================================================
# BATCH OPERATIONS — SIMD-Style Processing
# =============================================================================

class VectorBatch:
    """
    Batch operations on multiple vectors.
    
    SIMD-style processing for performance when working with many vectors.
    
    Example:
        points = VectorBatch([v1, v2, v3, v4])
        transformed = points.scale(2.0).translate(Vector3D(1, 0, 0))
        center = points.centroid()
    """
    __slots__ = ('_vectors',)
    
    def __init__(self, vectors: List[Vector3D]):
        self._vectors = vectors
    
    @property
    def vectors(self) -> List[Vector3D]:
        return self._vectors
    
    @property
    def count(self) -> int:
        return len(self._vectors)
    
    def scale(self, factor: float) -> 'VectorBatch':
        """Scale all vectors by factor"""
        return VectorBatch([v * factor for v in self._vectors])
    
    def translate(self, offset: Vector3D) -> 'VectorBatch':
        """Translate all vectors by offset"""
        return VectorBatch([v + offset for v in self._vectors])
    
    def rotate_around_axis(self, axis: Vector3D, angle: float) -> 'VectorBatch':
        """Rotate all vectors around axis"""
        return VectorBatch([v.rotate_around_axis(axis, angle) for v in self._vectors])
    
    def normalize_all(self) -> 'VectorBatch':
        """Normalize all vectors"""
        return VectorBatch([v.normalized for v in self._vectors])
    
    def centroid(self) -> Vector3D:
        """Calculate centroid of all points"""
        if not self._vectors:
            return Vector3D.zero()
        n = len(self._vectors)
        sx = sum(v.x for v in self._vectors)
        sy = sum(v.y for v in self._vectors)
        sz = sum(v.z for v in self._vectors)
        return Vector3D(sx / n, sy / n, sz / n)
    
    def bounding_box(self) -> Tuple[Vector3D, Vector3D]:
        """Calculate axis-aligned bounding box (min, max)"""
        if not self._vectors:
            return Vector3D.zero(), Vector3D.zero()
        
        min_x = min(v.x for v in self._vectors)
        min_y = min(v.y for v in self._vectors)
        min_z = min(v.z for v in self._vectors)
        max_x = max(v.x for v in self._vectors)
        max_y = max(v.y for v in self._vectors)
        max_z = max(v.z for v in self._vectors)
        
        return Vector3D(min_x, min_y, min_z), Vector3D(max_x, max_y, max_z)
    
    def distances_from(self, point: Vector3D) -> List[float]:
        """Calculate distance of each vector from a point"""
        return [v.distance_to(point) for v in self._vectors]
    
    def filter_by_distance(self, center: Vector3D, max_dist: float) -> 'VectorBatch':
        """Keep only vectors within max distance from center"""
        max_dist_sq = max_dist * max_dist
        return VectorBatch([
            v for v in self._vectors 
            if v.distance_squared_to(center) <= max_dist_sq
        ])


# =============================================================================
# QUATERNION — Rotation Without Gimbal Lock
# =============================================================================

@dataclass(frozen=True, slots=True)
class Quaternion:
    """
    Quaternion for 3D rotations.
    
    Avoids gimbal lock unlike Euler angles.
    Smooth interpolation with slerp.
    """
    w: float
    x: float
    y: float
    z: float
    
    @classmethod
    def identity(cls) -> 'Quaternion':
        return cls(1.0, 0.0, 0.0, 0.0)
    
    @classmethod
    def from_axis_angle(cls, axis: Vector3D, angle: float) -> 'Quaternion':
        """Create rotation quaternion from axis and angle"""
        half_angle = angle * 0.5
        sin_half = math.sin(half_angle)
        n = axis.normalized
        return cls(
            math.cos(half_angle),
            n.x * sin_half,
            n.y * sin_half,
            n.z * sin_half
        )
    
    @classmethod
    def from_euler(cls, pitch: float, yaw: float, roll: float) -> 'Quaternion':
        """Create from Euler angles (radians)"""
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)
        
        return cls(
            cr * cp * cy + sr * sp * sy,
            sr * cp * cy - cr * sp * sy,
            cr * sp * cy + sr * cp * sy,
            cr * cp * sy - sr * sp * cy
        )
    
    @classmethod
    def look_rotation(cls, forward: Vector3D, up: Vector3D = None) -> 'Quaternion':
        """Create rotation looking in the given direction"""
        if up is None:
            up = Vector3D.up()
        
        f = forward.normalized
        r = up.cross(f).normalized
        u = f.cross(r)
        
        # Build rotation matrix and convert to quaternion
        m00, m01, m02 = r.x, u.x, f.x
        m10, m11, m12 = r.y, u.y, f.y
        m20, m21, m22 = r.z, u.z, f.z
        
        trace = m00 + m11 + m22
        
        if trace > 0:
            s = 0.5 / math.sqrt(trace + 1.0)
            return cls(
                0.25 / s,
                (m21 - m12) * s,
                (m02 - m20) * s,
                (m10 - m01) * s
            )
        elif m00 > m11 and m00 > m22:
            s = 2.0 * math.sqrt(1.0 + m00 - m11 - m22)
            return cls(
                (m21 - m12) / s,
                0.25 * s,
                (m01 + m10) / s,
                (m02 + m20) / s
            )
        elif m11 > m22:
            s = 2.0 * math.sqrt(1.0 + m11 - m00 - m22)
            return cls(
                (m02 - m20) / s,
                (m01 + m10) / s,
                0.25 * s,
                (m12 + m21) / s
            )
        else:
            s = 2.0 * math.sqrt(1.0 + m22 - m00 - m11)
            return cls(
                (m10 - m01) / s,
                (m02 + m20) / s,
                (m12 + m21) / s,
                0.25 * s
            )
    
    @cached_property
    def magnitude(self) -> float:
        return math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)
    
    @cached_property
    def normalized(self) -> 'Quaternion':
        m = self.magnitude
        if m < 1e-10:
            return Quaternion.identity()
        return Quaternion(self.w / m, self.x / m, self.y / m, self.z / m)
    
    @cached_property
    def conjugate(self) -> 'Quaternion':
        return Quaternion(self.w, -self.x, -self.y, -self.z)
    
    @cached_property
    def inverse(self) -> 'Quaternion':
        mag_sq = self.w**2 + self.x**2 + self.y**2 + self.z**2
        if mag_sq < 1e-10:
            return Quaternion.identity()
        return Quaternion(
            self.w / mag_sq, -self.x / mag_sq, -self.y / mag_sq, -self.z / mag_sq
        )
    
    def rotate_vector(self, v: Vector3D) -> Vector3D:
        """Rotate a vector by this quaternion"""
        qv = Quaternion(0, v.x, v.y, v.z)
        result = self * qv * self.conjugate
        return Vector3D(result.x, result.y, result.z)
    
    def slerp(self, other: 'Quaternion', t: float) -> 'Quaternion':
        """Spherical linear interpolation"""
        # Normalize inputs
        q1 = self.normalized
        q2 = other.normalized
        
        # Compute dot product
        dot = q1.w * q2.w + q1.x * q2.x + q1.y * q2.y + q1.z * q2.z
        
        # If negative, negate one quaternion
        if dot < 0:
            q2 = Quaternion(-q2.w, -q2.x, -q2.y, -q2.z)
            dot = -dot
        
        # If very close, use linear interpolation
        if dot > 0.9995:
            return Quaternion(
                q1.w + t * (q2.w - q1.w),
                q1.x + t * (q2.x - q1.x),
                q1.y + t * (q2.y - q1.y),
                q1.z + t * (q2.z - q1.z)
            ).normalized
        
        # Slerp
        theta_0 = math.acos(dot)
        theta = theta_0 * t
        sin_theta = math.sin(theta)
        sin_theta_0 = math.sin(theta_0)
        
        s1 = math.cos(theta) - dot * sin_theta / sin_theta_0
        s2 = sin_theta / sin_theta_0
        
        return Quaternion(
            s1 * q1.w + s2 * q2.w,
            s1 * q1.x + s2 * q2.x,
            s1 * q1.y + s2 * q2.y,
            s1 * q1.z + s2 * q2.z
        )
    
    def to_euler(self) -> Tuple[float, float, float]:
        """Convert to Euler angles (pitch, yaw, roll)"""
        # Roll (x-axis)
        sinr_cosp = 2 * (self.w * self.x + self.y * self.z)
        cosr_cosp = 1 - 2 * (self.x**2 + self.y**2)
        roll = math.atan2(sinr_cosp, cosr_cosp)
        
        # Pitch (y-axis)
        sinp = 2 * (self.w * self.y - self.z * self.x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)
        else:
            pitch = math.asin(sinp)
        
        # Yaw (z-axis)
        siny_cosp = 2 * (self.w * self.z + self.x * self.y)
        cosy_cosp = 1 - 2 * (self.y**2 + self.z**2)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        
        return (pitch, yaw, roll)
    
    def __mul__(self, other: 'Quaternion') -> 'Quaternion':
        """Hamilton product"""
        return Quaternion(
            self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z,
            self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y,
            self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x,
            self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w
        )
    
    def __repr__(self) -> str:
        return f"Quat({self.w:.3f}, {self.x:.3f}, {self.y:.3f}, {self.z:.3f})"


# =============================================================================
# TRANSFORM — Position + Rotation + Scale
# =============================================================================

@dataclass
class Transform:
    """
    Full 3D transform: position, rotation, scale.
    
    Immutable operations return new transforms.
    Mutable operations update in place (for performance).
    """
    position: Vector3D = field(default_factory=Vector3D.zero)
    rotation: Quaternion = field(default_factory=Quaternion.identity)
    scale: Vector3D = field(default_factory=Vector3D.one)
    
    @classmethod
    def identity(cls) -> 'Transform':
        return cls()
    
    def translate(self, offset: Vector3D) -> 'Transform':
        """Return new Transform translated by offset"""
        return Transform(self.position + offset, self.rotation, self.scale)
    
    def rotate(self, rotation: Quaternion) -> 'Transform':
        """Return new Transform with additional rotation"""
        return Transform(self.position, rotation * self.rotation, self.scale)
    
    def rotate_around_axis(self, axis: Vector3D, angle: float) -> 'Transform':
        """Rotate around axis by angle"""
        return self.rotate(Quaternion.from_axis_angle(axis, angle))
    
    def scale_by(self, factor: Union[float, Vector3D]) -> 'Transform':
        """Return new Transform scaled by factor"""
        if isinstance(factor, (int, float)):
            factor = Vector3D(factor, factor, factor)
        new_scale = Vector3D(
            self.scale.x * factor.x,
            self.scale.y * factor.y,
            self.scale.z * factor.z
        )
        return Transform(self.position, self.rotation, new_scale)
    
    def transform_point(self, point: Vector3D) -> Vector3D:
        """Transform a point from local to world space"""
        scaled = Vector3D(
            point.x * self.scale.x,
            point.y * self.scale.y,
            point.z * self.scale.z
        )
        rotated = self.rotation.rotate_vector(scaled)
        return rotated + self.position
    
    def transform_direction(self, direction: Vector3D) -> Vector3D:
        """Transform a direction (no translation)"""
        return self.rotation.rotate_vector(direction)
    
    def inverse_transform_point(self, world_point: Vector3D) -> Vector3D:
        """Transform a point from world to local space"""
        relative = world_point - self.position
        unrotated = self.rotation.inverse.rotate_vector(relative)
        return Vector3D(
            unrotated.x / self.scale.x if self.scale.x != 0 else 0,
            unrotated.y / self.scale.y if self.scale.y != 0 else 0,
            unrotated.z / self.scale.z if self.scale.z != 0 else 0
        )
    
    def lerp(self, other: 'Transform', t: float) -> 'Transform':
        """Interpolate between transforms"""
        return Transform(
            self.position.lerp(other.position, t),
            self.rotation.slerp(other.rotation, t),
            self.scale.lerp(other.scale, t)
        )
    
    @property
    def forward(self) -> Vector3D:
        return self.rotation.rotate_vector(Vector3D.forward())
    
    @property
    def right(self) -> Vector3D:
        return self.rotation.rotate_vector(Vector3D.right())
    
    @property
    def up(self) -> Vector3D:
        return self.rotation.rotate_vector(Vector3D.up())


# =============================================================================
# ENHANCED COLOR PRIMITIVES
# =============================================================================

@dataclass(frozen=True, slots=True)
class Color:
    """
    RGBA color with float components [0-1].
    
    Provides color space conversions and operations.
    """
    r: float
    g: float
    b: float
    a: float = 1.0
    
    @classmethod
    def rgb(cls, r: int, g: int, b: int, a: int = 255) -> 'Color':
        """Create from 0-255 RGB values"""
        return cls(r / 255, g / 255, b / 255, a / 255)
    
    @classmethod
    def hex(cls, hex_str: str) -> 'Color':
        """Create from hex string (#RGB, #RGBA, #RRGGBB, #RRGGBBAA)"""
        h = hex_str.lstrip('#')
        if len(h) == 3:
            return cls(int(h[0]+h[0], 16)/255, int(h[1]+h[1], 16)/255, int(h[2]+h[2], 16)/255)
        elif len(h) == 4:
            return cls(int(h[0]+h[0], 16)/255, int(h[1]+h[1], 16)/255, int(h[2]+h[2], 16)/255, int(h[3]+h[3], 16)/255)
        elif len(h) == 6:
            return cls(int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255)
        elif len(h) == 8:
            return cls(int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255, int(h[6:8], 16)/255)
        raise ValueError(f"Invalid hex color: {hex_str}")
    
    @classmethod
    def hsl(cls, h: float, s: float, l: float, a: float = 1.0) -> 'Color':
        """Create from HSL values (h: 0-360, s/l: 0-1)"""
        h = h / 360
        if s == 0:
            return cls(l, l, l, a)
        
        def hue_to_rgb(p, q, t):
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1/6: return p + (q - p) * 6 * t
            if t < 1/2: return q
            if t < 2/3: return p + (q - p) * (2/3 - t) * 6
            return p
        
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        return cls(
            hue_to_rgb(p, q, h + 1/3),
            hue_to_rgb(p, q, h),
            hue_to_rgb(p, q, h - 1/3),
            a
        )
    
    @classmethod
    def hsv(cls, h: float, s: float, v: float, a: float = 1.0) -> 'Color':
        """Create from HSV values (h: 0-360, s/v: 0-1)"""
        h = (h / 60) % 6
        i = int(h)
        f = h - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        
        if i == 0: return cls(v, t, p, a)
        if i == 1: return cls(q, v, p, a)
        if i == 2: return cls(p, v, t, a)
        if i == 3: return cls(p, q, v, a)
        if i == 4: return cls(t, p, v, a)
        return cls(v, p, q, a)
    
    # Preset colors
    @classmethod
    def white(cls) -> 'Color': return cls(1, 1, 1, 1)
    @classmethod  
    def black(cls) -> 'Color': return cls(0, 0, 0, 1)
    @classmethod
    def red(cls) -> 'Color': return cls(1, 0, 0, 1)
    @classmethod
    def green(cls) -> 'Color': return cls(0, 1, 0, 1)
    @classmethod
    def blue(cls) -> 'Color': return cls(0, 0, 1, 1)
    @classmethod
    def yellow(cls) -> 'Color': return cls(1, 1, 0, 1)
    @classmethod
    def cyan(cls) -> 'Color': return cls(0, 1, 1, 1)
    @classmethod
    def magenta(cls) -> 'Color': return cls(1, 0, 1, 1)
    @classmethod
    def transparent(cls) -> 'Color': return cls(0, 0, 0, 0)
    
    @cached_property
    def rgb_int(self) -> Tuple[int, int, int]:
        """Convert to 0-255 RGB tuple"""
        return (
            int(max(0, min(1, self.r)) * 255),
            int(max(0, min(1, self.g)) * 255),
            int(max(0, min(1, self.b)) * 255)
        )
    
    @cached_property
    def rgba_int(self) -> Tuple[int, int, int, int]:
        """Convert to 0-255 RGBA tuple"""
        return (*self.rgb_int, int(max(0, min(1, self.a)) * 255))
    
    @cached_property
    def hex_rgb(self) -> str:
        """Convert to #RRGGBB"""
        r, g, b = self.rgb_int
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @cached_property
    def hex_rgba(self) -> str:
        """Convert to #RRGGBBAA"""
        r, g, b, a = self.rgba_int
        return f"#{r:02x}{g:02x}{b:02x}{a:02x}"
    
    @cached_property
    def luminance(self) -> float:
        """Relative luminance (Y)"""
        return 0.2126 * self.r + 0.7152 * self.g + 0.0722 * self.b
    
    def to_hsl(self) -> Tuple[float, float, float]:
        """Convert to HSL (h: 0-360, s/l: 0-1)"""
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
    
    def lerp(self, other: 'Color', t: float) -> 'Color':
        """Linear interpolation"""
        return Color(
            self.r + (other.r - self.r) * t,
            self.g + (other.g - self.g) * t,
            self.b + (other.b - self.b) * t,
            self.a + (other.a - self.a) * t
        )
    
    def brighten(self, factor: float) -> 'Color':
        """Increase brightness"""
        return Color(
            min(1, self.r * (1 + factor)),
            min(1, self.g * (1 + factor)),
            min(1, self.b * (1 + factor)),
            self.a
        )
    
    def darken(self, factor: float) -> 'Color':
        """Decrease brightness"""
        return Color(
            self.r * (1 - factor),
            self.g * (1 - factor),
            self.b * (1 - factor),
            self.a
        )
    
    def with_alpha(self, alpha: float) -> 'Color':
        """Return color with different alpha"""
        return Color(self.r, self.g, self.b, alpha)
    
    def invert(self) -> 'Color':
        """Invert color"""
        return Color(1 - self.r, 1 - self.g, 1 - self.b, self.a)
    
    def grayscale(self) -> 'Color':
        """Convert to grayscale"""
        gray = self.luminance
        return Color(gray, gray, gray, self.a)
    
    def blend(self, other: 'Color', mode: str = 'normal') -> 'Color':
        """Blend with another color"""
        if mode == 'normal':
            return other.lerp(self, 1 - other.a)
        elif mode == 'multiply':
            return Color(self.r * other.r, self.g * other.g, self.b * other.b, self.a * other.a)
        elif mode == 'screen':
            return Color(
                1 - (1 - self.r) * (1 - other.r),
                1 - (1 - self.g) * (1 - other.g),
                1 - (1 - self.b) * (1 - other.b),
                1 - (1 - self.a) * (1 - other.a)
            )
        elif mode == 'overlay':
            def overlay_channel(a, b):
                return 2 * a * b if a < 0.5 else 1 - 2 * (1 - a) * (1 - b)
            return Color(
                overlay_channel(self.r, other.r),
                overlay_channel(self.g, other.g),
                overlay_channel(self.b, other.b),
                self.a
            )
        return self
    
    def __repr__(self) -> str:
        return f"Color({self.r:.2f}, {self.g:.2f}, {self.b:.2f}, {self.a:.2f})"


# =============================================================================
# TEMPORAL PRIMITIVES — Time and Duration
# =============================================================================

@dataclass(frozen=True, slots=True)
class Duration:
    """
    Time duration with multiple unit accessors.
    """
    _nanoseconds: int
    
    @classmethod
    def nanoseconds(cls, ns: int) -> 'Duration':
        return cls(ns)
    
    @classmethod
    def microseconds(cls, us: float) -> 'Duration':
        return cls(int(us * 1_000))
    
    @classmethod
    def milliseconds(cls, ms: float) -> 'Duration':
        return cls(int(ms * 1_000_000))
    
    @classmethod
    def seconds(cls, s: float) -> 'Duration':
        return cls(int(s * 1_000_000_000))
    
    @classmethod
    def minutes(cls, m: float) -> 'Duration':
        return cls(int(m * 60_000_000_000))
    
    @classmethod
    def hours(cls, h: float) -> 'Duration':
        return cls(int(h * 3_600_000_000_000))
    
    @classmethod
    def zero(cls) -> 'Duration':
        return cls(0)
    
    @property
    def ns(self) -> int: return self._nanoseconds
    
    @property
    def us(self) -> float: return self._nanoseconds / 1_000
    
    @property
    def ms(self) -> float: return self._nanoseconds / 1_000_000
    
    @property
    def s(self) -> float: return self._nanoseconds / 1_000_000_000
    
    @property
    def total_seconds(self) -> float: return self.s
    
    @property
    def total_minutes(self) -> float: return self.s / 60
    
    @property
    def total_hours(self) -> float: return self.s / 3600
    
    def __add__(self, other: 'Duration') -> 'Duration':
        return Duration(self._nanoseconds + other._nanoseconds)
    
    def __sub__(self, other: 'Duration') -> 'Duration':
        return Duration(self._nanoseconds - other._nanoseconds)
    
    def __mul__(self, factor: float) -> 'Duration':
        return Duration(int(self._nanoseconds * factor))
    
    def __truediv__(self, divisor: float) -> 'Duration':
        return Duration(int(self._nanoseconds / divisor))
    
    def __lt__(self, other: 'Duration') -> bool:
        return self._nanoseconds < other._nanoseconds
    
    def __le__(self, other: 'Duration') -> bool:
        return self._nanoseconds <= other._nanoseconds
    
    def __gt__(self, other: 'Duration') -> bool:
        return self._nanoseconds > other._nanoseconds
    
    def __ge__(self, other: 'Duration') -> bool:
        return self._nanoseconds >= other._nanoseconds
    
    def formatted(self) -> str:
        """Format as HH:MM:SS.mmm"""
        total_ms = self.ms
        hours = int(total_ms // 3_600_000)
        mins = int((total_ms % 3_600_000) // 60_000)
        secs = int((total_ms % 60_000) // 1000)
        ms = int(total_ms % 1000)
        return f"{hours:02d}:{mins:02d}:{secs:02d}.{ms:03d}"
    
    def __repr__(self) -> str:
        if self._nanoseconds < 1_000:
            return f"Duration({self._nanoseconds}ns)"
        elif self._nanoseconds < 1_000_000:
            return f"Duration({self.us:.1f}µs)"
        elif self._nanoseconds < 1_000_000_000:
            return f"Duration({self.ms:.2f}ms)"
        else:
            return f"Duration({self.s:.3f}s)"


@dataclass(frozen=True, slots=True)
class TimePoint:
    """
    A point in time (Unix timestamp with nanosecond precision).
    """
    _nanoseconds: int
    
    @classmethod
    def now(cls) -> 'TimePoint':
        return cls(int(time.time() * 1_000_000_000))
    
    @classmethod
    def from_timestamp(cls, ts: float) -> 'TimePoint':
        return cls(int(ts * 1_000_000_000))
    
    @classmethod
    def epoch(cls) -> 'TimePoint':
        return cls(0)
    
    @property
    def timestamp(self) -> float:
        return self._nanoseconds / 1_000_000_000
    
    @property
    def timestamp_ms(self) -> int:
        return self._nanoseconds // 1_000_000
    
    def elapsed_since(self, earlier: 'TimePoint') -> Duration:
        return Duration(self._nanoseconds - earlier._nanoseconds)
    
    def __add__(self, duration: Duration) -> 'TimePoint':
        return TimePoint(self._nanoseconds + duration._nanoseconds)
    
    def __sub__(self, other: Union['TimePoint', Duration]) -> Union['TimePoint', Duration]:
        if isinstance(other, TimePoint):
            return Duration(self._nanoseconds - other._nanoseconds)
        return TimePoint(self._nanoseconds - other._nanoseconds)
    
    def __lt__(self, other: 'TimePoint') -> bool:
        return self._nanoseconds < other._nanoseconds
    
    def __le__(self, other: 'TimePoint') -> bool:
        return self._nanoseconds <= other._nanoseconds
    
    def __gt__(self, other: 'TimePoint') -> bool:
        return self._nanoseconds > other._nanoseconds
    
    def __ge__(self, other: 'TimePoint') -> bool:
        return self._nanoseconds >= other._nanoseconds


# =============================================================================
# SERIALIZATION — Binary Transport
# =============================================================================

class BinaryEncoder:
    """
    Encode dimensional primitives to binary for transport.
    
    Wire format is compact and deterministic.
    """
    
    # Type tags
    TAG_VECTOR3D = 0x01
    TAG_QUATERNION = 0x02
    TAG_TRANSFORM = 0x03
    TAG_COLOR = 0x04
    TAG_DURATION = 0x05
    TAG_TIMEPOINT = 0x06
    
    @staticmethod
    def encode_vector3d(v: Vector3D) -> bytes:
        return struct.pack('>Bfff', BinaryEncoder.TAG_VECTOR3D, v.x, v.y, v.z)
    
    @staticmethod
    def encode_quaternion(q: Quaternion) -> bytes:
        return struct.pack('>Bffff', BinaryEncoder.TAG_QUATERNION, q.w, q.x, q.y, q.z)
    
    @staticmethod
    def encode_color(c: Color) -> bytes:
        return struct.pack('>Bffff', BinaryEncoder.TAG_COLOR, c.r, c.g, c.b, c.a)
    
    @staticmethod
    def encode_duration(d: Duration) -> bytes:
        return struct.pack('>Bq', BinaryEncoder.TAG_DURATION, d._nanoseconds)
    
    @staticmethod
    def encode_timepoint(t: TimePoint) -> bytes:
        return struct.pack('>Bq', BinaryEncoder.TAG_TIMEPOINT, t._nanoseconds)
    
    @staticmethod
    def decode(data: bytes) -> Any:
        tag = data[0]
        
        if tag == BinaryEncoder.TAG_VECTOR3D:
            _, x, y, z = struct.unpack('>Bfff', data[:13])
            return Vector3D(x, y, z)
        
        elif tag == BinaryEncoder.TAG_QUATERNION:
            _, w, x, y, z = struct.unpack('>Bffff', data[:17])
            return Quaternion(w, x, y, z)
        
        elif tag == BinaryEncoder.TAG_COLOR:
            _, r, g, b, a = struct.unpack('>Bffff', data[:17])
            return Color(r, g, b, a)
        
        elif tag == BinaryEncoder.TAG_DURATION:
            _, ns = struct.unpack('>Bq', data[:9])
            return Duration(ns)
        
        elif tag == BinaryEncoder.TAG_TIMEPOINT:
            _, ns = struct.unpack('>Bq', data[:9])
            return TimePoint(ns)
        
        raise ValueError(f"Unknown type tag: {tag}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Reactive
    'ReactiveValue',
    'ComputedValue',
    'Observable',
    'Observer',
    
    # Lazy
    'Lazy',
    
    # Vectors
    'Vector3D',
    'VectorBatch',
    
    # Rotation
    'Quaternion',
    'Transform',
    
    # Color
    'Color',
    
    # Time
    'Duration',
    'TimePoint',
    
    # Serialization
    'BinaryEncoder',
]
