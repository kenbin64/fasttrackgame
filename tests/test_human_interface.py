"""
Test Suite: Human Interface

Tests for the Human Interface layer, verifying:
- Law 11: Human-readable code compiles to substrate math
- Law 3: All attribute access through lenses
- Law 9: Invocation reveals truth
- Law 5: Immutability preserved through interface
- Law 6: No hard-coded dynamic values
"""

import pytest
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from interface.human import HumanInterface
from interface.dto import SubstrateDTO, LensDTO, InvocationResponse


class TestHumanInterfaceBasics:
    """Basic functionality of Human Interface"""
    
    @pytest.fixture
    def hi(self):
        return HumanInterface()
    
    def test_interface_instantiation(self, hi):
        """Human interface can be instantiated"""
        assert hi is not None
        assert hi._gateway is not None
        assert hi._translator is not None
        assert hi._validator is not None
        assert hi._invocator is not None
    
    def test_create_substrate_from_name(self, hi):
        """Create substrate with human-readable name"""
        substrate = hi.create_substrate(name="test_user")
        
        assert isinstance(substrate, SubstrateDTO)
        assert substrate.identity != 0  # Hashed from name
        assert substrate.expression_type == "constant"
    
    def test_create_substrate_with_expression_type(self, hi):
        """Create substrate with specific expression type"""
        substrate = hi.create_substrate(
            name="timestamp_test",
            expression_type="timestamp"
        )
        
        assert substrate.expression_type == "timestamp"
    
    def test_create_lens_from_name(self, hi):
        """Create lens with human-readable name"""
        lens = hi.create_lens(name="identity_view")
        
        assert isinstance(lens, LensDTO)
        assert lens.lens_id != 0
        assert lens.projection_type == "identity"
    
    def test_create_lens_with_mask(self, hi):
        """Create lens with mask projection"""
        lens = hi.create_lens(
            name="low_byte",
            projection_type="mask",
            mask=0xFF,
            shift=0
        )
        
        assert lens.projection_type == "mask"
        assert lens.projection_params["mask"] == 0xFF


class TestHumanInterfaceInvocation:
    """Test invocation through Human Interface"""
    
    @pytest.fixture
    def hi(self):
        return HumanInterface()
    
    def test_invoke_constant_substrate(self, hi):
        """Invoke substrate with constant expression"""
        substrate = hi.create_substrate(
            name="constant_test",
            expression_type="constant",
            value=42
        )
        lens = hi.create_lens(
            name="identity",
            projection_type="identity"
        )
        
        result = hi.invoke(substrate, lens)
        
        assert isinstance(result, InvocationResponse)
        assert result.value == 42
    
    def test_invoke_with_mask_lens(self, hi):
        """Invoke with masking lens"""
        substrate = hi.create_substrate(
            name="mask_test",
            expression_type="constant",
            value=0xAABBCCDD
        )
        lens = hi.create_lens(
            name="low_byte",
            projection_type="mask",
            mask=0xFF,
            shift=0
        )
        
        result = hi.invoke(substrate, lens)
        
        assert result.value == 0xDD
    
    def test_invoke_with_bit_extraction(self, hi):
        """Invoke with bit extraction lens"""
        substrate = hi.create_substrate(
            name="extract_test",
            expression_type="constant",
            value=0xFFFF0000
        )
        lens = hi.create_lens(
            name="high_16",
            projection_type="extract_bits",
            start=16,
            length=16
        )
        
        result = hi.invoke(substrate, lens)
        
        assert result.value == 0xFFFF
    
    def test_invocation_returns_audit_info(self, hi):
        """Invocation result includes substrate and lens IDs"""
        substrate = hi.create_substrate(name="audit_test", value=1)
        lens = hi.create_lens(name="audit_lens")
        
        result = hi.invoke(substrate, lens)
        
        assert result.substrate_id == substrate.identity
        assert result.lens_id == lens.lens_id


class TestHumanInterfacePromotion:
    """Test dimensional promotion through Human Interface"""
    
    @pytest.fixture
    def hi(self):
        return HumanInterface()
    
    def test_promote_creates_new_identity(self, hi):
        """Promotion creates new identity, not mutation"""
        substrate = hi.create_substrate(
            name="promote_test",
            expression_type="constant",
            value=100
        )
        
        new_id = hi.promote(
            substrate=substrate,
            attribute_value=200,
            change_description="version_increment"
        )
        
        # New identity is different from original
        assert new_id != substrate.identity
        assert isinstance(new_id, int)
        assert 0 <= new_id < 2**64
    
    def test_promote_is_deterministic(self, hi):
        """Same promotion parameters produce same result"""
        substrate = hi.create_substrate(
            name="deterministic_test",
            expression_type="constant",
            value=100
        )
        
        id1 = hi.promote(substrate, 200, "change_v1")
        id2 = hi.promote(substrate, 200, "change_v1")
        
        assert id1 == id2
    
    def test_promote_different_deltas(self, hi):
        """Different change descriptions produce different identities"""
        substrate = hi.create_substrate(
            name="delta_test",
            expression_type="constant",
            value=100
        )
        
        id1 = hi.promote(substrate, 200, "change_a")
        id2 = hi.promote(substrate, 200, "change_b")
        
        assert id1 != id2


class TestLaw6_NoDynamicValues:
    """Law 6: No hard-coded dynamic values"""
    
    @pytest.fixture
    def hi(self):
        return HumanInterface()
    
    def test_age_calculation_is_math(self, hi):
        """Age is calculated as math, not stored"""
        birth_ts = 1000000
        current_ts = 2000000
        
        age = hi.calculate_age(birth_ts, current_ts)
        
        # Age is derived from math
        assert age == current_ts - birth_ts
    
    def test_age_uses_current_time_by_default(self, hi):
        """Age calculation uses current time when not provided"""
        birth_ts = int(time.time() * 1000) - 86400000  # 1 day ago
        
        age = hi.calculate_age(birth_ts)
        
        # Age should be approximately 1 day in ms
        assert 86300000 < age < 86500000
    
    def test_timestamp_expression_is_dynamic(self, hi):
        """Timestamp expression computes fresh value each time"""
        substrate = hi.create_substrate(
            name="timestamp_dynamic",
            expression_type="timestamp"
        )
        lens = hi.create_lens(name="time_lens")
        
        result1 = hi.invoke(substrate, lens)
        time.sleep(0.01)
        result2 = hi.invoke(substrate, lens)
        
        # Values differ because timestamp is computed, not stored
        assert result2.value >= result1.value


class TestLaw11_HumanReadableCompilesDown:
    """Law 11: Human-readable code compiles to substrate math"""
    
    @pytest.fixture
    def hi(self):
        return HumanInterface()
    
    def test_name_hashes_to_identity(self, hi):
        """Human-readable names hash to 64-bit identity"""
        substrate = hi.create_substrate(name="alice")
        
        # Name compiled to 64-bit identity
        assert isinstance(substrate.identity, int)
        assert 0 <= substrate.identity < 2**64
    
    def test_same_name_same_identity(self, hi):
        """Same name produces same identity (deterministic)"""
        s1 = hi.create_substrate(name="consistent_test")
        s2 = hi.create_substrate(name="consistent_test")
        
        assert s1.identity == s2.identity
    
    def test_different_names_different_identities(self, hi):
        """Different names produce different identities"""
        s1 = hi.create_substrate(name="alice")
        s2 = hi.create_substrate(name="bob")
        
        assert s1.identity != s2.identity
    
    def test_expression_params_passed_through(self, hi):
        """Expression parameters compile to substrate expression"""
        substrate = hi.create_substrate(
            name="params_test",
            expression_type="derived",
            base=100,
            offset=50
        )
        lens = hi.create_lens(name="view")
        
        result = hi.invoke(substrate, lens)
        
        # Derived expression: base + offset
        assert result.value == 150


class TestHumanInterfaceDTOImmutability:
    """Test that DTOs maintain immutability"""
    
    @pytest.fixture
    def hi(self):
        return HumanInterface()
    
    def test_substrate_dto_is_frozen(self, hi):
        """SubstrateDTO is frozen dataclass"""
        substrate = hi.create_substrate(name="frozen_test")
        
        with pytest.raises(Exception):  # FrozenInstanceError
            substrate.identity = 999
    
    def test_lens_dto_is_frozen(self, hi):
        """LensDTO is frozen dataclass"""
        lens = hi.create_lens(name="frozen_lens")
        
        with pytest.raises(Exception):
            lens.lens_id = 999
    
    def test_invocation_response_is_frozen(self, hi):
        """InvocationResponse is frozen dataclass"""
        substrate = hi.create_substrate(name="response_test", value=1)
        lens = hi.create_lens(name="response_lens")
        
        result = hi.invoke(substrate, lens)
        
        with pytest.raises(Exception):
            result.value = 999


class TestHumanInterfaceSerialization:
    """Test DTO serialization for human readability"""
    
    @pytest.fixture
    def hi(self):
        return HumanInterface()
    
    def test_substrate_dto_to_dict(self, hi):
        """SubstrateDTO serializes to dict"""
        substrate = hi.create_substrate(
            name="serialize_test",
            expression_type="constant",
            value=42
        )
        
        d = substrate.to_dict()
        
        assert d["identity"] == substrate.identity
        assert d["expression_type"] == "constant"
        assert d["expression_params"]["value"] == 42
    
    def test_lens_dto_to_dict(self, hi):
        """LensDTO serializes to dict"""
        lens = hi.create_lens(
            name="lens_serialize",
            projection_type="mask",
            mask=0xFF
        )
        
        d = lens.to_dict()
        
        assert d["lens_id"] == lens.lens_id
        assert d["projection_type"] == "mask"
        assert d["projection_params"]["mask"] == 0xFF
    
    def test_invocation_response_to_dict(self, hi):
        """InvocationResponse serializes to dict"""
        substrate = hi.create_substrate(name="inv_test", value=100)
        lens = hi.create_lens(name="inv_lens")
        
        result = hi.invoke(substrate, lens)
        d = result.to_dict()
        
        assert d["value"] == 100
        assert d["substrate_id"] == substrate.identity
        assert d["lens_id"] == lens.lens_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
