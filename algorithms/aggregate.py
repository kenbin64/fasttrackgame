"""
Dimensional Aggregation Algorithms

Aggregation algorithms that work with dimensional structures:
- All algorithms are pure functions (no mutation)
- All algorithms return NEW structures
- Aggregation combines dimensions (Law 1: Multiplication recombines dimensions)
- Follows Charter principles (immutability, no side effects)

CHARTER COMPLIANCE:
✅ Principle 2: Passive Until Invoked - No background processing
✅ Principle 3: No Self-Modifying Code - Immutable at runtime
✅ Principle 5: No Hacking Surface - Pure functions only
"""

from __future__ import annotations
from typing import Callable, TypeVar
from kernel import Substrate
from structures import DimensionalList

T = TypeVar('T')


def fold_left(
    lst: DimensionalList,
    folder: Callable[[T, Substrate], T],
    initial: T
) -> T:
    """
    Fold (reduce) list from left to right with accumulator.
    
    Time complexity: O(n)
    
    Args:
        lst: DimensionalList to fold
        folder: Function that combines accumulator and substrate
        initial: Initial accumulator value
    
    Returns:
        Final accumulator value
    
    Example:
        # Sum all identity values
        total = fold_left(lst, lambda acc, s: acc + s.identity.value, 0)
    """
    accumulator = initial
    for substrate in lst:
        accumulator = folder(accumulator, substrate)
    return accumulator


def fold_right(
    lst: DimensionalList,
    folder: Callable[[Substrate, T], T],
    initial: T
) -> T:
    """
    Fold (reduce) list from right to left with accumulator.
    
    Time complexity: O(n)
    
    Args:
        lst: DimensionalList to fold
        folder: Function that combines substrate and accumulator
        initial: Initial accumulator value
    
    Returns:
        Final accumulator value
    
    Example:
        # Build list in reverse
        result = fold_right(lst, lambda s, acc: [s] + acc, [])
    """
    accumulator = initial
    for i in range(len(lst) - 1, -1, -1):
        accumulator = folder(lst[i], accumulator)
    return accumulator


def scan_left(
    lst: DimensionalList,
    scanner: Callable[[Substrate, Substrate], Substrate],
    initial: Substrate
) -> DimensionalList:
    """
    Scan (cumulative fold) from left to right.
    
    Returns list of intermediate accumulator values.
    
    Time complexity: O(n)
    
    Args:
        lst: DimensionalList to scan
        scanner: Function that combines two substrates
        initial: Initial accumulator substrate
    
    Returns:
        DimensionalList of intermediate results (includes initial)
    
    Example:
        # Cumulative sum
        cumulative = scan_left(lst, lambda acc, s: combine(acc, s), initial_substrate)
    """
    result = [initial]
    accumulator = initial
    
    for substrate in lst:
        accumulator = scanner(accumulator, substrate)
        result.append(accumulator)
    
    return DimensionalList(result)


def zip_lists(
    lst1: DimensionalList,
    lst2: DimensionalList,
    combiner: Callable[[Substrate, Substrate], Substrate]
) -> DimensionalList:
    """
    Zip two lists together element-wise.
    
    Time complexity: O(min(n, m))
    
    Args:
        lst1: First DimensionalList
        lst2: Second DimensionalList
        combiner: Function that combines two substrates into one
    
    Returns:
        DimensionalList of combined elements (length = min of input lengths)
    
    Example:
        zipped = zip_lists(lst1, lst2, lambda s1, s2: combine(s1, s2))
    """
    result = []
    min_len = min(len(lst1), len(lst2))
    
    for i in range(min_len):
        combined = combiner(lst1[i], lst2[i])
        result.append(combined)
    
    return DimensionalList(result)


def zip_with_index(
    lst: DimensionalList
) -> DimensionalList:
    """
    Zip list with indices.
    
    Note: Returns list of tuples (index, substrate) wrapped as substrates.
    This is a convenience function for tracking positions.
    
    Time complexity: O(n)
    
    Args:
        lst: DimensionalList to zip
    
    Returns:
        DimensionalList where each element contains (index, original_substrate)
    
    Example:
        indexed = zip_with_index(lst)
        # Access: indexed[i] contains tuple (i, original_substrate)
    """
    from kernel import SubstrateIdentity
    
    result = []
    for i, substrate in enumerate(lst):
        # Create substrate that holds tuple (index, substrate)
        # Use identity based on original substrate
        indexed_substrate = Substrate(
            SubstrateIdentity(substrate.identity.value),
            lambda idx=i, s=substrate: (idx, s)
        )
        result.append(indexed_substrate)
    
    return DimensionalList(result)


def group_by(
    lst: DimensionalList,
    key_fn: Callable[[Substrate], int]
) -> dict[int, DimensionalList]:
    """
    Group substrates by key function.
    
    Time complexity: O(n)
    
    Args:
        lst: DimensionalList to group
        key_fn: Function that extracts grouping key from substrate
    
    Returns:
        Dictionary mapping keys to DimensionalLists
    
    Example:
        # Group by identity modulo 10
        groups = group_by(lst, lambda s: s.identity.value % 10)
    """
    groups: dict[int, list[Substrate]] = {}
    
    for substrate in lst:
        key = key_fn(substrate)
        if key not in groups:
            groups[key] = []
        groups[key].append(substrate)
    
    # Convert lists to DimensionalLists
    return {k: DimensionalList(v) for k, v in groups.items()}


def chunk(
    lst: DimensionalList,
    size: int
) -> List[DimensionalList]:
    """
    Split list into chunks of given size.

    Time complexity: O(n)

    Args:
        lst: DimensionalList to chunk
        size: Size of each chunk

    Returns:
        List of DimensionalLists (chunks)

    Note:
        Returns a Python list of DimensionalLists, not a DimensionalList of substrates.
        This is because DimensionalLists are structures, not substrate expression results.

    Example:
        chunks = chunk(lst, 10)  # Split into chunks of 10
        for chunk_list in chunks:
            # Process each chunk
            pass
    """
    if size <= 0:
        raise ValueError("Chunk size must be positive")

    result = []
    for i in range(0, len(lst), size):
        chunk_list = lst.slice(i, min(i + size, len(lst)))
        result.append(chunk_list)

    return result

