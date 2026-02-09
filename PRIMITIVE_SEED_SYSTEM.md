# Primitive Seed System

**Version:** 1.0  
**Date:** 2026-02-09  
**Status:** KNOWLEDGE BASE ARCHITECTURE

---

## EXECUTIVE SUMMARY

**Core Insight:** Words are **SEEDS** to be ingested into DimensionOS as a knowledge base.

Each primitive is not just a function - it's a **complete knowledge package** containing:
1. **Definition** - What it is
2. **Usage** - How it's used
3. **Meaning** - Why it matters
4. **Relationships** - How it connects to other primitives
5. **Examples** - Concrete instances
6. **Expression** - Mathematical/computational form

This creates a **living knowledge base** that grows and evolves.

---

## THE SEED METAPHOR

A **seed** contains:
- **Genetic code** (definition, expression)
- **Nutrients** (usage, examples)
- **Growth potential** (relationships, extensions)
- **Reproduction** (can create new seeds)

When **ingested** (loaded into DimensionOS):
- Seeds **germinate** (instantiate as dimensional primitives)
- Seeds **grow** (develop relationships)
- Seeds **reproduce** (create derived concepts)
- Seeds **evolve** (learn from usage)

---

## SEED STRUCTURE

```python
@dataclass(frozen=True)
class PrimitiveSeed:
    """A seed is a complete knowledge package for a primitive."""
    
    # IDENTITY
    identity: SubstrateIdentity  # 64-bit unique ID
    name: str  # Human-readable name
    category: PrimitiveCategory  # Tier 1-4 classification
    
    # KNOWLEDGE
    definition: str  # What it is
    usage: List[str]  # How it's used (multiple contexts)
    meaning: str  # Why it matters (philosophical/practical)
    etymology: Optional[str]  # Word origin
    
    # COMPUTATIONAL
    expression: Callable  # Mathematical/computational function
    signature: str  # Function signature
    return_type: str  # What it returns
    
    # RELATIONAL
    relationships: RelationshipSet  # Connections to other primitives
    synonyms: List[str]  # Similar concepts
    antonyms: List[str]  # Opposite concepts
    related: List[str]  # Related concepts
    
    # EXAMPLES
    examples: List[Dict[str, Any]]  # Concrete usage examples
    counterexamples: List[Dict[str, Any]]  # What it's NOT
    
    # METADATA
    metadata: Dict[str, Any]  # Additional properties
    tags: List[str]  # Searchable tags
    domain: str  # Primary domain (math, physics, etc.)
    
    # GROWTH
    extensions: List[str]  # Derived concepts
    compositions: List[str]  # Can be combined with
    transformations: List[str]  # Can be transformed into
```

---

## EXAMPLE SEEDS

### Mathematical Seed: PI

```python
PI_SEED = PrimitiveSeed(
    # IDENTITY
    identity=SubstrateIdentity(hash("PI")),
    name="PI",
    category=PrimitiveCategory.MATHEMATICAL_CONSTANT,
    
    # KNOWLEDGE
    definition="The ratio of a circle's circumference to its diameter",
    usage=[
        "Calculate circle circumference: C = 2πr",
        "Calculate circle area: A = πr²",
        "Calculate sphere volume: V = (4/3)πr³",
        "Trigonometric functions: sin, cos, tan",
        "Fourier transforms",
        "Probability distributions"
    ],
    meaning="π represents the fundamental relationship between linear and circular dimensions. It appears throughout mathematics and physics as a bridge between straight and curved space.",
    etymology="Greek letter π (pi), from 'periphery' (περιφέρεια)",
    
    # COMPUTATIONAL
    expression=lambda: 3.141592653589793,
    signature="() -> float",
    return_type="float",
    
    # RELATIONAL
    relationships=RelationshipSet([
        Relationship(PART_TO_WHOLE, PI, CIRCLE),
        Relationship(DEPENDENCY, CIRCUMFERENCE, PI),
        Relationship(DEPENDENCY, AREA, PI),
        Relationship(RELATED, PI, E),
        Relationship(RELATED, PI, PHI)
    ]),
    synonyms=["π", "pi", "3.14159..."],
    antonyms=[],
    related=["CIRCLE", "RADIUS", "DIAMETER", "CIRCUMFERENCE", "E", "PHI", "GOLDEN_RATIO"],
    
    # EXAMPLES
    examples=[
        {"context": "circle_area", "input": {"radius": 5}, "output": 78.54, "formula": "πr²"},
        {"context": "circle_circumference", "input": {"radius": 5}, "output": 31.42, "formula": "2πr"},
        {"context": "euler_identity", "input": {}, "output": "e^(iπ) + 1 = 0", "formula": "e^(iπ) + 1 = 0"}
    ],
    counterexamples=[
        {"wrong": "π = 3.14", "correct": "π ≈ 3.14159265358979323846..."},
        {"wrong": "π is rational", "correct": "π is irrational (cannot be expressed as fraction)"}
    ],
    
    # METADATA
    metadata={
        "value": 3.141592653589793,
        "symbol": "π",
        "decimal_places": "infinite (irrational)",
        "discovered": "Ancient civilizations",
        "proven_irrational": "1768 (Johann Lambert)"
    },
    tags=["mathematics", "geometry", "constant", "irrational", "transcendental"],
    domain="mathematics",
    
    # GROWTH
    extensions=["TAU", "HALF_PI", "TWO_PI", "PI_SQUARED"],
    compositions=["RADIUS", "DIAMETER", "AREA", "VOLUME"],
    transformations=["RADIANS", "DEGREES", "EULER_IDENTITY"]
)
```

---

## SEED INGESTION PROCESS

### 1. PARSE
Read seed definition from various sources:
- JSON/YAML files
- Markdown documents
- Python code
- Natural language descriptions

### 2. VALIDATE
Check seed completeness:
- Required fields present
- Relationships valid
- Expression computable
- Examples executable

### 3. INSTANTIATE
Create dimensional primitive from seed:
- Generate 64-bit identity
- Compile expression
- Build relationship set
- Index for search

### 4. CONNECT
Link to existing primitives:
- Create relationships
- Update relationship sets
- Build knowledge graph

### 5. INDEX
Make searchable:
- By name
- By definition
- By usage
- By tags
- By domain
- By relationships

### 6. ACTIVATE
Make available for use:
- Export to kernel/core/interface
- Register in primitive registry
- Enable in API

---

## SEED STORAGE FORMATS

### Format 1: JSON Seed File

```json
{
  "name": "DIVIDE",
  "category": "MATHEMATICAL_OPERATION",
  "definition": "Separate a whole into parts, creating dimensional structure",
  "usage": [
    "Create dimensions from unity: 1 / 2 = [0.5, 0.5]",
    "Partition resources: divide budget into categories",
    "Decompose problems: divide and conquer algorithms"
  ],
  "meaning": "Division is the fundamental act of creating structure from unity. It is the birth of dimensional complexity.",
  "expression": "lambda whole: whole.divide()",
  "signature": "(Substrate) -> List[Dimension]",
  "return_type": "List[Dimension]",
  "relationships": [
    {"type": "INVERSE", "target": "MULTIPLY"},
    {"type": "CREATES", "target": "DIMENSION"},
    {"type": "OPPOSITE", "target": "UNITY"}
  ],
  "synonyms": ["split", "partition", "separate", "decompose"],
  "antonyms": ["multiply", "unite", "combine", "merge"],
  "related": ["DIMENSION", "PART", "WHOLE", "FRACTION"],
  "examples": [
    {
      "context": "create_dimensions",
      "input": {"whole": 1, "parts": 2},
      "output": [0.5, 0.5],
      "description": "Divide unity into two equal parts"
    }
  ],
  "tags": ["mathematics", "operation", "dimensional", "fundamental"],
  "domain": "mathematics"
}
```

### Format 2: YAML Seed File

```yaml
name: SEE
category: SENSORY_PERCEPTION
definition: Perceive visually through light entering the eye
usage:
  - "Observe distant objects: see the horizon"
  - "Detect motion: see movement"
  - "Recognize patterns: see faces"
  - "Navigate space: see obstacles"
  - "Understand context: see the big picture"
meaning: |
  Vision is the primary sense for spatial understanding and pattern recognition.
  "To see" is both literal (physical sight) and metaphorical (understanding).
  "As far as I could see" represents the limit of perception and knowledge.
etymology: "Old English 'seon', from Proto-Germanic 'sehwan'"
expression: |
  lambda observer, target, distance:
    distance <= observer.vision_range and
    not obscured(observer, target)
signature: "(Observer, Target, Distance) -> bool"
return_type: "bool"
relationships:
  - type: DEPENDENCY
    target: VISION
  - type: DEPENDENCY
    target: LIGHT
  - type: ATTRIBUTE
    target: DISTANCE
  - type: RELATED
    target: OBSERVE
synonyms: [view, look, watch, observe, perceive, behold, witness]
antonyms: [blind, overlook, miss, ignore]
related: [VISION, LOOK, WATCH, OBSERVE, GLANCE, STARE, GAZE, HORIZON, DISTANCE, VISIBLE]
examples:
  - context: visual_range
    input: {observer_range: 100, target_distance: 50}
    output: true
    description: "Target within visual range"
  - context: beyond_horizon
    input: {observer_range: 100, target_distance: 150}
    output: false
    description: "Target beyond visual range (as far as I could see)"
tags: [perception, vision, sense, spatial, awareness]
domain: human_experience
```

### Format 3: Markdown Seed File

```markdown
# FREEDOM

**Category:** PHILOSOPHICAL_CONCEPT
**Domain:** philosophy, politics, human_rights

## Definition
The state of being free from constraints, having the power to act, speak, or think without externally imposed restraints.

## Usage
- Political freedom: "freedom of speech, freedom of assembly"
- Personal autonomy: "freedom to choose one's path"
- Physical liberty: "freedom from captivity"
- Economic freedom: "freedom to trade, own property"
- Philosophical freedom: "free will vs determinism"

## Meaning
Freedom is the fundamental condition for human flourishing and dignity. It represents the capacity for self-determination and the absence of coercion. Freedom exists in tension with order, security, and responsibility.

## Etymology
Old English 'frēodōm', from 'frēo' (free) + '-dōm' (state/condition)

## Expression
```python
lambda entity: entity.constraints == [] and entity.autonomy == True
```

## Signature
`(Entity) -> bool`

## Relationships
- **OPPOSITE:** CAPTIVITY, SLAVERY, BONDAGE
- **RELATED:** LIBERTY, AUTONOMY, INDEPENDENCE, SOVEREIGNTY
- **REQUIRES:** RESPONSIBILITY, CHOICE, WILL
- **ENABLES:** CREATIVITY, GROWTH, SELF_DETERMINATION

## Synonyms
liberty, independence, autonomy, sovereignty, self-determination

## Antonyms
captivity, slavery, bondage, constraint, oppression

## Examples

### Political Freedom
```python
{
  "context": "democracy",
  "freedoms": ["speech", "assembly", "press", "religion"],
  "constraints": ["laws", "rights_of_others"],
  "balance": "maximum_freedom_compatible_with_order"
}
```

### Personal Freedom
```python
{
  "context": "individual",
  "freedoms": ["choice", "movement", "thought", "expression"],
  "constraints": ["physical_laws", "social_norms", "resources"],
  "balance": "autonomy_within_reality"
}
```

## Tags
philosophy, politics, human_rights, autonomy, liberty, ethics

## Extensions
- FREEDOM_OF_SPEECH
- FREEDOM_OF_ASSEMBLY
- FREEDOM_OF_RELIGION
- ECONOMIC_FREEDOM
- POLITICAL_FREEDOM
```

---

## SEED KNOWLEDGE BASE ARCHITECTURE

### Directory Structure

```
seeds/
├── tier1_fundamental/
│   ├── mathematics/
│   │   ├── constants/
│   │   │   ├── pi.yaml
│   │   │   ├── e.yaml
│   │   │   ├── phi.yaml
│   │   │   └── c.yaml
│   │   ├── operations/
│   │   │   ├── divide.yaml
│   │   │   ├── multiply.yaml
│   │   │   ├── add.yaml
│   │   │   └── subtract.yaml
│   │   └── structures/
│   │       ├── set.yaml
│   │       ├── map.yaml
│   │       └── graph.yaml
│   └── dimensional/
│       ├── relationships/
│       └── traversal/
├── tier2_composite/
│   ├── mathematics/
│   │   ├── calculus/
│   │   ├── linear_algebra/
│   │   └── trigonometry/
│   ├── physics/
│   │   ├── mechanics/
│   │   ├── quantum/
│   │   └── relativity/
│   └── geometry/
│       ├── shapes/
│       └── sacred_geometry/
├── tier3_domain/
│   ├── computer_science/
│   ├── chemistry/
│   ├── biology/
│   ├── human_experience/
│   │   ├── senses/
│   │   │   ├── see.yaml
│   │   │   ├── hear.yaml
│   │   │   └── touch.yaml
│   │   ├── emotions/
│   │   └── cognition/
│   ├── economics/
│   │   ├── invest.yaml
│   │   ├── stock_market.yaml
│   │   └── currency.yaml
│   └── language/
│       ├── instruction.yaml
│       ├── definition.yaml
│       └── meaning.yaml
└── tier4_emergent/
    ├── philosophy/
    │   ├── freedom.yaml
    │   ├── truth.yaml
    │   └── existence.yaml
    └── behaviors/
```

---

## SEED LOADER IMPLEMENTATION

```python
# kernel/seed_loader.py

from pathlib import Path
from typing import Dict, List, Any
import yaml
import json
from dataclasses import dataclass

class SeedLoader:
    """Load primitive seeds from knowledge base."""

    def __init__(self, seed_directory: Path):
        self.seed_directory = seed_directory
        self.loaded_seeds: Dict[str, PrimitiveSeed] = {}
        self.seed_index: Dict[str, List[str]] = {
            "by_name": {},
            "by_category": {},
            "by_domain": {},
            "by_tag": {}
        }

    def ingest_all(self) -> None:
        """Ingest all seeds from directory."""
        for seed_file in self.seed_directory.rglob("*.yaml"):
            self.ingest_seed_file(seed_file)
        for seed_file in self.seed_directory.rglob("*.json"):
            self.ingest_seed_file(seed_file)

    def ingest_seed_file(self, filepath: Path) -> PrimitiveSeed:
        """Ingest a single seed file."""
        # 1. PARSE
        seed_data = self._parse_file(filepath)

        # 2. VALIDATE
        self._validate_seed(seed_data)

        # 3. INSTANTIATE
        seed = self._create_seed(seed_data)

        # 4. CONNECT (deferred until all seeds loaded)
        self.loaded_seeds[seed.name] = seed

        # 5. INDEX
        self._index_seed(seed)

        return seed

    def _parse_file(self, filepath: Path) -> Dict[str, Any]:
        """Parse seed file (YAML or JSON)."""
        if filepath.suffix == ".yaml":
            with open(filepath) as f:
                return yaml.safe_load(f)
        elif filepath.suffix == ".json":
            with open(filepath) as f:
                return json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}")

    def _validate_seed(self, seed_data: Dict[str, Any]) -> None:
        """Validate seed has required fields."""
        required = ["name", "category", "definition", "usage", "meaning"]
        for field in required:
            if field not in seed_data:
                raise ValueError(f"Missing required field: {field}")

    def _create_seed(self, seed_data: Dict[str, Any]) -> PrimitiveSeed:
        """Create PrimitiveSeed from data."""
        # Convert expression string to callable
        expression = eval(seed_data.get("expression", "lambda: None"))

        return PrimitiveSeed(
            identity=SubstrateIdentity(hash(seed_data["name"])),
            name=seed_data["name"],
            category=PrimitiveCategory[seed_data["category"]],
            definition=seed_data["definition"],
            usage=seed_data["usage"],
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
        """Index seed for fast lookup."""
        self.seed_index["by_name"][seed.name] = seed

        if seed.category not in self.seed_index["by_category"]:
            self.seed_index["by_category"][seed.category] = []
        self.seed_index["by_category"][seed.category].append(seed.name)

        if seed.domain not in self.seed_index["by_domain"]:
            self.seed_index["by_domain"][seed.domain] = []
        self.seed_index["by_domain"][seed.domain].append(seed.name)

        for tag in seed.tags:
            if tag not in self.seed_index["by_tag"]:
                self.seed_index["by_tag"][tag] = []
            self.seed_index["by_tag"][tag].append(seed.name)

    def connect_all(self) -> None:
        """Build relationships between all loaded seeds."""
        for seed in self.loaded_seeds.values():
            self._connect_seed(seed)

    def _connect_seed(self, seed: PrimitiveSeed) -> None:
        """Build relationships for a seed."""
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
        """Search seeds by name, definition, usage, or tags."""
        results = []
        query_lower = query.lower()

        for seed in self.loaded_seeds.values():
            # Search in name
            if query_lower in seed.name.lower():
                results.append(seed)
                continue

            # Search in definition
            if query_lower in seed.definition.lower():
                results.append(seed)
                continue

            # Search in usage
            for usage in seed.usage:
                if query_lower in usage.lower():
                    results.append(seed)
                    break

            # Search in tags
            if query_lower in [tag.lower() for tag in seed.tags]:
                results.append(seed)

        return results
```

---

## USAGE EXAMPLE

```python
# Load all seeds from knowledge base
loader = SeedLoader(Path("seeds/"))
loader.ingest_all()
loader.connect_all()

# Search for vision-related primitives
vision_seeds = loader.search("see")
# Returns: [SEE, VISION, OBSERVE, VISIBLE, INVISIBLE, ...]

# Get specific seed
pi_seed = loader.seed_index["by_name"]["PI"]
print(pi_seed.definition)
# "The ratio of a circle's circumference to its diameter"

print(pi_seed.usage)
# ["Calculate circle circumference: C = 2πr", ...]

print(pi_seed.meaning)
# "π represents the fundamental relationship between linear and circular dimensions..."

# Use the seed's expression
result = pi_seed.expression()
# 3.141592653589793

# Find all mathematical constants
math_constants = loader.seed_index["by_category"][PrimitiveCategory.MATHEMATICAL_CONSTANT]
# ["PI", "E", "PHI", "C", ...]

# Find all economics primitives
econ_seeds = loader.seed_index["by_domain"]["economics"]
# ["INVEST", "STOCK_MARKET", "CURRENCY", "VALUE", ...]
```

---

## CONCLUSION

**Words are seeds.** Each primitive is a complete knowledge package containing:
- ✅ **Definition** - What it is
- ✅ **Usage** - How it's used
- ✅ **Meaning** - Why it matters
- ✅ **Relationships** - How it connects
- ✅ **Examples** - Concrete instances
- ✅ **Expression** - Computational form

This creates a **living knowledge base** that:
- Grows as new seeds are added
- Evolves as relationships deepen
- Learns from usage patterns
- Reproduces through extensions

**Next Steps:**
1. Create seed files for all 550+ primitives
2. Implement `SeedLoader` in `kernel/seed_loader.py`
3. Build seed knowledge base in `seeds/` directory
4. Create seed authoring tools
5. Enable natural language seed creation

---

**END OF PRIMITIVE SEED SYSTEM**


