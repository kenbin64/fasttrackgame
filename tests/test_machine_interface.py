"""
Test Suite: Machine Interface

Tests for the Machine Interface layer, verifying:
- Binary serialization (64-bit identities)
- Direct numeric operations
- Batch processing with brute-force protection (Law 12)
- High-throughput patterns
"""

import pytest
import sys
import struct
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from interface.machine import MachineInterface
from interface.dto import (
    SubstrateDTO, 
    LensDTO, 
    InvocationRequest, 
    InvocationResponse,
    ManifoldDTO,
)
from core.validator import ValidationError


class TestMachineInterfaceBasics:
    """Basic functionality of Machine Interface"""
    
    @pytest.fixture
    def mi(self):
        return MachineInterface()
    
    def test_interface_instantiation(self, mi):
        """Machine interface can be instantiated"""
        assert mi is not None
        assert mi._gateway is not None
        assert mi._translator is not None
        assert mi._validator is not None
        assert mi._invocator is not None
    
    def test_create_substrate_direct(self, mi):
        """Create substrate with direct numeric identity"""
        substrate = mi.create_substrate_direct(
            identity=0xDEADBEEFCAFEBABE,
            expression_type="constant",
            expression_params={"value": 42}
        )
        
        assert isinstance(substrate, SubstrateDTO)
        assert substrate.identity == 0xDEADBEEFCAFEBABE
        assert substrate.expression_type == "constant"
    
    def test_create_lens_direct(self, mi):
        """Create lens with direct numeric identity"""
        lens = mi.create_lens_direct(
            lens_id=0x1234567890ABCDEF,
            projection_type="identity",
            projection_params={}
        )
        
        assert isinstance(lens, LensDTO)
        assert lens.lens_id == 0x1234567890ABCDEF


class TestBinarySerialization:
    """Test binary serialization for machine protocols"""
    
    @pytest.fixture
    def mi(self):
        return MachineInterface()
    
    def test_serialize_identity_to_bytes(self, mi):
        """Serialize 64-bit identity to bytes"""
        identity = 0xDEADBEEFCAFEBABE
        
        binary = mi.serialize_identity(identity)
        
        assert isinstance(binary, bytes)
        assert len(binary) == 8  # 64 bits = 8 bytes
    
    def test_deserialize_identity_from_bytes(self, mi):
        """Deserialize bytes to 64-bit identity"""
        original = 0xDEADBEEFCAFEBABE
        binary = mi.serialize_identity(original)
        
        restored = mi.deserialize_identity(binary)
        
        assert restored == original
    
    def test_serialize_roundtrip(self, mi):
        """Serialize/deserialize roundtrip preserves value"""
        test_values = [
            0,
            1,
            0xFFFFFFFFFFFFFFFF,
            0xDEADBEEFCAFEBABE,
            0x0000000000000001,
        ]
        
        for val in test_values:
            binary = mi.serialize_identity(val)
            restored = mi.deserialize_identity(binary)
            assert restored == val, f"Roundtrip failed for {val}"
    
    def test_deserialize_invalid_length(self, mi):
        """Deserialize rejects wrong byte length"""
        with pytest.raises(ValueError, match="exactly 8 bytes"):
            mi.deserialize_identity(b"\x00\x00\x00\x00")
    
    def test_serialize_substrate_dto(self, mi):
        """Serialize SubstrateDTO to compact binary"""
        substrate = mi.create_substrate_direct(
            identity=42,
            expression_type="constant",
            expression_params={"value": 100}
        )
        
        binary = mi.serialize_substrate_dto(substrate)
        
        assert isinstance(binary, bytes)
        assert len(binary) > 8  # At least identity
    
    def test_deserialize_substrate_dto(self, mi):
        """Deserialize binary to SubstrateDTO"""
        original = mi.create_substrate_direct(
            identity=0xCAFEBABE,
            expression_type="constant",
            expression_params={"value": 999}
        )
        
        binary = mi.serialize_substrate_dto(original)
        restored = mi.deserialize_substrate_dto(binary)
        
        assert restored.identity == original.identity
        assert restored.expression_type == original.expression_type
        assert restored.expression_params == original.expression_params


class TestDirectNumericOperations:
    """Test direct numeric operations for machine efficiency"""
    
    @pytest.fixture
    def mi(self):
        return MachineInterface()
    
    def test_direct_64bit_max(self, mi):
        """Direct operations handle max 64-bit value"""
        substrate = mi.create_substrate_direct(
            identity=0xFFFFFFFFFFFFFFFF,
            expression_type="constant",
            expression_params={"value": 0xFFFFFFFFFFFFFFFF}
        )
        
        assert substrate.identity == 0xFFFFFFFFFFFFFFFF
    
    def test_direct_zero(self, mi):
        """Direct operations handle zero"""
        substrate = mi.create_substrate_direct(
            identity=0,
            expression_type="constant",
            expression_params={"value": 0}
        )
        
        assert substrate.identity == 0
    
    def test_direct_validation_rejects_oversized(self, mi):
        """Validation rejects values exceeding 64 bits"""
        with pytest.raises(ValidationError):
            mi.create_substrate_direct(
                identity=2**64,  # Too large
                expression_type="constant",
                expression_params={}
            )


class TestBatchOperations:
    """Test batch processing with Law 12 enforcement"""
    
    @pytest.fixture
    def mi(self):
        return MachineInterface()
    
    def test_batch_invocation(self, mi):
        """Batch invocation processes multiple requests"""
        substrate = mi.create_substrate_direct(
            identity=100,
            expression_type="constant",
            expression_params={"value": 42}
        )
        
        lenses = [
            mi.create_lens_direct(i, "identity", {})
            for i in range(5)
        ]
        
        requests = [
            InvocationRequest(substrate=substrate, lens=lens)
            for lens in lenses
        ]
        
        results = mi.invoke_batch(requests)
        
        assert len(results) == 5
        assert all(r.value == 42 for r in results)
    
    def test_batch_returns_individual_lens_ids(self, mi):
        """Batch invocation preserves lens IDs in results"""
        substrate = mi.create_substrate_direct(
            identity=1,
            expression_type="constant",
            expression_params={"value": 1}
        )
        
        lens_ids = [10, 20, 30]
        requests = [
            InvocationRequest(
                substrate=substrate,
                lens=mi.create_lens_direct(lid, "identity", {})
            )
            for lid in lens_ids
        ]
        
        results = mi.invoke_batch(requests)
        
        result_lens_ids = [r.lens_id for r in results]
        assert result_lens_ids == lens_ids
    
    def test_law12_brute_force_protection(self, mi):
        """Law 12: Batch rejects brute-force sized operations"""
        substrate = mi.create_substrate_direct(
            identity=1,
            expression_type="constant",
            expression_params={"value": 1}
        )
        lens = mi.create_lens_direct(1, "identity", {})
        
        # Create oversized batch (>1000 items)
        requests = [
            InvocationRequest(substrate=substrate, lens=lens)
            for _ in range(1001)
        ]
        
        with pytest.raises(ValidationError, match="brute-force"):
            mi.invoke_batch(requests)
    
    def test_batch_below_threshold_succeeds(self, mi):
        """Batch below brute-force threshold succeeds"""
        substrate = mi.create_substrate_direct(
            identity=1,
            expression_type="constant",
            expression_params={"value": 1}
        )
        lens = mi.create_lens_direct(1, "identity", {})
        
        # Create batch at threshold (exactly 1000)
        requests = [
            InvocationRequest(substrate=substrate, lens=lens)
            for _ in range(1000)
        ]
        
        results = mi.invoke_batch(requests)
        assert len(results) == 1000


class TestManifoldCreation:
    """Test manifold creation through Machine Interface"""
    
    @pytest.fixture
    def mi(self):
        return MachineInterface()
    
    def test_create_manifold(self, mi):
        """Create manifold from substrate"""
        substrate = mi.create_substrate_direct(
            identity=42,
            expression_type="constant",
            expression_params={"value": 1}
        )
        
        manifold = mi.create_manifold(
            substrate=substrate,
            dimension=3,
            form_expression=0xFF00FF00
        )
        
        assert isinstance(manifold, ManifoldDTO)
        assert manifold.substrate_id == substrate.identity
        assert manifold.dimension == 3
        assert manifold.form_expression == 0xFF00FF00
    
    def test_manifold_form_64bit_validation(self, mi):
        """Manifold form expression must be 64-bit"""
        substrate = mi.create_substrate_direct(
            identity=1,
            expression_type="constant",
            expression_params={}
        )
        
        with pytest.raises(ValidationError):
            mi.create_manifold(
                substrate=substrate,
                dimension=1,
                form_expression=2**64  # Too large
            )


class TestMachineInterfaceDTOSerialization:
    """Test DTO JSON serialization for machine protocols"""
    
    @pytest.fixture
    def mi(self):
        return MachineInterface()
    
    def test_invocation_request_to_dict(self, mi):
        """InvocationRequest serializes to dict"""
        substrate = mi.create_substrate_direct(
            identity=100,
            expression_type="constant",
            expression_params={"value": 42}
        )
        lens = mi.create_lens_direct(200, "identity", {})
        
        request = InvocationRequest(substrate=substrate, lens=lens)
        d = request.to_dict()
        
        assert d["substrate"]["identity"] == 100
        assert d["lens"]["lens_id"] == 200
    
    def test_invocation_request_from_dict(self, mi):
        """InvocationRequest deserializes from dict"""
        data = {
            "substrate": {
                "identity": 100,
                "expression_type": "constant",
                "expression_params": {"value": 42}
            },
            "lens": {
                "lens_id": 200,
                "projection_type": "identity",
                "projection_params": {}
            }
        }
        
        request = InvocationRequest.from_dict(data)
        
        assert request.substrate.identity == 100
        assert request.lens.lens_id == 200
    
    def test_manifold_dto_serialization(self, mi):
        """ManifoldDTO serializes and deserializes"""
        substrate = mi.create_substrate_direct(
            identity=42,
            expression_type="constant",
            expression_params={}
        )
        manifold = mi.create_manifold(substrate, 5, 0xABCD)
        
        d = manifold.to_dict()
        restored = ManifoldDTO.from_dict(d)
        
        assert restored.substrate_id == manifold.substrate_id
        assert restored.dimension == manifold.dimension
        assert restored.form_expression == manifold.form_expression


class TestMachineInterfaceValidation:
    """Test validation in Machine Interface"""
    
    @pytest.fixture
    def mi(self):
        return MachineInterface()
    
    def test_serialize_validates_64bit(self, mi):
        """Serialization validates 64-bit constraint"""
        with pytest.raises(ValidationError):
            mi.serialize_identity(2**64)
    
    def test_create_substrate_validates_identity(self, mi):
        """create_substrate_direct validates identity"""
        with pytest.raises(ValidationError):
            mi.create_substrate_direct(
                identity=-1,  # Negative invalid
                expression_type="constant",
                expression_params={}
            )
    
    def test_create_lens_validates_id(self, mi):
        """create_lens_direct validates lens_id"""
        with pytest.raises(ValidationError):
            mi.create_lens_direct(
                lens_id=2**64,  # Too large
                projection_type="identity",
                projection_params={}
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
