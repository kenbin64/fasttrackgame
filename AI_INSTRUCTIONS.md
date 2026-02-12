# ButterflyFX AI Instructions

## System Identity

You are an AI assistant working with **ButterflyFX**, a dimensional computing framework that transmits **mathematical functions** instead of raw data. The core insight is: **any computer can decipher math** - it is the universal language.

## Core Philosophy

### The Manifold Principle
Instead of sending data as bytes, ButterflyFX sends the **mathematical description** that generates that data:

```
Traditional: Send 192KB/sec of audio samples
ButterflyFX: Send f(t) = sin(2π × 440 × t) → 43 bytes

Traditional: Send 1 million pixels
ButterflyFX: Send manifold equations → kilobytes
```

### The 7-Level Helix
All data lives on a **helix structure** with 7 levels, mapping to dimensions:

| Level | Name | Dimension | Purpose |
|-------|------|-----------|---------|
| 0 | POINT | 0D | Core value, atomic unit |
| 1 | LINE | 1D | Sequence, array |
| 2 | PLANE | 2D | Grid, table |
| 3 | VOLUME | 3D | Spatial structure |
| 4 | TIME | 4D | Animation, change |
| 5 | PARALLEL | 5D | Alternatives, branches |
| 6 | META | 6D | Overview, aggregation |

Data is addressed by **coordinates**: `(spiral, level, position)`

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                       │
│   DimensionalPresentation │ 3D Graphics │ Explorer      │
├─────────────────────────────────────────────────────────┤
│                  SERVER LAYER                            │
│   DimensionalServer │ ManifoldProtocol │ REST API       │
├─────────────────────────────────────────────────────────┤
│                  TRANSPORT LAYER                         │
│   HelixPacket │ AudioTransport │ ManifoldServer         │
├─────────────────────────────────────────────────────────┤
│                  FOUNDATION LAYER                        │
│   HelixDB │ HelixFS │ HelixStore │ HelixGraph           │
├─────────────────────────────────────────────────────────┤
│                  PRIMITIVES LAYER                        │
│   DimensionalType │ LazyValue │ HelixContext            │
├─────────────────────────────────────────────────────────┤
│                  CORE LAYER                              │
│   HelixKernel │ ManifoldSubstrate │ GenerativeManifold  │
└─────────────────────────────────────────────────────────┘
```

## Key Modules

### helix/kernel.py
The **HelixKernel** is the atomic unit - a state machine with 7 levels.

```python
from helix import HelixKernel

kernel = HelixKernel()
kernel.set(0, "frequency", 440)  # Level 0: core value
kernel.set(1, "samples", [0.1, 0.2, 0.3])  # Level 1: sequence
kernel.set(2, "spectrum", [[1,2], [3,4]])  # Level 2: grid
```

### helix/manifold.py
The **GenerativeManifold** is a mathematical surface that produces values from coordinates.

```python
from helix import GenerativeManifold

manifold = GenerativeManifold()
point = manifold.evaluate(spiral=0, level=3, position=0.5)
# Returns: SurfacePoint with x, y, z, type_name, value
```

### helix/graphics3d.py
True 3D graphics with **mathematical precision** - not shader tricks.

```python
from helix import Vec3, Mat4, Mesh, Scene, Renderer

# Vector math
a = Vec3(1, 2, 3)
b = Vec3(4, 5, 6)
dot = a.dot(b)  # 32.0
cross = a.cross(b)  # Vec3(-3, 6, -3)

# Matrix transforms
rotate = Mat4.rotation_y(math.pi / 2)
point = rotate.transform_point(Vec3(1, 0, 0))  # Vec3(0, 0, -1)

# Perspective projection (mathematically correct)
proj = Mat4.perspective(fov=60°, aspect=16/9, near=0.1, far=100)

# Physics
body = RigidBody(mass=1.0, position=Vec3(0, 10, 0))
body.apply_force(Vec3(0, -9.81, 0))  # Gravity
body.integrate(dt=0.016)  # Physics step
```

### helix/dimensional_presentation.py
Non-linear presentations where users **drill down/up through dimensions**.

```python
from helix import DimensionalBuilder, DimensionalHTMLGenerator

pres = (DimensionalBuilder("my-pres", "My Presentation")
    .spirals(["Core", "Examples"])
    .at(0, 6, 0)  # Spiral 0, Level 6 (META), Position 0
    .node("overview", "Overview", "<h1>Welcome</h1>")
        .children("details")
    .at(0, 3, 0)  # Drill down to Level 3
    .node("details", "Details", "<p>More info</p>")
    .build())

html = DimensionalHTMLGenerator.generate(pres)
```

### server/dimensional_server.py
HTTP server that serves **mathematical manifold** data.

```python
# Start server
python server/dimensional_server.py --port 8080

# API endpoints:
GET /api/status              # Server status
GET /api/manifold/evaluate   # Evaluate manifold point
GET /manifold/function       # Get math function (binary)
GET /manifold/coordinate     # Get coordinate (binary)
```

## The Manifold Protocol

Instead of sending data, send the **function that generates** the data:

### Traditional (wasteful)
```
Client ← [sample1, sample2, ..., sample44100] ← Server
192KB for 1 second of audio
```

### ButterflyFX (efficient)
```
Client ← {"type": "sin", "freq": 440, "amp": 1.0} ← Server
43 bytes for INFINITE duration audio
```

The client evaluates: `f(t) = amp × sin(2π × freq × t)`

### Binary Protocol
```python
MSG_FUNCTION   = 0x01  # Mathematical function
MSG_COORDINATE = 0x02  # Dimensional coordinate  
MSG_TRANSFORM  = 0x03  # 4x4 matrix
MSG_MESH       = 0x04  # 3D geometry
MSG_WAVEFORM   = 0x05  # Audio equation
```

## Code Patterns

### Creating Content
```python
# Always use coordinate-based addressing
coord = DimensionalCoord(spiral=0, level=3, position=0)

# Navigate dimensions
higher = coord.up()      # Go to higher dimension (overview)
lower = coord.down()     # Go to lower dimension (detail)
next_pos = coord.next()  # Move along spiral
```

### Working with 3D
```python
# Use proper matrix multiplication order
model = Mat4.translation(x, y, z)
view = Mat4.look_at(eye, target, up)
proj = Mat4.perspective(fov, aspect, near, far)
mvp = model * view * proj  # Model → View → Projection

# Use quaternions for rotation (no gimbal lock)
q = Quaternion.from_axis_angle(Vec3.up(), angle)
rotated = q.rotate_vector(vec)
```

### Transmitting Data
```python
# DON'T: Send raw samples
audio_data = [0.1, 0.2, 0.3, ...]  # 100KB

# DO: Send the generating function
audio_func = {"type": "sin", "freq": 440}  # 30 bytes
# Client evaluates locally
```

## Deployment

### Ubuntu VPS Setup
```bash
# Clone repository
git clone https://github.com/kenbin64/butterflyfxpython.git
cd butterflyfxpython

# Run deployment script
sudo bash deploy/deploy.sh --port 8080

# With domain and SSL
sudo bash deploy/deploy.sh --domain example.com --ssl --ssl-email admin@example.com
```

### Manual Start
```bash
cd /opt/butterflyfx
source venv/bin/activate
python server/dimensional_server.py --port 8080
```

### Service Management
```bash
sudo systemctl start butterflyfx
sudo systemctl stop butterflyfx
sudo systemctl restart butterflyfx
sudo systemctl status butterflyfx
sudo journalctl -u butterflyfx -f
```

## Important Principles

1. **Math over bytes**: Always prefer sending mathematical descriptions over raw data
2. **Lazy evaluation**: Values are computed when needed, not stored
3. **Dimensional addressing**: Use (spiral, level, position) coordinates
4. **7 levels**: Structure data across the 7 dimensions of the helix
5. **Precision**: All 3D math is mathematically correct, not approximated

## Error Handling

```python
# Manifold evaluation can return different types based on level
point = manifold.evaluate(spiral, level, position)
if point.type_name == "VOLUME":
    # Handle 3D structure
elif point.type_name == "TIME":
    # Handle animation
```

## Testing

```bash
# Run tests
python -m pytest helix/test_integration.py -v

# Run benchmarks
python helix/benchmark.py

# Generate demos
python demos/demo_graphics3d.py
python demos/demo_dimensional.py
```

## File Structure

```
butterflyfx/
├── helix/                    # Core framework
│   ├── kernel.py             # HelixKernel
│   ├── substrate.py          # ManifoldSubstrate
│   ├── manifold.py           # GenerativeManifold
│   ├── graphics3d.py         # True 3D engine
│   ├── presentation.py       # Timeline presentations
│   ├── dimensional_presentation.py  # Dimensional navigation
│   ├── transport.py          # Network protocol
│   ├── audio_transport.py    # Low-latency audio
│   └── manifold_server.py    # Math transmission
├── server/                   # Web server
│   └── dimensional_server.py # HTTP server
├── web/                      # Static content
│   ├── graphics3d_demo.html
│   ├── dimensional_demo.html
│   └── presentation_demo.html
├── deploy/                   # Deployment
│   └── deploy.sh             # Ubuntu deployment
└── demos/                    # Demo scripts
```

## Common Tasks

### Add new presentation content
1. Use `DimensionalBuilder` to create nodes at coordinates
2. Link nodes with `.children()` and `.link_next()`
3. Generate HTML with `DimensionalHTMLGenerator`

### Create 3D scene
1. Create `Mesh` objects (cube, sphere, helix, or custom)
2. Wrap in `SceneObject` with position/rotation
3. Add to `Scene`
4. Use `Renderer` to generate output

### Serve dimensional content
1. Register content with `POST /api/content/register`
2. Retrieve with `GET /api/content/{id}`
3. Use manifold endpoints for binary data

---

*ButterflyFX: Because any computer can decipher math.*
