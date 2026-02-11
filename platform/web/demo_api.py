"""
ButterflyFx Demo API - Real Image Compression Demo

This is a PROOF OF CONCEPT that demonstrates:
1. Upload an image
2. Convert to pattern-based substrate
3. Show compression ratio
4. Reconstruct the image from substrate
5. Compare original vs reconstructed

This MUST work with real images or we have no product.
"""

from flask import Flask, request, jsonify, send_file, render_template
from PIL import Image
import numpy as np
import io
import base64
import sys
import os
import uuid

# Add parent directories to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import after path is set
try:
    from kernel.pattern_substrate import PatternSubstrateEncoder, PatternRegion
    from kernel.universal_substrate_database import ImageSubstrate
    print("✓ Imports successful")
except Exception as e:
    print(f"✗ Import error: {e}")
    import traceback
    traceback.print_exc()

app = Flask(__name__, template_folder='templates', static_folder='static')

def calculate_storage_size(regions):
    """
    Calculate actual storage size of substrate.
    
    Storage = sum of all pattern region data
    """
    total_bytes = 0
    
    for region in regions:
        # Bounding box: 4 integers (x, y, width, height) = 16 bytes
        total_bytes += 16
        
        # Pattern type: 1 byte
        total_bytes += 1
        
        # Color positions: each color is 3 bytes (RGB)
        total_bytes += len(region.color_positions) * 3
        
        # Direction (for gradients): 1 byte
        total_bytes += 1
    
    return total_bytes


@app.route('/')
def demo_page():
    """Serve the demo page."""
    return render_template('landing/demo.html')


@app.route('/api/demo/compress', methods=['POST'])
def compress_image():
    """
    Compress image to substrate and return statistics.
    
    Returns:
        {
            'success': bool,
            'original_size': int (bytes),
            'substrate_size': int (bytes),
            'compression_ratio': float,
            'num_patterns': int,
            'pattern_breakdown': {
                'solid': int,
                'linear': int,
                'bilinear': int,
                'complex': int
            },
            'substrate_id': str (for reconstruction)
        }
    """
    try:
        # Get uploaded image
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        
        # Load image
        img = Image.open(file.stream)
        img_array = np.array(img)
        
        # Calculate original size
        original_size = img_array.nbytes
        
        # Encode to substrate (smaller blocks = better quality, lower compression)
        # block_size=16 gives better quality, block_size=64 gives higher compression
        encoder = PatternSubstrateEncoder(block_size=16)
        regions = encoder.encode_image(img_array)
        
        # Calculate substrate storage size
        substrate_size = calculate_storage_size(regions)
        
        # Calculate compression ratio
        compression_ratio = original_size / substrate_size if substrate_size > 0 else 0
        
        # Count pattern types
        pattern_breakdown = {
            'solid': 0,
            'linear': 0,
            'bilinear': 0,
            'complex': 0
        }
        
        for region in regions:
            if region is None:
                pattern_breakdown['complex'] += 1
            else:
                pattern_type = str(region.pattern_type).split('.')[-1].lower()
                if pattern_type in pattern_breakdown:
                    pattern_breakdown[pattern_type] += 1
        
        # Create substrate
        height, width = img_array.shape[:2]
        substrate = ImageSubstrate(regions, width, height)

        # Generate unique ID for this substrate
        substrate_id = str(uuid.uuid4())

        # Store for reconstruction (in-memory for demo)
        if not hasattr(app, 'substrate_cache'):
            app.substrate_cache = {}
        app.substrate_cache[substrate_id] = substrate
        
        return jsonify({
            'success': True,
            'original_size': original_size,
            'substrate_size': substrate_size,
            'compression_ratio': round(compression_ratio, 2),
            'num_patterns': len(regions),
            'pattern_breakdown': pattern_breakdown,
            'substrate_id': substrate_id,
            'image_dimensions': {
                'width': width,
                'height': height
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/demo/reconstruct/<substrate_id>', methods=['GET'])
def reconstruct_image(substrate_id):
    """
    Reconstruct image from substrate.
    
    Returns:
        Image file (PNG)
    """
    try:
        # Get substrate from cache
        if not hasattr(app, 'substrate_cache') or substrate_id not in app.substrate_cache:
            return jsonify({'success': False, 'error': 'Substrate not found'}), 404
        
        substrate = app.substrate_cache[substrate_id]
        
        # Reconstruct image
        reconstructed = substrate.render()
        
        # Convert to PIL Image
        img = Image.fromarray(reconstructed.astype('uint8'))
        
        # Save to bytes
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)

