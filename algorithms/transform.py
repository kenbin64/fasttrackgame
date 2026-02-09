"""
Dimensional Transformation Algorithms

Transformation algorithms that work with dimensional structures:
- All algorithms are pure functions (no mutation)
- All algorithms return NEW structures
- Transformations follow Law 5 (Change Is Motion)
- Follows Charter principles (immutability, no side effects)

CHARTER COMPLIANCE:
✅ Principle 2: Passive Until Invoked - No background processing
✅ Principle 3: No Self-Modifying Code - Immutable at runtime
✅ Principle 5: No Hacking Surface - Pure functions only
"""

from __future__ import annotations
from typing import Callable, TypeVar, Any
from kernel import Substrate
from structures import DimensionalList, DimensionalDict, DimensionalSet

T = TypeVar('T')


def map_list(
    lst: DimensionalList,
    transform: Callable[[Substrate], Substrate]
) -> DimensionalList:
    """
    Map transformation over dimensional list.
    
    Time complexity: O(n)
    
    Args:
        lst: DimensionalList to transform
        transform: Function that transforms substrate to new substrate
    
    Returns:
        New DimensionalList with transformed elements
    
    Example:
        new_list = map_list(lst, lambda s: transform(s))
    """
    return lst.map(transform)


def filter_list(
    lst: DimensionalList,
    predicate: Callable[[Substrate], bool]
) -> DimensionalList:
    """
    Filter dimensional list by predicate.
    
    Time complexity: O(n)
    
    Args:
        lst: DimensionalList to filter
        predicate: Function that returns True for elements to keep
    
    Returns:
        New DimensionalList with filtered elements
    
    Example:
        filtered = filter_list(lst, lambda s: s.identity.value > 100)
    """
    return lst.filter(predicate)


def reduce_list(
    lst: DimensionalList,
    reducer: Callable[[Substrate, Substrate], Substrate],
    initial: Substrate
) -> Substrate:
    """
    Reduce dimensional list to single substrate.
    
    Time complexity: O(n)
    
    Args:
        lst: DimensionalList to reduce
        reducer: Function that combines two substrates into one
        initial: Initial accumulator value
    
    Returns:
        Single substrate result
    
    Example:
        # Sum all substrate values
        total = reduce_list(lst, lambda acc, s: combine(acc, s), initial_substrate)
    """
    accumulator = initial
    for substrate in lst:
        accumulator = reducer(accumulator, substrate)
    return accumulator


def flat_map(
    lst: DimensionalList,
    transform: Callable[[Substrate], DimensionalList]
) -> DimensionalList:
    """
    Map transformation that returns lists, then flatten.
    
    Time complexity: O(n * m) where m is average list size
    
    Args:
        lst: DimensionalList to transform
        transform: Function that transforms substrate to DimensionalList
    
    Returns:
        Flattened DimensionalList
    
    Example:
        # Expand each substrate into multiple substrates
        expanded = flat_map(lst, lambda s: expand(s))
    """
    result = DimensionalList()
    for substrate in lst:
        sub_list = transform(substrate)
        result = result.concat(sub_list)
    return result


def partition(
    lst: DimensionalList,
    predicate: Callable[[Substrate], bool]
) -> tuple[DimensionalList, DimensionalList]:
    """
    Partition list into two lists based on predicate.
    
    Time complexity: O(n)
    
    Args:
        lst: DimensionalList to partition
        predicate: Function that returns True for first partition
    
    Returns:
        Tuple of (matching, non-matching) DimensionalLists
    
    Example:
        evens, odds = partition(lst, lambda s: s.identity.value % 2 == 0)
    """
    matching = []
    non_matching = []
    
    for substrate in lst:
        if predicate(substrate):
            matching.append(substrate)
        else:
            non_matching.append(substrate)
    
    return (DimensionalList(matching), DimensionalList(non_matching))


def take(
    lst: DimensionalList,
    n: int
) -> DimensionalList:
    """
    Take first n elements from list.
    
    Time complexity: O(n)
    
    Args:
        lst: DimensionalList to take from
        n: Number of elements to take
    
    Returns:
        New DimensionalList with first n elements
    
    Example:
        first_10 = take(lst, 10)
    """
    return lst.slice(0, min(n, len(lst)))


def drop(
    lst: DimensionalList,
    n: int
) -> DimensionalList:
    """
    Drop first n elements from list.
    
    Time complexity: O(n)
    
    Args:
        lst: DimensionalList to drop from
        n: Number of elements to drop
    
    Returns:
        New DimensionalList without first n elements
    
    Example:
        rest = drop(lst, 10)
    """
    return lst.slice(min(n, len(lst)), None)


def reverse(
    lst: DimensionalList
) -> DimensionalList:
    """
    Reverse dimensional list.
    
    Time complexity: O(n)
    
    Args:
        lst: DimensionalList to reverse
    
    Returns:
        New reversed DimensionalList
    
    Example:
        reversed_list = reverse(lst)
    """
    elements = [lst[i] for i in range(len(lst) - 1, -1, -1)]
    return DimensionalList(elements)

