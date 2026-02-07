"""
Machine Interface - Binary protocol and structured data access to Core.

Machines interact with ButterflyFx through:
- Binary serialization (msgpack, protobuf, etc.)
- Structured data (JSON, BSON)
- Low-level numeric APIs

All machine operations compile down to Core operations,
which compile down to Kernel math.
"""

from __future__ import annotations
import struct
from typing import Any, Dict, List, Optional, Tuple

from .dto import (
    SubstrateDTO, 
    LensDTO, 
    InvocationRequest, 
    InvocationResponse,
    ManifoldDTO,
    DeltaDTO,
)

# Core imports - Interface ONLY talks to Core
from core import KernelGateway, Translator, Validator, Invocator


class MachineInterface:
    """
    Machine-optimized access to ButterflyFx.
    
    Designed for:
    - High-throughput binary protocols
    - Direct numeric operations
    - Batch processing
    """
    
    def __init__(self):
        self._gateway = KernelGateway()
        self._translator = Translator()
        self._validator = Validator()
        self._invocator = Invocator()
    
    # ═══════════════════════════════════════════════════════════════
    # BINARY SERIALIZATION
    # ═══════════════════════════════════════════════════════════════
    
    def serialize_identity(self, identity: int) -> bytes:
        """Serialize 64-bit identity to bytes (big-endian)"""
        self._validator.validate_64bit(identity, "identity")
        return struct.pack('>Q', identity)
    
    def deserialize_identity(self, data: bytes) -> int:
        """Deserialize bytes to 64-bit identity"""
        if len(data) != 8:
            raise ValueError("Identity must be exactly 8 bytes")
        return struct.unpack('>Q', data)[0]
    
    def serialize_substrate_dto(self, dto: SubstrateDTO) -> bytes:
        """Serialize SubstrateDTO to compact binary format"""
        # Format: identity (8) + expr_type_len (2) + expr_type + params_json
        import json
        
        identity_bytes = struct.pack('>Q', dto.identity)
        expr_type_bytes = dto.expression_type.encode('utf-8')
        expr_type_len = struct.pack('>H', len(expr_type_bytes))
        params_bytes = json.dumps(dto.expression_params).encode('utf-8')
        
        return identity_bytes + expr_type_len + expr_type_bytes + params_bytes
    
    def deserialize_substrate_dto(self, data: bytes) -> SubstrateDTO:
        """Deserialize binary to SubstrateDTO"""
        import json
        
        identity = struct.unpack('>Q', data[:8])[0]
        expr_type_len = struct.unpack('>H', data[8:10])[0]
        expr_type = data[10:10+expr_type_len].decode('utf-8')
        params = json.loads(data[10+expr_type_len:].decode('utf-8'))
        
        return SubstrateDTO(
            identity=identity,
            expression_type=expr_type,
            expression_params=params,
        )
    
    # ═══════════════════════════════════════════════════════════════
    # DIRECT NUMERIC OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def create_substrate_direct(
        self,
        identity: int,
        expression_type: str,
        expression_params: Dict[str, Any]
    ) -> SubstrateDTO:
        """Create substrate with direct numeric identity"""
        self._validator.validate_64bit(identity, "identity")
        
        return SubstrateDTO(
            identity=identity,
            expression_type=expression_type,
            expression_params=expression_params,
        )
    
    def create_lens_direct(
        self,
        lens_id: int,
        projection_type: str,
        projection_params: Dict[str, Any]
    ) -> LensDTO:
        """Create lens with direct numeric identity"""
        self._validator.validate_64bit(lens_id, "lens_id")
        
        return LensDTO(
            lens_id=lens_id,
            projection_type=projection_type,
            projection_params=projection_params,
        )
    
    # ═══════════════════════════════════════════════════════════════
    # BATCH OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def invoke_batch(
        self,
        requests: List[InvocationRequest]
    ) -> List[InvocationResponse]:
        """
        Batch invocation for high-throughput scenarios.
        
        Validates batch size to prevent brute-force violations.
        """
        self._validator.validate_no_brute_force("invoke_batch", len(requests))
        
        responses = []
        for req in requests:
            response = self._invoke_single(req.substrate, req.lens)
            responses.append(response)
        
        return responses
    
    def _invoke_single(
        self,
        substrate: SubstrateDTO,
        lens: LensDTO
    ) -> InvocationResponse:
        """Internal single invocation"""
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
        
        return InvocationResponse(
            value=result.value,
            substrate_id=result.substrate_id,
            lens_id=result.lens_id,
        )
    
    # ═══════════════════════════════════════════════════════════════
    # MANIFOLD OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def create_manifold(
        self,
        substrate: SubstrateDTO,
        dimension: int,
        form_expression: int
    ) -> ManifoldDTO:
        """Create manifold - dimensional expression of substrate"""
        self._validator.validate_64bit(form_expression, "form_expression")
        
        return ManifoldDTO(
            substrate_id=substrate.identity,
            dimension=dimension,
            form_expression=form_expression,
        )
