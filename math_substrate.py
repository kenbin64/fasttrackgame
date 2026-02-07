"""
Pure Mathematical Substrates

═══════════════════════════════════════════════════════════════════
            SUBSTRATE = MATHEMATICAL EXPRESSION
            LENS = CONTEXT TO EXTRACT VALUES
═══════════════════════════════════════════════════════════════════

A substrate IS a mathematical expression like z = xy

It doesn't have "name" or "domain" as properties.
It IS the relationship itself.

A LENS provides context to extract what EXISTS:
    - Value at a point
    - Slope/derivative
    - Inflection points
    - Angles
    - Intercepts
    - Any property of the mathematical relationship

The values don't need to be computed. They EXIST.
The lens just reveals them.

═══════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
import math
import hashlib
from typing import Callable, Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from kernel_v2 import SubstrateIdentity


def _create_identity(source: str) -> SubstrateIdentity:
    """Create 64-bit identity from source string."""
    h = hashlib.sha256(source.encode()).digest()
    value = int.from_bytes(h[:8], 'big')
    return SubstrateIdentity(value)


# ═══════════════════════════════════════════════════════════════════
# MATHEMATICAL SUBSTRATE
# ═══════════════════════════════════════════════════════════════════

class MathSubstrate:
    """
    A substrate IS a mathematical expression.
    
    Examples:
        z = xy           (product)
        z = x² + y²      (sum of squares)
        y = mx + b       (linear)
        A = πr²          (circle area)
        E = mc²          (energy-mass)
    
    The substrate contains the relationship.
    Lenses reveal what EXISTS within it.
    """
    __slots__ = ('_identity', '_expression', '_variables', '_symbolic')
    
    def __init__(
        self, 
        expression: Callable[..., float],
        variables: Tuple[str, ...],
        symbolic: str = ""
    ):
        """
        Create a mathematical substrate.
        
        Args:
            expression: The mathematical function (the relationship)
            variables: Names of the input variables
            symbolic: Human-readable form (optional, for display)
        """
        # Identity derived from the symbolic expression
        identity_source = symbolic or f"expr({','.join(variables)})"
        object.__setattr__(self, '_identity', _create_identity(identity_source))
        object.__setattr__(self, '_expression', expression)
        object.__setattr__(self, '_variables', variables)
        object.__setattr__(self, '_symbolic', symbolic)
    
    def __setattr__(self, name, value):
        raise TypeError("Substrate is immutable")
    
    @property
    def identity(self) -> SubstrateIdentity:
        return self._identity
    
    @property
    def variables(self) -> Tuple[str, ...]:
        return self._variables
    
    @property
    def symbolic(self) -> str:
        return self._symbolic
    
    def __repr__(self) -> str:
        return f"Substrate({self._symbolic})"


# ═══════════════════════════════════════════════════════════════════
# LENSES - EXTRACT WHAT EXISTS
# ═══════════════════════════════════════════════════════════════════

class Lens:
    """
    A lens provides context to extract values from a substrate.
    
    Lenses reveal what EXISTS:
        - value_at:    The value at a specific point
        - slope:       The derivative at a point
        - inflection:  Where the curve changes direction
        - zeros:       Where the function equals zero
        - angle:       The angle of the tangent line
        - curvature:   How much the curve bends
    """
    
    @staticmethod
    def value_at(substrate: MathSubstrate, **point) -> float:
        """
        The value that EXISTS at this point.
        
        For z = xy, at point (x=3, y=4), z = 12 EXISTS.
        We're not computing it. We're revealing it.
        """
        return substrate._expression(**point)
    
    @staticmethod
    def partial_derivative(
        substrate: MathSubstrate, 
        with_respect_to: str,
        **point
    ) -> float:
        """
        The slope that EXISTS at this point with respect to a variable.
        
        Uses numerical differentiation to reveal the derivative.
        """
        h = 1e-8
        
        # Get values at point and point + h
        point_plus = point.copy()
        point_plus[with_respect_to] = point[with_respect_to] + h
        
        f_at_point = substrate._expression(**point)
        f_at_plus = substrate._expression(**point_plus)
        
        return (f_at_plus - f_at_point) / h
    
    @staticmethod
    def gradient(substrate: MathSubstrate, **point) -> Dict[str, float]:
        """
        The gradient vector that EXISTS at this point.
        
        Returns partial derivatives with respect to all variables.
        """
        return {
            var: Lens.partial_derivative(substrate, var, **point)
            for var in substrate.variables
        }
    
    @staticmethod
    def slope_angle(substrate: MathSubstrate, with_respect_to: str, **point) -> float:
        """
        The angle of the tangent line that EXISTS at this point.
        
        Returns angle in degrees.
        """
        slope = Lens.partial_derivative(substrate, with_respect_to, **point)
        return math.degrees(math.atan(slope))
    
    @staticmethod
    def second_derivative(
        substrate: MathSubstrate,
        with_respect_to: str,
        **point
    ) -> float:
        """
        The curvature that EXISTS at this point.
        
        Second derivative reveals inflection behavior.
        """
        h = 1e-5
        
        point_minus = point.copy()
        point_minus[with_respect_to] = point[with_respect_to] - h
        
        point_plus = point.copy()
        point_plus[with_respect_to] = point[with_respect_to] + h
        
        f_minus = substrate._expression(**point_minus)
        f_at = substrate._expression(**point)
        f_plus = substrate._expression(**point_plus)
        
        return (f_plus - 2*f_at + f_minus) / (h * h)
    
    @staticmethod
    def is_inflection_point(
        substrate: MathSubstrate,
        with_respect_to: str,
        **point
    ) -> bool:
        """
        Whether an inflection point EXISTS at this location.
        
        Inflection occurs where second derivative crosses zero.
        """
        second = Lens.second_derivative(substrate, with_respect_to, **point)
        return abs(second) < 1e-6
    
    @staticmethod
    def curvature(substrate: MathSubstrate, with_respect_to: str, **point) -> float:
        """
        The curvature that EXISTS at this point.
        
        κ = |f''| / (1 + f'²)^(3/2)
        """
        first = Lens.partial_derivative(substrate, with_respect_to, **point)
        second = Lens.second_derivative(substrate, with_respect_to, **point)
        
        return abs(second) / ((1 + first**2) ** 1.5)
    
    @staticmethod
    def find_zero(
        substrate: MathSubstrate,
        variable: str,
        start: float,
        other_vars: Dict[str, float],
        max_iterations: int = 100
    ) -> Optional[float]:
        """
        Find where zero EXISTS (Newton-Raphson).
        
        Seeks the root of the equation.
        """
        x = start
        
        for _ in range(max_iterations):
            point = {variable: x, **other_vars}
            f_val = substrate._expression(**point)
            
            if abs(f_val) < 1e-10:
                return x
            
            f_prime = Lens.partial_derivative(substrate, variable, **point)
            
            if abs(f_prime) < 1e-15:
                break
            
            x = x - f_val / f_prime
        
        return None if abs(substrate._expression(**{variable: x, **other_vars})) > 1e-6 else x


# ═══════════════════════════════════════════════════════════════════
# SUBSTRATE FACTORY - CREATE EXPRESSIONS
# ═══════════════════════════════════════════════════════════════════

def expr(symbolic: str, variables: Tuple[str, ...], fn: Callable[..., float]) -> MathSubstrate:
    """
    Create a mathematical substrate from an expression.
    
    Example:
        z_equals_xy = expr("z = xy", ("x", "y"), lambda x, y: x * y)
    """
    return MathSubstrate(fn, variables, symbolic)


# ═══════════════════════════════════════════════════════════════════
# STANDARD MATHEMATICAL RELATIONSHIPS (They EXIST)
# ═══════════════════════════════════════════════════════════════════

# Algebra
LINEAR = expr("y = mx + b", ("x", "m", "b"), lambda x, m, b: m * x + b)
QUADRATIC = expr("y = ax² + bx + c", ("x", "a", "b", "c"), lambda x, a, b, c: a*x**2 + b*x + c)
CUBIC = expr("y = ax³ + bx² + cx + d", ("x", "a", "b", "c", "d"), 
             lambda x, a, b, c, d: a*x**3 + b*x**2 + c*x + d)
EXPONENTIAL = expr("y = a·eᵇˣ", ("x", "a", "b"), lambda x, a, b: a * math.exp(b * x))
LOGARITHM = expr("y = a·ln(x) + b", ("x", "a", "b"), lambda x, a, b: a * math.log(x) + b if x > 0 else float('nan'))

# Multi-variable
PRODUCT = expr("z = xy", ("x", "y"), lambda x, y: x * y)
SUM_OF_SQUARES = expr("z = x² + y²", ("x", "y"), lambda x, y: x**2 + y**2)
HYPERBOLIC_PARABOLOID = expr("z = x² - y²", ("x", "y"), lambda x, y: x**2 - y**2)
DISTANCE = expr("d = √((x₂-x₁)² + (y₂-y₁)²)", ("x1", "y1", "x2", "y2"),
                lambda x1, y1, x2, y2: math.sqrt((x2-x1)**2 + (y2-y1)**2))

# Geometry
CIRCLE_AREA = expr("A = πr²", ("r",), lambda r: math.pi * r**2)
CIRCLE_CIRCUMFERENCE = expr("C = 2πr", ("r",), lambda r: 2 * math.pi * r)
SPHERE_VOLUME = expr("V = (4/3)πr³", ("r",), lambda r: (4/3) * math.pi * r**3)
TRIANGLE_AREA = expr("A = ½bh", ("b", "h"), lambda b, h: 0.5 * b * h)
PYTHAGOREAN = expr("c = √(a² + b²)", ("a", "b"), lambda a, b: math.sqrt(a**2 + b**2))

# Physics
KINETIC_ENERGY = expr("E = ½mv²", ("m", "v"), lambda m, v: 0.5 * m * v**2)
POTENTIAL_ENERGY = expr("E = mgh", ("m", "g", "h"), lambda m, g, h: m * g * h)
MOMENTUM = expr("p = mv", ("m", "v"), lambda m, v: m * v)
FORCE = expr("F = ma", ("m", "a"), lambda m, a: m * a)
VELOCITY = expr("v = d/t", ("d", "t"), lambda d, t: d / t if t != 0 else float('inf'))
GRAVITATIONAL_FORCE = expr("F = Gm₁m₂/r²", ("m1", "m2", "r", "G"),
                           lambda m1, m2, r, G=6.67430e-11: G * m1 * m2 / (r**2))

# Finance
COMPOUND_INTEREST = expr("A = P(1+r)ⁿ", ("P", "r", "n"), lambda P, r, n: P * ((1 + r) ** n))
SIMPLE_INTEREST = expr("A = P(1+rt)", ("P", "r", "t"), lambda P, r, t: P * (1 + r * t))
PRESENT_VALUE = expr("PV = FV/(1+r)ⁿ", ("FV", "r", "n"), lambda FV, r, n: FV / ((1 + r) ** n))

# Trigonometry
SINE_WAVE = expr("y = A·sin(ωx + φ)", ("x", "A", "omega", "phi"),
                 lambda x, A, omega, phi: A * math.sin(omega * x + phi))
COSINE_WAVE = expr("y = A·cos(ωx + φ)", ("x", "A", "omega", "phi"),
                   lambda x, A, omega, phi: A * math.cos(omega * x + phi))


# ═══════════════════════════════════════════════════════════════════
# MATRIX SUBSTRATE - Values exist at (i, j) positions
# ═══════════════════════════════════════════════════════════════════

class MatrixSubstrate:
    """
    A matrix IS a substrate.
    
    The relationship: value = f(i, j)
    
    You can lift values from any position.
    The lens reveals what EXISTS at (i, j).
    """
    __slots__ = ('_identity', '_generator', '_rows', '_cols', '_symbolic')
    
    def __init__(
        self,
        rows: int,
        cols: int,
        generator: Callable[[int, int], float],
        symbolic: str = ""
    ):
        identity_source = symbolic or f"matrix({rows}x{cols})"
        object.__setattr__(self, '_identity', _create_identity(identity_source))
        object.__setattr__(self, '_generator', generator)
        object.__setattr__(self, '_rows', rows)
        object.__setattr__(self, '_cols', cols)
        object.__setattr__(self, '_symbolic', symbolic)
    
    def __setattr__(self, name, value):
        raise TypeError("Substrate is immutable")
    
    @property
    def shape(self) -> Tuple[int, int]:
        return (self._rows, self._cols)
    
    @property
    def symbolic(self) -> str:
        return self._symbolic


class MatrixLens:
    """Lenses to extract what EXISTS in a matrix."""
    
    @staticmethod
    def at(matrix: MatrixSubstrate, i: int, j: int) -> float:
        """The value that EXISTS at position (i, j)."""
        return matrix._generator(i, j)
    
    @staticmethod
    def row(matrix: MatrixSubstrate, i: int) -> List[float]:
        """The entire row that EXISTS at index i."""
        return [matrix._generator(i, j) for j in range(matrix._cols)]
    
    @staticmethod
    def col(matrix: MatrixSubstrate, j: int) -> List[float]:
        """The entire column that EXISTS at index j."""
        return [matrix._generator(i, j) for i in range(matrix._rows)]
    
    @staticmethod
    def diagonal(matrix: MatrixSubstrate) -> List[float]:
        """The diagonal that EXISTS."""
        n = min(matrix._rows, matrix._cols)
        return [matrix._generator(i, i) for i in range(n)]
    
    @staticmethod
    def trace(matrix: MatrixSubstrate) -> float:
        """The trace (sum of diagonal) that EXISTS."""
        return sum(MatrixLens.diagonal(matrix))
    
    @staticmethod
    def submatrix(matrix: MatrixSubstrate, r1: int, r2: int, c1: int, c2: int) -> List[List[float]]:
        """A submatrix region that EXISTS."""
        return [
            [matrix._generator(i, j) for j in range(c1, c2)]
            for i in range(r1, r2)
        ]
    
    @staticmethod
    def to_list(matrix: MatrixSubstrate) -> List[List[float]]:
        """Materialize the entire matrix (all values that EXIST)."""
        return [
            [matrix._generator(i, j) for j in range(matrix._cols)]
            for i in range(matrix._rows)
        ]


def matrix(rows: int, cols: int, gen: Callable[[int, int], float], symbolic: str = "") -> MatrixSubstrate:
    """Create a matrix substrate."""
    return MatrixSubstrate(rows, cols, gen, symbolic)


# ═══════════════════════════════════════════════════════════════════
# GRID SUBSTRATE - Properties exist at (x, y, z) coordinates
# ═══════════════════════════════════════════════════════════════════

class GridSubstrate:
    """
    A grid IS a substrate.
    
    The relationship: property = f(x, y) or f(x, y, z)
    
    Values exist at every coordinate.
    The lens reveals what EXISTS at any point.
    """
    __slots__ = ('_identity', '_field', '_dimensions', '_symbolic')
    
    def __init__(
        self,
        field: Callable[..., float],
        dimensions: int,
        symbolic: str = ""
    ):
        identity_source = symbolic or f"grid({dimensions}D)"
        object.__setattr__(self, '_identity', _create_identity(identity_source))
        object.__setattr__(self, '_field', field)
        object.__setattr__(self, '_dimensions', dimensions)
        object.__setattr__(self, '_symbolic', symbolic)
    
    def __setattr__(self, name, value):
        raise TypeError("Substrate is immutable")


class GridLens:
    """Lenses to extract what EXISTS in a grid."""
    
    @staticmethod
    def at(grid: GridSubstrate, *coords) -> float:
        """The value that EXISTS at these coordinates."""
        return grid._field(*coords)
    
    @staticmethod
    def sample_line(grid: GridSubstrate, start: Tuple, end: Tuple, samples: int = 10) -> List[float]:
        """Sample values along a line through the grid."""
        results = []
        for t in [i / (samples - 1) for i in range(samples)]:
            point = tuple(s + t * (e - s) for s, e in zip(start, end))
            results.append(grid._field(*point))
        return results
    
    @staticmethod
    def gradient_at(grid: GridSubstrate, *coords, h: float = 1e-6) -> Tuple[float, ...]:
        """The gradient vector that EXISTS at these coordinates."""
        grads = []
        base = grid._field(*coords)
        for i in range(len(coords)):
            shifted = list(coords)
            shifted[i] += h
            grads.append((grid._field(*shifted) - base) / h)
        return tuple(grads)
    
    @staticmethod
    def magnitude_at(grid: GridSubstrate, *coords) -> float:
        """Magnitude of gradient at this point."""
        grad = GridLens.gradient_at(grid, *coords)
        return math.sqrt(sum(g**2 for g in grad))


def grid2d(field: Callable[[float, float], float], symbolic: str = "") -> GridSubstrate:
    """Create a 2D grid substrate."""
    return GridSubstrate(field, 2, symbolic)

def grid3d(field: Callable[[float, float, float], float], symbolic: str = "") -> GridSubstrate:
    """Create a 3D grid substrate."""
    return GridSubstrate(field, 3, symbolic)


# ═══════════════════════════════════════════════════════════════════
# SPECTRUM SUBSTRATE - Amplitudes exist at frequencies
# ═══════════════════════════════════════════════════════════════════

class SpectrumSubstrate:
    """
    A spectrum IS a substrate.
    
    The relationship: amplitude = f(frequency)
    
    Every frequency has an amplitude.
    The lens reveals what EXISTS at any frequency.
    """
    __slots__ = ('_identity', '_amplitude_fn', '_symbolic')
    
    def __init__(
        self,
        amplitude_fn: Callable[[float], float],
        symbolic: str = ""
    ):
        identity_source = symbolic or "spectrum"
        object.__setattr__(self, '_identity', _create_identity(identity_source))
        object.__setattr__(self, '_amplitude_fn', amplitude_fn)
        object.__setattr__(self, '_symbolic', symbolic)
    
    def __setattr__(self, name, value):
        raise TypeError("Substrate is immutable")


class SpectrumLens:
    """Lenses to extract what EXISTS in a spectrum."""
    
    @staticmethod
    def amplitude_at(spectrum: SpectrumSubstrate, frequency: float) -> float:
        """The amplitude that EXISTS at this frequency."""
        return spectrum._amplitude_fn(frequency)
    
    @staticmethod
    def power_at(spectrum: SpectrumSubstrate, frequency: float) -> float:
        """The power (amplitude²) that EXISTS at this frequency."""
        amp = spectrum._amplitude_fn(frequency)
        return amp * amp
    
    @staticmethod
    def band(spectrum: SpectrumSubstrate, f_low: float, f_high: float, samples: int = 100) -> List[Tuple[float, float]]:
        """Sample the spectrum across a frequency band."""
        step = (f_high - f_low) / (samples - 1)
        return [
            (f_low + i * step, spectrum._amplitude_fn(f_low + i * step))
            for i in range(samples)
        ]
    
    @staticmethod
    def peak_in_band(spectrum: SpectrumSubstrate, f_low: float, f_high: float, samples: int = 100) -> Tuple[float, float]:
        """Find the peak frequency and amplitude in a band."""
        band_data = SpectrumLens.band(spectrum, f_low, f_high, samples)
        return max(band_data, key=lambda x: x[1])
    
    @staticmethod
    def total_power(spectrum: SpectrumSubstrate, f_low: float, f_high: float, samples: int = 100) -> float:
        """Total power in a frequency band (integration)."""
        band_data = SpectrumLens.band(spectrum, f_low, f_high, samples)
        step = (f_high - f_low) / (samples - 1)
        return sum(amp**2 for _, amp in band_data) * step


def spectrum(amplitude_fn: Callable[[float], float], symbolic: str = "") -> SpectrumSubstrate:
    """Create a spectrum substrate."""
    return SpectrumSubstrate(amplitude_fn, symbolic)


# ═══════════════════════════════════════════════════════════════════
# STRATUM SUBSTRATE - Layers exist at depth levels
# ═══════════════════════════════════════════════════════════════════

class StratumSubstrate:
    """
    A stratum IS a substrate.
    
    The relationship: layer_properties = f(depth)
    
    Every depth has properties.
    The lens reveals what EXISTS at any depth.
    """
    __slots__ = ('_identity', '_layer_fn', '_property_names', '_symbolic')
    
    def __init__(
        self,
        layer_fn: Callable[[float], Dict[str, float]],
        property_names: Tuple[str, ...],
        symbolic: str = ""
    ):
        identity_source = symbolic or f"stratum({','.join(property_names)})"
        object.__setattr__(self, '_identity', _create_identity(identity_source))
        object.__setattr__(self, '_layer_fn', layer_fn)
        object.__setattr__(self, '_property_names', property_names)
        object.__setattr__(self, '_symbolic', symbolic)
    
    def __setattr__(self, name, value):
        raise TypeError("Substrate is immutable")


class StratumLens:
    """Lenses to extract what EXISTS in a stratum."""
    
    @staticmethod
    def at_depth(stratum: StratumSubstrate, depth: float) -> Dict[str, float]:
        """All properties that EXIST at this depth."""
        return stratum._layer_fn(depth)
    
    @staticmethod
    def property_at(stratum: StratumSubstrate, depth: float, property_name: str) -> float:
        """A specific property that EXISTS at this depth."""
        return stratum._layer_fn(depth).get(property_name, 0.0)
    
    @staticmethod
    def profile(stratum: StratumSubstrate, property_name: str, 
                depth_min: float, depth_max: float, samples: int = 20) -> List[Tuple[float, float]]:
        """Profile a property across depths."""
        step = (depth_max - depth_min) / (samples - 1)
        return [
            (depth_min + i * step, stratum._layer_fn(depth_min + i * step).get(property_name, 0.0))
            for i in range(samples)
        ]
    
    @staticmethod
    def find_layer(stratum: StratumSubstrate, property_name: str, target_value: float,
                   depth_min: float, depth_max: float, tolerance: float = 0.01) -> Optional[float]:
        """Find depth where a property reaches a target value."""
        for depth in [depth_min + i * 0.1 for i in range(int((depth_max - depth_min) / 0.1) + 1)]:
            value = stratum._layer_fn(depth).get(property_name, 0.0)
            if abs(value - target_value) < tolerance:
                return depth
        return None


def stratum(layer_fn: Callable[[float], Dict[str, float]], 
            properties: Tuple[str, ...], 
            symbolic: str = "") -> StratumSubstrate:
    """Create a stratum substrate."""
    return StratumSubstrate(layer_fn, properties, symbolic)


# ═══════════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════════

def demo():
    """Demonstrate pure mathematical substrates with lenses."""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║              PURE MATHEMATICAL SUBSTRATES                          ║
║         Substrate = Expression. Lens = Context.                    ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    # ═══════════════════════════════════════════════════════════════
    # Example 1: z = xy
    # ═══════════════════════════════════════════════════════════════
    
    print("SUBSTRATE: z = xy")
    print("─" * 60)
    
    z_xy = PRODUCT
    
    # Value at a point
    value = Lens.value_at(z_xy, x=3, y=4)
    print(f"  Value at (x=3, y=4):  z = {value}")
    print(f"    → This value EXISTS. We revealed it.\n")
    
    # Partial derivatives (slopes)
    dz_dx = Lens.partial_derivative(z_xy, "x", x=3, y=4)
    dz_dy = Lens.partial_derivative(z_xy, "y", x=3, y=4)
    print(f"  Slope with respect to x:  ∂z/∂x = {dz_dx:.4f}")
    print(f"  Slope with respect to y:  ∂z/∂y = {dz_dy:.4f}")
    print(f"    → These slopes EXIST at this point.\n")
    
    # Gradient
    grad = Lens.gradient(z_xy, x=3, y=4)
    print(f"  Gradient: ∇z = {grad}")
    print(f"    → The direction of steepest ascent EXISTS.\n")
    
    # ═══════════════════════════════════════════════════════════════
    # Example 2: Matrix - Identity matrix
    # ═══════════════════════════════════════════════════════════════
    
    print("\nSUBSTRATE: Identity Matrix (4x4)")
    print("─" * 60)
    
    identity_matrix = matrix(4, 4, lambda i, j: 1.0 if i == j else 0.0, "I₄")
    
    print(f"  Full matrix that EXISTS:")
    for row in MatrixLens.to_list(identity_matrix):
        print(f"    {row}")
    
    print(f"\n  Value at (1, 1): {MatrixLens.at(identity_matrix, 1, 1)}")
    print(f"  Value at (1, 2): {MatrixLens.at(identity_matrix, 1, 2)}")
    print(f"  Diagonal: {MatrixLens.diagonal(identity_matrix)}")
    print(f"  Trace: {MatrixLens.trace(identity_matrix)}")
    print(f"    → All these values EXISTED. We lifted them.\n")
    
    # ═══════════════════════════════════════════════════════════════
    # Example 3: Matrix - Multiplication table
    # ═══════════════════════════════════════════════════════════════
    
    print("\nSUBSTRATE: Multiplication Table (10x10)")
    print("─" * 60)
    
    mult_table = matrix(10, 10, lambda i, j: (i+1) * (j+1), "mult")
    
    print(f"  7 × 8 = {MatrixLens.at(mult_table, 6, 7)}")
    print(f"  9 × 9 = {MatrixLens.at(mult_table, 8, 8)}")
    print(f"  Row 5 (the 5× table): {MatrixLens.row(mult_table, 4)}")
    print(f"    → These products EXIST in the multiplication relationship.\n")
    
    # ═══════════════════════════════════════════════════════════════
    # Example 4: Grid - Temperature field
    # ═══════════════════════════════════════════════════════════════
    
    print("\nSUBSTRATE: Temperature Field T(x,y)")
    print("─" * 60)
    
    # Temperature decreases from center (100) outward
    temp_field = grid2d(
        lambda x, y: 100 * math.exp(-(x**2 + y**2) / 50),
        "T = 100·e^(-(x²+y²)/50)"
    )
    
    print(f"  Temperature at origin (0, 0): {GridLens.at(temp_field, 0, 0):.2f}°")
    print(f"  Temperature at (3, 4): {GridLens.at(temp_field, 3, 4):.2f}°")
    print(f"  Temperature at (5, 5): {GridLens.at(temp_field, 5, 5):.2f}°")
    
    grad = GridLens.gradient_at(temp_field, 3, 4)
    print(f"\n  Gradient at (3, 4): ({grad[0]:.4f}, {grad[1]:.4f})")
    print(f"  Gradient magnitude: {GridLens.magnitude_at(temp_field, 3, 4):.4f}")
    print(f"    → Heat flows from hot to cold. The gradient EXISTS.\n")
    
    # Sample along a line
    print(f"  Temperature along x-axis (y=0):")
    line_temps = GridLens.sample_line(temp_field, (0, 0), (10, 0), 6)
    for i, temp in enumerate(line_temps):
        print(f"    x={i*2}: {temp:.2f}°")
    
    # ═══════════════════════════════════════════════════════════════
    # Example 5: Spectrum - Audio frequencies
    # ═══════════════════════════════════════════════════════════════
    
    print("\n\nSUBSTRATE: Audio Spectrum")
    print("─" * 60)
    
    # A spectrum with peaks at 440Hz (A4) and 880Hz (A5)
    audio_spectrum = spectrum(
        lambda f: (
            math.exp(-((f - 440) / 20)**2) +  # A4 peak
            0.5 * math.exp(-((f - 880) / 30)**2)  # A5 harmonic
        ),
        "A4 with harmonic"
    )
    
    print(f"  Amplitude at 440 Hz (A4): {SpectrumLens.amplitude_at(audio_spectrum, 440):.4f}")
    print(f"  Amplitude at 880 Hz (A5): {SpectrumLens.amplitude_at(audio_spectrum, 880):.4f}")
    print(f"  Amplitude at 600 Hz: {SpectrumLens.amplitude_at(audio_spectrum, 600):.4f}")
    
    peak = SpectrumLens.peak_in_band(audio_spectrum, 400, 500, 50)
    print(f"\n  Peak in 400-500 Hz band: {peak[0]:.1f} Hz at amplitude {peak[1]:.4f}")
    
    power = SpectrumLens.total_power(audio_spectrum, 200, 1000)
    print(f"  Total power in 200-1000 Hz: {power:.4f}")
    print(f"    → These spectral properties EXIST.\n")
    
    # ═══════════════════════════════════════════════════════════════
    # Example 6: Stratum - Earth layers
    # ═══════════════════════════════════════════════════════════════
    
    print("\nSUBSTRATE: Earth Stratum")
    print("─" * 60)
    
    def earth_layers(depth_km: float) -> Dict[str, float]:
        """Properties at different depths in Earth."""
        if depth_km < 35:  # Crust
            return {"temperature": 20 + depth_km * 25, "density": 2.7, "pressure": depth_km * 30}
        elif depth_km < 2900:  # Mantle
            return {"temperature": 900 + (depth_km - 35) * 0.5, "density": 4.5, "pressure": depth_km * 33}
        else:  # Core
            return {"temperature": 4000 + (depth_km - 2900) * 0.8, "density": 10.0, "pressure": depth_km * 35}
    
    earth = stratum(earth_layers, ("temperature", "density", "pressure"), "Earth")
    
    print(f"  At 10 km (crust): {StratumLens.at_depth(earth, 10)}")
    print(f"  At 100 km (upper mantle): {StratumLens.at_depth(earth, 100)}")
    print(f"  At 3000 km (outer core): {StratumLens.at_depth(earth, 3000)}")
    
    print(f"\n  Temperature profile (0-100 km):")
    profile = StratumLens.profile(earth, "temperature", 0, 100, 5)
    for depth, temp in profile:
        print(f"    {depth:.0f} km: {temp:.0f}°C")
    
    print(f"    → These geological properties EXIST at each depth.\n")
    
    # ═══════════════════════════════════════════════════════════════
    
    print("""
═══════════════════════════════════════════════════════════════════

KEY INSIGHT:

    SUBSTRATE = Mathematical relationship
        - Expression: z = xy
        - Matrix:     value = f(i, j)
        - Grid:       property = f(x, y, z)
        - Spectrum:   amplitude = f(frequency)
        - Stratum:    layer = f(depth)
    
    LENS = Context to extract what EXISTS
        - Values at points
        - Derivatives, gradients
        - Peaks, zeros
        - Profiles, slices
        - Any mathematical property
    
    Nothing is computed. Everything REVEALED.

═══════════════════════════════════════════════════════════════════
""")


if __name__ == "__main__":
    demo()
