"""
Example substrate kernel: deterministic synthetic time series generator.
Takes state_summary = {seed: hex, params: {...}, op_log: [...]}
query_params: {length: int, freq: float, noise: float}
region: {t0: float, t1: float, dt: float} or {n: int}
Returns: dict with 't': list, 'y': list, 'meta': {...}
"""
from __future__ import annotations

import math
from typing import Any, Dict

from helix.manifold_core import DeterministicPRNG, _json_canonical, _sha256_hex


def _prng_from_state(state_summary: Dict[str, Any], view_key_material: bytes) -> DeterministicPRNG:
    k = (state_summary["seed"] + "|" + _sha256_hex(view_key_material)).encode("utf-8")
    return DeterministicPRNG(key=k, nonce=b"series")


def generate(state_summary: Dict[str, Any], query_params: Dict[str, Any], region: Dict[str, Any], prng: DeterministicPRNG) -> Dict[str, Any]:
    params = {
        "amplitude": 1.0,
        "phase": 0.0,
        "trend": 0.0,
        "bias": 0.0,
    }
    params.update(state_summary.get("params", {}))

    length = int(query_params.get("length", 256))
    freq = float(query_params.get("freq", 1.0))
    noise = float(query_params.get("noise", 0.0))

    # Build time axis deterministically from region
    if "dt" in region and "t0" in region:
        dt = float(region["dt"]) or 1.0
        t0 = float(region["t0"]) or 0.0
        t = [t0 + i * dt for i in range(length)]
    else:
        t = list(range(length))

    # Optional: fold op_log to adjust behavior
    for op in state_summary.get("op_log", []):
        if op.get("op") == "add_harmonic":
            # handled inline below via extra frequency component
            pass

    y = []
    for i, ti in enumerate(t):
        base = params["amplitude"] * math.sin(2 * math.pi * freq * ti + params["phase"]) + params["bias"]
        base += params["trend"] * ti
        # add deterministic noise
        if noise > 0:
            n = (prng.random_float() - 0.5) * 2.0 * noise
            base += n
        # process harmonics from op_log deterministically
        for op in state_summary.get("op_log", []):
            if op.get("op") == "add_harmonic":
                a = float(op.get("amplitude", 0.0))
                f = float(op.get("freq", 0.0))
                p = float(op.get("phase", 0.0))
                base += a * math.sin(2 * math.pi * f * ti + p)
        y.append(base)

    meta = {
        "params": params,
        "query_params": query_params,
        "region": region,
    }
    return {"t": t, "y": y, "meta": meta}
