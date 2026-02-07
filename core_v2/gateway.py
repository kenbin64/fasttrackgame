"""
Gateway - The sole point of access to the Kernel.

This is the inner sanctum guard. ALL access to Kernel
primitives MUST flow through this gateway.

The gateway:
1. Validates access permissions  
2. Ensures all operations are substrate-compliant
3. Returns only what the Kernel math reveals
4. NEVER exposes Kernel internals for modification
"""

from __future__ import annotations
from typing import Callable, Optional, Any
import threading

# ═══════════════════════════════════════════════════════════════
# KERNEL IMPORTS - Core is the ONLY layer allowed to do this
# ═══════════════════════════════════════════════════════════════
from kernel_v2 import (
    SubstrateIdentity,
    Substrate,
    Lens,
    Delta,
    Dimension,
    Manifold,
    promote,
    invoke,
    SRL,
    create_srl_identity,
)

__all__ = ['Gateway']


class Gateway:
    """
    The sole gateway to the Kernel layer.
    
    External code (human, machine, AI) accesses the Kernel
    ONLY through Core, and Core accesses ONLY through this gateway.
    
    This is a singleton - one gateway to the inner sanctum.
    """
    
    _instance: Optional[Gateway] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> Gateway:
        """Singleton pattern - one gateway only."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
    
    # ═══════════════════════════════════════════════════════════════
    # IDENTITY OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def create_identity(self, value: int) -> SubstrateIdentity:
        """
        Create a 64-bit substrate identity.
        
        Args:
            value: Integer value (will be masked to 64 bits)
        
        Returns:
            SubstrateIdentity
        """
        return SubstrateIdentity(value)
    
    def identity_from_bytes(self, data: bytes) -> SubstrateIdentity:
        """
        Create identity from bytes using deterministic hash.
        
        Args:
            data: Arbitrary bytes
        
        Returns:
            SubstrateIdentity (64-bit hash of data)
        """
        return create_srl_identity("hash", str(data), 0)
    
    # ═══════════════════════════════════════════════════════════════
    # SUBSTRATE OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def create_substrate(
        self,
        identity: SubstrateIdentity,
        expression: Callable[[], int]
    ) -> Substrate:
        """
        Create a substrate with its mathematical expression.
        
        Args:
            identity: The 64-bit identity (x₁)
            expression: Function that computes substrate value
        
        Returns:
            Substrate
        """
        return Substrate(identity, expression)
    
    def evaluate_substrate(self, substrate: Substrate) -> int:
        """
        Evaluate a substrate's expression.
        
        Args:
            substrate: The substrate to evaluate
        
        Returns:
            64-bit evaluation result
        """
        return substrate.evaluate()
    
    # ═══════════════════════════════════════════════════════════════
    # LENS OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def create_lens(
        self,
        lens_id: int,
        projection: Callable[[int], int]
    ) -> Lens:
        """
        Create a lens for attribute derivation.
        
        Args:
            lens_id: 64-bit lens identity
            projection: Function (substrate_value → attribute)
        
        Returns:
            Lens
        """
        return Lens(lens_id, projection)
    
    # ═══════════════════════════════════════════════════════════════
    # INVOCATION - Truth Revelation
    # ═══════════════════════════════════════════════════════════════
    
    def invoke(self, substrate: Substrate, lens: Lens) -> int:
        """
        Invoke substrate through lens to reveal truth.
        
        This is the fundamental computation:
            substrate → lens → invocation → truth
        
        Args:
            substrate: The substrate to query
            lens: The projection lens
        
        Returns:
            Derived 64-bit attribute value (y₁)
        """
        return invoke(substrate, lens)
    
    # ═══════════════════════════════════════════════════════════════
    # DELTA OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def create_delta(self, z1: int) -> Delta:
        """
        Create a delta for change representation.
        
        Args:
            z1: 64-bit delta identity
        
        Returns:
            Delta
        """
        return Delta(z1)
    
    # ═══════════════════════════════════════════════════════════════
    # DIMENSIONAL PROMOTION - The Mechanism of Change
    # ═══════════════════════════════════════════════════════════════
    
    def promote(
        self,
        x1: SubstrateIdentity,
        y1: int,
        delta: Delta
    ) -> SubstrateIdentity:
        """
        Promote identity through delta.
        
        x₁ + y₁ + δ(z₁) → m₁
        
        This is the ONLY way change occurs.
        Returns a NEW identity - original is untouched.
        
        Args:
            x1: Substrate identity
            y1: Derived attribute value
            delta: Change encoding
        
        Returns:
            New SubstrateIdentity (m₁)
        """
        return promote(x1, y1, delta)
    
    # ═══════════════════════════════════════════════════════════════
    # DIMENSION OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def get_dimension(self, level: int) -> Dimension:
        """
        Get a dimension by level.
        
        Args:
            level: Non-negative dimensional level
        
        Returns:
            Dimension
        """
        return Dimension(level)
    
    # ═══════════════════════════════════════════════════════════════
    # MANIFOLD OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def create_manifold(
        self,
        substrate_id: SubstrateIdentity,
        dimension: Dimension,
        form: int
    ) -> Manifold:
        """
        Create a manifold - shape of substrate at dimension.
        
        Args:
            substrate_id: Source substrate identity
            dimension: Dimensional level
            form: 64-bit form expression
        
        Returns:
            Manifold
        """
        return Manifold(substrate_id, dimension, form)
    
    # ═══════════════════════════════════════════════════════════════
    # SRL OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def create_srl(
        self,
        domain: str,
        path: str,
        identity: SubstrateIdentity
    ) -> SRL:
        """
        Create a Substrate Reference Locator.
        
        Args:
            domain: Domain component
            path: Path component
            identity: Substrate identity
        
        Returns:
            SRL
        """
        return SRL(domain, path, identity)
    
    def parse_srl(self, uri: str) -> SRL:
        """
        Parse SRL URI string.
        
        Args:
            uri: SRL URI (e.g., "srl://domain/path#identity")
        
        Returns:
            SRL
        """
        return SRL.from_uri(uri)
