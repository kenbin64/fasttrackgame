"""
ButterflyFX Converters - Type Conversion Utilities

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

Attribution required: Kenneth Bingham - https://butterflyfx.us

---

Converters for transforming data between ButterflyFX dimensional types
and standard Python/JSON/external formats.

Converters:
    - to_json / from_json: JSON serialization
    - to_dict / from_dict: Dictionary conversion
    - to_dataframe / from_dataframe: Pandas integration
    - to_numpy / from_numpy: NumPy array conversion
    - to_helix / from_helix: Helix state conversion
    - to_token / from_token: Token creation helpers
"""

from __future__ import annotations
from typing import Any, Dict, List, Union, Optional, Set, Callable, TypeVar, TYPE_CHECKING
from dataclasses import dataclass, asdict, is_dataclass
import json
from datetime import datetime
import math

from .kernel import HelixState, HelixKernel, LEVEL_NAMES, LEVEL_ICONS
from .substrate import Token, PayloadSource, GeometricProperty

if TYPE_CHECKING:
    from .primitives import DimensionalType

T = TypeVar('T')


# =============================================================================
# JSON CONVERTERS
# =============================================================================

class HelixJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for ButterflyFX types"""
    
    def default(self, obj):
        if isinstance(obj, HelixState):
            return {
                '__helix_state__': True,
                'spiral': obj.spiral,
                'level': obj.level,
                'level_name': obj.level_name
            }
        if isinstance(obj, Token):
            return {
                '__token__': True,
                'id': obj.id,
                'location': obj.location,
                'signature': list(obj.signature),
                'spiral_affinity': obj.spiral_affinity,
                'payload_source': obj.payload_source.name
            }
        if isinstance(obj, set):
            return {'__set__': True, 'values': list(obj)}
        if isinstance(obj, datetime):
            return {'__datetime__': True, 'iso': obj.isoformat()}
        if is_dataclass(obj) and not isinstance(obj, type):
            return {'__dataclass__': obj.__class__.__name__, **asdict(obj)}
        if callable(obj):
            return {'__callable__': True, 'name': getattr(obj, '__name__', 'lambda')}
        return super().default(obj)


def helix_json_decoder(obj: Dict) -> Any:
    """Custom JSON decoder for ButterflyFX types"""
    if '__helix_state__' in obj:
        return HelixState(obj['spiral'], obj['level'])
    if '__set__' in obj:
        return set(obj['values'])
    if '__datetime__' in obj:
        return datetime.fromisoformat(obj['iso'])
    return obj


def to_json(obj: Any, indent: int = 2) -> str:
    """Convert ButterflyFX object to JSON string"""
    return json.dumps(obj, cls=HelixJSONEncoder, indent=indent)


def from_json(s: str) -> Any:
    """Parse JSON string to ButterflyFX objects"""
    return json.loads(s, object_hook=helix_json_decoder)


# =============================================================================
# DICTIONARY CONVERTERS
# =============================================================================

def state_to_dict(state: HelixState) -> Dict[str, Any]:
    """Convert HelixState to dictionary"""
    return {
        'spiral': state.spiral,
        'level': state.level,
        'level_name': state.level_name,
        'level_icon': state.level_icon
    }


def dict_to_state(d: Dict[str, Any]) -> HelixState:
    """Convert dictionary to HelixState"""
    return HelixState(
        spiral=d.get('spiral', 0),
        level=d.get('level', 0)
    )


def token_to_dict(token: Token, materialize: bool = False) -> Dict[str, Any]:
    """Convert Token to dictionary"""
    result = {
        'id': token.id,
        'location': token.location,
        'signature': list(token.signature),
        'spiral_affinity': token.spiral_affinity,
        'payload_source': token.payload_source.name
    }
    if materialize:
        result['payload'] = token.materialize()
    return result


def dict_to_token(d: Dict[str, Any], payload: Callable = None) -> Token:
    """Convert dictionary to Token"""
    return Token(
        id=d.get('id', ''),
        location=tuple(d.get('location', (0, 0, 0))),
        signature=set(d.get('signature', {0})),
        payload=payload or (lambda: d.get('payload')),
        spiral_affinity=d.get('spiral_affinity'),
        payload_source=PayloadSource[d.get('payload_source', 'STORED')]
    )


# =============================================================================
# HELIX STATE CONVERTERS
# =============================================================================

def to_helix_coords(level: int, spiral: int = 0) -> tuple:
    """
    Convert level to helix 3D coordinates.
    
    Uses parametric helix: x = cos(t), y = sin(t), z = t/(2π)
    where t = (spiral * 7 + level) * π/7
    """
    t = (spiral * 7 + level) * math.pi / 7
    x = math.cos(t)
    y = math.sin(t)
    z = t / (2 * math.pi)
    return (x, y, z)


def from_helix_coords(x: float, y: float, z: float) -> HelixState:
    """
    Convert 3D coordinates back to helix state.
    Finds nearest valid (spiral, level) position.
    """
    t = z * 2 * math.pi
    total_level = t * 7 / math.pi
    spiral = int(total_level // 7)
    level = int(round(total_level % 7))
    level = max(0, min(6, level))  # Clamp to valid range
    return HelixState(spiral, level)


def level_to_fraction(level: int) -> float:
    """Convert level 0-6 to fractional position 0.0-1.0"""
    return level / 6.0


def fraction_to_level(fraction: float) -> int:
    """Convert fractional position 0.0-1.0 to level 0-6"""
    return int(round(fraction * 6))


# =============================================================================
# NUMPY CONVERTERS (lazy import)
# =============================================================================

def to_numpy(tokens: List[Token], property: str = 'location'):
    """
    Convert list of tokens to NumPy array.
    
    Args:
        tokens: List of Token objects
        property: Which property to extract ('location', 'signature', 'materialized')
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError("NumPy required for to_numpy(). pip install numpy")
    
    if property == 'location':
        return np.array([t.location for t in tokens])
    elif property == 'signature':
        return np.array([list(t.signature) for t in tokens], dtype=object)
    elif property == 'materialized':
        return np.array([t.materialize() for t in tokens], dtype=object)
    else:
        raise ValueError(f"Unknown property: {property}")


def from_numpy(arr, signature: Set[int] = None, spiral: int = 0):
    """
    Create tokens from NumPy array.
    Each row becomes a token with location from array values.
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError("NumPy required for from_numpy(). pip install numpy")
    
    signature = signature or {0, 1, 2, 3, 4, 5, 6}
    tokens = []
    
    for i, row in enumerate(arr):
        token = Token(
            id=f"np_{i}",
            location=tuple(row.tolist()),
            signature=signature,
            payload=lambda r=row: r.tolist(),
            spiral_affinity=spiral
        )
        tokens.append(token)
    
    return tokens


# =============================================================================
# PANDAS CONVERTERS (lazy import)
# =============================================================================

def to_dataframe(tokens: List[Token], include_payload: bool = False):
    """
    Convert list of tokens to Pandas DataFrame.
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("Pandas required for to_dataframe(). pip install pandas")
    
    data = []
    for t in tokens:
        row = {
            'id': t.id,
            'x': t.location[0] if len(t.location) > 0 else None,
            'y': t.location[1] if len(t.location) > 1 else None,
            'z': t.location[2] if len(t.location) > 2 else None,
            'min_level': min(t.signature),
            'max_level': max(t.signature),
            'spiral_affinity': t.spiral_affinity,
            'source': t.payload_source.name
        }
        if include_payload:
            row['payload'] = t.materialize()
        data.append(row)
    
    return pd.DataFrame(data)


def from_dataframe(df, id_col: str = 'id', location_cols: List[str] = None):
    """
    Create tokens from Pandas DataFrame.
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("Pandas required for from_dataframe(). pip install pandas")
    
    location_cols = location_cols or ['x', 'y', 'z']
    tokens = []
    
    for idx, row in df.iterrows():
        token_id = str(row.get(id_col, f"df_{idx}"))
        location = tuple(row.get(c, 0) for c in location_cols if c in row)
        
        token = Token(
            id=token_id,
            location=location,
            signature={0, 1, 2, 3, 4, 5, 6},
            payload=lambda r=row: r.to_dict()
        )
        tokens.append(token)
    
    return tokens


# =============================================================================
# LEVEL CONVERSIONS
# =============================================================================

def level_from_depth(depth: int, max_depth: int = 7) -> int:
    """
    Convert tree depth to helix level.
    Root (depth=0) -> level 6
    Leaves (depth=max) -> level 0
    """
    return max(0, min(6, 6 - depth))


def depth_from_level(level: int) -> int:
    """
    Convert helix level to tree depth.
    Level 6 (Whole) -> depth 0 (root)
    Level 0 (Potential) -> depth 6 (leaf)
    """
    return 6 - level


def nested_to_dimensional(data: Dict, current_level: int = 6) -> List[Dict]:
    """
    Flatten nested dictionary to dimensional records.
    
    Input: {'cars': {'tesla': {'model_s': {...}}}}
    Output: [
        {'level': 6, 'key': 'cars', 'value': ...},
        {'level': 5, 'key': 'tesla', 'value': ...},
        {'level': 4, 'key': 'model_s', 'value': ...}
    ]
    """
    results = []
    
    def _flatten(obj, level, path=''):
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}/{key}" if path else key
                results.append({
                    'level': level,
                    'key': key,
                    'path': new_path,
                    'is_leaf': not isinstance(value, dict)
                })
                if isinstance(value, dict) and level > 0:
                    _flatten(value, level - 1, new_path)
                else:
                    results[-1]['value'] = value
        else:
            results.append({
                'level': level,
                'key': path.split('/')[-1],
                'path': path,
                'value': obj,
                'is_leaf': True
            })
    
    _flatten(data, current_level)
    return results


def dimensional_to_nested(records: List[Dict]) -> Dict:
    """
    Reconstruct nested dictionary from dimensional records.
    Inverse of nested_to_dimensional.
    """
    result = {}
    
    # Sort by path length (breadth-first reconstruction)
    sorted_records = sorted(records, key=lambda r: r.get('path', '').count('/'))
    
    for record in sorted_records:
        path = record.get('path', record.get('key', ''))
        parts = path.split('/')
        
        current = result
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]
        
        if 'value' in record:
            current[parts[-1]] = record['value']
        elif parts[-1] not in current:
            current[parts[-1]] = {}
    
    return result


# =============================================================================
# QUICK CONVERTERS
# =============================================================================

def quick_token(data: Any, level: int = 3, spiral: int = 0) -> Token:
    """
    Quickly create a token from any Python data.
    
    Usage:
        token = quick_token({'name': 'Alice', 'age': 30})
        token = quick_token("hello world", level=2)
    """
    import uuid
    
    return Token(
        id=f"quick_{uuid.uuid4().hex[:8]}",
        location=(spiral, level, 0),
        signature={level},
        payload=lambda d=data: d,
        spiral_affinity=spiral
    )


def quick_tokens(items: List[Any], base_level: int = 3, spiral: int = 0) -> List[Token]:
    """Create multiple tokens from a list of items"""
    return [quick_token(item, level=base_level, spiral=spiral) for item in items]


def tokens_to_list(tokens: List[Token]) -> List[Any]:
    """Extract materialized payloads from tokens"""
    return [t.materialize() for t in tokens]


# =============================================================================
# FORMAT DETECTION
# =============================================================================

def detect_format(data: Any) -> str:
    """
    Detect the format of input data.
    Returns: 'helix_state', 'token', 'dict', 'list', 'primitive', 'unknown'
    """
    if isinstance(data, HelixState):
        return 'helix_state'
    if isinstance(data, Token):
        return 'token'
    if isinstance(data, dict):
        if '__helix_state__' in data:
            return 'helix_state_dict'
        if '__token__' in data:
            return 'token_dict'
        return 'dict'
    if isinstance(data, (list, tuple, set)):
        return 'collection'
    if isinstance(data, (int, float, str, bool, type(None))):
        return 'primitive'
    return 'unknown'
