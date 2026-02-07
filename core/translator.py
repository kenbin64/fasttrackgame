"""
Translator - Converts external representations to Kernel math.

Human language, machine code, AI instructions - all must be
translated into substrate-compliant mathematical expressions.

The Translator is the compiler from intent to math.
"""

from __future__ import annotations
from typing import Callable, Dict, Optional, Tuple
from .gateway import KernelGateway


class TranslationError(Exception):
    """Raised when translation to substrate math fails"""
    pass


class Translator:
    """
    Translates external representations into Kernel primitives.
    
    Input sources:
    - Human: Natural language, declarative syntax
    - Machine: Binary protocols, structured data
    - AI: Instruction sets, embeddings
    
    Output: Substrate-compliant mathematical expressions
    """
    
    def __init__(self):
        self._gateway = KernelGateway()
        self._expression_cache: Dict[int, Callable[[], int]] = {}
    
    # ═══════════════════════════════════════════════════════════════
    # IDENTITY TRANSLATION
    # ═══════════════════════════════════════════════════════════════
    
    def translate_identity(self, source: int | str | bytes) -> int:
        """
        Translate various identity representations to 64-bit int.
        
        No data is stored - this is pure transformation.
        """
        if isinstance(source, int):
            if 0 <= source < 2**64:
                return source
            raise TranslationError(f"Integer {source} exceeds 64 bits")
        
        if isinstance(source, str):
            # Hash string to 64-bit identity
            return self._hash_to_64bit(source.encode('utf-8'))
        
        if isinstance(source, bytes):
            return self._hash_to_64bit(source)
        
        raise TranslationError(f"Cannot translate {type(source)} to identity")
    
    def _hash_to_64bit(self, data: bytes) -> int:
        """Deterministic hash to 64-bit identity"""
        # Using FNV-1a for speed and distribution
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
    
    def translate_expression(
        self,
        expr_type: str,
        parameters: Dict
    ) -> Callable[[], int]:
        """
        Translate declarative expression to Kernel-compatible callable.
        
        No hard-coded values - expressions are mathematical.
        """
        if expr_type == "constant":
            value = parameters.get("value", 0)
            return lambda v=value: v
        
        if expr_type == "timestamp":
            import time
            return lambda: int(time.time() * 1000)
        
        if expr_type == "derived":
            base = parameters.get("base", 0)
            offset = parameters.get("offset", 0)
            return lambda b=base, o=offset: b + o
        
        if expr_type == "composite":
            # For composed expressions
            sub_exprs = parameters.get("expressions", [])
            operator = parameters.get("operator", "xor")
            return self._compose_expressions(sub_exprs, operator)
        
        raise TranslationError(f"Unknown expression type: {expr_type}")
    
    def _compose_expressions(
        self,
        expressions: list,
        operator: str
    ) -> Callable[[], int]:
        """Compose multiple expressions into one"""
        if operator == "xor":
            def composed():
                result = 0
                for expr in expressions:
                    result ^= expr()
                return result
            return composed
        
        if operator == "add":
            def composed():
                result = 0
                for expr in expressions:
                    result = (result + expr()) & 0xFFFFFFFFFFFFFFFF
                return result
            return composed
        
        raise TranslationError(f"Unknown operator: {operator}")
    
    # ═══════════════════════════════════════════════════════════════
    # LENS TRANSLATION
    # ═══════════════════════════════════════════════════════════════
    
    def translate_projection(
        self,
        proj_type: str,
        parameters: Dict
    ) -> Callable[[int], int]:
        """
        Translate lens projection specification to callable.
        """
        if proj_type == "identity":
            return lambda x: x
        
        if proj_type == "mask":
            mask = parameters.get("mask", 0xFFFFFFFFFFFFFFFF)
            shift = parameters.get("shift", 0)
            return lambda x, m=mask, s=shift: (x >> s) & m
        
        if proj_type == "extract_bits":
            start = parameters.get("start", 0)
            length = parameters.get("length", 64)
            mask = (1 << length) - 1
            return lambda x, s=start, m=mask: (x >> s) & m
        
        raise TranslationError(f"Unknown projection type: {proj_type}")
