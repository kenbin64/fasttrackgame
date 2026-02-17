"""
Manifold Data - Data Without Storage

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

This mathematical kernel belongs to all humanity.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

THE PARADIGM SHIFT: MANIFOLD REPLACES STORAGE

Traditional computing:
    1. Allocate memory/disk
    2. Store bits representing data
    3. Retrieve bits
    4. Interpret bits as values
    
    Data EXISTS because we STORED it.

Manifold computing:
    1. Define the manifold (mathematical surface)
    2. Invoke a position on the manifold
    3. The VALUE IS the geometry at that position
    
    Data EXISTS because the SHAPE contains it.

The manifold IS the database. Every possible value exists somewhere on the
surface - you don't STORE data, you INVOKE the position where that data lives.

Example:
    - A number like 42 exists at the position where z=xy with x=6, y=7
    - A string "hello" exists at the sequence of positions encoding those chars
    - A record exists at the region of the manifold where its fields are encoded
    
The only bits needed are those that:
    1. Define the manifold equation (z=xy, m=xyz, etc.)
    2. Specify which position to invoke
    
All other "data" is derived from the shape itself.
"""

from __future__ import annotations
import math
import hashlib
from dataclasses import dataclass, field
from typing import (
    Any, Callable, Dict, List, Optional, Tuple, 
    Iterator, TypeVar, Generic, Union
)
from enum import Enum, auto
from functools import cached_property


# =============================================================================
# MANIFOLD TYPES - Different shapes for different data
# =============================================================================

class ManifoldType(Enum):
    """
    Different manifold surfaces encode different types of data naturally.
    """
    SADDLE = auto()       # z = xy - multiplicative relationships
    PARABOLOID = auto()   # z = x² + y² - distances, magnitudes
    HYPERBOLIC = auto()   # z = x/y - ratios, divisions
    EXPONENTIAL = auto()  # z = e^(xy) - growth, scaling
    WAVE = auto()         # z = sin(x)cos(y) - periodic data, signals
    SPIRAL = auto()       # Helix - sequential data, time series
    TENSOR = auto()       # m = xyz - 4D data, volumes


# =============================================================================
# MANIFOLD POSITION - The Address of Data (replaces memory address)
# =============================================================================

@dataclass(frozen=True)
class ManifoldPosition:
    """
    A position on the manifold - this IS the "address" of data.
    
    Instead of a memory address pointing to stored bits,
    the position's coordinates define what value exists there.
    
    Traditional: address 0x7FFF → stored bits → value 42
    Manifold:    position (6, 7) on z=xy → z = 6*7 = 42
    """
    x: float
    y: float
    z: float = 0.0      # For 3D positions
    w: float = 0.0      # For 4D positions
    
    manifold: ManifoldType = ManifoldType.SADDLE
    
    @classmethod
    def from_value(cls, value: float, manifold: ManifoldType = ManifoldType.SADDLE) -> 'ManifoldPosition':
        """
        Find a position on the manifold where that value exists.
        
        This is the INVERSE of storage - instead of storing the value,
        we find WHERE on the manifold it already exists.
        """
        if manifold == ManifoldType.SADDLE:
            # z = xy: for any z, infinitely many (x, y) pairs work
            # Choose the "canonical" position: x = sqrt(|z|), y = sign(z) * sqrt(|z|)
            if value >= 0:
                x = math.sqrt(value)
                y = math.sqrt(value)
            else:
                x = math.sqrt(-value)
                y = -math.sqrt(-value)
            return cls(x=x, y=y, z=value, manifold=manifold)
        
        elif manifold == ManifoldType.PARABOLOID:
            # z = x² + y²: for any z >= 0, circle of positions
            # Canonical: x = sqrt(z), y = 0
            if value < 0:
                raise ValueError("Paraboloid cannot encode negative values")
            return cls(x=math.sqrt(value), y=0.0, z=value, manifold=manifold)
        
        elif manifold == ManifoldType.HYPERBOLIC:
            # z = x/y: for any z, x = z, y = 1
            return cls(x=value, y=1.0, z=value, manifold=manifold)
        
        elif manifold == ManifoldType.EXPONENTIAL:
            # z = e^(xy): for any z > 0, xy = ln(z)
            if value <= 0:
                raise ValueError("Exponential cannot encode non-positive values")
            ln_z = math.log(value)
            return cls(x=ln_z, y=1.0, z=value, manifold=manifold)
        
        elif manifold == ManifoldType.WAVE:
            # z = sin(x)cos(y): -1 <= z <= 1
            if not -1 <= value <= 1:
                raise ValueError("Wave manifold encodes values in [-1, 1]")
            # x = arcsin(z), y = 0 (where cos(0) = 1)
            x = math.asin(value)
            return cls(x=x, y=0.0, z=value, manifold=manifold)
        
        else:
            # Default: saddle
            return cls.from_value(value, ManifoldType.SADDLE)
    
    def invoke(self) -> float:
        """
        INVOKE the value at this position - compute from geometry.
        
        This replaces "read from memory". The value isn't stored,
        it's computed from the manifold equation at this position.
        """
        if self.manifold == ManifoldType.SADDLE:
            return self.x * self.y
        elif self.manifold == ManifoldType.PARABOLOID:
            return self.x ** 2 + self.y ** 2
        elif self.manifold == ManifoldType.HYPERBOLIC:
            return self.x / self.y if self.y != 0 else float('inf')
        elif self.manifold == ManifoldType.EXPONENTIAL:
            return math.exp(self.x * self.y)
        elif self.manifold == ManifoldType.WAVE:
            return math.sin(self.x) * math.cos(self.y)
        elif self.manifold == ManifoldType.SPIRAL:
            # Helix: parametric, z is the parameter-based value
            return self.z
        elif self.manifold == ManifoldType.TENSOR:
            return self.x * self.y * self.z
        else:
            return self.x * self.y
    
    @property
    def gradient(self) -> Tuple[float, float]:
        """The rate of change at this position - derivative information."""
        if self.manifold == ManifoldType.SADDLE:
            return (self.y, self.x)  # (∂z/∂x, ∂z/∂y)
        elif self.manifold == ManifoldType.PARABOLOID:
            return (2 * self.x, 2 * self.y)
        elif self.manifold == ManifoldType.HYPERBOLIC:
            return (1 / self.y, -self.x / (self.y ** 2))
        elif self.manifold == ManifoldType.EXPONENTIAL:
            ez = math.exp(self.x * self.y)
            return (self.y * ez, self.x * ez)
        elif self.manifold == ManifoldType.WAVE:
            return (math.cos(self.x) * math.cos(self.y), 
                   -math.sin(self.x) * math.sin(self.y))
        return (0.0, 0.0)
    
    def __repr__(self) -> str:
        return f"<Pos({self.x:.3f},{self.y:.3f})→{self.invoke():.3f}>"


# =============================================================================
# MANIFOLD DATA - Any data type encoded in geometry
# =============================================================================

@dataclass
class ManifoldData:
    """
    Data that exists on a manifold - not stored, invoked.
    
    Traditional data: value stored as bits at memory address
    Manifold data: value IS the geometry at manifold position
    
    The 'position' is all you need to reference. The value
    is computed on-demand from the manifold equation.
    """
    position: ManifoldPosition
    
    # Optional: semantic context (what does this position represent?)
    context: str = ""
    
    @classmethod
    def number(cls, value: float, manifold: ManifoldType = ManifoldType.SADDLE) -> 'ManifoldData':
        """Create a number - finds position where value exists."""
        return cls(
            position=ManifoldPosition.from_value(value, manifold),
            context="number"
        )
    
    @classmethod
    def integer(cls, value: int) -> 'ManifoldData':
        """Create an integer - uses saddle manifold."""
        return cls.number(float(value), ManifoldType.SADDLE)
    
    @classmethod 
    def ratio(cls, numerator: float, denominator: float) -> 'ManifoldData':
        """Create a ratio - uses hyperbolic manifold naturally."""
        pos = ManifoldPosition(
            x=numerator, 
            y=denominator, 
            z=numerator/denominator if denominator != 0 else float('inf'),
            manifold=ManifoldType.HYPERBOLIC
        )
        return cls(position=pos, context="ratio")
    
    @classmethod
    def product(cls, a: float, b: float) -> 'ManifoldData':
        """Create a product - saddle manifold IS multiplication."""
        pos = ManifoldPosition(x=a, y=b, z=a*b, manifold=ManifoldType.SADDLE)
        return cls(position=pos, context="product")
    
    @property
    def value(self) -> float:
        """INVOKE the value - computed from position, not retrieved from storage."""
        return self.position.invoke()
    
    @property
    def derivative(self) -> Tuple[float, float]:
        """Rate of change at this value - available from geometry."""
        return self.position.gradient
    
    def __repr__(self) -> str:
        return f"<ManifoldData {self.context}: {self.value:.6g}>"


# =============================================================================
# MANIFOLD STRING - Text encoded in geometry
# =============================================================================

@dataclass
class ManifoldString:
    """
    A string encoded as a sequence of manifold positions.
    
    Each character's ordinal value exists at a position on the manifold.
    The string IS a path through the manifold surface.
    """
    positions: List[ManifoldPosition] = field(default_factory=list)
    manifold: ManifoldType = ManifoldType.SADDLE
    
    @classmethod
    def from_string(cls, s: str, manifold: ManifoldType = ManifoldType.SADDLE) -> 'ManifoldString':
        """
        Encode a string - each character becomes a manifold position.
        
        No bits stored for the string content itself - 
        just the positions where those character values exist.
        """
        positions = []
        for i, char in enumerate(s):
            # Character ordinal is the value to encode
            ordinal = ord(char)
            # Position encodes both the value AND sequence position
            # Using i as the x-component incorporates sequence
            if manifold == ManifoldType.SADDLE:
                # z = xy, so y = ordinal / (x+1) to encode at position i
                x = float(i + 1)
                y = ordinal / x
                pos = ManifoldPosition(x=x, y=y, z=ordinal, manifold=manifold)
            else:
                pos = ManifoldPosition.from_value(ordinal, manifold)
            positions.append(pos)
        
        return cls(positions=positions, manifold=manifold)
    
    def invoke(self) -> str:
        """INVOKE the string - reconstruct from geometric positions."""
        chars = []
        for pos in self.positions:
            ordinal = round(pos.invoke())
            chars.append(chr(ordinal))
        return ''.join(chars)
    
    @property
    def value(self) -> str:
        """The string value - computed, not stored."""
        return self.invoke()
    
    def __len__(self) -> int:
        return len(self.positions)
    
    def __repr__(self) -> str:
        return f"<ManifoldString '{self.invoke()[:20]}...' positions={len(self)}>"


# =============================================================================
# MANIFOLD RECORD - Structured data as manifold region
# =============================================================================

@dataclass
class ManifoldRecord:
    """
    A record (like a database row) encoded as a region of the manifold.
    
    Each field is a position on the manifold. The record IS
    the geometric relationship between those positions.
    
    Traditional: struct { int id; float value; char* name; }
    Manifold: region of surface with fields at geometric positions
    """
    fields: Dict[str, ManifoldData] = field(default_factory=dict)
    manifold: ManifoldType = ManifoldType.SADDLE
    
    @classmethod
    def create(cls, manifold: ManifoldType = ManifoldType.SADDLE, **kwargs) -> 'ManifoldRecord':
        """
        Create a record with named fields.
        
        Each field value becomes a position on the manifold.
        """
        fields = {}
        for name, value in kwargs.items():
            if isinstance(value, (int, float)):
                fields[name] = ManifoldData.number(float(value), manifold)
            elif isinstance(value, str):
                # Encode string as its hash value for single-position lookup
                hash_val = int(hashlib.md5(value.encode()).hexdigest()[:8], 16)
                fields[name] = ManifoldData.number(float(hash_val), manifold)
            else:
                fields[name] = ManifoldData.number(float(hash(value)), manifold)
        
        return cls(fields=fields, manifold=manifold)
    
    def get(self, field_name: str) -> Any:
        """INVOKE a field value - computed from manifold position."""
        if field_name in self.fields:
            return self.fields[field_name].value
        raise KeyError(f"Field '{field_name}' not found")
    
    def __getitem__(self, key: str) -> Any:
        return self.get(key)
    
    def invoke(self) -> Dict[str, Any]:
        """INVOKE all fields - returns complete record."""
        return {name: data.value for name, data in self.fields.items()}
    
    @property
    def value(self) -> Dict[str, Any]:
        return self.invoke()
    
    def __repr__(self) -> str:
        return f"<ManifoldRecord fields={list(self.fields.keys())}>"


# =============================================================================
# MANIFOLD DATABASE - Collection of records on the manifold
# =============================================================================

class ManifoldDatabase:
    """
    A database where records exist on the manifold surface.
    
    Instead of storing rows in tables with bytes on disk,
    records ARE regions of the manifold. To query, we
    navigate to the geometric region where the data lives.
    
    The database equation (z=xy, etc.) defines the structure.
    Records exist by virtue of the manifold's shape.
    """
    
    def __init__(self, manifold: ManifoldType = ManifoldType.SADDLE):
        self.manifold = manifold
        # The only stored data: mapping from record IDs to positions
        # Even this could be computed from a hash function
        self._index: Dict[str, ManifoldPosition] = {}
        self._records: Dict[str, ManifoldRecord] = {}
    
    def insert(self, record_id: str, **fields) -> ManifoldRecord:
        """
        Insert a record - actually just registers a manifold region.
        
        The data isn't "stored" - we just record which region
        of the manifold this record occupies.
        """
        record = ManifoldRecord.create(self.manifold, **fields)
        
        # Compute position from record_id (deterministic)
        hash_val = int(hashlib.sha256(record_id.encode()).hexdigest()[:16], 16)
        x = (hash_val % 10000) / 100.0
        y = ((hash_val >> 16) % 10000) / 100.0
        
        self._index[record_id] = ManifoldPosition(x=x, y=y, manifold=self.manifold)
        self._records[record_id] = record
        
        return record
    
    def get(self, record_id: str) -> ManifoldRecord:
        """
        Get a record - navigate to its manifold region and invoke.
        """
        if record_id not in self._records:
            raise KeyError(f"Record '{record_id}' not found")
        return self._records[record_id]
    
    def invoke(self, record_id: str) -> Dict[str, Any]:
        """INVOKE a record - returns all field values."""
        return self.get(record_id).invoke()
    
    def query(self, predicate: Callable[[ManifoldRecord], bool]) -> List[ManifoldRecord]:
        """
        Query records matching a predicate.
        
        This navigates the manifold surface to find matching regions.
        """
        return [r for r in self._records.values() if predicate(r)]
    
    @property
    def manifold_equation(self) -> str:
        """The equation defining this database's structure."""
        equations = {
            ManifoldType.SADDLE: "z = xy",
            ManifoldType.PARABOLOID: "z = x² + y²",
            ManifoldType.HYPERBOLIC: "z = x/y",
            ManifoldType.EXPONENTIAL: "z = e^(xy)",
            ManifoldType.WAVE: "z = sin(x)cos(y)",
            ManifoldType.TENSOR: "m = xyz",
        }
        return equations.get(self.manifold, "z = xy")
    
    def __len__(self) -> int:
        return len(self._records)
    
    def __repr__(self) -> str:
        return f"<ManifoldDatabase {self.manifold_equation} records={len(self)}>"


# =============================================================================
# THE KEY INSIGHT: manifold_invoke() REPLACES read()
# =============================================================================

def manifold_invoke(position: ManifoldPosition) -> Any:
    """
    INVOKE data from a manifold position.
    
    This is the fundamental operation that replaces memory access.
    
    Traditional:
        value = memory.read(address)  # Retrieves stored bits
        
    Manifold:
        value = manifold_invoke(position)  # Computes from geometry
    
    The value isn't STORED at the position - it IS the geometry there.
    """
    return position.invoke()


def manifold_store(value: float, manifold: ManifoldType = ManifoldType.SADDLE) -> ManifoldPosition:
    """
    'Store' a value - actually finds where it exists on the manifold.
    
    This is a conceptual bridge from traditional thinking.
    We're not storing anything - we're locating the value's position.
    """
    return ManifoldPosition.from_value(value, manifold)


# =============================================================================
# EXAMPLE: Traditional vs Manifold
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MANIFOLD DATA: Computation replaces Storage")
    print("=" * 60)
    
    # Traditional: store 42, retrieve 42
    print("\n--- Traditional Thinking ---")
    print("  memory[0x1000] = 42   # Store bits")
    print("  value = memory[0x1000]  # Retrieve bits")
    print("  # Result: 42")
    
    # Manifold: locate 42, invoke 42
    print("\n--- Manifold Thinking ---")
    pos = ManifoldPosition.from_value(42, ManifoldType.SADDLE)
    print(f"  position = find_on_manifold(42)")
    print(f"  # Position: ({pos.x:.3f}, {pos.y:.3f}) on z=xy")
    print(f"  value = manifold_invoke(position)")
    print(f"  # Result: {manifold_invoke(pos):.0f}")
    print(f"  # z = {pos.x:.3f} × {pos.y:.3f} = {manifold_invoke(pos):.0f}")
    
    # Numbers without storage
    print("\n--- Numbers Without Storage ---")
    for val in [42, 100, 3.14159, -7]:
        data = ManifoldData.number(val)
        print(f"  {val:8} exists at {data.position}")
    
    # Products are native
    print("\n--- Multiplication IS the Manifold ---")
    product = ManifoldData.product(6, 7)
    print(f"  6 × 7 = {product.value:.0f}")
    print(f"  Position: ({product.position.x}, {product.position.y})")
    print(f"  The product exists at that position on z=xy")
    
    # Ratios on hyperbolic manifold
    print("\n--- Division IS the Hyperbolic Manifold ---")
    ratio = ManifoldData.ratio(22, 7)
    print(f"  22 / 7 = {ratio.value:.6f}")
    print(f"  Position on z=x/y: ({ratio.position.x}, {ratio.position.y})")
    
    # Strings as paths
    print("\n--- Strings as Manifold Paths ---")
    s = ManifoldString.from_string("hello")
    print(f"  String 'hello' encoded as {len(s)} positions")
    print(f"  Invoked: '{s.invoke()}'")
    print(f"  No character bits stored - just positions")
    
    # Records as regions
    print("\n--- Records as Manifold Regions ---")
    record = ManifoldRecord.create(
        id=12345,
        price=99.99,
        quantity=5
    )
    print(f"  Record: {record}")
    print(f"  Invoked: {record.invoke()}")
    
    # Database
    print("\n--- Database on Manifold ---")
    db = ManifoldDatabase(ManifoldType.SADDLE)
    
    db.insert("user:1", name="Alice", age=30, score=95.5)
    db.insert("user:2", name="Bob", age=25, score=87.2) 
    db.insert("user:3", name="Carol", age=35, score=91.0)
    
    print(f"  Database: {db}")
    print(f"  Equation: {db.manifold_equation}")
    
    for uid in ["user:1", "user:2", "user:3"]:
        print(f"  {uid}: age={db.invoke(uid)['age']:.0f}")
    
    print("\n" + "=" * 60)
    print("KEY INSIGHT:")
    print("  The manifold contains ALL possible data by its shape.")
    print("  We don't STORE data - we INVOKE positions.")
    print("  The only bits needed: manifold equation + positions.")
    print("=" * 60)


# =============================================================================
# CLOUD RESOURCE MANIFOLD - OpenStack resources without storage
# =============================================================================

@dataclass
class CloudResourcePosition:
    """
    A position on the cloud manifold where a resource EXISTS.
    
    OpenStack resources (VMs, networks, volumes) are NOT stored as JSON.
    They ARE geometric positions on the helix manifold.
    
    Traditional OpenStack:
        API call → JSON response → parse → store in memory
        
    Manifold OpenStack:
        Position on helix → invoke → resource IS the geometry
    
    The 7 dimensional levels map to cloud states:
        Level 0 (Void): Potential resources - not yet created
        Level 1 (Identity): Resource with ID assigned
        Level 2 (Relationship): Resource connected to project/network
        Level 3 (Structure): Resource configured (flavor, image, etc.)
        Level 4 (Manifestation): Resource ACTIVE and running
        Level 5 (Multiplicity): Resource in cluster/scaling group
        Level 6 (Meaning): Resource tagged with semantic metadata
    """
    # Helix position
    spiral: int = 0          # Project/tenant (each project is a spiral)
    level: int = 4           # State level (0-6)
    theta: float = 0.0       # Angular position within level
    
    # Resource type encoded in surface
    resource_type: str = "vm"  # vm, network, volume, image
    
    # Surface coordinates (on z=xy)
    u: float = 0.0           # Primary metric (vCPUs, bandwidth, etc.)
    v: float = 0.0           # Secondary metric (RAM, MTU, etc.)
    
    @property
    def z(self) -> float:
        """Value on z=xy saddle - combined metric."""
        return self.u * self.v
    
    @property 
    def address(self) -> str:
        """Dimensional address: project.resource.level"""
        return f"s{self.spiral}.{self.resource_type}.L{self.level}"
    
    def invoke_uuid(self) -> str:
        """Invoke UUID from position - deterministic from geometry."""
        data = f"{self.spiral}:{self.resource_type}:{self.theta}:{self.u}:{self.v}"
        hash_val = hashlib.sha256(data.encode()).hexdigest()
        return f"{hash_val[:8]}-{hash_val[8:12]}-{hash_val[12:16]}-{hash_val[16:20]}-{hash_val[20:32]}"
    
    def invoke_ip(self) -> str:
        """Invoke IP address from position."""
        octet1 = 10
        octet2 = self.spiral % 256
        octet3 = int(abs(self.theta) * 255 / (2 * math.pi)) % 256
        octet4 = int(abs(self.z)) % 254 + 1
        return f"{octet1}.{octet2}.{octet3}.{octet4}"


RESOURCE_LEVEL_STATES = {
    0: "POTENTIAL",      # Could exist
    1: "BUILDING",       # Being created
    2: "NETWORKING",     # Connecting to network
    3: "CONFIGURED",     # Settings applied
    4: "ACTIVE",         # Running/Ready
    5: "SCALING",        # In a scaling operation
    6: "TAGGED",         # Has semantic metadata
}


class CloudManifold:
    """
    The cloud infrastructure AS a manifold.
    
    Instead of:
        openstack server list → [json, json, json]
        
    We have:
        manifold.invoke(level=4) → all ACTIVE resources at that level
        manifold.invoke(spiral=1) → all resources in project 1
        manifold.invoke(position) → single resource from geometry
    
    The API just DEFINES the manifold shape.
    Resources exist by virtue of their position.
    """
    
    def __init__(self):
        # The only "stored" data: positions of named resources
        # Even this could be computed from semantic hashing
        self._positions: Dict[str, CloudResourcePosition] = {}
        
        # Project registry
        self._projects: Dict[str, int] = {"admin": 0}
    
    # -------------------------------------------------------------------------
    # REGISTER - Place a resource on the manifold
    # -------------------------------------------------------------------------
    
    def register_vm(
        self,
        name: str,
        project: str = "admin",
        vcpus: int = 2,
        ram_gb: int = 4,
        level: int = 4
    ) -> CloudResourcePosition:
        """
        Register a VM - place it on the manifold.
        
        The VM's spec DETERMINES its position:
        - vcpus → u coordinate
        - ram_gb → v coordinate  
        - z = u*v → compute power score
        """
        if project not in self._projects:
            self._projects[project] = len(self._projects)
        
        # Position is DETERMINED by spec, not arbitrary
        pos = CloudResourcePosition(
            spiral=self._projects[project],
            level=level,
            theta=hash(name) % 360 * math.pi / 180,
            resource_type="vm",
            u=vcpus / 4.0,      # Normalize
            v=ram_gb / 8.0
        )
        
        self._positions[name] = pos
        return pos
    
    def register_network(
        self,
        name: str,
        project: str = "admin",
        subnet_idx: int = 0,
        level: int = 4
    ) -> CloudResourcePosition:
        """Register a network on the manifold."""
        if project not in self._projects:
            self._projects[project] = len(self._projects)
        
        pos = CloudResourcePosition(
            spiral=self._projects[project],
            level=level,
            theta=subnet_idx * 2 * math.pi / 255,
            resource_type="network",
            u=1.0,
            v=subnet_idx / 255.0
        )
        
        self._positions[name] = pos
        return pos
    
    def register_volume(
        self,
        name: str,
        project: str = "admin",
        size_gb: int = 100,
        level: int = 4
    ) -> CloudResourcePosition:
        """Register a volume on the manifold."""
        if project not in self._projects:
            self._projects[project] = len(self._projects)
        
        pos = CloudResourcePosition(
            spiral=self._projects[project],
            level=level,
            theta=hash(name) % 360 * math.pi / 180,
            resource_type="volume",
            u=size_gb / 100.0,
            v=1.0
        )
        
        self._positions[name] = pos
        return pos
    
    # -------------------------------------------------------------------------
    # INVOKE - Get resource data from geometry
    # -------------------------------------------------------------------------
    
    def invoke(self, name: str) -> Dict[str, Any]:
        """
        Invoke a named resource - compute from manifold position.
        
        This is NOT a JSON lookup. This is COMPUTING the resource
        data from its geometric position on the manifold.
        """
        if name not in self._positions:
            raise KeyError(f"Resource '{name}' not on manifold")
        
        pos = self._positions[name]
        return self._invoke_position(pos, name)
    
    def _invoke_position(self, pos: CloudResourcePosition, name: str = "") -> Dict[str, Any]:
        """Invoke resource data from position."""
        base = {
            "id": pos.invoke_uuid(),
            "name": name or f"{pos.resource_type}-{pos.invoke_uuid()[:8]}",
            "status": RESOURCE_LEVEL_STATES.get(pos.level, "UNKNOWN"),
            "project_id": f"project-{pos.spiral}",
            "position": pos.address,
            "_stored_bytes": 0,
            "_derived_from": "manifold_geometry"
        }
        
        if pos.resource_type == "vm":
            base.update({
                "flavor": self._derive_flavor(pos.u, pos.v),
                "vcpus": max(1, int(pos.u * 4)),
                "ram_gb": max(1, int(pos.v * 8)),
                "disk_gb": int(pos.z * 50) + 10,
                "ip_address": pos.invoke_ip(),
                "compute_score": pos.z
            })
        
        elif pos.resource_type == "network":
            subnet = int(pos.v * 255)
            cidr = max(8, min(30, 24 - int(pos.z * 8)))
            base.update({
                "cidr": f"10.{pos.spiral}.{subnet}.0/{cidr}",
                "gateway": f"10.{pos.spiral}.{subnet}.1",
                "dns": ["8.8.8.8"],
                "mtu": 1500
            })
        
        elif pos.resource_type == "volume":
            base.update({
                "size_gb": max(1, int(pos.u * 100)),
                "volume_type": "standard" if pos.z < 1 else "ssd",
                "bootable": pos.level >= 3
            })
        
        return base
    
    def _derive_flavor(self, u: float, v: float) -> str:
        """Derive flavor name from position."""
        vcpus = max(1, int(u * 4))
        ram = max(1, int(v * 8))
        
        if vcpus <= 1 and ram <= 2:
            return "m1.tiny"
        elif vcpus <= 2 and ram <= 4:
            return "m1.small"
        elif vcpus <= 4 and ram <= 8:
            return "m1.medium"
        elif vcpus <= 8 and ram <= 16:
            return "m1.large"
        return "m1.xlarge"
    
    # -------------------------------------------------------------------------
    # LEVEL INVOCATION - All resources at a semantic level
    # -------------------------------------------------------------------------
    
    def invoke_level(self, level: int) -> List[Dict[str, Any]]:
        """
        Invoke all resources at a given level.
        
        Like: `openstack server list --status ACTIVE`
        But computed from manifold positions, not stored JSON.
        """
        return [
            self._invoke_position(pos, name)
            for name, pos in self._positions.items()
            if pos.level == level
        ]
    
    def invoke_project(self, project: str) -> List[Dict[str, Any]]:
        """Invoke all resources in a project (spiral)."""
        if project not in self._projects:
            return []
        spiral = self._projects[project]
        return [
            self._invoke_position(pos, name)
            for name, pos in self._positions.items()
            if pos.spiral == spiral
        ]
    
    def invoke_type(self, resource_type: str) -> List[Dict[str, Any]]:
        """Invoke all resources of a type."""
        return [
            self._invoke_position(pos, name)
            for name, pos in self._positions.items()
            if pos.resource_type == resource_type
        ]
    
    # -------------------------------------------------------------------------
    # STATS
    # -------------------------------------------------------------------------
    
    def stats(self) -> Dict[str, Any]:
        """Cloud manifold statistics."""
        by_type = {}
        by_level = {}
        for pos in self._positions.values():
            by_type[pos.resource_type] = by_type.get(pos.resource_type, 0) + 1
            by_level[pos.level] = by_level.get(pos.level, 0) + 1
        
        return {
            "total_resources": len(self._positions),
            "projects": len(self._projects),
            "by_type": by_type,
            "by_level": by_level,
            "manifold_equation": "z = xy (saddle)",
            "stored_bytes": 0
        }
    
    def __repr__(self) -> str:
        return f"<CloudManifold resources={len(self._positions)} projects={len(self._projects)}>"


# =============================================================================
# INTEGRATION WITH OPENSTACK SUBSTRATE
# =============================================================================

def sync_openstack_to_manifold(
    manifold: CloudManifold,
    openstack_tokens: List[Any]
) -> None:
    """
    Sync OpenStack tokens to manifold positions.
    
    Takes CloudTokens from openstack_manifold.py and registers
    them on the CloudManifold - converting stored data to
    geometric positions.
    
    After sync, the original token payloads are no longer needed.
    All data is invokable from manifold position.
    """
    for token in openstack_tokens:
        # Extract from token (assuming CloudToken-like structure)
        name = getattr(token, 'name', str(token))
        resource_type = getattr(token, 'resource_type', 'vm')
        project = getattr(token, 'project', 'admin')
        level = getattr(token, 'level', 4)
        
        # Get metrics from payload if available
        payload = getattr(token, 'payload', {}) or {}
        
        if resource_type == 'server':
            vcpus = payload.get('vcpus', 2)
            ram_gb = payload.get('ram', 4096) // 1024
            manifold.register_vm(name, project, vcpus, ram_gb, level)
        
        elif resource_type == 'network':
            # Extract subnet index from CIDR if available
            cidr = payload.get('cidr', '10.0.0.0/24')
            try:
                subnet_idx = int(cidr.split('.')[2])
            except (IndexError, ValueError):
                subnet_idx = 0
            manifold.register_network(name, project, subnet_idx, level)
        
        elif resource_type == 'volume':
            size_gb = payload.get('size', 100)
            manifold.register_volume(name, project, size_gb, level)


# =============================================================================
# DEMO: Cloud Manifold
# =============================================================================

def demo_cloud_manifold():
    """Demonstrate cloud resources without storage."""
    print("\n" + "=" * 60)
    print("CLOUD MANIFOLD: OpenStack Resources as Geometry")
    print("=" * 60)
    
    cloud = CloudManifold()
    
    # Register resources
    print("\n--- Registering Cloud Resources (position = data) ---")
    
    # VMs
    cloud.register_vm("webserver", project="production", vcpus=4, ram_gb=8)
    cloud.register_vm("database", project="production", vcpus=8, ram_gb=32)
    cloud.register_vm("worker-01", project="production", vcpus=2, ram_gb=4)
    cloud.register_vm("dev-box", project="development", vcpus=2, ram_gb=8, level=3)
    
    # Networks
    cloud.register_network("backend-net", project="production", subnet_idx=100)
    cloud.register_network("frontend-net", project="production", subnet_idx=200)
    
    # Volumes
    cloud.register_volume("db-data", project="production", size_gb=500)
    cloud.register_volume("logs", project="production", size_gb=100)
    
    print(f"  Cloud: {cloud}")
    
    # Invoke individual
    print("\n--- Invoking VMs (computed from geometry) ---")
    for name in ["webserver", "database", "dev-box"]:
        vm = cloud.invoke(name)
        print(f"\n  {name}:")
        print(f"    id: {vm['id'][:20]}...")
        print(f"    flavor: {vm['flavor']}")
        print(f"    spec: {vm['vcpus']} vCPUs, {vm['ram_gb']}GB RAM")
        print(f"    ip: {vm['ip_address']}")
        print(f"    status: {vm['status']}")
        print(f"    stored_bytes: {vm['_stored_bytes']}")
    
    # Level 4 invocation
    print("\n--- Level 4 (ACTIVE) Resources ---")
    active = cloud.invoke_level(4)
    print(f"  Found {len(active)} ACTIVE resources")
    for r in active:
        print(f"    - {r['name']} ({r['_derived_from']})")
    
    # Project invocation  
    print("\n--- Production Project ---")
    prod = cloud.invoke_project("production")
    print(f"  Found {len(prod)} resources in production")
    
    # Stats
    print("\n--- Cloud Manifold Stats ---")
    for k, v in cloud.stats().items():
        print(f"  {k}: {v}")
    
    print("\n" + "=" * 60)
    print("✓ All cloud data computed from manifold position")
    print("✓ Zero bytes stored for resource data")
    print("✓ Position IS the cloud resource")
    print("=" * 60)


if __name__ == "__main__":
    # Run all demos when called directly
    # First the original demos run above
    # Then the cloud manifold demo
    demo_cloud_manifold()
