"""
ButterflyFX Access Control
===========================

LOGIN IS NOT A PAYWALL - it provides role-based views.

PUBLIC (No Login Required)
==========================
Anyone can access:
- Landing page / website
- Documentation (public)
- About / Contact
- Pricing information
- Open source project info
- Demo pages
- Login / Register pages

AFTER LOGIN (Role-Based Views)
==============================
Each role sees features appropriate to their tier:

ANONYMOUS (0) - Not logged in
    → Public pages only
    → "Login to access downloads"

USER (1) - Basic registered users
    → Open source downloads
    → Basic API access
    → Community forums
    → User profile
    → Basic documentation

DEV (2) - Developers (inherits USER)
    → All USER features +
    → Developer tools
    → Premium packages
    → Marketplace submission
    → Local sandbox
    → Dev documentation
    → API key management
    → Collaboration chat (collaborators only)

BETA (3) - Beta testers (inherits DEV)
    → All DEV features +
    → Beta features (unreleased)
    → VPS sandbox with ALL apps
    → Secret beta chat room
    → Source code access
    → Free production forever (Kenneth's content only)

SUPERUSER (4) - Kenneth only (inherits ALL)
    → All BETA features +
    → Admin panel
    → User management
    → Universal blocks
    → System configuration
    → Beta code generation
    → License management

Copyright (c) 2024-2026 Kenneth Bingham
All Rights Reserved
"""

from enum import IntEnum
from typing import Dict, List, Set, Any
from dataclasses import dataclass, field


class PageAccess(IntEnum):
    """Access level for pages/features"""
    PUBLIC = 0       # No login required
    USER = 1         # Any logged in user
    DEV = 2          # Developer or higher
    BETA = 3         # Beta tester or higher
    SUPERUSER = 4    # Superuser only


@dataclass
class Page:
    """A page/view with access control"""
    id: str
    name: str
    path: str
    access: PageAccess
    description: str = ""
    icon: str = ""


# =============================================================================
# PUBLIC PAGES (No Login Required)
# =============================================================================

PUBLIC_PAGES: List[Page] = [
    Page(
        id="landing",
        name="Home",
        path="/",
        access=PageAccess.PUBLIC,
        description="ButterflyFX landing page",
        icon="🏠",
    ),
    Page(
        id="about",
        name="About",
        path="/about",
        access=PageAccess.PUBLIC,
        description="About ButterflyFX",
        icon="ℹ️",
    ),
    Page(
        id="docs",
        name="Documentation",
        path="/docs",
        access=PageAccess.PUBLIC,
        description="Public documentation",
        icon="📚",
    ),
    Page(
        id="pricing",
        name="Pricing",
        path="/pricing",
        access=PageAccess.PUBLIC,
        description="Pricing and plans",
        icon="💰",
    ),
    Page(
        id="opensource",
        name="Open Source",
        path="/opensource",
        access=PageAccess.PUBLIC,
        description="Open source projects info",
        icon="🔓",
    ),
    Page(
        id="demos",
        name="Demos",
        path="/demos",
        access=PageAccess.PUBLIC,
        description="Interactive demos",
        icon="🎮",
    ),
    Page(
        id="login",
        name="Login",
        path="/login",
        access=PageAccess.PUBLIC,
        description="Login page",
        icon="🔑",
    ),
    Page(
        id="register",
        name="Register",
        path="/register",
        access=PageAccess.PUBLIC,
        description="Create account",
        icon="📝",
    ),
]


# =============================================================================
# USER PAGES (Login Required - Any Role)
# =============================================================================

USER_PAGES: List[Page] = [
    Page(
        id="dashboard",
        name="Dashboard",
        path="/dashboard",
        access=PageAccess.USER,
        description="User dashboard",
        icon="📊",
    ),
    Page(
        id="profile",
        name="Profile",
        path="/profile",
        access=PageAccess.USER,
        description="User profile settings",
        icon="👤",
    ),
    Page(
        id="downloads",
        name="Downloads",
        path="/downloads",
        access=PageAccess.USER,
        description="Open source downloads",
        icon="⬇️",
    ),
    Page(
        id="community",
        name="Community",
        path="/community",
        access=PageAccess.USER,
        description="Community forums",
        icon="👥",
    ),
    Page(
        id="api",
        name="API Access",
        path="/api",
        access=PageAccess.USER,
        description="Basic API documentation",
        icon="🔌",
    ),
]


# =============================================================================
# DEV PAGES (Developer Tier)
# =============================================================================

DEV_PAGES: List[Page] = [
    Page(
        id="dev-dashboard",
        name="Developer Dashboard",
        path="/dev/dashboard",
        access=PageAccess.DEV,
        description="Developer home",
        icon="⚙️",
    ),
    Page(
        id="dev-tools",
        name="Dev Tools",
        path="/dev/tools",
        access=PageAccess.DEV,
        description="Developer tools and utilities",
        icon="🛠️",
    ),
    Page(
        id="premium-packages",
        name="Premium Packages",
        path="/dev/packages",
        access=PageAccess.DEV,
        description="Premium package downloads",
        icon="📦",
    ),
    Page(
        id="marketplace",
        name="Marketplace",
        path="/dev/marketplace",
        access=PageAccess.DEV,
        description="App marketplace and submissions",
        icon="🏪",
    ),
    Page(
        id="submit-app",
        name="Submit App",
        path="/dev/submit",
        access=PageAccess.DEV,
        description="Submit app to marketplace",
        icon="📤",
    ),
    Page(
        id="sandbox",
        name="Local Sandbox",
        path="/dev/sandbox",
        access=PageAccess.DEV,
        description="Local development sandbox",
        icon="🏖️",
    ),
    Page(
        id="api-key",
        name="API Key",
        path="/dev/api-key",
        access=PageAccess.DEV,
        description="API key management",
        icon="🔐",
    ),
    Page(
        id="collab-chat",
        name="Collaboration",
        path="/dev/chat",
        access=PageAccess.DEV,
        description="Collaborator chat (invite only)",
        icon="💬",
    ),
    Page(
        id="dev-docs",
        name="Dev Docs",
        path="/dev/docs",
        access=PageAccess.DEV,
        description="Developer documentation",
        icon="📖",
    ),
]


# =============================================================================
# BETA PAGES (Beta Tester Tier)
# =============================================================================

BETA_PAGES: List[Page] = [
    Page(
        id="beta-dashboard",
        name="Beta Dashboard",
        path="/beta/dashboard",
        access=PageAccess.BETA,
        description="Beta tester home",
        icon="🧪",
    ),
    Page(
        id="beta-features",
        name="Beta Features",
        path="/beta/features",
        access=PageAccess.BETA,
        description="Unreleased beta features",
        icon="🚀",
    ),
    Page(
        id="beta-sandbox",
        name="VPS Sandbox",
        path="/beta/sandbox",
        access=PageAccess.BETA,
        description="VPS sandbox with all apps",
        icon="☁️",
    ),
    Page(
        id="beta-secret",
        name="Beta Lounge",
        path="/beta/lounge",
        access=PageAccess.BETA,
        description="Secret beta testers chat",
        icon="🔒",
    ),
    Page(
        id="source-code",
        name="Source Code",
        path="/beta/source",
        access=PageAccess.BETA,
        description="Access to source code",
        icon="💻",
    ),
    Page(
        id="beta-downloads",
        name="Beta Downloads",
        path="/beta/downloads",
        access=PageAccess.BETA,
        description="Beta release downloads",
        icon="📥",
    ),
]


# =============================================================================
# SUPERUSER PAGES (Kenneth Only)
# =============================================================================

SUPERUSER_PAGES: List[Page] = [
    Page(
        id="admin",
        name="Admin Panel",
        path="/admin",
        access=PageAccess.SUPERUSER,
        description="System administration",
        icon="👑",
    ),
    Page(
        id="user-management",
        name="User Management",
        path="/admin/users",
        access=PageAccess.SUPERUSER,
        description="Manage all users",
        icon="👥",
    ),
    Page(
        id="beta-codes",
        name="Beta Codes",
        path="/admin/beta-codes",
        access=PageAccess.SUPERUSER,
        description="Generate beta invitation codes",
        icon="🎟️",
    ),
    Page(
        id="universal-blocks",
        name="Universal Blocks",
        path="/admin/blocks",
        access=PageAccess.SUPERUSER,
        description="Universal block management",
        icon="🚫",
    ),
    Page(
        id="system-config",
        name="System Config",
        path="/admin/config",
        access=PageAccess.SUPERUSER,
        description="System configuration",
        icon="⚙️",
    ),
    Page(
        id="licenses",
        name="Licenses",
        path="/admin/licenses",
        access=PageAccess.SUPERUSER,
        description="License management",
        icon="📜",
    ),
    Page(
        id="analytics",
        name="Analytics",
        path="/admin/analytics",
        access=PageAccess.SUPERUSER,
        description="System analytics",
        icon="📈",
    ),
]


# =============================================================================
# ALL PAGES INDEX
# =============================================================================

ALL_PAGES = {
    PageAccess.PUBLIC: PUBLIC_PAGES,
    PageAccess.USER: USER_PAGES,
    PageAccess.DEV: DEV_PAGES,
    PageAccess.BETA: BETA_PAGES,
    PageAccess.SUPERUSER: SUPERUSER_PAGES,
}


def get_pages_for_tier(tier: int) -> List[Page]:
    """
    Get all pages accessible to a tier.
    
    Uses DIMENSIONAL inheritance - higher tiers see all lower tier pages.
    """
    pages = []
    
    # Always include public
    pages.extend(PUBLIC_PAGES)
    
    # Add pages based on tier (dimensional - inherit lower)
    if tier >= 1:  # USER
        pages.extend(USER_PAGES)
    if tier >= 2:  # DEV
        pages.extend(DEV_PAGES)
    if tier >= 3:  # BETA
        pages.extend(BETA_PAGES)
    if tier >= 4:  # SUPERUSER
        pages.extend(SUPERUSER_PAGES)
    
    return pages


def can_access_page(user_tier: int, page: Page) -> bool:
    """Check if a user tier can access a page"""
    return user_tier >= page.access


def get_navigation_for_tier(tier: int) -> Dict[str, List[Page]]:
    """
    Get navigation structure for a tier.
    
    Returns pages grouped by access level.
    """
    nav = {
        "public": PUBLIC_PAGES,
        "main": [],
        "dev": [],
        "beta": [],
        "admin": [],
    }
    
    if tier >= 1:
        nav["main"] = USER_PAGES
    if tier >= 2:
        nav["dev"] = DEV_PAGES
    if tier >= 3:
        nav["beta"] = BETA_PAGES
    if tier >= 4:
        nav["admin"] = SUPERUSER_PAGES
    
    return nav


# =============================================================================
# FEATURE GATES (What features appear based on role)
# =============================================================================

@dataclass
class FeatureGate:
    """A feature with access control"""
    id: str
    name: str
    min_tier: int
    description: str = ""
    is_premium: bool = False  # Premium means paid for non-beta


FEATURE_GATES = [
    # Public features
    FeatureGate("view_docs", "View Documentation", 0, "Read public docs"),
    FeatureGate("view_demos", "View Demos", 0, "Interactive demos"),
    
    # User features
    FeatureGate("download_opensource", "Download Open Source", 1, "Download open source packages"),
    FeatureGate("basic_api", "Basic API", 1, "Basic API access"),
    FeatureGate("community_access", "Community Forums", 1, "Join community discussions"),
    
    # Dev features
    FeatureGate("dev_tools", "Developer Tools", 2, "Access dev tools", is_premium=True),
    FeatureGate("premium_packages", "Premium Packages", 2, "Download premium packages", is_premium=True),
    FeatureGate("marketplace_submit", "Submit to Marketplace", 2, "Submit apps to marketplace"),
    FeatureGate("local_sandbox", "Local Sandbox", 2, "Run local development sandbox"),
    FeatureGate("api_key", "API Key", 2, "Get developer API key"),
    FeatureGate("collab_chat", "Collaboration Chat", 2, "Chat with collaborators"),
    
    # Beta features
    FeatureGate("beta_features", "Beta Features", 3, "Access unreleased features"),
    FeatureGate("vps_sandbox", "VPS Sandbox", 3, "Cloud sandbox with all apps"),
    FeatureGate("beta_chat", "Beta Chat Room", 3, "Secret beta testers lounge"),
    FeatureGate("source_access", "Source Code Access", 3, "Access to source code"),
    FeatureGate("free_production", "Free Production", 3, "Free production license (Kenneth's content)"),
    
    # Superuser features
    FeatureGate("admin_panel", "Admin Panel", 4, "System administration"),
    FeatureGate("user_management", "User Management", 4, "Manage all users"),
    FeatureGate("beta_code_gen", "Generate Beta Codes", 4, "Create beta invitation codes"),
    FeatureGate("universal_block", "Universal Blocks", 4, "Block users globally"),
    FeatureGate("system_config", "System Configuration", 4, "Configure system settings"),
]


def get_features_for_tier(tier: int) -> List[FeatureGate]:
    """Get all features accessible to a tier"""
    return [f for f in FEATURE_GATES if tier >= f.min_tier]


def can_use_feature(user_tier: int, feature_id: str) -> bool:
    """Check if a user can use a feature"""
    for f in FEATURE_GATES:
        if f.id == feature_id:
            return user_tier >= f.min_tier
    return False
