"""
ButterflyFX Sandbox Models
===========================

Sandbox environments for Beta testers and Developers.

Types:
- BETA_VPS: Server-hosted sandbox with ALL apps
- DEV_LOCAL: Local instance with only dev's own apps

AI Integration:
- ALWAYS OPTIONAL - never default
- User must explicitly enable and configure
- Bring your own AI (BYOA) supported

Copyright (c) 2024-2026 Kenneth Bingham
All Rights Reserved
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from enum import IntEnum
from datetime import datetime
import secrets


class SandboxType(IntEnum):
    """Types of sandbox environments"""
    DEV_LOCAL = 0    # Local instance on dev's machine, only their apps
    BETA_VPS = 1     # VPS-hosted, includes ALL apps


class SandboxStatus(IntEnum):
    """Sandbox lifecycle status"""
    CREATING = 0
    RUNNING = 1
    STOPPED = 2
    SUSPENDED = 3
    DELETED = 4
    ERROR = 5


class AIProvider(IntEnum):
    """
    Supported AI providers for BYOA (Bring Your Own AI).
    
    AI IS ALWAYS A CHOICE - NEVER DEFAULT.
    Users must explicitly opt-in and configure.
    """
    NONE = 0              # No AI (default)
    OPENAI = 1            # OpenAI API
    ANTHROPIC = 2         # Anthropic Claude
    GOOGLE = 3            # Google AI (Gemini)
    OLLAMA = 4            # Ollama (local)
    HUGGINGFACE = 5       # HuggingFace
    CUSTOM = 6            # Custom API endpoint


@dataclass
class AIIntegration:
    """
    AI integration configuration for a sandbox.
    
    AI IS ALWAYS A CHOICE - NEVER DEFAULT.
    - enabled must be explicitly set to True
    - User provides their own API keys
    - No AI features without explicit opt-in
    """
    # AI is OFF by default - must opt-in
    enabled: bool = False
    
    # Provider configuration
    provider: AIProvider = AIProvider.NONE
    api_key: str = ""           # User's own API key (encrypted in storage)
    api_endpoint: str = ""      # Custom endpoint for CUSTOM provider
    model: str = ""             # Model name (e.g., "gpt-4", "claude-3")
    
    # Optional configuration
    max_tokens: int = 4096
    temperature: float = 0.7
    
    # Rate limiting
    requests_per_minute: int = 60
    requests_per_day: int = 1000
    
    # Tracking
    enabled_at: Optional[datetime] = None
    total_requests: int = 0
    total_tokens_used: int = 0
    
    def enable(self, provider: AIProvider, api_key: str, model: str = "") -> None:
        """
        Enable AI integration (explicit opt-in).
        
        User must call this method to enable AI - it is never automatic.
        """
        if provider == AIProvider.NONE:
            raise ValueError("Must specify an AI provider")
        if not api_key and provider != AIProvider.OLLAMA:
            raise ValueError("API key required for this provider")
        
        self.enabled = True
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.enabled_at = datetime.now()
    
    def disable(self) -> None:
        """Disable AI integration"""
        self.enabled = False
        self.provider = AIProvider.NONE
        self.api_key = ""
        self.model = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "provider": self.provider.value,
            # Note: api_key should be encrypted in production
            "api_key_set": bool(self.api_key),  # Don't expose actual key
            "api_endpoint": self.api_endpoint,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "requests_per_minute": self.requests_per_minute,
            "requests_per_day": self.requests_per_day,
            "enabled_at": self.enabled_at.isoformat() if self.enabled_at else None,
            "total_requests": self.total_requests,
            "total_tokens_used": self.total_tokens_used,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], api_key: str = "") -> 'AIIntegration':
        ai = cls(
            enabled=data.get("enabled", False),
            provider=AIProvider(data.get("provider", 0)),
            api_key=api_key,  # Passed separately (decrypted)
            api_endpoint=data.get("api_endpoint", ""),
            model=data.get("model", ""),
            max_tokens=data.get("max_tokens", 4096),
            temperature=data.get("temperature", 0.7),
            requests_per_minute=data.get("requests_per_minute", 60),
            requests_per_day=data.get("requests_per_day", 1000),
            total_requests=data.get("total_requests", 0),
            total_tokens_used=data.get("total_tokens_used", 0),
        )
        if data.get("enabled_at"):
            ai.enabled_at = datetime.fromisoformat(data["enabled_at"])
        return ai


@dataclass
class SandboxConfig:
    """Configuration for sandbox resources"""
    # Storage
    storage_mb: int = 1024      # 1GB default
    max_storage_mb: int = 10240 # 10GB max
    
    # Memory
    memory_mb: int = 512        # 512MB default
    max_memory_mb: int = 4096   # 4GB max
    
    # CPU
    cpu_percent: int = 25       # 25% CPU default
    max_cpu_percent: int = 100  # 100% max
    
    # Network
    network_enabled: bool = True
    ports: List[int] = field(default_factory=lambda: [8080, 8443])
    
    # Timeouts
    idle_timeout_minutes: int = 60    # Auto-stop after 1hr idle
    max_runtime_hours: int = 24       # Max 24hr continuous run
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "storage_mb": self.storage_mb,
            "max_storage_mb": self.max_storage_mb,
            "memory_mb": self.memory_mb,
            "max_memory_mb": self.max_memory_mb,
            "cpu_percent": self.cpu_percent,
            "max_cpu_percent": self.max_cpu_percent,
            "network_enabled": self.network_enabled,
            "ports": self.ports,
            "idle_timeout_minutes": self.idle_timeout_minutes,
            "max_runtime_hours": self.max_runtime_hours,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SandboxConfig':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    @classmethod
    def for_beta(cls) -> 'SandboxConfig':
        """Create config for beta sandbox (generous limits)"""
        return cls(
            storage_mb=5120,      # 5GB
            memory_mb=2048,       # 2GB
            cpu_percent=50,       # 50% CPU
            max_runtime_hours=72, # 3 days
        )
    
    @classmethod
    def for_dev(cls) -> 'SandboxConfig':
        """Create config for dev sandbox (standard limits)"""
        return cls(
            storage_mb=2048,      # 2GB
            memory_mb=1024,       # 1GB
            cpu_percent=25,       # 25% CPU
            max_runtime_hours=24, # 1 day
        )


@dataclass
class SandboxApp:
    """An app deployed to a sandbox"""
    id: str
    name: str
    version: str
    
    # Source
    source_type: str = "local"   # local, git, marketplace
    source_path: str = ""        # Path or URL
    
    # Deployment
    deployed_at: datetime = field(default_factory=datetime.now)
    is_running: bool = False
    port: int = 8080
    
    # For marketplace apps (beta gets all, dev gets own)
    marketplace_id: str = ""
    is_owned_by_sandbox_owner: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "source_type": self.source_type,
            "source_path": self.source_path,
            "deployed_at": self.deployed_at.isoformat(),
            "is_running": self.is_running,
            "port": self.port,
            "marketplace_id": self.marketplace_id,
            "is_owned_by_sandbox_owner": self.is_owned_by_sandbox_owner,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SandboxApp':
        app = cls(
            id=data["id"],
            name=data["name"],
            version=data.get("version", "1.0.0"),
            source_type=data.get("source_type", "local"),
            source_path=data.get("source_path", ""),
            is_running=data.get("is_running", False),
            port=data.get("port", 8080),
            marketplace_id=data.get("marketplace_id", ""),
            is_owned_by_sandbox_owner=data.get("is_owned_by_sandbox_owner", True),
        )
        if data.get("deployed_at"):
            app.deployed_at = datetime.fromisoformat(data["deployed_at"])
        return app


@dataclass
class Sandbox:
    """
    Isolated sandbox environment.
    
    Types:
    - BETA_VPS: Server-hosted, includes ALL ButterflyFX apps
    - DEV_LOCAL: Local instance, only dev's own apps
    
    Features:
    - Isolated file system
    - Resource limits
    - Optional AI integration (NEVER default, always opt-in)
    - App deployment
    """
    id: str
    owner_id: str               # User who owns this sandbox
    name: str
    sandbox_type: SandboxType
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    # Status
    status: SandboxStatus = SandboxStatus.CREATING
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    
    # Configuration
    config: SandboxConfig = field(default_factory=SandboxConfig)
    
    # AI Integration (ALWAYS OPTIONAL - OFF by default)
    ai: AIIntegration = field(default_factory=AIIntegration)
    
    # Location
    host: str = ""              # Hostname or IP
    path: str = ""              # File system path
    url: str = ""               # Access URL
    
    # Apps deployed
    apps: Dict[str, SandboxApp] = field(default_factory=dict)
    
    # For BETA: includes ALL marketplace apps
    # For DEV: only apps owned by the dev
    include_all_apps: bool = False
    
    # Metadata
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_beta_vps(cls, owner_id: str, name: str) -> 'Sandbox':
        """
        Create a VPS-hosted sandbox for beta tester.
        
        Includes ALL ButterflyFX apps.
        AI is NOT enabled by default - user must opt-in.
        """
        sandbox_id = f"sandbox-beta-{secrets.token_hex(8)}"
        return cls(
            id=sandbox_id,
            owner_id=owner_id,
            name=name,
            sandbox_type=SandboxType.BETA_VPS,
            config=SandboxConfig.for_beta(),
            host="sandbox.butterflyfx.us",
            path=f"/sandboxes/beta/{owner_id}/{sandbox_id}",
            url=f"https://{sandbox_id}.sandbox.butterflyfx.us",
            include_all_apps=True,  # Beta gets ALL apps
            description="Beta tester VPS sandbox with all ButterflyFX apps",
        )
    
    @classmethod
    def create_dev_local(cls, owner_id: str, name: str, local_path: str = "") -> 'Sandbox':
        """
        Create a local sandbox for developer.
        
        Only includes apps owned by the developer.
        AI is NOT enabled by default - user must opt-in.
        """
        sandbox_id = f"sandbox-dev-{secrets.token_hex(8)}"
        return cls(
            id=sandbox_id,
            owner_id=owner_id,
            name=name,
            sandbox_type=SandboxType.DEV_LOCAL,
            config=SandboxConfig.for_dev(),
            host="localhost",
            path=local_path or f"~/.butterflyfx/sandboxes/{sandbox_id}",
            url=f"http://localhost:8080",
            include_all_apps=False,  # Dev only gets their apps
            description="Developer local sandbox for app development",
        )
    
    def enable_ai(self, provider: AIProvider, api_key: str, model: str = "") -> None:
        """
        Enable AI integration (explicit opt-in).
        
        AI IS ALWAYS A CHOICE - NEVER DEFAULT.
        """
        self.ai.enable(provider, api_key, model)
        self.updated_at = datetime.now()
    
    def disable_ai(self) -> None:
        """Disable AI integration"""
        self.ai.disable()
        self.updated_at = datetime.now()
    
    def add_app(self, app: SandboxApp) -> None:
        """Add an app to the sandbox"""
        # DEV sandboxes can only add their own apps
        if self.sandbox_type == SandboxType.DEV_LOCAL:
            if not app.is_owned_by_sandbox_owner:
                raise ValueError("Developer sandboxes can only include apps owned by the developer")
        
        self.apps[app.id] = app
        self.updated_at = datetime.now()
    
    def remove_app(self, app_id: str) -> bool:
        """Remove an app from the sandbox"""
        if app_id in self.apps:
            del self.apps[app_id]
            self.updated_at = datetime.now()
            return True
        return False
    
    def start(self) -> None:
        """Start the sandbox"""
        if self.status == SandboxStatus.DELETED:
            raise ValueError("Cannot start a deleted sandbox")
        self.status = SandboxStatus.RUNNING
        self.started_at = datetime.now()
        self.updated_at = datetime.now()
    
    def stop(self) -> None:
        """Stop the sandbox"""
        self.status = SandboxStatus.STOPPED
        self.stopped_at = datetime.now()
        self.updated_at = datetime.now()
    
    def delete(self) -> None:
        """Mark sandbox for deletion"""
        self.status = SandboxStatus.DELETED
        self.updated_at = datetime.now()
    
    @property
    def is_running(self) -> bool:
        return self.status == SandboxStatus.RUNNING
    
    @property
    def has_ai(self) -> bool:
        """Check if AI is enabled (explicit opt-in)"""
        return self.ai.enabled
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "name": self.name,
            "sandbox_type": self.sandbox_type.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "stopped_at": self.stopped_at.isoformat() if self.stopped_at else None,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "config": self.config.to_dict(),
            "ai": self.ai.to_dict(),
            "host": self.host,
            "path": self.path,
            "url": self.url,
            "apps": {k: v.to_dict() for k, v in self.apps.items()},
            "include_all_apps": self.include_all_apps,
            "description": self.description,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], ai_api_key: str = "") -> 'Sandbox':
        sandbox = cls(
            id=data["id"],
            owner_id=data["owner_id"],
            name=data["name"],
            sandbox_type=SandboxType(data["sandbox_type"]),
            status=SandboxStatus(data.get("status", 0)),
            host=data.get("host", ""),
            path=data.get("path", ""),
            url=data.get("url", ""),
            include_all_apps=data.get("include_all_apps", False),
            description=data.get("description", ""),
            metadata=data.get("metadata", {}),
        )
        
        sandbox.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            sandbox.updated_at = datetime.fromisoformat(data["updated_at"])
        if data.get("started_at"):
            sandbox.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("stopped_at"):
            sandbox.stopped_at = datetime.fromisoformat(data["stopped_at"])
        if data.get("last_accessed"):
            sandbox.last_accessed = datetime.fromisoformat(data["last_accessed"])
        
        if data.get("config"):
            sandbox.config = SandboxConfig.from_dict(data["config"])
        if data.get("ai"):
            sandbox.ai = AIIntegration.from_dict(data["ai"], ai_api_key)
        
        for app_id, app_data in data.get("apps", {}).items():
            sandbox.apps[app_id] = SandboxApp.from_dict(app_data)
        
        return sandbox
