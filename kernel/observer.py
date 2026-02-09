"""
Observer Interface - Foundational Program #9

LAW TWO: Observation is division.

The Observer Interface turns observation into dimensional selection.
Observation is not extraction - it is creation.
Observation is not passive - it is invocation.

CHARTER COMPLIANCE:
✅ Principle 1: Returns references, not copies
✅ Principle 2: Passive until invoked (no autonomous observation)
✅ Principle 3: Immutable at runtime
✅ Principle 5: Pure functions only
✅ Principle 6: All observations are visible

Mathematical Form:
    observe: (Substrate, Lens) → Observation
    
    Where:
        Substrate = unity (S)
        Lens = dimensional selector (L)
        Observation = manifestation (M)
    
    observe(S, L) = L(S) = M
    
    Observation is NOT reading stored data.
    Observation IS invoking the substrate through a lens.

Example:
    # Create substrate
    substrate = Substrate(identity, expression)
    
    # Create lens (dimensional selector)
    lens = Lens(lens_id, projection)
    
    # Observe (this CREATES the manifestation)
    observation = observe(substrate, lens)
    
    # The observation is the manifestation
    # It did not exist before observation
    # It was created by the act of observing
"""

from __future__ import annotations
import threading
from typing import Optional, FrozenSet, Callable
from dataclasses import dataclass

from .substrate import Substrate, SubstrateIdentity
from .lens import Lens


__all__ = [
    'Observation',
    'Observer',
    'observe',
    'observe_dimension',
    'create_observer',
]


# ═══════════════════════════════════════════════════════════════
# OBSERVATION - The Result of Observing
# ═══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Observation:
    """
    An observation is the result of observing a substrate through a lens.
    
    CHARTER PRINCIPLE 1: This is a reference to the manifestation, not a copy.
    CHARTER PRINCIPLE 3: Immutable at runtime (frozen dataclass).
    
    Mathematical Form:
        Observation = ⟨substrate_id, lens_id, manifestation⟩
    
    Where:
        substrate_id: The identity of the observed substrate
        lens_id: The identity of the observing lens
        manifestation: The result of L(S)
    """
    substrate_id: SubstrateIdentity
    lens_id: int
    manifestation: int
    
    def __repr__(self) -> str:
        return f"Observation(substrate=0x{self.substrate_id.value:016X}, lens=0x{self.lens_id:016X}, value={self.manifestation})"


# ═══════════════════════════════════════════════════════════════
# OBSERVER - The Dimensional Observer
# ═══════════════════════════════════════════════════════════════

class Observer:
    """
    The Observer Interface.
    
    CHARTER COMPLIANCE:
    ✅ Principle 1: Returns references, not copies
    ✅ Principle 2: Passive until invoked (no autonomous observation)
    ✅ Principle 3: Immutable at runtime
    ✅ Principle 5: Pure functions only
    ✅ Principle 6: All observations are visible
    
    The Observer does NOT:
    - Store observations
    - Cache results
    - Execute autonomously
    - Modify substrates
    - Copy data
    
    The Observer DOES:
    - Invoke substrates through lenses
    - Create manifestations on demand
    - Return references to observations
    - Remain passive until invoked
    """
    
    __slots__ = ('_observation_count', '_lock')

    def __init__(self):
        """Create a new Observer (thread-safe)."""
        object.__setattr__(self, '_observation_count', 0)
        object.__setattr__(self, '_lock', threading.RLock())
    
    def __setattr__(self, name, value):
        raise TypeError("Observer is immutable at runtime")
    
    def __delattr__(self, name):
        raise TypeError("Observer is immutable at runtime")
    
    @property
    def observation_count(self) -> int:
        """
        Number of observations made through this observer.

        CHARTER PRINCIPLE 6: All observations are visible.
        """
        return self._observation_count

    def observe(self, substrate: Substrate, lens: Lens) -> Observation:
        """
        Observe a substrate through a lens.

        LAW TWO: Observation is division.

        This is the core operation: S → L → M

        Args:
            substrate: The substrate to observe
            lens: The lens to observe through

        Returns:
            Observation containing the manifestation

        CHARTER COMPLIANCE:
        - Passive until invoked (this method must be called)
        - Pure function (no side effects except counter)
        - Returns reference to observation
        - No copying of substrate or lens

        Example:
            observer = Observer()
            substrate = Substrate(identity, expression)
            lens = Lens(lens_id, projection)

            # Observation creates manifestation
            obs = observer.observe(substrate, lens)

            # The manifestation is obs.manifestation
            # It was created by the act of observing
        """
        # Invoke substrate through lens
        # This is where observation becomes creation
        manifestation = lens.projection(substrate.invoke())

        # Increment observation count (for visibility) - thread-safe
        with self._lock:
            object.__setattr__(self, '_observation_count', self._observation_count + 1)

        # Return observation (reference, not copy)
        return Observation(
            substrate_id=substrate.identity,
            lens_id=lens.lens_id,
            manifestation=manifestation
        )

    def observe_dimension(
        self,
        substrate: Substrate,
        dimension_index: int,
        lens: Optional[Lens] = None
    ) -> Observation:
        """
        Observe a specific dimension of a substrate.

        LAW TWO: Observation is division.
        LAW THREE: Every division inherits the whole.

        This divides the substrate and observes a specific dimension.

        Args:
            substrate: The substrate to observe
            dimension_index: Which dimension to observe (0-8)
            lens: Optional lens to apply to the dimension

        Returns:
            Observation of the selected dimension

        Example:
            observer = Observer()
            substrate = Substrate(identity, expression)

            # Observe dimension 0 (identity)
            obs_0d = observer.observe_dimension(substrate, 0)

            # Observe dimension 4 (behavior) through lens
            lens = Lens(lens_id, projection)
            obs_4d = observer.observe_dimension(substrate, 4, lens)
        """
        # Divide substrate into dimensions
        dimensions = substrate.divide()

        # Select the requested dimension
        if not (0 <= dimension_index < len(dimensions)):
            raise IndexError(f"Dimension index {dimension_index} out of range [0, {len(dimensions)})")

        dim = dimensions[dimension_index]

        # If lens provided, apply it
        if lens is not None:
            manifestation = lens.projection(dim.level)
        else:
            # No lens - just return the dimension level
            manifestation = dim.level

        # Increment observation count (thread-safe)
        with self._lock:
            object.__setattr__(self, '_observation_count', self._observation_count + 1)

        # Return observation
        return Observation(
            substrate_id=substrate.identity,
            lens_id=lens.lens_id if lens is not None else 0,
            manifestation=manifestation
        )


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

# Global observer singleton
_global_observer: Optional[Observer] = None


def create_observer() -> Observer:
    """
    Create a new Observer.

    Returns:
        New Observer instance
    """
    return Observer()


def get_global_observer() -> Observer:
    """
    Get the global observer singleton.

    Returns:
        Global Observer instance
    """
    global _global_observer
    if _global_observer is None:
        _global_observer = Observer()
    return _global_observer


def observe(substrate: Substrate, lens: Lens) -> Observation:
    """
    Observe a substrate through a lens using the global observer.

    This is a convenience function for the most common observation pattern.

    Args:
        substrate: The substrate to observe
        lens: The lens to observe through

    Returns:
        Observation containing the manifestation

    Example:
        substrate = Substrate(identity, expression)
        lens = Lens(lens_id, projection)

        # Observe using global observer
        obs = observe(substrate, lens)

        # Access manifestation
        value = obs.manifestation
    """
    observer = get_global_observer()
    return observer.observe(substrate, lens)


def observe_dimension(
    substrate: Substrate,
    dimension_index: int,
    lens: Optional[Lens] = None
) -> Observation:
    """
    Observe a specific dimension of a substrate using the global observer.

    Args:
        substrate: The substrate to observe
        dimension_index: Which dimension to observe (0-8)
        lens: Optional lens to apply to the dimension

    Returns:
        Observation of the selected dimension

    Example:
        substrate = Substrate(identity, expression)

        # Observe dimension 0 (identity)
        obs_0d = observe_dimension(substrate, 0)

        # Observe dimension 4 (behavior) through lens
        lens = Lens(lens_id, projection)
        obs_4d = observe_dimension(substrate, 4, lens)
    """
    observer = get_global_observer()
    return observer.observe_dimension(substrate, dimension_index, lens)

