"""
ButterflyFX Audio Transport - Optimized for Real-Time Music Collaboration

Designed for systems like JamKazam where latency causes:
    1. Music distortion (audio arrives too late)
    2. Player confusion (listening for cues that are delayed)
    3. Feedback loops (adjusting to already-delayed signals)

HELIX ADVANTAGES FOR AUDIO:

    1. SPIRAL PER MUSICIAN
       Each player gets their own dimensional channel.
       Parallel processing, no serialization bottleneck.
       
    2. LEVEL-BASED AUDIO STACK
       Level 0: Raw PCM samples (lowest latency path)
       Level 1: Audio frames (encoded chunks)
       Level 2: Timing/sync signals (metronome, beat)
       Level 3: Flow control (buffer management)
       Level 4: Session state (who's playing, muted)
       Level 5: Metadata (instrument, channel)
       Level 6: Application control (mix, effects)
       
    3. PRIORITY CHANNELS
       Timing data (Level 2) gets priority over metadata (Level 5).
       Critical sync info never waits behind less important data.
       
    4. PREDICTIVE BUFFERING
       Use manifold geometry to extrapolate missing samples.
       If a packet is late, predict based on waveform continuity.

TARGET LATENCIES:
    - JamKazam typical: 20-40ms (barely playable)
    - Professional studio: <10ms
    - ButterflyFX goal: Reduce encoding overhead to <1ms
    
The network RTT is fixed, but we can minimize everything else.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Generator, Callable
from enum import Enum, auto
import struct
import time
import math
import array


# =============================================================================
# AUDIO TRANSPORT LEVELS - Optimized for Music
# =============================================================================

class AudioLevel(Enum):
    """
    Audio-specific level mapping for the helix.
    Each level has a specific role in the audio pipeline.
    """
    RAW_SAMPLES = 0      # PCM samples - fastest path, no encoding
    AUDIO_FRAMES = 1     # Encoded audio chunks (opus, etc.)
    TIMING_SYNC = 2      # Metronome, beat markers, sync signals
    FLOW_CONTROL = 3     # Buffer status, congestion
    SESSION_STATE = 4    # Player status, mute, solo
    METADATA = 5         # Instrument info, channel assignment
    APP_CONTROL = 6      # Mix levels, effects, room settings


AUDIO_LEVEL_PRIORITY = {
    AudioLevel.RAW_SAMPLES: 0,     # Highest priority
    AudioLevel.TIMING_SYNC: 1,     # Second highest - sync is critical
    AudioLevel.AUDIO_FRAMES: 2,
    AudioLevel.FLOW_CONTROL: 3,
    AudioLevel.SESSION_STATE: 4,
    AudioLevel.METADATA: 5,
    AudioLevel.APP_CONTROL: 6,     # Lowest priority
}


# =============================================================================
# AUDIO FRAME - Minimal overhead audio packet
# =============================================================================

@dataclass
class AudioFrame:
    """
    A single audio frame for transmission.
    
    Designed for MINIMAL LATENCY:
        - Fixed-size header (16 bytes)
        - No JSON, no base64
        - Direct struct pack
        - Sequence number for ordering
        - Timestamp for sync
    
    Header format: [spiral:2][level:1][seq:4][timestamp:4][samples:2][channels:1][bits:1][len:2]
    """
    spiral: int           # Musician ID (0-65535)
    level: int            # AudioLevel value (0-6)
    sequence: int         # Frame sequence number
    timestamp_ms: int     # Milliseconds since session start
    samples: int          # Number of samples in frame
    channels: int         # 1=mono, 2=stereo
    bits_per_sample: int  # 16 or 24
    payload: bytes        # Raw audio data
    
    # Header: H(2) + B(1) + I(4) + I(4) + H(2) + H(2) + B(1) + B(1) = 17 bytes
    HEADER_SIZE = 17
    HEADER_FORMAT = '>HBIIHHBB'
    
    def serialize(self) -> bytes:
        """
        Serialize to wire format.
        
        This is FAST - just struct.pack, no encoding.
        Target: <0.01ms for typical frame.
        """
        header = struct.pack(
            self.HEADER_FORMAT,
            self.spiral,
            self.level,
            self.sequence,
            self.timestamp_ms,
            len(self.payload),
            self.samples,
            self.channels,
            self.bits_per_sample
        )
        return header + self.payload
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'AudioFrame':
        """
        Deserialize from wire format.
        
        Also FAST - just struct.unpack.
        """
        (spiral, level, seq, ts, payload_len, 
         samples, channels, bits) = struct.unpack(cls.HEADER_FORMAT, data[:cls.HEADER_SIZE])
        
        return cls(
            spiral=spiral,
            level=level,
            sequence=seq,
            timestamp_ms=ts,
            samples=samples,
            channels=channels,
            bits_per_sample=bits,
            payload=data[cls.HEADER_SIZE:cls.HEADER_SIZE+payload_len]
        )
    
    @property
    def wire_size(self) -> int:
        return self.HEADER_SIZE + len(self.payload)
    
    @property
    def duration_ms(self) -> float:
        """Duration of this frame in milliseconds"""
        # Assuming 48kHz sample rate
        return (self.samples / 48000) * 1000
    
    def __repr__(self) -> str:
        return f"AudioFrame(spiral={self.spiral}, seq={self.sequence}, {self.samples} samples, {self.duration_ms:.1f}ms)"


# =============================================================================
# SYNC SIGNAL - Critical timing data
# =============================================================================

@dataclass
class SyncSignal:
    """
    Timing synchronization signal.
    
    This is the HIGHEST PRIORITY data after raw samples.
    Used to keep all musicians in sync.
    
    Contains:
        - Session clock (master time reference)
        - Beat position (where we are in the bar)
        - Tempo (BPM)
        - Latency estimates per musician
    """
    session_time_ms: int      # Master clock
    beat_position: float      # 0.0 to 4.0 for 4/4 time
    tempo_bpm: float          # Current tempo
    bar_number: int           # Which bar we're in
    latencies: Dict[int, int] # spiral -> estimated latency ms
    
    def serialize(self) -> bytes:
        """Compact binary format"""
        # Fixed part: 4 + 4 + 4 + 4 = 16 bytes
        header = struct.pack(
            '>I f f I',
            self.session_time_ms,
            self.beat_position,
            self.tempo_bpm,
            self.bar_number
        )
        # Latency pairs: 2 bytes spiral + 2 bytes latency each
        latency_data = b''.join(
            struct.pack('>HH', spiral, lat)
            for spiral, lat in self.latencies.items()
        )
        return struct.pack('>B', len(self.latencies)) + header + latency_data
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'SyncSignal':
        count = data[0]
        session_time, beat_pos, tempo, bar = struct.unpack('>I f f I', data[1:17])
        
        latencies = {}
        offset = 17
        for _ in range(count):
            spiral, lat = struct.unpack('>HH', data[offset:offset+4])
            latencies[spiral] = lat
            offset += 4
        
        return cls(
            session_time_ms=session_time,
            beat_position=beat_pos,
            tempo_bpm=tempo,
            bar_number=bar,
            latencies=latencies
        )


# =============================================================================
# AUDIO STREAM - Per-musician audio channel
# =============================================================================

class AudioStream:
    """
    Audio stream for a single musician (one spiral).
    
    Features:
        - Jitter buffer to smooth network variance
        - Sequence tracking for packet loss detection
        - Latency estimation
        - Sample interpolation for missing frames
    """
    
    def __init__(
        self, 
        spiral: int,
        buffer_ms: int = 20,
        sample_rate: int = 48000
    ):
        self.spiral = spiral
        self.buffer_ms = buffer_ms
        self.sample_rate = sample_rate
        
        # Jitter buffer
        self._buffer: List[AudioFrame] = []
        self._max_buffer_frames = int(buffer_ms * sample_rate / 1000 / 480)  # 10ms frames
        
        # Sequence tracking
        self._last_sequence = -1
        self._packets_received = 0
        self._packets_lost = 0
        
        # Latency tracking
        self._latencies: List[int] = []
        self._send_times: Dict[int, int] = {}  # sequence -> send time
        
    def send(self, samples: bytes, channels: int = 2, bits: int = 16) -> AudioFrame:
        """
        Create and send an audio frame.
        
        Returns the frame ready for transmission.
        """
        self._last_sequence += 1
        
        # Calculate samples count
        bytes_per_sample = bits // 8 * channels
        num_samples = len(samples) // bytes_per_sample
        
        frame = AudioFrame(
            spiral=self.spiral,
            level=AudioLevel.RAW_SAMPLES.value,
            sequence=self._last_sequence,
            timestamp_ms=int(time.time() * 1000) % (2**32),
            samples=num_samples,
            channels=channels,
            bits_per_sample=bits,
            payload=samples
        )
        
        # Track send time for latency calculation
        self._send_times[frame.sequence] = frame.timestamp_ms
        
        return frame
    
    def receive(self, frame: AudioFrame) -> Optional[bytes]:
        """
        Receive an audio frame into the jitter buffer.
        
        Returns samples if buffer is ready, None if buffering.
        """
        self._packets_received += 1
        
        # Check for lost packets
        if self._last_sequence >= 0:
            expected = self._last_sequence + 1
            if frame.sequence > expected:
                lost = frame.sequence - expected
                self._packets_lost += lost
        
        self._last_sequence = frame.sequence
        
        # Add to buffer (sorted by sequence)
        self._buffer.append(frame)
        self._buffer.sort(key=lambda f: f.sequence)
        
        # Trim buffer if too large
        while len(self._buffer) > self._max_buffer_frames:
            self._buffer.pop(0)
        
        # Return oldest frame if buffer is full enough
        if len(self._buffer) >= self._max_buffer_frames // 2:
            oldest = self._buffer.pop(0)
            return oldest.payload
        
        return None
    
    def interpolate_missing(self, prev_samples: bytes, next_samples: bytes) -> bytes:
        """
        Interpolate missing audio frame.
        
        Uses linear interpolation between previous and next frames.
        This prevents clicks/pops from dropped packets.
        """
        # Convert to array for math
        prev = array.array('h')
        prev.frombytes(prev_samples)
        
        next_arr = array.array('h')
        next_arr.frombytes(next_samples)
        
        # Linear interpolation
        result = array.array('h')
        for i in range(len(prev)):
            interpolated = (prev[i] + next_arr[i]) // 2
            result.append(interpolated)
        
        return result.tobytes()
    
    @property
    def stats(self) -> Dict:
        return {
            'spiral': self.spiral,
            'packets_received': self._packets_received,
            'packets_lost': self._packets_lost,
            'loss_rate': self._packets_lost / max(1, self._packets_received),
            'buffer_depth': len(self._buffer),
            'estimated_latency': sum(self._latencies[-10:]) // max(1, len(self._latencies[-10:])) if self._latencies else 0
        }


# =============================================================================
# AUDIO TRANSPORT - Multi-musician coordination
# =============================================================================

class AudioTransport:
    """
    Full audio transport for multi-musician sessions.
    
    Each musician gets their own spiral (dimensional channel).
    All spirals share timing via sync signals at Level 2.
    
    Usage:
        transport = AudioTransport(my_spiral=0)
        
        # Send my audio
        for frame in transport.send_audio(my_samples):
            network.send(frame.serialize())
        
        # Receive others' audio  
        for data in network.receive():
            samples = transport.receive_audio(data)
            mixer.add(samples)
        
        # Check sync
        sync = transport.get_sync()
        adjust_playback(sync.beat_position)
    """
    
    def __init__(
        self,
        my_spiral: int,
        buffer_ms: int = 20,
        frame_size_ms: int = 10
    ):
        self.my_spiral = my_spiral
        self.buffer_ms = buffer_ms
        self.frame_size_ms = frame_size_ms
        
        # My outgoing stream
        self._my_stream = AudioStream(my_spiral, buffer_ms)
        
        # Incoming streams (one per other musician)
        self._streams: Dict[int, AudioStream] = {}
        
        # Sync state
        self._sync = SyncSignal(
            session_time_ms=0,
            beat_position=0.0,
            tempo_bpm=120.0,
            bar_number=0,
            latencies={}
        )
        
        # Latency tracking
        self._latency_samples: Dict[int, List[int]] = {}
        
        # Stats
        self._frames_sent = 0
        self._frames_received = 0
        self._total_latency_ms = 0
    
    def _get_stream(self, spiral: int) -> AudioStream:
        """Get or create stream for a musician"""
        if spiral not in self._streams:
            self._streams[spiral] = AudioStream(spiral, self.buffer_ms)
        return self._streams[spiral]
    
    # -------------------------------------------------------------------------
    # Sending
    # -------------------------------------------------------------------------
    
    def send_audio(
        self,
        samples: bytes,
        channels: int = 2,
        bits: int = 16
    ) -> AudioFrame:
        """
        Send audio samples.
        
        Returns frame ready for wire transmission.
        """
        frame = self._my_stream.send(samples, channels, bits)
        self._frames_sent += 1
        return frame
    
    def send_sync(self, beat_position: float, tempo: float, bar: int) -> bytes:
        """
        Send sync signal (usually from session leader).
        
        Returns serialized sync data.
        """
        self._sync = SyncSignal(
            session_time_ms=int(time.time() * 1000) % (2**32),
            beat_position=beat_position,
            tempo_bpm=tempo,
            bar_number=bar,
            latencies=dict(self._latency_samples)
        )
        return self._sync.serialize()
    
    # -------------------------------------------------------------------------
    # Receiving
    # -------------------------------------------------------------------------
    
    def receive_audio(self, data: bytes) -> Tuple[int, Optional[bytes]]:
        """
        Receive audio from wire.
        
        Returns (spiral, samples) - samples may be None if still buffering.
        """
        frame = AudioFrame.deserialize(data)
        stream = self._get_stream(frame.spiral)
        
        self._frames_received += 1
        
        # Calculate latency
        now = int(time.time() * 1000) % (2**32)
        latency = (now - frame.timestamp_ms) % (2**32)
        if latency < 1000:  # Sanity check
            if frame.spiral not in self._latency_samples:
                self._latency_samples[frame.spiral] = []
            self._latency_samples[frame.spiral].append(latency)
            # Keep last 100 samples
            self._latency_samples[frame.spiral] = self._latency_samples[frame.spiral][-100:]
        
        samples = stream.receive(frame)
        return frame.spiral, samples
    
    def receive_sync(self, data: bytes) -> SyncSignal:
        """Receive sync signal"""
        self._sync = SyncSignal.deserialize(data)
        return self._sync
    
    # -------------------------------------------------------------------------
    # Sync & Timing
    # -------------------------------------------------------------------------
    
    def get_sync(self) -> SyncSignal:
        """Get current sync state"""
        return self._sync
    
    def get_latency(self, spiral: int) -> int:
        """Get estimated latency to a musician in ms"""
        samples = self._latency_samples.get(spiral, [])
        if not samples:
            return 0
        return sum(samples) // len(samples)
    
    def get_all_latencies(self) -> Dict[int, int]:
        """Get latencies to all musicians"""
        return {
            spiral: self.get_latency(spiral)
            for spiral in self._streams.keys()
        }
    
    def calculate_playback_offset(self, target_spiral: int) -> int:
        """
        Calculate how much to offset playback for a musician.
        
        This helps compensate for latency variations.
        If musician A has 30ms latency and B has 50ms,
        we might delay A's playback by 20ms so they align.
        """
        my_lat = self.get_latency(self.my_spiral)
        their_lat = self.get_latency(target_spiral)
        
        # Offset is the difference
        return max(0, their_lat - my_lat)
    
    # -------------------------------------------------------------------------
    # Stats
    # -------------------------------------------------------------------------
    
    @property
    def stats(self) -> Dict:
        all_latencies = self.get_all_latencies()
        avg_latency = sum(all_latencies.values()) // max(1, len(all_latencies)) if all_latencies else 0
        
        return {
            'my_spiral': self.my_spiral,
            'active_musicians': len(self._streams),
            'frames_sent': self._frames_sent,
            'frames_received': self._frames_received,
            'average_latency_ms': avg_latency,
            'latencies': all_latencies,
            'sync': {
                'time': self._sync.session_time_ms,
                'beat': self._sync.beat_position,
                'tempo': self._sync.tempo_bpm,
                'bar': self._sync.bar_number,
            }
        }


# =============================================================================
# LATENCY OPTIMIZER - Minimize processing overhead
# =============================================================================

class LatencyOptimizer:
    """
    Utilities for minimizing latency in audio transport.
    
    Tracks timing at each stage to identify bottlenecks.
    """
    
    def __init__(self):
        self._timings: Dict[str, List[float]] = {}
    
    def time(self, stage: str):
        """Context manager for timing a stage"""
        return _TimingContext(self, stage)
    
    def record(self, stage: str, duration_ms: float):
        """Record a timing"""
        if stage not in self._timings:
            self._timings[stage] = []
        self._timings[stage].append(duration_ms)
        # Keep last 1000
        self._timings[stage] = self._timings[stage][-1000:]
    
    def get_average(self, stage: str) -> float:
        """Get average time for a stage in ms"""
        times = self._timings.get(stage, [])
        return sum(times) / len(times) if times else 0
    
    def get_total(self) -> float:
        """Get total average processing time"""
        return sum(self.get_average(s) for s in self._timings)
    
    def report(self) -> str:
        """Generate timing report"""
        lines = ["Latency Breakdown:"]
        total = 0
        for stage, times in sorted(self._timings.items()):
            avg = sum(times) / len(times)
            total += avg
            lines.append(f"  {stage}: {avg:.3f} ms")
        lines.append(f"  TOTAL: {total:.3f} ms")
        return "\n".join(lines)


class _TimingContext:
    def __init__(self, optimizer: LatencyOptimizer, stage: str):
        self.optimizer = optimizer
        self.stage = stage
        self.start = None
    
    def __enter__(self):
        self.start = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        duration = (time.perf_counter() - self.start) * 1000
        self.optimizer.record(self.stage, duration)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'AudioLevel',
    'AUDIO_LEVEL_PRIORITY',
    'AudioFrame',
    'SyncSignal',
    'AudioStream',
    'AudioTransport',
    'LatencyOptimizer',
]
