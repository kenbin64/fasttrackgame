"""
ButterflyFX Helix - Complete Dimensional Computing Framework

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

# Audio Transport (Layer 3.8) - Low-Latency Audio for Music Collaboration
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
]
