"""
Fibonacci Spiral Geometry - Mathematical Foundation
====================================================

The Universal Substrate Law states:
- Division creates dimensions following the Fibonacci spiral
- Multiplication collapses dimensions back to unity
- The Golden Ratio (φ) is the natural limiter

This module provides the mathematical functions for:
- Fibonacci sequence generation
- Golden Ratio calculations
- Spiral geometry
- Dimensional navigation

NOTE: Fibonacci calculations use raw arithmetic operators because they
compute mathematical sequences, not dimensional operations. The Fibonacci
sequence itself is the PATTERN that dimensional operations follow, not
a dimensional operation itself.
"""

from __future__ import annotations
import math


# Golden Ratio constant
PHI = (1 + math.sqrt(5)) / 2  # ≈ 1.618033988749895


def fibonacci(n: int) -> int:
    """
    Generate the nth Fibonacci number.
    
    The Fibonacci sequence: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144...
    
    Recurrence relation: f(n) = f(n-1) + f(n-2)
    
    Args:
        n: Index in the Fibonacci sequence (0-based)
    
    Returns:
        The nth Fibonacci number
    
    Examples:
        fibonacci(0) → 0
        fibonacci(1) → 1
        fibonacci(2) → 1
        fibonacci(3) → 2
        fibonacci(8) → 21
    """
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    
    # Iterative calculation for efficiency
    # NOTE: Uses raw + operator because Fibonacci is a mathematical sequence,
    # not a dimensional operation. The sequence defines the PATTERN that
    # dimensional operations follow.
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def fibonacci_sequence(count: int) -> list:
    """
    Generate a sequence of Fibonacci numbers.
    
    Args:
        count: Number of Fibonacci numbers to generate
    
    Returns:
        List of Fibonacci numbers
    
    Example:
        fibonacci_sequence(9) → [0, 1, 1, 2, 3, 5, 8, 13, 21]
    """
    return [fibonacci(i) for i in range(count)]


def golden_ratio_limit(n: int) -> float:
    """
    Calculate the ratio of consecutive Fibonacci numbers.
    
    As n approaches infinity, f(n+1)/f(n) approaches φ (Golden Ratio).
    
    Args:
        n: Index in the Fibonacci sequence
    
    Returns:
        Ratio f(n+1)/f(n)
    
    Example:
        golden_ratio_limit(10) → ~1.618 (approaching φ)
    """
    fn = fibonacci(n)
    fn_plus_1 = fibonacci(n + 1)
    
    if fn == 0:
        return 0.0
    
    return fn_plus_1 / fn


def spiral_angle(n: int) -> float:
    """
    Calculate the angle (in radians) for the nth point on the Fibonacci spiral.
    
    Each division creates a new angle based on the Golden Ratio.
    
    Args:
        n: Division index
    
    Returns:
        Angle in radians
    """
    # Golden angle = 2π / φ² ≈ 2.399963 radians ≈ 137.5°
    golden_angle = 2 * math.pi / (PHI * PHI)
    return n * golden_angle


def spiral_radius(n: int) -> float:
    """
    Calculate the radius for the nth point on the Fibonacci spiral.
    
    The radius grows according to the Fibonacci sequence.
    
    Args:
        n: Division index
    
    Returns:
        Radius (distance from center)
    """
    return math.sqrt(fibonacci(n))


def spiral_coordinates(n: int) -> tuple:
    """
    Calculate (x, y) coordinates for the nth point on the Fibonacci spiral.
    
    Args:
        n: Division index
    
    Returns:
        Tuple of (x, y) coordinates
    """
    angle = spiral_angle(n)
    radius = spiral_radius(n)
    
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    
    return (x, y)


def dimensional_index(dimension_level: int) -> int:
    """
    Map a dimension level to its Fibonacci index.
    
    Dimension structure:
    - 0D → fibonacci(0) = 0
    - 1D → fibonacci(1) = 1
    - 1D → fibonacci(2) = 1
    - 2D → fibonacci(3) = 2
    - 3D → fibonacci(4) = 3
    - 5D → fibonacci(5) = 5
    - 8D → fibonacci(6) = 8
    - 13D → fibonacci(7) = 13
    - 21D → fibonacci(8) = 21
    
    Args:
        dimension_level: The dimensional level (0, 1, 2, 3, 5, 8, 13, 21)
    
    Returns:
        Index in the Fibonacci sequence
    """
    # Map dimension level to Fibonacci index
    dimension_map = {
        0: 0,   # Void
        1: 1,   # Identity/Domain
        2: 3,   # Length
        3: 4,   # Area
        5: 5,   # Volume
        8: 6,   # Frequency
        13: 7,  # System
        21: 8,  # Complete
    }
    
    return dimension_map.get(dimension_level, 0)

