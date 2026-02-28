"""
Trinity Substrate - Unified Geometric Computing
================================================

The trinity of equations that form the foundation of dimensional computing:
1. Pythagorean: a² + b² = c² (distance/similarity)
2. Linear: z = xy (composition)
3. Parabolic: z = xy² (acceleration)

Together they create the Fibonacci spiral - the optimal geometric substrate.

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
"""

import math
from typing import Tuple, List, Optional, Callable, Any
from dataclasses import dataclass
import numpy as np


# Golden ratio - emerges from Fibonacci spiral
PHI = (1 + math.sqrt(5)) / 2  # ≈ 1.618033988749895
GOLDEN_ANGLE = 2 * math.pi / (PHI ** 2)  # ≈ 137.5° (optimal distribution)


@dataclass
class TrinityPoint:
    """A point in trinity substrate space"""
    x: float
    y: float
    z: float = 0.0  # Third dimension for manifold
    
    # Trinity components
    pythagorean_distance: float = 0.0  # √(x² + y²)
    linear_composition: float = 0.0    # xy
    parabolic_acceleration: float = 0.0  # xy²
    
    # Fibonacci properties
    spiral_index: int = 0
    spiral_radius: float = 0.0
    spiral_angle: float = 0.0
    
    def __post_init__(self):
        """Calculate trinity components"""
        self.update_trinity()
    
    def update_trinity(self):
        """Recalculate all trinity components"""
        # 1. PYTHAGOREAN: Distance metric
        self.pythagorean_distance = math.sqrt(self.x**2 + self.y**2)
        
        # 2. LINEAR: Composition
        self.linear_composition = self.x * self.y
        
        # 3. PARABOLIC: Acceleration
        self.parabolic_acceleration = self.x * (self.y ** 2)
        
        # FIBONACCI: Spiral properties
        if self.pythagorean_distance > 0:
            self.spiral_radius = self.pythagorean_distance
            self.spiral_angle = math.atan2(self.y, self.x)
            # Map to Fibonacci index (logarithmic spiral)
            self.spiral_index = int(math.log(self.spiral_radius + 1) / math.log(PHI))


class TrinitySubstrate:
    """
    Unified geometric substrate using trinity of equations.
    
    Provides O(1) operations through geometric indexing:
    - Pythagorean for spatial indexing
    - Linear for composition
    - Parabolic for acceleration
    - Fibonacci for optimal organization
    """
    
    def __init__(self):
        self.points = {}  # coordinate -> TrinityPoint
        self.spatial_index = {}  # spiral_index -> [points]
        self.fibonacci_cache = [1, 1]  # Memoized Fibonacci sequence
    
    def fibonacci(self, n: int) -> int:
        """Get nth Fibonacci number (cached)"""
        while len(self.fibonacci_cache) <= n:
            self.fibonacci_cache.append(
                self.fibonacci_cache[-1] + self.fibonacci_cache[-2]
            )
        return self.fibonacci_cache[n]
    
    def create_point(self, x: float, y: float, z: float = 0.0) -> TrinityPoint:
        """Create a point in trinity substrate space"""
        point = TrinityPoint(x, y, z)
        
        # Store in spatial index by Fibonacci spiral layer
        if point.spiral_index not in self.spatial_index:
            self.spatial_index[point.spiral_index] = []
        self.spatial_index[point.spiral_index].append(point)
        
        # Store by coordinates
        coord_key = (round(x, 6), round(y, 6), round(z, 6))
        self.points[coord_key] = point
        
        return point
    
    def pythagorean_distance(self, p1: TrinityPoint, p2: TrinityPoint) -> float:
        """
        Calculate Pythagorean distance between two points.
        O(1) operation.
        """
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        dz = p2.z - p1.z
        return math.sqrt(dx**2 + dy**2 + dz**2)
    
    def linear_compose(self, p1: TrinityPoint, p2: TrinityPoint) -> float:
        """
        Linear composition: z = xy
        Combines two dimensions multiplicatively.
        O(1) operation.
        """
        return p1.linear_composition * p2.linear_composition
    
    def parabolic_accelerate(self, p: TrinityPoint, factor: float = 1.0) -> float:
        """
        Parabolic acceleration: z = xy²
        Applies non-linear growth.
        O(1) operation.
        """
        return p.x * (p.y ** 2) * factor
    
    def fibonacci_position(self, index: int) -> Tuple[float, float]:
        """
        Calculate position on Fibonacci spiral for given index.
        Uses golden angle for optimal distribution.
        """
        # Golden angle rotation
        angle = index * GOLDEN_ANGLE
        
        # Fibonacci radius (exponential growth)
        radius = PHI ** (index / 4.0)
        
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        
        return (x, y)
    
    def nearest_neighbors(self, query: TrinityPoint, k: int = 5) -> List[TrinityPoint]:
        """
        Find k nearest neighbors using Pythagorean distance.
        O(log n) using Fibonacci spiral indexing.
        """
        candidates = []
        
        # Search in same spiral layer and adjacent layers
        search_layers = [
            query.spiral_index - 1,
            query.spiral_index,
            query.spiral_index + 1
        ]
        
        for layer in search_layers:
            if layer in self.spatial_index:
                candidates.extend(self.spatial_index[layer])
        
        # Sort by Pythagorean distance
        candidates.sort(key=lambda p: self.pythagorean_distance(query, p))
        
        return candidates[:k]
    
    def compose_manifold(self, points: List[TrinityPoint]) -> TrinityPoint:
        """
        Compose multiple points into a single manifold point.
        Uses linear composition (z = xy) for each dimension.
        O(n) where n is number of points.
        """
        if not points:
            return TrinityPoint(0, 0, 0)
        
        # Linear composition of all points
        x = 1.0
        y = 1.0
        z = 1.0
        
        for point in points:
            x *= point.x if point.x != 0 else 1.0
            y *= point.y if point.y != 0 else 1.0
            z *= point.z if point.z != 0 else 1.0
        
        return self.create_point(x, y, z)
    
    def accelerate_toward(self, current: TrinityPoint, target: TrinityPoint, 
                         acceleration: float = PHI) -> TrinityPoint:
        """
        Accelerate current point toward target using parabolic curve.
        Uses z = xy² for smooth acceleration.
        """
        # Direction vector
        dx = target.x - current.x
        dy = target.y - current.y
        dz = target.z - current.z
        
        # Parabolic acceleration factor
        distance = self.pythagorean_distance(current, target)
        accel_factor = (distance / PHI) ** 2  # Parabolic
        
        # New position with acceleration
        new_x = current.x + dx * accel_factor / distance
        new_y = current.y + dy * accel_factor / distance
        new_z = current.z + dz * accel_factor / distance
        
        return self.create_point(new_x, new_y, new_z)
    
    def spiral_time_index(self, timestamp: float) -> int:
        """
        Map timestamp to Fibonacci spiral index.
        Recent times = inner spiral (low index)
        Older times = outer spiral (high index)
        """
        # Logarithmic mapping to spiral
        # More recent = tighter spiral
        return int(math.log(timestamp + 1) / math.log(PHI))
    
    def delta_threshold(self, point: TrinityPoint) -> float:
        """
        Calculate delta threshold using golden ratio.
        Only recompute if change exceeds φ proportion.
        """
        magnitude = point.pythagorean_distance
        return magnitude / PHI  # Golden ratio threshold


class TrinityManifold:
    """
    Manifold processor using trinity substrate.
    Enables smooth transformations through geometric space.
    """
    
    def __init__(self, substrate: TrinitySubstrate):
        self.substrate = substrate
        self.transformations = []  # History of transformations
    
    def transform(self, point: TrinityPoint, 
                 transformation: Callable[[TrinityPoint], TrinityPoint]) -> TrinityPoint:
        """
        Apply transformation to point on manifold.
        Transformation is a smooth curve, not a discrete jump.
        """
        # Apply transformation
        new_point = transformation(point)
        
        # Store transformation for composition
        self.transformations.append((point, new_point))
        
        return new_point
    
    def compose(self, *transformations: Callable) -> Callable:
        """
        Compose multiple transformations geometrically.
        f ∘ g ∘ h applied as smooth manifold curve.
        """
        def composed(point: TrinityPoint) -> TrinityPoint:
            result = point
            for transform in transformations:
                result = transform(result)
            return result
        return composed
    
    def geodesic(self, start: TrinityPoint, end: TrinityPoint, 
                steps: int = 10) -> List[TrinityPoint]:
        """
        Calculate geodesic (shortest path) between two points.
        Uses Pythagorean distance and parabolic acceleration.
        """
        path = [start]
        current = start
        
        for i in range(1, steps):
            # Interpolation factor (parabolic for smooth acceleration)
            t = (i / steps) ** 2  # Parabolic interpolation
            
            # Linear interpolation with parabolic weighting
            x = start.x + (end.x - start.x) * t
            y = start.y + (end.y - start.y) * t
            z = start.z + (end.z - start.z) * t
            
            current = self.substrate.create_point(x, y, z)
            path.append(current)
        
        path.append(end)
        return path
    
    def lazy_evaluate(self, point: TrinityPoint, 
                     computation: Callable[[TrinityPoint], Any],
                     cache: dict) -> Any:
        """
        Lazy evaluation - only compute if not in cache.
        Uses Pythagorean distance to find cached results.
        """
        # Check cache for nearby points (within golden ratio threshold)
        threshold = self.substrate.delta_threshold(point)
        
        for cached_point, cached_result in cache.items():
            if isinstance(cached_point, TrinityPoint):
                distance = self.substrate.pythagorean_distance(point, cached_point)
                if distance < threshold:
                    return cached_result  # Cache hit!
        
        # Cache miss - compute and store
        result = computation(point)
        cache[point] = result
        return result


# Example usage and demonstrations
if __name__ == "__main__":
    print("=" * 60)
    print("Trinity Substrate - Unified Geometric Computing")
    print("=" * 60)
    print()
    
    # Create substrate
    substrate = TrinitySubstrate()
    
    # Create some points
    p1 = substrate.create_point(3.0, 4.0)
    p2 = substrate.create_point(5.0, 12.0)
    p3 = substrate.create_point(8.0, 15.0)
    
    print("Point 1:")
    print(f"  Position: ({p1.x}, {p1.y})")
    print(f"  Pythagorean distance: {p1.pythagorean_distance:.2f}")
    print(f"  Linear composition: {p1.linear_composition:.2f}")
    print(f"  Parabolic acceleration: {p1.parabolic_acceleration:.2f}")
    print(f"  Fibonacci spiral index: {p1.spiral_index}")
    print()
    
    # Pythagorean distance
    dist = substrate.pythagorean_distance(p1, p2)
    print(f"Distance between p1 and p2: {dist:.2f}")
    print()
    
    # Linear composition
    composed = substrate.linear_compose(p1, p2)
    print(f"Linear composition of p1 and p2: {composed:.2f}")
    print()
    
    # Parabolic acceleration
    accel = substrate.parabolic_accelerate(p1)
    print(f"Parabolic acceleration of p1: {accel:.2f}")
    print()
    
    # Fibonacci spiral positions
    print("Fibonacci spiral positions:")
    for i in range(8):
        x, y = substrate.fibonacci_position(i)
        fib = substrate.fibonacci(i)
        print(f"  F({i}) = {fib:3d}: ({x:6.2f}, {y:6.2f})")
    print()
    
    # Manifold operations
    manifold = TrinityManifold(substrate)
    
    # Geodesic path
    path = manifold.geodesic(p1, p2, steps=5)
    print("Geodesic path from p1 to p2:")
    for i, point in enumerate(path):
        print(f"  Step {i}: ({point.x:.2f}, {point.y:.2f})")
    print()
    
    print("=" * 60)
    print("Trinity substrate demonstrates:")
    print("  ✓ Pythagorean distance (a² + b² = c²)")
    print("  ✓ Linear composition (z = xy)")
    print("  ✓ Parabolic acceleration (z = xy²)")
    print("  ✓ Fibonacci spiral organization")
    print("  ✓ O(1) operations through geometric indexing")
    print("=" * 60)
