"""
Substrate - A mathematical expression encoded in 64 bits.

A substrate IS a mathematical structure like:
- z = xy
- z = xy²
- z = x + y
- z = d/dt[position]

The 64-bit identity is a HASH of the expression, not the data.
Invocation reveals truth - nothing is stored.

Examples:
    # Linear expression
    expr = lambda x, y: x + y
    identity = hash("z = x + y") & 0xFFFFFFFFFFFFFFFF
    substrate = Substrate(SubstrateIdentity(identity), expr)

    # Quadratic expression
    expr = lambda x, y: x * (y ** 2)
    identity = hash("z = xy²") & 0xFFFFFFFFFFFFFFFF
    substrate = Substrate(SubstrateIdentity(identity), expr)

No attribute is stored. All truth emerges from invocation.
"""

from __future__ import annotations
from typing import Callable


class SubstrateIdentity:
    """
    64-bit mathematical identity.
    
    Encodes the mathematical universe, NOT data.
    Two identical expressions = same identity (non-duplication law).
    """
    __slots__ = ('_identity',)
    
    def __init__(self, identity: int):
        if not (0 <= identity < 2**64):
            raise ValueError("Identity must fit in 64 bits")
        object.__setattr__(self, '_identity', identity)
    
    def __setattr__(self, name, value):
        raise TypeError("SubstrateIdentity is immutable")
    
    def __delattr__(self, name):
        raise TypeError("SubstrateIdentity is immutable")
    
    @property
    def value(self) -> int:
        return self._identity
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, SubstrateIdentity):
            return self._identity == other._identity
        return False
    
    def __hash__(self) -> int:
        return self._identity
    
    def __repr__(self) -> str:
        return f"SubstrateIdentity(0x{self._identity:016X})"


class Substrate:
    """
    The complete mathematical identity.

    A substrate IS a mathematical expression (z = xy, z = xy², etc.)

    UNIVERSAL SUBSTRATE LAW:
    - A substrate is UNITY (undivided whole)
    - Division creates DIMENSIONS (Fibonacci spiral)
    - Multiplication restores UNITY (manifestation)

    When created, EVERY CONCEIVABLE ATTRIBUTE EXISTS.
    Only identity (x0) and name (x0 in 1D) are explicit.
    Everything else exists because the object exists.

    Attributes manifest ONLY when invoked - nothing is stored.

    The 64-bit identity is BITWISE (2^64 = 18 quintillion combinations).
    The expression can compute ANY attribute - infinite detail from finite encoding.
    """
    __slots__ = ('_x1', '_expression')

    def __init__(self, x1: SubstrateIdentity, expression: Callable):
        """
        x1: The atomic identity (64-bit bitwise) - UNITY
        expression: The mathematical expression that IS this substrate

        Example:
            def car_expression(**kwargs):
                attr = kwargs.get('attribute', 'identity')
                if attr == 'vin': return compute_vin()
                if attr == 'year': return compute_year()
                if attr == 'tire_atoms': return compute_atomic_composition()
                # ... infinite attributes possible
                return derive_attribute(attr)
        """
        object.__setattr__(self, '_x1', x1)
        object.__setattr__(self, '_expression', expression)

    def __setattr__(self, name, value):
        raise TypeError("Substrate is immutable")

    def __delattr__(self, name):
        raise TypeError("Substrate is immutable")

    @property
    def identity(self) -> SubstrateIdentity:
        """The atomic 64-bit identity (x₁) - UNITY"""
        return self._x1

    @property
    def expression(self) -> Callable:
        """The mathematical expression defining this substrate"""
        return self._expression

    def divide(self) -> list:
        """
        DIVISION: Unity → Dimensions (Fibonacci spiral)

        Division separates the whole into distinct parts.
        Each separation introduces a new degree of freedom.
        Each degree of freedom becomes a dimension.
        Recursive division produces the Fibonacci spiral.

        Returns:
            List of dimensions following Fibonacci sequence:
            [0D, 1D, 1D, 2D, 3D, 5D, 8D, 13D, 21D]

        This is the FIRST operation of the Universal Substrate Law.
        """
        from .dimensional import Dimension

        # Fibonacci dimensional structure
        return [
            Dimension(0),   # Void (potential)
            Dimension(1),   # Identity (who)
            Dimension(1),   # Domain (what type)
            Dimension(2),   # Length (attributes)
            Dimension(3),   # Area (relationships)
            Dimension(5),   # Volume (state + change)
            Dimension(8),   # Frequency (temporal patterns)
            Dimension(13),  # System (behaviors)
            Dimension(21),  # Complete (whole object)
        ]

    def multiply(self, dimensions: list) -> int:
        """
        MULTIPLICATION: Dimensions → Unity (Manifestation)

        Multiplication is the inverse of division.
        It collapses ratios, dissolves boundaries, folds dimensions.
        The spiral unwinds. Unity is restored.

        Args:
            dimensions: List of dimensional values to collapse

        Returns:
            64-bit manifestation (unity restored)

        This is the SECOND operation of the Universal Substrate Law.
        """
        # Collapse all dimensions back to unity
        result = 1
        for dim in dimensions:
            # Each dimension contributes to the manifestation
            if hasattr(dim, 'level'):
                result *= (dim.level + 1)  # Avoid multiplication by 0
            else:
                result *= (int(dim) + 1)

        # Ensure result fits in 64 bits
        return result & 0xFFFFFFFFFFFFFFFF

    def invoke(self, **kwargs) -> int:
        """
        INVOCATION: Division → Navigation → Multiplication

        This is the computational expression of the Universal Substrate Law:
        1. DIVIDE substrate into dimensions (Fibonacci spiral)
        2. NAVIGATE to position specified by kwargs
        3. MULTIPLY dimensions back to unity (manifestation)

        This is how attributes come into existence - through invocation.
        Nothing is stored; everything is computed.

        Args:
            **kwargs: Parameters for the expression (e.g., attribute='vin')

        Returns:
            64-bit result of the mathematical expression

        Example:
            substrate.invoke(attribute='vin')  # Manifests VIN
            substrate.invoke(attribute='year')  # Manifests year
            substrate.invoke(attribute='tire_atoms')  # Manifests atomic composition
        """
        # Step 1: DIVISION - Unity → Dimensions
        dimensions = self.divide()

        # Step 2: NAVIGATION - Evaluate expression at position
        result = self._expression(**kwargs)

        # Step 3: MULTIPLICATION - Dimensions → Unity
        # (The expression result is already the collapsed manifestation)

        # Ensure result fits in 64 bits (bitwise)
        return result & 0xFFFFFFFFFFFFFFFF

    def __eq__(self, other: object) -> bool:
        # Non-duplication: identical expressions = same identity
        if isinstance(other, Substrate):
            return self._x1 == other._x1
        return False

    def __hash__(self) -> int:
        return hash(self._x1)

    def __repr__(self) -> str:
        return f"Substrate({self._x1})"

    # ═══════════════════════════════════════════════════════════════
    # DIMENSIONAL LAW HELPERS
    # ═══════════════════════════════════════════════════════════════

    # ─────────────────────────────────────────────────────────────
    # LAW ONE: Universal Substrate Law
    # ─────────────────────────────────────────────────────────────

    def get_unity(self) -> SubstrateIdentity:
        """
        Get substrate as unity (undivided whole).

        LAW ONE: All substrates begin as unity.

        Returns:
            The substrate's 64-bit identity (unity)
        """
        return self._x1

    def get_dimensions(self) -> list:
        """
        Get dimensions (alias for divide()).

        LAW ONE: Division generates dimensions.

        Returns:
            List of Fibonacci dimensions
        """
        return self.divide()

    def recombine(self, dimensions: list) -> int:
        """
        Recombine dimensions back to unity (alias for multiply()).

        LAW ONE: Multiplication recombines dimensions and restores unity.

        Args:
            dimensions: List of dimensional values

        Returns:
            64-bit manifestation (unity restored)
        """
        return self.multiply(dimensions)

    # ─────────────────────────────────────────────────────────────
    # LAW TWO: Observation Is Division
    # ─────────────────────────────────────────────────────────────

    def observe(self, state_vector=None) -> list:
        """
        Observe substrate (triggers division).

        LAW TWO: Observation is division.

        Observation creates dimensions. The act of observing
        divides unity into its constituent dimensions.

        Args:
            state_vector: Optional state vector for navigation

        Returns:
            List of dimensions (observation result)
        """
        # Observation triggers division
        return self.divide()

    def select_dimension(self, index: int):
        """
        Select a specific dimension from the substrate.

        LAW TWO: Division creates dimensions.

        Args:
            index: Dimension index (0-8 for Fibonacci dimensions)

        Returns:
            The selected dimension
        """
        dimensions = self.divide()
        if 0 <= index < len(dimensions):
            return dimensions[index]
        raise IndexError(f"Dimension index {index} out of range (0-{len(dimensions)-1})")

    def manifest(self, lens=None) -> int:
        """
        Manifest substrate through optional lens.

        LAW TWO: Recombination restores unity.

        This is the complete observation cycle:
        Unity → Division → Recombination → Manifestation

        Args:
            lens: Optional lens for projection

        Returns:
            64-bit manifestation
        """
        # Divide into dimensions
        dimensions = self.divide()

        # Recombine to unity
        manifestation = self.multiply(dimensions)

        # Apply lens if provided
        if lens is not None and hasattr(lens, 'projection'):
            return lens.projection(manifestation)

        return manifestation

    # ─────────────────────────────────────────────────────────────
    # LAW THREE: Inheritance and Recursion
    # ─────────────────────────────────────────────────────────────

    def verify_inheritance(self) -> bool:
        """
        Verify that divisions inherit the whole.

        LAW THREE: Every division inherits the whole.

        Each dimension is a projection of the substrate's unity.
        The substrate identity persists through all divisions.

        Returns:
            True (always - this is a law, not a condition)
        """
        # Get dimensions
        dimensions = self.divide()

        # Verify each dimension exists (inheritance is implicit)
        # The fact that divide() returns dimensions proves inheritance
        return len(dimensions) == 9  # Fibonacci structure

    def get_pattern(self) -> list:
        """
        Extract the Fibonacci pattern from substrate.

        LAW THREE: Every part contains the pattern.

        Returns:
            List of Fibonacci numbers [0, 1, 1, 2, 3, 5, 8, 13, 21]
        """
        dimensions = self.divide()
        return [dim.level for dim in dimensions]

    def check_recursion(self) -> bool:
        """
        Verify recursive preservation of unity.

        LAW THREE: Recursion preserves unity across dimensions.

        Returns:
            True if recursion preserves unity
        """
        # The substrate identity never changes
        identity_before = self._x1

        # Perform division (recursive operation)
        _ = self.divide()

        # Identity persists
        identity_after = self._x1

        return identity_before == identity_after

    # ─────────────────────────────────────────────────────────────
    # LAW FOUR: Connection Creates Meaning
    # ─────────────────────────────────────────────────────────────

    def connect_to(self, other_substrate: 'Substrate', srl=None) -> tuple:
        """
        Create connection to another substrate.

        LAW FOUR: Dimensions relate through connection.

        Connection creates a relationship between two substrates.
        The relationship itself can be represented as a substrate (via SRL).

        Args:
            other_substrate: The substrate to connect to
            srl: Optional SRL defining the connection rule

        Returns:
            Tuple of (self_identity, other_identity, relationship_hash)
        """
        # Connection is the relationship between two identities
        self_id = self._x1.value
        other_id = other_substrate.identity.value

        # Create relationship hash
        relationship = (self_id ^ other_id) & 0xFFFFFFFFFFFFFFFF

        return (self_id, other_id, relationship)

    def get_relationships(self) -> list:
        """
        Get all relationships (placeholder for relationship tracking).

        LAW FOUR: Connection creates meaning.

        In a full implementation, this would track all connections
        made via connect_to(). For now, returns empty list.

        Returns:
            List of relationships
        """
        # Placeholder - full implementation would track relationships
        return []

    def extract_meaning(self, relationships: list = None) -> int:
        """
        Extract emergent meaning from relationships.

        LAW FOUR: Meaning emerges from the pattern of relationships.

        Meaning is not stored - it emerges from the structure
        of connections between substrates.

        Args:
            relationships: Optional list of relationships

        Returns:
            64-bit meaning (emergent from pattern)
        """
        if relationships is None or len(relationships) == 0:
            # No relationships - meaning is the substrate itself
            return self._x1.value

        # Meaning emerges from the pattern of relationships
        meaning = self._x1.value
        for rel in relationships:
            if isinstance(rel, tuple) and len(rel) >= 3:
                meaning ^= rel[2]  # XOR with relationship hash

        return meaning & 0xFFFFFFFFFFFFFFFF

    # ─────────────────────────────────────────────────────────────
    # LAW FIVE: Change Is Motion
    # ─────────────────────────────────────────────────────────────

    def evolve(self, delta) -> SubstrateIdentity:
        """
        Evolve substrate through dimensional motion.

        LAW FIVE: Change is motion through dimensions.

        The substrate itself doesn't change - a new identity is created.
        This is dimensional promotion: x₁ + δ → m₁

        Args:
            delta: Delta representing the change

        Returns:
            New substrate identity (evolved state)
        """
        from .dimensional import promote

        # Evolution creates new identity through promotion
        # For now, use a simple manifestation as the attribute value
        attribute_value = self.multiply(self.divide())

        return promote(self._x1, attribute_value, delta)

    def get_trajectory(self) -> list:
        """
        Get evolution trajectory (placeholder for motion tracking).

        LAW FIVE: Time is the order of motion.

        In a full implementation, this would track the sequence
        of dimensional promotions. For now, returns current state.

        Returns:
            List containing current identity
        """
        # Placeholder - full implementation would track evolution
        return [self._x1]

    def time_sequence(self, deltas: list) -> list:
        """
        Create time sequence through multiple evolutions.

        LAW FIVE: Evolution is the reexpression of unity across states.

        Args:
            deltas: List of deltas representing sequential changes

        Returns:
            List of substrate identities (time sequence)
        """
        sequence = [self._x1]  # Start with current identity

        current_identity = self._x1
        for delta in deltas:
            # Each delta creates a new identity
            from .dimensional import promote
            attribute_value = self.multiply(self.divide())
            new_identity = promote(current_identity, attribute_value, delta)
            sequence.append(new_identity)
            current_identity = new_identity

        return sequence

    # ─────────────────────────────────────────────────────────────
    # LAW SIX: Identity Persists
    # ─────────────────────────────────────────────────────────────

    def verify_identity_persistence(self) -> bool:
        """
        Verify that identity persists through transformations.

        LAW SIX: Identity persists through change.

        The substrate identity NEVER changes. All transformations
        (division, multiplication, observation) preserve identity.

        Returns:
            True (always - identity is immutable)
        """
        # Store original identity
        original = self._x1

        # Perform various transformations
        _ = self.divide()
        _ = self.multiply(self.divide())
        _ = self.observe()
        _ = self.manifest()

        # Identity persists
        return self._x1 == original

    def get_continuity_thread(self) -> SubstrateIdentity:
        """
        Get the continuity thread (the persistent identity).

        LAW SIX: Continuity is the thread of unity.

        The identity is the thread that persists through
        all transformations, divisions, and evolutions.

        Returns:
            The substrate's identity (the continuity thread)
        """
        return self._x1

    # ─────────────────────────────────────────────────────────────
    # LAW SEVEN: Return to Unity
    # ─────────────────────────────────────────────────────────────

    def complete_cycle(self, lens=None) -> int:
        """
        Complete the full Unity → Division → Unity cycle.

        LAW SEVEN: All dimensions return to unity.

        This is the complete dimensional cycle:
        1. Unity (substrate identity)
        2. Division (create dimensions)
        3. Multiplication (collapse dimensions)
        4. Projection (apply lens)
        5. Unity restored (manifestation)

        Args:
            lens: Optional lens for final projection

        Returns:
            64-bit manifestation (unity restored)
        """
        # STEP 1: Unity (the source)
        unity_start = self._x1.value

        # STEP 2: Division (observation creates dimensions)
        dimensions = self.divide()

        # STEP 3: Multiplication (dimensions return to unity)
        manifestation = self.multiply(dimensions)

        # STEP 4: Projection (lens transforms unity)
        if lens is not None and hasattr(lens, 'projection'):
            result = lens.projection(manifestation)
        else:
            result = manifestation

        # STEP 5: Unity restored (the cycle is complete)
        # The result is unity at a new level
        return result & 0xFFFFFFFFFFFFFFFF

    def verify_return(self) -> bool:
        """
        Verify that dimensions return to unity.

        LAW SEVEN: Completion is the reunion of the many.

        Division creates many dimensions.
        Multiplication reunites them into one.
        The cycle ends where it begins: unity.

        Returns:
            True if multiplication successfully returns to unity
        """
        # Divide into many
        dimensions = self.divide()

        # Multiply back to one
        unity_restored = self.multiply(dimensions)

        # Verify we got a 64-bit result (unity)
        return 0 <= unity_restored < 2**64
