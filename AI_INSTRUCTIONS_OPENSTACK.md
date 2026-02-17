# ButterflyFX OpenStack Integration - AI Instructions

## Purpose

This document specifies how ButterflyFX integrates with OpenStack to provide **dimensional cloud control** — treating cloud infrastructure as a manifold substrate rather than traditional API iteration.

---

## Core Concept: Cloud as Dimensional Substrate

OpenStack resources become **tokens** in the ButterflyFX manifold:

```
Traditional OpenStack:
  nova list → iterate all VMs → filter by name → O(N)
  nova show vm-id → fetch details → another API call

ButterflyFX Dimensional:
  kernel.get("vm.production.webserver") → O(1) direct access
  kernel.invoke(4) → all Level 4 (running) resources
```

---

## The 7 Dimensional Levels for Cloud Resources

| Level | Geometric | Semantic | Cloud Meaning | OpenStack Examples |
|-------|-----------|----------|---------------|-------------------|
| 0 | Potential | Defined | Resource template, not created | Heat templates, Terraform |
| 1 | Point | Identity | UUID, name — exists in registry | server.id, network.id |
| 2 | Line | Relationship | Attachments, dependencies | networks, security_groups, volumes |
| 3 | Width | Structure | Spec/blueprint | flavor, image, metadata |
| 4 | Plane | Manifestation | **RUNNING** — first visible form | status=ACTIVE, IP assigned |
| 5 | Volume | Multiplicity | Scaling, clusters | Heat stacks, Magnum clusters |
| 6 | Whole | Meaning | Project context, purpose | project, tags, application |

---

## Key Components

### CloudToken

A cloud resource as a dimensional token: `τ = (x, σ, π)`

```python
@dataclass
class CloudToken:
    id: str                    # UUID
    name: str                  # Human name
    resource_type: str         # vm, network, volume, image
    project: str               # Spiral context
    signature: Set[int]        # Which levels {0,1,2,3,4,5,6}
    current_level: int         # Current manifestation level
    status: str                # POTENTIAL, BUILD, ACTIVE, etc.
    spec: Dict                 # Level 3 structure
    relations: Dict            # Level 2 relationships
```

**Dimensional Address:** `resource_type.project.name`
- `vm.production.webserver`
- `network.default.internal`
- `volume.staging.database`

### OpenStackSubstrate

The manifold `S = (M, T, R)` containing all cloud resources:

```python
class OpenStackSubstrate:
    def tokens_for_state(s, level) -> Set[CloudToken]:
        """μ(s,ℓ) — materialization function"""
        
    def register_token(token) -> str:
        """Add resource to manifold"""
        
    def sync_from_openstack() -> int:
        """Pull resources from OpenStack into manifold"""
```

### OpenStackKernel

The helix kernel for cloud operations:

```python
class OpenStackKernel:
    def invoke(level: int) -> Set[CloudToken]:
        """I_k: Jump to level, materialize resources"""
        
    def spiral_up(project: str):
        """U: Switch to different project context"""
        
    def spiral_down():
        """D: Return to previous project"""
        
    def collapse():
        """C: Release all to potential"""
        
    def get(address: str) -> CloudToken:
        """O(1) dimensional access"""
```

---

## Operations Mapping

### Traditional vs Dimensional

| Task | Traditional (OpenStack CLI) | Dimensional (ButterflyFX) |
|------|----------------------------|---------------------------|
| List running VMs | `openstack server list` + iterate | `kernel.invoke(4)` |
| Find VM by name | `for vm in list: if name == x` | `kernel.get("vm.proj.name")` |
| Create VM | `openstack server create` + wait | `kernel.create_vm()` (0→1→3→4) |
| Delete VM | `openstack server delete` | `kernel.delete_vm()` (4→0 collapse) |
| Switch project | `export OS_PROJECT=x` | `kernel.spiral_up("x")` |

### VM Creation as Dimensional Invocation

```
Level 0: POTENTIAL
    ↓ Token created with spec
Level 1: IDENTITY  
    ↓ UUID assigned
Level 3: STRUCTURE
    ↓ Flavor, image, network applied
Level 4: MANIFESTATION
    ↓ Instance boots, becomes ACTIVE
```

This is **4 discrete transitions**, not iteration.

### VM Deletion as Collapse

```
Level 4: MANIFESTATION (ACTIVE)
    ↓ collapse()
Level 0: POTENTIAL (resource released)
```

---

## Universal Connector Integration

OpenStack becomes a connector in the Universal Connector system:

```python
class OpenStackConnector:
    id = "openstack"
    name = "OpenStack Cloud"
    icon = "☁️"
    
    def list_srls() -> List[str]:
        """Generate SRLs for all cloud resources"""
        # srl://openstack/vm/production/webserver
        # srl://openstack/network/default/internal
        
    def materialize(srl: str) -> Dict:
        """Get resource data from SRL"""
```

### SRL Format

```
srl://openstack/{resource_type}/{project}/{name}

Examples:
  srl://openstack/vm/production/webserver
  srl://openstack/network/staging/backend-net
  srl://openstack/volume/default/database-vol
  srl://openstack/image/shared/ubuntu-22.04
```

---

## CLI Usage

```bash
# Connect to OpenStack
python -m helix.openstack_manifold connect --openrc ~/demo-openrc

# List VMs at Level 4 (running)
python -m helix.openstack_manifold list vm --level 4

# List all resources at Level 3 (defined structure)
python -m helix.openstack_manifold list all --level 3

# Get specific VM by dimensional address
python -m helix.openstack_manifold get vm.production.webserver

# Create VM (invokes 0→1→3→4)
python -m helix.openstack_manifold create-vm myvm --image ubuntu --flavor m1.small

# Delete VM (collapse 4→0)
python -m helix.openstack_manifold delete vm.production.myvm

# Show current helix state
python -m helix.openstack_manifold state
```

---

## API Usage

```python
from helix.openstack_manifold import OpenStackSubstrate, OpenStackKernel

# Initialize
substrate = OpenStackSubstrate(openrc_path="~/demo-openrc")
kernel = OpenStackKernel(substrate)

# Sync from OpenStack
substrate.sync_from_openstack()

# O(1) access by dimensional address
vm = kernel.get("vm.production.webserver")
print(f"ID: {vm.id}, Status: {vm.status}")

# Invoke level (materialize resources at that level)
running_vms = kernel.invoke(4)  # All Level 4 (ACTIVE) resources

# Filter by type
vms_only = [t for t in running_vms if t.resource_type == 'vm']

# Create VM through dimensional invocation
new_vm = kernel.create_vm(
    name="api-server",
    image="ubuntu-22.04",
    flavor="m1.medium",
    network="private",
    project="production"
)

# Switch project (spiral)
kernel.spiral_up("staging")

# Collapse all
kernel.collapse()
```

---

## Why This Matters

### Performance

| Operation | Traditional | Dimensional |
|-----------|-------------|-------------|
| Find 1 VM in 10,000 | O(10,000) API iteration | O(1) address lookup |
| List running VMs | O(N) filter on client | O(1) level invocation |
| Multi-project access | Re-auth per project | Spiral transitions |

### Conceptual Clarity

- **Resources are tokens**, not API responses
- **Projects are spirals**, not environment variables
- **States are levels**, not status strings
- **Operations are transitions**, not CRUD

### Integration

- OpenStack resources appear in Universal HDD as dimensional files
- SRLs provide unified addressing across clouds
- Same model works for AWS, GCP, Azure (different substrates, same kernel)

---

## Key Rules for AI

1. **Never iterate over resources** — use level invocation
2. **Address directly** — `kernel.get("vm.project.name")` not loops
3. **Track state** — always know current `(spiral, level)`
4. **Use proper levels**:
   - Level 4 for running/active resources
   - Level 3 for definitions/specs
   - Level 1 for identities only
5. **Spiral for projects** — spiral_up/down, not environment switching
6. **Collapse, don't delete** — resources return to potential

---

## Future Extensions

### Multi-Cloud Substrate

```python
# Same kernel, different substrates
aws_substrate = AWSSubstrate()
gcp_substrate = GCPSubstrate()
azure_substrate = AzureSubstrate()

# Unified access
vm = cloud_kernel.get("vm.aws.production.webserver")
vm = cloud_kernel.get("vm.gcp.staging.api")
```

### Heat/Terraform as Level 0

Templates are Level 0 (Potential) that can be invoked to manifest:

```python
# Template exists at Level 0
template = kernel.get("stack.production.webapp")

# Invoke to manifest (0 → 4)
kernel.invoke_stack(template)  # Creates all resources
```

### Kubernetes Integration

Pods, services, deployments follow same model:

```python
# Kubernetes resources as tokens
pod = kernel.get("pod.default.nginx-abc123")
svc = kernel.get("service.production.api")
```

---

*"Why iterate through every cloud resource when you can invoke the level you need?"*
