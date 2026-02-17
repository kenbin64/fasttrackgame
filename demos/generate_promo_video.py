#!/usr/bin/env python3
"""
ButterflyFX Promotional Video Generator
========================================

Uses the AI Substrate to orchestrate all other substrates and
generate a 1-minute promotional video with:
- 3D animated visuals (spinning helix, substrate layers)
- Ambient electronic music 
- Voice narration
- Spectral color narrative

This demonstrates the power of substrate composition.
"""

import os
import sys
import math
import struct
import wave
import subprocess
import tempfile
from pathlib import Path

# Setup environment
os.environ["BUTTERFLYFX_DEV"] = "1"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helix.kernel_primitives import (
    RGB, RGBA, Vector2D, Vector3D, Matrix4x4,
    Frequency, Duration
)
from helix.packages.media_pkg import FrameSubstrate, AudioSubstrate, VideoSubstrate
from helix.packages.ai_substrate import get_ai


# ============================================================
# VIDEO CONFIGURATION
# ============================================================

WIDTH = 1280
HEIGHT = 720
FPS = 30
DURATION = 60  # seconds

# Colors - ButterflyFX brand palette
COLOR_BG_START = RGB(15, 20, 35)      # Deep space blue
COLOR_BG_END = RGB(40, 30, 60)        # Deep purple
COLOR_HELIX_1 = RGB(255, 120, 80)     # Warm orange
COLOR_HELIX_2 = RGB(80, 200, 255)     # Electric cyan  
COLOR_ACCENT = RGB(255, 200, 100)     # Golden glow
COLOR_TEXT = RGB(255, 255, 255)       # White

# Narration script (will be synthesized to speech)
NARRATION_SCRIPT = [
    (0, "ButterflyFX"),
    (3, "A new paradigm in creative computing"),
    (8, "Where everything is a substrate"),
    (13, "Colors derive from wavelengths of light"),
    (18, "Sound emerges from fundamental frequencies"),
    (23, "Geometry flows from mathematical transformations"),
    (28, "The kernel is free, open, and universal"),
    (33, "Build anything by composing substrates"),
    (38, "Video, audio, 3D graphics, artificial intelligence"),
    (43, "All connected through a unified addressing system"),
    (48, "ButterflyFX. Create without limits."),
    (55, ""),
]


def lerp(a, b, t):
    """Linear interpolation"""
    return a + (b - a) * max(0, min(1, t))


def ease_in_out(t):
    """Smooth ease in/out"""
    return t * t * (3 - 2 * t)


def create_gradient_frame(frame_sub, frame, t):
    """Create animated gradient background"""
    # Time-based color shift
    shift = math.sin(t * 0.5) * 0.3
    
    c1 = RGB(
        int(lerp(COLOR_BG_START.r, COLOR_BG_END.r, 0.5 + shift)),
        int(lerp(COLOR_BG_START.g, COLOR_BG_END.g, 0.5 + shift)),
        int(lerp(COLOR_BG_START.b, COLOR_BG_END.b, 0.5 + shift))
    )
    c2 = RGB(
        int(lerp(COLOR_BG_END.r, COLOR_BG_START.r, 0.5 + shift)),
        int(lerp(COLOR_BG_END.g, COLOR_BG_START.g, 0.5 + shift)),
        int(lerp(COLOR_BG_END.b, COLOR_BG_START.b, 0.5 + shift))
    )
    
    frame_sub.gradient_fill(frame, c1, c2)


def draw_helix_3d(frame_sub, frame, t, cx, cy, radius, num_turns=3):
    """Draw a 3D double helix rotating in time"""
    rotation = t * 0.8  # Rotation speed
    
    for i in range(200):
        angle = (i / 200) * math.pi * 2 * num_turns + rotation
        z = (i / 200) * 2 - 1  # -1 to 1
        
        # Helix strand 1
        x1 = math.cos(angle) * radius
        y1 = math.sin(angle) * radius * 0.5 + z * radius * 0.8
        
        # Helix strand 2 (opposite)
        x2 = math.cos(angle + math.pi) * radius
        y2 = math.sin(angle + math.pi) * radius * 0.5 + z * radius * 0.8
        
        # Project to screen (simple perspective)
        depth = (math.sin(angle) + 1) * 0.5 + 0.3
        
        # Screen coordinates
        sx1 = int(cx + x1 * depth)
        sy1 = int(cy + y1 * depth)
        sx2 = int(cx + x2 * depth)
        sy2 = int(cy + y2 * depth)
        
        # Colors based on depth and position
        c1 = RGB(
            int(COLOR_HELIX_1.r * depth),
            int(COLOR_HELIX_1.g * depth),
            int(COLOR_HELIX_1.b * depth)
        )
        c2 = RGB(
            int(COLOR_HELIX_2.r * depth),
            int(COLOR_HELIX_2.g * depth),
            int(COLOR_HELIX_2.b * depth)
        )
        
        # Draw points with glow effect
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if 0 <= sx1+dx < WIDTH and 0 <= sy1+dy < HEIGHT:
                    frame.set_pixel(sx1+dx, sy1+dy, c1)
                if 0 <= sx2+dx < WIDTH and 0 <= sy2+dy < HEIGHT:
                    frame.set_pixel(sx2+dx, sy2+dy, c2)


def draw_spectral_ring(frame_sub, frame, t, cx, cy, radius):
    """Draw a spectral ring showing wavelength-to-color derivation"""
    for angle_deg in range(360):
        angle = math.radians(angle_deg) + t * 0.3
        
        # Map angle to visible spectrum wavelength (380nm - 780nm)
        wavelength = 380 + (angle_deg / 360) * 400
        color = RGBA.from_wavelength(wavelength)
        
        x = int(cx + math.cos(angle) * radius)
        y = int(cy + math.sin(angle) * radius)
        
        # Draw thick line
        for r in range(-3, 4):
            px = int(cx + math.cos(angle) * (radius + r))
            py = int(cy + math.sin(angle) * (radius + r))
            if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                frame.set_pixel(px, py, RGB(color.r, color.g, color.b))


def draw_particles(frame_sub, frame, t, num_particles=50):
    """Draw floating particle effect"""
    import random
    random.seed(42)  # Consistent particles
    
    for i in range(num_particles):
        # Each particle has its own path
        px = random.random()
        py = random.random() 
        speed = 0.2 + random.random() * 0.3
        
        x = int((px + t * speed * 0.1) % 1 * WIDTH)
        y = int((py + math.sin(t + px * 10) * 0.05) * HEIGHT)
        
        brightness = int(150 + 105 * math.sin(t * 2 + i))
        color = RGB(brightness, brightness//2, brightness)
        
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            frame.set_pixel(x, y, color)


def draw_text_glow(frame_sub, frame, text, cx, cy, t):
    """Simple text indication (just a glowing area where text would be)"""
    if not text:
        return
    
    # Create a glowing area proportional to text length
    width = min(len(text) * 20, WIDTH - 100)
    height = 40
    
    fade = ease_in_out(min(1, t * 2))
    
    for dx in range(-width//2, width//2):
        for dy in range(-height//2, height//2):
            x = cx + dx
            y = cy + dy
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                dist = abs(dy) / (height / 2)
                brightness = int((1 - dist) * 80 * fade)
                if brightness > 20:  # Only draw if visible
                    color = RGB(
                        min(255, int(COLOR_TEXT.r * 0.2 + brightness)),
                        min(255, int(COLOR_TEXT.g * 0.2 + brightness)),
                        min(255, int(COLOR_TEXT.b * 0.2 + brightness))
                    )
                    frame.set_pixel(x, y, color)


def generate_ambient_music(audio_sub, duration):
    """Generate ambient electronic music"""
    print("  Generating ambient music...")
    
    # Base frequencies for ambient pad
    base_freqs = [
        Frequency(110),   # A2
        Frequency(165),   # E3
        Frequency(220),   # A3
        Frequency(277.2), # C#4
        Frequency(330),   # E4
    ]
    
    # Generate layered ambient sound
    samples = []
    sample_rate = audio_sub.sample_rate
    num_samples = int(sample_rate * duration)
    
    for i in range(num_samples):
        t = i / sample_rate
        sample = 0.0
        
        # Layer 1: Deep bass drone
        sample += 0.2 * math.sin(2 * math.pi * 55 * t + math.sin(t * 0.5) * 0.5)
        
        # Layer 2: Pad harmony
        for j, freq in enumerate(base_freqs):
            mod = math.sin(t * 0.3 + j) * 0.3
            sample += 0.08 * math.sin(2 * math.pi * freq.hz * t * (1 + mod * 0.01))
        
        # Layer 3: High shimmer
        shimmer_freq = 880 + math.sin(t * 2) * 100
        sample += 0.05 * math.sin(2 * math.pi * shimmer_freq * t)
        
        # Apply envelope
        fade_in = min(1, t / 3)
        fade_out = min(1, (duration - t) / 3)
        envelope = fade_in * fade_out
        
        # Subtle modulation
        modulation = 0.8 + 0.2 * math.sin(t * 0.1)
        
        sample *= envelope * modulation * 0.6
        samples.append(sample)
    
    return samples


def generate_voice_narration(duration):
    """Generate voice narration using gTTS"""
    print("  Generating voice narration...")
    
    try:
        from gtts import gTTS
        from pydub import AudioSegment
        import io
        
        # Create segments for each narration line
        narration_segments = []
        
        for start_time, text in NARRATION_SCRIPT:
            if not text:
                continue
            print(f"    - '{text}'")
            tts = gTTS(text=text, lang='en', slow=False)
            audio_bytes = io.BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            segment = AudioSegment.from_mp3(audio_bytes)
            narration_segments.append((start_time, segment))
        
        # Create silence base track
        silence = AudioSegment.silent(duration=duration * 1000)
        
        # Overlay narration at correct times
        for start_time, segment in narration_segments:
            silence = silence.overlay(segment, position=start_time * 1000)
        
        # Convert to samples
        silence = silence.set_channels(1).set_sample_width(2).set_frame_rate(44100)
        samples = []
        raw = silence.raw_data
        for i in range(0, len(raw), 2):
            if i + 1 < len(raw):
                value = struct.unpack('<h', raw[i:i+2])[0]
                samples.append(value / 32768.0)
        
        return samples
    except Exception as e:
        print(f"    Voice generation error: {e}")
        return [0.0] * (44100 * duration)


def mix_audio(music_samples, voice_samples, music_volume=0.4, voice_volume=0.7):
    """Mix music and voice tracks"""
    print("  Mixing audio tracks...")
    
    # Ensure same length
    max_len = max(len(music_samples), len(voice_samples))
    
    music_samples = music_samples + [0.0] * (max_len - len(music_samples))
    voice_samples = voice_samples + [0.0] * (max_len - len(voice_samples))
    
    mixed = []
    for i in range(max_len):
        sample = music_samples[i] * music_volume + voice_samples[i] * voice_volume
        # Soft clip
        sample = max(-1.0, min(1.0, sample))
        mixed.append(sample)
    
    return mixed


def samples_to_wav(samples, filepath, sample_rate=44100):
    """Write samples to WAV file"""
    with wave.open(filepath, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        
        for sample in samples:
            value = int(max(-32768, min(32767, sample * 32767)))
            wav.writeframes(struct.pack('<h', value))


def render_video():
    """Main video rendering function"""
    print("=" * 60)
    print("ButterflyFX PROMOTIONAL VIDEO GENERATOR")
    print("=" * 60)
    
    # Get AI to orchestrate
    ai = get_ai()
    plan = ai.generate_promo_plan()
    print(f"\nAI Plan: {plan.goal}")
    print(f"Confidence: {plan.confidence:.0%}")
    print(f"Substrates: {', '.join(plan.substrates_used)}")
    print()
    
    # Initialize substrates
    frame_sub = FrameSubstrate(WIDTH, HEIGHT)
    audio_sub = AudioSubstrate()
    video_sub = VideoSubstrate()
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="butterflyfx_")
    frames_dir = os.path.join(temp_dir, "frames")
    os.makedirs(frames_dir)
    
    print(f"Temp directory: {temp_dir}")
    print(f"Target: {WIDTH}x{HEIGHT} @ {FPS}fps, {DURATION}s")
    print()
    
    # Step 1: Generate frames
    print("STEP 1: Generating video frames...")
    total_frames = FPS * DURATION
    
    # Find current narration text for each frame
    def get_narration_text(t):
        current_text = ""
        for start, text in NARRATION_SCRIPT:
            if t >= start:
                current_text = text
            else:
                break
        return current_text
    
    try:
        from PIL import Image
        has_pil = True
    except:
        has_pil = False
    
    for frame_num in range(total_frames):
        t = frame_num / FPS
        
        # Create frame
        frame = frame_sub.create_frame(t)
        
        # Layer 1: Animated gradient background
        create_gradient_frame(frame_sub, frame, t)
        
        # Layer 2: Spectral ring (showing wavelength derivation)
        ring_radius = 150 + 30 * math.sin(t * 0.5)
        draw_spectral_ring(frame_sub, frame, t, WIDTH//2, HEIGHT//2, ring_radius)
        
        # Layer 3: 3D Helix
        helix_radius = 100 + 20 * math.sin(t * 0.3)
        draw_helix_3d(frame_sub, frame, t, WIDTH//2, HEIGHT//2, helix_radius)
        
        # Layer 4: Particles
        draw_particles(frame_sub, frame, t)
        
        # Layer 5: Text glow
        text = get_narration_text(t)
        draw_text_glow(frame_sub, frame, text, WIDTH//2, HEIGHT - 100, t)
        
        # Save frame
        frame_path = os.path.join(frames_dir, f"frame_{frame_num:05d}.png")
        
        if has_pil:
            img = frame.to_pil()
            img.save(frame_path)
        else:
            # Fallback: just save as raw
            frame_path = frame_path.replace('.png', '.raw')
            with open(frame_path, 'wb') as f:
                for y in range(HEIGHT):
                    for x in range(WIDTH):
                        c = frame.get_pixel(x, y)
                        f.write(bytes([c.r, c.g, c.b]))
        
        if frame_num % (FPS * 5) == 0:
            print(f"  Frame {frame_num}/{total_frames} ({t:.0f}s)")
    
    print(f"  Generated {total_frames} frames")
    
    # Step 2: Generate audio
    print("\nSTEP 2: Generating audio...")
    music = generate_ambient_music(audio_sub, DURATION)
    voice = generate_voice_narration(DURATION)
    mixed = mix_audio(music, voice)
    
    audio_path = os.path.join(temp_dir, "audio.wav")
    samples_to_wav(mixed, audio_path)
    print(f"  Audio saved: {audio_path}")
    
    # Step 3: Encode video with ffmpeg
    print("\nSTEP 3: Encoding video with ffmpeg...")
    output_path = "/opt/butterflyfx/dimensionsos/demos/butterflyfx_promo.mp4"
    
    # Ensure demos directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if has_pil:
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", os.path.join(frames_dir, "frame_%05d.png"),
            "-i", audio_path,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_path
        ]
    else:
        # For raw frames, need different approach
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo",
            "-pixel_format", "rgb24",
            "-video_size", f"{WIDTH}x{HEIGHT}",
            "-framerate", str(FPS),
            "-i", os.path.join(frames_dir, "frame_%05d.raw"),
            "-i", audio_path,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_path
        ]
    
    print(f"  Running: {' '.join(ffmpeg_cmd[:5])}...")
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"\n{'=' * 60}")
        print("VIDEO GENERATION COMPLETE!")
        print(f"{'=' * 60}")
        print(f"Output: {output_path}")
        
        # Get file size
        size = os.path.getsize(output_path)
        print(f"Size: {size / (1024*1024):.1f} MB")
        print(f"Duration: {DURATION}s")
        print(f"Resolution: {WIDTH}x{HEIGHT}")
        print(f"FPS: {FPS}")
    else:
        print(f"  ffmpeg error: {result.stderr[:500]}")
    
    # Cleanup
    print("\nCleaning up temp files...")
    import shutil
    shutil.rmtree(temp_dir)
    print("Done!")
    
    return output_path


if __name__ == "__main__":
    render_video()
