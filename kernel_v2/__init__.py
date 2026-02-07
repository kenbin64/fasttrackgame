"""
ButterflyFx Kernel - Pure Mathematical Substrate Operations

═══════════════════════════════════════════════════════════════════
                        INNER SANCTUM
═══════════════════════════════════════════════════════════════════

This module contains ONLY pure mathematical expressions.
No logic. No conditions. No state. No side effects.

ABSOLUTE RULES:
1. Kernel is IMMUTABLE - cannot be altered at runtime
2. Kernel can ONLY be accessed through Core
3. All values are 64-bit substrate math
4. No imports from Core or Interface layers
5. No I/O, logging, or external dependencies

MATHEMATICAL PRIMITIVES:
- SubstrateIdentity: 64-bit atomic identity (x₁)
- Substrate: Identity + Expression
- Lens: Projection function for attribute derivation
- Delta: Change encoding (z₁)
- Dimension: Containment level
- Manifold: Shape of substrate at dimensional intersection

OPERATIONS:
- promote(x₁, y₁, z₁) → m₁: The ONLY way change occurs
- invoke(substrate, lens) → value: Truth revelation

═══════════════════════════════════════════════════════════════════
"""

# Kernel exports - accessed ONLY through Core.KernelGateway
from ._identity import SubstrateIdentity
from ._substrate import Substrate
from ._lens import Lens
from ._delta import Delta
from ._dimension import Dimension
from ._manifold import Manifold
from ._promote import promote
from ._invoke import invoke
from ._srl import SRL, create_srl_identity

__all__ = [
    'SubstrateIdentity',
    'Substrate',
    'Lens',
    'Delta',
    'Dimension',
    'Manifold',
    'promote',
    'invoke',
    'SRL',
    'create_srl_identity',
]

# Protocol version for Core-Kernel communication
KERNEL_PROTOCOL_VERSION = 1
KERNEL_MATH_BITS = 64
