# Universal Connector Blueprint
## Coordinate-First Architecture for the Universal Hard Drive

**ButterflyFX — Copyright (c) 2024-2026 Kenneth Bingham**  
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)

---

## Overview

The Universal Connector is an extension of Dimensional Computing that reimagines **storage and retrieval** the same way Dimensional Computing reimagines computation. Instead of storing data, you store **coordinates on the manifold**. The resource is never truly stored — only its address exists. When needed, the resource is **instantiated on demand** from its coordinate. When done, it **evaporates** — the coordinate remains, the data does not.

> **The Universal Hard Drive Premise:**  
> A coordinate IS the resource. Storage is only a cache. The manifold is the address space. Everything connected to the manifold is on the same "drive", regardless of where it physically lives.

This creates a universal interface where local files, remote APIs, peer nodes, and computed values all look identical to calling code. The substrate resolves the coordinate; the caller never knows (or needs to know) the source.

---

## Core Principles

| # | Principle | Description |
|---|---|---|
| 1 | **Coordinate is eternal** | Once a coordinate exists on the manifold, it is valid forever — it can always be re-invoked |
| 2 | **Instantiation is ephemeral** | The resource only exists during invocation — it evaporates after `release()` unless `persist=true` |
| 3 | **Storage is a fallback** | Local caching only occurs when the resolver is unreachable — not as primary storage |
| 4 | **Universal addressing** | All resources — local, remote, computed — share a single coordinate schema |
| 5 | **Resolver transparency** | Calling code invokes a coordinate; the substrate selects the resolver — the source is opaque |
| 6 | **Lineage is preserved** | Every invocation is traced in the lineage DAG for explainability and audit |
| 7 | **z = x · y binds** | The coordinate binding `z = x · y` where `x` = resource identity and `y` = resolver type |

---

## Coordinate Schema

Every resource on the manifold is addressed by a `UniversalCoordinate`:

```javascript
{
    id:       String,   // Unique stable ID (e.g. "butterflyfx/fonts/orbitron-v35")
    layer:    Number,   // Dimensional layer 1–7 (see Layer Mapping below)
    spiral:   Number,   // Spiral depth (0 = primary, 1+ = nested invocations)

    // Dimensional binding — z = x · y
    x:        Number,   // Resource identity vector (hash of id + version)
    y:        Number,   // Resolver type vector (see Resolver Types)
    z:        Number,   // Computed: x · y — the manifold address / binding key

    // Source
    uri:      String,   // Where to fetch: file path, URL, peer address, or compute fn name

    // Lifecycle
    persist:  Boolean,  // false (default) = evaporate after release; true = cache locally
    ttl:      Number,   // Milliseconds to live if persist=true (null = indefinite)

    // Traceability
    lineage:  Object,   // Lineage DAG node — records all invocations, transformations
    version:  String    // Semantic version of the resource (e.g. "v35", "r128")
}
```

**z = x · y** is the canonical Dimensional Computing binding equation. For the Universal Connector:
- `x` encodes **what** the resource is (a deterministic hash of `id + version`)
- `y` encodes **how** to fetch it (a numeric constant assigned to each resolver type)
- `z` is the stable manifold address — the binding key used for cache lookup and deduplication

---

## Layer Mapping

Universal Connector operations map to the 7-layer genesis model:

| Layer | Name | Op | Universal Connector Role |
|---|---|---|---|
| 1 | **Spark** | `lift` | A coordinate is declared — the resource's existence is announced on the manifold |
| 2 | **Mirror** | `map` | The coordinate is positioned — resolver type is assigned, `y` vector is set |
| 3 | **Relation** | `bind` | `z = x · y` is computed — the binding key is established |
| 4 | **Form** | `navigate` | The substrate routes to the correct resolver (disk, cache, http, peer, compute) |
| 5 | **Life** | `transform` | The resource is fetched, decoded, and transformed into usable form |
| 6 | **Mind** | `merge` | Multiple coordinates may be merged (e.g. font families = merge of weight variants) |
| 7 | **Completion** | `resolve` | The resource manifests to the caller; lineage is recorded |

After `resolve()`, if `persist=false`, the resource evaporates. The coordinate at Layer 1 remains — re-invocation is always possible.

---

## Resolver Types

The resolver type determines `y` in `z = x · y` and tells the substrate **how** to manifest the resource:

| Resolver | y value | Description |
|---|---|---|
| `local-disk` | 1 | Synchronous read from local filesystem (Node.js / Python) |
| `local-cache` | 2 | In-memory cache hit — fastest possible resolution |
| `sw-cache` | 3 | Browser Service Worker cache (offline-first fallback) |
| `http` | 5 | Fetch from a remote URL (CDN, API, peer server) |
| `peer` | 8 | Fetch from a peer node on the same manifold network |
| `compute` | 13 | Resource is generated on-the-fly by a computation function |

The `y` values follow the **Fibonacci sequence** (1, 1, 2, 3, 5, 8, 13) aligning with the 7-layer genesis model, where lower values (faster resolvers) align with lower layers.

---

## Lifecycle

```
DECLARE         MAP             BIND            INVOKE          MANIFEST        USE             RELEASE
  lift()    →   map()       →   bind()      →   invoke()    →   transform() →   [caller]    →   release()
  Layer 1       Layer 2         Layer 3         Layer 4         Layer 5         Layer 6         Layer 7
  Spark         Mirror          Relation        Form            Life            Mind            Completion
  coord born    resolver set    z = x·y         route to        fetch+decode    data available  evaporate
                                                resolver
```

**Detailed flow:**

1. **`lift(descriptor)`** — Creates a `UniversalCoordinate` from a descriptor object. Assigns `id`, `layer=1`, `spiral=0`, computes `x` from identity hash. Resource does not yet exist.
2. **`map(coord, resolverType, uri)`** — Assigns resolver type (sets `y`), stores `uri`. Positions coordinate on the manifold.
3. **`bind(coord)`** — Computes `z = x · y`. Registers coordinate in the substrate registry. Coordinate is now addressable.
4. **`invoke(coord)`** — Routes to the correct resolver. Attempts resolution in priority order: `local-cache → local-disk → sw-cache → http → peer → compute`. Returns a Promise/handle.
5. **`transform(raw)`** — Internal: decodes raw bytes/response into the typed resource (font bytes, JSON object, image, etc.).
6. **`resolve(coord)`** — Delivers the manifested resource to the caller. Records invocation in lineage DAG.
7. **`release(coord)`** — If `persist=false`: resource is evicted from memory. If `persist=true`: resource is written to local cache with `ttl`. Coordinate always remains.

**Re-invocation:** After `release()`, invoking the same coordinate repeats from step 4. The coordinate is eternal; the resource is ephemeral.

**Cache-as-fallback rule:** The substrate only writes to local cache (step 7 with `persist=true`) when the primary resolver was unreachable during the last invocation. The next invocation tries the primary resolver again — cache is not the source of truth, the resolver is.

---

## Substrate API

The `UniversalSubstrate` is the runtime that manages coordinate registration and resolution.

### JavaScript Interface

```javascript
class UniversalSubstrate {
    // Core lifecycle
    lift(descriptor)                    // → UniversalCoordinate (Layer 1)
    map(coord, resolverType, uri)       // → coord (Layer 2, y vector set)
    bind(coord)                         // → coord (Layer 3, z = x·y computed)
    invoke(coord)                       // → Promise<resource> (Layers 4–6)
    release(coord)                      // → void (Layer 7, evaporate or persist)

    // Resolver registry
    registerResolver(type, fn)          // Register a custom resolver function
    getResolver(type)                   // → resolver function

    // Coordinate registry
    register(coord)                     // Add coord to the substrate registry
    lookup(id)                          // → UniversalCoordinate | null
    lookupByZ(z)                        // → UniversalCoordinate | null (by binding key)

    // Cache management
    cache(coord, resource)              // Store resource in local cache
    evict(coord)                        // Remove resource from local cache
    isCached(coord)                     // → Boolean

    // Lineage
    trace(coord)                        // → LineageNode[] (full invocation history)
    explain(coord)                      // → String (human-readable lineage)
}

class UniversalCoordinate {
    constructor(descriptor)             // id, layer, spiral, x, y, uri, persist, ttl, version
    computeZ()                          // → Number: z = x · y
    spiralUp()                          // layer 7→1, spiral++
    spiralDown()                        // layer 1→7, spiral--
    toJSON()                            // → serializable coordinate
    static fromJSON(obj)                // → UniversalCoordinate
}
```

### Python Interface

```python
class UniversalSubstrate:
    def lift(self, descriptor: dict) -> UniversalCoordinate
    def map(self, coord: UniversalCoordinate, resolver_type: str, uri: str) -> UniversalCoordinate
    def bind(self, coord: UniversalCoordinate) -> UniversalCoordinate
    def invoke(self, coord: UniversalCoordinate) -> Any
    def release(self, coord: UniversalCoordinate) -> None
    def register_resolver(self, resolver_type: str, fn: Callable) -> None
    def register(self, coord: UniversalCoordinate) -> None
    def lookup(self, id: str) -> Optional[UniversalCoordinate]
    def trace(self, coord: UniversalCoordinate) -> List[LineageNode]

class UniversalCoordinate:
    id: str
    layer: int          # 1–7
    spiral: int
    x: float            # identity vector
    y: float            # resolver vector
    z: float            # binding: x · y
    uri: str
    persist: bool
    ttl: Optional[int]
    lineage: LineageNode
    version: str

    def compute_z(self) -> float
    def spiral_up(self) -> None
    def spiral_down(self) -> None
    def to_dict(self) -> dict
```

---

## Resolver Priority Chain

When `invoke(coord)` is called, the substrate attempts resolvers in this order:

```
1. local-cache  (y=2)  → fastest, in-memory; skip if not cached
2. local-disk   (y=1)  → filesystem; skip if uri is not a local path
3. sw-cache     (y=3)  → Service Worker cache (browser only); skip if not in SW context
4. http         (y=5)  → remote fetch; skip if offline
5. peer         (y=8)  → peer node; skip if peer unreachable
6. compute      (y=13) → generate; skip if no compute fn registered
```

If all resolvers fail: `invoke()` throws `ManifoldResolutionError` with full lineage trace.
If a non-primary resolver succeeds and `persist=true`, the result is cached locally for the next invocation.

---

## Canonical Example: Font Loading

Fonts are the **first concrete example** of the Universal Connector pattern. Instead of Google Fonts (an external CDN) serving fonts to your page, the substrate holds coordinates pointing to locally-hosted woff2 files.

```javascript
const substrate = new UniversalSubstrate();

// 1. Declare the coordinate (Spark — Layer 1)
const orbitronCoord = substrate.lift({
    id: 'butterflyfx/fonts/orbitron',
    version: 'v35',
    persist: true,         // fonts can be cached — they are static
    ttl: 31536000000       // 1 year in ms
});

// 2. Map to resolver and URI (Mirror — Layer 2)
substrate.map(orbitronCoord, 'local-disk', '/lib/fonts/yMJRMIlzdpvBhQQL_Qq7dy0.woff2');

// 3. Bind — z = x · y (Relation — Layer 3)
substrate.bind(orbitronCoord);

// 4–7. Invoke — manifest, use, resolve (Form → Completion)
const fontBytes = await substrate.invoke(orbitronCoord);
// fontBytes is available here
// After use, substrate.release(orbitronCoord) persists to cache (persist=true)
```

If the local file is missing (resolver fails), the substrate automatically falls back to the `http` resolver using the original Google Fonts URL — then caches the result locally so the next invocation is local.

**Why this matters:** The caller's code is identical whether the font comes from disk, cache, or the original CDN. The coordinate is the contract. The source is an implementation detail of the resolver.

---

## Relationship to Dimensional Computing Blueprint

The Universal Connector is built on top of the core Dimensional Computing framework:

| Blueprint Concept | Universal Connector Usage |
|---|---|
| `DimensionalObject` | `UniversalCoordinate` (a coordinate IS a DimensionalObject) |
| `z = x · y` | Binding equation: resource identity × resolver type = manifold address |
| 7-layer genesis model | Lifecycle maps directly (lift→resolve = Layer 1→7) |
| Substate system | Resolver substates: `offline-substate` forces `local-cache` only |
| Lineage DAG | Every invocation recorded; full audit trail of resource fetches |
| Spiral navigation | Re-invocation after release = spiral; same coord, next spiral turn |
| Golden Ratio φ | Fibonacci y-values for resolver types approach φ — faster resolvers "cost less" |

---

## Consistency Rules

These rules ensure the Universal Connector remains consistent as it evolves:

1. **Coordinates are immutable after `bind()`** — `id`, `x`, `y`, and `z` must never change after binding
2. **`release()` is always called** — resources must be released when done; use `try/finally`
3. **`persist=false` is the default** — explicitly set `persist=true` only for static assets
4. **Resolvers are pure functions** — a resolver receives a `uri` and returns bytes/object; no side effects
5. **Lineage is never truncated** — all invocations are recorded; the DAG is append-only
6. **Cache is a mirror, not the source** — cache stores a copy; the resolver is always the authority
7. **Spiral means re-entry** — same coordinate invoked a second time is a new spiral turn, not a mutation

---

*See also: `docs/DIMENSIONAL_COMPUTING_BLUEPRINT.md` for the full kernel op specification.*
*Implementation: `web/lib/universal-substrate.js` (JavaScript), `helix/universal_substrate.py` (Python)*

