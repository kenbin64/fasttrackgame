"""
JWT token generation and validation utilities.

Uses python-jose for JWT handling.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status


# JWT configuration
SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "CHANGE_THIS_IN_PRODUCTION_TO_RANDOM_SECRET_KEY_MIN_32_CHARS"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 days


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Data to encode in token (must include 'sub' for user_id)
        expires_delta: Optional custom expiration time
    
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create JWT refresh token.
    
    Args:
        data: Data to encode in token (must include 'sub' for user_id)
    
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token(token: str, token_type: str = "access") -> str:
    """
    Verify token and extract user_id.
    
    Args:
        token: JWT token string
        token_type: Expected token type ('access' or 'refresh')
    
    Returns:
        User ID from token
    
    Raises:
        HTTPException: If token is invalid
    """
    payload = decode_token(token)
    
    # Check token type
    if payload.get("type") != token_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type. Expected {token_type}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user ID
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


def refresh_access_token(refresh_token: str) -> str:
    """
    Generate new access token from refresh token.
    
    Args:
        refresh_token: Valid refresh token
    
    Returns:
        New access token
    
    Raises:
        HTTPException: If refresh token is invalid
    """
    user_id = verify_token(refresh_token, token_type="refresh")
    return create_access_token({"sub": user_id})

