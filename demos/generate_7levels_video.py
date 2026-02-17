#!/usr/bin/env python3
"""
ButterflyFX 7 Levels Promo Video Generator
============================================

Creates a 1-minute video explaining:
1. What is a Dimension?
2. Data as Coordinates
3. The 7 Levels of Dimensional Creation
4. Substrates - Dimensional Containers
5. Extracting Data from Substrates
6. ButterflyFx Logo Finale

Pure Python with PIL - fast rendering!
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import subprocess
import tempfile
import math
import wave
import struct

# ============================================================================
# CONSTANTS
# ============================================================================

WIDTH, HEIGHT = 1280, 720
FPS = 30
DURATION = 60
TOTAL_FRAMES = FPS * DURATION
CX, CY = WIDTH // 2, HEIGHT // 2

# Colors
VOID = (5, 5, 15)
GOLD = (255, 215, 0)
CYAN = (0, 255, 255)
PURPLE = (180, 100, 255)
WHITE = (255, 255, 255)
DIM_BLUE = (26, 26, 62)

# 7 Levels
LEVELS = [
    ("0", "○", "Potential", "Pure possibility — nothing instantiated", (102, 102, 102)),
    ("1", "•", "Point", "Single instantiation — moment of existence", (255, 107, 107)),
    ("2", "━", "Length", "Extension in one dimension", (78, 205, 196)),
    ("3", "▭", "Width", "Extension in two dimensions", (69, 183, 209)),
    ("4", "▦", "Plane", "Surface — 2D completeness", (150, 206, 180)),
    ("5", "▣", "Volume", "Full 3D existence", (255, 234, 167)),
    ("6", "◉", "Whole", "Complete entity — ready for next spiral", GOLD),
]

# Scene timings (start, end, scene_func)
SCENES = [
    (0, 10, "scene_dimensions"),
    (10, 22, "scene_coordinates"),
    (22, 35, "scene_seven_levels"),
    (35, 45, "scene_substrates"),
    (45, 52, "scene_extraction"),
    (52, 60, "scene_finale"),
]

# ============================================================================
# EASING & UTILITIES
# ============================================================================

def ease_in_out(t):
    return t * t * (3 - 2 * t)

def ease_out(t):
    return 1 - (1 - t) ** 3

def lerp(a, b, t):
    return a + (b - a) * t

def get_font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', size)
        return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)
    except:
        return ImageFont.load_default()

def draw_text_centered(draw, text, y, font, color):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((CX - tw // 2, y), text, fill=color, font=font)

def create_gradient_bg(arr, t):
    """Create animated gradient background"""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(5 + 20 * ratio * (0.8 + 0.2 * math.sin(t * 0.3)))
        g = int(5 + 15 * ratio)
        b = int(15 + 50 * ratio)
        arr[y, :] = [r, g, b]

def draw_grid(draw, t, alpha=0.1):
    """Draw animated grid background"""
    spacing = 50
    offset_x = int(t * 10) % spacing
    
    grid_color = tuple(int(c * alpha) for c in CYAN)
    
    for x in range(-spacing + offset_x, WIDTH + spacing, spacing):
        draw.line([(x, 0), (x, HEIGHT)], fill=grid_color, width=1)
    
    for y in range(0, HEIGHT, spacing):
        draw.line([(0, y), (WIDTH, y)], fill=grid_color, width=1)

# ============================================================================
# SCENE: WHAT IS A DIMENSION?
# ============================================================================

def scene_dimensions(draw, t, progress):
    """Scene 1: What is a Dimension? (0-10s)"""
    fade_in = min(1, progress * 5) if progress < 0.2 else 1
    fade_out = max(0, (1 - progress) * 5) if progress > 0.8 else 1
    alpha = fade_in * fade_out
    
    # Title
    font_large = get_font(56, bold=True)
    font_small = get_font(24)
    
    color = tuple(int(c * alpha) for c in GOLD)
    draw_text_centered(draw, "What is a Dimension?", 150, font_large, color)
    
    # Subtitle
    sub_color = tuple(int(c * alpha) for c in CYAN)
    draw_text_centered(draw, "An axis of measurement. A degree of freedom.", 220, font_small, sub_color)
    
    # Draw axis visualization
    if progress > 0.15:
        axis_alpha = min(1, (progress - 0.15) * 5) * alpha
        
        axes = [
            ("X", CX - 200, CY + 50),
            ("Y", CX - 70, CY + 50),
            ("Z", CX + 60, CY + 50),
            ("TIME", CX + 190, CY + 50),
        ]
        
        for i, (label, ax, ay) in enumerate(axes):
            delay = i * 0.05
            if progress > 0.15 + delay:
                ax_progress = min(1, (progress - 0.15 - delay) * 5)
                
                # Floating animation
                float_y = math.sin(t * 2 + i * 0.5) * 10
                
                # Draw axis line
                line_height = int(100 * ax_progress)
                line_color = GOLD if label == "TIME" else CYAN
                line_alpha = tuple(int(c * axis_alpha) for c in line_color)
                draw.line([(ax, ay - line_height + float_y), (ax, ay + float_y)], 
                         fill=line_alpha, width=4)
                
                # Draw label
                font_label = get_font(22, bold=True)
                bbox = draw.textbbox((0, 0), label, font=font_label)
                tw = bbox[2] - bbox[0]
                label_color = tuple(int(c * axis_alpha) for c in line_color)
                draw.text((ax - tw // 2, ay + 20 + float_y), label, fill=label_color, font=font_label)

# ============================================================================
# SCENE: DATA AS COORDINATES
# ============================================================================

def scene_coordinates(draw, t, progress):
    """Scene 2: Data as Coordinates (10-22s)"""
    fade_in = min(1, progress * 5) if progress < 0.1 else 1
    fade_out = max(0, (1 - progress) * 5) if progress > 0.85 else 1
    alpha = fade_in * fade_out
    
    font_large = get_font(38, bold=True)
    font_medium = get_font(28)
    font_small = get_font(20)
    
    # Main text
    text1_color = tuple(int(c * alpha) for c in WHITE)
    draw_text_centered(draw, "Every piece of data is a", CY - 150, font_large, text1_color)
    
    coord_color = tuple(int(c * alpha) for c in GOLD)
    draw_text_centered(draw, "COORDINATE", CY - 100, get_font(48, bold=True), coord_color)
    
    draw_text_centered(draw, "in a multi-dimensional space", CY - 40, font_large, text1_color)
    
    # Data point visualization
    if progress > 0.2:
        box_alpha = min(1, (progress - 0.2) * 3) * alpha
        
        # Color box
        box_x, box_y = CX - 250, CY + 80
        box_color = tuple(int(c * box_alpha) for c in CYAN)
        draw.rectangle([box_x, box_y, box_x + 140, box_y + 100], 
                      outline=box_color, width=2)
        
        # Pulsing effect
        pulse = 0.8 + 0.2 * math.sin(t * 4)
        inner_color = tuple(int(c * box_alpha * pulse) for c in (255, 107, 0))
        draw.rectangle([box_x + 20, box_y + 20, box_x + 120, box_y + 80], fill=inner_color)
        
        value_color = tuple(int(255 * box_alpha) for _ in range(3))
        draw.text((box_x + 25, box_y + 35), "#FF6B00", fill=value_color, font=font_medium)
        
        type_color = tuple(int(100 * box_alpha) for _ in range(3))
        draw.text((box_x + 50, box_y + 105), "Color", fill=type_color, font=font_small)
    
    # Arrow
    if progress > 0.35:
        arrow_alpha = min(1, (progress - 0.35) * 3) * alpha
        arrow_pulse = int(CX - 70 + math.sin(t * 3) * 10)
        arrow_color = tuple(int(c * arrow_alpha) for c in PURPLE)
        draw.text((arrow_pulse, CY + 110), "→", fill=arrow_color, font=get_font(48))
    
    # Output box
    if progress > 0.45:
        out_alpha = min(1, (progress - 0.45) * 3) * alpha
        out_x = CX + 50
        out_color = tuple(int(c * out_alpha) for c in GOLD)
        draw.rectangle([out_x, CY + 70, out_x + 280, CY + 180], outline=out_color, width=2)
        
        text_color = tuple(int(c * out_alpha) for c in CYAN)
        draw.text((out_x + 15, CY + 85), "R: 255  G: 107  B: 0", fill=text_color, font=font_small)
        draw.text((out_x + 15, CY + 115), "H: 25°  S: 100%", fill=text_color, font=font_small)
        draw.text((out_x + 15, CY + 145), "L: 50%", fill=text_color, font=font_small)

# ============================================================================
# SCENE: 7 LEVELS OF DIMENSIONAL CREATION
# ============================================================================

def scene_seven_levels(draw, t, progress):
    """Scene 3: The 7 Levels (22-35s)"""
    fade_in = min(1, progress * 5) if progress < 0.1 else 1
    fade_out = max(0, (1 - progress) * 5) if progress > 0.85 else 1
    alpha = fade_in * fade_out
    
    font_title = get_font(42, bold=True)
    font_level = get_font(22, bold=True)
    font_desc = get_font(18)
    
    # Title
    title_color = tuple(int(c * alpha) for c in PURPLE)
    draw_text_centered(draw, "The 7 Levels of Dimensional Creation", 60, font_title, title_color)
    
    # Draw each level
    start_y = 130
    row_height = 65
    
    for i, (num, symbol, name, desc, color) in enumerate(LEVELS):
        delay = i * 0.04
        if progress > 0.08 + delay:
            level_progress = min(1, (progress - 0.08 - delay) * 4)
            level_alpha = level_progress * alpha
            
            # Slide in from left
            x_offset = int((1 - ease_out(level_progress)) * -100)
            y = start_y + i * row_height
            
            # Level number circle
            num_x = 150 + x_offset
            num_color = tuple(int(lerp(PURPLE[j], CYAN[j], i / 6) * level_alpha) for j in range(3))
            draw.ellipse([num_x - 18, y - 18, num_x + 18, y + 18], fill=num_color)
            num_text_color = tuple(int(255 * level_alpha) for _ in range(3))
            draw.text((num_x - 6, y - 12), num, fill=num_text_color, font=font_level)
            
            # Symbol with pulse
            pulse = 0.8 + 0.4 * math.sin(t * 3 + i * 0.5)
            sym_x = 210 + x_offset
            sym_color = tuple(int(c * level_alpha * pulse) for c in color)
            draw.text((sym_x, y - 15), symbol, fill=sym_color, font=get_font(32))
            
            # Name
            name_color = tuple(int(255 * level_alpha) for _ in range(3))
            draw.text((270 + x_offset, y - 10), name, fill=name_color, font=font_level)
            
            # Description
            desc_color = tuple(int(150 * level_alpha) for _ in range(3))
            draw.text((420 + x_offset, y - 8), desc, fill=desc_color, font=font_desc)
    
    # Spiral visualization on the right
    if progress > 0.3:
        spiral_alpha = min(1, (progress - 0.3) * 2) * alpha
        spiral_cx, spiral_cy = WIDTH - 120, CY + 30
        
        # Draw spiral
        for i in range(60):
            angle = i * 0.15 + t * 2
            r = 20 + i * 1.5
            x = spiral_cx + math.cos(angle) * r * 0.4
            y = spiral_cy + math.sin(angle) * r * 0.3 - i * 2 + 60
            
            size = 3 + math.sin(angle) * 1
            level_idx = i % 7
            point_color = tuple(int(c * spiral_alpha * 0.8) for c in LEVELS[level_idx][4])
            draw.ellipse([x - size, y - size, x + size, y + size], fill=point_color)

# ============================================================================
# SCENE: SUBSTRATES
# ============================================================================

def scene_substrates(draw, t, progress):
    """Scene 4: Substrates Explained (35-45s)"""
    fade_in = min(1, progress * 5) if progress < 0.1 else 1
    fade_out = max(0, (1 - progress) * 5) if progress > 0.85 else 1
    alpha = fade_in * fade_out
    
    font_title = get_font(52, bold=True)
    font_sub = get_font(20, bold=True)
    font_desc = get_font(22)
    
    # Title
    title_color = tuple(int(c * alpha) for c in CYAN)
    draw_text_centered(draw, "SUBSTRATES", 100, font_title, title_color)
    
    # Substrate boxes
    substrates = [
        ("ColorSubstrate", (255, 107, 107), 120, 200),
        ("SoundSubstrate", (78, 205, 196), 220, 290),
        ("PhysicsSubstrate", (102, 126, 234), 320, 380),
        ("GraphicsSubstrate", (240, 147, 251), 170, 470),
        ("TimeSubstrate", (79, 172, 254), 270, 560),
    ]
    
    for i, (name, color, y_pos, x_pos) in enumerate(substrates):
        delay = i * 0.06
        if progress > 0.1 + delay:
            sub_progress = min(1, (progress - 0.1 - delay) * 4)
            sub_alpha = sub_progress * alpha
            
            # Slide in
            x_offset = int((1 - ease_out(sub_progress)) * -80)
            
            # Draw box
            box_color = tuple(int(c * sub_alpha) for c in color)
            draw.rounded_rectangle([x_pos + x_offset, y_pos, x_pos + x_offset + 230, y_pos + 60], 
                                   radius=12, fill=box_color)
            
            # Label
            label_color = tuple(int(255 * sub_alpha) for _ in range(3))
            bbox = draw.textbbox((0, 0), name, font=font_sub)
            tw = bbox[2] - bbox[0]
            draw.text((x_pos + x_offset + 115 - tw // 2, y_pos + 18), name, fill=label_color, font=font_sub)
    
    # Explanation
    if progress > 0.5:
        exp_alpha = min(1, (progress - 0.5) * 3) * alpha
        exp_color = tuple(int(180 * exp_alpha) for _ in range(3))
        draw_text_centered(draw, "Substrates are dimensional containers.", CY + 180, font_desc, exp_color)
        draw_text_centered(draw, "They define which levels exist and how to extract data.", CY + 215, font_desc, exp_color)

# ============================================================================
# SCENE: EXTRACTING DATA
# ============================================================================

def scene_extraction(draw, t, progress):
    """Scene 5: Extracting Data (45-52s)"""
    fade_in = min(1, progress * 5) if progress < 0.1 else 1
    fade_out = max(0, (1 - progress) * 5) if progress > 0.85 else 1
    alpha = fade_in * fade_out
    
    font_title = get_font(42, bold=True)
    font_data = get_font(18)
    font_key = get_font(18, bold=True)
    
    # Title
    title_color = tuple(int(lerp(CYAN[i], PURPLE[i], 0.5) * alpha) for i in range(3))
    draw_text_centered(draw, "Extracting Data from Substrates", 80, font_title, title_color)
    
    # Rotating cube
    cube_x, cube_y = CX - 250, CY + 20
    rotation = t * 0.8
    
    # Cube faces (simplified 3D)
    cube_size = 120
    faces = [
        ("Level 0", 0), ("Level 1", 1), ("Level 2", 2),
        ("Level 4", 4), ("Level 5", 5), ("Level 6", 6),
    ]
    
    # Draw cube wireframe
    for angle_offset, label_idx in [(0, 0), (math.pi/2, 1), (math.pi, 2)]:
        angle = rotation + angle_offset
        
        # Calculate face visibility
        vis = math.cos(angle)
        if vis > -0.3:
            face_alpha = (vis + 0.3) / 1.3 * alpha
            
            # Draw face
            offset_x = math.sin(angle) * 40
            offset_y = math.cos(angle) * 20
            
            face_color = tuple(int(c * face_alpha * 0.3) for c in CYAN)
            draw.rectangle([
                cube_x - 60 + offset_x, cube_y - 60 + offset_y,
                cube_x + 60 + offset_x, cube_y + 60 + offset_y
            ], outline=face_color, fill=tuple(int(c * face_alpha * 0.1) for c in CYAN), width=2)
            
            # Label
            label = faces[label_idx % len(faces)][0]
            label_color = tuple(int(255 * face_alpha) for _ in range(3))
            draw.text((cube_x - 30 + offset_x, cube_y - 10 + offset_y), label, fill=label_color, font=font_data)
    
    # Extraction beam
    if progress > 0.15:
        beam_alpha = min(1, (progress - 0.15) * 3) * alpha
        beam_pulse = 0.7 + 0.3 * math.sin(t * 5)
        
        for i in range(3):
            beam_y = cube_y - 20 + i * 20
            beam_color = tuple(int(lerp(PURPLE[j], GOLD[j], i / 2) * beam_alpha * beam_pulse) for j in range(3))
            draw.line([(cube_x + 80, beam_y), (cube_x + 200, beam_y)], fill=beam_color, width=3)
    
    # Extracted data
    data_items = [
        ("Level 1 (Point):", "RGB(255, 180, 50)"),
        ("Level 2 (Length):", "Vector3D(12.5, 8.3, 2.1)"),
        ("Level 5 (Volume):", "Mesh(vertices: 1024)"),
        ("Level 6 (Whole):", "Entity.complete()"),
    ]
    
    data_x = CX + 50
    data_y_start = CY - 80
    
    for i, (key, value) in enumerate(data_items):
        delay = 0.25 + i * 0.08
        if progress > delay:
            item_progress = min(1, (progress - delay) * 4)
            item_alpha = item_progress * alpha
            
            y = data_y_start + i * 55
            x_offset = int((1 - ease_out(item_progress)) * 30)
            
            # Background bar
            bar_color = tuple(int(c * item_alpha * 0.15) for c in GOLD)
            draw.rectangle([data_x + x_offset, y, data_x + x_offset + 350, y + 40], fill=bar_color)
            
            # Left accent
            accent_color = tuple(int(c * item_alpha) for c in GOLD)
            draw.rectangle([data_x + x_offset, y, data_x + x_offset + 4, y + 40], fill=accent_color)
            
            # Key
            key_color = tuple(int(c * item_alpha) for c in CYAN)
            draw.text((data_x + x_offset + 15, y + 10), key, fill=key_color, font=font_key)
            
            # Value
            value_color = tuple(int(c * item_alpha) for c in GOLD)
            draw.text((data_x + x_offset + 150, y + 10), value, fill=value_color, font=font_data)

# ============================================================================
# SCENE: FINALE
# ============================================================================

def scene_finale(draw, t, progress):
    """Scene 6: Logo Finale (52-60s)"""
    fade_in = min(1, progress * 3) if progress < 0.2 else 1
    
    # Particles converging
    if progress < 0.5:
        for i in range(100):
            seed = i * 1.618
            
            # Start position (scattered)
            start_x = CX + math.cos(seed * 7) * 500
            start_y = CY + math.sin(seed * 11) * 300
            
            # Target position (logo area)
            target_x = CX + math.cos(seed * 3) * 100
            target_y = CY - 50 + math.sin(seed * 5) * 20
            
            # Interpolate
            converge = ease_in_out(min(1, progress * 2))
            px = lerp(start_x, target_x, converge)
            py = lerp(start_y, target_y, converge)
            
            # Draw particle
            size = 2 + math.sin(t * 5 + i) * 1
            hue = (i / 100) * 0.15 + 0.1
            r = int(255 * (0.8 + 0.2 * math.sin(hue * 6)))
            g = int(200 * (0.5 + 0.5 * math.sin(hue * 6 + 2)))
            b = int(100 * (0.3 + 0.7 * math.sin(hue * 6 + 4)))
            
            particle_alpha = 0.3 + converge * 0.7
            color = tuple(int(c * particle_alpha * fade_in) for c in (r, g, b))
            draw.ellipse([px - size, py - size, px + size, py + size], fill=color)
    
    # Logo
    if progress > 0.2:
        logo_progress = min(1, (progress - 0.2) / 0.3)
        logo_alpha = ease_out(logo_progress) * fade_in
        
        # Glow effect
        font_logo = get_font(80, bold=True)
        logo_text = "ButterflyFx"
        
        # Multiple glow layers
        for glow in range(3, 0, -1):
            glow_alpha = logo_alpha * 0.2 / glow
            glow_color = tuple(int(c * glow_alpha) for c in GOLD)
            bbox = draw.textbbox((0, 0), logo_text, font=font_logo)
            tw = bbox[2] - bbox[0]
            draw.text((CX - tw // 2 - glow, CY - 80 - glow), logo_text, fill=glow_color, font=font_logo)
        
        # Main logo with gradient effect (simulated)
        logo_color = tuple(int(c * logo_alpha) for c in WHITE)
        bbox = draw.textbbox((0, 0), logo_text, font=font_logo)
        tw = bbox[2] - bbox[0]
        draw.text((CX - tw // 2, CY - 80), logo_text, fill=logo_color, font=font_logo)
    
    # Tagline
    if progress > 0.4:
        tag_alpha = min(1, (progress - 0.4) / 0.2) * fade_in
        font_tag = get_font(32)
        tag_color = tuple(int(c * tag_alpha) for c in CYAN)
        draw_text_centered(draw, "Dimensional Computing", CY + 20, font_tag, tag_color)
    
    # Final line
    if progress > 0.6:
        final_alpha = min(1, (progress - 0.6) / 0.2) * fade_in
        font_final = get_font(22)
        final_color = tuple(int(150 * final_alpha) for _ in range(3))
        draw_text_centered(draw, "7 levels. Infinite spirals. One unified system.", CY + 80, font_final, final_color)

# ============================================================================
# SCENE DISPATCHER
# ============================================================================

SCENE_FUNCS = {
    "scene_dimensions": scene_dimensions,
    "scene_coordinates": scene_coordinates,
    "scene_seven_levels": scene_seven_levels,
    "scene_substrates": scene_substrates,
    "scene_extraction": scene_extraction,
    "scene_finale": scene_finale,
}

def get_scene(t):
    for start, end, scene_name in SCENES:
        if start <= t < end:
            progress = (t - start) / (end - start)
            return scene_name, progress
    return "scene_finale", 1.0

def create_frame(frame_num):
    t = frame_num / FPS
    
    # Create background
    arr = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    create_gradient_bg(arr, t)
    
    img = Image.fromarray(arr, 'RGB')
    draw = ImageDraw.Draw(img)
    
    # Draw grid
    draw_grid(draw, t, alpha=0.15)
    
    # Get and render scene
    scene_name, progress = get_scene(t)
    if scene_name in SCENE_FUNCS:
        SCENE_FUNCS[scene_name](draw, t, progress)
    
    # Vignette
    # (applied in post for performance)
    
    return img

# ============================================================================
# AUDIO GENERATION
# ============================================================================

def generate_audio(output_path):
    """Generate cinematic ambient audio"""
    sample_rate = 44100
    duration_samples = sample_rate * DURATION
    
    with wave.open(output_path, 'w') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        
        for i in range(duration_samples):
            t = i / sample_rate
            
            # Deep bass
            val = 0.2 * math.sin(2 * math.pi * 55 * t)
            val += 0.12 * math.sin(2 * math.pi * 82.5 * t)
            
            # Ethereal pad
            val += 0.08 * math.sin(2 * math.pi * 220 * t * (1 + 0.002 * math.sin(0.2 * t)))
            val += 0.06 * math.sin(2 * math.pi * 330 * t * (1 + 0.003 * math.sin(0.15 * t)))
            val += 0.05 * math.sin(2 * math.pi * 440 * t * (1 + 0.001 * math.sin(0.25 * t)))
            
            # Crystalline highs
            val += 0.03 * math.sin(2 * math.pi * 880 * t) * (0.5 + 0.5 * math.sin(t * 0.5))
            
            # Scene transitions
            if 20 < t < 24:
                val *= 1 + (t - 20) / 4 * 0.2
            if 50 < t < 55:
                val *= 1 + (t - 50) / 5 * 0.3
            
            sample = int(val * 18000)
            sample = max(-32768, min(32767, sample))
            wav.writeframes(struct.pack('<hh', sample, sample))

# ============================================================================
# MAIN RENDER
# ============================================================================

def render_video():
    print("=" * 60)
    print("ButterflyFX 7 LEVELS PROMO VIDEO")
    print("=" * 60)
    print()
    
    temp_dir = tempfile.mkdtemp(prefix='butterflyfx_7levels_')
    frames_dir = os.path.join(temp_dir, 'frames')
    os.makedirs(frames_dir)
    
    print(f"Temp: {temp_dir}")
    print(f"Target: {WIDTH}x{HEIGHT} @ {FPS}fps, {DURATION}s")
    print()
    
    print("STEP 1: Generating frames...")
    for frame_num in range(TOTAL_FRAMES):
        if frame_num % 90 == 0:
            pct = frame_num / TOTAL_FRAMES * 100
            scene_name, _ = get_scene(frame_num / FPS)
            print(f"  Frame {frame_num}/{TOTAL_FRAMES} ({pct:.1f}%) - {scene_name}")
        
        img = create_frame(frame_num)
        img.save(os.path.join(frames_dir, f'frame_{frame_num:05d}.png'), 'PNG')
    
    print(f"  Generated {TOTAL_FRAMES} frames")
    
    print("\nSTEP 2: Generating audio...")
    audio_path = os.path.join(temp_dir, 'ambient.wav')
    generate_audio(audio_path)
    print(f"  Audio: {audio_path}")
    
    print("\nSTEP 3: Encoding video...")
    output_path = '/opt/butterflyfx/dimensionsos/demos/dimensional_7levels.mp4'
    
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
        print(f"\nError: {result.stderr}")
    
    import shutil
    shutil.rmtree(temp_dir)
    print("\nTemp cleaned up.")
    
    print("\n" + "=" * 60)
    print("SCENES:")
    for start, end, name in SCENES:
        print(f"  {start:02d}s-{end:02d}s: {name}")
    print("=" * 60)

if __name__ == "__main__":
    render_video()
