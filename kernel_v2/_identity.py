"""
SubstrateIdentity - 64-bit atomic identity.

Pure mathematical encoding. No logic.
"""

__all__ = ['SubstrateIdentity']


class SubstrateIdentity:
    """
    64-bit atomic identity (x₁).
    
    Mathematical properties:
    - Immutable
    - Hashable  
    - Comparable
    - Fits in 64 bits exactly
    
    Two identical mathematical expressions produce the same identity.
    (Non-duplication law)
    """
    __slots__ = ('_x1',)
    
    def __init__(self, x1: int):
        """Create identity from 64-bit integer."""
        # Enforce 64-bit bounds
        object.__setattr__(self, '_x1', x1 & 0xFFFFFFFFFFFFFFFF)
    
    def __setattr__(self, name, value):
        raise TypeError("SubstrateIdentity is immutable")
    
    def __delattr__(self, name):
        raise TypeError("SubstrateIdentity is immutable")
    
    @property
    def value(self) -> int:
        """The 64-bit identity value."""
        return self._x1
    
    @property
    def x1(self) -> int:
        """Alias for value (mathematical notation)."""
        return self._x1
    
    # === Mathematical Operations ===
    
    def __xor__(self, other: 'SubstrateIdentity') -> 'SubstrateIdentity':
        """XOR combination of identities."""
        return SubstrateIdentity(self._x1 ^ other._x1)
    
    def __and__(self, other: 'SubstrateIdentity') -> 'SubstrateIdentity':
        """AND combination of identities."""
        return SubstrateIdentity(self._x1 & other._x1)
    
    def __or__(self, other: 'SubstrateIdentity') -> 'SubstrateIdentity':
        """OR combination of identities."""
        return SubstrateIdentity(self._x1 | other._x1)
    
    def __invert__(self) -> 'SubstrateIdentity':
        """Bitwise NOT."""
        return SubstrateIdentity(~self._x1 & 0xFFFFFFFFFFFFFFFF)
    
    def rotate_left(self, n: int) -> 'SubstrateIdentity':
        """Rotate bits left by n positions."""
        n = n % 64
        rotated = ((self._x1 << n) | (self._x1 >> (64 - n))) & 0xFFFFFFFFFFFFFFFF
        return SubstrateIdentity(rotated)
    
    def rotate_right(self, n: int) -> 'SubstrateIdentity':
        """Rotate bits right by n positions."""
        n = n % 64
        rotated = ((self._x1 >> n) | (self._x1 << (64 - n))) & 0xFFFFFFFFFFFFFFFF
        return SubstrateIdentity(rotated)
    
    # === Comparison ===
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, SubstrateIdentity):
            return self._x1 == other._x1
        return False
    
    def __hash__(self) -> int:
        return self._x1
    
    def __lt__(self, other: 'SubstrateIdentity') -> bool:
        return self._x1 < other._x1
    
    # === Representation ===
    
    def __repr__(self) -> str:
        return f"x₁(0x{self._x1:016X})"
    
    def __int__(self) -> int:
        return self._x1
    
    def __bytes__(self) -> bytes:
        return self._x1.to_bytes(8, 'big')
