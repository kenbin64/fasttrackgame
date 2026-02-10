"""
Authentication API routes for DimensionOS Platform.

Endpoints:
- POST /auth/register - Register new user
- POST /auth/login - Login user
- POST /auth/refresh - Refresh access token
- POST /auth/logout - Logout user (client-side token deletion)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from server.database import get_db
from server.models.user import UserTier
from server.auth import (
    register_user,
    login_user,
    refresh_access_token,
    get_current_user,
    is_password_strong
)


router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    tier: UserTier = UserTier.FREE
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "tier": "free"
            }
        }


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }


class RefreshRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str


class AuthResponse(BaseModel):
    """Authentication response."""
    user_id: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    tier: str
    service_status: str
    trial_ends_at: str = None


class RefreshResponse(BaseModel):
    """Token refresh response."""
    access_token: str
    token_type: str = "bearer"


# ============================================================================
# ROUTES
# ============================================================================

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    Privacy-first:
    - Email is hashed to create anonymous user_id
    - Password is hashed with bcrypt
    - Server never stores email or plain password
    
    Returns:
    - user_id: Anonymous user ID (SHA256 hash)
    - access_token: JWT access token (1 hour)
    - refresh_token: JWT refresh token (30 days)
    - tier: User tier
    - service_status: Service status
    """
    # Validate password strength
    is_strong, error_msg = is_password_strong(request.password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Register user
    result = register_user(
        db=db,
        email=request.email,
        password=request.password,
        tier=request.tier
    )
    
    return result


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login user and return JWT tokens.
    
    Args:
    - email: User's email (will be hashed to find user)
    - password: User's password
    
    Returns:
    - user_id: Anonymous user ID
    - access_token: JWT access token (1 hour)
    - refresh_token: JWT refresh token (30 days)
    - tier: User tier
    - service_status: Service status
    """
    result = login_user(
        db=db,
        email=request.email,
        password=request.password
    )
    
    return result


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(request: RefreshRequest):
    """
    Refresh access token using refresh token.
    
    Args:
    - refresh_token: Valid refresh token
    
    Returns:
    - access_token: New JWT access token (1 hour)
    """
    access_token = refresh_access_token(request.refresh_token)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    """
    Logout user.
    
    Note: JWT tokens are stateless, so logout is handled client-side
    by deleting the tokens. This endpoint is provided for consistency
    and can be used for logging/analytics.
    
    Returns:
    - message: Success message
    """
    return {
        "message": "Logged out successfully",
        "user_id": current_user.user_id
    }

