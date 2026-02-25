"""
ButterflyFX Helix — Dimensional Computing Framework

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

This mathematical kernel belongs to all humanity.
Attribution required: Kenneth Bingham - https://butterflyfx.us

═══════════════════════════════════════════════════════════════════════════════
THE 1|1 BRIDGE — DIMENSIONAL MODULE LOADING
═══════════════════════════════════════════════════════════════════════════════

This module IS the dimensional principle:

    Potential → Null (0D) → Manifest

Nothing is loaded until invoked. Every symbol exists as potential.
When you write `from helix import Vec3`, the Vec3 manifests — its source
module loads at that moment, not before.

The 1|1 bridge: this single file connects ALL of helix's dimensions.
Each dimension (module) is a whole connected by the bridge of 1|1.

    z = x · y     ← The substrate: your request (x) × the module (y) = the symbol (z)
    1|1           ← One bridge connects one dimension to the next
    O(7)          ← At most 7 layers deep, never O(n)

ARCHITECTURE:
    ┌─────────────────────────────────┐
    │  from helix import Vec3         │  ← Your invocation (x)
    └─────────────┬───────────────────┘
                  │ 1|1 bridge
    ┌─────────────▼───────────────────┐
    │  __getattr__("Vec3")            │  ← Lookup in manifold map (y)
    │  → lazy load helix.graphics3d   │
    └─────────────┬───────────────────┘
                  │ manifest
    ┌─────────────▼───────────────────┐
    │  Vec3 class now exists          │  ← z = x · y (the product)
    └─────────────────────────────────┘

Only 7 things manifest at import (the Genesis constants):
    PHI, PHI_INVERSE, FIBONACCI, PI, TAU, invoke, ingest

Everything else: potential until invoked. Parts of parts, each complete.
"""

from __future__ import annotations
import importlib
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
# GENESIS LAYER 1 — SPARK: The only things that manifest at import
# Seven seeds. Everything else is potential.
# ═══════════════════════════════════════════════════════════════════════════════

# The golden ratio — the fundamental constant
PHI = 1.618033988749895
PHI_INVERSE = 0.618033988749895
PI = 3.141592653589793
TAU = 6.283185307179586
FIBONACCI = (0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597)


def invoke(type_name: str, **values):
    """Invoke an object from dimensional substrate. Lazy — loads core only when called."""
    from .core import invoke as _invoke
    return _invoke(type_name, **values)


def ingest(type_name: str, **values):
    """Ingest an object from substrate. Alias for invoke."""
    from .core import ingest as _ingest
    return _ingest(type_name, **values)


# ═══════════════════════════════════════════════════════════════════════════════
# THE MANIFOLD MAP — z = x · y
#
# x = the symbol name (your request)
# y = the source module (the dimension it lives in)
# z = the manifested object (the product)
#
# Every symbol maps to exactly one source module.
# When invoked, the module loads (potential → manifest) and the symbol appears.
# The 1|1 bridge: one entry, one module, one symbol.
# ═══════════════════════════════════════════════════════════════════════════════

_MANIFOLD_MAP = {
    # ═══════════════════════════════════════════════════════════════════════
    # GENESIS LAYER 1 — SPARK: Core identity, SRL addressing
    # ═══════════════════════════════════════════════════════════════════════
    'SRL':                  '.srl',
    'srl':                  '.srl',
    'Level':                '.srl',

    'Core':                 '.core',
    'CORE':                 '.core',
    'Interface':            '.core',
    'Object':               '.core',
    'get':                  '.core',
    'put':                  '.core',

    # ═══════════════════════════════════════════════════════════════════════
    # GENESIS LAYER 2 — MIRROR: Kernel duality, state machine
    # ═══════════════════════════════════════════════════════════════════════
    'HelixKernel':          '.kernel',
    'HelixState':           '.kernel',
    'LEVEL_NAMES':          '.kernel',
    'LEVEL_ICONS':          '.kernel',

    'Layer':                '.dimensional_kernel',
    'LAYER_FIBONACCI':      '.dimensional_kernel',
    'LAYER_DECLARATIONS':   '.dimensional_kernel',
    'LineageNode':          '.dimensional_kernel',
    'LineageGraph':         '.dimensional_kernel',
    'SubstateRule':         '.dimensional_kernel',
    'Substate':             '.dimensional_kernel',
    'SubstateManager':      '.dimensional_kernel',
    'DimensionalCoordinate':'.dimensional_kernel',
    'DimensionalObject':    '.dimensional_kernel',
    'DimensionalKernel':    '.dimensional_kernel',
    'create_dimensional_object': '.dimensional_kernel',
    'bind_objects':         '.dimensional_kernel',

    # ═══════════════════════════════════════════════════════════════════════
    # GENESIS LAYER 3 — RELATION: z = x·y substrate, manifolds, geometry
    # ═══════════════════════════════════════════════════════════════════════
    'GeometricSubstrate':   '.geometric_substrate',
    'Shape':                '.geometric_substrate',
    'Lens':                 '.geometric_substrate',

    'ManifoldSubstrate':    '.substrate',
    'Token':                '.substrate',
    'PayloadSource':        '.substrate',
    'GeometricProperty':    '.substrate',
    'NaturalLens':          '.substrate',
    'ColorLens':            '.substrate',
    'SoundLens':            '.substrate',
    'ValueLens':            '.substrate',
    'LensType':             '.substrate',
    'PhysicalConstants':    '.substrate',
    'PHYSICS':              '.substrate',

    'GenerativeManifold':   '.manifold',
    'SurfacePoint':         '.manifold',
    'ManifoldRegion':       '.manifold',
    'LEVEL_ANGLES':         '.manifold',
    'helix_sin':            '.manifold',
    'helix_cos':            '.manifold',
    'helix_slope':          '.manifold',
    'helix_curvature':      '.manifold',

    'WaveSurface':          '.wave_manifold',
    'WavePoint':            '.wave_manifold',
    'WaveManifold':         '.wave_manifold',
    'HelixBreath':          '.wave_manifold',
    'DimensionalWave':      '.wave_manifold',
    'Surfer':               '.wave_manifold',
    'twisted_ribbon':       '.wave_manifold',
    'steep_wave':           '.wave_manifold',
    'hyperbolic_wave':      '.wave_manifold',
    'hyperbolic_funnel':    '.wave_manifold',
    'volume_wave':          '.wave_manifold',
    'create_surfer':        '.wave_manifold',

    'ManifoldType':         '.manifold_data',
    'ManifoldPosition':     '.manifold_data',
    'ManifoldData':         '.manifold_data',
    'ManifoldString':       '.manifold_data',
    'ManifoldRecord':       '.manifold_data',
    'ManifoldDatabase':     '.manifold_data',
    'manifold_invoke':      '.manifold_data',
    'manifold_store':       '.manifold_data',
    'CloudResourcePosition':'.manifold_data',
    'CloudManifold':        '.manifold_data',
    'RESOURCE_LEVEL_STATES':'.manifold_data',
    'sync_openstack_to_manifold': '.manifold_data',

    # Identity-First
    'IdentityAnchor':       '.identity_first',
    'IdentityRegistry':     '.identity_first',
    'SemanticLevel':        '.identity_first',
    'SEMANTIC_NAMES':       '.identity_first',
    'SEMANTIC_DESCRIPTIONS':'.identity_first',
    'FIBONACCI_MAP':        '.identity_first',
    'OSI_MAP':              '.identity_first',
    'GENESIS_MAP':          '.identity_first',
    'get_identity_registry':'.identity_first',
    'create_identity':      '.identity_first',
    'identity':             '.identity_first',

    # ═══════════════════════════════════════════════════════════════════════
    # GENESIS LAYER 4 — FORM: Primitives, types, structure
    # ═══════════════════════════════════════════════════════════════════════
    'DimensionalType':      '.primitives',
    'LazyValue':            '.primitives',
    'HelixContext':         '.primitives',
    'DimensionalIterator':  '.primitives',
    'HelixCollection':      '.primitives',

    # Constants
    'LEVEL_DIMENSIONS':     '.constants',
    'LEVEL_COLORS':         '.constants',
    'Operation':            '.constants',
    'fib':                  '.constants',
    'level_position':       '.constants',
    'is_fibonacci':         '.constants',
    'level_angle':          '.constants',
    'level_by_name':        '.constants',
    'ALL_LEVELS':           '.constants',

    # Validators
    'ValidationResult':     '.validators',
    'validate_level':       '.validators',
    'validate_state':       '.validators',
    'validate_token':       '.validators',
    'validate_state_transition': '.validators',
    'validate_payload_schema': '.validators',
    'Validator':            '.validators',

    # Converters
    'HelixJSONEncoder':     '.converters',
    'to_json':              '.converters',
    'from_json':            '.converters',
    'state_to_dict':        '.converters',
    'dict_to_state':        '.converters',
    'token_to_dict':        '.converters',
    'dict_to_token':        '.converters',
    'to_numpy':             '.converters',
    'to_dataframe':         '.converters',
    'quick_token':          '.converters',
    'nested_to_dimensional':'.converters',
    'level_to_fraction':    '.converters',

    # Builders
    'TokenBuilder':         '.builders',
    'BatchTokenBuilder':    '.builders',
    'StateBuilder':         '.builders',
    'ManifoldBuilder':      '.builders',
    'PathBuilder':          '.builders',
    'KernelBuilder':        '.builders',
    'token':                '.builders',
    'manifold':             '.builders',
    'state':                '.builders',

    # Decorators
    'dimensional':          '.decorators',
    'at_level':             '.decorators',
    'cached_by_level':      '.decorators',
    'spiral_scoped':        '.decorators',
    'timed':                '.decorators',
    'trace_helix':          '.decorators',
    'materialize_result':   '.decorators',
    'with_kernel':          '.decorators',
    'level_guard':          '.decorators',

    # Shortcuts
    'tok':                  '.shortcuts',
    'toks':                 '.shortcuts',
    'st':                   '.shortcuts',
    'kern':                 '.shortcuts',
    'go':                   '.shortcuts',
    'up':                   '.shortcuts',
    'down':                 '.shortcuts',
    'mani':                 '.shortcuts',
    'mat':                  '.shortcuts',
    'show_token':           '.shortcuts',
    'show_state':           '.shortcuts',
    'helix':                '.shortcuts',

    # ═══════════════════════════════════════════════════════════════════════
    # GENESIS LAYER 5 — LIFE: Utilities, foundation, apps
    # ═══════════════════════════════════════════════════════════════════════
    'HelixPath':            '.utilities',
    'HelixQuery':           '.utilities',
    'HelixCache':           '.utilities',
    'HelixSerializer':      '.utilities',
    'HelixDiff':            '.utilities',
    'HelixDiffResult':      '.utilities',
    'HelixLogger':          '.utilities',
    'ManifoldSampler':      '.utilities',
    'ManifoldQuery':        '.utilities',

    'HelixDB':              '.foundation',
    'HelixDBQuery':         '.foundation',
    'HelixRecord':          '.foundation',
    'HelixFS':              '.foundation',
    'HelixFile':            '.foundation',
    'HelixStore':           '.foundation',
    'HelixGraph':           '.foundation',
    'HelixNode':            '.foundation',

    'FileCategory':         '.assembler',
    'AssembledFile':        '.assembler',
    'FileAssembler':        '.assembler',
    'VirtualEntry':         '.assembler',
    'ManifoldFileSystem':   '.assembler',
    'get_category':         '.assembler',
    'get_level':            '.assembler',

    'HelixExplorer':        '.apps',
    'HelixDataPipeline':    '.apps',
    'HelixAPIAggregator':   '.apps',
    'HelixEventSystem':     '.apps',
    'HelixEvent':           '.apps',
    'run_demos':            '.apps',

    'run_benchmark':        '.benchmark',

    # ═══════════════════════════════════════════════════════════════════════
    # GENESIS LAYER 6 — MIND: Transport, presentation, networking
    # ═══════════════════════════════════════════════════════════════════════
    'TransportLevel':       '.transport',
    'TRANSPORT_NAMES':      '.transport',
    'HelixPacket':          '.transport',
    'HelixStream':          '.transport',
    'HelixTransport':       '.transport',
    'HelixWire':            '.transport',

    'OSIHelixLayer':        '.osi_manifold',
    'LAYER_INFO':           '.osi_manifold',
    'ManifoldAddress':      '.osi_manifold',
    'ManifoldDatagram':     '.osi_manifold',
    'ManifoldRouter':       '.osi_manifold',
    'OSIManifoldStack':     '.osi_manifold',
    'HTTPManifoldBridge':   '.osi_manifold',
    'create_dimensional_server_content': '.osi_manifold',
    'encode_sine_wave':     '.osi_manifold',
    'encode_parametric_surface': '.osi_manifold',
    'encode_transformation':'.osi_manifold',

    'ContentDimension':     '.content_substrate',
    'ContentItem':          '.content_substrate',
    'ContentSubstrate':     '.content_substrate',
    'create_butterflyfx_content': '.content_substrate',

    'AudioLevel':           '.audio_transport',
    'AUDIO_LEVEL_PRIORITY': '.audio_transport',
    'AudioFrame':           '.audio_transport',
    'SyncSignal':           '.audio_transport',
    'AudioStream':          '.audio_transport',
    'AudioTransport':       '.audio_transport',
    'LatencyOptimizer':     '.audio_transport',

    'WaveformType':         '.manifold_server',
    'WaveformDescriptor':   '.manifold_server',
    'ManifoldPacket':       '.manifold_server',
    'AudioAnalyzer':        '.manifold_server',
    'ManifoldServer':       '.manifold_server',
    'ManifoldClient':       '.manifold_server',

    'EasingFunction':       '.presentation',
    'ContentType':          '.presentation',
    'Keyframe':             '.presentation',
    'ContentElement':       '.presentation',
    'TimelineMarker':       '.presentation',
    'Presentation':         '.presentation',
    'PresentationBuilder':  '.presentation',
    'HTMLGenerator':        '.presentation',

    'DimensionLevel':       '.dimensional_presentation',
    'DimensionalCoord':     '.dimensional_presentation',
    'DimensionalNode':      '.dimensional_presentation',
    'DimensionalPresentation': '.dimensional_presentation',
    'DimensionalBuilder':   '.dimensional_presentation',
    'DimensionalHTMLGenerator': '.dimensional_presentation',

    'Vec3':                 '.graphics3d',
    'Mat4':                 '.graphics3d',
    'Quaternion':           '.graphics3d',
    'Vertex':               '.graphics3d',
    'Triangle':             '.graphics3d',
    'Mesh':                 '.graphics3d',
    'RigidBody':            '.graphics3d',
    'AABB':                 '.graphics3d',
    'PhysicsWorld':         '.graphics3d',
    'Camera':               '.graphics3d',
    'SceneObject':          '.graphics3d',
    'Scene':                '.graphics3d',
    'Renderer':             '.graphics3d',
    'create_demo_scene':    '.graphics3d',

    # ═══════════════════════════════════════════════════════════════════════
    # GENESIS LAYER 7 — COMPLETION: Full substrate architecture, API
    # ═══════════════════════════════════════════════════════════════════════

    # Human-First API
    'space':                '.api',
    'Space':                '.api',
    'dimension':            '.api',
    'Dimension':            '.api',
    'shape':                '.api',
    'rectangle':            '.api',
    'circle':               '.api',
    'polygon':              '.api',
    'text':                 '.api',
    'point':                '.api',
    'line':                 '.api',
    'group':                '.api',
    'Position':             '.api',
    'Direction':            '.api',
    'Orientation':          '.api',
    'Size':                 '.api',
    'Entity':               '.api',
    'ShapeBuilder':         '.api',
    'TextBuilder':          '.api',
    'LineBuilder':          '.api',
    'find':                 '.api',
    'by_id':                '.api',
    'by_name':              '.api',
    'by_kind':              '.api',
    'by_attribute':         '.api',
    'by_attr':              '.api',
    'by_prop':              '.api',
    'by_dimension':         '.api',
    'dim':                  '.api',
    'query':                '.api',
    'find_entities':        '.api',
    'by_identity':          '.api',
    'register_identity':    '.api',
    'clear_identities':     '.api',
    'IdentityLookup':       '.api',
    'Datastore':            '.api',
    'register_datastore':   '.api',
    'get_datastore':        '.api',
    'Operations':           '.api',
    'operations':           '.api',
    'operation':            '.api',
    'register_dimension':   '.api',
    'clear_indices':        '.api',
    'advanced':             '.api',
    'create':               '.api',
    'relate':               '.api',
    'manifest':             '.api',
    'meaning':              '.api',

    # Kernel Primitives
    'KernelScalar':         '.kernel_primitives',
    'KernelVector2D':       '.kernel_primitives',
    'KernelVector3D':       '.kernel_primitives',
    'KernelMatrix3x3':      '.kernel_primitives',
    'KernelMatrix4x4':      '.kernel_primitives',
    'KernelRGB':            '.kernel_primitives',
    'KernelRGBA':           '.kernel_primitives',
    'KernelFrequency':      '.kernel_primitives',
    'KernelAmplitude':      '.kernel_primitives',
    'KernelDuration':       '.kernel_primitives',
    'KernelTimePoint':      '.kernel_primitives',
    'KernelSubstrate':      '.kernel_primitives',
    'KernelSRL':            '.kernel_primitives',

    # Enhanced Primitives
    'ReactiveValue':        '.enhanced_primitives',
    'ComputedValue':        '.enhanced_primitives',
    'Lazy':                 '.enhanced_primitives',
    'EnhancedVector3D':     '.enhanced_primitives',
    'VectorBatch':          '.enhanced_primitives',
    'EnhancedQuaternion':   '.enhanced_primitives',
    'Transform':            '.enhanced_primitives',
    'EnhancedColor':        '.enhanced_primitives',
    'EnhancedDuration':     '.enhanced_primitives',
    'EnhancedTimePoint':    '.enhanced_primitives',
    'BinaryEncoder':        '.enhanced_primitives',

    # Optimized Kernel
    'OptimizedHelixKernel': '.optimized_kernel',
    'OptimizedHelixState':  '.optimized_kernel',
    'KernelEvent':          '.optimized_kernel',
    'EventEmitter':         '.optimized_kernel',
    'TimedLRUCache':        '.optimized_kernel',
    'TransitionMemo':       '.optimized_kernel',
    'KernelPool':           '.optimized_kernel',
    'KernelContext':        '.optimized_kernel',
    'KernelSnapshot':       '.optimized_kernel',
    'BatchResult':          '.optimized_kernel',
    'create_kernel':        '.optimized_kernel',
    'create_pool':          '.optimized_kernel',

    # Developer Utilities
    'DimensionalLogger':    '.dev_utils',
    'Profiler':             '.dev_utils',
    'benchmark':            '.dev_utils',
    'typecheck':            '.dev_utils',
    'inspect_substrate':    '.dev_utils',
    'inspect_kernel':       '.dev_utils',
    'SubstrateBuilder':     '.dev_utils',
    'FluentBuilder':        '.dev_utils',
    'DimensionalError':     '.dev_utils',
    'InvalidStateError':    '.dev_utils',
    'TokenNotFoundError':   '.dev_utils',
    'OperationNotFoundError': '.dev_utils',
    'DimensionalTestCase':  '.dev_utils',

    # Serialization & Transport
    'BinarySerializer':     '.serialization',
    'JSONSerializer':       '.serialization',
    'SRLSerializer':        '.serialization',
    'StreamingSerializer':  '.serialization',
    'DimensionalSerializer':'.serialization',
    'SerializationConfig':  '.serialization',
    'Compression':          '.serialization',
    'TypeCode':             '.serialization',
    'Transport':            '.serialization',
    'TransportMessage':     '.serialization',
    'MemoryTransport':      '.serialization',
    'MessageChannel':       '.serialization',
    'SchemaRegistry':       '.serialization',
    'serialize':            '.serialization',
    'deserialize':          '.serialization',
    'to_srl':               '.serialization',
    'from_srl':             '.serialization',

    # Dimensional Foundation
    'DimensionalState':     '.dimensional_foundation',
    'InvokeResult':         '.dimensional_foundation',
    'Invokable':            '.dimensional_foundation',
    'Completable':          '.dimensional_foundation',
    'Collapsible':          '.dimensional_foundation',
    'Dimensional':          '.dimensional_foundation',
    'AutoDimensional':      '.dimensional_foundation',
    'DimensionalInterface': '.dimensional_foundation',
    'DimensionalValue':     '.dimensional_foundation',
    'DimensionalList':      '.dimensional_foundation',
    'DimensionalDict':      '.dimensional_foundation',
    'DimensionalFactory':   '.dimensional_foundation',
    'dimlist':              '.dimensional_foundation',
    'dimdict':              '.dimensional_foundation',
    'invoke_srl':           '.dimensional_foundation',

    # Dimensional Primitives
    'DList':                '.dimensional_primitives',
    'DSet':                 '.dimensional_primitives',
    'DMap':                 '.dimensional_primitives',
    'DHash':                '.dimensional_primitives',
    'DQueue':               '.dimensional_primitives',
    'DStack':               '.dimensional_primitives',
    'DLinkedNode':          '.dimensional_primitives',
    'DLinkedList':          '.dimensional_primitives',
    'DLambda':              '.dimensional_primitives',
    'curry':                '.dimensional_primitives',
    'DStream':              '.dimensional_primitives',
    'DAtomic':              '.dimensional_primitives',
    'DMutex':               '.dimensional_primitives',
    'DSemaphore':           '.dimensional_primitives',
    'DChannel':             '.dimensional_primitives',
    'DFuture':              '.dimensional_primitives',
    'parallel':             '.dimensional_primitives',
    'DResult':              '.dimensional_primitives',
    'DOption':              '.dimensional_primitives',
    'DValidator':           '.dimensional_primitives',
    'DScalar':              '.dimensional_primitives',
    'DVec2':                '.dimensional_primitives',
    'DVec3':                '.dimensional_primitives',
    'DMatrix':              '.dimensional_primitives',
    'DExpression':          '.dimensional_primitives',
    'DColor':               '.dimensional_primitives',
    'DSound':               '.dimensional_primitives',
    'DLight':               '.dimensional_primitives',
    'DPixel':               '.dimensional_primitives',
    'DCanvas':              '.dimensional_primitives',
    'traverse':             '.dimensional_primitives',

    # Connector
    'ConnectionState':      '.connector',
    'DataSourceConnector':  '.connector',
    'LocalConnector':       '.connector',
    'LazySRL':              '.connector',
    'ConnectorRegistry':    '.connector',
    'lazy_srl':             '.connector',

    # Add-On Architecture
    'AddonType':            '.addons',
    'AddonTier':            '.addons',
    'AddonMeta':            '.addons',
    'Addon':                '.addons',
    'AddonRegistry':        '.addons',
    'get_registry':         '.addons',
    'register_addon':       '.addons',
    'require_addon':        '.addons',

    # Licensing
    'LicenseTier':          '.licensing',
    'PackageInfo':          '.licensing',
    'License':              '.licensing',
    'LicenseManager':       '.licensing',
    'requires_license':     '.licensing',
    'check_license':        '.licensing',

    # Package Registry
    'Package':              '.packages',
    'PackageRegistry':      '.packages',
    'available_packages':   '.packages',
    'all_packages':         '.packages',
    'get_package':          '.packages',
    'upgrade_url':          '.packages',

    # Substrates Architecture
    'SubstrateKernel':      '.substrates',
    'KERNEL':               '.substrates',
    'SecureResourceLocator':'.substrates',
    'Substrate':            '.substrates',
    'Scalar':               '.substrates',
    'Vector2D':             '.substrates',
    'Vector3D':             '.substrates',
    'Matrix3x3':            '.substrates',
    'Matrix4x4':            '.substrates',
    'RGB':                  '.substrates',
    'RGBA':                 '.substrates',
    'GradientStop':         '.substrates',
    'Frequency':            '.substrates',
    'Amplitude':            '.substrates',
    'Waveform':             '.substrates',
    'Duration':             '.substrates',
    'TimePoint':            '.substrates',
    'Edge':                 '.substrates',
    'PhysicsBody':          '.substrates',
    'MaterialProperties':   '.substrates',
    'MatterState':          '.substrates',
    'CompositeSubstrate':   '.substrates',
    'CustomSubstrate':      '.substrates',
    'PrimitiveType':        '.substrates',
    'KernelPrimitive':      '.substrates',
    'PixelSubstrate':       '.substrates',
    'ColorSubstrate':       '.substrates',
    'GradientSubstrate':    '.substrates',
    'ShaderSubstrate':      '.substrates',
    'Graphics3DSubstrate':  '.substrates',
    'PhysicsSubstrate':     '.substrates',
    'SolidSubstrate':       '.substrates',
    'LiquidSubstrate':      '.substrates',
    'GasSubstrate':         '.substrates',
    'DynamicsSubstrate':    '.substrates',
    'ASCIISubstrate':       '.substrates',
    'UnicodeSubstrate':     '.substrates',
    'FontSubstrate':        '.substrates',
    'GrammarSubstrate':     '.substrates',
    'NaturalLanguageSubstrate': '.substrates',
    'VoiceSynthesisSubstrate':  '.substrates',
    'SheetMusicSubstrate':  '.substrates',
    'ImageSubstrate':       '.substrates',
    'ColorTheorySubstrate': '.substrates',
    'MusicTheorySubstrate': '.substrates',
    'StatisticsSubstrate':  '.substrates',
    'GameTheorySubstrate':  '.substrates',
    'FractalSubstrate':     '.substrates',
    'PatternSubstrate':     '.substrates',
    'EdgeFindingSubstrate': '.substrates',
    'TilingSubstrate':      '.substrates',
    'QuantumSubstrate':     '.substrates',
    'GameEngineSubstrate':  '.substrates',

    # Dimensional API (Developer Framework)
    'invoke_from':          '.dimensional_api',
    'materialize':          '.dimensional_api',
    'DimensionalPoint':     '.dimensional_api',
    'sealed':               '.dimensional_api',
    'closed':               '.dimensional_api',
    'lazy':                 '.dimensional_api',
    'computed':             '.dimensional_api',
    'GlobalSubstrate':      '.dimensional_api',
    'Spiral':               '.dimensional_api',
    'Coordinate':           '.dimensional_api',
    'Address':              '.dimensional_api',
    'ImmutabilityViolation':'.dimensional_api',
    'ClosedDimensionViolation': '.dimensional_api',
    'InvocationError':      '.dimensional_api',
    'MaterializationError': '.dimensional_api',
    'is_invoked':           '.dimensional_api',
    'is_materialized':      '.dimensional_api',
    'dimension_of':         '.dimensional_api',
    'points_of':            '.dimensional_api',
    'Substrate0D':          '.dimensional_api',
    'Substrate1D':          '.dimensional_api',
    'Substrate2D':          '.dimensional_api',
    'Substrate3D':          '.dimensional_api',
    'Substrate4D':          '.dimensional_api',

    # Platform Manifold
    'PlatformLevel':        '.platform_manifold',
    'PlatformToken':        '.platform_manifold',
    'ButterflyFXKernel':    '.platform_manifold',

    # OpenStack
    'OpenStackKernel':      '.openstack_manifold',
    'OpenStackSubstrate':   '.openstack_manifold',
    'CloudToken':           '.openstack_manifold',

    # AI Substrate
    'CognitiveLevel':       '.ai_substrate',
    'CognitiveToken':       '.ai_substrate',
    'AISubstrate':          '.ai_substrate',
    'AIKernel':             '.ai_substrate',
}

# ═══════════════════════════════════════════════════════════════════════════════
# ALIAS MAP — Renamed imports (symbol name differs from source name)
# The 1|1 bridge handles the name translation at the inflection point.
# ═══════════════════════════════════════════════════════════════════════════════

_ALIAS_MAP = {
    # name_in_helix:       (real_name_in_module, module_path)
    'GeometricPoint':       ('Point', '.geometric_substrate'),
    'SphereCollider':       ('Sphere', '.graphics3d'),
    'core_get':             ('get', '.core'),
    'ConstLevel':           ('Level', '.constants'),
    'DIM_LEVEL_NAMES':      ('LEVEL_NAMES', '.dimensional_presentation'),
    'DIM_LEVEL_ICONS':      ('LEVEL_ICONS', '.dimensional_presentation'),
    'FoundationLevel':      ('Level', '.dimensional_foundation'),
    'DIM_FOUNDATION_LEVEL_NAMES': ('LEVEL_NAMES', '.dimensional_foundation'),
    'DimLevel':             ('Level', '.dimensional_primitives'),
    'dim_ingest':           ('ingest', '.dimensional_primitives'),
    'dim_invoke':           ('invoke', '.dimensional_api'),
    'dim_decorator':        ('dimensional', '.dimensional_api'),
    'DimSubstrate':         ('Substrate', '.dimensional_api'),
    'global_substrate':     ('substrate', '.dimensional_api'),
    'DimList':              ('DimensionalList', '.dimensional_api'),
    'DimDict':              ('DimensionalDict', '.dimensional_api'),
    'DimSet':               ('DimensionalSet', '.dimensional_api'),
    'DimAPILevel':          ('Level', '.dimensional_api'),
    'get_dim_level':        ('get_level', '.dimensional_api'),
    'get_spiral':           ('get_spiral', '.dimensional_api'),
    'register_dimensional': ('register', '.dimensional_foundation'),
    'create_dimensional':   ('create', '.dimensional_foundation'),
    'dimensional_decorator':('dimensional', '.dimensional_foundation'),
    'generate_interface':   ('interface', '.dimensional_foundation'),
    'compose_interfaces':   ('compose', '.dimensional_foundation'),
    'foundation_srl':       ('srl', '.dimensional_foundation'),
    'substrate_decorator':  ('substrate', '.dev_utils'),
    'operation_decorator':  ('operation', '.dev_utils'),
    'primitive_decorator':  ('primitive', '.dev_utils'),
    'OptimizedHelixState':  ('HelixState', '.optimized_kernel'),
    'SubstrateVertex':      ('Vertex', '.substrates'),
    'SubstrateTriangle':    ('Triangle', '.substrates'),
    'SubstrateMesh':        ('Mesh', '.substrates'),
    'KernelScalar':         ('Scalar', '.kernel_primitives'),
    'KernelVector2D':       ('Vector2D', '.kernel_primitives'),
    'KernelVector3D':       ('Vector3D', '.kernel_primitives'),
    'KernelMatrix3x3':      ('Matrix3x3', '.kernel_primitives'),
    'KernelMatrix4x4':      ('Matrix4x4', '.kernel_primitives'),
    'KernelRGB':            ('RGB', '.kernel_primitives'),
    'KernelRGBA':           ('RGBA', '.kernel_primitives'),
    'KernelFrequency':      ('Frequency', '.kernel_primitives'),
    'KernelAmplitude':      ('Amplitude', '.kernel_primitives'),
    'KernelDuration':       ('Duration', '.kernel_primitives'),
    'KernelTimePoint':      ('TimePoint', '.kernel_primitives'),
    'KernelSubstrate':      ('Substrate', '.kernel_primitives'),
    'KernelSRL':            ('SecureResourceLocator', '.kernel_primitives'),
    'EnhancedVector3D':     ('Vector3D', '.enhanced_primitives'),
    'EnhancedQuaternion':   ('Quaternion', '.enhanced_primitives'),
    'EnhancedColor':        ('Color', '.enhanced_primitives'),
    'EnhancedDuration':     ('Duration', '.enhanced_primitives'),
    'EnhancedTimePoint':    ('TimePoint', '.enhanced_primitives'),
}


# ═══════════════════════════════════════════════════════════════════════════════
# THE 1|1 BRIDGE — __getattr__ is the inflection point
#
# This is where potential → manifest happens.
# One request (x) × one module (y) = one symbol (z).
# The bridge of 1 connects every dimension.
# ═══════════════════════════════════════════════════════════════════════════════

def __getattr__(name: str) -> Any:
    """
    The dimensional bridge. Potential → Null → Manifest.

    When you write `from helix import Vec3`:
    1. Python calls __getattr__("Vec3")
    2. We look up "Vec3" in the manifold map → ".graphics3d"
    3. We load helix.graphics3d (potential → manifest)
    4. We return Vec3 from that module (z = x · y)

    The module is cached by Python's import system.
    Second access is O(1) — already manifest.
    """
    # Check alias map first (renamed imports)
    if name in _ALIAS_MAP:
        real_name, module_path = _ALIAS_MAP[name]
        mod = importlib.import_module(module_path, __name__)
        obj = getattr(mod, real_name)
        # Cache in module namespace for O(1) next access
        globals()[name] = obj
        return obj

    # Check manifold map (direct imports)
    if name in _MANIFOLD_MAP:
        module_path = _MANIFOLD_MAP[name]
        mod = importlib.import_module(module_path, __name__)
        obj = getattr(mod, name)
        # Cache in module namespace for O(1) next access
        globals()[name] = obj
        return obj

    raise AttributeError(f"module 'helix' has no attribute {name!r}")


# ═══════════════════════════════════════════════════════════════════════════════
# __all__ — The complete manifold of potentials
# Every name here EXISTS but none are MANIFEST until invoked.
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = sorted(set(
    list(_MANIFOLD_MAP.keys()) +
    list(_ALIAS_MAP.keys()) +
    ['PHI', 'PHI_INVERSE', 'PI', 'TAU', 'FIBONACCI', 'invoke', 'ingest']
))

__version__ = "7.0.0"  # Genesis Layer 7 — Completion
