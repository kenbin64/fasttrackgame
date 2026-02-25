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
# THE FIRST PRINCIPLE: MANIFOLD DUALITY AND INFINITE POTENTIAL
# =============================================================================
# Every manifold is both a whole object and a dimension.
# Every point is both real and potential.
# Only the invoked is manifest.
#
# Points represent lower dimensions. Each point is a subpart of its parent
# manifold and is itself a manifold (M ⊃ Mᵢ ⊃ Mᵢⱼ ⊃ ...).
# Resolution descends iteratively — atoms, quarks — as deep as needed.
# The set of potentials is practically infinite. Like quantum superposition,
# the periodic table, and atomic structure: only invoked parts are real.

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
# THE 7 LAYERS OF CREATION (Genesis Model)
# =============================================================================
# THE CANONICAL REFERENCE - See DIMENSIONAL_GENESIS.md

# Layer Names (Creation Interpretation)
LAYER_NAMES = {
    1: "Spark",       # Let there be the First Point
    2: "Mirror",      # Let there be a second point
    3: "Relation",    # Let the two interact (z = x·y)
    4: "Form",        # Let structure become shape
    5: "Life",        # Let form become meaning
    6: "Mind",        # Let meaning become coherence
    7: "Completion"   # Let the whole become one again
}

LAYER_FIBONACCI = {
    1: 1,   # First 1
    2: 1,   # Second 1 (1|1 = direction)
    3: 2,   # 1+1 = 2 (relation)
    4: 3,   # 1+2 = 3 (form)
    5: 5,   # 2+3 = 5 (life)
    6: 8,   # 3+5 = 8 (mind)
    7: 13   # 5+8 = 13 (completion → 21)
}

LAYER_CREATION = {
    1: "Let there be the First Point",
    2: "Let there be a second point",
    3: "Let the two interact",
    4: "Let structure become shape",
    5: "Let form become meaning",
    6: "Let meaning become coherence",
    7: "Let the whole become one again"
}

LAYER_BIRTH = {
    1: "Existence",     # The seed of all dimensions
    2: "Direction",     # The birth of direction
    3: "Structure",     # The birth of structure
    4: "Form",          # The birth of form
    5: "Meaning",       # The birth of meaning
    6: "Intelligence",  # The birth of intelligence
    7: "Consciousness"  # The birth of consciousness
}

LAYER_ICONS = {
    1: "•",  # Point - spark
    2: "━",  # Line - mirror/direction
    3: "×",  # Cross - relation/interaction
    4: "▲",  # Triangle - form
    5: "◆",  # Diamond - life/meaning
    6: "✦",  # Star - mind/intelligence
    7: "◉"   # Target - completion/consciousness
}

# =============================================================================
# MANIFOLD DEFINITIONS PER LAYER
# =============================================================================

LAYER_MANIFOLDS = {
    1: "Point",           # Single point, no direction
    2: "Line",            # First axis, d(a,b) = |b-a|
    3: "z = x·y",         # Identity surface (THE CANONICAL BASE)
    4: "z = x·y²",        # Weighted interaction
    5: "m = x·y·z",       # Triadic meaning
    6: "Gyroid",          # Minimal surface, self-organizing
    7: "Golden Spiral"    # φ = (1+√5)/2, completion
}

LAYER_EQUATIONS = {
    1: "P₀ = {1}",              # The seed
    2: "d(a,b) = |b-a|",        # First distance
    3: "z = x * y",             # Identity interaction
    4: "z = x * y**2",          # Weighted form
    5: "m = x * y * z",         # Triadic meaning
    6: "∇²f = λf (minimal)",    # Eigenvalue surface
    7: "φ = (1+√5)/2"           # Golden ratio
}

LAYER_TRAVERSAL = {
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
        if not 1 <= self.layer <= 7:
            raise ValueError(f"Layer must be 1-7, got {self.layer}")
    
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
        """DEPRECATED: Use layer instead. Returns layer-1 for compatibility."""
        return self.layer - 1
    
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
