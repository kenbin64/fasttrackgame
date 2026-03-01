"""
ButterflyFX Server Substrates

Dimensional substrate architecture for server optimization.
"""

from .connection_substrate import (
    ConnectionPoint,
    DimensionalConnectionIndex,
    ConnectionSubstrate,
    ConnectionPoolManifold
)

from .request_substrate import (
    RequestPoint,
    RouteSubstrate,
    RequestSubstrate,
    RequestResponseManifold
)

__all__ = [
    'ConnectionPoint',
    'DimensionalConnectionIndex',
    'ConnectionSubstrate',
    'ConnectionPoolManifold',
    'RequestPoint',
    'RouteSubstrate',
    'RequestSubstrate',
    'RequestResponseManifold',
]
