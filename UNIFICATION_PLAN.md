# ButterflyFx Kernel/Core Unification Plan

## Critical Understanding

**Substrates are MATHEMATICAL EXPRESSIONS like `z = xy`, `z = xy²`, not data containers.**

The 64-bit identity is a **hash of the expression**, not the data.
Invocation reveals truth - nothing is stored.

See `SUBSTRATE_MATHEMATICS.md` for complete explanation.

## Problem
- Duplicate modules: `kernel` and `kernel_v2`, `core` and `core_v2`
- Confusion about which is canonical
- Need to optimize dimensional structure for real-life patterns
- Need to ensure kernel properly supports mathematical expressions

## Analysis

### Current State
```
butterflyfx/
├── kernel/          # Original kernel (used by tests)
├── kernel_v2/       # Duplicate kernel
├── core/            # Original core (used by tests)
├── core_v2/         # Duplicate core (used by DimensionOS)
```

### Test Results
- All 166 tests pass using `kernel` and `core` (not v2)
- DimensionOS uses `core_v2`
- This creates confusion and duplication

## Decision: Keep `kernel` and `core` as Canonical

**Rationale:**
1. Tests verify these implementations (166 tests passing)
2. Follows the architecture documented in ARCHITECTURE.md
3. Simpler names (no version suffix)
4. `kernel_v2` and `core_v2` appear to be experimental/duplicate

## Unification Steps

### Phase 1: Audit Differences
1. Compare `kernel` vs `kernel_v2` implementations
2. Compare `core` vs `core_v2` implementations
3. Identify any improvements in v2 that should be merged into canonical
4. Document any breaking changes

### Phase 2: Merge Improvements
1. Port any better implementations from v2 to canonical
2. Ensure dimensional structure follows spec:
   - 0D: x0 (identity)
   - 1D: x0 (name), x1, x2, ... (attributes)
   - 2D: y0 (rel name), y1 (rel type), y2, ... (rel attrs)
   - 3D: z0 (present), z1, z2, ... (delta attrs)
   - 4D+: m0, m1, m2, ... (higher dimension points)
3. Add SRL-based communication as primary interface

### Phase 3: Update DimensionOS
1. Change DimensionOS to import from `core` instead of `core_v2`
2. Update any API differences
3. Test that DimensionOS still works

### Phase 4: Remove Duplicates
1. Archive `kernel_v2` and `core_v2` (don't delete, move to archive/)
2. Update all imports
3. Run full test suite
4. Update documentation

### Phase 5: Optimize Dimensional Structure

#### Real-Life Pattern Mapping

**0D - Identity (The "Who")**
- x0: Unique 64-bit identity
- Like: Social Security Number, UUID, VIN
- Example: Person ID, Car VIN, Product SKU

**1D - Attributes (The "What")**
- x0: Name (primary identifier)
- x1, x2, x3: Scalar properties
- Like: Name, Age, Color, Price, Weight
- Example: 
  - Person: x0=name, x1=birth_timestamp, x2=height, x3=weight
  - Car: x0=model, x1=year, x2=mileage, x3=price

**2D - Relationships (The "With Whom")**
- y0: Relationship name
- y1: Relationship type (parent, child, owns, contains, etc.)
- y2, y3: Relationship metadata
- Like: Family tree, Org chart, Ownership, Dependencies
- Example:
  - Person→Person: y0="parent_of", y1="family", y2=since_date
  - Person→Car: y0="owns", y1="ownership", y2=purchase_date

**3D - State & Change (The "When & How")**
- z0: Current state/timestamp (the "now")
- z1, z2, z3: Change vectors (deltas)
- Like: Position, Velocity, Acceleration, State transitions
- Example:
  - Car: z0=current_location, z1=velocity, z2=acceleration
  - Account: z0=current_balance, z1=transaction_delta, z2=interest_rate

**4D+ - Behavior & Systems (The "Why & Context")**
- m0: Complete object in next dimension
- m1, m2: Higher-order patterns
- Like: Physics simulation, AI behavior, Market dynamics
- Example:
  - Car: m0=complete_car_with_physics, m1=traffic_behavior
  - Market: m0=complete_market_state, m1=trend_prediction

## Implementation Priority

1. ✅ Create DIMENSIONAL_STRUCTURE_SPEC.md (DONE)
2. ⏳ Audit kernel vs kernel_v2
3. ⏳ Audit core vs core_v2
4. ⏳ Merge improvements
5. ⏳ Update DimensionOS
6. ⏳ Remove duplicates
7. ⏳ Run full test suite
8. ⏳ Update documentation

## Success Criteria

- [ ] Only `kernel/` and `core/` exist (no v2)
- [ ] All 166 tests still pass
- [ ] DimensionOS works with canonical core
- [ ] Dimensional structure clearly documented
- [ ] SRL-based communication implemented
- [ ] Real-life pattern examples documented

