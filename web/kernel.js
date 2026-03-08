/**
 * ButterflyFX Dimensional Kernel
 * The Schwarz Diamond Gyroid Lattice — one kernel, all dimensions
 *
 * z = x·y is the primitive at every node, connected at 90°.
 * Each dimension is a complete Fibonacci square.
 * All dimensions are connected through this lattice.
 *
 * Substrate (x) · Manifold (y) → Dimension (z)
 * Nothing imposed. Everything revealed.
 *
 * Copyright (c) 2024-2026 Kenneth Bingham — https://butterflyfx.us
 * CC BY 4.0 — Attribution required.
 */

const ButterflyKernel = (function () {
  'use strict';

  // ── Fibonacci Constants ──────────────────────────────────────────────────
  const PHI              = 1.618033988749895;
  const GOLDEN_ANGLE_DEG = 137.5077640500378;
  const GOLDEN_ANGLE_RAD = GOLDEN_ANGLE_DEG * Math.PI / 180;
  const FIBONACCI_CAP    = 21;   // Healthy growth ceiling — unlimited growth is cancer
  const FIBONACCI        = Object.freeze([0, 1, 1, 2, 3, 5, 8, 13, 21]);

  // ── The 7 Layers of Creation (Genesis Model) ─────────────────────────────
  // Each number is a dimension of its own — its complete square.
  // Point → Line → Width → Plane → Volume → Whole → Transcendence
  const LAYERS = Object.freeze({
    1: { name: 'Spark',      fibonacci: 1,  geometry: 'point',         equation: 'P₀ = {1}',          icon: '•' },
    2: { name: 'Mirror',     fibonacci: 1,  geometry: 'line',          equation: 'd(a,b) = |b-a|',    icon: '━' },
    3: { name: 'Relation',   fibonacci: 2,  geometry: 'width',         equation: 'z = x·y',           icon: '×' },
    4: { name: 'Form',       fibonacci: 3,  geometry: 'plane',         equation: 'z = x·y²',          icon: '▲' },
    5: { name: 'Life',       fibonacci: 5,  geometry: 'volume',        equation: 'm = x·y·z',         icon: '◆' },
    6: { name: 'Mind',       fibonacci: 8,  geometry: 'whole',         equation: 'Schwarz Diamond Gyroid Lattice', icon: '✦' },
    7: { name: 'Completion', fibonacci: 13, geometry: 'transcendence', equation: 'φ = (1+√5)/2',      icon: '◉' },
  });

  // ── The primitive manifold — z = x·y ────────────────────────────────────
  // Hyperbolic paraboloid — the twisted square.
  // Doubly ruled: every angle represented. Connected at 90°.
  // Positive curvature in one node → negative curvature in neighbour.
  // Self-supporting. No external scaffold. The geometry IS the support.
  function manifold(x, y) { return x * y; }

  // ── Fibonacci momentum ───────────────────────────────────────────────────
  // Each Fibonacci number carries forward velocity from the previous two.
  // Position, vector, and convergence toward φ — all live in the number.
  function momentum(layer) {
    const l    = Math.max(1, Math.min(7, layer));
    const fib  = FIBONACCI[l] || 1;
    const prev = FIBONACCI[Math.max(0, l - 1)] || 1;
    return Object.freeze({
      position:    fib,
      square:      fib * fib,          // each number is its own complete square
      vector:      fib - prev,         // carried-forward velocity
      ratio:       prev > 0 ? fib / prev : 1,
      convergence: Math.abs((prev > 0 ? fib / prev : 1) - PHI),
    });
  }

  // ── Healthy growth — stop at 21 ──────────────────────────────────────────
  // At 21 the unit is complete. It becomes a single point in the next spiral.
  // Transcendence, not death.
  function fanOut(value) {
    if (value >= FIBONACCI_CAP) return 1;  // transcend → point(1) in next spiral
    const idx = FIBONACCI.indexOf(value);
    return idx >= 0 && idx < FIBONACCI.length - 1 ? FIBONACCI[idx + 1] : value;
  }

  // ── Lattice registry ─────────────────────────────────────────────────────
  // Dimensions = complete z=xy squares (games, creation, learning…)
  // Nodes      = sub-nodes within a dimension (brickbreaker, music, photo…)
  // Connections = 90° bonds — compression becomes tension, self-balancing
  const _dimensions = {};
  const _nodes      = {};

  function registerDimension(id, descriptor) {
    if (_dimensions[id]) return _dimensions[id];
    _dimensions[id] = Object.assign({
      id,
      label:       id,
      layer:       5,          // Life — a dimension fills volume
      primitive:   'z = x·y',
      nodes:       [],
      connections: [],
    }, descriptor);
    return _dimensions[id];
  }

  function registerNode(id, dimensionId, descriptor) {
    if (_nodes[id]) return _nodes[id];
    const dim = _dimensions[dimensionId];
    if (dim && !dim.nodes.includes(id)) dim.nodes.push(id);
    _nodes[id] = Object.assign({
      id,
      dimension:   dimensionId,
      layer:       3,          // Relation — every node is a z=xy surface
      primitive:   'z = x·y',
      connections: [],
    }, descriptor);
    return _nodes[id];
  }

  // 90° bond — the Schwarz Diamond connection between any two nodes or dimensions
  function connect(a, b) {
    const ra = _dimensions[a] || _nodes[a];
    const rb = _dimensions[b] || _nodes[b];
    if (ra && !ra.connections.includes(b)) ra.connections.push(b);
    if (rb && !rb.connections.includes(a)) rb.connections.push(a);
  }

  function dimension(id) { return _dimensions[id] || null; }
  function node(id)      { return _nodes[id] || null; }
  function dimensions()  { return Object.assign({}, _dimensions); }
  function nodes()       { return Object.assign({}, _nodes); }

  // ── Public API ───────────────────────────────────────────────────────────
  return Object.freeze({
    // Constants
    PHI, GOLDEN_ANGLE_DEG, GOLDEN_ANGLE_RAD, FIBONACCI_CAP, FIBONACCI, LAYERS,
    // Primitives
    manifold, momentum, fanOut,
    // Lattice
    registerDimension, registerNode, connect,
    dimension, node, dimensions, nodes,
  });

}());

// ── Register the two root dimensions ────────────────────────────────────────
// All nodes within each dimension connect at 90° to nodes in the other.
ButterflyKernel.registerDimension('games', {
  label:  "Ken's Games",
  layer:  5,
  substrate:  'player interaction',
  manifold:   'game mechanics',
  dimension:  'z = player · mechanics',
});

ButterflyKernel.registerDimension('creation', {
  label:  'Creation Studio',
  layer:  5,
  substrate:  'medium spectrum (light, sound, time)',
  manifold:   'creative tools (lens)',
  dimension:  'z = medium · tool',
});

// 90° bond — games and creation support each other structurally
ButterflyKernel.connect('games', 'creation');

