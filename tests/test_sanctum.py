"""
Test Suite: Sanctum Layer Boundaries

Tests verifying the three-layer sanctum architecture:
- Kernel: Pure math, no external imports
- Core: Only imports Kernel
- Interface: Only imports Core

These tests ensure layer boundaries are respected.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sanctum import (
    SanctumEnforcer,
    SanctumViolation,
    LayerBoundary,
    StaticAnalyzer,
)


class TestLayerBoundaryRules:
    """Test layer boundary definitions"""
    
    def test_kernel_imports_nothing(self):
        """Kernel layer has no allowed imports"""
        allowed = LayerBoundary.ALLOWED_IMPORTS[LayerBoundary.KERNEL]
        assert allowed == set()
    
    def test_core_imports_only_kernel(self):
        """Core layer imports only Kernel"""
        allowed = LayerBoundary.ALLOWED_IMPORTS[LayerBoundary.CORE]
        assert allowed == {LayerBoundary.KERNEL}
    
    def test_interface_imports_only_core(self):
        """Interface layer imports only Core"""
        allowed = LayerBoundary.ALLOWED_IMPORTS[LayerBoundary.INTERFACE]
        assert allowed == {LayerBoundary.CORE}
    
    def test_only_core_imports_kernel(self):
        """Only Core can import from Kernel"""
        importers = LayerBoundary.ALLOWED_IMPORTERS[LayerBoundary.KERNEL]
        assert importers == {LayerBoundary.CORE}
    
    def test_only_interface_imports_core(self):
        """Only Interface can import from Core"""
        importers = LayerBoundary.ALLOWED_IMPORTERS[LayerBoundary.CORE]
        assert importers == {LayerBoundary.INTERFACE}


class TestSanctumEnforcer:
    """Test runtime sanctum enforcement"""
    
    @pytest.fixture
    def enforcer(self):
        e = SanctumEnforcer()
        e.clear_violations()
        return e
    
    def test_same_layer_allowed(self, enforcer):
        """Same layer imports are allowed"""
        # Should not raise
        enforcer.check_import("kernel.substrate", "kernel.manifold")
        enforcer.check_import("core.gateway", "core.translator")
        enforcer.check_import("interface.human", "interface.dto")
    
    def test_core_importing_kernel_allowed(self, enforcer):
        """Core importing Kernel is allowed"""
        # Should not raise
        enforcer.check_import("core.gateway", "kernel.substrate")
    
    def test_interface_importing_core_allowed(self, enforcer):
        """Interface importing Core is allowed"""
        # Should not raise
        enforcer.check_import("interface.human", "core.gateway")
    
    def test_interface_importing_kernel_forbidden(self, enforcer):
        """Interface importing Kernel is forbidden"""
        with pytest.raises(SanctumViolation, match="cannot import"):
            enforcer.check_import("interface.human", "kernel.substrate")
    
    def test_kernel_importing_core_forbidden(self, enforcer):
        """Kernel importing Core is forbidden"""
        with pytest.raises(SanctumViolation, match="cannot import"):
            enforcer.check_import("kernel.substrate", "core.gateway")
    
    def test_kernel_importing_interface_forbidden(self, enforcer):
        """Kernel importing Interface is forbidden"""
        with pytest.raises(SanctumViolation, match="cannot import"):
            enforcer.check_import("kernel.substrate", "interface.human")
    
    def test_core_importing_interface_forbidden(self, enforcer):
        """Core importing Interface is forbidden"""
        with pytest.raises(SanctumViolation, match="cannot import"):
            enforcer.check_import("core.gateway", "interface.human")
    
    def test_external_modules_ignored(self, enforcer):
        """External modules are not checked"""
        # Should not raise - external modules not in our layers
        enforcer.check_import("kernel.substrate", "typing")
        enforcer.check_import("interface.human", "pytest")
    
    def test_violations_tracked(self, enforcer):
        """Violations are recorded"""
        try:
            enforcer.check_import("interface.human", "kernel.substrate")
        except SanctumViolation:
            pass
        
        violations = enforcer.get_violations()
        assert len(violations) == 1
        assert violations[0][0] == "interface"
        assert violations[0][1] == "kernel"
    
    def test_violations_cleared(self, enforcer):
        """Violations can be cleared"""
        try:
            enforcer.check_import("interface.human", "kernel.substrate")
        except SanctumViolation:
            pass
        
        enforcer.clear_violations()
        assert len(enforcer.get_violations()) == 0


class TestStaticAnalyzer:
    """Test static analysis for CI/CD"""
    
    def test_module_to_layer_kernel(self):
        """Correctly identifies kernel modules"""
        assert StaticAnalyzer._module_to_layer("kernel") == "kernel"
        assert StaticAnalyzer._module_to_layer("kernel.substrate") == "kernel"
    
    def test_module_to_layer_core(self):
        """Correctly identifies core modules"""
        assert StaticAnalyzer._module_to_layer("core") == "core"
        assert StaticAnalyzer._module_to_layer("core.gateway") == "core"
    
    def test_module_to_layer_interface(self):
        """Correctly identifies interface modules"""
        assert StaticAnalyzer._module_to_layer("interface") == "interface"
        assert StaticAnalyzer._module_to_layer("interface.human") == "interface"
    
    def test_module_to_layer_external(self):
        """External modules return None"""
        assert StaticAnalyzer._module_to_layer("pytest") is None
        assert StaticAnalyzer._module_to_layer("typing") is None


class TestActualLayerCompliance:
    """Verify actual source files comply with layer rules"""
    
    def test_kernel_files_exist(self):
        """Kernel layer files exist"""
        project_root = Path(__file__).parent.parent
        kernel_path = project_root / "kernel"
        
        assert (kernel_path / "__init__.py").exists()
        assert (kernel_path / "substrate.py").exists()
        assert (kernel_path / "manifold.py").exists()
        assert (kernel_path / "lens.py").exists()
        assert (kernel_path / "delta.py").exists()
        assert (kernel_path / "dimensional.py").exists()
        assert (kernel_path / "srl.py").exists()
    
    def test_core_files_exist(self):
        """Core layer files exist"""
        project_root = Path(__file__).parent.parent
        core_path = project_root / "core"
        
        assert (core_path / "__init__.py").exists()
        assert (core_path / "gateway.py").exists()
        assert (core_path / "invocation.py").exists()
        assert (core_path / "translator.py").exists()
        assert (core_path / "validator.py").exists()
    
    def test_interface_files_exist(self):
        """Interface layer files exist"""
        project_root = Path(__file__).parent.parent
        interface_path = project_root / "interface"
        
        assert (interface_path / "__init__.py").exists()
        assert (interface_path / "dto.py").exists()
        assert (interface_path / "human.py").exists()
        assert (interface_path / "machine.py").exists()
        assert (interface_path / "ai.py").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
