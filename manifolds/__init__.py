"""
ButterflyFX DimensionsOS — Manifolds Layer  (y)

In the Fibonacci Dimensional Creation Model  z = x · y:
  y  =  manifolds  —  pure transformations

THE MANIFOLD IS A TWISTED SQUARE
─────────────────────────────────
The canonical manifold surface is  z = x·y  — a hyperbolic paraboloid.
Take a square.  Lift two opposite corners UP, press two opposite corners DOWN.
The saddle surface that forms is exactly z = x·y.

This surface is DOUBLY RULED — two complete families of straight lines cover
it (fix x=t → a line; fix y=t → a line).  At its saddle point, every possible
angular orientation of a tangent plane exists simultaneously.  No angle is
excluded.  The manifold IS the complete angle-space of the interaction between
x (substrate) and y (manifold).

Every Fibonacci square tiles one angular sector of this surface, spiraling out
at the golden angle ≈ 137.5°.  The twist in the surface IS the momentum carried
from layer to layer.  It is not a flat mapping.  It curves.  It contains.

  Fib=1 (Spark)    → 0° sector  — the seed point on the surface
  Fib=1 (Mirror)   → 137.5°     — the line that gives direction
  Fib=2 (Relation) → 275.0°     — WIDTH emerges, z=x·y first applies  ← HERE
  Fib=3 (Form)     → 52.5°      — plane stabilizes (manifolds produce this)
  ...converging toward φ = 1.618...

MANIFOLD REGISTRY (Fibonacci-ordered by transformation depth)
──────────────────────────────────────────────────────────────
  Fib 1  — core manifold      : helix.manifold.GenerativeManifold
  Fib 1  — wave manifold      : helix.wave_manifold.WaveManifold
  Fib 2  — platform manifold  : helix.platform_manifold.ButterflyFXKernel
  Fib 3  — openstack manifold : helix.openstack_manifold.OpenStackManifold
  Fib 5  — OSI manifold       : helix.osi_manifold.OSIManifold
  Fib 8  — fibonacci bridge   : demos.fibonacci_universe.manifold_bridge

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

# ── Momentum — live, sourced from the kernel ──────────────────────────────
from helix.kernel import (
    PHI, GOLDEN_ANGLE_DEG,
    LAYER_FIBONACCI, LAYER_ANGLE_DEG,
    LAYER_NAMES, LAYER_BIRTH, LAYER_CREATION, LAYER_EQUATIONS, LAYER_ICONS,
    LAYER_GEOMETRY, LAYER_DIMENSION_SQUARE,
    FIBONACCI_CAP, FIBONACCI_COMPLETE_SQUARE,
    MANIFOLD_SURFACE,
)

_LAYER = 3   # Relation — width emerges, z=x·y first applies

def _phi_ratio(layer):
    """Fibonacci ratio at this layer — current fan-out toward φ."""
    f_now  = LAYER_FIBONACCI[layer]
    f_prev = LAYER_FIBONACCI[layer - 1] if layer > 1 else 1
    return f_now / f_prev if f_prev else 1.0

def fan_out(steps=1):
    """
    Project manifold momentum forward N Fibonacci steps.
    Caps at FIBONACCI_CAP (21) — beyond that is cancer; 21 becomes
    a single point in the next spiral dimension.

        manifolds.fan_out(1)
        → {'layer': 4, 'fibonacci': 3, 'geometry': 'plane', ...}
    """
    layer = _LAYER
    for _ in range(steps):
        nxt = min(layer + 1, 7)
        if LAYER_FIBONACCI[nxt] > FIBONACCI_CAP:
            # healthy growth ceiling reached — unit transcends
            return {
                'layer':        'transcendence',
                'fibonacci':    FIBONACCI_CAP,
                'geometry':     'point in next spiral',
                'dimension_sq': FIBONACCI_COMPLETE_SQUARE,
                'phi_ratio':    PHI,
                'distance_to_phi': 0.0,
                'note':         f'F={FIBONACCI_CAP} is the healthy cap — '
                                 'this unit collapses to a single point '
                                 'and re-enters the next dimension as Fib=1',
            }
        layer = nxt
    f     = LAYER_FIBONACCI[layer]
    ratio = _phi_ratio(layer)
    return {
        'layer':           layer,
        'name':            LAYER_NAMES[layer],
        'geometry':        LAYER_GEOMETRY[layer],
        'dimension_sq':    LAYER_DIMENSION_SQUARE[layer],
        'fibonacci':       f,
        'phi_ratio':       ratio,
        'distance_to_phi': abs(PHI - ratio),
        'angle_deg':       LAYER_ANGLE_DEG[layer],
        'equation':        LAYER_EQUATIONS[layer],
        'icon':            LAYER_ICONS[layer],
    }

MOMENTUM = {
    # Position in the spiral
    'layer':           _LAYER,
    'name':            LAYER_NAMES[_LAYER],        # 'Relation'
    'birth':           LAYER_BIRTH[_LAYER],         # 'Structure'
    'creation':        LAYER_CREATION[_LAYER],      # 'Let the two interact'
    'equation':        LAYER_EQUATIONS[_LAYER],     # 'z = x * y'
    'icon':            LAYER_ICONS[_LAYER],         # '×'
    # Geometric identity
    'geometry':        LAYER_GEOMETRY[_LAYER],      # 'width'
    'surface':         MANIFOLD_SURFACE,            # full twisted-square descriptor
    'dimension_sq':    LAYER_DIMENSION_SQUARE[_LAYER],  # 2²=4  (the complete square)
    # Fibonacci momentum
    'fibonacci':       LAYER_FIBONACCI[_LAYER],     # 2
    'angle_deg':       LAYER_ANGLE_DEG[_LAYER],     # 275.02°
    'phi_ratio':       _phi_ratio(_LAYER),          # 2.0  (fanning wide, above φ)
    'distance_to_phi': abs(PHI - _phi_ratio(_LAYER)),   # 0.382 — closing on φ
    'phi':             PHI,                         # 1.618...
    'golden_angle':    GOLDEN_ANGLE_DEG,            # 137.507...°
    # Healthy growth
    'fibonacci_cap':   FIBONACCI_CAP,              # 21 — stop here
    'cap_sq':          FIBONACCI_COMPLETE_SQUARE,  # 441 — the final complete square
    # Axis role
    'axis':            'y',
    'role':            'pure transformation — the twisted square where every '
                       'angle is represented.  x·y produces z.  The manifold '
                       'does not store state; it twists substrate momentum '
                       'into dimensional form.',
}

