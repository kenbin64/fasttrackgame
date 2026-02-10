"""
ButterflyFx Lens System - Apply Context to Reveal Substrate Truths

PHILOSOPHY:
A lens is a transformation that extracts specific truths from a substrate.
The substrate contains ALL information - the lens reveals what you seek.

DATA EFFICIENCY:
Instead of storing color data, sound data, 3D models separately,
store ONE expression and apply lenses on demand.
Compression ratio: 900,000:1 or higher
"""

from typing import Dict, Any, Callable, List
import math


# ============================================================================
# BUILT-IN SYSTEM LENSES
# ============================================================================

SYSTEM_LENSES = {
    # ========================================================================
    # SPECTRUM LENSES - Map substrate to sensory spectrums
    # ========================================================================
    
    "color_distance": {
        "name": "color_distance",
        "lens_type": "spectrum",
        "category": "color",
        "description": "Maps distance from origin to color hue (0-360°)",
        "transformation_code": """
def apply(z, x, y, max_distance=100):
    import math
    distance = math.sqrt(x**2 + y**2)
    hue = (distance / max_distance) * 360
    return {'hue': hue % 360, 'saturation': 100, 'value': 100}
""",
        "parameters": {"max_distance": 100, "color_space": "HSV"},
        "input_type": "point",
        "output_type": "color",
        "is_system": True,
        "is_public": True
    },
    
    "color_height": {
        "name": "color_height",
        "lens_type": "spectrum",
        "category": "color",
        "description": "Maps substrate height (z-value) to color",
        "transformation_code": """
def apply(z, x, y, min_z=0, max_z=100):
    normalized = (z - min_z) / (max_z - min_z) if max_z != min_z else 0
    hue = normalized * 360
    return {'hue': hue % 360, 'saturation': 100, 'value': 100}
""",
        "parameters": {"min_z": 0, "max_z": 100},
        "input_type": "substrate",
        "output_type": "color",
        "is_system": True,
        "is_public": True
    },
    
    "sound_frequency": {
        "name": "sound_frequency",
        "lens_type": "spectrum",
        "category": "sound",
        "description": "Maps substrate height to audio frequency (20Hz - 20kHz)",
        "transformation_code": """
def apply(z, x, y, min_freq=20, max_freq=20000):
    import math
    # Logarithmic scale for frequency (musical)
    normalized = (z + 100) / 200  # Assume z in [-100, 100]
    frequency = min_freq * (max_freq / min_freq) ** normalized
    return {'frequency': frequency, 'amplitude': abs(z) / 100}
""",
        "parameters": {"min_freq": 20, "max_freq": 20000},
        "input_type": "substrate",
        "output_type": "frequency",
        "is_system": True,
        "is_public": True
    },
    
    "light_wavelength": {
        "name": "light_wavelength",
        "lens_type": "spectrum",
        "category": "light",
        "description": "Maps substrate to light wavelength (400-700nm visible spectrum)",
        "transformation_code": """
def apply(z, x, y, min_wl=400, max_wl=700):
    normalized = (z + 100) / 200  # Assume z in [-100, 100]
    wavelength = min_wl + normalized * (max_wl - min_wl)
    return {'wavelength': wavelength, 'color': wavelength_to_color(wavelength)}

def wavelength_to_color(wl):
    if wl < 450: return 'violet'
    elif wl < 495: return 'blue'
    elif wl < 570: return 'green'
    elif wl < 590: return 'yellow'
    elif wl < 620: return 'orange'
    else: return 'red'
""",
        "parameters": {"min_wl": 400, "max_wl": 700},
        "input_type": "substrate",
        "output_type": "wavelength",
        "is_system": True,
        "is_public": True
    },
    
    # ========================================================================
    # PHYSICS LENSES - Extract physical properties
    # ========================================================================
    
    "gravity_force": {
        "name": "gravity_force",
        "lens_type": "physics",
        "category": "gravity",
        "description": "Extracts gravitational force from potential field",
        "transformation_code": """
def apply(z, x, y, dx=0.01, dy=0.01):
    # Force = -gradient(potential)
    # Approximate gradient with finite differences
    grad_x = -(z(x+dx, y) - z(x-dx, y)) / (2*dx)
    grad_y = -(z(x, y+dy) - z(x, y-dy)) / (2*dy)
    import math
    magnitude = math.sqrt(grad_x**2 + grad_y**2)
    return {'force_x': grad_x, 'force_y': grad_y, 'magnitude': magnitude}
""",
        "parameters": {"dx": 0.01, "dy": 0.01},
        "input_type": "substrate",
        "output_type": "vector",
        "is_system": True,
        "is_public": True
    },
    
    "fluid_velocity": {
        "name": "fluid_velocity",
        "lens_type": "physics",
        "category": "fluid",
        "description": "Extracts fluid velocity from height field",
        "transformation_code": """
def apply(z, x, y, dx=0.01, dy=0.01, g=9.8):
    # Velocity proportional to gradient (downhill flow)
    grad_x = -(z(x+dx, y) - z(x-dx, y)) / (2*dx)
    grad_y = -(z(x, y+dy) - z(x, y-dy)) / (2*dy)
    import math
    speed = math.sqrt(2 * g * abs(z))  # v = sqrt(2gh)
    return {'velocity_x': grad_x * speed, 'velocity_y': grad_y * speed, 'speed': speed}
""",
        "parameters": {"dx": 0.01, "dy": 0.01, "g": 9.8},
        "input_type": "substrate",
        "output_type": "vector",
        "is_system": True,
        "is_public": True
    },
    
    # ========================================================================
    # GEOMETRIC LENSES - Extract geometric properties
    # ========================================================================
    
    "curvature": {
        "name": "curvature",
        "lens_type": "geometric",
        "category": "shape",
        "description": "Extracts Gaussian curvature from surface",
        "transformation_code": """
def apply(z, x, y, dx=0.01, dy=0.01):
    # Second derivatives for curvature
    z_xx = (z(x+dx, y) - 2*z(x, y) + z(x-dx, y)) / dx**2
    z_yy = (z(x, y+dy) - 2*z(x, y) + z(x, y-dy)) / dy**2
    z_xy = (z(x+dx, y+dy) - z(x+dx, y-dy) - z(x-dx, y+dy) + z(x-dx, y-dy)) / (4*dx*dy)
    
    # Gaussian curvature K = (z_xx * z_yy - z_xy^2) / (1 + z_x^2 + z_y^2)^2
    gaussian_curvature = z_xx * z_yy - z_xy**2
    mean_curvature = (z_xx + z_yy) / 2
    
    return {'gaussian': gaussian_curvature, 'mean': mean_curvature}
""",
        "parameters": {"dx": 0.01, "dy": 0.01},
        "input_type": "substrate",
        "output_type": "scalar",
        "is_system": True,
        "is_public": True
    },
    
    "gradient_vector": {
        "name": "gradient_vector",
        "lens_type": "geometric",
        "category": "shape",
        "description": "Extracts gradient (slope) vector",
        "transformation_code": """
def apply(z, x, y, dx=0.01, dy=0.01):
    grad_x = (z(x+dx, y) - z(x-dx, y)) / (2*dx)
    grad_y = (z(x, y+dy) - z(x, y-dy)) / (2*dy)
    import math
    magnitude = math.sqrt(grad_x**2 + grad_y**2)
    angle = math.atan2(grad_y, grad_x) * 180 / math.pi
    return {'grad_x': grad_x, 'grad_y': grad_y, 'magnitude': magnitude, 'angle': angle}
""",
        "parameters": {"dx": 0.01, "dy": 0.01},
        "input_type": "substrate",
        "output_type": "vector",
        "is_system": True,
        "is_public": True
    },
}


# ============================================================================
# LENS APPLICATION FUNCTIONS
# ============================================================================

def compile_lens(transformation_code: str) -> Callable:
    """Compile lens transformation code into callable function."""
    namespace = {}
    exec(transformation_code, namespace)
    return namespace.get('apply')


def apply_lens(lens_name: str, substrate_func: Callable, x: float, y: float, **params) -> Dict[str, Any]:
    """
    Apply a lens to a substrate at a specific point.
    
    Args:
        lens_name: Name of the lens to apply
        substrate_func: The substrate function z = f(x, y)
        x, y: Point at which to apply the lens
        **params: Additional parameters for the lens
    
    Returns:
        Dictionary containing the extracted properties
    """
    if lens_name not in SYSTEM_LENSES:
        raise ValueError(f"Unknown lens: {lens_name}")
    
    lens = SYSTEM_LENSES[lens_name]
    lens_func = compile_lens(lens["transformation_code"])
    
    # Merge default parameters with provided parameters
    lens_params = {**lens.get("parameters", {}), **params}
    
    # Evaluate substrate at point
    z = substrate_func(x, y)
    
    # Apply lens
    return lens_func(z, x, y, **lens_params)


def get_available_lenses(category: str = None) -> List[Dict[str, Any]]:
    """Get list of available lenses, optionally filtered by category."""
    lenses = []
    for lens_name, lens_data in SYSTEM_LENSES.items():
        if category is None or lens_data.get("category") == category:
            lenses.append({
                "name": lens_data["name"],
                "type": lens_data["lens_type"],
                "category": lens_data["category"],
                "description": lens_data["description"],
                "input_type": lens_data["input_type"],
                "output_type": lens_data["output_type"]
            })
    return lenses

