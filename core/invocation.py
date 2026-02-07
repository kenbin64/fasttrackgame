"""
Invocator - Executes substrate → lens → truth pipeline.

The Invocator handles the computation pattern:
    substrate → lens → invocation → truth

This is where attributes are DERIVED, never stored.
"""

from __future__ import annotations
from typing import Any, Dict, List
from .gateway import KernelGateway


class InvocationResult:
    """Immutable result of an invocation"""
    __slots__ = ('_value', '_substrate_id', '_lens_id')
    
    def __init__(self, value: int, substrate_id: int, lens_id: int):
        object.__setattr__(self, '_value', value)
        object.__setattr__(self, '_substrate_id', substrate_id)
        object.__setattr__(self, '_lens_id', lens_id)
    
    def __setattr__(self, name, value):
        raise TypeError("InvocationResult is immutable")
    
    @property
    def value(self) -> int:
        return self._value
    
    @property
    def substrate_id(self) -> int:
        return self._substrate_id
    
    @property
    def lens_id(self) -> int:
        return self._lens_id
    
    def __repr__(self) -> str:
        return f"InvocationResult(value={self._value})"


class Invocator:
    """
    Executes invocations through the Kernel gateway.
    
    All attribute access flows through here:
    1. Accept substrate reference
    2. Accept lens specification
    3. Invoke through gateway
    4. Return derived truth
    """
    
    def __init__(self):
        self._gateway = KernelGateway()
    
    def invoke_single(
        self,
        substrate,  # Substrate from gateway
        lens        # Lens from gateway
    ) -> InvocationResult:
        """
        Single invocation: substrate → lens → truth
        """
        value = self._gateway.invoke(substrate, lens)
        return InvocationResult(
            value=value,
            substrate_id=substrate.identity.value,
            lens_id=lens.lens_id
        )
    
    def invoke_batch(
        self,
        substrate,
        lenses: List
    ) -> List[InvocationResult]:
        """
        Batch invocation: substrate → [lens₁, lens₂, ...] → [truth₁, truth₂, ...]
        
        Multiple lens views of the same substrate.
        """
        results = []
        for lens in lenses:
            result = self.invoke_single(substrate, lens)
            results.append(result)
        return results
