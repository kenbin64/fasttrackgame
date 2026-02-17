"""
ButterflyFX Kernel Primitives
==============================

OPEN SOURCE - Licensed under CC BY 4.0
https://creativecommons.org/licenses/by/4.0/

Copyright (c) 2024-2026 Kenneth Bingham
Attribution required: Kenneth Bingham - https://butterflyfx.us

This is the mathematical kernel - the fundamental building blocks that
belong to all humanity. These primitives are:

1. TOO FUNDAMENTAL to charge for (like charging for numbers)
2. NECESSARY for the ecosystem to function
3. The FOUNDATION all paid packages build upon

Everything here is O(1) accessible, composable, and forms the
"index card" (SRL) for the entire system.

---

FREE KERNEL INCLUDES:
- Mathematical primitives (Scalar, Vector, Matrix)
- Basic color (RGB, RGBA)  
- Basic sound (Frequency, Amplitude)
- Temporal primitives (Duration, TimePoint)
- Base Substrate class
- SRL (Secure Resource Locator) - O(1) lookup
- Basic geometric primitives

PAID PACKAGES (subscription) build complex capabilities ON TOP of this kernel.
See helix/packages/ for available substrate packages.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable, Union
from enum import Enum, auto
from abc import ABC, abstractmethod
import math
import hashlib


# =============================================================================
# KERNEL PRIMITIVE TYPES
# =============================================================================

class PrimitiveType(Enum):
    """Categories of kernel primitives - all free"""
    MATHEMATICAL = auto()
    GEOMETRIC = auto()
    COLOR = auto()
    SOUND = auto()
    TEMPORAL = auto()
    SPATIAL = auto()
    DIMENSIONAL = auto()


@dataclass(frozen=True)
class KernelPrimitive:
    """Base primitive - the atomic unit of the kernel"""
    name: str
    primitive_type: PrimitiveType
    dimensions: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash((self.name, self.primitive_type, self.dimensions))


# =============================================================================
# MATHEMATICAL PRIMITIVES - The Numbers Behind Everything
# =============================================================================

@dataclass
class Scalar:
    """0D - A single value. The most fundamental unit."""
    value: float
    
    def __add__(self, other): 
        return Scalar(self.value + (other.value if isinstance(other, Scalar) else other))
    def __sub__(self, other):
        return Scalar(self.value - (other.value if isinstance(other, Scalar) else other))
    def __mul__(self, other): 
        return Scalar(self.value * (other.value if isinstance(other, Scalar) else other))
    def __truediv__(self, other): 
        return Scalar(self.value / (other.value if isinstance(other, Scalar) else other))
    def __neg__(self):
        return Scalar(-self.value)
    def __abs__(self):
        return Scalar(abs(self.value))
    def __float__(self):
        return self.value
    def __int__(self):
        return int(self.value)
    
    def clamp(self, min_v: float = 0, max_v: float = 1) -> 'Scalar':
        return Scalar(max(min_v, min(max_v, self.value)))
    
    def lerp(self, other: 'Scalar', t: float) -> 'Scalar':
        """Linear interpolation"""
        return Scalar(self.value + (other.value - self.value) * t)


@dataclass
class Vector2D:
    """2D vector - position, direction, force in 2D space"""
    x: float
    y: float
    
    @property
    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)
    
    @property
    def magnitude_squared(self) -> float:
        """Faster than magnitude when you don't need actual distance"""
        return self.x**2 + self.y**2
    
    @property
    def angle(self) -> float:
        """Angle in radians from positive x-axis"""
        return math.atan2(self.y, self.x)
    
    @property
    def angle_degrees(self) -> float:
        return math.degrees(self.angle)
    
    def normalize(self) -> 'Vector2D':
        m = self.magnitude
        return Vector2D(self.x/m, self.y/m) if m > 0 else Vector2D(0, 0)
    
    def dot(self, other: 'Vector2D') -> float:
        return self.x * other.x + self.y * other.y
    
    def cross(self, other: 'Vector2D') -> float:
        """2D cross product (scalar result)"""
        return self.x * other.y - self.y * other.x
    
    def rotate(self, angle: float) -> 'Vector2D':
        """Rotate by angle (radians)"""
        c, s = math.cos(angle), math.sin(angle)
        return Vector2D(self.x * c - self.y * s, self.x * s + self.y * c)
    
    def lerp(self, other: 'Vector2D', t: float) -> 'Vector2D':
        return Vector2D(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t
        )
    
    def __add__(self, other): return Vector2D(self.x + other.x, self.y + other.y)
    def __sub__(self, other): return Vector2D(self.x - other.x, self.y - other.y)
    def __mul__(self, s): return Vector2D(self.x * s, self.y * s)
    def __truediv__(self, s): return Vector2D(self.x / s, self.y / s)
    def __neg__(self): return Vector2D(-self.x, -self.y)
    
    @classmethod
    def from_angle(cls, angle: float, magnitude: float = 1.0) -> 'Vector2D':
        return cls(math.cos(angle) * magnitude, math.sin(angle) * magnitude)


@dataclass
class Vector3D:
    """3D vector - the workhorse of spatial computing"""
    x: float
    y: float
    z: float
    
    @property
    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    @property
    def magnitude_squared(self) -> float:
        return self.x**2 + self.y**2 + self.z**2
    
    @property
    def azimuth(self) -> float:
        """Horizontal angle (radians) - phi in spherical coords"""
        return math.atan2(self.y, self.x)
    
    @property
    def elevation(self) -> float:
        """Vertical angle (radians) - theta from z-axis"""
        m = self.magnitude
        return math.acos(self.z / m) if m > 0 else 0
    
    @property
    def xy(self) -> Vector2D:
        return Vector2D(self.x, self.y)
    
    @property
    def xz(self) -> Vector2D:
        return Vector2D(self.x, self.z)
    
    @property
    def yz(self) -> Vector2D:
        return Vector2D(self.y, self.z)
    
    def normalize(self) -> 'Vector3D':
        m = self.magnitude
        return Vector3D(self.x/m, self.y/m, self.z/m) if m > 0 else Vector3D(0, 0, 0)
    
    def cross(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def dot(self, other: 'Vector3D') -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def lerp(self, other: 'Vector3D', t: float) -> 'Vector3D':
        return Vector3D(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
            self.z + (other.z - self.z) * t
        )
    
    def reflect(self, normal: 'Vector3D') -> 'Vector3D':
        """Reflect vector off surface with given normal"""
        d = 2 * self.dot(normal)
        return Vector3D(self.x - d * normal.x, self.y - d * normal.y, self.z - d * normal.z)
    
    def __add__(self, other): return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
    def __sub__(self, other): return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
    def __mul__(self, s): return Vector3D(self.x * s, self.y * s, self.z * s)
    def __truediv__(self, s): return Vector3D(self.x / s, self.y / s, self.z / s)
    def __neg__(self): return Vector3D(-self.x, -self.y, -self.z)
    
    @classmethod
    def from_spherical(cls, r: float, theta: float, phi: float) -> 'Vector3D':
        """Create from spherical coordinates (r, theta=elevation, phi=azimuth)"""
        return cls(
            r * math.sin(theta) * math.cos(phi),
            r * math.sin(theta) * math.sin(phi),
            r * math.cos(theta)
        )


@dataclass
class Matrix3x3:
    """3x3 matrix for 2D transformations (homogeneous coordinates)"""
    data: List[List[float]] = field(default_factory=lambda: [[1,0,0],[0,1,0],[0,0,1]])
    
    @classmethod
    def identity(cls) -> 'Matrix3x3':
        return cls([[1,0,0],[0,1,0],[0,0,1]])
    
    @classmethod
    def rotation(cls, angle: float) -> 'Matrix3x3':
        c, s = math.cos(angle), math.sin(angle)
        return cls([[c,-s,0],[s,c,0],[0,0,1]])
    
    @classmethod
    def scale(cls, sx: float, sy: float) -> 'Matrix3x3':
        return cls([[sx,0,0],[0,sy,0],[0,0,1]])
    
    @classmethod
    def translation(cls, tx: float, ty: float) -> 'Matrix3x3':
        return cls([[1,0,tx],[0,1,ty],[0,0,1]])
    
    def transform(self, v: Vector2D) -> Vector2D:
        x = self.data[0][0]*v.x + self.data[0][1]*v.y + self.data[0][2]
        y = self.data[1][0]*v.x + self.data[1][1]*v.y + self.data[1][2]
        return Vector2D(x, y)
    
    def __mul__(self, other: 'Matrix3x3') -> 'Matrix3x3':
        """Matrix multiplication"""
        result = [[0,0,0],[0,0,0],[0,0,0]]
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    result[i][j] += self.data[i][k] * other.data[k][j]
        return Matrix3x3(result)


@dataclass
class Matrix4x4:
    """4x4 matrix for 3D transformations"""
    data: List[List[float]] = field(default_factory=lambda: [
        [1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]
    ])
    
    @classmethod
    def identity(cls) -> 'Matrix4x4':
        return cls([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
    
    @classmethod
    def rotation_x(cls, angle: float) -> 'Matrix4x4':
        c, s = math.cos(angle), math.sin(angle)
        return cls([[1,0,0,0],[0,c,-s,0],[0,s,c,0],[0,0,0,1]])
    
    @classmethod
    def rotation_y(cls, angle: float) -> 'Matrix4x4':
        c, s = math.cos(angle), math.sin(angle)
        return cls([[c,0,s,0],[0,1,0,0],[-s,0,c,0],[0,0,0,1]])
    
    @classmethod
    def rotation_z(cls, angle: float) -> 'Matrix4x4':
        c, s = math.cos(angle), math.sin(angle)
        return cls([[c,-s,0,0],[s,c,0,0],[0,0,1,0],[0,0,0,1]])
    
    @classmethod
    def scale(cls, sx: float, sy: float, sz: float) -> 'Matrix4x4':
        return cls([[sx,0,0,0],[0,sy,0,0],[0,0,sz,0],[0,0,0,1]])
    
    @classmethod
    def translation(cls, tx: float, ty: float, tz: float) -> 'Matrix4x4':
        return cls([[1,0,0,tx],[0,1,0,ty],[0,0,1,tz],[0,0,0,1]])
    
    @classmethod
    def perspective(cls, fov: float, aspect: float, near: float, far: float) -> 'Matrix4x4':
        f = 1.0 / math.tan(fov / 2)
        return cls([
            [f/aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far+near)/(near-far), (2*far*near)/(near-far)],
            [0, 0, -1, 0]
        ])
    
    @classmethod
    def look_at(cls, eye: Vector3D, target: Vector3D, up: Vector3D) -> 'Matrix4x4':
        """Create view matrix"""
        f = (target - eye).normalize()
        r = f.cross(up).normalize()
        u = r.cross(f)
        return cls([
            [r.x, r.y, r.z, -r.dot(eye)],
            [u.x, u.y, u.z, -u.dot(eye)],
            [-f.x, -f.y, -f.z, f.dot(eye)],
            [0, 0, 0, 1]
        ])
    
    def transform(self, v: Vector3D) -> Vector3D:
        d = self.data
        w = d[3][0]*v.x + d[3][1]*v.y + d[3][2]*v.z + d[3][3]
        w = w if w != 0 else 1
        return Vector3D(
            (d[0][0]*v.x + d[0][1]*v.y + d[0][2]*v.z + d[0][3]) / w,
            (d[1][0]*v.x + d[1][1]*v.y + d[1][2]*v.z + d[1][3]) / w,
            (d[2][0]*v.x + d[2][1]*v.y + d[2][2]*v.z + d[2][3]) / w
        )
    
    def __mul__(self, other: 'Matrix4x4') -> 'Matrix4x4':
        result = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    result[i][j] += self.data[i][k] * other.data[k][j]
        return Matrix4x4(result)


# =============================================================================
# COLOR PRIMITIVES - Basic Color Representation
# =============================================================================

@dataclass
class RGB:
    """RGB color (0-255) - the universal color primitive"""
    r: int
    g: int
    b: int
    
    @classmethod
    def from_wavelength(cls, wavelength_nm: float) -> 'RGB':
        """Convert visible light wavelength (380-700nm) to RGB
        
        This is physics - light wavelength to human-perceivable color.
        """
        wl = wavelength_nm
        if wl < 380 or wl > 700:
            return cls(0, 0, 0)
        
        if wl < 440:
            r, g, b = -(wl-440)/(440-380), 0, 1
        elif wl < 490:
            r, g, b = 0, (wl-440)/(490-440), 1
        elif wl < 510:
            r, g, b = 0, 1, -(wl-510)/(510-490)
        elif wl < 580:
            r, g, b = (wl-510)/(580-510), 1, 0
        elif wl < 645:
            r, g, b = 1, -(wl-645)/(645-580), 0
        else:
            r, g, b = 1, 0, 0
        
        # Intensity correction at spectrum edges
        if wl < 420:
            factor = 0.3 + 0.7 * (wl - 380) / (420 - 380)
        elif wl > 645:
            factor = 0.3 + 0.7 * (700 - wl) / (700 - 645)
        else:
            factor = 1.0
        
        return cls(
            int(max(0, min(255, r * factor * 255))),
            int(max(0, min(255, g * factor * 255))),
            int(max(0, min(255, b * factor * 255)))
        )
    
    @classmethod
    def from_hsv(cls, h: float, s: float, v: float) -> 'RGB':
        """Convert HSV (h: 0-360, s: 0-1, v: 0-1) to RGB"""
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        
        if h < 60: r, g, b = c, x, 0
        elif h < 120: r, g, b = x, c, 0
        elif h < 180: r, g, b = 0, c, x
        elif h < 240: r, g, b = 0, x, c
        elif h < 300: r, g, b = x, 0, c
        else: r, g, b = c, 0, x
        
        return cls(int((r+m)*255), int((g+m)*255), int((b+m)*255))
    
    @classmethod
    def from_hex(cls, hex_str: str) -> 'RGB':
        """Parse hex color string"""
        h = hex_str.lstrip('#')
        return cls(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    
    @property
    def hex(self) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"
    
    @property
    def css(self) -> str:
        return f"rgb({self.r}, {self.g}, {self.b})"
    
    @property
    def hsv(self) -> Tuple[float, float, float]:
        r, g, b = self.r/255, self.g/255, self.b/255
        mx, mn = max(r,g,b), min(r,g,b)
        d = mx - mn
        v = mx
        s = 0 if mx == 0 else d/mx
        if d == 0: h = 0
        elif mx == r: h = 60 * ((g-b)/d % 6)
        elif mx == g: h = 60 * ((b-r)/d + 2)
        else: h = 60 * ((r-g)/d + 4)
        return (h, s, v)
    
    @property
    def luminance(self) -> float:
        """Perceived brightness (0-1)"""
        return (0.299 * self.r + 0.587 * self.g + 0.114 * self.b) / 255
    
    def blend(self, other: 'RGB', t: float) -> 'RGB':
        """Linear interpolation between colors"""
        return RGB(
            int(self.r + (other.r - self.r) * t),
            int(self.g + (other.g - self.g) * t),
            int(self.b + (other.b - self.b) * t)
        )
    
    def __eq__(self, other):
        if isinstance(other, RGB):
            return self.r == other.r and self.g == other.g and self.b == other.b
        return False


@dataclass
class RGBA(RGB):
    """RGBA color with alpha channel"""
    a: float = 1.0  # 0-1
    
    @property
    def hex(self) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}{int(self.a*255):02x}"
    
    @property
    def css(self) -> str:
        return f"rgba({self.r}, {self.g}, {self.b}, {self.a})"
    
    def composite(self, background: RGB) -> RGB:
        """Alpha composite over background"""
        return RGB(
            int(self.r * self.a + background.r * (1 - self.a)),
            int(self.g * self.a + background.g * (1 - self.a)),
            int(self.b * self.a + background.b * (1 - self.a))
        )
    
    def premultiply(self) -> 'RGBA':
        """Premultiply alpha"""
        return RGBA(
            int(self.r * self.a),
            int(self.g * self.a),
            int(self.b * self.a),
            self.a
        )


# =============================================================================
# SOUND PRIMITIVES - Basic Audio Representation
# =============================================================================

@dataclass
class Frequency:
    """Sound frequency - the fundamental unit of audio"""
    hz: float
    
    SPEED_OF_SOUND = 343.0  # m/s at 20°C in air
    
    @property
    def wavelength(self) -> float:
        """Wavelength in meters"""
        return self.SPEED_OF_SOUND / self.hz if self.hz > 0 else float('inf')
    
    @property
    def period(self) -> float:
        """Period in seconds"""
        return 1.0 / self.hz if self.hz > 0 else float('inf')
    
    @property
    def angular(self) -> float:
        """Angular frequency (radians/second)"""
        return 2 * math.pi * self.hz
    
    @property
    def midi_note(self) -> int:
        """Convert to MIDI note number (0-127)"""
        if self.hz <= 0:
            return 0
        return int(round(69 + 12 * math.log2(self.hz / 440)))
    
    @property
    def note_name(self) -> str:
        """Get musical note name with octave"""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        midi = self.midi_note
        octave = (midi // 12) - 1
        note = notes[midi % 12]
        return f"{note}{octave}"
    
    @classmethod
    def from_midi(cls, midi_note: int) -> 'Frequency':
        """Create from MIDI note number"""
        return cls(440 * (2 ** ((midi_note - 69) / 12)))
    
    @classmethod
    def from_note(cls, note: str, octave: int) -> 'Frequency':
        """Create from note name and octave (e.g., 'C', 4 for middle C)"""
        notes = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
                 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
                 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
        midi = (octave + 1) * 12 + notes.get(note, 0)
        return cls.from_midi(midi)
    
    def harmonic(self, n: int) -> 'Frequency':
        """Get nth harmonic (n=1 is fundamental)"""
        return Frequency(self.hz * n)
    
    def interval(self, semitones: int) -> 'Frequency':
        """Transpose by semitones"""
        return Frequency(self.hz * (2 ** (semitones / 12)))
    
    def __add__(self, other: 'Frequency') -> 'Frequency':
        return Frequency(self.hz + other.hz)
    
    def __mul__(self, factor: float) -> 'Frequency':
        return Frequency(self.hz * factor)


@dataclass
class Amplitude:
    """Sound amplitude - loudness/volume"""
    level: float  # 0-1 linear scale
    
    REFERENCE_DB = -60  # dB for level=0
    
    @property
    def db(self) -> float:
        """Convert to decibels"""
        return 20 * math.log10(self.level) if self.level > 0 else self.REFERENCE_DB
    
    @classmethod
    def from_db(cls, db: float) -> 'Amplitude':
        """Create from decibels"""
        return cls(10 ** (db / 20))
    
    def __mul__(self, factor: float) -> 'Amplitude':
        return Amplitude(max(0, min(1, self.level * factor)))
    
    def fade(self, target: 'Amplitude', t: float) -> 'Amplitude':
        """Fade to target amplitude"""
        return Amplitude(self.level + (target.level - self.level) * t)


# =============================================================================
# TEMPORAL PRIMITIVES - Time Handling
# =============================================================================

@dataclass
class Duration:
    """Time duration - interval of time"""
    seconds: float
    
    @property
    def milliseconds(self) -> float:
        return self.seconds * 1000
    
    @property
    def microseconds(self) -> float:
        return self.seconds * 1_000_000
    
    def frames(self, fps: float = 60) -> float:
        """Get frame count at given FPS"""
        return self.seconds * fps
    
    def beats(self, bpm: float = 120) -> float:
        """Get beat count at given BPM"""
        return self.seconds * bpm / 60
    
    def samples(self, sample_rate: int = 44100) -> int:
        """Get sample count at given sample rate"""
        return int(self.seconds * sample_rate)
    
    @classmethod
    def from_frames(cls, frames: int, fps: float = 60) -> 'Duration':
        return cls(frames / fps)
    
    @classmethod
    def from_beats(cls, beats: float, bpm: float = 120) -> 'Duration':
        return cls(beats * 60 / bpm)
    
    @classmethod
    def from_samples(cls, samples: int, sample_rate: int = 44100) -> 'Duration':
        return cls(samples / sample_rate)
    
    def __add__(self, other: 'Duration') -> 'Duration':
        return Duration(self.seconds + other.seconds)
    
    def __sub__(self, other: 'Duration') -> 'Duration':
        return Duration(self.seconds - other.seconds)
    
    def __mul__(self, factor: float) -> 'Duration':
        return Duration(self.seconds * factor)


@dataclass
class TimePoint:
    """Point in time - absolute position in timeline"""
    t: float  # seconds from origin
    
    def __add__(self, d: Duration) -> 'TimePoint':
        return TimePoint(self.t + d.seconds)
    
    def __sub__(self, other: Union['TimePoint', Duration]) -> Union['TimePoint', Duration]:
        if isinstance(other, TimePoint):
            return Duration(self.t - other.t)
        return TimePoint(self.t - other.seconds)
    
    def __lt__(self, other: 'TimePoint') -> bool:
        return self.t < other.t
    
    def __le__(self, other: 'TimePoint') -> bool:
        return self.t <= other.t


# =============================================================================
# SUBSTRATE BASE CLASS - Foundation for All Substrates
# =============================================================================

class Substrate(ABC):
    """
    Base class for all substrates - both free kernel and paid packages.
    
    A substrate is a domain-specific collection of primitives and operations
    that can be composed with other substrates.
    """
    
    def __init__(self, name: str):
        self.name = name
        self._primitives: Dict[str, Any] = {}
        self._operations: Dict[str, Callable] = {}
        self._sub_substrates: Dict[str, 'Substrate'] = {}
    
    @property
    @abstractmethod
    def domain(self) -> str:
        """Domain identifier for this substrate (e.g., 'graphics.color')"""
        pass
    
    @property
    def is_licensed(self) -> bool:
        """Override in paid packages to check license"""
        return True  # Kernel primitives are always licensed (free)
    
    def register_primitive(self, name: str, primitive: Any) -> None:
        """Add a primitive to this substrate"""
        self._primitives[name] = primitive
    
    def register_operation(self, name: str, op: Callable) -> None:
        """Add an operation to this substrate"""
        self._operations[name] = op
    
    def add_sub_substrate(self, substrate: 'Substrate') -> None:
        """Add a sub-substrate for composition"""
        self._sub_substrates[substrate.name] = substrate
    
    def get(self, path: str) -> Any:
        """O(1) lookup by path (e.g., 'color.rgb' or 'transform')"""
        parts = path.split('.')
        if len(parts) == 1:
            return self._primitives.get(path) or self._operations.get(path)
        else:
            sub = self._sub_substrates.get(parts[0])
            return sub.get('.'.join(parts[1:])) if sub else None
    
    def invoke(self, op_name: str, *args, **kwargs) -> Any:
        """Invoke an operation by name"""
        op = self._operations.get(op_name)
        if op:
            return op(*args, **kwargs)
        raise ValueError(f"Unknown operation: {op_name}")
    
    def srl_address(self) -> str:
        """Generate SRL address for this substrate"""
        return f"srl://{self.domain}/{self.name}"


# =============================================================================
# SECURE RESOURCE LOCATOR (SRL) - O(1) Lookup System
# =============================================================================

class SecureResourceLocator:
    """
    SRL - The Index Card for Everything
    
    O(1) lookup for any primitive, operation, or substrate in the system.
    This is the "library card catalog" that makes dimensional computing work.
    
    Address format: srl://domain/substrate/resource
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._registry: Dict[str, Any] = {}
            cls._instance._substrates: Dict[str, Substrate] = {}
            cls._instance._hash_index: Dict[str, str] = {}
        return cls._instance
    
    def register(self, substrate: Substrate) -> str:
        """Register a substrate and index all its contents"""
        address = substrate.srl_address()
        self._substrates[address] = substrate
        self._registry[address] = substrate
        
        # Index all primitives
        for name, primitive in substrate._primitives.items():
            prim_addr = f"{address}/{name}"
            self._registry[prim_addr] = primitive
            self._hash_index[self._hash(prim_addr)] = prim_addr
        
        # Index all operations
        for name, op in substrate._operations.items():
            op_addr = f"{address}/{name}"
            self._registry[op_addr] = op
            self._hash_index[self._hash(op_addr)] = op_addr
        
        # Recursively register sub-substrates
        for sub in substrate._sub_substrates.values():
            self.register(sub)
        
        return address
    
    def _hash(self, address: str) -> str:
        """Generate hash for O(1) lookup"""
        return hashlib.sha256(address.encode()).hexdigest()[:16]
    
    def get(self, address: str) -> Any:
        """O(1) lookup by SRL address"""
        if address in self._registry:
            return self._registry[address]
        
        addr_hash = self._hash(address)
        if addr_hash in self._hash_index:
            return self._registry.get(self._hash_index[addr_hash])
        
        return None
    
    def invoke(self, address: str, *args, **kwargs) -> Any:
        """O(1) invoke operation by address"""
        op = self.get(address)
        if callable(op):
            return op(*args, **kwargs)
        raise ValueError(f"Not callable: {address}")
    
    def find(self, pattern: str) -> List[str]:
        """Find addresses matching pattern"""
        import re
        regex = re.compile(pattern, re.IGNORECASE)
        return [addr for addr in self._registry.keys() if regex.search(addr)]
    
    def list_substrates(self) -> List[str]:
        """List all registered substrate addresses"""
        return list(self._substrates.keys())


# =============================================================================
# GLOBAL INSTANCES
# =============================================================================

# Global SRL instance
SRL = SecureResourceLocator()


# Convenience functions
def srl(address: str) -> Any:
    """O(1) lookup via global SRL"""
    return SRL.get(address)


def invoke(address: str, *args, **kwargs) -> Any:
    """O(1) invoke via global SRL"""
    return SRL.invoke(address, *args, **kwargs)


# =============================================================================
# EXPORTS - Everything here is FREE and open source
# =============================================================================

__all__ = [
    # Type enums
    'PrimitiveType',
    'KernelPrimitive',
    
    # Mathematical primitives
    'Scalar',
    'Vector2D',
    'Vector3D',
    'Matrix3x3',
    'Matrix4x4',
    
    # Color primitives
    'RGB',
    'RGBA',
    
    # Sound primitives
    'Frequency',
    'Amplitude',
    
    # Temporal primitives
    'Duration',
    'TimePoint',
    
    # Substrate system
    'Substrate',
    'SecureResourceLocator',
    'SRL',
    'srl',
    'invoke',
]
