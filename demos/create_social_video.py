#!/usr/bin/env python3
"""
ButterflyFX Social Media Video Generator
Creates a 30-second promotional MP4 video
"""

import os
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont
import tempfile
import shutil

# Configuration
WIDTH = 1080
HEIGHT = 1080  # Square for Instagram/social
FPS = 30
DURATION = 30  # seconds
TOTAL_FRAMES = FPS * DURATION

# Colors (from ButterflyFX palette)
BG_COLOR = (5, 5, 8)
NEON_PURPLE = (136, 85, 255)
NEON_PINK = (255, 85, 170)
NEON_CYAN = (64, 255, 255)
WHITE = (255, 255, 255)
TEXT_DIM = (160, 168, 192)

# Paths
LOGO_PATH = "/opt/butterflyfx/dimensionsos/web/static/image/butterflyLogo.png"
OUTPUT_PATH = "/opt/butterflyfx/dimensionsos/demos/butterflyfx_promo.mp4"

def lerp(a, b, t):
    """Linear interpolation"""
    return a + (b - a) * t

def ease_in_out(t):
    """Ease in-out function"""
    return t * t * (3 - 2 * t)

def ease_out(t):
    """Ease out function"""
    return 1 - (1 - t) ** 3

def draw_star(draw, cx, cy, size, alpha, color):
    """Draw a glowing star"""
    r, g, b = color
    a = int(alpha * 255)
    for i in range(3, 0, -1):
        s = size * i / 3
        c = (r, g, b, int(a * (4-i) / 3))
        draw.ellipse([cx-s, cy-s, cx+s, cy+s], fill=c[:3])

def draw_manifold_point(draw, x, y, z, alpha, frame, width, height):
    """Draw a point on the z=xy manifold"""
    # Rotate around Y axis
    angle = frame * 0.02
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    # Rotate x and z
    rx = x * cos_a - z * sin_a
    rz = x * sin_a + z * cos_a
    
    # Perspective projection
    perspective = 3 / (3 + rz * 0.5)
    px = width // 2 + int(rx * 100 * perspective)
    py = height // 2 - int(y * 100 * perspective) + 50
    
    size = max(2, int(4 * perspective))
    
    # Color based on z value
    hue = 260 + z * 30
    r = int(136 + z * 20)
    g = int(85 + abs(z) * 10)
    b = int(255 - abs(z) * 10)
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    
    a = int(alpha * (0.5 + perspective * 0.5) * 255)
    draw.ellipse([px-size, py-size, px+size, py+size], fill=(r, g, b))

def create_frame(frame_num, logo_img, font_large, font_medium, font_small, temp_dir):
    """Create a single frame of the video"""
    img = Image.new('RGBA', (WIDTH, HEIGHT), BG_COLOR + (255,))
    draw = ImageDraw.Draw(img)
    
    t = frame_num / TOTAL_FRAMES  # 0 to 1 over entire video
    
    # === SCENE TIMING ===
    # 0-3s: Logo fade in with stars
    # 3-8s: Logo + tagline appears
    # 8-15s: Manifold animation appears
    # 15-22s: Key messages cycle
    # 22-28s: URL appears prominently
    # 28-30s: Final logo + URL
    
    scene_time = frame_num / FPS  # time in seconds
    
    # Draw animated starfield background
    for i in range(50):
        seed = i * 1337 + 42
        sx = (seed * 7919) % WIDTH
        sy = (seed * 6271) % HEIGHT
        sz = ((seed * 3571 + frame_num * 2) % 1000) / 1000
        star_alpha = sz * 0.5
        star_size = 1 + sz * 2
        
        # Move stars toward viewer
        perspective = 1 + sz
        sx_moved = WIDTH // 2 + int((sx - WIDTH // 2) * perspective)
        sy_moved = HEIGHT // 2 + int((sy - HEIGHT // 2) * perspective)
        
        if 0 <= sx_moved < WIDTH and 0 <= sy_moved < HEIGHT:
            c = int(100 + star_alpha * 155)
            draw.ellipse([sx_moved-star_size, sy_moved-star_size, 
                         sx_moved+star_size, sy_moved+star_size], 
                        fill=(c, c, int(c*1.2)))
    
    # === LOGO ===
    logo_alpha = 0
    if scene_time < 3:
        # Fade in
        logo_alpha = ease_out(scene_time / 3)
    elif scene_time < 28:
        logo_alpha = 1.0
    else:
        # Slight pulse at end
        logo_alpha = 0.9 + 0.1 * math.sin(scene_time * 5)
    
    if logo_alpha > 0:
        # Position logo
        if scene_time < 8:
            logo_y = HEIGHT // 2 - 100  # Center
        else:
            logo_y = 100  # Top
        
        logo_size = int(200 * logo_alpha)
        if logo_size > 0:
            resized_logo = logo_img.resize((logo_size, logo_size), Image.LANCZOS)
            logo_x = (WIDTH - logo_size) // 2
            
            # Apply alpha
            if resized_logo.mode != 'RGBA':
                resized_logo = resized_logo.convert('RGBA')
            
            # Paste with alpha
            img.paste(resized_logo, (logo_x, logo_y), resized_logo)
    
    # === TAGLINE (3-8s) ===
    if 3 <= scene_time < 27:
        tagline_alpha = min(1, (scene_time - 3) / 1)
        if scene_time > 22:
            tagline_alpha = max(0, 1 - (scene_time - 22) / 2)
        
        if tagline_alpha > 0:
            tagline = "Dimensional Computing"
            c = int(255 * tagline_alpha)
            try:
                bbox = draw.textbbox((0, 0), tagline, font=font_large)
                tw = bbox[2] - bbox[0]
                if scene_time < 8:
                    ty = HEIGHT // 2 + 120
                else:
                    ty = 320
                draw.text(((WIDTH - tw) // 2, ty), tagline, fill=(c, c, c), font=font_large)
            except:
                draw.text((WIDTH // 2 - 150, HEIGHT // 2 + 120), tagline, fill=(c, c, c))
    
    # === MANIFOLD ANIMATION (8-22s) ===
    if 8 <= scene_time < 22:
        manifold_alpha = min(1, (scene_time - 8) / 2)
        if scene_time > 20:
            manifold_alpha = max(0, 1 - (scene_time - 20) / 2)
        
        if manifold_alpha > 0:
            # Draw z=xy point cloud
            points = 15
            for i in range(points):
                for j in range(points):
                    x = (i / points - 0.5) * 3
                    y = (j / points - 0.5) * 3
                    z = x * y * 0.5
                    draw_manifold_point(draw, x, y, z, manifold_alpha, frame_num, WIDTH, HEIGHT)
    
    # === KEY MESSAGES (10-22s) ===
    messages = [
        ("Shapes Hold Data", 10, 13),
        ("O(7) Per Spiral", 13, 16),
        ("No Iteration", 16, 19),
        ("Identity First", 19, 22),
    ]
    
    for msg, start, end in messages:
        if start <= scene_time < end:
            msg_t = (scene_time - start) / (end - start)
            if msg_t < 0.2:
                alpha = ease_out(msg_t / 0.2)
            elif msg_t > 0.8:
                alpha = ease_out((1 - msg_t) / 0.2)
            else:
                alpha = 1.0
            
            c = int(alpha * 255)
            # Purple-pink gradient text
            try:
                bbox = draw.textbbox((0, 0), msg, font=font_medium)
                tw = bbox[2] - bbox[0]
                draw.text(((WIDTH - tw) // 2, HEIGHT - 300), msg, 
                         fill=(int(136 * alpha), int(85 * alpha), int(255 * alpha)), 
                         font=font_medium)
            except:
                draw.text((WIDTH // 2 - 100, HEIGHT - 300), msg, 
                         fill=(int(136 * alpha), int(85 * alpha), int(255 * alpha)))
    
    # === URL (22-30s) ===
    if scene_time >= 22:
        url_alpha = min(1, (scene_time - 22) / 1.5)
        
        url = "butterflyfx.us"
        c = int(url_alpha * 255)
        try:
            bbox = draw.textbbox((0, 0), url, font=font_large)
            tw = bbox[2] - bbox[0]
            
            # Glowing effect
            for offset in [3, 2, 1]:
                glow_c = int(c * 0.3)
                draw.text(((WIDTH - tw) // 2 + offset, HEIGHT // 2 + 50 + offset), url, 
                         fill=(glow_c, int(glow_c * 0.5), glow_c), font=font_large)
            
            draw.text(((WIDTH - tw) // 2, HEIGHT // 2 + 50), url, 
                     fill=(int(64 * url_alpha), int(255 * url_alpha), int(255 * url_alpha)), 
                     font=font_large)
        except:
            draw.text((WIDTH // 2 - 100, HEIGHT // 2 + 50), url, fill=(64, c, c))
    
    # === CALL TO ACTION (25-30s) ===
    if scene_time >= 25:
        cta_alpha = min(1, (scene_time - 25) / 1)
        cta = "Experience the Future"
        c = int(cta_alpha * 200)
        try:
            bbox = draw.textbbox((0, 0), cta, font=font_small)
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw) // 2, HEIGHT // 2 + 150), cta, fill=(c, c, c), font=font_small)
        except:
            draw.text((WIDTH // 2 - 80, HEIGHT // 2 + 150), cta, fill=(c, c, c))
    
    # Convert to RGB for video
    img = img.convert('RGB')
    
    # Save frame
    frame_path = os.path.join(temp_dir, f"frame_{frame_num:05d}.png")
    img.save(frame_path, 'PNG')
    return frame_path

def main():
    print("🦋 ButterflyFX Social Video Generator")
    print("=" * 40)
    
    # Load logo
    print("Loading logo...")
    try:
        logo_img = Image.open(LOGO_PATH)
        print(f"  Logo loaded: {logo_img.size}")
    except Exception as e:
        print(f"  Error loading logo: {e}")
        # Create placeholder
        logo_img = Image.new('RGBA', (200, 200), NEON_PURPLE + (255,))
        draw = ImageDraw.Draw(logo_img)
        draw.text((50, 90), "🦋", fill=WHITE)
    
    # Load fonts
    print("Loading fonts...")
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        print("  Fonts loaded successfully")
    except:
        print("  Using default fonts")
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Create temp directory for frames
    temp_dir = tempfile.mkdtemp(prefix="butterflyfx_video_")
    print(f"Temp directory: {temp_dir}")
    
    try:
        # Generate frames
        print(f"\nGenerating {TOTAL_FRAMES} frames...")
        for i in range(TOTAL_FRAMES):
            create_frame(i, logo_img, font_large, font_medium, font_small, temp_dir)
            if (i + 1) % 30 == 0:
                print(f"  Progress: {i + 1}/{TOTAL_FRAMES} ({(i + 1) * 100 // TOTAL_FRAMES}%)")
        
        print("\nEncoding video with ffmpeg...")
        
        # Use ffmpeg to create video
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',  # Overwrite output
            '-framerate', str(FPS),
            '-i', os.path.join(temp_dir, 'frame_%05d.png'),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            OUTPUT_PATH
        ]
        
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"\n✅ Video created successfully!")
            print(f"   Output: {OUTPUT_PATH}")
            
            # Get file size
            size = os.path.getsize(OUTPUT_PATH)
            print(f"   Size: {size / 1024 / 1024:.2f} MB")
        else:
            print(f"\n❌ Error creating video:")
            print(result.stderr)
    
    finally:
        # Clean up temp directory
        print(f"\nCleaning up temp files...")
        shutil.rmtree(temp_dir)
    
    print("\n🦋 Done!")

if __name__ == "__main__":
    main()
