#!/usr/bin/env python3
"""
ButterflyFX Platform Manifold - Unified Dimensional Computing Platform

Integrates ALL butterflyfx.us components into a single dimensional manifold:

    Level 6 (WHOLE/Meaning):     ButterflyFX Platform
    Level 5 (VOLUME/Multiplicity): Product Suites
    Level 4 (PLANE/Manifestation): Individual Apps/Services
    Level 3 (WIDTH/Structure):     Features/Endpoints
    Level 2 (LINE/Relationship):   Configurations/Connections
    Level 1 (POINT/Identity):      Resource IDs (UUIDs, SRLs)
    Level 0 (VOID/Potential):      Templates/Unmanifested

Product Suites (Level 5):
    - storage:    Universal Hard Drive (file substrate)
    - connector:  Universal Connector (API substrate)
    - ai:         Data & AI Suite (cognitive substrate)
    - platform:   DimensionOS (kernel substrate)
    - cloud:      OpenStack Manifold (infrastructure substrate)

OpenStack Integration:
    - Each product can be deployed as OpenStack instances
    - Resources tracked in cloud kernel
    - Dimensional addressing: product.suite.resource

Website: https://butterflyfx.us
Copyright (c) 2026 ButterflyFX. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Union, Callable
from enum import Enum, auto
import hashlib
import time
import json
from pathlib import Path
import sys

# Ensure helix imports work
sys.path.insert(0, str(Path(__file__).parent.parent))


# ═══════════════════════════════════════════════════════════════════════════════
# PLATFORM CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

class PlatformLevel(Enum):
    """7-level platform hierarchy."""
    VOID = 0           # Templates, potential
    POINT = 1          # Resource identities
    LINE = 2           # Configurations
    WIDTH = 3          # Features/endpoints
    PLANE = 4          # Individual apps
    VOLUME = 5         # Product suites
    WHOLE = 6          # Entire platform

# Fibonacci weights per level
FIBONACCI = {0: 0, 1: 1, 2: 1, 3: 2, 4: 3, 5: 5, 6: 8}

# Product suite definitions
PRODUCT_SUITES = {
    "storage": {
        "name": "Universal Hard Drive",
        "description": "Every file. Every cloud. One place.",
        "icon": "💾",
        "url": "https://butterflyfx.us/products/universal-hdd.html",
        "apps": ["explorer", "vault", "search", "sync"],
        "features": ["100+ connectors", "instant search", "smart organization", "secure vault"]
    },
    "connector": {
        "name": "Universal Connector", 
        "description": "Connect to anything. Literally.",
        "icon": "🔌",
        "url": "https://butterflyfx.us/products/universal-connector.html",
        "apps": ["api_hub", "database", "cloud_storage", "services"],
        "features": ["102+ integrations", "lazy connection", "SRL addressing", "real-time sync"]
    },
    "ai": {
        "name": "Data & AI Suite",
        "description": "Amplify your AI. Analyze anything.",
        "icon": "🧠",
        "url": "https://butterflyfx.us/products/data-ai-suite.html",
        "apps": ["amplifier", "predictor", "generator", "alchemist"],
        "features": ["AI integration", "trend prediction", "report generation", "data transformation"]
    },
    "platform": {
        "name": "DimensionOS",
        "description": "Build dimensional apps.",
        "icon": "🔧",
        "url": "https://butterflyfx.us/platform.html",
        "apps": ["helix", "substrate", "ui", "docs"],
        "features": ["helix framework", "substrate API", "UI components", "full documentation"]
    },
    "cloud": {
        "name": "OpenStack Manifold",
        "description": "Cloud infrastructure as dimensional substrate.",
        "icon": "☁️",
        "url": "https://butterflyfx.us/cloud.html",
        "apps": ["compute", "network", "storage", "identity"],
        "features": ["VM management", "network topology", "volume control", "project isolation"]
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
# PLATFORM TOKEN - Resource representation
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(eq=False)
class PlatformToken:
    """
    A resource token in the platform manifold.
    
    τ = (address, level, suite, payload)
    
    Address format: type.suite.name
        - vm.cloud.web-server
        - api.connector.bitcoin
        - file.storage.report.pdf
    """
    address: str
    level: PlatformLevel
    suite: str
    payload: Dict[str, Any] = field(default_factory=dict)
    signature: str = field(default="")
    timestamp: float = field(default_factory=time.time)
    
    def __post_init__(self):
        if not self.signature:
            self.signature = hashlib.sha256(
                f"{self.address}:{self.suite}:{self.timestamp}".encode()
            ).hexdigest()[:16]
    
    def __hash__(self):
        return hash(self.signature)
    
    def __eq__(self, other):
        if not isinstance(other, PlatformToken):
            return False
        return self.signature == other.signature
    
    @property
    def type(self) -> str:
        """Extract resource type from address."""
        return self.address.split(".")[0] if "." in self.address else self.address
    
    @property
    def name(self) -> str:
        """Extract resource name from address."""
        parts = self.address.split(".")
        return parts[-1] if len(parts) > 1 else self.address
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "address": self.address,
            "level": self.level.name,
            "suite": self.suite,
            "type": self.type,
            "name": self.name,
            "payload": self.payload,
            "signature": self.signature
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SUBSTRATE ADAPTERS - Connect to actual implementations
# ═══════════════════════════════════════════════════════════════════════════════

class SubstrateAdapter:
    """Base adapter for connecting to ButterflyFX substrates."""
    
    def __init__(self, suite: str):
        self.suite = suite
        self._connected = False
        self._instance = None
    
    def connect(self) -> bool:
        """Connect to the underlying substrate."""
        raise NotImplementedError
    
    def list_resources(self) -> List[PlatformToken]:
        """List all resources from this substrate."""
        raise NotImplementedError
    
    def get(self, address: str) -> Optional[PlatformToken]:
        """Get a specific resource by address."""
        raise NotImplementedError
    
    def invoke(self, action: str, **kwargs) -> Any:
        """Invoke an action on the substrate."""
        raise NotImplementedError


class StorageAdapter(SubstrateAdapter):
    """Adapter for Universal Hard Drive."""
    
    def __init__(self):
        super().__init__("storage")
    
    def connect(self) -> bool:
        try:
            from apps.universal_harddrive import UniversalHardDrive
            self._instance = UniversalHardDrive()
            self._connected = True
            return True
        except ImportError:
            return False
    
    def list_resources(self) -> List[PlatformToken]:
        if not self._connected:
            self.connect()
        
        tokens = []
        if self._instance:
            # List drives
            for drive_letter, drive in self._instance.drives.items():
                tokens.append(PlatformToken(
                    address=f"drive.storage.{drive_letter}",
                    level=PlatformLevel.PLANE,
                    suite="storage",
                    payload={"label": getattr(drive, 'label', drive_letter)}
                ))
        return tokens
    
    def get(self, address: str) -> Optional[PlatformToken]:
        if not self._connected:
            self.connect()
        
        # Parse address like file.storage.path
        parts = address.split(".", 2)
        if len(parts) >= 3 and self._instance:
            path = parts[2]
            try:
                content = self._instance.read(path)
                return PlatformToken(
                    address=address,
                    level=PlatformLevel.WIDTH,
                    suite="storage",
                    payload={"content": content, "path": path}
                )
            except:
                pass
        return None
    
    def invoke(self, action: str, **kwargs) -> Any:
        if not self._connected:
            self.connect()
        
        if self._instance:
            if action == "ls":
                return self._instance.ls(kwargs.get("path", "/"))
            elif action == "read":
                return self._instance.read(kwargs.get("path"))
            elif action == "save":
                return self._instance.save(kwargs.get("src"), kwargs.get("dst"))
        return None


class ConnectorAdapter(SubstrateAdapter):
    """Adapter for Universal Connector."""
    
    def __init__(self):
        super().__init__("connector")
    
    def connect(self) -> bool:
        try:
            from apps.universal_connector import UniversalConnector
            self._instance = UniversalConnector()
            self._connected = True
            return True
        except ImportError:
            return False
    
    def list_resources(self) -> List[PlatformToken]:
        if not self._connected:
            self.connect()
        
        tokens = []
        if self._instance:
            # List categories and APIs
            categories = self._instance.invoke(5)  # Level 5 = categories
            for cat_name, cat_data in categories.items():
                tokens.append(PlatformToken(
                    address=f"category.connector.{cat_name}",
                    level=PlatformLevel.VOLUME,
                    suite="connector",
                    payload={"icon": cat_data.get("icon", "📦")}
                ))
                
                # List APIs in category
                for api_name in cat_data.get("apis", {}):
                    tokens.append(PlatformToken(
                        address=f"api.connector.{api_name}",
                        level=PlatformLevel.PLANE,
                        suite="connector",
                        payload={"category": cat_name}
                    ))
        return tokens
    
    def get(self, address: str) -> Optional[PlatformToken]:
        if not self._connected:
            self.connect()
        
        parts = address.split(".", 2)
        if len(parts) >= 3 and self._instance:
            api_name = parts[2]
            try:
                data = self._instance.connect(api_name)
                return PlatformToken(
                    address=address,
                    level=PlatformLevel.PLANE,
                    suite="connector",
                    payload={"data": data}
                )
            except:
                pass
        return None
    
    def invoke(self, action: str, **kwargs) -> Any:
        if not self._connected:
            self.connect()
        
        if self._instance:
            if action == "connect":
                return self._instance.connect(kwargs.get("api"))
            elif action == "categories":
                return self._instance.invoke(5)
            elif action == "query":
                return self._instance.query(kwargs.get("q", "")).execute()
        return None


class AIAdapter(SubstrateAdapter):
    """Adapter for Data & AI Suite (AI Substrate)."""
    
    def __init__(self, backend: str = "mock"):
        super().__init__("ai")
        self.backend = backend
    
    def connect(self) -> bool:
        try:
            from helix.ai_substrate import AIKernel
            self._instance = AIKernel(self.backend)
            self._connected = True
            return True
        except ImportError:
            return False
    
    def list_resources(self) -> List[PlatformToken]:
        if not self._connected:
            self.connect()
        
        tokens = []
        if self._instance:
            status = self._instance.substrate.status()
            # Model as resource
            tokens.append(PlatformToken(
                address=f"model.ai.{self._instance.substrate.backend.name.replace(':', '_')}",
                level=PlatformLevel.PLANE,
                suite="ai",
                payload={"status": "active"}
            ))
            # Conversations as resources
            for conv_id in status.get("conversations", []):
                tokens.append(PlatformToken(
                    address=f"conversation.ai.{conv_id}",
                    level=PlatformLevel.WIDTH,
                    suite="ai",
                    payload={}
                ))
        return tokens
    
    def get(self, address: str) -> Optional[PlatformToken]:
        return None  # AI is stateless
    
    def invoke(self, action: str, **kwargs) -> Any:
        if not self._connected:
            self.connect()
        
        if self._instance:
            if action == "ask":
                return self._instance.ask(kwargs.get("question", ""))
            elif action == "chat":
                return self._instance.chat(kwargs.get("message", ""))
            elif action == "embed":
                return self._instance.embed(kwargs.get("text", ""))
            elif action == "spiral_up":
                return self._instance.spiral_up().name
            elif action == "spiral_down":
                return self._instance.spiral_down().name
        return None


class CloudAdapter(SubstrateAdapter):
    """Adapter for OpenStack Manifold."""
    
    def __init__(self):
        super().__init__("cloud")
        self._auth = {}
    
    def connect(self, auth_url: str = "", username: str = "", 
                password: str = "", project: str = "") -> bool:
        try:
            from helix.openstack_manifold import OpenStackKernel
            self._instance = OpenStackKernel()
            if auth_url:
                self._instance.connect(auth_url, username, password, project)
            self._connected = True
            return True
        except ImportError:
            return False
    
    def list_resources(self) -> List[PlatformToken]:
        if not self._connected:
            self.connect()
        
        tokens = []
        if self._instance:
            # Get tokens at manifestation level (4)
            for cloud_token in self._instance.substrate.tokens_for_state((0, 4)):
                tokens.append(PlatformToken(
                    address=f"{cloud_token.type}.cloud.{cloud_token.payload.get('name', cloud_token.id[:8])}",
                    level=PlatformLevel.PLANE,
                    suite="cloud",
                    payload=cloud_token.payload
                ))
        return tokens
    
    def get(self, address: str) -> Optional[PlatformToken]:
        if not self._connected:
            self.connect()
        
        if self._instance:
            result = self._instance.get(address.replace("cloud.", "", 1))
            if result:
                return PlatformToken(
                    address=address,
                    level=PlatformLevel.PLANE,
                    suite="cloud",
                    payload=result if isinstance(result, dict) else {"data": result}
                )
        return None
    
    def invoke(self, action: str, **kwargs) -> Any:
        if not self._connected:
            self.connect()
        
        if self._instance:
            if action == "list":
                return self._instance.get_all_tokens(kwargs.get("type", "vm"))
            elif action == "create_vm":
                return self._instance.create_vm(
                    kwargs.get("name"),
                    kwargs.get("flavor", "m1.small"),
                    kwargs.get("image", "ubuntu")
                )
            elif action == "spiral_up":
                return self._instance.spiral_up()
            elif action == "spiral_down":
                return self._instance.spiral_down()
        return None


class PlatformAdapter(SubstrateAdapter):
    """Adapter for DimensionOS Platform (Helix Kernel)."""
    
    def __init__(self):
        super().__init__("platform")
    
    def connect(self) -> bool:
        try:
            from helix.kernel import HelixKernel
            self._instance = HelixKernel()
            self._connected = True
            return True
        except ImportError:
            try:
                # Fallback to basic kernel
                from helix import HelixKernel
                self._instance = HelixKernel()
                self._connected = True
                return True
            except:
                return False
    
    def list_resources(self) -> List[PlatformToken]:
        tokens = []
        if self._connected and self._instance:
            state = self._instance.state
            tokens.append(PlatformToken(
                address=f"kernel.platform.helix",
                level=PlatformLevel.PLANE,
                suite="platform",
                payload={"spiral": state.spiral, "level": state.level}
            ))
        return tokens
    
    def get(self, address: str) -> Optional[PlatformToken]:
        return None
    
    def invoke(self, action: str, **kwargs) -> Any:
        if not self._connected:
            self.connect()
        
        if self._instance:
            if action == "invoke":
                return self._instance.invoke(kwargs.get("level", 4))
            elif action == "spiral_up":
                return self._instance.spiral_up()
            elif action == "spiral_down":
                return self._instance.spiral_down()
            elif action == "state":
                return self._instance.state
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# PLATFORM MANIFOLD - Unified dimensional surface
# ═══════════════════════════════════════════════════════════════════════════════

class PlatformManifold:
    """
    ButterflyFX Platform Manifold - The unified dimensional surface.
    
    M = (S, T, R) where:
        S = Space (7-level helix across all suites)
        T = Tokens (all platform resources)
        R = Relations (cross-suite connections)
    
    Provides O(1) access to any resource via dimensional addressing:
        type.suite.name
    """
    
    def __init__(self):
        self.state: tuple[int, int] = (0, 6)  # Start at WHOLE
        self.adapters: Dict[str, SubstrateAdapter] = {}
        self.token_index: Dict[str, PlatformToken] = {}
        self._init_adapters()
    
    def _init_adapters(self):
        """Initialize all substrate adapters."""
        self.adapters = {
            "storage": StorageAdapter(),
            "connector": ConnectorAdapter(),
            "ai": AIAdapter(),
            "cloud": CloudAdapter(),
            "platform": PlatformAdapter()
        }
    
    @property
    def level(self) -> PlatformLevel:
        return PlatformLevel(self.state[1])
    
    @property
    def spiral(self) -> int:
        return self.state[0]
    
    # ─────────────────────────────────────────────────────────────────────────
    # HELIX OPERATORS
    # ─────────────────────────────────────────────────────────────────────────
    
    def invoke(self, level: Optional[int] = None) -> List[PlatformToken]:
        """
        INVOKE operator - materialize tokens at specified level.
        
        Level 6: All suites
        Level 5: Apps within suites
        Level 4: Resources within apps
        Level 3: Features/endpoints
        Level 2: Configurations
        Level 1: Identities
        Level 0: Templates
        """
        target_level = level if level is not None else self.state[1]
        self.state = (self.state[0], target_level)
        
        tokens = []
        
        if target_level == 6:
            # Return all suite tokens
            for suite_id, suite_info in PRODUCT_SUITES.items():
                tokens.append(PlatformToken(
                    address=f"suite.{suite_id}",
                    level=PlatformLevel.WHOLE,
                    suite=suite_id,
                    payload={
                        "name": suite_info["name"],
                        "description": suite_info["description"],
                        "icon": suite_info["icon"],
                        "url": suite_info["url"]
                    }
                ))
        
        elif target_level == 5:
            # Return apps within suites
            for suite_id, suite_info in PRODUCT_SUITES.items():
                for app in suite_info["apps"]:
                    tokens.append(PlatformToken(
                        address=f"app.{suite_id}.{app}",
                        level=PlatformLevel.VOLUME,
                        suite=suite_id,
                        payload={"app": app}
                    ))
        
        elif target_level == 4:
            # Return actual resources from adapters
            for suite_id, adapter in self.adapters.items():
                try:
                    tokens.extend(adapter.list_resources())
                except:
                    pass
        
        elif target_level == 3:
            # Return features
            for suite_id, suite_info in PRODUCT_SUITES.items():
                for feature in suite_info["features"]:
                    tokens.append(PlatformToken(
                        address=f"feature.{suite_id}.{feature.replace(' ', '_')}",
                        level=PlatformLevel.WIDTH,
                        suite=suite_id,
                        payload={"feature": feature}
                    ))
        
        # Index all tokens
        for token in tokens:
            self.token_index[token.address] = token
        
        return tokens
    
    def spiral_up(self) -> PlatformLevel:
        """Ascend the helix toward meaning."""
        s, l = self.state
        if l < 6:
            self.state = (s, l + 1)
        else:
            self.state = (s + 1, 1)
        return self.level
    
    def spiral_down(self) -> PlatformLevel:
        """Descend the helix toward identity."""
        s, l = self.state
        if l > 0:
            self.state = (s, l - 1)
        elif s > 0:
            self.state = (s - 1, 6)
        return self.level
    
    def collapse(self) -> PlatformLevel:
        """Collapse to potential (level 0)."""
        self.state = (self.state[0], 0)
        return self.level
    
    # ─────────────────────────────────────────────────────────────────────────
    # O(1) ACCESS
    # ─────────────────────────────────────────────────────────────────────────
    
    def get(self, address: str) -> Optional[PlatformToken]:
        """
        O(1) resource access by dimensional address.
        
        Address format: type.suite.name
            - suite.storage
            - api.connector.bitcoin
            - vm.cloud.web-server
        """
        # Check index first
        if address in self.token_index:
            return self.token_index[address]
        
        # Parse address
        parts = address.split(".", 2)
        if len(parts) < 2:
            return None
        
        resource_type, suite = parts[0], parts[1]
        
        # Route to appropriate adapter
        if suite in self.adapters:
            token = self.adapters[suite].get(address)
            if token:
                self.token_index[address] = token
                return token
        
        return None
    
    def query(self, pattern: str = "*") -> List[PlatformToken]:
        """Query tokens matching pattern."""
        # Ensure index is populated
        if not self.token_index:
            self.invoke(4)
        
        if pattern == "*":
            return list(self.token_index.values())
        
        import fnmatch
        return [
            token for address, token in self.token_index.items()
            if fnmatch.fnmatch(address, pattern)
        ]
    
    # ─────────────────────────────────────────────────────────────────────────
    # SUITE OPERATIONS
    # ─────────────────────────────────────────────────────────────────────────
    
    def connect_suite(self, suite: str, **kwargs) -> bool:
        """Connect to a specific suite."""
        if suite in self.adapters:
            return self.adapters[suite].connect(**kwargs)
        return False
    
    def invoke_suite(self, suite: str, action: str, **kwargs) -> Any:
        """Invoke an action on a specific suite."""
        if suite in self.adapters:
            return self.adapters[suite].invoke(action, **kwargs)
        return None
    
    def list_suites(self) -> Dict[str, Dict]:
        """List all product suites."""
        return PRODUCT_SUITES.copy()
    
    # ─────────────────────────────────────────────────────────────────────────
    # OPENSTACK INTEGRATION
    # ─────────────────────────────────────────────────────────────────────────
    
    def deploy_to_cloud(self, suite: str, resources: Dict[str, Any]) -> List[PlatformToken]:
        """
        Deploy a suite to OpenStack cloud infrastructure.
        
        Creates VMs, networks, volumes as needed.
        """
        cloud = self.adapters.get("cloud")
        if not cloud or not cloud._connected:
            raise RuntimeError("Cloud adapter not connected")
        
        deployed = []
        suite_info = PRODUCT_SUITES.get(suite, {})
        
        # Create VM for the suite
        vm_name = f"butterflyfx-{suite}"
        result = cloud.invoke("create_vm", 
            name=vm_name,
            flavor=resources.get("flavor", "m1.medium"),
            image=resources.get("image", "ubuntu-22.04")
        )
        
        if result:
            deployed.append(PlatformToken(
                address=f"vm.cloud.{vm_name}",
                level=PlatformLevel.PLANE,
                suite="cloud",
                payload={"deployed_suite": suite, "status": "ACTIVE"}
            ))
        
        return deployed
    
    def cloud_status(self) -> Dict[str, Any]:
        """Get status of cloud-deployed resources."""
        cloud = self.adapters.get("cloud")
        if cloud and cloud._connected and cloud._instance:
            return {
                "state": cloud._instance.state,
                "vms": len(cloud._instance.substrate.tokens_for_state((0, 4))),
                "connected": True
            }
        return {"connected": False}
    
    # ─────────────────────────────────────────────────────────────────────────
    # UNIFIED OPERATIONS
    # ─────────────────────────────────────────────────────────────────────────
    
    def status(self) -> Dict[str, Any]:
        """Get full platform status."""
        return {
            "state": self.state,
            "level": self.level.name,
            "spiral": self.spiral,
            "indexed_tokens": len(self.token_index),
            "suites": {
                suite: {
                    "name": info["name"],
                    "connected": self.adapters[suite]._connected if suite in self.adapters else False
                }
                for suite, info in PRODUCT_SUITES.items()
            },
            "cloud": self.cloud_status()
        }
    
    def to_json(self) -> str:
        """Export platform state as JSON."""
        return json.dumps({
            "state": self.state,
            "suites": list(PRODUCT_SUITES.keys()),
            "tokens": [t.to_dict() for t in self.token_index.values()]
        }, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED KERNEL - Single interface to all ButterflyFX
# ═══════════════════════════════════════════════════════════════════════════════

class ButterflyFXKernel:
    """
    The Unified ButterflyFX Kernel.
    
    Single entry point to the entire ButterflyFX platform:
        - Storage (Universal Hard Drive)
        - Connector (Universal Connector)
        - AI (Data & AI Suite)
        - Cloud (OpenStack Manifold)
        - Platform (DimensionOS)
    
    Usage:
        kernel = ButterflyFXKernel()
        
        # Access any resource
        kernel.get("api.connector.bitcoin")
        kernel.get("file.storage./path/to/file")
        kernel.get("vm.cloud.web-server")
        
        # Invoke actions
        kernel.ask("What is ButterflyFX?")  # AI
        kernel.connect("bitcoin")            # Connector
        kernel.read("/path/to/file")         # Storage
        
        # Navigate dimensions
        kernel.spiral_up()
        kernel.spiral_down()
    """
    
    def __init__(self, ai_backend: str = "mock"):
        self.manifold = PlatformManifold()
        self.ai_backend = ai_backend
        self._configure_ai()
    
    def _configure_ai(self):
        """Configure AI adapter with specified backend."""
        if "ai" in self.manifold.adapters:
            self.manifold.adapters["ai"] = AIAdapter(self.ai_backend)
    
    # ─────────────────────────────────────────────────────────────────────────
    # UNIFIED INTERFACE
    # ─────────────────────────────────────────────────────────────────────────
    
    def get(self, address: str) -> Optional[Any]:
        """Get any resource by dimensional address."""
        token = self.manifold.get(address)
        return token.payload if token else None
    
    def invoke(self, level: int = 4) -> List[PlatformToken]:
        """Invoke at specified level."""
        return self.manifold.invoke(level)
    
    def spiral_up(self) -> str:
        """Navigate up the helix."""
        return self.manifold.spiral_up().name
    
    def spiral_down(self) -> str:
        """Navigate down the helix."""
        return self.manifold.spiral_down().name
    
    @property
    def level(self) -> str:
        """Current level name."""
        return self.manifold.level.name
    
    @property
    def state(self) -> tuple:
        """Current (spiral, level) state."""
        return self.manifold.state
    
    # ─────────────────────────────────────────────────────────────────────────
    # AI SHORTCUTS
    # ─────────────────────────────────────────────────────────────────────────
    
    def ask(self, question: str, context: Optional[str] = None) -> str:
        """Ask AI a question."""
        self.manifold.connect_suite("ai")
        if context:
            return self.manifold.invoke_suite("ai", "ask", question=f"{context}\n\n{question}")
        return self.manifold.invoke_suite("ai", "ask", question=question)
    
    def chat(self, message: str) -> str:
        """Multi-turn chat with AI."""
        self.manifold.connect_suite("ai")
        return self.manifold.invoke_suite("ai", "chat", message=message)
    
    # ─────────────────────────────────────────────────────────────────────────
    # CONNECTOR SHORTCUTS
    # ─────────────────────────────────────────────────────────────────────────
    
    def connect(self, api: str) -> Dict:
        """Connect to an API via Universal Connector."""
        self.manifold.connect_suite("connector")
        return self.manifold.invoke_suite("connector", "connect", api=api)
    
    def apis(self) -> Dict:
        """List available API categories."""
        self.manifold.connect_suite("connector")
        return self.manifold.invoke_suite("connector", "categories")
    
    # ─────────────────────────────────────────────────────────────────────────
    # STORAGE SHORTCUTS
    # ─────────────────────────────────────────────────────────────────────────
    
    def ls(self, path: str = "/") -> List:
        """List files in Universal Hard Drive."""
        self.manifold.connect_suite("storage")
        return self.manifold.invoke_suite("storage", "ls", path=path)
    
    def read(self, path: str) -> Any:
        """Read file from Universal Hard Drive."""
        self.manifold.connect_suite("storage")
        return self.manifold.invoke_suite("storage", "read", path=path)
    
    # ─────────────────────────────────────────────────────────────────────────
    # CLOUD SHORTCUTS
    # ─────────────────────────────────────────────────────────────────────────
    
    def cloud_connect(self, auth_url: str, username: str, password: str, project: str):
        """Connect to OpenStack cloud."""
        return self.manifold.adapters["cloud"].connect(auth_url, username, password, project)
    
    def vms(self) -> List:
        """List VMs from OpenStack."""
        self.manifold.connect_suite("cloud")
        tokens = self.manifold.invoke_suite("cloud", "list", type="vm")
        return tokens if tokens else []
    
    def create_vm(self, name: str, flavor: str = "m1.small", image: str = "ubuntu") -> Dict:
        """Create VM in OpenStack."""
        self.manifold.connect_suite("cloud")
        return self.manifold.invoke_suite("cloud", "create_vm", 
            name=name, flavor=flavor, image=image)
    
    # ─────────────────────────────────────────────────────────────────────────
    # PLATFORM STATUS
    # ─────────────────────────────────────────────────────────────────────────
    
    def status(self) -> Dict:
        """Get full platform status."""
        return self.manifold.status()
    
    def suites(self) -> Dict:
        """List all product suites."""
        return self.manifold.list_suites()


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """CLI for ButterflyFX Platform."""
    import sys
    
    print("═" * 70)
    print("ButterflyFX Platform Manifold - Unified Dimensional Computing")
    print("═" * 70)
    
    kernel = ButterflyFXKernel()
    
    print(f"\nPlatform State: {kernel.state}")
    print(f"Current Level: {kernel.level}")
    
    # List suites
    print("\n--- Product Suites (Level 6) ---")
    for suite_id, info in kernel.suites().items():
        print(f"  {info['icon']} {info['name']}: {info['description']}")
    
    # Invoke at level 6
    print("\n--- Manifest Level 6 (WHOLE) ---")
    tokens = kernel.invoke(6)
    for t in tokens[:5]:
        print(f"  {t.address}: {t.payload.get('name', '')}")
    
    # Spiral navigation
    print("\n--- Spiral Navigation ---")
    print(f"  Current: {kernel.level}")
    kernel.spiral_down()
    print(f"  After spiral_down: {kernel.level}")
    kernel.spiral_down()
    print(f"  After spiral_down: {kernel.level}")
    
    # Invoke at level 4 (resources)
    print("\n--- Resources (Level 4) ---")
    tokens = kernel.invoke(4)
    for t in tokens[:5]:
        print(f"  {t.address}")
    
    # Status
    print("\n--- Platform Status ---")
    status = kernel.status()
    print(f"  State: {status['state']}")
    print(f"  Indexed Tokens: {status['indexed_tokens']}")
    print("  Suites:")
    for suite, info in status['suites'].items():
        print(f"    {suite}: connected={info['connected']}")
    
    print("\n" + "═" * 70)
    print("SUCCESS - ButterflyFX Platform operational!")
    print("═" * 70)
    
    # Interactive mode
    if "--interactive" in sys.argv or "-i" in sys.argv:
        print("\nEntering interactive mode. Type 'quit' to exit.")
        while True:
            try:
                cmd = input("\nbfx> ").strip()
                if cmd == "quit":
                    break
                elif cmd == "status":
                    print(json.dumps(kernel.status(), indent=2))
                elif cmd == "suites":
                    for s, i in kernel.suites().items():
                        print(f"  {i['icon']} {s}: {i['name']}")
                elif cmd.startswith("get "):
                    addr = cmd[4:].strip()
                    result = kernel.get(addr)
                    print(json.dumps(result, indent=2, default=str))
                elif cmd == "up":
                    print(f"Level: {kernel.spiral_up()}")
                elif cmd == "down":
                    print(f"Level: {kernel.spiral_down()}")
                elif cmd.startswith("invoke "):
                    level = int(cmd[7:].strip())
                    tokens = kernel.invoke(level)
                    for t in tokens[:10]:
                        print(f"  {t.address}")
                elif cmd.startswith("ask "):
                    question = cmd[4:].strip()
                    print(kernel.ask(question))
                elif cmd == "help":
                    print("Commands: status, suites, get <addr>, up, down, invoke <level>, ask <question>, quit")
                else:
                    print(f"Unknown command: {cmd}")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    main()
