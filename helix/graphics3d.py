"""
ButterflyFX 3D Graphics Engine

True 3D graphics with mathematical precision:
- Vector/Matrix math (not shading tricks)
- Proper perspective projection
- Depth buffer (z-ordering)
- Physics simulation (forces, collisions)
- Scene graph with transformations

All coordinates are mathematically correct in 3D space.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Callable
from enum import Enum, auto
import math


# =============================================================================
# VECTOR MATHEMATICS
# =============================================================================

@dataclass
class Vec3:
    """3D vector with full mathematical operations"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other: 'Vec3') -> 'Vec3':
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: 'Vec3') -> 'Vec3':
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float) -> 'Vec3':
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __rmul__(self, scalar: float) -> 'Vec3':
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar: float) -> 'Vec3':
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def __neg__(self) -> 'Vec3':
        return Vec3(-self.x, -self.y, -self.z)
    
    def dot(self, other: 'Vec3') -> float:
        """Dot product: a · b = |a||b|cos(θ)"""
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other: 'Vec3') -> 'Vec3':
        """Cross product: a × b = normal to both vectors"""
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def magnitude(self) -> float:
        """Length of vector: |v| = √(x² + y² + z²)"""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def magnitude_squared(self) -> float:
        """Squared length (faster, no sqrt)"""
        return self.x**2 + self.y**2 + self.z**2
    
    def normalized(self) -> 'Vec3':
        """Unit vector: v̂ = v / |v|"""
        mag = self.magnitude()
        if mag < 1e-10:
            return Vec3(0, 0, 0)
        return self / mag
    
    def lerp(self, other: 'Vec3', t: float) -> 'Vec3':
        """Linear interpolation: a + t(b - a)"""
        return self + (other - self) * t
    
    def reflect(self, normal: 'Vec3') -> 'Vec3':
        """Reflection: v - 2(v·n)n"""
        return self - normal * (2 * self.dot(normal))
    
    def project_onto(self, other: 'Vec3') -> 'Vec3':
        """Project this vector onto another"""
        return other * (self.dot(other) / other.dot(other))
    
    def angle_to(self, other: 'Vec3') -> float:
        """Angle between vectors in radians"""
        cos_angle = self.dot(other) / (self.magnitude() * other.magnitude())
        return math.acos(max(-1, min(1, cos_angle)))
    
    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)
    
    @staticmethod
    def zero() -> 'Vec3':
        return Vec3(0, 0, 0)
    
    @staticmethod
    def one() -> 'Vec3':
        return Vec3(1, 1, 1)
    
    @staticmethod
    def up() -> 'Vec3':
        return Vec3(0, 1, 0)
    
    @staticmethod
    def right() -> 'Vec3':
        return Vec3(1, 0, 0)
    
    @staticmethod
    def forward() -> 'Vec3':
        return Vec3(0, 0, 1)


# =============================================================================
# MATRIX MATHEMATICS
# =============================================================================

@dataclass
class Mat4:
    """4x4 transformation matrix (row-major)
    
    Used for:
    - Translation, rotation, scaling
    - Model → World → View → Clip space transforms
    - Perspective projection
    """
    m: List[List[float]] = field(default_factory=lambda: [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    
    def __mul__(self, other: 'Mat4') -> 'Mat4':
        """Matrix multiplication: C = A × B"""
        result = [[0.0] * 4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    result[i][j] += self.m[i][k] * other.m[k][j]
        return Mat4(result)
    
    def transform_point(self, v: Vec3) -> Vec3:
        """Transform a point (w=1, applies translation)"""
        x = self.m[0][0]*v.x + self.m[0][1]*v.y + self.m[0][2]*v.z + self.m[0][3]
        y = self.m[1][0]*v.x + self.m[1][1]*v.y + self.m[1][2]*v.z + self.m[1][3]
        z = self.m[2][0]*v.x + self.m[2][1]*v.y + self.m[2][2]*v.z + self.m[2][3]
        w = self.m[3][0]*v.x + self.m[3][1]*v.y + self.m[3][2]*v.z + self.m[3][3]
        
        if abs(w) > 1e-10:
            return Vec3(x/w, y/w, z/w)
        return Vec3(x, y, z)
    
    def transform_direction(self, v: Vec3) -> Vec3:
        """Transform a direction (w=0, no translation)"""
        x = self.m[0][0]*v.x + self.m[0][1]*v.y + self.m[0][2]*v.z
        y = self.m[1][0]*v.x + self.m[1][1]*v.y + self.m[1][2]*v.z
        z = self.m[2][0]*v.x + self.m[2][1]*v.y + self.m[2][2]*v.z
        return Vec3(x, y, z)
    
    def determinant(self) -> float:
        """Calculate 4x4 determinant using cofactor expansion"""
        # Expand along first row
        det = 0.0
        for j in range(4):
            minor = self._minor(0, j)
            cofactor = ((-1) ** j) * minor
            det += self.m[0][j] * cofactor
        return det
    
    def _minor(self, row: int, col: int) -> float:
        """3x3 minor determinant"""
        sub = []
        for i in range(4):
            if i == row:
                continue
            sub_row = []
            for j in range(4):
                if j == col:
                    continue
                sub_row.append(self.m[i][j])
            sub.append(sub_row)
        
        # 3x3 determinant
        return (sub[0][0] * (sub[1][1]*sub[2][2] - sub[1][2]*sub[2][1]) -
                sub[0][1] * (sub[1][0]*sub[2][2] - sub[1][2]*sub[2][0]) +
                sub[0][2] * (sub[1][0]*sub[2][1] - sub[1][1]*sub[2][0]))
    
    def inverse(self) -> Optional['Mat4']:
        """Calculate matrix inverse using adjugate method"""
        det = self.determinant()
        if abs(det) < 1e-10:
            return None
        
        # Compute adjugate matrix
        adj = [[0.0] * 4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                minor = self._minor(i, j)
                adj[j][i] = ((-1) ** (i + j)) * minor / det
        
        return Mat4(adj)
    
    def transpose(self) -> 'Mat4':
        """Matrix transpose: M^T"""
        return Mat4([[self.m[j][i] for j in range(4)] for i in range(4)])
    
    @staticmethod
    def identity() -> 'Mat4':
        return Mat4()
    
    @staticmethod
    def translation(tx: float, ty: float, tz: float) -> 'Mat4':
        """Translation matrix"""
        return Mat4([
            [1, 0, 0, tx],
            [0, 1, 0, ty],
            [0, 0, 1, tz],
            [0, 0, 0, 1]
        ])
    
    @staticmethod
    def scale(sx: float, sy: float, sz: float) -> 'Mat4':
        """Scale matrix"""
        return Mat4([
            [sx, 0, 0, 0],
            [0, sy, 0, 0],
            [0, 0, sz, 0],
            [0, 0, 0, 1]
        ])
    
    @staticmethod
    def rotation_x(angle: float) -> 'Mat4':
        """Rotation around X axis (angle in radians)"""
        c, s = math.cos(angle), math.sin(angle)
        return Mat4([
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1]
        ])
    
    @staticmethod
    def rotation_y(angle: float) -> 'Mat4':
        """Rotation around Y axis (angle in radians)"""
        c, s = math.cos(angle), math.sin(angle)
        return Mat4([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1]
        ])
    
    @staticmethod
    def rotation_z(angle: float) -> 'Mat4':
        """Rotation around Z axis (angle in radians)"""
        c, s = math.cos(angle), math.sin(angle)
        return Mat4([
            [c, -s, 0, 0],
            [s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
    
    @staticmethod
    def rotation_axis(axis: Vec3, angle: float) -> 'Mat4':
        """Rotation around arbitrary axis (Rodrigues' rotation formula)"""
        axis = axis.normalized()
        c, s = math.cos(angle), math.sin(angle)
        t = 1 - c
        x, y, z = axis.x, axis.y, axis.z
        
        return Mat4([
            [t*x*x + c,     t*x*y - s*z,   t*x*z + s*y,   0],
            [t*x*y + s*z,   t*y*y + c,     t*y*z - s*x,   0],
            [t*x*z - s*y,   t*y*z + s*x,   t*z*z + c,     0],
            [0,             0,             0,             1]
        ])
    
    @staticmethod
    def look_at(eye: Vec3, target: Vec3, up: Vec3) -> 'Mat4':
        """View matrix: camera at eye, looking at target"""
        forward = (target - eye).normalized()
        right = forward.cross(up).normalized()
        up = right.cross(forward)
        
        return Mat4([
            [right.x, right.y, right.z, -right.dot(eye)],
            [up.x, up.y, up.z, -up.dot(eye)],
            [-forward.x, -forward.y, -forward.z, forward.dot(eye)],
            [0, 0, 0, 1]
        ])
    
    @staticmethod
    def perspective(fov_y: float, aspect: float, near: float, far: float) -> 'Mat4':
        """Perspective projection matrix
        
        fov_y: Field of view in radians (vertical)
        aspect: Width / height
        near: Near clipping plane
        far: Far clipping plane
        """
        f = 1.0 / math.tan(fov_y / 2.0)
        nf = 1.0 / (near - far)
        
        return Mat4([
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) * nf, 2 * far * near * nf],
            [0, 0, -1, 0]
        ])
    
    @staticmethod
    def orthographic(left: float, right: float, bottom: float, top: float, 
                    near: float, far: float) -> 'Mat4':
        """Orthographic projection matrix (no perspective distortion)"""
        return Mat4([
            [2/(right-left), 0, 0, -(right+left)/(right-left)],
            [0, 2/(top-bottom), 0, -(top+bottom)/(top-bottom)],
            [0, 0, -2/(far-near), -(far+near)/(far-near)],
            [0, 0, 0, 1]
        ])


# =============================================================================
# QUATERNION (for smooth rotations)
# =============================================================================

@dataclass
class Quaternion:
    """Quaternion for rotation (avoids gimbal lock)
    
    q = w + xi + yj + zk
    """
    w: float = 1.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __mul__(self, other: 'Quaternion') -> 'Quaternion':
        """Quaternion multiplication"""
        return Quaternion(
            w=self.w*other.w - self.x*other.x - self.y*other.y - self.z*other.z,
            x=self.w*other.x + self.x*other.w + self.y*other.z - self.z*other.y,
            y=self.w*other.y - self.x*other.z + self.y*other.w + self.z*other.x,
            z=self.w*other.z + self.x*other.y - self.y*other.x + self.z*other.w
        )
    
    def magnitude(self) -> float:
        return math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)
    
    def normalized(self) -> 'Quaternion':
        mag = self.magnitude()
        if mag < 1e-10:
            return Quaternion()
        return Quaternion(self.w/mag, self.x/mag, self.y/mag, self.z/mag)
    
    def conjugate(self) -> 'Quaternion':
        """Quaternion conjugate: q* = w - xi - yj - zk"""
        return Quaternion(self.w, -self.x, -self.y, -self.z)
    
    def inverse(self) -> 'Quaternion':
        """Quaternion inverse: q⁻¹ = q* / |q|²"""
        mag_sq = self.w**2 + self.x**2 + self.y**2 + self.z**2
        if mag_sq < 1e-10:
            return Quaternion()
        return Quaternion(self.w/mag_sq, -self.x/mag_sq, -self.y/mag_sq, -self.z/mag_sq)
    
    def rotate_vector(self, v: Vec3) -> Vec3:
        """Rotate vector by quaternion: q × v × q*"""
        qv = Quaternion(0, v.x, v.y, v.z)
        result = self * qv * self.conjugate()
        return Vec3(result.x, result.y, result.z)
    
    def to_matrix(self) -> Mat4:
        """Convert to rotation matrix"""
        xx, yy, zz = self.x**2, self.y**2, self.z**2
        xy, xz, yz = self.x*self.y, self.x*self.z, self.y*self.z
        wx, wy, wz = self.w*self.x, self.w*self.y, self.w*self.z
        
        return Mat4([
            [1 - 2*(yy+zz), 2*(xy-wz), 2*(xz+wy), 0],
            [2*(xy+wz), 1 - 2*(xx+zz), 2*(yz-wx), 0],
            [2*(xz-wy), 2*(yz+wx), 1 - 2*(xx+yy), 0],
            [0, 0, 0, 1]
        ])
    
    def slerp(self, other: 'Quaternion', t: float) -> 'Quaternion':
        """Spherical linear interpolation (smooth rotation blend)"""
        # Compute dot product
        dot = self.w*other.w + self.x*other.x + self.y*other.y + self.z*other.z
        
        # If negative, negate one to take shorter path
        q2 = other
        if dot < 0:
            q2 = Quaternion(-other.w, -other.x, -other.y, -other.z)
            dot = -dot
        
        # If very close, use linear interpolation
        if dot > 0.9995:
            result = Quaternion(
                self.w + t*(q2.w - self.w),
                self.x + t*(q2.x - self.x),
                self.y + t*(q2.y - self.y),
                self.z + t*(q2.z - self.z)
            )
            return result.normalized()
        
        # Spherical interpolation
        theta = math.acos(dot)
        sin_theta = math.sin(theta)
        s1 = math.sin((1-t)*theta) / sin_theta
        s2 = math.sin(t*theta) / sin_theta
        
        return Quaternion(
            s1*self.w + s2*q2.w,
            s1*self.x + s2*q2.x,
            s1*self.y + s2*q2.y,
            s1*self.z + s2*q2.z
        )
    
    @staticmethod
    def from_axis_angle(axis: Vec3, angle: float) -> 'Quaternion':
        """Create quaternion from axis and angle (radians)"""
        half = angle / 2
        s = math.sin(half)
        axis = axis.normalized()
        return Quaternion(math.cos(half), axis.x*s, axis.y*s, axis.z*s)
    
    @staticmethod
    def from_euler(pitch: float, yaw: float, roll: float) -> 'Quaternion':
        """Create from Euler angles (radians)"""
        cy, sy = math.cos(yaw/2), math.sin(yaw/2)
        cp, sp = math.cos(pitch/2), math.sin(pitch/2)
        cr, sr = math.cos(roll/2), math.sin(roll/2)
        
        return Quaternion(
            w=cr*cp*cy + sr*sp*sy,
            x=sr*cp*cy - cr*sp*sy,
            y=cr*sp*cy + sr*cp*sy,
            z=cr*cp*sy - sr*sp*cy
        )


# =============================================================================
# GEOMETRY PRIMITIVES
# =============================================================================

@dataclass
class Vertex:
    """3D vertex with position, normal, and color"""
    position: Vec3
    normal: Vec3 = field(default_factory=Vec3.up)
    color: Tuple[int, int, int] = (255, 255, 255)
    uv: Tuple[float, float] = (0.0, 0.0)


@dataclass
class Triangle:
    """Triangle defined by three vertex indices"""
    v0: int
    v1: int
    v2: int
    
    def get_vertices(self, vertices: List[Vertex]) -> Tuple[Vertex, Vertex, Vertex]:
        return vertices[self.v0], vertices[self.v1], vertices[self.v2]
    
    def compute_normal(self, vertices: List[Vertex]) -> Vec3:
        """Calculate face normal from vertices"""
        v0, v1, v2 = self.get_vertices(vertices)
        edge1 = v1.position - v0.position
        edge2 = v2.position - v0.position
        return edge1.cross(edge2).normalized()
    
    def center(self, vertices: List[Vertex]) -> Vec3:
        """Triangle centroid"""
        v0, v1, v2 = self.get_vertices(vertices)
        return (v0.position + v1.position + v2.position) / 3


@dataclass
class Mesh:
    """3D mesh with vertices and triangles"""
    vertices: List[Vertex] = field(default_factory=list)
    triangles: List[Triangle] = field(default_factory=list)
    
    def compute_normals(self):
        """Calculate vertex normals from face normals"""
        # Reset normals
        for v in self.vertices:
            v.normal = Vec3.zero()
        
        # Accumulate face normals to vertices
        for tri in self.triangles:
            normal = tri.compute_normal(self.vertices)
            self.vertices[tri.v0].normal = self.vertices[tri.v0].normal + normal
            self.vertices[tri.v1].normal = self.vertices[tri.v1].normal + normal
            self.vertices[tri.v2].normal = self.vertices[tri.v2].normal + normal
        
        # Normalize
        for v in self.vertices:
            v.normal = v.normal.normalized()
    
    def get_bounds(self) -> Tuple[Vec3, Vec3]:
        """Get axis-aligned bounding box"""
        if not self.vertices:
            return Vec3.zero(), Vec3.zero()
        
        min_p = Vec3(float('inf'), float('inf'), float('inf'))
        max_p = Vec3(float('-inf'), float('-inf'), float('-inf'))
        
        for v in self.vertices:
            min_p.x = min(min_p.x, v.position.x)
            min_p.y = min(min_p.y, v.position.y)
            min_p.z = min(min_p.z, v.position.z)
            max_p.x = max(max_p.x, v.position.x)
            max_p.y = max(max_p.y, v.position.y)
            max_p.z = max(max_p.z, v.position.z)
        
        return min_p, max_p
    
    @staticmethod
    def cube(size: float = 1.0, color: Tuple[int, int, int] = (255, 255, 255)) -> 'Mesh':
        """Generate a unit cube centered at origin"""
        h = size / 2
        vertices = [
            # Front face
            Vertex(Vec3(-h, -h, h), Vec3(0, 0, 1), color),
            Vertex(Vec3(h, -h, h), Vec3(0, 0, 1), color),
            Vertex(Vec3(h, h, h), Vec3(0, 0, 1), color),
            Vertex(Vec3(-h, h, h), Vec3(0, 0, 1), color),
            # Back face
            Vertex(Vec3(h, -h, -h), Vec3(0, 0, -1), color),
            Vertex(Vec3(-h, -h, -h), Vec3(0, 0, -1), color),
            Vertex(Vec3(-h, h, -h), Vec3(0, 0, -1), color),
            Vertex(Vec3(h, h, -h), Vec3(0, 0, -1), color),
            # Top face
            Vertex(Vec3(-h, h, h), Vec3(0, 1, 0), color),
            Vertex(Vec3(h, h, h), Vec3(0, 1, 0), color),
            Vertex(Vec3(h, h, -h), Vec3(0, 1, 0), color),
            Vertex(Vec3(-h, h, -h), Vec3(0, 1, 0), color),
            # Bottom face
            Vertex(Vec3(-h, -h, -h), Vec3(0, -1, 0), color),
            Vertex(Vec3(h, -h, -h), Vec3(0, -1, 0), color),
            Vertex(Vec3(h, -h, h), Vec3(0, -1, 0), color),
            Vertex(Vec3(-h, -h, h), Vec3(0, -1, 0), color),
            # Right face
            Vertex(Vec3(h, -h, h), Vec3(1, 0, 0), color),
            Vertex(Vec3(h, -h, -h), Vec3(1, 0, 0), color),
            Vertex(Vec3(h, h, -h), Vec3(1, 0, 0), color),
            Vertex(Vec3(h, h, h), Vec3(1, 0, 0), color),
            # Left face
            Vertex(Vec3(-h, -h, -h), Vec3(-1, 0, 0), color),
            Vertex(Vec3(-h, -h, h), Vec3(-1, 0, 0), color),
            Vertex(Vec3(-h, h, h), Vec3(-1, 0, 0), color),
            Vertex(Vec3(-h, h, -h), Vec3(-1, 0, 0), color),
        ]
        
        triangles = [
            Triangle(0, 1, 2), Triangle(0, 2, 3),    # Front
            Triangle(4, 5, 6), Triangle(4, 6, 7),    # Back
            Triangle(8, 9, 10), Triangle(8, 10, 11), # Top
            Triangle(12, 13, 14), Triangle(12, 14, 15), # Bottom
            Triangle(16, 17, 18), Triangle(16, 18, 19), # Right
            Triangle(20, 21, 22), Triangle(20, 22, 23), # Left
        ]
        
        return Mesh(vertices, triangles)
    
    @staticmethod
    def sphere(radius: float = 1.0, segments: int = 16, rings: int = 12,
               color: Tuple[int, int, int] = (255, 255, 255)) -> 'Mesh':
        """Generate a UV sphere"""
        vertices = []
        triangles = []
        
        for ring in range(rings + 1):
            phi = math.pi * ring / rings
            for seg in range(segments):
                theta = 2 * math.pi * seg / segments
                
                x = radius * math.sin(phi) * math.cos(theta)
                y = radius * math.cos(phi)
                z = radius * math.sin(phi) * math.sin(theta)
                
                pos = Vec3(x, y, z)
                normal = pos.normalized()
                vertices.append(Vertex(pos, normal, color))
        
        # Create triangles
        for ring in range(rings):
            for seg in range(segments):
                next_seg = (seg + 1) % segments
                
                current = ring * segments + seg
                next_ring = (ring + 1) * segments + seg
                
                triangles.append(Triangle(current, next_ring, ring * segments + next_seg))
                triangles.append(Triangle(ring * segments + next_seg, next_ring, (ring + 1) * segments + next_seg))
        
        return Mesh(vertices, triangles)
    
    @staticmethod
    def cylinder(radius: float = 1.0, height: float = 2.0, segments: int = 16,
                 color: Tuple[int, int, int] = (255, 255, 255)) -> 'Mesh':
        """Generate a cylinder"""
        vertices = []
        triangles = []
        h2 = height / 2
        
        # Side vertices
        for i in range(segments):
            theta = 2 * math.pi * i / segments
            x = radius * math.cos(theta)
            z = radius * math.sin(theta)
            normal = Vec3(math.cos(theta), 0, math.sin(theta))
            
            vertices.append(Vertex(Vec3(x, -h2, z), normal, color))
            vertices.append(Vertex(Vec3(x, h2, z), normal, color))
        
        # Side triangles
        for i in range(segments):
            next_i = (i + 1) % segments
            v0 = i * 2
            v1 = i * 2 + 1
            v2 = next_i * 2
            v3 = next_i * 2 + 1
            triangles.append(Triangle(v0, v2, v1))
            triangles.append(Triangle(v1, v2, v3))
        
        # Top and bottom caps
        top_center = len(vertices)
        vertices.append(Vertex(Vec3(0, h2, 0), Vec3.up(), color))
        bottom_center = len(vertices)
        vertices.append(Vertex(Vec3(0, -h2, 0), Vec3(0, -1, 0), color))
        
        for i in range(segments):
            next_i = (i + 1) % segments
            triangles.append(Triangle(top_center, i*2 + 1, next_i*2 + 1))
            triangles.append(Triangle(bottom_center, next_i*2, i*2))
        
        return Mesh(vertices, triangles)
    
    @staticmethod
    def helix_spiral(radius: float = 1.0, pitch: float = 0.5, turns: int = 3,
                     tube_radius: float = 0.1, segments: int = 8, 
                     rings_per_turn: int = 24,
                     color: Tuple[int, int, int] = (139, 92, 246)) -> 'Mesh':
        """Generate a 3D helix (coiled tube) - the ButterflyFX signature shape"""
        vertices = []
        triangles = []
        
        total_rings = turns * rings_per_turn
        
        for ring in range(total_rings + 1):
            t = ring / rings_per_turn
            theta = 2 * math.pi * t
            
            # Helix center point
            cx = radius * math.cos(theta)
            cy = pitch * t
            cz = radius * math.sin(theta)
            
            # Tangent direction (derivative of helix)
            tx = -radius * math.sin(theta)
            ty = pitch / (2 * math.pi)
            tz = radius * math.cos(theta)
            tangent = Vec3(tx, ty, tz).normalized()
            
            # Build local coordinate frame
            up = Vec3.up()
            right = tangent.cross(up).normalized()
            up = right.cross(tangent).normalized()
            
            # Create tube vertices around this point
            for seg in range(segments):
                phi = 2 * math.pi * seg / segments
                # Point on tube surface
                offset = right * (tube_radius * math.cos(phi)) + up * (tube_radius * math.sin(phi))
                pos = Vec3(cx, cy, cz) + offset
                normal = offset.normalized()
                vertices.append(Vertex(pos, normal, color))
        
        # Create triangles
        for ring in range(total_rings):
            for seg in range(segments):
                next_seg = (seg + 1) % segments
                
                v0 = ring * segments + seg
                v1 = ring * segments + next_seg
                v2 = (ring + 1) * segments + seg
                v3 = (ring + 1) * segments + next_seg
                
                triangles.append(Triangle(v0, v2, v1))
                triangles.append(Triangle(v1, v2, v3))
        
        return Mesh(vertices, triangles)


# =============================================================================
# PHYSICS
# =============================================================================

@dataclass
class RigidBody:
    """Physics body with mass, velocity, and forces"""
    mass: float = 1.0
    position: Vec3 = field(default_factory=Vec3.zero)
    velocity: Vec3 = field(default_factory=Vec3.zero)
    acceleration: Vec3 = field(default_factory=Vec3.zero)
    angular_velocity: Vec3 = field(default_factory=Vec3.zero)
    rotation: Quaternion = field(default_factory=Quaternion)
    
    # Physics properties
    restitution: float = 0.5      # Bounciness (0-1)
    friction: float = 0.3         # Surface friction
    drag: float = 0.01            # Air resistance
    
    # Constraints
    is_static: bool = False       # If true, doesn't move
    freeze_rotation: bool = False
    
    # Accumulated forces
    _force: Vec3 = field(default_factory=Vec3.zero)
    _torque: Vec3 = field(default_factory=Vec3.zero)
    
    def apply_force(self, force: Vec3):
        """Apply force at center of mass"""
        self._force = self._force + force
    
    def apply_force_at_point(self, force: Vec3, point: Vec3):
        """Apply force at a point (generates torque)"""
        self._force = self._force + force
        r = point - self.position
        self._torque = self._torque + r.cross(force)
    
    def apply_impulse(self, impulse: Vec3):
        """Instant velocity change"""
        if not self.is_static:
            self.velocity = self.velocity + impulse / self.mass
    
    def apply_torque(self, torque: Vec3):
        """Apply rotational force"""
        self._torque = self._torque + torque
    
    def integrate(self, dt: float):
        """Update physics state using semi-implicit Euler integration"""
        if self.is_static:
            return
        
        # Linear motion
        self.acceleration = self._force / self.mass
        self.velocity = self.velocity + self.acceleration * dt
        
        # Apply drag
        self.velocity = self.velocity * (1 - self.drag)
        
        # Update position
        self.position = self.position + self.velocity * dt
        
        # Angular motion
        if not self.freeze_rotation:
            self.angular_velocity = self.angular_velocity + self._torque * dt
            self.angular_velocity = self.angular_velocity * (1 - self.drag)
            
            # Update rotation
            omega = self.angular_velocity.magnitude()
            if omega > 1e-6:
                axis = self.angular_velocity / omega
                delta_rot = Quaternion.from_axis_angle(axis, omega * dt)
                self.rotation = delta_rot * self.rotation
                self.rotation = self.rotation.normalized()
        
        # Clear forces
        self._force = Vec3.zero()
        self._torque = Vec3.zero()


@dataclass 
class AABB:
    """Axis-Aligned Bounding Box for collision detection"""
    min: Vec3 = field(default_factory=Vec3.zero)
    max: Vec3 = field(default_factory=Vec3.zero)
    
    def contains(self, point: Vec3) -> bool:
        return (self.min.x <= point.x <= self.max.x and
                self.min.y <= point.y <= self.max.y and
                self.min.z <= point.z <= self.max.z)
    
    def intersects(self, other: 'AABB') -> bool:
        return (self.min.x <= other.max.x and self.max.x >= other.min.x and
                self.min.y <= other.max.y and self.max.y >= other.min.y and
                self.min.z <= other.max.z and self.max.z >= other.min.z)
    
    def center(self) -> Vec3:
        return (self.min + self.max) * 0.5
    
    def extents(self) -> Vec3:
        return (self.max - self.min) * 0.5
    
    @staticmethod
    def from_mesh(mesh: Mesh, transform: Mat4 = None) -> 'AABB':
        """Create AABB from mesh vertices"""
        if not mesh.vertices:
            return AABB()
        
        min_p = Vec3(float('inf'), float('inf'), float('inf'))
        max_p = Vec3(float('-inf'), float('-inf'), float('-inf'))
        
        for v in mesh.vertices:
            pos = v.position
            if transform:
                pos = transform.transform_point(pos)
            
            min_p.x = min(min_p.x, pos.x)
            min_p.y = min(min_p.y, pos.y)
            min_p.z = min(min_p.z, pos.z)
            max_p.x = max(max_p.x, pos.x)
            max_p.y = max(max_p.y, pos.y)
            max_p.z = max(max_p.z, pos.z)
        
        return AABB(min_p, max_p)


@dataclass
class Sphere:
    """Sphere collider"""
    center: Vec3 = field(default_factory=Vec3.zero)
    radius: float = 1.0
    
    def contains(self, point: Vec3) -> bool:
        return (point - self.center).magnitude_squared() <= self.radius**2
    
    def intersects_sphere(self, other: 'Sphere') -> bool:
        dist_sq = (other.center - self.center).magnitude_squared()
        return dist_sq <= (self.radius + other.radius)**2
    
    def intersects_aabb(self, box: AABB) -> bool:
        # Find closest point on AABB to sphere center
        closest = Vec3(
            max(box.min.x, min(self.center.x, box.max.x)),
            max(box.min.y, min(self.center.y, box.max.y)),
            max(box.min.z, min(self.center.z, box.max.z))
        )
        return (closest - self.center).magnitude_squared() <= self.radius**2


class CollisionResult:
    """Result of collision detection"""
    def __init__(self, hit: bool, normal: Vec3 = None, depth: float = 0.0, contact_point: Vec3 = None):
        self.hit = hit
        self.normal = normal or Vec3.zero()
        self.depth = depth
        self.contact_point = contact_point or Vec3.zero()


class PhysicsWorld:
    """Physics simulation world"""
    
    def __init__(self, gravity: Vec3 = Vec3(0, -9.81, 0)):
        self.gravity = gravity
        self.bodies: List[RigidBody] = []
        self.colliders: Dict[RigidBody, Sphere] = {}
    
    def add_body(self, body: RigidBody, collider: Sphere = None):
        self.bodies.append(body)
        if collider:
            self.colliders[body] = collider
    
    def remove_body(self, body: RigidBody):
        if body in self.bodies:
            self.bodies.remove(body)
        if body in self.colliders:
            del self.colliders[body]
    
    def step(self, dt: float):
        """Advance physics simulation by dt seconds"""
        # Apply gravity
        for body in self.bodies:
            if not body.is_static:
                body.apply_force(self.gravity * body.mass)
        
        # Detect and resolve collisions
        self._resolve_collisions()
        
        # Integrate motion
        for body in self.bodies:
            body.integrate(dt)
    
    def _resolve_collisions(self):
        """Simple sphere-sphere collision resolution"""
        for i, body_a in enumerate(self.bodies):
            if body_a.is_static:
                continue
            
            collider_a = self.colliders.get(body_a)
            if not collider_a:
                continue
            
            sphere_a = Sphere(body_a.position + collider_a.center, collider_a.radius)
            
            for body_b in self.bodies[i+1:]:
                collider_b = self.colliders.get(body_b)
                if not collider_b:
                    continue
                
                sphere_b = Sphere(body_b.position + collider_b.center, collider_b.radius)
                
                # Check collision
                diff = sphere_b.center - sphere_a.center
                dist = diff.magnitude()
                overlap = sphere_a.radius + sphere_b.radius - dist
                
                if overlap > 0:
                    # Collision detected
                    normal = diff.normalized() if dist > 1e-6 else Vec3.up()
                    
                    # Separate bodies
                    if body_b.is_static:
                        body_a.position = body_a.position - normal * overlap
                    elif body_a.is_static:
                        body_b.position = body_b.position + normal * overlap
                    else:
                        body_a.position = body_a.position - normal * (overlap * 0.5)
                        body_b.position = body_b.position + normal * (overlap * 0.5)
                    
                    # Calculate relative velocity
                    rel_vel = body_b.velocity - body_a.velocity
                    vel_along_normal = rel_vel.dot(normal)
                    
                    # Only resolve if moving towards each other
                    if vel_along_normal < 0:
                        continue
                    
                    # Calculate impulse
                    e = min(body_a.restitution, body_b.restitution)
                    j = -(1 + e) * vel_along_normal
                    j /= (1/body_a.mass if not body_a.is_static else 0) + \
                         (1/body_b.mass if not body_b.is_static else 0)
                    
                    impulse = normal * j
                    
                    if not body_a.is_static:
                        body_a.apply_impulse(-impulse)
                    if not body_b.is_static:
                        body_b.apply_impulse(impulse)


# =============================================================================
# CAMERA
# =============================================================================

@dataclass
class Camera:
    """3D camera with projection"""
    position: Vec3 = field(default_factory=lambda: Vec3(0, 0, 5))
    target: Vec3 = field(default_factory=Vec3.zero)
    up: Vec3 = field(default_factory=Vec3.up)
    
    fov: float = 60.0  # Degrees
    aspect: float = 16/9
    near: float = 0.1
    far: float = 1000.0
    
    def view_matrix(self) -> Mat4:
        return Mat4.look_at(self.position, self.target, self.up)
    
    def projection_matrix(self) -> Mat4:
        return Mat4.perspective(
            math.radians(self.fov), 
            self.aspect, 
            self.near, 
            self.far
        )
    
    def view_projection_matrix(self) -> Mat4:
        return self.projection_matrix() * self.view_matrix()
    
    def orbit(self, yaw: float, pitch: float, distance: float):
        """Set camera to orbit around target"""
        x = distance * math.sin(yaw) * math.cos(pitch)
        y = distance * math.sin(pitch)
        z = distance * math.cos(yaw) * math.cos(pitch)
        self.position = self.target + Vec3(x, y, z)
    
    def screen_to_ray(self, screen_x: float, screen_y: float, 
                      screen_width: int, screen_height: int) -> Tuple[Vec3, Vec3]:
        """Convert screen coordinates to ray (origin, direction)"""
        # Normalize to [-1, 1]
        ndc_x = (2 * screen_x / screen_width) - 1
        ndc_y = 1 - (2 * screen_y / screen_height)
        
        # Inverse projection
        inv_proj = self.projection_matrix().inverse()
        inv_view = self.view_matrix().inverse()
        
        if not inv_proj or not inv_view:
            return self.position, Vec3.forward()
        
        # Near and far points in NDC
        near_point = inv_view.transform_point(inv_proj.transform_point(Vec3(ndc_x, ndc_y, -1)))
        far_point = inv_view.transform_point(inv_proj.transform_point(Vec3(ndc_x, ndc_y, 1)))
        
        direction = (far_point - near_point).normalized()
        return self.position, direction


# =============================================================================
# SCENE GRAPH
# =============================================================================

@dataclass
class SceneObject:
    """Object in the 3D scene with transform hierarchy"""
    name: str
    mesh: Optional[Mesh] = None
    body: Optional[RigidBody] = None
    
    # Transform
    position: Vec3 = field(default_factory=Vec3.zero)
    rotation: Quaternion = field(default_factory=Quaternion)
    scale: Vec3 = field(default_factory=Vec3.one)
    
    # Hierarchy
    parent: Optional['SceneObject'] = None
    children: List['SceneObject'] = field(default_factory=list)
    
    # Rendering
    visible: bool = True
    cast_shadow: bool = True
    
    def local_matrix(self) -> Mat4:
        """Get local transformation matrix"""
        t = Mat4.translation(self.position.x, self.position.y, self.position.z)
        r = self.rotation.to_matrix()
        s = Mat4.scale(self.scale.x, self.scale.y, self.scale.z)
        return t * r * s
    
    def world_matrix(self) -> Mat4:
        """Get world transformation matrix (includes parent transforms)"""
        local = self.local_matrix()
        if self.parent:
            return self.parent.world_matrix() * local
        return local
    
    def add_child(self, child: 'SceneObject'):
        child.parent = self
        self.children.append(child)
    
    def remove_child(self, child: 'SceneObject'):
        if child in self.children:
            child.parent = None
            self.children.remove(child)
    
    def sync_from_physics(self):
        """Update transform from physics body"""
        if self.body:
            self.position = self.body.position
            self.rotation = self.body.rotation


class Scene:
    """Container for all 3D objects"""
    
    def __init__(self):
        self.objects: List[SceneObject] = []
        self.camera = Camera()
        self.physics = PhysicsWorld()
        
        # Lighting
        self.ambient_light: Vec3 = Vec3(0.2, 0.2, 0.2)
        self.light_direction: Vec3 = Vec3(-1, -1, -1).normalized()
        self.light_color: Vec3 = Vec3(1, 1, 1)
    
    def add(self, obj: SceneObject) -> SceneObject:
        self.objects.append(obj)
        if obj.body:
            collider = None
            if obj.mesh:
                bounds = obj.mesh.get_bounds()
                radius = ((bounds[1] - bounds[0]) * 0.5).magnitude()
                collider = Sphere(Vec3.zero(), radius)
            self.physics.add_body(obj.body, collider)
        return obj
    
    def remove(self, obj: SceneObject):
        if obj in self.objects:
            self.objects.remove(obj)
        if obj.body:
            self.physics.remove_body(obj.body)
    
    def update(self, dt: float):
        """Update physics and sync transforms"""
        self.physics.step(dt)
        for obj in self.objects:
            obj.sync_from_physics()
    
    def get_all_objects(self) -> List[SceneObject]:
        """Get all objects including children"""
        result = []
        def collect(obj):
            result.append(obj)
            for child in obj.children:
                collect(child)
        for obj in self.objects:
            collect(obj)
        return result


# =============================================================================
# SOFTWARE RENDERER
# =============================================================================

class Renderer:
    """Software 3D renderer with depth buffer"""
    
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        # Frame buffer (RGB)
        self.color_buffer: List[List[Tuple[int, int, int]]] = []
        # Depth buffer (z values)
        self.depth_buffer: List[List[float]] = []
        self.clear()
    
    def clear(self, color: Tuple[int, int, int] = (20, 20, 30)):
        """Clear buffers"""
        self.color_buffer = [[color for _ in range(self.width)] for _ in range(self.height)]
        self.depth_buffer = [[float('inf') for _ in range(self.width)] for _ in range(self.height)]
    
    def render(self, scene: Scene) -> List[List[Tuple[int, int, int]]]:
        """Render scene to color buffer"""
        self.clear()
        
        vp = scene.camera.view_projection_matrix()
        
        # Collect and sort triangles by depth (painter's algorithm)
        triangles_to_render = []
        
        for obj in scene.get_all_objects():
            if not obj.visible or not obj.mesh:
                continue
            
            world = obj.world_matrix()
            mvp = vp * world
            
            for tri in obj.mesh.triangles:
                v0, v1, v2 = tri.get_vertices(obj.mesh.vertices)
                
                # Transform vertices
                p0 = mvp.transform_point(v0.position)
                p1 = mvp.transform_point(v1.position)
                p2 = mvp.transform_point(v2.position)
                
                # Backface culling
                face_normal = tri.compute_normal(obj.mesh.vertices)
                world_normal = world.transform_direction(face_normal)
                camera_dir = (scene.camera.position - obj.position).normalized()
                if world_normal.dot(camera_dir) < 0:
                    continue
                
                # Calculate lighting
                light_intensity = max(0.0, -world_normal.dot(scene.light_direction))
                
                # Average depth for sorting
                avg_z = (p0.z + p1.z + p2.z) / 3
                
                # Add to render list
                triangles_to_render.append({
                    'p0': p0, 'p1': p1, 'p2': p2,
                    'color': v0.color,
                    'light': light_intensity,
                    'z': avg_z,
                    'ambient': scene.ambient_light
                })
        
        # Sort by depth (far to near for painter's algorithm)
        triangles_to_render.sort(key=lambda t: t['z'], reverse=True)
        
        # Rasterize triangles
        for tri_data in triangles_to_render:
            self._rasterize_triangle(tri_data)
        
        return self.color_buffer
    
    def _ndc_to_screen(self, p: Vec3) -> Tuple[int, int]:
        """Convert NDC [-1, 1] to screen coordinates"""
        x = int((p.x + 1) * 0.5 * self.width)
        y = int((1 - p.y) * 0.5 * self.height)  # Flip Y
        return x, y
    
    def _rasterize_triangle(self, tri_data: dict):
        """Rasterize a triangle with depth testing"""
        p0, p1, p2 = tri_data['p0'], tri_data['p1'], tri_data['p2']
        
        # Convert to screen space
        s0 = self._ndc_to_screen(p0)
        s1 = self._ndc_to_screen(p1)
        s2 = self._ndc_to_screen(p2)
        
        # Clip to screen
        min_x = max(0, min(s0[0], s1[0], s2[0]))
        max_x = min(self.width - 1, max(s0[0], s1[0], s2[0]))
        min_y = max(0, min(s0[1], s1[1], s2[1]))
        max_y = min(self.height - 1, max(s0[1], s1[1], s2[1]))
        
        # Calculate lighting color
        base_color = tri_data['color']
        ambient = tri_data['ambient']
        light = tri_data['light']
        
        r = int(base_color[0] * (ambient.x + light * 0.8))
        g = int(base_color[1] * (ambient.y + light * 0.8))
        b = int(base_color[2] * (ambient.z + light * 0.8))
        color = (min(255, r), min(255, g), min(255, b))
        
        # Simplified rasterization - fill bounding box with edge function test
        def edge_function(a, b, c):
            return (c[0] - a[0]) * (b[1] - a[1]) - (c[1] - a[1]) * (b[0] - a[0])
        
        area = edge_function(s0, s1, s2)
        if abs(area) < 1:  # Degenerate triangle
            return
        
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                p = (x, y)
                
                # Barycentric coordinates
                w0 = edge_function(s1, s2, p)
                w1 = edge_function(s2, s0, p)
                w2 = edge_function(s0, s1, p)
                
                # Check if inside triangle
                if area > 0:
                    inside = w0 >= 0 and w1 >= 0 and w2 >= 0
                else:
                    inside = w0 <= 0 and w1 <= 0 and w2 <= 0
                
                if inside:
                    # Interpolate depth
                    w0 /= area
                    w1 /= area
                    w2 /= area
                    z = w0 * p0.z + w1 * p1.z + w2 * p2.z
                    
                    # Depth test
                    if z < self.depth_buffer[y][x]:
                        self.depth_buffer[y][x] = z
                        self.color_buffer[y][x] = color
    
    def to_ppm(self) -> str:
        """Export to PPM image format"""
        lines = [f"P3\n{self.width} {self.height}\n255"]
        for row in self.color_buffer:
            line = " ".join(f"{r} {g} {b}" for r, g, b in row)
            lines.append(line)
        return "\n".join(lines)
    
    def to_html_canvas(self, scene: Scene) -> str:
        """Generate HTML with canvas rendering"""
        return f'''<!DOCTYPE html>
<html>
<head>
    <title>ButterflyFX 3D</title>
    <style>
        body {{ margin: 0; background: #0a0a0f; overflow: hidden; }}
        canvas {{ display: block; }}
        #info {{ position: absolute; top: 10px; left: 10px; color: #888; font-family: monospace; }}
    </style>
</head>
<body>
    <div id="info">
        Drag to orbit | Scroll to zoom | WASD to move
    </div>
    <canvas id="canvas"></canvas>
    <script>
{self._generate_js(scene)}
    </script>
</body>
</html>'''
    
    def _generate_js(self, scene: Scene) -> str:
        """Generate JavaScript 3D engine"""
        # Serialize meshes
        meshes_js = []
        for i, obj in enumerate(scene.get_all_objects()):
            if obj.mesh:
                verts = [(v.position.x, v.position.y, v.position.z, 
                         v.normal.x, v.normal.y, v.normal.z,
                         v.color[0], v.color[1], v.color[2]) for v in obj.mesh.vertices]
                tris = [(t.v0, t.v1, t.v2) for t in obj.mesh.triangles]
                
                pos = obj.position
                scale = obj.scale
                
                meshes_js.append(f'''{{
    name: "{obj.name}",
    vertices: {verts},
    triangles: {tris},
    position: [{pos.x}, {pos.y}, {pos.z}],
    scale: [{scale.x}, {scale.y}, {scale.z}],
    rotation: [0, 0, 0]
}}''')
        
        return f'''
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

// Vector/Matrix math
class Vec3 {{
    constructor(x=0, y=0, z=0) {{ this.x=x; this.y=y; this.z=z; }}
    add(v) {{ return new Vec3(this.x+v.x, this.y+v.y, this.z+v.z); }}
    sub(v) {{ return new Vec3(this.x-v.x, this.y-v.y, this.z-v.z); }}
    mul(s) {{ return new Vec3(this.x*s, this.y*s, this.z*s); }}
    dot(v) {{ return this.x*v.x + this.y*v.y + this.z*v.z; }}
    cross(v) {{ return new Vec3(this.y*v.z-this.z*v.y, this.z*v.x-this.x*v.z, this.x*v.y-this.y*v.x); }}
    length() {{ return Math.sqrt(this.x*this.x + this.y*this.y + this.z*this.z); }}
    normalize() {{ const l=this.length(); return l>0 ? this.mul(1/l) : new Vec3(); }}
}}

class Mat4 {{
    constructor() {{ this.m = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]; }}
    
    static perspective(fov, aspect, near, far) {{
        const f = 1/Math.tan(fov/2), nf = 1/(near-far);
        const m = new Mat4();
        m.m = [f/aspect,0,0,0, 0,f,0,0, 0,0,(far+near)*nf,-1, 0,0,2*far*near*nf,0];
        return m;
    }}
    
    static lookAt(eye, target, up) {{
        const f = target.sub(eye).normalize();
        const r = f.cross(up).normalize();
        const u = r.cross(f);
        const m = new Mat4();
        m.m = [r.x,u.x,-f.x,0, r.y,u.y,-f.y,0, r.z,u.z,-f.z,0, -r.dot(eye),-u.dot(eye),f.dot(eye),1];
        return m;
    }}
    
    static rotateY(a) {{
        const c=Math.cos(a), s=Math.sin(a), m=new Mat4();
        m.m = [c,0,s,0, 0,1,0,0, -s,0,c,0, 0,0,0,1];
        return m;
    }}
    
    static rotateX(a) {{
        const c=Math.cos(a), s=Math.sin(a), m=new Mat4();
        m.m = [1,0,0,0, 0,c,-s,0, 0,s,c,0, 0,0,0,1];
        return m;
    }}
    
    static translate(x,y,z) {{
        const m = new Mat4();
        m.m = [1,0,0,0, 0,1,0,0, 0,0,1,0, x,y,z,1];
        return m;
    }}
    
    static scale(x,y,z) {{
        const m = new Mat4();
        m.m = [x,0,0,0, 0,y,0,0, 0,0,z,0, 0,0,0,1];
        return m;
    }}
    
    mul(b) {{
        const a=this.m, r=new Mat4();
        for(let i=0;i<4;i++) for(let j=0;j<4;j++) {{
            r.m[i*4+j] = 0;
            for(let k=0;k<4;k++) r.m[i*4+j] += a[i*4+k]*b.m[k*4+j];
        }}
        return r;
    }}
    
    transformVec3(v) {{
        const m=this.m;
        const w = m[3]*v.x + m[7]*v.y + m[11]*v.z + m[15];
        return new Vec3(
            (m[0]*v.x + m[4]*v.y + m[8]*v.z + m[12])/w,
            (m[1]*v.x + m[5]*v.y + m[9]*v.z + m[13])/w,
            (m[2]*v.x + m[6]*v.y + m[10]*v.z + m[14])/w
        );
    }}
}}

// Scene data
const meshes = [{",".join(meshes_js)}];

// Camera
let camDist = {scene.camera.position.magnitude()};
let camYaw = 0, camPitch = 0.3;
let camTarget = new Vec3(0, 0, 0);

// Input
let isDragging = false;
let lastMouse = {{x:0, y:0}};

canvas.addEventListener('mousedown', e => {{ isDragging = true; lastMouse = {{x:e.clientX, y:e.clientY}}; }});
canvas.addEventListener('mouseup', () => isDragging = false);
canvas.addEventListener('mousemove', e => {{
    if (isDragging) {{
        camYaw += (e.clientX - lastMouse.x) * 0.01;
        camPitch += (e.clientY - lastMouse.y) * 0.01;
        camPitch = Math.max(-1.5, Math.min(1.5, camPitch));
        lastMouse = {{x:e.clientX, y:e.clientY}};
    }}
}});
canvas.addEventListener('wheel', e => {{ camDist *= e.deltaY > 0 ? 1.1 : 0.9; camDist = Math.max(2, Math.min(50, camDist)); }});

// Lighting
const lightDir = new Vec3(-1, -1, -1).normalize();
const ambient = 0.3;

// Animation time
let time = 0;

function render() {{
    ctx.fillStyle = '#0a0a0f';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    time += 0.016;
    
    // Update camera
    const camX = camDist * Math.sin(camYaw) * Math.cos(camPitch);
    const camY = camDist * Math.sin(camPitch);
    const camZ = camDist * Math.cos(camYaw) * Math.cos(camPitch);
    const camPos = new Vec3(camX, camY, camZ);
    
    const view = Mat4.lookAt(camPos, camTarget, new Vec3(0,1,0));
    const proj = Mat4.perspective(Math.PI/3, canvas.width/canvas.height, 0.1, 100);
    const vp = view.mul(proj);
    
    // Collect all triangles
    const tris = [];
    
    for (const mesh of meshes) {{
        // Build model matrix with rotation animation
        let model = Mat4.translate(mesh.position[0], mesh.position[1], mesh.position[2])
            .mul(Mat4.rotateY(mesh.rotation[1] + time * 0.5))
            .mul(Mat4.rotateX(mesh.rotation[0]))
            .mul(Mat4.scale(mesh.scale[0], mesh.scale[1], mesh.scale[2]));
        
        const mvp = model.mul(vp);
        
        for (const [i0, i1, i2] of mesh.triangles) {{
            const v0 = mesh.vertices[i0];
            const v1 = mesh.vertices[i1];
            const v2 = mesh.vertices[i2];
            
            // World positions for normal
            const wp0 = model.transformVec3(new Vec3(v0[0], v0[1], v0[2]));
            const wp1 = model.transformVec3(new Vec3(v1[0], v1[1], v1[2]));
            const wp2 = model.transformVec3(new Vec3(v2[0], v2[1], v2[2]));
            
            // Face normal
            const edge1 = wp1.sub(wp0);
            const edge2 = wp2.sub(wp0);
            const normal = edge1.cross(edge2).normalize();
            
            // Backface culling
            const toCamera = camPos.sub(wp0).normalize();
            if (normal.dot(toCamera) < 0) continue;
            
            // Clip space
            const p0 = mvp.transformVec3(new Vec3(v0[0], v0[1], v0[2]));
            const p1 = mvp.transformVec3(new Vec3(v1[0], v1[1], v1[2]));
            const p2 = mvp.transformVec3(new Vec3(v2[0], v2[1], v2[2]));
            
            // Frustum culling
            if (p0.z < -1 || p1.z < -1 || p2.z < -1) continue;
            if (p0.z > 1 || p1.z > 1 || p2.z > 1) continue;
            
            // Lighting
            const light = Math.max(0, -normal.dot(lightDir));
            const intensity = ambient + light * 0.7;
            
            const r = Math.min(255, Math.floor(v0[6] * intensity));
            const g = Math.min(255, Math.floor(v0[7] * intensity));
            const b = Math.min(255, Math.floor(v0[8] * intensity));
            
            tris.push({{
                p0, p1, p2,
                color: `rgb(${{r}},${{g}},${{b}})`,
                z: (p0.z + p1.z + p2.z) / 3
            }});
        }}
    }}
    
    // Sort by depth (painter's algorithm)
    tris.sort((a, b) => b.z - a.z);
    
    // Rasterize
    const hw = canvas.width / 2;
    const hh = canvas.height / 2;
    
    for (const tri of tris) {{
        const x0 = (tri.p0.x + 1) * hw;
        const y0 = (1 - tri.p0.y) * hh;
        const x1 = (tri.p1.x + 1) * hw;
        const y1 = (1 - tri.p1.y) * hh;
        const x2 = (tri.p2.x + 1) * hw;
        const y2 = (1 - tri.p2.y) * hh;
        
        ctx.beginPath();
        ctx.moveTo(x0, y0);
        ctx.lineTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.closePath();
        ctx.fillStyle = tri.color;
        ctx.fill();
    }}
    
    requestAnimationFrame(render);
}}

render();
'''


# =============================================================================
# CONVENIENCE BUILDERS
# =============================================================================

def create_demo_scene() -> Scene:
    """Create a demonstration scene with various 3D objects"""
    scene = Scene()
    
    # Add a helix (the ButterflyFX signature)
    helix = SceneObject(
        name="helix",
        mesh=Mesh.helix_spiral(radius=1.5, pitch=0.4, turns=3, tube_radius=0.12),
        position=Vec3(0, 0, 0)
    )
    scene.add(helix)
    
    # Add orbiting cubes
    for i in range(6):
        angle = i * math.pi / 3
        cube = SceneObject(
            name=f"cube_{i}",
            mesh=Mesh.cube(0.4, color=(
                100 + int(80 * math.sin(angle)),
                100 + int(80 * math.sin(angle + 2)),
                100 + int(80 * math.sin(angle + 4))
            )),
            position=Vec3(
                3 * math.cos(angle),
                math.sin(angle * 2),
                3 * math.sin(angle)
            )
        )
        scene.add(cube)
    
    # Add sphere
    sphere = SceneObject(
        name="sphere",
        mesh=Mesh.sphere(0.6, 12, 8, color=(34, 197, 94)),
        position=Vec3(0, 2.5, 0)
    )
    scene.add(sphere)
    
    # Set camera
    scene.camera.position = Vec3(6, 4, 6)
    scene.camera.target = Vec3(0, 0, 0)
    
    return scene
