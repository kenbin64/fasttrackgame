"""
ButterflyFx Core - The Bridge Layer

═══════════════════════════════════════════════════════════════════
                    THE PUBLIC INTERFACE
═══════════════════════════════════════════════════════════════════

The Core is the ONLY way to interact with the kernel.
All data enters through the Core, gets converted to substrates,
processed through pure 64-bit math, and results returned.

ARCHITECTURE:
    - Kernel: Pure mathematical substrate (NO connections)
    - Core: Gateway, server, SRL connections, rendering
    - API: Public interface for developers

DEVELOPER API:
    from butterflyfx import ButterflyFx
    
    fx = ButterflyFx()
    result = fx.process(data)   # Data → Substrate
    result = fx.compute(...)    # Run operations
    fx.render(result)           # Display output

SRL (Connection Device):
    SRL is a Core function for connecting to datasources.
    Data fetched through SRL goes through ingest() into kernel.
    
    srl = SRL(domain="api.example.com", path="/data")
    result = srl.fetch()        # Returns bytes
    # Then: fx.process(result.data)  # Becomes substrate

═══════════════════════════════════════════════════════════════════
"""

# Internal ingest (NOT exposed publicly - use ButterflyFx API)
from ._ingest import (
    SubstrateManifest,
    IngestResult,
    AssetType,
    LensSpec,
    DeltaSpec,
    DimensionSpec,
)

# SRL Connection Device (Core function, NOT kernel)
from .srl import (
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
)

# Public Developer API
from .api import (
    ButterflyFx,
    FxResult,
    FxError,
    FxConfig,
    Computation,
    Pipeline,
    Projection,
    Reference,
    Transform,
)

# Validation (for law enforcement)
from .validator import Validator, ValidationError

# Expression builder (compiles to substrates)
from .expressions import Expression, ExpressionBuilder

# Translator (internal, but available for advanced use)
from .translator import Translator

# Dimensional Programming
from .dimensional import (
    Dimension,
    DimensionalSubstrate,
    DimensionalLens,
    DimensionalDelta,
    DimensionalManifold,
)

# Persistence (Internal and External Data Storage)
from .persistence import (
    Persistence,
    Store,
    LocalStore,
    CentralStore,
    StoreSRL,
    SRLReference,
    StoreType,
    SyncMode,
    PersistenceError,
    StoreNotFoundError,
    SubstrateNotFoundError,
    create_local_store,
    create_central_store,
    create_memory_store,
)

__all__ = [
    # Developer API (primary interface)
    'ButterflyFx',
    'FxResult',
    'FxError',
    'FxConfig',
    'Computation',
    'Pipeline',
    'Projection',
    'Reference',
    'Transform',
    
    # SRL Connection Device
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
    
    # Result types
    'IngestResult',
    'SubstrateManifest',
    'AssetType',
    
    # Spec classes for special substrates
    'LensSpec',
    'DeltaSpec',
    'DimensionSpec',
    
    # Utilities
    'Validator',
    'ValidationError',
    'Expression',
    'ExpressionBuilder',
    'Translator',
    
    # Dimensional Programming
    'Dimension',
    'DimensionalSubstrate',
    'DimensionalLens',
    'DimensionalDelta',
    'DimensionalManifold',
    
    # Persistence (Internal/External Storage)
    'Persistence',
    'Store',
    'LocalStore',
    'CentralStore',
    'StoreSRL',
    'SRLReference',
    'StoreType',
    'SyncMode',
    'PersistenceError',
    'StoreNotFoundError',
    'SubstrateNotFoundError',
    'create_local_store',
    'create_central_store',
    'create_memory_store',
]
