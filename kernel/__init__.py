"""
ButterflyFx Kernel - The Inner Sanctum

This module contains ONLY pure mathematical expressions.
No logic, no conditions, no state, no side effects.

RULES:
1. The Kernel is IMMUTABLE - it cannot be altered at runtime
2. The Kernel can ONLY be accessed through the Core
3. All expressions are substrate math - 64-bit identity transformations
4. No imports from Core or Interface layers permitted
5. No I/O, no logging, no external dependencies
"""

from .substrate import Substrate, SubstrateIdentity
from .manifold import Manifold
from .lens import Lens
from .delta import Delta
from .dimensional import Dimension, promote
from .srl import SRL, create_srl_identity

__all__ = [
    'Substrate',
    'SubstrateIdentity', 
    'Manifold',
    'Lens',
    'Delta',
    'Dimension',
    'promote',
    'SRL',
    'create_srl_identity',
]
