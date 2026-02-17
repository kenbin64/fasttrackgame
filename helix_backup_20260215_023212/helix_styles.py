"""
ButterflyFX HelixStyles - Substrate-Based Visual Presentation

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

Attribution required: Kenneth Bingham - https://butterflyfx.us

---

HelixStyles: A Revolutionary Presentation Paradigm

This is NOT CSS. This is dimensional substrate presentation where:
- Every visual element is a Token in the manifold
- Styling is "invoking" visual states, not applying properties
- Animations are spiral movements through dimensional levels
- Text/images decompose into particle swarms
- Each render is mathematically unique via phi-based seeds
- Elements exist in 3D/4D space with helix coordinates

Core Concepts:
    1. SubstrateElement - A visual element existing in the helix
    2. VisualPayload - The lazy-loaded visual representation
    3. ParticleSwarm - Decomposed elements (text chars, image pixels)
    4. HelixTransition - Movement through dimensional levels
    5. ManifoldSkin - A complete visual theme as a manifold surface

The helix provides 7 levels of visual complexity:
    Level 0 (Potential): Invisible/hidden - pure possibility
    Level 1 (Point): Single pixel/dot - minimal presence
    Level 2 (Length): Line/stroke - one-dimensional form
    Level 3 (Width): Shape outline - two-dimensional boundary
    Level 4 (Plane): Filled surface - complete 2D form
    Level 5 (Volume): 3D depth/shadow - dimensional presence
    Level 6 (Whole): Full immersive experience - 4D with time

Elements spiral between levels for transitions.
"""

from __future__ import annotations
import math
import random
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Set, Union
from enum import Enum, IntEnum
import json

# Mathematical constants
PHI = (1 + math.sqrt(5)) / 2
TAU = 2 * math.pi


# =============================================================================
# VISUAL LEVEL DEFINITIONS
# =============================================================================

class VisualLevel(IntEnum):
    """Visual complexity levels - what can be rendered at each level"""
    POTENTIAL = 0   # Invisible - element exists but not rendered
    POINT = 1       # Single point/pixel - minimal visual presence
    LENGTH = 2      # Lines/strokes - one-dimensional marks
    WIDTH = 3       # Outlines/borders - 2D boundaries
    PLANE = 4       # Filled shapes - complete 2D surfaces
    VOLUME = 5      # 3D effects - depth, shadow, perspective
    WHOLE = 6       # Full 4D - time-based, immersive, interactive


LEVEL_RENDER_CAPABILITIES = {
    0: {"opacity": 0, "dimensions": 0, "interactive": False},
    1: {"opacity": 0.1, "dimensions": 0, "interactive": False},
    2: {"opacity": 0.3, "dimensions": 1, "interactive": False},
    3: {"opacity": 0.6, "dimensions": 2, "interactive": True},
    4: {"opacity": 0.9, "dimensions": 2, "interactive": True},
    5: {"opacity": 1.0, "dimensions": 3, "interactive": True},
    6: {"opacity": 1.0, "dimensions": 4, "interactive": True},
}


# =============================================================================
# COLOR IN THE HELIX
# =============================================================================

@dataclass
class HelixColor:
    """
    Color as a point on the helix manifold.
    
    Instead of RGB/HSL, colors exist as positions on the helix:
    - Hue = angle around the helix (0 to TAU)
    - Saturation = distance from helix center
    - Lightness = vertical position (spiral number)
    - Alpha = level (0-6 maps to transparency)
    
    Colors can spiral and morph between states.
    """
    angle: float = 0.0        # Radians, hue equivalent
    radius: float = 1.0       # Saturation equivalent
    spiral: float = 0.0       # Lightness equivalent
    level: int = 6            # Alpha/complexity
    
    def to_rgb(self) -> Tuple[int, int, int]:
        """Convert helix position to RGB"""
        # Angle determines base hue (rainbow around helix)
        hue = (self.angle % TAU) / TAU
        
        # Radius determines saturation
        sat = min(1.0, max(0.0, self.radius))
        
        # Spiral determines lightness (higher spirals = brighter)
        light = 0.5 + 0.4 * math.tanh(self.spiral / 3)
        
        # HSL to RGB conversion
        if sat == 0:
            r = g = b = int(light * 255)
        else:
            def hue_to_rgb(p, q, t):
                if t < 0: t += 1
                if t > 1: t -= 1
                if t < 1/6: return p + (q - p) * 6 * t
                if t < 1/2: return q
                if t < 2/3: return p + (q - p) * (2/3 - t) * 6
                return p
            
            q = light * (1 + sat) if light < 0.5 else light + sat - light * sat
            p = 2 * light - q
            r = int(hue_to_rgb(p, q, hue + 1/3) * 255)
            g = int(hue_to_rgb(p, q, hue) * 255)
            b = int(hue_to_rgb(p, q, hue - 1/3) * 255)
        
        return (r, g, b)
    
    def to_rgba(self) -> Tuple[int, int, int, float]:
        """Convert to RGBA with level-based alpha"""
        r, g, b = self.to_rgb()
        alpha = LEVEL_RENDER_CAPABILITIES[self.level]["opacity"]
        return (r, g, b, alpha)
    
    def to_css(self) -> str:
        """Generate CSS rgba() string"""
        r, g, b, a = self.to_rgba()
        return f"rgba({r}, {g}, {b}, {a})"
    
    def to_hex(self) -> str:
        """Generate hex color"""
        r, g, b = self.to_rgb()
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def spiral_to(self, target: 'HelixColor', t: float) -> 'HelixColor':
        """Spiral interpolation to another color (not linear!)"""
        # Use phi-based spiral interpolation
        phi_t = (1 - math.cos(t * math.pi * PHI)) / 2
        
        return HelixColor(
            angle=self.angle + (target.angle - self.angle) * phi_t,
            radius=self.radius + (target.radius - self.radius) * phi_t,
            spiral=self.spiral + (target.spiral - self.spiral) * phi_t,
            level=round(self.level + (target.level - self.level) * phi_t)
        )
    
    @classmethod
    def from_rgb(cls, r: int, g: int, b: int, level: int = 6) -> 'HelixColor':
        """Create HelixColor from RGB values"""
        # RGB to HSL
        r_norm, g_norm, b_norm = r / 255, g / 255, b / 255
        max_c = max(r_norm, g_norm, b_norm)
        min_c = min(r_norm, g_norm, b_norm)
        light = (max_c + min_c) / 2
        
        if max_c == min_c:
            hue = sat = 0.0
        else:
            d = max_c - min_c
            sat = d / (2 - max_c - min_c) if light > 0.5 else d / (max_c + min_c)
            if max_c == r_norm:
                hue = ((g_norm - b_norm) / d + (6 if g_norm < b_norm else 0)) / 6
            elif max_c == g_norm:
                hue = ((b_norm - r_norm) / d + 2) / 6
            else:
                hue = ((r_norm - g_norm) / d + 4) / 6
        
        return cls(
            angle=hue * TAU,
            radius=sat,
            spiral=(light - 0.5) * 3 / 0.4,  # Inverse of to_rgb lightness
            level=level
        )


# =============================================================================
# PARTICLE SYSTEM - Text/Image Decomposition
# =============================================================================

@dataclass
class Particle:
    """
    A single particle in a swarm.
    
    Particles can represent:
    - A single character of text
    - A pixel or region of an image
    - A geometric primitive
    
    Each particle has its own helix position and can move independently.
    """
    id: str
    content: str  # The visual content (char, color, shape)
    
    # Helix position
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    level: int = 4
    spiral: int = 0
    
    # Velocity for animations
    vx: float = 0.0
    vy: float = 0.0
    vz: float = 0.0
    
    # Visual properties
    color: Optional[HelixColor] = None
    scale: float = 1.0
    rotation: float = 0.0
    opacity: float = 1.0
    
    # Behavior
    mass: float = 1.0
    drag: float = 0.02
    
    def update(self, dt: float):
        """Update particle physics"""
        # Apply drag
        self.vx *= (1 - self.drag)
        self.vy *= (1 - self.drag)
        self.vz *= (1 - self.drag)
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
    
    def attract_to(self, target_x: float, target_y: float, target_z: float, strength: float = 0.1):
        """Apply attraction force toward a target"""
        dx = target_x - self.x
        dy = target_y - self.y
        dz = target_z - self.z
        dist = math.sqrt(dx*dx + dy*dy + dz*dz) + 0.001
        
        force = strength / self.mass
        self.vx += (dx / dist) * force
        self.vy += (dy / dist) * force
        self.vz += (dz / dist) * force


@dataclass
class ParticleSwarm:
    """
    A collection of particles that can form text, images, or abstract shapes.
    
    Swarms can:
    - Explode from a shape
    - Coalesce into a new shape
    - Flow along helix paths
    - Morph text into other text
    """
    particles: List[Particle] = field(default_factory=list)
    formation: str = "scattered"  # scattered, text, grid, helix, sphere
    
    # Swarm behavior
    cohesion: float = 0.01      # How much particles stick together
    separation: float = 0.02    # How much particles avoid each other
    alignment: float = 0.01     # How much particles align velocities
    
    @classmethod
    def from_text(cls, text: str, x: float = 0, y: float = 0, 
                  char_spacing: float = 20, line_height: float = 30,
                  color: Optional[HelixColor] = None) -> 'ParticleSwarm':
        """Create a swarm from text, each character is a particle"""
        particles = []
        curr_x, curr_y = x, y
        
        for i, char in enumerate(text):
            if char == '\n':
                curr_x = x
                curr_y += line_height
                continue
            
            particles.append(Particle(
                id=f"char_{i}",
                content=char,
                x=curr_x,
                y=curr_y,
                z=0,
                color=color or HelixColor(angle=i * 0.1, level=6),
                level=6
            ))
            curr_x += char_spacing
        
        swarm = cls(particles=particles, formation="text")
        return swarm
    
    def explode(self, strength: float = 100, center_x: float = 0, center_y: float = 0):
        """Explode particles outward from center"""
        for p in self.particles:
            dx = p.x - center_x
            dy = p.y - center_y
            dist = math.sqrt(dx*dx + dy*dy) + 0.001
            p.vx += (dx / dist) * strength * random.uniform(0.5, 1.5)
            p.vy += (dy / dist) * strength * random.uniform(0.5, 1.5)
            p.vz += random.uniform(-strength, strength) * 0.3
        self.formation = "scattered"
    
    def implode(self, target_x: float, target_y: float, strength: float = 0.1):
        """Pull all particles toward a point"""
        for p in self.particles:
            p.attract_to(target_x, target_y, 0, strength)
    
    def morph_to_text(self, new_text: str, char_spacing: float = 20):
        """Morph current particles into new text formation"""
        # Calculate target positions for new text
        targets = []
        x, y = 0, 0
        for char in new_text:
            if char == '\n':
                x = 0
                y += 30
                continue
            targets.append((x, y, char))
            x += char_spacing
        
        # Match particles to targets (nearest neighbor)
        for i, (tx, ty, char) in enumerate(targets):
            if i < len(self.particles):
                p = self.particles[i]
                p.content = char
                p.attract_to(tx, ty, 0, 0.05)
            else:
                # Create new particle
                self.particles.append(Particle(
                    id=f"new_{i}",
                    content=char,
                    x=tx + random.uniform(-100, 100),
                    y=ty + random.uniform(-100, 100),
                    z=random.uniform(-50, 50),
                    level=6
                ))
                self.particles[-1].attract_to(tx, ty, 0, 0.05)
        
        # Mark excess particles for fade out
        for i in range(len(targets), len(self.particles)):
            self.particles[i].opacity *= 0.95
        
        self.formation = "text"
    
    def spiral_formation(self, center_x: float, center_y: float, radius: float = 100):
        """Arrange particles in helix spiral"""
        n = len(self.particles)
        for i, p in enumerate(self.particles):
            t = i / n * TAU * 3  # 3 rotations
            target_x = center_x + radius * math.cos(t) * (1 + i / n)
            target_y = center_y + radius * math.sin(t) * (1 + i / n)
            target_z = i * 5  # Rising helix
            p.attract_to(target_x, target_y, target_z, 0.03)
        self.formation = "helix"
    
    def update(self, dt: float):
        """Update all particles"""
        for p in self.particles:
            p.update(dt)
        
        # Remove faded particles
        self.particles = [p for p in self.particles if p.opacity > 0.01]


# =============================================================================
# SUBSTRATE ELEMENT - Visual Elements as Tokens
# =============================================================================

class ElementType(Enum):
    """Types of substrate elements"""
    CONTAINER = "container"
    TEXT = "text"
    IMAGE = "image"
    SHAPE = "shape"
    PARTICLE_SYSTEM = "particle"
    VIDEO = "video"
    CANVAS_3D = "canvas3d"
    PORTAL = "portal"  # A window into another dimensional space


@dataclass
class SubstrateElement:
    """
    A visual element existing in the helix manifold.
    
    Unlike CSS where you apply styles TO elements,
    here the element IS its visual representation -
    it exists at a certain level with inherent properties.
    """
    id: str
    element_type: ElementType
    
    # Helix position
    level: int = 4
    spiral: int = 0
    angle: float = 0.0  # Position around the helix at this level
    
    # Content (lazy-loaded)
    content: Any = None
    content_loader: Optional[Callable] = None
    
    # Signature - which levels this element manifests at
    signature: Set[int] = field(default_factory=lambda: {4, 5, 6})
    
    # Visual properties (derived from helix position)
    _cached_visuals: Optional[Dict] = None
    
    # Particle decomposition
    particles: Optional[ParticleSwarm] = None
    is_decomposed: bool = False
    
    # Children (for containers)
    children: List['SubstrateElement'] = field(default_factory=list)
    
    def get_visuals(self) -> Dict[str, Any]:
        """
        Derive visual properties from helix position.
        
        This is the core magic - visuals emerge from position,
        not from explicit property assignment.
        """
        if self._cached_visuals is not None:
            return self._cached_visuals
        
        # Level determines complexity/opacity
        capabilities = LEVEL_RENDER_CAPABILITIES[self.level]
        
        # Angle determines hue
        hue_angle = self.angle % TAU
        
        # Spiral determines scale and depth
        scale = PHI ** (self.spiral * 0.1)
        z_depth = self.spiral * 10
        
        # Derive base color from position
        base_color = HelixColor(
            angle=hue_angle,
            radius=0.8,
            spiral=self.spiral,
            level=self.level
        )
        
        visuals = {
            "opacity": capabilities["opacity"],
            "dimensions": capabilities["dimensions"],
            "interactive": capabilities["interactive"],
            "color": base_color,
            "scale": scale,
            "z_depth": z_depth,
            "glow_intensity": 0.3 if self.level >= 5 else 0,
            "shadow_depth": z_depth * 0.5 if self.level >= 5 else 0,
            "blur": max(0, (6 - self.level) * 2),  # Lower levels are blurrier
        }
        
        self._cached_visuals = visuals
        return visuals
    
    def spiral_up(self) -> 'SubstrateElement':
        """Move to higher level (more complex/visible)"""
        if self.level < 6:
            self.level += 1
            self._cached_visuals = None
        return self
    
    def spiral_down(self) -> 'SubstrateElement':
        """Move to lower level (simpler/less visible)"""
        if self.level > 0:
            self.level -= 1
            self._cached_visuals = None
        return self
    
    def invoke_at(self, level: int) -> 'SubstrateElement':
        """Invoke element at specific level"""
        self.level = max(0, min(6, level))
        self._cached_visuals = None
        return self
    
    def decompose(self):
        """Decompose element into particles"""
        if self.element_type == ElementType.TEXT and self.content:
            self.particles = ParticleSwarm.from_text(str(self.content))
            self.is_decomposed = True
        elif self.element_type == ElementType.SHAPE:
            # Decompose shape into point particles
            pass  # TODO: Implement shape decomposition
    
    def recompose(self):
        """Recompose particles back into element"""
        self.is_decomposed = False
    
    def to_css(self) -> Dict[str, str]:
        """
        Generate CSS-compatible styles.
        
        This bridges to traditional CSS for compatibility,
        but the true representation is the helix position.
        """
        visuals = self.get_visuals()
        color = visuals["color"]
        
        css = {
            "opacity": str(visuals["opacity"]),
            "transform": f"scale({visuals['scale']}) translateZ({visuals['z_depth']}px)",
            "color": color.to_css(),
            "filter": f"blur({visuals['blur']}px)",
        }
        
        if visuals["glow_intensity"] > 0:
            glow_color = color.to_css()
            css["box-shadow"] = f"0 0 {visuals['glow_intensity'] * 20}px {glow_color}"
        
        if visuals["shadow_depth"] > 0:
            css["box-shadow"] = f"0 {visuals['shadow_depth']}px {visuals['shadow_depth'] * 2}px rgba(0,0,0,0.3)"
        
        return css


# =============================================================================
# HELIX TRANSITION - Movement Through Levels
# =============================================================================

class TransitionType(Enum):
    """Types of helix transitions"""
    SPIRAL_UP = "spiral_up"      # Rise through levels
    SPIRAL_DOWN = "spiral_down"  # Descend through levels
    ORBIT = "orbit"              # Circle around current level
    WARP = "warp"                # Jump across spirals
    MORPH = "morph"              # Transform to different element
    EXPLODE = "explode"          # Decompose into particles
    COALESCE = "coalesce"        # Particles form shape
    PHASE = "phase"              # Shift in/out of visibility


@dataclass
class HelixTransition:
    """
    A transition is movement through the helix.
    
    Unlike CSS transitions that interpolate properties,
    helix transitions move elements through dimensional space.
    """
    transition_type: TransitionType
    duration: float = 1.0  # seconds
    
    # Start and end states
    from_level: int = 0
    to_level: int = 6
    from_spiral: int = 0
    to_spiral: int = 0
    
    # Easing via helix mathematics
    phi_factor: float = PHI  # Golden ratio easing
    
    # Current progress
    progress: float = 0.0
    started_at: float = 0.0
    
    def start(self):
        """Start the transition"""
        self.started_at = time.time()
        self.progress = 0.0
    
    def update(self) -> float:
        """Update and return current progress (0-1)"""
        if self.duration <= 0:
            return 1.0
        
        elapsed = time.time() - self.started_at
        self.progress = min(1.0, elapsed / self.duration)
        
        # Apply phi-based easing
        # This creates a more organic, spiral-like movement
        eased = self._phi_ease(self.progress)
        return eased
    
    def _phi_ease(self, t: float) -> float:
        """
        Phi-based easing function.
        
        Creates a natural, golden-ratio based acceleration/deceleration
        that mimics natural spiral movement.
        """
        if t <= 0:
            return 0
        if t >= 1:
            return 1
        
        # Combine multiple phi-derived frequencies
        return (
            0.5 * (1 - math.cos(t * math.pi)) +  # Base ease
            0.3 * math.sin(t * math.pi * self.phi_factor) * (1 - t) +  # Phi oscillation
            0.2 * t * t * (3 - 2 * t)  # Smooth step
        )
    
    def get_current_level(self) -> float:
        """Get interpolated level at current progress"""
        eased = self._phi_ease(self.progress)
        return self.from_level + (self.to_level - self.from_level) * eased
    
    @property
    def is_complete(self) -> bool:
        return self.progress >= 1.0


# =============================================================================
# MANIFOLD SKIN - Complete Visual Theme
# =============================================================================

@dataclass
class ManifoldSkin:
    """
    A complete visual theme as a manifold surface.
    
    Instead of a CSS stylesheet, a ManifoldSkin defines
    the visual characteristics of the entire helix space.
    
    Elements placed in this space inherit visual properties
    from their position on the manifold surface.
    """
    name: str
    
    # Base helix properties
    radius_scale: float = 1.0
    pitch_scale: float = PHI
    
    # Color gradient across levels
    level_colors: Dict[int, HelixColor] = field(default_factory=dict)
    
    # Level-specific visual modifiers
    level_blur: Dict[int, float] = field(default_factory=dict)
    level_glow: Dict[int, float] = field(default_factory=dict)
    level_scale: Dict[int, float] = field(default_factory=dict)
    
    # Global effects
    ambient_particles: bool = False
    particle_density: float = 0.1
    background_spiral: bool = True
    
    # 3D/4D properties
    perspective_depth: float = 1000
    time_scale: float = 1.0
    
    def apply_to_element(self, element: SubstrateElement) -> Dict[str, Any]:
        """Apply skin properties to an element based on its position"""
        level = element.level
        
        # Get level-specific properties
        color = self.level_colors.get(level, HelixColor(level=level))
        blur = self.level_blur.get(level, max(0, (6 - level) * 2))
        glow = self.level_glow.get(level, 0.3 if level >= 5 else 0)
        scale = self.level_scale.get(level, 1.0)
        
        return {
            "color": color,
            "blur": blur,
            "glow": glow,
            "scale": scale * self.radius_scale,
            "perspective": self.perspective_depth,
        }
    
    @classmethod
    def default_dark(cls) -> 'ManifoldSkin':
        """Create default dark theme"""
        return cls(
            name="dark",
            level_colors={
                0: HelixColor.from_rgb(255, 255, 255, 0),
                1: HelixColor.from_rgb(100, 150, 255, 1),
                2: HelixColor.from_rgb(150, 100, 255, 2),
                3: HelixColor.from_rgb(200, 100, 200, 3),
                4: HelixColor.from_rgb(255, 100, 150, 4),
                5: HelixColor.from_rgb(255, 150, 100, 5),
                6: HelixColor.from_rgb(255, 200, 100, 6),
            },
            ambient_particles=True,
            background_spiral=True,
        )
    
    @classmethod
    def neon_cyber(cls) -> 'ManifoldSkin':
        """Cyberpunk neon theme"""
        return cls(
            name="neon",
            level_colors={
                0: HelixColor.from_rgb(0, 0, 0, 0),
                1: HelixColor.from_rgb(255, 0, 128, 1),
                2: HelixColor.from_rgb(0, 255, 128, 2),
                3: HelixColor.from_rgb(0, 128, 255, 3),
                4: HelixColor.from_rgb(255, 128, 0, 4),
                5: HelixColor.from_rgb(128, 0, 255, 5),
                6: HelixColor.from_rgb(255, 255, 0, 6),
            },
            level_glow={i: i * 0.2 for i in range(7)},
            ambient_particles=True,
            particle_density=0.3,
        )


# =============================================================================
# HELIX PRESENTATION ENGINE
# =============================================================================

class HelixPresentation:
    """
    The main presentation engine.
    
    This orchestrates all substrate elements, transitions,
    particles, and renders to various outputs.
    """
    
    def __init__(self, skin: Optional[ManifoldSkin] = None):
        self.skin = skin or ManifoldSkin.default_dark()
        self.elements: Dict[str, SubstrateElement] = {}
        self.active_transitions: List[HelixTransition] = []
        self.particle_systems: List[ParticleSwarm] = []
        self.time = 0.0
        self.time_scale = 1.0
    
    def add_element(self, element: SubstrateElement) -> SubstrateElement:
        """Add an element to the presentation"""
        self.elements[element.id] = element
        return element
    
    def create_text(self, id: str, content: str, level: int = 6) -> SubstrateElement:
        """Create a text element"""
        elem = SubstrateElement(
            id=id,
            element_type=ElementType.TEXT,
            content=content,
            level=level
        )
        return self.add_element(elem)
    
    def create_container(self, id: str, level: int = 6) -> SubstrateElement:
        """Create a container element"""
        elem = SubstrateElement(
            id=id,
            element_type=ElementType.CONTAINER,
            level=level
        )
        return self.add_element(elem)
    
    def transition(self, element_id: str, transition_type: TransitionType,
                   to_level: int, duration: float = 1.0) -> HelixTransition:
        """Start a transition on an element"""
        if element_id not in self.elements:
            raise ValueError(f"Element {element_id} not found")
        
        elem = self.elements[element_id]
        trans = HelixTransition(
            transition_type=transition_type,
            from_level=elem.level,
            to_level=to_level,
            duration=duration
        )
        trans.start()
        self.active_transitions.append(trans)
        return trans
    
    def update(self, dt: float):
        """Update all animations and particles"""
        self.time += dt * self.time_scale
        
        # Update transitions
        for trans in self.active_transitions[:]:
            trans.update()
            if trans.is_complete:
                self.active_transitions.remove(trans)
        
        # Update particle systems
        for ps in self.particle_systems:
            ps.update(dt)
        
        # Update element particles
        for elem in self.elements.values():
            if elem.particles:
                elem.particles.update(dt)
    
    def render_to_json(self) -> str:
        """Render current state to JSON for JavaScript consumption"""
        state = {
            "time": self.time,
            "skin": self.skin.name,
            "elements": {}
        }
        
        for id, elem in self.elements.items():
            visuals = elem.get_visuals()
            state["elements"][id] = {
                "type": elem.element_type.value,
                "level": elem.level,
                "spiral": elem.spiral,
                "angle": elem.angle,
                "content": str(elem.content) if elem.content else None,
                "visuals": {
                    "opacity": visuals["opacity"],
                    "color": visuals["color"].to_css(),
                    "scale": visuals["scale"],
                    "blur": visuals["blur"],
                    "glow": visuals["glow_intensity"],
                },
                "is_decomposed": elem.is_decomposed,
                "particles": None  # TODO: Serialize particles
            }
        
        return json.dumps(state, indent=2)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_presentation(skin_name: str = "dark") -> HelixPresentation:
    """Create a new presentation with specified skin"""
    skins = {
        "dark": ManifoldSkin.default_dark,
        "neon": ManifoldSkin.neon_cyber,
    }
    skin = skins.get(skin_name, ManifoldSkin.default_dark)()
    return HelixPresentation(skin)


def text_swarm(text: str, explode: bool = False) -> ParticleSwarm:
    """Quick helper to create a text particle swarm"""
    swarm = ParticleSwarm.from_text(text)
    if explode:
        swarm.explode()
    return swarm


def helix_color(hue: float, saturation: float = 1.0, lightness: float = 0.5) -> HelixColor:
    """Create a helix color from HSL-like values"""
    return HelixColor(
        angle=hue * TAU,
        radius=saturation,
        spiral=(lightness - 0.5) * 6,
        level=6
    )


# Quick test
if __name__ == "__main__":
    print("HelixStyles - Substrate Presentation System")
    print("=" * 50)
    
    # Create a presentation
    pres = create_presentation("neon")
    
    # Add some elements
    title = pres.create_text("title", "ButterflyFX", level=6)
    subtitle = pres.create_text("subtitle", "Dimensional Computing", level=4)
    
    # Decompose title into particles
    title.decompose()
    print(f"Title decomposed into {len(title.particles.particles)} particles")
    
    # Show visual properties
    print(f"\nTitle visuals: {title.get_visuals()}")
    print(f"Subtitle visuals: {subtitle.get_visuals()}")
    
    # Create swarm morphing demo
    swarm = text_swarm("HELLO WORLD")
    print(f"\nSwarm has {len(swarm.particles)} particles")
    swarm.explode(50)
    
    # Show JSON output
    print("\n" + pres.render_to_json())
