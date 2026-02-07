# ButterflyFx Dimensional Structure Specification

## Core Principles

1. **SRLs are the primary way to commune with the Core**
2. **Only the Core can commune with the Kernel**
3. **Kernel is pure 64-bit math using substrate identities**
4. **Each substrate is 1 point in a higher dimension**
5. **A point on a substrate contains ALL information from ALL lower dimensions**

## Dimensional Coordinate System

### 0D - Identity
- **x0**: Always the **identity** (64-bit substrate ID)
- This is the atomic, immutable identity of the substrate

### 1D - Attributes
- **x0**: Always the **name** of the object
- **x1, x2, x3, ..., xn**: **Attributes** of the object
- Each attribute is a 64-bit value
- 2^64 unique options per attribute position

### 2D - Relationships
- **y0**: **Name** of the relationship
- **y1**: **Type** of relationship
- **y2, y3, ..., yn**: **Attributes** of the relationship
- Relationships connect substrates dimensionally

### 3D - State & Deltas
- **z0**: The **present** state (current point in time)
- **z1, z2, ..., zn**: **Attributes of the delta** (change vectors)
- Deltas encode change without mutation

### 4D+ - Higher Dimensions
- **m0, m1, m2, ..., mn**: **Attributes, points, or objects** of the higher dimension
- Each higher dimension point encapsulates ALL lower dimensions
- **m0** is the complete object in the next dimension

## Dimensional Hierarchy

```
0D: Identity
    └─ x0 (identity)

1D: Attributes  
    ├─ x0 (name)
    ├─ x1 (attribute 1)
    ├─ x2 (attribute 2)
    └─ xn (attribute n)

2D: Relationships
    ├─ y0 (relationship name)
    ├─ y1 (relationship type)
    ├─ y2 (relationship attribute 1)
    └─ yn (relationship attribute n)

3D: State & Deltas
    ├─ z0 (present state)
    ├─ z1 (delta attribute 1)
    ├─ z2 (delta attribute 2)
    └─ zn (delta attribute n)

4D+: Higher Dimensions
    ├─ m0 (complete object in next dimension)
    ├─ m1 (higher dimension point 1)
    ├─ m2 (higher dimension point 2)
    └─ mn (higher dimension point n)
```

## Key Rules

### 1. No Iteration Required
- **Higher dimensions encapsulate lower dimensions**
- To access dimension 4, just call `substrate.dimension(4)`
- That single point IS dimensions 0, 1, 2, 3, 4 all at once
- No need to iterate through 0→1→2→3→4

### 2. 64-Bit Structure
- Each level is 64-bit (2^64 unique options)
- Enables ~18 quintillion unique values per position
- Bitwise operations for maximum efficiency

### 3. Immutability
- Substrates never mutate
- Change is dimensional promotion: x₁ + y₁ + δ(z₁) → m₁
- Creates NEW substrate in higher dimension

### 4. SRL-Based Communication
- External data enters via SRL (Substrate Resource Locator)
- SRL fetches data → Core ingests → Kernel processes
- Core is the ONLY gateway to Kernel

## Architecture Layers

```
External World
      ↓
    SRL (fetch data)
      ↓
    CORE (ingest, translate, validate)
      ↓
    KERNEL (pure 64-bit math)
```

### Core Responsibilities
- Accept SRL requests
- Translate external data → substrate identities
- Validate against 15 Laws
- Route to Kernel operations
- Return results

### Kernel Responsibilities
- Pure 64-bit mathematical operations
- Substrate identity transformations
- Dimensional promotion: promote(x₁, y₁, z₁) → m₁
- Lens invocation: invoke(substrate, lens) → value
- NO external access - Core is sole gateway

## Real-Life Pattern Mapping

### 0D - Identity (The "Who")
**What it represents:** Unique, immutable identity
**Real-world analogy:** Social Security Number, UUID, VIN, Fingerprint
**64-bit encoding:** Cryptographic hash of essential properties

**Examples:**
- Person: Hash of (birth_timestamp + birth_location + biometric)
- Car: VIN number encoded as 64-bit
- Product: SKU or barcode as 64-bit
- File: Content hash (SHA-256 truncated to 64-bit)

### 1D - Attributes (The "What")
**What it represents:** Intrinsic properties of the object
**Real-world analogy:** Name, age, color, price, dimensions
**64-bit encoding:** Each attribute slot is 64-bit

**Examples:**
- **Person:**
  - x0 = "John Doe" (name, hashed to 64-bit)
  - x1 = 946684800 (birth timestamp)
  - x2 = 175 (height in cm)
  - x3 = 70 (weight in kg)

- **Car:**
  - x0 = "Toyota Camry" (model name)
  - x1 = 2024 (year)
  - x2 = 15000 (mileage)
  - x3 = 25000 (price in USD)

- **Product:**
  - x0 = "iPhone 15 Pro" (product name)
  - x1 = 999 (price)
  - x2 = 256 (storage GB)
  - x3 = 0x000000 (color: black)

### 2D - Relationships (The "With Whom")
**What it represents:** Connections between substrates
**Real-world analogy:** Family tree, org chart, ownership, dependencies
**64-bit encoding:** Relationship type + target substrate ID

**Examples:**
- **Person → Person (Family):**
  - y0 = "parent_of" (relationship name)
  - y1 = 0x01 (type: family)
  - y2 = target_substrate_id (child's ID)
  - y3 = 946684800 (relationship start date)

- **Person → Car (Ownership):**
  - y0 = "owns"
  - y1 = 0x02 (type: ownership)
  - y2 = car_substrate_id
  - y3 = 1609459200 (purchase date)

- **File → File (Dependency):**
  - y0 = "imports"
  - y1 = 0x03 (type: code dependency)
  - y2 = imported_file_id
  - y3 = version_number

### 3D - State & Change (The "When & How")
**What it represents:** Current state and change vectors
**Real-world analogy:** Position, velocity, acceleration, balance, transactions
**64-bit encoding:** Current value + rate of change

**Examples:**
- **Car (Motion):**
  - z0 = (lat, lon) encoded (current position)
  - z1 = velocity_vector (speed + direction)
  - z2 = acceleration_vector
  - z3 = steering_angle

- **Bank Account:**
  - z0 = 5000 (current balance in cents)
  - z1 = +200 (last transaction delta)
  - z2 = 0.05 (interest rate)
  - z3 = 1609459200 (last update timestamp)

- **Stock Price:**
  - z0 = 15000 (current price in cents)
  - z1 = -50 (price change delta)
  - z2 = 1000000 (volume)
  - z3 = volatility_index

### 4D+ - Behavior & Systems (The "Why & Context")
**What it represents:** Complete object with physics, AI, market dynamics
**Real-world analogy:** Simulation, prediction, emergent behavior
**64-bit encoding:** Encapsulated state of all lower dimensions

**Examples:**
- **Car (Complete System):**
  - m0 = complete_car_substrate (all 0D-3D in one point)
  - m1 = traffic_behavior_model
  - m2 = maintenance_prediction
  - m3 = resale_value_forecast

- **Person (AI Agent):**
  - m0 = complete_person_substrate
  - m1 = personality_model
  - m2 = decision_making_pattern
  - m3 = social_network_influence

- **Market (Economic System):**
  - m0 = complete_market_state
  - m1 = supply_demand_dynamics
  - m2 = trend_prediction
  - m3 = systemic_risk_model

## Dimensional Access Pattern

```python
# Example: Person substrate
person_data = {
    "name": "Alice",
    "birth": 946684800,  # Jan 1, 2000
    "height": 165,
    "weight": 60
}

# Create substrate via SRL
srl = SRL("person://alice")
substrate = core.ingest(srl, person_data)

# Access dimension 4 directly (contains 0D-3D)
complete_person = substrate.dimension(4)

# This single point contains:
# - 0D: identity (unique person ID)
# - 1D: name="Alice", birth=946684800, height=165, weight=60
# - 2D: relationships (family, friends, owns)
# - 3D: current location, velocity, health metrics
# - 4D: complete person with behavior model

# Access attributes via lenses
name = substrate.lens("x0").invoke()      # "Alice"
birth = substrate.lens("x1").invoke()     # 946684800
age = substrate.lens("age").invoke()      # Computed: now() - birth

# Access relationships
parent = substrate.lens("y0").invoke()    # Parent relationship
owns_car = substrate.lens("y2").invoke()  # Car ownership

# Access state
location = substrate.lens("z0").invoke()  # Current GPS
velocity = substrate.lens("z1").invoke()  # Movement vector

# Apply delta (creates NEW substrate)
# Example: Person moves to new location
move_delta = core.delta({"z0": new_location, "z1": velocity})
moved_person = substrate.apply(move_delta)

# Promote to next dimension (time evolution)
# Example: Age person by 1 year
time_delta = core.delta({"time": 31536000})  # 1 year in seconds
future_person = substrate.promote(time_delta)
```

## Summary

- **0D**: Identity (x0) - The "Who" - Unique ID
- **1D**: Name (x0) + Attributes (x1, x2, ...) - The "What" - Properties
- **2D**: Relationship name (y0), type (y1), target (y2), ... - The "With Whom" - Connections
- **3D**: Present (z0) + Deltas (z1, z2, ...) - The "When & How" - State & Change
- **4D+**: Complete object (m0) + Behaviors (m1, m2, ...) - The "Why & Context" - Systems
- **Each level**: 64-bit (2^64 options = ~18 quintillion)
- **Higher dimensions**: Encapsulate ALL lower dimensions
- **Access**: Direct (no iteration) - Just call dimension(n)
- **Change**: Dimensional promotion (no mutation) - Creates new substrate
- **Gateway**: SRL → Core → Kernel - Only path to kernel

