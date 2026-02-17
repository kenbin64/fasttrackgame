# ButterflyFX Dimensional API — Go Reference

**Version:** 1.0.0  
**Go:** 1.21+  
**Package:** `github.com/butterflyfx/helix`

---

## Installation

```bash
go get github.com/butterflyfx/helix
```

## Quick Start

```go
package main

import (
    "fmt"
    "github.com/butterflyfx/helix"
)

func main() {
    // Create dimension
    dim := helix.NewDimension("vehicles")
    
    // Create entities
    car := dim.Rectangle(helix.EntityOpts{
        ID:    "VIN-001",
        Name:  "car",
        Props: map[string]any{"color": "red"},
    })
    
    engine := dim.Rectangle(helix.EntityOpts{
        ID:   "ENGINE-001",
        Name: "engine",
    })
    
    car.AddChild(engine)
    
    // Lookup
    found := helix.Find("VIN-001")
    allCars := helix.FindByName("car")
    
    // Operations
    ops := helix.Operations()
    sorted := ops.Sort([]int{3, 1, 2}) // [1, 2, 3]
    
    // Custom operation
    helix.RegisterOperation("square", func(x int) int {
        return x * x
    }, helix.OpOpts{Category: "math"})
    
    result := ops.Call("square", 7) // 49
    
    fmt.Printf("Car: %v, Sorted: %v, Square: %v\n", found, sorted, result)
}
```

---

## Package Structure

```go
package helix

// Core types
type Dimension struct { ... }
type Entity struct { ... }
type Operation struct { ... }
type OperationRegistry struct { ... }
type Datastore struct { ... }
type Space struct { ... }

// Option types
type EntityOpts struct { ... }
type DimensionOpts struct { ... }
type OpOpts struct { ... }
type DatastoreOpts struct { ... }
```

---

## Type: `Dimension`

### Constructor

```go
func NewDimension(name string, opts ...DimensionOpts) *Dimension

type DimensionOpts struct {
    Width  float64 // Default: 100.0
    Height float64 // Default: 100.0
}
```

### Methods

```go
// Entity creation
func (d *Dimension) Rectangle(opts EntityOpts) *Entity
func (d *Dimension) Circle(opts EntityOpts) *Entity
func (d *Dimension) Triangle(opts EntityOpts) *Entity
func (d *Dimension) Polygon(opts PolygonOpts) *Entity
func (d *Dimension) Text(content string, opts EntityOpts) *Entity
func (d *Dimension) Point(opts EntityOpts) *Entity
func (d *Dimension) Line(opts LineOpts) *Entity
func (d *Dimension) Group(entities []*Entity, opts EntityOpts) *Entity

// Lookup
func (d *Dimension) ByID(id string) *Entity
func (d *Dimension) ByName(name string) []*Entity
func (d *Dimension) ByKind(kind string) []*Entity
func (d *Dimension) All() []*Entity
func (d *Dimension) Query(criteria map[string]any) []*Entity
func (d *Dimension) Invoke(identifier string) *Entity

// Properties
func (d *Dimension) Name() string
func (d *Dimension) Space() *Space
```

### Option Types

```go
type EntityOpts struct {
    ID       string
    Name     string
    Position string         // "center", "top-left", etc.
    Props    map[string]any
}

type PolygonOpts struct {
    EntityOpts
    Sides int
}

type LineOpts struct {
    EntityOpts
    Start string
    End   string
}
```

### Example

```go
package main

import "github.com/butterflyfx/helix"

func main() {
    // Create dimension
    physics := helix.NewDimension("physics", helix.DimensionOpts{
        Width:  800,
        Height: 600,
    })
    
    // Create entities
    car := physics.Rectangle(helix.EntityOpts{
        ID:       "VIN-001",
        Name:     "car",
        Position: "center",
        Props: map[string]any{
            "color": "red",
            "brand": "Tesla",
        },
    })
    
    engine := physics.Rectangle(helix.EntityOpts{
        ID:   "ENGINE-001",
        Name: "engine",
        Props: map[string]any{
            "horsepower": 670,
        },
    })
    
    // Link hierarchy
    car.AddChild(engine)
    
    // Lookup
    found := physics.ByID("VIN-001")       // *Entity
    engines := physics.ByName("engine")    // []*Entity
}
```

---

## Type: `Entity`

### Fields

```go
type Entity struct {
    ID       string
    Name     string
    Kind     string
    X        float64
    Y        float64
    Props    map[string]any
    Parent   *Entity
    Children []*Entity
    Space    *Space
}
```

### Dimensional Drilling

```go
func (e *Entity) DrillDown(name string) *Entity
func (e *Entity) DrillUp() *Entity
func (e *Entity) DrillAcross(name string) *Entity
func (e *Entity) Select(names ...string) []*Entity
```

### Methods

```go
func (e *Entity) Prop(key string, value any) *Entity  // Chainable
func (e *Entity) SetProps(props map[string]any) *Entity
func (e *Entity) Identify(id string) *Entity
func (e *Entity) AddChild(child *Entity) *Entity
func (e *Entity) ToMap() map[string]any
```

### Example

```go
// Set up hierarchy
engine.Parent = car
car.Children = append(car.Children, engine)
// Or use helper:
car.AddChild(engine)
car.AddChild(transmission)

// Dimensional drilling (NOT JOINs!)
myEngine := car.DrillDown("engine")           // *Entity
parent := myEngine.DrillUp()                  // *Entity
trans := myEngine.DrillAcross("transmission") // *Entity

// Select multiple
parts := car.Select("engine", "transmission") // []*Entity

// Chain properties
engine.Prop("horsepower", 670).Prop("turbo", true).Prop("fuel", "electric")
```

---

## Global Lookup Functions

```go
// Unified find
func Find(id string) *Entity
func FindBy(criteria map[string]any) []*Entity

// Specific methods
func ByID(id string) *Entity
func ByName(name string) []*Entity
func ByKind(kind string) []*Entity
func ByAttribute(attr string, value any) []*Entity
func ByDimension(name string) []*Entity
func Query(criteria map[string]any) []*Entity
```

### Example

```go
// Find by id
car := helix.Find("VIN-001")

// Find by name
cars := helix.FindBy(map[string]any{"name": "car"})

// Find by kind and attribute
redRectangles := helix.FindBy(map[string]any{
    "kind":  "rectangle",
    "color": "red",
})

// Specific methods
helix.ByID("VIN-001")
helix.ByName("car")
helix.ByKind("circle")
helix.ByAttribute("color", "red")
```

---

## Type: `OperationRegistry`

### Get Operations

```go
func Operations() *OperationRegistry
```

### Methods

```go
func (o *OperationRegistry) ByID(id string) *Operation
func (o *OperationRegistry) ByName(name string) []*Operation
func (o *OperationRegistry) ByKind(kind string) []*Operation
func (o *OperationRegistry) ByCategory(category string) []*Operation
func (o *OperationRegistry) All() []*Operation
func (o *OperationRegistry) Has(name string) bool
func (o *OperationRegistry) Len() int

// Call operation by name
func (o *OperationRegistry) Call(name string, args ...any) any
```

### Built-in Operations

```go
// Math
func (o *OperationRegistry) Add(a, b float64) float64
func (o *OperationRegistry) Subtract(a, b float64) float64
func (o *OperationRegistry) Multiply(a, b float64) float64
func (o *OperationRegistry) Divide(a, b float64) float64
func (o *OperationRegistry) Sqrt(x float64) float64
func (o *OperationRegistry) Pow(x, n float64) float64
func (o *OperationRegistry) Abs(x float64) float64

// Transform (generic via reflection)
func (o *OperationRegistry) Sort(slice any) any
func (o *OperationRegistry) Reverse(slice any) any
func (o *OperationRegistry) Unique(slice any) any

// Query
func (o *OperationRegistry) Count(slice any) int
func (o *OperationRegistry) First(slice any) any
func (o *OperationRegistry) Last(slice any) any
func (o *OperationRegistry) Sum(numbers []float64) float64
func (o *OperationRegistry) Min(slice any) any
func (o *OperationRegistry) Max(slice any) any
```

### Register Operations

```go
func RegisterOperation(name string, fn any, opts OpOpts) *Operation

type OpOpts struct {
    ID          string
    Kind        string
    Category    string
    Description string
}
```

### Example

```go
ops := helix.Operations()

// Use built-in operations
sorted := ops.Sort([]int{3, 1, 2})            // [1, 2, 3]
total := ops.Add(10, 5)                       // 15.0
first := ops.First(ops.Sort([]int{5, 3, 8}))  // 3

// Register custom operation
helix.RegisterOperation("double", func(x int) int {
    return x * 2
}, helix.OpOpts{Category: "math"})

result := ops.Call("double", 21) // 42

// Lookup operations
mathOps := ops.ByCategory("math")
for _, op := range mathOps {
    fmt.Println(op.Name)
}
```

---

## Type: `Operation`

### Fields

```go
type Operation struct {
    ID          string
    Name        string
    Kind        string
    Category    string
    Description string
}
```

### Methods

```go
func (op *Operation) Call(args ...any) any
func (op *Operation) DrillDown(name string) *Operation
func (op *Operation) DrillUp() *Operation
func (op *Operation) DrillAcross(name string) *Operation
func (op *Operation) Link(name string, other *Operation) *Operation
func (op *Operation) AddChild(child *Operation) *Operation
```

---

## Type: `Datastore`

### Constructor

```go
func RegisterDatastore(name string, opts DatastoreOpts) *Datastore

type DatastoreOpts struct {
    FetchFn       func(id string) map[string]any
    PersistFn     func(id string, data map[string]any) bool
    CheckChangeFn func(id string, version any) bool
    Writable      bool
}
```

### Methods

```go
func (ds *Datastore) Get(id string, space *Space) *Entity
func (ds *Datastore) SetInstanceAttr(entityID, attr string, value any)
func (ds *Datastore) GetInstanceAttr(entityID, attr string) any
func (ds *Datastore) Persist(entity *Entity) bool
func (ds *Datastore) Invalidate(id string)
func (ds *Datastore) ClearCache()

func (ds *Datastore) Name() string
func (ds *Datastore) Writable() bool
```

### Example

```go
// Simulated database
mockDB := map[string]map[string]any{
    "VIN-001": {"name": "car", "color": "red", "brand": "Tesla"},
    "VIN-002": {"name": "truck", "color": "blue", "brand": "Ford"},
}

// Register datastore
carsDB := helix.RegisterDatastore("vehicles", helix.DatastoreOpts{
    FetchFn: func(vin string) map[string]any {
        return mockDB[vin]
    },
    PersistFn: func(vin string, data map[string]any) bool {
        mockDB[vin] = data
        return true
    },
    Writable: true,
})

// First access → DB fetch
car := carsDB.Get("VIN-001", nil)
fmt.Println(car.Props["color"]) // "red"

// Second access → cached (no DB hit)
sameCar := carsDB.Get("VIN-001", nil)

// Instance attribute (ephemeral)
carsDB.SetInstanceAttr("VIN-001", "tempFlag", true)

// Persist
carsDB.Persist(car)
```

---

## Error Handling

Go uses explicit error returns:

```go
func (d *Dimension) ByIDOrError(id string) (*Entity, error)
func (ds *Datastore) PersistWithError(entity *Entity) error
```

For simple cases, methods return `nil` on not found:

```go
entity := dim.ByID("NONEXISTENT") // Returns nil, not error
if entity == nil {
    // Handle not found
}
```

---

## Concurrency

```go
// Thread-safe operations
ops := helix.Operations() // Safe for concurrent reads

// For concurrent writes, use mutex
var mu sync.Mutex
mu.Lock()
dim.Rectangle(opts)
mu.Unlock()
```

---

## Complete Example

```go
package main

import (
    "fmt"
    "github.com/butterflyfx/helix"
)

func main() {
    // ============================================
    // 1. Create dimension with entities
    // ============================================
    vehicles := helix.NewDimension("vehicles")
    
    car := vehicles.Rectangle(helix.EntityOpts{
        ID:   "VIN-001",
        Name: "car",
        Props: map[string]any{
            "color": "red",
            "brand": "Tesla",
            "model": "Model S",
        },
    })
    
    engine := vehicles.Rectangle(helix.EntityOpts{
        ID:   "ENGINE-001",
        Name: "engine",
        Props: map[string]any{
            "horsepower": 670,
            "type":       "electric",
        },
    })
    
    car.AddChild(engine)
    
    // ============================================
    // 2. Multi-path lookup
    // ============================================
    tesla := helix.Find("VIN-001")
    allCars := helix.FindBy(map[string]any{"name": "car"})
    
    // ============================================
    // 3. Dimensional drilling
    // ============================================
    myEngine := car.DrillDown("engine")
    myCar := myEngine.DrillUp()
    
    // ============================================
    // 4. Operations
    // ============================================
    ops := helix.Operations()
    
    // Built-in
    sortedList := ops.Sort([]int{3, 1, 2})
    total := ops.Sum([]float64{1, 2, 3, 4, 5})
    
    // Custom
    helix.RegisterOperation("getBrand", func(e *helix.Entity) string {
        if brand, ok := e.Props["brand"].(string); ok {
            return brand
        }
        return "Unknown"
    }, helix.OpOpts{Category: "vehicle"})
    
    brand := ops.Call("getBrand", car).(string)
    
    // ============================================
    // 5. Chained operations
    // ============================================
    prices := []int{50000, 75000, 100000, 45000}
    minPrice := ops.First(ops.Sort(prices))
    maxPrice := ops.Last(ops.Sort(prices))
    
    fmt.Printf("Tesla: %v\n", tesla)
    fmt.Printf("All cars: %v\n", allCars)
    fmt.Printf("Engine: %v, Parent: %v\n", myEngine, myCar)
    fmt.Printf("Sorted: %v, Total: %v\n", sortedList, total)
    fmt.Printf("Brand: %s\n", brand)
    fmt.Printf("Price range: $%v - $%v\n", minPrice, maxPrice)
}
```

---

**© 2026 ButterflyFX. All rights reserved.**
