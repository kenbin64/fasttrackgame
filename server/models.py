"""
Server Models - Pydantic models for API requests/responses
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


# ============================================================================
# SUBSTRATE MODELS
# ============================================================================

class CreateSubstrateRequest(BaseModel):
    """Request to create a new substrate."""
    expression_type: str = Field(..., description="Type of expression: 'lambda', 'constant', 'function'")
    expression_code: str = Field(..., description="Python code for the expression")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "expression_type": "lambda",
                "expression_code": "lambda **kw: kw.get('x', 0) * kw.get('y', 0)",
                "metadata": {
                    "name": "multiply_substrate",
                    "description": "Multiplies x and y"
                }
            }
        }


class SubstrateResponse(BaseModel):
    """Response containing substrate information."""
    substrate_id: str = Field(..., description="Hex-encoded 64-bit substrate identity")
    identity: int = Field(..., description="Numeric substrate identity")
    created_at: datetime = Field(..., description="Creation timestamp")
    expression_type: str = Field(..., description="Type of expression")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Substrate metadata")


class InvokeSubstrateRequest(BaseModel):
    """Request to invoke a substrate expression."""
    parameters: Dict[str, Any] = Field(..., description="Parameters to pass to expression")
    
    class Config:
        json_schema_extra = {
            "example": {
                "parameters": {
                    "x": 5,
                    "y": 7
                }
            }
        }


class InvokeSubstrateResponse(BaseModel):
    """Response from substrate invocation."""
    substrate_id: str = Field(..., description="Substrate identity")
    result: Any = Field(..., description="Result of expression invocation")
    invocation_time_ms: float = Field(..., description="Time taken in milliseconds")


class DimensionInfo(BaseModel):
    """Information about a single dimension."""
    level: int = Field(..., description="Fibonacci level")
    name: str = Field(..., description="Dimension name")
    description: str = Field(..., description="Dimension description")


class DivideSubstrateResponse(BaseModel):
    """Response from dividing a substrate."""
    substrate_id: str = Field(..., description="Substrate identity")
    dimensions: List[DimensionInfo] = Field(..., description="9 Fibonacci dimensions")
    fibonacci_sequence: List[int] = Field(..., description="Fibonacci sequence")


# ============================================================================
# RELATIONSHIP MODELS
# ============================================================================

class CreateRelationshipRequest(BaseModel):
    """Request to create a relationship."""
    rel_type: str = Field(..., description="Relationship type")
    source_id: str = Field(..., description="Source substrate identity (hex)")
    target_id: str = Field(..., description="Target substrate identity (hex)")
    bidirectional: bool = Field(default=False, description="Whether relationship is bidirectional")
    constraints: Optional[Dict[str, Any]] = Field(default=None, description="Relationship constraints")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rel_type": "DEPENDENCY",
                "source_id": "0x1A2B3C4D5E6F7890",
                "target_id": "0x9876543210FEDCBA",
                "bidirectional": False
            }
        }


class RelationshipResponse(BaseModel):
    """Response containing relationship information."""
    relationship_id: str = Field(..., description="Relationship identity (hex)")
    rel_type: str = Field(..., description="Relationship type")
    source_id: str = Field(..., description="Source substrate identity")
    target_id: str = Field(..., description="Target substrate identity")
    bidirectional: bool = Field(..., description="Whether bidirectional")
    created_at: datetime = Field(..., description="Creation timestamp")


class RelationshipListResponse(BaseModel):
    """Response containing list of relationships."""
    relationships: List[RelationshipResponse] = Field(..., description="List of relationships")
    count: int = Field(..., description="Total count")


# ============================================================================
# QUERY MODELS
# ============================================================================

class TraverseGraphRequest(BaseModel):
    """Request to traverse relationship graph."""
    start_id: str = Field(..., description="Starting substrate identity (hex)")
    max_depth: int = Field(default=3, description="Maximum traversal depth")
    rel_types: Optional[List[str]] = Field(default=None, description="Filter by relationship types")


class SystemStatsResponse(BaseModel):
    """System statistics."""
    total_substrates: int = Field(..., description="Total substrates in registry")
    total_relationships: int = Field(..., description="Total relationships")
    uptime_seconds: float = Field(..., description="Server uptime in seconds")
    version: str = Field(..., description="Server version")


# ============================================================================
# AUTHENTICATION MODELS
# ============================================================================

class LoginRequest(BaseModel):
    """Login request."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")


# ============================================================================
# ERROR MODELS
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")

