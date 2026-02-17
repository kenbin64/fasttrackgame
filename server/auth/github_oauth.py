"""
ButterflyFX GitHub OAuth Integration
=====================================

Provides GitHub OAuth 2.0 authentication for the Developer Portal.

Flow:
1. User clicks "Login with GitHub"
2. Redirect to GitHub authorization URL
3. User authorizes on GitHub
4. GitHub redirects back with code
5. Exchange code for access token
6. Fetch user info from GitHub
7. Create/link ButterflyFX account

Copyright (c) 2024-2026 Kenneth Bingham
All Rights Reserved
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import os
import secrets
import json
import urllib.request
import urllib.parse
import urllib.error


@dataclass
class GitHubUser:
    """GitHub user profile data"""
    id: int
    login: str
    name: str
    email: str
    avatar_url: str
    html_url: str
    bio: str = ""
    company: str = ""
    location: str = ""
    public_repos: int = 0
    followers: int = 0
    following: int = 0
    created_at: str = ""
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'GitHubUser':
        """Create from GitHub API response"""
        return cls(
            id=data.get('id', 0),
            login=data.get('login', ''),
            name=data.get('name') or data.get('login', ''),
            email=data.get('email') or '',
            avatar_url=data.get('avatar_url', ''),
            html_url=data.get('html_url', ''),
            bio=data.get('bio') or '',
            company=data.get('company') or '',
            location=data.get('location') or '',
            public_repos=data.get('public_repos', 0),
            followers=data.get('followers', 0),
            following=data.get('following', 0),
            created_at=data.get('created_at', ''),
        )


@dataclass
class GitHubOAuthState:
    """State for OAuth flow - prevents CSRF"""
    state: str
    created_at: datetime
    redirect_uri: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """State expires after 10 minutes"""
        return (datetime.now() - self.created_at).total_seconds() > 600


class GitHubOAuthError(Exception):
    """GitHub OAuth error"""
    pass


class GitHubOAuth:
    """
    GitHub OAuth 2.0 handler for ButterflyFX Developer Portal.
    
    Environment Variables Required:
        GITHUB_CLIENT_ID: OAuth App client ID
        GITHUB_CLIENT_SECRET: OAuth App client secret
        GITHUB_REDIRECT_URI: Callback URL (default: https://butterflyfx.us/api/auth/github/callback)
    
    Scopes Requested:
        - read:user (profile info)
        - user:email (email addresses)
    """
    
    AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_URL = "https://api.github.com/user"
    EMAILS_URL = "https://api.github.com/user/emails"
    
    # Required scopes
    SCOPES = ["read:user", "user:email"]
    
    def __init__(self, client_id: str = None, client_secret: str = None, 
                 redirect_uri: str = None):
        """
        Initialize GitHub OAuth handler.
        
        Args:
            client_id: GitHub OAuth App client ID (or use GITHUB_CLIENT_ID env var)
            client_secret: GitHub OAuth App client secret (or use GITHUB_CLIENT_SECRET env var)
            redirect_uri: Callback URL (or use GITHUB_REDIRECT_URI env var)
        """
        self.client_id = client_id or os.environ.get('GITHUB_CLIENT_ID', '')
        self.client_secret = client_secret or os.environ.get('GITHUB_CLIENT_SECRET', '')
        self.redirect_uri = redirect_uri or os.environ.get(
            'GITHUB_REDIRECT_URI', 
            'https://butterflyfx.us/api/auth/github/callback'
        )
        
        # Active OAuth states (in production, use Redis or database)
        self._states: Dict[str, GitHubOAuthState] = {}
        
        # Linked GitHub accounts: github_id -> butterflyfx_user_id
        self._linked_accounts: Dict[int, str] = {}
        
        # Data persistence
        self._data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data", "auth", "github_links.json"
        )
        self._load_links()
    
    def _load_links(self):
        """Load linked GitHub accounts from file"""
        try:
            if os.path.exists(self._data_path):
                with open(self._data_path, 'r') as f:
                    data = json.load(f)
                    self._linked_accounts = {int(k): v for k, v in data.items()}
        except Exception as e:
            print(f"Warning: Could not load GitHub links: {e}")
            self._linked_accounts = {}
    
    def _save_links(self):
        """Save linked GitHub accounts to file"""
        try:
            os.makedirs(os.path.dirname(self._data_path), exist_ok=True)
            with open(self._data_path, 'w') as f:
                json.dump({str(k): v for k, v in self._linked_accounts.items()}, f)
        except Exception as e:
            print(f"Warning: Could not save GitHub links: {e}")
    
    @property
    def is_configured(self) -> bool:
        """Check if GitHub OAuth is properly configured"""
        return bool(self.client_id and self.client_secret)
    
    def get_authorization_url(self, redirect_after: str = "/developer-portal.html") -> Tuple[str, str]:
        """
        Generate GitHub authorization URL.
        
        Args:
            redirect_after: Where to redirect after successful login
            
        Returns:
            Tuple of (authorization_url, state_token)
        """
        if not self.is_configured:
            raise GitHubOAuthError("GitHub OAuth not configured. Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET.")
        
        # Generate state token for CSRF protection
        state = secrets.token_urlsafe(32)
        self._states[state] = GitHubOAuthState(
            state=state,
            created_at=datetime.now(),
            redirect_uri=redirect_after,
        )
        
        # Clean up expired states
        self._cleanup_states()
        
        # Build authorization URL
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.SCOPES),
            'state': state,
            'allow_signup': 'true',
        }
        
        url = f"{self.AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"
        return url, state
    
    def _cleanup_states(self):
        """Remove expired OAuth states"""
        expired = [s for s, obj in self._states.items() if obj.is_expired]
        for s in expired:
            del self._states[s]
    
    def exchange_code(self, code: str, state: str) -> Tuple[str, GitHubUser]:
        """
        Exchange authorization code for access token and fetch user info.
        
        Args:
            code: Authorization code from GitHub callback
            state: State token from initial request
            
        Returns:
            Tuple of (access_token, GitHubUser)
            
        Raises:
            GitHubOAuthError: If exchange fails
        """
        # Validate state
        state_obj = self._states.get(state)
        if not state_obj:
            raise GitHubOAuthError("Invalid state token - possible CSRF attack")
        if state_obj.is_expired:
            del self._states[state]
            raise GitHubOAuthError("OAuth session expired - please try again")
        
        # Remove used state
        redirect_after = state_obj.redirect_uri
        del self._states[state]
        
        # Exchange code for token
        token_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
        }
        
        try:
            req = urllib.request.Request(
                self.TOKEN_URL,
                data=urllib.parse.urlencode(token_data).encode(),
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                token_response = json.loads(response.read().decode())
            
            if 'error' in token_response:
                raise GitHubOAuthError(f"GitHub error: {token_response.get('error_description', token_response['error'])}")
            
            access_token = token_response.get('access_token')
            if not access_token:
                raise GitHubOAuthError("No access token received from GitHub")
            
        except urllib.error.URLError as e:
            raise GitHubOAuthError(f"Network error exchanging code: {e}")
        
        # Fetch user info
        github_user = self._fetch_user_info(access_token)
        
        return access_token, github_user
    
    def _fetch_user_info(self, access_token: str) -> GitHubUser:
        """Fetch user profile from GitHub API"""
        try:
            req = urllib.request.Request(
                self.USER_URL,
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/vnd.github+json',
                    'X-GitHub-Api-Version': '2022-11-28',
                }
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                user_data = json.loads(response.read().decode())
            
            github_user = GitHubUser.from_api_response(user_data)
            
            # If email is not public, fetch from emails endpoint
            if not github_user.email:
                github_user.email = self._fetch_primary_email(access_token) or ''
            
            return github_user
            
        except urllib.error.URLError as e:
            raise GitHubOAuthError(f"Failed to fetch user info: {e}")
    
    def _fetch_primary_email(self, access_token: str) -> Optional[str]:
        """Fetch user's primary verified email"""
        try:
            req = urllib.request.Request(
                self.EMAILS_URL,
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/vnd.github+json',
                    'X-GitHub-Api-Version': '2022-11-28',
                }
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                emails = json.loads(response.read().decode())
            
            # Find primary verified email
            for email in emails:
                if email.get('primary') and email.get('verified'):
                    return email.get('email')
            
            # Fallback to any verified email
            for email in emails:
                if email.get('verified'):
                    return email.get('email')
            
            return None
            
        except urllib.error.URLError:
            return None
    
    def link_account(self, github_id: int, butterflyfx_user_id: str):
        """Link a GitHub account to a ButterflyFX user"""
        self._linked_accounts[github_id] = butterflyfx_user_id
        self._save_links()
    
    def unlink_account(self, github_id: int):
        """Unlink a GitHub account"""
        if github_id in self._linked_accounts:
            del self._linked_accounts[github_id]
            self._save_links()
    
    def get_linked_user(self, github_id: int) -> Optional[str]:
        """Get ButterflyFX user ID linked to a GitHub account"""
        return self._linked_accounts.get(github_id)
    
    def is_linked(self, github_id: int) -> bool:
        """Check if a GitHub account is linked"""
        return github_id in self._linked_accounts


# Singleton instance
_github_oauth: Optional[GitHubOAuth] = None


def get_github_oauth() -> GitHubOAuth:
    """Get the GitHub OAuth handler singleton"""
    global _github_oauth
    if _github_oauth is None:
        _github_oauth = GitHubOAuth()
    return _github_oauth
