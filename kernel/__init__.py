"""
ButterflyFx Kernel - The Inner Sanctum

This module contains ONLY pure mathematical expressions.
No logic, no conditions, no state, no side effects.

RULES:
1. The Kernel is IMMUTABLE - it cannot be altered at runtime
2. The Kernel can ONLY be accessed through the Core
3. All expressions are substrate math - 64-bit identity transformations
4. No imports from Core or Interface layers permitted
5. No I/O, no logging, no external dependencies
"""

from .substrate import Substrate, SubstrateIdentity
from .manifold import Manifold
from .lens import Lens
from .delta import Delta
from .dimensional import Dimension, promote
from .srl import SRL, create_srl_identity
from . import fibonacci
from .canonical import (
    CanonicalObject,
    DimensionSpec,
    RelationshipSpec,
    ManifestationFunction,
    default_manifestation,
    create_canonical_object,
    create_dimension,
    create_relationship,
)
from .return_engine import (
    ReturnEngine,
    collapse_to_unity,
    complete_cycle,
)
from .registry import (
    DimensionalObjectRegistry,
    RegistryReference,
    get_registry,
    register_substrate,
    lookup_substrate,
    substrate_exists,
)
from .observer import (
    Observation,
    Observer,
    observe,
    observe_dimension,
    create_observer,
)
from .optimizations import (
    FibonacciCache,
    fibonacci_memoized,
    check_64bit_bounds,
)

from .residue import (
    DimensionalResidue,
    compute_residue,
)

from .arithmetic import (
    dimensional_divide,
    dimensional_multiply,
    dimensional_add,
    dimensional_subtract,
    dimensional_modulus,
)

from .operators import (
    # Cross-dimensional operators
    cross_divide,
    cross_multiply,
    cross_modulus,
    cross_power,
    cross_root,
    # Intra-dimensional operators
    intra_add,
    intra_subtract,
    intra_and,
    intra_or,
    intra_not,
    intra_xor,
    intra_nand,
    intra_nor,
    intra_equal,
    intra_not_equal,
    intra_less_than,
    intra_greater_than,
    intra_less_equal,
    intra_greater_equal,
    intra_bitwise_and,
    intra_bitwise_or,
    intra_bitwise_xor,
    intra_bitwise_not,
    intra_left_shift,
    intra_right_shift,
    # Operator categorization
    CROSS_DIMENSIONAL_OPS,
    INTRA_DIMENSIONAL_OPS,
    is_cross_dimensional,
    is_intra_dimensional,
)

from .reversibility import (
    ReversibilityError,
    validate_addition_reversibility,
    validate_subtraction_reversibility,
    validate_multiplication_reversibility,
    validate_residue_reversibility,
)

from .logging import (
    LogLevel,
    LogEntry,
    DimensionalLogger,
    get_logger,
    get_audit_logger,
    console_handler,
    json_handler,
    file_handler,
    audit_file_handler,
)

from .relationships import (
    RelationshipType,
    Relationship,
    RelationshipSet,
)

from .seed_loader import (
    PrimitiveCategory,
    PrimitiveSeed,
    SeedLoader,
)

__all__ = [
    'Substrate',
    'SubstrateIdentity',
    'Manifold',
    'Lens',
    'Delta',
    'Dimension',
    'promote',
    'SRL',
    'create_srl_identity',
    'fibonacci',
    # Canonical Form
    'CanonicalObject',
    'DimensionSpec',
    'RelationshipSpec',
    'ManifestationFunction',
    'default_manifestation',
    'create_canonical_object',
    'create_dimension',
    'create_relationship',
    # Return Engine
    'ReturnEngine',
    'collapse_to_unity',
    'complete_cycle',
    # Dimensional Object Registry
    'DimensionalObjectRegistry',
    'RegistryReference',
    'get_registry',
    'register_substrate',
    'lookup_substrate',
    'substrate_exists',
    # Observer Interface
    'Observation',
    'Observer',
    'observe',
    'observe_dimension',
    'create_observer',
    # Optimizations
    'FibonacciCache',
    'fibonacci_memoized',
    'check_64bit_bounds',
    # Dimensional Residue
    'DimensionalResidue',
    'compute_residue',
    # Dimensional Arithmetic (legacy)
    'dimensional_divide',
    'dimensional_multiply',
    'dimensional_add',
    'dimensional_subtract',
    'dimensional_modulus',
    # Dimensional Operators (new framework)
    'cross_divide',
    'cross_multiply',
    'cross_modulus',
    'cross_power',
    'cross_root',
    'intra_add',
    'intra_subtract',
    'intra_and',
    'intra_or',
    'intra_not',
    'intra_xor',
    'intra_nand',
    'intra_nor',
    'intra_equal',
    'intra_not_equal',
    'intra_less_than',
    'intra_greater_than',
    'intra_less_equal',
    'intra_greater_equal',
    'intra_bitwise_and',
    'intra_bitwise_or',
    'intra_bitwise_xor',
    'intra_bitwise_not',
    'intra_left_shift',
    'intra_right_shift',
    'CROSS_DIMENSIONAL_OPS',
    'INTRA_DIMENSIONAL_OPS',
    'is_cross_dimensional',
    'is_intra_dimensional',
    # Reversibility Validation
    'ReversibilityError',
    'validate_addition_reversibility',
    'validate_subtraction_reversibility',
    'validate_multiplication_reversibility',
    'validate_residue_reversibility',
    # Dimensional Logging
    'LogLevel',
    'LogEntry',
    'DimensionalLogger',
    'get_logger',
    'get_audit_logger',
    'console_handler',
    'json_handler',
    'file_handler',
    'audit_file_handler',
    # Dimensional Relationships
    'RelationshipType',
    'Relationship',
    'RelationshipSet',
    # Primitive Seed System
    'PrimitiveCategory',
    'PrimitiveSeed',
    'SeedLoader',
]
