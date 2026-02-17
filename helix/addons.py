"""
ButterflyFX Add-On Architecture

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)

ADD-ONS vs PRIMITIVES:
    PRIMITIVES (dimensional_primitives.py):
        - Atomic, universally needed
        - Part of core kernel
        - Always available
        
    ADD-ONS (this module):
        - Lightweight extensions
        - App-specific functionality
        - Marketable products
        - Developer ecosystem
        - Loaded on demand
        
This creates a PRODUCT LINE:
    - Core Kernel: Pristine, no overhead
    - Add-Ons: Optional extensions
    - Marketplace: Revenue opportunity
    - Developer API: Third-party add-ons

ADD-ON LIFECYCLE:
    1. Discover - Find available add-ons
    2. Load - Import on demand
    3. Register - Add to runtime
    4. Use - Invoke functionality
    5. Unload - Free resources
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional, Set, Type
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
import importlib
import importlib.util
import json


# =============================================================================
# ADD-ON TYPES
# =============================================================================

class AddonType(Enum):
    """Types of add-ons."""
    SUBSTRATE = auto()      # New substrate types
    LENS = auto()           # New lens/view types
    CONNECTOR = auto()      # Data source connectors
    TRANSFORMER = auto()    # Data transformers
    VALIDATOR = auto()      # Validation rules
    VISUALIZATION = auto()  # Display/rendering
    INTEGRATION = auto()    # Third-party integrations
    UTILITY = auto()        # General utilities


class AddonTier(Enum):
    """Pricing tiers for marketplace."""
    FREE = "free"
    STARTER = "starter"       # $9/month
    PROFESSIONAL = "pro"      # $29/month
    ENTERPRISE = "enterprise" # Custom pricing


# =============================================================================
# ADD-ON METADATA
# =============================================================================

@dataclass
class AddonMeta:
    """Metadata for an add-on."""
    id: str                          # Unique identifier (e.g., "butterflyfx.mysql")
    name: str                        # Display name
    version: str                     # Semantic version
    description: str                 # What it does
    author: str                      # Creator
    addon_type: AddonType             # Category
    tier: AddonTier = AddonTier.FREE # Price tier
    
    # Dependencies
    requires: List[str] = field(default_factory=list)  # Other add-ons needed
    conflicts: List[str] = field(default_factory=list)  # Incompatible add-ons
    
    # Capabilities
    exports: List[str] = field(default_factory=list)  # What this add-on provides
    
    # Marketplace
    homepage: str = ""
    repository: str = ""
    license: str = "MIT"
    keywords: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "type": self.addon_type.name,
            "tier": self.tier.value,
            "requires": self.requires,
            "conflicts": self.conflicts,
            "exports": self.exports,
            "homepage": self.homepage,
            "repository": self.repository,
            "license": self.license,
            "keywords": self.keywords,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AddonMeta':
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            description=data["description"],
            author=data["author"],
            addon_type=AddonType[data.get("type", "UTILITY")],
            tier=AddonTier(data.get("tier", "free")),
            requires=data.get("requires", []),
            conflicts=data.get("conflicts", []),
            exports=data.get("exports", []),
            homepage=data.get("homepage", ""),
            repository=data.get("repository", ""),
            license=data.get("license", "MIT"),
            keywords=data.get("keywords", []),
        )


# =============================================================================
# ADD-ON INTERFACE
# =============================================================================

class Addon:
    """
    Base class for all add-ons.
    
    Add-ons must implement:
        - meta: AddonMeta with metadata
        - activate(): Called when loaded
        - deactivate(): Called when unloaded
    """
    
    @property
    def meta(self) -> AddonMeta:
        """Return add-on metadata."""
        raise NotImplementedError
    
    def activate(self, registry: 'AddonRegistry') -> None:
        """
        Called when the add-on is activated.
        
        Register your exports with the registry here.
        """
        pass
    
    def deactivate(self, registry: 'AddonRegistry') -> None:
        """
        Called when the add-on is deactivated.
        
        Clean up resources here.
        """
        pass
    
    def health_check(self) -> bool:
        """Check if add-on is functioning properly."""
        return True


# =============================================================================
# ADD-ON REGISTRY
# =============================================================================

class AddonRegistry:
    """
    Central registry for all add-ons.
    
    Manages discovery, loading, activation, and lifecycle.
    """
    
    _instance: Optional['AddonRegistry'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the registry."""
        self._addons: Dict[str, Addon] = {}
        self._active: Set[str] = set()
        self._exports: Dict[str, Any] = {}
        self._addon_paths: List[Path] = []
        self._marketplace_url: str = "https://addons.butterflyfx.us"
    
    # =========================================================================
    # DISCOVERY
    # =========================================================================
    
    def add_path(self, path: Path) -> None:
        """Add a directory to search for add-ons."""
        if path not in self._addon_paths:
            self._addon_paths.append(path)
    
    def discover(self) -> List[AddonMeta]:
        """
        Discover available add-ons from registered paths.
        
        Looks for:
            - addon.json metadata files
            - Python modules with Addon subclass
        """
        found = []
        
        for addon_path in self._addon_paths:
            if not addon_path.exists():
                continue
            
            # Look for addon.json files
            for meta_file in addon_path.rglob("addon.json"):
                try:
                    with open(meta_file) as f:
                        data = json.load(f)
                        found.append(AddonMeta.from_dict(data))
                except Exception:
                    pass
        
        return found
    
    def search_marketplace(self, query: str) -> List[AddonMeta]:
        """
        Search the add-on marketplace.
        
        Returns list of matching add-ons available for download.
        """
        # TODO: Implement actual marketplace API
        # For now, return empty list
        return []
    
    # =========================================================================
    # LOADING
    # =========================================================================
    
    def load(self, addon_id: str, module_path: str = None) -> bool:
        """
        Load an add-on by ID.
        
        If module_path is provided, load from that path.
        Otherwise, search registered paths.
        """
        if addon_id in self._addons:
            return True  # Already loaded
        
        try:
            if module_path:
                # Load from specific path
                spec = importlib.util.spec_from_file_location(addon_id, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                # Try to import as module
                module = importlib.import_module(addon_id)
            
            # Find Addon subclass
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(obj, Addon) and obj is not Addon:
                    addon = obj()
                    self._addons[addon_id] = addon
                    return True
            
            return False
        except Exception as e:
            print(f"Failed to load add-on {addon_id}: {e}")
            return False
    
    def load_from_class(self, addon_class: Type[Addon]) -> bool:
        """Load an add-on directly from a class."""
        try:
            addon = addon_class()
            addon_id = addon.meta.id
            self._addons[addon_id] = addon
            return True
        except Exception as e:
            print(f"Failed to load add-on class: {e}")
            return False
    
    def unload(self, addon_id: str) -> bool:
        """Unload an add-on."""
        if addon_id not in self._addons:
            return True
        
        # Deactivate if active
        if addon_id in self._active:
            self.deactivate(addon_id)
        
        del self._addons[addon_id]
        return True
    
    # =========================================================================
    # ACTIVATION
    # =========================================================================
    
    def activate(self, addon_id: str) -> bool:
        """
        Activate a loaded add-on.
        
        Checks dependencies and conflicts before activating.
        """
        if addon_id in self._active:
            return True  # Already active
        
        if addon_id not in self._addons:
            if not self.load(addon_id):
                return False
        
        addon = self._addons[addon_id]
        meta = addon.meta
        
        # Check dependencies
        for dep in meta.requires:
            if dep not in self._active:
                if not self.activate(dep):
                    print(f"Missing dependency: {dep}")
                    return False
        
        # Check conflicts
        for conflict in meta.conflicts:
            if conflict in self._active:
                print(f"Conflict with: {conflict}")
                return False
        
        # Activate
        try:
            addon.activate(self)
            self._active.add(addon_id)
            return True
        except Exception as e:
            print(f"Failed to activate {addon_id}: {e}")
            return False
    
    def deactivate(self, addon_id: str) -> bool:
        """Deactivate an add-on."""
        if addon_id not in self._active:
            return True
        
        addon = self._addons.get(addon_id)
        if addon:
            try:
                addon.deactivate(self)
            except Exception:
                pass
        
        # Remove exports
        exports_to_remove = []
        for name, (provider, _) in self._exports.items():
            if provider == addon_id:
                exports_to_remove.append(name)
        
        for name in exports_to_remove:
            del self._exports[name]
        
        self._active.discard(addon_id)
        return True
    
    # =========================================================================
    # EXPORTS
    # =========================================================================
    
    def register_export(self, addon_id: str, name: str, value: Any) -> None:
        """Register an export from an add-on."""
        self._exports[name] = (addon_id, value)
    
    def get_export(self, name: str) -> Optional[Any]:
        """Get an exported value by name."""
        entry = self._exports.get(name)
        return entry[1] if entry else None
    
    def list_exports(self) -> Dict[str, str]:
        """List all exports with their provider add-on ID."""
        return {name: provider for name, (provider, _) in self._exports.items()}
    
    # =========================================================================
    # QUERIES
    # =========================================================================
    
    def is_loaded(self, addon_id: str) -> bool:
        """Check if add-on is loaded."""
        return addon_id in self._addons
    
    def is_active(self, addon_id: str) -> bool:
        """Check if add-on is active."""
        return addon_id in self._active
    
    def get_addon(self, addon_id: str) -> Optional[Addon]:
        """Get add-on instance."""
        return self._addons.get(addon_id)
    
    def list_loaded(self) -> List[str]:
        """List loaded add-on IDs."""
        return list(self._addons.keys())
    
    def list_active(self) -> List[str]:
        """List active add-on IDs."""
        return list(self._active)
    
    def get_by_type(self, addon_type: AddonType) -> List[str]:
        """Get add-on IDs by type."""
        return [
            addon_id
            for addon_id, addon in self._addons.items()
            if addon.meta.addon_type == addon_type
        ]


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_registry() -> AddonRegistry:
    """Get the global add-on registry."""
    return AddonRegistry()


def register_addon(addon_class: Type[Addon]) -> Type[Addon]:
    """
    Decorator to register an add-on class.
    
    Usage:
        @register_addon
        class MyAddon(Addon):
            ...
    """
    get_registry().load_from_class(addon_class)
    return addon_class


def require_addon(addon_id: str):
    """
    Decorator to require an add-on be active before calling function.
    
    Usage:
        @require_addon("butterflyfx.mysql")
        def query_database():
            ...
    """
    def decorator(fn):
        def wrapper(*args, **kwargs):
            registry = get_registry()
            if not registry.is_active(addon_id):
                if not registry.activate(addon_id):
                    raise RuntimeError(f"Required add-on not available: {addon_id}")
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# EXAMPLE ADD-ONS
# =============================================================================

class ExampleSubstrateAddon(Addon):
    """Example substrate add-on."""
    
    @property
    def meta(self) -> AddonMeta:
        return AddonMeta(
            id="butterflyfx.example-substrate",
            name="Example Substrate",
            version="1.0.0",
            description="Demonstrates how to create a substrate add-on",
            author="ButterflyFX",
            addon_type=AddonType.SUBSTRATE,
            tier=AddonTier.FREE,
            exports=["ExampleSubstrate"],
            keywords=["example", "substrate", "demo"],
        )
    
    def activate(self, registry: AddonRegistry) -> None:
        # Register our exports
        from dataclasses import dataclass
        
        @dataclass
        class ExampleSubstrate:
            value: Any = None
            
            def transform(self, fn: Callable) -> 'ExampleSubstrate':
                return ExampleSubstrate(fn(self.value))
        
        registry.register_export(self.meta.id, "ExampleSubstrate", ExampleSubstrate)


class ExampleConnectorAddon(Addon):
    """Example connector add-on for database access."""
    
    @property
    def meta(self) -> AddonMeta:
        return AddonMeta(
            id="butterflyfx.example-connector",
            name="Example DB Connector",
            version="1.0.0",
            description="Demonstrates how to create a connector add-on",
            author="ButterflyFX",
            addon_type=AddonType.CONNECTOR,
            tier=AddonTier.STARTER,  # Paid add-on
            exports=["ExampleConnector", "connect_example"],
            keywords=["database", "connector", "demo"],
        )
    
    def activate(self, registry: AddonRegistry) -> None:
        class ExampleConnector:
            def __init__(self, host: str, port: int = 5432):
                self.host = host
                self.port = port
                self._connected = False
            
            def connect(self) -> bool:
                # Simulate connection
                self._connected = True
                return True
            
            def query(self, sql: str) -> Dict:
                if not self._connected:
                    raise RuntimeError("Not connected")
                return {"result": [], "sql": sql}
        
        def connect_example(host: str, port: int = 5432) -> ExampleConnector:
            conn = ExampleConnector(host, port)
            conn.connect()
            return conn
        
        registry.register_export(self.meta.id, "ExampleConnector", ExampleConnector)
        registry.register_export(self.meta.id, "connect_example", connect_example)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    'AddonType',
    'AddonTier',
    
    # Metadata
    'AddonMeta',
    
    # Base class
    'Addon',
    
    # Registry
    'AddonRegistry',
    'get_registry',
    
    # Decorators
    'register_addon',
    'require_addon',
    
    # Examples
    'ExampleSubstrateAddon',
    'ExampleConnectorAddon',
]
