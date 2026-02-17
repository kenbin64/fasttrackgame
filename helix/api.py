"""
ButterflyFX Human-First API — Intentions Over Coordinates

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)

---

HUMAN-FIRST DESIGN — the engine translates to geometry under the hood.

Developers write:
    card = shape("rectangle").place("center").orient("landscape")
    title = text("Hello").attachTo(card, "top-inside").align("center")
    
The engine resolves:
    "center" → x=0.5, y=0.5 (normalized substrate position)
    "landscape" → θ=0
    "top-inside" → relative offset computed from parent geometry

THE KEY PRINCIPLE:
    We do NOT store what the substrate gives us inherently.
    Human concepts translate to substrate positions.
    The manifold IS the computation.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto

# Import the REAL substrate system
from .dimensional_api import (
    Substrate, Substrate0D, Substrate1D, Substrate2D, 
    Substrate3D, Substrate4D,
    Interface, Object,
    invoke as _invoke,
    Level,
)
from .geometric_substrate import (
    GeometricSubstrate,
    Shape as GeoShape,
    Lens,
    Point as GeometricPoint,
)

__all__ = [
    # Space creation
    'space', 'Space',
    
    # Dimension (objects exist by virtue of dimension)
    'dimension', 'Dimension',
    
    # Entity creation - human concepts
    'shape', 'text', 'point', 'line', 'group',
    
    # Shapes
    'rectangle', 'circle', 'triangle', 'polygon',
    
    # Relationships
    'attachTo', 'placeRelativeTo', 'align', 'orient',
    
    # Semantic positions
    'Position', 'Direction', 'Orientation', 'Size',
    
    # Builders
    'Entity', 'ShapeBuilder', 'TextBuilder', 'LineBuilder',
    
    # Low-level escape hatch
    'advanced',
    
    # Unified lookup (single entry point)
    'find',
    
    # Multi-path lookup (specific methods)
    'by_id', 'by_name', 'by_kind', 'by_attribute', 'by_attr', 'by_prop',
    'by_dimension', 'dim',
    'query', 'find_entities',
    
    # Identity System
    'identity', 'by_identity', 'register_identity', 'clear_identities',
    'IdentityLookup',
    
    # Datastore (lazy ingest, instance vs persisted attrs)
    'Datastore', 'register_datastore', 'get_datastore',
    
    # Registry management
    'register_dimension', 'clear_indices',
    
    # Stats
    'count', 'reset',
]


# =============================================================================
# SEMANTIC VOCABULARY — Human concepts, not coordinates
# =============================================================================

class Position(Enum):
    """Semantic positions on a space."""
    CENTER = auto()
    TOP = auto()
    BOTTOM = auto()
    LEFT = auto()
    RIGHT = auto()
    TOP_LEFT = auto()
    TOP_RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_RIGHT = auto()
    TOP_EDGE = auto()
    BOTTOM_EDGE = auto()
    LEFT_EDGE = auto()
    RIGHT_EDGE = auto()


class Direction(Enum):
    """Semantic directions."""
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    DIAGONAL_TOP_LEFT = auto()
    DIAGONAL_TOP_RIGHT = auto()
    DIAGONAL_BOTTOM_LEFT = auto()
    DIAGONAL_BOTTOM_RIGHT = auto()


class Orientation(Enum):
    """Semantic orientations."""
    LANDSCAPE = auto()      # θ = 0
    PORTRAIT = auto()       # θ = π/2
    UPSIDE_DOWN = auto()    # θ = π
    ROTATED_LEFT = auto()   # θ = 3π/2
    FACING_UP = auto()      # θ = π/2
    FACING_DOWN = auto()    # θ = 3π/2
    FACING_LEFT = auto()    # θ = π
    FACING_RIGHT = auto()   # θ = 0


class Size(Enum):
    """Semantic sizes."""
    TINY = auto()       # 0.05
    SMALL = auto()      # 0.1
    MEDIUM = auto()     # 0.2
    LARGE = auto()      # 0.4
    HUGE = auto()       # 0.6
    FULL = auto()       # 1.0


class Anchor(Enum):
    """Semantic anchor points."""
    CENTER = auto()
    TOP = auto()
    BOTTOM = auto()
    LEFT = auto()
    RIGHT = auto()
    TOP_LEFT = auto()
    TOP_RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_RIGHT = auto()


class Relation(Enum):
    """Semantic spatial relationships."""
    ABOVE = auto()
    BELOW = auto()
    LEFT_OF = auto()
    RIGHT_OF = auto()
    INSIDE = auto()
    OUTSIDE = auto()
    TOP_INSIDE = auto()
    BOTTOM_INSIDE = auto()
    LEFT_INSIDE = auto()
    RIGHT_INSIDE = auto()
    TOP_OUTSIDE = auto()
    BOTTOM_OUTSIDE = auto()
    TOP_LEFT_OUTSIDE = auto()
    TOP_RIGHT_OUTSIDE = auto()
    BOTTOM_LEFT_OUTSIDE = auto()
    BOTTOM_RIGHT_OUTSIDE = auto()


# =============================================================================
# TRANSLATION TABLES — Human → Substrate
# =============================================================================

# Position → (x, y) normalized coordinates
POSITION_TO_COORDS: Dict[str, Tuple[float, float]] = {
    'center': (0.5, 0.5),
    'top': (0.5, 1.0),
    'bottom': (0.5, 0.0),
    'left': (0.0, 0.5),
    'right': (1.0, 0.5),
    'top-left': (0.0, 1.0),
    'top-right': (1.0, 1.0),
    'bottom-left': (0.0, 0.0),
    'bottom-right': (1.0, 0.0),
    'top-edge': (0.5, 1.0),
    'bottom-edge': (0.5, 0.0),
    'left-edge': (0.0, 0.5),
    'right-edge': (1.0, 0.5),
}

# Orientation → angle in radians
ORIENTATION_TO_ANGLE: Dict[str, float] = {
    'landscape': 0.0,
    'horizontal': 0.0,
    'portrait': math.pi / 2,
    'vertical': math.pi / 2,
    'upside-down': math.pi,
    'rotated-left': 3 * math.pi / 2,
    'facing-up': math.pi / 2,
    'facing-down': 3 * math.pi / 2,
    'facing-left': math.pi,
    'facing-right': 0.0,
    'diagonal': math.pi / 4,
    'diagonal-top-right': math.pi / 4,
    'diagonal-top-left': 3 * math.pi / 4,
    'diagonal-bottom-left': 5 * math.pi / 4,
    'diagonal-bottom-right': 7 * math.pi / 4,
}

# Direction → unit vector (dx, dy)
DIRECTION_TO_VECTOR: Dict[str, Tuple[float, float]] = {
    'up': (0.0, 1.0),
    'down': (0.0, -1.0),
    'left': (-1.0, 0.0),
    'right': (1.0, 0.0),
    'diagonal-top-left': (-0.707, 0.707),
    'diagonal-top-right': (0.707, 0.707),
    'diagonal-bottom-left': (-0.707, -0.707),
    'diagonal-bottom-right': (0.707, -0.707),
}

# Size → normalized value
SIZE_TO_VALUE: Dict[str, float] = {
    'tiny': 0.05,
    'small': 0.1,
    'medium': 0.2,
    'large': 0.4,
    'huge': 0.6,
    'full': 1.0,
}

# Anchor → (ax, ay) anchor offset
ANCHOR_TO_OFFSET: Dict[str, Tuple[float, float]] = {
    'center': (0.5, 0.5),
    'middle': (0.5, 0.5),
    'top': (0.5, 1.0),
    'bottom': (0.5, 0.0),
    'left': (0.0, 0.5),
    'right': (1.0, 0.5),
    'top-left': (0.0, 1.0),
    'top-right': (1.0, 1.0),
    'bottom-left': (0.0, 0.0),
    'bottom-right': (1.0, 0.0),
}

# Relation → (dx, dy) relative offset direction + inside/outside flag
RELATION_TO_OFFSET: Dict[str, Tuple[float, float, bool]] = {
    # (dx, dy, inside)
    'above': (0.0, 1.0, False),
    'below': (0.0, -1.0, False),
    'left-of': (-1.0, 0.0, False),
    'right-of': (1.0, 0.0, False),
    'inside': (0.0, 0.0, True),
    'outside': (0.0, 0.0, False),
    'top-inside': (0.0, 0.5, True),
    'bottom-inside': (0.0, -0.5, True),
    'left-inside': (-0.5, 0.0, True),
    'right-inside': (0.5, 0.0, True),
    'top-outside': (0.0, 1.0, False),
    'bottom-outside': (0.0, -1.0, False),
    'top-left-outside': (-1.0, 1.0, False),
    'top-right-outside': (1.0, 1.0, False),
    'bottom-left-outside': (-1.0, -1.0, False),
    'bottom-right-outside': (1.0, -1.0, False),
}


# =============================================================================
# IDENTITY SYSTEM — Unique identification, dimensional drilling
# =============================================================================

# Global registry: identity → Entity
_identity_registry: Dict[str, 'Entity'] = {}

# Identity index: (identity_type, identity_value) → Entity
_identity_index: Dict[Tuple[str, Any], 'Entity'] = {}


def by_identity(identity_value: Any, identity_type: str = "id") -> Optional['Entity']:
    """
    Look up an entity by its unique identity.
    
    Identity is ANY information completely unique to that object.
    For a car: VIN. For a person: SSN. For a product: SKU.
    
    Args:
        identity_value: The unique identifier value
        identity_type: The type of identity (default: "id")
        
    Returns:
        The Entity if found, None otherwise
        
    Example:
        # Register a car with VIN
        my_car = canvas.shape("rectangle").identify(vin="1HGBH41JXMN109186").done()
        
        # Later, retrieve by identity
        car = by_identity("1HGBH41JXMN109186", "vin")
        car.drillDown("engine").select("horsepower")
    """
    key = (identity_type.lower(), identity_value)
    return _identity_index.get(key)


def register_identity(entity: 'Entity', identity_value: Any, identity_type: str = "id") -> None:
    """Register an entity with a unique identity."""
    key = (identity_type.lower(), identity_value)
    _identity_index[key] = entity
    _identity_registry[str(identity_value)] = entity


def clear_identities() -> None:
    """Clear all identity registrations."""
    _identity_registry.clear()
    _identity_index.clear()


class IdentityLookup:
    """
    Fluent interface for identity-based entity access.
    
    Example:
        car = (identity("1HGBH41JXMN109186", "vin")
               .verify()
               .drillDown("engine")
               .select("horsepower"))
    """
    
    def __init__(self, identity_value: Any, identity_type: str = "id"):
        self._identity_value = identity_value
        self._identity_type = identity_type
        self._entity: Optional['Entity'] = None
        self._verified = False
        self._current_part: Optional['Entity'] = None
    
    def verify(self) -> 'IdentityLookup':
        """Verify identity exists and load the entity."""
        self._entity = by_identity(self._identity_value, self._identity_type)
        if self._entity is not None:
            self._verified = True
            self._current_part = self._entity
        return self
    
    @property
    def verified(self) -> bool:
        """Check if identity was verified."""
        return self._verified
    
    @property
    def entity(self) -> Optional['Entity']:
        """Get the verified entity."""
        return self._entity if self._verified else None
    
    @property
    def current(self) -> Optional['Entity']:
        """Get current part after drilling."""
        return self._current_part
    
    def drillDown(self, part_name: str) -> 'IdentityLookup':
        """
        Drill down dimensionally to a child component.
        
        After identity is verified, navigate to sub-components.
        
        Args:
            part_name: Name of the child entity to navigate to
            
        Example:
            car = identity("VIN123").verify()
            engine = car.drillDown("engine")  # Navigate to engine
            piston = engine.drillDown("piston1")  # Navigate deeper
        """
        if not self._verified or self._current_part is None:
            return self
        
        # Find child with matching name
        for child in self._current_part.children:
            if child.name == part_name or child.kind == part_name:
                self._current_part = child
                return self
        
        # Not found - stay at current
        return self
    
    def drillUp(self) -> 'IdentityLookup':
        """
        Drill up dimensionally to the parent.
        
        Example:
            piston = identity("PISTON123").verify()
            engine = piston.drillUp()  # Navigate to engine
            car = engine.drillUp()  # Navigate to car
        """
        if not self._verified or self._current_part is None:
            return self
        
        if self._current_part.parent is not None:
            self._current_part = self._current_part.parent
        
        return self
    
    def drillAcross(self, sibling_name: str) -> 'IdentityLookup':
        """
        Drill across to a sibling at the same dimensional level.
        
        Example:
            engine = identity("ENGINE123").verify()
            transmission = engine.drillAcross("transmission")  # Same parent
        """
        if not self._verified or self._current_part is None:
            return self
        
        parent = self._current_part.parent
        if parent is None:
            return self
        
        for sibling in parent.children:
            if sibling.name == sibling_name or sibling.kind == sibling_name:
                self._current_part = sibling
                return self
        
        return self
    
    def select(self, *properties: str) -> Dict[str, Any]:
        """
        Select specific properties after identity is verified.
        
        Args:
            *properties: Names of properties to retrieve
            
        Returns:
            Dict with requested properties
            
        Example:
            data = (identity("VIN123")
                    .verify()
                    .drillDown("engine")
                    .select("horsepower", "torque", "cylinders"))
        """
        if not self._verified or self._current_part is None:
            return {}
        
        result = {}
        entity = self._current_part
        
        for prop in properties:
            # Check derived geometric properties
            if hasattr(entity, prop):
                result[prop] = getattr(entity, prop)
            # Check custom properties
            elif prop in entity.props:
                result[prop] = entity.props[prop]
            # Check core fields
            elif prop in ('x', 'y', 'width', 'height', 'angle', 'level', 'name', 'kind', 'id'):
                result[prop] = getattr(entity, prop)
        
        return result
    
    def all(self) -> Dict[str, Any]:
        """Get all information about the current part."""
        if not self._verified or self._current_part is None:
            return {}
        return self._current_part.to_dict()


def identity(value: Any, identity_type: str = "id") -> IdentityLookup:
    """
    Start an identity-based lookup.
    
    Identity is ANY information completely unique to that object.
    Once you bring it up, it brings ALL information.
    If you only want one part, that part is identified after identity is verified.
    
    Args:
        value: The unique identity value
        identity_type: Type of identity ("id", "vin", "ssn", "sku", etc.)
        
    Returns:
        IdentityLookup for fluent chaining
        
    Example:
        # A car can be identified by VIN
        car = identity("1HGBH41JXMN109186", "vin").verify()
        
        # Drill down to a specific part
        engine = car.drillDown("engine")
        
        # Select only what you need
        hp = engine.select("horsepower")
        
        # Or get everything
        all_engine_data = engine.all()
    """
    return IdentityLookup(value, identity_type)


# =============================================================================
# MULTI-PATH LOOKUP — Find objects by id, name, attribute, type, dimension
# =============================================================================

# Global index by name (type)
_name_index: Dict[str, List['Entity']] = {}

# Global index by kind (visual type)
_kind_index: Dict[str, List['Entity']] = {}

# Global index by attribute value
_attribute_index: Dict[Tuple[str, Any], List['Entity']] = {}

# Dimension registry: name or number → Space
_dimension_registry: Dict[Union[str, int], 'Space'] = {}
_dimension_counter = 0


def _register_entity_indices(entity: 'Entity') -> None:
    """Register entity in all lookup indices."""
    # By name (type)
    if entity.name not in _name_index:
        _name_index[entity.name] = []
    _name_index[entity.name].append(entity)
    
    # By kind (visual type)
    if entity.kind not in _kind_index:
        _kind_index[entity.kind] = []
    _kind_index[entity.kind].append(entity)
    
    # By each attribute/property
    for key, value in entity.props.items():
        attr_key = (key, value)
        if attr_key not in _attribute_index:
            _attribute_index[attr_key] = []
        _attribute_index[attr_key].append(entity)


def register_dimension(space: 'Space', name: str = None, number: int = None) -> None:
    """Register a dimension (Space) by name and/or number."""
    global _dimension_counter
    if name:
        _dimension_registry[name] = space
    if number is not None:
        _dimension_registry[number] = space
    else:
        _dimension_registry[_dimension_counter] = space
        _dimension_counter += 1


def clear_indices() -> None:
    """Clear all lookup indices."""
    global _dimension_counter
    _name_index.clear()
    _kind_index.clear()
    _attribute_index.clear()
    _dimension_registry.clear()
    _dimension_counter = 0
    clear_identities()


# -----------------------------------------------------------------------------
# Lookup by ID (unique identifier) — returns ONE entity
# -----------------------------------------------------------------------------

def by_id(id_value: Any) -> Optional['Entity']:
    """
    Look up entity by unique ID.
    
    Example:
        car = by_id("VIN123")
        user = by_id("user-uuid-456")
    """
    return by_identity(id_value, "id")


# -----------------------------------------------------------------------------
# Lookup by Name (type) — returns LIST (multiple cars exist)
# -----------------------------------------------------------------------------

def by_name(name: str) -> List['Entity']:
    """
    Look up all entities of a given name/type.
    
    Example:
        all_cars = by_name("car")      # All car objects
        all_pistons = by_name("piston")  # All piston objects
    """
    return _name_index.get(name, [])


# -----------------------------------------------------------------------------
# Lookup by Kind (visual type) — returns LIST
# -----------------------------------------------------------------------------

def by_kind(kind: str) -> List['Entity']:
    """
    Look up all entities with a given visual kind.
    
    Example:
        all_rectangles = by_kind("rectangle")
        all_circles = by_kind("circle")
    """
    return _kind_index.get(kind, [])


# -----------------------------------------------------------------------------
# Lookup by Attribute — returns LIST
# -----------------------------------------------------------------------------

def by_attribute(attr_name: str, attr_value: Any) -> List['Entity']:
    """
    Look up all entities with a specific attribute value.
    
    Example:
        red_things = by_attribute("color", "red")
        electric_cars = by_attribute("type", "electric")
        high_power = by_attribute("horsepower", 670)
    """
    return _attribute_index.get((attr_name, attr_value), [])


# Alias
by_attr = by_attribute
by_prop = by_attribute


# -----------------------------------------------------------------------------
# Lookup by Dimension — returns Space
# -----------------------------------------------------------------------------

def by_dimension(name_or_number: Union[str, int]) -> Optional['Space']:
    """
    Look up a dimension by name or number.
    
    Dimensions can be named ("physics", "ui", "audio")
    or numbered (0, 1, 2, 3...).
    
    Example:
        physics_space = by_dimension("physics")
        first_space = by_dimension(0)
    """
    return _dimension_registry.get(name_or_number)


# Alias
dim = by_dimension


# -----------------------------------------------------------------------------
# Combined Query — find with multiple criteria
# -----------------------------------------------------------------------------

def query(
    id: Optional[str] = None,
    name: Optional[str] = None,
    kind: Optional[str] = None,
    dimension: Optional[Union[str, int]] = None,
    **attributes
) -> List['Entity']:
    """
    Query entities with multiple criteria.
    
    Returns entities matching ALL criteria.
    
    Args:
        id: Exact unique ID (returns 0 or 1 result)
        name: Entity name/type (e.g., "car", "engine")
        kind: Visual kind (e.g., "rectangle", "circle")
        dimension: Space name or number to search in
        **attributes: Property filters (e.g., color="red")
        
    Example:
        # Find red cars
        red_cars = query(name="car", color="red")
        
        # Find circles in physics dimension
        circles = query(kind="circle", dimension="physics")
        
        # Find specific car by VIN
        my_car = query(id="VIN123")
    """
    # Start with ID lookup if provided
    if id is not None:
        entity = by_id(id)
        if entity is None:
            return []
        # Filter by other criteria
        results = [entity]
        if name and entity.name != name:
            return []
        if kind and entity.kind != kind:
            return []
        for attr, val in attributes.items():
            if entity.props.get(attr) != val:
                return []
        return results
    
    # Otherwise, gather candidates
    candidates: Optional[List['Entity']] = None
    
    # Filter by name
    if name is not None:
        candidates = by_name(name)
    
    # Filter by kind
    if kind is not None:
        kind_matches = by_kind(kind)
        if candidates is None:
            candidates = kind_matches
        else:
            candidates = [e for e in candidates if e in kind_matches]
    
    # Filter by attributes
    for attr, val in attributes.items():
        attr_matches = by_attribute(attr, val)
        if candidates is None:
            candidates = attr_matches
        else:
            candidates = [e for e in candidates if e in attr_matches]
    
    # Filter by dimension
    if dimension is not None:
        space = by_dimension(dimension)
        if space is None:
            return []
        if candidates is None:
            candidates = list(space._entities.values())
        else:
            space_entities = set(space._entities.values())
            candidates = [e for e in candidates if e in space_entities]
    
    return candidates if candidates is not None else []


# Alias
find_entities = query


# =============================================================================
# UNIFIED find() — Single entry point for all lookups
# =============================================================================

def find(
    identifier: Optional[str] = None,
    *,
    name: Optional[str] = None,
    kind: Optional[str] = None,
    dimension: Optional[Union[str, int]] = None,
    datastore: Optional[str] = None,
    **attributes
) -> Union[Optional['Entity'], List['Entity']]:
    """
    Universal lookup — find entities by any criteria.
    
    Objects exist by virtue of their dimension existing.
    No tables, no JOINs, no foreign keys.
    
    Args:
        identifier: If provided alone, finds by unique ID (returns 1 entity)
        name: Filter by entity name/type (e.g., "car", "engine")
        kind: Filter by visual kind (e.g., "rectangle", "circle")
        dimension: Filter by dimension name or number
        datastore: External datastore name (lazy ingest)
        **attributes: Property filters (e.g., color="red")
    
    Returns:
        Single Entity if identifier provided alone, List[Entity] otherwise
    
    Examples:
        # Find ONE by unique ID
        my_car = find("VIN-123")
        
        # Find ALL cars
        all_cars = find(name="car")
        
        # Find from external datastore (lazy ingest)
        car = find("VIN-123", datastore="cars_db")
        
        # Find red circles in physics dimension
        red_circles = find(kind="circle", dimension="physics", color="red")
        
        # Drill without JOINs - objects exist by dimension
        engine = find("VIN-123").drillDown("engine")
        hp = engine.select("horsepower")
    """
    # Datastore lookup (lazy ingest from external)
    if datastore is not None and identifier is not None:
        ds = get_datastore(datastore)
        if ds is None:
            raise ValueError(f"Datastore '{datastore}' not registered")
        return ds.get(identifier)
    
    # If only identifier, do quick id lookup
    if identifier is not None and name is None and kind is None and dimension is None and not attributes:
        return by_id(identifier)
    
    # Otherwise use full query
    return query(id=identifier, name=name, kind=kind, dimension=dimension, **attributes)


# =============================================================================
# DIMENSION CLASS — Objects exist by virtue of dimension
# =============================================================================

class Dimension:
    """
    A dimensional space where objects exist inherently.
    
    This is NOT a database table. There are NO foreign keys, NO JOINs.
    
    When a dimension exists:
    - Objects in it exist by position on the manifold
    - Properties are DERIVED from geometry
    - Relationships are geometric (drillDown/drillUp)
    - "Adding" materializes what's already inherent
    
    Example:
        physics = Dimension("physics", 800, 600)
        
        # Materialize entities - no INSERT
        car = physics.materialize("car", id="VIN-123", brand="Tesla")
        engine = physics.materialize("engine", parent=car, horsepower=670)
        
        # Invoke via dimension - no JOIN
        my_car = physics.invoke("VIN-123")
        my_engine = my_car.drillDown("engine")  # NOT a JOIN!
    """
    
    def __init__(self, name: str, width: float = 100.0, height: float = 100.0):
        self._space = Space(width, height, name)
        self._name = name
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def space(self) -> 'Space':
        return self._space
    
    def materialize(
        self,
        name: str,
        id: Optional[str] = None,
        parent: Optional['Entity'] = None,
        position: str = "center",
        kind: str = "rectangle",
        **props
    ) -> 'Entity':
        """
        Materialize an object in this dimension.
        
        Objects don't get "added" - they EXIST by position.
        We're specifying where on the manifold they materialize.
        """
        builder = self._space.shape(kind, id=id).name(name).place(position)
        for k, v in props.items():
            builder.prop(**{k: v})
        
        entity = builder.done()
        
        if parent is not None:
            entity.parent = parent
            parent.children.append(entity)
        
        return entity
    
    # =========================================================================
    # SHAPE BUILDERS — Create entities in this dimension
    # =========================================================================
    
    def rectangle(self, id: Optional[str] = None, name: str = "rectangle", 
                  position: str = "center", **props) -> 'Entity':
        """Create a rectangle in this dimension."""
        return self.materialize(kind="rectangle", id=id, name=name, position=position, **props)
    
    def circle(self, id: Optional[str] = None, name: str = "circle",
               position: str = "center", **props) -> 'Entity':
        """Create a circle in this dimension."""
        return self.materialize(kind="circle", id=id, name=name, position=position, **props)
    
    def triangle(self, id: Optional[str] = None, name: str = "triangle",
                 position: str = "center", **props) -> 'Entity':
        """Create a triangle in this dimension."""
        return self.materialize(kind="triangle", id=id, name=name, position=position, **props)
    
    def polygon(self, id: Optional[str] = None, name: str = "polygon",
                position: str = "center", sides: int = 6, **props) -> 'Entity':
        """Create a polygon in this dimension."""
        return self.materialize(kind="polygon", id=id, name=name, position=position, sides=sides, **props)
    
    def text(self, content: str, id: Optional[str] = None, name: str = "text",
             position: str = "center", **props) -> 'Entity':
        """Create text in this dimension."""
        return self.materialize(kind="text", id=id, name=name, position=position, content=content, **props)
    
    def point(self, id: Optional[str] = None, name: str = "point",
              position: str = "center", **props) -> 'Entity':
        """Create a point in this dimension."""
        return self.materialize(kind="point", id=id, name=name, position=position, **props)
    
    def line(self, id: Optional[str] = None, name: str = "line",
             start: str = "center", end: str = "right", **props) -> 'Entity':
        """Create a line in this dimension."""
        return self.materialize(kind="line", id=id, name=name, position=start, end=end, **props)
    
    def group(self, *entities, id: Optional[str] = None, name: str = "group",
              position: str = "center", **props) -> 'Entity':
        """Create a group containing entities."""
        grp = self.materialize(kind="group", id=id, name=name, position=position, **props)
        for entity in entities:
            entity.parent = grp
            grp.children.append(entity)
        return grp
    
    def invoke(self, identifier: str) -> Optional['Entity']:
        """
        Invoke an object by identity.
        
        Once invoked, drill without JOINs:
            engine = dim.invoke("VIN-123").drillDown("engine")
        """
        return by_id(identifier)
    
    def all(self) -> List['Entity']:
        """Get all entities in this dimension."""
        return list(self._space._entities.values())
    
    def query(self, **criteria) -> List['Entity']:
        """Find entities in this dimension matching criteria."""
        return query(dimension=self._name, **criteria)
    
    # =========================================================================
    # SHORTHAND NOTATIONS
    # =========================================================================
    
    def by_name(self, name: str) -> List['Entity']:
        """Shorthand: dimension.by_name("car")"""
        return [e for e in self.all() if e.name == name]
    
    def by_id(self, id: str) -> Optional['Entity']:
        """Shorthand: dimension.by_id("VIN-123")"""
        return self._space._entities.get(id)
    
    def by_kind(self, kind: str) -> List['Entity']:
        """Shorthand: dimension.by_kind("rectangle")"""
        return [e for e in self.all() if e.kind == kind]
    
    def __getattr__(self, name: str) -> Union['Entity', List['Entity']]:
        """
        Shorthand: dimension.car → all cars in dimension
        
        Example:
            physics = dimension("physics")
            physics.car      # All cars
            physics.engine   # All engines
        """
        # Avoid recursion for private attrs
        if name.startswith('_'):
            raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")
        
        # Try to find by name
        matches = self.by_name(name)
        if matches:
            return matches if len(matches) > 1 else matches[0]
        
        # Try to find by kind
        matches = self.by_kind(name)
        if matches:
            return matches if len(matches) > 1 else matches[0]
        
        raise AttributeError(f"No entities named or of kind '{name}' in dimension '{self._name}'")
    
    def __getitem__(self, key: str) -> Union['Entity', List['Entity']]:
        """
        Shorthand: dimension["car"] or dimension["VIN-123"]
        
        Example:
            physics["car"]        # All cars
            physics["VIN-123"]    # Specific car by id
        """
        # Try by id first
        entity = self.by_id(key)
        if entity:
            return entity
        
        # Then by name
        matches = self.by_name(key)
        if matches:
            return matches if len(matches) > 1 else matches[0]
        
        raise KeyError(f"No entity with id or name '{key}' in dimension '{self._name}'")


def dimension(name: str, width: float = 100.0, height: float = 100.0) -> Dimension:
    """Create a dimension where objects exist by virtue of geometry."""
    return Dimension(name, width, height)


# =============================================================================
# LAZY DATASTORE — External data only ingested when accessed
# =============================================================================

class Datastore:
    """
    Wrapper for external datastores (SQL, NoSQL, files, APIs).
    
    The ButterflyFX way:
    1. Register a datastore — we don't read it yet
    2. When you need data, we ingest it → becomes dimensional
    3. Next access uses dimensional lookup (no DB hit)
    4. We only check DB if value might have changed (dirty check)
    
    Instance vs Persisted:
    - Adding attribute to entity = instance-only (ephemeral)
    - Persist requires: write privileges + explicit persist() call
    """
    
    def __init__(
        self,
        name: str,
        fetch_fn: Callable[[str], Optional[Dict[str, Any]]],
        persist_fn: Optional[Callable[[str, Dict[str, Any]], bool]] = None,
        check_changed_fn: Optional[Callable[[str, Any], bool]] = None,
        writable: bool = False
    ):
        """
        Args:
            name: Datastore identifier
            fetch_fn: Function to fetch data by id from external source
            persist_fn: Function to write data back (requires writable=True)
            check_changed_fn: Function to check if external data changed
            writable: Whether this datastore allows writes
        """
        self._name = name
        self._fetch = fetch_fn
        self._persist = persist_fn
        self._check_changed = check_changed_fn
        self._writable = writable
        
        # Cache: id → (entity, version/timestamp)
        self._cache: Dict[str, Tuple['Entity', Any]] = {}
        
        # Instance attributes (not persisted)
        self._instance_attrs: Dict[str, Dict[str, Any]] = {}
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def writable(self) -> bool:
        return self._writable
    
    def get(self, id: str, space: Optional['Space'] = None) -> Optional['Entity']:
        """
        Get entity by id — lazy ingest from datastore.
        
        First access: fetch from external DB, ingest to dimension
        Subsequent: return from dimensional cache (no DB hit)
        """
        # Check cache first
        if id in self._cache:
            entity, version = self._cache[id]
            
            # Check if external data changed (if check function provided)
            if self._check_changed and self._check_changed(id, version):
                # Data changed — re-fetch
                pass
            else:
                # Return cached dimensional entity
                return entity
        
        # Fetch from external datastore
        data = self._fetch(id)
        if data is None:
            return None
        
        # Ingest into dimension — NOW it's dimensional
        if space is None:
            space = Space(name=f"{self._name}_space")
        
        # Create entity from fetched data
        entity = Entity(
            id=id,
            name=data.get('name', data.get('type', 'object')),
            kind=data.get('kind', 'rectangle'),
            space=space,
            x=data.get('x', 0.0),
            y=data.get('y', 0.0),
            props={k: v for k, v in data.items() 
                   if k not in ('id', 'name', 'kind', 'x', 'y', 'type')},
        )
        
        # Cache with version
        version = data.get('_version', data.get('updated_at', None))
        self._cache[id] = (entity, version)
        
        return entity
    
    def set_instance_attr(self, entity_id: str, attr: str, value: Any) -> None:
        """
        Set instance-only attribute (ephemeral, not persisted).
        
        This is the default behavior — adding attributes doesn't modify
        the external datastore.
        """
        if entity_id not in self._instance_attrs:
            self._instance_attrs[entity_id] = {}
        self._instance_attrs[entity_id][attr] = value
    
    def get_instance_attr(self, entity_id: str, attr: str) -> Optional[Any]:
        """Get instance-only attribute."""
        return self._instance_attrs.get(entity_id, {}).get(attr)
    
    def persist(self, entity: 'Entity') -> bool:
        """
        Persist entity changes to external datastore.
        
        Requires:
        1. Datastore is writable
        2. Persist function was provided
        
        Only persists if both conditions met.
        """
        if not self._writable:
            raise PermissionError(f"Datastore '{self._name}' is not writable")
        
        if self._persist is None:
            raise NotImplementedError(f"Datastore '{self._name}' has no persist function")
        
        # Merge instance attributes into props for persistence
        instance_attrs = self._instance_attrs.get(entity.id, {})
        data = entity.to_dict()
        data['props'].update(instance_attrs)
        
        # Persist to external store
        success = self._persist(entity.id, data)
        
        if success:
            # Clear instance attrs (now persisted)
            self._instance_attrs.pop(entity.id, None)
            # Update cache
            self._cache[entity.id] = (entity, data.get('_version'))
        
        return success
    
    def invalidate(self, id: str) -> None:
        """Invalidate cache for an id — force re-fetch next access."""
        self._cache.pop(id, None)
    
    def clear_cache(self) -> None:
        """Clear entire cache."""
        self._cache.clear()


# Global datastore registry
_datastores: Dict[str, Datastore] = {}


def register_datastore(
    name: str,
    fetch_fn: Callable[[str], Optional[Dict[str, Any]]],
    persist_fn: Optional[Callable[[str, Dict[str, Any]], bool]] = None,
    check_changed_fn: Optional[Callable[[str, Any], bool]] = None,
    writable: bool = False
) -> Datastore:
    """
    Register an external datastore.
    
    The datastore is not accessed until you need data from it.
    When accessed, data is ingested → becomes dimensional.
    Subsequent accesses use dimensional lookup (no DB hit).
    
    Args:
        name: Datastore name
        fetch_fn: Function(id) → dict or None
        persist_fn: Function(id, data) → bool (for writes)
        check_changed_fn: Function(id, version) → bool (for dirty checks)
        writable: Allow writes?
        
    Example:
        # Register a SQL datastore
        def fetch_car(vin):
            return db.query("SELECT * FROM cars WHERE vin = ?", vin)
        
        def persist_car(vin, data):
            return db.update("cars", vin, data)
        
        cars_db = register_datastore(
            "cars",
            fetch_fn=fetch_car,
            persist_fn=persist_car,
            writable=True
        )
        
        # First access — hits DB, ingests to dimension
        my_car = cars_db.get("VIN123")
        
        # Second access — dimensional lookup, no DB
        my_car = cars_db.get("VIN123")
        
        # Add instance attribute (not persisted)
        my_car.prop(temp_flag=True)
        
        # Persist if you have write privileges
        cars_db.persist(my_car)
    """
    ds = Datastore(name, fetch_fn, persist_fn, check_changed_fn, writable)
    _datastores[name] = ds
    return ds


def get_datastore(name: str) -> Optional[Datastore]:
    """Get registered datastore by name."""
    return _datastores.get(name)


# =============================================================================
# OPERATIONS DIMENSION — Functions as dimensional substrates
# =============================================================================

class Operation:
    """
    A function/operation as a dimensional entity.
    
    Operations exist in the same dimensional framework as data:
    - Have id, name, kind (just like any entity)
    - Can be looked up dimensionally
    - Can be invoked with arguments
    - Can drill to related operations
    """
    
    def __init__(
        self,
        id: str,
        name: str,
        fn: Callable,
        kind: str = "function",
        category: Optional[str] = None,
        description: str = "",
        **props
    ):
        self._id = id
        self._name = name
        self._fn = fn
        self._kind = kind
        self._category = category or "general"
        self._description = description
        self._props = props
        
        # Dimensional links to related operations
        self._children: List['Operation'] = []
        self._parent: Optional['Operation'] = None
        self._related: Dict[str, 'Operation'] = {}
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def kind(self) -> str:
        return self._kind
    
    @property
    def category(self) -> str:
        return self._category
    
    @property
    def description(self) -> str:
        return self._description
    
    def __call__(self, *args, **kwargs) -> Any:
        """Invoke the operation."""
        return self._fn(*args, **kwargs)
    
    def __repr__(self) -> str:
        return f"<operation:{self._name}>"
    
    def link(self, name: str, op: 'Operation') -> 'Operation':
        """Link to a related operation."""
        self._related[name] = op
        return self
    
    def child(self, op: 'Operation') -> 'Operation':
        """Add child operation."""
        op._parent = self
        self._children.append(op)
        return self
    
    def drillDown(self, name: Optional[str] = None) -> Optional['Operation']:
        """Navigate to child operation."""
        if name is None:
            return self._children[0] if self._children else None
        for child in self._children:
            if child.name == name:
                return child
        return None
    
    def drillUp(self) -> Optional['Operation']:
        """Navigate to parent operation."""
        return self._parent
    
    def drillAcross(self, name: str) -> Optional['Operation']:
        """Navigate to related operation."""
        return self._related.get(name)


class Operations:
    """
    The Operations dimension — functions as dimensional substrates.
    
    The ButterflyFX Way:
    - Operations ARE dimensional entities
    - Look them up by name, id, kind, category
    - Invoke them just like calling functions
    - Navigate between related operations dimensionally
    
    Usage:
        ops = Operations()
        
        # Register operations
        ops.register("sort", sorted, category="transform")
        ops.register("filter", filter, category="transform")
        ops.register("add", lambda a, b: a + b, category="math")
        
        # Look up by name
        sort_op = ops.by_name("sort")
        sort_op([3, 1, 2])  # → [1, 2, 3]
        
        # Direct attribute access
        ops.sort([3, 1, 2])  # → [1, 2, 3]
        
        # Look up by category
        math_ops = ops.by_category("math")
        
        # Look up by id
        specific_op = ops.by_id("sort_ascending")
    """
    
    def __init__(self, name: str = "operations"):
        self._name = name
        
        # Indices for multi-path lookup
        self._by_id: Dict[str, Operation] = {}
        self._by_name: Dict[str, List[Operation]] = {}
        self._by_kind: Dict[str, List[Operation]] = {}
        self._by_category: Dict[str, List[Operation]] = {}
    
    @property
    def name(self) -> str:
        return self._name
    
    def register(
        self,
        name: str,
        fn: Callable,
        id: Optional[str] = None,
        kind: str = "function",
        category: str = "general",
        description: str = "",
        **props
    ) -> Operation:
        """
        Register an operation in the dimension.
        
        Args:
            name: Operation name (e.g., "sort", "filter")
            fn: The callable function
            id: Unique id (defaults to name)
            kind: Operation type (function, method, transform, etc.)
            category: Category for grouping (math, transform, query, etc.)
            description: Human-readable description
            **props: Additional properties
            
        Returns:
            The registered Operation entity
        """
        op_id = id or name
        
        op = Operation(
            id=op_id,
            name=name,
            fn=fn,
            kind=kind,
            category=category,
            description=description,
            **props
        )
        
        # Index for multi-path lookup
        self._by_id[op_id] = op
        
        if name not in self._by_name:
            self._by_name[name] = []
        self._by_name[name].append(op)
        
        if kind not in self._by_kind:
            self._by_kind[kind] = []
        self._by_kind[kind].append(op)
        
        if category not in self._by_category:
            self._by_category[category] = []
        self._by_category[category].append(op)
        
        return op
    
    def by_id(self, id: str) -> Optional[Operation]:
        """Look up operation by unique id."""
        return self._by_id.get(id)
    
    def by_name(self, name: str) -> List[Operation]:
        """Look up operations by name."""
        return self._by_name.get(name, [])
    
    def by_kind(self, kind: str) -> List[Operation]:
        """Look up operations by kind."""
        return self._by_kind.get(kind, [])
    
    def by_category(self, category: str) -> List[Operation]:
        """Look up operations by category."""
        return self._by_category.get(category, [])
    
    def all(self) -> List[Operation]:
        """Get all registered operations."""
        return list(self._by_id.values())
    
    def __getattr__(self, name: str) -> Any:
        """
        Shorthand: ops.sort(...) → call the 'sort' operation.
        
        If operation exists, returns its invocation.
        """
        if name.startswith('_'):
            raise AttributeError(name)
        
        ops = self._by_name.get(name, [])
        if ops:
            # Return the operation (which is callable)
            return ops[0] if len(ops) == 1 else ops
        
        raise AttributeError(f"No operation named '{name}'")
    
    def __getitem__(self, key: str) -> Operation:
        """
        Shorthand: ops["sort"] → get operation by name or id.
        """
        # Try id first
        if key in self._by_id:
            return self._by_id[key]
        
        # Try name
        ops = self._by_name.get(key, [])
        if ops:
            return ops[0] if len(ops) == 1 else ops
        
        raise KeyError(f"No operation with id or name '{key}'")
    
    def __contains__(self, name: str) -> bool:
        """Check if operation exists."""
        return name in self._by_id or name in self._by_name
    
    def __iter__(self):
        """Iterate over all operations."""
        return iter(self._by_id.values())
    
    def __len__(self) -> int:
        """Number of registered operations."""
        return len(self._by_id)


# Global operations dimension (pre-populated with common operations)
_operations = Operations("global")


def operations() -> Operations:
    """Get the global operations dimension."""
    return _operations


def operation(
    name_or_fn: Union[str, Callable, None] = None,
    fn: Optional[Callable] = None,
    id: Optional[str] = None,
    kind: str = "function",
    category: str = "general",
    description: str = "",
    **props
) -> Union[Operation, Callable[[Callable], Operation]]:
    """
    Register an operation in the global operations dimension.
    
    Can be used as:
        # As decorator without args — uses function name
        @operation
        def square(x):
            return x * x
        
        # As decorator with args
        @operation("sq", category="math")
        def square(x):
            return x * x
        
        # Direct call
        operation("square", lambda x: x * x, category="math")
        
        # Now accessible as:
        operations().square(5)  # → 25
        operations().by_name("square")
    """
    # Case 1: @operation without args — name_or_fn is the function
    if callable(name_or_fn) and fn is None:
        fn = name_or_fn
        name = fn.__name__
        return _operations.register(name, fn, id, kind, category, description, **props)
    
    # Case 2: @operation("name", ...) — returns decorator
    if name_or_fn is None or isinstance(name_or_fn, str):
        name = name_or_fn
        
        # If fn provided directly, register now
        if fn is not None:
            return _operations.register(name or fn.__name__, fn, id, kind, category, description, **props)
        
        # Return decorator
        def decorator(func: Callable) -> Operation:
            op_name = name or func.__name__
            return _operations.register(op_name, func, id, kind, category, description, **props)
        return decorator
    
    raise TypeError("operation() expects a string name or callable")


# Register common built-in operations
def _register_builtins():
    """Register common operations."""
    import math
    
    # Math operations
    _operations.register("add", lambda a, b: a + b, category="math", description="Add two values")
    _operations.register("subtract", lambda a, b: a - b, category="math", description="Subtract b from a")
    _operations.register("multiply", lambda a, b: a * b, category="math", description="Multiply two values")
    _operations.register("divide", lambda a, b: a / b if b != 0 else float('inf'), category="math", description="Divide a by b")
    _operations.register("sqrt", math.sqrt, category="math", description="Square root")
    _operations.register("pow", pow, category="math", description="Power")
    _operations.register("abs", abs, category="math", description="Absolute value")
    
    # Transform operations
    _operations.register("sort", sorted, category="transform", description="Sort a sequence")
    _operations.register("reverse", lambda x: list(reversed(x)), category="transform", description="Reverse a sequence")
    _operations.register("unique", lambda x: list(set(x)), category="transform", description="Get unique values")
    
    # Query operations
    _operations.register("count", len, category="query", description="Count items")
    _operations.register("first", lambda x: x[0] if x else None, category="query", description="Get first item")
    _operations.register("last", lambda x: x[-1] if x else None, category="query", description="Get last item")
    _operations.register("sum", sum, category="query", description="Sum values")
    _operations.register("min", min, category="query", description="Get minimum")
    _operations.register("max", max, category="query", description="Get maximum")


# Initialize built-in operations
_register_builtins()


def _resolve_position(pos: Union[str, Position, Tuple[float, float]]) -> Tuple[float, float]:
    """Resolve a semantic position to coordinates."""
    if isinstance(pos, tuple):
        return pos
    if isinstance(pos, Position):
        pos = pos.name.lower().replace('_', '-')
    return POSITION_TO_COORDS.get(pos.lower().replace('_', '-'), (0.5, 0.5))


def _resolve_orientation(orient: Union[str, Orientation, float]) -> float:
    """Resolve a semantic orientation to angle in radians."""
    if isinstance(orient, (int, float)):
        return float(orient)
    if isinstance(orient, Orientation):
        orient = orient.name.lower().replace('_', '-')
    return ORIENTATION_TO_ANGLE.get(orient.lower().replace('_', '-'), 0.0)


def _resolve_direction(direction: Union[str, Direction]) -> Tuple[float, float]:
    """Resolve a semantic direction to unit vector."""
    if isinstance(direction, Direction):
        direction = direction.name.lower().replace('_', '-')
    return DIRECTION_TO_VECTOR.get(direction.lower().replace('_', '-'), (0.0, 0.0))


def _resolve_size(size: Union[str, Size, float]) -> float:
    """Resolve a semantic size to normalized value."""
    if isinstance(size, (int, float)):
        return float(size)
    if isinstance(size, Size):
        size = size.name.lower()
    return SIZE_TO_VALUE.get(size.lower(), 0.2)


def _resolve_anchor(anchor: Union[str, Anchor]) -> Tuple[float, float]:
    """Resolve a semantic anchor to offset."""
    if isinstance(anchor, Anchor):
        anchor = anchor.name.lower().replace('_', '-')
    return ANCHOR_TO_OFFSET.get(anchor.lower().replace('_', '-'), (0.5, 0.5))


def _resolve_relation(rel: Union[str, Relation]) -> Tuple[float, float, bool]:
    """Resolve a semantic relation to offset."""
    if isinstance(rel, Relation):
        rel = rel.name.lower().replace('_', '-')
    return RELATION_TO_OFFSET.get(rel.lower().replace('_', '-'), (0.0, 0.0, False))


# =============================================================================
# SPACE — The canvas/container
# =============================================================================

class Space:
    """
    A dimensional space for placing entities.
    
    Under the hood, this is a Substrate2D with z = xy.
    Human positions map to substrate coordinates.
    """
    
    def __init__(
        self,
        width: float = 100.0,
        height: float = 100.0,
        name: str = "space"
    ):
        self._name = name
        self._width = width
        self._height = height
        self._substrate = Substrate2D(name=name)
        self._entities: Dict[str, 'Entity'] = {}
        # Auto-register as a dimension (can be looked up by name)
        register_dimension(self, name=name)
    
    @property
    def width(self) -> float:
        return self._width
    
    @property
    def height(self) -> float:
        return self._height
    
    @property
    def substrate(self) -> Substrate2D:
        """Access underlying substrate."""
        return self._substrate
    
    def _to_substrate_coords(self, x_norm: float, y_norm: float) -> Tuple[float, float]:
        """Convert normalized (0-1) coordinates to substrate coordinates."""
        return (x_norm * self._width, y_norm * self._height)
    
    def shape(
        self,
        kind: str,
        width: Union[str, float] = "medium",
        height: Union[str, float] = "medium",
        size: Optional[Union[str, float]] = None,
        **props
    ) -> 'ShapeBuilder':
        """
        Create a shape with human-friendly sizing.
        
        Args:
            kind: "rectangle", "circle", "triangle", etc.
            width: Semantic ("small", "medium") or numeric
            height: Semantic or numeric
            size: If provided, sets both width and height
        """
        if size is not None:
            width = height = size
        return ShapeBuilder(self, kind, width, height, **props)
    
    def text(self, content: str, **props) -> 'TextBuilder':
        """Create text with semantic styling."""
        return TextBuilder(self, content, **props)
    
    def point(self, name: Optional[str] = None) -> 'PointBuilder':
        """Create a point."""
        return PointBuilder(self, name)
    
    def line(self) -> 'LineBuilder':
        """Create a line."""
        return LineBuilder(self)
    
    def group(self, *entities: 'Entity', name: Optional[str] = None) -> 'GroupBuilder':
        """Group entities together."""
        return GroupBuilder(self, list(entities), name)
    
    def add(self, entity: 'Entity') -> 'Entity':
        """Add entity to space."""
        self._entities[entity.id] = entity
        return entity
    
    def find(self, name: str) -> Optional['Entity']:
        """Find entity by name."""
        for eid, ent in self._entities.items():
            if ent.name == name:
                return ent
        return None
    
    def all(self) -> List['Entity']:
        """Get all entities."""
        return list(self._entities.values())


def space(width: float = 100, height: float = 100, name: str = "space") -> Space:
    """Create a dimensional space."""
    return Space(width, height, name)


# =============================================================================
# ENTITY — The base for all entities
# =============================================================================

@dataclass
class Entity:
    """
    An entity in dimensional space.
    
    Fields:
        id: Unique identity - index, UUID, VIN, or any unique identifier.
            THIS IS THE PRIMARY LOOKUP KEY. One particular car is identified
            by its VIN, not by the fact that it's a "car".
        name: The object type/class name (e.g., "car", "engine", "piston").
            This is WHAT the object is, not WHICH specific one.
        kind: Shape/visual kind - "rectangle", "circle", "text", etc.
    
    Example:
        Entity(id="VIN123", name="car", kind="rectangle")
        - id="VIN123" → identifies THIS SPECIFIC car
        - name="car" → this is a car object
        - kind="rectangle" → rendered as rectangle
    
    Identity-First Access:
        my_car = by_identity("VIN123")          # Find by unique ID
        engine = my_car.drillDown("engine")     # Navigate to child
        hp = engine.select("horsepower")        # Get specific property
        
    Dimensional Drilling:
        - drillDown(part): Navigate to child/component
        - drillUp(): Navigate to parent/container
        - drillAcross(sibling): Navigate to sibling at same level
        - select(*props): Get specific properties after navigation
    """
    id: str                    # Unique identity: index, UUID, VIN, etc.
    name: str                  # Object type/class: "car", "engine", etc.
    kind: str                  # Visual kind: "rectangle", "circle", etc.
    space: Space
    
    # Substrate position (resolved from semantic positions)
    x: float = 0.0
    y: float = 0.0
    
    # Dimensions
    width: float = 0.2
    height: float = 0.2
    
    # Orientation (resolved from semantic orientations)
    angle: float = 0.0
    
    # Anchor point
    anchor_x: float = 0.5
    anchor_y: float = 0.5
    
    # Level
    level: int = 0
    
    # Identity — any unique identifier for this specific entity
    _identities: Dict[str, Any] = field(default_factory=dict)
    
    # Custom properties
    props: Dict[str, Any] = field(default_factory=dict)
    
    # Relationships
    parent: Optional['Entity'] = None
    children: List['Entity'] = field(default_factory=list)
    
    # Internal
    _interface: Optional[Interface] = None
    
    def __post_init__(self):
        # Ingest into substrate
        if self.space:
            self._interface = self.space.substrate.ingest(self.name, x=self.x, y=self.y)
            self.space.add(self)
        # Auto-register by id for identity lookup
        register_identity(self, self.id, "id")
        # Register in multi-path indices (name, kind, attributes)
        _register_entity_indices(self)
    
    # =========================================================================
    # DERIVED GEOMETRIC PROPERTIES — from substrate
    # =========================================================================
    
    @property
    def z(self) -> float:
        """Z value - DERIVED from manifold: z = x * y."""
        return self.x * self.y
    
    @property
    def slope(self) -> float:
        """Slope at position - DERIVED."""
        return self.y
    
    @property
    def curvature(self) -> float:
        """Curvature at position - DERIVED."""
        denom = 1 + self.x**2 + self.y**2
        return -1 / (denom * denom)
    
    @property
    def theta(self) -> float:
        """θ at current level - DERIVED."""
        level_angles = {0: 0.0, 1: math.pi/6, 2: math.pi/3, 3: math.pi/2,
                        4: 2*math.pi/3, 5: 5*math.pi/6, 6: math.pi}
        return level_angles.get(self.level, 0.0)
    
    @property
    def distance_from_center(self) -> float:
        """Distance from center - DERIVED."""
        cx, cy = self.space.width / 2, self.space.height / 2
        return math.sqrt((self.x - cx)**2 + (self.y - cy)**2)
    
    @property
    def sin(self) -> float:
        """sin(angle) - DERIVED."""
        return math.sin(self.angle)
    
    @property
    def cos(self) -> float:
        """cos(angle) - DERIVED."""
        return math.cos(self.angle)
    
    # =========================================================================
    # HUMAN-FRIENDLY METHODS
    # =========================================================================
    
    def place(self, position: Union[str, Position, Tuple[float, float]]) -> 'Entity':
        """
        Place entity at a semantic position.
        
        Args:
            position: "center", "top-left", etc. or (x, y) tuple
        """
        x_norm, y_norm = _resolve_position(position)
        self.x, self.y = self.space._to_substrate_coords(x_norm, y_norm)
        return self
    
    def orient(self, orientation: Union[str, Orientation, float]) -> 'Entity':
        """
        Orient entity using semantic orientation.
        
        Args:
            orientation: "landscape", "portrait", "facing-right", etc.
        """
        self.angle = _resolve_orientation(orientation)
        return self
    
    def anchor(self, point: Union[str, Anchor]) -> 'Entity':
        """
        Set anchor point using semantic name.
        
        Args:
            point: "center", "top-left", "bottom", etc.
        """
        self.anchor_x, self.anchor_y = _resolve_anchor(point)
        return self
    
    def attachTo(
        self,
        target: 'Entity',
        relation: Union[str, Relation],
        margin: Union[str, float] = 0,
        offset: Union[str, float] = 0
    ) -> 'Entity':
        """
        Attach to another entity with semantic relationship.
        
        Args:
            target: Entity to attach to
            relation: "above", "below", "top-inside", "top-right-outside", etc.
            margin: Gap between entities ("small", "medium", etc.)
            offset: Additional offset
        """
        dx, dy, inside = _resolve_relation(relation)
        margin_val = _resolve_size(margin) if isinstance(margin, str) else margin
        offset_val = _resolve_size(offset) if isinstance(offset, str) else offset
        
        if inside:
            # Position inside target
            self.x = target.x + dx * target.width * 0.5
            self.y = target.y + dy * target.height * 0.5
        else:
            # Position outside target
            self.x = target.x + dx * (target.width * 0.5 + self.width * 0.5 + margin_val * self.space.width)
            self.y = target.y + dy * (target.height * 0.5 + self.height * 0.5 + margin_val * self.space.height)
        
        # Apply offset
        self.x += offset_val * dx
        self.y += offset_val * dy
        
        self.parent = target
        target.children.append(self)
        return self
    
    def placeRelativeTo(
        self,
        target: 'Entity',
        relation: Union[str, Relation],
        gap: Union[str, float] = "small"
    ) -> 'Entity':
        """Alias for attachTo with simpler naming."""
        return self.attachTo(target, relation, margin=gap)
    
    def align(self, direction: Union[str, Direction]) -> 'Entity':
        """
        Align entity in a direction.
        
        For text, this affects text alignment.
        For shapes, this affects anchor point.
        """
        dx, dy = _resolve_direction(direction)
        self.anchor_x = 0.5 + dx * 0.5
        self.anchor_y = 0.5 + dy * 0.5
        return self
    
    def size(
        self,
        width: Optional[Union[str, float]] = None,
        height: Optional[Union[str, float]] = None
    ) -> 'Entity':
        """Set size using semantic names or absolute values."""
        if width is not None:
            if isinstance(width, (int, float)) and width > 1:
                self.width = float(width)
            else:
                self.width = _resolve_size(width) * self.space.width
        if height is not None:
            if isinstance(height, (int, float)) and height > 1:
                self.height = float(height)
            else:
                self.height = _resolve_size(height) * self.space.height
        return self
    
    def move(
        self,
        direction: Union[str, Direction],
        distance: Union[str, float] = "small"
    ) -> 'Entity':
        """Move in a direction."""
        dx, dy = _resolve_direction(direction)
        dist = _resolve_size(distance) * min(self.space.width, self.space.height)
        self.x += dx * dist
        self.y += dy * dist
        return self
    
    def rotateTo(self, target: str) -> 'Entity':
        """Rotate to face a direction."""
        return self.orient(target)
    
    def rotateBy(self, amount: str) -> 'Entity':
        """
        Rotate by a semantic amount.
        
        Args:
            amount: "quarter-turn", "half-turn", "eighth-turn",
                    "clockwise", "counter-clockwise"
        """
        turns = {
            'quarter-turn': math.pi / 2,
            'quarter-turn-clockwise': -math.pi / 2,
            'quarter-turn-counter-clockwise': math.pi / 2,
            'half-turn': math.pi,
            'eighth-turn': math.pi / 4,
            'clockwise': -math.pi / 2,
            'counter-clockwise': math.pi / 2,
            'full-turn': 2 * math.pi,
        }
        self.angle += turns.get(amount.lower().replace('_', '-'), 0.0)
        return self
    
    def snapTo(self, constraint: str) -> 'Entity':
        """
        Snap to a geometric constraint.
        
        Args:
            constraint: "golden-angle", "grid", "diagonal", etc.
        """
        constraints = {
            'golden-angle': 2.39996,  # Golden angle in radians
            'diagonal': math.pi / 4,
            'horizontal': 0.0,
            'vertical': math.pi / 2,
        }
        if constraint.lower().replace('_', '-') in constraints:
            self.angle = constraints[constraint.lower().replace('_', '-')]
        return self
    
    def at_level(self, level: int) -> 'Entity':
        """Jump to level in O(1)."""
        self.level = level
        return self
    
    def label(self, text: str) -> 'Entity':
        """Add a label."""
        self.props['label'] = text
        return self
    
    def prop(self, **kwargs) -> 'Entity':
        """Set properties."""
        self.props.update(kwargs)
        return self
    
    # =========================================================================
    # IDENTITY SYSTEM — Unique identification
    # =========================================================================
    
    def identify(self, **identities) -> 'Entity':
        """
        Set unique identity for this entity.
        
        Identity is ANY information completely unique to this specific object.
        A model of a car is not unique, but ONE particular car (identified
        by VIN) is unique.
        
        Args:
            **identities: Key-value pairs of identity types and values
                          e.g., vin="1HGBH41JXMN109186", serial="ABC123"
                          
        Returns:
            Self for chaining
            
        Example:
            car = canvas.shape("car").identify(vin="1HGBH41JXMN109186").done()
            
            # Later retrieve:
            my_car = by_identity("1HGBH41JXMN109186", "vin")
        """
        for id_type, id_value in identities.items():
            self._identities[id_type.lower()] = id_value
            register_identity(self, id_value, id_type)
        return self
    
    def get_identity(self, identity_type: str = "id") -> Optional[Any]:
        """Get the identity value for a given type."""
        return self._identities.get(identity_type.lower())
    
    @property
    def identities(self) -> Dict[str, Any]:
        """Get all identities for this entity."""
        return self._identities.copy()
    
    # =========================================================================
    # DIMENSIONAL DRILLING — Navigate up/down/across
    # =========================================================================
    
    def drillDown(self, part_name: str) -> Optional['Entity']:
        """
        Drill down dimensionally to a child component.
        
        Args:
            part_name: Name or kind of child to navigate to
            
        Returns:
            The child entity if found, None otherwise
            
        Example:
            car = by_identity("VIN123", "vin")
            engine = car.drillDown("engine")
            piston = engine.drillDown("piston1")
        """
        for child in self.children:
            if child.name == part_name or child.kind == part_name:
                return child
        return None
    
    def drillUp(self) -> Optional['Entity']:
        """
        Drill up dimensionally to the parent.
        
        Returns:
            The parent entity if exists, None otherwise
            
        Example:
            piston = by_identity("PISTON123", "id")
            engine = piston.drillUp()
            car = engine.drillUp()
        """
        return self.parent
    
    def drillAcross(self, sibling_name: str) -> Optional['Entity']:
        """
        Drill across to a sibling at the same dimensional level.
        
        Args:
            sibling_name: Name or kind of sibling
            
        Returns:
            The sibling entity if found, None otherwise
            
        Example:
            engine = by_identity("ENGINE123", "id")
            transmission = engine.drillAcross("transmission")
        """
        if self.parent is None:
            return None
        
        for sibling in self.parent.children:
            if sibling is not self:
                if sibling.name == sibling_name or sibling.kind == sibling_name:
                    return sibling
        return None
    
    def select(self, *properties: str) -> Dict[str, Any]:
        """
        Select specific properties from this entity.
        
        After bringing up an entity by identity, if you only need
        specific parts, use select to get just those.
        
        Args:
            *properties: Property names to retrieve
            
        Returns:
            Dict with requested property values
            
        Example:
            car = by_identity("VIN123", "vin")
            engine = car.drillDown("engine")
            specs = engine.select("horsepower", "torque", "cylinders")
        """
        result = {}
        for prop in properties:
            # Derived geometric properties
            if prop in ('z', 'slope', 'curvature', 'theta', 'sin', 'cos', 'distance_from_center'):
                result[prop] = getattr(self, prop)
            # Core fields
            elif prop in ('x', 'y', 'width', 'height', 'angle', 'level', 'name', 'kind', 'id'):
                result[prop] = getattr(self, prop)
            # Custom properties
            elif prop in self.props:
                result[prop] = self.props[prop]
            # Identities
            elif prop in self._identities:
                result[prop] = self._identities[prop]
        return result
    
    def all_data(self) -> Dict[str, Any]:
        """Get ALL information about this entity."""
        return self.to_dict()
    
    # =========================================================================
    # OUTPUT
    # =========================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Export as dict with both human-friendly and computed values."""
        return {
            'id': self.id,
            'name': self.name,
            'kind': self.kind,
            'identities': self._identities,
            'position': {
                'x': self.x,
                'y': self.y,
                'normalized': (self.x / self.space.width, self.y / self.space.height),
            },
            'size': {
                'width': self.width,
                'height': self.height,
            },
            'orientation': {
                'angle': self.angle,
                'degrees': math.degrees(self.angle),
            },
            'anchor': {
                'x': self.anchor_x,
                'y': self.anchor_y,
            },
            'geometry': {
                'z': self.z,
                'slope': self.slope,
                'curvature': self.curvature,
                'theta': self.theta,
                'sin': self.sin,
                'cos': self.cos,
            },
            'level': self.level,
            'props': self.props,
            'parent': self.parent.id if self.parent else None,
            'children': [c.id for c in self.children],
        }
    
    def __repr__(self) -> str:
        return f"<{self.kind}:{self.name} at ({self.x:.1f}, {self.y:.1f})>"
    
    def __hash__(self) -> int:
        """Hash by id - entities are uniquely identified."""
        return hash(self.id)
    
    def __eq__(self, other: object) -> bool:
        """Equality by id."""
        if not isinstance(other, Entity):
            return False
        return self.id == other.id


# =============================================================================
# BUILDERS — Fluent API for creating entities
# =============================================================================

_entity_counter = 0

def _next_id() -> str:
    global _entity_counter
    _entity_counter += 1
    return f"entity_{_entity_counter}"


class ShapeBuilder:
    """Fluent builder for shapes."""
    
    def __init__(
        self,
        space: Space,
        kind: str,
        width: Union[str, float],
        height: Union[str, float],
        **props
    ):
        self._space = space
        self._kind = kind
        # If numeric > 1, treat as absolute. Otherwise resolve as proportion.
        if isinstance(width, (int, float)) and width > 1:
            self._width = float(width)
        else:
            self._width = _resolve_size(width) * space.width
        if isinstance(height, (int, float)) and height > 1:
            self._height = float(height)
        else:
            self._height = _resolve_size(height) * space.height
        self._props = props
        # Extract id and name from props, auto-generate if not provided
        self._id = props.pop('id', None)  # Will use _next_id() in build() if None
        self._name = props.pop('name', f"{kind}")
        
        # Defaults
        self._x = 0.0
        self._y = 0.0
        self._angle = 0.0
        self._anchor_x = 0.5
        self._anchor_y = 0.5
        self._parent: Optional[Entity] = None
        self._relation: Optional[str] = None
        self._margin = 0.0
    
    def place(self, position: Union[str, Position, Tuple[float, float]]) -> 'ShapeBuilder':
        """Place at semantic position."""
        x_norm, y_norm = _resolve_position(position)
        self._x, self._y = self._space._to_substrate_coords(x_norm, y_norm)
        return self
    
    def orient(self, orientation: Union[str, Orientation, float]) -> 'ShapeBuilder':
        """Set orientation."""
        self._angle = _resolve_orientation(orientation)
        return self
    
    def anchor(self, point: Union[str, Anchor]) -> 'ShapeBuilder':
        """Set anchor point."""
        self._anchor_x, self._anchor_y = _resolve_anchor(point)
        return self
    
    def attachTo(
        self,
        target: Entity,
        relation: Union[str, Relation],
        margin: Union[str, float] = 0,
        offset: Union[str, float] = 0
    ) -> 'ShapeBuilder':
        """Attach to another entity."""
        self._parent = target
        self._relation = relation
        self._margin = _resolve_size(margin) if isinstance(margin, str) else margin
        
        dx, dy, inside = _resolve_relation(relation)
        if inside:
            self._x = target.x + dx * target.width * 0.5
            self._y = target.y + dy * target.height * 0.5
        else:
            self._x = target.x + dx * (target.width * 0.5 + self._width * 0.5 + self._margin * self._space.width)
            self._y = target.y + dy * (target.height * 0.5 + self._height * 0.5 + self._margin * self._space.height)
        return self
    
    def size(
        self,
        width: Optional[Union[str, float]] = None,
        height: Optional[Union[str, float]] = None
    ) -> 'ShapeBuilder':
        """Set size."""
        if width is not None:
            if isinstance(width, (int, float)) and width > 1:
                self._width = float(width)
            else:
                self._width = _resolve_size(width) * self._space.width
        if height is not None:
            if isinstance(height, (int, float)) and height > 1:
                self._height = float(height)
            else:
                self._height = _resolve_size(height) * self._space.height
        return self
    
    def label(self, text: str) -> 'ShapeBuilder':
        """Add label."""
        self._props['label'] = text
        return self
    
    def name(self, n: str) -> 'ShapeBuilder':
        """Set name (object type: car, engine, etc.)."""
        self._name = n
        return self
    
    def id(self, id_value: str) -> 'ShapeBuilder':
        """Set unique ID (VIN, UUID, index, etc.)."""
        self._id = id_value
        return self
    
    def prop(self, **kwargs) -> 'ShapeBuilder':
        """Set properties."""
        self._props.update(kwargs)
        return self
    
    def identify(self, **identities) -> 'ShapeBuilder':
        """
        Set unique identity for this entity.
        
        Args:
            **identities: Identity type-value pairs (e.g., vin="ABC123")
        """
        if not hasattr(self, '_identities'):
            self._identities = {}
        self._identities.update({k.lower(): v for k, v in identities.items()})
        return self
    
    def build(self) -> Entity:
        """Build the entity."""
        entity = Entity(
            id=self._id if self._id else _next_id(),
            name=self._name,
            kind=self._kind,
            space=self._space,
            x=self._x,
            y=self._y,
            width=self._width,
            height=self._height,
            angle=self._angle,
            anchor_x=self._anchor_x,
            anchor_y=self._anchor_y,
            props=self._props,
            parent=self._parent,
        )
        if self._parent:
            self._parent.children.append(entity)
        # Apply identities
        if hasattr(self, '_identities'):
            entity.identify(**self._identities)
        return entity
    
    def done(self) -> Entity:
        """Alias for build() - finalize and return entity."""
        return self.build()
    
    # Allow implicit build
    def __getattr__(self, name: str):
        # Build implicitly when accessing entity methods
        if name in ['x', 'y', 'z', 'slope', 'curvature', 'to_dict']:
            return getattr(self.build(), name)
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")


class TextBuilder:
    """Fluent builder for text."""
    
    def __init__(self, space: Space, content: str, **props):
        self._space = space
        self._content = content
        self._props = props
        self._name = props.pop('name', f"text_{_next_id()}")
        
        self._x = 0.0
        self._y = 0.0
        self._angle = 0.0
        self._anchor_x = 0.5
        self._anchor_y = 0.5
        self._parent: Optional[Entity] = None
        self._font_size = "medium"
    
    def place(self, position: Union[str, Position, Tuple[float, float]]) -> 'TextBuilder':
        """Place at semantic position."""
        x_norm, y_norm = _resolve_position(position)
        self._x, self._y = self._space._to_substrate_coords(x_norm, y_norm)
        return self
    
    def attachTo(
        self,
        target: Entity,
        relation: Union[str, Relation],
        margin: Union[str, float] = 0
    ) -> 'TextBuilder':
        """Attach to another entity."""
        self._parent = target
        dx, dy, inside = _resolve_relation(relation)
        margin_val = _resolve_size(margin) if isinstance(margin, str) else margin
        
        if inside:
            self._x = target.x + dx * target.width * 0.4
            self._y = target.y + dy * target.height * 0.4
        else:
            self._x = target.x + dx * (target.width * 0.5 + margin_val * self._space.width)
            self._y = target.y + dy * (target.height * 0.5 + margin_val * self._space.height)
        return self
    
    def align(self, direction: str) -> 'TextBuilder':
        """Align text."""
        self._props['textAlign'] = direction
        return self
    
    def fontSize(self, size: str) -> 'TextBuilder':
        """Set font size."""
        self._font_size = size
        return self
    
    def prop(self, **kwargs) -> 'TextBuilder':
        """Set properties."""
        self._props.update(kwargs)
        return self
    
    def build(self) -> Entity:
        """Build the text entity."""
        self._props['content'] = self._content
        self._props['fontSize'] = self._font_size
        
        # Estimate size based on content
        size_mult = SIZE_TO_VALUE.get(self._font_size, 0.2)
        width = len(self._content) * size_mult * 2
        height = size_mult * 3
        
        entity = Entity(
            id=_next_id(),
            name=self._name,
            kind="text",
            space=self._space,
            x=self._x,
            y=self._y,
            width=width,
            height=height,
            angle=self._angle,
            anchor_x=self._anchor_x,
            anchor_y=self._anchor_y,
            props=self._props,
            parent=self._parent,
        )
        if self._parent:
            self._parent.children.append(entity)
        return entity
    
    def done(self) -> Entity:
        """Alias for build() - finalize and return entity."""
        return self.build()


class PointBuilder:
    """Fluent builder for points."""
    
    def __init__(self, space: Space, name: Optional[str] = None):
        self._space = space
        self._name = name or f"point_{_next_id()}"
        self._x = 0.0
        self._y = 0.0
        self._props: Dict[str, Any] = {}
    
    def at(self, position: Union[str, Position, Tuple[float, float]]) -> 'PointBuilder':
        """Place at position."""
        if isinstance(position, tuple):
            self._x, self._y = position
        else:
            x_norm, y_norm = _resolve_position(position)
            self._x, self._y = self._space._to_substrate_coords(x_norm, y_norm)
        return self
    
    def build(self) -> Entity:
        """Build point entity."""
        return Entity(
            id=_next_id(),
            name=self._name,
            kind="point",
            space=self._space,
            x=self._x,
            y=self._y,
            width=0.01,
            height=0.01,
            props=self._props,
        )
    
    def done(self) -> Entity:
        """Alias for build() - finalize and return entity."""
        return self.build()


class LineBuilder:
    """Fluent builder for lines."""
    
    def __init__(self, space: Space):
        self._space = space
        self._name = f"line_{_next_id()}"
        self._from_x = 0.0
        self._from_y = 0.0
        self._to_x = 0.0
        self._to_y = 0.0
        self._props: Dict[str, Any] = {}
    
    def start(self, position: Union[str, Position, Tuple[float, float], Entity]) -> 'LineBuilder':
        """Set start point."""
        if isinstance(position, Entity):
            self._from_x, self._from_y = position.x, position.y
        elif isinstance(position, tuple):
            self._from_x, self._from_y = position
        else:
            x_norm, y_norm = _resolve_position(position)
            self._from_x, self._from_y = self._space._to_substrate_coords(x_norm, y_norm)
        return self
    
    # Alias
    from_ = start
    
    def end(self, position: Union[str, Position, Tuple[float, float], Entity]) -> 'LineBuilder':
        """Set end point."""
        if isinstance(position, Entity):
            self._to_x, self._to_y = position.x, position.y
        elif isinstance(position, tuple):
            self._to_x, self._to_y = position
        else:
            x_norm, y_norm = _resolve_position(position)
            self._to_x, self._to_y = self._space._to_substrate_coords(x_norm, y_norm)
        return self
    
    # Alias
    to = end
    
    def build(self) -> Entity:
        """Build line entity."""
        self._props['from'] = (self._from_x, self._from_y)
        self._props['to'] = (self._to_x, self._to_y)
        
        # Calculate center and dimensions
        cx = (self._from_x + self._to_x) / 2
        cy = (self._from_y + self._to_y) / 2
        dx = self._to_x - self._from_x
        dy = self._to_y - self._from_y
        length = math.sqrt(dx*dx + dy*dy)
        angle = math.atan2(dy, dx)
        
        return Entity(
            id=_next_id(),
            name=self._name,
            kind="line",
            space=self._space,
            x=cx,
            y=cy,
            width=length,
            height=0.01,
            angle=angle,
            props=self._props,
        )
    
    def done(self) -> Entity:
        """Alias for build() - finalize and return entity."""
        return self.build()
    
    def fromPoint(self, position: Union[str, Position, Tuple[float, float], Entity]) -> 'LineBuilder':
        """Alias for start()."""
        return self.start(position)
    
    def toPoint(self, position: Union[str, Position, Tuple[float, float], Entity]) -> 'LineBuilder':
        """Alias for end()."""
        return self.end(position)


class GroupBuilder:
    """Fluent builder for groups."""
    
    def __init__(self, space: Space, entities: List[Entity], name: Optional[str] = None):
        self._space = space
        self._entities = entities
        self._name = name or f"group_{_next_id()}"
        self._props: Dict[str, Any] = {}
    
    def add(self, entity: Entity) -> 'GroupBuilder':
        """Add entity to group."""
        self._entities.append(entity)
        return self
    
    def build(self) -> Entity:
        """Build group entity."""
        if not self._entities:
            return Entity(
                id=_next_id(),
                name=self._name,
                kind="group",
                space=self._space,
            )
        
        # Calculate bounding box
        min_x = min(e.x - e.width/2 for e in self._entities)
        max_x = max(e.x + e.width/2 for e in self._entities)
        min_y = min(e.y - e.height/2 for e in self._entities)
        max_y = max(e.y + e.height/2 for e in self._entities)
        
        group = Entity(
            id=_next_id(),
            name=self._name,
            kind="group",
            space=self._space,
            x=(min_x + max_x) / 2,
            y=(min_y + max_y) / 2,
            width=max_x - min_x,
            height=max_y - min_y,
            props=self._props,
            children=self._entities,
        )
        
        for e in self._entities:
            e.parent = group
        
        return group
    
    def done(self) -> Entity:
        """Alias for build() - finalize and return entity."""
        return self.build()


# =============================================================================
# CONVENIENCE FUNCTIONS — Top-level shape creators
# =============================================================================

_global_space: Optional[Space] = None

def _get_space() -> Space:
    """Get or create global space."""
    global _global_space
    if _global_space is None:
        _global_space = Space()
    return _global_space


def shape(kind: str, **kwargs) -> ShapeBuilder:
    """Create a shape in the global space."""
    return _get_space().shape(kind, **kwargs)


def rectangle(**kwargs) -> ShapeBuilder:
    """Create a rectangle."""
    return shape("rectangle", **kwargs)


def circle(**kwargs) -> ShapeBuilder:
    """Create a circle."""
    if 'size' in kwargs:
        kwargs['width'] = kwargs['height'] = kwargs.pop('size')
    return shape("circle", **kwargs)


def triangle(**kwargs) -> ShapeBuilder:
    """Create a triangle."""
    return shape("triangle", **kwargs)


def polygon(sides: int = 6, **kwargs) -> ShapeBuilder:
    """Create a polygon."""
    kwargs['sides'] = sides
    return shape("polygon", **kwargs)


def text(content: str, **kwargs) -> TextBuilder:
    """Create text in the global space."""
    return _get_space().text(content, **kwargs)


def point(name: Optional[str] = None) -> PointBuilder:
    """Create a point in the global space."""
    return _get_space().point(name)


def line() -> LineBuilder:
    """Create a line in the global space."""
    return _get_space().line()


def group(*entities: Entity, name: Optional[str] = None) -> GroupBuilder:
    """Create a group in the global space."""
    return _get_space().group(*entities, name=name)


# =============================================================================
# DEPRECATED/COMPATIBILITY - maintain old create/relate syntax
# =============================================================================

def create(name: str, x: float = 1.0, y: float = 1.0, **props) -> Entity:
    """
    Create an entity on the substrate.
    
    DEPRECATED: Use shape().place() for human-first syntax.
    Kept for backward compatibility.
    """
    sp = _get_space()
    return Entity(
        id=_next_id(),
        name=name,
        kind=props.pop('entity_type', 'entity'),
        space=sp,
        x=x,
        y=y,
        width=props.pop('width', 20),
        height=props.pop('height', 20),
        props=props,
    )


def relate(source: Entity, relationship: str, target: Entity) -> Entity:
    """
    Create a relationship between entities.
    
    DEPRECATED: Use attachTo() for spatial relationships.
    Kept for backward compatibility.
    """
    if not hasattr(source, '_relationships'):
        source._relationships = {}
    if relationship not in source._relationships:
        source._relationships[relationship] = []
    source._relationships[relationship].append(target)
    return source


def manifest(entity: Entity) -> Dict[str, Any]:
    """Get entity data. Alias for to_dict()."""
    return entity.to_dict()


def meaning(entity: Entity) -> str:
    """
    Get semantic meaning.
    
    Meaning emerges from geometry at level 6 (WHOLE).
    """
    entity.at_level(6)
    quadrant = 1 if entity.x >= 0 and entity.y >= 0 else (
        2 if entity.x < 0 and entity.y >= 0 else (
            3 if entity.x < 0 and entity.y < 0 else 4
        )
    )
    sign = 1 if entity.z >= 0 else -1
    
    if quadrant == 1 and sign > 0:
        return f"positive:{entity.kind}:{entity.name}"
    elif quadrant == 2:
        return f"transitional:{entity.kind}:{entity.name}"
    elif quadrant == 3:
        return f"negative:{entity.kind}:{entity.name}"
    else:
        return f"emergent:{entity.kind}:{entity.name}"


# =============================================================================
# QUERY FUNCTIONS (Legacy - use find() for new code)
# =============================================================================

def find_in_global(name: str) -> Optional[Entity]:
    """Find entity by name in global space. Use find() instead."""
    return _get_space().find(name)


def find_all() -> List[Entity]:
    """Get all entities in global space."""
    return _get_space().all()


def at(position: Union[str, Tuple[float, float]]) -> Tuple[float, float]:
    """Get coordinates for a semantic position."""
    return _resolve_position(position)


def count() -> int:
    """Count entities in global space."""
    return len(_get_space().all())


def reset():
    """Reset global space."""
    global _global_space, _entity_counter
    _global_space = None
    _entity_counter = 0


# =============================================================================
# ADVANCED — Low-level escape hatch
# =============================================================================

class AdvancedAPI:
    """
    Low-level escape hatch for when you need raw coordinates/angles.
    
    This is "expert mode" — use the human-friendly API when possible.
    """
    
    @staticmethod
    def rotateByRadians(entity: Entity, radians: float) -> Entity:
        """Rotate entity by exact radians."""
        entity.angle += radians
        return entity
    
    @staticmethod
    def rotateByDegrees(entity: Entity, degrees: float) -> Entity:
        """Rotate entity by exact degrees."""
        entity.angle += math.radians(degrees)
        return entity
    
    @staticmethod
    def setPosition(entity: Entity, x: float, y: float) -> Entity:
        """Set exact position."""
        entity.x = x
        entity.y = y
        return entity
    
    @staticmethod
    def setSize(entity: Entity, width: float, height: float) -> Entity:
        """Set exact size."""
        entity.width = width
        entity.height = height
        return entity
    
    @staticmethod
    def setAngle(entity: Entity, radians: float) -> Entity:
        """Set exact angle."""
        entity.angle = radians
        return entity
    
    @staticmethod
    def substrate() -> Substrate2D:
        """Get the underlying substrate."""
        return _get_space().substrate
    
    @staticmethod
    def substrate2D(name: str = "substrate") -> Substrate2D:
        """Create a new Substrate2D."""
        return Substrate2D(name=name)
    
    @staticmethod
    def substrate3D(name: str = "substrate") -> Substrate3D:
        """Create a new Substrate3D."""
        return Substrate3D(name=name)
    
    @staticmethod
    def geometric(shape: GeoShape) -> GeometricSubstrate:
        """Create a GeometricSubstrate."""
        return GeometricSubstrate(shape)


advanced = AdvancedAPI()
