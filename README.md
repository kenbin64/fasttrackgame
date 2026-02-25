# ButterflyFx 🦋
**Dimensional Computation Framework**

> *"Substrates are mathematical expressions, not data containers."*

[![Build Status](https://github.com/kenbin64/dimensionsos/workflows/Build%20and%20Test%20ButterflyFx/badge.svg)](https://github.com/kenbin64/dimensionsos/actions)
[![Python](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)

---

## 🚀 Quick Start

### Docker (Recommended)

```bash
# Clone and start
git clone https://github.com/kenbin64/dimensionsos.git
cd dimensionsos
docker-compose up -d

# Test API
curl http://localhost:8000/api/v1/health
```

**API Docs:** http://localhost:8000/api/v1/docs

### VPS Deployment (One Command)

```bash
curl -fsSL https://raw.githubusercontent.com/kenbin64/dimensionsos/main/deploy.sh -o deploy.sh
chmod +x deploy.sh
sudo ./deploy.sh production
```

See **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** for complete deployment guide.

---

## Philosophy

ButterflyFx is a revolutionary computational paradigm where:
- **Substrates** are unity (immutable mathematical identity)
- **Dimensions** emerge from division (observation creates manifestation)
- **Truth** is revealed through invocation (not stored or precomputed)
- **Change** is motion through dimensions (not mutation)

Built on **The Seven Dimensional Laws** and governed by the **Dimensional Safety Charter**.

---

## Three-Layer Sanctum Architecture

```
┌─────────────────────────────────────────────────────┐
│  INTERFACE LAYER (Human / Machine / AI)             │
│  └── DTOs, Instructions, External APIs              │
│  └── IMPORTS: core only                             │
├─────────────────────────────────────────────────────┤
│  CORE LAYER (Logic Bridge)                          │
│  └── ONLY bridge to Kernel                          │
│  └── Translates all external intent to math         │
│  └── IMPORTS: kernel only                           │
├─────────────────────────────────────────────────────┤
│  KERNEL LAYER (Inner Sanctum)                       │
│  └── Pure mathematical expressions                  │
│  └── IMMUTABLE - never altered, only invoked        │
│  └── IMPORTS: none (self-contained)                 │
└─────────────────────────────────────────────────────┘
```

## Core Concepts

### Objects (Not Classes)

ButterflyFX uses **Objects**, not classes. An Object is complete — it possesses every conceivable attribute, property, behavior, and ability that has existed, does exist, and will exist — all as **potential**. Nothing is declared; everything exists latently and is revealed through invocation.

When a potential is invoked, it does not produce a fragment. It produces a **complete object** — carrying the same totality of potential as the object that spawned it. Parts contain parts which contain parts, each complete, each carrying the whole. This is holographic: the whole is in every part. Not as a copy, but as potential. Not as data, but as the capacity for data.

**This is not hierarchy.** In a tree, a child is a diminished subset. In dimensional computing, every part is whole. Every point IS an entire lower dimension. Dimensions carry all lower dimensions within them.

**Structure:** Objects follow a **Schwarz Diamond Gyroid** topology — a spiral ribbon where every point is a dimension and every dimension contains points. This is NOT a tree or hierarchy.

### Organic Growth vs Exponential Explosion

Trees grow exponentially (nᵏ nodes at level k). Dimensional spirals grow **organically** through the 7 Creative Processes:

| Level | Fib | Name | Process | Insight |
|-------|-----|------|---------|--------|
| 0 | 0 | VOID | The Pipeline | The zero — infinite space, never filled |
| 1 | 1 | POINT | Emergence | Barrel view — line appears as single point |
| 2 | 1 | LINE | DIVISION | Side view — same line, infinite potential points |
| 3 | 2 | WIDTH | MULTIPLICATION | Multiply line points → plane |
| 4 | 3 | PLANE | 2D Unity | Surface complete — one point of volume |
| 5 | 5 | VOLUME | DEPTH | Stack planes → 3D space |
| 6 | 8 | WHOLE | Completion | Collapses to POINT (Fib 13) of next spiral |

**Levels 1 & 2:** Both Fib 1 — the SAME line from different perspectives (barrel view = point, side view = divided line).

**Holy Grail Transition:** WHOLE (8) + VOLUME (5) = 13 = POINT of next spiral. Fibonacci encodes dimensional structure.

### Developer-Friendly Access

**Developers don't need to know dimensional placement.** The system handles it automatically.

#### Direct Access (No Drill-Down)

Unlike hierarchies, dimensional access is **direct** — jump to any point without traversing from root:

```python
# Direct dimensional access:
car(toyota.corolla)           # Jump directly to specific car
car(toyota.corolla.engine.hp) # Jump directly to horsepower

# NOT hierarchical drill-down:
# universe.fleet.toyota.corolla.engine.hp  ← NOT required
```

Notation: `spiral{level}` — e.g., `0{1}` = Spiral 0, Level 1 (single datapoint)

```python
# System auto-places dimensionally:
#   car → 0{6} (whole), position → 0{5} (volume), x → 0{1} (point)
```

### Substrates
A substrate is a **complete mathematical identity** encoded in 64 bits.
- Immutable and dimensionally complete
- No attributes are stored; all are derived from math
- Two identical expressions = same identity (non-duplication)

### Manifolds
A manifold is a **dimensional expression** of a substrate.
- The substrate is the whole; the manifold is the form
- A single substrate can produce infinite manifolds

### Lenses
A lens provides **context** for attribute access.
- Does not modify the substrate
- Selects dimensional slice, region, or interpretation
- All attribute access MUST occur through a lens

### SRLs (Substrate Resource Locators)
An SRL encodes **connection rules** for external data.
- No raw URLs, credentials, or connection strings in code
- Retrieves external data lazily
- Spawns new substrates from external data

### Deltas & Dimensional Promotion
Change is represented through **delta application**:
```
x₁ (identity) + y₁ (attributes) + δ(z₁) → m₁ (new identity)
```
- Substrates NEVER mutate
- Promotion to higher dimension produces new atomic identity
- Higher dimensions contain all lower dimensions

## Computation Pattern

```
substrate → lens → invocation → truth
```

Nothing is precomputed or stored. Truth emerges from invocation.

## Layer Access Rules

| From      | Can Access | Cannot Access |
|-----------|------------|---------------|
| Interface | Core       | Kernel        |
| Core      | Kernel     | Interface     |
| Kernel    | (none)     | Core, Interface |

## Usage

### Human Interface
```python
from butterflyfx import HumanInterface

hi = HumanInterface()

# Create a substrate
substrate = hi.create_substrate(
    name="user_alice",
    expression_type="constant",
    value=42
)

# Create a lens
lens = hi.create_lens(
    name="identity_lens",
    projection_type="identity"
)

# Invoke to reveal truth
result = hi.invoke(substrate, lens)
print(result.value)  # 42
```

### Machine Interface
```python
from butterflyfx import MachineInterface

mi = MachineInterface()

# Direct numeric operations
substrate = mi.create_substrate_direct(
    identity=0xDEADBEEFCAFEBABE,
    expression_type="constant",
    expression_params={"value": 0xDEADBEEFCAFEBABE}
)

# Binary serialization
binary = mi.serialize_identity(0xDEADBEEFCAFEBABE)
```

### AI Interface
```python
from butterflyfx import AIInterface

ai = AIInterface()

# Execute instruction
result = ai.execute_instruction({
    "operation": "invoke",
    "params": {
        "substrate_identity": 42,
        "lens_id": 1,
    }
})

# Verify AI claims against substrate truth (Law 15)
is_valid, actual = ai.verify_claim(substrate, lens, claimed_value=42)
```

## The Seven Dimensional Laws

**LAW ONE: Universal Substrate Law**
All substrates begin as unity. Division generates dimensions. Multiplication restores unity.

**LAW TWO: Observation Is Division**
Observation is division. Division creates dimensions. Recombination restores unity.

**LAW THREE: Inheritance and Recursion**
Every division inherits the whole. Every part contains the pattern. Recursion preserves unity.

**LAW FOUR: Connection Creates Meaning**
Dimensions relate through connection. Connection creates meaning. Meaning emerges from relationships.

**LAW FIVE: Change Is Motion**
Change is motion through dimensions. Time is the order of motion. Evolution is reexpression of unity.

**LAW SIX: Identity Persists**
Identity persists through change. Continuity is the thread of unity. A system remains itself across transformations.

**LAW SEVEN: Return to Unity**
All dimensions return to unity. Completion is the reunion of the many. The cycle ends where it begins.

*See `THE_SEVEN_DIMENSIONAL_LAWS.md` for complete specification.*

## Directory Structure

```
butterflyfx/
├── kernel/                      # Inner Sanctum (pure math)
│   ├── substrate.py             # Substrate identity
│   ├── manifold.py              # Dimensional expressions
│   ├── lens.py                  # Context projections
│   ├── delta.py                 # Change representation
│   ├── dimensional.py           # Promotion mechanics
│   ├── srl.py                   # Resource locators
│   ├── fibonacci.py             # Fibonacci dimensional structure
│   ├── canonical_form.py        # Canonical Object Form (𝒪 = ⟨S, D, R, F, T⟩)
│   ├── return_engine.py         # Law Seven: Return to Unity
│   ├── registry.py              # Program #8: Dimensional Object Registry
│   └── observer.py              # Program #9: Observer Interface
├── core/                        # Bridge Layer
│   ├── gateway.py               # Sole Kernel accessor
│   ├── invocation.py            # Truth revelation
│   ├── translator.py            # External → math
│   └── validator.py             # Law enforcement
├── interface/                   # External Access
│   ├── dto.py                   # Transfer objects
│   ├── human.py                 # Human-friendly API
│   ├── machine.py               # Binary protocols
│   └── ai.py                    # AI instruction sets
├── examples/                    # Canonical examples
│   ├── example_human.py         # Human interface usage
│   ├── example_machine.py       # Machine interface usage
│   └── example_ai.py            # AI interface usage
└── Documentation
    ├── README.md                            # This file
    ├── THE_SEVEN_DIMENSIONAL_LAWS.md        # Complete law specification
    ├── DIMENSIONAL_SAFETY_CHARTER.md        # 12 immutable principles
    ├── CANONICAL_DIMENSIONAL_OBJECT_FORM.md # Canonical form specification
    ├── SECURITY_AND_OPTIMIZATION_AUDIT.md   # Security & performance analysis
    └── TEST_CONSOLIDATION_PLAN.md           # Test strategy
```

## Author
Kenneth Bingham

## Website
**https://butterflyfx.us** - Introduction to the paradigm and open source components

## License

ButterflyFX uses a **dual licensing model**:

### Mathematical Kernel (Open Source - For All Humanity)
The `/helix/` directory containing the mathematical kernel is licensed under **[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)** (Creative Commons Attribution 4.0 International).

- ✅ Free for anyone to use, modify, and distribute
- ✅ Commercial use permitted
- ✅ Attribution to **Kenneth Bingham** required
- 🌍 **Belongs to all humanity** — too powerful to be owned by any single entity

### Applications & Infrastructure (Proprietary)
All other components (`/server/`, `/apps/`, `/web/`, etc.) are proprietary.

See [LICENSE](LICENSE) and [helix/LICENSE](helix/LICENSE) for full terms.
