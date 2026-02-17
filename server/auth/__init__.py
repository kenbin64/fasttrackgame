"""
ButterflyFX Authentication Package
===================================

TWO SEPARATE ROLE SYSTEMS:

1. WEBSITE TIERS (VPS, Downloads, Hosted Services)
   - SUPERUSER: Kenneth Bingham - supreme control, free everything
   - BETA: Beta testers - free for superuser content only, sandbox on VPS
   - DEV: Developers - dev packages, marketplace submission, local sandbox
   - USER: Basic users - open source only

2. INSTANCE ROLES (Zero Trust - Local Apps)
   - ADMIN: Full control (default for downloader)
   - MODERATOR: Content moderation
   - MEMBER: Basic participation
   - GUEST: Read-only
   
   Admins only control their own domains/instances.
   Website roles do NOT grant local access.

BETA DESIGNATION:
   - Only for content created by superuser (Kenneth)
   - Does NOT grant free access to dev submissions
   - Devs set their own pricing

MARKETPLACE FEES (Industry Standard):
   - Free apps: no fee
   - Paid apps: $0.30 flat + 2.9% + 15% platform cut

Usage:
    from server.auth import get_auth_service, UserTier, InstanceRole
    
    # Website access
    auth = get_auth_service()
    user, session = auth.login(username, password)
    
    # Instance access (Zero Trust)
    perms = InstancePermissions.for_role(InstanceRole.ADMIN, is_owner=True)

Copyright (c) 2024-2026 Kenneth Bingham
All Rights Reserved
"""

from .models import (
    User,
    UserTier,
    UserPermissions,
    AccessLevel,
    Session,
    BetaCode,
    TIER_INFO,
    get_tier_info,
    # Instance roles (Zero Trust for local apps)
    InstanceRole,
    InstancePermissions,
    # Sandbox system
    Sandbox,
    # Content ownership
    Content,
    ContentCreator,
    # Marketplace
    MarketplaceSubmission,
    SubmissionStatus,
    MARKETPLACE_FEES,
)

from .service import (
    AuthService,
    AuthError,
    InvalidCredentialsError,
    UserNotFoundError,
    UserExistsError,
    InsufficientPermissionsError,
    SessionExpiredError,
    InvalidBetaCodeError,
    get_auth_service,
    requires_auth,
    requires_tier,
    requires_permission,
)

from .access import (
    PageAccess,
    Page,
    FeatureGate,
    PUBLIC_PAGES,
    USER_PAGES,
    DEV_PAGES,
    BETA_PAGES,
    SUPERUSER_PAGES,
    ALL_PAGES,
    FEATURE_GATES,
    get_pages_for_tier,
    can_access_page,
    get_navigation_for_tier,
    get_features_for_tier,
    can_use_feature,
)

from .payment import (
    PaymentStatus,
    SubscriptionPlan,
    PlanDetails,
    Subscription,
    PaymentMethod,
    PaymentRequiredInfo,
    SUBSCRIPTION_PLANS,
    PAYMENT_METHODS,
    get_enabled_payment_methods,
    requires_payment,
    check_payment_gate,
    get_payment_required_info,
)

from .middleware import (
    AccessControlMiddleware,
    create_access_gate,
)

from .github_oauth import (
    GitHubOAuth,
    GitHubUser,
    GitHubOAuthState,
    GitHubOAuthError,
    get_github_oauth,
)

__all__ = [
    # Website Models (VPS access, downloads)
    'User',
    'UserTier',
    'UserPermissions',
    'AccessLevel',
    'Session',
    'BetaCode',
    'TIER_INFO',
    'get_tier_info',
    
    # Instance Models (Zero Trust for local apps)
    'InstanceRole',
    'InstancePermissions',
    
    # Sandbox System
    'Sandbox',
    
    # Content Ownership
    'Content',
    'ContentCreator',
    
    # Marketplace
    'MarketplaceSubmission',
    'SubmissionStatus',
    'MARKETPLACE_FEES',
    
    # Access Control (Pages & Features per Role)
    'PageAccess',
    'Page',
    'FeatureGate',
    'PUBLIC_PAGES',
    'USER_PAGES',
    'DEV_PAGES',
    'BETA_PAGES',
    'SUPERUSER_PAGES',
    'ALL_PAGES',
    'FEATURE_GATES',
    'get_pages_for_tier',
    'can_access_page',
    'get_navigation_for_tier',
    'get_features_for_tier',
    'can_use_feature',
    
    # Payment & Subscription
    'PaymentStatus',
    'SubscriptionPlan',
    'PlanDetails',
    'Subscription',
    'PaymentMethod',
    'PaymentRequiredInfo',
    'SUBSCRIPTION_PLANS',
    'PAYMENT_METHODS',
    'get_enabled_payment_methods',
    'requires_payment',
    'check_payment_gate',
    'get_payment_required_info',
    
    # Service
    'AuthService',
    'AuthError',
    'InvalidCredentialsError',
    'UserNotFoundError',
    'UserExistsError',
    'InsufficientPermissionsError',
    'SessionExpiredError',
    'InvalidBetaCodeError',
    'get_auth_service',
    
    # Decorators
    'requires_auth',
    'requires_tier',
    'requires_permission',
    
    # Middleware
    'AccessControlMiddleware',
    'create_access_gate',
    
    # GitHub OAuth
    'GitHubOAuth',
    'GitHubUser',
    'GitHubOAuthState',
    'GitHubOAuthError',
    'get_github_oauth',
]
