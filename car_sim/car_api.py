"""
Car API - Fetch Vehicle Specifications from Free APIs

Uses NHTSA (National Highway Traffic Safety Administration) API
https://vpic.nhtsa.dot.gov/api/

This is a free, public API that provides vehicle specifications.
No API key required.

Dimensional Mapping:
    - Vehicle specs map to manifold coordinates
    - Engine power -> Spiral dimension (torque curve)
    - Weight -> Level dimension (mass affects dynamics)
    - Fuel capacity -> Position dimension (resource tracking)
"""

import json
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


# =============================================================================
# NHTSA API CONFIGURATION
# =============================================================================

NHTSA_API = {
    "base_url": "https://vpic.nhtsa.dot.gov/api/vehicles",
    "decode_vin": "/DecodeVinValues/{vin}?format=json",
    "decode_vin_extended": "/DecodeVinExtended/{vin}?format=json",
    "get_makes": "/GetAllMakes?format=json",
    "get_models": "/GetModelsForMake/{make}?format=json",
    "get_models_year": "/GetModelsForMakeYear/make/{make}/modelyear/{year}?format=json",
    "get_vehicle_types": "/GetVehicleTypesForMake/{make}?format=json",
}


# =============================================================================
# DIMENSIONAL VEHICLE COORDINATES
# =============================================================================

@dataclass
class DimensionalVehicleCoord:
    """
    Map vehicle specifications to dimensional manifold coordinates.
    
    The car exists at a point in the vehicle manifold where:
        - Spiral (s): Power class (0-7 based on horsepower bands)
        - Level (l): Weight class (0-6 based on curb weight)
        - Position (p): Efficiency rating (MPG normalized 0-1)
    
    This allows vehicles to be compared geometrically and
    physics calculations to leverage manifold properties.
    """
    spiral: int = 0      # Power class (0=<100hp, 7=700+hp)
    level: int = 0       # Weight class (0=<2000lb, 6=6000+lb)
    position: float = 0  # Efficiency (0=10mpg, 1=60mpg)
    
    # Raw specs for physics
    horsepower: float = 150
    torque: float = 150
    weight_lbs: float = 3000
    mpg_combined: float = 28
    fuel_capacity_gal: float = 14
    
    @classmethod
    def from_specs(cls, specs: 'VehicleSpecs') -> 'DimensionalVehicleCoord':
        """Convert vehicle specs to dimensional coordinates"""
        # Power class: 0-100hp=0, 100-200=1, 200-300=2, etc.
        spiral = min(7, int(specs.horsepower / 100))
        
        # Weight class: 2000lb increments
        level = min(6, int(specs.weight_lbs / 1000))
        
        # Efficiency: normalize 10-60 MPG to 0-1
        position = max(0, min(1, (specs.mpg_combined - 10) / 50))
        
        return cls(
            spiral=spiral,
            level=level,
            position=position,
            horsepower=specs.horsepower,
            torque=specs.torque,
            weight_lbs=specs.weight_lbs,
            mpg_combined=specs.mpg_combined,
            fuel_capacity_gal=specs.fuel_capacity_gal
        )
    
    def to_manifold_point(self) -> Dict[str, float]:
        """Convert to manifold (x, y, z) coordinates for 3D visualization"""
        import math
        # Spiral maps to angle around helix
        theta = self.spiral * (2 * math.pi / 8)
        # Level maps to height
        y = self.level * 0.5
        # Position maps to radius
        r = 1 + self.position
        
        return {
            "x": r * math.cos(theta),
            "y": y,
            "z": r * math.sin(theta),
            "spiral": self.spiral,
            "level": self.level,
            "position": self.position
        }


# =============================================================================
# VEHICLE SPECIFICATIONS
# =============================================================================

@dataclass
class VehicleSpecs:
    """Complete vehicle specifications from API"""
    
    # Identity
    make: str = "Generic"
    model: str = "Sedan"
    year: int = 2024
    vin: str = ""
    
    # Engine
    engine_type: str = "Gasoline"
    engine_displacement_l: float = 2.0
    cylinders: int = 4
    horsepower: float = 150
    torque: float = 150  # lb-ft
    
    # Dimensions
    weight_lbs: float = 3000
    wheelbase_in: float = 106
    length_in: float = 180
    width_in: float = 72
    height_in: float = 56
    
    # Fuel
    fuel_type: str = "Gasoline"
    fuel_capacity_gal: float = 14
    mpg_city: float = 25
    mpg_highway: float = 32
    mpg_combined: float = 28
    
    # Performance (derived/estimated if not provided)
    top_speed_mph: float = 120
    zero_to_sixty: float = 8.5
    
    # Drivetrain
    drive_type: str = "FWD"  # FWD, RWD, AWD
    transmission: str = "Automatic"
    gears: int = 6
    
    # Tire specs (for physics)
    tire_width_mm: int = 215
    tire_aspect_ratio: int = 55
    wheel_diameter_in: int = 17
    
    def to_dimensional(self) -> DimensionalVehicleCoord:
        """Convert to dimensional manifold coordinates"""
        return DimensionalVehicleCoord.from_specs(self)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export as dictionary"""
        return {
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "engine": {
                "type": self.engine_type,
                "displacement_l": self.engine_displacement_l,
                "cylinders": self.cylinders,
                "horsepower": self.horsepower,
                "torque": self.torque
            },
            "dimensions": {
                "weight_lbs": self.weight_lbs,
                "wheelbase_in": self.wheelbase_in,
                "length_in": self.length_in
            },
            "fuel": {
                "type": self.fuel_type,
                "capacity_gal": self.fuel_capacity_gal,
                "mpg_city": self.mpg_city,
                "mpg_highway": self.mpg_highway,
                "mpg_combined": self.mpg_combined
            },
            "performance": {
                "top_speed_mph": self.top_speed_mph,
                "zero_to_sixty": self.zero_to_sixty
            },
            "dimensional": self.to_dimensional().to_manifold_point()
        }


# =============================================================================
# API FETCHING
# =============================================================================

def fetch_car_specs(vin: str = None, make: str = None, model: str = None, 
                    year: int = None) -> VehicleSpecs:
    """
    Fetch vehicle specifications from NHTSA API.
    
    Can query by:
        - VIN (most detailed)
        - Make/Model/Year combination
    
    Returns VehicleSpecs with dimensional coordinates.
    """
    
    if vin:
        return _fetch_by_vin(vin)
    elif make:
        return _fetch_by_make_model(make, model, year)
    else:
        # Return default specs
        return VehicleSpecs()


def _fetch_by_vin(vin: str) -> VehicleSpecs:
    """Decode VIN using NHTSA API"""
    url = NHTSA_API["base_url"] + NHTSA_API["decode_vin"].format(vin=vin)
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            
        if "Results" not in data or not data["Results"]:
            print(f"No results for VIN: {vin}")
            return VehicleSpecs()
        
        result = data["Results"][0]
        
        # Parse the response
        specs = VehicleSpecs(
            make=result.get("Make", "Unknown") or "Unknown",
            model=result.get("Model", "Unknown") or "Unknown",
            year=int(result.get("ModelYear", 2024) or 2024),
            vin=vin,
            engine_type=result.get("FuelTypePrimary", "Gasoline") or "Gasoline",
            engine_displacement_l=_safe_float(result.get("DisplacementL"), 2.0),
            cylinders=_safe_int(result.get("EngineCylinders"), 4),
            horsepower=_safe_float(result.get("EngineHP"), 150),
            drive_type=result.get("DriveType", "FWD") or "FWD",
            transmission=result.get("TransmissionStyle", "Automatic") or "Automatic",
            gears=_safe_int(result.get("TransmissionSpeeds"), 6),
        )
        
        # Estimate missing values
        specs = _estimate_missing_specs(specs)
        
        return specs
        
    except urllib.error.URLError as e:
        print(f"API Error: {e}")
        return VehicleSpecs()
    except json.JSONDecodeError as e:
        print(f"JSON Error: {e}")
        return VehicleSpecs()


def _fetch_by_make_model(make: str, model: str = None, year: int = None) -> VehicleSpecs:
    """Get vehicle info by make/model - returns generic specs"""
    # NHTSA doesn't provide full specs by make/model, so we use estimates
    
    # Known makes with typical specs
    MAKE_DEFAULTS = {
        "toyota": {"hp": 180, "mpg": 32, "weight": 3200},
        "honda": {"hp": 170, "mpg": 33, "weight": 3100},
        "ford": {"hp": 200, "mpg": 28, "weight": 3500},
        "chevrolet": {"hp": 220, "mpg": 26, "weight": 3600},
        "bmw": {"hp": 250, "mpg": 28, "weight": 3800},
        "mercedes": {"hp": 260, "mpg": 27, "weight": 3900},
        "tesla": {"hp": 350, "mpg": 120, "weight": 4200},  # MPGe
        "porsche": {"hp": 380, "mpg": 22, "weight": 3500},
        "ferrari": {"hp": 600, "mpg": 16, "weight": 3400},
        "lamborghini": {"hp": 650, "mpg": 14, "weight": 3600},
    }
    
    make_lower = make.lower()
    defaults = MAKE_DEFAULTS.get(make_lower, {"hp": 180, "mpg": 28, "weight": 3200})
    
    specs = VehicleSpecs(
        make=make.title(),
        model=model.title() if model else "Sedan",
        year=year or 2024,
        horsepower=defaults["hp"],
        mpg_combined=defaults["mpg"],
        weight_lbs=defaults["weight"],
    )
    
    return _estimate_missing_specs(specs)


def _estimate_missing_specs(specs: VehicleSpecs) -> VehicleSpecs:
    """Estimate missing specs using physics relationships"""
    
    # Torque estimate: roughly equal to HP for most engines
    if specs.torque == 150:  # default
        specs.torque = specs.horsepower * 0.95
    
    # Top speed from power-to-weight ratio
    # Simplified formula: top_speed ≈ 30 * sqrt(HP / (weight/1000))
    if specs.top_speed_mph == 120:  # default
        import math
        pwr_ratio = specs.horsepower / (specs.weight_lbs / 1000)
        specs.top_speed_mph = min(200, 30 * math.sqrt(pwr_ratio))
    
    # 0-60 time estimate from power-to-weight
    if specs.zero_to_sixty == 8.5:  # default
        pwr_ratio = specs.horsepower / (specs.weight_lbs / 2000)
        specs.zero_to_sixty = max(3, 15 - pwr_ratio * 0.8)
    
    # MPG estimates
    if specs.mpg_city == 25 and specs.mpg_combined != 28:
        specs.mpg_city = specs.mpg_combined * 0.85
        specs.mpg_highway = specs.mpg_combined * 1.15
    
    # Fuel capacity from MPG (target ~350 mile range)
    if specs.fuel_capacity_gal == 14:
        specs.fuel_capacity_gal = max(10, min(25, 350 / specs.mpg_combined))
    
    return specs


def _safe_float(value: Any, default: float) -> float:
    """Safely convert to float"""
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _safe_int(value: Any, default: int) -> int:
    """Safely convert to int"""
    if value is None or value == "":
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


# =============================================================================
# GET AVAILABLE MAKES (for UI selection)
# =============================================================================

def get_all_makes() -> List[str]:
    """Fetch all available makes from NHTSA"""
    url = NHTSA_API["base_url"] + NHTSA_API["get_makes"]
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        makes = [r["Make_Name"] for r in data.get("Results", [])]
        return sorted(makes)
        
    except Exception as e:
        print(f"Error fetching makes: {e}")
        return ["Toyota", "Honda", "Ford", "Chevrolet", "BMW", "Mercedes"]


def get_models_for_make(make: str, year: int = None) -> List[str]:
    """Fetch models for a given make"""
    if year:
        url = NHTSA_API["base_url"] + NHTSA_API["get_models_year"].format(make=make, year=year)
    else:
        url = NHTSA_API["base_url"] + NHTSA_API["get_models"].format(make=make)
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        models = [r["Model_Name"] for r in data.get("Results", [])]
        return sorted(set(models))
        
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    # Test with a sample VIN (2020 Toyota Camry)
    print("Testing NHTSA API...")
    
    # Test by make
    specs = fetch_car_specs(make="Toyota", model="Camry", year=2024)
    print(f"\nToyota Camry 2024:")
    print(f"  Engine: {specs.cylinders}cyl {specs.engine_displacement_l}L")
    print(f"  Power: {specs.horsepower}hp / {specs.torque}lb-ft")
    print(f"  Weight: {specs.weight_lbs}lbs")
    print(f"  MPG: {specs.mpg_city}/{specs.mpg_highway} (combined: {specs.mpg_combined})")
    print(f"  0-60: {specs.zero_to_sixty:.1f}s")
    print(f"  Top Speed: {specs.top_speed_mph:.0f}mph")
    
    # Dimensional coordinates
    dim = specs.to_dimensional()
    print(f"\nDimensional Coordinates:")
    print(f"  Spiral (power): {dim.spiral}")
    print(f"  Level (weight): {dim.level}")
    print(f"  Position (efficiency): {dim.position:.3f}")
    
    manifold = dim.to_manifold_point()
    print(f"\nManifold Point:")
    print(f"  x={manifold['x']:.3f}, y={manifold['y']:.3f}, z={manifold['z']:.3f}")
