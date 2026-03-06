"""
ButterflyFX DimensionsOS — Dimensions Layer (z = x · y)

In the Fibonacci Dimensional Creation Model  z = x · y:
  z  =  dimensions  —  emergent applications

A dimension is the product of a substrate (x) and a manifold (y).
It is the highest-level concept in the DimensionsOS hierarchy:
applications, services, and interactive systems that emerge from
combining raw state with pure transformation.

Dimension registry (Fibonacci-ordered by emergence level):
  Depth 2  — helix database    : apps.helix_database
  Depth 3  — connector         : apps.universal_connector  (40+ live APIs)
  Depth 5  — harddrive         : apps.universal_harddrive  (virtual filesystem)
  Depth 8  — explorer          : apps.dimensional_explorer (dimensional nav)
  Depth 13 — games / fasttrack : web/games/fasttrack
  Depth 21 — brickbreaker 3D   : web/kensgames/brickbreaker3d

O(1) access — import any dimension from this single namespace.
"""

# ── Helix database (foundational data dimension) ───────────────────────────
try:
    from apps.helix_database import (
        HelixDatabase, HelixRecord, HelixCollection, HelixQuery
    )
except ImportError:
    HelixDatabase = None
    HelixRecord = None
    HelixCollection = None
    HelixQuery = None

# ── Universal Connector (API aggregation dimension) ────────────────────────
try:
    from apps.universal_connector import (
        UniversalConnector, APIConnection, ConnectionResult
    )
except ImportError:
    UniversalConnector = None
    APIConnection = None
    ConnectionResult = None

# ── Universal Hard Drive (virtual filesystem dimension) ────────────────────
try:
    from apps.universal_harddrive import (
        UniversalHardDrive, SRL, VirtualDrive, FileNode, run_server
    )
except ImportError:
    UniversalHardDrive = None
    SRL = None
    VirtualDrive = None
    FileNode = None
    run_server = None

# ── Dimensional Explorer (navigation dimension) ────────────────────────────
try:
    from apps.dimensional_explorer import (
        DimensionalExplorer, ExplorerNode, run_explorer
    )
except ImportError:
    DimensionalExplorer = None
    ExplorerNode = None
    run_explorer = None

__all__ = [
    # helix database
    "HelixDatabase", "HelixRecord", "HelixCollection", "HelixQuery",
    # connector
    "UniversalConnector", "APIConnection", "ConnectionResult",
    # harddrive
    "UniversalHardDrive", "SRL", "VirtualDrive", "FileNode", "run_server",
    # explorer
    "DimensionalExplorer", "ExplorerNode", "run_explorer",
]

# Fibonacci dimensional coordinate for this layer
FIBONACCI_DEPTH = 3   # z — the third axis (z = x · y, 1·2=2, 1·2=2... → 3rd Fib)
LAYER_NAME = "dimensions"
LAYER_EQUATION = "z = x · y"

