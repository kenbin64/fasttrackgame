#!/usr/bin/env python3
"""
CSS Animation Video Capture
============================

Captures the CSS animation HTML page as an MP4 video using Playwright.
Renders 1280x720 at 30fps for 60 seconds.
"""

import asyncio
import os
import subprocess
import tempfile
import time

async def capture_css_animation():
    """Capture CSS animation as video frames"""
    from playwright.async_api import async_playwright
    
    print("=" * 60)
    print("ButterflyFX CSS ANIMATION VIDEO CAPTURE")
    print("=" * 60)
    print()
    
    # Paths
    html_path = "/opt/butterflyfx/dimensionsos/web/dimensional_promo.html"
    output_path = "/opt/butterflyfx/dimensionsos/demos/dimensional_promo.mp4"
    
    # Create temp directory for frames
    temp_dir = tempfile.mkdtemp(prefix='butterflyfx_css_')
    frames_dir = os.path.join(temp_dir, 'frames')
    os.makedirs(frames_dir)
    
    print(f"HTML: {html_path}")
    print(f"Temp: {temp_dir}")
    print(f"Output: {output_path}")
    print()
    
    WIDTH, HEIGHT = 1280, 720
    FPS = 30
    DURATION = 60
    TOTAL_FRAMES = FPS * DURATION
    
    print(f"Target: {WIDTH}x{HEIGHT} @ {FPS}fps, {DURATION}s ({TOTAL_FRAMES} frames)")
    print()
    
    async with async_playwright() as p:
        # Launch browser
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        
        # Create page with exact viewport
        page = await browser.new_page(viewport={'width': WIDTH, 'height': HEIGHT})
        
        # Load HTML
        print(f"Loading {html_path}...")
        await page.goto(f"file://{html_path}")
        
        # Wait for fonts to load
        await page.wait_for_timeout(2000)
        
        print("\nCapturing frames...")
        print("(This will take several minutes)")
        print()
        
        start_time = time.time()
        
        for frame_num in range(TOTAL_FRAMES):
            if frame_num % 90 == 0:
                pct = frame_num / TOTAL_FRAMES * 100
                elapsed = time.time() - start_time
                eta = (elapsed / (frame_num + 1)) * (TOTAL_FRAMES - frame_num) if frame_num > 0 else 0
                print(f"  Frame {frame_num}/{TOTAL_FRAMES} ({pct:.1f}%) - ETA: {eta:.0f}s")
            
            # Take screenshot
            frame_path = os.path.join(frames_dir, f'frame_{frame_num:05d}.png')
            await page.screenshot(path=frame_path)
            
            # Advance animation time by 1/30th second (33.33ms)
            # We do this by waiting real-time for CSS animations
            await page.wait_for_timeout(33)
        
        await browser.close()
    
    print(f"\nCaptured {TOTAL_FRAMES} frames")
    
    # Generate audio
    print("\nGenerating ambient audio...")
    import wave
    import struct
    import math
    
    audio_path = os.path.join(temp_dir, 'ambient.wav')
    sample_rate = 44100
    duration_samples = sample_rate * DURATION
    
    with wave.open(audio_path, 'w') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        
        for i in range(duration_samples):
            t = i / sample_rate
            
            # Ethereal ambient
            val = 0.2 * math.sin(2 * math.pi * 55 * t)
            val += 0.15 * math.sin(2 * math.pi * 110 * t * (1 + 0.002 * math.sin(0.3 * t)))
            val += 0.1 * math.sin(2 * math.pi * 220 * t)
            val += 0.08 * math.sin(2 * math.pi * 440 * t * (1 + 0.001 * math.sin(0.2 * t)))
            
            # Scene builds
            if 20 < t < 25:
                val *= 1 + (t - 20) / 5 * 0.3
            if 50 < t < 55:
                val *= 1 + (t - 50) / 5 * 0.4
            
            sample = int(val * 20000)
            sample = max(-32768, min(32767, sample))
            wav.writeframes(struct.pack('<hh', sample, sample))
    
    print(f"  Audio: {audio_path}")
    
    # Encode video
    print("\nEncoding video with ffmpeg...")
    
    result = subprocess.run([
        'ffmpeg', '-y',
        '-framerate', str(FPS),
        '-i', os.path.join(frames_dir, 'frame_%05d.png'),
        '-i', audio_path,
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
        '-c:a', 'aac', '-b:a', '192k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        output_path
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        size = os.path.getsize(output_path)
        print(f"\n✓ SUCCESS: {output_path}")
        print(f"  Size: {size / 1024 / 1024:.2f} MB")
    else:
        print(f"\nFFMPEG Error: {result.stderr}")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    print("\nTemp files cleaned up.")
    
    print("\n" + "=" * 60)
    print("VIDEO CAPTURE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(capture_css_animation())
