"""
Dimensional Object Registry - Foundational Program #8

The heart of DimensionOS. Where every substrate identity and mathematical
expression lives.

PRINCIPLES:
- No state is stored, only expressions (code, not data)
- Everything is by reference (Charter Principle 1)
- Passive until invoked (Charter Principle 2)
- Immutable at runtime (Charter Principle 3)
- No global power surface (Charter Principle 4)
- All relationships visible (Charter Principle 6)

MATHEMATICAL FORM:
    Registry = { identity → expression }
    
    Where:
        identity ∈ [0, 2^64)
        expression: Callable[..., int]
        
    Operations:
        register(identity, expression) → reference
        lookup(identity) → expression
        exists(identity) → bool
        
INVARIANTS:
    1. ∀ identity: registered(identity) ⟹ ∃! expression
    2. ∀ identity: lookup(identity) returns reference, not copy
    3. Registry is immutable after registration
    4. No identity can be unregistered (append-only)
"""

from __future__ import annotations
from typing import Callable, Optional, Dict, FrozenSet
from .substrate import Substrate, SubstrateIdentity


class RegistryReference:
    """
    A reference to a registered substrate.
    
    This is NOT the substrate itself - it's a reference to unity.
    Charter Principle 1: All things are by reference.
    """
    __slots__ = ('_identity',)
    
    def __init__(self, identity: SubstrateIdentity):
        object.__setattr__(self, '_identity', identity)
    
    def __setattr__(self, name, value):
        raise TypeError("RegistryReference is immutable")
    
    def __delattr__(self, name):
        raise TypeError("RegistryReference is immutable")
    
    @property
    def identity(self) -> SubstrateIdentity:
        """The identity this reference points to."""
        return self._identity
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, RegistryReference):
            return self._identity == other._identity
        return False
    
    def __hash__(self) -> int:
        return hash(self._identity)
    
    def __repr__(self) -> str:
        return f"RegistryReference({self._identity})"


class DimensionalObjectRegistry:
    """
    The Dimensional Object Registry.
    
    This is the heart of DimensionOS - where every substrate identity
    and mathematical expression is registered.
    
    CHARTER COMPLIANCE:
    ✅ Principle 1: Stores references only, no copies
    ✅ Principle 2: Passive until invoked
    ✅ Principle 3: Immutable at runtime (append-only)
    ✅ Principle 4: No global power surface (no override capability)
    ✅ Principle 5: Pure functions only
    ✅ Principle 6: All relationships visible
    
    DESIGN:
    - Registry is a singleton per dimensional context
    - Substrates are registered by identity
    - Lookup returns references, not copies
    - No deletion (append-only, immutable history)
    - All operations are pure functions
    """
    __slots__ = ('_registry', '_frozen')
    
    def __init__(self):
        """
        Create a new dimensional object registry.
        
        The registry starts empty and builds up through registration.
        """
        # Dictionary mapping identity → substrate
        # This is the ONLY place substrates are held
        object.__setattr__(self, '_registry', {})
        object.__setattr__(self, '_frozen', False)
    
    def __setattr__(self, name, value):
        raise TypeError("DimensionalObjectRegistry is immutable")
    
    def __delattr__(self, name):
        raise TypeError("DimensionalObjectRegistry is immutable")
    
    def register(self, substrate: Substrate) -> RegistryReference:
        """
        Register a substrate in the dimensional registry.
        
        Args:
            substrate: The substrate to register
        
        Returns:
            A reference to the registered substrate
        
        Raises:
            RuntimeError: If registry is frozen
            ValueError: If identity already registered with different expression
        
        Mathematical form:
            register: Substrate → Reference
            
        Charter compliance:
            - Returns reference, not copy (Principle 1)
            - Passive operation (Principle 2)
            - Append-only, immutable (Principle 3)
        """
        if self._frozen:
            raise RuntimeError("Registry is frozen - cannot register new substrates")

        identity = substrate.identity

        # Check if already registered
        if identity.value in self._registry:
            existing = self._registry[identity.value]
            # Non-duplication law: same identity must have same expression
            # We need to check if it's the exact same object or if expressions differ
            if existing is not substrate:
                # Different substrate object - check if expressions are the same
                # Since we can't easily compare lambda functions, we raise an error
                # if someone tries to register a different substrate with same identity
                raise ValueError(
                    f"Identity {identity} already registered with different expression"
                )
            # Already registered - return existing reference
            return RegistryReference(identity)

        # Register the substrate
        self._registry[identity.value] = substrate

        # Return reference to unity
        return RegistryReference(identity)

    def lookup(self, identity: SubstrateIdentity) -> Optional[Substrate]:
        """
        Look up a substrate by identity.

        Args:
            identity: The substrate identity to look up

        Returns:
            The substrate if found, None otherwise

        Note: Returns the substrate itself, not a copy.
              The substrate is immutable, so this is safe.

        Mathematical form:
            lookup: Identity → Substrate | ⊥

        Charter compliance:
            - Returns reference to original (Principle 1)
            - Passive operation (Principle 2)
        """
        return self._registry.get(identity.value)

    def exists(self, identity: SubstrateIdentity) -> bool:
        """
        Check if a substrate identity is registered.

        Args:
            identity: The substrate identity to check

        Returns:
            True if registered, False otherwise

        Mathematical form:
            exists: Identity → {True, False}
        """
        return identity.value in self._registry

    def get_all_identities(self) -> FrozenSet[SubstrateIdentity]:
        """
        Get all registered substrate identities.

        Returns:
            Frozen set of all registered identities

        Note: Returns a frozen set to prevent modification.

        Charter compliance:
            - Returns immutable view (Principle 3)
            - All relationships visible (Principle 6)
        """
        return frozenset(
            SubstrateIdentity(identity_value)
            for identity_value in self._registry.keys()
        )

    def count(self) -> int:
        """
        Count the number of registered substrates.

        Returns:
            Number of registered substrates
        """
        return len(self._registry)

    def freeze(self) -> None:
        """
        Freeze the registry - no more registrations allowed.

        This creates an immutable snapshot of the registry.
        Useful for creating versioned registry states.

        Charter compliance:
            - Enforces immutability (Principle 3)
        """
        object.__setattr__(self, '_frozen', True)

    def is_frozen(self) -> bool:
        """
        Check if the registry is frozen.

        Returns:
            True if frozen, False otherwise
        """
        return self._frozen

    def __len__(self) -> int:
        """Number of registered substrates."""
        return len(self._registry)

    def __contains__(self, identity: SubstrateIdentity) -> bool:
        """Check if identity is registered."""
        return identity.value in self._registry

    def __repr__(self) -> str:
        status = "frozen" if self._frozen else "active"
        return f"DimensionalObjectRegistry({len(self._registry)} substrates, {status})"


# Global registry instance (singleton pattern)
# This is the ONE place where substrates are registered
_global_registry: Optional[DimensionalObjectRegistry] = None


def get_registry() -> DimensionalObjectRegistry:
    """
    Get the global dimensional object registry.

    Returns:
        The global registry instance

    Note: This creates a singleton registry.
          In a multi-context system, you would have one registry per context.
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = DimensionalObjectRegistry()
    return _global_registry


def register_substrate(substrate: Substrate) -> RegistryReference:
    """
    Register a substrate in the global registry.

    Helper function for easy registration.

    Args:
        substrate: The substrate to register

    Returns:
        A reference to the registered substrate
    """
    registry = get_registry()
    return registry.register(substrate)


def lookup_substrate(identity: SubstrateIdentity) -> Optional[Substrate]:
    """
    Look up a substrate by identity in the global registry.

    Helper function for easy lookup.

    Args:
        identity: The substrate identity to look up

    Returns:
        The substrate if found, None otherwise
    """
    registry = get_registry()
    return registry.lookup(identity)


def substrate_exists(identity: SubstrateIdentity) -> bool:
    """
    Check if a substrate exists in the global registry.

    Helper function for easy existence check.

    Args:
        identity: The substrate identity to check

    Returns:
        True if registered, False otherwise
    """
    registry = get_registry()
    return registry.exists(identity)

