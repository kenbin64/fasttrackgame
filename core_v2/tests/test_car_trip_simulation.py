"""
Test: Car Travels 1 Mile - Dimensional Simulation

═══════════════════════════════════════════════════════════════════
                    FULL VEHICLE PHYSICS SIMULATION
═══════════════════════════════════════════════════════════════════

The car substrate contains:
    - Engine (fuel consumption, RPM, power)
    - Transmission (gears, ratios, efficiency)
    - Wheels/Tires (rubber, wear, rotation)
    - Fuel tank (capacity, consumption)
    - Physics (position, velocity, acceleration)

All these EXIST because the car exists.
We simulate traveling 1 mile and calculate:
    - Fuel consumed
    - Tire rubber worn off

Everything works together through dimensional promotion.

═══════════════════════════════════════════════════════════════════
"""

import sys
from pathlib import Path
import math

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core_v2 import ButterflyFx


# ═══════════════════════════════════════════════════════════════════
# CONSTANTS (exist as mathematical truths)
# ═══════════════════════════════════════════════════════════════════

# Distance
MILE_IN_METERS = 1609.34
MILE_IN_FEET = 5280

# Tire specifications (average passenger car)
TIRE_DIAMETER_INCHES = 26  # ~26 inches for typical tire
TIRE_DIAMETER_METERS = TIRE_DIAMETER_INCHES * 0.0254
TIRE_CIRCUMFERENCE_METERS = math.pi * TIRE_DIAMETER_METERS
TIRE_TREAD_DEPTH_MM = 8.0  # New tire tread depth
TIRE_RUBBER_DENSITY_KG_M3 = 1100  # Rubber density
TIRE_WIDTH_MM = 225  # Common tire width

# Fuel specifications
GASOLINE_DENSITY_KG_L = 0.755
GASOLINE_ENERGY_MJ_L = 34.2

# Road specifications (average paved road)
ROAD_COEFFICIENT_ROLLING_RESISTANCE = 0.015  # Paved asphalt
ROAD_ABRASIVENESS_FACTOR = 1.0  # 1.0 = normal, higher = rougher

# Physics
GRAVITY_M_S2 = 9.81


def create_car():
    """
    Create a fully-specified car substrate.
    All parts EXIST because the car exists.
    """
    fx = ButterflyFx()
    
    car = fx.substrate({
        # Identity
        "make": "Toyota",
        "model": "Camry",
        "year": 2024,
        "vin": "1HGBH41JXMN109186",
        
        # Mass
        "curb_weight_kg": 1500,
        "passenger_weight_kg": 80,
        "cargo_weight_kg": 20,
        
        # Engine
        "engine": {
            "cylinders": 4,
            "displacement_cc": 2500,
            "max_power_hp": 203,
            "max_torque_nm": 250,
            "idle_rpm": 800,
            "redline_rpm": 6500,
            "thermal_efficiency": 0.35,  # 35% efficient (typical gasoline)
            "current_rpm": 0,
        },
        
        # Transmission
        "transmission": {
            "type": "automatic",
            "gears": 8,
            "current_gear": 0,  # 0 = Park
            "gear_ratios": {
                1: 4.71,
                2: 3.14,
                3: 2.11,
                4: 1.67,
                5: 1.29,
                6: 1.00,
                7: 0.84,
                8: 0.67,
            },
            "final_drive_ratio": 3.42,
            "efficiency": 0.94,  # 94% efficient
        },
        
        # Fuel system
        "fuel": {
            "tank_capacity_liters": 60,
            "current_level_liters": 45,
            "fuel_type": "gasoline",
            "consumption_rate_L_100km": 7.5,  # Average consumption
        },
        
        # Wheels and tires (all 4)
        "wheels": {
            "count": 4,
            "tire_diameter_m": TIRE_DIAMETER_METERS,
            "tire_width_mm": TIRE_WIDTH_MM,
            "tire_circumference_m": TIRE_CIRCUMFERENCE_METERS,
            "tread_depth_mm": TIRE_TREAD_DEPTH_MM,
            "rubber_compound": "all_season",
            "pressure_psi": 35,
            "rotations": 0,
        },
        
        # Physics state
        "physics": {
            "position_m": 0,
            "velocity_m_s": 0,
            "acceleration_m_s2": 0,
            "heading_degrees": 0,
        },
        
        # Driving conditions
        "conditions": {
            "road_type": "paved_asphalt",
            "road_condition": "dry",
            "ambient_temp_c": 20,
            "grade_percent": 0,  # Flat road
        },
    })
    
    return fx, car


def calculate_fuel_consumption(car, distance_m, avg_speed_m_s):
    """
    Calculate fuel consumed for a distance.
    
    Fuel consumption EXISTS because the engine, transmission, and physics exist.
    """
    # Get car properties (they exist because car exists)
    weight_kg = (
        car.lens("curb_weight_kg").invoke() +
        car.lens("passenger_weight_kg").invoke() +
        car.lens("cargo_weight_kg").invoke()
    )
    
    consumption_L_100km = car.lens("fuel.consumption_rate_L_100km").invoke()
    thermal_efficiency = car.lens("engine.thermal_efficiency").invoke()
    trans_efficiency = car.lens("transmission.efficiency").invoke()
    
    # Convert distance to km
    distance_km = distance_m / 1000
    
    # Base fuel consumption
    base_consumption_L = (consumption_L_100km / 100) * distance_km
    
    # Adjust for rolling resistance force
    rolling_resistance_N = ROAD_COEFFICIENT_ROLLING_RESISTANCE * weight_kg * GRAVITY_M_S2
    
    # Energy needed to overcome rolling resistance
    rolling_energy_J = rolling_resistance_N * distance_m
    rolling_energy_MJ = rolling_energy_J / 1_000_000
    
    # Additional fuel for rolling resistance
    additional_fuel_L = rolling_energy_MJ / (GASOLINE_ENERGY_MJ_L * thermal_efficiency * trans_efficiency)
    
    # Total fuel
    total_fuel_L = base_consumption_L + additional_fuel_L
    
    return {
        "distance_m": distance_m,
        "distance_miles": distance_m / MILE_IN_METERS,
        "base_consumption_L": base_consumption_L,
        "rolling_resistance_N": rolling_resistance_N,
        "rolling_energy_MJ": rolling_energy_MJ,
        "additional_fuel_L": additional_fuel_L,
        "total_fuel_L": total_fuel_L,
        "total_fuel_gallons": total_fuel_L / 3.78541,
        "fuel_economy_mpg": (distance_m / MILE_IN_METERS) / (total_fuel_L / 3.78541),
    }


def calculate_tire_wear(car, distance_m, avg_speed_m_s):
    """
    Calculate tire rubber wear for a distance.
    
    Tire wear EXISTS because the wheels, physics, and road conditions exist.
    """
    # Get tire properties (they exist because car exists)
    tire_circumference = car.lens("wheels.tire_circumference_m").invoke()
    tire_width_mm = car.lens("wheels.tire_width_mm").invoke()
    tread_depth_mm = car.lens("wheels.tread_depth_mm").invoke()
    wheel_count = car.lens("wheels.count").invoke()
    
    # Get car weight
    weight_kg = (
        car.lens("curb_weight_kg").invoke() +
        car.lens("passenger_weight_kg").invoke() +
        car.lens("cargo_weight_kg").invoke()
    )
    
    # Calculate rotations
    rotations = distance_m / tire_circumference
    rotations_per_tire = rotations  # Each tire rotates the same
    
    # Tire wear model (empirical)
    # Average tire lasts ~60,000 miles and loses ~6mm of tread
    TIRE_LIFE_MILES = 60000
    TIRE_LIFE_METERS = TIRE_LIFE_MILES * MILE_IN_METERS
    TREAD_WEAR_MM = 6.0  # mm worn over tire life
    
    # Linear wear rate (mm per meter traveled)
    wear_rate_mm_per_m = TREAD_WEAR_MM / TIRE_LIFE_METERS
    
    # Wear for this distance
    tread_wear_mm = wear_rate_mm_per_m * distance_m
    
    # Adjust for speed (higher speed = more wear)
    # Every 10 mph over 30 increases wear by 10%
    speed_mph = avg_speed_m_s * 2.237
    speed_factor = 1.0 + max(0, (speed_mph - 30) / 100)
    
    # Adjust for road abrasiveness
    abrasiveness_factor = ROAD_ABRASIVENESS_FACTOR
    
    # Adjusted wear
    adjusted_wear_mm = tread_wear_mm * speed_factor * abrasiveness_factor
    
    # Calculate rubber volume lost
    # Approximate tread contact as a rectangular strip
    # Contact patch width ≈ tire width, length depends on deformation
    contact_patch_length_mm = 150  # Approximate
    contact_area_mm2 = tire_width_mm * contact_patch_length_mm
    
    # Volume lost (mm³) = area × depth worn
    rubber_volume_per_tire_mm3 = contact_area_mm2 * adjusted_wear_mm
    
    # Convert to cubic meters
    rubber_volume_per_tire_m3 = rubber_volume_per_tire_mm3 / 1e9
    
    # Mass lost (all 4 tires)
    rubber_mass_per_tire_kg = rubber_volume_per_tire_m3 * TIRE_RUBBER_DENSITY_KG_M3
    total_rubber_mass_kg = rubber_mass_per_tire_kg * wheel_count
    
    # Convert to grams for readability
    total_rubber_mass_g = total_rubber_mass_kg * 1000
    
    return {
        "distance_m": distance_m,
        "distance_miles": distance_m / MILE_IN_METERS,
        "tire_rotations": rotations_per_tire,
        "wear_rate_mm_per_km": wear_rate_mm_per_m * 1000,
        "tread_wear_mm": adjusted_wear_mm,
        "speed_factor": speed_factor,
        "abrasiveness_factor": abrasiveness_factor,
        "rubber_volume_per_tire_mm3": rubber_volume_per_tire_mm3,
        "rubber_mass_per_tire_g": rubber_mass_per_tire_kg * 1000,
        "total_rubber_mass_g": total_rubber_mass_g,
        "remaining_tread_mm": tread_depth_mm - adjusted_wear_mm,
        "tire_life_used_percent": (adjusted_wear_mm / TREAD_WEAR_MM) * 100,
    }


def simulate_1_mile_trip():
    """
    Simulate a car traveling exactly 1 mile.
    
    All components work together:
    - Engine burns fuel
    - Transmission transfers power
    - Wheels rotate and wear
    - Physics tracks position
    """
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " SIMULATING: CAR TRAVELS 1 MILE ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    # Create the car (all parts exist)
    fx, car = create_car()
    
    # Trip parameters
    distance_m = MILE_IN_METERS  # Exactly 1 mile
    avg_speed_mph = 35  # Average city driving
    avg_speed_m_s = avg_speed_mph * 0.44704
    travel_time_s = distance_m / avg_speed_m_s
    
    print("=" * 60)
    print("TRIP PARAMETERS")
    print("=" * 60)
    print(f"  Distance: 1 mile ({distance_m:.2f} meters)")
    print(f"  Average Speed: {avg_speed_mph} mph ({avg_speed_m_s:.2f} m/s)")
    print(f"  Travel Time: {travel_time_s:.1f} seconds ({travel_time_s/60:.2f} minutes)")
    print()
    
    # ─────────────────────────────────────────────────────────────
    # SHOW THAT ALL PARTS EXIST (because the car exists)
    # ─────────────────────────────────────────────────────────────
    print("=" * 60)
    print("CAR COMPONENTS (all exist because CAR exists)")
    print("=" * 60)
    
    print(f"\nCar Identity: 0x{car.truth:016X}")
    print(f"  Make: {car.lens('make').invoke()}")
    print(f"  Model: {car.lens('model').invoke()}")
    
    print(f"\nEngine (exists because car exists):")
    print(f"  Cylinders: {car.lens('engine.cylinders').invoke()}")
    print(f"  Displacement: {car.lens('engine.displacement_cc').invoke()} cc")
    print(f"  Max Power: {car.lens('engine.max_power_hp').invoke()} hp")
    print(f"  Thermal Efficiency: {car.lens('engine.thermal_efficiency').invoke() * 100:.0f}%")
    
    print(f"\nTransmission (exists because car exists):")
    print(f"  Gears: {car.lens('transmission.gears').invoke()}")
    print(f"  Type: {car.lens('transmission.type').invoke()}")
    print(f"  Efficiency: {car.lens('transmission.efficiency').invoke() * 100:.0f}%")
    
    print(f"\nFuel System (exists because car exists):")
    print(f"  Tank Capacity: {car.lens('fuel.tank_capacity_liters').invoke()} L")
    print(f"  Current Level: {car.lens('fuel.current_level_liters').invoke()} L")
    print(f"  Base Consumption: {car.lens('fuel.consumption_rate_L_100km').invoke()} L/100km")
    
    print(f"\nWheels/Tires (exist because car exists):")
    print(f"  Count: {car.lens('wheels.count').invoke()}")
    print(f"  Diameter: {car.lens('wheels.tire_diameter_m').invoke():.4f} m ({TIRE_DIAMETER_INCHES} inches)")
    print(f"  Width: {car.lens('wheels.tire_width_mm').invoke()} mm")
    print(f"  Tread Depth: {car.lens('wheels.tread_depth_mm').invoke()} mm")
    
    print(f"\nRoad Conditions (exist because conditions exist):")
    print(f"  Surface: {car.lens('conditions.road_type').invoke()}")
    print(f"  Condition: {car.lens('conditions.road_condition').invoke()}")
    print(f"  Rolling Resistance Coefficient: {ROAD_COEFFICIENT_ROLLING_RESISTANCE}")
    print()
    
    # ─────────────────────────────────────────────────────────────
    # CALCULATE FUEL CONSUMPTION
    # ─────────────────────────────────────────────────────────────
    print("=" * 60)
    print("FUEL CONSUMPTION ANALYSIS")
    print("=" * 60)
    
    fuel_result = calculate_fuel_consumption(car, distance_m, avg_speed_m_s)
    
    print(f"\n  Distance traveled: {fuel_result['distance_miles']:.3f} miles")
    print(f"  Base consumption: {fuel_result['base_consumption_L']*1000:.2f} mL")
    print(f"  Rolling resistance force: {fuel_result['rolling_resistance_N']:.1f} N")
    print(f"  Energy to overcome resistance: {fuel_result['rolling_energy_MJ']*1000:.2f} kJ")
    print(f"  Additional fuel for resistance: {fuel_result['additional_fuel_L']*1000:.2f} mL")
    print()
    print(f"  ┌{'─'*40}┐")
    print(f"  │ TOTAL FUEL CONSUMED: {fuel_result['total_fuel_L']*1000:>12.2f} mL │")
    print(f"  │                      {fuel_result['total_fuel_gallons']*128:>12.2f} fl oz │")
    print(f"  │ Fuel Economy:        {fuel_result['fuel_economy_mpg']:>12.1f} mpg │")
    print(f"  └{'─'*40}┘")
    print()
    
    # ─────────────────────────────────────────────────────────────
    # CALCULATE TIRE WEAR
    # ─────────────────────────────────────────────────────────────
    print("=" * 60)
    print("TIRE WEAR ANALYSIS")
    print("=" * 60)
    
    tire_result = calculate_tire_wear(car, distance_m, avg_speed_m_s)
    
    print(f"\n  Tire Rotations: {tire_result['tire_rotations']:.1f} per tire")
    print(f"  Wear Rate: {tire_result['wear_rate_mm_per_km']:.6f} mm/km")
    print(f"  Speed Factor: {tire_result['speed_factor']:.2f}x")
    print(f"  Road Abrasiveness: {tire_result['abrasiveness_factor']:.1f}x")
    print(f"  Tread Wear: {tire_result['tread_wear_mm']*1000:.4f} µm (micrometers)")
    print()
    print(f"  Rubber lost per tire: {tire_result['rubber_volume_per_tire_mm3']:.4f} mm³")
    print(f"                        {tire_result['rubber_mass_per_tire_g']*1000:.4f} mg")
    print()
    print(f"  ┌{'─'*44}┐")
    print(f"  │ TOTAL RUBBER WORN (4 tires): {tire_result['total_rubber_mass_g']*1000:>8.4f} mg │")
    print(f"  │ Remaining Tread:             {tire_result['remaining_tread_mm']:>8.4f} mm │")
    print(f"  │ Tire Life Used:              {tire_result['tire_life_used_percent']:>8.6f} %  │")
    print(f"  └{'─'*44}┘")
    print()
    
    # ─────────────────────────────────────────────────────────────
    # SUMMARY
    # ─────────────────────────────────────────────────────────────
    print("=" * 60)
    print("TRIP SUMMARY")
    print("=" * 60)
    print()
    print(f"  Car traveled: 1 mile at {avg_speed_mph} mph average")
    print(f"  Time elapsed: {travel_time_s/60:.2f} minutes")
    print()
    fuel_str = f"{fuel_result['total_fuel_L']*1000:.2f} mL ({fuel_result['total_fuel_gallons']*128:.2f} fl oz)"
    rubber_str = f"{tire_result['total_rubber_mass_g']*1000:.4f} milligrams"
    print(f"  ╔{'═'*50}╗")
    print(f"  ║{'FUEL CONSUMED:':^50}║")
    print(f"  ║{fuel_str:^50}║")
    print(f"  ╠{'═'*50}╣")
    print(f"  ║{'RUBBER WORN OFF (all 4 tires):':^50}║")
    print(f"  ║{rubber_str:^50}║")
    print(f"  ╚{'═'*50}╝")
    print()
    
    # ─────────────────────────────────────────────────────────────
    # PROVE DIMENSIONAL PROMOTION
    # ─────────────────────────────────────────────────────────────
    print("=" * 60)
    print("DIMENSIONAL PROMOTION (state changes)")
    print("=" * 60)
    print()
    
    # Calculate new fuel level
    original_fuel = car.lens("fuel.current_level_liters").invoke()
    new_fuel = original_fuel - fuel_result['total_fuel_L']
    
    # Calculate new tread depth
    original_tread = car.lens("wheels.tread_depth_mm").invoke()
    new_tread = original_tread - tire_result['tread_wear_mm']
    
    # Create delta for state change
    trip_delta = fx.delta({
        "distance_traveled_m": distance_m,
        "fuel_consumed_L": fuel_result['total_fuel_L'],
        "rubber_worn_g": tire_result['total_rubber_mass_g'],
        "tire_rotations": tire_result['tire_rotations'],
    })
    
    # Promote car to new state
    car_after_trip = car.promote(trip_delta)
    
    print(f"  Original car identity: 0x{car.truth:016X}")
    print(f"  After trip identity:   0x{car_after_trip.truth:016X}")
    print(f"  (New substrate - original unchanged)")
    print()
    print(f"  State Changes:")
    print(f"    Fuel: {original_fuel:.2f} L → {new_fuel:.2f} L (-{fuel_result['total_fuel_L']*1000:.2f} mL)")
    print(f"    Tread: {original_tread:.4f} mm → {new_tread:.6f} mm (-{tire_result['tread_wear_mm']*1000:.4f} µm)")
    print(f"    Position: 0 → {distance_m:.2f} m")
    print()
    
    return fuel_result, tire_result


def main():
    """Run the simulation."""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " DIMENSIONAL PROGRAMMING: VEHICLE PHYSICS ".center(58) + "║")
    print("║" + " All components exist because the CAR exists ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    
    fuel_result, tire_result = simulate_1_mile_trip()
    
    print("=" * 60)
    print("PROOF OF DIMENSIONAL EXISTENCE")
    print("=" * 60)
    print()
    print("  1. We created ONE substrate: the car")
    print("  2. Engine, transmission, fuel, wheels ALL EXIST")
    print("     because the car exists")
    print("  3. Fuel consumption EXISTS (calculated from engine, trans, physics)")
    print("  4. Tire wear EXISTS (calculated from wheels, road, physics)")
    print("  5. No iteration through dimensions — just INVOKE what exists")
    print()
    print("  THE ONE RULE:")
    print("  A higher dimension IS a single point of all lower dimensions.")
    print("  The car at 4D (behavioral) IS the moving car with all parts.")
    print()
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
