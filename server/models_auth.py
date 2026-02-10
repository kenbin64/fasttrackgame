"""
Authentication and User Models - Pydantic models for auth/user operations

SECURITY: These models ensure NO source code is ever exposed to clients
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, Dict, Any
from datetime import datetime


# ============================================================================
# AUTHENTICATION MODELS
# ============================================================================

class UserRegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    accept_tos: bool = Field(..., description="Must accept Terms of Service")
    tos_version: str = Field(..., description="TOS version being accepted")
    
    @validator('accept_tos')
    def tos_must_be_accepted(cls, v):
        if not v:
            raise ValueError('You must accept the Terms of Service to register')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "SecurePass123",
                "full_name": "John Doe",
                "accept_tos": True,
                "tos_version": "1.0.0"
            }
        }


class UserLoginRequest(BaseModel):
    """User login request."""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "password": "SecurePass123"
            }
        }


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user: "UserResponse" = Field(..., description="User information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400,
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "username": "johndoe",
                    "full_name": "John Doe",
                    "is_active": True,
                    "created_at": "2026-02-09T12:00:00Z"
                }
            }
        }


class UserResponse(BaseModel):
    """User information response (NO sensitive data)."""
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="Email address")
    username: str = Field(..., description="Username")
    full_name: Optional[str] = Field(None, description="Full name")
    is_active: bool = Field(..., description="Account active status")
    is_verified: bool = Field(..., description="Email verified status")
    created_at: datetime = Field(..., description="Account creation date")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    
    class Config:
        from_attributes = True


class TOSResponse(BaseModel):
    """Terms of Service response."""
    version: str = Field(..., description="TOS version")
    effective_date: str = Field(..., description="Effective date")
    content: str = Field(..., description="TOS content")
    disclaimer: str = Field(..., description="Disclaimers")


class TOSAcceptanceRequest(BaseModel):
    """TOS acceptance request."""
    tos_version: str = Field(..., description="TOS version being accepted")
    accept: bool = Field(..., description="Acceptance confirmation")
    
    @validator('accept')
    def must_accept(cls, v):
        if not v:
            raise ValueError('You must accept the Terms of Service')
        return v


class ChangePasswordRequest(BaseModel):
    """Change password request."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @validator('new_password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str = Field(..., description="Refresh token")



