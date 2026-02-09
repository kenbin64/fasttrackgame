"""
Dimensional Query DSL - Navigate Dimensional Structures

Human-readable query language for dimensional navigation:

Instead of:
    dims = substrate.divide()
    identity_dim = dims[0]
    domain_dim = dims[1]

Use:
    query = DimensionalQuery(substrate)
    identity_dim = query.dimension("identity").get()
    domain_dim = query.dimension("domain").get()

Or:
    dims = query.select("identity", "domain", "range").as_list()

CHARTER COMPLIANCE:
✅ Principle 1: Returns references, not copies
✅ Principle 2: Passive until invoked
✅ Principle 5: Pure functions only
"""

from __future__ import annotations
from typing import List, Optional, Union
from kernel import Substrate, Dimension


# Dimension name to index mapping (0-8)
# Maps dimension names to their position in the divide() list
DIMENSION_NAMES = {
    "void": 0,        # Dimension(0) - potential
    "identity": 1,    # Dimension(1) - who
    "domain": 2,      # Dimension(1) - what type
    "length": 3,      # Dimension(2) - attributes
    "area": 4,        # Dimension(3) - relationships
    "volume": 5,      # Dimension(5) - state + change
    "frequency": 6,   # Dimension(8) - temporal patterns
    "system": 7,      # Dimension(13) - behaviors
    "complete": 8,    # Dimension(21) - whole object
}

# Reverse mapping (index to name)
DIMENSION_INDEX_TO_NAME = {v: k for k, v in DIMENSION_NAMES.items()}

# Dimension level to name mapping
DIMENSION_LEVEL_TO_NAME = {
    0: "void",
    1: "identity/domain",
    2: "length",
    3: "area",
    5: "volume",
    8: "frequency",
    13: "system",
    21: "complete",
}


class DimensionalQuery:
    """
    Fluent API for querying dimensional structures.
    
    Example:
        query = DimensionalQuery(substrate)
        
        # Get single dimension
        identity = query.dimension("identity").get()
        
        # Get multiple dimensions
        dims = query.select("identity", "domain", "range").as_list()
        
        # Get dimension by index
        dim = query.at(0).get()
    """
    
    def __init__(self, substrate: Substrate):
        """
        Initialize query for a substrate.
        
        Args:
            substrate: The substrate to query
        """
        self._substrate = substrate
        self._dimensions: Optional[List[Dimension]] = None
        self._selected_indices: List[int] = []
    
    def _ensure_divided(self) -> None:
        """Ensure substrate has been divided (lazy evaluation)."""
        if self._dimensions is None:
            self._dimensions = self._substrate.divide()
    
    def dimension(self, name: str) -> DimensionalQuery:
        """
        Select a dimension by name.
        
        Args:
            name: Dimension name (identity, domain, range, behavior, state, time, connection, pattern, unity)
        
        Returns:
            Self for chaining
        
        Raises:
            ValueError: If dimension name is invalid
        """
        if name not in DIMENSION_NAMES:
            raise ValueError(
                f"Invalid dimension name '{name}'. "
                f"Valid names: {', '.join(DIMENSION_NAMES.keys())}"
            )
        
        self._selected_indices = [DIMENSION_NAMES[name]]
        return self
    
    def at(self, index: int) -> DimensionalQuery:
        """
        Select a dimension by index.
        
        Args:
            index: Dimension index (0-8)
        
        Returns:
            Self for chaining
        
        Raises:
            ValueError: If index is out of range
        """
        if not (0 <= index <= 8):
            raise ValueError(f"Dimension index must be 0-8, got {index}")
        
        self._selected_indices = [index]
        return self
    
    def select(self, *names: str) -> DimensionalQuery:
        """
        Select multiple dimensions by name.
        
        Args:
            *names: Dimension names
        
        Returns:
            Self for chaining
        
        Example:
            query.select("identity", "domain", "range")
        """
        indices = []
        for name in names:
            if name not in DIMENSION_NAMES:
                raise ValueError(
                    f"Invalid dimension name '{name}'. "
                    f"Valid names: {', '.join(DIMENSION_NAMES.keys())}"
                )
            indices.append(DIMENSION_NAMES[name])
        
        self._selected_indices = indices
        return self
    
    def get(self) -> Dimension:
        """
        Get the selected dimension.

        Returns:
            The selected dimension

        Raises:
            ValueError: If no dimension selected or multiple selected
        """
        if len(self._selected_indices) == 0:
            raise ValueError("No dimension selected")
        if len(self._selected_indices) > 1:
            raise ValueError("Multiple dimensions selected, use as_list() instead")

        self._ensure_divided()
        return self._dimensions[self._selected_indices[0]]

    def get_index(self) -> int:
        """
        Get the index of the selected dimension.

        Returns:
            The dimension index (0-8)
        """
        if len(self._selected_indices) == 0:
            raise ValueError("No dimension selected")
        if len(self._selected_indices) > 1:
            raise ValueError("Multiple dimensions selected")

        return self._selected_indices[0]
    
    def as_list(self) -> List[Dimension]:
        """
        Get selected dimensions as a list.
        
        Returns:
            List of selected dimensions
        """
        if len(self._selected_indices) == 0:
            # No selection - return all dimensions
            self._ensure_divided()
            return self._dimensions
        
        self._ensure_divided()
        return [self._dimensions[i] for i in self._selected_indices]
    
    def all(self) -> List[Dimension]:
        """
        Get all dimensions.
        
        Returns:
            List of all 9 dimensions
        """
        self._ensure_divided()
        return self._dimensions

