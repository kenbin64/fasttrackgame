"""
ButterflyFx Server - HTTP and Socket Interface

═══════════════════════════════════════════════════════════════════
                    COMPUTATION SERVER
═══════════════════════════════════════════════════════════════════

The ButterflyFx Core acts as a computation server, accepting
requests over HTTP and raw sockets. All requests go through the
Core→Kernel pipeline.

ENDPOINTS:

    HTTP:
        POST /process     - Process data into substrates
        POST /compute     - Execute computations
        POST /project     - Apply lens projections
        POST /transform   - Apply delta transformations
        GET  /reference   - Resolve SRL references
        POST /render      - Render results
        GET  /status      - Server status
        WS   /stream      - WebSocket for streaming

    Socket:
        Raw TCP socket for direct substrate operations
        Protocol: length-prefixed JSON messages

═══════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
import json
import socket
import struct
import threading
import socketserver
import traceback
from typing import Any, Dict, List, Optional, Callable, Tuple, TYPE_CHECKING
from dataclasses import dataclass, field
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import queue

if TYPE_CHECKING:
    from .api import ButterflyFx, FxResult


__all__ = [
    'FxServer',
    'FxHTTPHandler',
    'FxSocketHandler',
]


# ═══════════════════════════════════════════════════════════════════
# HTTP SERVER
# ═══════════════════════════════════════════════════════════════════

class FxHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for ButterflyFx API."""
    
    # Reference to the ButterflyFx instance
    fx: 'ButterflyFx' = None
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass
    
    def send_json(self, data: Dict, status: int = 200):
        """Send JSON response."""
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)
    
    def send_error_json(self, message: str, code: int = 400):
        """Send error response."""
        self.send_json({
            'success': False,
            'error': message,
            'code': code
        }, status=code)
    
    def read_json_body(self) -> Optional[Dict]:
        """Read and parse JSON request body."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length)
                return json.loads(body.decode('utf-8'))
            return {}
        except Exception as e:
            return None
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/status':
            self._handle_status()
        elif path == '/reference':
            query = parse_qs(parsed.query)
            uri = query.get('uri', [''])[0]
            self._handle_reference(uri)
        elif path == '/':
            self._handle_info()
        else:
            self.send_error_json('Not found', 404)
    
    def do_POST(self):
        """Handle POST requests."""
        path = urlparse(self.path).path
        body = self.read_json_body()
        
        if body is None:
            self.send_error_json('Invalid JSON body', 400)
            return
        
        try:
            if path == '/process':
                self._handle_process(body)
            elif path == '/compute':
                self._handle_compute(body)
            elif path == '/project':
                self._handle_project(body)
            elif path == '/transform':
                self._handle_transform(body)
            elif path == '/render':
                self._handle_render(body)
            elif path == '/batch':
                self._handle_batch(body)
            else:
                self.send_error_json('Not found', 404)
        except Exception as e:
            self.send_error_json(str(e), 500)
    
    def _handle_status(self):
        """Return server status."""
        self.send_json({
            'success': True,
            'status': 'running',
            'version': '2.0.0',
            'cached': len(self.fx._cache),
            'config': {
                'host': self.fx.config.server_host,
                'port': self.fx.config.server_port,
                'strict_mode': self.fx.config.strict_mode,
                'caching': self.fx.config.enable_caching
            }
        })
    
    def _handle_info(self):
        """Return API info."""
        self.send_json({
            'name': 'ButterflyFx Core API',
            'version': '2.0.0',
            'description': 'Mathematical substrate computation engine',
            'endpoints': {
                'GET /status': 'Server status',
                'POST /process': 'Process data into substrate',
                'POST /compute': 'Execute computation',
                'POST /project': 'Apply lens projection',
                'POST /transform': 'Apply delta transformation',
                'GET /reference?uri=': 'Resolve SRL reference',
                'POST /render': 'Render result',
                'POST /batch': 'Batch operations'
            }
        })
    
    def _handle_process(self, body: Dict):
        """Process data through the Core."""
        data = body.get('data')
        if data is None:
            self.send_error_json('Missing "data" field', 400)
            return
        
        result = self.fx.process(data)
        self.send_json({
            'success': True,
            'truth': result.truth,
            'truth_hex': f'0x{result.truth:016X}',
            'execution_time_ns': result.execution_time_ns
        })
    
    def _handle_compute(self, body: Dict):
        """Execute a computation."""
        from .api import Computation
        
        operation = body.get('operation')
        inputs = body.get('inputs', [])
        
        if not operation:
            self.send_error_json('Missing "operation" field', 400)
            return
        
        comp = Computation(operation=operation, inputs=inputs)
        result = self.fx.compute(comp)
        
        self.send_json({
            'success': True,
            'value': result.value,
            'truth': result.truth,
            'truth_hex': f'0x{result.truth:016X}',
            'execution_time_ns': result.execution_time_ns
        })
    
    def _handle_project(self, body: Dict):
        """Apply a lens projection."""
        data = body.get('data')
        projection_expr = body.get('projection')
        
        if data is None or projection_expr is None:
            self.send_error_json('Missing "data" or "projection" field', 400)
            return
        
        # For security, we only allow simple expressions
        # Format: "x OP value" where OP is XOR, AND, OR, ROT, +, -, *, /
        try:
            projection = self._parse_projection(projection_expr)
        except Exception as e:
            self.send_error_json(f'Invalid projection: {e}', 400)
            return
        
        result = self.fx.project(data, projection)
        
        self.send_json({
            'success': True,
            'value': result.value,
            'truth': result.truth,
            'truth_hex': f'0x{result.truth:016X}'
        })
    
    def _parse_projection(self, expr: str) -> Callable[[int], int]:
        """Parse a simple projection expression into a callable."""
        MASK = 0xFFFFFFFFFFFFFFFF
        
        # Handle identity
        if expr.strip().lower() == 'x':
            return lambda x: x
        
        # Parse "x OP value"
        parts = expr.replace('  ', ' ').strip().split(' ')
        if len(parts) != 3 or parts[0].lower() != 'x':
            raise ValueError("Expression must be 'x OP value'")
        
        op = parts[1].upper()
        value = int(parts[2], 0)  # Supports 0x hex
        
        if op == 'XOR' or op == '^':
            return lambda x, v=value: (x ^ v) & MASK
        elif op == 'AND' or op == '&':
            return lambda x, v=value: (x & v) & MASK
        elif op == 'OR' or op == '|':
            return lambda x, v=value: (x | v) & MASK
        elif op == 'ROT' or op == '<<<':
            return lambda x, v=value: ((x << (v % 64)) | (x >> (64 - (v % 64)))) & MASK
        elif op == '+':
            return lambda x, v=value: (x + v) & MASK
        elif op == '-':
            return lambda x, v=value: (x - v) & MASK
        elif op == '*':
            return lambda x, v=value: (x * v) & MASK
        elif op == '/':
            if value == 0:
                raise ValueError("Division by zero")
            return lambda x, v=value: (x // v) & MASK
        else:
            raise ValueError(f"Unknown operator: {op}")
    
    def _handle_transform(self, body: Dict):
        """Apply a delta transformation."""
        source = body.get('source')
        derived = body.get('derived')
        delta = body.get('delta')
        
        if source is None or derived is None or delta is None:
            self.send_error_json('Missing required fields', 400)
            return
        
        result = self.fx.transform(source, derived, delta)
        
        self.send_json({
            'success': True,
            'truth': result.truth,
            'truth_hex': f'0x{result.truth:016X}'
        })
    
    def _handle_reference(self, uri: str):
        """Resolve an SRL reference."""
        if not uri:
            self.send_error_json('Missing "uri" parameter', 400)
            return
        
        try:
            result = self.fx.reference(uri)
            self.send_json({
                'success': True,
                'uri': uri,
                'truth': result.truth,
                'truth_hex': f'0x{result.truth:016X}'
            })
        except Exception as e:
            self.send_error_json(str(e), 404)
    
    def _handle_render(self, body: Dict):
        """Render a result."""
        data = body.get('data')
        format_type = body.get('format', 'auto')
        
        if data is None:
            self.send_error_json('Missing "data" field', 400)
            return
        
        rendered = self.fx.render(data, format=format_type)
        
        self.send_json({
            'success': True,
            'rendered': rendered,
            'format': format_type
        })
    
    def _handle_batch(self, body: Dict):
        """Handle batch operations."""
        operations = body.get('operations', [])
        results = []
        
        for op in operations:
            op_type = op.get('type')
            try:
                if op_type == 'process':
                    r = self.fx.process(op.get('data'))
                    results.append({'success': True, 'truth': r.truth})
                elif op_type == 'compute':
                    from .api import Computation
                    c = Computation(op.get('operation'), op.get('inputs', []))
                    r = self.fx.compute(c)
                    results.append({'success': True, 'truth': r.truth})
                else:
                    results.append({'success': False, 'error': f'Unknown type: {op_type}'})
            except Exception as e:
                results.append({'success': False, 'error': str(e)})
        
        self.send_json({
            'success': True,
            'results': results,
            'count': len(results)
        })


# ═══════════════════════════════════════════════════════════════════
# SOCKET SERVER
# ═══════════════════════════════════════════════════════════════════

class FxSocketHandler(socketserver.BaseRequestHandler):
    """Raw socket handler for direct substrate operations."""
    
    fx: 'ButterflyFx' = None
    
    def handle(self):
        """Handle a socket connection."""
        while True:
            try:
                # Read length-prefixed message
                length_bytes = self._recv_exact(4)
                if not length_bytes:
                    break
                
                length = struct.unpack('!I', length_bytes)[0]
                if length > 1024 * 1024:  # 1MB max
                    break
                
                message_bytes = self._recv_exact(length)
                if not message_bytes:
                    break
                
                message = json.loads(message_bytes.decode('utf-8'))
                response = self._handle_message(message)
                
                # Send response
                response_bytes = json.dumps(response).encode('utf-8')
                self.request.sendall(struct.pack('!I', len(response_bytes)))
                self.request.sendall(response_bytes)
                
            except Exception as e:
                break
    
    def _recv_exact(self, n: int) -> Optional[bytes]:
        """Receive exactly n bytes."""
        data = b''
        while len(data) < n:
            chunk = self.request.recv(n - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def _handle_message(self, message: Dict) -> Dict:
        """Handle a socket message."""
        action = message.get('action')
        
        try:
            if action == 'process':
                result = self.fx.process(message.get('data'))
                return {
                    'success': True,
                    'truth': result.truth
                }
            elif action == 'compute':
                from .api import Computation
                comp = Computation(message.get('operation'), message.get('inputs', []))
                result = self.fx.compute(comp)
                return {
                    'success': True,
                    'value': result.value,
                    'truth': result.truth
                }
            elif action == 'ping':
                return {'success': True, 'pong': True}
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


# ═══════════════════════════════════════════════════════════════════
# COMBINED SERVER
# ═══════════════════════════════════════════════════════════════════

class FxServer:
    """
    Combined HTTP and Socket server for ButterflyFx.
    
    Runs both servers in parallel for maximum compatibility.
    """
    
    def __init__(
        self, 
        fx: 'ButterflyFx', 
        host: str = '127.0.0.1', 
        port: int = 8088
    ):
        self.fx = fx
        self.host = host
        self.port = port
        self.socket_port = port + 1
        
        self._http_server: Optional[HTTPServer] = None
        self._socket_server: Optional[socketserver.TCPServer] = None
        self._running = False
        self._threads: List[threading.Thread] = []
    
    def run(self):
        """Start both servers (blocking)."""
        self._running = True
        
        # Set up HTTP handler
        class Handler(FxHTTPHandler):
            fx = self.fx
        
        # Set up Socket handler
        class SocketHandler(FxSocketHandler):
            fx = self.fx
        
        try:
            # Create HTTP server
            self._http_server = HTTPServer((self.host, self.port), Handler)
            
            # Create Socket server
            self._socket_server = socketserver.ThreadingTCPServer(
                (self.host, self.socket_port), 
                SocketHandler
            )
            self._socket_server.allow_reuse_address = True
            
            print(f"ButterflyFx Server starting...")
            print(f"  HTTP:   http://{self.host}:{self.port}")
            print(f"  Socket: {self.host}:{self.socket_port}")
            print(f"  Press Ctrl+C to stop")
            
            # Run socket server in thread
            socket_thread = threading.Thread(
                target=self._socket_server.serve_forever,
                daemon=True
            )
            socket_thread.start()
            self._threads.append(socket_thread)
            
            # Run HTTP server in main thread
            self._http_server.serve_forever()
            
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.stop()
    
    def stop(self):
        """Stop both servers."""
        self._running = False
        
        if self._http_server:
            self._http_server.shutdown()
            self._http_server = None
        
        if self._socket_server:
            self._socket_server.shutdown()
            self._socket_server = None
    
    def is_running(self) -> bool:
        return self._running
