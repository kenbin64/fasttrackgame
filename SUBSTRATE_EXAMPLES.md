# 🧬 Substrate Examples - From Atoms to Organisms

## 📐 1. Foundational Substrates (The Atoms)

### Simple Mathematical Relationships

```python
# Multiplication (Area)
substrate_multiply = {
    "expression_type": "lambda",
    "expression_code": "lambda x, y: x * y",
    "substrate_category": "foundational",
    "metadata": {
        "name": "Multiplication",
        "description": "Fundamental multiplication operation",
        "properties": ["commutative", "associative"],
        "dimension_type": "area (2D)"
    }
}

# Quadratic Relationship
substrate_quadratic = {
    "expression_type": "lambda",
    "expression_code": "lambda x, y: x * y**2",
    "substrate_category": "foundational",
    "metadata": {
        "name": "Quadratic",
        "description": "Quadratic relationship z = x * y²",
        "properties": ["non-linear", "parabolic"]
    }
}

# Addition (Linear Combination)
substrate_add = {
    "expression_type": "lambda",
    "expression_code": "lambda x, y: x + y",
    "substrate_category": "foundational",
    "metadata": {
        "name": "Addition",
        "description": "Linear combination",
        "properties": ["commutative", "associative"],
        "dimension_type": "linear (1D)"
    }
}
```

---

## 🌌 2. Complex Substrates (The Molecules - Natural Laws)

### Einstein's Mass-Energy Equivalence

```python
substrate_einstein = {
    "expression_type": "lambda",
    "expression_code": "lambda m: m * 299792458**2",  # c = speed of light
    "substrate_category": "complex",
    "metadata": {
        "name": "E=mc²",
        "description": "Einstein's mass-energy equivalence",
        "natural_law": "Special Relativity",
        "properties": ["energy", "mass", "conversion"],
        "constants": {"c": 299792458},  # m/s
        "units": {"input": "kg", "output": "joules"}
    }
}
```

### Newton's Law of Gravitation

```python
substrate_gravity = {
    "expression_type": "lambda",
    "expression_code": "lambda m1, m2, r: 6.674e-11 * (m1 * m2) / r**2",
    "substrate_category": "complex",
    "metadata": {
        "name": "Newton's Law of Gravitation",
        "description": "F = G * (m1 * m2) / r²",
        "natural_law": "Classical Mechanics",
        "properties": ["force", "gravity", "attraction"],
        "constants": {"G": 6.674e-11},  # N⋅m²/kg²
        "units": {"input": ["kg", "kg", "m"], "output": "newtons"}
    }
}
```

### Fibonacci Sequence

```python
substrate_fibonacci = {
    "expression_type": "function",
    "expression_code": """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
""",
    "substrate_category": "complex",
    "metadata": {
        "name": "Fibonacci Sequence",
        "description": "F(n) = F(n-1) + F(n-2)",
        "natural_law": "Golden Ratio",
        "properties": ["recursive", "growth", "nature"],
        "sequence": [0, 1, 1, 2, 3, 5, 8, 13, 21]
    }
}
```

---

## 📏 3. Dimensional Substrates (The Organs - Structure)

### 3D Point

```python
substrate_point = {
    "expression_type": "lambda",
    "expression_code": "lambda x, y, z: {'x': x, 'y': y, 'z': z}",
    "substrate_category": "dimensional",
    "dimension_level": 0,
    "metadata": {
        "name": "3D Point",
        "description": "Point in 3D space",
        "dimension_type": "point (0D)",
        "properties": ["position", "coordinates"]
    }
}
```

### Parametric Line

```python
substrate_line = {
    "expression_type": "lambda",
    "expression_code": "lambda t, start, direction: [start[i] + t * direction[i] for i in range(3)]",
    "substrate_category": "dimensional",
    "dimension_level": 1,
    "metadata": {
        "name": "Parametric Line",
        "description": "Line in 3D space: P(t) = start + t * direction",
        "dimension_type": "line (1D)",
        "properties": ["direction", "parametric", "infinite"]
    }
}
```

### Circle (2D)

```python
substrate_circle = {
    "expression_type": "lambda",
    "expression_code": """
lambda r, property='area': {
    'area': 3.14159265359 * r**2,
    'circumference': 2 * 3.14159265359 * r,
    'diameter': 2 * r,
    'radius': r
}[property]
""",
    "substrate_category": "dimensional",
    "dimension_level": 2,
    "metadata": {
        "name": "Circle",
        "description": "2D circle with all geometric properties",
        "dimension_type": "plane (2D)",
        "properties": ["area", "circumference", "diameter", "radius"],
        "formulas": {
            "area": "π * r²",
            "circumference": "2 * π * r"
        }
    }
}
```

### Sphere (3D)

```python
substrate_sphere = {
    "expression_type": "lambda",
    "expression_code": """
lambda r, property='volume': {
    'volume': (4/3) * 3.14159265359 * r**3,
    'surface_area': 4 * 3.14159265359 * r**2,
    'diameter': 2 * r,
    'radius': r
}[property]
""",
    "substrate_category": "dimensional",
    "dimension_level": 3,
    "metadata": {
        "name": "Sphere",
        "description": "3D sphere with all geometric properties",
        "dimension_type": "volume (3D)",
        "properties": ["volume", "surface_area", "diameter", "radius"],
        "formulas": {
            "volume": "(4/3) * π * r³",
            "surface_area": "4 * π * r²"
        }
    }
}
```

---

## 🚗 4. Object Substrates (The Organisms - Complete Entities)

### Car (Complete Vehicle)

```python
substrate_car = {
    "expression_type": "function",
    "expression_code": """
def car(property=None, **params):
    # ALL properties exist in superposition
    properties = {
        'engine': lambda rpm: 200 * (rpm / 6000),  # Torque curve
        'battery': lambda: {'charge': 85, 'capacity': 75, 'voltage': 400},
        'wheels': lambda speed: speed / (2 * 3.14159 * 0.35),  # RPM from speed
        'mass': 1500,  # kg
        'drag_coefficient': 0.3,
        'frontal_area': 2.2,  # m²
        'color': 'red',
        'seats': 5,
        'max_speed': 200,  # km/h
        'acceleration': lambda v, t: v + (9.8 * 0.6 * t),  # 0-100 in ~6s
        'fuel_efficiency': 15,  # km/L
        'tire_pressure': [32, 32, 31, 32],  # psi
        'temperature': lambda: {'engine': 90, 'cabin': 22, 'outside': 25},
        'position': lambda t, v: v * t,  # Simple kinematics
        'physics': lambda state: {
            'velocity': state.get('velocity', 0),
            'acceleration': state.get('acceleration', 0),
            'position': state.get('position', 0)
        }
    }
    
    if property:
        value = properties.get(property)
        return value(**params) if callable(value) else value
    return properties
""",
    "substrate_category": "object",
    "dimension_level": 3,
    "metadata": {
        "name": "Car",
        "description": "Complete vehicle with ALL properties in superposition",
        "object_type": "vehicle",
        "properties": [
            "engine", "battery", "wheels", "mass", "drag_coefficient",
            "color", "seats", "max_speed", "acceleration", "fuel_efficiency",
            "tire_pressure", "temperature", "position", "physics"
        ],
        "tags": ["vehicle", "transport", "physics"],
        "note": "All properties exist whether invoked or not"
    }
}
```

### Ball (Physics Object)

```python
substrate_ball = {
    "expression_type": "function",
    "expression_code": """
def ball(property=None, state=None, **params):
    dt = params.get('dt', 0.01)
    gravity = -9.8  # m/s²
    
    properties = {
        'position': lambda s: [
            s['position'][0] + s['velocity'][0] * dt,
            s['position'][1] + s['velocity'][1] * dt,
            s['position'][2] + s['velocity'][2] * dt
        ] if s else [0, 0, 0],
        'velocity': lambda s: [
            s['velocity'][0],
            s['velocity'][1],
            s['velocity'][2] + gravity * dt
        ] if s else [0, 0, 0],
        'mass': 0.5,  # kg
        'radius': 0.1,  # m
        'material': 'rubber',
        'elasticity': 0.8,  # Coefficient of restitution
        'color': 'red',
        'temperature': 293,  # K (20°C)
        'density': 1200,  # kg/m³
        'volume': (4/3) * 3.14159 * 0.1**3,  # m³
        'surface_area': 4 * 3.14159 * 0.1**2,  # m²
        'moment_of_inertia': (2/5) * 0.5 * 0.1**2,  # kg⋅m²
        'kinetic_energy': lambda s: 0.5 * 0.5 * sum(v**2 for v in s['velocity']) if s else 0,
        'potential_energy': lambda s: 0.5 * 9.8 * s['position'][2] if s else 0
    }
    
    if property:
        value = properties.get(property)
        return value(state) if callable(value) and state else (value() if callable(value) else value)
    return properties
""",
    "substrate_category": "object",
    "dimension_level": 3,
    "metadata": {
        "name": "Ball",
        "description": "Physics ball with ALL properties in superposition",
        "object_type": "physics_object",
        "properties": [
            "position", "velocity", "mass", "radius", "material",
            "elasticity", "color", "temperature", "density", "volume",
            "surface_area", "moment_of_inertia", "kinetic_energy", "potential_energy"
        ],
        "physics": ["gravity", "collision", "rotation"],
        "note": "Complete physics simulation - all properties exist"
    }
}
```

---

## 🔬 Key Insights

### 1. **Everything Exists in Superposition**

When you create a car substrate, it **immediately has**:
- Engine (exists but not manifested)
- Battery (exists but not manifested)
- Wheels (exists but not manifested)
- Color (exists but not manifested)
- ALL properties (exist but not manifested)

### 2. **Invocation Collapses Superposition**

```python
# Create car
car_id = create_substrate(substrate_car)

# Invoke to see battery
battery = invoke_substrate(car_id, property="battery")
# Output: {'charge': 85, 'capacity': 75, 'voltage': 400}

# Invoke to see engine torque at 3000 RPM
torque = invoke_substrate(car_id, property="engine", rpm=3000)
# Output: 100 (Nm)
```

### 3. **You Don't Define Everything Explicitly**

Just like you don't list every atom in a car, you don't list every property in a substrate.

**The expression IS the object.**  
**The object IS the expression.**  
**Everything else is just observation.**

---

## 🦋 The Beauty

**64-bit identity space = 18.4 quintillion unique substrates**

You can represent:
- Every mathematical formula ever discovered
- Every physical object in the universe
- Every dimension from 0D to ∞D
- Every natural law
- Every possible computation

**All with just an expression and a 64-bit hash.** 🌌

