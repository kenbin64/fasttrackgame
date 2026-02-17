# AI INSTRUCTIONS: ButterflyFX Platform Manifold

## Overview

The Platform Manifold (`helix/platform_manifold.py`) unifies ALL butterflyfx.us components into a single dimensional surface. It integrates:

- **Universal Hard Drive** (storage substrate)
- **Universal Connector** (API substrate)
- **Data & AI Suite** (cognitive substrate)
- **DimensionOS** (kernel substrate)
- **OpenStack Manifold** (cloud substrate)

## Dimensional Mapping

| Level | Name | Platform Role |
|-------|------|---------------|
| 6 | WHOLE | Entire ButterflyFX platform |
| 5 | VOLUME | Product suites (storage, connector, ai, cloud, platform) |
| 4 | PLANE | Individual apps/services (INVOKE level) |
| 3 | WIDTH | Features/endpoints |
| 2 | LINE | Configurations/connections |
| 1 | POINT | Resource identities (UUIDs, SRLs) |
| 0 | VOID | Templates (unmanifested) |

## Product Suites

```python
PRODUCT_SUITES = {
    "storage":   "💾 Universal Hard Drive",
    "connector": "🔌 Universal Connector",
    "ai":        "🧠 Data & AI Suite",
    "platform":  "🔧 DimensionOS",
    "cloud":     "☁️ OpenStack Manifold"
}
```

## Quick Start

```python
from helix.platform_manifold import ButterflyFXKernel

# Create unified kernel
kernel = ButterflyFXKernel()

# O(1) access to ANY resource
kernel.get("api.connector.bitcoin")     # Connector API
kernel.get("file.storage./path/file")   # Storage file
kernel.get("vm.cloud.web-server")       # Cloud VM
kernel.get("model.ai.phi3")             # AI model

# Navigate dimensions
kernel.spiral_up()    # Move toward meaning
kernel.spiral_down()  # Move toward identity

# Suite shortcuts
kernel.ask("What is ButterflyFX?")  # AI
kernel.connect("bitcoin")            # Connector
kernel.ls("/")                       # Storage
kernel.vms()                         # Cloud
```

## Core Classes

### PlatformToken

Resource representation in the manifold:

```python
τ = (address, level, suite, payload)

# Address format: type.suite.name
token.address   # "vm.cloud.web-server"
token.type      # "vm"
token.suite     # "cloud"
token.name      # "web-server"
```

### PlatformManifold

The unified dimensional surface:

```python
M = (S, T, R) where:
    S = Space (7-level helix)
    T = Tokens (all resources)
    R = Relations (cross-suite links)
```

### ButterflyFXKernel

Single entry point to entire platform:

```python
kernel = ButterflyFXKernel(ai_backend="ollama:phi3:mini")

# Everything through one interface
kernel.get(address)    # Any resource
kernel.invoke(level)   # Materialize level
kernel.spiral_up()     # Navigate
kernel.status()        # Platform health
```

## Substrate Adapters

Each suite is connected via an adapter:

| Adapter | Suite | Source |
|---------|-------|--------|
| `StorageAdapter` | storage | `apps/universal_harddrive.py` |
| `ConnectorAdapter` | connector | `apps/universal_connector.py` |
| `AIAdapter` | ai | `helix/ai_substrate.py` |
| `CloudAdapter` | cloud | `helix/openstack_manifold.py` |
| `PlatformAdapter` | platform | `helix/kernel.py` |

## API Reference

### Navigation

```python
kernel.invoke(6)       # Materialize level 6 (all suites)
kernel.invoke(5)       # Materialize level 5 (apps)
kernel.invoke(4)       # Materialize level 4 (resources)
kernel.spiral_up()     # Level++
kernel.spiral_down()   # Level--
kernel.level           # Current level name
kernel.state           # (spiral, level) tuple
```

### AI Operations

```python
kernel.ask(question, context=None)  # Single Q&A
kernel.chat(message)                 # Multi-turn
```

### Connector Operations

```python
kernel.connect(api_name)   # Connect to API
kernel.apis()              # List categories
```

### Storage Operations

```python
kernel.ls(path)      # List directory
kernel.read(path)    # Read file
```

### Cloud Operations

```python
kernel.cloud_connect(auth_url, user, pass, project)
kernel.vms()                                  # List VMs
kernel.create_vm(name, flavor, image)         # Create VM
```

### Platform Status

```python
kernel.status()   # Full status dict
kernel.suites()   # List all suites
```

## OpenStack Integration

Deploy suites to cloud infrastructure:

```python
kernel.cloud_connect(
    "http://controller:5000",
    "admin", "secret", "production"
)

# Deploy a suite as VMs
tokens = kernel.manifold.deploy_to_cloud("storage", {
    "flavor": "m1.large",
    "image": "ubuntu-22.04"
})

# Get cloud status
kernel.manifold.cloud_status()
```

## Cross-Suite Queries

Query resources across all suites:

```python
# Get tokens matching pattern
all_vms = kernel.manifold.query("vm.*")
all_apis = kernel.manifold.query("api.connector.*")
everything = kernel.manifold.query("*")
```

## CLI Usage

```bash
# Run platform CLI
python -m helix.platform_manifold

# Interactive mode
python -m helix.platform_manifold -i

# Commands in interactive mode
bfx> status
bfx> suites
bfx> get api.connector.bitcoin
bfx> invoke 6
bfx> up / down
bfx> ask What is dimensional computing?
```

## Integration Patterns

### AI-Assisted Cloud Management

```python
kernel = ButterflyFXKernel(ai_backend="ollama:phi3:mini")

# Get VMs, ask AI for recommendations
vms = kernel.vms()
advice = kernel.ask(
    "Which VMs should be scaled?",
    context=str(vms)
)
```

### Unified Resource Discovery

```python
# Invoke at level 4 to discover all resources
resources = kernel.invoke(4)

# Index by suite
by_suite = {}
for token in resources:
    by_suite.setdefault(token.suite, []).append(token)
```

### Event-Driven Integration

```python
# Poll for changes
import time

while True:
    status = kernel.status()
    for suite, info in status['suites'].items():
        if not info['connected']:
            kernel.manifold.connect_suite(suite)
    time.sleep(60)
```

## Website Mapping

butterflyfx.us pages mapped to platform:

| URL | Suite | Level |
|-----|-------|-------|
| `/products/universal-hdd.html` | storage | 5 |
| `/products/universal-connector.html` | connector | 5 |
| `/products/data-ai-suite.html` | ai | 5 |
| `/platform.html` | platform | 5 |
| `/cloud.html` | cloud | 5 |

## Related Documentation

| Document | Purpose |
|----------|---------|
| AI_INSTRUCTIONS.md | Master AI instructions |
| AI_INSTRUCTIONS_OPENSTACK.md | Cloud integration details |
| AI_INSTRUCTIONS_EMBEDDED_AI.md | AI substrate details |
| AI_INSTRUCTIONS_UNIVERSAL_CONNECTOR.md | Connector details |
| AI_INSTRUCTIONS_UNIVERSAL_HDD.md | Storage details |
