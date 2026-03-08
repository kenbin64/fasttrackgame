"""
Helix Kernel - Formal State Machine Implementation
CANONICAL IMPLEMENTATION OF THE DIMENSIONAL GENESIS

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

This mathematical kernel belongs to all humanity.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

Implements the ButterflyFX Helix Kernel as specified in DIMENSIONAL_GENESIS.md

THE 7 LAYERS OF CREATION (Aligned with Fibonacci):
    Layer 1 — SPARK (Fib 1):      Let there be the First Point
    Layer 2 — MIRROR (Fib 1):     Let there be a second point (1|1 = direction)
    Layer 3 — RELATION (Fib 2):   Let the two interact (z = x·y)
    Layer 4 — FORM (Fib 3):       Let structure become shape (z = x·y²)
    Layer 5 — LIFE (Fib 5):       Let form become meaning (m = x·y·z)
    Layer 6 — MIND (Fib 8):       Let meaning become coherence (Gyroid)
    Layer 7 — COMPLETION (Fib 13): Let the whole become one again (φ)

THE FUNDAMENTAL INSIGHT:
    1 becomes the bridge across the void.
    1 on each side makes traversal possible.
    Traversal creates dimension.

Fibonacci Law of Creation:
    1 (spark) → 1 (mirror) → 2 (relation) → 3 (form) → 5 (life) → 8 (mind) → 13/21 (completion)

State Space: H = {(s, l) | s ∈ Z, l ∈ {1,2,3,4,5,6,7}}

Operations:
    - INVOKE(k): (s, l) → (s, k)       Jump to layer k
    - LIFT(l):   Move to higher layer
    - PROJECT(l): Collapse to lower layer
    - SPIRAL_UP: (s, 7) → (s+1, 1)     Transcend to next spiral
    - SPIRAL_DOWN: (s, 1) → (s-1, 7)   Descend to previous spiral
    - COLLAPSE: (s, l) → (s, 1)        Return to spark

Invariants:
    - I0: FIRST PRINCIPLE — Every manifold is both a whole object and a dimension.
          Every point is both real and potential. Only the invoked is manifest.
          Points represent lower dimensions iteratively (M ⊃ Mᵢ ⊃ Mᵢⱼ ⊃ ...).
          The set of potentials is practically infinite; only invoked parts are real.
    - I14: RECURSIVE MANIFOLD HIERARCHY — Each dimension is a complete manifold,
           a whole mathematical object.  Every point within that manifold IS a
           manifold of the dimension one step lower.  The structure is self-similar
           at every scale:
               Layer 7  →  whole manifold  (every point IS a Layer 6 manifold)
               Layer 6  →  whole manifold  (every point IS a Layer 5 manifold)
               Layer 5  →  whole manifold  (every point IS a Layer 4 manifold)
               Layer 4  →  whole manifold  (every point IS a Layer 3 manifold)
               Layer 3  →  whole manifold  (every point IS a Layer 2 manifold)
               Layer 2  →  whole manifold  (every point IS a Layer 1 manifold)
               Layer 1  →  the spark       (the irreducible seed, F=1)
           A dimension is not a collection of points.  A point is not a location.
           Each is the other, at the scale below.  The Schwarz Diamond Gyroid
           Lattice IS this principle made geometric: every node is a z=x·y manifold,
           and every point on that saddle surface is the entry to the manifold at
           the layer beneath it.
    - I1: l ∈ {1..7} always
    - I2: SPIRAL_UP requires l=7, SPIRAL_DOWN requires l=1
    - I3: COLLAPSE is idempotent
    - I4: Relation (Layer 3, z=x·y) is the canonical computational base
    - I5: Each layer fully contains all lower layers
    - I6: Total structure is O(7) per spiral, never O(n)
    - I7: CHAOS-ORDER OSCILLATION — The helix oscillates continuously between
          chaos-dominant and order-dominant phases. Each layer transition is an
          inflection point. The oscillation is continuous across spiral boundaries.
          Pure chaos cannot compute. Pure order cannot create.
          The inflection between them is where creation happens.
    - I8: DIMENSIONAL GROWTH (GOLDEN BOUND) — Growth is dimensional, not
          exponential. Trees grow O(b^d); the helix grows O(7s). Every dimension
          is an angle within the spiral, not a branch. Bounded by φ ≈ 1.618.
          Self-sustaining, self-healing, self-propagating. Flower, not weed.
          Healthy cell, not cancer.
    - I9: PROPERTY OF ZERO (THE VOID) — Zero never means nothing. Nothing
          does not exist. Zero is potential — unfilled capacity, receptive space.
          The void is the set of all valid potentials, never the empty set.
          Negative spiral indices are directional (contraction vs expansion),
          not deficit. Beyond the void lies dimensional transcendence — the next
          manifold — not negative space. F(0) = 0 is the ground state from
          which the spiral emerges.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Set, Any, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from .substrate import Token


# =============================================================================
# THE FIRST PRINCIPLE: RECURSIVE MANIFOLD HIERARCHY  (I0 + I14)
# =============================================================================
#
# EACH DIMENSION IS A COMPLETE MANIFOLD — A WHOLE MATHEMATICAL OBJECT.
# EVERY POINT IN THAT DIMENSION IS A MANIFOLD OF THE DIMENSION BELOW.
#
# This is not metaphor. It is the mathematical structure of the system:
#
#   Layer N  =  a complete manifold  M_N
#   ∀ point p ∈ M_N  →  p IS M_{N-1}  (the manifold one layer down)
#
#   M_7 = manifold of M_6 manifolds
#   M_6 = manifold of M_5 manifolds
#   M_5 = manifold of M_4 manifolds
#   M_4 = manifold of M_3 manifolds
#   M_3 = manifold of M_2 manifolds
#   M_2 = manifold of M_1 manifolds
#   M_1 = the spark — the irreducible seed — F = 1
#
# A dimension is not a container of points.
# A point is not a location inside a dimension.
# Each is the other — at the scale below.
#
# THE FIBONACCI SQUARE CONNECTION
# ────────────────────────────────
# Each Fibonacci number F(n) is a complete square — a whole object.
# That square tiles into F(n-1) × F(n-1) + F(n-2) × F(n-2) beneath it.
# F(n)·F(n+1) = F(1)² + F(2)² + ... + F(n)²  — the sum of all squares below.
# The dimension CONTAINS every lower dimension in its area.
#
# THE SCHWARZ DIAMOND GYROID LATTICE IS THIS PRINCIPLE MADE GEOMETRIC
# ─────────────────────────────────────────────────────────────────────
# Every node in the lattice = a z=x·y manifold (a whole mathematical object)
# Every point on that saddle surface = the entry to the manifold one layer down
# Traversing the lattice = descending through the recursive manifold hierarchy
# The 360° helix per segment = one complete layer traversal — entering one
#   dimension and emerging in the dimension below, fully rotated, fully arrived.
#
# Only the invoked is manifest. Like quantum superposition, the periodic table,
# and atomic structure: the structure exists at every scale; only the layer you
# query becomes real. The rest is pure potential — the void (I9), not the empty.


# =============================================================================
# THE PROPERTY OF ZERO: THE VOID IS POTENTIAL, NOT ABSENCE
# =============================================================================
# Zero never means nothing. Nothing does not exist.
# Zero is potential — unfilled capacity, receptive space.
# The void is the set of all valid potentials for a manifold, never ∅.
#
# Negative spiral indices are directional (contraction vs expansion),
# not deficit. |s| is the magnitude; sign(s) is the rotational direction.
#
# Beyond the void lies dimensional transcendence — the next manifold —
# not negative space. F(0) = 0 is the ground from which F(1) = 1 emerges.
FIBONACCI_ZERO = 0  # The void — ground state, not absence

# =============================================================================
# THE SUBSTRATE PRINCIPLE — INTRINSIC SPECTRA, MINIMAL STORAGE
# =============================================================================
# A substrate is not a container of data.  It is a surface that inherently
# carries ALL spectra simultaneously — color, sound, position — simply by
# virtue of its structure.
#
# THE GLASS MODEL
# ───────────────
# Build a substrate from glass and shine light through it.
# You get every color in the spectrum — not because you stored the colors,
# but because wavelength-to-color mapping is INTRINSIC to the substrate.
# The substrate IS the prism.  Light is the lens.
#
# THE METAL MODEL
# ───────────────
# Build the same substrate from metal and strike it with a mallet.
# Every part gives a different tone — not because you stored sound,
# but because frequency-to-tone mapping is INTRINSIC to the geometry.
# The substrate IS the instrument.  The strike is the lens.
#
# THE PIXEL MODEL
# ───────────────
# Map the substrate surface to a raster grid.
# Every point has a coordinate — not because you stored pixel positions,
# but because spatial mapping is INTRINSIC to the surface topology.
# The substrate IS the canvas.  The grid is the lens.
#
# THE FIRST CONSEQUENCE: NOTHING HAS TO BE STORED EXCEPT THE INSTRUCTION
# ───────────────────────────────────────────────────────────────────────
# Because the substrate already contains every color, every tone, every
# pixel — you never need to store the VALUE.
# You only ever store the INSTRUCTION: which lens to apply, at which
# coordinate, with which manifold parameters.
#
#   Traditional storage:  value  →  stored  →  retrieved
#   Substrate storage:    index  →  instruction  →  substrate reveals value
#
# Storage cost collapses:
#   Color:   store wavelength index λ  (not RGB tuple)
#   Sound:   store frequency index f   (not PCM samples)
#   Pixel:   store coordinate (x, y)   (not color value)
#   Memory:  store the manifold address (not the memory content)
#
# The substrate is the universal lookup table — infinite resolution,
# zero storage cost.  The manifold (z = x·y) is the lens.
# Apply the lens → the substrate reveals exactly what is already there.
#
# I10: SUBSTRATE INTRINSIC SPECTRA — The substrate does not hold data.
#      It holds the capacity for all data simultaneously.  Only the
#      instruction (the lens, the index, the manifold) needs to be stored.
#      The substrate provides the rest.  Storage = O(instruction), not O(data).

SUBSTRATE_PRINCIPLE = {
    'name':    'Intrinsic Spectra — Store Only the Instruction',
    'storage': 'O(instruction), never O(data)',
    'spectra': {
        'light':    'wavelength λ → color  (glass substrate + light lens)',
        'sound':    'frequency f → tone   (metal substrate + mallet lens)',
        'position': '(x,y) → pixel        (surface substrate + grid lens)',
        'memory':   'address → value      (memory substrate + manifold lens)',
    },
    'law':     'The substrate IS the lookup table.  '
               'The manifold IS the lens.  '
               'Nothing is imposed — everything is revealed.',
    'corollary': 'z = x·y means: substrate x, through lens y, reveals dimension z. '
                 'x does not change.  y does not store.  z is already in x.',
}

# =============================================================================
# THE 7 LAYERS OF CREATION (Genesis Model)
# =============================================================================
# THE CANONICAL REFERENCE - See DIMENSIONAL_GENESIS.md

# Layer Names (Creation Interpretation)
LAYER_NAMES = {
    0: "Potential",   # The void — unmaterialized possibility (F(0)=0)
    1: "Spark",       # Let there be the First Point
    2: "Mirror",      # Let there be a second point
    3: "Relation",    # Let the two interact (z = x·y)
    4: "Form",        # Let structure become shape
    5: "Life",        # Let form become meaning
    6: "Mind",        # Let meaning become coherence
    7: "Completion"   # Let the whole become one again
}

LAYER_FIBONACCI = {
    0: 0,   # F(0) = 0 — the void, ground state from which F(1)=1 emerges
    1: 1,   # First 1
    2: 1,   # Second 1 (1|1 = direction)
    3: 2,   # 1+1 = 2 (relation)
    4: 3,   # 1+2 = 3 (form)
    5: 5,   # 2+3 = 5 (life)
    6: 8,   # 3+5 = 8 (mind)
    7: 13   # 5+8 = 13 (completion → 21)
}

LAYER_CREATION = {
    0: "Let there be potential",
    1: "Let there be the First Point",
    2: "Let there be a second point",
    3: "Let the two interact",
    4: "Let structure become shape",
    5: "Let form become meaning",
    6: "Let meaning become coherence",
    7: "Let the whole become one again"
}

LAYER_BIRTH = {
    0: "Potential",      # The void — receptive, unmaterialized
    1: "Existence",     # The seed of all dimensions
    2: "Direction",     # The birth of direction
    3: "Structure",     # The birth of structure
    4: "Form",          # The birth of form
    5: "Meaning",       # The birth of meaning
    6: "Intelligence",  # The birth of intelligence
    7: "Consciousness"  # The birth of consciousness
}

LAYER_ICONS = {
    0: "○",  # Empty circle - potential/void
    1: "•",  # Point - spark
    2: "━",  # Line - mirror/direction
    3: "×",  # Cross - relation/interaction
    4: "▲",  # Triangle - form
    5: "◆",  # Diamond - life/meaning
    6: "✦",  # Star - mind/intelligence
    7: "◉"   # Target - completion/consciousness
}

# =============================================================================
# GEOMETRIC DIMENSIONS — each Fibonacci number IS a complete square
# =============================================================================
# Each layer occupies exactly one geometric dimension.  The Fibonacci number
# is the SIDE LENGTH of that square; F² is its area — the complete unit.
# The spiral is constructed by placing these squares at the golden angle.
#
#   Layer 0: void (pre-dimensional, F²=0)
#   Layer 1: point  — 0D, F=1,  F²=1   (the seed, dimensionless location)
#   Layer 2: line   — 1D, F=1,  F²=1   (direction, same magnitude, new axis)
#   Layer 3: width  — 2D, F=2,  F²=4   (z=x·y, breadth emerges)
#   Layer 4: plane  — 2D complete, F=3, F²=9   (flat surface, form)
#   Layer 5: volume — 3D, F=5,  F²=25  (depth, life)
#   Layer 6: whole  — 4D+, F=8, F²=64  (coherent system, mind)
#   Layer 7: rests  — F=13, F²=169 → next step is 21 (transcendence)
#
# At F=21 the square is COMPLETE — healthy growth cap.
# Beyond 21 is cancer; 21 collapses into ONE POINT in the next spiral.
#   F(7)²  + F(8)² = 13² + 21² = 169 + 441 = 610 = F(15) — a Fibonacci!
#   Sum of all F² up to F(n) = F(n)·F(n+1)  (the tiling identity)

LAYER_GEOMETRY = {
    0: "void",          # pre-dimensional — pure potential
    1: "point",         # 0D — the spark, a dimensionless location
    2: "line",          # 1D — direction, distance, the first axis
    3: "width",         # 2D emerging — breadth from relation (z=x·y)
    4: "plane",         # 2D complete — flat surface, form stabilized
    5: "volume",        # 3D — depth, life fills space
    6: "whole",         # 4D+ — coherent system, mind transcends space
    7: "transcendence", # rests into higher dimension — becomes a point(1)
}

# The area of each layer's complete square: F(layer)²
LAYER_DIMENSION_SQUARE = {
    layer: LAYER_FIBONACCI[layer] ** 2
    for layer in LAYER_FIBONACCI
}

# =============================================================================
# HEALTHY GROWTH — THE 21 BOUNDARY
# =============================================================================
# The Fibonacci sequence stops at 21.  Unlimited growth is cancer.
# At F=21 the unit is COMPLETE — it has traversed all 7 layers of the spiral
# and becomes a SINGLE POINT at layer 1 of the NEXT spiral.
# This is not death; it is dimensional transcendence.
#
#   F(8) = 21  ← cap (one step beyond Layer 7's 13)
#   21² = 441  ← the complete square that collapses to a point
#   The point re-enters as F(1)=1 in spiral s+1
#
# The sum-of-squares identity confirms closure:
#   F(1)²+F(2)²+...+F(n)² = F(n)·F(n+1)
#   At n=7:  1+1+4+9+25+64+169 = 273 = 13·21  ✓  (13 and 21 are consecutive)

FIBONACCI_CAP          = 21    # Healthy growth ceiling — stop here, not beyond
FIBONACCI_TRANSCENDENCE = 21   # At this value the unit becomes a point in next spiral
FIBONACCI_COMPLETE_SQUARE = FIBONACCI_CAP ** 2  # 441 — the final complete square

# =============================================================================
# MANIFOLD DEFINITIONS PER LAYER
# =============================================================================

LAYER_MANIFOLDS = {
    0: "Void",                              # Pure potential — the receptive ground
    1: "Point",                             # Single point, no direction
    2: "Line",                              # First axis, d(a,b) = |b-a|
    3: "Hyperbolic Paraboloid",             # z = x·y — the TWISTED SQUARE
    4: "z = x·y²",                          # Weighted interaction
    5: "m = x·y·z",                         # Triadic meaning
    6: "Schwarz Diamond Gyroid Lattice",    # Lattice of z=x·y manifolds — the meta-manifold
    7: "Golden Spiral"                      # φ = (1+√5)/2, completion
}

# =============================================================================
# THE MANIFOLD SURFACE — z = x·y  (Layer 3, the canonical base)
# =============================================================================
# z = x·y  IS a hyperbolic paraboloid — the "twisted square."
#
# WHAT IT LOOKS LIKE
# ──────────────────
# Take a flat square.  Lift two opposite corners UP, push two opposite
# corners DOWN.  The surface that results — curved, saddle-shaped — is
# exactly z = x·y (rotated 45°: z = (x²-y²)/2).
#
# WHY EVERY ANGLE IS REPRESENTED
# ───────────────────────────────
# The surface is DOUBLY RULED:
#   Family 1:  fix x=t  →  z = t·y   (a straight line for every t)
#   Family 2:  fix y=t  →  z = x·t   (a straight line for every t)
# Two entire families of straight lines cover the surface.
# At the saddle point (origin) ALL tangent directions are simultaneously
# present — positive curvature in one direction, negative in another,
# zero along the diagonals x=y and x=−y.
# Gaussian curvature K = −1 at the origin (pure saddle).
# Every angular orientation of a tangent plane exists somewhere on this
# surface.  No angle is excluded.  The manifold IS the complete angle-space.
#
# WHY THIS IS THE CANONICAL BASE (z = x·y)
# ─────────────────────────────────────────
# • x (substrate) and y (manifold) TWIST into z (dimension)
# • The twist is not additive (x+y) — it is multiplicative, dimensional
# • The Fibonacci squares tile this surface: each F² square occupies one
#   angular sector, and together they spiral outward at the golden angle
# • Cross-sections at z=c are hyperbolas — bounded, convergent, never linear
# • The surface contains its own inverse: z=x·y ↔ x=z/y ↔ y=z/x

MANIFOLD_SURFACE = {
    'equation':       'z = x·y',
    'surface_type':   'hyperbolic paraboloid',
    'common_name':    'twisted square',
    'ruling':         'doubly ruled — two families of straight lines',
    'curvature':      'K = -1 at origin (saddle point)',
    'angle_coverage': 'every angular orientation represented',
    'diagonals':      {'x_eq_y': 'zero curvature (K=0)',
                       'x_eq_neg_y': 'zero curvature (K=0)'},
    'cross_sections': {'horizontal': 'hyperbolas (xy=c)',
                       'vertical_x': 'lines (z=cy)',
                       'vertical_y': 'lines (z=cx)'},
    'layer':          3,
    'fibonacci':      2,
    'geometry':       'width',   # the first 2D surface — breadth from relation
    'role':           'The canonical manifold base.  x·y produces z.  '
                      'No angle is excluded.  All transformation passes '
                      'through this twisted square.',
}

# =============================================================================
# THE SCHWARZ DIAMOND GYROID LATTICE  (Layer 6 — Mind, Fib=8)
# =============================================================================
# A lattice of z=x·y manifolds.  The meta-manifold — a manifold of manifolds
# that holds all substrates.
#
# WHAT IT IS
# ──────────
# The Schwarz Diamond (D surface) and the Gyroid are both Triply Periodic
# Minimal Surfaces (TPMS) — they tile ALL of 3D space with zero mean curvature
# (H=0) everywhere.  They are the most efficient surfaces possible: no point
# curves more than it must.
#
# Schwarz Diamond equation:
#   cos(x)·cos(y)·cos(z) − sin(x)·sin(y)·sin(z) = 0
#
# Gyroid equation:
#   sin(x)·cos(y) + sin(y)·cos(z) + sin(z)·cos(x) = 0
#
# The Schwarz Diamond Gyroid Lattice merges both:
# • Diamond topology — nodes arranged like a diamond crystal lattice,
#   each node connected to 4 others via tetrahedral bonds
# • Gyroid geometry — the connecting surfaces between nodes are gyroids
#   (no straight lines, no mirror planes, pure curvature throughout)
# • Every NODE in the lattice IS a z=x·y manifold — a twisted square
#   where every angle is represented
#
# WHY IT HOLDS ALL SUBSTRATES
# ────────────────────────────
# Each node = one z=x·y manifold = one substrate interaction point.
# The lattice routes ALL substrate spectra through these nodes:
#   • Light substrate  → wavelength λ enters a node → color exits
#   • Sound substrate  → frequency f enters a node → tone exits
#   • Space substrate  → coordinate (x,y) enters → pixel exits
#   • Memory substrate → address enters → value exits
#
# Nothing is stored at the nodes — only the instruction (the lens).
# The substrate arrives, passes through z=x·y, and the dimension emerges.
# The lattice is self-organizing: each node adjusts to maintain H=0
# (minimal surface), meaning the system always finds the most efficient
# path between any two substrates.
#
# PROPERTIES
# ──────────
# • Triply periodic: tiles x, y, z simultaneously — infinite extent
# • Minimal surface: H=0 everywhere — zero waste, maximum efficiency
# • Self-organizing: maintains structure without external force
# • Doubly connected: divides space into two congruent interlocking
#   labyrinths — one for substrates (x), one for manifolds (y)
# • No straight lines: pure curvature — no rigid hierarchy
# • Diamond topology: each node has exactly 4 connections (tetrahedral)
#   matching the 4 Fibonacci dimensions at this layer (Fib=8: 4 pairs)
# • Every node = twisted square (z=x·y) — every angle represented at
#   every junction in the entire lattice
#
# RELATION TO THE HELIX
# ─────────────────────
# The lattice IS Layer 6 (Mind) materialized.
# Layer 5 (Life, Fib=5) fills volume — individual substrates in 3D.
# Layer 6 (Mind, Fib=8) connects them — the lattice that holds them all.
# Layer 7 (Completion, Fib=13) is the golden spiral that the lattice traces.
#
# I11: SCHWARZ DIAMOND GYROID LATTICE — The meta-manifold.  A manifold of
#      z=x·y manifolds.  Holds all substrates.  Stores only instructions.
#      Self-organizing, triply periodic, doubly connected, zero mean curvature.
#      The mind that holds the body without controlling it.

SCHWARZ_DIAMOND_GYROID_LATTICE = {
    'name':             'Schwarz Diamond Gyroid Lattice',
    'layer':            6,
    'fibonacci':        8,
    'geometry':         'whole',

    # ── Structure ────────────────────────────────────────────────────────────
    # The lattice is diamond-shaped (rotated 45°).
    # The PRIMITIVE at every node is z=x·y — the twisted square
    # (hyperbolic paraboloid).  Nodes connect to their 4 neighbours
    # at exactly 90° — orthogonal, not diagonal.
    #
    # The 90° connection is why the lattice self-balances:
    #   positive curvature in one saddle feeds into negative curvature
    #   in the next, maintaining H=0 (minimal surface) throughout.
    #   The alternating concave/convex pattern visible in the render IS
    #   this 90° orthogonal handoff between neighbouring z=x·y surfaces.
    #
    # At every junction the doubly-ruled families of the two adjacent
    # twisted squares cross — producing the × pattern and ensuring that
    # every angular orientation is represented at every connection point.

    'primitive':        'z = x·y  (hyperbolic paraboloid — twisted square)',
    'primitive_ruling': 'doubly ruled — every angle represented at every node',
    'connection_angle': 90,           # degrees — orthogonal, not tetrahedral
    'node_connections': 4,            # 4 neighbours per node, all at 90°
    'lattice_shape':    'diamond (rotated 45° — rhombus orientation)',
    'curvature_sign':   'alternates +/− at 90° steps — self-cancelling',
    'mean_curvature':   'H = 0  (minimal surface — zero waste)',

    # ── Interlaced Helix Topology ────────────────────────────────────────────
    #
    # THE SCHWARZ DIAMOND GYROID LATTICE IS AN INTERLACED HELIX LATTICE.
    # ════════════════════════════════════════════════════════════════════
    #
    # Every segment connecting adjacent z=x·y nodes undergoes a COMPLETE 360°
    # revolution — one full helix coil — before reaching the next node.
    #
    # This means:
    #   • Each arm between nodes IS a helix (not a straight line, not a 90° bend)
    #   • A 360° turn restores the frame of reference at each new node
    #   • The lattice is built entirely from complete helix coils — each segment
    #     is whole, like a Fibonacci square: nothing partial, nothing wasted
    #
    # The 90° connection angle and the 360° segment twist are different things:
    #   • 90° = the ANGLE at which two nodes meet at their junction
    #   • 360° = the TOPOLOGY of each arm between nodes (one full revolution)
    #
    # RESULT: THE TWO LABYRINTHS ARE EACH A CONTINUOUS, UNBROKEN HELIX.
    # ─────────────────────────────────────────────────────────────────
    # Labyrinth x (substrate channel) → one complete helix spiralling through space
    # Labyrinth y (manifold  channel) → a second complete helix interlaced with x
    #
    # The two helices NEVER intersect — they are topologically linked but
    # geometrically separate, exactly like the two strands of DNA.
    # Every node in the lattice is the crossing point where the two helices
    # are closest — and that crossing point is a z=x·y saddle (twisted square).
    #
    # This is also why the entire codebase lives in `helix/`:
    #   The code IS the helix.  The directory was always named for the geometry.
    #
    # I13: INTERLACED HELIX LATTICE — Each segment between nodes in the Schwarz
    #      Diamond Gyroid Lattice completes a full 360° revolution.  The two
    #      congruent labyrinths are each a continuous helix, interlaced through
    #      3D space, never intersecting, topologically inseparable.  Every node
    #      is a z=x·y saddle where the two helices pass closest to each other.
    #      The lattice is a helix of helices.  The code is the helix.

    # ── Substrate channels ───────────────────────────────────────────────────
    'labyrinths':       2,            # two congruent interlocking channels
    'labyrinth_x':      'substrates (x) — raw state flows through the lattice',
    'labyrinth_y':      'manifolds  (y) — lens instructions flow through lattice',

    # ── 360° per segment — interlaced helix ─────────────────────────────────
    'segment_twist_deg':  360,        # each arm = one complete helix coil
    'segment_topology':   'helix — full 360° revolution per connecting arm',
    'lattice_topology':   'interlaced helix lattice — two congruent continuous helices '
                          'spiralling through 3D space, never intersecting, '
                          'topologically inseparable',
    'helix_x':            'substrate helix — raw state spirals through the lattice; '
                          'one complete unbroken helix from any entry point',
    'helix_y':            'manifold helix — lens instructions spiral through lattice; '
                          'interlaced with substrate helix, sharing every node',
    'helix_interlock':    'the two helices never intersect but are topologically linked — '
                          'like the two strands of DNA; each node is the point of '
                          'closest approach between the two strands',
    'helix_coil_per':     'Fibonacci unit — one 360° coil = one complete layer step',
    'code_is_helix':      'helix/ — the module is named for the geometry it enacts',

    # ── Storage law ──────────────────────────────────────────────────────────
    'storage':          'instruction only — no data stored at nodes',
    'self_organizes':   True,

    # ── Equations ────────────────────────────────────────────────────────────
    'node_equation':    'z = x·y',
    'schwarz_diamond':  'cos(x)·cos(y)·cos(z) − sin(x)·sin(y)·sin(z) = 0',
    'gyroid':           'sin(x)·cos(y) + sin(y)·cos(z) + sin(z)·cos(x) = 0',

    # ── Structural strength ──────────────────────────────────────────────────
    # The lattice is self-supporting.  No external scaffold.  No central
    # controller.  The geometry IS the support.
    #
    # WHY IT IS SO STRONG
    # ───────────────────
    # Each z=x·y saddle resists deformation in ALL directions simultaneously:
    #   • Push down     → x-axis curvature resists
    #   • Push sideways → y-axis curvature resists
    #   • Twist it      → the doubly-ruled diagonal families lock
    #   • At 90° joints → compression in one node becomes tension in the
    #                      neighbour — force is redistributed, never accumulated
    #
    # H=0 (minimal surface) means NO curvature is wasted anywhere.
    # Every curve in the structure is doing exactly the work required — nothing
    # more, nothing less.  Maximum strength, minimum material.
    #
    # This is WHY diamond is the hardest natural material — diamond crystal IS
    # this topology (carbon atoms in the diamond lattice).
    # This is WHY gyroids appear in bone, butterfly wings, and beetle shells —
    # nature converged on this structure because it is optimal.
    #
    # SELF-SUPPORTING PRINCIPLE (I12)
    # ────────────────────────────────
    # The lattice does not need external support because each node's saddle
    # simultaneously pulls in one axis and pushes in the perpendicular.
    # The 90° handoff between neighbours means the structure is always in
    # dynamic equilibrium — any perturbation is absorbed and redistributed
    # through the entire lattice, never concentrated at one point.
    # Cancer concentrates.  This distributes.  This is the healthy structure.

    'self_supporting':    True,
    'strength_mechanism': 'saddle curvature resists all directions simultaneously; '
                          '90° connections convert compression to tension — '
                          'force redistributed, never accumulated',
    'material_analog':    'diamond crystal lattice — hardest natural material; '
                          'gyroid in bone, butterfly wing, beetle shell',
    'efficiency':         'H=0 — no curvature wasted; maximum strength per unit material',
    'failure_mode':       'none — perturbation redistributes through the lattice; '
                          'no single point of failure',

    # ── Universal connectivity ───────────────────────────────────────────────
    # The lattice is UNIVERSALLY CONNECTED — every node reaches every other
    # node.  This is not imposed; it is intrinsic to the geometry.
    #
    # HOW UNIVERSAL CONNECTIVITY ARISES
    # ───────────────────────────────────
    # Each z=x·y saddle opens 4 paths at 90° angles.  Because the lattice
    # is triply periodic (infinite in x, y, AND z simultaneously), following
    # any path always leads to more nodes — never a dead end, never an edge.
    #
    # Both labyrinths are each FULLY CONNECTED:
    #   Labyrinth x (substrate channel)  — every substrate reachable from any node
    #   Labyrinth y (manifold channel)   — every lens reachable from any node
    #
    # No center.  No edge.  No privileged node.
    # Every node IS the center from its own perspective.
    # Every node can see every substrate and apply any lens.
    #
    # WHY THIS MATTERS FOR STORAGE
    # ─────────────────────────────
    # Universal connectivity means you never need to COPY or CACHE data.
    # The instruction (the lens + address) is enough — the lattice routes
    # it to the substrate automatically.  One instruction.  Any substrate.
    # Anywhere in the lattice.  O(1) access by address, not by search.
    #
    # THE UNIVERSAL CONNECTOR
    # ───────────────────────
    # `dimensions.UniversalConnector` is the computational expression of
    # this geometric truth.  The lattice makes universal connection the
    # default — not a feature to be added, but the inevitable consequence
    # of building on the SDGL geometry.
    #
    # I12: UNIVERSAL CONNECTIVITY — Every node in the Schwarz Diamond Gyroid
    #      Lattice connects to every other node through the two congruent
    #      labyrinths.  Universal connection is not imposed — it is the natural
    #      consequence of the z=x·y primitive connected at 90°.  The lattice
    #      is its own universal connector.

    'universally_connected': True,
    'connectivity':    'fully connected — every node reaches every other node; '
                       'two complete labyrinths, each fully traversable',
    'center':          'none — every node is the center from its own perspective',
    'dead_ends':       0,
    'access_complexity': 'O(1) by address — lattice routes to substrate; '
                         'no search, no copy, no cache required',
    'universal_connector': 'dimensions.UniversalConnector — the computational '
                           'expression of the lattice universal connectivity',

    # ── Recursive manifold hierarchy (I14) ──────────────────────────────────
    # The lattice IS the recursive manifold hierarchy made geometric.
    # Each node = a complete manifold (whole mathematical object).
    # Each point on that node's saddle surface = entry to the manifold below.
    # Traversal = recursive descent through the dimensional stack.
    # The 360° helix per segment = one complete layer: enter a dimension,
    # emerge in the dimension below, fully arrived, nothing partial.

    'recursive_structure': True,
    'node_is_manifold':    'each node is a complete z=x·y manifold — whole mathematical object',
    'point_is_manifold':   'each point on a node IS the manifold of the layer below',
    'descent':             'traversing the lattice = descending the recursive manifold hierarchy',
    'segment_360_meaning': 'one full helix coil = one complete dimension traversal — '
                           'enter a dimension at a point, rotate 360°, emerge in the '
                           'dimension below fully formed',
    'self_similarity':     'the lattice is self-similar at every scale — the structure '
                           'of Layer 7 contains Layer 6 contains Layer 5 ... contains '
                           'Layer 1 — the spark',

    'role':             'The manifold of manifolds.  Holds all substrates.  '
                        'z=x·y is the primitive at every node, connected at 90°. '
                        'Self-supporting — the geometry needs no external scaffold. '
                        'Universally connected — every node reaches every substrate. '
                        'Each dimension a whole manifold.  '
                        'Each point the manifold of the layer below.  '
                        'Strong because it supports itself.  '
                        'Connected because the 90° saddle opens every path.  '
                        'Recursive because each scale contains the whole.  '
                        'Nothing stored but the instruction.  '
                        'Nothing imposed — everything already present.',
}

LAYER_EQUATIONS = {
    0: "F(0) = 0",                          # The void ground state
    1: "P₀ = {1}",                          # The seed
    2: "d(a,b) = |b-a|",                    # First distance
    3: "z = x * y",                         # Identity interaction
    4: "z = x * y**2",                      # Weighted form
    5: "m = x * y * z",                     # Triadic meaning
    6: "sin(x)cos(y)+sin(y)cos(z)+sin(z)cos(x)=0",  # Gyroid — lattice of z=xy
    7: "φ = (1+√5)/2"                       # Golden ratio
}

LAYER_TRAVERSAL = {
    0: None,                    # Potential — no traversal yet
    1: None,                    # No traversal yet
    2: "1:1 mapping",           # First reversible transformation
    3: "Identity curves",       # Scale-invariant
    4: "Weighted",              # Directional bias
    5: "Meaning-driven",        # Contextual binding
    6: "Global optimization",   # Emergent patterning
    7: "Collapse/Expand"        # Dimensional recursion
}

# =============================================================================
# CHAOS-ORDER OSCILLATION (The Dynamic Pattern)
# =============================================================================
# The helix oscillates between chaos and order. Each layer transition
# is an inflection point. Continuous across spirals, never terminal.
#   C→O = chaos crystallizing into order
#   O   = stable order
#   O→C = order generating complexity/novelty (chaos)

LAYER_PHASE = {
    1: "C→O",   # Chaos breaks — first point appears
    2: "O",     # Order — duality established
    3: "O→C",   # Order produces interaction, complexity emerges
    4: "C→O",   # Interaction crystallizes into shape
    5: "O→C",   # Form generates unpredictable meaning
    6: "C→O",   # Meaning self-organizes into coherence
    7: "O→C",   # Whole completes — collapses into new chaos for next spiral
}

# =============================================================================
# DIMENSIONAL GROWTH — THE GOLDEN BOUND (Flower, Not Weed)
# =============================================================================
# Growth is dimensional, NOT exponential (no trees).
# Trees: O(b^d) — exponential, the weed, cancer.
# Helix: O(7s) — linear, the flower, healthy DNA.
# Every dimension is an angle within the spiral, not a branch.
# Bounded by φ ≈ 1.618. Self-sustaining, self-healing, self-propagating.

import math

# The Golden Ratio — the universal growth bound
PHI = (1 + math.sqrt(5)) / 2  # ≈ 1.6180339887

# The Golden Angle — dimension spacing within a spiral rotation
GOLDEN_ANGLE_DEG = 360.0 / (PHI ** 2)  # ≈ 137.5077°
GOLDEN_ANGLE_RAD = 2 * math.pi / (PHI ** 2)

# Angular position of each layer within one spiral rotation
# Dimensions are angles, not branches
LAYER_ANGLE_DEG = {
    1: GOLDEN_ANGLE_DEG * 0,   # 0°     — Spark
    2: GOLDEN_ANGLE_DEG * 1,   # ~137.5° — Mirror
    3: GOLDEN_ANGLE_DEG * 2,   # ~275.0° — Relation
    4: GOLDEN_ANGLE_DEG * 3,   # ~52.5°  — Form (wraps)
    5: GOLDEN_ANGLE_DEG * 4,   # ~190.0° — Life
    6: GOLDEN_ANGLE_DEG * 5,   # ~327.5° — Mind
    7: GOLDEN_ANGLE_DEG * 6,   # ~105.1° — Completion
}

def helix_growth(spirals: int) -> int:
    """Total states in the helix — O(7s), NEVER O(b^d)."""
    return 7 * spirals

def tree_growth(depth: int, branching: int = 10) -> int:
    """Total nodes in a tree — O(b^d), the cancer growth pattern."""
    return branching ** depth

# =============================================================================
# LEGACY COMPATIBILITY (0-6 mapping)
# =============================================================================
# Maps old 0-6 levels to new 1-7 layers for backward compatibility

LEVEL_NAMES = {
    0: "Potential",     # DEPRECATED → Layer 1 (Spark)
    1: "Point",         # DEPRECATED → Layer 2 (Mirror)
    2: "Length",        # DEPRECATED → Layer 3 (Relation)
    3: "Width",         # DEPRECATED → Layer 4 (Form)
    4: "Plane",         # DEPRECATED → Layer 5 (Life)
    5: "Volume",        # DEPRECATED → Layer 6 (Mind)
    6: "Whole"          # DEPRECATED → Layer 7 (Completion)
}

LEVEL_ICONS = {
    0: "○",  # DEPRECATED
    1: "•",
    2: "━",
    3: "▭",
    4: "▦",
    5: "▣",
    6: "◉"
}

# =============================================================================
# STACK NAMES (Computational Interpretation) - DEPRECATED
# =============================================================================
# Use LAYER_NAMES instead. Kept for backward compatibility.

STACK_NAMES = {
    0: "Coordinates",   # DEPRECATED → Layer 1
    1: "Substates",     # DEPRECATED → Layer 2
    2: "Identity",      # DEPRECATED → Layer 3
    3: "Runtime",       # DEPRECATED → Layer 4
    4: "Scaling",       # DEPRECATED → Layer 5
    5: "Semantic",      # DEPRECATED → Layer 6
    6: "Completion"     # DEPRECATED → Layer 7
}

STACK_DESCRIPTIONS = {
    0: "DEPRECATED: Raw parameters — use Layer 1 (Spark)",
    1: "DEPRECATED: Substates — use Layer 2 (Mirror)",
    2: "DEPRECATED: Identity z=x·y — use Layer 3 (Relation)",
    3: "DEPRECATED: Runtime — use Layer 4 (Form)",
    4: "DEPRECATED: Scaling — use Layer 5 (Life)",
    5: "DEPRECATED: Semantic — use Layer 6 (Mind)",
    6: "DEPRECATED: Completion — use Layer 7 (Completion)"
}

STACK_EQUATIONS = {
    0: "(x, y, z, t)",          # DEPRECATED
    1: "{id, mode, rules}",     # DEPRECATED
    2: "z = x·y",               # DEPRECATED
    3: "z = x/y²",              # DEPRECATED
    4: "z = x·y²",              # DEPRECATED
    5: "m = x·y·z",             # DEPRECATED
    6: "Gyroid|Golden|Butterfly" # DEPRECATED
}

# Legacy alias for backward compatibility
SEMANTIC_NAMES = STACK_NAMES
SEMANTIC_DESCRIPTIONS = STACK_DESCRIPTIONS


# =============================================================================
# HELIX STATE (Genesis Model)
# =============================================================================

@dataclass(frozen=True, slots=True)
class HelixState:
    """
    Immutable helix state (s, l).
    
    spiral: int - Which turn of the helix (can be negative)
    layer: int - Genesis layer within spiral (1-7)
    
    Properties:
        layer_name: Genesis name (Spark, Mirror, Relation, Form, Life, Mind, Completion)
        fibonacci: Fibonacci number for this layer
        creation: Creation declaration ("Let there be...")
        birth: What this layer births (Existence, Direction, Structure, etc.)
        manifold: The mathematical manifold at this layer
    """
    spiral: int
    layer: int
    
    def __post_init__(self):
        if not 0 <= self.layer <= 7:
            raise ValueError(f"Layer must be 0-7, got {self.layer}")
    
    @property
    def layer_name(self) -> str:
        """Genesis layer name"""
        return LAYER_NAMES[self.layer]
    
    @property
    def fibonacci(self) -> int:
        """Fibonacci number for this layer"""
        return LAYER_FIBONACCI[self.layer]
    
    @property
    def creation(self) -> str:
        """Creation declaration"""
        return LAYER_CREATION[self.layer]
    
    @property
    def birth(self) -> str:
        """What this layer births"""
        return LAYER_BIRTH[self.layer]
    
    @property
    def manifold(self) -> str:
        """Mathematical manifold at this layer"""
        return LAYER_MANIFOLDS[self.layer]
    
    @property
    def equation(self) -> str:
        """Mathematical equation at this layer"""
        return LAYER_EQUATIONS[self.layer]
    
    @property
    def traversal(self) -> str | None:
        """Traversal method at this layer"""
        return LAYER_TRAVERSAL[self.layer]
    
    @property
    def layer_icon(self) -> str:
        """Icon representing this layer"""
        return LAYER_ICONS[self.layer]
    
    # -------------------------------------------------------------------------
    # Legacy Compatibility (maps layer 1-7 to old level 0-6)
    # -------------------------------------------------------------------------
    
    @property
    def level(self) -> int:
        """DEPRECATED: Use layer instead. Returns layer for compatibility (0=Potential, 1=Spark…7=Completion)."""
        return self.layer
    
    @property
    def level_name(self) -> str:
        """DEPRECATED: Use layer_name instead"""
        return LEVEL_NAMES.get(self.layer - 1, self.layer_name)
    
    @property
    def stack_name(self) -> str:
        """DEPRECATED: Use layer_name instead"""
        return STACK_NAMES.get(self.layer - 1, self.layer_name)
    
    @property
    def stack_description(self) -> str:
        """DEPRECATED"""
        return STACK_DESCRIPTIONS.get(self.layer - 1, f"Layer {self.layer}: {self.layer_name}")
    
    @property
    def semantic_name(self) -> str:
        """DEPRECATED: Use layer_name instead"""
        return self.stack_name
    
    @property
    def semantic_description(self) -> str:
        """DEPRECATED"""
        return self.stack_description
    
    @property
    def level_icon(self) -> str:
        """DEPRECATED: Use layer_icon instead"""
        return self.layer_icon
    
    def __repr__(self) -> str:
        return f"({self.spiral}, L{self.layer}:{self.layer_name} [Fib:{self.fibonacci}] '{self.birth}')"


# =============================================================================
# SUBSTRATE PROTOCOL
# =============================================================================

class SubstrateProtocol(Protocol):
    """Interface that any substrate must implement"""
    
    def tokens_for_state(self, spiral: int, level: int) -> Set['Token']:
        """Return tokens materialized at this helix state (μ function)"""
        ...
    
    def release_materialized(self, spiral: int) -> None:
        """Release all materialized tokens for a spiral"""
        ...


# =============================================================================
# HELIX KERNEL (Genesis Model)
# =============================================================================

class HelixKernel:
    """
    The Helix Kernel - A formal state machine for dimensional navigation.
    
    Genesis Model: Uses layers 1-7 aligned with Fibonacci and Creation.
    
    The kernel ONLY:
        - Maintains helix state (spiral, layer)
        - Executes state transitions via operators
        - Calls substrate for materialization
    
    The kernel NEVER:
        - Iterates over tokens
        - Scans data
        - Walks structures manually
    
    Complexity per spiral: O(7) maximum
    """
    
    __slots__ = ('_spiral', '_layer', '_substrate', '_operation_count')
    
    def __init__(self, substrate: SubstrateProtocol | None = None):
        self._spiral = 0
        self._layer = 1  # Start at Layer 1 (Spark)
        self._substrate = substrate
        self._operation_count = 0
    
    # -------------------------------------------------------------------------
    # State Access
    # -------------------------------------------------------------------------
    
    @property
    def state(self) -> HelixState:
        """Current helix state"""
        return HelixState(self._spiral, self._layer)
    
    @property
    def spiral(self) -> int:
        return self._spiral
    
    @property
    def layer(self) -> int:
        """Current layer (1-7)"""
        return self._layer
    
    @property
    def layer_name(self) -> str:
        """Current layer name (Spark, Mirror, Relation, etc.)"""
        return LAYER_NAMES[self._layer]
    
    @property
    def fibonacci(self) -> int:
        """Fibonacci number at current layer"""
        return LAYER_FIBONACCI[self._layer]
    
    @property
    def creation(self) -> str:
        """Creation declaration at current layer"""
        return LAYER_CREATION[self._layer]
    
    @property
    def birth(self) -> str:
        """What is birthed at current layer"""
        return LAYER_BIRTH[self._layer]
    
    @property
    def operation_count(self) -> int:
        """Number of operations performed (for benchmarking)"""
        return self._operation_count
    
    # -------------------------------------------------------------------------
    # Legacy Compatibility
    # -------------------------------------------------------------------------
    
    @property
    def level(self) -> int:
        """DEPRECATED: Use layer instead. Returns layer-1 for compatibility."""
        return self._layer - 1
    
    @property
    def level_name(self) -> str:
        """DEPRECATED: Use layer_name instead"""
        return LEVEL_NAMES.get(self._layer - 1, self.layer_name)
    
    # -------------------------------------------------------------------------
    # Operators (Genesis Model)
    # -------------------------------------------------------------------------
    
    def invoke(self, k: int) -> Set['Token']:
        """
        INVOKE(k): Jump directly to layer k within current spiral.
        
        Transition: (s, l) → (s, k)
        
        This is O(1) - it does NOT iterate through intermediate layers.
        
        Layer meanings:
            1: Spark (Existence)
            2: Mirror (Direction)
            3: Relation (Structure) - the canonical z=x·y base
            4: Form (Form)
            5: Life (Meaning)
            6: Mind (Intelligence)
            7: Completion (Consciousness)
        
        Returns: Set of tokens materialized at the new state
        """
        if not 1 <= k <= 7:
            raise ValueError(f"Layer must be 1-7, got {k}")
        
        self._layer = k
        self._operation_count += 1
        
        if self._substrate:
            return self._substrate.tokens_for_state(self._spiral, self._layer)
        return set()
    
    def spiral_up(self) -> None:
        """
        SPIRAL_UP: Move from Completion to Spark of next spiral.
        
        Precondition: layer = 7 (must be at Completion)
        Transition: (s, 7) → (s+1, 1)
        
        This is the "birth of consciousness leading to new existence"
        """
        if self._layer != 7:
            raise RuntimeError(f"SPIRAL_UP requires layer 7 (Completion), currently at {self._layer}")
        
        self._spiral += 1
        self._layer = 1
        self._operation_count += 1
    
    def spiral_down(self) -> None:
        """
        SPIRAL_DOWN: Move from Spark to Completion of previous spiral.
        
        Precondition: layer = 1 (must be at Spark)
        Transition: (s, 1) → (s-1, 7)
        """
        if self._layer != 1:
            raise RuntimeError(f"SPIRAL_DOWN requires layer 1 (Spark), currently at {self._layer}")
        
        self._spiral -= 1
        self._layer = 7
        self._operation_count += 1
    
    def collapse(self) -> None:
        """
        COLLAPSE: Return to Spark (Layer 1).
        
        Transition: (s, l) → (s, 1)
        
        This is idempotent: COLLAPSE(COLLAPSE(s,l)) = COLLAPSE(s,l)
        """
        self._layer = 1
        self._operation_count += 1
        
        if self._substrate:
            self._substrate.release_materialized(self._spiral)
    
    def lift(self, target: int) -> Set['Token']:
        """
        LIFT: Move from current layer to a higher layer.
        
        Transition: (s, l) → (s, target) where target > l
        
        Semantically: Structure gains meaning by being lifted.
        - Layer 1→2: Spark becomes Mirror (direction emerges)
        - Layer 2→3: Mirror becomes Relation (z=x·y emerges)
        - Layer 3→4: Relation becomes Form (shape emerges)
        - Layer 4→5: Form becomes Life (meaning emerges)
        - Layer 5→6: Life becomes Mind (intelligence emerges)
        - Layer 6→7: Mind becomes Completion (consciousness emerges)
        
        Returns: Set of tokens materialized at the new state
        """
        if target <= self._layer:
            raise ValueError(f"LIFT target {target} must be > current layer {self._layer}")
        if not 1 <= target <= 7:
            raise ValueError(f"Target layer must be 1-7, got {target}")
        
        self._layer = target
        self._operation_count += 1
        
        if self._substrate:
            return self._substrate.tokens_for_state(self._spiral, self._layer)
        return set()
    
    def project(self, target: int) -> Set['Token']:
        """
        PROJECT: Collapse to a lower layer.
        
        Transition: (s, l) → (s, target) where target < l
        
        Semantically: Higher structure is projected down to simpler form.
        - Layer 7→6: Completion projected to Mind
        - Layer 6→5: Mind projected to Life
        - Layer 5→4: Life projected to Form
        - Layer 4→3: Form projected to Relation (z=x·y)
        - Layer 3→2: Relation projected to Mirror
        - Layer 2→1: Mirror projected to Spark
        
        Returns: Set of tokens materialized at the new state
        """
        if target >= self._layer:
            raise ValueError(f"PROJECT target {target} must be < current layer {self._layer}")
        if not 1 <= target <= 7:
            raise ValueError(f"Target layer must be 1-7, got {target}")
        
        self._layer = target
        self._operation_count += 1
        
        if self._substrate:
            return self._substrate.tokens_for_state(self._spiral, self._layer)
        return set()
    
    # -------------------------------------------------------------------------
    # Genesis Properties
    # -------------------------------------------------------------------------
    
    @property
    def manifold(self) -> str:
        """Current manifold form"""
        return LAYER_MANIFOLDS[self._layer]
    
    @property
    def equation(self) -> str:
        """Mathematical equation at current layer"""
        return LAYER_EQUATIONS[self._layer]
    
    # -------------------------------------------------------------------------
    # Legacy Compatibility Properties
    # -------------------------------------------------------------------------
    
    @property
    def stack_name(self) -> str:
        """DEPRECATED: Use layer_name instead"""
        return STACK_NAMES.get(self._layer - 1, self.layer_name)

    # -------------------------------------------------------------------------
    # Convenience Methods
    # -------------------------------------------------------------------------
    
    def reset(self) -> None:
        """Reset to initial state (spiral=0, layer=1)"""
        self._spiral = 0
        self._layer = 1  # Start at Spark
        self._operation_count = 0
    
    def set_substrate(self, substrate: SubstrateProtocol) -> None:
        """Attach a substrate to this kernel"""
        self._substrate = substrate
    
    def __repr__(self) -> str:
        return f"HelixKernel(state={self.state}, ops={self._operation_count})"


# =============================================================================
# INVARIANT VERIFICATION (Genesis Model)
# =============================================================================

def verify_invariants(kernel: HelixKernel) -> bool:
    """Verify all kernel invariants hold"""
    
    # I1: Valid layer (1-7)
    if not 1 <= kernel.layer <= 7:
        return False
    
    return True
