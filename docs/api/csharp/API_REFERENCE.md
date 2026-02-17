# ButterflyFX Dimensional API — C# .NET Reference

**Version:** 1.0.0  
**.NET:** 8.0+  
**Package:** `ButterflyFX.Helix`  
**NuGet:** `ButterflyFX.Helix`

---

## Installation

### NuGet Package Manager

```powershell
Install-Package ButterflyFX.Helix
```

### .NET CLI

```bash
dotnet add package ButterflyFX.Helix
```

### PackageReference

```xml
<PackageReference Include="ButterflyFX.Helix" Version="1.0.0" />
```

## Quick Start

```csharp
using ButterflyFX.Helix;
using static ButterflyFX.Helix.Helix;

// Create dimension
var dim = Dimension("vehicles");

// Create entities
var car = dim.Rectangle()
    .Id("VIN-001")
    .Name("car")
    .Prop("color", "red")
    .Build();

var engine = dim.Rectangle()
    .Id("ENGINE-001")
    .Name("engine")
    .Build();

car.AddChild(engine);

// Lookup
var found = Find("VIN-001");
var allCars = FindByName("car");

// Operations
var ops = Operations();
var sorted = ops.Sort(new[] { 3, 1, 2 }); // [1, 2, 3]

// Custom operation
Operation("square", (int x) => x * x, category: "math");
var result = ops.Call<int>("square", 7); // 49
```

---

## Namespace Structure

```csharp
namespace ButterflyFX.Helix
{
    // Core classes
    public class Dimension { }
    public class Entity { }
    public class Operation { }
    public class Operations { }
    public class Datastore { }
    public class Space { }
    
    // Builders
    public class EntityBuilder { }
    public class OperationBuilder { }
    public class DatastoreBuilder { }
    
    // Static factory
    public static class Helix { }
}
```

---

## Class: `Dimension`

### Creation

```csharp
// Static factory
var dim = Helix.Dimension("vehicles");
var dim = Helix.Dimension("physics", width: 800, height: 600);

// Constructor
var dim = new Dimension("vehicles");
var dim = new Dimension("physics", 800, 600);
```

### Entity Builders

```csharp
EntityBuilder Rectangle();
EntityBuilder Circle();
EntityBuilder Triangle();
EntityBuilder Polygon(int sides = 6);
EntityBuilder Text(string content);
EntityBuilder Point();
EntityBuilder Line();
EntityBuilder Group(params Entity[] entities);
```

### Lookup Methods

```csharp
Entity? ById(string id);
IReadOnlyList<Entity> ByName(string name);
IReadOnlyList<Entity> ByKind(string kind);
IReadOnlyList<Entity> All();
IReadOnlyList<Entity> Query(Dictionary<string, object> criteria);
Entity? Invoke(string identifier);
```

### Properties

```csharp
string Name { get; }
Space Space { get; }
```

### Indexers

```csharp
Entity? this[string id] { get; }
```

### Example

```csharp
using ButterflyFX.Helix;
using static ButterflyFX.Helix.Helix;

var physics = Dimension("physics", 800, 600);

var car = physics.Rectangle()
    .Id("VIN-001")
    .Name("car")
    .Position("center")
    .Prop("color", "red")
    .Prop("brand", "Tesla")
    .Build();

var engine = physics.Rectangle()
    .Id("ENGINE-001")
    .Name("engine")
    .Prop("horsepower", 670)
    .Build();

// Link hierarchy
car.AddChild(engine);

// Lookup
var found = physics.ById("VIN-001");
var engines = physics.ByName("engine");
var byIndex = physics["VIN-001"];
```

---

## Class: `Entity`

### Properties

```csharp
string Id { get; }
string Name { get; set; }
string Kind { get; }
double X { get; }
double Y { get; }
Dictionary<string, object> Props { get; }
Entity? Parent { get; set; }
List<Entity> Children { get; }
Space Space { get; }
```

### Dimensional Drilling

```csharp
Entity? DrillDown();                         // First child
Entity? DrillDown(string name);              // Child by name
Entity? DrillUp();                           // Parent
Entity? DrillAcross(string name);            // Sibling by name
IReadOnlyList<Entity> Select(params string[] names);  // Multiple children
```

### Methods

```csharp
Entity Prop(string key, object value);       // Chainable
Entity SetProps(Dictionary<string, object> props);  // Chainable
Entity Identify(string id);                  // Chainable
Entity AddChild(Entity child);               // Chainable
Dictionary<string, object> ToDict();
```

### Generic Property Access

```csharp
T? GetProp<T>(string key);
Entity SetProp<T>(string key, T value);
```

### Example

```csharp
// Set up hierarchy
engine.Parent = car;
car.Children.Add(engine);
// Or use helper:
car.AddChild(engine).AddChild(transmission);

// Dimensional drilling (NOT JOINs!)
var myEngine = car.DrillDown("engine");
var parent = myEngine?.DrillUp();
var trans = myEngine?.DrillAcross("transmission");

// Select multiple
var parts = car.Select("engine", "transmission");

// Chain properties
engine
    .Prop("horsepower", 670)
    .Prop("turbo", true)
    .Prop("fuel", "electric");

// Generic access
var hp = engine.GetProp<int>("horsepower"); // 670
```

---

## Global Lookup (Static Methods)

```csharp
using static ButterflyFX.Helix.Helix;

// Find by id
var car = Find("VIN-001");

// Find by criteria
var cars = FindBy(new Dictionary<string, object> { ["name"] = "car" });

// Specific methods
Entity? entity = ById("VIN-001");
IReadOnlyList<Entity> entities = ByName("car");
IReadOnlyList<Entity> entities = ByKind("rectangle");
IReadOnlyList<Entity> entities = ByAttribute("color", "red");
IReadOnlyList<Entity> entities = ByDimension("vehicles");
IReadOnlyList<Entity> entities = Query(new() { ["kind"] = "rectangle", ["color"] = "red" });
```

---

## Class: `Operations`

### Get Operations

```csharp
var ops = Helix.Operations();
// or
var ops = Operations.Instance;
```

### Lookup Methods

```csharp
Operation? ById(string id);
IReadOnlyList<Operation> ByName(string name);
IReadOnlyList<Operation> ByKind(string kind);
IReadOnlyList<Operation> ByCategory(string category);
IReadOnlyList<Operation> All();
bool Has(string name);
int Count { get; }
```

### Built-in Operations

```csharp
// Math
double Add(double a, double b);
double Subtract(double a, double b);
double Multiply(double a, double b);
double Divide(double a, double b);
double Sqrt(double x);
double Pow(double x, double n);
double Abs(double x);

// Transform (generic)
IReadOnlyList<T> Sort<T>(IEnumerable<T> source) where T : IComparable<T>;
IReadOnlyList<T> Reverse<T>(IEnumerable<T> source);
IReadOnlyList<T> Unique<T>(IEnumerable<T> source);

// Query
int Count<T>(IEnumerable<T> source);
T? First<T>(IEnumerable<T> source);
T? Last<T>(IEnumerable<T> source);
double Sum(IEnumerable<double> source);
T? Min<T>(IEnumerable<T> source) where T : IComparable<T>;
T? Max<T>(IEnumerable<T> source) where T : IComparable<T>;
```

### Call Dynamic Operations

```csharp
T Call<T>(string name, params object[] args);
object? Call(string name, params object[] args);
```

### Register Operations

```csharp
// Fluent builder
Helix.Operation("square", (int x) => x * x)
    .Id("square_v1")
    .Kind("function")
    .Category("math")
    .Description("Square a number")
    .Register();

// Direct
Operations.Register("double", (int x) => x * 2, "math");

// Lambda syntax
Operation<int, int>("triple", x => x * 3, category: "math");
```

### Example

```csharp
var ops = Operations();

// Use built-in operations
var sorted = ops.Sort(new[] { 3, 1, 2 });     // [1, 2, 3]
var total = ops.Add(10, 5);                    // 15.0
var first = ops.First(ops.Sort(new[] { 5, 3, 8, 1 })); // 1

// Register custom operation
Operation("double", (int x) => x * 2, category: "math");
var result = ops.Call<int>("double", 21); // 42

// Lookup operations
var mathOps = ops.ByCategory("math");
foreach (var op in mathOps)
{
    Console.WriteLine(op.Name);
}
```

---

## Class: `Operation`

### Properties

```csharp
string Id { get; }
string Name { get; }
string Kind { get; }
string Category { get; }
string Description { get; }
```

### Methods

```csharp
T Call<T>(params object[] args);
object? Call(params object[] args);
Operation? DrillDown();
Operation? DrillDown(string name);
Operation? DrillUp();
Operation? DrillAcross(string name);
Operation Link(string name, Operation other);
Operation AddChild(Operation child);
```

---

## Class: `Datastore`

### Builder

```csharp
var ds = Helix.Datastore("vehicles")
    .FetchFn(id => database.FindById(id))
    .PersistFn((id, data) => database.Save(id, data))
    .CheckChangedFn((id, version) => database.IsModified(id, version))
    .Writable(true)
    .Build();
```

### Methods

```csharp
Entity? Get(string id);
Entity? Get(string id, Space? space);
void SetInstanceAttr(string entityId, string attr, object value);
T? GetInstanceAttr<T>(string entityId, string attr);
object? GetInstanceAttr(string entityId, string attr);
bool Persist(Entity entity);
void Invalidate(string id);
void ClearCache();

string Name { get; }
bool IsWritable { get; }
```

### Example

```csharp
// Simulated database
var mockDb = new Dictionary<string, Dictionary<string, object>>
{
    ["VIN-001"] = new() { ["name"] = "car", ["color"] = "red", ["brand"] = "Tesla" },
    ["VIN-002"] = new() { ["name"] = "truck", ["color"] = "blue", ["brand"] = "Ford" }
};

// Register datastore
var carsDb = Datastore("vehicles")
    .FetchFn(vin => mockDb.GetValueOrDefault(vin))
    .PersistFn((vin, data) =>
    {
        mockDb[vin] = data;
        return true;
    })
    .Writable(true)
    .Build();

// First access → DB fetch
var car = carsDb.Get("VIN-001");
Console.WriteLine(car?.Props["color"]); // "red"

// Second access → cached (no DB hit)
var sameCar = carsDb.Get("VIN-001");

// Instance attribute (ephemeral)
carsDb.SetInstanceAttr("VIN-001", "tempFlag", true);

// Persist
carsDb.Persist(car!);
```

---

## Delegates

```csharp
public delegate Dictionary<string, object>? FetchFunc(string id);
public delegate bool PersistFunc(string id, Dictionary<string, object> data);
public delegate bool CheckChangedFunc(string id, object? version);
```

---

## Records (C# 9+)

```csharp
public record EntityOptions(
    string? Id = null,
    string? Name = null,
    string Position = "center",
    Dictionary<string, object>? Props = null
);

public record DimensionOptions(
    double Width = 100.0,
    double Height = 100.0
);

public record OperationOptions(
    string? Id = null,
    string Kind = "function",
    string Category = "general",
    string Description = ""
);
```

---

## LINQ Integration

```csharp
using ButterflyFX.Helix;
using System.Linq;

var dim = Dimension("vehicles");

// Create entities
dim.Rectangle().Id("VIN-001").Name("car").Prop("color", "red").Build();
dim.Rectangle().Id("VIN-002").Name("car").Prop("color", "blue").Build();
dim.Circle().Id("VIN-003").Name("motorcycle").Prop("color", "black").Build();

// LINQ queries on entities
var redVehicles = dim.All()
    .Where(e => e.Props.GetValueOrDefault("color")?.ToString() == "red")
    .ToList();

var vehiclesByKind = dim.All()
    .GroupBy(e => e.Kind)
    .ToDictionary(g => g.Key, g => g.ToList());

var carColors = dim.ByName("car")
    .Select(e => e.GetProp<string>("color"))
    .Distinct()
    .ToList();
```

---

## Async Support

```csharp
// Async datastore
var asyncDb = Datastore("vehicles")
    .FetchFnAsync(async id => await database.FindByIdAsync(id))
    .PersistFnAsync(async (id, data) => await database.SaveAsync(id, data))
    .Writable(true)
    .Build();

// Async operations
var car = await asyncDb.GetAsync("VIN-001");
await asyncDb.PersistAsync(car);
```

---

## Nullable Reference Types

```csharp
#nullable enable

Entity? entity = dim.ById("VIN-001");
if (entity is not null)
{
    var engine = entity.DrillDown("engine");
    var brand = entity.GetProp<string>("brand") ?? "Unknown";
}

// Pattern matching
if (dim.ById("VIN-001") is { } car)
{
    Console.WriteLine(car.Name);
}
```

---

## Complete Example

```csharp
using ButterflyFX.Helix;
using static ButterflyFX.Helix.Helix;

// ============================================
// 1. Create dimension with entities
// ============================================
var vehicles = Dimension("vehicles");

var car = vehicles.Rectangle()
    .Id("VIN-001")
    .Name("car")
    .Prop("color", "red")
    .Prop("brand", "Tesla")
    .Prop("model", "Model S")
    .Build();

var engine = vehicles.Rectangle()
    .Id("ENGINE-001")
    .Name("engine")
    .Prop("horsepower", 670)
    .Prop("type", "electric")
    .Build();

car.AddChild(engine);

// ============================================
// 2. Multi-path lookup
// ============================================
var tesla = Find("VIN-001");
var allCars = FindBy(new() { ["name"] = "car" });

// ============================================
// 3. Dimensional drilling
// ============================================
var myEngine = car.DrillDown("engine");
var myCar = myEngine?.DrillUp();

// ============================================
// 4. Operations
// ============================================
var ops = Operations();

// Built-in
var sortedList = ops.Sort(new[] { 3, 1, 2 });
var total = ops.Sum(new[] { 1.0, 2.0, 3.0, 4.0, 5.0 });

// Custom
Operation("getBrand", (Entity e) => 
    e.Props.GetValueOrDefault("brand")?.ToString() ?? "Unknown",
    category: "vehicle"
);

var brand = ops.Call<string>("getBrand", car); // "Tesla"

// ============================================
// 5. Chained operations
// ============================================
var prices = new[] { 50000, 75000, 100000, 45000 };
var minPrice = ops.First(ops.Sort(prices));
var maxPrice = ops.Last(ops.Sort(prices));

Console.WriteLine($"Tesla: {tesla}");
Console.WriteLine($"Engine: {myEngine}");
Console.WriteLine($"Brand: {brand}");
Console.WriteLine($"Price range: ${minPrice} - ${maxPrice}");
```

---

## Thread Safety

```csharp
// Operations singleton is thread-safe
var ops = Operations(); // Safe for concurrent access

// For dimension modifications, use lock
lock (dimension)
{
    dimension.Rectangle()
        .Id("NEW-001")
        .Build();
}

// Or use ConcurrentDictionary for caching
var entityCache = new ConcurrentDictionary<string, Entity>();
```

---

## Exceptions

```csharp
// Not found returns null (not exception)
Entity? entity = dim.ById("NONEXISTENT"); // Returns null

// For strict mode
var entity = dim.ByIdOrThrow("VIN-001"); // Throws EntityNotFoundException

// Datastore exceptions
try
{
    datastore.Persist(entity);
}
catch (DatastoreNotWritableException)
{
    // Handle read-only datastore
}
catch (PersistenceException ex)
{
    // Handle persistence failure
}
```

---

## Source Generators (Advanced)

```csharp
// Auto-generate strongly-typed operation methods
[GenerateOperations]
public partial class MyOperations : Operations
{
    [Operation(Category = "math")]
    public static int Square(int x) => x * x;
    
    [Operation(Category = "vehicle")]
    public static string GetBrand(Entity e) => 
        e.Props.GetValueOrDefault("brand")?.ToString() ?? "Unknown";
}

// Usage
var ops = new MyOperations();
ops.Square(7);        // Strongly typed
ops.GetBrand(car);    // Strongly typed
```

---

**© 2026 ButterflyFX. All rights reserved.**
