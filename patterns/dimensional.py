"""
Dimensional Pattern - Dimensional Navigation and Transformation

The Dimensional Pattern provides utilities for navigating and transforming
substrates across dimensions:
- Navigate to specific dimensions
- Transform substrates in dimensional space
- Project across multiple dimensions
- Dimensional queries and filters

CHARTER COMPLIANCE:
✅ Principle 1: Returns references, not copies
✅ Principle 2: Passive until invoked
✅ Principle 3: Immutable at runtime
✅ Principle 5: Pure functions only
✅ Principle 7: Fibonacci-bounded growth (max 9 dimensions)

LAW ALIGNMENT:
- Law 2: Observation is division
- Law 5: Change is motion through dimensions
- Law 6: Identity persists through dimensional navigation
"""

from __future__ import annotations
from typing import List, Callable, Optional
from kernel.substrate import Substrate, SubstrateIdentity
from kernel.dimensional import Dimension, promote
from kernel.delta import Delta


class DimensionalNavigator:
    """
    Navigator for traversing substrate dimensions.
    
    Provides utilities for navigating through the 9 Fibonacci dimensions:
    0 (Void), 1 (Identity), 1 (Domain), 2 (Length), 3 (Area), 
    5 (Volume), 8 (Frequency), 13 (System), 21 (Complete)
    """
    __slots__ = ('_substrate',)
    
    def __init__(self, substrate: Substrate):
        """
        Create dimensional navigator.
        
        Args:
            substrate: The substrate to navigate
        
        Example:
            nav = DimensionalNavigator(substrate)
            dim = nav.get_dimension(3)  # Get Area dimension
        """
        object.__setattr__(self, '_substrate', substrate)
    
    def __setattr__(self, name, value):
        raise TypeError("DimensionalNavigator is immutable")
    
    def get_dimension(self, index: int) -> Dimension:
        """
        Get dimension by index.
        
        Args:
            index: Dimension index (0-8)
        
        Returns:
            Dimension at that index
        
        Example:
            nav = DimensionalNavigator(substrate)
            dim = nav.get_dimension(3)  # 4th dimension (Area)
        """
        dimensions = self._substrate.divide()
        if not (0 <= index < len(dimensions)):
            raise IndexError(f"Dimension index {index} out of range")
        return dimensions[index]
    
    def get_dimension_by_level(self, level: int) -> Optional[Dimension]:
        """
        Get dimension by level value.
        
        Args:
            level: Dimension level (0, 1, 2, 3, 5, 8, 13, 21)
        
        Returns:
            Dimension with that level, or None if not found
        
        Example:
            nav = DimensionalNavigator(substrate)
            dim = nav.get_dimension_by_level(5)  # Volume dimension
        """
        dimensions = self._substrate.divide()
        for dim in dimensions:
            if dim.level == level:
                return dim
        return None
    
    def filter_dimensions(self, predicate: Callable[[Dimension], bool]) -> List[Dimension]:
        """
        Filter dimensions by predicate.
        
        Args:
            predicate: Function that returns True for dimensions to keep
        
        Returns:
            List of dimensions matching predicate
        
        Example:
            nav = DimensionalNavigator(substrate)
            high_dims = nav.filter_dimensions(lambda d: d.level >= 5)
        """
        dimensions = self._substrate.divide()
        return [dim for dim in dimensions if predicate(dim)]


class DimensionalTransformer:
    """
    Transformer for moving substrates through dimensional space.
    
    Uses the promote() function to transform substrates across dimensions
    while preserving identity continuity.
    """
    __slots__ = ()
    
    def __setattr__(self, name, value):
        raise TypeError("DimensionalTransformer is immutable")
    
    def transform(
        self,
        substrate: Substrate,
        attribute_value: int,
        delta: Delta
    ) -> Substrate:
        """
        Transform substrate to next dimension.
        
        Args:
            substrate: Original substrate
            attribute_value: Attribute value (y₁)
            delta: Change encoding (δ)
        
        Returns:
            New substrate in promoted dimension
        
        Example:
            transformer = DimensionalTransformer()
            delta = Delta(42)
            new_substrate = transformer.transform(substrate, 100, delta)
        """
        # Promote identity to next dimension
        new_identity = promote(substrate.identity, attribute_value, delta)
        
        # Preserve expression (substrate IS the expression)
        return Substrate(new_identity, substrate._expression)
    
    def transform_sequence(
        self,
        substrate: Substrate,
        transformations: List[tuple[int, Delta]]
    ) -> List[Substrate]:
        """
        Apply sequence of transformations.
        
        Args:
            substrate: Starting substrate
            transformations: List of (attribute_value, delta) tuples
        
        Returns:
            List of substrates, one for each transformation
        
        Example:
            transformer = DimensionalTransformer()
            sequence = transformer.transform_sequence(
                substrate,
                [(100, delta1), (200, delta2), (300, delta3)]
            )
        """
        result = [substrate]
        current = substrate
        
        for attr_val, delta in transformations:
            current = self.transform(current, attr_val, delta)
            result.append(current)
        
        return result


# Convenience functions

def navigate_to_dimension(substrate: Substrate, index: int) -> Dimension:
    """
    Navigate to specific dimension by index.
    
    Args:
        substrate: The substrate to navigate
        index: Dimension index (0-8)
    
    Returns:
        Dimension at that index
    """
    nav = DimensionalNavigator(substrate)
    return nav.get_dimension(index)


def transform_dimension(
    substrate: Substrate,
    attribute_value: int,
    delta: Delta
) -> Substrate:
    """
    Transform substrate to next dimension.
    
    Args:
        substrate: Original substrate
        attribute_value: Attribute value
        delta: Change encoding
    
    Returns:
        Transformed substrate
    """
    transformer = DimensionalTransformer()
    return transformer.transform(substrate, attribute_value, delta)

