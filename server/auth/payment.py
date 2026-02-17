"""
ButterflyFX Payment & Subscription System
==========================================

LOGIN IS NOT A PAYWALL.
PAYMENT STATUS IS A SEPARATE GATE.

When users access paid features without payment:
→ Show payment required page
→ Display available payment methods
→ Explain what they're trying to access
→ Provide upgrade path

FREE TIERS (No Payment Required)
================================
- ANONYMOUS: Public access
- USER: Open source access (free forever)
- BETA: Free for Kenneth's content (invited testers)
- SUPERUSER: Kenneth (free)

PAID TIERS
==========
- DEV: Requires subscription for premium features
  → Free: Open source + basic API
  → Paid: Premium packages, dev tools, marketplace, sandbox

Payment Methods (Industry Standard)
===================================
- Stripe (credit/debit cards)
- PayPal
- Crypto (optional)

Copyright (c) 2024-2026 Kenneth Bingham
All Rights Reserved
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import IntEnum
from datetime import datetime, timedelta


class PaymentStatus(IntEnum):
    """User's payment status"""
    NOT_REQUIRED = 0     # Free tiers (USER, BETA, SUPERUSER)
    UNPAID = 1           # Has accessed paid features but not paid
    PENDING = 2          # Payment processing
    PAID = 3             # Current subscription active
    EXPIRED = 4          # Subscription lapsed
    CANCELLED = 5        # User cancelled
    REFUNDED = 6         # Payment refunded


class SubscriptionPlan(IntEnum):
    """Available subscription plans"""
    FREE = 0             # Free tier
    DEV_MONTHLY = 1      # Developer monthly
    DEV_YEARLY = 2       # Developer yearly (discount)
    DEV_LIFETIME = 3     # Developer lifetime (one-time)


@dataclass
class PlanDetails:
    """Details of a subscription plan"""
    id: str
    name: str
    plan: SubscriptionPlan
    price_usd: float
    billing_period: str       # "monthly", "yearly", "lifetime"
    description: str
    features: List[str] = field(default_factory=list)
    
    # Discount
    discount_percent: int = 0
    original_price: float = 0.0


# =============================================================================
# SUBSCRIPTION PLANS
# =============================================================================

SUBSCRIPTION_PLANS: Dict[SubscriptionPlan, PlanDetails] = {
    SubscriptionPlan.FREE: PlanDetails(
        id="free",
        name="Free",
        plan=SubscriptionPlan.FREE,
        price_usd=0.0,
        billing_period="forever",
        description="Open source access for everyone",
        features=[
            "Open source downloads",
            "Basic API access",
            "Community forums",
            "Public documentation",
        ],
    ),
    SubscriptionPlan.DEV_MONTHLY: PlanDetails(
        id="dev-monthly",
        name="Developer Monthly",
        plan=SubscriptionPlan.DEV_MONTHLY,
        price_usd=29.0,
        billing_period="monthly",
        description="Full developer access, billed monthly",
        features=[
            "Everything in Free +",
            "Premium packages",
            "Developer tools",
            "Local sandbox",
            "Marketplace submission",
            "API key",
            "Collaboration chat",
            "Dev documentation",
            "Priority support",
        ],
    ),
    SubscriptionPlan.DEV_YEARLY: PlanDetails(
        id="dev-yearly",
        name="Developer Yearly",
        plan=SubscriptionPlan.DEV_YEARLY,
        price_usd=290.0,
        billing_period="yearly",
        description="Full developer access, billed yearly (2 months free)",
        discount_percent=17,
        original_price=348.0,
        features=[
            "Everything in Monthly +",
            "2 months free",
            "Early access to new features",
        ],
    ),
    SubscriptionPlan.DEV_LIFETIME: PlanDetails(
        id="dev-lifetime",
        name="Developer Lifetime",
        plan=SubscriptionPlan.DEV_LIFETIME,
        price_usd=999.0,
        billing_period="lifetime",
        description="One-time payment, lifetime access",
        features=[
            "Everything in Yearly +",
            "Never pay again",
            "Lifetime updates",
            "Founding developer badge",
        ],
    ),
}


@dataclass
class Subscription:
    """User's subscription record"""
    id: str
    user_id: str
    plan: SubscriptionPlan
    status: PaymentStatus
    
    # Dates
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    # Payment
    payment_method: str = ""     # "stripe", "paypal", "crypto"
    payment_id: str = ""         # External payment reference
    amount_paid: float = 0.0
    currency: str = "USD"
    
    # Auto-renew
    auto_renew: bool = True
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        if self.status != PaymentStatus.PAID:
            return False
        if self.plan == SubscriptionPlan.DEV_LIFETIME:
            return True  # Lifetime never expires
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        return True
    
    @property
    def is_expired(self) -> bool:
        """Check if subscription has expired"""
        if self.plan == SubscriptionPlan.DEV_LIFETIME:
            return False
        if self.expires_at and datetime.now() > self.expires_at:
            return True
        return False
    
    @property
    def days_remaining(self) -> int:
        """Days until expiration"""
        if self.plan == SubscriptionPlan.DEV_LIFETIME:
            return 999999
        if not self.expires_at:
            return 0
        delta = self.expires_at - datetime.now()
        return max(0, delta.days)
    
    def activate(self, payment_id: str, payment_method: str, amount: float) -> None:
        """Activate subscription after payment"""
        self.status = PaymentStatus.PAID
        self.started_at = datetime.now()
        self.payment_id = payment_id
        self.payment_method = payment_method
        self.amount_paid = amount
        
        # Set expiration based on plan
        if self.plan == SubscriptionPlan.DEV_MONTHLY:
            self.expires_at = datetime.now() + timedelta(days=30)
        elif self.plan == SubscriptionPlan.DEV_YEARLY:
            self.expires_at = datetime.now() + timedelta(days=365)
        elif self.plan == SubscriptionPlan.DEV_LIFETIME:
            self.expires_at = None  # Never expires
    
    def cancel(self) -> None:
        """Cancel subscription"""
        self.status = PaymentStatus.CANCELLED
        self.cancelled_at = datetime.now()
        self.auto_renew = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plan": self.plan.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "payment_method": self.payment_method,
            "payment_id": self.payment_id,
            "amount_paid": self.amount_paid,
            "currency": self.currency,
            "auto_renew": self.auto_renew,
            "is_active": self.is_active,
            "days_remaining": self.days_remaining,
            "metadata": self.metadata,
        }


# =============================================================================
# PAYMENT REQUIRED PAGE DATA
# =============================================================================

@dataclass
class PaymentRequiredInfo:
    """Information to display on payment required page"""
    feature_name: str
    feature_description: str
    required_plan: SubscriptionPlan
    available_plans: List[PlanDetails]
    current_status: PaymentStatus
    
    # Messages
    title: str = "Upgrade Required"
    message: str = ""
    
    def __post_init__(self):
        if not self.message:
            self.message = f"To access {self.feature_name}, please upgrade to a paid plan."


def get_payment_required_info(feature_id: str, user_status: PaymentStatus) -> PaymentRequiredInfo:
    """Generate payment required page info for a feature"""
    
    # Feature descriptions
    feature_info = {
        "premium_packages": ("Premium Packages", "Download premium development packages"),
        "dev_tools": ("Developer Tools", "Access to advanced developer tools"),
        "local_sandbox": ("Local Sandbox", "Run local development sandbox"),
        "marketplace_submit": ("Marketplace Submission", "Submit apps to the marketplace"),
        "dev_docs": ("Developer Documentation", "Full developer documentation"),
        "collab_chat": ("Collaboration Chat", "Chat with collaborators"),
    }
    
    name, desc = feature_info.get(feature_id, ("Premium Feature", "This feature requires a paid subscription"))
    
    # Get available paid plans
    paid_plans = [
        SUBSCRIPTION_PLANS[SubscriptionPlan.DEV_MONTHLY],
        SUBSCRIPTION_PLANS[SubscriptionPlan.DEV_YEARLY],
        SUBSCRIPTION_PLANS[SubscriptionPlan.DEV_LIFETIME],
    ]
    
    return PaymentRequiredInfo(
        feature_name=name,
        feature_description=desc,
        required_plan=SubscriptionPlan.DEV_MONTHLY,
        available_plans=paid_plans,
        current_status=user_status,
    )


# =============================================================================
# PAYMENT METHODS
# =============================================================================

@dataclass
class PaymentMethod:
    """Available payment method"""
    id: str
    name: str
    icon: str
    description: str
    enabled: bool = True
    processing_fee: float = 0.0      # Percentage
    flat_fee: float = 0.0            # Flat fee per transaction


PAYMENT_METHODS: List[PaymentMethod] = [
    PaymentMethod(
        id="stripe",
        name="Credit/Debit Card",
        icon="💳",
        description="Pay with Visa, Mastercard, Amex via Stripe",
        processing_fee=2.9,
        flat_fee=0.30,
    ),
    PaymentMethod(
        id="paypal",
        name="PayPal",
        icon="🅿️",
        description="Pay with your PayPal account",
        processing_fee=2.9,
        flat_fee=0.30,
    ),
    PaymentMethod(
        id="crypto",
        name="Cryptocurrency",
        icon="₿",
        description="Pay with Bitcoin, Ethereum, or other crypto",
        enabled=False,  # Enable when supported
        processing_fee=1.0,
        flat_fee=0.0,
    ),
]


def get_enabled_payment_methods() -> List[PaymentMethod]:
    """Get list of enabled payment methods"""
    return [pm for pm in PAYMENT_METHODS if pm.enabled]


# =============================================================================
# TIER PAYMENT REQUIREMENTS
# =============================================================================

def requires_payment(tier: int, feature_id: str = None) -> bool:
    """
    Check if a tier/feature requires payment.
    
    FREE (no payment needed):
    - ANONYMOUS (0): Public access
    - USER (1): Open source access
    - BETA (3): Invited testers (free)
    - SUPERUSER (4): Kenneth (free)
    
    PAID:
    - DEV (2): Premium features require payment
    """
    # Free tiers
    if tier in (0, 1, 3, 4):  # ANONYMOUS, USER, BETA, SUPERUSER
        return False
    
    # DEV tier - check specific feature
    if tier == 2:
        # Free dev features
        free_dev_features = {
            "download_opensource",
            "basic_api",
            "community_access",
            "profile",
        }
        if feature_id and feature_id in free_dev_features:
            return False
        # Premium dev features require payment
        return True
    
    return False


def check_payment_gate(user_tier: int, user_payment_status: PaymentStatus, 
                       feature_id: str) -> Optional[PaymentRequiredInfo]:
    """
    Check if user should see payment gate.
    
    Returns PaymentRequiredInfo if payment required, None if access granted.
    """
    # Free tiers - no gate
    if user_tier in (0, 1, 3, 4):
        return None
    
    # DEV tier with active subscription - no gate
    if user_payment_status == PaymentStatus.PAID:
        return None
    
    # DEV tier without payment - check feature
    if requires_payment(user_tier, feature_id):
        return get_payment_required_info(feature_id, user_payment_status)
    
    return None
