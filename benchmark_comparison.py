"""
Computational Comparison: Dimensional vs Traditional Programming

═══════════════════════════════════════════════════════════════════
This benchmark compares:
    1. DIMENSIONAL (ButterflyFx) - Invoke what exists
    2. TRADITIONAL (OOP/Imperative) - Iterate and compute each step
═══════════════════════════════════════════════════════════════════
"""

import time
import tracemalloc
import math
import sys
from dataclasses import dataclass
from typing import List

sys.path.insert(0, '.')

# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════

MILE_IN_METERS = 1609.34
TIRE_DIAMETER_METERS = 0.6604
TIRE_CIRCUMFERENCE = math.pi * TIRE_DIAMETER_METERS
TIRE_LIFE_MILES = 60000
TREAD_WEAR_MM = 6.0


# ═══════════════════════════════════════════════════════════════════
# TRADITIONAL APPROACH: Object-Oriented with State Iteration
# ═══════════════════════════════════════════════════════════════════

@dataclass
class TraditionalEngine:
    cylinders: int
    displacement_cc: int
    thermal_efficiency: float
    current_rpm: float = 0

@dataclass
class TraditionalTransmission:
    gears: int
    current_gear: int
    efficiency: float
    gear_ratios: List[float] = None

@dataclass  
class TraditionalWheel:
    diameter_m: float
    tread_depth_mm: float
    rotations: float = 0
    rubber_worn_g: float = 0

@dataclass
class TraditionalFuelTank:
    capacity_L: float
    current_L: float
    consumed_L: float = 0

@dataclass
class TraditionalCar:
    """Traditional OOP car with mutable state."""
    engine: TraditionalEngine
    transmission: TraditionalTransmission
    wheels: List[TraditionalWheel]
    fuel: TraditionalFuelTank
    mass_kg: float
    position_m: float = 0
    velocity_m_s: float = 0


def traditional_simulation(distance_m: float, avg_speed_m_s: float, time_step: float = 0.1):
    """
    Traditional simulation: iterate through each time step.
    Updates state at every step. Mutates objects.
    """
    # Create car with mutable state
    car = TraditionalCar(
        engine=TraditionalEngine(
            cylinders=4,
            displacement_cc=2500,
            thermal_efficiency=0.35,
        ),
        transmission=TraditionalTransmission(
            gears=8,
            current_gear=4,
            efficiency=0.94,
            gear_ratios=[4.71, 3.14, 2.11, 1.67, 1.29, 1.00, 0.84, 0.67],
        ),
        wheels=[
            TraditionalWheel(diameter_m=TIRE_DIAMETER_METERS, tread_depth_mm=8.0)
            for _ in range(4)
        ],
        fuel=TraditionalFuelTank(capacity_L=60, current_L=45),
        mass_kg=1600,
    )
    
    # Simulation parameters
    total_time = distance_m / avg_speed_m_s
    current_time = 0
    iterations = 0
    
    # Consumption rates (per second at this speed)
    consumption_rate_L_100km = 7.5
    consumption_per_meter = consumption_rate_L_100km / 100000
    
    wear_rate_mm_per_m = TREAD_WEAR_MM / (TIRE_LIFE_MILES * MILE_IN_METERS)
    
    # ITERATE through each time step (traditional approach)
    while current_time < total_time:
        iterations += 1
        dt = min(time_step, total_time - current_time)
        
        # Update position
        distance_step = avg_speed_m_s * dt
        car.position_m += distance_step
        
        # Update each wheel (iterate through all 4)
        for wheel in car.wheels:
            # Calculate rotations this step
            rotations = distance_step / TIRE_CIRCUMFERENCE
            wheel.rotations += rotations
            
            # Calculate wear this step
            wear_mm = wear_rate_mm_per_m * distance_step * 1.05  # speed factor
            wheel.tread_depth_mm -= wear_mm
            
            # Calculate rubber mass lost (simplified)
            rubber_volume_mm3 = 225 * 150 * wear_mm  # width * patch * depth
            rubber_mass_g = rubber_volume_mm3 * 1100 / 1e9  # density conversion
            wheel.rubber_worn_g += rubber_mass_g
        
        # Update fuel consumption
        fuel_consumed = consumption_per_meter * distance_step
        
        # Add rolling resistance fuel
        rolling_force = 0.015 * car.mass_kg * 9.81
        rolling_energy_J = rolling_force * distance_step
        additional_fuel = rolling_energy_J / (34.2e6 * car.engine.thermal_efficiency * car.transmission.efficiency)
        
        total_fuel_step = fuel_consumed + additional_fuel
        car.fuel.current_L -= total_fuel_step
        car.fuel.consumed_L += total_fuel_step
        
        # Update engine RPM (simulate gear/speed relationship)
        car.engine.current_rpm = (avg_speed_m_s * 60 / TIRE_CIRCUMFERENCE) * car.transmission.gear_ratios[car.transmission.current_gear - 1] * 3.42
        
        current_time += dt
    
    # Sum up results
    total_rubber_g = sum(w.rubber_worn_g for w in car.wheels)
    total_rotations = car.wheels[0].rotations
    
    return {
        'iterations': iterations,
        'fuel_consumed_mL': car.fuel.consumed_L * 1000,
        'rubber_worn_mg': total_rubber_g * 1000,
        'tire_rotations': total_rotations,
        'position_m': car.position_m,
    }


# ═══════════════════════════════════════════════════════════════════
# DIMENSIONAL APPROACH: Invoke What Exists
# ═══════════════════════════════════════════════════════════════════

def dimensional_simulation(distance_m: float, avg_speed_m_s: float):
    """
    Dimensional simulation: invoke mathematical relationships.
    No iteration. No mutation. Just reveal what exists.
    """
    from core_v2 import ButterflyFx
    
    fx = ButterflyFx()
    
    # Create ONE substrate - everything exists because the car exists
    car = fx.substrate({
        "mass_kg": 1600,
        "engine": {"thermal_efficiency": 0.35},
        "transmission": {"efficiency": 0.94},
        "fuel": {"consumption_rate_L_100km": 7.5},
        "wheels": {"tread_depth_mm": 8.0, "count": 4},
    })
    
    # These values EXIST - we just invoke them
    mass_kg = car.lens("mass_kg").invoke()
    thermal_eff = car.lens("engine.thermal_efficiency").invoke()
    trans_eff = car.lens("transmission.efficiency").invoke()
    consumption_rate = car.lens("fuel.consumption_rate_L_100km").invoke()
    
    # Calculate fuel (no iteration - mathematical relationship)
    distance_km = distance_m / 1000
    base_fuel_L = (consumption_rate / 100) * distance_km
    
    rolling_force = 0.015 * mass_kg * 9.81
    rolling_energy_MJ = (rolling_force * distance_m) / 1e6
    additional_fuel_L = rolling_energy_MJ / (34.2 * thermal_eff * trans_eff)
    
    total_fuel_L = base_fuel_L + additional_fuel_L
    
    # Calculate tire wear (no iteration - the relationship exists)
    rotations = distance_m / TIRE_CIRCUMFERENCE
    wear_rate_mm_per_m = TREAD_WEAR_MM / (TIRE_LIFE_MILES * MILE_IN_METERS)
    tread_wear_mm = wear_rate_mm_per_m * distance_m * 1.05  # speed factor
    
    # Rubber volume from the relationship
    rubber_volume_per_tire_mm3 = 225 * 150 * tread_wear_mm
    rubber_mass_per_tire_g = rubber_volume_per_tire_mm3 * 1100 / 1e9
    total_rubber_g = rubber_mass_per_tire_g * 4
    
    return {
        'iterations': 1,  # Just ONE invocation
        'fuel_consumed_mL': total_fuel_L * 1000,
        'rubber_worn_mg': total_rubber_g * 1000,
        'tire_rotations': rotations,
        'position_m': distance_m,
    }


# ═══════════════════════════════════════════════════════════════════
# BENCHMARK
# ═══════════════════════════════════════════════════════════════════

def run_benchmark():
    """Run both simulations and compare."""
    
    distance = MILE_IN_METERS
    speed = 15.65  # 35 mph
    
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " COMPUTATIONAL COMPARISON: DIMENSIONAL vs TRADITIONAL ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    # ─────────────────────────────────────────────────────────────
    # TRADITIONAL (0.1s timestep = ~10 iterations/second)
    # ─────────────────────────────────────────────────────────────
    print("=" * 60)
    print("TRADITIONAL SIMULATION (iterate every 0.1s)")
    print("=" * 60)
    
    tracemalloc.start()
    start = time.perf_counter()
    
    trad_result = traditional_simulation(distance, speed, time_step=0.1)
    
    trad_time = time.perf_counter() - start
    trad_current, trad_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"  Iterations:       {trad_result['iterations']}")
    print(f"  Time:             {trad_time*1000:.3f} ms")
    print(f"  Memory (peak):    {trad_peak/1024:.2f} KB")
    print(f"  Fuel consumed:    {trad_result['fuel_consumed_mL']:.2f} mL")
    print(f"  Rubber worn:      {trad_result['rubber_worn_mg']:.4f} mg")
    print()
    
    # ─────────────────────────────────────────────────────────────
    # TRADITIONAL (0.001s timestep = 1000 iterations/second)
    # More precise but more expensive
    # ─────────────────────────────────────────────────────────────
    print("=" * 60)
    print("TRADITIONAL SIMULATION (iterate every 0.001s - higher precision)")
    print("=" * 60)
    
    tracemalloc.start()
    start = time.perf_counter()
    
    trad_precise = traditional_simulation(distance, speed, time_step=0.001)
    
    trad_precise_time = time.perf_counter() - start
    trad_precise_curr, trad_precise_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"  Iterations:       {trad_precise['iterations']}")
    print(f"  Time:             {trad_precise_time*1000:.3f} ms")
    print(f"  Memory (peak):    {trad_precise_peak/1024:.2f} KB")
    print(f"  Fuel consumed:    {trad_precise['fuel_consumed_mL']:.2f} mL")
    print(f"  Rubber worn:      {trad_precise['rubber_worn_mg']:.4f} mg")
    print()
    
    # ─────────────────────────────────────────────────────────────
    # DIMENSIONAL (no iteration)
    # ─────────────────────────────────────────────────────────────
    print("=" * 60)
    print("DIMENSIONAL SIMULATION (invoke - no iteration)")
    print("=" * 60)
    
    tracemalloc.start()
    start = time.perf_counter()
    
    dim_result = dimensional_simulation(distance, speed)
    
    dim_time = time.perf_counter() - start
    dim_current, dim_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"  Iterations:       {dim_result['iterations']} (just invoke)")
    print(f"  Time:             {dim_time*1000:.3f} ms")
    print(f"  Memory (peak):    {dim_peak/1024:.2f} KB")
    print(f"  Fuel consumed:    {dim_result['fuel_consumed_mL']:.2f} mL")
    print(f"  Rubber worn:      {dim_result['rubber_worn_mg']:.4f} mg")
    print()
    
    # ─────────────────────────────────────────────────────────────
    # COMPARISON
    # ─────────────────────────────────────────────────────────────
    print("=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    print()
    print("                           Traditional    Trad (precise)    Dimensional")
    print("                           -----------    --------------    -----------")
    print(f"  Iterations:              {trad_result['iterations']:>11}    {trad_precise['iterations']:>14}    {dim_result['iterations']:>11}")
    print(f"  Time (ms):               {trad_time*1000:>11.3f}    {trad_precise_time*1000:>14.3f}    {dim_time*1000:>11.3f}")
    print(f"  Memory (KB):             {trad_peak/1024:>11.2f}    {trad_precise_peak/1024:>14.2f}    {dim_peak/1024:>11.2f}")
    print()
    
    # Speed comparisons
    speedup_vs_trad = trad_time / dim_time if dim_time > 0 else float('inf')
    speedup_vs_precise = trad_precise_time / dim_time if dim_time > 0 else float('inf')
    
    print(f"  ┌{'─'*56}┐")
    print(f"  │{'SPEEDUP':^56}│")
    print(f"  ├{'─'*56}┤")
    print(f"  │  Dimensional vs Traditional (0.1s step): {speedup_vs_trad:>7.1f}x faster  │")
    print(f"  │  Dimensional vs Traditional (0.001s):    {speedup_vs_precise:>7.1f}x faster  │")
    print(f"  └{'─'*56}┘")
    print()
    
    # Scalability demonstration
    print("=" * 60)
    print("SCALABILITY: 100 MILES vs 1 MILE")
    print("=" * 60)
    print()
    
    # Traditional scales with distance (more iterations)
    tracemalloc.start()
    start = time.perf_counter()
    trad_100 = traditional_simulation(distance * 100, speed, time_step=0.1)
    trad_100_time = time.perf_counter() - start
    _, trad_100_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Dimensional is constant (no iteration)
    tracemalloc.start()
    start = time.perf_counter()
    dim_100 = dimensional_simulation(distance * 100, speed)
    dim_100_time = time.perf_counter() - start
    _, dim_100_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"  100 Miles Traditional:  {trad_100['iterations']} iterations, {trad_100_time*1000:.2f} ms")
    print(f"  100 Miles Dimensional:  {dim_100['iterations']} invocation,  {dim_100_time*1000:.2f} ms")
    print()
    print(f"  Traditional time scales linearly: 1mi→100mi = {trad_100_time/trad_time:.1f}x time")
    print(f"  Dimensional time is CONSTANT:     1mi→100mi = {dim_100_time/dim_time:.1f}x time")
    print()
    
    print("=" * 60)
    print("WHY DIMENSIONAL IS FUNDAMENTALLY DIFFERENT")
    print("=" * 60)
    print("""
  TRADITIONAL:
    - Creates objects with mutable state
    - Iterates through time steps (10, 100, 1000+ loops)
    - Updates each wheel separately (×4 per step)
    - Accumulates values step by step
    - More precision = more iterations = more time
    - Linear complexity: O(n) where n = steps

  DIMENSIONAL:
    - Creates ONE substrate (the car)
    - ALL parts EXIST because the car exists
    - Invokes mathematical relationships directly
    - No loops, no accumulation, no mutation
    - Precision is mathematical, not iterative
    - Constant complexity: O(1) - just invoke

  THE ONE RULE:
    A higher dimension IS a single point of all lower dimensions.
    The fuel consumption ALREADY EXISTS as a relationship.
    The tire wear ALREADY EXISTS as a relationship.
    We don't compute them step-by-step — we INVOKE them.
""")


if __name__ == "__main__":
    run_benchmark()
