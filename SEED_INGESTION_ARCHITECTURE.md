# Seed Ingestion Architecture

**Date:** 2026-02-09  
**Status:** ACTIVE SYSTEM  
**Purpose:** Context-free knowledge available on demand

---

## EXECUTIVE SUMMARY

Seeds are **YAML files** that contain complete knowledge packages. They are **ingested** by the `SeedLoader` and transformed into **substrates** in the kernel.

**Key Insight:** Source code is human-readable/writable. Seeds are ingested and compiled into the runtime archive as substrates.

---

## THE SEED LIFECYCLE

```
YAML File → Parse → Validate → Create PrimitiveSeed → Index → Connect → Substrate
```

### 1. **YAML File** (Human-Readable)
- Complete knowledge package
- Definition, usage, meaning, relationships, examples
- Stored in `seeds/` directory hierarchy

### 2. **Parse** (`SeedLoader._parse_file()`)
- Read YAML/JSON file
- Convert to Python dict

### 3. **Validate** (`SeedLoader._validate_seed()`)
- Check required fields: name, category, definition, usage, meaning
- Ensure data integrity

### 4. **Create PrimitiveSeed** (`SeedLoader._create_seed()`)
- Convert to `PrimitiveSeed` dataclass
- Generate `SubstrateIdentity` from name hash (64-bit)
- Evaluate expression string to callable
- Convert category string to enum

### 5. **Index** (`SeedLoader._index_seed()`)
- Index by name, category, domain, tags
- Enable fast lookup and search

### 6. **Connect** (`SeedLoader.connect_all()`)
- Build relationships between seeds
- Create `Relationship` objects
- Form knowledge graph

### 7. **Substrate** (Runtime)
- Seed becomes a substrate with 64-bit identity
- Expression becomes invocable
- Knowledge available on demand

---

## SEED STRUCTURE

```yaml
name: DIVIDE
category: MATHEMATICAL_OPERATION
domain: mathematics

definition: Separate a whole into parts, creating dimensional structure

usage:
  - "Create dimensions from unity: 1 / 2 = [0.5, 0.5]"
  - "Partition resources: divide budget into categories"

meaning: |
  Division is the fundamental act of creating structure from unity.
  This is Law Two: "Observation Is Division."

etymology: |
  From Latin "dividere" meaning "to separate"

expression: "lambda whole: whole.divide()"
signature: "(Substrate) -> Tuple[List[Dimension], RelationshipSet]"
return_type: "Tuple[List[Dimension], RelationshipSet]"

relationships:
  - type: INVERSE
    target: MULTIPLY
    description: "Multiplication reverses division"

synonyms: [split, partition, separate]
antonyms: [multiply, unite, combine]
related: [DIMENSION, PART, WHOLE, MULTIPLY]

examples:
  - context: create_dimensions
    input: {whole: 1, parts: 2}
    output: [0.5, 0.5]
    formula: "1 / 2"

metadata:
  symbol: "/"
  operator_type: cross_dimensional
  creates_dimensions: true

tags: [mathematics, operation, dimensional, fundamental]
```

---

## DIRECTORY STRUCTURE

```
seeds/
├── tier1_fundamental/
│   ├── mathematics/
│   │   ├── constants/          # PI, E, PHI
│   │   └── operations/         # DIVIDE, MULTIPLY, ADD, SUBTRACT, MODULUS, POWER, ROOT
│   └── dimensional/
│       ├── core/               # UNITY, DIMENSION, OBSERVATION, MANIFESTATION, FIBONACCI
│       └── relationships/      # PART_TO_WHOLE, WHOLE_TO_PART, SIBLING, CONTAINMENT
├── tier2_composite/
├── tier3_domain/
│   ├── human_experience/
│   │   └── senses/             # SEE, HEAR, FEEL, TOUCH, TASTE
│   ├── language/
│   └── economics/
└── tier4_emergent/
    └── philosophy/
```

---

## INGESTION PROCESS

### Load All Seeds
```python
from kernel.seed_loader import SeedLoader
from pathlib import Path

# Initialize loader
loader = SeedLoader(Path("seeds"))

# Ingest all YAML/JSON files
count = loader.ingest_all()
print(f"Loaded {count} seeds")

# Build relationships
loader.connect_all()
```

### Query Seeds
```python
# By name
pi_seed = loader.get_by_name("PI")
value = pi_seed.expression()  # 3.141592653589793

# By category
constants = loader.get_by_category("mathematical_constant")

# By domain
math_seeds = loader.get_by_domain("mathematics")

# By tag
fundamental = loader.get_by_tag("fundamental")

# Search
results = loader.search("growth")
```

---

## SEED TO SUBSTRATE CONVERSION

### PrimitiveSeed Structure
```python
@dataclass(frozen=True)
class PrimitiveSeed:
    identity: SubstrateIdentity      # 64-bit hash of name
    name: str                         # Human-readable name
    category: PrimitiveCategory       # Tier 1-4 classification
    definition: str                   # What it is
    usage: List[str]                  # How it's used
    meaning: str                      # Why it matters
    expression: Callable              # Computational form
    relationships: RelationshipSet    # Connections
    examples: List[Dict]              # Concrete instances
    metadata: Dict                    # Additional properties
```

### Identity Generation
```python
# Create 64-bit identity from name hash
name_hash = hash(seed_data["name"]) & 0xFFFFFFFFFFFFFFFF
identity = SubstrateIdentity(name_hash)
```

### Expression Evaluation
```python
# Convert expression string to callable
expression = eval(seed_data["expression"])
# "lambda: 3.14159" → callable function
```

---

## CONTEXT-FREE KNOWLEDGE

Seeds are **context-free** - they contain complete knowledge without requiring external context.

**Available on demand:**
- Definition: What is it?
- Usage: How is it used?
- Meaning: Why does it matter?
- Relationships: How does it connect?
- Examples: Show me concrete instances
- Expression: Compute it

**No context needed:**
- Seeds are self-contained
- All information embedded
- Relationships explicit
- Examples included

---

## CURRENT SEED COUNT

**Tier 1 - Fundamental:**
- Mathematics/constants: 3 (PI, E, PHI)
- Mathematics/operations: 7 (DIVIDE, MULTIPLY, ADD, SUBTRACT, MODULUS, POWER, ROOT)

**Tier 3 - Domain:**
- Human experience/senses: 1 (SEE)

**Total: 11 seeds**

---

## NEXT STEPS

1. Create dimensional/core seeds: UNITY, DIMENSION, OBSERVATION, MANIFESTATION, FIBONACCI
2. Create dimensional/relationships seeds: PART_TO_WHOLE, WHOLE_TO_PART, SIBLING, CONTAINMENT
3. Expand tier 3 domain seeds: language, economics, computer science
4. Create tier 4 emergent seeds: philosophy, behaviors

---

**END OF DOCUMENT**

