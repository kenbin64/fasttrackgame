"""
Manifold-Dimensional Integration

The manifold z = xy demonstrates:
- INTRINSIC dimension: 2D (the surface itself)
- EMBEDDING dimension: 3D (the space it lives in)

A 2D square warped into 3D = the saddle surface (hyperbolic paraboloid)

This is the bridge between Fibonacci levels:
- Level 4 (PLANE, F=5): The 2D surface intrinsically
- Level 5 (VOLUME, F=8): The 3D space it's embedded in

The manifold is HOW dimensions nest:
z = xy means every point on the 2D surface
has a deterministic position in 3D space.

The mapping function IS the dimensional relationship.
"""

import math
import numpy as np
from typing import Tuple, List, Dict, Any, Callable
from dataclasses import dataclass, field


@dataclass
class ManifoldPoint:
    """
    A point that exists in multiple dimensional representations.
    
    intrinsic: (x, y) - 2D surface coordinates
    embedded: (x, y, z) - 3D space coordinates
    
    The manifold function maps intrinsic → embedded
    """
    # Intrinsic coordinates (on the surface)
    u: float  # First surface parameter
    v: float  # Second surface parameter
    
    # Embedded coordinates (in 3D space)
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    # The manifold that defines the embedding
    manifold_type: str = "saddle"  # z = xy
    
    def __post_init__(self):
        """Compute embedded coordinates from intrinsic"""
        self.x, self.y, self.z = self.embed()
    
    def embed(self) -> Tuple[float, float, float]:
        """
        Map intrinsic (u, v) to embedded (x, y, z) via the manifold function.
        """
        if self.manifold_type == "saddle":
            # z = xy (hyperbolic paraboloid / saddle)
            x = self.u
            y = self.v
            z = self.u * self.v
            return (x, y, z)
        
        elif self.manifold_type == "sphere":
            # Sphere: intrinsic (θ, φ) → embedded (x, y, z)
            theta = self.u * math.pi  # 0 to π
            phi = self.v * 2 * math.pi  # 0 to 2π
            x = math.sin(theta) * math.cos(phi)
            y = math.sin(theta) * math.sin(phi)
            z = math.cos(theta)
            return (x, y, z)
        
        elif self.manifold_type == "torus":
            # Torus: intrinsic (u, v) → embedded (x, y, z)
            R, r = 2.0, 0.5  # Major and minor radii
            u_rad = self.u * 2 * math.pi
            v_rad = self.v * 2 * math.pi
            x = (R + r * math.cos(v_rad)) * math.cos(u_rad)
            y = (R + r * math.cos(v_rad)) * math.sin(u_rad)
            z = r * math.sin(v_rad)
            return (x, y, z)
        
        elif self.manifold_type == "mobius":
            # Möbius strip: 2D with a twist
            u_rad = self.u * 2 * math.pi
            v_centered = self.v - 0.5  # -0.5 to 0.5
            x = (1 + v_centered * math.cos(u_rad / 2)) * math.cos(u_rad)
            y = (1 + v_centered * math.cos(u_rad / 2)) * math.sin(u_rad)
            z = v_centered * math.sin(u_rad / 2)
            return (x, y, z)
        
        elif self.manifold_type == "klein":
            # Klein bottle (immersion in 3D)
            u_rad = self.u * 2 * math.pi
            v_rad = self.v * 2 * math.pi
            r = 4 * (1 - math.cos(u_rad) / 2)
            x = 6 * math.cos(u_rad) * (1 + math.sin(u_rad)) + r * math.cos(u_rad) * math.cos(v_rad)
            y = 16 * math.sin(u_rad) + r * math.sin(u_rad) * math.cos(v_rad)
            z = r * math.sin(v_rad)
            return (x * 0.1, y * 0.1, z * 0.1)  # Scale down
        
        else:
            # Default: flat plane z = 0
            return (self.u, self.v, 0.0)
    
    @property
    def intrinsic_address(self) -> str:
        """Address in intrinsic (surface) coordinates"""
        return f"σ({self.u:.3f},{self.v:.3f})"
    
    @property
    def embedded_address(self) -> str:
        """Address in embedded (3D) coordinates"""
        return f"ξ({self.x:.3f},{self.y:.3f},{self.z:.3f})"
    
    def to_dict(self) -> dict:
        return {
            "intrinsic": {"u": self.u, "v": self.v},
            "embedded": {"x": self.x, "y": self.y, "z": self.z},
            "manifold": self.manifold_type,
            "intrinsic_address": self.intrinsic_address,
            "embedded_address": self.embedded_address
        }


@dataclass
class DimensionalManifold:
    """
    A manifold that bridges dimensional levels.
    
    The manifold is the RELATIONSHIP between dimensions:
    - Intrinsic dimension: The surface's own dimension (2D for z=xy)
    - Embedding dimension: The space it lives in (3D for z=xy)
    
    z = xy is a 2D surface (PLANE level) embedded in 3D (VOLUME level)
    
    This IS dimensional programming:
    - The 2D grid is your data structure
    - The 3D embedding is the visualization/interaction
    - The mapping function is the transformation
    """
    name: str
    manifold_type: str  # saddle, sphere, torus, mobius, klein
    intrinsic_dim: int  # Dimension of the surface itself
    embedding_dim: int  # Dimension of the space it lives in
    
    # Grid of points on the manifold
    _points: Dict[Tuple[float, float], ManifoldPoint] = field(default_factory=dict)
    
    @property
    def description(self) -> str:
        descriptions = {
            "saddle": "z = xy (hyperbolic paraboloid) - 2D square warped to 3D saddle",
            "sphere": "2-sphere - 2D surface in 3D, constant curvature",
            "torus": "Torus - 2D surface, product of two circles",
            "mobius": "Möbius strip - 2D with a twist, single-sided",
            "klein": "Klein bottle - 2D, no inside/outside distinction"
        }
        return descriptions.get(self.manifold_type, "Custom manifold")
    
    @property
    def equation(self) -> str:
        equations = {
            "saddle": "z = x·y",
            "sphere": "x² + y² + z² = 1",
            "torus": "(√(x²+y²) - R)² + z² = r²",
            "mobius": "Parametric twist embedding",
            "klein": "4D surface immersed in 3D"
        }
        return equations.get(self.manifold_type, "Custom")
    
    def sample(self, u: float, v: float) -> ManifoldPoint:
        """
        Sample a point on the manifold.
        Creates the point (invokes it from potential).
        """
        key = (round(u, 6), round(v, 6))
        
        if key not in self._points:
            point = ManifoldPoint(u=u, v=v, manifold_type=self.manifold_type)
            self._points[key] = point
        
        return self._points[key]
    
    def generate_grid(self, resolution: int = 20) -> List[ManifoldPoint]:
        """
        Generate a grid of points on the manifold.
        """
        points = []
        for i in range(resolution + 1):
            for j in range(resolution + 1):
                u = i / resolution
                v = j / resolution
                point = self.sample(u, v)
                points.append(point)
        return points
    
    def to_mesh(self, resolution: int = 20) -> dict:
        """
        Generate a mesh representation for 3D rendering.
        Returns vertices and faces for Three.js.
        """
        vertices = []
        uvs = []
        
        # Generate vertices
        for i in range(resolution + 1):
            for j in range(resolution + 1):
                u = (i / resolution - 0.5) * 2  # -1 to 1 for saddle
                v = (j / resolution - 0.5) * 2
                
                if self.manifold_type == "saddle":
                    x, y, z = u, v, u * v
                else:
                    # Use normalized 0-1 for other manifolds
                    u_norm = i / resolution
                    v_norm = j / resolution
                    point = ManifoldPoint(u=u_norm, v=v_norm, manifold_type=self.manifold_type)
                    x, y, z = point.x, point.y, point.z
                
                vertices.extend([x, y, z])
                uvs.extend([i / resolution, j / resolution])
        
        # Generate face indices
        indices = []
        for i in range(resolution):
            for j in range(resolution):
                a = i * (resolution + 1) + j
                b = a + 1
                c = a + (resolution + 1)
                d = c + 1
                
                # Two triangles per quad
                indices.extend([a, b, c])
                indices.extend([b, d, c])
        
        return {
            "vertices": vertices,
            "uvs": uvs,
            "indices": indices,
            "resolution": resolution,
            "vertex_count": len(vertices) // 3,
            "face_count": len(indices) // 3
        }
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.manifold_type,
            "equation": self.equation,
            "description": self.description,
            "intrinsic_dimension": self.intrinsic_dim,
            "embedding_dimension": self.embedding_dim,
            "points_sampled": len(self._points),
            "dimensional_relationship": f"{self.intrinsic_dim}D surface in {self.embedding_dim}D space"
        }


class ManifoldDimensionalBridge:
    """
    The bridge between Fibonacci levels via manifolds.
    
    Manifolds show HOW lower dimensions embed in higher ones:
    - A 2D manifold (PLANE level) embeds in 3D (VOLUME level)
    - The embedding function IS the dimensional relationship
    
    z = xy demonstrates:
    - (x, y) is the intrinsic 2D address
    - (x, y, z) is the embedded 3D position
    - z = xy is the TRANSFORMATION between dimensional levels
    """
    
    FIBONACCI_MANIFOLDS = {
        # Level 4 (PLANE) → Level 5 (VOLUME) examples
        "saddle": {
            "from_level": 4,  # PLANE
            "to_level": 5,    # VOLUME
            "equation": "z = xy",
            "meaning": "2D square warped into 3D saddle"
        },
        "sphere": {
            "from_level": 4,
            "to_level": 5,
            "equation": "x² + y² + z² = 1",
            "meaning": "2D surface of constant positive curvature"
        },
        "torus": {
            "from_level": 4,
            "to_level": 5,
            "equation": "(R + r·cos(v))·cos(u), (R + r·cos(v))·sin(u), r·sin(v)",
            "meaning": "2D surface, product topology"
        },
        # More exotic
        "mobius": {
            "from_level": 4,
            "to_level": 5,
            "equation": "Twisted embedding",
            "meaning": "Non-orientable 2D surface"
        },
        "klein": {
            "from_level": 4,
            "to_level": 5,  # Actually needs 4D, immersed in 3D
            "equation": "Self-intersecting immersion",
            "meaning": "2D surface with no inside/outside"
        }
    }
    
    def __init__(self):
        self.manifolds: Dict[str, DimensionalManifold] = {}
        self._create_standard_manifolds()
    
    def _create_standard_manifolds(self):
        """Create the standard dimensional manifolds"""
        for name, info in self.FIBONACCI_MANIFOLDS.items():
            manifold = DimensionalManifold(
                name=f"{name.title()} Manifold",
                manifold_type=name,
                intrinsic_dim=2,
                embedding_dim=3
            )
            self.manifolds[name] = manifold
    
    def get(self, name: str) -> DimensionalManifold:
        """Get a manifold by name"""
        return self.manifolds.get(name)
    
    def sample_point(self, manifold_name: str, u: float, v: float) -> dict:
        """
        Sample a point on a manifold.
        Shows the dimensional transformation in action.
        """
        manifold = self.manifolds.get(manifold_name)
        if not manifold:
            return {"error": f"Unknown manifold: {manifold_name}"}
        
        point = manifold.sample(u, v)
        
        return {
            "manifold": manifold_name,
            "intrinsic": {"u": u, "v": v, "address": point.intrinsic_address},
            "embedded": {"x": point.x, "y": point.y, "z": point.z, "address": point.embedded_address},
            "transformation": f"({u:.3f}, {v:.3f}) → ({point.x:.3f}, {point.y:.3f}, {point.z:.3f})",
            "equation": manifold.equation,
            "dimensional_bridge": f"Level 4 (PLANE) → Level 5 (VOLUME)"
        }
    
    def explain_dimensional_embedding(self) -> dict:
        """
        Explain how manifolds bridge Fibonacci levels.
        """
        return {
            "title": "Manifolds as Dimensional Bridges",
            "core_insight": (
                "A manifold is a lower-dimensional space embedded in a higher-dimensional one. "
                "The manifold function (like z = xy) IS the dimensional relationship. "
                "This is how Fibonacci levels nest inside each other."
            ),
            "z_equals_xy": {
                "equation": "z = xy",
                "name": "Hyperbolic Paraboloid (Saddle)",
                "intrinsic": "2D - every point addressed by (x, y)",
                "embedded": "3D - every point has position (x, y, z)",
                "transformation": "z = x·y computes the embedding",
                "fibonacci": "PLANE (F=5) embedded in VOLUME (F=8)"
            },
            "dimensional_principle": (
                "Every Fibonacci level is a 'manifold' embedded in the level above. "
                "A POINT is embedded in VALUE (it gains content). "
                "A VALUE is embedded in LENGTH (it gains extent). "
                "A LENGTH is embedded in WIDTH (it gains breadth). "
                "A WIDTH is embedded in PLANE (it becomes a surface). "
                "A PLANE is embedded in VOLUME (it gains depth). "
                "A VOLUME is embedded in WHOLE (it becomes complete). "
                "A WHOLE becomes a POINT in the next scale."
            ),
            "manifolds": {name: info for name, info in self.FIBONACCI_MANIFOLDS.items()}
        }
    
    def list_all(self) -> List[dict]:
        """List all available manifolds"""
        return [m.to_dict() for m in self.manifolds.values()]


# ========== DEMO ==========

if __name__ == "__main__":
    print("=" * 70)
    print("MANIFOLD-DIMENSIONAL BRIDGE")
    print("z = xy: The 2D square warped to 3D")
    print("=" * 70)
    print()
    
    bridge = ManifoldDimensionalBridge()
    
    # Sample the saddle manifold
    print("Saddle Manifold (z = xy):")
    print("-" * 50)
    
    samples = [
        (0.0, 0.0),   # Origin: z = 0
        (1.0, 1.0),   # z = 1
        (1.0, -1.0),  # z = -1
        (-1.0, 1.0),  # z = -1
        (0.5, 0.5),   # z = 0.25
    ]
    
    for u, v in samples:
        result = bridge.sample_point("saddle", u, v)
        print(f"  {result['transformation']}")
    
    print()
    print("Dimensional Embedding Explanation:")
    print("-" * 50)
    explanation = bridge.explain_dimensional_embedding()
    print(explanation["core_insight"])
    print()
    print(f"z = xy:")
    for key, val in explanation["z_equals_xy"].items():
        print(f"  {key}: {val}")
    
    print()
    print("=" * 70)
    print("THE MANIFOLD IS THE DIMENSIONAL TRANSFORMATION")
    print("=" * 70)
