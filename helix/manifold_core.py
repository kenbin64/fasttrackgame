"""
Manifold/Substrate core: persists only contracts, kernels (code refs), and compact generative state
(deltas) as content-addressed descriptors. No payload persistence. Views are computed JIT in RAM.

Public API:
- register_contract(manifest)
- get_contract(contract_id, version=None)
- init_state(contract_id, base_seed: bytes|str|int, base_params: dict) -> state_hash
- apply_delta(state_hash, delta: dict) -> new_state_hash
- merge_states(state_hash_a, state_hash_b, rule: dict) -> merged_state_hash
- compute_view(contract_id, version, state_hash, query_params, region) -> (result, provenance)

Design goals:
- Deterministic: fixed canonicalization and PRNG discipline
- Content-addressed: everything addressable by SHA-256 of canonical JSON
- RAM-only view cache; no on-disk payloads
- Small, dependency-light, pure Python
"""
from __future__ import annotations

import hashlib
import json
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Tuple

# ------------------------
# Utilities
# ------------------------

def _json_canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash_json(obj: Any) -> str:
    return _sha256_hex(_json_canonical(obj).encode("utf-8"))


# Deterministic PRNG: simple ChaCha-like counter-based using hashlib as KDF (not crypto-secure for secrets)
# but fully deterministic. For true crypto, wire python cryptography libs; here we avoid deps.
class DeterministicPRNG:
    def __init__(self, key: bytes, nonce: bytes = b"", counter: int = 0):
        self.key = key
        self.nonce = nonce
        self.counter = counter

    def _block(self) -> bytes:
        material = self.key + b"|" + self.nonce + b"|" + str(self.counter).encode()
        self.counter += 1
        return hashlib.sha256(material).digest()

    def random_bytes(self, n: int) -> bytes:
        out = bytearray()
        while len(out) < n:
            out.extend(self._block())
        return bytes(out[:n])

    def random_float(self) -> float:
        # 53-bit mantissa from 8 bytes
        b = self.random_bytes(8)
        val = int.from_bytes(b, "big") & ((1 << 53) - 1)
        return val / float(1 << 53)


# ------------------------
# In-memory registries (persistable small descriptors only)
# ------------------------

@dataclass(frozen=True)
class Contract:
    contract_id: str
    version: str
    kernel_ref: str  # module:function path e.g., "helix.kernels.synthetic_series:generate"
    invariants: Dict[str, Any] = field(default_factory=dict)
    cost_caps: Dict[str, Any] = field(default_factory=dict)


class Registry:
    def __init__(self):
        self._contracts: Dict[Tuple[str, str], Contract] = {}
        self._states: Dict[str, Dict[str, Any]] = {}  # state_hash -> state_node
        self._lock = threading.RLock()

    # Contracts
    def register_contract(self, manifest: Dict[str, Any]) -> Contract:
        with self._lock:
            contract = Contract(
                contract_id=manifest["contract_id"],
                version=manifest["version"],
                kernel_ref=manifest["kernel_ref"],
                invariants=manifest.get("invariants", {}),
                cost_caps=manifest.get("cost_caps", {}),
            )
            key = (contract.contract_id, contract.version)
            self._contracts[key] = contract
            return contract

    def get_contract(self, contract_id: str, version: Optional[str] = None) -> Contract:
        with self._lock:
            if version is not None:
                key = (contract_id, version)
                if key not in self._contracts:
                    raise KeyError(f"Contract {contract_id}@{version} not registered")
                return self._contracts[key]
            # choose latest by lexical version if not specified
            cands = [c for (cid, _), c in self._contracts.items() if cid == contract_id]
            if not cands:
                raise KeyError(f"No versions registered for contract {contract_id}")
            return sorted(cands, key=lambda c: c.version)[-1]

    # Generative State (Merkle-like DAG nodes stored as small JSON)
    def init_state(self, contract_id: str, base_seed: Any, base_params: Dict[str, Any]) -> str:
        node = {
            "type": "root",
            "contract_id": contract_id,
            "base_seed": base_seed,
            "base_params": base_params,
            "parents": [],
            "ops": [],
        }
        h = _hash_json(node)
        with self._lock:
            self._states[h] = node
        return h

    def apply_delta(self, state_hash: str, delta: Dict[str, Any]) -> str:
        with self._lock:
            if state_hash not in self._states:
                raise KeyError(f"Unknown state {state_hash}")
            parent = self._states[state_hash]
            node = {
                "type": "delta",
                "contract_id": parent["contract_id"],
                "parents": [state_hash],
                "ops": [delta],
            }
            h = _hash_json(node)
            self._states[h] = node
            return h

    def merge_states(self, state_hash_a: str, state_hash_b: str, rule: Dict[str, Any]) -> str:
        with self._lock:
            if state_hash_a not in self._states or state_hash_b not in self._states:
                raise KeyError("Unknown state(s) for merge")
            node = {
                "type": "merge",
                "parents": [state_hash_a, state_hash_b],
                "rule": rule,
            }
            h = _hash_json(node)
            self._states[h] = node
            return h

    def materialize_state(self, state_hash: str) -> Dict[str, Any]:
        # Replay from root(s) deterministically to compute current seed/params and op log
        with self._lock:
            if state_hash not in self._states:
                raise KeyError(f"Unknown state {state_hash}")
            # Collect ancestors via DFS, then topologically sort by hash order for determinism
            visited = set()
            stack = [state_hash]
            nodes: Dict[str, Dict[str, Any]] = {}
            while stack:
                h = stack.pop()
                if h in visited:
                    continue
                visited.add(h)
                n = self._states[h]
                nodes[h] = n
                for p in n.get("parents", []):
                    stack.append(p)
            # Find roots and order parents list deterministically
            # Simple approach: sort by hash, apply roots first, then deltas, then merges by hash order
            ordered = sorted(nodes.items(), key=lambda kv: kv[0])
            seed = None
            params: Dict[str, Any] = {}
            op_log = []
            for h, n in ordered:
                if n.get("type") == "root":
                    # if multiple roots reachable, combine deterministically: concat seeds and merge params
                    root_seed_bytes = _json_canonical(n["base_seed"]).encode("utf-8")
                    seed = _sha256_hex((seed.encode() if seed else b"") + root_seed_bytes)
                    params = {**params, **n["base_params"]}
                elif n.get("type") == "delta":
                    op = n["ops"][0]
                    # apply op to params/seed deterministically
                    kind = op.get("op")
                    if kind == "set_param":
                        params[op["key"]] = op["value"]]
                    elif kind == "inc_param":
                        k = op["key"]
                        params[k] = params.get(k, 0) + op.get("delta", 0)
                    elif kind == "seed_mix":
                        # mix seed with provided material
                        mixin = _json_canonical(op.get("mixin", "")).encode("utf-8")
                        base = (seed or "").encode("utf-8")
                        seed = _sha256_hex(base + mixin)
                    else:
                        # Unknown op: include in log for kernel-defined handling
                        op_log.append(op)
                elif n.get("type") == "merge":
                    # deterministically fold parent summaries and rule
                    rule_bytes = _json_canonical(n["rule"]).encode("utf-8")
                    seed = _sha256_hex((seed or "").encode("utf-8") + rule_bytes)
                    # params unchanged here; kernel may inspect rule/op_log
                else:
                    pass
            if seed is None:
                # if no root seed was set, default to zero seed
                seed = _sha256_hex(b"")
            return {"seed": seed, "params": params, "op_log": op_log}


# ------------------------
# Kernel resolution and JIT view engine
# ------------------------

def _resolve_kernel(ref: str) -> Callable[[Dict[str, Any], Dict[str, Any], Dict[str, Any], DeterministicPRNG], Any]:
    # ref format: module_path:function_name
    mod_path, fn_name = ref.split(":", 1)
    mod = __import__(mod_path, fromlist=[fn_name])
    fn = getattr(mod, fn_name)
    return fn


@dataclass
class Provenance:
    contract_id: str
    version: str
    kernel_ref: str
    kernel_hash: str
    state_hash: str
    state_summary_hash: str
    query_hash: str
    region_hash: str
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


class ViewEngine:
    def __init__(self, registry: Registry, ram_cache_bytes: int = 16 * 1024 * 1024):
        self.registry = registry
        self.cache: Dict[str, Any] = {}
        self.cache_order: list[str] = []
        self.cache_size = 0
        self.cache_cap = ram_cache_bytes
        self._lock = threading.RLock()

    def _cache_put(self, key: str, value: Any, approx_size: int = 0):
        with self._lock:
            self.cache[key] = value
            self.cache_order.append(key)
            self.cache_size += approx_size
            while self.cache_size > self.cache_cap and self.cache_order:
                evict = self.cache_order.pop(0)
                v = self.cache.pop(evict, None)
                # best-effort size accounting; we don't know exact bytes without sys.getsizeof deep scan
                # treat each as equal chunk for simplicity if no size given
                self.cache_size = max(0, self.cache_size - approx_size)

    def _cache_get(self, key: str) -> Optional[Any]:
        with self._lock:
            return self.cache.get(key)

    def compute_view(self, contract_id: str, version: Optional[str], state_hash: str,
                     query_params: Dict[str, Any], region: Dict[str, Any]) -> Tuple[Any, Provenance]:
        contract = self.registry.get_contract(contract_id, version)
        kernel = _resolve_kernel(contract.kernel_ref)
        # kernel hash = hash of ref string; for stronger guarantee, developer can embed code hash in manifest
        kernel_hash = _hash_json({"kernel_ref": contract.kernel_ref})

        # Materialize state summary deterministically
        state_summary = self.registry.materialize_state(state_hash)
        state_summary_hash = _hash_json(state_summary)

        # Query/region hashes
        query_hash = _hash_json(query_params)
        region_hash = _hash_json(region)

        # Content address for view cache key
        view_key = _hash_json({
            "contract_id": contract.contract_id,
            "version": contract.version,
            "kernel_hash": kernel_hash,
            "state_hash": state_hash,
            "state_summary_hash": state_summary_hash,
            "query_hash": query_hash,
            "region_hash": region_hash,
        })

        cached = self._cache_get(view_key)
        if cached is not None:
            return cached[0], cached[1]

        # Deterministic PRNG keyed by the above
        prng = DeterministicPRNG(key=view_key.encode("utf-8"), nonce=b"manifold")

        # Enforce cost caps (simple time cap)
        start = time.time()
        time_cap = contract.cost_caps.get("time_ms", 5000)

        def _deadline_guard():
            if (time.time() - start) * 1000.0 > time_cap:
                raise TimeoutError("View computation exceeded time cap")

        # Execute kernel with guard points (kernel should call back if long-running, here we do coarse check)
        result = kernel(state_summary, query_params, region, prng)
        _deadline_guard()

        prov = Provenance(
            contract_id=contract.contract_id,
            version=contract.version,
            kernel_ref=contract.kernel_ref,
            kernel_hash=kernel_hash,
            state_hash=state_hash,
            state_summary_hash=state_summary_hash,
            query_hash=query_hash,
            region_hash=region_hash,
            timestamp=time.time(),
        )
        # Approx size heuristic
        approx_size = 1
        self._cache_put(view_key, (result, prov), approx_size)
        return result, prov


# Singleton-like convenience
_registry = Registry()
_view_engine = ViewEngine(_registry)

# Public API wrappers

def register_contract(manifest: Dict[str, Any]) -> Contract:
    return _registry.register_contract(manifest)


def get_contract(contract_id: str, version: Optional[str] = None) -> Contract:
    return _registry.get_contract(contract_id, version)


def init_state(contract_id: str, base_seed: Any, base_params: Dict[str, Any]) -> str:
    return _registry.init_state(contract_id, base_seed, base_params)


def apply_delta(state_hash: str, delta: Dict[str, Any]) -> str:
    return _registry.apply_delta(state_hash, delta)


def merge_states(state_hash_a: str, state_hash_b: str, rule: Dict[str, Any]) -> str:
    return _registry.merge_states(state_hash_a, state_hash_b, rule)


def compute_view(contract_id: str, version: Optional[str], state_hash: str,
                 query_params: Dict[str, Any], region: Dict[str, Any]) -> Tuple[Any, Dict[str, Any]]:
    result, prov = _view_engine.compute_view(contract_id, version, state_hash, query_params, region)
    return result, prov.to_dict()
