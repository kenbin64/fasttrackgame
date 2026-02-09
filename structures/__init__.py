"""
ButterflyFx Dimensional Data Structures

Immutable data structures where:
- Elements are substrates
- All operations return NEW structures (immutability)
- Relationships follow the Seven Dimensional Laws
- Charter-compliant (no mutation, no side effects)

STRUCTURES:
- DimensionalList: Immutable list of substrates
- DimensionalDict: Immutable dictionary mapping identities to substrates
- DimensionalSet: Immutable set of substrates (uniqueness by identity)
- DimensionalTree: Immutable tree of substrates
- DimensionalGraph: Immutable graph of substrates

CHARTER COMPLIANCE:
✅ Principle 1: All Things Are by Reference - Elements are substrate references
✅ Principle 2: Passive Until Invoked - No background processing
✅ Principle 3: No Self-Modifying Code - Immutable at runtime
✅ Principle 5: No Hacking Surface - Pure functions only
✅ Principle 6: No Dark Web, No Concealment Dimensions - All relationships visible
✅ Principle 7: Fibonacci-Bounded Growth - Predictable structure
"""

from .dimensional_list import DimensionalList
from .dimensional_dict import DimensionalDict
from .dimensional_set import DimensionalSet
from .dimensional_tree import DimensionalTree, DimensionalTreeNode
from .dimensional_graph import DimensionalGraph


__all__ = [
    'DimensionalList',
    'DimensionalDict',
    'DimensionalSet',
    'DimensionalTree',
    'DimensionalTreeNode',
    'DimensionalGraph',
]

