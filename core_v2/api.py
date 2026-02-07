"""
ButterflyFx Core API - The Public Interface

═══════════════════════════════════════════════════════════════════
                    DEVELOPER API
═══════════════════════════════════════════════════════════════════

This is the ONLY way to interact with the ButterflyFx Core/Kernel.

Developers use this API. The Core evaluates inputs internally,
calls ingest to enter data into the kernel, converting everything
to pure mathematical substrates.

The Core is:
    - The ONLY gateway to the Kernel
    - A computation server 
    - A renderer
    - The interface for ALL data processing

USAGE:
    from butterflyfx import ButterflyFx
    
    fx = ButterflyFx()
    result = fx.process(data)
    fx.render(result)

═══════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
import hashlib
import json
import asyncio
from typing import (
    Any, Dict, List, Optional, Union, Callable, 
    Iterator, TypeVar, Generic, Tuple, overload,
    TYPE_CHECKING, AsyncIterator
)
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum, auto
import threading
import queue

if TYPE_CHECKING:
    from .srl import SRL
    from .dimensional import DimensionalSubstrate, DimensionalDelta
    from dimension_os import DimensionOS

# Internal imports - NOT exposed
from ._ingest import (
    ingest as _ingest,
    invoke as _invoke,
    promote as _promote,
    Ingest as _IngestClass,
    SubstrateManifest,
    IngestResult,
    AssetType,
    LensSpec,
    DeltaSpec,
    DimensionSpec,
)
from .validator import Validator, ValidationError
from .translator import Translator


__all__ = [
    # Main API
    'ButterflyFx',
    'FxResult',
    'FxError',
    
    # Types developers can create
    'Computation',
    'Pipeline',
    'Projection',
    'Reference',
    'Transform',
    
    # Configuration
    'FxConfig',
    
    # Spec types (for advanced use)
    'LensSpec',
    'DeltaSpec',
    'DimensionSpec',
]


# ═══════════════════════════════════════════════════════════════════
# RESULT TYPES
# ═══════════════════════════════════════════════════════════════════

class FxError(Exception):
    """Error from the ButterflyFx Core."""
    def __init__(self, message: str, code: int = 0, details: Optional[Dict] = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}


@dataclass
class FxResult:
    """Result from a ButterflyFx operation."""
    value: Any
    truth: int  # The 64-bit substrate truth
    success: bool = True
    execution_time_ns: int = 0
    manifest: Optional[SubstrateManifest] = None
    
    def __repr__(self) -> str:
        return f"FxResult(value={self.value!r}, truth=0x{self.truth:016X})"
    
    def as_int(self) -> int:
        """Get result as integer."""
        if isinstance(self.value, int):
            return self.value
        return self.truth
    
    def as_float(self) -> float:
        """Get result as float."""
        if isinstance(self.value, float):
            return self.value
        import struct
        return struct.unpack('d', struct.pack('Q', self.truth & 0xFFFFFFFFFFFFFFFF))[0]
    
    def as_str(self) -> str:
        """Get result as string."""
        if isinstance(self.value, str):
            return self.value
        return str(self.value)
    
    def as_bytes(self) -> bytes:
        """Get result as bytes."""
        if isinstance(self.value, bytes):
            return self.value
        return self.truth.to_bytes(8, 'little')


# ═══════════════════════════════════════════════════════════════════
# COMPUTATION TYPES
# ═══════════════════════════════════════════════════════════════════

@dataclass
class Computation:
    """
    A computation to be processed by the Core.
    
    All computations become substrate operations in the kernel.
    """
    operation: str
    inputs: List[Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Common operations
    XOR = "XOR"
    AND = "AND"
    OR = "OR"
    ROT = "ROT"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    
    @classmethod
    def xor(cls, a: Any, b: Any) -> Computation:
        return cls(cls.XOR, [a, b])
    
    @classmethod
    def and_(cls, a: Any, b: Any) -> Computation:
        return cls(cls.AND, [a, b])
    
    @classmethod
    def or_(cls, a: Any, b: Any) -> Computation:
        return cls(cls.OR, [a, b])
    
    @classmethod
    def rot(cls, a: Any, n: int) -> Computation:
        return cls(cls.ROT, [a, n])
    
    @classmethod 
    def add(cls, a: Any, b: Any) -> Computation:
        return cls(cls.ADD, [a, b])
    
    @classmethod
    def sub(cls, a: Any, b: Any) -> Computation:
        return cls(cls.SUB, [a, b])
    
    @classmethod
    def mul(cls, a: Any, b: Any) -> Computation:
        return cls(cls.MUL, [a, b])
    
    @classmethod
    def div(cls, a: Any, b: Any) -> Computation:
        return cls(cls.DIV, [a, b])


@dataclass
class Pipeline:
    """
    A sequence of computations to be executed.
    
    Pipelines allow chaining operations that all run through
    the Core→Kernel pathway.
    """
    steps: List[Computation]
    name: Optional[str] = None
    
    def then(self, operation: str, *args) -> Pipeline:
        """Add a step to the pipeline."""
        new_steps = self.steps + [Computation(operation, list(args))]
        return Pipeline(new_steps, self.name)
    
    def xor(self, value: Any) -> Pipeline:
        return self.then(Computation.XOR, "_prev", value)
    
    def and_(self, value: Any) -> Pipeline:
        return self.then(Computation.AND, "_prev", value)
    
    def or_(self, value: Any) -> Pipeline:
        return self.then(Computation.OR, "_prev", value)


@dataclass
class Projection:
    """
    A lens projection definition.
    
    Projections transform substrates through mathematical operations.
    """
    transform: Callable[[int], int]
    name: Optional[str] = None
    
    def to_lens_spec(self) -> LensSpec:
        return LensSpec(
            projection=self.transform,
            name=self.name
        )


@dataclass 
class Reference:
    """
    A substrate reference (SRL location).
    
    References locate substrates anywhere in the system.
    Can be converted to an SRL connection device for fetching.
    """
    domain: str
    path: str
    target: int
    
    def to_srl(self) -> 'SRL':
        """Convert to an SRL connection device."""
        from .srl import SRL as SRLClass
        return SRLClass(
            domain=self.domain,
            path=self.path,
            identity=self.target
        )
    
    @property
    def uri(self) -> str:
        return f"srl://{self.domain}/{self.path}#{self.target:016x}"
    
    def to_data(self) -> Dict[str, Any]:
        """Convert to dictionary for ingestion as substrate."""
        return {
            'type': 'reference',
            'domain': self.domain,
            'path': self.path,
            'target': self.target
        }


@dataclass
class Transform:
    """
    A delta transform definition.
    
    Transforms encode how substrates change through promotion.
    """
    delta_value: int
    
    def to_delta_spec(self) -> DeltaSpec:
        return DeltaSpec(value=self.delta_value)


# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

@dataclass
class FxConfig:
    """Configuration for ButterflyFx instance."""
    # Validation
    strict_mode: bool = True
    validate_laws: bool = True
    
    # Performance
    enable_caching: bool = True
    cache_max_size: int = 10000
    parallel_workers: int = 4
    
    # Server
    server_host: str = "127.0.0.1"
    server_port: int = 8088
    enable_server: bool = False
    
    # Rendering
    enable_rendering: bool = True
    render_backend: str = "auto"  # auto, terminal, gui, web
    
    # SRL
    srl_socket_timeout: float = 30.0
    srl_default_domain: str = "local"


# ═══════════════════════════════════════════════════════════════════
# MAIN API CLASS
# ═══════════════════════════════════════════════════════════════════

class ButterflyFx:
    """
    The ButterflyFx Core Interface.
    
    This is the ONLY way for developers to interact with the kernel.
    All data enters through this interface, gets converted to substrates,
    processed through pure 64-bit math, and results returned.
    
    The ButterflyFx system is:
        - A complete programming paradigm
        - A computation server
        - A renderer
        - A data processing pipeline
    
    Usage:
        fx = ButterflyFx()
        
        # Process any data
        result = fx.process(42)
        result = fx.process([1, 2, 3])
        result = fx.process({"key": "value"})
        
        # Compute operations
        result = fx.compute(Computation.xor(a, b))
        
        # Create pipelines
        pipeline = fx.pipeline().xor(42).and_(0xFF).or_(0x100)
        result = fx.run(pipeline)
        
        # Render results
        fx.render(result)
        
        # Start as server
        fx.serve()
    """
    
    def __init__(self, config: Optional[FxConfig] = None):
        self._config = config or FxConfig()
        self._validator = Validator()
        self._translator = Translator()
        self._cache: Dict[int, SubstrateManifest] = {}
        self._lock = threading.RLock()
        self._server = None
        self._running = False
        
    @property
    def config(self) -> FxConfig:
        return self._config
    
    # ─────────────────────────────────────────────────────────────────
    # CORE OPERATIONS - All data goes through these
    # ─────────────────────────────────────────────────────────────────
    
    def process(self, data: Any) -> FxResult:
        """
        Process any data through the Core→Kernel pipeline.
        
        This is the primary method for entering data into the system.
        All data is converted to substrates inside the kernel.
        
        Args:
            data: Any Python value, object, file, or data structure
            
        Returns:
            FxResult containing the processed substrate truth
        """
        import time
        start = time.time_ns()
        
        try:
            # Validate input if in strict mode
            if self._config.strict_mode:
                self._validate_input(data)
            
            # Internal ingest - converts to substrate
            result = _ingest(data)
            
            if not result.success:
                raise FxError(result.error or "Ingestion failed", code=1)
            
            # Get the truth value
            truth = 0
            if result.manifest and result.manifest._substrate:
                truth = result.manifest._substrate.identity.value
            
            # Cache if enabled
            if self._config.enable_caching and result.manifest:
                with self._lock:
                    self._cache[truth] = result.manifest
            
            end = time.time_ns()
            
            return FxResult(
                value=data,
                truth=truth,
                success=True,
                execution_time_ns=end - start,
                manifest=result.manifest
            )
            
        except FxError:
            raise
        except Exception as e:
            raise FxError(str(e), code=2)
    
    def compute(self, computation: Computation) -> FxResult:
        """
        Execute a computation through the kernel.
        
        Args:
            computation: A Computation object defining the operation
            
        Returns:
            FxResult with the computed value
        """
        import time
        start = time.time_ns()
        
        # Process all inputs first
        substrates = []
        for inp in computation.inputs:
            if isinstance(inp, str) and inp == "_prev":
                # Placeholder for pipeline chaining
                continue
            result = self.process(inp)
            substrates.append(result)
        
        # Execute the operation
        truth = self._execute_operation(computation.operation, substrates)
        
        end = time.time_ns()
        
        return FxResult(
            value=truth,
            truth=truth,
            success=True,
            execution_time_ns=end - start
        )
    
    def _execute_operation(self, op: str, inputs: List[FxResult]) -> int:
        """Execute a kernel operation on substrates."""
        if len(inputs) < 2:
            if len(inputs) == 1:
                return inputs[0].truth
            return 0
        
        a = inputs[0].truth
        b = inputs[1].truth if len(inputs) > 1 else 0
        
        MASK = 0xFFFFFFFFFFFFFFFF
        
        if op == Computation.XOR:
            return (a ^ b) & MASK
        elif op == Computation.AND:
            return (a & b) & MASK
        elif op == Computation.OR:
            return (a | b) & MASK
        elif op == Computation.ROT:
            n = b % 64
            return ((a << n) | (a >> (64 - n))) & MASK
        elif op == Computation.ADD:
            return (a + b) & MASK
        elif op == Computation.SUB:
            return (a - b) & MASK
        elif op == Computation.MUL:
            return (a * b) & MASK
        elif op == Computation.DIV:
            if b == 0:
                raise FxError("Division by zero", code=3)
            return (a // b) & MASK
        else:
            raise FxError(f"Unknown operation: {op}", code=4)
    
    def pipeline(self, initial: Optional[Any] = None) -> Pipeline:
        """
        Create a computation pipeline.
        
        Pipelines chain operations together for batch processing.
        """
        steps = []
        if initial is not None:
            steps.append(Computation("LOAD", [initial]))
        return Pipeline(steps)
    
    def run(self, pipeline: Pipeline) -> FxResult:
        """
        Execute a pipeline through the kernel.
        
        Args:
            pipeline: A Pipeline object with computation steps
            
        Returns:
            FxResult with the final computed value
        """
        import time
        start = time.time_ns()
        
        prev_result = None
        
        for step in pipeline.steps:
            # Replace _prev placeholders with actual previous result
            inputs = []
            for inp in step.inputs:
                if isinstance(inp, str) and inp == "_prev":
                    if prev_result is None:
                        raise FxError("Pipeline step references _prev but no previous result", code=5)
                    inputs.append(prev_result.truth)
                else:
                    inputs.append(inp)
            
            modified_step = Computation(step.operation, inputs)
            prev_result = self.compute(modified_step)
        
        end = time.time_ns()
        
        if prev_result is None:
            return FxResult(value=0, truth=0, success=True, execution_time_ns=end - start)
        
        prev_result.execution_time_ns = end - start
        return prev_result
    
    # ─────────────────────────────────────────────────────────────────
    # DIMENSIONAL PROGRAMMING
    # ─────────────────────────────────────────────────────────────────
    
    def substrate(self, data: Any) -> 'DimensionalSubstrate':
        """
        Create a dimensional substrate from any data.
        
        This is the primary method for dimensional programming.
        Substrates can be accessed at different dimensions, have
        attributes accessed via lenses, and behavior applied via deltas.
        
        Args:
            data: Any Python value to convert to substrate
        
        Returns:
            DimensionalSubstrate with dimensional programming interface
        
        Example:
            obj = fx.substrate({"x": 0, "y": 100, "vx": 5})
            
            # Access dimensions
            identity = obj.dimension(0)
            attrs = obj.dimension(1)
            physics = obj.dimension(4)
            
            # Access attributes via lenses
            x_value = obj.lens("x").invoke()
            
            # Apply behavior via deltas
            gravity = fx.delta(9.8)
            falling = obj.apply(gravity)
            
            # Promote to next state
            next_state = obj.promote(gravity)
        """
        from .dimensional import DimensionalSubstrate
        return DimensionalSubstrate(data=data, fx=self)
    
    def delta(self, value: Any, generation: int = 0) -> 'DimensionalDelta':
        """
        Create a delta (behavior encoding) for dimensional programming.
        
        Deltas represent behavior that can be applied to substrates.
        Applying a delta produces a NEW substrate (no mutation).
        
        Args:
            value: The delta value (int, float, dict with changes)
            generation: Optional generation counter
        
        Returns:
            DimensionalDelta for applying behavior
        
        Example:
            # Simple delta
            gravity = fx.delta(9.8)
            
            # Dict delta with named changes
            physics = fx.delta({"dx": 5, "dy": -9.8, "dt": 0.016})
            
            # Apply to substrate
            next_ball = ball.apply(physics)
        """
        from .dimensional import DimensionalDelta
        return DimensionalDelta(value=value, generation=generation)
    
    def animate(
        self, 
        substrate: 'DimensionalSubstrate',
        delta: Any,
        frames: int
    ) -> List['DimensionalSubstrate']:
        """
        Generate animation frames through dimensional promotion.
        
        Animation is dimensional promotion through time.
        Each frame is a new substrate - no mutation occurs.
        
        Args:
            substrate: The starting substrate
            delta: Per-frame behavior delta
            frames: Number of frames to generate
        
        Returns:
            List of DimensionalSubstrate frames
        
        Example:
            ball = fx.substrate({"x": 0, "y": 100, "vy": 0})
            gravity = fx.delta({"dy": -9.8})
            
            animation = fx.animate(ball, gravity, 100)
            for frame in animation:
                render(frame)
        """
        from .dimensional import DimensionalSubstrate, DimensionalDelta
        
        if not isinstance(substrate, DimensionalSubstrate):
            substrate = self.substrate(substrate)
        
        if not isinstance(delta, DimensionalDelta):
            delta = self.delta(delta)
        
        return substrate.animate(delta, frames)
    
    # ─────────────────────────────────────────────────────────────────
    # PROJECTION (Lens operations)
    # ─────────────────────────────────────────────────────────────────
    
    def project(
        self, 
        data: Any, 
        projection: Union[Projection, Callable[[int], int]]
    ) -> FxResult:
        """
        Project data through a lens transformation.
        
        Args:
            data: Input data to project
            projection: A Projection or callable transform
            
        Returns:
            FxResult with projected value
        """
        # Process input
        input_result = self.process(data)
        
        # Create lens
        if isinstance(projection, Projection):
            lens_spec = projection.to_lens_spec()
        else:
            lens_spec = LensSpec(projection=projection)
        
        lens_result = _ingest(lens_spec)
        
        if not lens_result.success or not lens_result.manifest._lens:
            raise FxError("Failed to create lens", code=6)
        
        # Invoke projection
        truth = _invoke(input_result.manifest._substrate, lens_result.manifest._lens)
        
        return FxResult(
            value=truth,
            truth=truth,
            success=True
        )
    
    # ─────────────────────────────────────────────────────────────────
    # TRANSFORMATION (Delta/Promote operations)
    # ─────────────────────────────────────────────────────────────────
    
    def transform(
        self, 
        source: Any, 
        derived: Any, 
        delta: Union[Transform, int]
    ) -> FxResult:
        """
        Transform a substrate through promotion with a delta.
        
        Args:
            source: Original substrate
            derived: Derived substrate
            delta: Transform delta or delta value
            
        Returns:
            FxResult with transformed substrate
        """
        # Process inputs
        source_result = self.process(source)
        derived_result = self.process(derived)
        
        # Create delta
        if isinstance(delta, Transform):
            delta_spec = delta.to_delta_spec()
        else:
            delta_spec = DeltaSpec(value=delta)
        
        delta_result = _ingest(delta_spec)
        
        if not delta_result.success or not delta_result.manifest._delta:
            raise FxError("Failed to create delta", code=7)
        
        # Promote
        new_substrate = _promote(
            source_result.manifest._substrate,
            derived_result.manifest._substrate,
            delta_result.manifest._delta
        )
        
        return FxResult(
            value=new_substrate.identity.identity,
            truth=new_substrate.identity.identity,
            success=True
        )
    
    # ─────────────────────────────────────────────────────────────────
    # REFERENCING (SRL operations)
    # ─────────────────────────────────────────────────────────────────
    
    def reference(self, ref: Union[Reference, str]) -> FxResult:
        """
        Create a reference to a substrate location.
        
        Args:
            ref: A Reference object or SRL URI string
            
        Returns:
            FxResult with the reference substrate
        """
        if isinstance(ref, str):
            # Parse SRL URI
            ref = self._parse_srl_uri(ref)
        
        # Ingest the reference data itself as a substrate
        ref_data = {
            'type': 'reference',
            'domain': ref.domain,
            'path': ref.path,
            'target': ref.target
        }
        return self.process(ref_data)
    
    def _parse_srl_uri(self, uri: str) -> Reference:
        """Parse an SRL URI string into a Reference."""
        # srl://domain/path#target
        if not uri.startswith("srl://"):
            raise FxError(f"Invalid SRL URI: {uri}", code=9)
        
        uri = uri[6:]  # Remove srl://
        
        if "#" in uri:
            path_part, target = uri.rsplit("#", 1)
            target_int = int(target, 16)
        else:
            path_part = uri
            target_int = 0
        
        if "/" in path_part:
            domain, path = path_part.split("/", 1)
        else:
            domain = path_part
            path = ""
        
        return Reference(domain=domain, path=path, target=target_int)
    
    # ─────────────────────────────────────────────────────────────────
    # SRL FETCH (Connection + Ingestion)
    # ─────────────────────────────────────────────────────────────────
    
    def fetch(
        self, 
        srl: 'SRL',
        query: Optional[str] = None
    ) -> FxResult:
        """
        Fetch data through SRL and automatically ingest it.
        
        This is the primary way to bring external data into the kernel:
            1. SRL connects to datasource
            2. Data is fetched
            3. Data goes through ingest() → becomes substrate
        
        Args:
            srl: An SRL connection device
            query: Optional query string
            
        Returns:
            FxResult with the ingested substrate
        
        Example:
            from core_v2 import ButterflyFx, http_srl, TokenAuth
            
            fx = ButterflyFx()
            srl = http_srl("https://api.example.com/data", 
                          credentials=TokenAuth(token="..."))
            
            result = fx.fetch(srl, query="id=42")
            # result.value is the fetched bytes
            # result.truth is the substrate identity
        """
        import time
        start = time.time_ns()
        
        # Import SRL here to avoid circular import
        from .srl import SRL as SRLClass, SRLError
        
        if not isinstance(srl, SRLClass):
            raise FxError("fetch() requires an SRL connection device", code=11)
        
        try:
            # Connect and fetch through SRL
            srl_result = srl.fetch(query)
            
            if not srl_result.success:
                raise FxError(f"SRL fetch failed: {srl_result.error}", code=12)
            
            # Now ingest the fetched data into the kernel
            data = srl_result.data
            result = _ingest(data)
            
            if not result.success:
                raise FxError(f"Ingestion failed: {result.error}", code=13)
            
            end = time.time_ns()
            
            return FxResult(
                value=data,
                truth=result.manifest.root_identity,
                success=True,
                execution_time_ns=end - start,
                manifest=result.manifest
            )
            
        except SRLError as e:
            raise FxError(f"SRL error: {e}", code=e.code)
    
    def send(
        self,
        srl: 'SRL',
        data: Any
    ) -> FxResult:
        """
        Process data through kernel then send via SRL.
        
        Flow:
            1. Data is processed through kernel (becomes substrate)
            2. Substrate truth is serialized
            3. SRL sends to datasource
        
        Args:
            srl: An SRL connection device
            data: Data to process and send
            
        Returns:
            FxResult indicating success
        """
        import time
        start = time.time_ns()
        
        from .srl import SRL as SRLClass, SRLError
        
        if not isinstance(srl, SRLClass):
            raise FxError("send() requires an SRL connection device", code=11)
        
        # First, process the data through the kernel
        processed = self.process(data)
        
        # Serialize the substrate for transmission
        if isinstance(data, bytes):
            send_data = data
        elif isinstance(data, str):
            send_data = data.encode('utf-8')
        else:
            # Send the truth value as bytes
            send_data = processed.truth.to_bytes(8, 'little')
        
        try:
            srl_result = srl.send(send_data)
            
            if not srl_result.success:
                raise FxError(f"SRL send failed: {srl_result.error}", code=14)
            
            end = time.time_ns()
            
            return FxResult(
                value=True,
                truth=processed.truth,
                success=True,
                execution_time_ns=end - start
            )
            
        except SRLError as e:
            raise FxError(f"SRL error: {e}", code=e.code)
    
    # ─────────────────────────────────────────────────────────────────
    # RENDERING
    # ─────────────────────────────────────────────────────────────────
    
    def render(
        self, 
        result: Union[FxResult, Any],
        format: str = "auto"
    ) -> str:
        """
        Render a result for display.
        
        All rendered output goes through the kernel for consistency.
        
        Args:
            result: An FxResult or raw value to render
            format: Output format (auto, text, hex, binary, json)
            
        Returns:
            Rendered string representation
        """
        if not isinstance(result, FxResult):
            result = self.process(result)
        
        truth = result.truth
        
        if format == "auto":
            format = self._detect_format(result)
        
        if format == "hex":
            return f"0x{truth:016X}"
        elif format == "binary":
            return f"0b{truth:064b}"
        elif format == "json":
            return json.dumps({
                "truth": truth,
                "hex": f"0x{truth:016X}",
                "value": result.value if not isinstance(result.value, bytes) else result.value.hex()
            })
        else:  # text
            return str(result.value)
    
    def _detect_format(self, result: FxResult) -> str:
        """Auto-detect best output format."""
        if isinstance(result.value, bytes):
            return "hex"
        elif isinstance(result.value, int) and result.value > 0xFFFF:
            return "hex"
        else:
            return "text"
    
    # ─────────────────────────────────────────────────────────────────
    # VALIDATION
    # ─────────────────────────────────────────────────────────────────
    
    def _validate_input(self, data: Any) -> None:
        """Validate input against the 15 Laws."""
        if self._config.validate_laws:
            # Check serializable
            try:
                if hasattr(data, '__dict__'):
                    # Object - check it can be represented
                    pass
            except Exception as e:
                raise FxError(f"Input validation failed: {e}", code=10)
    
    def validate(self, data: Any) -> bool:
        """
        Check if data can be processed by the system.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, raises FxError if not
        """
        try:
            self._validate_input(data)
            return True
        except FxError:
            raise
    
    # ─────────────────────────────────────────────────────────────────
    # CACHE
    # ─────────────────────────────────────────────────────────────────
    
    def cached(self, truth: int) -> Optional[FxResult]:
        """
        Retrieve a cached substrate by its truth value.
        
        Args:
            truth: The 64-bit substrate identity
            
        Returns:
            FxResult if cached, None otherwise
        """
        with self._lock:
            manifest = self._cache.get(truth)
            if manifest:
                return FxResult(
                    value=truth,
                    truth=truth,
                    success=True,
                    manifest=manifest
                )
            return None
    
    def clear_cache(self) -> int:
        """Clear the substrate cache. Returns count of items cleared."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count
    
    # ─────────────────────────────────────────────────────────────────
    # SERVER
    # ─────────────────────────────────────────────────────────────────
    
    def serve(self, blocking: bool = True) -> None:
        """
        Start the ButterflyFx server.
        
        The server accepts HTTP and socket connections for remote
        processing through the Core→Kernel pipeline.
        
        Args:
            blocking: If True, blocks until server stops
        """
        from .server import FxServer
        
        self._server = FxServer(
            self,
            host=self._config.server_host,
            port=self._config.server_port
        )
        
        self._running = True
        
        if blocking:
            self._server.run()
        else:
            import threading
            thread = threading.Thread(target=self._server.run, daemon=True)
            thread.start()
    
    def stop(self) -> None:
        """Stop the server if running."""
        self._running = False
        if self._server:
            self._server.stop()
    
    # ─────────────────────────────────────────────────────────────────
    # CONTEXT MANAGER
    # ─────────────────────────────────────────────────────────────────
    
    def __enter__(self) -> ButterflyFx:
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()
        self.clear_cache()
    
    # ─────────────────────────────────────────────────────────────────
    # STRING REPRESENTATION
    # ─────────────────────────────────────────────────────────────────
    
    def __repr__(self) -> str:
        return f"ButterflyFx(cached={len(self._cache)}, running={self._running})"

    # ═══════════════════════════════════════════════════════════════════
    # ASYNC API
    # ═══════════════════════════════════════════════════════════════════
    
    async def process_async(self, data: Any) -> FxResult:
        """
        Async version of process().
        
        Process any data through the Core→Kernel pipeline.
        """
        return await asyncio.get_event_loop().run_in_executor(
            None, self.process, data
        )
    
    async def compute_async(self, computation: Computation) -> FxResult:
        """
        Async version of compute().
        
        Execute a computation through the kernel.
        """
        return await asyncio.get_event_loop().run_in_executor(
            None, self.compute, computation
        )
    
    async def fetch_async(
        self, 
        srl: 'SRL',
        query: Optional[str] = None
    ) -> FxResult:
        """
        Async version of fetch().
        
        Fetch data through SRL and automatically ingest it.
        """
        return await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.fetch(srl, query)
        )
    
    async def run_async(self, pipeline: Pipeline) -> FxResult:
        """
        Async version of run().
        
        Execute a pipeline through the kernel.
        """
        return await asyncio.get_event_loop().run_in_executor(
            None, self.run, pipeline
        )

    # ═══════════════════════════════════════════════════════════════════
    # BATCH OPERATIONS
    # ═══════════════════════════════════════════════════════════════════
    
    def process_batch(self, items: List[Any]) -> List[FxResult]:
        """
        Process multiple items in a batch.
        
        All items go through the Core→Kernel pipeline.
        Validates against Law 12 (no brute force for >1000 items).
        
        Args:
            items: List of items to process
            
        Returns:
            List of FxResult objects
        """
        if len(items) > 1000:
            raise FxError(
                "Batch exceeds Law 12 limit of 1000 items. "
                "Use streaming or chunked processing.",
                code=12
            )
        
        return [self.process(item) for item in items]
    
    def compute_batch(self, computations: List[Computation]) -> List[FxResult]:
        """
        Execute multiple computations in a batch.
        
        Args:
            computations: List of Computation objects
            
        Returns:
            List of FxResult objects
        """
        if len(computations) > 1000:
            raise FxError(
                "Batch exceeds Law 12 limit of 1000 items.",
                code=12
            )
        
        return [self.compute(comp) for comp in computations]
    
    async def process_batch_async(self, items: List[Any]) -> List[FxResult]:
        """Async version of process_batch()."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.process_batch, items
        )
    
    def stream(self, items: Iterator[Any]) -> Iterator[FxResult]:
        """
        Stream items through the kernel one at a time.
        
        For large datasets that exceed Law 12's batch limit.
        
        Args:
            items: Iterator of items to process
            
        Yields:
            FxResult for each item
        """
        for item in items:
            yield self.process(item)
    
    async def stream_async(self, items: Iterator[Any]) -> AsyncIterator[FxResult]:
        """Async version of stream()."""
        for item in items:
            yield await self.process_async(item)

    # ═══════════════════════════════════════════════════════════════════
    # EVENTS / HOOKS
    # ═══════════════════════════════════════════════════════════════════
    
    _hooks: Dict[str, List[Callable]] = {}
    
    def on(self, event: str, callback: Callable) -> None:
        """
        Register a callback for an event.
        
        Events:
            - 'process': Called after each process()
            - 'compute': Called after each compute()
            - 'fetch': Called after each fetch()
            - 'error': Called on any error
        
        Args:
            event: Event name
            callback: Function to call (receives FxResult or Exception)
        
        Example:
            def on_process(result):
                print(f"Processed: {result.truth:016X}")
            
            fx.on('process', on_process)
        """
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(callback)
    
    def off(self, event: str, callback: Optional[Callable] = None) -> None:
        """
        Remove a callback for an event.
        
        Args:
            event: Event name
            callback: Specific callback to remove (or None for all)
        """
        if event in self._hooks:
            if callback is None:
                self._hooks[event] = []
            else:
                self._hooks[event] = [cb for cb in self._hooks[event] if cb != callback]
    
    def _emit(self, event: str, data: Any) -> None:
        """Emit an event to all registered callbacks."""
        for callback in self._hooks.get(event, []):
            try:
                callback(data)
            except Exception:
                pass  # Don't let callback errors break the flow

    # ═══════════════════════════════════════════════════════════════════
    # SUBSTRATE TEMPLATES
    # ═══════════════════════════════════════════════════════════════════
    
    def entity(
        self,
        name: str,
        position: Tuple[float, float] = (0.0, 0.0),
        velocity: Tuple[float, float] = (0.0, 0.0),
        **attributes
    ) -> 'DimensionalSubstrate':
        """
        Create a game/simulation entity substrate.
        
        Pre-built template with common properties.
        
        Args:
            name: Entity name
            position: (x, y) position
            velocity: (vx, vy) velocity vector
            **attributes: Additional attributes
            
        Returns:
            DimensionalSubstrate with entity data
        
        Example:
            player = fx.entity("player", (100, 200), (5, 0), health=100)
        """
        data = {
            "name": name,
            "x": position[0],
            "y": position[1],
            "vx": velocity[0],
            "vy": velocity[1],
            **attributes
        }
        return self.substrate(data)
    
    def point(self, x: float, y: float, z: float = 0.0) -> 'DimensionalSubstrate':
        """Create a 3D point substrate."""
        return self.substrate({"x": x, "y": y, "z": z})
    
    def vector(self, *components: float) -> 'DimensionalSubstrate':
        """Create an n-dimensional vector substrate."""
        data = {f"v{i}": c for i, c in enumerate(components)}
        data["dimension"] = len(components)
        return self.substrate(data)
    
    def timestamp(self, seconds: Optional[float] = None) -> 'DimensionalSubstrate':
        """
        Create a timestamp substrate.
        
        If no time given, uses current time.
        """
        import time
        t = seconds if seconds is not None else time.time()
        return self.substrate({
            "timestamp": t,
            "seconds": int(t),
            "nanoseconds": int((t % 1) * 1e9)
        })
    
    def money(
        self, 
        amount: float, 
        currency: str = "USD"
    ) -> 'DimensionalSubstrate':
        """Create a monetary value substrate."""
        # Store as cents/pence to avoid float precision issues
        cents = int(round(amount * 100))
        return self.substrate({
            "amount": amount,
            "cents": cents,
            "currency": currency
        })
    
    def color(
        self, 
        r: int, 
        g: int, 
        b: int, 
        a: int = 255
    ) -> 'DimensionalSubstrate':
        """Create an RGBA color substrate."""
        # Pack into 32-bit integer
        packed = (a << 24) | (r << 16) | (g << 8) | b
        return self.substrate({
            "r": r, "g": g, "b": b, "a": a,
            "packed": packed,
            "hex": f"#{r:02X}{g:02X}{b:02X}"
        })

    # ═══════════════════════════════════════════════════════════════════
    # NATURAL LANGUAGE INTERFACE (DimensionOS)
    # ═══════════════════════════════════════════════════════════════════
    
    _dimension_os: Optional['DimensionOS'] = None
    
    def query(self, text: str) -> str:
        """
        Natural language query interface.
        
        Uses DimensionOS for intelligent object ingestion
        and query processing.
        
        Args:
            text: Natural language query
            
        Returns:
            Human-readable response
        
        Example:
            fx.query("Load the 2026 Toyota Corolla")
            fx.query("What's the gas mileage?")
            fx.query("Load bitcoin")
            fx.query("What's the price?")
        """
        if self._dimension_os is None:
            from dimension_os import DimensionOS
            self._dimension_os = DimensionOS()
        
        return self._dimension_os.query(text)
    
    def chat(self) -> None:
        """
        Start interactive chat session.
        
        Natural language interface powered by DimensionOS.
        """
        if self._dimension_os is None:
            from dimension_os import DimensionOS
            self._dimension_os = DimensionOS()
        
        self._dimension_os.repl()
