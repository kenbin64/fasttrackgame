"""
Delta - The mechanism of change without mutation.

Change is represented as δ(z₁) applied to:
  - x₁ (identity)
  - y₁ (attributes)

This produces a NEW atomic identity m₁ through dimensional promotion.
No in-place updates, patches, or state changes.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .substrate import SubstrateIdentity


class Delta:
    """
    A delta represents change without mutation.
    
    δ(z₁) encodes a transformation that, when applied to x₁ and y₁,
    produces a new identity m₁ in the next dimension.
    """
    __slots__ = ('_z1',)
    
    def __init__(self, z1: int):
        """
        z1: The 64-bit delta identity encoding the change
        """
        if not (0 <= z1 < 2**64):
            raise ValueError("Delta must fit in 64 bits")
        object.__setattr__(self, '_z1', z1)
    
    def __setattr__(self, name, value):
        raise TypeError("Delta is immutable")
    
    def __delattr__(self, name):
        raise TypeError("Delta is immutable")
    
    @property
    def z1(self) -> int:
        """The delta identity"""
        return self._z1
    
    def __repr__(self) -> str:
        return f"Delta(z₁=0x{self._z1:016X})"
