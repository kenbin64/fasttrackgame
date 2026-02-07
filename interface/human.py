"""
Human Interface - Natural language and declarative access to Core.

Humans interact with ButterflyFx through:
- Declarative syntax
- Natural language queries (compiled to substrate math)
- High-level convenience APIs

All human intents compile down to Core operations,
which compile down to Kernel math.
"""

from __future__ import annotations
from typing import Any, Dict, Optional

from .dto import (
    SubstrateDTO, 
    LensDTO, 
    InvocationRequest, 
    InvocationResponse,
    PromotionRequest,
    DeltaDTO,
)

# Core imports - Interface ONLY talks to Core
from core import KernelGateway, Translator, Validator, Invocator


class HumanInterface:
    """
    Human-friendly access to ButterflyFx.
    
    Provides convenience APIs that compile to substrate math.
    Law 11: Human-readable code is allowed, but MUST
    compile down to substrate math.
    """
    
    def __init__(self):
        self._gateway = KernelGateway()
        self._translator = Translator()
        self._validator = Validator()
        self._invocator = Invocator()
    
    # ═══════════════════════════════════════════════════════════════
    # SUBSTRATE CREATION (Human-friendly)
    # ═══════════════════════════════════════════════════════════════
    
    def create_substrate(
        self,
        name: str,
        expression_type: str = "constant",
        **params
    ) -> SubstrateDTO:
        """
        Create a substrate from human-friendly parameters.
        
        Args:
            name: Human-readable identifier (hashed to 64-bit identity)
            expression_type: Type of mathematical expression
            **params: Expression parameters
        
        Returns:
            SubstrateDTO for further operations
        """
        # Translate human-readable name to 64-bit identity
        identity = self._translator.translate_identity(name)
        
        # Validate
        self._validator.validate_64bit(identity, "identity")
        
        return SubstrateDTO(
            identity=identity,
            expression_type=expression_type,
            expression_params=params,
        )
    
    # ═══════════════════════════════════════════════════════════════
    # LENS CREATION (Human-friendly)
    # ═══════════════════════════════════════════════════════════════
    
    def create_lens(
        self,
        name: str,
        projection_type: str = "identity",
        **params
    ) -> LensDTO:
        """
        Create a lens from human-friendly parameters.
        
        Args:
            name: Human-readable lens name
            projection_type: Type of projection
            **params: Projection parameters
        """
        lens_id = self._translator.translate_identity(name)
        self._validator.validate_64bit(lens_id, "lens_id")
        
        return LensDTO(
            lens_id=lens_id,
            projection_type=projection_type,
            projection_params=params,
        )
    
    # ═══════════════════════════════════════════════════════════════
    # INVOCATION (Human-friendly)
    # ═══════════════════════════════════════════════════════════════
    
    def invoke(
        self,
        substrate: SubstrateDTO,
        lens: LensDTO
    ) -> InvocationResponse:
        """
        Invoke substrate through lens to reveal attribute.
        
        This is the primary computation pattern:
            substrate → lens → invocation → truth
        """
        # Translate DTO to Kernel primitives via Core
        expression = self._translator.translate_expression(
            substrate.expression_type,
            substrate.expression_params,
        )
        self._validator.validate_expression(expression)
        
        projection = self._translator.translate_projection(
            lens.projection_type,
            lens.projection_params,
        )
        self._validator.validate_projection(projection)
        
        # Create Kernel objects through gateway
        identity = self._gateway.create_identity(substrate.identity)
        kernel_substrate = self._gateway.create_substrate(identity, expression)
        kernel_lens = self._gateway.create_lens(lens.lens_id, projection)
        
        # Invoke
        result = self._invocator.invoke_single(kernel_substrate, kernel_lens)
        
        return InvocationResponse(
            value=result.value,
            substrate_id=result.substrate_id,
            lens_id=result.lens_id,
        )
    
    # ═══════════════════════════════════════════════════════════════
    # CHANGE / PROMOTION (Human-friendly)
    # ═══════════════════════════════════════════════════════════════
    
    def promote(
        self,
        substrate: SubstrateDTO,
        attribute_value: int,
        change_description: str
    ) -> int:
        """
        Promote substrate to new identity through change.
        
        Change is represented as delta, not mutation.
        x₁ + y₁ + δ(z₁) → m₁
        
        Args:
            substrate: The substrate to promote
            attribute_value: Current attribute value (y₁)
            change_description: Human description of change (hashed to z₁)
        
        Returns:
            New substrate identity (m₁)
        """
        self._validator.validate_64bit(attribute_value, "attribute_value")
        
        # Translate human change description to delta
        z1 = self._translator.translate_identity(change_description)
        
        # Create Kernel objects
        expression = self._translator.translate_expression(
            substrate.expression_type,
            substrate.expression_params,
        )
        identity = self._gateway.create_identity(substrate.identity)
        kernel_substrate = self._gateway.create_substrate(identity, expression)
        delta = self._gateway.create_delta(z1)
        
        # Promote
        new_identity = self._gateway.promote_substrate(
            kernel_substrate, 
            attribute_value, 
            delta
        )
        
        return new_identity.value
    
    # ═══════════════════════════════════════════════════════════════
    # CONVENIENCE: Age calculation (Law 6 compliant)
    # ═══════════════════════════════════════════════════════════════
    
    def calculate_age(
        self,
        birth_timestamp_ms: int,
        current_timestamp_ms: Optional[int] = None
    ) -> int:
        """
        Calculate age as mathematical expression.
        
        Law 6: age = now() - birth_timestamp
        No snapshots, no cached values.
        """
        if current_timestamp_ms is None:
            import time
            current_timestamp_ms = int(time.time() * 1000)
        
        # This is math, not a stored value
        return current_timestamp_ms - birth_timestamp_ms
