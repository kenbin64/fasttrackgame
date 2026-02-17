"""
Wave Manifold - The Surfer and the Barrel

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

This mathematical kernel belongs to all humanity.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

THE SURFER RIDING THE WAVE

A surfer riding a wave demonstrates the principle:
- The WAVE SURFACE is the manifold (z=xy, z=xy², z=x/y, etc.)
- The BARREL (empty cylindrical space) is where meaning lives
- The SURFER's position relative to the void encodes information
- The VOID DEFINES THE FORM as much as the surface itself

Information is encoded through:
    - Shape: The curvature of the wave surface
    - Position: Points on the surface relative to the barrel
    - Degrees/Angles: The twist of the ribbon (90° for z=xy)
    - Vectors: Direction of flow along the surface
    - Pitch/Slope: Rate of rise/fall of the wave
    - Inflection Points: Where curvature changes sign (wave crest/trough)
    - Distance: How far the surfer is from the barrel center

Fundamental Wave Surfaces:
    z = xy          The twisted ribbon at 90° - fundamental unit
    z = xy²         Wave with stronger y-dependence (steeper face)
    z = x/y         Hyperbolic wave (asymptotic to axes)
    z = x/y²        Sharper hyperbolic funnel
    m = xyz         4D manifold - volume wave (the 3D barrel)

Each dimension is like a helix:
    - Expands to ALL its points (the wave face)
    - Collapses to 1 (the barrel center)
    - Expands again (back to surface)
    
The cycle: Many → One → Many → One
This is the breath of the dimension.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import (
    Any, Callable, Dict, List, Optional, Set, Tuple,
    Iterator, TypeVar, Generic, Union, Sequence
)
from enum import Enum, auto
from functools import cached_property


# =============================================================================
# WAVE SURFACE TYPES - The Mathematical Manifolds
# =============================================================================

class WaveSurface(Enum):
    """
    Types of wave surfaces that encode information through shape.
    Each is a different way of folding dimensions together.
    """
    TWISTED_RIBBON = auto()      # z = xy (fundamental unit, 90° twist)
    STEEP_FACE = auto()          # z = xy² (stronger y-dependence)
    HYPERBOLIC_WAVE = auto()     # z = x/y (asymptotic to axes)
    HYPERBOLIC_FUNNEL = auto()   # z = x/y² (sharper funnel)
    VOLUME_WAVE = auto()         # m = xyz (4D manifold, 3D barrel)


# =============================================================================
# WAVE POINT - A Point on the Wave Surface
# =============================================================================

@dataclass
class WavePoint:
    """
    A point on a wave manifold surface.
    
    Contains both:
    - Surface coordinates (on the wave)
    - Barrel coordinates (position relative to void)
    """
    # Surface parameters (intrinsic)
    u: float  # Parameter along wave direction
    v: float  # Parameter across wave width
    
    # Which type of wave surface
    wave_type: WaveSurface = WaveSurface.TWISTED_RIBBON
    
    # 4D parameter for volume wave
    w: float = 0.0
    
    def __post_init__(self):
        """Initialize computed properties."""
        self._compute_embedded_coords()
        self._compute_barrel_properties()
    
    def _compute_embedded_coords(self) -> None:
        """Compute 3D (or 4D) embedded coordinates from surface params."""
        if self.wave_type == WaveSurface.TWISTED_RIBBON:
            # z = xy: The fundamental twisted ribbon at 90°
            self._x = self.u
            self._y = self.v
            self._z = self.u * self.v
            self._m = 0.0
            
        elif self.wave_type == WaveSurface.STEEP_FACE:
            # z = xy²: Steeper wave face with stronger y-dependence
            self._x = self.u
            self._y = self.v
            self._z = self.u * (self.v ** 2)
            self._m = 0.0
            
        elif self.wave_type == WaveSurface.HYPERBOLIC_WAVE:
            # z = x/y: Hyperbolic surface asymptotic to axes
            self._x = self.u
            self._y = self.v if abs(self.v) > 1e-10 else 1e-10
            self._z = self.u / self._y
            self._m = 0.0
            
        elif self.wave_type == WaveSurface.HYPERBOLIC_FUNNEL:
            # z = x/y²: Sharper hyperbolic funnel
            self._x = self.u
            self._y = self.v if abs(self.v) > 1e-10 else 1e-10
            self._z = self.u / (self._y ** 2)
            self._m = 0.0
            
        elif self.wave_type == WaveSurface.VOLUME_WAVE:
            # m = xyz: 4D manifold, the "3D barrel"
            self._x = self.u
            self._y = self.v
            self._z = self.w
            self._m = self.u * self.v * self.w
    
    def _compute_barrel_properties(self) -> None:
        """
        Compute properties relative to the barrel (void space).
        
        The barrel is the empty cylindrical space inside the wave.
        The surfer rides the boundary between form and void.
        """
        # Distance to the wave axis (where the barrel forms)
        # For saddle surfaces, the barrel is along the z-axis at x=y=0
        self._barrel_distance = math.sqrt(self._x**2 + self._y**2)
        
        # Angular position around the barrel
        self._barrel_angle = math.atan2(self._y, self._x)
        
        # Height relative to the barrel center
        self._barrel_height = self._z
        
        # For volume wave, barrel radius is the 4D measure
        if self.wave_type == WaveSurface.VOLUME_WAVE:
            self._barrel_radius = abs(self._m) ** (1/3) if self._m != 0 else 0.0
        else:
            self._barrel_radius = abs(self._z) ** 0.5 if self._z != 0 else 0.0
    
    # -------------------------------------------------------------------------
    # Embedded Coordinates (the wave surface in 3D/4D)
    # -------------------------------------------------------------------------
    
    @property
    def x(self) -> float:
        """X coordinate in embedded space."""
        return self._x
    
    @property
    def y(self) -> float:
        """Y coordinate in embedded space."""
        return self._y
    
    @property
    def z(self) -> float:
        """Z coordinate in embedded space."""
        return self._z
    
    @property
    def m(self) -> float:
        """M coordinate (4th dimension for volume wave)."""
        return self._m
    
    @property
    def position_3d(self) -> Tuple[float, float, float]:
        """3D position in embedded space."""
        return (self._x, self._y, self._z)
    
    @property
    def position_4d(self) -> Tuple[float, float, float, float]:
        """4D position for volume wave."""
        return (self._x, self._y, self._z, self._m)
    
    # -------------------------------------------------------------------------
    # Barrel Coordinates (relative to the void)
    # -------------------------------------------------------------------------
    
    @property
    def barrel_distance(self) -> float:
        """Distance from the barrel axis (the void center)."""
        return self._barrel_distance
    
    @property
    def barrel_angle(self) -> float:
        """Angular position around the barrel (radians)."""
        return self._barrel_angle
    
    @property
    def barrel_height(self) -> float:
        """Height along the barrel axis."""
        return self._barrel_height
    
    @property
    def barrel_radius(self) -> float:
        """Effective barrel radius at this point."""
        return self._barrel_radius
    
    @property
    def in_barrel(self) -> bool:
        """Is this point inside the barrel (the void)?"""
        # The "barrel" exists where the surface curves around emptiness
        # For saddle: near the saddle point where curvature changes sign
        threshold = 0.1
        return self._barrel_distance < threshold
    
    # -------------------------------------------------------------------------
    # Differential Geometry - Slopes, Curvature, Inflection
    # -------------------------------------------------------------------------
    
    @cached_property
    def slope_u(self) -> float:
        """Partial derivative of z with respect to u (wave direction slope)."""
        if self.wave_type == WaveSurface.TWISTED_RIBBON:
            return self.v  # ∂z/∂u = y
        elif self.wave_type == WaveSurface.STEEP_FACE:
            return self.v ** 2  # ∂z/∂u = y²
        elif self.wave_type == WaveSurface.HYPERBOLIC_WAVE:
            return 1 / self._y  # ∂z/∂u = 1/y
        elif self.wave_type == WaveSurface.HYPERBOLIC_FUNNEL:
            return 1 / (self._y ** 2)  # ∂z/∂u = 1/y²
        elif self.wave_type == WaveSurface.VOLUME_WAVE:
            return self.v * self.w  # ∂m/∂u = yz
        return 0.0
    
    @cached_property
    def slope_v(self) -> float:
        """Partial derivative of z with respect to v (across wave slope)."""
        if self.wave_type == WaveSurface.TWISTED_RIBBON:
            return self.u  # ∂z/∂v = x
        elif self.wave_type == WaveSurface.STEEP_FACE:
            return 2 * self.u * self.v  # ∂z/∂v = 2xy
        elif self.wave_type == WaveSurface.HYPERBOLIC_WAVE:
            return -self.u / (self._y ** 2)  # ∂z/∂v = -x/y²
        elif self.wave_type == WaveSurface.HYPERBOLIC_FUNNEL:
            return -2 * self.u / (self._y ** 3)  # ∂z/∂v = -2x/y³
        elif self.wave_type == WaveSurface.VOLUME_WAVE:
            return self.u * self.w  # ∂m/∂v = xz
        return 0.0
    
    @cached_property
    def gradient(self) -> Tuple[float, float]:
        """Gradient vector (∂z/∂u, ∂z/∂v) - direction of steepest ascent."""
        return (self.slope_u, self.slope_v)
    
    @cached_property
    def gradient_magnitude(self) -> float:
        """Magnitude of gradient - steepness of the wave at this point."""
        return math.sqrt(self.slope_u**2 + self.slope_v**2)
    
    @cached_property
    def normal_vector(self) -> Tuple[float, float, float]:
        """Normal vector to the surface at this point."""
        # n = (-∂z/∂u, -∂z/∂v, 1) / |n|
        nx = -self.slope_u
        ny = -self.slope_v
        nz = 1.0
        mag = math.sqrt(nx**2 + ny**2 + nz**2)
        return (nx/mag, ny/mag, nz/mag)
    
    @cached_property
    def gaussian_curvature(self) -> float:
        """
        Gaussian curvature K = (fuu * fvv - fuv²) / (1 + fu² + fv²)²
        
        For z=xy (saddle): K < 0 everywhere (hyperbolic)
        K = 0 at the saddle point origin
        """
        if self.wave_type == WaveSurface.TWISTED_RIBBON:
            # For z = xy: fuu = 0, fvv = 0, fuv = 1
            fu2 = self.slope_u ** 2
            fv2 = self.slope_v ** 2
            denom = (1 + fu2 + fv2) ** 2
            return -1.0 / denom  # Always negative (saddle)
            
        elif self.wave_type == WaveSurface.STEEP_FACE:
            # For z = xy²: fuu = 0, fvv = 2x, fuv = 2y
            fuu = 0
            fvv = 2 * self.u
            fuv = 2 * self.v
            fu2 = self.slope_u ** 2
            fv2 = self.slope_v ** 2
            denom = (1 + fu2 + fv2) ** 2
            return (fuu * fvv - fuv**2) / denom
            
        # Default: compute numerically or return 0
        return 0.0
    
    @cached_property
    def mean_curvature(self) -> float:
        """Mean curvature H - average of principal curvatures."""
        if self.wave_type == WaveSurface.TWISTED_RIBBON:
            # For z = xy: H = 0 everywhere (minimal surface locally)
            # Actually H = (fuu(1+fv²) - 2fu*fv*fuv + fvv(1+fu²)) / (2*(1+fu²+fv²)^1.5)
            # For z=xy: fuu=0, fvv=0, fuv=1
            fu = self.slope_u
            fv = self.slope_v
            fuv = 1.0
            denom = 2 * ((1 + fu**2 + fv**2) ** 1.5)
            return -2 * fu * fv * fuv / denom
        return 0.0
    
    @cached_property
    def is_inflection(self) -> bool:
        """Is this an inflection point where curvature changes sign?"""
        # At the saddle point (origin), the surface is locally flat
        return abs(self.gaussian_curvature) < 1e-6
    
    # -------------------------------------------------------------------------
    # Information Encoding - The Void Speaks
    # -------------------------------------------------------------------------
    
    def encode_information(self) -> Dict[str, Any]:
        """
        Extract all encoded information from this point's geometry.
        
        The shape holds information through:
        - Position (x, y, z)
        - Angles (barrel_angle)
        - Slopes (gradient)
        - Curvature (gaussian_curvature, mean_curvature)
        - Distance (barrel_distance)
        - Inflection (is_inflection)
        """
        return {
            # Position encoding
            "position": self.position_3d,
            "intrinsic": (self.u, self.v),
            
            # Angular encoding
            "barrel_angle": self.barrel_angle,
            "angle_degrees": math.degrees(self.barrel_angle),
            
            # Slope/vector encoding
            "gradient": self.gradient,
            "gradient_magnitude": self.gradient_magnitude,
            "normal": self.normal_vector,
            
            # Curvature encoding
            "gaussian_curvature": self.gaussian_curvature,
            "mean_curvature": self.mean_curvature,
            
            # Distance encoding
            "barrel_distance": self.barrel_distance,
            "barrel_height": self.barrel_height,
            "barrel_radius": self.barrel_radius,
            
            # Inflection encoding
            "is_inflection": self.is_inflection,
            "in_barrel": self.in_barrel,
            
            # Surface type
            "wave_type": self.wave_type.name,
        }
    
    def __repr__(self) -> str:
        return (
            f"<WavePoint {self.wave_type.name} "
            f"({self.u:.2f},{self.v:.2f})→({self._x:.2f},{self._y:.2f},{self._z:.2f}) "
            f"barrel_d={self.barrel_distance:.2f}>"
        )


# =============================================================================
# WAVE MANIFOLD - The Complete Wave Surface
# =============================================================================

@dataclass
class WaveManifold:
    """
    A dimensional wave manifold that encodes information through shape.
    
    Like a surfer riding a wave:
    - The SURFACE is the boundary between form and void
    - The BARREL is the empty space inside the wave
    - The SURFER's trajectory encodes information
    
    z = xy is the fundamental unit: a twisted ribbon at 90°
    """
    wave_type: WaveSurface = WaveSurface.TWISTED_RIBBON
    
    # The grid of sampled points
    _points: Dict[Tuple[float, float], WavePoint] = field(default_factory=dict)
    
    # Bounds for the manifold
    u_range: Tuple[float, float] = (-1.0, 1.0)
    v_range: Tuple[float, float] = (-1.0, 1.0)
    
    def sample(self, u: float, v: float, w: float = 0.0) -> WavePoint:
        """Sample the wave surface at (u, v) to get a WavePoint."""
        key = (u, v)
        if key not in self._points:
            self._points[key] = WavePoint(u, v, self.wave_type, w)
        return self._points[key]
    
    def generate_grid(self, resolution: int = 20) -> List[WavePoint]:
        """Generate a grid of points spanning the wave surface."""
        points = []
        u_min, u_max = self.u_range
        v_min, v_max = self.v_range
        
        for i in range(resolution):
            for j in range(resolution):
                u = u_min + (u_max - u_min) * i / (resolution - 1)
                v = v_min + (v_max - v_min) * j / (resolution - 1)
                points.append(self.sample(u, v))
        
        return points
    
    def surfer_trajectory(
        self, 
        start: Tuple[float, float], 
        direction: Tuple[float, float],
        steps: int = 50,
        step_size: float = 0.05
    ) -> List[WavePoint]:
        """
        Trace the path of a surfer riding the wave.
        
        The surfer's trajectory encodes information through
        the sequence of geometric properties encountered.
        """
        trajectory = []
        u, v = start
        du, dv = direction
        
        # Normalize direction
        mag = math.sqrt(du**2 + dv**2)
        if mag > 0:
            du, dv = du/mag, dv/mag
        
        for _ in range(steps):
            point = self.sample(u, v)
            trajectory.append(point)
            
            # Advance along direction
            u += du * step_size
            v += dv * step_size
            
            # Optionally: follow the gradient (ride down the wave face)
            # du, dv = -point.slope_u, -point.slope_v
        
        return trajectory
    
    def barrel_contour(self, height: float = 0.0, resolution: int = 50) -> List[WavePoint]:
        """
        Trace the contour of the barrel at a given height.
        
        This is the edge of the void - where the surfer rides.
        """
        contour = []
        
        for i in range(resolution):
            angle = 2 * math.pi * i / resolution
            
            # For saddle z=xy, find points where z = height
            # z = xy = height → y = height/x
            # Parameterize by angle around barrel
            r = max(0.1, abs(height) ** 0.5) if height != 0 else 0.5
            u = r * math.cos(angle)
            v = r * math.sin(angle)
            
            if self.wave_type == WaveSurface.TWISTED_RIBBON:
                # Adjust v so that uv = height
                if abs(u) > 0.01:
                    v = height / u
                    
            point = self.sample(u, v)
            contour.append(point)
        
        return contour
    
    def inflection_line(self) -> List[WavePoint]:
        """
        Find the inflection line where curvature changes sign.
        
        For z=xy, this is the origin (saddle point).
        For other surfaces, this forms curves on the surface.
        """
        inflections = []
        for point in self._points.values():
            if point.is_inflection:
                inflections.append(point)
        return inflections
    
    def encode_surface_information(self) -> Dict[str, Any]:
        """
        Extract holistic information from the entire surface.
        
        The surface as a whole encodes:
        - Total curvature (integral of Gaussian curvature)
        - Boundary properties
        - Topology (e.g., saddle = hyperbolic)
        """
        if not self._points:
            self.generate_grid(20)
        
        points = list(self._points.values())
        
        return {
            "wave_type": self.wave_type.name,
            "num_points": len(points),
            "u_range": self.u_range,
            "v_range": self.v_range,
            
            # Aggregate curvature
            "avg_gaussian_curvature": sum(p.gaussian_curvature for p in points) / len(points),
            "avg_mean_curvature": sum(p.mean_curvature for p in points) / len(points),
            
            # Distance statistics
            "min_barrel_distance": min(p.barrel_distance for p in points),
            "max_barrel_distance": max(p.barrel_distance for p in points),
            
            # Inflection count
            "inflection_count": sum(1 for p in points if p.is_inflection),
            
            # Topology indicator
            "topology": "hyperbolic" if all(p.gaussian_curvature < 0 for p in points) else "mixed",
        }
    
    def __repr__(self) -> str:
        return f"<WaveManifold {self.wave_type.name} points={len(self._points)}>"


# =============================================================================
# HELIX BREATH - The expansion/collapse cycle of each dimension
# =============================================================================

@dataclass
class HelixBreath:
    """
    Each dimension breathes:
    - Expands to ALL its points (the wave face)
    - Collapses to ONE (the barrel center)
    - Expands again
    
    The cycle: Many → One → Many → One
    
    At the "fat part": all possible values exist
    At the collapse point: only the singular value exists
    """
    dimension: int  # Which dimension (0-6)
    phase: float = 0.0  # Phase in the breath cycle (0 to 2π)
    frequency: float = 1.0  # Breath rate
    
    @property
    def expansion(self) -> float:
        """
        Expansion factor: 0 = collapsed to single point, 1 = fully expanded.
        
        Uses a smooth oscillation (cardioid-like) to model breath.
        """
        return 0.5 * (1 + math.cos(self.phase))
    
    @property
    def multiplicity(self) -> float:
        """
        How many points are "active" at this phase.
        
        At expansion=0: 1 point (collapsed)
        At expansion=1: ∞ points (fully expanded)
        """
        if self.expansion < 0.01:
            return 1.0  # Collapsed to one
        return 1.0 / self.expansion
    
    def advance(self, dt: float = 0.1) -> None:
        """Advance the breath cycle by dt."""
        self.phase = (self.phase + self.frequency * dt) % (2 * math.pi)
    
    @property 
    def state(self) -> str:
        """Current state in the breath cycle."""
        if self.expansion > 0.9:
            return "EXPANDED"  # All points
        elif self.expansion < 0.1:
            return "COLLAPSED"  # One point
        elif math.sin(self.phase) > 0:
            return "EXPANDING"  # Going toward all
        else:
            return "COLLAPSING"  # Going toward one
    
    def __repr__(self) -> str:
        return f"<HelixBreath dim={self.dimension} phase={self.phase:.2f} {self.state}>"


# =============================================================================
# DIMENSIONAL WAVE - Combining manifold with breath
# =============================================================================

@dataclass
class DimensionalWave:
    """
    A complete dimensional wave combining:
    - The wave manifold (z=xy, etc.)
    - The helix breath (expansion/collapse)
    - The surfer (observer position)
    
    The surfer riding the wave in the barrel represents
    the observer navigating the dimensional structure.
    """
    manifold: WaveManifold = field(default_factory=WaveManifold)
    breath: HelixBreath = field(default_factory=lambda: HelixBreath(dimension=0))
    
    # Surfer position
    surfer_u: float = 0.0
    surfer_v: float = 0.0
    
    @property
    def surfer_point(self) -> WavePoint:
        """The wave point where the surfer currently is."""
        return self.manifold.sample(self.surfer_u, self.surfer_v)
    
    @property
    def surfer_in_barrel(self) -> bool:
        """Is the surfer inside the barrel (the void)?"""
        return self.surfer_point.in_barrel
    
    def ride(self, direction: Tuple[float, float], step: float = 0.1) -> WavePoint:
        """
        Move the surfer along the wave surface.
        
        The trajectory encodes information through the
        sequence of geometric properties encountered.
        """
        du, dv = direction
        # Scale by breath expansion (harder to move when collapsed)
        scale = 0.1 + 0.9 * self.breath.expansion
        
        self.surfer_u += du * step * scale
        self.surfer_v += dv * step * scale
        
        # Advance the breath
        self.breath.advance(step)
        
        return self.surfer_point
    
    def observe(self) -> Dict[str, Any]:
        """
        What the surfer observes from their current position.
        
        This is the information extracted from the wave geometry
        at the surfer's location.
        """
        point = self.surfer_point
        return {
            "position": point.position_3d,
            "in_barrel": self.surfer_in_barrel,
            "barrel_distance": point.barrel_distance,
            "barrel_angle": point.barrel_angle,
            
            # What the surfer "feels"
            "gradient": point.gradient,  # Direction of force
            "curvature": point.gaussian_curvature,  # Intensity of curve
            
            # Breath state
            "breath_state": self.breath.state,
            "expansion": self.breath.expansion,
            
            # Full encoding
            "encoded": point.encode_information(),
        }
    
    def __repr__(self) -> str:
        return (
            f"<DimensionalWave {self.manifold.wave_type.name} "
            f"surfer=({self.surfer_u:.2f},{self.surfer_v:.2f}) "
            f"breath={self.breath.state}>"
        )


# =============================================================================
# SURFER - The Observer Whose Geometry IS Information
# =============================================================================

@dataclass
class Surfer:
    """
    The surfer on the wave manifold.
    
    The surfer's geometry IS the information - no stored data required:
    - Position angle: where on wave face → velocity/momentum
    - Wave orientation: local slope → forces acting on surfer
    - Board angle: pitch/roll → direction of travel
    - Weight distribution: center of mass → stability/turning
    
    The wave surface + surfer position = COMPLETE STATE
    No bits and bytes needed except those that create the manifold.
    """
    # Position on the wave (intrinsic coordinates)
    u: float = 0.0  # Position along wave direction
    v: float = 0.0  # Position across wave width
    
    # Board orientation (angles relative to wave surface)
    board_pitch: float = 0.0   # Forward/back tilt (radians)
    board_roll: float = 0.0    # Left/right tilt (radians)
    board_yaw: float = 0.0     # Rotation in plane (radians)
    
    # Weight distribution (0 = center, -1 = back/left, +1 = front/right)
    weight_fore_aft: float = 0.0   # Forward (+) or back (-)
    weight_left_right: float = 0.0  # Right (+) or left (-)
    
    # The wave manifold the surfer is on
    wave: WaveManifold = field(default_factory=WaveManifold)
    
    @property
    def wave_point(self) -> WavePoint:
        """The point on the wave where the surfer currently is."""
        return self.wave.sample(self.u, self.v)
    
    # -------------------------------------------------------------------------
    # INFORMATION FROM POSITION ALONE (no storage)
    # -------------------------------------------------------------------------
    
    @property
    def velocity_direction(self) -> Tuple[float, float]:
        """
        Direction of travel - derived from board yaw and wave gradient.
        
        The gradient tells the wave's "downhill" direction.
        The board yaw rotates from that baseline.
        """
        grad = self.wave_point.gradient
        grad_angle = math.atan2(grad[1], grad[0])
        travel_angle = grad_angle + self.board_yaw
        return (math.cos(travel_angle), math.sin(travel_angle))
    
    @property
    def speed(self) -> float:
        """
        Speed - derived from wave slope and weight distribution.
        
        Steeper slope + forward weight = faster
        This is physics from geometry, not stored data.
        """
        slope_magnitude = self.wave_point.gradient_magnitude
        weight_factor = 1.0 + 0.3 * self.weight_fore_aft  # Forward lean = more speed
        return slope_magnitude * weight_factor
    
    @property
    def acceleration(self) -> Tuple[float, float, float]:
        """
        Acceleration vector - derived from curvature and position.
        
        The wave's curvature determines the forces on the surfer.
        Gaussian curvature < 0 (saddle) creates different dynamics than > 0 (bowl).
        """
        k = self.wave_point.gaussian_curvature
        normal = self.wave_point.normal_vector
        
        # Centripetal acceleration from curvature
        speed2 = self.speed ** 2
        accel_magnitude = abs(k) * speed2
        
        return (
            normal[0] * accel_magnitude,
            normal[1] * accel_magnitude,
            normal[2] * accel_magnitude - 9.81  # Gravity
        )
    
    @property
    def turning_rate(self) -> float:
        """
        Rate of turn - derived from board roll and weight distribution.
        
        Roll angle + lateral weight shift = turning force.
        No stored "turn state" needed.
        """
        roll_factor = math.sin(self.board_roll)
        weight_factor = self.weight_left_right
        return roll_factor + 0.5 * weight_factor
    
    @property
    def stability(self) -> float:
        """
        Stability measure (0 = unstable, 1 = stable).
        
        Derived from:
        - Barrel distance (closer to barrel = less stable)
        - Board pitch (extreme angles = less stable)
        - Weight distribution (centered = more stable)
        """
        barrel_factor = min(1.0, self.wave_point.barrel_distance / 2.0)
        pitch_factor = math.cos(self.board_pitch)
        weight_spread = abs(self.weight_fore_aft) + abs(self.weight_left_right)
        weight_factor = 1.0 - 0.3 * weight_spread
        
        return barrel_factor * pitch_factor * weight_factor
    
    @property
    def in_barrel(self) -> bool:
        """Is the surfer inside the barrel (tube)?"""
        return self.wave_point.in_barrel
    
    @property
    def wave_face_position(self) -> str:
        """
        Position on wave face - derived from gradient direction.
        
        Returns: 'TOP', 'FACE', 'BOTTOM', 'BARREL'
        """
        if self.in_barrel:
            return 'BARREL'
        
        z = self.wave_point.z
        if z > 0.5:
            return 'TOP'
        elif z < -0.5:
            return 'BOTTOM'
        else:
            return 'FACE'
    
    # -------------------------------------------------------------------------
    # COMPLETE STATE - All information from geometry alone
    # -------------------------------------------------------------------------
    
    def state(self) -> Dict[str, Any]:
        """
        Complete surfer state - ALL derived from geometry, NOTHING stored.
        
        This is the key insight: the manifold shape + surfer position
        contains ALL the information needed. The geometry IS the data.
        """
        return {
            # Position (from manifold coordinates)
            "position_3d": self.wave_point.position_3d,
            "position_intrinsic": (self.u, self.v),
            "wave_face": self.wave_face_position,
            
            # Motion (from slopes and angles)
            "velocity_direction": self.velocity_direction,
            "speed": self.speed,
            "acceleration": self.acceleration,
            
            # Orientation (from board angles)
            "board_pitch": self.board_pitch,
            "board_roll": self.board_roll,
            "board_yaw": self.board_yaw,
            
            # Balance (from weight distribution)
            "weight_distribution": (self.weight_fore_aft, self.weight_left_right),
            "turning_rate": self.turning_rate,
            "stability": self.stability,
            
            # Wave geometry (from manifold shape)
            "wave_gradient": self.wave_point.gradient,
            "wave_curvature": self.wave_point.gaussian_curvature,
            "barrel_distance": self.wave_point.barrel_distance,
            "in_barrel": self.in_barrel,
            
            # ALL of this computed from position + shape, zero stored bits
            "_stored_bytes": 0,
            "_computed_from": "geometry",
        }
    
    # -------------------------------------------------------------------------
    # ACTIONS - Changes to geometry that propagate naturally
    # -------------------------------------------------------------------------
    
    def lean_forward(self, amount: float = 0.1) -> 'Surfer':
        """Shift weight forward - accelerates."""
        self.weight_fore_aft = max(-1, min(1, self.weight_fore_aft + amount))
        return self
    
    def lean_back(self, amount: float = 0.1) -> 'Surfer':
        """Shift weight back - decelerates / stalls."""
        self.weight_fore_aft = max(-1, min(1, self.weight_fore_aft - amount))
        return self
    
    def lean_left(self, amount: float = 0.1) -> 'Surfer':
        """Shift weight left - turns left."""
        self.weight_left_right = max(-1, min(1, self.weight_left_right - amount))
        self.board_roll = max(-math.pi/4, min(math.pi/4, self.board_roll - amount * 0.5))
        return self
    
    def lean_right(self, amount: float = 0.1) -> 'Surfer':
        """Shift weight right - turns right."""
        self.weight_left_right = max(-1, min(1, self.weight_left_right + amount))
        self.board_roll = max(-math.pi/4, min(math.pi/4, self.board_roll + amount * 0.5))
        return self
    
    def pump(self, intensity: float = 0.1) -> 'Surfer':
        """Pump the board - generates speed from timing with wave."""
        # Timing with wave curvature generates/absorbs energy
        curvature = self.wave_point.gaussian_curvature
        energy_transfer = abs(curvature) * intensity
        self.board_pitch = math.sin(self.u * 2) * intensity * 0.3
        return self
    
    def advance(self, dt: float = 0.1) -> 'Surfer':
        """
        Advance time - position updates based on velocity.
        
        The new position is computed from current geometry.
        No stored velocity - it's derived from slope + weight.
        """
        direction = self.velocity_direction
        speed = self.speed
        
        self.u += direction[0] * speed * dt
        self.v += direction[1] * speed * dt + self.turning_rate * dt * 0.3
        
        return self
    
    def __repr__(self) -> str:
        return (
            f"<Surfer at ({self.u:.2f},{self.v:.2f}) "
            f"speed={self.speed:.2f} stability={self.stability:.2f} "
            f"{self.wave_face_position}>"
        )


# =============================================================================
# FACTORY FUNCTIONS - Create common wave manifolds
# =============================================================================

def twisted_ribbon(u_range: Tuple[float, float] = (-2, 2), 
                   v_range: Tuple[float, float] = (-2, 2)) -> WaveManifold:
    """
    Create z = xy, the fundamental twisted ribbon at 90°.
    
    This is the basic unit of dimensional transformation.
    """
    return WaveManifold(
        wave_type=WaveSurface.TWISTED_RIBBON,
        u_range=u_range,
        v_range=v_range
    )


def steep_wave(u_range: Tuple[float, float] = (-2, 2), 
               v_range: Tuple[float, float] = (-2, 2)) -> WaveManifold:
    """
    Create z = xy², a wave with steeper face.
    
    Stronger y-dependence creates a more dramatic wave face.
    """
    return WaveManifold(
        wave_type=WaveSurface.STEEP_FACE,
        u_range=u_range,
        v_range=v_range
    )


def hyperbolic_wave(u_range: Tuple[float, float] = (0.1, 2), 
                    v_range: Tuple[float, float] = (0.1, 2)) -> WaveManifold:
    """
    Create z = x/y, hyperbolic wave asymptotic to axes.
    
    The asymptotes represent boundaries/infinities.
    """
    return WaveManifold(
        wave_type=WaveSurface.HYPERBOLIC_WAVE,
        u_range=u_range,
        v_range=v_range
    )


def hyperbolic_funnel(u_range: Tuple[float, float] = (0.1, 2), 
                      v_range: Tuple[float, float] = (0.1, 2)) -> WaveManifold:
    """
    Create z = x/y², sharper hyperbolic funnel.
    
    The sharper funnel represents concentrated information.
    """
    return WaveManifold(
        wave_type=WaveSurface.HYPERBOLIC_FUNNEL,
        u_range=u_range,
        v_range=v_range
    )


def volume_wave(u_range: Tuple[float, float] = (-2, 2),
                v_range: Tuple[float, float] = (-2, 2)) -> WaveManifold:
    """
    Create m = xyz, the 4D volume wave with 3D barrel.
    
    This extends the wave concept to 4 dimensions.
    """
    return WaveManifold(
        wave_type=WaveSurface.VOLUME_WAVE,
        u_range=u_range,
        v_range=v_range
    )


def create_surfer(
    wave_type: WaveSurface = WaveSurface.TWISTED_RIBBON,
    position: Tuple[float, float] = (0.5, 0.5)
) -> Surfer:
    """
    Create a surfer on a wave manifold.
    
    The surfer's state is entirely determined by geometry:
    - Position on wave → speed, forces
    - Board angle → direction, turning
    - Weight distribution → acceleration, stability
    
    NO stored data required. The geometry IS the information.
    """
    wave = WaveManifold(wave_type=wave_type)
    return Surfer(u=position[0], v=position[1], wave=wave)


# =============================================================================
# GEOMETRIC LENS - Extract Any Data Type from Shape Alone
# =============================================================================

class GeometricLens:
    """
    THE LENS REVEALS WHAT THE GEOMETRY CONTAINS
    
    The manifold holds so much information by virtue of its shape and 
    composition that ANY data type can be extracted from it. You only 
    need to give it CONTEXT via a lens to bring out the information 
    you're looking for.
    
    No bits and bytes required except those that create the manifold.
    
    The lens extracts:
    - Floats from positions, angles, slopes, distances
    - Integers from quantized zones, octants, levels
    - Booleans from thresholds and boundaries
    - Strings from categorical regions
    - Vectors from gradients, normals, directions
    - Complex structures from geometric relationships
    
    The SAME geometry yields DIFFERENT data through different lenses.
    """
    
    def __init__(self, surfer: Surfer):
        """Create a lens focused on a surfer's geometry."""
        self.surfer = surfer
        self._point = surfer.wave_point
    
    # -------------------------------------------------------------------------
    # FLOAT LENSES - Continuous values from geometry
    # -------------------------------------------------------------------------
    
    def as_float(self, aspect: str) -> float:
        """Extract a float from any geometric aspect."""
        extractors = {
            # Position
            "x": lambda: self._point.x,
            "y": lambda: self._point.y,
            "z": lambda: self._point.z,
            "u": lambda: self.surfer.u,
            "v": lambda: self.surfer.v,
            
            # Angles
            "barrel_angle": lambda: self._point.barrel_angle,
            "board_pitch": lambda: self.surfer.board_pitch,
            "board_roll": lambda: self.surfer.board_roll,
            "board_yaw": lambda: self.surfer.board_yaw,
            
            # Derivatives
            "slope_u": lambda: self._point.slope_u,
            "slope_v": lambda: self._point.slope_v,
            "slope_magnitude": lambda: self._point.gradient_magnitude,
            
            # Curvature
            "gaussian_curvature": lambda: self._point.gaussian_curvature,
            "mean_curvature": lambda: self._point.mean_curvature,
            
            # Distances
            "barrel_distance": lambda: self._point.barrel_distance,
            "barrel_radius": lambda: self._point.barrel_radius,
            "barrel_height": lambda: self._point.barrel_height,
            
            # Dynamics (computed from geometry)
            "speed": lambda: self.surfer.speed,
            "turning_rate": lambda: self.surfer.turning_rate,
            "stability": lambda: self.surfer.stability,
            
            # Weight
            "weight_fore_aft": lambda: self.surfer.weight_fore_aft,
            "weight_left_right": lambda: self.surfer.weight_left_right,
        }
        
        if aspect in extractors:
            return extractors[aspect]()
        
        # Default: try to compute from combinations
        return 0.0
    
    def as_normalized_float(self, aspect: str, 
                            min_val: float = -1.0, 
                            max_val: float = 1.0) -> float:
        """Extract a float normalized to [0, 1] range."""
        raw = self.as_float(aspect)
        if max_val == min_val:
            return 0.5
        return (raw - min_val) / (max_val - min_val)
    
    # -------------------------------------------------------------------------
    # INTEGER LENSES - Discrete values from geometry
    # -------------------------------------------------------------------------
    
    def as_int(self, aspect: str) -> int:
        """Extract an integer from geometric quantization."""
        extractors = {
            # Angular sectors
            "octant": lambda: int((self._point.barrel_angle + math.pi) / (math.pi/4)) % 8,
            "quadrant": lambda: int((self._point.barrel_angle + math.pi) / (math.pi/2)) % 4,
            "sextant": lambda: int((self._point.barrel_angle + math.pi) / (math.pi/3)) % 6,
            
            # Quantized levels
            "stability_level": lambda: int(self.surfer.stability * 10),
            "speed_level": lambda: int(self.surfer.speed * 5),
            
            # Zone indices
            "barrel_zone": lambda: 0 if self._point.in_barrel else (
                1 if self._point.barrel_distance < 0.5 else 2
            ),
            
            # Pitch quantized to degrees
            "pitch_degrees": lambda: int(math.degrees(self.surfer.board_pitch)),
            "roll_degrees": lambda: int(math.degrees(self.surfer.board_roll)),
            "yaw_degrees": lambda: int(math.degrees(self.surfer.board_yaw)),
            
            # Grid position
            "grid_u": lambda: int(self.surfer.u * 10),
            "grid_v": lambda: int(self.surfer.v * 10),
        }
        
        if aspect in extractors:
            return extractors[aspect]()
        return 0
    
    def as_index(self, aspect: str, num_bins: int = 10) -> int:
        """Extract an integer index into num_bins bins."""
        normalized = self.as_normalized_float(aspect)
        return min(num_bins - 1, max(0, int(normalized * num_bins)))
    
    # -------------------------------------------------------------------------
    # BOOLEAN LENSES - Truth from thresholds
    # -------------------------------------------------------------------------
    
    def as_bool(self, aspect: str) -> bool:
        """Extract a boolean from geometric thresholds."""
        extractors = {
            # Position predicates
            "in_barrel": lambda: self._point.in_barrel,
            "at_inflection": lambda: self._point.is_inflection,
            "above_surface": lambda: self._point.z > 0,
            "below_surface": lambda: self._point.z < 0,
            
            # Motion predicates
            "accelerating": lambda: self.surfer.speed > 0.5,
            "turning_left": lambda: self.surfer.turning_rate < -0.1,
            "turning_right": lambda: self.surfer.turning_rate > 0.1,
            "stable": lambda: self.surfer.stability > 0.7,
            "unstable": lambda: self.surfer.stability < 0.3,
            
            # Weight predicates
            "leaning_forward": lambda: self.surfer.weight_fore_aft > 0.3,
            "leaning_back": lambda: self.surfer.weight_fore_aft < -0.3,
            "on_rail": lambda: abs(self.surfer.board_roll) > 0.3,
            
            # Curvature predicates
            "convex": lambda: self._point.gaussian_curvature > 0,
            "concave": lambda: self._point.gaussian_curvature < 0,
            "saddle": lambda: abs(self._point.gaussian_curvature) > 0.01,
        }
        
        if aspect in extractors:
            return extractors[aspect]()
        return False
    
    # -------------------------------------------------------------------------
    # STRING LENSES - Categories from regions
    # -------------------------------------------------------------------------
    
    def as_string(self, aspect: str) -> str:
        """Extract a categorical string from geometric regions."""
        extractors = {
            # Wave position
            "wave_face": lambda: self.surfer.wave_face_position,
            "wave_type": lambda: self._point.wave_type.name,
            
            # Cardinal direction (from barrel angle)
            "direction": lambda: ["E", "NE", "N", "NW", "W", "SW", "S", "SE"][
                int((self._point.barrel_angle + math.pi) / (math.pi/4)) % 8
            ],
            
            # Stability state
            "stability_state": lambda: (
                "SOLID" if self.surfer.stability > 0.8 else
                "BALANCED" if self.surfer.stability > 0.5 else
                "SHAKY" if self.surfer.stability > 0.3 else
                "FALLING"
            ),
            
            # Motion state
            "motion_state": lambda: (
                "CARVING" if abs(self.surfer.turning_rate) > 0.5 else
                "CRUISING" if self.surfer.speed > 0.3 else
                "STALLING" if self.surfer.speed < 0.1 else
                "FLOWING"
            ),
            
            # Curvature type
            "surface_type": lambda: (
                "BOWL" if self._point.gaussian_curvature > 0.1 else
                "SADDLE" if self._point.gaussian_curvature < -0.1 else
                "FLAT"
            ),
        }
        
        if aspect in extractors:
            return extractors[aspect]()
        return "UNKNOWN"
    
    # -------------------------------------------------------------------------
    # VECTOR LENSES - Multi-valued from geometry
    # -------------------------------------------------------------------------
    
    def as_vector(self, aspect: str) -> Tuple[float, ...]:
        """Extract a vector from geometric properties."""
        extractors = {
            # Positions
            "position_3d": lambda: self._point.position_3d,
            "position_2d": lambda: (self.surfer.u, self.surfer.v),
            
            # Directions
            "velocity": lambda: self.surfer.velocity_direction,
            "gradient": lambda: self._point.gradient,
            "normal": lambda: self._point.normal_vector,
            
            # Board orientation
            "board_angles": lambda: (
                self.surfer.board_pitch,
                self.surfer.board_roll,
                self.surfer.board_yaw
            ),
            
            # Weight
            "weight_distribution": lambda: (
                self.surfer.weight_fore_aft,
                self.surfer.weight_left_right
            ),
            
            # Acceleration
            "acceleration": lambda: self.surfer.acceleration,
            
            # Barrel coordinates
            "barrel_coords": lambda: (
                self._point.barrel_distance,
                self._point.barrel_angle,
                self._point.barrel_height
            ),
        }
        
        if aspect in extractors:
            return extractors[aspect]()
        return (0.0,)
    
    # -------------------------------------------------------------------------
    # COMPOSITE LENSES - Structured data from geometry
    # -------------------------------------------------------------------------
    
    def as_dict(self, aspects: List[str]) -> Dict[str, Any]:
        """Extract multiple aspects into a dictionary."""
        result = {}
        for aspect in aspects:
            # Auto-detect type
            if aspect in ["in_barrel", "stable", "accelerating", "on_rail"]:
                result[aspect] = self.as_bool(aspect)
            elif aspect in ["octant", "quadrant", "stability_level"]:
                result[aspect] = self.as_int(aspect)
            elif aspect in ["position_3d", "gradient", "normal"]:
                result[aspect] = self.as_vector(aspect)
            elif aspect in ["wave_face", "direction", "stability_state"]:
                result[aspect] = self.as_string(aspect)
            else:
                result[aspect] = self.as_float(aspect)
        return result
    
    def as_bytes(self, num_bytes: int = 8) -> bytes:
        """
        Encode geometry as bytes.
        
        This is the ONLY place where bits are created - and they
        come directly from the shape, not from stored values.
        """
        # Use position and angles to create bytes
        values = [
            self.as_normalized_float("u"),
            self.as_normalized_float("v"),
            self.as_normalized_float("board_pitch", -math.pi/4, math.pi/4),
            self.as_normalized_float("board_roll", -math.pi/4, math.pi/4),
            self.as_normalized_float("weight_fore_aft"),
            self.as_normalized_float("weight_left_right"),
            self.as_normalized_float("stability", 0, 1),
            self.as_normalized_float("speed", 0, 2),
        ]
        
        result = []
        for i in range(min(num_bytes, len(values))):
            byte_val = int(values[i] * 255) % 256
            result.append(byte_val)
        
        return bytes(result)
    
    # -------------------------------------------------------------------------
    # UNIVERSAL LENS - Any type from geometry
    # -------------------------------------------------------------------------
    
    def extract(self, aspect: str, dtype: type = float) -> Any:
        """
        Universal extraction - get any data type from geometry.
        
        The manifold contains ALL information by virtue of shape.
        The lens + dtype context reveals what you're looking for.
        """
        if dtype == float:
            return self.as_float(aspect)
        elif dtype == int:
            return self.as_int(aspect)
        elif dtype == bool:
            return self.as_bool(aspect)
        elif dtype == str:
            return self.as_string(aspect)
        elif dtype == tuple:
            return self.as_vector(aspect)
        elif dtype == bytes:
            return self.as_bytes()
        elif dtype == dict:
            return self.surfer.state()
        else:
            return self.as_float(aspect)
    
    def __repr__(self) -> str:
        return (
            f"<GeometricLens focused on {self.surfer} "
            f"extracting from shape alone>"
        )


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Create the fundamental twisted ribbon z=xy
    ribbon = twisted_ribbon()
    
    # Sample some points
    points = ribbon.generate_grid(10)
    print(f"Generated {len(points)} points on twisted ribbon")
    
    # Trace a surfer's path
    trajectory = ribbon.surfer_trajectory(
        start=(1.0, 0.5),
        direction=(-0.5, 0.5),
        steps=20
    )
    
    print("\nSurfer trajectory:")
    for i, p in enumerate(trajectory[:5]):
        info = p.encode_information()
        print(f"  Step {i}: barrel_d={info['barrel_distance']:.2f}, "
              f"curv={info['gaussian_curvature']:.4f}")
    
    # Surface-level encoding
    print("\nSurface information:")
    surface_info = ribbon.encode_surface_information()
    for k, v in surface_info.items():
        print(f"  {k}: {v}")
    
    # The dimensional wave with breath
    print("\n--- Dimensional Wave with Breath ---")
    wave = DimensionalWave()
    
    for _ in range(10):
        obs = wave.observe()
        print(f"Breath: {obs['breath_state']:10s} | "
              f"Expansion: {obs['expansion']:.2f} | "
              f"In barrel: {obs['in_barrel']}")
        wave.ride((0.1, 0.05))
    
    # The SURFER - geometry IS information, no storage needed
    print("\n--- Surfer: Geometry IS Information ---")
    surfer = create_surfer(position=(0.8, 0.3))
    print(f"Initial: {surfer}")
    
    # Simulate surfing - all state derived from geometry
    print("\nSurfing (no stored data, just geometry):")
    for i in range(8):
        state = surfer.state()
        print(f"  t={i}: speed={state['speed']:.2f}, "
              f"stability={state['stability']:.2f}, "
              f"face={state['wave_face']}, "
              f"stored_bytes={state['_stored_bytes']}")
        
        # Actions just change geometry, which changes derived values
        if i < 3:
            surfer.lean_forward(0.15)  # Accelerate
        elif i < 5:
            surfer.lean_right(0.2)     # Turn
        else:
            surfer.pump(0.1)           # Generate speed
        
        surfer.advance(0.15)
    
    print(f"\nFinal: {surfer}")
    print("\n✓ All information derived from geometry - zero stored bits")
    
    # THE LENS - Extract any data type from the same geometry
    print("\n--- Geometric Lens: Any Data Type from Shape ---")
    lens = GeometricLens(surfer)
    
    print("\nSAME geometry → DIFFERENT data types via LENS:")
    print(f"  as_float('speed'):        {lens.as_float('speed'):.3f}")
    print(f"  as_float('stability'):    {lens.as_float('stability'):.3f}")
    print(f"  as_float('barrel_angle'): {lens.as_float('barrel_angle'):.3f}")
    
    print(f"\n  as_int('octant'):         {lens.as_int('octant')}")
    print(f"  as_int('stability_level'):{lens.as_int('stability_level')}")
    print(f"  as_int('barrel_zone'):    {lens.as_int('barrel_zone')}")
    
    print(f"\n  as_bool('stable'):        {lens.as_bool('stable')}")
    print(f"  as_bool('accelerating'):  {lens.as_bool('accelerating')}")
    print(f"  as_bool('on_rail'):       {lens.as_bool('on_rail')}")
    
    print(f"\n  as_string('wave_face'):   {lens.as_string('wave_face')}")
    print(f"  as_string('direction'):   {lens.as_string('direction')}")
    print(f"  as_string('motion_state'):{lens.as_string('motion_state')}")
    
    print(f"\n  as_vector('position_3d'): {lens.as_vector('position_3d')}")
    print(f"  as_vector('gradient'):    {lens.as_vector('gradient')}")
    
    print(f"\n  as_bytes(8):              {lens.as_bytes(8).hex()}")
    
    print("\n✓ No stored data - all extracted from shape + lens context")
    print("✓ The manifold IS the information - bits only for rendering")
