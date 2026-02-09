"""
Canonical Dimensional Object Form

This module implements the pure mathematical contract for dimensional objects:

    𝒪 = ⟨S, D, R, F, T⟩

Where:
    - S = substrate (unity, immutable identity)
    - D = set of dimensions (axes with domains and inheritance)
    - R = set of relationships (functions between dimensions)
    - F = manifestation function (pure computation)
    - T = time/ordering parameter

No state is stored. All states are computed from this expression.

This is the canonical form that any programming AI can implement.
"""

from __future__ import annotations
from typing import Callable, Any, Optional, Set, Tuple, Dict
from dataclasses import dataclass

from .substrate import Substrate, SubstrateIdentity
from .dimensional import Dimension


# ═══════════════════════════════════════════════════════════════════
# DIMENSION SPECIFICATION
# ═══════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class DimensionSpec:
    """
    A dimension specification: ⟨name, domain, inherit⟩
    
    Each dimension is a named axis with:
        - name: Label (e.g., "position", "mass", "color", "role")
        - domain: Allowed values (type or constraint)
        - inherit: How this dimension derives from substrate
    
    Example:
        position = DimensionSpec(
            name="position",
            domain=float,
            inherit=lambda s: s.expression(attribute="position")
        )
    """
    name: str
    domain: type | Callable[[Any], bool]  # Type or validation function
    inherit: Callable[[Substrate], Any]   # How to derive from substrate


# ═══════════════════════════════════════════════════════════════════
# RELATIONSHIP SPECIFICATION
# ═══════════════════════════════════════════════════════════════════

class RelationshipSpec:
    """
    A relationship specification: ⟨name, inputs, outputs, f⟩

    Relationships are functions between dimensions:
        - name: Label (e.g., "velocity", "force", "color_perception")
        - inputs: Set of input dimension names
        - outputs: Set of output dimension names
        - f: Function mapping input values to output values

    Example:
        velocity = RelationshipSpec(
            name="velocity",
            inputs={"position", "time"},
            outputs={"velocity"},
            f=lambda pos, time: pos / time if time != 0 else 0
        )
    """
    __slots__ = ('name', 'inputs', 'outputs', 'f', '_hash')

    def __init__(self, name: str, inputs: Set[str], outputs: Set[str], f: Callable[..., Any]):
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'inputs', frozenset(inputs))
        object.__setattr__(self, 'outputs', frozenset(outputs))
        object.__setattr__(self, 'f', f)
        # Hash based on name only (functions aren't hashable)
        object.__setattr__(self, '_hash', hash(name))

    def __setattr__(self, name, value):
        raise TypeError("RelationshipSpec is immutable")

    def __delattr__(self, name):
        raise TypeError("RelationshipSpec is immutable")

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if not isinstance(other, RelationshipSpec):
            return False
        return self.name == other.name

    def __repr__(self):
        return f"RelationshipSpec(name={self.name!r}, inputs={set(self.inputs)}, outputs={set(self.outputs)})"


# ═══════════════════════════════════════════════════════════════════
# MANIFESTATION FUNCTION
# ═══════════════════════════════════════════════════════════════════

ManifestationFunction = Callable[[Substrate, Set[DimensionSpec], Set[RelationshipSpec], float | int], Any]


# ═══════════════════════════════════════════════════════════════════
# CANONICAL DIMENSIONAL OBJECT
# ═══════════════════════════════════════════════════════════════════

class CanonicalObject:
    """
    The canonical dimensional object form: 𝒪 = ⟨S, D, R, F, T⟩
    
    This is the pure mathematical contract for dimensional objects.
    
    Components:
        - S: Substrate (unity, immutable identity)
        - D: Set of dimensions (axes with domains and inheritance)
        - R: Set of relationships (functions between dimensions)
        - F: Manifestation function (pure computation)
        - T: Time/ordering parameter
    
    No state is stored. All states are computed from the expression.
    
    Example:
        # Define dimensions
        position = DimensionSpec("position", float, lambda s: s.expression(attribute="position"))
        velocity = DimensionSpec("velocity", float, lambda s: s.expression(attribute="velocity"))
        
        # Define relationships
        motion = RelationshipSpec("motion", {"position", "velocity", "time"}, {"position"}, 
                                  lambda pos, vel, t: pos + vel * t)
        
        # Create canonical object
        obj = CanonicalObject(
            substrate=my_substrate,
            dimensions={position, velocity},
            relationships={motion},
            manifestation=default_manifestation,
            time=0.0
        )
        
        # Manifest at time t
        state = obj.manifest(t=1.0)
    """
    
    __slots__ = ('_S', '_D', '_R', '_F', '_T')
    
    def __init__(
        self,
        substrate: Substrate,
        dimensions: Set[DimensionSpec],
        relationships: Set[RelationshipSpec],
        manifestation: ManifestationFunction,
        time: float | int = 0
    ):
        """
        Create a canonical dimensional object.
        
        Args:
            substrate: S - The substrate (unity, immutable identity)
            dimensions: D - Set of dimension specifications
            relationships: R - Set of relationship specifications
            manifestation: F - The manifestation function
            time: T - Time/ordering parameter (default: 0)
        """
        object.__setattr__(self, '_S', substrate)
        object.__setattr__(self, '_D', frozenset(dimensions))
        object.__setattr__(self, '_R', frozenset(relationships))
        object.__setattr__(self, '_F', manifestation)
        object.__setattr__(self, '_T', time)

    def __setattr__(self, name, value):
        raise TypeError("CanonicalObject is immutable")

    def __delattr__(self, name):
        raise TypeError("CanonicalObject is immutable")

    # ═══════════════════════════════════════════════════════════════
    # PROPERTIES - Access the five elements
    # ═══════════════════════════════════════════════════════════════

    @property
    def substrate(self) -> Substrate:
        """S - The substrate (unity)"""
        return self._S

    @property
    def dimensions(self) -> frozenset[DimensionSpec]:
        """D - Set of dimensions"""
        return self._D

    @property
    def relationships(self) -> frozenset[RelationshipSpec]:
        """R - Set of relationships"""
        return self._R

    @property
    def manifestation_function(self) -> ManifestationFunction:
        """F - The manifestation function"""
        return self._F

    @property
    def time(self) -> float | int:
        """T - Time/ordering parameter"""
        return self._T

    # ═══════════════════════════════════════════════════════════════
    # CORE OPERATIONS
    # ═══════════════════════════════════════════════════════════════

    def manifest(self, t: Optional[float | int] = None) -> Any:
        """
        Manifest the object at time t.

        This is the core operation: F(S, D, R, T) → M

        Args:
            t: Time parameter (uses current time if None)

        Returns:
            Manifestation M (computed from S, D, R, T)
        """
        time_param = t if t is not None else self._T
        return self._F(self._S, self._D, self._R, time_param)

    def at_time(self, t: float | int) -> 'CanonicalObject':
        """
        Create a new canonical object at time t.

        This does NOT mutate the object - it creates a new one.

        Args:
            t: New time parameter

        Returns:
            New CanonicalObject with updated time
        """
        return CanonicalObject(
            substrate=self._S,
            dimensions=self._D,
            relationships=self._R,
            manifestation=self._F,
            time=t
        )

    def get_dimension_value(self, dimension_name: str, t: Optional[float | int] = None) -> Any:
        """
        Get the value of a specific dimension at time t.

        This computes the dimension value from:
            d_i(t) = inherit_i(S) combined with R and t

        Args:
            dimension_name: Name of the dimension
            t: Time parameter (uses current time if None)

        Returns:
            Dimension value (computed, not stored)
        """
        time_param = t if t is not None else self._T

        # Find the dimension spec
        dim_spec = None
        for d in self._D:
            if d.name == dimension_name:
                dim_spec = d
                break

        if dim_spec is None:
            raise ValueError(f"Dimension '{dimension_name}' not found")

        # Compute base value from substrate inheritance
        base_value = dim_spec.inherit(self._S)

        # Apply relationships that output this dimension
        for rel in self._R:
            if dimension_name in rel.outputs:
                # Collect input values
                input_values = {}
                for input_name in rel.inputs:
                    if input_name == "time":
                        input_values["time"] = time_param
                    else:
                        # Recursively get input dimension values
                        for d in self._D:
                            if d.name == input_name:
                                input_values[input_name] = d.inherit(self._S)
                                break

                # Apply relationship function
                if input_values:
                    base_value = rel.f(**input_values)

        return base_value

    def get_all_dimension_values(self, t: Optional[float | int] = None) -> Dict[str, Any]:
        """
        Get all dimension values at time t.

        Returns:
            Dictionary mapping dimension names to values
        """
        time_param = t if t is not None else self._T
        return {d.name: self.get_dimension_value(d.name, time_param) for d in self._D}

    def __repr__(self) -> str:
        return (
            f"CanonicalObject(\n"
            f"  S={self._S.identity.value:016X},\n"
            f"  D={{{', '.join(d.name for d in self._D)}}},\n"
            f"  R={{{', '.join(r.name for r in self._R)}}},\n"
            f"  T={self._T}\n"
            f")"
        )


# ═══════════════════════════════════════════════════════════════════
# DEFAULT MANIFESTATION FUNCTION
# ═══════════════════════════════════════════════════════════════════

def default_manifestation(
    substrate: Substrate,
    dimensions: Set[DimensionSpec],
    relationships: Set[RelationshipSpec],
    time: float | int
) -> Dict[str, Any]:
    """
    Default manifestation function: F(S, D, R, T) → M

    This computes all dimension values at time t and returns them as a dictionary.

    Args:
        substrate: S - The substrate
        dimensions: D - Set of dimensions
        relationships: R - Set of relationships
        time: T - Time parameter

    Returns:
        M - Manifestation as dictionary of dimension values
    """
    manifestation = {}

    # First pass: Compute base values from substrate inheritance
    for dim in dimensions:
        manifestation[dim.name] = dim.inherit(substrate)

    # Second pass: Apply relationships
    for rel in relationships:
        # Collect input values
        input_values = {}
        for input_name in rel.inputs:
            if input_name == "time":
                input_values["time"] = time
            elif input_name in manifestation:
                input_values[input_name] = manifestation[input_name]

        # Apply relationship function if all inputs are available
        if len(input_values) == len(rel.inputs):
            result = rel.f(**input_values)

            # Update output dimensions
            if len(rel.outputs) == 1:
                output_name = next(iter(rel.outputs))
                manifestation[output_name] = result
            else:
                # Multiple outputs - result should be a dict or tuple
                if isinstance(result, dict):
                    for output_name in rel.outputs:
                        if output_name in result:
                            manifestation[output_name] = result[output_name]

    return manifestation


# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def create_canonical_object(
    substrate: Substrate,
    dimensions: Set[DimensionSpec] | list[DimensionSpec],
    relationships: Set[RelationshipSpec] | list[RelationshipSpec] | None = None,
    manifestation: Optional[ManifestationFunction] = None,
    time: float | int = 0
) -> CanonicalObject:
    """
    Helper function to create a canonical object.

    Args:
        substrate: The substrate (S)
        dimensions: Set or list of dimension specifications (D)
        relationships: Set or list of relationship specifications (R), optional
        manifestation: Manifestation function (F), uses default if None
        time: Time parameter (T), default 0

    Returns:
        CanonicalObject instance
    """
    dims = set(dimensions) if isinstance(dimensions, list) else dimensions
    rels = set(relationships) if isinstance(relationships, list) else (relationships or set())
    func = manifestation if manifestation is not None else default_manifestation

    return CanonicalObject(
        substrate=substrate,
        dimensions=dims,
        relationships=rels,
        manifestation=func,
        time=time
    )


def create_dimension(
    name: str,
    domain: type | Callable[[Any], bool],
    inherit: Callable[[Substrate], Any]
) -> DimensionSpec:
    """
    Helper function to create a dimension specification.

    Args:
        name: Dimension name
        domain: Type or validation function
        inherit: Function to derive value from substrate

    Returns:
        DimensionSpec instance
    """
    return DimensionSpec(name=name, domain=domain, inherit=inherit)


def create_relationship(
    name: str,
    inputs: Set[str] | list[str],
    outputs: Set[str] | list[str],
    f: Callable[..., Any]
) -> RelationshipSpec:
    """
    Helper function to create a relationship specification.

    Args:
        name: Relationship name
        inputs: Set or list of input dimension names
        outputs: Set or list of output dimension names
        f: Function mapping inputs to outputs

    Returns:
        RelationshipSpec instance
    """
    ins = set(inputs) if isinstance(inputs, list) else inputs
    outs = set(outputs) if isinstance(outputs, list) else outputs

    return RelationshipSpec(name=name, inputs=ins, outputs=outs, f=f)

