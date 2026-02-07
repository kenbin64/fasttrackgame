"""
SRL - Substrate Resource Locator

An SRL is a substrate that encodes connection rules.
It retrieves external data LAZILY and spawns new substrates.

RULES (Law 4):
- No raw URLs, credentials, or connection strings in code
- SRL is the ONLY way to reference external resources
- SRL is itself a substrate (64-bit identity)
- Actual connection details are resolved through lenses
"""

from __future__ import annotations
from typing import Callable, Optional

from .substrate import Substrate, SubstrateIdentity


class SRL:
    """
    Substrate Resource Locator.
    
    A substrate that encodes connection rules for external data.
    Connection details are NEVER exposed - only the mathematical
    identity is visible.
    """
    __slots__ = ('_srl_id', '_resource_expression', '_spawn_rule')
    
    def __init__(
        self,
        srl_id: SubstrateIdentity,
        resource_expression: Callable[[], int],
        spawn_rule: Callable[[int], SubstrateIdentity]
    ):
        """
        srl_id: The 64-bit identity of this SRL
        resource_expression: Math expression encoding the resource
        spawn_rule: Function to spawn new substrate from retrieved data
        """
        object.__setattr__(self, '_srl_id', srl_id)
        object.__setattr__(self, '_resource_expression', resource_expression)
        object.__setattr__(self, '_spawn_rule', spawn_rule)
    
    def __setattr__(self, name, value):
        raise TypeError("SRL is immutable")
    
    def __delattr__(self, name):
        raise TypeError("SRL is immutable")
    
    @property
    def identity(self) -> SubstrateIdentity:
        return self._srl_id
    
    @property
    def resource_expression(self) -> Callable[[], int]:
        return self._resource_expression
    
    def spawn(self, external_data: int) -> SubstrateIdentity:
        """
        Spawn a new substrate identity from external data.
        
        The external data is incorporated into the mathematical
        identity, not stored as a value.
        """
        return self._spawn_rule(external_data)
    
    def __repr__(self) -> str:
        return f"SRL({self._srl_id})"


def create_srl_identity(
    resource_type: int,
    resource_namespace: int,
    resource_path: int
) -> int:
    """
    Create a deterministic SRL identity from components.
    
    All components are mathematical - no strings, no URLs.
    The identity encodes the connection rule, not the data.
    """
    # Pack components into 64-bit identity
    # High 16 bits: resource type
    # Middle 24 bits: namespace  
    # Low 24 bits: path
    
    type_part = (resource_type & 0xFFFF) << 48
    namespace_part = (resource_namespace & 0xFFFFFF) << 24
    path_part = resource_path & 0xFFFFFF
    
    return type_part | namespace_part | path_part
