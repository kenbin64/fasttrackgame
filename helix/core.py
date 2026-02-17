"""
Core - The only layer that talks to the Kernel.

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)

ARCHITECTURE (Simple):
    ┌─────────────────────────────────┐
    │  Developer Code (simple syntax) │
    └─────────────┬───────────────────┘
                  │ uses
    ┌─────────────▼───────────────────┐
    │  Interface (Object)             │
    │  - Talks to Core via SRL        │
    └─────────────┬───────────────────┘
                  │ SRL
    ┌─────────────▼───────────────────┐
    │  CORE                           │
    │  - ONLY thing that talks to     │
    │    the Kernel                   │
    │  - Handles all abstraction      │
    └─────────────┬───────────────────┘
                  │ direct
    ┌─────────────▼───────────────────┐
    │  KERNEL                         │
    │  - Mathematical substrate       │
    │  - 7 levels, Fibonacci          │
    └─────────────────────────────────┘

Developers never see this. They just use simple syntax:
    car = ingest("Car")
    car.engine.horsepower = 300
    
Behind the scenes:
    Interface → Core.set(srl("local/0.6.car.engine.horsepower"), 300)
    Core → Kernel.write(coordinate, value)
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Callable, List
from dataclasses import dataclass, field
import threading
import time

from .srl import SRL, Level, srl


# =============================================================================
# CORE - Singleton that manages kernel communication
# =============================================================================

class Core:
    """
    The Core. Only thing that talks to Kernel.
    
    All interfaces communicate through Core via SRL.
    Core handles:
        - Kernel read/write
        - Substrate management
        - Spiral position tracking
        - Object registry
    
    Developers don't use this directly.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance
    
    def _init(self):
        """Initialize core state."""
        # Storage by SRL address (O(1) lookup)
        self._data: Dict[str, Any] = {}
        
        # Object registry
        self._objects: Dict[str, 'Interface'] = {}
        
        # Spiral tracking
        self._spiral = 0
        self._position = 0.0
        
        # Substrate registry
        self._substrates: Dict[str, Any] = {}
    
    # =========================================================================
    # CORE OPERATIONS - What interfaces call via SRL
    # =========================================================================
    
    def get(self, loc: SRL) -> Any:
        """
        Get value at SRL location. O(1).
        
        The SRL IS the location - no search needed.
        """
        return self._data.get(loc.address)
    
    def set(self, loc: SRL, value: Any) -> None:
        """
        Set value at SRL location. O(1).
        """
        self._data[loc.address] = value
    
    def exists(self, loc: SRL) -> bool:
        """Check if location has value. O(1)."""
        return loc.address in self._data
    
    def delete(self, loc: SRL) -> bool:
        """Delete value at location. O(1)."""
        if loc.address in self._data:
            del self._data[loc.address]
            return True
        return False
    
    # =========================================================================
    # OBJECT MANAGEMENT
    # =========================================================================
    
    def register(self, obj: 'Interface') -> str:
        """Register an interface object."""
        self._objects[obj._id] = obj
        return obj._id
    
    def unregister(self, obj_id: str) -> bool:
        """Unregister an interface object."""
        if obj_id in self._objects:
            del self._objects[obj_id]
            return True
        return False
    
    def get_object(self, obj_id: str) -> Optional['Interface']:
        """Get interface by ID."""
        return self._objects.get(obj_id)
    
    # =========================================================================
    # SPIRAL MANAGEMENT
    # =========================================================================
    
    def advance(self, delta: float = 0.01) -> SRL:
        """
        Advance spiral position.
        Returns new SRL at current position.
        """
        self._position += delta
        level = min(6, int(self._position * 7))
        
        # Spiral transition at x=1
        if self._position >= 1.0:
            self._spiral += 1
            self._position = 0.0
            level = 0
        
        return srl(f"local/{self._spiral}.{level}")
    
    @property
    def current_srl(self) -> SRL:
        """Current spiral position as SRL."""
        level = min(6, int(self._position * 7))
        return srl(f"local/{self._spiral}.{level}")
    
    # =========================================================================
    # CONVENIENCE
    # =========================================================================
    
    def __getitem__(self, address: str) -> Any:
        """core["srl://local/0.6.car"] syntax."""
        return self.get(srl(address))
    
    def __setitem__(self, address: str, value: Any) -> None:
        """core["srl://local/0.6.car"] = value syntax."""
        self.set(srl(address), value)
    
    def __contains__(self, address: str) -> bool:
        """'address' in core syntax."""
        return self.exists(srl(address))


# Global core instance
CORE = Core()


# =============================================================================
# INTERFACE - Simple object that talks to Core via SRL
# =============================================================================

class Interface:
    """
    The object. Talks to Core via SRL.
    
    Developer syntax is SIMPLE:
        car = ingest("Car")
        car.engine.hp = 300
        print(car.engine.hp)  # 300
    
    Behind the scenes, Interface uses SRL to talk to Core.
    Core talks to Kernel. Developer never sees this.
    """
    
    def __init__(self, type_name: str = "Object", parent: 'Interface' = None):
        # Identity
        self._id = f"{type_name}_{id(self)}"
        self._type = type_name
        
        # SRL location (where this object lives)
        self._srl = CORE.advance()
        if parent:
            self._srl = parent._srl.child(type_name)
        
        # Parent reference (for path building)
        self._parent = parent
        
        # Children cache (for attribute access)
        self._children: Dict[str, Interface] = {}
        
        # Register with core
        CORE.register(self)
    
    @property 
    def srl(self) -> SRL:
        """This object's SRL location."""
        return self._srl
    
    # =========================================================================
    # SIMPLE ATTRIBUTE ACCESS - The magic
    # =========================================================================
    
    def __getattr__(self, name: str) -> Any:
        """
        car.engine → get or create child Interface
        car.engine.hp → if hp was set, return value
        car.floors[0] → _0 → numeric index access
        """
        # Allow numeric indices (_0, _1, etc.) but reject other internal attrs
        if name.startswith('_') and not (len(name) > 1 and name[1:].isdigit()):
            raise AttributeError(name)
        
        # Check if value was set at this path
        child_srl = self._srl.child(name)
        value = CORE.get(child_srl)
        if value is not None:
            return value
        
        # Return or create child Interface
        if name not in self._children:
            self._children[name] = Interface(name, parent=self)
        return self._children[name]
    
    def __setattr__(self, name: str, value: Any) -> None:
        """
        car.vin = "ABC123" → store in Core via SRL
        car.floors[0].number = 1 → _0 → numeric index
        """
        # Internal attrs (except numeric indices like _0)
        if name.startswith('_') and not (len(name) > 1 and name[1:].isdigit()):
            object.__setattr__(self, name, value)
            return
        
        # Store value at SRL location
        child_srl = self._srl.child(name)
        CORE.set(child_srl, value)
    
    # =========================================================================
    # INDEX ACCESS - Direct dimensional addressing
    # =========================================================================
    
    def __getitem__(self, key) -> Any:
        """car[0] or car["vin"] → direct access."""
        if isinstance(key, int):
            return self.__getattr__(f"_{key}")
        return self.__getattr__(str(key))
    
    def __setitem__(self, key, value: Any) -> None:
        """car[0] = x or car["vin"] = x."""
        if isinstance(key, int):
            self.__setattr__(f"_{key}", value)
        else:
            self.__setattr__(str(key), value)
    
    # =========================================================================
    # CALL SYNTAX - Direct path access
    # =========================================================================
    
    def __call__(self, path: str = None) -> Any:
        """
        car("engine.hp") → direct path access O(1)
        """
        if path is None:
            return self
        
        # Build full SRL and get from Core
        full_srl = self._srl
        for part in path.split('.'):
            full_srl = full_srl.child(part)
        
        value = CORE.get(full_srl)
        if value is not None:
            return value
        
        # Return interface at that path
        current = self
        for part in path.split('.'):
            current = getattr(current, part)
        return current
    
    # =========================================================================
    # RECURSION - When many items needed (down the pipeline)
    # =========================================================================
    
    def recurse(self, fn: Callable[['Interface', int], Any], depth: int = 0, max_depth: int = 7) -> List[Any]:
        """
        Recurse DOWN the dimensional pipeline.
        Use when many items must be referenced.
        """
        results = []
        result = fn(self, depth)
        if result is not None:
            results.append(result)
        
        if depth < max_depth:
            for child in self._children.values():
                results.extend(child.recurse(fn, depth + 1, max_depth))
        
        return results
    
    # =========================================================================
    # REPRESENTATION
    # =========================================================================
    
    def __repr__(self) -> str:
        return f"<{self._type} @ {self._srl}>"


# Alias
Object = Interface


# =============================================================================
# DEVELOPER API - What developers actually use
# =============================================================================

def ingest(type_name: str, **values) -> Interface:
    """
    Ingest an object from the substrate.
    
    Like ingesting food - bring data into the system.
    
    Usage:
        car = ingest("Car")
        car = ingest("Car", vin="ABC123", make="Toyota")
    """
    obj = Interface(type_name)
    for key, value in values.items():
        setattr(obj, key, value)
    return obj


def invoke(type_name: str, **values) -> Interface:
    """Alias for ingest."""
    return ingest(type_name, **values)


def get(address: str) -> Any:
    """
    Direct SRL access.
    
    Usage:
        value = get("local/0.6.car.vin")
    """
    return CORE.get(srl(address))


def put(address: str, value: Any) -> None:
    """
    Direct SRL write.
    
    Usage:
        put("local/0.6.car.vin", "ABC123")
    """
    CORE.set(srl(address), value)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'Core', 'CORE',
    'Interface', 'Object',
    'ingest', 'invoke',
    'get', 'put',
    'SRL', 'srl', 'Level',
]
