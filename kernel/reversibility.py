"""
Reversibility Validation - The Redemption Equation

This module validates that all transformations are reversible according to
the Redemption Equation: T⁻¹(T(x)) = x

DIMENSIONAL LAW:
"Every descent must have a path back"

CHARTER PRINCIPLE 9:
"The Redemption Equation - Every transformation reversible"

Mathematical expression:
    For any transformation T and its inverse T⁻¹:
    T⁻¹(T(x)) = x  (forward then reverse returns to origin)
    T(T⁻¹(x)) = x  (reverse then forward returns to origin)

REVERSIBILITY REQUIREMENTS:
1. Addition/Subtraction: (x + y) - y = x
2. Multiplication/Division: (x * y) / y = x (when y ≠ 0)
3. Modulus/Residue: expressed + residue = original
4. Promote/Demote: demote(promote(x)) = x

CHARTER COMPLIANCE:
✅ Principle 3: Immutable at runtime (validation is pure)
✅ Principle 5: Pure functions only
✅ Principle 9: Redemption Equation enforced

LAW ALIGNMENT:
- Law 6: Identity persists through change
- Law 7: Return to unity (all paths lead back)
"""

from __future__ import annotations
from typing import Tuple, Optional
from kernel.substrate import SubstrateIdentity
from kernel.residue import DimensionalResidue


class ReversibilityError(Exception):
    """Raised when a transformation is not reversible."""
    pass


# ═══════════════════════════════════════════════════════════════
# ADDITION/SUBTRACTION REVERSIBILITY
# ═══════════════════════════════════════════════════════════════

def validate_addition_reversibility(x: int, y: int, result: int) -> bool:
    """
    Validate that addition is reversible: (x + y) - y = x
    
    Args:
        x: Original value
        y: Value added
        result: Result of addition (x + y)
    
    Returns:
        True if reversible
    
    Raises:
        ReversibilityError: If not reversible
    """
    # Reverse the addition
    reversed_value = (result - y) & 0xFFFFFFFFFFFFFFFF
    
    if reversed_value != x:
        raise ReversibilityError(
            f"Addition not reversible: ({x} + {y}) - {y} = {reversed_value}, expected {x}"
        )
    
    return True


def validate_subtraction_reversibility(x: int, y: int, result: int) -> bool:
    """
    Validate that subtraction is reversible: (x - y) + y = x
    
    Args:
        x: Original value
        y: Value subtracted
        result: Result of subtraction (x - y)
    
    Returns:
        True if reversible
    
    Raises:
        ReversibilityError: If not reversible
    """
    # Reverse the subtraction
    reversed_value = (result + y) & 0xFFFFFFFFFFFFFFFF
    
    if reversed_value != x:
        raise ReversibilityError(
            f"Subtraction not reversible: ({x} - {y}) + {y} = {reversed_value}, expected {x}"
        )
    
    return True


# ═══════════════════════════════════════════════════════════════
# MULTIPLICATION/DIVISION REVERSIBILITY
# ═══════════════════════════════════════════════════════════════

def validate_multiplication_reversibility(
    x: int,
    y: int,
    result: int,
    tolerance: float = 0.01
) -> bool:
    """
    Validate that multiplication is reversible: (x * y) / y ≈ x
    
    Note: Due to 64-bit bounds and modular arithmetic, exact reversal
    may not always be possible. We check within tolerance.
    
    Args:
        x: Original value
        y: Multiplier
        result: Result of multiplication (x * y)
        tolerance: Acceptable relative error (default 1%)
    
    Returns:
        True if reversible within tolerance
    
    Raises:
        ReversibilityError: If not reversible
    """
    if y == 0:
        raise ReversibilityError("Cannot reverse multiplication by zero")
    
    # Reverse the multiplication (integer division)
    reversed_value = result // y
    
    # Check if within tolerance
    if x == 0:
        if reversed_value != 0:
            raise ReversibilityError(
                f"Multiplication not reversible: ({x} * {y}) / {y} = {reversed_value}, expected {x}"
            )
    else:
        relative_error = abs(reversed_value - x) / x
        if relative_error > tolerance:
            raise ReversibilityError(
                f"Multiplication not reversible: ({x} * {y}) / {y} = {reversed_value}, "
                f"expected {x} (error: {relative_error:.2%})"
            )
    
    return True


# ═══════════════════════════════════════════════════════════════
# MODULUS/RESIDUE REVERSIBILITY
# ═══════════════════════════════════════════════════════════════

def validate_residue_reversibility(
    original: int,
    expressed: int,
    residue: DimensionalResidue
) -> bool:
    """
    Validate that modulus is reversible: expressed + residue = original
    
    Args:
        original: Original substrate value
        expressed: Expressed value (original % modulus)
        residue: Dimensional residue
    
    Returns:
        True if reversible
    
    Raises:
        ReversibilityError: If not reversible
    """
    # Reconstruct original from expressed + residue
    reconstructed = (expressed + residue.value) & 0xFFFFFFFFFFFFFFFF
    
    if reconstructed != original:
        raise ReversibilityError(
            f"Residue not reversible: {expressed} + {residue.value} = {reconstructed}, "
            f"expected {original}"
        )
    
    return True

