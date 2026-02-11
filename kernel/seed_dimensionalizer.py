"""
Seed Dimensionalizer - Converts Seeds into Dimensional Substrates

PHILOSOPHY:
When a seed enters the kernel, it must be DIMENSIONALIZED:

1. The seed itself is a POINT (0D) in a higher dimension
2. Its parts exist in LOWER dimensions (Russian Dolls principle)
3. Each part is itself a point that can be further divided

DIMENSIONAL HIERARCHY (Fibonacci):
- Dimension 0 (Point):     The seed identity itself
- Dimension 1 (Line):      Name + Category (identity axis)
- Dimension 1 (Line):      Domain + Tier (classification axis)
- Dimension 2 (Plane):     Definition + Meaning (semantic space)
- Dimension 3 (Volume):    Usage + Examples (application space)
- Dimension 5 (5D):        Relationships (connection space)
- Dimension 8 (8D):        Expression (computational space)
- Dimension 13 (13D):      Metadata + Tags (context space)
- Dimension 21 (21D):      Complete seed (whole object)

LAW COMPLIANCE:
- Law One: Seed begins as unity (64-bit identity)
- Law Two: Division creates dimensions (parts in lower dimensions)
- Law Three: Every part inherits the whole (each part contains seed identity)
- Law Six: Identity persists (seed identity NEVER changes)
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from kernel.substrate import Substrate, SubstrateIdentity
from kernel.dimensional import Dimension
from kernel.seed_types import PrimitiveSeed


@dataclass(frozen=True)
class DimensionalizedSeed:
    """
    A seed that has been dimensionalized into substrate form.
    
    The seed is now a POINT in 21D space, with each dimension
    containing specific aspects of the seed's knowledge.
    """
    # UNITY (0D) - The seed as undivided whole
    substrate: Substrate
    
    # DIMENSIONAL DECOMPOSITION (Fibonacci hierarchy)
    dimensions: Dict[int, Any]  # Maps Fibonacci level → content
    
    # ORIGINAL SEED (for reference)
    original_seed: PrimitiveSeed


class SeedDimensionalizer:
    """
    Dimensionalizes seeds when they enter the kernel.
    
    Converts flat seed data into hierarchical dimensional structure
    following the Russian Dolls principle.
    """
    
    # Fibonacci dimensional levels
    FIBONACCI_LEVELS = [0, 1, 1, 2, 3, 5, 8, 13, 21]
    
    def dimensionalize(self, seed: PrimitiveSeed) -> DimensionalizedSeed:
        """
        Convert a seed into a dimensional substrate.
        
        Args:
            seed: The primitive seed to dimensionalize
            
        Returns:
            DimensionalizedSeed with hierarchical structure
            
        Process:
        1. Create substrate from seed identity
        2. Decompose seed into dimensional hierarchy
        3. Each part becomes a point in lower dimension
        4. Parts contain parts (recursive Russian Dolls)
        """
        # 1. CREATE SUBSTRATE (Unity - 0D point in 21D space)
        substrate = self._create_substrate(seed)
        
        # 2. DECOMPOSE INTO DIMENSIONS (Division creates dimensions)
        dimensions = self._decompose_to_dimensions(seed)
        
        # 3. RETURN DIMENSIONALIZED SEED
        return DimensionalizedSeed(
            substrate=substrate,
            dimensions=dimensions,
            original_seed=seed
        )
    
    def _create_substrate(self, seed: PrimitiveSeed) -> Substrate:
        """
        Create substrate from seed.
        
        The substrate IS the seed's mathematical expression.
        The 64-bit identity is the seed's identity.
        """
        # Use seed's existing identity
        identity = seed.identity
        
        # Create expression that can compute any seed attribute
        def seed_expression(**kwargs):
            """
            The seed's expression - computes attributes on demand.
            
            This is the DNA of the seed. All attributes exist in superposition.
            Invocation collapses potential into manifestation.
            """
            attr = kwargs.get('attribute', 'identity')
            
            # Dimension 0: Identity
            if attr == 'identity':
                return identity.value
            
            # Dimension 1: Name + Category
            if attr == 'name':
                return seed.name
            if attr == 'category':
                return seed.category.value
            
            # Dimension 1: Domain + Tier
            if attr == 'domain':
                return seed.domain
            if attr == 'tier':
                return seed.metadata.get('tier', 1)
            
            # Dimension 2: Definition + Meaning
            if attr == 'definition':
                return seed.definition
            if attr == 'meaning':
                return seed.meaning
            
            # Dimension 3: Usage + Examples
            if attr == 'usage':
                return seed.usage
            if attr == 'examples':
                return seed.examples
            
            # Dimension 5: Relationships
            if attr == 'relationships':
                return seed.relationships
            if attr == 'related':
                return seed.related
            if attr == 'synonyms':
                return seed.synonyms
            if attr == 'antonyms':
                return seed.antonyms
            
            # Dimension 8: Expression (computational)
            if attr == 'expression':
                return seed.expression
            if attr == 'signature':
                return seed.signature
            if attr == 'return_type':
                return seed.return_type
            
            # Dimension 13: Metadata + Tags
            if attr == 'metadata':
                return seed.metadata
            if attr == 'tags':
                return seed.tags

            # Dimension 21: Complete seed (whole object)
            if attr == 'complete':
                return seed

            # Unknown attribute - return None (exists in potential)
            return None

        # Create and return substrate
        return Substrate(identity, seed_expression)

    def _decompose_to_dimensions(self, seed: PrimitiveSeed) -> Dict[int, Any]:
        """
        Decompose seed into Fibonacci dimensional hierarchy.

        Each dimension contains specific aspects of the seed.
        Higher dimensions contain lower dimensions (Russian Dolls).

        Returns:
            Dictionary mapping Fibonacci level → content
        """
        dimensions = {}

        # Dimension 0 (Point): The seed identity itself
        dimensions[0] = {
            'type': 'identity',
            'content': seed.identity,
            'description': 'The seed as undivided unity (point in 21D space)'
        }

        # Dimension 1 (Line): Name + Category (identity axis)
        dimensions[1] = {
            'type': 'identity_axis',
            'content': {
                'name': seed.name,
                'category': seed.category
            },
            'description': 'Identity axis: who/what this seed is',
            'contains': [0]  # Contains dimension 0
        }

        # Dimension 1 (Line): Domain + Tier (classification axis)
        # Note: Two 1D dimensions (different axes in same dimensional level)
        dimensions['1b'] = {
            'type': 'classification_axis',
            'content': {
                'domain': seed.domain,
                'tier': seed.metadata.get('tier', 1)
            },
            'description': 'Classification axis: where this seed belongs',
            'contains': [0]  # Contains dimension 0
        }

        # Dimension 2 (Plane): Definition + Meaning (semantic space)
        dimensions[2] = {
            'type': 'semantic_plane',
            'content': {
                'definition': seed.definition,
                'meaning': seed.meaning,
                'etymology': seed.etymology
            },
            'description': 'Semantic plane: what this seed means',
            'contains': [0, 1, '1b']  # Contains all lower dimensions
        }

        # Dimension 3 (Volume): Usage + Examples (application space)
        dimensions[3] = {
            'type': 'application_volume',
            'content': {
                'usage': seed.usage,
                'examples': seed.examples,
                'counterexamples': seed.counterexamples
            },
            'description': 'Application volume: how this seed is used',
            'contains': [0, 1, '1b', 2]  # Contains all lower dimensions
        }

        # Dimension 5 (5D): Relationships (connection space)
        dimensions[5] = {
            'type': 'connection_space',
            'content': {
                'relationships': seed.relationships,
                'related': seed.related,
                'synonyms': seed.synonyms,
                'antonyms': seed.antonyms
            },
            'description': 'Connection space: how this seed relates to others',
            'contains': [0, 1, '1b', 2, 3]  # Contains all lower dimensions
        }

        # Dimension 8 (8D): Expression (computational space)
        dimensions[8] = {
            'type': 'computational_space',
            'content': {
                'expression': seed.expression,
                'signature': seed.signature,
                'return_type': seed.return_type
            },
            'description': 'Computational space: how this seed computes',
            'contains': [0, 1, '1b', 2, 3, 5]  # Contains all lower dimensions
        }

        # Dimension 13 (13D): Metadata + Tags (context space)
        dimensions[13] = {
            'type': 'context_space',
            'content': {
                'metadata': seed.metadata,
                'tags': seed.tags,
                'extensions': seed.extensions,
                'compositions': seed.compositions,
                'transformations': seed.transformations
            },
            'description': 'Context space: additional context and growth paths',
            'contains': [0, 1, '1b', 2, 3, 5, 8]  # Contains all lower dimensions
        }

        # Dimension 21 (21D): Complete seed (whole object)
        dimensions[21] = {
            'type': 'complete_object',
            'content': seed,
            'description': 'Complete seed: the whole object in full dimensionality',
            'contains': [0, 1, '1b', 2, 3, 5, 8, 13]  # Contains ALL lower dimensions
        }

        return dimensions

    def get_dimension(self, dimensionalized: DimensionalizedSeed, level: int) -> Any:
        """
        Extract a specific dimension from a dimensionalized seed.

        Args:
            dimensionalized: The dimensionalized seed
            level: The Fibonacci level to extract

        Returns:
            Content at that dimensional level
        """
        return dimensionalized.dimensions.get(level)

    def get_parts(self, dimensionalized: DimensionalizedSeed, level: int) -> List[Any]:
        """
        Get all parts at a specific dimensional level.

        This implements the WHOLE_TO_PART relationship:
        Division of a dimension reveals its constituent parts.

        Args:
            dimensionalized: The dimensionalized seed
            level: The dimensional level to divide

        Returns:
            List of parts at that level
        """
        dimension = dimensionalized.dimensions.get(level)
        if not dimension:
            return []

        # Return the content as parts
        content = dimension['content']
        if isinstance(content, dict):
            return list(content.values())
        elif isinstance(content, list):
            return content
        else:
            return [content]

