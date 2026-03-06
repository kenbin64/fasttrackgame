"""
ButterflyFX DimensionsOS — Substrates Layer (x)

In the Fibonacci Dimensional Creation Model  z = x · y:
  x  =  substrates  —  raw state, persistence, and identity

A substrate is a pure state container.  It holds data but applies no
transformation.  Transformations live in manifolds/; emergent applications
live in dimensions/.

Substrate registry (Fibonacci-ordered by formation depth):
  Depth 1 — identity          : helix.substrate.Substrate, SubstrateIdentity
  Depth 2 — delta             : helix.substrate (delta layer)
  Depth 3 — memory            : substrates.ai.memory_substrate
  Depth 5 — geometric         : helix.geometric_substrate
  Depth 8 — content           : helix.content_substrate
  Depth 13 — universal        : helix.universal_substrate
  Depth 21 — ai-intelligence  : substrates.ai.dimensional_ai

O(1) access — import what you need from this single namespace.
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

# Fibonacci dimensional coordinate for this layer
FIBONACCI_DEPTH = 1   # x — the first axis
LAYER_NAME = "substrates"
LAYER_EQUATION = "x"

