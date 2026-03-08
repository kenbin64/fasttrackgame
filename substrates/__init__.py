"""
ButterflyFX DimensionsOS — Substrates Layer  (x)

In the Fibonacci Dimensional Creation Model  z = x · y:
  x  =  substrates  —  raw state, persistence, identity

A substrate is the SPARK — the first unit of momentum (Fib 1, Layer 1).
It holds state but applies no transformation.  Momentum fans out from here
toward the golden ratio φ ≈ 1.618 with every successive Fibonacci step.

        Layer 1 • Spark      fib=1  angle=  0.00°  ratio→φ: 1.000
        Layer 2 ━ Mirror     fib=1  angle=137.51°  ratio→φ: 1.000
        Layer 3 × Relation   fib=2  angle=275.02°  ratio→φ: 2.000  ← manifolds
        Layer 4 ▲ Form       fib=3  angle= 52.52°  ratio→φ: 1.500  ← dimensions
        ...converges to φ = 1.6180...

THIS layer sits at Layer 1 — the seed from which all momentum originates.
"""

# ── Helix kernel substrates ────────────────────────────────────────────────
try:
    from helix.substrate import ManifoldSubstrate, Token
    Substrate = ManifoldSubstrate   # canonical alias
    SubstrateIdentity = Token       # token = identity-in-a-substrate
except ImportError:
    ManifoldSubstrate = None
    Token = None
    Substrate = None
    SubstrateIdentity = None

try:
    from helix.geometric_substrate import GeometricSubstrate
except ImportError:
    GeometricSubstrate = None

try:
    from helix.content_substrate import ContentSubstrate
except ImportError:
    ContentSubstrate = None

try:
    from helix.universal_substrate import UniversalSubstrate
except ImportError:
    UniversalSubstrate = None

try:
    from helix.ai_substrate import AISubstrate
except ImportError:
    AISubstrate = None

# ── AI / Memory substrates (substrates/ai/) ────────────────────────────────
try:
    from substrates.ai.memory_substrate import (
        MemorySubstrate, MemoryPoint, DimensionalMemoryIndex
    )
except ImportError:
    MemorySubstrate = None
    MemoryPoint = None
    DimensionalMemoryIndex = None

try:
    from substrates.ai.delta_substrate import DeltaSubstrate
except ImportError:
    DeltaSubstrate = None

try:
    from substrates.ai.dimensional_ai import (
        DimensionalAI, AIConfig, IntentionVector,
        IntentionSubstrate, AIIngestionSubstrate,
    )
except ImportError:
    DimensionalAI = None
    AIConfig = None
    IntentionVector = None
    IntentionSubstrate = None
    AIIngestionSubstrate = None

__all__ = [
    # helix kernel substrates
    "Substrate", "SubstrateIdentity",
    "GeometricSubstrate", "ContentSubstrate",
    "UniversalSubstrate", "AISubstrate",
    # ai substrates
    "MemorySubstrate", "MemoryPoint", "DimensionalMemoryIndex",
    "DeltaSubstrate",
    "DimensionalAI", "AIConfig", "IntentionVector",
    "IntentionSubstrate", "AIIngestionSubstrate",
]

# ── Momentum — live, sourced from the kernel ──────────────────────────────
from helix.kernel import (
    PHI, GOLDEN_ANGLE_DEG,
    LAYER_FIBONACCI, LAYER_ANGLE_DEG,
    LAYER_NAMES, LAYER_BIRTH, LAYER_CREATION, LAYER_EQUATIONS, LAYER_ICONS,
)

_LAYER = 1   # Spark — the seed

def _phi_ratio(layer):
    """Fibonacci ratio at this layer — the current fan-out toward φ."""
    f_now  = LAYER_FIBONACCI[layer]
    f_prev = LAYER_FIBONACCI[layer - 1] if layer > 1 else 1
    return f_now / f_prev if f_prev else 1.0

def fan_out(steps=1):
    """
    Project momentum forward N Fibonacci steps from this layer.
    Returns a dict showing how momentum fans toward φ.

        substrates.fan_out(2)
        → {'layer': 3, 'fibonacci': 2, 'phi_ratio': 2.0,
           'distance_to_phi': 0.382, 'angle_deg': 275.02}

    Each step fans the spiral by the golden angle (≈137.5°).
    The ratio converges to φ ≈ 1.618 from above and below alternately.
    """
    layer = _LAYER
    for _ in range(steps):
        layer = min(layer + 1, 7)
    f = LAYER_FIBONACCI[layer]
    ratio = _phi_ratio(layer)
    return {
        'layer':           layer,
        'name':            LAYER_NAMES[layer],
        'fibonacci':       f,
        'phi_ratio':       ratio,
        'distance_to_phi': abs(PHI - ratio),
        'angle_deg':       LAYER_ANGLE_DEG[layer],
        'equation':        LAYER_EQUATIONS[layer],
        'icon':            LAYER_ICONS[layer],
    }

MOMENTUM = {
    'layer':           _LAYER,
    'name':            LAYER_NAMES[_LAYER],       # 'Spark'
    'birth':           LAYER_BIRTH[_LAYER],        # 'Existence'
    'creation':        LAYER_CREATION[_LAYER],     # 'Let there be the First Point'
    'equation':        LAYER_EQUATIONS[_LAYER],    # 'P₀ = {1}'
    'icon':            LAYER_ICONS[_LAYER],        # '•'
    'fibonacci':       LAYER_FIBONACCI[_LAYER],    # 1
    'angle_deg':       LAYER_ANGLE_DEG[_LAYER],    # 0.0°
    'phi_ratio':       _phi_ratio(_LAYER),         # 1.0  (seed, not yet fanning)
    'distance_to_phi': abs(PHI - _phi_ratio(_LAYER)),  # 0.618 — potential energy
    'phi':             PHI,                        # 1.618...
    'golden_angle':    GOLDEN_ANGLE_DEG,           # 137.507...°
    'axis':            'x',
    'role':            'raw state & persistence — the substrate carries momentum '
                       'at rest; it does not transform, it accumulates.',
}

