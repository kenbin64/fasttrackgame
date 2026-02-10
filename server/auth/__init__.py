"""
Authentication module for DimensionOS Platform.

Privacy-first authentication with:
- Anonymous user IDs (SHA256 hashes)
- Bcrypt password hashing
- JWT tokens
- Service status checking
"""

from server.auth.auth_service import (
    generate_anonymous_id,
    register_user,
    login_user
)

from server.auth.password_utils import (
    hash_password,
    verify_password,
    is_password_strong
)

from server.auth.jwt_utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token,
    refresh_access_token
)

from server.auth.dependencies import (
    get_current_user,
    get_active_user,
    get_full_access_user,
    check_trial_status,
    check_payment_status
)


__all__ = [
    # Auth service
    "generate_anonymous_id",
    "register_user",
    "login_user",
    
    # Password utils
    "hash_password",
    "verify_password",
    "is_password_strong",
    
    # JWT utils
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "verify_token",
    "refresh_access_token",
    
    # Dependencies
    "get_current_user",
    "get_active_user",
    "get_full_access_user",
    "check_trial_status",
    "check_payment_status",
]

