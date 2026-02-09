"""
ButterflyFx Helper Functions - Human Readability & Comprehension

This module provides helper functions to make ButterflyFx:
- Human-readable
- Comprehensible
- Easy to use
- Robust

MODULES:
- builders: SubstrateBuilder pattern for fluent substrate creation
- query: DimensionalQuery DSL for navigating dimensional structures
- display: Pretty printing utilities for human-readable output
- inspect: Substrate inspection tools for understanding structure

CHARTER COMPLIANCE:
✅ Principle 1: Returns references, not copies
✅ Principle 2: Passive until invoked
✅ Principle 3: Immutable at runtime
✅ Principle 5: Pure functions only
✅ Principle 6: All relationships visible
"""

from .builders import (
    SubstrateBuilder,
    build_substrate,
    build_substrate_from_value,
    build_substrate_from_formula,
)

from .query import (
    DimensionalQuery,
    DIMENSION_NAMES,
    DIMENSION_INDEX_TO_NAME,
    DIMENSION_LEVEL_TO_NAME,
)

from .display import (
    pretty_substrate,
    pretty_dimension,
    pretty_dimensions,
    pretty_observation,
    pretty_observer,
    compact_substrate,
    compact_dimension,
)

from .inspect import (
    inspect_substrate,
    trace_division,
    analyze_expression,
    compare_substrates,
)


__all__ = [
    # Builders
    'SubstrateBuilder',
    'build_substrate',
    'build_substrate_from_value',
    'build_substrate_from_formula',
    
    # Query
    'DimensionalQuery',
    'DIMENSION_NAMES',
    'DIMENSION_INDEX_TO_NAME',
    'DIMENSION_LEVEL_TO_NAME',
    
    # Display
    'pretty_substrate',
    'pretty_dimension',
    'pretty_dimensions',
    'pretty_observation',
    'pretty_observer',
    'compact_substrate',
    'compact_dimension',
    
    # Inspect
    'inspect_substrate',
    'trace_division',
    'analyze_expression',
    'compare_substrates',
]

