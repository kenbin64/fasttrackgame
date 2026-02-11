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
from typing import Dict, List, Any, Optional, Callable, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import yaml
import json

from kernel.substrate import SubstrateIdentity
from kernel.relationships import Relationship, RelationshipSet, RelationshipType
from kernel.seed_validator import SeedValidator, SeedValidationError
from kernel.seed_types import PrimitiveSeed, PrimitiveCategory

# Avoid circular import - import at runtime when needed
if TYPE_CHECKING:
    from kernel.seed_dimensionalizer import SeedDimensionalizer, DimensionalizedSeed


class SeedLoader:
    """Load primitive seeds from knowledge base."""

    def __init__(self, seed_directory: Path):
        """Initialize seed loader.

        Args:
            seed_directory: Root directory containing seed files
        """
        self.seed_directory = Path(seed_directory)
        self.validator = SeedValidator()  # Security-first validator
        self._dimensionalizer = None  # Lazy-loaded to avoid circular import
        self.loaded_seeds: Dict[str, PrimitiveSeed] = {}
        self.dimensionalized_seeds: Dict[str, Any] = {}  # Dimensional substrates
        self.seed_index: Dict[str, Any] = {
            "by_name": {},
            "by_category": {},
            "by_domain": {},
            "by_tag": {}
        }

    @property
    def dimensionalizer(self):
        """Lazy-load dimensionalizer to avoid circular import."""
        if self._dimensionalizer is None:
            from kernel.seed_dimensionalizer import SeedDimensionalizer
            self._dimensionalizer = SeedDimensionalizer()
        return self._dimensionalizer
    
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
        """Ingest a single seed file with comprehensive security validation.

        Args:
            filepath: Path to seed file

        Returns:
            Loaded PrimitiveSeed

        Raises:
            SeedValidationError: If seed validation fails
        """
        # 0. VALIDATE FILE (security check)
        try:
            self.validator.validate_file(filepath)
        except SeedValidationError as e:
            raise ValueError(f"File validation failed for {filepath}: {e}")

        # 1. PARSE
        seed_data = self._parse_file(filepath)

        # 2. VALIDATE SEED DATA (comprehensive security validation)
        self._validate_seed(seed_data)

        # 3. INSTANTIATE
        seed = self._create_seed(seed_data)

        # 4. DIMENSIONALIZE (convert to substrate - Russian Dolls principle)
        dimensionalized = self.dimensionalizer.dimensionalize(seed)

        # 5. STORE (both flat and dimensional forms)
        self.loaded_seeds[seed.name] = seed
        self.dimensionalized_seeds[seed.name] = dimensionalized

        # 6. INDEX
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
        """Validate seed comprehensively (security-first).

        Args:
            seed_data: Parsed seed data

        Raises:
            ValueError: If validation fails
        """
        try:
            # Use comprehensive security-first validator
            self.validator.validate_seed(seed_data)
        except SeedValidationError as e:
            raise ValueError(f"Seed validation failed: {e}")

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

    def get_dimensionalized(self, name: str) -> Optional[Any]:
        """
        Get dimensionalized seed by name.

        Returns the seed as a dimensional substrate with hierarchical structure.

        Args:
            name: Seed name

        Returns:
            DimensionalizedSeed or None if not found
        """
        return self.dimensionalized_seeds.get(name)

    def get_dimension(self, name: str, level: int) -> Any:
        """
        Get a specific dimension of a seed.

        Args:
            name: Seed name
            level: Fibonacci dimensional level (0, 1, 2, 3, 5, 8, 13, 21)

        Returns:
            Content at that dimensional level, or None if not found
        """
        dimensionalized = self.dimensionalized_seeds.get(name)
        if not dimensionalized:
            return None

        return self.dimensionalizer.get_dimension(dimensionalized, level)

    def get_parts(self, name: str, level: int) -> List[Any]:
        """
        Get parts of a seed at a specific dimensional level.

        Implements WHOLE_TO_PART relationship: division reveals parts.

        Args:
            name: Seed name
            level: Dimensional level to divide

        Returns:
            List of parts at that level
        """
        dimensionalized = self.dimensionalized_seeds.get(name)
        if not dimensionalized:
            return []

        return self.dimensionalizer.get_parts(dimensionalized, level)

    def stats(self) -> Dict[str, Any]:
        """Get statistics about loaded seeds.

        Returns:
            Dictionary of statistics
        """
        return {
            "total_seeds": len(self.loaded_seeds),
            "dimensionalized_seeds": len(self.dimensionalized_seeds),
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

