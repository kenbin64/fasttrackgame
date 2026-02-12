# ButterflyFX Kernel + Substrate Specification

## Language-Agnostic Formal Specification v1.0

**Status:** Draft  
**Date:** February 2026  
**Authors:** ButterflyFX Project

---

## Abstract

This document specifies the ButterflyFX Helix Kernel and Manifold Substrate as abstract, language-agnostic components. Any implementation conforming to this specification will exhibit the core ButterflyFX properties: non-iterative dimensional navigation, lazy materialization, and bounded complexity per spiral.

---

## 1. HELIX KERNEL FORMAL SPECIFICATION

### 1.1 Core Concepts

#### Helix State

**Definition:**  
A helix state is an ordered pair $(s,\ell)$.

**Components:**

| Component | Type | Domain | Interpretation |
|-----------|------|--------|----------------|
| Spiral index $s$ | integer | $\mathbb{Z}$ | Which "turn" of the helix |
| Level $\ell$ | integer | $\{0,1,2,3,4,5,6\}$ | Dimensional stage within spiral |

#### Level Semantics

| Level | Name | Semantics |
|-------|------|-----------|
| 0 | Potential | Nothing instantiated, pure possibility |
| 1 | Point | Single instantiation |
| 2 | Length | Linear extension |
| 3 | Width | 2D extension |
| 4 | Plane | Surface completeness |
| 5 | Volume | 3D existence |
| 6 | Whole | Complete entity, ready for next spiral |

#### Formal State Space

$$\mathcal{H} = \{(s,\ell) \mid s \in \mathbb{Z},\ \ell \in \{0,\dots,6\}\}$$

---

### 1.2 Kernel Operations

The kernel defines a small, closed set of operations on $\mathcal{H}$. These are **pure state transitions**.

Let $(s,\ell) \in \mathcal{H}$.

#### Operation 1: INVOKE

**Name:** `INVOKE(k)`

**Parameter:**  
- $k \in \{0,\dots,6\}$ (target level)

**Transition:**
$$INVOKE_k(s,\ell) = (s,k)$$

**Semantics:**  
Jump directly to level $k$ within the current spiral.

---

#### Operation 2: SPIRAL_UP

**Name:** `SPIRAL_UP`

**Precondition:** $\ell = 6$ (must be at Whole)

**Transition:**
$$SPIRAL\_UP(s,6) = (s+1,0)$$

**Semantics:**  
Move from Whole of current spiral to Potential of next spiral.

---

#### Operation 3: SPIRAL_DOWN

**Name:** `SPIRAL_DOWN`

**Precondition:** $\ell = 0$ (must be at Potential)

**Transition:**
$$SPIRAL\_DOWN(s,0) = (s-1,6)$$

**Semantics:**  
Move from Potential of current spiral to Whole of previous spiral.

---

#### Operation 4: COLLAPSE

**Name:** `COLLAPSE`

**Precondition:** None

**Transition:**
$$COLLAPSE(s,\ell) = (s,0)$$

**Semantics:**  
Return all instantiated structure in this spiral to Potential.

---

### 1.3 Kernel as Labeled Transition System

Formally, the Helix Kernel is:

**States:** $\mathcal{H}$

**Operations:**
$$\Sigma = \{INVOKE_k \mid k \in \{0,\dots,6\}\} \cup \{SPIRAL\_UP, SPIRAL\_DOWN, COLLAPSE\}$$

**Transition function:**
$$\delta: \mathcal{H} \times \Sigma \rightarrow \mathcal{H}$$

defined by the rules in Section 1.2.

#### Key Property: Bounded Dimensional Complexity

- For any fixed spiral $s$, the number of distinct levels is 7.
- Any sequence that visits each level at most once has length ≤ 7.
- Therefore, **dimensional navigation per spiral is bounded by constant 7**.

$$O(levels\ per\ spiral) = O(7) = O(1)$$

---

### 1.4 Kernel Invariants

Any conforming implementation MUST respect these invariants:

#### I1 — Valid State

At all times, $\ell \in \{0,\dots,6\}$.

#### I2 — Spiral Up/Down Constraints

- `SPIRAL_UP` is only valid when $\ell = 6$.
- `SPIRAL_DOWN` is only valid when $\ell = 0$.

Violation of preconditions is an error state.

#### I3 — Collapse Idempotence

Applying `COLLAPSE` multiple times does not change state after the first:

$$COLLAPSE(COLLAPSE(s,\ell)) = COLLAPSE(s,\ell) = (s,0)$$

#### I4 — Invoke Idempotence Per Level

Invoking the same level twice yields the same state:

$$INVOKE_k(INVOKE_k(s,\ell)) = INVOKE_k(s,\ell) = (s,k)$$

#### I5 — Spiral Reversibility

$$SPIRAL\_DOWN(SPIRAL\_UP(s,6)) = SPIRAL\_DOWN(s+1,0) = (s,6)$$

Spiral up followed by spiral down returns to original state.

---

## 2. MANIFOLD SUBSTRATE AND TOKEN MODEL

### 2.1 Manifold of Potential

#### Definition

**Manifold $M$:**  
A topological space that locally resembles $\mathbb{R}^n$ for some $n$.

**Interpretation:**  
The space of all potential tokens — nothing here is necessarily instantiated.

**Note:** The dimension $n$ is not fixed by this specification. Implementations may choose $n$ based on:
- Embedding dimension
- Semantic space dimensionality
- Application requirements

---

### 2.2 Tokens

A **token** is the fundamental unit of "something that could exist".

#### Token Definition

$$\tau = (x, \sigma, \pi)$$

#### Token Components

| Component | Type | Domain | Interpretation |
|-----------|------|--------|----------------|
| Location $x$ | point in manifold | $x \in M$ | Geometric or semantic position |
| Signature $\sigma$ | finite set or bitmask | subset of $\{0,\dots,6\}$ | Which helix levels this token can inhabit |
| Payload $\pi$ | abstract | any | What is revealed when instantiated |

#### Token Set

$$\mathcal{T} = \{\tau_i\}$$

**Interpretation:** All potential entities that could be materialized by the kernel.

---

### 2.3 Substrate Structure

The **substrate** is the combination of:
- the manifold
- the tokens
- the relations between them

#### Formal Definition

$$\mathcal{S} = (M, \mathcal{T}, \mathcal{R})$$

| Component | Type | Description |
|-----------|------|-------------|
| $M$ | manifold | Space of potential |
| $\mathcal{T}$ | set of tokens | All potential entities |
| $\mathcal{R}$ | relations | Connections between tokens |

#### Relation Types

$\mathcal{R}$ can encode:
- **Geometric relations:** distance, neighborhoods, clusters
- **Semantic relations:** is-part-of, depends-on, similar-to
- **Causal relations:** causes, enables, blocks
- **Temporal relations:** before, after, concurrent

No assumption is made about how $\mathcal{R}$ is stored — only that it exists conceptually.

---

### 2.4 Materialization Function

The kernel must be able to query the substrate:

> "Given helix state $(s,\ell)$, what becomes real?"

#### Definition

**Materialization $\mu$:**

$$\mu: \mathcal{H} \rightarrow \mathcal{P}(\mathcal{T})$$

where $\mathcal{P}(\mathcal{T})$ is the power set of $\mathcal{T}$.

**Interpretation:**  
For helix state $(s,\ell)$, $\mu(s,\ell)$ returns tokens that:
- are relevant to spiral $s$, and
- are compatible with level $\ell$ via their signature $\sigma$

#### Constraints on $\mu$

**M1 — Signature Compatibility:**  
If $\tau \in \mu(s,\ell)$, then $\ell \in \sigma_\tau$.

A token can only materialize at levels permitted by its signature.

**M2 — Spiral Scoping (OPTIONAL):**  
Implementations MAY scope tokens to specific spirals (episodes, contexts, sessions).

**M3 — Empty Potential:**  
$\mu(s,0) = \emptyset$ or returns only tokens with $0 \in \sigma$.

At Potential level, minimal or no tokens materialize.

---

### 2.5 Substrate API

Any conforming implementation MUST provide:

#### Required Operations

**1. Token Registration**

```
REGISTER_TOKEN(τ)
```

- **Input:** token $\tau = (x,\sigma,\pi)$
- **Effect:** adds $\tau$ to $\mathcal{T}$, updates $\mathcal{R}$ as needed
- **Returns:** token identifier

**2. Materialization Query**

```
TOKENS_FOR_STATE(s, level)
```

- **Input:** helix state $(s,\ell)$
- **Output:** $\mu(s,\ell) \subseteq \mathcal{T}$
- **Complexity:** Implementation-dependent, but kernel treats as $O(1)$

#### Optional Operations

**3. Relation Query**

```
RELATED(τ, relation_type)
```

- **Input:** token $\tau$, relation type from $\mathcal{R}$
- **Output:** set of related tokens

**4. Nearest Query**

```
NEAREST(x, k)
```

- **Input:** point $x \in M$, count $k$
- **Output:** $k$ nearest tokens by manifold distance

**5. Release**

```
RELEASE_MATERIALIZED(s)
```

- **Input:** spiral $s$
- **Effect:** marks all materialized tokens in spiral $s$ as potential again

---

### 2.6 Kernel–Substrate Contract

#### The Kernel NEVER:
- Iterates over all tokens
- Scans the manifold
- Walks relations manually
- Accesses raw bytes

#### The Kernel ONLY:
- Transitions between helix states via `INVOKE`, `SPIRAL_UP`, `SPIRAL_DOWN`, `COLLAPSE`
- Calls substrate to materialize tokens for current state

#### The Substrate:
- Guarantees `TOKENS_FOR_STATE(s, level)` implements $\mu(s,\ell)$
- Is free to implement $\mu$ internally however it wants
- Hides all complexity of indexing, searching, caching

#### Contract Formalization

```
INVARIANT: kernel_does_not_iterate
  FORALL operations op IN kernel.operations:
    op.complexity_in_tokens = O(1)
    
INVARIANT: substrate_provides_materialization
  FORALL states (s,ℓ) IN H:
    substrate.TOKENS_FOR_STATE(s,ℓ) = μ(s,ℓ)

INVARIANT: tokens_are_lazy
  FORALL tokens τ IN T:
    τ.payload.state = UNREALIZED until materialized
```

---

## 3. EXAMPLE SCENARIOS

### 3.1 Example: CAR Entity

**Tokens:**

| Token ID | Location $x$ | Signature $\sigma$ | Payload $\pi$ |
|----------|-------------|-------------------|---------------|
| car_001 | (0.5, 0.5, 0.8) | {6} | Car definition |
| engine_001 | (0.4, 0.5, 0.7) | {5} | Engine data |
| transmission_001 | (0.5, 0.6, 0.7) | {5} | Transmission data |
| piston_001 | (0.4, 0.5, 0.5) | {4} | Piston specs |
| steel_001 | (0.3, 0.4, 0.3) | {2,3} | Steel properties |
| iron_atom | (0.2, 0.2, 0.1) | {1} | Fe atom |

**Relations $\mathcal{R}$:**

| From | To | Relation |
|------|-----|----------|
| car_001 | engine_001 | has-part |
| car_001 | transmission_001 | has-part |
| engine_001 | piston_001 | has-part |
| piston_001 | steel_001 | made-of |
| steel_001 | iron_atom | contains |

**Scenario:**

```
Initial state: (0, 0)  — Potential

INVOKE(6)
  State: (0, 6)
  μ(0, 6) = {car_001}
  Only the CAR as Whole materializes.

INVOKE(5)
  State: (0, 5)
  μ(0, 5) = {engine_001, transmission_001}
  Parts materialize. CAR remains as context.

INVOKE(4)
  State: (0, 4)
  μ(0, 4) = {piston_001}
  Sub-parts materialize.

COLLAPSE
  State: (0, 0)
  All returns to Potential.
```

**Key insight:** At no point did the kernel iterate through all tokens. It invoked levels and received exactly what was relevant.

---

### 3.2 Example: Database Query

**Traditional SQL:**

```sql
SELECT * FROM cars
JOIN parts ON cars.id = parts.car_id
JOIN materials ON parts.id = materials.part_id
WHERE cars.model = 'Tesla'
```

Problems:
- All tables scanned
- All joins computed
- Result narrowed after traversal

**ButterflyFX equivalent:**

```
INVOKE(6)                    -- Materialize Wholes
  → Returns: Tesla car token

INVOKE(5)                    -- Materialize Volumes (parts)
  → Returns: parts of Tesla

INVOKE(3)                    -- Materialize Widths (materials)
  → Returns: materials of those parts
```

No iteration. No joins. Direct dimensional invocation.

---

### 3.3 Example: AI Memory System

**Spiral mapping:**
- Spiral 0: Current session
- Spiral −1: Previous session
- Spiral −2: Older sessions
- ...

**Level mapping:**
- Level 1: Raw tokens (words)
- Level 2: Snippets (sentences)
- Level 3: Chunks (paragraphs)
- Level 4: Summaries (sections)
- Level 5: Narratives (documents)
- Level 6: Whole (complete context)

**Scenario:**

```
State: (0, 0)  — New session, Potential

User asks about previous conversation.

SPIRAL_DOWN
  State: (-1, 6)
  Previous session's Whole materializes.

INVOKE(4)
  State: (-1, 4)
  Summaries from previous session.

INVOKE(2)
  State: (-1, 2)
  Specific snippets for detail.

SPIRAL_UP
  State: (0, 0)
  Return to current session.
```

**This feels like dream-style jumps:** You're suddenly accessing the summary of yesterday's conversation, then zooming to a specific detail, without iterating through all past messages.

---

## 4. CONFORMANCE REQUIREMENTS

### 4.1 Kernel Conformance

An implementation is **kernel-conformant** if:

1. **State validity:** All states are in $\mathcal{H}$
2. **Operation semantics:** All four operations behave as specified
3. **Invariants hold:** I1–I5 are maintained
4. **No iteration:** Kernel contains no loops over data

### 4.2 Substrate Conformance

An implementation is **substrate-conformant** if:

1. **Token model:** Tokens have $(x, \sigma, \pi)$ structure
2. **Materialization:** `TOKENS_FOR_STATE` implements $\mu$
3. **Signature respect:** M1 constraint holds
4. **Lazy payloads:** $\pi$ not dereferenced until materialization

### 4.3 Full Conformance

An implementation is **ButterflyFX-conformant** if:

1. Kernel-conformant
2. Substrate-conformant
3. Kernel–substrate contract respected

---

## 5. PRIMITIVE UNIT: TOKEN vs BIT

### Why Token, Not Bit

In this model:

| Traditional | ButterflyFX |
|-------------|-------------|
| Primitive: bit | Primitive: token |
| Structure: bytes, rows, objects | Structure: manifold positions |
| Access: iteration, indexing | Access: dimensional invocation |
| Hierarchy: trees, graphs | Hierarchy: helix spirals |

Bits still exist at hardware level, but:
- They are **hidden behind** the manifold + token abstraction
- All higher-level computation expressed via:
  - helix states
  - tokens
  - materialization

This makes the system conceptually more manageable and aligned with the helix model.

---

## 6. SUMMARY

### Kernel

$$K = (\mathcal{H}, \Sigma, \delta)$$

- States: $(s, \ell)$ where $s \in \mathbb{Z}$, $\ell \in \{0..6\}$
- Operations: `INVOKE`, `SPIRAL_UP`, `SPIRAL_DOWN`, `COLLAPSE`
- Complexity: $O(7)$ per spiral

### Substrate

$$\mathcal{S} = (M, \mathcal{T}, \mathcal{R})$$

- Manifold: space of potential
- Tokens: $(x, \sigma, \pi)$
- Materialization: $\mu: \mathcal{H} \rightarrow \mathcal{P}(\mathcal{T})$

### Contract

- Kernel transitions, substrate materializes
- No iteration in kernel
- Lazy realization of payloads

### Core Principle

> **"The motion is the transition, not the traversal."**

---

## APPENDIX A: Formal Notation Reference

| Symbol | Meaning |
|--------|---------|
| $\mathcal{H}$ | Helix state space |
| $(s, \ell)$ | Helix state (spiral, level) |
| $\Sigma$ | Set of kernel operations |
| $\delta$ | Transition function |
| $M$ | Manifold of potential |
| $\mathcal{T}$ | Set of tokens |
| $\tau$ | Individual token |
| $(x, \sigma, \pi)$ | Token components (location, signature, payload) |
| $\mathcal{R}$ | Relations between tokens |
| $\mathcal{S}$ | Substrate $(M, \mathcal{T}, \mathcal{R})$ |
| $\mu$ | Materialization function |
| $\mathcal{P}(\mathcal{T})$ | Power set of tokens |

---

## APPENDIX B: Quick Implementation Checklist

### Kernel Implementation

- [ ] State stored as `(spiral: int, level: int)`
- [ ] `INVOKE(k)` sets level to k
- [ ] `SPIRAL_UP` increments spiral, sets level to 0
- [ ] `SPIRAL_DOWN` decrements spiral, sets level to 6
- [ ] `COLLAPSE` sets level to 0
- [ ] Preconditions enforced for spiral operations
- [ ] No loops over data in kernel

### Substrate Implementation

- [ ] Tokens have id, location, signature, payload
- [ ] Registry for adding tokens
- [ ] `TOKENS_FOR_STATE(s, level)` returns matching tokens
- [ ] Signature filtering implemented
- [ ] Payloads are lazy (not loaded until needed)

### Integration

- [ ] Kernel calls substrate, never iterates directly
- [ ] Materialization returns token sets, not raw data
- [ ] Contract between kernel and substrate documented

---

*End of Specification*
