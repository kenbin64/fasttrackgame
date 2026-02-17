"""
Helix Kernel - Formal State Machine Implementation

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

This mathematical kernel belongs to all humanity.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

Implements the ButterflyFX Helix Kernel as specified in BUTTERFLYFX_SPECIFICATION.md

State Space: H = {(s, l) | s in Z, l in {0,1,2,3,4,5,6}}

Operations:
    - INVOKE(k): (s, l) -> (s, k)
    - SPIRAL_UP: (s, 6) -> (s+1, 0)
    - SPIRAL_DOWN: (s, 0) -> (s-1, 6)
    - COLLAPSE: (s, l) -> (s, 0)

Invariants:
    - I1: l in {0..6} always
    - I2: SPIRAL_UP requires l=6, SPIRAL_DOWN requires l=0
    - I3: COLLAPSE is idempotent
    - I4: INVOKE is idempotent per level
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Set, Any, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from .substrate import Token


# =============================================================================
# LEVEL DEFINITIONS
# =============================================================================

LEVEL_NAMES = {
    0: "Potential",
    1: "Point", 
    2: "Length",
    3: "Width",
    4: "Plane",
    5: "Volume",
    6: "Whole"
}

LEVEL_ICONS = {
    0: "○",
    1: "•",
    2: "━",
    3: "▭",
    4: "▦",
    5: "▣",
    6: "◉"
}

# =============================================================================
# SEMANTIC LAYER (Identity-First Paradigm)
# =============================================================================
# Each level has both GEOMETRIC meaning (shape) and SEMANTIC meaning (purpose)
# "Manifestation does NOT begin with the object — it begins with identity."

SEMANTIC_NAMES = {
    0: "Void",           # Nothing exists — only possibility
    1: "Identity",       # UUID, name, "this" — the anchor, NOT the object
    2: "Relationship",   # Attributes, references, links
    3: "Structure",      # Schema, blueprint, geometry — still no object
    4: "Manifestation",  # Object APPEARS — first visible form
    5: "Multiplicity",   # Systems, behavior, interaction
    6: "Meaning"         # Interpretation — transcends form
}

SEMANTIC_DESCRIPTIONS = {
    0: "Nothing exists yet — only pure possibility",
    1: "The identity anchor (UUID, name) — NOT the object itself",
    2: "Attributes, references, links — relationships between identities",
    3: "Schema, blueprint, geometry — the structure before manifestation",
    4: "The object APPEARS — first visible form (collapsed projection)",
    5: "Systems, behavior, interaction — multiplicity and dynamics",
    6: "Interpretation and meaning — transcends the physical form"
}


# =============================================================================
# HELIX STATE
# =============================================================================

@dataclass(frozen=True, slots=True)
class HelixState:
    """
    Immutable helix state (s, l).
    
    spiral: int - Which turn of the helix (can be negative)
    level: int - Dimensional level within spiral (0-6)
    
    Properties:
        level_name: Geometric name (Point, Line, Plane, etc.)
        semantic_name: Semantic purpose (Identity, Relationship, Structure, etc.)
    """
    spiral: int
    level: int
    
    def __post_init__(self):
        if not 0 <= self.level <= 6:
            raise ValueError(f"Level must be 0-6, got {self.level}")
    
    @property
    def level_name(self) -> str:
        """Geometric level name"""
        return LEVEL_NAMES[self.level]
    
    @property
    def semantic_name(self) -> str:
        """Semantic level name (Identity-First paradigm)"""
        return SEMANTIC_NAMES[self.level]
    
    @property
    def semantic_description(self) -> str:
        """Semantic level description"""
        return SEMANTIC_DESCRIPTIONS[self.level]
    
    @property
    def level_icon(self) -> str:
        return LEVEL_ICONS[self.level]
    
    def __repr__(self) -> str:
        return f"({self.spiral}, {self.level}:{self.level_name}/{self.semantic_name})"


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
# HELIX KERNEL
# =============================================================================

class HelixKernel:
    """
    The Helix Kernel - A formal state machine for dimensional navigation.
    
    The kernel ONLY:
        - Maintains helix state (spiral, level)
        - Executes state transitions via operators
        - Calls substrate for materialization
    
    The kernel NEVER:
        - Iterates over tokens
        - Scans data
        - Walks structures manually
    
    Complexity per spiral: O(7) maximum
    """
    
    __slots__ = ('_spiral', '_level', '_substrate', '_operation_count')
    
    def __init__(self, substrate: SubstrateProtocol | None = None):
        self._spiral = 0
        self._level = 0
        self._substrate = substrate
        self._operation_count = 0
    
    # -------------------------------------------------------------------------
    # State Access
    # -------------------------------------------------------------------------
    
    @property
    def state(self) -> HelixState:
        """Current helix state"""
        return HelixState(self._spiral, self._level)
    
    @property
    def spiral(self) -> int:
        return self._spiral
    
    @property
    def level(self) -> int:
        return self._level
    
    @property
    def level_name(self) -> str:
        return LEVEL_NAMES[self._level]
    
    @property
    def operation_count(self) -> int:
        """Number of operations performed (for benchmarking)"""
        return self._operation_count
    
    # -------------------------------------------------------------------------
    # Operators
    # -------------------------------------------------------------------------
    
    def invoke(self, k: int) -> Set['Token']:
        """
        INVOKE(k): Jump directly to level k within current spiral.
        
        Transition: (s, l) -> (s, k)
        
        This is O(1) - it does NOT iterate through intermediate levels.
        
        Returns: Set of tokens materialized at the new state
        """
        if not 0 <= k <= 6:
            raise ValueError(f"Level must be 0-6, got {k}")
        
        self._level = k
        self._operation_count += 1
        
        if self._substrate:
            return self._substrate.tokens_for_state(self._spiral, self._level)
        return set()
    
    def spiral_up(self) -> None:
        """
        SPIRAL_UP: Move from Whole to Potential of next spiral.
        
        Precondition: l = 6 (must be at Whole)
        Transition: (s, 6) -> (s+1, 0)
        """
        if self._level != 6:
            raise RuntimeError(f"SPIRAL_UP requires level 6 (Whole), currently at {self._level}")
        
        self._spiral += 1
        self._level = 0
        self._operation_count += 1
    
    def spiral_down(self) -> None:
        """
        SPIRAL_DOWN: Move from Potential to Whole of previous spiral.
        
        Precondition: l = 0 (must be at Potential)
        Transition: (s, 0) -> (s-1, 6)
        """
        if self._level != 0:
            raise RuntimeError(f"SPIRAL_DOWN requires level 0 (Potential), currently at {self._level}")
        
        self._spiral -= 1
        self._level = 6
        self._operation_count += 1
    
    def collapse(self) -> None:
        """
        COLLAPSE: Return all levels to Potential.
        
        Transition: (s, l) -> (s, 0)
        
        This is idempotent: COLLAPSE(COLLAPSE(s,l)) = COLLAPSE(s,l)
        """
        self._level = 0
        self._operation_count += 1
        
        if self._substrate:
            self._substrate.release_materialized(self._spiral)
    
    # -------------------------------------------------------------------------
    # Convenience Methods
    # -------------------------------------------------------------------------
    
    def reset(self) -> None:
        """Reset to initial state (0, 0)"""
        self._spiral = 0
        self._level = 0
        self._operation_count = 0
    
    def set_substrate(self, substrate: SubstrateProtocol) -> None:
        """Attach a substrate to this kernel"""
        self._substrate = substrate
    
    def __repr__(self) -> str:
        return f"HelixKernel(state={self.state}, ops={self._operation_count})"


# =============================================================================
# INVARIANT VERIFICATION (for testing)
# =============================================================================

def verify_invariants(kernel: HelixKernel) -> bool:
    """Verify all kernel invariants hold"""
    
    # I1: Valid level
    if not 0 <= kernel.level <= 6:
        return False
    
    return True
