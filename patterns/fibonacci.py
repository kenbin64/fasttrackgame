"""
Fibonacci Pattern - Recursive Substrate Generation

The Fibonacci Pattern creates substrates that follow the Fibonacci spiral:
- Recursive generation following f(n) = f(n-1) + f(n-2)
- Spiral geometry for dimensional navigation
- Golden Ratio convergence
- Substrate sequences following natural growth patterns

CHARTER COMPLIANCE:
✅ Principle 1: Returns references, not copies
✅ Principle 2: Passive until invoked
✅ Principle 3: Immutable at runtime
✅ Principle 5: Pure functions only
✅ Principle 7: Fibonacci-bounded growth (by definition)

LAW ALIGNMENT:
- Law 1: Division follows Fibonacci spiral
- Law 3: Every division inherits the whole (recursive pattern)
- Law 7: Return to unity (spiral converges to φ)
"""

from __future__ import annotations
from typing import List, Callable
from kernel.substrate import Substrate, SubstrateIdentity
from kernel import fibonacci as fib_module


class FibonacciGenerator:
    """
    Generator for creating substrates following Fibonacci patterns.
    
    This pattern encapsulates recursive substrate generation where each
    substrate's value depends on previous substrates in the sequence.
    """
    __slots__ = ('_seed_fn',)
    
    def __init__(self, seed_fn: Callable[[int], int] = None):
        """
        Create Fibonacci generator.
        
        Args:
            seed_fn: Optional function to generate seed values
                    Default: standard Fibonacci sequence
        
        Example:
            gen = FibonacciGenerator()
            substrate = gen.create_fibonacci_substrate(10)
        """
        if seed_fn is None:
            seed_fn = fib_module.fibonacci
        object.__setattr__(self, '_seed_fn', seed_fn)
    
    def __setattr__(self, name, value):
        raise TypeError("FibonacciGenerator is immutable")
    
    def create_fibonacci_substrate(self, n: int) -> Substrate:
        """
        Create substrate that generates nth Fibonacci number.
        
        Args:
            n: Index in Fibonacci sequence
        
        Returns:
            Substrate with Fibonacci expression
        
        Example:
            gen = FibonacciGenerator()
            s = gen.create_fibonacci_substrate(10)
            assert s.invoke() == 55
        """
        identity_value = hash(f"fibonacci({n})") & 0xFFFFFFFFFFFFFFFF
        identity = SubstrateIdentity(identity_value)
        expression = lambda: self._seed_fn(n) & 0xFFFFFFFFFFFFFFFF
        
        return Substrate(identity, expression)
    
    def create_fibonacci_sequence(self, count: int) -> List[Substrate]:
        """
        Create sequence of Fibonacci substrates.
        
        Args:
            count: Number of substrates to generate
        
        Returns:
            List of substrates, each encoding a Fibonacci number
        
        Example:
            gen = FibonacciGenerator()
            seq = gen.create_fibonacci_sequence(9)
            values = [s.invoke() for s in seq]
            # [0, 1, 1, 2, 3, 5, 8, 13, 21]
        """
        return [self.create_fibonacci_substrate(i) for i in range(count)]
    
    def fibonacci_spiral_substrate(self, n: int) -> Substrate:
        """
        Create substrate following spiral geometry.
        
        The substrate encodes both the Fibonacci value and spiral coordinates.
        
        Args:
            n: Division index in spiral
        
        Returns:
            Substrate with spiral expression
        
        Example:
            gen = FibonacciGenerator()
            s = gen.fibonacci_spiral_substrate(5)
            # Substrate encodes position on Fibonacci spiral
        """
        identity_value = hash(f"spiral({n})") & 0xFFFFFFFFFFFFFFFF
        identity = SubstrateIdentity(identity_value)
        
        def spiral_expression(**kwargs):
            attr = kwargs.get('attribute', 'value')
            if attr == 'value':
                return self._seed_fn(n) & 0xFFFFFFFFFFFFFFFF
            elif attr == 'angle':
                return int(fib_module.spiral_angle(n) * 1000) & 0xFFFFFFFFFFFFFFFF
            elif attr == 'radius':
                return int(fib_module.spiral_radius(n) * 1000) & 0xFFFFFFFFFFFFFFFF
            elif attr == 'x':
                x, _ = fib_module.spiral_coordinates(n)
                return int(x * 1000) & 0xFFFFFFFFFFFFFFFF
            elif attr == 'y':
                _, y = fib_module.spiral_coordinates(n)
                return int(y * 1000) & 0xFFFFFFFFFFFFFFFF
            else:
                return self._seed_fn(n) & 0xFFFFFFFFFFFFFFFF
        
        return Substrate(identity, spiral_expression)


# Convenience functions

def create_fibonacci_substrate(n: int) -> Substrate:
    """
    Create substrate for nth Fibonacci number.
    
    Args:
        n: Index in Fibonacci sequence
    
    Returns:
        Substrate encoding fibonacci(n)
    """
    gen = FibonacciGenerator()
    return gen.create_fibonacci_substrate(n)


def create_fibonacci_sequence(count: int) -> List[Substrate]:
    """
    Create sequence of Fibonacci substrates.
    
    Args:
        count: Number of substrates
    
    Returns:
        List of Fibonacci substrates
    """
    gen = FibonacciGenerator()
    return gen.create_fibonacci_sequence(count)

