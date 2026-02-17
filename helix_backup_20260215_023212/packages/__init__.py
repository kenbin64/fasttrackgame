"""
ButterflyFX Substrate Packages
==============================

Copyright (c) 2024-2026 Kenneth Bingham - All Rights Reserved
https://butterflyfx.us

Subscription-based substrate packages that build on the open source kernel.

Package Tiers:
- STARTER: $9/mo - Basic creative tools
- PROFESSIONAL: $29/mo - Advanced capabilities
- ENTERPRISE: $99/mo - Full suite + support

Each package is a collection of substrates for a specific domain.
Packages can depend on other packages and share primitives from the kernel.
"""

from typing import Dict, List, Optional
from ..licensing import (
    LicenseManager, 
    LicenseTier, 
    PackageInfo,
    requires_license,
    check_license,
    LICENSE,
)


# =============================================================================
# PACKAGE REGISTRY
# =============================================================================

class PackageRegistry:
    """
    Central registry for all substrate packages.
    
    Discovery is O(1) through the SRL system.
    """
    
    _packages: Dict[str, 'Package'] = {}
    
    @classmethod
    def register(cls, package: 'Package') -> None:
        """Register a package"""
        cls._packages[package.name] = package
    
    @classmethod
    def get(cls, name: str) -> Optional['Package']:
        """Get package by name"""
        return cls._packages.get(name)
    
    @classmethod
    def list_available(cls) -> List['Package']:
        """List packages available to current license"""
        return [
            pkg for pkg in cls._packages.values()
            if pkg.is_available
        ]
    
    @classmethod
    def list_all(cls) -> List['Package']:
        """List all packages"""
        return list(cls._packages.values())


class Package:
    """
    A collection of related substrates.
    
    Packages are the unit of subscription - users subscribe to packages,
    not individual substrates.
    """
    
    def __init__(
        self,
        name: str,
        domain: str,
        description: str,
        tier: LicenseTier,
        substrates: List[str] = None,
        dependencies: List[str] = None,
    ):
        self.name = name
        self.domain = domain
        self.description = description
        self.tier = tier
        self.substrates = substrates or []
        self.dependencies = dependencies or []
        
        # Register with central registry
        PackageRegistry.register(self)
    
    @property
    def is_available(self) -> bool:
        """Check if this package is available to current license"""
        return LICENSE.check_package_access(self.name)
    
    @property
    def price_monthly(self) -> str:
        """Get monthly price string"""
        prices = {
            LicenseTier.FREE: "Free",
            LicenseTier.STARTER: "$9/mo",
            LicenseTier.PROFESSIONAL: "$29/mo",
            LicenseTier.ENTERPRISE: "$99/mo",
        }
        return prices.get(self.tier, "Contact us")
    
    def require(self) -> None:
        """Require this package - raises if not licensed"""
        LICENSE.require_package(self.name)
    
    def __repr__(self) -> str:
        status = "✓" if self.is_available else "🔒"
        return f"Package({self.name}, {self.tier.name}, {status})"


# =============================================================================
# DEFINE PACKAGES
# =============================================================================

# --- STARTER TIER ($9/mo) ---

GRAPHICS_PKG = Package(
    name="graphics",
    domain="graphics",
    description="Advanced graphics: shaders, gradients, 3D, GPU",
    tier=LicenseTier.STARTER,
    substrates=[
        "PixelSubstrate",
        "ColorSubstrate", 
        "GradientSubstrate",
        "ShaderSubstrate",
        "Graphics3DSubstrate",
    ],
)

PHYSICS_PKG = Package(
    name="physics",
    domain="physics",
    description="Physics: solid, liquid, gas dynamics, collisions",
    tier=LicenseTier.STARTER,
    substrates=[
        "PhysicsSubstrate",
        "SolidSubstrate",
        "LiquidSubstrate",
        "GasSubstrate",
        "DynamicsSubstrate",
    ],
)

AUDIO_PKG = Package(
    name="audio",
    domain="audio",
    description="Audio: synthesis, music theory, voice",
    tier=LicenseTier.STARTER,
    substrates=[
        "WaveformSubstrate",
        "MusicTheorySubstrate",
        "VoiceSynthesisSubstrate",
        "SheetMusicSubstrate",
    ],
)

TEXT_PKG = Package(
    name="text",
    domain="text",
    description="Text: NLP, fonts, unicode, grammar",
    tier=LicenseTier.STARTER,
    substrates=[
        "ASCIISubstrate",
        "UnicodeSubstrate",
        "FontSubstrate",
        "GrammarSubstrate",
        "NLPSubstrate",
    ],
)

PATTERNS_PKG = Package(
    name="patterns",
    domain="patterns",
    description="Patterns: fractals, tiling, procedural",
    tier=LicenseTier.STARTER,
    substrates=[
        "FractalSubstrate",
        "PatternSubstrate",
        "TilingSubstrate",
        "NoiseSubstrate",
    ],
)

# --- PROFESSIONAL TIER ($29/mo) ---

THEORY_PKG = Package(
    name="theory",
    domain="theory",
    description="Theory: statistics, probability, game theory",
    tier=LicenseTier.PROFESSIONAL,
    substrates=[
        "StatisticsSubstrate",
        "ProbabilitySubstrate",
        "GameTheorySubstrate",
        "ColorTheorySubstrate",
    ],
    dependencies=["graphics"],
)

MEDIA_PKG = Package(
    name="media",
    domain="media",
    description="Media: image, video, text-to-image",
    tier=LicenseTier.PROFESSIONAL,
    substrates=[
        "ImageSubstrate",
        "VideoSubstrate",
        "TextToImageSubstrate",
        "ImageToVideoSubstrate",
    ],
    dependencies=["graphics", "text"],
)

GAME_ENGINE_PKG = Package(
    name="game_engine",
    domain="game",
    description="Game Engine: ECS, scenes, rendering",
    tier=LicenseTier.PROFESSIONAL,
    substrates=[
        "EntitySubstrate",
        "ComponentSubstrate",
        "SystemSubstrate",
        "SceneSubstrate",
        "RenderPipelineSubstrate",
    ],
    dependencies=["graphics", "physics"],
)

AI_ML_PKG = Package(
    name="ai_ml",
    domain="ai",
    description="AI/ML: pattern matching, detection, neural",
    tier=LicenseTier.PROFESSIONAL,
    substrates=[
        "PatternMatchSubstrate",
        "EdgeFindingSubstrate",
        "ObjectDetectionSubstrate",
        "NeuralSubstrate",
    ],
    dependencies=["patterns"],
)

# --- ENTERPRISE TIER ($99/mo) ---

FINANCE_PKG = Package(
    name="finance",
    domain="finance",
    description="Finance: stocks, economics, risk",
    tier=LicenseTier.ENTERPRISE,
    substrates=[
        "StockSubstrate",
        "EconomicSubstrate",
        "RiskSubstrate",
        "PortfolioSubstrate",
    ],
    dependencies=["theory"],
)

QUANTUM_PKG = Package(
    name="quantum",
    domain="quantum",
    description="Quantum: superposition, entanglement",
    tier=LicenseTier.ENTERPRISE,
    substrates=[
        "QuantumSubstrate",
        "SuperpositionSubstrate",
        "EntanglementSubstrate",
    ],
)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def available_packages() -> List[Package]:
    """Get all packages available to current license"""
    return PackageRegistry.list_available()


def all_packages() -> List[Package]:
    """Get all packages (including locked ones)"""
    return PackageRegistry.list_all()


def get_package(name: str) -> Optional[Package]:
    """Get a package by name"""
    return PackageRegistry.get(name)


def upgrade_url(package_name: str = None) -> str:
    """Get URL to upgrade license"""
    if package_name:
        pkg = get_package(package_name)
        if pkg:
            return f"https://butterflyfx.us/pricing?package={package_name}"
    return "https://butterflyfx.us/pricing"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'Package',
    'PackageRegistry',
    
    # Starter packages
    'GRAPHICS_PKG',
    'PHYSICS_PKG',
    'AUDIO_PKG',
    'TEXT_PKG',
    'PATTERNS_PKG',
    
    # Professional packages
    'THEORY_PKG',
    'MEDIA_PKG',
    'GAME_ENGINE_PKG',
    'AI_ML_PKG',
    
    # Enterprise packages
    'FINANCE_PKG',
    'QUANTUM_PKG',
    
    # Functions
    'available_packages',
    'all_packages',
    'get_package',
    'upgrade_url',
]
