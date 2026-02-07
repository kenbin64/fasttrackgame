"""
Manifold - Shape of substrate at dimensional intersection.

A manifold is not the substrate itself - it is how the substrate
appears when viewed through a specific dimensional lens.
"""

from ._identity import SubstrateIdentity
from ._dimension import Dimension

__all__ = ['Manifold']


class Manifold:
    """
    Shape of substrate at a dimensional level.
    
    Components:
    - substrate_id: Identity of the source substrate
    - dimension: The dimensional level
    - form: The 64-bit form expression
    
    Manifolds are discovered, not created arbitrarily.
    """
    __slots__ = ('_substrate_id', '_dimension', '_form')
    
    def __init__(
        self, 
        substrate_id: SubstrateIdentity,
        dimension: Dimension,
        form: int
    ):
        """
        Create a manifold.
        
        Args:
            substrate_id: Source substrate identity
            dimension: Dimensional level
            form: 64-bit form expression
        """
        object.__setattr__(self, '_substrate_id', substrate_id)
        object.__setattr__(self, '_dimension', dimension)
        object.__setattr__(self, '_form', form & 0xFFFFFFFFFFFFFFFF)
    
    def __setattr__(self, name, value):
        raise TypeError("Manifold is immutable")
    
    def __delattr__(self, name):
        raise TypeError("Manifold is immutable")
    
    @property
    def substrate_id(self) -> SubstrateIdentity:
        """The source substrate identity."""
        return self._substrate_id
    
    @property
    def dimension(self) -> Dimension:
        """The dimensional level."""
        return self._dimension
    
    @property
    def form(self) -> int:
        """The 64-bit form expression."""
        return self._form
    
    def at_dimension(self, dim: Dimension) -> 'Manifold':
        """
        Project manifold to different dimension.
        
        Returns new manifold at specified dimension.
        """
        # Form changes based on dimensional projection
        dim_offset = dim.level - self._dimension.level
        new_form = (self._form >> abs(dim_offset)) if dim_offset < 0 else (self._form << dim_offset)
        return Manifold(self._substrate_id, dim, new_form & 0xFFFFFFFFFFFFFFFF)
    
    def __repr__(self) -> str:
        return f"Manifold({self._substrate_id}, {self._dimension}, form=0x{self._form:016X})"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Manifold):
            return (
                self._substrate_id == other._substrate_id and
                self._dimension == other._dimension and
                self._form == other._form
            )
        return False
    
    def __hash__(self) -> int:
        return hash((self._substrate_id, self._dimension.level, self._form))
