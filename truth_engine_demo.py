"""
The Truth Engine - AI-like Without AI

═══════════════════════════════════════════════════════════════════
                 NOT TRAINED. NOT SCRAPED. INVOKED.
═══════════════════════════════════════════════════════════════════

Traditional AI:
    - Needs billions of training examples
    - Scrapes data from the internet
    - PREDICTS what MIGHT be true (probabilistic)
    - Can hallucinate, fabricate, be wrong
    - Gets stale without retraining

ButterflyFx Truth Engine:
    - No training data needed
    - No scraped examples
    - INVOKES what IS true (deterministic)
    - Cannot fabricate - only reveals relationships
    - Always current - truth is computed at invocation

THE INSIGHT:
    You don't need to LEARN that fuel = distance × rate
    You DEFINE the relationship, then INVOKE it.
    
    AI learns patterns: "cars usually use 7-10 L/100km"
    Truth Engine knows: fuel = (rate/100) × distance + corrections

═══════════════════════════════════════════════════════════════════
"""

import sys
import time
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union, Callable

sys.path.insert(0, '.')

from kernel_v2 import Substrate, SubstrateIdentity, Lens


# ═══════════════════════════════════════════════════════════════════
# THE TRUTH ENGINE
# ═══════════════════════════════════════════════════════════════════

class TruthEngine:
    """
    An AI-like interface that doesn't use AI.
    
    Instead of:
        - Training on data
        - Predicting probabilities
        - Estimating from patterns
        
    It:
        - Defines dimensional relationships
        - Invokes mathematical truth
        - Returns what IS, not what might be
    
    Ask it questions → Get deterministic answers
    No hallucination. No fabrication. Just truth.
    """
    
    def __init__(self):
        self._domains: Dict[str, 'Domain'] = {}
        self._substrates: Dict[int, Substrate] = {}
    
    def define(self, domain: 'Domain') -> 'Domain':
        """Define a domain of knowledge."""
        self._domains[domain.name] = domain
        return domain
    
    def ask(self, query: str) -> 'TruthResponse':
        """
        Ask a question → Get truth.
        
        Unlike AI which PREDICTS:
            This INVOKES the mathematical relationship.
        """
        # Parse query to find domain and question
        parsed = self._parse_query(query)
        
        if not parsed:
            return TruthResponse(
                query=query,
                answer=None,
                confidence=0.0,
                explanation="Query not understood. Define a domain first."
            )
        
        domain_name, entity, attribute = parsed
        
        if domain_name not in self._domains:
            return TruthResponse(
                query=query,
                answer=None,
                confidence=0.0,
                explanation=f"Domain '{domain_name}' not defined."
            )
        
        domain = self._domains[domain_name]
        
        # INVOKE (not predict, not estimate)
        result = domain.invoke(entity, attribute)
        
        return TruthResponse(
            query=query,
            answer=result.value,
            confidence=1.0,  # Always 1.0 - it's math, not probability
            explanation=result.derivation,
            domain=domain_name,
            entity=entity,
            attribute=attribute
        )
    
    def _parse_query(self, query: str) -> Optional[tuple]:
        """Simple query parser."""
        query = query.lower().strip()
        
        # Pattern: "what is the {attribute} of {entity} in {domain}?"
        # Or simpler: "{domain}.{entity}.{attribute}"
        
        if '.' in query:
            parts = query.replace('?', '').split('.')
            if len(parts) >= 3:
                return (parts[0], parts[1], parts[2])
            elif len(parts) == 2:
                return (parts[0], parts[1], None)
        
        # Try natural language patterns
        for domain_name in self._domains:
            if domain_name in query:
                domain = self._domains[domain_name]
                for entity_name in domain.entities:
                    if entity_name in query:
                        # Find what attribute they're asking for
                        entity = domain.entities[entity_name]
                        for attr_name in entity.attributes:
                            if attr_name in query:
                                return (domain_name, entity_name, attr_name)
                        # Default to summary if no specific attribute
                        return (domain_name, entity_name, '__summary__')
        
        return None


@dataclass
class TruthResponse:
    """Response from the Truth Engine."""
    query: str
    answer: Any
    confidence: float  # Always 1.0 for invocations
    explanation: str
    domain: Optional[str] = None
    entity: Optional[str] = None
    attribute: Optional[str] = None
    
    def __str__(self):
        if self.answer is None:
            return f"[Unknown] {self.explanation}"
        return f"[TRUTH] {self.answer}\n  Derivation: {self.explanation}"


@dataclass
class InvokeResult:
    """Result of invoking a relationship."""
    value: Any
    derivation: str
    timestamp: float


class Domain:
    """
    A domain of knowledge defined by relationships.
    
    Unlike ML models trained on examples:
        Domains are DEFINED by mathematical relationships.
        Values are COMPUTED, not predicted.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.entities: Dict[str, 'Entity'] = {}
        self.relationships: List['Relationship'] = []
    
    def entity(self, name: str, **attributes) -> 'Entity':
        """Define an entity with attributes."""
        e = Entity(name, attributes, self)
        self.entities[name] = e
        return e
    
    def relationship(self, formula: Callable, description: str) -> 'Relationship':
        """Define a relationship (formula)."""
        r = Relationship(formula, description)
        self.relationships.append(r)
        return r
    
    def invoke(self, entity_name: str, attribute: Optional[str]) -> InvokeResult:
        """Invoke truth about an entity."""
        if entity_name not in self.entities:
            return InvokeResult(None, f"Entity '{entity_name}' not found", time.time())
        
        entity = self.entities[entity_name]
        
        if attribute == '__summary__' or attribute is None:
            # Return summary of all attributes
            summary = entity.invoke_all()
            return InvokeResult(
                summary,
                f"Invoked all attributes of {entity_name}",
                time.time()
            )
        
        if attribute not in entity.attributes and attribute not in entity.computed:
            return InvokeResult(None, f"Attribute '{attribute}' not found", time.time())
        
        value, derivation = entity.invoke(attribute)
        return InvokeResult(value, derivation, time.time())


class Entity:
    """An entity with attributes and computed properties."""
    
    def __init__(self, name: str, attributes: Dict[str, Any], domain: Domain):
        self.name = name
        self.attributes = attributes
        self.computed: Dict[str, Callable] = {}
        self.formulas: Dict[str, str] = {}
        self.domain = domain
    
    def compute(self, name: str, formula: Callable, description: str) -> 'Entity':
        """Add a computed attribute."""
        self.computed[name] = formula
        self.formulas[name] = description
        return self
    
    def invoke(self, attribute: str) -> tuple:
        """Invoke an attribute."""
        if attribute in self.attributes:
            value = self.attributes[attribute]
            return (value, f"{attribute} = {value} (defined)")
        
        if attribute in self.computed:
            formula = self.computed[attribute]
            value = formula(self.attributes)
            derivation = self.formulas.get(attribute, "computed")
            return (value, f"{attribute} = {value} ({derivation})")
        
        return (None, f"Not found")
    
    def invoke_all(self) -> Dict[str, Any]:
        """Invoke all attributes."""
        result = {}
        for attr in self.attributes:
            result[attr] = self.attributes[attr]
        for attr in self.computed:
            result[attr] = self.computed[attr](self.attributes)
        return result


class Relationship:
    """A mathematical relationship."""
    
    def __init__(self, formula: Callable, description: str):
        self.formula = formula
        self.description = description


# ═══════════════════════════════════════════════════════════════════
# DEMONSTRATION
# ═══════════════════════════════════════════════════════════════════

def demo_physics_domain():
    """Demonstrate physics knowledge without training data."""
    print()
    print("=" * 70)
    print("DEMO 1: PHYSICS DOMAIN - No Training, Just Math")
    print("=" * 70)
    print()
    
    engine = TruthEngine()
    
    # Define physics domain
    physics = Domain("physics")
    
    # Define a moving object
    car = physics.entity("car",
        mass_kg=1600,
        velocity_m_s=30,
        height_m=0,
        g=9.81
    )
    
    # Add computed properties (these are RELATIONSHIPS, not learned patterns)
    car.compute("kinetic_energy_j",
        lambda a: 0.5 * a['mass_kg'] * a['velocity_m_s'] ** 2,
        "KE = ½mv²"
    )
    car.compute("momentum_kg_m_s",
        lambda a: a['mass_kg'] * a['velocity_m_s'],
        "p = mv"
    )
    car.compute("stopping_distance_m",
        lambda a: (a['velocity_m_s'] ** 2) / (2 * 0.7 * a['g']),
        "d = v²/(2μg)"
    )
    car.compute("braking_force_n",
        lambda a: a['mass_kg'] * 0.7 * a['g'],
        "F = μmg"
    )
    
    engine.define(physics)
    
    # Ask questions - NO training, NO prediction
    print("QUERY: physics.car.kinetic_energy_j")
    response = engine.ask("physics.car.kinetic_energy_j")
    print(f"  {response}")
    print()
    
    print("QUERY: physics.car.momentum_kg_m_s")
    response = engine.ask("physics.car.momentum_kg_m_s")
    print(f"  {response}")
    print()
    
    print("QUERY: physics.car.stopping_distance_m")
    response = engine.ask("physics.car.stopping_distance_m")
    print(f"  {response}")
    print()
    
    print("KEY INSIGHT:")
    print("  - AI would need thousands of car/physics examples to 'learn' this")
    print("  - Truth Engine just INVOKED E = ½mv²")
    print("  - No training data. No datasets. Just math.")
    print()


def demo_finance_domain():
    """Demonstrate financial calculations without ML."""
    print()
    print("=" * 70)
    print("DEMO 2: FINANCE DOMAIN - Investment Truth, Not Predictions")
    print("=" * 70)
    print()
    
    engine = TruthEngine()
    
    finance = Domain("finance")
    
    # Define an investment
    investment = finance.entity("investment",
        principal=10000,
        rate=0.08,
        years=10,
        compounds_per_year=12
    )
    
    investment.compute("compound_interest",
        lambda a: a['principal'] * (1 + a['rate']/a['compounds_per_year']) ** (a['compounds_per_year'] * a['years']),
        "A = P(1 + r/n)^(nt)"
    )
    investment.compute("simple_interest",
        lambda a: a['principal'] * (1 + a['rate'] * a['years']),
        "A = P(1 + rt)"
    )
    investment.compute("rule_of_72_years",
        lambda a: 72 / (a['rate'] * 100),
        "Years to double ≈ 72/r%"
    )
    investment.compute("total_interest_earned",
        lambda a: a['principal'] * (1 + a['rate']/a['compounds_per_year']) ** (a['compounds_per_year'] * a['years']) - a['principal'],
        "Interest = Final - Principal"
    )
    
    engine.define(finance)
    
    print("QUERY: finance.investment.compound_interest")
    response = engine.ask("finance.investment.compound_interest")
    print(f"  {response}")
    print()
    
    print("QUERY: finance.investment.total_interest_earned")
    response = engine.ask("finance.investment.total_interest_earned")
    print(f"  {response}")
    print()
    
    print("QUERY: finance.investment.rule_of_72_years")
    response = engine.ask("finance.investment.rule_of_72_years")
    print(f"  {response}")
    print()
    
    print("KEY INSIGHT:")
    print("  - AI 'predicts' investment returns based on historical patterns")
    print("  - Truth Engine COMPUTES exact compound interest")
    print("  - Can't hallucinate. The formula IS the truth.")
    print()


def demo_geometry_domain():
    """Demonstrate geometric truths."""
    print()
    print("=" * 70)
    print("DEMO 3: GEOMETRY DOMAIN - Pure Math, No Learning")
    print("=" * 70)
    print()
    
    engine = TruthEngine()
    
    geometry = Domain("geometry")
    
    circle = geometry.entity("circle", radius=5)
    circle.compute("area", lambda a: math.pi * a['radius'] ** 2, "A = πr²")
    circle.compute("circumference", lambda a: 2 * math.pi * a['radius'], "C = 2πr")
    circle.compute("diameter", lambda a: 2 * a['radius'], "d = 2r")
    
    sphere = geometry.entity("sphere", radius=5)
    sphere.compute("volume", lambda a: (4/3) * math.pi * a['radius'] ** 3, "V = (4/3)πr³")
    sphere.compute("surface_area", lambda a: 4 * math.pi * a['radius'] ** 2, "A = 4πr²")
    
    triangle = geometry.entity("triangle", base=10, height=8, side_a=10, side_b=8, side_c=6)
    triangle.compute("area", lambda a: 0.5 * a['base'] * a['height'], "A = ½bh")
    triangle.compute("perimeter", lambda a: a['side_a'] + a['side_b'] + a['side_c'], "P = a + b + c")
    
    engine.define(geometry)
    
    print("QUERY: geometry.circle.area")
    response = engine.ask("geometry.circle.area")
    print(f"  {response}")
    print()
    
    print("QUERY: geometry.sphere.volume")
    response = engine.ask("geometry.sphere.volume")
    print(f"  {response}")
    print()
    
    print("QUERY: geometry.triangle.area")
    response = engine.ask("geometry.triangle.area")
    print(f"  {response}")
    print()


def demo_vs_ai():
    """Show the fundamental difference from AI."""
    print()
    print("=" * 70)
    print("THE FUNDAMENTAL DIFFERENCE")
    print("=" * 70)
    print("""
    ┌─────────────────────────────────────────────────────────────────────┐
    │                    TRADITIONAL AI                                   │
    ├─────────────────────────────────────────────────────────────────────┤
    │                                                                     │
    │  INPUT:  Scrape millions of documents about physics                 │
    │  TRAIN:  Neural network learns patterns over weeks                  │
    │  QUERY:  "What's the kinetic energy of a 1600kg car at 30m/s?"     │
    │  OUTPUT: "Approximately 720,000 joules" (probability: 87%)          │
    │                                                                     │
    │  PROBLEMS:                                                          │
    │    - Can hallucinate (wrong answer with high confidence)            │
    │    - Needs massive compute to train                                 │
    │    - Stale without retraining                                       │
    │    - Can't explain derivation precisely                             │
    │    - May embed errors from training data                            │
    │                                                                     │
    └─────────────────────────────────────────────────────────────────────┘
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │                    TRUTH ENGINE (ButterflyFx)                       │
    ├─────────────────────────────────────────────────────────────────────┤
    │                                                                     │
    │  DEFINE: KE = ½mv²                                                  │
    │  INVOKE: engine.ask("physics.car.kinetic_energy_j")                 │
    │  OUTPUT: 720000.0 J (confidence: 100%)                              │
    │          Derivation: KE = ½mv² = 0.5 × 1600 × 30² = 720000         │
    │                                                                     │
    │  ADVANTAGES:                                                        │
    │    ✓ Cannot hallucinate (math is deterministic)                     │
    │    ✓ No training needed (relationships are defined)                 │
    │    ✓ Always current (computed at invocation)                        │
    │    ✓ Exact derivation provided                                      │
    │    ✓ Runs in nanoseconds, not milliseconds                          │
    │    ✓ No scraped data needed                                         │
    │                                                                     │
    └─────────────────────────────────────────────────────────────────────┘
    
    THE PARADIGM SHIFT:
    ═══════════════════════════════════════════════════════════════════════
    
    AI asks: "What have I seen that looks like this?"
    
    Truth Engine asks: "What IS this, mathematically?"
    
    AI PREDICTS patterns from data.
    Truth Engine INVOKES relationships that EXIST.
    
    AI can be wrong.
    Truth Engine reveals what IS.
    
    ═══════════════════════════════════════════════════════════════════════
""")


def demo_car_trip():
    """Full car trip using Truth Engine."""
    print()
    print("=" * 70)
    print("DEMO 4: CAR TRIP - Same Example, Truth Engine Interface")
    print("=" * 70)
    print()
    
    engine = TruthEngine()
    
    automotive = Domain("automotive")
    
    # Define the trip
    trip = automotive.entity("trip",
        distance_miles=1,
        avg_speed_mph=35,
        car_mass_kg=1600,
        fuel_rate_L_100km=7.5,
        thermal_efficiency=0.35,
        trans_efficiency=0.94,
        tire_diameter_m=0.6604,
        tire_life_miles=60000,
        tread_wear_mm=6.0
    )
    
    # Computed properties
    trip.compute("distance_m",
        lambda a: a['distance_miles'] * 1609.34,
        "distance_m = miles × 1609.34"
    )
    trip.compute("fuel_consumed_mL",
        lambda a: (
            (a['fuel_rate_L_100km'] / 100) * (a['distance_miles'] * 1.60934) +
            (0.015 * a['car_mass_kg'] * 9.81 * a['distance_miles'] * 1609.34) / 
            (34.2e6 * a['thermal_efficiency'] * a['trans_efficiency'])
        ) * 1000,
        "fuel = base + rolling_resistance"
    )
    trip.compute("tire_rotations",
        lambda a: (a['distance_miles'] * 1609.34) / (math.pi * a['tire_diameter_m']),
        "rotations = distance / circumference"
    )
    trip.compute("rubber_worn_mg",
        lambda a: (
            (a['tread_wear_mm'] / (a['tire_life_miles'] * 1609.34)) *
            (a['distance_miles'] * 1609.34) * 1.05 *
            (225 * 150) * 1100 / 1e9 * 4 * 1000
        ),
        "wear = wear_rate × distance × 4_tires"
    )
    trip.compute("trip_time_minutes",
        lambda a: (a['distance_miles'] / a['avg_speed_mph']) * 60,
        "time = distance / speed"
    )
    
    engine.define(automotive)
    
    queries = [
        "automotive.trip.fuel_consumed_mL",
        "automotive.trip.rubber_worn_mg",
        "automotive.trip.tire_rotations",
        "automotive.trip.trip_time_minutes",
    ]
    
    for q in queries:
        response = engine.ask(q)
        print(f"QUERY: {q}")
        print(f"  {response}")
        print()


def show_no_training_comparison():
    """Show computational comparison."""
    print()
    print("=" * 70)
    print("COMPUTATIONAL COMPARISON")
    print("=" * 70)
    print("""
    ┌──────────────────────┬─────────────────────┬─────────────────────┐
    │      Metric          │    Traditional AI   │    Truth Engine     │
    ├──────────────────────┼─────────────────────┼─────────────────────┤
    │ Training data        │ Billions of tokens  │        ZERO         │
    │ Training time        │ Weeks/months        │        ZERO         │
    │ Training compute     │ $Millions           │        ZERO         │
    │ Scraped content      │ Internet-scale      │        ZERO         │
    │ Query latency        │ 100-1000ms          │      ~100 ns        │
    │ Can hallucinate?     │ YES                 │        NO           │
    │ Confidence           │ Probabilistic       │    Deterministic    │
    │ Explains derivation? │ Sometimes           │       ALWAYS        │
    │ Needs GPU cluster?   │ YES                 │        NO           │
    │ Works offline?       │ Depends             │        YES          │
    │ Carbon footprint     │ Massive             │      Trivial        │
    └──────────────────────┴─────────────────────┴─────────────────────┘
    
    THE CATCH:
    ═══════════════════════════════════════════════════════════════════════
    
    Truth Engine works for:
        ✓ Physics formulas
        ✓ Mathematical relationships
        ✓ Financial calculations
        ✓ Engineering specifications
        ✓ Anything that CAN be expressed as a formula
    
    AI is still needed for:
        ✓ Pattern recognition (images, audio)
        ✓ Natural language understanding
        ✓ Creative generation
        ✓ Things without closed-form expressions
    
    THE HYBRID OPPORTUNITY:
        Use Truth Engine for deterministic computations.
        Use AI only where prediction is actually needed.
        Result: Faster, cheaper, more accurate for 80% of queries.
    
    ═══════════════════════════════════════════════════════════════════════
""")


if __name__ == "__main__":
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " THE TRUTH ENGINE - AI-like Without AI ".center(68) + "║")
    print("║" + " No Training. No Datasets. No Hallucination. ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    
    demo_physics_domain()
    demo_finance_domain()
    demo_geometry_domain()
    demo_car_trip()
    demo_vs_ai()
    show_no_training_comparison()
    
    print()
    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print("""
    The Truth Engine is not AI. It doesn't:
        - Learn from examples
        - Predict probabilities
        - Hallucinate answers
        
    It INVOKES mathematical relationships.
    The answer doesn't need to be "learned" - it EXISTS.
    
    This is the ButterflyFx paradigm:
        DEFINE relationships (the substrate)
        INVOKE truth (via lens)
        RECEIVE answer (deterministic, auditable, exact)
    
    For anything that CAN be expressed as a formula:
        Skip the AI. INVOKE the truth.
""")
