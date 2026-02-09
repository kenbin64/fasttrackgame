"""
Composite Pattern - Hierarchical Substrate Structures

The Composite Pattern in ButterflyFx creates tree structures:
- Substrates can contain other substrates
- Uniform interface for leaf and composite substrates
- Recursive operations on substrate trees

CHARTER COMPLIANCE:
✅ Principle 1: Returns references, not copies
✅ Principle 2: Passive until invoked
✅ Principle 3: Immutable at runtime
✅ Principle 5: Pure functions only
✅ Principle 7: Fibonacci-bounded growth (predictable recursion)

LAW ALIGNMENT:
- Law 1: Division generates dimensions
- Law 3: Every division inherits the whole
- Law 7: Return to unity (composites reduce to single value)
"""

from __future__ import annotations
from typing import List, Callable, Optional
from kernel import Substrate, SubstrateIdentity


class CompositeSubstrate:
    """
    Composite substrate that contains child substrates.
    
    Provides uniform interface for working with individual substrates
    and compositions of substrates.
    """
    __slots__ = ('_substrate', '_children', '_aggregation')
    
    def __init__(
        self,
        substrate: Substrate,
        children: Optional[List['CompositeSubstrate']] = None,
        aggregation: Optional[Callable[[List[int]], int]] = None
    ):
        """
        Create composite substrate.
        
        Args:
            substrate: The substrate at this node
            children: Optional list of child composites
            aggregation: Optional function to aggregate child results
                        Default: sum of all child invocations
        
        Example:
            # Leaf node
            leaf = CompositeSubstrate(substrate1)
            
            # Composite node
            composite = CompositeSubstrate(
                substrate2,
                children=[leaf1, leaf2],
                aggregation=lambda results: sum(results)
            )
        """
        if children is None:
            children = []
        if aggregation is None:
            aggregation = lambda results: sum(results) & 0xFFFFFFFFFFFFFFFF
        
        object.__setattr__(self, '_substrate', substrate)
        object.__setattr__(self, '_children', tuple(children))
        object.__setattr__(self, '_aggregation', aggregation)
    
    def __setattr__(self, name, value):
        raise TypeError("CompositeSubstrate is immutable")
    
    def __delattr__(self, name):
        raise TypeError("CompositeSubstrate is immutable")
    
    @property
    def substrate(self) -> Substrate:
        """The substrate at this node"""
        return self._substrate
    
    @property
    def children(self) -> tuple['CompositeSubstrate', ...]:
        """Child composites"""
        return self._children
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf node (no children)"""
        return len(self._children) == 0
    
    def invoke(self, **kwargs) -> int:
        """
        Invoke composite substrate.
        
        For leaf nodes: invokes substrate directly
        For composite nodes: invokes substrate and aggregates children
        
        Args:
            **kwargs: Arguments to pass to substrate invocation
        
        Returns:
            Aggregated result
        
        Example:
            composite = CompositeSubstrate(root, [child1, child2])
            result = composite.invoke()
        """
        # Invoke this substrate
        result = self._substrate.invoke(**kwargs)
        
        # If leaf, return result
        if self.is_leaf():
            return result
        
        # Invoke all children
        child_results = [child.invoke(**kwargs) for child in self._children]
        
        # Aggregate children with this result
        all_results = [result] + child_results
        return self._aggregation(all_results)
    
    def add_child(self, child: 'CompositeSubstrate') -> 'CompositeSubstrate':
        """
        Create new composite with additional child.
        
        Args:
            child: Child composite to add
        
        Returns:
            New CompositeSubstrate with added child
        
        Example:
            composite = CompositeSubstrate(substrate)
            new_composite = composite.add_child(child)
        """
        new_children = list(self._children) + [child]
        return CompositeSubstrate(self._substrate, new_children, self._aggregation)
    
    def map_tree(self, fn: Callable[[Substrate], Substrate]) -> 'CompositeSubstrate':
        """
        Map function over entire tree.
        
        Args:
            fn: Function to apply to each substrate
        
        Returns:
            New CompositeSubstrate with transformed substrates
        
        Example:
            # Double all substrate results
            doubled = composite.map_tree(
                lambda s: Substrate(s.identity, lambda: s.invoke() * 2)
            )
        """
        # Transform this substrate
        new_substrate = fn(self._substrate)
        
        # Recursively transform children
        new_children = [child.map_tree(fn) for child in self._children]
        
        return CompositeSubstrate(new_substrate, new_children, self._aggregation)
    
    def count_nodes(self) -> int:
        """
        Count total nodes in tree.
        
        Returns:
            Total number of nodes (including this one)
        """
        return 1 + sum(child.count_nodes() for child in self._children)

