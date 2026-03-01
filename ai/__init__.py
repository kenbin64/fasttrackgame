"""
ButterflyFX AI - Dimensional AI System

AI that remembers, doesn't hallucinate, and truly helps.
"""

from .memory_substrate import MemorySubstrate, MemoryPoint, DimensionalMemoryIndex
from .dimensional_ai import (
    DimensionalAI,
    AIConfig,
    IntentionVector,
    IntentionSubstrate,
    AIIngestionSubstrate
)

__all__ = [
    'MemorySubstrate',
    'MemoryPoint',
    'DimensionalMemoryIndex',
    'DimensionalAI',
    'AIConfig',
    'IntentionVector',
    'IntentionSubstrate',
    'AIIngestionSubstrate',
]

__version__ = '1.0.0'
