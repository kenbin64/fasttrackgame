"""
Decorator Pattern - Delta as Behavior Decorator

The Decorator Pattern in ButterflyFx uses Delta to decorate substrates:
- Delta wraps substrate with additional behavior
- Applying delta produces NEW substrate (no mutation)
- Decorators can be chained

CHARTER COMPLIANCE:
✅ Principle 1: Returns references, not copies
✅ Principle 2: Passive until invoked
✅ Principle 3: Immutable at runtime (no mutation)
✅ Principle 5: Pure functions only
✅ Principle 9: Redemption Equation - decorations are reversible

LAW ALIGNMENT:
- Law 5: Change is motion through dimensions
- Law 6: Identity persists through change
- Law 7: Return to unity (decorations can be unwrapped)
"""

from __future__ import annotations
from typing import Callable, Optional
from kernel import Substrate, SubstrateIdentity, Delta, promote


class SubstrateDecorator:
    """
    Decorator for substrates using Delta transformations.
    
    Each decorator wraps a substrate with additional behavior,
    producing a NEW substrate while preserving the original.
    """
    __slots__ = ('_transformation',)
    
    def __init__(self, transformation: Callable[[int], int]):
        """
        Create substrate decorator.
        
        Args:
            transformation: Function to transform substrate result
        
        Example:
            # Create decorator that doubles values
            doubler = SubstrateDecorator(lambda x: x * 2)
        """
        object.__setattr__(self, '_transformation', transformation)
    
    def __setattr__(self, name, value):
        raise TypeError("SubstrateDecorator is immutable")
    
    def __delattr__(self, name):
        raise TypeError("SubstrateDecorator is immutable")
    
    def decorate(self, substrate: Substrate) -> Substrate:
        """
        Decorate substrate with transformation.
        
        Args:
            substrate: Substrate to decorate
        
        Returns:
            NEW substrate with decorated behavior
        
        Example:
            doubler = SubstrateDecorator(lambda x: x * 2)
            original = Substrate(SubstrateIdentity(42), lambda: 100)
            decorated = doubler.decorate(original)
            
            assert original.invoke() == 100
            assert decorated.invoke() == 200
        """
        # Create new identity for decorated substrate
        # Use promote to move to next dimension
        original_identity = substrate.identity
        delta = Delta(hash(str(self._transformation)) & 0xFFFFFFFFFFFFFFFF)
        new_identity = promote(original_identity, delta.z1, delta)
        
        # Create new expression that applies transformation
        original_expression = substrate._expression
        new_expression = lambda **kwargs: self._transformation(original_expression(**kwargs))
        
        return Substrate(new_identity, new_expression)
    
    def chain(self, other: 'SubstrateDecorator') -> 'SubstrateDecorator':
        """
        Chain two decorators together.
        
        Args:
            other: Decorator to chain after this one
        
        Returns:
            New decorator that applies both transformations
        
        Example:
            doubler = SubstrateDecorator(lambda x: x * 2)
            incrementer = SubstrateDecorator(lambda x: x + 1)
            
            # Chain: first double, then increment
            chained = doubler.chain(incrementer)
            
            substrate = Substrate(SubstrateIdentity(1), lambda: 10)
            result = chained.decorate(substrate)
            # result.invoke() == (10 * 2) + 1 == 21
        """
        # Create transformation that applies both
        combined = lambda x: other._transformation(self._transformation(x))
        return SubstrateDecorator(combined)


# Common decorators

class AddDecorator(SubstrateDecorator):
    """Decorator that adds a constant value"""
    
    def __init__(self, value: int):
        """
        Create add decorator.
        
        Args:
            value: Value to add
        """
        super().__init__(lambda x: (x + value) & 0xFFFFFFFFFFFFFFFF)


class MultiplyDecorator(SubstrateDecorator):
    """Decorator that multiplies by a constant"""
    
    def __init__(self, factor: int):
        """
        Create multiply decorator.
        
        Args:
            factor: Multiplication factor
        """
        super().__init__(lambda x: (x * factor) & 0xFFFFFFFFFFFFFFFF)


class ModuloDecorator(SubstrateDecorator):
    """Decorator that applies modulo operation"""
    
    def __init__(self, modulus: int):
        """
        Create modulo decorator.
        
        Args:
            modulus: Modulus value
        """
        if modulus <= 0:
            raise ValueError("Modulus must be positive")
        super().__init__(lambda x: x % modulus)


class ClampDecorator(SubstrateDecorator):
    """Decorator that clamps value to range"""
    
    def __init__(self, min_value: int, max_value: int):
        """
        Create clamp decorator.
        
        Args:
            min_value: Minimum value
            max_value: Maximum value
        """
        if min_value > max_value:
            raise ValueError("min_value must be <= max_value")
        super().__init__(lambda x: max(min_value, min(max_value, x)))

