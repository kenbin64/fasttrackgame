"""
Manifold Substrate - Token Model Implementation

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

This mathematical kernel belongs to all humanity.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

Implements the ButterflyFX Manifold Substrate as specified in BUTTERFLYFX_SPECIFICATION.md

Components:
    - Manifold M: Space of potential (represented as coordinate space)
    - Tokens T: Entities with (location, signature, payload)
    - Relations R: Connections between tokens
    - Materialization μ: H -> P(T)

Key property: Payloads are LAZY - not dereferenced until materialization.

GENERATIVE PRINCIPLE:
    The manifold is a mathematical surface - we don't need to STORE data when
    we can DERIVE it from the geometry. Tokens can pull their values directly
    from manifold coordinates (angles, slopes, curvature, etc.)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Set, Dict, List, Any, Callable, Optional, Union, TYPE_CHECKING
from collections import defaultdict
from enum import Enum, auto
import uuid
import math

if TYPE_CHECKING:
    from .manifold import GenerativeManifold


# =============================================================================
# PAYLOAD SOURCE - Where does the token's value come from?
# =============================================================================

class PayloadSource(Enum):
    """How a token derives its payload value"""
    STORED = auto()        # Traditional: value is stored/provided
    GEOMETRIC = auto()     # Derived from manifold geometry at location
    COMPUTED = auto()      # Computed from a function of position
    EXTRAPOLATED = auto()  # Extrapolated from nearby values
    COMPOSITE = auto()     # Combined from multiple sources


class GeometricProperty(Enum):
    """Which geometric property to extract from manifold surface"""
    # Trigonometric
    SIN = "sin"
    COS = "cos"
    TAN = "tan"
    COT = "cot"
    SEC = "sec"
    CSC = "csc"
    
    # Position
    X = "x"
    Y = "y"
    Z = "z"
    ANGLE = "angle"
    T = "t"
    
    # Derivatives
    SLOPE = "slope"
    DX_DT = "dx_dt"
    DY_DT = "dy_dt"
    DZ_DT = "dz_dt"
    GRADIENT = "gradient_magnitude"
    TANGENT = "tangent_vector"
    
    # Curvature
    CURVATURE = "curvature"
    TORSION = "torsion"
    D2X_DT2 = "d2x_dt2"
    D2Y_DT2 = "d2y_dt2"
    INFLECTION = "inflection_distance"
    
    # Frenet-Serret frame
    NORMAL = "normal_vector"
    BINORMAL = "binormal_vector"


# =============================================================================
# LENS SYSTEM - Derives Color, Sound, and Value from Geometric Properties
# =============================================================================
# 
# This is the NATURAL lens system. Values are NOT arbitrary or imposed.
# They are EXTRACTED from the actual geometric properties of the point:
#
#   COLOR: From AZIMUTH ANGLE (θ) → Visible spectrum wavelength
#          - The angle IS the wavelength (radians map to nanometers)
#          - 0° = Red (700nm), 60° = Yellow (580nm), 120° = Green (510nm),
#            180° = Cyan (490nm), 240° = Blue (450nm), 300° = Violet (380nm)
#
#   SOUND: From MAGNITUDE (|r|) → Physical resonating length → Frequency
#          - f = c / (2L) where L = magnitude mapped to pipe/string length
#          - Small magnitude = short string = high frequency (flute)
#          - Large magnitude = long string = low frequency (bass)
#
#   VALUE: The raw geometric properties (magnitude, angle, derivatives)
#
# =============================================================================

class LensType(Enum):
    """Which perceptual property to extract"""
    COLOR = "color"      # Spectral color from azimuth angle
    SOUND = "sound"      # Frequency from magnitude
    VALUE = "value"      # Raw geometric properties


@dataclass(frozen=True)
class PhysicalConstants:
    """Physical constants for natural lens calculations"""
    SPEED_OF_LIGHT: float = 299792458.0       # m/s
    SPEED_OF_SOUND: float = 343.0             # m/s in air at 20°C
    PLANCK: float = 6.62607015e-34            # Planck's constant J·s
    
    # Visible light spectrum (nm)
    WAVELENGTH_VIOLET: float = 380.0
    WAVELENGTH_RED: float = 700.0
    
    # Audible sound (Hz) - piano range A0 to C8
    FREQ_MIN: float = 27.5                    # A0
    FREQ_MAX: float = 4186.01                 # C8
    
    # String/pipe resonating lengths (m)
    RESONANT_LENGTH_MIN: float = 0.041        # ~41mm (piccolo)
    RESONANT_LENGTH_MAX: float = 6.25         # ~6.25m (bass organ pipe)


PHYSICS = PhysicalConstants()


@dataclass(frozen=True)
class ColorLens:
    """
    Color derived NATURALLY from azimuth angle.
    
    The angle θ on the manifold surface maps directly to the electromagnetic
    spectrum. This is NOT arbitrary - light waves have wavelengths, and our
    mapping preserves the physics: angle ↔ wavelength ↔ frequency.
    """
    wavelength_nm: float    # Wavelength in nanometers (380-700)
    r: int                  # Red component (0-255)
    g: int                  # Green component (0-255)
    b: int                  # Blue component (0-255)
    luminosity: float       # Luminosity from z-height (0-1)
    
    @classmethod
    def from_angle(cls, azimuth: float, z: float = 0.0, z_range: float = 1.5) -> 'ColorLens':
        """
        Derive color from azimuth angle.
        
        Args:
            azimuth: Angle in radians (from atan2(y, x))
            z: Height for luminosity
            z_range: Expected z range
            
        Returns:
            ColorLens with wavelength and RGB derived from angle
        """
        # Normalize angle to [0, 2π]
        a = ((azimuth % (2 * math.pi)) + 2 * math.pi) % (2 * math.pi)
        
        # Map angle to visible spectrum
        # Color wheel: 0°→Red, 60°→Yellow, 120°→Green, 180°→Cyan, 240°→Blue, 300°→Violet
        # Visible spectrum: 700nm (red) → 380nm (violet)
        position = a / (2 * math.pi)  # 0 to 1
        
        # Map to wavelength (only use 5/6 of wheel for visible spectrum)
        if position <= 5/6:
            t = position / (5/6)
            wavelength = PHYSICS.WAVELENGTH_RED - t * (PHYSICS.WAVELENGTH_RED - PHYSICS.WAVELENGTH_VIOLET)
        else:
            # Wrap back to red
            t = (position - 5/6) / (1/6)
            wavelength = PHYSICS.WAVELENGTH_VIOLET + t * (PHYSICS.WAVELENGTH_RED - PHYSICS.WAVELENGTH_VIOLET)
        
        # Convert wavelength to RGB using CIE 1931 approximation
        r, g, b = cls._wavelength_to_rgb(wavelength)
        
        # Luminosity from z-height
        luminosity = max(0.2, min(1.0, 0.3 + ((z + z_range) / (2 * z_range)) * 0.7))
        
        # Apply luminosity
        r = int(r * luminosity)
        g = int(g * luminosity)
        b = int(b * luminosity)
        
        return cls(wavelength_nm=wavelength, r=r, g=g, b=b, luminosity=luminosity)
    
    @staticmethod
    def _wavelength_to_rgb(wavelength: float) -> tuple:
        """CIE 1931 spectral locus approximation"""
        wavelength = max(380, min(700, wavelength))
        
        if 380 <= wavelength < 440:
            r = -(wavelength - 440) / 60
            g = 0.0
            b = 1.0
        elif 440 <= wavelength < 490:
            r = 0.0
            g = (wavelength - 440) / 50
            b = 1.0
        elif 490 <= wavelength < 510:
            r = 0.0
            g = 1.0
            b = -(wavelength - 510) / 20
        elif 510 <= wavelength < 580:
            r = (wavelength - 510) / 70
            g = 1.0
            b = 0.0
        elif 580 <= wavelength < 645:
            r = 1.0
            g = -(wavelength - 645) / 65
            b = 0.0
        else:
            r = 1.0
            g = 0.0
            b = 0.0
        
        # Intensity attenuation at spectrum edges
        if 380 <= wavelength < 420:
            intensity = 0.3 + 0.7 * (wavelength - 380) / 40
        elif wavelength > 645:
            intensity = 0.3 + 0.7 * (700 - wavelength) / 55
        else:
            intensity = 1.0
        
        # Gamma correction
        gamma = 0.8
        r = int(255 * pow(r * intensity, gamma))
        g = int(255 * pow(g * intensity, gamma))
        b = int(255 * pow(b * intensity, gamma))
        
        return (r, g, b)
    
    @property
    def rgb(self) -> str:
        """CSS rgb() format"""
        return f"rgb({self.r}, {self.g}, {self.b})"
    
    @property
    def hex(self) -> str:
        """Hex color code"""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"


@dataclass(frozen=True)
class SoundLens:
    """
    Sound derived NATURALLY from vector magnitude.
    
    The magnitude |r| = √(x² + y² + z²) represents the resonating length
    of a string or pipe. Physics: f = c / (2L).
    
    Small magnitude → short string → high frequency (flute, piccolo)
    Large magnitude → long string → low frequency (bass, organ)
    """
    frequency_hz: float     # Frequency in Hz
    wavelength_m: float     # Sound wavelength in meters
    note_name: str          # Musical note name (e.g., "C4", "A#3")
    instrument: str         # Natural instrument for this range
    
    # Overtone series
    harmonics: tuple = ()   # First 8 harmonics
    
    @classmethod
    def from_magnitude(cls, magnitude: float, max_magnitude: float = 1.5) -> 'SoundLens':
        """
        Derive sound from vector magnitude.
        
        Args:
            magnitude: |r| = √(x² + y² + z²)
            max_magnitude: Maximum expected magnitude (for normalization)
            
        Returns:
            SoundLens with frequency, wavelength, note derived from magnitude
        """
        # Clamp and normalize magnitude
        m = max(0.01, min(magnitude, max_magnitude))
        normalized = m / max_magnitude  # 0 to 1
        
        # Map to resonating length (logarithmic interpolation)
        log_min = math.log(PHYSICS.RESONANT_LENGTH_MIN)
        log_max = math.log(PHYSICS.RESONANT_LENGTH_MAX)
        length = math.exp(log_min + normalized * (log_max - log_min))
        
        # f = c / (2L)
        freq = PHYSICS.SPEED_OF_SOUND / (2 * length)
        
        # Sound wavelength
        wavelength = PHYSICS.SPEED_OF_SOUND / freq
        
        # Note name
        note_name = cls._freq_to_note(freq)
        
        # Instrument
        instrument = cls._freq_to_instrument(freq)
        
        # Harmonics (natural overtone series)
        harmonics = tuple(freq * (i + 1) for i in range(8))
        
        return cls(
            frequency_hz=freq,
            wavelength_m=wavelength,
            note_name=note_name,
            instrument=instrument,
            harmonics=harmonics
        )
    
    @staticmethod
    def _freq_to_note(freq: float) -> str:
        """Convert frequency to note name (12-TET, A4=440Hz)"""
        NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        midi = 69 + 12 * math.log2(freq / 440.0)
        rounded = round(midi)
        octave = (rounded // 12) - 1
        note_index = ((rounded % 12) + 12) % 12
        return f"{NOTE_NAMES[note_index]}{octave}"
    
    @staticmethod
    def _freq_to_instrument(freq: float) -> str:
        """Natural instrument for frequency range"""
        if freq < 100:
            return "Bass"
        elif freq < 262:
            return "Cello"
        elif freq < 523:
            return "Viola"
        elif freq < 2000:
            return "Violin"
        else:
            return "Flute"


@dataclass(frozen=True)
class ValueLens:
    """
    Raw geometric values from the point.
    
    This is the pure mathematical information, not transformed for perception.
    """
    magnitude: float            # |r| = √(x² + y² + z²)
    azimuth: float              # θ = atan2(y, x) in radians
    azimuth_degrees: float      # θ in degrees
    elevation: float            # φ = atan2(z, √(x²+y²)) in radians
    elevation_degrees: float    # φ in degrees
    x: float
    y: float
    z: float
    
    @classmethod
    def from_point(cls, x: float, y: float, z: float = 0.0) -> 'ValueLens':
        """Create ValueLens from cartesian coordinates"""
        magnitude = math.sqrt(x*x + y*y + z*z)
        azimuth = math.atan2(y, x)
        elevation = math.atan2(z, math.sqrt(x*x + y*y)) if (x*x + y*y) > 0 else 0.0
        
        return cls(
            magnitude=magnitude,
            azimuth=azimuth,
            azimuth_degrees=math.degrees(azimuth),
            elevation=elevation,
            elevation_degrees=math.degrees(elevation),
            x=x, y=y, z=z
        )


@dataclass(frozen=True)
class NaturalLens:
    """
    Complete natural lens system for a geometric point.
    
    Combines color (from angle), sound (from magnitude), and value (raw)
    into a single structure that extracts ALL perceptual properties
    from the actual geometry.
    
    Usage:
        lens = NaturalLens.from_geometry(x, y, z)
        print(lens.color.rgb)     # "rgb(255, 100, 50)"
        print(lens.sound.note_name)  # "C4"
        print(lens.value.magnitude)  # 0.707
    """
    color: ColorLens
    sound: SoundLens
    value: ValueLens
    
    @classmethod
    def from_geometry(cls, x: float, y: float, z: float = 0.0, 
                       max_magnitude: float = 1.5) -> 'NaturalLens':
        """
        Create complete lens from geometric point.
        
        ALL values are derived from the actual geometry - nothing is arbitrary.
        """
        # Value lens (raw geometry)
        value = ValueLens.from_point(x, y, z)
        
        # Color lens (from azimuth angle)
        color = ColorLens.from_angle(value.azimuth, z)
        
        # Sound lens (from magnitude)
        sound = SoundLens.from_magnitude(value.magnitude, max_magnitude)
        
        return cls(color=color, sound=sound, value=value)
    
    @classmethod
    def from_surface_point(cls, point: Any) -> 'NaturalLens':
        """Create lens from a SurfacePoint on the manifold"""
        return cls.from_geometry(point.x, point.y, point.z)


# =============================================================================
# TOKEN - Enhanced with Generative Capabilities
# =============================================================================

@dataclass
class Token:
    """
    A potential entity in the manifold.
    
    Components:
        id: Unique identifier
        location: Coordinates in the manifold (embedding)
        signature: Set of levels this token can inhabit {0..6}
        payload: Lazy data (callable that returns actual data)
        spiral_affinity: Primary spiral this token belongs to (optional scoping)
    
    GENERATIVE ENHANCEMENT:
        Tokens can now derive their payload from manifold geometry rather
        than storing it. Set payload_source to GEOMETRIC and geometric_property
        to specify which surface property to extract.
    """
    id: str
    location: tuple  # (x, y, z, ...) in manifold OR (spiral, level) for geometric
    signature: Set[int]  # Which levels {0,1,2,3,4,5,6} this token inhabits
    payload: Callable[[], Any]  # Lazy - called only on materialization
    spiral_affinity: Optional[int] = None
    
    # Generative fields
    payload_source: PayloadSource = field(default=PayloadSource.STORED, repr=False)
    geometric_property: Optional[GeometricProperty] = field(default=None, repr=False)
    
    # Track materialization state
    _materialized: bool = field(default=False, repr=False)
    _cached_value: Any = field(default=None, repr=False)
    _manifold_ref: Any = field(default=None, repr=False)  # Reference to GenerativeManifold
    
    def materialize(self) -> Any:
        """
        Realize the payload.
        
        For GEOMETRIC source, derives value from manifold surface.
        For STORED source, calls the payload factory.
        """
        if not self._materialized:
            if self.payload_source == PayloadSource.GEOMETRIC:
                self._cached_value = self._derive_from_geometry()
            elif self.payload_source == PayloadSource.COMPUTED:
                # Payload is a function of (spiral, level)
                spiral, level = self.location[0], self.location[1] if len(self.location) > 1 else 0
                self._cached_value = self.payload(spiral, level)
            else:
                self._cached_value = self.payload()
            self._materialized = True
        return self._cached_value
    
    def _derive_from_geometry(self) -> Any:
        """Extract value from manifold surface geometry"""
        if self._manifold_ref is None:
            raise ValueError("Token has GEOMETRIC source but no manifold reference")
        
        # Location is (spiral, level) for geometric tokens
        spiral = self.location[0]
        level = self.location[1] if len(self.location) > 1 else 0
        
        point = self._manifold_ref.at(spiral, level)
        prop = self.geometric_property
        
        if prop is None:
            raise ValueError("Token has GEOMETRIC source but no geometric_property set")
        
        # Extract the property from the surface point
        return getattr(point, prop.value)
    
    def release(self) -> None:
        """Return to potential (release cached value)"""
        self._materialized = False
        self._cached_value = None
    
    def inhabits(self, level: int) -> bool:
        """Check if this token can exist at the given level"""
        return level in self.signature
    
    @property
    def is_generative(self) -> bool:
        """True if this token derives its value from geometry"""
        return self.payload_source in (PayloadSource.GEOMETRIC, PayloadSource.COMPUTED)
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if isinstance(other, Token):
            return self.id == other.id
        return False


# =============================================================================
# MANIFOLD SUBSTRATE - ENHANCED WITH GENERATIVE CAPABILITIES
# =============================================================================

class ManifoldSubstrate:
    """
    The Manifold Substrate - Space of potential tokens.
    
    GENERATIVE PARADIGM:
        Don't store data - derive it from mathematics.
        The manifold surface IS the data source.
    
    Implements:
        - Token registration (stored and generative)
        - Materialization function μ(s, l) -> P(T)
        - Geometric value derivation
        - Relation queries
        - Lazy evaluation
    
    The substrate hides all indexing/searching from the kernel.
    The kernel only calls tokens_for_state() - O(1) from kernel perspective.
    """
    
    def __init__(self, manifold: 'GenerativeManifold' = None):
        """
        Initialize the substrate.
        
        Args:
            manifold: Optional GenerativeManifold for geometric derivation.
                     If not provided, creates one lazily when needed.
        """
        # Token storage
        self._tokens: Dict[str, Token] = {}
        
        # The underlying generative manifold
        self._manifold = manifold
        
        # Indices for fast lookup (implementation detail, hidden from kernel)
        self._by_level: Dict[int, Set[str]] = defaultdict(set)
        self._by_spiral: Dict[int, Set[str]] = defaultdict(set)
        
        # Relations
        self._relations: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))
        
        # =================================================================
        # INGESTION STORAGE - O(1) lookup by coordinate
        # =================================================================
        # Direct hash table: (spiral, level) -> value
        # This is THE primary storage for ingested data
        # Retrieval is O(1) - just a dictionary lookup
        self._ingested: Dict[tuple, Any] = {}
        
        # Keyed ingestion: (spiral, level, key) -> value
        # For multiple values at the same coordinate
        self._ingested_keyed: Dict[tuple, Any] = {}
        
        # Reverse lookup: value_hash -> (spiral, level) for finding where data lives
        self._value_locations: Dict[int, tuple] = {}
        
        # Ingestion stats
        self._ingestion_count = 0
        self._extraction_count = 0
        
        # Stats for benchmarking
        self._materialization_count = 0
        self._index_lookups = 0
        self._geometric_derivations = 0
    
    @property
    def manifold(self) -> 'GenerativeManifold':
        """Get or create the generative manifold"""
        if self._manifold is None:
            # Lazy import to avoid circular dependency
            from .manifold import GenerativeManifold
            self._manifold = GenerativeManifold()
        return self._manifold
    
    # -------------------------------------------------------------------------
    # Token Registration (Substrate API)
    # -------------------------------------------------------------------------
    
    def register_token(self, token: Token) -> str:
        """
        REGISTER_TOKEN: Add a token to the manifold.
        
        Updates indices for fast materialization queries.
        For generative tokens, sets the manifold reference.
        """
        # Set manifold reference for generative tokens
        if token.payload_source == PayloadSource.GEOMETRIC:
            token._manifold_ref = self.manifold
        
        self._tokens[token.id] = token
        
        # Index by level
        for level in token.signature:
            self._by_level[level].add(token.id)
        
        # Index by spiral affinity
        if token.spiral_affinity is not None:
            self._by_spiral[token.spiral_affinity].add(token.id)
        else:
            # Token is available in all spirals
            self._by_spiral[-999].add(token.id)  # Sentinel for "all spirals"
        
        return token.id
    
    def create_token(
        self,
        location: tuple,
        signature: Set[int],
        payload: Callable[[], Any],
        spiral_affinity: Optional[int] = None,
        token_id: Optional[str] = None
    ) -> Token:
        """Convenience: Create and register a stored token"""
        token = Token(
            id=token_id or str(uuid.uuid4()),
            location=location,
            signature=signature,
            payload=payload,
            spiral_affinity=spiral_affinity,
            payload_source=PayloadSource.STORED
        )
        self.register_token(token)
        return token
    
    # -------------------------------------------------------------------------
    # GENERATIVE TOKEN CREATION - Values from mathematics, not storage
    # -------------------------------------------------------------------------
    
    def create_geometric_token(
        self,
        spiral: int,
        level: int,
        geometric_property: GeometricProperty,
        signature: Optional[Set[int]] = None,
        token_id: Optional[str] = None
    ) -> Token:
        """
        Create a token that derives its value from manifold geometry.
        
        NO DATA STORED - value is computed from the surface when materialized.
        
        Args:
            spiral: Which spiral turn
            level: Which level (0-6)
            geometric_property: Which surface property to extract (SIN, COS, SLOPE, etc.)
            signature: Which levels this token inhabits (default: {level})
            token_id: Optional ID
        
        Example:
            # Create a token that returns sin(angle) at position (0, 3)
            token = substrate.create_geometric_token(0, 3, GeometricProperty.SIN)
            print(token.materialize())  # 1.0 (sin(π/2) at level 3)
        """
        token = Token(
            id=token_id or f"geo_{spiral}_{level}_{geometric_property.value}_{uuid.uuid4().hex[:8]}",
            location=(spiral, level),
            signature=signature or {level},
            payload=lambda: None,  # Not used for geometric tokens
            spiral_affinity=spiral,
            payload_source=PayloadSource.GEOMETRIC,
            geometric_property=geometric_property
        )
        self.register_token(token)
        return token
    
    def create_computed_token(
        self,
        location: tuple,
        compute_fn: Callable[[int, int], Any],
        signature: Set[int],
        spiral_affinity: Optional[int] = None,
        token_id: Optional[str] = None
    ) -> Token:
        """
        Create a token with a computed payload based on position.
        
        The compute_fn receives (spiral, level) and returns the value.
        This allows mathematical transformations of position.
        
        Example:
            # Token that returns level * spiral
            token = substrate.create_computed_token(
                (0, 3), 
                lambda s, l: s * l + 10,
                {3}
            )
        """
        token = Token(
            id=token_id or f"comp_{uuid.uuid4().hex[:8]}",
            location=location,
            signature=signature,
            payload=compute_fn,
            spiral_affinity=spiral_affinity,
            payload_source=PayloadSource.COMPUTED
        )
        self.register_token(token)
        return token
    
    def populate_with_geometry(
        self,
        spiral_range: tuple,
        level_range: tuple,
        properties: List[GeometricProperty]
    ) -> List[Token]:
        """
        Populate a region of the substrate with geometric tokens.
        
        Creates tokens for all combinations of position and property.
        No data is stored - all values derived from manifold surface.
        
        Args:
            spiral_range: (start, end) inclusive
            level_range: (start, end) inclusive
            properties: List of geometric properties to create tokens for
        
        Returns:
            List of created tokens
        """
        tokens = []
        for spiral in range(spiral_range[0], spiral_range[1] + 1):
            for level in range(level_range[0], level_range[1] + 1):
                for prop in properties:
                    token = self.create_geometric_token(spiral, level, prop)
                    tokens.append(token)
        return tokens
    
    # =========================================================================
    # INGESTION - Assimilate external data into the manifold with O(1) retrieval
    # =========================================================================
    
    def ingest(self, spiral: int, level: int, data: Any) -> tuple:
        """
        INGEST: Assimilate external data into the manifold at a coordinate.
        
        Once ingested, the data can be retrieved in O(1) time using extract().
        
        Args:
            spiral: Which spiral to place the data
            level: Which level (0-6) to place the data
            data: Any data from any source
        
        Returns:
            The coordinate tuple (spiral, level) where data was placed
        
        Complexity: O(1) insertion
        
        Example:
            substrate.ingest(0, 6, {"name": "Tesla", "type": "car"})
            substrate.ingest(0, 5, ["wheel", "engine", "battery"])
            substrate.ingest(1, 3, 42.5)
        """
        if not 0 <= level <= 6:
            raise ValueError(f"Level must be 0-6, got {level}")
        
        coord = (spiral, level)
        self._ingested[coord] = data
        
        # Track location by value hash for reverse lookup
        try:
            self._value_locations[hash(str(data))] = coord
        except:
            pass  # Some values aren't hashable, skip reverse lookup
        
        self._ingestion_count += 1
        return coord
    
    def ingest_keyed(self, spiral: int, level: int, key: str, data: Any) -> tuple:
        """
        INGEST_KEYED: Assimilate data with a key for multiple values at same coordinate.
        
        Allows storing multiple distinct values at the same (spiral, level).
        
        Args:
            spiral: Which spiral
            level: Which level (0-6)
            key: Unique key for this data item
            data: Any data from any source
        
        Returns:
            The full coordinate tuple (spiral, level, key)
        
        Complexity: O(1) insertion
        
        Example:
            substrate.ingest_keyed(0, 6, "car", {"name": "Tesla"})
            substrate.ingest_keyed(0, 6, "driver", {"name": "Alice"})
        """
        if not 0 <= level <= 6:
            raise ValueError(f"Level must be 0-6, got {level}")
        
        coord = (spiral, level, key)
        self._ingested_keyed[coord] = data
        self._ingestion_count += 1
        return coord
    
    def extract(self, spiral: int, level: int, default: Any = None) -> Any:
        """
        EXTRACT: Retrieve ingested data from a coordinate in O(1) time.
        
        This is the primary retrieval method - direct hash table lookup.
        
        Args:
            spiral: Which spiral
            level: Which level
            default: Value to return if nothing at coordinate (default: None)
        
        Returns:
            The ingested data, or default if nothing at that coordinate
        
        Complexity: O(1) - single dictionary lookup
        
        Example:
            data = substrate.extract(0, 6)  # O(1)
        """
        self._extraction_count += 1
        return self._ingested.get((spiral, level), default)
    
    def extract_keyed(self, spiral: int, level: int, key: str, default: Any = None) -> Any:
        """
        EXTRACT_KEYED: Retrieve keyed data from a coordinate in O(1) time.
        
        Complexity: O(1) - single dictionary lookup
        """
        self._extraction_count += 1
        return self._ingested_keyed.get((spiral, level, key), default)
    
    def extract_all_at(self, spiral: int, level: int) -> Dict[str, Any]:
        """
        Extract all keyed data at a coordinate.
        
        Returns dict of {key: value} for all data at (spiral, level).
        
        Complexity: O(k) where k = number of keys at this coordinate
        """
        result = {}
        prefix = (spiral, level)
        for coord, value in self._ingested_keyed.items():
            if coord[0] == spiral and coord[1] == level:
                result[coord[2]] = value
        return result
    
    def ingest_batch(
        self,
        data_list: List[Any],
        start_spiral: int = 0,
        start_level: int = 0
    ) -> List[tuple]:
        """
        INGEST_BATCH: Assimilate a list of data items sequentially.
        
        Data is placed along the helix, incrementing level then spiral.
        
        Args:
            data_list: List of data items to ingest
            start_spiral: Starting spiral (default 0)
            start_level: Starting level (default 0)
        
        Returns:
            List of coordinates where data was placed
        
        Example:
            coords = substrate.ingest_batch(["a", "b", "c", "d", "e", "f", "g", "h"])
            # Places: (0,0), (0,1), (0,2), (0,3), (0,4), (0,5), (0,6), (1,0)
        """
        coords = []
        spiral = start_spiral
        level = start_level
        
        for data in data_list:
            coords.append(self.ingest(spiral, level, data))
            level += 1
            if level > 6:
                level = 0
                spiral += 1
        
        return coords
    
    def ingest_dict(
        self,
        data: Dict[str, Any],
        spiral: int = 0,
        level: int = 6
    ) -> Dict[str, tuple]:
        """
        INGEST_DICT: Assimilate a dictionary, using keys as keyed storage.
        
        All key-value pairs are stored at the same (spiral, level) coordinate.
        
        Args:
            data: Dictionary to ingest
            spiral: Which spiral
            level: Which level
        
        Returns:
            Dict mapping keys to their full coordinates
        
        Example:
            coords = substrate.ingest_dict({"name": "Tesla", "year": 2024}, spiral=0)
            # substrate.extract_keyed(0, 6, "name") -> "Tesla"
        """
        result = {}
        for key, value in data.items():
            coord = self.ingest_keyed(spiral, level, key, value)
            result[key] = coord
        return result
    
    def ingest_hierarchical(
        self,
        data: Dict[str, Any],
        spiral: int = 0,
        top_level: int = 6
    ) -> Dict[str, tuple]:
        """
        INGEST_HIERARCHICAL: Assimilate nested data with level = depth.
        
        Top-level keys go to top_level, nested data goes to lower levels.
        Deeper nesting = lower level (more specific).
        
        Args:
            data: Nested dictionary
            spiral: Which spiral
            top_level: Starting level for top-level keys
        
        Returns:
            Dict mapping dot-notation paths to coordinates
        
        Example:
            data = {
                "car": {
                    "engine": {
                        "cylinders": 8
                    }
                }
            }
            coords = substrate.ingest_hierarchical(data)
            # "car" at level 6
            # "car.engine" at level 5
            # "car.engine.cylinders" at level 4
        """
        result = {}
        
        def process(obj: Any, path: str, level: int):
            if isinstance(obj, dict):
                # Store the dict itself at this level
                self.ingest_keyed(spiral, level, path, obj)
                result[path] = (spiral, level, path)
                
                # Process children at lower level
                if level > 0:
                    for key, value in obj.items():
                        child_path = f"{path}.{key}" if path else key
                        process(value, child_path, level - 1)
            else:
                # Leaf value
                self.ingest_keyed(spiral, level, path, obj)
                result[path] = (spiral, level, path)
        
        for key, value in data.items():
            process(value, key, top_level)
        
        return result
    
    def has(self, spiral: int, level: int) -> bool:
        """Check if data exists at coordinate. O(1)."""
        return (spiral, level) in self._ingested
    
    def has_keyed(self, spiral: int, level: int, key: str) -> bool:
        """Check if keyed data exists at coordinate. O(1)."""
        return (spiral, level, key) in self._ingested_keyed
    
    def remove(self, spiral: int, level: int) -> Any:
        """Remove and return data at coordinate. O(1)."""
        return self._ingested.pop((spiral, level), None)
    
    def remove_keyed(self, spiral: int, level: int, key: str) -> Any:
        """Remove and return keyed data. O(1)."""
        return self._ingested_keyed.pop((spiral, level, key), None)
    
    def clear_spiral(self, spiral: int) -> int:
        """Remove all ingested data in a spiral. Returns count removed."""
        removed = 0
        to_remove = [k for k in self._ingested.keys() if k[0] == spiral]
        for k in to_remove:
            del self._ingested[k]
            removed += 1
        
        to_remove_keyed = [k for k in self._ingested_keyed.keys() if k[0] == spiral]
        for k in to_remove_keyed:
            del self._ingested_keyed[k]
            removed += 1
        
        return removed
    
    def list_coordinates(self) -> List[tuple]:
        """List all coordinates with ingested data."""
        return list(self._ingested.keys())
    
    def list_keyed_coordinates(self) -> List[tuple]:
        """List all keyed coordinates."""
        return list(self._ingested_keyed.keys())
    
    @property
    def ingested_count(self) -> int:
        """Total ingested items (simple + keyed)."""
        return len(self._ingested) + len(self._ingested_keyed)
    
    # -------------------------------------------------------------------------
    # DIRECT GEOMETRIC ACCESS - Pull values without tokens
    # -------------------------------------------------------------------------
    
    def derive_value(
        self,
        spiral: int,
        level: int,
        property: GeometricProperty
    ) -> Any:
        """
        Directly derive a value from manifold geometry.
        
        Skips token creation - just pulls the value from mathematics.
        Use this when you need a value but don't need to track it as a token.
        """
        self._geometric_derivations += 1
        point = self.manifold.at(spiral, level)
        return getattr(point, property.value)
    
    def derive_matrix(
        self,
        spiral_range: tuple,
        level_range: tuple,
        property: GeometricProperty
    ) -> List[List[float]]:
        """
        Derive a matrix of values directly from the manifold surface.
        
        No storage, no tokens - pure mathematical extraction.
        """
        matrix = []
        for spiral in range(spiral_range[0], spiral_range[1] + 1):
            row = []
            for level in range(level_range[0], level_range[1] + 1):
                row.append(self.derive_value(spiral, level, property))
            matrix.append(row)
        return matrix
    
    def derive_function(
        self,
        property: GeometricProperty
    ) -> Callable[[int, int], float]:
        """
        Create a function that derives values from the manifold.
        
        Returns f(spiral, level) -> value
        """
        def f(spiral: int, level: int) -> float:
            return self.derive_value(spiral, level, property)
        return f
    
    def derive_wave(
        self,
        wave_type: str = 'sin',
        frequency: float = 1.0,
        amplitude: float = 1.0
    ) -> Callable[[float], float]:
        """Generate a wave function directly from manifold geometry"""
        return self.manifold.as_wave(wave_type, frequency, amplitude)
    
    def derive_spectrum(
        self,
        spiral_range: tuple,
        level_range: tuple,
        num_harmonics: int = 7
    ) -> Dict[int, complex]:
        """Extract spectrum from a region of the manifold"""
        region = self.manifold.region(
            spiral_range[0], level_range[0],
            spiral_range[1], level_range[1]
        )
        return self.manifold.as_spectrum(region, num_harmonics)
    
    def derive_probability(
        self,
        spiral_range: tuple,
        level_range: tuple
    ) -> Callable[[int, int], float]:
        """Generate a probability distribution from manifold geometry"""
        region = self.manifold.region(
            spiral_range[0], level_range[0],
            spiral_range[1], level_range[1]
        )
        return self.manifold.as_probability(region)
    
    def derive_graph(
        self,
        spiral_range: tuple,
        level_range: tuple
    ) -> Dict[tuple, List[tuple]]:
        """Generate a graph structure from manifold topology"""
        region = self.manifold.region(
            spiral_range[0], level_range[0],
            spiral_range[1], level_range[1]
        )
        return self.manifold.as_graph(region)
    
    # -------------------------------------------------------------------------
    # Materialization (Substrate API)
    # -------------------------------------------------------------------------
    
    def tokens_for_state(self, spiral: int, level: int) -> Set[Token]:
        """
        TOKENS_FOR_STATE: Implementation of μ(s, l).
        
        Returns tokens that:
            1. Have level in their signature
            2. Are scoped to this spiral (or all spirals)
        
        This is O(k) where k = matching tokens, but from the kernel's
        perspective it's a single operation - the kernel doesn't loop.
        """
        self._index_lookups += 1
        
        # Get tokens at this level
        level_tokens = self._by_level.get(level, set())
        
        # Filter by spiral scoping
        spiral_tokens = self._by_spiral.get(spiral, set())
        all_spiral_tokens = self._by_spiral.get(-999, set())
        valid_tokens = spiral_tokens | all_spiral_tokens
        
        # Intersection: level + spiral
        matching_ids = level_tokens & valid_tokens if valid_tokens else level_tokens
        
        # Return actual token objects
        result = set()
        for token_id in matching_ids:
            token = self._tokens[token_id]
            self._materialization_count += 1
            result.add(token)
        
        return result
    
    def release_materialized(self, spiral: int) -> None:
        """
        RELEASE_MATERIALIZED: Return tokens to potential state.
        
        Called on COLLAPSE to release cached values.
        """
        spiral_tokens = self._by_spiral.get(spiral, set())
        all_spiral_tokens = self._by_spiral.get(-999, set())
        
        for token_id in spiral_tokens | all_spiral_tokens:
            if token_id in self._tokens:
                self._tokens[token_id].release()
    
    # -------------------------------------------------------------------------
    # Relations (Optional Substrate API)
    # -------------------------------------------------------------------------
    
    def add_relation(self, from_id: str, to_id: str, relation_type: str) -> None:
        """Add a relation between two tokens"""
        self._relations[from_id][relation_type].add(to_id)
    
    def related(self, token_id: str, relation_type: str) -> Set[Token]:
        """Get tokens related to the given token"""
        related_ids = self._relations.get(token_id, {}).get(relation_type, set())
        return {self._tokens[tid] for tid in related_ids if tid in self._tokens}
    
    # -------------------------------------------------------------------------
    # Stats (for benchmarking)
    # -------------------------------------------------------------------------
    
    @property
    def token_count(self) -> int:
        return len(self._tokens)
    
    @property
    def generative_token_count(self) -> int:
        return sum(1 for t in self._tokens.values() if t.is_generative)
    
    @property
    def stored_token_count(self) -> int:
        return sum(1 for t in self._tokens.values() if not t.is_generative)
    
    @property
    def materialization_count(self) -> int:
        return self._materialization_count
    
    @property
    def geometric_derivation_count(self) -> int:
        return self._geometric_derivations
    
    @property
    def ingestion_stats(self) -> Dict[str, int]:
        """Ingestion statistics"""
        return {
            'ingested': len(self._ingested),
            'ingested_keyed': len(self._ingested_keyed),
            'total': self.ingested_count,
            'ingestion_ops': self._ingestion_count,
            'extraction_ops': self._extraction_count,
        }
    
    @property 
    def index_lookups(self) -> int:
        return self._index_lookups
    
    def reset_stats(self) -> None:
        self._materialization_count = 0
        self._index_lookups = 0
        self._geometric_derivations = 0
        self._ingestion_count = 0
        self._extraction_count = 0
    
    def __repr__(self) -> str:
        return (f"ManifoldSubstrate(tokens={self.token_count}, "
                f"ingested={self.ingested_count}, "
                f"generative={self.generative_token_count})")
