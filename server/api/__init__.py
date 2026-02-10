"""
API routes for DimensionOS Platform.

Privacy-first REST API with:
- Authentication (register, login, refresh)
- User management (profile, status, tier)
- Payment status (update, get)
- Resource monitoring (metrics, usage)
"""

from server.api.auth_routes import router as auth_router
from server.api.user_routes import router as user_router
from server.api.payment_routes import router as payment_router
from server.api.resource_routes import router as resource_router


__all__ = [
    "auth_router",
    "user_router",
    "payment_router",
    "resource_router",
]

