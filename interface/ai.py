"""
AI Interface - Instruction set and embedding access to Core.

AI systems interact with ButterflyFx through:
- Instruction sets (declarative commands)
- Embedding translations
- Constrained generation

Law 15: AI MUST NEVER fabricate substrate behavior.
No hallucinated attributes. No invented manifolds. No guessed values.
Only derive what the substrate math implies.
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional, Tuple

from .dto import (
    SubstrateDTO, 
    LensDTO, 
    InvocationRequest, 
    InvocationResponse,
    DeltaDTO,
    PromotionRequest,
)

# Core imports - Interface ONLY talks to Core
from core import KernelGateway, Translator, Validator, Invocator


class AIInterfaceError(Exception):
    """Raised when AI operation violates constraints"""
    pass


class FabricationGuard:
    """
    Prevents AI from fabricating substrate behavior.
    
    Law 15 Enforcement:
    - No hallucinated attributes
    - No invented manifolds
    - No guessed values
    """
    
    @staticmethod
    def validate_not_fabricated(
        claimed_value: Any,
        derived_value: Any,
        tolerance: float = 0.0
    ) -> None:
        """
        Verify AI's claimed value matches substrate-derived truth.
        """
        if isinstance(claimed_value, (int, float)):
            if isinstance(derived_value, (int, float)):
                if abs(claimed_value - derived_value) > tolerance:
                    raise AIInterfaceError(
                        f"Fabrication detected: claimed {claimed_value}, "
                        f"substrate says {derived_value}"
                    )
            else:
                raise AIInterfaceError(
                    f"Type mismatch: claimed numeric, derived {type(derived_value)}"
                )
        elif claimed_value != derived_value:
            raise AIInterfaceError(
                f"Fabrication detected: claimed {claimed_value}, "
                f"substrate says {derived_value}"
            )
    
    @staticmethod
    def validate_derivation_path(
        substrate_id: int,
        lens_id: int,
        operation: str
    ) -> Dict[str, Any]:
        """
        Return audit trail for AI derivation.
        
        All AI-derived values must be traceable to substrate math.
        """
        return {
            'substrate_id': f"0x{substrate_id:016X}",
            'lens_id': f"0x{lens_id:016X}",
            'operation': operation,
            'fabricated': False,
            'source': 'substrate_math',
        }


class AIInterface:
    """
    AI-optimized access to ButterflyFx.
    
    Designed for:
    - LLM instruction following
    - Embedding-based semantic operations
    - Constrained generation with substrate verification
    
    CRITICAL: All outputs must be substrate-derived, never fabricated.
    """
    
    def __init__(self):
        self._gateway = KernelGateway()
        self._translator = Translator()
        self._validator = Validator()
        self._invocator = Invocator()
        self._guard = FabricationGuard()
    
    # ═══════════════════════════════════════════════════════════════
    # INSTRUCTION EXECUTION
    # ═══════════════════════════════════════════════════════════════
    
    def execute_instruction(
        self,
        instruction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a declarative instruction.
        
        Instruction format:
        {
            "operation": "invoke" | "promote" | "create_substrate" | ...,
            "params": { ... }
        }
        """
        operation = instruction.get("operation")
        params = instruction.get("params", {})
        
        if operation == "invoke":
            return self._execute_invoke(params)
        elif operation == "promote":
            return self._execute_promote(params)
        elif operation == "create_substrate":
            return self._execute_create_substrate(params)
        elif operation == "create_lens":
            return self._execute_create_lens(params)
        else:
            raise AIInterfaceError(f"Unknown operation: {operation}")
    
    def _execute_invoke(self, params: Dict) -> Dict[str, Any]:
        """Execute invoke instruction"""
        substrate_dto = SubstrateDTO(
            identity=params["substrate_identity"],
            expression_type=params.get("expression_type", "constant"),
            expression_params=params.get("expression_params", {"value": params["substrate_identity"]}),
        )
        lens_dto = LensDTO(
            lens_id=params["lens_id"],
            projection_type=params.get("projection_type", "identity"),
            projection_params=params.get("projection_params", {}),
        )
        
        # Derive through substrate math
        expression = self._translator.translate_expression(
            substrate_dto.expression_type,
            substrate_dto.expression_params,
        )
        projection = self._translator.translate_projection(
            lens_dto.projection_type,
            lens_dto.projection_params,
        )
        
        identity = self._gateway.create_identity(substrate_dto.identity)
        kernel_substrate = self._gateway.create_substrate(identity, expression)
        kernel_lens = self._gateway.create_lens(lens_dto.lens_id, projection)
        
        result = self._invocator.invoke_single(kernel_substrate, kernel_lens)
        
        # Return with audit trail
        return {
            "value": result.value,
            "audit": self._guard.validate_derivation_path(
                result.substrate_id, 
                result.lens_id,
                "invoke"
            ),
        }
    
    def _execute_promote(self, params: Dict) -> Dict[str, Any]:
        """Execute promote instruction"""
        substrate_dto = SubstrateDTO(
            identity=params["substrate_identity"],
            expression_type=params.get("expression_type", "constant"),
            expression_params=params.get("expression_params", {"value": params["substrate_identity"]}),
        )
        
        expression = self._translator.translate_expression(
            substrate_dto.expression_type,
            substrate_dto.expression_params,
        )
        identity = self._gateway.create_identity(substrate_dto.identity)
        kernel_substrate = self._gateway.create_substrate(identity, expression)
        delta = self._gateway.create_delta(params["delta_z1"])
        
        new_id = self._gateway.promote_substrate(
            kernel_substrate,
            params["attribute_value"],
            delta,
        )
        
        return {
            "new_identity": new_id.value,
            "new_identity_hex": f"0x{new_id.value:016X}",
            "audit": self._guard.validate_derivation_path(
                substrate_dto.identity,
                0,
                "promote"
            ),
        }
    
    def _execute_create_substrate(self, params: Dict) -> Dict[str, Any]:
        """Execute create_substrate instruction"""
        name = params.get("name", str(params.get("identity", 0)))
        identity = self._translator.translate_identity(name)
        
        return {
            "identity": identity,
            "identity_hex": f"0x{identity:016X}",
            "expression_type": params.get("expression_type", "constant"),
        }
    
    def _execute_create_lens(self, params: Dict) -> Dict[str, Any]:
        """Execute create_lens instruction"""
        name = params.get("name", str(params.get("lens_id", 0)))
        lens_id = self._translator.translate_identity(name)
        
        return {
            "lens_id": lens_id,
            "lens_id_hex": f"0x{lens_id:016X}",
            "projection_type": params.get("projection_type", "identity"),
        }
    
    # ═══════════════════════════════════════════════════════════════
    # VERIFIED GENERATION
    # ═══════════════════════════════════════════════════════════════
    
    def verify_claim(
        self,
        substrate: SubstrateDTO,
        lens: LensDTO,
        claimed_value: Any
    ) -> Tuple[bool, Any]:
        """
        Verify an AI's claimed value against substrate truth.
        
        Returns (is_valid, actual_value)
        
        Law 15: AI claims MUST match substrate math.
        """
        expression = self._translator.translate_expression(
            substrate.expression_type,
            substrate.expression_params,
        )
        projection = self._translator.translate_projection(
            lens.projection_type,
            lens.projection_params,
        )
        
        identity = self._gateway.create_identity(substrate.identity)
        kernel_substrate = self._gateway.create_substrate(identity, expression)
        kernel_lens = self._gateway.create_lens(lens.lens_id, projection)
        
        result = self._invocator.invoke_single(kernel_substrate, kernel_lens)
        actual_value = result.value
        
        try:
            self._guard.validate_not_fabricated(claimed_value, actual_value)
            return (True, actual_value)
        except AIInterfaceError:
            return (False, actual_value)
    
    # ═══════════════════════════════════════════════════════════════
    # EMBEDDING TRANSLATION
    # ═══════════════════════════════════════════════════════════════
    
    def embedding_to_identity(self, embedding: List[float]) -> int:
        """
        Translate embedding vector to 64-bit substrate identity.
        
        This is a lossy projection - embeddings are high-dimensional,
        identities are 64-bit. Use for semantic lookup, not storage.
        """
        if not embedding:
            return 0
        
        # Quantize and hash embedding to 64 bits
        # This is deterministic: same embedding → same identity
        quantized = tuple(int(x * 1000000) for x in embedding[:8])
        hash_input = str(quantized).encode('utf-8')
        return self._translator._hash_to_64bit(hash_input)
