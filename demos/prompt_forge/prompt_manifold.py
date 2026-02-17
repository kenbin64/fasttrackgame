"""
Prompt Forge - AI Prompts as a Navigable Manifold

Instead of searching through thousands of prompts:
  ❌ Traditional: filter by tag → scroll → find → copy
  ✅ Dimensional: navigate to position → prompt EXISTS at that coordinate

The Prompt Manifold:
  X-axis: PURPOSE (creative → technical → analytical)
  Y-axis: STYLE (casual → professional → academic)
  Z-axis: LENGTH (short → medium → detailed)

Any position on this 3D surface IS a prompt. No database. No search.
The geometry CONTAINS the prompts.

This is the manifold-data paradigm in action:
  - We don't STORE prompts, we INVOKE them from geometric position
  - Position determines purpose, style, length simultaneously
  - Navigation replaces pagination
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Tuple, Optional
from enum import IntEnum
import math
import hashlib
import json


class Purpose(IntEnum):
    """X-axis: What is the prompt FOR?"""
    CREATIVE = 0      # Poetry, stories, art
    BRAINSTORM = 1    # Ideas, possibilities
    CONVERSATIONAL = 2 # Chat, dialogue
    INSTRUCTIONAL = 3 # How-to, guides
    TECHNICAL = 4     # Code, systems
    ANALYTICAL = 5    # Research, data
    
    @property
    def keywords(self) -> List[str]:
        return {
            0: ["imagine", "create", "write", "compose", "design"],
            1: ["brainstorm", "generate ideas", "explore", "what if"],
            2: ["discuss", "explain", "describe", "tell me about"],
            3: ["how to", "steps to", "guide me", "teach me"],
            4: ["implement", "code", "build", "debug", "optimize"],
            5: ["analyze", "compare", "evaluate", "research", "assess"],
        }[self.value]


class Style(IntEnum):
    """Y-axis: What TONE should the output have?"""
    CASUAL = 0       # Friendly, informal
    NEUTRAL = 1      # Balanced, general
    PROFESSIONAL = 2 # Business, formal
    ACADEMIC = 3     # Scholarly, precise
    EXPERT = 4       # Deep technical
    
    @property
    def modifiers(self) -> List[str]:
        return {
            0: ["casually", "in simple terms", "like explaining to a friend"],
            1: ["clearly", "straightforwardly", "in general terms"],
            2: ["professionally", "formally", "in business context"],
            3: ["academically", "with citations", "using formal language"],
            4: ["with expert depth", "using technical terminology", "comprehensively"],
        }[self.value]


class Length(IntEnum):
    """Z-axis: How DETAILED should the output be?"""
    BRIEF = 0       # One sentence
    SHORT = 1       # One paragraph
    MEDIUM = 2      # Several paragraphs
    DETAILED = 3    # Comprehensive
    EXHAUSTIVE = 4  # Complete deep-dive
    
    @property
    def constraints(self) -> str:
        return {
            0: "in one sentence",
            1: "in a brief paragraph",
            2: "in several paragraphs",
            3: "comprehensively with examples",
            4: "exhaustively covering all aspects",
        }[self.value]


@dataclass
class ManifoldPosition:
    """A position on the 3D prompt manifold"""
    purpose: float  # 0.0 to 5.0 (creative to analytical)
    style: float    # 0.0 to 4.0 (casual to expert)  
    length: float   # 0.0 to 4.0 (brief to exhaustive)
    
    def discretize(self) -> Tuple[Purpose, Style, Length]:
        """Snap to nearest discrete values"""
        return (
            Purpose(min(5, max(0, round(self.purpose)))),
            Style(min(4, max(0, round(self.style)))),
            Length(min(4, max(0, round(self.length))))
        )
    
    def distance_to(self, other: 'ManifoldPosition') -> float:
        """Euclidean distance in manifold space"""
        return math.sqrt(
            (self.purpose - other.purpose) ** 2 +
            (self.style - other.style) ** 2 +
            (self.length - other.length) ** 2
        )
    
    @property
    def address(self) -> str:
        """Dimensional address"""
        p, s, l = self.discretize()
        return f"prompt.{p.name.lower()}.{s.name.lower()}.{l.name.lower()}"
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "purpose": self.purpose,
            "style": self.style,
            "length": self.length
        }


@dataclass
class PromptTemplate:
    """A prompt that EXISTS at a manifold position"""
    position: ManifoldPosition
    topic: str  # What the prompt is about
    
    # Generated elements (invoked from position)
    _cached_prompt: Optional[str] = field(default=None, repr=False)
    
    def invoke(self) -> str:
        """
        INVOKE the prompt from its geometric position.
        
        This is the key insight: we don't RETRIEVE a stored prompt,
        we GENERATE it from the position's properties.
        The geometry CONTAINS the prompt.
        """
        if self._cached_prompt:
            return self._cached_prompt
            
        purpose, style, length = self.position.discretize()
        
        # Build prompt from position
        action = purpose.keywords[0]
        modifier = style.modifiers[0]
        constraint = length.constraints
        
        # The prompt IS the position
        prompt = self._generate_prompt(action, modifier, constraint)
        self._cached_prompt = prompt
        return prompt
    
    def _generate_prompt(self, action: str, modifier: str, constraint: str) -> str:
        """Generate prompt string from positional parameters"""
        purpose, style, length = self.position.discretize()
        
        templates = {
            Purpose.CREATIVE: f"Please {action} a {self.topic} {modifier}, {constraint}.",
            Purpose.BRAINSTORM: f"Please {action} for {self.topic} {modifier}, {constraint}.",
            Purpose.CONVERSATIONAL: f"Please {action} {self.topic} {modifier}, {constraint}.",
            Purpose.INSTRUCTIONAL: f"Please explain {action} {self.topic} {modifier}, {constraint}.",
            Purpose.TECHNICAL: f"Please {action} {self.topic} {modifier}, {constraint}.",
            Purpose.ANALYTICAL: f"Please {action} {self.topic} {modifier}, {constraint}.",
        }
        
        return templates[purpose]
    
    @property
    def address(self) -> str:
        return f"{self.position.address}.{self.topic_slug}"
    
    @property
    def topic_slug(self) -> str:
        return self.topic.lower().replace(" ", "_")[:20]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": self.position.to_dict(),
            "topic": self.topic,
            "prompt": self.invoke(),
            "address": self.address
        }


class PromptManifold:
    """
    The 3D surface containing ALL possible prompts.
    
    Instead of storing prompts in a database:
    - Every point on the manifold IS a prompt
    - Navigation replaces searching
    - Position determines prompt properties
    - O(1) access to any prompt type
    """
    
    # Semantic regions on the manifold
    REGIONS = {
        "coding_help": ManifoldPosition(4.5, 2.5, 2.5),  # Technical, professional, medium
        "creative_writing": ManifoldPosition(0.5, 1.0, 3.0),  # Creative, neutral, detailed
        "research": ManifoldPosition(5.0, 3.5, 4.0),  # Analytical, academic, exhaustive
        "quick_answer": ManifoldPosition(2.5, 0.5, 0.0),  # Conversational, casual, brief
        "business_email": ManifoldPosition(3.0, 2.0, 1.5),  # Instructional, professional, short
        "brainstorm": ManifoldPosition(1.0, 0.5, 2.0),  # Brainstorm, casual, medium
        "tutorial": ManifoldPosition(3.5, 1.5, 3.5),  # Instructional, neutral, detailed
        "code_review": ManifoldPosition(4.0, 4.0, 3.0),  # Technical, expert, detailed
    }
    
    def __init__(self):
        self.favorites: Dict[str, PromptTemplate] = {}
        self.recent_positions: List[ManifoldPosition] = []
    
    def navigate(self, position: ManifoldPosition, topic: str) -> PromptTemplate:
        """
        Navigate to a position on the manifold.
        The prompt at that position is INVOKED (not retrieved).
        """
        prompt = PromptTemplate(position, topic)
        
        # Track navigation
        self.recent_positions.append(position)
        if len(self.recent_positions) > 50:
            self.recent_positions.pop(0)
        
        return prompt
    
    def goto_region(self, region_name: str, topic: str) -> PromptTemplate:
        """Jump to a named region on the manifold"""
        if region_name not in self.REGIONS:
            raise ValueError(f"Unknown region: {region_name}")
        return self.navigate(self.REGIONS[region_name], topic)
    
    def nearby(self, position: ManifoldPosition, radius: float = 1.0) -> List[str]:
        """Find named regions near a position"""
        nearby_regions = []
        for name, region_pos in self.REGIONS.items():
            if position.distance_to(region_pos) <= radius:
                nearby_regions.append(name)
        return nearby_regions
    
    def interpolate(self, start: ManifoldPosition, end: ManifoldPosition, 
                    t: float, topic: str) -> PromptTemplate:
        """
        Smoothly interpolate between two positions.
        Creates prompts that blend properties.
        """
        position = ManifoldPosition(
            purpose=start.purpose + t * (end.purpose - start.purpose),
            style=start.style + t * (end.style - start.style),
            length=start.length + t * (end.length - start.length)
        )
        return self.navigate(position, topic)
    
    def save_favorite(self, name: str, prompt: PromptTemplate):
        """Bookmark a position on the manifold"""
        self.favorites[name] = prompt
    
    def list_regions(self) -> Dict[str, Dict[str, Any]]:
        """List all named regions with their positions"""
        return {
            name: {
                "position": pos.to_dict(),
                "address": pos.address,
                "discrete": {
                    "purpose": pos.discretize()[0].name,
                    "style": pos.discretize()[1].name,
                    "length": pos.discretize()[2].name
                }
            }
            for name, pos in self.REGIONS.items()
        }
    
    def to_state(self) -> Dict[str, Any]:
        """Export manifold state"""
        return {
            "regions": self.list_regions(),
            "favorites": {k: v.to_dict() for k, v in self.favorites.items()},
            "recent_count": len(self.recent_positions)
        }


# === CLI Demo ===

def demo():
    """Demonstrate the Prompt Forge manifold"""
    print("=" * 60)
    print("PROMPT FORGE - Prompts as Manifold Navigation")
    print("=" * 60)
    
    manifold = PromptManifold()
    
    # Navigate to different regions
    print("\n📍 NAVIGATING TO NAMED REGIONS:\n")
    
    regions = ["coding_help", "creative_writing", "quick_answer", "research"]
    topic = "machine learning"
    
    for region in regions:
        prompt = manifold.goto_region(region, topic)
        p, s, l = prompt.position.discretize()
        print(f"🔹 {region.upper()}")
        print(f"   Position: purpose={p.name}, style={s.name}, length={l.name}")
        print(f"   Address: {prompt.address}")
        print(f"   Prompt: {prompt.invoke()}")
        print()
    
    # Custom navigation
    print("📍 CUSTOM POSITION NAVIGATION:\n")
    
    custom_pos = ManifoldPosition(purpose=2.7, style=0.3, length=1.8)
    prompt = manifold.navigate(custom_pos, "API design")
    print(f"   Raw position: {custom_pos.to_dict()}")
    print(f"   Address: {prompt.address}")
    print(f"   Prompt: {prompt.invoke()}")
    print()
    
    # Interpolation
    print("📍 INTERPOLATION (blend two regions):\n")
    
    start = manifold.REGIONS["creative_writing"]
    end = manifold.REGIONS["coding_help"]
    
    for t in [0.0, 0.33, 0.66, 1.0]:
        prompt = manifold.interpolate(start, end, t, "documentation")
        p, s, l = prompt.position.discretize()
        print(f"   t={t:.2f}: {p.name} / {s.name} / {l.name}")
    
    print()
    print("=" * 60)
    print("KEY INSIGHT: Prompts weren't stored anywhere.")
    print("They were INVOKED from geometric positions.")
    print("Position IS the prompt. Navigation replaces search.")
    print("=" * 60)


if __name__ == "__main__":
    demo()
