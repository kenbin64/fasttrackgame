"""
ButterflyFX Social OAuth Integration
=====================================

Provides Google and Facebook OAuth 2.0 authentication.

Both providers are FREE to use:
- Google Cloud Console: https://console.cloud.google.com/
- Facebook Developers: https://developers.facebook.com/

Flow:
1. User clicks "Login with Google/Facebook"
2. Redirect to provider authorization URL
3. User authorizes on provider
4. Provider redirects back with code
5. Exchange code for access token
6. Fetch user info from provider
7. Create/link ButterflyFX account

Copyright (c) 2024-2026 Kenneth Bingham
All Rights Reserved
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime
from enum import Enum
import os
import secrets
import json
import urllib.request
import urllib.parse
import urllib.error


class OAuthProvider(Enum):
    """Supported OAuth providers"""
    GOOGLE = "google"
    FACEBOOK = "facebook"
    GITHUB = "github"


@dataclass
class SocialUser:
    """Unified social user profile"""
    provider: OAuthProvider
    provider_id: str           # Unique ID from provider
    email: str
    name: str
    first_name: str = ""
    last_name: str = ""
    avatar_url: str = ""
    locale: str = ""
    verified: bool = False
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def display_name(self) -> str:
        return self.name or f"{self.first_name} {self.last_name}".strip() or self.email.split('@')[0]


@dataclass
class OAuthState:
    """State for OAuth flow - prevents CSRF"""
    state: str
    provider: OAuthProvider
    created_at: datetime
    redirect_after: str        # Where to redirect after login
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """State expires after 10 minutes"""
        return (datetime.now() - self.created_at).total_seconds() > 600


class SocialOAuthError(Exception):
    """Social OAuth error"""
    pass


# =============================================================================
# GOOGLE OAUTH
# =============================================================================

class GoogleOAuth:
    """
    Google OAuth 2.0 handler.
    
    Setup (FREE):
    1. Go to https://console.cloud.google.com/
    2. Create project → APIs & Services → Credentials
    3. Create OAuth 2.0 Client ID (Web application)
    4. Add authorized redirect URIs
    5. Copy Client ID and Client Secret
    
    Environment Variables:
        GOOGLE_CLIENT_ID: OAuth client ID
        GOOGLE_CLIENT_SECRET: OAuth client secret
        GOOGLE_REDIRECT_URI: Callback URL
    """
    
    AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
    
    # Scopes - openid for ID token, email, profile for user info
    SCOPES = ["openid", "email", "profile"]
    
    def __init__(self, client_id: str = None, client_secret: str = None,
                 redirect_uri: str = None):
        self.client_id = client_id or os.environ.get('GOOGLE_CLIENT_ID', '')
        self.client_secret = client_secret or os.environ.get('GOOGLE_CLIENT_SECRET', '')
        self.redirect_uri = redirect_uri or os.environ.get(
            'GOOGLE_REDIRECT_URI', 
            'https://butterflyfx.us/api/auth/google/callback'
        )
        
        # Store pending OAuth states
        self._pending_states: Dict[str, OAuthState] = {}
    
    def get_authorization_url(self, redirect_after: str = "/") -> Tuple[str, str]:
        """
        Generate Google authorization URL.
        
        Args:
            redirect_after: Where to redirect after successful login
            
        Returns:
            Tuple of (authorization_url, state)
        """
        state = secrets.token_urlsafe(32)
        
        # Store state for validation
        self._pending_states[state] = OAuthState(
            state=state,
            provider=OAuthProvider.GOOGLE,
            created_at=datetime.now(),
            redirect_after=redirect_after
        )
        
        # Clean expired states
        self._clean_expired_states()
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(self.SCOPES),
            'state': state,
            'access_type': 'offline',      # Get refresh token
            'prompt': 'select_account',    # Always show account chooser
        }
        
        url = f"{self.AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"
        return url, state
    
    def handle_callback(self, code: str, state: str) -> Tuple[SocialUser, str]:
        """
        Handle OAuth callback from Google.
        
        Args:
            code: Authorization code from Google
            state: State parameter for CSRF validation
            
        Returns:
            Tuple of (SocialUser, redirect_after_url)
        """
        # Validate state
        oauth_state = self._pending_states.get(state)
        if not oauth_state:
            raise SocialOAuthError("Invalid state parameter")
        if oauth_state.is_expired:
            del self._pending_states[state]
            raise SocialOAuthError("OAuth state expired")
        if oauth_state.provider != OAuthProvider.GOOGLE:
            raise SocialOAuthError("Provider mismatch")
        
        redirect_after = oauth_state.redirect_after
        del self._pending_states[state]
        
        # Exchange code for tokens
        tokens = self._exchange_code(code)
        access_token = tokens.get('access_token')
        if not access_token:
            raise SocialOAuthError("No access token in response")
        
        # Fetch user info
        user = self._fetch_user(access_token)
        
        return user, redirect_after
    
    def _exchange_code(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
        }
        
        req = urllib.request.Request(
            self.TOKEN_URL,
            data=urllib.parse.urlencode(data).encode('utf-8'),
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise SocialOAuthError(f"Token exchange failed: {error_body}")
    
    def _fetch_user(self, access_token: str) -> SocialUser:
        """Fetch user info from Google"""
        req = urllib.request.Request(
            self.USER_URL,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise SocialOAuthError(f"Failed to fetch user info: {error_body}")
        
        return SocialUser(
            provider=OAuthProvider.GOOGLE,
            provider_id=data.get('sub', ''),
            email=data.get('email', ''),
            name=data.get('name', ''),
            first_name=data.get('given_name', ''),
            last_name=data.get('family_name', ''),
            avatar_url=data.get('picture', ''),
            locale=data.get('locale', ''),
            verified=data.get('email_verified', False),
            raw_data=data
        )
    
    def _clean_expired_states(self):
        """Remove expired OAuth states"""
        expired = [s for s, state in self._pending_states.items() if state.is_expired]
        for s in expired:
            del self._pending_states[s]


# =============================================================================
# FACEBOOK OAUTH
# =============================================================================

class FacebookOAuth:
    """
    Facebook OAuth 2.0 handler.
    
    Setup (FREE):
    1. Go to https://developers.facebook.com/
    2. Create App → Consumer type
    3. Add Facebook Login product
    4. Settings → Basic: Get App ID and App Secret
    5. Facebook Login → Settings: Add OAuth redirect URIs
    
    Environment Variables:
        FACEBOOK_APP_ID: App ID
        FACEBOOK_APP_SECRET: App Secret
        FACEBOOK_REDIRECT_URI: Callback URL
    """
    
    AUTHORIZE_URL = "https://www.facebook.com/v18.0/dialog/oauth"
    TOKEN_URL = "https://graph.facebook.com/v18.0/oauth/access_token"
    USER_URL = "https://graph.facebook.com/v18.0/me"
    
    # Scopes - email and public_profile are the basics
    SCOPES = ["email", "public_profile"]
    
    # Fields to request from Graph API
    USER_FIELDS = ["id", "name", "email", "first_name", "last_name", "picture.type(large)"]
    
    def __init__(self, app_id: str = None, app_secret: str = None,
                 redirect_uri: str = None):
        self.app_id = app_id or os.environ.get('FACEBOOK_APP_ID', '')
        self.app_secret = app_secret or os.environ.get('FACEBOOK_APP_SECRET', '')
        self.redirect_uri = redirect_uri or os.environ.get(
            'FACEBOOK_REDIRECT_URI',
            'https://butterflyfx.us/api/auth/facebook/callback'
        )
        
        # Store pending OAuth states
        self._pending_states: Dict[str, OAuthState] = {}
    
    def get_authorization_url(self, redirect_after: str = "/") -> Tuple[str, str]:
        """
        Generate Facebook authorization URL.
        
        Args:
            redirect_after: Where to redirect after successful login
            
        Returns:
            Tuple of (authorization_url, state)
        """
        state = secrets.token_urlsafe(32)
        
        # Store state for validation
        self._pending_states[state] = OAuthState(
            state=state,
            provider=OAuthProvider.FACEBOOK,
            created_at=datetime.now(),
            redirect_after=redirect_after
        )
        
        # Clean expired states
        self._clean_expired_states()
        
        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'state': state,
            'scope': ','.join(self.SCOPES),
            'response_type': 'code',
        }
        
        url = f"{self.AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"
        return url, state
    
    def handle_callback(self, code: str, state: str) -> Tuple[SocialUser, str]:
        """
        Handle OAuth callback from Facebook.
        
        Args:
            code: Authorization code from Facebook
            state: State parameter for CSRF validation
            
        Returns:
            Tuple of (SocialUser, redirect_after_url)
        """
        # Validate state
        oauth_state = self._pending_states.get(state)
        if not oauth_state:
            raise SocialOAuthError("Invalid state parameter")
        if oauth_state.is_expired:
            del self._pending_states[state]
            raise SocialOAuthError("OAuth state expired")
        if oauth_state.provider != OAuthProvider.FACEBOOK:
            raise SocialOAuthError("Provider mismatch")
        
        redirect_after = oauth_state.redirect_after
        del self._pending_states[state]
        
        # Exchange code for tokens
        tokens = self._exchange_code(code)
        access_token = tokens.get('access_token')
        if not access_token:
            raise SocialOAuthError("No access token in response")
        
        # Fetch user info
        user = self._fetch_user(access_token)
        
        return user, redirect_after
    
    def _exchange_code(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        params = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
        }
        
        url = f"{self.TOKEN_URL}?{urllib.parse.urlencode(params)}"
        
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise SocialOAuthError(f"Token exchange failed: {error_body}")
    
    def _fetch_user(self, access_token: str) -> SocialUser:
        """Fetch user info from Facebook Graph API"""
        params = {
            'access_token': access_token,
            'fields': ','.join(self.USER_FIELDS),
        }
        
        url = f"{self.USER_URL}?{urllib.parse.urlencode(params)}"
        
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise SocialOAuthError(f"Failed to fetch user info: {error_body}")
        
        # Extract avatar URL from nested picture object
        avatar_url = ""
        if 'picture' in data and 'data' in data['picture']:
            avatar_url = data['picture']['data'].get('url', '')
        
        return SocialUser(
            provider=OAuthProvider.FACEBOOK,
            provider_id=data.get('id', ''),
            email=data.get('email', ''),
            name=data.get('name', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            avatar_url=avatar_url,
            locale='',
            verified=True,  # Facebook verifies emails
            raw_data=data
        )
    
    def _clean_expired_states(self):
        """Remove expired OAuth states"""
        expired = [s for s, state in self._pending_states.items() if state.is_expired]
        for s in expired:
            del self._pending_states[s]


# =============================================================================
# UNIFIED SOCIAL AUTH MANAGER
# =============================================================================

class SocialAuthManager:
    """
    Unified manager for all social OAuth providers.
    
    Usage:
        manager = SocialAuthManager()
        
        # Get login URL
        url, state = manager.get_login_url('google', redirect_after='/dashboard')
        
        # Handle callback
        user, redirect = manager.handle_callback('google', code, state)
        
        # Link to ButterflyFX account
        bfx_user = manager.link_or_create_user(user)
    """
    
    def __init__(self):
        self.google = GoogleOAuth()
        self.facebook = FacebookOAuth()
        
        # Provider map
        self._providers = {
            'google': self.google,
            'facebook': self.facebook,
        }
    
    @property
    def available_providers(self) -> List[Dict[str, str]]:
        """List of available OAuth providers with display info"""
        return [
            {
                'id': 'google',
                'name': 'Google',
                'icon': 'fab fa-google',
                'color': '#4285F4',
                'configured': bool(self.google.client_id),
            },
            {
                'id': 'facebook',
                'name': 'Facebook',
                'icon': 'fab fa-facebook-f',
                'color': '#1877F2',
                'configured': bool(self.facebook.app_id),
            },
        ]
    
    def get_login_url(self, provider: str, redirect_after: str = "/") -> Tuple[str, str]:
        """
        Get OAuth login URL for a provider.
        
        Args:
            provider: 'google' or 'facebook'
            redirect_after: Where to redirect after login
            
        Returns:
            Tuple of (authorization_url, state)
        """
        handler = self._providers.get(provider)
        if not handler:
            raise SocialOAuthError(f"Unknown provider: {provider}")
        
        return handler.get_authorization_url(redirect_after)
    
    def handle_callback(self, provider: str, code: str, state: str) -> Tuple[SocialUser, str]:
        """
        Handle OAuth callback from a provider.
        
        Args:
            provider: 'google' or 'facebook'
            code: Authorization code
            state: State for CSRF validation
            
        Returns:
            Tuple of (SocialUser, redirect_after_url)
        """
        handler = self._providers.get(provider)
        if not handler:
            raise SocialOAuthError(f"Unknown provider: {provider}")
        
        return handler.handle_callback(code, state)
    
    def link_or_create_user(self, social_user: SocialUser) -> Dict[str, Any]:
        """
        Link social account to existing user or create new user.
        
        Args:
            social_user: User info from OAuth provider
            
        Returns:
            ButterflyFX user dict with session token
        """
        from .service import AuthService
        
        auth = AuthService()
        
        # Try to find existing user by email
        existing = None
        for user in auth.users.values():
            if user.email == social_user.email:
                existing = user
                break
        
        if existing:
            # Link social account and create session
            # Store social provider info
            if not hasattr(existing, 'social_links'):
                existing.social_links = {}
            existing.social_links[social_user.provider.value] = social_user.provider_id
            auth._save_users()
            
            # Create session
            session = auth.create_session(existing.id)
            return {
                'user_id': existing.id,
                'username': existing.username,
                'email': existing.email,
                'tier': existing.tier.name,
                'session_token': session.token,
                'avatar_url': social_user.avatar_url,
                'is_new': False,
            }
        else:
            # Create new user
            # Generate unique username from email
            base_username = social_user.email.split('@')[0]
            username = base_username
            counter = 1
            while username in auth.users:
                username = f"{base_username}{counter}"
                counter += 1
            
            # Create user without password (social-only)
            user = auth.register(
                username=username,
                email=social_user.email,
                password=None,  # Social login, no password
                display_name=social_user.display_name,
            )
            
            # Link social account
            if not hasattr(user, 'social_links'):
                user.social_links = {}
            user.social_links[social_user.provider.value] = social_user.provider_id
            auth._save_users()
            
            # Create session
            session = auth.create_session(user.id)
            return {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'tier': user.tier.name,
                'session_token': session.token,
                'avatar_url': social_user.avatar_url,
                'is_new': True,
            }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_social_auth_manager: Optional[SocialAuthManager] = None

def get_social_auth() -> SocialAuthManager:
    """Get singleton SocialAuthManager instance"""
    global _social_auth_manager
    if _social_auth_manager is None:
        _social_auth_manager = SocialAuthManager()
    return _social_auth_manager
