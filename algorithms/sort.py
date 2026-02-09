"""
Dimensional Sorting Algorithms

Sorting algorithms that work with dimensional structures:
- All algorithms are pure functions (no mutation)
- All algorithms return NEW structures
- Comparison is based on substrate properties (identity or invocation result)
- Follows Charter principles (immutability, no side effects)

CHARTER COMPLIANCE:
✅ Principle 2: Passive Until Invoked - No background processing
✅ Principle 3: No Self-Modifying Code - Immutable at runtime
✅ Principle 5: No Hacking Surface - Pure functions only
"""

from __future__ import annotations
from typing import Callable, Optional
from kernel import Substrate
from structures import DimensionalList


def merge_sort(
    lst: DimensionalList,
    key: Optional[Callable[[Substrate], int]] = None
) -> DimensionalList:
    """
    Merge sort for dimensional lists.
    
    Time complexity: O(n log n)
    Space complexity: O(n)
    
    Args:
        lst: DimensionalList to sort
        key: Optional function to extract comparison key from substrate
             (default: use substrate identity)
    
    Returns:
        New sorted DimensionalList
    
    Example:
        sorted_list = merge_sort(lst)
        sorted_list = merge_sort(lst, key=lambda s: s.invoke())
    """
    if key is None:
        key = lambda s: s.identity.value
    
    # Base case: lists of 0 or 1 element are already sorted
    if len(lst) <= 1:
        return lst
    
    # Divide
    mid = len(lst) // 2
    left = lst.slice(0, mid)
    right = lst.slice(mid, None)
    
    # Conquer (recursively sort)
    left_sorted = merge_sort(left, key)
    right_sorted = merge_sort(right, key)
    
    # Combine (merge)
    return _merge(left_sorted, right_sorted, key)


def _merge(
    left: DimensionalList,
    right: DimensionalList,
    key: Callable[[Substrate], int]
) -> DimensionalList:
    """
    Merge two sorted lists into one sorted list.
    
    Args:
        left: Sorted DimensionalList
        right: Sorted DimensionalList
        key: Function to extract comparison key
    
    Returns:
        Merged sorted DimensionalList
    """
    result = []
    i, j = 0, 0
    
    # Merge while both lists have elements
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    # Append remaining elements
    while i < len(left):
        result.append(left[i])
        i += 1
    
    while j < len(right):
        result.append(right[j])
        j += 1
    
    return DimensionalList(result)


def quick_sort(
    lst: DimensionalList,
    key: Optional[Callable[[Substrate], int]] = None
) -> DimensionalList:
    """
    Quick sort for dimensional lists.
    
    Time complexity: O(n log n) average, O(n²) worst case
    Space complexity: O(log n) average
    
    Args:
        lst: DimensionalList to sort
        key: Optional function to extract comparison key from substrate
             (default: use substrate identity)
    
    Returns:
        New sorted DimensionalList
    
    Example:
        sorted_list = quick_sort(lst)
        sorted_list = quick_sort(lst, key=lambda s: s.invoke())
    """
    if key is None:
        key = lambda s: s.identity.value
    
    # Base case: lists of 0 or 1 element are already sorted
    if len(lst) <= 1:
        return lst
    
    # Choose pivot (middle element)
    pivot_idx = len(lst) // 2
    pivot = lst[pivot_idx]
    pivot_key = key(pivot)
    
    # Partition
    less = []
    equal = []
    greater = []
    
    for substrate in lst:
        substrate_key = key(substrate)
        if substrate_key < pivot_key:
            less.append(substrate)
        elif substrate_key == pivot_key:
            equal.append(substrate)
        else:
            greater.append(substrate)
    
    # Recursively sort partitions and concatenate
    less_sorted = quick_sort(DimensionalList(less), key)
    greater_sorted = quick_sort(DimensionalList(greater), key)
    
    return less_sorted.concat(DimensionalList(equal)).concat(greater_sorted)


def is_sorted(
    lst: DimensionalList,
    key: Optional[Callable[[Substrate], int]] = None,
    descending: bool = False
) -> bool:
    """
    Check if a dimensional list is sorted.
    
    Args:
        lst: DimensionalList to check
        key: Optional function to extract comparison key from substrate
             (default: use substrate identity)
        descending: Check for descending order (default: False)
    
    Returns:
        True if sorted, False otherwise
    """
    if key is None:
        key = lambda s: s.identity.value
    
    if len(lst) <= 1:
        return True
    
    for i in range(len(lst) - 1):
        current_key = key(lst[i])
        next_key = key(lst[i + 1])
        
        if descending:
            if current_key < next_key:
                return False
        else:
            if current_key > next_key:
                return False
    
    return True

