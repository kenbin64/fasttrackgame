"""
ButterflyFX Substrate Architecture
===================================

The substrate system provides composable building blocks for all domains:
- Graphics, Physics, Text, Audio, Theory, Patterns, and more

Architecture:
- KERNEL: Core primitives shared by all substrates (math, geometry, color, sound)
- SUBSTRATES: Domain-specific primitives that inherit from kernel
- SRL: Secure Resource Locator - O(1) lookup for any primitive in the system

This is the Butterfly Effect: small primitives combine to create complex effects,
all accessible via O(1) lookup through SRL.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable, Union, TYPE_CHECKING
from enum import Enum, auto
from abc import ABC, abstractmethod
import math
import hashlib

# =============================================================================
# KERNEL - Core Primitives Shared By All Substrates
# =============================================================================

class PrimitiveType(Enum):
    """Categories of kernel primitives"""
    MATHEMATICAL = auto()
    GEOMETRIC = auto()
    COLOR = auto()
    SOUND = auto()
    TEMPORAL = auto()
    SPATIAL = auto()
    DIMENSIONAL = auto()


@dataclass(frozen=True)
class KernelPrimitive:
    """Base primitive that all substrates can use"""
    name: str
    primitive_type: PrimitiveType
    dimensions: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash((self.name, self.primitive_type, self.dimensions))


# --- Mathematical Primitives ---

@dataclass
class Scalar:
    """0D - A single value"""
    value: float
    
    def __add__(self, other): return Scalar(self.value + (other.value if isinstance(other, Scalar) else other))
    def __mul__(self, other): return Scalar(self.value * (other.value if isinstance(other, Scalar) else other))
    def __truediv__(self, other): return Scalar(self.value / (other.value if isinstance(other, Scalar) else other))
    def normalize(self, min_v: float = 0, max_v: float = 1) -> float:
        return max(min_v, min(max_v, self.value))


@dataclass
class Vector2D:
    """2D vector primitive"""
    x: float
    y: float
    
    @property
    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)
    
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
    
    def __add__(self, other): return Vector2D(self.x + other.x, self.y + other.y)
    def __sub__(self, other): return Vector2D(self.x - other.x, self.y - other.y)
    def __mul__(self, s): return Vector2D(self.x * s, self.y * s)


@dataclass
class Vector3D:
    """3D vector primitive"""
    x: float
    y: float
    z: float
    
    @property
    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    @property
    def azimuth(self) -> float:
        """Horizontal angle (radians)"""
        return math.atan2(self.y, self.x)
    
    @property
    def elevation(self) -> float:
        """Vertical angle (radians)"""
        m = self.magnitude
        return math.asin(self.z / m) if m > 0 else 0
    
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
    
    def __add__(self, other): return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
    def __sub__(self, other): return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
    def __mul__(self, s): return Vector3D(self.x * s, self.y * s, self.z * s)


@dataclass
class Matrix3x3:
    """3x3 matrix for 2D transformations"""
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
    
    def transform(self, v: Vector3D) -> Vector3D:
        d = self.data
        w = d[3][0]*v.x + d[3][1]*v.y + d[3][2]*v.z + d[3][3]
        w = w if w != 0 else 1
        return Vector3D(
            (d[0][0]*v.x + d[0][1]*v.y + d[0][2]*v.z + d[0][3]) / w,
            (d[1][0]*v.x + d[1][1]*v.y + d[1][2]*v.z + d[1][3]) / w,
            (d[2][0]*v.x + d[2][1]*v.y + d[2][2]*v.z + d[2][3]) / w
        )


# --- Color Primitives ---

@dataclass
class RGB:
    """RGB color (0-255)"""
    r: int
    g: int
    b: int
    
    @classmethod
    def from_wavelength(cls, wavelength_nm: float) -> 'RGB':
        """Convert wavelength (380-700nm) to RGB"""
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
    
    @property
    def hex(self) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"
    
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
    
    def blend(self, other: 'RGB', t: float) -> 'RGB':
        """Linear interpolation between colors"""
        return RGB(
            int(self.r + (other.r - self.r) * t),
            int(self.g + (other.g - self.g) * t),
            int(self.b + (other.b - self.b) * t)
        )


@dataclass
class RGBA(RGB):
    """RGBA color with alpha"""
    a: float = 1.0  # 0-1
    
    @property
    def hex(self) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}{int(self.a*255):02x}"
    
    def composite(self, background: 'RGB') -> RGB:
        """Alpha composite over background"""
        return RGB(
            int(self.r * self.a + background.r * (1 - self.a)),
            int(self.g * self.a + background.g * (1 - self.a)),
            int(self.b * self.a + background.b * (1 - self.a))
        )


# --- Sound Primitives ---

@dataclass
class Frequency:
    """Sound frequency primitive"""
    hz: float
    
    SPEED_OF_SOUND = 343.0  # m/s at 20°C
    
    @property
    def wavelength(self) -> float:
        """Wavelength in meters"""
        return self.SPEED_OF_SOUND / self.hz if self.hz > 0 else float('inf')
    
    @property
    def period(self) -> float:
        """Period in seconds"""
        return 1.0 / self.hz if self.hz > 0 else float('inf')
    
    @property
    def midi_note(self) -> int:
        """Convert to MIDI note number"""
        if self.hz <= 0:
            return 0
        return int(round(69 + 12 * math.log2(self.hz / 440)))
    
    @property
    def note_name(self) -> str:
        """Get musical note name"""
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
        """Create from note name and octave"""
        notes = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
                 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
                 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
        midi = (octave + 1) * 12 + notes.get(note, 0)
        return cls.from_midi(midi)
    
    def harmonic(self, n: int) -> 'Frequency':
        """Get nth harmonic"""
        return Frequency(self.hz * n)
    
    def interval(self, semitones: int) -> 'Frequency':
        """Transpose by semitones"""
        return Frequency(self.hz * (2 ** (semitones / 12)))


@dataclass
class Amplitude:
    """Sound amplitude primitive"""
    level: float  # 0-1 linear
    
    @property
    def db(self) -> float:
        """Convert to decibels"""
        return 20 * math.log10(self.level) if self.level > 0 else -float('inf')
    
    @classmethod
    def from_db(cls, db: float) -> 'Amplitude':
        return cls(10 ** (db / 20))


@dataclass
class Waveform:
    """Waveform primitive"""
    wave_type: str  # 'sine', 'square', 'triangle', 'sawtooth'
    frequency: Frequency
    amplitude: Amplitude = field(default_factory=lambda: Amplitude(1.0))
    phase: float = 0.0  # radians
    
    def sample(self, t: float) -> float:
        """Sample waveform at time t (seconds)"""
        theta = 2 * math.pi * self.frequency.hz * t + self.phase
        
        if self.wave_type == 'sine':
            return self.amplitude.level * math.sin(theta)
        elif self.wave_type == 'square':
            return self.amplitude.level * (1 if math.sin(theta) >= 0 else -1)
        elif self.wave_type == 'triangle':
            return self.amplitude.level * (2 * abs(2 * (theta/(2*math.pi) % 1) - 1) - 1)
        elif self.wave_type == 'sawtooth':
            return self.amplitude.level * (2 * (theta/(2*math.pi) % 1) - 1)
        return 0


# --- Temporal Primitives ---

@dataclass
class Duration:
    """Time duration primitive"""
    seconds: float
    
    @property
    def milliseconds(self) -> float:
        return self.seconds * 1000
    
    @property
    def frames(self, fps: float = 60) -> float:
        return self.seconds * fps
    
    @classmethod
    def from_frames(cls, frames: int, fps: float = 60) -> 'Duration':
        return cls(frames / fps)
    
    @classmethod
    def from_beats(cls, beats: float, bpm: float = 120) -> 'Duration':
        return cls(beats * 60 / bpm)


@dataclass
class TimePoint:
    """Point in time primitive"""
    t: float  # seconds from origin
    
    def __add__(self, d: Duration) -> 'TimePoint':
        return TimePoint(self.t + d.seconds)
    
    def __sub__(self, other: 'TimePoint') -> Duration:
        return Duration(self.t - other.t)


# =============================================================================
# SUBSTRATE BASE - All substrates inherit from this
# =============================================================================

class Substrate(ABC):
    """Base class for all substrates"""
    
    def __init__(self, name: str):
        self.name = name
        self._primitives: Dict[str, Any] = {}
        self._operations: Dict[str, Callable] = {}
        self._sub_substrates: Dict[str, 'Substrate'] = {}
    
    @property
    @abstractmethod
    def domain(self) -> str:
        """Domain identifier for this substrate"""
        pass
    
    def register_primitive(self, name: str, primitive: Any) -> None:
        """Add a primitive to this substrate"""
        self._primitives[name] = primitive
    
    def register_operation(self, name: str, op: Callable) -> None:
        """Add an operation to this substrate"""
        self._operations[name] = op
    
    def add_sub_substrate(self, substrate: 'Substrate') -> None:
        """Add a sub-substrate"""
        self._sub_substrates[substrate.name] = substrate
    
    def get(self, path: str) -> Any:
        """O(1) lookup by path"""
        parts = path.split('.')
        if len(parts) == 1:
            return self._primitives.get(path) or self._operations.get(path)
        else:
            sub = self._sub_substrates.get(parts[0])
            return sub.get('.'.join(parts[1:])) if sub else None
    
    def invoke(self, op_name: str, *args, **kwargs) -> Any:
        """Invoke an operation"""
        op = self._operations.get(op_name)
        if op:
            return op(*args, **kwargs)
        raise ValueError(f"Operation {op_name} not found in {self.name}")
    
    def srl_address(self) -> str:
        """Generate SRL address for this substrate"""
        return f"srl://{self.domain}/{self.name}"


# =============================================================================
# GRAPHICS SUBSTRATES
# =============================================================================

class PixelSubstrate(Substrate):
    """Pixel-level graphics operations"""
    
    def __init__(self):
        super().__init__("pixel")
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "graphics.pixel"
    
    def _init_primitives(self):
        self.register_primitive("point", Vector2D)
        self.register_primitive("rgb", RGB)
        self.register_primitive("rgba", RGBA)
        self.register_operation("blend", self.blend)
        self.register_operation("sample", self.sample)
    
    def blend(self, c1: RGBA, c2: RGBA, mode: str = "normal") -> RGBA:
        """Blend two pixels with various modes"""
        if mode == "normal":
            # Alpha composite
            a_out = c1.a + c2.a * (1 - c1.a)
            if a_out == 0:
                return RGBA(0, 0, 0, 0)
            r = (c1.r * c1.a + c2.r * c2.a * (1 - c1.a)) / a_out
            g = (c1.g * c1.a + c2.g * c2.a * (1 - c1.a)) / a_out
            b = (c1.b * c1.a + c2.b * c2.a * (1 - c1.a)) / a_out
            return RGBA(int(r), int(g), int(b), a_out)
        elif mode == "multiply":
            return RGBA(c1.r*c2.r//255, c1.g*c2.g//255, c1.b*c2.b//255, c1.a*c2.a)
        elif mode == "screen":
            return RGBA(255-(255-c1.r)*(255-c2.r)//255,
                       255-(255-c1.g)*(255-c2.g)//255,
                       255-(255-c1.b)*(255-c2.b)//255, c1.a)
        elif mode == "overlay":
            def ov(a, b):
                return (2*a*b//255) if a < 128 else (255 - 2*(255-a)*(255-b)//255)
            return RGBA(ov(c1.r, c2.r), ov(c1.g, c2.g), ov(c1.b, c2.b), c1.a)
        return c1
    
    def sample(self, x: float, y: float, texture: List[List[RGBA]]) -> RGBA:
        """Bilinear sample from texture"""
        h, w = len(texture), len(texture[0]) if texture else 0
        if w == 0 or h == 0:
            return RGBA(0, 0, 0, 0)
        
        x = x * (w - 1)
        y = y * (h - 1)
        x0, y0 = int(x), int(y)
        x1, y1 = min(x0 + 1, w - 1), min(y0 + 1, h - 1)
        fx, fy = x - x0, y - y0
        
        c00 = texture[y0][x0]
        c10 = texture[y0][x1]
        c01 = texture[y1][x0]
        c11 = texture[y1][x1]
        
        # Bilinear interpolation
        r = c00.r*(1-fx)*(1-fy) + c10.r*fx*(1-fy) + c01.r*(1-fx)*fy + c11.r*fx*fy
        g = c00.g*(1-fx)*(1-fy) + c10.g*fx*(1-fy) + c01.g*(1-fx)*fy + c11.g*fx*fy
        b = c00.b*(1-fx)*(1-fy) + c10.b*fx*(1-fy) + c01.b*(1-fx)*fy + c11.b*fx*fy
        a = c00.a*(1-fx)*(1-fy) + c10.a*fx*(1-fy) + c01.a*(1-fx)*fy + c11.a*fx*fy
        
        return RGBA(int(r), int(g), int(b), a)


class ColorSubstrate(Substrate):
    """Color theory operations"""
    
    def __init__(self):
        super().__init__("color")
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "graphics.color"
    
    def _init_primitives(self):
        self.register_primitive("rgb", RGB)
        self.register_primitive("rgba", RGBA)
        self.register_operation("wavelength_to_rgb", RGB.from_wavelength)
        self.register_operation("hsv_to_rgb", RGB.from_hsv)
        self.register_operation("complement", self.complement)
        self.register_operation("triadic", self.triadic)
        self.register_operation("analogous", self.analogous)
        self.register_operation("gradient", self.gradient)
    
    def complement(self, color: RGB) -> RGB:
        """Get complementary color"""
        h, s, v = color.hsv
        return RGB.from_hsv((h + 180) % 360, s, v)
    
    def triadic(self, color: RGB) -> Tuple[RGB, RGB]:
        """Get triadic colors"""
        h, s, v = color.hsv
        return (RGB.from_hsv((h + 120) % 360, s, v),
                RGB.from_hsv((h + 240) % 360, s, v))
    
    def analogous(self, color: RGB, angle: float = 30) -> Tuple[RGB, RGB]:
        """Get analogous colors"""
        h, s, v = color.hsv
        return (RGB.from_hsv((h + angle) % 360, s, v),
                RGB.from_hsv((h - angle) % 360, s, v))
    
    def gradient(self, c1: RGB, c2: RGB, steps: int = 10) -> List[RGB]:
        """Generate gradient between two colors"""
        return [c1.blend(c2, i / (steps - 1)) for i in range(steps)]


@dataclass
class GradientStop:
    """A stop in a gradient"""
    position: float  # 0-1
    color: RGBA


class GradientSubstrate(Substrate):
    """Gradient operations"""
    
    def __init__(self):
        super().__init__("gradient")
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "graphics.gradient"
    
    def _init_primitives(self):
        self.register_primitive("stop", GradientStop)
        self.register_operation("linear", self.linear)
        self.register_operation("radial", self.radial)
        self.register_operation("angular", self.angular)
    
    def linear(self, stops: List[GradientStop], t: float) -> RGBA:
        """Sample linear gradient at position t (0-1)"""
        if not stops:
            return RGBA(0, 0, 0, 0)
        if len(stops) == 1:
            return stops[0].color
        
        stops = sorted(stops, key=lambda s: s.position)
        
        if t <= stops[0].position:
            return stops[0].color
        if t >= stops[-1].position:
            return stops[-1].color
        
        for i in range(len(stops) - 1):
            if stops[i].position <= t <= stops[i+1].position:
                local_t = (t - stops[i].position) / (stops[i+1].position - stops[i].position)
                c1, c2 = stops[i].color, stops[i+1].color
                return RGBA(
                    int(c1.r + (c2.r - c1.r) * local_t),
                    int(c1.g + (c2.g - c1.g) * local_t),
                    int(c1.b + (c2.b - c1.b) * local_t),
                    c1.a + (c2.a - c1.a) * local_t
                )
        return stops[-1].color
    
    def radial(self, stops: List[GradientStop], x: float, y: float,
               cx: float = 0.5, cy: float = 0.5, radius: float = 0.5) -> RGBA:
        """Sample radial gradient"""
        dist = math.sqrt((x - cx)**2 + (y - cy)**2) / radius
        return self.linear(stops, min(1, dist))
    
    def angular(self, stops: List[GradientStop], x: float, y: float,
                cx: float = 0.5, cy: float = 0.5) -> RGBA:
        """Sample angular/conic gradient"""
        angle = (math.atan2(y - cy, x - cx) + math.pi) / (2 * math.pi)
        return self.linear(stops, angle)


class ShaderSubstrate(Substrate):
    """Shader-like operations"""
    
    def __init__(self):
        super().__init__("shader")
        # Compose with other substrates
        self.add_sub_substrate(PixelSubstrate())
        self.add_sub_substrate(ColorSubstrate())
        self.add_sub_substrate(GradientSubstrate())
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "graphics.shader"
    
    def _init_primitives(self):
        self.register_operation("fragment", self.fragment)
        self.register_operation("vertex", self.vertex)
    
    def fragment(self, uv: Vector2D, time: float, 
                 shader_func: Callable[[Vector2D, float], RGBA]) -> RGBA:
        """Execute fragment shader function"""
        return shader_func(uv, time)
    
    def vertex(self, position: Vector3D, transform: Matrix4x4) -> Vector3D:
        """Execute vertex transformation"""
        return transform.transform(position)


# --- 3D Graphics Substrate ---

@dataclass
class Vertex:
    """3D vertex with attributes"""
    position: Vector3D
    normal: Optional[Vector3D] = None
    uv: Optional[Vector2D] = None
    color: Optional[RGBA] = None


@dataclass
class Edge:
    """Edge between two vertices"""
    v0: int  # vertex index
    v1: int
    
    def length(self, vertices: List[Vertex]) -> float:
        p0, p1 = vertices[self.v0].position, vertices[self.v1].position
        return (p1 - p0).magnitude


@dataclass
class Triangle:
    """Triangle face (3 vertex indices)"""
    v0: int
    v1: int
    v2: int
    
    def normal(self, vertices: List[Vertex]) -> Vector3D:
        """Compute face normal"""
        p0 = vertices[self.v0].position
        p1 = vertices[self.v1].position
        p2 = vertices[self.v2].position
        e1 = p1 - p0
        e2 = p2 - p0
        return e1.cross(e2).normalize()
    
    def area(self, vertices: List[Vertex]) -> float:
        """Compute triangle area"""
        p0 = vertices[self.v0].position
        p1 = vertices[self.v1].position
        p2 = vertices[self.v2].position
        return (p1 - p0).cross(p2 - p0).magnitude / 2


@dataclass
class Mesh:
    """3D mesh composed of vertices and faces"""
    vertices: List[Vertex] = field(default_factory=list)
    triangles: List[Triangle] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    
    def compute_edges(self) -> None:
        """Compute edge list from triangles"""
        edge_set = set()
        for tri in self.triangles:
            for e in [(tri.v0, tri.v1), (tri.v1, tri.v2), (tri.v2, tri.v0)]:
                edge = tuple(sorted(e))
                edge_set.add(edge)
        self.edges = [Edge(e[0], e[1]) for e in edge_set]
    
    def compute_vertex_normals(self) -> None:
        """Compute smooth vertex normals"""
        normal_sum = [Vector3D(0, 0, 0) for _ in self.vertices]
        for tri in self.triangles:
            n = tri.normal(self.vertices)
            normal_sum[tri.v0] = normal_sum[tri.v0] + n
            normal_sum[tri.v1] = normal_sum[tri.v1] + n
            normal_sum[tri.v2] = normal_sum[tri.v2] + n
        for i, v in enumerate(self.vertices):
            v.normal = normal_sum[i].normalize()


class Graphics3DSubstrate(Substrate):
    """3D graphics with edges, vertices, polygons"""
    
    def __init__(self):
        super().__init__("graphics3d")
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "graphics.3d"
    
    def _init_primitives(self):
        self.register_primitive("vertex", Vertex)
        self.register_primitive("edge", Edge)
        self.register_primitive("triangle", Triangle)
        self.register_primitive("mesh", Mesh)
        self.register_primitive("transform", Matrix4x4)
        self.register_operation("cube", self.create_cube)
        self.register_operation("sphere", self.create_sphere)
        self.register_operation("plane", self.create_plane)
    
    def create_cube(self, size: float = 1.0) -> Mesh:
        """Create a unit cube mesh"""
        s = size / 2
        vertices = [
            Vertex(Vector3D(-s, -s, -s)), Vertex(Vector3D(s, -s, -s)),
            Vertex(Vector3D(s, s, -s)), Vertex(Vector3D(-s, s, -s)),
            Vertex(Vector3D(-s, -s, s)), Vertex(Vector3D(s, -s, s)),
            Vertex(Vector3D(s, s, s)), Vertex(Vector3D(-s, s, s)),
        ]
        triangles = [
            Triangle(0,2,1), Triangle(0,3,2),  # back
            Triangle(4,5,6), Triangle(4,6,7),  # front
            Triangle(0,1,5), Triangle(0,5,4),  # bottom
            Triangle(2,3,7), Triangle(2,7,6),  # top
            Triangle(0,4,7), Triangle(0,7,3),  # left
            Triangle(1,2,6), Triangle(1,6,5),  # right
        ]
        mesh = Mesh(vertices, triangles)
        mesh.compute_edges()
        mesh.compute_vertex_normals()
        return mesh
    
    def create_sphere(self, radius: float = 1.0, segments: int = 16) -> Mesh:
        """Create a UV sphere"""
        vertices = []
        triangles = []
        
        for i in range(segments + 1):
            theta = math.pi * i / segments
            for j in range(segments):
                phi = 2 * math.pi * j / segments
                x = radius * math.sin(theta) * math.cos(phi)
                y = radius * math.sin(theta) * math.sin(phi)
                z = radius * math.cos(theta)
                vertices.append(Vertex(Vector3D(x, y, z)))
        
        for i in range(segments):
            for j in range(segments):
                v0 = i * segments + j
                v1 = i * segments + (j + 1) % segments
                v2 = (i + 1) * segments + j
                v3 = (i + 1) * segments + (j + 1) % segments
                triangles.append(Triangle(v0, v1, v2))
                triangles.append(Triangle(v1, v3, v2))
        
        mesh = Mesh(vertices, triangles)
        mesh.compute_edges()
        mesh.compute_vertex_normals()
        return mesh
    
    def create_plane(self, width: float = 1.0, height: float = 1.0,
                     segments_x: int = 1, segments_y: int = 1) -> Mesh:
        """Create a plane mesh"""
        vertices = []
        triangles = []
        
        for i in range(segments_y + 1):
            for j in range(segments_x + 1):
                x = (j / segments_x - 0.5) * width
                z = (i / segments_y - 0.5) * height
                vertices.append(Vertex(Vector3D(x, 0, z), Vector3D(0, 1, 0),
                                       Vector2D(j / segments_x, i / segments_y)))
        
        for i in range(segments_y):
            for j in range(segments_x):
                v0 = i * (segments_x + 1) + j
                v1 = v0 + 1
                v2 = v0 + segments_x + 1
                v3 = v2 + 1
                triangles.append(Triangle(v0, v1, v2))
                triangles.append(Triangle(v1, v3, v2))
        
        return Mesh(vertices, triangles)


# --- Physics Substrate ---

@dataclass
class PhysicsBody:
    """Physics body primitive"""
    position: Vector3D
    velocity: Vector3D = field(default_factory=lambda: Vector3D(0, 0, 0))
    acceleration: Vector3D = field(default_factory=lambda: Vector3D(0, 0, 0))
    mass: float = 1.0
    restitution: float = 0.8  # bounciness
    friction: float = 0.3
    
    @property
    def momentum(self) -> Vector3D:
        return self.velocity * self.mass
    
    @property
    def kinetic_energy(self) -> float:
        return 0.5 * self.mass * (self.velocity.magnitude ** 2)
    
    def apply_force(self, force: Vector3D) -> None:
        """Apply force to body"""
        self.acceleration = self.acceleration + force * (1 / self.mass)
    
    def step(self, dt: float) -> None:
        """Integrate physics step"""
        self.velocity = self.velocity + self.acceleration * dt
        self.position = self.position + self.velocity * dt
        self.acceleration = Vector3D(0, 0, 0)  # reset forces


class PhysicsSubstrate(Substrate):
    """Physics simulation substrate"""
    
    GRAVITY = Vector3D(0, -9.81, 0)
    
    def __init__(self):
        super().__init__("physics")
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "physics"
    
    def _init_primitives(self):
        self.register_primitive("body", PhysicsBody)
        self.register_primitive("gravity", self.GRAVITY)
        self.register_operation("simulate", self.simulate)
        self.register_operation("collide", self.collide)
    
    def simulate(self, bodies: List[PhysicsBody], dt: float,
                 gravity: bool = True) -> None:
        """Simulate physics for all bodies"""
        for body in bodies:
            if gravity:
                body.apply_force(self.GRAVITY * body.mass)
            body.step(dt)
    
    def collide(self, a: PhysicsBody, b: PhysicsBody) -> bool:
        """Simple sphere collision (assumed radius 1)"""
        dist = (a.position - b.position).magnitude
        if dist < 2:  # collision
            normal = (b.position - a.position).normalize()
            rel_vel = a.velocity - b.velocity
            vel_along_normal = rel_vel.dot(normal)
            
            if vel_along_normal > 0:
                return False
            
            e = min(a.restitution, b.restitution)
            j = -(1 + e) * vel_along_normal
            j /= 1/a.mass + 1/b.mass
            
            impulse = normal * j
            a.velocity = a.velocity + impulse * (1/a.mass)
            b.velocity = b.velocity - impulse * (1/b.mass)
            return True
        return False


# =============================================================================
# TEXT & LANGUAGE SUBSTRATES
# =============================================================================

class ASCIISubstrate(Substrate):
    """ASCII character operations"""
    
    def __init__(self):
        super().__init__("ascii")
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "text.ascii"
    
    def _init_primitives(self):
        self.register_operation("char_to_int", ord)
        self.register_operation("int_to_char", chr)
        self.register_operation("is_printable", self.is_printable)
        self.register_operation("art_block", self.art_block)
        self.register_operation("gradient_chars", self.gradient_chars)
    
    def is_printable(self, c: str) -> bool:
        return 32 <= ord(c) <= 126
    
    def gradient_chars(self) -> str:
        """Characters from darkest to lightest for ASCII art"""
        return " .:-=+*#%@"
    
    def art_block(self, intensity: float) -> str:
        """Get ASCII art character for intensity (0-1)"""
        chars = self.gradient_chars()
        idx = int(intensity * (len(chars) - 1))
        return chars[max(0, min(len(chars) - 1, idx))]
    
    def image_to_ascii(self, pixels: List[List[float]], width: int = 80) -> str:
        """Convert intensity array to ASCII art"""
        if not pixels:
            return ""
        h, w = len(pixels), len(pixels[0])
        scale_x = w / width
        scale_y = scale_x * 2  # Characters are ~2x tall as wide
        height = int(h / scale_y)
        
        result = []
        for y in range(height):
            row = []
            for x in range(width):
                px = int(x * scale_x)
                py = int(y * scale_y)
                if py < h and px < w:
                    row.append(self.art_block(pixels[py][px]))
                else:
                    row.append(' ')
            result.append(''.join(row))
        return '\n'.join(result)


class UnicodeSubstrate(Substrate):
    """Unicode character operations"""
    
    # Unicode block primitives
    BLOCKS = {
        'box_drawing': (0x2500, 0x257F),
        'block_elements': (0x2580, 0x259F),
        'geometric_shapes': (0x25A0, 0x25FF),
        'arrows': (0x2190, 0x21FF),
        'math_operators': (0x2200, 0x22FF),
        'braille': (0x2800, 0x28FF),
        'emoji': (0x1F600, 0x1F64F),
    }
    
    def __init__(self):
        super().__init__("unicode")
        self.add_sub_substrate(ASCIISubstrate())
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "text.unicode"
    
    def _init_primitives(self):
        self.register_primitive("blocks", self.BLOCKS)
        self.register_operation("codepoint", self.codepoint)
        self.register_operation("char", self.char)
        self.register_operation("braille_from_dots", self.braille_from_dots)
        self.register_operation("box_char", self.box_char)
    
    def codepoint(self, c: str) -> int:
        return ord(c)
    
    def char(self, codepoint: int) -> str:
        return chr(codepoint)
    
    def braille_from_dots(self, dots: List[int]) -> str:
        """Create braille character from dot positions (1-8)"""
        # Braille dots: 1 4
        #              2 5
        #              3 6
        #              7 8
        offset = 0
        for d in dots:
            offset |= (1 << (d - 1))
        return chr(0x2800 + offset)
    
    def box_char(self, left: bool = False, right: bool = False,
                 up: bool = False, down: bool = False) -> str:
        """Get box drawing character for connections"""
        # Lookup table for box drawing
        patterns = {
            (False, False, False, False): ' ',
            (True, True, False, False): '─',
            (False, False, True, True): '│',
            (False, True, False, True): '┌',
            (True, False, False, True): '┐',
            (False, True, True, False): '└',
            (True, False, True, False): '┘',
            (True, True, False, True): '┬',
            (True, True, True, False): '┴',
            (False, True, True, True): '├',
            (True, False, True, True): '┤',
            (True, True, True, True): '┼',
        }
        return patterns.get((left, right, up, down), '?')


class FontSubstrate(Substrate):
    """Typography and font metrics"""
    
    # Standard measurements
    POINTS_PER_INCH = 72
    PICAS_PER_INCH = 6
    POINTS_PER_PICA = 12
    
    def __init__(self):
        super().__init__("font")
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "text.font"
    
    def _init_primitives(self):
        self.register_primitive("points_per_inch", self.POINTS_PER_INCH)
        self.register_primitive("picas_per_inch", self.PICAS_PER_INCH)
        self.register_operation("points_to_pixels", self.points_to_pixels)
        self.register_operation("picas_to_points", self.picas_to_points)
        self.register_operation("em", self.em)
        self.register_operation("kerning", self.kerning)
    
    def points_to_pixels(self, points: float, dpi: float = 96) -> float:
        """Convert points to pixels at given DPI"""
        return points * dpi / self.POINTS_PER_INCH
    
    def picas_to_points(self, picas: float) -> float:
        """Convert picas to points"""
        return picas * self.POINTS_PER_PICA
    
    def em(self, font_size: float) -> float:
        """Get em unit for font size"""
        return font_size
    
    def kerning(self, char1: str, char2: str, base_spacing: float = 0) -> float:
        """Get kerning adjustment (simplified)"""
        # Kerning pairs that need tightening
        tight_pairs = {
            ('A', 'V'): -0.1, ('A', 'W'): -0.1, ('A', 'Y'): -0.1,
            ('V', 'A'): -0.1, ('W', 'A'): -0.1, ('Y', 'A'): -0.1,
            ('T', 'o'): -0.05, ('T', 'e'): -0.05, ('T', 'a'): -0.05,
            ('L', 'T'): -0.05, ('L', 'V'): -0.05,
            ('f', 'i'): -0.02, ('f', 'j'): -0.02,
        }
        return base_spacing + tight_pairs.get((char1, char2), 0)


class GrammarSubstrate(Substrate):
    """Grammar and language structure"""
    
    def __init__(self):
        super().__init__("grammar")
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "text.grammar"
    
    def _init_primitives(self):
        self.register_operation("tokenize", self.tokenize)
        self.register_operation("sentence_split", self.sentence_split)
        self.register_operation("pos_simple", self.pos_simple)
    
    def tokenize(self, text: str) -> List[str]:
        """Simple word tokenization"""
        import re
        return re.findall(r'\b\w+\b', text.lower())
    
    def sentence_split(self, text: str) -> List[str]:
        """Split text into sentences"""
        import re
        return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    
    def pos_simple(self, word: str) -> str:
        """Very simple POS tagging (placeholder)"""
        # In real implementation, this would use a proper NLP model
        if word.endswith('ly'):
            return 'ADV'
        elif word.endswith('ing'):
            return 'VERB'
        elif word.endswith('ed'):
            return 'VERB'
        elif word.endswith('tion') or word.endswith('ness'):
            return 'NOUN'
        return 'UNKNOWN'


class NaturalLanguageSubstrate(Substrate):
    """Natural language processing"""
    
    def __init__(self):
        super().__init__("nlp")
        self.add_sub_substrate(GrammarSubstrate())
        self.add_sub_substrate(UnicodeSubstrate())
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "text.nlp"
    
    def _init_primitives(self):
        self.register_operation("word_count", self.word_count)
        self.register_operation("char_count", self.char_count)
        self.register_operation("similarity", self.similarity)
        self.register_operation("ngrams", self.ngrams)
    
    def word_count(self, text: str) -> int:
        return len(self.get('grammar.tokenize')(text))
    
    def char_count(self, text: str, exclude_spaces: bool = False) -> int:
        if exclude_spaces:
            return len(text.replace(' ', ''))
        return len(text)
    
    def similarity(self, text1: str, text2: str) -> float:
        """Jaccard similarity between texts"""
        words1 = set(self.get('grammar.tokenize')(text1))
        words2 = set(self.get('grammar.tokenize')(text2))
        if not words1 or not words2:
            return 0.0
        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union)
    
    def ngrams(self, text: str, n: int = 2) -> List[Tuple[str, ...]]:
        """Generate n-grams from text"""
        words = self.get('grammar.tokenize')(text)
        return [tuple(words[i:i+n]) for i in range(len(words) - n + 1)]


# =============================================================================
# PHYSICS STATE SUBSTRATES (Solid, Liquid, Gas)
# =============================================================================

class MatterState(Enum):
    SOLID = auto()
    LIQUID = auto()
    GAS = auto()
    PLASMA = auto()


@dataclass
class MaterialProperties:
    """Material physical properties"""
    density: float  # kg/m³
    melting_point: float  # Kelvin
    boiling_point: float  # Kelvin
    specific_heat: float  # J/(kg·K)
    thermal_conductivity: float  # W/(m·K)
    viscosity: Optional[float] = None  # Pa·s (for fluids)
    youngs_modulus: Optional[float] = None  # Pa (for solids)
    
    def state_at_temp(self, temp_k: float) -> MatterState:
        """Determine state at given temperature"""
        if temp_k < self.melting_point:
            return MatterState.SOLID
        elif temp_k < self.boiling_point:
            return MatterState.LIQUID
        else:
            return MatterState.GAS


class SolidSubstrate(Substrate):
    """Solid state physics"""
    
    def __init__(self):
        super().__init__("solid")
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "physics.solid"
    
    def _init_primitives(self):
        self.register_operation("stress", self.stress)
        self.register_operation("strain", self.strain)
        self.register_operation("elastic_modulus", self.elastic_modulus)
        self.register_operation("fracture", self.fracture)
    
    def stress(self, force: float, area: float) -> float:
        """Calculate stress (Pa)"""
        return force / area if area > 0 else 0
    
    def strain(self, delta_length: float, original_length: float) -> float:
        """Calculate strain (dimensionless)"""
        return delta_length / original_length if original_length > 0 else 0
    
    def elastic_modulus(self, stress: float, strain: float) -> float:
        """Calculate Young's modulus"""
        return stress / strain if strain > 0 else 0
    
    def fracture(self, stress: float, yield_strength: float) -> bool:
        """Check if material will fracture"""
        return stress > yield_strength


class LiquidSubstrate(Substrate):
    """Liquid state physics"""
    
    def __init__(self):
        super().__init__("liquid")
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "physics.liquid"
    
    def _init_primitives(self):
        self.register_operation("pressure", self.pressure)
        self.register_operation("flow_rate", self.flow_rate)
        self.register_operation("viscous_force", self.viscous_force)
        self.register_operation("buoyancy", self.buoyancy)
    
    def pressure(self, density: float, depth: float, g: float = 9.81) -> float:
        """Hydrostatic pressure (Pa)"""
        return density * g * depth
    
    def flow_rate(self, area: float, velocity: float) -> float:
        """Volumetric flow rate (m³/s)"""
        return area * velocity
    
    def viscous_force(self, viscosity: float, area: float, 
                      velocity_gradient: float) -> float:
        """Calculate viscous drag force"""
        return viscosity * area * velocity_gradient
    
    def buoyancy(self, fluid_density: float, displaced_volume: float,
                 g: float = 9.81) -> float:
        """Buoyant force (N)"""
        return fluid_density * displaced_volume * g


class GasSubstrate(Substrate):
    """Gas state physics"""
    
    R = 8.314  # Universal gas constant J/(mol·K)
    
    def __init__(self):
        super().__init__("gas")
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "physics.gas"
    
    def _init_primitives(self):
        self.register_primitive("R", self.R)
        self.register_operation("ideal_gas", self.ideal_gas)
        self.register_operation("pressure", self.pressure)
        self.register_operation("rms_speed", self.rms_speed)
    
    def ideal_gas(self, n: float, T: float, V: float) -> float:
        """Ideal gas pressure P = nRT/V"""
        return n * self.R * T / V if V > 0 else 0
    
    def pressure(self, n: float, V: float, T: float) -> float:
        """Same as ideal_gas for clarity"""
        return self.ideal_gas(n, T, V)
    
    def rms_speed(self, T: float, molar_mass: float) -> float:
        """Root mean square speed of gas molecules"""
        return math.sqrt(3 * self.R * T / molar_mass) if molar_mass > 0 else 0


class DynamicsSubstrate(Substrate):
    """General dynamics combining all matter states"""
    
    def __init__(self):
        super().__init__("dynamics")
        self.add_sub_substrate(SolidSubstrate())
        self.add_sub_substrate(LiquidSubstrate())
        self.add_sub_substrate(GasSubstrate())
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "physics.dynamics"
    
    def _init_primitives(self):
        self.register_primitive("material", MaterialProperties)
        self.register_operation("phase_transition", self.phase_transition)
        self.register_operation("heat_transfer", self.heat_transfer)
    
    def phase_transition(self, material: MaterialProperties, 
                         current_temp: float, heat_added: float,
                         mass: float) -> Tuple[float, MatterState]:
        """Calculate temperature change and possible phase transition"""
        new_temp = current_temp + heat_added / (mass * material.specific_heat)
        new_state = material.state_at_temp(new_temp)
        return new_temp, new_state
    
    def heat_transfer(self, k: float, area: float, temp_diff: float,
                      thickness: float) -> float:
        """Conductive heat transfer rate (W)"""
        return k * area * temp_diff / thickness if thickness > 0 else 0


# =============================================================================
# MEDIA SUBSTRATES
# =============================================================================

class VoiceSynthesisSubstrate(Substrate):
    """Voice synthesis primitives"""
    
    # Formant frequencies for basic vowels (Hz)
    VOWEL_FORMANTS = {
        'a': (800, 1150, 2900),   # F1, F2, F3
        'e': (400, 2000, 2800),
        'i': (250, 2400, 3000),
        'o': (450, 800, 2830),
        'u': (300, 870, 2250),
    }
    
    def __init__(self):
        super().__init__("voice")
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "media.voice"
    
    def _init_primitives(self):
        self.register_primitive("vowel_formants", self.VOWEL_FORMANTS)
        self.register_operation("pitch_shift", self.pitch_shift)
        self.register_operation("formant_synthesis", self.formant_synthesis)
    
    def pitch_shift(self, base_freq: float, semitones: float) -> float:
        """Shift pitch by semitones"""
        return base_freq * (2 ** (semitones / 12))
    
    def formant_synthesis(self, vowel: str, pitch: float, 
                          duration: float) -> Dict[str, Any]:
        """Generate formant parameters for vowel synthesis"""
        formants = self.VOWEL_FORMANTS.get(vowel.lower(), self.VOWEL_FORMANTS['a'])
        return {
            'fundamental': pitch,
            'formants': formants,
            'duration': duration,
            'vowel': vowel
        }


class SheetMusicSubstrate(Substrate):
    """Sheet music notation"""
    
    NOTE_VALUES = {
        'whole': 4.0,
        'half': 2.0,
        'quarter': 1.0,
        'eighth': 0.5,
        'sixteenth': 0.25,
        'thirty-second': 0.125,
    }
    
    def __init__(self):
        super().__init__("sheet_music")
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "media.sheet_music"
    
    def _init_primitives(self):
        self.register_primitive("note_values", self.NOTE_VALUES)
        self.register_operation("beats", self.beats)
        self.register_operation("duration_at_tempo", self.duration_at_tempo)
        self.register_operation("staff_position", self.staff_position)
    
    def beats(self, note_type: str, dotted: bool = False) -> float:
        """Get number of beats for note type"""
        base = self.NOTE_VALUES.get(note_type, 1.0)
        return base * 1.5 if dotted else base
    
    def duration_at_tempo(self, note_type: str, bpm: float, 
                          dotted: bool = False) -> float:
        """Get duration in seconds at given tempo"""
        beats = self.beats(note_type, dotted)
        return beats * 60 / bpm
    
    def staff_position(self, note: str, octave: int, clef: str = 'treble') -> int:
        """Get staff line/space position (-10 to 10, 0 = middle line)"""
        notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        note_base = note.replace('#', '').replace('b', '')
        note_idx = notes.index(note_base) if note_base in notes else 0
        
        if clef == 'treble':
            # Middle C (C4) is on ledger line below staff = -6
            base_pos = (octave - 4) * 7 + note_idx - 6
        else:  # bass
            # Middle C (C4) is on ledger line above staff = 6
            base_pos = (octave - 4) * 7 + note_idx + 6 - 12
        
        return base_pos


class ImageSubstrate(Substrate):
    """Image manipulation"""
    
    def __init__(self):
        super().__init__("image")
        self.add_sub_substrate(PixelSubstrate())
        self.add_sub_substrate(ColorSubstrate())
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "media.image"
    
    def _init_primitives(self):
        self.register_operation("grayscale", self.grayscale)
        self.register_operation("brightness", self.brightness)
        self.register_operation("contrast", self.contrast)
        self.register_operation("invert", self.invert)
        self.register_operation("tint", self.tint)
    
    def grayscale(self, color: RGB) -> RGB:
        """Convert to grayscale using luminosity method"""
        gray = int(0.299 * color.r + 0.587 * color.g + 0.114 * color.b)
        return RGB(gray, gray, gray)
    
    def brightness(self, color: RGB, factor: float) -> RGB:
        """Adjust brightness (factor > 1 = brighter)"""
        return RGB(
            max(0, min(255, int(color.r * factor))),
            max(0, min(255, int(color.g * factor))),
            max(0, min(255, int(color.b * factor)))
        )
    
    def contrast(self, color: RGB, factor: float) -> RGB:
        """Adjust contrast (factor > 1 = more contrast)"""
        def adjust(c):
            return max(0, min(255, int(128 + (c - 128) * factor)))
        return RGB(adjust(color.r), adjust(color.g), adjust(color.b))
    
    def invert(self, color: RGB) -> RGB:
        """Invert colors"""
        return RGB(255 - color.r, 255 - color.g, 255 - color.b)
    
    def tint(self, color: RGB, tint_color: RGB, amount: float = 0.5) -> RGB:
        """Apply tint to color"""
        return color.blend(tint_color, amount)


# =============================================================================
# THEORY SUBSTRATES
# =============================================================================

class ColorTheorySubstrate(Substrate):
    """Color theory principles"""
    
    # Color wheel positions (degrees)
    COLOR_WHEEL = {
        'red': 0, 'orange': 30, 'yellow': 60, 'chartreuse': 90,
        'green': 120, 'spring': 150, 'cyan': 180, 'azure': 210,
        'blue': 240, 'violet': 270, 'magenta': 300, 'rose': 330
    }
    
    def __init__(self):
        super().__init__("color_theory")
        self.add_sub_substrate(ColorSubstrate())
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "theory.color"
    
    def _init_primitives(self):
        self.register_primitive("color_wheel", self.COLOR_WHEEL)
        self.register_operation("harmony", self.harmony)
        self.register_operation("temperature", self.temperature)
        self.register_operation("saturation_level", self.saturation_level)
    
    def harmony(self, base_hue: float, scheme: str) -> List[float]:
        """Get harmonious hues based on color theory schemes"""
        if scheme == 'complementary':
            return [base_hue, (base_hue + 180) % 360]
        elif scheme == 'triadic':
            return [base_hue, (base_hue + 120) % 360, (base_hue + 240) % 360]
        elif scheme == 'tetradic':
            return [base_hue, (base_hue + 90) % 360, 
                    (base_hue + 180) % 360, (base_hue + 270) % 360]
        elif scheme == 'analogous':
            return [(base_hue - 30) % 360, base_hue, (base_hue + 30) % 360]
        elif scheme == 'split-complementary':
            return [base_hue, (base_hue + 150) % 360, (base_hue + 210) % 360]
        return [base_hue]
    
    def temperature(self, hue: float) -> str:
        """Classify color temperature"""
        if 0 <= hue < 60 or 300 <= hue < 360:
            return 'warm'
        elif 160 <= hue < 280:
            return 'cool'
        return 'neutral'
    
    def saturation_level(self, s: float) -> str:
        """Classify saturation level"""
        if s < 0.2:
            return 'desaturated'
        elif s < 0.5:
            return 'muted'
        elif s < 0.8:
            return 'vivid'
        return 'saturated'


class MusicTheorySubstrate(Substrate):
    """Music theory principles"""
    
    # Intervals in semitones
    INTERVALS = {
        'unison': 0, 'minor_2nd': 1, 'major_2nd': 2, 'minor_3rd': 3,
        'major_3rd': 4, 'perfect_4th': 5, 'tritone': 6, 'perfect_5th': 7,
        'minor_6th': 8, 'major_6th': 9, 'minor_7th': 10, 'major_7th': 11,
        'octave': 12
    }
    
    # Scale patterns (semitone intervals)
    SCALES = {
        'major': [0, 2, 4, 5, 7, 9, 11],
        'minor': [0, 2, 3, 5, 7, 8, 10],
        'pentatonic_major': [0, 2, 4, 7, 9],
        'pentatonic_minor': [0, 3, 5, 7, 10],
        'blues': [0, 3, 5, 6, 7, 10],
        'chromatic': list(range(12)),
    }
    
    # Chord patterns
    CHORDS = {
        'major': [0, 4, 7],
        'minor': [0, 3, 7],
        'diminished': [0, 3, 6],
        'augmented': [0, 4, 8],
        'major_7th': [0, 4, 7, 11],
        'minor_7th': [0, 3, 7, 10],
        'dominant_7th': [0, 4, 7, 10],
    }
    
    def __init__(self):
        super().__init__("music_theory")
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "theory.music"
    
    def _init_primitives(self):
        self.register_primitive("intervals", self.INTERVALS)
        self.register_primitive("scales", self.SCALES)
        self.register_primitive("chords", self.CHORDS)
        self.register_operation("scale", self.scale)
        self.register_operation("chord", self.chord)
        self.register_operation("transpose", self.transpose)
    
    def scale(self, root: Frequency, scale_type: str = 'major') -> List[Frequency]:
        """Generate scale from root frequency"""
        pattern = self.SCALES.get(scale_type, self.SCALES['major'])
        return [root.interval(semitones) for semitones in pattern]
    
    def chord(self, root: Frequency, chord_type: str = 'major') -> List[Frequency]:
        """Generate chord from root frequency"""
        pattern = self.CHORDS.get(chord_type, self.CHORDS['major'])
        return [root.interval(semitones) for semitones in pattern]
    
    def transpose(self, freq: Frequency, semitones: int) -> Frequency:
        """Transpose by semitones"""
        return freq.interval(semitones)


class StatisticsSubstrate(Substrate):
    """Statistics and probability"""
    
    def __init__(self):
        super().__init__("statistics")
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "theory.statistics"
    
    def _init_primitives(self):
        self.register_operation("mean", self.mean)
        self.register_operation("median", self.median)
        self.register_operation("std_dev", self.std_dev)
        self.register_operation("variance", self.variance)
        self.register_operation("normalize", self.normalize)
        self.register_operation("percentile", self.percentile)
    
    def mean(self, data: List[float]) -> float:
        return sum(data) / len(data) if data else 0
    
    def median(self, data: List[float]) -> float:
        if not data:
            return 0
        sorted_data = sorted(data)
        n = len(sorted_data)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_data[mid - 1] + sorted_data[mid]) / 2
        return sorted_data[mid]
    
    def variance(self, data: List[float]) -> float:
        if not data:
            return 0
        m = self.mean(data)
        return sum((x - m) ** 2 for x in data) / len(data)
    
    def std_dev(self, data: List[float]) -> float:
        return math.sqrt(self.variance(data))
    
    def normalize(self, data: List[float]) -> List[float]:
        """Normalize to 0-1 range"""
        if not data:
            return []
        min_val, max_val = min(data), max(data)
        if max_val == min_val:
            return [0.5] * len(data)
        return [(x - min_val) / (max_val - min_val) for x in data]
    
    def percentile(self, data: List[float], p: float) -> float:
        """Get p-th percentile (0-100)"""
        if not data:
            return 0
        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * p / 100
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_data[int(k)]
        return sorted_data[int(f)] * (c - k) + sorted_data[int(c)] * (k - f)


class GameTheorySubstrate(Substrate):
    """Game theory primitives"""
    
    def __init__(self):
        super().__init__("game_theory")
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "theory.game"
    
    def _init_primitives(self):
        self.register_operation("payoff_matrix", self.payoff_matrix)
        self.register_operation("nash_equilibrium", self.nash_equilibrium_2x2)
        self.register_operation("minimax", self.minimax)
    
    def payoff_matrix(self, player1_payoffs: List[List[float]],
                      player2_payoffs: List[List[float]]) -> Dict[str, List[List[float]]]:
        """Create payoff matrix for 2-player game"""
        return {'player1': player1_payoffs, 'player2': player2_payoffs}
    
    def nash_equilibrium_2x2(self, p1: List[List[float]], 
                              p2: List[List[float]]) -> List[Tuple[int, int]]:
        """Find Nash equilibria in 2x2 game (simplified)"""
        equilibria = []
        for i in range(2):
            for j in range(2):
                # Check if (i,j) is a Nash equilibrium
                best_response_p1 = p1[0][j] >= p1[1][j] if i == 0 else p1[1][j] >= p1[0][j]
                best_response_p2 = p2[i][0] >= p2[i][1] if j == 0 else p2[i][1] >= p2[i][0]
                if best_response_p1 and best_response_p2:
                    equilibria.append((i, j))
        return equilibria
    
    def minimax(self, payoffs: List[List[float]], maximize: bool = True) -> Tuple[int, float]:
        """Find minimax strategy for zero-sum game"""
        if maximize:
            # Maximize minimum payoff
            min_per_row = [min(row) for row in payoffs]
            best_row = max(range(len(payoffs)), key=lambda i: min_per_row[i])
            return best_row, min_per_row[best_row]
        else:
            # Minimize maximum loss
            max_per_col = [max(payoffs[i][j] for i in range(len(payoffs))) 
                          for j in range(len(payoffs[0]))]
            best_col = min(range(len(payoffs[0])), key=lambda j: max_per_col[j])
            return best_col, max_per_col[best_col]


# =============================================================================
# PATTERN SUBSTRATES
# =============================================================================

class FractalSubstrate(Substrate):
    """Fractal generation"""
    
    def __init__(self):
        super().__init__("fractal")
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "pattern.fractal"
    
    def _init_primitives(self):
        self.register_operation("mandelbrot", self.mandelbrot)
        self.register_operation("julia", self.julia)
        self.register_operation("sierpinski", self.sierpinski_depth)
    
    def mandelbrot(self, x: float, y: float, max_iter: int = 100) -> int:
        """Calculate Mandelbrot set escape iterations"""
        c = complex(x, y)
        z = 0
        for i in range(max_iter):
            z = z * z + c
            if abs(z) > 2:
                return i
        return max_iter
    
    def julia(self, x: float, y: float, c: complex, max_iter: int = 100) -> int:
        """Calculate Julia set escape iterations"""
        z = complex(x, y)
        for i in range(max_iter):
            z = z * z + c
            if abs(z) > 2:
                return i
        return max_iter
    
    def sierpinski_depth(self, x: float, y: float, depth: int = 5) -> bool:
        """Check if point is in Sierpinski triangle at given depth"""
        for _ in range(depth):
            if x < 0.5:
                if y < 0.5:
                    return False  # bottom-left (hole)
                else:
                    y = y * 2 - 1  # top-left
            else:
                if y < 0.5:
                    x = x * 2 - 1  # bottom-right
                    y = y * 2
                else:
                    x = x * 2 - 1  # top-right
                    y = y * 2 - 1
        return True


class PatternSubstrate(Substrate):
    """Pattern generation and tiling"""
    
    def __init__(self):
        super().__init__("pattern")
        self.add_sub_substrate(FractalSubstrate())
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "pattern"
    
    def _init_primitives(self):
        self.register_operation("checkerboard", self.checkerboard)
        self.register_operation("stripes", self.stripes)
        self.register_operation("dots", self.dots)
        self.register_operation("hexagonal", self.hexagonal)
        self.register_operation("noise", self.simple_noise)
    
    def checkerboard(self, x: float, y: float, scale: float = 1.0) -> bool:
        """Checkerboard pattern"""
        return (int(x * scale) + int(y * scale)) % 2 == 0
    
    def stripes(self, coord: float, width: float = 0.1) -> bool:
        """Stripe pattern"""
        return (coord % (width * 2)) < width
    
    def dots(self, x: float, y: float, spacing: float = 0.2, 
             radius: float = 0.05) -> bool:
        """Polka dot pattern"""
        x = x % spacing
        y = y % spacing
        cx, cy = spacing / 2, spacing / 2
        return math.sqrt((x - cx)**2 + (y - cy)**2) < radius
    
    def hexagonal(self, x: float, y: float, size: float = 0.1) -> int:
        """Return which hexagon cell the point is in"""
        # Simplified hex grid indexing
        col = int(x / (size * 1.5))
        row = int(y / (size * math.sqrt(3)))
        return col * 1000 + row
    
    def simple_noise(self, x: float, y: float, seed: int = 42) -> float:
        """Simple value noise (not Perlin, but deterministic)"""
        def hash_coord(ix, iy):
            n = ix + iy * 57 + seed
            n = (n << 13) ^ n
            return 1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0
        
        ix, iy = int(x), int(y)
        fx, fy = x - ix, y - iy
        
        # Smooth interpolation
        fx = fx * fx * (3 - 2 * fx)
        fy = fy * fy * (3 - 2 * fy)
        
        v00 = hash_coord(ix, iy)
        v10 = hash_coord(ix + 1, iy)
        v01 = hash_coord(ix, iy + 1)
        v11 = hash_coord(ix + 1, iy + 1)
        
        return (v00 * (1 - fx) + v10 * fx) * (1 - fy) + \
               (v01 * (1 - fx) + v11 * fx) * fy


class EdgeFindingSubstrate(Substrate):
    """Edge detection primitives"""
    
    def __init__(self):
        super().__init__("edge_finding")
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "pattern.edge"
    
    def _init_primitives(self):
        # Sobel kernels
        self.register_primitive("sobel_x", [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        self.register_primitive("sobel_y", [[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        self.register_operation("gradient", self.gradient)
        self.register_operation("edge_strength", self.edge_strength)
    
    def gradient(self, neighborhood: List[List[float]], 
                 kernel: List[List[int]]) -> float:
        """Apply kernel to 3x3 neighborhood"""
        total = 0
        for i in range(3):
            for j in range(3):
                total += neighborhood[i][j] * kernel[i][j]
        return total
    
    def edge_strength(self, neighborhood: List[List[float]]) -> float:
        """Calculate edge magnitude using Sobel"""
        gx = self.gradient(neighborhood, self._primitives['sobel_x'])
        gy = self.gradient(neighborhood, self._primitives['sobel_y'])
        return math.sqrt(gx * gx + gy * gy)


class TilingSubstrate(Substrate):
    """Tiling and mosaic patterns"""
    
    def __init__(self):
        super().__init__("tiling")
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "pattern.tiling"
    
    def _init_primitives(self):
        self.register_operation("voronoi_cell", self.voronoi_cell)
        self.register_operation("brick", self.brick)
        self.register_operation("herringbone", self.herringbone)
    
    def voronoi_cell(self, x: float, y: float, 
                     points: List[Tuple[float, float]]) -> int:
        """Find which Voronoi cell contains point"""
        min_dist = float('inf')
        cell = 0
        for i, (px, py) in enumerate(points):
            dist = (x - px)**2 + (y - py)**2
            if dist < min_dist:
                min_dist = dist
                cell = i
        return cell
    
    def brick(self, x: float, y: float, width: float = 0.2, 
              height: float = 0.1) -> Tuple[int, int]:
        """Brick pattern - returns (row, col) of brick"""
        row = int(y / height)
        offset = (row % 2) * (width / 2)
        col = int((x + offset) / width)
        return (row, col)
    
    def herringbone(self, x: float, y: float, size: float = 0.1) -> int:
        """Herringbone pattern - returns tile index"""
        # Simplified herringbone indexing
        scaled_x = x / size
        scaled_y = y / size
        block_x = int(scaled_x) // 2
        block_y = int(scaled_y)
        return (block_x + block_y) % 2


# =============================================================================
# ADVANCED SUBSTRATES
# =============================================================================

class QuantumSubstrate(Substrate):
    """Quantum-inspired primitives"""
    
    def __init__(self):
        super().__init__("quantum")
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "advanced.quantum"
    
    def _init_primitives(self):
        self.register_operation("superposition", self.superposition)
        self.register_operation("collapse", self.collapse)
        self.register_operation("entangle", self.entangle)
    
    def superposition(self, states: List[Any], amplitudes: List[float]) -> Dict[str, Any]:
        """Create superposition of states with amplitudes"""
        # Normalize amplitudes
        total = sum(a**2 for a in amplitudes)
        normalized = [a / math.sqrt(total) for a in amplitudes] if total > 0 else amplitudes
        return {
            'states': states,
            'amplitudes': normalized,
            'probabilities': [a**2 for a in normalized]
        }
    
    def collapse(self, superposition: Dict[str, Any], random_val: float = None) -> Any:
        """Collapse superposition to definite state"""
        import random
        r = random_val if random_val is not None else random.random()
        cumulative = 0
        for state, prob in zip(superposition['states'], superposition['probabilities']):
            cumulative += prob
            if r < cumulative:
                return state
        return superposition['states'][-1]
    
    def entangle(self, state_a: Any, state_b: Any) -> Dict[str, Any]:
        """Create entangled pair"""
        return {
            'entangled': True,
            'state_a': state_a,
            'state_b': state_b,
            'correlation': 1.0  # Perfect correlation
        }


class GameEngineSubstrate(Substrate):
    """Game engine primitives"""
    
    def __init__(self):
        super().__init__("game_engine")
        self.add_sub_substrate(Graphics3DSubstrate())
        self.add_sub_substrate(PhysicsSubstrate())
        self._init_primitives()
    
    @property
    def domain(self) -> str:
        return "advanced.game_engine"
    
    def _init_primitives(self):
        self.register_operation("entity", self.create_entity)
        self.register_operation("component", self.create_component)
        self.register_operation("system", self.create_system)
    
    def create_entity(self, entity_id: int) -> Dict[str, Any]:
        """Create ECS entity"""
        return {'id': entity_id, 'components': {}}
    
    def create_component(self, component_type: str, **data) -> Dict[str, Any]:
        """Create component with data"""
        return {'type': component_type, 'data': data}
    
    def create_system(self, name: str, 
                      component_types: List[str]) -> Dict[str, Any]:
        """Create system that processes specific components"""
        return {
            'name': name,
            'requires': component_types,
            'entities': []
        }


# =============================================================================
# SECURE RESOURCE LOCATOR (SRL) - O(1) Lookup System
# =============================================================================

class SecureResourceLocator:
    """
    The SRL System - O(1) Lookup for All Substrates
    
    This is the "library index card" that knows where everything is.
    Every primitive, every operation, every substrate is addressable.
    
    Address format: srl://domain/substrate/primitive
    Example: srl://graphics.color/color/rgb
             srl://theory.music/music_theory/scale
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._registry: Dict[str, Any] = {}
            cls._instance._substrates: Dict[str, Substrate] = {}
            cls._instance._hash_index: Dict[str, str] = {}  # hash -> address
        return cls._instance
    
    def register(self, substrate: Substrate) -> str:
        """Register a substrate and all its contents"""
        address = substrate.srl_address()
        self._substrates[address] = substrate
        self._registry[address] = substrate
        
        # Index all primitives
        for name, primitive in substrate._primitives.items():
            prim_addr = f"{address}/{name}"
            self._registry[prim_addr] = primitive
            # Create hash for O(1) lookup
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
        """Generate hash for address"""
        return hashlib.sha256(address.encode()).hexdigest()[:16]
    
    def get(self, address: str) -> Any:
        """O(1) lookup by SRL address"""
        # Direct lookup
        if address in self._registry:
            return self._registry[address]
        
        # Try hash lookup
        addr_hash = self._hash(address)
        if addr_hash in self._hash_index:
            real_addr = self._hash_index[addr_hash]
            return self._registry.get(real_addr)
        
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
    
    def list_operations(self, substrate_address: str) -> List[str]:
        """List all operations in a substrate"""
        substrate = self._substrates.get(substrate_address)
        if substrate:
            return list(substrate._operations.keys())
        return []


# =============================================================================
# SUBSTRATE KERNEL - Factory for Creating Substrate Instances
# =============================================================================

class SubstrateKernel:
    """
    The Kernel that instantiates and manages all substrates.
    
    This is the core that:
    - Creates substrates from primitives
    - Combines substrates for complex operations
    - Registers everything with the SRL for O(1) access
    """
    
    def __init__(self):
        self.srl = SecureResourceLocator()
        self._core_substrates: Dict[str, Substrate] = {}
        self._initialize_core()
    
    def _initialize_core(self):
        """Initialize all core substrates"""
        # Graphics
        self._register_core(PixelSubstrate())
        self._register_core(ColorSubstrate())
        self._register_core(GradientSubstrate())
        self._register_core(ShaderSubstrate())
        self._register_core(Graphics3DSubstrate())
        
        # Physics
        self._register_core(PhysicsSubstrate())
        self._register_core(SolidSubstrate())
        self._register_core(LiquidSubstrate())
        self._register_core(GasSubstrate())
        self._register_core(DynamicsSubstrate())
        
        # Text
        self._register_core(ASCIISubstrate())
        self._register_core(UnicodeSubstrate())
        self._register_core(FontSubstrate())
        self._register_core(GrammarSubstrate())
        self._register_core(NaturalLanguageSubstrate())
        
        # Media
        self._register_core(VoiceSynthesisSubstrate())
        self._register_core(SheetMusicSubstrate())
        self._register_core(ImageSubstrate())
        
        # Theory
        self._register_core(ColorTheorySubstrate())
        self._register_core(MusicTheorySubstrate())
        self._register_core(StatisticsSubstrate())
        self._register_core(GameTheorySubstrate())
        
        # Pattern
        self._register_core(FractalSubstrate())
        self._register_core(PatternSubstrate())
        self._register_core(EdgeFindingSubstrate())
        self._register_core(TilingSubstrate())
        
        # Advanced
        self._register_core(QuantumSubstrate())
        self._register_core(GameEngineSubstrate())
    
    def _register_core(self, substrate: Substrate) -> None:
        """Register a core substrate"""
        self._core_substrates[substrate.name] = substrate
        self.srl.register(substrate)
    
    def get(self, name: str) -> Optional[Substrate]:
        """Get a core substrate by name"""
        return self._core_substrates.get(name)
    
    def combine(self, *substrate_names: str) -> Substrate:
        """Combine multiple substrates into a composite"""
        combined = CompositeSubstrate("composite")
        for name in substrate_names:
            substrate = self.get(name)
            if substrate:
                combined.add_sub_substrate(substrate)
        return combined
    
    def create_custom(self, name: str, base: str = None, 
                      primitives: Dict[str, Any] = None,
                      operations: Dict[str, Callable] = None) -> Substrate:
        """Create a custom substrate"""
        custom = CustomSubstrate(name, base)
        
        if primitives:
            for pname, prim in primitives.items():
                custom.register_primitive(pname, prim)
        
        if operations:
            for oname, op in operations.items():
                custom.register_operation(oname, op)
        
        self._register_core(custom)
        return custom
    
    def invoke(self, address: str, *args, **kwargs) -> Any:
        """Direct O(1) invoke through SRL"""
        return self.srl.invoke(address, *args, **kwargs)
    
    def lookup(self, address: str) -> Any:
        """Direct O(1) lookup through SRL"""
        return self.srl.get(address)


class CompositeSubstrate(Substrate):
    """A substrate composed of multiple sub-substrates"""
    
    def __init__(self, name: str):
        super().__init__(name)
    
    @property
    def domain(self) -> str:
        return f"composite.{self.name}"


class CustomSubstrate(Substrate):
    """A user-defined custom substrate"""
    
    def __init__(self, name: str, base_domain: str = None):
        super().__init__(name)
        self._base_domain = base_domain or "custom"
    
    @property
    def domain(self) -> str:
        return f"{self._base_domain}.{self.name}"


# =============================================================================
# CONVENIENCE - Global kernel instance
# =============================================================================

# Create global kernel instance
KERNEL = SubstrateKernel()

# Convenience function for O(1) access
def srl(address: str) -> Any:
    """O(1) lookup via SRL"""
    return KERNEL.srl.get(address)

def invoke(address: str, *args, **kwargs) -> Any:
    """O(1) invoke via SRL"""
    return KERNEL.srl.invoke(address, *args, **kwargs)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Kernel
    'SubstrateKernel', 'KERNEL',
    'SecureResourceLocator', 'srl', 'invoke',
    
    # Base classes
    'Substrate', 'CompositeSubstrate', 'CustomSubstrate',
    'PrimitiveType', 'KernelPrimitive',
    
    # Mathematical primitives
    'Scalar', 'Vector2D', 'Vector3D', 'Matrix3x3', 'Matrix4x4',
    
    # Color primitives
    'RGB', 'RGBA', 'GradientStop',
    
    # Sound primitives
    'Frequency', 'Amplitude', 'Waveform', 'Duration', 'TimePoint',
    
    # 3D primitives
    'Vertex', 'Edge', 'Triangle', 'Mesh',
    
    # Physics primitives
    'PhysicsBody', 'MaterialProperties', 'MatterState',
    
    # Graphics substrates
    'PixelSubstrate', 'ColorSubstrate', 'GradientSubstrate',
    'ShaderSubstrate', 'Graphics3DSubstrate',
    
    # Physics substrates
    'PhysicsSubstrate', 'SolidSubstrate', 'LiquidSubstrate',
    'GasSubstrate', 'DynamicsSubstrate',
    
    # Text substrates
    'ASCIISubstrate', 'UnicodeSubstrate', 'FontSubstrate',
    'GrammarSubstrate', 'NaturalLanguageSubstrate',
    
    # Media substrates
    'VoiceSynthesisSubstrate', 'SheetMusicSubstrate', 'ImageSubstrate',
    
    # Theory substrates
    'ColorTheorySubstrate', 'MusicTheorySubstrate',
    'StatisticsSubstrate', 'GameTheorySubstrate',
    
    # Pattern substrates
    'FractalSubstrate', 'PatternSubstrate',
    'EdgeFindingSubstrate', 'TilingSubstrate',
    
    # Advanced substrates
    'QuantumSubstrate', 'GameEngineSubstrate',
]
