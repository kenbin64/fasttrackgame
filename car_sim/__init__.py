"""
ButterflyFX Car Simulator
=========================

A car driving simulator built entirely on ButterflyFX substrate architecture.
No AI - pure mathematical substrate transformations.

Components:
    - CarSubstrate: Car entity with physics properties
    - RoadSubstrate: Road geometry and rendering
    - DashboardSubstrate: Instrument panel (MPH, gas, odometer)
    - PhysicsEngine: Pure math state evolution

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
"""

from .car_substrate import CarSubstrate, CarSpecs
from .physics import PhysicsEngine
from .car_api import fetch_car_specs, NHTSA_API

__all__ = [
    'CarSubstrate',
    'CarSpecs', 
    'PhysicsEngine',
    'fetch_car_specs',
    'NHTSA_API',
]
