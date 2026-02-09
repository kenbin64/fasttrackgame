"""
DimensionalSet - Immutable Set of Substrates

A set where:
- Membership is determined by substrate identity (64-bit integer)
- All operations return NEW sets (immutability)
- Set operations (union, intersection, difference) follow mathematical laws
- No duplicates (identity uniqueness)

CHARTER COMPLIANCE:
✅ Principle 1: All Things Are by Reference - Elements are substrate references
✅ Principle 2: Passive Until Invoked - No background processing
✅ Principle 3: No Self-Modifying Code - Immutable at runtime
✅ Principle 5: No Hacking Surface - Pure functions only
✅ Principle 6: No Dark Web, No Concealment Dimensions - All relationships visible
"""

from __future__ import annotations
from typing import Dict, Callable, Optional, Iterator
from kernel import Substrate


class DimensionalSet:
    """
    Immutable set of substrates.
    
    Membership is determined by substrate identity.
    All operations return NEW sets, preserving immutability.
    """
    __slots__ = ('_elements',)
    
    def __init__(self, elements: Optional[list[Substrate]] = None):
        """
        Create a dimensional set.
        
        Args:
            elements: Optional list of substrates (duplicates removed by identity)
        """
        if elements is None:
            elements = []
        
        # Store as dict mapping identity -> substrate (ensures uniqueness)
        element_dict = {}
        for elem in elements:
            if not isinstance(elem, Substrate):
                raise TypeError(f"Element must be Substrate, not {type(elem)}")
            element_dict[elem.identity.value] = elem
        
        object.__setattr__(self, '_elements', element_dict)
    
    def __setattr__(self, name, value):
        raise TypeError("DimensionalSet is immutable")
    
    def __delattr__(self, name):
        raise TypeError("DimensionalSet is immutable")
    
    @property
    def size(self) -> int:
        """Number of elements in the set"""
        return len(self._elements)
    
    def __len__(self) -> int:
        """Number of elements in the set"""
        return len(self._elements)
    
    def contains(self, substrate: Substrate) -> bool:
        """
        Check if substrate is in the set.
        
        Args:
            substrate: Substrate to check
        
        Returns:
            True if substrate identity is in set, False otherwise
        """
        return substrate.identity.value in self._elements
    
    def __contains__(self, substrate: Substrate) -> bool:
        """Check if substrate is in the set"""
        return substrate.identity.value in self._elements
    
    def __iter__(self) -> Iterator[Substrate]:
        """Iterate over elements"""
        return iter(self._elements.values())
    
    def add(self, substrate: Substrate) -> DimensionalSet:
        """
        Return NEW set with substrate added.
        
        Args:
            substrate: Substrate to add
        
        Returns:
            New DimensionalSet with element added
        """
        if not isinstance(substrate, Substrate):
            raise TypeError(f"Can only add Substrate, not {type(substrate)}")
        
        new_elements = dict(self._elements)
        new_elements[substrate.identity.value] = substrate
        return DimensionalSet._from_dict(new_elements)
    
    def remove(self, substrate: Substrate) -> DimensionalSet:
        """
        Return NEW set with substrate removed.
        
        Args:
            substrate: Substrate to remove
        
        Returns:
            New DimensionalSet with element removed
        
        Raises:
            KeyError: If substrate not in set
        """
        if substrate.identity.value not in self._elements:
            raise KeyError(f"Substrate with identity {substrate.identity.value} not in set")
        
        new_elements = dict(self._elements)
        del new_elements[substrate.identity.value]
        return DimensionalSet._from_dict(new_elements)
    
    def union(self, other: DimensionalSet) -> DimensionalSet:
        """
        Return NEW set with union of this set and other.
        
        Args:
            other: Another DimensionalSet
        
        Returns:
            New DimensionalSet with union of elements
        """
        if not isinstance(other, DimensionalSet):
            raise TypeError(f"Can only union with DimensionalSet, not {type(other)}")
        
        new_elements = dict(self._elements)
        new_elements.update(other._elements)
        return DimensionalSet._from_dict(new_elements)
    
    def intersection(self, other: DimensionalSet) -> DimensionalSet:
        """
        Return NEW set with intersection of this set and other.
        
        Args:
            other: Another DimensionalSet
        
        Returns:
            New DimensionalSet with intersection of elements
        """
        if not isinstance(other, DimensionalSet):
            raise TypeError(f"Can only intersect with DimensionalSet, not {type(other)}")
        
        new_elements = {
            identity: substrate
            for identity, substrate in self._elements.items()
            if identity in other._elements
        }
        return DimensionalSet._from_dict(new_elements)
    
    def difference(self, other: DimensionalSet) -> DimensionalSet:
        """
        Return NEW set with elements in this set but not in other.
        
        Args:
            other: Another DimensionalSet
        
        Returns:
            New DimensionalSet with difference of elements
        """
        if not isinstance(other, DimensionalSet):
            raise TypeError(f"Can only diff with DimensionalSet, not {type(other)}")
        
        new_elements = {
            identity: substrate
            for identity, substrate in self._elements.items()
            if identity not in other._elements
        }
        return DimensionalSet._from_dict(new_elements)
    
    @classmethod
    def _from_dict(cls, element_dict: Dict[int, Substrate]) -> DimensionalSet:
        """Internal: Create set from pre-built dict"""
        instance = object.__new__(cls)
        object.__setattr__(instance, '_elements', element_dict)
        return instance
    
    def __repr__(self) -> str:
        return f"DimensionalSet({len(self._elements)} elements)"

