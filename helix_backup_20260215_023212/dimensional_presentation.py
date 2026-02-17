"""
ButterflyFX Dimensional Presentation Engine

Copyright (c) 2024-2026 Kenneth Bingham. All Rights Reserved.

This is a DERIVED IMPLEMENTATION built on the open source mathematical kernel.
This file is proprietary software. See /helix/LICENSE for details.

---

NOT a linear timeline. A 7-dimensional space to navigate.

TRADITIONAL PRESENTATION:
    Slide 1 → Slide 2 → Slide 3 → ...
    Linear, flat, one path

DIMENSIONAL PRESENTATION:
    Each "slide" exists at a coordinate in helix space:
        (spiral, level, position)
    
    Navigation:
        → / ← : Move along spiral (next/prev at same depth)
        ↑ / ↓ : Drill up/down levels (overview ↔ detail)
        Tab   : Switch spirals (different topics/branches)

THE 7-LEVEL HIERARCHY (Point → Volume → Beyond):
    Level 0: POINT      - The core concept, single focus
    Level 1: LINE       - One dimension, a sequence
    Level 2: PLANE      - Two dimensions, a grid/table
    Level 3: VOLUME     - Three dimensions, spatial
    Level 4: TIME       - Fourth dimension, animation
    Level 5: PARALLEL   - Fifth dimension, alternatives
    Level 6: META       - Sixth dimension, about itself

EXAMPLE:
    A presentation about "ButterflyFX Architecture"
    
    Spiral 0 (Main):
        Level 6 (META):     "ButterflyFX Overview"
        Level 5 (PARALLEL): "vs Traditional" | "vs Competitors"
        Level 4 (TIME):     "Evolution", "Roadmap"
        Level 3 (VOLUME):   "System Diagram"
        Level 2 (PLANE):    "Module Grid"
        Level 1 (LINE):     "Data Flow"
        Level 0 (POINT):    "Core Kernel"
    
    From any point, user can:
        - Drill DOWN into more detail
        - Drill UP for broader context
        - Move SIDEWAYS for related topics
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
import json
import math


# =============================================================================
# DIMENSIONAL LEVELS
# =============================================================================

class DimensionLevel(Enum):
    """The 7 levels of dimensional hierarchy"""
    POINT = 0       # Core concept, atomic
    LINE = 1        # Sequence, one direction
    PLANE = 2       # Grid, two directions
    VOLUME = 3      # Space, three directions
    TIME = 4        # Animation, temporal
    PARALLEL = 5    # Alternatives, branches
    META = 6        # Overview, about itself


LEVEL_NAMES = {
    DimensionLevel.POINT: "Point (Core)",
    DimensionLevel.LINE: "Line (Sequence)",
    DimensionLevel.PLANE: "Plane (Grid)",
    DimensionLevel.VOLUME: "Volume (Space)",
    DimensionLevel.TIME: "Time (Animation)",
    DimensionLevel.PARALLEL: "Parallel (Alternatives)",
    DimensionLevel.META: "Meta (Overview)",
}

LEVEL_ICONS = {
    DimensionLevel.POINT: "●",
    DimensionLevel.LINE: "━",
    DimensionLevel.PLANE: "▢",
    DimensionLevel.VOLUME: "◇",
    DimensionLevel.TIME: "◷",
    DimensionLevel.PARALLEL: "⫽",
    DimensionLevel.META: "◎",
}


# =============================================================================
# DIMENSIONAL COORDINATE
# =============================================================================

@dataclass(frozen=True)
class DimensionalCoord:
    """
    A coordinate in dimensional presentation space.
    
    spiral: Which topic/branch (0, 1, 2, ...)
    level: Depth in hierarchy (0-6)
    position: Position along the spiral at this level
    """
    spiral: int = 0
    level: int = 0
    position: int = 0
    
    def up(self) -> 'DimensionalCoord':
        """Move up one level (more abstract/overview)"""
        return DimensionalCoord(self.spiral, min(6, self.level + 1), 0)
    
    def down(self) -> 'DimensionalCoord':
        """Move down one level (more detail)"""
        return DimensionalCoord(self.spiral, max(0, self.level - 1), 0)
    
    def next(self) -> 'DimensionalCoord':
        """Move to next position at same level"""
        return DimensionalCoord(self.spiral, self.level, self.position + 1)
    
    def prev(self) -> 'DimensionalCoord':
        """Move to previous position at same level"""
        return DimensionalCoord(self.spiral, self.level, max(0, self.position - 1))
    
    def to_spiral(self, spiral: int) -> 'DimensionalCoord':
        """Switch to different spiral"""
        return DimensionalCoord(spiral, self.level, 0)
    
    def to_dict(self) -> dict:
        return {"spiral": self.spiral, "level": self.level, "position": self.position}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DimensionalCoord':
        return cls(data["spiral"], data["level"], data["position"])
    
    def __str__(self) -> str:
        return f"({self.spiral}, {self.level}, {self.position})"


# =============================================================================
# DIMENSIONAL NODE - A single "slide" in the space
# =============================================================================

@dataclass
class DimensionalNode:
    """
    A node in the dimensional presentation space.
    
    Each node has:
        - A coordinate (where it exists)
        - Content (what to display)
        - Links to related nodes (navigation paths)
        - Transitions for animations
    """
    id: str
    coord: DimensionalCoord
    title: str
    content: Any                              # HTML, text, image, etc.
    content_type: str = "html"                # "html", "text", "image", "code", "chart"
    
    # Visual properties
    background: str = "#1a1a2e"
    color: str = "#ffffff"
    scale: float = 1.0
    
    # Navigation - explicit links (optional, auto-detected if not set)
    link_up: Optional[str] = None             # Node ID to go up to
    link_down: Optional[str] = None           # Node ID to drill into
    link_next: Optional[str] = None           # Node ID for next
    link_prev: Optional[str] = None           # Node ID for previous
    
    # Children at lower levels (for drill-down)
    children: List[str] = field(default_factory=list)  # Node IDs
    
    # Transition animation when entering this node
    transition: str = "zoom"                  # "zoom", "fade", "slide", "flip", "spiral"
    transition_duration: float = 0.5          # seconds
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "coord": self.coord.to_dict(),
            "title": self.title,
            "content": self.content,
            "contentType": self.content_type,
            "background": self.background,
            "color": self.color,
            "scale": self.scale,
            "linkUp": self.link_up,
            "linkDown": self.link_down,
            "linkNext": self.link_next,
            "linkPrev": self.link_prev,
            "children": self.children,
            "transition": self.transition,
            "transitionDuration": self.transition_duration,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DimensionalNode':
        return cls(
            id=data["id"],
            coord=DimensionalCoord.from_dict(data["coord"]),
            title=data["title"],
            content=data["content"],
            content_type=data.get("contentType", "html"),
            background=data.get("background", "#1a1a2e"),
            color=data.get("color", "#ffffff"),
            scale=data.get("scale", 1.0),
            link_up=data.get("linkUp"),
            link_down=data.get("linkDown"),
            link_next=data.get("linkNext"),
            link_prev=data.get("linkPrev"),
            children=data.get("children", []),
            transition=data.get("transition", "zoom"),
            transition_duration=data.get("transitionDuration", 0.5),
        )


# =============================================================================
# DIMENSIONAL PRESENTATION - The full space
# =============================================================================

@dataclass
class DimensionalPresentation:
    """
    A presentation as a navigable dimensional space.
    
    Contains nodes at various coordinates.
    Supports drilling up/down, moving along spirals, switching topics.
    """
    id: str
    title: str
    nodes: Dict[str, DimensionalNode] = field(default_factory=dict)
    spirals: List[str] = field(default_factory=list)  # Spiral names/topics
    start_node: Optional[str] = None
    
    # Visual settings
    width: int = 1920
    height: int = 1080
    
    def add_node(self, node: DimensionalNode) -> 'DimensionalPresentation':
        """Add a node to the presentation"""
        self.nodes[node.id] = node
        if self.start_node is None:
            self.start_node = node.id
        return self
    
    def get_node(self, node_id: str) -> Optional[DimensionalNode]:
        """Get a node by ID"""
        return self.nodes.get(node_id)
    
    def get_node_at(self, coord: DimensionalCoord) -> Optional[DimensionalNode]:
        """Get node at a specific coordinate"""
        for node in self.nodes.values():
            if node.coord == coord:
                return node
        return None
    
    def find_navigation(self, from_node: DimensionalNode, direction: str) -> Optional[str]:
        """
        Find the node to navigate to from a given node.
        
        Directions: "up", "down", "next", "prev", "spiral-N"
        """
        # Check explicit links first
        if direction == "up" and from_node.link_up:
            return from_node.link_up
        if direction == "down" and from_node.link_down:
            return from_node.link_down
        if direction == "next" and from_node.link_next:
            return from_node.link_next
        if direction == "prev" and from_node.link_prev:
            return from_node.link_prev
        
        # If drilling down, check children
        if direction == "down" and from_node.children:
            return from_node.children[0]
        
        # Auto-detect based on coordinates
        if direction == "up":
            target = from_node.coord.up()
        elif direction == "down":
            target = from_node.coord.down()
        elif direction == "next":
            target = from_node.coord.next()
        elif direction == "prev":
            target = from_node.coord.prev()
        elif direction.startswith("spiral-"):
            spiral = int(direction.split("-")[1])
            target = from_node.coord.to_spiral(spiral)
        else:
            return None
        
        # Find node at target coordinate
        node = self.get_node_at(target)
        return node.id if node else None
    
    def get_structure(self) -> Dict[int, Dict[int, List[str]]]:
        """
        Get the structure of the presentation.
        Returns: {spiral: {level: [node_ids]}}
        """
        structure: Dict[int, Dict[int, List[str]]] = {}
        
        for node in self.nodes.values():
            s, l = node.coord.spiral, node.coord.level
            if s not in structure:
                structure[s] = {}
            if l not in structure[s]:
                structure[s][l] = []
            structure[s][l].append(node.id)
        
        return structure
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "spirals": self.spirals,
            "startNode": self.start_node,
            "width": self.width,
            "height": self.height,
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DimensionalPresentation':
        pres = cls(
            id=data["id"],
            title=data["title"],
            spirals=data.get("spirals", []),
            start_node=data.get("startNode"),
            width=data.get("width", 1920),
            height=data.get("height", 1080),
        )
        for node_data in data.get("nodes", {}).values():
            pres.add_node(DimensionalNode.from_dict(node_data))
        return pres


# =============================================================================
# DIMENSIONAL BUILDER - Fluent API
# =============================================================================

class DimensionalBuilder:
    """
    Fluent builder for creating dimensional presentations.
    
    Usage:
        pres = (DimensionalBuilder("my-pres", "My Presentation")
            .spirals(["Main", "Appendix"])
            
            # META level - overview
            .at(0, 6, 0)
            .node("overview", "Overview", '''
                <h1>Welcome</h1>
                <p>This is the big picture</p>
            ''')
                .children("detail-1", "detail-2")
            
            # POINT level - core details
            .at(0, 0, 0)
            .node("detail-1", "Core Concept", "The fundamental idea")
            
            .at(0, 0, 1)
            .node("detail-2", "Second Detail", "More information")
            
            .build())
    """
    
    def __init__(self, id: str, title: str):
        self._pres = DimensionalPresentation(id=id, title=title)
        self._current_coord = DimensionalCoord(0, 6, 0)  # Start at META
        self._current_node: Optional[DimensionalNode] = None
    
    def spirals(self, names: List[str]) -> 'DimensionalBuilder':
        """Define spiral names/topics"""
        self._pres.spirals = names
        return self
    
    def size(self, width: int, height: int) -> 'DimensionalBuilder':
        """Set presentation dimensions"""
        self._pres.width = width
        self._pres.height = height
        return self
    
    def at(self, spiral: int, level: int, position: int = 0) -> 'DimensionalBuilder':
        """Set the current coordinate for the next node"""
        self._current_coord = DimensionalCoord(spiral, level, position)
        return self
    
    def node(
        self,
        id: str,
        title: str,
        content: str,
        content_type: str = "html",
        background: str = "#1a1a2e",
        color: str = "#ffffff",
        transition: str = "zoom"
    ) -> 'DimensionalBuilder':
        """Create a node at the current coordinate"""
        self._current_node = DimensionalNode(
            id=id,
            coord=self._current_coord,
            title=title,
            content=content,
            content_type=content_type,
            background=background,
            color=color,
            transition=transition,
        )
        self._pres.add_node(self._current_node)
        return self
    
    def children(self, *node_ids: str) -> 'DimensionalBuilder':
        """Set children for the current node (drill-down targets)"""
        if self._current_node:
            self._current_node.children = list(node_ids)
        return self
    
    def link_up(self, node_id: str) -> 'DimensionalBuilder':
        """Set explicit up link"""
        if self._current_node:
            self._current_node.link_up = node_id
        return self
    
    def link_down(self, node_id: str) -> 'DimensionalBuilder':
        """Set explicit down link"""
        if self._current_node:
            self._current_node.link_down = node_id
        return self
    
    def link_next(self, node_id: str) -> 'DimensionalBuilder':
        """Set explicit next link"""
        if self._current_node:
            self._current_node.link_next = node_id
        return self
    
    def link_prev(self, node_id: str) -> 'DimensionalBuilder':
        """Set explicit prev link"""
        if self._current_node:
            self._current_node.link_prev = node_id
        return self
    
    def transition(self, style: str, duration: float = 0.5) -> 'DimensionalBuilder':
        """Set transition for current node"""
        if self._current_node:
            self._current_node.transition = style
            self._current_node.transition_duration = duration
        return self
    
    def start_at(self, node_id: str) -> 'DimensionalBuilder':
        """Set the starting node"""
        self._pres.start_node = node_id
        return self
    
    def build(self) -> DimensionalPresentation:
        """Build and return the presentation"""
        return self._pres


# =============================================================================
# HTML GENERATOR - Generate navigable HTML
# =============================================================================

class DimensionalHTMLGenerator:
    """
    Generate a standalone HTML file for dimensional navigation.
    
    Controls:
        ↑ / W : Drill UP (overview)
        ↓ / S : Drill DOWN (detail)
        ← / A : Previous at same level
        → / D : Next at same level
        1-9   : Jump to spiral
        Home  : Go to start
        
    Visual:
        - 3D helix visualization showing current position
        - Mini-map of structure
        - Breadcrumb showing level hierarchy
    """
    
    @staticmethod
    def generate(pres: DimensionalPresentation) -> str:
        data_json = pres.to_json()
        
        # Generate level colors
        level_colors = [
            "#ef4444",  # 0: Point - red
            "#f97316",  # 1: Line - orange
            "#eab308",  # 2: Plane - yellow
            "#22c55e",  # 3: Volume - green
            "#06b6d4",  # 4: Time - cyan
            "#3b82f6",  # 5: Parallel - blue
            "#8b5cf6",  # 6: Meta - purple
        ]
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{pres.title}</title>
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
        
        /* Main content area */
        #content {{
            position: absolute;
            top: 60px;
            left: 0;
            right: 280px;
            bottom: 60px;
            overflow: hidden;
            perspective: 1000px;
        }}
        
        #stage {{
            position: absolute;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1),
                        opacity 0.3s ease;
        }}
        
        .node-content {{
            max-width: 80%;
            max-height: 80%;
            padding: 60px;
            border-radius: 20px;
            overflow: auto;
        }}
        
        .node-content h1 {{
            font-size: 3em;
            margin-bottom: 0.5em;
            font-weight: 700;
        }}
        
        .node-content h2 {{
            font-size: 2em;
            margin: 1em 0 0.5em;
            font-weight: 600;
        }}
        
        .node-content p {{
            font-size: 1.5em;
            line-height: 1.6;
            margin-bottom: 1em;
        }}
        
        .node-content ul, .node-content ol {{
            font-size: 1.3em;
            margin-left: 2em;
            margin-bottom: 1em;
        }}
        
        .node-content li {{
            margin-bottom: 0.5em;
        }}
        
        .node-content code {{
            background: rgba(0,0,0,0.3);
            padding: 0.2em 0.5em;
            border-radius: 4px;
            font-family: 'Fira Code', monospace;
        }}
        
        .node-content pre {{
            background: rgba(0,0,0,0.4);
            padding: 1.5em;
            border-radius: 10px;
            overflow-x: auto;
            margin: 1em 0;
        }}
        
        /* Header */
        #header {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: linear-gradient(180deg, rgba(0,0,0,0.9), transparent);
            display: flex;
            align-items: center;
            padding: 0 20px;
            z-index: 100;
        }}
        
        #breadcrumb {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 14px;
        }}
        
        .breadcrumb-item {{
            display: flex;
            align-items: center;
            gap: 5px;
            padding: 5px 12px;
            border-radius: 20px;
            cursor: pointer;
            transition: background 0.2s;
        }}
        
        .breadcrumb-item:hover {{
            background: rgba(255,255,255,0.1);
        }}
        
        .breadcrumb-item.current {{
            background: rgba(255,255,255,0.2);
        }}
        
        .level-indicator {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}
        
        #title {{
            margin-left: auto;
            font-size: 18px;
            color: #888;
        }}
        
        /* Sidebar - Structure map */
        #sidebar {{
            position: fixed;
            top: 60px;
            right: 0;
            width: 280px;
            bottom: 60px;
            background: rgba(20, 20, 30, 0.95);
            border-left: 1px solid #333;
            overflow-y: auto;
            padding: 15px;
        }}
        
        #sidebar h3 {{
            font-size: 12px;
            text-transform: uppercase;
            color: #666;
            margin-bottom: 15px;
            letter-spacing: 1px;
        }}
        
        .structure-level {{
            margin-bottom: 20px;
        }}
        
        .level-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
            font-size: 12px;
            color: #888;
        }}
        
        .level-line {{
            flex: 1;
            height: 1px;
            background: currentColor;
            opacity: 0.3;
        }}
        
        .level-nodes {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            padding-left: 20px;
        }}
        
        .structure-node {{
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            background: rgba(255,255,255,0.05);
            border: 1px solid transparent;
            transition: all 0.2s;
        }}
        
        .structure-node:hover {{
            background: rgba(255,255,255,0.1);
        }}
        
        .structure-node.current {{
            border-color: currentColor;
            background: rgba(255,255,255,0.15);
        }}
        
        /* Footer - Controls */
        #footer {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: linear-gradient(0deg, rgba(0,0,0,0.9), transparent);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 30px;
            z-index: 100;
        }}
        
        .nav-btn {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            padding: 8px 16px;
            background: rgba(255,255,255,0.1);
            border: none;
            border-radius: 10px;
            color: white;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .nav-btn:hover {{
            background: rgba(255,255,255,0.2);
            transform: translateY(-2px);
        }}
        
        .nav-btn:disabled {{
            opacity: 0.3;
            cursor: not-allowed;
            transform: none;
        }}
        
        .nav-btn svg {{
            width: 24px;
            height: 24px;
        }}
        
        .nav-btn span {{
            font-size: 10px;
            color: #888;
        }}
        
        /* Coordinate display */
        #coord-display {{
            position: fixed;
            bottom: 70px;
            left: 20px;
            font-family: 'Fira Code', monospace;
            font-size: 14px;
            color: #666;
            background: rgba(0,0,0,0.5);
            padding: 8px 15px;
            border-radius: 8px;
        }}
        
        /* Level colors */
        .level-0 {{ color: {level_colors[0]}; }}
        .level-1 {{ color: {level_colors[1]}; }}
        .level-2 {{ color: {level_colors[2]}; }}
        .level-3 {{ color: {level_colors[3]}; }}
        .level-4 {{ color: {level_colors[4]}; }}
        .level-5 {{ color: {level_colors[5]}; }}
        .level-6 {{ color: {level_colors[6]}; }}
        
        .bg-level-0 {{ background: {level_colors[0]}; }}
        .bg-level-1 {{ background: {level_colors[1]}; }}
        .bg-level-2 {{ background: {level_colors[2]}; }}
        .bg-level-3 {{ background: {level_colors[3]}; }}
        .bg-level-4 {{ background: {level_colors[4]}; }}
        .bg-level-5 {{ background: {level_colors[5]}; }}
        .bg-level-6 {{ background: {level_colors[6]}; }}
        
        /* Transitions */
        .transition-zoom {{
            animation: zoomIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .transition-fade {{
            animation: fadeIn 0.5s ease;
        }}
        
        .transition-slide {{
            animation: slideIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .transition-spiral {{
            animation: spiralIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .transition-drill-down {{
            animation: drillDown 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .transition-drill-up {{
            animation: drillUp 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        @keyframes zoomIn {{
            from {{ transform: scale(0.8); opacity: 0; }}
            to {{ transform: scale(1); opacity: 1; }}
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        @keyframes slideIn {{
            from {{ transform: translateX(100px); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        
        @keyframes spiralIn {{
            from {{ transform: rotate(-180deg) scale(0); opacity: 0; }}
            to {{ transform: rotate(0deg) scale(1); opacity: 1; }}
        }}
        
        @keyframes drillDown {{
            from {{ transform: scale(2) translateY(-50px); opacity: 0; }}
            to {{ transform: scale(1) translateY(0); opacity: 1; }}
        }}
        
        @keyframes drillUp {{
            from {{ transform: scale(0.5) translateY(50px); opacity: 0; }}
            to {{ transform: scale(1) translateY(0); opacity: 1; }}
        }}
        
        /* Keyboard hints */
        .hint {{
            position: fixed;
            bottom: 70px;
            right: 300px;
            font-size: 12px;
            color: #555;
        }}
        
        .hint kbd {{
            background: #333;
            padding: 2px 8px;
            border-radius: 4px;
            margin: 0 3px;
        }}
    </style>
</head>
<body>
    <div id="header">
        <div id="breadcrumb"></div>
        <div id="title">{pres.title}</div>
    </div>
    
    <div id="content">
        <div id="stage"></div>
    </div>
    
    <div id="sidebar">
        <h3>Structure</h3>
        <div id="structure"></div>
    </div>
    
    <div id="footer">
        <button class="nav-btn" id="btn-up" title="Drill Up (↑ or W)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 19V5M5 12l7-7 7 7"/>
            </svg>
            <span>UP</span>
        </button>
        <button class="nav-btn" id="btn-prev" title="Previous (← or A)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            <span>PREV</span>
        </button>
        <button class="nav-btn" id="btn-next" title="Next (→ or D)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
            <span>NEXT</span>
        </button>
        <button class="nav-btn" id="btn-down" title="Drill Down (↓ or S)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 5v14M5 12l7 7 7-7"/>
            </svg>
            <span>DOWN</span>
        </button>
    </div>
    
    <div id="coord-display"></div>
    
    <div class="hint">
        <kbd>↑↓←→</kbd> Navigate
        <kbd>1-9</kbd> Spirals
        <kbd>Home</kbd> Start
    </div>

    <script>
        // Presentation data
        const pres = {data_json};
        
        const levelNames = ['Point', 'Line', 'Plane', 'Volume', 'Time', 'Parallel', 'Meta'];
        const levelIcons = ['●', '━', '▢', '◇', '◷', '⫽', '◎'];
        const levelColors = {json.dumps(level_colors)};
        
        // State
        let currentNodeId = pres.startNode;
        let navigationHistory = [];
        
        // Elements
        const stage = document.getElementById('stage');
        const breadcrumb = document.getElementById('breadcrumb');
        const structure = document.getElementById('structure');
        const coordDisplay = document.getElementById('coord-display');
        
        const btnUp = document.getElementById('btn-up');
        const btnDown = document.getElementById('btn-down');
        const btnPrev = document.getElementById('btn-prev');
        const btnNext = document.getElementById('btn-next');
        
        // Initialize
        function init() {{
            renderStructure();
            if (currentNodeId) {{
                navigateTo(currentNodeId, 'zoom');
            }}
        }}
        
        function renderStructure() {{
            // Group nodes by level
            const byLevel = {{}};
            Object.values(pres.nodes).forEach(node => {{
                const level = node.coord.level;
                if (!byLevel[level]) byLevel[level] = [];
                byLevel[level].push(node);
            }});
            
            // Render from top (6) to bottom (0)
            let html = '';
            for (let level = 6; level >= 0; level--) {{
                const nodes = byLevel[level] || [];
                if (nodes.length === 0) continue;
                
                html += `
                    <div class="structure-level">
                        <div class="level-header level-${{level}}">
                            <span>${{levelIcons[level]}} ${{levelNames[level]}}</span>
                            <div class="level-line"></div>
                        </div>
                        <div class="level-nodes">
                            ${{nodes.map(n => `
                                <div class="structure-node level-${{level}}" 
                                     data-node="${{n.id}}"
                                     onclick="navigateTo('${{n.id}}', 'zoom')">
                                    ${{n.title}}
                                </div>
                            `).join('')}}
                        </div>
                    </div>
                `;
            }}
            
            structure.innerHTML = html;
        }}
        
        function renderNode(node, transition) {{
            const content = document.createElement('div');
            content.className = `node-content transition-${{transition}}`;
            content.style.background = node.background;
            content.style.color = node.color;
            
            // Add content based on type
            if (node.contentType === 'html') {{
                content.innerHTML = `<h1>${{node.title}}</h1>${{node.content}}`;
            }} else if (node.contentType === 'text') {{
                content.innerHTML = `<h1>${{node.title}}</h1><p>${{node.content}}</p>`;
            }} else if (node.contentType === 'code') {{
                content.innerHTML = `<h1>${{node.title}}</h1><pre><code>${{escapeHtml(node.content)}}</code></pre>`;
            }} else {{
                content.innerHTML = `<h1>${{node.title}}</h1>${{node.content}}`;
            }}
            
            stage.innerHTML = '';
            stage.appendChild(content);
            
            // Update breadcrumb
            renderBreadcrumb(node);
            
            // Update structure highlighting
            document.querySelectorAll('.structure-node').forEach(el => {{
                el.classList.toggle('current', el.dataset.node === node.id);
            }});
            
            // Update coordinate display
            const c = node.coord;
            coordDisplay.innerHTML = `
                <span class="level-${{c.level}}">${{levelIcons[c.level]}}</span>
                Spiral ${{c.spiral}} · Level ${{c.level}} · Position ${{c.position}}
            `;
            
            // Update button states
            updateNavButtons(node);
        }}
        
        function renderBreadcrumb(node) {{
            // Build path from META to current
            const path = [];
            let level = node.coord.level;
            
            // Add current node
            path.unshift({{ node, isCurrent: true }});
            
            // Add parent levels
            for (let l = level + 1; l <= 6; l++) {{
                const parent = Object.values(pres.nodes).find(
                    n => n.coord.spiral === node.coord.spiral && n.coord.level === l
                );
                if (parent) {{
                    path.unshift({{ node: parent, isCurrent: false }});
                }}
            }}
            
            breadcrumb.innerHTML = path.map(item => `
                <div class="breadcrumb-item ${{item.isCurrent ? 'current' : ''}}"
                     onclick="navigateTo('${{item.node.id}}', '${{item.isCurrent ? 'zoom' : 'drill-up'}}')">
                    <div class="level-indicator bg-level-${{item.node.coord.level}}"></div>
                    <span>${{item.node.title}}</span>
                </div>
                ${{!item.isCurrent ? '<span style="color:#555">›</span>' : ''}}
            `).join('');
        }}
        
        function updateNavButtons(node) {{
            btnUp.disabled = !findNavigationTarget(node, 'up');
            btnDown.disabled = !findNavigationTarget(node, 'down');
            btnPrev.disabled = !findNavigationTarget(node, 'prev');
            btnNext.disabled = !findNavigationTarget(node, 'next');
        }}
        
        function findNavigationTarget(node, direction) {{
            // Check explicit links
            if (direction === 'up' && node.linkUp) return node.linkUp;
            if (direction === 'down' && node.linkDown) return node.linkDown;
            if (direction === 'next' && node.linkNext) return node.linkNext;
            if (direction === 'prev' && node.linkPrev) return node.linkPrev;
            
            // Check children for drill-down
            if (direction === 'down' && node.children && node.children.length > 0) {{
                return node.children[0];
            }}
            
            // Calculate target coordinate
            const c = node.coord;
            let target;
            
            switch (direction) {{
                case 'up':
                    target = {{ spiral: c.spiral, level: Math.min(6, c.level + 1), position: 0 }};
                    break;
                case 'down':
                    target = {{ spiral: c.spiral, level: Math.max(0, c.level - 1), position: 0 }};
                    break;
                case 'next':
                    target = {{ spiral: c.spiral, level: c.level, position: c.position + 1 }};
                    break;
                case 'prev':
                    target = {{ spiral: c.spiral, level: c.level, position: Math.max(0, c.position - 1) }};
                    break;
                default:
                    return null;
            }}
            
            // Find node at target coordinate
            const found = Object.values(pres.nodes).find(
                n => n.coord.spiral === target.spiral && 
                     n.coord.level === target.level && 
                     n.coord.position === target.position
            );
            
            return found ? found.id : null;
        }}
        
        function navigateTo(nodeId, transition = 'zoom') {{
            const node = pres.nodes[nodeId];
            if (!node) return;
            
            // Remember history for back navigation
            if (currentNodeId && currentNodeId !== nodeId) {{
                navigationHistory.push(currentNodeId);
            }}
            
            currentNodeId = nodeId;
            renderNode(node, transition);
        }}
        
        function navigate(direction) {{
            const node = pres.nodes[currentNodeId];
            if (!node) return;
            
            const targetId = findNavigationTarget(node, direction);
            if (!targetId) return;
            
            // Choose transition based on direction
            let transition = 'zoom';
            if (direction === 'up') transition = 'drill-up';
            else if (direction === 'down') transition = 'drill-down';
            else if (direction === 'next') transition = 'slide';
            else if (direction === 'prev') transition = 'slide';
            
            navigateTo(targetId, transition);
        }}
        
        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}
        
        // Event handlers
        btnUp.onclick = () => navigate('up');
        btnDown.onclick = () => navigate('down');
        btnPrev.onclick = () => navigate('prev');
        btnNext.onclick = () => navigate('next');
        
        document.onkeydown = (e) => {{
            switch (e.key) {{
                case 'ArrowUp':
                case 'w':
                case 'W':
                    e.preventDefault();
                    navigate('up');
                    break;
                case 'ArrowDown':
                case 's':
                case 'S':
                    e.preventDefault();
                    navigate('down');
                    break;
                case 'ArrowLeft':
                case 'a':
                case 'A':
                    e.preventDefault();
                    navigate('prev');
                    break;
                case 'ArrowRight':
                case 'd':
                case 'D':
                    e.preventDefault();
                    navigate('next');
                    break;
                case 'Home':
                    e.preventDefault();
                    if (pres.startNode) navigateTo(pres.startNode, 'zoom');
                    break;
                case 'Backspace':
                    e.preventDefault();
                    if (navigationHistory.length > 0) {{
                        const prev = navigationHistory.pop();
                        navigateTo(prev, 'fade');
                    }}
                    break;
            }}
            
            // Number keys for spirals
            if (e.key >= '1' && e.key <= '9') {{
                const spiral = parseInt(e.key) - 1;
                const node = Object.values(pres.nodes).find(
                    n => n.coord.spiral === spiral && n.coord.level === 6
                );
                if (node) navigateTo(node.id, 'spiral');
            }}
        }};
        
        // Touch support for mobile
        let touchStartX = 0;
        let touchStartY = 0;
        
        document.addEventListener('touchstart', (e) => {{
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        }});
        
        document.addEventListener('touchend', (e) => {{
            const dx = e.changedTouches[0].clientX - touchStartX;
            const dy = e.changedTouches[0].clientY - touchStartY;
            
            const threshold = 50;
            
            if (Math.abs(dx) > Math.abs(dy)) {{
                if (dx > threshold) navigate('prev');
                else if (dx < -threshold) navigate('next');
            }} else {{
                if (dy > threshold) navigate('up');
                else if (dy < -threshold) navigate('down');
            }}
        }});
        
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
    'DimensionLevel',
    'LEVEL_NAMES',
    'LEVEL_ICONS',
    'DimensionalCoord',
    'DimensionalNode',
    'DimensionalPresentation',
    'DimensionalBuilder',
    'DimensionalHTMLGenerator',
]
