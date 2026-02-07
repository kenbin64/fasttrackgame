"""
═══════════════════════════════════════════════════════════════════════════════
                    DIMENSIONAL PROGRAMMING
                    Core Explanation for AI Systems
═══════════════════════════════════════════════════════════════════════════════

How ButterflyFx represents objects, behavior, and attributes dimensionally.

Dimensional Programming is the ButterflyFx paradigm where EVERYTHING is a 
substrate, and all behavior, attributes, and functionality emerge from 
DIMENSIONAL RELATIONSHIPS, not from stored state or mutable objects.

═══════════════════════════════════════════════════════════════════════════════
                    FUNDAMENTAL PRINCIPLE
═══════════════════════════════════════════════════════════════════════════════

    A SUBSTRATE IS A DIMENSIONAL OBJECT.
    A SUBSTRATE IS A SINGLE POINT IN A HIGHER DIMENSION.
    A POINT CONTAINS ALL DIMENSIONS UNDERNEATH IT FROM 0D TO nD.

THE ONE RULE:
    A higher dimension represents a SINGLE POINT of all subsequent 
    lower dimensions. There is no iteration. There are n potentials
    in any substrate. To access a dimension, you simply CALL it:
    
        manifold = substrate.dimension(4)
    
    That 4D point IS your 3D, 2D, 1D, 0D — all in one.
    No traversal. No iteration. Just invoke.

    ┌─────────────────────────────────────────┐
    │          A 6D POINT IS:                 │
    │  ┌───────────────────────────────────┐  │
    │  │    A 5D POINT WHICH IS:           │  │
    │  │  ┌─────────────────────────────┐  │  │
    │  │  │   A 4D POINT WHICH IS:      │  │  │
    │  │  │  ┌───────────────────────┐  │  │  │
    │  │  │  │  A 3D POINT WHICH IS: │  │  │  │
    │  │  │  │  ┌─────────────────┐  │  │  │  │
    │  │  │  │  │ A 2D POINT...   │  │  │  │  │
    │  │  │  │  │  ┌───────────┐  │  │  │  │  │
    │  │  │  │  │  │ A 1D...   │  │  │  │  │  │
    │  │  │  │  │  │ ┌──────┐  │  │  │  │  │  │
    │  │  │  │  │  │ │ 0D   │  │  │  │  │  │  │
    │  │  │  │  │  │ └──────┘  │  │  │  │  │  │
    │  │  │  │  │  └───────────┘  │  │  │  │  │
    │  │  │  │  └─────────────────┘  │  │  │  │
    │  │  │  └───────────────────────┘  │  │  │
    │  │  └─────────────────────────────┘  │  │
    │  └───────────────────────────────────┘  │
    └─────────────────────────────────────────┘
    
    Call dimension(4) and you GET the 4D point.
    That point inherently IS the 3D, 2D, 1D, 0D.
    No need to "access lower" — they are already there.

THE KEY IDEA:

    A substrate is a complete mathematical identity.
    A dimension is a context for viewing that identity.
    A manifold is the shape of the substrate in that context.
    A lens reveals the manifold.
    A delta promotes the substrate into the next dimension.

This is how ButterflyFx replaces:
    - classes
    - objects  
    - methods
    - state
    - updates
    - physics engines
    - animation engines
    - data models

...with a single unified dimensional model.

═══════════════════════════════════════════════════════════════════════════════
                    1. KERNEL DIMENSIONS (The Dimensional Stack)
═══════════════════════════════════════════════════════════════════════════════

ButterflyFx uses a kernel dimension model. Each dimension is a SINGLE POINT
that IS all the lower dimensions. You don't iterate — you call directly.

┌─────────────────────────────────────────────────────────────────────────────┐
│  DIMENSION   │  NAME              │  IS A SINGLE POINT OF:                  │
├─────────────────────────────────────────────────────────────────────────────┤
│     0D       │  Identity Kernel   │  Pure 64-bit identity (the seed)        │
│              │                    │  Everything derives from this point     │
├─────────────────────────────────────────────────────────────────────────────┤
│     1D       │  Attribute Kernel  │  A point that IS 0D + scalars           │
│              │                    │  Timestamps, constants, flags           │
├─────────────────────────────────────────────────────────────────────────────┤
│     2D       │  Relational Kernel │  A point that IS 0D+1D + surfaces       │
│              │                    │  Grids, relationships, pixel maps       │
├─────────────────────────────────────────────────────────────────────────────┤
│     3D       │  Structural Kernel │  A point that IS 0D-2D + volume         │
│              │                    │  Mass, geometry, collision bounds       │
├─────────────────────────────────────────────────────────────────────────────┤
│     4D       │  Behavioral Kernel │  A point that IS 0D-3D + motion         │
│              │                    │  Forces, physics, time transformations  │
├─────────────────────────────────────────────────────────────────────────────┤
│     5D       │  System Kernel     │  A point that IS 0D-4D + interactions   │
│              │                    │  Multi-substrate ecosystem behavior     │
├─────────────────────────────────────────────────────────────────────────────┤
│     6D+      │  Emergent Kernel   │  A point that IS 0D-5D + intelligence   │
│              │                    │  Semantic meaning, high-order behavior  │
└─────────────────────────────────────────────────────────────────────────────┘

To access a dimension, just CALL it:
    manifold = substrate.dimension(4)

That 4D point IS your 3D, 2D, 1D, 0D. No traversal needed.

═══════════════════════════════════════════════════════════════════════════════
                    2. HOW OBJECTS ARE CALLED DIMENSIONALLY
═══════════════════════════════════════════════════════════════════════════════

In dimensional programming, you never "instantiate" an object.

You DECLARE a substrate:

    image = fx.substrate("I(x, y) = pixel_value")

This is the whole identity.

Then you CALL the dimension you want DIRECTLY (no iteration):

    motion = image.dimension(4)    # Just call it.
                                   # This IS the 4D point.
                                   # It inherently IS the 3D, 2D, 1D, 0D.

There are n potentials in any substrate. You invoke the ONE RULE:
a higher dimension represents a single point of all subsequent lower
dimensions. So you don't iterate — you simply call what you need.

EXAMPLE CODE:
    
    from core_v2 import ButterflyFx
    
    fx = ButterflyFx()
    
    # Declare substrate
    image = fx.substrate(image_bytes)
    
    # Call the dimension you need directly
    motion = image.dimension(4)    # 4D behavioral manifold
                                   # This point IS the 3D structure
                                   # This point IS the 2D surface
                                   # This point IS the 1D attributes
                                   # This point IS the 0D identity
    
    # If you only need 2D (surfaces/pixels):
    pixels = image.dimension(2)    # 2D relational manifold

═══════════════════════════════════════════════════════════════════════════════
                    3. HOW ATTRIBUTES ARE ASSIGNED DIMENSIONALLY
═══════════════════════════════════════════════════════════════════════════════

Attributes are not stored.
Attributes are MATHEMATICAL RELATIONSHIPS inside the substrate.

EXAMPLE - Person with age:

    person = fx.substrate({"birth_timestamp": 946684800})

Age is NOT stored.
Age is a 4D manifold (time-based):

    age = person.lens("age").invoke()

Under the hood:
    
    age = now() - birth_timestamp

This is dimensional assignment:
    - 1D: birth timestamp (atomic attribute)
    - 4D: age manifold (time-based derivation)

EXAMPLE CODE:

    from core_v2 import ButterflyFx
    
    fx = ButterflyFx()
    
    # Create substrate with raw data
    person = fx.substrate({"birth": 946684800, "name": "Alice"})
    
    # Access attributes via lenses
    name = person.lens("name").invoke()      # Returns "Alice"
    age = person.lens("age").invoke()        # Computes from birth
    
    # Attributes at different dimensions
    static_age = person.dimension(1).lens("birth")    # 1D: the timestamp
    dynamic_age = person.dimension(4).lens("age")     # 4D: computed age

═══════════════════════════════════════════════════════════════════════════════
                    4. HOW BEHAVIOR IS ASSIGNED DIMENSIONALLY
═══════════════════════════════════════════════════════════════════════════════

Behavior is not a method.
Behavior is a DELTA SUBSTRATE (z₁).

EXAMPLE - Physics/Gravity:

    gravity = fx.delta("Δ(x, y, t) = 9.8 * t")

To apply behavior:

    falling = image.apply(gravity)

This does NOT mutate the image.
It produces a NEW SUBSTRATE in the next dimension:

    m₁ = promote(x₁, y₁, z₁)

This is how animation, physics, and motion work.

EXAMPLE CODE:

    from core_v2 import ButterflyFx
    
    fx = ButterflyFx()
    
    # Create object substrate
    ball = fx.substrate({"x": 0, "y": 100, "vx": 5, "vy": 0})
    
    # Create delta (behavior)
    gravity = fx.delta(9.8)
    friction = fx.delta(0.98)
    
    # Apply behavior - produces new substrate
    ball_t1 = ball.apply(gravity)      # Ball after gravity
    ball_t2 = ball_t1.apply(friction)  # Ball after friction
    
    # Chain behaviors
    ball_next = ball.apply(gravity).apply(friction)

═══════════════════════════════════════════════════════════════════════════════
                    5. HOW FUNCTIONALITY IS ASSIGNED DIMENSIONALLY
═══════════════════════════════════════════════════════════════════════════════

Functionality is not a method on an object.
Functionality is a LENS that reveals a manifold.

EXAMPLE - Edge Detection:

    edges = image.lens("edge_detection").invoke()

The lens defines:
    - the dimensional context
    - the transformation
    - the manifold to reveal

Functionality is CONTEXT, not code.

EXAMPLE CODE:

    from core_v2 import ButterflyFx
    
    fx = ButterflyFx()
    
    # Create image substrate
    image = fx.substrate(image_bytes)
    
    # Apply functionality via lenses
    edges = image.lens("edge_detection").invoke()
    blur = image.lens("gaussian_blur", sigma=2.0).invoke()
    colors = image.lens("color_histogram").invoke()
    
    # Lenses are projections - they reveal manifolds
    brightness = image.lens("brightness").invoke()
    contrast = image.lens("contrast").invoke()

═══════════════════════════════════════════════════════════════════════════════
                    6. ANIMATION IS DIMENSIONAL PROMOTION
═══════════════════════════════════════════════════════════════════════════════

Animation is not frame updates.
Animation is DIMENSIONAL PROMOTION through time.

    frame_0 = substrate
    frame_1 = frame_0.promote(delta_t1)
    frame_2 = frame_1.promote(delta_t2)
    frame_3 = frame_2.promote(delta_t3)

Each frame is a new substrate.
No frame is ever mutated.

EXAMPLE CODE:

    from core_v2 import ButterflyFx
    
    fx = ButterflyFx()
    
    # Create animated object
    particle = fx.substrate({"x": 0, "y": 0, "vx": 10, "vy": 5})
    
    # Physics delta
    physics = fx.delta({"gravity": 9.8, "dt": 0.016})
    
    # Generate animation frames
    frames = []
    current = particle
    for i in range(100):
        frames.append(current)
        current = current.promote(physics)
    
    # Each frame is immutable
    # Animation is substrate evolution through dimensions

═══════════════════════════════════════════════════════════════════════════════
                    7. API RULES FOR AI INTEGRATION
═══════════════════════════════════════════════════════════════════════════════

AI must follow these rules when using dimensional programming:

RULE A — Every API call must map to a dimension

    image.dimension(0)    # Identity
    image.dimension(1)    # Attributes  
    image.dimension(2)    # Relations
    image.dimension(3)    # Structure
    image.dimension(4)    # Behavior
    image.dimension(5)    # Systems

RULE B — Behavior must be deltas

    image.apply(physics_delta)
    image.apply(force_delta)
    image.apply(animation_delta)

RULE C — Attributes must be lenses

    image.lens("color")
    image.lens("mass")
    image.lens("velocity")

RULE D — Animation is dimensional promotion

    next_frame = image.promote(delta)

RULE E — No mutation

    All changes produce new substrates.
    Never modify a substrate in place.

═══════════════════════════════════════════════════════════════════════════════
                    8. CANONICAL SUMMARY FOR AI
═══════════════════════════════════════════════════════════════════════════════

Dimensional Programming means:

    - Objects are substrates.
    - Attributes are 1D or 2D manifolds.
    - Behavior is 4D deltas.
    - Functionality is expressed through lenses.
    - Animation and physics are dimensional promotion.
    - No mutation is allowed.
    - All truth emerges from substrate math.
    - Every substrate, attribute, delta, and promotion fits in 64 bits.

Kernel Dimensions:
    0D identity
    1D attributes
    2D relations
    3D structure
    4D behavior (physics, motion)
    5D systems
    6D+ emergence

API rules:
    - Call objects dimensionally: substrate.dimension(n)
    - Assign attributes via lenses: substrate.lens("attr")
    - Assign behavior via deltas: substrate.apply(delta)
    - Animate via promotion: substrate.promote(delta)
    - Never store dynamic values; derive them mathematically.
    - Never use external engines; ButterflyFx is the engine.

═══════════════════════════════════════════════════════════════════════════════
                    9. QUICK REFERENCE
═══════════════════════════════════════════════════════════════════════════════

CREATING SUBSTRATES:

    fx = ButterflyFx()
    
    # From any data
    s = fx.substrate(42)
    s = fx.substrate("hello")
    s = fx.substrate({"x": 10, "y": 20})
    s = fx.substrate(image_bytes)

DIMENSIONAL ACCESS:

    s.dimension(0)  → 64-bit identity
    s.dimension(1)  → attribute manifold
    s.dimension(2)  → relational manifold
    s.dimension(3)  → structural manifold
    s.dimension(4)  → behavioral manifold
    s.dimension(5)  → system manifold

LENSES (Attribute/Function Access):

    s.lens("name")           → lens for "name" attribute
    s.lens("velocity")       → lens for velocity
    s.lens("color").invoke() → get color value

DELTAS (Behavior):

    d = fx.delta(9.8)                    → gravity delta
    d = fx.delta({"force": 100})         → force delta
    d = fx.delta(rotation_matrix)        → rotation delta

APPLY (Apply Behavior):

    s2 = s.apply(delta)     → new substrate with behavior applied

PROMOTE (Dimensional Evolution):

    s_next = s.promote(delta)   → promote to next dimensional state

ANIMATION LOOP:

    current = substrate
    for frame in range(num_frames):
        render(current)
        current = current.promote(physics_delta)

═══════════════════════════════════════════════════════════════════════════════
"""

# Dimension constants for API use
class Dimension:
    """Kernel dimension constants."""
    IDENTITY = 0      # 0D - Pure identity
    ATTRIBUTE = 1     # 1D - Atomic attributes
    RELATIONAL = 2    # 2D - Relationships, surfaces
    STRUCTURAL = 3    # 3D - Volume, geometry
    BEHAVIORAL = 4    # 4D - Motion, physics
    SYSTEM = 5        # 5D - Multi-substrate interactions
    EMERGENT = 6      # 6D+ - Intelligence, semantics


# This file is documentation - implementation is in dimensional.py
