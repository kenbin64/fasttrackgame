# Canonical Dimensional Object Form

## For Programming AIs

This document defines the **pure mathematical contract** for dimensional objects that any programming AI can implement.

---

## The Mathematical Definition

Every object is defined as a **pure mathematical construct**:

```
𝒪 = ⟨S, D, R, F, T⟩
```

Where:

- **S** = substrate (unity, immutable identity)
- **D** = set of dimensions (axes with domains and inheritance)
- **R** = set of relationships (functions between dimensions)
- **F** = manifestation function (pure computation)
- **T** = time or ordering of motion

**No state is stored. All states are computed from this expression.**

---

## 1. Substrate (S)

Unity, immutable, no stored state.

```
S = unity_id
```

It is only an identity, not data.

**Example:**
```python
identity = SubstrateIdentity(0x1234567890ABCDEF)

def expression(**kwargs):
    attr = kwargs.get('attribute', 'identity')
    if attr == 'identity':
        return 0x1234567890ABCDEF
    elif attr == 'mass':
        return 1500.0  # kg
    # ... all attributes computed, not stored

substrate = Substrate(identity, expression)
```

---

## 2. Dimensions (D)

Each dimension is a named axis with a value space and an inheritance rule.

```
D = { d_i | d_i = ⟨name_i, domain_i, inherit_i⟩ }
```

- `name_i` = label such as position, mass, color, role
- `domain_i` = allowed values (type or validation function)
- `inherit_i(S)` = how this dimension derives from the substrate

**Example:**
```python
position = DimensionSpec(
    name="position",
    domain=float,
    inherit=lambda s: s.expression(attribute="position")
)

velocity = DimensionSpec(
    name="velocity",
    domain=float,
    inherit=lambda s: s.expression(attribute="velocity")
)

D = {position, velocity}
```

---

## 3. Relationships (R)

Relationships are functions between dimensions.

```
R = { r_j | r_j = ⟨name_j, inputs_j, outputs_j, f_j⟩ }
```

- `inputs_j ⊆ D` = input dimension names
- `outputs_j ⊆ D` = output dimension names
- `f_j` = function mapping input dimension values to output dimension values

**Example:**
```python
motion = RelationshipSpec(
    name="motion",
    inputs={"position", "velocity", "time"},
    outputs={"position"},
    f=lambda position, velocity, time: position + velocity * time
)

R = {motion}
```

---

## 4. Time and Motion (T)

Time is a parameter that orders change.

```
T ∈ ℝ  or  T ∈ ℤ
```

State at time `t` is not stored, it is computed.

```
state(t) = { d_i(t) }
```

Each `d_i(t)` is derived from:

```
d_i(t) = inherit_i(S) combined with R and t
```

**Example:**
```python
# State at t=0
state_0 = obj.manifest(t=0)

# State at t=10
state_10 = obj.manifest(t=10)

# Original object unchanged
assert obj.time == 0
```

---

## 5. Manifestation Function (F)

The object as experienced is a manifestation of unity through dimensions, relationships, and time.

```
F : (S, D, R, T) → M
```

Where:

- `M` = manifestation such as geometry, behavior, response, view

So:

```
M(t) = F(S, D, R, t)
```

**No state is stored. Everything is recomputed from the expression.**

**Example:**
```python
def manifestation(substrate, dimensions, relationships, time):
    """Compute state from S, D, R, T"""
    state = {}
    
    # Compute base values from substrate
    for dim in dimensions:
        state[dim.name] = dim.inherit(substrate)
    
    # Apply relationships
    for rel in relationships:
        inputs = {name: state[name] for name in rel.inputs if name in state}
        if "time" in rel.inputs:
            inputs["time"] = time
        state[rel.outputs[0]] = rel.f(**inputs)
    
    return state
```

---

## Minimal Form for Programming AI

You can give a programming AI this exact contract:

> **A dimensional object is defined as:**
> 
> ```
> 𝒪 = ⟨S, D, R, F, T⟩
> ```
> 
> where:
> - **S** is an immutable substrate identity
> - **D** is a set of dimensions with domains and inheritance rules
> - **R** is a set of functional relationships between dimensions
> - **T** is a time parameter or ordering index
> - **F** is a pure function that maps `(S, D, R, T)` to a manifestation `M`
> 
> **No state is stored. All states are computed from this expression.**

---

## Complete Example: Car Object

```python
# S - Substrate
car_substrate = create_car_substrate(vin="1HGBH41JXMN109186", year=2024)

# D - Dimensions
dimensions = {
    DimensionSpec("position", float, lambda s: s.expression(attribute="initial_position")),
    DimensionSpec("velocity", float, lambda s: s.expression(attribute="initial_velocity")),
    DimensionSpec("mass", float, lambda s: s.expression(attribute="mass")),
}

# R - Relationships
relationships = {
    RelationshipSpec(
        "motion",
        inputs={"position", "velocity", "time"},
        outputs={"position"},
        f=lambda position, velocity, time: position + velocity * time
    ),
}

# Create canonical object
car = CanonicalObject(
    substrate=car_substrate,
    dimensions=dimensions,
    relationships=relationships,
    manifestation=default_manifestation,
    time=0.0
)

# Manifest at t=10
state = car.manifest(t=10.0)
```

---

## Key Principles

1. **Unity is constant** - The substrate (S) never changes
2. **Dimensions are computed** - Values derived from substrate, not stored
3. **Relationships define interactions** - How dimensions affect each other
4. **Time is a parameter** - Not stored state, just an input to computation
5. **Manifestation is pure** - Same inputs always produce same output
6. **No mutation** - Creating new time creates new object, doesn't mutate
7. **Everything is mathematical** - No side effects, no I/O, pure expressions

---

## Implementation

See:
- `kernel/canonical.py` - Core implementation
- `examples/canonical_car.py` - Car example
- `examples/canonical_document.py` - Document example
- `tests/test_canonical_form.py` - Comprehensive tests

All 363 tests passing ✅

---

## This Is Revolutionary

Traditional programming:
```python
car.position = 100  # Mutation
car.velocity = 20   # State stored
```

Dimensional programming:
```python
car_at_t10 = car.at_time(10)  # New object, computed state
state = car_at_t10.manifest()  # Pure function, no storage
```

**The difference:** Traditional programming stores state. Dimensional programming computes state from mathematical expressions.

This is the foundation of ButterflyFx.
