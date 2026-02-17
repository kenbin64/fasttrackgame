"""
ButterflyFX CSS Animation Substrate
====================================

Derives CSS animations from kernel primitives.
Generates keyframes, transforms, and animated properties.

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under ButterflyFX Commercial License
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any
import math

from ..licensing import requires_license, LicenseTier
from ..substrates import Substrate, RGB, RGBA, Vector2D, Vector3D, Duration


# =============================================================================
# CSS PRIMITIVES
# =============================================================================

@dataclass
class CSSKeyframe:
    """A single keyframe in an animation"""
    percent: float  # 0-100
    properties: Dict[str, str] = field(default_factory=dict)
    
    def to_css(self) -> str:
        props = "; ".join(f"{k}: {v}" for k, v in self.properties.items())
        return f"{self.percent}% {{ {props} }}"


@dataclass
class CSSAnimation:
    """Complete CSS animation definition"""
    name: str
    keyframes: List[CSSKeyframe] = field(default_factory=list)
    duration: str = "1s"
    timing: str = "ease-in-out"
    iteration: str = "infinite"
    direction: str = "normal"
    fill_mode: str = "forwards"
    
    def to_css(self) -> str:
        keyframes_css = "\n    ".join(kf.to_css() for kf in self.keyframes)
        return f"""@keyframes {self.name} {{
    {keyframes_css}
}}"""
    
    def apply_to(self, selector: str) -> str:
        return f"""{selector} {{
    animation: {self.name} {self.duration} {self.timing} {self.iteration} {self.direction} {self.fill_mode};
}}"""


@dataclass
class CSSTransform:
    """3D CSS transform"""
    translate: Vector3D = field(default_factory=lambda: Vector3D(0, 0, 0))
    rotate: Vector3D = field(default_factory=lambda: Vector3D(0, 0, 0))  # degrees
    scale: Vector3D = field(default_factory=lambda: Vector3D(1, 1, 1))
    
    def to_css(self) -> str:
        parts = []
        if self.translate.x != 0 or self.translate.y != 0 or self.translate.z != 0:
            parts.append(f"translate3d({self.translate.x}px, {self.translate.y}px, {self.translate.z}px)")
        if self.rotate.x != 0:
            parts.append(f"rotateX({self.rotate.x}deg)")
        if self.rotate.y != 0:
            parts.append(f"rotateY({self.rotate.y}deg)")
        if self.rotate.z != 0:
            parts.append(f"rotateZ({self.rotate.z}deg)")
        if self.scale.x != 1 or self.scale.y != 1 or self.scale.z != 1:
            parts.append(f"scale3d({self.scale.x}, {self.scale.y}, {self.scale.z})")
        return " ".join(parts) if parts else "none"


# =============================================================================
# CSS ANIMATION SUBSTRATE
# =============================================================================

@requires_license("graphics")
class CSSAnimationSubstrate(Substrate):
    """
    Derives CSS animations from kernel primitives.
    
    Dimensions:
    - Time: Animation duration and keyframe positions
    - Space: 2D/3D transforms (translate, rotate, scale)
    - Color: RGB/RGBA color transitions
    - Easing: Timing functions (cubic-bezier derivations)
    
    The substrate extracts animation data by sampling these dimensions
    at keyframe positions along the timeline.
    """
    
    def __init__(self):
        super().__init__("css_animation")
        self.animations: Dict[str, CSSAnimation] = {}
        self.styles: List[str] = []
    
    # -------------------------------------------------------------------------
    # KEYFRAME GENERATION (derives from Duration primitive)
    # -------------------------------------------------------------------------
    
    def create_animation(self, name: str, duration: Duration, 
                         timing: str = "ease-in-out") -> CSSAnimation:
        """Create a new animation derived from Duration primitive"""
        anim = CSSAnimation(
            name=name,
            duration=f"{duration.seconds}s",
            timing=timing
        )
        self.animations[name] = anim
        return anim
    
    def add_keyframe(self, animation: CSSAnimation, percent: float,
                     transform: Optional[CSSTransform] = None,
                     color: Optional[RGB] = None,
                     opacity: Optional[float] = None,
                     **extra_props) -> CSSKeyframe:
        """Add keyframe - extracts transform/color data from primitives"""
        props = {}
        
        if transform:
            props["transform"] = transform.to_css()
        
        if color:
            props["color"] = f"rgb({color.r}, {color.g}, {color.b})"
            props["text-shadow"] = f"0 0 20px rgb({color.r}, {color.g}, {color.b})"
        
        if opacity is not None:
            props["opacity"] = str(opacity)
        
        props.update(extra_props)
        
        kf = CSSKeyframe(percent=percent, properties=props)
        animation.keyframes.append(kf)
        return kf
    
    # -------------------------------------------------------------------------
    # ANIMATION PRESETS (derived from mathematical functions)
    # -------------------------------------------------------------------------
    
    def pulse_animation(self, name: str = "pulse", 
                        color: RGB = RGB(255, 200, 100),
                        duration: float = 2.0) -> CSSAnimation:
        """Pulsing glow effect - derived from sine wave"""
        anim = self.create_animation(name, Duration(duration))
        
        # Sample sine wave at keyframe positions
        for percent in [0, 50, 100]:
            t = percent / 100
            scale = 1.0 + 0.1 * math.sin(t * math.pi * 2)
            opacity = 0.7 + 0.3 * math.sin(t * math.pi * 2)
            
            self.add_keyframe(anim, percent,
                transform=CSSTransform(scale=Vector3D(scale, scale, 1)),
                opacity=opacity,
                filter=f"brightness({0.8 + 0.4 * math.sin(t * math.pi * 2)})"
            )
        
        return anim
    
    def float_animation(self, name: str = "float",
                        amplitude: float = 20,
                        duration: float = 3.0) -> CSSAnimation:
        """Floating effect - derived from cosine wave"""
        anim = self.create_animation(name, Duration(duration))
        
        for percent in [0, 25, 50, 75, 100]:
            t = percent / 100
            y_offset = amplitude * math.cos(t * math.pi * 2)
            
            self.add_keyframe(anim, percent,
                transform=CSSTransform(translate=Vector3D(0, y_offset, 0))
            )
        
        return anim
    
    def rotate_3d_animation(self, name: str = "rotate3d",
                            axis: Vector3D = Vector3D(0, 1, 0),
                            duration: float = 4.0) -> CSSAnimation:
        """3D rotation - extracts rotation from Vector3D axis"""
        anim = self.create_animation(name, Duration(duration), timing="linear")
        
        self.add_keyframe(anim, 0, transform=CSSTransform(rotate=Vector3D(0, 0, 0)))
        self.add_keyframe(anim, 100, transform=CSSTransform(
            rotate=Vector3D(axis.x * 360, axis.y * 360, axis.z * 360)
        ))
        
        return anim
    
    def typewriter_animation(self, name: str = "typewriter",
                             char_count: int = 50,
                             duration: float = 3.0) -> CSSAnimation:
        """Typewriter text reveal"""
        anim = self.create_animation(name, Duration(duration), timing="steps({}, end)".format(char_count))
        anim.iteration = "1"
        
        self.add_keyframe(anim, 0, width="0")
        self.add_keyframe(anim, 100, width="100%")
        
        return anim
    
    def fade_slide_animation(self, name: str = "fadeSlide",
                             direction: Vector2D = Vector2D(0, -30),
                             duration: float = 1.0) -> CSSAnimation:
        """Fade in with slide"""
        anim = self.create_animation(name, Duration(duration))
        anim.iteration = "1"
        
        self.add_keyframe(anim, 0,
            transform=CSSTransform(translate=Vector3D(direction.x, direction.y, 0)),
            opacity=0
        )
        self.add_keyframe(anim, 100,
            transform=CSSTransform(translate=Vector3D(0, 0, 0)),
            opacity=1
        )
        
        return anim
    
    def dimension_wave_animation(self, name: str = "dimensionWave",
                                  duration: float = 2.0) -> CSSAnimation:
        """Dimensional wave effect - represents data extraction from substrate"""
        anim = self.create_animation(name, Duration(duration))
        
        # Wave represents sampling across dimensions
        for percent in [0, 20, 40, 60, 80, 100]:
            t = percent / 100
            # Extract position from wave function
            scale = 1.0 + 0.2 * math.sin(t * math.pi * 4)
            skew = 5 * math.sin(t * math.pi * 2)
            
            self.add_keyframe(anim, percent,
                transform=CSSTransform(
                    scale=Vector3D(scale, 1/scale, 1),
                ),
                filter=f"hue-rotate({int(t * 60)}deg)"
            )
        
        return anim
    
    # -------------------------------------------------------------------------
    # CSS GENERATION
    # -------------------------------------------------------------------------
    
    def generate_css(self) -> str:
        """Generate all CSS for registered animations"""
        parts = []
        
        for anim in self.animations.values():
            parts.append(anim.to_css())
        
        parts.extend(self.styles)
        
        return "\n\n".join(parts)
    
    def add_style(self, css: str):
        """Add raw CSS style"""
        self.styles.append(css)


# =============================================================================
# HTML PAGE SUBSTRATE
# =============================================================================

@requires_license("graphics")
class HTMLPageSubstrate(Substrate):
    """
    Generates complete HTML pages with CSS animations.
    
    Extracts:
    - Structure from content hierarchy
    - Timing from scene durations
    - Style from color/typography primitives
    """
    
    def __init__(self, title: str = "ButterflyFX"):
        super().__init__("html_page")
        self.title = title
        self.css_substrate = CSSAnimationSubstrate()
        self.scenes: List[Dict] = []
        self.global_styles = ""
    
    def add_scene(self, id: str, content: str, 
                  start_time: float, duration: float,
                  animation: str = "fadeSlide",
                  styles: Dict[str, str] = None) -> None:
        """Add a scene with timing"""
        self.scenes.append({
            "id": id,
            "content": content,
            "start": start_time,
            "duration": duration,
            "animation": animation,
            "styles": styles or {}
        })
    
    def generate_html(self) -> str:
        """Generate complete HTML with embedded CSS animations"""
        
        # Generate base animations
        self.css_substrate.pulse_animation()
        self.css_substrate.float_animation()
        self.css_substrate.rotate_3d_animation()
        self.css_substrate.dimension_wave_animation()
        self.css_substrate.fade_slide_animation()
        
        # Scene-specific animations
        for scene in self.scenes:
            anim_name = f"scene_{scene['id']}"
            self.css_substrate.fade_slide_animation(anim_name, duration=0.8)
        
        animations_css = self.css_substrate.generate_css()
        
        # Generate scene HTML
        scenes_html = []
        for scene in self.scenes:
            style_str = "; ".join(f"{k}: {v}" for k, v in scene["styles"].items())
            scenes_html.append(f'''
    <div class="scene" id="{scene['id']}" 
         style="animation-delay: {scene['start']}s; {style_str}">
        {scene['content']}
    </div>''')
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1280, height=720">
    <title>{self.title}</title>
    <style>
{animations_css}

{self.global_styles}
    </style>
</head>
<body>
    <div class="container">
        {"".join(scenes_html)}
    </div>
</body>
</html>'''


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'CSSKeyframe',
    'CSSAnimation', 
    'CSSTransform',
    'CSSAnimationSubstrate',
    'HTMLPageSubstrate',
]
