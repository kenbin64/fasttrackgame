"""
Pretty Printing Utilities - Human-Readable Display

Makes ButterflyFx objects comprehensible:

Instead of:
    <Substrate object at 0x...>

Use:
    print(pretty_substrate(substrate))
    
    Output:
    ╔═══════════════════════════════════════╗
    ║ SUBSTRATE                             ║
    ╠═══════════════════════════════════════╣
    ║ Identity: 42                          ║
    ║ Expression: λ() → 100                 ║
    ║ Invocation: 100                       ║
    ╚═══════════════════════════════════════╝

CHARTER COMPLIANCE:
✅ Principle 2: Passive until invoked (display doesn't modify)
✅ Principle 5: Pure functions only
✅ Principle 6: All relationships visible
"""

from __future__ import annotations
from typing import List, Optional
from kernel import Substrate, Dimension, Observation, Observer
from .query import DIMENSION_LEVEL_TO_NAME


def pretty_substrate(substrate: Substrate, invoke: bool = True) -> str:
    """
    Pretty print a substrate.
    
    Args:
        substrate: The substrate to display
        invoke: Whether to invoke the expression (default: True)
    
    Returns:
        Human-readable string representation
    
    Example:
        print(pretty_substrate(substrate))
    """
    lines = []
    lines.append("╔═══════════════════════════════════════╗")
    lines.append("║ SUBSTRATE                             ║")
    lines.append("╠═══════════════════════════════════════╣")
    lines.append(f"║ Identity: {substrate.identity.value:<27} ║")
    
    if invoke:
        try:
            result = substrate.invoke()
            lines.append(f"║ Expression: λ() → {result:<19} ║")
        except Exception as e:
            lines.append(f"║ Expression: λ() → ERROR           ║")
    else:
        lines.append(f"║ Expression: λ() → <not invoked>   ║")
    
    lines.append("╚═══════════════════════════════════════╝")
    return "\n".join(lines)


def pretty_dimension(dimension: Dimension, index: Optional[int] = None) -> str:
    """
    Pretty print a dimension.

    Args:
        dimension: The dimension to display
        index: Optional index in the divide() list (0-8)

    Returns:
        Human-readable string representation
    """
    # Get dimension name from level
    name = DIMENSION_LEVEL_TO_NAME.get(dimension.level, f"Level {dimension.level}")

    lines = []
    lines.append("┌───────────────────────────────────────┐")
    lines.append(f"│ DIMENSION: {name.upper():<24} │")
    lines.append("├───────────────────────────────────────┤")
    if index is not None:
        lines.append(f"│ Index: {index:<30} │")
    lines.append(f"│ Level: {dimension.level:<30} │")
    lines.append("└───────────────────────────────────────┘")
    return "\n".join(lines)


def pretty_dimensions(dimensions: List[Dimension], compact: bool = False) -> str:
    """
    Pretty print a list of dimensions.

    Args:
        dimensions: List of dimensions to display
        compact: Use compact format (default: False)

    Returns:
        Human-readable string representation
    """
    if compact:
        lines = []
        lines.append("╔═══════════════════════════════════════════════════════════╗")
        lines.append("║ DIMENSIONS (9)                                            ║")
        lines.append("╠═════╦═══════════════════╦═══════════════════════════════╣")
        lines.append("║ IDX ║ NAME              ║ LEVEL                         ║")
        lines.append("╠═════╬═══════════════════╬═══════════════════════════════╣")

        for idx, dim in enumerate(dimensions):
            name = DIMENSION_LEVEL_TO_NAME.get(dim.level, f"Level{dim.level}")
            lines.append(f"║ {idx:<3} ║ {name:<17} ║ {dim.level:<29} ║")

        lines.append("╚═════╩═══════════════════╩═══════════════════════════════╝")
        return "\n".join(lines)
    else:
        # Full format - show each dimension separately
        parts = []
        for idx, dim in enumerate(dimensions):
            parts.append(pretty_dimension(dim, index=idx))
        return "\n\n".join(parts)


def pretty_observation(observation: Observation) -> str:
    """
    Pretty print an observation.
    
    Args:
        observation: The observation to display
    
    Returns:
        Human-readable string representation
    """
    lines = []
    lines.append("╔═══════════════════════════════════════╗")
    lines.append("║ OBSERVATION                           ║")
    lines.append("╠═══════════════════════════════════════╣")
    lines.append(f"║ Substrate ID: {observation.substrate_id.value:<19} ║")
    lines.append(f"║ Lens ID: {observation.lens_id:<26} ║")
    lines.append(f"║ Manifestation: {observation.manifestation:<18} ║")
    lines.append("╚═══════════════════════════════════════╝")
    return "\n".join(lines)


def pretty_observer(observer: Observer) -> str:
    """
    Pretty print an observer.
    
    Args:
        observer: The observer to display
    
    Returns:
        Human-readable string representation
    """
    lines = []
    lines.append("╔═══════════════════════════════════════╗")
    lines.append("║ OBSERVER                              ║")
    lines.append("╠═══════════════════════════════════════╣")
    lines.append(f"║ Observations: {observer.observation_count:<23} ║")
    lines.append("╚═══════════════════════════════════════╝")
    return "\n".join(lines)


def compact_substrate(substrate: Substrate) -> str:
    """
    Compact one-line representation of substrate.
    
    Args:
        substrate: The substrate to display
    
    Returns:
        Compact string representation
    
    Example:
        Substrate(id=42, expr=λ()→100)
    """
    try:
        result = substrate.invoke()
        return f"Substrate(id={substrate.identity.value}, expr=λ()→{result})"
    except:
        return f"Substrate(id={substrate.identity.value}, expr=λ()→ERROR)"


def compact_dimension(dimension: Dimension, index: Optional[int] = None) -> str:
    """
    Compact one-line representation of dimension.

    Args:
        dimension: The dimension to display
        index: Optional index in the divide() list (0-8)

    Returns:
        Compact string representation

    Example:
        Dimension[0:void](level=0)
    """
    name = DIMENSION_LEVEL_TO_NAME.get(dimension.level, f"level{dimension.level}")
    if index is not None:
        return f"Dimension[{index}:{name}](level={dimension.level})"
    else:
        return f"Dimension[{name}](level={dimension.level})"

