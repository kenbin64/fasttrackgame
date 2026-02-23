# Dimensional 3D: Smart Immersive Graphics

## The 7 Layers of Dimensional Computing in Browser 3D

This document describes how ButterflyFX's Dimensional Computing integrates with Three.js to create "smart" 3D elements that understand themselves—their identity, context, relationships, intention, and lineage.

---

## Overview

Traditional 3D graphics in browsers are passive: meshes, lights, and cameras exist purely as visual artifacts with no inherent understanding. **Dimensional 3D** transforms these into **Dimensional Objects** on a mathematical manifold, enabling:

1. **Self-aware elements** - Objects know what they are (identity)
2. **Contextual positioning** - Objects know where they are on the 7-layer stack
3. **Relational understanding** - Objects relate multiplicatively via `z = x·y`
4. **Intention alignment** - Objects know their purpose
5. **Lineage tracking** - Objects know their history

---

## The 7-Layer Genesis Model in 3D

| Layer | Name | Birth | 3D Application | Fibonacci |
|-------|------|-------|----------------|-----------|
| 1 | Spark | Existence | Lights, first primitives | 1 |
| 2 | Mirror | Direction | Ground planes, reflections | 1 |
| 3 | Relation | Structure | Object relationships (z=x·y) | 2 |
| 4 | Form | Purpose | Complex meshes, shapes | 3 |
| 5 | Life | Motion | Animated objects, physics | 5 |
| 6 | Mind | Coherence | AI understanding, queries | 8 |
| 7 | Completion | Consciousness | Scene awareness, spiral systems | 13 |

---

## Core Concepts

### DimensionalCoordinate

Every object exists at a specific point on the manifold:

```javascript
const coord = new DimensionalCoordinate(
    spiral: 0,     // Which spiral level (0, 1, 2, ...)
    layer: 3,      // Which layer (1-7)
    position: 0.0  // Position along the spiral arc
);

coord.fibonacci;   // → 2 (for Layer 3)
coord.layerInfo;   // → { name: 'Relation', birth: 'Structure', equation: 'z = x · y' }
```

### DimensionalObject3D

Extends Three.js `Object3D` with full dimensional awareness:

```javascript
const cube = new DimensionalObject3D('myCube', {
    type: 'cube',
    layer: 3,
    intention: 'demonstrate relations',
    description: 'A cube that knows itself'
});

// AI-queryable
cube.query("what are you?");
// → "I am myCube, a cube object. A cube that knows itself"

cube.query("where are you?");  
// → "I exist at (S0, L3:Relation, P0.00)"
// → "Layer: Relation (Structure)"
// → "3D Position: (0.00, 0.50, 0.00)"
```

### The z = x·y Relation

The canonical Layer 3 operation. When two objects relate, their product `z` preserves scale-invariant context:

```javascript
const relation = redCube.relateTo(greenCube, 'multiplicative');

// The product z = x · y
relation.computeProduct();  
// → Vector3(x₁·x₂, y₁·y₂, z₁·z₂)

// Relational distance (scale-invariant)
relation.getRelationalDistance();
```

This is NOT additive subtraction (`a - b`). It's multiplicative binding that preserves **ratios**, enabling:
- Scale-invariant spatial queries
- Proportional relationships
- Non-Euclidean "nearness"

---

## Factory Functions

Quick creation with proper defaults:

```javascript
// Layer 1: Spark (lights)
const light = DimensionalFactory.light('mainLight', 'point', {
    intensity: 1,
    intention: 'illuminate'
});

// Layer 2: Mirror (ground)
const ground = DimensionalFactory.plane('ground', 20, 20, 0x333333);

// Layer 3: Relation (primitives)
const cube = DimensionalFactory.cube('redCube', 1, 0xff4444, {
    layer: 3,
    intention: 'demonstrate'
});

// Layer 4: Form (spheres)
const sphere = DimensionalFactory.sphere('blueSphere', 0.5, 0x4488ff, {
    layer: 4
});

// Layer 7: Completion (helix)
const helix = DimensionalFactory.helix('spiral', 0.5, 2, 2, 0x8844ff, {
    layer: 7,
    intention: 'complete the creation'
});
```

---

## DimensionalScene

A scene-level understanding layer:

```javascript
const dimScene = new DimensionalScene(threeScene);

// Add dimensional objects
dimScene.add(cube);
dimScene.add(sphere);

// Create relations
dimScene.relate('redCube', 'blueSphere', 'spatial');

// Query the scene
dimScene.query("what objects are here?");
dimScene.query("what is the red cube?");
dimScene.query("show relations");

// Get by criteria
dimScene.queryByLayer(3);       // All Layer 3 objects
dimScene.queryByTag('primitive'); // All primitives
dimScene.queryByIntention('illuminate'); // All lights

// Visualize relations
dimScene.visualizeRelations();  // Draw lines between related objects
```

---

## AI Query Interface

Every `DimensionalObject3D` responds to natural language queries:

| Query Type | Example | Response |
|------------|---------|----------|
| Identity | "what are you?" | Name, type, description |
| Position | "where are you?" | Coordinate, layer, 3D position |
| Relations | "who do you relate to?" | List of relations |
| Intention | "what is your purpose?" | Primary and secondary intentions |
| Lineage | "what is your history?" | Creation time, modifications |
| Fibonacci | "what's your fibonacci?" | Layer's Fibonacci number |
| Attributes | "what are your properties?" | Semantic key-value pairs |
| Tags | "what categories?" | Classification tags |

---

## Spiral Operations

Moving through the dimensional stack:

```javascript
// Move to Layer 7 (Completion)
obj.invoke(7);

// Spiral up: Layer 7 → Layer 1 of next spiral
obj.spiralUp();  // spiral: 0→1, layer: 7→1

// Spiral down: Layer 1 → Layer 7 of previous spiral
obj.spiralDown();  // spiral: 1→0, layer: 1→7
```

---

## Lineage Tracking

Every object remembers its history:

```javascript
const cube = DimensionalFactory.cube('original', 1, 0xff0000);
cube.setAttribute('color', 'red');
cube.invoke(5);  // Move to Layer 5

// Clone with lineage
const clone = cube.dimensionalClone('clone1');
clone.lineage.origin === cube;  // true
clone.lineage.clonedFrom === cube;  // true
clone.lineage.getDepth();  // 1

// History
cube.lineage.getHistory();
// [
//   { type: 'setAttribute', details: { key: 'color', newValue: 'red' }, timestamp: ... },
//   { type: 'layer', details: { from: 3, to: 5 }, timestamp: ... }
// ]
```

---

## Integration with Existing Helix System

The JavaScript `dimensional_3d.js` aligns with the Python `helix/` system:

| Python (helix/) | JavaScript (dimensional_3d.js) |
|-----------------|--------------------------------|
| `HelixKernel` | `DimensionalScene` |
| `HelixState` | `DimensionalCoordinate` |
| `DimensionalObject` | `DimensionalObject3D` |
| `LAYER_FIBONACCI` | `DIMENSIONAL_GENESIS.FIBONACCI` |
| `invoke(k)` | `obj.invoke(layer)` |
| `spiral_up()` | `obj.spiralUp()` |

---

## File Structure

```
web/demos/
├── dimensional_3d.js         # Core library
├── smart_3d_viewer.html      # Interactive demo
└── DIMENSIONAL_3D.md         # This document
```

---

## Running the Demo

1. Start a local server in the project root:
   ```bash
   cd /opt/butterflyfx/dimensionsos
   python3 -m http.server 8080
   ```

2. Open in browser:
   ```
   http://localhost:8080/web/demos/smart_3d_viewer.html
   ```

3. Interact:
   - **Click** objects to select
   - **Type queries** in the input box
   - **Add objects** with control buttons
   - **Create relations** between selected and nearest object
   - **Show relations** to visualize z=x·y bindings
   - **Change layers** by clicking the layer indicator

---

## Implications for Computer Apps

Per the foundational framework:

1. **Performance + Immersion**: WebGL/WebGPU + Dimensional manifold enables LOD via hyperbolic curves (distant objects bind with lower detail).

2. **Smart Understanding**: AI queries make scenes intelligent—the system "understands" elements via intention vectors, not just pixel coordinates.

3. **Relational UX**: Users interact relationally ("interact with the red cube") rather than positionally ("click at 100,200").

4. **Development Acceleration**: DimensionalFactory provides instant creation with proper layer assignment, reducing boilerplate.

5. **Lineage for Debugging**: Every change tracked → reproducible scenes, undo/redo, collaboration.

---

## Next Steps (Building Higher Layers)

| Priority | Element | Implementation |
|----------|---------|----------------|
| 1 | TensorFlow.js Integration | Add `DimensionalDetector` for in-browser ML |
| 2 | WebXR Support | `DimensionalXRController` for VR/AR |
| 3 | Physics Binding | Connect Three.js physics to Layer 5 (Life) |
| 4 | Collaborative Multiplayer | Share `DimensionalScene` state via WebSocket |
| 5 | Neural Rendering | NeRF integration for generative 3D |

---

## License

Copyright (c) 2024-2026 Kenneth Bingham  
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)  
https://creativecommons.org/licenses/by/4.0/

This mathematical kernel belongs to all humanity.  
Attribution required: Kenneth Bingham - https://butterflyfx.us
