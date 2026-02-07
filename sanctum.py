"""
Sanctum Enforcer - Layer Boundary Protection

Enforces the three-layer sanctum architecture:
- Kernel: Inner sanctum, pure math, no external access
- Core: Bridge layer, sole Kernel accessor
- Interface: External access point, talks only to Core

This module provides:
1. Import guards to detect layer violations
2. Runtime checks for boundary crossings
3. Static analysis helpers for CI/CD
"""

from __future__ import annotations
import sys
import importlib
from typing import Dict, List, Set, Tuple


class SanctumViolation(Exception):
    """Raised when layer boundaries are violated"""
    pass


class LayerBoundary:
    """Defines allowed import relationships between layers"""
    
    KERNEL = "kernel"
    CORE = "core"
    INTERFACE = "interface"
    
    # Allowed imports: layer → set of layers it can import from
    ALLOWED_IMPORTS: Dict[str, Set[str]] = {
        KERNEL: set(),           # Kernel imports NOTHING
        CORE: {KERNEL},          # Core imports only Kernel
        INTERFACE: {CORE},       # Interface imports only Core
    }
    
    # Reverse: what can import each layer
    ALLOWED_IMPORTERS: Dict[str, Set[str]] = {
        KERNEL: {CORE},          # Only Core can import Kernel
        CORE: {INTERFACE},       # Only Interface can import Core
        INTERFACE: set(),        # Nothing imports Interface (external only)
    }


class SanctumEnforcer:
    """
    Enforces layer boundaries at runtime and provides static checks.
    """
    
    def __init__(self):
        self._violations: List[Tuple[str, str, str]] = []
    
    def check_import(
        self, 
        importer_module: str, 
        imported_module: str
    ) -> None:
        """
        Verify an import respects layer boundaries.
        
        Args:
            importer_module: Full module path of the importing module
            imported_module: Full module path being imported
            
        Raises:
            SanctumViolation if boundary is crossed
        """
        importer_layer = self._get_layer(importer_module)
        imported_layer = self._get_layer(imported_module)
        
        if importer_layer is None or imported_layer is None:
            return  # External module, not our concern
        
        if importer_layer == imported_layer:
            return  # Same layer, always OK
        
        allowed = LayerBoundary.ALLOWED_IMPORTS.get(importer_layer, set())
        
        if imported_layer not in allowed:
            violation = (
                f"Sanctum violation: {importer_layer} cannot import from "
                f"{imported_layer}. Allowed: {allowed or 'none'}"
            )
            self._violations.append((importer_layer, imported_layer, violation))
            raise SanctumViolation(violation)
    
    def _get_layer(self, module_path: str) -> str | None:
        """Determine which layer a module belongs to"""
        parts = module_path.split('.')
        
        if not parts:
            return None
        
        root = parts[0]
        if root == LayerBoundary.KERNEL:
            return LayerBoundary.KERNEL
        elif root == LayerBoundary.CORE:
            return LayerBoundary.CORE
        elif root == LayerBoundary.INTERFACE:
            return LayerBoundary.INTERFACE
        
        return None
    
    def get_violations(self) -> List[Tuple[str, str, str]]:
        """Return all recorded violations"""
        return self._violations.copy()
    
    def clear_violations(self) -> None:
        """Clear recorded violations"""
        self._violations.clear()


class StaticAnalyzer:
    """
    Static analysis for layer boundary compliance.
    
    For use in CI/CD pipelines and pre-commit hooks.
    """
    
    @staticmethod
    def analyze_imports(file_path: str) -> List[str]:
        """
        Analyze a Python file for potential layer violations.
        
        Returns list of violation messages.
        """
        violations = []
        
        # Determine which layer this file belongs to
        if '/kernel/' in file_path or '\\kernel\\' in file_path:
            current_layer = LayerBoundary.KERNEL
        elif '/core/' in file_path or '\\core\\' in file_path:
            current_layer = LayerBoundary.CORE
        elif '/interface/' in file_path or '\\interface\\' in file_path:
            current_layer = LayerBoundary.INTERFACE
        else:
            return []  # Not in our layers
        
        # Parse imports
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return [f"Cannot read {file_path}: {e}"]
        
        import ast
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return [f"Syntax error in {file_path}: {e}"]
        
        allowed = LayerBoundary.ALLOWED_IMPORTS.get(current_layer, set())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    layer = StaticAnalyzer._module_to_layer(alias.name)
                    if layer and layer != current_layer and layer not in allowed:
                        violations.append(
                            f"{file_path}: {current_layer} imports {layer} "
                            f"(module: {alias.name})"
                        )
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    layer = StaticAnalyzer._module_to_layer(node.module)
                    if layer and layer != current_layer and layer not in allowed:
                        violations.append(
                            f"{file_path}: {current_layer} imports from {layer} "
                            f"(module: {node.module})"
                        )
        
        return violations
    
    @staticmethod
    def _module_to_layer(module_name: str) -> str | None:
        """Map module name to layer"""
        if module_name.startswith('kernel'):
            return LayerBoundary.KERNEL
        elif module_name.startswith('core'):
            return LayerBoundary.CORE
        elif module_name.startswith('interface'):
            return LayerBoundary.INTERFACE
        return None


# Global enforcer instance
_enforcer = SanctumEnforcer()


def enforce_sanctum():
    """Enable runtime sanctum enforcement via import hooks"""
    import builtins
    
    _original_import = builtins.__import__
    
    def sanctum_import(name, globals=None, locals=None, fromlist=(), level=0):
        result = _original_import(name, globals, locals, fromlist, level)
        
        # Determine caller's module
        if globals and '__name__' in globals:
            caller = globals['__name__']
            try:
                _enforcer.check_import(caller, name)
            except SanctumViolation:
                raise
        
        return result
    
    builtins.__import__ = sanctum_import
