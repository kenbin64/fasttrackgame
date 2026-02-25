# Helix Directory — Complete Python File Inventory

> Generated from full analysis of 50 Python files, 47,860 total lines.

## Summary Dashboard

| Metric | Count |
|--------|-------|
| Total files | 50 |
| Total lines | 47,860 |
| Files using **Genesis 1-7** model | 2 |
| Files using **deprecated 0-6** model | 25+ |
| Files model-agnostic | ~20 |
| Duplicate `Level` enum definitions | **8+** |
| Duplicate `Vector3D` definitions | **4** |
| Duplicate `Core` class definitions | **2** |
| Duplicate `SRL` class definitions | **2** |
| Files with `__main__` demo blocks | 5+ |
| Files with `TODO` markers | 3+ |

---

## Layer Model Legend

| Symbol | Meaning |
|--------|---------|
| ✅ 1-7 | Uses Genesis layers (Spark=1..Completion=7) — **canonical** |
| ❌ 0-6 | Uses deprecated levels (Potential=0..Whole=6) |
| ⚠️ Mixed | Docstring says Genesis, code uses 0-6 |
| ➖ N/A | Not tied to a specific layer model |

---

## Complete File Inventory

### 1. KERNEL & STATE MACHINE

| # | File | Lines | Model | Purpose | Key Classes / Functions | Issues |
|---|------|-------|-------|---------|------------------------|--------|
| 1 | `kernel.py` | 697 | ✅ 1-7 | **Canonical helix state machine.** Defines HelixState, HelixKernel with invoke/spiral_up/spiral_down/collapse/lift/project. Golden ratio constants, layer metadata. | `HelixState`, `HelixKernel`, `SubstrateProtocol`, `LAYER_NAMES`, `LAYER_FIBONACCI`, `PHI` | ~100 lines of deprecated 0-6 LEVEL_NAMES/LEVEL_ICONS kept for backward compat. `verify_invariants()` is a stub. |
| 2 | `dimensional_kernel.py` | 1112 | ✅ 1-7 | **Alternative kernel** with numpy. DimensionalObject with identity/intention vectors, lineage tracking (DAG), substate system. `Layer` enum (SPARK=1..COMPLETION=7). | `Layer`, `LineageNode`, `LineageGraph`, `SubstateManager`, `DimensionalObject`, `DimensionalKernel` | **Duplicates kernel.py** significantly. Heavy numpy dependency. `_id` based on `time.time()` (not unique under concurrency). |
| 3 | `optimized_kernel.py` | 1002 | ❌ 0-6 | Performance-focused kernel variant. Uses tuples instead of dicts for LEVEL_NAMES. TimedLRU cache, event emitter, batch operations, kernel pool, snapshots. | `HelixState`, `TimedLRUCache`, `TransitionMemo`, `OptimizedHelixKernel`, `KernelPool`, `KernelContext` | **Third kernel implementation.** Uses 0-6, not migrated. Duplicates HelixState. |
| 4 | `core.py` | 525 | ❌ 0-6 | Singleton `Core` managing kernel communication. `Interface`/`Object` with magic `__getattr__` for `car.engine.hp` syntax. SRL addressing. | `Core` (singleton), `Interface`/`Object`, `ingest()`, `invoke()`, `get()`, `put()` | GENESIS_LAYERS defined but unused. Interface recursion could be infinite. No SRL validation. Not thread-safe. |

### 2. SUBSTRATE & MANIFOLD

| # | File | Lines | Model | Purpose | Key Classes / Functions | Issues |
|---|------|-------|-------|---------|------------------------|--------|
| 5 | `substrate.py` | 1238 | ❌ 0-6 | Token model, manifold substrate, lens system (color/sound/value from geometry), ingestion/extraction. | `Token`, `ManifoldSubstrate`, `ColorLens`, `SoundLens`, `ValueLens`, `NaturalLens`, `PayloadSource`, `GeometricProperty` | Level param validated as 0-6 only. Bare `except:` in `ingest()`. File does too many things (lenses + tokens + substrate). |
| 6 | `manifold.py` | 1188 | ⚠️ Mixed | Generative manifold — mathematical surface producing data types. SurfacePoint with Frenet frame, curvature. Multiple manifold types (Identity, Runtime, Scaling, Semantic, Completion). | `SurfacePoint`, `GenerativeManifold`, `ManifoldRegion`, `IdentityManifold`, `RuntimeManifold`, `SemanticManifold`, `CompletionManifold` | Docstring says Genesis 1-7 but `at()` and ManifoldRegion validate 0-6. Convenience funcs create new instances each call (wasteful). DIMENSIONAL_MANIFOLDS uses 0-6 keys. |
| 7 | `manifold_data.py` | 1003 | ❌ 0-6 | "Data without storage" — values exist as manifold geometry. ManifoldPosition, ManifoldString, ManifoldRecord, ManifoldDatabase. Also includes CloudManifold / CloudResourcePosition. | `ManifoldPosition`, `ManifoldData`, `ManifoldString`, `ManifoldRecord`, `ManifoldDatabase`, `CloudManifold`, `CloudResourcePosition` | Levels 0-6 in CloudResourcePosition. `ManifoldRecord.create()` hashes strings via MD5 (not round-trippable). Large `if __name__` demo block. CloudManifold overlaps with openstack_manifold.py. |
| 8 | `manifold_server.py` | 634 | ➖ N/A | "Transmit math, not bits" — audio as waveform equations. Server broadcasts mathematical descriptions; clients synthesize locally. | `WaveformDescriptor`, `ManifoldPacket`, `AudioAnalyzer`, `ManifoldServer`, `ManifoldClient` | Audio analysis is simplified (no FFT). Overlaps conceptually with audio_transport.py. Good bounds-checking on deserialization. |
| 9 | `geometric_substrate.py` | 668 | ➖ N/A | Geometric primitives substrate: points, shapes, lenses. | `Lens`, `GeometricProperty`, `Shape`, `Point`, `GeometricSubstrate` | Overlaps with kernel_primitives.py and enhanced_primitives.py for vector/point types. |
| 10 | `content_substrate.py` | 667 | ❌ 0-6 | Content (text, media, data) organized by dimensional level. Integrates with OSI manifold for networking. | `ContentDimension` (IntEnum 0-6), `ContentItem`, `ContentSubstrate`, `create_butterflyfx_content()` | Uses 0-6 model via ContentDimension. |
| 11 | `ai_substrate.py` | 914 | ❌ 0-6 | AI/LLM integration substrate. CognitiveLevel enum, AI backends (Ollama, OpenAI, Mock), conversation management. | `CognitiveLevel` (0-6), `CognitiveToken`, `Message`, `Conversation`, `AIBackend`, `OllamaBackend`, `OpenAIBackend`, `MockBackend`, `AISubstrate` | Uses 0-6 levels. API keys may be in code/env vars — review security. |
| 12 | `substrates.py` | 2357 | ➖ N/A | **Mega-file.** Re-implements kernel_primitives (Scalar, Vector2D/3D, RGB, etc.) plus domain substrates: Pixel, Color, Gradient, Shader, Graphics3D, Physics, ASCII, Unicode, Font. | `Scalar`, `Vector2D`, `Vector3D`, `RGB`, `RGBA`, `Frequency`, `Amplitude`, `Substrate`, `PixelSubstrate`, `ColorSubstrate`, `GradientSubstrate`, `ShaderSubstrate`, `Mesh`, `Graphics3DSubstrate`, `PhysicsSubstrate`, `ASCIISubstrate`, `UnicodeSubstrate`, `FontSubstrate` | **Massive duplication** of kernel_primitives.py and enhanced_primitives.py. Same classes defined again. Should import, not copy. |

### 3. PRIMITIVES & TYPES

| # | File | Lines | Model | Purpose | Key Classes / Functions | Issues |
|---|------|-------|-------|---------|------------------------|--------|
| 13 | `kernel_primitives.py` | 861 | ➖ N/A | "Free kernel" math primitives: Scalar, Vector2D/3D, Matrix3x3/4x4, RGB/RGBA, Frequency, Amplitude, Duration, TimePoint. Also defines Substrate ABC and SecureResourceLocator (SRL singleton). | `Scalar`, `Vector2D`, `Vector3D`, `Matrix3x3`, `Matrix4x4`, `RGB`, `RGBA`, `Frequency`, `Amplitude`, `Duration`, `TimePoint`, `Substrate`, `SecureResourceLocator`, `SRL` | SRL singleton conflicts with srl.py's SRL class. Vector3D duplicated in enhanced_primitives.py, graphics3d.py, substrates.py. |
| 14 | `primitives.py` | 717 | ❌ 0-6 | Re-exports from kernel.py and substrate.py. Adds DimensionalType[T], LazyValue[T], HelixContext. | `DimensionalType`, `LazyValue`, `HelixContext` | Imports LEVEL_NAMES (0-6). Thin re-export layer, could be merged into __init__.py. |
| 15 | `enhanced_primitives.py` | 1282 | ➖ N/A | Advanced building blocks: reactive bindings, vectors, quaternions, SIMD-style batch ops. | `ReactiveValue[T]`, `ComputedValue[T]`, `Lazy[T]`, `Vector3D` (frozen,slots), `VectorBatch`, `Quaternion` | Vector3D duplicates kernel_primitives.py version. Quaternion duplicates graphics3d.py version. |
| 16 | `dimensional_primitives.py` | 1677 | ❌ 0-6 | "Atomic building blocks" — dimensional ops, collections (DList, DSet, DMap, DHash, DQueue, DStack, DLinkedList), functional (DLambda, DStream), concurrency, validation, math, sensory. | `Level` (enum 0-6), `Dimension`, `DList`, `DSet`, `DMap`, `DHash`, `DQueue`, `DStack`, `DLinkedList`, `DLambda`, `DStream`, `ingest()`, `traverse()`, `curry()` | **Yet another Level enum duplicate.** `ingest()` duplicates core.py. Largest primitives file — could be split. |

### 4. FOUNDATION & INFRASTRUCTURE

| # | File | Lines | Model | Purpose | Key Classes / Functions | Issues |
|---|------|-------|-------|---------|------------------------|--------|
| 17 | `foundation.py` | 758 | ❌ 0-6 | Reusable components: HelixDB (in-memory DB with query builder), HelixFS (virtual filesystem), HelixStore (key-value), HelixGraph (graph with level-based nodes). | `HelixDB`, `HelixDBQuery`, `HelixFS`, `HelixStore`, `HelixGraph` | All level references 0-6. HelixDB.invoke_level iterates all records (not O(1)). HelixFS untested. |
| 18 | `dimensional_foundation.py` | 1149 | ❌ 0-6 | Base classes for universal invoke pattern. Generic `Dimensional[T]` with invoke/complete/collapse/spiral_up/spiral_down. Protocols. | `Level` (enum 0-6), `DimensionalState`, `InvokeResult[T]`, `Invokable`/`Completable`/`Collapsible` (protocols), `Dimensional[T]`, `DimensionalInterface` | Yet another Level enum. Not Genesis. Heavyweight RLock per instance. |
| 19 | `constants.py` | 401 | ❌ 0-6 | Standard constants: PHI, Fibonacci, Level IntEnum 0-6, level metadata dicts, OSI mapping, Genesis mapping, helix geometry functions. | `Level` (IntEnum), `Operation` (IntEnum), `LEVEL_NAMES`, `LEVEL_ICONS`, `LEVEL_DIMENSIONS`, `LEVEL_DESCRIPTIONS`, `fib()`, `level_angle()`, `level_position()` | **Canonical 0-6 constants.** Should be the single source of truth for 0-6 but duplicated everywhere. Genesis mapping is here but level model is 0-6. |

### 5. API & IDENTITY

| # | File | Lines | Model | Purpose | Key Classes / Functions | Issues |
|---|------|-------|-------|---------|------------------------|--------|
| 20 | `api.py` | 2886 | ➖ N/A | Human-first API with semantic positioning, identity system, multi-path lookup, Dimension class, Datastore (lazy ingest), Operations. | `Position`/`Direction`/`Orientation`/`Size`/`Anchor`/`Relation` (enums), `IdentityLookup`, `Dimension`, `Datastore`, `Operation`, `Operations`, `find()`, `query()`, `identity()`, `register_datastore()` | Very large (2886 lines), should be split. Global mutable state (_identity_registry, etc.). Not thread-safe. |
| 21 | `dimensional_api.py` | 3478 | ❌ 0-6 | **Largest file.** Extended dimensional API. (Not fully read but grep shows level 0-6 references.) | Presumably extends api.py pattern | Too large. Likely duplicates api.py concepts. |
| 22 | `identity_first.py` | 679 | ❌ 0-6 | Identity-First paradigm: identity precedes form. IdentityAnchor[T] with D0-D6 semantic levels, lazy manifestation at D4, meaning at D6. IdentityRegistry. | `SemanticLevel` (IntEnum 0-6), `IdentityAnchor[T]`, `IdentityRegistry`, `create_identity()`, `identity()` | Uses 0-6 (VOID-MEANING). Global `_default_registry` singleton. `get_by_name()` is O(N) scan. |

### 6. SRL & SERIALIZATION

| # | File | Lines | Model | Purpose | Key Classes / Functions | Issues |
|---|------|-------|-------|---------|------------------------|--------|
| 23 | `srl.py` | 321 | ❌ 0-6 | Secure Resource Locator — universal addressing. SRL dataclass with parse/navigate/traverse. Also defines a **second Core class** (class-level `_store` dict). | `Level` (IntEnum 0-6), `SRL`, `srl()`, `Core` | **Duplicate Core** (conflicts with core.py). Another Level enum. SRL.parse is fragile (no error handling for malformed input). Core._store is class-level mutable (shared across all instances). |
| 24 | `serialization.py` | 1050 | ➖ N/A | Binary/JSON/SRL serialization, transport abstractions (MemoryTransport, MessageChannel), streaming serializer, schema registry. | `BinarySerializer`, `JSONSerializer`, `SRLSerializer`, `StreamingSerializer`, `DimensionalSerializer`, `Transport`, `TransportMessage`, `MemoryTransport`, `MessageChannel`, `SchemaRegistry` | Large file mixing serialization + transport. SRLSerializer overlaps with srl.py. |
| 25 | `converters.py` | 443 | ❌ 0-6 | Type converters: JSON, dict, numpy, pandas, helix coords. Nested-to-dimensional flattening. | `HelixJSONEncoder`, `to_json()`, `from_json()`, `to_numpy()`, `to_dataframe()`, `to_helix_coords()`, `nested_to_dimensional()`, `quick_token()` | Uses LEVEL_NAMES (0-6). Lazy numpy/pandas imports are correct. |

### 7. BUILDERS, VALIDATORS, ASSEMBLER

| # | File | Lines | Model | Purpose | Key Classes / Functions | Issues |
|---|------|-------|-------|---------|------------------------|--------|
| 26 | `builders.py` | 529 | ❌ 0-6 | Fluent builders: TokenBuilder, BatchTokenBuilder, StateBuilder, ManifoldBuilder, PathBuilder, KernelBuilder. Quick factory functions. | `TokenBuilder`, `BatchTokenBuilder`, `StateBuilder`, `ManifoldBuilder`, `PathBuilder`, `KernelBuilder`, `token()`, `manifold()` | StateBuilder validates 0-6. Imports LEVEL_NAMES (0-6). |
| 27 | `validators.py` | 641 | ❌ 0-6 | Input validation: level/spiral/state/token/signature/location/payload/path validators. Fluent `Validator` class. | `ValidationResult`, `ValidationIssue`, `validate_level()`, `validate_state()`, `validate_token()`, `validate_state_transition()`, `Validator` | Validates levels as 0-6 exclusively. transition validation uses wrong rules for Genesis model. |
| 28 | `assembler.py` | 714 | ❌ 0-6 | File reconstruction from manifold data. FileCategory enum mapped to levels 0-6. FileAssembler, ManifoldFileSystem (virtual FS: spirals→folders, levels→categories). | `FileCategory` (0-6), `AssembledFile`, `FileAssembler`, `VirtualEntry`, `ManifoldFileSystem` | FileCategory maps BINARY=0..TEXT=6 (uses 0-6 model). Accesses substrate internal `_ingested_keyed` directly (encapsulation violation). |

### 8. TRANSPORT & NETWORKING

| # | File | Lines | Model | Purpose | Key Classes / Functions | Issues |
|---|------|-------|-------|---------|------------------------|--------|
| 29 | `transport.py` | 700 | ❌ 0-6 | OSI-mapped transport layer. HelixPacket (spiral + level addressing), HelixStream (ordered packet output), HelixTransport (multi-stream management), HelixWire (serialization). | `TransportLevel` (enum), `HelixPacket`, `HelixStream`, `HelixTransport`, `HelixWire` | Uses levels 0-6 mapped to OSI layers. |
| 30 | `audio_transport.py` | 670 | ❌ 0-6 | Audio-specific transport. AudioLevel enum (0-6), AudioFrame, SyncSignal, AudioStream, AudioTransport, LatencyOptimizer. | `AudioLevel` (0-6), `AudioFrame`, `SyncSignal`, `AudioStream`, `AudioTransport`, `LatencyOptimizer` | Uses 0-6. Priority system maps AudioLevel to precedence. |
| 31 | `connector.py` | 508 | ➖ N/A | Connection management: LocalConnector, LazySRL, ConnectorRegistry. Protocols for data source connectors. | `ConnectionState`, `DataSourceConnector` (Protocol), `LocalConnector`, `LazySRL`, `ConnectorRegistry`, `lazy_srl()` | LazySRL duplicates SRL concepts from srl.py and kernel_primitives.py. |
| 32 | `dimensional_ip.py` | 610 | ➖ N/A | IP addresses as dimensional coordinates. DimensionalSubnet (CIDR as dimensional regions). DimensionalPacket. DimensionalRouter. | `DimensionalIP`, `DimensionalSubnet`, `DimensionalPacket`, `DimensionalRouter`, `ManifoldBenchmark` | Router.route() is trivial. Checksum is non-cryptographic. `if __name__` test block inline. |

### 9. OSI / CLOUD / PLATFORM MANIFOLDS

| # | File | Lines | Model | Purpose | Key Classes / Functions | Issues |
|---|------|-------|-------|---------|------------------------|--------|
| 33 | `osi_manifold.py` | 868 | ❌ 0-6 | OSI-Helix unified transport. ManifoldAddress replacing IP, ManifoldDatagram replacing packets, ManifoldRouter (geodesic routing), OSIManifoldStack, HTTPManifoldBridge. | `OSIHelixLayer` (0-6), `ManifoldAddress`, `ManifoldDatagram`, `ManifoldRouter`, `OSIManifoldStack`, `HTTPManifoldBridge` | Uses POINT=0..META=6 (0-6 model). Good deserialization bounds checking. URL-to-address bridge is useful. `if __name__` block. |
| 34 | `openstack_manifold.py` | 885 | ❌ 0-6 | OpenStack as dimensional substrate. CloudToken, OpenStackSubstrate (sync from CLI), OpenStackKernel. | `CloudToken`, `OpenStackSubstrate`, `OpenStackKernel`, `CLOUD_LEVELS` (0-6) | Uses 0-6 levels. `tokens_for_state()` iterates all tokens (not O(1)). Uses `subprocess.run` for OpenStack CLI — **security concern** (command injection if names are user-controlled). |
| 35 | `platform_manifold.py` | 1044 | ❌ 0-6 | Unified platform manifold. Product suites (storage, connector, AI, platform, cloud). PlatformToken, SubstrateAdapter hierarchy. | `PlatformLevel` (0-6), `PlatformToken`, `SubstrateAdapter`, `StorageAdapter`, `ConnectorAdapter`, `AIAdapter`, `PlatformManifold` | Uses 0-6 levels. sys.path manipulation. Adapter classes are mostly stubs (`raise NotImplementedError`). |
| 36 | `wave_manifold.py` | 1456 | ➖ N/A | Wave/surfer metaphor for manifold geometry. WavePoint (surface + barrel coords), WaveSurface types (twisted ribbon, steep face, hyperbolic, volume wave). | `WaveSurface` (enum), `WavePoint`, plus likely wave analysis/traversal classes | Mathematical — no explicit layer model. Large file for a single metaphor. |

### 10. PRESENTATION & GRAPHICS

| # | File | Lines | Model | Purpose | Key Classes / Functions | Issues |
|---|------|-------|-------|---------|------------------------|--------|
| 37 | `presentation.py` | 1271 | ➖ N/A | Timeline-based presentation engine (linear slides). Easing functions, keyframes, content elements, transitions, HTML generation. | `EasingFunction`, `ContentType`, `Keyframe`, `ContentElement`, `Presentation`, `PresentationBuilder`, `HTMLGenerator` | Not dimensional — linear timeline model. Overlaps with dimensional_presentation.py conceptually. |
| 38 | `dimensional_presentation.py` | 1244 | ❌ 0-6 | 7-dimensional navigable presentation space. DimensionLevel enum (POINT=0..META=6). Nodes at dimensional coordinates. HTMLGenerator with inline CSS/JS. | `DimensionLevel` (0-6), `DimensionalCoord`, `DimensionalNode`, `DimensionalPresentation`, `DimensionalBuilder`, `DimensionalHTMLGenerator` | Uses 0-6. Inline CSS/JS in HTML generation. Could be merged with presentation.py. |
| 39 | `helix_styles.py` | 879 | ❌ 0-6 | Visual styling by level. VisualLevel IntEnum (0-6), HelixColor, ParticleSwarm, SubstrateElement, ManifoldSkin, HelixPresentation. | `VisualLevel` (0-6), `HelixColor`, `Particle`, `ParticleSwarm`, `SubstrateElement`, `HelixTransition`, `ManifoldSkin`, `HelixPresentation` | Uses 0-6. `TODO` markers. |
| 40 | `graphics3d.py` | 1580 | ➖ N/A | Full 3D engine: Vec3, Mat4, Quaternion, Mesh, RigidBody, AABB, CollisionResult, PhysicsWorld, Camera, Scene, Renderer. | `Vec3`, `Mat4`, `Quaternion`, `Vertex`, `Triangle`, `Mesh`, `RigidBody`, `AABB`, `PhysicsWorld`, `Camera`, `SceneObject`, `Scene`, `Renderer` | Vec3 duplicates Vector3D from kernel_primitives.py. Quaternion duplicates enhanced_primitives.py. Mat4 duplicates Matrix4x4. Software renderer — useful but duplicative math. |

### 11. UTILITIES & DEVELOPER TOOLS

| # | File | Lines | Model | Purpose | Key Classes / Functions | Issues |
|---|------|-------|-------|---------|------------------------|--------|
| 41 | `utilities.py` | 865 | ❌ 0-6 | HelixPath (dimensional path navigation), HelixQuery, HelixCache, HelixSerializer, HelixDiff, HelixLogger, ManifoldSampler, ManifoldQuery. | `HelixPath`, `HelixQuery`, `HelixCache`, `HelixSerializer`, `HelixDiff`, `HelixLogger`, `ManifoldSampler`, `ManifoldQuery` | Uses 0-6 via LEVEL_NAMES. HelixSerializer overlaps with serialization.py. |
| 42 | `dev_utils.py` | 812 | ❌ 0-6 | Developer tools: DimensionalLogger, Profiler, type validation, substrate/kernel inspection, FluentBuilder, custom exceptions. | `DimensionalLogger`, `Profiler`, `validate_level()` (0-6), `inspect_substrate()`, `inspect_kernel()`, `SubstrateBuilder`, `DimensionalError`, `DimensionalTestCase` | `validate_level()` checks 0-6. Duplicates validators.py logic. |
| 43 | `decorators.py` | 581 | ❌ 0-6 | Python decorators: `@dimensional`, `@at_level`, `@cached_by_level`, `@level_guard`, `@timed`, `@trace_helix`, `@materialize_result`, `@lazy_result`, `@retry_on_level_change`. | `dimensional()`, `at_level()`, `cached_by_level()`, `level_guard(min=0,max=6)`, `timed()`, `trace_helix()`, `compose()` | Uses LEVEL_NAMES (0-6). level_guard hardcodes 0-6 bounds. |
| 44 | `shortcuts.py` | 407 | ❌ 0-6 | Short aliases: `tok()`, `toks()`, `st()`, `kern()`, `go()`, `up()`, `down()`, `mani()`, `lvl()`, `ico()`. Level convenience functions. | `tok()`, `toks()`, `st()`, `origin()`, `apex()`, `kern()`, `go()`, `up()`, `down()`, `mani()`, `lvl()`, `ico()`, `potential()..whole()` | Uses LEVEL_NAMES/LEVEL_ICONS (0-6). |

### 12. APPS, ADDONS, LICENSING

| # | File | Lines | Model | Purpose | Key Classes / Functions | Issues |
|---|------|-------|-------|---------|------------------------|--------|
| 45 | `apps.py` | 731 | ❌ 0-6 | Application-level components: HelixExplorer (interactive manifold browser), HelixDataPipeline, HelixAPIAggregator, HelixEventSystem. | `HelixExplorer`, `HelixDataPipeline`, `HelixAPIAggregator`, `HelixEventSystem` | Uses LEVEL_NAMES/LEVEL_ICONS (0-6). |
| 46 | `addons.py` | 569 | ➖ N/A | Addon system: AddonType, AddonTier, AddonRegistry, decorator-based registration. Example addons. | `AddonType`, `AddonTier`, `AddonMeta`, `Addon`, `AddonRegistry`, `@register_addon` | `TODO: Implement actual marketplace API`. |
| 47 | `licensing.py` | 482 | ➖ N/A | License management: LicenseTier (FREE, STARTER, PRO, ENTERPRISE), PackageInfo, License, LicenseManager. License validation decorators. | `LicenseTier`, `PackageInfo`, `License`, `LicenseManager`, `@requires_license`, `check_license()` | `TODO: In production, validate against license server`. License validation is placeholder — **security concern** (trivially bypassable). |

### 13. TESTING & BENCHMARKING

| # | File | Lines | Model | Purpose | Key Classes / Functions | Issues |
|---|------|-------|-------|---------|------------------------|--------|
| 48 | `benchmark.py` | 606 | ❌ 0-6 | Benchmarks comparing traditional tree/SQL vs helix approach for car data. | `generate_car_data()`, `TraditionalTree`, `TraditionalSQL`, `HelixCars`, `run_benchmark()` | Uses 0-6 levels for car data organization. |
| 49 | `test_integration.py` | 340 | ❌ 0-6 | Integration tests: test_primitives, test_utilities, test_foundation, test_apps. | `test_primitives()`, `test_utilities()`, `test_foundation()`, `test_apps()`, `run_all_tests()` | Basic functional tests. No pytest framework — uses manual assertions. |

### 14. PACKAGE INIT

| # | File | Lines | Model | Purpose | Key Classes / Functions | Issues |
|---|------|-------|-------|---------|------------------------|--------|
| 50 | `__init__.py` | 1169 | Both | Package init. Re-exports from all modules. Exports both LAYER_* (Genesis 1-7) and LEVEL_* (0-6) symbols. Massive `__all__` list. | Imports from all 49 other files. Defines `__all__` with 200+ symbols. | Exports conflicting Level enums from multiple modules. Very large for an __init__.py. Import errors will cascade. |

---

## Critical Analysis

### A. Files Still Using Deprecated 0-6 Model (25+)

Nearly every file except `kernel.py` and `dimensional_kernel.py` uses the 0-6 level model. The most impactful files to migrate:

1. **`constants.py`** — Defines the canonical 0-6 Level enum that everything imports
2. **`core.py`** — Core singleton used by Interface system
3. **`substrate.py`** — Token signatures use Set[int] with {0..6}
4. **`manifold.py`** — Generative manifold (docstring says 1-7 but code is 0-6)
5. **`validators.py`** — All validation hardcodes 0-6
6. **`builders.py`** — StateBuilder hardcodes 0-6

### B. Duplicated Functionality (Consolidation Targets)

| What's Duplicated | Where | Recommendation |
|-------------------|-------|----------------|
| `Level` enum (0-6) | constants.py, srl.py, dimensional_primitives.py, dimensional_foundation.py, dimensional_presentation.py, identity_first.py (SemanticLevel), helix_styles.py (VisualLevel), + more | **Single source in constants.py**, all others import |
| `Vector3D` class | kernel_primitives.py, enhanced_primitives.py, substrates.py, graphics3d.py (as Vec3) | **Single source in kernel_primitives.py** |
| `Quaternion` class | enhanced_primitives.py, graphics3d.py | Merge into kernel_primitives.py |
| `Matrix4x4`/`Mat4` | kernel_primitives.py, graphics3d.py | Merge |
| `RGB`/`RGBA` | kernel_primitives.py, substrates.py | Import from kernel_primitives |
| `Scalar`, `Frequency`, `Amplitude`, `Duration`, `TimePoint` | kernel_primitives.py, substrates.py | substrates.py should import, not redefine |
| `Core` class | core.py, srl.py | **Remove from srl.py** or merge |
| `SRL`/`SecureResourceLocator` | srl.py, kernel_primitives.py, serialization.py (SRLSerializer) | Unify into srl.py |
| `HelixKernel`/`HelixState` | kernel.py, optimized_kernel.py, dimensional_kernel.py | Pick one canonical, alias the others |
| `ingest()` function | core.py, dimensional_primitives.py | Single implementation |
| `validate_level()` | validators.py, dev_utils.py | Use validators.py only |
| Presentation systems | presentation.py (linear), dimensional_presentation.py (7D) | Merge or clearly distinguish |

### C. Stubs / Incomplete Files

| File | Issue |
|------|-------|
| `platform_manifold.py` | SubstrateAdapter subclasses are stubs (`raise NotImplementedError`) |
| `addons.py` | `TODO: Implement actual marketplace API` |
| `licensing.py` | `TODO: In production, validate against license server` |
| `helix_styles.py` | `TODO: Implement shape decomposition` |
| `kernel.py` | `verify_invariants()` only checks one invariant |

### D. Security Concerns

| File | Concern | Severity |
|------|---------|----------|
| `openstack_manifold.py` | `subprocess.run` with potentially user-influenced args — **command injection risk** | HIGH |
| `licensing.py` | License validation is a placeholder stub — trivially bypassable | MEDIUM |
| `ai_substrate.py` | API keys handled via env vars / constructor — review for leakage | MEDIUM |
| `substrate.py` | Bare `except:` in `ingest()` — swallows all errors silently | MEDIUM |
| `srl.py` | Core._store is class-level mutable dict — shared mutable state | LOW |
| `dimensional_ip.py` | Checksum is simple sum, not cryptographic | LOW |
| `core.py` | No validation on SRL addresses — potential injection | LOW |

### E. Oversized Files (Candidates for Splitting)

| File | Lines | Recommendation |
|------|-------|----------------|
| `dimensional_api.py` | 3478 | Split into API modules |
| `api.py` | 2886 | Split identity/dimension/datastore/operations |
| `substrates.py` | 2357 | Import from kernel_primitives instead of copying; split domain substrates |
| `dimensional_primitives.py` | 1677 | Split collections/functional/concurrency/math/sensory into separate files |
| `wave_manifold.py` | 1456 | Single metaphor in 1456 lines — reduce |
| `graphics3d.py` | 1580 | Large but coherent; could split engine vs renderer |
| `__init__.py` | 1169 | Too many re-exports — use lazy imports or subpackage __init__ files |

### F. Recommended Migration Priority

1. **constants.py** → Add Genesis 1-7 `Layer` enum alongside existing `Level`
2. **validators.py** → Support both models, prefer 1-7
3. **substrate.py** → Migrate Token.signature from {0..6} to {1..7}  
4. **core.py** → Use Layer instead of LEVEL_NAMES
5. **manifold.py** → Fix code to match Genesis docstring
6. **builders.py** → Support both models
7. Remaining files follow naturally

### G. Architecture Observations

- **Three competing kernels**: kernel.py (Genesis 1-7), dimensional_kernel.py (Genesis 1-7 + numpy), optimized_kernel.py (0-6 + perf features). Should be unified.
- **Two competing Core classes**: core.py and srl.py both define `Core`.
- **Two competing SRL systems**: srl.py (SRL dataclass) and kernel_primitives.py (SecureResourceLocator singleton). 
- **substrates.py is a copy-paste** of kernel_primitives.py plus domain substrates. Should import, not duplicate.
- **No dependency injection** — many files create global singletons.
- **No pytest** — test_integration.py uses manual testing pattern.
