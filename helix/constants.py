"""
ButterflyFX Constants - Standard Constants and Values

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

Attribution required: Kenneth Bingham - https://butterflyfx.us

---

Standard constants used throughout ButterflyFX.

Includes:
    - Mathematical constants (phi, Fibonacci)
    - Level definitions
    - Helix geometry constants
    - Default configurations
"""

from __future__ import annotations
import math
from typing import Dict, List, Tuple
from enum import IntEnum


# =============================================================================
# MATHEMATICAL CONSTANTS
# =============================================================================

# Golden Ratio
PHI = (1 + math.sqrt(5)) / 2  # φ ≈ 1.618033988749895
PHI_INVERSE = PHI - 1  # 1/φ ≈ 0.618033988749895

# Fibonacci sequence (first 20 numbers)
FIBONACCI = (0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181)

# Fibonacci ratios (approach phi)
FIBONACCI_RATIOS = tuple(FIBONACCI[i+1] / FIBONACCI[i] if FIBONACCI[i] != 0 else 0 for i in range(len(FIBONACCI) - 1))

# Lucas numbers (related to Fibonacci)
LUCAS = (2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322, 521, 843, 1364)

# Pi multiples used in helix
PI = math.pi
TAU = 2 * math.pi  # Full rotation
HALF_PI = math.pi / 2
QUARTER_PI = math.pi / 4
SEVENTH_PI = math.pi / 7  # One level step on helix


# =============================================================================
# LEVEL CONSTANTS
# =============================================================================

class Level(IntEnum):
    """Helix level enumeration"""
    POTENTIAL = 0  # ○ - Pure possibility
    POINT = 1      # • - Single location
    LENGTH = 2     # ━ - One dimension
    WIDTH = 3      # ▭ - Two dimensions
    PLANE = 4      # ▦ - Surface
    VOLUME = 5     # ▣ - Three dimensions
    WHOLE = 6      # ◉ - Complete entity


# Level metadata
LEVEL_NAMES: Dict[int, str] = {
    0: "Potential",
    1: "Point",
    2: "Length",
    3: "Width",
    4: "Plane",
    5: "Volume",
    6: "Whole"
}

LEVEL_ICONS: Dict[int, str] = {
    0: "○",
    1: "•",
    2: "━",
    3: "▭",
    4: "▦",
    5: "▣",
    6: "◉"
}

LEVEL_DIMENSIONS: Dict[int, int] = {
    0: 0,  # Zero-dimensional
    1: 0,  # Zero-dimensional (point)
    2: 1,  # One-dimensional
    3: 2,  # Two-dimensional
    4: 2,  # Two-dimensional (surface)
    5: 3,  # Three-dimensional
    6: 3   # Three-dimensional (whole)
}

LEVEL_DESCRIPTIONS: Dict[int, str] = {
    0: "Pure potential - unmanifested possibility",
    1: "A single point - location without extension",
    2: "A line - extension in one direction",
    3: "Width - extension in two perpendicular directions",
    4: "A plane - a flat surface",
    5: "Volume - extension in three directions",
    6: "The whole - complete entity with all properties"
}

# =============================================================================
# SEMANTIC LAYER (Identity-First Paradigm)
# =============================================================================
# Each level has both a GEOMETRIC meaning (shape) and SEMANTIC meaning (purpose)
# "Manifestation does NOT begin with the object — it begins with identity."

SEMANTIC_NAMES: Dict[int, str] = {
    0: "Void",           # Nothing exists — only possibility
    1: "Identity",       # UUID, name, "this" — the anchor, NOT the object
    2: "Relationship",   # Attributes, references, links, directions
    3: "Structure",      # Schema, blueprint, geometry — still no object
    4: "Manifestation",  # Object APPEARS here — first visible form
    5: "Multiplicity",   # Systems, behavior, interaction, scaling
    6: "Meaning"         # Interpretation — transcends form
}

SEMANTIC_DESCRIPTIONS: Dict[int, str] = {
    0: "Nothing exists yet — only pure possibility",
    1: "The identity anchor (UUID, name, 'this') — NOT the object itself",
    2: "Attributes, references, links — relationships between identities",
    3: "Schema, blueprint, geometry — the structure before manifestation",
    4: "The object APPEARS — first visible/tangible form (collapsed projection)",
    5: "Systems, behavior, interaction — multiplicity and dynamics",
    6: "Interpretation and meaning — transcends the physical form"
}

# The Identity-First insight:
# - Identity (D1) is MORE FUNDAMENTAL (everything derives from here)
# - Object (D4) is the MANIFESTATION POINT (collapsed projection)
# - Meaning (D6) is MORE ABSTRACT (transcends the physical form)
# "The object is not the truth — it is the shadow."

# =============================================================================
# UNIVERSAL PATTERN MAPPINGS
# =============================================================================
# The 7-level helix appears in multiple established systems.
# ButterflyFX did not invent this — we formalized what already exists.

# OSI Network Model mapping
OSI_LAYER_NAMES: Dict[int, str] = {
    0: "(Pre-network)",      # Before any networking exists
    1: "Physical",           # Identity: MAC address, the "this"
    2: "Data Link",          # Relationship: frames, links
    3: "Network",            # Structure: IP addressing, routing
    4: "Transport",          # Manifestation: packets exist
    5: "Session",            # Multiplicity: connections, state
    6: "Presentation",       # Meaning: encoding, interpretation
    # 7: "Application"       # → becomes level 0 of next spiral
}

# Genesis Creation mapping
GENESIS_DAYS: Dict[int, str] = {
    0: "Formless and void",           # Before creation
    1: "Let there be light",          # Identity: first distinction
    2: "Separation of waters",        # Relationship: division
    3: "Land and vegetation",         # Structure: form emerges
    4: "Sun, moon, and stars",        # Manifestation: visible bodies
    5: "Fish and birds",              # Multiplicity: living systems
    6: "Humans",                       # Meaning: purpose/interpretation
    # 7: "Rest"                        # → completion becomes new potential
}

# Fibonacci mapping (the mathematical proof)
FIBONACCI_LEVELS: Dict[int, int] = {
    0: FIBONACCI[0],   # 0 - Void
    1: FIBONACCI[1],   # 1 - Identity
    2: FIBONACCI[2],   # 1 - Relationship
    3: FIBONACCI[3],   # 2 - Structure
    4: FIBONACCI[4],   # 3 - Manifestation
    5: FIBONACCI[5],   # 5 - Multiplicity
    6: FIBONACCI[6],   # 8 - Meaning
    # 7: FIBONACCI[7]  # 13 - POINT of next spiral (8+5=13)
}

# Level colors (for visualization)
LEVEL_COLORS: Dict[int, str] = {
    0: "#FFFFFF",  # White - potential
    1: "#FF0000",  # Red - point
    2: "#FF7F00",  # Orange - length
    3: "#FFFF00",  # Yellow - width
    4: "#00FF00",  # Green - plane
    5: "#0000FF",  # Blue - volume
    6: "#8B00FF"   # Violet - whole
}

LEVEL_RGB: Dict[int, Tuple[int, int, int]] = {
    0: (255, 255, 255),
    1: (255, 0, 0),
    2: (255, 127, 0),
    3: (255, 255, 0),
    4: (0, 255, 0),
    5: (0, 0, 255),
    6: (139, 0, 255)
}


# =============================================================================
# HELIX GEOMETRY CONSTANTS
# =============================================================================

# Number of levels per spiral turn
LEVELS_PER_SPIRAL = 7

# Default helix parameters
DEFAULT_HELIX_RADIUS = 1.0
DEFAULT_HELIX_PITCH = PHI  # Vertical distance per full turn

# Angle per level (in radians)
LEVEL_ANGLE = TAU / LEVELS_PER_SPIRAL  # ≈ 0.897 radians

# Standard helix parametric equations use:
# x(t) = r * cos(t)
# y(t) = r * sin(t)
# z(t) = (pitch / TAU) * t


# =============================================================================
# OPERATION CONSTANTS
# =============================================================================

class Operation(IntEnum):
    """Helix kernel operations"""
    INVOKE = 0
    SPIRAL_UP = 1
    SPIRAL_DOWN = 2
    COLLAPSE = 3


OPERATION_NAMES: Dict[int, str] = {
    0: "INVOKE",
    1: "SPIRAL_UP",
    2: "SPIRAL_DOWN",
    3: "COLLAPSE"
}


# =============================================================================
# DEFAULT CONFIGURATIONS
# =============================================================================

# Default limits
DEFAULT_MAX_SPIRAL = 1000
DEFAULT_MIN_SPIRAL = -1000
DEFAULT_MAX_TOKENS = 100000
DEFAULT_CACHE_SIZE = 1024
DEFAULT_QUERY_LIMIT = 100

# Timeouts (in seconds)
DEFAULT_OPERATION_TIMEOUT = 30.0
DEFAULT_MATERIALIZATION_TIMEOUT = 5.0
DEFAULT_QUERY_TIMEOUT = 10.0


# =============================================================================
# SIGNATURE PRESETS
# =============================================================================

# Common signature patterns
ALL_LEVELS = frozenset({0, 1, 2, 3, 4, 5, 6})
NO_LEVELS = frozenset()
LOWER_LEVELS = frozenset({0, 1, 2, 3})
UPPER_LEVELS = frozenset({4, 5, 6})
ODD_LEVELS = frozenset({1, 3, 5})
EVEN_LEVELS = frozenset({0, 2, 4, 6})
MIDDLE_LEVELS = frozenset({2, 3, 4})
EXTREMES = frozenset({0, 6})


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def fib(n: int) -> int:
    """Get nth Fibonacci number"""
    if n < len(FIBONACCI):
        return FIBONACCI[n]
    a, b = FIBONACCI[-2], FIBONACCI[-1]
    for _ in range(len(FIBONACCI), n + 1):
        a, b = b, a + b
    return b


def fibonacci_sequence(count: int) -> Tuple[int, ...]:
    """Generate Fibonacci sequence of given length"""
    if count <= 0:
        return ()
    if count <= len(FIBONACCI):
        return FIBONACCI[:count]
    
    result = list(FIBONACCI)
    while len(result) < count:
        result.append(result[-1] + result[-2])
    return tuple(result[:count])


def is_fibonacci(n: int) -> bool:
    """Check if a number is a Fibonacci number"""
    if n < 0:
        return False
    if n in FIBONACCI:
        return True
    # Check using formula: n is Fibonacci iff 5n²+4 or 5n²-4 is a perfect square
    def is_perfect_square(x):
        s = int(math.sqrt(x))
        return s * s == x
    return is_perfect_square(5 * n * n + 4) or is_perfect_square(5 * n * n - 4)


def fibonacci_index(n: int) -> int:
    """Get the index of n in Fibonacci sequence (-1 if not found)"""
    for i, f in enumerate(FIBONACCI):
        if f == n:
            return i
    if not is_fibonacci(n):
        return -1
    # Calculate index for larger numbers
    idx = len(FIBONACCI) - 1
    a, b = FIBONACCI[-2], FIBONACCI[-1]
    while b < n:
        a, b = b, a + b
        idx += 1
    return idx if b == n else -1


def level_angle(level: int, spiral: int = 0) -> float:
    """Get the angle (in radians) for a helix position"""
    return (spiral * LEVELS_PER_SPIRAL + level) * LEVEL_ANGLE


def level_position(level: int, spiral: int = 0, radius: float = 1.0, pitch: float = PHI) -> Tuple[float, float, float]:
    """Get 3D position on helix for a given level and spiral"""
    t = level_angle(level, spiral)
    x = radius * math.cos(t)
    y = radius * math.sin(t)
    z = (pitch / TAU) * t
    return (x, y, z)


# =============================================================================
# LEVEL LOOKUP TABLES
# =============================================================================

def level_by_name(name: str) -> int:
    """Get level number by name (case-insensitive)"""
    name_lower = name.lower()
    for level, level_name in LEVEL_NAMES.items():
        if level_name.lower() == name_lower:
            return level
    raise ValueError(f"Unknown level name: {name}")


def level_by_icon(icon: str) -> int:
    """Get level number by icon"""
    for level, level_icon in LEVEL_ICONS.items():
        if level_icon == icon:
            return level
    raise ValueError(f"Unknown level icon: {icon}")


# =============================================================================
# DIMENSIONAL RELATIONSHIPS
# =============================================================================

# How levels relate to each other
LEVEL_CONTAINS: Dict[int, List[int]] = {
    6: [5, 4, 3, 2, 1, 0],  # Whole contains all
    5: [4, 3, 2, 1, 0],     # Volume contains plane and below
    4: [3, 2, 1, 0],        # Plane contains width and below
    3: [2, 1, 0],           # Width contains length and below
    2: [1, 0],              # Length contains point and below
    1: [0],                 # Point contains potential
    0: []                   # Potential contains nothing
}

LEVEL_CONTAINED_BY: Dict[int, List[int]] = {
    0: [1, 2, 3, 4, 5, 6],  # Potential is contained by all
    1: [2, 3, 4, 5, 6],     # Point contained by length and above
    2: [3, 4, 5, 6],        # Length contained by width and above
    3: [4, 5, 6],           # Width contained by plane and above
    4: [5, 6],              # Plane contained by volume and above
    5: [6],                 # Volume contained by whole
    6: []                   # Whole contained by nothing
}


# =============================================================================
# STRING CONSTANTS
# =============================================================================

VERSION = "1.0.0"
AUTHOR = "Kenneth Bingham"
LICENSE = "CC BY 4.0"
ATTRIBUTION = "Kenneth Bingham - https://butterflyfx.us"
COPYRIGHT = "Copyright (c) 2024-2026 Kenneth Bingham"
