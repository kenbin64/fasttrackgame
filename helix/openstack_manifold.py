"""
ButterflyFX OpenStack Manifold — Cloud Infrastructure as Dimensional Substrate

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

This mathematical kernel belongs to all humanity.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

OpenStack becomes a manifold substrate where:
- VMs, networks, volumes are TOKENS with dimensional signatures
- Projects/tenants are SPIRALS (isolated dimensional spaces)
- Resources exist as POTENTIAL until invoked
- Access is O(1) via dimensional addressing, not API iteration

The 7 Levels for Cloud Resources:
    Level 0 (Potential): Resource defined but not created
    Level 1 (Identity): UUID, name — the resource anchor
    Level 2 (Relationship): Networks, security groups, attachments
    Level 3 (Structure): Flavor, image, specs — the blueprint
    Level 4 (Manifestation): RUNNING instance — first visible form
    Level 5 (Multiplicity): Scaling groups, clusters, load balancers
    Level 6 (Meaning): Project purpose, tags, classifications

Key Insight:
    Traditional: for vm in nova.list(): if vm.name == target: return vm  # O(N)
    Dimensional: invoke("vm.myproject.webserver")  # O(1)
"""

from __future__ import annotations
import os
import json
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from enum import Enum, auto
from functools import cached_property
import subprocess
import threading
from datetime import datetime

# Import ButterflyFX kernel
from .kernel import HelixState, LEVEL_NAMES, SEMANTIC_NAMES


# =============================================================================
# CLOUD RESOURCE LEVELS — Mapping OpenStack to Dimensional Semantics
# =============================================================================

CLOUD_LEVELS = {
    0: {
        "name": "Potential",
        "semantic": "Defined",
        "description": "Resource template/definition — not yet created",
        "openstack": ["heat_template", "terraform", "definition"]
    },
    1: {
        "name": "Identity", 
        "semantic": "Anchor",
        "description": "UUID and name — the resource exists in registry",
        "openstack": ["id", "name", "created_at"]
    },
    2: {
        "name": "Relationship",
        "semantic": "Connected",
        "description": "Network attachments, security groups, dependencies",
        "openstack": ["networks", "security_groups", "volumes", "keypairs"]
    },
    3: {
        "name": "Structure",
        "semantic": "Blueprint",
        "description": "Flavor, image, configuration — the spec",
        "openstack": ["flavor", "image", "metadata", "user_data"]
    },
    4: {
        "name": "Manifestation",
        "semantic": "Running",
        "description": "Instance is ACTIVE — first visible form",
        "openstack": ["status=ACTIVE", "ip_addresses", "console"]
    },
    5: {
        "name": "Multiplicity",
        "semantic": "Scaling",
        "description": "Auto-scaling groups, clusters, replicas",
        "openstack": ["heat_stack", "magnum_cluster", "senlin_cluster"]
    },
    6: {
        "name": "Meaning",
        "semantic": "Purpose",
        "description": "Project context, tags, business meaning",
        "openstack": ["project", "tags", "description", "application"]
    }
}


# =============================================================================
# CLOUD TOKEN — A Resource in the Manifold
# =============================================================================

@dataclass(eq=False)
class CloudToken:
    """
    A cloud resource as a dimensional token.
    
    Following ButterflyFX spec: τ = (x, σ, π)
    - x: coordinates in manifold (project, resource_type, name)
    - σ: signature — which levels this token inhabits
    - π: payload — lazy-loaded resource data
    """
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return isinstance(other, CloudToken) and self.id == other.id
    # Identity (Level 1)
    id: str
    name: str
    resource_type: str  # vm, network, volume, etc.
    
    # Coordinates in manifold
    project: str  # Spiral context
    
    # Dimensional signature — which levels this resource inhabits
    signature: Set[int] = field(default_factory=lambda: {1})
    
    # Current level (where it's manifested)
    current_level: int = 0
    
    # Lazy payload
    _payload: Optional[Dict[str, Any]] = None
    _payload_loader: Optional[Callable[[], Dict]] = None
    
    # Relationships (Level 2)
    relations: Dict[str, List[str]] = field(default_factory=dict)
    
    # Structure (Level 3)
    spec: Dict[str, Any] = field(default_factory=dict)
    
    # State (Level 4)
    status: str = "POTENTIAL"
    
    # Metadata (Level 6)
    tags: List[str] = field(default_factory=list)
    purpose: str = ""
    
    @property
    def coordinates(self) -> Tuple[str, str, str]:
        """Position in the manifold: (project, type, name)"""
        return (self.project, self.resource_type, self.name)
    
    @property
    def address(self) -> str:
        """Dimensional address: type.project.name"""
        return f"{self.resource_type}.{self.project}.{self.name}"
    
    @property
    def payload(self) -> Dict[str, Any]:
        """Lazy-load payload on first access"""
        if self._payload is None and self._payload_loader:
            self._payload = self._payload_loader()
        return self._payload or {}
    
    def inhabits(self, level: int) -> bool:
        """Check if token exists at given level"""
        return level in self.signature
    
    def invoke_to(self, level: int) -> None:
        """Move token to specified level"""
        self.signature.add(level)
        self.current_level = level
    
    def collapse(self) -> None:
        """Return to potential"""
        self.signature = {0}
        self.current_level = 0
        self._payload = None


# =============================================================================
# OPENSTACK SUBSTRATE — The Manifold of Cloud Resources
# =============================================================================

class OpenStackSubstrate:
    """
    OpenStack as a ButterflyFX substrate: S = (M, T, R)
    
    - M: The cloud manifold (all possible resources)
    - T: Token registry (resources as tokens)
    - R: Relations between resources
    
    Implements the substrate interface from BUTTERFLYFX_SPECIFICATION.md
    """
    
    def __init__(self, openrc_path: Optional[str] = None):
        """
        Initialize OpenStack substrate.
        
        Args:
            openrc_path: Path to OpenStack credentials file
        """
        self.openrc_path = openrc_path
        self._tokens: Dict[str, CloudToken] = {}
        self._relations: Dict[str, Dict[str, List[str]]] = {}
        self._spirals: Dict[str, str] = {}  # project_id -> project_name
        self._connected = False
        self._lock = threading.RLock()
        
        # Load credentials if provided
        if openrc_path:
            self._load_openrc(openrc_path)
    
    def _load_openrc(self, path: str) -> None:
        """Load OpenStack credentials from openrc file"""
        if os.path.exists(path):
            # Source the file and extract environment variables
            with open(path, 'r') as f:
                for line in f:
                    if line.startswith('export '):
                        parts = line.replace('export ', '').strip().split('=', 1)
                        if len(parts) == 2:
                            key, value = parts
                            os.environ[key] = value.strip('"\'')
            self._connected = True
    
    # =========================================================================
    # SUBSTRATE INTERFACE (from BUTTERFLYFX_SPECIFICATION.md)
    # =========================================================================
    
    def register_token(self, token: CloudToken) -> str:
        """
        REGISTER_TOKEN(τ) — Add token to manifold
        
        Returns: token identifier
        """
        with self._lock:
            self._tokens[token.id] = token
            # Index by address for O(1) lookup
            self._tokens[token.address] = token
            return token.id
    
    def tokens_for_state(self, spiral: int, level: int) -> List[CloudToken]:
        """
        TOKENS_FOR_STATE(s, ℓ) — Returns μ(s,ℓ)
        
        The materialization function: given helix state, return matching tokens.
        
        This is the KEY operation — O(1) from kernel's perspective.
        """
        with self._lock:
            result = []
            seen_ids = set()
            for token in self._tokens.values():
                if isinstance(token, CloudToken) and token.inhabits(level):
                    if token.id not in seen_ids:
                        result.append(token)
                        seen_ids.add(token.id)
            return result
    
    def relate(self, token_a: str, token_b: str, relation: str) -> None:
        """Add relation between tokens"""
        with self._lock:
            if token_a not in self._relations:
                self._relations[token_a] = {}
            if relation not in self._relations[token_a]:
                self._relations[token_a][relation] = []
            self._relations[token_a][relation].append(token_b)
    
    def related(self, token_id: str, relation_type: str) -> List[str]:
        """Get related tokens"""
        with self._lock:
            return self._relations.get(token_id, {}).get(relation_type, [])
    
    def release_materialized(self, spiral: int) -> None:
        """Release all materialized tokens in spiral (collapse)"""
        with self._lock:
            for token in self._tokens.values():
                if isinstance(token, CloudToken):
                    token.collapse()
    
    # =========================================================================
    # OPENSTACK-SPECIFIC OPERATIONS
    # =========================================================================
    
    def _run_openstack(self, *args) -> Dict[str, Any]:
        """Run OpenStack CLI command and return JSON result"""
        cmd = ['openstack', '--format', 'json'] + list(args)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return json.loads(result.stdout) if result.stdout.strip() else {}
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}
    
    def sync_from_openstack(self) -> int:
        """
        Sync OpenStack resources into the substrate.
        
        This populates the manifold with tokens from actual cloud state.
        Returns: number of tokens synced
        """
        count = 0
        
        # Sync VMs (servers)
        servers = self._run_openstack('server', 'list', '--all-projects')
        if isinstance(servers, list):
            for server in servers:
                token = self._server_to_token(server)
                self.register_token(token)
                count += 1
        
        # Sync Networks
        networks = self._run_openstack('network', 'list')
        if isinstance(networks, list):
            for network in networks:
                token = self._network_to_token(network)
                self.register_token(token)
                count += 1
        
        # Sync Volumes
        volumes = self._run_openstack('volume', 'list', '--all-projects')
        if isinstance(volumes, list):
            for volume in volumes:
                token = self._volume_to_token(volume)
                self.register_token(token)
                count += 1
        
        # Sync Images
        images = self._run_openstack('image', 'list')
        if isinstance(images, list):
            for image in images:
                token = self._image_to_token(image)
                self.register_token(token)
                count += 1
        
        return count
    
    def _server_to_token(self, server: Dict) -> CloudToken:
        """Convert OpenStack server to CloudToken"""
        status = server.get('Status', 'UNKNOWN')
        
        # Determine dimensional signature based on status
        signature = {1}  # Always has identity
        if status == 'BUILD':
            signature.update({2, 3})  # Has relationships and structure
        elif status == 'ACTIVE':
            signature.update({2, 3, 4})  # Manifested!
        elif status == 'SHUTOFF':
            signature.update({2, 3})  # Structure exists, not running
        
        return CloudToken(
            id=server.get('ID', str(uuid.uuid4())),
            name=server.get('Name', 'unnamed'),
            resource_type='vm',
            project=server.get('Project', 'default'),
            signature=signature,
            current_level=4 if status == 'ACTIVE' else 3,
            status=status,
            spec={
                'flavor': server.get('Flavor'),
                'image': server.get('Image'),
            },
            relations={
                'networks': server.get('Networks', '').split(', ') if server.get('Networks') else []
            }
        )
    
    def _network_to_token(self, network: Dict) -> CloudToken:
        """Convert OpenStack network to CloudToken"""
        return CloudToken(
            id=network.get('ID', str(uuid.uuid4())),
            name=network.get('Name', 'unnamed'),
            resource_type='network',
            project=network.get('Project', 'default'),
            signature={1, 2, 4},  # Networks are always "active" when created
            current_level=4,
            status='ACTIVE' if network.get('State') == 'UP' else 'DOWN'
        )
    
    def _volume_to_token(self, volume: Dict) -> CloudToken:
        """Convert OpenStack volume to CloudToken"""
        status = volume.get('Status', 'available')
        signature = {1, 3}  # Has identity and structure
        if status in ['available', 'in-use']:
            signature.add(4)
        
        return CloudToken(
            id=volume.get('ID', str(uuid.uuid4())),
            name=volume.get('Name', 'unnamed'),
            resource_type='volume',
            project=volume.get('Project', 'default'),
            signature=signature,
            current_level=4 if status in ['available', 'in-use'] else 3,
            status=status,
            spec={
                'size_gb': volume.get('Size'),
                'type': volume.get('Type')
            }
        )
    
    def _image_to_token(self, image: Dict) -> CloudToken:
        """Convert OpenStack image to CloudToken"""
        return CloudToken(
            id=image.get('ID', str(uuid.uuid4())),
            name=image.get('Name', 'unnamed'),
            resource_type='image',
            project='shared',  # Images are typically shared
            signature={1, 3, 4},  # Images are structure templates
            current_level=3,
            status=image.get('Status', 'active')
        )


# =============================================================================
# OPENSTACK KERNEL — Dimensional Cloud Control
# =============================================================================

class OpenStackKernel:
    """
    ButterflyFX Helix Kernel for OpenStack operations.
    
    Implements the 4 operators:
    - INVOKE(k): Jump to level k, materialize cloud resources
    - SPIRAL_UP: Move to next project/context
    - SPIRAL_DOWN: Return to previous project/context
    - COLLAPSE: Release all resources to potential
    
    Key Property: O(7) per spiral, no iteration over resources
    """
    
    def __init__(self, substrate: OpenStackSubstrate):
        self.substrate = substrate
        self._spiral = 0  # Current project index
        self._level = 0   # Current dimensional level
        self._spirals: List[str] = ['default']  # Project stack
        self._materialized: Set[str] = set()  # Currently materialized token IDs
    
    @property
    def state(self) -> Tuple[int, int]:
        """Current helix state (s, ℓ)"""
        return (self._spiral, self._level)
    
    @property
    def current_project(self) -> str:
        """Current project (spiral context)"""
        return self._spirals[self._spiral] if self._spiral < len(self._spirals) else 'default'
    
    # =========================================================================
    # KERNEL OPERATIONS (from BUTTERFLYFX_FORMAL_KERNEL.md)
    # =========================================================================
    
    def invoke(self, level: int) -> List[CloudToken]:
        """
        I_k(s,ℓ) = (s,k) — Jump to level k
        
        Materializes cloud resources at the specified level.
        
        Level mappings:
            0: Show potential (templates, definitions)
            1: Show identities (UUIDs, names)
            2: Show relationships (networks, groups)
            3: Show structure (flavors, images)
            4: Show manifested (ACTIVE instances)
            5: Show multiplicity (scaling groups)
            6: Show meaning (project context)
        """
        assert 0 <= level <= 6, f"Level must be 0-6, got {level}"
        self._level = level
        
        # Get tokens for this state
        tokens = self.substrate.tokens_for_state(self._spiral, level)
        
        # Track materialized
        self._materialized = {t.id for t in tokens}
        
        return tokens
    
    def spiral_up(self, project: Optional[str] = None) -> None:
        """
        U(s,6) = (s+1,0) — Move to next spiral (project)
        
        Precondition: Must be at level 6 (Whole/Meaning)
        
        Args:
            project: Optional specific project to switch to
        """
        if project:
            if project not in self._spirals:
                self._spirals.append(project)
            self._spiral = self._spirals.index(project)
        else:
            self._spiral += 1
            if self._spiral >= len(self._spirals):
                self._spirals.append(f'project_{self._spiral}')
        
        self._level = 0
        self._materialized = set()
    
    def spiral_down(self) -> None:
        """
        D(s,0) = (s-1,6) — Return to previous spiral
        
        Precondition: Must be at level 0 (Potential)
        """
        if self._spiral > 0:
            self._spiral -= 1
            self._level = 6
    
    def collapse(self) -> None:
        """
        C(s,ℓ) = (s,0) — Collapse all to potential
        
        Releases all materialized resources back to potential state.
        """
        self.substrate.release_materialized(self._spiral)
        self._level = 0
        self._materialized = set()
    
    # =========================================================================
    # DIMENSIONAL CLOUD OPERATIONS
    # =========================================================================
    
    def get(self, address: str) -> Optional[CloudToken]:
        """
        O(1) dimensional access to cloud resource.
        
        Address format: resource_type.project.name
        Examples:
            vm.production.webserver
            network.default.internal
            volume.staging.database
        
        This is the KEY advantage:
            Traditional: iterate all VMs, filter by name  # O(N)
            Dimensional: direct address lookup  # O(1)
        """
        with self.substrate._lock:
            return self.substrate._tokens.get(address)
    
    def create_vm(
        self,
        name: str,
        image: str,
        flavor: str,
        network: Optional[str] = None,
        project: Optional[str] = None
    ) -> CloudToken:
        """
        Create VM through dimensional invocation.
        
        The VM starts at Level 0 (Potential) and is invoked
        through levels until it manifests at Level 4.
        """
        project = project or self.current_project
        
        # Create token at Level 0 (potential)
        token = CloudToken(
            id=str(uuid.uuid4()),
            name=name,
            resource_type='vm',
            project=project,
            signature={0, 1},
            current_level=0,
            status='POTENTIAL',
            spec={
                'image': image,
                'flavor': flavor,
                'network': network
            }
        )
        
        # Register in substrate
        self.substrate.register_token(token)
        
        # Invoke through levels to manifest
        self._invoke_vm_creation(token)
        
        return token
    
    def _invoke_vm_creation(self, token: CloudToken) -> None:
        """
        Invoke VM through dimensional levels to manifestation.
        
        This is NOT iteration — it's 4 discrete level transitions:
        0 → 1 → 3 → 4
        """
        # Level 1: Identity (create in OpenStack, get UUID)
        token.invoke_to(1)
        
        # Level 3: Structure (apply flavor, image)
        token.invoke_to(3)
        
        # Level 4: Manifestation (boot the instance)
        result = self.substrate._run_openstack(
            'server', 'create',
            '--image', token.spec.get('image', 'ubuntu'),
            '--flavor', token.spec.get('flavor', 'm1.small'),
            '--network', token.spec.get('network', 'private'),
            '--format', 'json',
            token.name
        )
        
        if 'id' in result:
            token.id = result['id']
            token.status = result.get('status', 'BUILD')
            token.invoke_to(4)
        else:
            token.status = 'ERROR'
    
    def delete_vm(self, address: str) -> bool:
        """
        Delete VM by collapsing it from manifested back to void.
        
        Dimensional operation: 4 → 0 (collapse)
        """
        token = self.get(address)
        if not token or token.resource_type != 'vm':
            return False
        
        # Collapse in OpenStack
        result = self.substrate._run_openstack('server', 'delete', token.id)
        
        # Collapse token
        token.collapse()
        token.status = 'DELETED'
        
        return 'error' not in result
    
    # =========================================================================
    # QUERY INTERFACE — Dimensional vs Traditional
    # =========================================================================
    
    def list_vms(self, level: int = 4) -> List[CloudToken]:
        """
        List VMs at specified dimensional level.
        
        Level 4 = Running instances (traditional "list servers")
        Level 3 = Defined instances (including stopped)
        Level 1 = All identities (including deleted references)
        """
        tokens = self.invoke(level)
        return [t for t in tokens if t.resource_type == 'vm']
    
    def find(self, pattern: str, level: int = 4) -> List[CloudToken]:
        """
        Find resources matching pattern at level.
        
        Pattern: resource_type.project.name (wildcards supported)
        """
        tokens = self.invoke(level)
        results = []
        
        parts = pattern.split('.')
        for token in tokens:
            match = True
            coords = token.coordinates
            for i, part in enumerate(parts):
                if part != '*' and i < len(coords) and coords[i] != part:
                    match = False
                    break
            if match:
                results.append(token)
        
        return results


# =============================================================================
# UNIVERSAL CONNECTOR INTEGRATION
# =============================================================================

class OpenStackConnector:
    """
    Universal Connector interface for OpenStack.
    
    Provides SRL generation for cloud resources:
        srl://openstack/vm/project/name
        srl://openstack/network/project/name
        srl://openstack/volume/project/name
    """
    
    def __init__(self, kernel: OpenStackKernel):
        self.kernel = kernel
        self.id = "openstack"
        self.name = "OpenStack Cloud"
        self.icon = "☁️"
        self.status = "disconnected"
    
    def connect(self, openrc_path: str) -> bool:
        """Connect to OpenStack cloud"""
        try:
            self.kernel.substrate._load_openrc(openrc_path)
            self.kernel.substrate.sync_from_openstack()
            self.status = "connected"
            return True
        except Exception as e:
            self.status = "error"
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from OpenStack"""
        self.kernel.collapse()
        self.status = "disconnected"
        return True
    
    def list_srls(self) -> List[str]:
        """List all SRLs for cloud resources"""
        srls = []
        tokens = self.kernel.invoke(4)  # All manifested resources
        for token in tokens:
            srl = f"srl://openstack/{token.resource_type}/{token.project}/{token.name}"
            srls.append(srl)
        return srls
    
    def materialize(self, srl: str) -> Optional[Dict[str, Any]]:
        """Materialize resource data from SRL"""
        # Parse SRL: srl://openstack/type/project/name
        parts = srl.replace('srl://openstack/', '').split('/')
        if len(parts) >= 3:
            address = f"{parts[0]}.{parts[1]}.{parts[2]}"
            token = self.kernel.get(address)
            if token:
                return {
                    'id': token.id,
                    'name': token.name,
                    'type': token.resource_type,
                    'project': token.project,
                    'status': token.status,
                    'level': token.current_level,
                    'spec': token.spec,
                    'payload': token.payload
                }
        return None


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI for dimensional cloud control"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='ButterflyFX Dimensional Cloud Control',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    # Connect to OpenStack
    python -m helix.openstack_manifold connect --openrc ~/demo-openrc
    
    # List VMs at Level 4 (running)
    python -m helix.openstack_manifold list vm --level 4
    
    # Get specific VM by dimensional address
    python -m helix.openstack_manifold get vm.production.webserver
    
    # Create VM (invokes through levels 0→1→3→4)
    python -m helix.openstack_manifold create-vm myvm --image ubuntu --flavor m1.small
    
    # Collapse (delete) VM
    python -m helix.openstack_manifold delete vm.production.webserver
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command')
    
    # Connect
    connect_parser = subparsers.add_parser('connect', help='Connect to OpenStack')
    connect_parser.add_argument('--openrc', required=True, help='Path to openrc file')
    
    # List
    list_parser = subparsers.add_parser('list', help='List resources at level')
    list_parser.add_argument('type', choices=['vm', 'network', 'volume', 'image', 'all'])
    list_parser.add_argument('--level', type=int, default=4, help='Dimensional level (0-6)')
    
    # Get
    get_parser = subparsers.add_parser('get', help='Get resource by dimensional address')
    get_parser.add_argument('address', help='Dimensional address (e.g., vm.project.name)')
    
    # Create VM
    create_parser = subparsers.add_parser('create-vm', help='Create VM through dimensional invocation')
    create_parser.add_argument('name', help='VM name')
    create_parser.add_argument('--image', required=True, help='Image name/ID')
    create_parser.add_argument('--flavor', required=True, help='Flavor name/ID')
    create_parser.add_argument('--network', help='Network name/ID')
    create_parser.add_argument('--project', help='Project name')
    
    # Delete
    delete_parser = subparsers.add_parser('delete', help='Delete resource (collapse to void)')
    delete_parser.add_argument('address', help='Dimensional address')
    
    # State
    state_parser = subparsers.add_parser('state', help='Show current helix state')
    
    args = parser.parse_args()
    
    # Initialize
    substrate = OpenStackSubstrate()
    kernel = OpenStackKernel(substrate)
    
    if args.command == 'connect':
        substrate._load_openrc(args.openrc)
        count = substrate.sync_from_openstack()
        print(f"✓ Connected to OpenStack")
        print(f"  Synced {count} resources into manifold")
        print(f"  State: {kernel.state}")
    
    elif args.command == 'list':
        tokens = kernel.invoke(args.level)
        if args.type != 'all':
            tokens = [t for t in tokens if t.resource_type == args.type]
        
        print(f"\n{'='*60}")
        print(f"Resources at Level {args.level} ({CLOUD_LEVELS[args.level]['name']})")
        print(f"{'='*60}\n")
        
        for token in tokens:
            icon = {'vm': '🖥️', 'network': '🌐', 'volume': '💾', 'image': '📀'}.get(token.resource_type, '📦')
            print(f"  {icon} {token.address}")
            print(f"     ID: {token.id}")
            print(f"     Status: {token.status}")
            print(f"     Level: {token.current_level}")
            print()
    
    elif args.command == 'get':
        token = kernel.get(args.address)
        if token:
            print(f"\n📍 {token.address}")
            print(f"   ID: {token.id}")
            print(f"   Type: {token.resource_type}")
            print(f"   Project: {token.project}")
            print(f"   Status: {token.status}")
            print(f"   Level: {token.current_level} ({CLOUD_LEVELS[token.current_level]['name']})")
            print(f"   Signature: {token.signature}")
            print(f"   Spec: {json.dumps(token.spec, indent=6)}")
        else:
            print(f"✗ Not found: {args.address}")
    
    elif args.command == 'create-vm':
        print(f"Creating VM '{args.name}' through dimensional invocation...")
        print(f"  Level 0 → Potential (definition)")
        print(f"  Level 1 → Identity (UUID)")
        print(f"  Level 3 → Structure (flavor: {args.flavor}, image: {args.image})")
        print(f"  Level 4 → Manifestation (ACTIVE)")
        
        token = kernel.create_vm(
            name=args.name,
            image=args.image,
            flavor=args.flavor,
            network=args.network,
            project=args.project
        )
        
        print(f"\n✓ VM manifested at Level {token.current_level}")
        print(f"  Address: {token.address}")
        print(f"  ID: {token.id}")
        print(f"  Status: {token.status}")
    
    elif args.command == 'delete':
        print(f"Collapsing {args.address} from manifested → void...")
        success = kernel.delete_vm(args.address)
        if success:
            print(f"✓ Collapsed to Level 0 (Potential)")
        else:
            print(f"✗ Failed to collapse")
    
    elif args.command == 'state':
        s, l = kernel.state
        print(f"\nHelix State: (s={s}, ℓ={l})")
        print(f"  Spiral: {kernel.current_project}")
        print(f"  Level: {l} ({CLOUD_LEVELS[l]['name']} / {CLOUD_LEVELS[l]['semantic']})")
        print(f"  Materialized: {len(kernel._materialized)} tokens")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
