"""
Lens - Mathematical projection for attribute derivation.

A lens does NOT store attributes. It defines the transformation
from substrate expression to derived attribute.
"""

from typing import Callable

__all__ = ['Lens']


class Lens:
    """
    Projection function for deriving attributes.
    
    Every attribute access MUST go through a lens.
    The lens defines how the substrate value maps to an attribute.
    
    Lens = (lens_id, projection: int → int)
    """
    __slots__ = ('_lens_id', '_projection')
    
    def __init__(self, lens_id: int, projection: Callable[[int], int]):
        """
        Create a lens.
        
        Args:
            lens_id: 64-bit identity of this lens
            projection: Function (substrate_value → attribute_value)
        """
        object.__setattr__(self, '_lens_id', lens_id & 0xFFFFFFFFFFFFFFFF)
        object.__setattr__(self, '_projection', projection)
    
    def __setattr__(self, name, value):
        raise TypeError("Lens is immutable")
    
    def __delattr__(self, name):
        raise TypeError("Lens is immutable")
    
    @property
    def lens_id(self) -> int:
        """The 64-bit lens identity."""
        return self._lens_id
    
    @property
    def projection(self) -> Callable[[int], int]:
        """The projection function."""
        return self._projection
    
    def project(self, substrate_value: int) -> int:
        """
        Apply projection to substrate value.
        
        Returns the derived attribute (y₁).
        """
        result = self._projection(substrate_value)
        return result & 0xFFFFFFFFFFFFFFFF
    
    def __repr__(self) -> str:
        return f"Lens(0x{self._lens_id:016X})"
