"""
Car Substrate - Dimensional Vehicle Entity

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)

The car is a TOKEN on the MANIFOLD. Its state evolves through
SUBSTRATE TRANSFORMATIONS, not imperative state mutation.

Dimensional Architecture:
    - Car position is a point on the road manifold
    - Velocity is the tangent vector at that point  
    - Acceleration is the rate of change of the tangent
    - Dashboard readings are LENS projections of state

The car's physics are pure mathematical transformations:
    F = ma  (force manifold -> acceleration manifold)
    v = ∫a dt  (integration along time dimension)
    x = ∫v dt  (position as path integral)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Tuple
from enum import Enum, auto
import math
import time

from .car_api import VehicleSpecs, DimensionalVehicleCoord, fetch_car_specs

# Alias for backward compatibility
CarSpecs = VehicleSpecs


# =============================================================================
# DIMENSIONAL STATE COORDINATES
# =============================================================================

class DriveState(Enum):
    """Car drive states on the state manifold"""
    PARKED = auto()
    IDLE = auto()
    ACCELERATING = auto()
    CRUISING = auto()
    BRAKING = auto()
    COASTING = auto()


@dataclass
class ManifoldPosition:
    """Position on the road manifold"""
    # Road coordinate (1D path parameter)
    distance: float = 0.0  # Total distance traveled (odometer)
    
    # Lane position (-1 to 1, 0 = center)
    lane_offset: float = 0.0
    
    # Heading angle (radians from road tangent)
    heading: float = 0.0
    
    def to_world(self, road_curvature: float = 0.0) -> Tuple[float, float]:
        """Convert to world (x, y) coordinates for rendering"""
        # Road follows a curve; position maps to (x, y)
        # For now, assume straight road along x-axis
        x = self.distance
        y = self.lane_offset * 3.0  # Lane width ~3 meters
        return (x, y)


@dataclass
class VelocityVector:
    """Velocity as tangent vector on manifold"""
    speed: float = 0.0  # mph
    angular_velocity: float = 0.0  # rad/s (steering)
    
    @property
    def speed_mps(self) -> float:
        """Speed in meters per second"""
        return self.speed * 0.44704
    
    @property
    def speed_fps(self) -> float:
        """Speed in feet per second"""
        return self.speed * 1.46667


@dataclass
class ForceVector:
    """Forces acting on the car (dimensional force field)"""
    engine: float = 0.0      # Engine force (Newtons)
    braking: float = 0.0     # Brake force (Newtons)
    drag: float = 0.0        # Air resistance
    rolling: float = 0.0     # Rolling resistance
    gravity: float = 0.0     # Slope component
    
    @property
    def net_force(self) -> float:
        """Net longitudinal force"""
        return self.engine - self.braking - self.drag - self.rolling - self.gravity


# =============================================================================
# CAR SUBSTRATE - The Main Token
# =============================================================================

@dataclass
class CarSubstrate:
    """
    A car as a TOKEN on the vehicle/road MANIFOLD.
    
    The car's state is defined by its COORDINATES on multiple manifolds:
        - Position manifold (road geometry)
        - Velocity manifold (tangent space)
        - Force manifold (dynamics)
        - Resource manifold (fuel, wear)
    
    State evolution follows substrate transformation rules.
    """
    
    # Vehicle specifications (from API)
    specs: VehicleSpecs = field(default_factory=VehicleSpecs)
    dimensional: DimensionalVehicleCoord = field(default_factory=DimensionalVehicleCoord)
    
    # Current state (manifold coordinates)
    position: ManifoldPosition = field(default_factory=ManifoldPosition)
    velocity: VelocityVector = field(default_factory=VelocityVector)
    forces: ForceVector = field(default_factory=ForceVector)
    
    # Drive state
    state: DriveState = DriveState.PARKED
    engine_rpm: float = 0.0
    gear: int = 0  # 0 = Park, 1-6 = gears, -1 = Reverse
    
    # Resources (position on resource manifold)
    fuel_gallons: float = 14.0      # Current fuel
    fuel_consumed: float = 0.0      # Total consumed
    trip_distance: float = 0.0      # Trip odometer
    
    # Controls (input from steering wheel/pedals)
    throttle: float = 0.0      # 0-1
    brake: float = 0.0         # 0-1
    steering: float = 0.0      # -1 to 1
    
    # Timestamps for physics
    _last_update: float = field(default_factory=time.time)
    
    # ==========================================================================
    # FACTORY METHODS
    # ==========================================================================
    
    @classmethod
    def from_api(cls, make: str = "Toyota", model: str = "Camry", 
                 year: int = 2024, vin: str = None) -> 'CarSubstrate':
        """Create car from API specs"""
        if vin:
            specs = fetch_car_specs(vin=vin)
        else:
            specs = fetch_car_specs(make=make, model=model, year=year)
        
        dimensional = specs.to_dimensional()
        
        return cls(
            specs=specs,
            dimensional=dimensional,
            fuel_gallons=specs.fuel_capacity_gal,  # Start with full tank
        )
    
    @classmethod
    def from_specs(cls, specs: VehicleSpecs) -> 'CarSubstrate':
        """Create from existing specs"""
        return cls(
            specs=specs,
            dimensional=specs.to_dimensional(),
            fuel_gallons=specs.fuel_capacity_gal,
        )
    
    # ==========================================================================
    # LENS PROJECTIONS (Substrate -> Dashboard Readings)
    # ==========================================================================
    
    @property
    def speedometer_mph(self) -> float:
        """Speedometer reading"""
        return abs(self.velocity.speed)
    
    @property
    def tachometer_rpm(self) -> float:
        """Engine RPM"""
        return self.engine_rpm
    
    @property
    def fuel_gauge(self) -> float:
        """Fuel level as 0-1"""
        return self.fuel_gallons / self.specs.fuel_capacity_gal
    
    @property
    def odometer_miles(self) -> float:
        """Total distance (feet to miles)"""
        return self.position.distance / 5280
    
    @property
    def trip_miles(self) -> float:
        """Trip distance"""
        return self.trip_distance / 5280
    
    @property
    def current_mpg(self) -> float:
        """Current fuel efficiency (instantaneous)"""
        if self.fuel_consumed < 0.001:
            return self.specs.mpg_combined  # No consumption yet
        return self.trip_miles / self.fuel_consumed
    
    @property
    def range_miles(self) -> float:
        """Estimated range remaining"""
        return self.fuel_gallons * self.specs.mpg_combined
    
    # ==========================================================================
    # DASHBOARD STATE (for UI)
    # ==========================================================================
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get all dashboard readings as dictionary"""
        return {
            "mph": round(self.speedometer_mph, 1),
            "rpm": round(self.tachometer_rpm),
            "gear": self._gear_display(),
            "fuel_level": round(self.fuel_gauge, 2),
            "fuel_gallons": round(self.fuel_gallons, 2),
            "odometer": round(self.odometer_miles, 1),
            "trip": round(self.trip_miles, 2),
            "mpg": round(self.current_mpg, 1),
            "range": round(self.range_miles),
            "state": self.state.name,
            "throttle": round(self.throttle * 100),
            "brake": round(self.brake * 100),
            "steering": round(self.steering * 100),
        }
    
    def _gear_display(self) -> str:
        """Gear display for dashboard"""
        if self.gear == 0:
            return "P"
        elif self.gear == -1:
            return "R"
        else:
            return str(self.gear)
    
    # ==========================================================================
    # SUBSTRATE TRANSFORMATIONS (Physics)
    # ==========================================================================
    
    def transform(self, dt: float) -> 'CarSubstrate':
        """
        Apply substrate transformation (time evolution).
        
        This is the core physics: state at t+dt is computed from
        state at t through pure mathematical transformation.
        
        Returns: New car state (immutable transformation)
        """
        # 1. Compute forces from controls
        forces = self._compute_forces()
        
        # 2. Compute acceleration from forces (F = ma)
        mass_kg = self.specs.weight_lbs * 0.453592
        accel_mps2 = forces.net_force / mass_kg
        accel_mph_s = accel_mps2 * 2.23694  # m/s² to mph/s
        
        # 3. Update velocity (v = v0 + a*dt)
        new_speed = self.velocity.speed + accel_mph_s * dt
        new_speed = max(0, new_speed)  # Can't go negative (would need reverse)
        
        if self.gear == -1:  # Reverse
            new_speed = -abs(new_speed)
        
        # 4. Update position (x = x0 + v*dt)
        distance_feet = self.velocity.speed_fps * dt
        new_distance = self.position.distance + abs(distance_feet)
        
        # 5. Update steering/lane position
        steering_rate = self.steering * 0.5  # Lane change rate
        new_lane = self.position.lane_offset + steering_rate * dt
        new_lane = max(-1, min(1, new_lane))
        
        # 6. Update fuel consumption
        fuel_rate = self._fuel_consumption_rate()
        fuel_used = fuel_rate * dt / 3600  # gallons per second
        new_fuel = max(0, self.fuel_gallons - fuel_used)
        
        # 7. Compute engine RPM
        new_rpm = self._compute_rpm(new_speed)
        
        # 8. Determine gear (automatic transmission)
        new_gear = self._compute_gear(new_speed)
        
        # 9. Determine state
        new_state = self._determine_state()
        
        # 10. Create new immutable state (functional transformation)
        # In practice we mutate for performance, but conceptually this is pure
        self.velocity = VelocityVector(speed=new_speed)
        self.position = ManifoldPosition(
            distance=new_distance,
            lane_offset=new_lane,
            heading=self.position.heading
        )
        self.forces = forces
        self.fuel_gallons = new_fuel
        self.fuel_consumed += fuel_used
        self.trip_distance += abs(distance_feet)
        self.engine_rpm = new_rpm
        self.gear = new_gear
        self.state = new_state
        self._last_update = time.time()
        
        return self
    
    def _compute_forces(self) -> ForceVector:
        """Compute all forces acting on the car"""
        mass_kg = self.specs.weight_lbs * 0.453592
        speed_mps = self.velocity.speed_mps
        
        # Engine force (from throttle and power curve)
        # P = F * v, so F = P / v (with limits)
        max_engine_force = self._max_engine_force()
        engine_force = self.throttle * max_engine_force
        
        # Braking force
        max_brake_force = mass_kg * 10  # ~1g deceleration max
        brake_force = self.brake * max_brake_force
        
        # Aerodynamic drag: F_drag = 0.5 * rho * Cd * A * v²
        rho = 1.225  # Air density kg/m³
        cd = 0.3     # Drag coefficient (typical sedan)
        area = 2.2   # Frontal area m²
        drag = 0.5 * rho * cd * area * speed_mps ** 2
        
        # Rolling resistance: F = Crr * m * g
        crr = 0.01   # Rolling resistance coefficient
        rolling = crr * mass_kg * 9.81
        
        return ForceVector(
            engine=engine_force,
            braking=brake_force,
            drag=drag,
            rolling=rolling if speed_mps > 0.1 else 0,
            gravity=0  # Flat road for now
        )
    
    def _max_engine_force(self) -> float:
        """Maximum engine force available at current speed"""
        # Power (W) = HP * 745.7
        power_watts = self.specs.horsepower * 745.7
        
        speed_mps = max(0.1, self.velocity.speed_mps)  # Avoid div by zero
        
        # F = P / v, but limited by torque at low speeds
        max_from_power = power_watts / speed_mps
        
        # At low speed, limited by torque
        # Torque (Nm) = lb-ft * 1.356
        torque_nm = self.specs.torque * 1.356
        wheel_radius = 0.35  # meters (typical)
        gear_ratio = 3.5     # Simplified
        max_from_torque = torque_nm * gear_ratio / wheel_radius
        
        return min(max_from_power, max_from_torque)
    
    def _fuel_consumption_rate(self) -> float:
        """Fuel consumption in gallons per hour"""
        base_mpg = self.specs.mpg_combined
        
        # Adjust for driving conditions
        if self.velocity.speed < 5:
            # Idling: ~0.5 gal/hr
            return 0.5 if self.throttle > 0 else 0
        
        # MPG varies with speed (peak around 45-55 mph)
        speed = abs(self.velocity.speed)
        efficiency_factor = 1.0
        if speed < 30:
            efficiency_factor = 0.7
        elif speed < 60:
            efficiency_factor = 1.0
        elif speed < 80:
            efficiency_factor = 0.85
        else:
            efficiency_factor = 0.7
        
        # Throttle position affects consumption
        throttle_factor = 0.5 + self.throttle * 0.5
        
        effective_mpg = base_mpg * efficiency_factor / throttle_factor
        
        # gph = mph / mpg
        return speed / max(1, effective_mpg)
    
    def _compute_rpm(self, speed: float) -> float:
        """Compute engine RPM from speed and gear"""
        if speed < 1:
            return 800 if self.gear != 0 else 0  # Idle or off
        
        # RPM = (speed * gear_ratio * final_drive * 60) / (tire_circumference)
        tire_radius_m = 0.35
        tire_circum = 2 * math.pi * tire_radius_m
        
        # Gear ratios (typical 6-speed)
        gear_ratios = [0, 3.5, 2.1, 1.4, 1.0, 0.8, 0.65]
        final_drive = 3.5
        
        gear = max(1, min(6, self.gear))
        ratio = gear_ratios[gear] * final_drive
        
        speed_mps = speed * 0.44704
        rpm = (speed_mps * ratio * 60) / tire_circum
        
        return min(7000, max(800, rpm))  # Limit to 800-7000 RPM
    
    def _compute_gear(self, speed: float) -> int:
        """Automatic transmission gear selection"""
        if self.gear == 0:  # Park
            return 0
        if self.gear == -1:  # Reverse
            return -1
        
        # Shift points (mph)
        shift_up = [15, 25, 40, 55, 70, 999]
        shift_down = [10, 18, 30, 45, 60, 80]
        
        current = max(1, self.gear)
        
        # Shift up
        if current < 6 and speed > shift_up[current - 1]:
            return current + 1
        
        # Shift down
        if current > 1 and speed < shift_down[current - 2]:
            return current - 1
        
        return current
    
    def _determine_state(self) -> DriveState:
        """Determine current drive state"""
        if self.gear == 0:
            return DriveState.PARKED
        
        speed = abs(self.velocity.speed)
        
        if speed < 1 and self.throttle < 0.1:
            return DriveState.IDLE
        elif self.brake > 0.1:
            return DriveState.BRAKING
        elif self.throttle > 0.3:
            return DriveState.ACCELERATING
        elif self.throttle > 0.05:
            return DriveState.CRUISING
        else:
            return DriveState.COASTING
    
    # ==========================================================================
    # CONTROL INPUTS
    # ==========================================================================
    
    def set_throttle(self, value: float):
        """Set throttle position (0-1)"""
        self.throttle = max(0, min(1, value))
        if self.gear == 0 and self.throttle > 0:
            self.gear = 1  # Auto-shift to drive
    
    def set_brake(self, value: float):
        """Set brake position (0-1)"""
        self.brake = max(0, min(1, value))
    
    def set_steering(self, value: float):
        """Set steering (-1 to 1, left to right)"""
        self.steering = max(-1, min(1, value))
    
    def shift_gear(self, gear: int):
        """Shift to specific gear"""
        self.gear = max(-1, min(6, gear))
    
    def start_engine(self):
        """Start the engine (shift to idle)"""
        if self.gear == 0:
            self.gear = 1  # Shift to drive
            self.engine_rpm = 800
    
    def stop_engine(self):
        """Stop the engine (shift to park)"""
        if self.velocity.speed < 5:
            self.gear = 0
            self.engine_rpm = 0
    
    def reset_trip(self):
        """Reset trip odometer"""
        self.trip_distance = 0
        self.fuel_consumed = 0
    
    # ==========================================================================
    # SERIALIZATION
    # ==========================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Export full state as dictionary"""
        return {
            "specs": self.specs.to_dict(),
            "position": {
                "distance": self.position.distance,
                "lane_offset": self.position.lane_offset,
                "heading": self.position.heading
            },
            "velocity": {
                "speed": self.velocity.speed,
                "angular_velocity": self.velocity.angular_velocity
            },
            "dashboard": self.get_dashboard(),
            "resources": {
                "fuel_gallons": self.fuel_gallons,
                "fuel_consumed": self.fuel_consumed
            }
        }


# =============================================================================
# CAR SPECS PRESETS
# =============================================================================

class CarPresets:
    """Predefined car configurations"""
    
    @staticmethod
    def economy() -> CarSubstrate:
        """Economy sedan (Toyota Corolla style)"""
        return CarSubstrate.from_api(make="Toyota", model="Corolla", year=2024)
    
    @staticmethod
    def midsize() -> CarSubstrate:
        """Midsize sedan (Toyota Camry style)"""
        return CarSubstrate.from_api(make="Toyota", model="Camry", year=2024)
    
    @staticmethod
    def sports() -> CarSubstrate:
        """Sports car (Porsche 911 style)"""
        return CarSubstrate.from_api(make="Porsche", model="911", year=2024)
    
    @staticmethod
    def muscle() -> CarSubstrate:
        """Muscle car (Ford Mustang style)"""
        return CarSubstrate.from_api(make="Ford", model="Mustang", year=2024)
    
    @staticmethod
    def supercar() -> CarSubstrate:
        """Supercar (Ferrari style)"""
        return CarSubstrate.from_api(make="Ferrari", model="488", year=2024)
    
    @staticmethod
    def electric() -> CarSubstrate:
        """Electric (Tesla style)"""
        return CarSubstrate.from_api(make="Tesla", model="Model3", year=2024)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("Creating Car Substrate...")
    
    # Create a car from API
    car = CarSubstrate.from_api(make="Toyota", model="Camry", year=2024)
    
    print(f"\n{car.specs.year} {car.specs.make} {car.specs.model}")
    print(f"  Power: {car.specs.horsepower}hp")
    print(f"  Weight: {car.specs.weight_lbs}lbs")
    print(f"  MPG: {car.specs.mpg_combined}")
    
    # Start engine and accelerate
    car.start_engine()
    car.set_throttle(0.5)
    
    print("\nSimulating 10 seconds of driving...")
    for i in range(100):  # 100 steps of 0.1s
        car.transform(0.1)
        if i % 20 == 0:
            dash = car.get_dashboard()
            print(f"  t={i/10:.1f}s: {dash['mph']}mph, {dash['rpm']}rpm, gear={dash['gear']}")
    
    print("\nFinal Dashboard:")
    for key, value in car.get_dashboard().items():
        print(f"  {key}: {value}")
