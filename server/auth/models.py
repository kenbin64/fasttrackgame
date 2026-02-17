"""
ButterflyFX User Authentication Models
=======================================

WEBSITE & DOWNLOAD PERMISSIONS ONLY
====================================

These roles govern access to:
- butterflyfx.us website features
- Package downloads from the VPS
- Hosted services and APIs

DIMENSIONAL ROLE HIERARCHY:

    SUPERUSER (4) - All permissions + admin/system management
        |
    BETA (3)      - All DEV perms + beta features + free production forever
        |             NOTE: Beta benefits ONLY apply to Kenneth/superuser
        |             created content, NOT dev submissions
        |
    DEV (2)       - All USER perms + dev packages + premium access
        |
    USER (1)      - All PUBLIC perms + open source downloads + API access
        |
    ANONYMOUS (0) - Public access only, no downloads

ZERO TRUST FOR DOWNLOADED APPS
==============================

Downloaded/installed software uses ZERO TRUST:
- Apps do NOT inherit website roles
- Users define their own local role systems
- Default local role: ADMIN (for the person who downloaded)
- Devs can implement custom role systems in their apps

Beta designation:
- Applies ONLY to content created by Kenneth/superuser
- Does NOT grant free access to dev-submitted content
- Devs set their own pricing for their submissions

Copyright (c) 2024-2026 Kenneth Bingham
All Rights Reserved
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from enum import IntEnum, auto
from datetime import datetime, timedelta
import hashlib
import secrets
import json
import os
import time


class UserTier(IntEnum):
    """User tiers - higher number = more access"""
    ANONYMOUS = 0    # Not logged in
    USER = 1         # Basic users - open source only
    DEV = 2          # Developers - free/premium dev packages
    BETA = 3         # Beta testers - full access, free forever
    SUPERUSER = 4    # Kenneth Bingham - full access, supreme control


class AccessLevel(IntEnum):
    """Access levels for resources"""
    PUBLIC = 0       # Anyone can access (open source docs, etc.)
    OPEN_SOURCE = 1  # Logged in users (open source packages)
    DEV = 2          # Developer tier (dev tools, premium packages)
    BETA = 3         # Beta tier (unreleased features)
    SUPERUSER = 4    # Superuser only (admin, system config)


@dataclass
class UserPermissions:
    """Detailed permissions for a user"""
    # Download permissions
    can_download_opensource: bool = True
    can_download_dev_packages: bool = False
    can_download_premium: bool = False
    can_download_beta: bool = False
    can_download_source: bool = False
    
    # Access permissions
    can_access_admin: bool = False
    can_access_api: bool = False
    can_access_dev_tools: bool = False
    can_access_beta_features: bool = False
    can_access_superuser_panel: bool = False
    
    # Management permissions
    can_manage_users: bool = False
    can_manage_packages: bool = False
    can_manage_licenses: bool = False
    can_manage_system: bool = False
    
    # Free tier access
    has_free_production: bool = False
    bypass_licensing: bool = False
    
    @classmethod
    def for_tier(cls, tier: UserTier) -> 'UserPermissions':
        """
        Create permissions based on user tier using DIMENSIONAL INHERITANCE.
        
        Each tier inherits ALL permissions from the tier below it.
        This ensures that higher tiers can always do what lower tiers can do.
        """
        # Start with minimal permissions
        perms = cls()
        
        # DIMENSIONAL INHERITANCE: Each tier adds to the previous
        
        # Tier >= ANONYMOUS (0): Public access only
        # Nothing to add - defaults are restrictive
        
        # Tier >= USER (1): Add user capabilities
        if tier >= UserTier.USER:
            perms.can_download_opensource = True
            perms.can_access_api = True
        
        # Tier >= DEV (2): Add developer capabilities (inherits USER)
        if tier >= UserTier.DEV:
            perms.can_download_dev_packages = True
            perms.can_download_premium = True
            perms.can_access_dev_tools = True
        
        # Tier >= BETA (3): Add beta capabilities (inherits DEV + USER)
        if tier >= UserTier.BETA:
            perms.can_download_beta = True
            perms.can_download_source = True
            perms.can_access_beta_features = True
            perms.has_free_production = True
            perms.bypass_licensing = True
        
        # Tier >= SUPERUSER (4): Add superuser capabilities (inherits ALL)
        if tier >= UserTier.SUPERUSER:
            perms.can_access_admin = True
            perms.can_access_superuser_panel = True
            perms.can_manage_users = True
            perms.can_manage_packages = True
            perms.can_manage_licenses = True
            perms.can_manage_system = True
        
        return perms


@dataclass
class User:
    """User account with tier-based access"""
    id: str
    username: str
    email: str
    password_hash: str
    tier: UserTier
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    is_active: bool = True
    is_verified: bool = False
    
    # Profile
    display_name: str = ""
    avatar_url: str = ""
    bio: str = ""
    
    # API Key (for DEV and BETA tiers)
    api_key: str = ""
    api_key_created: Optional[datetime] = None
    
    # TOS Acceptance
    tos_accepted: bool = False
    tos_accepted_at: Optional[datetime] = None
    tos_version: str = ""
    dev_tos_accepted: bool = False
    dev_tos_accepted_at: Optional[datetime] = None
    beta_tos_accepted: bool = False
    beta_tos_accepted_at: Optional[datetime] = None
    
    # Subscription
    subscription_expires: Optional[datetime] = None
    subscription_type: str = "free"
    
    # Beta program
    beta_joined: Optional[datetime] = None
    beta_code: str = ""
    beta_invited_by: str = ""  # superuser who invited them
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.display_name:
            self.display_name = self.username
    
    @property
    def permissions(self) -> UserPermissions:
        """Get permissions for this user's tier"""
        return UserPermissions.for_tier(self.tier)
    
    @property
    def is_superuser(self) -> bool:
        return self.tier >= UserTier.SUPERUSER
    
    @property
    def is_beta(self) -> bool:
        """True if user has beta-level access (BETA or higher)"""
        return self.tier >= UserTier.BETA
    
    @property
    def is_dev(self) -> bool:
        """True if user has dev-level access (DEV or higher)"""
        return self.tier >= UserTier.DEV
    
    @property
    def is_user(self) -> bool:
        """True if user has basic user access (USER or higher)"""
        return self.tier >= UserTier.USER
    
    def has_at_least(self, required_tier: UserTier) -> bool:
        """
        Dimensional access check: Does user have at least this tier level?
        
        Higher tiers can do everything lower tiers can do.
        Example: SUPERUSER.has_at_least(USER) = True
        """
        return self.tier >= required_tier
    
    @property
    def tier_name(self) -> str:
        return self.tier.name.lower()
    
    @property
    def tier_badge(self) -> str:
        badges = {
            UserTier.SUPERUSER: "👑",
            UserTier.BETA: "🧪",
            UserTier.DEV: "⚙️",
            UserTier.USER: "👤",
            UserTier.ANONYMOUS: "👻",
        }
        return badges.get(self.tier, "❓")
    
    @property
    def has_api_key(self) -> bool:
        return bool(self.api_key)
    
    @property
    def requires_api_key(self) -> bool:
        return self.tier in (UserTier.DEV, UserTier.BETA)
    
    def generate_api_key(self) -> str:
        """
        Generate a new API key for this user (ONE-TIME ONLY).
        
        API keys are single-use and permanent. Once generated at registration,
        they cannot be regenerated. If a key already exists, this method
        raises an error.
        
        Raises:
            ValueError: If user already has an API key
        """
        # Enforce single-use: cannot regenerate existing key
        if self.api_key:
            raise ValueError(f"API key already exists for user {self.username}. Keys are single-use and cannot be regenerated.")
        
        prefix = "bfx"
        tier_code = {
            UserTier.SUPERUSER: "su",
            UserTier.BETA: "bt",
            UserTier.DEV: "dv",
            UserTier.USER: "us",
        }.get(self.tier, "xx")
        
        # Format: bfx_<tier>_<random>
        self.api_key = f"{prefix}_{tier_code}_{secrets.token_urlsafe(32)}"
        self.api_key_created = datetime.now()
        return self.api_key
    
    def revoke_api_key(self) -> None:
        """
        Revoke the current API key (SUPERUSER ACTION ONLY).
        
        Once revoked, the key is permanently invalidated. There is no
        way to regenerate - the user loses API access forever.
        """
        self.api_key = ""
        self.api_key_created = None
    
    def accept_tos(self, version: str = "1.0") -> None:
        """Accept general Terms of Service"""
        self.tos_accepted = True
        self.tos_accepted_at = datetime.now()
        self.tos_version = version
    
    def accept_dev_tos(self) -> None:
        """Accept Developer Terms of Service"""
        self.dev_tos_accepted = True
        self.dev_tos_accepted_at = datetime.now()
    
    def accept_beta_tos(self) -> None:
        """Accept Beta Tester Terms of Service"""
        self.beta_tos_accepted = True
        self.beta_tos_accepted_at = datetime.now()
    
    def can_access(self, required_level: AccessLevel) -> bool:
        """
        Dimensional access check for resources.
        
        Returns True if user's tier >= required access level.
        Higher tiers can access everything lower tiers can.
        """
        return self.tier >= required_level
    
    def can_download(self, package_type: str) -> bool:
        """Check if user can download a package type"""
        perms = self.permissions
        
        if package_type == "opensource":
            return perms.can_download_opensource
        elif package_type == "dev":
            return perms.can_download_dev_packages
        elif package_type == "premium":
            return perms.can_download_premium
        elif package_type == "beta":
            return perms.can_download_beta
        elif package_type == "source":
            return perms.can_download_source
        
        return False
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email if include_sensitive else self.email[:3] + "***",
            "tier": self.tier_name,
            "tier_badge": self.tier_badge,
            "display_name": self.display_name,
            "avatar_url": self.avatar_url,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat(),
            "has_api_key": self.has_api_key,
            "tos_accepted": self.tos_accepted,
            "dev_tos_accepted": self.dev_tos_accepted,
            "beta_tos_accepted": self.beta_tos_accepted,
            "permissions": {
                k: v for k, v in self.permissions.__dict__.items()
                if not k.startswith('_')
            }
        }
        
        if include_sensitive:
            data["last_login"] = self.last_login.isoformat() if self.last_login else None
            data["subscription_type"] = self.subscription_type
            data["api_key"] = self.api_key
            data["api_key_created"] = self.api_key_created.isoformat() if self.api_key_created else None
            data["tos_accepted_at"] = self.tos_accepted_at.isoformat() if self.tos_accepted_at else None
            data["dev_tos_accepted_at"] = self.dev_tos_accepted_at.isoformat() if self.dev_tos_accepted_at else None
            data["beta_tos_accepted_at"] = self.beta_tos_accepted_at.isoformat() if self.beta_tos_accepted_at else None
            data["beta_invited_by"] = self.beta_invited_by
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary"""
        tier_map = {
            "anonymous": UserTier.ANONYMOUS,
            "user": UserTier.USER,
            "dev": UserTier.DEV,
            "beta": UserTier.BETA,
            "superuser": UserTier.SUPERUSER,
        }
        
        return cls(
            id=data["id"],
            username=data["username"],
            email=data["email"],
            password_hash=data.get("password_hash", ""),
            tier=tier_map.get(data.get("tier", "user"), UserTier.USER),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            last_login=datetime.fromisoformat(data["last_login"]) if data.get("last_login") else None,
            is_active=data.get("is_active", True),
            is_verified=data.get("is_verified", False),
            display_name=data.get("display_name", ""),
            avatar_url=data.get("avatar_url", ""),
            bio=data.get("bio", ""),
            api_key=data.get("api_key", ""),
            api_key_created=datetime.fromisoformat(data["api_key_created"]) if data.get("api_key_created") else None,
            tos_accepted=data.get("tos_accepted", False),
            tos_accepted_at=datetime.fromisoformat(data["tos_accepted_at"]) if data.get("tos_accepted_at") else None,
            tos_version=data.get("tos_version", ""),
            dev_tos_accepted=data.get("dev_tos_accepted", False),
            dev_tos_accepted_at=datetime.fromisoformat(data["dev_tos_accepted_at"]) if data.get("dev_tos_accepted_at") else None,
            beta_tos_accepted=data.get("beta_tos_accepted", False),
            beta_tos_accepted_at=datetime.fromisoformat(data["beta_tos_accepted_at"]) if data.get("beta_tos_accepted_at") else None,
            subscription_expires=datetime.fromisoformat(data["subscription_expires"]) if data.get("subscription_expires") else None,
            subscription_type=data.get("subscription_type", "free"),
            beta_joined=datetime.fromisoformat(data["beta_joined"]) if data.get("beta_joined") else None,
            beta_code=data.get("beta_code", ""),
            beta_invited_by=data.get("beta_invited_by", ""),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Session:
    """User session for authentication"""
    id: str
    user_id: str
    token: str
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=7))
    ip_address: str = ""
    user_agent: str = ""
    is_active: bool = True
    
    @property
    def is_valid(self) -> bool:
        return self.is_active and datetime.now() < self.expires_at
    
    @classmethod
    def create(cls, user_id: str, ip: str = "", user_agent: str = "") -> 'Session':
        """Create a new session"""
        return cls(
            id=secrets.token_hex(16),
            user_id=user_id,
            token=secrets.token_urlsafe(64),
            ip_address=ip,
            user_agent=user_agent,
        )
    
    def refresh(self, days: int = 7) -> None:
        """Extend session expiry"""
        self.expires_at = datetime.now() + timedelta(days=days)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "token": self.token,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "ip_address": self.ip_address,
            "is_active": self.is_active,
        }


@dataclass
class BetaCode:
    """Beta program invitation code"""
    code: str
    created_by: str  # superuser who created it
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    max_uses: int = 1
    uses: int = 0
    used_by: List[str] = field(default_factory=list)
    is_active: bool = True
    
    @property
    def is_valid(self) -> bool:
        if not self.is_active:
            return False
        if self.max_uses > 0 and self.uses >= self.max_uses:
            return False
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        return True
    
    def use(self, user_id: str) -> bool:
        """Mark code as used by a user"""
        if not self.is_valid:
            return False
        self.uses += 1
        self.used_by.append(user_id)
        return True
    
    @classmethod
    def generate(cls, created_by: str, max_uses: int = 1, 
                 expires_days: int = 30) -> 'BetaCode':
        """Generate a new beta code"""
        return cls(
            code=f"BETA-{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}",
            created_by=created_by,
            max_uses=max_uses,
            expires_at=datetime.now() + timedelta(days=expires_days) if expires_days > 0 else None,
        )


# =============================================================================
# TIER EXPLANATIONS
# =============================================================================

TIER_INFO = {
    UserTier.SUPERUSER: {
        "name": "Superuser",
        "badge": "👑",
        "color": "#FFD700",
        "description": "Full system access. Creator/owner tier.",
        "features": [
            "Complete access to all features",
            "System administration",
            "User management",
            "License management",
            "Everything is free",
        ]
    },
    UserTier.BETA: {
        "name": "Beta Tester",
        "badge": "🧪",
        "color": "#9B59B6",
        "description": "Early adopter with full access and free production forever.",
        "features": [
            "All downloads free",
            "Developer source code access",
            "Free production license forever",
            "Early access to unreleased features",
            "Direct feedback channel",
        ]
    },
    UserTier.DEV: {
        "name": "Developer",
        "badge": "⚙️",
        "color": "#3498DB",
        "description": "Developer tier with access to dev tools and premium packages.",
        "features": [
            "Open source downloads",
            "Developer tools access",
            "Premium package downloads",
            "API access",
            "Dev documentation",
        ]
    },
    UserTier.USER: {
        "name": "User",
        "badge": "👤",
        "color": "#2ECC71",
        "description": "Basic user with access to open source packages.",
        "features": [
            "Open source downloads",
            "Basic API access",
            "Community support",
        ]
    },
    UserTier.ANONYMOUS: {
        "name": "Guest",
        "badge": "👻",
        "color": "#95A5A6",
        "description": "Not logged in. Create an account to access downloads.",
        "features": [
            "View documentation",
            "Browse packages",
        ]
    },
}


def get_tier_info(tier: UserTier) -> Dict[str, Any]:
    """Get information about a tier"""
    return TIER_INFO.get(tier, TIER_INFO[UserTier.ANONYMOUS])


# =============================================================================
# INSTANCE ROLES (ZERO TRUST - Local App Permissions)
# =============================================================================
# Downloaded apps use ZERO TRUST - website roles do NOT apply.
# Users define their own local role systems. Default is ADMIN for downloader.
# =============================================================================

class InstanceRole(IntEnum):
    """
    Local instance roles for downloaded/installed apps.
    
    These are SEPARATE from website tiers. Apps use ZERO TRUST:
    - Website roles do NOT grant local access
    - Admins control only their own domains/instances
    - Users can define custom roles in their apps
    """
    GUEST = 0        # Read-only, minimal access
    MEMBER = 1       # Basic participation
    MODERATOR = 2    # Content moderation
    ADMIN = 3        # Full control of this instance (default for downloader)


@dataclass
class InstancePermissions:
    """Permissions for local app instances (Zero Trust)"""
    can_read: bool = True
    can_write: bool = False
    can_delete: bool = False
    can_manage_content: bool = False
    can_manage_users: bool = False
    can_manage_settings: bool = False
    can_manage_roles: bool = False
    is_owner: bool = False
    
    @classmethod
    def for_role(cls, role: InstanceRole, is_owner: bool = False) -> 'InstancePermissions':
        """Create permissions for an instance role"""
        perms = cls()
        
        if role >= InstanceRole.GUEST:
            perms.can_read = True
        
        if role >= InstanceRole.MEMBER:
            perms.can_write = True
        
        if role >= InstanceRole.MODERATOR:
            perms.can_delete = True
            perms.can_manage_content = True
        
        if role >= InstanceRole.ADMIN:
            perms.can_manage_users = True
            perms.can_manage_settings = True
            perms.can_manage_roles = True
        
        if is_owner:
            perms.is_owner = True
        
        return perms


# =============================================================================
# SANDBOX SYSTEM (Beta and Dev testing environments)
# =============================================================================

@dataclass
class Sandbox:
    """
    Isolated sandbox environment for Beta/Dev users on VPS.
    
    - Beta testers get their own sandbox to experiment
    - Can modify code, debug, add features - only affects their sandbox
    - Cannot affect main VPS server or other users
    - Devs get sandbox on their own machines, plus submission access
    """
    id: str
    owner_id: str               # User who owns this sandbox
    owner_tier: UserTier        # BETA or DEV
    name: str
    created_at: datetime = field(default_factory=datetime.now)
    
    # Sandbox location
    is_vps_hosted: bool = False  # True for beta sandboxes on VPS
    path: str = ""               # Local path or VPS path
    
    # Resource limits
    storage_mb: int = 1024       # 1GB default
    memory_mb: int = 512         # 512MB limit
    cpu_percent: int = 25        # 25% CPU max
    
    # Status
    is_active: bool = True
    last_accessed: Optional[datetime] = None
    
    # Metadata
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_for_beta(cls, user_id: str, sandbox_name: str) -> 'Sandbox':
        """Create VPS-hosted sandbox for beta tester"""
        return cls(
            id=f"sandbox-beta-{secrets.token_hex(8)}",
            owner_id=user_id,
            owner_tier=UserTier.BETA,
            name=sandbox_name,
            is_vps_hosted=True,
            path=f"/sandboxes/beta/{user_id}/{sandbox_name}",
            storage_mb=2048,  # 2GB for beta
            memory_mb=1024,   # 1GB for beta
        )
    
    @classmethod
    def create_for_dev(cls, user_id: str, sandbox_name: str) -> 'Sandbox':
        """Create local sandbox reference for developer"""
        return cls(
            id=f"sandbox-dev-{secrets.token_hex(8)}",
            owner_id=user_id,
            owner_tier=UserTier.DEV,
            name=sandbox_name,
            is_vps_hosted=False,  # Dev sandboxes are local
            path="",  # Local path determined by dev
        )


# =============================================================================
# CONTENT OWNERSHIP (Beta benefits only for superuser-created content)
# =============================================================================

class ContentCreator(IntEnum):
    """Who created the content - determines beta benefit eligibility"""
    SUPERUSER = 0    # Created by Kenneth - Beta gets free access
    COMMUNITY = 1    # Created by devs - Normal pricing applies


@dataclass
class Content:
    """
    Content/Package with ownership tracking.
    
    Beta benefits ONLY apply to SUPERUSER-created content.
    Dev-submitted content has its own pricing set by the dev.
    """
    id: str
    name: str
    creator_id: str             # User ID of creator
    creator_type: ContentCreator
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    # Pricing (only applies to COMMUNITY content for beta users)
    is_free: bool = True
    price_usd: float = 0.0
    
    # Access control
    min_tier: UserTier = UserTier.USER
    
    # Metadata
    description: str = ""
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def beta_gets_free(self) -> bool:
        """Beta users get this content free if created by superuser"""
        return self.creator_type == ContentCreator.SUPERUSER
    
    def get_price_for_user(self, user_tier: UserTier) -> float:
        """Get price for a user based on tier and content creator"""
        # Superuser always free
        if user_tier >= UserTier.SUPERUSER:
            return 0.0
        
        # Beta gets free for superuser-created content only
        if user_tier >= UserTier.BETA and self.creator_type == ContentCreator.SUPERUSER:
            return 0.0
        
        # Free content is free for everyone
        if self.is_free:
            return 0.0
        
        # Otherwise pay the listed price
        return self.price_usd


# =============================================================================
# MARKETPLACE SUBMISSION (Dev submissions to site)
# =============================================================================

class SubmissionStatus(IntEnum):
    """Status of a marketplace submission"""
    DRAFT = 0
    SUBMITTED = 1
    UNDER_REVIEW = 2
    APPROVED = 3
    REJECTED = 4
    PUBLISHED = 5


# Industry standard marketplace fees
MARKETPLACE_FEES = {
    "free": 0.0,                    # Free apps: no fee
    "paid_flat": 0.30,              # Flat fee per transaction (like Stripe)
    "paid_percentage": 0.029,       # 2.9% (industry standard payment processing)
    "platform_cut": 0.15,           # 15% platform cut (lower than Apple's 30%)
}


@dataclass
class MarketplaceSubmission:
    """
    Developer submission to the marketplace.
    
    - Free apps: upload for free
    - Paid apps: industry standard fees apply
    - Developer sets their own pricing
    - Beta designation applies ONLY to superuser content
    """
    id: str
    developer_id: str           # Dev who submitted
    
    # Content info
    name: str
    description: str = ""
    version: str = "1.0.0"
    
    # Pricing (set by developer)
    is_free: bool = True
    price_usd: float = 0.0      # Price set by dev
    
    # Status workflow
    status: SubmissionStatus = SubmissionStatus.DRAFT
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    
    # Review
    reviewer_notes: str = ""
    rejection_reason: str = ""
    
    # Metadata
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def marketplace_fee(self) -> float:
        """Calculate marketplace fee for this submission"""
        if self.is_free:
            return 0.0
        
        # Industry standard: flat fee + percentage + platform cut
        flat = MARKETPLACE_FEES["paid_flat"]
        pct = MARKETPLACE_FEES["paid_percentage"] * self.price_usd
        platform = MARKETPLACE_FEES["platform_cut"] * self.price_usd
        
        return flat + pct + platform
    
    @property
    def developer_revenue(self) -> float:
        """What the developer earns per sale"""
        if self.is_free:
            return 0.0
        return self.price_usd - self.marketplace_fee
    
    def submit_for_review(self) -> None:
        """Submit to marketplace for review"""
        if self.status != SubmissionStatus.DRAFT:
            raise ValueError("Can only submit drafts")
        self.status = SubmissionStatus.SUBMITTED
        self.submitted_at = datetime.now()
    
    def approve(self) -> None:
        """Approve submission (superuser only)"""
        if self.status not in (SubmissionStatus.SUBMITTED, SubmissionStatus.UNDER_REVIEW):
            raise ValueError("Can only approve submitted or under-review submissions")
        self.status = SubmissionStatus.APPROVED
        self.reviewed_at = datetime.now()
    
    def publish(self) -> 'Content':
        """Publish approved submission as Content"""
        if self.status != SubmissionStatus.APPROVED:
            raise ValueError("Can only publish approved submissions")
        
        self.status = SubmissionStatus.PUBLISHED
        self.published_at = datetime.now()
        
        # Create Content entry (marked as COMMUNITY, not beta-free)
        return Content(
            id=f"content-{self.id}",
            name=self.name,
            creator_id=self.developer_id,
            creator_type=ContentCreator.COMMUNITY,  # NOT beta-free
            is_free=self.is_free,
            price_usd=self.price_usd,
            description=self.description,
            version=self.version,
        )

