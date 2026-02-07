"""
Test Suite: Kernel Laws

Tests proving the fundamental laws of the ButterflyFx Kernel.
The Kernel is pure mathematical expression - these tests verify
that all Kernel primitives obey the 15 Laws.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from kernel.substrate import Substrate, SubstrateIdentity
from kernel.manifold import Manifold
from kernel.lens import Lens
from kernel.delta import Delta
from kernel.dimensional import Dimension, promote
from kernel.srl import SRL, create_srl_identity


class TestLaw1_SubstratesAreSourceOfTruth:
    """Law 1: Substrates are the source of truth"""
    
    def test_substrate_is_complete_identity(self):
        """A substrate is a complete mathematical identity"""
        identity = SubstrateIdentity(0xDEADBEEFCAFEBABE)
        substrate = Substrate(identity, lambda: 42)
        
        assert substrate.identity == identity
        assert substrate.expression() == 42
    
    def test_substrate_has_mathematical_expression(self):
        """All attributes derived from substrate's math"""
        # Expression is a function, not stored data
        expression = lambda: 100 + 200
        identity = SubstrateIdentity(1)
        substrate = Substrate(identity, expression)
        
        # Value is computed, not stored
        assert substrate.expression() == 300
    
    def test_substrate_identity_is_64bit(self):
        """Identity must fit in 64 bits"""
        # Valid 64-bit identity
        SubstrateIdentity(0xFFFFFFFFFFFFFFFF)
        
        # Invalid: exceeds 64 bits
        with pytest.raises(ValueError):
            SubstrateIdentity(2**64)
        
        # Invalid: negative
        with pytest.raises(ValueError):
            SubstrateIdentity(-1)


class TestLaw5_ImmutabilityIsAbsolute:
    """Law 5: Immutability is absolute"""
    
    def test_substrate_identity_is_immutable(self):
        """SubstrateIdentity cannot be mutated"""
        identity = SubstrateIdentity(42)
        
        with pytest.raises(TypeError, match="immutable"):
            identity._identity = 100
        
        with pytest.raises(TypeError, match="immutable"):
            identity.new_attr = "test"
    
    def test_substrate_is_immutable(self):
        """Substrate cannot be mutated"""
        identity = SubstrateIdentity(1)
        substrate = Substrate(identity, lambda: 1)
        
        with pytest.raises(TypeError, match="immutable"):
            substrate._x1 = SubstrateIdentity(2)
        
        with pytest.raises(TypeError, match="immutable"):
            substrate.new_attr = "test"
    
    def test_manifold_is_immutable(self):
        """Manifold cannot be mutated"""
        identity = SubstrateIdentity(1)
        manifold = Manifold(identity, 1, 0xFF)
        
        with pytest.raises(TypeError, match="immutable"):
            manifold._dimension = 2
    
    def test_lens_is_immutable(self):
        """Lens cannot be mutated"""
        lens = Lens(1, lambda x: x)
        
        with pytest.raises(TypeError, match="immutable"):
            lens._lens_id = 2
    
    def test_delta_is_immutable(self):
        """Delta cannot be mutated"""
        delta = Delta(1)
        
        with pytest.raises(TypeError, match="immutable"):
            delta._z1 = 2
    
    def test_dimension_is_immutable(self):
        """Dimension cannot be mutated"""
        dim = Dimension(3)
        
        with pytest.raises(TypeError, match="immutable"):
            dim._level = 4
    
    def test_srl_is_immutable(self):
        """SRL cannot be mutated"""
        srl = SRL(
            SubstrateIdentity(1),
            lambda: 1,
            lambda x: SubstrateIdentity(x)
        )
        
        with pytest.raises(TypeError, match="immutable"):
            srl._srl_id = SubstrateIdentity(2)


class TestLaw8_EverythingFitsIn64Bits:
    """Law 8: Everything fits in 64 bits"""
    
    def test_substrate_identity_64bit(self):
        """SubstrateIdentity is 64-bit"""
        # Max valid value
        max_id = SubstrateIdentity(0xFFFFFFFFFFFFFFFF)
        assert max_id.value == 2**64 - 1
        
        # Zero is valid
        zero_id = SubstrateIdentity(0)
        assert zero_id.value == 0
    
    def test_lens_id_64bit(self):
        """Lens ID is 64-bit"""
        lens = Lens(0xFFFFFFFFFFFFFFFF, lambda x: x)
        assert lens.lens_id == 2**64 - 1
        
        with pytest.raises(ValueError):
            Lens(2**64, lambda x: x)
    
    def test_delta_64bit(self):
        """Delta z1 is 64-bit"""
        delta = Delta(0xFFFFFFFFFFFFFFFF)
        assert delta.z1 == 2**64 - 1
        
        with pytest.raises(ValueError):
            Delta(2**64)
    
    def test_manifold_form_can_be_64bit(self):
        """Manifold form expression is 64-bit"""
        identity = SubstrateIdentity(1)
        manifold = Manifold(identity, 1, 0xFFFFFFFFFFFFFFFF)
        assert manifold.form == 2**64 - 1


class TestLaw9_InvocationRevealsTruth:
    """Law 9: Invocation reveals truth"""
    
    def test_substrate_lens_invocation(self):
        """Computation = substrate → lens → invocation"""
        identity = SubstrateIdentity(42)
        substrate = Substrate(identity, lambda: 0xABCD)
        lens = Lens(1, lambda x: x >> 8)  # Extract high byte
        
        # Invocation reveals truth
        substrate_value = substrate.expression()
        result = lens.projection(substrate_value)
        
        assert result == 0xAB  # High byte of 0xABCD
    
    def test_nothing_precomputed(self):
        """Nothing is precomputed or stored"""
        counter = [0]
        
        def dynamic_expression():
            counter[0] += 1
            return counter[0]
        
        identity = SubstrateIdentity(1)
        substrate = Substrate(identity, dynamic_expression)
        
        # Each invocation computes anew
        assert substrate.expression() == 1
        assert substrate.expression() == 2
        assert substrate.expression() == 3


class TestLaw13_NonDuplication:
    """Law 13: If two substrates have identical expressions, same identity"""
    
    def test_identical_identities_are_equal(self):
        """Same identity value = equal substrates"""
        id1 = SubstrateIdentity(42)
        id2 = SubstrateIdentity(42)
        
        assert id1 == id2
        assert hash(id1) == hash(id2)
    
    def test_substrate_equality_by_identity(self):
        """Substrates are equal by identity, not expression"""
        id1 = SubstrateIdentity(42)
        
        s1 = Substrate(id1, lambda: 1)
        s2 = Substrate(id1, lambda: 2)  # Different expression, same identity
        
        assert s1 == s2  # Same identity = same substrate


class TestLaw14_DimensionalContainment:
    """Law 14: Higher dimension contains all lower dimensions"""
    
    def test_dimension_containment(self):
        """Higher dimensions contain lower dimensions"""
        dim0 = Dimension(0)
        dim1 = Dimension(1)
        dim2 = Dimension(2)
        dim3 = Dimension(3)
        
        # Higher contains lower
        assert dim3.contains(dim0)
        assert dim3.contains(dim1)
        assert dim3.contains(dim2)
        assert dim3.contains(dim3)  # Contains itself
        
        # Lower does not contain higher
        assert not dim0.contains(dim1)
        assert not dim1.contains(dim2)
    
    def test_dimensional_promotion(self):
        """Promotion produces new identity in next dimension"""
        x1 = SubstrateIdentity(0xAABBCCDDEEFF0011)
        y1 = 0x1122334455667788
        delta = Delta(0x0F0F0F0F0F0F0F0F)
        
        # Promote to new identity
        m1 = promote(x1, y1, delta)
        
        # Result is different from original
        assert m1.value != x1.value
        
        # Result is deterministic
        m1_again = promote(x1, y1, delta)
        assert m1.value == m1_again.value
    
    def test_promotion_is_change_mechanism(self):
        """Change occurs only through promotion"""
        x1 = SubstrateIdentity(100)
        y1 = 200
        
        # Different deltas produce different results
        delta1 = Delta(1)
        delta2 = Delta(2)
        
        m1 = promote(x1, y1, delta1)
        m2 = promote(x1, y1, delta2)
        
        assert m1.value != m2.value


class TestLaw2_ManifoldsAreShapes:
    """Law 2: Manifolds are shapes of substrates"""
    
    def test_manifold_references_substrate(self):
        """Manifold is dimensional expression of substrate"""
        substrate_id = SubstrateIdentity(42)
        manifold = Manifold(substrate_id, dimension=3, form_expression=0xFF)
        
        assert manifold.substrate_id == substrate_id
        assert manifold.dimension == 3
        assert manifold.form == 0xFF
    
    def test_single_substrate_infinite_manifolds(self):
        """Single substrate can produce infinite manifolds"""
        substrate_id = SubstrateIdentity(1)
        
        manifolds = [
            Manifold(substrate_id, dim, form)
            for dim in range(10)
            for form in range(10)
        ]
        
        # All refer to same substrate
        assert all(m.substrate_id == substrate_id for m in manifolds)
        assert len(manifolds) == 100


class TestLaw3_LensesProvideContext:
    """Law 3: Lenses provide context"""
    
    def test_lens_does_not_modify(self):
        """Lens does not modify substrate - only projects"""
        original_value = 0xFFFFFFFF
        lens = Lens(1, lambda x: x & 0xFF)  # Extract low byte
        
        result = lens.projection(original_value)
        
        # Original is unchanged, result is projection
        assert result == 0xFF
        assert original_value == 0xFFFFFFFF
    
    def test_lens_selects_dimensional_slice(self):
        """Lens selects dimensional slice"""
        value = 0xAABBCCDD
        
        # Different lenses extract different "slices"
        lens_low = Lens(1, lambda x: x & 0xFF)
        lens_high = Lens(2, lambda x: (x >> 24) & 0xFF)
        
        assert lens_low.projection(value) == 0xDD
        assert lens_high.projection(value) == 0xAA


class TestLaw4_SRLsDefineConnections:
    """Law 4: SRLs define connections"""
    
    def test_srl_encodes_connection_rules(self):
        """SRL is substrate encoding connection rules"""
        srl_id = SubstrateIdentity(1)
        srl = SRL(
            srl_id,
            resource_expression=lambda: 42,
            spawn_rule=lambda x: SubstrateIdentity(x * 2)
        )
        
        assert srl.identity == srl_id
        assert srl.resource_expression() == 42
    
    def test_srl_spawns_new_substrates(self):
        """SRL spawns new substrates from external data"""
        srl_id = SubstrateIdentity(1)
        srl = SRL(
            srl_id,
            resource_expression=lambda: 0,
            spawn_rule=lambda x: SubstrateIdentity(x)
        )
        
        # Spawn substrates from "external" data
        spawned1 = srl.spawn(100)
        spawned2 = srl.spawn(200)
        
        assert spawned1.value == 100
        assert spawned2.value == 200
    
    def test_srl_identity_creation(self):
        """SRL identity encodes resource type/namespace/path"""
        srl_id = create_srl_identity(
            resource_type=1,
            resource_namespace=2,
            resource_path=3
        )
        
        # Identity is 64-bit
        assert 0 <= srl_id < 2**64
        
        # Deterministic
        srl_id2 = create_srl_identity(1, 2, 3)
        assert srl_id == srl_id2


class TestKernelIntegration:
    """Integration tests for Kernel layer"""
    
    def test_full_computation_pattern(self):
        """Test substrate → lens → invocation pattern"""
        # Create substrate with expression
        identity = SubstrateIdentity(0x123456789ABCDEF0)
        substrate = Substrate(identity, lambda: 0xDEADBEEF)
        
        # Create lens for projection
        lens = Lens(1, lambda x: x ^ 0xFFFFFFFF)  # Bitwise NOT
        
        # Invoke
        substrate_value = substrate.expression()
        result = lens.projection(substrate_value)
        
        assert result == 0xDEADBEEF ^ 0xFFFFFFFF
    
    def test_promotion_chain(self):
        """Test chain of dimensional promotions"""
        x1 = SubstrateIdentity(1)
        
        # Chain of changes
        m1 = promote(x1, 10, Delta(100))
        m2 = promote(m1, 20, Delta(200))
        m3 = promote(m2, 30, Delta(300))
        
        # Each promotion produces unique identity
        assert x1.value != m1.value
        assert m1.value != m2.value
        assert m2.value != m3.value
        
        # Chain is deterministic
        m1_verify = promote(x1, 10, Delta(100))
        assert m1.value == m1_verify.value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
