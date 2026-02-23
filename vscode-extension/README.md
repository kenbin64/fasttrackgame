# Dimensional VPS Optimizer

A VS Code extension that applies the **Dimensional Computing** paradigm to optimize your VPS resources.

## Features

- **7-Layer Genesis Model** (SPARK → COMPLETION) with Fibonacci alignment
- **z = x·y multiplicative binding** for scale-invariant resource optimization
- **Intention vectors** for priority-driven decisions (energy vs performance)
- **Lineage tracking** for full explainability of optimizations
- **Real-time dashboard** with live VPS metrics

## The 7 Kernel Operations

| Layer | Operation | Fibonacci | Description |
|-------|-----------|-----------|-------------|
| 1. Spark | LIFT | 1 | Convert raw VPS data to Dimensional Objects |
| 2. Mirror | MAP | 1 | Project onto manifold (identity vectors) |
| 3. Relation | BIND | 2 | Multiplicative z = x·y binding |
| 4. Form | NAVIGATE | 3 | Move through dimensional space |
| 5. Life | TRANSFORM | 5 | Apply semantic transformations |
| 6. Mind | MERGE | 8 | Combine multiple objects |
| 7. Completion | RESOLVE | 13 | Extract final result with lineage |

## Commands

Open Command Palette (`Ctrl+Shift+P`) and type "Dimensional":

- **Dimensional: Lift VPS Data** - Collect and lift VPS metrics
- **Dimensional: Optimize Resources** - Run optimization analysis
- **Dimensional: Show Dashboard** - Open real-time monitoring dashboard
- **Dimensional: Bind Processes** - Merge process objects
- **Dimensional: Navigate Layers** - Explore the 7 layers
- **Dimensional: Resolve Lineage** - View operation history

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `dimensionalVPS.pythonPath` | `python3` | Python interpreter path |
| `dimensionalVPS.helixPath` | `/opt/butterflyfx/dimensionsos` | Path to helix package |
| `dimensionalVPS.refreshInterval` | `5000` | Dashboard refresh (ms) |
| `dimensionalVPS.intentionPriority` | `balanced` | `energy`, `performance`, or `balanced` |

## Installation

### From Source

```bash
cd vscode-extension
npm install
npm run compile
vsce package
# Install the .vsix file via VS Code: Extensions → ... → Install from VSIX
```

### Development

```bash
cd vscode-extension
npm install
# Press F5 in VS Code to launch Extension Development Host
```

## The Dimensional Computing Paradigm

### Core Concept: z = x·y

Every VPS resource is lifted into a **Dimensional Object** with:
- **Identity Vector** `[x, y]` where `z = x * y` (the "binding value")
- **Intention Vector** defining optimization priorities
- **Semantic Payload** containing the actual data
- **Lineage Graph** tracking all transformations

### Why This Improves Your VPS

1. **Efficiency**: Scale-invariant bindings optimize resource graphs
2. **Smart Orchestration**: Fibonacci-layered task stacking
3. **Explainability**: Lineage graphs trace "why" decisions were made
4. **Low Overhead**: HDC-style geometric operations

### Golden Ratio (φ)

The extension uses φ = 1.618... for natural scaling during transformations, ensuring harmonic resource allocation aligned with natural patterns.

## Integration with Helix

This extension is designed to work with the **DimensionsOS helix package**:

```python
from helix import DimensionalKernel, Layer, DimensionalObject

kernel = DimensionalKernel()
obj = kernel.lift(vps_data)
optimized = kernel.transform(obj, lambda x: analyze(x))
result = kernel.resolve(optimized)
```

## License

MIT License - ButterflyFX
