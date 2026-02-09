"""
ButterflyFx Dimensional Algorithms

Pure functional algorithms that work with dimensional data structures:
- All algorithms are pure functions (no mutation, no side effects)
- All algorithms return NEW structures (immutability)
- Algorithms follow the Seven Dimensional Laws
- Charter-compliant (passive until invoked, no hacking surface)

ALGORITHM CATEGORIES:

1. SORTING (algorithms/sort.py):
   - merge_sort: O(n log n) merge sort
   - quick_sort: O(n log n) average quick sort
   - is_sorted: Check if list is sorted

2. SEARCHING (algorithms/search.py):
   - linear_search: O(n) linear search for first match
   - linear_search_all: O(n) linear search for all matches
   - binary_search: O(log n) binary search (requires sorted list)
   - find_min: O(n) find minimum element
   - find_max: O(n) find maximum element
   - contains: O(n) check if element exists
   - count: O(n) count matching elements

3. TRANSFORMATION (algorithms/transform.py):
   - map_list: Transform all elements
   - filter_list: Filter elements by predicate
   - reduce_list: Reduce list to single value
   - flat_map: Map and flatten
   - partition: Split into two lists
   - take: Take first n elements
   - drop: Drop first n elements
   - reverse: Reverse list

4. TRAVERSAL (algorithms/traverse.py):
   - dfs_tree: Depth-first search for trees
   - bfs_tree: Breadth-first search for trees
   - dfs_graph: Depth-first search for graphs
   - bfs_graph: Breadth-first search for graphs
   - find_path: Find path between vertices

5. AGGREGATION (algorithms/aggregate.py):
   - fold_left: Fold from left with accumulator
   - fold_right: Fold from right with accumulator
   - scan_left: Cumulative fold (returns intermediate results)
   - zip_lists: Combine two lists element-wise
   - zip_with_index: Zip list with indices
   - group_by: Group elements by key
   - chunk: Split list into chunks

CHARTER COMPLIANCE:
✅ Principle 1: All Things Are by Reference - No copying
✅ Principle 2: Passive Until Invoked - No background processing
✅ Principle 3: No Self-Modifying Code - Immutable at runtime
✅ Principle 5: No Hacking Surface - Pure functions only
✅ Principle 6: No Dark Web, No Concealment Dimensions - All operations visible
"""

# Sorting
from .sort import merge_sort, quick_sort, is_sorted

# Searching
from .search import (
    linear_search,
    linear_search_all,
    binary_search,
    find_min,
    find_max,
    contains,
    count,
)

# Transformation
from .transform import (
    map_list,
    filter_list,
    reduce_list,
    flat_map,
    partition,
    take,
    drop,
    reverse,
)

# Traversal
from .traverse import (
    dfs_tree,
    bfs_tree,
    dfs_graph,
    bfs_graph,
    find_path,
)

# Aggregation
from .aggregate import (
    fold_left,
    fold_right,
    scan_left,
    zip_lists,
    zip_with_index,
    group_by,
    chunk,
)


__all__ = [
    # Sorting
    'merge_sort',
    'quick_sort',
    'is_sorted',
    # Searching
    'linear_search',
    'linear_search_all',
    'binary_search',
    'find_min',
    'find_max',
    'contains',
    'count',
    # Transformation
    'map_list',
    'filter_list',
    'reduce_list',
    'flat_map',
    'partition',
    'take',
    'drop',
    'reverse',
    # Traversal
    'dfs_tree',
    'bfs_tree',
    'dfs_graph',
    'bfs_graph',
    'find_path',
    # Aggregation
    'fold_left',
    'fold_right',
    'scan_left',
    'zip_lists',
    'zip_with_index',
    'group_by',
    'chunk',
]

