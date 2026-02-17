"""
ButterflyFX Shortcuts - Quick One-Liner Helpers

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

Attribution required: Kenneth Bingham - https://butterflyfx.us

---

Shortcuts for common ButterflyFX operations.
Import this module for quick access to frequently used functionality.

Usage:
    from helix.shortcuts import *
    
    # Quick token creation
    t = tok("user", 3, {"name": "Alice"})
    
    # Quick state creation
    s = st(0, 4)  # spiral 0, level 4
    
    # Quick kernel operations
    k = kern()
    go(k, 3)  # invoke level 3
"""

from __future__ import annotations
from typing import Any, Dict, List, Set, Optional, Union, Callable
import uuid

from .kernel import HelixState, HelixKernel, LEVEL_NAMES, LEVEL_ICONS
from .substrate import Token, ManifoldSubstrate, PayloadSource
from .constants import (
    PHI, FIBONACCI, Level,
    ALL_LEVELS, LOWER_LEVELS, UPPER_LEVELS,
    level_position, fib
)


# =============================================================================
# QUICK TOKEN SHORTCUTS
# =============================================================================

def tok(
    id: str = None,
    level: int = 3,
    data: Any = None,
    spiral: int = 0
) -> Token:
    """
    Quick token creation.
    
    Usage:
        t = tok("user_1", 3, {"name": "Alice"})
        t = tok(data={"x": 1})  # auto-id
    """
    token_id = id or f"t_{uuid.uuid4().hex[:6]}"
    return Token(
        id=token_id,
        location=(spiral, level, 0),
        signature={level},
        payload=lambda d=data: d,
        spiral_affinity=spiral
    )


def toks(items: List[Any], level: int = 3, prefix: str = "t") -> List[Token]:
    """
    Quick multiple token creation.
    
    Usage:
        tokens = toks([1, 2, 3])
        tokens = toks([{"a": 1}, {"a": 2}], level=4)
    """
    return [
        tok(f"{prefix}_{i}", level, item)
        for i, item in enumerate(items)
    ]


def empty_tok(id: str = None, level: int = 3) -> Token:
    """Create an empty token (no payload)"""
    return tok(id, level, None)


# =============================================================================
# QUICK STATE SHORTCUTS
# =============================================================================

def st(spiral: int = 0, level: int = 0) -> HelixState:
    """
    Quick state creation.
    
    Usage:
        s = st(0, 3)  # spiral 0, level 3
        s = st(level=4)  # spiral 0, level 4
    """
    return HelixState(spiral, level)


def origin() -> HelixState:
    """Origin state (0, 0)"""
    return HelixState(0, 0)


def apex() -> HelixState:
    """Apex of spiral 0 (0, 6)"""
    return HelixState(0, 6)


# =============================================================================
# QUICK KERNEL SHORTCUTS
# =============================================================================

def kern(manifold: ManifoldSubstrate = None) -> HelixKernel:
    """Quick kernel creation"""
    return HelixKernel(substrate=manifold)


def go(kernel: HelixKernel, level: int) -> Set[Token]:
    """Quick invoke"""
    return kernel.invoke(level)


def up(kernel: HelixKernel) -> Set[Token]:
    """Quick spiral up"""
    return kernel.spiral_up()


def down(kernel: HelixKernel) -> Set[Token]:
    """Quick spiral down"""
    return kernel.spiral_down()


def reset(kernel: HelixKernel) -> Set[Token]:
    """Quick collapse"""
    return kernel.collapse()


def where(kernel: HelixKernel) -> tuple:
    """Get current (spiral, level)"""
    return (kernel.spiral, kernel.level)


def at(kernel: HelixKernel) -> str:
    """Get human-readable state"""
    return f"spiral {kernel.spiral}, {LEVEL_NAMES[kernel.level]} ({kernel.level})"


# =============================================================================
# QUICK MANIFOLD SHORTCUTS
# =============================================================================

def mani(*tokens) -> ManifoldSubstrate:
    """
    Quick manifold creation with tokens.
    
    Usage:
        m = mani(tok1, tok2, tok3)
    """
    manifold = ManifoldSubstrate()
    for t in tokens:
        manifold.place(t)
    return manifold


def mani_from(items: List[Any], level: int = 3) -> ManifoldSubstrate:
    """
    Quick manifold from list of items.
    
    Usage:
        m = mani_from([1, 2, 3])
        m = mani_from([{"name": "A"}, {"name": "B"}])
    """
    manifold = ManifoldSubstrate()
    for i, item in enumerate(items):
        t = tok(f"item_{i}", level, item)
        manifold.place(t)
    return manifold


# =============================================================================
# QUICK LEVEL SHORTCUTS
# =============================================================================

def lvl(n: int) -> str:
    """Get level name"""
    return LEVEL_NAMES.get(n, "Unknown")


def ico(n: int) -> str:
    """Get level icon"""
    return LEVEL_ICONS.get(n, "?")


def potential() -> int:
    return 0

def point() -> int:
    return 1

def length() -> int:
    return 2

def width() -> int:
    return 3

def plane() -> int:
    return 4

def volume() -> int:
    return 5

def whole() -> int:
    return 6


# Level aliases
L0 = 0
L1 = 1
L2 = 2
L3 = 3
L4 = 4
L5 = 5
L6 = 6


# =============================================================================
# QUICK OPERATIONS
# =============================================================================

def mat(token: Token) -> Any:
    """Quick materialize"""
    return token.materialize()


def mats(tokens: List[Token]) -> List[Any]:
    """Quick materialize list"""
    return [t.materialize() for t in tokens]


def ids(tokens: Union[List[Token], Set[Token]]) -> List[str]:
    """Get token IDs"""
    return [t.id for t in tokens]


def payloads(tokens: Union[List[Token], Set[Token]]) -> List[Any]:
    """Get materialized payloads"""
    return [t.materialize() for t in tokens]


def filter_level(tokens: Union[List[Token], Set[Token]], level: int) -> List[Token]:
    """Filter tokens by level"""
    return [t for t in tokens if level in t.signature]


def filter_spiral(tokens: Union[List[Token], Set[Token]], spiral: int) -> List[Token]:
    """Filter tokens by spiral affinity"""
    return [t for t in tokens if t.spiral_affinity == spiral]


# =============================================================================
# QUICK MATH
# =============================================================================

phi = PHI  # Golden ratio shortcut


def fib_n(n: int) -> int:
    """Get nth Fibonacci number"""
    return fib(n)


def pos(level: int, spiral: int = 0) -> tuple:
    """Get 3D position for level/spiral"""
    return level_position(level, spiral)


# =============================================================================
# QUICK PRINTING
# =============================================================================

def show_state(kernel: HelixKernel):
    """Print kernel state"""
    s = kernel.state
    print(f"{LEVEL_ICONS[s.level]} Spiral {s.spiral}, Level {s.level} ({LEVEL_NAMES[s.level]})")


def show_token(token: Token):
    """Print token details"""
    print(f"Token {token.id}:")
    print(f"  Location: {token.location}")
    print(f"  Levels: {sorted(token.signature)}")
    print(f"  Payload: {token.materialize()}")


def show_tokens(tokens: Union[List[Token], Set[Token]], limit: int = 10):
    """Print multiple tokens"""
    for i, t in enumerate(list(tokens)[:limit]):
        print(f"  {i}: {t.id} @ {t.location} = {t.materialize()}")
    if len(list(tokens)) > limit:
        print(f"  ... and {len(list(tokens)) - limit} more")


def show_levels():
    """Print all levels"""
    for i in range(7):
        print(f"  {LEVEL_ICONS[i]} {i}: {LEVEL_NAMES[i]}")


# =============================================================================
# QUICK CONTEXT MANAGER
# =============================================================================

class helix:
    """
    Quick context manager for helix operations.
    
    Usage:
        with helix(3) as (k, tokens):
            print(tokens)
    """
    
    def __init__(self, level: int = 0, spiral: int = 0, manifold: ManifoldSubstrate = None):
        self.level = level
        self.spiral = spiral
        self.manifold = manifold
        self.kernel = None
    
    def __enter__(self):
        self.kernel = HelixKernel(substrate=self.manifold)
        tokens = self.kernel.invoke(self.level) if self.level > 0 else set()
        return self.kernel, tokens
    
    def __exit__(self, *args):
        pass


# =============================================================================
# QUICK BUILDERS (aliases)
# =============================================================================

def token_builder():
    """Start a token builder"""
    from .builders import TokenBuilder
    return TokenBuilder()


def state_builder():
    """Start a state builder"""
    from .builders import StateBuilder
    return StateBuilder()


def manifold_builder():
    """Start a manifold builder"""
    from .builders import ManifoldBuilder
    return ManifoldBuilder()


# Builder aliases
T = token_builder
S = state_builder
M = manifold_builder


# =============================================================================
# ALL EXPORTS
# =============================================================================

__all__ = [
    # Token shortcuts
    'tok', 'toks', 'empty_tok',
    
    # State shortcuts
    'st', 'origin', 'apex',
    
    # Kernel shortcuts
    'kern', 'go', 'up', 'down', 'reset', 'where', 'at',
    
    # Manifold shortcuts
    'mani', 'mani_from',
    
    # Level shortcuts
    'lvl', 'ico',
    'potential', 'point', 'length', 'width', 'plane', 'volume', 'whole',
    'L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6',
    
    # Operations
    'mat', 'mats', 'ids', 'payloads',
    'filter_level', 'filter_spiral',
    
    # Math
    'phi', 'fib_n', 'pos',
    
    # Printing
    'show_state', 'show_token', 'show_tokens', 'show_levels',
    
    # Context
    'helix',
    
    # Builders
    'token_builder', 'state_builder', 'manifold_builder',
    'T', 'S', 'M',
]
