"""
ButterflyFx Server v2.0 - Production-Grade Dimensional Computation Platform

FEATURES:
- User authentication & registration
- TOS acceptance required
- Source code protection (server-side only execution)
- All dimensional operators (divide, multiply, add, subtract, modulus, power, root)
- Redis caching (10-100x performance boost)
- PostgreSQL persistence
- Rate limiting
- Prometheus metrics
- Advanced monitoring

SECURITY:
- JWT authentication
- Password hashing (bcrypt)
- No source code exposure to clients
- Rate limiting per user
- Session management
"""

from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.security import HTTPBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from sqlalchemy.orm import Session
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import traceback

# Server modules
from server.config import settings, validate_settings
from server.database import (
    get_db, init_db, User, TOSAgreement, SubstrateModel, RelationshipModel,
    Session as SessionModel, LensModel, LensApplicationModel, CURRENT_TOS_VERSION
)
from server.auth import (
    get_current_user, get_current_active_user, get_current_superuser,
    create_access_token, create_refresh_token, verify_password, get_password_hash
)
from server.models import *
from server.models_auth import *
from server.legal import TERMS_OF_SERVICE, DISCLAIMER, TOS_VERSION, TOS_EFFECTIVE_DATE
from server.cache import cache
from server.lenses import SYSTEM_LENSES, compile_lens, get_available_lenses

# Kernel imports
from kernel.substrate import Substrate, SubstrateIdentity
from kernel.relationships import Relationship, RelationshipType
from kernel.operators import (
    cross_divide, cross_multiply, cross_modulus, cross_power, cross_root,
    intra_add, intra_subtract
)
from kernel.fibonacci import fibonacci_sequence

# ============================================================================
# APPLICATION SETUP
# ============================================================================

# Validate configuration
validate_settings()

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="ButterflyFx Server",
    description="Production-Grade Dimensional Computation Platform (Patent Pending)",
    version=settings.APP_VERSION,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Server start time
SERVER_START_TIME = datetime.utcnow()

# ============================================================================
# PROMETHEUS METRICS
# ============================================================================

# Counters
requests_total = Counter('butterflyfx_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
substrate_creations_total = Counter('butterflyfx_substrate_creations_total', 'Total substrate creations')
substrate_invocations_total = Counter('butterflyfx_substrate_invocations_total', 'Total substrate invocations')
user_registrations_total = Counter('butterflyfx_user_registrations_total', 'Total user registrations')
user_logins_total = Counter('butterflyfx_user_logins_total', 'Total user logins')
srl_connections_total = Counter('butterflyfx_srl_connections_total', 'Total SRL connections created')
srl_fetches_total = Counter('butterflyfx_srl_fetches_total', 'Total SRL data fetches')
errors_total = Counter('butterflyfx_errors_total', 'Total errors', ['error_type'])

# Histograms
request_duration = Histogram('butterflyfx_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
invocation_duration = Histogram('butterflyfx_invocation_duration_seconds', 'Substrate invocation duration')

# Gauges
active_users = Gauge('butterflyfx_active_users', 'Number of active users')
total_substrates = Gauge('butterflyfx_total_substrates', 'Total substrates in database')
total_relationships = Gauge('butterflyfx_total_relationships', 'Total relationships in database')
cache_hit_rate = Gauge('butterflyfx_cache_hit_rate_percent', 'Cache hit rate percentage')


# ============================================================================
# MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Track request metrics."""
    start_time = time.time()
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Record metrics
        requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        request_duration.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response
    
    except Exception as e:
        duration = time.time() - start_time
        errors_total.labels(error_type=type(e).__name__).inc()
        raise


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
    """Compile expression code into a callable (SERVER-SIDE ONLY)."""
    if expression_type == "lambda":
        return eval(expression_code)
    elif expression_type == "constant":
        value = int(expression_code)
        return lambda **kw: value
    else:
        raise ValueError(f"Unsupported expression type: {expression_type}")


def check_tos_acceptance(user: User, db: Session) -> bool:
    """Check if user has accepted current TOS version."""
    agreement = db.query(TOSAgreement).filter(
        TOSAgreement.user_id == user.id,
        TOSAgreement.tos_version == CURRENT_TOS_VERSION
    ).first()
    return agreement is not None


# ============================================================================
# AUTHENTICATION & USER ENDPOINTS
# ============================================================================

@app.get("/api/v1/legal/tos", response_model=TOSResponse)
async def get_terms_of_service():
    """Get current Terms of Service."""
    return TOSResponse(
        version=TOS_VERSION,
        effective_date=TOS_EFFECTIVE_DATE,
        content=TERMS_OF_SERVICE,
        disclaimer=DISCLAIMER
    )


@app.post("/api/v1/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register_user(
    request: Request,
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user.

    REQUIREMENTS:
    - Must accept current TOS version
    - Password must meet strength requirements
    - Email must be unique
    - Username must be unique
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Verify TOS version matches current
    if user_data.tos_version != CURRENT_TOS_VERSION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Must accept current TOS version {CURRENT_TOS_VERSION}"
        )

    # Create user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Record TOS acceptance
    tos_agreement = TOSAgreement(
        user_id=new_user.id,
        tos_version=user_data.tos_version,
        agreed_at=datetime.utcnow(),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    db.add(tos_agreement)
    db.commit()

    # Create tokens
    access_token = create_access_token(data={"sub": new_user.id})
    refresh_token = create_refresh_token(data={"sub": new_user.id})

    # Update metrics
    user_registrations_total.inc()
    active_users.set(db.query(User).filter(User.is_active == True).count())

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.from_orm(new_user)
    )


@app.post("/api/v1/auth/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login_user(
    request: Request,
    credentials: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login user and return JWT tokens.

    Accepts username or email for login.
    """
    # Find user by username or email
    user = db.query(User).filter(
        (User.username == credentials.username) | (User.email == credentials.username)
    ).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Check TOS acceptance
    if not check_tos_acceptance(user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Must accept Terms of Service version {CURRENT_TOS_VERSION}"
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    # Update metrics
    user_logins_total.inc()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.from_orm(user)
    )


@app.get("/api/v1/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information."""
    return UserResponse.from_orm(current_user)


# ============================================================================
# HEALTH & SYSTEM ENDPOINTS
# ============================================================================

@app.get("/api/v1/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    # Check database
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Check cache
    cache_stats = cache.get_stats()

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "database": db_status,
        "cache": cache_stats.get("status", "unknown"),
        "uptime_seconds": (datetime.utcnow() - SERVER_START_TIME).total_seconds()
    }


@app.get("/api/v1/metrics/advanced")
async def get_advanced_metrics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get advanced system metrics (authenticated users only)."""

    # Update gauges
    total_users = db.query(User).count()
    active_users_count = db.query(User).filter(User.is_active == True).count()
    total_substrates_count = db.query(SubstrateModel).count()
    total_relationships_count = db.query(RelationshipModel).count()

    active_users.set(active_users_count)
    total_substrates.set(total_substrates_count)
    total_relationships.set(total_relationships_count)

    # Cache stats
    cache_stats = cache.get_stats()
    if cache_stats.get("enabled"):
        cache_hit_rate.set(cache_stats.get("hit_rate", 0))

    return {
        "users": {
            "total": total_users,
            "active": active_users_count,
        },
        "substrates": {
            "total": total_substrates_count,
        },
        "relationships": {
            "total": total_relationships_count,
        },
        "cache": cache_stats,
        "uptime_seconds": (datetime.utcnow() - SERVER_START_TIME).total_seconds(),
        "version": settings.APP_VERSION
    }


@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint."""
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ============================================================================
# SUBSTRATE ENDPOINTS (All require authentication, NO source code exposure)
# ============================================================================

@app.post("/api/v1/substrates", response_model=SubstrateResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
async def create_substrate(
    request: Request,
    substrate_request: CreateSubstrateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new substrate (authenticated users only).

    SECURITY: Expression code is stored server-side only and NEVER exposed to clients.
    """
    try:
        # Compile expression (server-side only)
        expression = compile_expression(
            substrate_request.expression_type,
            substrate_request.expression_code
        )

        # Generate identity from expression code
        identity_value = hash(substrate_request.expression_code) & 0xFFFFFFFFFFFFFFFF
        identity_hex = int_to_hex(identity_value)

        # Check if substrate already exists
        existing = db.query(SubstrateModel).filter(
            SubstrateModel.identity_value == identity_value
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Substrate with identity {identity_hex} already exists"
            )

        # Create substrate in database
        # PHILOSOPHY: At this moment, ALL properties exist in superposition
        # The substrate contains everything - invocation will reveal what already exists
        substrate_model = SubstrateModel(
            identity=identity_hex,
            identity_value=identity_value,
            expression_type=substrate_request.expression_type,
            expression_code=substrate_request.expression_code,  # The DNA (NEVER exposed)
            substrate_category=substrate_request.substrate_category,
            dimension_level=substrate_request.dimension_level,
            fibonacci_index=substrate_request.fibonacci_index,
            metadata=substrate_request.metadata,
            owner_id=current_user.id,
            created_at=datetime.utcnow(),
            invocation_count=0
        )

        db.add(substrate_model)
        db.commit()
        db.refresh(substrate_model)

        # Update metrics
        substrate_creations_total.inc()
        total_substrates.set(db.query(SubstrateModel).count())

        # Return response WITHOUT source code
        return SubstrateResponse(
            substrate_id=identity_hex,
            identity=identity_value,
            created_at=substrate_model.created_at,
            expression_type=substrate_model.expression_type,
            metadata=substrate_model.metadata,
            owner_username=current_user.username,
            invocation_count=0
        )

    except Exception as e:
        errors_total.labels(error_type=type(e).__name__).inc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create substrate: {str(e)}"
        )


@app.get("/api/v1/substrates/{substrate_id}", response_model=SubstrateResponse)
async def get_substrate(
    substrate_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get substrate by ID (authenticated users only).

    SECURITY: Expression code is NEVER included in response.
    """
    try:
        identity_value = hex_to_int(substrate_id)

        substrate_model = db.query(SubstrateModel).filter(
            SubstrateModel.identity_value == identity_value
        ).first()

        if not substrate_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Substrate {substrate_id} not found"
            )

        # Get owner username
        owner = db.query(User).filter(User.id == substrate_model.owner_id).first()

        # Return WITHOUT source code
        return SubstrateResponse(
            substrate_id=substrate_model.identity,
            identity=substrate_model.identity_value,
            created_at=substrate_model.created_at,
            expression_type=substrate_model.expression_type,
            metadata=substrate_model.metadata,
            owner_username=owner.username if owner else "unknown",
            invocation_count=substrate_model.invocation_count
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid substrate ID: {substrate_id}"
        )


@app.delete("/api/v1/substrates/{substrate_id}")
async def delete_substrate(
    substrate_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete substrate (owner only)."""
    try:
        identity_value = hex_to_int(substrate_id)

        substrate_model = db.query(SubstrateModel).filter(
            SubstrateModel.identity_value == identity_value
        ).first()

        if not substrate_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Substrate {substrate_id} not found"
            )

        # Check ownership
        if substrate_model.owner_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own substrates"
            )

        db.delete(substrate_model)
        db.commit()

        # Update metrics
        total_substrates.set(db.query(SubstrateModel).count())

        return {"message": f"Substrate {substrate_id} deleted successfully"}

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid substrate ID: {substrate_id}"
        )


@app.post("/api/v1/substrates/{substrate_id}/invoke", response_model=InvokeSubstrateResponse)
@limiter.limit("1000/minute")
async def invoke_substrate(
    request: Request,
    substrate_id: str,
    invoke_request: InvokeSubstrateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Invoke substrate expression with parameters.

    PERFORMANCE: Results are cached in Redis for 10-100x speedup on repeated invocations.
    """
    try:
        identity_value = hex_to_int(substrate_id)

        # Check cache first (10-100x faster)
        cache_key_args = (substrate_id, str(invoke_request.parameters))
        cached_result = cache.get("invoke", *cache_key_args)
        if cached_result:
            return InvokeSubstrateResponse(
                substrate_id=substrate_id,
                result=cached_result["result"],
                invocation_time_ms=cached_result["invocation_time_ms"],
                cached=True
            )

        # Get substrate from database
        substrate_model = db.query(SubstrateModel).filter(
            SubstrateModel.identity_value == identity_value
        ).first()

        if not substrate_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Substrate {substrate_id} not found"
            )

        # Compile expression (server-side only)
        expression = compile_expression(
            substrate_model.expression_type,
            substrate_model.expression_code
        )

        # Invoke expression
        start_time = time.time()
        result = expression(**invoke_request.parameters)
        elapsed_ms = (time.time() - start_time) * 1000

        # Update invocation count
        substrate_model.invocation_count += 1
        substrate_model.last_invoked_at = datetime.utcnow()
        db.commit()

        # Cache result
        cache_data = {
            "result": result,
            "invocation_time_ms": elapsed_ms
        }
        cache.set("invoke", cache_data, settings.REDIS_CACHE_TTL, *cache_key_args)

        # Update metrics
        substrate_invocations_total.inc()
        invocation_duration.observe(elapsed_ms / 1000)

        return InvokeSubstrateResponse(
            substrate_id=substrate_id,
            result=result,
            invocation_time_ms=elapsed_ms,
            cached=False
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid substrate ID: {substrate_id}"
        )
    except Exception as e:
        errors_total.labels(error_type=type(e).__name__).inc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invocation failed: {str(e)}"
        )


# ============================================================================
# DIMENSIONAL OPERATORS (All require authentication)
# ============================================================================

@app.post("/api/v1/substrates/{substrate_id}/divide", response_model=DivideSubstrateResponse)
async def divide_substrate(
    substrate_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    DIVISION (/) - Creates dimensions by splitting unity into parts.

    Divides substrate into 9 Fibonacci dimensions: [0, 1, 1, 2, 3, 5, 8, 13, 21]

    PHILOSOPHY:
    - Division creates structure (parts/dimensions)
    - Each dimension inherits the whole (like DNA in every cell)
    - 21 represents completion (7) → becomes 1 in next higher plane
    """
    try:
        identity_value = hex_to_int(substrate_id)

        substrate_model = db.query(SubstrateModel).filter(
            SubstrateModel.identity_value == identity_value
        ).first()

        if not substrate_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Substrate {substrate_id} not found"
            )

        # Create substrate object
        identity = SubstrateIdentity(identity_value)
        expression = compile_expression(
            substrate_model.expression_type,
            substrate_model.expression_code
        )
        substrate = Substrate(identity, expression)

        # Divide into 9 Fibonacci dimensions
        dimensions = cross_divide(substrate)

        # Get Fibonacci sequence
        fib_sequence = fibonacci_sequence(9)

        # Build response
        dimension_info = [
            DimensionInfo(
                level=dim.level,
                fibonacci_value=fib_sequence[i],
                manifestation=dim.manifest()
            )
            for i, dim in enumerate(dimensions)
        ]

        return DivideSubstrateResponse(
            substrate_id=substrate_id,
            dimensions=dimension_info,
            fibonacci_sequence=fib_sequence
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid substrate ID: {substrate_id}"
        )
    except Exception as e:
        errors_total.labels(error_type=type(e).__name__).inc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Division failed: {str(e)}"
        )


@app.post("/api/v1/substrates/multiply")
async def multiply_dimensions(
    values: List[int],
    current_user: User = Depends(get_current_active_user)
):
    """
    MULTIPLICATION (*) - Unifies parts into whole, collapses dimensions back to unity.

    Takes multiple dimensional values and combines them into a single unified value.

    PHILOSOPHY:
    - Multiplication destroys structure (returns to unity)
    - Parts collapse back to whole
    - Reverse of division

    Example: [2, 3, 5] → 30 (unified whole)
    """
    try:
        if not values:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide at least one value"
            )

        # Multiply all values to restore unity
        unity = cross_multiply(values)

        return {
            "operation": "multiply",
            "input_values": values,
            "unity_value": unity,
            "unity_hex": int_to_hex(unity),
            "dimensions_collapsed": len(values),
            "description": "Parts unified back to whole"
        }

    except Exception as e:
        errors_total.labels(error_type=type(e).__name__).inc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Multiplication failed: {str(e)}"
        )


@app.post("/api/v1/substrates/{substrate_id}/add")
async def add_to_substrate(
    substrate_id: str,
    value: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    ADDITION (+) - Concatenate/add points within dimension.

    Expands within the same dimension by adding points.

    PHILOSOPHY:
    - Addition works within structure (same dimension)
    - Adds more points to the line/plane/volume
    - Same dimensional level, more magnitude

    Example: 100 points + 50 points = 150 points (same dimension, longer)
    """
    try:
        identity_value = hex_to_int(substrate_id)

        substrate_model = db.query(SubstrateModel).filter(
            SubstrateModel.identity_value == identity_value
        ).first()

        if not substrate_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Substrate {substrate_id} not found"
            )

        # Add within dimension
        result = intra_add(identity_value, value)

        return {
            "operation": "add",
            "substrate_id": substrate_id,
            "original_value": identity_value,
            "added_value": value,
            "result_value": result,
            "result_hex": int_to_hex(result),
            "description": "Points added within dimension (expanded)"
        }

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid substrate ID: {substrate_id}"
        )
    except Exception as e:
        errors_total.labels(error_type=type(e).__name__).inc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Addition failed: {str(e)}"
        )


@app.post("/api/v1/substrates/{substrate_id}/subtract")
async def subtract_from_substrate(
    substrate_id: str,
    value: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    SUBTRACTION (-) - Remove points/parts within dimension.

    Contracts within dimension by removing points.

    PHILOSOPHY:
    - Subtraction works within structure (same dimension)
    - Removes points from the line/plane/volume
    - Same dimensional level, less magnitude

    Example: 150 points - 50 points = 100 points (same dimension, shorter)
    """
    try:
        identity_value = hex_to_int(substrate_id)

        substrate_model = db.query(SubstrateModel).filter(
            SubstrateModel.identity_value == identity_value
        ).first()

        if not substrate_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Substrate {substrate_id} not found"
            )

        # Subtract within dimension
        result = intra_subtract(identity_value, value)

        return {
            "operation": "subtract",
            "substrate_id": substrate_id,
            "original_value": identity_value,
            "subtracted_value": value,
            "result_value": result,
            "result_hex": int_to_hex(result),
            "description": "Points removed within dimension (contracted)"
        }

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid substrate ID: {substrate_id}"
        )
    except Exception as e:
        errors_total.labels(error_type=type(e).__name__).inc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Subtraction failed: {str(e)}"
        )


@app.post("/api/v1/substrates/{substrate_id}/modulus")
async def modulus_substrate(
    substrate_id: str,
    modulus: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    MODULUS (%) - Extract residue/residuals (unexpressed remainder).

    Returns what cannot be expressed in current dimension.

    PHILOSOPHY:
    - Modulus extracts the unexpressed (residue)
    - Residue seeds the next dimensional recursion
    - What doesn't fit in current structure

    Example: 100 % 7 = (2 expressed, 98 residue)
    """
    try:
        identity_value = hex_to_int(substrate_id)

        substrate_model = db.query(SubstrateModel).filter(
            SubstrateModel.identity_value == identity_value
        ).first()

        if not substrate_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Substrate {substrate_id} not found"
            )

        if modulus <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Modulus must be positive"
            )

        # Extract residue
        identity = SubstrateIdentity(identity_value)
        expressed, residue = cross_modulus(identity_value, modulus, identity)

        return {
            "operation": "modulus",
            "substrate_id": substrate_id,
            "original_value": identity_value,
            "modulus": modulus,
            "expressed": expressed,
            "residue": {
                "value": residue.value,
                "identity_hex": int_to_hex(residue.identity.value),
                "description": "Unexpressed remainder (seeds next recursion)"
            },
            "description": f"{identity_value} % {modulus} = {expressed} (with residue {residue.value})"
        }

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid substrate ID: {substrate_id}"
        )
    except Exception as e:
        errors_total.labels(error_type=type(e).__name__).inc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Modulus operation failed: {str(e)}"
        )


@app.post("/api/v1/substrates/{substrate_id}/power")
async def power_substrate(
    substrate_id: str,
    exponent: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    POWER (**) - Dimensional stacking.

    Creates higher-order dimensional spaces.

    PHILOSOPHY:
    - Power creates dimensional stacking
    - x^2 = area (2D), x^3 = volume (3D), x^4 = hypervolume (4D)
    - Elevates to higher dimensional plane

    Example: 10^2 = 100 (point → area), 10^3 = 1000 (point → volume)
    """
    try:
        identity_value = hex_to_int(substrate_id)

        substrate_model = db.query(SubstrateModel).filter(
            SubstrateModel.identity_value == identity_value
        ).first()

        if not substrate_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Substrate {substrate_id} not found"
            )

        if exponent < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exponent must be non-negative"
            )

        # Dimensional stacking
        result = cross_power(identity_value, exponent)

        # Determine dimensional description
        dim_names = {0: "point", 1: "line", 2: "area", 3: "volume", 4: "hypervolume"}
        dim_desc = dim_names.get(exponent, f"{exponent}D space")

        return {
            "operation": "power",
            "substrate_id": substrate_id,
            "base_value": identity_value,
            "exponent": exponent,
            "result_value": result,
            "result_hex": int_to_hex(result),
            "dimensional_elevation": f"Elevated to {dim_desc}",
            "description": f"{identity_value}^{exponent} = {result} (dimensional stacking)"
        }

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid substrate ID: {substrate_id}"
        )
    except Exception as e:
        errors_total.labels(error_type=type(e).__name__).inc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Power operation failed: {str(e)}"
        )


@app.post("/api/v1/substrates/{substrate_id}/root")
async def root_substrate(
    substrate_id: str,
    degree: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    ROOT (√) - Dimensional reduction.

    Reduces dimensional order.

    PHILOSOPHY:
    - Root reduces dimensional complexity
    - √(area) = length, ∛(volume) = length
    - Descends to lower dimensional plane

    Example: √100 = 10 (area → line), ∛1000 = 10 (volume → line)
    """
    try:
        identity_value = hex_to_int(substrate_id)

        substrate_model = db.query(SubstrateModel).filter(
            SubstrateModel.identity_value == identity_value
        ).first()

        if not substrate_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Substrate {substrate_id} not found"
            )

        if degree <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Root degree must be positive"
            )

        # Dimensional reduction
        result = cross_root(identity_value, degree)

        # Determine dimensional description
        root_names = {2: "square root", 3: "cube root", 4: "fourth root"}
        root_desc = root_names.get(degree, f"{degree}th root")

        return {
            "operation": "root",
            "substrate_id": substrate_id,
            "value": identity_value,
            "degree": degree,
            "result_value": result,
            "result_hex": int_to_hex(result),
            "dimensional_reduction": f"Reduced via {root_desc}",
            "description": f"{root_desc}({identity_value}) = {result} (dimensional reduction)"
        }

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid substrate ID: {substrate_id}"
        )
    except Exception as e:
        errors_total.labels(error_type=type(e).__name__).inc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Root operation failed: {str(e)}"
        )


# ============================================================================
# LENS ENDPOINTS - Apply Context to Reveal Substrate Truths
# ============================================================================

@app.get("/api/v1/lenses", response_model=LensListResponse)
@limiter.limit("100/minute")
async def list_lenses(
    request: Request,
    category: Optional[str] = None,
    lens_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List available lenses (system + user-created).

    PHILOSOPHY:
    Lenses extract truths from substrates. This endpoint shows what perspectives
    are available to view your substrates through.
    """
    try:
        query = db.query(LensModel)

        # Filter by category if provided
        if category:
            query = query.filter(LensModel.category == category)

        # Filter by lens_type if provided
        if lens_type:
            query = query.filter(LensModel.lens_type == lens_type)

        # Only show public lenses or user's own lenses
        query = query.filter(
            (LensModel.is_public == True) | (LensModel.owner_id == current_user.id)
        )

        lenses = query.all()

        return LensListResponse(
            lenses=[LensResponse.model_validate(lens) for lens in lenses],
            total=len(lenses)
        )

    except Exception as e:
        errors_total.labels(error_type=type(e).__name__).inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list lenses: {str(e)}"
        )


@app.get("/api/v1/lenses/categories", response_model=LensCategoriesResponse)
@limiter.limit("100/minute")
async def get_lens_categories(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all available lens categories."""
    try:
        categories = db.query(LensModel.category).filter(
            LensModel.category.isnot(None),
            (LensModel.is_public == True) | (LensModel.owner_id == current_user.id)
        ).distinct().all()

        return LensCategoriesResponse(
            categories=[cat[0] for cat in categories if cat[0]]
        )

    except Exception as e:
        errors_total.labels(error_type=type(e).__name__).inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get categories: {str(e)}"
        )


@app.get("/api/v1/lenses/{lens_name}", response_model=LensResponse)
@limiter.limit("100/minute")
async def get_lens(
    request: Request,
    lens_name: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific lens."""
    try:
        lens = db.query(LensModel).filter(
            LensModel.name == lens_name,
            (LensModel.is_public == True) | (LensModel.owner_id == current_user.id)
        ).first()

        if not lens:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lens '{lens_name}' not found or not accessible"
            )

        return LensResponse.model_validate(lens)

    except HTTPException:
        raise
    except Exception as e:
        errors_total.labels(error_type=type(e).__name__).inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get lens: {str(e)}"
        )


@app.post("/api/v1/lenses", response_model=LensResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_lens(
    request: Request,
    lens_request: CreateLensRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a custom lens (authenticated users only).

    PHILOSOPHY:
    Users can create their own lenses to extract custom truths from substrates.
    This is how you define new perspectives on reality.
    """
    try:
        # Check if lens name already exists
        existing = db.query(LensModel).filter(LensModel.name == lens_request.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Lens with name '{lens_request.name}' already exists"
            )

        # Validate transformation code by compiling it
        try:
            compile_lens(lens_request.transformation_code)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid transformation code: {str(e)}"
            )

        # Create lens
        lens_model = LensModel(
            name=lens_request.name,
            lens_type=lens_request.lens_type,
            category=lens_request.category,
            description=lens_request.description,
            transformation_code=lens_request.transformation_code,
            parameters=lens_request.parameters,
            input_type=lens_request.input_type,
            output_type=lens_request.output_type,
            owner_id=current_user.id,
            is_system=False,
            is_public=lens_request.is_public,
            created_at=datetime.utcnow(),
            usage_count=0
        )

        db.add(lens_model)
        db.commit()
        db.refresh(lens_model)

        return LensResponse.model_validate(lens_model)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        errors_total.labels(error_type=type(e).__name__).inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create lens: {str(e)}"
        )


@app.post("/api/v1/substrates/{substrate_id}/apply-lens", response_model=ApplyLensResponse)
@limiter.limit("100/minute")
async def apply_lens_to_substrate(
    request: Request,
    substrate_id: str,
    lens_request: ApplyLensRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Apply a lens to a substrate at a specific point.

    PHILOSOPHY:
    This is where the magic happens - the lens extracts specific truth from the substrate.
    The substrate contains ALL information; the lens reveals what you seek.

    EXAMPLE:
    - Substrate: z = x² + y² (paraboloid)
    - Lens: color_distance
    - Point: (5, 3)
    - Result: {hue: 180, saturation: 100, value: 100} (cyan color)
    """
    try:
        # Get substrate
        identity_value = hex_to_int(substrate_id)
        substrate_model = db.query(SubstrateModel).filter(
            SubstrateModel.identity_value == identity_value
        ).first()

        if not substrate_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Substrate {substrate_id} not found"
            )

        # Check ownership
        if substrate_model.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this substrate"
            )

        # Get lens
        lens_model = db.query(LensModel).filter(
            LensModel.name == lens_request.lens_name,
            (LensModel.is_public == True) | (LensModel.owner_id == current_user.id)
        ).first()

        if not lens_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lens '{lens_request.lens_name}' not found or not accessible"
            )

        # Check cache first
        cache_key = f"lens:{lens_model.id}:substrate:{substrate_id}:x:{lens_request.x}:y:{lens_request.y}"
        cached_result = cache.get(cache_key)

        if cached_result:
            return ApplyLensResponse(
                substrate_id=substrate_id,
                lens_name=lens_request.lens_name,
                x=lens_request.x,
                y=lens_request.y,
                result=cached_result["result"],
                computation_time_ms=cached_result["computation_time_ms"],
                cached=True
            )

        # Compile substrate expression
        substrate_func = compile_expression(
            substrate_model.expression_type,
            substrate_model.expression_code
        )

        # Compile lens transformation
        lens_func = compile_lens(lens_model.transformation_code)

        # Merge parameters
        lens_params = {**(lens_model.parameters or {}), **(lens_request.parameters or {})}

        # Apply lens
        start_time = time.time()

        # Evaluate substrate at point
        z = substrate_func(x=lens_request.x, y=lens_request.y)

        # Apply lens transformation
        result = lens_func(z, lens_request.x, lens_request.y, **lens_params)

        computation_time_ms = (time.time() - start_time) * 1000

        # Cache result if requested
        if lens_request.cache_result:
            cache.set(cache_key, {
                "result": result,
                "computation_time_ms": computation_time_ms
            }, ttl=3600)  # Cache for 1 hour

        # Record lens application
        if lens_request.cache_result:
            lens_application = LensApplicationModel(
                lens_id=lens_model.id,
                substrate_identity=substrate_id,
                application_parameters={"x": lens_request.x, "y": lens_request.y, **lens_params},
                result_cached=True,
                result_data=result,
                computation_time_ms=computation_time_ms,
                applied_by=current_user.id,
                applied_at=datetime.utcnow()
            )
            db.add(lens_application)

        # Update lens usage count
        lens_model.usage_count += 1

        # Update substrate invocation count
        substrate_model.invocation_count += 1
        substrate_model.last_invoked_at = datetime.utcnow()

        db.commit()

        return ApplyLensResponse(
            substrate_id=substrate_id,
            lens_name=lens_request.lens_name,
            x=lens_request.x,
            y=lens_request.y,
            result=result,
            computation_time_ms=computation_time_ms,
            cached=False
        )

    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid substrate ID: {substrate_id}"
        )
    except Exception as e:
        db.rollback()
        errors_total.labels(error_type=type(e).__name__).inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply lens: {str(e)}"
        )


# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print(f"🦋 ButterflyFx Server v{settings.APP_VERSION} starting...")
    print(f"📊 Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'configured'}")
    print(f"🔴 Redis: {settings.REDIS_URL}")
    print(f"🔒 Authentication: Enabled (JWT)")
    print(f"⚖️  TOS Version: {CURRENT_TOS_VERSION}")

    # Initialize system lenses
    db = next(get_db())
    try:
        print(f"🔍 Initializing system lenses...")
        initialized_count = 0
        for lens_name, lens_data in SYSTEM_LENSES.items():
            # Check if lens already exists
            existing = db.query(LensModel).filter(LensModel.name == lens_name).first()
            if not existing:
                lens_model = LensModel(
                    name=lens_data["name"],
                    lens_type=lens_data["lens_type"],
                    category=lens_data["category"],
                    description=lens_data["description"],
                    transformation_code=lens_data["transformation_code"],
                    parameters=lens_data["parameters"],
                    input_type=lens_data["input_type"],
                    output_type=lens_data["output_type"],
                    owner_id=None,  # System lenses have no owner
                    is_system=True,
                    is_public=True,
                    created_at=datetime.utcnow(),
                    usage_count=0
                )
                db.add(lens_model)
                initialized_count += 1

        db.commit()
        print(f"✅ Initialized {initialized_count} system lenses")
    except Exception as e:
        db.rollback()
        print(f"⚠️  Warning: Failed to initialize system lenses: {str(e)}")
    finally:
        db.close()

    print(f"🚀 Server ready!")


# ============================================================================
# SRL ENDPOINTS - Secure Resource Locator (Universal Connector)
# ============================================================================

@app.post("/api/v1/srl/register", response_model=SRLResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def register_srl_connection(
    request: Request,
    srl_request: CreateSRLRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Register a new SRL connection.

    SECURITY:
    - Credentials are encrypted with AES-256 before storage
    - Only name and status are exposed in responses
    - Per-user connections (isolated by user_id)

    PHILOSOPHY:
    - SRL is like a library card - it fetches but doesn't copy
    - Passive until invoked (Safety Charter #2)
    - No caching unless explicitly requested
    """
    try:
        from server.srl_crypto import SRLCrypto
        from server.database import SRLConnectionModel, SubstrateModel
        from kernel.substrate import SubstrateIdentity

        # Initialize encryption
        crypto = SRLCrypto()

        # Encrypt credentials
        encrypted_credentials = None
        if srl_request.credentials:
            encrypted_credentials = crypto.encrypt_credentials(srl_request.credentials)

        # Create substrate for SRL
        substrate_identity = SubstrateIdentity.generate()
        substrate = SubstrateModel(
            identity=substrate_identity.value,
            expression_type="srl_connector",
            expression_code=f"# SRL: {srl_request.name}",
            substrate_category="srl",
            dimension_level=0,
            fibonacci_index=0,
            owner_id=current_user.id,
            metadata={
                "srl_name": srl_request.name,
                "resource_type": srl_request.resource_type,
                "protocol": srl_request.protocol
            }
        )
        db.add(substrate)
        db.flush()

        # Create SRL connection
        srl_connection = SRLConnectionModel(
            substrate_id=substrate.id,
            user_id=current_user.id,
            name=srl_request.name,
            resource_type=srl_request.resource_type,
            protocol=srl_request.protocol,
            connection_string=srl_request.connection_string,
            auth_method=srl_request.auth_method,
            encrypted_credentials=encrypted_credentials,
            config=srl_request.config,
            passive=srl_request.passive,
            allow_cache=srl_request.allow_cache,
            default_cache_ttl=srl_request.default_cache_ttl,
            metadata=srl_request.metadata,
            status="disconnected",  # Initial status
            is_active=True
        )
        db.add(srl_connection)
        db.commit()
        db.refresh(srl_connection)

        # Track metric
        srl_connections_total.inc()

        # Return sanitized response (NO credentials)
        return SRLResponse(
            id=srl_connection.id,
            substrate_identity=f"0x{substrate.identity:016X}",
            name=srl_connection.name,
            resource_type=srl_connection.resource_type,
            status=srl_connection.status,
            created_at=srl_connection.created_at.isoformat(),
            last_used_at=srl_connection.last_used_at.isoformat() if srl_connection.last_used_at else None,
            fetch_count=srl_connection.fetch_count,
            is_active=srl_connection.is_active
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to register SRL: {str(e)}"
        )


@app.get("/api/v1/srl", response_model=SRLListResponse)
@limiter.limit("100/minute")
async def list_srl_connections(
    request: Request,
    resource_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List user's SRL connections.

    SECURITY: Only returns connections owned by current user.
    """
    try:
        from server.database import SRLConnectionModel, SubstrateModel

        # Query user's connections
        query = db.query(SRLConnectionModel).filter(
            SRLConnectionModel.user_id == current_user.id
        )

        # Apply filters
        if resource_type:
            query = query.filter(SRLConnectionModel.resource_type == resource_type)
        if status_filter:
            query = query.filter(SRLConnectionModel.status == status_filter)

        connections = query.all()

        # Convert to response models (sanitized)
        srls = []
        for conn in connections:
            substrate = db.query(SubstrateModel).filter(SubstrateModel.id == conn.substrate_id).first()

            srls.append(SRLResponse(
                id=conn.id,
                substrate_identity=f"0x{substrate.identity:016X}" if substrate else "0x0000000000000000",
                name=conn.name,
                resource_type=conn.resource_type,
                status=conn.status,
                created_at=conn.created_at.isoformat(),
                last_used_at=conn.last_used_at.isoformat() if conn.last_used_at else None,
                fetch_count=conn.fetch_count,
                is_active=conn.is_active
            ))

        return SRLListResponse(
            srls=srls,
            total=len(srls)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list SRL connections: {str(e)}"
        )


@app.post("/api/v1/srl/{srl_id}/fetch", response_model=SRLFetchResponse)
@limiter.limit("100/minute")
async def fetch_from_srl(
    request: Request,
    srl_id: int,
    fetch_request: SRLFetchRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Fetch data through SRL connection.

    PHILOSOPHY:
    - Passive fetch (only when invoked)
    - No caching unless explicitly requested
    - Audit trail for all fetches
    """
    import time
    from server.database import SRLConnectionModel, SRLFetchLogModel
    from server.srl_crypto import SRLCrypto
    from server.srl_adapters import get_adapter

    start_time = time.time()

    try:
        # Get SRL connection (verify ownership)
        srl_conn = db.query(SRLConnectionModel).filter(
            SRLConnectionModel.id == srl_id,
            SRLConnectionModel.user_id == current_user.id
        ).first()

        if not srl_conn:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SRL connection not found"
            )

        if not srl_conn.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"SRL connection is {srl_conn.status}"
            )

        # Decrypt credentials
        crypto = SRLCrypto()
        credentials = None
        if srl_conn.encrypted_credentials:
            credentials = crypto.decrypt_credentials(srl_conn.encrypted_credentials)

        # Get adapter for protocol
        adapter = get_adapter(
            protocol=srl_conn.protocol,
            connection_string=srl_conn.connection_string,
            credentials=credentials,
            config=srl_conn.config or {}
        )

        # Update status to connecting
        srl_conn.status = "connecting"
        db.commit()

        # Fetch data
        result = adapter.fetch(
            query=fetch_request.query,
            parameters=fetch_request.parameters or {}
        )

        # Update status to connected
        srl_conn.status = "connected"
        srl_conn.last_used_at = datetime.utcnow()
        srl_conn.fetch_count += 1

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log fetch
        fetch_log = SRLFetchLogModel(
            connection_id=srl_conn.id,
            user_id=current_user.id,
            query=fetch_request.query,
            parameters=fetch_request.parameters,
            success=True,
            result_size_bytes=len(str(result)) if result else 0,
            cached=False,
            duration_ms=duration_ms
        )
        db.add(fetch_log)
        db.commit()

        # Track metric
        srl_fetches_total.inc()

        return SRLFetchResponse(
            success=True,
            data=result,
            metadata={
                "connection_id": srl_conn.id,
                "protocol": srl_conn.protocol,
                "resource_type": srl_conn.resource_type
            },
            cached=False,
            duration_ms=duration_ms
        )

    except HTTPException:
        raise
    except Exception as e:
        # Update status to disconnected on error
        if 'srl_conn' in locals():
            srl_conn.status = "disconnected"
            db.commit()

        # Log failed fetch
        duration_ms = (time.time() - start_time) * 1000
        fetch_log = SRLFetchLogModel(
            connection_id=srl_id,
            user_id=current_user.id,
            query=fetch_request.query,
            parameters=fetch_request.parameters,
            success=False,
            error_message=str(e),
            duration_ms=duration_ms
        )
        db.add(fetch_log)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch from SRL: {str(e)}"
        )


@app.put("/api/v1/srl/{srl_id}/credentials", response_model=SRLResponse)
@limiter.limit("10/minute")
async def update_srl_credentials(
    request: Request,
    srl_id: int,
    credentials_request: UpdateCredentialsRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update SRL credentials.

    SECURITY: Credentials are encrypted before storage.
    """
    try:
        from server.database import SRLConnectionModel, SubstrateModel
        from server.srl_crypto import SRLCrypto

        # Get SRL connection (verify ownership)
        srl_conn = db.query(SRLConnectionModel).filter(
            SRLConnectionModel.id == srl_id,
            SRLConnectionModel.user_id == current_user.id
        ).first()

        if not srl_conn:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SRL connection not found"
            )

        # Encrypt new credentials
        crypto = SRLCrypto()
        encrypted_credentials = crypto.encrypt_credentials(credentials_request.credentials)

        # Update credentials
        srl_conn.encrypted_credentials = encrypted_credentials
        db.commit()
        db.refresh(srl_conn)

        # Get substrate
        substrate = db.query(SubstrateModel).filter(SubstrateModel.id == srl_conn.substrate_id).first()

        # Return sanitized response
        return SRLResponse(
            id=srl_conn.id,
            substrate_identity=f"0x{substrate.identity:016X}" if substrate else "0x0000000000000000",
            name=srl_conn.name,
            resource_type=srl_conn.resource_type,
            status=srl_conn.status,
            created_at=srl_conn.created_at.isoformat(),
            last_used_at=srl_conn.last_used_at.isoformat() if srl_conn.last_used_at else None,
            fetch_count=srl_conn.fetch_count,
            is_active=srl_conn.is_active
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update credentials: {str(e)}"
        )


@app.post("/api/v1/srl/{srl_id}/test", response_model=SRLTestResponse)
@limiter.limit("10/minute")
async def test_srl_connection(
    request: Request,
    srl_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Test SRL connection without fetching data.

    PHILOSOPHY: Verify connection is valid before actual fetch.
    """
    import time
    from server.database import SRLConnectionModel
    from server.srl_crypto import SRLCrypto
    from server.srl_adapters import get_adapter

    start_time = time.time()

    try:
        # Get SRL connection (verify ownership)
        srl_conn = db.query(SRLConnectionModel).filter(
            SRLConnectionModel.id == srl_id,
            SRLConnectionModel.user_id == current_user.id
        ).first()

        if not srl_conn:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SRL connection not found"
            )

        # Decrypt credentials
        crypto = SRLCrypto()
        credentials = None
        if srl_conn.encrypted_credentials:
            credentials = crypto.decrypt_credentials(srl_conn.encrypted_credentials)

        # Get adapter
        adapter = get_adapter(
            protocol=srl_conn.protocol,
            connection_string=srl_conn.connection_string,
            credentials=credentials,
            config=srl_conn.config or {}
        )

        # Test connection
        test_result = adapter.test_connection()

        # Update status based on test result
        if test_result:
            srl_conn.status = "connected"
            message = "Connection successful"
        else:
            srl_conn.status = "disconnected"
            message = "Connection failed"

        db.commit()

        duration_ms = (time.time() - start_time) * 1000

        return SRLTestResponse(
            success=test_result,
            status=srl_conn.status,
            message=message,
            duration_ms=duration_ms
        )

    except HTTPException:
        raise
    except Exception as e:
        # Update status to disconnected on error
        if 'srl_conn' in locals():
            srl_conn.status = "disconnected"
            db.commit()

        duration_ms = (time.time() - start_time) * 1000

        return SRLTestResponse(
            success=False,
            status="disconnected",
            message=str(e),
            duration_ms=duration_ms
        )


@app.get("/api/v1/srl/{srl_id}/logs", response_model=SRLFetchLogsResponse)
@limiter.limit("100/minute")
async def get_srl_fetch_logs(
    request: Request,
    srl_id: int,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get fetch logs for an SRL connection.

    SECURITY: Only returns logs for connections owned by current user.
    """
    try:
        from server.database import SRLConnectionModel, SRLFetchLogModel

        # Verify ownership
        srl_conn = db.query(SRLConnectionModel).filter(
            SRLConnectionModel.id == srl_id,
            SRLConnectionModel.user_id == current_user.id
        ).first()

        if not srl_conn:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SRL connection not found"
            )

        # Get logs
        logs_query = db.query(SRLFetchLogModel).filter(
            SRLFetchLogModel.connection_id == srl_id
        ).order_by(SRLFetchLogModel.fetched_at.desc())

        total = logs_query.count()
        logs = logs_query.limit(limit).offset(offset).all()

        # Convert to response models
        log_responses = [
            SRLFetchLogResponse(
                id=log.id,
                connection_id=log.connection_id,
                success=log.success,
                result_size_bytes=log.result_size_bytes,
                result_rows=log.result_rows,
                cached=log.cached,
                duration_ms=log.duration_ms,
                error_message=log.error_message,
                fetched_at=log.fetched_at.isoformat()
            )
            for log in logs
        ]

        return SRLFetchLogsResponse(
            logs=log_responses,
            total=total
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get fetch logs: {str(e)}"
        )


@app.put("/api/v1/srl/{srl_id}/status")
@limiter.limit("10/minute")
async def update_srl_status(
    request: Request,
    srl_id: int,
    new_status: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update SRL connection status.

    Allowed statuses: disabled, blacklisted
    (connected/disconnected are set automatically)
    """
    try:
        from server.database import SRLConnectionModel, SubstrateModel

        # Validate status
        allowed_statuses = ["disabled", "blacklisted"]
        if new_status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Allowed: {allowed_statuses}"
            )

        # Get SRL connection (verify ownership)
        srl_conn = db.query(SRLConnectionModel).filter(
            SRLConnectionModel.id == srl_id,
            SRLConnectionModel.user_id == current_user.id
        ).first()

        if not srl_conn:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SRL connection not found"
            )

        # Update status
        srl_conn.status = new_status
        srl_conn.is_active = (new_status not in ["disabled", "blacklisted"])
        db.commit()
        db.refresh(srl_conn)

        # Get substrate
        substrate = db.query(SubstrateModel).filter(SubstrateModel.id == srl_conn.substrate_id).first()

        # Return sanitized response
        return SRLResponse(
            id=srl_conn.id,
            substrate_identity=f"0x{substrate.identity:016X}" if substrate else "0x0000000000000000",
            name=srl_conn.name,
            resource_type=srl_conn.resource_type,
            status=srl_conn.status,
            created_at=srl_conn.created_at.isoformat(),
            last_used_at=srl_conn.last_used_at.isoformat() if srl_conn.last_used_at else None,
            fetch_count=srl_conn.fetch_count,
            is_active=srl_conn.is_active
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update status: {str(e)}"
        )


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("🦋 ButterflyFx Server shutting down...")
    cache.close()
    print("👋 Goodbye!")



