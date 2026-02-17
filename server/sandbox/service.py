"""
ButterflyFX Sandbox Service
============================

Manages sandbox environments for Beta testers and Developers.

Sandbox Types:
- BETA_VPS: Server-hosted, includes ALL apps
- DEV_LOCAL: Local instance, only dev's own apps

AI Integration:
- ALWAYS OPTIONAL - never default
- User must explicitly enable and configure
- BYOA (Bring Your Own AI) supported

Copyright (c) 2024-2026 Kenneth Bingham
All Rights Reserved
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import secrets
import json
import os

from .models import (
    Sandbox, SandboxType, SandboxStatus, SandboxConfig,
    AIIntegration, AIProvider, SandboxApp
)

# Import auth to check user tiers
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from server.auth.models import User, UserTier


class SandboxError(Exception):
    """Base sandbox error"""
    pass


class SandboxNotFoundError(SandboxError):
    """Sandbox does not exist"""
    pass


class SandboxLimitError(SandboxError):
    """User has reached sandbox limit"""
    pass


class AIIntegrationError(SandboxError):
    """Error with AI integration"""
    pass


class SandboxService:
    """
    Sandbox service for managing isolated environments.
    
    Beta Sandboxes (VPS):
    - Server-hosted on butterflyfx.us
    - Includes ALL ButterflyFX apps
    - Full testing environment
    - Optional AI integration (BYOA)
    
    Dev Sandboxes (Local):
    - Runs on developer's machine
    - Only includes dev's own apps
    - For app development and testing
    - Optional AI integration (BYOA)
    
    AI IS ALWAYS A CHOICE - NEVER DEFAULT.
    """
    
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "sandboxes")
    SANDBOXES_FILE = "sandboxes.json"
    
    # Limits
    MAX_SANDBOXES_PER_BETA = 3
    MAX_SANDBOXES_PER_DEV = 5
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.sandboxes: Dict[str, Sandbox] = {}
        
        os.makedirs(self.DATA_DIR, exist_ok=True)
        self._load_data()
        
        self._initialized = True
    
    # =========================================================================
    # SANDBOX CREATION
    # =========================================================================
    
    def create_beta_sandbox(self, user: User, name: str) -> Sandbox:
        """
        Create a VPS sandbox for beta tester.
        
        - Includes ALL ButterflyFX apps
        - AI is NOT enabled by default
        """
        if not user.is_beta:
            raise SandboxError("Only beta testers can create VPS sandboxes")
        
        # Check limit
        user_sandboxes = self.get_user_sandboxes(user)
        if len(user_sandboxes) >= self.MAX_SANDBOXES_PER_BETA:
            raise SandboxLimitError(f"Maximum {self.MAX_SANDBOXES_PER_BETA} sandboxes allowed")
        
        sandbox = Sandbox.create_beta_vps(user.id, name)
        
        # Load ALL marketplace apps into sandbox
        self._load_all_apps_for_beta(sandbox)
        
        self.sandboxes[sandbox.id] = sandbox
        self._save_data()
        
        print(f"✓ Beta sandbox created: {sandbox.name} ({sandbox.id})")
        return sandbox
    
    def create_dev_sandbox(self, user: User, name: str, 
                           local_path: str = "") -> Sandbox:
        """
        Create a local sandbox for developer.
        
        - Only includes dev's own apps
        - AI is NOT enabled by default
        """
        if not user.is_dev:
            raise SandboxError("Only developers can create local sandboxes")
        
        # Check limit
        user_sandboxes = self.get_user_sandboxes(user)
        if len(user_sandboxes) >= self.MAX_SANDBOXES_PER_DEV:
            raise SandboxLimitError(f"Maximum {self.MAX_SANDBOXES_PER_DEV} sandboxes allowed")
        
        sandbox = Sandbox.create_dev_local(user.id, name, local_path)
        
        # Load only dev's own apps
        self._load_dev_apps(sandbox, user.id)
        
        self.sandboxes[sandbox.id] = sandbox
        self._save_data()
        
        print(f"✓ Dev sandbox created: {sandbox.name} ({sandbox.id})")
        return sandbox
    
    def _load_all_apps_for_beta(self, sandbox: Sandbox) -> None:
        """Load all ButterflyFX apps into beta sandbox"""
        # In production, this would load from marketplace
        # For now, add placeholder for all available apps
        sandbox.metadata["apps_loaded"] = "all"
        sandbox.metadata["apps_loaded_at"] = datetime.now().isoformat()
    
    def _load_dev_apps(self, sandbox: Sandbox, dev_id: str) -> None:
        """Load only dev's own apps into sandbox"""
        sandbox.metadata["apps_loaded"] = "owned"
        sandbox.metadata["apps_owner"] = dev_id
        sandbox.metadata["apps_loaded_at"] = datetime.now().isoformat()
    
    # =========================================================================
    # AI INTEGRATION (ALWAYS OPTIONAL)
    # =========================================================================
    
    def enable_ai(self, sandbox_id: str, user: User,
                  provider: AIProvider, api_key: str, 
                  model: str = "") -> AIIntegration:
        """
        Enable AI integration for a sandbox.
        
        AI IS ALWAYS A CHOICE - NEVER DEFAULT.
        User must explicitly call this to enable AI.
        """
        sandbox = self.get_sandbox(sandbox_id)
        
        # Verify ownership
        if sandbox.owner_id != user.id and not user.is_superuser:
            raise SandboxError("You don't own this sandbox")
        
        # Validate provider
        if provider == AIProvider.NONE:
            raise AIIntegrationError("Must specify an AI provider")
        
        # Validate API key (except for local Ollama)
        if not api_key and provider != AIProvider.OLLAMA:
            raise AIIntegrationError("API key required for this provider")
        
        # Enable AI
        sandbox.enable_ai(provider, api_key, model)
        self._save_data()
        
        print(f"✓ AI enabled for sandbox {sandbox.name}: {provider.name}")
        return sandbox.ai
    
    def disable_ai(self, sandbox_id: str, user: User) -> bool:
        """Disable AI integration for a sandbox"""
        sandbox = self.get_sandbox(sandbox_id)
        
        if sandbox.owner_id != user.id and not user.is_superuser:
            raise SandboxError("You don't own this sandbox")
        
        sandbox.disable_ai()
        self._save_data()
        
        print(f"✓ AI disabled for sandbox {sandbox.name}")
        return True
    
    def get_ai_status(self, sandbox_id: str) -> Dict:
        """Get AI integration status (without exposing API key)"""
        sandbox = self.get_sandbox(sandbox_id)
        
        return {
            "enabled": sandbox.ai.enabled,
            "provider": sandbox.ai.provider.name if sandbox.ai.enabled else None,
            "model": sandbox.ai.model if sandbox.ai.enabled else None,
            "total_requests": sandbox.ai.total_requests,
            "total_tokens_used": sandbox.ai.total_tokens_used,
        }
    
    # =========================================================================
    # SANDBOX MANAGEMENT
    # =========================================================================
    
    def get_sandbox(self, sandbox_id: str) -> Sandbox:
        """Get a sandbox by ID"""
        sandbox = self.sandboxes.get(sandbox_id)
        if not sandbox:
            raise SandboxNotFoundError(f"Sandbox {sandbox_id} not found")
        return sandbox
    
    def get_user_sandboxes(self, user: User) -> List[Sandbox]:
        """Get all sandboxes owned by user"""
        return [s for s in self.sandboxes.values() 
                if s.owner_id == user.id and s.status != SandboxStatus.DELETED]
    
    def start_sandbox(self, sandbox_id: str, user: User) -> Sandbox:
        """Start a sandbox"""
        sandbox = self.get_sandbox(sandbox_id)
        
        if sandbox.owner_id != user.id and not user.is_superuser:
            raise SandboxError("You don't own this sandbox")
        
        sandbox.start()
        self._save_data()
        
        print(f"✓ Sandbox started: {sandbox.name}")
        return sandbox
    
    def stop_sandbox(self, sandbox_id: str, user: User) -> Sandbox:
        """Stop a sandbox"""
        sandbox = self.get_sandbox(sandbox_id)
        
        if sandbox.owner_id != user.id and not user.is_superuser:
            raise SandboxError("You don't own this sandbox")
        
        sandbox.stop()
        self._save_data()
        
        print(f"✓ Sandbox stopped: {sandbox.name}")
        return sandbox
    
    def delete_sandbox(self, sandbox_id: str, user: User) -> bool:
        """Delete a sandbox"""
        sandbox = self.get_sandbox(sandbox_id)
        
        if sandbox.owner_id != user.id and not user.is_superuser:
            raise SandboxError("You don't own this sandbox")
        
        sandbox.delete()
        self._save_data()
        
        print(f"✓ Sandbox deleted: {sandbox.name}")
        return True
    
    # =========================================================================
    # APP MANAGEMENT
    # =========================================================================
    
    def deploy_app(self, sandbox_id: str, user: User, 
                   app_name: str, source_path: str,
                   version: str = "1.0.0") -> SandboxApp:
        """Deploy an app to a sandbox"""
        sandbox = self.get_sandbox(sandbox_id)
        
        if sandbox.owner_id != user.id and not user.is_superuser:
            raise SandboxError("You don't own this sandbox")
        
        app = SandboxApp(
            id=f"app-{secrets.token_hex(8)}",
            name=app_name,
            version=version,
            source_type="local",
            source_path=source_path,
            is_owned_by_sandbox_owner=True,
        )
        
        # Dev sandboxes can only have their own apps
        sandbox.add_app(app)
        self._save_data()
        
        print(f"✓ App deployed to sandbox: {app.name}")
        return app
    
    def remove_app(self, sandbox_id: str, user: User, app_id: str) -> bool:
        """Remove an app from a sandbox"""
        sandbox = self.get_sandbox(sandbox_id)
        
        if sandbox.owner_id != user.id and not user.is_superuser:
            raise SandboxError("You don't own this sandbox")
        
        result = sandbox.remove_app(app_id)
        if result:
            self._save_data()
        return result
    
    # =========================================================================
    # DATA PERSISTENCE
    # =========================================================================
    
    def _load_data(self):
        """Load sandboxes from file"""
        filepath = os.path.join(self.DATA_DIR, self.SANDBOXES_FILE)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                for sandbox_data in data:
                    sandbox = Sandbox.from_dict(sandbox_data)
                    self.sandboxes[sandbox.id] = sandbox
            except Exception as e:
                print(f"Error loading sandboxes: {e}")
    
    def _save_data(self):
        """Save sandboxes to file"""
        filepath = os.path.join(self.DATA_DIR, self.SANDBOXES_FILE)
        with open(filepath, 'w') as f:
            json.dump([s.to_dict() for s in self.sandboxes.values()], f, indent=2)


# Singleton accessor
_sandbox_service = None

def get_sandbox_service() -> SandboxService:
    """Get the sandbox service singleton"""
    global _sandbox_service
    if _sandbox_service is None:
        _sandbox_service = SandboxService()
    return _sandbox_service
