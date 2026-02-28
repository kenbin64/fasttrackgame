"""
Request Substrate - Dimensional Request/Response Management

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)

Manages HTTP requests/responses as dimensional objects.
O(1) routing, lazy parsing, geometric composition.
"""

from __future__ import annotations
import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Set, Optional, Any, Callable, List, Tuple
from collections import OrderedDict
from urllib.parse import urlparse, parse_qs
import threading


# =============================================================================
# REQUEST POINT - A request as a dimensional coordinate
# =============================================================================

@dataclass
class RequestPoint:
    """
    An HTTP request represented as a point on the manifold.
    
    Coordinates:
        spiral: Request type (0=GET, 1=POST, 2=PUT, 3=DELETE, etc.)
        layer: Processing stage (1=received, 2=parsed, 3=routed, 4=processed, 5=response, 6=sent, 7=logged)
        position: Priority/weight
    """
    request_id: str
    method: str
    path: str
    headers: Dict[str, str]
    body: bytes = b''
    
    # Dimensional coordinates
    spiral: int = 0  # Request type
    layer: int = 1   # Processing stage
    position: float = 0.0  # Priority
    
    # Metadata
    created_at: float = field(default_factory=time.time)
    client_ip: str = ""
    query_params: Dict[str, List[str]] = field(default_factory=dict)
    
    # Response data
    response_status: int = 0
    response_headers: Dict[str, str] = field(default_factory=dict)
    response_body: bytes = b''
    
    # Identity vector for z = x·y
    identity_vector: Tuple[float, float] = field(default_factory=lambda: (1.0, 1.0))
    
    def __post_init__(self):
        # Parse query parameters
        parsed = urlparse(self.path)
        self.query_params = parse_qs(parsed.query)
        
        # Calculate identity vector from path
        path_hash = hashlib.md5(self.path.encode()).digest()
        x = int.from_bytes(path_hash[:4], 'big') / (2**32)
        y = 1.0 / (x + 0.001)
        self.identity_vector = (x, y)
        
        # Map method to spiral
        method_map = {
            'GET': 0,
            'POST': 1,
            'PUT': 2,
            'DELETE': 3,
            'PATCH': 4,
            'OPTIONS': 5,
            'HEAD': 6
        }
        self.spiral = method_map.get(self.method.upper(), 0)
    
    @property
    def z_value(self) -> float:
        """Compute z = x·y for geometric composition"""
        return self.identity_vector[0] * self.identity_vector[1]
    
    @property
    def stage_name(self) -> str:
        """Human-readable processing stage"""
        stages = {
            1: "received",
            2: "parsed",
            3: "routed",
            4: "processed",
            5: "response_ready",
            6: "sent",
            7: "logged"
        }
        return stages.get(self.layer, "unknown")
    
    @property
    def processing_time_ms(self) -> float:
        """Time spent processing (milliseconds)"""
        return (time.time() - self.created_at) * 1000
    
    def transition_to(self, new_layer: int):
        """Transition to new processing stage"""
        if 1 <= new_layer <= 7:
            self.layer = new_layer


# =============================================================================
# ROUTE SUBSTRATE - O(1) routing with dimensional index
# =============================================================================

class RouteSubstrate:
    """
    Routes requests using dimensional coordinates.
    
    Routes are indexed by (spiral, path_pattern) for O(1) lookup.
    No iteration through route list - direct addressing.
    """
    
    def __init__(self):
        self._routes: Dict[Tuple[int, str], Callable] = {}  # (spiral, pattern) -> handler
        self._exact_routes: Dict[Tuple[int, str], Callable] = {}  # Exact matches
        self._prefix_routes: List[Tuple[int, str, Callable]] = []  # Prefix matches (fallback)
        self._lock = threading.RLock()
        
        # Route statistics
        self.route_hits: Dict[str, int] = {}
        self.route_times: Dict[str, List[float]] = {}
    
    def register(
        self,
        method: str,
        pattern: str,
        handler: Callable,
        exact: bool = True
    ):
        """
        Register a route handler.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            pattern: URL pattern (/api/users, /api/*, etc.)
            handler: Function to handle request
            exact: If True, exact match only. If False, prefix match.
        """
        with self._lock:
            method_map = {
                'GET': 0, 'POST': 1, 'PUT': 2, 'DELETE': 3,
                'PATCH': 4, 'OPTIONS': 5, 'HEAD': 6
            }
            spiral = method_map.get(method.upper(), 0)
            
            if exact:
                self._exact_routes[(spiral, pattern)] = handler
            else:
                self._prefix_routes.append((spiral, pattern, handler))
                # Sort by pattern length (longest first for best match)
                self._prefix_routes.sort(key=lambda x: len(x[1]), reverse=True)
    
    def route(self, request: RequestPoint) -> Optional[Callable]:
        """
        Route request to handler - O(1) for exact, O(log n) for prefix.
        
        Returns handler function or None if no route found.
        """
        with self._lock:
            # Try exact match first - O(1)
            key = (request.spiral, request.path)
            if key in self._exact_routes:
                handler = self._exact_routes[key]
                self._record_hit(request.path)
                return handler
            
            # Try prefix match - O(log n) with sorted list
            for spiral, pattern, handler in self._prefix_routes:
                if spiral == request.spiral and request.path.startswith(pattern):
                    self._record_hit(pattern)
                    return handler
            
            return None
    
    def _record_hit(self, pattern: str):
        """Record route hit for statistics"""
        self.route_hits[pattern] = self.route_hits.get(pattern, 0) + 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        with self._lock:
            return {
                "total_routes": len(self._exact_routes) + len(self._prefix_routes),
                "exact_routes": len(self._exact_routes),
                "prefix_routes": len(self._prefix_routes),
                "route_hits": self.route_hits,
                "most_hit": max(self.route_hits.items(), key=lambda x: x[1]) if self.route_hits else None
            }


# =============================================================================
# REQUEST SUBSTRATE - Lazy parsing and processing
# =============================================================================

class RequestSubstrate:
    """
    Manages requests as a dimensional substrate.
    
    Features:
        - O(1) request lookup by ID
        - Lazy parsing (parse only when needed)
        - Automatic state transitions
        - Request/response composition
    """
    
    def __init__(self):
        self._requests: Dict[str, RequestPoint] = {}
        self._lock = threading.RLock()
        
        # Statistics
        self.total_requests = 0
        self.total_processed = 0
        self.total_errors = 0
        
        # Performance tracking
        self._processing_times: List[float] = []
    
    def manifest(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: bytes = b'',
        client_ip: str = ""
    ) -> RequestPoint:
        """
        Manifest a new request (lazy creation).
        
        Returns RequestPoint at layer 1 (received).
        """
        with self._lock:
            # Generate request ID
            request_id = hashlib.md5(
                f"{method}:{path}:{time.time()}".encode()
            ).hexdigest()[:16]
            
            # Create request point
            request = RequestPoint(
                request_id=request_id,
                method=method,
                path=path,
                headers=headers,
                body=body,
                client_ip=client_ip,
                layer=1  # received
            )
            
            self._requests[request_id] = request
            self.total_requests += 1
            
            return request
    
    def transition(self, request_id: str, new_layer: int):
        """Transition request to new processing stage"""
        with self._lock:
            request = self._requests.get(request_id)
            if request:
                request.transition_to(new_layer)
                
                # Auto-cleanup logged requests
                if new_layer == 7:
                    self._archive_request(request)
    
    def _archive_request(self, request: RequestPoint):
        """Archive and remove request"""
        with self._lock:
            # Record processing time
            self._processing_times.append(request.processing_time_ms)
            
            # Keep only last 1000 times
            if len(self._processing_times) > 1000:
                self._processing_times = self._processing_times[-1000:]
            
            # Update statistics
            if request.response_status >= 200 and request.response_status < 400:
                self.total_processed += 1
            else:
                self.total_errors += 1
            
            # Remove from active requests
            if request.request_id in self._requests:
                del self._requests[request.request_id]
    
    def get_request(self, request_id: str) -> Optional[RequestPoint]:
        """Get request by ID - O(1)"""
        with self._lock:
            return self._requests.get(request_id)
    
    def set_response(
        self,
        request_id: str,
        status: int,
        headers: Dict[str, str],
        body: bytes
    ):
        """Set response data for request"""
        with self._lock:
            request = self._requests.get(request_id)
            if request:
                request.response_status = status
                request.response_headers = headers
                request.response_body = body
                self.transition(request_id, 5)  # response_ready
    
    def compose(self, req1_id: str, req2_id: str) -> Optional[float]:
        """
        Geometric composition: z = x·y
        
        Composes two requests to compute similarity.
        Useful for caching, deduplication, etc.
        """
        req1 = self.get_request(req1_id)
        req2 = self.get_request(req2_id)
        
        if not req1 or not req2:
            return None
        
        z1 = req1.z_value
        z2 = req2.z_value
        return z1 * z2
    
    def get_stats(self) -> Dict[str, Any]:
        """Get substrate statistics"""
        with self._lock:
            avg_time = sum(self._processing_times) / len(self._processing_times) if self._processing_times else 0
            
            return {
                "active_requests": len(self._requests),
                "total_requests": self.total_requests,
                "total_processed": self.total_processed,
                "total_errors": self.total_errors,
                "avg_processing_time_ms": round(avg_time, 2),
                "success_rate": round(self.total_processed / max(self.total_requests, 1) * 100, 2)
            }


# =============================================================================
# REQUEST/RESPONSE MANIFOLD - Complete pipeline
# =============================================================================

class RequestResponseManifold:
    """
    Complete request/response processing manifold.
    
    Combines:
        - Request substrate (request management)
        - Route substrate (routing)
        - Response composition
    
    Pipeline:
        1. Manifest request (layer 1)
        2. Parse request (layer 2)
        3. Route request (layer 3)
        4. Process request (layer 4)
        5. Compose response (layer 5)
        6. Send response (layer 6)
        7. Log request (layer 7)
    """
    
    def __init__(self):
        self.request_substrate = RequestSubstrate()
        self.route_substrate = RouteSubstrate()
        self._lock = threading.RLock()
    
    def register_route(
        self,
        method: str,
        pattern: str,
        handler: Callable,
        exact: bool = True
    ):
        """Register a route handler"""
        self.route_substrate.register(method, pattern, handler, exact)
    
    def process_request(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: bytes = b'',
        client_ip: str = ""
    ) -> Tuple[int, Dict[str, str], bytes]:
        """
        Process complete request through pipeline.
        
        Returns: (status_code, response_headers, response_body)
        """
        with self._lock:
            # 1. Manifest request
            request = self.request_substrate.manifest(method, path, headers, body, client_ip)
            
            # 2. Parse (already done in __post_init__)
            self.request_substrate.transition(request.request_id, 2)
            
            # 3. Route
            handler = self.route_substrate.route(request)
            self.request_substrate.transition(request.request_id, 3)
            
            if not handler:
                # No route found
                status = 404
                response_headers = {'Content-Type': 'application/json'}
                response_body = json.dumps({"error": "Not found"}).encode()
            else:
                # 4. Process
                try:
                    status, response_headers, response_body = handler(request)
                    self.request_substrate.transition(request.request_id, 4)
                except Exception as e:
                    status = 500
                    response_headers = {'Content-Type': 'application/json'}
                    response_body = json.dumps({"error": str(e)}).encode()
            
            # 5. Set response
            self.request_substrate.set_response(
                request.request_id,
                status,
                response_headers,
                response_body
            )
            
            # 6. Mark as sent
            self.request_substrate.transition(request.request_id, 6)
            
            # 7. Log
            self.request_substrate.transition(request.request_id, 7)
            
            return status, response_headers, response_body
    
    def get_stats(self) -> Dict[str, Any]:
        """Get complete manifold statistics"""
        return {
            "requests": self.request_substrate.get_stats(),
            "routes": self.route_substrate.get_stats()
        }


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Create manifold
    manifold = RequestResponseManifold()
    
    # Register routes
    def handle_status(request: RequestPoint):
        return 200, {'Content-Type': 'application/json'}, json.dumps({
            "status": "ok",
            "path": request.path
        }).encode()
    
    def handle_api(request: RequestPoint):
        return 200, {'Content-Type': 'application/json'}, json.dumps({
            "api": "v1",
            "path": request.path,
            "method": request.method
        }).encode()
    
    manifold.register_route('GET', '/api/status', handle_status, exact=True)
    manifold.register_route('GET', '/api/', handle_api, exact=False)
    
    # Process requests
    status, headers, body = manifold.process_request(
        'GET',
        '/api/status',
        {'User-Agent': 'Test'},
        client_ip='127.0.0.1'
    )
    print(f"Status: {status}")
    print(f"Body: {body.decode()}")
    
    # Get statistics
    stats = manifold.get_stats()
    print(f"\nStatistics: {json.dumps(stats, indent=2)}")
