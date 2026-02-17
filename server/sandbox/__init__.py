"""
ButterflyFX Sandbox System
===========================

Isolated sandbox environments for Beta testers and Developers.

Sandbox Types:
- BETA: VPS-hosted, includes ALL apps, can bring own AI
- DEV: Local instance, only their own apps, can bring own AI

Features:
- Isolated file system
- Resource limits (CPU, memory, storage)
- Custom AI integration
- App deployment
- No impact on production

Copyright (c) 2024-2026 Kenneth Bingham
All Rights Reserved
"""

from .models import (
    Sandbox,
    SandboxType,
    SandboxStatus,
    SandboxConfig,
    AIIntegration,
    AIProvider,
    SandboxApp,
)

from .service import (
    SandboxService,
    get_sandbox_service,
    SandboxError,
    SandboxNotFoundError,
    SandboxLimitError,
    AIIntegrationError,
)

__all__ = [
    # Models
    'Sandbox',
    'SandboxType',
    'SandboxStatus',
    'SandboxConfig',
    'AIIntegration',
    'AIProvider',
    'SandboxApp',
    
    # Service
    'SandboxService',
    'get_sandbox_service',
    'SandboxError',
    'SandboxNotFoundError',
    'SandboxLimitError',
    'AIIntegrationError',
]
