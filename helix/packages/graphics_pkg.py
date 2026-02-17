"""
ButterflyFX Graphics Package
=============================

Copyright (c) 2024-2026 Kenneth Bingham - All Rights Reserved
https://butterflyfx.us

STARTER TIER PACKAGE - $9/month

Advanced graphics substrates building on the kernel primitives.
Includes: Pixel operations, Color theory, Gradients, Shaders, 3D Graphics

This package requires a STARTER or higher license.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable
import math

# Import kernel primitives (always available - open source)
from ..kernel_primitives import (
    Substrate,
    Vector2D, Vector3D,
    Matrix3x3, Matrix4x4,
    RGB, RGBA,
    Scalar,
)

# Import licensing (required for paid packages)
from ..licensing import requires_license, LicenseTier


# =============================================================================
# PIXEL SUBSTRATE
# =============================================================================

@requires_license("graphics")
class PixelSubstrate(Substrate):
    """
    Pixel-level graphics operations.
    
    Operations: blend modes, sampling, filtering
    """
    
    def __init__(self):
        super().__init__("pixel")
        self._init_operations()
    
    @property
    def domain(self) -> str:
        return "graphics.pixel"
    
    def _init_operations(self):
        self.register_operation("blend", self.blend)
        self.register_operation("sample", self.sample)
        self.register_operation("filter_3x3", self.filter_3x3)
    
    def blend(self, src: RGBA, dst: RGBA, mode: str = "normal") -> RGBA:
        """
        Blend source over destination with various blend modes.
        
        Modes: normal, multiply, screen, overlay, darken, lighten, 
               color-dodge, color-burn, hard-light, soft-light, difference
        """
        if mode == "normal":
            # Standard alpha composite
            a_out = src.a + dst.a * (1 - src.a)
            if a_out == 0:
                return RGBA(0, 0, 0, 0)
            r = (src.r * src.a + dst.r * dst.a * (1 - src.a)) / a_out
            g = (src.g * src.a + dst.g * dst.a * (1 - src.a)) / a_out
            b = (src.b * src.a + dst.b * dst.a * (1 - src.a)) / a_out
            return RGBA(int(r), int(g), int(b), a_out)
        
        elif mode == "multiply":
            return RGBA(
                src.r * dst.r // 255,
                src.g * dst.g // 255,
                src.b * dst.b // 255,
                src.a * dst.a
            )
        
        elif mode == "screen":
            return RGBA(
                255 - (255 - src.r) * (255 - dst.r) // 255,
                255 - (255 - src.g) * (255 - dst.g) // 255,
                255 - (255 - src.b) * (255 - dst.b) // 255,
                src.a
            )
        
        elif mode == "overlay":
            def overlay_channel(s, d):
                if d < 128:
                    return 2 * s * d // 255
                return 255 - 2 * (255 - s) * (255 - d) // 255
            return RGBA(
                overlay_channel(src.r, dst.r),
                overlay_channel(src.g, dst.g),
                overlay_channel(src.b, dst.b),
                src.a
            )
        
        elif mode == "darken":
            return RGBA(
                min(src.r, dst.r),
                min(src.g, dst.g),
                min(src.b, dst.b),
                max(src.a, dst.a)
            )
        
        elif mode == "lighten":
            return RGBA(
                max(src.r, dst.r),
                max(src.g, dst.g),
                max(src.b, dst.b),
                max(src.a, dst.a)
            )
        
        elif mode == "difference":
            return RGBA(
                abs(src.r - dst.r),
                abs(src.g - dst.g),
                abs(src.b - dst.b),
                src.a
            )
        
        # Default fallback
        return src
    
    def sample(self, x: float, y: float, texture: List[List[RGBA]], 
               filter_mode: str = "bilinear") -> RGBA:
        """
        Sample color from texture at (x, y) coordinates.
        
        Filter modes: nearest, bilinear
        x, y: normalized 0-1 coordinates
        """
        h = len(texture)
        w = len(texture[0]) if h > 0 else 0
        
        if w == 0 or h == 0:
            return RGBA(0, 0, 0, 0)
        
        px = x * (w - 1)
        py = y * (h - 1)
        
        if filter_mode == "nearest":
            ix = int(round(px))
            iy = int(round(py))
            ix = max(0, min(w - 1, ix))
            iy = max(0, min(h - 1, iy))
            return texture[iy][ix]
        
        # Bilinear interpolation
        x0, y0 = int(px), int(py)
        x1, y1 = min(x0 + 1, w - 1), min(y0 + 1, h - 1)
        fx, fy = px - x0, py - y0
        
        c00 = texture[y0][x0]
        c10 = texture[y0][x1]
        c01 = texture[y1][x0]
        c11 = texture[y1][x1]
        
        r = c00.r*(1-fx)*(1-fy) + c10.r*fx*(1-fy) + c01.r*(1-fx)*fy + c11.r*fx*fy
        g = c00.g*(1-fx)*(1-fy) + c10.g*fx*(1-fy) + c01.g*(1-fx)*fy + c11.g*fx*fy
        b = c00.b*(1-fx)*(1-fy) + c10.b*fx*(1-fy) + c01.b*(1-fx)*fy + c11.b*fx*fy
        a = c00.a*(1-fx)*(1-fy) + c10.a*fx*(1-fy) + c01.a*(1-fx)*fy + c11.a*fx*fy
        
        return RGBA(int(r), int(g), int(b), a)
    
    def filter_3x3(self, center: RGBA, neighbors: List[List[RGBA]], 
                   kernel: List[List[float]]) -> RGBA:
        """
        Apply 3x3 convolution kernel to pixel neighborhood.
        
        neighbors: 3x3 grid of pixels
        kernel: 3x3 convolution weights
        """
        r_sum = g_sum = b_sum = 0.0
        
        for i in range(3):
            for j in range(3):
                k = kernel[i][j]
                c = neighbors[i][j]
                r_sum += c.r * k
                g_sum += c.g * k
                b_sum += c.b * k
        
        return RGBA(
            max(0, min(255, int(r_sum))),
            max(0, min(255, int(g_sum))),
            max(0, min(255, int(b_sum))),
            center.a
        )


# =============================================================================
# GRADIENT SUBSTRATE
# =============================================================================

@dataclass
class GradientStop:
    """A stop in a gradient"""
    position: float  # 0-1 along gradient
    color: RGBA


@requires_license("graphics")
class GradientSubstrate(Substrate):
    """
    Gradient generation and sampling.
    
    Types: linear, radial, angular/conic, diamond
    """
    
    def __init__(self):
        super().__init__("gradient")
        self._init_operations()
    
    @property
    def domain(self) -> str:
        return "graphics.gradient"
    
    def _init_operations(self):
        self.register_primitive("stop", GradientStop)
        self.register_operation("linear", self.linear)
        self.register_operation("radial", self.radial)
        self.register_operation("angular", self.angular)
        self.register_operation("diamond", self.diamond)
    
    def _sample_stops(self, stops: List[GradientStop], t: float) -> RGBA:
        """Sample color at position t in gradient"""
        if not stops:
            return RGBA(0, 0, 0, 0)
        if len(stops) == 1:
            return stops[0].color
        
        stops = sorted(stops, key=lambda s: s.position)
        t = max(0, min(1, t))
        
        if t <= stops[0].position:
            return stops[0].color
        if t >= stops[-1].position:
            return stops[-1].color
        
        for i in range(len(stops) - 1):
            if stops[i].position <= t <= stops[i+1].position:
                span = stops[i+1].position - stops[i].position
                if span == 0:
                    return stops[i].color
                local_t = (t - stops[i].position) / span
                c1, c2 = stops[i].color, stops[i+1].color
                return RGBA(
                    int(c1.r + (c2.r - c1.r) * local_t),
                    int(c1.g + (c2.g - c1.g) * local_t),
                    int(c1.b + (c2.b - c1.b) * local_t),
                    c1.a + (c2.a - c1.a) * local_t
                )
        
        return stops[-1].color
    
    def linear(self, stops: List[GradientStop], x: float, y: float,
               angle: float = 0) -> RGBA:
        """
        Sample linear gradient at (x, y).
        
        angle: gradient angle in radians (0 = left to right)
        """
        # Project point onto gradient line
        t = x * math.cos(angle) + y * math.sin(angle)
        return self._sample_stops(stops, t)
    
    def radial(self, stops: List[GradientStop], x: float, y: float,
               cx: float = 0.5, cy: float = 0.5, radius: float = 0.5) -> RGBA:
        """
        Sample radial gradient at (x, y).
        
        cx, cy: center of gradient
        radius: outer edge radius
        """
        dist = math.sqrt((x - cx)**2 + (y - cy)**2)
        t = dist / radius if radius > 0 else 0
        return self._sample_stops(stops, t)
    
    def angular(self, stops: List[GradientStop], x: float, y: float,
                cx: float = 0.5, cy: float = 0.5, offset: float = 0) -> RGBA:
        """
        Sample angular (conic) gradient at (x, y).
        
        cx, cy: center point
        offset: rotation offset in radians
        """
        angle = math.atan2(y - cy, x - cx) + math.pi + offset
        t = (angle % (2 * math.pi)) / (2 * math.pi)
        return self._sample_stops(stops, t)
    
    def diamond(self, stops: List[GradientStop], x: float, y: float,
                cx: float = 0.5, cy: float = 0.5, size: float = 0.5) -> RGBA:
        """
        Sample diamond gradient at (x, y).
        
        Uses Manhattan distance for diamond shape.
        """
        dist = abs(x - cx) + abs(y - cy)
        t = dist / size if size > 0 else 0
        return self._sample_stops(stops, t)


# =============================================================================
# SHADER SUBSTRATE
# =============================================================================

@requires_license("graphics")
class ShaderSubstrate(Substrate):
    """
    Shader-like programmable graphics operations.
    
    Define functions that run per-pixel or per-vertex.
    """
    
    def __init__(self):
        super().__init__("shader")
        self._pixel = PixelSubstrate()
        self._gradient = GradientSubstrate()
        self._init_operations()
    
    @property
    def domain(self) -> str:
        return "graphics.shader"
    
    def _init_operations(self):
        self.register_operation("fragment", self.fragment)
        self.register_operation("vertex", self.vertex)
        self.register_operation("noise", self.noise)
        self.register_operation("fbm", self.fbm)
    
    def fragment(self, uv: Vector2D, time: float, 
                 shader_func: Callable[[Vector2D, float], RGBA]) -> RGBA:
        """
        Execute fragment shader function.
        
        uv: texture coordinates (0-1)
        time: animation time
        shader_func: function(uv, time) -> RGBA
        """
        return shader_func(uv, time)
    
    def vertex(self, position: Vector3D, 
               transform: Matrix4x4) -> Vector3D:
        """
        Execute vertex transformation.
        """
        return transform.transform(position)
    
    def noise(self, x: float, y: float, seed: int = 42) -> float:
        """
        Value noise function.
        
        Returns value in range [-1, 1]
        """
        def hash_coord(ix, iy):
            n = ix + iy * 57 + seed
            n = (n << 13) ^ n
            return 1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0
        
        ix, iy = int(math.floor(x)), int(math.floor(y))
        fx, fy = x - ix, y - iy
        
        # Smoothstep interpolation
        fx = fx * fx * (3 - 2 * fx)
        fy = fy * fy * (3 - 2 * fy)
        
        v00 = hash_coord(ix, iy)
        v10 = hash_coord(ix + 1, iy)
        v01 = hash_coord(ix, iy + 1)
        v11 = hash_coord(ix + 1, iy + 1)
        
        return (v00 * (1 - fx) + v10 * fx) * (1 - fy) + \
               (v01 * (1 - fx) + v11 * fx) * fy
    
    def fbm(self, x: float, y: float, octaves: int = 6, 
            lacunarity: float = 2.0, gain: float = 0.5) -> float:
        """
        Fractal Brownian Motion (layered noise).
        
        Returns sum of noise at multiple frequencies.
        """
        value = 0.0
        amplitude = 1.0
        frequency = 1.0
        
        for _ in range(octaves):
            value += amplitude * self.noise(x * frequency, y * frequency)
            amplitude *= gain
            frequency *= lacunarity
        
        return value


# =============================================================================
# 3D GRAPHICS SUBSTRATE
# =============================================================================

@dataclass
class Vertex:
    """3D vertex with attributes"""
    position: Vector3D
    normal: Optional[Vector3D] = None
    uv: Optional[Vector2D] = None
    color: Optional[RGBA] = None


@dataclass
class Triangle:
    """Triangle face (3 vertex indices)"""
    v0: int
    v1: int
    v2: int
    
    def normal(self, vertices: List[Vertex]) -> Vector3D:
        """Compute face normal"""
        p0 = vertices[self.v0].position
        p1 = vertices[self.v1].position
        p2 = vertices[self.v2].position
        e1 = p1 - p0
        e2 = p2 - p0
        return e1.cross(e2).normalize()


@dataclass
class Mesh:
    """3D mesh"""
    vertices: List[Vertex] = field(default_factory=list)
    triangles: List[Triangle] = field(default_factory=list)


@requires_license("graphics")
class Graphics3DSubstrate(Substrate):
    """
    3D graphics operations.
    
    Mesh creation, transformation, rendering.
    """
    
    def __init__(self):
        super().__init__("graphics3d")
        self._init_operations()
    
    @property
    def domain(self) -> str:
        return "graphics.3d"
    
    def _init_operations(self):
        self.register_primitive("vertex", Vertex)
        self.register_primitive("triangle", Triangle)
        self.register_primitive("mesh", Mesh)
        self.register_operation("cube", self.create_cube)
        self.register_operation("sphere", self.create_sphere)
        self.register_operation("plane", self.create_plane)
        self.register_operation("transform_mesh", self.transform_mesh)
    
    def create_cube(self, size: float = 1.0) -> Mesh:
        """Create a cube mesh"""
        s = size / 2
        vertices = [
            Vertex(Vector3D(-s, -s, -s)), Vertex(Vector3D(s, -s, -s)),
            Vertex(Vector3D(s, s, -s)), Vertex(Vector3D(-s, s, -s)),
            Vertex(Vector3D(-s, -s, s)), Vertex(Vector3D(s, -s, s)),
            Vertex(Vector3D(s, s, s)), Vertex(Vector3D(-s, s, s)),
        ]
        triangles = [
            Triangle(0, 2, 1), Triangle(0, 3, 2),
            Triangle(4, 5, 6), Triangle(4, 6, 7),
            Triangle(0, 1, 5), Triangle(0, 5, 4),
            Triangle(2, 3, 7), Triangle(2, 7, 6),
            Triangle(0, 4, 7), Triangle(0, 7, 3),
            Triangle(1, 2, 6), Triangle(1, 6, 5),
        ]
        return Mesh(vertices, triangles)
    
    def create_sphere(self, radius: float = 1.0, segments: int = 16) -> Mesh:
        """Create a UV sphere"""
        vertices = []
        triangles = []
        
        for i in range(segments + 1):
            theta = math.pi * i / segments
            for j in range(segments):
                phi = 2 * math.pi * j / segments
                x = radius * math.sin(theta) * math.cos(phi)
                y = radius * math.sin(theta) * math.sin(phi)
                z = radius * math.cos(theta)
                pos = Vector3D(x, y, z)
                vertices.append(Vertex(pos, pos.normalize()))
        
        for i in range(segments):
            for j in range(segments):
                v0 = i * segments + j
                v1 = i * segments + (j + 1) % segments
                v2 = (i + 1) * segments + j
                v3 = (i + 1) * segments + (j + 1) % segments
                triangles.append(Triangle(v0, v1, v2))
                triangles.append(Triangle(v1, v3, v2))
        
        return Mesh(vertices, triangles)
    
    def create_plane(self, width: float = 1.0, height: float = 1.0) -> Mesh:
        """Create a plane"""
        w2, h2 = width / 2, height / 2
        vertices = [
            Vertex(Vector3D(-w2, 0, -h2), Vector3D(0, 1, 0), Vector2D(0, 0)),
            Vertex(Vector3D(w2, 0, -h2), Vector3D(0, 1, 0), Vector2D(1, 0)),
            Vertex(Vector3D(w2, 0, h2), Vector3D(0, 1, 0), Vector2D(1, 1)),
            Vertex(Vector3D(-w2, 0, h2), Vector3D(0, 1, 0), Vector2D(0, 1)),
        ]
        triangles = [
            Triangle(0, 1, 2),
            Triangle(0, 2, 3),
        ]
        return Mesh(vertices, triangles)
    
    def transform_mesh(self, mesh: Mesh, transform: Matrix4x4) -> Mesh:
        """Apply transformation to mesh"""
        new_vertices = []
        for v in mesh.vertices:
            new_pos = transform.transform(v.position)
            # Transform normal (without translation)
            new_normal = None
            if v.normal:
                new_normal = Vector3D(
                    transform.data[0][0] * v.normal.x + transform.data[0][1] * v.normal.y + transform.data[0][2] * v.normal.z,
                    transform.data[1][0] * v.normal.x + transform.data[1][1] * v.normal.y + transform.data[1][2] * v.normal.z,
                    transform.data[2][0] * v.normal.x + transform.data[2][1] * v.normal.y + transform.data[2][2] * v.normal.z,
                ).normalize()
            new_vertices.append(Vertex(new_pos, new_normal, v.uv, v.color))
        
        return Mesh(new_vertices, mesh.triangles)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'PixelSubstrate',
    'GradientSubstrate',
    'GradientStop',
    'ShaderSubstrate',
    'Graphics3DSubstrate',
    'Vertex',
    'Triangle',
    'Mesh',
]
