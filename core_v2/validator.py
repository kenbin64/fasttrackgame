"""
Validator - Enforces the 15 Laws of ButterflyFx.

All operations from Human/Machine/AI must pass validation
before reaching the Kernel through the Gateway.
"""

from __future__ import annotations
from typing import Any, Callable, Optional, Set

__all__ = ['Validator', 'ValidationError']


class ValidationError(Exception):
    """Raised when an operation violates ButterflyFx laws."""
    
    def __init__(self, message: str, law: Optional[int] = None):
        self.law = law
        law_str = f" (Law {law})" if law else ""
        super().__init__(f"{message}{law_str}")


class Validator:
    """
    Validates operations against the 15 Laws.
    
    THE 15 LAWS:
    1.  Dimensional Supremacy - Higher dimensions contain lower
    2.  Unified Representation - All entities as substrates
    3.  Non-Duplication - Identical expressions = same identity
    4.  No Collisions - Different expressions = different identity
    5.  Immutability - No in-place modification
    6.  No Hard-Coded Dynamic Values - All dynamic values as expressions
    7.  All Attributes as Expressions - Never stored, always derived
    8.  64-bit Atomic Identity - Single 64-bit identifier
    9.  Truthful Invocation - substrate→lens→truth
    10. No State Precomputation - Compute on demand
    11. No Brute Force - No iteration to find identity
    12. No Fabrication - No fake identities
    13. Core-Kernel Separation - Core translates, Kernel computes
    14. Dimensional Promotion Only - Change only through promotion
    15. Manifold Discovery - Manifolds discovered, not created
    """
    
    # ═══════════════════════════════════════════════════════════════
    # LAW 5: IMMUTABILITY
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_immutable(obj: Any) -> None:
        """
        Validate object is properly immutable.
        
        Law 5: Entities cannot be modified in place.
        """
        if not hasattr(obj, '__slots__'):
            raise ValidationError(
                f"{type(obj).__name__} lacks __slots__ for immutability",
                law=5
            )
        
        if hasattr(obj, '__dict__') and obj.__dict__:
            raise ValidationError(
                f"{type(obj).__name__} has mutable __dict__",
                law=5
            )
    
    # ═══════════════════════════════════════════════════════════════
    # LAW 8: 64-BIT ATOMIC IDENTITY
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_64bit(value: int, name: str = "value") -> None:
        """
        Validate value fits in 64 bits.
        
        Law 8: All identities must be 64-bit.
        """
        if not isinstance(value, int):
            raise ValidationError(f"{name} must be an integer", law=8)
        
        if value < 0:
            raise ValidationError(f"{name} must be non-negative", law=8)
        
        if value >= 2**64:
            raise ValidationError(f"{name} exceeds 64-bit limit", law=8)
    
    # ═══════════════════════════════════════════════════════════════
    # LAW 7: ALL ATTRIBUTES AS EXPRESSIONS
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_expression(expr: Callable[[], int]) -> None:
        """
        Validate expression returns 64-bit int.
        
        Law 7: Attributes are expressions, not stored values.
        """
        if not callable(expr):
            raise ValidationError("Expression must be callable", law=7)
        
        try:
            result = expr()
            if not isinstance(result, int):
                raise ValidationError(
                    f"Expression must return int, got {type(result).__name__}",
                    law=7
                )
            Validator.validate_64bit(result, "expression result")
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Expression failed: {e}", law=7)
    
    # ═══════════════════════════════════════════════════════════════
    # LAW 6: NO HARD-CODED DYNAMIC VALUES
    # ═══════════════════════════════════════════════════════════════
    
    FORBIDDEN_DYNAMIC = frozenset([
        'age', 'timestamp', 'position', 'state', 'counter',
        'current', 'now', 'today', 'random'
    ])
    
    @staticmethod
    def validate_no_hardcoded_dynamic(
        expr: Callable,
        forbidden: Optional[Set[str]] = None
    ) -> None:
        """
        Validate expression doesn't contain hard-coded dynamic values.
        
        Law 6: Dynamic values that change over time must be
        expressed as math, not stored constants.
        """
        if forbidden is None:
            forbidden = Validator.FORBIDDEN_DYNAMIC
        
        # Check closure variables
        if hasattr(expr, '__closure__') and expr.__closure__:
            for cell in expr.__closure__:
                cell_contents = cell.cell_contents
                if isinstance(cell_contents, str):
                    lower = cell_contents.lower()
                    for word in forbidden:
                        if word in lower:
                            raise ValidationError(
                                f"Expression contains forbidden dynamic term: {word}",
                                law=6
                            )
    
    # ═══════════════════════════════════════════════════════════════
    # LAW 9: TRUTHFUL INVOCATION
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_lens_projection(projection: Callable[[int], int]) -> None:
        """
        Validate lens projection is deterministic.
        
        Law 9: Same substrate + same lens = same result.
        """
        if not callable(projection):
            raise ValidationError("Projection must be callable", law=9)
        
        # Test determinism with sample value
        try:
            test_value = 0x123456789ABCDEF0
            result1 = projection(test_value)
            result2 = projection(test_value)
            
            if result1 != result2:
                raise ValidationError(
                    "Projection is non-deterministic",
                    law=9
                )
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Projection test failed: {e}", law=9)
    
    # ═══════════════════════════════════════════════════════════════
    # LAW 14: DIMENSIONAL PROMOTION ONLY
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_promotion_inputs(x1: int, y1: int, z1: int) -> None:
        """
        Validate promotion inputs.
        
        Law 14: Change occurs only through dimensional promotion.
        """
        Validator.validate_64bit(x1, "x1 (identity)")
        Validator.validate_64bit(y1, "y1 (attribute)")
        Validator.validate_64bit(z1, "z1 (delta)")
    
    # ═══════════════════════════════════════════════════════════════
    # BATCH VALIDATION
    # ═══════════════════════════════════════════════════════════════
    
    @classmethod
    def validate_all(cls, **validations) -> None:
        """
        Run multiple validations.
        
        Args:
            **validations: name -> (validator_method, args)
        
        Example:
            Validator.validate_all(
                identity=('validate_64bit', [identity]),
                expression=('validate_expression', [expr])
            )
        """
        for name, (method_name, args) in validations.items():
            method = getattr(cls, method_name)
            try:
                method(*args)
            except ValidationError as e:
                raise ValidationError(f"{name}: {e}") from e
