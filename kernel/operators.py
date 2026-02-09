"""
Dimensional Operators - Complete Operator Framework

This module implements ALL operators in dimensional programming, categorized into:

1. CROSS-DIMENSIONAL OPERATORS - Change dimensional structure
   - Division (/) - Creates dimensions
   - Multiplication (*) - Collapses dimensions
   - Modulus (%) - Dimensional residue
   - Power (**) - Dimensional stacking
   - Root (√) - Dimensional reduction

2. INTRA-DIMENSIONAL OPERATORS - Work within dimensions
   - Addition (+) - Expand within dimension
   - Subtraction (-) - Contract within dimension
   - Logical (AND, OR, NOT, XOR, NAND, NOR) - Filter points
   - Comparison (=, !=, <, >, <=, >=) - Compare points
   - Bitwise (&, |, ^, ~) - Manipulate bits

PHILOSOPHY: "Sometimes points are just points if we do not go deeper."

CHARTER COMPLIANCE:
✅ Principle 1: All things are by reference
✅ Principle 3: No self-modifying code (immutable)
✅ Principle 5: No hacking surface (pure functions)
✅ Principle 7: Fibonacci-bounded growth
✅ Principle 9: Redemption Equation (reversibility)
"""

from __future__ import annotations
from typing import List, Tuple, Callable
from kernel.substrate import Substrate, SubstrateIdentity
from kernel.dimensional import Dimension
from kernel.residue import DimensionalResidue, compute_residue

# 64-bit mask
MASK_64 = 0xFFFFFFFFFFFFFFFF


# ═══════════════════════════════════════════════════════════════════
# CROSS-DIMENSIONAL OPERATORS
# These operators CHANGE the dimensional structure
# ═══════════════════════════════════════════════════════════════════

def cross_divide(substrate: Substrate) -> List[Dimension]:
    """
    Division CREATES dimensions (cross-dimensional).
    
    Divides unity into the 9 Fibonacci dimensions.
    This is the fundamental operation of dimensional expansion.
    
    Args:
        substrate: The substrate to divide
    
    Returns:
        List of 9 dimensions (Fibonacci: 0, 1, 1, 2, 3, 5, 8, 13, 21)
    
    Example:
        dimensions = cross_divide(substrate)
        # Creates 9 new dimensions from unity
    
    LAW ALIGNMENT:
    - Law 1: Division generates dimensions
    - Law 2: Observation is division
    - Law 3: Every division inherits the whole
    """
    return substrate.divide()


def cross_multiply(values: List[int]) -> int:
    """
    Multiplication COLLAPSES dimensions (cross-dimensional).
    
    Takes multiple dimensional values and collapses them back to
    a single unified value (return to unity).
    
    Args:
        values: List of dimensional values to collapse
    
    Returns:
        Unified value (product, bounded to 64 bits)
    
    Example:
        unity = cross_multiply([2, 3, 5])  # 30
    
    LAW ALIGNMENT:
    - Law 1: Multiplication recombines dimensions
    - Law 7: Return to unity
    
    REVERSIBILITY:
    - Can be reversed by division: unity / factor = original
    """
    if not values:
        return 1  # Multiplicative identity
    
    result = 1
    for value in values:
        result = (result * value) & MASK_64
    
    return result


def cross_modulus(
    substrate_value: int,
    dimension_modulus: int,
    source_identity: SubstrateIdentity
) -> Tuple[int, DimensionalResidue]:
    """
    Modulus returns DIMENSIONAL RESIDUE (cross-dimensional).
    
    The residue is the unexpressed identity that seeds the next
    dimensional recursion. This drives Fibonacci-like growth.
    
    Args:
        substrate_value: The substrate's manifested value
        dimension_modulus: The dimension's modulus
        source_identity: Original substrate identity
    
    Returns:
        Tuple of (expressed_value, residue)
    
    Example:
        expressed, residue = cross_modulus(100, 7, identity)
        # expressed = 2 (what CAN be expressed)
        # residue.value = 98 (what CANNOT be expressed - seeds next dimension)
    
    LAW ALIGNMENT:
    - Law 1: Residue drives dimensional creation
    - Law 3: Residue inherits the whole
    - Law 6: Identity persists through residue
    """
    return compute_residue(substrate_value, dimension_modulus, source_identity)


def cross_power(base: int, exponent: int) -> int:
    """
    Power creates DIMENSIONAL STACKING (cross-dimensional).

    Recursive multiplication creates higher-order dimensional spaces:
    - x^1 = length (1D)
    - x^2 = area (2D)
    - x^3 = volume (3D)

    Args:
        base: Base value
        exponent: Exponent (dimensional order)

    Returns:
        Result (bounded to 64 bits)

    Example:
        area = cross_power(5, 2)  # 25 (2D space)
        volume = cross_power(5, 3)  # 125 (3D space)

    LAW ALIGNMENT:
    - Law 3: Inheritance and recursion
    - Law 7: Fibonacci-bounded growth
    """
    if exponent == 0:
        return 1
    if exponent == 1:
        return base & MASK_64

    result = base
    for _ in range(exponent - 1):
        result = (result * base) & MASK_64

    return result


def cross_root(value: int, degree: int) -> int:
    """
    Root performs DIMENSIONAL REDUCTION (cross-dimensional).

    Inverse of power - reduces dimensional order:
    - √(area) = length (2D → 1D)
    - ∛(volume) = length (3D → 1D)

    Args:
        value: Value to take root of
        degree: Root degree (2 = square root, 3 = cube root, etc.)

    Returns:
        Root value (integer approximation, bounded to 64 bits)

    Example:
        length = cross_root(25, 2)  # 5 (from 2D to 1D)
        length = cross_root(125, 3)  # 5 (from 3D to 1D)

    LAW ALIGNMENT:
    - Law 7: Return to unity (dimensional reduction)
    - Law 9: Redemption Equation (inverse of power)
    """
    if degree == 1:
        return value & MASK_64
    if value == 0:
        return 0
    if value == 1:
        return 1

    # Integer approximation using binary search
    low, high = 0, value
    result = 0

    while low <= high:
        mid = (low + high) // 2
        mid_power = cross_power(mid, degree)

        if mid_power == value:
            return mid & MASK_64
        elif mid_power < value:
            result = mid
            low = mid + 1
        else:
            high = mid - 1

    return result & MASK_64


# ═══════════════════════════════════════════════════════════════════
# INTRA-DIMENSIONAL OPERATORS
# These operators work WITHIN dimensions (no structural change)
# ═══════════════════════════════════════════════════════════════════

def intra_add(x: int, y: int) -> int:
    """
    Addition EXPANDS within dimension (intra-dimensional).

    Adds two values within the same dimensional space.
    Like adding gas to an engine - expands magnitude, not structure.

    Args:
        x: First value
        y: Second value

    Returns:
        Sum (bounded to 64 bits)

    Example:
        expanded = intra_add(100, 50)  # 150
        # Same dimensional level, just more magnitude

    LAW ALIGNMENT:
    - Expansion within current dimension
    - Preserves dimensional level

    REVERSIBILITY:
    - Can be reversed by subtraction: (x + y) - y = x
    """
    return (x + y) & MASK_64


def intra_subtract(x: int, y: int) -> int:
    """
    Subtraction CONTRACTS within dimension (intra-dimensional).

    Subtracts values within the same dimensional space.
    Like removing rubber from a tire - contracts magnitude, not structure.

    Args:
        x: Value to contract from
        y: Amount to contract

    Returns:
        Difference (bounded to 64 bits, wraps on underflow)

    Example:
        contracted = intra_subtract(150, 50)  # 100
        # Same dimensional level, just less magnitude

    LAW ALIGNMENT:
    - Contraction within current dimension
    - Preserves dimensional level

    REVERSIBILITY:
    - Can be reversed by addition: (x - y) + y = x
    """
    return (x - y) & MASK_64


# ═══════════════════════════════════════════════════════════════════
# LOGICAL OPERATORS (All Intra-Dimensional)
# These filter/select points within a dimension
# ═══════════════════════════════════════════════════════════════════

def intra_and(x: bool, y: bool) -> bool:
    """
    AND filters points within dimension (intra-dimensional).

    Both conditions must be true at THIS dimensional level.

    Example:
        result = intra_and(x > 5, x < 10)  # Selects range [6, 9]
    """
    return x and y


def intra_or(x: bool, y: bool) -> bool:
    """
    OR expands selection within dimension (intra-dimensional).

    Either condition can be true at THIS dimensional level.

    Example:
        result = intra_or(x < 5, x > 10)  # Selects two ranges
    """
    return x or y


def intra_not(x: bool) -> bool:
    """
    NOT inverts selection within dimension (intra-dimensional).

    Inverts condition at THIS dimensional level.

    Example:
        result = intra_not(x > 5)  # Selects x <= 5
    """
    return not x


def intra_xor(x: bool, y: bool) -> bool:
    """
    XOR selects non-overlapping points (intra-dimensional).

    One or the other but not both.

    Example:
        result = intra_xor(x < 5, x > 3)  # Selects edges, excludes middle
    """
    return x != y


def intra_nand(x: bool, y: bool) -> bool:
    """
    NAND is inverted AND (intra-dimensional).

    At least one condition is false.

    Example:
        result = intra_nand(x > 5, x < 10)  # Everything except [6, 9]
    """
    return not (x and y)


def intra_nor(x: bool, y: bool) -> bool:
    """
    NOR is inverted OR (intra-dimensional).

    Both conditions must be false.

    Example:
        result = intra_nor(x < 5, x > 10)  # Only middle range [5, 10]
    """
    return not (x or y)


# ═══════════════════════════════════════════════════════════════════
# COMPARISON OPERATORS (All Intra-Dimensional)
# These compare points within a dimension
# ═══════════════════════════════════════════════════════════════════

def intra_equal(x: int, y: int) -> bool:
    """
    Equality tests if two points are the same (intra-dimensional).

    Example:
        result = intra_equal(5, 5)  # True
    """
    return x == y


def intra_not_equal(x: int, y: int) -> bool:
    """
    Inequality tests if two points are different (intra-dimensional).

    Example:
        result = intra_not_equal(5, 3)  # True
    """
    return x != y


def intra_less_than(x: int, y: int) -> bool:
    """
    Less than tests ordering within dimension (intra-dimensional).

    Example:
        result = intra_less_than(3, 5)  # True
    """
    return x < y


def intra_greater_than(x: int, y: int) -> bool:
    """
    Greater than tests ordering within dimension (intra-dimensional).

    Example:
        result = intra_greater_than(5, 3)  # True
    """
    return x > y


def intra_less_equal(x: int, y: int) -> bool:
    """
    Less than or equal tests ordering within dimension (intra-dimensional).

    Example:
        result = intra_less_equal(5, 5)  # True
    """
    return x <= y


def intra_greater_equal(x: int, y: int) -> bool:
    """
    Greater than or equal tests ordering within dimension (intra-dimensional).

    Example:
        result = intra_greater_equal(5, 5)  # True
    """
    return x >= y


# ═══════════════════════════════════════════════════════════════════
# BITWISE OPERATORS (All Intra-Dimensional)
# These manipulate bit patterns within 64-bit identity
# ═══════════════════════════════════════════════════════════════════

def intra_bitwise_and(x: int, y: int) -> int:
    """
    Bitwise AND masks/filters bits (intra-dimensional).

    Combines bits where both are 1.

    Example:
        result = intra_bitwise_and(identity, MASK_64)  # Ensure 64-bit bounds
    """
    return (x & y) & MASK_64


def intra_bitwise_or(x: int, y: int) -> int:
    """
    Bitwise OR merges bit patterns (intra-dimensional).

    Combines bits where either is 1.

    Example:
        result = intra_bitwise_or(flags, NEW_FLAG)  # Add flag
    """
    return (x | y) & MASK_64


def intra_bitwise_xor(x: int, y: int) -> int:
    """
    Bitwise XOR toggles bits (intra-dimensional).

    Combines bits where exactly one is 1.

    Example:
        result = intra_bitwise_xor(identity, TOGGLE_MASK)  # Flip bits
    """
    return (x ^ y) & MASK_64


def intra_bitwise_not(x: int) -> int:
    """
    Bitwise NOT inverts all bits (intra-dimensional).

    Flips all bits within 64-bit identity.

    Example:
        result = intra_bitwise_not(identity)  # Invert bit pattern
    """
    return (~x) & MASK_64


def intra_left_shift(x: int, bits: int) -> int:
    """
    Left shift (hybrid - can be dimensional or intra-dimensional).

    Shifts bits left (multiply by powers of 2).
    Context determines if this is dimensional scaling or bit packing.

    Example:
        result = intra_left_shift(identity, 8)  # Shift for packing
    """
    return (x << bits) & MASK_64


def intra_right_shift(x: int, bits: int) -> int:
    """
    Right shift (hybrid - can be dimensional or intra-dimensional).

    Shifts bits right (divide by powers of 2).
    Context determines if this is dimensional scaling or bit unpacking.

    Example:
        result = intra_right_shift(identity, 8)  # Shift for unpacking
    """
    return (x >> bits) & MASK_64


# ═══════════════════════════════════════════════════════════════════
# OPERATOR CATEGORIZATION
# ═══════════════════════════════════════════════════════════════════

# Cross-dimensional operators (change structure)
CROSS_DIMENSIONAL_OPS = {
    'divide': cross_divide,
    'multiply': cross_multiply,
    'modulus': cross_modulus,
    'power': cross_power,
    'root': cross_root,
}

# Intra-dimensional operators (work within structure)
INTRA_DIMENSIONAL_OPS = {
    # Arithmetic
    'add': intra_add,
    'subtract': intra_subtract,

    # Logical
    'and': intra_and,
    'or': intra_or,
    'not': intra_not,
    'xor': intra_xor,
    'nand': intra_nand,
    'nor': intra_nor,

    # Comparison
    'equal': intra_equal,
    'not_equal': intra_not_equal,
    'less_than': intra_less_than,
    'greater_than': intra_greater_than,
    'less_equal': intra_less_equal,
    'greater_equal': intra_greater_equal,

    # Bitwise
    'bitwise_and': intra_bitwise_and,
    'bitwise_or': intra_bitwise_or,
    'bitwise_xor': intra_bitwise_xor,
    'bitwise_not': intra_bitwise_not,
    'left_shift': intra_left_shift,
    'right_shift': intra_right_shift,
}


def is_cross_dimensional(op_name: str) -> bool:
    """Check if operator is cross-dimensional (changes structure)."""
    return op_name in CROSS_DIMENSIONAL_OPS


def is_intra_dimensional(op_name: str) -> bool:
    """Check if operator is intra-dimensional (works within structure)."""
    return op_name in INTRA_DIMENSIONAL_OPS



