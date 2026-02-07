"""
Test Suite: Core Layer

Tests for the Core layer - the bridge between Interface and Kernel.
Verifies:
- Gateway is sole Kernel accessor
- Translator compiles external to math
- Validator enforces laws
- Invocator executes substrate → lens → truth
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.gateway import KernelGateway
from core.translator import Translator, TranslationError
from core.validator import Validator, ValidationError
from core.invocation import Invocator, InvocationResult


class TestKernelGateway:
    """Test KernelGateway - sole access to Kernel"""
    
    @pytest.fixture
    def gateway(self):
        return KernelGateway()
    
    def test_gateway_is_singleton(self):
        """Gateway is singleton - one access point"""
        g1 = KernelGateway()
        g2 = KernelGateway()
        
        assert g1 is g2
    
    def test_create_identity(self, gateway):
        """Gateway creates substrate identity"""
        identity = gateway.create_identity(42)
        
        assert identity.value == 42
    
    def test_create_substrate(self, gateway):
        """Gateway creates substrate"""
        identity = gateway.create_identity(1)
        substrate = gateway.create_substrate(identity, lambda: 100)
        
        assert substrate.identity == identity
        assert substrate.expression() == 100
    
    def test_create_lens(self, gateway):
        """Gateway creates lens"""
        lens = gateway.create_lens(1, lambda x: x * 2)
        
        assert lens.lens_id == 1
        assert lens.projection(10) == 20
    
    def test_invoke(self, gateway):
        """Gateway performs invocation"""
        identity = gateway.create_identity(1)
        substrate = gateway.create_substrate(identity, lambda: 42)
        lens = gateway.create_lens(1, lambda x: x + 1)
        
        result = gateway.invoke(substrate, lens)
        
        assert result == 43
    
    def test_create_delta(self, gateway):
        """Gateway creates delta"""
        delta = gateway.create_delta(999)
        
        assert delta.z1 == 999
    
    def test_promote_substrate(self, gateway):
        """Gateway promotes substrate to new identity"""
        identity = gateway.create_identity(100)
        substrate = gateway.create_substrate(identity, lambda: 100)
        delta = gateway.create_delta(50)
        
        new_id = gateway.promote_substrate(substrate, 200, delta)
        
        assert new_id.value != identity.value
    
    def test_create_manifold(self, gateway):
        """Gateway creates manifold"""
        identity = gateway.create_identity(1)
        substrate = gateway.create_substrate(identity, lambda: 1)
        
        manifold = gateway.create_manifold(substrate, dimension=3, form_expression=0xFF)
        
        assert manifold.substrate_id == identity
        assert manifold.dimension == 3
        assert manifold.form == 0xFF
    
    def test_get_dimension(self, gateway):
        """Gateway retrieves dimension"""
        dim = gateway.get_dimension(5)
        
        assert dim.level == 5


class TestTranslator:
    """Test Translator - external to math compilation"""
    
    @pytest.fixture
    def translator(self):
        return Translator()
    
    def test_translate_int_identity(self, translator):
        """Translate integer to identity"""
        result = translator.translate_identity(42)
        
        assert result == 42
    
    def test_translate_string_identity(self, translator):
        """Translate string to 64-bit identity"""
        result = translator.translate_identity("test_name")
        
        assert isinstance(result, int)
        assert 0 <= result < 2**64
    
    def test_translate_bytes_identity(self, translator):
        """Translate bytes to identity"""
        result = translator.translate_identity(b"binary_data")
        
        assert isinstance(result, int)
        assert 0 <= result < 2**64
    
    def test_translate_same_string_same_identity(self, translator):
        """Same string produces same identity"""
        id1 = translator.translate_identity("consistent")
        id2 = translator.translate_identity("consistent")
        
        assert id1 == id2
    
    def test_translate_different_strings_different_identities(self, translator):
        """Different strings produce different identities"""
        id1 = translator.translate_identity("alpha")
        id2 = translator.translate_identity("beta")
        
        assert id1 != id2
    
    def test_translate_oversized_int_raises(self, translator):
        """Oversized integer raises TranslationError"""
        with pytest.raises(TranslationError, match="exceeds 64 bits"):
            translator.translate_identity(2**64)
    
    def test_translate_constant_expression(self, translator):
        """Translate constant expression"""
        expr = translator.translate_expression("constant", {"value": 42})
        
        assert callable(expr)
        assert expr() == 42
    
    def test_translate_timestamp_expression(self, translator):
        """Translate timestamp expression"""
        import time
        expr = translator.translate_expression("timestamp", {})
        
        before = int(time.time() * 1000)
        result = expr()
        after = int(time.time() * 1000)
        
        assert before <= result <= after
    
    def test_translate_derived_expression(self, translator):
        """Translate derived expression"""
        expr = translator.translate_expression("derived", {"base": 100, "offset": 50})
        
        assert expr() == 150
    
    def test_translate_unknown_expression_raises(self, translator):
        """Unknown expression type raises error"""
        with pytest.raises(TranslationError, match="Unknown expression type"):
            translator.translate_expression("nonexistent", {})
    
    def test_translate_identity_projection(self, translator):
        """Translate identity projection"""
        proj = translator.translate_projection("identity", {})
        
        assert proj(42) == 42
    
    def test_translate_mask_projection(self, translator):
        """Translate mask projection"""
        proj = translator.translate_projection("mask", {"mask": 0xFF, "shift": 8})
        
        # 0xAABB >> 8 = 0xAA, 0xAA & 0xFF = 0xAA
        assert proj(0xAABB) == 0xAA
    
    def test_translate_extract_bits_projection(self, translator):
        """Translate extract_bits projection"""
        proj = translator.translate_projection("extract_bits", {"start": 4, "length": 4})
        
        # 0xFF >> 4 = 0xF, 0xF & 0xF = 0xF
        assert proj(0xFF) == 0xF


class TestValidator:
    """Test Validator - law enforcement"""
    
    def test_validate_64bit_valid(self):
        """Valid 64-bit values pass"""
        Validator.validate_64bit(0, "zero")
        Validator.validate_64bit(42, "answer")
        Validator.validate_64bit(2**64 - 1, "max")
    
    def test_validate_64bit_oversized(self):
        """Oversized values fail"""
        with pytest.raises(ValidationError, match="exceeds 64-bit"):
            Validator.validate_64bit(2**64, "too_big")
    
    def test_validate_64bit_negative(self):
        """Negative values fail"""
        with pytest.raises(ValidationError, match="non-negative"):
            Validator.validate_64bit(-1, "negative")
    
    def test_validate_64bit_non_int(self):
        """Non-integers fail"""
        with pytest.raises(ValidationError, match="must be an integer"):
            Validator.validate_64bit("not_an_int", "string")
    
    def test_validate_expression_valid(self):
        """Valid expression passes"""
        Validator.validate_expression(lambda: 42)
    
    def test_validate_expression_non_callable(self):
        """Non-callable fails"""
        with pytest.raises(ValidationError, match="must be callable"):
            Validator.validate_expression(42)
    
    def test_validate_expression_wrong_return_type(self):
        """Expression returning non-int fails"""
        with pytest.raises(ValidationError, match="must return int"):
            Validator.validate_expression(lambda: "string")
    
    def test_validate_expression_oversized_return(self):
        """Expression returning oversized int fails"""
        with pytest.raises(ValidationError, match="exceeds 64-bit"):
            Validator.validate_expression(lambda: 2**64)
    
    def test_validate_projection_valid(self):
        """Valid projection passes"""
        Validator.validate_projection(lambda x: x * 2)
    
    def test_validate_projection_non_callable(self):
        """Non-callable projection fails"""
        with pytest.raises(ValidationError, match="must be callable"):
            Validator.validate_projection(42)
    
    def test_validate_no_brute_force_under_threshold(self):
        """Under threshold passes"""
        Validator.validate_no_brute_force("test_op", 500)
    
    def test_validate_no_brute_force_over_threshold(self):
        """Over threshold fails"""
        with pytest.raises(ValidationError, match="brute-force"):
            Validator.validate_no_brute_force("test_op", 1001)


class TestInvocator:
    """Test Invocator - truth revelation"""
    
    @pytest.fixture
    def invocator(self):
        return Invocator()
    
    @pytest.fixture
    def gateway(self):
        return KernelGateway()
    
    def test_invoke_single(self, invocator, gateway):
        """Single invocation returns result"""
        identity = gateway.create_identity(1)
        substrate = gateway.create_substrate(identity, lambda: 42)
        lens = gateway.create_lens(1, lambda x: x)
        
        result = invocator.invoke_single(substrate, lens)
        
        assert isinstance(result, InvocationResult)
        assert result.value == 42
        assert result.substrate_id == 1
        assert result.lens_id == 1
    
    def test_invoke_batch(self, invocator, gateway):
        """Batch invocation returns multiple results"""
        identity = gateway.create_identity(1)
        substrate = gateway.create_substrate(identity, lambda: 100)
        
        lenses = [
            gateway.create_lens(i, lambda x, i=i: x + i)
            for i in range(5)
        ]
        
        results = invocator.invoke_batch(substrate, lenses)
        
        assert len(results) == 5
        assert [r.value for r in results] == [100, 101, 102, 103, 104]
    
    def test_invocation_result_is_immutable(self, invocator, gateway):
        """InvocationResult is immutable"""
        identity = gateway.create_identity(1)
        substrate = gateway.create_substrate(identity, lambda: 1)
        lens = gateway.create_lens(1, lambda x: x)
        
        result = invocator.invoke_single(substrate, lens)
        
        with pytest.raises(TypeError, match="immutable"):
            result._value = 999


class TestCoreIntegration:
    """Integration tests for Core layer"""
    
    def test_full_pipeline(self):
        """Test full pipeline: translate → validate → invoke"""
        translator = Translator()
        validator = Validator()
        gateway = KernelGateway()
        invocator = Invocator()
        
        # Translate external representation
        identity_int = translator.translate_identity("test_entity")
        expression = translator.translate_expression("constant", {"value": 42})
        projection = translator.translate_projection("identity", {})
        
        # Validate
        validator.validate_64bit(identity_int, "identity")
        validator.validate_expression(expression)
        validator.validate_projection(projection)
        
        # Create kernel objects through gateway
        identity = gateway.create_identity(identity_int)
        substrate = gateway.create_substrate(identity, expression)
        lens = gateway.create_lens(1, projection)
        
        # Invoke
        result = invocator.invoke_single(substrate, lens)
        
        assert result.value == 42


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
