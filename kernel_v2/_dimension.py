"""
Dimension - Containment levels.

Higher dimensions contain all lower dimensions.
Promotion into higher dimensions is the mechanism of change.
"""

__all__ = ['Dimension']


class Dimension:
    """
    Dimensional level.
    
    Properties:
    - Each dimension contains all lower dimensions
    - Substrates exist at specific dimensional levels
    - Promotion moves to higher dimension
    """
    __slots__ = ('_level',)
    
    def __init__(self, level: int):
        """
        Create a dimension.
        
        Args:
            level: Non-negative dimensional level
        """
        # Ensure non-negative
        level = max(0, level)
        object.__setattr__(self, '_level', level)
    
    def __setattr__(self, name, value):
        raise TypeError("Dimension is immutable")
    
    def __delattr__(self, name):
        raise TypeError("Dimension is immutable")
    
    @property
    def level(self) -> int:
        """The dimensional level."""
        return self._level
    
    def contains(self, other: 'Dimension') -> bool:
        """
        Check if this dimension contains another.
        
        Higher dimensions contain all lower dimensions.
        """
        return self._level >= other._level
    
    def __gt__(self, other: 'Dimension') -> bool:
        return self._level > other._level
    
    def __ge__(self, other: 'Dimension') -> bool:
        return self._level >= other._level
    
    def __lt__(self, other: 'Dimension') -> bool:
        return self._level < other._level
    
    def __le__(self, other: 'Dimension') -> bool:
        return self._level <= other._level
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Dimension):
            return self._level == other._level
        return False
    
    def __hash__(self) -> int:
        return self._level
    
    def __repr__(self) -> str:
        return f"D{self._level}"
    
    def __int__(self) -> int:
        return self._level
