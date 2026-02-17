"""
ButterflyFX Identity-First Layer

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

This mathematical kernel belongs to all humanity.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

THE IDENTITY-FIRST PARADIGM:

> "Manifestation does NOT begin with the object — it begins with identity."
> "The object is not the truth — it is the shadow."
> "Identity precedes form. Meaning transcends form."

The semantic levels:
    D0: Void         — Nothing exists, only possibility
    D1: Identity     — UUID, name, "this" — the anchor, NOT the object
    D2: Relationship — Attributes, references, links
    D3: Structure    — Schema, blueprint, geometry — still no object
    D4: Manifestation — Object APPEARS — first visible form (collapsed projection)
    D5: Multiplicity — Systems, behavior, interaction
    D6: Meaning      — Interpretation — transcends form

The object at D4 is a COLLAPSED PROJECTION of the identity at D1:
    Identity(D1) → collapse → Object(D4) → transcend → Meaning(D6)

This maps to:
    - Fibonacci: 0-1-1-2-3-5-8-13 (spiral transition)
    - OSI Model: Physical → Transport → Presentation
    - Genesis: Light → Sun/Moon → Humans → Rest
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Callable, TypeVar, Generic
from enum import IntEnum
from collections import defaultdict
import uuid as uuid_module


# =============================================================================
# SEMANTIC LEVELS
# =============================================================================

class SemanticLevel(IntEnum):
    """
    Semantic purpose of each dimensional level.
    
    The Identity-First paradigm assigns MEANING to each level:
    - D1 is most FUNDAMENTAL (everything derives from identity)
    - D4 is the MANIFESTATION POINT (object appears)
    - D6 is most ABSTRACT (meaning transcends form)
    """
    VOID = 0           # Nothing exists — only possibility
    IDENTITY = 1       # UUID, name, "this" — the anchor, NOT the object
    RELATIONSHIP = 2   # Attributes, references, links
    STRUCTURE = 3      # Schema, blueprint, geometry — still no object
    MANIFESTATION = 4  # Object APPEARS — first visible form
    MULTIPLICITY = 5   # Systems, behavior, interaction
    MEANING = 6        # Interpretation — transcends form


SEMANTIC_NAMES: Dict[int, str] = {
    0: "Void",
    1: "Identity",
    2: "Relationship",
    3: "Structure",
    4: "Manifestation",
    5: "Multiplicity",
    6: "Meaning"
}

SEMANTIC_DESCRIPTIONS: Dict[int, str] = {
    0: "Nothing exists yet — only pure possibility",
    1: "The identity anchor (UUID, name) — NOT the object itself",
    2: "Attributes, references, links — relationships between identities",
    3: "Schema, blueprint, geometry — the structure before manifestation",
    4: "The object APPEARS — first visible/tangible form (collapsed projection)",
    5: "Systems, behavior, interaction — multiplicity and dynamics",
    6: "Interpretation and meaning — transcends the physical form"
}

# Universal mappings
FIBONACCI_MAP: Dict[int, int] = {0: 0, 1: 1, 2: 1, 3: 2, 4: 3, 5: 5, 6: 8}
OSI_MAP: Dict[int, str] = {
    0: "(Pre-network)", 1: "Physical", 2: "Data Link", 3: "Network",
    4: "Transport", 5: "Session", 6: "Presentation"
}
GENESIS_MAP: Dict[int, str] = {
    0: "Formless and void", 1: "Let there be light", 2: "Separation of waters",
    3: "Land and vegetation", 4: "Sun, moon, and stars", 5: "Fish and birds",
    6: "Humans"
}


# =============================================================================
# IDENTITY ANCHOR - The Most Fundamental Entity
# =============================================================================

T = TypeVar('T')


@dataclass
class IdentityAnchor(Generic[T]):
    """
    The identity exists BEFORE any object.
    
    This is D1 (Identity) — the most fundamental level.
    Everything else derives from this anchor.
    
    Properties:
        uuid: Unique identifier — the "this"
        name: Human-readable name
        relationships: D2 — links to other identities
        structure: D3 — schema/blueprint before manifestation
        _manifestation: D4 — lazy, created on demand
        _meaning: D6 — interpretation, assigned after manifestation
    
    The object (D4) is a COLLAPSED PROJECTION of identity (D1).
    """
    uuid: str
    name: str
    entity_type: str = "entity"
    
    # D2: Relationships (before form)
    relationships: Dict[str, Any] = field(default_factory=dict)
    
    # D3: Structure (before form)
    structure: Dict[str, Any] = field(default_factory=dict)
    
    # D4: Manifestation (lazy — not created until collapse)
    _manifestation: Optional[T] = field(default=None, repr=False)
    _manifested: bool = field(default=False, repr=False)
    
    # D5: Multiplicity (behavior/interaction handlers)
    _behaviors: Dict[str, Callable] = field(default_factory=dict, repr=False)
    
    # D6: Meaning (transcends form)
    _meaning: Optional[str] = field(default=None, repr=False)
    _interpreted: bool = field(default=False, repr=False)
    
    # Tracking
    _level: SemanticLevel = field(default=SemanticLevel.IDENTITY, repr=False)
    
    # -------------------------------------------------------------------------
    # D1: IDENTITY OPERATIONS
    # -------------------------------------------------------------------------
    
    @classmethod
    def create(cls, name: str, entity_type: str = "entity") -> 'IdentityAnchor':
        """
        Create a new identity anchor.
        
        This is the TRUE BEGINNING — identity exists before any object.
        """
        return cls(
            uuid=str(uuid_module.uuid4()),
            name=name,
            entity_type=entity_type
        )
    
    @property
    def id(self) -> str:
        """Alias for uuid"""
        return self.uuid
    
    @property
    def level(self) -> SemanticLevel:
        """Current semantic level"""
        return self._level
    
    @property
    def level_name(self) -> str:
        """Name of current semantic level"""
        return SEMANTIC_NAMES[self._level]
    
    # -------------------------------------------------------------------------
    # D2: RELATIONSHIP OPERATIONS
    # -------------------------------------------------------------------------
    
    def relate(self, rel_type: str, target: 'IdentityAnchor | str') -> 'IdentityAnchor':
        """
        Add relationship to another identity at D2.
        
        Relationships exist BEFORE form — they connect identities,
        not objects.
        """
        target_id = target.uuid if isinstance(target, IdentityAnchor) else target
        
        if rel_type not in self.relationships:
            self.relationships[rel_type] = []
        
        if target_id not in self.relationships[rel_type]:
            self.relationships[rel_type].append(target_id)
        
        self._level = max(self._level, SemanticLevel.RELATIONSHIP)
        return self
    
    def unrelate(self, rel_type: str, target: 'IdentityAnchor | str') -> 'IdentityAnchor':
        """Remove relationship"""
        target_id = target.uuid if isinstance(target, IdentityAnchor) else target
        
        if rel_type in self.relationships and target_id in self.relationships[rel_type]:
            self.relationships[rel_type].remove(target_id)
        
        return self
    
    def get_relations(self, rel_type: str) -> List[str]:
        """Get all related identity UUIDs"""
        return self.relationships.get(rel_type, [])
    
    # -------------------------------------------------------------------------
    # D3: STRUCTURE OPERATIONS
    # -------------------------------------------------------------------------
    
    def define(self, **properties) -> 'IdentityAnchor':
        """
        Define structure at D3.
        
        Structure is the blueprint — schema, geometry, properties.
        The object still doesn't exist yet!
        """
        self.structure.update(properties)
        self._level = max(self._level, SemanticLevel.STRUCTURE)
        return self
    
    def schema(self, structure_dict: Dict[str, Any]) -> 'IdentityAnchor':
        """Set entire structure at once"""
        self.structure = structure_dict
        self._level = max(self._level, SemanticLevel.STRUCTURE)
        return self
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """Get structure property"""
        return self.structure.get(key, default)
    
    # -------------------------------------------------------------------------
    # D4: MANIFESTATION - The Object APPEARS Here
    # -------------------------------------------------------------------------
    
    @property
    def manifestation(self) -> T:
        """
        Collapse identity to manifestation at D4.
        
        THIS is where the object first APPEARS.
        The object is a PROJECTION of identity through structure.
        
        LAZY: The manifestation is not created until first access.
        """
        if not self._manifested:
            self._manifestation = self._collapse_to_form()
            self._manifested = True
            self._level = max(self._level, SemanticLevel.MANIFESTATION)
        return self._manifestation
    
    def _collapse_to_form(self) -> Dict[str, Any]:
        """
        Create the manifested object.
        
        The object is built from:
            - Identity (uuid, name, type) from D1
            - Relationships from D2
            - Structure from D3
        
        Override this method for custom manifestation logic.
        """
        return {
            "id": self.uuid,
            "name": self.name,
            "type": self.entity_type,
            "properties": dict(self.structure),
            "relationships": dict(self.relationships),
        }
    
    def manifest(self, custom_form: Optional[T] = None) -> T:
        """
        Explicitly collapse to manifestation.
        
        Optionally provide a custom manifestation.
        """
        if custom_form is not None:
            self._manifestation = custom_form
            self._manifested = True
        
        self._level = max(self._level, SemanticLevel.MANIFESTATION)
        return self.manifestation
    
    @property
    def is_manifested(self) -> bool:
        """Check if manifestation has been collapsed"""
        return self._manifested
    
    def dematerialize(self) -> 'IdentityAnchor':
        """
        Return to potential — unmake the manifestation.
        
        The identity remains, but the object disappears.
        """
        self._manifestation = None
        self._manifested = False
        self._meaning = None
        self._interpreted = False
        self._level = SemanticLevel.STRUCTURE if self.structure else SemanticLevel.IDENTITY
        return self
    
    # -------------------------------------------------------------------------
    # D5: MULTIPLICITY - Behavior and Interaction
    # -------------------------------------------------------------------------
    
    def behave(self, action: str, handler: Callable) -> 'IdentityAnchor':
        """
        Register behavior at D5.
        
        Behaviors define how the entity interacts in systems.
        """
        self._behaviors[action] = handler
        self._level = max(self._level, SemanticLevel.MULTIPLICITY)
        return self
    
    def act(self, action: str, *args, **kwargs) -> Any:
        """Execute behavior"""
        if action not in self._behaviors:
            raise ValueError(f"No behavior registered for '{action}'")
        return self._behaviors[action](self, *args, **kwargs)
    
    def can_act(self, action: str) -> bool:
        """Check if behavior exists"""
        return action in self._behaviors
    
    # -------------------------------------------------------------------------
    # D6: MEANING - Transcends Form
    # -------------------------------------------------------------------------
    
    @property
    def meaning(self) -> str:
        """
        Get meaning at D6.
        
        Meaning TRANSCENDS the physical form.
        It is ABOVE the object, not a property of it.
        """
        if not self._interpreted:
            self._meaning = self._interpret()
            self._interpreted = True
            self._level = max(self._level, SemanticLevel.MEANING)
        return self._meaning
    
    def _interpret(self) -> str:
        """
        Derive meaning from identity, structure, and manifestation.
        
        Override for custom interpretation logic.
        """
        return f"{self.entity_type}:{self.name}"
    
    def assign_meaning(self, meaning: str) -> 'IdentityAnchor':
        """Explicitly assign meaning"""
        self._meaning = meaning
        self._interpreted = True
        self._level = max(self._level, SemanticLevel.MEANING)
        return self
    
    @property
    def is_interpreted(self) -> bool:
        """Check if meaning has been assigned"""
        return self._interpreted
    
    # -------------------------------------------------------------------------
    # NAVIGATION - The Key Advantage
    # -------------------------------------------------------------------------
    
    def identity_to_meaning(self) -> str:
        """
        Navigate from identity (D1) to meaning (D6).
        
        This is the Identity-First advantage:
            - Start with identity, not object
            - Collapse to form when needed (lazy)
            - Transcend to meaning when needed
        
        Operations: O(1) semantic transitions
        Traditional: O(N) iteration to find, build, derive
        """
        # Identity already exists at D1
        
        # Collapse to manifestation at D4 (lazy)
        _ = self.manifestation
        
        # Transcend to meaning at D6
        return self.meaning
    
    # -------------------------------------------------------------------------
    # SERIALIZATION
    # -------------------------------------------------------------------------
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize identity anchor"""
        return {
            "uuid": self.uuid,
            "name": self.name,
            "type": self.entity_type,
            "level": int(self._level),
            "level_name": self.level_name,
            "relationships": self.relationships,
            "structure": self.structure,
            "manifested": self._manifested,
            "interpreted": self._interpreted,
            "meaning": self._meaning if self._interpreted else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IdentityAnchor':
        """Deserialize identity anchor"""
        anchor = cls(
            uuid=data["uuid"],
            name=data["name"],
            entity_type=data.get("type", "entity"),
            relationships=data.get("relationships", {}),
            structure=data.get("structure", {}),
        )
        anchor._level = SemanticLevel(data.get("level", 1))
        
        if data.get("meaning"):
            anchor._meaning = data["meaning"]
            anchor._interpreted = True
        
        return anchor
    
    def __repr__(self) -> str:
        state = "potential"
        if self._manifested:
            state = "manifested"
        if self._interpreted:
            state = "meaningful"
        return f"Identity({self.name}@{self.level_name}, {state})"


# =============================================================================
# IDENTITY REGISTRY - Managing Multiple Identities
# =============================================================================

class IdentityRegistry:
    """
    Registry for managing multiple identity anchors.
    
    Provides semantic-level operations across all identities:
        - invoke(level) to get all identities at a semantic level
        - navigate between levels
        - lazy manifestation tracking
    """
    
    def __init__(self):
        self._identities: Dict[str, IdentityAnchor] = {}
        self._by_level: Dict[SemanticLevel, Set[str]] = defaultdict(set)
        self._by_type: Dict[str, Set[str]] = defaultdict(set)
        self._operation_count: int = 0
    
    # -------------------------------------------------------------------------
    # REGISTRATION
    # -------------------------------------------------------------------------
    
    def create(self, name: str, entity_type: str = "entity") -> IdentityAnchor:
        """Create and register a new identity"""
        anchor = IdentityAnchor.create(name, entity_type)
        self.register(anchor)
        return anchor
    
    def register(self, anchor: IdentityAnchor) -> None:
        """Register an existing identity anchor"""
        self._identities[anchor.uuid] = anchor
        self._by_level[anchor.level].add(anchor.uuid)
        self._by_type[anchor.entity_type].add(anchor.uuid)
        self._operation_count += 1
    
    def unregister(self, anchor_or_uuid: IdentityAnchor | str) -> None:
        """Remove identity from registry"""
        uuid = anchor_or_uuid.uuid if isinstance(anchor_or_uuid, IdentityAnchor) else anchor_or_uuid
        
        if uuid in self._identities:
            anchor = self._identities[uuid]
            self._by_level[anchor.level].discard(uuid)
            self._by_type[anchor.entity_type].discard(uuid)
            del self._identities[uuid]
    
    # -------------------------------------------------------------------------
    # RETRIEVAL
    # -------------------------------------------------------------------------
    
    def get(self, uuid: str) -> Optional[IdentityAnchor]:
        """Get identity by UUID"""
        self._operation_count += 1
        return self._identities.get(uuid)
    
    def get_by_name(self, name: str) -> Optional[IdentityAnchor]:
        """Get first identity with matching name"""
        self._operation_count += 1
        for anchor in self._identities.values():
            if anchor.name == name:
                return anchor
        return None
    
    def __getitem__(self, uuid: str) -> IdentityAnchor:
        """Dictionary-style access"""
        return self._identities[uuid]
    
    def __contains__(self, uuid: str) -> bool:
        return uuid in self._identities
    
    def __len__(self) -> int:
        return len(self._identities)
    
    def __iter__(self):
        return iter(self._identities.values())
    
    # -------------------------------------------------------------------------
    # SEMANTIC OPERATIONS - O(1) Level Access
    # -------------------------------------------------------------------------
    
    def invoke(self, level: SemanticLevel) -> Set[IdentityAnchor]:
        """
        Get all identities at a semantic level.
        
        This is O(1) — no iteration required!
        The Identity-First advantage.
        """
        self._operation_count += 1
        uuids = self._by_level[level]
        return {self._identities[uuid] for uuid in uuids}
    
    def invoke_by_type(self, entity_type: str) -> Set[IdentityAnchor]:
        """Get all identities of a type"""
        self._operation_count += 1
        uuids = self._by_type[entity_type]
        return {self._identities[uuid] for uuid in uuids}
    
    def at_void(self) -> Set[IdentityAnchor]:
        """Get identities at D0 (Void)"""
        return self.invoke(SemanticLevel.VOID)
    
    def at_identity(self) -> Set[IdentityAnchor]:
        """Get identities at D1 (Identity)"""
        return self.invoke(SemanticLevel.IDENTITY)
    
    def at_relationship(self) -> Set[IdentityAnchor]:
        """Get identities at D2 (Relationship)"""
        return self.invoke(SemanticLevel.RELATIONSHIP)
    
    def at_structure(self) -> Set[IdentityAnchor]:
        """Get identities at D3 (Structure)"""
        return self.invoke(SemanticLevel.STRUCTURE)
    
    def at_manifestation(self) -> Set[IdentityAnchor]:
        """Get identities at D4 (Manifestation) — manifested objects"""
        return self.invoke(SemanticLevel.MANIFESTATION)
    
    def at_multiplicity(self) -> Set[IdentityAnchor]:
        """Get identities at D5 (Multiplicity) — with behaviors"""
        return self.invoke(SemanticLevel.MULTIPLICITY)
    
    def at_meaning(self) -> Set[IdentityAnchor]:
        """Get identities at D6 (Meaning) — interpreted"""
        return self.invoke(SemanticLevel.MEANING)
    
    # -------------------------------------------------------------------------
    # BULK OPERATIONS
    # -------------------------------------------------------------------------
    
    def manifest_all(self) -> List[Any]:
        """Manifest all identities — collapse all to D4"""
        return [anchor.manifestation for anchor in self._identities.values()]
    
    def interpret_all(self) -> List[str]:
        """Interpret all identities — transcend all to D6"""
        return [anchor.meaning for anchor in self._identities.values()]
    
    def dematerialize_all(self) -> None:
        """Return all to potential"""
        for anchor in self._identities.values():
            anchor.dematerialize()
    
    # -------------------------------------------------------------------------
    # STATS
    # -------------------------------------------------------------------------
    
    @property
    def operation_count(self) -> int:
        return self._operation_count
    
    def reset_stats(self) -> None:
        self._operation_count = 0
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        manifested = sum(1 for a in self._identities.values() if a.is_manifested)
        interpreted = sum(1 for a in self._identities.values() if a.is_interpreted)
        
        return {
            "total": len(self._identities),
            "manifested": manifested,
            "potential": len(self._identities) - manifested,
            "interpreted": interpreted,
            "by_level": {
                SEMANTIC_NAMES[level]: len(uuids) 
                for level, uuids in self._by_level.items()
                if uuids
            },
            "by_type": {
                etype: len(uuids) 
                for etype, uuids in self._by_type.items()
            },
            "operations": self._operation_count,
        }
    
    def __repr__(self) -> str:
        return f"IdentityRegistry({len(self._identities)} identities, {self._operation_count} ops)"


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

# Global registry (optional)
_default_registry: Optional[IdentityRegistry] = None


def get_identity_registry() -> IdentityRegistry:
    """Get or create the default identity registry"""
    global _default_registry
    if _default_registry is None:
        _default_registry = IdentityRegistry()
    return _default_registry


def create_identity(name: str, entity_type: str = "entity") -> IdentityAnchor:
    """Create identity in default registry"""
    return get_identity_registry().create(name, entity_type)


def identity(name: str, **structure) -> IdentityAnchor:
    """
    Quick identity creation with structure.
    
    Example:
        car = identity("MyCar", wheels=4, engine="v8", color="red")
    """
    anchor = create_identity(name, "entity")
    if structure:
        anchor.define(**structure)
    return anchor


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Core classes
    'IdentityAnchor',
    'IdentityRegistry',
    'SemanticLevel',
    
    # Constants
    'SEMANTIC_NAMES',
    'SEMANTIC_DESCRIPTIONS',
    'FIBONACCI_MAP',
    'OSI_MAP',
    'GENESIS_MAP',
    
    # Convenience
    'get_identity_registry',
    'create_identity',
    'identity',
]
