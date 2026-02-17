"""
ButterflyFX Authentication Service
===================================

Handles user authentication, session management, and authorization.

Copyright (c) 2024-2026 Kenneth Bingham
All Rights Reserved
"""

from typing import Dict, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import secrets
import json
import os
import re

from .models import User, UserTier, Session, BetaCode, AccessLevel, UserPermissions


class AuthError(Exception):
    """Base authentication error"""
    pass


class InvalidCredentialsError(AuthError):
    """Invalid username or password"""
    pass


class UserNotFoundError(AuthError):
    """User does not exist"""
    pass


class UserExistsError(AuthError):
    """Username or email already taken"""
    pass


class InsufficientPermissionsError(AuthError):
    """User does not have required permissions"""
    pass


class SessionExpiredError(AuthError):
    """Session has expired"""
    pass


class InvalidBetaCodeError(AuthError):
    """Beta code is invalid or expired"""
    pass


class AuthService:
    """
    Authentication service with tier-based access control.
    
    Features:
    - User registration and login
    - Password hashing with salt
    - Session management
    - Tier-based permissions
    - Beta code redemption
    """
    
    # File paths for persistence
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "auth")
    USERS_FILE = "users.json"
    SESSIONS_FILE = "sessions.json"
    BETA_CODES_FILE = "beta_codes.json"
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self.beta_codes: Dict[str, BetaCode] = {}
        
        # Ensure data directory exists
        os.makedirs(self.DATA_DIR, exist_ok=True)
        
        # Load data
        self._load_data()
        
        # Ensure superuser exists
        self._ensure_superuser()
        
        self._initialized = True
    
    def _ensure_superuser(self):
        """Ensure the superuser account exists"""
        superuser_email = "kenneth@butterflyfx.us"
        
        # Check if superuser exists
        for user in self.users.values():
            if user.tier == UserTier.SUPERUSER:
                return
        
        # Create superuser - Kenneth Bingham
        superuser = User(
            id="superuser-001",
            username="kenneth",
            email=superuser_email,
            password_hash=self._hash_password("butterfly2026!"),  # Default password - CHANGE IN PRODUCTION
            tier=UserTier.SUPERUSER,
            is_active=True,
            is_verified=True,
            display_name="Kenneth Bingham",
            bio="Creator of ButterflyFX",
            metadata={"founder": True}
        )
        
        self.users[superuser.id] = superuser
        self._save_users()
        print(f"✓ Superuser account created: {superuser.username}")
    
    # =========================================================================
    # PASSWORD HANDLING
    # =========================================================================
    
    def _hash_password(self, password: str, salt: str = None) -> str:
        """Hash password with salt using SHA-256"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Multiple rounds of hashing
        hashed = password
        for _ in range(10000):
            hashed = hashlib.sha256(f"{salt}{hashed}".encode()).hexdigest()
        
        return f"{salt}:{hashed}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, stored_hash = password_hash.split(":")
            computed = self._hash_password(password, salt)
            return computed == password_hash
        except:
            return False
    
    # =========================================================================
    # USER MANAGEMENT
    # =========================================================================
    
    def register(self, username: str, email: str, password: str, 
                 tier: UserTier = UserTier.USER,
                 beta_code: str = None,
                 accept_tos: bool = True,
                 accept_dev_tos: bool = False,
                 accept_beta_tos: bool = False) -> User:
        """
        Register a new user.
        
        Args:
            username: Unique username
            email: Email address
            password: Plain text password
            tier: Initial tier (default: USER)
            beta_code: Required for BETA tier - superuser generated invite code
            accept_tos: Accept general Terms of Service
            accept_dev_tos: Accept Developer TOS (required for DEV tier)
            accept_beta_tos: Accept Beta TOS (required for BETA tier)
            
        Returns:
            Created User object
            
        Raises:
            UserExistsError: If username or email already taken
            InvalidBetaCodeError: If beta code is invalid
            AuthError: If TOS not accepted for tier
        """
        # Validate username
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
            raise AuthError("Username must be 3-20 alphanumeric characters or underscores")
        
        # Check for existing user
        for user in self.users.values():
            if user.username.lower() == username.lower():
                raise UserExistsError(f"Username '{username}' already taken")
            if user.email.lower() == email.lower():
                raise UserExistsError(f"Email '{email}' already registered")
        
        # Handle beta code for BETA tier
        if beta_code:
            code_obj = self.beta_codes.get(beta_code)
            if not code_obj or not code_obj.is_valid:
                raise InvalidBetaCodeError("Invalid or expired beta invitation code")
            if not accept_beta_tos:
                raise AuthError("Must accept Beta Tester Terms of Service")
            tier = UserTier.BETA
        
        # DEV tier requires dev TOS
        if tier == UserTier.DEV and not accept_dev_tos:
            raise AuthError("Must accept Developer Terms of Service to register as developer")
        
        # General TOS is always required
        if not accept_tos:
            raise AuthError("Must accept Terms of Service")
        
        # Create user
        user = User(
            id=f"user-{secrets.token_hex(8)}",
            username=username,
            email=email,
            password_hash=self._hash_password(password),
            tier=tier,
            created_at=datetime.now(),
            is_active=True,
        )
        
        # Accept TOS
        user.accept_tos()
        
        # Handle DEV tier - auto generate API key
        if tier == UserTier.DEV:
            user.accept_dev_tos()
            user.generate_api_key()
            print(f"✓ Developer API key generated for {username}")
        
        # Handle BETA tier
        if tier == UserTier.BETA and beta_code:
            user.accept_beta_tos()
            user.generate_api_key()
            user.beta_joined = datetime.now()
            user.beta_code = beta_code
            
            # Get invited by from the beta code
            code_obj = self.beta_codes[beta_code]
            user.beta_invited_by = code_obj.created_by
            
            # Mark beta code as used
            code_obj.use(user.id)
            self._save_beta_codes()
            print(f"✓ Beta tester registered: {username} (invited by {code_obj.created_by})")
        
        self.users[user.id] = user
        self._save_users()
        
        return user
    
    def register_as_dev(self, username: str, email: str, password: str,
                        accept_dev_tos: bool = True) -> Tuple[User, str]:
        """
        Register as a developer - auto generates API key.
        
        Args:
            username: Unique username
            email: Email address
            password: Plain text password
            accept_dev_tos: Must be True to register as dev
            
        Returns:
            Tuple of (User, API key string)
        """
        if not accept_dev_tos:
            raise AuthError("Must accept Developer Terms of Service")
        
        user = self.register(
            username=username,
            email=email,
            password=password,
            tier=UserTier.DEV,
            accept_tos=True,
            accept_dev_tos=True,
        )
        
        return user, user.api_key
    
    def register_as_beta(self, username: str, email: str, password: str,
                         beta_code: str, accept_beta_tos: bool = True) -> Tuple[User, str]:
        """
        Register as a beta tester using an invitation code.
        
        Args:
            username: Unique username
            email: Email address
            password: Plain text password
            beta_code: Invitation code from superuser
            accept_beta_tos: Must be True to register as beta
            
        Returns:
            Tuple of (User, API key string)
        """
        if not accept_beta_tos:
            raise AuthError("Must accept Beta Tester Terms of Service")
        
        user = self.register(
            username=username,
            email=email,
            password=password,
            beta_code=beta_code,
            accept_tos=True,
            accept_beta_tos=True,
        )
        
        return user, user.api_key
    
    def login(self, username_or_email: str, password: str, 
              ip: str = "", user_agent: str = "") -> Tuple[User, Session]:
        """
        Authenticate user and create session.
        
        Args:
            username_or_email: Username or email
            password: Plain text password
            ip: Client IP address
            user_agent: Client user agent
            
        Returns:
            Tuple of (User, Session)
            
        Raises:
            InvalidCredentialsError: If credentials are wrong
        """
        # Find user
        user = None
        for u in self.users.values():
            if u.username.lower() == username_or_email.lower() or \
               u.email.lower() == username_or_email.lower():
                user = u
                break
        
        if not user:
            raise InvalidCredentialsError("Invalid username or password")
        
        if not user.is_active:
            raise InvalidCredentialsError("Account is disabled")
        
        if not self._verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid username or password")
        
        # Update last login
        user.last_login = datetime.now()
        self._save_users()
        
        # Create session
        session = Session.create(user.id, ip, user_agent)
        self.sessions[session.id] = session
        self._save_sessions()
        
        return user, session
    
    def logout(self, session_id: str) -> bool:
        """Invalidate a session"""
        if session_id in self.sessions:
            self.sessions[session_id].is_active = False
            self._save_sessions()
            return True
        return False
    
    def get_user_by_session(self, token: str) -> Optional[User]:
        """Get user from session token"""
        for session in self.sessions.values():
            if session.token == token and session.is_valid:
                user = self.users.get(session.user_id)
                if user and user.is_active:
                    return user
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        for user in self.users.values():
            if user.username.lower() == username.lower():
                return user
        return None
    
    def list_users(self, tier: UserTier = None) -> List[User]:
        """List all users, optionally filtered by tier"""
        users = list(self.users.values())
        if tier is not None:
            users = [u for u in users if u.tier == tier]
        return sorted(users, key=lambda u: (u.tier, u.username), reverse=True)
    
    def update_user_tier(self, user_id: str, new_tier: UserTier, 
                         by_user: User) -> User:
        """Update a user's tier (requires superuser)"""
        if not by_user.is_superuser:
            raise InsufficientPermissionsError("Only superuser can change tiers")
        
        user = self.users.get(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
        # Cannot change superuser tier
        if user.tier == UserTier.SUPERUSER and new_tier != UserTier.SUPERUSER:
            raise InsufficientPermissionsError("Cannot demote superuser")
        
        user.tier = new_tier
        self._save_users()
        return user
    
    def delete_user(self, user_id: str, by_user: User) -> bool:
        """Delete a user (requires admin or self)"""
        user = self.users.get(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
        # Cannot delete superuser
        if user.tier == UserTier.SUPERUSER:
            raise InsufficientPermissionsError("Cannot delete superuser")
        
        # Must be superuser, or deleting own account
        if not by_user.is_superuser and by_user.id != user_id:
            raise InsufficientPermissionsError("Cannot delete other users")
        
        del self.users[user_id]
        self._save_users()
        
        # Invalidate sessions
        for session_id, session in list(self.sessions.items()):
            if session.user_id == user_id:
                del self.sessions[session_id]
        self._save_sessions()
        
        return True
    
    # =========================================================================
    # BETA CODE MANAGEMENT (SUPERUSER ONLY)
    # =========================================================================
    
    def create_beta_code(self, by_user: User, max_uses: int = 1, 
                         expires_days: int = 30,
                         note: str = "") -> BetaCode:
        """
        Create a new beta invitation code (superuser only).
        
        Beta codes are used to invite beta testers. Only the superuser
        can create these codes.
        
        Args:
            by_user: Must be superuser
            max_uses: How many people can use this code
            expires_days: Days until code expires (0 = never)
            note: Optional note about who this is for
            
        Returns:
            BetaCode object with the invitation code
        """
        if not by_user.is_superuser:
            raise InsufficientPermissionsError("Only superuser can create beta invitation codes")
        
        code = BetaCode.generate(by_user.id, max_uses, expires_days)
        if note:
            code.metadata = {"note": note}
        self.beta_codes[code.code] = code
        self._save_beta_codes()
        
        return code
    
    def generate_beta_invite_email(self, code: BetaCode, recipient_email: str,
                                    recipient_name: str = "") -> Dict[str, str]:
        """
        Generate email content for beta invitation.
        
        Returns dict with 'subject' and 'body' for sending via email.
        This doesn't send the email - you pass this to your email service.
        """
        subject = "🧪 You're Invited to the ButterflyFX Beta Program!"
        
        body = f"""Hi {recipient_name or 'there'}!

You've been personally invited to join the ButterflyFX Beta Program!

As a beta tester, you'll get:
🎁 FREE access to all features
📦 Developer source code access
🏆 Free production license FOREVER
🚀 Early access to unreleased features
💬 Direct feedback channel to the development team

Your Beta Invitation Code:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{code.code}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

To get started:
1. Visit https://butterflyfx.us/register
2. Select "Join as Beta Tester"
3. Enter your invitation code
4. Accept the Beta Tester Terms of Service

This code expires: {code.expires_at.strftime('%B %d, %Y') if code.expires_at else 'Never'}
Uses remaining: {code.max_uses - code.uses}

Welcome to the future of dimensional computing!

— Kenneth Bingham
Creator of ButterflyFX

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ButterflyFX | Dimensional Computing
https://butterflyfx.us
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        return {
            "subject": subject,
            "body": body,
            "recipient": recipient_email,
            "code": code.code,
        }
    
    def list_beta_codes(self, by_user: User, include_expired: bool = False) -> List[BetaCode]:
        """List all beta codes (superuser only)"""
        if not by_user.is_superuser:
            raise InsufficientPermissionsError("Only superuser can view beta codes")
        
        codes = list(self.beta_codes.values())
        if not include_expired:
            codes = [c for c in codes if c.is_valid]
        return sorted(codes, key=lambda c: c.created_at, reverse=True)
    
    def revoke_beta_code(self, code: str, by_user: User) -> bool:
        """Revoke a beta code (superuser only)"""
        if not by_user.is_superuser:
            raise InsufficientPermissionsError("Only superuser can revoke beta codes")
        
        if code in self.beta_codes:
            self.beta_codes[code].is_active = False
            self._save_beta_codes()
            return True
        return False
    
    # =========================================================================
    # API KEY MANAGEMENT
    # =========================================================================
    #
    # API KEYS ARE SINGLE-USE:
    # - Generated once at registration for DEV and BETA tiers
    # - Cannot be regenerated by anyone (permanent assignment)
    # - Only superuser can revoke keys
    # - If revoked, user loses API access permanently
    # =========================================================================
    
    def revoke_api_key(self, user_id: str, by_user: User) -> bool:
        """
        Revoke a user's API key (SUPERUSER ONLY).
        
        API keys are single-use and permanent. Once revoked, the user
        loses API access forever - there is no way to regenerate.
        
        Args:
            user_id: The user whose key to revoke
            by_user: Must be superuser
            
        Returns:
            True if revoked
            
        Raises:
            InsufficientPermissionsError: If not superuser
        """
        if not by_user.is_superuser:
            raise InsufficientPermissionsError("Only superuser can revoke API keys")
        
        user = self.users.get(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
        if not user.api_key:
            raise AuthError(f"User {user.username} has no API key to revoke")
        
        old_key = user.api_key
        user.revoke_api_key()
        user.metadata = user.metadata or {}
        user.metadata["api_key_revoked_at"] = datetime.now().isoformat()
        user.metadata["api_key_revoked_by"] = by_user.id
        self._save_users()
        
        print(f"⚠️ API key revoked for {user.username} by {by_user.username}")
        return True
    
    def validate_api_key(self, api_key: str) -> Optional[User]:
        """Validate an API key and return the associated user"""
        if not api_key:
            return None
        
        for user in self.users.values():
            if user.api_key == api_key and user.is_active:
                return user
        return None
    
    # =========================================================================
    # PERMISSION CHECKING
    # =========================================================================
    
    def check_permission(self, user: User, permission: str) -> bool:
        """Check if user has a specific permission"""
        perms = user.permissions
        return getattr(perms, permission, False)
    
    def check_access_level(self, user: User, required: AccessLevel) -> bool:
        """Check if user has required access level"""
        return user.can_access(required)
    
    def can_download(self, user: User, package_type: str) -> bool:
        """Check if user can download a package type"""
        return user.can_download(package_type)
    
    # =========================================================================
    # DATA PERSISTENCE
    # =========================================================================
    
    def _load_data(self):
        """Load all data from JSON files"""
        self._load_users()
        self._load_sessions()
        self._load_beta_codes()
    
    def _load_users(self):
        """Load users from file"""
        path = os.path.join(self.DATA_DIR, self.USERS_FILE)
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    for user_data in data:
                        user = User.from_dict(user_data)
                        self.users[user.id] = user
            except Exception as e:
                print(f"Error loading users: {e}")
    
    def _save_users(self):
        """Save users to file"""
        path = os.path.join(self.DATA_DIR, self.USERS_FILE)
        data = [
            {**u.to_dict(include_sensitive=True), "password_hash": u.password_hash}
            for u in self.users.values()
        ]
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load_sessions(self):
        """Load sessions from file"""
        path = os.path.join(self.DATA_DIR, self.SESSIONS_FILE)
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    for sess_data in data:
                        session = Session(
                            id=sess_data["id"],
                            user_id=sess_data["user_id"],
                            token=sess_data["token"],
                            created_at=datetime.fromisoformat(sess_data["created_at"]),
                            expires_at=datetime.fromisoformat(sess_data["expires_at"]),
                            ip_address=sess_data.get("ip_address", ""),
                            is_active=sess_data.get("is_active", True),
                        )
                        if session.is_valid:
                            self.sessions[session.id] = session
            except Exception as e:
                print(f"Error loading sessions: {e}")
    
    def _save_sessions(self):
        """Save sessions to file"""
        path = os.path.join(self.DATA_DIR, self.SESSIONS_FILE)
        # Only save valid sessions
        data = [s.to_dict() for s in self.sessions.values() if s.is_valid]
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load_beta_codes(self):
        """Load beta codes from file"""
        path = os.path.join(self.DATA_DIR, self.BETA_CODES_FILE)
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    for code_data in data:
                        code = BetaCode(
                            code=code_data["code"],
                            created_by=code_data["created_by"],
                            created_at=datetime.fromisoformat(code_data["created_at"]),
                            expires_at=datetime.fromisoformat(code_data["expires_at"]) if code_data.get("expires_at") else None,
                            max_uses=code_data.get("max_uses", 1),
                            uses=code_data.get("uses", 0),
                            used_by=code_data.get("used_by", []),
                            is_active=code_data.get("is_active", True),
                        )
                        self.beta_codes[code.code] = code
            except Exception as e:
                print(f"Error loading beta codes: {e}")
    
    def _save_beta_codes(self):
        """Save beta codes to file"""
        path = os.path.join(self.DATA_DIR, self.BETA_CODES_FILE)
        data = []
        for code in self.beta_codes.values():
            data.append({
                "code": code.code,
                "created_by": code.created_by,
                "created_at": code.created_at.isoformat(),
                "expires_at": code.expires_at.isoformat() if code.expires_at else None,
                "max_uses": code.max_uses,
                "uses": code.uses,
                "used_by": code.used_by,
                "is_active": code.is_active,
            })
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

def get_auth_service() -> AuthService:
    """Get the singleton auth service instance"""
    return AuthService()


# =============================================================================
# DECORATORS FOR FLASK/FASTAPI
# =============================================================================

def requires_auth(f: Callable) -> Callable:
    """Decorator that requires user to be logged in"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # This should be overridden by the web framework integration
        raise NotImplementedError("Framework-specific implementation needed")
    return decorated


def requires_tier(min_tier: UserTier) -> Callable:
    """Decorator that requires minimum tier"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            # This should be overridden by the web framework integration
            raise NotImplementedError("Framework-specific implementation needed")
        return decorated
    return decorator


def requires_permission(permission: str) -> Callable:
    """Decorator that requires specific permission"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            # This should be overridden by the web framework integration
            raise NotImplementedError("Framework-specific implementation needed")
        return decorated
    return decorator


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ButterflyFX Authentication Service Test")
    print("=" * 60)
    
    auth = get_auth_service()
    
    print(f"\n✓ Auth service initialized")
    print(f"  Users: {len(auth.users)}")
    print(f"  Sessions: {len(auth.sessions)}")
    print(f"  Beta codes: {len(auth.beta_codes)}")
    
    # List users
    print("\n--- Users ---")
    for user in auth.list_users():
        print(f"  {user.tier_badge} {user.username} ({user.tier_name})")
    
    # Test superuser login
    print("\n--- Superuser Login Test ---")
    try:
        user, session = auth.login("kenneth", "butterfly2026!")
        print(f"  ✓ Logged in as: {user.username}")
        print(f"  Tier: {user.tier_name}")
        print(f"  Session token: {session.token[:20]}...")
        
        # Test permissions
        print(f"\n  Permissions:")
        perms = user.permissions
        print(f"    can_download_opensource: {perms.can_download_opensource}")
        print(f"    can_download_premium: {perms.can_download_premium}")
        print(f"    can_access_admin: {perms.can_access_admin}")
        print(f"    can_manage_users: {perms.can_manage_users}")
        print(f"    bypass_licensing: {perms.bypass_licensing}")
        
        # Create beta code
        print("\n--- Beta Code Test ---")
        beta_code = auth.create_beta_code(user, max_uses=5, expires_days=90)
        print(f"  Created beta code: {beta_code.code}")
        
        # Register test user with beta code
        print("\n--- Beta User Registration ---")
        try:
            beta_user = auth.register(
                username="betatester",
                email="beta@test.com",
                password="test123",
                beta_code=beta_code.code
            )
            print(f"  ✓ Beta user created: {beta_user.username}")
            print(f"  Tier: {beta_user.tier_name}")
            print(f"  Free production: {beta_user.permissions.has_free_production}")
        except UserExistsError:
            print(f"  (Beta user already exists)")
        
        # Logout
        auth.logout(session.id)
        print(f"\n✓ Logged out")
        
    except InvalidCredentialsError as e:
        print(f"  ✗ Login failed: {e}")
    
    print("\n" + "=" * 60)
    print("Auth Service Test Complete")
    print("=" * 60)
