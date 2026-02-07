"""
Example: Creating Substrates with Infinite Attributes

This demonstrates how substrates contain EVERY CONCEIVABLE ATTRIBUTE,
but attributes only manifest when invoked.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kernel.substrate import Substrate, SubstrateIdentity


def create_car_substrate():
    """
    Create a car substrate where EVERY car attribute exists.
    
    Only identity and name are explicit.
    Everything else exists because the car exists.
    """
    
    # The car's mathematical expression
    # This can compute ANY attribute about the car
    def car_expression(**kwargs):
        """
        The complete mathematical definition of this car.
        Can compute ANY attribute - infinite detail.
        """
        attribute = kwargs.get('attribute', 'identity')
        
        # 1D Attributes (basic properties)
        if attribute == 'vin':
            return hash("1HGBH41JXMN109186") & 0xFFFFFFFFFFFFFFFF
        elif attribute == 'year':
            return 2024
        elif attribute == 'make':
            return hash("Toyota") & 0xFFFFFFFFFFFFFFFF
        elif attribute == 'model':
            return hash("Camry") & 0xFFFFFFFFFFFFFFFF
        elif attribute == 'mileage':
            return 15000
        elif attribute == 'color':
            return 0xFF0000  # Red (RGB)
        
        # Engine attributes (detailed)
        elif attribute == 'engine_displacement':
            return 2500  # 2.5L in cc
        elif attribute == 'horsepower':
            return 203
        elif attribute == 'cylinders':
            return 4
        elif attribute == 'spark_plug_gap':
            return 110  # 1.1mm in 0.01mm units
        
        # Tire attributes (very detailed)
        elif attribute == 'tire_pressure_front_left':
            return 32  # PSI
        elif attribute == 'tire_pressure_front_right':
            return 32
        elif attribute == 'tire_tread_depth_front_left':
            return 8  # mm
        
        # Atomic level (extreme detail)
        elif attribute == 'carbon_atoms_in_engine_block':
            # Estimate: ~10kg of iron/aluminum, ~10^25 atoms
            return 10**25 & 0xFFFFFFFFFFFFFFFF
        elif attribute == 'tire_rubber_molecular_weight':
            return 100000  # Daltons
        
        # Computed attributes (derived from others)
        elif attribute == 'age_years':
            return 2026 - car_expression(attribute='year')
        elif attribute == 'value_usd':
            # Depreciation: $25000 - ($2000 * age)
            age = car_expression(attribute='age_years')
            return 25000 - (2000 * age)
        
        # Default: hash the attribute name
        # This ensures EVERY conceivable attribute exists
        return hash(f"car_{attribute}") & 0xFFFFFFFFFFFFFFFF
    
    # Create the substrate
    identity = hash("Car:Toyota:Camry:2024") & 0xFFFFFFFFFFFFFFFF
    substrate_id = SubstrateIdentity(identity)
    
    return Substrate(substrate_id, car_expression)


def create_person_substrate():
    """
    Create a person substrate where EVERY person attribute exists.
    Including DNA, memories, atomic composition, etc.
    """
    
    def person_expression(**kwargs):
        """Complete mathematical definition of a person."""
        attribute = kwargs.get('attribute', 'identity')
        
        # Basic attributes
        if attribute == 'name':
            return hash("Alice") & 0xFFFFFFFFFFFFFFFF
        elif attribute == 'birth_timestamp':
            return 946684800  # Jan 1, 2000
        elif attribute == 'height_cm':
            return 165
        elif attribute == 'weight_kg':
            return 60
        
        # Biological attributes
        elif attribute == 'blood_type':
            return hash("O+") & 0xFFFFFFFFFFFFFFFF
        elif attribute == 'dna_base_pairs':
            return 3_000_000_000  # 3 billion
        elif attribute == 'neuron_count':
            return 86_000_000_000  # 86 billion
        
        # Atomic level
        elif attribute == 'total_atoms':
            return 7 * (10**27) & 0xFFFFFFFFFFFFFFFF  # 7 octillion
        elif attribute == 'carbon_atoms':
            return int(0.18 * 7 * (10**27)) & 0xFFFFFFFFFFFFFFFF
        
        # Computed attributes
        elif attribute == 'age_seconds':
            import time
            return int(time.time()) - person_expression(attribute='birth_timestamp')
        elif attribute == 'age_years':
            return person_expression(attribute='age_seconds') // 31536000
        
        # Memory/cognitive (hypothetical encoding)
        elif attribute == 'memory_at_age_5':
            return hash("childhood_memories") & 0xFFFFFFFFFFFFFFFF
        elif attribute == 'personality_openness':
            return 75  # 0-100 scale
        
        # Default
        return hash(f"person_{attribute}") & 0xFFFFFFFFFFFFFFFF
    
    identity = hash("Person:Alice:946684800") & 0xFFFFFFFFFFFFFFFF
    substrate_id = SubstrateIdentity(identity)
    
    return Substrate(substrate_id, person_expression)


def main():
    """Demonstrate infinite attributes."""
    
    print("=" * 70)
    print("SUBSTRATE INFINITE ATTRIBUTES DEMONSTRATION")
    print("=" * 70)
    print()
    
    # Create car substrate
    print("Creating car substrate...")
    car = create_car_substrate()
    print(f"Car substrate: {car}")
    print(f"Identity: {car.identity}")
    print()
    
    # Manifest various attributes
    print("Manifesting car attributes (they exist, now they appear):")
    print(f"  VIN: {car.invoke(attribute='vin'):016X}")
    print(f"  Year: {car.invoke(attribute='year')}")
    print(f"  Mileage: {car.invoke(attribute='mileage'):,}")
    print(f"  Horsepower: {car.invoke(attribute='horsepower')}")
    print(f"  Tire pressure (FL): {car.invoke(attribute='tire_pressure_front_left')} PSI")
    print(f"  Carbon atoms in engine: {car.invoke(attribute='carbon_atoms_in_engine_block'):.2e}")
    print(f"  Age (years): {car.invoke(attribute='age_years')}")
    print(f"  Value (USD): ${car.invoke(attribute='value_usd'):,}")
    print()
    
    # Manifest attributes that were never explicitly defined
    print("Manifesting attributes that were NEVER explicitly defined:")
    print(f"  Windshield wiper speed: {car.invoke(attribute='windshield_wiper_speed'):016X}")
    print(f"  Radio frequency: {car.invoke(attribute='radio_frequency'):016X}")
    print(f"  Seat fabric thread count: {car.invoke(attribute='seat_fabric_thread_count'):016X}")
    print("  ^ These exist because the car exists!")
    print()
    
    # Create person substrate
    print("Creating person substrate...")
    person = create_person_substrate()
    print(f"Person substrate: {person}")
    print()
    
    # Manifest person attributes
    print("Manifesting person attributes:")
    print(f"  Name: {person.invoke(attribute='name'):016X}")
    print(f"  Age (years): {person.invoke(attribute='age_years')}")
    print(f"  Height: {person.invoke(attribute='height_cm')} cm")
    print(f"  Neuron count: {person.invoke(attribute='neuron_count'):,}")
    print(f"  Total atoms: {person.invoke(attribute='total_atoms'):.2e}")
    print(f"  Personality (openness): {person.invoke(attribute='personality_openness')}/100")
    print()
    
    print("=" * 70)
    print("KEY INSIGHTS:")
    print("=" * 70)
    print("1. Only identity is stored (64 bits)")
    print("2. ALL attributes exist because the object exists")
    print("3. Attributes manifest ONLY when invoked")
    print("4. Infinite detail from finite encoding")
    print("5. Nothing is stored - everything is computed")
    print("=" * 70)


if __name__ == '__main__':
    main()

