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
    """
    Request to create a new substrate - The DNA of dimensional reality.

    PHILOSOPHY:
    A substrate is mathematical DNA that contains ALL possible properties in superposition.
    When created, everything exists - invocation reveals what already exists.

    TYPES:
    - foundational: z=x*y, z=x+y (building blocks - atoms)
    - complex: E=mc², Fibonacci (natural laws - molecules)
    - dimensional: Point, Line, Sphere (structural - organs)
    - object: Car, Ball, Person (complete entities - organisms)
    """
    expression_type: str = Field(..., description="Type of expression: 'lambda', 'constant', 'function'")
    expression_code: str = Field(..., description="Python code for the expression (NEVER exposed after creation)")
    substrate_category: Optional[str] = Field(default=None, description="Category: 'foundational', 'complex', 'dimensional', 'object'")
    dimension_level: Optional[int] = Field(default=None, description="Dimensional level: 0=point, 1=line, 2=plane, 3=volume, etc.")
    fibonacci_index: Optional[int] = Field(default=None, description="Position in Fibonacci sequence (0-8)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata about the substrate")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "name": "Foundational - Multiplication",
                    "value": {
                        "expression_type": "lambda",
                        "expression_code": "lambda x, y: x * y",
                        "substrate_category": "foundational",
                        "dimension_level": 2,
                        "metadata": {
                            "name": "Multiplication",
                            "description": "Fundamental multiplication - creates area (2D)",
                            "properties": ["commutative", "associative"]
                        }
                    }
                },
                {
                    "name": "Complex - Einstein's E=mc²",
                    "value": {
                        "expression_type": "lambda",
                        "expression_code": "lambda m: m * 299792458**2",
                        "substrate_category": "complex",
                        "metadata": {
                            "name": "E=mc²",
                            "description": "Einstein's mass-energy equivalence",
                            "natural_law": "Special Relativity",
                            "constants": {"c": 299792458}
                        }
                    }
                },
                {
                    "name": "Dimensional - Circle",
                    "value": {
                        "expression_type": "lambda",
                        "expression_code": "lambda r, property='area': {'area': 3.14159*r**2, 'circumference': 2*3.14159*r}[property]",
                        "substrate_category": "dimensional",
                        "dimension_level": 2,
                        "metadata": {
                            "name": "Circle",
                            "description": "2D circle with all geometric properties in superposition",
                            "properties": ["area", "circumference", "diameter"]
                        }
                    }
                },
                {
                    "name": "Object - Car",
                    "value": {
                        "expression_type": "function",
                        "expression_code": "def car(property=None): return {'engine': 200, 'wheels': 4, 'color': 'red'}.get(property) if property else {'engine': 200, 'wheels': 4, 'color': 'red'}",
                        "substrate_category": "object",
                        "dimension_level": 3,
                        "metadata": {
                            "name": "Car",
                            "description": "Complete vehicle with ALL properties in superposition",
                            "properties": ["engine", "wheels", "color", "mass", "speed"]
                        }
                    }
                }
            ]
        }


class SubstrateResponse(BaseModel):
    """Response containing substrate information.

    SECURITY: expression_code is NEVER included in responses to protect source code.
    """
    substrate_id: str = Field(..., description="Hex-encoded 64-bit substrate identity")
    identity: int = Field(..., description="Numeric substrate identity")
    created_at: datetime = Field(..., description="Creation timestamp")
    expression_type: str = Field(..., description="Type of expression")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Substrate metadata")
    owner_username: Optional[str] = Field(None, description="Owner username")
    invocation_count: int = Field(default=0, description="Number of times invoked")
    # NOTE: expression_code is NEVER exposed to clients for security


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


# ============================================================================
# LENS MODELS - Apply Context to Reveal Substrate Truths
# ============================================================================

class LensResponse(BaseModel):
    """Response containing lens information."""
    id: int
    name: str
    lens_type: str
    category: Optional[str] = None
    description: Optional[str] = None
    input_type: Optional[str] = None
    output_type: Optional[str] = None
    is_system: bool
    is_public: bool
    parameters: Optional[Dict[str, Any]] = None
    usage_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "color_distance",
                "lens_type": "spectrum",
                "category": "color",
                "description": "Maps distance from origin to color hue (0-360°)",
                "input_type": "point",
                "output_type": "color",
                "is_system": True,
                "is_public": True,
                "parameters": {"max_distance": 100, "color_space": "HSV"},
                "usage_count": 42,
                "created_at": "2026-02-09T12:00:00"
            }
        }


class CreateLensRequest(BaseModel):
    """Request to create a custom lens."""
    name: str = Field(..., description="Unique name for the lens")
    lens_type: str = Field(..., description="Type: spectrum, logic, physics, geometric, domain, design, graphics")
    category: Optional[str] = Field(None, description="Category: color, sound, gravity, fluid, etc.")
    description: Optional[str] = Field(None, description="Description of what the lens extracts")
    transformation_code: str = Field(..., description="Python code for the transformation function")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Default parameters for the lens")
    input_type: Optional[str] = Field(None, description="Input type: substrate, point, field")
    output_type: Optional[str] = Field(None, description="Output type: scalar, vector, color, frequency")
    is_public: bool = Field(True, description="Whether other users can use this lens")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "temperature_gradient",
                "lens_type": "physics",
                "category": "thermodynamics",
                "description": "Extracts temperature gradient from heat field",
                "transformation_code": "def apply(z, x, y, dx=0.01): return (z(x+dx,y) - z(x-dx,y)) / (2*dx)",
                "parameters": {"dx": 0.01, "dy": 0.01},
                "input_type": "substrate",
                "output_type": "vector",
                "is_public": True
            }
        }


class ApplyLensRequest(BaseModel):
    """Request to apply a lens to a substrate."""
    lens_name: str = Field(..., description="Name of the lens to apply")
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Override lens parameters")
    cache_result: bool = Field(True, description="Whether to cache the result")

    class Config:
        json_schema_extra = {
            "example": {
                "lens_name": "color_distance",
                "x": 5.0,
                "y": 3.0,
                "parameters": {"max_distance": 50},
                "cache_result": True
            }
        }


class ApplyLensResponse(BaseModel):
    """Response from applying a lens to a substrate."""
    substrate_id: str
    lens_name: str
    x: float
    y: float
    result: Dict[str, Any]
    computation_time_ms: float
    cached: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "substrate_id": "0x1A2B3C4D5E6F7890",
                "lens_name": "color_distance",
                "x": 5.0,
                "y": 3.0,
                "result": {"hue": 180.5, "saturation": 100, "value": 100},
                "computation_time_ms": 0.42,
                "cached": False
            }
        }


class LensListResponse(BaseModel):
    """Response containing list of lenses."""
    lenses: List[LensResponse]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "lenses": [
                    {
                        "id": 1,
                        "name": "color_distance",
                        "lens_type": "spectrum",
                        "category": "color",
                        "description": "Maps distance from origin to color hue",
                        "is_system": True,
                        "is_public": True
                    }
                ],
                "total": 1
            }
        }


class LensCategoriesResponse(BaseModel):
    """Response containing available lens categories."""
    categories: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "categories": ["color", "sound", "light", "gravity", "fluid", "shape"]
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


# ============================================================================
# SRL MODELS - Secure Resource Locator
# ============================================================================

class CreateSRLRequest(BaseModel):
    \"\"\"
    Request to register a new SRL connection.

    SECURITY: Credentials are encrypted before storage and NEVER exposed.
    \"\"\"
    name: str = Field(..., description=\"Connection name\")
    resource_type: str = Field(..., description=\"Resource type: file, database, api, stream, web, game, app\")
    protocol: str = Field(..., description=\"Protocol: postgresql, mongodb, http, https, file, etc.\")
    connection_string: str = Field(..., description=\"Connection string (will be encrypted)\")
    auth_method: str = Field(..., description=\"Auth method: none, basic, bearer, api_key, oauth, certificate, password\")
    credentials: Optional[Dict[str, Any]] = Field(default=None, description=\"Credentials (will be encrypted)\")
    config: Optional[Dict[str, Any]] = Field(default=None, description=\"Adapter configuration\")
    passive: bool = Field(default=True, description=\"Passive mode (fetch on demand)\")
    allow_cache: bool = Field(default=False, description=\"Allow caching fetched data\")
    default_cache_ttl: Optional[int] = Field(default=None, description=\"Default cache TTL in seconds\")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description=\"Additional metadata\")


class SRLResponse(BaseModel):
    \"\"\"
    Response containing SRL information.

    SECURITY: Only name and status are exposed. Credentials NEVER included.
    \"\"\"
    id: int = Field(..., description=\"SRL connection ID\")
    substrate_identity: str = Field(..., description=\"Substrate identity (18-char hex)\")
    name: str = Field(..., description=\"Connection name\")
    resource_type: str = Field(..., description=\"Resource type\")
    status: str = Field(..., description=\"Status: connected, disconnected, disabled, connecting, blacklisted\")
    created_at: str = Field(..., description=\"Creation timestamp\")
    last_used_at: Optional[str] = Field(default=None, description=\"Last used timestamp\")
    fetch_count: int = Field(..., description=\"Total fetch count\")
    is_active: bool = Field(..., description=\"Whether connection is active\")


class SRLFetchRequest(BaseModel):
    \"\"\"Request to fetch data from SRL.\"\"\"
    query: Optional[str] = Field(default=None, description=\"Query string (SQL, API endpoint, file path, etc.)\")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description=\"Additional parameters\")
    cache: bool = Field(default=False, description=\"Cache the result\")
    cache_ttl: Optional[int] = Field(default=None, description=\"Cache TTL in seconds\")


class SRLFetchResponse(BaseModel):
    \"\"\"Response from fetching data via SRL.\"\"\"
    success: bool = Field(..., description=\"Whether fetch was successful\")
    data: Any = Field(..., description=\"Fetched data\")
    metadata: Dict[str, Any] = Field(..., description=\"Fetch metadata (size, duration, etc.)\")
    cached: bool = Field(..., description=\"Whether result was cached\")
    duration_ms: float = Field(..., description=\"Fetch duration in milliseconds\")


class SRLListResponse(BaseModel):
    \"\"\"Response containing list of SRLs.\"\"\"
    srls: List[SRLResponse] = Field(..., description=\"List of SRL connections\")
    total: int = Field(..., description=\"Total count\")


class UpdateCredentialsRequest(BaseModel):
    \"\"\"Request to update SRL credentials.\"\"\"
    credentials: Dict[str, Any] = Field(..., description=\"New credentials (will be encrypted)\")


class SRLTestResponse(BaseModel):
    \"\"\"Response from testing SRL connection.\"\"\"
    success: bool = Field(..., description=\"Whether connection test was successful\")
    status: str = Field(..., description=\"Connection status\")
    message: str = Field(..., description=\"Status message\")
    duration_ms: float = Field(..., description=\"Test duration in milliseconds\")


class SRLFetchLogResponse(BaseModel):
    \"\"\"Response containing SRL fetch log entry.\"\"\"
    id: int = Field(..., description=\"Log entry ID\")
    connection_id: int = Field(..., description=\"SRL connection ID\")
    success: bool = Field(..., description=\"Whether fetch was successful\")
    result_size_bytes: Optional[int] = Field(default=None, description=\"Result size in bytes\")
    result_rows: Optional[int] = Field(default=None, description=\"Number of rows (for database queries)\")
    cached: bool = Field(..., description=\"Whether result was cached\")
    duration_ms: float = Field(..., description=\"Fetch duration in milliseconds\")
    error_message: Optional[str] = Field(default=None, description=\"Error message if failed\")
    fetched_at: str = Field(..., description=\"Fetch timestamp\")


class SRLFetchLogsResponse(BaseModel):
    \"\"\"Response containing list of SRL fetch logs.\"\"\"
    logs: List[SRLFetchLogResponse] = Field(..., description=\"List of fetch logs\")
    total: int = Field(..., description=\"Total count\")


class SRLProtocolsResponse(BaseModel):
    \"\"\"Response containing supported protocols.\"\"\"
    protocols: List[str] = Field(..., description=\"List of supported protocols\")
    count: int = Field(..., description=\"Total count\")
