"""
Translator - Converts Python to Kernel math.

Human language, machine code, AI instructions - all must be
translated into substrate-compliant mathematical expressions.

The Translator is the compiler from intent to math.
"""

from __future__ import annotations
from typing import Callable, Dict, Any, Optional, Union
from .gateway import Gateway
from .validator import Validator, ValidationError

__all__ = ['Translator', 'TranslationError']


class TranslationError(Exception):
    """Raised when translation to substrate math fails."""
    pass


class Translator:
    """
    Translates Python constructs into Kernel primitives.
    
    Input sources:
    - Python dicts, objects, values
    - Strings (hashed to identity)
    - Bytes (hashed to identity)
    - Callables (wrapped as expressions)
    
    Output: Substrate-compliant mathematical expressions
    """
    
    def __init__(self):
        self._gateway = Gateway()
    
    # ═══════════════════════════════════════════════════════════════
    # IDENTITY TRANSLATION
    # ═══════════════════════════════════════════════════════════════
    
    def to_identity(self, source: Union[int, str, bytes, Any]) -> int:
        """
        Translate various Python types to 64-bit identity.
        
        Args:
            source: Any Python value
        
        Returns:
            64-bit identity integer
        """
        if isinstance(source, int):
            return source & 0xFFFFFFFFFFFFFFFF
        
        if isinstance(source, str):
            return self._hash_to_64bit(source.encode('utf-8'))
        
        if isinstance(source, bytes):
            return self._hash_to_64bit(source)
        
        # For other objects, hash their representation
        return self._hash_to_64bit(repr(source).encode('utf-8'))
    
    def _hash_to_64bit(self, data: bytes) -> int:
        """
        Deterministic FNV-1a hash to 64-bit identity.
        
        This is the canonical hash function for translating
        arbitrary bytes to substrate identity.
        """
        FNV_PRIME = 0x100000001b3
        FNV_OFFSET = 0xcbf29ce484222325
        
        h = FNV_OFFSET
        for byte in data:
            h ^= byte
            h = (h * FNV_PRIME) & 0xFFFFFFFFFFFFFFFF
        return h
    
    # ═══════════════════════════════════════════════════════════════
    # EXPRESSION TRANSLATION
    # ═══════════════════════════════════════════════════════════════
    
    def to_expression(
        self,
        source: Union[int, Callable, Dict, str]
    ) -> Callable[[], int]:
        """
        Translate Python value to kernel expression.
        
        Args:
            source: Python value to translate
                - int: Constant expression
                - callable: Wrapped with validation
                - dict: Expression specification
                - str: Hashed to constant
        
        Returns:
            Callable that returns 64-bit int
        """
        if isinstance(source, int):
            # Constant expression
            value = source & 0xFFFFFFFFFFFFFFFF
            return lambda v=value: v
        
        if callable(source):
            # Wrap callable with 64-bit enforcement
            return lambda s=source: s() & 0xFFFFFFFFFFFFFFFF
        
        if isinstance(source, str):
            # Hash to constant
            value = self._hash_to_64bit(source.encode('utf-8'))
            return lambda v=value: v
        
        if isinstance(source, dict):
            return self._translate_dict_expression(source)
        
        # Fallback: hash representation
        value = self.to_identity(source)
        return lambda v=value: v
    
    def _translate_dict_expression(self, spec: Dict[str, Any]) -> Callable[[], int]:
        """
        Translate dictionary specification to expression.
        
        Supported specs:
            {"type": "constant", "value": 42}
            {"type": "hash", "data": "hello"}
            {"type": "composite", "op": "xor", "operands": [...]}
            {"type": "derived", "base": x, "offset": n}
        """
        expr_type = spec.get("type", "constant")
        
        if expr_type == "constant":
            value = spec.get("value", 0) & 0xFFFFFFFFFFFFFFFF
            return lambda v=value: v
        
        if expr_type == "hash":
            data = spec.get("data", "")
            if isinstance(data, str):
                data = data.encode('utf-8')
            value = self._hash_to_64bit(data)
            return lambda v=value: v
        
        if expr_type == "derived":
            base = spec.get("base", 0) & 0xFFFFFFFFFFFFFFFF
            offset = spec.get("offset", 0) & 0xFFFFFFFFFFFFFFFF
            return lambda b=base, o=offset: (b + o) & 0xFFFFFFFFFFFFFFFF
        
        if expr_type == "composite":
            op = spec.get("op", "xor")
            operands = spec.get("operands", [0, 0])
            
            # Recursively compile operands
            compiled_operands = []
            for operand in operands:
                if isinstance(operand, dict):
                    compiled_operands.append(self._translate_dict_expression(operand))
                elif isinstance(operand, int):
                    compiled_operands.append(lambda v=operand: v)
                else:
                    compiled_operands.append(self.to_expression(operand))
            
            if op == "xor":
                return lambda cops=compiled_operands: self._reduce_xor_compiled(cops)
            elif op == "and":
                return lambda cops=compiled_operands: self._reduce_and_compiled(cops)
            elif op == "or":
                return lambda cops=compiled_operands: self._reduce_or_compiled(cops)
        
        raise TranslationError(f"Unknown expression type: {expr_type}")
    
    def _reduce_xor(self, operands: list) -> int:
        result = 0
        for op in operands:
            result ^= (op & 0xFFFFFFFFFFFFFFFF)
        return result
    
    def _reduce_xor_compiled(self, operands: list) -> int:
        result = 0
        for op_fn in operands:
            result ^= (op_fn() & 0xFFFFFFFFFFFFFFFF)
        return result
    
    def _reduce_and(self, operands: list) -> int:
        result = 0xFFFFFFFFFFFFFFFF
        for op in operands:
            result &= (op & 0xFFFFFFFFFFFFFFFF)
        return result
    
    def _reduce_and_compiled(self, operands: list) -> int:
        result = 0xFFFFFFFFFFFFFFFF
        for op_fn in operands:
            result &= (op_fn() & 0xFFFFFFFFFFFFFFFF)
        return result
    
    def _reduce_or(self, operands: list) -> int:
        result = 0
        for op in operands:
            result |= (op & 0xFFFFFFFFFFFFFFFF)
        return result
    
    def _reduce_or_compiled(self, operands: list) -> int:
        result = 0
        for op_fn in operands:
            result |= (op_fn() & 0xFFFFFFFFFFFFFFFF)
        return result
    
    # ═══════════════════════════════════════════════════════════════
    # SUBSTRATE TRANSLATION
    # ═══════════════════════════════════════════════════════════════
    
    def to_substrate(
        self,
        identity_source: Any,
        expression_source: Any = None
    ):
        """
        Translate Python values to Substrate.
        
        Args:
            identity_source: Value to translate to identity
            expression_source: Value to translate to expression
                              (defaults to identity if not provided)
        
        Returns:
            Substrate from gateway
        """
        identity_int = self.to_identity(identity_source)
        identity = self._gateway.create_identity(identity_int)
        
        if expression_source is None:
            expression = lambda i=identity_int: i
        else:
            expression = self.to_expression(expression_source)
        
        return self._gateway.create_substrate(identity, expression)
    
    # ═══════════════════════════════════════════════════════════════
    # LENS TRANSLATION
    # ═══════════════════════════════════════════════════════════════
    
    def to_lens(
        self,
        lens_id: Any,
        projection: Union[Callable[[int], int], str]
    ):
        """
        Translate Python values to Lens.
        
        Args:
            lens_id: Value to translate to lens identity
            projection: Projection function or named projection
        
        Returns:
            Lens from gateway
        """
        lens_id_int = self.to_identity(lens_id)
        
        if isinstance(projection, str):
            projection = self._get_named_projection(projection)
        
        return self._gateway.create_lens(lens_id_int, projection)
    
    def _get_named_projection(self, name: str) -> Callable[[int], int]:
        """Get built-in named projection."""
        projections = {
            "identity": lambda x: x,
            "low_byte": lambda x: x & 0xFF,
            "high_byte": lambda x: (x >> 56) & 0xFF,
            "low_word": lambda x: x & 0xFFFF,
            "high_word": lambda x: (x >> 48) & 0xFFFF,
            "low_dword": lambda x: x & 0xFFFFFFFF,
            "high_dword": lambda x: (x >> 32) & 0xFFFFFFFF,
            "invert": lambda x: ~x & 0xFFFFFFFFFFFFFFFF,
            "double": lambda x: (x * 2) & 0xFFFFFFFFFFFFFFFF,
            "half": lambda x: x >> 1,
        }
        
        if name not in projections:
            raise TranslationError(f"Unknown projection: {name}")
        
        return projections[name]
    
    # ═══════════════════════════════════════════════════════════════
    # DELTA TRANSLATION
    # ═══════════════════════════════════════════════════════════════
    
    def to_delta(self, source: Any):
        """
        Translate Python value to Delta.
        
        Args:
            source: Value to translate to delta z1
        
        Returns:
            Delta from gateway
        """
        z1 = self.to_identity(source)
        return self._gateway.create_delta(z1)
