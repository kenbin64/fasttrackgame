# ButterflyFX Dimensional API Documentation

**Version:** 1.0.0  
**Date:** February 2026

---

## Overview

The ButterflyFX Dimensional API provides a **human-first** programming interface for dimensional computing. Objects exist by virtue of their dimension existing — no tables, no foreign keys, no JOINs.

---

## Documentation Index

### Language-Agnostic Specification

| Document | Description |
|----------|-------------|
| [DIMENSIONAL_API_SPECIFICATION.md](DIMENSIONAL_API_SPECIFICATION.md) | Formal API specification — concepts, types, methods |

### Language-Specific References

| Language | Document | Package |
|----------|----------|---------|
| **Python** | [python/API_REFERENCE.md](python/API_REFERENCE.md) | `helix` |
| **Node.js** | [nodejs/API_REFERENCE.md](nodejs/API_REFERENCE.md) | `@butterflyfx/helix` |
| **TypeScript** | [typescript/API_REFERENCE.md](typescript/API_REFERENCE.md) | `@butterflyfx/helix` |
| **Go** | [go/API_REFERENCE.md](go/API_REFERENCE.md) | `github.com/butterflyfx/helix` |
| **Java** | [java/API_REFERENCE.md](java/API_REFERENCE.md) | `com.butterflyfx:helix` |
| **C# .NET** | [csharp/API_REFERENCE.md](csharp/API_REFERENCE.md) | `ButterflyFX.Helix` |

---

## Core Concepts

### 1. Dimension
A geometric space where objects exist inherently by position on the manifold.

```
dimension("vehicles")
```

### 2. Entity
An object that exists within a Dimension — has identity, position, and properties.

```
dim.rectangle(id="VIN-001", name="car", color="red")
```

### 3. Dimensional Drilling
Navigate relationships without JOINs.

```
car.drillDown("engine")     // Navigate to child
engine.drillUp()            // Navigate to parent
engine.drillAcross("trans") // Navigate to sibling
```

### 4. Multi-Path Lookup
Find objects by id, name, kind, or attribute.

```
find("VIN-001")             // By id
find(name="car")            // By name
dim.car                     // Shorthand
dim["VIN-001"]              // Index
```

### 5. Operations Dimension
Functions as first-class dimensional entities.

```
ops = operations()
ops.sort([3, 1, 2])         // [1, 2, 3]
ops.by_category("math")     // [add, subtract, ...]
```

### 6. Datastore Integration
Lazy ingest from external sources — data becomes dimensional.

```
ds = register_datastore("vehicles", fetch_fn=fetch_vehicle)
car = ds.get("VIN-001")     // First: DB hit, then: cached
```

---

## Quick Comparison

| Concept | Python | Node.js | Go | Java | C# |
|---------|--------|---------|-----|------|-----|
| Create dimension | `dimension("x")` | `dimension('x')` | `NewDimension("x")` | `dimension("x")` | `Dimension("x")` |
| Create entity | `dim.rectangle(...)` | `dim.rectangle({...})` | `dim.Rectangle(opts)` | `dim.rectangle().build()` | `dim.Rectangle().Build()` |
| Find by id | `find("id")` | `find('id')` | `Find("id")` | `find("id")` | `Find("id")` |
| Drill down | `entity.drillDown("x")` | `entity.drillDown('x')` | `entity.DrillDown("x")` | `entity.drillDown("x")` | `entity.DrillDown("x")` |
| Operations | `operations()` | `operations()` | `Operations()` | `operations()` | `Operations()` |
| Call operation | `ops.sort([...])` | `ops.sort([...])` | `ops.Sort(slice)` | `ops.sort(list)` | `ops.Sort(array)` |

---

## Philosophy

> **"Objects exist by virtue of their dimension existing."**

- No tables, no foreign keys, no JOINs
- Relationships are geometric (drillDown/drillUp/drillAcross)
- Properties are derived from position on manifold
- Instance attributes are ephemeral unless persisted
- Operations are dimensional entities themselves

---

## Getting Started

### Python
```bash
pip install butterflyfx-helix
```
```python
from helix import dimension, find, operations
```

### Node.js / TypeScript
```bash
npm install @butterflyfx/helix
```
```javascript
const { dimension, find, operations } = require('@butterflyfx/helix');
```

### Go
```bash
go get github.com/butterflyfx/helix
```
```go
import "github.com/butterflyfx/helix"
```

### Java
```xml
<dependency>
    <groupId>com.butterflyfx</groupId>
    <artifactId>helix</artifactId>
    <version>1.0.0</version>
</dependency>
```
```java
import static com.butterflyfx.helix.Helix.*;
```

### C# .NET
```bash
dotnet add package ButterflyFX.Helix
```
```csharp
using static ButterflyFX.Helix.Helix;
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Feb 2026 | Initial release |

---

**© 2026 ButterflyFX. All rights reserved.**
