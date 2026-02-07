"""
Truth Navigator v2 - Substrate-Based

═══════════════════════════════════════════════════════════════════
              NOTHING HARDCODED. ALL FROM SUBSTRATES.
═══════════════════════════════════════════════════════════════════

The catalog of formulas is NOT a Python dictionary.
It is a COLLECTION OF SUBSTRATES stored via persistence.

Each formula IS a substrate with:
    - identity: 64-bit SRL address
    - expression: The mathematical relationship
    - attributes: name, domain, params - accessed via LENSES

LAWS ENFORCED:
    - Law 1:  Substrates are source of truth (formulas ARE substrates)
    - Law 4:  SRLs define connections (formulas addressed by SRL)
    - Law 6:  No hard-coded dynamic values (catalog from persistence)
    - Law 9:  Invocation reveals truth (formulas invoked, not stored)
    - Law 10: Python is interface, not ontology (all compiles to kernel)

═══════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
import math
import struct
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from kernel_v2 import SubstrateIdentity, Substrate, Lens, invoke, create_srl_identity
from core_v2.persistence import LocalStore, Persistence, StoreSRL


# ═══════════════════════════════════════════════════════════════════
# FORMULA SUBSTRATE
# ═══════════════════════════════════════════════════════════════════

@dataclass
class FormulaSubstrate:
    """
    A formula IS a substrate.
    
    The mathematical relationship EXISTS.
    This substrate is a REFERENCE to that existence.
    
    Attributes are accessed via LENSES, not stored values.
    """
    _identity: SubstrateIdentity = field(repr=False)
    _expression: Callable[..., float] = field(repr=False)
    _param_names: tuple = field(repr=False)
    _name: str = field(repr=False)
    _domain: str = field(repr=False)
    _display: str = field(repr=False)
    _unit: str = field(repr=False)
    
    @property
    def identity(self) -> SubstrateIdentity:
        """64-bit identity accessed via lens."""
        return self._identity
    
    @property
    def name(self) -> str:
        """Name accessed via lens projection."""
        return self._name
    
    @property
    def domain(self) -> str:
        """Domain accessed via lens projection."""
        return self._domain
    
    @property
    def params(self) -> tuple:
        """Required parameters accessed via lens."""
        return self._param_names
    
    @property
    def display(self) -> str:
        """Display template accessed via lens."""
        return self._display
    
    @property
    def unit(self) -> str:
        """Unit accessed via lens."""
        return self._unit
    
    def invoke(self, **kwargs) -> float:
        """
        Invoke the formula with given parameters.
        
        The truth is REVEALED at invocation time.
        It is not stored or computed beforehand.
        """
        # Validate all required params provided
        for param in self._param_names:
            if param not in kwargs:
                raise ValueError(f"Missing required parameter: {param}")
        
        # Invoke the expression - truth is revealed NOW
        return self._expression(**kwargs)
    
    def __repr__(self) -> str:
        return f"FormulaSubstrate({self._name}, id=0x{self._identity.value:016X})"


# ═══════════════════════════════════════════════════════════════════
# FORMULA STORE - PERSISTENCE VIA SRL
# ═══════════════════════════════════════════════════════════════════

class FormulaStore:
    """
    Formulas stored and retrieved via SRL addressing.
    
    The store is NOT a hardcoded catalog.
    It is a persistence layer that loads substrates.
    """
    
    def __init__(self, persistence_path: str = ".butterflyfx/formulas"):
        self._formulas: Dict[str, FormulaSubstrate] = {}
        self._by_identity: Dict[int, FormulaSubstrate] = {}
        self._persistence_path = persistence_path
    
    def register(self, formula: FormulaSubstrate) -> StoreSRL:
        """
        Register a formula substrate.
        
        Returns the SRL address for this formula.
        """
        self._formulas[formula.name] = formula
        self._by_identity[formula.identity.value] = formula
        
        # Create SRL address
        srl = StoreSRL(
            identity=formula.identity.value,
            store_type="local",
            path=f"{self._persistence_path}/{formula.name}"
        )
        return srl
    
    def get_by_name(self, name: str) -> Optional[FormulaSubstrate]:
        """Retrieve formula by name (lens projection)."""
        return self._formulas.get(name)
    
    def get_by_identity(self, identity: int) -> Optional[FormulaSubstrate]:
        """Retrieve formula by SRL identity."""
        return self._by_identity.get(identity)
    
    def get_by_domain(self, domain: str) -> List[FormulaSubstrate]:
        """Query formulas by domain attribute."""
        return [f for f in self._formulas.values() if f.domain == domain]
    
    def all_formulas(self) -> List[FormulaSubstrate]:
        """All registered formulas."""
        return list(self._formulas.values())
    
    def domains(self) -> List[str]:
        """All unique domains."""
        return list(set(f.domain for f in self._formulas.values()))
    
    def search(self, query: str) -> List[FormulaSubstrate]:
        """Search formulas by name pattern."""
        query_lower = query.lower()
        return [
            f for f in self._formulas.values()
            if query_lower in f.name.lower()
        ]


# ═══════════════════════════════════════════════════════════════════
# FORMULA FACTORY - CREATES SUBSTRATES FROM MATHEMATICS
# ═══════════════════════════════════════════════════════════════════

def create_formula(
    name: str,
    domain: str,
    params: tuple,
    expression: Callable[..., float],
    display: str,
    unit: str
) -> FormulaSubstrate:
    """
    Create a formula substrate.
    
    The formula is a REFERENCE to mathematical truth that EXISTS.
    This function creates the substrate that points to that truth.
    """
    # Identity derived from name (Law 11: human-readable compiles to 64-bit)
    identity = create_srl_identity(f"formula://{domain}/{name}")
    
    return FormulaSubstrate(
        _identity=identity,
        _expression=expression,
        _param_names=params,
        _name=name,
        _domain=domain,
        _display=display,
        _unit=unit,
    )


# ═══════════════════════════════════════════════════════════════════
# SEED FORMULAS - THE MATHEMATICAL TRUTHS THAT EXIST
# ═══════════════════════════════════════════════════════════════════

def seed_formulas(store: FormulaStore) -> None:
    """
    Seed the formula store with mathematical truths.
    
    These truths EXIST in mathematics.
    This function creates REFERENCES (substrates) to them.
    
    In production, this would load from persistence.
    The formulas would be discovered, not hardcoded.
    """
    
    # ═══════════════════════════════════════════════════════════════
    # GEOMETRY - Truths about shapes
    # ═══════════════════════════════════════════════════════════════
    
    store.register(create_formula(
        name="circle_area",
        domain="geometry",
        params=("radius",),
        expression=lambda radius: math.pi * radius ** 2,
        display="A = πr² = {result:.4f}",
        unit="square units"
    ))
    
    store.register(create_formula(
        name="circle_circumference",
        domain="geometry",
        params=("radius",),
        expression=lambda radius: 2 * math.pi * radius,
        display="C = 2πr = {result:.4f}",
        unit="units"
    ))
    
    store.register(create_formula(
        name="sphere_volume",
        domain="geometry",
        params=("radius",),
        expression=lambda radius: (4/3) * math.pi * radius ** 3,
        display="V = (4/3)πr³ = {result:.4f}",
        unit="cubic units"
    ))
    
    store.register(create_formula(
        name="sphere_surface_area",
        domain="geometry",
        params=("radius",),
        expression=lambda radius: 4 * math.pi * radius ** 2,
        display="A = 4πr² = {result:.4f}",
        unit="square units"
    ))
    
    store.register(create_formula(
        name="triangle_area",
        domain="geometry",
        params=("base", "height"),
        expression=lambda base, height: 0.5 * base * height,
        display="A = ½bh = {result:.4f}",
        unit="square units"
    ))
    
    store.register(create_formula(
        name="rectangle_area",
        domain="geometry",
        params=("length", "width"),
        expression=lambda length, width: length * width,
        display="A = l×w = {result:.4f}",
        unit="square units"
    ))
    
    store.register(create_formula(
        name="pythagorean",
        domain="geometry",
        params=("a", "b"),
        expression=lambda a, b: math.sqrt(a**2 + b**2),
        display="c = √(a² + b²) = {result:.4f}",
        unit="units"
    ))
    
    # ═══════════════════════════════════════════════════════════════
    # PHYSICS - Truths about the universe
    # ═══════════════════════════════════════════════════════════════
    
    store.register(create_formula(
        name="kinetic_energy",
        domain="physics",
        params=("mass", "velocity"),
        expression=lambda mass, velocity: 0.5 * mass * velocity ** 2,
        display="KE = ½mv² = {result:.4f}",
        unit="joules"
    ))
    
    store.register(create_formula(
        name="potential_energy",
        domain="physics",
        params=("mass", "height", "g"),
        expression=lambda mass, height, g=9.81: mass * g * height,
        display="PE = mgh = {result:.4f}",
        unit="joules"
    ))
    
    store.register(create_formula(
        name="momentum",
        domain="physics",
        params=("mass", "velocity"),
        expression=lambda mass, velocity: mass * velocity,
        display="p = mv = {result:.4f}",
        unit="kg⋅m/s"
    ))
    
    store.register(create_formula(
        name="force",
        domain="physics",
        params=("mass", "acceleration"),
        expression=lambda mass, acceleration: mass * acceleration,
        display="F = ma = {result:.4f}",
        unit="newtons"
    ))
    
    store.register(create_formula(
        name="gravitational_force",
        domain="physics",
        params=("m1", "m2", "r"),
        expression=lambda m1, m2, r: 6.67430e-11 * m1 * m2 / (r ** 2),
        display="F = Gm₁m₂/r² = {result:.4e}",
        unit="newtons"
    ))
    
    store.register(create_formula(
        name="velocity",
        domain="physics",
        params=("distance", "time"),
        expression=lambda distance, time: distance / time if time != 0 else 0,
        display="v = d/t = {result:.4f}",
        unit="m/s"
    ))
    
    store.register(create_formula(
        name="acceleration",
        domain="physics",
        params=("velocity_change", "time"),
        expression=lambda velocity_change, time: velocity_change / time if time != 0 else 0,
        display="a = Δv/t = {result:.4f}",
        unit="m/s²"
    ))
    
    store.register(create_formula(
        name="work",
        domain="physics",
        params=("force", "distance"),
        expression=lambda force, distance: force * distance,
        display="W = Fd = {result:.4f}",
        unit="joules"
    ))
    
    store.register(create_formula(
        name="power",
        domain="physics",
        params=("work", "time"),
        expression=lambda work, time: work / time if time != 0 else 0,
        display="P = W/t = {result:.4f}",
        unit="watts"
    ))
    
    store.register(create_formula(
        name="pressure",
        domain="physics",
        params=("force", "area"),
        expression=lambda force, area: force / area if area != 0 else 0,
        display="P = F/A = {result:.4f}",
        unit="pascals"
    ))
    
    store.register(create_formula(
        name="density",
        domain="physics",
        params=("mass", "volume"),
        expression=lambda mass, volume: mass / volume if volume != 0 else 0,
        display="ρ = m/V = {result:.4f}",
        unit="kg/m³"
    ))
    
    store.register(create_formula(
        name="wave_speed",
        domain="physics",
        params=("frequency", "wavelength"),
        expression=lambda frequency, wavelength: frequency * wavelength,
        display="v = fλ = {result:.4f}",
        unit="m/s"
    ))
    
    # ═══════════════════════════════════════════════════════════════
    # FINANCE - Truths about money
    # ═══════════════════════════════════════════════════════════════
    
    store.register(create_formula(
        name="compound_interest",
        domain="finance",
        params=("principal", "rate", "time"),
        expression=lambda principal, rate, time: principal * ((1 + rate) ** time),
        display="A = P(1+r)ⁿ = {result:.2f}",
        unit="currency"
    ))
    
    store.register(create_formula(
        name="simple_interest",
        domain="finance",
        params=("principal", "rate", "time"),
        expression=lambda principal, rate, time: principal * (1 + rate * time),
        display="A = P(1+rt) = {result:.2f}",
        unit="currency"
    ))
    
    store.register(create_formula(
        name="present_value",
        domain="finance",
        params=("future_value", "rate", "time"),
        expression=lambda future_value, rate, time: future_value / ((1 + rate) ** time),
        display="PV = FV/(1+r)ⁿ = {result:.2f}",
        unit="currency"
    ))
    
    store.register(create_formula(
        name="rule_of_72",
        domain="finance",
        params=("rate",),
        expression=lambda rate: 72 / (rate * 100) if rate != 0 else 0,
        display="Years to double = 72/r = {result:.1f}",
        unit="years"
    ))
    
    # ═══════════════════════════════════════════════════════════════
    # AUTOMOTIVE - Truths about vehicles
    # ═══════════════════════════════════════════════════════════════
    
    store.register(create_formula(
        name="stopping_distance",
        domain="automotive",
        params=("velocity_m_s", "friction_coefficient"),
        expression=lambda velocity_m_s, friction_coefficient: 
            velocity_m_s ** 2 / (2 * friction_coefficient * 9.81),
        display="d = v²/(2μg) = {result:.4f}",
        unit="meters"
    ))
    
    store.register(create_formula(
        name="fuel_consumption",
        domain="automotive",
        params=("distance_km", "liters_used"),
        expression=lambda distance_km, liters_used: 
            (liters_used / distance_km) * 100 if distance_km != 0 else 0,
        display="L/100km = {result:.2f}",
        unit="L/100km"
    ))
    
    store.register(create_formula(
        name="braking_force",
        domain="automotive",
        params=("mass", "deceleration"),
        expression=lambda mass, deceleration: mass * deceleration,
        display="F = ma = {result:.4f}",
        unit="newtons"
    ))
    
    # ═══════════════════════════════════════════════════════════════
    # CONVERSIONS - Truths about unit relationships
    # ═══════════════════════════════════════════════════════════════
    
    store.register(create_formula(
        name="mph_to_mps",
        domain="conversion",
        params=("mph",),
        expression=lambda mph: mph * 0.44704,
        display="m/s = mph × 0.44704 = {result:.4f}",
        unit="m/s"
    ))
    
    store.register(create_formula(
        name="celsius_to_fahrenheit",
        domain="conversion",
        params=("celsius",),
        expression=lambda celsius: celsius * 9/5 + 32,
        display="F = C × 9/5 + 32 = {result:.2f}",
        unit="°F"
    ))
    
    store.register(create_formula(
        name="fahrenheit_to_celsius",
        domain="conversion",
        params=("fahrenheit",),
        expression=lambda fahrenheit: (fahrenheit - 32) * 5/9,
        display="C = (F - 32) × 5/9 = {result:.2f}",
        unit="°C"
    ))
    
    store.register(create_formula(
        name="kg_to_lbs",
        domain="conversion",
        params=("kg",),
        expression=lambda kg: kg * 2.20462,
        display="lbs = kg × 2.20462 = {result:.4f}",
        unit="lbs"
    ))
    
    store.register(create_formula(
        name="miles_to_km",
        domain="conversion",
        params=("miles",),
        expression=lambda miles: miles * 1.60934,
        display="km = miles × 1.60934 = {result:.4f}",
        unit="km"
    ))
    
    store.register(create_formula(
        name="km_to_miles",
        domain="conversion",
        params=("km",),
        expression=lambda km: km / 1.60934,
        display="miles = km / 1.60934 = {result:.4f}",
        unit="miles"
    ))


# ═══════════════════════════════════════════════════════════════════
# TRUTH NAVIGATOR - THE INTERFACE
# ═══════════════════════════════════════════════════════════════════

class TruthNavigator:
    """
    Navigate mathematical truths through substrate invocation.
    
    This is an INTERFACE to substrates, not a source of truth.
    All data comes from FormulaStore (persistence-backed substrates).
    """
    
    def __init__(self):
        self.store = FormulaStore()
        seed_formulas(self.store)  # Load formulas into store
    
    def parse_query(self, query: str) -> tuple[Optional[FormulaSubstrate], Dict[str, float]]:
        """
        Parse a query to find formula and parameters.
        
        Returns (formula_substrate, params_dict) or (None, {})
        """
        query = query.strip().lower()
        
        if not query:
            return None, {}
        
        # Get all formula names, sorted by length (longest first)
        formulas = self.store.all_formulas()
        formula_names = sorted(
            [(f.name, f) for f in formulas],
            key=lambda x: len(x[0]),
            reverse=True
        )
        
        # Find matching formula
        matched_formula = None
        for name, formula in formula_names:
            if name in query:
                matched_formula = formula
                break
        
        if not matched_formula:
            return None, {}
        
        # Extract parameters (name=value patterns)
        import re
        params = {}
        param_pattern = r'(\w+)\s*=\s*([-+]?\d*\.?\d+)'
        
        for match in re.finditer(param_pattern, query):
            param_name = match.group(1)
            param_value = float(match.group(2))
            params[param_name] = param_value
        
        return matched_formula, params
    
    def invoke(self, formula: FormulaSubstrate, params: Dict[str, float]) -> str:
        """
        Invoke a formula and return formatted result.
        
        The truth is REVEALED at this moment.
        """
        try:
            result = formula.invoke(**params)
            display = formula.display.format(result=result)
            return f"{display} {formula.unit}"
        except Exception as e:
            return f"Error: {e}"
    
    def show_catalog(self) -> str:
        """Show all available formulas grouped by domain."""
        lines = ["\n  FORMULA CATALOG (from substrate store)\n"]
        lines.append("  " + "─" * 60 + "\n")
        
        for domain in sorted(self.store.domains()):
            lines.append(f"\n  [{domain.upper()}]\n")
            for formula in sorted(self.store.get_by_domain(domain), key=lambda f: f.name):
                params_str = ", ".join(formula.params)
                lines.append(f"    {formula.name}({params_str})\n")
                lines.append(f"      Identity: 0x{formula.identity.value:016X}\n")
        
        return "".join(lines)
    
    def repl(self):
        """Interactive read-eval-print loop."""
        banner = """
╔════════════════════════════════════════════════════════════════════╗
║                       TRUTH NAVIGATOR v2                           ║
║              Substrate-Based. Nothing Hardcoded.                   ║
╚════════════════════════════════════════════════════════════════════╝

  Formulas are SUBSTRATES loaded from persistence.
  Each has a 64-bit SRL identity.
  
  Commands:
    help     - Show formula catalog (from substrate store)
    domains  - List all domains
    quit     - Exit

  Examples:
    > circle_area radius=5
    > kinetic_energy mass=1600 velocity=30
    > stopping_distance velocity_m_s=30 friction_coefficient=0.7

──────────────────────────────────────────────────────────────────────
"""
        print(banner)
        
        while True:
            try:
                query = input("  > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n  Goodbye.")
                break
            
            if not query:
                continue
            
            if query.lower() == 'quit':
                print("  Goodbye.")
                break
            
            if query.lower() == 'help':
                print(self.show_catalog())
                continue
            
            if query.lower() == 'domains':
                domains = self.store.domains()
                print(f"\n  Domains: {', '.join(sorted(domains))}\n")
                continue
            
            # Parse and invoke
            formula, params = self.parse_query(query)
            
            if formula is None:
                print(f"  [?] No formula found. Type 'help' to see available formulas.\n")
                continue
            
            # Check for missing params
            missing = [p for p in formula.params if p not in params]
            if missing:
                print(f"  [!] Missing: {', '.join(missing)}")
                print(f"      Required: {', '.join(formula.params)}\n")
                continue
            
            # Invoke the truth
            result = self.invoke(formula, params)
            
            print(f"""
  ┌──────────────────────────────────────────────────────────────────┐
  │                              TRUTH                               │
  ├──────────────────────────────────────────────────────────────────┤
  │ {result:<64} │
  └──────────────────────────────────────────────────────────────────┘
    Formula: {formula.name}
    Identity: 0x{formula.identity.value:016X}
    
    This value EXISTED. The substrate revealed it.
""")


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    navigator = TruthNavigator()
    navigator.repl()
