"""
Lens - Contextual slice for attribute access.

A lens does NOT modify a substrate.
It selects a dimensional slice, region, or interpretation.
ALL attribute access MUST occur through a lens.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .substrate import Substrate, SubstrateIdentity


class Lens:
    """
    A lens provides context for substrate observation.
    
    It does not store attributes - it defines the mathematical
    transformation for deriving attributes from substrate expressions.
    """
    __slots__ = ('_lens_id', '_projection')
    
    def __init__(
        self, 
        lens_id: int,
        projection: Callable[[int], int]
    ):
        """
        lens_id: 64-bit identity of this lens
        projection: Mathematical projection function (substrate → attribute)
        """
        if not (0 <= lens_id < 2**64):
            raise ValueError("Lens ID must fit in 64 bits")
        object.__setattr__(self, '_lens_id', lens_id)
        object.__setattr__(self, '_projection', projection)
    
    def __setattr__(self, name, value):
        raise TypeError("Lens is immutable")
    
    def __delattr__(self, name):
        raise TypeError("Lens is immutable")
    
    @property
    def lens_id(self) -> int:
        return self._lens_id
    
    @property
    def projection(self) -> Callable[[int], int]:
        return self._projection
    
    def __repr__(self) -> str:
        return f"Lens(0x{self._lens_id:016X})"
