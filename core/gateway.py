"""
KernelGateway - The sole point of access to the Kernel.

This is the inner sanctum guard. All access to Kernel
primitives MUST flow through this gateway.

The gateway:
1. Validates access permissions
2. Ensures all operations are substrate-compliant
3. Returns only what the Kernel math reveals
4. NEVER exposes Kernel internals for modification
"""

from __future__ import annotations
from typing import Callable, Optional

# Kernel imports - Core is the ONLY layer allowed to do this
from kernel.substrate import Substrate, SubstrateIdentity
from kernel.manifold import Manifold
from kernel.lens import Lens
from kernel.delta import Delta
from kernel.dimensional import Dimension, promote


class KernelGateway:
    """
    The sole gateway to the Kernel layer.
    
    External code (human, machine, AI) accesses the Kernel
    ONLY through Core, and Core accesses ONLY through this gateway.
    """
    
    _instance: Optional[KernelGateway] = None
    
    def __new__(cls) -> KernelGateway:
        # Singleton - one gateway to the inner sanctum
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    # ═══════════════════════════════════════════════════════════════
    # SUBSTRATE OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def create_identity(self, value: int) -> SubstrateIdentity:
        """Create a 64-bit substrate identity"""
        return SubstrateIdentity(value)
    
    def create_substrate(
        self, 
        identity: SubstrateIdentity,
        expression: Callable[[], int]
    ) -> Substrate:
        """Create a substrate with its mathematical expression"""
        return Substrate(identity, expression)
    
    # ═══════════════════════════════════════════════════════════════
    # LENS OPERATIONS  
    # ═══════════════════════════════════════════════════════════════
    
    def create_lens(
        self,
        lens_id: int,
        projection: Callable[[int], int]
    ) -> Lens:
        """Create a lens for attribute derivation"""
        return Lens(lens_id, projection)
    
    # ═══════════════════════════════════════════════════════════════
    # INVOCATION - Truth Revelation
    # ═══════════════════════════════════════════════════════════════
    
    def invoke(self, substrate: Substrate, lens: Lens) -> int:
        """
        Invoke substrate through lens to reveal truth.
        
        Computation = substrate → lens → invocation
        Nothing is precomputed or stored.
        """
        # Get the substrate's expression result
        substrate_value = substrate.expression()
        
        # Apply lens projection to derive attribute
        return lens.projection(substrate_value)
    
    # ═══════════════════════════════════════════════════════════════
    # MANIFOLD OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def create_manifold(
        self,
        substrate: Substrate,
        dimension: int,
        form_expression: int
    ) -> Manifold:
        """Create a manifold - dimensional expression of substrate"""
        return Manifold(substrate.identity, dimension, form_expression)
    
    # ═══════════════════════════════════════════════════════════════
    # DIMENSIONAL PROMOTION - The Mechanism of Change
    # ═══════════════════════════════════════════════════════════════
    
    def create_delta(self, z1: int) -> Delta:
        """Create a delta for change representation"""
        return Delta(z1)
    
    def promote_substrate(
        self,
        substrate: Substrate,
        attribute_value: int,
        delta: Delta
    ) -> SubstrateIdentity:
        """
        Promote substrate to new identity through delta.
        
        x₁ + y₁ + δ(z₁) → m₁
        
        This is the ONLY way change occurs.
        Returns a NEW identity - original is untouched.
        """
        return promote(substrate.identity, attribute_value, delta)
    
    def get_dimension(self, level: int) -> Dimension:
        """Get a dimension by level"""
        return Dimension(level)
