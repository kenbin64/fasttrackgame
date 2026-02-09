"""
DimensionalList - Immutable List of Substrates

A list where:
- Each element is a substrate
- All operations return NEW lists (immutability)
- Indexing is observation
- Iteration is sequential observation
- Transformations follow the Seven Laws

CHARTER COMPLIANCE:
✅ Principle 1: All Things Are by Reference - Elements are substrate references
✅ Principle 2: Passive Until Invoked - No background processing
✅ Principle 3: No Self-Modifying Code - Immutable at runtime
✅ Principle 5: No Hacking Surface - Pure functions only
✅ Principle 7: Fibonacci-Bounded Growth - Predictable structure
"""

from __future__ import annotations
from typing import List, Callable, Optional, Iterator
from kernel import Substrate


class DimensionalList:
    """
    Immutable list of substrates.
    
    All operations return NEW lists, preserving immutability.
    """
    __slots__ = ('_elements',)
    
    def __init__(self, elements: Optional[List[Substrate]] = None):
        """
        Create a dimensional list.
        
        Args:
            elements: Optional list of substrates (default: empty list)
        """
        if elements is None:
            elements = []
        
        # Validate all elements are substrates
        for i, elem in enumerate(elements):
            if not isinstance(elem, Substrate):
                raise TypeError(f"Element {i} is not a Substrate: {type(elem)}")
        
        object.__setattr__(self, '_elements', tuple(elements))  # Store as tuple for immutability
    
    def __setattr__(self, name, value):
        raise TypeError("DimensionalList is immutable")
    
    def __delattr__(self, name):
        raise TypeError("DimensionalList is immutable")
    
    @property
    def length(self) -> int:
        """Number of elements in the list"""
        return len(self._elements)
    
    def __len__(self) -> int:
        """Number of elements in the list"""
        return len(self._elements)
    
    def __getitem__(self, index: int) -> Substrate:
        """
        Observation: Get element at index.
        
        Args:
            index: Index of element to retrieve
        
        Returns:
            Substrate at the given index
        """
        return self._elements[index]
    
    def __iter__(self) -> Iterator[Substrate]:
        """Iterate over elements"""
        return iter(self._elements)
    
    def append(self, substrate: Substrate) -> DimensionalList:
        """
        Return NEW list with substrate appended.
        
        Args:
            substrate: Substrate to append
        
        Returns:
            New DimensionalList with element appended
        """
        if not isinstance(substrate, Substrate):
            raise TypeError(f"Can only append Substrate, not {type(substrate)}")
        
        new_elements = list(self._elements) + [substrate]
        return DimensionalList(new_elements)
    
    def prepend(self, substrate: Substrate) -> DimensionalList:
        """
        Return NEW list with substrate prepended.
        
        Args:
            substrate: Substrate to prepend
        
        Returns:
            New DimensionalList with element prepended
        """
        if not isinstance(substrate, Substrate):
            raise TypeError(f"Can only prepend Substrate, not {type(substrate)}")
        
        new_elements = [substrate] + list(self._elements)
        return DimensionalList(new_elements)
    
    def map(self, transform: Callable[[Substrate], Substrate]) -> DimensionalList:
        """
        Transform each element and return NEW list.
        
        Args:
            transform: Function that takes a substrate and returns a substrate
        
        Returns:
            New DimensionalList with transformed elements
        """
        new_elements = [transform(elem) for elem in self._elements]
        return DimensionalList(new_elements)
    
    def filter(self, predicate: Callable[[Substrate], bool]) -> DimensionalList:
        """
        Filter elements and return NEW list.
        
        Args:
            predicate: Function that takes a substrate and returns bool
        
        Returns:
            New DimensionalList with filtered elements
        """
        new_elements = [elem for elem in self._elements if predicate(elem)]
        return DimensionalList(new_elements)
    
    def slice(self, start: int, end: Optional[int] = None) -> DimensionalList:
        """
        Return NEW list with slice of elements.
        
        Args:
            start: Start index (inclusive)
            end: End index (exclusive), None for end of list
        
        Returns:
            New DimensionalList with sliced elements
        """
        if end is None:
            new_elements = list(self._elements[start:])
        else:
            new_elements = list(self._elements[start:end])
        return DimensionalList(new_elements)
    
    def concat(self, other: DimensionalList) -> DimensionalList:
        """
        Concatenate with another list and return NEW list.
        
        Args:
            other: Another DimensionalList
        
        Returns:
            New DimensionalList with concatenated elements
        """
        if not isinstance(other, DimensionalList):
            raise TypeError(f"Can only concat with DimensionalList, not {type(other)}")
        
        new_elements = list(self._elements) + list(other._elements)
        return DimensionalList(new_elements)
    
    def __repr__(self) -> str:
        return f"DimensionalList({len(self._elements)} elements)"

