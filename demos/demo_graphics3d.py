"""
Demo: True 3D Graphics Engine

Mathematically correct 3D with:
- Vector/Matrix math (not fake shading)
- Proper perspective projection
- Depth buffer z-ordering
- Physics simulation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helix.graphics3d import (
    Vec3, Mat4, Quaternion,
    Mesh, SceneObject, Scene, Renderer,
    create_demo_scene
)
import math


def demo_vector_math():
    """Demonstrate vector operations"""
    print("=" * 60)
    print("VECTOR MATHEMATICS")
    print("=" * 60)
    
    a = Vec3(1, 2, 3)
    b = Vec3(4, 5, 6)
    
    print(f"\n  a = {a.to_tuple()}")
    print(f"  b = {b.to_tuple()}")
    
    print(f"\n  a + b = {(a + b).to_tuple()}")
    print(f"  a - b = {(a - b).to_tuple()}")
    print(f"  a × 2 = {(a * 2).to_tuple()}")
    
    print(f"\n  a · b (dot)   = {a.dot(b):.4f}")
    print(f"  a × b (cross) = {a.cross(b).to_tuple()}")
    
    print(f"\n  |a| (length)  = {a.magnitude():.4f}")
    print(f"  â (unit)      = {tuple(round(x, 4) for x in a.normalized().to_tuple())}")
    
    print(f"\n  angle(a, b)   = {math.degrees(a.angle_to(b)):.2f}°")


def demo_matrix_transforms():
    """Demonstrate matrix transformations"""
    print("\n" + "=" * 60)
    print("MATRIX TRANSFORMATIONS")
    print("=" * 60)
    
    point = Vec3(1, 0, 0)
    print(f"\n  Original point: {point.to_tuple()}")
    
    # Translation
    t = Mat4.translation(5, 0, 0)
    translated = t.transform_point(point)
    print(f"  + Translate(5,0,0): {translated.to_tuple()}")
    
    # Rotation
    r = Mat4.rotation_y(math.pi / 2)  # 90 degrees
    rotated = r.transform_point(point)
    print(f"  + Rotate Y 90°: {tuple(round(x, 4) for x in rotated.to_tuple())}")
    
    # Scale
    s = Mat4.scale(2, 2, 2)
    scaled = s.transform_point(point)
    print(f"  + Scale(2,2,2): {scaled.to_tuple()}")
    
    # Combined transformation
    combined = t * r * s
    result = combined.transform_point(point)
    print(f"  + All combined: {tuple(round(x, 4) for x in result.to_tuple())}")


def demo_quaternion_rotation():
    """Demonstrate quaternion rotation (no gimbal lock)"""
    print("\n" + "=" * 60)
    print("QUATERNION ROTATION")
    print("=" * 60)
    
    # Create rotation around arbitrary axis
    axis = Vec3(1, 1, 0).normalized()
    angle = math.radians(45)
    
    q = Quaternion.from_axis_angle(axis, angle)
    print(f"\n  Rotation axis: {tuple(round(x, 4) for x in axis.to_tuple())}")
    print(f"  Rotation angle: 45°")
    print(f"  Quaternion: w={q.w:.4f}, x={q.x:.4f}, y={q.y:.4f}, z={q.z:.4f}")
    
    # Rotate a vector
    v = Vec3(1, 0, 0)
    rotated = q.rotate_vector(v)
    print(f"\n  Original vector: {v.to_tuple()}")
    print(f"  Rotated vector: {tuple(round(x, 4) for x in rotated.to_tuple())}")
    
    # SLERP interpolation
    print("\n  SLERP interpolation (smooth rotation blend):")
    q1 = Quaternion.from_axis_angle(Vec3.up(), 0)
    q2 = Quaternion.from_axis_angle(Vec3.up(), math.pi)
    
    for t in [0, 0.25, 0.5, 0.75, 1.0]:
        q_interp = q1.slerp(q2, t)
        angle_deg = 2 * math.acos(q_interp.w) * 180 / math.pi
        print(f"    t={t:.2f}: angle ≈ {angle_deg:.1f}°")


def demo_perspective_projection():
    """Demonstrate perspective vs orthographic projection"""
    print("\n" + "=" * 60)
    print("PERSPECTIVE PROJECTION")
    print("=" * 60)
    
    # Create perspective matrix
    fov = math.radians(60)
    aspect = 16/9
    near = 0.1
    far = 100.0
    
    persp = Mat4.perspective(fov, aspect, near, far)
    
    # Points at different depths
    points = [
        Vec3(0, 0, -2),   # Close
        Vec3(0, 0, -5),   # Medium
        Vec3(0, 0, -10),  # Far
    ]
    
    print(f"\n  FOV: 60°, Aspect: {aspect:.2f}, Near: {near}, Far: {far}")
    print("\n  Same X,Y at different Z depths:")
    
    for p in points:
        projected = persp.transform_point(p)
        print(f"    z={p.z:4.0f} → screen x,y = ({projected.x:.4f}, {projected.y:.4f})")
    
    print("\n  Notice: closer points appear larger (proper foreshortening)")


def demo_mesh_generation():
    """Demonstrate procedural mesh generation"""
    print("\n" + "=" * 60)
    print("PROCEDURAL MESH GENERATION")
    print("=" * 60)
    
    # Generate primitives
    cube = Mesh.cube(1.0)
    sphere = Mesh.sphere(1.0, segments=16, rings=12)
    cylinder = Mesh.cylinder(1.0, 2.0, segments=16)
    helix = Mesh.helix_spiral(radius=1.0, pitch=0.5, turns=3, tube_radius=0.1)
    
    print(f"\n  Cube:     {len(cube.vertices):4} vertices, {len(cube.triangles):4} triangles")
    print(f"  Sphere:   {len(sphere.vertices):4} vertices, {len(sphere.triangles):4} triangles")
    print(f"  Cylinder: {len(cylinder.vertices):4} vertices, {len(cylinder.triangles):4} triangles")
    print(f"  Helix:    {len(helix.vertices):4} vertices, {len(helix.triangles):4} triangles")
    
    # Show bounds
    min_b, max_b = helix.get_bounds()
    print(f"\n  Helix bounds:")
    print(f"    min: ({min_b.x:.2f}, {min_b.y:.2f}, {min_b.z:.2f})")
    print(f"    max: ({max_b.x:.2f}, {max_b.y:.2f}, {max_b.z:.2f})")


def demo_scene_graph():
    """Demonstrate scene hierarchy"""
    print("\n" + "=" * 60)
    print("SCENE GRAPH")
    print("=" * 60)
    
    scene = create_demo_scene()
    
    print(f"\n  Objects in scene: {len(scene.objects)}")
    for obj in scene.objects:
        pos = obj.position
        print(f"    - {obj.name}: pos=({pos.x:.1f}, {pos.y:.1f}, {pos.z:.1f})")
    
    print(f"\n  Camera:")
    print(f"    Position: {scene.camera.position.to_tuple()}")
    print(f"    Target: {scene.camera.target.to_tuple()}")
    print(f"    FOV: {scene.camera.fov}°")


def demo_render_to_html():
    """Generate interactive HTML with true 3D"""
    print("\n" + "=" * 60)
    print("RENDERING TO HTML")
    print("=" * 60)
    
    scene = create_demo_scene()
    renderer = Renderer(800, 600)
    
    html = renderer.to_html_canvas(scene)
    
    output_path = os.path.join(os.path.dirname(__file__), "..", "web", "graphics3d_demo.html")
    output_path = os.path.abspath(output_path)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n  Generated: {output_path}")
    print(f"  Size: {len(html):,} bytes")
    print("\n  Features:")
    print("    ✓ True 3D vector/matrix math")
    print("    ✓ Perspective projection (mathematically correct)")
    print("    ✓ Backface culling")
    print("    ✓ Depth sorting (painter's algorithm)")
    print("    ✓ Directional lighting")
    print("    ✓ Interactive camera (drag to orbit, scroll to zoom)")


def main():
    print("\n" + "=" * 60)
    print("  BUTTERFLYFX TRUE 3D GRAPHICS ENGINE")
    print("  Mathematically Correct • Structure • Physics • Depth")
    print("=" * 60)
    
    demo_vector_math()
    demo_matrix_transforms()
    demo_quaternion_rotation()
    demo_perspective_projection()
    demo_mesh_generation()
    demo_scene_graph()
    demo_render_to_html()
    
    print("\n" + "=" * 60)
    print("  ✓ All demonstrations complete!")
    print("  Open web/graphics3d_demo.html in a browser")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
