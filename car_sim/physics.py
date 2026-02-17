"""
Physics Engine - Pure Substrate Transformations

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)

The physics engine applies DIMENSIONAL TRANSFORMATIONS to evolve
car state through time. No AI, no heuristics - pure mathematics.

Key Dimensional Mappings:
    - Time is a dimension (dt advances along time manifold)
    - Force is a vector field on the spatial manifold  
    - Velocity is the tangent to the position curve
    - Energy conservation is a manifold invariant
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Tuple
import math
import time


@dataclass
class PhysicsConfig:
    """Physics simulation configuration"""
    # Simulation
    time_step: float = 0.016   # ~60 FPS
    max_dt: float = 0.1        # Maximum time step
    
    # Environment
    gravity: float = 9.81      # m/s²
    air_density: float = 1.225 # kg/m³ at sea level
    road_friction: float = 0.8 # Coefficient
    
    # Vehicle defaults
    drag_coefficient: float = 0.30
    frontal_area: float = 2.2  # m²
    rolling_resistance: float = 0.01
    
    # Limits
    max_speed_mph: float = 200
    max_brake_decel: float = 10  # m/s² (~1g)
    max_accel: float = 8         # m/s²


class PhysicsEngine:
    """
    Pure mathematical physics engine.
    
    Evolves car state through substrate transformations.
    All calculations are deterministic and reproducible.
    """
    
    def __init__(self, config: PhysicsConfig = None):
        self.config = config or PhysicsConfig()
        self._last_time = time.time()
    
    def step(self, car, dt: float = None) -> Dict:
        """
        Advance physics simulation by one time step.
        
        Args:
            car: CarSubstrate to update
            dt: Time step (uses config default if None)
        
        Returns:
            Dictionary of physics state for telemetry
        """
        if dt is None:
            current = time.time()
            dt = min(current - self._last_time, self.config.max_dt)
            self._last_time = current
        
        # Apply substrate transformation
        car.transform(dt)
        
        # Return telemetry
        return {
            "dt": dt,
            "speed_mph": car.velocity.speed,
            "speed_mps": car.velocity.speed_mps,
            "acceleration": car.forces.net_force / (car.specs.weight_lbs * 0.453592),
            "engine_force": car.forces.engine,
            "drag_force": car.forces.drag,
            "brake_force": car.forces.braking,
        }
    
    def run_simulation(self, car, duration: float, 
                       control_func: Callable = None) -> List[Dict]:
        """
        Run simulation for specified duration.
        
        Args:
            car: CarSubstrate to simulate
            duration: Simulation time in seconds
            control_func: Optional function(car, t) to set controls
        
        Returns:
            List of state snapshots
        """
        dt = self.config.time_step
        steps = int(duration / dt)
        history = []
        
        for i in range(steps):
            t = i * dt
            
            # Apply controls if provided
            if control_func:
                control_func(car, t)
            
            # Step physics
            telemetry = self.step(car, dt)
            
            # Record state
            history.append({
                "t": t,
                "dashboard": car.get_dashboard(),
                "telemetry": telemetry
            })
        
        return history


@dataclass 
class RoadSegment:
    """A segment of the road manifold"""
    start_x: float = 0
    end_x: float = 1000
    curvature: float = 0      # 0 = straight, + = right curve, - = left
    grade: float = 0          # Slope (0 = flat, + = uphill)
    friction: float = 0.8     # Surface friction
    lanes: int = 2
    lane_width: float = 3.5   # meters
    
    @property
    def length(self) -> float:
        return self.end_x - self.start_x


class RoadManifold:
    """
    Road as a 1D manifold embedded in 2D/3D space.
    
    The road is parameterized by distance (arc length).
    At each point, we have:
        - Position (x, y) or (x, y, z)
        - Tangent direction
        - Curvature
        - Road width
    """
    
    def __init__(self, segments: List[RoadSegment] = None):
        self.segments = segments or [RoadSegment()]
        self._build_road()
    
    def _build_road(self):
        """Build the road path from segments"""
        self.total_length = sum(s.length for s in self.segments)
        
        # Compute cumulative distances
        self.segment_starts = []
        dist = 0
        for seg in self.segments:
            self.segment_starts.append(dist)
            dist += seg.length
    
    def get_position(self, distance: float) -> Tuple[float, float]:
        """Get world (x, y) position at distance along road"""
        # Find which segment
        seg_idx = 0
        local_dist = distance
        
        for i, start in enumerate(self.segment_starts):
            if i < len(self.segments) - 1:
                if distance >= start and distance < self.segment_starts[i + 1]:
                    seg_idx = i
                    local_dist = distance - start
                    break
            else:
                seg_idx = i
                local_dist = distance - start
        
        seg = self.segments[seg_idx]
        
        # For straight road
        if abs(seg.curvature) < 0.001:
            x = seg.start_x + local_dist
            y = 0
        else:
            # Curved road: arc of circle
            r = 1 / seg.curvature
            theta = local_dist / r
            x = seg.start_x + r * math.sin(theta)
            y = r * (1 - math.cos(theta))
        
        return (x, y)
    
    def get_tangent(self, distance: float) -> float:
        """Get road heading (radians) at distance"""
        # Find segment and compute tangent
        pos1 = self.get_position(distance)
        pos2 = self.get_position(distance + 0.1)
        
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        
        return math.atan2(dy, dx)
    
    def get_lane_center(self, distance: float, lane: int) -> Tuple[float, float]:
        """Get world position for lane center"""
        x, y = self.get_position(distance)
        tangent = self.get_tangent(distance)
        
        # Perpendicular offset for lane
        seg = self.segments[0]  # Simplified
        offset = (lane - 0.5) * seg.lane_width
        
        # Offset perpendicular to tangent
        x += offset * math.sin(tangent)
        y -= offset * math.cos(tangent)
        
        return (x, y)


# =============================================================================
# DIMENSIONAL COORDINATE TRANSFORMATIONS
# =============================================================================

def world_to_screen(world_x: float, world_y: float, 
                    camera_x: float, camera_y: float,
                    screen_width: int, screen_height: int,
                    scale: float = 10) -> Tuple[int, int]:
    """Transform world coordinates to screen pixels"""
    # Center on camera
    rel_x = world_x - camera_x
    rel_y = world_y - camera_y
    
    # Scale to pixels
    px = int(screen_width / 2 + rel_x * scale)
    py = int(screen_height / 2 - rel_y * scale)  # Y inverted
    
    return (px, py)


def screen_to_world(screen_x: int, screen_y: int,
                    camera_x: float, camera_y: float, 
                    screen_width: int, screen_height: int,
                    scale: float = 10) -> Tuple[float, float]:
    """Transform screen pixels to world coordinates"""
    rel_x = (screen_x - screen_width / 2) / scale
    rel_y = (screen_height / 2 - screen_y) / scale
    
    world_x = camera_x + rel_x
    world_y = camera_y + rel_y
    
    return (world_x, world_y)


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    from car_substrate import CarSubstrate
    
    print("Physics Engine Test")
    print("=" * 40)
    
    # Create car and engine
    car = CarSubstrate.from_api(make="Toyota", model="Camry")
    engine = PhysicsEngine()
    
    # Accelerate for 5 seconds
    car.start_engine()
    car.set_throttle(0.8)
    
    print("\nAccelerating for 5 seconds...")
    history = engine.run_simulation(car, 5.0)
    
    for h in history[::int(len(history)/5)]:
        d = h['dashboard']
        print(f"  t={h['t']:.1f}s: {d['mph']}mph, {d['rpm']}rpm")
    
    # Coast and brake
    car.set_throttle(0)
    car.set_brake(0.5)
    
    print("\nBraking for 3 seconds...")
    history = engine.run_simulation(car, 3.0)
    
    for h in history[::int(len(history)/3)]:
        d = h['dashboard']
        print(f"  t={h['t']:.1f}s: {d['mph']}mph")
    
    print(f"\nFinal state:")
    print(f"  Speed: {car.get_dashboard()['mph']} mph")
    print(f"  Distance: {car.get_dashboard()['trip']} miles")
    print(f"  Fuel used: {car.fuel_consumed:.3f} gallons")
