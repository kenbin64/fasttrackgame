# Dimensional Programming Control Document

**Version:** 2.0  
**Date:** 2026-02-09  
**Status:** CANONICAL SPECIFICATION

---

## EXECUTIVE SUMMARY

This document defines the complete specification for **Dimensional Programming** in DimensionOS. It establishes how ALL operators, relationships, and dimensional entities interact according to the Seven Dimensional Laws and the Dimensional Safety Charter.

**Core Principle:** "Sometimes points are just points if we do not go deeper."

---

## 1. FOUNDATIONAL PHILOSOPHY

### 1.1 Dimensional Identity

Every entity in DimensionOS has:
- **64-bit Identity** - Unique, immutable, bitwise (not numeric)
- **Dimensional Level** - Position in Fibonacci hierarchy (0, 1, 1, 2, 3, 5, 8, 13, 21)
- **Relational Set** - All relationships this entity participates in: `Rel(A) = {all relationships A participates in}`
- **Expression** - Mathematical function that manifests value when invoked

### 1.2 The Dimensional Relationship Law

**CRITICAL INSIGHT:** A relationship is NOT metadata or a pointer. It is a **first-class dimensional entity**.

A relationship is a **mapping from one dimension to another**: `A → B`

This mapping is itself a dimension with its own structure.

**A relationship has:**
- **Identity** - 64-bit unique identifier
- **Attributes** - Properties of the relationship itself
- **Direction** - Whole→Part, Part→Whole, Sibling, Dependency, etc.
- **Constraints** - Rules governing the relationship
- **Reversibility** - Can create inverse relationship (B → A)
- **Lineage** - Inheritance chain from source dimension

**Every dimension has a relationship set:**
```
Rel(A) = {all relationships A participates in}
```

Operators act on these sets using set theory:
- **AND** = intersection
- **OR** = union
- **NOT** = complement
- **XOR** = symmetric difference

This makes dimensional programming **set-theoretic and algebraic**.

### 1.3 Two Categories of Operations

**CROSS-DIMENSIONAL OPERATORS** - Change dimensional structure:
- Create new dimensions
- Collapse dimensions
- Generate new relationships
- Modify dimensional hierarchy
- Examples: `/`, `*`, `%`, `**`, `√`

**INTRA-DIMENSIONAL OPERATORS** - Work within structure:
- Manipulate points/values
- Filter relationship sets
- Compare entities
- Preserve dimensional level
- Examples: `+`, `-`, `AND`, `OR`, `==`, `<`, `&`, `|`

---

## 2. OPERATOR SPECIFICATIONS

### 2.1 DIVISION (/) - Creates New Relationships

**Type:** Cross-Dimensional
**Effect:** Creates dimensional plurality AND relational structure

**The Relationship Law:**
> "Division is the birth of relational structure."

When you divide `Whole / n`, you create:
- **Part-to-Whole relationships** - Each part knows its parent
- **Sibling relationships** - Parts know each other
- **Ordering relationships** - Sequential position in division
- **Containment relationships** - Spatial/logical containment

**Dimensional Semantics:**
- Divides unity into 9 Fibonacci dimensions
- Each part inherits the whole (Law 3)
- Creates dimensional depth (observation is division - Law 2)

**Relational Semantics:**
- **Part→Whole:** Each child dimension knows its parent
- **Whole→Part:** Parent dimension knows all children
- **Sibling:** All children know each other (horizontal relationships)
- **Containment:** Spatial/logical containment relationship
- **Ordering:** Sequential position (1st, 2nd, 3rd, etc.)
- **Lineage:** Inheritance chain preserved

**Code Signature:**
```python
def cross_divide(whole: Substrate) -> Tuple[List[Dimension], RelationshipSet]:
    """
    Divide whole into parts, creating dimensional and relational structure.

    Division is the BIRTH of relational structure.

    Returns:
        (dimensions, relationships) where relationships include:
        - PART_TO_WHOLE: Each part → whole mapping
        - WHOLE_TO_PART: Whole → all parts mapping
        - SIBLING: Part ↔ part mappings (horizontal)
        - CONTAINMENT: Spatial containment graph
        - ORDERING: Sequential position relationships
    """
```

**Reversibility:** Multiplication can restore unity (Law 7, Law 9)

---

### 2.2 MULTIPLICATION (*) - Collapses Relationships

**Type:** Cross-Dimensional
**Effect:** Recombines parts into unity, collapses horizontal relationships

**The Relationship Law:**
> "Multiplication severs horizontal relationships but preserves vertical lineage."

When you multiply parts together, you:
- **Collapse sibling relationships** - Parts no longer relate horizontally
- **Collapse part-to-part relationships** - Direct peer connections severed
- **Preserve part-to-whole lineage** - Vertical ancestry maintained
- **Restore unity** - Return to common origin

**Dimensional Semantics:**
- Recombines parts back to unity
- Collapses horizontal relationships
- Returns to higher dimensional level

**Relational Semantics:**
- **Horizontal Collapse:** Sibling relationships dissolved
- **Vertical Preservation:** Part→Whole lineage maintained
- **Unity Restoration:** All parts recognize common origin
- **Lineage Tracking:** Maintains history of division/multiplication

**Code Signature:**
```python
def cross_multiply(parts: List[Dimension], preserve_lineage: bool = True) -> Tuple[Substrate, RelationshipSet]:
    """
    Recombine parts into unity, collapsing horizontal relationships.

    Multiplication SEVERS horizontal relationships but PRESERVES vertical lineage.

    Args:
        parts: Dimensional parts to recombine
        preserve_lineage: Keep vertical part→whole relationships

    Returns:
        (unified_substrate, preserved_relationships) where:
        - Sibling relationships are SEVERED
        - Part→Whole lineage is PRESERVED
        - Unity is RESTORED
    """
```

**Reversibility:** Division can recreate parts (Law 9)

---

### 2.3 ADDITION (+) - Adds Relationships Within a Dimension

**Type:** Intra-Dimensional
**Effect:** Expands content, creates intra-dimensional relationships

**The Relationship Law:**
> "Addition creates intra-dimensional relationships."

When you add `A + B`, you create:
- **New attribute relationships** - B becomes attribute of A
- **New adjacency relationships** - Spatial/temporal proximity
- **New dependency relationships** - Dependencies between content

**Example:**
Adding gas to an engine creates a `fuel → combustion` relationship.

**Dimensional Semantics:**
- Stays within current dimensional level
- Expands magnitude without changing structure
- Like adding gas to an engine or width to length

**Relational Semantics:**
- **Attribute Relationships:** New attributes added to entity
- **Dependency Relationships:** Dependencies between added content
- **Adjacency Relationships:** Spatial/temporal adjacency
- **Aggregation Relationships:** Collection membership

**Code Signature:**
```python
def intra_add(x: DimensionalEntity, y: DimensionalEntity) -> Tuple[DimensionalEntity, RelationshipSet]:
    """
    Add content within dimension, creating intra-dimensional relationships.

    Addition creates INTRA-DIMENSIONAL relationships (within the same level).

    Returns:
        (expanded_entity, new_relationships) where relationships include:
        - ATTRIBUTE: New attribute relationships
        - DEPENDENCY: Content dependencies
        - ADJACENCY: Spatial/temporal adjacency
        - AGGREGATION: Collection membership
    """
```

**Reversibility:** Subtraction removes content (Law 9)

---

### 2.4 SUBTRACTION (-) - Removes Relationships Within a Dimension

**Type:** Intra-Dimensional
**Effect:** Contracts content, severs intra-dimensional relationships

**The Relationship Law:**
> "Subtraction severs intra-dimensional relationships."

When you subtract `A - B`, you sever:
- **Dependencies** - Breaks dependency relationships
- **Attributes** - Removes attribute relationships
- **Adjacency** - Updates spatial/temporal adjacency
- **Internal structure** - Removes structural relationships

**Example:**
Subtracting rubber from a tire removes the `rubber → traction` relationship.

**Dimensional Semantics:**
- Stays within current dimensional level
- Contracts magnitude without changing structure
- Like removing rubber from a tire

**Relational Semantics:**
- **Relationship Severance:** Breaks relationships to removed content
- **Dependency Cleanup:** Removes dependent relationships
- **Adjacency Update:** Updates spatial/temporal adjacency
- **Attribute Removal:** Removes attribute relationships

**Code Signature:**
```python
def intra_subtract(x: DimensionalEntity, y: DimensionalEntity) -> Tuple[DimensionalEntity, RelationshipSet]:
    """
    Remove content within dimension, severing relationships.

    Subtraction SEVERS intra-dimensional relationships.

    Returns:
        (contracted_entity, severed_relationships) where:
        - DEPENDENCY relationships are SEVERED
        - ATTRIBUTE relationships are REMOVED
        - ADJACENCY relationships are UPDATED
    """
```

**Reversibility:** Addition restores content (Law 9)

---

### 2.5 MODULUS (%) - Reveals Residual Relationships

**Type:** Cross-Dimensional
**Effect:** Produces residue and residual relationships

**The Relationship Law:**
> "Modulus exposes the residual identity that cannot be expressed in the target dimension."

When you compute `A % B`, the residue is:
- **A relationship seed** - Seeds next dimensional level
- **A boundary condition** - Defines dimensional boundaries
- **A cycle origin** - Marks where cycles begin
- **A recursion driver** - Drives Fibonacci-like growth

**Dimensional Semantics:**
- Returns unexpressed identity
- Seeds next dimensional recursion
- Drives Fibonacci-like growth
- Creates the next relationship in a sequence

**Relational Semantics:**
- **Boundary Relationships:** Defines dimensional boundaries
- **Cycle Relationships:** Marks cycle origins
- **Recursion Seeds:** Relationships that trigger next level
- **Residual Lineage:** Inheritance from unexpressed identity

**Code Signature:**
```python
def cross_modulus(
    substrate: Substrate,
    dimension_modulus: int
) -> Tuple[int, DimensionalResidue, RelationshipSet]:
    """
    Compute dimensional residue and residual relationships.

    Modulus creates the NEXT relationship in a sequence (Fibonacci-like).

    Returns:
        (expressed_value, residue, residual_relationships) where:
        - expressed_value: What CAN be expressed in this dimension
        - residue: What CANNOT be expressed (seeds next dimension)
        - residual_relationships: BOUNDARY, CYCLE, RECURSION, LINEAGE
    """
```

---

### 2.6 POWER (**) - Dimensional Stacking

**Type:** Cross-Dimensional
**Effect:** Creates higher-order dimensional spaces

**Dimensional Semantics:**
- x^1 = length (1D)
- x^2 = area (2D)
- x^3 = volume (3D)
- Recursive multiplication creates dimensional layers

**Relational Semantics:**
- **Projection Relationships:** Lower dimension → higher dimension
- **Embedding Relationships:** How lower fits into higher
- **Orthogonal Relationships:** Independent dimensional axes

**Code Signature:**
```python
def cross_power(base: Dimension, exponent: int) -> Tuple[Dimension, RelationshipSet]:
    """
    Stack dimensions to create higher-order space.

    Returns:
        (higher_dimension, projection_relationships)
    """
```

---

### 2.7 ROOT (√) - Dimensional Reduction

**Type:** Cross-Dimensional
**Effect:** Reduces dimensional order

**Dimensional Semantics:**
- √(area) = length (2D → 1D)
- ∛(volume) = length (3D → 1D)
- Inverse of power operation

**Relational Semantics:**
- **Extraction Relationships:** Higher dimension → lower dimension
- **Projection Relationships:** Dimensional collapse mapping
- **Lineage Preservation:** Maintains origin tracking

**Code Signature:**
```python
def cross_root(higher_dimension: Dimension, degree: int) -> Tuple[Dimension, RelationshipSet]:
    """
    Reduce dimensional order, preserving lineage.

    Returns:
        (lower_dimension, extraction_relationships)
    """
```

---

## 3. LOGICAL OPERATORS (Relationship Set Operations)

### 3.1 AND (&&) - Relationship Set Intersection

**Type:** Intra-Dimensional
**Effect:** Intersection of relationship sets

**Relational Semantics:**
- Returns relationships common to BOTH sets
- Filters to shared connections
- Preserves only mutual relationships

**Code Signature:**
```python
def intra_and(rel_set_a: RelationshipSet, rel_set_b: RelationshipSet) -> RelationshipSet:
    """
    Intersection of relationship sets.

    Returns relationships that exist in BOTH sets.
    """
```

**Example:**
```python
# Find entities related to BOTH parent1 AND parent2
common_children = parent1.relationships && parent2.relationships
```

---

### 3.2 OR (||) - Relationship Set Union

**Type:** Intra-Dimensional
**Effect:** Union of relationship sets

**Relational Semantics:**
- Returns relationships from EITHER set
- Expands to all connections
- Combines relationship sets

**Code Signature:**
```python
def intra_or(rel_set_a: RelationshipSet, rel_set_b: RelationshipSet) -> RelationshipSet:
    """
    Union of relationship sets.

    Returns relationships that exist in EITHER set.
    """
```

---

### 3.3 NOT (!) - Relationship Set Complement

**Type:** Intra-Dimensional
**Effect:** Removal of relationships

**Relational Semantics:**
- Returns relationships NOT in the set
- Inverts relationship selection
- Severs specified connections

**Code Signature:**
```python
def intra_not(rel_set: RelationshipSet, universe: RelationshipSet) -> RelationshipSet:
    """
    Complement of relationship set within universe.

    Returns relationships in universe but NOT in rel_set.
    """
```

---

### 3.4 XOR (⊕) - Divergent Relationship Sets

**Type:** Intra-Dimensional
**Effect:** Symmetric difference of relationship sets

**Relational Semantics:**
- Returns relationships in ONE set but not BOTH
- Identifies divergent connections
- Highlights differences

**Code Signature:**
```python
def intra_xor(rel_set_a: RelationshipSet, rel_set_b: RelationshipSet) -> RelationshipSet:
    """
    Symmetric difference of relationship sets.

    Returns relationships in EITHER set but NOT both.
    """
```

---

## 4. COMPARISON OPERATORS (Dimensional Hierarchy)

### 4.1 LESS THAN (<) - Containment

**Type:** Intra-Dimensional
**Effect:** Tests if left is contained within right

**Relational Semantics:**
- Left is a LOWER dimension contained in right
- Part < Whole relationship
- Child < Parent in hierarchy

**Code Signature:**
```python
def intra_less_than(left: Dimension, right: Dimension) -> bool:
    """
    Test if left is contained within right (lower dimension).

    Returns True if left is a part of right.
    """
```

**Example:**
```python
# Is this dimension a part of the whole?
if part < whole:
    # part is contained within whole
```

---

### 4.2 GREATER THAN (>) - Containment (Inverse)

**Type:** Intra-Dimensional
**Effect:** Tests if left contains right

**Relational Semantics:**
- Left is a HIGHER dimension containing right
- Whole > Part relationship
- Parent > Child in hierarchy

**Code Signature:**
```python
def intra_greater_than(left: Dimension, right: Dimension) -> bool:
    """
    Test if left contains right (higher dimension).

    Returns True if left contains right as a part.
    """
```

---

### 4.3 EQUALITY (==) - Dimensional and Relational Identity

**Type:** Intra-Dimensional
**Effect:** Tests same dimensional and relational identity

**Relational Semantics:**
- Same 64-bit identity
- Same dimensional level
- Same relational set (or equivalent)

**Code Signature:**
```python
def intra_equal(left: Dimension, right: Dimension) -> bool:
    """
    Test if left and right have same dimensional and relational identity.
    """
```

---

## 5. TRAVERSAL OPERATORS

### 5.1 DOT (.) - Dimensional Descent

**Type:** Traversal
**Effect:** Access lower dimension or attribute

**Relational Semantics:**
- Follows Whole→Part relationship
- Descends dimensional hierarchy
- Accesses contained entity

**Code Signature:**
```python
def dimensional_descent(whole: Dimension, part_name: str) -> Dimension:
    """
    Descend from whole to named part.

    Follows whole→part relationship.
    """
```

**Example:**
```python
# Access a part of the whole
child = parent.child_dimension
```

---

### 5.2 ARROW (→, =>) - Dimensional Ascent

**Type:** Traversal
**Effect:** Project into higher dimension

**Relational Semantics:**
- Follows Part→Whole relationship
- Ascends dimensional hierarchy
- Projects to containing entity

**Code Signature:**
```python
def dimensional_ascent(part: Dimension) -> Dimension:
    """
    Ascend from part to containing whole.

    Follows part→whole relationship.
    """
```

**Example:**
```python
# Project to containing whole
parent = child => whole
```

---

## 6. BITWISE OPERATORS (Identity Manipulation)

All bitwise operators are **INTRA-DIMENSIONAL** - they manipulate the 64-bit identity pattern without changing dimensional structure.

### 6.1 Bitwise AND (&) - Identity Masking
- Filters bits within identity
- Use for: Masking, extracting bit patterns

### 6.2 Bitwise OR (|) - Identity Merging
- Combines bit patterns
- Use for: Setting flags, combining patterns

### 6.3 Bitwise XOR (^) - Identity Toggling
- Toggles bits
- Use for: Encryption, checksums

### 6.4 Bitwise NOT (~) - Identity Inversion
- Inverts all bits
- Use for: Complement, inversion

### 6.5 Shifts (<<, >>) - HYBRID
- Can be dimensional (scaling) or intra-dimensional (bit packing)
- Context determines interpretation

---

## 7. RELATIONSHIP TYPES

### 7.1 Structural Relationships (Created by Division)
- **Part→Whole:** Child knows parent
- **Whole→Part:** Parent knows children
- **Sibling:** Peer relationships
- **Containment:** Spatial/logical containment

### 7.2 Operational Relationships (Created by Addition)
- **Attribute:** Entity has attribute
- **Dependency:** Entity depends on entity
- **Adjacency:** Spatial/temporal proximity
- **Aggregation:** Collection membership

### 7.3 Residual Relationships (Created by Modulus)
- **Boundary:** Dimensional boundary conditions
- **Cycle:** Cycle origin markers
- **Recursion:** Recursion seeds
- **Lineage:** Unexpressed identity inheritance

### 7.4 Projection Relationships (Created by Power/Root)
- **Embedding:** Lower dimension in higher
- **Extraction:** Higher dimension to lower
- **Orthogonal:** Independent axes

---

## 8. IMPLEMENTATION RULES

### 8.1 Immutability
- All operations return NEW entities
- Original entities never modified
- Relationships are immutable once created

### 8.2 Reversibility (Redemption Equation)
- Every operation must have an inverse
- T⁻¹(T(x)) = x for all transformations
- Relationship lineage preserved through transformations

### 8.3 Relationship Tracking
- Every operation returns (result, relationships)
- Relationships are first-class return values
- Relationship sets are queryable

### 8.4 64-Bit Identity
- All entities have 64-bit identity
- Identity is bitwise, not numeric
- Identity preserved through transformations

### 8.5 Fibonacci Bounds
- Maximum 9 dimensional levels (0, 1, 1, 2, 3, 5, 8, 13, 21)
- Growth follows Fibonacci sequence
- Prevents exponential explosion

---

## 9. CODE GENERATION GUIDELINES

### 9.1 Naming Conventions
- Use dimensional/relational names, not numeric
- Prefer: `whole`, `part`, `residue`, `projection`, `intersection`
- Avoid: `value`, `number`, `data`, `item`

### 9.2 Comments and Documentation
- Explain dimensional and relational semantics
- Document relationship creation/modification
- Describe dimensional level changes

### 9.3 Function Signatures
- Return tuples: `(result, relationships)`
- Accept relationship sets as parameters
- Make dimensional intent explicit

### 9.4 Type Annotations
```python
from typing import Tuple

def operation(
    entity: DimensionalEntity,
    relationships: RelationshipSet
) -> Tuple[DimensionalEntity, RelationshipSet]:
    """
    Dimensional operation with relationship tracking.
    """
```

---

## 10. COMPLIANCE CHECKLIST

Every dimensional operation MUST:

- [ ] Respect the Seven Dimensional Laws
- [ ] Follow the Dimensional Safety Charter
- [ ] Return (result, relationships) tuple
- [ ] Preserve 64-bit identity bounds
- [ ] Maintain immutability
- [ ] Provide reversibility
- [ ] Track relationship changes
- [ ] Document dimensional semantics
- [ ] Use relational naming
- [ ] Stay within Fibonacci bounds

---

## 11. EXAMPLES

### Example 1: Division Creates Relationships
```python
# Divide whole into parts
whole = Substrate(identity=42)
parts, relationships = cross_divide(whole)

# Relationships created:
# - part_to_whole: Each part knows its parent
# - whole_to_part: Parent knows all children
# - sibling: Children know each other
# - containment: Spatial containment graph

# Query relationships
parent = relationships.part_to_whole[parts[0]]
children = relationships.whole_to_part[whole]
siblings = relationships.sibling[parts[0]]
```

### Example 2: Addition Creates Intra-Dimensional Relationships
```python
# Add content within dimension (like adding gas to engine)
engine = DimensionalEntity(identity=100, content={"gas": 10})
gas_added = DimensionalEntity(identity=101, content={"gas": 5})

expanded_engine, new_relationships = intra_add(engine, gas_added)

# Relationships created:
# - attribute: gas_added is attribute of engine
# - dependency: engine depends on gas_added
# - adjacency: spatial/temporal adjacency

# expanded_engine.content = {"gas": 15}
# new_relationships.attributes = [gas_added]
```

### Example 3: Logical Operators on Relationship Sets
```python
# Find entities related to BOTH parent1 AND parent2
parent1_rels = parent1.get_relationships()
parent2_rels = parent2.get_relationships()

# Intersection (AND)
common_children = intra_and(parent1_rels, parent2_rels)

# Union (OR)
all_children = intra_or(parent1_rels, parent2_rels)

# Symmetric difference (XOR)
unique_children = intra_xor(parent1_rels, parent2_rels)
```

---

## 12. CONCLUSION

This control document establishes dimensional programming as a complete paradigm where:

1. **Relationships are first-class dimensions**
2. **Operators work on dimensions AND relationships**
3. **Cross-dimensional operators change structure**
4. **Intra-dimensional operators work within structure**
5. **All operations are reversible and trackable**

**Philosophy:** "Sometimes points are just points if we do not go deeper."

This means we can work at any dimensional level without forcing deeper decomposition. Intra-dimensional operators let us manipulate content without creating new dimensions.

**Status:** This document is the CANONICAL specification for all dimensional programming in DimensionOS.

---

**END OF CONTROL DOCUMENT**


