"""
DimensionalDict - Immutable Dictionary of Substrates

A dictionary where:
- Keys are substrate identities (64-bit integers)
- Values are substrates
- Lookups are observations
- All operations return NEW dictionaries (immutability)
- Relationships are visible (Charter Principle 6)

CHARTER COMPLIANCE:
✅ Principle 1: All Things Are by Reference - Values are substrate references
✅ Principle 2: Passive Until Invoked - No background processing
✅ Principle 3: No Self-Modifying Code - Immutable at runtime
✅ Principle 5: No Hacking Surface - Pure functions only
✅ Principle 6: No Dark Web, No Concealment Dimensions - All relationships visible
"""

from __future__ import annotations
from typing import Dict, Callable, Optional, Iterator, Tuple
from kernel import Substrate


class DimensionalDict:
    """
    Immutable dictionary mapping substrate identities to substrates.
    
    All operations return NEW dictionaries, preserving immutability.
    """
    __slots__ = ('_mapping',)
    
    def __init__(self, mapping: Optional[Dict[int, Substrate]] = None):
        """
        Create a dimensional dictionary.
        
        Args:
            mapping: Optional dict mapping identities (int) to substrates
        """
        if mapping is None:
            mapping = {}
        
        # Validate all keys are integers and values are substrates
        for key, value in mapping.items():
            if not isinstance(key, int):
                raise TypeError(f"Key must be int (substrate identity), not {type(key)}")
            if not isinstance(value, Substrate):
                raise TypeError(f"Value must be Substrate, not {type(value)}")
        
        # Store as immutable dict (frozen)
        object.__setattr__(self, '_mapping', dict(mapping))
    
    def __setattr__(self, name, value):
        raise TypeError("DimensionalDict is immutable")
    
    def __delattr__(self, name):
        raise TypeError("DimensionalDict is immutable")
    
    @property
    def size(self) -> int:
        """Number of key-value pairs"""
        return len(self._mapping)
    
    def __len__(self) -> int:
        """Number of key-value pairs"""
        return len(self._mapping)
    
    def __getitem__(self, key: int) -> Substrate:
        """
        Observation: Get value for key.
        
        Args:
            key: Substrate identity (int)
        
        Returns:
            Substrate associated with the key
        
        Raises:
            KeyError: If key not found
        """
        return self._mapping[key]
    
    def get(self, key: int, default: Optional[Substrate] = None) -> Optional[Substrate]:
        """
        Get value for key, or default if not found.
        
        Args:
            key: Substrate identity (int)
            default: Default value if key not found
        
        Returns:
            Substrate associated with the key, or default
        """
        return self._mapping.get(key, default)
    
    def contains(self, key: int) -> bool:
        """
        Check if key exists.
        
        Args:
            key: Substrate identity (int)
        
        Returns:
            True if key exists, False otherwise
        """
        return key in self._mapping
    
    def __contains__(self, key: int) -> bool:
        """Check if key exists"""
        return key in self._mapping
    
    def keys(self) -> Iterator[int]:
        """Iterate over keys"""
        return iter(self._mapping.keys())
    
    def values(self) -> Iterator[Substrate]:
        """Iterate over values"""
        return iter(self._mapping.values())
    
    def items(self) -> Iterator[Tuple[int, Substrate]]:
        """Iterate over key-value pairs"""
        return iter(self._mapping.items())
    
    def set(self, key: int, value: Substrate) -> DimensionalDict:
        """
        Return NEW dictionary with key-value pair added/updated.
        
        Args:
            key: Substrate identity (int)
            value: Substrate to associate with key
        
        Returns:
            New DimensionalDict with updated mapping
        """
        if not isinstance(key, int):
            raise TypeError(f"Key must be int (substrate identity), not {type(key)}")
        if not isinstance(value, Substrate):
            raise TypeError(f"Value must be Substrate, not {type(value)}")
        
        new_mapping = dict(self._mapping)
        new_mapping[key] = value
        return DimensionalDict(new_mapping)
    
    def remove(self, key: int) -> DimensionalDict:
        """
        Return NEW dictionary with key removed.
        
        Args:
            key: Substrate identity (int)
        
        Returns:
            New DimensionalDict with key removed
        
        Raises:
            KeyError: If key not found
        """
        if key not in self._mapping:
            raise KeyError(f"Key {key} not found")
        
        new_mapping = dict(self._mapping)
        del new_mapping[key]
        return DimensionalDict(new_mapping)
    
    def map_values(self, transform: Callable[[Substrate], Substrate]) -> DimensionalDict:
        """
        Transform all values and return NEW dictionary.
        
        Args:
            transform: Function that takes a substrate and returns a substrate
        
        Returns:
            New DimensionalDict with transformed values
        """
        new_mapping = {key: transform(value) for key, value in self._mapping.items()}
        return DimensionalDict(new_mapping)
    
    def __repr__(self) -> str:
        return f"DimensionalDict({len(self._mapping)} pairs)"

