# ButterflyFX Dimensional API Specification

**Version:** 1.0.0  
**Date:** February 2026  
**Status:** Formal Specification

---

## Overview

The ButterflyFX Dimensional API provides a **human-first** programming interface for dimensional computing. This specification is **language-agnostic** — implementations exist for Python, Node.js, Go, TypeScript, Java, and C# .NET.

### Core Philosophy

1. **Objects exist by virtue of their dimension existing** — no tables, no foreign keys
2. **Multi-path lookup** — find any object by id, name, kind, or attribute
3. **Dimensional drilling** — navigate relationships without JOINs
4. **Operations are dimensions** — functions are first-class dimensional entities
5. **Instance vs persisted** — attributes are ephemeral unless explicitly persisted

---

## 1. Dimension

A **Dimension** is a geometric space where objects exist inherently by position on the manifold.

### 1.1 Creation

```
dimension(name: String, width?: Float = 100.0, height?: Float = 100.0) → Dimension
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | String | required | Dimension identifier |
| `width` | Float | 100.0 | Dimension width |
| `height` | Float | 100.0 | Dimension height |

### 1.2 Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | String | Dimension name |
| `space` | Space | Underlying geometric space |

### 1.3 Methods

#### Entity Creation

```
dimension.rectangle(id?: String, name?: String, position?: String, **props) → Entity
dimension.circle(id?: String, name?: String, position?: String, **props) → Entity
dimension.triangle(id?: String, name?: String, position?: String, **props) → Entity
dimension.polygon(id?: String, name?: String, position?: String, sides?: Int, **props) → Entity
dimension.text(content: String, id?: String, name?: String, position?: String, **props) → Entity
dimension.point(id?: String, name?: String, position?: String, **props) → Entity
dimension.line(id?: String, name?: String, start?: String, end?: String, **props) → Entity
dimension.group(*entities, id?: String, name?: String, position?: String, **props) → Entity
```

#### Lookup Methods

```
dimension.by_id(id: String) → Entity | Null
dimension.by_name(name: String) → List<Entity>
dimension.by_kind(kind: String) → List<Entity>
dimension.all() → List<Entity>
dimension.query(**criteria) → List<Entity>
dimension.invoke(identifier: String) → Entity | Null
```

#### Shorthand Access

```
dimension.{name}      → Entity | List<Entity>    // by entity name
dimension["{id}"]     → Entity                    // by id or name
```

---

## 2. Entity

An **Entity** is an object that exists within a Dimension. Entities have identity, position, and properties.

### 2.1 Core Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | String | Unique identifier (VIN, UUID, index) |
| `name` | String | Object type/class (car, engine) |
| `kind` | String | Shape type (rectangle, circle) |
| `x` | Float | X coordinate |
| `y` | Float | Y coordinate |
| `props` | Map | Custom properties |
| `parent` | Entity | Parent entity (null for root) |
| `children` | List<Entity> | Child entities |

### 2.2 Dimensional Drilling

Navigate relationships **without JOINs**:

```
entity.drillDown(name?: String) → Entity | Null
entity.drillUp() → Entity | Null
entity.drillAcross(name: String) → Entity | Null
entity.select(*names) → List<Entity>
```

| Method | Description |
|--------|-------------|
| `drillDown` | Navigate to child entity |
| `drillUp` | Navigate to parent entity |
| `drillAcross` | Navigate to sibling entity |
| `select` | Select multiple children by name |

### 2.3 Property Methods

```
entity.prop(**kwargs) → Entity           // Set properties (chainable)
entity.identify(id: String) → Entity     // Set identity
entity.to_dict() → Map                   // Export to dictionary
```

---

## 3. Global Lookup Functions

Find entities across all dimensions using a single entry point.

### 3.1 Unified Find

```
find(id?: String, name?: String, kind?: String, **attributes) → Entity | List<Entity> | Null
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | String | Find by unique id |
| `name` | String | Find by entity name |
| `kind` | String | Find by shape type |
| `**attributes` | Map | Find by custom attributes |

### 3.2 Specific Lookup Methods

```
by_id(id: String) → Entity | Null
by_name(name: String) → List<Entity>
by_kind(kind: String) → List<Entity>
by_attribute(attr: String, value: Any) → List<Entity>
by_dimension(name: String) → List<Entity>
query(**criteria) → List<Entity>
```

---

## 4. Operations Dimension

**Operations are dimensional substrates** — functions are entities that can be looked up by name, id, or category.

### 4.1 Get Operations Dimension

```
operations() → Operations
```

### 4.2 Operations Methods

```
operations.by_id(id: String) → Operation | Null
operations.by_name(name: String) → List<Operation>
operations.by_kind(kind: String) → List<Operation>
operations.by_category(category: String) → List<Operation>
operations.all() → List<Operation>
```

### 4.3 Shorthand Access

```
operations.{name}(args...)    // Call operation by name
operations["{id}"]            // Get operation by id or name
```

### 4.4 Register Operations

```
operation(name_or_fn, fn?, id?, kind?, category?, description?, **props) → Operation
```

**Usage patterns:**

```
// As decorator (no args)
@operation
def square(x): return x * x

// As decorator (with args)
@operation("sq", category="math")
def square(x): return x * x

// Direct call
operation("negate", lambda x: -x, category="math")
```

### 4.5 Built-in Operations

| Category | Operations |
|----------|------------|
| **math** | add, subtract, multiply, divide, sqrt, pow, abs |
| **transform** | sort, reverse, unique |
| **query** | count, first, last, sum, min, max |

---

## 5. Operation Entity

An **Operation** is a function as a dimensional entity.

### 5.1 Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | String | Unique identifier |
| `name` | String | Operation name |
| `kind` | String | Operation type (function, method, transform) |
| `category` | String | Category (math, transform, query) |
| `description` | String | Human-readable description |

### 5.2 Methods

```
operation(*args, **kwargs) → Any          // Invoke the operation
operation.drillDown(name?: String) → Operation | Null
operation.drillUp() → Operation | Null
operation.drillAcross(name: String) → Operation | Null
operation.link(name: String, op: Operation) → Operation
operation.child(op: Operation) → Operation
```

---

## 6. Datastore Integration

External datastores are accessed lazily — data is ingested on first access and cached dimensionally.

### 6.1 Register Datastore

```
register_datastore(
    name: String,
    fetch_fn: Function(id: String) → Map | Null,
    persist_fn?: Function(id: String, data: Map) → Boolean,
    check_changed_fn?: Function(id: String, version: Any) → Boolean,
    writable?: Boolean = false
) → Datastore
```

### 6.2 Datastore Methods

```
datastore.get(id: String, space?: Space) → Entity | Null
datastore.set_instance_attr(entity_id: String, attr: String, value: Any) → Void
datastore.get_instance_attr(entity_id: String, attr: String) → Any | Null
datastore.persist(entity: Entity) → Boolean
datastore.invalidate(id: String) → Void
datastore.clear_cache() → Void
```

### 6.3 Instance vs Persisted Attributes

| Type | Behavior |
|------|----------|
| **Instance** | Ephemeral — only exists in current session |
| **Persisted** | Written to datastore — requires `writable=True` + `persist()` call |

---

## 7. Semantic Vocabulary

Human-readable positions, orientations, and directions that map to manifold coordinates.

### 7.1 Position

```
"center", "top", "bottom", "left", "right"
"top-left", "top-right", "bottom-left", "bottom-right"
```

### 7.2 Orientation

```
"north", "south", "east", "west"
"northeast", "northwest", "southeast", "southwest"
"horizontal", "vertical", "diagonal"
```

### 7.3 Size

```
"tiny", "small", "medium", "large", "huge"
```

### 7.4 Direction

```
"up", "down", "left", "right"
"forward", "backward", "inward", "outward"
```

---

## 8. Shape Builder Pattern

Fluent API for building entities with chained method calls.

```
space.shape(kind: String, id?: String)
    .name(name: String)
    .place(position: String | Tuple)
    .size(size: String | Float)
    .orient(orientation: String | Float)
    .color(color: String)
    .prop(**kwargs)
    .relate(target: Entity, relation: String)
    .done() → Entity
```

---

## 9. Space

A **Space** is the underlying geometric canvas for a Dimension.

### 9.1 Creation

```
space(width?: Float = 100.0, height?: Float = 100.0, name?: String = "space") → Space
```

### 9.2 Methods

```
space.shape(kind: String, id?: String) → ShapeBuilder
space.point(id?: String) → ShapeBuilder
space.line(id?: String) → LineBuilder
space.text(id?: String) → TextBuilder
space.group(*entities, id?: String) → Entity
space.render() → RenderedOutput
```

---

## 10. Error Handling

### 10.1 Standard Errors

| Error | Cause |
|-------|-------|
| `KeyError` | Entity not found by id or name |
| `AttributeError` | Attribute access failed |
| `PermissionError` | Datastore not writable |
| `NotImplementedError` | Persist function not provided |

### 10.2 Error Behavior

- Failed lookups return `Null` (not exceptions) for `by_id`, `by_name`
- Index access (`dimension["id"]`) raises `KeyError` if not found
- Attribute access (`dimension.name`) raises `AttributeError` if not found

---

## 11. Threading and Concurrency

| Aspect | Behavior |
|--------|----------|
| **Global registries** | Thread-safe for reads; lock for writes |
| **Dimension operations** | Each dimension is independent |
| **Datastore cache** | Per-datastore caching; invalidate for consistency |

---

## 12. Type System

### 12.1 Core Types

```
Dimension     // Geometric space for entities
Entity        // Object existing in a dimension
Operation     // Function as dimensional entity
Operations    // The operations dimension
Space         // Underlying geometric canvas
Datastore     // External data source wrapper
ShapeBuilder  // Fluent builder for shapes
```

### 12.2 Value Types

```
String        // Text values
Float         // Numeric coordinates and sizes
Int           // Integer values
Boolean       // True/False values
Map           // Key-value dictionary
List          // Ordered collection
Null          // Absence of value
Any           // Any type
```

---

## Appendix A: Quick Reference

### Create Dimension and Entities
```
dim = dimension("physics")
car = dim.rectangle(id="VIN-001", name="car", color="red")
engine = dim.rectangle(id="ENGINE-001", name="engine", parent=car)
```

### Lookup
```
find("VIN-001")              // By id
find(name="car")             // By name
dim.car                      // Shorthand
dim["VIN-001"]               // Index
```

### Dimensional Drilling
```
car.drillDown("engine")      // Navigate to child
engine.drillUp()             // Navigate to parent
engine.drillAcross("trans")  // Navigate to sibling
```

### Operations
```
ops = operations()
ops.sort([3, 1, 2])          // [1, 2, 3]
ops.add(5, 3)                // 8
ops.by_category("math")      // [add, subtract, multiply, ...]
```

### Custom Operations
```
@operation
def square(x): return x * x

ops.square(7)                // 49
```

---

## Appendix B: Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Feb 2026 | Initial formal specification |

---

**© 2026 ButterflyFX. All rights reserved.**
