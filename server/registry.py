"""
Substrate Registry - In-memory storage for substrates and relationships

This is the server-side registry that holds substrates created via API.
For production, this could be backed by Redis or a database.
"""

from typing import Dict, Optional, List
from datetime import datetime
from kernel.substrate import Substrate, SubstrateIdentity
from kernel.relationships import Relationship, RelationshipGraph, RelationshipType


class SubstrateMetadata:
    """Metadata for a substrate stored in the registry."""
    
    def __init__(
        self,
        substrate: Substrate,
        expression_type: str,
        expression_code: str,
        metadata: Optional[Dict] = None
    ):
        self.substrate = substrate
        self.expression_type = expression_type
        self.expression_code = expression_code
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()


class SubstrateRegistry:
    """
    In-memory registry for substrates.
    
    Stores substrates created via API and provides lookup by identity.
    Thread-safe for concurrent access.
    """
    
    def __init__(self):
        self._substrates: Dict[int, SubstrateMetadata] = {}
        self._relationship_graph = RelationshipGraph()
        self._created_at = datetime.utcnow()
    
    def add_substrate(
        self,
        substrate: Substrate,
        expression_type: str,
        expression_code: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """Add substrate to registry."""
        identity_value = substrate._x1.value
        
        if identity_value in self._substrates:
            raise ValueError(f"Substrate with identity {identity_value} already exists")
        
        self._substrates[identity_value] = SubstrateMetadata(
            substrate=substrate,
            expression_type=expression_type,
            expression_code=expression_code,
            metadata=metadata
        )
    
    def get_substrate(self, identity: int) -> Optional[SubstrateMetadata]:
        """Get substrate by identity."""
        return self._substrates.get(identity)
    
    def delete_substrate(self, identity: int) -> bool:
        """Delete substrate from registry."""
        if identity in self._substrates:
            del self._substrates[identity]
            return True
        return False
    
    def count_substrates(self) -> int:
        """Count total substrates in registry."""
        return len(self._substrates)
    
    def add_relationship(self, relationship: Relationship) -> None:
        """Add relationship to graph."""
        self._relationship_graph.add_relationship(relationship)
    
    def get_outgoing_relationships(self, source: SubstrateIdentity) -> List[Relationship]:
        """Get all outgoing relationships from a substrate."""
        return self._relationship_graph.get_outgoing(source)
    
    def get_incoming_relationships(self, target: SubstrateIdentity) -> List[Relationship]:
        """Get all incoming relationships to a substrate."""
        return self._relationship_graph.get_incoming(target)
    
    def get_relationships_by_type(self, rel_type: RelationshipType) -> List[Relationship]:
        """Get all relationships of a specific type."""
        return self._relationship_graph.get_by_type(rel_type)
    
    def count_relationships(self) -> int:
        """Count total relationships."""
        return self._relationship_graph.count()
    
    def get_uptime(self) -> float:
        """Get server uptime in seconds."""
        return (datetime.utcnow() - self._created_at).total_seconds()
    
    def clear(self) -> None:
        """Clear all substrates and relationships (for testing)."""
        self._substrates.clear()
        self._relationship_graph = RelationshipGraph()


# Global registry instance
_registry = SubstrateRegistry()


def get_registry() -> SubstrateRegistry:
    """Get the global substrate registry."""
    return _registry

