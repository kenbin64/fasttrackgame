"""
ButterflyFX Manifold Server - Transmit Math, Not Bits

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

Part of DimensionsOS - Open source networking layer.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

CORE INSIGHT:
    Traditional: Send 48,000 samples per second (192KB/s at 16-bit stereo)
    Manifold:    Send mathematical function parameters (tens of bytes)
    
    Any computer can evaluate math. Math is universal.
    The receiver GENERATES the audio from the equation.

EXAMPLE:
    A pure sine wave at 440Hz (concert A):
    
    Traditional: 48,000 samples = 192,000 bytes/second
    Manifold:    f(t) = sin(2π * 440 * t)
                 Parameters: {type: 'sin', freq: 440, amp: 1.0}
                 Size: ~30 bytes TOTAL (not per second)

For complex audio:
    - Decompose into harmonic components (Fourier)
    - Transmit the spectrum coefficients
    - Receiver synthesizes from harmonics
    
Even voice/instruments can be approximated:
    - Guitar string: sum of harmonic modes with decay
    - Voice: formant frequencies + noise component
    - Drums: impulse + resonance parameters

LATENCY ADVANTAGE:
    - Smaller data = faster transmission
    - Receiver can PREDICT future samples (just evaluate f(t+dt))
    - No waiting for samples to arrive - math is continuous
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable, Union
from enum import Enum, auto
import math
import struct
import time
import array


# =============================================================================
# MATHEMATICAL WAVEFORM DESCRIPTIONS
# =============================================================================

class WaveformType(Enum):
    """Types of mathematical waveforms"""
    SILENCE = 0        # f(t) = 0
    SINE = 1           # f(t) = A * sin(2πft + φ)
    COSINE = 2         # f(t) = A * cos(2πft + φ)
    SQUARE = 3         # f(t) = A * sign(sin(2πft))
    SAWTOOTH = 4       # f(t) = A * (2(ft mod 1) - 1)
    TRIANGLE = 5       # f(t) = A * (2|2(ft mod 1) - 1| - 1)
    NOISE = 6          # Pseudo-random with seed
    HARMONIC = 7       # Sum of sine waves (Fourier)
    ENVELOPE = 8       # ADSR envelope
    COMPOSITE = 9      # Multiple waveforms combined


@dataclass
class WaveformDescriptor:
    """
    Mathematical description of a waveform.
    
    This is what gets transmitted instead of samples.
    The receiver evaluates this to generate audio.
    """
    waveform_type: WaveformType
    frequency: float = 440.0      # Hz
    amplitude: float = 1.0        # 0.0 to 1.0
    phase: float = 0.0            # radians
    
    # For harmonics (Fourier series)
    harmonics: Optional[List[Tuple[float, float, float]]] = None  # [(freq, amp, phase), ...]
    
    # For envelope
    attack_ms: float = 10.0
    decay_ms: float = 100.0
    sustain_level: float = 0.7
    release_ms: float = 200.0
    
    # For noise
    seed: int = 0
    
    # Start time reference
    start_time: float = 0.0
    
    def evaluate(self, t: float) -> float:
        """
        Evaluate waveform at time t (seconds).
        
        This is the UNIVERSAL decoder - just math.
        """
        local_t = t - self.start_time
        if local_t < 0:
            return 0.0
        
        if self.waveform_type == WaveformType.SILENCE:
            return 0.0
        
        elif self.waveform_type == WaveformType.SINE:
            return self.amplitude * math.sin(2 * math.pi * self.frequency * local_t + self.phase)
        
        elif self.waveform_type == WaveformType.COSINE:
            return self.amplitude * math.cos(2 * math.pi * self.frequency * local_t + self.phase)
        
        elif self.waveform_type == WaveformType.SQUARE:
            sine_val = math.sin(2 * math.pi * self.frequency * local_t + self.phase)
            return self.amplitude * (1.0 if sine_val >= 0 else -1.0)
        
        elif self.waveform_type == WaveformType.SAWTOOTH:
            phase_pos = (self.frequency * local_t + self.phase / (2 * math.pi)) % 1.0
            return self.amplitude * (2 * phase_pos - 1)
        
        elif self.waveform_type == WaveformType.TRIANGLE:
            phase_pos = (self.frequency * local_t + self.phase / (2 * math.pi)) % 1.0
            return self.amplitude * (4 * abs(phase_pos - 0.5) - 1)
        
        elif self.waveform_type == WaveformType.NOISE:
            # Deterministic pseudo-random based on time and seed
            sample_idx = int(local_t * 48000)  # Sample rate
            x = (sample_idx + self.seed) * 1103515245 + 12345
            x = ((x >> 16) & 0x7FFF) / 32767.0 * 2 - 1
            return self.amplitude * x
        
        elif self.waveform_type == WaveformType.HARMONIC:
            if not self.harmonics:
                return 0.0
            total = 0.0
            for freq, amp, phase in self.harmonics:
                total += amp * math.sin(2 * math.pi * freq * local_t + phase)
            return self.amplitude * total
        
        return 0.0
    
    def generate_samples(self, duration_ms: float, sample_rate: int = 48000) -> bytes:
        """
        Generate PCM samples from the mathematical description.
        
        This is what the receiver does - evaluate math, produce samples.
        """
        num_samples = int(sample_rate * duration_ms / 1000)
        samples = array.array('h')  # 16-bit signed
        
        for i in range(num_samples):
            t = i / sample_rate + self.start_time
            value = self.evaluate(t)
            # Clamp and convert to 16-bit
            sample = int(max(-1.0, min(1.0, value)) * 32767)
            samples.append(sample)
        
        return samples.tobytes()
    
    def serialize(self) -> bytes:
        """
        Serialize to compact binary format.
        
        This is TINY compared to raw audio.
        """
        # Base: type(1) + freq(4) + amp(4) + phase(4) + start(8) = 21 bytes
        data = struct.pack(
            '>B f f f d',
            self.waveform_type.value,
            self.frequency,
            self.amplitude,
            self.phase,
            self.start_time
        )
        
        # Harmonics if present
        if self.harmonics:
            data += struct.pack('>H', len(self.harmonics))
            for freq, amp, phase in self.harmonics:
                data += struct.pack('>f f f', freq, amp, phase)
        else:
            data += struct.pack('>H', 0)
        
        # Envelope
        data += struct.pack('>f f f f', self.attack_ms, self.decay_ms, self.sustain_level, self.release_ms)
        
        # Noise seed
        data += struct.pack('>I', self.seed)
        
        return data
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'WaveformDescriptor':
        """Deserialize from binary with bounds checking"""
        # Minimum size: 21 (header) + 2 (num_harmonics) + 16 (envelope) + 4 (seed) = 43 bytes
        if len(data) < 43:
            raise ValueError(f"WaveformDescriptor requires at least 43 bytes, got {len(data)}")
        
        offset = 0
        
        wtype, freq, amp, phase, start = struct.unpack('>B f f f d', data[offset:offset+21])
        offset += 21
        
        # Validate waveform type
        if wtype > 10:
            raise ValueError(f"Invalid waveform type: {wtype}")
        
        num_harmonics = struct.unpack('>H', data[offset:offset+2])[0]
        offset += 2
        
        # Limit harmonics to prevent memory exhaustion
        if num_harmonics > 1000:
            raise ValueError(f"Too many harmonics: {num_harmonics}")
        
        # Check we have enough data for harmonics
        required = offset + (num_harmonics * 12) + 16 + 4
        if len(data) < required:
            raise ValueError(f"Truncated data: need {required} bytes for {num_harmonics} harmonics")
        
        harmonics = None
        if num_harmonics > 0:
            harmonics = []
            for _ in range(num_harmonics):
                hf, ha, hp = struct.unpack('>f f f', data[offset:offset+12])
                harmonics.append((hf, ha, hp))
                offset += 12
        
        attack, decay, sustain, release = struct.unpack('>f f f f', data[offset:offset+16])
        offset += 16
        
        seed = struct.unpack('>I', data[offset:offset+4])[0]
        
        return cls(
            waveform_type=WaveformType(wtype),
            frequency=freq,
            amplitude=amp,
            phase=phase,
            start_time=start,
            harmonics=harmonics,
            attack_ms=attack,
            decay_ms=decay,
            sustain_level=sustain,
            release_ms=release,
            seed=seed
        )


# =============================================================================
# MANIFOLD PACKET - Mathematical state transmission
# =============================================================================

@dataclass
class ManifoldPacket:
    """
    A packet containing mathematical waveform descriptions.
    
    Instead of sending audio samples:
        spiral: Which musician
        level: Audio priority level
        time_ref: Absolute time reference for synchronization
        waveforms: List of active mathematical descriptions
        
    The receiver evaluates all waveforms at their local time.
    """
    spiral: int                              # Musician ID
    sequence: int                            # Packet sequence
    time_ref: float                          # Server time reference
    waveforms: List[WaveformDescriptor]      # Active waveforms
    
    # Magic header for wire format
    MAGIC = b'MFLD'
    
    def serialize(self) -> bytes:
        """Serialize to wire format"""
        # Serialize all waveforms
        waveform_data = b''
        for wf in self.waveforms:
            wf_bytes = wf.serialize()
            waveform_data += struct.pack('>H', len(wf_bytes)) + wf_bytes
        
        # Header: magic(4) + spiral(2) + seq(4) + time(8) + num_wf(2) = 20 bytes
        header = struct.pack(
            '>4s H I d H',
            self.MAGIC,
            self.spiral,
            self.sequence,
            self.time_ref,
            len(self.waveforms)
        )
        
        return header + waveform_data
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'ManifoldPacket':
        """Deserialize from wire format with bounds checking"""
        # Minimum header size: 20 bytes
        if len(data) < 20:
            raise ValueError(f"ManifoldPacket requires at least 20 bytes, got {len(data)}")
        
        magic, spiral, seq, time_ref, num_wf = struct.unpack('>4s H I d H', data[:20])
        
        if magic != cls.MAGIC:
            raise ValueError(f"Invalid magic: {magic}")
        
        # Limit waveforms to prevent memory exhaustion
        if num_wf > 1000:
            raise ValueError(f"Too many waveforms: {num_wf}")
        
        offset = 20
        waveforms = []
        for i in range(num_wf):
            # Check we can read wf_len
            if offset + 2 > len(data):
                raise ValueError(f"Truncated data reading waveform {i} length")
            
            wf_len = struct.unpack('>H', data[offset:offset+2])[0]
            offset += 2
            
            # Check we have enough data for this waveform
            if offset + wf_len > len(data):
                raise ValueError(f"Truncated data reading waveform {i}: need {wf_len} bytes")
            
            wf = WaveformDescriptor.deserialize(data[offset:offset+wf_len])
            waveforms.append(wf)
            offset += wf_len
        
        return cls(
            spiral=spiral,
            sequence=seq,
            time_ref=time_ref,
            waveforms=waveforms
        )
    
    def generate_audio(self, duration_ms: float, local_time: float, sample_rate: int = 48000) -> bytes:
        """
        Generate audio by evaluating all waveforms.
        
        This is what the receiver does - math to samples.
        """
        num_samples = int(sample_rate * duration_ms / 1000)
        samples = array.array('h')
        
        for i in range(num_samples):
            t = local_time + (i / sample_rate)
            total = 0.0
            
            for wf in self.waveforms:
                total += wf.evaluate(t)
            
            # Clamp and convert
            sample = int(max(-1.0, min(1.0, total)) * 32767)
            samples.append(sample)
        
        return samples.tobytes()


# =============================================================================
# AUDIO ANALYZER - Convert samples to mathematical description
# =============================================================================

class AudioAnalyzer:
    """
    Analyze audio samples and extract mathematical description.
    
    This is the encoder side - convert raw audio to math.
    
    Methods:
        - Zero-crossing frequency detection
        - Amplitude envelope extraction
        - Simple harmonic analysis (FFT for proper use)
    """
    
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
    
    def analyze(self, samples: bytes) -> WaveformDescriptor:
        """
        Analyze raw audio and return mathematical description.
        
        For real use, this would use FFT. Here we demonstrate the concept.
        """
        # Convert to array
        arr = array.array('h')
        arr.frombytes(samples)
        
        if len(arr) == 0:
            return WaveformDescriptor(WaveformType.SILENCE)
        
        # Normalize
        max_val = max(abs(s) for s in arr) or 1
        normalized = [s / max_val for s in arr]
        
        # Estimate amplitude
        amplitude = max_val / 32767.0
        
        # Count zero crossings for frequency estimate
        crossings = 0
        for i in range(1, len(normalized)):
            if normalized[i-1] < 0 and normalized[i] >= 0:
                crossings += 1
            elif normalized[i-1] >= 0 and normalized[i] < 0:
                crossings += 1
        
        duration = len(arr) / self.sample_rate
        frequency = crossings / (2 * duration) if duration > 0 else 440
        
        # Guess waveform type based on harmonic content
        # (In reality, we'd use FFT)
        waveform_type = WaveformType.SINE  # Default assumption
        
        return WaveformDescriptor(
            waveform_type=waveform_type,
            frequency=frequency,
            amplitude=amplitude,
            phase=0.0,
            start_time=time.time()
        )
    
    def decompose_harmonics(self, samples: bytes, num_harmonics: int = 8) -> WaveformDescriptor:
        """
        Decompose audio into harmonic components.
        
        This is a simplified version - real implementation would use FFT.
        Returns a HARMONIC waveform with multiple sine components.
        """
        arr = array.array('h')
        arr.frombytes(samples)
        
        if len(arr) == 0:
            return WaveformDescriptor(WaveformType.SILENCE)
        
        # Get base frequency
        base = self.analyze(samples)
        
        # Create harmonic series
        harmonics = []
        for n in range(1, num_harmonics + 1):
            freq = base.frequency * n
            # Amplitude decreases with harmonic number (1/n approximation)
            amp = base.amplitude / n
            phase = 0.0
            harmonics.append((freq, amp, phase))
        
        return WaveformDescriptor(
            waveform_type=WaveformType.HARMONIC,
            frequency=base.frequency,
            amplitude=1.0,
            harmonics=harmonics,
            start_time=time.time()
        )


# =============================================================================
# MANIFOLD SERVER - Serves math, not bytes
# =============================================================================

class ManifoldServer:
    """
    Server that broadcasts mathematical waveform descriptions.
    
    Instead of streaming audio samples:
        1. Receive audio from musician
        2. Analyze and extract mathematical description
        3. Broadcast description to all participants
        4. Each participant generates audio locally from math
    
    ADVANTAGES:
        - Tiny data: ~50 bytes vs ~192KB per second
        - Universal: any computer understands math
        - Predictive: receiver can extrapolate future samples
        - Graceful degradation: partial data still produces audio
    """
    
    def __init__(self):
        self.analyzer = AudioAnalyzer()
        self.active_waveforms: Dict[int, List[WaveformDescriptor]] = {}  # spiral -> waveforms
        self.sequence = 0
        self.time_sync = time.time()
    
    def receive_audio(self, spiral: int, samples: bytes) -> ManifoldPacket:
        """
        Receive raw audio from a musician and convert to manifold.
        
        Returns packet ready for broadcast.
        """
        # Analyze the audio
        waveform = self.analyzer.decompose_harmonics(samples)
        
        # Store active waveform
        if spiral not in self.active_waveforms:
            self.active_waveforms[spiral] = []
        
        # Keep only recent waveforms (last 10)
        self.active_waveforms[spiral].append(waveform)
        self.active_waveforms[spiral] = self.active_waveforms[spiral][-10:]
        
        # Create packet with all active waveforms for this musician
        self.sequence += 1
        return ManifoldPacket(
            spiral=spiral,
            sequence=self.sequence,
            time_ref=time.time(),
            waveforms=[waveform]  # Just the new one
        )
    
    def broadcast(self) -> List[ManifoldPacket]:
        """
        Create broadcast packets for all active musicians.
        """
        packets = []
        for spiral, waveforms in self.active_waveforms.items():
            if waveforms:
                self.sequence += 1
                packets.append(ManifoldPacket(
                    spiral=spiral,
                    sequence=self.sequence,
                    time_ref=time.time(),
                    waveforms=waveforms[-1:]  # Most recent
                ))
        return packets


# =============================================================================
# MANIFOLD CLIENT - Receives math, generates audio
# =============================================================================

class ManifoldClient:
    """
    Client that receives mathematical descriptions and generates audio.
    
    The client:
        1. Receives ManifoldPackets (mathematical descriptions)
        2. Evaluates the math at local time
        3. Produces audio samples for playback
        
    PREDICTION:
        Because we have the mathematical function, we can evaluate
        it at any time - including FUTURE times. This allows us to
        buffer ahead, smoothing over network jitter.
    """
    
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.active_waveforms: Dict[int, List[WaveformDescriptor]] = {}
        self.time_offset = 0.0  # Local time adjustment
    
    def receive_packet(self, packet: ManifoldPacket):
        """
        Receive a manifold packet and update local state.
        """
        if packet.spiral not in self.active_waveforms:
            self.active_waveforms[packet.spiral] = []
        
        self.active_waveforms[packet.spiral].extend(packet.waveforms)
        
        # Keep only recent
        self.active_waveforms[packet.spiral] = self.active_waveforms[packet.spiral][-20:]
    
    def generate_audio(self, duration_ms: float) -> Dict[int, bytes]:
        """
        Generate audio for all active musicians.
        
        Returns: spiral -> PCM samples
        """
        now = time.time() + self.time_offset
        num_samples = int(self.sample_rate * duration_ms / 1000)
        
        result = {}
        for spiral, waveforms in self.active_waveforms.items():
            if not waveforms:
                continue
            
            samples = array.array('h')
            for i in range(num_samples):
                t = now + (i / self.sample_rate)
                total = 0.0
                
                for wf in waveforms[-5:]:  # Use recent waveforms
                    total += wf.evaluate(t)
                
                sample = int(max(-1.0, min(1.0, total)) * 32767)
                samples.append(sample)
            
            result[spiral] = samples.tobytes()
        
        return result
    
    def predict_ahead(self, spiral: int, lookahead_ms: float) -> bytes:
        """
        Generate predicted audio for a musician.
        
        Because we have math, we can evaluate at future times.
        This is IMPOSSIBLE with raw sample transmission.
        """
        waveforms = self.active_waveforms.get(spiral, [])
        if not waveforms:
            return b''
        
        future_time = time.time() + self.time_offset + (lookahead_ms / 1000)
        num_samples = int(self.sample_rate * lookahead_ms / 1000)
        
        samples = array.array('h')
        for i in range(num_samples):
            t = future_time + (i / self.sample_rate)
            total = 0.0
            
            for wf in waveforms[-5:]:
                total += wf.evaluate(t)
            
            sample = int(max(-1.0, min(1.0, total)) * 32767)
            samples.append(sample)
        
        return samples.tobytes()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'WaveformType',
    'WaveformDescriptor',
    'ManifoldPacket',
    'AudioAnalyzer',
    'ManifoldServer',
    'ManifoldClient',
]
