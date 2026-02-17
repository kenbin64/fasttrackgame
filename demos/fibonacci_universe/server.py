"""
Fibonacci Universe Server

Serves the Fibonacci-Dimensional substrate with visualization.
"""

import os
import sys
import json
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fibonacci_substrate import FibonacciUniverse, FibonacciLevel, FIBONACCI
from manifold_bridge import ManifoldDimensionalBridge, DimensionalManifold
from information_manifolds import ManifoldInformationSystem, ManifoldType
from conical_helix import ConicalHelix, DimensionalWave

app = Flask(__name__, static_folder='static')
CORS(app)

# Create the universe
universe = FibonacciUniverse("ButterflyFX Fibonacci")

# Create the manifold bridge
manifold_bridge = ManifoldDimensionalBridge()

# Create the information manifold system
info_system = ManifoldInformationSystem()

# Create the conical helix
conical_helix = ConicalHelix(num_dimensions=7)
dimensional_wave = DimensionalWave(num_cycles=7)


# ========== STATIC FILES ==========

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('static', 'index.html')


# ========== FIBONACCI STRUCTURE ==========

@app.route('/api/fibonacci')
def get_fibonacci():
    """Get the Fibonacci dimensional structure"""
    return jsonify(universe.get_fibonacci_structure())


@app.route('/api/stats')
def get_stats():
    """Get universe statistics"""
    return jsonify(universe.stats())


# ========== NAVIGATION ==========

@app.route('/api/current')
def get_current():
    """Get current location"""
    return jsonify({
        "point": universe.current().to_dict(),
        "path": universe.path(),
        "path_string": universe.path_string(),
        "inner_points": universe.list_inner()
    })


@app.route('/api/down/<point_id>')
def go_down(point_id: str):
    """Navigate into an inner point"""
    point = universe.down(point_id)
    if point:
        return jsonify({
            "success": True,
            "point": point.to_dict(),
            "path": universe.path(),
            "message": f"Entered {point.address}"
        })
    return jsonify({"success": False, "error": f"Point {point_id} not found"}), 404


@app.route('/api/up')
def go_up():
    """Navigate up to parent"""
    point = universe.up()
    if point:
        return jsonify({
            "success": True,
            "point": point.to_dict(),
            "path": universe.path(),
            "message": f"Returned to {point.address}"
        })
    return jsonify({"success": False, "error": "Already at root"}), 400


# ========== INVOCATION ==========

@app.route('/api/invoke', methods=['POST'])
def invoke_path():
    """
    Invoke a path - manifest points from the void.
    POST body: { "path": "car.engine.block" }
    """
    data = request.get_json()
    path = data.get("path", "")
    
    if not path:
        return jsonify({"error": "Path required"}), 400
    
    point, time_ns, steps = universe.invoke(path)
    
    return jsonify({
        "success": True,
        "path": path,
        "point": point.to_dict() if point else None,
        "time_ns": time_ns,
        "depth": len(steps),
        "steps": steps,
        "complexity": f"O({len(steps)})",
        "message": f"Invoked {len(steps)} points in {time_ns}ns"
    })


@app.route('/api/create', methods=['POST'])
def create_point():
    """
    Create a new point in current location.
    POST body: { "id": "mypoint", "name": "My Point", "value": {...} }
    """
    data = request.get_json()
    point_id = data.get("id")
    name = data.get("name", point_id)
    value = data.get("value")
    
    if not point_id:
        return jsonify({"error": "Point ID required"}), 400
    
    current = universe.current()
    
    if current.is_point:
        return jsonify({
            "error": "Cannot create inside POINT level - it is irreducible",
            "level": "POINT",
            "fibonacci": 1
        }), 400
    
    point = current.create_inner(point_id, name=name, value=value)
    universe._index[point_id] = point
    
    return jsonify({
        "success": True,
        "point": point.to_dict(),
        "message": f"Created and invoked {point.address}"
    })


# ========== DEMOS ==========

@app.route('/api/demo/o_d')
def demo_o_d():
    """Demonstrate O(d) complexity"""
    return jsonify(universe.demonstrate_o_d())


@app.route('/api/demo/emergence')
def demo_emergence():
    """Demonstrate Fibonacci emergence"""
    return jsonify(universe.demonstrate_fibonacci_emergence())


@app.route('/api/demo/void')
def demo_void():
    """Demonstrate the void vs invocation concept"""
    current = universe.current()
    
    # Create potential points (described but not invoked)
    potential_ids = ["potential_1", "potential_2", "potential_3"]
    for pid in potential_ids:
        if pid not in current._inner:
            current._inner[pid] = FibonacciUniverse._create_potential_point(pid, current.level)
    
    return jsonify({
        "current": current.to_dict(max_depth=0),
        "invoked_count": current.inner_count(),
        "potential_count": current.potential_described(),
        "explanation": (
            "The void contains infinite potential points. "
            "Only INVOCATION manifests them into existence. "
            f"Here we have {current.inner_count()} invoked (real) points "
            f"and {current.potential_described()} potential (void) points."
        ),
        "invoked_points": [p.to_dict(max_depth=0) for p in current.list_invoked_inner()],
        "concept": {
            "invoked": "EXISTS - has been observed/created",
            "potential": "VOID - waits to be invoked",
            "fibonacci": "Structure emerges through Fibonacci levels"
        }
    })


def _create_potential_point(pid: str, parent_level: int):
    """Create a potential (uninvoked) point"""
    from fibonacci_substrate import FibonacciPoint
    inner_level = parent_level - 1 if parent_level > 0 else 0
    return FibonacciPoint(
        id=pid,
        level=FibonacciLevel(inner_level),
        name=f"Potential {pid}",
        invoked=False  # NOT invoked = in the void
    )

# Add this method to universe
FibonacciUniverse._create_potential_point = staticmethod(_create_potential_point)


# ========== MANIFOLD API ==========

@app.route('/api/manifold')
def list_manifolds():
    """List all available manifolds"""
    return jsonify({
        "manifolds": manifold_bridge.list_all(),
        "explanation": manifold_bridge.explain_dimensional_embedding()
    })


@app.route('/api/manifold/<name>')
def get_manifold(name: str):
    """Get a specific manifold"""
    manifold = manifold_bridge.get(name)
    if manifold:
        return jsonify(manifold.to_dict())
    return jsonify({"error": f"Unknown manifold: {name}"}), 404


@app.route('/api/manifold/<name>/mesh')
def get_manifold_mesh(name: str):
    """Get manifold mesh data for 3D rendering"""
    resolution = request.args.get('resolution', 30, type=int)
    manifold = manifold_bridge.get(name)
    if manifold:
        mesh = manifold.to_mesh(resolution=resolution)
        mesh["manifold"] = manifold.to_dict()
        return jsonify(mesh)
    return jsonify({"error": f"Unknown manifold: {name}"}), 404


@app.route('/api/manifold/<name>/sample')
def sample_manifold(name: str):
    """Sample a point on the manifold"""
    u = request.args.get('u', 0.5, type=float)
    v = request.args.get('v', 0.5, type=float)
    return jsonify(manifold_bridge.sample_point(name, u, v))


@app.route('/api/manifold/saddle/demo')
def demo_saddle():
    """Demonstrate z = xy dimensional transformation"""
    samples = []
    
    # Sample key points
    test_points = [
        (0, 0, "origin"),
        (1, 1, "positive quadrant"),
        (1, -1, "negative z"),
        (-1, 1, "negative z"),
        (-1, -1, "positive z"),
        (0.5, 0.5, "quarter"),
        (2, 0.5, "stretched")
    ]
    
    for x, y, desc in test_points:
        z = x * y
        samples.append({
            "intrinsic": {"x": x, "y": y},
            "embedded": {"x": x, "y": y, "z": z},
            "description": desc,
            "equation": f"z = {x} × {y} = {z}"
        })
    
    return jsonify({
        "manifold": "saddle",
        "equation": "z = xy",
        "name": "Hyperbolic Paraboloid",
        "dimensional_insight": {
            "intrinsic": "2D - addressed by (x, y)",
            "embedded": "3D - positioned at (x, y, z)",
            "transformation": "z = x·y",
            "fibonacci_levels": "PLANE (F=5) → VOLUME (F=8)"
        },
        "samples": samples,
        "geometry": {
            "saddle_point": "At origin (0,0,0)",
            "positive_regions": "Quadrants I and III",
            "negative_regions": "Quadrants II and IV",
            "curvature": "Negative (saddle)"
        },
        "dimensional_principle": (
            "The 2D surface z=xy is a PLANE (Fibonacci level 4) "
            "embedded in a VOLUME (Fibonacci level 5). "
            "The equation IS the dimensional relationship."
        )
    })


# ========== MAIN ==========

if __name__ == '__main__':
    # Create static directory
    os.makedirs('static', exist_ok=True)
    
    print("=" * 60)
    print("FIBONACCI UNIVERSE SERVER")
    print("=" * 60)
    print(f"Root: {universe.root.address}")
    print(f"Current: {universe.current().address}")
    print(f"Invoked points: {len(universe._index)}")
    print()
    print("API Endpoints:")
    print("  GET  /api/fibonacci     - Fibonacci structure")
    print("  GET  /api/current       - Current location")
    print("  GET  /api/down/<id>     - Navigate into point")
    print("  GET  /api/up            - Navigate up")
    print("  POST /api/invoke        - Invoke path from void")
    print("  POST /api/create        - Create new point")
    print("  GET  /api/demo/o_d      - O(d) complexity demo")
    print("  GET  /api/demo/emergence - Fibonacci emergence demo")
    print()
    print("Starting server at http://localhost:5052")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5052, debug=False)
