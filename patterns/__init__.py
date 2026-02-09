"""
Dimensional Design Patterns - Charter-Compliant Pattern Library

This package provides design patterns adapted for dimensional programming:

1. **Factory Pattern** (`factory.py`)
   - SubstrateFactory - Create substrates from templates
   - SRL-based substrate creation
   - Convenience functions for common patterns

2. **Strategy Pattern** (`strategy.py`)
   - ObservationStrategy - Lens as interchangeable strategy
   - Multiple observation strategies for same substrate
   - Strategy selection based on criteria

3. **Decorator Pattern** (`decorator.py`)
   - SubstrateDecorator - Delta as behavior decorator
   - Chainable decorators
   - Common decorators: Add, Multiply, Modulo, Clamp

4. **Iterator Pattern** (`iterator.py`)
   - DimensionalIterator - Iterate through dimensions
   - SubstrateSequenceIterator - Iterate through substrates
   - Lazy evaluation

5. **Composite Pattern** (`composite.py`)
   - CompositeSubstrate - Hierarchical substrate structures
   - Uniform interface for leaf and composite
   - Tree operations: map, count, aggregate

All patterns comply with the Dimensional Safety Charter and align with
the Seven Dimensional Laws.

CHARTER COMPLIANCE:
✅ Principle 1: All Things Are by Reference
✅ Principle 2: Passive Until Invoked
✅ Principle 3: No Self-Modifying Code
✅ Principle 5: No Hacking Surface
✅ Principle 7: Fibonacci-Bounded Growth

LAW ALIGNMENT:
- Law 1: Universal Substrate Law
- Law 2: Observation Is Division
- Law 3: Inheritance and Recursion
- Law 4: Connection Creates Meaning
- Law 5: Change Is Motion
- Law 6: Identity Persists
- Law 7: Return to Unity
"""

from .factory import (
    SubstrateFactory,
    create_constant_substrate,
    create_linear_substrate,
    create_quadratic_substrate,
)

from .strategy import (
    ObservationStrategy,
)

from .decorator import (
    SubstrateDecorator,
    AddDecorator,
    MultiplyDecorator,
    ModuloDecorator,
    ClampDecorator,
)

from .iterator import (
    DimensionalIterator,
    SubstrateSequenceIterator,
    iterate_dimensions,
    iterate_substrates,
)

from .composite import (
    CompositeSubstrate,
)

from .fibonacci import (
    FibonacciGenerator,
    create_fibonacci_substrate,
    create_fibonacci_sequence,
)

from .dimensional import (
    DimensionalNavigator,
    DimensionalTransformer,
    navigate_to_dimension,
    transform_dimension,
)

from .substrate import (
    SubstrateLifecycle,
    create_substrate,
    clone_substrate,
    merge_substrates,
    validate_substrate,
)

__all__ = [
    # Factory Pattern
    'SubstrateFactory',
    'create_constant_substrate',
    'create_linear_substrate',
    'create_quadratic_substrate',

    # Strategy Pattern
    'ObservationStrategy',

    # Decorator Pattern
    'SubstrateDecorator',
    'AddDecorator',
    'MultiplyDecorator',
    'ModuloDecorator',
    'ClampDecorator',

    # Iterator Pattern
    'DimensionalIterator',
    'SubstrateSequenceIterator',
    'iterate_dimensions',
    'iterate_substrates',

    # Composite Pattern
    'CompositeSubstrate',

    # Fibonacci Pattern
    'FibonacciGenerator',
    'create_fibonacci_substrate',
    'create_fibonacci_sequence',

    # Dimensional Pattern
    'DimensionalNavigator',
    'DimensionalTransformer',
    'navigate_to_dimension',
    'transform_dimension',

    # Substrate Pattern
    'SubstrateLifecycle',
    'create_substrate',
    'clone_substrate',
    'merge_substrates',
    'validate_substrate',
]

