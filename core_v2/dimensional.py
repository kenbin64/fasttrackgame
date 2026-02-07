"""
Dimensional Programming Implementation

═══════════════════════════════════════════════════════════════════
                    DIMENSIONAL SUBSTRATE API
═══════════════════════════════════════════════════════════════════

FUNDAMENTAL PRINCIPLE:
    A SUBSTRATE IS A DIMENSIONAL OBJECT.
    A SUBSTRATE IS A SINGLE POINT IN A HIGHER DIMENSION.
    A POINT CONTAINS ALL DIMENSIONS UNDERNEATH IT FROM 0D TO nD.

THE ONE RULE:
    A higher dimension represents a SINGLE POINT of all subsequent
    lower dimensions. There are n potentials in any substrate.
    We do NOT iterate through dimensions — we simply CALL the
    dimension we want, and that IS the point we need.

This module implements the dimensional programming paradigm where:
    - Objects are substrates (dimensional points)
    - Attributes are lenses (views into the substrate)
    - Behavior is deltas (promotion to new states)
    - Animation is promotion (movement through time = 4D)
    - No mutation is allowed (new substrates are created)

Usage:
    from core_v2 import ButterflyFx
    
    fx = ButterflyFx()
    
    # Create dimensional substrate
    obj = fx.substrate({"x": 0, "y": 0})
    
    # Call the dimension you want directly (no iteration)
    behavior = obj.dimension(4)  # This IS the 4D point
                                 # It inherently is the 3D, 2D, 1D, 0D
    
    # Apply lens (view attribute)
    x_value = obj.lens("x").invoke()
    
    # Apply delta (creates NEW substrate)
    moved = obj.apply(fx.delta({"dx": 10}))
    
    # Promote (advance to next state)
    next_state = obj.promote(physics_delta)

═══════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Union, Callable, Tuple, TYPE_CHECKING
from dataclasses import dataclass, field
import time
import json
import struct

if TYPE_CHECKING:
    from .api import ButterflyFx

# Import kernel primitives
from kernel_v2 import (
    SubstrateIdentity,
    Substrate,
    Lens,
    Delta,
    Dimension as KernelDimension,
    Manifold,
    promote as kernel_promote,
    invoke as kernel_invoke,
)


__all__ = [
    'DimensionalSubstrate',
    'DimensionalLens',
    'DimensionalDelta',
    'DimensionalManifold',
    'Dimension',
]


# ═══════════════════════════════════════════════════════════════════
# DIMENSION CONSTANTS
# ═══════════════════════════════════════════════════════════════════

class Dimension:
    """
    Kernel dimension constants.
    
    A substrate at dimension N IS a single point containing all lower dimensions.
    You don't iterate through dimensions - you call the one you want.
    
    0D — Identity Kernel: Pure 64-bit identity (the seed)
    1D — Attribute Kernel: Single point containing 0D + scalars, timestamps
    2D — Relational Kernel: Single point containing 0D+1D + surfaces, grids
    3D — Structural Kernel: Single point containing 0D-2D + volume, geometry
    4D — Behavioral Kernel: Single point containing 0D-3D + motion, physics
    5D — System Kernel: Single point containing 0D-4D + interactions
    6D+ — Emergent Kernel: Single point containing 0D-5D + intelligence
    
    To access dimension N, just call it:
        manifold = substrate.dimension(4)  # Get the 4D point directly
    
    That 4D point IS your 3D, 2D, 1D, 0D - all in one.
    No iteration required.
    """
    IDENTITY = 0
    ATTRIBUTE = 1
    RELATIONAL = 2
    STRUCTURAL = 3
    BEHAVIORAL = 4
    SYSTEM = 5
    EMERGENT = 6
    
    @classmethod
    def name(cls, level: int) -> str:
        """Get the name of a dimension level."""
        names = {
            0: "Identity",
            1: "Attribute",
            2: "Relational",
            3: "Structural",
            4: "Behavioral",
            5: "System",
            6: "Emergent"
        }
        return names.get(level, f"Dimension-{level}")


# ═══════════════════════════════════════════════════════════════════
# MASK
# ═══════════════════════════════════════════════════════════════════

MASK_64 = 0xFFFFFFFFFFFFFFFF


# ═══════════════════════════════════════════════════════════════════
# DIMENSIONAL MANIFOLD
# ═══════════════════════════════════════════════════════════════════

@dataclass
class DimensionalManifold:
    """
    The shape of a substrate at a specific dimension.
    
    A manifold is what you "see" when viewing a substrate
    through a dimensional lens at level N.
    
    IMPORTANT: A manifold at dimension N IS the single point
    that represents all lower dimensions. There is no iteration.
    Just call the dimension you need:
    
        substrate.dimension(4)  # This IS your 4D point
                                # It inherently contains 3D, 2D, 1D, 0D
    
    There are infinite (n) potentials in any substrate.
    Calling a dimension invokes the ONE rule: higher dimension
    represents a single point of all subsequent lower dimensions.
    """
    substrate: 'DimensionalSubstrate'
    dimension: int
    shape: Any = None
    
    @property
    def level(self) -> int:
        """The dimension level."""
        return self.dimension
    
    @property
    def name(self) -> str:
        """The dimension name."""
        return Dimension.name(self.dimension)
    
    @property
    def identity(self) -> int:
        """The substrate identity at this dimension."""
        # Identity is modified by dimension for manifold uniqueness
        base = self.substrate.truth
        return (base ^ (self.dimension * 0x123456789ABCDEF0)) & MASK_64
    
    def lens(self, name: str, **params) -> 'DimensionalLens':
        """Create a lens on this manifold."""
        return DimensionalLens(
            substrate=self.substrate,
            name=name,
            dimension=self.dimension,
            params=params
        )
    
    def project(self, projection: Callable[[int], int]) -> int:
        """Project through a custom function."""
        return projection(self.identity) & MASK_64
    
    def __repr__(self) -> str:
        return f"Manifold({self.name}, id=0x{self.identity:016X})"


# ═══════════════════════════════════════════════════════════════════
# DIMENSIONAL LENS
# ═══════════════════════════════════════════════════════════════════

@dataclass
class DimensionalLens:
    """
    A lens that reveals attributes or functionality from a substrate.
    
    Lenses are how you access attributes dimensionally.
    Attributes are not stored - they are computed through lenses.
    """
    substrate: 'DimensionalSubstrate'
    name: str
    dimension: int = 1  # Default to attribute dimension
    params: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def projection(self) -> Callable[[int], int]:
        """Get the projection function for this lens."""
        # Built-in lens projections
        projections = {
            # Identity projections
            "identity": lambda x: x,
            "hash": lambda x: x,
            
            # Bit projections
            "low_byte": lambda x: x & 0xFF,
            "high_byte": lambda x: (x >> 56) & 0xFF,
            "low_word": lambda x: x & 0xFFFF,
            "high_word": lambda x: (x >> 48) & 0xFFFF,
            "low_dword": lambda x: x & 0xFFFFFFFF,
            "high_dword": lambda x: (x >> 32) & 0xFFFFFFFF,
            
            # Math projections
            "abs": lambda x: x if x < (1 << 63) else (1 << 64) - x,
            "negate": lambda x: ((~x) + 1) & MASK_64,
            "double": lambda x: (x * 2) & MASK_64,
            "half": lambda x: x >> 1,
            "square": lambda x: (x * x) & MASK_64,
            
            # Bit operations
            "popcount": lambda x: bin(x).count('1'),
            "leading_zeros": lambda x: 64 - x.bit_length() if x else 64,
            "trailing_zeros": lambda x: (x & -x).bit_length() - 1 if x else 64,
            "reverse_bits": lambda x: int(bin(x)[2:].zfill(64)[::-1], 2),
            
            # Time projections (dimension 4)
            "now": lambda x: int(time.time()),
            "age": lambda x: int(time.time()) - x,
            "timestamp": lambda x: x,
        }
        
        return projections.get(self.name, lambda x: x)
    
    def invoke(self) -> Any:
        """
        Invoke the lens to reveal the attribute value.
        
        This is the core operation - revealing truth through projection.
        
        THE ONE RULE: The attribute EXISTS because the substrate exists.
        We don't "get" it, we INVOKE it — it's already there.
        
        Supports nested access: "transmission.gears.gear_4.ratio"
        """
        # Get the substrate's data
        if self.substrate._data is not None:
            # Try to extract named attribute from data
            if isinstance(self.substrate._data, dict):
                # Support nested attribute access: "a.b.c"
                value = self.substrate._data
                parts = self.name.split('.')
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    elif isinstance(value, list):
                        try:
                            idx = int(part)
                            value = value[idx]
                        except (ValueError, IndexError):
                            break
                    else:
                        # Attribute path not found, fall back to projection
                        break
                else:
                    # Found the value - return it directly
                    # The value EXISTS because the parent exists
                    return value
        
        # Fall back to projection on identity (for built-in lenses)
        return self.projection(self.substrate.truth) & MASK_64
    
    def __call__(self) -> int:
        """Shorthand for invoke()."""
        return self.invoke()
    
    def __repr__(self) -> str:
        return f"Lens({self.name}, dim={self.dimension})"


# ═══════════════════════════════════════════════════════════════════
# DIMENSIONAL DELTA
# ═══════════════════════════════════════════════════════════════════

@dataclass
class DimensionalDelta:
    """
    A delta that encodes change/behavior.
    
    Deltas are how behavior is applied to substrates.
    Applying a delta produces a NEW substrate (no mutation).
    """
    value: int
    data: Any = None
    generation: int = 0
    
    def __init__(self, value: Any, generation: int = 0):
        """
        Create a delta from any value.
        
        Args:
            value: The delta value (int, float, dict, etc.)
            generation: The generation counter
        """
        self.generation = generation
        self.data = value
        
        if isinstance(value, int):
            self.value = value & MASK_64
        elif isinstance(value, float):
            self.value = struct.unpack('Q', struct.pack('d', value))[0]
        elif isinstance(value, dict):
            # Hash the dict for the delta value
            h = 0x811c9dc5
            for k, v in sorted(value.items()):
                for c in str(k) + str(v):
                    h ^= ord(c)
                    h = (h * 0x01000193) & MASK_64
            self.value = h
        else:
            # Hash any other value
            h = hash(value) & MASK_64
            self.value = h
    
    def combine(self, other: 'DimensionalDelta') -> 'DimensionalDelta':
        """Combine two deltas into one."""
        return DimensionalDelta(
            value=(self.value ^ other.value),
            generation=max(self.generation, other.generation) + 1
        )
    
    def scale(self, factor: float) -> 'DimensionalDelta':
        """Scale the delta by a factor."""
        scaled = int(self.value * factor) & MASK_64
        return DimensionalDelta(value=scaled, generation=self.generation)
    
    def __repr__(self) -> str:
        return f"Delta(0x{self.value:016X}, gen={self.generation})"


# ═══════════════════════════════════════════════════════════════════
# DIMENSIONAL SUBSTRATE
# ═══════════════════════════════════════════════════════════════════

class DimensionalSubstrate:
    """
    A substrate with dimensional programming interface.
    
    This is the core object in dimensional programming.
    Everything is a substrate, and all behavior, attributes,
    and functionality emerge from dimensional relationships.
    
    Usage:
        # Create
        obj = DimensionalSubstrate(data)
        
        # Access dimensions
        identity = obj.dimension(0)    # 0D identity
        attrs = obj.dimension(1)       # 1D attributes
        behavior = obj.dimension(4)    # 4D behavior
        
        # Access attributes via lenses
        x = obj.lens("x").invoke()
        
        # Apply behavior via deltas
        moved = obj.apply(delta)
        
        # Promote to next state
        next_state = obj.promote(delta)
    """
    
    __slots__ = ('_truth', '_data', '_kernel_substrate', '_generation', '_parent', '_fx')
    
    def __init__(
        self, 
        data: Any,
        fx: Optional['ButterflyFx'] = None,
        parent: Optional['DimensionalSubstrate'] = None,
        generation: int = 0
    ):
        """
        Create a dimensional substrate from any data.
        
        Args:
            data: Any Python value to convert to substrate
            fx: The ButterflyFx instance (for internal use)
            parent: Parent substrate (for promoted substrates)
            generation: Generation counter
        """
        self._data = data
        self._fx = fx
        self._parent = parent
        self._generation = generation
        
        # Compute 64-bit identity
        if isinstance(data, int):
            self._truth = data & MASK_64
        elif isinstance(data, float):
            self._truth = struct.unpack('Q', struct.pack('d', data))[0]
        elif isinstance(data, str):
            # FNV-1a hash
            h = 0xcbf29ce484222325
            for c in data:
                h ^= ord(c)
                h = (h * 0x100000001b3) & MASK_64
            self._truth = h
        elif isinstance(data, bytes):
            h = 0xcbf29ce484222325
            for b in data:
                h ^= b
                h = (h * 0x100000001b3) & MASK_64
            self._truth = h
        elif isinstance(data, dict):
            # Hash dict content
            h = 0xcbf29ce484222325
            for k, v in sorted(data.items()):
                for c in str(k) + str(v):
                    h ^= ord(c)
                    h = (h * 0x100000001b3) & MASK_64
            self._truth = h
        elif isinstance(data, (list, tuple)):
            h = 0xcbf29ce484222325
            for item in data:
                for c in str(item):
                    h ^= ord(c)
                    h = (h * 0x100000001b3) & MASK_64
            self._truth = h
        elif hasattr(data, 'truth'):
            # Already a substrate-like object
            self._truth = data.truth & MASK_64
        else:
            # Hash any other object
            self._truth = hash(data) & MASK_64
        
        # Create kernel substrate with expression
        identity = SubstrateIdentity(self._truth)
        # Expression returns the truth value
        self._kernel_substrate = Substrate(identity, lambda t=self._truth: t)
    
    # ─────────────────────────────────────────────────────────────────
    # CORE PROPERTIES
    # ─────────────────────────────────────────────────────────────────
    
    @property
    def truth(self) -> int:
        """The 64-bit substrate identity (x₁)."""
        return self._truth
    
    @property
    def identity(self) -> int:
        """Alias for truth."""
        return self._truth
    
    @property
    def data(self) -> Any:
        """The original data (for lens access)."""
        return self._data
    
    @property
    def generation(self) -> int:
        """The generation (how many promotions from root)."""
        return self._generation
    
    @property
    def kernel_substrate(self) -> Substrate:
        """The underlying kernel substrate."""
        return self._kernel_substrate
    
    # ─────────────────────────────────────────────────────────────────
    # DIMENSIONAL ACCESS
    # ─────────────────────────────────────────────────────────────────
    
    def dimension(self, level: int) -> DimensionalManifold:
        """
        View the substrate at a specific dimension.
        
        Args:
            level: The dimension level (0-6+)
                0 = Identity (pure 64-bit)
                1 = Attributes (scalars, constants)
                2 = Relations (surfaces, grids)
                3 = Structure (volume, geometry)
                4 = Behavior (motion, physics)
                5 = Systems (multi-substrate)
                6+ = Emergent (intelligence)
        
        Returns:
            DimensionalManifold at that dimension
        """
        return DimensionalManifold(
            substrate=self,
            dimension=level
        )
    
    # Convenience accessors
    @property
    def d0(self) -> DimensionalManifold:
        """0D - Identity dimension."""
        return self.dimension(0)
    
    @property
    def d1(self) -> DimensionalManifold:
        """1D - Attribute dimension."""
        return self.dimension(1)
    
    @property
    def d2(self) -> DimensionalManifold:
        """2D - Relational dimension."""
        return self.dimension(2)
    
    @property
    def d3(self) -> DimensionalManifold:
        """3D - Structural dimension."""
        return self.dimension(3)
    
    @property
    def d4(self) -> DimensionalManifold:
        """4D - Behavioral dimension."""
        return self.dimension(4)
    
    @property
    def d5(self) -> DimensionalManifold:
        """5D - System dimension."""
        return self.dimension(5)
    
    # ─────────────────────────────────────────────────────────────────
    # LENS ACCESS (Attributes & Functionality)
    # ─────────────────────────────────────────────────────────────────
    
    def lens(self, name: str, dimension: int = 1, **params) -> DimensionalLens:
        """
        Create a lens to access an attribute or functionality.
        
        Attributes are not stored - they are mathematical relationships
        revealed through lenses.
        
        Args:
            name: The attribute/function name
            dimension: The dimension to operate at (default: 1 = Attribute)
            **params: Additional parameters for the lens
        
        Returns:
            DimensionalLens that can be invoked
        
        Example:
            x = substrate.lens("x").invoke()
            age = substrate.lens("age", dimension=4).invoke()
        """
        return DimensionalLens(
            substrate=self,
            name=name,
            dimension=dimension,
            params=params
        )
    
    def __getitem__(self, key: str) -> int:
        """Shorthand for lens access: substrate["x"] == substrate.lens("x").invoke()"""
        return self.lens(key).invoke()
    
    # ─────────────────────────────────────────────────────────────────
    # DELTA APPLICATION (Behavior)
    # ─────────────────────────────────────────────────────────────────
    
    def apply(self, delta: Union[DimensionalDelta, int, float, dict]) -> 'DimensionalSubstrate':
        """
        Apply a delta (behavior) to produce a new substrate.
        
        This does NOT mutate the current substrate.
        It produces a NEW substrate with the delta applied.
        
        Args:
            delta: The behavior delta to apply
        
        Returns:
            New DimensionalSubstrate with delta applied
        
        Example:
            gravity = DimensionalDelta(9.8)
            falling_ball = ball.apply(gravity)
        """
        if not isinstance(delta, DimensionalDelta):
            delta = DimensionalDelta(delta)
        
        # Compute new truth by XOR with delta
        new_truth = (self._truth ^ delta.value) & MASK_64
        
        # Create new data if dict
        new_data = self._data
        if isinstance(self._data, dict) and isinstance(delta.data, dict):
            new_data = dict(self._data)
            for k, v in delta.data.items():
                if k.startswith('d') and k[1:] in new_data:
                    # Delta key like "dx" applies to "x"
                    base_key = k[1:]
                    if isinstance(new_data[base_key], (int, float)):
                        new_data[base_key] = new_data[base_key] + v
                elif k in new_data:
                    new_data[k] = v
        
        return DimensionalSubstrate(
            data=new_data if new_data != self._data else new_truth,
            fx=self._fx,
            parent=self,
            generation=self._generation + 1
        )
    
    # ─────────────────────────────────────────────────────────────────
    # PROMOTION (Dimensional Evolution)
    # ─────────────────────────────────────────────────────────────────
    
    def promote(self, delta: Union[DimensionalDelta, int, float, dict]) -> 'DimensionalSubstrate':
        """
        Promote the substrate to its next dimensional state.
        
        This is the fundamental operation for animation and evolution.
        
            m₁ = promote(x₁, y₁, z₁)
        
        Args:
            delta: The change encoding (z₁)
        
        Returns:
            New DimensionalSubstrate in the next state
        
        Example:
            frame_0 = substrate
            frame_1 = frame_0.promote(physics_delta)
            frame_2 = frame_1.promote(physics_delta)
        """
        return self.apply(delta)
    
    # ─────────────────────────────────────────────────────────────────
    # OPERATIONS
    # ─────────────────────────────────────────────────────────────────
    
    def xor(self, other: Union['DimensionalSubstrate', int]) -> 'DimensionalSubstrate':
        """XOR with another substrate or value."""
        other_val = other.truth if isinstance(other, DimensionalSubstrate) else other
        return DimensionalSubstrate(
            data=self._truth ^ other_val,
            fx=self._fx,
            generation=self._generation
        )
    
    def and_(self, other: Union['DimensionalSubstrate', int]) -> 'DimensionalSubstrate':
        """AND with another substrate or value."""
        other_val = other.truth if isinstance(other, DimensionalSubstrate) else other
        return DimensionalSubstrate(
            data=self._truth & other_val,
            fx=self._fx,
            generation=self._generation
        )
    
    def or_(self, other: Union['DimensionalSubstrate', int]) -> 'DimensionalSubstrate':
        """OR with another substrate or value."""
        other_val = other.truth if isinstance(other, DimensionalSubstrate) else other
        return DimensionalSubstrate(
            data=self._truth | other_val,
            fx=self._fx,
            generation=self._generation
        )
    
    def rotate(self, n: int) -> 'DimensionalSubstrate':
        """Rotate left by n bits."""
        n = n % 64
        rotated = ((self._truth << n) | (self._truth >> (64 - n))) & MASK_64
        return DimensionalSubstrate(
            data=rotated,
            fx=self._fx,
            generation=self._generation
        )
    
    # ─────────────────────────────────────────────────────────────────
    # ANIMATION HELPERS
    # ─────────────────────────────────────────────────────────────────
    
    def animate(
        self, 
        delta: Union[DimensionalDelta, int, float, dict],
        frames: int
    ) -> List['DimensionalSubstrate']:
        """
        Generate animation frames through promotion.
        
        Args:
            delta: The per-frame delta
            frames: Number of frames to generate
        
        Returns:
            List of DimensionalSubstrate frames
        
        Example:
            gravity = DimensionalDelta({"dy": 9.8, "dt": 0.016})
            animation = ball.animate(gravity, 100)
        """
        if not isinstance(delta, DimensionalDelta):
            delta = DimensionalDelta(delta)
        
        result = [self]
        current = self
        for _ in range(frames - 1):
            current = current.promote(delta)
            result.append(current)
        
        return result
    
    # ─────────────────────────────────────────────────────────────────
    # STRING REPRESENTATION
    # ─────────────────────────────────────────────────────────────────
    
    def __repr__(self) -> str:
        return f"Substrate(0x{self._truth:016X}, gen={self._generation})"
    
    def __str__(self) -> str:
        return f"Substrate(truth=0x{self._truth:016X})"
    
    # ─────────────────────────────────────────────────────────────────
    # IMMUTABILITY
    # ─────────────────────────────────────────────────────────────────
    
    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            raise TypeError("DimensionalSubstrate is immutable - use apply() or promote()")
    
    # ─────────────────────────────────────────────────────────────────
    # COMPARISON
    # ─────────────────────────────────────────────────────────────────
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, DimensionalSubstrate):
            return self._truth == other._truth
        elif isinstance(other, int):
            return self._truth == other
        return False
    
    def __hash__(self) -> int:
        return hash(self._truth)
