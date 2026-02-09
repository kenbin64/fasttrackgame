"""
Lens - Contextual slice for attribute access.

A lens does NOT modify a substrate.
It selects a dimensional slice, region, or interpretation.
ALL attribute access MUST occur through a lens.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .substrate import Substrate, SubstrateIdentity


class Lens:
    """
    A lens provides context for substrate observation.
    
    It does not store attributes - it defines the mathematical
    transformation for deriving attributes from substrate expressions.
    """
    __slots__ = ('_lens_id', '_projection')
    
    def __init__(
        self, 
        lens_id: int,
        projection: Callable[[int], int]
    ):
        """
        lens_id: 64-bit identity of this lens
        projection: Mathematical projection function (substrate → attribute)
        """
        if not (0 <= lens_id < 2**64):
            raise ValueError("Lens ID must fit in 64 bits")
        object.__setattr__(self, '_lens_id', lens_id)
        object.__setattr__(self, '_projection', projection)
    
    def __setattr__(self, name, value):
        raise TypeError("Lens is immutable")
    
    def __delattr__(self, name):
        raise TypeError("Lens is immutable")
    
    @property
    def lens_id(self) -> int:
        return self._lens_id
    
    @property
    def projection(self) -> Callable[[int], int]:
        return self._projection
    
    def __repr__(self) -> str:
        return f"Lens(0x{self._lens_id:016X})"

    # ═══════════════════════════════════════════════════════════════
    # DIMENSIONAL LAW HELPERS
    # ═══════════════════════════════════════════════════════════════

    # ─────────────────────────────────────────────────────────────
    # LAW TWO: Observation Is Division
    # ─────────────────────────────────────────────────────────────

    def observe_dimension(self, substrate: 'Substrate', dimension_index: int) -> int:
        """
        Observe a specific dimension of the substrate.

        LAW TWO: Observation is division.

        This method divides the substrate and projects a specific dimension.

        Args:
            substrate: The substrate to observe
            dimension_index: Which dimension to observe (0-8)

        Returns:
            Projected value of the selected dimension
        """
        # Divide substrate into dimensions
        dimensions = substrate.divide()

        # Select the requested dimension
        if 0 <= dimension_index < len(dimensions):
            dim = dimensions[dimension_index]
            # Project the dimension level
            return self._projection(dim.level)

        raise IndexError(f"Dimension index {dimension_index} out of range")

    def project_all(self, substrate: 'Substrate') -> list:
        """
        Project all dimensions of the substrate.

        LAW TWO: Division creates dimensions.

        Args:
            substrate: The substrate to project

        Returns:
            List of projected values for each dimension
        """
        # Divide substrate
        dimensions = substrate.divide()

        # Project each dimension
        return [self._projection(dim.level) for dim in dimensions]

    # ─────────────────────────────────────────────────────────────
    # LAW FOUR: Connection Creates Meaning
    # ─────────────────────────────────────────────────────────────

    def extract_meaning(self, manifestation: int) -> int:
        """
        Extract meaning from a manifestation.

        LAW FOUR: Meaning emerges from the pattern of relationships.

        The lens interprets the manifestation to extract meaning.

        Args:
            manifestation: The manifested value

        Returns:
            Interpreted meaning
        """
        # Apply projection to extract meaning
        return self._projection(manifestation)

    def interpret_relationships(self, substrate: 'Substrate') -> int:
        """
        Interpret the relational structure of a substrate.

        LAW FOUR: Connection creates meaning.

        Args:
            substrate: The substrate to interpret

        Returns:
            Interpreted relational meaning
        """
        # Get substrate's manifestation
        dimensions = substrate.divide()
        manifestation = substrate.multiply(dimensions)

        # Extract meaning through projection
        return self._projection(manifestation)

    # ─────────────────────────────────────────────────────────────
    # COMMON PROJECTION PATTERNS
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def identity_projection() -> Callable[[int], int]:
        """
        Create an identity projection (λx: x).

        Returns the value unchanged.

        Returns:
            Identity projection function
        """
        return lambda x: x & 0xFFFFFFFFFFFFFFFF

    @staticmethod
    def mask_projection(mask: int) -> Callable[[int], int]:
        """
        Create a mask projection (λx: x & mask).

        Extracts specific bits using a mask.

        Args:
            mask: 64-bit mask

        Returns:
            Mask projection function
        """
        return lambda x: (x & mask) & 0xFFFFFFFFFFFFFFFF

    @staticmethod
    def extract_bits_projection(start_bit: int, end_bit: int) -> Callable[[int], int]:
        """
        Create a bit extraction projection.

        Extracts a range of bits from the value.

        Args:
            start_bit: Starting bit position (0-63)
            end_bit: Ending bit position (0-63, inclusive)

        Returns:
            Bit extraction projection function
        """
        def extract(x: int) -> int:
            # Create mask for the bit range
            num_bits = end_bit - start_bit + 1
            mask = (1 << num_bits) - 1
            # Shift and mask
            return ((x >> start_bit) & mask) & 0xFFFFFFFFFFFFFFFF

        return extract

    @staticmethod
    def transform_projection(func: Callable[[int], int]) -> Callable[[int], int]:
        """
        Create a custom transformation projection.

        Wraps a custom function to ensure 64-bit result.

        Args:
            func: Custom transformation function

        Returns:
            Wrapped projection function
        """
        return lambda x: func(x) & 0xFFFFFFFFFFFFFFFF
