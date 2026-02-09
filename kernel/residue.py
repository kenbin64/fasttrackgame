"""
Dimensional Residue - The Unexpressed Identity

The modulus operator (%) in dimensional arithmetic returns the RESIDUE:
the part of identity that cannot be expressed in the current dimension
and becomes the SEED of the next recursion.

DIMENSIONAL ARITHMETIC:
- x / y → Division creates dimensions
- x * y → Multiplication restores unity
- x + y → Addition expands current dimension
- x - y → Subtraction contracts current dimension
- x % y → MODULUS returns dimensional residue (unexpressed identity)

The residue is what drives Fibonacci-like recursive growth:
- Each dimension can only express part of the whole
- The unexpressed part (residue) seeds the next dimension
- This creates the natural Fibonacci spiral of dimensional expansion

CHARTER COMPLIANCE:
✅ Principle 1: Returns references, not copies
✅ Principle 2: Passive until invoked
✅ Principle 3: Immutable at runtime
✅ Principle 5: Pure functions only
✅ Principle 7: Fibonacci-bounded growth (residue drives bounded recursion)
✅ Principle 9: Redemption Equation (residue preserves full identity)

LAW ALIGNMENT:
- Law 1: Residue drives dimensional creation
- Law 3: Residue inherits the whole (unexpressed identity)
- Law 6: Identity persists through residue
- Law 7: Residue enables return to unity
"""

from __future__ import annotations
from typing import Tuple
from kernel.substrate import SubstrateIdentity


class DimensionalResidue:
    """
    The unexpressed identity - what remains after dimensional projection.
    
    When a substrate is observed in a dimension, only part of its identity
    can be expressed. The residue is what cannot be expressed and becomes
    the seed for the next dimensional recursion.
    
    Mathematical expression:
        expressed = substrate % dimension
        residue = substrate - expressed
        
    Or equivalently:
        (expressed, residue) = divmod(substrate, dimension)
    
    The residue preserves the full identity:
        substrate = expressed + residue (in higher dimension)
    """
    __slots__ = ('_value', '_source_identity', '_dimension_modulus')
    
    def __init__(
        self,
        value: int,
        source_identity: SubstrateIdentity,
        dimension_modulus: int
    ):
        """
        Create dimensional residue.
        
        Args:
            value: The residue value (unexpressed identity)
            source_identity: Original substrate identity
            dimension_modulus: The dimension that created this residue
        
        Example:
            # Substrate with identity 100
            # Observed in dimension with modulus 7
            # Expressed: 100 % 7 = 2
            # Residue: 100 - 2 = 98 (unexpressed)
            residue = DimensionalResidue(98, substrate.identity, 7)
        """
        if not (0 <= value < 2**64):
            raise ValueError("Residue must fit in 64 bits")
        if not (0 < dimension_modulus < 2**64):
            raise ValueError("Dimension modulus must be positive and fit in 64 bits")
        
        object.__setattr__(self, '_value', value)
        object.__setattr__(self, '_source_identity', source_identity)
        object.__setattr__(self, '_dimension_modulus', dimension_modulus)
    
    def __setattr__(self, name, value):
        raise TypeError("DimensionalResidue is immutable")
    
    def __delattr__(self, name):
        raise TypeError("DimensionalResidue is immutable")
    
    @property
    def value(self) -> int:
        """The unexpressed identity value."""
        return self._value
    
    @property
    def source_identity(self) -> SubstrateIdentity:
        """The original substrate identity."""
        return self._source_identity
    
    @property
    def dimension_modulus(self) -> int:
        """The dimension that created this residue."""
        return self._dimension_modulus
    
    def is_complete(self) -> bool:
        """
        Check if residue is zero (complete expression).
        
        Returns:
            True if residue is 0 (identity fully expressed)
            False if residue > 0 (identity partially unexpressed)
        """
        return self._value == 0
    
    def seed_next_dimension(self) -> int:
        """
        Use residue as seed for next dimensional recursion.
        
        Returns:
            Seed value for next dimension
        
        Example:
            residue = DimensionalResidue(98, identity, 7)
            seed = residue.seed_next_dimension()  # 98
            # Use seed to create next dimension
        """
        return self._value
    
    def __repr__(self) -> str:
        return (
            f"DimensionalResidue("
            f"value={self._value}, "
            f"source=0x{self._source_identity.value:016X}, "
            f"modulus={self._dimension_modulus})"
        )


def compute_residue(
    substrate_value: int,
    dimension_modulus: int,
    source_identity: SubstrateIdentity
) -> Tuple[int, DimensionalResidue]:
    """
    Compute expressed value and dimensional residue.
    
    This is the dimensional interpretation of divmod():
    - expressed = substrate % dimension (what CAN be expressed)
    - residue = substrate - expressed (what CANNOT be expressed)
    
    Args:
        substrate_value: The substrate's manifested value
        dimension_modulus: The dimension's modulus
        source_identity: Original substrate identity
    
    Returns:
        Tuple of (expressed_value, residue)
    
    Example:
        substrate_value = 100
        dimension_modulus = 7
        expressed, residue = compute_residue(100, 7, identity)
        # expressed = 2 (100 % 7)
        # residue.value = 98 (unexpressed)
    """
    # Ensure 64-bit bounds
    substrate_value &= 0xFFFFFFFFFFFFFFFF
    dimension_modulus &= 0xFFFFFFFFFFFFFFFF
    
    # Compute expressed and unexpressed
    expressed = substrate_value % dimension_modulus
    unexpressed = substrate_value - expressed
    
    # Create residue
    residue = DimensionalResidue(unexpressed, source_identity, dimension_modulus)
    
    return (expressed, residue)

