"""
ButterflyFx API Documentation
═════════════════════════════════════════════════════════════════════════════

A Complete Programming Paradigm Based on Mathematical Substrates

═════════════════════════════════════════════════════════════════════════════
                              ARCHITECTURE
═════════════════════════════════════════════════════════════════════════════

    ┌─────────────────────────────────────────────────────────────────────┐
    │                         EXTERNAL WORLD                               │
    │   (Developers, APIs, Files, Databases, AI Models, Streams)          │
    └───────────────────────────────┬─────────────────────────────────────┘
                                    │
                                    ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │                      ButterflyFx API (api.py)                        │
    │                                                                      │
    │   fx = ButterflyFx()                                                │
    │   fx.process(data)    # Enter data into system                      │
    │   fx.compute(...)     # Execute operations                          │
    │   fx.fetch(srl)       # Fetch from datasources                      │
    │   fx.render(result)   # Display output                              │
    │   fx.serve()          # Run as server                               │
    └───────────────────────────────┬─────────────────────────────────────┘
                                    │
                                    ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │                         CORE LAYER                                   │
    │                                                                      │
    │   ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
    │   │   _ingest()  │  │    SRL       │  │       Server             │  │
    │   │  (internal)  │  │ (connection) │  │   (HTTP/Socket)          │  │
    │   └──────┬───────┘  └──────────────┘  └──────────────────────────┘  │
    │          │                                                           │
    │   ┌──────┴──────────────────────────────────────────────────────┐   │
    │   │                    ingest() → Substrate                      │   │
    │   │                 THE ONLY WAY INTO KERNEL                     │   │
    │   └──────────────────────────────┬──────────────────────────────┘   │
    └──────────────────────────────────┼──────────────────────────────────┘
                                       │
                                       ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │                           KERNEL                                     │
    │                     (Pure 64-bit Math)                              │
    │                                                                      │
    │   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                │
    │   │  Substrate   │ │    Lens      │ │    Delta     │                │
    │   │    x₁        │ │  projection  │ │    z₁        │                │
    │   └──────────────┘ └──────────────┘ └──────────────┘                │
    │                                                                      │
    │   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                │
    │   │  Dimension   │ │   Manifold   │ │   promote()  │                │
    │   │   level      │ │    shape     │ │  invoke()    │                │
    │   └──────────────┘ └──────────────┘ └──────────────┘                │
    │                                                                      │
    │   NO CONNECTIONS. NO SERVER. PURE MATHEMATICAL TRUTH.               │
    └─────────────────────────────────────────────────────────────────────┘


═════════════════════════════════════════════════════════════════════════════
                              QUICK START
═════════════════════════════════════════════════════════════════════════════

BASIC USAGE:

    from core_v2 import ButterflyFx
    
    # Create instance
    fx = ButterflyFx()
    
    # Process any data into a substrate
    result = fx.process(42)
    print(result.truth)  # 64-bit substrate identity
    
    # Process complex data
    result = fx.process({"name": "entity", "value": 123})
    
    # Compute operations
    from core_v2 import Computation
    result = fx.compute(Computation.xor(100, 50))
    print(result.value)  # 86
    
    # Render output
    print(fx.render(result, format="hex"))  # 0x0000000000000056


═════════════════════════════════════════════════════════════════════════════
                              API REFERENCE
═════════════════════════════════════════════════════════════════════════════

CLASS: ButterflyFx
──────────────────

    The main interface for all operations. All data enters the kernel
    through this class.
    
    Constructor:
        fx = ButterflyFx(config: Optional[FxConfig] = None)
    
    Methods:
        
        process(data: Any) -> FxResult
            Process any data through the Core→Kernel pipeline.
            Data becomes a substrate with a 64-bit identity.
            
            Args:
                data: Any Python value, object, or data structure
            
            Returns:
                FxResult with truth (64-bit identity) and manifest
            
            Example:
                result = fx.process("hello world")
                result = fx.process([1, 2, 3, 4, 5])
                result = fx.process({"key": "value"})
        
        compute(computation: Computation) -> FxResult
            Execute a mathematical computation on substrates.
            
            Operations: XOR, AND, OR, ROT, ADD, SUB, MUL, DIV
            
            Example:
                result = fx.compute(Computation.xor(a, b))
                result = fx.compute(Computation.add(100, 50))
        
        pipeline(initial: Optional[Any] = None) -> Pipeline
            Create a computation pipeline for chaining operations.
            
            Example:
                pipe = fx.pipeline(42)
                pipe = pipe.xor(0xFF).and_(0xF0).or_(0x01)
                result = fx.run(pipe)
        
        run(pipeline: Pipeline) -> FxResult
            Execute a pipeline through the kernel.
        
        project(data: Any, projection: Callable[[int], int]) -> FxResult
            Apply a lens projection to transform data.
            
            Example:
                result = fx.project(42, lambda x: x * 2)
        
        transform(source: Any, derived: Any, delta: int) -> FxResult
            Transform a substrate through promotion with a delta.
            
            Example:
                result = fx.transform(old_value, new_value, change_id)
        
        fetch(srl: SRL, query: Optional[str] = None) -> FxResult
            Fetch data through SRL and automatically ingest it.
            
            This is the primary way to bring external data into the kernel:
                1. SRL connects to datasource
                2. Data is fetched
                3. Data goes through ingest() → becomes substrate
            
            Example:
                from core_v2 import http_srl, TokenAuth
                
                srl = http_srl("https://api.example.com/data",
                              credentials=TokenAuth(token="..."))
                result = fx.fetch(srl, query="id=42")
        
        send(srl: SRL, data: Any) -> FxResult
            Process data through kernel then send via SRL.
            
            Example:
                fx.send(srl, {"message": "hello"})
        
        render(result: FxResult, format: str = "auto") -> str
            Render a result for display.
            
            Formats: "auto", "text", "hex", "binary", "json"
            
            Example:
                print(fx.render(result, format="hex"))
        
        validate(data: Any) -> bool
            Check if data can be processed by the system.
        
        cached(truth: int) -> Optional[FxResult]
            Retrieve a cached substrate by its truth value.
        
        clear_cache() -> int
            Clear the substrate cache. Returns count cleared.
        
        serve(blocking: bool = True) -> None
            Start the ButterflyFx server for remote access.
            
            Endpoints:
                HTTP: http://host:port/
                Socket: host:port+1
        
        stop() -> None
            Stop the server if running.


CLASS: FxResult
───────────────

    Result from a ButterflyFx operation.
    
    Attributes:
        value: Any           # The original or computed value
        truth: int           # The 64-bit substrate identity
        success: bool        # Whether operation succeeded
        execution_time_ns: int   # Execution time in nanoseconds
        manifest: Optional[SubstrateManifest]  # Full substrate info
    
    Methods:
        as_int() -> int      # Get result as integer
        as_float() -> float  # Get result as float
        as_str() -> str      # Get result as string
        as_bytes() -> bytes  # Get result as bytes


CLASS: FxConfig
───────────────

    Configuration for ButterflyFx instance.
    
    Attributes:
        strict_mode: bool = True       # Enable strict validation
        validate_laws: bool = True     # Validate against 15 Laws
        enable_caching: bool = True    # Enable substrate caching
        cache_max_size: int = 10000    # Max cache entries
        parallel_workers: int = 4      # Worker thread count
        server_host: str = "127.0.0.1" # Server bind host
        server_port: int = 8088        # Server bind port
        enable_server: bool = False    # Auto-start server
        enable_rendering: bool = True  # Enable render pipeline
        render_backend: str = "auto"   # Render backend
        srl_socket_timeout: float = 30.0   # SRL timeout
        srl_default_domain: str = "local"  # Default SRL domain


CLASS: Computation
──────────────────

    A computation to be processed by the Core.
    
    Class Methods:
        xor(a, b)   # XOR operation
        and_(a, b)  # AND operation  
        or_(a, b)   # OR operation
        rot(a, n)   # Rotate left by n bits
        add(a, b)   # Addition
        sub(a, b)   # Subtraction
        mul(a, b)   # Multiplication
        div(a, b)   # Division
    
    Example:
        comp = Computation.xor(0xFF00, 0x00FF)
        result = fx.compute(comp)


CLASS: Pipeline
───────────────

    A sequence of computations to be executed.
    
    Methods:
        then(operation: str, *args) -> Pipeline  # Add step
        xor(value) -> Pipeline   # Add XOR step
        and_(value) -> Pipeline  # Add AND step
        or_(value) -> Pipeline   # Add OR step
    
    Example:
        pipe = fx.pipeline(100)
        pipe = pipe.xor(50).and_(0xFF).or_(0x100)
        result = fx.run(pipe)


CLASS: Projection
─────────────────

    A lens projection definition.
    
    Example:
        proj = Projection(transform=lambda x: x * 2, name="double")
        result = fx.project(42, proj)


CLASS: Reference
────────────────

    A substrate reference (SRL location).
    
    Attributes:
        domain: str      # Target domain
        path: str        # Resource path
        target: int      # Target identity
    
    Methods:
        to_srl() -> SRL  # Convert to SRL connection device
        uri -> str       # Get SRL URI string
    
    Example:
        ref = Reference(domain="api.example.com", path="/data", target=0x123)
        srl = ref.to_srl()
        result = fx.fetch(srl)


CLASS: Transform
────────────────

    A delta transform definition.
    
    Example:
        delta = Transform(delta_value=42)
        result = fx.transform(source, derived, delta)


═════════════════════════════════════════════════════════════════════════════
                              SRL - CONNECTION DEVICE
═════════════════════════════════════════════════════════════════════════════

SRL (Substrate Reference Locator) is a Core function for connecting to
datasources. The kernel remains pure math - SRL handles all connections.

CLASS: SRL
──────────

    Connection device for fetching/sending data.
    
    Constructor:
        srl = SRL(
            domain: str,                      # Target domain
            path: str,                        # Resource path
            credentials: Optional[Credentials] = None,
            protocol: Optional[Protocol] = None,
            config: Optional[SRLConfig] = None,
            identity: Optional[int] = None
        )
    
    Methods:
        connect() -> SRLConnection   # Establish connection
        fetch(query: str = None) -> SRLResult   # Fetch data
        send(data: bytes) -> SRLResult   # Send data
        uri() -> str                 # Get URI string
        
    Example:
        srl = SRL(
            domain="api.example.com",
            path="/v1/users",
            credentials=TokenAuth(token="secret"),
            protocol=HTTPProtocol()
        )
        
        # Single fetch
        result = srl.fetch(query="id=42")
        
        # Use with ButterflyFx
        fx = ButterflyFx()
        result = fx.fetch(srl)  # Fetches AND ingests automatically


FACTORY FUNCTIONS:
    
    file_srl(path: str) -> SRL
        Create SRL for local file access.
        
        Example:
            srl = file_srl("/data/file.txt")
            result = fx.fetch(srl)
    
    http_srl(url: str, credentials=None, headers=None) -> SRL
        Create SRL for HTTP API access.
        
        Example:
            srl = http_srl("https://api.example.com/data",
                          credentials=TokenAuth(token="..."))
            result = fx.fetch(srl)
    
    socket_srl(host: str, port: int, use_ssl=False) -> SRL
        Create SRL for raw socket connection.
        
        Example:
            srl = socket_srl("192.168.1.100", 8089, use_ssl=True)


CREDENTIALS:

    APIKey(key: str, header_name: str = "X-API-Key")
        API key authentication.
    
    BasicAuth(username: str, password: str)
        HTTP Basic authentication.
    
    TokenAuth(token: str, token_type: str = "Bearer")
        Bearer token authentication.
    
    CertAuth(cert_path: str, key_path: str, ca_path: str = None)
        Certificate-based authentication.


PROTOCOLS:

    FileProtocol(base_path: str = None)
        Local file system access.
    
    HTTPProtocol(method="GET", headers={}, timeout=30.0)
        HTTP/HTTPS requests.
    
    SocketProtocol(timeout=30.0, buffer_size=8192, use_ssl=False)
        Raw TCP socket.
    
    DatabaseProtocol(driver="generic")
        Database connections (abstract).


═════════════════════════════════════════════════════════════════════════════
                              SERVER API
═════════════════════════════════════════════════════════════════════════════

ButterflyFx can run as a computation server, accepting HTTP and socket
connections.

STARTING THE SERVER:

    fx = ButterflyFx()
    fx.serve()  # Blocking
    
    # Or non-blocking
    fx.serve(blocking=False)
    # ... do other work ...
    fx.stop()


HTTP ENDPOINTS:

    GET /
        Returns API info and available endpoints.
        
        Response:
            {
                "name": "ButterflyFx Core API",
                "version": "2.0.0",
                "endpoints": {...}
            }
    
    GET /status
        Returns server status.
        
        Response:
            {
                "success": true,
                "status": "running",
                "cached": 123,
                "config": {...}
            }
    
    POST /process
        Process data into a substrate.
        
        Request:
            {"data": <any>}
        
        Response:
            {
                "success": true,
                "truth": 12345,
                "truth_hex": "0x0000000000003039"
            }
    
    POST /compute
        Execute a computation.
        
        Request:
            {
                "operation": "XOR",
                "inputs": [100, 50]
            }
        
        Response:
            {
                "success": true,
                "value": 86,
                "truth": 86,
                "truth_hex": "0x0000000000000056"
            }
    
    POST /project
        Apply a lens projection.
        
        Request:
            {
                "data": 42,
                "projection": "x XOR 0xFF"
            }
        
        Projection expression format:
            "x OP value" where OP is XOR, AND, OR, ROT, +, -, *, /
    
    POST /transform
        Apply a delta transformation.
        
        Request:
            {
                "source": <any>,
                "derived": <any>,
                "delta": 7
            }
    
    GET /reference?uri=srl://domain/path#identity
        Resolve an SRL reference.
    
    POST /render
        Render a result.
        
        Request:
            {"data": <any>, "format": "hex"}
    
    POST /batch
        Execute multiple operations.
        
        Request:
            {
                "operations": [
                    {"type": "process", "data": 42},
                    {"type": "compute", "operation": "XOR", "inputs": [100, 50]}
                ]
            }


SOCKET PROTOCOL:

    Port: HTTP_PORT + 1 (default 8089)
    
    Message format: Length-prefixed JSON
        [4 bytes: message length (big-endian)] + [JSON payload]
    
    Actions:
        {"action": "process", "data": <any>}
        {"action": "compute", "operation": "XOR", "inputs": [...]}
        {"action": "ping"}


═════════════════════════════════════════════════════════════════════════════
                              EXAMPLES
═════════════════════════════════════════════════════════════════════════════

EXAMPLE 1: Basic Data Processing

    from core_v2 import ButterflyFx
    
    fx = ButterflyFx()
    
    # Process primitives
    r1 = fx.process(42)
    r2 = fx.process(3.14159)
    r3 = fx.process("hello")
    r4 = fx.process(True)
    
    # Process collections
    r5 = fx.process([1, 2, 3, 4, 5])
    r6 = fx.process({"name": "entity", "value": 100})
    
    # All become substrates with 64-bit identities
    print(f"42 → 0x{r1.truth:016X}")


EXAMPLE 2: Computations

    from core_v2 import ButterflyFx, Computation
    
    fx = ButterflyFx()
    
    # Basic operations
    xor_result = fx.compute(Computation.xor(0xFF00, 0x00FF))
    and_result = fx.compute(Computation.and_(0xFF, 0x0F))
    or_result = fx.compute(Computation.or_(0xF0, 0x0F))
    
    # Arithmetic
    sum_result = fx.compute(Computation.add(100, 50))
    diff_result = fx.compute(Computation.sub(100, 50))
    prod_result = fx.compute(Computation.mul(10, 5))


EXAMPLE 3: Pipelines

    from core_v2 import ButterflyFx
    
    fx = ButterflyFx()
    
    # Create and run a pipeline
    pipe = fx.pipeline(0x1234)
    pipe = pipe.xor(0x00FF)
    pipe = pipe.and_(0xFFFF)
    pipe = pipe.or_(0x0001)
    
    result = fx.run(pipe)
    print(fx.render(result, format="hex"))


EXAMPLE 4: Fetching Data via SRL

    from core_v2 import ButterflyFx, http_srl, TokenAuth
    
    fx = ButterflyFx()
    
    # Create SRL connection
    srl = http_srl(
        "https://api.example.com/v1/data",
        credentials=TokenAuth(token="your-api-token"),
        headers={"Accept": "application/json"}
    )
    
    # Fetch and ingest in one call
    result = fx.fetch(srl, query="limit=100")
    
    # result.value contains the fetched bytes
    # result.truth is the substrate identity


EXAMPLE 5: File Processing

    from core_v2 import ButterflyFx, file_srl
    
    fx = ButterflyFx()
    
    # Read local file
    srl = file_srl("/path/to/data.json")
    result = fx.fetch(srl)
    
    # Process content
    content = result.value  # bytes
    data = json.loads(content)
    processed = fx.process(data)


EXAMPLE 6: Running as Server

    from core_v2 import ButterflyFx, FxConfig
    
    # Configure server
    config = FxConfig(
        server_host="0.0.0.0",
        server_port=8088,
        enable_caching=True
    )
    
    fx = ButterflyFx(config=config)
    
    print("Starting ButterflyFx server...")
    fx.serve()  # Blocks


EXAMPLE 7: Client Request to Server

    import requests
    
    # Process data
    response = requests.post("http://localhost:8088/process", 
                            json={"data": [1, 2, 3, 4, 5]})
    result = response.json()
    print(f"Truth: {result['truth_hex']}")
    
    # Compute operation
    response = requests.post("http://localhost:8088/compute",
                            json={"operation": "XOR", "inputs": [100, 50]})
    result = response.json()
    print(f"Result: {result['value']}")


═════════════════════════════════════════════════════════════════════════════
                              THE 15 LAWS
═════════════════════════════════════════════════════════════════════════════

The ButterflyFx system is governed by 15 immutable laws:

1. SUBSTRATE TRUTH: The substrate is the singular source of truth.
2. 64-BIT CONSTRAINT: All values fit in 64 bits.
3. IMMUTABILITY: Substrates cannot be modified, only promoted.
4. PROMOTION: Change occurs ONLY through promote(x₁, y₁, z₁) → m₁.
5. LENS PROJECTION: Attributes derived through lens invocation.
6. CORE GATEWAY: Kernel accessed ONLY through Core.
7. NO SHADOW STATE: No state exists outside substrates.
8. MATHEMATICAL PURITY: Kernel contains only pure math.
9. DETERMINISM: Same inputs → same outputs, always.
10. COMPOSABILITY: All operations compose mathematically.
11. DIMENSIONAL INTEGRITY: Substrates maintain dimensional bounds.
12. DELTA ENCODING: Changes encoded as deltas, not new values.
13. MANIFEST SHAPES: Substrates have definite shapes at intersections.
14. INVOKE TRUTH: invoke(substrate, lens) reveals truth.
15. NO EXTERNAL STATE: System state is entirely in substrates.

═════════════════════════════════════════════════════════════════════════════
"""

# This file is documentation only - no code to import
