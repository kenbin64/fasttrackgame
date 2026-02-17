"""
ButterflyFX Manifold Presentation Engine

Copyright (c) 2024-2026 Kenneth Bingham. All Rights Reserved.

This is a DERIVED IMPLEMENTATION built on the open source mathematical kernel.
This file is proprietary software. See /helix/LICENSE for details.

---

Websites as timelines, not pages.

TRADITIONAL WEB:
    - Static pages
    - Scroll for more content
    - Click links to navigate
    - Content exists in space

MANIFOLD PRESENTATION:
    - Dynamic timeline
    - Scrub progress bar to navigate
    - Content animates through time
    - Rewind, fast-forward, replay
    - Marks for specific moments
    - Like a video, but for any content

The manifold describes content as f(t) where t is the timeline position.
Any moment can be computed instantly - just evaluate at that t.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Union, Tuple
from enum import Enum, auto
import json
import math
import time


# =============================================================================
# TIMELINE TYPES
# =============================================================================

class EasingFunction(Enum):
    """Animation easing functions"""
    LINEAR = "linear"
    EASE_IN = "ease-in"
    EASE_OUT = "ease-out"
    EASE_IN_OUT = "ease-in-out"
    BOUNCE = "bounce"
    ELASTIC = "elastic"


class ContentType(Enum):
    """Types of content on the timeline"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    SHAPE = "shape"
    CHART = "chart"
    CODE = "code"
    HTML = "html"
    COMPONENT = "component"


# =============================================================================
# KEYFRAME - A moment in time
# =============================================================================

@dataclass
class Keyframe:
    """
    A keyframe defines properties at a specific moment.
    
    The presentation interpolates between keyframes.
    """
    time: float                    # 0.0 to 1.0 (normalized timeline)
    properties: Dict[str, Any]     # Property values at this moment
    easing: EasingFunction = EasingFunction.EASE_IN_OUT
    
    def to_dict(self) -> dict:
        return {
            "time": self.time,
            "properties": self.properties,
            "easing": self.easing.value
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Keyframe':
        return cls(
            time=data["time"],
            properties=data["properties"],
            easing=EasingFunction(data.get("easing", "ease-in-out"))
        )


# =============================================================================
# CONTENT ELEMENT - Something on the timeline
# =============================================================================

@dataclass
class ContentElement:
    """
    A piece of content that exists on the timeline.
    
    Each element has:
        - An ID for reference
        - A type (text, image, etc.)
        - Keyframes defining its state over time
        - Entry/exit points on the timeline
    """
    id: str
    content_type: ContentType
    content: Any                           # The actual content
    keyframes: List[Keyframe] = field(default_factory=list)
    enter_time: float = 0.0                # When it appears (0-1)
    exit_time: float = 1.0                 # When it disappears (0-1)
    layer: int = 0                         # Z-index for stacking
    
    def is_visible(self, t: float) -> bool:
        """Check if element is visible at time t"""
        return self.enter_time <= t <= self.exit_time
    
    def get_properties(self, t: float) -> Dict[str, Any]:
        """
        Get interpolated properties at time t.
        
        This is the MANIFOLD evaluation - compute state from time.
        """
        if not self.keyframes:
            return {}
        
        # Find surrounding keyframes
        before = None
        after = None
        
        for kf in self.keyframes:
            if kf.time <= t:
                before = kf
            if kf.time >= t and after is None:
                after = kf
        
        # Edge cases
        if before is None:
            return self.keyframes[0].properties.copy()
        if after is None or before == after:
            return before.properties.copy()
        
        # Interpolate
        progress = (t - before.time) / (after.time - before.time)
        eased = self._apply_easing(progress, after.easing)
        
        return self._interpolate(before.properties, after.properties, eased)
    
    def _apply_easing(self, t: float, easing: EasingFunction) -> float:
        """Apply easing function to progress value"""
        if easing == EasingFunction.LINEAR:
            return t
        elif easing == EasingFunction.EASE_IN:
            return t * t
        elif easing == EasingFunction.EASE_OUT:
            return 1 - (1 - t) * (1 - t)
        elif easing == EasingFunction.EASE_IN_OUT:
            return 3 * t * t - 2 * t * t * t
        elif easing == EasingFunction.BOUNCE:
            if t < 0.5:
                return 8 * t * t * t * t
            else:
                return 1 - 8 * (1 - t) ** 4
        elif easing == EasingFunction.ELASTIC:
            if t == 0 or t == 1:
                return t
            return math.sin(13 * math.pi / 2 * t) * math.pow(2, 10 * (t - 1))
        return t
    
    def _interpolate(self, start: Dict, end: Dict, t: float) -> Dict:
        """Interpolate between two property sets"""
        result = {}
        
        all_keys = set(start.keys()) | set(end.keys())
        
        for key in all_keys:
            start_val = start.get(key, 0)
            end_val = end.get(key, 0)
            
            if isinstance(start_val, (int, float)) and isinstance(end_val, (int, float)):
                # Numeric interpolation
                result[key] = start_val + (end_val - start_val) * t
            elif isinstance(start_val, str) and isinstance(end_val, str):
                # Color interpolation if both are hex colors
                if start_val.startswith('#') and end_val.startswith('#'):
                    result[key] = self._interpolate_color(start_val, end_val, t)
                else:
                    # String - snap at midpoint
                    result[key] = start_val if t < 0.5 else end_val
            else:
                # Non-interpolatable - snap at midpoint
                result[key] = start_val if t < 0.5 else end_val
        
        return result
    
    def _interpolate_color(self, start: str, end: str, t: float) -> str:
        """Interpolate between two hex colors"""
        def hex_to_rgb(h):
            h = h.lstrip('#')
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return '#{:02x}{:02x}{:02x}'.format(*[int(c) for c in rgb])
        
        start_rgb = hex_to_rgb(start)
        end_rgb = hex_to_rgb(end)
        
        result_rgb = tuple(s + (e - s) * t for s, e in zip(start_rgb, end_rgb))
        return rgb_to_hex(result_rgb)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.content_type.value,
            "content": self.content,
            "keyframes": [kf.to_dict() for kf in self.keyframes],
            "enter": self.enter_time,
            "exit": self.exit_time,
            "layer": self.layer
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ContentElement':
        return cls(
            id=data["id"],
            content_type=ContentType(data["type"]),
            content=data["content"],
            keyframes=[Keyframe.from_dict(kf) for kf in data.get("keyframes", [])],
            enter_time=data.get("enter", 0.0),
            exit_time=data.get("exit", 1.0),
            layer=data.get("layer", 0)
        )


# =============================================================================
# TIMELINE MARKER - Named positions
# =============================================================================

@dataclass
class TimelineMarker:
    """
    A named position on the timeline.
    
    Users can click markers to jump to specific moments.
    Like chapters in a video.
    """
    id: str
    name: str
    time: float           # 0.0 to 1.0
    icon: Optional[str] = None
    color: str = "#3b82f6"
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "time": self.time,
            "icon": self.icon,
            "color": self.color
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TimelineMarker':
        return cls(
            id=data["id"],
            name=data["name"],
            time=data["time"],
            icon=data.get("icon"),
            color=data.get("color", "#3b82f6")
        )


# =============================================================================
# PRESENTATION - The full timeline
# =============================================================================

@dataclass
class Presentation:
    """
    A manifold presentation - content as a function of time.
    
    Features:
        - Elements appear/disappear at specific times
        - Properties animate between keyframes
        - Markers for navigation
        - Can be evaluated at any time t
    """
    id: str
    title: str
    duration_seconds: float = 60.0
    elements: List[ContentElement] = field(default_factory=list)
    markers: List[TimelineMarker] = field(default_factory=list)
    background: str = "#000000"
    width: int = 1920
    height: int = 1080
    
    def add_element(self, element: ContentElement) -> 'Presentation':
        """Add an element to the presentation"""
        self.elements.append(element)
        return self
    
    def add_marker(self, marker: TimelineMarker) -> 'Presentation':
        """Add a marker to the timeline"""
        self.markers.append(marker)
        return self
    
    def get_state(self, t: float) -> Dict[str, Any]:
        """
        Get the complete presentation state at time t.
        
        This is the MANIFOLD - compute everything from the timeline position.
        """
        # Clamp t to [0, 1]
        t = max(0.0, min(1.0, t))
        
        visible_elements = []
        
        for element in sorted(self.elements, key=lambda e: e.layer):
            if element.is_visible(t):
                props = element.get_properties(t)
                visible_elements.append({
                    "id": element.id,
                    "type": element.content_type.value,
                    "content": element.content,
                    "properties": props,
                    "layer": element.layer
                })
        
        return {
            "time": t,
            "time_seconds": t * self.duration_seconds,
            "elements": visible_elements,
            "background": self.background,
            "width": self.width,
            "height": self.height
        }
    
    def get_marker_at(self, t: float, tolerance: float = 0.02) -> Optional[TimelineMarker]:
        """Find marker near time t"""
        for marker in self.markers:
            if abs(marker.time - t) <= tolerance:
                return marker
        return None
    
    def next_marker(self, t: float) -> Optional[TimelineMarker]:
        """Get the next marker after time t"""
        future = [m for m in self.markers if m.time > t]
        return min(future, key=lambda m: m.time) if future else None
    
    def prev_marker(self, t: float) -> Optional[TimelineMarker]:
        """Get the previous marker before time t"""
        past = [m for m in self.markers if m.time < t]
        return max(past, key=lambda m: m.time) if past else None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "duration": self.duration_seconds,
            "elements": [e.to_dict() for e in self.elements],
            "markers": [m.to_dict() for m in self.markers],
            "background": self.background,
            "width": self.width,
            "height": self.height
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Presentation':
        return cls(
            id=data["id"],
            title=data["title"],
            duration_seconds=data.get("duration", 60.0),
            elements=[ContentElement.from_dict(e) for e in data.get("elements", [])],
            markers=[TimelineMarker.from_dict(m) for m in data.get("markers", [])],
            background=data.get("background", "#000000"),
            width=data.get("width", 1920),
            height=data.get("height", 1080)
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Presentation':
        return cls.from_dict(json.loads(json_str))


# =============================================================================
# PRESENTATION BUILDER - Easy API for creating presentations
# =============================================================================

class PresentationBuilder:
    """
    Fluent builder for creating presentations.
    
    Usage:
        pres = (PresentationBuilder("my-presentation", "My Title")
            .duration(120)
            .background("#1a1a2e")
            .text("title", "Welcome!", x=100, y=100)
                .animate(0, 0.5, opacity=0)
                .animate(0.1, 1.0, opacity=1, scale=1.2)
                .until(0.5)
            .marker("intro", "Introduction", 0.0)
            .image("logo", "/logo.png", x=800, y=100)
                .animate(0.2, 1.0, opacity=0)
                .animate(0.3, 1.0, opacity=1, rotate=360)
            .marker("content", "Main Content", 0.3)
            .build())
    """
    
    def __init__(self, id: str, title: str):
        self._presentation = Presentation(id=id, title=title)
        self._current_element: Optional[ContentElement] = None
    
    def duration(self, seconds: float) -> 'PresentationBuilder':
        """Set presentation duration in seconds"""
        self._presentation.duration_seconds = seconds
        return self
    
    def background(self, color: str) -> 'PresentationBuilder':
        """Set background color"""
        self._presentation.background = color
        return self
    
    def size(self, width: int, height: int) -> 'PresentationBuilder':
        """Set presentation dimensions"""
        self._presentation.width = width
        self._presentation.height = height
        return self
    
    def _finish_element(self):
        """Finish current element and add to presentation"""
        if self._current_element:
            self._presentation.add_element(self._current_element)
            self._current_element = None
    
    def text(
        self, 
        id: str, 
        content: str, 
        x: float = 0, 
        y: float = 0,
        font_size: float = 24,
        color: str = "#ffffff",
        enter: float = 0.0,
        layer: int = 0
    ) -> 'PresentationBuilder':
        """Add a text element"""
        self._finish_element()
        
        self._current_element = ContentElement(
            id=id,
            content_type=ContentType.TEXT,
            content=content,
            enter_time=enter,
            layer=layer,
            keyframes=[
                Keyframe(enter, {
                    "x": x,
                    "y": y,
                    "fontSize": font_size,
                    "color": color,
                    "opacity": 1.0,
                    "scale": 1.0,
                    "rotate": 0
                })
            ]
        )
        return self
    
    def image(
        self,
        id: str,
        src: str,
        x: float = 0,
        y: float = 0,
        width: Optional[float] = None,
        height: Optional[float] = None,
        enter: float = 0.0,
        layer: int = 0
    ) -> 'PresentationBuilder':
        """Add an image element"""
        self._finish_element()
        
        props = {
            "x": x,
            "y": y,
            "opacity": 1.0,
            "scale": 1.0,
            "rotate": 0
        }
        if width:
            props["width"] = width
        if height:
            props["height"] = height
        
        self._current_element = ContentElement(
            id=id,
            content_type=ContentType.IMAGE,
            content=src,
            enter_time=enter,
            layer=layer,
            keyframes=[Keyframe(enter, props)]
        )
        return self
    
    def shape(
        self,
        id: str,
        shape_type: str,  # "rect", "circle", "line", etc.
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 100,
        fill: str = "#3b82f6",
        enter: float = 0.0,
        layer: int = 0
    ) -> 'PresentationBuilder':
        """Add a shape element"""
        self._finish_element()
        
        self._current_element = ContentElement(
            id=id,
            content_type=ContentType.SHAPE,
            content=shape_type,
            enter_time=enter,
            layer=layer,
            keyframes=[Keyframe(enter, {
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "fill": fill,
                "opacity": 1.0,
                "scale": 1.0,
                "rotate": 0
            })]
        )
        return self
    
    def code(
        self,
        id: str,
        content: str,
        language: str = "python",
        x: float = 0,
        y: float = 0,
        enter: float = 0.0,
        layer: int = 0
    ) -> 'PresentationBuilder':
        """Add a code block element"""
        self._finish_element()
        
        self._current_element = ContentElement(
            id=id,
            content_type=ContentType.CODE,
            content={"code": content, "language": language},
            enter_time=enter,
            layer=layer,
            keyframes=[Keyframe(enter, {
                "x": x,
                "y": y,
                "opacity": 1.0,
                "scale": 1.0
            })]
        )
        return self
    
    def html(
        self,
        id: str,
        content: str,
        x: float = 0,
        y: float = 0,
        enter: float = 0.0,
        layer: int = 0
    ) -> 'PresentationBuilder':
        """Add raw HTML element"""
        self._finish_element()
        
        self._current_element = ContentElement(
            id=id,
            content_type=ContentType.HTML,
            content=content,
            enter_time=enter,
            layer=layer,
            keyframes=[Keyframe(enter, {
                "x": x,
                "y": y,
                "opacity": 1.0,
                "scale": 1.0
            })]
        )
        return self
    
    def animate(
        self,
        time: float,
        easing: EasingFunction = EasingFunction.EASE_IN_OUT,
        **properties
    ) -> 'PresentationBuilder':
        """
        Add a keyframe to the current element.
        
        Usage:
            .text("title", "Hello")
            .animate(0.0, opacity=0)      # Start invisible
            .animate(0.1, opacity=1.0)    # Fade in
            .animate(0.5, x=100, y=200)   # Move
        """
        if not self._current_element:
            raise ValueError("No current element to animate")
        
        # Start with previous keyframe's properties
        if self._current_element.keyframes:
            base_props = self._current_element.keyframes[-1].properties.copy()
        else:
            base_props = {}
        
        # Override with new properties
        base_props.update(properties)
        
        self._current_element.keyframes.append(
            Keyframe(time, base_props, easing)
        )
        return self
    
    def until(self, time: float) -> 'PresentationBuilder':
        """Set when the current element exits"""
        if self._current_element:
            self._current_element.exit_time = time
        return self
    
    def marker(self, id: str, name: str, time: float, icon: str = None, color: str = "#3b82f6") -> 'PresentationBuilder':
        """Add a timeline marker"""
        self._finish_element()
        self._presentation.add_marker(TimelineMarker(
            id=id,
            name=name,
            time=time,
            icon=icon,
            color=color
        ))
        return self
    
    def build(self) -> Presentation:
        """Build and return the presentation"""
        self._finish_element()
        return self._presentation


# =============================================================================
# HTML GENERATOR - Generate playable HTML
# =============================================================================

class HTMLGenerator:
    """
    Generate a standalone HTML file that plays the presentation.
    
    The generated HTML includes:
        - Progress bar/scrubber
        - Play/pause controls
        - Marker navigation
        - Keyboard shortcuts
        - Full presentation renderer
    """
    
    @staticmethod
    def generate(presentation: Presentation) -> str:
        """Generate complete HTML for the presentation"""
        
        # Convert presentation to JSON for embedding
        data_json = presentation.to_json()
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{presentation.title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: white;
            overflow: hidden;
            height: 100vh;
        }}
        
        #presentation {{
            position: relative;
            width: 100vw;
            height: calc(100vh - 80px);
            overflow: hidden;
        }}
        
        #stage {{
            position: absolute;
            transform-origin: top left;
        }}
        
        .element {{
            position: absolute;
            transition: none;
        }}
        
        .element.text {{
            white-space: pre-wrap;
        }}
        
        .element.code {{
            background: #1e1e1e;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Fira Code', 'Consolas', monospace;
            overflow: auto;
        }}
        
        /* Controls */
        #controls {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 80px;
            background: linear-gradient(transparent, rgba(0,0,0,0.9));
            padding: 15px 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        
        #timeline {{
            position: relative;
            height: 24px;
            background: #333;
            border-radius: 12px;
            cursor: pointer;
        }}
        
        #progress {{
            height: 100%;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6);
            border-radius: 12px;
            width: 0%;
            pointer-events: none;
        }}
        
        #scrubber {{
            position: absolute;
            top: 50%;
            transform: translate(-50%, -50%);
            width: 16px;
            height: 16px;
            background: white;
            border-radius: 50%;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            cursor: grab;
        }}
        
        #scrubber:active {{
            cursor: grabbing;
        }}
        
        .marker {{
            position: absolute;
            top: 50%;
            transform: translate(-50%, -50%);
            width: 8px;
            height: 8px;
            border-radius: 50%;
            cursor: pointer;
            z-index: 10;
        }}
        
        .marker:hover::after {{
            content: attr(data-name);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: #333;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            white-space: nowrap;
            margin-bottom: 8px;
        }}
        
        #buttons {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        button {{
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            padding: 8px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        button:hover {{
            background: rgba(255,255,255,0.1);
        }}
        
        button svg {{
            width: 24px;
            height: 24px;
        }}
        
        #time-display {{
            font-size: 14px;
            color: #888;
            font-variant-numeric: tabular-nums;
        }}
        
        #marker-nav {{
            display: flex;
            gap: 8px;
            margin-left: auto;
        }}
        
        .marker-btn {{
            padding: 6px 12px;
            font-size: 12px;
            border-radius: 4px;
        }}
        
        /* Keyboard hint */
        #hint {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.7);
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 12px;
            color: #888;
        }}
        
        #hint kbd {{
            background: #333;
            padding: 2px 6px;
            border-radius: 4px;
            margin: 0 2px;
        }}
    </style>
</head>
<body>
    <div id="presentation">
        <div id="stage"></div>
    </div>
    
    <div id="controls">
        <div id="timeline">
            <div id="progress"></div>
            <div id="scrubber"></div>
            <!-- Markers will be inserted here -->
        </div>
        <div id="buttons">
            <button id="prev-marker" title="Previous marker (,)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M19 20L9 12l10-8v16z"/>
                    <path d="M5 19V5"/>
                </svg>
            </button>
            <button id="play-pause" title="Play/Pause (Space)">
                <svg id="play-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8 5v14l11-7z"/>
                </svg>
                <svg id="pause-icon" viewBox="0 0 24 24" fill="currentColor" style="display:none">
                    <path d="M6 4h4v16H6zM14 4h4v16h-4z"/>
                </svg>
            </button>
            <button id="next-marker" title="Next marker (.)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M5 4l10 8-10 8V4z"/>
                    <path d="M19 5v14"/>
                </svg>
            </button>
            <span id="time-display">0:00 / 0:00</span>
            <div id="marker-nav"></div>
        </div>
    </div>
    
    <div id="hint">
        <kbd>Space</kbd> Play/Pause
        <kbd>,</kbd> <kbd>.</kbd> Markers
        <kbd>←</kbd> <kbd>→</kbd> Seek
    </div>

    <script>
        // Presentation data
        const presentationData = {data_json};
        
        // State
        let currentTime = 0;
        let isPlaying = false;
        let lastFrameTime = 0;
        
        // Elements
        const stage = document.getElementById('stage');
        const progress = document.getElementById('progress');
        const scrubber = document.getElementById('scrubber');
        const timeline = document.getElementById('timeline');
        const playPause = document.getElementById('play-pause');
        const playIcon = document.getElementById('play-icon');
        const pauseIcon = document.getElementById('pause-icon');
        const timeDisplay = document.getElementById('time-display');
        const markerNav = document.getElementById('marker-nav');
        
        // Initialize
        function init() {{
            // Set stage size
            stage.style.width = presentationData.width + 'px';
            stage.style.height = presentationData.height + 'px';
            stage.style.background = presentationData.background;
            
            // Scale to fit
            scaleStage();
            window.addEventListener('resize', scaleStage);
            
            // Add markers to timeline
            presentationData.markers.forEach(marker => {{
                const el = document.createElement('div');
                el.className = 'marker';
                el.style.left = (marker.time * 100) + '%';
                el.style.background = marker.color;
                el.setAttribute('data-name', marker.name);
                el.onclick = () => seekTo(marker.time);
                timeline.appendChild(el);
                
                // Add marker button
                const btn = document.createElement('button');
                btn.className = 'marker-btn';
                btn.textContent = marker.name;
                btn.style.borderLeft = '3px solid ' + marker.color;
                btn.onclick = () => seekTo(marker.time);
                markerNav.appendChild(btn);
            }});
            
            // Initial render
            render();
        }}
        
        function scaleStage() {{
            const container = document.getElementById('presentation');
            const scaleX = container.clientWidth / presentationData.width;
            const scaleY = container.clientHeight / presentationData.height;
            const scale = Math.min(scaleX, scaleY);
            
            stage.style.transform = `scale(${{scale}})`;
            stage.style.left = (container.clientWidth - presentationData.width * scale) / 2 + 'px';
            stage.style.top = (container.clientHeight - presentationData.height * scale) / 2 + 'px';
        }}
        
        function render() {{
            // Clear stage
            stage.innerHTML = '';
            
            // Get state at current time
            const state = getState(currentTime);
            
            // Render each visible element
            state.elements.forEach(element => {{
                const el = document.createElement('div');
                el.className = 'element ' + element.type;
                el.id = element.id;
                
                const props = element.properties;
                
                // Position and transform
                el.style.left = (props.x || 0) + 'px';
                el.style.top = (props.y || 0) + 'px';
                el.style.opacity = props.opacity ?? 1;
                el.style.transform = `scale(${{props.scale || 1}}) rotate(${{props.rotate || 0}}deg)`;
                el.style.zIndex = element.layer;
                
                // Type-specific rendering
                switch (element.type) {{
                    case 'text':
                        el.textContent = element.content;
                        el.style.fontSize = (props.fontSize || 24) + 'px';
                        el.style.color = props.color || '#ffffff';
                        break;
                    case 'image':
                        const img = document.createElement('img');
                        img.src = element.content;
                        if (props.width) img.style.width = props.width + 'px';
                        if (props.height) img.style.height = props.height + 'px';
                        el.appendChild(img);
                        break;
                    case 'shape':
                        el.style.width = (props.width || 100) + 'px';
                        el.style.height = (props.height || 100) + 'px';
                        el.style.background = props.fill || '#3b82f6';
                        if (element.content === 'circle') {{
                            el.style.borderRadius = '50%';
                        }}
                        break;
                    case 'code':
                        el.innerHTML = '<pre>' + escapeHtml(element.content.code) + '</pre>';
                        break;
                    case 'html':
                        el.innerHTML = element.content;
                        break;
                }}
                
                stage.appendChild(el);
            }});
            
            // Update progress bar
            progress.style.width = (currentTime * 100) + '%';
            scrubber.style.left = (currentTime * 100) + '%';
            
            // Update time display
            const current = formatTime(currentTime * presentationData.duration);
            const total = formatTime(presentationData.duration);
            timeDisplay.textContent = current + ' / ' + total;
        }}
        
        function getState(t) {{
            const elements = [];
            
            presentationData.elements.forEach(element => {{
                if (t < element.enter || t > element.exit) return;
                
                const props = interpolateProperties(element.keyframes, t);
                elements.push({{
                    id: element.id,
                    type: element.type,
                    content: element.content,
                    properties: props,
                    layer: element.layer
                }});
            }});
            
            return {{ elements }};
        }}
        
        function interpolateProperties(keyframes, t) {{
            if (!keyframes || keyframes.length === 0) return {{}};
            
            let before = null;
            let after = null;
            
            for (const kf of keyframes) {{
                if (kf.time <= t) before = kf;
                if (kf.time >= t && !after) after = kf;
            }}
            
            if (!before) return keyframes[0].properties;
            if (!after || before === after) return before.properties;
            
            const progress = (t - before.time) / (after.time - before.time);
            const eased = applyEasing(progress, after.easing);
            
            const result = {{}};
            const allKeys = new Set([...Object.keys(before.properties), ...Object.keys(after.properties)]);
            
            allKeys.forEach(key => {{
                const start = before.properties[key] ?? 0;
                const end = after.properties[key] ?? 0;
                
                if (typeof start === 'number' && typeof end === 'number') {{
                    result[key] = start + (end - start) * eased;
                }} else if (typeof start === 'string' && start.startsWith('#')) {{
                    result[key] = interpolateColor(start, end, eased);
                }} else {{
                    result[key] = eased < 0.5 ? start : end;
                }}
            }});
            
            return result;
        }}
        
        function applyEasing(t, easing) {{
            switch (easing) {{
                case 'linear': return t;
                case 'ease-in': return t * t;
                case 'ease-out': return 1 - (1 - t) * (1 - t);
                case 'ease-in-out': return 3 * t * t - 2 * t * t * t;
                case 'bounce': return t < 0.5 ? 8 * t * t * t * t : 1 - 8 * Math.pow(1 - t, 4);
                case 'elastic': 
                    if (t === 0 || t === 1) return t;
                    return Math.sin(13 * Math.PI / 2 * t) * Math.pow(2, 10 * (t - 1));
                default: return t;
            }}
        }}
        
        function interpolateColor(start, end, t) {{
            const hexToRgb = h => {{
                h = h.replace('#', '');
                return [
                    parseInt(h.substr(0, 2), 16),
                    parseInt(h.substr(2, 2), 16),
                    parseInt(h.substr(4, 2), 16)
                ];
            }};
            
            const s = hexToRgb(start);
            const e = hexToRgb(end);
            const r = Math.round(s[0] + (e[0] - s[0]) * t);
            const g = Math.round(s[1] + (e[1] - s[1]) * t);
            const b = Math.round(s[2] + (e[2] - s[2]) * t);
            
            return '#' + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');
        }}
        
        function formatTime(seconds) {{
            const m = Math.floor(seconds / 60);
            const s = Math.floor(seconds % 60);
            return m + ':' + s.toString().padStart(2, '0');
        }}
        
        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}
        
        // Playback
        function play() {{
            isPlaying = true;
            lastFrameTime = performance.now();
            playIcon.style.display = 'none';
            pauseIcon.style.display = 'block';
            requestAnimationFrame(tick);
        }}
        
        function pause() {{
            isPlaying = false;
            playIcon.style.display = 'block';
            pauseIcon.style.display = 'none';
        }}
        
        function tick(timestamp) {{
            if (!isPlaying) return;
            
            const delta = (timestamp - lastFrameTime) / 1000;
            lastFrameTime = timestamp;
            
            currentTime += delta / presentationData.duration;
            
            if (currentTime >= 1) {{
                currentTime = 1;
                pause();
            }}
            
            render();
            
            if (isPlaying) {{
                requestAnimationFrame(tick);
            }}
        }}
        
        function seekTo(t) {{
            currentTime = Math.max(0, Math.min(1, t));
            render();
        }}
        
        // Controls
        playPause.onclick = () => isPlaying ? pause() : play();
        
        document.getElementById('prev-marker').onclick = () => {{
            const markers = presentationData.markers.filter(m => m.time < currentTime - 0.01);
            if (markers.length > 0) {{
                seekTo(markers[markers.length - 1].time);
            }} else {{
                seekTo(0);
            }}
        }};
        
        document.getElementById('next-marker').onclick = () => {{
            const marker = presentationData.markers.find(m => m.time > currentTime + 0.01);
            if (marker) seekTo(marker.time);
        }};
        
        // Timeline scrubbing
        let isDragging = false;
        
        timeline.onmousedown = (e) => {{
            isDragging = true;
            updateFromMouse(e);
        }};
        
        document.onmousemove = (e) => {{
            if (isDragging) updateFromMouse(e);
        }};
        
        document.onmouseup = () => {{
            isDragging = false;
        }};
        
        function updateFromMouse(e) {{
            const rect = timeline.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width;
            seekTo(x);
        }}
        
        // Keyboard
        document.onkeydown = (e) => {{
            switch (e.code) {{
                case 'Space':
                    e.preventDefault();
                    isPlaying ? pause() : play();
                    break;
                case 'ArrowLeft':
                    seekTo(currentTime - 0.02);
                    break;
                case 'ArrowRight':
                    seekTo(currentTime + 0.02);
                    break;
                case 'Comma':
                    document.getElementById('prev-marker').click();
                    break;
                case 'Period':
                    document.getElementById('next-marker').click();
                    break;
                case 'Home':
                    seekTo(0);
                    break;
                case 'End':
                    seekTo(1);
                    break;
            }}
        }};
        
        // Start
        init();
    </script>
</body>
</html>'''
        
        return html


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'EasingFunction',
    'ContentType',
    'Keyframe',
    'ContentElement',
    'TimelineMarker',
    'Presentation',
    'PresentationBuilder',
    'HTMLGenerator',
]
