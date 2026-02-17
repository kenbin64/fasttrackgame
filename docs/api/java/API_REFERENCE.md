# ButterflyFX Dimensional API — Java Reference

**Version:** 1.0.0  
**Java:** 17+  
**Package:** `com.butterflyfx.helix`  
**Maven:** `com.butterflyfx:helix:1.0.0`

---

## Installation

### Maven

```xml
<dependency>
    <groupId>com.butterflyfx</groupId>
    <artifactId>helix</artifactId>
    <version>1.0.0</version>
</dependency>
```

### Gradle

```groovy
implementation 'com.butterflyfx:helix:1.0.0'
```

## Quick Start

```java
import com.butterflyfx.helix.*;
import static com.butterflyfx.helix.Helix.*;

public class Main {
    public static void main(String[] args) {
        // Create dimension
        Dimension dim = dimension("vehicles");
        
        // Create entities
        Entity car = dim.rectangle()
            .id("VIN-001")
            .name("car")
            .prop("color", "red")
            .build();
        
        Entity engine = dim.rectangle()
            .id("ENGINE-001")
            .name("engine")
            .build();
        
        car.addChild(engine);
        
        // Lookup
        Entity found = find("VIN-001");
        List<Entity> allCars = findByName("car");
        
        // Operations
        Operations ops = operations();
        List<Integer> sorted = ops.sort(List.of(3, 1, 2)); // [1, 2, 3]
        
        // Custom operation
        operation("square", (Integer x) -> x * x)
            .category("math")
            .register();
        
        int result = ops.<Integer>call("square", 7); // 49
    }
}
```

---

## Package Structure

```java
package com.butterflyfx.helix;

// Core classes
public class Dimension { ... }
public class Entity { ... }
public class Operation { ... }
public class Operations { ... }
public class Datastore { ... }
public class Space { ... }

// Builders
public class EntityBuilder { ... }
public class OperationBuilder { ... }
public class DatastoreBuilder { ... }

// Static factory
public final class Helix { ... }
```

---

## Class: `Dimension`

### Creation

```java
// Static factory
Dimension dim = Helix.dimension("vehicles");
Dimension dim = Helix.dimension("physics", 800.0, 600.0);

// Constructor
Dimension dim = new Dimension("vehicles");
Dimension dim = new Dimension("physics", 800.0, 600.0);
```

### Entity Builders

```java
// Fluent builders
EntityBuilder rectangle();
EntityBuilder circle();
EntityBuilder triangle();
EntityBuilder polygon(int sides);
EntityBuilder text(String content);
EntityBuilder point();
EntityBuilder line();
EntityBuilder group(Entity... entities);
```

### Lookup Methods

```java
Entity byId(String id);
List<Entity> byName(String name);
List<Entity> byKind(String kind);
List<Entity> all();
List<Entity> query(Map<String, Object> criteria);
Entity invoke(String identifier);
```

### Properties

```java
String getName();
Space getSpace();
```

### Example

```java
import com.butterflyfx.helix.*;
import static com.butterflyfx.helix.Helix.*;

Dimension physics = dimension("physics", 800.0, 600.0);

Entity car = physics.rectangle()
    .id("VIN-001")
    .name("car")
    .position("center")
    .prop("color", "red")
    .prop("brand", "Tesla")
    .build();

Entity engine = physics.rectangle()
    .id("ENGINE-001")
    .name("engine")
    .prop("horsepower", 670)
    .build();

// Link hierarchy
car.addChild(engine);

// Lookup
Entity found = physics.byId("VIN-001");
List<Entity> engines = physics.byName("engine");
```

---

## Class: `Entity`

### Properties

```java
String getId();
String getName();
void setName(String name);
String getKind();
double getX();
double getY();
Map<String, Object> getProps();
Entity getParent();
void setParent(Entity parent);
List<Entity> getChildren();
Space getSpace();
```

### Dimensional Drilling

```java
Entity drillDown();                    // First child
Entity drillDown(String name);         // Child by name
Entity drillUp();                      // Parent
Entity drillAcross(String name);       // Sibling by name
List<Entity> select(String... names);  // Multiple children
```

### Methods

```java
Entity prop(String key, Object value);          // Chainable
Entity setProps(Map<String, Object> props);     // Chainable
Entity identify(String id);                     // Chainable
Entity addChild(Entity child);                  // Chainable
Map<String, Object> toMap();
```

### Example

```java
// Set up hierarchy
engine.setParent(car);
car.getChildren().add(engine);
// Or use helper:
car.addChild(engine).addChild(transmission);

// Dimensional drilling (NOT JOINs!)
Entity myEngine = car.drillDown("engine");
Entity parent = myEngine.drillUp();
Entity trans = myEngine.drillAcross("transmission");

// Select multiple
List<Entity> parts = car.select("engine", "transmission");

// Chain properties
engine.prop("horsepower", 670)
      .prop("turbo", true)
      .prop("fuel", "electric");
```

---

## Global Lookup (Static Methods)

```java
import static com.butterflyfx.helix.Helix.*;

// Find by id
Entity car = find("VIN-001");

// Find by criteria
List<Entity> cars = findBy(Map.of("name", "car"));

// Specific methods
Entity entity = byId("VIN-001");
List<Entity> entities = byName("car");
List<Entity> entities = byKind("rectangle");
List<Entity> entities = byAttribute("color", "red");
List<Entity> entities = byDimension("vehicles");
List<Entity> entities = query(Map.of("kind", "rectangle", "color", "red"));
```

---

## Class: `Operations`

### Get Operations

```java
Operations ops = Helix.operations();
// or
Operations ops = Operations.getInstance();
```

### Lookup Methods

```java
Operation byId(String id);
List<Operation> byName(String name);
List<Operation> byKind(String kind);
List<Operation> byCategory(String category);
List<Operation> all();
boolean has(String name);
int size();
```

### Built-in Operations

```java
// Math
double add(double a, double b);
double subtract(double a, double b);
double multiply(double a, double b);
double divide(double a, double b);
double sqrt(double x);
double pow(double x, double n);
double abs(double x);

// Transform (generic)
<T extends Comparable<T>> List<T> sort(List<T> list);
<T> List<T> reverse(List<T> list);
<T> List<T> unique(List<T> list);

// Query
<T> int count(List<T> list);
<T> T first(List<T> list);
<T> T last(List<T> list);
double sum(List<? extends Number> list);
<T extends Comparable<T>> T min(List<T> list);
<T extends Comparable<T>> T max(List<T> list);
```

### Call Dynamic Operations

```java
<T> T call(String name, Object... args);
```

### Register Operations

```java
// Fluent builder
Helix.operation("square", (Integer x) -> x * x)
    .id("square_v1")
    .kind("function")
    .category("math")
    .description("Square a number")
    .register();

// Or directly
Operations.register("double", (Integer x) -> x * 2, "math");
```

### Example

```java
Operations ops = operations();

// Use built-in operations
List<Integer> sorted = ops.sort(List.of(3, 1, 2));  // [1, 2, 3]
double total = ops.add(10, 5);                       // 15.0
Integer first = ops.first(ops.sort(List.of(5, 3, 8, 1))); // 1

// Register custom operation
operation("double", (Integer x) -> x * 2)
    .category("math")
    .register();

int result = ops.<Integer>call("double", 21); // 42

// Lookup operations
List<Operation> mathOps = ops.byCategory("math");
mathOps.forEach(op -> System.out.println(op.getName()));
```

---

## Class: `Operation`

### Properties

```java
String getId();
String getName();
String getKind();
String getCategory();
String getDescription();
```

### Methods

```java
<T> T call(Object... args);
Operation drillDown();
Operation drillDown(String name);
Operation drillUp();
Operation drillAcross(String name);
Operation link(String name, Operation other);
Operation addChild(Operation child);
```

---

## Class: `Datastore`

### Builder

```java
Datastore ds = Helix.datastore("vehicles")
    .fetchFn(id -> database.findById(id))
    .persistFn((id, data) -> database.save(id, data))
    .checkChangedFn((id, version) -> database.isModified(id, version))
    .writable(true)
    .build();
```

### Methods

```java
Entity get(String id);
Entity get(String id, Space space);
void setInstanceAttr(String entityId, String attr, Object value);
Object getInstanceAttr(String entityId, String attr);
boolean persist(Entity entity);
void invalidate(String id);
void clearCache();

String getName();
boolean isWritable();
```

### Example

```java
// Simulated database
Map<String, Map<String, Object>> mockDb = new HashMap<>();
mockDb.put("VIN-001", Map.of("name", "car", "color", "red", "brand", "Tesla"));
mockDb.put("VIN-002", Map.of("name", "truck", "color", "blue", "brand", "Ford"));

// Register datastore
Datastore carsDb = datastore("vehicles")
    .fetchFn(vin -> mockDb.get(vin))
    .persistFn((vin, data) -> {
        mockDb.put(vin, data);
        return true;
    })
    .writable(true)
    .build();

// First access → DB fetch
Entity car = carsDb.get("VIN-001");
System.out.println(car.getProps().get("color")); // "red"

// Second access → cached (no DB hit)
Entity sameCar = carsDb.get("VIN-001");

// Instance attribute (ephemeral)
carsDb.setInstanceAttr("VIN-001", "tempFlag", true);

// Persist
carsDb.persist(car);
```

---

## Functional Interfaces

```java
@FunctionalInterface
public interface FetchFunction {
    Map<String, Object> apply(String id);
}

@FunctionalInterface
public interface PersistFunction {
    boolean apply(String id, Map<String, Object> data);
}

@FunctionalInterface
public interface CheckChangedFunction {
    boolean apply(String id, Object version);
}

@FunctionalInterface
public interface UnaryOperation<T, R> {
    R apply(T arg);
}

@FunctionalInterface
public interface BinaryOperation<T, U, R> {
    R apply(T arg1, U arg2);
}
```

---

## Records (Java 17+)

```java
public record EntityOpts(
    String id,
    String name,
    String position,
    Map<String, Object> props
) {}

public record DimensionOpts(
    double width,
    double height
) {}

public record OperationOpts(
    String id,
    String kind,
    String category,
    String description
) {}
```

---

## Complete Example

```java
package com.example;

import com.butterflyfx.helix.*;
import static com.butterflyfx.helix.Helix.*;
import java.util.*;

public class DimensionalDemo {
    public static void main(String[] args) {
        // ============================================
        // 1. Create dimension with entities
        // ============================================
        Dimension vehicles = dimension("vehicles");
        
        Entity car = vehicles.rectangle()
            .id("VIN-001")
            .name("car")
            .prop("color", "red")
            .prop("brand", "Tesla")
            .prop("model", "Model S")
            .build();
        
        Entity engine = vehicles.rectangle()
            .id("ENGINE-001")
            .name("engine")
            .prop("horsepower", 670)
            .prop("type", "electric")
            .build();
        
        car.addChild(engine);
        
        // ============================================
        // 2. Multi-path lookup
        // ============================================
        Entity tesla = find("VIN-001");
        List<Entity> allCars = findBy(Map.of("name", "car"));
        
        // ============================================
        // 3. Dimensional drilling
        // ============================================
        Entity myEngine = car.drillDown("engine");
        Entity myCar = myEngine.drillUp();
        
        // ============================================
        // 4. Operations
        // ============================================
        Operations ops = operations();
        
        // Built-in
        List<Integer> sortedList = ops.sort(List.of(3, 1, 2));
        double total = ops.sum(List.of(1.0, 2.0, 3.0, 4.0, 5.0));
        
        // Custom
        operation("getBrand", (Entity e) -> 
            e.getProps().getOrDefault("brand", "Unknown").toString()
        ).category("vehicle").register();
        
        String brand = ops.<String>call("getBrand", car); // "Tesla"
        
        // ============================================
        // 5. Chained operations
        // ============================================
        List<Integer> prices = List.of(50000, 75000, 100000, 45000);
        Integer minPrice = ops.first(ops.sort(prices));
        Integer maxPrice = ops.last(ops.sort(prices));
        
        System.out.println("Tesla: " + tesla);
        System.out.println("Engine: " + myEngine);
        System.out.println("Brand: " + brand);
        System.out.printf("Price range: $%d - $%d%n", minPrice, maxPrice);
    }
}
```

---

## Thread Safety

```java
// Operations singleton is thread-safe
Operations ops = operations(); // Safe for concurrent access

// For dimension modifications, use synchronized
synchronized(dimension) {
    dimension.rectangle()
        .id("NEW-001")
        .build();
}

// Or use concurrent collections
ConcurrentHashMap<String, Entity> entityCache = new ConcurrentHashMap<>();
```

---

## Exceptions

```java
// Not found returns null (not exception)
Entity entity = dim.byId("NONEXISTENT"); // Returns null

// For strict mode, use:
Entity entity = dim.byIdOrThrow("VIN-001"); // Throws EntityNotFoundException

// Datastore exceptions
try {
    datastore.persist(entity);
} catch (DatastoreNotWritableException e) {
    // Handle read-only datastore
} catch (PersistenceException e) {
    // Handle persistence failure
}
```

---

**© 2026 ButterflyFX. All rights reserved.**
