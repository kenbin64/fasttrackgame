"""
ButterflyFX Assembler - File Reconstruction from Manifold Data

Copyright (c) 2024-2026 Kenneth Bingham. All Rights Reserved.

This is a DERIVED IMPLEMENTATION built on the open source mathematical kernel.
This file is proprietary software. See /helix/LICENSE for details.

---

The Assembler takes ingested substrate data and reconstructs actual file types.
Data is never permanently saved - it exists in the manifold and materializes on demand.

Virtual File System Mapping:
    - Spiral (dimension) → Folder
    - Level → File category/type
    - Ingested data → File contents

Supported File Types:
    - Text: .txt, .json, .csv, .xml, .html, .md
    - Binary: .png, .jpg, .gif, .bmp
    - Audio: .mp3, .wav, .ogg
    - Video: .mp4, .avi, .webm
    - Document: .pdf
    - Archive: .zip

PRINCIPLE:
    The manifold IS the storage. Files are just views into dimensional data.
    Assemble on demand, never persist permanently.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Tuple, BinaryIO, Callable, TYPE_CHECKING
from pathlib import Path
from enum import Enum, auto
import base64
import json
import io
import struct
import zlib
import os

if TYPE_CHECKING:
    from .substrate import ManifoldSubstrate


# =============================================================================
# FILE TYPE REGISTRY
# =============================================================================

class FileCategory(Enum):
    """Maps to helix levels"""
    BINARY = 0       # Level 0: Raw binary data
    AUDIO = 1        # Level 1: Audio files
    IMAGE = 2        # Level 2: Image files  
    VIDEO = 3        # Level 3: Video files
    DOCUMENT = 4     # Level 4: Document files
    STRUCTURED = 5   # Level 5: Structured data (JSON, XML)
    TEXT = 6         # Level 6: Plain text


EXTENSION_MAP: Dict[str, FileCategory] = {
    # Binary
    '.bin': FileCategory.BINARY,
    '.dat': FileCategory.BINARY,
    
    # Audio
    '.mp3': FileCategory.AUDIO,
    '.wav': FileCategory.AUDIO,
    '.ogg': FileCategory.AUDIO,
    '.flac': FileCategory.AUDIO,
    
    # Image
    '.png': FileCategory.IMAGE,
    '.jpg': FileCategory.IMAGE,
    '.jpeg': FileCategory.IMAGE,
    '.gif': FileCategory.IMAGE,
    '.bmp': FileCategory.IMAGE,
    '.webp': FileCategory.IMAGE,
    
    # Video
    '.mp4': FileCategory.VIDEO,
    '.avi': FileCategory.VIDEO,
    '.webm': FileCategory.VIDEO,
    '.mkv': FileCategory.VIDEO,
    '.mov': FileCategory.VIDEO,
    
    # Document
    '.pdf': FileCategory.DOCUMENT,
    '.doc': FileCategory.DOCUMENT,
    '.docx': FileCategory.DOCUMENT,
    
    # Structured
    '.json': FileCategory.STRUCTURED,
    '.xml': FileCategory.STRUCTURED,
    '.yaml': FileCategory.STRUCTURED,
    '.yml': FileCategory.STRUCTURED,
    '.csv': FileCategory.STRUCTURED,
    
    # Text
    '.txt': FileCategory.TEXT,
    '.md': FileCategory.TEXT,
    '.html': FileCategory.TEXT,
    '.htm': FileCategory.TEXT,
    '.py': FileCategory.TEXT,
    '.js': FileCategory.TEXT,
    '.ts': FileCategory.TEXT,
    '.css': FileCategory.TEXT,
}


def get_category(extension: str) -> FileCategory:
    """Get category for file extension"""
    return EXTENSION_MAP.get(extension.lower(), FileCategory.BINARY)


def get_level(extension: str) -> int:
    """Get helix level for file extension"""
    return get_category(extension).value


# =============================================================================
# FILE ASSEMBLER - Reconstruct files from substrate data
# =============================================================================

@dataclass
class AssembledFile:
    """
    A file reconstructed from manifold data.
    
    The file exists in memory, materialized from substrate coordinates.
    """
    name: str
    extension: str
    data: bytes
    source_coords: Tuple[int, int]  # (spiral, level)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def size(self) -> int:
        return len(self.data)
    
    @property
    def category(self) -> FileCategory:
        return get_category(self.extension)
    
    def write_to(self, path: Union[str, Path]) -> Path:
        """Materialize to disk (temporary manifestation)"""
        path = Path(path)
        path.write_bytes(self.data)
        return path
    
    def as_stream(self) -> BinaryIO:
        """Get as file-like stream"""
        return io.BytesIO(self.data)
    
    def as_base64(self) -> str:
        """Encode as base64 string"""
        return base64.b64encode(self.data).decode('utf-8')
    
    def __repr__(self) -> str:
        return f"AssembledFile({self.name}{self.extension}, {self.size} bytes, from {self.source_coords})"


class FileAssembler:
    """
    Assembles files from manifold substrate data.
    
    The assembler reconstructs actual files from ingested data.
    Files are assembled on-demand, never permanently stored.
    
    Usage:
        assembler = FileAssembler(substrate)
        
        # Ingest file data
        assembler.ingest_file("image.png", image_bytes, spiral=0)
        
        # Assemble (reconstruct) the file
        file = assembler.assemble("image.png", spiral=0)
        file.write_to("output.png")
    """
    
    def __init__(self, substrate: 'ManifoldSubstrate'):
        self.substrate = substrate
        self._file_registry: Dict[str, Tuple[int, int]] = {}  # name -> (spiral, level)
        self._metadata: Dict[str, Dict] = {}
    
    # -------------------------------------------------------------------------
    # Ingestion - Take file data into the manifold
    # -------------------------------------------------------------------------
    
    def ingest_file(
        self,
        filename: str,
        data: Union[bytes, str, Path],
        spiral: int = 0,
        level: Optional[int] = None
    ) -> Tuple[int, int]:
        """
        Ingest a file into the manifold.
        
        The file data is assimilated into substrate coordinates.
        Level is automatically determined from file extension if not provided.
        
        Args:
            filename: Name of the file (with extension)
            data: File data as bytes, string, or Path to read from
            spiral: Which spiral/dimension to store in
            level: Which level (auto-determined from extension if None)
        
        Returns:
            (spiral, level) coordinates where data was stored
        """
        # Get actual bytes
        if isinstance(data, Path):
            data = data.read_bytes()
        elif isinstance(data, str):
            if os.path.exists(data):
                data = Path(data).read_bytes()
            else:
                data = data.encode('utf-8')
        
        # Determine level from extension
        ext = Path(filename).suffix
        if level is None:
            level = get_level(ext)
        
        # Store as base64 for text-safe storage
        encoded = base64.b64encode(data).decode('utf-8')
        
        # Ingest into substrate
        self.substrate.ingest_keyed(spiral, level, filename, encoded)
        
        # Register file location
        self._file_registry[filename] = (spiral, level)
        self._metadata[filename] = {
            'size': len(data),
            'extension': ext,
            'category': get_category(ext).name,
            'spiral': spiral,
            'level': level,
        }
        
        return (spiral, level)
    
    def ingest_directory(
        self,
        directory: Union[str, Path],
        spiral: int = 0,
        recursive: bool = True
    ) -> Dict[str, Tuple[int, int]]:
        """
        Ingest all files from a directory into the manifold.
        
        Each file goes to its category level within the specified spiral.
        
        Args:
            directory: Path to directory
            spiral: Which spiral to use
            recursive: Whether to include subdirectories
        
        Returns:
            Dict mapping filenames to coordinates
        """
        directory = Path(directory)
        results = {}
        
        pattern = '**/*' if recursive else '*'
        for path in directory.glob(pattern):
            if path.is_file():
                rel_path = path.relative_to(directory)
                coords = self.ingest_file(str(rel_path), path, spiral=spiral)
                results[str(rel_path)] = coords
        
        return results
    
    # -------------------------------------------------------------------------
    # Assembly - Reconstruct files from manifold data
    # -------------------------------------------------------------------------
    
    def assemble(
        self,
        filename: str,
        spiral: Optional[int] = None,
        level: Optional[int] = None
    ) -> Optional[AssembledFile]:
        """
        Assemble (reconstruct) a file from manifold data.
        
        The file is materialized from its substrate coordinates.
        
        Args:
            filename: Name of the file to assemble
            spiral: Which spiral (uses registry if not provided)
            level: Which level (uses registry if not provided)
        
        Returns:
            AssembledFile if found, None otherwise
        """
        # Look up coordinates
        if spiral is None or level is None:
            if filename not in self._file_registry:
                return None
            reg_spiral, reg_level = self._file_registry[filename]
            spiral = spiral if spiral is not None else reg_spiral
            level = level if level is not None else reg_level
        
        # Extract from substrate
        encoded = self.substrate.extract_keyed(spiral, level, filename)
        if encoded is None:
            return None
        
        # Decode from base64
        try:
            data = base64.b64decode(encoded)
        except Exception:
            # Maybe it's raw data
            data = encoded if isinstance(encoded, bytes) else encoded.encode('utf-8')
        
        # Get extension
        ext = Path(filename).suffix
        name = Path(filename).stem
        
        return AssembledFile(
            name=name,
            extension=ext,
            data=data,
            source_coords=(spiral, level),
            metadata=self._metadata.get(filename, {})
        )
    
    def assemble_all(self, spiral: int) -> List[AssembledFile]:
        """
        Assemble all files from a spiral.
        
        Returns all files stored in the given spiral/dimension.
        """
        files = []
        for filename, (s, l) in self._file_registry.items():
            if s == spiral:
                assembled = self.assemble(filename)
                if assembled:
                    files.append(assembled)
        return files
    
    def assemble_by_category(
        self,
        category: FileCategory,
        spiral: Optional[int] = None
    ) -> List[AssembledFile]:
        """
        Assemble all files of a specific category.
        
        Args:
            category: FileCategory to filter by
            spiral: Specific spiral, or all if None
        """
        files = []
        level = category.value
        
        for filename, (s, l) in self._file_registry.items():
            if l == level and (spiral is None or s == spiral):
                assembled = self.assemble(filename)
                if assembled:
                    files.append(assembled)
        
        return files
    
    # -------------------------------------------------------------------------
    # Registry Operations
    # -------------------------------------------------------------------------
    
    def list_files(self, spiral: Optional[int] = None) -> List[str]:
        """List all registered filenames"""
        if spiral is None:
            return list(self._file_registry.keys())
        return [f for f, (s, _) in self._file_registry.items() if s == spiral]
    
    def get_metadata(self, filename: str) -> Optional[Dict]:
        """Get metadata for a file"""
        return self._metadata.get(filename)
    
    def has_file(self, filename: str) -> bool:
        """Check if file exists in registry"""
        return filename in self._file_registry
    
    def remove_file(self, filename: str) -> bool:
        """Remove file from manifold"""
        if filename not in self._file_registry:
            return False
        
        spiral, level = self._file_registry[filename]
        self.substrate.remove_keyed(spiral, level, filename)
        del self._file_registry[filename]
        self._metadata.pop(filename, None)
        return True
    
    @property
    def file_count(self) -> int:
        return len(self._file_registry)
    
    def __repr__(self) -> str:
        return f"FileAssembler({self.file_count} files registered)"


# =============================================================================
# MANIFOLD FILE SYSTEM - Virtual FS backed by substrate
# =============================================================================

@dataclass
class VirtualEntry:
    """Entry in the virtual file system"""
    name: str
    is_directory: bool
    size: int = 0
    children: List[str] = field(default_factory=list)
    coords: Optional[Tuple[int, int, str]] = None  # (spiral, level, key)


class ManifoldFileSystem:
    """
    Virtual File System backed by the manifold substrate.
    
    Presents dimensional data as a navigable file system:
        /spiral_0/          <- Dimension 0 as folder
            level_0/        <- Binary category
            level_1/        <- Audio category
            level_2/        <- Image category
            ...
            level_6/        <- Text category
        /spiral_1/          <- Dimension 1 as folder
            ...
    
    Files are assembled on-demand when accessed.
    
    Usage:
        fs = ManifoldFileSystem(substrate)
        
        # Navigate
        entries = fs.list("/spiral_0")
        
        # Read file
        content = fs.read("/spiral_0/level_2/image.png")
        
        # Write file
        fs.write("/spiral_0/level_6/notes.txt", b"Hello")
    """
    
    def __init__(self, substrate: 'ManifoldSubstrate'):
        self.substrate = substrate
        self.assembler = FileAssembler(substrate)
        self._path_cache: Dict[str, VirtualEntry] = {}
    
    # -------------------------------------------------------------------------
    # Path Parsing
    # -------------------------------------------------------------------------
    
    def _parse_path(self, path: str) -> Tuple[Optional[int], Optional[int], Optional[str]]:
        """
        Parse path into (spiral, level, filename).
        
        Path format: /spiral_N/level_M/filename
        Or: /spiral_N/filename (level determined by extension)
        """
        parts = [p for p in path.strip('/').split('/') if p]
        
        spiral = None
        level = None
        filename = None
        
        for part in parts:
            if part.startswith('spiral_'):
                try:
                    spiral = int(part.split('_')[1])
                except (IndexError, ValueError):
                    pass
            elif part.startswith('level_'):
                try:
                    level = int(part.split('_')[1])
                except (IndexError, ValueError):
                    pass
            elif '.' in part:
                filename = part
                if level is None:
                    level = get_level(Path(part).suffix)
        
        return spiral, level, filename
    
    def _make_path(self, spiral: int, level: Optional[int] = None, filename: Optional[str] = None) -> str:
        """Construct path from components"""
        path = f"/spiral_{spiral}"
        if level is not None:
            path += f"/level_{level}"
            if filename:
                path += f"/{filename}"
        return path
    
    # -------------------------------------------------------------------------
    # File System Operations
    # -------------------------------------------------------------------------
    
    def list(self, path: str = "/") -> List[VirtualEntry]:
        """
        List entries at path.
        
        Returns list of VirtualEntry objects.
        """
        path = path.strip('/')
        entries = []
        
        if not path:
            # Root - list spirals
            spirals = set()
            for (s, l, k) in self.substrate._ingested_keyed.keys():
                spirals.add(s)
            for (s, l) in self.substrate._ingested.keys():
                spirals.add(s)
            
            for s in sorted(spirals):
                entries.append(VirtualEntry(
                    name=f"spiral_{s}",
                    is_directory=True,
                    children=self._get_spiral_children(s)
                ))
        
        elif path.startswith('spiral_'):
            parts = path.split('/')
            spiral = int(parts[0].split('_')[1])
            
            if len(parts) == 1:
                # List levels in spiral
                for level in range(7):
                    level_files = self._get_level_files(spiral, level)
                    if level_files:
                        entries.append(VirtualEntry(
                            name=f"level_{level}",
                            is_directory=True,
                            children=level_files
                        ))
            
            elif len(parts) >= 2 and parts[1].startswith('level_'):
                # List files in level
                level = int(parts[1].split('_')[1])
                for filename in self._get_level_files(spiral, level):
                    meta = self.assembler.get_metadata(filename) or {}
                    entries.append(VirtualEntry(
                        name=filename,
                        is_directory=False,
                        size=meta.get('size', 0),
                        coords=(spiral, level, filename)
                    ))
        
        return entries
    
    def _get_spiral_children(self, spiral: int) -> List[str]:
        """Get level folder names for a spiral"""
        levels = set()
        for (s, l, k) in self.substrate._ingested_keyed.keys():
            if s == spiral:
                levels.add(l)
        return [f"level_{l}" for l in sorted(levels)]
    
    def _get_level_files(self, spiral: int, level: int) -> List[str]:
        """Get filenames at (spiral, level)"""
        files = []
        for (s, l, k) in self.substrate._ingested_keyed.keys():
            if s == spiral and l == level:
                files.append(k)
        return files
    
    def read(self, path: str) -> Optional[bytes]:
        """
        Read file at path.
        
        Assembles the file from manifold data and returns bytes.
        """
        spiral, level, filename = self._parse_path(path)
        
        if spiral is None or filename is None:
            return None
        
        assembled = self.assembler.assemble(filename, spiral, level)
        return assembled.data if assembled else None
    
    def write(self, path: str, data: bytes) -> Tuple[int, int]:
        """
        Write file to path.
        
        Ingests data into manifold at appropriate coordinates.
        """
        spiral, level, filename = self._parse_path(path)
        
        if spiral is None:
            spiral = 0
        if filename is None:
            raise ValueError("Path must include filename")
        
        return self.assembler.ingest_file(filename, data, spiral, level)
    
    def exists(self, path: str) -> bool:
        """Check if path exists"""
        spiral, level, filename = self._parse_path(path)
        
        if spiral is None:
            return False
        
        if filename:
            return self.assembler.has_file(filename)
        
        # Check if spiral has any data
        for (s, l) in self.substrate._ingested.keys():
            if s == spiral and (level is None or l == level):
                return True
        for (s, l, k) in self.substrate._ingested_keyed.keys():
            if s == spiral and (level is None or l == level):
                return True
        
        return False
    
    def delete(self, path: str) -> bool:
        """Delete file at path"""
        spiral, level, filename = self._parse_path(path)
        
        if filename:
            return self.assembler.remove_file(filename)
        return False
    
    def mkdir(self, path: str) -> bool:
        """
        Create directory (spiral or level).
        
        In the manifold FS, directories are implicit.
        This is a no-op that returns True.
        """
        return True
    
    # -------------------------------------------------------------------------
    # Tree View
    # -------------------------------------------------------------------------
    
    def tree(self, path: str = "/", indent: int = 0) -> str:
        """
        Generate tree view of file system.
        
        Returns string representation like Unix `tree` command.
        """
        lines = []
        prefix = "    " * indent
        
        for entry in self.list(path):
            icon = "📁" if entry.is_directory else "📄"
            size = f" ({entry.size} bytes)" if not entry.is_directory else ""
            lines.append(f"{prefix}{icon} {entry.name}{size}")
            
            if entry.is_directory:
                child_path = f"{path.rstrip('/')}/{entry.name}"
                lines.append(self.tree(child_path, indent + 1))
        
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        spirals = len(set(s for s, l in self.substrate._ingested.keys()))
        files = self.assembler.file_count
        return f"ManifoldFileSystem({spirals} spirals, {files} files)"


# =============================================================================
# QUICK ASSEMBLER FUNCTIONS
# =============================================================================

def assemble_text(data: Union[str, bytes]) -> str:
    """Quick assemble text data"""
    if isinstance(data, bytes):
        return data.decode('utf-8')
    return data


def assemble_json(data: Union[str, bytes, dict]) -> dict:
    """Quick assemble JSON data"""
    if isinstance(data, dict):
        return data
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    return json.loads(data)


def assemble_binary(data: Union[str, bytes]) -> bytes:
    """Quick assemble binary data from base64"""
    if isinstance(data, bytes):
        return data
    try:
        return base64.b64decode(data)
    except Exception:
        return data.encode('utf-8')


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'FileCategory',
    'EXTENSION_MAP',
    'get_category',
    'get_level',
    'AssembledFile',
    'FileAssembler',
    'VirtualEntry',
    'ManifoldFileSystem',
    'assemble_text',
    'assemble_json',
    'assemble_binary',
]
