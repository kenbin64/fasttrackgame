"""
ButterflyFx - Dimensional Computation Framework

═══════════════════════════════════════════════════════════════════════════════
                    THE COMPLETE PROGRAMMING PARADIGM
═══════════════════════════════════════════════════════════════════════════════

QUICK START:
    from butterflyfx import ButterflyFx
    
    fx = ButterflyFx()
    
    # Process any data into a substrate
    result = fx.process(42)
    
    # Compute operations
    result = fx.compute(Computation.xor(100, 50))
    
    # Dimensional programming
    obj = fx.substrate({"x": 0, "y": 100})
    falling = obj.apply(fx.delta({"dy": -9.8}))
    
    # Connect to external data via SRL
    srl = http_srl("https://api.example.com/data")
    result = fx.fetch(srl)

═══════════════════════════════════════════════════════════════════════════════

Three-Layer Sanctum Architecture:

┌─────────────────────────────────────────────────────┐
│  INTERFACE LAYER (Human / Machine / AI)             │
│  └── DTOs, Instructions, Code                       │
│  └── IMPORTS: core only                             │
├─────────────────────────────────────────────────────┤
│  CORE LAYER (Logic Bridge)                          │
│  └── ONLY bridge to Kernel                          │
│  └── Translates all external intent to math         │
│  └── IMPORTS: kernel only                           │
├─────────────────────────────────────────────────────┤
│  KERNEL LAYER (Inner Sanctum)                       │
│  └── Pure mathematical expressions                  │
│  └── IMMUTABLE - never altered, only invoked        │
│  └── IMPORTS: none (self-contained)                 │
└─────────────────────────────────────────────────────┘

Access Rules:
- Interface → Core → Kernel (one-way only)
- Kernel cannot be accessed directly from Interface
- Kernel cannot be modified at runtime
"""

__version__ = "1.0.0"
__author__ = "Kenneth Bingham"

# ═══════════════════════════════════════════════════════════════════════════════
# CORE API - The Primary Developer Interface
# ═══════════════════════════════════════════════════════════════════════════════

from core_v2 import (
    # Main API class
    ButterflyFx,
    FxResult,
    FxError,
    FxConfig,
    
    # Computation types
    Computation,
    Pipeline,
    Projection,
    Reference,
    Transform,
    
    # SRL Connection Device
    SRL,
    SRLConnection,
    SRLResult,
    SRLConfig,
    SRLError,
    
    # Protocols
    Protocol,
    FileProtocol,
    HTTPProtocol,
    SocketProtocol,
    DatabaseProtocol,
    
    # Credentials
    Credentials,
    APIKey,
    BasicAuth,
    TokenAuth,
    CertAuth,
    
    # Factory functions
    file_srl,
    http_srl,
    socket_srl,
    
    # Result types
    IngestResult,
    SubstrateManifest,
    AssetType,
    
    # Spec classes
    LensSpec,
    DeltaSpec,
    DimensionSpec,
    
    # Expression builder
    Expression,
    ExpressionBuilder,
    
    # Dimensional programming
    Dimension,
    DimensionalSubstrate,
    DimensionalLens,
    DimensionalDelta,
    DimensionalManifold,
    
    # Persistence
    Persistence,
    Store,
    LocalStore,
    CentralStore,
    create_local_store,
    create_central_store,
    create_memory_store,
    
    # Validation
    Validator,
    ValidationError,
)

# ═══════════════════════════════════════════════════════════════════════════════
# INTERFACE LAYER - DTOs and Interface Classes
# ═══════════════════════════════════════════════════════════════════════════════

from interface import (
    # DTOs
    SubstrateDTO,
    LensDTO,
    ManifoldDTO,
    InvocationRequest,
    InvocationResponse,
    DeltaDTO,
    PromotionRequest,
    # Interfaces
    HumanInterface,
    MachineInterface,
    AIInterface,
)

# ═══════════════════════════════════════════════════════════════════════════════
# HIGH-LEVEL APIs
# ═══════════════════════════════════════════════════════════════════════════════

from dimension_os import (
    DimensionOS,
    DimensionalObject,
    UniversalConnector,
)

from math_substrate import (
    MathSubstrate,
    MatrixSubstrate,
    GridSubstrate,
    SpectrumSubstrate,
    StratumSubstrate,
    Lens as MathLens,
    expr,
    matrix,
    grid2d,
    grid3d,
    spectrum,
    stratum,
)


__all__ = [
    # ═══ Main API ═══
    'ButterflyFx',
    'FxResult',
    'FxError',
    'FxConfig',
    
    # ═══ Computation ═══
    'Computation',
    'Pipeline',
    'Projection',
    'Reference',
    'Transform',
    
    # ═══ SRL Connection Device ═══
    'SRL',
    'SRLConnection',
    'SRLResult',
    'SRLConfig',
    'SRLError',
    'Protocol',
    'FileProtocol',
    'HTTPProtocol',
    'SocketProtocol',
    'DatabaseProtocol',
    'Credentials',
    'APIKey',
    'BasicAuth',
    'TokenAuth',
    'CertAuth',
    'file_srl',
    'http_srl',
    'socket_srl',
    
    # ═══ Results & Specs ═══
    'IngestResult',
    'SubstrateManifest',
    'AssetType',
    'LensSpec',
    'DeltaSpec',
    'DimensionSpec',
    
    # ═══ Expression Builder ═══
    'Expression',
    'ExpressionBuilder',
    
    # ═══ Dimensional Programming ═══
    'Dimension',
    'DimensionalSubstrate',
    'DimensionalLens',
    'DimensionalDelta',
    'DimensionalManifold',
    
    # ═══ Persistence ═══
    'Persistence',
    'Store',
    'LocalStore',
    'CentralStore',
    'create_local_store',
    'create_central_store',
    'create_memory_store',
    
    # ═══ Validation ═══
    'Validator',
    'ValidationError',
    
    # ═══ Interface Layer ═══
    'SubstrateDTO',
    'LensDTO',
    'ManifoldDTO',
    'InvocationRequest',
    'InvocationResponse',
    'DeltaDTO',
    'PromotionRequest',
    'HumanInterface',
    'MachineInterface',
    'AIInterface',
    
    # ═══ High-Level APIs ═══
    'DimensionOS',
    'DimensionalObject',
    'UniversalConnector',
    
    # ═══ Math Substrates ═══
    'MathSubstrate',
    'MatrixSubstrate',
    'GridSubstrate',
    'SpectrumSubstrate',
    'StratumSubstrate',
    'MathLens',
    'expr',
    'matrix',
    'grid2d',
    'grid3d',
    'spectrum',
    'stratum',
]
