"""
Manifold - A dimensional expression of a substrate.

A manifold is the SHAPE of a substrate.
The substrate is whole; the manifold is form.
A single substrate can produce infinite manifolds.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .substrate import Substrate, SubstrateIdentity


class Manifold:
    """
    Dimensional expression of a substrate.
    
    A manifold does not contain data - it represents a shape
    through which substrate truth can be observed.
    """
    __slots__ = ('_substrate_id', '_dimension', '_form_expression')
    
    def __init__(
        self, 
        substrate_id: SubstrateIdentity, 
        dimension: int,
        form_expression: int
    ):
        """
        substrate_id: The identity of the source substrate
        dimension: The dimensional level of this manifold
        form_expression: 64-bit encoding of the manifold's form
        """
        object.__setattr__(self, '_substrate_id', substrate_id)
        object.__setattr__(self, '_dimension', dimension)
        object.__setattr__(self, '_form_expression', form_expression)
    
    def __setattr__(self, name, value):
        raise TypeError("Manifold is immutable")
    
    def __delattr__(self, name):
        raise TypeError("Manifold is immutable")
    
    @property
    def substrate_id(self) -> SubstrateIdentity:
        return self._substrate_id
    
    @property
    def dimension(self) -> int:
        return self._dimension
    
    @property
    def form(self) -> int:
        return self._form_expression
    
    def __repr__(self) -> str:
        return f"Manifold(dim={self._dimension}, form=0x{self._form_expression:016X})"
