"""
Substrate Pattern - Substrate Lifecycle Management

The Substrate Pattern provides utilities for managing substrate lifecycle:
- Unified substrate creation
- Substrate cloning with modifications
- Substrate merging and composition
- Substrate validation and integrity checks

CHARTER COMPLIANCE:
✅ Principle 1: Returns references, not copies (clones are NEW substrates)
✅ Principle 2: Passive until invoked
✅ Principle 3: Immutable at runtime
✅ Principle 5: Pure functions only
✅ Principle 6: All relationships visible

LAW ALIGNMENT:
- Law 1: All substrates begin as unity
- Law 6: Identity persists through lifecycle
- Law 7: Return to unity (substrates can be reduced)
"""

from __future__ import annotations
from typing import Callable, List, Optional
from kernel.substrate import Substrate, SubstrateIdentity


class SubstrateLifecycle:
    """
    Lifecycle manager for substrates.
    
    Provides utilities for creating, cloning, merging, and validating substrates
    while maintaining Charter compliance and Law alignment.
    """
    __slots__ = ()
    
    def __setattr__(self, name, value):
        raise TypeError("SubstrateLifecycle is immutable")
    
    def create(
        self,
        identity_source: str,
        expression: Callable
    ) -> Substrate:
        """
        Create substrate from identity source and expression.
        
        Args:
            identity_source: String to hash for identity
            expression: Mathematical expression
        
        Returns:
            New substrate
        
        Example:
            lifecycle = SubstrateLifecycle()
            substrate = lifecycle.create(
                "z = x + y",
                lambda x=0, y=0: x + y
            )
        """
        identity_value = hash(identity_source) & 0xFFFFFFFFFFFFFFFF
        identity = SubstrateIdentity(identity_value)
        return Substrate(identity, expression)
    
    def clone(
        self,
        substrate: Substrate,
        new_expression: Optional[Callable] = None
    ) -> Substrate:
        """
        Clone substrate with optional new expression.
        
        Creates a NEW substrate with same identity but potentially different expression.
        
        Args:
            substrate: Original substrate
            new_expression: Optional new expression (default: keep original)
        
        Returns:
            New substrate (clone)
        
        Example:
            lifecycle = SubstrateLifecycle()
            clone = lifecycle.clone(substrate, lambda: 42)
        """
        if new_expression is None:
            new_expression = substrate._expression
        
        return Substrate(substrate.identity, new_expression)
    
    def merge(
        self,
        substrates: List[Substrate],
        merge_fn: Callable[[List[int]], int]
    ) -> Substrate:
        """
        Merge multiple substrates into one.
        
        Args:
            substrates: List of substrates to merge
            merge_fn: Function to merge invocation results
        
        Returns:
            New substrate representing merged result
        
        Example:
            lifecycle = SubstrateLifecycle()
            merged = lifecycle.merge(
                [s1, s2, s3],
                lambda results: sum(results)
            )
        """
        if not substrates:
            raise ValueError("Cannot merge empty list of substrates")
        
        # Create identity from all substrate identities
        identity_value = 0
        for s in substrates:
            identity_value ^= s.identity.value
        identity_value &= 0xFFFFFFFFFFFFFFFF
        identity = SubstrateIdentity(identity_value)
        
        # Create expression that invokes all substrates and merges
        def merged_expression(**kwargs):
            results = [s.invoke(**kwargs) for s in substrates]
            return merge_fn(results) & 0xFFFFFFFFFFFFFFFF
        
        return Substrate(identity, merged_expression)
    
    def validate(self, substrate: Substrate) -> bool:
        """
        Validate substrate integrity.
        
        Checks:
        - Identity is valid (64-bit)
        - Expression is callable
        - Invocation succeeds
        
        Args:
            substrate: Substrate to validate
        
        Returns:
            True if valid, False otherwise
        
        Example:
            lifecycle = SubstrateLifecycle()
            is_valid = lifecycle.validate(substrate)
        """
        try:
            # Check identity
            if not isinstance(substrate.identity, SubstrateIdentity):
                return False
            
            # Check expression is callable
            if not callable(substrate._expression):
                return False
            
            # Try invocation
            substrate.invoke()
            return True
        except Exception:
            return False


# Convenience functions

def create_substrate(identity_source: str, expression: Callable) -> Substrate:
    """
    Create substrate from identity source and expression.
    
    Args:
        identity_source: String to hash for identity
        expression: Mathematical expression
    
    Returns:
        New substrate
    """
    lifecycle = SubstrateLifecycle()
    return lifecycle.create(identity_source, expression)


def clone_substrate(
    substrate: Substrate,
    new_expression: Optional[Callable] = None
) -> Substrate:
    """
    Clone substrate with optional new expression.
    
    Args:
        substrate: Original substrate
        new_expression: Optional new expression
    
    Returns:
        Cloned substrate
    """
    lifecycle = SubstrateLifecycle()
    return lifecycle.clone(substrate, new_expression)


def merge_substrates(
    substrates: List[Substrate],
    merge_fn: Callable[[List[int]], int]
) -> Substrate:
    """
    Merge multiple substrates.
    
    Args:
        substrates: List of substrates
        merge_fn: Merge function
    
    Returns:
        Merged substrate
    """
    lifecycle = SubstrateLifecycle()
    return lifecycle.merge(substrates, merge_fn)


def validate_substrate(substrate: Substrate) -> bool:
    """
    Validate substrate integrity.
    
    Args:
        substrate: Substrate to validate
    
    Returns:
        True if valid
    """
    lifecycle = SubstrateLifecycle()
    return lifecycle.validate(substrate)

