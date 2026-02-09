"""
Dimensional Relationships - Relationships as First-Class Dimensions

This module implements relationships as first-class dimensional entities.

CORE PRINCIPLE:
Relationships ARE dimensions, not metadata. Every relationship has:
- 64-bit identity
- Direction (whole→part, part→whole, sibling, etc.)
- Constraints
- Lineage

RELATIONSHIP TYPES:
1. Structural (from division): part→whole, whole→part, sibling, containment
2. Operational (from addition): attribute, dependency, adjacency, aggregation
3. Residual (from modulus): boundary, cycle, recursion, lineage
4. Projection (from power/root): embedding, extraction, orthogonal

CHARTER COMPLIANCE:
✅ Principle 1: All things are by reference
✅ Principle 3: No self-modifying code (immutable)
✅ Principle 4: No global power surface
✅ Principle 6: All relationships visible
✅ Principle 9: Redemption Equation (reversible)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
from kernel.substrate import SubstrateIdentity

# 64-bit mask
MASK_64 = 0xFFFFFFFFFFFFFFFF


class RelationshipType(Enum):
    """Types of dimensional relationships."""
    
    # Structural relationships (from division)
    PART_TO_WHOLE = "part_to_whole"  # Child knows parent
    WHOLE_TO_PART = "whole_to_part"  # Parent knows children
    SIBLING = "sibling"  # Peer relationships
    CONTAINMENT = "containment"  # Spatial/logical containment
    
    # Operational relationships (from addition)
    ATTRIBUTE = "attribute"  # Entity has attribute
    DEPENDENCY = "dependency"  # Entity depends on entity
    ADJACENCY = "adjacency"  # Spatial/temporal proximity
    AGGREGATION = "aggregation"  # Collection membership
    
    # Residual relationships (from modulus)
    BOUNDARY = "boundary"  # Dimensional boundary
    CYCLE = "cycle"  # Cycle origin
    RECURSION = "recursion"  # Recursion seed
    LINEAGE = "lineage"  # Unexpressed identity inheritance
    
    # Projection relationships (from power/root)
    EMBEDDING = "embedding"  # Lower dimension in higher
    EXTRACTION = "extraction"  # Higher dimension to lower
    ORTHOGONAL = "orthogonal"  # Independent axes


@dataclass(frozen=True)
class Relationship:
    """
    A relationship is a first-class dimension.
    
    Every relationship has identity, direction, and lineage.
    Relationships are immutable once created.
    """
    identity: SubstrateIdentity  # 64-bit unique identity
    rel_type: RelationshipType  # Type of relationship
    source: SubstrateIdentity  # Source entity
    target: SubstrateIdentity  # Target entity
    bidirectional: bool = False  # Whether relationship goes both ways
    constraints: Optional[Dict[str, any]] = None  # Relationship constraints
    lineage: Optional[SubstrateIdentity] = None  # Parent relationship
    
    def __post_init__(self):
        """Validate relationship."""
        if not isinstance(self.identity, SubstrateIdentity):
            raise TypeError("Relationship identity must be SubstrateIdentity")
        if not isinstance(self.source, SubstrateIdentity):
            raise TypeError("Source must be SubstrateIdentity")
        if not isinstance(self.target, SubstrateIdentity):
            raise TypeError("Target must be SubstrateIdentity")
    
    def reverse(self) -> Relationship:
        """
        Create reverse relationship (target → source).
        
        Returns new relationship with swapped source/target.
        """
        # Create new identity for reverse relationship
        reverse_identity_value = (int(self.identity) ^ int(self.source) ^ int(self.target)) & MASK_64
        
        return Relationship(
            identity=SubstrateIdentity(reverse_identity_value),
            rel_type=self.rel_type,
            source=self.target,
            target=self.source,
            bidirectional=self.bidirectional,
            constraints=self.constraints,
            lineage=self.identity  # Original relationship is parent
        )
    
    def __repr__(self) -> str:
        arrow = "↔" if self.bidirectional else "→"
        return f"Relationship({self.rel_type.value}: {self.source} {arrow} {self.target})"


@dataclass
class RelationshipSet:
    """
    A set of relationships.
    
    Relationships are organized by type for efficient querying.
    This is the primary way to work with relationship collections.
    """
    _relationships: Dict[RelationshipType, List[Relationship]]
    
    def __init__(self):
        """Create empty relationship set."""
        self._relationships = {rel_type: [] for rel_type in RelationshipType}
    
    def add(self, relationship: Relationship) -> None:
        """Add relationship to set."""
        if not isinstance(relationship, Relationship):
            raise TypeError("Must add Relationship instance")
        
        self._relationships[relationship.rel_type].append(relationship)
    
    def get_by_type(self, rel_type: RelationshipType) -> List[Relationship]:
        """Get all relationships of a specific type."""
        return self._relationships.get(rel_type, [])
    
    def get_by_source(self, source: SubstrateIdentity) -> List[Relationship]:
        """Get all relationships from a source entity."""
        result = []
        for relationships in self._relationships.values():
            result.extend([r for r in relationships if r.source == source])
        return result
    
    def get_by_target(self, target: SubstrateIdentity) -> List[Relationship]:
        """Get all relationships to a target entity."""
        result = []
        for relationships in self._relationships.values():
            result.extend([r for r in relationships if r.target == target])
        return result
    
    def get_all(self) -> List[Relationship]:
        """Get all relationships in set."""
        result = []
        for relationships in self._relationships.values():
            result.extend(relationships)
        return result
    
    def count(self) -> int:
        """Count total relationships."""
        return sum(len(rels) for rels in self._relationships.values())
    
    def __repr__(self) -> str:
        return f"RelationshipSet(count={self.count()})"


class RelationshipGraph:
    """
    Graph structure for managing relationships between substrates.

    Provides efficient querying of relationships by source, target, or type.
    Optimized for large-scale relationship graphs.
    """

    def __init__(self):
        """Create empty relationship graph."""
        self._relationships: List[Relationship] = []
        self._by_source: Dict[int, List[Relationship]] = {}
        self._by_target: Dict[int, List[Relationship]] = {}
        self._by_type: Dict[RelationshipType, List[Relationship]] = {
            rel_type: [] for rel_type in RelationshipType
        }

    def add_relationship(self, relationship: Relationship) -> None:
        """Add relationship to graph."""
        if not isinstance(relationship, Relationship):
            raise TypeError("Must add Relationship instance")

        self._relationships.append(relationship)

        # Index by source (use .value property)
        source_id = relationship.source.value
        if source_id not in self._by_source:
            self._by_source[source_id] = []
        self._by_source[source_id].append(relationship)

        # Index by target (use .value property)
        target_id = relationship.target.value
        if target_id not in self._by_target:
            self._by_target[target_id] = []
        self._by_target[target_id].append(relationship)

        # Index by type
        self._by_type[relationship.rel_type].append(relationship)

    def get_outgoing(self, source: SubstrateIdentity) -> List[Relationship]:
        """Get all relationships from a source."""
        return self._by_source.get(source.value, [])

    def get_incoming(self, target: SubstrateIdentity) -> List[Relationship]:
        """Get all relationships to a target."""
        return self._by_target.get(target.value, [])

    def get_by_type(self, rel_type: RelationshipType) -> List[Relationship]:
        """Get all relationships of a specific type."""
        return self._by_type.get(rel_type, [])

    def get_all(self) -> List[Relationship]:
        """Get all relationships."""
        return self._relationships

    def count(self) -> int:
        """Count total relationships."""
        return len(self._relationships)

    def __repr__(self) -> str:
        return f"RelationshipGraph(relationships={self.count()})"


