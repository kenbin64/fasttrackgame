"""
Payment status API routes for DimensionOS Platform.

Privacy-first payment handling:
- Client processes payments via Stripe
- Client sends ONLY payment status to server (NO payment details)
- Server updates service status based on payment status

Endpoints:
- POST /payment/status - Update payment status (from client)
- GET /payment/status - Get payment status
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

from server.database import get_db
from server.models.user import User, ServiceStatus
from server.auth import get_current_user


router = APIRouter(prefix="/payment", tags=["Payment"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class UpdatePaymentStatusRequest(BaseModel):
    """Update payment status request (from client)."""
    payment_status: str  # 'paid' or 'unpaid'
    amount: float  # Amount paid (for logging only - NO details)
    period: str  # Billing period (e.g., '2026-02')
    
    class Config:
        schema_extra = {
            "example": {
                "payment_status": "paid",
                "amount": 10.0,
                "period": "2026-02"
            }
        }


class PaymentStatusResponse(BaseModel):
    """Payment status response."""
    payment_status: str
    last_payment_date: Optional[str]
    next_payment_due: Optional[str]
    service_status: str
    is_payment_overdue: bool
    days_overdue: int


# ============================================================================
# ROUTES
# ============================================================================

@router.post("/status", response_model=PaymentStatusResponse)
async def update_payment_status(
    request: UpdatePaymentStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update payment status (called by client after processing payment).
    
    Privacy-first:
    - Client processes payment via Stripe
    - Client sends ONLY status (paid/unpaid) and amount
    - Server NEVER sees credit card, billing address, or payment details
    
    Args:
    - payment_status: 'paid' or 'unpaid'
    - amount: Amount paid (for logging only)
    - period: Billing period (e.g., '2026-02')
    
    Returns:
    - Updated payment status
    - Service status
    """
    # Update payment status
    current_user.payment_status = request.payment_status
    
    if request.payment_status == "paid":
        # Payment received - activate service
        current_user.service_status = ServiceStatus.ACTIVE
        current_user.last_payment_date = datetime.utcnow()
        
        # Set next payment due date (30 days from now)
        current_user.next_payment_due = datetime.utcnow() + timedelta(days=30)
        
    else:
        # Payment failed or unpaid
        # Service status will be updated by background job based on days overdue
        pass
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "payment_status": current_user.payment_status,
        "last_payment_date": current_user.last_payment_date.isoformat() if current_user.last_payment_date else None,
        "next_payment_due": current_user.next_payment_due.isoformat() if current_user.next_payment_due else None,
        "service_status": current_user.service_status.value,
        "is_payment_overdue": current_user.is_payment_overdue(),
        "days_overdue": current_user.days_overdue()
    }


@router.get("/status", response_model=PaymentStatusResponse)
async def get_payment_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get payment status for current user.
    
    Returns:
    - payment_status: 'paid' or 'unpaid'
    - last_payment_date: Last payment date
    - next_payment_due: Next payment due date
    - service_status: Current service status
    - is_payment_overdue: Whether payment is overdue
    - days_overdue: Number of days payment is overdue
    """
    return {
        "payment_status": current_user.payment_status,
        "last_payment_date": current_user.last_payment_date.isoformat() if current_user.last_payment_date else None,
        "next_payment_due": current_user.next_payment_due.isoformat() if current_user.next_payment_due else None,
        "service_status": current_user.service_status.value,
        "is_payment_overdue": current_user.is_payment_overdue(),
        "days_overdue": current_user.days_overdue()
    }

