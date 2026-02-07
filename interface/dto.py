"""
Data Transfer Objects - External representations for Interface layer.

DTOs are NOT truth sources. They are transfer containers
that compile down to substrate math through the Core.

DTOs exist for serialization/deserialization of external formats.
They NEVER bypass the Core to access the Kernel.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class SubstrateDTO:
    """
    External representation of a substrate.
    
    This is NOT the substrate - it's a specification
    that the Core will translate into Kernel math.
    """
    identity: int
    expression_type: str
    expression_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'identity': self.identity,
            'expression_type': self.expression_type,
            'expression_params': self.expression_params,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> SubstrateDTO:
        return cls(
            identity=data['identity'],
            expression_type=data['expression_type'],
            expression_params=data.get('expression_params', {}),
        )


@dataclass(frozen=True)
class LensDTO:
    """
    External representation of a lens.
    
    Defines projection specification for Core translation.
    """
    lens_id: int
    projection_type: str
    projection_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'lens_id': self.lens_id,
            'projection_type': self.projection_type,
            'projection_params': self.projection_params,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> LensDTO:
        return cls(
            lens_id=data['lens_id'],
            projection_type=data['projection_type'],
            projection_params=data.get('projection_params', {}),
        )


@dataclass(frozen=True)
class ManifoldDTO:
    """
    External representation of a manifold.
    """
    substrate_id: int
    dimension: int
    form_expression: int
    
    def to_dict(self) -> Dict:
        return {
            'substrate_id': self.substrate_id,
            'dimension': self.dimension,
            'form_expression': self.form_expression,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> ManifoldDTO:
        return cls(
            substrate_id=data['substrate_id'],
            dimension=data['dimension'],
            form_expression=data['form_expression'],
        )


@dataclass(frozen=True)
class InvocationRequest:
    """
    Request for substrate invocation through lens.
    
    substrate → lens → invocation
    """
    substrate: SubstrateDTO
    lens: LensDTO
    
    def to_dict(self) -> Dict:
        return {
            'substrate': self.substrate.to_dict(),
            'lens': self.lens.to_dict(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> InvocationRequest:
        return cls(
            substrate=SubstrateDTO.from_dict(data['substrate']),
            lens=LensDTO.from_dict(data['lens']),
        )


@dataclass(frozen=True)
class InvocationResponse:
    """
    Response from invocation - the revealed truth.
    """
    value: int
    substrate_id: int
    lens_id: int
    
    def to_dict(self) -> Dict:
        return {
            'value': self.value,
            'substrate_id': self.substrate_id,
            'lens_id': self.lens_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> InvocationResponse:
        return cls(
            value=data['value'],
            substrate_id=data['substrate_id'],
            lens_id=data['lens_id'],
        )


@dataclass(frozen=True)
class DeltaDTO:
    """
    External representation of a delta (change).
    """
    z1: int
    
    def to_dict(self) -> Dict:
        return {'z1': self.z1}
    
    @classmethod
    def from_dict(cls, data: Dict) -> DeltaDTO:
        return cls(z1=data['z1'])


@dataclass(frozen=True)
class PromotionRequest:
    """
    Request for dimensional promotion.
    
    x₁ + y₁ + δ(z₁) → m₁
    """
    substrate: SubstrateDTO
    attribute_value: int
    delta: DeltaDTO
    
    def to_dict(self) -> Dict:
        return {
            'substrate': self.substrate.to_dict(),
            'attribute_value': self.attribute_value,
            'delta': self.delta.to_dict(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> PromotionRequest:
        return cls(
            substrate=SubstrateDTO.from_dict(data['substrate']),
            attribute_value=data['attribute_value'],
            delta=DeltaDTO.from_dict(data['delta']),
        )
