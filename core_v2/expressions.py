"""
Expression Builder - Fluent API for constructing Kernel expressions.

Provides a Pythonic interface for building substrate math
that compiles down to pure Kernel operations.
"""

from __future__ import annotations
from typing import Callable, Optional, Union, Any
from .gateway import Gateway
from .translator import Translator

__all__ = ['Expression', 'ExpressionBuilder']


class Expression:
    """
    Represents a mathematical expression to be evaluated by the Kernel.
    
    Expressions are immutable specifications that compile to
    substrate math when submitted to the Gateway.
    """
    __slots__ = ('_spec', '_translator')
    
    def __init__(self, spec: dict):
        object.__setattr__(self, '_spec', spec)
        object.__setattr__(self, '_translator', Translator())
    
    def __setattr__(self, name, value):
        raise TypeError("Expression is immutable")
    
    @property
    def spec(self) -> dict:
        """The expression specification."""
        return self._spec
    
    def compile(self) -> Callable[[], int]:
        """Compile to kernel-compatible callable."""
        return self._translator.to_expression(self._spec)
    
    def evaluate(self) -> int:
        """Evaluate the expression."""
        return self.compile()()
    
    # === Composition ===
    
    def xor(self, other: Union[Expression, int]) -> Expression:
        """XOR with another expression or value."""
        other_spec = other._spec if isinstance(other, Expression) else {"type": "constant", "value": other}
        return Expression({
            "type": "composite",
            "op": "xor", 
            "operands": [self._spec, other_spec]
        })
    
    def and_(self, other: Union[Expression, int]) -> Expression:
        """AND with another expression or value."""
        other_spec = other._spec if isinstance(other, Expression) else {"type": "constant", "value": other}
        return Expression({
            "type": "composite",
            "op": "and",
            "operands": [self._spec, other_spec]
        })
    
    def or_(self, other: Union[Expression, int]) -> Expression:
        """OR with another expression or value."""
        other_spec = other._spec if isinstance(other, Expression) else {"type": "constant", "value": other}
        return Expression({
            "type": "composite",
            "op": "or",
            "operands": [self._spec, other_spec]
        })
    
    def __repr__(self) -> str:
        return f"Expression({self._spec})"


class ExpressionBuilder:
    """
    Fluent builder for constructing expressions.
    
    Example:
        expr = (ExpressionBuilder()
            .constant(42)
            .xor(0xFF)
            .build())
    """
    
    def __init__(self):
        self._gateway = Gateway()
        self._translator = Translator()
        self._spec: Optional[dict] = None
    
    def constant(self, value: int) -> ExpressionBuilder:
        """Create constant expression."""
        self._spec = {"type": "constant", "value": value}
        return self
    
    def hash(self, data: Union[str, bytes]) -> ExpressionBuilder:
        """Create hashed expression."""
        if isinstance(data, str):
            data = data
        self._spec = {"type": "hash", "data": data}
        return self
    
    def derived(self, base: int, offset: int) -> ExpressionBuilder:
        """Create derived expression."""
        self._spec = {"type": "derived", "base": base, "offset": offset}
        return self
    
    def from_identity(self, identity: Any) -> ExpressionBuilder:
        """Create expression from identity source."""
        value = self._translator.to_identity(identity)
        self._spec = {"type": "constant", "value": value}
        return self
    
    def xor(self, value: int) -> ExpressionBuilder:
        """XOR with value."""
        if self._spec is None:
            raise ValueError("No base expression set")
        self._spec = {
            "type": "composite",
            "op": "xor",
            "operands": [self._spec, {"type": "constant", "value": value}]
        }
        return self
    
    def and_(self, value: int) -> ExpressionBuilder:
        """AND with value."""
        if self._spec is None:
            raise ValueError("No base expression set")
        self._spec = {
            "type": "composite", 
            "op": "and",
            "operands": [self._spec, {"type": "constant", "value": value}]
        }
        return self
    
    def or_(self, value: int) -> ExpressionBuilder:
        """OR with value."""
        if self._spec is None:
            raise ValueError("No base expression set")
        self._spec = {
            "type": "composite",
            "op": "or", 
            "operands": [self._spec, {"type": "constant", "value": value}]
        }
        return self
    
    def build(self) -> Expression:
        """Build the expression."""
        if self._spec is None:
            raise ValueError("No expression specified")
        return Expression(self._spec)
    
    def to_substrate(self, identity: Optional[Any] = None):
        """
        Build expression and create substrate.
        
        Args:
            identity: Optional identity source (uses expression if not provided)
        
        Returns:
            Substrate from gateway
        """
        expr = self.build()
        compiled = expr.compile()
        
        if identity is None:
            identity_int = compiled()
        else:
            identity_int = self._translator.to_identity(identity)
        
        identity_obj = self._gateway.create_identity(identity_int)
        return self._gateway.create_substrate(identity_obj, compiled)
