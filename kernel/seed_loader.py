"""
Primitive Seed Loader

Loads primitive seeds from YAML/JSON files and creates dimensional primitives.

Seeds are complete knowledge packages containing:
- Definition (what it is)
- Usage (how it's used)
- Meaning (why it matters)
- Relationships (how it connects)
- Examples (concrete instances)
- Expression (computational form)
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import yaml
import json

from kernel.substrate import SubstrateIdentity
from kernel.relationships import Relationship, RelationshipSet, RelationshipType


class PrimitiveCategory(Enum):
    """Categories of dimensional primitives."""
    # Tier 1: Fundamental
    MATHEMATICAL_CONSTANT = "mathematical_constant"
    MATHEMATICAL_OPERATION = "mathematical_operation"
    PHYSICAL_CONSTANT = "physical_constant"
    DIMENSIONAL_STRUCTURE = "dimensional_structure"
    
    # Tier 2: Composite
    GEOMETRIC_SHAPE = "geometric_shape"
    PHYSICAL_LAW = "physical_law"
    MATHEMATICAL_FUNCTION = "mathematical_function"
    
    # Tier 3: Domain
    SENSORY_PERCEPTION = "sensory_perception"
    ECONOMIC_ACTION = "economic_action"
    LANGUAGE_ELEMENT = "language_element"
    COMPUTER_SCIENCE = "computer_science"
    
    # Tier 4: Emergent
    PHILOSOPHICAL_CONCEPT = "philosophical_concept"
    COMPLEX_BEHAVIOR = "complex_behavior"


@dataclass(frozen=True)
class PrimitiveSeed:
    """A seed is a complete knowledge package for a primitive."""
    
    # IDENTITY
    identity: SubstrateIdentity
    name: str
    category: PrimitiveCategory
    
    # KNOWLEDGE
    definition: str
    usage: List[str]
    meaning: str
    etymology: Optional[str] = None
    
    # COMPUTATIONAL
    expression: Optional[Callable] = None
    signature: str = ""
    return_type: str = "Any"
    
    # RELATIONAL
    relationships: RelationshipSet = field(default_factory=RelationshipSet)
    synonyms: List[str] = field(default_factory=list)
    antonyms: List[str] = field(default_factory=list)
    related: List[str] = field(default_factory=list)
    
    # EXAMPLES
    examples: List[Dict[str, Any]] = field(default_factory=list)
    counterexamples: List[Dict[str, Any]] = field(default_factory=list)
    
    # METADATA
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    domain: str = "general"
    
    # GROWTH
    extensions: List[str] = field(default_factory=list)
    compositions: List[str] = field(default_factory=list)
    transformations: List[str] = field(default_factory=list)


class SeedLoader:
    """Load primitive seeds from knowledge base."""
    
    def __init__(self, seed_directory: Path):
        """Initialize seed loader.
        
        Args:
            seed_directory: Root directory containing seed files
        """
        self.seed_directory = Path(seed_directory)
        self.loaded_seeds: Dict[str, PrimitiveSeed] = {}
        self.seed_index: Dict[str, Any] = {
            "by_name": {},
            "by_category": {},
            "by_domain": {},
            "by_tag": {}
        }
    
    def ingest_all(self) -> int:
        """Ingest all seeds from directory.
        
        Returns:
            Number of seeds loaded
        """
        count = 0
        
        # Load YAML files
        for seed_file in self.seed_directory.rglob("*.yaml"):
            try:
                self.ingest_seed_file(seed_file)
                count += 1
            except Exception as e:
                print(f"Error loading {seed_file}: {e}")
        
        # Load JSON files
        for seed_file in self.seed_directory.rglob("*.json"):
            try:
                self.ingest_seed_file(seed_file)
                count += 1
            except Exception as e:
                print(f"Error loading {seed_file}: {e}")
        
        return count
    
    def ingest_seed_file(self, filepath: Path) -> PrimitiveSeed:
        """Ingest a single seed file.
        
        Args:
            filepath: Path to seed file
            
        Returns:
            Loaded PrimitiveSeed
        """
        # 1. PARSE
        seed_data = self._parse_file(filepath)
        
        # 2. VALIDATE
        self._validate_seed(seed_data)
        
        # 3. INSTANTIATE
        seed = self._create_seed(seed_data)
        
        # 4. STORE
        self.loaded_seeds[seed.name] = seed
        
        # 5. INDEX
        self._index_seed(seed)

        return seed

    def _parse_file(self, filepath: Path) -> Dict[str, Any]:
        """Parse seed file (YAML or JSON).

        Args:
            filepath: Path to seed file

        Returns:
            Parsed seed data
        """
        if filepath.suffix == ".yaml" or filepath.suffix == ".yml":
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        elif filepath.suffix == ".json":
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}")

    def _validate_seed(self, seed_data: Dict[str, Any]) -> None:
        """Validate seed has required fields.

        Args:
            seed_data: Parsed seed data

        Raises:
            ValueError: If required field is missing
        """
        required = ["name", "category", "definition", "usage", "meaning"]
        for field in required:
            if field not in seed_data:
                raise ValueError(f"Missing required field: {field}")

    def _create_seed(self, seed_data: Dict[str, Any]) -> PrimitiveSeed:
        """Create PrimitiveSeed from data.

        Args:
            seed_data: Parsed seed data

        Returns:
            PrimitiveSeed instance
        """
        # Convert expression string to callable if present
        expression = None
        if "expression" in seed_data and seed_data["expression"]:
            try:
                # Safe evaluation of lambda expressions
                expression = eval(seed_data["expression"])
            except Exception as e:
                print(f"Warning: Could not evaluate expression for {seed_data['name']}: {e}")
                expression = None

        # Convert category string to enum
        try:
            category = PrimitiveCategory[seed_data["category"]]
        except KeyError:
            # Try by value
            category = PrimitiveCategory(seed_data["category"])

        # Create identity from name hash (ensure it fits in 64 bits)
        name_hash = hash(seed_data["name"]) & 0xFFFFFFFFFFFFFFFF  # Mask to 64 bits

        return PrimitiveSeed(
            identity=SubstrateIdentity(name_hash),
            name=seed_data["name"],
            category=category,
            definition=seed_data["definition"],
            usage=seed_data.get("usage", []),
            meaning=seed_data["meaning"],
            etymology=seed_data.get("etymology"),
            expression=expression,
            signature=seed_data.get("signature", ""),
            return_type=seed_data.get("return_type", "Any"),
            relationships=RelationshipSet(),  # Built in connect phase
            synonyms=seed_data.get("synonyms", []),
            antonyms=seed_data.get("antonyms", []),
            related=seed_data.get("related", []),
            examples=seed_data.get("examples", []),
            counterexamples=seed_data.get("counterexamples", []),
            metadata=seed_data.get("metadata", {}),
            tags=seed_data.get("tags", []),
            domain=seed_data.get("domain", "general"),
            extensions=seed_data.get("extensions", []),
            compositions=seed_data.get("compositions", []),
            transformations=seed_data.get("transformations", [])
        )

    def _index_seed(self, seed: PrimitiveSeed) -> None:
        """Index seed for fast lookup.

        Args:
            seed: PrimitiveSeed to index
        """
        # Index by name
        self.seed_index["by_name"][seed.name] = seed

        # Index by category
        category_key = seed.category.value
        if category_key not in self.seed_index["by_category"]:
            self.seed_index["by_category"][category_key] = []
        self.seed_index["by_category"][category_key].append(seed.name)

        # Index by domain
        if seed.domain not in self.seed_index["by_domain"]:
            self.seed_index["by_domain"][seed.domain] = []
        self.seed_index["by_domain"][seed.domain].append(seed.name)

        # Index by tags
        for tag in seed.tags:
            if tag not in self.seed_index["by_tag"]:
                self.seed_index["by_tag"][tag] = []
            self.seed_index["by_tag"][tag].append(seed.name)

    def connect_all(self) -> None:
        """Build relationships between all loaded seeds."""
        for seed in self.loaded_seeds.values():
            self._connect_seed(seed)

    def _connect_seed(self, seed: PrimitiveSeed) -> None:
        """Build relationships for a seed.

        Args:
            seed: PrimitiveSeed to connect
        """
        # Connect to related seeds
        for related_name in seed.related:
            if related_name in self.loaded_seeds:
                related_seed = self.loaded_seeds[related_name]
                relationship = Relationship(
                    identity=SubstrateIdentity(hash(f"{seed.name}->{related_name}")),
                    rel_type=RelationshipType.RELATED,
                    source=seed.identity,
                    target=related_seed.identity
                )
                seed.relationships.add(relationship)

    def search(self, query: str) -> List[PrimitiveSeed]:
        """Search seeds by name, definition, usage, or tags.

        Args:
            query: Search query string

        Returns:
            List of matching PrimitiveSeeds
        """
        results = []
        query_lower = query.lower()

        for seed in self.loaded_seeds.values():
            # Search in name
            if query_lower in seed.name.lower():
                if seed not in results:
                    results.append(seed)
                continue

            # Search in definition
            if query_lower in seed.definition.lower():
                if seed not in results:
                    results.append(seed)
                continue

            # Search in usage
            for usage in seed.usage:
                if query_lower in usage.lower():
                    if seed not in results:
                        results.append(seed)
                    break

            # Search in tags
            if query_lower in [tag.lower() for tag in seed.tags]:
                if seed not in results:
                    results.append(seed)

        return results

    def get_by_name(self, name: str) -> Optional[PrimitiveSeed]:
        """Get seed by name.

        Args:
            name: Primitive name

        Returns:
            PrimitiveSeed or None if not found
        """
        return self.seed_index["by_name"].get(name)

    def get_by_category(self, category: str) -> List[PrimitiveSeed]:
        """Get all seeds in a category.

        Args:
            category: Category name

        Returns:
            List of PrimitiveSeeds in category
        """
        seed_names = self.seed_index["by_category"].get(category, [])
        return [self.loaded_seeds[name] for name in seed_names]

    def get_by_domain(self, domain: str) -> List[PrimitiveSeed]:
        """Get all seeds in a domain.

        Args:
            domain: Domain name

        Returns:
            List of PrimitiveSeeds in domain
        """
        seed_names = self.seed_index["by_domain"].get(domain, [])
        return [self.loaded_seeds[name] for name in seed_names]

    def get_by_tag(self, tag: str) -> List[PrimitiveSeed]:
        """Get all seeds with a tag.

        Args:
            tag: Tag name

        Returns:
            List of PrimitiveSeeds with tag
        """
        seed_names = self.seed_index["by_tag"].get(tag, [])
        return [self.loaded_seeds[name] for name in seed_names]

    def stats(self) -> Dict[str, Any]:
        """Get statistics about loaded seeds.

        Returns:
            Dictionary of statistics
        """
        return {
            "total_seeds": len(self.loaded_seeds),
            "categories": len(self.seed_index["by_category"]),
            "domains": len(self.seed_index["by_domain"]),
            "tags": len(self.seed_index["by_tag"]),
            "category_counts": {
                cat: len(seeds)
                for cat, seeds in self.seed_index["by_category"].items()
            },
            "domain_counts": {
                dom: len(seeds)
                for dom, seeds in self.seed_index["by_domain"].items()
            }
        }

