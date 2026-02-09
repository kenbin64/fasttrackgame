"""
Factory Pattern - Substrate Creation via SRL

The Factory Pattern in ButterflyFx creates substrates based on:
- SRL (Substrate Resource Locator) specifications
- Type specifications
- Expression templates

CHARTER COMPLIANCE:
✅ Principle 1: Returns references, not copies
✅ Principle 2: Passive until invoked
✅ Principle 3: Immutable at runtime
✅ Principle 5: Pure functions only

LAW ALIGNMENT:
- Law 1: All substrates begin as unity
- Law 6: Identity persists through creation
"""

from __future__ import annotations
from typing import Callable, Optional, Dict, Any
from kernel import Substrate, SubstrateIdentity, SRL, create_srl_identity


class SubstrateFactory:
    """
    Factory for creating substrates with consistent patterns.
    
    The factory encapsulates substrate creation logic while maintaining
    Charter compliance and Law alignment.
    """
    __slots__ = ('_templates',)
    
    def __init__(self, templates: Optional[Dict[str, Callable]] = None):
        """
        Create a substrate factory.
        
        Args:
            templates: Optional dict of template name -> expression function
        """
        if templates is None:
            templates = {}
        object.__setattr__(self, '_templates', templates)
    
    def __setattr__(self, name, value):
        raise TypeError("SubstrateFactory is immutable")
    
    def __delattr__(self, name):
        raise TypeError("SubstrateFactory is immutable")
    
    def create_from_srl(self, srl: SRL) -> Substrate:
        """
        Create substrate from SRL specification.
        
        Args:
            srl: Substrate Resource Locator
        
        Returns:
            New substrate with identity from SRL
        
        Example:
            factory = SubstrateFactory()
            srl = SRL(create_srl_identity("constant", 42))
            substrate = factory.create_from_srl(srl)
        """
        # Extract identity from SRL
        identity = SubstrateIdentity(srl.identity)
        
        # Create expression based on SRL type
        # For now, use identity as constant expression
        expression = lambda: identity.value
        
        return Substrate(identity, expression)
    
    def create_constant(self, value: int) -> Substrate:
        """
        Create constant substrate.
        
        Args:
            value: Constant value (must fit in 64 bits)
        
        Returns:
            Substrate with constant expression
        
        Example:
            factory = SubstrateFactory()
            substrate = factory.create_constant(42)
            assert substrate.invoke() == 42
        """
        if not (0 <= value < 2**64):
            raise ValueError("Value must fit in 64 bits")
        
        identity = SubstrateIdentity(value)
        expression = lambda: value
        
        return Substrate(identity, expression)
    
    def create_linear(self, a: int, b: int) -> Substrate:
        """
        Create linear substrate: z = ax + b
        
        Args:
            a: Coefficient (slope)
            b: Constant (intercept)
        
        Returns:
            Substrate with linear expression
        
        Example:
            factory = SubstrateFactory()
            substrate = factory.create_linear(2, 3)
            # z = 2x + 3
            result = substrate.invoke(x=5)  # 2*5 + 3 = 13
        """
        # Identity is hash of expression
        identity_value = hash(f"z = {a}x + {b}") & 0xFFFFFFFFFFFFFFFF
        identity = SubstrateIdentity(identity_value)
        
        expression = lambda x=0: (a * x + b) & 0xFFFFFFFFFFFFFFFF
        
        return Substrate(identity, expression)
    
    def create_quadratic(self, a: int, b: int, c: int) -> Substrate:
        """
        Create quadratic substrate: z = ax² + bx + c
        
        Args:
            a: Quadratic coefficient
            b: Linear coefficient
            c: Constant
        
        Returns:
            Substrate with quadratic expression
        
        Example:
            factory = SubstrateFactory()
            substrate = factory.create_quadratic(1, 0, 0)
            # z = x²
            result = substrate.invoke(x=5)  # 25
        """
        # Identity is hash of expression
        identity_value = hash(f"z = {a}x² + {b}x + {c}") & 0xFFFFFFFFFFFFFFFF
        identity = SubstrateIdentity(identity_value)
        
        expression = lambda x=0: (a * x * x + b * x + c) & 0xFFFFFFFFFFFFFFFF

        return Substrate(identity, expression)

    def create_from_template(self, template_name: str, **kwargs) -> Substrate:
        """
        Create substrate from registered template.

        Args:
            template_name: Name of template
            **kwargs: Parameters for template expression

        Returns:
            Substrate created from template

        Raises:
            KeyError: If template not found

        Example:
            templates = {
                "fibonacci": lambda n=0: fibonacci(n)
            }
            factory = SubstrateFactory(templates)
            substrate = factory.create_from_template("fibonacci", n=10)
        """
        if template_name not in self._templates:
            raise KeyError(f"Template '{template_name}' not found")

        template_fn = self._templates[template_name]

        # Identity is hash of template name + params
        identity_value = hash(f"{template_name}:{kwargs}") & 0xFFFFFFFFFFFFFFFF
        identity = SubstrateIdentity(identity_value)

        # Create expression that applies template with kwargs
        expression = lambda: template_fn(**kwargs)

        return Substrate(identity, expression)

    def with_template(self, name: str, template: Callable) -> 'SubstrateFactory':
        """
        Create new factory with additional template.

        Args:
            name: Template name
            template: Template function

        Returns:
            New SubstrateFactory with added template

        Example:
            factory = SubstrateFactory()
            new_factory = factory.with_template("double", lambda x: x * 2)
        """
        new_templates = dict(self._templates)
        new_templates[name] = template
        return SubstrateFactory(new_templates)


# Convenience functions

def create_constant_substrate(value: int) -> Substrate:
    """
    Create constant substrate.

    Args:
        value: Constant value

    Returns:
        Substrate with constant expression
    """
    factory = SubstrateFactory()
    return factory.create_constant(value)


def create_linear_substrate(a: int, b: int) -> Substrate:
    """
    Create linear substrate: z = ax + b

    Args:
        a: Coefficient
        b: Constant

    Returns:
        Substrate with linear expression
    """
    factory = SubstrateFactory()
    return factory.create_linear(a, b)


def create_quadratic_substrate(a: int, b: int, c: int) -> Substrate:
    """
    Create quadratic substrate: z = ax² + bx + c

    Args:
        a: Quadratic coefficient
        b: Linear coefficient
        c: Constant

    Returns:
        Substrate with quadratic expression
    """
    factory = SubstrateFactory()
    return factory.create_quadratic(a, b, c)

