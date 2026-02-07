"""
Truth Navigator - Ask Questions, Get Answers

An interactive interface to invoke mathematical truths.
No training. No datasets. Just relationships that exist.
"""

import sys
import math
import re
from typing import Any, Dict, Optional, Callable, Tuple

sys.path.insert(0, '.')


# ═══════════════════════════════════════════════════════════════════
# TRUTH CATALOG - Relationships that EXIST
# ═══════════════════════════════════════════════════════════════════

CATALOG = {
    # ─────────────────────────────────────────────────────────────
    # GEOMETRY
    # ─────────────────────────────────────────────────────────────
    'circle_area': {
        'params': ['radius'],
        'formula': lambda r: math.pi * r ** 2,
        'derivation': 'A = πr²',
        'unit': 'square units',
    },
    'circle_circumference': {
        'params': ['radius'],
        'formula': lambda r: 2 * math.pi * r,
        'derivation': 'C = 2πr',
        'unit': 'units',
    },
    'sphere_volume': {
        'params': ['radius'],
        'formula': lambda r: (4/3) * math.pi * r ** 3,
        'derivation': 'V = (4/3)πr³',
        'unit': 'cubic units',
    },
    'sphere_surface_area': {
        'params': ['radius'],
        'formula': lambda r: 4 * math.pi * r ** 2,
        'derivation': 'A = 4πr²',
        'unit': 'square units',
    },
    'triangle_area': {
        'params': ['base', 'height'],
        'formula': lambda b, h: 0.5 * b * h,
        'derivation': 'A = ½bh',
        'unit': 'square units',
    },
    'rectangle_area': {
        'params': ['length', 'width'],
        'formula': lambda l, w: l * w,
        'derivation': 'A = l × w',
        'unit': 'square units',
    },
    'pythagorean': {
        'params': ['a', 'b'],
        'formula': lambda a, b: math.sqrt(a**2 + b**2),
        'derivation': 'c = √(a² + b²)',
        'unit': 'units',
    },
    
    # ─────────────────────────────────────────────────────────────
    # PHYSICS
    # ─────────────────────────────────────────────────────────────
    'kinetic_energy': {
        'params': ['mass', 'velocity'],
        'formula': lambda m, v: 0.5 * m * v ** 2,
        'derivation': 'KE = ½mv²',
        'unit': 'joules',
    },
    'potential_energy': {
        'params': ['mass', 'height'],
        'formula': lambda m, h: m * 9.81 * h,
        'derivation': 'PE = mgh (g=9.81)',
        'unit': 'joules',
    },
    'momentum': {
        'params': ['mass', 'velocity'],
        'formula': lambda m, v: m * v,
        'derivation': 'p = mv',
        'unit': 'kg·m/s',
    },
    'force': {
        'params': ['mass', 'acceleration'],
        'formula': lambda m, a: m * a,
        'derivation': 'F = ma',
        'unit': 'newtons',
    },
    'gravitational_force': {
        'params': ['mass1', 'mass2', 'distance'],
        'formula': lambda m1, m2, r: 6.674e-11 * m1 * m2 / r ** 2,
        'derivation': 'F = Gm₁m₂/r² (G=6.674×10⁻¹¹)',
        'unit': 'newtons',
    },
    'velocity': {
        'params': ['distance', 'time'],
        'formula': lambda d, t: d / t,
        'derivation': 'v = d/t',
        'unit': 'm/s',
    },
    'acceleration': {
        'params': ['velocity_change', 'time'],
        'formula': lambda dv, t: dv / t,
        'derivation': 'a = Δv/t',
        'unit': 'm/s²',
    },
    'work': {
        'params': ['force', 'distance'],
        'formula': lambda f, d: f * d,
        'derivation': 'W = Fd',
        'unit': 'joules',
    },
    'power': {
        'params': ['work', 'time'],
        'formula': lambda w, t: w / t,
        'derivation': 'P = W/t',
        'unit': 'watts',
    },
    'pressure': {
        'params': ['force', 'area'],
        'formula': lambda f, a: f / a,
        'derivation': 'P = F/A',
        'unit': 'pascals',
    },
    'density': {
        'params': ['mass', 'volume'],
        'formula': lambda m, v: m / v,
        'derivation': 'ρ = m/V',
        'unit': 'kg/m³',
    },
    'wave_speed': {
        'params': ['frequency', 'wavelength'],
        'formula': lambda f, w: f * w,
        'derivation': 'v = fλ',
        'unit': 'm/s',
    },
    
    # ─────────────────────────────────────────────────────────────
    # FINANCE
    # ─────────────────────────────────────────────────────────────
    'compound_interest': {
        'params': ['principal', 'rate', 'years', 'compounds_per_year'],
        'formula': lambda p, r, t, n: p * (1 + r/n) ** (n * t),
        'derivation': 'A = P(1 + r/n)^(nt)',
        'unit': 'currency',
    },
    'simple_interest': {
        'params': ['principal', 'rate', 'years'],
        'formula': lambda p, r, t: p * (1 + r * t),
        'derivation': 'A = P(1 + rt)',
        'unit': 'currency',
    },
    'present_value': {
        'params': ['future_value', 'rate', 'years'],
        'formula': lambda fv, r, t: fv / (1 + r) ** t,
        'derivation': 'PV = FV/(1+r)^t',
        'unit': 'currency',
    },
    'rule_of_72': {
        'params': ['rate_percent'],
        'formula': lambda r: 72 / r,
        'derivation': 'Years to double ≈ 72/r%',
        'unit': 'years',
    },
    'loan_payment': {
        'params': ['principal', 'annual_rate', 'months'],
        'formula': lambda p, r, n: p * (r/12) * (1 + r/12)**n / ((1 + r/12)**n - 1) if r > 0 else p/n,
        'derivation': 'PMT = P × r(1+r)^n / ((1+r)^n - 1)',
        'unit': 'currency/month',
    },
    
    # ─────────────────────────────────────────────────────────────
    # AUTOMOTIVE
    # ─────────────────────────────────────────────────────────────
    'fuel_consumption': {
        'params': ['distance_km', 'rate_L_per_100km'],
        'formula': lambda d, r: (r / 100) * d,
        'derivation': 'Fuel = (rate/100) × distance',
        'unit': 'liters',
    },
    'stopping_distance': {
        'params': ['velocity_m_s', 'friction_coefficient'],
        'formula': lambda v, mu: v ** 2 / (2 * mu * 9.81),
        'derivation': 'd = v²/(2μg)',
        'unit': 'meters',
    },
    'tire_rotations': {
        'params': ['distance_m', 'tire_diameter_m'],
        'formula': lambda d, diam: d / (math.pi * diam),
        'derivation': 'rotations = distance / (πd)',
        'unit': 'rotations',
    },
    'braking_force': {
        'params': ['mass', 'friction_coefficient'],
        'formula': lambda m, mu: mu * m * 9.81,
        'derivation': 'F = μmg',
        'unit': 'newtons',
    },
    
    # ─────────────────────────────────────────────────────────────
    # CONVERSIONS
    # ─────────────────────────────────────────────────────────────
    'mph_to_mps': {
        'params': ['mph'],
        'formula': lambda mph: mph * 0.44704,
        'derivation': 'm/s = mph × 0.44704',
        'unit': 'm/s',
    },
    'celsius_to_fahrenheit': {
        'params': ['celsius'],
        'formula': lambda c: c * 9/5 + 32,
        'derivation': 'F = C × 9/5 + 32',
        'unit': '°F',
    },
    'fahrenheit_to_celsius': {
        'params': ['fahrenheit'],
        'formula': lambda f: (f - 32) * 5/9,
        'derivation': 'C = (F - 32) × 5/9',
        'unit': '°C',
    },
    'kg_to_lbs': {
        'params': ['kg'],
        'formula': lambda kg: kg * 2.20462,
        'derivation': 'lbs = kg × 2.20462',
        'unit': 'lbs',
    },
    'miles_to_km': {
        'params': ['miles'],
        'formula': lambda mi: mi * 1.60934,
        'derivation': 'km = miles × 1.60934',
        'unit': 'km',
    },
}


def parse_question(question: str) -> Tuple[Optional[str], Dict[str, float]]:
    """Parse a natural language question into formula + parameters."""
    q = question.lower().strip()
    
    # Direct formula invocation: "circle_area radius=5"
    # Try exact matches first (longest match wins)
    matched_formula = None
    for formula_name in sorted(CATALOG.keys(), key=len, reverse=True):
        if formula_name in q.replace(' ', '_'):
            matched_formula = formula_name
            break
    
    if matched_formula:
        params = {}
        # Extract numbers with optional param names (support underscores in names)
        pattern = r'(\w+)\s*=\s*([\d.]+)'
        matches = re.findall(pattern, q)
        for name, value in matches:
            params[name.lower()] = float(value)
        
        # If no named params, try to extract just numbers
        if not params:
            numbers = re.findall(r'[\d.]+', q)
            formula_params = CATALOG[matched_formula]['params']
            for i, num in enumerate(numbers):
                if i < len(formula_params):
                    params[formula_params[i]] = float(num)
        
        return matched_formula, params
    
    # Natural language patterns
    patterns = [
        # Circle area
        (r'area.*(circle|radius)\s*(?:of|with|is|=)?\s*([\d.]+)', 'circle_area', ['radius']),
        (r'circle.*radius\s*([\d.]+).*area', 'circle_area', ['radius']),
        
        # Sphere volume
        (r'volume.*sphere.*radius\s*([\d.]+)', 'sphere_volume', ['radius']),
        (r'sphere.*radius\s*([\d.]+).*volume', 'sphere_volume', ['radius']),
        
        # Kinetic energy
        (r'kinetic.*energy.*([\d.]+)\s*kg.*([\d.]+)\s*m/s', 'kinetic_energy', ['mass', 'velocity']),
        (r'([\d.]+)\s*kg.*moving.*([\d.]+)\s*m/s', 'kinetic_energy', ['mass', 'velocity']),
        
        # Momentum
        (r'momentum.*([\d.]+)\s*kg.*([\d.]+)', 'momentum', ['mass', 'velocity']),
        
        # Force
        (r'force.*([\d.]+)\s*kg.*([\d.]+)', 'force', ['mass', 'acceleration']),
        
        # Compound interest
        (r'compound.*\$([\d,]+).*(\d+\.?\d*)%.*(\d+)\s*year', 'compound_interest', ['principal', 'rate', 'years']),
        
        # Temperature
        (r'([\d.]+)\s*(?:degrees?\s*)?(?:c|celsius).*(?:to|in)\s*(?:f|fahrenheit)', 'celsius_to_fahrenheit', ['celsius']),
        (r'([\d.]+)\s*(?:degrees?\s*)?(?:f|fahrenheit).*(?:to|in)\s*(?:c|celsius)', 'fahrenheit_to_celsius', ['fahrenheit']),
        
        # Distance
        (r'([\d.]+)\s*miles?\s*(?:to|in)\s*km', 'miles_to_km', ['miles']),
        
        # Stopping distance
        (r'stopping.*distance.*([\d.]+)\s*m/s', 'stopping_distance', ['velocity_m_s']),
    ]
    
    for pattern, formula, param_names in patterns:
        match = re.search(pattern, q)
        if match:
            params = {}
            for i, name in enumerate(param_names):
                if i < len(match.groups()):
                    val = match.group(i + 1).replace(',', '')
                    params[name] = float(val) / 100 if 'rate' in name and '%' in q else float(val)
            return formula, params
    
    return None, {}


def invoke(formula_name: str, params: Dict[str, float]) -> Tuple[Any, str]:
    """Invoke a truth from the catalog."""
    if formula_name not in CATALOG:
        return None, f"Unknown formula: {formula_name}"
    
    entry = CATALOG[formula_name]
    required = entry['params']
    
    # Check for missing params
    missing = [p for p in required if p not in params]
    if missing:
        return None, f"Missing: {', '.join(missing)}"
    
    # Fill in defaults
    if 'compounds_per_year' in required and 'compounds_per_year' not in params:
        params['compounds_per_year'] = 12  # monthly
    if 'friction_coefficient' in required and 'friction_coefficient' not in params:
        params['friction_coefficient'] = 0.7  # dry road
    
    # Get values in order
    args = [params[p] for p in required]
    
    # INVOKE
    result = entry['formula'](*args)
    derivation = entry['derivation']
    unit = entry['unit']
    
    return result, f"{derivation} = {result:.6g} {unit}"


def show_catalog():
    """Show available formulas."""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " TRUTH CATALOG - Relationships That Exist ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    categories = {
        'GEOMETRY': ['circle_area', 'circle_circumference', 'sphere_volume', 
                     'sphere_surface_area', 'triangle_area', 'rectangle_area', 'pythagorean'],
        'PHYSICS': ['kinetic_energy', 'potential_energy', 'momentum', 'force',
                    'gravitational_force', 'velocity', 'acceleration', 'work', 
                    'power', 'pressure', 'density', 'wave_speed'],
        'FINANCE': ['compound_interest', 'simple_interest', 'present_value',
                    'rule_of_72', 'loan_payment'],
        'AUTOMOTIVE': ['fuel_consumption', 'stopping_distance', 'tire_rotations', 'braking_force'],
        'CONVERSIONS': ['mph_to_mps', 'celsius_to_fahrenheit', 'fahrenheit_to_celsius',
                        'kg_to_lbs', 'miles_to_km'],
    }
    
    for category, formulas in categories.items():
        print(f"  {category}:")
        for name in formulas:
            if name in CATALOG:
                entry = CATALOG[name]
                params = ', '.join(entry['params'])
                print(f"    {name}({params})")
                print(f"      → {entry['derivation']}")
        print()


def main():
    """Interactive truth navigator."""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " TRUTH NAVIGATOR ".center(68) + "║")
    print("║" + " Ask questions. Get answers. No AI. Just math. ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    print("  Commands:")
    print("    help     - Show available formulas")
    print("    quit     - Exit")
    print()
    print("  Examples:")
    print("    > circle_area radius=5")
    print("    > kinetic_energy mass=1600 velocity=30")
    print("    > What is the area of a circle with radius 7.3?")
    print("    > 100 fahrenheit to celsius")
    print("    > stopping_distance velocity_m_s=30")
    print()
    print("─" * 70)
    
    while True:
        try:
            question = input("\n  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Goodbye.\n")
            break
        
        if not question:
            continue
        
        if question.lower() in ('quit', 'exit', 'q'):
            print("\n  Goodbye.\n")
            break
        
        if question.lower() in ('help', 'catalog', 'list', '?'):
            show_catalog()
            continue
        
        # Parse and invoke
        formula, params = parse_question(question)
        
        if formula is None:
            print()
            print("  [?] Couldn't understand. Try:")
            print("      - circle_area radius=5")
            print("      - kinetic_energy mass=1600 velocity=30")
            print("      - Type 'help' to see all formulas")
            continue
        
        result, derivation = invoke(formula, params)
        
        if result is None:
            print(f"\n  [!] {derivation}")
            print(f"      Required: {', '.join(CATALOG[formula]['params'])}")
            continue
        
        print()
        print(f"  ┌{'─' * 66}┐")
        print(f"  │ {'TRUTH':^64} │")
        print(f"  ├{'─' * 66}┤")
        print(f"  │ {derivation:<64} │")
        print(f"  └{'─' * 66}┘")
        print()
        print(f"    This value EXISTED. You just asked.")


if __name__ == "__main__":
    main()
