"""
Test Suite: AI Interface

Tests for the AI Interface layer, verifying:
- Law 15: AI must never fabricate substrate behavior
- Instruction execution
- Claim verification against substrate truth
- Audit trails for all derivations
- Embedding translation
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from interface.ai import AIInterface, AIInterfaceError, FabricationGuard
from interface.dto import SubstrateDTO, LensDTO


class TestAIInterfaceBasics:
    """Basic functionality of AI Interface"""
    
    @pytest.fixture
    def ai(self):
        return AIInterface()
    
    def test_interface_instantiation(self, ai):
        """AI interface can be instantiated"""
        assert ai is not None
        assert ai._gateway is not None
        assert ai._translator is not None
        assert ai._validator is not None
        assert ai._invocator is not None
        assert ai._guard is not None
    
    def test_fabrication_guard_exists(self, ai):
        """AI interface has fabrication guard"""
        assert isinstance(ai._guard, FabricationGuard)


class TestLaw15_NoFabrication:
    """Law 15: AI must never fabricate substrate behavior"""
    
    @pytest.fixture
    def ai(self):
        return AIInterface()
    
    def test_valid_claim_passes_verification(self, ai):
        """Correct claims pass verification"""
        substrate = SubstrateDTO(
            identity=42,
            expression_type="constant",
            expression_params={"value": 100}
        )
        lens = LensDTO(
            lens_id=1,
            projection_type="identity",
            projection_params={}
        )
        
        # Claim the correct value
        is_valid, actual = ai.verify_claim(substrate, lens, claimed_value=100)
        
        assert is_valid is True
        assert actual == 100
    
    def test_fabricated_claim_fails_verification(self, ai):
        """Fabricated claims fail verification"""
        substrate = SubstrateDTO(
            identity=42,
            expression_type="constant",
            expression_params={"value": 100}
        )
        lens = LensDTO(
            lens_id=1,
            projection_type="identity",
            projection_params={}
        )
        
        # Claim a fabricated (wrong) value
        is_valid, actual = ai.verify_claim(substrate, lens, claimed_value=999)
        
        assert is_valid is False
        assert actual == 100  # Actual substrate truth
    
    def test_fabrication_guard_detects_mismatch(self):
        """FabricationGuard raises on value mismatch"""
        guard = FabricationGuard()
        
        with pytest.raises(AIInterfaceError, match="Fabrication detected"):
            guard.validate_not_fabricated(
                claimed_value=50,
                derived_value=100
            )
    
    def test_fabrication_guard_accepts_match(self):
        """FabricationGuard accepts matching values"""
        guard = FabricationGuard()
        
        # Should not raise
        guard.validate_not_fabricated(
            claimed_value=100,
            derived_value=100
        )
    
    def test_fabrication_guard_type_mismatch(self):
        """FabricationGuard detects type mismatches"""
        guard = FabricationGuard()
        
        with pytest.raises(AIInterfaceError, match="Type mismatch"):
            guard.validate_not_fabricated(
                claimed_value=100,  # int
                derived_value="100"  # string
            )


class TestInstructionExecution:
    """Test AI instruction execution"""
    
    @pytest.fixture
    def ai(self):
        return AIInterface()
    
    def test_invoke_instruction(self, ai):
        """Execute invoke instruction"""
        result = ai.execute_instruction({
            "operation": "invoke",
            "params": {
                "substrate_identity": 42,
                "lens_id": 1,
                "expression_type": "constant",
                "expression_params": {"value": 100}
            }
        })
        
        assert result["value"] == 100
        assert "audit" in result
    
    def test_promote_instruction(self, ai):
        """Execute promote instruction"""
        result = ai.execute_instruction({
            "operation": "promote",
            "params": {
                "substrate_identity": 42,
                "expression_type": "constant",
                "expression_params": {"value": 42},
                "attribute_value": 100,
                "delta_z1": 200
            }
        })
        
        assert "new_identity" in result
        assert "new_identity_hex" in result
        assert result["new_identity"] != 42  # Changed
    
    def test_create_substrate_instruction(self, ai):
        """Execute create_substrate instruction"""
        result = ai.execute_instruction({
            "operation": "create_substrate",
            "params": {
                "name": "test_entity",
                "expression_type": "constant"
            }
        })
        
        assert "identity" in result
        assert "identity_hex" in result
        assert isinstance(result["identity"], int)
    
    def test_create_lens_instruction(self, ai):
        """Execute create_lens instruction"""
        result = ai.execute_instruction({
            "operation": "create_lens",
            "params": {
                "name": "test_lens",
                "projection_type": "identity"
            }
        })
        
        assert "lens_id" in result
        assert "lens_id_hex" in result
    
    def test_unknown_operation_raises(self, ai):
        """Unknown operations raise error"""
        with pytest.raises(AIInterfaceError, match="Unknown operation"):
            ai.execute_instruction({
                "operation": "invalid_op",
                "params": {}
            })


class TestAuditTrails:
    """Test audit trail generation for AI operations"""
    
    @pytest.fixture
    def ai(self):
        return AIInterface()
    
    def test_invoke_includes_audit(self, ai):
        """Invoke instruction includes audit trail"""
        result = ai.execute_instruction({
            "operation": "invoke",
            "params": {
                "substrate_identity": 100,
                "lens_id": 200,
                "expression_type": "constant",
                "expression_params": {"value": 42}
            }
        })
        
        audit = result["audit"]
        assert "0x" in audit["substrate_id"]  # Hex format
        assert "0x" in audit["lens_id"]
        assert audit["operation"] == "invoke"
        assert audit["fabricated"] is False
        assert audit["source"] == "substrate_math"
    
    def test_promote_includes_audit(self, ai):
        """Promote instruction includes audit trail"""
        result = ai.execute_instruction({
            "operation": "promote",
            "params": {
                "substrate_identity": 100,
                "attribute_value": 200,
                "delta_z1": 300
            }
        })
        
        audit = result["audit"]
        assert audit["fabricated"] is False
    
    def test_audit_trail_is_deterministic(self, ai):
        """Same operation produces same audit info"""
        params = {
            "operation": "invoke",
            "params": {
                "substrate_identity": 42,
                "lens_id": 1
            }
        }
        
        result1 = ai.execute_instruction(params)
        result2 = ai.execute_instruction(params)
        
        assert result1["audit"]["substrate_id"] == result2["audit"]["substrate_id"]
        assert result1["audit"]["lens_id"] == result2["audit"]["lens_id"]


class TestEmbeddingTranslation:
    """Test embedding to identity translation"""
    
    @pytest.fixture
    def ai(self):
        return AIInterface()
    
    def test_embedding_to_identity(self, ai):
        """Translate embedding vector to 64-bit identity"""
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
        
        identity = ai.embedding_to_identity(embedding)
        
        assert isinstance(identity, int)
        assert 0 <= identity < 2**64
    
    def test_embedding_deterministic(self, ai):
        """Same embedding produces same identity"""
        embedding = [0.1, 0.2, 0.3, 0.4]
        
        id1 = ai.embedding_to_identity(embedding)
        id2 = ai.embedding_to_identity(embedding)
        
        assert id1 == id2
    
    def test_different_embeddings_different_identities(self, ai):
        """Different embeddings produce different identities"""
        emb1 = [0.1, 0.2, 0.3, 0.4]
        emb2 = [0.5, 0.6, 0.7, 0.8]
        
        id1 = ai.embedding_to_identity(emb1)
        id2 = ai.embedding_to_identity(emb2)
        
        assert id1 != id2
    
    def test_empty_embedding(self, ai):
        """Empty embedding returns 0"""
        identity = ai.embedding_to_identity([])
        assert identity == 0


class TestClaimVerification:
    """Test AI claim verification against substrate truth"""
    
    @pytest.fixture
    def ai(self):
        return AIInterface()
    
    def test_verify_correct_integer_claim(self, ai):
        """Verify correct integer claim"""
        substrate = SubstrateDTO(
            identity=1,
            expression_type="constant",
            expression_params={"value": 42}
        )
        lens = LensDTO(lens_id=1, projection_type="identity", projection_params={})
        
        is_valid, actual = ai.verify_claim(substrate, lens, 42)
        
        assert is_valid is True
        assert actual == 42
    
    def test_verify_incorrect_integer_claim(self, ai):
        """Verify incorrect integer claim""" 
        substrate = SubstrateDTO(
            identity=1,
            expression_type="constant",
            expression_params={"value": 42}
        )
        lens = LensDTO(lens_id=1, projection_type="identity", projection_params={})
        
        is_valid, actual = ai.verify_claim(substrate, lens, 999)
        
        assert is_valid is False
        assert actual == 42  # Returns actual truth
    
    def test_verify_with_mask_lens(self, ai):
        """Verify claim with masking lens"""
        substrate = SubstrateDTO(
            identity=1,
            expression_type="constant",
            expression_params={"value": 0xAABBCCDD}
        )
        lens = LensDTO(
            lens_id=1, 
            projection_type="mask", 
            projection_params={"mask": 0xFF, "shift": 0}
        )
        
        # Correct claim: low byte
        is_valid, actual = ai.verify_claim(substrate, lens, 0xDD)
        assert is_valid is True
        
        # Incorrect claim
        is_valid, actual = ai.verify_claim(substrate, lens, 0xAA)
        assert is_valid is False


class TestAIInterfaceCompliance:
    """Test AI interface compliance with all relevant laws"""
    
    @pytest.fixture
    def ai(self):
        return AIInterface()
    
    def test_law9_invocation_reveals_truth(self, ai):
        """Law 9: Invocation reveals truth, nothing precomputed"""
        counter = {"value": 0}
        
        # Each invoke should recompute
        result1 = ai.execute_instruction({
            "operation": "invoke",
            "params": {
                "substrate_identity": 1,
                "lens_id": 1,
                "expression_type": "timestamp"  # Dynamic
            }
        })
        
        import time
        time.sleep(0.01)
        
        result2 = ai.execute_instruction({
            "operation": "invoke",
            "params": {
                "substrate_identity": 1,
                "lens_id": 1,
                "expression_type": "timestamp"
            }
        })
        
        # Values differ because timestamp is computed fresh
        assert result2["value"] >= result1["value"]
    
    def test_law8_64bit_identities(self, ai):
        """Law 8: All identities fit in 64 bits"""
        result = ai.execute_instruction({
            "operation": "create_substrate",
            "params": {"name": "test_64bit"}
        })
        
        identity = result["identity"]
        assert 0 <= identity < 2**64
    
    def test_law5_immutability_through_promotion(self, ai):
        """Law 5: Change only through promotion, not mutation"""
        # Create initial
        create_result = ai.execute_instruction({
            "operation": "create_substrate",
            "params": {"name": "immutable_test"}
        })
        original_id = create_result["identity"]
        
        # Promote to create new identity
        promote_result = ai.execute_instruction({
            "operation": "promote",
            "params": {
                "substrate_identity": original_id,
                "attribute_value": 100,
                "delta_z1": 999
            }
        })
        
        new_id = promote_result["new_identity"]
        
        # Original is preserved, new identity created
        assert new_id != original_id


class TestFabricationGuardDetails:
    """Detailed tests for FabricationGuard"""
    
    def test_validate_derivation_path(self):
        """Derivation path audit is complete"""
        audit = FabricationGuard.validate_derivation_path(
            substrate_id=0xDEADBEEF,
            lens_id=0xCAFEBABE,
            operation="test_op"
        )
        
        assert audit["substrate_id"] == "0x00000000DEADBEEF"
        assert audit["lens_id"] == "0x00000000CAFEBABE"
        assert audit["operation"] == "test_op"
        assert audit["fabricated"] is False
        assert audit["source"] == "substrate_math"
    
    def test_numeric_tolerance(self):
        """Numeric comparison respects tolerance"""
        guard = FabricationGuard()
        
        # Within tolerance
        guard.validate_not_fabricated(100.0, 100.0, tolerance=0.01)
        
        # Outside tolerance
        with pytest.raises(AIInterfaceError):
            guard.validate_not_fabricated(100.0, 101.0, tolerance=0.5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
