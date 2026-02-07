# ButterflyFx Dimensional Computation Framework

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

## The 15 Laws

1. **Substrates are the source of truth**
2. **Manifolds are shapes of substrates**
3. **Lenses provide context**
4. **SRLs define connections**
5. **Immutability is absolute**
6. **No hard-coded dynamic values**
7. **No simulation or estimation in runtime**
8. **Everything fits in 64 bits**
9. **Invocation reveals truth**
10. **Python is the interface, not the ontology**
11. **Human-readable code is allowed**
12. **No brute force**
13. **Non-duplication**
14. **Dimensional containment**
15. **AI must never fabricate substrate behavior**

## Directory Structure

```
butterflyfx/
├── kernel/              # Inner Sanctum (pure math)
│   ├── substrate.py     # Substrate identity
│   ├── manifold.py      # Dimensional expressions
│   ├── lens.py          # Context projections
│   ├── delta.py         # Change representation
│   ├── dimensional.py   # Promotion mechanics
│   └── srl.py           # Resource locators
├── core/                # Bridge Layer
│   ├── gateway.py       # Sole Kernel accessor
│   ├── invocation.py    # Truth revelation
│   ├── translator.py    # External → math
│   └── validator.py     # Law enforcement
├── interface/           # External Access
│   ├── dto.py           # Transfer objects
│   ├── human.py         # Human-friendly API
│   ├── machine.py       # Binary protocols
│   └── ai.py            # AI instruction sets
├── sanctum.py           # Layer boundary enforcement
└── ai_directives.md     # Model operating rules
```

## Author
Kenneth Bingham

## License
Proprietary - ButterflyFx Dimensional Computation Model
