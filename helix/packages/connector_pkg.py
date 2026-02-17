"""
ButterflyFX Universal Connector
================================

Copyright (c) 2024-2026 Kenneth Bingham - All Rights Reserved
https://butterflyfx.us

The Universal Connector embodies the ButterflyFX philosophy:
GAIN ABILITIES by connecting and ingesting outside sources.

This substrate discovers, wraps, and unifies external capabilities
into the substrate system. It doesn't duplicate - it CONNECTS.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Type
import subprocess
import importlib
import sys
import os

# Setup path for standalone execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kernel_primitives import Substrate
from licensing import requires_license


@dataclass
class Capability:
    """A discovered external capability"""
    name: str
    source: str  # 'python', 'cli', 'api', 'file'
    available: bool = False
    version: Optional[str] = None
    module: Optional[Any] = None
    path: Optional[str] = None
    description: str = ""
    
    def invoke(self, *args, **kwargs) -> Any:
        """Invoke this capability"""
        raise NotImplementedError


@dataclass  
class PythonCapability(Capability):
    """Python package capability"""
    source: str = "python"
    
    def invoke(self, method: str, *args, **kwargs) -> Any:
        if not self.available or not self.module:
            raise RuntimeError(f"Capability {self.name} not available")
        func = getattr(self.module, method)
        return func(*args, **kwargs)


@dataclass
class CLICapability(Capability):
    """Command-line tool capability"""
    source: str = "cli"
    
    def invoke(self, *args, timeout: int = 60) -> subprocess.CompletedProcess:
        if not self.available or not self.path:
            raise RuntimeError(f"Capability {self.name} not available")
        cmd = [self.path] + list(args)
        return subprocess.run(cmd, capture_output=True, timeout=timeout, text=True)


class CapabilityRegistry:
    """Central registry of discovered capabilities"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._capabilities: Dict[str, Capability] = {}
            cls._instance._domains: Dict[str, List[str]] = {}
        return cls._instance
    
    def register(self, cap: Capability, domain: str = "general"):
        self._capabilities[cap.name] = cap
        if domain not in self._domains:
            self._domains[domain] = []
        self._domains[domain].append(cap.name)
    
    def get(self, name: str) -> Optional[Capability]:
        return self._capabilities.get(name)
    
    def list_domain(self, domain: str) -> List[Capability]:
        return [self._capabilities[n] for n in self._domains.get(domain, [])]
    
    def list_available(self) -> List[Capability]:
        return [c for c in self._capabilities.values() if c.available]


REGISTRY = CapabilityRegistry()


@requires_license("graphics")  # Starter tier - basic connector
class UniversalConnector(Substrate):
    """
    The Universal Connector - discovers and ingests external capabilities.
    
    Philosophy: Don't reinvent - CONNECT. The substrate gains abilities
    by wrapping and unifying external tools into the helix system.
    """
    
    def __init__(self):
        super().__init__("universal_connector")
        self.registry = REGISTRY
        self._discovered = False
        self._init_operations()
    
    @property
    def domain(self) -> str:
        return "system.connector"
    
    def _init_operations(self):
        self.register_operation("discover", self.discover_all)
        self.register_operation("get", self.get_capability)
        self.register_operation("list", self.list_capabilities)
        self.register_operation("ingest_python", self.ingest_python_package)
        self.register_operation("ingest_cli", self.ingest_cli_tool)
    
    def discover_all(self) -> Dict[str, List[str]]:
        """
        Discover all available external capabilities.
        
        Scans for:
        - Python packages (video, audio, image, AI)
        - CLI tools (ffmpeg, espeak, etc.)
        - System capabilities
        """
        if self._discovered:
            return {domain: [c.name for c in caps] 
                    for domain, caps in self._group_by_domain().items()}
        
        discovered = {
            "video": [],
            "audio": [],
            "image": [],
            "speech": [],
            "ai": [],
            "cli": [],
        }
        
        # === VIDEO CAPABILITIES ===
        
        # MoviePy - video editing
        cap = self._probe_python("moviepy", "moviepy.editor", 
            "Video editing and composition")
        if cap.available:
            discovered["video"].append(cap.name)
            self.registry.register(cap, "video")
        
        # OpenCV - computer vision
        cap = self._probe_python("opencv", "cv2",
            "Computer vision and video processing")
        if cap.available:
            discovered["video"].append(cap.name)
            self.registry.register(cap, "video")
        
        # === AUDIO CAPABILITIES ===
        
        # Pydub - audio manipulation
        cap = self._probe_python("pydub", "pydub",
            "Audio manipulation and conversion")
        if cap.available:
            discovered["audio"].append(cap.name)
            self.registry.register(cap, "audio")
        
        # Scipy - signal processing
        cap = self._probe_python("scipy_audio", "scipy.io.wavfile",
            "WAV file I/O and signal processing")
        if cap.available:
            discovered["audio"].append(cap.name)
            self.registry.register(cap, "audio")
        
        # === IMAGE CAPABILITIES ===
        
        # PIL/Pillow
        cap = self._probe_python("pillow", "PIL.Image",
            "Image manipulation and format conversion")
        if cap.available:
            discovered["image"].append(cap.name)
            self.registry.register(cap, "image")
        
        # Numpy
        cap = self._probe_python("numpy", "numpy",
            "Numerical arrays for pixel manipulation")
        if cap.available:
            discovered["image"].append(cap.name)
            self.registry.register(cap, "image")
        
        # === SPEECH CAPABILITIES ===
        
        # gTTS - Google TTS
        cap = self._probe_python("gtts", "gtts",
            "Google Text-to-Speech")
        if cap.available:
            discovered["speech"].append(cap.name)
            self.registry.register(cap, "speech")
        
        # pyttsx3 - offline TTS
        cap = self._probe_python("pyttsx3", "pyttsx3",
            "Offline text-to-speech engine")
        if cap.available:
            discovered["speech"].append(cap.name)
            self.registry.register(cap, "speech")
        
        # === AI CAPABILITIES ===
        
        # Transformers
        cap = self._probe_python("transformers", "transformers",
            "Hugging Face Transformers for AI models")
        if cap.available:
            discovered["ai"].append(cap.name)
            self.registry.register(cap, "ai")
        
        # Diffusers (Stable Diffusion)
        cap = self._probe_python("diffusers", "diffusers",
            "Stable Diffusion and diffusion models")
        if cap.available:
            discovered["ai"].append(cap.name)
            self.registry.register(cap, "ai")
        
        # === CLI TOOLS ===
        
        # ffmpeg
        cap = self._probe_cli("ffmpeg", "ffmpeg",
            "Video/audio encoding and conversion")
        if cap.available:
            discovered["cli"].append(cap.name)
            self.registry.register(cap, "cli")
        
        # espeak
        cap = self._probe_cli("espeak", "espeak",
            "Command-line speech synthesis")
        if cap.available:
            discovered["cli"].append(cap.name)
            self.registry.register(cap, "speech")
        
        # ImageMagick
        cap = self._probe_cli("imagemagick", "convert",
            "Image manipulation and conversion")
        if cap.available:
            discovered["cli"].append(cap.name)
            self.registry.register(cap, "image")
        
        self._discovered = True
        return discovered
    
    def _probe_python(self, name: str, module_path: str, desc: str) -> PythonCapability:
        """Probe for a Python package"""
        cap = PythonCapability(name=name, description=desc)
        try:
            parts = module_path.split('.')
            mod = importlib.import_module(parts[0])
            for part in parts[1:]:
                mod = getattr(mod, part)
            cap.module = mod
            cap.available = True
            cap.version = getattr(mod, '__version__', 'unknown')
        except (ImportError, AttributeError):
            cap.available = False
        return cap
    
    def _probe_cli(self, name: str, command: str, desc: str) -> CLICapability:
        """Probe for a CLI tool"""
        cap = CLICapability(name=name, description=desc)
        try:
            result = subprocess.run(['which', command], capture_output=True, text=True)
            if result.returncode == 0:
                cap.path = result.stdout.strip()
                cap.available = True
                # Try to get version
                try:
                    ver = subprocess.run([command, '-version'], capture_output=True, text=True, timeout=5)
                    cap.version = ver.stdout.split('\n')[0][:50] if ver.stdout else 'unknown'
                except:
                    cap.version = 'unknown'
        except:
            cap.available = False
        return cap
    
    def get_capability(self, name: str) -> Optional[Capability]:
        """Get a capability by name"""
        return self.registry.get(name)
    
    def list_capabilities(self, available_only: bool = True) -> List[Dict]:
        """List all capabilities"""
        caps = self.registry.list_available() if available_only else list(self.registry._capabilities.values())
        return [{"name": c.name, "source": c.source, "available": c.available, 
                 "version": c.version, "description": c.description} for c in caps]
    
    def ingest_python_package(self, package_name: str, module_path: str = None,
                              domain: str = "general") -> bool:
        """
        Ingest a Python package into the system.
        
        This is the key ButterflyFX concept - GAINING ABILITIES
        by connecting external sources.
        """
        module_path = module_path or package_name
        cap = self._probe_python(package_name, module_path, f"Ingested: {package_name}")
        if cap.available:
            self.registry.register(cap, domain)
            return True
        return False
    
    def ingest_cli_tool(self, name: str, command: str, domain: str = "cli") -> bool:
        """Ingest a CLI tool into the system"""
        cap = self._probe_cli(name, command, f"Ingested: {command}")
        if cap.available:
            self.registry.register(cap, domain)
            return True
        return False
    
    def _group_by_domain(self) -> Dict[str, List[Capability]]:
        """Group capabilities by domain"""
        return {domain: [self.registry.get(n) for n in names] 
                for domain, names in self.registry._domains.items()}


# =============================================================================
# Convenience function
# =============================================================================

def discover_capabilities() -> Dict[str, List[str]]:
    """Discover all available external capabilities"""
    connector = UniversalConnector()
    return connector.discover_all()


__all__ = [
    'Capability',
    'PythonCapability',
    'CLICapability',
    'CapabilityRegistry',
    'UniversalConnector',
    'REGISTRY',
    'discover_capabilities',
]
