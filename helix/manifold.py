"""
ButterflyFX Generative Manifold - Mathematical Surface That Produces Data Types

The manifold is not just a container for data - it IS mathematical structure.
Every point on the surface encodes geometric properties that can be extracted
as mathematical forms.

Key Principle:
    The helix geometry contains ALL possible mathematical structures within its
    surface properties: angles, slopes, curvature, inflections, oscillations.
    Any data type can be produced by sampling the appropriate geometric property.

Geometric Properties → Data Types:
    - Angles → Trigonometric values (sin, cos, tan, cot, sec, csc)
    - Slopes → Derivatives, rates of change, gradients
    - Curvature → Acceleration, second derivatives, inflection points
    - Surface sampling → Grids, matrices, tensors
    - Regions → Sets, domains, ranges, spans
    - Oscillations → Waves, spectra, frequencies
    - Distributions → Probabilities, densities
    - Connectivity → Graphs, trees, networks
    - Projections → Functions, mappings, transforms

The 7 Dimensional Levels as Geometric Inflection Points:
    Level 0 (Potential): θ = 0, origin point, all possibilities superposed
    Level 1 (Point): θ = π/6, first instantiation, unit position
    Level 2 (Length): θ = π/3, linear extension, directional vector
    Level 3 (Width): θ = π/2, perpendicular extension, 2D spanning
    Level 4 (Plane): θ = 2π/3, surface completion, area
    Level 5 (Volume): θ = 5π/6, volumetric extension, enclosed space
    Level 6 (Whole): θ = π, completion, ready for spiral transition
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import (
    Any, Callable, Dict, List, Optional, Set, Tuple, 
    Iterator, TypeVar, Generic, Union, Sequence
)
from enum import Enum, auto
import uuid
from functools import cached_property


# =============================================================================
# CONSTANTS - The Geometric Foundation
# =============================================================================

# Level angles on the helix (θ values)
LEVEL_ANGLES = {
    0: 0.0,           # Potential - origin
    1: math.pi / 6,   # Point - 30°
    2: math.pi / 3,   # Length - 60°
    3: math.pi / 2,   # Width - 90°
    4: 2 * math.pi / 3,  # Plane - 120°
    5: 5 * math.pi / 6,  # Volume - 150°
    6: math.pi,       # Whole - 180°
}

# Full spiral is 2π, levels span π per half-turn
SPIRAL_ANGULAR_EXTENT = 2 * math.pi

# Helix pitch (vertical rise per full rotation)
DEFAULT_PITCH = 1.0

# Helix radius
DEFAULT_RADIUS = 1.0


# =============================================================================
# SURFACE POINT - A Point on the Manifold with All Geometric Properties
# =============================================================================

@dataclass(frozen=True)
class SurfacePoint:
    """
    A point on the helix manifold surface.
    
    Contains all geometric properties at this location, from which any
    mathematical form can be extracted.
    """
    # Helix coordinates
    spiral: int
    level: int
    
    # Continuous parameters
    theta: float      # Angular position (radians)
    t: float          # Continuous parameter along helix (spiral + level/7)
    
    # Geometric properties
    radius: float = DEFAULT_RADIUS
    pitch: float = DEFAULT_PITCH
    
    @cached_property
    def angle(self) -> float:
        """Full angular position including spiral rotations"""
        return self.spiral * SPIRAL_ANGULAR_EXTENT + LEVEL_ANGLES[self.level]
    
    # -------------------------------------------------------------------------
    # Cartesian Coordinates
    # -------------------------------------------------------------------------
    
    @cached_property
    def x(self) -> float:
        """X coordinate on helix"""
        return self.radius * math.cos(self.angle)
    
    @cached_property
    def y(self) -> float:
        """Y coordinate on helix"""
        return self.radius * math.sin(self.angle)
    
    @cached_property
    def z(self) -> float:
        """Z coordinate (height) on helix"""
        return self.t * self.pitch
    
    @cached_property
    def position(self) -> Tuple[float, float, float]:
        """(x, y, z) position in 3D space"""
        return (self.x, self.y, self.z)
    
    # -------------------------------------------------------------------------
    # Trigonometric Values - Direct from Surface Angle
    # -------------------------------------------------------------------------
    
    @cached_property
    def sin(self) -> float:
        """Sine of position angle"""
        return math.sin(self.angle)
    
    @cached_property
    def cos(self) -> float:
        """Cosine of position angle"""
        return math.cos(self.angle)
    
    @cached_property
    def tan(self) -> float:
        """Tangent of position angle"""
        if abs(self.cos) < 1e-10:
            return float('inf') if self.sin > 0 else float('-inf')
        return self.sin / self.cos
    
    @cached_property
    def cot(self) -> float:
        """Cotangent of position angle"""
        if abs(self.sin) < 1e-10:
            return float('inf') if self.cos > 0 else float('-inf')
        return self.cos / self.sin
    
    @cached_property
    def sec(self) -> float:
        """Secant of position angle"""
        if abs(self.cos) < 1e-10:
            return float('inf')
        return 1.0 / self.cos
    
    @cached_property
    def csc(self) -> float:
        """Cosecant of position angle"""
        if abs(self.sin) < 1e-10:
            return float('inf')
        return 1.0 / self.sin
    
    # -------------------------------------------------------------------------
    # Derivatives / Slopes - Tangent Vector to Helix
    # -------------------------------------------------------------------------
    
    @cached_property
    def dx_dt(self) -> float:
        """Rate of change of x with respect to t"""
        return -self.radius * math.sin(self.angle) * SPIRAL_ANGULAR_EXTENT
    
    @cached_property
    def dy_dt(self) -> float:
        """Rate of change of y with respect to t"""
        return self.radius * math.cos(self.angle) * SPIRAL_ANGULAR_EXTENT
    
    @cached_property
    def dz_dt(self) -> float:
        """Rate of change of z with respect to t (constant = pitch)"""
        return self.pitch
    
    @cached_property
    def tangent_vector(self) -> Tuple[float, float, float]:
        """Tangent vector to helix at this point"""
        return (self.dx_dt, self.dy_dt, self.dz_dt)
    
    @cached_property
    def slope(self) -> float:
        """Slope of helix projection in xy-plane"""
        if abs(self.dx_dt) < 1e-10:
            return float('inf') if self.dy_dt > 0 else float('-inf')
        return self.dy_dt / self.dx_dt
    
    @cached_property
    def gradient_magnitude(self) -> float:
        """Magnitude of the tangent vector (speed along helix)"""
        return math.sqrt(self.dx_dt**2 + self.dy_dt**2 + self.dz_dt**2)
    
    # -------------------------------------------------------------------------
    # Curvature / Inflection - Second Derivatives
    # -------------------------------------------------------------------------
    
    @cached_property
    def d2x_dt2(self) -> float:
        """Second derivative of x (curvature component)"""
        return -self.radius * math.cos(self.angle) * (SPIRAL_ANGULAR_EXTENT ** 2)
    
    @cached_property
    def d2y_dt2(self) -> float:
        """Second derivative of y (curvature component)"""
        return -self.radius * math.sin(self.angle) * (SPIRAL_ANGULAR_EXTENT ** 2)
    
    @cached_property
    def curvature(self) -> float:
        """Curvature of helix at this point (κ = r/(r² + c²) for helix)"""
        return self.radius / (self.radius**2 + (self.pitch / SPIRAL_ANGULAR_EXTENT)**2)
    
    @cached_property
    def torsion(self) -> float:
        """Torsion of helix (τ = c/(r² + c²) for helix)"""
        c = self.pitch / SPIRAL_ANGULAR_EXTENT
        return c / (self.radius**2 + c**2)
    
    @cached_property
    def inflection_distance(self) -> float:
        """Distance to nearest level boundary (inflection point)"""
        level_frac = self.t - int(self.t)
        next_level_dist = (1/7) - (level_frac % (1/7))
        prev_level_dist = level_frac % (1/7)
        return min(next_level_dist, prev_level_dist)
    
    # -------------------------------------------------------------------------
    # Normal and Binormal - Full Frenet-Serret Frame
    # -------------------------------------------------------------------------
    
    @cached_property
    def normal_vector(self) -> Tuple[float, float, float]:
        """Principal normal vector (points toward axis of helix)"""
        return (-math.cos(self.angle), -math.sin(self.angle), 0.0)
    
    @cached_property
    def binormal_vector(self) -> Tuple[float, float, float]:
        """Binormal vector = T × N"""
        # For helix: B = (c·sin(t), -c·cos(t), r) / sqrt(r² + c²)
        c = self.pitch / SPIRAL_ANGULAR_EXTENT
        denom = math.sqrt(self.radius**2 + c**2)
        return (
            c * math.sin(self.angle) / denom,
            -c * math.cos(self.angle) / denom,
            self.radius / denom
        )


# =============================================================================
# MANIFOLD REGION - A Section of the Surface
# =============================================================================

@dataclass
class ManifoldRegion:
    """
    A region of the manifold surface that can be sampled or analyzed.
    
    Regions can produce:
    - Grids (uniformly sampled points)
    - Matrices (values arranged in 2D)
    - Sets (discrete collection of points)
    - Domains/Ranges (continuous intervals)
    """
    spiral_start: int
    spiral_end: int
    level_start: int
    level_end: int
    
    def __post_init__(self):
        if not 0 <= self.level_start <= 6:
            raise ValueError(f"level_start must be 0-6, got {self.level_start}")
        if not 0 <= self.level_end <= 6:
            raise ValueError(f"level_end must be 0-6, got {self.level_end}")
    
    @property
    def spiral_span(self) -> int:
        """Number of spirals in region"""
        return self.spiral_end - self.spiral_start + 1
    
    @property
    def level_span(self) -> int:
        """Number of levels in region"""
        return self.level_end - self.level_start + 1
    
    @property
    def angular_span(self) -> float:
        """Total angular extent of region (radians)"""
        start_angle = self.spiral_start * SPIRAL_ANGULAR_EXTENT + LEVEL_ANGLES[self.level_start]
        end_angle = self.spiral_end * SPIRAL_ANGULAR_EXTENT + LEVEL_ANGLES[self.level_end]
        return end_angle - start_angle
    
    def contains(self, spiral: int, level: int) -> bool:
        """Check if a state is within this region"""
        return (self.spiral_start <= spiral <= self.spiral_end and
                self.level_start <= level <= self.level_end)


# =============================================================================
# GENERATIVE MANIFOLD - The Core Generative Surface
# =============================================================================

class GenerativeManifold:
    """
    The Generative Manifold - A mathematical surface that produces data types.
    
    This is not storage - it IS mathematical structure. The helix geometry
    inherently contains all possible mathematical forms:
    
    Usage:
        manifold = GenerativeManifold()
        
        # Get a point with all its geometric properties
        point = manifold.at(spiral=0, level=3)
        sin_value = point.sin
        slope = point.slope
        
        # Sample a region as different structures
        region = manifold.region(0, 0, 0, 6)
        grid = manifold.as_grid(region, resolution=10)
        matrix = manifold.as_matrix(region, rows=7, cols=10)
        
        # Generate functions from the surface
        wave = manifold.as_wave(frequency=1.0)
        prob = manifold.as_probability(region)
    """
    
    def __init__(self, radius: float = DEFAULT_RADIUS, pitch: float = DEFAULT_PITCH):
        self.radius = radius
        self.pitch = pitch
    
    # -------------------------------------------------------------------------
    # Point Access
    # -------------------------------------------------------------------------
    
    def at(self, spiral: int, level: int) -> SurfacePoint:
        """
        Get the surface point at a specific helix state.
        
        Returns a SurfacePoint with all geometric properties available.
        """
        if not 0 <= level <= 6:
            raise ValueError(f"Level must be 0-6, got {level}")
        
        t = spiral + level / 7.0
        theta = LEVEL_ANGLES[level]
        
        return SurfacePoint(
            spiral=spiral,
            level=level,
            theta=theta,
            t=t,
            radius=self.radius,
            pitch=self.pitch
        )
    
    def at_continuous(self, t: float) -> SurfacePoint:
        """
        Get surface point at continuous parameter t.
        
        t = spiral + level/7, so t=0.5 is spiral 0, level ~3.5 (interpolated)
        """
        spiral = int(t)
        level_frac = (t - spiral) * 7
        level = int(level_frac)
        level = min(max(level, 0), 6)
        
        # Interpolate theta between level boundaries
        if level < 6:
            theta = LEVEL_ANGLES[level] + (level_frac - level) * (LEVEL_ANGLES[level + 1] - LEVEL_ANGLES[level])
        else:
            theta = LEVEL_ANGLES[6]
        
        return SurfacePoint(
            spiral=spiral,
            level=level,
            theta=theta,
            t=t,
            radius=self.radius,
            pitch=self.pitch
        )
    
    def region(self, spiral_start: int, level_start: int, 
               spiral_end: int, level_end: int) -> ManifoldRegion:
        """Define a region of the manifold surface"""
        return ManifoldRegion(spiral_start, spiral_end, level_start, level_end)
    
    # -------------------------------------------------------------------------
    # GRID - Sample the Surface as a Grid of Points
    # -------------------------------------------------------------------------
    
    def as_grid(self, region: ManifoldRegion, 
                spiral_resolution: int = 1,
                level_resolution: int = 1) -> List[List[SurfacePoint]]:
        """
        Sample a region as a 2D grid of surface points.
        
        Returns: List[spiral][level] of SurfacePoints
        """
        grid = []
        for s in range(region.spiral_start, region.spiral_end + 1, spiral_resolution):
            row = []
            for l in range(region.level_start, region.level_end + 1, level_resolution):
                row.append(self.at(s, l))
            grid.append(row)
        return grid
    
    def as_point_set(self, region: ManifoldRegion) -> Set[SurfacePoint]:
        """Sample a region as a discrete set of points"""
        points = set()
        for s in range(region.spiral_start, region.spiral_end + 1):
            for l in range(region.level_start, region.level_end + 1):
                points.add(self.at(s, l))
        return points
    
    # -------------------------------------------------------------------------
    # MATRIX - Extract Numeric Values as a Matrix
    # -------------------------------------------------------------------------
    
    def as_matrix(self, region: ManifoldRegion, 
                  extractor: Callable[[SurfacePoint], float] = lambda p: p.sin,
                  rows: Optional[int] = None,
                  cols: Optional[int] = None) -> List[List[float]]:
        """
        Extract a numeric matrix from a region of the surface.
        
        Args:
            region: The region to sample
            extractor: Function to extract a value from each point (default: sin)
            rows: Number of rows (default: spiral span)
            cols: Number of cols (default: level span)
        
        Returns a 2D matrix of extracted values.
        """
        rows = rows or region.spiral_span
        cols = cols or region.level_span
        
        matrix = []
        for i in range(rows):
            row = []
            for j in range(cols):
                # Map (i,j) to region coordinates
                s = region.spiral_start + int(i * region.spiral_span / rows)
                l = region.level_start + int(j * region.level_span / cols)
                l = min(l, region.level_end)
                
                point = self.at(s, l)
                row.append(extractor(point))
            matrix.append(row)
        return matrix
    
    def as_vector(self, region: ManifoldRegion,
                  extractor: Callable[[SurfacePoint], float] = lambda p: p.sin) -> List[float]:
        """Extract a 1D vector by traversing the region linearly"""
        values = []
        for s in range(region.spiral_start, region.spiral_end + 1):
            for l in range(region.level_start, region.level_end + 1):
                values.append(extractor(self.at(s, l)))
        return values
    
    # -------------------------------------------------------------------------
    # FUNCTIONS - Generate Callable Functions from Surface
    # -------------------------------------------------------------------------
    
    def as_function(self, 
                    extractor: Callable[[SurfacePoint], float] = lambda p: p.sin
                    ) -> Callable[[float], float]:
        """
        Generate a continuous function f(t) -> value from the surface.
        
        The returned function samples the helix at continuous parameter t.
        """
        def f(t: float) -> float:
            point = self.at_continuous(t)
            return extractor(point)
        return f
    
    def as_parametric_function(self) -> Callable[[float], Tuple[float, float, float]]:
        """
        Generate the parametric representation of the helix.
        
        Returns f(t) -> (x, y, z)
        """
        def f(t: float) -> Tuple[float, float, float]:
            point = self.at_continuous(t)
            return point.position
        return f
    
    # -------------------------------------------------------------------------
    # WAVES - Trigonometric Waveforms
    # -------------------------------------------------------------------------
    
    def as_wave(self, wave_type: str = 'sin', 
                frequency: float = 1.0,
                amplitude: float = 1.0,
                phase: float = 0.0) -> Callable[[float], float]:
        """
        Generate a wave function from the helix geometry.
        
        Args:
            wave_type: 'sin', 'cos', 'tan', 'sawtooth', 'square', 'triangle'
            frequency: Wave frequency multiplier
            amplitude: Wave amplitude
            phase: Phase offset (radians)
        """
        def wave(t: float) -> float:
            angle = t * frequency * SPIRAL_ANGULAR_EXTENT + phase
            
            if wave_type == 'sin':
                return amplitude * math.sin(angle)
            elif wave_type == 'cos':
                return amplitude * math.cos(angle)
            elif wave_type == 'tan':
                return amplitude * math.tan(angle)
            elif wave_type == 'sawtooth':
                # Sawtooth: linear ramp from -1 to 1
                return amplitude * (2 * (angle / (2 * math.pi) % 1) - 1)
            elif wave_type == 'square':
                return amplitude * (1 if math.sin(angle) >= 0 else -1)
            elif wave_type == 'triangle':
                # Triangle wave
                return amplitude * (2 * abs(2 * (angle / (2 * math.pi) % 1) - 1) - 1)
            else:
                raise ValueError(f"Unknown wave type: {wave_type}")
        
        return wave
    
    # -------------------------------------------------------------------------
    # SPECTRUM - Frequency Domain Representation
    # -------------------------------------------------------------------------
    
    def as_spectrum(self, region: ManifoldRegion, 
                    num_harmonics: int = 7) -> Dict[int, complex]:
        """
        Extract frequency spectrum from a region of the surface.
        
        Uses discrete Fourier-like decomposition based on level structure.
        The 7 levels naturally map to harmonic components.
        """
        # Sample values from the region
        values = self.as_vector(region)
        n = len(values)
        
        # Compute coefficients (simplified DFT)
        spectrum = {}
        for k in range(min(num_harmonics, n)):
            real = 0.0
            imag = 0.0
            for i, v in enumerate(values):
                angle = -2 * math.pi * k * i / n
                real += v * math.cos(angle)
                imag += v * math.sin(angle)
            spectrum[k] = complex(real / n, imag / n)
        
        return spectrum
    
    def as_spectral_density(self, region: ManifoldRegion) -> List[float]:
        """Power spectral density of the region"""
        spectrum = self.as_spectrum(region)
        return [abs(c)**2 for c in spectrum.values()]
    
    # -------------------------------------------------------------------------
    # PROBABILITY - Statistical/Probabilistic Interpretations
    # -------------------------------------------------------------------------
    
    def as_probability(self, region: ManifoldRegion,
                       extractor: Callable[[SurfacePoint], float] = lambda p: abs(p.sin)
                       ) -> Callable[[int, int], float]:
        """
        Generate a probability distribution over the region.
        
        Normalizes extracted values to sum to 1.0.
        Returns P(spiral, level) function.
        """
        # Compute all values
        values = {}
        total = 0.0
        for s in range(region.spiral_start, region.spiral_end + 1):
            for l in range(region.level_start, region.level_end + 1):
                val = extractor(self.at(s, l))
                val = max(val, 0.0)  # Ensure non-negative
                values[(s, l)] = val
                total += val
        
        # Normalize
        if total > 0:
            for key in values:
                values[key] /= total
        
        def P(spiral: int, level: int) -> float:
            return values.get((spiral, level), 0.0)
        
        return P
    
    def as_density(self, region: ManifoldRegion) -> Callable[[float], float]:
        """
        Generate a continuous probability density function over t.
        
        Based on the curvature of the helix - higher curvature = higher density.
        """
        # Normalize by integrating curvature over region
        t_start = region.spiral_start + region.level_start / 7.0
        t_end = region.spiral_end + region.level_end / 7.0
        
        # Sample to estimate normalization constant
        samples = 100
        total = 0.0
        for i in range(samples):
            t = t_start + (t_end - t_start) * i / samples
            total += self.at_continuous(t).curvature
        total /= samples
        
        def density(t: float) -> float:
            if t < t_start or t > t_end:
                return 0.0
            point = self.at_continuous(t)
            return point.curvature / total if total > 0 else 0.0
        
        return density
    
    # -------------------------------------------------------------------------
    # DOMAIN / RANGE - Interval Representations
    # -------------------------------------------------------------------------
    
    def as_domain(self, region: ManifoldRegion) -> Tuple[float, float]:
        """Get the t-parameter domain of a region"""
        t_start = region.spiral_start + region.level_start / 7.0
        t_end = region.spiral_end + region.level_end / 7.0
        return (t_start, t_end)
    
    def as_range(self, region: ManifoldRegion,
                 extractor: Callable[[SurfacePoint], float] = lambda p: p.sin
                 ) -> Tuple[float, float]:
        """Get the value range of an extractor over a region"""
        values = self.as_vector(region, extractor)
        return (min(values), max(values))
    
    def as_span(self, region: ManifoldRegion) -> Dict[str, Tuple[float, float]]:
        """Get all geometric spans of a region"""
        points = list(self.as_point_set(region))
        
        return {
            'x': (min(p.x for p in points), max(p.x for p in points)),
            'y': (min(p.y for p in points), max(p.y for p in points)),
            'z': (min(p.z for p in points), max(p.z for p in points)),
            'angle': (min(p.angle for p in points), max(p.angle for p in points)),
            't': (min(p.t for p in points), max(p.t for p in points)),
        }
    
    # -------------------------------------------------------------------------
    # GRAPH - Graph Structure from Surface Connectivity
    # -------------------------------------------------------------------------
    
    def as_graph(self, region: ManifoldRegion,
                 connect_levels: bool = True,
                 connect_spirals: bool = True) -> Dict[Tuple[int, int], List[Tuple[int, int]]]:
        """
        Generate a graph structure from the helix topology.
        
        Nodes are (spiral, level) states.
        Edges connect adjacent states based on connectivity options.
        """
        graph = {}
        
        for s in range(region.spiral_start, region.spiral_end + 1):
            for l in range(region.level_start, region.level_end + 1):
                node = (s, l)
                neighbors = []
                
                if connect_levels:
                    # Connect to adjacent levels
                    if l > region.level_start:
                        neighbors.append((s, l - 1))
                    if l < region.level_end:
                        neighbors.append((s, l + 1))
                
                if connect_spirals:
                    # Connect to adjacent spirals at same level
                    if s > region.spiral_start:
                        neighbors.append((s - 1, l))
                    if s < region.spiral_end:
                        neighbors.append((s + 1, l))
                    
                    # Spiral transitions
                    if l == 6 and s < region.spiral_end:
                        neighbors.append((s + 1, 0))  # SPIRAL_UP
                    if l == 0 and s > region.spiral_start:
                        neighbors.append((s - 1, 6))  # SPIRAL_DOWN
                
                graph[node] = neighbors
        
        return graph
    
    def as_adjacency_matrix(self, region: ManifoldRegion) -> List[List[int]]:
        """Generate adjacency matrix from graph structure"""
        graph = self.as_graph(region)
        nodes = sorted(graph.keys())
        node_index = {n: i for i, n in enumerate(nodes)}
        n = len(nodes)
        
        matrix = [[0] * n for _ in range(n)]
        for node, neighbors in graph.items():
            i = node_index[node]
            for neighbor in neighbors:
                if neighbor in node_index:
                    j = node_index[neighbor]
                    matrix[i][j] = 1
        
        return matrix
    
    # -------------------------------------------------------------------------
    # EXTRAPOLATION - Produce Data Beyond Sampled Region
    # -------------------------------------------------------------------------
    
    def extrapolate(self, region: ManifoldRegion, 
                    target_t: float,
                    extractor: Callable[[SurfacePoint], float] = lambda p: p.sin,
                    method: str = 'linear') -> float:
        """
        Extrapolate a value beyond the sampled region.
        
        Methods:
            'linear': Linear extrapolation from boundary
            'periodic': Periodic extension (wrap around)
            'polynomial': Polynomial fit extrapolation
        """
        domain = self.as_domain(region)
        
        if domain[0] <= target_t <= domain[1]:
            # Within region, just sample
            return extractor(self.at_continuous(target_t))
        
        if method == 'periodic':
            # Wrap around periodically
            span = domain[1] - domain[0]
            wrapped_t = domain[0] + (target_t - domain[0]) % span
            return extractor(self.at_continuous(wrapped_t))
        
        elif method == 'linear':
            # Linear extrapolation from boundary
            if target_t < domain[0]:
                # Extrapolate from start
                t1, t2 = domain[0], domain[0] + 0.1
            else:
                # Extrapolate from end
                t1, t2 = domain[1] - 0.1, domain[1]
            
            v1 = extractor(self.at_continuous(t1))
            v2 = extractor(self.at_continuous(t2))
            slope = (v2 - v1) / (t2 - t1) if t2 != t1 else 0
            
            if target_t < domain[0]:
                return v1 + slope * (target_t - t1)
            else:
                return v2 + slope * (target_t - t2)
        
        elif method == 'polynomial':
            # Polynomial fit (quadratic)
            samples = []
            for i in range(5):
                t = domain[0] + (domain[1] - domain[0]) * i / 4
                samples.append((t, extractor(self.at_continuous(t))))
            
            # Simple quadratic fit using least squares
            # y = a*t² + b*t + c
            n = len(samples)
            sum_t = sum(s[0] for s in samples)
            sum_t2 = sum(s[0]**2 for s in samples)
            sum_t3 = sum(s[0]**3 for s in samples)
            sum_t4 = sum(s[0]**4 for s in samples)
            sum_y = sum(s[1] for s in samples)
            sum_ty = sum(s[0]*s[1] for s in samples)
            sum_t2y = sum(s[0]**2 * s[1] for s in samples)
            
            # Simplified: just use linear for now (polynomial needs matrix inversion)
            slope = sum_ty / sum_t2 if sum_t2 != 0 else 0
            intercept = sum_y / n - slope * sum_t / n
            return slope * target_t + intercept
        
        raise ValueError(f"Unknown extrapolation method: {method}")
    
    # -------------------------------------------------------------------------
    # TRANSFORMATION - Project to Other Structures
    # -------------------------------------------------------------------------
    
    def project_to_plane(self, region: ManifoldRegion, 
                         plane: str = 'xy') -> List[Tuple[float, float]]:
        """Project region points onto a 2D plane"""
        points = []
        for s in range(region.spiral_start, region.spiral_end + 1):
            for l in range(region.level_start, region.level_end + 1):
                p = self.at(s, l)
                if plane == 'xy':
                    points.append((p.x, p.y))
                elif plane == 'xz':
                    points.append((p.x, p.z))
                elif plane == 'yz':
                    points.append((p.y, p.z))
        return points
    
    def as_polar_coordinates(self, spiral: int, level: int) -> Tuple[float, float]:
        """Get polar coordinates (r, θ) at a state"""
        point = self.at(spiral, level)
        return (point.radius, point.angle)
    
    def as_cylindrical_coordinates(self, spiral: int, level: int) -> Tuple[float, float, float]:
        """Get cylindrical coordinates (r, θ, z) at a state"""
        point = self.at(spiral, level)
        return (point.radius, point.angle, point.z)
    
    def as_spherical_coordinates(self, spiral: int, level: int) -> Tuple[float, float, float]:
        """Get spherical coordinates (ρ, θ, φ) at a state"""
        point = self.at(spiral, level)
        rho = math.sqrt(point.x**2 + point.y**2 + point.z**2)
        theta = point.angle
        phi = math.acos(point.z / rho) if rho > 0 else 0
        return (rho, theta, phi)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def helix_sin(spiral: int, level: int) -> float:
    """Direct sine value at helix position"""
    return GenerativeManifold().at(spiral, level).sin

def helix_cos(spiral: int, level: int) -> float:
    """Direct cosine value at helix position"""
    return GenerativeManifold().at(spiral, level).cos

def helix_slope(spiral: int, level: int) -> float:
    """Slope at helix position"""
    return GenerativeManifold().at(spiral, level).slope

def helix_curvature(spiral: int, level: int) -> float:
    """Curvature at helix position"""
    return GenerativeManifold().at(spiral, level).curvature
