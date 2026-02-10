"""
User management API routes for DimensionOS Platform.

Endpoints:
- GET /user/me - Get current user info
- GET /user/status - Get service status
- PUT /user/tier - Update user tier (upgrade/downgrade)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any

from server.database import get_db
from server.models.user import User, UserTier, ServiceStatus, ResourceAllocation
from server.auth import get_current_user, get_active_user


router = APIRouter(prefix="/user", tags=["User Management"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class UserResponse(BaseModel):
    """User information response."""
    user_id: str
    tier: str
    service_status: str
    created_at: str
    last_login: str = None
    trial_ends_at: str = None
    payment_status: str
    next_payment_due: str = None
    resources: Dict[str, Any]
    usage: Dict[str, Any]
    tos_violations: int


class ServiceStatusResponse(BaseModel):
    """Service status response."""
    service_status: str
    is_active: bool
    is_trial_expired: bool
    is_payment_overdue: bool
    days_overdue: int
    message: str


class UpdateTierRequest(BaseModel):
    """Update user tier request."""
    tier: UserTier


# ============================================================================
# ROUTES
# ============================================================================

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information.
    
    Returns:
    - user_id: Anonymous user ID
    - tier: User tier
    - service_status: Service status
    - resources: Allocated resources
    - usage: Current usage metrics
    - tos_violations: Number of TOS violations
    """
    return current_user.to_dict()


@router.get("/status", response_model=ServiceStatusResponse)
async def get_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get service status for current user.
    
    Returns:
    - service_status: Current service status
    - is_active: Whether service is active
    - is_trial_expired: Whether trial has expired
    - is_payment_overdue: Whether payment is overdue
    - days_overdue: Number of days payment is overdue
    - message: Human-readable status message
    """
    is_active = current_user.is_active()
    is_trial_expired = current_user.is_trial_expired()
    is_payment_overdue = current_user.is_payment_overdue()
    days_overdue = current_user.days_overdue()
    
    # Generate status message
    if current_user.service_status == ServiceStatus.ACTIVE:
        if is_trial_expired:
            message = "Trial expired - please upgrade to continue"
        elif is_payment_overdue:
            message = f"Payment {days_overdue} days overdue - please update payment"
        else:
            message = "Service active"
    elif current_user.service_status == ServiceStatus.READ_ONLY:
        message = f"Read-only mode - payment {days_overdue} days overdue"
    elif current_user.service_status == ServiceStatus.SUSPENDED:
        message = f"Service suspended - payment {days_overdue} days overdue"
    elif current_user.service_status == ServiceStatus.CANCELLED:
        message = "Service cancelled"
    else:
        message = "Unknown status"
    
    return {
        "service_status": current_user.service_status.value,
        "is_active": is_active,
        "is_trial_expired": is_trial_expired,
        "is_payment_overdue": is_payment_overdue,
        "days_overdue": days_overdue,
        "message": message
    }


@router.put("/tier", response_model=UserResponse)
async def update_tier(
    request: UpdateTierRequest,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    """
    Update user tier (upgrade/downgrade).
    
    Args:
    - tier: New tier (free, starter, pro, enterprise)
    
    Returns:
    - Updated user information
    
    Note: This endpoint updates the tier but does NOT process payment.
    Payment is handled client-side via Stripe, and payment status
    is updated via the /payment/status endpoint.
    """
    # Get resource allocation for new tier
    allocation = db.query(ResourceAllocation).filter(
        ResourceAllocation.tier == request.tier
    ).first()
    
    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier: {request.tier}"
        )
    
    # Update user tier and resources
    current_user.tier = request.tier
    current_user.cpu_cores_allocated = allocation.cpu_cores
    current_user.ram_gb_allocated = allocation.ram_gb
    current_user.storage_gb_allocated = allocation.storage_gb
    current_user.bandwidth_allocated = allocation.bandwidth
    
    # If upgrading from free tier, clear trial end date
    if request.tier != UserTier.FREE:
        current_user.trial_ends_at = None
    
    db.commit()
    db.refresh(current_user)
    
    return current_user.to_dict()

