"""
ButterflyFX Media Package
==========================

Copyright (c) 2024-2026 Kenneth Bingham - All Rights Reserved
https://butterflyfx.us

PROFESSIONAL TIER PACKAGE - $29/month

Media production substrates that derive video, audio, and voice from
kernel primitives. This package demonstrates the substrate's ability
to orchestrate complex multimedia workflows.

The substrate DERIVES capabilities - it doesn't just wrap libraries,
it composes them from fundamental operations.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Setup path for standalone execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import kernel primitives (always available - open source)
from kernel_primitives import (
    Substrate,
    Vector2D, Vector3D,
    Matrix4x4,
    RGB, RGBA,
    Frequency, Amplitude,
    Duration, TimePoint,
)

# Import licensing
from licensing import requires_license


# =============================================================================
# FRAME SUBSTRATE - Derives visual frames from geometry + color
# =============================================================================

@dataclass
class Frame:
    """A single video frame - derived from kernel primitives"""
    width: int
    height: int
    pixels: List[List[RGB]] = field(default_factory=list)
    timestamp: float = 0.0
    
    def __post_init__(self):
        if not self.pixels:
            self.pixels = [[RGB(0, 0, 0) for _ in range(self.width)] for _ in range(self.height)]
    
    def set_pixel(self, x: int, y: int, color: RGB):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color
    
    def fill(self, color: RGB):
        for y in range(self.height):
            for x in range(self.width):
                self.pixels[y][x] = color
    
    def to_pil(self):
        """Convert to PIL Image for export - optimized with numpy"""
        from PIL import Image
        import numpy as np
        # Fast numpy conversion instead of pixel-by-pixel
        arr = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        for y in range(self.height):
            for x in range(self.width):
                c = self.pixels[y][x]
                arr[y, x] = [c.r, c.g, c.b]
        return Image.fromarray(arr, 'RGB')
    
    def to_pil_fast(self, np_array):
        """Fastest conversion from pre-built numpy array"""
        from PIL import Image
        return Image.fromarray(np_array, 'RGB')


@requires_license("media")
class FrameSubstrate(Substrate):
    """
    Derives video frames from kernel primitives.
    
    Operations: create_frame, draw_circle, draw_rect, draw_text, gradient_fill
    """
    
    def __init__(self, width: int = 1920, height: int = 1080):
        super().__init__("frame")
        self.width = width
        self.height = height
        self._init_operations()
    
    @property
    def domain(self) -> str:
        return "media.frame"
    
    def _init_operations(self):
        self.register_primitive("frame", Frame)
        self.register_operation("create", self.create_frame)
        self.register_operation("gradient", self.gradient_fill)
        self.register_operation("circle", self.draw_circle)
        self.register_operation("rect", self.draw_rect)
        self.register_operation("sphere_3d", self.draw_3d_sphere)
        self.register_operation("helix_3d", self.draw_3d_helix)
    
    def create_frame(self, timestamp: float = 0.0) -> Frame:
        """Create empty frame"""
        return Frame(self.width, self.height, timestamp=timestamp)
    
    def gradient_fill(self, frame: Frame, color1: RGB, color2: RGB, 
                      angle: float = 0) -> Frame:
        """Fill frame with gradient - derived from color blending"""
        for y in range(frame.height):
            for x in range(frame.width):
                # Project onto gradient line
                nx = x / frame.width
                ny = y / frame.height
                t = nx * math.cos(angle) + ny * math.sin(angle)
                t = max(0, min(1, (t + 0.5)))  # Normalize
                frame.set_pixel(x, y, color1.blend(color2, t))
        return frame
    
    def draw_circle(self, frame: Frame, cx: int, cy: int, radius: int, 
                    color: RGB, filled: bool = True) -> Frame:
        """Draw circle - derived from Euclidean distance"""
        r2 = radius * radius
        for y in range(max(0, cy - radius), min(frame.height, cy + radius + 1)):
            for x in range(max(0, cx - radius), min(frame.width, cx + radius + 1)):
                d2 = (x - cx) ** 2 + (y - cy) ** 2
                if filled:
                    if d2 <= r2:
                        frame.set_pixel(x, y, color)
                else:
                    if abs(d2 - r2) < radius * 2:
                        frame.set_pixel(x, y, color)
        return frame
    
    def draw_rect(self, frame: Frame, x: int, y: int, w: int, h: int, 
                  color: RGB) -> Frame:
        """Draw rectangle"""
        for dy in range(h):
            for dx in range(w):
                frame.set_pixel(x + dx, y + dy, color)
        return frame
    
    def draw_3d_sphere(self, frame: Frame, cx: int, cy: int, radius: int,
                       base_color: RGB, light_dir: Vector3D, time: float = 0) -> Frame:
        """
        Draw 3D-shaded sphere - derives lighting from vector math.
        
        This demonstrates the kernel's ability to derive 3D graphics
        from fundamental primitives (vectors, colors).
        """
        light = light_dir.normalize()
        
        for y in range(max(0, cy - radius), min(frame.height, cy + radius + 1)):
            for x in range(max(0, cx - radius), min(frame.width, cx + radius + 1)):
                dx = (x - cx) / radius
                dy = (y - cy) / radius
                d2 = dx * dx + dy * dy
                
                if d2 <= 1.0:
                    # Calculate surface normal
                    dz = math.sqrt(1.0 - d2)
                    normal = Vector3D(dx, dy, dz)
                    
                    # Lambertian shading
                    diffuse = max(0, normal.x * light.x + normal.y * light.y + normal.z * light.z)
                    
                    # Add some ambient
                    intensity = 0.2 + 0.8 * diffuse
                    
                    # Apply to color
                    r = int(min(255, base_color.r * intensity))
                    g = int(min(255, base_color.g * intensity))
                    b = int(min(255, base_color.b * intensity))
                    
                    frame.set_pixel(x, y, RGB(r, g, b))
        
        return frame
    
    def draw_3d_helix(self, frame: Frame, cx: int, cy: int, 
                      radius: int, color: RGB, time: float, 
                      turns: int = 3, points: int = 100) -> Frame:
        """
        Draw 3D helix - the ButterflyFX signature shape.
        
        Derived from parametric equations using kernel vectors.
        """
        for i in range(points):
            t = i / points * turns * 2 * math.pi + time
            
            # Parametric helix
            x = cx + int(radius * math.cos(t) * (0.5 + 0.5 * math.cos(t / turns)))
            y = cy + int(radius * 0.3 * t / (turns * 2 * math.pi) - radius * 0.15)
            
            # Depth-based color
            depth = 0.5 + 0.5 * math.sin(t)
            r = int(color.r * (0.3 + 0.7 * depth))
            g = int(color.g * (0.3 + 0.7 * depth))
            b = int(color.b * (0.3 + 0.7 * depth))
            
            # Draw point with glow
            for dy in range(-3, 4):
                for dx in range(-3, 4):
                    d = math.sqrt(dx*dx + dy*dy)
                    if d < 3:
                        intensity = 1.0 - d / 3
                        frame.set_pixel(
                            x + dx, y + dy,
                            RGB(int(r * intensity), int(g * intensity), int(b * intensity))
                        )
        
        return frame


# =============================================================================
# AUDIO SUBSTRATE - Derives sound from frequency primitives
# =============================================================================

@dataclass
class AudioSample:
    """Audio sample - derived from Frequency and Amplitude"""
    sample_rate: int = 44100
    channels: int = 2
    samples: List[float] = field(default_factory=list)
    duration: float = 0.0


@requires_license("media")
class AudioSubstrate(Substrate):
    """
    Derives audio from kernel frequency/amplitude primitives.
    
    Operations: tone, chord, envelope, mix
    """
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__("audio")
        self.sample_rate = sample_rate
        self._init_operations()
    
    @property
    def domain(self) -> str:
        return "media.audio"
    
    def _init_operations(self):
        self.register_primitive("sample", AudioSample)
        self.register_operation("tone", self.generate_tone)
        self.register_operation("chord", self.generate_chord)
        self.register_operation("envelope", self.apply_envelope)
        self.register_operation("ambient", self.generate_ambient)
    
    def generate_tone(self, freq: Frequency, duration: float, 
                      amplitude: float = 0.5) -> AudioSample:
        """Generate pure tone from Frequency primitive or float Hz"""
        # Handle float input
        if isinstance(freq, (int, float)):
            freq = Frequency(float(freq))
        
        num_samples = int(self.sample_rate * duration)
        samples = []
        
        for i in range(num_samples):
            t = i / self.sample_rate
            sample = amplitude * math.sin(2 * math.pi * freq.hz * t)
            samples.append(sample)
        
        return AudioSample(self.sample_rate, 1, samples, duration)
    
    def generate_chord(self, frequencies: List[Frequency], duration: float,
                       amplitude: float = 0.3) -> AudioSample:
        """Generate chord from multiple frequencies"""
        num_samples = int(self.sample_rate * duration)
        samples = []
        
        for i in range(num_samples):
            t = i / self.sample_rate
            sample = 0.0
            for freq in frequencies:
                sample += amplitude * math.sin(2 * math.pi * freq.hz * t)
            sample /= len(frequencies)
            samples.append(sample)
        
        return AudioSample(self.sample_rate, 1, samples, duration)
    
    def apply_envelope(self, audio: AudioSample, attack: float = 0.1,
                       decay: float = 0.1, sustain: float = 0.7,
                       release: float = 0.2) -> AudioSample:
        """Apply ADSR envelope - derived from temporal primitives"""
        total = attack + decay + sustain + release
        new_samples = []
        
        for i, sample in enumerate(audio.samples):
            t = i / self.sample_rate
            progress = t / audio.duration
            
            if progress < attack / total:
                env = progress / (attack / total)
            elif progress < (attack + decay) / total:
                env = 1.0 - 0.3 * (progress - attack/total) / (decay/total)
            elif progress < (attack + decay + sustain) / total:
                env = 0.7
            else:
                env = 0.7 * (1.0 - (progress - (attack+decay+sustain)/total) / (release/total))
            
            new_samples.append(sample * max(0, env))
        
        return AudioSample(audio.sample_rate, audio.channels, new_samples, audio.duration)
    
    def generate_ambient(self, duration: float, base_freq: float = 80) -> AudioSample:
        """
        Generate ambient pad sound - demonstrates procedural audio.
        
        Uses layered sine waves with subtle modulation.
        """
        num_samples = int(self.sample_rate * duration)
        samples = []
        
        # Multiple detuned oscillators
        freqs = [base_freq, base_freq * 1.5, base_freq * 2, base_freq * 2.5, base_freq * 3]
        
        for i in range(num_samples):
            t = i / self.sample_rate
            sample = 0.0
            
            for j, freq in enumerate(freqs):
                # Slow modulation
                mod = 1.0 + 0.01 * math.sin(2 * math.pi * 0.1 * t + j)
                amp = 0.15 / (j + 1)  # Higher harmonics quieter
                sample += amp * math.sin(2 * math.pi * freq * mod * t)
            
            # Soft filter effect (simple low-pass approximation)
            samples.append(sample * 0.8)
        
        return AudioSample(self.sample_rate, 1, samples, duration)
    
    def to_wav_bytes(self, audio: AudioSample) -> bytes:
        """Export to WAV format"""
        import struct
        import io
        
        # Normalize and convert to 16-bit
        max_val = max(abs(s) for s in audio.samples) if audio.samples else 1.0
        if max_val == 0:
            max_val = 1.0
        
        int_samples = [int(s / max_val * 32767) for s in audio.samples]
        
        # WAV header
        buf = io.BytesIO()
        num_samples = len(int_samples)
        
        buf.write(b'RIFF')
        buf.write(struct.pack('<I', 36 + num_samples * 2))
        buf.write(b'WAVE')
        buf.write(b'fmt ')
        buf.write(struct.pack('<I', 16))  # Subchunk1Size
        buf.write(struct.pack('<H', 1))   # AudioFormat (PCM)
        buf.write(struct.pack('<H', 1))   # NumChannels
        buf.write(struct.pack('<I', audio.sample_rate))
        buf.write(struct.pack('<I', audio.sample_rate * 2))  # ByteRate
        buf.write(struct.pack('<H', 2))   # BlockAlign
        buf.write(struct.pack('<H', 16))  # BitsPerSample
        buf.write(b'data')
        buf.write(struct.pack('<I', num_samples * 2))
        
        for sample in int_samples:
            buf.write(struct.pack('<h', sample))
        
        return buf.getvalue()


# =============================================================================
# VOICE SUBSTRATE - Derives speech from text
# =============================================================================

@requires_license("media")
class VoiceSubstrate(Substrate):
    """
    Derives voice/speech from text.
    
    Can ingest external TTS engines or generate simple synthesis.
    """
    
    def __init__(self):
        super().__init__("voice")
        self._tts_available = self._check_tts()
        self._init_operations()
    
    @property
    def domain(self) -> str:
        return "media.voice"
    
    def _check_tts(self) -> bool:
        """Check if external TTS is available"""
        try:
            from gtts import gTTS
            return True
        except ImportError:
            return False
    
    def _init_operations(self):
        self.register_operation("speak", self.generate_speech)
        self.register_operation("available", lambda: self._tts_available)
    
    def generate_speech(self, text: str, output_path: str, lang: str = 'en') -> str:
        """Generate speech audio file from text"""
        if self._tts_available:
            from gtts import gTTS
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(output_path)
            return output_path
        else:
            # Fallback: create silent placeholder
            audio = AudioSubstrate()
            silent = audio.generate_tone(Frequency(0), len(text) * 0.1)
            with open(output_path, 'wb') as f:
                f.write(audio.to_wav_bytes(silent))
            return output_path


# =============================================================================
# VIDEO SUBSTRATE - Orchestrates frame + audio into video
# =============================================================================

@requires_license("media")
class VideoSubstrate(Substrate):
    """
    Derives video from frames + audio.
    
    Orchestrates the media production pipeline using kernel primitives.
    """
    
    def __init__(self, width: int = 1920, height: int = 1080, fps: int = 30):
        super().__init__("video")
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_sub = FrameSubstrate(width, height)
        self.audio_sub = AudioSubstrate()
        self.voice_sub = VoiceSubstrate()
        self._init_operations()
    
    @property
    def domain(self) -> str:
        return "media.video"
    
    def _init_operations(self):
        self.register_operation("render", self.render_video)
        self.register_operation("compose", self.compose_scene)
    
    def render_video(self, frames: List[Frame], audio_path: Optional[str],
                     output_path: str) -> str:
        """
        Render frames + audio to MP4 video.
        
        Uses ffmpeg for encoding but all content is substrate-derived.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save frames as images
            print(f"  Saving {len(frames)} frames...")
            for i, frame in enumerate(frames):
                img = frame.to_pil()
                img.save(os.path.join(tmpdir, f"frame_{i:05d}.png"))
            
            # Build ffmpeg command
            cmd = [
                'ffmpeg', '-y',
                '-framerate', str(self.fps),
                '-i', os.path.join(tmpdir, 'frame_%05d.png'),
            ]
            
            if audio_path and os.path.exists(audio_path):
                cmd.extend(['-i', audio_path])
                cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
            
            cmd.extend([
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-preset', 'fast',
                output_path
            ])
            
            print(f"  Encoding video...")
            subprocess.run(cmd, capture_output=True)
        
        return output_path
    
    def compose_scene(self, scene_script: List[dict], duration: float) -> Tuple[List[Frame], str]:
        """
        Compose a scene from script directives.
        
        Each directive describes what to draw at what time.
        """
        num_frames = int(duration * self.fps)
        frames = []
        
        for frame_idx in range(num_frames):
            t = frame_idx / self.fps
            progress = t / duration
            
            frame = self.frame_sub.create_frame(t)
            
            # Process each scene element
            for element in scene_script:
                elem_type = element.get("type")
                start = element.get("start", 0)
                end = element.get("end", duration)
                
                if not (start <= t <= end):
                    continue
                
                elem_progress = (t - start) / (end - start) if end > start else 0
                
                if elem_type == "gradient":
                    c1 = RGB.from_hex(element["color1"])
                    c2 = RGB.from_hex(element["color2"])
                    angle = element.get("angle", 0) + elem_progress * element.get("rotate", 0)
                    self.frame_sub.gradient_fill(frame, c1, c2, angle)
                
                elif elem_type == "sphere":
                    cx = int(element.get("x", self.width // 2) + 
                            elem_progress * element.get("move_x", 0))
                    cy = int(element.get("y", self.height // 2) +
                            elem_progress * element.get("move_y", 0))
                    radius = int(element.get("radius", 100) * 
                                (element.get("start_scale", 1) + 
                                 elem_progress * (element.get("end_scale", 1) - element.get("start_scale", 1))))
                    color = RGB.from_hex(element["color"])
                    light = Vector3D(
                        math.cos(t * element.get("light_speed", 1)),
                        0.5,
                        math.sin(t * element.get("light_speed", 1))
                    )
                    self.frame_sub.draw_3d_sphere(frame, cx, cy, radius, color, light, t)
                
                elif elem_type == "helix":
                    cx = element.get("x", self.width // 2)
                    cy = element.get("y", self.height // 2)
                    radius = element.get("radius", 200)
                    color = RGB.from_hex(element["color"])
                    self.frame_sub.draw_3d_helix(frame, cx, cy, radius, color, t * 2)
                
                elif elem_type == "circle":
                    cx = element.get("x", self.width // 2)
                    cy = element.get("y", self.height // 2)
                    radius = int(element.get("radius", 50) * (1 + elem_progress * element.get("grow", 0)))
                    color = RGB.from_hex(element["color"])
                    self.frame_sub.draw_circle(frame, cx, cy, radius, color)
            
            frames.append(frame)
            
            if frame_idx % 30 == 0:
                print(f"    Frame {frame_idx}/{num_frames} ({100*frame_idx//num_frames}%)")
        
        return frames


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'Frame',
    'FrameSubstrate',
    'AudioSample',
    'AudioSubstrate',
    'VoiceSubstrate',
    'VideoSubstrate',
]
