"""
ButterflyFx Server - Main FastAPI Application

Exposes substrate operations via REST API.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from datetime import datetime
from typing import Dict, Any

from server.models import (
    CreateSubstrateRequest, SubstrateResponse,
    InvokeSubstrateRequest, InvokeSubstrateResponse,
    DivideSubstrateResponse, DimensionInfo,
    CreateRelationshipRequest, RelationshipResponse, RelationshipListResponse,
    SystemStatsResponse, ErrorResponse
)
from server.registry import get_registry
from kernel.substrate import Substrate, SubstrateIdentity
from kernel.relationships import Relationship, RelationshipType

# Create FastAPI app
app = FastAPI(
    title="ButterflyFx Server",
    description="HTTP API for DimensionOS Substrate Operations",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get registry
registry = get_registry()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def hex_to_int(hex_str: str) -> int:
    """Convert hex string to integer."""
    if hex_str.startswith("0x"):
        return int(hex_str, 16)
    return int(hex_str, 16)


def int_to_hex(value: int) -> str:
    """Convert integer to hex string."""
    return f"0x{value:016X}"


def compile_expression(expression_type: str, expression_code: str):
    """Compile expression code into a callable."""
    if expression_type == "lambda":
        # Compile lambda expression
        return eval(expression_code)
    elif expression_type == "constant":
        # Constant expression
        value = int(expression_code)
        return lambda **kw: value
    else:
        raise ValueError(f"Unsupported expression type: {expression_type}")


# ============================================================================
# HEALTH & SYSTEM ENDPOINTS
# ============================================================================

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.get("/api/v1/metrics", response_model=SystemStatsResponse)
async def get_metrics():
    """Get system metrics."""
    return SystemStatsResponse(
        total_substrates=registry.count_substrates(),
        total_relationships=registry.count_relationships(),
        uptime_seconds=registry.get_uptime(),
        version="1.0.0"
    )


# ============================================================================
# SUBSTRATE ENDPOINTS
# ============================================================================

@app.post("/api/v1/substrates", response_model=SubstrateResponse, status_code=status.HTTP_201_CREATED)
async def create_substrate(request: CreateSubstrateRequest):
    """Create a new substrate."""
    try:
        # Compile expression
        expression = compile_expression(request.expression_type, request.expression_code)
        
        # Generate identity from expression code
        identity_value = hash(request.expression_code) & 0xFFFFFFFFFFFFFFFF
        identity = SubstrateIdentity(identity_value)
        
        # Create substrate
        substrate = Substrate(identity, expression)
        
        # Add to registry
        registry.add_substrate(
            substrate=substrate,
            expression_type=request.expression_type,
            expression_code=request.expression_code,
            metadata=request.metadata
        )
        
        # Get metadata for response
        metadata = registry.get_substrate(identity_value)
        
        return SubstrateResponse(
            substrate_id=int_to_hex(identity_value),
            identity=identity_value,
            created_at=metadata.created_at,
            expression_type=request.expression_type,
            metadata=request.metadata
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create substrate: {str(e)}"
        )


@app.get("/api/v1/substrates/{substrate_id}", response_model=SubstrateResponse)
async def get_substrate(substrate_id: str):
    """Get substrate by identity."""
    try:
        identity_value = hex_to_int(substrate_id)
        metadata = registry.get_substrate(identity_value)
        
        if metadata is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Substrate {substrate_id} not found"
            )
        
        return SubstrateResponse(
            substrate_id=int_to_hex(identity_value),
            identity=identity_value,
            created_at=metadata.created_at,
            expression_type=metadata.expression_type,
            metadata=metadata.metadata
        )
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid substrate ID: {substrate_id}"
        )


@app.delete("/api/v1/substrates/{substrate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_substrate(substrate_id: str):
    """Delete substrate."""
    try:
        identity_value = hex_to_int(substrate_id)
        success = registry.delete_substrate(identity_value)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Substrate {substrate_id} not found"
            )

        return None

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid substrate ID: {substrate_id}"
        )


@app.post("/api/v1/substrates/{substrate_id}/divide", response_model=DivideSubstrateResponse)
async def divide_substrate(substrate_id: str):
    """Divide substrate into 9 Fibonacci dimensions."""
    try:
        identity_value = hex_to_int(substrate_id)
        metadata = registry.get_substrate(identity_value)

        if metadata is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Substrate {substrate_id} not found"
            )

        # Divide substrate
        dimensions = metadata.substrate.divide()

        # Dimension names and descriptions
        dim_info = [
            (0, "Void", "Potential"),
            (1, "Identity", "Who"),
            (1, "Domain", "What type"),
            (2, "Length", "Attributes"),
            (3, "Area", "Relationships"),
            (5, "Volume", "State + change"),
            (8, "Frequency", "Temporal patterns"),
            (13, "System", "Behaviors"),
            (21, "Complete", "Whole object")
        ]

        dimension_responses = [
            DimensionInfo(level=level, name=name, description=desc)
            for level, name, desc in dim_info
        ]

        return DivideSubstrateResponse(
            substrate_id=substrate_id,
            dimensions=dimension_responses,
            fibonacci_sequence=[0, 1, 1, 2, 3, 5, 8, 13, 21]
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid substrate ID: {substrate_id}"
        )


@app.post("/api/v1/substrates/{substrate_id}/invoke", response_model=InvokeSubstrateResponse)
async def invoke_substrate(substrate_id: str, request: InvokeSubstrateRequest):
    """Invoke substrate expression with parameters."""
    try:
        identity_value = hex_to_int(substrate_id)
        metadata = registry.get_substrate(identity_value)

        if metadata is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Substrate {substrate_id} not found"
            )

        # Invoke expression
        start_time = time.time()
        result = metadata.substrate._expression(**request.parameters)
        elapsed_ms = (time.time() - start_time) * 1000

        return InvokeSubstrateResponse(
            substrate_id=substrate_id,
            result=result,
            invocation_time_ms=elapsed_ms
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invocation failed: {str(e)}"
        )


# ============================================================================
# RELATIONSHIP ENDPOINTS
# ============================================================================

@app.post("/api/v1/relationships", response_model=RelationshipResponse, status_code=status.HTTP_201_CREATED)
async def create_relationship(request: CreateRelationshipRequest):
    """Create a new relationship between substrates."""
    try:
        # Parse identities
        source_value = hex_to_int(request.source_id)
        target_value = hex_to_int(request.target_id)

        # Verify substrates exist
        if registry.get_substrate(source_value) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source substrate {request.source_id} not found"
            )

        if registry.get_substrate(target_value) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target substrate {request.target_id} not found"
            )

        # Create relationship identity
        rel_identity_value = hash(f"{source_value}->{target_value}") & 0xFFFFFFFFFFFFFFFF

        # Create relationship
        relationship = Relationship(
            identity=SubstrateIdentity(rel_identity_value),
            rel_type=RelationshipType[request.rel_type],
            source=SubstrateIdentity(source_value),
            target=SubstrateIdentity(target_value),
            bidirectional=request.bidirectional,
            constraints=request.constraints
        )

        # Add to registry
        registry.add_relationship(relationship)

        return RelationshipResponse(
            relationship_id=int_to_hex(rel_identity_value),
            rel_type=request.rel_type,
            source_id=request.source_id,
            target_id=request.target_id,
            bidirectional=request.bidirectional,
            created_at=datetime.utcnow()
        )

    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid relationship type: {request.rel_type}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create relationship: {str(e)}"
        )


@app.get("/api/v1/relationships/outgoing/{substrate_id}", response_model=RelationshipListResponse)
async def get_outgoing_relationships(substrate_id: str):
    """Get all outgoing relationships from a substrate."""
    try:
        identity_value = hex_to_int(substrate_id)
        source = SubstrateIdentity(identity_value)

        relationships = registry.get_outgoing_relationships(source)

        responses = [
            RelationshipResponse(
                relationship_id=int_to_hex(rel.identity.value),
                rel_type=rel.rel_type.value,
                source_id=int_to_hex(rel.source.value),
                target_id=int_to_hex(rel.target.value),
                bidirectional=rel.bidirectional,
                created_at=datetime.utcnow()  # Note: We don't store creation time in Relationship
            )
            for rel in relationships
        ]

        return RelationshipListResponse(
            relationships=responses,
            count=len(responses)
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid substrate ID: {substrate_id}"
        )


@app.get("/api/v1/relationships/incoming/{substrate_id}", response_model=RelationshipListResponse)
async def get_incoming_relationships(substrate_id: str):
    """Get all incoming relationships to a substrate."""
    try:
        identity_value = hex_to_int(substrate_id)
        target = SubstrateIdentity(identity_value)

        relationships = registry.get_incoming_relationships(target)

        responses = [
            RelationshipResponse(
                relationship_id=int_to_hex(rel.identity.value),
                rel_type=rel.rel_type.value,
                source_id=int_to_hex(rel.source.value),
                target_id=int_to_hex(rel.target.value),
                bidirectional=rel.bidirectional,
                created_at=datetime.utcnow()
            )
            for rel in relationships
        ]

        return RelationshipListResponse(
            relationships=responses,
            count=len(responses)
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid substrate ID: {substrate_id}"
        )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

