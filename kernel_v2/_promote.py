"""
Promote - The ONLY mechanism of change.

promote(x₁, y₁, z₁) → m₁

Takes substrate identity, derived attribute, and delta,
produces NEW identity in higher dimension.

No mutation. No patching. No state change.
"""

from ._identity import SubstrateIdentity
from ._delta import Delta

__all__ = ['promote']


def promote(x1: SubstrateIdentity, y1: int, delta: Delta) -> SubstrateIdentity:
    """
    Dimensional promotion: x₁ + y₁ + δ(z₁) → m₁
    
    This is the ONLY way change occurs in ButterflyFx.
    
    Args:
        x1: Substrate identity
        y1: Derived attribute value (from lens invocation)
        delta: Change encoding
    
    Returns:
        m₁: New identity in higher dimension
    
    Mathematical expression:
        m₁ = f(x₁, y₁, z₁)
        
    Where f is a deterministic transformation that:
    - Encodes the relationship between x₁, y₁, z₁
    - Produces unique m₁ for unique inputs
    - Is reversible with sufficient information
    """
    # Get raw values
    x1_val = x1.value
    y1_val = y1 & 0xFFFFFFFFFFFFFFFF
    z1_val = delta.z1
    
    # Promotion formula: combine all three components
    # Using rotation and XOR to preserve bit distribution
    
    # Step 1: Combine identity with attribute
    intermediate = x1_val ^ y1_val
    
    # Step 2: Rotate by attribute-derived amount for diffusion
    rotation = (y1_val % 64)
    rotated = ((intermediate << rotation) | (intermediate >> (64 - rotation))) & 0xFFFFFFFFFFFFFFFF
    
    # Step 3: Apply delta transformation
    m1_val = rotated ^ z1_val
    
    return SubstrateIdentity(m1_val)


def promote_chain(
    x1: SubstrateIdentity,
    y1_values: list,
    deltas: list
) -> SubstrateIdentity:
    """
    Chain multiple promotions.
    
    Each step: m₁ₙ = promote(m₁ₙ₋₁, y₁ₙ, δₙ)
    
    Useful for applying multiple changes in sequence.
    """
    current = x1
    
    for y1, delta in zip(y1_values, deltas):
        current = promote(current, y1, delta)
    
    return current
