"""
ButterflyFX Access Control Middleware

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)

Middleware for gating premium content behind login and payment.
"""

import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).parent.parent))

from server.auth.models import UserTier, AccessLevel
from server.auth.access import can_access_page, FEATURE_GATES
from server.auth.payment import check_payment_gate, requires_payment


class AccessControlMiddleware:
    """
    Middleware that gates premium content behind login and payment.
    
    Access Flow:
    1. Check if page requires authentication
    2. If not authenticated -> redirect to /login
    3. Check if user tier has access
    4. If insufficient tier -> show access denied
    5. Check if payment is required (dev tier)
    6. If unpaid -> redirect to /payment-required
    7. Allow access
    """
    
    # Pages that require login (not public)
    LOGIN_REQUIRED_PAGES = [
        '/dashboard',
        '/developer',
        '/beta',
        '/admin',
        '/sandbox',
        '/chat',
        '/settings',
        '/profile',
        '/marketplace/submit',
        '/api-keys',
    ]
    
    # Pages by tier (minimum required)
    TIER_PAGES = {
        UserTier.USER: ['/dashboard', '/settings', '/profile'],
        UserTier.DEV: ['/developer', '/sandbox', '/marketplace/submit', '/api-keys', '/chat/collab'],
        UserTier.BETA: ['/beta', '/chat/beta'],
        UserTier.SUPERUSER: ['/admin', '/superuser'],
    }
    
    # Premium features that require payment (for dev tier)
    PAYMENT_REQUIRED_FEATURES = [
        '/developer/premium',
        '/sandbox/create',
        '/marketplace/submit',
        '/downloads/premium',
    ]
    
    def __init__(self, get_session_func):
        """
        Initialize middleware.
        
        Args:
            get_session_func: Function to get current session from headers
        """
        self.get_session = get_session_func
    
    def check_access(self, path: str, headers: Dict) -> Tuple[bool, Optional[str], Dict]:
        """
        Check if request should be allowed.
        
        Returns:
            (allowed, redirect_url, context)
            - allowed: True if access granted
            - redirect_url: URL to redirect to if denied
            - context: Additional context (error message, etc.)
        """
        # Normalize path
        path = path.rstrip('/')
        if not path:
            path = '/'
        
        # Public pages - always allowed
        if self._is_public_page(path):
            return True, None, {}
        
        # Get session
        session = self.get_session(headers)
        
        # Check if login required
        if self._requires_login(path):
            if not session:
                redirect_url = f"/login?redirect={urlencode({'r': path})}"
                return False, redirect_url, {"reason": "login_required"}
        
        # Get user from session
        user = session.get('user') if session else None
        tier = user.tier if user else UserTier.ANONYMOUS
        
        # Check tier access
        if not self._has_tier_access(path, tier):
            return False, None, {
                "reason": "insufficient_tier",
                "required_tier": self._get_required_tier(path).name,
                "user_tier": tier.name
            }
        
        # Check payment for dev tier
        if tier == UserTier.DEV and self._requires_payment(path):
            # Check if user has paid
            subscription = getattr(user, 'subscription_status', None)
            gate_info = check_payment_gate(user, subscription, path)
            
            if gate_info:
                feature_name = path.split('/')[-1].replace('-', '_')
                redirect_url = f"/payment-required?feature={feature_name}"
                return False, redirect_url, {
                    "reason": "payment_required",
                    "feature": path
                }
        
        return True, None, {}
    
    def _is_public_page(self, path: str) -> bool:
        """Check if page is public (no auth required)"""
        # Exact match public pages
        exact_public = ['/', '/index', '/index.html', '/about', '/docs']
        if path in exact_public:
            return True
        
        # Prefix match public patterns
        public_prefixes = [
            '/login',
            '/register',
            '/payment-required',
            '/checkout',
            '/api/status',
            '/api/auth/',
            '/static/',
            '/manifold/',
            '/d/',
            '/dim/',
            '/about/',
            '/docs/',
        ]
        
        for pattern in public_prefixes:
            if path.startswith(pattern):
                return True
        
        # Static files (CSS, JS, images)
        static_extensions = ['.css', '.js', '.png', '.jpg', '.svg', '.ico', '.woff', '.woff2']
        if any(path.endswith(ext) for ext in static_extensions):
            return True
        
        return False
    
    def _requires_login(self, path: str) -> bool:
        """Check if page requires login"""
        for protected in self.LOGIN_REQUIRED_PAGES:
            if path == protected or path.startswith(protected + '/'):
                return True
        return False
    
    def _has_tier_access(self, path: str, tier: UserTier) -> bool:
        """Check if tier can access path"""
        # Dimensional: higher tiers can access lower tier pages
        required_tier = self._get_required_tier(path)
        return tier.value >= required_tier.value
    
    def _get_required_tier(self, path: str) -> UserTier:
        """Get minimum tier required for path"""
        # Check from highest to lowest
        for tier in [UserTier.SUPERUSER, UserTier.BETA, UserTier.DEV, UserTier.USER]:
            if tier in self.TIER_PAGES:
                for tier_path in self.TIER_PAGES[tier]:
                    if path == tier_path or path.startswith(tier_path + '/'):
                        return tier
        
        # Default to USER for authenticated pages
        if self._requires_login(path):
            return UserTier.USER
        
        return UserTier.ANONYMOUS
    
    def _requires_payment(self, path: str) -> bool:
        """Check if path requires payment"""
        for premium_path in self.PAYMENT_REQUIRED_FEATURES:
            if path == premium_path or path.startswith(premium_path + '/'):
                return True
        return False


def create_access_gate(auth_api):
    """
    Create an access gate function for the server.
    
    Usage in server:
        gate = create_access_gate(auth_api)
        allowed, redirect, ctx = gate(path, headers)
        if not allowed:
            return redirect_response(redirect)
    """
    def get_session(headers):
        return auth_api._get_session(headers)
    
    middleware = AccessControlMiddleware(get_session)
    
    def gate(path: str, headers: Dict) -> Tuple[bool, Optional[str], Dict]:
        return middleware.check_access(path, headers)
    
    return gate
