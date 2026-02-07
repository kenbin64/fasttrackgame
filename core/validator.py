"""
Validator - Ensures all operations comply with ButterflyFx laws.

The Validator enforces:
1. Immutability
2. 64-bit identity constraints
3. No stored attributes
4. No brute force
5. No fabrication
"""

from __future__ import annotations
from typing import Any, Callable, List, Optional


class ValidationError(Exception):
    """Raised when operation violates ButterflyFx laws"""
    pass


class Validator:
    """
    Validates operations against ButterflyFx Dimensional Computation laws.
    
    All operations from Human/Machine/AI must pass validation
    before reaching the Kernel through the Gateway.
    """
    
    # ═══════════════════════════════════════════════════════════════
    # IDENTITY VALIDATION
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_64bit(value: int, name: str = "value") -> None:
        """Validate value fits in 64 bits (Law 8)"""
        if not isinstance(value, int):
            raise ValidationError(f"{name} must be an integer")
        if value < 0:
            raise ValidationError(f"{name} must be non-negative")
        if value >= 2**64:
            raise ValidationError(f"{name} exceeds 64-bit limit")
    
    # ═══════════════════════════════════════════════════════════════
    # IMMUTABILITY VALIDATION
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_immutable(obj: Any) -> None:
        """Validate object is properly immutable (Law 5)"""
        if hasattr(obj, '__dict__') and obj.__dict__:
            raise ValidationError(
                f"{type(obj).__name__} has mutable __dict__"
            )
        if not hasattr(obj, '__slots__'):
            raise ValidationError(
                f"{type(obj).__name__} missing __slots__ for immutability"
            )
    
    # ═══════════════════════════════════════════════════════════════
    # EXPRESSION VALIDATION
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_expression(expr: Callable[[], int]) -> None:
        """Validate expression is callable and returns int"""
        if not callable(expr):
            raise ValidationError("Expression must be callable")
        
        # Test invocation
        try:
            result = expr()
            if not isinstance(result, int):
                raise ValidationError(
                    f"Expression must return int, got {type(result)}"
                )
            Validator.validate_64bit(result, "expression result")
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Expression invocation failed: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # NO HARD-CODED DYNAMIC VALUES (Law 6)
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_no_hardcoded_dynamic(
        expr: Callable,
        dynamic_indicators: Optional[List[str]] = None
    ) -> None:
        """
        Validate expression doesn't contain hard-coded dynamic values.
        
        Dynamic values that change over time (e.g., age, position)
        MUST be expressed as math, not stored constants.
        """
        if dynamic_indicators is None:
            dynamic_indicators = ['age', 'timestamp', 'position', 'state']
        
        # Inspect closure for hard-coded values
        if hasattr(expr, '__closure__') and expr.__closure__:
            for cell in expr.__closure__:
                try:
                    val = cell.cell_contents
                    if isinstance(val, str) and any(
                        ind in val.lower() for ind in dynamic_indicators
                    ):
                        raise ValidationError(
                            f"Possible hard-coded dynamic value detected: {val}"
                        )
                except ValueError:
                    pass  # Empty cell
    
    # ═══════════════════════════════════════════════════════════════
    # NO BRUTE FORCE (Law 12)
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_no_brute_force(operation_name: str, item_count: int) -> None:
        """
        Validate operation doesn't require brute-force iteration.
        
        If brute force is required, the substrate is wrong.
        """
        BRUTE_FORCE_THRESHOLD = 1000
        if item_count > BRUTE_FORCE_THRESHOLD:
            raise ValidationError(
                f"Operation '{operation_name}' on {item_count} items "
                f"exceeds brute-force threshold ({BRUTE_FORCE_THRESHOLD}). "
                "Redesign substrate for mathematical derivation."
            )
    
    # ═══════════════════════════════════════════════════════════════
    # PROJECTION VALIDATION
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_projection(proj: Callable[[int], int]) -> None:
        """Validate lens projection function"""
        if not callable(proj):
            raise ValidationError("Projection must be callable")
        
        # Test with sample input
        try:
            test_input = 0xDEADBEEFCAFEBABE
            result = proj(test_input)
            if not isinstance(result, int):
                raise ValidationError(
                    f"Projection must return int, got {type(result)}"
                )
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Projection test failed: {e}")
