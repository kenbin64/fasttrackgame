"""
ButterflyFX Auth API Routes

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)

Authentication and authorization API endpoints.
"""

import json
import time
import hashlib
from typing import Dict, Any, Optional, Tuple
from dataclasses import asdict

# Import auth system
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from server.auth import (
    AuthService, UserTier, InstanceRole,
    get_pages_for_tier, can_access_page, get_navigation_for_tier,
    check_payment_gate, SUBSCRIPTION_PLANS, PAYMENT_METHODS
)


class AuthAPI:
    """Authentication API handler"""
    
    def __init__(self, auth_service: AuthService = None):
        self.auth = auth_service or AuthService()
        # Session storage (in production use Redis/database)
        self.sessions: Dict[str, Dict] = {}
    
    def handle_get(self, path: str, query: Dict, headers: Dict) -> Tuple[Dict, int]:
        """Handle GET requests to auth API"""
        
        # Get session from cookie or Authorization header
        session = self._get_session(headers)
        
        if path == 'status':
            if session:
                user = session.get('user')
                return {
                    "authenticated": True,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "tier": user.tier.name,
                        "tier_level": user.tier.value
                    },
                    "expires": session.get('expires')
                }, 200
            return {"authenticated": False}, 200
        
        elif path == 'navigation':
            # Get navigation items for current user's tier
            tier = UserTier.ANONYMOUS
            if session:
                tier = session['user'].tier
            
            nav = get_navigation_for_tier(tier)
            return {"navigation": nav, "tier": tier.name}, 200
        
        elif path == 'pages':
            # Get accessible pages for tier
            tier_name = query.get('tier', ['ANONYMOUS'])[0].upper()
            try:
                tier = UserTier[tier_name]
            except KeyError:
                tier = UserTier.ANONYMOUS
            
            pages = get_pages_for_tier(tier)
            return {
                "tier": tier.name,
                "pages": [{"path": p.path, "name": p.name} for p in pages]
            }, 200
        
        elif path == 'plans':
            # Get subscription plans
            plans = []
            for plan_id, details in SUBSCRIPTION_PLANS.items():
                plans.append({
                    "id": plan_id.name,
                    "name": details.name,
                    "price": details.price,
                    "interval": details.interval,
                    "description": details.description,
                    "features": details.features
                })
            return {"plans": plans}, 200
        
        elif path == 'payment-methods':
            # Get payment methods
            methods = []
            for method_id, method in PAYMENT_METHODS.items():
                if method.enabled:
                    methods.append({
                        "id": method_id,
                        "name": method.name,
                        "icon": method.icon
                    })
            return {"methods": methods}, 200
        
        elif path == 'logout':
            # Clear session
            session_id = self._get_session_id(headers)
            if session_id and session_id in self.sessions:
                del self.sessions[session_id]
            return {"success": True, "redirect": "/"}, 200
        
        return {"error": "Unknown endpoint"}, 404
    
    def handle_post(self, path: str, body: Dict, headers: Dict) -> Tuple[Dict, int]:
        """Handle POST requests to auth API"""
        
        if path == 'login':
            return self._handle_login(body)
        
        elif path == 'login/apikey':
            return self._handle_api_key_login(body)
        
        elif path == 'register':
            return self._handle_register(body, UserTier.USER)
        
        elif path == 'register/dev':
            return self._handle_register(body, UserTier.DEV)
        
        elif path == 'register/beta':
            return self._handle_register_beta(body)
        
        elif path == 'check-access':
            # Check if user can access a page
            session = self._get_session(headers)
            page_path = body.get('path', '/')
            
            tier = UserTier.ANONYMOUS
            if session:
                tier = session['user'].tier
            
            can_access = can_access_page(page_path, tier)
            
            # Check payment gate for dev tier
            payment_required = None
            if tier == UserTier.DEV and session:
                user = session['user']
                gate_info = check_payment_gate(
                    user,
                    user.subscription_status if hasattr(user, 'subscription_status') else None,
                    page_path
                )
                if gate_info:
                    payment_required = {
                        "required": True,
                        "required_tier": gate_info.required_tier.name,
                        "plans": [
                            {
                                "id": p.name,
                                "name": SUBSCRIPTION_PLANS[p].name,
                                "price": SUBSCRIPTION_PLANS[p].price
                            }
                            for p in gate_info.available_plans
                        ]
                    }
            
            return {
                "can_access": can_access,
                "tier": tier.name,
                "payment_required": payment_required
            }, 200
        
        elif path == 'apikey/generate':
            # Generate API key (must be authenticated)
            session = self._get_session(headers)
            if not session:
                return {"error": "Not authenticated"}, 401
            
            user = session['user']
            key = self.auth.generate_api_key(user.id)
            return {"api_key": key, "warning": "Store this key safely - it cannot be retrieved again"}, 200
        
        elif path == 'beta-code/create':
            # Create beta code (superuser only)
            session = self._get_session(headers)
            if not session:
                return {"error": "Not authenticated"}, 401
            
            user = session['user']
            if user.tier != UserTier.SUPERUSER:
                return {"error": "Superuser access required"}, 403
            
            max_uses = body.get('max_uses', 1)
            code = self.auth.create_beta_code(user.id, max_uses)
            return {"code": code, "max_uses": max_uses}, 200
        
        return {"error": "Unknown endpoint"}, 404
    
    def _handle_login(self, body: Dict) -> Tuple[Dict, int]:
        """Handle login request"""
        identifier = body.get('identifier') or body.get('username')
        password = body.get('password')
        
        if not identifier or not password:
            return {"error": "Username/email and password required"}, 400
        
        # Try login
        try:
            user, auth_session = self.auth.login(identifier, password)
        except Exception as e:
            return {"error": str(e)}, 401
        
        if not user:
            return {"error": "Invalid credentials"}, 401
        
        # Create session
        session_id = self._create_session(user)
        
        # Determine redirect based on tier
        redirect = '/dashboard'
        if user.tier == UserTier.SUPERUSER:
            redirect = '/admin'
        elif user.tier == UserTier.BETA:
            redirect = '/beta'
        elif user.tier == UserTier.DEV:
            redirect = '/developer'
        
        return {
            "success": True,
            "session_id": session_id,
            "user": {
                "id": user.id,
                "username": user.username,
                "tier": user.tier.name
            },
            "redirect": redirect
        }, 200
    
    def _handle_api_key_login(self, body: Dict) -> Tuple[Dict, int]:
        """Handle API key authentication"""
        api_key = body.get('api_key')
        
        if not api_key:
            return {"error": "API key required"}, 400
        
        # Validate API key
        user = self.auth.validate_api_key(api_key)
        
        if not user:
            return {"error": "Invalid or expired API key"}, 401
        
        # Create session
        session_id = self._create_session(user)
        
        return {
            "success": True,
            "session_id": session_id,
            "user": {
                "id": user.id,
                "username": user.username,
                "tier": user.tier.name
            },
            "redirect": "/dashboard"
        }, 200
    
    def _handle_register(self, body: Dict, tier: UserTier) -> Tuple[Dict, int]:
        """Handle registration request"""
        username = body.get('username')
        email = body.get('email')
        password = body.get('password')
        
        if not username or not email or not password:
            return {"error": "Username, email, and password required"}, 400
        
        if len(password) < 6:
            return {"error": "Password must be at least 6 characters"}, 400
        
        try:
            if tier == UserTier.DEV:
                user = self.auth.register_as_dev(username, email, password)
                # Dev needs to pay - redirect to checkout
                session_id = self._create_session(user)
                return {
                    "success": True,
                    "session_id": session_id,
                    "user": {"id": user.id, "username": user.username, "tier": user.tier.name},
                    "redirect": "/checkout?plan=monthly",
                    "payment_required": True
                }, 200
            else:
                user = self.auth.register(username, email, password)
                session_id = self._create_session(user)
                return {
                    "success": True,
                    "session_id": session_id,
                    "user": {"id": user.id, "username": user.username, "tier": user.tier.name},
                    "redirect": "/dashboard"
                }, 200
        
        except ValueError as e:
            return {"error": str(e)}, 400
    
    def _handle_register_beta(self, body: Dict) -> Tuple[Dict, int]:
        """Handle beta registration with invite code"""
        username = body.get('username')
        email = body.get('email')
        password = body.get('password')
        beta_code = body.get('beta_code')
        
        if not username or not email or not password:
            return {"error": "Username, email, and password required"}, 400
        
        if not beta_code:
            return {"error": "Beta invitation code required"}, 400
        
        try:
            user = self.auth.register_as_beta(username, email, password, beta_code)
            session_id = self._create_session(user)
            return {
                "success": True,
                "session_id": session_id,
                "user": {"id": user.id, "username": user.username, "tier": user.tier.name},
                "redirect": "/beta"
            }, 200
        
        except ValueError as e:
            return {"error": str(e)}, 400
    
    def _create_session(self, user) -> str:
        """Create a session for user"""
        session_id = hashlib.sha256(
            f"{user.id}{time.time()}{id(user)}".encode()
        ).hexdigest()
        
        self.sessions[session_id] = {
            "user": user,
            "created": time.time(),
            "expires": time.time() + (24 * 60 * 60)  # 24 hours
        }
        
        return session_id
    
    def _get_session_id(self, headers: Dict) -> Optional[str]:
        """Extract session ID from headers"""
        # Check Authorization header
        auth_header = headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        
        # Check Cookie header
        cookie = headers.get('Cookie', '')
        if 'session=' in cookie:
            for part in cookie.split(';'):
                if part.strip().startswith('session='):
                    return part.strip()[8:]
        
        return None
    
    def _get_session(self, headers: Dict) -> Optional[Dict]:
        """Get session from headers"""
        session_id = self._get_session_id(headers)
        if not session_id:
            return None
        
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        # Check expiry
        if time.time() > session.get('expires', 0):
            del self.sessions[session_id]
            return None
        
        return session


# Singleton instance
_auth_api = None

def get_auth_api() -> AuthAPI:
    """Get or create the auth API singleton"""
    global _auth_api
    if _auth_api is None:
        _auth_api = AuthAPI()
    return _auth_api


# =============================================================================
# SOCIAL OAUTH SUPPORT (Google, Facebook)
# =============================================================================

from server.auth.social_oauth import get_social_auth, SocialOAuthError


class SocialAuthAPI:
    """
    Social OAuth API handler for Google and Facebook login.
    
    Routes:
        GET /api/auth/google           - Start Google OAuth
        GET /api/auth/google/callback  - Handle Google callback
        GET /api/auth/facebook         - Start Facebook OAuth
        GET /api/auth/facebook/callback - Handle Facebook callback
    """
    
    def __init__(self):
        self.social = get_social_auth()
        self.auth_api = get_auth_api()
    
    def handle_google_start(self, query: Dict, headers: Dict) -> Tuple[Dict, int]:
        """Start Google OAuth flow"""
        redirect_after = query.get('redirect', '/dashboard.html')
        
        try:
            url, state = self.social.get_login_url('google', redirect_after=redirect_after)
            return {
                'redirect': url,
                'state': state,
            }, 302
        except Exception as e:
            return {'error': str(e)}, 500
    
    def handle_google_callback(self, query: Dict, headers: Dict) -> Tuple[Dict, int]:
        """Handle Google OAuth callback"""
        if query.get('error'):
            error_msg = query.get('error_description', 'Google login failed')
            return {'redirect': f'/login.html?error={error_msg}'}, 302
        
        code = query.get('code', '')
        state = query.get('state', '')
        
        if not code or not state:
            return {'redirect': '/login.html?error=Invalid OAuth response'}, 302
        
        try:
            social_user, redirect_after = self.social.handle_callback('google', code, state)
            result = self.social.link_or_create_user(social_user)
            
            return {
                'redirect': redirect_after,
                'set_cookie': f"session={result['session_token']}; Path=/; HttpOnly; SameSite=Lax",
                'user': result,
            }, 302
            
        except SocialOAuthError as e:
            return {'redirect': f'/login.html?error={str(e)}'}, 302
    
    def handle_facebook_start(self, query: Dict, headers: Dict) -> Tuple[Dict, int]:
        """Start Facebook OAuth flow"""
        redirect_after = query.get('redirect', '/dashboard.html')
        
        try:
            url, state = self.social.get_login_url('facebook', redirect_after=redirect_after)
            return {
                'redirect': url,
                'state': state,
            }, 302
        except Exception as e:
            return {'error': str(e)}, 500
    
    def handle_facebook_callback(self, query: Dict, headers: Dict) -> Tuple[Dict, int]:
        """Handle Facebook OAuth callback"""
        if query.get('error'):
            error_msg = query.get('error_description', 'Facebook login failed')
            return {'redirect': f'/login.html?error={error_msg}'}, 302
        
        code = query.get('code', '')
        state = query.get('state', '')
        
        if not code or not state:
            return {'redirect': '/login.html?error=Invalid OAuth response'}, 302
        
        try:
            social_user, redirect_after = self.social.handle_callback('facebook', code, state)
            result = self.social.link_or_create_user(social_user)
            
            return {
                'redirect': redirect_after,
                'set_cookie': f"session={result['session_token']}; Path=/; HttpOnly; SameSite=Lax",
                'user': result,
            }, 302
            
        except SocialOAuthError as e:
            return {'redirect': f'/login.html?error={str(e)}'}, 302
    
    def get_providers(self) -> Dict:
        """Get available OAuth providers"""
        return {
            'providers': self.social.available_providers
        }


# Social auth singleton
_social_auth_api = None

def get_social_auth_api() -> SocialAuthAPI:
    """Get or create the social auth API singleton"""
    global _social_auth_api
    if _social_auth_api is None:
        _social_auth_api = SocialAuthAPI()
    return _social_auth_api
