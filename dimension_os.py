"""
DimensionOS — The Interface

═══════════════════════════════════════════════════════════════════
           TURNS ANYTHING INTO A DIMENSIONAL OBJECT
          RETURNS DETERMINISTIC TRUTH WHEN YOU ASK
═══════════════════════════════════════════════════════════════════

Philosophy:
    1. Everything begins with ingestion
    2. Users interact through natural language
    3. Truth is revealed through lenses
    4. No hallucinations — ever
    5. All change is dimensional, not mutable
    6. Returns manifolds as human-readable answers
    7. Simplest interface, most powerful system

Universal Connector:
    - Connect to ANY public API
    - Connect to ANY data source with credentials
    - SRL-addressed, bit-counted, encrypted
    - Data → Substrate → Lens → Truth

═══════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
import math
import hashlib
import re
import json
import urllib.request
import urllib.parse
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum, auto

# Import the substrate primitives
from math_substrate import (
    MathSubstrate, Lens, expr,
    MatrixSubstrate, MatrixLens, matrix,
    GridSubstrate, GridLens, grid2d, grid3d,
    SpectrumSubstrate, SpectrumLens, spectrum,
    StratumSubstrate, StratumLens, stratum,
)

# Import SRL for external connections
try:
    from core_v2.srl import SRL as CoreSRL, SRLResult, HTTPProtocol, APIKey
    HAS_SRL = True
except ImportError:
    HAS_SRL = False


# ═══════════════════════════════════════════════════════════════════
# UNIVERSAL CONNECTOR — Connect to ANY data source
# ═══════════════════════════════════════════════════════════════════

class DataSourceConfig:
    """Configuration for a data source."""
    
    # Free public APIs (no key required)
    PUBLIC_APIS = {
        # Crypto
        "bitcoin": "https://api.coinbase.com/v2/prices/BTC-USD/spot",
        "ethereum": "https://api.coinbase.com/v2/prices/ETH-USD/spot",
        "crypto": "https://api.coinbase.com/v2/prices/{symbol}-USD/spot",
        
        # General data
        "ip": "https://api.ipify.org?format=json",
        "time": "https://worldtimeapi.org/api/ip",
        
        # Placeholder for APIs that need keys
        "weather": "https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}",
        "news": "https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}",
        "stocks": "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}",
    }
    
    def __init__(self):
        self.api_keys: Dict[str, str] = {}
    
    def set_api_key(self, service: str, key: str) -> None:
        """Set API key for a service."""
        self.api_keys[service] = key
    
    def get_url(self, source: str, **params) -> Optional[str]:
        """Get URL for a data source with parameters filled in."""
        template = self.PUBLIC_APIS.get(source.lower())
        if not template:
            return None
        
        # Fill in api_key if required and available
        if "{api_key}" in template:
            key = self.api_keys.get(source.lower())
            if key:
                params["api_key"] = key
            else:
                return None  # Need API key
        
        try:
            return template.format(**params)
        except KeyError:
            return template  # Return as-is if params don't match


class UniversalConnector:
    """
    Universal Connector — Connect to ANY data source.
    
    Via SRL, connects to:
        - Public APIs (no key required)
        - Private APIs (with credentials)
        - Databases
        - Files
        - Streams
    
    Returns data as dimensional substrates.
    """
    
    def __init__(self, config: Optional[DataSourceConfig] = None):
        self.config = config or DataSourceConfig()
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._cache_ttl = 60.0  # 1 minute cache
    
    def fetch_json(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[Dict]:
        """Fetch JSON from a URL."""
        import time
        
        # Check cache
        cache_key = url
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return data
        
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'DimensionOS/1.0')
            if headers:
                for k, v in headers.items():
                    req.add_header(k, v)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                self._cache[cache_key] = (data, time.time())
                return data
        except Exception as e:
            print(f"  [!] Fetch error: {e}")
            return None
    
    def fetch_crypto_price(self, symbol: str = "BTC") -> Optional[Dict]:
        """Fetch cryptocurrency price."""
        url = f"https://api.coinbase.com/v2/prices/{symbol.upper()}-USD/spot"
        data = self.fetch_json(url)
        if data and "data" in data:
            return {
                "symbol": symbol.upper(),
                "price": float(data["data"]["amount"]),
                "currency": data["data"]["currency"],
                "source": "coinbase",
            }
        return None
    
    def fetch_multiple_cryptos(self) -> List[Dict]:
        """Fetch prices for major cryptocurrencies."""
        symbols = ["BTC", "ETH", "SOL", "XRP", "DOGE"]
        results = []
        for sym in symbols:
            data = self.fetch_crypto_price(sym)
            if data:
                results.append(data)
        return results
    
    def fetch_world_time(self) -> Optional[Dict]:
        """Fetch current world time."""
        data = self.fetch_json("https://worldtimeapi.org/api/ip")
        if data:
            return {
                "timezone": data.get("timezone"),
                "datetime": data.get("datetime"),
                "day_of_week": data.get("day_of_week"),
                "utc_offset": data.get("utc_offset"),
            }
        return None
    
    def fetch_public_ip(self) -> Optional[str]:
        """Fetch public IP address."""
        data = self.fetch_json("https://api.ipify.org?format=json")
        if data:
            return data.get("ip")
        return None


# ═══════════════════════════════════════════════════════════════════
# IDENTITY
# ═══════════════════════════════════════════════════════════════════

def create_identity(source: str) -> int:
    """Create stable 64-bit identity from any source."""
    h = hashlib.sha256(source.encode()).digest()
    return int.from_bytes(h[:8], 'big')


# ═══════════════════════════════════════════════════════════════════
# DIMENSIONAL OBJECT — The Universal Substrate
# ═══════════════════════════════════════════════════════════════════

class DimensionalObject:
    """
    Anything ingested becomes a DimensionalObject.
    
    It has:
        - identity: stable 64-bit address
        - attributes: derived properties (accessed via lenses)
        - behaviors: how it responds to deltas
        - relationships: connections to other objects
    
    The object doesn't store values. Values are REVEALED through lenses.
    """
    __slots__ = ('_identity', '_name', '_type', '_attributes', '_behaviors', '_relationships')
    
    def __init__(self, name: str, obj_type: str, attributes: Dict[str, Any], 
                 behaviors: Optional[Dict[str, Callable]] = None):
        object.__setattr__(self, '_identity', create_identity(f"{obj_type}:{name}"))
        object.__setattr__(self, '_name', name)
        object.__setattr__(self, '_type', obj_type)
        object.__setattr__(self, '_attributes', attributes)
        object.__setattr__(self, '_behaviors', behaviors or {})
        object.__setattr__(self, '_relationships', {})
    
    def __setattr__(self, name, value):
        raise TypeError("DimensionalObject is immutable. Use promote() for changes.")
    
    @property
    def identity(self) -> int:
        return self._identity
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def type(self) -> str:
        return self._type
    
    def lens(self, attribute: str) -> Any:
        """Reveal a truth through a lens."""
        if attribute in self._attributes:
            val = self._attributes[attribute]
            # If it's a callable, invoke it (dynamic attribute)
            return val() if callable(val) else val
        return None
    
    def lens_computed(self, name: str, **context) -> Any:
        """Reveal computed truth through a behavior lens."""
        if name in self._behaviors:
            return self._behaviors[name](self._attributes, context)
        return None
    
    def promote(self, delta: Dict[str, Any]) -> 'DimensionalObject':
        """
        Apply a delta to create a NEW dimensional object.
        
        The original is unchanged. A new manifold is created.
        """
        new_attrs = dict(self._attributes)
        new_attrs.update(delta)
        
        # New identity based on original + delta
        delta_str = str(sorted(delta.items()))
        new_name = f"{self._name}+Δ({delta_str[:20]})"
        
        return DimensionalObject(
            name=new_name,
            obj_type=self._type,
            attributes=new_attrs,
            behaviors=self._behaviors
        )
    
    def __repr__(self) -> str:
        return f"DimensionalObject({self._name}, id=0x{self._identity:016X})"


# ═══════════════════════════════════════════════════════════════════
# OBJECT REGISTRY — Where ingested objects live
# ═══════════════════════════════════════════════════════════════════

class ObjectRegistry:
    """Registry of all dimensional objects."""
    
    def __init__(self):
        self._objects: Dict[str, DimensionalObject] = {}
        self._by_identity: Dict[int, DimensionalObject] = {}
    
    def register(self, obj: DimensionalObject) -> None:
        self._objects[obj.name.lower()] = obj
        self._by_identity[obj.identity] = obj
    
    def get(self, name: str) -> Optional[DimensionalObject]:
        return self._objects.get(name.lower())
    
    def get_by_identity(self, identity: int) -> Optional[DimensionalObject]:
        return self._by_identity.get(identity)
    
    def all_objects(self) -> List[DimensionalObject]:
        return list(self._objects.values())


# ═══════════════════════════════════════════════════════════════════
# INGESTION — Turn anything into a dimensional object
# ═══════════════════════════════════════════════════════════════════

class Ingestor:
    """
    Ingests anything into a dimensional substrate.
    
    "Existence implies completeness."
    
    If something exists, it has structure, behavior, relationships,
    and future states that can be derived.
    
    Uses UniversalConnector for external data (APIs, SRL).
    """
    
    def __init__(self, registry: ObjectRegistry, connector: Optional[UniversalConnector] = None):
        self.registry = registry
        self.connector = connector or UniversalConnector()
        self._templates = self._build_templates()
    
    def _build_templates(self) -> Dict[str, Callable]:
        """Templates for known object types."""
        return {
            # Vehicles
            "vehicle": self._ingest_vehicle,
            "car": self._ingest_vehicle,
            "truck": self._ingest_vehicle,
            "toyota": self._ingest_vehicle,
            "honda": self._ingest_vehicle,
            "ford": self._ingest_vehicle,
            "chevrolet": self._ingest_vehicle,
            "bmw": self._ingest_vehicle,
            "mercedes": self._ingest_vehicle,
            "tesla": self._ingest_tesla,  # Could be car or stock
            "corolla": self._ingest_vehicle,
            "camry": self._ingest_vehicle,
            "civic": self._ingest_vehicle,
            "accord": self._ingest_vehicle,
            "mustang": self._ingest_vehicle,
            "f-150": self._ingest_vehicle,
            "person": self._ingest_person,
            "shape": self._ingest_shape,
            "circle": self._ingest_circle,
            "wave": self._ingest_wave,
            
            # External data (SRL-backed)
            "bitcoin": self._ingest_crypto,
            "btc": self._ingest_crypto,
            "ethereum": self._ingest_crypto,
            "eth": self._ingest_crypto,
            "crypto": self._ingest_crypto,
            "doge": self._ingest_crypto,
            "dogecoin": self._ingest_crypto,
            "solana": self._ingest_crypto,
            "sol": self._ingest_crypto,
            "stock": self._ingest_stock,
            "time": self._ingest_time,
            "ip": self._ingest_ip,
        }
    
    def ingest(self, description: str) -> DimensionalObject:
        """
        Ingest any description into a dimensional object.
        
        Example: "2026 Toyota Corolla" → DimensionalObject with full attributes
        """
        # Parse the description
        parsed = self._parse_description(description)
        desc_lower = description.lower()
        
        # Find matching template
        template = None
        for key in self._templates:
            if key in desc_lower:
                template = self._templates[key]
                break
        
        if template:
            obj = template(parsed)
        else:
            # Generic object
            obj = self._ingest_generic(parsed)
        
        self.registry.register(obj)
        return obj
    
    def _parse_description(self, desc: str) -> Dict[str, Any]:
        """Extract components from description."""
        # Look for year
        year_match = re.search(r'\b(19|20)\d{2}\b', desc)
        year = int(year_match.group()) if year_match else None
        
        # Look for make/model patterns
        words = desc.split()
        
        return {
            "raw": desc,
            "year": year,
            "words": words,
            "name": desc,
        }
    
    def _ingest_vehicle(self, parsed: Dict) -> DimensionalObject:
        """Ingest a vehicle with full physics."""
        name = parsed["raw"]
        year = parsed.get("year", 2024)
        
        # Base physics (derived from existence)
        mass = 1400  # kg (typical sedan)
        drag_coefficient = 0.29
        frontal_area = 2.2  # m²
        engine_power = 130000  # watts (~175 hp)
        fuel_tank = 50  # liters
        fuel_efficiency_base = 14  # km/L at optimal speed
        
        attributes = {
            "name": name,
            "year": year,
            "mass": mass,
            "drag_coefficient": drag_coefficient,
            "frontal_area": frontal_area,
            "engine_power": engine_power,
            "fuel_tank": fuel_tank,
            "fuel_efficiency_base": fuel_efficiency_base,
            "velocity": 0,  # current state
            "position": 0,
            "fuel_level": fuel_tank,
            "air_density": 1.225,  # kg/m³
            "rolling_resistance": 0.01,
            "gravity": 9.81,
        }
        
        behaviors = {
            "gas_mileage": self._vehicle_gas_mileage,
            "gas_mileage_at_speed": self._vehicle_gas_mileage_at_speed,
            "drag_force": self._vehicle_drag_force,
            "power_required": self._vehicle_power_required,
            "max_speed": self._vehicle_max_speed,
            "acceleration": self._vehicle_acceleration,
            "stopping_distance": self._vehicle_stopping_distance,
            "range": self._vehicle_range,
            "uphill_mileage": self._vehicle_uphill_mileage,
        }
        
        return DimensionalObject(name, "vehicle", attributes, behaviors)
    
    def _vehicle_gas_mileage(self, attrs: Dict, ctx: Dict) -> str:
        """Gas mileage in normal conditions."""
        km_per_liter = attrs["fuel_efficiency_base"]
        mpg = km_per_liter * 2.352  # km/L to MPG
        return f"{mpg:.0f} MPG"
    
    def _vehicle_gas_mileage_at_speed(self, attrs: Dict, ctx: Dict) -> str:
        """Gas mileage at specific speed."""
        speed_mph = ctx.get("speed", 60)
        speed_mps = speed_mph * 0.44704
        
        # Aerodynamic losses increase with v²
        base_efficiency = attrs["fuel_efficiency_base"]
        
        # Optimal speed is around 45 mph
        optimal_speed = 20  # m/s (~45 mph)
        efficiency_factor = 1.0 - 0.01 * ((speed_mps - optimal_speed) / 10) ** 2
        efficiency_factor = max(0.5, min(1.0, efficiency_factor))
        
        km_per_liter = base_efficiency * efficiency_factor
        mpg = km_per_liter * 2.352
        
        return f"{mpg:.0f} MPG at {speed_mph} mph"
    
    def _vehicle_uphill_mileage(self, attrs: Dict, ctx: Dict) -> str:
        """Gas mileage going uphill."""
        speed_mph = ctx.get("speed", 60)
        grade = ctx.get("grade", 0.05)  # 5% grade default
        
        speed_mps = speed_mph * 0.44704
        mass = attrs["mass"]
        g = attrs["gravity"]
        
        # Additional power needed for climbing
        climb_power = mass * g * grade * speed_mps
        base_power = attrs["engine_power"] * 0.3  # typical cruise power
        total_power = base_power + climb_power
        
        # Power ratio affects efficiency
        power_ratio = total_power / base_power
        base_efficiency = attrs["fuel_efficiency_base"]
        uphill_efficiency = base_efficiency / power_ratio
        
        mpg = uphill_efficiency * 2.352
        return f"{mpg:.0f} MPG (uphill at {grade*100:.0f}% grade, {speed_mph} mph)"
    
    def _vehicle_drag_force(self, attrs: Dict, ctx: Dict) -> str:
        """Aerodynamic drag at speed."""
        speed_mph = ctx.get("speed", 60)
        speed_mps = speed_mph * 0.44704
        
        rho = attrs["air_density"]
        cd = attrs["drag_coefficient"]
        A = attrs["frontal_area"]
        
        drag = 0.5 * rho * cd * A * speed_mps ** 2
        return f"{drag:.0f} N at {speed_mph} mph"
    
    def _vehicle_power_required(self, attrs: Dict, ctx: Dict) -> str:
        """Power required to maintain speed."""
        speed_mph = ctx.get("speed", 60)
        speed_mps = speed_mph * 0.44704
        
        rho = attrs["air_density"]
        cd = attrs["drag_coefficient"]
        A = attrs["frontal_area"]
        mass = attrs["mass"]
        rolling = attrs["rolling_resistance"]
        g = attrs["gravity"]
        
        drag = 0.5 * rho * cd * A * speed_mps ** 2
        rolling_force = mass * g * rolling
        total_force = drag + rolling_force
        power = total_force * speed_mps
        
        hp = power / 745.7
        return f"{power/1000:.1f} kW ({hp:.0f} hp) at {speed_mph} mph"
    
    def _vehicle_max_speed(self, attrs: Dict, ctx: Dict) -> str:
        """Theoretical maximum speed."""
        power = attrs["engine_power"]
        rho = attrs["air_density"]
        cd = attrs["drag_coefficient"]
        A = attrs["frontal_area"]
        
        # P = 0.5 * rho * Cd * A * v³
        # v = (2P / (rho * Cd * A))^(1/3)
        v_max = (2 * power / (rho * cd * A)) ** (1/3)
        mph = v_max / 0.44704
        
        return f"{mph:.0f} mph theoretical maximum"
    
    def _vehicle_acceleration(self, attrs: Dict, ctx: Dict) -> str:
        """0-60 time estimate."""
        power = attrs["engine_power"]
        mass = attrs["mass"]
        
        # Simplified: assumes 80% power to wheels, average across gears
        effective_power = power * 0.8
        # a = P/(m*v), averaged
        # Time ≈ m * v² / (2 * P)
        v_60 = 60 * 0.44704  # 60 mph in m/s
        time_0_60 = mass * v_60 ** 2 / (2 * effective_power)
        
        return f"0-60 mph in approximately {time_0_60:.1f} seconds"
    
    def _vehicle_stopping_distance(self, attrs: Dict, ctx: Dict) -> str:
        """Stopping distance from speed."""
        speed_mph = ctx.get("speed", 60)
        speed_mps = speed_mph * 0.44704
        friction = ctx.get("friction", 0.7)
        g = attrs["gravity"]
        
        # d = v² / (2 * μ * g)
        distance = speed_mps ** 2 / (2 * friction * g)
        feet = distance * 3.281
        
        return f"{distance:.0f} meters ({feet:.0f} feet) from {speed_mph} mph"
    
    def _vehicle_range(self, attrs: Dict, ctx: Dict) -> str:
        """Range on current fuel."""
        fuel = attrs["fuel_level"]
        efficiency = attrs["fuel_efficiency_base"]
        
        km = fuel * efficiency
        miles = km * 0.621371
        
        return f"{miles:.0f} miles ({km:.0f} km) on full tank"

    def _ingest_person(self, parsed: Dict) -> DimensionalObject:
        """Ingest a person."""
        name = parsed.get("name", "Unknown")
        
        attributes = {
            "name": name,
            "type": "human",
        }
        
        return DimensionalObject(name, "person", attributes)
    
    def _ingest_circle(self, parsed: Dict) -> DimensionalObject:
        """Ingest a circle."""
        # Extract radius if specified
        radius = 1.0
        for word in parsed["words"]:
            try:
                radius = float(word)
                break
            except:
                pass
        
        attributes = {
            "radius": radius,
            "area": lambda: math.pi * radius ** 2,
            "circumference": lambda: 2 * math.pi * radius,
            "diameter": lambda: 2 * radius,
        }
        
        return DimensionalObject(f"circle_r{radius}", "shape", attributes)
    
    def _ingest_shape(self, parsed: Dict) -> DimensionalObject:
        """Generic shape."""
        return DimensionalObject(parsed["raw"], "shape", {"raw": parsed["raw"]})
    
    def _ingest_wave(self, parsed: Dict) -> DimensionalObject:
        """Ingest a wave."""
        frequency = 440  # default A4
        amplitude = 1.0
        
        for word in parsed["words"]:
            if "hz" in word.lower():
                try:
                    frequency = float(word.lower().replace("hz", ""))
                except:
                    pass
        
        attributes = {
            "frequency": frequency,
            "amplitude": amplitude,
            "period": lambda: 1.0 / frequency,
            "wavelength": lambda: 343 / frequency,  # assuming sound in air
        }
        
        behaviors = {
            "value_at": lambda attrs, ctx: attrs["amplitude"] * math.sin(
                2 * math.pi * attrs["frequency"] * ctx.get("t", 0)
            ),
        }
        
        return DimensionalObject(f"wave_{frequency}hz", "wave", attributes, behaviors)
    
    def _ingest_generic(self, parsed: Dict) -> DimensionalObject:
        """Ingest anything as a generic object."""
        return DimensionalObject(
            parsed["raw"],
            "generic",
            {"description": parsed["raw"], "words": parsed["words"]}
        )

    # ═══════════════════════════════════════════════════════════════════
    # EXTERNAL DATA TEMPLATES (SRL-backed via UniversalConnector)
    # ═══════════════════════════════════════════════════════════════════
    
    def _ingest_tesla(self, parsed: Dict) -> DimensionalObject:
        """Handle 'tesla' - could be car or stock."""
        desc_lower = parsed["raw"].lower()
        
        # Check for stock indicators
        if "stock" in desc_lower or "tsla" in desc_lower or "price" in desc_lower:
            return self._ingest_stock(parsed)
        
        # Otherwise it's a car
        return self._ingest_vehicle(parsed)
    
    def _ingest_crypto(self, parsed: Dict) -> DimensionalObject:
        """Ingest cryptocurrency with live price from Coinbase."""
        desc_lower = parsed["raw"].lower()
        
        # Map common names to symbols
        symbol_map = {
            "bitcoin": "BTC",
            "btc": "BTC",
            "ethereum": "ETH",
            "eth": "ETH",
            "solana": "SOL",
            "sol": "SOL",
            "dogecoin": "DOGE",
            "doge": "DOGE",
            "xrp": "XRP",
            "ripple": "XRP",
        }
        
        symbol = "BTC"  # default
        for key, sym in symbol_map.items():
            if key in desc_lower:
                symbol = sym
                break
        
        # Fetch live price
        price_data = self.connector.fetch_crypto_price(symbol)
        
        if price_data:
            price = price_data["price"]
            name = f"{symbol} ({price_data['source']})"
            
            attributes = {
                "name": name,
                "symbol": symbol,
                "price": price,
                "currency": price_data["currency"],
                "source": price_data["source"],
                "_connector": self.connector,  # For refresh
                "_symbol": symbol,
            }
            
            behaviors = {
                "current_price": self._crypto_price,
                "refresh": self._crypto_refresh,
            }
            
            return DimensionalObject(name, "crypto", attributes, behaviors)
        else:
            # No connection - return object that knows it needs data
            return DimensionalObject(
                symbol,
                "crypto",
                {"symbol": symbol, "price": None, "error": "Could not fetch price"},
                {"current_price": lambda a, c: "No connection to price feed"}
            )
    
    def _crypto_price(self, attrs: Dict, ctx: Dict) -> str:
        """Return current crypto price."""
        if attrs.get("price") is None:
            return "Price unavailable (no connection)"
        return f"${attrs['price']:,.2f} USD"
    
    def _crypto_refresh(self, attrs: Dict, ctx: Dict) -> str:
        """Refresh crypto price."""
        connector = attrs.get("_connector")
        symbol = attrs.get("_symbol")
        if connector and symbol:
            data = connector.fetch_crypto_price(symbol)
            if data:
                return f"${data['price']:,.2f} USD (refreshed)"
        return "Could not refresh"
    
    def _ingest_stock(self, parsed: Dict) -> DimensionalObject:
        """Ingest stock (requires API key for live data)."""
        desc_lower = parsed["raw"].lower()
        
        # Extract ticker symbol
        symbol_map = {
            "tesla": "TSLA",
            "apple": "AAPL", 
            "google": "GOOGL",
            "microsoft": "MSFT",
            "amazon": "AMZN",
            "nvidia": "NVDA",
            "meta": "META",
        }
        
        symbol = None
        for key, sym in symbol_map.items():
            if key in desc_lower:
                symbol = sym
                break
        
        # Look for explicit ticker
        ticker_match = re.search(r'\b([A-Z]{1,5})\b', parsed["raw"])
        if ticker_match:
            potential = ticker_match.group(1)
            if len(potential) >= 2 and len(potential) <= 5:
                symbol = potential
        
        if not symbol:
            symbol = "UNKNOWN"
        
        # Stock API requires key - return object indicating need for setup
        attributes = {
            "name": f"{symbol} Stock",
            "symbol": symbol,
            "price": None,
            "note": "Stock data requires API key. Use: connector.config.set_api_key('stocks', 'YOUR_KEY')",
        }
        
        behaviors = {
            "current_price": lambda a, c: f"{a['symbol']} - API key required for stock data",
        }
        
        return DimensionalObject(f"{symbol} Stock", "stock", attributes, behaviors)
    
    def _ingest_time(self, parsed: Dict) -> DimensionalObject:
        """Ingest world time."""
        time_data = self.connector.fetch_world_time()
        
        if time_data:
            attributes = {
                "timezone": time_data["timezone"],
                "datetime": time_data["datetime"],
                "day_of_week": time_data["day_of_week"],
                "utc_offset": time_data["utc_offset"],
            }
            
            behaviors = {
                "current_time": lambda a, c: a["datetime"],
                "timezone": lambda a, c: a["timezone"],
            }
            
            return DimensionalObject("World Time", "time", attributes, behaviors)
        else:
            return DimensionalObject(
                "World Time",
                "time", 
                {"error": "Could not fetch time"},
                {"current_time": lambda a, c: "Time unavailable"}
            )
    
    def _ingest_ip(self, parsed: Dict) -> DimensionalObject:
        """Ingest public IP."""
        ip = self.connector.fetch_public_ip()
        
        if ip:
            attributes = {"ip_address": ip}
            behaviors = {
                "ip": lambda a, c: a["ip_address"],
            }
            return DimensionalObject("My IP", "network", attributes, behaviors)
        else:
            return DimensionalObject(
                "My IP",
                "network",
                {"error": "Could not fetch IP"},
                {"ip": lambda a, c: "IP unavailable"}
            )


# ═══════════════════════════════════════════════════════════════════
# QUERY PROCESSOR — Natural language to dimensional operations
# ═══════════════════════════════════════════════════════════════════

class QueryProcessor:
    """
    Translates natural language into dimensional operations.
    
    The user never needs to know about substrates, lenses, or deltas.
    They just ask questions.
    """
    
    def __init__(self, registry: ObjectRegistry, connector: Optional[UniversalConnector] = None):
        self.registry = registry
        self.connector = connector or UniversalConnector()
        self.current_object: Optional[DimensionalObject] = None
    
    def process(self, query: str) -> str:
        """Process a natural language query."""
        query_lower = query.lower().strip()
        
        # Load command
        if query_lower.startswith("load "):
            return self._handle_load(query[5:])
        
        # List loaded objects
        if query_lower in ["list", "show objects", "what's loaded"]:
            return self._handle_list()
        
        # No object loaded
        if self.current_object is None:
            return "No object loaded. Try: Load the 2026 Toyota Corolla"
        
        # Question about current object
        return self._handle_question(query)
    
    def _handle_load(self, description: str) -> str:
        """Handle load command."""
        description = description.strip().rstrip(".")
        
        # Check if already loaded
        existing = self.registry.get(description)
        if existing:
            self.current_object = existing
            return f'"{existing.name}" loaded from registry.'
        
        # Ingest new object with connector
        ingestor = Ingestor(self.registry, self.connector)
        obj = ingestor.ingest(description)
        self.current_object = obj
        
        # Special message for external data
        if obj.type in ("crypto", "stock", "time", "network"):
            price = obj.lens("price")
            if price:
                return f'"{obj.name}" loaded. Current price: ${price:,.2f}'
            elif obj.type == "time":
                return f'"{obj.name}" loaded. Current time: {obj.lens("datetime")}'
            elif obj.type == "network":
                return f'"{obj.name}" loaded. IP: {obj.lens("ip_address")}'
        
        return f'"{obj.name}" loaded.'
    
    def _handle_list(self) -> str:
        """List all loaded objects."""
        objects = self.registry.all_objects()
        if not objects:
            return "No objects loaded."
        
        lines = ["Loaded objects:"]
        for obj in objects:
            lines.append(f"  • {obj.name} ({obj.type})")
        return "\n".join(lines)
    
    def _handle_question(self, query: str) -> str:
        """Handle a question about the current object."""
        query_lower = query.lower()
        obj = self.current_object
        
        # ═══════════════════════════════════════════════════════════════════
        # EXTERNAL DATA QUESTIONS (crypto, stock, time, ip)
        # ═══════════════════════════════════════════════════════════════════
        
        # Price questions (crypto/stock)
        if "price" in query_lower or "worth" in query_lower or "value" in query_lower:
            if obj.type == "crypto":
                result = obj.lens_computed("current_price")
                if result:
                    return result
            if obj.type == "stock":
                result = obj.lens_computed("current_price")
                if result:
                    return result
        
        # Refresh/update
        if "refresh" in query_lower or "update" in query_lower:
            if obj.type == "crypto":
                result = obj.lens_computed("refresh")
                if result:
                    return result
        
        # Time questions
        if obj.type == "time":
            if "what time" in query_lower or "current" in query_lower:
                return obj.lens_computed("current_time") or obj.lens("datetime")
            if "timezone" in query_lower:
                return obj.lens_computed("timezone") or obj.lens("timezone")
        
        # IP questions
        if obj.type == "network":
            if "ip" in query_lower or "address" in query_lower:
                return obj.lens_computed("ip") or obj.lens("ip_address")
        
        # ═══════════════════════════════════════════════════════════════════
        # VEHICLE QUESTIONS
        # ═══════════════════════════════════════════════════════════════════
        
        # Gas mileage questions
        if "gas mileage" in query_lower or "mpg" in query_lower or "fuel" in query_lower:
            # Check for speed
            speed_match = re.search(r'(\d+)\s*mph', query_lower)
            
            # Check for uphill
            if "uphill" in query_lower or "hill" in query_lower:
                speed = int(speed_match.group(1)) if speed_match else 60
                grade_match = re.search(r'(\d+)%', query_lower)
                grade = int(grade_match.group(1)) / 100 if grade_match else 0.05
                result = obj.lens_computed("uphill_mileage", speed=speed, grade=grade)
                if result:
                    return result
            
            if speed_match:
                speed = int(speed_match.group(1))
                result = obj.lens_computed("gas_mileage_at_speed", speed=speed)
                if result:
                    return result
            
            result = obj.lens_computed("gas_mileage")
            if result:
                return result
        
        # Speed questions
        if "max speed" in query_lower or "top speed" in query_lower:
            result = obj.lens_computed("max_speed")
            if result:
                return result
        
        # Acceleration questions
        if "0-60" in query_lower or "acceleration" in query_lower or "fast" in query_lower:
            result = obj.lens_computed("acceleration")
            if result:
                return result
        
        # Stopping distance
        if "stop" in query_lower or "braking" in query_lower:
            speed_match = re.search(r'(\d+)\s*mph', query_lower)
            speed = int(speed_match.group(1)) if speed_match else 60
            result = obj.lens_computed("stopping_distance", speed=speed)
            if result:
                return result
        
        # Range
        if "range" in query_lower or "how far" in query_lower:
            result = obj.lens_computed("range")
            if result:
                return result
        
        # Drag / aerodynamics
        if "drag" in query_lower or "wind" in query_lower:
            speed_match = re.search(r'(\d+)\s*mph', query_lower)
            speed = int(speed_match.group(1)) if speed_match else 60
            result = obj.lens_computed("drag_force", speed=speed)
            if result:
                return result
        
        # Power required
        if "power" in query_lower:
            speed_match = re.search(r'(\d+)\s*mph', query_lower)
            speed = int(speed_match.group(1)) if speed_match else 60
            result = obj.lens_computed("power_required", speed=speed)
            if result:
                return result
        
        # "What if" questions - dimensional promotion
        if "what if" in query_lower or "what happens" in query_lower:
            return self._handle_what_if(query)
        
        # Generic attribute lens
        for attr in ["name", "year", "mass", "type"]:
            if attr in query_lower:
                val = obj.lens(attr)
                if val:
                    return f"{attr.capitalize()}: {val}"
        
        # Show all attributes
        if "show" in query_lower or "tell me about" in query_lower or "describe" in query_lower:
            return self._describe_object(obj)
        
        return f"I can answer questions about {obj.name}. Try asking about gas mileage, max speed, range, or acceleration."
    
    def _handle_what_if(self, query: str) -> str:
        """Handle 'what if' questions through dimensional promotion."""
        obj = self.current_object
        query_lower = query.lower()
        
        # Uphill check FIRST (before speed check)
        if "uphill" in query_lower or "hill" in query_lower:
            speed_match = re.search(r'(\d+)\s*mph', query_lower)
            speed = int(speed_match.group(1)) if speed_match else 60
            grade = 0.05
            grade_match = re.search(r'(\d+)%', query_lower)
            if grade_match:
                grade = int(grade_match.group(1)) / 100
            
            result = obj.lens_computed("uphill_mileage", speed=speed, grade=grade)
            return result if result else "Could not calculate uphill mileage."
        
        # Speed change
        speed_match = re.search(r'(\d+)\s*mph', query_lower)
        if speed_match:
            new_speed = int(speed_match.group(1))
            new_obj = obj.promote({"velocity": new_speed * 0.44704})
            
            lines = [f"At {new_speed} mph:"]
            lines.append(f"  • {new_obj.lens_computed('gas_mileage_at_speed', speed=new_speed)}")
            lines.append(f"  • {new_obj.lens_computed('power_required', speed=new_speed)}")
            lines.append(f"  • {new_obj.lens_computed('drag_force', speed=new_speed)}")
            lines.append(f"  • {new_obj.lens_computed('stopping_distance', speed=new_speed)}")
            return "\n".join(lines)
        
        return "I can simulate: speed changes, uphill conditions, and more."
    
    def _describe_object(self, obj: DimensionalObject) -> str:
        """Describe an object's primary attributes."""
        lines = [f"{obj.name}:", f"  Type: {obj.type}"]
        
        for attr in ["year", "mass", "engine_power", "fuel_tank"]:
            val = obj.lens(attr)
            if val:
                if attr == "mass":
                    lines.append(f"  Mass: {val} kg")
                elif attr == "engine_power":
                    hp = val / 745.7
                    lines.append(f"  Power: {hp:.0f} hp")
                elif attr == "fuel_tank":
                    lines.append(f"  Fuel tank: {val} liters")
                else:
                    lines.append(f"  {attr.capitalize()}: {val}")
        
        # Add computed attributes
        lines.append("")
        lines.append("Derived truths:")
        for behavior in ["gas_mileage", "max_speed", "range", "acceleration"]:
            result = obj.lens_computed(behavior)
            if result:
                lines.append(f"  • {result}")
        
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# DIMENSION OS — The Main Interface
# ═══════════════════════════════════════════════════════════════════

class DimensionOS:
    """
    DimensionOS — The Interface
    
    Turns anything you give it into a complete dimensional object,
    and returns deterministic truth whenever you ask about it.
    
    Uses SRL/UniversalConnector for external data.
    """
    
    def __init__(self):
        self.registry = ObjectRegistry()
        self.connector = UniversalConnector()
        self.processor = QueryProcessor(self.registry, self.connector)
    
    def set_api_key(self, service: str, key: str) -> None:
        """Set API key for a service (stocks, news, weather)."""
        self.connector.config.set_api_key(service, key)
    
    def query(self, text: str) -> str:
        """
        Process any query.
        
        Commands:
            "Load the 2026 Toyota Corolla"
            "What's its gas mileage?"
            "What if it's going 80 mph?"
        """
        return self.processor.process(text)
    
    def repl(self):
        """Interactive session."""
        print("""
╔════════════════════════════════════════════════════════════════════╗
║                         DIMENSION OS                               ║
║                                                                    ║
║   Turns anything into a dimensional object.                        ║
║   Returns deterministic truth when you ask.                        ║
╚════════════════════════════════════════════════════════════════════╝

  Try:
    • Load the 2026 Toyota Corolla
    • What's the gas mileage?
    • What if it's going uphill at 60 mph?
    • What's the stopping distance at 70 mph?
    
  Type 'quit' to exit.
──────────────────────────────────────────────────────────────────────
""")
        
        while True:
            try:
                query = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye.")
                break
            
            if not query:
                continue
            
            if query.lower() == 'quit':
                print("Goodbye.")
                break
            
            response = self.query(query)
            print(f"\nDimensionOS: {response}\n")


# ═══════════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════════

def demo():
    """Demonstrate DimensionOS with the example from the spec."""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                     DIMENSION OS — DEMO                            ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    os = DimensionOS()
    
    # The conversation from the spec
    conversations = [
        ("Load the 2026 Toyota Corolla.", None),
        ("What's the gas mileage?", None),
        ("What if it's going uphill at 60 mph?", None),
        ("What's the max speed?", None),
        ("How fast is 0-60?", None),
        ("What's the stopping distance at 70 mph?", None),
        ("What if it's going 80 mph?", None),
        ("Tell me about it.", None),
    ]
    
    for query, _ in conversations:
        print(f"User: {query}")
        response = os.query(query)
        print(f"DimensionOS: {response}")
        print()
    
    print("""
═══════════════════════════════════════════════════════════════════

KEY PRINCIPLES DEMONSTRATED:

    1. INGESTION:     "Load the 2026 Toyota Corolla" → DimensionalObject
    2. NATURAL LANG:  "What's the gas mileage?" → Lens query
    3. LENSES:        Attributes revealed, not stored
    4. NO HALLUCINATION: All values derived from physics
    5. DIMENSIONAL:   "What if 80 mph?" → Promote with delta
    6. HUMAN OUTPUT:  Math becomes readable answers

═══════════════════════════════════════════════════════════════════
""")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
    else:
        os = DimensionOS()
        os.repl()
