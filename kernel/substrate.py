"""
Substrate - A mathematical expression encoded in 64 bits.

A substrate IS a mathematical structure like:
- z = xy
- z = xy²
- z = x + y
- z = d/dt[position]

The 64-bit identity is a HASH of the expression, not the data.
Invocation reveals truth - nothing is stored.

Examples:
    # Linear expression
    expr = lambda x, y: x + y
    identity = hash("z = x + y") & 0xFFFFFFFFFFFFFFFF
    substrate = Substrate(SubstrateIdentity(identity), expr)

    # Quadratic expression
    expr = lambda x, y: x * (y ** 2)
    identity = hash("z = xy²") & 0xFFFFFFFFFFFFFFFF
    substrate = Substrate(SubstrateIdentity(identity), expr)

No attribute is stored. All truth emerges from invocation.
"""

from __future__ import annotations
from typing import Callable


class SubstrateIdentity:
    """
    64-bit mathematical identity.
    
    Encodes the mathematical universe, NOT data.
    Two identical expressions = same identity (non-duplication law).
    """
    __slots__ = ('_identity',)
    
    def __init__(self, identity: int):
        if not (0 <= identity < 2**64):
            raise ValueError("Identity must fit in 64 bits")
        object.__setattr__(self, '_identity', identity)
    
    def __setattr__(self, name, value):
        raise TypeError("SubstrateIdentity is immutable")
    
    def __delattr__(self, name):
        raise TypeError("SubstrateIdentity is immutable")
    
    @property
    def value(self) -> int:
        return self._identity
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, SubstrateIdentity):
            return self._identity == other._identity
        return False
    
    def __hash__(self) -> int:
        return self._identity
    
    def __repr__(self) -> str:
        return f"SubstrateIdentity(0x{self._identity:016X})"


class Substrate:
    """
    The complete mathematical identity.

    A substrate IS a mathematical expression (z = xy, z = xy², etc.)

    When created, EVERY CONCEIVABLE ATTRIBUTE EXISTS.
    Only identity (x0) and name (x0 in 1D) are explicit.
    Everything else exists because the object exists.

    Attributes manifest ONLY when invoked - nothing is stored.

    The 64-bit identity is BITWISE (2^64 = 18 quintillion combinations).
    The expression can compute ANY attribute - infinite detail from finite encoding.
    """
    __slots__ = ('_x1', '_expression')

    def __init__(self, x1: SubstrateIdentity, expression: Callable):
        """
        x1: The atomic identity (64-bit bitwise)
        expression: The mathematical expression that IS this substrate
                   Must accept **kwargs to compute any attribute

        Example:
            def car_expression(**kwargs):
                attr = kwargs.get('attribute', 'identity')
                if attr == 'vin': return compute_vin()
                if attr == 'year': return compute_year()
                if attr == 'tire_atoms': return compute_atomic_composition()
                # ... infinite attributes possible
                return derive_attribute(attr)
        """
        object.__setattr__(self, '_x1', x1)
        object.__setattr__(self, '_expression', expression)
    
    def __setattr__(self, name, value):
        raise TypeError("Substrate is immutable")
    
    def __delattr__(self, name):
        raise TypeError("Substrate is immutable")
    
    @property
    def identity(self) -> SubstrateIdentity:
        """The atomic 64-bit identity (x₁)"""
        return self._x1
    
    @property
    def expression(self) -> Callable:
        """The mathematical expression defining this substrate"""
        return self._expression

    def invoke(self, **kwargs) -> int:
        """
        Invoke the substrate's expression to manifest an attribute.

        This is how attributes come into existence - through invocation.
        Nothing is stored; everything is computed.

        Args:
            **kwargs: Parameters for the expression (e.g., attribute='vin')

        Returns:
            64-bit result of the mathematical expression

        Example:
            substrate.invoke(attribute='vin')  # Manifests VIN
            substrate.invoke(attribute='year')  # Manifests year
            substrate.invoke(attribute='tire_atoms')  # Manifests atomic composition
        """
        result = self._expression(**kwargs)
        # Ensure result fits in 64 bits (bitwise)
        return result & 0xFFFFFFFFFFFFFFFF

    def __eq__(self, other: object) -> bool:
        # Non-duplication: identical expressions = same identity
        if isinstance(other, Substrate):
            return self._x1 == other._x1
        return False

    def __hash__(self) -> int:
        return hash(self._x1)

    def __repr__(self) -> str:
        return f"Substrate({self._x1})"
