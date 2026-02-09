"""
Dimensional Search Algorithms

Search algorithms that work with dimensional structures:
- All algorithms are pure functions (no mutation)
- Search is observation (Law 2: Observation Is Division)
- Comparison is based on substrate properties
- Follows Charter principles (immutability, no side effects)

CHARTER COMPLIANCE:
✅ Principle 2: Passive Until Invoked - No background processing
✅ Principle 3: No Self-Modifying Code - Immutable at runtime
✅ Principle 5: No Hacking Surface - Pure functions only
"""

from __future__ import annotations
from typing import Callable, Optional
from kernel import Substrate
from structures import DimensionalList, DimensionalSet


def linear_search(
    lst: DimensionalList,
    predicate: Callable[[Substrate], bool]
) -> Optional[Substrate]:
    """
    Linear search for first element matching predicate.
    
    Time complexity: O(n)
    
    Args:
        lst: DimensionalList to search
        predicate: Function that returns True for matching substrate
    
    Returns:
        First matching substrate, or None if not found
    
    Example:
        result = linear_search(lst, lambda s: s.identity.value == 42)
        result = linear_search(lst, lambda s: s.invoke() > 100)
    """
    for substrate in lst:
        if predicate(substrate):
            return substrate
    return None


def linear_search_all(
    lst: DimensionalList,
    predicate: Callable[[Substrate], bool]
) -> DimensionalList:
    """
    Linear search for all elements matching predicate.
    
    Time complexity: O(n)
    
    Args:
        lst: DimensionalList to search
        predicate: Function that returns True for matching substrate
    
    Returns:
        DimensionalList of all matching substrates
    
    Example:
        results = linear_search_all(lst, lambda s: s.invoke() > 100)
    """
    return lst.filter(predicate)


def binary_search(
    lst: DimensionalList,
    target: int,
    key: Optional[Callable[[Substrate], int]] = None
) -> Optional[Substrate]:
    """
    Binary search for element with target key value.
    
    REQUIRES: List must be sorted by key
    Time complexity: O(log n)
    
    Args:
        lst: Sorted DimensionalList to search
        target: Target key value to find
        key: Optional function to extract comparison key from substrate
             (default: use substrate identity)
    
    Returns:
        Substrate with matching key, or None if not found
    
    Example:
        result = binary_search(sorted_list, 42)
        result = binary_search(sorted_list, 100, key=lambda s: s.invoke())
    """
    if key is None:
        key = lambda s: s.identity.value
    
    left, right = 0, len(lst) - 1
    
    while left <= right:
        mid = (left + right) // 2
        mid_key = key(lst[mid])
        
        if mid_key == target:
            return lst[mid]
        elif mid_key < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return None


def find_min(
    lst: DimensionalList,
    key: Optional[Callable[[Substrate], int]] = None
) -> Optional[Substrate]:
    """
    Find element with minimum key value.
    
    Time complexity: O(n)
    
    Args:
        lst: DimensionalList to search
        key: Optional function to extract comparison key from substrate
             (default: use substrate identity)
    
    Returns:
        Substrate with minimum key, or None if list is empty
    
    Example:
        min_substrate = find_min(lst)
        min_substrate = find_min(lst, key=lambda s: s.invoke())
    """
    if len(lst) == 0:
        return None
    
    if key is None:
        key = lambda s: s.identity.value
    
    min_substrate = lst[0]
    min_key = key(min_substrate)
    
    for substrate in lst:
        substrate_key = key(substrate)
        if substrate_key < min_key:
            min_substrate = substrate
            min_key = substrate_key
    
    return min_substrate


def find_max(
    lst: DimensionalList,
    key: Optional[Callable[[Substrate], int]] = None
) -> Optional[Substrate]:
    """
    Find element with maximum key value.
    
    Time complexity: O(n)
    
    Args:
        lst: DimensionalList to search
        key: Optional function to extract comparison key from substrate
             (default: use substrate identity)
    
    Returns:
        Substrate with maximum key, or None if list is empty
    
    Example:
        max_substrate = find_max(lst)
        max_substrate = find_max(lst, key=lambda s: s.invoke())
    """
    if len(lst) == 0:
        return None
    
    if key is None:
        key = lambda s: s.identity.value
    
    max_substrate = lst[0]
    max_key = key(max_substrate)
    
    for substrate in lst:
        substrate_key = key(substrate)
        if substrate_key > max_key:
            max_substrate = substrate
            max_key = substrate_key
    
    return max_substrate


def contains(
    lst: DimensionalList,
    predicate: Callable[[Substrate], bool]
) -> bool:
    """
    Check if list contains any element matching predicate.
    
    Time complexity: O(n)
    
    Args:
        lst: DimensionalList to search
        predicate: Function that returns True for matching substrate
    
    Returns:
        True if any element matches, False otherwise
    
    Example:
        has_match = contains(lst, lambda s: s.identity.value == 42)
    """
    return linear_search(lst, predicate) is not None


def count(
    lst: DimensionalList,
    predicate: Callable[[Substrate], bool]
) -> int:
    """
    Count elements matching predicate.
    
    Time complexity: O(n)
    
    Args:
        lst: DimensionalList to search
        predicate: Function that returns True for matching substrate
    
    Returns:
        Number of matching elements
    
    Example:
        count = count(lst, lambda s: s.invoke() > 100)
    """
    return len(linear_search_all(lst, predicate))

