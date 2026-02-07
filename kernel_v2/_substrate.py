"""
Substrate - Complete mathematical identity with expression.

A substrate IS the complete entity. Not a container of data.
Attributes are derived through lens invocation, never stored.
"""

from typing import Callable
from ._identity import SubstrateIdentity

__all__ = ['Substrate']


class Substrate:
    """
    The complete mathematical identity.
    
    A substrate consists of:
    - x₁: The 64-bit atomic identity  
    - expression: A function that computes the substrate's value
    
    Attributes are NOT stored. They are derived through lens invocation.
    """
    __slots__ = ('_identity', '_expression')
    
    def __init__(self, identity: SubstrateIdentity, expression: Callable[[], int]):
        """
        Create a substrate.
        
        Args:
            identity: The 64-bit identity (x₁)
            expression: Mathematical expression defining this substrate
        """
        object.__setattr__(self, '_identity', identity)
        object.__setattr__(self, '_expression', expression)
    
    def __setattr__(self, name, value):
        raise TypeError("Substrate is immutable")
    
    def __delattr__(self, name):
        raise TypeError("Substrate is immutable")
    
    @property
    def identity(self) -> SubstrateIdentity:
        """The atomic identity x₁."""
        return self._identity
    
    @property 
    def x1(self) -> SubstrateIdentity:
        """Alias for identity (mathematical notation)."""
        return self._identity
    
    @property
    def expression(self) -> Callable[[], int]:
        """The mathematical expression."""
        return self._expression
    
    def evaluate(self) -> int:
        """
        Evaluate the substrate's expression.
        
        Returns the 64-bit result of the mathematical expression.
        """
        result = self._expression()
        return result & 0xFFFFFFFFFFFFFFFF
    
    # === Equality based on identity ===
    
    def __eq__(self, other: object) -> bool:
        """Two substrates are equal iff their identities are equal."""
        if isinstance(other, Substrate):
            return self._identity == other._identity
        return False
    
    def __hash__(self) -> int:
        return hash(self._identity)
    
    def __repr__(self) -> str:
        return f"Substrate({self._identity})"
