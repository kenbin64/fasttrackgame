"""
DimensionOS Platform - Main Application

Privacy-first cloud platform with:
- Anonymous user IDs (NO PII on server)
- Client-side payment processing
- Resource monitoring (metrics only)
- TOS enforcement (pattern-based)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from server.database import init_db
from server.api import (
    auth_router,
    user_router,
    payment_router,
    resource_router
)


# ============================================================================
# LIFESPAN EVENTS
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    
    Startup:
    - Initialize database
    - Seed resource allocations
    
    Shutdown:
    - Cleanup resources
    """
    # Startup
    print("🚀 Starting DimensionOS Platform...")
    init_db()
    print("✅ Database initialized")
    
    yield
    
    # Shutdown
    print("👋 Shutting down DimensionOS Platform...")


# ============================================================================
# APPLICATION
# ============================================================================

app = FastAPI(
    title="DimensionOS Platform",
    description="Privacy-first cloud platform with dimensional computing",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================================
# CORS MIDDLEWARE
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ROUTES
# ============================================================================

# Include API routers
app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(payment_router, prefix="/api")
app.include_router(resource_router, prefix="/api")


# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "DimensionOS Platform",
        "version": "1.0.0",
        "description": "Privacy-first cloud platform with dimensional computing",
        "docs": "/docs",
        "privacy": "NO PII stored on server - all personal data on client side"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "DimensionOS Platform"
    }


@app.get("/api/info")
async def api_info():
    """API information endpoint."""
    return {
        "api_version": "1.0.0",
        "endpoints": {
            "auth": {
                "register": "POST /api/auth/register",
                "login": "POST /api/auth/login",
                "refresh": "POST /api/auth/refresh",
                "logout": "POST /api/auth/logout"
            },
            "user": {
                "me": "GET /api/user/me",
                "status": "GET /api/user/status",
                "update_tier": "PUT /api/user/tier"
            },
            "payment": {
                "update_status": "POST /api/payment/status",
                "get_status": "GET /api/payment/status"
            },
            "resources": {
                "metrics": "GET /api/resources/metrics",
                "usage": "GET /api/resources/usage"
            }
        },
        "privacy": {
            "pii_on_server": False,
            "payment_details_on_server": False,
            "content_inspection": False,
            "anonymous_user_ids": True,
            "client_side_encryption": True
        }
    }


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "server.main_platform:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

