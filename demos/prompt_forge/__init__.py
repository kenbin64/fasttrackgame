"""
Prompt Forge - AI prompts as a navigable manifold

Navigate to prompts instead of searching for them.
Position on the 3D surface IS the prompt.
"""

from .prompt_manifold import (
    Purpose,
    Style,
    Length,
    ManifoldPosition,
    PromptTemplate,
    PromptManifold
)

__all__ = [
    'Purpose',
    'Style', 
    'Length',
    'ManifoldPosition',
    'PromptTemplate',
    'PromptManifold'
]
