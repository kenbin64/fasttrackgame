"""
Substrate Builder Pattern - Fluent API for Substrate Creation

Makes substrate creation human-readable and comprehensible:

Instead of:
    substrate = Substrate(SubstrateIdentity(42), lambda: 100)

Use:
    substrate = SubstrateBuilder().with_identity(42).with_expression(lambda: 100).build()

Or even simpler:
    substrate = build_substrate(42, lambda: 100)

CHARTER COMPLIANCE:
✅ Principle 1: Returns references, not copies
✅ Principle 3: Immutable at runtime
✅ Principle 5: Pure functions only
"""

from __future__ import annotations
from typing import Callable, Optional
from kernel import Substrate, SubstrateIdentity


class SubstrateBuilder:
    """
    Fluent API for building substrates with readable syntax.
    
    Example:
        builder = SubstrateBuilder()
        substrate = (builder
            .with_identity(42)
            .with_expression(lambda: 100)
            .build())
    """
    
    def __init__(self):
        """Initialize empty builder."""
        self._identity: Optional[int] = None
        self._expression: Optional[Callable[[], int]] = None
    
    def with_identity(self, identity: int) -> SubstrateBuilder:
        """
        Set the substrate identity.
        
        Args:
            identity: 64-bit identity value
        
        Returns:
            Self for chaining
        """
        self._identity = identity
        return self
    
    def with_expression(self, expression: Callable[[], int]) -> SubstrateBuilder:
        """
        Set the substrate expression.
        
        Args:
            expression: Callable that returns an integer
        
        Returns:
            Self for chaining
        """
        self._expression = expression
        return self
    
    def from_value(self, value: int) -> SubstrateBuilder:
        """
        Create expression from a constant value.
        
        Args:
            value: The constant value
        
        Returns:
            Self for chaining
        """
        self._expression = lambda: value
        return self
    
    def from_formula(self, formula: str, **variables) -> SubstrateBuilder:
        """
        Create expression from a formula string.
        
        Args:
            formula: Python expression as string (e.g., "x * y + z")
            **variables: Variable values for the formula
        
        Returns:
            Self for chaining
        
        Example:
            builder.from_formula("x * y", x=5, y=10)
        """
        # Create expression that evaluates the formula
        self._expression = lambda: eval(formula, {}, variables)
        return self
    
    def build(self) -> Substrate:
        """
        Build the substrate.
        
        Returns:
            The constructed substrate
        
        Raises:
            ValueError: If identity or expression not set
        """
        if self._identity is None:
            raise ValueError("Identity must be set before building")
        if self._expression is None:
            raise ValueError("Expression must be set before building")
        
        return Substrate(
            SubstrateIdentity(self._identity),
            self._expression
        )


# ═══════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def build_substrate(identity: int, expression: Callable[[], int]) -> Substrate:
    """
    Quick substrate builder.
    
    Args:
        identity: 64-bit identity value
        expression: Callable that returns an integer
    
    Returns:
        The constructed substrate
    
    Example:
        substrate = build_substrate(42, lambda: 100)
    """
    return Substrate(SubstrateIdentity(identity), expression)


def build_substrate_from_value(identity: int, value: int) -> Substrate:
    """
    Build substrate from a constant value.
    
    Args:
        identity: 64-bit identity value
        value: The constant value
    
    Returns:
        The constructed substrate
    
    Example:
        substrate = build_substrate_from_value(42, 100)
    """
    return Substrate(SubstrateIdentity(identity), lambda: value)


def build_substrate_from_formula(identity: int, formula: str, **variables) -> Substrate:
    """
    Build substrate from a formula string.
    
    Args:
        identity: 64-bit identity value
        formula: Python expression as string
        **variables: Variable values for the formula
    
    Returns:
        The constructed substrate
    
    Example:
        substrate = build_substrate_from_formula(42, "x * y + z", x=5, y=10, z=3)
    """
    return Substrate(
        SubstrateIdentity(identity),
        lambda: eval(formula, {}, variables)
    )

