# ButterflyFX Dimensional API — Node.js Reference

**Version:** 1.0.0  
**Node.js:** 18+  
**Package:** `@butterflyfx/helix`

---

## Installation

```bash
npm install @butterflyfx/helix
# or
yarn add @butterflyfx/helix
```

## Quick Start

```javascript
const { dimension, find, operations, operation } = require('@butterflyfx/helix');

// Create dimension
const dim = dimension('vehicles');

// Create entities
const car = dim.rectangle({ id: 'VIN-001', name: 'car', color: 'red' });
const engine = dim.rectangle({ id: 'ENGINE-001', name: 'engine' });
car.children.push(engine);
engine.parent = car;

// Lookup
const found = find('VIN-001');
const allCars = find({ name: 'car' });

// Operations
const ops = operations();
const sortedData = ops.sort([3, 1, 2]); // [1, 2, 3]

// Custom operation
operation('square', (x) => x * x, { category: 'math' });
ops.square(7); // 49
```

---

## Module Exports

```javascript
const {
  // Dimension
  dimension,
  Dimension,
  
  // Space
  space,
  Space,
  
  // Entity
  Entity,
  
  // Builders
  ShapeBuilder,
  TextBuilder,
  LineBuilder,
  
  // Shape creators
  shape,
  rectangle,
  circle,
  triangle,
  polygon,
  text,
  point,
  line,
  group,
  
  // Global lookup
  find,
  byId,
  byName,
  byKind,
  byAttribute,
  byDimension,
  query,
  
  // Datastore
  Datastore,
  registerDatastore,
  getDatastore,
  
  // Operations
  Operation,
  Operations,
  operations,
  operation,
  
  // Registry
  registerDimension,
  clearIndices,
} = require('@butterflyfx/helix');
```

---

## Class: `Dimension`

### Constructor

```javascript
function dimension(name, options = {})

// Options
{
  width: 100.0,   // Dimension width
  height: 100.0   // Dimension height
}
```

### Properties

```javascript
dim.name    // String: Dimension name
dim.space   // Space: Underlying space
```

### Entity Creation Methods

```javascript
// All methods accept an options object
dim.rectangle({ id, name, position, ...props })
dim.circle({ id, name, position, ...props })
dim.triangle({ id, name, position, ...props })
dim.polygon({ id, name, position, sides, ...props })
dim.text(content, { id, name, position, ...props })
dim.point({ id, name, position, ...props })
dim.line({ id, name, start, end, ...props })
dim.group(entities, { id, name, position, ...props })
```

### Lookup Methods

```javascript
dim.byId(id)              // Entity | null
dim.byName(name)          // Entity[]
dim.byKind(kind)          // Entity[]
dim.all()                 // Entity[]
dim.query(criteria)       // Entity[]
dim.invoke(identifier)    // Entity | null
```

### Shorthand Access

```javascript
dim.get('car')            // Entity | Entity[]
dim['VIN-001']            // Entity (throws if not found)
```

### Example

```javascript
const { dimension } = require('@butterflyfx/helix');

// Create dimension
const physics = dimension('physics', { width: 800, height: 600 });

// Create entities
const car = physics.rectangle({
  id: 'VIN-001',
  name: 'car',
  color: 'red',
  brand: 'Tesla'
});

const engine = physics.rectangle({
  id: 'ENGINE-001',
  name: 'engine',
  horsepower: 670
});

// Link parent-child
engine.parent = car;
car.children.push(engine);

// Lookup
physics.byId('VIN-001');        // car entity
physics.byName('engine');       // [engine]
physics.get('car');             // car entity
physics['VIN-001'];             // car entity
```

---

## Class: `Entity`

### Properties

```javascript
entity.id         // String: Unique identifier
entity.name       // String: Entity name/type
entity.kind       // String: Shape type
entity.x          // Number: X coordinate
entity.y          // Number: Y coordinate
entity.props      // Object: Custom properties
entity.parent     // Entity | null: Parent entity
entity.children   // Entity[]: Child entities
entity.space      // Space: Parent space
```

### Dimensional Drilling

```javascript
entity.drillDown(name)     // Entity | null - Navigate to child
entity.drillUp()           // Entity | null - Navigate to parent
entity.drillAcross(name)   // Entity | null - Navigate to sibling
entity.select(...names)    // Entity[] - Select multiple children
```

### Property Methods

```javascript
entity.prop(props)         // Entity - Set properties (chainable)
entity.identify(id)        // Entity - Set identity
entity.toDict()            // Object - Export to dictionary
```

### Example

```javascript
const { dimension } = require('@butterflyfx/helix');

const dim = dimension('vehicles');
const car = dim.rectangle({ id: 'VIN-001', name: 'car' });
const engine = dim.rectangle({ id: 'ENGINE-001', name: 'engine' });
const transmission = dim.rectangle({ id: 'TRANS-001', name: 'transmission' });

// Set up hierarchy
engine.parent = car;
transmission.parent = car;
car.children.push(engine, transmission);

// Dimensional drilling (NOT JOINs!)
const myEngine = car.drillDown('engine');
const parent = myEngine.drillUp();
const trans = myEngine.drillAcross('transmission');

// Select multiple
const parts = car.select('engine', 'transmission');

// Chain properties
engine
  .prop({ horsepower: 670, turbo: true })
  .prop({ fuel: 'electric' });
```

---

## Global Lookup Functions

### find()

```javascript
function find(idOrCriteria, criteria = {})

// Usage
find('VIN-001')                      // By id
find({ name: 'car' })                // By name
find({ kind: 'rectangle', color: 'red' })  // By criteria
```

### Specific Methods

```javascript
byId(id)                   // Entity | null
byName(name)               // Entity[]
byKind(kind)               // Entity[]
byAttribute(attr, value)   // Entity[]
byDimension(name)          // Entity[]
query(criteria)            // Entity[]
```

### Example

```javascript
const { find, byId, byName, byKind, byAttribute } = require('@butterflyfx/helix');

// Find by id
const car = find('VIN-001');

// Find by name
const cars = find({ name: 'car' });

// Find by kind and attribute
const redRectangles = find({ kind: 'rectangle', color: 'red' });

// Specific methods
byId('VIN-001');
byName('car');
byKind('circle');
byAttribute('color', 'red');
```

---

## Class: `Operations`

### Get Operations

```javascript
const ops = operations();
```

### Methods

```javascript
ops.byId(id)               // Operation | null
ops.byName(name)           // Operation[]
ops.byKind(kind)           // Operation[]
ops.byCategory(category)   // Operation[]
ops.all()                  // Operation[]
```

### Shorthand Access

```javascript
ops.sort([3, 1, 2])        // Call operation
ops['sqrt']                // Get operation by id/name
ops.has('sqrt')            // Check if operation exists
ops.length                 // Number of operations
```

### Register Operations

```javascript
// Direct registration
operation('square', (x) => x * x, { category: 'math' });

// With full options
operation('calculate', calculateFn, {
  id: 'calc_v2',
  kind: 'function',
  category: 'math',
  description: 'Advanced calculation'
});
```

### Built-in Operations

```javascript
// Math
ops.add(a, b)              // a + b
ops.subtract(a, b)         // a - b
ops.multiply(a, b)         // a * b
ops.divide(a, b)           // a / b
ops.sqrt(x)                // √x
ops.pow(x, n)              // x^n
ops.abs(x)                 // |x|

// Transform
ops.sort(array)            // Sorted array
ops.reverse(array)         // Reversed array
ops.unique(array)          // Unique values

// Query
ops.count(array)           // Length
ops.first(array)           // First item
ops.last(array)            // Last item
ops.sum(array)             // Sum
ops.min(array)             // Minimum
ops.max(array)             // Maximum
```

### Example

```javascript
const { operations, operation } = require('@butterflyfx/helix');

const ops = operations();

// Use built-in operations
ops.sort([3, 1, 2]);                     // [1, 2, 3]
ops.add(10, 5);                          // 15
ops.first(ops.sort([5, 3, 8, 1]));       // 1

// Register custom operation
operation('double', (x) => x * 2, { category: 'math' });
ops.double(21);                          // 42

// Lookup operations
const mathOps = ops.byCategory('math');
console.log(mathOps.map(op => op.name));
```

---

## Class: `Datastore`

### Register

```javascript
function registerDatastore(name, options)

// Options
{
  fetchFn: (id) => object | null,           // Required
  persistFn: (id, data) => boolean,         // Optional
  checkChangedFn: (id, version) => boolean, // Optional
  writable: false                           // Default
}
```

### Methods

```javascript
ds.get(id, space)                  // Entity | null
ds.setInstanceAttr(entityId, attr, value)
ds.getInstanceAttr(entityId, attr) // any | null
ds.persist(entity)                 // boolean
ds.invalidate(id)
ds.clearCache()
```

### Example

```javascript
const { registerDatastore } = require('@butterflyfx/helix');

// Simulated database
const mockDb = {
  'VIN-001': { name: 'car', color: 'red', brand: 'Tesla' },
  'VIN-002': { name: 'truck', color: 'blue', brand: 'Ford' },
};

// Register datastore
const carsDb = registerDatastore('vehicles', {
  fetchFn: (vin) => mockDb[vin] || null,
  persistFn: (vin, data) => {
    mockDb[vin] = data;
    return true;
  },
  writable: true
});

// First access → DB fetch
const car = carsDb.get('VIN-001');
console.log(car.props.color);  // "red"

// Second access → cached (no DB hit)
const sameCar = carsDb.get('VIN-001');

// Instance attribute (ephemeral)
carsDb.setInstanceAttr('VIN-001', 'tempFlag', true);

// Persist
carsDb.persist(car);
```

---

## Complete Example

```javascript
const {
  dimension,
  find,
  operations,
  operation,
  registerDatastore
} = require('@butterflyfx/helix');

// ============================================
// 1. Create dimension with entities
// ============================================
const vehicles = dimension('vehicles');

const car = vehicles.rectangle({
  id: 'VIN-001',
  name: 'car',
  color: 'red',
  brand: 'Tesla',
  model: 'Model S'
});

const engine = vehicles.rectangle({
  id: 'ENGINE-001',
  name: 'engine',
  horsepower: 670,
  type: 'electric'
});

// Link hierarchy
engine.parent = car;
car.children.push(engine);

// ============================================
// 2. Multi-path lookup
// ============================================
const tesla = find('VIN-001');
const allCars = find({ name: 'car' });
vehicles.get('car');
vehicles['VIN-001'];

// ============================================
// 3. Dimensional drilling
// ============================================
const myEngine = car.drillDown('engine');
const myCar = myEngine.drillUp();

// ============================================
// 4. Operations
// ============================================
const ops = operations();

// Built-in
const sortedList = ops.sort([3, 1, 2]);
const total = ops.sum([1, 2, 3, 4, 5]);

// Custom
operation('getBrand', (entity) => entity.props.brand || 'Unknown', {
  category: 'vehicle'
});
const brand = ops.getBrand(car);  // "Tesla"

// ============================================
// 5. Chained operations
// ============================================
const prices = [50000, 75000, 100000, 45000];
const minPrice = ops.first(ops.sort(prices));  // 45000
const maxPrice = ops.last(ops.sort(prices));   // 100000

console.log(`Price range: $${minPrice} - $${maxPrice}`);
```

---

## ES Module Syntax

```javascript
import {
  dimension,
  find,
  operations,
  operation
} from '@butterflyfx/helix';
```

---

## TypeScript Support

TypeScript definitions are included. See the TypeScript API reference for full type definitions.

---

**© 2026 ButterflyFX. All rights reserved.**
