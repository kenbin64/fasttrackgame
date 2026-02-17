"""
ButterflyFX Server API

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)

API route handlers for the ButterflyFX server.
"""

from .auth_routes import AuthAPI, get_auth_api

__all__ = [
    'AuthAPI',
    'get_auth_api',
]
