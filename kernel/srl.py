"""
SRL - Substrate Resource Locator

An SRL is a substrate that encodes connection rules.
It retrieves external data LAZILY and spawns new substrates.

RULES (Law 4):
- No raw URLs, credentials, or connection strings in code
- SRL is the ONLY way to reference external resources
- SRL is itself a substrate (64-bit identity)
- Actual connection details are resolved through lenses
"""

from __future__ import annotations
from typing import Callable, Optional

from .substrate import Substrate, SubstrateIdentity


class SRL:
    """
    Substrate Resource Locator.
    
    A substrate that encodes connection rules for external data.
    Connection details are NEVER exposed - only the mathematical
    identity is visible.
    """
    __slots__ = ('_srl_id', '_resource_expression', '_spawn_rule')
    
    def __init__(
        self,
        srl_id: SubstrateIdentity,
        resource_expression: Callable[[], int],
        spawn_rule: Callable[[int], SubstrateIdentity]
    ):
        """
        srl_id: The 64-bit identity of this SRL
        resource_expression: Math expression encoding the resource
        spawn_rule: Function to spawn new substrate from retrieved data
        """
        object.__setattr__(self, '_srl_id', srl_id)
        object.__setattr__(self, '_resource_expression', resource_expression)
        object.__setattr__(self, '_spawn_rule', spawn_rule)
    
    def __setattr__(self, name, value):
        raise TypeError("SRL is immutable")
    
    def __delattr__(self, name):
        raise TypeError("SRL is immutable")
    
    @property
    def identity(self) -> SubstrateIdentity:
        return self._srl_id
    
    @property
    def resource_expression(self) -> Callable[[], int]:
        return self._resource_expression
    
    def spawn(self, external_data: int) -> SubstrateIdentity:
        """
        Spawn a new substrate identity from external data.
        
        The external data is incorporated into the mathematical
        identity, not stored as a value.
        """
        return self._spawn_rule(external_data)
    
    def __repr__(self) -> str:
        return f"SRL({self._srl_id})"

    # ═══════════════════════════════════════════════════════════════
    # DIMENSIONAL LAW HELPERS
    # ═══════════════════════════════════════════════════════════════

    # ─────────────────────────────────────────────────────────────
    # LAW FOUR: Connection Creates Meaning
    # ─────────────────────────────────────────────────────────────

    def connect(self, substrate_a: Substrate, substrate_b: Substrate) -> SubstrateIdentity:
        """
        Create a relationship substrate connecting two substrates.

        LAW FOUR: Dimensions relate through connection.

        The SRL defines the connection rule. This method creates
        a new substrate identity representing the relationship.

        Args:
            substrate_a: First substrate
            substrate_b: Second substrate

        Returns:
            New substrate identity representing the relationship
        """
        # Create relationship data from both substrates
        relationship_data = (
            substrate_a.identity.value ^ substrate_b.identity.value
        ) & 0xFFFFFFFFFFFFFFFF

        # Spawn new substrate identity for the relationship
        return self.spawn(relationship_data)

    def build_network(self, substrates: list) -> list:
        """
        Build a relationship network from multiple substrates.

        LAW FOUR: Connection creates meaning.

        Creates pairwise relationships between all substrates,
        forming a network where meaning emerges from the pattern.

        Args:
            substrates: List of substrates to connect

        Returns:
            List of relationship substrate identities
        """
        relationships = []

        # Create pairwise connections
        for i in range(len(substrates)):
            for j in range(i + 1, len(substrates)):
                relationship = self.connect(substrates[i], substrates[j])
                relationships.append(relationship)

        return relationships

    def spawn_relationship(self, substrate_a_id: int, substrate_b_id: int) -> SubstrateIdentity:
        """
        Spawn a relationship substrate from two substrate IDs.

        LAW FOUR: Relationships are dimensions of their own.

        Args:
            substrate_a_id: First substrate's 64-bit identity
            substrate_b_id: Second substrate's 64-bit identity

        Returns:
            New substrate identity for the relationship
        """
        # Create relationship data
        relationship_data = (substrate_a_id ^ substrate_b_id) & 0xFFFFFFFFFFFFFFFF

        # Spawn relationship substrate
        return self.spawn(relationship_data)

    # ─────────────────────────────────────────────────────────────
    # LAW FIVE: Change Is Motion
    # ─────────────────────────────────────────────────────────────

    def track_evolution(self, substrate: Substrate, versions: list) -> list:
        """
        Track substrate evolution through multiple versions.

        LAW FIVE: Change is motion through dimensions.

        Each version represents a state in the substrate's evolution.
        The SRL can spawn new substrate identities for each version.

        Args:
            substrate: The substrate to track
            versions: List of version numbers or states

        Returns:
            List of substrate identities (evolution trajectory)
        """
        trajectory = [substrate.identity]  # Start with current state

        for version in versions:
            # Create version-specific data
            version_data = (substrate.identity.value + version) & 0xFFFFFFFFFFFFFFFF

            # Spawn new identity for this version
            new_identity = self.spawn(version_data)
            trajectory.append(new_identity)

        return trajectory

    def get_evolution_path(self, start_id: int, end_id: int, steps: int) -> list:
        """
        Get evolution path between two substrate identities.

        LAW FIVE: Time is the order of motion.

        Creates intermediate substrate identities representing
        the path from start to end.

        Args:
            start_id: Starting substrate identity
            end_id: Ending substrate identity
            steps: Number of intermediate steps

        Returns:
            List of substrate identities forming the path
        """
        path = [SubstrateIdentity(start_id)]

        if steps <= 0:
            path.append(SubstrateIdentity(end_id))
            return path

        # Calculate step size
        delta = ((end_id - start_id) // (steps + 1)) & 0xFFFFFFFFFFFFFFFF

        # Create intermediate identities
        current = start_id
        for _ in range(steps):
            current = (current + delta) & 0xFFFFFFFFFFFFFFFF
            path.append(self.spawn(current))

        # Add final identity
        path.append(SubstrateIdentity(end_id))

        return path


def create_srl_identity(
    resource_type: int,
    resource_namespace: int,
    resource_path: int
) -> int:
    """
    Create a deterministic SRL identity from components.
    
    All components are mathematical - no strings, no URLs.
    The identity encodes the connection rule, not the data.
    """
    # Pack components into 64-bit identity
    # High 16 bits: resource type
    # Middle 24 bits: namespace  
    # Low 24 bits: path
    
    type_part = (resource_type & 0xFFFF) << 48
    namespace_part = (resource_namespace & 0xFFFFFF) << 24
    path_part = resource_path & 0xFFFFFF
    
    return type_part | namespace_part | path_part
