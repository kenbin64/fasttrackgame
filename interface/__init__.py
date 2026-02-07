"""
ButterflyFx Interface Layer - External Access Point

This layer provides DTOs and APIs for:
- Human access (natural language, declarative syntax)
- Machine access (binary protocols, structured data)
- AI access (instruction sets, embeddings)

RULES:
1. Interface ONLY talks to Core
2. Interface NEVER imports from Kernel
3. All operations compile to substrate math via Core
4. DTOs are transfer objects, NOT truth sources
"""

from .dto import (
    SubstrateDTO,
    LensDTO,
    ManifoldDTO,
    InvocationRequest,
    InvocationResponse,
    DeltaDTO,
    PromotionRequest,
)
from .human import HumanInterface
from .machine import MachineInterface
from .ai import AIInterface

__all__ = [
    # DTOs
    'SubstrateDTO',
    'LensDTO',
    'ManifoldDTO',
    'InvocationRequest',
    'InvocationResponse',
    'DeltaDTO',
    'PromotionRequest',
    # Interfaces
    'HumanInterface',
    'MachineInterface',
    'AIInterface',
]
