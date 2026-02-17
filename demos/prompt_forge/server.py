"""
Prompt Forge Server - Serve the interactive demo and API

Run with: python -m demos.prompt_forge.server
"""

import json
from pathlib import Path
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

from .prompt_manifold import PromptManifold, ManifoldPosition

# Initialize
app = Flask(__name__, static_folder='.')
CORS(app)

# Global manifold instance
manifold = PromptManifold()

# Static files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# API Endpoints

@app.route('/api/navigate', methods=['POST'])
def navigate():
    """Navigate to a position on the manifold"""
    data = request.json
    position = ManifoldPosition(
        purpose=float(data.get('purpose', 2.5)),
        style=float(data.get('style', 1.5)),
        length=float(data.get('length', 2.0))
    )
    topic = data.get('topic', 'your topic')
    
    prompt = manifold.navigate(position, topic)
    
    return jsonify({
        'success': True,
        'prompt': prompt.invoke(),
        'address': prompt.address,
        'position': position.to_dict()
    })

@app.route('/api/presets', methods=['GET'])
def get_presets():
    """List all preset regions"""
    return jsonify({
        'success': True,
        'presets': manifold.list_regions()
    })

@app.route('/api/preset/<name>', methods=['POST'])
def goto_preset(name):
    """Jump to a preset region"""
    data = request.json or {}
    topic = data.get('topic', 'your topic')
    
    try:
        prompt = manifold.goto_region(name, topic)
        return jsonify({
            'success': True,
            'prompt': prompt.invoke(),
            'address': prompt.address,
            'position': prompt.position.to_dict()
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/interpolate', methods=['POST'])
def interpolate():
    """Interpolate between two positions"""
    data = request.json
    
    start = ManifoldPosition(**data['start'])
    end = ManifoldPosition(**data['end'])
    t = float(data.get('t', 0.5))
    topic = data.get('topic', 'your topic')
    
    prompt = manifold.interpolate(start, end, t, topic)
    
    return jsonify({
        'success': True,
        'prompt': prompt.invoke(),
        'address': prompt.address,
        'position': prompt.position.to_dict(),
        't': t
    })

@app.route('/api/state', methods=['GET'])
def get_state():
    """Get current manifold state"""
    return jsonify({
        'success': True,
        'state': manifold.to_state()
    })


def main():
    """Run the server"""
    import os
    port = int(os.environ.get('PORT', 8088))
    
    print("=" * 50)
    print("⚡ PROMPT FORGE")
    print("=" * 50)
    print(f"Open: http://localhost:{port}")
    print()
    print("Navigate the prompt manifold!")
    print("Position IS the prompt. No database. No search.")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=port, debug=True)


if __name__ == '__main__':
    main()
