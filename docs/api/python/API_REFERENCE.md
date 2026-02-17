# ButterflyFX Dimensional API — Python Reference

**Version:** 1.0.0  
**Python:** 3.9+  
**Package:** `helix`

---

## Installation

```bash
pip install butterflyfx-helix
```

## Quick Start

```python
from helix import dimension, find, operations, operation

# Create dimension
dim = dimension("vehicles")

# Create entities
car = dim.rectangle(id="VIN-001", name="car", color="red")
engine = dim.rectangle(id="ENGINE-001", name="engine")
car.children.append(engine)
engine.parent = car

# Lookup
found = find("VIN-001")
all_cars = find(name="car")

# Operations
ops = operations()
sorted_data = ops.sort([3, 1, 2])  # [1, 2, 3]

# Custom operation
@operation
def square(x):
    return x * x

ops.square(7)  # 49
```

---

## Module: `helix`

### Imports

```python
from helix import (
    # Dimension
    dimension, Dimension,
    
    # Space
    space, Space,
    
    # Entity
    Entity,
    
    # Builders
    ShapeBuilder, TextBuilder, LineBuilder,
    
    # Shape creators
    shape, rectangle, circle, triangle, polygon,
    text, point, line, group,
    
    # Semantic enums
    Position, Direction, Orientation, Size,
    
    # Global lookup
    find,
    by_id, by_name, by_kind, by_attribute, by_attr, by_prop,
    by_dimension, dim,
    query, find_entities,
    
    # Identity
    identity, by_identity, register_identity, clear_identities,
    IdentityLookup,
    
    # Datastore
    Datastore, register_datastore, get_datastore,
    
    # Operations
    Operation, Operations, operations, operation,
    
    # Registry
    register_dimension, clear_indices,
    
    # Advanced
    advanced,
)
```

---

## Class: `Dimension`

### Constructor

```python
def dimension(
    name: str,
    width: float = 100.0,
    height: float = 100.0
) -> Dimension
```

### Properties

```python
dim.name: str              # Dimension name
dim.space: Space           # Underlying space
```

### Entity Creation Methods

```python
def rectangle(
    self,
    id: Optional[str] = None,
    name: str = "rectangle",
    position: str = "center",
    **props
) -> Entity

def circle(
    self,
    id: Optional[str] = None,
    name: str = "circle",
    position: str = "center",
    **props
) -> Entity

def triangle(
    self,
    id: Optional[str] = None,
    name: str = "triangle",
    position: str = "center",
    **props
) -> Entity

def polygon(
    self,
    id: Optional[str] = None,
    name: str = "polygon",
    position: str = "center",
    sides: int = 6,
    **props
) -> Entity

def text(
    self,
    content: str,
    id: Optional[str] = None,
    name: str = "text",
    position: str = "center",
    **props
) -> Entity

def point(
    self,
    id: Optional[str] = None,
    name: str = "point",
    position: str = "center",
    **props
) -> Entity

def line(
    self,
    id: Optional[str] = None,
    name: str = "line",
    start: str = "center",
    end: str = "right",
    **props
) -> Entity

def group(
    self,
    *entities,
    id: Optional[str] = None,
    name: str = "group",
    position: str = "center",
    **props
) -> Entity
```

### Lookup Methods

```python
def by_id(self, id: str) -> Optional[Entity]
def by_name(self, name: str) -> List[Entity]
def by_kind(self, kind: str) -> List[Entity]
def all(self) -> List[Entity]
def query(self, **criteria) -> List[Entity]
def invoke(self, identifier: str) -> Optional[Entity]
```

### Shorthand Access

```python
dim.car                    # Returns Entity or List[Entity]
dim["VIN-001"]             # Returns Entity (raises KeyError if not found)
```

### Example

```python
from helix import dimension

# Create dimension
physics = dimension("physics", 800, 600)

# Create entities
car = physics.rectangle(id="VIN-001", name="car", color="red", brand="Tesla")
engine = physics.rectangle(id="ENGINE-001", name="engine", horsepower=670)

# Link parent-child
engine.parent = car
car.children.append(engine)

# Lookup
physics.by_id("VIN-001")           # <rectangle:car>
physics.by_name("engine")          # [<rectangle:engine>]
physics.car                        # <rectangle:car>
physics["VIN-001"]                 # <rectangle:car>
```

---

## Class: `Entity`

### Properties

```python
entity.id: str                     # Unique identifier
entity.name: str                   # Entity name/type
entity.kind: str                   # Shape type
entity.x: float                    # X coordinate
entity.y: float                    # Y coordinate
entity.props: Dict[str, Any]       # Custom properties
entity.parent: Optional[Entity]    # Parent entity
entity.children: List[Entity]      # Child entities
entity.space: Space                # Parent space
```

### Dimensional Drilling

```python
def drillDown(self, name: Optional[str] = None) -> Optional[Entity]:
    """Navigate to child entity by name, or first child if name is None."""

def drillUp(self) -> Optional[Entity]:
    """Navigate to parent entity."""

def drillAcross(self, name: str) -> Optional[Entity]:
    """Navigate to sibling entity by name."""

def select(self, *names: str) -> List[Entity]:
    """Select multiple children by name."""
```

### Property Methods

```python
def prop(self, **kwargs) -> Entity:
    """Set properties (chainable)."""

def identify(self, id: str) -> Entity:
    """Set entity identity."""

def to_dict(self) -> Dict[str, Any]:
    """Export entity to dictionary."""
```

### Example

```python
from helix import dimension

dim = dimension("vehicles")
car = dim.rectangle(id="VIN-001", name="car")
engine = dim.rectangle(id="ENGINE-001", name="engine")
transmission = dim.rectangle(id="TRANS-001", name="transmission")

# Set up hierarchy
engine.parent = car
transmission.parent = car
car.children.extend([engine, transmission])

# Dimensional drilling (NOT JOINs!)
engine = car.drillDown("engine")           # Get engine from car
parent = engine.drillUp()                  # Get back to car
trans = engine.drillAcross("transmission") # Get sibling

# Select multiple
parts = car.select("engine", "transmission")  # [engine, transmission]

# Chain properties
engine.prop(horsepower=670, turbo=True).prop(fuel="electric")
```

---

## Global Lookup Functions

### find()

```python
def find(
    id: Optional[str] = None,
    name: Optional[str] = None,
    kind: Optional[str] = None,
    **attributes
) -> Union[Entity, List[Entity], None]
```

### Specific Methods

```python
def by_id(id: str) -> Optional[Entity]
def by_name(name: str) -> List[Entity]
def by_kind(kind: str) -> List[Entity]
def by_attribute(attr: str, value: Any) -> List[Entity]
def by_attr(attr: str, value: Any) -> List[Entity]  # Alias
def by_prop(attr: str, value: Any) -> List[Entity]  # Alias
def by_dimension(name: str) -> List[Entity]
def dim(name: str) -> List[Entity]  # Alias
def query(**criteria) -> List[Entity]
```

### Example

```python
from helix import find, by_id, by_name, by_kind, by_attribute

# Find by id
car = find("VIN-001")

# Find by name
cars = find(name="car")

# Find by kind and attribute
red_rectangles = find(kind="rectangle", color="red")

# Specific methods
by_id("VIN-001")
by_name("car")
by_kind("circle")
by_attribute("color", "red")
```

---

## Class: `Operations`

The operations dimension — functions as dimensional substrates.

### Get Operations

```python
def operations() -> Operations
```

### Methods

```python
def by_id(self, id: str) -> Optional[Operation]
def by_name(self, name: str) -> List[Operation]
def by_kind(self, kind: str) -> List[Operation]
def by_category(self, category: str) -> List[Operation]
def all(self) -> List[Operation]
```

### Shorthand Access

```python
ops.sort([3, 1, 2])        # Call operation
ops["sqrt"]                 # Get operation by id/name
"sqrt" in ops               # Check if operation exists
len(ops)                    # Number of operations
for op in ops: ...          # Iterate operations
```

### Register Operations

```python
# Decorator (no args)
@operation
def square(x):
    return x * x

# Decorator (with args)
@operation("sq", category="math")
def square(x):
    return x * x

# Direct call
operation("negate", lambda x: -x, category="math")
```

### Built-in Operations

```python
# Math
ops.add(a, b)              # a + b
ops.subtract(a, b)         # a - b
ops.multiply(a, b)         # a * b
ops.divide(a, b)           # a / b
ops.sqrt(x)                # √x
ops.pow(x, n)              # x^n
ops.abs(x)                 # |x|

# Transform
ops.sort(sequence)         # Sorted list
ops.reverse(sequence)      # Reversed list
ops.unique(sequence)       # Unique values

# Query
ops.count(sequence)        # Length
ops.first(sequence)        # First item
ops.last(sequence)         # Last item
ops.sum(sequence)          # Sum
ops.min(sequence)          # Minimum
ops.max(sequence)          # Maximum
```

### Example

```python
from helix import operations, operation

ops = operations()

# Use built-in operations
ops.sort([3, 1, 2])                    # [1, 2, 3]
ops.add(10, 5)                         # 15
ops.first(ops.sort([5, 3, 8, 1]))      # 1

# Register custom operation
@operation("double", category="math")
def double_fn(x):
    return x * 2

ops.double(21)                         # 42

# Lookup operations
math_ops = ops.by_category("math")
print([op.name for op in math_ops])
```

---

## Class: `Operation`

### Properties

```python
op.id: str                 # Unique identifier
op.name: str               # Operation name
op.kind: str               # Operation type
op.category: str           # Category (math, transform, query)
op.description: str        # Human-readable description
```

### Methods

```python
def __call__(self, *args, **kwargs) -> Any:
    """Invoke the operation."""

def drillDown(self, name: Optional[str] = None) -> Optional[Operation]
def drillUp(self) -> Optional[Operation]
def drillAcross(self, name: str) -> Optional[Operation]
def link(self, name: str, op: Operation) -> Operation
def child(self, op: Operation) -> Operation
```

---

## Class: `Datastore`

### Register

```python
def register_datastore(
    name: str,
    fetch_fn: Callable[[str], Optional[Dict[str, Any]]],
    persist_fn: Optional[Callable[[str, Dict[str, Any]], bool]] = None,
    check_changed_fn: Optional[Callable[[str, Any], bool]] = None,
    writable: bool = False
) -> Datastore
```

### Methods

```python
def get(self, id: str, space: Optional[Space] = None) -> Optional[Entity]
def set_instance_attr(self, entity_id: str, attr: str, value: Any) -> None
def get_instance_attr(self, entity_id: str, attr: str) -> Optional[Any]
def persist(self, entity: Entity) -> bool
def invalidate(self, id: str) -> None
def clear_cache(self) -> None
```

### Properties

```python
ds.name: str               # Datastore name
ds.writable: bool          # Whether writes are allowed
```

### Example

```python
from helix import register_datastore

# Simulated database
mock_db = {
    "VIN-001": {"name": "car", "color": "red", "brand": "Tesla"},
    "VIN-002": {"name": "truck", "color": "blue", "brand": "Ford"},
}

def fetch_vehicle(vin):
    return mock_db.get(vin)

def persist_vehicle(vin, data):
    mock_db[vin] = data
    return True

# Register datastore
cars_db = register_datastore(
    "vehicles",
    fetch_fn=fetch_vehicle,
    persist_fn=persist_vehicle,
    writable=True
)

# First access → DB fetch, ingest to dimension
car = cars_db.get("VIN-001")
print(car.props["color"])  # "red"

# Second access → dimensional lookup (no DB hit)
car = cars_db.get("VIN-001")

# Instance attribute (ephemeral)
cars_db.set_instance_attr("VIN-001", "temp_flag", True)

# Persist (requires writable)
cars_db.persist(car)
```

---

## Type Hints

```python
from typing import Optional, List, Dict, Any, Union, Callable, Tuple

# Function signatures
def dimension(name: str, width: float = 100.0, height: float = 100.0) -> Dimension: ...
def find(id: Optional[str] = None, **kwargs) -> Union[Entity, List[Entity], None]: ...
def operations() -> Operations: ...
def operation(name_or_fn: Union[str, Callable, None] = None, ...) -> Union[Operation, Callable]: ...
```

---

## Complete Example

```python
from helix import (
    dimension, find, operations, operation,
    register_datastore
)

# ============================================
# 1. Create dimension with entities
# ============================================
vehicles = dimension("vehicles")

car = vehicles.rectangle(
    id="VIN-001",
    name="car",
    color="red",
    brand="Tesla",
    model="Model S"
)

engine = vehicles.rectangle(
    id="ENGINE-001",
    name="engine",
    horsepower=670,
    type="electric"
)

# Link hierarchy
engine.parent = car
car.children.append(engine)

# ============================================
# 2. Multi-path lookup
# ============================================
# By id
tesla = find("VIN-001")

# By name
all_cars = find(name="car")

# Shorthand
vehicles.car
vehicles["VIN-001"]

# ============================================
# 3. Dimensional drilling
# ============================================
my_engine = car.drillDown("engine")
my_car = my_engine.drillUp()

# ============================================
# 4. Operations
# ============================================
ops = operations()

# Built-in
sorted_list = ops.sort([3, 1, 2])
total = ops.sum([1, 2, 3, 4, 5])

# Custom
@operation("get_brand", category="vehicle")
def get_brand(entity):
    return entity.props.get("brand", "Unknown")

brand = ops.get_brand(car)  # "Tesla"

# ============================================
# 5. Chained operations
# ============================================
prices = [50000, 75000, 100000, 45000]
min_price = ops.first(ops.sort(prices))  # 45000
max_price = ops.last(ops.sort(prices))   # 100000

print(f"Price range: ${min_price} - ${max_price}")
```

---

**© 2026 ButterflyFX. All rights reserved.**
