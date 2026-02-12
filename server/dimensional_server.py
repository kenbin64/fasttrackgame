"""
ButterflyFX Dimensional Server

A server that serves pure mathematical manifold rather than bits and bytes.
Any computer can decipher math - this is the universal language.

Features:
- Serves dimensional content (presentations, 3D, data)
- WebSocket for real-time manifold streaming
- REST API for dimensional operations
- Static file serving for web demos
- Manifold endpoint for mathematical data transmission
"""

import os
import sys
import json
import time
import hashlib
import asyncio
import mimetypes
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Callable
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import struct
import math

# Add helix to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from helix import (
        HelixKernel, ManifoldSubstrate, GenerativeManifold,
        HelixSerializer, Vec3, Mat4
    )
    HELIX_AVAILABLE = True
except ImportError:
    HELIX_AVAILABLE = False
    print("Warning: helix module not fully available, running in minimal mode")


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class ServerConfig:
    """Server configuration"""
    host: str = "0.0.0.0"
    port: int = 8080
    static_dir: str = "web"
    data_dir: str = "data"
    enable_cors: bool = True
    enable_manifold: bool = True
    enable_websocket: bool = True
    debug: bool = False
    
    # Rate limiting
    max_requests_per_minute: int = 100
    
    # Manifold settings
    manifold_precision: int = 6  # Decimal places
    manifold_cache_size: int = 1000


# =============================================================================
# MANIFOLD PROTOCOL
# =============================================================================

class ManifoldProtocol:
    """
    The Manifold Protocol: Transmit math, not bytes.
    
    Instead of sending raw data, we send mathematical descriptions
    that the client evaluates locally. This achieves:
    - Massive compression (function vs samples)
    - Resolution independence
    - Deterministic reproduction
    """
    
    # Message types
    MSG_FUNCTION = 0x01      # Mathematical function
    MSG_COORDINATE = 0x02    # Dimensional coordinate
    MSG_TRANSFORM = 0x03     # Transformation matrix
    MSG_MESH = 0x04          # 3D mesh (vertices + indices as equations)
    MSG_WAVEFORM = 0x05      # Audio waveform equation
    MSG_PRESENTATION = 0x06  # Dimensional presentation
    MSG_QUERY = 0x07         # Manifold query
    MSG_RESPONSE = 0x08      # Query response
    
    @staticmethod
    def encode_function(func_type: str, params: Dict[str, float]) -> bytes:
        """Encode a mathematical function
        
        Instead of sending sin wave samples, send:
        {"type": "sin", "freq": 440, "amp": 1.0, "phase": 0}
        
        Client evaluates: f(t) = amp * sin(2π * freq * t + phase)
        """
        data = json.dumps({"t": func_type, "p": params}).encode('utf-8')
        header = struct.pack('!BH', ManifoldProtocol.MSG_FUNCTION, len(data))
        return header + data
    
    @staticmethod
    def encode_coordinate(spiral: int, level: int, position: int) -> bytes:
        """Encode a dimensional coordinate"""
        return struct.pack('!BBBB', ManifoldProtocol.MSG_COORDINATE, spiral, level, position)
    
    @staticmethod
    def encode_transform(matrix: List[List[float]]) -> bytes:
        """Encode a 4x4 transformation matrix"""
        flat = [v for row in matrix for v in row]
        data = struct.pack('!16f', *flat)
        return struct.pack('!BH', ManifoldProtocol.MSG_TRANSFORM, len(data)) + data
    
    @staticmethod
    def decode(data: bytes) -> Dict[str, Any]:
        """Decode a manifold message"""
        if len(data) < 1:
            return {"error": "empty message"}
        
        msg_type = data[0]
        
        if msg_type == ManifoldProtocol.MSG_FUNCTION:
            length = struct.unpack('!H', data[1:3])[0]
            payload = json.loads(data[3:3+length].decode('utf-8'))
            return {"type": "function", "func": payload["t"], "params": payload["p"]}
        
        elif msg_type == ManifoldProtocol.MSG_COORDINATE:
            return {
                "type": "coordinate",
                "spiral": data[1],
                "level": data[2],
                "position": data[3]
            }
        
        elif msg_type == ManifoldProtocol.MSG_TRANSFORM:
            length = struct.unpack('!H', data[1:3])[0]
            values = struct.unpack('!16f', data[3:3+length])
            matrix = [list(values[i:i+4]) for i in range(0, 16, 4)]
            return {"type": "transform", "matrix": matrix}
        
        return {"error": "unknown message type", "type_code": msg_type}


# =============================================================================
# DIMENSIONAL CONTENT REGISTRY
# =============================================================================

class ContentRegistry:
    """Registry of dimensional content (presentations, 3D scenes, data)"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.content: Dict[str, Dict] = {}
        self._scan_content()
    
    def _scan_content(self):
        """Scan data directory for content"""
        if not self.data_dir.exists():
            return
        
        for path in self.data_dir.rglob('*.json'):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                content_id = path.stem
                self.content[content_id] = {
                    "path": str(path),
                    "data": data,
                    "modified": path.stat().st_mtime
                }
            except Exception as e:
                print(f"Warning: Could not load {path}: {e}")
    
    def get(self, content_id: str) -> Optional[Dict]:
        """Get content by ID"""
        return self.content.get(content_id, {}).get("data")
    
    def list_all(self) -> List[Dict]:
        """List all registered content"""
        return [
            {"id": k, "modified": v["modified"]}
            for k, v in self.content.items()
        ]
    
    def register(self, content_id: str, data: Dict):
        """Register new content"""
        self.content[content_id] = {
            "path": None,
            "data": data,
            "modified": time.time()
        }


# =============================================================================
# REQUEST HANDLER
# =============================================================================

class DimensionalRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for dimensional server"""
    
    server_version = "ButterflyFX/1.0"
    
    def log_message(self, format, *args):
        if self.server.config.debug:
            super().log_message(format, *args)
    
    def send_cors_headers(self):
        if self.server.config.enable_cors:
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        # API routes
        if path.startswith('/api/'):
            self._handle_api(path[5:], query)
        
        # Manifold protocol
        elif path.startswith('/manifold/'):
            self._handle_manifold(path[10:], query)
        
        # Static files
        else:
            self._serve_static(path)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        # Read body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''
        
        if path.startswith('/api/'):
            self._handle_api_post(path[5:], body)
        elif path.startswith('/manifold/'):
            self._handle_manifold_post(path[10:], body)
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def _handle_api(self, path: str, query: Dict):
        """Handle API requests"""
        
        if path == 'status':
            self._send_json({
                "status": "online",
                "version": "1.0.0",
                "helix_available": HELIX_AVAILABLE,
                "manifold_enabled": self.server.config.enable_manifold,
                "uptime": time.time() - self.server.start_time
            })
        
        elif path == 'content':
            self._send_json({
                "content": self.server.registry.list_all()
            })
        
        elif path.startswith('content/'):
            content_id = path[8:]
            data = self.server.registry.get(content_id)
            if data:
                self._send_json(data)
            else:
                self._send_json({"error": "Content not found"}, 404)
        
        elif path == 'kernel/new':
            # Create a new helix kernel
            if HELIX_AVAILABLE:
                kernel = HelixKernel()
                kernel_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
                self.server.kernels[kernel_id] = kernel
                self._send_json({"kernel_id": kernel_id, "state": kernel.state.name})
            else:
                self._send_json({"error": "Helix not available"}, 503)
        
        elif path == 'manifold/evaluate':
            # Evaluate manifold at coordinates
            spiral = int(query.get('spiral', [0])[0])
            level = int(query.get('level', [0])[0])
            position = float(query.get('position', [0])[0])
            
            if HELIX_AVAILABLE:
                manifold = GenerativeManifold()
                point = manifold.evaluate(spiral, level, position)
                self._send_json({
                    "coordinate": {"spiral": spiral, "level": level, "position": position},
                    "point": {"x": point.x, "y": point.y, "z": point.z},
                    "type": point.type_name,
                    "value": point.value
                })
            else:
                # Fallback calculation
                theta = level * (2 * math.pi / 7)
                r = spiral + 1
                x = r * math.cos(theta)
                y = position * 0.5
                z = r * math.sin(theta)
                self._send_json({
                    "coordinate": {"spiral": spiral, "level": level, "position": position},
                    "point": {"x": x, "y": y, "z": z}
                })
        
        elif path == 'demos':
            # List available demos
            demos = []
            web_dir = Path(self.server.config.static_dir)
            if web_dir.exists():
                for f in web_dir.glob('*.html'):
                    demos.append({
                        "name": f.stem,
                        "url": f"/{f.name}",
                        "size": f.stat().st_size
                    })
            self._send_json({"demos": demos})
        
        else:
            self._send_json({"error": "Unknown API endpoint"}, 404)
    
    def _handle_api_post(self, path: str, body: bytes):
        """Handle POST API requests"""
        try:
            data = json.loads(body.decode('utf-8')) if body else {}
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, 400)
            return
        
        if path == 'content/register':
            content_id = data.get('id')
            content_data = data.get('data')
            if content_id and content_data:
                self.server.registry.register(content_id, content_data)
                self._send_json({"status": "registered", "id": content_id})
            else:
                self._send_json({"error": "Missing id or data"}, 400)
        
        elif path.startswith('kernel/') and '/set' in path:
            # Set kernel level value
            kernel_id = path.split('/')[1]
            kernel = self.server.kernels.get(kernel_id)
            if kernel:
                level = data.get('level', 0)
                key = data.get('key', '')
                value = data.get('value')
                kernel.set(level, key, value)
                self._send_json({"status": "ok", "level": level, "key": key})
            else:
                self._send_json({"error": "Kernel not found"}, 404)
        
        else:
            self._send_json({"error": "Unknown endpoint"}, 404)
    
    def _handle_manifold(self, path: str, query: Dict):
        """Handle manifold protocol requests"""
        
        if path == 'function':
            # Return a mathematical function description
            func_type = query.get('type', ['sin'])[0]
            
            if func_type == 'sin':
                freq = float(query.get('freq', [440])[0])
                amp = float(query.get('amp', [1.0])[0])
                phase = float(query.get('phase', [0])[0])
                
                # Send the function, not samples
                self._send_binary(ManifoldProtocol.encode_function(
                    'sin', {'freq': freq, 'amp': amp, 'phase': phase}
                ))
            
            elif func_type == 'helix':
                radius = float(query.get('radius', [1.0])[0])
                pitch = float(query.get('pitch', [0.5])[0])
                turns = int(query.get('turns', [3])[0])
                
                self._send_binary(ManifoldProtocol.encode_function(
                    'helix', {'radius': radius, 'pitch': pitch, 'turns': turns}
                ))
            
            else:
                self._send_json({"error": f"Unknown function type: {func_type}"}, 400)
        
        elif path == 'coordinate':
            spiral = int(query.get('spiral', [0])[0])
            level = int(query.get('level', [0])[0])
            position = int(query.get('position', [0])[0])
            
            self._send_binary(ManifoldProtocol.encode_coordinate(spiral, level, position))
        
        elif path == 'transform':
            # Return identity or specified transform
            transform_type = query.get('type', ['identity'])[0]
            
            if transform_type == 'identity':
                matrix = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]
            elif transform_type == 'rotate_y':
                angle = float(query.get('angle', [0])[0])
                c, s = math.cos(angle), math.sin(angle)
                matrix = [[c,0,s,0], [0,1,0,0], [-s,0,c,0], [0,0,0,1]]
            else:
                matrix = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]
            
            self._send_binary(ManifoldProtocol.encode_transform(matrix))
        
        else:
            self._send_json({"error": "Unknown manifold endpoint"}, 404)
    
    def _handle_manifold_post(self, path: str, body: bytes):
        """Handle manifold protocol POST (binary data)"""
        try:
            decoded = ManifoldProtocol.decode(body)
            
            if "error" in decoded:
                self._send_json(decoded, 400)
            else:
                # Process the manifold message
                self._send_json({
                    "status": "received",
                    "decoded": decoded
                })
        
        except Exception as e:
            self._send_json({"error": str(e)}, 500)
    
    def _serve_static(self, path: str):
        """Serve static files"""
        if path == '/':
            path = '/index.html'
        
        # Security: prevent path traversal
        path = path.lstrip('/')
        if '..' in path:
            self._send_error(403, "Forbidden")
            return
        
        # Check in static directory
        static_dir = Path(self.server.config.static_dir)
        file_path = static_dir / path
        
        if not file_path.exists():
            # Try without .html extension
            file_path = static_dir / (path + '.html')
        
        if file_path.exists() and file_path.is_file():
            self._send_file(file_path)
        else:
            self._send_error(404, f"Not found: {path}")
    
    def _send_json(self, data: Dict, status: int = 200):
        """Send JSON response"""
        body = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(body)
    
    def _send_binary(self, data: bytes, content_type: str = 'application/octet-stream'):
        """Send binary response"""
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', len(data))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(data)
    
    def _send_file(self, path: Path):
        """Send file response"""
        content_type, _ = mimetypes.guess_type(str(path))
        content_type = content_type or 'application/octet-stream'
        
        with open(path, 'rb') as f:
            content = f.read()
        
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', len(content))
        self.send_header('Cache-Control', 'public, max-age=3600')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(content)
    
    def _send_error(self, status: int, message: str):
        """Send error response"""
        self._send_json({"error": message}, status)


# =============================================================================
# DIMENSIONAL SERVER
# =============================================================================

class DimensionalServer(HTTPServer):
    """The ButterflyFX Dimensional Server"""
    
    def __init__(self, config: ServerConfig = None):
        self.config = config or ServerConfig()
        super().__init__((self.config.host, self.config.port), DimensionalRequestHandler)
        
        self.start_time = time.time()
        self.registry = ContentRegistry(self.config.data_dir)
        self.kernels: Dict[str, 'HelixKernel'] = {}
        
        print(f"""
╔═══════════════════════════════════════════════════════════════╗
║           BUTTERFLYFX DIMENSIONAL SERVER                       ║
║                                                                 ║
║   "A server that serves pure mathematical manifold             ║
║    rather than bits and bytes"                                 ║
╠═══════════════════════════════════════════════════════════════╣
║   Host:     {self.config.host:<47} ║
║   Port:     {self.config.port:<47} ║
║   Static:   {self.config.static_dir:<47} ║
║   Helix:    {'Available' if HELIX_AVAILABLE else 'Minimal mode':<47} ║
╠═══════════════════════════════════════════════════════════════╣
║   Endpoints:                                                   ║
║     GET  /                      → Index page                   ║
║     GET  /api/status            → Server status                ║
║     GET  /api/content           → List content                 ║
║     GET  /api/demos             → List demos                   ║
║     GET  /api/manifold/evaluate → Evaluate manifold point      ║
║     GET  /manifold/function     → Get math function (binary)   ║
║     GET  /manifold/coordinate   → Get coordinate (binary)      ║
║     POST /api/content/register  → Register content             ║
╚═══════════════════════════════════════════════════════════════╝

   Server running at http://{self.config.host}:{self.config.port}/
   Press Ctrl+C to stop.
""")
    
    def run_forever(self):
        """Run the server"""
        try:
            super().serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.shutdown()


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='ButterflyFX Dimensional Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python dimensional_server.py
  python dimensional_server.py --port 8888
  python dimensional_server.py --host 127.0.0.1 --debug
        '''
    )
    
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind (default: 8080)')
    parser.add_argument('--static', default='web', help='Static files directory (default: web)')
    parser.add_argument('--data', default='data', help='Data directory (default: data)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--no-cors', action='store_true', help='Disable CORS headers')
    
    args = parser.parse_args()
    
    config = ServerConfig(
        host=args.host,
        port=args.port,
        static_dir=args.static,
        data_dir=args.data,
        debug=args.debug,
        enable_cors=not args.no_cors
    )
    
    server = DimensionalServer(config)
    server.run_forever()


if __name__ == '__main__':
    main()
