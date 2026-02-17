"""
ButterflyFX Helix - Complete Dimensional Computing Framework

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

This mathematical kernel belongs to all humanity.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

Formal implementation of the dimensional helix model.
See BUTTERFLYFX_SPECIFICATION.md for the formal specification.

Layers:
    1. Primitives: Core building blocks (kernel, substrate, context)
    2. Utilities: Practical tools (path, query, cache, serialization)
    3. Foundation: Reusable components (database, filesystem, store, graph)
    4. Apps: Example applications (explorer, pipeline, API aggregator)
"""

# Core (Layer 0)
from .kernel import HelixKernel, HelixState, LEVEL_NAMES, LEVEL_ICONS
from .substrate import (
    ManifoldSubstrate, 
    Token,
    PayloadSource,
    GeometricProperty,
    # Natural Lens System
    NaturalLens,
    ColorLens,
    SoundLens,
    ValueLens,
    LensType,
    PhysicalConstants,
    PHYSICS,
)

# Generative Manifold (Layer 0.5) - Mathematical Surface That Produces Data Types
from .manifold import (
    GenerativeManifold,
    SurfacePoint,
    ManifoldRegion,
    LEVEL_ANGLES,
    helix_sin,
    helix_cos,
    helix_slope,
    helix_curvature,
)

# Primitives (Layer 1)
from .primitives import (
    DimensionalType,
    LazyValue,
    HelixContext,
    DimensionalIterator,
    HelixCollection,
)

# Utilities (Layer 2)
from .utilities import (
    HelixPath,
    HelixQuery,
    HelixCache,
    HelixSerializer,
    HelixDiff,
    HelixDiffResult,
    HelixLogger,
    ManifoldSampler,
    ManifoldQuery,
)

# Foundation (Layer 3)
from .foundation import (
    HelixDB,
    HelixDBQuery,
    HelixRecord,
    HelixFS,
    HelixFile,
    HelixStore,
    HelixGraph,
    HelixNode,
)

# Assembler (Layer 3.5) - File Reconstruction from Manifold Data
from .assembler import (
    FileCategory,
    AssembledFile,
    FileAssembler,
    VirtualEntry,
    ManifoldFileSystem,
    get_category,
    get_level,
)

# Transport (Layer 3.7) - Network Transport via Helix Structure
from .transport import (
    TransportLevel,
    TRANSPORT_NAMES,
    HelixPacket,
    HelixStream,
    HelixTransport,
    HelixWire,
)

# OSI-Manifold Transport (Layer 3.75) - The Network IS the Manifold
from .osi_manifold import (
    OSIHelixLayer,
    LAYER_INFO,
    ManifoldAddress,
    ManifoldDatagram,
    ManifoldRouter,
    OSIManifoldStack,
    HTTPManifoldBridge,
    create_dimensional_server_content,
    encode_sine_wave,
    encode_parametric_surface,
    encode_transformation,
)

# Content Substrate (Layer 3.8) - Application to Transport Bridge
from .content_substrate import (
    ContentDimension,
    ContentItem,
    ContentSubstrate,
    create_butterflyfx_content,
)

# Audio Transport (Layer 3.85) - Low-Latency Audio for Music Collaboration
from .audio_transport import (
    AudioLevel,
    AUDIO_LEVEL_PRIORITY,
    AudioFrame,
    SyncSignal,
    AudioStream,
    AudioTransport,
    LatencyOptimizer,
)

# Manifold Server (Layer 3.9) - Transmit Math, Not Bytes
from .manifold_server import (
    WaveformType,
    WaveformDescriptor,
    ManifoldPacket,
    AudioAnalyzer,
    ManifoldServer,
    ManifoldClient,
)

# Presentation Engine (Layer 4.5) - Timeline-Based Dynamic Content
from .presentation import (
    EasingFunction,
    ContentType,
    Keyframe,
    ContentElement,
    TimelineMarker,
    Presentation,
    PresentationBuilder,
    HTMLGenerator,
)

# Dimensional Presentation (Layer 4.6) - Non-Linear Hierarchy Navigation
from .dimensional_presentation import (
    DimensionLevel,
    LEVEL_NAMES as DIM_LEVEL_NAMES,
    LEVEL_ICONS as DIM_LEVEL_ICONS,
    DimensionalCoord,
    DimensionalNode,
    DimensionalPresentation,
    DimensionalBuilder,
    DimensionalHTMLGenerator,
)

# 3D Graphics Engine (Layer 5) - True Mathematical 3D
from .graphics3d import (
    Vec3,
    Mat4,
    Quaternion,
    Vertex,
    Triangle,
    Mesh,
    RigidBody,
    AABB,
    Sphere as SphereCollider,
    PhysicsWorld,
    Camera,
    SceneObject,
    Scene,
    Renderer,
    create_demo_scene,
)

# Apps (Layer 4)
from .apps import (
    HelixExplorer,
    HelixDataPipeline,
    HelixAPIAggregator,
    HelixEventSystem,
    HelixEvent,
    run_demos,
)

# Benchmark
from .benchmark import run_benchmark

# Helpers (Layer 0.1) - Foundational Utilities
from .constants import (
    PHI,
    PHI_INVERSE,
    FIBONACCI,
    PI,
    TAU,
    Level,
    LEVEL_DIMENSIONS,
    LEVEL_COLORS,
    Operation,
    fib,
    level_position,
    is_fibonacci,
    level_angle,
    level_by_name,
    ALL_LEVELS,
)

from .validators import (
    ValidationResult,
    validate_level,
    validate_state,
    validate_token,
    validate_state_transition,
    validate_payload_schema,
    Validator,
)

from .converters import (
    HelixJSONEncoder,
    to_json,
    from_json,
    state_to_dict,
    dict_to_state,
    token_to_dict,
    dict_to_token,
    to_numpy,
    to_dataframe,
    quick_token,
    nested_to_dimensional,
    level_to_fraction,
)

from .builders import (
    TokenBuilder,
    BatchTokenBuilder,
    StateBuilder,
    ManifoldBuilder,
    PathBuilder,
    KernelBuilder,
    token,
    manifold,
    state,
)

from .decorators import (
    dimensional,
    at_level,
    cached_by_level,
    spiral_scoped,
    timed,
    trace_helix,
    materialize_result,
    with_kernel,
    level_guard,
)

from .shortcuts import (
    tok,
    toks,
    st,
    kern,
    go,
    up,
    down,
    mani,
    mat,
    show_token,
    show_state,
    helix,
)

# Kernel Primitives (Layer 5.5) - Open Source Foundation
from .kernel_primitives import (
    Scalar as KernelScalar,
    Vector2D as KernelVector2D,
    Vector3D as KernelVector3D,
    Matrix3x3 as KernelMatrix3x3,
    Matrix4x4 as KernelMatrix4x4,
    RGB as KernelRGB,
    RGBA as KernelRGBA,
    Frequency as KernelFrequency,
    Amplitude as KernelAmplitude,
    Duration as KernelDuration,
    TimePoint as KernelTimePoint,
    Substrate as KernelSubstrate,
    SecureResourceLocator as KernelSRL,
)

# Enhanced Primitives (Layer 5.55) - Performance-Optimized Types
from .enhanced_primitives import (
    # Reactive System
    ReactiveValue,
    ComputedValue,
    Lazy,
    # Optimized Vectors
    Vector3D as EnhancedVector3D,
    VectorBatch,
    # Rotation
    Quaternion as EnhancedQuaternion,
    Transform,
    # Color
    Color as EnhancedColor,
    # Temporal
    Duration as EnhancedDuration,
    TimePoint as EnhancedTimePoint,
    # Binary Encoding
    BinaryEncoder,
)

# Optimized Kernel (Layer 5.6) - Performance-Enhanced State Machine
from .optimized_kernel import (
    OptimizedHelixKernel,
    HelixState as OptimizedHelixState,
    KernelEvent,
    EventEmitter,
    TimedLRUCache,
    TransitionMemo,
    KernelPool,
    KernelContext,
    KernelSnapshot,
    BatchResult,
    create_kernel,
    create_pool,
)

# Developer Utilities (Layer 5.65) - Dev Tools
from .dev_utils import (
    DimensionalLogger,
    Profiler,
    benchmark,
    typecheck,
    inspect_substrate,
    inspect_kernel,
    SubstrateBuilder,
    FluentBuilder,
    substrate as substrate_decorator,
    operation as operation_decorator,
    primitive as primitive_decorator,
    DimensionalError,
    InvalidStateError,
    TokenNotFoundError,
    OperationNotFoundError,
    DimensionalTestCase,
)

# Serialization & Transport (Layer 5.7) - Wire Formats
from .serialization import (
    BinarySerializer,
    JSONSerializer,
    SRLSerializer,
    StreamingSerializer,
    DimensionalSerializer,
    SerializationConfig,
    Compression,
    TypeCode,
    Transport,
    TransportMessage,
    MemoryTransport,
    MessageChannel,
    SchemaRegistry,
    serialize,
    deserialize,
    to_srl,
    from_srl,
)

# Dimensional Foundation (Layer 5.8) - Universal Base Classes
from .dimensional_foundation import (
    # State
    Level as DimLevel,
    LEVEL_NAMES as DIM_FOUNDATION_LEVEL_NAMES,
    DimensionalState,
    InvokeResult,
    # Protocols
    Invokable,
    Completable,
    Collapsible,
    # Base Classes
    Dimensional,
    AutoDimensional,
    DimensionalInterface,
    # Concrete Types
    DimensionalValue,
    DimensionalList,
    DimensionalDict,
    # Factory
    DimensionalFactory,
    register as register_dimensional,
    create as create_dimensional,
    # Decorator
    dimensional as dimensional_decorator,
    # Interface Generation
    interface as generate_interface,
    compose as compose_interfaces,
    # Convenience
    dim,
    dimlist,
    dimdict,
    # SRL
    srl as foundation_srl,
    invoke_srl,
)

# Licensing System (Layer 5.6) - Package Access Control
from .licensing import (
    LicenseTier,
    PackageInfo,
    License,
    LicenseManager,
    requires_license,
    check_license,
)

# Package Registry (Layer 5.7) - Subscription Packages
from .packages import (
    Package,
    PackageRegistry,
    available_packages,
    all_packages,
    get_package,
    upgrade_url,
)

# Substrates Architecture (Layer 6) - Composable Domain Primitives
from .substrates import (
    # Kernel & SRL
    SubstrateKernel, KERNEL,
    SecureResourceLocator, srl, invoke,
    
    # Base classes
    Substrate, CompositeSubstrate, CustomSubstrate,
    PrimitiveType, KernelPrimitive,
    
    # Mathematical primitives
    Scalar, Vector2D, Vector3D, Matrix3x3, Matrix4x4,
    
    # Color primitives
    RGB, RGBA, GradientStop,
    
    # Sound primitives
    Frequency, Amplitude, Waveform, Duration, TimePoint,
    
    # 3D primitives
    Vertex as SubstrateVertex, Edge, Triangle as SubstrateTriangle, 
    Mesh as SubstrateMesh,
    
    # Physics primitives
    PhysicsBody, MaterialProperties, MatterState,
    
    # Graphics substrates
    PixelSubstrate, ColorSubstrate, GradientSubstrate,
    ShaderSubstrate, Graphics3DSubstrate,
    
    # Physics substrates
    PhysicsSubstrate, SolidSubstrate, LiquidSubstrate,
    GasSubstrate, DynamicsSubstrate,
    
    # Text substrates
    ASCIISubstrate, UnicodeSubstrate, FontSubstrate,
    GrammarSubstrate, NaturalLanguageSubstrate,
    
    # Media substrates
    VoiceSynthesisSubstrate, SheetMusicSubstrate, ImageSubstrate,
    
    # Theory substrates
    ColorTheorySubstrate, MusicTheorySubstrate,
    StatisticsSubstrate, GameTheorySubstrate,
    
    # Pattern substrates
    FractalSubstrate, PatternSubstrate,
    EdgeFindingSubstrate, TilingSubstrate,
    
    # Advanced substrates
    QuantumSubstrate, GameEngineSubstrate,
)

__all__ = [
    # Core
    'HelixKernel',
    'HelixState',
    'LEVEL_NAMES',
    'LEVEL_ICONS',
    'ManifoldSubstrate',
    'Token',
    'PayloadSource',
    'GeometricProperty',
    
    # Generative Manifold
    'GenerativeManifold',
    'SurfacePoint',
    'ManifoldRegion',
    'LEVEL_ANGLES',
    'helix_sin',
    'helix_cos',
    'helix_slope',
    'helix_curvature',
    
    # Primitives
    'DimensionalType',
    'LazyValue',
    'HelixContext',
    'DimensionalIterator',
    'HelixCollection',
    
    # Utilities
    'HelixPath',
    'HelixQuery',
    'HelixCache',
    'HelixSerializer',
    'HelixDiff',
    'HelixDiffResult',
    'HelixLogger',
    'ManifoldSampler',
    'ManifoldQuery',
    
    # Foundation
    'HelixDB',
    'HelixDBQuery',
    'HelixRecord',
    'HelixFS',
    'HelixFile',
    'HelixStore',
    'HelixGraph',
    'HelixNode',
    
    # Assembler
    'FileCategory',
    'AssembledFile',
    'FileAssembler',
    'VirtualEntry',
    'ManifoldFileSystem',
    'get_category',
    'get_level',
    
    # Transport
    'TransportLevel',
    'TRANSPORT_NAMES',
    'HelixPacket',
    'HelixStream',
    'HelixTransport',
    'HelixWire',
    
    # Audio Transport
    'AudioLevel',
    'AUDIO_LEVEL_PRIORITY',
    'AudioFrame',
    'SyncSignal',
    'AudioStream',
    'AudioTransport',
    'LatencyOptimizer',
    
    # Manifold Server
    'WaveformType',
    'WaveformDescriptor',
    'ManifoldPacket',
    'AudioAnalyzer',
    'ManifoldServer',
    'ManifoldClient',
    
    # Presentation Engine
    'EasingFunction',
    'ContentType',
    'Keyframe',
    'ContentElement',
    'TimelineMarker',
    'Presentation',
    'PresentationBuilder',
    'HTMLGenerator',
    
    # Dimensional Presentation
    'DimensionLevel',
    'DIM_LEVEL_NAMES',
    'DIM_LEVEL_ICONS',
    'DimensionalCoord',
    'DimensionalNode',
    'DimensionalPresentation',
    'DimensionalBuilder',
    'DimensionalHTMLGenerator',
    
    # 3D Graphics Engine
    'Vec3',
    'Mat4',
    'Quaternion',
    'Vertex',
    'Triangle',
    'Mesh',
    'RigidBody',
    'AABB',
    'SphereCollider',
    'PhysicsWorld',
    'Camera',
    'SceneObject',
    'Scene',
    'Renderer',
    'create_demo_scene',
    
    # Apps
    'HelixExplorer',
    'HelixDataPipeline',
    'HelixAPIAggregator',
    'HelixEventSystem',
    'HelixEvent',
    'run_demos',
    
    # Benchmark
    'run_benchmark',
    
    # Constants
    'PHI',
    'PHI_INVERSE',
    'FIBONACCI',
    'PI',
    'TAU',
    'Level',
    'LEVEL_DIMENSIONS',
    'LEVEL_COLORS',
    'Operation',
    'fib',
    'level_position',
    'is_fibonacci',
    'level_angle',
    'level_by_name',
    'ALL_LEVELS',
    
    # Validators
    'ValidationResult',
    'validate_level',
    'validate_state',
    'validate_token',
    'validate_state_transition',
    'validate_payload_schema',
    'Validator',
    
    # Converters
    'HelixJSONEncoder',
    'to_json',
    'from_json',
    'state_to_dict',
    'dict_to_state',
    'token_to_dict',
    'dict_to_token',
    'to_numpy',
    'to_dataframe',
    'quick_token',
    'nested_to_dimensional',
    'level_to_fraction',
    
    # Builders
    'TokenBuilder',
    'BatchTokenBuilder',
    'StateBuilder',
    'ManifoldBuilder',
    'PathBuilder',
    'KernelBuilder',
    'token',
    'manifold',
    'state',
    
    # Decorators
    'dimensional',
    'at_level',
    'cached_by_level',
    'spiral_scoped',
    'timed',
    'trace_helix',
    'materialize_result',
    'with_kernel',
    'level_guard',
    
    # Shortcuts
    'tok',
    'toks',
    'st',
    'kern',
    'go',
    'up',
    'down',
    'mani',
    'mat',
    'show_token',
    'show_state',
    'helix',
    
    # Kernel Primitives (Open Source Foundation)
    'KernelScalar', 'KernelVector2D', 'KernelVector3D',
    'KernelMatrix3x3', 'KernelMatrix4x4',
    'KernelRGB', 'KernelRGBA',
    'KernelFrequency', 'KernelAmplitude',
    'KernelDuration', 'KernelTimePoint',
    'KernelSubstrate', 'KernelSRL',
    
    # Enhanced Primitives
    'ReactiveValue', 'ComputedValue', 'Lazy',
    'EnhancedVector3D', 'VectorBatch',
    'EnhancedQuaternion', 'Transform',
    'EnhancedColor',
    'EnhancedDuration', 'EnhancedTimePoint',
    'BinaryEncoder',
    
    # Optimized Kernel
    'OptimizedHelixKernel', 'OptimizedHelixState',
    'KernelEvent', 'EventEmitter',
    'TimedLRUCache', 'TransitionMemo',
    'KernelPool', 'KernelContext', 'KernelSnapshot', 'BatchResult',
    'create_kernel', 'create_pool',
    
    # Developer Utilities
    'DimensionalLogger', 'Profiler', 'benchmark', 'typecheck',
    'inspect_substrate', 'inspect_kernel',
    'SubstrateBuilder', 'FluentBuilder',
    'substrate_decorator', 'operation_decorator', 'primitive_decorator',
    'DimensionalError', 'InvalidStateError', 'TokenNotFoundError', 'OperationNotFoundError',
    'DimensionalTestCase',
    
    # Serialization & Transport
    'BinarySerializer', 'JSONSerializer', 'SRLSerializer',
    'StreamingSerializer', 'DimensionalSerializer',
    'SerializationConfig', 'Compression', 'TypeCode',
    'Transport', 'TransportMessage', 'MemoryTransport', 'MessageChannel',
    'SchemaRegistry', 'serialize', 'deserialize', 'to_srl', 'from_srl',
    
    # Dimensional Foundation (Universal Base Classes)
    'DimLevel', 'DIM_FOUNDATION_LEVEL_NAMES',
    'DimensionalState', 'InvokeResult',
    'Invokable', 'Completable', 'Collapsible',
    'Dimensional', 'AutoDimensional', 'DimensionalInterface',
    'DimensionalValue', 'DimensionalList', 'DimensionalDict',
    'DimensionalFactory', 'register_dimensional', 'create_dimensional',
    'dimensional_decorator', 'generate_interface', 'compose_interfaces',
    'dim', 'dimlist', 'dimdict',
    'foundation_srl', 'invoke_srl',
    
    # Licensing System
    'LicenseTier',
    'PackageInfo',
    'License',
    'LicenseManager',
    'requires_license',
    'check_license',
    
    # Package Registry
    'Package',
    'PackageRegistry',
    'available_packages',
    'all_packages',
    'get_package',
    'upgrade_url',
    
    # Substrates Architecture
    'SubstrateKernel', 'KERNEL',
    'SecureResourceLocator', 'srl', 'invoke',
    'Substrate', 'CompositeSubstrate', 'CustomSubstrate',
    'PrimitiveType', 'KernelPrimitive',
    
    # Substrate Primitives
    'Scalar', 'Vector2D', 'Vector3D', 'Matrix3x3', 'Matrix4x4',
    'RGB', 'RGBA', 'GradientStop',
    'Frequency', 'Amplitude', 'Waveform', 'Duration', 'TimePoint',
    'SubstrateVertex', 'Edge', 'SubstrateTriangle', 'SubstrateMesh',
    'PhysicsBody', 'MaterialProperties', 'MatterState',
    
    # Graphics Substrates
    'PixelSubstrate', 'ColorSubstrate', 'GradientSubstrate',
    'ShaderSubstrate', 'Graphics3DSubstrate',
    
    # Physics Substrates
    'PhysicsSubstrate', 'SolidSubstrate', 'LiquidSubstrate',
    'GasSubstrate', 'DynamicsSubstrate',
    
    # Text Substrates
    'ASCIISubstrate', 'UnicodeSubstrate', 'FontSubstrate',
    'GrammarSubstrate', 'NaturalLanguageSubstrate',
    
    # Media Substrates
    'VoiceSynthesisSubstrate', 'SheetMusicSubstrate', 'ImageSubstrate',
    
    # Theory Substrates
    'ColorTheorySubstrate', 'MusicTheorySubstrate',
    'StatisticsSubstrate', 'GameTheorySubstrate',
    
    # Pattern Substrates
    'FractalSubstrate', 'PatternSubstrate',
    'EdgeFindingSubstrate', 'TilingSubstrate',
    
    # Advanced Substrates
    'QuantumSubstrate', 'GameEngineSubstrate',
]
