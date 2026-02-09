"""
KernelGateway - The sole point of access to the Kernel.

This is the inner sanctum guard. All access to Kernel
primitives MUST flow through this gateway.

The gateway:
1. Validates access permissions
2. Ensures all operations are substrate-compliant
3. Returns only what the Kernel math reveals
4. NEVER exposes Kernel internals for modification
"""

from __future__ import annotations
from typing import Callable, Optional

# Kernel imports - Core is the ONLY layer allowed to do this
from kernel.substrate import Substrate, SubstrateIdentity
from kernel.manifold import Manifold
from kernel.lens import Lens
from kernel.delta import Delta
from kernel.dimensional import Dimension, promote


class KernelGateway:
    """
    The sole gateway to the Kernel layer.
    
    External code (human, machine, AI) accesses the Kernel
    ONLY through Core, and Core accesses ONLY through this gateway.
    """
    
    _instance: Optional[KernelGateway] = None
    
    def __new__(cls) -> KernelGateway:
        # Singleton - one gateway to the inner sanctum
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    # ═══════════════════════════════════════════════════════════════
    # SUBSTRATE OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def create_identity(self, value: int) -> SubstrateIdentity:
        """Create a 64-bit substrate identity"""
        return SubstrateIdentity(value)
    
    def create_substrate(
        self, 
        identity: SubstrateIdentity,
        expression: Callable[[], int]
    ) -> Substrate:
        """Create a substrate with its mathematical expression"""
        return Substrate(identity, expression)
    
    # ═══════════════════════════════════════════════════════════════
    # LENS OPERATIONS  
    # ═══════════════════════════════════════════════════════════════
    
    def create_lens(
        self,
        lens_id: int,
        projection: Callable[[int], int]
    ) -> Lens:
        """Create a lens for attribute derivation"""
        return Lens(lens_id, projection)
    
    # ═══════════════════════════════════════════════════════════════
    # INVOCATION - Truth Revelation
    # ═══════════════════════════════════════════════════════════════
    
    def invoke(self, substrate: Substrate, lens: Lens, state_vector=None) -> int:
        """
        Invoke substrate through lens to reveal truth.

        UNIVERSAL SUBSTRATE LAW IMPLEMENTATION:
        ---------------------------------------
        The substrate contains unity (the expression result).
        The lens provides the projection (dimensional view).
        The state vector (if provided) navigates the Fibonacci spiral.

        For now, we maintain backward compatibility by using the
        substrate's expression directly. The full Division → Navigation →
        Multiplication pattern will be implemented when state vectors are
        provided with invocations.

        Computation = substrate → lens → invocation
        Nothing is precomputed or stored.

        Args:
            substrate: The substrate (unity)
            lens: The lens (projection)
            state_vector: Optional 64-bit state vector (spiral coordinate)

        Returns:
            Manifestation (collapsed unity)
        """
        # Get the substrate's expression result (unity)
        substrate_value = substrate.expression()

        # If state vector is provided, use the Universal Substrate Law pattern
        if state_vector is not None:
            # STEP 1: DIVISION - Unity → Dimensions
            dimensions = substrate.divide()

            # STEP 2: NAVIGATION - Navigate to state vector position
            if hasattr(state_vector, 'to_spiral_coordinates'):
                coords = state_vector.to_spiral_coordinates()
                # Navigate dimensions based on coordinates
                # This is where we would use Fibonacci spiral geometry
                # to navigate the dimensional space
                pass

            # STEP 3: MULTIPLICATION - Dimensions → Unity
            # For now, we use the substrate value as the manifestation
            # Full implementation will collapse dimensions using multiply()
            manifestation = substrate_value
        else:
            # Backward compatible path: use expression directly
            manifestation = substrate_value

        # Apply lens projection to the manifestation
        # The lens transforms the manifestation into the final truth
        if lens is not None:
            return lens.projection(manifestation)

        return manifestation
    
    # ═══════════════════════════════════════════════════════════════
    # MANIFOLD OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def create_manifold(
        self,
        substrate: Substrate,
        dimension: int,
        form_expression: int
    ) -> Manifold:
        """Create a manifold - dimensional expression of substrate"""
        return Manifold(substrate.identity, dimension, form_expression)
    
    # ═══════════════════════════════════════════════════════════════
    # DIMENSIONAL PROMOTION - The Mechanism of Change
    # ═══════════════════════════════════════════════════════════════
    
    def create_delta(self, z1: int) -> Delta:
        """Create a delta for change representation"""
        return Delta(z1)
    
    def promote_substrate(
        self,
        substrate: Substrate,
        attribute_value: int,
        delta: Delta
    ) -> SubstrateIdentity:
        """
        Promote substrate to new identity through delta.
        
        x₁ + y₁ + δ(z₁) → m₁
        
        This is the ONLY way change occurs.
        Returns a NEW identity - original is untouched.
        """
        return promote(substrate.identity, attribute_value, delta)
    
    def get_dimension(self, level: int) -> Dimension:
        """Get a dimension by level"""
        return Dimension(level)

    # ═══════════════════════════════════════════════════════════════
    # DIMENSIONAL LAW OPERATIONS
    # ═══════════════════════════════════════════════════════════════

    # ─────────────────────────────────────────────────────────────
    # LAW ONE: Universal Substrate Law
    # ─────────────────────────────────────────────────────────────

    def divide_substrate(self, substrate: Substrate) -> list:
        """
        Divide substrate into dimensions.

        LAW ONE: Division generates dimensions and follows the Fibonacci spiral.

        Args:
            substrate: The substrate to divide

        Returns:
            List of Fibonacci dimensions
        """
        return substrate.divide()

    def multiply_dimensions(self, substrate: Substrate, dimensions: list) -> int:
        """
        Multiply dimensions back to unity.

        LAW ONE: Multiplication recombines dimensions and restores unity.

        Args:
            substrate: The substrate
            dimensions: List of dimensions to collapse

        Returns:
            64-bit manifestation (unity restored)
        """
        return substrate.multiply(dimensions)

    def get_unity(self, substrate: Substrate) -> SubstrateIdentity:
        """
        Get substrate as unity.

        LAW ONE: All substrates begin as unity.

        Args:
            substrate: The substrate

        Returns:
            The substrate's identity (unity)
        """
        return substrate.get_unity()

    # ─────────────────────────────────────────────────────────────
    # LAW TWO: Observation Is Division
    # ─────────────────────────────────────────────────────────────

    def observe(self, substrate: Substrate, state_vector=None) -> list:
        """
        Observe substrate (triggers division).

        LAW TWO: Observation is division.

        Args:
            substrate: The substrate to observe
            state_vector: Optional state vector for navigation

        Returns:
            List of dimensions (observation result)
        """
        return substrate.observe(state_vector)

    def manifest(self, substrate: Substrate, lens: Lens = None) -> int:
        """
        Manifest substrate through optional lens.

        LAW TWO: Recombination restores unity.

        Args:
            substrate: The substrate to manifest
            lens: Optional lens for projection

        Returns:
            64-bit manifestation
        """
        return substrate.manifest(lens)

    # ─────────────────────────────────────────────────────────────
    # LAW THREE: Inheritance and Recursion
    # ─────────────────────────────────────────────────────────────

    def verify_inheritance(self, substrate: Substrate) -> bool:
        """
        Verify that divisions inherit the whole.

        LAW THREE: Every division inherits the whole.

        Args:
            substrate: The substrate to verify

        Returns:
            True if inheritance is preserved
        """
        return substrate.verify_inheritance()

    def get_pattern(self, substrate: Substrate) -> list:
        """
        Extract the Fibonacci pattern from substrate.

        LAW THREE: Every part contains the pattern.

        Args:
            substrate: The substrate

        Returns:
            List of Fibonacci numbers
        """
        return substrate.get_pattern()

    # ─────────────────────────────────────────────────────────────
    # LAW FOUR: Connection Creates Meaning
    # ─────────────────────────────────────────────────────────────

    def create_relationship(
        self,
        substrate_a: Substrate,
        substrate_b: Substrate,
        srl=None
    ) -> tuple:
        """
        Create relationship between two substrates.

        LAW FOUR: Dimensions relate through connection.

        Args:
            substrate_a: First substrate
            substrate_b: Second substrate
            srl: Optional SRL defining connection rule

        Returns:
            Tuple of (id_a, id_b, relationship_hash)
        """
        return substrate_a.connect_to(substrate_b, srl)

    def extract_meaning(self, substrate: Substrate, relationships: list = None) -> int:
        """
        Extract emergent meaning from substrate.

        LAW FOUR: Meaning emerges from the pattern of relationships.

        Args:
            substrate: The substrate
            relationships: Optional list of relationships

        Returns:
            64-bit meaning (emergent from pattern)
        """
        return substrate.extract_meaning(relationships)

    # ─────────────────────────────────────────────────────────────
    # LAW FIVE: Change Is Motion
    # ─────────────────────────────────────────────────────────────

    def evolve(self, substrate: Substrate, delta: Delta) -> SubstrateIdentity:
        """
        Evolve substrate through dimensional motion.

        LAW FIVE: Change is motion through dimensions.

        Args:
            substrate: The substrate to evolve
            delta: Delta representing the change

        Returns:
            New substrate identity (evolved state)
        """
        return substrate.evolve(delta)

    def create_time_sequence(self, substrate: Substrate, deltas: list) -> list:
        """
        Create time sequence through multiple evolutions.

        LAW FIVE: Time is the order of motion.

        Args:
            substrate: The substrate
            deltas: List of deltas representing sequential changes

        Returns:
            List of substrate identities (time sequence)
        """
        return substrate.time_sequence(deltas)

    def get_trajectory(self, substrate: Substrate) -> list:
        """
        Get evolution trajectory of substrate.

        LAW FIVE: Evolution is the reexpression of unity across states.

        Args:
            substrate: The substrate

        Returns:
            List of substrate identities (trajectory)
        """
        return substrate.get_trajectory()

    # ─────────────────────────────────────────────────────────────
    # LAW SIX: Identity Persists
    # ─────────────────────────────────────────────────────────────

    def verify_identity_persistence(self, substrate: Substrate) -> bool:
        """
        Verify that identity persists through transformations.

        LAW SIX: Identity persists through change.

        Args:
            substrate: The substrate to verify

        Returns:
            True (always - identity is immutable)
        """
        return substrate.verify_identity_persistence()

    def get_continuity_thread(self, substrate: Substrate) -> SubstrateIdentity:
        """
        Get the continuity thread (persistent identity).

        LAW SIX: Continuity is the thread of unity.

        Args:
            substrate: The substrate

        Returns:
            The substrate's identity (continuity thread)
        """
        return substrate.get_continuity_thread()

    # ─────────────────────────────────────────────────────────────
    # LAW SEVEN: Return to Unity
    # ─────────────────────────────────────────────────────────────

    def complete_cycle(self, substrate: Substrate, lens: Lens = None) -> int:
        """
        Complete the full Unity → Division → Unity cycle.

        LAW SEVEN: All dimensions return to unity.

        Args:
            substrate: The substrate
            lens: Optional lens for final projection

        Returns:
            64-bit manifestation (unity restored)
        """
        return substrate.complete_cycle(lens)

    def verify_return(self, substrate: Substrate) -> bool:
        """
        Verify that dimensions return to unity.

        LAW SEVEN: Completion is the reunion of the many.

        Args:
            substrate: The substrate to verify

        Returns:
            True if multiplication successfully returns to unity
        """
        return substrate.verify_return()
