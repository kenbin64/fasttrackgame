"""
Iterator Pattern - Dimensional Navigation as Iteration

The Iterator Pattern in ButterflyFx uses dimensional navigation:
- Iterate through dimensions (0-8)
- Iterate through substrate divisions
- Iterate through dimensional structures

CHARTER COMPLIANCE:
✅ Principle 1: Returns references, not copies
✅ Principle 2: Passive until invoked
✅ Principle 3: Immutable at runtime
✅ Principle 5: Pure functions only
✅ Principle 7: Fibonacci-bounded growth (max 9 dimensions)

LAW ALIGNMENT:
- Law 2: Observation is division
- Law 3: Every division inherits the whole
"""

from __future__ import annotations
from typing import Iterator, Optional
from kernel import Substrate, Dimension


class DimensionalIterator:
    """
    Iterator for traversing substrate dimensions.
    
    Provides iteration over the 9 Fibonacci dimensions (0-8).
    """
    __slots__ = ('_substrate', '_current_index', '_dimensions')
    
    def __init__(self, substrate: Substrate):
        """
        Create dimensional iterator.
        
        Args:
            substrate: Substrate to iterate over
        """
        object.__setattr__(self, '_substrate', substrate)
        object.__setattr__(self, '_current_index', 0)
        object.__setattr__(self, '_dimensions', None)
    
    def __setattr__(self, name, value):
        raise TypeError("DimensionalIterator is immutable")
    
    def __delattr__(self, name):
        raise TypeError("DimensionalIterator is immutable")
    
    def __iter__(self) -> 'DimensionalIterator':
        """Return self as iterator"""
        return self
    
    def __next__(self) -> Dimension:
        """
        Get next dimension.
        
        Returns:
            Next Dimension
        
        Raises:
            StopIteration: When all dimensions exhausted
        """
        # Lazy division - only divide when iteration starts
        if self._dimensions is None:
            object.__setattr__(self, '_dimensions', self._substrate.divide())
        
        if self._current_index >= len(self._dimensions):
            raise StopIteration
        
        dimension = self._dimensions[self._current_index]
        object.__setattr__(self, '_current_index', self._current_index + 1)
        
        return dimension


class SubstrateSequenceIterator:
    """
    Iterator for sequences of substrates.
    
    Provides iteration over substrate collections.
    """
    __slots__ = ('_substrates', '_current_index')
    
    def __init__(self, substrates: list[Substrate]):
        """
        Create substrate sequence iterator.
        
        Args:
            substrates: List of substrates to iterate
        """
        object.__setattr__(self, '_substrates', tuple(substrates))
        object.__setattr__(self, '_current_index', 0)
    
    def __setattr__(self, name, value):
        raise TypeError("SubstrateSequenceIterator is immutable")
    
    def __delattr__(self, name):
        raise TypeError("SubstrateSequenceIterator is immutable")
    
    def __iter__(self) -> 'SubstrateSequenceIterator':
        """Return self as iterator"""
        return self
    
    def __next__(self) -> Substrate:
        """
        Get next substrate.
        
        Returns:
            Next Substrate
        
        Raises:
            StopIteration: When all substrates exhausted
        """
        if self._current_index >= len(self._substrates):
            raise StopIteration
        
        substrate = self._substrates[self._current_index]
        object.__setattr__(self, '_current_index', self._current_index + 1)
        
        return substrate


def iterate_dimensions(substrate: Substrate) -> Iterator[Dimension]:
    """
    Iterate over substrate dimensions.
    
    Args:
        substrate: Substrate to iterate
    
    Yields:
        Each dimension (0-8)
    
    Example:
        substrate = Substrate(identity, expression)
        for dimension in iterate_dimensions(substrate):
            print(f"Dimension {dimension.level}")
    """
    return DimensionalIterator(substrate)


def iterate_substrates(substrates: list[Substrate]) -> Iterator[Substrate]:
    """
    Iterate over substrate sequence.
    
    Args:
        substrates: List of substrates
    
    Yields:
        Each substrate in sequence
    
    Example:
        substrates = [s1, s2, s3]
        for substrate in iterate_substrates(substrates):
            result = substrate.invoke()
    """
    return SubstrateSequenceIterator(substrates)

