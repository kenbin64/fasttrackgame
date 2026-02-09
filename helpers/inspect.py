"""
Substrate Inspection Tools - Understand Substrate Structure

Tools to inspect and understand substrates:

- inspect_substrate() - Complete substrate analysis
- trace_division() - Trace dimensional division process
- analyze_expression() - Analyze expression behavior
- compare_substrates() - Compare two substrates

CHARTER COMPLIANCE:
✅ Principle 2: Passive until invoked
✅ Principle 5: Pure functions only
✅ Principle 6: All relationships visible
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional
from kernel import Substrate, Dimension
from .query import DIMENSION_LEVEL_TO_NAME


def inspect_substrate(substrate: Substrate, invoke: bool = True) -> Dict[str, Any]:
    """
    Complete substrate analysis.
    
    Args:
        substrate: The substrate to inspect
        invoke: Whether to invoke the expression (default: True)
    
    Returns:
        Dictionary with inspection results
    
    Example:
        info = inspect_substrate(substrate)
        print(f"Identity: {info['identity']}")
        print(f"Result: {info['invocation_result']}")
    """
    info = {
        "identity": substrate.identity.value,
        "identity_hex": hex(substrate.identity.value),
        "identity_binary": bin(substrate.identity.value),
    }
    
    if invoke:
        try:
            result = substrate.invoke()
            info["invocation_result"] = result
            info["invocation_success"] = True
            info["invocation_error"] = None
        except Exception as e:
            info["invocation_result"] = None
            info["invocation_success"] = False
            info["invocation_error"] = str(e)
    else:
        info["invocation_result"] = None
        info["invocation_success"] = None
        info["invocation_error"] = None
    
    # Analyze dimensions
    try:
        dimensions = substrate.divide()
        info["dimension_count"] = len(dimensions)
        info["dimensions"] = [
            {
                "index": idx,
                "name": DIMENSION_LEVEL_TO_NAME.get(dim.level, f"level{dim.level}"),
                "level": dim.level,
            }
            for idx, dim in enumerate(dimensions)
        ]
    except Exception as e:
        info["dimension_count"] = 0
        info["dimensions"] = []
        info["division_error"] = str(e)
    
    return info


def trace_division(substrate: Substrate) -> str:
    """
    Trace the dimensional division process.
    
    Args:
        substrate: The substrate to trace
    
    Returns:
        Human-readable trace of division
    
    Example:
        print(trace_division(substrate))
    """
    lines = []
    lines.append("═" * 60)
    lines.append("DIMENSIONAL DIVISION TRACE")
    lines.append("═" * 60)
    lines.append(f"Substrate Identity: {substrate.identity.value}")
    lines.append("")
    
    try:
        result = substrate.invoke()
        lines.append(f"Unity (before division): {result}")
        lines.append("")
    except Exception as e:
        lines.append(f"Unity (before division): ERROR - {e}")
        lines.append("")
    
    try:
        dimensions = substrate.divide()
        lines.append(f"Division created {len(dimensions)} dimensions:")
        lines.append("")
        
        for idx, dim in enumerate(dimensions):
            name = DIMENSION_LEVEL_TO_NAME.get(dim.level, f"level{dim.level}")
            lines.append(f"  [{idx}] {name.upper()}")
            lines.append(f"      Level: {dim.level}")
            lines.append("")
        
    except Exception as e:
        lines.append(f"Division failed: {e}")
    
    lines.append("═" * 60)
    return "\n".join(lines)


def analyze_expression(substrate: Substrate, iterations: int = 10) -> Dict[str, Any]:
    """
    Analyze expression behavior over multiple invocations.
    
    Args:
        substrate: The substrate to analyze
        iterations: Number of times to invoke (default: 10)
    
    Returns:
        Dictionary with analysis results
    
    Example:
        analysis = analyze_expression(substrate, iterations=100)
        print(f"Deterministic: {analysis['is_deterministic']}")
        print(f"Average: {analysis['average']}")
    """
    results = []
    errors = []
    
    for i in range(iterations):
        try:
            result = substrate.invoke()
            results.append(result)
        except Exception as e:
            errors.append(str(e))
    
    analysis = {
        "iterations": iterations,
        "successful_invocations": len(results),
        "failed_invocations": len(errors),
        "success_rate": len(results) / iterations if iterations > 0 else 0,
    }
    
    if results:
        analysis["is_deterministic"] = len(set(results)) == 1
        analysis["unique_values"] = len(set(results))
        analysis["min"] = min(results)
        analysis["max"] = max(results)
        analysis["average"] = sum(results) / len(results)
        analysis["first_result"] = results[0]
        analysis["last_result"] = results[-1]
    else:
        analysis["is_deterministic"] = None
        analysis["unique_values"] = 0
    
    if errors:
        analysis["errors"] = errors
    
    return analysis


def compare_substrates(substrate1: Substrate, substrate2: Substrate) -> Dict[str, Any]:
    """
    Compare two substrates.
    
    Args:
        substrate1: First substrate
        substrate2: Second substrate
    
    Returns:
        Dictionary with comparison results
    
    Example:
        comparison = compare_substrates(s1, s2)
        print(f"Same identity: {comparison['same_identity']}")
        print(f"Same result: {comparison['same_invocation_result']}")
    """
    comparison = {
        "identity1": substrate1.identity.value,
        "identity2": substrate2.identity.value,
        "same_identity": substrate1.identity.value == substrate2.identity.value,
    }
    
    # Compare invocation results
    try:
        result1 = substrate1.invoke()
        result2 = substrate2.invoke()
        comparison["invocation_result1"] = result1
        comparison["invocation_result2"] = result2
        comparison["same_invocation_result"] = result1 == result2
    except Exception as e:
        comparison["invocation_result1"] = None
        comparison["invocation_result2"] = None
        comparison["same_invocation_result"] = None
        comparison["comparison_error"] = str(e)
    
    return comparison

