"""
Strategy Pattern - Lens as Interchangeable Strategy

The Strategy Pattern in ButterflyFx uses Lens as the strategy:
- Different lenses = different observation strategies
- Same substrate, different interpretations
- Strategy selection at observation time

CHARTER COMPLIANCE:
✅ Principle 1: Returns references, not copies
✅ Principle 2: Passive until invoked
✅ Principle 3: Immutable at runtime
✅ Principle 5: Pure functions only

LAW ALIGNMENT:
- Law 2: Observation is division
- Law 4: Connection creates meaning
"""

from __future__ import annotations
from typing import Callable, List, Optional
from kernel import Substrate, Lens


class ObservationStrategy:
    """
    Strategy for observing substrates through different lenses.
    
    Each lens represents a different strategy for interpreting
    the substrate's manifestation.
    """
    __slots__ = ('_strategies',)
    
    def __init__(self, strategies: Optional[List[Lens]] = None):
        """
        Create observation strategy.
        
        Args:
            strategies: Optional list of lenses (strategies)
        """
        if strategies is None:
            strategies = []
        object.__setattr__(self, '_strategies', tuple(strategies))
    
    def __setattr__(self, name, value):
        raise TypeError("ObservationStrategy is immutable")
    
    def __delattr__(self, name):
        raise TypeError("ObservationStrategy is immutable")
    
    @property
    def strategies(self) -> tuple[Lens, ...]:
        """Available strategies"""
        return self._strategies
    
    def observe_with_strategy(
        self,
        substrate: Substrate,
        strategy_index: int
    ) -> int:
        """
        Observe substrate using specific strategy.
        
        Args:
            substrate: Substrate to observe
            strategy_index: Index of strategy to use
        
        Returns:
            Manifestation through selected lens
        
        Raises:
            IndexError: If strategy index out of range
        
        Example:
            # Create strategies
            identity_lens = Lens(1, lambda x: x)
            double_lens = Lens(2, lambda x: x * 2)
            
            strategy = ObservationStrategy([identity_lens, double_lens])
            
            # Observe with different strategies
            result1 = strategy.observe_with_strategy(substrate, 0)  # identity
            result2 = strategy.observe_with_strategy(substrate, 1)  # doubled
        """
        if not (0 <= strategy_index < len(self._strategies)):
            raise IndexError(f"Strategy index {strategy_index} out of range")
        
        lens = self._strategies[strategy_index]
        return lens.projection(substrate.invoke())
    
    def observe_all_strategies(self, substrate: Substrate) -> List[int]:
        """
        Observe substrate through all strategies.
        
        Args:
            substrate: Substrate to observe
        
        Returns:
            List of manifestations, one per strategy
        
        Example:
            strategy = ObservationStrategy([lens1, lens2, lens3])
            results = strategy.observe_all_strategies(substrate)
            # results = [manifestation1, manifestation2, manifestation3]
        """
        return [
            lens.projection(substrate.invoke())
            for lens in self._strategies
        ]
    
    def add_strategy(self, lens: Lens) -> 'ObservationStrategy':
        """
        Create new strategy with additional lens.
        
        Args:
            lens: Lens to add
        
        Returns:
            New ObservationStrategy with added lens
        
        Example:
            strategy = ObservationStrategy([lens1])
            new_strategy = strategy.add_strategy(lens2)
            # new_strategy has [lens1, lens2]
        """
        new_strategies = list(self._strategies) + [lens]
        return ObservationStrategy(new_strategies)
    
    def select_best_strategy(
        self,
        substrate: Substrate,
        criterion: Callable[[int], float]
    ) -> tuple[int, int]:
        """
        Select best strategy based on criterion.
        
        Args:
            substrate: Substrate to observe
            criterion: Function that scores manifestations (higher = better)
        
        Returns:
            Tuple of (best_strategy_index, best_manifestation)
        
        Raises:
            ValueError: If no strategies available
        
        Example:
            # Select strategy that produces smallest value
            strategy = ObservationStrategy([lens1, lens2, lens3])
            index, value = strategy.select_best_strategy(
                substrate,
                lambda x: -x  # Negative for minimization
            )
        """
        if not self._strategies:
            raise ValueError("No strategies available")
        
        best_index = 0
        best_manifestation = self._strategies[0].projection(substrate.invoke())
        best_score = criterion(best_manifestation)
        
        for i in range(1, len(self._strategies)):
            manifestation = self._strategies[i].projection(substrate.invoke())
            score = criterion(manifestation)
            
            if score > best_score:
                best_index = i
                best_manifestation = manifestation
                best_score = score
        
        return (best_index, best_manifestation)

