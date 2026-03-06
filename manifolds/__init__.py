"""
ButterflyFX DimensionsOS — Manifolds Layer (y)

In the Fibonacci Dimensional Creation Model  z = x · y:
  y  =  manifolds  —  pure transformations over substrates

A manifold maps one substrate state to another without storing state itself.
The composition of a substrate (x) and a manifold (y) produces a dimension (z).

Manifold registry (Fibonacci-ordered by transformation depth):
  Depth 1  — core manifold      : helix.manifold.Manifold
  Depth 2  — wave manifold      : helix.wave_manifold
  Depth 3  — platform manifold  : helix.platform_manifold (ButterflyFXKernel)
  Depth 5  — openstack manifold : helix.openstack_manifold
  Depth 8  — OSI manifold       : helix.osi_manifold
  Depth 13 — fibonacci manifold : demos/fibonacci_universe/manifold_bridge

O(1) access — import any manifold from this single namespace.
"""

# ── Core manifold ──────────────────────────────────────────────────────────
try:
    from helix.manifold import (
        GenerativeManifold, IdentityManifold, RuntimeManifold,
        ScalingManifold, SemanticManifold, CompletionManifold,
        SurfacePoint, ManifoldRegion,
    )
    Manifold = GenerativeManifold   # canonical alias
except ImportError:
    GenerativeManifold = None
    IdentityManifold = None
    RuntimeManifold = None
    ScalingManifold = None
    SemanticManifold = None
    CompletionManifold = None
    SurfacePoint = None
    ManifoldRegion = None
    Manifold = None

# ── Wave manifold ──────────────────────────────────────────────────────────
try:
    from helix.wave_manifold import WaveManifold
except ImportError:
    WaveManifold = None

# ── Platform manifold (ButterflyFXKernel) ─────────────────────────────────
try:
    from helix.platform_manifold import ButterflyFXKernel, PlatformManifold
except ImportError:
    try:
        from helix.platform_manifold import ButterflyFXKernel
        PlatformManifold = None
    except ImportError:
        ButterflyFXKernel = None
        PlatformManifold = None

# ── OpenStack manifold ─────────────────────────────────────────────────────
try:
    from helix.openstack_manifold import OpenStackManifold
except ImportError:
    OpenStackManifold = None

# ── OSI manifold ───────────────────────────────────────────────────────────
try:
    from helix.osi_manifold import OSIManifold
except ImportError:
    OSIManifold = None

# ── Fibonacci manifold bridge ──────────────────────────────────────────────
try:
    from demos.fibonacci_universe.manifold_bridge import ManifoldBridge
except ImportError:
    ManifoldBridge = None

__all__ = [
    "Manifold",
    "WaveManifold",
    "ButterflyFXKernel", "PlatformManifold",
    "OpenStackManifold",
    "OSIManifold",
    "ManifoldBridge",
]

# Fibonacci dimensional coordinate for this layer
FIBONACCI_DEPTH = 2   # y — the second axis
LAYER_NAME = "manifolds"
LAYER_EQUATION = "y"

