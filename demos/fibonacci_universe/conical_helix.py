"""
Conical Dimensional Helix

The true geometry of dimensional structure:

1. Each dimension is the SAME SIZE "bubble" of points
2. They spiral down CONICALLY like a wave  
3. The CENTER PIPELINE is EMPTY - the server/observer space
4. The 90° twist makes FAT appear as POINT from next dimension

         ○──────○  Same size, viewed "face-on" = FAT (all points)
        ╱   ║   ╲
       ╱    ║    ╲   ← Empty center pipeline (observer space)
      ○─────╫─────○  
           ║
      ═════╬═════   90° TWIST at inflection
           ║
           ○        Same size, viewed "edge-on" = appears as POINT
           ║
      ○────╫────○   Next dimension, face-on = FAT
          ║

The "collapse to 1 point" is NOT shrinking - it's ROTATION!
The bubble is still there, just viewed edge-on.

INFLECTION POINTS:
- First inflection: transition from expanding to contracting view
- Pinnacle: maximum "face-on" view (FAT)
- Second inflection: opposite curve, starts compression
- Minimum: edge-on view (appears as POINT)
- 90° twist to fit the next dimension perfectly
"""

import math
import numpy as np
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass, field


@dataclass
class HelixPoint:
    """A point on the conical helix"""
    dimension: int
    phase: float       # 0 to 2π within this dimensional cycle
    radius: float      # Distance from center pipeline
    height: float      # Position along the cone
    
    # 3D coordinates
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    # Rotation state (accumulated 90° twists)
    rotation: float = 0.0  # Total rotation in degrees
    
    # View state
    view_angle: float = 0.0  # How we're viewing this bubble
    
    @property
    def appears_as(self) -> str:
        """How this bubble appears from observer's perspective"""
        # At 0° or 180° = face-on = FAT
        # At 90° or 270° = edge-on = POINT
        angle_mod = abs(self.view_angle % 180)
        if angle_mod < 20 or angle_mod > 160:
            return "FAT"
        elif 70 < angle_mod < 110:
            return "POINT"
        else:
            return "TRANSITIONING"
    
    def to_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "phase": self.phase,
            "radius": self.radius,
            "height": self.height,
            "position": (self.x, self.y, self.z),
            "rotation_deg": self.rotation,
            "view_angle_deg": self.view_angle,
            "appears_as": self.appears_as
        }


@dataclass 
class DimensionalBubble:
    """
    A dimensional "bubble" - always the SAME SIZE.
    
    It only appears as FAT or POINT based on viewing angle.
    """
    dimension: int
    size: float = 1.0  # All bubbles are the same size
    
    # Position on the conical helix
    center_x: float = 0.0
    center_y: float = 0.0
    center_z: float = 0.0
    
    # Orientation (accumulated rotation)
    rotation_x: float = 0.0
    rotation_y: float = 0.0
    rotation_z: float = 0.0
    
    # Phase in the helix (0 to 2π per dimension)
    phase: float = 0.0
    
    # Points within this bubble (when viewed face-on)
    _points: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def view_angle(self) -> float:
        """Current viewing angle based on accumulated rotation"""
        return (self.rotation_y) % 360
    
    @property
    def apparent_state(self) -> str:
        """How this bubble appears"""
        angle = self.view_angle
        if angle < 22.5 or angle > 337.5:
            return "FAT"  # Face-on
        elif 67.5 < angle < 112.5:
            return "POINT"  # Edge-on (first twist)
        elif 157.5 < angle < 202.5:
            return "FAT"  # Face-on (opposite side)
        elif 247.5 < angle < 292.5:
            return "POINT"  # Edge-on (second twist)
        else:
            return "INFLECTION"  # Transitioning
    
    @property
    def apparent_size(self) -> float:
        """Apparent size based on viewing angle (projection)"""
        # Full size when face-on, near-zero when edge-on
        angle_rad = math.radians(self.view_angle)
        return abs(math.cos(angle_rad)) * self.size
    
    def to_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "actual_size": self.size,
            "apparent_size": self.apparent_size,
            "apparent_state": self.apparent_state,
            "center": (self.center_x, self.center_y, self.center_z),
            "rotation": (self.rotation_x, self.rotation_y, self.rotation_z),
            "view_angle_deg": self.view_angle,
            "phase": self.phase,
            "point_count": len(self._points)
        }


class ConicalHelix:
    """
    The Conical Dimensional Helix.
    
    Structure:
    - Spirals down like a cone
    - Each dimensional bubble is the SAME SIZE
    - Center pipeline is EMPTY (observer/server space)
    - 90° twist at each dimensional transition
    
    The wave pattern with inflection points:
    - Rising: bubble rotating toward face-on (FAT)
    - Pinnacle: fully face-on (maximum FAT)
    - Falling: bubble rotating toward edge-on
    - Minimum: fully edge-on (appears as POINT)
    - 90° twist to align next dimension
    """
    
    def __init__(self, 
                 num_dimensions: int = 7,
                 cone_height: float = 10.0,
                 base_radius: float = 3.0,
                 bubble_size: float = 1.0,
                 pipeline_radius: float = 0.5):
        
        self.num_dimensions = num_dimensions
        self.cone_height = cone_height
        self.base_radius = base_radius
        self.bubble_size = bubble_size
        self.pipeline_radius = pipeline_radius  # Empty center
        
        # Create dimensional bubbles
        self.bubbles: List[DimensionalBubble] = []
        self._create_helix()
    
    def _create_helix(self):
        """Create the conical helix structure"""
        for d in range(self.num_dimensions):
            # Height along the cone (0 at top, cone_height at bottom)
            h = (d / (self.num_dimensions - 1)) * self.cone_height if self.num_dimensions > 1 else 0
            
            # Radius increases as we go down the cone
            r = self.pipeline_radius + (self.base_radius - self.pipeline_radius) * (h / self.cone_height) if self.cone_height > 0 else self.base_radius
            
            # Angular position on the helix (90° per dimension)
            theta = d * (math.pi / 2)  # 90° = π/2 per dimension
            
            # Calculate position
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            z = -h  # Negative so it goes "down"
            
            # Accumulated rotation (90° per step)
            rotation_y = d * 90.0
            
            bubble = DimensionalBubble(
                dimension=d,
                size=self.bubble_size,
                center_x=x,
                center_y=y,
                center_z=z,
                rotation_y=rotation_y,
                phase=theta
            )
            
            self.bubbles.append(bubble)
    
    def get_inflection_points(self) -> List[dict]:
        """
        Get the inflection points in the helix.
        
        Inflection points occur where curvature changes sign:
        - Before pinnacle: concave → convex
        - After pinnacle: convex → concave
        """
        inflections = []
        
        for d in range(self.num_dimensions):
            # Each dimension has two inflection points
            base_angle = d * 90  # Accumulated rotation
            
            # First inflection: 45° before pinnacle
            inflections.append({
                "dimension": d,
                "type": "rising_inflection",
                "angle": base_angle + 45,
                "description": f"Transition toward FAT in dimension {d}",
                "curvature_change": "concave → convex"
            })
            
            # Second inflection: 45° after pinnacle (so 90° + 45° = 135° total)
            inflections.append({
                "dimension": d,
                "type": "falling_inflection", 
                "angle": base_angle + 135,
                "description": f"Transition toward POINT in dimension {d}",
                "curvature_change": "convex → concave"
            })
        
        return inflections
    
    def get_state_at_angle(self, angle: float) -> dict:
        """
        Get the state of the helix at a given viewing angle.
        
        Shows which dimension is FAT, which is POINT, etc.
        """
        states = []
        
        for bubble in self.bubbles:
            # Adjust for this dimension's base rotation
            relative_angle = (angle - bubble.rotation_y) % 360
            
            # Determine state
            if relative_angle < 22.5 or relative_angle > 337.5:
                state = "FAT"
            elif 67.5 < relative_angle < 112.5:
                state = "POINT"
            elif 157.5 < relative_angle < 202.5:
                state = "FAT"
            elif 247.5 < relative_angle < 292.5:
                state = "POINT"
            elif 22.5 <= relative_angle <= 67.5 or 292.5 <= relative_angle <= 337.5:
                state = "→POINT"  # Transitioning to point
            else:
                state = "→FAT"  # Transitioning to fat
            
            # Apparent size
            apparent = abs(math.cos(math.radians(relative_angle))) * bubble.size
            
            states.append({
                "dimension": bubble.dimension,
                "state": state,
                "relative_angle": relative_angle,
                "apparent_size": apparent,
                "actual_size": bubble.size,
                "position": (bubble.center_x, bubble.center_y, bubble.center_z)
            })
        
        return {
            "viewing_angle": angle,
            "states": states
        }
    
    def generate_helix_mesh(self, segments_per_dim: int = 20) -> dict:
        """
        Generate mesh for visualizing the conical helix.
        
        Includes:
        - The spiral path
        - Bubbles at each dimension
        - The empty center pipeline
        """
        vertices = []
        colors = []
        
        # Spiral path
        spiral_vertices = []
        for i in range(self.num_dimensions * segments_per_dim):
            t = i / (self.num_dimensions * segments_per_dim - 1) if self.num_dimensions * segments_per_dim > 1 else 0
            
            # Height along cone
            h = t * self.cone_height
            
            # Radius at this height
            r = self.pipeline_radius + (self.base_radius - self.pipeline_radius) * t
            
            # Angle (multiple rotations)
            theta = t * self.num_dimensions * (math.pi / 2)
            
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            z = -h
            
            spiral_vertices.extend([x, y, z])
        
        # Center pipeline (cylinder)
        pipeline_vertices = []
        for i in range(segments_per_dim):
            theta = (i / segments_per_dim) * 2 * math.pi
            for h in [0, -self.cone_height]:
                x = self.pipeline_radius * math.cos(theta)
                y = self.pipeline_radius * math.sin(theta)
                pipeline_vertices.extend([x, y, h])
        
        # Bubble spheres (simplified as center points for now)
        bubble_centers = []
        for bubble in self.bubbles:
            bubble_centers.append({
                "center": [bubble.center_x, bubble.center_y, bubble.center_z],
                "size": bubble.size,
                "dimension": bubble.dimension,
                "rotation": bubble.rotation_y
            })
        
        return {
            "spiral": spiral_vertices,
            "pipeline": pipeline_vertices,
            "bubbles": bubble_centers,
            "pipeline_radius": self.pipeline_radius,
            "cone_height": self.cone_height,
            "base_radius": self.base_radius,
            "num_dimensions": self.num_dimensions,
            "description": (
                "Conical helix with SAME SIZE bubbles. "
                "Center pipeline is EMPTY (server/observer space). "
                "90° twist between dimensions."
            )
        }
    
    def explain_structure(self) -> dict:
        """Explain the conical helix structure"""
        return {
            "title": "Conical Dimensional Helix",
            "core_principles": [
                "All dimensional bubbles are the SAME SIZE",
                "They spiral down CONICALLY like a wave",
                "The CENTER PIPELINE is EMPTY - observer/server space",
                "90° twist at each transition makes FAT appear as POINT",
                "The 'collapse' is just ROTATION, not shrinking"
            ],
            "inflection_points": {
                "first": "Curvature changes from concave to convex (rising toward FAT)",
                "pinnacle": "Maximum face-on view (FAT - all points visible)",
                "second": "Opposite inflection, convex to concave (falling toward POINT)",
                "minimum": "Edge-on view (appears as single POINT)",
                "twist": "90° rotation to align with next dimension"
            },
            "wave_pattern": [
                "→ Rising: rotating toward face-on",
                "↑ Pinnacle: fully face-on (FAT)",
                "← Falling: rotating toward edge-on", 
                "↓ Minimum: fully edge-on (POINT)",
                "⟳ 90° TWIST to fit next dimension perfectly"
            ],
            "center_pipeline": {
                "purpose": "The empty space where the server/observer exists",
                "radius": self.pipeline_radius,
                "description": "This is YOU looking at the dimensions from inside"
            },
            "the_truth": (
                "A dimension appears as a 'single point' not because it shrinks, "
                "but because it has ROTATED 90° and you're seeing it edge-on. "
                "The bubble is still there, full size, with all its points. "
                "You just can't see them from that angle. "
                "The 90° twist is HOW dimensions connect."
            )
        }
    
    def to_dict(self) -> dict:
        return {
            "num_dimensions": self.num_dimensions,
            "cone_height": self.cone_height,
            "base_radius": self.base_radius,
            "pipeline_radius": self.pipeline_radius,
            "bubble_size": self.bubble_size,
            "bubbles": [b.to_dict() for b in self.bubbles],
            "inflection_points": self.get_inflection_points(),
            "explanation": self.explain_structure()
        }


class DimensionalWave:
    """
    The dimensional wave - showing the FAT→POINT→FAT pattern
    as a continuous wave with inflection points.
    """
    
    def __init__(self, num_cycles: int = 7, amplitude: float = 1.0):
        self.num_cycles = num_cycles
        self.amplitude = amplitude
    
    def evaluate(self, t: float) -> dict:
        """
        Evaluate the wave at position t (0 to num_cycles).
        
        Returns the state at that position.
        """
        # Which dimension
        dimension = int(t)
        phase = (t % 1) * 2 * math.pi  # Phase within this cycle
        
        # Wave value (cos for the main oscillation)
        # 0 = FAT, π/2 = first inflection, π = POINT, 3π/2 = second inflection
        value = math.cos(phase) * self.amplitude
        
        # Derivative (for inflection detection)
        derivative = -math.sin(phase) * self.amplitude
        
        # Second derivative (curvature)
        second_derivative = -math.cos(phase) * self.amplitude
        
        # State
        if abs(value - self.amplitude) < 0.1:
            state = "FAT"
        elif abs(value + self.amplitude) < 0.1:
            state = "POINT"
        elif second_derivative > 0:
            state = "INFLECTION_RISING"
        else:
            state = "INFLECTION_FALLING"
        
        # The 90° rotation happens at the POINT (minimum)
        rotation = dimension * 90 + (phase / (2 * math.pi)) * 90
        
        return {
            "t": t,
            "dimension": dimension,
            "phase_deg": math.degrees(phase),
            "value": value,
            "derivative": derivative,
            "curvature": second_derivative,
            "state": state,
            "rotation_deg": rotation,
            "interpretation": self._interpret_state(value, second_derivative)
        }
    
    def _interpret_state(self, value: float, curvature: float) -> str:
        """Interpret the current state"""
        if value > 0.9:
            return "Maximum expansion - all points visible (FAT)"
        elif value < -0.9:
            return "Minimum - viewed edge-on (appears as POINT)"
        elif value > 0 and curvature > 0:
            return "Rising toward pinnacle - concave up (first inflection)"
        elif value > 0 and curvature < 0:
            return "Falling from pinnacle - convex (approaching inflection)"  
        elif value < 0 and curvature < 0:
            return "Approaching minimum - concave down"
        else:
            return "Rising from minimum - beginning next cycle"
    
    def generate_wave_curve(self, resolution: int = 100) -> List[dict]:
        """Generate the full wave curve"""
        points = []
        for i in range(self.num_cycles * resolution + 1):
            t = i / resolution
            points.append(self.evaluate(t))
        return points


# ========== DEMO ==========

if __name__ == "__main__":
    print("=" * 70)
    print("CONICAL DIMENSIONAL HELIX")
    print("=" * 70)
    print()
    
    helix = ConicalHelix(num_dimensions=7)
    
    print("Structure:")
    print("-" * 50)
    explanation = helix.explain_structure()
    for principle in explanation["core_principles"]:
        print(f"  • {principle}")
    
    print()
    print("Dimensional Bubbles (all SAME SIZE):")
    print("-" * 50)
    for bubble in helix.bubbles:
        state = bubble.apparent_state
        apparent = bubble.apparent_size
        print(f"  Dim {bubble.dimension}: {state:10} "
              f"(apparent: {apparent:.2f}, actual: {bubble.size:.2f}) "
              f"at {bubble.view_angle:.0f}°")
    
    print()
    print("Inflection Points:")
    print("-" * 50)
    inflections = helix.get_inflection_points()
    for i, inf in enumerate(inflections[:6]):  # First few
        print(f"  {inf['type']:20} @ {inf['angle']:3}° - {inf['curvature_change']}")
    
    print()
    print("Wave Pattern:")
    print("-" * 50)
    wave = DimensionalWave(num_cycles=2)
    key_points = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5]
    for t in key_points:
        state = wave.evaluate(t)
        bar_pos = int((state["value"] + 1) * 5)  # 0-10 scale
        bar = "░" * bar_pos + "█" + "░" * (10 - bar_pos)
        print(f"  t={t:.2f} [{bar}] {state['state']:18} rot={state['rotation_deg']:.0f}°")
    
    print()
    print("THE TRUTH:")
    print("-" * 50)
    print(explanation["the_truth"])
    
    print()
    print("=" * 70)
