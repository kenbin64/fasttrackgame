"""
FastAPI dependencies for authentication.

Provides dependency injection for:
- Current user
- Active user
- Service status checking
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from server.database import get_db
from server.models.user import User, ServiceStatus
from server.auth.jwt_utils import verify_token


# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
    
    Returns:
        User object
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    # Verify token and extract user_id
    user_id = verify_token(token, token_type="access")
    
    # Get user from database
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and verify service is active.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User object
    
    Raises:
        HTTPException: If service is not active
    """
    if current_user.service_status == ServiceStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Service suspended - payment required"
        )
    
    if current_user.service_status == ServiceStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Service cancelled"
        )
    
    if current_user.service_status == ServiceStatus.READ_ONLY:
        # Allow read-only access but include warning in response
        # This is handled at the route level
        pass
    
    return current_user


async def get_full_access_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and verify full access (not read-only).
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User object
    
    Raises:
        HTTPException: If service is not fully active
    """
    if current_user.service_status != ServiceStatus.ACTIVE:
        if current_user.service_status == ServiceStatus.READ_ONLY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account in read-only mode - payment overdue"
            )
        elif current_user.service_status == ServiceStatus.SUSPENDED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Service suspended - payment required"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Service not active"
            )
    
    return current_user


async def check_trial_status(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Check if user's trial has expired.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User object
    
    Raises:
        HTTPException: If trial has expired
    """
    if current_user.is_trial_expired():
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Free trial expired - please upgrade to continue"
        )
    
    return current_user


async def check_payment_status(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Check if user's payment is overdue.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User object (with warning if payment is overdue)
    """
    if current_user.is_payment_overdue():
        days_overdue = current_user.days_overdue()
        
        if days_overdue > 7:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Payment {days_overdue} days overdue - service suspended"
            )
        elif days_overdue > 3:
            # Read-only mode
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Payment {days_overdue} days overdue - read-only mode"
            )
        # else: Grace period - allow full access but include warning
    
    return current_user

