"""
SRL - Secure Resource Locator

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)

The SRL IS the location. O(1) access because the address encodes WHERE it is.

STRUCTURE:
    srl://domain/substrate/path?credentials

    domain    = which substrate (local, remote, internal, external)
    substrate = the mathematical substrate (0D-4D)
    path      = dimensional path (spiral.level.point)
    creds     = connection info, keys, auth (optional)

EXAMPLES:
    srl://local/car/0.6.engine           # Local car engine at spiral 0, level 6
    srl://db.mysql/users/1.3.admin       # MySQL user admin at level 3
    srl://api.stripe/payments/0.6.txn123 # Stripe payment
    srl://ws.server/stream/0.2.audio     # WebSocket audio stream

The SRL holds EVERYTHING needed to connect:
    - Location (instant - no search)
    - Credentials (auth, keys, tokens)
    - Protocol (how to connect)
    - Substrate (what mathematical form)

This is the ONLY way interfaces talk to Core.
Core is the ONLY thing that talks to Kernel.
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import IntEnum
import re


# =============================================================================
# THE 7 LEVELS - That's it. Simple.
# =============================================================================

class Level(IntEnum):
    """
    The 7 levels. Fibonacci structure.
    
    DIMENSIONAL HIERARCHY:
    ┌─────────────────────────────────────────────────────────────────────┐
    │  VOID    │ Pure potential - not yet evaluated                      │
    │  0D      │ Evaluated point - IS both point AND dimensional object  │
    │  1D      │ Line - division of points                               │
    │  2D      │ Width - multiplication of divided points → FIRST       │
    │          │ SUBSTRATE (z=xy) → plane/table/grid/matrix              │
    │  3D      │ Volume of 2D objects - depth, height, deltas, trends    │
    │  4D      │ 3D as single point → completion → spiral twist          │
    └─────────────────────────────────────────────────────────────────────┘
    
    Level 6 (WHOLE) = 3D→4D transition
    WHOLE (Fib 8) + VOLUME (Fib 5) = 13 = POINT of next spiral
    """
    VOID   = 0  # Pure potential - not yet evaluated
    POINT  = 1  # 0D: Evaluated point - IS both point AND dimension
    LINE   = 2  # 1D: Division of points
    WIDTH  = 3  # 2D: Multiplication → plane/grid (FIRST SUBSTRATE z=xy)
    PLANE  = 4  # 2D complete: Surface/table/matrix
    VOLUME = 5  # 3D: Depth, height, deltas, trends
    WHOLE  = 6  # 4D: Complete object as point → spiral twist


# =============================================================================
# SRL - The Universal Connector
# =============================================================================

@dataclass
class SRL:
    """
    Secure Resource Locator - Universal connector for everything.
    
    The address IS the location. O(1) access.
    Holds location + credentials + connection info.
    
    Usage:
        # Create SRL
        loc = SRL("car", 0, Level.WHOLE, "engine")
        loc = SRL.parse("srl://local/car/0.6.engine")
        
        # Access instantly (O(1))
        value = loc.get()
        loc.set(value)
        
        # With credentials
        loc = SRL("db", 0, Level.PLANE, "users", 
                  credentials={"host": "localhost", "key": "xxx"})
    """
    
    # Location (this IS where it is)
    domain: str = "local"           # Which substrate domain
    spiral: int = 0                 # Which spiral (0-N)
    level: Level = Level.WHOLE      # Which level (0-6)
    path: str = ""                  # Path to point
    
    # Connection info (everything needed to connect)
    credentials: Dict[str, Any] = field(default_factory=dict)
    protocol: str = "internal"      # internal, http, ws, tcp, etc.
    
    def __post_init__(self):
        if isinstance(self.level, int):
            self.level = Level(self.level)
    
    @property
    def coordinate(self) -> Tuple[int, int]:
        """(spiral, level) - the dimensional coordinate."""
        return (self.spiral, self.level.value)
    
    @property 
    def address(self) -> str:
        """Full SRL address string."""
        base = f"srl://{self.domain}/{self.spiral}.{self.level.value}"
        if self.path:
            base += f".{self.path}"
        return base
    
    def __str__(self) -> str:
        return self.address
    
    def __hash__(self) -> int:
        return hash(self.address)
    
    def __eq__(self, other) -> bool:
        if isinstance(other, SRL):
            return self.address == other.address
        if isinstance(other, str):
            return self.address == other
        return False
    
    # =========================================================================
    # INSTANT TRAVERSAL - O(1) jumps
    # =========================================================================
    
    def at(self, level: int) -> 'SRL':
        """Jump to level. O(1)."""
        return SRL(self.domain, self.spiral, Level(level), self.path, 
                   self.credentials, self.protocol)
    
    def up(self) -> 'SRL':
        """Go up one level. At WHOLE, spiral up."""
        if self.level >= Level.WHOLE:
            return SRL(self.domain, self.spiral + 1, Level.VOID, "",
                       self.credentials, self.protocol)
        return self.at(self.level + 1)
    
    def down(self) -> 'SRL':
        """Go down one level. At VOID, spiral down."""
        if self.level <= Level.VOID:
            return SRL(self.domain, self.spiral - 1, Level.WHOLE, "",
                       self.credentials, self.protocol)
        return self.at(self.level - 1)
    
    def child(self, name: str) -> 'SRL':
        """Get child point. O(1)."""
        new_path = f"{self.path}.{name}" if self.path else name
        return SRL(self.domain, self.spiral, self.level, new_path,
                   self.credentials, self.protocol)
    
    def point(self, name: str) -> 'SRL':
        """Alias for child. Access a point in this dimension."""
        return self.child(name)
    
    # =========================================================================
    # PARSING - Create SRL from string
    # =========================================================================
    
    @classmethod
    def parse(cls, srl_string: str) -> 'SRL':
        """
        Parse SRL string to SRL object.
        
        Formats:
            srl://domain/spiral.level.path
            srl://domain/spiral.level
            domain/spiral.level.path
            spiral.level.path
        """
        # Remove srl:// prefix if present
        s = srl_string
        if s.startswith("srl://"):
            s = s[6:]
        
        # Extract domain if present
        domain = "local"
        if "/" in s:
            parts = s.split("/", 1)
            domain = parts[0]
            s = parts[1] if len(parts) > 1 else ""
        
        # Parse spiral.level.path
        parts = s.split(".")
        spiral = int(parts[0]) if parts and parts[0].isdigit() else 0
        level = Level(int(parts[1])) if len(parts) > 1 and parts[1].isdigit() else Level.WHOLE
        path = ".".join(parts[2:]) if len(parts) > 2 else ""
        
        return cls(domain=domain, spiral=spiral, level=level, path=path)
    
    # =========================================================================
    # CONNECTION HELPERS
    # =========================================================================
    
    def with_credentials(self, **creds) -> 'SRL':
        """Add credentials to this SRL."""
        new_creds = {**self.credentials, **creds}
        return SRL(self.domain, self.spiral, self.level, self.path,
                   new_creds, self.protocol)
    
    def with_protocol(self, protocol: str) -> 'SRL':
        """Set protocol for this SRL."""
        return SRL(self.domain, self.spiral, self.level, self.path,
                   self.credentials, protocol)
    
    @property
    def is_local(self) -> bool:
        return self.domain == "local"
    
    @property
    def is_external(self) -> bool:
        return not self.is_local


# =============================================================================
# CONVENIENCE FUNCTION - srl()
# =============================================================================

def srl(address: str = "", **kwargs) -> SRL:
    """
    Create an SRL. The universal accessor.
    
    Usage:
        loc = srl("local/0.6.car.engine")
        loc = srl("db.mysql/0.3.users", host="localhost", password="xxx")
        loc = srl(domain="api", spiral=0, level=6, path="payments")
    """
    if address:
        result = SRL.parse(address)
        if kwargs:
            result = result.with_credentials(**kwargs)
        return result
    return SRL(**kwargs)


# =============================================================================
# CORE - The ONLY thing that talks to Kernel
# =============================================================================

class Core:
    """
    Core handles ALL kernel communication.
    
    Interfaces talk to Core via SRL.
    Core talks to Kernel.
    That's it.
    
    O(1) access because SRL IS the location.
    7 levels. Instant traversal.
    """
    
    _store: Dict[str, Any] = {}  # Simple storage (kernel proxy)
    
    @classmethod
    def get(cls, address: str) -> Any:
        """
        Get value at SRL address. O(1).
        
        Usage:
            value = Core.get("srl://local/car/0.6.engine")
        """
        loc = SRL.parse(address) if isinstance(address, str) else address
        return cls._store.get(loc.address)
    
    @classmethod
    def set(cls, address: str, value: Any) -> None:
        """
        Set value at SRL address. O(1).
        
        Usage:
            Core.set("srl://local/car/0.6.engine", engine_obj)
        """
        loc = SRL.parse(address) if isinstance(address, str) else address
        cls._store[loc.address] = value
    
    @classmethod
    def exists(cls, address: str) -> bool:
        """Check if address has a value."""
        loc = SRL.parse(address) if isinstance(address, str) else address
        return loc.address in cls._store
    
    @classmethod
    def delete(cls, address: str) -> bool:
        """Delete value at address. Returns True if existed."""
        loc = SRL.parse(address) if isinstance(address, str) else address
        if loc.address in cls._store:
            del cls._store[loc.address]
            return True
        return False
    
    @classmethod
    def at(cls, spiral: int, level: int, path: str = "") -> Any:
        """
        Direct coordinate access. O(1).
        
        Usage:
            value = Core.at(0, 6, "car.engine")
        """
        loc = SRL("local", spiral, Level(level), path)
        return cls._store.get(loc.address)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ['SRL', 'srl', 'Level', 'Core']
