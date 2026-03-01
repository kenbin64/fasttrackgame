"""
Hexadic Manifold - Complete Computational Field
================================================

The six-part computational manifold where multiplication, division, and
oscillation form a single continuous field embedded in gyroid topology.

Components:
1. Order-generators (multipliers): z=xy, z=xy²
2. Order-reducers (divisors): z=x/y, z=x/y²
3. Harmonic stabilizers: Pythagorean metric, gyroid curvature

Together they form a closed manifold where computation is flow-based,
not stepwise. The Fibonacci spiral provides the global flow direction,
and the Schwarz diamond gyroid provides the 3D embedding substrate.

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
"""

import math
import numpy as np
from typing import Tuple, List, Optional, Callable, Any
from dataclasses import dataclass
from server.substrates.trinity_substrate import TrinityPoint, TrinitySubstrate, PHI, GOLDEN_ANGLE


@dataclass
class HexadicPoint(TrinityPoint):
    """
    Extended point in hexadic manifold space.
    Includes both multiplicative and divisive operations.
    """
    
    # Divisive components (order-reducers)
    linear_division: float = 0.0      # x/y
    parabolic_division: float = 0.0   # x/y²
    
    # Oscillation state
    phase: float = 0.0                # Position in order↔chaos cycle
    curvature: float = 0.0            # Local manifold curvature
    
    # Gyroid coordinates
    gyroid_u: float = 0.0
    gyroid_v: float = 0.0
    gyroid_w: float = 0.0
    
    def __post_init__(self):
        """Calculate all hexadic components"""
        super().__post_init__()
        self.update_hexadic()
    
    def update_hexadic(self):
        """Recalculate hexadic components"""
        # Update trinity components first
        self.update_trinity()
        
        # DIVISORS: Order-reducers
        if self.y != 0:
            self.linear_division = self.x / self.y
            self.parabolic_division = self.x / (self.y ** 2)
        else:
            self.linear_division = float('inf')
            self.parabolic_division = float('inf')
        
        # OSCILLATION: Phase in order↔chaos cycle
        # Multipliers increase order, divisors increase chaos
        order_force = self.linear_composition + self.parabolic_acceleration
        chaos_force = self.linear_division + self.parabolic_division
        
        # Phase oscillates between -π and π
        if order_force + chaos_force != 0:
            self.phase = math.atan2(chaos_force, order_force)
        else:
            self.phase = 0.0
        
        # CURVATURE: Local manifold curvature
        # Positive = expansion, Negative = contraction
        self.curvature = (order_force - chaos_force) / (order_force + chaos_force + 1e-10)
        
        # GYROID: Map to gyroid coordinates
        self.update_gyroid()
    
    def update_gyroid(self):
        """Map point to Schwarz diamond gyroid surface"""
        # Gyroid equation: sin(u)cos(v) + sin(v)cos(w) + sin(w)cos(u) = 0
        # Map Cartesian to gyroid parameters
        
        # Use Fibonacci spiral angle for u
        self.gyroid_u = self.spiral_angle
        
        # Use phase for v (oscillation)
        self.gyroid_v = self.phase
        
        # Use curvature for w (expansion/contraction)
        self.gyroid_w = self.curvature * math.pi


class HexadicManifold:
    """
    Complete computational manifold with six operators:
    - Multipliers (z=xy, z=xy²): generate order
    - Divisors (z=x/y, z=x/y²): generate chaos
    - Pythagorean metric: stabilize oscillation
    - Fibonacci spiral: global flow
    - Schwarz gyroid: 3D embedding
    
    Computation is flow-based, not stepwise.
    """
    
    def __init__(self):
        self.substrate = TrinitySubstrate()
        self.points = {}
        self.flow_field = {}  # Vector field for flow-based computation
        
        # Oscillation parameters
        self.oscillation_frequency = GOLDEN_ANGLE  # Natural frequency
        self.phase_velocity = PHI  # Speed of phase propagation
    
    def create_point(self, x: float, y: float, z: float = 0.0) -> HexadicPoint:
        """Create point in hexadic manifold"""
        point = HexadicPoint(x, y, z)
        
        coord_key = (round(x, 6), round(y, 6), round(z, 6))
        self.points[coord_key] = point
        
        return point
    
    def multiply_expand(self, p1: HexadicPoint, p2: HexadicPoint, 
                       power: int = 1) -> HexadicPoint:
        """
        Order-generator: multiply to expand manifold.
        power=1: linear (z=xy)
        power=2: parabolic (z=xy²)
        """
        if power == 1:
            # Linear multiplication
            x = p1.x * p2.x
            y = p1.y * p2.y
            z = p1.z * p2.z
        else:
            # Parabolic multiplication
            x = p1.x * (p2.x ** power)
            y = p1.y * (p2.y ** power)
            z = p1.z * (p2.z ** power)
        
        return self.create_point(x, y, z)
    
    def divide_contract(self, p1: HexadicPoint, p2: HexadicPoint,
                       power: int = 1) -> HexadicPoint:
        """
        Order-reducer: divide to contract manifold.
        power=1: linear (z=x/y)
        power=2: parabolic (z=x/y²)
        """
        if power == 1:
            # Linear division
            x = p1.x / p2.x if p2.x != 0 else float('inf')
            y = p1.y / p2.y if p2.y != 0 else float('inf')
            z = p1.z / p2.z if p2.z != 0 else float('inf')
        else:
            # Parabolic division
            x = p1.x / (p2.x ** power) if p2.x != 0 else float('inf')
            y = p1.y / (p2.y ** power) if p2.y != 0 else float('inf')
            z = p1.z / (p2.z ** power) if p2.z != 0 else float('inf')
        
        return self.create_point(x, y, z)
    
    def oscillate(self, point: HexadicPoint, time: float) -> HexadicPoint:
        """
        Oscillate between order and chaos.
        The manifold flows: order → chaos → order
        """
        # Calculate oscillation phase
        phase = point.phase + self.oscillation_frequency * time
        
        # Determine if expanding (order) or contracting (chaos)
        is_expanding = math.cos(phase) > 0
        
        if is_expanding:
            # Multiply: generate order
            factor = 1.0 + abs(math.cos(phase)) * (PHI - 1.0)
            x = point.x * factor
            y = point.y * factor
            z = point.z * factor
        else:
            # Divide: generate chaos
            factor = 1.0 + abs(math.cos(phase)) * (PHI - 1.0)
            x = point.x / factor
            y = point.y / factor
            z = point.z / factor
        
        new_point = self.create_point(x, y, z)
        new_point.phase = phase
        
        return new_point
    
    def gyroid_surface(self, u: float, v: float, w: float) -> Tuple[float, float, float]:
        """
        Calculate point on Schwarz diamond gyroid surface.
        Gyroid equation: sin(u)cos(v) + sin(v)cos(w) + sin(w)cos(u) = 0
        """
        # Parametric form of gyroid
        x = math.sin(u) * math.cos(v)
        y = math.sin(v) * math.cos(w)
        z = math.sin(w) * math.cos(u)
        
        return (x, y, z)
    
    def embed_in_gyroid(self, point: HexadicPoint) -> Tuple[float, float, float]:
        """
        Embed computational point in gyroid topology.
        Returns 3D coordinates on gyroid surface.
        """
        return self.gyroid_surface(point.gyroid_u, point.gyroid_v, point.gyroid_w)
    
    def flow_vector(self, point: HexadicPoint) -> Tuple[float, float, float]:
        """
        Calculate flow vector at point.
        Flow direction determined by:
        - Fibonacci spiral (global flow)
        - Oscillation phase (local flow)
        - Gyroid curvature (embedding constraint)
        """
        # Global flow along Fibonacci spiral
        spiral_flow = (
            math.cos(point.spiral_angle),
            math.sin(point.spiral_angle),
            0.0
        )
        
        # Local flow from oscillation
        if point.curvature > 0:
            # Expanding: flow outward
            oscillation_flow = (point.x, point.y, point.z)
        else:
            # Contracting: flow inward
            oscillation_flow = (-point.x, -point.y, -point.z)
        
        # Normalize and combine
        magnitude = math.sqrt(sum(x**2 for x in oscillation_flow)) + 1e-10
        oscillation_flow = tuple(x / magnitude for x in oscillation_flow)
        
        # Combine flows with golden ratio weighting
        flow = tuple(
            spiral_flow[i] / PHI + oscillation_flow[i] * (1 - 1/PHI)
            for i in range(3)
        )
        
        return flow
    
    def compute_flow(self, start: HexadicPoint, steps: int = 100, 
                    dt: float = 0.1) -> List[HexadicPoint]:
        """
        Flow-based computation: follow the manifold flow.
        This is computation by flowing, not by stepping.
        """
        path = [start]
        current = start
        
        for step in range(steps):
            # Get flow vector
            flow = self.flow_vector(current)
            
            # Move along flow
            x = current.x + flow[0] * dt
            y = current.y + flow[1] * dt
            z = current.z + flow[2] * dt
            
            # Oscillate
            time = step * dt
            current = self.oscillate(self.create_point(x, y, z), time)
            
            path.append(current)
        
        return path
    
    def geodesic_gyroid(self, start: HexadicPoint, end: HexadicPoint,
                       steps: int = 50) -> List[HexadicPoint]:
        """
        Calculate geodesic path on gyroid surface.
        Shortest path constrained to gyroid topology.
        """
        path = []
        
        for i in range(steps + 1):
            t = i / steps
            
            # Interpolate in gyroid parameter space
            u = start.gyroid_u + (end.gyroid_u - start.gyroid_u) * t
            v = start.gyroid_v + (end.gyroid_v - start.gyroid_v) * t
            w = start.gyroid_w + (end.gyroid_w - start.gyroid_w) * t
            
            # Get point on gyroid surface
            x, y, z = self.gyroid_surface(u, v, w)
            
            point = self.create_point(x, y, z)
            point.gyroid_u = u
            point.gyroid_v = v
            point.gyroid_w = w
            
            path.append(point)
        
        return path
    
    def phase_lock(self, p1: HexadicPoint, p2: HexadicPoint) -> float:
        """
        Calculate phase-locking between two points.
        Returns correlation (-1 to 1).
        """
        phase_diff = abs(p1.phase - p2.phase)
        
        # Normalize to [-π, π]
        while phase_diff > math.pi:
            phase_diff -= 2 * math.pi
        
        # Convert to correlation
        correlation = math.cos(phase_diff)
        
        return correlation
    
    def standing_wave(self, points: List[HexadicPoint]) -> List[float]:
        """
        Calculate standing wave pattern across points.
        Returns amplitude at each point.
        """
        amplitudes = []
        
        for point in points:
            # Standing wave amplitude from oscillation
            amplitude = abs(math.sin(point.phase)) * (1.0 + point.curvature)
            amplitudes.append(amplitude)
        
        return amplitudes


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Hexadic Manifold - Complete Computational Field")
    print("=" * 60)
    print()
    
    manifold = HexadicManifold()
    
    # Create points
    p1 = manifold.create_point(3.0, 4.0, 0.0)
    p2 = manifold.create_point(5.0, 12.0, 0.0)
    
    print("Point 1:")
    print(f"  Position: ({p1.x}, {p1.y}, {p1.z})")
    print(f"  Multipliers:")
    print(f"    Linear (z=xy): {p1.linear_composition:.2f}")
    print(f"    Parabolic (z=xy²): {p1.parabolic_acceleration:.2f}")
    print(f"  Divisors:")
    print(f"    Linear (z=x/y): {p1.linear_division:.2f}")
    print(f"    Parabolic (z=x/y²): {p1.parabolic_division:.2f}")
    print(f"  Oscillation:")
    print(f"    Phase: {p1.phase:.2f} rad")
    print(f"    Curvature: {p1.curvature:.2f}")
    print(f"  Gyroid: ({p1.gyroid_u:.2f}, {p1.gyroid_v:.2f}, {p1.gyroid_w:.2f})")
    print()
    
    # Multiply (expand)
    expanded = manifold.multiply_expand(p1, p2, power=1)
    print(f"Multiply (expand): ({expanded.x:.2f}, {expanded.y:.2f})")
    print(f"  Curvature: {expanded.curvature:.2f} (positive = expansion)")
    print()
    
    # Divide (contract)
    contracted = manifold.divide_contract(p1, p2, power=1)
    print(f"Divide (contract): ({contracted.x:.2f}, {contracted.y:.2f})")
    print(f"  Curvature: {contracted.curvature:.2f} (negative = contraction)")
    print()
    
    # Oscillation
    print("Oscillation over time:")
    for t in [0.0, 0.5, 1.0, 1.5, 2.0]:
        oscillated = manifold.oscillate(p1, t)
        print(f"  t={t:.1f}: ({oscillated.x:.2f}, {oscillated.y:.2f}), phase={oscillated.phase:.2f}")
    print()
    
    # Flow-based computation
    print("Flow-based computation (10 steps):")
    flow_path = manifold.compute_flow(p1, steps=10, dt=0.1)
    for i, point in enumerate(flow_path[::2]):  # Every other point
        print(f"  Step {i*2}: ({point.x:.2f}, {point.y:.2f}), curvature={point.curvature:.2f}")
    print()
    
    # Gyroid embedding
    print("Gyroid surface embedding:")
    gyroid_coords = manifold.embed_in_gyroid(p1)
    print(f"  Cartesian: ({p1.x:.2f}, {p1.y:.2f}, {p1.z:.2f})")
    print(f"  Gyroid: ({gyroid_coords[0]:.2f}, {gyroid_coords[1]:.2f}, {gyroid_coords[2]:.2f})")
    print()
    
    print("=" * 60)
    print("Hexadic Manifold demonstrates:")
    print("  ✓ Order-generators (z=xy, z=xy²)")
    print("  ✓ Order-reducers (z=x/y, z=x/y²)")
    print("  ✓ Pythagorean stabilization")
    print("  ✓ Fibonacci spiral flow")
    print("  ✓ Schwarz gyroid embedding")
    print("  ✓ Flow-based computation")
    print("  ✓ Order ↔ Chaos oscillation")
    print("=" * 60)
