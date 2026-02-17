"""
Dimensional Pet API Server

Endpoints:
- POST /api/pet/create - Create a new pet
- POST /api/pet/chat - Chat with the pet
- GET /api/pet/mind - Get mind map
- GET /api/pet/mind/<address> - Browse specific mind location
- GET /api/pet/memories - Get recent memories
- GET /api/pet/status - Get pet status
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from demos.dimensional_pet.pet_substrate import DimensionalPet, SPECIES

app = Flask(__name__, static_folder='static')
CORS(app)

# Global pet instance (in production, would be per-session)
current_pet: DimensionalPet = None

# Data directory for persistence
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "pets"
DATA_DIR.mkdir(parents=True, exist_ok=True)


@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('static', 'index.html')


@app.route('/api/species', methods=['GET'])
def get_species():
    """Get available pet species"""
    return jsonify({
        "species": [
            {"id": k, **v} for k, v in SPECIES.items()
        ]
    })


@app.route('/api/pet/create', methods=['POST'])
def create_pet():
    """Create a new dimensional pet"""
    global current_pet
    
    data = request.json or {}
    name = data.get('name', 'Pixel')
    species = data.get('species', 'fox')
    
    if species not in SPECIES:
        species = 'fox'
    
    current_pet = DimensionalPet(name, species)
    
    # Save immediately
    current_pet.save(str(DATA_DIR / f"{current_pet.mind.pet_id}.json"))
    
    return jsonify({
        "success": True,
        "pet": {
            "id": current_pet.mind.pet_id,
            "name": current_pet.mind.name,
            "species": current_pet.mind.species,
            "emoji": current_pet.mind.species_info["emoji"],
            "color": current_pet.mind.species_info["color"],
            "personality": current_pet.mind.species_info["trait"]
        },
        "mind_map": current_pet.get_mind_map()
    })


@app.route('/api/pet/chat', methods=['POST'])
def chat():
    """Chat with the pet"""
    global current_pet
    
    if not current_pet:
        return jsonify({"error": "No pet created yet!"}), 400
    
    data = request.json or {}
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    response = current_pet.chat(message)
    
    # Auto-save after each interaction
    current_pet.save(str(DATA_DIR / f"{current_pet.mind.pet_id}.json"))
    
    return jsonify({
        "success": True,
        **response,
        "mind_map": current_pet.get_mind_map()
    })


@app.route('/api/pet/mind', methods=['GET'])
def get_mind_map():
    """Get the pet's mind map"""
    global current_pet
    
    if not current_pet:
        return jsonify({"error": "No pet created yet!"}), 400
    
    return jsonify({
        "success": True,
        "mind_map": current_pet.get_mind_map()
    })


@app.route('/api/pet/mind/<path:address>', methods=['GET'])
def browse_mind(address):
    """Browse a specific location in the pet's mind"""
    global current_pet
    
    if not current_pet:
        return jsonify({"error": "No pet created yet!"}), 400
    
    result = current_pet.browse_mind(address)
    
    return jsonify({
        "success": True,
        "location": result
    })


@app.route('/api/pet/memories', methods=['GET'])
def get_memories():
    """Get the pet's memories"""
    global current_pet
    
    if not current_pet:
        return jsonify({"error": "No pet created yet!"}), 400
    
    category = request.args.get('category')
    limit = int(request.args.get('limit', 20))
    
    memories = current_pet.get_memories(category, limit)
    
    return jsonify({
        "success": True,
        "memories": memories,
        "total": len(memories)
    })


@app.route('/api/pet/status', methods=['GET'])
def get_status():
    """Get the pet's current status"""
    global current_pet
    
    if not current_pet:
        return jsonify({
            "has_pet": False
        })
    
    mind_map = current_pet.get_mind_map()
    
    return jsonify({
        "has_pet": True,
        "pet": {
            "id": current_pet.mind.pet_id,
            "name": current_pet.mind.name,
            "species": current_pet.mind.species,
            "emoji": current_pet.mind.species_info["emoji"],
            "color": current_pet.mind.species_info["color"]
        },
        "emotion": current_pet.mind.substrate["emotions"]["current"],
        "stats": {
            "total_memories": mind_map["total_memories"],
            "conversations": current_pet.mind.substrate["knowledge"]["conversation_count"],
            "facts_known": len(current_pet.mind.substrate["knowledge"]["user_facts"]),
            "user_name": current_pet.mind.substrate["knowledge"]["user_name"]
        }
    })


@app.route('/api/pet/search', methods=['GET'])
def search_memories():
    """Search the pet's memories"""
    global current_pet
    
    if not current_pet:
        return jsonify({"error": "No pet created yet!"}), 400
    
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    results = current_pet.mind.remember(query, limit=10)
    
    return jsonify({
        "success": True,
        "query": query,
        "results": results
    })


@app.route('/api/pet/load/<pet_id>', methods=['POST'])
def load_pet(pet_id):
    """Load a saved pet"""
    global current_pet
    
    pet_file = DATA_DIR / f"{pet_id}.json"
    if not pet_file.exists():
        return jsonify({"error": "Pet not found"}), 404
    
    current_pet = DimensionalPet.load(str(pet_file))
    
    return jsonify({
        "success": True,
        "pet": {
            "id": current_pet.mind.pet_id,
            "name": current_pet.mind.name,
            "species": current_pet.mind.species,
            "emoji": current_pet.mind.species_info["emoji"],
            "color": current_pet.mind.species_info["color"]
        },
        "mind_map": current_pet.get_mind_map()
    })


@app.route('/api/pets', methods=['GET'])
def list_pets():
    """List all saved pets"""
    pets = []
    for pet_file in DATA_DIR.glob("*.json"):
        try:
            pet = DimensionalPet.load(str(pet_file))
            pets.append({
                "id": pet.mind.pet_id,
                "name": pet.mind.name,
                "species": pet.mind.species,
                "emoji": pet.mind.species_info["emoji"]
            })
        except Exception:
            pass
    
    return jsonify({
        "success": True,
        "pets": pets
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🐾 DIMENSIONAL PET SERVER")
    print("="*60)
    print("\nStarting server at http://localhost:5050")
    print("\nEndpoints:")
    print("  GET  /                    - Web interface")
    print("  GET  /api/species         - Available species")
    print("  POST /api/pet/create      - Create a new pet")
    print("  POST /api/pet/chat        - Chat with your pet")
    print("  GET  /api/pet/mind        - View mind map")
    print("  GET  /api/pet/mind/<addr> - Browse mind location")
    print("  GET  /api/pet/memories    - View memories")
    print("  GET  /api/pet/search?q=   - Search memories")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5050, debug=True)
