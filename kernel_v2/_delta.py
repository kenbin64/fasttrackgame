"""
Delta - The mechanism of change without mutation.

δ(z₁) encodes a transformation that, when applied through
dimensional promotion, creates a NEW identity.

No in-place updates. No patches. No state changes.
"""

__all__ = ['Delta']


class Delta:
    """
    Change encoding (z₁).
    
    A delta represents transformation that produces new identity
    through dimensional promotion:
    
        x₁ + y₁ + δ(z₁) → m₁
    
    The delta itself is immutable - it's a mathematical descriptor.
    """
    __slots__ = ('_z1',)
    
    def __init__(self, z1: int):
        """
        Create a delta.
        
        Args:
            z1: 64-bit delta identity encoding the change
        """
        object.__setattr__(self, '_z1', z1 & 0xFFFFFFFFFFFFFFFF)
    
    def __setattr__(self, name, value):
        raise TypeError("Delta is immutable")
    
    def __delattr__(self, name):
        raise TypeError("Delta is immutable")
    
    @property
    def z1(self) -> int:
        """The 64-bit delta identity."""
        return self._z1
    
    @property
    def value(self) -> int:
        """Alias for z1."""
        return self._z1
    
    # === Delta composition ===
    
    def compose(self, other: 'Delta') -> 'Delta':
        """
        Compose two deltas: δ₁ ∘ δ₂
        
        The result is a single delta representing both transformations.
        """
        # XOR composition preserves mathematical properties
        composed = self._z1 ^ other._z1
        return Delta(composed)
    
    def __xor__(self, other: 'Delta') -> 'Delta':
        """Delta XOR composition."""
        return self.compose(other)
    
    def __repr__(self) -> str:
        return f"δ(z₁=0x{self._z1:016X})"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Delta):
            return self._z1 == other._z1
        return False
    
    def __hash__(self) -> int:
        return self._z1
