"""
ButterflyFX Licensing System
=============================

Copyright (c) 2024-2026 Kenneth Bingham - All Rights Reserved
https://butterflyfx.us

This module handles license validation for subscription-based substrate packages.

License Tiers:
- FREE: Kernel primitives (always available, open source CC BY 4.0)
- STARTER: Basic packages (individual creators, students)
- PROFESSIONAL: Advanced packages (businesses, teams)
- ENTERPRISE: All packages + support + custom integrations

Each package has a tier requirement. License keys are validated against
the ButterflyFX license server.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from enum import Enum, IntEnum
from datetime import datetime, timedelta
import hashlib
import os
import json


class LicenseTier(IntEnum):
    """License tiers - higher number = more access"""
    FREE = 0         # Kernel only - always available
    STARTER = 1      # Basic packages
    PROFESSIONAL = 2 # Advanced packages
    ENTERPRISE = 3   # Everything + priority support


@dataclass
class PackageInfo:
    """Information about a substrate package"""
    name: str
    domain: str
    description: str
    tier_required: LicenseTier
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)
    
    @property
    def is_free(self) -> bool:
        return self.tier_required == LicenseTier.FREE


@dataclass
class License:
    """User license information"""
    license_key: str
    tier: LicenseTier
    user_email: str
    issued_date: datetime
    expiry_date: Optional[datetime] = None
    allowed_packages: Set[str] = field(default_factory=set)  # Empty = all for tier
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        if self.expiry_date is None:
            return True  # Perpetual license
        return datetime.now() < self.expiry_date
    
    @property
    def is_expired(self) -> bool:
        return not self.is_valid
    
    def can_access(self, package: PackageInfo) -> bool:
        """Check if this license can access a package"""
        if not self.is_valid:
            return False
        
        # Free packages always accessible
        if package.is_free:
            return True
        
        # Check tier
        if self.tier < package.tier_required:
            return False
        
        # If specific packages listed, check them
        if self.allowed_packages and package.name not in self.allowed_packages:
            return False
        
        return True
    
    def days_remaining(self) -> Optional[int]:
        if self.expiry_date is None:
            return None
        delta = self.expiry_date - datetime.now()
        return max(0, delta.days)


class LicenseError(Exception):
    """Raised when license validation fails"""
    pass


class PackageNotLicensedError(LicenseError):
    """Raised when trying to use an unlicensed package"""
    def __init__(self, package_name: str, required_tier: LicenseTier):
        self.package_name = package_name
        self.required_tier = required_tier
        super().__init__(
            f"Package '{package_name}' requires {required_tier.name} license. "
            f"Upgrade at https://butterflyfx.us/pricing"
        )


class LicenseExpiredError(LicenseError):
    """Raised when license has expired"""
    def __init__(self, expiry_date: datetime):
        self.expiry_date = expiry_date
        super().__init__(
            f"License expired on {expiry_date.strftime('%Y-%m-%d')}. "
            f"Renew at https://butterflyfx.us/account"
        )


class LicenseManager:
    """
    Manages license validation and package access.
    
    In development mode, all packages are available.
    In production, validates against license server.
    """
    
    _instance = None
    
    # Package registry - all available packages
    PACKAGES: Dict[str, PackageInfo] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._license: Optional[License] = None
            cls._instance._dev_mode = os.environ.get('BUTTERFLYFX_DEV', '0') == '1'
            cls._instance._init_packages()
        return cls._instance
    
    def _init_packages(self):
        """Register all available packages"""
        # These are the subscription packages
        self.register_package(PackageInfo(
            name="graphics",
            domain="graphics",
            description="Advanced graphics: shaders, gradients, 3D rendering, GPU compute",
            tier_required=LicenseTier.STARTER,
        ))
        
        self.register_package(PackageInfo(
            name="physics",
            domain="physics",
            description="Physics simulation: solid, liquid, gas dynamics, collisions",
            tier_required=LicenseTier.STARTER,
        ))
        
        self.register_package(PackageInfo(
            name="audio",
            domain="audio",
            description="Audio/Music: synthesis, music theory, sheet music, voice",
            tier_required=LicenseTier.STARTER,
        ))
        
        self.register_package(PackageInfo(
            name="text",
            domain="text",
            description="Text/NLP: grammar, unicode, fonts, natural language processing",
            tier_required=LicenseTier.STARTER,
        ))
        
        self.register_package(PackageInfo(
            name="patterns",
            domain="patterns",
            description="Patterns: fractals, tiling, edge detection, procedural generation",
            tier_required=LicenseTier.STARTER,
        ))
        
        self.register_package(PackageInfo(
            name="theory",
            domain="theory",
            description="Theory: color theory, music theory, statistics, probability",
            tier_required=LicenseTier.PROFESSIONAL,
        ))
        
        self.register_package(PackageInfo(
            name="media",
            domain="media",
            description="Media: image manipulation, video, text-to-image, image-to-video",
            tier_required=LicenseTier.PROFESSIONAL,
        ))
        
        self.register_package(PackageInfo(
            name="game_engine",
            domain="game",
            description="Game Engine: ECS, scene graph, physics, rendering pipeline",
            tier_required=LicenseTier.PROFESSIONAL,
        ))
        
        self.register_package(PackageInfo(
            name="ai_ml",
            domain="ai",
            description="AI/ML: pattern matching, object detection, neural substrates",
            tier_required=LicenseTier.PROFESSIONAL,
        ))
        
        self.register_package(PackageInfo(
            name="finance",
            domain="finance",
            description="Finance: stock theory, economic modeling, risk analysis",
            tier_required=LicenseTier.ENTERPRISE,
        ))
        
        self.register_package(PackageInfo(
            name="quantum",
            domain="quantum",
            description="Quantum: quantum-inspired computing, superposition, entanglement",
            tier_required=LicenseTier.ENTERPRISE,
        ))
    
    def register_package(self, package: PackageInfo) -> None:
        """Register a package in the system"""
        self.PACKAGES[package.name] = package
    
    @property
    def is_dev_mode(self) -> bool:
        """Check if running in development mode"""
        return self._dev_mode
    
    def set_dev_mode(self, enabled: bool) -> None:
        """Enable/disable development mode"""
        self._dev_mode = enabled
    
    def activate_license(self, license_key: str) -> License:
        """
        Activate a license key.
        
        In production, this validates against the license server.
        In dev mode, creates a full enterprise license.
        """
        if self._dev_mode:
            self._license = License(
                license_key="DEV-MODE-FULL-ACCESS",
                tier=LicenseTier.ENTERPRISE,
                user_email="developer@local",
                issued_date=datetime.now(),
                expiry_date=None,  # Never expires in dev
                metadata={"dev_mode": True}
            )
            return self._license
        
        # TODO: In production, validate against license server
        # For now, decode the key format: TIER-HASH-USER_ID
        # This is a placeholder - real implementation would call license server
        
        validated = self._validate_key_offline(license_key)
        if validated:
            self._license = validated
            return self._license
        
        raise LicenseError(f"Invalid license key. Purchase at https://butterflyfx.us/pricing")
    
    def _validate_key_offline(self, key: str) -> Optional[License]:
        """
        Offline key validation (fallback).
        
        Real implementation would cache validated keys from server.
        """
        # Key format: TIER-HASH (simplified for demo)
        parts = key.split('-')
        if len(parts) < 2:
            return None
        
        tier_map = {
            'FREE': LicenseTier.FREE,
            'STARTER': LicenseTier.STARTER,
            'PRO': LicenseTier.PROFESSIONAL,
            'ENTERPRISE': LicenseTier.ENTERPRISE,
        }
        
        tier = tier_map.get(parts[0].upper())
        if tier is None:
            return None
        
        return License(
            license_key=key,
            tier=tier,
            user_email="offline@validation",
            issued_date=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=30),
        )
    
    def load_license_from_file(self, path: str = None) -> Optional[License]:
        """Load license from file"""
        if path is None:
            path = os.path.expanduser("~/.butterflyfx/license.json")
        
        if not os.path.exists(path):
            return None
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            self._license = License(
                license_key=data['license_key'],
                tier=LicenseTier(data['tier']),
                user_email=data['user_email'],
                issued_date=datetime.fromisoformat(data['issued_date']),
                expiry_date=datetime.fromisoformat(data['expiry_date']) if data.get('expiry_date') else None,
                allowed_packages=set(data.get('allowed_packages', [])),
            )
            return self._license
        except Exception:
            return None
    
    def save_license_to_file(self, path: str = None) -> bool:
        """Save current license to file"""
        if self._license is None:
            return False
        
        if path is None:
            path = os.path.expanduser("~/.butterflyfx/license.json")
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        data = {
            'license_key': self._license.license_key,
            'tier': self._license.tier.value,
            'user_email': self._license.user_email,
            'issued_date': self._license.issued_date.isoformat(),
            'expiry_date': self._license.expiry_date.isoformat() if self._license.expiry_date else None,
            'allowed_packages': list(self._license.allowed_packages),
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    
    @property
    def current_license(self) -> Optional[License]:
        return self._license
    
    @property
    def current_tier(self) -> LicenseTier:
        if self._dev_mode:
            return LicenseTier.ENTERPRISE
        if self._license is None:
            return LicenseTier.FREE
        if not self._license.is_valid:
            return LicenseTier.FREE
        return self._license.tier
    
    def check_package_access(self, package_name: str) -> bool:
        """Check if current license can access a package"""
        if self._dev_mode:
            return True
        
        package = self.PACKAGES.get(package_name)
        if package is None:
            return False  # Unknown package
        
        if package.is_free:
            return True
        
        if self._license is None:
            return False
        
        return self._license.can_access(package)
    
    def require_package(self, package_name: str) -> None:
        """
        Require a package - raises exception if not licensed.
        
        Use this at the top of substrates that require a license.
        """
        if self._dev_mode:
            return
        
        package = self.PACKAGES.get(package_name)
        if package is None:
            raise LicenseError(f"Unknown package: {package_name}")
        
        if package.is_free:
            return
        
        if self._license is None:
            raise PackageNotLicensedError(package_name, package.tier_required)
        
        if not self._license.is_valid:
            raise LicenseExpiredError(self._license.expiry_date)
        
        if not self._license.can_access(package):
            raise PackageNotLicensedError(package_name, package.tier_required)
    
    def list_available_packages(self) -> List[PackageInfo]:
        """List all packages available to current license"""
        return [
            pkg for pkg in self.PACKAGES.values()
            if self.check_package_access(pkg.name)
        ]
    
    def list_all_packages(self) -> List[PackageInfo]:
        """List all packages with their tier requirements"""
        return list(self.PACKAGES.values())
    
    def get_upgrade_url(self, package_name: str) -> str:
        """Get URL to purchase/upgrade for a package"""
        package = self.PACKAGES.get(package_name)
        if package:
            return f"https://butterflyfx.us/pricing?package={package_name}&tier={package.tier_required.name.lower()}"
        return "https://butterflyfx.us/pricing"


# =============================================================================
# DECORATOR FOR LICENSED SUBSTRATES
# =============================================================================

def requires_license(package_name: str):
    """
    Decorator for substrate classes that require a license.
    
    Usage:
        @requires_license("graphics")
        class ShaderSubstrate(Substrate):
            ...
    """
    def decorator(cls):
        original_init = cls.__init__
        
        def new_init(self, *args, **kwargs):
            LicenseManager().require_package(package_name)
            original_init(self, *args, **kwargs)
        
        cls.__init__ = new_init
        cls._required_package = package_name
        return cls
    
    return decorator


def check_license(package_name: str) -> bool:
    """
    Check if a package is licensed (without raising exception).
    
    Usage:
        if check_license("graphics"):
            shader = ShaderSubstrate()
    """
    return LicenseManager().check_package_access(package_name)


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

LICENSE = LicenseManager()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'LicenseTier',
    'PackageInfo',
    'License',
    'LicenseError',
    'PackageNotLicensedError',
    'LicenseExpiredError',
    'LicenseManager',
    'LICENSE',
    'requires_license',
    'check_license',
]
