#!/usr/bin/env python3
"""
ButterflyFX Developer Quickstart - Dimensional API

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)

This is your starting point for any ButterflyFX project.
Copy this scaffolding to begin building dimensional applications.

---

THE PARADIGM SHIFT:
  Traditional OOP: Objects are containers with declared properties
  ButterflyFX:     Objects are DIMENSIONS containing infinite potential

CORE INSIGHT:
  When you invoke("Car"), you don't get an empty container.
  You get a COMPLETE car with EVERY possible attribute in POTENTIAL.
  Attributes materialize only when accessed.

THE 7 LEVELS (Fibonacci):
  0: VOID   (0) - Pure potential, the pipeline
  1: POINT  (1) - Single value
  2: LINE   (1) - Sequence/list
  3: WIDTH  (2) - Plane/grid
  4: PLANE  (3) - 2D surface
  5: VOLUME (5) - 3D structure
  6: WHOLE  (8) - Complete object

HOLY GRAIL: WHOLE(8) + VOLUME(5) = 13 = POINT of next spiral
"""

# =============================================================================
# IMPORTS - Everything you need to start
# =============================================================================

# Core invocation - the primary way to create objects
from helix.dimensional_api import (
    invoke,                    # Create dimensional objects
    materialize,               # Explicitly materialize at a level
    substrate,                 # Global substrate reference
)

# Dimensional types - for type hints and custom collections
from helix.dimensional_api import (
    DimensionalObject,         # Base dimensional object
    DimensionalPoint,          # A point in a dimension (also a dimension)
    DimensionalList,           # A LINE of points (Level 2)
    DimensionalDict,           # A PLANE of points (Level 3)
    DimensionalSet,            # Unique points
)

# Decorators - for controlling dimensional behavior
from helix.dimensional_api import (
    sealed,                    # Mark as immutable
    closed,                    # Prevent new points
    dimensional,               # Make a class dimensional
    lazy,                      # Lazy-evaluated properties
    computed,                  # Auto-recomputing properties
)

# Levels and coordinates - for dimensional navigation
from helix.dimensional_api import (
    Level,                     # The 7 dimensional levels
    Spiral,                    # Spiral context management
    Coordinate,                # Position in dimensional space
    Address,                   # Full path addressing
)

# Exceptions - for error handling
from helix.dimensional_api import (
    DimensionalError,          # Base exception
    ImmutabilityViolation,     # Sealed point modified
    ClosedDimensionViolation,  # Added to closed dimension
    InvocationError,           # Invocation failed
    MaterializationError,      # Materialization failed
)

# Utilities - helper functions
from helix.dimensional_api import (
    is_invoked,                # Check if object is invoked
    is_materialized,           # Alias for is_invoked
    get_level,                 # Get object's level
    get_spiral,                # Get object's spiral
    dimension_of,              # Get dimension identity
    points_of,                 # Get materialized points
)


# =============================================================================
# EXAMPLE 1: Basic Object Invocation
# =============================================================================

def example_basic_invocation():
    """
    The fundamental operation: invoke, not instantiate.
    
    When you invoke("Car"), the car ALREADY has every possible
    attribute of a car - engine, wheels, VIN, color, etc.
    They exist in POTENTIAL until accessed.
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Object Invocation")
    print("="*60)
    
    # Invoke a car from the dimensional substrate
    # This is NOT like Car() - it's fundamentally different
    car = invoke("Car")
    
    # The car exists but nothing is materialized yet
    print(f"\nInvoked: {car}")
    print(f"Level: {car.level.name_display}")
    print(f"Materialized points: {points_of(car)}")  # Empty - nothing accessed yet
    
    # Now access some attributes - they materialize on access
    car.make = "Toyota"
    car.model = "Corolla"
    car.year = 2024
    
    print(f"\nAfter setting attributes:")
    print(f"  car.make = {car.make.value}")
    print(f"  car.model = {car.model.value}")
    print(f"  car.year = {car.year.value}")
    print(f"Materialized points: {points_of(car)}")


# =============================================================================
# EXAMPLE 2: Dimensional Depth - Every Point is a Dimension
# =============================================================================

def example_dimensional_depth():
    """
    Every attribute is BOTH a point AND a dimension.
    
    car.engine is:
      - A POINT in the car dimension
      - A DIMENSION containing engine attributes
    
    This is the point↔dimension duality.
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Dimensional Depth")
    print("="*60)
    
    car = invoke("Car")
    
    # Access engine - creates the engine dimension with ALL engine attributes
    engine = car.engine  # This IS the engine, complete in potential
    
    print(f"\ncar.engine: {engine}")
    print(f"Identity: {engine.identity}")
    
    # Set engine properties - each is also a dimension
    car.engine.type = "V8"
    car.engine.displacement = 5.0
    car.engine.horsepower = 450
    car.engine.torque = 420
    
    # Go deeper - pistons
    car.engine.cylinders = 8
    
    # Each cylinder has ALL cylinder attributes in potential
    car.engine.cylinder1.bore = 3.5
    car.engine.cylinder1.stroke = 4.0
    car.engine.cylinder1.compression_ratio = 10.5
    
    print(f"\nEngine attributes:")
    print(f"  Type: {car.engine.type.value}")
    print(f"  Horsepower: {car.engine.horsepower.value}")
    
    print(f"\nCylinder 1 attributes:")
    print(f"  Bore: {car.engine.cylinder1.bore.value}")
    print(f"  Stroke: {car.engine.cylinder1.stroke.value}")


# =============================================================================
# EXAMPLE 3: Direct Addressing - No Iteration
# =============================================================================

def example_direct_addressing():
    """
    ButterflyFX uses O(1) direct addressing, not O(n) iteration.
    
    You don't traverse through all pistons to get piston[5].
    You jump directly to it.
    
    This is like dimensional coordinates, not array indexing.
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Direct Addressing (No Iteration)")
    print("="*60)
    
    car = invoke("Car")
    
    # Create a dimensional list for pistons
    pistons = DimensionalList("Car.engine.pistons")
    car.engine.pistons = pistons
    
    # Direct access to piston[5] - O(1)
    # We don't iterate through [0], [1], [2], [3], [4]
    # We jump directly to [5]
    car.engine.pistons.value[5].firing = True
    car.engine.pistons.value[5].position = "TDC"
    car.engine.pistons.value[5].temperature = 250
    
    # Now access [0] - still O(1)
    car.engine.pistons.value[0].firing = False
    car.engine.pistons.value[0].position = "BDC"
    
    print(f"\nDirect access to piston[5]:")
    print(f"  firing: {car.engine.pistons.value[5].firing.value}")
    print(f"  position: {car.engine.pistons.value[5].position.value}")
    print(f"  temperature: {car.engine.pistons.value[5].temperature.value}")
    
    print(f"\nDirect access to piston[0]:")
    print(f"  firing: {car.engine.pistons.value[0].firing.value}")
    print(f"  position: {car.engine.pistons.value[0].position.value}")
    
    print(f"\nMaterialized indices: {car.engine.pistons.value.indices}")
    print("Note: Only [0] and [5] exist - no wasted resources on [1,2,3,4]")


# =============================================================================
# EXAMPLE 4: Sealing and Closing - Immutability
# =============================================================================

def example_sealing_and_closing():
    """
    @sealed - Makes material immutable
    @closed - Prevents adding new points
    
    These control dimensional structure integrity.
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Sealing and Closing")
    print("="*60)
    
    # Create and seal a token
    token = invoke("AuthToken")
    token.value = "abc123xyz"
    token.issued_at = "2024-02-15T10:00:00Z"
    token.expires_at = "2024-02-15T11:00:00Z"
    
    # Seal the token value - it's now immutable
    token.seal_point("value")
    
    print(f"\nSealed token.value: {token.value.value}")
    print(f"token.value.is_sealed: {token.value.is_sealed}")
    
    # Try to modify - will raise ImmutabilityViolation
    try:
        token.value.value = "hacked"
    except ImmutabilityViolation as e:
        print(f"\n✓ ImmutabilityViolation raised: {e}")
    
    # Close a protocol message - no new fields allowed
    message = invoke("ProtocolMessage")
    message.type = "request"
    message.payload = {"action": "get"}
    message.close()
    
    print(f"\nClosed message fields: {points_of(message)}")
    
    # Try to add new field - will raise ClosedDimensionViolation
    try:
        message.unauthorized_field = "hack"
    except ClosedDimensionViolation as e:
        print(f"✓ ClosedDimensionViolation raised: {e}")


# =============================================================================
# EXAMPLE 5: Custom Dimensional Types
# =============================================================================

def example_custom_types():
    """
    Create your own dimensional types using @dimensional decorator.
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Custom Dimensional Types")
    print("="*60)
    
    @dimensional(level=Level.VOLUME)
    class PhysicsBody:
        """A physics body exists in 3D space (VOLUME level)."""
        pass
    
    # Invoke the custom type
    body = PhysicsBody()
    
    # Set physics properties
    body.position.x = 0.0
    body.position.y = 10.0
    body.position.z = 0.0
    body.velocity.x = 5.0
    body.velocity.y = 0.0
    body.velocity.z = 0.0
    body.mass = 1.0
    
    print(f"\nPhysicsBody: {body}")
    print(f"Position: ({body.position.x.value}, {body.position.y.value}, {body.position.z.value})")
    print(f"Velocity: ({body.velocity.x.value}, {body.velocity.y.value}, {body.velocity.z.value})")
    print(f"Mass: {body.mass.value}")


# =============================================================================
# EXAMPLE 6: Spiral Navigation
# =============================================================================

def example_spiral_navigation():
    """
    Navigate through the dimensional helix.
    
    Spiral up: Move to next spiral (requires WHOLE level)
    Spiral down: Move to previous spiral (requires VOID level)
    """
    print("\n" + "="*60)
    print("EXAMPLE 6: Spiral Navigation")
    print("="*60)
    
    # Get current spiral context
    spiral = Spiral.current()
    
    print(f"\nCurrent spiral: {spiral.index}")
    print(f"Current level: {spiral.level.name_display}")
    
    # Invoke level directly (O(1) jump)
    spiral.invoke_level(Level.WIDTH)
    print(f"\nAfter invoke_level(WIDTH):")
    print(f"Current level: {spiral.level.name_display}")
    
    # Jump to WHOLE
    spiral.invoke_level(Level.WHOLE)
    print(f"\nAfter invoke_level(WHOLE):")
    print(f"Current level: {spiral.level.name_display}")
    
    # Spiral up (transition to next spiral)
    spiral.spiral_up()
    print(f"\nAfter spiral_up():")
    print(f"Current spiral: {spiral.index}")
    print(f"Current level: {spiral.level.name_display}")
    
    print("\n💡 Key insight:")
    print(f"   WHOLE ({Level.WHOLE.fibonacci}) + VOLUME ({Level.VOLUME.fibonacci})")
    print(f"   = {Level.WHOLE.fibonacci + Level.VOLUME.fibonacci}")
    print(f"   = POINT of next spiral (Fibonacci 13)")


# =============================================================================
# EXAMPLE 7: Complete Application Pattern
# =============================================================================

def example_complete_application():
    """
    A complete application pattern showing real-world usage.
    """
    print("\n" + "="*60)
    print("EXAMPLE 7: Complete Application Pattern")
    print("="*60)
    
    # 1. Define your domain model by registering types
    substrate.register("User", {
        "email": str,
        "name": str,
        "profile": {
            "avatar": str,
            "bio": str,
        }
    })
    
    substrate.register("Order", {
        "id": str,
        "items": list,
        "total": float,
        "status": str,
    })
    
    # 2. Invoke and populate objects
    user = invoke("User")
    user.email = "ken@butterflyfx.us"
    user.name = "Kenneth Bingham"
    user.profile.avatar = "https://butterflyfx.us/avatar.png"
    user.profile.bio = "Creator of ButterflyFX"
    
    # 3. Create related objects
    order = invoke("Order")
    order.id = "ORD-2024-001"
    order.status = "pending"
    order.total = 99.99
    
    # Create order items as dimensional list
    items = DimensionalList("Order.items")
    items[0].name = "ButterflyFX License"
    items[0].price = 99.99
    items[0].quantity = 1
    order.items = items
    
    # 4. Link objects (dimensional direction)
    order.user = user  # Order points to User
    user.orders = DimensionalList("User.orders")
    user.orders.value[0] = order  # User has list of orders
    
    # 5. Seal important data
    order.seal_point("id")  # Order ID cannot change
    
    # 6. Export current state
    print("\nUser:")
    print(f"  Email: {user.email.value}")
    print(f"  Name: {user.name.value}")
    print(f"  Bio: {user.profile.bio.value}")
    
    print("\nOrder:")
    print(f"  ID: {order.id.value} (sealed)")
    print(f"  Status: {order.status.value}")
    print(f"  Total: ${order.total.value}")


# =============================================================================
# SCAFFOLDING TEMPLATE - Copy this for new projects
# =============================================================================

SCAFFOLDING_TEMPLATE = '''
#!/usr/bin/env python3
"""
My ButterflyFX Application

Description of your dimensional application here.
"""

from helix.dimensional_api import (
    invoke, materialize, substrate,
    DimensionalObject, DimensionalList, DimensionalDict,
    Level, Coordinate, Address,
    sealed, closed, dimensional, lazy,
    DimensionalError, ImmutabilityViolation, ClosedDimensionViolation,
)


def main():
    """Main application entry point."""
    
    # 1. Register your types (optional - types can be invoked dynamically)
    substrate.register("MyType", {
        "attribute1": str,
        "attribute2": int,
    })
    
    # 2. Invoke objects
    obj = invoke("MyType")
    
    # 3. Set attributes (they materialize on access)
    obj.attribute1 = "Hello, Dimensional World!"
    obj.attribute2 = 42
    
    # 4. Build your application logic
    print(f"Attribute 1: {obj.attribute1.value}")
    print(f"Attribute 2: {obj.attribute2.value}")
    
    # 5. Return or export results
    return obj.to_dict()


if __name__ == "__main__":
    result = main()
    print(f"\\nResult: {result}")
'''


# =============================================================================
# MAIN - Run all examples
# =============================================================================

def main():
    """Run all quickstart examples."""
    print("="*60)
    print("🦋 BUTTERFLYFX DEVELOPER QUICKSTART")
    print("="*60)
    print("\nThis quickstart demonstrates the dimensional paradigm.")
    print("Copy this file to start any ButterflyFX project.")
    
    # Run examples
    example_basic_invocation()
    example_dimensional_depth()
    example_direct_addressing()
    example_sealing_and_closing()
    example_custom_types()
    example_spiral_navigation()
    example_complete_application()
    
    # Show scaffolding template
    print("\n" + "="*60)
    print("SCAFFOLDING TEMPLATE")
    print("="*60)
    print("\nCopy this template to start a new ButterflyFX project:")
    print("-"*60)
    print(SCAFFOLDING_TEMPLATE)
    
    print("\n" + "="*60)
    print("🦋 You're ready to build with ButterflyFX!")
    print("="*60)
    print("\nKey concepts to remember:")
    print("  • invoke() not instantiate()")
    print("  • Objects are dimensions with infinite potential")
    print("  • Attributes materialize only when accessed")
    print("  • Direct addressing is O(1), not iteration")
    print("  • 7 levels: VOID → POINT → LINE → WIDTH → PLANE → VOLUME → WHOLE")
    print("  • WHOLE + VOLUME = POINT of next spiral")
    print("\nDocumentation: https://butterflyfx.us")
    print("Creator: Kenneth Bingham")


if __name__ == "__main__":
    main()
