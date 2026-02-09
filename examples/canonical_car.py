"""
Canonical Car Example

This demonstrates how to define a Car as a canonical dimensional object:

    𝒪_car = ⟨S, D, R, F, T⟩

Where:
    - S = car substrate (unity, immutable identity)
    - D = {position, velocity, mass, fuel, ...}
    - R = {motion, fuel_consumption, ...}
    - F = manifestation function
    - T = time

No state is stored. All states are computed from the expression.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kernel import (
    Substrate, SubstrateIdentity,
    create_canonical_object,
    create_dimension,
    create_relationship,
)


# ═══════════════════════════════════════════════════════════════════
# STEP 1: CREATE SUBSTRATE (S)
# ═══════════════════════════════════════════════════════════════════

def create_car_substrate(vin: str, year: int, make: str, model: str) -> Substrate:
    """
    Create a car substrate.
    
    The substrate is unity - it contains NO data, only identity.
    All attributes are derived through the expression.
    """
    # Create 64-bit identity from VIN
    identity_value = hash(f"car:{vin}") & 0xFFFFFFFFFFFFFFFF
    identity = SubstrateIdentity(identity_value)
    
    # Expression that computes car attributes
    def car_expression(**kwargs):
        """
        The car's mathematical expression.
        
        This is where ALL attributes exist as potential.
        Nothing is stored - everything is computed.
        """
        attr = kwargs.get('attribute', 'identity')
        
        if attr == 'identity':
            return identity_value
        elif attr == 'vin':
            return vin
        elif attr == 'year':
            return year
        elif attr == 'make':
            return make
        elif attr == 'model':
            return model
        elif attr == 'mass':
            # Mass derived from make/model (simplified)
            return 1500.0  # kg
        elif attr == 'initial_position':
            return 0.0  # meters
        elif attr == 'initial_velocity':
            return 0.0  # m/s
        elif attr == 'initial_fuel':
            return 50.0  # liters
        elif attr == 'fuel_efficiency':
            # km per liter
            return 12.0
        else:
            # Unknown attribute - derive from identity
            return hash(f"{identity_value}:{attr}") & 0xFFFFFFFFFFFFFFFF
    
    return Substrate(identity, car_expression)


# ═══════════════════════════════════════════════════════════════════
# STEP 2: DEFINE DIMENSIONS (D)
# ═══════════════════════════════════════════════════════════════════

def create_car_dimensions():
    """
    Define car dimensions: D = {position, velocity, mass, fuel, ...}
    
    Each dimension has:
        - name: Label
        - domain: Type or validation
        - inherit: How to derive from substrate
    """
    return [
        # Position dimension
        create_dimension(
            name="position",
            domain=float,
            inherit=lambda s: s.expression(attribute="initial_position")
        ),
        
        # Velocity dimension
        create_dimension(
            name="velocity",
            domain=float,
            inherit=lambda s: s.expression(attribute="initial_velocity")
        ),
        
        # Mass dimension
        create_dimension(
            name="mass",
            domain=float,
            inherit=lambda s: s.expression(attribute="mass")
        ),
        
        # Fuel dimension
        create_dimension(
            name="fuel",
            domain=float,
            inherit=lambda s: s.expression(attribute="initial_fuel")
        ),
        
        # Fuel efficiency dimension
        create_dimension(
            name="fuel_efficiency",
            domain=float,
            inherit=lambda s: s.expression(attribute="fuel_efficiency")
        ),
        
        # VIN dimension (identity attribute)
        create_dimension(
            name="vin",
            domain=str,
            inherit=lambda s: s.expression(attribute="vin")
        ),
        
        # Year dimension
        create_dimension(
            name="year",
            domain=int,
            inherit=lambda s: s.expression(attribute="year")
        ),
    ]


# ═══════════════════════════════════════════════════════════════════
# STEP 3: DEFINE RELATIONSHIPS (R)
# ═══════════════════════════════════════════════════════════════════

def create_car_relationships():
    """
    Define car relationships: R = {motion, fuel_consumption, ...}

    Each relationship has:
        - name: Label
        - inputs: Input dimension names
        - outputs: Output dimension names
        - f: Function mapping inputs to outputs
    """
    return [
        # Motion relationship: position(t) = position(0) + velocity * time
        create_relationship(
            name="motion",
            inputs=["position", "velocity", "time"],
            outputs=["position"],
            f=lambda position, velocity, time: position + velocity * time
        ),

        # Fuel consumption: fuel(t) = fuel(0) - (distance / efficiency)
        create_relationship(
            name="fuel_consumption",
            inputs=["fuel", "velocity", "fuel_efficiency", "time"],
            outputs=["fuel"],
            f=lambda fuel, velocity, fuel_efficiency, time: max(
                0.0,
                fuel - (abs(velocity) * time / 1000.0) / fuel_efficiency
            )
        ),
    ]


# ═══════════════════════════════════════════════════════════════════
# STEP 4: CREATE CANONICAL CAR OBJECT
# ═══════════════════════════════════════════════════════════════════

def create_car(vin: str, year: int, make: str, model: str):
    """
    Create a canonical car object: 𝒪_car = ⟨S, D, R, F, T⟩

    Args:
        vin: Vehicle Identification Number
        year: Year of manufacture
        make: Manufacturer
        model: Model name

    Returns:
        CanonicalObject representing the car
    """
    # S - Substrate (unity)
    substrate = create_car_substrate(vin, year, make, model)

    # D - Dimensions
    dimensions = create_car_dimensions()

    # R - Relationships
    relationships = create_car_relationships()

    # F - Manifestation function (uses default)
    # T - Time (starts at 0)

    return create_canonical_object(
        substrate=substrate,
        dimensions=dimensions,
        relationships=relationships,
        time=0.0
    )


# ═══════════════════════════════════════════════════════════════════
# DEMONSTRATION
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("CANONICAL CAR EXAMPLE")
    print("=" * 70)
    print()

    # Create a car
    car = create_car(
        vin="1HGBH41JXMN109186",
        year=2024,
        make="Tesla",
        model="Model 3"
    )

    print("Car created as canonical object:")
    print(car)
    print()

    # Manifest at t=0
    print("State at t=0 (initial):")
    state_0 = car.manifest(t=0.0)
    for key, value in sorted(state_0.items()):
        print(f"  {key}: {value}")
    print()

    # Get car at t=10 (10 seconds later, traveling at 20 m/s)
    car_moving = car.at_time(10.0)

    # First set velocity
    print("Setting velocity to 20 m/s...")
    # Note: In a real implementation, we'd need a way to update dimension values
    # For now, we'll just show the concept
    print()

    # Manifest at t=10
    print("State at t=10 (after 10 seconds):")
    state_10 = car_moving.manifest(t=10.0)
    for key, value in sorted(state_10.items()):
        print(f"  {key}: {value}")
    print()

    # Show that original car is unchanged
    print("Original car state (still at t=0):")
    state_original = car.manifest(t=0.0)
    for key, value in sorted(state_original.items()):
        print(f"  {key}: {value}")
    print()

    print("=" * 70)
    print("KEY INSIGHTS:")
    print("=" * 70)
    print("1. NO STATE IS STORED - Everything is computed from S, D, R, T")
    print("2. The car substrate (S) is immutable unity")
    print("3. Dimensions (D) define what can be observed")
    print("4. Relationships (R) define how dimensions interact")
    print("5. Time (T) is a parameter, not stored state")
    print("6. Manifestation (F) computes the observable state")
    print("7. Creating car.at_time(10) doesn't mutate - it creates new object")
    print("=" * 70)

