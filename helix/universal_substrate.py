"""
Universal Substrate — Python Implementation
============================================

ButterflyFX Dimensional Computing Framework

Coordinate-first architecture: resources are never stored, only coordinates.
Invoke a coordinate → resource manifests → resource evaporates (unless persist=True).

See: docs/UNIVERSAL_CONNECTOR_BLUEPRINT.md

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
"""

from __future__ import annotations

import hashlib
import time
import asyncio
import json
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Callable, Dict, List, Optional, Tuple


# =============================================================================
# LAYER CONSTANTS — 7-Layer Genesis Model
# =============================================================================

class Layer(IntEnum):
    SPARK      = 1   # lift      — coordinate declared
    MIRROR     = 2   # map       — resolver assigned
    RELATION   = 3   # bind      — z = x·y computed
    FORM       = 4   # navigate  — resolver routed
    LIFE       = 5   # transform — resource fetched
    MIND       = 6   # merge     — resource assembled
    COMPLETION = 7   # resolve   — resource delivered


# =============================================================================
# RESOLVER TYPE CONSTANTS — Fibonacci y-values
# =============================================================================

class Resolver:
    LOCAL_DISK  = 1
    LOCAL_CACHE = 2
    SW_CACHE    = 3
    HTTP        = 5
    PEER        = 8
    COMPUTE     = 13

    _NAME_MAP: Dict[str, int] = {
        'local-disk':  LOCAL_DISK,
        'local_disk':  LOCAL_DISK,
        'local-cache': LOCAL_CACHE,
        'local_cache': LOCAL_CACHE,
        'sw-cache':    SW_CACHE,
        'sw_cache':    SW_CACHE,
        'http':        HTTP,
        'peer':        PEER,
        'compute':     COMPUTE,
    }

    @classmethod
    def y_for(cls, name: str) -> int:
        return cls._NAME_MAP.get(name.lower(), cls.HTTP)


# =============================================================================
# LINEAGE NODE
# =============================================================================

@dataclass
class LineageNode:
    op:        str
    coord_id:  str
    timestamp: float = field(default_factory=time.time)
    detail:    Dict  = field(default_factory=dict)
    children:  List['LineageNode'] = field(default_factory=list)

    def add_child(self, node: 'LineageNode') -> 'LineageNode':
        self.children.append(node)
        return node

    def explain(self, indent: int = 0) -> str:
        pad = '  ' * indent
        out = f"{pad}[{self.op}] {self.coord_id}\n"
        if self.detail:
            out += f"{pad}  {json.dumps(self.detail)}\n"
        for child in self.children:
            out += child.explain(indent + 1)
        return out


# =============================================================================
# UNIVERSAL COORDINATE
# =============================================================================

class UniversalCoordinate:
    """
    A point on the manifold that addresses a resource.
    The coordinate is eternal; the resource is ephemeral.

    z = x · y  where:
        x = identity vector (hash of id + version)
        y = resolver type vector (Fibonacci constant)
        z = manifold binding address
    """

    def __init__(self, id: str, version: str = 'v1',
                 persist: bool = False, ttl: Optional[float] = None):
        self.id            = id
        self.version       = version
        self.persist       = persist
        self.ttl           = ttl          # seconds, None = indefinite
        self.layer         = Layer.SPARK
        self.spiral        = 0
        self.x             = self._hash_id(f"{id}@{version}")
        self.y             = 0.0          # set by map()
        self.z             = 0.0          # set by bind()
        self.uri:          Optional[str] = None
        self.resolver_type: Optional[str] = None
        self.lineage       = LineageNode('lift', self.id, {'version': self.version})

    def _hash_id(self, s: str) -> float:
        """Stable deterministic float in (0, 1) from a string."""
        digest = hashlib.sha256(s.encode()).hexdigest()
        h = int(digest[:8], 16)
        return (h % 100_000) / 100_000 + 0.00001

    def compute_z(self) -> float:
        return self.x * self.y

    def spiral_up(self) -> None:
        self.layer  = Layer.SPARK
        self.spiral += 1

    def spiral_down(self) -> None:
        self.layer  = Layer.COMPLETION
        self.spiral = max(0, self.spiral - 1)

    def to_dict(self) -> dict:
        return {
            'id': self.id, 'version': self.version, 'layer': int(self.layer),
            'spiral': self.spiral, 'x': self.x, 'y': self.y, 'z': self.z,
            'uri': self.uri, 'persist': self.persist, 'ttl': self.ttl,
            'resolver_type': self.resolver_type,
        }

    def __repr__(self) -> str:
        return f"UniversalCoordinate(id={self.id!r}, z={self.z:.6f}, layer={self.layer.name})"


# =============================================================================
# MANIFOLD RESOLUTION ERROR
# =============================================================================

class ManifoldResolutionError(Exception):
    def __init__(self, coord: UniversalCoordinate, tried: List[str]):
        super().__init__(
            f"[UniversalSubstrate] Cannot resolve coordinate '{coord.id}' "
            f"(tried: {', '.join(tried)})"
        )
        self.coord = coord
        self.tried = tried


# =============================================================================
# UNIVERSAL SUBSTRATE
# =============================================================================

class UniversalSubstrate:
    """
    The runtime that manages coordinate registration and resource resolution.

    Lifecycle:
        lift()  → Layer 1 Spark      — coordinate declared
        map()   → Layer 2 Mirror     — resolver assigned
        bind()  → Layer 3 Relation   — z = x·y computed
        invoke()→ Layers 4–7         — resource manifested
        release()→ Layer 7 Completion — resource evaporated
    """

    def __init__(self):
        self._registry:  Dict[str, UniversalCoordinate] = {}
        self._cache:     Dict[float, Tuple[Any, Optional[float]]] = {}  # z → (resource, expires)
        self._resolvers: Dict[str, Callable] = {}
        self._compute:   Dict[str, Callable] = {}
        self._register_builtins()

    # ── Lifecycle: Layer 1 — Spark ──────────────────────────────────────────

    def lift(self, id: str, version: str = 'v1',
             persist: bool = False, ttl: Optional[float] = None) -> UniversalCoordinate:
        """Declare a coordinate. Resource does not yet exist."""
        return UniversalCoordinate(id=id, version=version, persist=persist, ttl=ttl)

    # ── Lifecycle: Layer 2 — Mirror ─────────────────────────────────────────

    def map(self, coord: UniversalCoordinate,
            resolver_type: str, uri: str) -> UniversalCoordinate:
        """Assign resolver type and URI. Positions coordinate on the manifold."""
        coord.resolver_type = resolver_type
        coord.y   = Resolver.y_for(resolver_type)
        coord.uri = uri
        coord.layer = Layer.MIRROR
        coord.lineage.add_child(
            LineageNode('map', coord.id, {'resolver_type': resolver_type, 'uri': uri, 'y': coord.y})
        )
        return coord

    # ── Lifecycle: Layer 3 — Relation ───────────────────────────────────────

    def bind(self, coord: UniversalCoordinate) -> UniversalCoordinate:
        """Compute z = x · y. Register in substrate registry."""
        coord.z = coord.compute_z()
        coord.layer = Layer.RELATION
        self._registry[coord.id] = coord
        coord.lineage.add_child(LineageNode('bind', coord.id, {'z': coord.z}))
        return coord

    # ── Lifecycle: Layers 4–7 — Form → Completion ──────────────────────────

    async def invoke(self, coord: UniversalCoordinate) -> Any:
        """
        Manifest the resource. Resolution priority:
        local-cache → local-disk → sw-cache → http → peer → compute
        """
        coord.layer = Layer.FORM
        tried: List[str] = []

        # 1. local-cache (fastest)
        cached = self._from_cache(coord)
        if cached is not None:
            coord.layer = Layer.COMPLETION
            coord.lineage.add_child(LineageNode('resolve', coord.id, {'via': 'local-cache'}))
            return cached

        # 2. Attempt resolvers in priority order
        priority = ['local-disk', 'sw-cache', 'http', 'peer', 'compute']
        resource = None
        used_resolver = None

        for rtype in priority:
            resolver = self._resolvers.get(rtype)
            if not resolver:
                continue
            # Skip mismatched types unless they're a plausible fallback
            if rtype != coord.resolver_type:
                if rtype == 'local-disk' and coord.uri and coord.uri.startswith('http'):
                    continue
                if rtype == 'http' and coord.uri and not coord.uri.startswith('http'):
                    continue
            tried.append(rtype)
            try:
                coord.layer = Layer.LIFE
                result = resolver(coord.uri, coord)
                if asyncio.iscoroutine(result):
                    result = await result
                resource = result
                used_resolver = rtype
                break
            except Exception:
                pass

        if resource is None:
            raise ManifoldResolutionError(coord, tried)

        coord.layer = Layer.COMPLETION
        coord.lineage.add_child(LineageNode('resolve', coord.id, {'via': used_resolver}))

        if coord.persist:
            self._to_cache(coord, resource)

        return resource

    def invoke_sync(self, coord: UniversalCoordinate) -> Any:
        """Synchronous wrapper around invoke() for non-async contexts."""
        return asyncio.get_event_loop().run_until_complete(self.invoke(coord))

    # ── Lifecycle: Release ──────────────────────────────────────────────────

    def release(self, coord: UniversalCoordinate) -> None:
        """Release resource. If persist=False, evict from cache. Coordinate remains."""
        if not coord.persist:
            self.evict(coord)
        coord.layer = Layer.SPARK   # reset — re-invocable
        coord.lineage.add_child(LineageNode('release', coord.id, {'persist': coord.persist}))

    # ── Resolver Registry ───────────────────────────────────────────────────

    def register_resolver(self, resolver_type: str, fn: Callable) -> None:
        """Register a custom resolver: fn(uri, coord) → resource (sync or async)."""
        self._resolvers[resolver_type] = fn

    def get_resolver(self, resolver_type: str) -> Optional[Callable]:
        return self._resolvers.get(resolver_type)

    def register_compute(self, name: str, fn: Callable) -> None:
        """Register a named compute function for the 'compute' resolver."""
        self._compute[name] = fn

    # ── Coordinate Registry ─────────────────────────────────────────────────

    def register(self, coord: UniversalCoordinate) -> None:
        self._registry[coord.id] = coord

    def lookup(self, id: str) -> Optional[UniversalCoordinate]:
        return self._registry.get(id)

    def lookup_by_z(self, z: float) -> Optional[UniversalCoordinate]:
        for c in self._registry.values():
            if abs(c.z - z) < 1e-10:
                return c
        return None

    # ── Cache Management ────────────────────────────────────────────────────

    def cache(self, coord: UniversalCoordinate, resource: Any) -> None:
        self._to_cache(coord, resource)

    def evict(self, coord: UniversalCoordinate) -> None:
        self._cache.pop(coord.z, None)

    def is_cached(self, coord: UniversalCoordinate) -> bool:
        return self._from_cache(coord) is not None

    def _to_cache(self, coord: UniversalCoordinate, resource: Any) -> None:
        expires = time.time() + coord.ttl if coord.ttl else None
        self._cache[coord.z] = (resource, expires)

    def _from_cache(self, coord: UniversalCoordinate) -> Optional[Any]:
        entry = self._cache.get(coord.z)
        if entry is None:
            return None
        resource, expires = entry
        if expires and time.time() > expires:
            del self._cache[coord.z]
            return None
        return resource

    # ── Lineage ─────────────────────────────────────────────────────────────

    def trace(self, coord: UniversalCoordinate) -> LineageNode:
        return coord.lineage

    def explain(self, coord: UniversalCoordinate) -> str:
        return coord.lineage.explain()

    # ── Built-in Resolvers ──────────────────────────────────────────────────

    def _register_builtins(self) -> None:
        # local-disk resolver
        def local_disk(uri: str, coord: UniversalCoordinate) -> bytes:
            with open(uri, 'rb') as f:
                return f.read()
        self.register_resolver('local-disk', local_disk)

        # http resolver (sync using urllib)
        def http_resolver(uri: str, coord: UniversalCoordinate) -> bytes:
            import urllib.request
            with urllib.request.urlopen(uri, timeout=15) as resp:
                return resp.read()
        self.register_resolver('http', http_resolver)

        # compute resolver
        def compute_resolver(uri: str, coord: UniversalCoordinate) -> Any:
            fn = self._compute.get(uri)
            if not fn:
                raise ValueError(f"No compute function '{uri}'")
            return fn(coord)
        self.register_resolver('compute', compute_resolver)

