"""
Dimensional Universe API Server

Navigate infinite dimensional space in your browser.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from demos.dimensional_universe.universe_substrate import DimensionalUniverse

app = Flask(__name__, static_folder='static')
CORS(app)

# Global universe instance
universe: DimensionalUniverse = None

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "universes"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_universe():
    global universe
    if universe is None:
        universe = DimensionalUniverse("ButterflyFX")
    return universe


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/api/universe', methods=['GET'])
def get_universe_state():
    """Get current universe visualization data"""
    u = get_universe()
    return jsonify({
        "success": True,
        **u.get_visualization_data()
    })


@app.route('/api/universe/stats', methods=['GET'])
def get_stats():
    """Get universe statistics"""
    u = get_universe()
    return jsonify({
        "success": True,
        "stats": u.stats()
    })


@app.route('/api/drill/down/<point_id>', methods=['POST'])
def drill_down(point_id):
    """Drill down into a point - enter its inner universe"""
    u = get_universe()
    result = u.drill_down(point_id)
    
    if result:
        return jsonify({
            "success": True,
            "message": f"Entered {result.name}",
            **u.get_visualization_data()
        })
    else:
        return jsonify({"success": False, "error": "Cannot drill down"}), 400


@app.route('/api/drill/up', methods=['POST'])
def drill_up():
    """Drill up - current universe becomes a point in higher dimension"""
    u = get_universe()
    result = u.drill_up()
    
    if result:
        return jsonify({
            "success": True,
            "message": f"Ascended to {result.name}",
            **u.get_visualization_data()
        })
    else:
        return jsonify({"success": False, "error": "Already at top dimension"}), 400


@app.route('/api/goto/<point_id>', methods=['POST'])
def goto_point(point_id):
    """O(1) jump to any point"""
    u = get_universe()
    result = u.goto(point_id)
    
    if result:
        return jsonify({
            "success": True,
            "message": f"Jumped to {result.name}",
            **u.get_visualization_data()
        })
    else:
        return jsonify({"success": False, "error": "Point not found"}), 404


@app.route('/api/create', methods=['POST'])
def create_point():
    """Create a new point in current dimension"""
    u = get_universe()
    data = request.json or {}
    
    name = data.get('name', 'New Point')
    coords = data.get('coordinates')
    properties = data.get('properties', {})
    
    if coords:
        coords = tuple(coords)
    
    point = u.create(name=name, coordinates=coords, properties=properties)
    
    return jsonify({
        "success": True,
        "created": {
            "id": point.id,
            "name": point.name,
            "address": point.address,
            "dimension": point.dimension
        },
        **u.get_visualization_data()
    })


@app.route('/api/create/complex', methods=['POST'])
def create_complex():
    """Create a complex object with nested structure"""
    u = get_universe()
    data = request.json or {}
    
    name = data.get('name', 'Complex Object')
    structure = data.get('structure', {})
    coords = data.get('coordinates')
    
    if coords:
        coords = tuple(coords)
    
    point = u.create_with_structure(name=name, structure=structure, coordinates=coords)
    
    return jsonify({
        "success": True,
        "created": {
            "id": point.id,
            "name": point.name,
            "address": point.address,
            "total_points": point.total_points()
        },
        **u.get_visualization_data()
    })


@app.route('/api/point/<point_id>', methods=['GET'])
def get_point(point_id):
    """Get details of a specific point"""
    u = get_universe()
    point = u.get_point(point_id)
    
    if point:
        return jsonify({
            "success": True,
            "point": point
        })
    else:
        return jsonify({"success": False, "error": "Point not found"}), 404


@app.route('/api/search', methods=['GET'])
def search():
    """Search points by name"""
    u = get_universe()
    query = request.args.get('q', '')
    results = u.search(query)
    
    return jsonify({
        "success": True,
        "query": query,
        "results": results
    })


@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset to a fresh universe"""
    global universe
    universe = DimensionalUniverse("ButterflyFX")
    return jsonify({
        "success": True,
        "message": "Universe reset",
        **universe.get_visualization_data()
    })


@app.route('/api/invoke', methods=['POST'])
def invoke_path():
    """
    Dimensional invocation - O(1) per level, NOT tree traversal.
    
    Example: {"path": "car.engine.alternator.gasket"}
    
    Returns timing proof that each level is O(1).
    """
    u = get_universe()
    data = request.json or {}
    path = data.get('path', '')
    
    if not path:
        return jsonify({"error": "No path provided"}), 400
    
    result = u.invoke_path(path)
    
    return jsonify({
        "success": True,
        **result
    })


@app.route('/api/invoke/<path:address>', methods=['GET'])
def invoke_get(address):
    """GET version of invoke for easy testing"""
    u = get_universe()
    result = u.invoke_path(address)
    return jsonify({
        "success": True,
        **result
    })


@app.route('/api/explain', methods=['GET'])
def explain_dimensional():
    """Explain why dimensional is not a tree"""
    u = get_universe()
    return jsonify({
        "success": True,
        "explanation": u.why_not_tree(),
        "demonstration": {
            "tree_complexity": "O(n) per level, O(n^d) total",
            "dimensional_complexity": "O(1) per level, O(d) total",
            "example_path": "car.engine.alternator.gasket.fiber.element.molecule.atom",
            "tree_worst_case": "O(n^8) if each level has n children",
            "dimensional_case": "O(8) always, regardless of universe size"
        }
    })


@app.route('/api/dimensions', methods=['GET'])
def list_dimensions():
    """
    List all dimensions with entry points.
    
    You don't have to start at the top. Enter at ANY level.
    - Scientist: enters at atomic level (-5)
    - Architect: enters at building level (2)
    - City planner: enters at world level (3)
    """
    u = get_universe()
    return jsonify({
        "success": True,
        **u.list_dimensions()
    })


@app.route('/api/enter', methods=['POST'])
def enter_dimension():
    """
    Enter a dimension directly - O(1) entry at any level.
    
    No need to traverse from the top. Start where you need to be.
    
    Body: {"dimension": -5, "point_id": "optional_specific_point"}
    """
    u = get_universe()
    data = request.json or {}
    dimension = data.get('dimension', 0)
    point_id = data.get('point_id')
    
    result = u.enter_dimension(dimension, point_id)
    
    if result:
        return jsonify({
            "success": True,
            "message": f"Entered dimension {dimension} ({u.dimension_name(dimension)}) at {result.name}",
            "entered": {
                "id": result.id,
                "name": result.name,
                "dimension": result.dimension,
                "address": result.address
            },
            **u.get_visualization_data()
        })
    else:
        return jsonify({
            "success": False,
            "error": f"No points exist at dimension {dimension} yet"
        }), 404


@app.route('/api/find', methods=['GET'])
def find_at_dimension():
    """
    Find all points at a specific dimension.
    
    Example: GET /api/find?dim=-5 → all atoms
    Example: GET /api/find?dim=2 → all entities (cars, buildings, people)
    """
    u = get_universe()
    dimension = int(request.args.get('dim', 0))
    name_filter = request.args.get('name')
    
    points = u.invoke_at_dimension(dimension, name_filter)
    
    return jsonify({
        "success": True,
        "dimension": dimension,
        "dimension_name": u.dimension_name(dimension),
        "points": [
            {
                "id": p.id,
                "name": p.name,
                "address": p.address,
                "inner_count": p.inner_count()
            }
            for p in points[:50]  # Limit results
        ],
        "total": len(points),
        "insight": f"Direct access to dimension {dimension}. No traversal from root needed."
    })


@app.route('/api/demo/deep', methods=['POST'])
def create_deep_structure():
    """Create a deep structure to demonstrate dimensional addressing"""
    u = get_universe()
    
    # Create: Car → Engine → Alternator → Gasket → Fiber → Element → Molecule → Atom
    car = u.create_with_structure(
        name="Car",
        structure={
            "type": "vehicle",
            "children": {
                "engine": {
                    "type": "mechanical",
                    "children": {
                        "alternator": {
                            "type": "electrical",
                            "children": {
                                "gasket": {
                                    "type": "seal",
                                    "children": {
                                        "fiber": {
                                            "type": "material",
                                            "children": {
                                                "element": {
                                                    "type": "chemical",
                                                    "children": {
                                                        "molecule": {
                                                            "type": "molecular",
                                                            "children": {
                                                                "atom": {
                                                                    "type": "atomic",
                                                                    "nucleus": True
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        coordinates=(0, 0, 0)
    )
    
    # Now invoke the full path to demonstrate O(d) access
    invoke_result = u.invoke_path("Car.engine.alternator.gasket.fiber.element.molecule.atom")
    
    return jsonify({
        "success": True,
        "message": "Created deep structure: Car → Engine → Alternator → Gasket → Fiber → Element → Molecule → Atom",
        "created": {
            "id": car.id,
            "name": car.name,
            "total_nested_points": car.total_points()
        },
        "invocation_proof": invoke_result,
        "key_insight": "8 levels traversed in O(8) time, not O(n^8)",
        **u.get_visualization_data()
    })


@app.route('/api/demo/populate', methods=['POST'])
def populate_demo():
    """Populate with demo objects"""
    u = get_universe()
    
    # Create some interesting objects
    objects_created = []
    
    # A building
    building = u.create_with_structure(
        name="Crystal Tower",
        structure={
            "type": "building",
            "material": "glass",
            "children": {
                "floors": [{"type": "floor", "number": i} for i in range(1, 11)],
                "elevator": {"type": "transport", "speed": "fast"},
                "lobby": {"type": "room", "area": "grand"}
            }
        },
        coordinates=(5, 0, 0)
    )
    objects_created.append(building.name)
    
    # A vehicle
    vehicle = u.create_with_structure(
        name="Hover Craft",
        structure={
            "type": "vehicle",
            "propulsion": "anti-gravity",
            "children": {
                "hull": {"type": "shell", "material": "titanium"},
                "engines": [
                    {"type": "thruster", "position": "rear"},
                    {"type": "thruster", "position": "left"},
                    {"type": "thruster", "position": "right"}
                ],
                "cockpit": {
                    "type": "control_center",
                    "children": {
                        "console": {"type": "interface"},
                        "seat": {"type": "furniture"}
                    }
                }
            }
        },
        coordinates=(-4, 0, 2)
    )
    objects_created.append(vehicle.name)
    
    # A tree of life
    tree = u.create_with_structure(
        name="World Tree",
        structure={
            "type": "organic",
            "species": "yggdrasil",
            "children": {
                "trunk": {"type": "wood", "age": "eternal"},
                "branches": [
                    {"type": "branch", "direction": d} 
                    for d in ["north", "south", "east", "west", "up"]
                ],
                "roots": {
                    "type": "root_system",
                    "depth": "infinite",
                    "children": {
                        "taproot": {"type": "main_root"},
                        "network": {"type": "mycorrhizal"}
                    }
                }
            }
        },
        coordinates=(0, 0, -5)
    )
    objects_created.append(tree.name)
    
    # A data structure
    data_crystal = u.create_with_structure(
        name="Data Crystal",
        structure={
            "type": "storage",
            "capacity": "infinite",
            "children": {
                "memories": {"type": "data_bank", "records": 1000000},
                "index": {"type": "lookup_table", "complexity": "O(1)"},
                "interface": {"type": "neural_link"}
            }
        },
        coordinates=(3, 0, 4)
    )
    objects_created.append(data_crystal.name)
    
    return jsonify({
        "success": True,
        "created": objects_created,
        **u.get_visualization_data()
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("DIMENSIONAL UNIVERSE SERVER")
    print("Navigate infinite dimensions in your browser")
    print("="*60)
    print("\nStarting at http://localhost:5051")
    print("\nEvery point contains a universe.")
    print("Every universe is a point.")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5051, debug=True)
