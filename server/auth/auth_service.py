"""
Authentication Service for DimensionOS Platform.

Privacy-first authentication:
- Client sends anonymous user ID (SHA256 hash of email)
- Server never sees real email or personal data
- All authentication via anonymous IDs
"""

import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from server.models.user import User, UserTier, ServiceStatus, ResourceAllocation
from server.auth.password_utils import hash_password, verify_password
from server.auth.jwt_utils import create_access_token, create_refresh_token


def generate_anonymous_id(email: str) -> str:
    """
    Generate anonymous user ID from email.
    
    Uses SHA256 hash to create anonymous identifier.
    Server never stores the real email.
    
    Args:
        email: User's email address (client-side only)
    
    Returns:
        64-character hex string (SHA256 hash)
    """
    return hashlib.sha256(email.encode()).hexdigest()


def register_user(
    db: Session,
    email: str,
    password: str,
    tier: UserTier = UserTier.FREE
) -> Dict[str, Any]:
    """
    Register a new user.
    
    Privacy-first:
    - Email is hashed to create anonymous user_id
    - Password is hashed with bcrypt
    - Server never stores email or plain password
    
    Args:
        db: Database session
        email: User's email (will be hashed)
        password: User's password (will be hashed)
        tier: User tier (default: FREE)
    
    Returns:
        Dict with user_id, access_token, refresh_token
    
    Raises:
        HTTPException: If user already exists
    """
    # Generate anonymous user ID
    user_id = generate_anonymous_id(email)
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.user_id == user_id).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    # Get resource allocation for tier
    allocation = db.query(ResourceAllocation).filter(
        ResourceAllocation.tier == tier
    ).first()
    
    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resource allocation not found for tier: {tier}"
        )
    
    # Create user
    user = User(
        user_id=user_id,
        password_hash=hash_password(password),
        tier=tier,
        service_status=ServiceStatus.ACTIVE,
        created_at=datetime.utcnow(),
        
        # Set trial end date for free tier
        trial_ends_at=datetime.utcnow() + timedelta(days=allocation.trial_days) if allocation.trial_days else None,
        
        # Allocate resources based on tier
        cpu_cores_allocated=allocation.cpu_cores,
        ram_gb_allocated=allocation.ram_gb,
        storage_gb_allocated=allocation.storage_gb,
        bandwidth_allocated=allocation.bandwidth,
        
        # Initialize usage to zero
        cpu_hours_used=0.0,
        ram_gb_hours_used=0.0,
        storage_gb_used=0.0,
        bandwidth_gb_used=0.0,
        
        # Initialize TOS compliance
        tos_violations=0,
        tos_violation_flags=[]
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate tokens
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})
    
    return {
        "user_id": user_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "tier": tier.value,
        "service_status": user.service_status.value,
        "trial_ends_at": user.trial_ends_at.isoformat() if user.trial_ends_at else None
    }


def login_user(
    db: Session,
    email: str,
    password: str
) -> Dict[str, Any]:
    """
    Login user and return JWT tokens.
    
    Args:
        db: Database session
        email: User's email (will be hashed to find user)
        password: User's password
    
    Returns:
        Dict with user_id, access_token, refresh_token
    
    Raises:
        HTTPException: If credentials are invalid
    """
    # Generate anonymous user ID from email
    user_id = generate_anonymous_id(email)
    
    # Find user
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check service status
    if user.service_status == ServiceStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account suspended - payment required"
        )
    
    if user.service_status == ServiceStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account cancelled"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Generate tokens
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})
    
    return {
        "user_id": user_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "tier": user.tier.value,
        "service_status": user.service_status.value
    }

