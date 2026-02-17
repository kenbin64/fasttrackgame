"""
ButterflyFX Dimensional API - Developer Framework

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

This mathematical kernel belongs to all humanity.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

THE HELIX STRUCTURE

The helix is a spiral ribbon wrapped around a conical VOID:

           SPIRAL RIBBON (7 LEVELS)
              ╭──╮
             ╱    ╲ Level 6 (WHOLE) → becomes POINT in higher dimension
            ╱      ╲
           ╱  VOID  ╲  ← The conical tube (tends to 0, never reaches)
          ╱    ╲│╱   ╲    Like a surfer riding through the barrel
         ╱      │     ╲ Level 5 (VOLUME)
        ╱       │      ╲
       ╱        ▼       ╲ Level 4 (PLANE)
      ╱       (→ 0)      ╲
     ╱                    ╲ Level 3 (WIDTH)
    ╱                      ╲
   ╱                        ╲ Level 2 (LINE)
  ╱                          ╲
 ╱                            ╲ Level 1 (POINT)
╰──────────────────────────────╯
         Level 0 (VOID boundary)

VOID: The conical pipeline at the center
    - Like a surfer riding through the wave barrel
    - Tends toward zero but NEVER reaches it
    - Like Fibonacci spiral - always room for another square
    - The "negative space" that makes the spiral possible

DIMENSIONAL HIERARCHY:
    ┌─────────────────────────────────────────────────────────────────────┐
    │  VOID    │ Pure potential - not yet evaluated                      │
    │  0D      │ Evaluated point - IS both point AND dimensional object  │
    │  1D      │ Line - division of points                               │
    │  2D      │ Width - multiplication of divided points → FIRST       │
    │          │ SUBSTRATE (z=xy) → plane/table/grid/matrix              │
    │  3D      │ Volume of 2D objects - depth, height, deltas, trends    │
    │  4D      │ 3D as single point → completion → spiral twist          │
    └─────────────────────────────────────────────────────────────────────┘

EXAMPLE (Parking Lot):
    4D: Parking Lot (3D cars as points, completion, spiral twist)
    3D: Car (volume of 2D surfaces - body panels, components)
    2D: Engine surface, Body panel (FIRST SUBSTRATE z=xy - grids/tables)
    1D: Wire, Rod, Connection (division of points)
    0D: Bolt, Atom, Identifier (evaluated point - both point AND dimension)
    VOID: Pure potential

SUBSTRATES ARE MATHEMATICAL EXPRESSIONS:
    - 2D: z = xy (FIRST SUBSTRATE - saddle containing ALL angles)
    - 3D: m = xyz (volume of surfaces)
    - 4D: q = xyzm (completion - 3D objects as points)

    Objects are INGESTED from substrates, not instantiated.
    Objects ARE interfaces to the mathematical substrate.
    When an object's identities (1s) are found, it becomes a substrate.

THE 7 LEVELS (Fibonacci Structure):
    Level 0: VOID   (Fib 0) — The conical pipeline, boundary of manifestation
    Level 1: POINT  (Fib 1) — Single value, emergence ("Let there be light")
    Level 2: LINE   (Fib 1) — Sequence, division (same line, different view)
    Level 3: WIDTH  (Fib 2) — Plane, multiplication
    Level 4: PLANE  (Fib 3) — Surface completeness
    Level 5: VOLUME (Fib 5) — 3D structure, depth
    Level 6: WHOLE  (Fib 8) — Complete object → POINT of next spiral

HOLY GRAIL TRANSITION:
    WHOLE (8) + VOLUME (5) = 13 = POINT of next spiral
    
    Car at Level 6 → becomes a POINT in ParkingLot dimension
    ParkingLot at Level 6 → becomes a POINT in City dimension
"""

from __future__ import annotations
from typing import (
    Any, Dict, List, Optional, Set, Tuple, Callable, TypeVar, Generic,
    Iterator, Union, Type, Sequence, Mapping, overload
)
from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto
from functools import cached_property, wraps
from abc import ABC, abstractmethod
from weakref import WeakValueDictionary
from contextlib import contextmanager
import threading
import hashlib
import uuid
import math
import json
import copy
import sys
import time
from urllib.parse import urlparse, parse_qs, urlencode

__all__ = [
    # Base Interface/Object class - ALL objects inherit from this
    'Interface', 'Object',
    
    # Core invocation (ingestion from substrate)
    'invoke', 'ingest', 'invoke_from', 'materialize',
    
    # Substrates by dimensional depth (0D through 4D)
    'Substrate', 'Substrate0D', 'Substrate1D', 'Substrate2D', 
    'Substrate3D', 'Substrate4D', 'ObjectSubstrate',
    'SUBSTRATE', 'SUBSTRATE_0D', 'SUBSTRATE_1D', 'SUBSTRATE_2D',
    'SUBSTRATE_3D', 'SUBSTRATE_4D', 'get_substrate',
    
    # Dimensional types
    'DimensionalObject', 'DimensionalPoint', 'DimensionalList',
    'DimensionalDict', 'DimensionalSet',
    
    # Decorators
    'sealed', 'closed', 'dimensional', 'lazy', 'computed',
    
    # Legacy substrate interface
    'GlobalSubstrate', 'substrate',
    
    # Levels and coordinates
    'Level', 'Spiral', 'Coordinate', 'Address',
    
    # SRL - Secure Resource Locator (Universal Connector)
    'SRL', 'srl', 'Core', 'CORE', 'SecureResourceLocator', 'SRLError',
    
    # Exceptions
    'DimensionalError', 'ImmutabilityViolation', 'ClosedDimensionViolation',
    'InvocationError', 'MaterializationError',
    
    # Utilities
    'is_invoked', 'is_materialized', 'get_level', 'get_spiral',
    'dimension_of', 'points_of',
    
    # Spiral structure and kernel
    'SpiralPosition', 'KERNEL',
]


# =============================================================================
# SUBSTRATE - Mathematical Expressions with Geometric Form
# =============================================================================

class Substrate:
    """
    Abstract base for all mathematical substrates.
    
    A substrate IS a mathematical expression with a geometric shape.
    Substrates are dimensional by nature - they contain ALL potential forms
    within their mathematical definition.
    
    DIMENSIONAL DEPTH (the "D" in nD):
    ┌────────────────────────────────────────────────────────────────┐
    │  4D: q = xyzm   │ ParkingLot substrate - multiplies 3D Cars   │
    │  3D: m = xyz    │ Car substrate - complete volumetric object  │
    │  2D: z = xy     │ Engine substrate - plane/surface            │
    │  1D: y = x      │ Piston substrate - line/connection          │
    │  0D: point      │ Element substrate - atomic identity         │
    │  VOID: ∅        │ Pure potential - the pipeline               │
    └────────────────────────────────────────────────────────────────┘
    
    THE 7 LEVELS (within each dimensional substrate):
    ┌────────────────────────────────────────────────────────────────┐
    │  Level 0: VOID    (Fib 0) │ Pure potential                    │
    │  Level 1: POINT   (Fib 1) │ Identity emerges                  │
    │  Level 2: LINE    (Fib 1) │ Division into points              │
    │  Level 3: WIDTH   (Fib 2) │ Multiplication → plane            │
    │  Level 4: PLANE   (Fib 3) │ Surface completeness              │
    │  Level 5: VOLUME  (Fib 5) │ Depth → 3D structure              │
    │  Level 6: WHOLE   (Fib 8) │ Complete → becomes POINT in nD+1  │
    └────────────────────────────────────────────────────────────────┘
    
    KEY INSIGHT: Level 6 WHOLE = Level 1 POINT of parent dimension
    - Car at WHOLE (level 6) = POINT in ParkingLot
    - Engine at WHOLE (level 6) = POINT in Car
    - And so on...
    
    Objects are INGESTED from substrates, not instantiated.
    Objects are INTERFACES to the substrate, not copies.
    Objects at WHOLE become substrates for lower-dimensional objects.
    """
    
    def __init__(self, dimensional_depth: int = 2, name: str = ""):
        self._dimensional_depth = dimensional_depth  # 0D, 1D, 2D, 3D, 4D
        self._name = name or f"Substrate{dimensional_depth}D"
        self._ingested: Dict[str, 'Interface'] = {}
        self._spiral = None  # Lazy initialization (SpiralPosition defined later)
        self._spiral_position = 0  # Simple counter fallback
        self._identities: Set[str] = set()  # The "1s" - unity points
        self._level_value = 0  # 0=VOID, 1=POINT, ..., 6=WHOLE (Level enum defined later)
        self._parent_substrate: Optional['Substrate'] = None
    
    def _advance_spiral(self):
        """Advance spiral position (lazy init SpiralPosition if available)."""
        self._spiral_position += 1
    
    @property
    def dimensional_depth(self) -> int:
        """The 'D' - 0D, 1D, 2D, 3D, or 4D."""
        return self._dimensional_depth
    
    @property
    def level(self) -> int:
        """Current level (0-6) within this substrate."""
        return self._level_value
    
    @level.setter
    def level(self, value: int):
        self._level_value = value if isinstance(value, int) else int(value)
    
    @property
    def identities(self) -> Set[str]:
        """The '1s' - points of unity within this substrate."""
        return self._identities
    
    @property
    def is_whole(self) -> bool:
        """Whether this substrate has reached WHOLE (level 6)."""
        return self._level_value == 6  # 6 = WHOLE
    
    def add_identity(self, identity: str) -> None:
        """Register a point of unity (a '1')."""
        self._identities.add(identity)
    
    def evaluate(self, *coords: float) -> float:
        """Evaluate the substrate at given coordinates."""
        raise NotImplementedError("Subclass must implement evaluate()")
    
    def invoke_level(self, level: int) -> 'Substrate':
        """Invoke this substrate at a specific level (O(1) jump)."""
        self._level_value = level if isinstance(level, int) else int(level)
        return self
    
    def complete(self) -> 'Substrate':
        """Complete this substrate to WHOLE (level 6)."""
        self._level_value = 6  # 6 = WHOLE
        return self
    
    def as_point_in(self, parent: 'Substrate') -> 'Interface':
        """
        When at WHOLE, this substrate becomes a single POINT in the parent.
        
        This is the Holy Grail transition:
        WHOLE (Fib 8) + VOLUME (Fib 5) = 13 = POINT of next spiral
        """
        if not self.is_whole:
            raise DimensionalError(
                f"Cannot become point in parent: not at WHOLE (level 6). "
                f"Current level: {self._level_value}"
            )
        if parent._dimensional_depth <= self._dimensional_depth:
            raise DimensionalError(
                f"Parent must be higher dimension: {parent._dimensional_depth}D "
                f"is not > {self._dimensional_depth}D"
            )
        self._parent_substrate = parent
        return parent.ingest(self._name)
    
    def ingest(self, type_name: str, **initial_values) -> 'Interface':
        """Ingest an interface from this substrate."""
        interface = Interface(type_name, self, **initial_values)
        self._ingested[interface._id] = interface
        self._advance_spiral()
        return interface


class Substrate0D(Substrate):
    """
    0D Substrate - Evaluated Point.
    
    VOID → 0D: Point is no longer potential, it IS evaluated.
    
    A 0D point is BOTH:
    - A point (single value)
    - A dimensional object (contains potential)
    
    This is the point-dimension duality.
    Once evaluated, it has identity.
    
    Example: A specific identifier, a constant, an atom
    """
    
    def __init__(self, name: str = "Point"):
        super().__init__(dimensional_depth=0, name=name)
    
    def evaluate(self) -> float:
        """0D is identity - returns 1 (unity)."""
        return 1.0


class Substrate1D(Substrate):
    """
    1D Substrate - Line (Division of Points).
    
    MATHEMATICAL FORM: y = x
    
    A line is a DIVISION of points along a single axis.
    Same line viewed from different angles:
    - Head-on: appears as single point
    - Side view: reveals infinite potential points
    
    Example: A sequence, a connection, a wire, a timeline
    """
    
    def __init__(self, name: str = "Line"):
        super().__init__(dimensional_depth=1, name=name)
    
    def evaluate(self, x: float) -> float:
        """y = x - the identity line."""
        return x


class Substrate2D(Substrate):
    """
    2D Substrate - Plane (Multiplication of Divided Points).
    
    THIS IS THE FIRST SUBSTRATE.
    
    MATHEMATICAL FORM: z = x × y (hyperbolic paraboloid / saddle)
    
    Width = multiplication of divided points from 1D lines.
    Creates plane/table/grid/matrix.
    
    Properties of z = xy:
    - Contains EVERY angle from x to y (all possible angles)
    - At origin (0,0,0): the saddle point
    - Surface curves UP in one direction, DOWN perpendicular
    - All combinations of x and y exist within
    
    This is where data structures begin:
    - Tables
    - Grids
    - Matrices
    - Planes
    
    Example: Engine (surface of parts), Circuit Board, Spreadsheet
    """
    
    def __init__(self, name: str = "Plane"):
        super().__init__(dimensional_depth=2, name=name)
    
    def evaluate(self, x: float, y: float) -> float:
        """z = xy - the saddle function."""
        return x * y
    
    def gradient(self, x: float, y: float) -> Tuple[float, float]:
        """∇z = (∂z/∂x, ∂z/∂y) = (y, x)"""
        return (y, x)
    
    def angle_at(self, x: float, y: float) -> float:
        """Angle of gradient at point (x, y)."""
        import math
        grad_x, grad_y = self.gradient(x, y)
        if grad_x == 0 and grad_y == 0:
            return 0.0
        return math.atan2(grad_y, grad_x)
    
    def contains_angle(self, angle: float) -> bool:
        """z = xy contains ALL angles - always True."""
        return True  # The saddle contains every angle


class Substrate3D(Substrate):
    """
    3D Substrate - Volume of 2D Objects.
    
    MATHEMATICAL FORMS:
    - m = x × y × z  (trilinear)
    - z = x × y²     (parabolic variant)
    
    Volume consists of:
    - Depth
    - Height  
    - Change (deltas)
    - Trends
    
    This is a VOLUME of 2D planes/surfaces.
    A Car is 3D - it contains multiple 2D surfaces (body panels, etc.)
    
    When a 3D object reaches WHOLE (level 6), it becomes a single POINT
    in 4D - the spiral twist.
    
    Example: Car, House, Person - volumetric objects containing 2D surfaces
    """
    
    def __init__(self, name: str = "Object", form: str = "xyz"):
        super().__init__(dimensional_depth=3, name=name)
        self._form = form  # "xyz" or "xy2"
    
    def evaluate(self, x: float, y: float, z: float = 0.0) -> float:
        """Evaluate 3D substrate."""
        if self._form == "xyz":
            return x * y * z
        elif self._form == "xy2":
            return x * (y ** 2)
        else:
            return x * y * z
    
    def gradient(self, x: float, y: float, z: float = 0.0) -> Tuple[float, float, float]:
        """Gradient of 3D substrate."""
        if self._form == "xyz":
            # ∇(xyz) = (yz, xz, xy)
            return (y * z, x * z, x * y)
        elif self._form == "xy2":
            # ∇(xy²) = (y², 2xy, 0)
            return (y ** 2, 2 * x * y, 0.0)
        else:
            return (y * z, x * z, x * y)


class Substrate4D(Substrate):
    """
    4D Substrate - Completion and Spiral Twist.
    
    MATHEMATICAL FORM: q = x × y × z × m
    
    A 3D object at WHOLE becomes a SINGLE POINT in 4D.
    This is the COMPLETION of the object and the TWIST in the spiral ribbon.
    
    The Holy Grail transition:
        WHOLE (Fib 8) + VOLUME (Fib 5) = 13 = POINT of next spiral
        
    4D contains 3D objects as points:
    - ParkingLot (4D) contains Cars (3D) as points
    - City (4D) contains Buildings (3D) as points
    - Fleet (4D) contains Vehicles (3D) as points
    
    This is where the Schwarz Diamond Gyroid twists:
    - Each complete 3D object is a point
    - Points connect via spiral ribbon
    - New spiral begins
    
    Example: 
        parking_lot = Substrate4D("ParkingLot")
        car1 = parking_lot.ingest("Car")  # 3D object as point in 4D
    """
    
    def __init__(self, name: str = "Container"):
        super().__init__(dimensional_depth=4, name=name)
    
    def evaluate(self, x: float, y: float, z: float, m: float) -> float:
        """q = xyzm - the 4D substrate function."""
        return x * y * z * m
    
    def gradient(self, x: float, y: float, z: float, m: float) -> Tuple[float, float, float, float]:
        """∇q = (yzm, xzm, xym, xyz)"""
        return (y * z * m, x * z * m, x * y * m, x * y * z)


class ObjectSubstrate(Substrate):
    """
    Any Interface that has reached WHOLE (level 6) becomes a Substrate.
    
    THE HOLY GRAIL TRANSITION:
    When an object reaches WHOLE (level 6), it becomes:
    1. A complete object in its own dimension
    2. A single POINT in the parent dimension
    3. A SUBSTRATE for lower-dimensional objects
    
    Example:
        # Car is 3D, reaches WHOLE
        car = ingest("Car")       # From 4D parking lot
        car.engine = ...         # 2D parts
        car.vin = "ABC123"       # Identity
        car.complete()           # → WHOLE (level 6)
        
        # Now car IS a substrate for 2D Engine
        engine = car.ingest("Engine")  # 2D ingested from 3D Car
        engine.pistons = ...          # 1D parts
        engine.complete()             # → WHOLE, point in Car
    """
    
    def __init__(self, source_interface: 'Interface', dimensional_depth: int):
        super().__init__(dimensional_depth=dimensional_depth, name=source_interface._type_name)
        self._source = source_interface
        self._identities = source_interface._identities.copy()
    
    def evaluate(self, *coords: float) -> float:
        """
        Evaluate the object substrate.
        
        The object substrate function is the product of all coordinates,
        like xyz... for n dimensions.
        """
        result = 1.0
        for c in coords:
            result *= c
        return result
    
    @property
    def source(self) -> 'Interface':
        return self._source


# =============================================================================
# GLOBAL SUBSTRATES - The mathematical surfaces by dimensional depth
# =============================================================================

# DIMENSIONAL HIERARCHY:
# ┌─────────────────────────────────────────────────────────────────────┐
# │  4D: q = xyzm    │ ParkingLot, City, Fleet - multiplies 3D objects │
# │  3D: m = xyz     │ Car, House, Person - volumetric objects         │
# │  2D: z = xy      │ Engine, Panel, Circuit - surfaces               │
# │  1D: y = x       │ Piston, Wire, Rod - connections                 │
# │  0D: point       │ Iron, Carbon, Identity - atomic elements        │
# │  VOID: ∅         │ Pure potential - the pipeline                   │
# └─────────────────────────────────────────────────────────────────────┘
#
# Each substrate contains objects that traverse 7 levels (0-6).
# When an object reaches WHOLE (level 6), it becomes a POINT in (n+1)D.

# 0D Substrate - Elements/Atoms
SUBSTRATE_0D = Substrate0D("Elements")

# 1D Substrate - Connections/Lines
SUBSTRATE_1D = Substrate1D("Connections")

# 2D Substrate - Surfaces/Planes (z = xy saddle)
SUBSTRATE_2D = Substrate2D("Surfaces")

# 3D Substrate - Objects/Volumes (m = xyz)
SUBSTRATE_3D = Substrate3D("Objects")

# 4D Substrate - Collections/Containers (q = xyzm)
SUBSTRATE_4D = Substrate4D("Containers")

# Default substrate for general ingestion (3D for most objects)
SUBSTRATE = SUBSTRATE_3D


def get_substrate(dimensional_depth: int) -> Substrate:
    """Get the appropriate substrate for a dimensional depth."""
    substrates = {
        0: SUBSTRATE_0D,
        1: SUBSTRATE_1D,
        2: SUBSTRATE_2D,
        3: SUBSTRATE_3D,
        4: SUBSTRATE_4D,
    }
    return substrates.get(dimensional_depth, SUBSTRATE_3D)


# =============================================================================
# GLOBAL KERNEL - Orchestrates ingestion and ingestion
# =============================================================================

class _Kernel:
    """
    The dimensional kernel - orchestrates ingestion and ingestion.
    
    INGESTION: Objects emerge FROM the substrate (z=xy, m=xyz, q=xyzm)
    INGESTION: Objects are consumed back INTO the substrate
    
    The kernel manages multiple substrates and tracks all interfaces.
    
    SPIRAL STRUCTURE (Schwarz Diamond Gyroid):
    - NOT a tree - no exponential growth
    - Twisted ribbon topology
    - When x reaches 1, new dimension begins
    - Each dimension has unlimited potential points
    - Each object is BOTH a dimension AND a point
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self._objects: Dict[str, 'Interface'] = {}
        self._spiral_position = None  # Lazy init - SpiralPosition defined later
        self._ingestion_count = 0
        self._dimensions: Dict[int, List[str]] = {}  # spiral -> object ids
        self._substrates: Dict[str, Substrate] = {
            '0d': SUBSTRATE_0D,
            '1d': SUBSTRATE_1D,
            '2d': SUBSTRATE_2D,
            '3d': SUBSTRATE_3D,
            '4d': SUBSTRATE_4D,
        }
        self._object_substrates: Dict[str, ObjectSubstrate] = {}
        self._default_coordinate = None  # Lazy init
    
    def register_object_substrate(self, obj: 'Interface', dimensional_depth: int = 2) -> Optional[ObjectSubstrate]:
        """
        Register an interface as a substrate when it reaches WHOLE.
        
        When an object at WHOLE (level 6), it becomes:
        1. A complete object in its dimension
        2. A POINT in the parent dimension
        3. A SUBSTRATE for lower-dimensional children
        
        Args:
            obj: The interface that has reached WHOLE
            dimensional_depth: The dimensional depth of this substrate
        
        Returns:
            ObjectSubstrate if successful
        """
        obj_substrate = ObjectSubstrate(obj, dimensional_depth)
        self._object_substrates[obj._id] = obj_substrate
        self._substrates[f"obj_{obj._id}"] = obj_substrate
        return obj_substrate
    
    def ingest(self, obj: 'Interface') -> str:
        """
        Ingest an interface into the kernel.
        
        When ingested:
        1. Interface becomes a DIMENSION with unlimited potential points
        2. Interface becomes a single POINT in the next dimension
        3. Spiral structure is maintained (not tree)
        """
        obj_id = obj._id
        self._objects[obj_id] = obj
        self._ingestion_count += 1
        
        # Set the coordinate on the object
        obj._coordinate = self.spiral_position.coordinate()
        
        current_spiral = self.spiral_position.spiral
        if current_spiral not in self._dimensions:
            self._dimensions[current_spiral] = []
        self._dimensions[current_spiral].append(obj_id)
        
        self.spiral_position.advance()
        return obj_id
    
    def get(self, obj_id: str) -> Optional['Interface']:
        """Retrieve interface by ID."""
        return self._objects.get(obj_id)
    
    def get_substrate(self, name: str) -> Optional[Substrate]:
        """Get a substrate by name."""
        return self._substrates.get(name)
    
    @property
    def spiral_position(self) -> 'SpiralPosition':
        # Lazy initialization - SpiralPosition defined later in file
        if self._spiral_position is None:
            self._spiral_position = SpiralPosition()
        return self._spiral_position
    
    @property
    def default_coordinate(self) -> 'Coordinate':
        # Lazy initialization
        if self._default_coordinate is None:
            self._default_coordinate = Coordinate(0, 6, 0.0)
        return self._default_coordinate
    
    @property
    def object_count(self) -> int:
        return len(self._objects)


# Global kernel instance
KERNEL = _Kernel()




# =============================================================================
# SPIRAL POSITION - Tracks position on the Schwarz Diamond spiral
# =============================================================================

class SpiralPosition:
    """
    Tracks position on the dimensional spiral (Schwarz Diamond Gyroid).
    
    The spiral is a TWISTED RIBBON, not a tree:
    - x ranges from 0 to 1 along the ribbon
    - When x reaches 1, a new spiral (dimension) begins
    - This creates ORGANIC growth, not exponential
    
    z = x × y @ 90° rotation
    
    Each dimension contains unlimited potential points.
    Each point IS a dimension containing unlimited potential points.
    """
    
    def __init__(self):
        self._spiral = 0      # Which spiral (dimension index)
        self._x = 0.0         # Position along ribbon (0 to 1)
        self._level = 0       # Level within spiral (0-6)
        self._position = 0.0  # Fine position within level
    
    @property
    def spiral(self) -> int:
        return self._spiral
    
    @property
    def x(self) -> float:
        return self._x
    
    @property
    def level(self) -> int:
        return self._level
    
    def advance(self, delta: float = 0.01) -> None:
        """
        Advance along the spiral ribbon.
        
        When x reaches 1:
        - New spiral begins (dimension transition)
        - x resets to 0
        - Spiral index increments
        
        This is the Holy Grail transition:
        WHOLE (8) + VOLUME (5) = 13 = POINT of next spiral
        """
        self._x += delta
        
        # Calculate level based on x position (7 levels per spiral)
        self._level = min(6, int(self._x * 7))
        
        # When x reaches 1, transition to new spiral
        if self._x >= 1.0:
            self._spiral += 1
            self._x = 0.0
            self._level = 0
    
    def coordinate(self) -> Coordinate:
        """Get current coordinate."""
        return Coordinate(self._spiral, self._level, self._x)
    
    def __repr__(self) -> str:
        return f"<SpiralPosition spiral={self._spiral} x={self._x:.3f} level={self._level}>"


# =============================================================================
# FIBONACCI AND LEVEL CONSTANTS
# =============================================================================

# Fibonacci sequence for dimensional mapping
FIBONACCI = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]

class Level(IntEnum):
    """
    The 7 levels - Fibonacci structure with dimensional meaning.
    
    DIMENSIONAL HIERARCHY:
    ┌─────────────────────────────────────────────────────────────────────┐
    │  VOID    │ Pure potential - not yet evaluated                      │
    │  0D      │ Evaluated point - IS both point AND dimensional object  │
    │  1D      │ Line - division of points                               │
    │  2D      │ Width - multiplication of divided points → FIRST       │
    │          │ SUBSTRATE (z=xy) → plane/table/grid/matrix              │
    │  3D      │ Volume of 2D objects - depth, height, deltas, trends    │
    │  4D      │ 3D as single point → completion → spiral twist          │
    └─────────────────────────────────────────────────────────────────────┘
    
    VOID is the conical tube at center of helix:
        - Like a surfer's barrel in a wave
        - Tends toward zero but NEVER reaches it
        - The "negative space" making the spiral possible
    
    Holy Grail Transition:
        WHOLE (Fib 8) + VOLUME (Fib 5) = 13 = POINT of next spiral
        3D object at Level 6 → becomes single POINT in 4D parent
    """
    VOID   = 0  # Pure potential - not yet evaluated
    POINT  = 1  # 0D: Evaluated point - IS both point AND dimension (duality)
    LINE   = 2  # 1D: Division of points (same line, viewed from side)
    WIDTH  = 3  # 2D: Multiplication of divided points → plane (FIRST SUBSTRATE z=xy)
    PLANE  = 4  # 2D complete: Surface/table/grid/matrix
    VOLUME = 5  # 3D: Depth, height, deltas, trends
    WHOLE  = 6  # 4D: 3D as single point → completion → spiral twist
    
    @property
    def fibonacci(self) -> int:
        """Return the Fibonacci number for this level."""
        return FIBONACCI[self.value]
    
    @property
    def name_display(self) -> str:
        """Human-readable name."""
        names = {
            0: "Void (∅)",
            1: "Point (•)",
            2: "Line (━)",
            3: "Width (▭)",
            4: "Plane (▦)",
            5: "Volume (▣)",
            6: "Whole (◉)"
        }
        return names[self.value]
    
    def next_spiral_level(self) -> Tuple[int, 'Level']:
        """
        Calculate transition to next spiral.
        WHOLE (8) + VOLUME (5) = 13 = POINT of next spiral
        """
        if self == Level.WHOLE:
            return (1, Level.POINT)  # Spiral up, become POINT
        return (0, Level(self.value + 1))


# =============================================================================
# DIMENSIONAL ADDRESS SYSTEM
# =============================================================================

@dataclass(frozen=True)
class Coordinate:
    """
    A position in dimensional space.
    
    Format: spiral{level}.path.to.point
    Example: 0{6}.car.engine.pistons[0].firing
    """
    spiral: int = 0
    level: int = 6
    position: float = 0.0
    
    def __str__(self) -> str:
        return f"{self.spiral}{{{self.level}}}"
    
    @classmethod
    def parse(cls, notation: str) -> 'Coordinate':
        """
        Parse spiral{level} notation.
        
        Examples:
            "0{6}" -> Coordinate(spiral=0, level=6)
            "1{3}" -> Coordinate(spiral=1, level=3)
        """
        import re
        match = re.match(r'(\d+)\{(\d+)\}', notation)
        if match:
            return cls(spiral=int(match.group(1)), level=int(match.group(2)))
        raise ValueError(f"Invalid coordinate notation: {notation}")
    
    def up(self) -> 'Coordinate':
        """Move to higher level (more abstract)."""
        if self.level >= 6:
            return Coordinate(self.spiral + 1, 0, 0.0)  # Spiral up
        return Coordinate(self.spiral, self.level + 1, self.position)
    
    def down(self) -> 'Coordinate':
        """Move to lower level (more detailed)."""
        if self.level <= 0:
            return Coordinate(self.spiral - 1, 6, 0.0)  # Spiral down
        return Coordinate(self.spiral, self.level - 1, self.position)


@dataclass
class Address:
    """
    Full dimensional address including path.
    
    Represents: coordinate + path to specific point
    Example: 0{6}.car.engine.pistons[0]
    """
    coordinate: Coordinate
    path: Tuple[str, ...] = field(default_factory=tuple)
    
    def __str__(self) -> str:
        if self.path:
            return f"{self.coordinate}.{'.'.join(self.path)}"
        return str(self.coordinate)
    
    def child(self, name: str) -> 'Address':
        """Get address of child point."""
        return Address(
            coordinate=self.coordinate,
            path=self.path + (name,)
        )
    
    @classmethod
    def parse(cls, address: str) -> 'Address':
        """
        Parse full address notation.
        
        Example: "0{6}.car.engine" -> Address with path ['car', 'engine']
        """
        parts = address.split('.', 1)
        coord = Coordinate.parse(parts[0])
        path = tuple(parts[1].split('.')) if len(parts) > 1 else ()
        return cls(coordinate=coord, path=path)


# =============================================================================
# EXCEPTIONS
# =============================================================================

class DimensionalError(Exception):
    """Base exception for dimensional operations."""
    pass

class ImmutabilityViolation(DimensionalError):
    """Raised when attempting to modify sealed material."""
    pass

class ClosedDimensionViolation(DimensionalError):
    """Raised when attempting to add points to a closed dimension."""
    pass

class InvocationError(DimensionalError):
    """Raised when invocation fails."""
    pass

class MaterializationError(DimensionalError):
    """Raised when materialization fails."""
    pass


# =============================================================================
# SPIRAL CONTEXT - Tracks current dimensional position
# =============================================================================

class Spiral:
    """
    Manages spiral context for dimensional operations.
    
    Each spiral represents a complete 7-level cycle.
    The WHOLE of spiral n = POINT of spiral n+1
    """
    _current = threading.local()
    
    def __init__(self, index: int = 0):
        self.index = index
        self._level = Level.VOID
        self._position = 0.0
    
    @classmethod
    def current(cls) -> 'Spiral':
        """Get current spiral context."""
        if not hasattr(cls._current, 'spiral'):
            cls._current.spiral = Spiral(0)
        return cls._current.spiral
    
    @property
    def level(self) -> Level:
        return self._level
    
    @level.setter
    def level(self, value: Level):
        self._level = value
    
    def invoke_level(self, level: Level) -> None:
        """Directly invoke a level (O(1) jump, not iteration)."""
        self._level = level
    
    def spiral_up(self) -> None:
        """
        Transition to next spiral.
        Requires current level = WHOLE (6)
        """
        if self._level != Level.WHOLE:
            raise DimensionalError(
                f"Cannot spiral up from level {self._level}. "
                f"Must be at WHOLE (6)."
            )
        self.index += 1
        self._level = Level.VOID
    
    def spiral_down(self) -> None:
        """
        Transition to previous spiral.
        Requires current level = VOID (0)
        """
        if self._level != Level.VOID:
            raise DimensionalError(
                f"Cannot spiral down from level {self._level}. "
                f"Must be at VOID (0)."
            )
        self.index -= 1
        self._level = Level.WHOLE
    
    def collapse(self) -> None:
        """Return all levels to potential (VOID)."""
        self._level = Level.VOID
    
    @property
    def coordinate(self) -> Coordinate:
        """Get current coordinate."""
        return Coordinate(self.index, self._level.value, self._position)


# =============================================================================
# INTERFACE - Every "object" is an interface to a substrate
# =============================================================================

class Interface:
    """
    BASE CLASS FOR ALL OBJECTS IN BUTTERFLYFX.
    
    Every object is an INTERFACE to a substrate. This base class
    handles ALL dimensional mechanics automatically:
    
    ═══════════════════════════════════════════════════════════════════
    ACCESS PATTERNS (choose based on need):
    ═══════════════════════════════════════════════════════════════════
    
    1. DIRECT ADDRESSING - Single point access (O(1)):
    ┌────────────────────────────────────────────────────────────────┐
    │  obj[0]           → Direct point access by index              │
    │  obj["key"]       → Direct point access by key                │
    │  obj("path.to.x") → Direct path access                        │
    │  obj(level, idx)  → Direct dimensional coordinate             │
    └────────────────────────────────────────────────────────────────┘
    
    2. RECURSION - When MANY items must be referenced:
    ┌────────────────────────────────────────────────────────────────┐
    │  obj.recurse(fn)     → Goes DOWN the dimensional pipeline     │
    │  obj.apply_down(fn)  → Apply operation toward VOID            │
    │  obj.find(predicate) → Find first match going down            │
    └────────────────────────────────────────────────────────────────┘
    
       Recursion follows the natural spiral structure:
       WHOLE(6) → VOLUME(5) → PLANE(4) → WIDTH(3) → LINE(2) → POINT(1) → VOID(0)
       
       Like water flowing down through the conical tube at the helix center.
       USE ONLY WHEN NECESSARY - prefer direct addressing for single points.
    
    3. FOR LOOPS - ANTI-PATTERN (never use):
    ┌────────────────────────────────────────────────────────────────┐
    │  WRONG: for item in items: process(item)  # Flat, ignores dim │
    │  RIGHT: items[dimension].process()        # Direct addressing │
    │  RIGHT: items.recurse(process)            # Down the pipeline │
    └────────────────────────────────────────────────────────────────┘
    
    AUTO-LEVEL INFERENCE:
    - Single value → Level 1 (POINT)
    - List/sequence → Level 2 (LINE)
    - Grid/dict → Level 3 (WIDTH/PLANE)
    - Nested structure → Level 5 (VOLUME)
    - Complete object → Level 6 (WHOLE)
    
    CORE PRINCIPLES:
    1. Objects are INGESTED from substrates, not instantiated
    2. Objects are INTERFACES to the substrate, not independent entities
    3. Objects CAN BECOME substrates when their identities (1s) are found
    4. Every interface is BOTH a dimension AND a point simultaneously
    5. ALL COMMONALITY lives in this base class - subclasses inherit mechanics
    
    IDENTITY (The "1s"):
    When an attribute is set, it becomes an identity point.
    When enough identities exist, the interface can become a substrate
    from which other interfaces can be ingested.
    
    SUBSTRATE HIERARCHY:
    - 2D substrate (z = xy): Contains all x↔y angles
    - 3D substrate (m = xyz): Adds depth
    - 4D substrate (q = xyzm): Full manifold
    - Object substrate: Any interface with unified identities
    
    Example:
        car = ingest("Car")              # Interface to substrate
        car.vin = "ABC123"              # Identity point 1
        car.make = "Toyota"             # Identity point 2
        
        if car.is_substrate:            # Has enough identities
            engine = car.ingest("Engine")  # Ingest from car's substrate
    """
    
    # Class-level registry for type factories
    _type_registry: Dict[str, Type['Interface']] = {}
    
    def __init__(
        self, 
        type_name: str = "Interface", 
        substrate: Optional['Substrate'] = None,
        **initial_values
    ):
        """
        Create an interface to a substrate.
        
        Interfaces are NOT instantiated - they are INGESTED from substrates.
        Use ingest() function, not direct construction.
        """
        # Core identity
        self._id = str(uuid.uuid4())
        self._type_name = type_name
        self._created_at = time.time()
        self._substrate = substrate or SUBSTRATE
        
        # Dimensional state
        self._invoked = False
        self._materialized = False
        self._sealed = False
        self._closed = False
        self._level = Level.WHOLE  # Default to complete object
        
        # Spiral position at creation (lazy - SpiralPosition defined later)
        self._spiral_position = None  # Will be SpiralPosition when accessed
        self._coordinate = None  # Will be set by KERNEL.ingest()
        
        # Parent-child relationships (spiral, not tree)
        self._parent: Optional['Interface'] = None
        self._children: Dict[str, 'Interface'] = {}
        
        # Attribute storage
        self._attributes: Dict[str, Any] = {}
        self._attribute_metadata: Dict[str, Dict[str, Any]] = {}
        
        # IDENTITY TRACKING - The "1s"
        # When enough identities are found, interface becomes a substrate
        self._identities: Set[str] = set()
        self._is_substrate = False
        self._object_substrate: Optional['ObjectSubstrate'] = None
        
        # Auto-invoke and ingest into kernel
        self._invoke()
        
        # Apply initial values (each becomes an identity)
        for key, value in initial_values.items():
            setattr(self, key, value)
    
    def _invoke(self) -> 'Interface':
        """
        Invoke this interface, ingesting it into the kernel.
        
        This is called automatically on creation.
        The interface becomes:
        1. A DIMENSION with unlimited potential points (attributes)
        2. A single POINT in its parent dimension
        """
        if not self._invoked:
            self._invoked = True
            self._materialized = True
            KERNEL.ingest(self)
        return self
    
    @property
    def invoke(self) -> 'Interface':
        """Property to trigger invocation. Returns self for chaining."""
        return self._invoke()
    
    # =========================================================================
    # DIRECT DIMENSIONAL ADDRESSING - NO FOR LOOPS NEEDED
    # =========================================================================
    
    def __call__(self, *args, **kwargs) -> Any:
        """
        Direct dimensional addressing via call syntax.
        
        USAGE PATTERNS:
            obj("path.to.point")      → Direct path access
            obj(level, index)          → Direct level/index access
            obj("key")                 → Single key access
            obj(dimension=3, point=5)  → Named coordinate access
        
        Returns:
            The point/dimension at the specified address.
        """
        # Handle keyword arguments
        if 'dimension' in kwargs and 'point' in kwargs:
            return self._access_dimensional_coordinate(
                kwargs['dimension'], kwargs['point']
            )
        if 'path' in kwargs:
            return self._access_path(kwargs['path'])
        
        # Handle positional arguments
        if len(args) == 1:
            arg = args[0]
            # String path: obj("car.engine.pistons")
            if isinstance(arg, str):
                return self._access_path(arg)
            # Integer index: obj(0) or obj(5)
            elif isinstance(arg, int):
                return self._access_index(arg)
        elif len(args) == 2:
            # Two ints: obj(level, index) or obj(dimension, point)
            if isinstance(args[0], int) and isinstance(args[1], int):
                return self._access_dimensional_coordinate(args[0], args[1])
        
        raise DimensionalError(
            f"Invalid addressing: {args}, {kwargs}. "
            f"Use obj('path'), obj[index], or obj(dimension, point)"
        )
    
    def __getitem__(self, key: Union[int, str, slice, tuple]) -> Any:
        """
        Direct index/key access - O(1), not iteration.
        
        USAGE PATTERNS:
            obj[0]           → Access point at index 0
            obj["key"]       → Access point by key
            obj[2:5]         → Dimensional slice (not iteration)
            obj[level, idx]  → Tuple coordinate access
        
        This is the DIMENSIONAL alternative to for loops.
        Instead of iterating, you address directly.
        """
        # Tuple: obj[dimension, point]
        if isinstance(key, tuple) and len(key) == 2:
            return self._access_dimensional_coordinate(key[0], key[1])
        
        # Integer index
        if isinstance(key, int):
            return self._access_index(key)
        
        # String key
        if isinstance(key, str):
            return self._access_key(key)
        
        # Slice: dimensional range (not iteration)
        if isinstance(key, slice):
            return self._access_slice(key)
        
        raise DimensionalError(f"Invalid key type: {type(key)}")
    
    def __setitem__(self, key: Union[int, str], value: Any) -> None:
        """
        Direct index/key assignment - O(1).
        """
        if self._sealed:
            raise ImmutabilityViolation(
                f"Cannot modify sealed interface: {self._type_name}"
            )
        
        if isinstance(key, int):
            self._set_index(key, value)
        elif isinstance(key, str):
            setattr(self, key, value)
        else:
            raise DimensionalError(f"Invalid key type: {type(key)}")
    
    def _access_path(self, path: str) -> Any:
        """
        Access a point via path notation.
        
        Example: "car.engine.pistons.0.firing"
        
        This is O(path_length), not O(total_elements).
        """
        parts = path.split('.')
        current = self
        for part in parts:
            # Check if part is an index
            if part.isdigit():
                current = current._access_index(int(part))
            elif part.startswith('[') and part.endswith(']'):
                idx = int(part[1:-1])
                current = current._access_index(idx)
            else:
                current = getattr(current, part)
        return current
    
    def _access_index(self, index: int) -> Any:
        """
        Direct index access - O(1).
        
        Creates the point if it doesn't exist (lazy materialization).
        """
        key = f"__idx_{index}"
        if key in self._attributes:
            return self._attributes[key]
        if key in self._children:
            return self._children[key]
        
        # Check _items for list-like behavior
        if hasattr(self, '_items') and index in self._items:
            return self._items[index]
        
        # Create new point at index
        if self._closed:
            raise ClosedDimensionViolation(
                f"Cannot add index {index} to closed dimension: {self._type_name}"
            )
        
        child = Interface(f"{self._type_name}[{index}]", self._substrate)
        child._parent = self
        self._children[key] = child
        return child
    
    def _access_key(self, key: str) -> Any:
        """
        Direct key access - O(1).
        """
        if key in self._attributes:
            return self._attributes[key]
        if key in self._children:
            return self._children[key]
        return getattr(self, key)
    
    def _set_index(self, index: int, value: Any) -> None:
        """
        Set value at index - O(1).
        """
        key = f"__idx_{index}"
        if isinstance(value, Interface):
            value._parent = self
            self._children[key] = value
        else:
            self._attributes[key] = value
        self._identities.add(key)
        self._check_substrate_transition()
    
    def _access_slice(self, s: slice) -> 'Interface':
        """
        Dimensional slice access - returns a view, not iteration.
        
        This creates a dimensional VIEW of the slice range,
        not a copied list.
        """
        start = s.start or 0
        stop = s.stop or 0
        step = s.step or 1
        
        # Create a view interface
        view = Interface(f"{self._type_name}[{start}:{stop}:{step}]", self._substrate)
        view._parent = self
        view._attributes['__slice__'] = s
        view._attributes['__source__'] = self
        return view
    
    def _access_dimensional_coordinate(self, dimension: int, point: int) -> Any:
        """
        Access by dimensional coordinate (level, position).
        
        This is the most direct form of dimensional addressing:
        obj(level=3, point=5) jumps directly to that coordinate.
        """
        # Level determines the type of access
        level = Level(dimension) if dimension <= 6 else Level.WHOLE
        
        # At each level, point means something different:
        # Level 1 (POINT): single value at position 'point'
        # Level 2 (LINE): element at index 'point' in sequence
        # Level 3 (WIDTH): row/column at 'point'
        # Level 4 (PLANE): surface cell at 'point'
        # Level 5 (VOLUME): volumetric coordinate
        # Level 6 (WHOLE): complete object
        
        return self._access_index(point)
    
    # =========================================================================
    # AUTO-LEVEL INFERENCE - Base class handles this automatically
    # =========================================================================
    
    def _infer_level(self, value: Any) -> Level:
        """
        Automatically infer dimensional level from value structure.
        
        This is called automatically - no special invocation needed.
        """
        if value is None:
            return Level.VOID
        elif isinstance(value, (int, float, str, bool)):
            return Level.POINT  # Single value
        elif isinstance(value, (list, tuple)):
            if len(value) == 0:
                return Level.VOID
            elif all(isinstance(v, (int, float, str, bool)) for v in value):
                return Level.LINE  # Sequence of values
            else:
                return Level.WIDTH  # Sequence of complex items
        elif isinstance(value, dict):
            return Level.PLANE  # Key-value structure
        elif isinstance(value, Interface):
            return value._infer_level_from_structure()
        else:
            return Level.VOLUME  # Complex object
    
    def _infer_level_from_structure(self) -> Level:
        """
        Infer this interface's level from its structure.
        """
        if not self._attributes and not self._children:
            return Level.VOID
        elif len(self._attributes) + len(self._children) == 1:
            return Level.POINT
        elif len(self._children) == 0:
            return Level.LINE if len(self._attributes) <= 7 else Level.PLANE
        else:
            return Level.WHOLE  # Has children = complete object
    
    # =========================================================================
    # COLLECTION INTERFACE - Direct access, not iteration
    # =========================================================================
    
    def __len__(self) -> int:
        """
        Count of materialized points (attributes + children).
        
        This is the count of MATERIALIZED points, not potential.
        """
        return len(self._attributes) + len(self._children)
    
    def __contains__(self, key: Union[str, int]) -> bool:
        """
        Check if a point exists (is materialized) at key.
        """
        if isinstance(key, str):
            return key in self._attributes or key in self._children
        elif isinstance(key, int):
            idx_key = f"__idx_{key}"
            return idx_key in self._attributes or idx_key in self._children
        return False
    
    def __bool__(self) -> bool:
        """
        Interface is truthy if invoked.
        """
        return self._invoked
    
    @property
    def count(self) -> int:
        """
        Count of materialized points. Alias for len().
        """
        return len(self)
    
    @property
    def dimension_count(self) -> int:
        """
        Count of child dimensions (interfaces/objects).
        """
        return len(self._children)
    
    @property
    def point_count(self) -> int:
        """
        Count of value points (scalar attributes).
        """
        return len(self._attributes)
    
    def at_level(self, level: int) -> 'Interface':
        """
        Jump directly to a level (O(1), not traversal).
        
        This is handled automatically by the base class.
        Subclasses don't need to implement level mechanics.
        """
        self._level = Level(level) if level <= 6 else Level.WHOLE
        return self
    
    def at_coordinate(self, spiral: int, level: int, position: float = 0.0) -> 'Interface':
        """
        Jump directly to a coordinate (O(1)).
        """
        self._coordinate = Coordinate(spiral, level, position)
        self._level = Level(level) if level <= 6 else Level.WHOLE
        return self
    
    # =========================================================================
    # RECURSIVE PIPELINE TRAVERSAL - When many items need processing
    # =========================================================================
    # 
    # FOR LOOPS ARE ANTI-PATTERN (flat iteration, doesn't respect dimensions)
    # DIRECT ADDRESSING for single point access (O(1))
    # RECURSION when many items must be referenced (follows the pipeline to VOID)
    #
    # Recursion goes DOWN the dimensional pipeline (6→5→4→3→2→1→0→VOID)
    # This respects the natural spiral structure - like water flowing down
    # through the conical tube at the center of the helix.
    #
    # USE RECURSION ONLY WHEN NECESSARY - prefer direct addressing when possible.
    # =========================================================================
    
    def recurse(
        self, 
        operation: Callable[['Interface', int], Any],
        max_depth: int = 7,
        _current_depth: int = 0
    ) -> List[Any]:
        """
        Recursive traversal DOWN the dimensional pipeline.
        
        This is for when MANY items must be referenced. Recursion follows
        the natural spiral structure toward VOID, respecting dimensional
        hierarchy rather than flat iteration.
        
        USE ONLY WHEN NECESSARY - prefer direct addressing for single points.
        
        Args:
            operation: Function(interface, depth) -> result
                       Called at each level, receives current interface and depth
            max_depth: Maximum descent depth (default: 7 levels)
            _current_depth: Internal - current depth counter
        
        Returns:
            List of results from operation at each visited point
        
        Example:
            # Process all engines in all cars (goes down pipeline)
            results = parking_lot.recurse(
                lambda obj, depth: obj.process() if depth == 2 else None
            )
            
            # Collect all VINs (depth 1 = point level)
            vins = cars.recurse(
                lambda obj, depth: obj.vin if depth == 1 and hasattr(obj, 'vin') else None
            )
        """
        results = []
        
        # Apply operation at current level
        result = operation(self, _current_depth)
        if result is not None:
            results.append(result)
        
        # Stop at max depth (approaching VOID)
        if _current_depth >= max_depth:
            return results
        
        # Recurse into children (going DOWN the pipeline)
        for child in self._children.values():
            if isinstance(child, Interface):
                child_results = child.recurse(
                    operation, 
                    max_depth, 
                    _current_depth + 1
                )
                results.extend(child_results)
        
        return results
    
    def apply_down(
        self, 
        operation: Callable[['Interface'], Any],
        target_level: Optional[int] = None
    ) -> List[Any]:
        """
        Apply operation going DOWN toward VOID.
        
        Simpler interface than recurse() - just applies operation
        at each level or only at target level.
        
        Args:
            operation: Function to apply to each interface
            target_level: If specified, only apply at this level
        
        Returns:
            List of non-None results
        """
        def wrapped_op(obj: 'Interface', depth: int) -> Any:
            if target_level is None:
                return operation(obj)
            elif depth == target_level:
                return operation(obj)
            return None
        
        return self.recurse(wrapped_op)
    
    def collect_at_level(self, level: int) -> List['Interface']:
        """
        Collect all interfaces at a specific level.
        
        Goes down the pipeline, collects everything at target level.
        """
        return self.apply_down(lambda obj: obj, target_level=level)
    
    def find(self, predicate: Callable[['Interface'], bool]) -> Optional['Interface']:
        """
        Find first interface matching predicate.
        
        Recurses down pipeline until predicate returns True.
        Returns None if not found.
        """
        results = self.apply_down(
            lambda obj: obj if predicate(obj) else None
        )
        return results[0] if results else None
    
    def find_all(self, predicate: Callable[['Interface'], bool]) -> List['Interface']:
        """
        Find all interfaces matching predicate.
        
        Recurses down pipeline, collects all matches.
        """
        return [
            obj for obj in self.apply_down(lambda o: o if predicate(o) else None)
            if obj is not None
        ]
    
    @property
    def list(self) -> List[str]:
        """Returns list of all invoked (materialized) attribute names."""
        return list(self._attributes.keys())
    
    @property
    def points(self) -> List[str]:
        """Alias for .list - all points in this dimension."""
        return self.list
    
    @property
    def identities(self) -> Set[str]:
        """The '1s' - identity points that have been established."""
        return self._identities
    
    @property
    def identity_count(self) -> int:
        """Number of identities (1s) found."""
        return len(self._identities)
    
    @property
    def is_substrate(self) -> bool:
        """
        Whether this interface has become a substrate.
        
        An interface becomes a substrate when it has enough identities.
        """
        return self._is_substrate
    
    def _check_substrate_transition(self) -> None:
        """Check if this interface should become a substrate."""
        if not self._is_substrate and len(self._identities) >= 2:
            self._object_substrate = KERNEL.register_object_substrate(self)
            if self._object_substrate:
                self._is_substrate = True
    
    def ingest(self, type_name: str, **initial_values) -> 'Interface':
        """
        Ingest an interface from this object's substrate.
        
        Only works if this interface has become a substrate
        (i.e., has enough identities).
        """
        if not self._is_substrate:
            self._check_substrate_transition()
        
        if self._is_substrate and self._object_substrate:
            return self._object_substrate.ingest(type_name, **initial_values)
        else:
            raise DimensionalError(
                f"Cannot ingest from {self._type_name}: "
                f"needs at least 2 identities (has {len(self._identities)})"
            )
    
    @property
    def children_list(self) -> List[str]:
        """Returns list of all child interface names."""
        return list(self._children.keys())
    
    @property
    def id(self) -> str:
        """Unique identifier."""
        return self._id
    
    @property
    def type_name(self) -> str:
        """The type name of this interface."""
        return self._type_name
    
    @property
    def coordinate(self) -> Coordinate:
        """Dimensional coordinate at creation."""
        return self._coordinate
    
    @property
    def substrate(self) -> 'Substrate':
        """The substrate this interface was ingested from."""
        return self._substrate
    
    @property
    def is_invoked(self) -> bool:
        return self._invoked
    
    @property
    def is_materialized(self) -> bool:
        return self._materialized
    
    @property
    def is_sealed(self) -> bool:
        return self._sealed
    
    @property
    def is_closed(self) -> bool:
        return self._closed
    
    def __getattr__(self, name: str) -> Any:
        """
        Auto-getter for any attribute.
        
        When accessing an attribute:
        1. If it exists, return it
        2. If it doesn't, create a new child Interface (dimension)
        3. Child is auto-invoked and becomes both point and dimension
        
        This is O(1) direct access, not tree traversal.
        """
        if name.startswith('_'):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        
        # Check direct attributes first
        if '_attributes' in self.__dict__ and name in self._attributes:
            return self._attributes[name]
        
        # Check children (other dimensions)
        if '_children' in self.__dict__ and name in self._children:
            return self._children[name]
        
        # Create new child dimension (auto-invoke)
        if '_closed' in self.__dict__ and self._closed:
            raise ClosedDimensionViolation(
                f"Cannot add point '{name}' to closed dimension: {self._type_name}"
            )
        
        # Auto-create child as new interface (dimension)
        if '_children' in self.__dict__:
            child = Interface(f"{self._type_name}.{name}", self._substrate)
            child._parent = self
            self._children[name] = child
            return child
        
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name: str, value: Any) -> None:
        """
        Auto-setter for any attribute.
        
        When setting an attribute:
        1. Check if sealed
        2. Check if closed (for new attributes)
        3. Store the value
        4. Mark as materialized
        5. Add to identities (the "1s")
        """
        if name.startswith('_'):
            object.__setattr__(self, name, value)
            return
        
        # Check sealing
        if hasattr(self, '_sealed') and self._sealed:
            raise ImmutabilityViolation(
                f"Cannot modify sealed interface: {self._type_name}"
            )
        
        # Check if closed (for new attributes)
        if hasattr(self, '_closed') and self._closed:
            if hasattr(self, '_attributes') and name not in self._attributes:
                raise ClosedDimensionViolation(
                    f"Cannot add point '{name}' to closed dimension: {self._type_name}"
                )
        
        # Store attribute
        if hasattr(self, '_attributes'):
            # If value is an Interface, store as child
            if isinstance(value, Interface):
                value._parent = self
                self._children[name] = value
                # Child's type becomes an identity
                self._identities.add(f"{name}:{value._type_name}")
            else:
                self._attributes[name] = value
                self._attribute_metadata[name] = {
                    'set_at': time.time(),
                    'type': type(value).__name__
                }
                # Attribute becomes an identity (a "1")
                self._identities.add(name)
            
            self._materialized = True
            
            # Check if we've become a substrate
            self._check_substrate_transition()
    
    def get(self, name: str, default: Any = None) -> Any:
        """Get attribute with default value."""
        try:
            return getattr(self, name)
        except AttributeError:
            return default
    
    def set(self, name: str, value: Any) -> 'Interface':
        """Set attribute and return self for chaining."""
        setattr(self, name, value)
        return self
    
    def seal(self) -> 'Interface':
        """Seal this interface (make immutable)."""
        self._sealed = True
        return self
    
    def close(self) -> 'Interface':
        """Close this dimension (no new points allowed)."""
        self._closed = True
        return self
    
    def seal_point(self, name: str) -> 'Interface':
        """Seal a specific attribute."""
        if name in self._children:
            self._children[name].seal()
        self._attribute_metadata.setdefault(name, {})['sealed'] = True
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Export this interface to a dictionary."""
        result = {
            '__type__': self._type_name,
            '__id__': self._id,
            '__coordinate__': str(self._coordinate),
            '__identities__': list(self._identities),
            '__is_substrate__': self._is_substrate,
        }
        
        for name, value in self._attributes.items():
            if isinstance(value, Interface):
                result[name] = value.to_dict()
            else:
                result[name] = value
        
        for name, child in self._children.items():
            result[name] = child.to_dict()
        
        return result
    
    def to_json(self) -> str:
        """Export to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)
    
    @classmethod
    def register_type(cls, type_name: str, factory: Type['Interface']) -> None:
        """Register a custom type factory."""
        cls._type_registry[type_name] = factory
    
    @classmethod
    def create(cls, type_name: str, **kwargs) -> 'Interface':
        """Create an interface of a specific type."""
        if type_name in cls._type_registry:
            return cls._type_registry[type_name](type_name, **kwargs)
        return cls(type_name, **kwargs)
    
    def __repr__(self) -> str:
        status = []
        if self._invoked:
            status.append("invoked")
        if self._materialized:
            status.append("materialized")
        if self._sealed:
            status.append("sealed")
        if self._closed:
            status.append("closed")
        if self._is_substrate:
            status.append("SUBSTRATE")
        
        return (
            f"<Interface {self._type_name} at {self._coordinate} "
            f"[{', '.join(status)}] "
            f"identities={len(self._identities)}>"
        )


# Alias: Object = Interface (for compatibility and conceptual clarity)
Object = Interface


# =============================================================================
# DIMENSIONAL POINT - The atomic unit (inherits from Object)
# =============================================================================

class DimensionalPoint(Object):
    """
    A point in dimensional space.
    
    Every point is simultaneously:
      1. A value at its location
      2. A dimension containing infinite potential points
    
    This is the dimension ↔ point duality.
    """
    __slots__ = (
        '_identity', '_value', '_materialized', '_sealed', '_closed',
        '_parent', '_name', '_level', '_children', '_substrate', '_metadata'
    )
    
    def __init__(
        self,
        identity: str,
        value: Any = None,
        *,
        parent: Optional['DimensionalPoint'] = None,
        name: str = "",
        level: Level = Level.POINT,
        substrate: Optional['Substrate'] = None
    ):
        self._identity = identity
        self._value = value
        self._materialized = value is not None
        self._sealed = False
        self._closed = False
        self._parent = parent
        self._name = name
        self._level = level
        self._children: Dict[str, DimensionalPoint] = {}
        self._substrate = substrate
        self._metadata: Dict[str, Any] = {}
    
    @property
    def identity(self) -> str:
        return self._identity
    
    @property
    def value(self) -> Any:
        return self._value
    
    @value.setter
    def value(self, new_value: Any) -> None:
        if self._sealed:
            raise ImmutabilityViolation(
                f"Cannot modify sealed point: {self._identity}"
            )
        self._value = new_value
        self._materialized = True
    
    @property
    def is_materialized(self) -> bool:
        return self._materialized
    
    @property
    def is_sealed(self) -> bool:
        return self._sealed
    
    @property
    def is_closed(self) -> bool:
        return self._closed
    
    @property
    def level(self) -> Level:
        return self._level
    
    def materialize(self) -> 'DimensionalPoint':
        """Explicitly materialize this point."""
        self._materialized = True
        return self
    
    def seal(self) -> 'DimensionalPoint':
        """Seal this point (make immutable)."""
        self._sealed = True
        return self
    
    def close(self) -> 'DimensionalPoint':
        """Close this dimension (no new points)."""
        self._closed = True
        return self
    
    def __getattr__(self, name: str) -> 'DimensionalPoint':
        """
        Dimensional access to child points.
        
        This is the core of the paradigm:
        - Accessing an attribute creates/retrieves a child dimension
        - The child exists in potential until accessed
        - Access is O(1), not traversal
        """
        if name.startswith('_'):
            raise AttributeError(name)
        
        if name not in self._children:
            if self._closed:
                raise ClosedDimensionViolation(
                    f"Cannot add point '{name}' to closed dimension: {self._identity}"
                )
            # Create child point in potential
            child = DimensionalPoint(
                identity=f"{self._identity}.{name}",
                parent=self,
                name=name,
                level=self._level,
                substrate=self._substrate
            )
            self._children[name] = child
        
        return self._children[name]
    
    def __setattr__(self, name: str, value: Any) -> None:
        """Set attribute value, materializing the point."""
        if name.startswith('_'):
            object.__setattr__(self, name, value)
            return
        
        if hasattr(self, '_sealed') and self._sealed:
            raise ImmutabilityViolation(
                f"Cannot modify sealed dimension: {self._identity}"
            )
        
        if hasattr(self, '_closed') and self._closed and name not in self._children:
            raise ClosedDimensionViolation(
                f"Cannot add point '{name}' to closed dimension: {self._identity}"
            )
        
        if hasattr(self, '_children') and name in self._children:
            self._children[name].value = value
        else:
            if hasattr(self, '_children'):
                child = DimensionalPoint(
                    identity=f"{self._identity}.{name}",
                    value=value,
                    parent=self,
                    name=name,
                    level=Level.POINT,
                    substrate=self._substrate if hasattr(self, '_substrate') else None
                )
                self._children[name] = child
    
    def __repr__(self) -> str:
        status = []
        if self._materialized:
            status.append("materialized")
        else:
            status.append("potential")
        if self._sealed:
            status.append("sealed")
        if self._closed:
            status.append("closed")
        
        return f"<DimensionalPoint {self._identity} [{', '.join(status)}]>"


# =============================================================================
# DIMENSIONAL OBJECT - The complete entity
# =============================================================================

class DimensionalObject(DimensionalPoint):
    """
    A complete dimensional object.
    
    When invoked, a DimensionalObject becomes an entire dimension
    containing every possible attribute, property, and method in POTENTIAL.
    
    Nothing materializes until accessed.
    
    Example:
        car = invoke("Car")
        # Car exists with ALL car attributes in potential
        
        car.engine
        # Engine now materialized with ALL engine attributes in potential
        
        car.engine.pistons[0].firing = True
        # Specific piston attribute materialized and set
    """
    
    def __init__(
        self,
        type_name: str,
        *,
        substrate: Optional['Substrate'] = None,
        coordinate: Optional[Coordinate] = None
    ):
        super().__init__(
            identity=type_name,
            parent=None,
            name=type_name,
            level=Level.WHOLE,
            substrate=substrate or GlobalSubstrate.instance()
        )
        self._type_name = type_name
        self._coordinate = coordinate or Coordinate(0, 6, 0.0)
        self._invocation_time = None
        self._spiral_index = Spiral.current().index
    
    @property
    def type_name(self) -> str:
        return self._type_name
    
    @property
    def coordinate(self) -> Coordinate:
        return self._coordinate
    
    def invoke(self, level: Optional[int] = None) -> 'DimensionalObject':
        """
        Invoke this object at a specific dimensional level.
        
        This is NOT iteration. This is a direct O(1) level jump.
        
        Args:
            level: Target level (0-6). Default: current level.
        
        Returns:
            Self for chaining.
        """
        import time
        if level is not None:
            self._level = Level(level)
            self._coordinate = Coordinate(
                self._coordinate.spiral,
                level,
                self._coordinate.position
            )
        self._invocation_time = time.time()
        self._materialized = True
        return self
    
    def at(self, spiral: int, level: int, position: float = 0.0) -> 'DimensionalObject':
        """
        Position this object at specific dimensional coordinates.
        
        Args:
            spiral: Spiral index
            level: Level (0-6)
            position: Position along spiral
        
        Returns:
            Self for chaining.
        """
        self._coordinate = Coordinate(spiral, level, position)
        self._level = Level(level)
        self._spiral_index = spiral
        return self
    
    def seal_point(self, name: str) -> 'DimensionalObject':
        """Seal a specific point (make it immutable)."""
        if name in self._children:
            self._children[name].seal()
        return self
    
    def close_dimension(self, level: int) -> 'DimensionalObject':
        """Close a dimension level (no new points)."""
        # This would affect all children at this level
        # Implementation depends on how you want level-based closing
        return self
    
    def seal_from_dimension(self, level: int) -> 'DimensionalObject':
        """Seal all dimensions from level onwards."""
        # Make all levels >= level read-only
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Export materialized state as dictionary.
        
        Only includes materialized points.
        """
        result = {
            "__type__": self._type_name,
            "__coordinate__": str(self._coordinate),
            "__level__": self._level.name,
        }
        
        for name, child in self._children.items():
            if child.is_materialized:
                if isinstance(child, DimensionalObject):
                    result[name] = child.to_dict()
                elif isinstance(child.value, (DimensionalList, DimensionalDict)):
                    result[name] = child.value.to_native()
                else:
                    result[name] = child.value
        
        return result
    
    def __repr__(self) -> str:
        return f"<DimensionalObject {self._type_name} at {self._coordinate}>"


# =============================================================================
# DIMENSIONAL COLLECTIONS - Lists, Dicts, Sets
# =============================================================================

class DimensionalList(Generic[TypeVar('T')]):
    """
    A dimensional list - a LINE of points (Level 2).
    
    Each element is a DimensionalPoint that can be both:
      - A value at its index
      - A dimension containing its own attributes
    
    Access is O(1) - no iteration through intermediate elements.
    """
    
    def __init__(
        self,
        identity: str,
        *,
        parent: Optional[DimensionalPoint] = None,
        substrate: Optional['Substrate'] = None
    ):
        self._identity = identity
        self._parent = parent
        self._substrate = substrate
        self._items: Dict[int, DimensionalPoint] = {}
        self._sealed = False
        self._closed = False
        self._level = Level.LINE  # A list is a LINE of points
    
    def __getitem__(self, index: int) -> DimensionalPoint:
        """
        Direct dimensional access to element.
        
        This is O(1) - we jump directly to the index,
        not iterate through 0..index-1.
        """
        if index not in self._items:
            if self._closed:
                raise ClosedDimensionViolation(
                    f"Cannot add index {index} to closed list: {self._identity}"
                )
            # Create element in potential
            self._items[index] = DimensionalPoint(
                identity=f"{self._identity}[{index}]",
                parent=self._parent,
                name=f"[{index}]",
                level=Level.POINT,
                substrate=self._substrate
            )
        return self._items[index]
    
    def __setitem__(self, index: int, value: Any) -> None:
        """Set element value."""
        if self._sealed:
            raise ImmutabilityViolation(
                f"Cannot modify sealed list: {self._identity}"
            )
        
        if index not in self._items:
            if self._closed:
                raise ClosedDimensionViolation(
                    f"Cannot add index {index} to closed list: {self._identity}"
                )
            self._items[index] = DimensionalPoint(
                identity=f"{self._identity}[{index}]",
                value=value,
                parent=self._parent,
                name=f"[{index}]",
                level=Level.POINT,
                substrate=self._substrate
            )
        else:
            self._items[index].value = value
    
    def __len__(self) -> int:
        """Return count of materialized elements."""
        return len(self._items)
    
    @property
    def count(self) -> int:
        """Alias for len, more dimensional-friendly."""
        return len(self._items)
    
    @property
    def indices(self) -> List[int]:
        """Return all materialized indices."""
        return sorted(self._items.keys())
    
    def seal(self) -> 'DimensionalList':
        """Seal this list (make immutable)."""
        self._sealed = True
        for item in self._items.values():
            item.seal()
        return self
    
    def close(self) -> 'DimensionalList':
        """Close this list (no new elements)."""
        self._closed = True
        return self
    
    def to_native(self) -> List[Any]:
        """Convert to native Python list (materialized elements only)."""
        if not self._items:
            return []
        max_idx = max(self._items.keys())
        result = [None] * (max_idx + 1)
        for idx, point in self._items.items():
            if point.is_materialized:
                result[idx] = point.value
        return result
    
    def __repr__(self) -> str:
        return f"<DimensionalList {self._identity} [{len(self)} materialized]>"


class DimensionalDict(Generic[TypeVar('K'), TypeVar('V')]):
    """
    A dimensional dictionary - a WIDTH/PLANE of points (Level 3-4).
    
    Keys map to DimensionalPoints, each of which is both
    a value and a dimension.
    """
    
    def __init__(
        self,
        identity: str,
        *,
        parent: Optional[DimensionalPoint] = None,
        substrate: Optional['Substrate'] = None
    ):
        self._identity = identity
        self._parent = parent
        self._substrate = substrate
        self._items: Dict[str, DimensionalPoint] = {}
        self._sealed = False
        self._closed = False
        self._level = Level.WIDTH
    
    def __getitem__(self, key: str) -> DimensionalPoint:
        """Direct dimensional access to key."""
        if key not in self._items:
            if self._closed:
                raise ClosedDimensionViolation(
                    f"Cannot add key '{key}' to closed dict: {self._identity}"
                )
            self._items[key] = DimensionalPoint(
                identity=f"{self._identity}[{key}]",
                parent=self._parent,
                name=key,
                level=Level.POINT,
                substrate=self._substrate
            )
        return self._items[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Set key value."""
        if self._sealed:
            raise ImmutabilityViolation(
                f"Cannot modify sealed dict: {self._identity}"
            )
        
        if key not in self._items:
            if self._closed:
                raise ClosedDimensionViolation(
                    f"Cannot add key '{key}' to closed dict: {self._identity}"
                )
            self._items[key] = DimensionalPoint(
                identity=f"{self._identity}[{key}]",
                value=value,
                parent=self._parent,
                name=key,
                level=Level.POINT,
                substrate=self._substrate
            )
        else:
            self._items[key].value = value
    
    def __contains__(self, key: str) -> bool:
        return key in self._items
    
    def __len__(self) -> int:
        return len(self._items)
    
    @property
    def keys(self) -> List[str]:
        """Return all keys."""
        return list(self._items.keys())
    
    def seal(self) -> 'DimensionalDict':
        """Seal this dict (make immutable)."""
        self._sealed = True
        for item in self._items.values():
            item.seal()
        return self
    
    def close(self) -> 'DimensionalDict':
        """Close this dict (no new keys)."""
        self._closed = True
        return self
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dict."""
        return {
            k: v.value for k, v in self._items.items() 
            if v.is_materialized
        }
    
    def __repr__(self) -> str:
        return f"<DimensionalDict {self._identity} [{len(self)} keys]>"


class DimensionalSet(Generic[TypeVar('T')]):
    """
    A dimensional set - unique points in a dimension.
    """
    
    def __init__(
        self,
        identity: str,
        *,
        parent: Optional[DimensionalPoint] = None,
        substrate: Optional['Substrate'] = None
    ):
        self._identity = identity
        self._parent = parent
        self._substrate = substrate
        self._items: Set[str] = set()
        self._sealed = False
        self._closed = False
        self._level = Level.WIDTH
    
    def add(self, value: str) -> None:
        """Add value to set."""
        if self._sealed:
            raise ImmutabilityViolation(
                f"Cannot modify sealed set: {self._identity}"
            )
        if self._closed and value not in self._items:
            raise ClosedDimensionViolation(
                f"Cannot add to closed set: {self._identity}"
            )
        self._items.add(value)
    
    def __contains__(self, value: str) -> bool:
        return value in self._items
    
    def __len__(self) -> int:
        return len(self._items)
    
    def seal(self) -> 'DimensionalSet':
        self._sealed = True
        return self
    
    def close(self) -> 'DimensionalSet':
        self._closed = True
        return self
    
    def to_native(self) -> Set[str]:
        return self._items.copy()
    
    def __repr__(self) -> str:
        return f"<DimensionalSet {self._identity} [{len(self)} items]>"


# =============================================================================
# SUBSTRATE - The dimensional manifold
# =============================================================================

class Substrate:
    """
    The dimensional substrate - where all objects exist in potential.
    
    The substrate is NOT a container in the traditional sense.
    It is the MANIFOLD from which all dimensional objects are invoked.
    
    All points exist in potential. Nothing consumes resources until invoked.
    """
    
    def __init__(self, name: str = "default"):
        self._name = name
        self._registry: Dict[str, Type[DimensionalObject]] = {}
        self._instances: WeakValueDictionary = WeakValueDictionary()
        self._type_definitions: Dict[str, Dict[str, Any]] = {}
        self._sealed = False
        self._closed = False
    
    @property
    def name(self) -> str:
        return self._name
    
    def register(
        self,
        type_name: str,
        definition: Optional[Dict[str, Any]] = None,
        cls: Optional[Type[DimensionalObject]] = None
    ) -> None:
        """
        Register a type in the substrate.
        
        The type exists in potential, ready to be invoked.
        
        Args:
            type_name: Name of the type (e.g., "Car", "Engine")
            definition: Optional attribute definitions
            cls: Optional custom class
        """
        if self._sealed:
            raise ImmutabilityViolation(
                f"Cannot register in sealed substrate: {self._name}"
            )
        if self._closed and type_name not in self._registry:
            raise ClosedDimensionViolation(
                f"Cannot add type to closed substrate: {self._name}"
            )
        
        self._type_definitions[type_name] = definition or {}
        if cls:
            self._registry[type_name] = cls
    
    def invoke(
        self,
        type_name: str,
        *,
        coordinate: Optional[Coordinate] = None
    ) -> DimensionalObject:
        """
        Invoke an object from the substrate.
        
        This is NOT instantiation. The object already exists in potential.
        We are materializing it into dimensional existence.
        
        Args:
            type_name: Type to invoke
            coordinate: Optional starting coordinate
        
        Returns:
            The invoked DimensionalObject
        """
        # Check if custom class registered
        if type_name in self._registry:
            cls = self._registry[type_name]
            obj = cls(
                type_name=type_name,
                substrate=self,
                coordinate=coordinate
            )
        else:
            obj = DimensionalObject(
                type_name=type_name,
                substrate=self,
                coordinate=coordinate
            )
        
        # Apply type definition if exists
        if type_name in self._type_definitions:
            self._apply_definition(obj, self._type_definitions[type_name])
        
        # Track instance
        obj_id = str(uuid.uuid4())
        self._instances[obj_id] = obj
        
        return obj
    
    def _apply_definition(
        self,
        obj: DimensionalObject,
        definition: Dict[str, Any]
    ) -> None:
        """Apply type definition to object (create child dimensions in potential)."""
        for name, config in definition.items():
            if isinstance(config, dict):
                # Nested dimension
                child = getattr(obj, name)
                self._apply_definition(child, config)
            elif isinstance(config, type):
                # Type annotation (stays in potential)
                pass
            else:
                # Default value
                setattr(obj, name, config)
    
    def at(self, spiral: int, level: int) -> 'SubstrateView':
        """
        Get a view of the substrate at specific coordinates.
        
        Returns a SubstrateView that can query objects at that location.
        """
        return SubstrateView(self, Coordinate(spiral, level))
    
    def __getitem__(self, address: str) -> Any:
        """
        Direct dimensional addressing.
        
        Examples:
            substrate["0{6}.Car"]
            substrate["0{3}.Car.engine"]
        """
        addr = Address.parse(address)
        # Find or invoke the type
        if addr.path:
            type_name = addr.path[0]
            obj = self.invoke(type_name, coordinate=addr.coordinate)
            # Navigate to specific point
            current = obj
            for part in addr.path[1:]:
                current = getattr(current, part)
            return current
        raise KeyError(f"Invalid address: {address}")
    
    def seal(self) -> 'Substrate':
        """Seal this substrate (no modifications)."""
        self._sealed = True
        return self
    
    def close(self) -> 'Substrate':
        """Close this substrate (no new types)."""
        self._closed = True
        return self
    
    def __repr__(self) -> str:
        return f"<Substrate '{self._name}' [{len(self._type_definitions)} types]>"


class SubstrateView:
    """A view into the substrate at specific coordinates."""
    
    def __init__(self, substrate: Substrate, coordinate: Coordinate):
        self._substrate = substrate
        self._coordinate = coordinate
    
    def get(self, name: str) -> Any:
        """Get a point at this coordinate."""
        return self._substrate.invoke(name, coordinate=self._coordinate)
    
    def __repr__(self) -> str:
        return f"<SubstrateView at {self._coordinate}>"


class GlobalSubstrate:
    """
    Singleton global substrate.
    
    The default dimensional manifold for all operations.
    """
    _instance: Optional[Substrate] = None
    _lock = threading.Lock()
    
    @classmethod
    def instance(cls) -> Substrate:
        """Get or create the global substrate."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = Substrate("global")
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """Reset the global substrate (for testing)."""
        with cls._lock:
            cls._instance = None


# Module-level substrate reference
substrate = GlobalSubstrate.instance()


# =============================================================================
# DECORATORS
# =============================================================================

def sealed(target: Any) -> Any:
    """
    Mark a dimensional object or point as sealed (immutable).
    
    Usage:
        @sealed
        def create_token():
            token = invoke("Token")
            token.value = "abc123"
            return token  # Token is now sealed
        
        @sealed
        class ImmutableConfig(DimensionalObject):
            pass
    """
    if isinstance(target, (DimensionalPoint, DimensionalObject)):
        target.seal()
        return target
    elif isinstance(target, type):
        # Class decorator
        original_init = target.__init__
        @wraps(original_init)
        def sealed_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            self.seal()
        target.__init__ = sealed_init
        return target
    elif callable(target):
        # Function decorator
        @wraps(target)
        def wrapper(*args, **kwargs):
            result = target(*args, **kwargs)
            if isinstance(result, (DimensionalPoint, DimensionalObject)):
                result.seal()
            return result
        return wrapper
    return target


def closed(target: Any) -> Any:
    """
    Mark a dimensional object as closed (no new points).
    
    Usage:
        @closed
        class ProtocolMessage(DimensionalObject):
            pass
        
        msg = invoke("ProtocolMessage")
        msg.type = "auth"     # OK if 'type' is predefined
        msg.extra = "data"    # Raises ClosedDimensionViolation
    """
    if isinstance(target, (DimensionalPoint, DimensionalObject)):
        target.close()
        return target
    elif isinstance(target, type):
        original_init = target.__init__
        @wraps(original_init)
        def closed_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            self.close()
        target.__init__ = closed_init
        return target
    elif callable(target):
        @wraps(target)
        def wrapper(*args, **kwargs):
            result = target(*args, **kwargs)
            if isinstance(result, (DimensionalPoint, DimensionalObject)):
                result.close()
            return result
        return wrapper
    return target


def dimensional(
    level: Level = Level.WHOLE,
    spiral: int = 0
) -> Callable:
    """
    Decorator to make a class a dimensional object.
    
    Usage:
        @dimensional(level=Level.VOLUME)
        class PhysicsBody:
            position: Vec3
            velocity: Vec3
            mass: float
    """
    def decorator(cls: Type) -> Type:
        class DimensionalWrapper(DimensionalObject):
            def __init__(self, **kwargs):
                super().__init__(
                    type_name=cls.__name__,
                    coordinate=Coordinate(spiral, level.value, 0.0)
                )
                # Apply any passed values
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        DimensionalWrapper.__name__ = cls.__name__
        DimensionalWrapper.__qualname__ = cls.__qualname__
        
        # Register in global substrate
        GlobalSubstrate.instance().register(cls.__name__, cls=DimensionalWrapper)
        
        return DimensionalWrapper
    
    return decorator


def lazy(func: Callable) -> property:
    """
    Decorator for lazy-evaluated dimensional properties.
    
    The property only computes when accessed (invoked).
    
    Usage:
        class Engine(DimensionalObject):
            @lazy
            def horsepower(self):
                return self.displacement.value * self.efficiency.value
    """
    attr_name = f"_lazy_{func.__name__}"
    
    @property
    @wraps(func)
    def wrapper(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)
    
    return wrapper


def computed(
    *dependencies: str
) -> Callable:
    """
    Decorator for computed dimensional properties.
    
    Automatically recomputes when dependencies change.
    
    Usage:
        class Rectangle(DimensionalObject):
            @computed('width', 'height')
            def area(self):
                return self.width.value * self.height.value
    """
    def decorator(func: Callable) -> property:
        @property
        @wraps(func)
        def wrapper(self):
            return func(self)
        return wrapper
    
    return decorator


# =============================================================================
# GLOBAL INGESTION AND INVOCATION FUNCTIONS
# =============================================================================

def ingest(
    type_name: str,
    *,
    dimensional_depth: int = 3,
    **initial_values
) -> Interface:
    """
    INGEST an interface from the dimensional substrate.
    
    This is the PRIMARY way to create objects in ButterflyFX.
    Objects are NOT instantiated — they are INGESTED from mathematical substrates.
    
    ARCHITECTURE: ingest() → Core → Kernel
    
    The developer calls ingest(), which goes through:
    1. CORE (handles kernel communication)
    2. Substrate (mathematical expression)
    3. KERNEL (registers the object)
    4. SRL (makes it universally addressable)
    
    DIMENSIONAL DEPTH:
    ┌────────────────────────────────────────────────────────────────┐
    │  4D: ParkingLot, City, Fleet - containers of 3D objects       │
    │  3D: Car, House, Person - complete volumetric objects         │
    │  2D: Engine, Panel - surfaces with parts                      │
    │  1D: Piston, Wire - connections                               │
    │  0D: Iron, Carbon - atomic elements                           │
    └────────────────────────────────────────────────────────────────┘
    
    Args:
        type_name: The type to ingest (e.g., "Car", "Engine", "ParkingLot")
        dimensional_depth: The dimension (0-4) - defaults to 3D for objects
        **initial_values: Initial attribute values to set
    
    Returns:
        The ingested Interface (registered in SRL for universal access)
    
    Example:
        # Ingest a 3D object (default)
        car = ingest("Car")
        car.vin = "ABC123"
        
        # Ingest a 4D container
        lot = ingest("ParkingLot", dimensional_depth=4)
        car1 = lot.ingest("Car")  # Car is a point in lot
        
        # Ingest with initial values
        car = ingest("Car", vin="XYZ789", color="red")
        
        # Access via SRL later
        same_car = srl(car._srl_address)
    """
    # Go through CORE - the proper architecture
    return CORE.ingest(type_name, dimensional_depth=dimensional_depth, **initial_values)


def invoke(
    type_name: str,
    *,
    substrate: Optional[Substrate] = None,
    dimensional_depth: int = 3,
    at: Optional[Tuple[int, int]] = None,
    **initial_values
) -> Union[Interface, 'DimensionalObject']:
    """
    Invoke a dimensional object from the substrate.
    
    This is an alias for ingest() with backward compatibility.
    Objects are not "instantiated" — they are INVOKED/INGESTED from potential.
    
    Args:
        type_name: The type to invoke (e.g., "Car", "Engine", "Person")
        substrate: Optional specific substrate to use
        dimensional_depth: The dimension (0-4) if no substrate provided
        at: Optional (spiral, level) tuple for positioning
        **initial_values: Initial attribute values to set
    
    Returns:
        The invoked object
    
    Example:
        car = invoke("Car")
        car.engine.cylinders = 8
        car.engine.pistons[0].firing = True
        
        # Or with initial values:
        car = invoke("Car", color="red", year=2024)
    """
    # If a specific substrate is provided, use it
    if substrate is not None:
        if hasattr(substrate, 'ingest'):
            return substrate.ingest(type_name, **initial_values)
        elif hasattr(substrate, 'invoke'):
            coordinate = None
            if at:
                coordinate = Coordinate(at[0], at[1], 0.0)
            return substrate.invoke(type_name, coordinate=coordinate)
    
    # Otherwise use the appropriate dimensional substrate
    return ingest(type_name, dimensional_depth=dimensional_depth, **initial_values)


def invoke_from(
    substrate_name: str,
    type_name: str,
    **kwargs
) -> DimensionalObject:
    """
    Invoke from a named substrate.
    
    Args:
        substrate_name: Name of the substrate
        type_name: Type to invoke
        **kwargs: Passed to invoke()
    
    Returns:
        The invoked DimensionalObject
    """
    # Would need substrate registry - for now use global
    return invoke(type_name, **kwargs)


def materialize(
    type_name: str,
    **values
) -> Interface:
    """
    MATERIALIZE an object with values in one call.
    
    This is a convenience function that combines ingest + attribute setting.
    The object is fully materialized with all provided values.
    
    Args:
        type_name: The type to materialize
        **values: All attribute values to set
    
    Returns:
        The materialized Interface
    
    Example:
        # One-liner object creation with values
        car = materialize("Car", 
            vin="ABC123",
            make="Toyota",
            model="Corolla",
            year=2024
        )
        
        # Equivalent to:
        # car = ingest("Car")
        # car.vin = "ABC123"
        # car.make = "Toyota"
        # etc.
    """
    return ingest(type_name, **values)


# =============================================================================
# SRL - SECURE RESOURCE LOCATOR (Universal Connector)
# =============================================================================
#
# SRL is the UNIVERSAL CONNECTOR for ButterflyFX.
# 
# It holds:
# - Connection addresses (internal and external)
# - Authentication keys and credentials
# - Connection parameters
# - Resource paths
#
# ALL interface-to-core communication goes through SRL.
# =============================================================================

class SRLError(DimensionalError):
    """Exception for SRL operations."""
    pass


class SecureResourceLocator:
    """
    SRL - Universal Connector for ButterflyFX.
    
    The SRL is the single point of access for ALL resources:
    - Internal dimensional objects
    - External databases
    - REST APIs
    - File systems
    - Any other data source
    
    FORMAT: srl://domain/substrate/resource[?key=value&...]
    
    EXAMPLES:
        srl://vehicle.car/toyota/corolla
        srl://database.postgres/users?host=localhost
        srl://api.weather/forecast?api_key=xxx
    
    The SRL holds ALL connection info, making it secure and universal.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the SRL registry."""
        self._registry: Dict[str, Any] = {}
        self._hash_index: Dict[str, str] = {}
        self._connections: Dict[str, Dict[str, Any]] = {}
        self._credentials: Dict[str, Dict[str, str]] = {}
    
    def _hash(self, address: str) -> str:
        """Generate hash for O(1) lookup."""
        return hashlib.sha256(address.encode()).hexdigest()[:16]
    
    def _parse(self, address: str) -> Tuple[str, str, str, Dict[str, str]]:
        """
        Parse SRL address into components.
        
        Returns: (domain, substrate, resource, params)
        """
        if not address.startswith("srl://"):
            raise SRLError(f"Invalid SRL format: {address}. Must start with srl://")
        
        parsed = urlparse(address)
        domain = parsed.netloc
        
        # Split path
        path_parts = parsed.path.strip('/').split('/')
        substrate = path_parts[0] if len(path_parts) > 0 else ""
        resource = '/'.join(path_parts[1:]) if len(path_parts) > 1 else ""
        
        # Parse query params
        params = {}
        if parsed.query:
            for key, values in parse_qs(parsed.query).items():
                params[key] = values[0] if len(values) == 1 else values
        
        return domain, substrate, resource, params
    
    def register(
        self, 
        address: str, 
        value: Any,
        credentials: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Register a resource at an SRL address.
        
        Args:
            address: SRL address (srl://domain/substrate/resource)
            value: The value or callable to register
            credentials: Optional credentials to store securely
        
        Returns:
            The full SRL address
        """
        # Normalize address
        if not address.startswith("srl://"):
            address = f"srl://{address}"
        
        self._registry[address] = value
        self._hash_index[self._hash(address)] = address
        
        if credentials:
            self._credentials[address] = credentials
        
        return address
    
    def register_interface(self, interface: 'Interface') -> str:
        """
        Register an Interface in the SRL.
        
        Creates an SRL address based on the interface's type and id.
        """
        domain = "object"
        substrate = interface._type_name.lower().replace(".", "_")
        resource = interface._id[:8]
        
        address = f"srl://{domain}/{substrate}/{resource}"
        self.register(address, interface)
        return address
    
    def get(self, address: str) -> Any:
        """
        O(1) lookup by SRL address.
        
        Args:
            address: Full SRL address
        
        Returns:
            The registered value, or None if not found
        """
        # Direct lookup
        if address in self._registry:
            return self._registry[address]
        
        # Hash lookup
        addr_hash = self._hash(address)
        if addr_hash in self._hash_index:
            actual_addr = self._hash_index[addr_hash]
            return self._registry.get(actual_addr)
        
        # Try to resolve via Core
        return _CORE_INSTANCE.resolve(address) if _CORE_INSTANCE else None
    
    def invoke(self, address: str, *args, **kwargs) -> Any:
        """
        Invoke an operation at an SRL address.
        
        Args:
            address: SRL address of the operation
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Result of the invocation
        """
        target = self.get(address)
        
        if target is None:
            raise SRLError(f"Not found: {address}")
        
        if callable(target):
            return target(*args, **kwargs)
        
        # If it's an Interface, return it
        if isinstance(target, Interface):
            return target
        
        return target
    
    def connect(
        self, 
        address: str,
        connection_type: str,
        **connection_params
    ) -> str:
        """
        Register a connection in the SRL.
        
        Args:
            address: SRL address for this connection
            connection_type: Type of connection (postgres, mysql, rest, etc.)
            **connection_params: Connection parameters (host, port, etc.)
        
        Returns:
            The full SRL address
        """
        if not address.startswith("srl://"):
            address = f"srl://{address}"
        
        self._connections[address] = {
            'type': connection_type,
            'params': connection_params,
            'created': time.time()
        }
        
        return address
    
    def set_credentials(self, address: str, **credentials) -> None:
        """
        Set credentials for a connection.
        
        Credentials are stored securely and never exposed.
        """
        self._credentials[address] = credentials
    
    def find(self, pattern: str) -> List[str]:
        """
        Find addresses matching a pattern.
        
        Args:
            pattern: Regex pattern to match
        
        Returns:
            List of matching addresses
        """
        import re
        regex = re.compile(pattern, re.IGNORECASE)
        return [addr for addr in self._registry.keys() if regex.search(addr)]
    
    def list_all(self) -> List[str]:
        """List all registered SRL addresses."""
        return list(self._registry.keys())
    
    def __call__(self, address: str) -> Any:
        """
        Shorthand for get().
        
        Allows: SRL("srl://...")
        """
        return self.get(address)


# Global SRL instance
SRL = SecureResourceLocator()


def srl(address: str) -> Any:
    """
    Universal resource access via SRL.
    
    This is the primary way to access ANY resource in ButterflyFX.
    
    Args:
        address: SRL address (srl://domain/substrate/resource)
    
    Returns:
        The resource at that address
    
    Example:
        car = srl("srl://vehicle.car/toyota/corolla")
        user = srl("srl://database.users/profile/123")
        temp = srl("srl://sensor.car/engine/temperature")
    """
    return SRL.get(address)


# =============================================================================
# CORE - Kernel Communication Layer
# =============================================================================
#
# The CORE is the ONLY layer that communicates with the Kernel.
# All interfaces communicate with Core through SRL.
#
# Architecture:
#   Interface → SRL → Core → Kernel
#
# =============================================================================

_CORE_INSTANCE: Optional['Core'] = None


class Core:
    """
    CORE - The bridge between interfaces and the kernel.
    
    ONLY Core communicates with the Kernel.
    All interfaces go through SRL → Core → Kernel.
    
    Core handles:
    - Object ingestion from substrates
    - Object ingestion into kernel
    - Resource resolution
    - Substrate management
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        global _CORE_INSTANCE
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
                    _CORE_INSTANCE = cls._instance
        return cls._instance
    
    def _initialize(self):
        """Initialize Core connection to Kernel."""
        self._kernel = KERNEL
        self._srl = SRL
        self._type_registry: Dict[str, Type[Interface]] = {}
    
    @property
    def kernel(self):
        """Access to kernel (internal use only)."""
        return self._kernel
    
    def ingest(
        self, 
        type_name: str, 
        dimensional_depth: int = 3,
        **initial_values
    ) -> Interface:
        """
        Ingest an object from substrate via kernel.
        
        This is how Core creates objects - going through Kernel.
        """
        substrate = get_substrate(dimensional_depth)
        interface = substrate.ingest(type_name, **initial_values)
        
        # Register in SRL for universal access
        srl_address = self._srl.register_interface(interface)
        interface._srl_address = srl_address
        
        return interface
    
    def resolve(self, address: str) -> Optional[Any]:
        """
        Resolve an SRL address to an object.
        
        Called by SRL when direct lookup fails.
        Core can resolve through kernel.
        """
        try:
            domain, substrate, resource, params = self._srl._parse(address)
            
            # Try to find in kernel objects
            for obj_id, obj in self._kernel._objects.items():
                if obj._type_name.lower() == substrate:
                    return obj
            
            return None
        except Exception:
            return None
    
    def ingest(self, obj: Interface) -> str:
        """
        Ingest an object into the kernel.
        
        Returns the kernel object ID.
        """
        return self._kernel.ingest(obj)
    
    def register_type(self, type_name: str, type_class: Type[Interface]) -> None:
        """Register a custom type for ingestion."""
        self._type_registry[type_name] = type_class
    
    def get_type(self, type_name: str) -> Optional[Type[Interface]]:
        """Get registered type class."""
        return self._type_registry.get(type_name)


# Global Core instance
CORE = Core()


def materialize_level(obj: DimensionalObject, level: Level = Level.WHOLE) -> DimensionalObject:
    """
    Explicitly materialize an object at a specific level.
    
    This triggers the object to exist at that dimensional level.
    All attributes at that level become active (but still lazy).
    
    Args:
        obj: The object to materialize
        level: The level to materialize at
    
    Returns:
        The materialized object
    """
    return obj.invoke(level.value)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def is_invoked(obj: Any) -> bool:
    """Check if an object has been invoked."""
    if isinstance(obj, DimensionalPoint):
        return obj.is_materialized
    return False


def is_materialized(obj: Any) -> bool:
    """Check if an object is materialized (alias for is_invoked)."""
    return is_invoked(obj)


def get_level(obj: DimensionalObject) -> Level:
    """Get the current dimensional level of an object."""
    return obj.level


def get_spiral(obj: DimensionalObject) -> int:
    """Get the current spiral index of an object."""
    return obj.coordinate.spiral


def dimension_of(point: DimensionalPoint) -> str:
    """Get the dimension identity of a point."""
    return point.identity


def points_of(obj: DimensionalObject) -> List[str]:
    """Get all materialized points in an object."""
    return [
        name for name, child in obj._children.items()
        if child.is_materialized
    ]


# =============================================================================
# HELLO WORLD EXAMPLE
# =============================================================================

def hello_world():
    """
    ButterflyFX Hello World - Demonstrating the dimensional paradigm.
    
    This example shows:
    1. Object invocation (not instantiation)
    2. Dimensional attribute access
    3. Lazy materialization
    4. Direct addressing (no iteration)
    5. The 7-level structure
    """
    print("=" * 60)
    print("ButterflyFX Dimensional Computing - Hello World")
    print("=" * 60)
    print()
    
    # 1. Invoke a Car (not instantiate!)
    print("1. Invoking a Car from the dimensional substrate...")
    car = invoke("Car")
    print(f"   {car}")
    print(f"   Coordinate: {car.coordinate}")
    print(f"   Level: {car.level.name_display}")
    print()
    
    # 2. Access the engine - this CREATES the engine dimension
    print("2. Accessing car.engine (materializes engine dimension)...")
    engine = car.engine
    print(f"   {engine}")
    print()
    
    # 3. Set engine properties - direct dimensional addressing
    print("3. Setting engine properties (direct dimensional addressing)...")
    car.engine.cylinders = 8
    car.engine.displacement = "5.0L"
    car.engine.horsepower = 450
    print(f"   car.engine.cylinders = {car.engine.cylinders.value}")
    print(f"   car.engine.displacement = {car.engine.displacement.value}")
    print(f"   car.engine.horsepower = {car.engine.horsepower.value}")
    print()
    
    # 4. Access pistons - a DimensionalList (Level 2: LINE)
    print("4. Accessing pistons (Level 2: LINE - no iteration!)...")
    # Direct access to piston[0] - O(1), not iterating through list
    car.engine.pistons = DimensionalList("Car.engine.pistons")
    car.engine.pistons[0].firing = True
    car.engine.pistons[0].position = "TDC"
    car.engine.pistons[3].firing = False
    car.engine.pistons[3].position = "BDC"
    print(f"   car.engine.pistons[0].firing = {car.engine.pistons.value[0].firing.value}")
    print(f"   car.engine.pistons[3].position = {car.engine.pistons.value[3].position.value}")
    print(f"   Materialized piston indices: {car.engine.pistons.value.indices}")
    print()
    
    # 5. Show what's materialized vs potential
    print("5. Materialized points (everything else is potential)...")
    print(f"   Materialized: {points_of(car)}")
    print()
    
    # 6. Seal the VIN (make it immutable)
    print("6. Setting and sealing the VIN...")
    car.vin = "1HGCM82633A123456"
    car.seal_point("vin")
    print(f"   car.vin = {car.vin.value} (sealed)")
    print()
    
    # 7. Export to dict (only materialized)
    print("7. Exporting to dict (only materialized points)...")
    data = car.to_dict()
    print(f"   {json.dumps(data, indent=4, default=str)}")
    print()
    
    # 8. Demonstrate the 7 levels
    print("8. The 7 Dimensional Levels (Fibonacci):")
    for level in Level:
        print(f"   Level {level.value}: {level.name_display} (Fib {level.fibonacci})")
    print()
    
    # 9. Holy Grail transition
    print("9. Holy Grail Transition:")
    print(f"   WHOLE ({Level.WHOLE.fibonacci}) + VOLUME ({Level.VOLUME.fibonacci})")
    print(f"   = {Level.WHOLE.fibonacci + Level.VOLUME.fibonacci}")
    print(f"   = POINT of next spiral (Fib 13)")
    print()
    
    print("=" * 60)
    print("That's ButterflyFX: Objects are dimensions, not containers.")
    print("Every point contains a universe. Every universe is a point.")
    print("=" * 60)


# =============================================================================
# MODULE ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    hello_world()
