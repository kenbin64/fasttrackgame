#!/usr/bin/env python3
"""
ButterflyFX Cinematic Promotional Video Generator
==================================================

Creates a 1-minute cinematic promo with:
- Dark void opening to geometric butterfly
- Dimensional grid erupting outward
- Substrates/identities aligning
- Butterfly flying through crystalline lattice
- Final logo formation from pure light

Uses AI Substrate for orchestration.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import subprocess
import tempfile
import math
import wave
import struct

# ============================================================================
# NARRATION SCRIPT WITH TIMINGS
# ============================================================================

NARRATION = [
    # (start_sec, end_sec, text, visual_mode)
    (0, 8, 
     "In a world drowning in data, we've been taught to compute harder, faster, louder. But what if the future isn't more computation at all?",
     "void_pulse"),
    
    (8, 16,
     "What if the universe has always been organized, not by machines, but by geometry?",
     "butterfly_unfold"),
    
    (16, 28,
     "ButterflyFx introduces Dimensional Computing. A new physics for information. Not stored. Not duplicated. Not lost. Observed.",
     "grid_eruption"),
    
    (28, 38,
     "One fingerprint for every idea. One reference for every truth. Instant clarity across every dimension of your digital life.",
     "substrate_align"),
    
    (38, 48,
     "This isn't an upgrade. It's a new era. A new operating system for reality itself.",
     "butterfly_flight"),
    
    (48, 60,
     "ButterflyFx. Dimensional Computing. The future doesn't compute. It unfolds.",
     "logo_formation"),
]

# ============================================================================
# VISUAL CONSTANTS
# ============================================================================

WIDTH, HEIGHT = 1280, 720
FPS = 30
DURATION = 60
TOTAL_FRAMES = FPS * DURATION
CX, CY = WIDTH // 2, HEIGHT // 2

# Color palette
VOID = (5, 5, 15)
GOLD = (255, 200, 80)
CYAN = (80, 220, 255)
PURPLE = (180, 100, 255)
WHITE = (255, 255, 255)
BUTTERFLY_GOLD = (255, 180, 50)

# ============================================================================
# GEOMETRIC PRIMITIVES (from ButterflyFX Kernel!)
# ============================================================================

def ease_in_out(t):
    """Smooth easing function"""
    return t * t * (3 - 2 * t)

def lerp(a, b, t):
    """Linear interpolation"""
    return a + (b - a) * t

def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB"""
    h = h % 1.0
    i = int(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    
    cases = [
        (v, t, p), (q, v, p), (p, v, t),
        (p, q, v), (t, p, v), (v, p, q)
    ]
    r, g, b = cases[i % 6]
    return (int(r * 255), int(g * 255), int(b * 255))

# ============================================================================
# VISUAL EFFECTS
# ============================================================================

def draw_void_pulse(draw, arr, t, progress):
    """Dark void with single glowing pulse point"""
    # Breathing pulse
    pulse_size = 20 + 30 * math.sin(t * 3) ** 2
    pulse_alpha = 0.5 + 0.5 * math.sin(t * 2)
    
    # Radial glow
    for r in range(int(pulse_size), 0, -1):
        alpha = (1 - r / pulse_size) * pulse_alpha
        color = tuple(int(c * alpha) for c in GOLD)
        draw.ellipse([CX - r, CY - r, CX + r, CY + r], fill=color)
    
    # Core point
    core_size = 5 + 3 * math.sin(t * 5)
    draw.ellipse([CX - core_size, CY - core_size, CX + core_size, CY + core_size], 
                 fill=WHITE)
    
    # Subtle particle trails emerging
    if progress > 0.5:
        for i in range(8):
            angle = i * math.pi / 4 + t * 0.5
            dist = (progress - 0.5) * 2 * 100
            x = CX + math.cos(angle) * dist
            y = CY + math.sin(angle) * dist
            size = 2 + math.sin(t * 4 + i) * 1
            alpha = 1 - (progress - 0.5) * 2
            color = tuple(int(c * alpha) for c in GOLD)
            draw.ellipse([x - size, y - size, x + size, y + size], fill=color)


def draw_butterfly_unfold(draw, arr, t, progress):
    """Geometric butterfly unfolding from point"""
    # Wing parameters
    wing_unfold = ease_in_out(min(1, progress * 1.5))
    beat = math.sin(t * 4) * 0.2 * wing_unfold
    
    # Draw both wings
    for side in [-1, 1]:
        # Wing made of mathematical curves (golden ratio spirals)
        points = []
        for i in range(60):
            angle = i * 0.1 * wing_unfold
            # Golden spiral
            phi = 1.618
            r = 10 * (phi ** (angle / (2 * math.pi)))
            r = min(r, 150 * wing_unfold)
            
            # Wing shape modulation
            wing_mod = math.sin(angle * 2) * 0.3 + 0.7
            r *= wing_mod
            
            # Beat animation
            y_offset = beat * r * 0.5
            
            x = CX + side * math.cos(angle + side * 0.2) * r
            y = CY + math.sin(angle) * r * 0.6 + y_offset - 20
            points.append((x, y))
        
        # Draw wing with gradient
        if len(points) > 2:
            for i in range(len(points) - 1):
                hue = 0.1 + i / len(points) * 0.15  # Gold to orange
                color = hsv_to_rgb(hue, 0.8, 1.0)
                draw.line([points[i], points[i + 1]], fill=color, width=3)
    
    # Body
    body_len = 40 * wing_unfold
    draw.line([CX, CY - body_len, CX, CY + body_len], fill=GOLD, width=4)
    
    # Antennae
    if wing_unfold > 0.5:
        for side in [-1, 1]:
            draw.line([CX, CY - body_len, 
                      CX + side * 20, CY - body_len - 25], 
                     fill=GOLD, width=2)
    
    # Glow particles
    for i in range(12):
        angle = i * math.pi / 6 + t
        dist = 80 + 40 * math.sin(t * 2 + i)
        x = CX + math.cos(angle) * dist
        y = CY + math.sin(angle) * dist * 0.6 - 20
        size = 2 + math.sin(t * 3 + i) * 1
        draw.ellipse([x - size, y - size, x + size, y + size], fill=CYAN)


def draw_grid_eruption(draw, arr, t, progress):
    """Dimensional grid erupting outward"""
    # Grid expansion
    expansion = ease_in_out(min(1, progress * 1.2))
    rotation = t * 0.3
    
    # Draw crystalline grid layers
    for layer in range(5):
        layer_offset = layer * 0.2
        layer_alpha = 1 - layer * 0.15
        z_depth = 1 + layer * 0.5
        
        # Grid lines
        grid_size = int(200 * expansion / z_depth)
        spacing = 40
        
        for i in range(-6, 7):
            # Vertical lines
            x_base = i * spacing
            # Rotate
            x = x_base * math.cos(rotation) * expansion
            z = x_base * math.sin(rotation) * 0.3
            
            # Perspective
            scale = 1 / (1 + z * 0.005)
            x_screen = CX + x * scale
            
            # Draw line with depth fade
            alpha = max(0.2, layer_alpha * scale)
            color = tuple(int(c * alpha) for c in CYAN)
            draw.line([x_screen, CY - grid_size, x_screen, CY + grid_size], 
                     fill=color, width=1)
        
        for j in range(-4, 5):
            # Horizontal lines
            y_base = j * spacing
            y = y_base * expansion
            
            alpha = max(0.2, layer_alpha)
            color = tuple(int(c * alpha) for c in CYAN)
            draw.line([CX - grid_size, CY + y, CX + grid_size, CY + y], 
                     fill=color, width=1)
    
    # Grid intersection points glow
    for i in range(-5, 6):
        for j in range(-3, 4):
            x = i * 50 * expansion
            y = j * 50 * expansion
            
            # Rotate
            rx = x * math.cos(rotation) - y * math.sin(rotation) * 0.3
            ry = x * math.sin(rotation) * 0.3 + y * math.cos(rotation) * 0.5
            
            px = int(CX + rx)
            py = int(CY + ry)
            
            # Pulse effect
            pulse = math.sin(t * 4 + i * 0.5 + j * 0.5) * 0.5 + 0.5
            size = 3 + pulse * 2
            
            # Color based on position
            hue = 0.5 + i * 0.02 + j * 0.02
            color = hsv_to_rgb(hue, 0.6, 0.8 + pulse * 0.2)
            
            draw.ellipse([px - size, py - size, px + size, py + size], fill=color)
    
    # Butterfly silhouette in center
    if progress > 0.3:
        bf_scale = (progress - 0.3) / 0.7
        draw_mini_butterfly(draw, CX, CY - 30, bf_scale * 0.4, t)


def draw_mini_butterfly(draw, cx, cy, scale, t):
    """Small butterfly helper"""
    beat = math.sin(t * 6) * 0.1
    wing_span = 60 * scale
    
    for side in [-1, 1]:
        # Wing curves
        points = []
        for i in range(20):
            angle = i * 0.15
            r = wing_span * math.sin(angle * 2) * (1 + beat * side)
            x = cx + side * r * math.cos(angle * 0.5)
            y = cy + r * math.sin(angle * 0.5) * 0.4
            points.append((x, y))
        
        if len(points) > 2:
            for i in range(len(points) - 1):
                draw.line([points[i], points[i + 1]], fill=GOLD, width=2)
    
    draw.ellipse([cx - 3, cy - 15 * scale, cx + 3, cy + 15 * scale], fill=GOLD)


def draw_substrate_align(draw, arr, t, progress):
    """Substrates and identities snapping into alignment"""
    # Floating substrate cards
    num_cards = 12
    
    for i in range(num_cards):
        # Initial chaotic positions
        chaos = 1 - ease_in_out(min(1, progress * 1.5))
        
        # Target position (circular arrangement)
        target_angle = i * 2 * math.pi / num_cards
        target_r = 180
        target_x = CX + math.cos(target_angle) * target_r
        target_y = CY + math.sin(target_angle) * target_r * 0.5
        
        # Chaotic position
        chaos_x = CX + math.cos(i * 1.7 + t * 0.5) * 300 * chaos
        chaos_y = CY + math.sin(i * 2.3 + t * 0.3) * 200 * chaos
        
        # Interpolate
        x = lerp(chaos_x, target_x, 1 - chaos)
        y = lerp(chaos_y, target_y, 1 - chaos)
        
        # Card size
        w, h = 60, 40
        
        # Draw substrate card
        card_color = hsv_to_rgb(i / num_cards, 0.6, 0.8)
        draw.rectangle([x - w/2, y - h/2, x + w/2, y + h/2], 
                      fill=card_color, outline=WHITE, width=1)
        
        # Substrate label
        labels = ['RGB', 'Vec3', 'Freq', 'Time', 'ID', 'Ref', 
                  'Mesh', 'Wave', 'Grid', 'Node', 'Link', 'State']
        
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
        except:
            font = ImageFont.load_default()
        
        label = labels[i % len(labels)]
        bbox = draw.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        draw.text((x - tw/2, y - 6), label, fill=WHITE, font=font)
    
    # Connection lines between aligned cards
    if progress > 0.6:
        alpha = (progress - 0.6) / 0.4
        line_color = tuple(int(c * alpha) for c in CYAN)
        
        for i in range(num_cards):
            angle1 = i * 2 * math.pi / num_cards
            angle2 = ((i + 1) % num_cards) * 2 * math.pi / num_cards
            
            x1 = CX + math.cos(angle1) * 180
            y1 = CY + math.sin(angle1) * 90
            x2 = CX + math.cos(angle2) * 180
            y2 = CY + math.sin(angle2) * 90
            
            draw.line([x1, y1, x2, y2], fill=line_color, width=2)
    
    # Central helix
    draw_central_helix(draw, t, progress)


def draw_central_helix(draw, t, progress):
    """Central helix structure"""
    helix_alpha = min(1, progress * 2)
    
    for i in range(80):
        angle = i * 0.1 + t * 2
        z = (i / 80 - 0.5) * 200
        
        r = 30 * helix_alpha
        x = CX + math.cos(angle) * r
        y = CY + z * 0.4 + math.sin(angle) * r * 0.3
        
        size = 3 + math.sin(angle) * 1
        hue = 0.1 + (i / 80) * 0.2
        color = hsv_to_rgb(hue, 0.8, helix_alpha)
        
        draw.ellipse([x - size, y - size, x + size, y + size], fill=color)


def draw_butterfly_flight(draw, arr, t, progress):
    """Butterfly diving through crystalline lattice"""
    # Lattice background
    draw_lattice_bg(draw, t, progress)
    
    # Butterfly path (diving curve)
    path_t = progress
    
    # Bezier-like path
    bx = CX + math.sin(path_t * math.pi * 2) * 300
    by = CY - 100 + path_t * 200 - 100 * math.sin(path_t * math.pi)
    
    # Draw trail
    trail_length = 30
    for i in range(trail_length):
        trail_t = max(0, path_t - i * 0.01)
        tx = CX + math.sin(trail_t * math.pi * 2) * 300
        ty = CY - 100 + trail_t * 200 - 100 * math.sin(trail_t * math.pi)
        
        alpha = 1 - i / trail_length
        size = (trail_length - i) / trail_length * 15
        
        # Golden spiral trail
        color = hsv_to_rgb(0.12 - i * 0.005, 0.9, alpha)
        draw.ellipse([tx - size, ty - size, tx + size, ty + size], fill=color)
    
    # Butterfly at current position
    draw_detailed_butterfly(draw, bx, by, t, 0.6)


def draw_lattice_bg(draw, t, progress):
    """Crystalline lattice background"""
    # 3D grid with perspective
    vanish_y = CY - 200
    
    for layer in range(3):
        z = layer + 1
        alpha = 0.8 / z
        
        spacing = 80
        for i in range(-8, 9):
            for j in range(-5, 6):
                # 3D position
                x3d = i * spacing
                y3d = j * spacing
                z3d = layer * 100 - 100
                
                # Rotation
                angle = t * 0.2
                rx = x3d * math.cos(angle) - z3d * math.sin(angle)
                rz = x3d * math.sin(angle) + z3d * math.cos(angle)
                
                # Perspective projection
                fov = 500
                scale = fov / (fov + rz + 200)  # Prevent division issues
                
                px = CX + rx * scale
                py = CY + y3d * scale * 0.4
                
                if 0 < px < WIDTH and 0 < py < HEIGHT and scale > 0.1:
                    size = max(1, 2 * scale)
                    brightness = int(max(20, min(255, 80 * alpha * scale)))
                    color = (brightness, brightness, brightness)
                    x1, y1 = int(px - size), int(py - size)
                    x2, y2 = int(px + size), int(py + size)
                    if x2 > x1 and y2 > y1:
                        draw.ellipse([x1, y1, x2, y2], fill=color)


def draw_detailed_butterfly(draw, cx, cy, t, scale):
    """Detailed geometric butterfly"""
    beat = math.sin(t * 8) * 0.15
    
    # Wings made of triangular facets
    for side in [-1, 1]:
        wing_angle = side * (0.3 + beat * 0.5)
        
        # Outer wing
        for i in range(8):
            angle = i * 0.3 * side
            r1 = 70 * scale
            r2 = 90 * scale
            
            x1 = cx + math.cos(wing_angle + angle) * r1 * abs(side)
            y1 = cy + math.sin(wing_angle + angle) * r1 * 0.5
            x2 = cx + math.cos(wing_angle + angle + 0.3 * side) * r2 * abs(side)
            y2 = cy + math.sin(wing_angle + angle + 0.3 * side) * r2 * 0.5
            
            hue = 0.08 + i * 0.02
            color = hsv_to_rgb(hue, 0.9, 0.95)
            draw.line([cx, cy, x1, y1], fill=color, width=2)
            draw.line([x1, y1, x2, y2], fill=color, width=2)
    
    # Body
    draw.ellipse([cx - 4, cy - 20 * scale, cx + 4, cy + 25 * scale], fill=GOLD)
    
    # Eyes
    for side in [-1, 1]:
        draw.ellipse([cx + side * 6 - 2, cy - 22 * scale, 
                     cx + side * 6 + 2, cy - 18 * scale], fill=CYAN)


def draw_logo_formation(draw, arr, t, progress):
    """ButterflyFx logo forming from pure light"""
    # Particles converging to logo
    convergence = ease_in_out(min(1, progress * 1.5))
    
    # Logo text position
    logo_y = CY - 50
    
    # Particle storm converging
    num_particles = 200
    for i in range(num_particles):
        # Random starting position
        seed = i * 1.618
        start_x = CX + math.cos(seed * 7) * 500
        start_y = CY + math.sin(seed * 11) * 300
        
        # Target position (logo area)
        target_x = CX + (math.cos(seed * 3) * 150)
        target_y = logo_y + math.sin(seed * 5) * 30
        
        # Interpolate
        px = lerp(start_x, target_x, convergence)
        py = lerp(start_y, target_y, convergence)
        
        # Particle properties
        size = 2 + math.sin(t * 5 + i) * 1
        hue = 0.1 + (i / num_particles) * 0.15
        alpha = 0.3 + convergence * 0.7
        color = hsv_to_rgb(hue, 0.8, alpha)
        
        draw.ellipse([px - size, py - size, px + size, py + size], fill=color)
    
    # Logo text fading in
    if progress > 0.4:
        text_alpha = (progress - 0.4) / 0.6
        
        try:
            font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 72)
            font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 28)
        except:
            font_large = ImageFont.load_default()
            font_small = font_large
        
        # ButterflyFx
        text = "ButterflyFx"
        bbox = draw.textbbox((0, 0), text, font=font_large)
        tw = bbox[2] - bbox[0]
        
        # Glow effect
        for glow in range(3, 0, -1):
            glow_alpha = text_alpha * 0.3 / glow
            glow_color = tuple(int(c * glow_alpha) for c in GOLD)
            draw.text((CX - tw/2, logo_y - 36), text, fill=glow_color, font=font_large)
        
        # Main text
        color = tuple(int(c * text_alpha) for c in WHITE)
        draw.text((CX - tw/2, logo_y - 36), text, fill=color, font=font_large)
        
        # Tagline
        tagline = "Dimensional Computing"
        bbox2 = draw.textbbox((0, 0), tagline, font=font_small)
        tw2 = bbox2[2] - bbox2[0]
        
        tag_color = tuple(int(c * text_alpha) for c in CYAN)
        draw.text((CX - tw2/2, logo_y + 50), tagline, fill=tag_color, font=font_small)
    
    # Final tagline
    if progress > 0.7:
        final_alpha = (progress - 0.7) / 0.3
        
        try:
            font_final = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
        except:
            font_final = ImageFont.load_default()
        
        final_text = "The future doesn't compute — it unfolds."
        bbox3 = draw.textbbox((0, 0), final_text, font=font_final)
        tw3 = bbox3[2] - bbox3[0]
        
        final_color = tuple(int(c * final_alpha) for c in (200, 200, 220))
        draw.text((CX - tw3/2, logo_y + 120), final_text, fill=final_color, font=font_final)
    
    # Butterfly silhouette above logo
    if convergence > 0.8:
        bf_alpha = (convergence - 0.8) / 0.2
        draw_detailed_butterfly(draw, CX, logo_y - 120, t, 0.5 * bf_alpha)


# ============================================================================
# VISUAL DISPATCHER
# ============================================================================

VISUAL_MODES = {
    "void_pulse": draw_void_pulse,
    "butterfly_unfold": draw_butterfly_unfold,
    "grid_eruption": draw_grid_eruption,
    "substrate_align": draw_substrate_align,
    "butterfly_flight": draw_butterfly_flight,
    "logo_formation": draw_logo_formation,
}


def get_current_segment(t):
    """Get current narration segment"""
    for start, end, text, mode in NARRATION:
        if start <= t < end:
            progress = (t - start) / (end - start)
            return text, mode, progress
    return "", "logo_formation", 1.0


def create_frame(frame_num):
    """Create a single frame"""
    t = frame_num / FPS
    
    # Create dark void background with vectorized vignette (fast!)
    y_coords, x_coords = np.ogrid[:HEIGHT, :WIDTH]
    dx = (x_coords - CX) / CX
    dy = (y_coords - CY) / CY
    dist = np.sqrt(dx*dx + dy*dy)
    vignette = np.maximum(0, 1 - dist * 0.5)
    
    arr = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    arr[:, :, 0] = np.clip(VOID[0] + (10 * vignette * math.sin(t * 0.5)).astype(np.uint8), 0, 255)
    arr[:, :, 1] = np.clip(VOID[1] + (5 * vignette * math.cos(t * 0.3)).astype(np.uint8), 0, 255)
    arr[:, :, 2] = np.clip(VOID[2] + (20 * vignette).astype(np.uint8), 0, 255)
    
    img = Image.fromarray(arr, 'RGB')
    draw = ImageDraw.Draw(img)
    
    # Get current segment and draw visuals
    text, mode, progress = get_current_segment(t)
    
    if mode in VISUAL_MODES:
        VISUAL_MODES[mode](draw, arr, t, progress)
    
    return img


# ============================================================================
# AUDIO GENERATION
# ============================================================================

def generate_cinematic_audio(output_path):
    """Generate cinematic ambient soundtrack"""
    sample_rate = 44100
    duration_samples = sample_rate * DURATION
    
    print("  Generating cinematic audio...")
    
    with wave.open(output_path, 'w') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        
        for i in range(duration_samples):
            t = i / sample_rate
            
            # Deep bass drone
            bass = 0.25 * math.sin(2 * math.pi * 55 * t)
            bass += 0.15 * math.sin(2 * math.pi * 82.5 * t)
            
            # Ethereal pad (shifted harmonics)
            pad = 0.1 * math.sin(2 * math.pi * 220 * t * (1 + 0.002 * math.sin(0.2 * t)))
            pad += 0.08 * math.sin(2 * math.pi * 330 * t * (1 + 0.003 * math.sin(0.15 * t)))
            pad += 0.06 * math.sin(2 * math.pi * 440 * t * (1 + 0.001 * math.sin(0.25 * t)))
            
            # Crystalline high frequencies
            crystal = 0.04 * math.sin(2 * math.pi * 880 * t) * (0.5 + 0.5 * math.sin(t * 0.5))
            crystal += 0.03 * math.sin(2 * math.pi * 1320 * t) * (0.5 + 0.5 * math.sin(t * 0.7))
            
            # Build-up for key moments
            buildup = 1.0
            if 14 < t < 18:  # Before grid eruption
                buildup = 1 + (t - 14) / 4 * 0.3
            elif 46 < t < 50:  # Before logo
                buildup = 1 + (t - 46) / 4 * 0.4
            
            # Combine
            val = (bass + pad + crystal) * buildup * 0.6
            
            # Segment-based envelope
            segment_t = t % 10
            if segment_t < 0.3:
                env = segment_t / 0.3
            elif segment_t > 9.7:
                env = (10 - segment_t) / 0.3
            else:
                env = 1.0
            
            val *= env
            
            # Final limiter
            sample = int(val * 20000)
            sample = max(-32768, min(32767, sample))
            wav.writeframes(struct.pack('<hh', sample, sample))


# ============================================================================
# MAIN RENDER FUNCTION
# ============================================================================

def render_video():
    """Main video rendering function"""
    print("=" * 60)
    print("ButterflyFX CINEMATIC PROMO VIDEO GENERATOR")
    print("=" * 60)
    print()
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix='butterflyfx_cinematic_')
    frames_dir = os.path.join(temp_dir, 'frames')
    os.makedirs(frames_dir)
    
    print(f"Temp directory: {temp_dir}")
    print(f"Target: {WIDTH}x{HEIGHT} @ {FPS}fps, {DURATION}s")
    print()
    
    # Generate frames
    print("STEP 1: Generating video frames...")
    for frame_num in range(TOTAL_FRAMES):
        if frame_num % 90 == 0:
            pct = frame_num / TOTAL_FRAMES * 100
            t = frame_num / FPS
            _, mode, _ = get_current_segment(t)
            print(f"  Frame {frame_num}/{TOTAL_FRAMES} ({pct:.1f}%) - {t:.1f}s [{mode}]")
        
        img = create_frame(frame_num)
        frame_path = os.path.join(frames_dir, f'frame_{frame_num:05d}.png')
        img.save(frame_path, 'PNG')
    
    print(f"  Generated {TOTAL_FRAMES} frames")
    
    # Generate audio
    print("\nSTEP 2: Generating cinematic audio...")
    audio_path = os.path.join(temp_dir, 'cinematic.wav')
    generate_cinematic_audio(audio_path)
    print(f"  Audio: {audio_path}")
    
    # Encode video
    print("\nSTEP 3: Encoding video with ffmpeg...")
    output_path = '/opt/butterflyfx/dimensionsos/demos/butterflyfx_promo.mp4'
    
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
        print(f"  Duration: {DURATION} seconds")
        print(f"  Resolution: {WIDTH}x{HEIGHT} @ {FPS}fps")
    else:
        print(f"\nFFMPEG Error: {result.stderr}")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    print("\nTemp files cleaned up.")
    
    print("\n" + "=" * 60)
    print("VIDEO GENERATION COMPLETE")
    print("=" * 60)
    
    # Print narration for reference
    print("\n[NARRATION SCRIPT]")
    for start, end, text, mode in NARRATION:
        print(f"  {start:02d}s-{end:02d}s: {text[:60]}...")


if __name__ == "__main__":
    render_video()
