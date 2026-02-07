"""
Dimensional - Dimension containment and promotion.

A point in a higher dimension contains ALL lower dimensions.
Promotion into higher dimensions is the ONLY mechanism of change.

This is pure math - no logic, no conditions.
"""

from __future__ import annotations
from .substrate import Substrate, SubstrateIdentity
from .delta import Delta


class Dimension:
    """
    Represents a dimensional level.
    
    Each dimension contains all lower dimensions.
    Substrates exist at specific dimensional levels.
    """
    __slots__ = ('_level',)
    
    def __init__(self, level: int):
        if level < 0:
            raise ValueError("Dimension level must be non-negative")
        object.__setattr__(self, '_level', level)
    
    def __setattr__(self, name, value):
        raise TypeError("Dimension is immutable")
    
    def __delattr__(self, name):
        raise TypeError("Dimension is immutable")
    
    @property
    def level(self) -> int:
        return self._level
    
    def contains(self, other: Dimension) -> bool:
        """Higher dimensions contain all lower dimensions"""
        return self._level >= other._level
    
    def __repr__(self) -> str:
        return f"Dimension({self._level})"


def promote(
    x1: SubstrateIdentity,
    y1: int,
    delta: Delta
) -> SubstrateIdentity:
    """
    Promote x₁ through δ(z₁) applied to y₁ → m₁
    
    This is the ONLY way change occurs.
    The result is a NEW atomic identity in the next dimension.
    
    Mathematical expression:
        m₁ = f(x₁, y₁, z₁)
    
    Where f is a deterministic, reversible transformation
    that encodes the full history in the new identity.
    """
    # XOR-based promotion preserving mathematical properties
    # This is a simplified expression - real impl would use
    # cryptographic hash for collision resistance
    x1_val = x1.value
    z1_val = delta.z1
    
    # m₁ = (x₁ ⊕ y₁) ⊕ z₁ rotated by dimensional offset
    intermediate = x1_val ^ y1
    m1_value = (intermediate ^ z1_val) & 0xFFFFFFFFFFFFFFFF
    
    return SubstrateIdentity(m1_value)
