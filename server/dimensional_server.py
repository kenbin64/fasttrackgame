"""
ButterflyFX Dimensional Server

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

Part of ButterflyFX Server - Open source server implementation.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

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

# Import OSI-Manifold transport layer
try:
    from helix.osi_manifold import (
        OSIHelixLayer, ManifoldAddress, ManifoldDatagram,
        OSIManifoldStack, HTTPManifoldBridge, LAYER_INFO,
        create_dimensional_server_content
    )
    OSI_MANIFOLD_AVAILABLE = True
except ImportError:
    OSI_MANIFOLD_AVAILABLE = False
    print("Warning: OSI-Manifold layer not available")

# Import Dimensional IP addressing
try:
    from helix.dimensional_ip import (
        DimensionalIP, DimensionalSubnet, DimensionalPacket,
        DimensionalRouter, ip_to_dimensional, dimensional_to_ip,
        run_all_benchmarks, ManifoldBenchmark
    )
    DIMENSIONAL_IP_AVAILABLE = True
except ImportError:
    DIMENSIONAL_IP_AVAILABLE = False
    print("Warning: Dimensional IP addressing not available")

# Import Auth API
try:
    from server.api import get_auth_api
    from server.auth import create_access_gate
    AUTH_API_AVAILABLE = True
except ImportError:
    AUTH_API_AVAILABLE = False
    print("Warning: Auth API not available")


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
    
    # Security settings
    allowed_origins: List[str] = None  # None = allow localhost only; ['*'] = allow all
    enable_security_headers: bool = True
    max_request_size: int = 10 * 1024 * 1024  # 10MB max request
    allowed_hosts: List[str] = None  # None = allow all
    
    def __post_init__(self):
        # Default to localhost-only CORS if not specified
        if self.allowed_origins is None:
            self.allowed_origins = ['http://localhost', 'https://localhost', 'http://127.0.0.1', 'https://127.0.0.1']


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
        """Send CORS headers with proper origin validation"""
        if self.server.config.enable_cors:
            origin = self.headers.get('Origin', '')
            allowed = self.server.config.allowed_origins
            
            # Check if origin is allowed
            if '*' in allowed:
                # Wildcard - allow any (less secure, only for dev)
                self.send_header('Access-Control-Allow-Origin', origin or '*')
            elif origin:
                # Check against allowed list (more secure)
                origin_base = origin.rstrip('/').lower()
                for allowed_origin in allowed:
                    if origin_base.startswith(allowed_origin.lower()):
                        self.send_header('Access-Control-Allow-Origin', origin)
                        break
            
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.send_header('Access-Control-Max-Age', '86400')  # Cache preflight for 24h
    
    def send_security_headers(self):
        """Send security headers to prevent common attacks"""
        if self.server.config.enable_security_headers:
            # Prevent clickjacking
            self.send_header('X-Frame-Options', 'SAMEORIGIN')
            # Prevent MIME-type sniffing
            self.send_header('X-Content-Type-Options', 'nosniff')
            # Enable XSS filter
            self.send_header('X-XSS-Protection', '1; mode=block')
            # Referrer policy
            self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
            # Content Security Policy (allows Three.js CDN for games)
            self.send_header('Content-Security-Policy', 
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://fonts.googleapis.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "img-src 'self' data: blob:; "
                "font-src 'self' https://fonts.gstatic.com; "
                "connect-src 'self' wss: ws:")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def _check_rate_limit(self) -> bool:
        """Check rate limit for this request. Returns False if rate limited."""
        client_ip = self.client_address[0]
        if not self.server.rate_limiter.is_allowed(client_ip):
            self.send_response(429)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Retry-After', '60')
            self.send_security_headers()
            self.end_headers()
            self.wfile.write(b'{"error": "Rate limit exceeded. Try again later."}')
            return False
        return True
    
    def _safe_int(self, value: str, default: int = 0, min_val: int = None, max_val: int = None) -> int:
        """Safely parse integer with bounds checking"""
        try:
            result = int(value)
            if min_val is not None:
                result = max(min_val, result)
            if max_val is not None:
                result = min(max_val, result)
            return result
        except (ValueError, TypeError):
            return default
    
    def _safe_float(self, value: str, default: float = 0.0, min_val: float = None, max_val: float = None) -> float:
        """Safely parse float with bounds checking"""
        try:
            result = float(value)
            if min_val is not None:
                result = max(min_val, result)
            if max_val is not None:
                result = min(max_val, result)
            # Check for infinity/NaN
            if not math.isfinite(result):
                return default
            return result
        except (ValueError, TypeError):
            return default
    
    def do_GET(self):
        # Rate limiting check
        if not self._check_rate_limit():
            return
        
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        # Check access control for protected pages
        if AUTH_API_AVAILABLE and self._requires_access_check(path):
            allowed, redirect_url, context = self._check_access(path)
            if not allowed:
                if redirect_url:
                    self._send_redirect(redirect_url)
                else:
                    self._send_access_denied(context)
                return
        
        # API routes
        if path.startswith('/api/'):
            self._handle_api(path[5:], query)
        
        # Manifold protocol
        elif path.startswith('/manifold/'):
            self._handle_manifold(path[10:], query)
        
        # Dimensional routing - the OSI-Manifold layer
        elif path.startswith('/d/') or path.startswith('/dim/'):
            self._handle_dimensional(path, query)
        
        # Auth pages (serve templates)
        elif path in ['/login', '/register', '/payment-required', '/checkout', '/dashboard', '/beta']:
            self._serve_auth_page(path, query)
        
        # Turbocharger demos
        elif path.startswith('/turbo/'):
            self._serve_turbo_demo(path)
        
        # Games (Fast Track, etc.)
        elif path.startswith('/games/'):
            self._serve_game(path, query)
        
        # Static files
        else:
            self._serve_static(path)

    
    def do_POST(self):
        # Rate limiting check
        if not self._check_rate_limit():
            return
        
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
        
        # Auth API routes
        if path.startswith('auth/') and AUTH_API_AVAILABLE:
            auth_path = path[5:]  # Remove 'auth/' prefix
            headers = dict(self.headers)
            auth_api = get_auth_api()
            response, status = auth_api.handle_get(auth_path, query, headers)
            self._send_json(response, status)
            return
        
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
            # Evaluate manifold at coordinates with input validation
            spiral = self._safe_int(query.get('spiral', ['0'])[0], 0, min_val=0, max_val=1000)
            level = self._safe_int(query.get('level', ['0'])[0], 0, min_val=0, max_val=6)
            position = self._safe_float(query.get('position', ['0'])[0], 0.0, min_val=-1e6, max_val=1e6)
            
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
        
        # =====================================================================
        # DIMENSIONAL IP ENDPOINTS - The Manifold IS the OSI Model
        # =====================================================================
        
        elif path == 'dimensional/encode':
            # Convert IP address to dimensional coordinates
            ip = query.get('ip', ['127.0.0.1'])[0]
            if DIMENSIONAL_IP_AVAILABLE:
                try:
                    result = ip_to_dimensional(ip)
                    result['client_ip'] = self.client_address[0]
                    result['client_dimensional'] = ip_to_dimensional(self.client_address[0])
                    self._send_json(result)
                except ValueError as e:
                    self._send_json({"error": str(e)}, 400)
            else:
                self._send_json({"error": "Dimensional IP not available"}, 503)
        
        elif path == 'dimensional/decode':
            # Convert dimensional coordinates back to IP
            x = self._safe_int(query.get('x', ['0'])[0], 0, min_val=0, max_val=255)
            y = self._safe_int(query.get('y', ['0'])[0], 0, min_val=0, max_val=255)
            z = self._safe_int(query.get('z', ['0'])[0], 0, min_val=0, max_val=255)
            m = self._safe_int(query.get('m', ['0'])[0], 0, min_val=0, max_val=255)
            if DIMENSIONAL_IP_AVAILABLE:
                ip = dimensional_to_ip(x, y, z, m)
                self._send_json({
                    "dimensional": {"x": x, "y": y, "z": z, "m": m},
                    "ip": ip,
                    "substrate_r": f"r={x},{y},{z},{m}",
                    "manifold_uri": f"manifold://{x}.{y}.{z}.{m}"
                })
            else:
                self._send_json({"error": "Dimensional IP not available"}, 503)
        
        elif path == 'dimensional/distance':
            # Calculate distance between two IPs in dimensional space
            ip1 = query.get('ip1', ['127.0.0.1'])[0]
            ip2 = query.get('ip2', ['127.0.0.1'])[0]
            if DIMENSIONAL_IP_AVAILABLE:
                try:
                    dim1 = DimensionalIP.from_ip(ip1)
                    dim2 = DimensionalIP.from_ip(ip2)
                    distance = dim1.distance_to(dim2)
                    same_subnet = dim1.is_same_subnet(dim2, 24)
                    self._send_json({
                        "ip1": {"ip": ip1, "dimensional": dim1.as_tuple},
                        "ip2": {"ip": ip2, "dimensional": dim2.as_tuple},
                        "distance": round(distance, 4),
                        "same_subnet_24": same_subnet,
                        "route_description": f"Direct geodesic through manifold: {distance:.2f} units"
                    })
                except ValueError as e:
                    self._send_json({"error": str(e)}, 400)
            else:
                self._send_json({"error": "Dimensional IP not available"}, 503)
        
        elif path == 'dimensional/subnet':
            # Analyze subnet in dimensional terms
            cidr = query.get('cidr', ['192.168.1.0/24'])[0]
            if DIMENSIONAL_IP_AVAILABLE:
                try:
                    subnet = DimensionalSubnet.from_cidr(cidr)
                    self._send_json({
                        "cidr": cidr,
                        "base_ip": subnet.base.to_ip(),
                        "base_dimensional": subnet.base.as_tuple,
                        "prefix_length": subnet.prefix_length,
                        "dimensionality": subnet.dimensionality,
                        "helix_level": subnet.helix_level,
                        "description": f"This subnet is a {subnet.helix_level} in manifold space ({subnet.dimensionality}D region)"
                    })
                except ValueError as e:
                    self._send_json({"error": str(e)}, 400)
            else:
                self._send_json({"error": "Dimensional IP not available"}, 503)
        
        elif path == 'dimensional/benchmark':
            # Run benchmarks for dimensional networking
            iterations = self._safe_int(query.get('iterations', ['1000'])[0], 1000, min_val=100, max_val=100000)
            if DIMENSIONAL_IP_AVAILABLE:
                benchmarks = run_all_benchmarks(iterations)
                results = {}
                for name, bench in benchmarks.items():
                    results[name] = {
                        "operation": bench.operation,
                        "iterations": bench.iterations,
                        "total_time_ms": round(bench.total_time_ms, 2),
                        "avg_latency_us": round(bench.avg_time_us, 2),
                        "min_latency_us": round(bench.min_time_us, 2),
                        "max_latency_us": round(bench.max_time_us, 2),
                        "throughput_ops_sec": round(bench.throughput, 0),
                        "bytes_processed": bench.bytes_processed,
                        "bandwidth_mbps": round(bench.bandwidth_mbps, 2) if bench.bandwidth_mbps > 0 else None
                    }
                self._send_json({
                    "benchmarks": results,
                    "summary": {
                        "total_iterations": iterations * 3,
                        "helix_available": HELIX_AVAILABLE,
                        "osi_manifold_available": OSI_MANIFOLD_AVAILABLE,
                        "server_ip": self.server.config.host,
                        "message": "THE MANIFOLD IS THE NETWORK. THE OSI MODEL IS THE GEOMETRY."
                    }
                })
            else:
                self._send_json({"error": "Dimensional IP not available"}, 503)
        
        elif path == 'dimensional/router':
            # Get router state and metrics
            if DIMENSIONAL_IP_AVAILABLE:
                if not hasattr(self.server, 'dimensional_router'):
                    self.server.dimensional_router = DimensionalRouter.from_ip_string(self.server.config.host)
                metrics = self.server.dimensional_router.get_metrics()
                self._send_json({
                    "router": metrics,
                    "osi_manifold_mapping": [
                        {"layer": l.name, "helix": info["helix"], "dimension": info["dimension"]}
                        for l, info in LAYER_INFO.items()
                    ] if OSI_MANIFOLD_AVAILABLE else None
                })
            else:
                self._send_json({"error": "Dimensional IP not available"}, 503)
        
        elif path == 'dimensional/packet':
            # Create and analyze a dimensional packet
            src = query.get('src', ['192.168.1.1'])[0]
            dst = query.get('dst', ['192.168.1.2'])[0]
            payload = query.get('payload', ['Hello, Manifold!'])[0]
            if DIMENSIONAL_IP_AVAILABLE:
                try:
                    src_dim = DimensionalIP.from_ip(src)
                    dst_dim = DimensionalIP.from_ip(dst)
                    packet = DimensionalPacket(
                        source=src_dim,
                        destination=dst_dim,
                        payload_type=DimensionalPacket.TYPE_FUNCTION,
                        payload=payload.encode('utf-8')
                    )
                    serialized = packet.serialize()
                    self._send_json({
                        "packet": {
                            "source": {"ip": src, "dimensional": src_dim.as_tuple},
                            "destination": {"ip": dst, "dimensional": dst_dim.as_tuple},
                            "route_distance": round(packet.route_distance, 4),
                            "is_local": packet.is_local,
                            "payload_size": len(payload),
                            "serialized_size": len(serialized),
                            "ttl": packet.ttl
                        },
                        "wire_format": serialized.hex(),
                        "overhead_bytes": len(serialized) - len(payload)
                    })
                except ValueError as e:
                    self._send_json({"error": str(e)}, 400)
            else:
                self._send_json({"error": "Dimensional IP not available"}, 503)
        
        else:
            self._send_json({"error": "Unknown API endpoint"}, 404)
    
    def _handle_api_post(self, path: str, body: bytes):
        """Handle POST API requests"""
        try:
            data = json.loads(body.decode('utf-8')) if body else {}
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, 400)
            return
        
        # Auth API routes
        if path.startswith('auth/') and AUTH_API_AVAILABLE:
            auth_path = path[5:]  # Remove 'auth/' prefix
            headers = dict(self.headers)
            auth_api = get_auth_api()
            response, status = auth_api.handle_post(auth_path, data, headers)
            self._send_json(response, status)
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
        """Handle manifold protocol requests with input validation"""
        
        if path == 'function':
            # Return a mathematical function description
            func_type = query.get('type', ['sin'])[0]
            
            # Validate function type (whitelist)
            allowed_functions = ['sin', 'cos', 'helix', 'linear', 'exp']
            if func_type not in allowed_functions:
                self._send_json({"error": f"Unknown function type: {func_type}. Allowed: {allowed_functions}"}, 400)
                return
            
            if func_type == 'sin':
                freq = self._safe_float(query.get('freq', ['440'])[0], 440.0, min_val=0.001, max_val=100000)
                amp = self._safe_float(query.get('amp', ['1.0'])[0], 1.0, min_val=0, max_val=1000)
                phase = self._safe_float(query.get('phase', ['0'])[0], 0.0, min_val=-1000, max_val=1000)
                
                # Send the function, not samples
                self._send_binary(ManifoldProtocol.encode_function(
                    'sin', {'freq': freq, 'amp': amp, 'phase': phase}
                ))
            
            elif func_type == 'helix':
                radius = self._safe_float(query.get('radius', ['1.0'])[0], 1.0, min_val=0.001, max_val=1000)
                pitch = self._safe_float(query.get('pitch', ['0.5'])[0], 0.5, min_val=0.001, max_val=100)
                turns = self._safe_int(query.get('turns', ['3'])[0], 3, min_val=1, max_val=1000)
                
                self._send_binary(ManifoldProtocol.encode_function(
                    'helix', {'radius': radius, 'pitch': pitch, 'turns': turns}
                ))
            
            else:
                self._send_json({"error": f"Function type '{func_type}' not implemented"}, 501)
        
        elif path == 'coordinate':
            spiral = self._safe_int(query.get('spiral', ['0'])[0], 0, min_val=0, max_val=65535)
            level = self._safe_int(query.get('level', ['0'])[0], 0, min_val=0, max_val=255)
            position = self._safe_int(query.get('position', ['0'])[0], 0, min_val=0, max_val=2**31-1)
            
            self._send_binary(ManifoldProtocol.encode_coordinate(spiral, level, position))
        
        elif path == 'transform':
            # Return identity or specified transform
            transform_type = query.get('type', ['identity'])[0]
            
            # Validate transform type (whitelist)
            allowed_transforms = ['identity', 'rotate_x', 'rotate_y', 'rotate_z', 'scale', 'translate']
            if transform_type not in allowed_transforms:
                transform_type = 'identity'
            
            if transform_type == 'identity':
                matrix = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]
            elif transform_type == 'rotate_y':
                angle = self._safe_float(query.get('angle', ['0'])[0], 0.0, min_val=-1000, max_val=1000)
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
    
    def _handle_dimensional(self, path: str, query: Dict):
        """
        Handle dimensional routing via OSI-Manifold layer.
        
        THE MODEL IS THE PAYLOAD. THE NETWORK IS THE MANIFOLD.
        
        Routes:
            /d/<level>             -> Content at (0, level, 0)
            /d/s/<spiral>/l/<level>/p/<pos>  -> Content at (spiral, level, pos)
            /dim/<level>           -> Same as /d/
        
        Returns dimensional content based on manifold coordinates.
        """
        if not OSI_MANIFOLD_AVAILABLE:
            self._send_json({
                "error": "OSI-Manifold layer not available",
                "message": "Dimensional routing requires osi_manifold.py"
            }, 503)
            return
        
        # Convert query dict format (lists) to simple dict
        simple_query = {k: v[0] if v else '' for k, v in query.items()}
        
        # Parse path to ManifoldAddress
        try:
            address = HTTPManifoldBridge.url_to_address(path, simple_query)
        except Exception as e:
            self._send_json({"error": f"Invalid dimensional path: {e}"}, 400)
            return
        
        # Get the OSI-Manifold stack (create if needed)
        if not hasattr(self.server, 'osi_stack'):
            local_addr = ManifoldAddress(0, 0, 0)
            self.server.osi_stack = OSIManifoldStack(local_addr)
            
            # Register dimensional content
            for addr, content in create_dimensional_server_content().items():
                self.server.osi_stack.router.register_content(
                    addr.spiral, addr.level, addr.position, content
                )
        
        # Route through the stack
        # Create a datagram requesting content at this address
        dg = ManifoldDatagram(
            source=ManifoldAddress(0, 0, 0),
            destination=address,
            payload_type=ManifoldDatagram.TYPE_QUERY,
            payload=b''
        )
        
        result = self.server.osi_stack.receive(dg)
        
        if result:
            # Return the dimensional content
            try:
                content = json.loads(result.decode('utf-8'))
                
                # Add routing metadata
                layer = OSIHelixLayer(min(address.level, 6))
                content['_routing'] = {
                    'address': address.to_uri(),
                    'coordinate': list(address.as_tuple),
                    'layer': {
                        'osi': layer.name,
                        'helix': LAYER_INFO[layer]['helix'],
                        'dimension': LAYER_INFO[layer]['dimension']
                    },
                    'stack_stats': {
                        l.name: self.server.osi_stack.layer_stats[l]
                        for l in OSIHelixLayer
                    }
                }
                
                self._send_json(content)
                
            except json.JSONDecodeError:
                # Binary content
                self._send_binary(result)
        else:
            # No content at this coordinate - return structure info
            layer = OSIHelixLayer(min(address.level, 6))
            self._send_json({
                'address': address.to_uri(),
                'coordinate': list(address.as_tuple),
                'layer': {
                    'osi': layer.name,
                    'helix': LAYER_INFO[layer]['helix'],
                    'dimension': LAYER_INFO[layer]['dimension'],
                    'unit': LAYER_INFO[layer]['unit'],
                    'expansion': LAYER_INFO[layer]['expansion']
                },
                'content': None,
                'message': 'No content at this coordinate. Navigate to populate.'
            })

    def _serve_auth_page(self, path: str, query: Dict):
        """Serve authentication pages (login, register, payment, dashboard)"""
        # Map paths to templates
        page_map = {
            '/login': 'login.html',
            '/register': 'login.html',  # Same page, JS handles tab
            '/payment-required': 'payment_required.html',
            '/checkout': 'payment_required.html',  # Checkout uses same template
            '/dashboard': 'dashboard.html',
            '/beta': 'beta_secret.html',
        }
        
        template_name = page_map.get(path)
        if not template_name:
            self._send_error(404, "Page not found")
            return
        
        # Look for template in web/templates/
        template_dir = Path(self.server.config.static_dir) / 'templates'
        template_path = template_dir / template_name
        
        if template_path.exists():
            # Read and serve the template
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple template variable replacement
            # (in production, use Jinja2)
            error = query.get('error', [''])[0]
            if error:
                content = content.replace('{% if error %}', '')
                content = content.replace('{% endif %}', '')
                content = content.replace('{{ error }}', error)
            else:
                # Remove error block if no error
                import re
                content = re.sub(r'\{%\s*if error\s*%\}.*?\{%\s*endif\s*%\}', '', content, flags=re.DOTALL)
            
            # Send response
            body = content.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(body))
            self.send_cors_headers()
            self.send_security_headers()
            self.end_headers()
            self.wfile.write(body)
        else:
            # Fallback to static file
            self._serve_static(path)

    def _requires_access_check(self, path: str) -> bool:
        """Check if path requires access control"""
        protected_prefixes = [
            '/dashboard',
            '/developer',
            '/beta',
            '/admin',
            '/sandbox',
            '/chat',
            '/settings',
            '/profile',
            '/marketplace/submit',
            '/api-keys',
            '/superuser',
        ]
        return any(path.startswith(p) for p in protected_prefixes)
    
    def _check_access(self, path: str):
        """Check if current request has access to path"""
        headers = dict(self.headers)
        auth_api = get_auth_api()
        gate = create_access_gate(auth_api)
        return gate(path, headers)
    
    def _send_redirect(self, url: str):
        """Send redirect response"""
        self.send_response(302)
        self.send_header('Location', url)
        self.send_cors_headers()
        self.end_headers()
    
    def _send_access_denied(self, context: dict):
        """Send access denied page"""
        reason = context.get('reason', 'access_denied')
        
        if reason == 'insufficient_tier':
            required = context.get('required_tier', 'Unknown')
            user_tier = context.get('user_tier', 'Unknown')
            html = f'''<!DOCTYPE html>
<html>
<head><title>Access Denied | ButterflyFX</title>
<style>
body {{ font-family: sans-serif; background: #0d1117; color: #c9d1d9; 
       display: flex; justify-content: center; align-items: center; 
       min-height: 100vh; margin: 0; }}
.box {{ background: #161b22; padding: 2rem; border-radius: 12px; 
        text-align: center; max-width: 400px; }}
h1 {{ color: #f85149; }}
a {{ color: #58a6ff; }}
</style></head>
<body><div class="box">
<h1>Access Denied</h1>
<p>This page requires <strong>{required}</strong> tier access.</p>
<p>Your current tier: <strong>{user_tier}</strong></p>
<p><a href="/login">Login</a> | <a href="/">Home</a></p>
</div></body></html>'''
        else:
            html = '''<!DOCTYPE html>
<html>
<head><title>Access Denied | ButterflyFX</title>
<style>
body { font-family: sans-serif; background: #0d1117; color: #c9d1d9; 
       display: flex; justify-content: center; align-items: center; 
       min-height: 100vh; margin: 0; }
.box { background: #161b22; padding: 2rem; border-radius: 12px; 
        text-align: center; max-width: 400px; }
h1 { color: #f85149; }
a { color: #58a6ff; }
</style></head>
<body><div class="box">
<h1>Access Denied</h1>
<p>You don't have permission to access this page.</p>
<p><a href="/login">Login</a> | <a href="/">Home</a></p>
</div></body></html>'''
        
        body = html.encode('utf-8')
        self.send_response(403)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.send_cors_headers()
        self.send_security_headers()
        self.end_headers()
        self.wfile.write(body)

    def _serve_turbo_demo(self, path: str):
        """Serve turbocharger demos from demos directory"""
        from urllib.parse import unquote
        
        # Map turbo routes to demo directories
        turbo_map = {
            '/turbo/convert': 'turbo_convert',
            '/turbo/bulk': 'turbo_bulk',
            '/turbo/prompt': 'prompt_forge',
            '/turbo/api': 'turbo_api',
            '/turbo/report': 'turbo_report',
            '/turbo/scrape': 'turbo_scrape',
        }
        
        # Find matching turbo app
        demo_dir = None
        for route, dir_name in turbo_map.items():
            if path.startswith(route):
                demo_dir = dir_name
                # Get remaining path after the route
                remaining = path[len(route):].lstrip('/')
                break
        
        if not demo_dir:
            self._send_error(404, "Turbo app not found")
            return
        
        # Resolve path
        demos_base = Path(__file__).parent.parent / 'demos'
        target_dir = demos_base / demo_dir
        
        if not remaining or remaining == '':
            file_path = target_dir / 'index.html'
        else:
            file_path = target_dir / unquote(remaining)
        
        # Security check
        try:
            file_path = file_path.resolve()
            target_dir = target_dir.resolve()
            file_path.relative_to(target_dir)
        except (ValueError, OSError):
            self._send_error(403, "Forbidden: Access denied")
            return
        
        if file_path.exists() and file_path.is_file():
            self._send_file(file_path)
        else:
            self._send_error(404, f"Not found: {path}")

    def _serve_game(self, path: str, query: Dict):
        """Serve game files from web/games directory"""
        from urllib.parse import unquote
        
        # Remove /games/ prefix
        remaining = path[7:]  # len('/games/') = 7
        
        if not remaining or remaining == '/':
            # Show games index
            self._send_json({
                "games": {
                    "fasttrack": {
                        "name": "Fast Track",
                        "description": "2-6 player board game with online multiplayer and AI",
                        "url": "/games/fasttrack/",
                        "players": "2-6",
                        "supports_ai": True,
                        "supports_multiplayer": True
                    }
                }
            })
            return
        
        # Parse game name and file path
        parts = remaining.strip('/').split('/', 1)
        game_name = parts[0]
        file_name = parts[1] if len(parts) > 1 else 'index.html'
        
        # Resolve path
        games_base = Path(__file__).parent.parent / 'web' / 'games'
        game_dir = games_base / game_name
        file_path = game_dir / unquote(file_name)
        
        # Security check - ensure path is within game directory
        try:
            file_path = file_path.resolve()
            game_dir = game_dir.resolve()
            file_path.relative_to(game_dir)
        except (ValueError, OSError):
            self._send_error(403, "Forbidden: Access denied")
            return
        
        if file_path.exists() and file_path.is_file():
            self._send_file(file_path)
        else:
            # Try index.html for directory requests
            if (game_dir / 'index.html').exists():
                self._send_file(game_dir / 'index.html')
            else:
                self._send_error(404, f"Game not found: {path}")

    def _serve_static(self, path: str):
        """Serve static files with secure path validation"""
        if path == '/':
            path = '/index.html'
        
        # URL decode and normalize path
        from urllib.parse import unquote
        path = unquote(path)
        
        # Remove leading slashes and normalize
        path = path.lstrip('/')
        
        # Security: reject obviously malicious patterns
        dangerous_patterns = ['..', '~', '\x00', '%00', '\\']
        if any(p in path for p in dangerous_patterns):
            self._send_error(403, "Forbidden: Invalid path")
            return
        
        # Resolve to absolute paths for comparison
        static_dir = Path(self.server.config.static_dir).resolve()
        try:
            file_path = (static_dir / path).resolve()
        except (ValueError, OSError):
            self._send_error(400, "Invalid path")
            return
        
        # CRITICAL: Ensure resolved path is under static directory
        try:
            file_path.relative_to(static_dir)
        except ValueError:
            # Path is outside static directory - path traversal attempt
            self._send_error(403, "Forbidden: Access denied")
            return
        
        if not file_path.exists():
            # Try without .html extension
            file_path = (static_dir / (path + '.html')).resolve()
            try:
                file_path.relative_to(static_dir)
            except ValueError:
                self._send_error(403, "Forbidden: Access denied")
                return
        
        if file_path.exists() and file_path.is_file():
            self._send_file(file_path)
        else:
            self._send_error(404, f"Not found: {path}")
    
    def _send_json(self, data: Dict, status: int = 200):
        """Send JSON response with security headers"""
        body = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.send_cors_headers()
        self.send_security_headers()
        self.end_headers()
        self.wfile.write(body)
    
    def _send_binary(self, data: bytes, content_type: str = 'application/octet-stream'):
        """Send binary response with security headers"""
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', len(data))
        self.send_cors_headers()
        self.send_security_headers()
        self.end_headers()
        self.wfile.write(data)
    
    def _send_file(self, path: Path):
        """Send file response with security headers"""
        content_type, _ = mimetypes.guess_type(str(path))
        content_type = content_type or 'application/octet-stream'
        
        with open(path, 'rb') as f:
            content = f.read()
        
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', len(content))
        self.send_header('Cache-Control', 'public, max-age=3600')
        self.send_cors_headers()
        self.send_security_headers()
        self.end_headers()
        self.wfile.write(content)
    
    def _send_error(self, status: int, message: str):
        """Send error response"""
        self._send_json({"error": message}, status)


# =============================================================================
# RATE LIMITER
# =============================================================================

class RateLimiter:
    """Simple in-memory rate limiter per IP address"""
    
    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests: Dict[str, List[float]] = {}
        self._cleanup_counter = 0
    
    def is_allowed(self, ip: str) -> bool:
        """Check if request from IP is allowed"""
        now = time.time()
        
        # Periodic cleanup (every 100 requests)
        self._cleanup_counter += 1
        if self._cleanup_counter >= 100:
            self._cleanup(now)
            self._cleanup_counter = 0
        
        # Get or create request list for this IP
        if ip not in self.requests:
            self.requests[ip] = []
        
        # Remove old requests outside window
        self.requests[ip] = [t for t in self.requests[ip] if now - t < self.window]
        
        # Check if under limit
        if len(self.requests[ip]) >= self.max_requests:
            return False
        
        # Record this request
        self.requests[ip].append(now)
        return True
    
    def _cleanup(self, now: float):
        """Remove expired entries"""
        expired_ips = [
            ip for ip, times in self.requests.items()
            if not times or now - max(times) > self.window * 2
        ]
        for ip in expired_ips:
            del self.requests[ip]


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
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(self.config.max_requests_per_minute)
        
        helix_status = 'Available' if HELIX_AVAILABLE else 'Minimal mode'
        print(f"""
================================================================
           BUTTERFLYFX DIMENSIONAL SERVER                       
                                                                 
   "A server that serves pure mathematical manifold             
    rather than bits and bytes"                                 
================================================================
   Host:     {self.config.host}
   Port:     {self.config.port}
   Static:   {self.config.static_dir}
   Helix:    {helix_status}
================================================================
   Endpoints:                                                   
     GET  /                      - Index page                   
     GET  /api/status            - Server status                
     GET  /api/content           - List content                 
     GET  /api/demos             - List demos                   
     GET  /api/manifold/evaluate - Evaluate manifold point      
     GET  /manifold/function     - Get math function (binary)   
     GET  /manifold/coordinate   - Get coordinate (binary)      
     POST /api/content/register  - Register content             
================================================================

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
