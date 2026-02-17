"""
Geometric Substrate - Shapes Hold Data

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)

THE CORE INSIGHT:
    Every mathematical expression has a geometric pattern/shape.
    The shape IS the data. The position IS the value.
    
    We do not have to store what the substrate gives us inherently.
    When data is ingested, it goes WHERE IT BELONGS on the substrate naturally.

INHERENT PROPERTIES OF POINTS:
    - Position (x, y, z, t...)
    - Angle, pitch, yaw
    - Vector from origin
    - Distance from zero
    - Distance from other points
    - Curvature, gradient, slope
    - Normal, tangent, binormal (Frenet-Serret frame)

INHERENT PROPERTIES OF SHAPES:
    - Inflection points
    - Quadrants, signs (+/-)
    - Grid/matrix structure
    - Dimensionality
    - Frequencies, wavelengths
    - Natural spectrums (color, sound, light)

PERSISTENCE:
    Instead of saving data, assign the substrate a position on z=xy.
    Then only a coordinate is needed to invoke the substrate via SRL.

EXAMPLE:
    # A sine wave substrate - values derive from position
    wave = GeometricSubstrate(shape="sin")
    wave[0.5].value      # → sin(0.5) = 0.479... (derived, not stored)
    wave[0.5].angle      # → 0.5 radians
    wave[0.5].slope      # → cos(0.5) (derivative at point)
    wave[0.5].curvature  # → -sin(0.5)
    
    # A color spectrum substrate
    spectrum = GeometricSubstrate(shape="linear", lens="color")
    spectrum[0.5].rgb    # → (128, 128, 128) middle gray
    spectrum[0.0].rgb    # → (0, 0, 0) black
    spectrum[1.0].rgb    # → (255, 255, 255) white
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Tuple, List, Callable, Union
from dataclasses import dataclass, field
from enum import Enum, auto
import math


# =============================================================================
# LENS - How to interpret the substrate
# =============================================================================

class Lens(Enum):
    """
    Same geometry, different interpretation.
    The shape is the data - the lens is how we read it.
    """
    VALUE = auto()      # Raw numeric value
    COLOR = auto()      # RGB/HSL color space
    SOUND = auto()      # Frequency/amplitude/waveform
    LIGHT = auto()      # Wavelength/intensity
    ANGLE = auto()      # Radians/degrees
    PERCENT = auto()    # 0-100%
    BINARY = auto()     # On/off threshold
    GRADIENT = auto()   # Rate of change
    
    # Natural spectrums
    VISIBLE = auto()    # 380-700nm light
    AUDIBLE = auto()    # 20Hz-20kHz sound
    THERMAL = auto()    # Temperature


# =============================================================================
# GEOMETRIC PROPERTIES - Inherent to every point
# =============================================================================

class GeometricProperty(Enum):
    """
    Properties that exist INHERENTLY at every point on a shape.
    These are derived, not stored.
    """
    # Position
    X = auto()          # X coordinate
    Y = auto()          # Y coordinate  
    Z = auto()          # Z coordinate (on z=xy substrate)
    T = auto()          # Time/parametric position
    
    # Trigonometric (derived from position)
    SIN = auto()        # sin(position)
    COS = auto()        # cos(position)
    TAN = auto()        # tan(position)
    
    # Derivatives (rate of change)
    SLOPE = auto()      # First derivative dy/dx
    GRADIENT = auto()   # Gradient vector
    CURVATURE = auto()  # Second derivative d²y/dx²
    
    # Geometric frame (Frenet-Serret)
    NORMAL = auto()     # Normal vector
    TANGENT = auto()    # Tangent vector
    BINORMAL = auto()   # Binormal vector
    TORSION = auto()    # Rate of twist
    
    # Distance
    DISTANCE = auto()   # Distance from origin
    ARC_LENGTH = auto() # Arc length from start
    
    # Angles
    ANGLE = auto()      # Angle from positive x-axis
    PITCH = auto()      # Rotation about x
    YAW = auto()        # Rotation about y
    ROLL = auto()       # Rotation about z
    
    # Signs and regions
    SIGN = auto()       # +1 or -1
    QUADRANT = auto()   # Which quadrant (1-4)
    OCTANT = auto()     # Which octant (1-8 in 3D)


# =============================================================================
# SHAPE - The mathematical substrate form
# =============================================================================

class Shape(Enum):
    """
    Mathematical shapes that can serve as substrates.
    Each shape has inherent properties that derive data.
    """
    # 1D Shapes
    LINE = auto()           # Linear: y = mx + b
    SINE = auto()           # Sinusoidal: y = sin(x)
    COSINE = auto()         # Cosine wave: y = cos(x)
    EXPONENTIAL = auto()    # Exponential: y = e^x
    LOGARITHM = auto()      # Logarithmic: y = ln(x)
    PARABOLA = auto()       # Quadratic: y = x²
    
    # 2D Shapes (first substrates - z=xy)
    PLANE = auto()          # Flat plane
    SADDLE = auto()         # Hyperbolic paraboloid: z = xy
    SPHERE = auto()         # Spherical surface
    TORUS = auto()          # Donut shape
    CONE = auto()           # Conical surface
    CYLINDER = auto()       # Cylindrical surface
    
    # Grid/Matrix shapes
    GRID = auto()           # Regular 2D grid
    HEXGRID = auto()        # Hexagonal grid
    MATRIX = auto()         # NxM matrix
    
    # Spiral shapes
    FIBONACCI = auto()      # Golden spiral
    ARCHIMEDEAN = auto()    # Archimedean spiral
    LOGARITHMIC = auto()    # Logarithmic spiral
    HELIX = auto()          # 3D helix (our dimensional spiral)
    
    # Fractal shapes
    MANDELBROT = auto()     # Mandelbrot set
    JULIA = auto()          # Julia set
    SIERPINSKI = auto()     # Sierpinski triangle
    
    # Natural shapes
    BELL = auto()           # Gaussian/bell curve
    WAVE = auto()           # Complex wave (sum of frequencies)
    SPECTRUM = auto()       # Continuous spectrum


# =============================================================================
# POINT - A position on the substrate with inherent properties
# =============================================================================

@dataclass
class Point:
    """
    A point on a geometric substrate.
    
    Properties are DERIVED from position, not stored.
    The shape gives us the data inherently.
    """
    substrate: 'GeometricSubstrate'
    coords: Tuple[float, ...]
    
    @property
    def x(self) -> float:
        """X coordinate."""
        return self.coords[0] if len(self.coords) > 0 else 0.0
    
    @property
    def y(self) -> float:
        """Y coordinate - derived from shape at x."""
        return self.substrate.evaluate(self.coords)
    
    @property
    def z(self) -> float:
        """Z coordinate (on z=xy substrate)."""
        return self.x * self.y
    
    # =========================================================================
    # INHERENT TRIGONOMETRIC PROPERTIES
    # =========================================================================
    
    @property
    def sin(self) -> float:
        """sin(position) - inherent, not stored."""
        return math.sin(self.x)
    
    @property
    def cos(self) -> float:
        """cos(position) - inherent, not stored."""
        return math.cos(self.x)
    
    @property
    def tan(self) -> float:
        """tan(position) - inherent, not stored."""
        return math.tan(self.x)
    
    # =========================================================================
    # INHERENT DERIVATIVE PROPERTIES
    # =========================================================================
    
    @property
    def slope(self) -> float:
        """First derivative at this point - dy/dx."""
        return self.substrate.derivative(self.coords)
    
    @property
    def gradient(self) -> Tuple[float, ...]:
        """Gradient vector at this point."""
        return self.substrate.gradient(self.coords)
    
    @property
    def curvature(self) -> float:
        """Curvature (second derivative) at this point."""
        return self.substrate.curvature(self.coords)
    
    # =========================================================================
    # INHERENT DISTANCE PROPERTIES
    # =========================================================================
    
    @property
    def distance(self) -> float:
        """Distance from origin."""
        return math.sqrt(sum(c**2 for c in self.coords))
    
    @property
    def angle(self) -> float:
        """Angle from positive x-axis (radians)."""
        if len(self.coords) >= 2:
            return math.atan2(self.coords[1], self.coords[0])
        return 0.0
    
    @property
    def sign(self) -> int:
        """Sign of value at this point (+1 or -1)."""
        return 1 if self.y >= 0 else -1
    
    @property
    def quadrant(self) -> int:
        """Which quadrant (1-4)."""
        if self.x >= 0 and self.y >= 0:
            return 1
        elif self.x < 0 and self.y >= 0:
            return 2
        elif self.x < 0 and self.y < 0:
            return 3
        else:
            return 4
    
    # =========================================================================
    # LENS INTERPRETATIONS
    # =========================================================================
    
    def as_color(self) -> Tuple[int, int, int]:
        """Interpret value as RGB color."""
        # Normalize y to 0-1 range based on substrate bounds
        normalized = self.substrate.normalize(self.y)
        # Map to grayscale by default
        v = int(normalized * 255)
        return (v, v, v)
    
    def as_sound(self) -> Dict[str, float]:
        """Interpret value as sound properties."""
        return {
            "frequency": 440 * (2 ** (self.y / 12)),  # Semitone mapping
            "amplitude": abs(self.y),
            "phase": self.angle,
        }
    
    def as_light(self) -> Dict[str, float]:
        """Interpret value as light properties."""
        # Map to visible spectrum (380-700nm)
        normalized = self.substrate.normalize(self.y)
        wavelength = 380 + normalized * 320
        return {
            "wavelength_nm": wavelength,
            "intensity": abs(self.y),
        }
    
    @property
    def value(self) -> float:
        """The raw value at this point (y)."""
        return self.y
    
    # =========================================================================
    # FRENET-SERRET FRAME
    # =========================================================================
    
    @property
    def tangent(self) -> Tuple[float, float]:
        """Tangent vector at this point."""
        s = self.slope
        mag = math.sqrt(1 + s**2)
        return (1/mag, s/mag)
    
    @property
    def normal(self) -> Tuple[float, float]:
        """Normal vector (perpendicular to tangent)."""
        tx, ty = self.tangent
        return (-ty, tx)
    
    def distance_to(self, other: 'Point') -> float:
        """Distance to another point."""
        return math.sqrt(sum((a - b)**2 for a, b in zip(self.coords, other.coords)))


# =============================================================================
# GEOMETRIC SUBSTRATE - The shape that holds data
# =============================================================================

class GeometricSubstrate:
    """
    A geometric substrate where shapes hold data inherently.
    
    THE PRINCIPLE:
        We do not store what the substrate gives us naturally.
        When data is ingested, it goes WHERE IT BELONGS.
        Any datatype can be a substrate.
    
    USAGE:
        # Create a sine wave substrate
        wave = GeometricSubstrate(Shape.SINE)
        wave[0.5]          # Point at x=0.5
        wave[0.5].value    # sin(0.5) ≈ 0.479 (derived, not stored)
        wave[0.5].slope    # cos(0.5) (derivative)
        
        # Create a z=xy substrate (saddle point - first 2D substrate)
        plane = GeometricSubstrate(Shape.SADDLE)
        plane[2, 3].z      # 2 * 3 = 6 (derived from position)
        
        # Assign substrate to z=xy for persistence
        plane.position = (x_coord, y_coord)  # Now only need this coord to invoke
        
        # Any datatype as substrate
        car = GeometricSubstrate.from_object(car_data)
    """
    
    def __init__(
        self,
        shape: Shape = Shape.LINE,
        lens: Lens = Lens.VALUE,
        bounds: Tuple[float, float] = (-10.0, 10.0),
        params: Optional[Dict[str, Any]] = None,
    ):
        self.shape = shape
        self.lens = lens
        self.bounds = bounds
        self.params = params or {}
        
        # Position on z=xy for persistence (optional)
        self._position: Optional[Tuple[float, float]] = None
        
        # Custom data overlaid on substrate (sparse storage)
        self._overlay: Dict[Tuple[float, ...], Any] = {}
    
    # =========================================================================
    # CORE EVALUATION - Derive value from shape
    # =========================================================================
    
    def evaluate(self, coords: Tuple[float, ...]) -> float:
        """
        Evaluate the substrate at given coordinates.
        This is DERIVED from the shape, not stored.
        """
        x = coords[0] if coords else 0.0
        
        # Check overlay first (for ingested data)
        if coords in self._overlay:
            return self._overlay[coords]
        
        # Derive from shape
        if self.shape == Shape.LINE:
            m = self.params.get('m', 1.0)
            b = self.params.get('b', 0.0)
            return m * x + b
        
        elif self.shape == Shape.SINE:
            freq = self.params.get('frequency', 1.0)
            amp = self.params.get('amplitude', 1.0)
            phase = self.params.get('phase', 0.0)
            return amp * math.sin(freq * x + phase)
        
        elif self.shape == Shape.COSINE:
            freq = self.params.get('frequency', 1.0)
            amp = self.params.get('amplitude', 1.0)
            return amp * math.cos(freq * x)
        
        elif self.shape == Shape.EXPONENTIAL:
            return math.exp(x)
        
        elif self.shape == Shape.LOGARITHM:
            return math.log(max(x, 0.001))  # Avoid log(0)
        
        elif self.shape == Shape.PARABOLA:
            return x ** 2
        
        elif self.shape == Shape.SADDLE:
            # z = xy - the FIRST SUBSTRATE
            y = coords[1] if len(coords) > 1 else x
            return x * y
        
        elif self.shape == Shape.PLANE:
            return 0.0  # Flat plane at z=0
        
        elif self.shape == Shape.SPHERE:
            r = self.params.get('radius', 1.0)
            y = coords[1] if len(coords) > 1 else 0.0
            val = r**2 - x**2 - y**2
            return math.sqrt(max(val, 0))
        
        elif self.shape == Shape.BELL:
            sigma = self.params.get('sigma', 1.0)
            return math.exp(-(x**2) / (2 * sigma**2))
        
        elif self.shape == Shape.FIBONACCI:
            # Golden spiral: r = φ^(θ/90°)
            phi = (1 + math.sqrt(5)) / 2
            return phi ** (x / (math.pi/2))
        
        elif self.shape == Shape.HELIX:
            # 3D helix - returns z at parameter t
            pitch = self.params.get('pitch', 1.0)
            return pitch * x
        
        else:
            return x  # Default to identity
    
    def derivative(self, coords: Tuple[float, ...], h: float = 0.0001) -> float:
        """First derivative at point (numerical approximation)."""
        x = coords[0]
        y1 = self.evaluate((x - h,))
        y2 = self.evaluate((x + h,))
        return (y2 - y1) / (2 * h)
    
    def gradient(self, coords: Tuple[float, ...]) -> Tuple[float, ...]:
        """Gradient vector at point."""
        h = 0.0001
        grad = []
        for i in range(len(coords)):
            c_minus = list(coords)
            c_plus = list(coords)
            c_minus[i] -= h
            c_plus[i] += h
            grad.append((self.evaluate(tuple(c_plus)) - self.evaluate(tuple(c_minus))) / (2 * h))
        return tuple(grad)
    
    def curvature(self, coords: Tuple[float, ...], h: float = 0.0001) -> float:
        """Second derivative (curvature) at point."""
        x = coords[0]
        y0 = self.evaluate((x,))
        y_minus = self.evaluate((x - h,))
        y_plus = self.evaluate((x + h,))
        return (y_plus - 2*y0 + y_minus) / (h**2)
    
    def normalize(self, value: float) -> float:
        """Normalize value to 0-1 range."""
        lo, hi = self.bounds
        return max(0.0, min(1.0, (value - lo) / (hi - lo)))
    
    # =========================================================================
    # POINT ACCESS - Direct addressing
    # =========================================================================
    
    def __getitem__(self, key) -> Point:
        """Get point at coordinates."""
        if isinstance(key, (int, float)):
            coords = (float(key),)
        elif isinstance(key, tuple):
            coords = tuple(float(k) for k in key)
        else:
            coords = (float(key),)
        return Point(self, coords)
    
    def __setitem__(self, key, value: Any) -> None:
        """
        Ingest data at coordinates.
        Data goes WHERE IT BELONGS on the substrate.
        """
        if isinstance(key, (int, float)):
            coords = (float(key),)
        elif isinstance(key, tuple):
            coords = tuple(float(k) for k in key)
        else:
            coords = (float(key),)
        
        # Overlay ingested data
        self._overlay[coords] = value
    
    # =========================================================================
    # PERSISTENCE - Assign position on z=xy
    # =========================================================================
    
    @property
    def position(self) -> Optional[Tuple[float, float]]:
        """Position on z=xy substrate for persistence."""
        return self._position
    
    @position.setter
    def position(self, coords: Tuple[float, float]) -> None:
        """
        Assign this substrate a position on z=xy.
        Only this coordinate is needed to invoke the substrate.
        """
        self._position = coords
    
    @property
    def srl(self) -> str:
        """Generate SRL from z=xy position."""
        if self._position:
            x, y = self._position
            return f"srl://substrate/{self.shape.name.lower()}/{x}.{y}"
        return f"srl://substrate/{self.shape.name.lower()}/unpositioned"
    
    # =========================================================================
    # SHAPE PROPERTIES - Inherent to the geometry
    # =========================================================================
    
    @property
    def inflection_points(self) -> List[float]:
        """Find inflection points (where curvature changes sign)."""
        points = []
        h = 0.1
        prev_sign = None
        lo, hi = self.bounds
        x = lo
        while x <= hi:
            curv = self.curvature((x,))
            sign = 1 if curv >= 0 else -1
            if prev_sign is not None and sign != prev_sign:
                points.append(x)
            prev_sign = sign
            x += h
        return points
    
    @property
    def zeros(self) -> List[float]:
        """Find zeros (where value crosses zero)."""
        points = []
        h = 0.1
        prev_sign = None
        lo, hi = self.bounds
        x = lo
        while x <= hi:
            val = self.evaluate((x,))
            sign = 1 if val >= 0 else -1
            if prev_sign is not None and sign != prev_sign:
                points.append(x)
            prev_sign = sign
            x += h
        return points
    
    @property
    def min_max(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Find min and max points."""
        lo, hi = self.bounds
        h = 0.1
        min_pt = (lo, self.evaluate((lo,)))
        max_pt = (lo, self.evaluate((lo,)))
        x = lo
        while x <= hi:
            val = self.evaluate((x,))
            if val < min_pt[1]:
                min_pt = (x, val)
            if val > max_pt[1]:
                max_pt = (x, val)
            x += h
        return (min_pt, max_pt)
    
    # =========================================================================
    # SPECTRUM PROPERTIES
    # =========================================================================
    
    @property
    def frequency(self) -> float:
        """Primary frequency (for periodic shapes)."""
        return self.params.get('frequency', 1.0)
    
    @property
    def wavelength(self) -> float:
        """Wavelength = 2π / frequency."""
        return (2 * math.pi) / self.frequency
    
    @property
    def bandwidth(self) -> float:
        """Bandwidth (range of active frequencies)."""
        return self.params.get('bandwidth', self.frequency)
    
    # =========================================================================
    # FACTORY METHODS
    # =========================================================================
    
    @classmethod
    def from_object(cls, obj: Any) -> 'GeometricSubstrate':
        """
        Create substrate from any object/datatype.
        The object becomes the substrate.
        """
        substrate = cls(Shape.GRID)
        
        if isinstance(obj, dict):
            for i, (key, value) in enumerate(obj.items()):
                substrate[(float(i), 0.0)] = value
        elif isinstance(obj, (list, tuple)):
            for i, value in enumerate(obj):
                substrate[(float(i),)] = value
        else:
            substrate[(0.0,)] = obj
        
        return substrate
    
    @classmethod
    def saddle(cls) -> 'GeometricSubstrate':
        """Create z=xy substrate (the first 2D substrate)."""
        return cls(Shape.SADDLE)
    
    @classmethod
    def sine(cls, frequency: float = 1.0, amplitude: float = 1.0) -> 'GeometricSubstrate':
        """Create sine wave substrate."""
        return cls(Shape.SINE, params={'frequency': frequency, 'amplitude': amplitude})
    
    @classmethod
    def helix(cls, pitch: float = 1.0) -> 'GeometricSubstrate':
        """Create helix substrate (the dimensional spiral)."""
        return cls(Shape.HELIX, params={'pitch': pitch})
    
    @classmethod
    def fibonacci(cls) -> 'GeometricSubstrate':
        """Create golden spiral substrate."""
        return cls(Shape.FIBONACCI)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'Lens',
    'GeometricProperty',
    'Shape',
    'Point',
    'GeometricSubstrate',
]
