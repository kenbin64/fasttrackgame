"""
Universal Connector - Connect to Anything Dimensionally

A dimensional API aggregator that connects to 40+ free APIs
and organizes them by dimensional levels.

Key Features:
    - 40+ free APIs (no keys required)
    - Lazy connection - APIs exist as potential until invoked
    - Level-based organization:
        Level 6: All connectors (the "Whole")
        Level 5: API categories (Finance, Weather, Fun, etc.)
        Level 4: Individual APIs
        Level 3: Endpoints
        Level 2: Response fields
        Level 1: Values
    - O(7) navigation vs O(N) iteration

Usage:
    from apps.universal_connector import UniversalConnector
    
    connector = UniversalConnector()
    
    # See all categories
    categories = connector.invoke(5)
    
    # Get specific category
    finance_apis = connector.invoke_category("finance")
    
    # Connect to an API (lazy - materializes on demand)
    data = connector.connect("bitcoin")
    
    # Query across all connected sources
    results = connector.query("price").execute()
"""

import json
import urllib.request
import urllib.error
import ssl
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Set
from pathlib import Path
import sys

# Add parent to path for helix imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from helix import (
    HelixKernel, ManifoldSubstrate, Token,
    HelixCache, HelixLogger, LEVEL_NAMES, LEVEL_ICONS
)


# =============================================================================
# API REGISTRY - Free APIs (No Key Required)
# =============================================================================

API_REGISTRY = {
    # -------------------------------------------------------------------------
    # FINANCE (Level 5, Category 0)
    # -------------------------------------------------------------------------
    "finance": {
        "level": 5,
        "icon": "💰",
        "apis": {
            "bitcoin": {
                "url": "https://api.coindesk.com/v1/bpi/currentprice.json",
                "description": "Bitcoin price index",
                "fields": ["bpi.USD.rate", "bpi.EUR.rate", "bpi.GBP.rate"]
            },
            "coinbase": {
                "url": "https://api.coinbase.com/v2/prices/BTC-USD/spot",
                "description": "Coinbase BTC spot price",
                "fields": ["data.amount", "data.currency"]
            },
            "coingecko": {
                "url": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd",
                "description": "Multiple crypto prices",
                "fields": ["bitcoin.usd", "ethereum.usd"]
            },
            "exchangerate": {
                "url": "https://open.er-api.com/v6/latest/USD",
                "description": "Exchange rates (USD base)",
                "fields": ["rates.EUR", "rates.GBP", "rates.JPY"]
            },
        }
    },
    
    # -------------------------------------------------------------------------
    # WEATHER (Level 5, Category 1)
    # -------------------------------------------------------------------------
    "weather": {
        "level": 5,
        "icon": "🌤️",
        "apis": {
            "wttr": {
                "url": "https://wttr.in/?format=j1",
                "description": "Weather for current location",
                "fields": ["current_condition.temp_F", "current_condition.weatherDesc"]
            },
            "wttr_nyc": {
                "url": "https://wttr.in/NewYork?format=j1",
                "description": "Weather for New York",
                "fields": ["current_condition.temp_F", "current_condition.humidity"]
            },
            "wttr_london": {
                "url": "https://wttr.in/London?format=j1",
                "description": "Weather for London",
                "fields": ["current_condition.temp_C", "current_condition.weatherDesc"]
            },
            "wttr_tokyo": {
                "url": "https://wttr.in/Tokyo?format=j1",
                "description": "Weather for Tokyo",
                "fields": ["current_condition.temp_C", "current_condition.humidity"]
            },
        }
    },
    
    # -------------------------------------------------------------------------
    # FUN & RANDOM (Level 5, Category 2)
    # -------------------------------------------------------------------------
    "fun": {
        "level": 5,
        "icon": "🎲",
        "apis": {
            "joke": {
                "url": "https://official-joke-api.appspot.com/random_joke",
                "description": "Random joke",
                "fields": ["setup", "punchline"]
            },
            "dad_joke": {
                "url": "https://icanhazdadjoke.com/",
                "description": "Random dad joke",
                "headers": {"Accept": "application/json"},
                "fields": ["joke"]
            },
            "cat_fact": {
                "url": "https://catfact.ninja/fact",
                "description": "Random cat fact",
                "fields": ["fact"]
            },
            "dog_fact": {
                "url": "https://dogapi.dog/api/v2/facts",
                "description": "Random dog fact",
                "fields": ["data.attributes.body"]
            },
            "useless_fact": {
                "url": "https://uselessfacts.jsph.pl/api/v2/facts/random",
                "description": "Random useless fact",
                "fields": ["text"]
            },
            "advice": {
                "url": "https://api.adviceslip.com/advice",
                "description": "Random advice",
                "fields": ["slip.advice"]
            },
            "quote": {
                "url": "https://api.quotable.io/random",
                "description": "Random quote",
                "fields": ["content", "author"]
            },
            "affirmation": {
                "url": "https://www.affirmations.dev/",
                "description": "Random affirmation",
                "fields": ["affirmation"]
            },
            "bored": {
                "url": "https://www.boredapi.com/api/activity",
                "description": "Activity suggestion",
                "fields": ["activity", "type"]
            },
        }
    },
    
    # -------------------------------------------------------------------------
    # IMAGES (Level 5, Category 3)
    # -------------------------------------------------------------------------
    "images": {
        "level": 5,
        "icon": "🖼️",
        "apis": {
            "random_dog": {
                "url": "https://dog.ceo/api/breeds/image/random",
                "description": "Random dog image",
                "fields": ["message"]
            },
            "random_cat": {
                "url": "https://api.thecatapi.com/v1/images/search",
                "description": "Random cat image",
                "fields": ["[0].url"]
            },
            "random_fox": {
                "url": "https://randomfox.ca/floof/",
                "description": "Random fox image",
                "fields": ["image"]
            },
            "random_duck": {
                "url": "https://random-d.uk/api/v2/random",
                "description": "Random duck image",
                "fields": ["url"]
            },
            "placeholder": {
                "url": "https://jsonplaceholder.typicode.com/photos/1",
                "description": "Placeholder image data",
                "fields": ["url", "thumbnailUrl"]
            },
        }
    },
    
    # -------------------------------------------------------------------------
    # DATA & REFERENCE (Level 5, Category 4)
    # -------------------------------------------------------------------------
    "data": {
        "level": 5,
        "icon": "📊",
        "apis": {
            "countries": {
                "url": "https://restcountries.com/v3.1/all?fields=name,capital,population",
                "description": "All countries data",
                "fields": ["name.common", "capital", "population"]
            },
            "universities": {
                "url": "http://universities.hipolabs.com/search?country=united+states",
                "description": "US Universities list",
                "fields": ["name", "web_pages"]
            },
            "ip_info": {
                "url": "https://ipapi.co/json/",
                "description": "Your IP information",
                "fields": ["ip", "city", "country_name"]
            },
            "user_agent": {
                "url": "https://httpbin.org/user-agent",
                "description": "Your user agent",
                "fields": ["user-agent"]
            },
            "headers": {
                "url": "https://httpbin.org/headers",
                "description": "Your request headers",
                "fields": ["headers"]
            },
        }
    },
    
    # -------------------------------------------------------------------------
    # TIME & DATE (Level 5, Category 5)
    # -------------------------------------------------------------------------
    "time": {
        "level": 5,
        "icon": "🕐",
        "apis": {
            "worldtime_utc": {
                "url": "https://worldtimeapi.org/api/timezone/Etc/UTC",
                "description": "Current UTC time",
                "fields": ["datetime", "day_of_week"]
            },
            "worldtime_nyc": {
                "url": "https://worldtimeapi.org/api/timezone/America/New_York",
                "description": "New York time",
                "fields": ["datetime", "timezone"]
            },
            "worldtime_london": {
                "url": "https://worldtimeapi.org/api/timezone/Europe/London",
                "description": "London time",
                "fields": ["datetime", "timezone"]
            },
            "worldtime_tokyo": {
                "url": "https://worldtimeapi.org/api/timezone/Asia/Tokyo",
                "description": "Tokyo time",
                "fields": ["datetime", "timezone"]
            },
        }
    },
    
    # -------------------------------------------------------------------------
    # SPACE (Level 5, Category 6)
    # -------------------------------------------------------------------------
    "space": {
        "level": 5,
        "icon": "🚀",
        "apis": {
            "iss_location": {
                "url": "http://api.open-notify.org/iss-now.json",
                "description": "Current ISS location",
                "fields": ["iss_position.latitude", "iss_position.longitude"]
            },
            "people_in_space": {
                "url": "http://api.open-notify.org/astros.json",
                "description": "People currently in space",
                "fields": ["number", "people"]
            },
            "spacex_launches": {
                "url": "https://api.spacexdata.com/v4/launches/latest",
                "description": "Latest SpaceX launch",
                "fields": ["name", "date_utc", "success"]
            },
        }
    },
    
    # -------------------------------------------------------------------------
    # NUMBERS & MATH (Level 5, Category 7)
    # -------------------------------------------------------------------------
    "numbers": {
        "level": 5,
        "icon": "🔢",
        "apis": {
            "number_fact": {
                "url": "http://numbersapi.com/random?json",
                "description": "Random number fact",
                "fields": ["text", "number"]
            },
            "year_fact": {
                "url": "http://numbersapi.com/random/year?json",
                "description": "Random year fact",
                "fields": ["text", "number"]
            },
            "math_fact": {
                "url": "http://numbersapi.com/random/math?json",
                "description": "Random math fact",
                "fields": ["text", "number"]
            },
        }
    },
}


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class APIConnection:
    """A connection to an API endpoint"""
    name: str
    category: str
    url: str
    description: str
    level: int
    fields: List[str]
    headers: Dict[str, str] = field(default_factory=dict)
    last_response: Optional[Dict] = None
    last_fetched: Optional[str] = None
    status: str = "potential"  # potential, connected, error
    error_message: Optional[str] = None


@dataclass
class ConnectionResult:
    """Result of a connection attempt"""
    success: bool
    api_name: str
    data: Optional[Dict]
    fetched_at: str
    error: Optional[str] = None


# =============================================================================
# UNIVERSAL CONNECTOR
# =============================================================================

class UniversalConnector:
    """
    Universal Connector - Connect to Any API Dimensionally
    
    Organizes 40+ free APIs by dimensional levels.
    Uses lazy loading - APIs exist as potential until invoked.
    
    Dimensional Structure:
        Level 6: The connector (Whole)
        Level 5: Categories (Finance, Weather, Fun, etc.)
        Level 4: Individual APIs
        Level 3: Endpoints/Methods
        Level 2: Response fields
        Level 1: Values
        Level 0: Uncommitted/Potential
    """
    
    def __init__(self):
        # Core helix components
        self.kernel = HelixKernel()
        self.substrate = ManifoldSubstrate()
        self.kernel.set_substrate(self.substrate)
        
        # Cache with level-aware TTL
        self.cache = HelixCache()
        self.logger = HelixLogger(min_level=3)
        
        # Connection state
        self._connections: Dict[str, APIConnection] = {}
        self._by_category: Dict[str, Set[str]] = {}
        self._by_level: Dict[int, Set[str]] = {i: set() for i in range(7)}
        
        # Initialize from registry
        self._init_from_registry()
        
        # SSL context for HTTPS
        self._ssl_context = ssl.create_default_context()
        
        # Stats
        self._stats = {
            'total_apis': len(self._connections),
            'connected': 0,
            'invocations': 0,
            'cache_hits': 0,
            'errors': 0
        }
        
        self.logger.whole("Universal Connector initialized")
    
    def _init_from_registry(self):
        """Initialize connections from API registry"""
        for category, cat_data in API_REGISTRY.items():
            self._by_category[category] = set()
            
            for api_name, api_data in cat_data["apis"].items():
                conn = APIConnection(
                    name=api_name,
                    category=category,
                    url=api_data["url"],
                    description=api_data.get("description", ""),
                    level=4,  # Individual APIs at level 4
                    fields=api_data.get("fields", []),
                    headers=api_data.get("headers", {})
                )
                
                self._connections[api_name] = conn
                self._by_category[category].add(api_name)
                self._by_level[4].add(api_name)
                
                # Register token in substrate
                self.substrate.create_token(
                    location=(hash(api_name) % 1000, 4, 0),
                    signature={4},
                    payload=lambda c=conn: c,
                    token_id=api_name
                )
    
    # -------------------------------------------------------------------------
    # Dimensional Operations
    # -------------------------------------------------------------------------
    
    def invoke(self, level: int) -> List[Any]:
        """
        Invoke a dimensional level.
        
        Level 6: Returns summary of all categories
        Level 5: Returns all categories with stats
        Level 4: Returns all API connections
        Level 3: Returns all connected API data
        """
        self._stats['invocations'] += 1
        self.kernel.invoke(level)
        
        if level == 6:
            # Whole - connector summary
            return [{
                'name': 'Universal Connector',
                'categories': len(self._by_category),
                'total_apis': len(self._connections),
                'connected': self._stats['connected']
            }]
        
        elif level == 5:
            # Categories
            return [
                {
                    'name': cat,
                    'icon': API_REGISTRY[cat]['icon'],
                    'apis': len(apis),
                    'connected': sum(
                        1 for a in apis 
                        if self._connections[a].status == 'connected'
                    )
                }
                for cat, apis in self._by_category.items()
            ]
        
        elif level == 4:
            # All APIs
            return list(self._connections.values())
        
        elif level == 3:
            # Connected data only
            return [
                conn.last_response
                for conn in self._connections.values()
                if conn.last_response is not None
            ]
        
        else:
            return []
    
    def invoke_category(self, category: str) -> List[APIConnection]:
        """Get all APIs in a category"""
        if category not in self._by_category:
            return []
        
        return [
            self._connections[name]
            for name in self._by_category[category]
        ]
    
    def categories(self) -> List[Dict[str, Any]]:
        """Get all categories with metadata"""
        return self.invoke(5)
    
    # -------------------------------------------------------------------------
    # Connection Operations
    # -------------------------------------------------------------------------
    
    def connect(self, api_name: str, force: bool = False) -> ConnectionResult:
        """
        Connect to an API and fetch data.
        
        This is the "materialization" - API goes from potential to connected.
        
        Args:
            api_name: Name of the API to connect to
            force: Force refresh even if cached
        """
        if api_name not in self._connections:
            return ConnectionResult(
                success=False,
                api_name=api_name,
                data=None,
                fetched_at=datetime.now().isoformat(),
                error=f"Unknown API: {api_name}"
            )
        
        conn = self._connections[api_name]
        
        # Check cache first
        if not force:
            cached = self.cache.get(api_name)
            if cached:
                self._stats['cache_hits'] += 1
                return ConnectionResult(
                    success=True,
                    api_name=api_name,
                    data=cached,
                    fetched_at=conn.last_fetched or datetime.now().isoformat()
                )
        
        # Fetch from API
        try:
            self.logger.width(f"Connecting to {api_name}...")
            
            req = urllib.request.Request(conn.url)
            
            # Add headers
            req.add_header('User-Agent', 'ButterflyFX-UniversalConnector/1.0')
            for key, value in conn.headers.items():
                req.add_header(key, value)
            
            # Make request
            with urllib.request.urlopen(req, context=self._ssl_context, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            # Update connection state
            conn.last_response = data
            conn.last_fetched = datetime.now().isoformat()
            conn.status = "connected"
            conn.error_message = None
            
            # Cache it
            self.cache.set(api_name, data, conn.level)
            
            self._stats['connected'] = sum(
                1 for c in self._connections.values() 
                if c.status == 'connected'
            )
            
            self.logger.width(f"Connected to {api_name}")
            
            return ConnectionResult(
                success=True,
                api_name=api_name,
                data=data,
                fetched_at=conn.last_fetched
            )
            
        except Exception as e:
            conn.status = "error"
            conn.error_message = str(e)
            self._stats['errors'] += 1
            
            self.logger.plane(f"Error connecting to {api_name}: {e}")
            
            return ConnectionResult(
                success=False,
                api_name=api_name,
                data=None,
                fetched_at=datetime.now().isoformat(),
                error=str(e)
            )
    
    def connect_category(self, category: str) -> List[ConnectionResult]:
        """Connect to all APIs in a category"""
        if category not in self._by_category:
            return []
        
        results = []
        for api_name in self._by_category[category]:
            result = self.connect(api_name)
            results.append(result)
        
        return results
    
    def connect_all(self) -> List[ConnectionResult]:
        """Connect to ALL APIs (careful - many requests!)"""
        results = []
        for api_name in self._connections:
            result = self.connect(api_name)
            results.append(result)
        
        return results
    
    def disconnect(self, api_name: str) -> bool:
        """Disconnect an API (return to potential)"""
        if api_name not in self._connections:
            return False
        
        conn = self._connections[api_name]
        conn.last_response = None
        conn.status = "potential"
        
        # Remove from cache
        self.cache.invalidate_level(conn.level)
        
        return True
    
    def disconnect_all(self):
        """Disconnect all APIs"""
        for api_name in self._connections:
            self.disconnect(api_name)
        self._stats['connected'] = 0
    
    # -------------------------------------------------------------------------
    # Query Operations
    # -------------------------------------------------------------------------
    
    def get(self, api_name: str) -> Optional[Dict]:
        """Get cached data for an API (doesn't fetch)"""
        conn = self._connections.get(api_name)
        if conn and conn.last_response:
            return conn.last_response
        return None
    
    def get_field(self, api_name: str, field_path: str) -> Any:
        """
        Get a specific field from API response.
        
        field_path uses dot notation: "bpi.USD.rate"
        """
        data = self.get(api_name)
        if not data:
            return None
        
        parts = field_path.split('.')
        current = data
        
        for part in parts:
            if part.startswith('[') and part.endswith(']'):
                # Array index
                idx = int(part[1:-1])
                if isinstance(current, list) and len(current) > idx:
                    current = current[idx]
                else:
                    return None
            elif isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    def search(self, keyword: str) -> List[APIConnection]:
        """Search APIs by name or description"""
        keyword_lower = keyword.lower()
        return [
            conn for conn in self._connections.values()
            if keyword_lower in conn.name.lower() 
            or keyword_lower in conn.description.lower()
        ]
    
    # -------------------------------------------------------------------------
    # Info & Stats
    # -------------------------------------------------------------------------
    
    def stats(self) -> Dict[str, Any]:
        """Get connector statistics"""
        return {
            **self._stats,
            'by_category': {
                cat: {
                    'total': len(apis),
                    'connected': sum(
                        1 for a in apis 
                        if self._connections[a].status == 'connected'
                    )
                }
                for cat, apis in self._by_category.items()
            }
        }
    
    def info(self) -> str:
        """Get human-readable connector info"""
        lines = [
            "Universal Connector",
            "=" * 50,
            f"Total APIs: {self._stats['total_apis']}",
            f"Connected: {self._stats['connected']}",
            f"Cache Hits: {self._stats['cache_hits']}",
            "",
            "Categories:"
        ]
        
        for cat, apis in self._by_category.items():
            icon = API_REGISTRY[cat]['icon']
            connected = sum(
                1 for a in apis 
                if self._connections[a].status == 'connected'
            )
            lines.append(f"  {icon} {cat}: {connected}/{len(apis)} connected")
        
        return '\n'.join(lines)
    
    def list_apis(self, category: str = None) -> List[Dict[str, str]]:
        """List all available APIs"""
        connections = self._connections.values()
        
        if category:
            connections = [c for c in connections if c.category == category]
        
        return [
            {
                'name': c.name,
                'category': c.category,
                'description': c.description,
                'status': c.status
            }
            for c in connections
        ]


# =============================================================================
# DEMO
# =============================================================================

def demo():
    """Demonstrate the Universal Connector"""
    print("=" * 60)
    print("Universal Connector Demo")
    print("=" * 60)
    
    connector = UniversalConnector()
    
    # Show info
    print("\n📊 Connector Info:")
    print(connector.info())
    
    # Invoke level 5 (categories)
    print("\n🎯 INVOKE Level 5 (Categories):")
    categories = connector.invoke(5)
    for cat in categories:
        print(f"  {cat['icon']} {cat['name']}: {cat['apis']} APIs")
    
    # List APIs in a category
    print("\n📋 APIs in 'fun' category:")
    for api in connector.list_apis("fun")[:5]:
        print(f"  • {api['name']}: {api['description']}")
    
    # Connect to some APIs
    print("\n🔌 Connecting to APIs...")
    
    # Bitcoin price
    result = connector.connect("bitcoin")
    if result.success:
        rate = connector.get_field("bitcoin", "bpi.USD.rate")
        print(f"  ✓ Bitcoin: ${rate}")
    else:
        print(f"  ✗ Bitcoin: {result.error}")
    
    # Random joke
    result = connector.connect("joke")
    if result.success:
        setup = connector.get_field("joke", "setup")
        punchline = connector.get_field("joke", "punchline")
        print(f"  ✓ Joke: {setup}")
        print(f"         {punchline}")
    else:
        print(f"  ✗ Joke: {result.error}")
    
    # ISS Location
    result = connector.connect("iss_location")
    if result.success:
        lat = connector.get_field("iss_location", "iss_position.latitude")
        lon = connector.get_field("iss_location", "iss_position.longitude")
        print(f"  ✓ ISS Location: {lat}, {lon}")
    else:
        print(f"  ✗ ISS: {result.error}")
    
    # People in space
    result = connector.connect("people_in_space")
    if result.success:
        count = connector.get_field("people_in_space", "number")
        print(f"  ✓ People in Space: {count}")
    else:
        print(f"  ✗ Astronauts: {result.error}")
    
    # Stats
    print(f"\n📈 Stats: {connector.stats()['connected']} APIs connected")
    
    # Invoke level 3 (connected data)
    print("\n🎯 INVOKE Level 3 (Connected Data):")
    connected_data = connector.invoke(3)
    print(f"  {len(connected_data)} responses available")


if __name__ == "__main__":
    demo()
