"""
Ingest - THE ONLY gateway for data to enter the Kernel.

═══════════════════════════════════════════════════════════════════
                    SINGULAR ENTRY POINT
═══════════════════════════════════════════════════════════════════

ALL data entering the kernel MUST pass through ingest().
There is NO other way. All other paths are closed.

    ingest(anything) → Substrate | Lens | SRL

This function is overloaded to handle:
    - Raw values (int, float, bool, str, bytes)
    - Files and file paths
    - Source code
    - Data structures (dict, list, JSON)
    - Python packages
    - AI models
    - Streams and iterators
    - Lens definitions (become Lens substrates)
    - SRL definitions (become SRL substrates)

EVERYTHING becomes a substrate. Lens and SRL are special substrates
that also act upon other substrates.

═══════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
import hashlib
import json
import struct
import os
import mimetypes
from pathlib import Path
from typing import (
    Any, Dict, List, Optional, Union, BinaryIO, 
    Iterator, Callable, Tuple, TypeVar, overload
)
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from functools import singledispatch
import importlib.util

# Internal kernel access - NOT exposed publicly
from kernel_v2 import (
    SubstrateIdentity,
    Substrate,
    Lens,
    Delta,
    Dimension,
    Manifold,
    promote as kernel_promote,
    invoke as kernel_invoke,
    SRL,
    create_srl_identity,
)

__all__ = [
    'ingest',
    'invoke',
    'promote',
    'Ingest',
    'SubstrateManifest',
    'IngestResult',
    'AssetType',
    'LensSpec',
    'DeltaSpec',
    'DimensionSpec',
]


# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════

MASK_64 = 0xFFFFFFFFFFFFFFFF
CHUNK_SIZE = 8  # 8 bytes = 64 bits per chunk


class AssetType:
    """Asset type identifiers (encoded in substrate metadata)."""
    UNKNOWN = 0x0000
    # Primitives
    INTEGER = 0x0001
    FLOAT = 0x0002
    BOOLEAN = 0x0003
    STRING = 0x0004
    BYTES = 0x0005
    # Files
    FILE_TEXT = 0x0010
    FILE_BINARY = 0x0011
    FILE_IMAGE = 0x0012
    FILE_AUDIO = 0x0013
    FILE_VIDEO = 0x0014
    # Code
    SOURCE_CODE = 0x0020
    PACKAGE = 0x0021
    # Data
    DATA_JSON = 0x0030
    DATA_XML = 0x0031
    DATA_CSV = 0x0032
    DATA_DICT = 0x0033
    DATA_LIST = 0x0034
    # Special Substrates
    LENS = 0x0100
    SRL = 0x0101
    DELTA = 0x0102
    DIMENSION = 0x0103
    MANIFOLD = 0x0104
    # AI
    AI_MODEL = 0x0200
    AI_WEIGHTS = 0x0201
    # Streams
    STREAM = 0x0300


# ═══════════════════════════════════════════════════════════════════
# SPEC CLASSES - Definitions for special substrates
# ═══════════════════════════════════════════════════════════════════

@dataclass
class LensSpec:
    """
    Specification for creating a Lens substrate.
    
    A Lens is a substrate that projects other substrates.
    
    Usage:
        lens = ingest(LensSpec(
            lens_id=0x01,
            projection=lambda x: x * 2
        ))
    """
    projection: Callable[[int], int]
    lens_id: Optional[int] = None
    name: Optional[str] = None
    
    def __post_init__(self):
        if self.lens_id is None:
            # Generate ID from projection
            self.lens_id = hash(self.projection.__code__.co_code) & MASK_64


@dataclass
class SRLSpec:
    """
    Specification for creating an SRL substrate.
    
    An SRL locates and references other substrates.
    
    Usage:
        srl = ingest(SRLSpec(
            domain="butterflyfx",
            path="entities/player",
            target_identity=0xDEADBEEF
        ))
    """
    domain: str
    path: str
    target_identity: int
    
    @property
    def uri(self) -> str:
        return f"srl://{self.domain}/{self.path}#{self.target_identity:016x}"


@dataclass
class DeltaSpec:
    """
    Specification for creating a Delta (change encoding).
    
    Usage:
        delta = ingest(DeltaSpec(value=42))
    """
    value: int


@dataclass
class DimensionSpec:
    """Specification for creating a Dimension."""
    level: int


# ═══════════════════════════════════════════════════════════════════
# SUBSTRATE MANIFEST
# ═══════════════════════════════════════════════════════════════════

@dataclass
class SubstrateManifest:
    """Complete substrate representation of an ingested asset."""
    root_identity: int
    asset_type: int
    original_size: int
    chunk_count: int
    chunk_identities: List[int]
    metadata_identity: int
    structure_identity: Optional[int] = None
    content_hash: Tuple[int, int, int, int] = (0, 0, 0, 0)
    source: Optional[str] = None
    
    # The actual kernel objects (internal)
    _substrate: Optional[Substrate] = field(default=None, repr=False)
    _lens: Optional[Lens] = field(default=None, repr=False)
    _srl: Optional[SRL] = field(default=None, repr=False)
    _delta: Optional[Delta] = field(default=None, repr=False)
    
    @property
    def substrate(self) -> Optional[Substrate]:
        """Get the underlying Substrate object."""
        return self._substrate
    
    @property
    def lens(self) -> Optional[Lens]:
        """Get as Lens if this is a lens substrate."""
        return self._lens
    
    @property
    def srl(self) -> Optional[SRL]:
        """Get as SRL if this is an SRL substrate."""
        return self._srl
    
    @property
    def delta(self) -> Optional[Delta]:
        """Get as Delta if this is a delta substrate."""
        return self._delta
    
    def is_lens(self) -> bool:
        return self.asset_type == AssetType.LENS
    
    def is_srl(self) -> bool:
        return self.asset_type == AssetType.SRL
    
    def is_delta(self) -> bool:
        return self.asset_type == AssetType.DELTA


@dataclass 
class IngestResult:
    """Result of an ingestion operation."""
    success: bool
    manifest: Optional[SubstrateManifest]
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    @property
    def substrate(self) -> Optional[Substrate]:
        """Convenience: get substrate from manifest."""
        return self.manifest.substrate if self.manifest else None
    
    @property
    def lens(self) -> Optional[Lens]:
        """Convenience: get lens from manifest."""
        return self.manifest.lens if self.manifest else None
    
    @property
    def srl(self) -> Optional[SRL]:
        """Convenience: get SRL from manifest."""
        return self.manifest.srl if self.manifest else None
    
    @property 
    def identity(self) -> Optional[int]:
        """Convenience: get root identity."""
        return self.manifest.root_identity if self.manifest else None


# ═══════════════════════════════════════════════════════════════════
# INTERNAL KERNEL ACCESSOR
# ═══════════════════════════════════════════════════════════════════

class _KernelAccess:
    """
    Internal kernel accessor - NOT EXPOSED.
    
    This provides the actual connection to kernel primitives.
    Only the Ingest class may use this.
    """
    
    @staticmethod
    def create_identity(value: int) -> SubstrateIdentity:
        return SubstrateIdentity(value)
    
    @staticmethod
    def create_substrate(identity: SubstrateIdentity, 
                         expression: Callable[[], int]) -> Substrate:
        return Substrate(identity, expression)
    
    @staticmethod
    def create_lens(lens_id: int, 
                    projection: Callable[[int], int]) -> Lens:
        return Lens(lens_id, projection)
    
    @staticmethod
    def create_delta(value: int) -> Delta:
        return Delta(value)
    
    @staticmethod
    def create_dimension(level: int) -> Dimension:
        return Dimension(level)
    
    @staticmethod
    def create_srl(domain: str, path: str, 
                   identity: SubstrateIdentity) -> SRL:
        return SRL(domain, path, identity)
    
    @staticmethod
    def invoke(substrate: Substrate, lens: Lens) -> int:
        return kernel_invoke(substrate, lens)
    
    @staticmethod
    def promote(x1: SubstrateIdentity, y1: int, 
                delta: Delta) -> SubstrateIdentity:
        return kernel_promote(x1, y1, delta)


# Private kernel access
_kernel = _KernelAccess()


# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def _hash_to_identity(data: bytes) -> int:
    """Hash bytes to 64-bit identity."""
    h = hashlib.sha256(data).digest()
    return int.from_bytes(h[:8], 'little') & MASK_64


def _bytes_to_chunks(data: bytes) -> List[int]:
    """Convert bytes to 64-bit chunks."""
    chunks = []
    padded = data + b'\x00' * (8 - len(data) % 8) if len(data) % 8 != 0 else data
    for i in range(0, len(padded), 8):
        chunk = int.from_bytes(padded[i:i+8], 'little') & MASK_64
        chunks.append(chunk)
    return chunks


def _content_hash(data: bytes) -> Tuple[int, int, int, int]:
    """SHA-256 as 4 x 64-bit values."""
    h = hashlib.sha256(data).digest()
    return (
        int.from_bytes(h[0:8], 'little') & MASK_64,
        int.from_bytes(h[8:16], 'little') & MASK_64,
        int.from_bytes(h[16:24], 'little') & MASK_64,
        int.from_bytes(h[24:32], 'little') & MASK_64,
    )


def _float_to_bits(f: float) -> int:
    """IEEE 754 double to 64-bit int."""
    return struct.unpack('<Q', struct.pack('<d', f))[0]


# ═══════════════════════════════════════════════════════════════════
# MAIN INGEST CLASS
# ═══════════════════════════════════════════════════════════════════

class Ingest:
    """
    THE ONLY entry point for data into the Kernel.
    
    All paths to the kernel are closed except through ingest().
    
    Usage:
        ing = Ingest()
        
        # Primitives
        result = ing(42)
        result = ing(3.14159)
        result = ing("hello")
        result = ing(b"bytes")
        
        # Collections
        result = ing([1, 2, 3])
        result = ing({"key": "value"})
        
        # Files
        result = ing(Path("file.txt"))
        
        # Lens (special substrate)
        result = ing(LensSpec(projection=lambda x: x * 2))
        
        # SRL (special substrate)
        result = ing(SRLSpec(domain="app", path="entity", target_identity=0x123))
        
        # Delta (change encoding)
        result = ing(DeltaSpec(value=7))
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton - one ingest point."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
    
    def __call__(self, asset: Any, **kwargs) -> IngestResult:
        """
        Ingest any asset into the kernel.
        
        This is the ONLY way data enters the kernel.
        """
        return self.ingest(asset, **kwargs)
    
    def ingest(self, asset: Any, **kwargs) -> IngestResult:
        """
        Universal ingest - handles any type.
        
        The method dispatches based on asset type.
        """
        try:
            # Special substrates first
            if isinstance(asset, LensSpec):
                return self._ingest_lens(asset)
            
            if isinstance(asset, SRLSpec):
                return self._ingest_srl(asset)
            
            if isinstance(asset, DeltaSpec):
                return self._ingest_delta(asset)
            
            if isinstance(asset, DimensionSpec):
                return self._ingest_dimension(asset)
            
            # Already-ingested manifests (pass through)
            if isinstance(asset, SubstrateManifest):
                return IngestResult(success=True, manifest=asset)
            
            if isinstance(asset, IngestResult):
                return asset
            
            # Primitives
            if isinstance(asset, bool):
                return self._ingest_bool(asset)
            
            if isinstance(asset, int):
                return self._ingest_int(asset)
            
            if isinstance(asset, float):
                return self._ingest_float(asset)
            
            if isinstance(asset, str):
                return self._ingest_string(asset, **kwargs)
            
            if isinstance(asset, (bytes, bytearray, memoryview)):
                return self._ingest_bytes(bytes(asset))
            
            # Collections
            if isinstance(asset, dict):
                return self._ingest_dict(asset)
            
            if isinstance(asset, (list, tuple)):
                return self._ingest_list(list(asset))
            
            # File paths
            if isinstance(asset, Path):
                return self._ingest_file(asset)
            
            # Callables become lenses
            if callable(asset):
                return self._ingest_lens(LensSpec(projection=asset))
            
            # Iterators/generators become streams
            if hasattr(asset, '__iter__') and hasattr(asset, '__next__'):
                return self._ingest_stream(asset)
            
            # Fallback: convert to string and ingest
            return self._ingest_string(str(asset))
            
        except Exception as e:
            return IngestResult(success=False, manifest=None, error=str(e))
    
    # ═══════════════════════════════════════════════════════════════
    # PRIMITIVE INGESTORS
    # ═══════════════════════════════════════════════════════════════
    
    def _ingest_int(self, value: int) -> IngestResult:
        """Ingest integer."""
        identity = _kernel.create_identity(value)
        substrate = _kernel.create_substrate(identity, lambda v=value: v & MASK_64)
        
        manifest = SubstrateManifest(
            root_identity=identity.value,
            asset_type=AssetType.INTEGER,
            original_size=8,
            chunk_count=1,
            chunk_identities=[identity.value],
            metadata_identity=_hash_to_identity(b'int'),
            _substrate=substrate,
        )
        return IngestResult(success=True, manifest=manifest)
    
    def _ingest_float(self, value: float) -> IngestResult:
        """Ingest float (IEEE 754)."""
        bits = _float_to_bits(value)
        identity = _kernel.create_identity(bits)
        substrate = _kernel.create_substrate(identity, lambda b=bits: b)
        
        manifest = SubstrateManifest(
            root_identity=identity.value,
            asset_type=AssetType.FLOAT,
            original_size=8,
            chunk_count=1,
            chunk_identities=[identity.value],
            metadata_identity=_hash_to_identity(b'float'),
            _substrate=substrate,
        )
        return IngestResult(success=True, manifest=manifest)
    
    def _ingest_bool(self, value: bool) -> IngestResult:
        """Ingest boolean."""
        int_val = 1 if value else 0
        identity = _kernel.create_identity(int_val)
        substrate = _kernel.create_substrate(identity, lambda v=int_val: v)
        
        manifest = SubstrateManifest(
            root_identity=identity.value,
            asset_type=AssetType.BOOLEAN,
            original_size=1,
            chunk_count=1,
            chunk_identities=[identity.value],
            metadata_identity=_hash_to_identity(b'bool'),
            _substrate=substrate,
        )
        return IngestResult(success=True, manifest=manifest)
    
    def _ingest_string(self, value: str, **kwargs) -> IngestResult:
        """Ingest string."""
        # Check if it's a file path
        if kwargs.get('as_file') or (os.path.exists(value) and not kwargs.get('as_string')):
            return self._ingest_file(Path(value))
        
        data = value.encode('utf-8')
        return self._ingest_bytes_as_type(data, AssetType.STRING, source=None)
    
    def _ingest_bytes(self, data: bytes) -> IngestResult:
        """Ingest raw bytes."""
        return self._ingest_bytes_as_type(data, AssetType.BYTES)
    
    def _ingest_bytes_as_type(self, data: bytes, asset_type: int, 
                               source: str = None) -> IngestResult:
        """Core bytes ingestion with type specification."""
        chunks = _bytes_to_chunks(data)
        content_hash = _content_hash(data)
        
        # Root identity from content
        root_id = content_hash[0] ^ content_hash[1] ^ content_hash[2] ^ content_hash[3]
        identity = _kernel.create_identity(root_id)
        
        # Create chunk identities
        chunk_identities = []
        for i, chunk in enumerate(chunks):
            chunk_id = chunk ^ (i & MASK_64)
            chunk_identities.append(chunk_id)
        
        # Create substrate with expression that returns root
        substrate = _kernel.create_substrate(identity, lambda r=root_id: r)
        
        manifest = SubstrateManifest(
            root_identity=root_id,
            asset_type=asset_type,
            original_size=len(data),
            chunk_count=len(chunks),
            chunk_identities=chunk_identities,
            metadata_identity=_hash_to_identity(f'type:{asset_type}'.encode()),
            content_hash=content_hash,
            source=source,
            _substrate=substrate,
        )
        return IngestResult(success=True, manifest=manifest)
    
    # ═══════════════════════════════════════════════════════════════
    # COLLECTION INGESTORS
    # ═══════════════════════════════════════════════════════════════
    
    def _ingest_dict(self, data: dict) -> IngestResult:
        """Ingest dictionary."""
        json_bytes = json.dumps(data, sort_keys=True).encode('utf-8')
        result = self._ingest_bytes_as_type(json_bytes, AssetType.DATA_DICT)
        
        if result.success and result.manifest:
            # Add structure info
            result.manifest.structure_identity = _hash_to_identity(
                json.dumps({'keys': list(data.keys())}).encode()
            )
        return result
    
    def _ingest_list(self, data: list) -> IngestResult:
        """Ingest list."""
        json_bytes = json.dumps(data).encode('utf-8')
        result = self._ingest_bytes_as_type(json_bytes, AssetType.DATA_LIST)
        
        if result.success and result.manifest:
            result.manifest.structure_identity = _hash_to_identity(
                json.dumps({'length': len(data)}).encode()
            )
        return result
    
    def _ingest_file(self, path: Path) -> IngestResult:
        """Ingest file from filesystem."""
        try:
            with open(path, 'rb') as f:
                data = f.read()
            
            # Determine type from extension
            mime_type, _ = mimetypes.guess_type(str(path))
            if mime_type:
                if mime_type.startswith('text/'):
                    asset_type = AssetType.FILE_TEXT
                elif mime_type.startswith('image/'):
                    asset_type = AssetType.FILE_IMAGE
                elif mime_type.startswith('audio/'):
                    asset_type = AssetType.FILE_AUDIO
                elif mime_type.startswith('video/'):
                    asset_type = AssetType.FILE_VIDEO
                else:
                    asset_type = AssetType.FILE_BINARY
            else:
                asset_type = AssetType.FILE_BINARY
            
            result = self._ingest_bytes_as_type(data, asset_type, str(path.absolute()))
            return result
            
        except Exception as e:
            return IngestResult(success=False, manifest=None, error=str(e))
    
    def _ingest_stream(self, stream: Iterator) -> IngestResult:
        """Ingest iterator/stream."""
        MAX_SIZE = 100 * 1024 * 1024  # 100MB
        chunks = []
        total = 0
        
        for chunk in stream:
            if isinstance(chunk, str):
                chunk = chunk.encode('utf-8')
            chunks.append(chunk)
            total += len(chunk)
            if total > MAX_SIZE:
                break
        
        data = b''.join(chunks)
        return self._ingest_bytes_as_type(data, AssetType.STREAM)
    
    # ═══════════════════════════════════════════════════════════════
    # SPECIAL SUBSTRATE INGESTORS
    # ═══════════════════════════════════════════════════════════════
    
    def _ingest_lens(self, spec: LensSpec) -> IngestResult:
        """
        Ingest Lens specification.
        
        A Lens is a special substrate that also acts upon other substrates.
        """
        lens = _kernel.create_lens(spec.lens_id, spec.projection)
        identity = _kernel.create_identity(spec.lens_id)
        
        # Lens is ALSO a substrate (its identity can be operated on)
        substrate = _kernel.create_substrate(identity, lambda lid=spec.lens_id: lid)
        
        manifest = SubstrateManifest(
            root_identity=spec.lens_id,
            asset_type=AssetType.LENS,
            original_size=8,
            chunk_count=1,
            chunk_identities=[spec.lens_id],
            metadata_identity=_hash_to_identity(
                f'lens:{spec.name or spec.lens_id}'.encode()
            ),
            _substrate=substrate,
            _lens=lens,
        )
        return IngestResult(success=True, manifest=manifest)
    
    def _ingest_srl(self, spec: SRLSpec) -> IngestResult:
        """
        Ingest SRL specification.
        
        An SRL is a special substrate that locates other substrates.
        """
        target_identity = _kernel.create_identity(spec.target_identity)
        srl = _kernel.create_srl(spec.domain, spec.path, target_identity)
        
        srl_id = _hash_to_identity(spec.uri.encode())
        identity = _kernel.create_identity(srl_id)
        
        # SRL is ALSO a substrate
        substrate = _kernel.create_substrate(identity, lambda sid=srl_id: sid)
        
        manifest = SubstrateManifest(
            root_identity=srl_id,
            asset_type=AssetType.SRL,
            original_size=len(spec.uri),
            chunk_count=1,
            chunk_identities=[srl_id],
            metadata_identity=_hash_to_identity(spec.uri.encode()),
            source=spec.uri,
            _substrate=substrate,
            _srl=srl,
        )
        return IngestResult(success=True, manifest=manifest)
    
    def _ingest_delta(self, spec: DeltaSpec) -> IngestResult:
        """Ingest Delta (change encoding)."""
        delta = _kernel.create_delta(spec.value)
        identity = _kernel.create_identity(spec.value)
        substrate = _kernel.create_substrate(identity, lambda v=spec.value: v)
        
        manifest = SubstrateManifest(
            root_identity=spec.value & MASK_64,
            asset_type=AssetType.DELTA,
            original_size=8,
            chunk_count=1,
            chunk_identities=[spec.value & MASK_64],
            metadata_identity=_hash_to_identity(b'delta'),
            _substrate=substrate,
            _delta=delta,
        )
        return IngestResult(success=True, manifest=manifest)
    
    def _ingest_dimension(self, spec: DimensionSpec) -> IngestResult:
        """Ingest Dimension."""
        dim = _kernel.create_dimension(spec.level)
        identity = _kernel.create_identity(spec.level)
        substrate = _kernel.create_substrate(identity, lambda l=spec.level: l)
        
        manifest = SubstrateManifest(
            root_identity=spec.level,
            asset_type=AssetType.DIMENSION,
            original_size=8,
            chunk_count=1,
            chunk_identities=[spec.level],
            metadata_identity=_hash_to_identity(b'dimension'),
            _substrate=substrate,
        )
        return IngestResult(success=True, manifest=manifest)
    
    # ═══════════════════════════════════════════════════════════════
    # KERNEL OPERATIONS (through ingested substrates)
    # ═══════════════════════════════════════════════════════════════
    
    def invoke(self, substrate: Union[SubstrateManifest, IngestResult],
               lens: Union[SubstrateManifest, IngestResult, LensSpec, Callable]) -> int:
        """
        Invoke substrate through lens.
        
        Both must have been ingested first.
        """
        # Get substrate
        if isinstance(substrate, IngestResult):
            substrate = substrate.manifest
        if substrate._substrate is None:
            raise ValueError("Substrate not properly ingested")
        
        # Get or create lens
        if callable(lens) and not isinstance(lens, (LensSpec, SubstrateManifest, IngestResult)):
            lens = self._ingest_lens(LensSpec(projection=lens)).manifest
        if isinstance(lens, LensSpec):
            lens = self._ingest_lens(lens).manifest
        if isinstance(lens, IngestResult):
            lens = lens.manifest
        if lens._lens is None:
            raise ValueError("Lens not properly ingested")
        
        return _kernel.invoke(substrate._substrate, lens._lens)
    
    def promote(self, 
                substrate: Union[SubstrateManifest, IngestResult],
                derived: int,
                delta: Union[SubstrateManifest, IngestResult, DeltaSpec, int]) -> IngestResult:
        """
        Promote substrate through delta.
        
        Returns a NEW ingested substrate (original unchanged).
        """
        # Get substrate identity
        if isinstance(substrate, IngestResult):
            substrate = substrate.manifest
        identity = _kernel.create_identity(substrate.root_identity)
        
        # Get or create delta
        if isinstance(delta, int):
            delta = self._ingest_delta(DeltaSpec(value=delta)).manifest
        if isinstance(delta, DeltaSpec):
            delta = self._ingest_delta(delta).manifest
        if isinstance(delta, IngestResult):
            delta = delta.manifest
        if delta._delta is None:
            raise ValueError("Delta not properly ingested")
        
        # Promote
        new_identity = _kernel.promote(identity, derived, delta._delta)
        
        # Ingest the result
        return self._ingest_int(new_identity.value)
    
    # ═══════════════════════════════════════════════════════════════
    # BATCH OPERATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def bulk(self, assets: List[Any]) -> List[IngestResult]:
        """Ingest multiple assets."""
        return [self.ingest(a) for a in assets]
    
    def directory(self, path: Union[str, Path], pattern: str = "**/*") -> List[IngestResult]:
        """Ingest all matching files in directory."""
        path = Path(path)
        results = []
        for file_path in path.glob(pattern):
            if file_path.is_file():
                results.append(self._ingest_file(file_path))
        return results


# ═══════════════════════════════════════════════════════════════════
# MODULE-LEVEL SINGLETON
# ═══════════════════════════════════════════════════════════════════

# The ONE ingest instance
_ingest = Ingest()


def ingest(asset: Any, **kwargs) -> IngestResult:
    """
    THE ONLY way data enters the kernel.
    
    Usage:
        from core_v2 import ingest
        
        result = ingest(42)
        result = ingest("hello")
        result = ingest({"key": "value"})
        result = ingest(Path("file.txt"))
        result = ingest(LensSpec(projection=lambda x: x * 2))
        result = ingest(SRLSpec(domain="app", path="entity", target_identity=0x123))
    
    Returns IngestResult with SubstrateManifest containing:
        - substrate: The kernel Substrate object
        - lens: The kernel Lens (if LensSpec was ingested)
        - srl: The kernel SRL (if SRLSpec was ingested)
        - root_identity: The 64-bit identity
    """
    return _ingest.ingest(asset, **kwargs)


def invoke(substrate, lens) -> int:
    """Invoke substrate through lens (both must be ingested)."""
    return _ingest.invoke(substrate, lens)


def promote(substrate, derived: int, delta) -> IngestResult:
    """Promote substrate through delta (returns new ingested substrate)."""
    return _ingest.promote(substrate, derived, delta)
