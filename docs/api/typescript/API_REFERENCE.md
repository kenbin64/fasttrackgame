# ButterflyFX Dimensional API — TypeScript Reference

**Version:** 1.0.0  
**TypeScript:** 5.0+  
**Package:** `@butterflyfx/helix`

---

## Installation

```bash
npm install @butterflyfx/helix
# or
yarn add @butterflyfx/helix
```

## Quick Start

```typescript
import { dimension, find, operations, operation } from '@butterflyfx/helix';

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
operation('square', (x: number) => x * x, { category: 'math' });
ops.square(7); // 49
```

---

## Type Definitions

### Core Types

```typescript
// Dimension
interface Dimension {
  readonly name: string;
  readonly space: Space;
  
  rectangle(options: EntityOptions): Entity;
  circle(options: EntityOptions): Entity;
  triangle(options: EntityOptions): Entity;
  polygon(options: PolygonOptions): Entity;
  text(content: string, options?: EntityOptions): Entity;
  point(options?: EntityOptions): Entity;
  line(options?: LineOptions): Entity;
  group(entities: Entity[], options?: EntityOptions): Entity;
  
  byId(id: string): Entity | null;
  byName(name: string): Entity[];
  byKind(kind: string): Entity[];
  all(): Entity[];
  query(criteria: QueryCriteria): Entity[];
  invoke(identifier: string): Entity | null;
  
  get(nameOrId: string): Entity | Entity[];
}

// Entity
interface Entity {
  readonly id: string;
  name: string;
  kind: string;
  x: number;
  y: number;
  props: Record<string, any>;
  parent: Entity | null;
  children: Entity[];
  space: Space;
  
  drillDown(name?: string): Entity | null;
  drillUp(): Entity | null;
  drillAcross(name: string): Entity | null;
  select(...names: string[]): Entity[];
  
  prop(props: Record<string, any>): Entity;
  identify(id: string): Entity;
  toDict(): Record<string, any>;
}

// Operation
interface Operation {
  readonly id: string;
  readonly name: string;
  readonly kind: string;
  readonly category: string;
  readonly description: string;
  
  (...args: any[]): any;
  
  drillDown(name?: string): Operation | null;
  drillUp(): Operation | null;
  drillAcross(name: string): Operation | null;
  link(name: string, op: Operation): Operation;
  child(op: Operation): Operation;
}

// Operations
interface Operations {
  readonly name: string;
  
  byId(id: string): Operation | null;
  byName(name: string): Operation[];
  byKind(kind: string): Operation[];
  byCategory(category: string): Operation[];
  all(): Operation[];
  has(name: string): boolean;
  readonly length: number;
  
  // Built-in operations
  add(a: number, b: number): number;
  subtract(a: number, b: number): number;
  multiply(a: number, b: number): number;
  divide(a: number, b: number): number;
  sqrt(x: number): number;
  pow(x: number, n: number): number;
  abs(x: number): number;
  
  sort<T>(array: T[]): T[];
  reverse<T>(array: T[]): T[];
  unique<T>(array: T[]): T[];
  
  count<T>(array: T[]): number;
  first<T>(array: T[]): T | null;
  last<T>(array: T[]): T | null;
  sum(array: number[]): number;
  min<T>(array: T[]): T;
  max<T>(array: T[]): T;
  
  // Dynamic operation access
  [operationName: string]: ((...args: any[]) => any) | any;
}

// Datastore
interface Datastore {
  readonly name: string;
  readonly writable: boolean;
  
  get(id: string, space?: Space): Entity | null;
  setInstanceAttr(entityId: string, attr: string, value: any): void;
  getInstanceAttr(entityId: string, attr: string): any | null;
  persist(entity: Entity): boolean;
  invalidate(id: string): void;
  clearCache(): void;
}
```

### Option Types

```typescript
interface EntityOptions {
  id?: string;
  name?: string;
  position?: Position;
  [key: string]: any;
}

interface PolygonOptions extends EntityOptions {
  sides?: number;
}

interface LineOptions extends EntityOptions {
  start?: Position;
  end?: Position;
}

interface QueryCriteria {
  name?: string;
  kind?: string;
  [attribute: string]: any;
}

interface DatastoreOptions {
  fetchFn: (id: string) => Record<string, any> | null;
  persistFn?: (id: string, data: Record<string, any>) => boolean;
  checkChangedFn?: (id: string, version: any) => boolean;
  writable?: boolean;
}

interface OperationOptions {
  id?: string;
  kind?: string;
  category?: string;
  description?: string;
  [key: string]: any;
}
```

### Semantic Types

```typescript
type Position = 
  | 'center' | 'top' | 'bottom' | 'left' | 'right'
  | 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right'
  | [number, number];

type Orientation = 
  | 'north' | 'south' | 'east' | 'west'
  | 'northeast' | 'northwest' | 'southeast' | 'southwest'
  | 'horizontal' | 'vertical' | 'diagonal'
  | number;

type Size = 'tiny' | 'small' | 'medium' | 'large' | 'huge' | number;

type Direction = 
  | 'up' | 'down' | 'left' | 'right'
  | 'forward' | 'backward' | 'inward' | 'outward';
```

---

## Function Signatures

### Dimension

```typescript
function dimension(name: string, options?: {
  width?: number;
  height?: number;
}): Dimension;
```

### Global Lookup

```typescript
function find(id: string): Entity | null;
function find(criteria: QueryCriteria): Entity[];

function byId(id: string): Entity | null;
function byName(name: string): Entity[];
function byKind(kind: string): Entity[];
function byAttribute(attr: string, value: any): Entity[];
function byDimension(name: string): Entity[];
function query(criteria: QueryCriteria): Entity[];
```

### Operations

```typescript
function operations(): Operations;

function operation(name: string, fn: (...args: any[]) => any, options?: OperationOptions): Operation;
function operation<T extends (...args: any[]) => any>(fn: T, options?: OperationOptions): Operation;
```

### Datastore

```typescript
function registerDatastore(name: string, options: DatastoreOptions): Datastore;
function getDatastore(name: string): Datastore | null;
```

---

## Usage Examples

### Dimension and Entities

```typescript
import { dimension, Entity } from '@butterflyfx/helix';

const vehicles = dimension('vehicles', { width: 800, height: 600 });

const car: Entity = vehicles.rectangle({
  id: 'VIN-001',
  name: 'car',
  color: 'red',
  brand: 'Tesla'
});

const engine: Entity = vehicles.rectangle({
  id: 'ENGINE-001',
  name: 'engine',
  horsepower: 670
});

// Parent-child relationship
engine.parent = car;
car.children.push(engine);

// Lookup
const found: Entity | null = vehicles.byId('VIN-001');
const engines: Entity[] = vehicles.byName('engine');
```

### Dimensional Drilling

```typescript
import { dimension } from '@butterflyfx/helix';

const dim = dimension('vehicles');
const car = dim.rectangle({ id: 'VIN-001', name: 'car' });
const engine = dim.rectangle({ id: 'ENGINE-001', name: 'engine' });
const transmission = dim.rectangle({ id: 'TRANS-001', name: 'transmission' });

engine.parent = car;
transmission.parent = car;
car.children.push(engine, transmission);

// Drill (NOT JOINs!)
const myEngine = car.drillDown('engine');        // Entity | null
const parent = myEngine?.drillUp();              // Entity | null
const trans = myEngine?.drillAcross('transmission'); // Entity | null

// Select multiple
const parts = car.select('engine', 'transmission'); // Entity[]
```

### Operations

```typescript
import { operations, operation, Operation } from '@butterflyfx/helix';

const ops = operations();

// Built-in operations (fully typed)
const sorted: number[] = ops.sort([3, 1, 2]);
const total: number = ops.sum([1, 2, 3, 4, 5]);

// Register custom operation
const squareOp: Operation = operation(
  'square',
  (x: number): number => x * x,
  { category: 'math' }
);

// Use custom operation
const result: number = ops.square(7); // 49

// Lookup
const mathOps: Operation[] = ops.byCategory('math');
```

### Datastore with Types

```typescript
import { registerDatastore, Datastore, Entity } from '@butterflyfx/helix';

interface VehicleData {
  name: string;
  color: string;
  brand: string;
}

const mockDb: Record<string, VehicleData> = {
  'VIN-001': { name: 'car', color: 'red', brand: 'Tesla' },
};

const vehicleStore: Datastore = registerDatastore('vehicles', {
  fetchFn: (vin: string): VehicleData | null => mockDb[vin] ?? null,
  persistFn: (vin: string, data: Record<string, any>): boolean => {
    mockDb[vin] = data as VehicleData;
    return true;
  },
  writable: true
});

const car: Entity | null = vehicleStore.get('VIN-001');
if (car) {
  console.log(car.props.color); // "red"
}
```

---

## Generic Operations

```typescript
import { operations } from '@butterflyfx/helix';

const ops = operations();

// Generic sort
const numbers: number[] = ops.sort([3, 1, 2]);
const strings: string[] = ops.sort(['c', 'a', 'b']);

// Generic first/last
const firstNum: number | null = ops.first([1, 2, 3]);
const lastStr: string | null = ops.last(['a', 'b', 'c']);

// Chained operations
const minPrice: number | null = ops.first(ops.sort([50000, 75000, 45000]));
```

---

## Declaration Merging

Extend the Operations interface for custom operations:

```typescript
declare module '@butterflyfx/helix' {
  interface Operations {
    square(x: number): number;
    getBrand(entity: Entity): string;
  }
}

// Now fully typed
const ops = operations();
ops.square(7);      // number
ops.getBrand(car);  // string
```

---

## Complete Example

```typescript
import {
  dimension,
  find,
  operations,
  operation,
  registerDatastore,
  Entity,
  Operation,
  Datastore
} from '@butterflyfx/helix';

// Extend Operations type for custom operations
declare module '@butterflyfx/helix' {
  interface Operations {
    getBrand(entity: Entity): string;
  }
}

// ============================================
// 1. Create dimension with entities
// ============================================
const vehicles = dimension('vehicles');

const car: Entity = vehicles.rectangle({
  id: 'VIN-001',
  name: 'car',
  color: 'red',
  brand: 'Tesla',
  model: 'Model S'
});

const engine: Entity = vehicles.rectangle({
  id: 'ENGINE-001',
  name: 'engine',
  horsepower: 670,
  type: 'electric'
});

engine.parent = car;
car.children.push(engine);

// ============================================
// 2. Multi-path lookup
// ============================================
const tesla: Entity | null = find('VIN-001');
const allCars: Entity[] = find({ name: 'car' });

// ============================================
// 3. Dimensional drilling
// ============================================
const myEngine: Entity | null = car.drillDown('engine');
const myCar: Entity | null = myEngine?.drillUp() ?? null;

// ============================================
// 4. Operations
// ============================================
const ops = operations();

// Built-in
const sortedList: number[] = ops.sort([3, 1, 2]);
const total: number = ops.sum([1, 2, 3, 4, 5]);

// Custom
operation('getBrand', (entity: Entity): string => 
  entity.props.brand ?? 'Unknown',
  { category: 'vehicle' }
);

const brand: string = ops.getBrand(car); // "Tesla"

// ============================================
// 5. Chained operations
// ============================================
const prices: number[] = [50000, 75000, 100000, 45000];
const minPrice: number | null = ops.first(ops.sort(prices));
const maxPrice: number | null = ops.last(ops.sort(prices));

console.log(`Price range: $${minPrice} - $${maxPrice}`);
```

---

**© 2026 ButterflyFX. All rights reserved.**
