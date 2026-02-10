"""
User models for DimensionOS platform.

Privacy-first architecture:
- NO PII stored on server
- Only anonymous user IDs (SHA256 hashes)
- Only service status and payment status
- All personal data on client side
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ServiceStatus(str, Enum):
    """Service status for user account."""
    ACTIVE = "active"           # Full access
    READ_ONLY = "read_only"     # Grace period - can read, can't write
    SUSPENDED = "suspended"     # No access - payment overdue
    CANCELLED = "cancelled"     # Account closed by user


class UserTier(str, Enum):
    """User subscription tier."""
    FREE = "free"               # 30-day trial
    STARTER = "starter"         # $10/month
    PRO = "pro"                 # $50/month
    ENTERPRISE = "enterprise"   # Custom pricing


class User(Base):
    """
    User model - Privacy-first design.
    
    Stores ONLY:
    - Anonymous user ID (SHA256 hash of email)
    - Password hash (bcrypt)
    - Service status
    - Payment status
    - Resource usage metrics
    
    Does NOT store:
    - Real name
    - Email address
    - Phone number
    - Billing address
    - Credit card info
    - Any PII
    """
    __tablename__ = "users"
    
    # Primary key - Anonymous user ID (SHA256 hash)
    user_id = Column(String(64), primary_key=True, index=True)
    
    # Authentication
    password_hash = Column(String(60), nullable=False)  # bcrypt hash
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret_hash = Column(String(255), nullable=True)  # Encrypted TOTP secret
    
    # Service management
    service_status = Column(SQLEnum(ServiceStatus), default=ServiceStatus.ACTIVE, nullable=False)
    tier = Column(SQLEnum(UserTier), default=UserTier.FREE, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    trial_ends_at = Column(DateTime, nullable=True)  # For free tier
    
    # Payment status (NO payment details!)
    payment_status = Column(String(20), default="unpaid")  # 'paid' or 'unpaid'
    last_payment_date = Column(DateTime, nullable=True)
    next_payment_due = Column(DateTime, nullable=True)
    
    # Resource allocation (based on tier)
    cpu_cores_allocated = Column(Integer, default=1)
    ram_gb_allocated = Column(Integer, default=4)
    storage_gb_allocated = Column(Integer, default=10)
    bandwidth_allocated = Column(String(20), default="1Gbps")
    
    # Resource usage (metrics only - NO content!)
    cpu_hours_used = Column(Float, default=0.0)
    ram_gb_hours_used = Column(Float, default=0.0)
    storage_gb_used = Column(Float, default=0.0)
    bandwidth_gb_used = Column(Float, default=0.0)
    
    # TOS compliance (flags only - NO content!)
    tos_violations = Column(Integer, default=0)
    tos_violation_flags = Column(JSON, default=list)  # List of violation types
    
    # Metadata
    substrate_id = Column(String(16), nullable=True)  # 64-bit substrate identity (hex)
    
    def __repr__(self):
        return f"<User(user_id={self.user_id[:8]}..., tier={self.tier}, status={self.service_status})>"
    
    def is_active(self) -> bool:
        """Check if user has active service."""
        return self.service_status == ServiceStatus.ACTIVE
    
    def is_trial_expired(self) -> bool:
        """Check if free trial has expired."""
        if self.tier != UserTier.FREE:
            return False
        if self.trial_ends_at is None:
            return False
        return datetime.utcnow() > self.trial_ends_at
    
    def is_payment_overdue(self) -> bool:
        """Check if payment is overdue."""
        if self.tier == UserTier.FREE:
            return False
        if self.next_payment_due is None:
            return False
        return datetime.utcnow() > self.next_payment_due
    
    def days_overdue(self) -> int:
        """Get number of days payment is overdue."""
        if not self.is_payment_overdue():
            return 0
        return (datetime.utcnow() - self.next_payment_due).days
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (for API responses)."""
        return {
            'user_id': self.user_id,
            'service_status': self.service_status.value,
            'tier': self.tier.value,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'payment_status': self.payment_status,
            'resources': {
                'cpu_cores': self.cpu_cores_allocated,
                'ram_gb': self.ram_gb_allocated,
                'storage_gb': self.storage_gb_allocated,
                'bandwidth': self.bandwidth_allocated
            },
            'usage': {
                'cpu_hours': self.cpu_hours_used,
                'ram_gb_hours': self.ram_gb_hours_used,
                'storage_gb': self.storage_gb_used,
                'bandwidth_gb': self.bandwidth_gb_used
            }
        }


class ResourceAllocation(Base):
    """
    Resource allocation per tier.
    Defines what resources each tier gets.
    """
    __tablename__ = "resource_allocations"
    
    tier = Column(SQLEnum(UserTier), primary_key=True)
    
    # Resource limits
    cpu_cores = Column(Integer, nullable=False)
    ram_gb = Column(Integer, nullable=False)
    storage_gb = Column(Integer, nullable=False)
    bandwidth = Column(String(20), nullable=False)
    database_type = Column(String(50), nullable=False)
    
    # Features
    ai_assistant = Column(Boolean, default=False)
    analytics = Column(Boolean, default=False)
    custom_domains = Column(Boolean, default=False)
    priority_support = Column(Boolean, default=False)
    
    # Pricing
    price_per_month = Column(Float, nullable=False)
    trial_days = Column(Integer, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'tier': self.tier.value,
            'resources': {
                'cpu_cores': self.cpu_cores,
                'ram_gb': self.ram_gb,
                'storage_gb': self.storage_gb,
                'bandwidth': self.bandwidth,
                'database': self.database_type
            },
            'features': {
                'ai_assistant': self.ai_assistant,
                'analytics': self.analytics,
                'custom_domains': self.custom_domains,
                'priority_support': self.priority_support
            },
            'pricing': {
                'price_per_month': self.price_per_month,
                'trial_days': self.trial_days
            }
        }

