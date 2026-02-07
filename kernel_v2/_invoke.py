"""
Invoke - Truth revelation through lens.

substrate → lens → invocation → truth

Attributes are derived, never stored.
"""

from ._substrate import Substrate
from ._lens import Lens

__all__ = ['invoke']


def invoke(substrate: Substrate, lens: Lens) -> int:
    """
    Invoke substrate through lens to reveal truth.
    
    This is the fundamental computation:
        substrate → lens → attribute
    
    Args:
        substrate: The substrate to query
        lens: The projection lens
    
    Returns:
        The derived 64-bit attribute value (y₁)
    
    Nothing is stored. Everything is computed on demand.
    """
    # Step 1: Evaluate substrate expression
    substrate_value = substrate.evaluate()
    
    # Step 2: Apply lens projection
    attribute = lens.project(substrate_value)
    
    return attribute


def invoke_batch(substrate: Substrate, lenses: list) -> list:
    """
    Invoke substrate through multiple lenses.
    
    Returns list of derived attributes.
    """
    substrate_value = substrate.evaluate()
    return [lens.project(substrate_value) for lens in lenses]
