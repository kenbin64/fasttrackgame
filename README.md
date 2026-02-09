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

## License
Proprietary - ButterflyFx Dimensional Computation Model
