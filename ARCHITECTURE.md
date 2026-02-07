# ButterflyFx Architecture: Core-Kernel Separation

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        EXTERNAL WORLD                           │
│   (Python code, Human input, Machine/AI instructions)          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                           CORE                                  │
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│   │  Translator │  │  Validator  │  │  Invocator  │            │
│   │             │  │             │  │             │            │
│   │ Python →    │  │ Enforce     │  │ Execute     │            │
│   │ Kernel Math │  │ 15 Laws     │  │ Expressions │            │
│   └─────────────┘  └─────────────┘  └─────────────┘            │
│                              │                                  │
│                    ┌─────────────────┐                         │
│                    │  KernelGateway  │  ← ONLY ACCESS POINT    │
│                    │   (Singleton)   │                         │
│                    └─────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          KERNEL                                 │
│                       (Pure Math)                               │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                    PRIMITIVES                            │  │
│   │                                                          │  │
│   │  SubstrateIdentity   64-bit identity (x₁)               │  │
│   │  Substrate           Expression + Identity               │  │
│   │  Lens                Projection function (y₁ derivation) │  │
│   │  Delta               Change encoding (z₁)               │  │
│   │  Dimension           Level of containment               │  │
│   │  Manifold            Shape of substrate                 │  │
│   │  SRL                 Substrate Reference Locator        │  │
│   │                                                          │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                    OPERATIONS                            │  │
│   │                                                          │  │
│   │  promote(x₁, y₁, z₁) → m₁   (dimensional promotion)     │  │
│   │  invoke(substrate, lens) → value   (truth revelation)    │  │
│   │                                                          │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│   NO EXTERNAL ACCESS - Core is the ONLY gateway                │
└─────────────────────────────────────────────────────────────────┘
```

## Kernel Layer

The Kernel is **pure mathematical substrate operations**:

- **No Python logic** - only mathematical expressions
- **No conditionals** - deterministic transformations
- **No I/O** - receives input only from Core
- **No state** - everything is immutable
- **No external imports** - self-contained math

### Kernel Primitives

| Primitive | Description | Size |
|-----------|-------------|------|
| `SubstrateIdentity` | 64-bit atomic identity | 8 bytes |
| `Substrate` | Identity + Expression | 8 bytes + fn |
| `Lens` | Projection function | 8 bytes + fn |
| `Delta` | Change encoding | 8 bytes |
| `Dimension` | Containment level | int |
| `Manifold` | Shape of substrate | 24 bytes |

### Kernel Operations

```
promote(x₁, y₁, z₁) → m₁
```
The ONLY way change occurs. No mutation, only promotion to new identity.

## Core Layer

The Core is the **bridge between external world and Kernel**:

### Responsibilities

1. **Translation**: Convert Python/human code → Kernel math
2. **Validation**: Enforce the 15 Laws before any operation
3. **Invocation**: Execute substrate→lens→truth pipeline
4. **Gateway**: Single point of Kernel access (no bypassing)

### Components

| Component | Role |
|-----------|------|
| `KernelGateway` | Singleton guard - ONLY Kernel access point |
| `Translator` | Python → Kernel math conversion |
| `Validator` | Law enforcement before operations |
| `Invocator` | Execute expressions, reveal truth |

## Boundary Enforcement

```python
# FORBIDDEN - Direct kernel access
from kernel.substrate import Substrate  # ❌ NO

# REQUIRED - Access through Core
from core import KernelGateway
gateway = KernelGateway()
substrate = gateway.create_substrate(...)  # ✓ YES
```

## Data Flow

```
Python Code
    │
    ▼
Translator.translate(python_dict) → KernelExpression
    │
    ▼
Validator.validate(expression) → None or ValidationError
    │
    ▼
KernelGateway.create_substrate(expression) → Substrate
    │
    ▼
Invocator.invoke(substrate, lens) → InvocationResult
    │
    ▼
Python receives 64-bit truth value
```

## The 15 Laws Enforced by Core

1. Dimensional Supremacy
2. Unified Representation
3. Non-Duplication
4. No Collisions
5. Immutability
6. No Hard-Coded Dynamic Values
7. All Attributes as Expressions
8. 64-bit Atomic Identity
9. Truthful Invocation
10. No State Precomputation
11. No Brute Force
12. No Fabrication
13. Core-Kernel Separation
14. Dimensional Promotion Only
15. Manifold Discovery
