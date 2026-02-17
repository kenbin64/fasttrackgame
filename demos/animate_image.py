#!/usr/bin/env python3
"""
ButterflyFX Image Animation Engine
====================================

Animates a static image with physics-based motion:
- Water/ocean waves with currents and crashing
- Bird flight with wing physics
- Palm leaves swaying in wind
- Water spray particles on rocks

Uses region segmentation and displacement mapping.

Copyright (c) 2024-2026 Kenneth Bingham
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
from scipy.ndimage import gaussian_filter, map_coordinates
import os
import subprocess
import tempfile
import math
import wave
import struct

# ============================================================================
# PHYSICS CONSTANTS
# ============================================================================

GRAVITY = 9.81  # m/s²
WIND_SPEED = 2.5  # m/s base
WAVE_SPEED = 1.2  # wave propagation
BIRD_FLIGHT_SPEED = 3.0  # takeoff speed

# ============================================================================
# IMAGE SEGMENTATION
# ============================================================================

class ImageSegmenter:
    """Segments image into animatable regions using color analysis"""
    
    def __init__(self, image_path):
        self.img = Image.open(image_path).convert('RGBA')
        self.arr = np.array(self.img)
        self.h, self.w = self.arr.shape[:2]
        
        # Create masks for different regions
        self.masks = {}
        self._segment()
    
    def _segment(self):
        """Segment image into regions based on color signatures"""
        rgb = self.arr[:, :, :3].astype(float)
        
        # Calculate HSV-like properties
        max_c = rgb.max(axis=2)
        min_c = rgb.min(axis=2)
        delta = max_c - min_c
        saturation = delta / (max_c + 1e-6)
        value = max_c / 255.0
        
        # Bird detection: Look for VERY saturated colors (parrots are bright)
        # Also check for specific parrot colors: red, bright green, blue, yellow
        r, g, b_ch = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
        
        # Parrot-specific color detection
        is_red = (r > 150) & (r > g + 40) & (r > b_ch + 40)
        is_bright_green = (g > 120) & (g > r + 30) & (g > b_ch + 20)
        is_blue = (b_ch > 120) & (b_ch > r + 20) & (b_ch > g)
        is_yellow = (r > 150) & (g > 150) & (b_ch < 100)
        is_orange = (r > 180) & (g > 80) & (g < 180) & (b_ch < 80)
        
        bird_color_mask = is_red | is_bright_green | is_blue | is_yellow | is_orange
        bird_mask = bird_color_mask & (saturation > 0.5)
        
        # Find connected component that's likely the bird
        labeled, num_features = ndimage.label(bird_mask)
        if num_features > 0:
            # Find a nicely-sized blob near center
            center_y, center_x = self.h // 2, self.w // 2
            best_label = 0
            best_score = float('inf')
            
            for label_id in range(1, min(num_features + 1, 100)):  # Limit iterations
                coords = np.where(labeled == label_id)
                size = len(coords[0])
                # Bird should be moderate size (2-20% of image)
                if 2000 < size < self.h * self.w * 0.2:
                    cy = coords[0].mean()
                    cx = coords[1].mean()
                    dist = math.sqrt((cy - center_y)**2 + (cx - center_x)**2)
                    score = dist
                    if score < best_score:
                        best_score = score
                        best_label = label_id
            
            self.masks['bird'] = (labeled == best_label)
            
            # Get bird bounding box
            bird_coords = np.where(self.masks['bird'])
            if len(bird_coords[0]) > 0:
                self.bird_bbox = (
                    bird_coords[1].min(), bird_coords[0].min(),  # x1, y1
                    bird_coords[1].max(), bird_coords[0].max()   # x2, y2
                )
                self.bird_center = (
                    (self.bird_bbox[0] + self.bird_bbox[2]) // 2,
                    (self.bird_bbox[1] + self.bird_bbox[3]) // 2
                )
            else:
                self.bird_bbox = (450, 400, 550, 550)
                self.bird_center = (500, 475)
        else:
            self.masks['bird'] = np.zeros((self.h, self.w), dtype=bool)
            self.bird_bbox = (450, 400, 550, 550)
            self.bird_center = (500, 475)
        
        # Water detection: Blue-ish regions, typically in lower portion
        # Also look for cyan/turquoise tones
        r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
        water_mask = (
            ((b > r - 30) & (b > g - 30) & (value > 0.15)) |  # Blue-dominant
            ((g > 100) & (b > 100) & (r < g + 50))  # Turquoise
        )
        # Weight toward bottom of image
        y_weight = np.linspace(0, 1, self.h)[:, np.newaxis]
        water_mask = water_mask & (y_weight > 0.3)
        self.masks['water'] = water_mask
        
        # Palm/foliage detection: Green regions
        green_mask = (g > r + 5) & (g > b + 5) & (value > 0.2)
        # Exclude bird area from palm
        green_mask = green_mask & ~self.masks['bird']
        self.masks['palm'] = green_mask
        
        # Rocks/beach: Brown/tan regions
        rock_mask = (
            (r > g - 30) & (r > b) & 
            (saturation < 0.5) & (value > 0.15) &
            (y_weight > 0.5)  # More likely in lower half
        )
        rock_mask = rock_mask & ~self.masks['bird'] & ~self.masks['water']
        self.masks['rocks'] = rock_mask
        
        # Sky: Upper region, light colors
        sky_mask = (value > 0.4) & (y_weight < 0.4) & ~self.masks['palm'] & ~self.masks['bird']
        self.masks['sky'] = sky_mask
        
        # Water edge (for spray): Interface between water and rocks
        water_dilated = ndimage.binary_dilation(self.masks['water'], iterations=15)
        rock_dilated = ndimage.binary_dilation(self.masks['rocks'], iterations=15)
        self.masks['spray_zone'] = water_dilated & rock_dilated
        
        print(f"Segmentation complete:")
        print(f"  Bird: {self.masks['bird'].sum()} pixels, bbox={self.bird_bbox}")
        print(f"  Water: {self.masks['water'].sum()} pixels")
        print(f"  Palm: {self.masks['palm'].sum()} pixels")
        print(f"  Rocks: {self.masks['rocks'].sum()} pixels")
        print(f"  Spray zone: {self.masks['spray_zone'].sum()} pixels")
    
    def get_mask(self, region):
        return self.masks.get(region, np.zeros((self.h, self.w), dtype=bool))
    
    def extract_region(self, region):
        """Extract region as RGBA image with transparency elsewhere"""
        mask = self.get_mask(region)
        result = self.arr.copy()
        result[~mask, 3] = 0  # Transparent where not in mask
        return result


# ============================================================================
# PHYSICS SIMULATION
# ============================================================================

class WavePhysics:
    """Simulates ocean wave motion using Gerstner waves"""
    
    def __init__(self, width, height):
        self.w = width
        self.h = height
        
        # Wave parameters (multiple wave components)
        self.waves = [
            {'amplitude': 8, 'wavelength': 200, 'speed': 1.0, 'direction': 0.1},
            {'amplitude': 4, 'wavelength': 80, 'speed': 1.5, 'direction': -0.2},
            {'amplitude': 2, 'wavelength': 40, 'speed': 2.0, 'direction': 0.3},
            {'amplitude': 6, 'wavelength': 150, 'speed': 0.8, 'direction': 0.0},
        ]
    
    def get_displacement(self, t, mask):
        """Calculate displacement field for water pixels"""
        # Create coordinate grids
        y, x = np.ogrid[:self.h, :self.w]
        
        dx = np.zeros((self.h, self.w), dtype=float)
        dy = np.zeros((self.h, self.w), dtype=float)
        
        for wave in self.waves:
            A = wave['amplitude']
            L = wave['wavelength']
            s = wave['speed']
            d = wave['direction']
            
            k = 2 * np.pi / L
            omega = s * k
            
            # Wave direction vector
            kx = k * np.cos(d)
            ky = k * np.sin(d)
            
            # Phase
            phase = kx * x + ky * y - omega * t
            
            # Gerstner wave displacement
            dx += A * np.cos(phase) * np.cos(d)
            dy += A * np.sin(phase) * 0.3  # Reduced vertical for subtlety
        
        # Apply only to water mask
        dx = dx * mask
        dy = dy * mask
        
        return dx, dy


class WindPhysics:
    """Simulates wind effect on palm leaves"""
    
    def __init__(self, base_speed=2.5):
        self.base_speed = base_speed
        # Turbulence frequencies
        self.turbulence = [
            {'freq': 0.5, 'amp': 1.0},
            {'freq': 1.2, 'amp': 0.5},
            {'freq': 2.5, 'amp': 0.3},
        ]
    
    def get_wind_force(self, t):
        """Get current wind force"""
        force = self.base_speed
        for turb in self.turbulence:
            force += turb['amp'] * math.sin(t * turb['freq'] * 2 * math.pi)
        return force
    
    def get_displacement(self, t, mask, pivot_y):
        """Calculate palm sway displacement"""
        h, w = mask.shape
        y, x = np.ogrid[:h, :w]
        
        # Wind force varies with time
        wind = self.get_wind_force(t)
        
        # Displacement increases with distance from pivot (base of palm)
        # Leaves at top sway more
        distance_from_pivot = np.maximum(0, pivot_y - y) / pivot_y
        
        # Horizontal sway
        dx = wind * distance_from_pivot ** 2 * 20 * np.sin(t * 2 + x / 50)
        
        # Slight vertical bob
        dy = wind * distance_from_pivot * 3 * np.cos(t * 3 + x / 30)
        
        dx = dx * mask
        dy = dy * mask
        
        return dx.astype(float), dy.astype(float)


class BirdFlight:
    """Physics-based bird flight animation"""
    
    def __init__(self, start_x, start_y, img_width, img_height):
        self.start_x = start_x
        self.start_y = start_y
        self.img_w = img_width
        self.img_h = img_height
        
        # Flight phases
        self.perch_time = 2.0  # Seconds before takeoff
        self.squawk_time = 1.5  # Squawk duration before flight
        self.flight_duration = 6.0  # Time to fly away
        
        # Physics
        self.takeoff_angle = -45  # degrees, upward
        self.flight_speed = 150  # pixels per second
        self.wing_freq = 4  # wing beats per second
    
    def get_state(self, t):
        """Get bird state at time t"""
        if t < self.perch_time:
            # Perched, slight movement
            return {
                'phase': 'perch',
                'x': self.start_x + math.sin(t * 2) * 2,
                'y': self.start_y + math.sin(t * 3) * 1,
                'rotation': math.sin(t * 1.5) * 3,
                'scale': 1.0,
                'wing_angle': 0
            }
        elif t < self.perch_time + self.squawk_time:
            # Squawking - head bob, wings flutter
            squawk_t = t - self.perch_time
            return {
                'phase': 'squawk',
                'x': self.start_x + math.sin(squawk_t * 8) * 5,
                'y': self.start_y + math.sin(squawk_t * 12) * 3,
                'rotation': math.sin(squawk_t * 10) * 8,
                'scale': 1.0 + math.sin(squawk_t * 15) * 0.05,
                'wing_angle': math.sin(squawk_t * 20) * 15
            }
        else:
            # Flying away
            flight_t = t - self.perch_time - self.squawk_time
            progress = min(1.0, flight_t / self.flight_duration)
            
            # Curved flight path
            angle_rad = math.radians(self.takeoff_angle)
            
            # Add some curve to the path
            curve = math.sin(progress * math.pi) * 100
            
            x = self.start_x + self.flight_speed * flight_t * math.cos(angle_rad) + curve
            y = self.start_y + self.flight_speed * flight_t * math.sin(angle_rad)
            
            # Wings flapping
            wing_angle = math.sin(flight_t * self.wing_freq * 2 * math.pi) * 30
            
            # Slight shrink as bird flies away
            scale = 1.0 - progress * 0.5
            
            return {
                'phase': 'flight',
                'x': x,
                'y': y,
                'rotation': self.takeoff_angle + math.sin(flight_t * 2) * 10,
                'scale': max(0.1, scale),
                'wing_angle': wing_angle
            }


class SprayParticles:
    """Water spray particles physics"""
    
    def __init__(self, spray_zone, num_particles=200):
        self.num_particles = num_particles
        
        # Find spawn points along spray zone
        coords = np.where(spray_zone)
        if len(coords[0]) > 0:
            indices = np.random.choice(len(coords[0]), min(num_particles * 10, len(coords[0])))
            self.spawn_y = coords[0][indices]
            self.spawn_x = coords[1][indices]
        else:
            self.spawn_y = np.array([500])
            self.spawn_x = np.array([500])
        
        self._init_particles()
    
    def _init_particles(self):
        """Initialize particle states"""
        self.particles = []
        for i in range(self.num_particles):
            self._spawn_particle(i, random_time=True)
    
    def _spawn_particle(self, idx, random_time=False):
        """Spawn a new particle"""
        spawn_idx = np.random.randint(len(self.spawn_x))
        
        particle = {
            'x': float(self.spawn_x[spawn_idx]),
            'y': float(self.spawn_y[spawn_idx]),
            'vx': np.random.uniform(-30, 30),
            'vy': np.random.uniform(-80, -20),  # Upward
            'life': np.random.uniform(0, 1.5) if random_time else 0,
            'max_life': np.random.uniform(0.5, 1.5),
            'size': np.random.uniform(1, 4),
            'alpha': np.random.uniform(0.3, 0.8)
        }
        
        if idx < len(self.particles):
            self.particles[idx] = particle
        else:
            self.particles.append(particle)
    
    def update(self, dt):
        """Update particle positions"""
        for i, p in enumerate(self.particles):
            p['life'] += dt
            
            if p['life'] > p['max_life']:
                self._spawn_particle(i)
                continue
            
            # Physics
            p['vy'] += GRAVITY * dt * 30  # Gravity pulls down
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            
            # Fade out
            life_ratio = p['life'] / p['max_life']
            p['current_alpha'] = p['alpha'] * (1 - life_ratio)
    
    def get_particles(self, t):
        """Get current particle states"""
        return self.particles


# ============================================================================
# IMAGE ANIMATOR
# ============================================================================

class ImageAnimator:
    """Main animation engine"""
    
    def __init__(self, image_path):
        self.image_path = image_path
        self.segmenter = ImageSegmenter(image_path)
        
        self.img = self.segmenter.img
        self.arr = self.segmenter.arr.astype(float)
        self.h, self.w = self.arr.shape[:2]
        
        # Initialize physics
        self.wave_physics = WavePhysics(self.w, self.h)
        self.wind_physics = WindPhysics()
        self.bird_flight = BirdFlight(
            self.segmenter.bird_center[0],
            self.segmenter.bird_center[1],
            self.w, self.h
        )
        self.spray_particles = SprayParticles(self.segmenter.get_mask('spray_zone'))
        
        # Extract bird as separate layer
        self.bird_layer = self._extract_bird_layer()
        
        # Create background without bird
        self.background = self._create_background()
    
    def _extract_bird_layer(self):
        """Extract bird with some padding"""
        bbox = self.segmenter.bird_bbox
        padding = 20
        x1 = max(0, bbox[0] - padding)
        y1 = max(0, bbox[1] - padding)
        x2 = min(self.w, bbox[2] + padding)
        y2 = min(self.h, bbox[3] + padding)
        
        bird_region = self.arr[y1:y2, x1:x2].copy()
        
        # Create alpha based on bird mask
        bird_mask = self.segmenter.get_mask('bird')[y1:y2, x1:x2]
        
        # Soften edges
        bird_mask_float = bird_mask.astype(float)
        bird_mask_float = gaussian_filter(bird_mask_float, sigma=2)
        
        bird_region[:, :, 3] = bird_region[:, :, 3] * bird_mask_float
        
        return {
            'image': bird_region,
            'offset': (x1, y1),
            'center': (
                self.segmenter.bird_center[0] - x1,
                self.segmenter.bird_center[1] - y1
            )
        }
    
    def _create_background(self):
        """Create background with bird area inpainted"""
        bg = self.arr.copy()
        
        # Simple inpainting: blur the bird area
        bird_mask = self.segmenter.get_mask('bird')
        dilated = ndimage.binary_dilation(bird_mask, iterations=10)
        
        for c in range(3):
            channel = bg[:, :, c]
            # Get average of surrounding pixels
            blurred = gaussian_filter(channel, sigma=20)
            channel[dilated] = blurred[dilated]
        
        return bg
    
    def apply_displacement(self, image, dx, dy, mask):
        """Apply displacement map to image - optimized version"""
        h, w = image.shape[:2]
        
        # Create coordinate grids
        y_coords, x_coords = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')
        
        # Apply displacement
        new_x = (x_coords - dx).astype(np.float32)
        new_y = (y_coords - dy).astype(np.float32)
        
        # Clamp coordinates
        np.clip(new_x, 0, w - 1, out=new_x)
        np.clip(new_y, 0, h - 1, out=new_y)
        
        # Get integer coordinates for simple nearest-neighbor sampling (much faster)
        new_x_int = new_x.astype(int)
        new_y_int = new_y.astype(int)
        
        # Use fancy indexing for fast sampling
        result = image[new_y_int, new_x_int]
        
        return result
    
    def render_frame(self, t):
        """Render a single animation frame"""
        # Start with background
        frame = self.background.copy()
        
        # 1. Apply water wave displacement
        water_mask = self.segmenter.get_mask('water').astype(float)
        dx_water, dy_water = self.wave_physics.get_displacement(t, water_mask)
        frame = self.apply_displacement(frame, dx_water, dy_water, water_mask)
        
        # 2. Apply palm wind displacement
        palm_mask = self.segmenter.get_mask('palm').astype(float)
        # Find top of palm region for pivot
        palm_coords = np.where(palm_mask)
        pivot_y = palm_coords[0].max() if len(palm_coords[0]) > 0 else self.h // 2
        dx_palm, dy_palm = self.wind_physics.get_displacement(t, palm_mask, pivot_y)
        frame = self.apply_displacement(frame, dx_palm, dy_palm, palm_mask)
        
        # 3. Update and render spray particles
        dt = 1.0 / 30  # Assuming 30 fps
        self.spray_particles.update(dt)
        
        frame_img = Image.fromarray(frame.astype(np.uint8))
        draw = ImageDraw.Draw(frame_img)
        
        for p in self.spray_particles.get_particles(t):
            if 0 < p['x'] < self.w and 0 < p['y'] < self.h:
                alpha = int(p.get('current_alpha', p['alpha']) * 255)
                size = p['size']
                color = (255, 255, 255, alpha)
                draw.ellipse([
                    p['x'] - size, p['y'] - size,
                    p['x'] + size, p['y'] + size
                ], fill=color)
        
        frame = np.array(frame_img)
        
        # 4. Render bird at its current position
        bird_state = self.bird_flight.get_state(t)
        
        if bird_state['phase'] != 'flight' or bird_state['scale'] > 0.15:
            bird_img = Image.fromarray(self.bird_layer['image'].astype(np.uint8))
            
            # Scale
            scale = bird_state['scale']
            new_size = (int(bird_img.width * scale), int(bird_img.height * scale))
            if new_size[0] > 0 and new_size[1] > 0:
                bird_img = bird_img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Rotate
                bird_img = bird_img.rotate(
                    -bird_state['rotation'], 
                    resample=Image.Resampling.BILINEAR,
                    expand=True
                )
                
                # Calculate paste position
                paste_x = int(bird_state['x'] - bird_img.width // 2)
                paste_y = int(bird_state['y'] - bird_img.height // 2)
                
                # Composite onto frame
                frame_pil = Image.fromarray(frame.astype(np.uint8))
                
                if 0 <= paste_x < self.w and 0 <= paste_y < self.h:
                    # Ensure we paste within bounds
                    frame_pil.paste(bird_img, (paste_x, paste_y), bird_img)
                
                frame = np.array(frame_pil)
        
        return frame.astype(np.uint8)


# ============================================================================
# AUDIO GENERATION
# ============================================================================

def generate_beach_audio(output_path, duration):
    """Generate beach ambient audio with waves and bird sounds"""
    sample_rate = 44100
    total_samples = sample_rate * duration
    
    with wave.open(output_path, 'w') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        
        for i in range(total_samples):
            t = i / sample_rate
            
            # Ocean waves (low frequency rumble)
            wave_sound = 0
            # Multiple wave frequencies
            wave_sound += 0.15 * math.sin(2 * math.pi * 0.1 * t) * (0.5 + 0.5 * math.sin(t * 0.3))
            wave_sound += 0.1 * math.sin(2 * math.pi * 0.3 * t + 1) * (0.5 + 0.5 * math.sin(t * 0.5))
            
            # White noise for wave crash (filtered)
            noise = np.random.uniform(-1, 1)
            crash_envelope = max(0, math.sin(t * 0.4) ** 8)  # Periodic crashes
            wave_sound += noise * 0.08 * crash_envelope
            
            # Bird squawk at specific time (around 2-3.5 seconds)
            bird_sound = 0
            if 2.0 < t < 3.5:
                squawk_t = t - 2.0
                # Harsh squawk sound
                freq = 800 + 400 * math.sin(squawk_t * 30)
                bird_sound = 0.2 * math.sin(2 * math.pi * freq * t)
                bird_sound *= math.sin(squawk_t * 8) ** 2  # Modulation
                bird_sound *= max(0, 1 - squawk_t / 1.5)  # Fade out
            
            # Wing flaps after 3.5 seconds
            if 3.5 < t < 8:
                flap_t = t - 3.5
                flap_env = abs(math.sin(flap_t * 4 * math.pi))
                bird_sound += np.random.uniform(-1, 1) * 0.05 * flap_env * max(0, 1 - flap_t / 4)
            
            # Wind ambience
            wind = np.random.uniform(-1, 1) * 0.02
            wind *= 0.5 + 0.5 * math.sin(t * 0.2)
            
            # Combine
            sample = wave_sound + bird_sound + wind
            sample = max(-0.9, min(0.9, sample))
            
            sample_int = int(sample * 20000)
            wav.writeframes(struct.pack('<hh', sample_int, sample_int))


# ============================================================================
# MAIN RENDER
# ============================================================================

def render_animated_image(image_path, output_path, duration=10, fps=30):
    """Render animated image to video"""
    
    print("=" * 60)
    print("ButterflyFX IMAGE ANIMATION ENGINE")
    print("=" * 60)
    print()
    
    # Initialize animator
    print(f"Loading image: {image_path}")
    animator = ImageAnimator(image_path)
    
    # Setup temp directory
    temp_dir = tempfile.mkdtemp(prefix='butterflyfx_anim_')
    frames_dir = os.path.join(temp_dir, 'frames')
    os.makedirs(frames_dir)
    
    print(f"\nTemp: {temp_dir}")
    print(f"Output: {output_path}")
    print(f"Duration: {duration}s @ {fps}fps = {duration * fps} frames")
    print()
    
    total_frames = duration * fps
    
    print("Rendering frames...")
    for frame_num in range(total_frames):
        if frame_num % 30 == 0:
            pct = frame_num / total_frames * 100
            print(f"  Frame {frame_num}/{total_frames} ({pct:.1f}%)")
        
        t = frame_num / fps
        frame = animator.render_frame(t)
        
        # Save frame
        frame_path = os.path.join(frames_dir, f'frame_{frame_num:05d}.png')
        Image.fromarray(frame).save(frame_path)
    
    print(f"  Generated {total_frames} frames")
    
    # Generate audio
    print("\nGenerating beach audio...")
    audio_path = os.path.join(temp_dir, 'beach.wav')
    generate_beach_audio(audio_path, duration)
    print(f"  Audio: {audio_path}")
    
    # Encode video
    print("\nEncoding video...")
    result = subprocess.run([
        'ffmpeg', '-y',
        '-framerate', str(fps),
        '-i', os.path.join(frames_dir, 'frame_%05d.png'),
        '-i', audio_path,
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
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
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    print("\nTemp files cleaned up.")
    
    print("\n" + "=" * 60)
    print("ANIMATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    image_path = "/opt/butterflyfx/dimensionsos/web/static/image/bird.png"
    output_path = "/opt/butterflyfx/dimensionsos/demos/bird_animated.mp4"
    
    render_animated_image(image_path, output_path, duration=10, fps=30)
