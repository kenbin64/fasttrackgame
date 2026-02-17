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
# SERVICE REGISTRY - All Connectable Services with Prefab Configs
# =============================================================================

class AuthType:
    """Authentication types for services"""
    NONE = "none"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC = "basic"
    TOKEN = "token"
    CONNECTION_STRING = "connection_string"
    IMAP = "imap"
    CUSTOM = "custom"


# Each service has:
# - id: unique identifier
# - name: display name
# - icon: emoji or logo identifier
# - logo_url: URL to service logo
# - color: brand color
# - category: service category
# - auth_type: type of authentication needed
# - auth_url: URL to get API keys/credentials
# - wizard_fields: fields to collect in connection wizard
# - srl_template: template for generating SRLs
# - endpoints: available endpoints/operations

SERVICE_REGISTRY = {
    # =========================================================================
    # CLOUD STORAGE
    # =========================================================================
    "google_drive": {
        "id": "google_drive",
        "name": "Google Drive",
        "icon": "📁",
        "logo_url": "https://ssl.gstatic.com/images/branding/product/1x/drive_2020q4_48dp.png",
        "color": "#4285F4",
        "category": "cloud_storage",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://console.cloud.google.com/apis/credentials",
        "docs_url": "https://developers.google.com/drive/api/guides/about-sdk",
        "wizard_fields": [
            {"name": "client_id", "label": "Client ID", "type": "text", "required": True},
            {"name": "client_secret", "label": "Client Secret", "type": "password", "required": True},
        ],
        "srl_template": "srl://cloud.google/drive/{path}",
        "drive_letter": "G",
        "substrates": ["files", "folders", "shared", "starred"],
    },
    "dropbox": {
        "id": "dropbox",
        "name": "Dropbox",
        "icon": "📦",
        "logo_url": "https://cf.dropboxstatic.com/static/images/favicon-vfl8lS9yw.ico",
        "color": "#0061FF",
        "category": "cloud_storage",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://www.dropbox.com/developers/apps",
        "docs_url": "https://www.dropbox.com/developers/documentation",
        "wizard_fields": [
            {"name": "app_key", "label": "App Key", "type": "text", "required": True},
            {"name": "app_secret", "label": "App Secret", "type": "password", "required": True},
        ],
        "srl_template": "srl://cloud.dropbox/{path}",
        "drive_letter": "D",
        "substrates": ["files", "folders", "shared"],
    },
    "onedrive": {
        "id": "onedrive",
        "name": "OneDrive",
        "icon": "☁️",
        "logo_url": "https://www.microsoft.com/favicon.ico",
        "color": "#0078D4",
        "category": "cloud_storage",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps",
        "docs_url": "https://docs.microsoft.com/graph/onedrive-concept-overview",
        "wizard_fields": [
            {"name": "client_id", "label": "Application ID", "type": "text", "required": True},
            {"name": "client_secret", "label": "Client Secret", "type": "password", "required": True},
        ],
        "srl_template": "srl://cloud.microsoft/onedrive/{path}",
        "drive_letter": "O",
        "substrates": ["files", "folders", "shared", "recent"],
    },
    "box": {
        "id": "box",
        "name": "Box",
        "icon": "📤",
        "logo_url": "https://www.box.com/favicon.ico",
        "color": "#0061D5",
        "category": "cloud_storage",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://app.box.com/developers/console",
        "docs_url": "https://developer.box.com/guides/",
        "wizard_fields": [
            {"name": "client_id", "label": "Client ID", "type": "text", "required": True},
            {"name": "client_secret", "label": "Client Secret", "type": "password", "required": True},
        ],
        "srl_template": "srl://cloud.box/{path}",
        "drive_letter": "X",
        "substrates": ["files", "folders", "collaborations"],
    },
    "icloud": {
        "id": "icloud",
        "name": "iCloud Drive",
        "icon": "🍎",
        "logo_url": "https://www.apple.com/favicon.ico",
        "color": "#999999",
        "category": "cloud_storage",
        "auth_type": AuthType.CUSTOM,
        "auth_url": "https://appleid.apple.com/",
        "docs_url": "https://developer.apple.com/icloud/",
        "wizard_fields": [
            {"name": "apple_id", "label": "Apple ID", "type": "email", "required": True},
            {"name": "app_password", "label": "App-Specific Password", "type": "password", "required": True},
        ],
        "srl_template": "srl://cloud.apple/icloud/{path}",
        "drive_letter": "I",
        "substrates": ["files", "folders"],
    },
    
    # =========================================================================
    # EMAIL SERVICES
    # =========================================================================
    "gmail": {
        "id": "gmail",
        "name": "Gmail",
        "icon": "📧",
        "logo_url": "https://ssl.gstatic.com/ui/v1/icons/mail/rfr/gmail.ico",
        "color": "#EA4335",
        "category": "email",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://console.cloud.google.com/apis/credentials",
        "docs_url": "https://developers.google.com/gmail/api",
        "wizard_fields": [
            {"name": "client_id", "label": "Client ID", "type": "text", "required": True},
            {"name": "client_secret", "label": "Client Secret", "type": "password", "required": True},
        ],
        "srl_template": "srl://email.google/gmail/{mailbox}/{message_id}",
        "drive_letter": "M",
        "substrates": ["inbox", "sent", "drafts", "labels", "threads"],
    },
    "outlook": {
        "id": "outlook",
        "name": "Outlook",
        "icon": "📬",
        "logo_url": "https://outlook.live.com/favicon.ico",
        "color": "#0078D4",
        "category": "email",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps",
        "docs_url": "https://docs.microsoft.com/graph/outlook-mail-concept-overview",
        "wizard_fields": [
            {"name": "client_id", "label": "Application ID", "type": "text", "required": True},
            {"name": "client_secret", "label": "Client Secret", "type": "password", "required": True},
        ],
        "srl_template": "srl://email.microsoft/outlook/{folder}/{message_id}",
        "drive_letter": "L",
        "substrates": ["inbox", "sent", "drafts", "folders"],
    },
    "yahoo_mail": {
        "id": "yahoo_mail",
        "name": "Yahoo Mail",
        "icon": "📨",
        "logo_url": "https://www.yahoo.com/favicon.ico",
        "color": "#6001D2",
        "category": "email",
        "auth_type": AuthType.IMAP,
        "auth_url": "https://login.yahoo.com/account/security",
        "docs_url": "https://developer.yahoo.com/",
        "wizard_fields": [
            {"name": "email", "label": "Yahoo Email", "type": "email", "required": True},
            {"name": "app_password", "label": "App Password", "type": "password", "required": True},
        ],
        "srl_template": "srl://email.yahoo/{folder}/{message_id}",
        "drive_letter": "Y",
        "substrates": ["inbox", "sent", "drafts"],
    },
    "protonmail": {
        "id": "protonmail",
        "name": "ProtonMail",
        "icon": "🔒",
        "logo_url": "https://proton.me/favicon.ico",
        "color": "#6D4AFF",
        "category": "email",
        "auth_type": AuthType.TOKEN,
        "auth_url": "https://account.proton.me/",
        "docs_url": "https://proton.me/support/bridge",
        "wizard_fields": [
            {"name": "bridge_password", "label": "Bridge Password", "type": "password", "required": True},
        ],
        "srl_template": "srl://email.proton/{folder}/{message_id}",
        "drive_letter": "P",
        "substrates": ["inbox", "sent", "archive"],
    },
    "imap_generic": {
        "id": "imap_generic",
        "name": "IMAP Email",
        "icon": "✉️",
        "logo_url": None,
        "color": "#555555",
        "category": "email",
        "auth_type": AuthType.IMAP,
        "auth_url": None,
        "docs_url": None,
        "wizard_fields": [
            {"name": "host", "label": "IMAP Server", "type": "text", "required": True, "placeholder": "imap.example.com"},
            {"name": "port", "label": "Port", "type": "number", "required": True, "default": 993},
            {"name": "username", "label": "Username", "type": "text", "required": True},
            {"name": "password", "label": "Password", "type": "password", "required": True},
            {"name": "ssl", "label": "Use SSL", "type": "checkbox", "required": False, "default": True},
        ],
        "srl_template": "srl://email.imap/{host}/{folder}/{message_id}",
        "drive_letter": None,
        "substrates": ["inbox", "folders"],
    },
    
    # =========================================================================
    # DATABASES
    # =========================================================================
    "postgresql": {
        "id": "postgresql",
        "name": "PostgreSQL",
        "icon": "🐘",
        "logo_url": "https://www.postgresql.org/favicon.ico",
        "color": "#336791",
        "category": "database",
        "auth_type": AuthType.CONNECTION_STRING,
        "auth_url": None,
        "docs_url": "https://www.postgresql.org/docs/",
        "wizard_fields": [
            {"name": "host", "label": "Host", "type": "text", "required": True, "default": "localhost"},
            {"name": "port", "label": "Port", "type": "number", "required": True, "default": 5432},
            {"name": "database", "label": "Database", "type": "text", "required": True},
            {"name": "username", "label": "Username", "type": "text", "required": True},
            {"name": "password", "label": "Password", "type": "password", "required": True},
        ],
        "srl_template": "srl://db.postgresql/{host}/{database}/{schema}/{table}",
        "drive_letter": None,
        "substrates": ["schemas", "tables", "views", "functions"],
    },
    "mysql": {
        "id": "mysql",
        "name": "MySQL",
        "icon": "🐬",
        "logo_url": "https://www.mysql.com/favicon.ico",
        "color": "#4479A1",
        "category": "database",
        "auth_type": AuthType.CONNECTION_STRING,
        "auth_url": None,
        "docs_url": "https://dev.mysql.com/doc/",
        "wizard_fields": [
            {"name": "host", "label": "Host", "type": "text", "required": True, "default": "localhost"},
            {"name": "port", "label": "Port", "type": "number", "required": True, "default": 3306},
            {"name": "database", "label": "Database", "type": "text", "required": True},
            {"name": "username", "label": "Username", "type": "text", "required": True},
            {"name": "password", "label": "Password", "type": "password", "required": True},
        ],
        "srl_template": "srl://db.mysql/{host}/{database}/{table}",
        "drive_letter": None,
        "substrates": ["tables", "views"],
    },
    "sqlite": {
        "id": "sqlite",
        "name": "SQLite",
        "icon": "📄",
        "logo_url": "https://sqlite.org/favicon.ico",
        "color": "#003B57",
        "category": "database",
        "auth_type": AuthType.NONE,
        "auth_url": None,
        "docs_url": "https://sqlite.org/docs.html",
        "wizard_fields": [
            {"name": "path", "label": "Database File", "type": "file", "required": True, "accept": ".db,.sqlite,.sqlite3"},
        ],
        "srl_template": "srl://db.sqlite/{filename}/{table}",
        "drive_letter": None,
        "substrates": ["tables", "views"],
    },
    "mongodb": {
        "id": "mongodb",
        "name": "MongoDB",
        "icon": "🍃",
        "logo_url": "https://www.mongodb.com/favicon.ico",
        "color": "#47A248",
        "category": "database",
        "auth_type": AuthType.CONNECTION_STRING,
        "auth_url": "https://cloud.mongodb.com/",
        "docs_url": "https://www.mongodb.com/docs/",
        "wizard_fields": [
            {"name": "connection_string", "label": "Connection String", "type": "text", "required": True, "placeholder": "mongodb://localhost:27017"},
            {"name": "database", "label": "Database", "type": "text", "required": True},
        ],
        "srl_template": "srl://db.mongodb/{host}/{database}/{collection}",
        "drive_letter": None,
        "substrates": ["collections", "documents"],
    },
    "redis": {
        "id": "redis",
        "name": "Redis",
        "icon": "🔴",
        "logo_url": "https://redis.io/favicon.ico",
        "color": "#DC382D",
        "category": "database",
        "auth_type": AuthType.CONNECTION_STRING,
        "auth_url": None,
        "docs_url": "https://redis.io/docs/",
        "wizard_fields": [
            {"name": "host", "label": "Host", "type": "text", "required": True, "default": "localhost"},
            {"name": "port", "label": "Port", "type": "number", "required": True, "default": 6379},
            {"name": "password", "label": "Password", "type": "password", "required": False},
            {"name": "db", "label": "Database Number", "type": "number", "required": False, "default": 0},
        ],
        "srl_template": "srl://db.redis/{host}/{db}/{key}",
        "drive_letter": None,
        "substrates": ["keys", "hashes", "lists", "sets"],
    },
    "sqlserver": {
        "id": "sqlserver",
        "name": "SQL Server",
        "icon": "🗄️",
        "logo_url": "https://www.microsoft.com/favicon.ico",
        "color": "#CC2927",
        "category": "database",
        "auth_type": AuthType.CONNECTION_STRING,
        "auth_url": None,
        "docs_url": "https://docs.microsoft.com/sql/",
        "wizard_fields": [
            {"name": "host", "label": "Server", "type": "text", "required": True},
            {"name": "database", "label": "Database", "type": "text", "required": True},
            {"name": "username", "label": "Username", "type": "text", "required": True},
            {"name": "password", "label": "Password", "type": "password", "required": True},
            {"name": "trust_cert", "label": "Trust Server Certificate", "type": "checkbox", "default": False},
        ],
        "srl_template": "srl://db.sqlserver/{host}/{database}/{schema}/{table}",
        "drive_letter": None,
        "substrates": ["schemas", "tables", "views", "procedures"],
    },
    
    # =========================================================================
    # CODE & DEV PLATFORMS
    # =========================================================================
    "github": {
        "id": "github",
        "name": "GitHub",
        "icon": "🐙",
        "logo_url": "https://github.com/favicon.ico",
        "color": "#181717",
        "category": "development",
        "auth_type": AuthType.TOKEN,
        "auth_url": "https://github.com/settings/tokens",
        "docs_url": "https://docs.github.com/rest",
        "wizard_fields": [
            {"name": "token", "label": "Personal Access Token", "type": "password", "required": True},
        ],
        "srl_template": "srl://code.github/{owner}/{repo}/{path}",
        "drive_letter": "F",
        "substrates": ["repos", "issues", "pulls", "actions", "gists"],
    },
    "gitlab": {
        "id": "gitlab",
        "name": "GitLab",
        "icon": "🦊",
        "logo_url": "https://gitlab.com/favicon.ico",
        "color": "#FC6D26",
        "category": "development",
        "auth_type": AuthType.TOKEN,
        "auth_url": "https://gitlab.com/-/profile/personal_access_tokens",
        "docs_url": "https://docs.gitlab.com/ee/api/",
        "wizard_fields": [
            {"name": "host", "label": "GitLab URL", "type": "text", "required": True, "default": "https://gitlab.com"},
            {"name": "token", "label": "Personal Access Token", "type": "password", "required": True},
        ],
        "srl_template": "srl://code.gitlab/{host}/{project}/{path}",
        "drive_letter": None,
        "substrates": ["projects", "issues", "merge_requests", "pipelines"],
    },
    "bitbucket": {
        "id": "bitbucket",
        "name": "Bitbucket",
        "icon": "🪣",
        "logo_url": "https://bitbucket.org/favicon.ico",
        "color": "#0052CC",
        "category": "development",
        "auth_type": AuthType.TOKEN,
        "auth_url": "https://bitbucket.org/account/settings/app-passwords/",
        "docs_url": "https://developer.atlassian.com/cloud/bitbucket/",
        "wizard_fields": [
            {"name": "username", "label": "Username", "type": "text", "required": True},
            {"name": "app_password", "label": "App Password", "type": "password", "required": True},
        ],
        "srl_template": "srl://code.bitbucket/{workspace}/{repo}/{path}",
        "drive_letter": None,
        "substrates": ["repos", "issues", "pull_requests", "pipelines"],
    },
    
    # =========================================================================
    # AI & ML PLATFORMS
    # =========================================================================
    "openai": {
        "id": "openai",
        "name": "OpenAI",
        "icon": "🤖",
        "logo_url": "https://openai.com/favicon.ico",
        "color": "#412991",
        "category": "ai",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://platform.openai.com/api-keys",
        "docs_url": "https://platform.openai.com/docs/",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
            {"name": "org_id", "label": "Organization ID", "type": "text", "required": False},
        ],
        "srl_template": "srl://ai.openai/{model}/{endpoint}",
        "drive_letter": None,
        "substrates": ["chat", "completions", "embeddings", "images", "audio"],
    },
    "anthropic": {
        "id": "anthropic",
        "name": "Anthropic",
        "icon": "🧠",
        "logo_url": "https://www.anthropic.com/favicon.ico",
        "color": "#D4A27F",
        "category": "ai",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://console.anthropic.com/settings/keys",
        "docs_url": "https://docs.anthropic.com/",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://ai.anthropic/{model}/{endpoint}",
        "drive_letter": None,
        "substrates": ["messages", "completions"],
    },
    "huggingface": {
        "id": "huggingface",
        "name": "Hugging Face",
        "icon": "🤗",
        "logo_url": "https://huggingface.co/favicon.ico",
        "color": "#FFD21E",
        "category": "ai",
        "auth_type": AuthType.TOKEN,
        "auth_url": "https://huggingface.co/settings/tokens",
        "docs_url": "https://huggingface.co/docs/api-inference/",
        "wizard_fields": [
            {"name": "token", "label": "API Token", "type": "password", "required": True},
        ],
        "srl_template": "srl://ai.huggingface/{model}",
        "drive_letter": None,
        "substrates": ["models", "datasets", "spaces"],
    },
    
    # =========================================================================
    # SOCIAL MEDIA
    # =========================================================================
    "twitter": {
        "id": "twitter",
        "name": "X (Twitter)",
        "icon": "🐦",
        "logo_url": "https://twitter.com/favicon.ico",
        "color": "#1DA1F2",
        "category": "social",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://developer.twitter.com/en/portal/dashboard",
        "docs_url": "https://developer.twitter.com/en/docs",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "text", "required": True},
            {"name": "api_secret", "label": "API Secret", "type": "password", "required": True},
            {"name": "bearer_token", "label": "Bearer Token", "type": "password", "required": True},
        ],
        "srl_template": "srl://social.twitter/{user}/{tweet_id}",
        "drive_letter": None,
        "substrates": ["timeline", "tweets", "followers", "lists"],
    },
    "linkedin": {
        "id": "linkedin",
        "name": "LinkedIn",
        "icon": "💼",
        "logo_url": "https://www.linkedin.com/favicon.ico",
        "color": "#0A66C2",
        "category": "social",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://www.linkedin.com/developers/apps",
        "docs_url": "https://docs.microsoft.com/linkedin/",
        "wizard_fields": [
            {"name": "client_id", "label": "Client ID", "type": "text", "required": True},
            {"name": "client_secret", "label": "Client Secret", "type": "password", "required": True},
        ],
        "srl_template": "srl://social.linkedin/{profile}/{post_id}",
        "drive_letter": None,
        "substrates": ["profile", "posts", "connections", "messages"],
    },
    "reddit": {
        "id": "reddit",
        "name": "Reddit",
        "icon": "👽",
        "logo_url": "https://www.reddit.com/favicon.ico",
        "color": "#FF4500",
        "category": "social",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://www.reddit.com/prefs/apps",
        "docs_url": "https://www.reddit.com/dev/api/",
        "wizard_fields": [
            {"name": "client_id", "label": "Client ID", "type": "text", "required": True},
            {"name": "client_secret", "label": "Client Secret", "type": "password", "required": True},
            {"name": "username", "label": "Username", "type": "text", "required": True},
            {"name": "password", "label": "Password", "type": "password", "required": True},
        ],
        "srl_template": "srl://social.reddit/{subreddit}/{post_id}",
        "drive_letter": None,
        "substrates": ["subreddits", "posts", "comments", "saved"],
    },
    "discord": {
        "id": "discord",
        "name": "Discord",
        "icon": "💬",
        "logo_url": "https://discord.com/favicon.ico",
        "color": "#5865F2",
        "category": "social",
        "auth_type": AuthType.TOKEN,
        "auth_url": "https://discord.com/developers/applications",
        "docs_url": "https://discord.com/developers/docs/",
        "wizard_fields": [
            {"name": "bot_token", "label": "Bot Token", "type": "password", "required": True},
        ],
        "srl_template": "srl://social.discord/{guild}/{channel}/{message_id}",
        "drive_letter": None,
        "substrates": ["guilds", "channels", "messages"],
    },
    
    # =========================================================================
    # MUSIC & MEDIA
    # =========================================================================
    "spotify": {
        "id": "spotify",
        "name": "Spotify",
        "icon": "🎵",
        "logo_url": "https://www.spotify.com/favicon.ico",
        "color": "#1DB954",
        "category": "music",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://developer.spotify.com/dashboard",
        "docs_url": "https://developer.spotify.com/documentation/web-api/",
        "wizard_fields": [
            {"name": "client_id", "label": "Client ID", "type": "text", "required": True},
            {"name": "client_secret", "label": "Client Secret", "type": "password", "required": True},
        ],
        "srl_template": "srl://music.spotify/{type}/{id}",
        "drive_letter": None,
        "substrates": ["playlists", "albums", "artists", "tracks", "podcasts"],
    },
    "youtube": {
        "id": "youtube",
        "name": "YouTube",
        "icon": "▶️",
        "logo_url": "https://www.youtube.com/favicon.ico",
        "color": "#FF0000",
        "category": "music",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://console.cloud.google.com/apis/credentials",
        "docs_url": "https://developers.google.com/youtube/v3",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://media.youtube/{type}/{id}",
        "drive_letter": None,
        "substrates": ["channels", "playlists", "videos", "subscriptions"],
    },
    "soundcloud": {
        "id": "soundcloud",
        "name": "SoundCloud",
        "icon": "🔊",
        "logo_url": "https://soundcloud.com/favicon.ico",
        "color": "#FF5500",
        "category": "music",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://soundcloud.com/you/apps",
        "docs_url": "https://developers.soundcloud.com/docs/api/guide",
        "wizard_fields": [
            {"name": "client_id", "label": "Client ID", "type": "text", "required": True},
            {"name": "client_secret", "label": "Client Secret", "type": "password", "required": True},
        ],
        "srl_template": "srl://music.soundcloud/{user}/{track}",
        "drive_letter": None,
        "substrates": ["tracks", "playlists", "users", "likes"],
    },
    
    # =========================================================================
    # FEEDS & NEWS
    # =========================================================================
    "rss": {
        "id": "rss",
        "name": "RSS Feed",
        "icon": "📰",
        "logo_url": None,
        "color": "#FFA500",
        "category": "feeds",
        "auth_type": AuthType.NONE,
        "auth_url": None,
        "docs_url": None,
        "wizard_fields": [
            {"name": "url", "label": "Feed URL", "type": "url", "required": True, "placeholder": "https://example.com/feed.xml"},
            {"name": "name", "label": "Feed Name", "type": "text", "required": True},
        ],
        "srl_template": "srl://feed.rss/{name}/{item_id}",
        "drive_letter": None,
        "substrates": ["items"],
    },
    "newsapi": {
        "id": "newsapi",
        "name": "News API",
        "icon": "📻",
        "logo_url": "https://newsapi.org/favicon.ico",
        "color": "#0080FF",
        "category": "feeds",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://newsapi.org/register",
        "docs_url": "https://newsapi.org/docs",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://feed.newsapi/{source}/{article_id}",
        "drive_letter": None,
        "substrates": ["headlines", "everything", "sources"],
    },
    "podcast": {
        "id": "podcast",
        "name": "Podcast Feed",
        "icon": "🎙️",
        "logo_url": None,
        "color": "#8940FA",
        "category": "feeds",
        "auth_type": AuthType.NONE,
        "auth_url": None,
        "docs_url": None,
        "wizard_fields": [
            {"name": "url", "label": "Podcast RSS URL", "type": "url", "required": True},
            {"name": "name", "label": "Podcast Name", "type": "text", "required": True},
        ],
        "srl_template": "srl://feed.podcast/{name}/{episode_id}",
        "drive_letter": None,
        "substrates": ["episodes"],
    },
    
    # =========================================================================
    # E-COMMERCE & SHOPPING
    # =========================================================================
    "stripe": {
        "id": "stripe",
        "name": "Stripe",
        "icon": "💳",
        "logo_url": "https://stripe.com/favicon.ico",
        "color": "#635BFF",
        "category": "shopping",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://dashboard.stripe.com/apikeys",
        "docs_url": "https://stripe.com/docs/api",
        "wizard_fields": [
            {"name": "secret_key", "label": "Secret Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://commerce.stripe/{type}/{id}",
        "drive_letter": None,
        "substrates": ["customers", "payments", "subscriptions", "invoices"],
    },
    "shopify": {
        "id": "shopify",
        "name": "Shopify",
        "icon": "🛒",
        "logo_url": "https://www.shopify.com/favicon.ico",
        "color": "#96BF48",
        "category": "shopping",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://partners.shopify.com/",
        "docs_url": "https://shopify.dev/docs/api",
        "wizard_fields": [
            {"name": "shop_url", "label": "Shop URL", "type": "text", "required": True, "placeholder": "mystore.myshopify.com"},
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
            {"name": "password", "label": "Admin API Password", "type": "password", "required": True},
        ],
        "srl_template": "srl://commerce.shopify/{shop}/{type}/{id}",
        "drive_letter": None,
        "substrates": ["products", "orders", "customers", "collections"],
    },
    "amazon_pa": {
        "id": "amazon_pa",
        "name": "Amazon Product API",
        "icon": "📦",
        "logo_url": "https://www.amazon.com/favicon.ico",
        "color": "#FF9900",
        "category": "shopping",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://affiliate-program.amazon.com/",
        "docs_url": "https://webservices.amazon.com/paapi5/documentation/",
        "wizard_fields": [
            {"name": "access_key", "label": "Access Key", "type": "text", "required": True},
            {"name": "secret_key", "label": "Secret Key", "type": "password", "required": True},
            {"name": "partner_tag", "label": "Partner Tag", "type": "text", "required": True},
        ],
        "srl_template": "srl://commerce.amazon/{category}/{product_id}",
        "drive_letter": None,
        "substrates": ["products", "categories", "reviews"],
    },
    
    # =========================================================================
    # PRODUCTIVITY
    # =========================================================================
    "notion": {
        "id": "notion",
        "name": "Notion",
        "icon": "📝",
        "logo_url": "https://www.notion.so/favicon.ico",
        "color": "#000000",
        "category": "productivity",
        "auth_type": AuthType.TOKEN,
        "auth_url": "https://www.notion.so/my-integrations",
        "docs_url": "https://developers.notion.com/",
        "wizard_fields": [
            {"name": "token", "label": "Integration Token", "type": "password", "required": True},
        ],
        "srl_template": "srl://app.notion/{workspace}/{page_id}",
        "drive_letter": "N",
        "substrates": ["pages", "databases", "blocks"],
    },
    "airtable": {
        "id": "airtable",
        "name": "Airtable",
        "icon": "📊",
        "logo_url": "https://airtable.com/favicon.ico",
        "color": "#18BFFF",
        "category": "productivity",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://airtable.com/create/tokens",
        "docs_url": "https://airtable.com/developers/web/api/introduction",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://app.airtable/{base}/{table}/{record_id}",
        "drive_letter": None,
        "substrates": ["bases", "tables", "records"],
    },
    "trello": {
        "id": "trello",
        "name": "Trello",
        "icon": "📋",
        "logo_url": "https://trello.com/favicon.ico",
        "color": "#0052CC",
        "category": "productivity",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://trello.com/power-ups/admin",
        "docs_url": "https://developer.atlassian.com/cloud/trello/",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "text", "required": True},
            {"name": "token", "label": "Token", "type": "password", "required": True},
        ],
        "srl_template": "srl://app.trello/{board}/{list}/{card_id}",
        "drive_letter": None,
        "substrates": ["boards", "lists", "cards"],
    },
    "slack": {
        "id": "slack",
        "name": "Slack",
        "icon": "💬",
        "logo_url": "https://slack.com/favicon.ico",
        "color": "#4A154B",
        "category": "productivity",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://api.slack.com/apps",
        "docs_url": "https://api.slack.com/docs",
        "wizard_fields": [
            {"name": "bot_token", "label": "Bot Token", "type": "password", "required": True},
        ],
        "srl_template": "srl://app.slack/{workspace}/{channel}/{message_ts}",
        "drive_letter": None,
        "substrates": ["channels", "messages", "users", "files"],
    },
    "calendar": {
        "id": "calendar",
        "name": "Google Calendar",
        "icon": "📅",
        "logo_url": "https://calendar.google.com/googlecalendar/images/favicons_2020q4/calendar_31.ico",
        "color": "#4285F4",
        "category": "productivity",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://console.cloud.google.com/apis/credentials",
        "docs_url": "https://developers.google.com/calendar/api/guides/overview",
        "wizard_fields": [
            {"name": "client_id", "label": "Client ID", "type": "text", "required": True},
            {"name": "client_secret", "label": "Client Secret", "type": "password", "required": True},
        ],
        "srl_template": "srl://app.google/calendar/{calendar_id}/{event_id}",
        "drive_letter": None,
        "substrates": ["calendars", "events"],
    },
    
    # =========================================================================
    # LOCAL RESOURCES
    # =========================================================================
    "local_files": {
        "id": "local_files",
        "name": "Local Files",
        "icon": "💾",
        "logo_url": None,
        "color": "#555555",
        "category": "local",
        "auth_type": AuthType.NONE,
        "auth_url": None,
        "docs_url": None,
        "wizard_fields": [
            {"name": "root_path", "label": "Root Path", "type": "folder", "required": True},
            {"name": "name", "label": "Display Name", "type": "text", "required": True},
        ],
        "srl_template": "srl://local/{name}/{path}",
        "drive_letter": "A",
        "substrates": ["files", "folders"],
    },
    "network_share": {
        "id": "network_share",
        "name": "Network Share",
        "icon": "🌐",
        "logo_url": None,
        "color": "#666666",
        "category": "local",
        "auth_type": AuthType.BASIC,
        "auth_url": None,
        "docs_url": None,
        "wizard_fields": [
            {"name": "path", "label": "Network Path", "type": "text", "required": True, "placeholder": "\\\\server\\share"},
            {"name": "username", "label": "Username", "type": "text", "required": False},
            {"name": "password", "label": "Password", "type": "password", "required": False},
            {"name": "name", "label": "Display Name", "type": "text", "required": True},
        ],
        "srl_template": "srl://network/{name}/{path}",
        "drive_letter": None,
        "substrates": ["files", "folders"],
    },
    
    # =========================================================================
    # WEB & APIs
    # =========================================================================
    "rest_api": {
        "id": "rest_api",
        "name": "REST API",
        "icon": "🔗",
        "logo_url": None,
        "color": "#00A86B",
        "category": "api",
        "auth_type": AuthType.CUSTOM,
        "auth_url": None,
        "docs_url": None,
        "wizard_fields": [
            {"name": "base_url", "label": "Base URL", "type": "url", "required": True},
            {"name": "name", "label": "API Name", "type": "text", "required": True},
            {"name": "auth_type", "label": "Auth Type", "type": "select", "required": True, "options": ["None", "API Key", "Bearer Token", "Basic Auth"]},
            {"name": "auth_value", "label": "Auth Value", "type": "password", "required": False},
            {"name": "auth_header", "label": "Auth Header", "type": "text", "required": False, "default": "Authorization"},
        ],
        "srl_template": "srl://api.rest/{name}/{endpoint}",
        "drive_letter": None,
        "substrates": ["endpoints"],
    },
    "graphql": {
        "id": "graphql",
        "name": "GraphQL API",
        "icon": "⬡",
        "logo_url": "https://graphql.org/favicon.ico",
        "color": "#E10098",
        "category": "api",
        "auth_type": AuthType.CUSTOM,
        "auth_url": None,
        "docs_url": "https://graphql.org/learn/",
        "wizard_fields": [
            {"name": "endpoint", "label": "GraphQL Endpoint", "type": "url", "required": True},
            {"name": "name", "label": "API Name", "type": "text", "required": True},
            {"name": "auth_header", "label": "Auth Header", "type": "text", "required": False},
            {"name": "auth_value", "label": "Auth Value", "type": "password", "required": False},
        ],
        "srl_template": "srl://api.graphql/{name}/{query}",
        "drive_letter": None,
        "substrates": ["queries", "mutations"],
    },
    "webhook": {
        "id": "webhook",
        "name": "Webhook",
        "icon": "🪝",
        "logo_url": None,
        "color": "#FF6B6B",
        "category": "api",
        "auth_type": AuthType.CUSTOM,
        "auth_url": None,
        "docs_url": None,
        "wizard_fields": [
            {"name": "url", "label": "Webhook URL", "type": "url", "required": True},
            {"name": "name", "label": "Webhook Name", "type": "text", "required": True},
            {"name": "method", "label": "Method", "type": "select", "required": True, "options": ["POST", "GET", "PUT"]},
            {"name": "secret", "label": "Secret Key", "type": "password", "required": False},
        ],
        "srl_template": "srl://hook/{name}",
        "drive_letter": None,
        "substrates": ["events"],
    },
    
    # =========================================================================
    # ADDITIONAL SOCIAL MEDIA
    # =========================================================================
    "facebook": {
        "id": "facebook",
        "name": "Facebook",
        "icon": "📘",
        "logo_url": "https://www.facebook.com/favicon.ico",
        "color": "#1877F2",
        "category": "social",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://developers.facebook.com/apps/",
        "docs_url": "https://developers.facebook.com/docs/graph-api/",
        "wizard_fields": [
            {"name": "app_id", "label": "App ID", "type": "text", "required": True},
            {"name": "app_secret", "label": "App Secret", "type": "password", "required": True},
            {"name": "access_token", "label": "Access Token", "type": "password", "required": True},
        ],
        "srl_template": "srl://social.facebook/{user}/{post_id}",
        "drive_letter": None,
        "substrates": ["posts", "photos", "pages", "groups", "events"],
    },
    "instagram": {
        "id": "instagram",
        "name": "Instagram",
        "icon": "📷",
        "logo_url": "https://www.instagram.com/favicon.ico",
        "color": "#E4405F",
        "category": "social",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://developers.facebook.com/apps/",
        "docs_url": "https://developers.facebook.com/docs/instagram-api/",
        "wizard_fields": [
            {"name": "app_id", "label": "App ID", "type": "text", "required": True},
            {"name": "app_secret", "label": "App Secret", "type": "password", "required": True},
            {"name": "access_token", "label": "Access Token", "type": "password", "required": True},
        ],
        "srl_template": "srl://social.instagram/{user}/{media_id}",
        "drive_letter": None,
        "substrates": ["posts", "stories", "reels", "igtv"],
    },
    "snapchat": {
        "id": "snapchat",
        "name": "Snapchat",
        "icon": "👻",
        "logo_url": "https://www.snapchat.com/favicon.ico",
        "color": "#FFFC00",
        "category": "social",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://kit.snapchat.com/manage/",
        "docs_url": "https://developers.snap.com/docs/",
        "wizard_fields": [
            {"name": "client_id", "label": "Client ID", "type": "text", "required": True},
            {"name": "client_secret", "label": "Client Secret", "type": "password", "required": True},
        ],
        "srl_template": "srl://social.snapchat/{user}/{snap_id}",
        "drive_letter": None,
        "substrates": ["snaps", "stories"],
    },
    "tiktok": {
        "id": "tiktok",
        "name": "TikTok",
        "icon": "🎵",
        "logo_url": "https://www.tiktok.com/favicon.ico",
        "color": "#000000",
        "category": "social",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://developers.tiktok.com/",
        "docs_url": "https://developers.tiktok.com/doc/",
        "wizard_fields": [
            {"name": "client_key", "label": "Client Key", "type": "text", "required": True},
            {"name": "client_secret", "label": "Client Secret", "type": "password", "required": True},
        ],
        "srl_template": "srl://social.tiktok/{user}/{video_id}",
        "drive_letter": None,
        "substrates": ["videos", "users", "sounds"],
    },
    "mastodon": {
        "id": "mastodon",
        "name": "Mastodon",
        "icon": "🐘",
        "logo_url": "https://joinmastodon.org/favicon.ico",
        "color": "#6364FF",
        "category": "social",
        "auth_type": AuthType.OAUTH2,
        "auth_url": None,
        "docs_url": "https://docs.joinmastodon.org/api/",
        "wizard_fields": [
            {"name": "instance", "label": "Instance URL", "type": "url", "required": True, "placeholder": "https://mastodon.social"},
            {"name": "access_token", "label": "Access Token", "type": "password", "required": True},
        ],
        "srl_template": "srl://social.mastodon/{instance}/{user}/{toot_id}",
        "drive_letter": None,
        "substrates": ["toots", "users", "timelines"],
    },
    "pinterest": {
        "id": "pinterest",
        "name": "Pinterest",
        "icon": "📌",
        "logo_url": "https://www.pinterest.com/favicon.ico",
        "color": "#E60023",
        "category": "social",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://developers.pinterest.com/apps/",
        "docs_url": "https://developers.pinterest.com/docs/api/v5/",
        "wizard_fields": [
            {"name": "app_id", "label": "App ID", "type": "text", "required": True},
            {"name": "app_secret", "label": "App Secret", "type": "password", "required": True},
        ],
        "srl_template": "srl://social.pinterest/{user}/{board}/{pin_id}",
        "drive_letter": None,
        "substrates": ["pins", "boards", "users"],
    },
    
    # =========================================================================
    # MOVIES & ENTERTAINMENT
    # =========================================================================
    "tmdb": {
        "id": "tmdb",
        "name": "The Movie Database",
        "icon": "🎬",
        "logo_url": "https://www.themoviedb.org/favicon.ico",
        "color": "#01D277",
        "category": "entertainment",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://www.themoviedb.org/settings/api",
        "docs_url": "https://developers.themoviedb.org/3",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://media.tmdb/{type}/{id}",
        "drive_letter": None,
        "substrates": ["movies", "tv_shows", "people", "collections"],
    },
    "omdb": {
        "id": "omdb",
        "name": "OMDb API",
        "icon": "🎞️",
        "logo_url": "https://www.omdbapi.com/favicon.ico",
        "color": "#FFD700",
        "category": "entertainment",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://www.omdbapi.com/apikey.aspx",
        "docs_url": "https://www.omdbapi.com/",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://media.omdb/{imdb_id}",
        "drive_letter": None,
        "substrates": ["movies", "series", "episodes"],
    },
    "tvmaze": {
        "id": "tvmaze",
        "name": "TVmaze",
        "icon": "📺",
        "logo_url": "https://www.tvmaze.com/favicon.ico",
        "color": "#3C948B",
        "category": "entertainment",
        "auth_type": AuthType.NONE,
        "auth_url": None,
        "docs_url": "https://www.tvmaze.com/api",
        "wizard_fields": [],
        "srl_template": "srl://media.tvmaze/{show_id}",
        "drive_letter": None,
        "substrates": ["shows", "episodes", "people", "schedule"],
    },
    "imdb": {
        "id": "imdb",
        "name": "IMDb",
        "icon": "⭐",
        "logo_url": "https://www.imdb.com/favicon.ico",
        "color": "#F5C518",
        "category": "entertainment",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://rapidapi.com/apidojo/api/imdb8",
        "docs_url": "https://rapidapi.com/apidojo/api/imdb8",
        "wizard_fields": [
            {"name": "rapidapi_key", "label": "RapidAPI Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://media.imdb/{title_id}",
        "drive_letter": None,
        "substrates": ["titles", "actors", "ratings", "reviews"],
    },
    "twitch": {
        "id": "twitch",
        "name": "Twitch",
        "icon": "🎮",
        "logo_url": "https://www.twitch.tv/favicon.ico",
        "color": "#9146FF",
        "category": "entertainment",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://dev.twitch.tv/console/apps",
        "docs_url": "https://dev.twitch.tv/docs/api/",
        "wizard_fields": [
            {"name": "client_id", "label": "Client ID", "type": "text", "required": True},
            {"name": "client_secret", "label": "Client Secret", "type": "password", "required": True},
        ],
        "srl_template": "srl://media.twitch/{channel}/{video_id}",
        "drive_letter": None,
        "substrates": ["streams", "videos", "clips", "channels", "games"],
    },
    
    # =========================================================================
    # REFERENCE & KNOWLEDGE
    # =========================================================================
    "dictionary": {
        "id": "dictionary",
        "name": "Free Dictionary",
        "icon": "📖",
        "logo_url": None,
        "color": "#2E7D32",
        "category": "reference",
        "auth_type": AuthType.NONE,
        "auth_url": None,
        "docs_url": "https://dictionaryapi.dev/",
        "wizard_fields": [],
        "srl_template": "srl://ref.dictionary/{word}",
        "drive_letter": None,
        "substrates": ["definitions", "phonetics", "synonyms"],
    },
    "thesaurus": {
        "id": "thesaurus",
        "name": "Datamuse Thesaurus",
        "icon": "📚",
        "logo_url": None,
        "color": "#5D4037",
        "category": "reference",
        "auth_type": AuthType.NONE,
        "auth_url": None,
        "docs_url": "https://www.datamuse.com/api/",
        "wizard_fields": [],
        "srl_template": "srl://ref.thesaurus/{word}",
        "drive_letter": None,
        "substrates": ["synonyms", "antonyms", "rhymes", "related"],
    },
    "wikipedia": {
        "id": "wikipedia",
        "name": "Wikipedia",
        "icon": "🌐",
        "logo_url": "https://www.wikipedia.org/favicon.ico",
        "color": "#000000",
        "category": "reference",
        "auth_type": AuthType.NONE,
        "auth_url": None,
        "docs_url": "https://www.mediawiki.org/wiki/API:Main_page",
        "wizard_fields": [
            {"name": "language", "label": "Language Code", "type": "text", "required": False, "default": "en"},
        ],
        "srl_template": "srl://ref.wikipedia/{lang}/{article}",
        "drive_letter": None,
        "substrates": ["articles", "categories", "images"],
    },
    "wikidata": {
        "id": "wikidata",
        "name": "Wikidata",
        "icon": "🔗",
        "logo_url": "https://www.wikidata.org/favicon.ico",
        "color": "#006699",
        "category": "reference",
        "auth_type": AuthType.NONE,
        "auth_url": None,
        "docs_url": "https://www.wikidata.org/wiki/Wikidata:Data_access",
        "wizard_fields": [],
        "srl_template": "srl://ref.wikidata/{entity_id}",
        "drive_letter": None,
        "substrates": ["entities", "properties", "statements"],
    },
    "openlibrary": {
        "id": "openlibrary",
        "name": "Open Library",
        "icon": "📕",
        "logo_url": "https://openlibrary.org/favicon.ico",
        "color": "#E74C3C",
        "category": "reference",
        "auth_type": AuthType.NONE,
        "auth_url": None,
        "docs_url": "https://openlibrary.org/developers/api",
        "wizard_fields": [],
        "srl_template": "srl://ref.openlibrary/{work_id}",
        "drive_letter": None,
        "substrates": ["books", "authors", "subjects", "covers"],
    },
    "gutenberg": {
        "id": "gutenberg",
        "name": "Project Gutenberg",
        "icon": "📜",
        "logo_url": "https://www.gutenberg.org/favicon.ico",
        "color": "#8B4513",
        "category": "reference",
        "auth_type": AuthType.NONE,
        "auth_url": None,
        "docs_url": "https://www.gutenberg.org/policy/robot_access.html",
        "wizard_fields": [],
        "srl_template": "srl://ref.gutenberg/{book_id}",
        "drive_letter": None,
        "substrates": ["ebooks", "authors", "subjects"],
    },
    
    # =========================================================================
    # IMAGES & MEDIA CDN
    # =========================================================================
    "unsplash": {
        "id": "unsplash",
        "name": "Unsplash",
        "icon": "📸",
        "logo_url": "https://unsplash.com/favicon.ico",
        "color": "#000000",
        "category": "images",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://unsplash.com/developers",
        "docs_url": "https://unsplash.com/documentation",
        "wizard_fields": [
            {"name": "access_key", "label": "Access Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://images.unsplash/{photo_id}",
        "drive_letter": None,
        "substrates": ["photos", "collections", "users", "topics"],
    },
    "pexels": {
        "id": "pexels",
        "name": "Pexels",
        "icon": "🖼️",
        "logo_url": "https://www.pexels.com/favicon.ico",
        "color": "#05A081",
        "category": "images",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://www.pexels.com/api/",
        "docs_url": "https://www.pexels.com/api/documentation/",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://images.pexels/{photo_id}",
        "drive_letter": None,
        "substrates": ["photos", "videos", "collections"],
    },
    "pixabay": {
        "id": "pixabay",
        "name": "Pixabay",
        "icon": "🌄",
        "logo_url": "https://pixabay.com/favicon.ico",
        "color": "#2EC66D",
        "category": "images",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://pixabay.com/api/docs/",
        "docs_url": "https://pixabay.com/api/docs/",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://images.pixabay/{image_id}",
        "drive_letter": None,
        "substrates": ["photos", "videos", "illustrations"],
    },
    "giphy": {
        "id": "giphy",
        "name": "GIPHY",
        "icon": "🎭",
        "logo_url": "https://giphy.com/favicon.ico",
        "color": "#FF6666",
        "category": "images",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://developers.giphy.com/dashboard/",
        "docs_url": "https://developers.giphy.com/docs/api/",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://images.giphy/{gif_id}",
        "drive_letter": None,
        "substrates": ["gifs", "stickers", "trending"],
    },
    
    # =========================================================================
    # STOCKS & FINANCE
    # =========================================================================
    "alphavantage": {
        "id": "alphavantage",
        "name": "Alpha Vantage",
        "icon": "📈",
        "logo_url": "https://www.alphavantage.co/favicon.ico",
        "color": "#22C55E",
        "category": "finance",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://www.alphavantage.co/support/#api-key",
        "docs_url": "https://www.alphavantage.co/documentation/",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://finance.alphavantage/{symbol}",
        "drive_letter": None,
        "substrates": ["stocks", "forex", "crypto", "indicators"],
    },
    "finnhub": {
        "id": "finnhub",
        "name": "Finnhub",
        "icon": "💹",
        "logo_url": "https://finnhub.io/favicon.ico",
        "color": "#00BFFF",
        "category": "finance",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://finnhub.io/register",
        "docs_url": "https://finnhub.io/docs/api",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://finance.finnhub/{symbol}",
        "drive_letter": None,
        "substrates": ["quotes", "news", "earnings", "recommendations"],
    },
    "polygon": {
        "id": "polygon",
        "name": "Polygon.io",
        "icon": "🔷",
        "logo_url": "https://polygon.io/favicon.ico",
        "color": "#8B5CF6",
        "category": "finance",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://polygon.io/dashboard/signup",
        "docs_url": "https://polygon.io/docs/",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://finance.polygon/{ticker}",
        "drive_letter": None,
        "substrates": ["stocks", "options", "forex", "crypto"],
    },
    "iex": {
        "id": "iex",
        "name": "IEX Cloud",
        "icon": "📊",
        "logo_url": "https://iexcloud.io/favicon.ico",
        "color": "#2D9CDB",
        "category": "finance",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://iexcloud.io/console/",
        "docs_url": "https://iexcloud.io/docs/api/",
        "wizard_fields": [
            {"name": "api_key", "label": "API Token", "type": "password", "required": True},
        ],
        "srl_template": "srl://finance.iex/{symbol}",
        "drive_letter": None,
        "substrates": ["quotes", "charts", "company", "news"],
    },
    
    # =========================================================================
    # WEATHER
    # =========================================================================
    "openweather": {
        "id": "openweather",
        "name": "OpenWeatherMap",
        "icon": "🌦️",
        "logo_url": "https://openweathermap.org/favicon.ico",
        "color": "#EB6E4B",
        "category": "weather",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://openweathermap.org/api",
        "docs_url": "https://openweathermap.org/api",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://weather.openweather/{city}",
        "drive_letter": None,
        "substrates": ["current", "forecast", "historical", "alerts"],
    },
    "weatherapi": {
        "id": "weatherapi",
        "name": "WeatherAPI",
        "icon": "☀️",
        "logo_url": "https://www.weatherapi.com/favicon.ico",
        "color": "#FFB300",
        "category": "weather",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://www.weatherapi.com/signup.aspx",
        "docs_url": "https://www.weatherapi.com/docs/",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://weather.weatherapi/{location}",
        "drive_letter": None,
        "substrates": ["current", "forecast", "history", "astronomy"],
    },
    "visualcrossing": {
        "id": "visualcrossing",
        "name": "Visual Crossing",
        "icon": "🌤️",
        "logo_url": "https://www.visualcrossing.com/favicon.ico",
        "color": "#3498DB",
        "category": "weather",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://www.visualcrossing.com/sign-up",
        "docs_url": "https://www.visualcrossing.com/resources/documentation/",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://weather.visualcrossing/{location}",
        "drive_letter": None,
        "substrates": ["current", "forecast", "historical"],
    },
    
    # =========================================================================
    # GEOGRAPHY & MAPPING
    # =========================================================================
    "openstreetmap": {
        "id": "openstreetmap",
        "name": "OpenStreetMap",
        "icon": "🗺️",
        "logo_url": "https://www.openstreetmap.org/favicon.ico",
        "color": "#7EBC6F",
        "category": "geography",
        "auth_type": AuthType.NONE,
        "auth_url": None,
        "docs_url": "https://wiki.openstreetmap.org/wiki/API",
        "wizard_fields": [],
        "srl_template": "srl://geo.osm/{type}/{id}",
        "drive_letter": None,
        "substrates": ["nodes", "ways", "relations", "changesets"],
    },
    "mapbox": {
        "id": "mapbox",
        "name": "Mapbox",
        "icon": "🧭",
        "logo_url": "https://www.mapbox.com/favicon.ico",
        "color": "#000000",
        "category": "geography",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://account.mapbox.com/",
        "docs_url": "https://docs.mapbox.com/api/",
        "wizard_fields": [
            {"name": "access_token", "label": "Access Token", "type": "password", "required": True},
        ],
        "srl_template": "srl://geo.mapbox/{type}/{id}",
        "drive_letter": None,
        "substrates": ["geocoding", "directions", "isochrones", "tilesets"],
    },
    "geonames": {
        "id": "geonames",
        "name": "GeoNames",
        "icon": "🌍",
        "logo_url": "https://www.geonames.org/favicon.ico",
        "color": "#4A90D9",
        "category": "geography",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://www.geonames.org/login",
        "docs_url": "https://www.geonames.org/export/web-services.html",
        "wizard_fields": [
            {"name": "username", "label": "Username", "type": "text", "required": True},
        ],
        "srl_template": "srl://geo.geonames/{geoname_id}",
        "drive_letter": None,
        "substrates": ["places", "countries", "admin_divisions", "postalcodes"],
    },
    "restcountries": {
        "id": "restcountries",
        "name": "REST Countries",
        "icon": "🏳️",
        "logo_url": None,
        "color": "#3F51B5",
        "category": "geography",
        "auth_type": AuthType.NONE,
        "auth_url": None,
        "docs_url": "https://restcountries.com/",
        "wizard_fields": [],
        "srl_template": "srl://geo.countries/{country_code}",
        "drive_letter": None,
        "substrates": ["countries", "regions", "languages", "currencies"],
    },
    "zipcodebase": {
        "id": "zipcodebase",
        "name": "ZipCodeBase",
        "icon": "📮",
        "logo_url": "https://zipcodebase.com/favicon.ico",
        "color": "#FF5722",
        "category": "geography",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://app.zipcodebase.com/register",
        "docs_url": "https://app.zipcodebase.com/documentation",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://geo.zipcode/{code}",
        "drive_letter": None,
        "substrates": ["zipcodes", "cities", "states"],
    },
    
    # =========================================================================
    # ACADEMIC & EDUCATION
    # =========================================================================
    "arxiv": {
        "id": "arxiv",
        "name": "arXiv",
        "icon": "🎓",
        "logo_url": "https://arxiv.org/favicon.ico",
        "color": "#B31B1B",
        "category": "academic",
        "auth_type": AuthType.NONE,
        "auth_url": None,
        "docs_url": "https://arxiv.org/help/api/",
        "wizard_fields": [],
        "srl_template": "srl://academic.arxiv/{paper_id}",
        "drive_letter": None,
        "substrates": ["papers", "authors", "categories"],
    },
    "semanticscholar": {
        "id": "semanticscholar",
        "name": "Semantic Scholar",
        "icon": "🔬",
        "logo_url": "https://www.semanticscholar.org/favicon.ico",
        "color": "#1857B6",
        "category": "academic",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://www.semanticscholar.org/product/api",
        "docs_url": "https://api.semanticscholar.org/",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": False},
        ],
        "srl_template": "srl://academic.semanticscholar/{paper_id}",
        "drive_letter": None,
        "substrates": ["papers", "authors", "citations", "topics"],
    },
    "crossref": {
        "id": "crossref",
        "name": "Crossref",
        "icon": "📑",
        "logo_url": "https://www.crossref.org/favicon.ico",
        "color": "#F36F21",
        "category": "academic",
        "auth_type": AuthType.NONE,
        "auth_url": None,
        "docs_url": "https://api.crossref.org/",
        "wizard_fields": [
            {"name": "email", "label": "Email (for polite pool)", "type": "email", "required": False},
        ],
        "srl_template": "srl://academic.crossref/{doi}",
        "drive_letter": None,
        "substrates": ["works", "funders", "journals", "publishers"],
    },
    "pubmed": {
        "id": "pubmed",
        "name": "PubMed",
        "icon": "🏥",
        "logo_url": "https://www.ncbi.nlm.nih.gov/favicon.ico",
        "color": "#326599",
        "category": "academic",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://www.ncbi.nlm.nih.gov/account/settings/",
        "docs_url": "https://www.ncbi.nlm.nih.gov/books/NBK25500/",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": False},
        ],
        "srl_template": "srl://academic.pubmed/{pmid}",
        "drive_letter": None,
        "substrates": ["articles", "abstracts", "citations", "mesh_terms"],
    },
    "coursera": {
        "id": "coursera",
        "name": "Coursera",
        "icon": "📚",
        "logo_url": "https://www.coursera.org/favicon.ico",
        "color": "#0056D2",
        "category": "academic",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://www.coursera.org/account/profile",
        "docs_url": "https://build.coursera.org/",
        "wizard_fields": [
            {"name": "client_id", "label": "Client ID", "type": "text", "required": True},
            {"name": "client_secret", "label": "Client Secret", "type": "password", "required": True},
        ],
        "srl_template": "srl://edu.coursera/{course_id}",
        "drive_letter": None,
        "substrates": ["courses", "specializations", "certificates"],
    },
    "khan_academy": {
        "id": "khan_academy",
        "name": "Khan Academy",
        "icon": "🧮",
        "logo_url": "https://www.khanacademy.org/favicon.ico",
        "color": "#14BF96",
        "category": "academic",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://www.khanacademy.org/profile",
        "docs_url": "https://github.com/Khan/khan-api/wiki",
        "wizard_fields": [
            {"name": "consumer_key", "label": "Consumer Key", "type": "text", "required": True},
            {"name": "consumer_secret", "label": "Consumer Secret", "type": "password", "required": True},
        ],
        "srl_template": "srl://edu.khan/{topic}/{content_id}",
        "drive_letter": None,
        "substrates": ["videos", "exercises", "topics", "progress"],
    },
    
    # =========================================================================
    # GAMES
    # =========================================================================
    "rawg": {
        "id": "rawg",
        "name": "RAWG Games",
        "icon": "🎮",
        "logo_url": "https://rawg.io/favicon.ico",
        "color": "#1D1D1D",
        "category": "games",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://rawg.io/apidocs",
        "docs_url": "https://api.rawg.io/docs/",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://games.rawg/{game_id}",
        "drive_letter": None,
        "substrates": ["games", "genres", "platforms", "developers"],
    },
    "igdb": {
        "id": "igdb",
        "name": "IGDB",
        "icon": "🕹️",
        "logo_url": "https://www.igdb.com/favicon.ico",
        "color": "#9147FF",
        "category": "games",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://dev.twitch.tv/console/apps",
        "docs_url": "https://api-docs.igdb.com/",
        "wizard_fields": [
            {"name": "client_id", "label": "Client ID", "type": "text", "required": True},
            {"name": "client_secret", "label": "Client Secret", "type": "password", "required": True},
        ],
        "srl_template": "srl://games.igdb/{game_id}",
        "drive_letter": None,
        "substrates": ["games", "companies", "characters", "franchises"],
    },
    "steam": {
        "id": "steam",
        "name": "Steam",
        "icon": "🎲",
        "logo_url": "https://store.steampowered.com/favicon.ico",
        "color": "#1B2838",
        "category": "games",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://steamcommunity.com/dev/apikey",
        "docs_url": "https://developer.valvesoftware.com/wiki/Steam_Web_API",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://games.steam/{app_id}",
        "drive_letter": None,
        "substrates": ["games", "players", "achievements", "stats"],
    },
    
    # =========================================================================
    # LAW & GOVERNMENT
    # =========================================================================
    "usagov": {
        "id": "usagov",
        "name": "USA.gov",
        "icon": "🇺🇸",
        "logo_url": "https://www.usa.gov/favicon.ico",
        "color": "#112E51",
        "category": "government",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://api.data.gov/signup/",
        "docs_url": "https://www.data.gov/developers/apis",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://gov.usa/{dataset}",
        "drive_letter": None,
        "substrates": ["datasets", "agencies", "regulations"],
    },
    "congress": {
        "id": "congress",
        "name": "Congress.gov",
        "icon": "🏛️",
        "logo_url": "https://www.congress.gov/favicon.ico",
        "color": "#003366",
        "category": "government",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://api.congress.gov/sign-up/",
        "docs_url": "https://api.congress.gov/",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://gov.congress/{bill_id}",
        "drive_letter": None,
        "substrates": ["bills", "members", "committees", "amendments"],
    },
    "federalregister": {
        "id": "federalregister",
        "name": "Federal Register",
        "icon": "📋",
        "logo_url": "https://www.federalregister.gov/favicon.ico",
        "color": "#0B3B5C",
        "category": "government",
        "auth_type": AuthType.NONE,
        "auth_url": None,
        "docs_url": "https://www.federalregister.gov/reader-aids/developer-resources/rest-api",
        "wizard_fields": [],
        "srl_template": "srl://gov.federalregister/{document_number}",
        "drive_letter": None,
        "substrates": ["documents", "agencies", "public_inspection"],
    },
    "courtlistener": {
        "id": "courtlistener",
        "name": "CourtListener",
        "icon": "⚖️",
        "logo_url": "https://www.courtlistener.com/favicon.ico",
        "color": "#6C757D",
        "category": "government",
        "auth_type": AuthType.TOKEN,
        "auth_url": "https://www.courtlistener.com/profile/",
        "docs_url": "https://www.courtlistener.com/help/api/rest/",
        "wizard_fields": [
            {"name": "token", "label": "API Token", "type": "password", "required": True},
        ],
        "srl_template": "srl://law.courtlistener/{case_id}",
        "drive_letter": None,
        "substrates": ["opinions", "courts", "dockets", "judges"],
    },
    "openstates": {
        "id": "openstates",
        "name": "Open States",
        "icon": "🗳️",
        "logo_url": "https://openstates.org/favicon.ico",
        "color": "#4AA564",
        "category": "government",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://openstates.org/accounts/register/",
        "docs_url": "https://docs.openstates.org/api-v3/",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://gov.openstates/{state}/{bill_id}",
        "drive_letter": None,
        "substrates": ["bills", "legislators", "committees", "votes"],
    },
    
    # =========================================================================
    # RECIPES & CRAFTS
    # =========================================================================
    "spoonacular": {
        "id": "spoonacular",
        "name": "Spoonacular",
        "icon": "🍽️",
        "logo_url": "https://spoonacular.com/favicon.ico",
        "color": "#8DC63F",
        "category": "recipes",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://spoonacular.com/food-api/console",
        "docs_url": "https://spoonacular.com/food-api/docs",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://recipes.spoonacular/{recipe_id}",
        "drive_letter": None,
        "substrates": ["recipes", "ingredients", "meal_plans", "nutrition"],
    },
    "edamam": {
        "id": "edamam",
        "name": "Edamam",
        "icon": "🥗",
        "logo_url": "https://www.edamam.com/favicon.ico",
        "color": "#67B26F",
        "category": "recipes",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://developer.edamam.com/admin/applications",
        "docs_url": "https://developer.edamam.com/edamam-docs-recipe-api",
        "wizard_fields": [
            {"name": "app_id", "label": "Application ID", "type": "text", "required": True},
            {"name": "app_key", "label": "Application Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://recipes.edamam/{recipe_id}",
        "drive_letter": None,
        "substrates": ["recipes", "nutrition", "food_database"],
    },
    "ravelry": {
        "id": "ravelry",
        "name": "Ravelry",
        "icon": "🧶",
        "logo_url": "https://www.ravelry.com/favicon.ico",
        "color": "#EE6352",
        "category": "crafts",
        "auth_type": AuthType.OAUTH2,
        "auth_url": "https://www.ravelry.com/pro/developer",
        "docs_url": "https://www.ravelry.com/api",
        "wizard_fields": [
            {"name": "username", "label": "Username", "type": "text", "required": True},
            {"name": "password", "label": "Password", "type": "password", "required": True},
        ],
        "srl_template": "srl://crafts.ravelry/{pattern_id}",
        "drive_letter": None,
        "substrates": ["patterns", "yarns", "projects", "stashes"],
    },
    
    # =========================================================================
    # EBOOKS & READING
    # =========================================================================
    "googlebooks": {
        "id": "googlebooks",
        "name": "Google Books",
        "icon": "📙",
        "logo_url": "https://books.google.com/favicon.ico",
        "color": "#4285F4",
        "category": "ebooks",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://console.cloud.google.com/apis/credentials",
        "docs_url": "https://developers.google.com/books/docs/v1/getting_started",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://ebooks.google/{volume_id}",
        "drive_letter": None,
        "substrates": ["volumes", "bookshelves", "annotations"],
    },
    "goodreads": {
        "id": "goodreads",
        "name": "Goodreads",
        "icon": "📖",
        "logo_url": "https://www.goodreads.com/favicon.ico",
        "color": "#553B08",
        "category": "ebooks",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://www.goodreads.com/api/keys",
        "docs_url": "https://www.goodreads.com/api",
        "wizard_fields": [
            {"name": "key", "label": "API Key", "type": "password", "required": True},
            {"name": "secret", "label": "API Secret", "type": "password", "required": True},
        ],
        "srl_template": "srl://ebooks.goodreads/{book_id}",
        "drive_letter": None,
        "substrates": ["books", "authors", "reviews", "shelves"],
    },
    "librarything": {
        "id": "librarything",
        "name": "LibraryThing",
        "icon": "📚",
        "logo_url": "https://www.librarything.com/favicon.ico",
        "color": "#333333",
        "category": "ebooks",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://www.librarything.com/services/keys.php",
        "docs_url": "https://www.librarything.com/services/",
        "wizard_fields": [
            {"name": "api_key", "label": "API Key", "type": "password", "required": True},
        ],
        "srl_template": "srl://ebooks.librarything/{work_id}",
        "drive_letter": None,
        "substrates": ["works", "authors", "tags", "collections"],
    },
    
    # =========================================================================
    # GENERAL KNOWLEDGE
    # =========================================================================
    "wolfram": {
        "id": "wolfram",
        "name": "Wolfram Alpha",
        "icon": "🔶",
        "logo_url": "https://www.wolframalpha.com/favicon.ico",
        "color": "#DD1100",
        "category": "knowledge",
        "auth_type": AuthType.API_KEY,
        "auth_url": "https://developer.wolframalpha.com/portal/myapps/",
        "docs_url": "https://products.wolframalpha.com/api/documentation/",
        "wizard_fields": [
            {"name": "app_id", "label": "App ID", "type": "password", "required": True},
        ],
        "srl_template": "srl://knowledge.wolfram/{query}",
        "drive_letter": None,
        "substrates": ["queries", "calculations", "conversions"],
    },
    "dbpedia": {
        "id": "dbpedia",
        "name": "DBpedia",
        "icon": "🌐",
        "logo_url": "https://www.dbpedia.org/favicon.ico",
        "color": "#F9A825",
        "category": "knowledge",
        "auth_type": AuthType.NONE,
        "auth_url": None,
        "docs_url": "https://www.dbpedia.org/resources/",
        "wizard_fields": [],
        "srl_template": "srl://knowledge.dbpedia/{resource}",
        "drive_letter": None,
        "substrates": ["resources", "classes", "properties"],
    },
    "conceptnet": {
        "id": "conceptnet",
        "name": "ConceptNet",
        "icon": "🧠",
        "logo_url": None,
        "color": "#4CAF50",
        "category": "knowledge",
        "auth_type": AuthType.NONE,
        "auth_url": None,
        "docs_url": "https://github.com/commonsense/conceptnet5/wiki/API",
        "wizard_fields": [],
        "srl_template": "srl://knowledge.conceptnet/{concept}",
        "drive_letter": None,
        "substrates": ["concepts", "relations", "assertions"],
    },
    "trivia": {
        "id": "trivia",
        "name": "Open Trivia DB",
        "icon": "❓",
        "logo_url": "https://opentdb.com/favicon.ico",
        "color": "#FF9800",
        "category": "knowledge",
        "auth_type": AuthType.NONE,
        "auth_url": None,
        "docs_url": "https://opentdb.com/api_config.php",
        "wizard_fields": [],
        "srl_template": "srl://knowledge.trivia/{category}",
        "drive_letter": None,
        "substrates": ["questions", "categories"],
    },
}

# Category metadata for UI organization
SERVICE_CATEGORIES = {
    "cloud_storage": {
        "name": "Cloud Storage",
        "icon": "☁️",
        "color": "#4285F4",
        "description": "Cloud file storage services",
    },
    "email": {
        "name": "Email",
        "icon": "📧",
        "color": "#EA4335",
        "description": "Email providers and mailboxes",
    },
    "database": {
        "name": "Databases",
        "icon": "🗄️",
        "color": "#336791",
        "description": "SQL and NoSQL databases",
    },
    "development": {
        "name": "Development",
        "icon": "💻",
        "color": "#181717",
        "description": "Code repositories and dev tools",
    },
    "ai": {
        "name": "AI & ML",
        "icon": "🤖",
        "color": "#412991",
        "description": "AI and machine learning services",
    },
    "social": {
        "name": "Social Media",
        "icon": "👥",
        "color": "#1DA1F2",
        "description": "Social networks and communities",
    },
    "music": {
        "name": "Music & Media",
        "icon": "🎵",
        "color": "#1DB954",
        "description": "Music and media streaming",
    },
    "feeds": {
        "name": "Feeds & News",
        "icon": "📰",
        "color": "#FFA500",
        "description": "RSS, news, and podcasts",
    },
    "shopping": {
        "name": "E-Commerce",
        "icon": "🛒",
        "color": "#FF9900",
        "description": "Shopping and payment platforms",
    },
    "productivity": {
        "name": "Productivity",
        "icon": "📋",
        "color": "#000000",
        "description": "Work and productivity apps",
    },
    "local": {
        "name": "Local Resources",
        "icon": "💾",
        "color": "#555555",
        "description": "Local files and network shares",
    },
    "api": {
        "name": "Custom APIs",
        "icon": "🔗",
        "color": "#00A86B",
        "description": "REST, GraphQL, and webhooks",
    },
    # =========================================================================
    # NEW CATEGORIES
    # =========================================================================
    "entertainment": {
        "name": "Entertainment",
        "icon": "🎬",
        "color": "#E50914",
        "description": "Movies, TV shows, and streaming",
    },
    "reference": {
        "name": "Reference",
        "icon": "📖",
        "color": "#2E7D32",
        "description": "Dictionaries, encyclopedias, and knowledge bases",
    },
    "images": {
        "name": "Images",
        "icon": "🖼️",
        "color": "#FF6B6B",
        "description": "Stock photos, CDNs, and media libraries",
    },
    "finance": {
        "name": "Finance",
        "icon": "📈",
        "color": "#22C55E",
        "description": "Stocks, crypto, and financial data",
    },
    "weather": {
        "name": "Weather",
        "icon": "🌦️",
        "color": "#EB6E4B",
        "description": "Weather data and forecasts",
    },
    "geography": {
        "name": "Geography",
        "icon": "🗺️",
        "color": "#7EBC6F",
        "description": "Maps, GIS, and location services",
    },
    "academic": {
        "name": "Academic",
        "icon": "🎓",
        "color": "#B31B1B",
        "description": "Research papers, education, and scholarly data",
    },
    "games": {
        "name": "Games",
        "icon": "🎮",
        "color": "#9146FF",
        "description": "Video games, gaming platforms, and esports",
    },
    "government": {
        "name": "Government",
        "icon": "🏛️",
        "color": "#112E51",
        "description": "Government data, laws, and regulations",
    },
    "recipes": {
        "name": "Recipes",
        "icon": "🍽️",
        "color": "#8DC63F",
        "description": "Recipes, nutrition, and food data",
    },
    "crafts": {
        "name": "Crafts",
        "icon": "🧶",
        "color": "#EE6352",
        "description": "DIY, crafts, and hobby projects",
    },
    "ebooks": {
        "name": "eBooks",
        "icon": "📙",
        "color": "#553B08",
        "description": "Digital books, libraries, and reading lists",
    },
    "knowledge": {
        "name": "Knowledge",
        "icon": "🧠",
        "color": "#4CAF50",
        "description": "General knowledge, trivia, and semantic data",
    },
}


# =============================================================================
# DATA MODELS
# =============================================================================

class ServiceStatus:
    """Connection status for services"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected" 
    UNAVAILABLE = "unavailable"
    PENDING = "pending"
    ERROR = "error"
    
    @staticmethod
    def get_dot(status: str) -> str:
        """Get status dot emoji"""
        return {
            "connected": "🟢",
            "disconnected": "🔴",
            "unavailable": "⚫",
            "pending": "🟡",
            "error": "🟠",
        }.get(status, "⚫")
    
    @staticmethod
    def get_css_class(status: str) -> str:
        """Get CSS class for status"""
        return f"status-{status}"


@dataclass
class ServiceConnection:
    """A connection to an external service"""
    service_id: str
    name: str
    category: str
    icon: str
    color: str
    status: str = ServiceStatus.DISCONNECTED
    auth_type: str = AuthType.NONE
    credentials: Dict[str, str] = field(default_factory=dict)
    drive_letter: Optional[str] = None
    srl_base: Optional[str] = None
    last_connected: Optional[str] = None
    last_sync: Optional[str] = None
    items_count: int = 0
    error_message: Optional[str] = None
    substrates: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "service_id": self.service_id,
            "name": self.name,
            "category": self.category,
            "icon": self.icon,
            "color": self.color,
            "status": self.status,
            "status_dot": ServiceStatus.get_dot(self.status),
            "auth_type": self.auth_type,
            "drive_letter": self.drive_letter,
            "srl_base": self.srl_base,
            "last_connected": self.last_connected,
            "last_sync": self.last_sync,
            "items_count": self.items_count,
            "error_message": self.error_message,
            "substrates": self.substrates,
        }


@dataclass
class SRL:
    """Substrate Reference Layer - Universal resource identifier"""
    uri: str
    service_id: str
    substrate_type: str
    path: str
    schema: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    cached_data: Optional[Any] = None
    cache_timestamp: Optional[str] = None
    materialized: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "uri": self.uri,
            "service_id": self.service_id,
            "substrate_type": self.substrate_type,
            "path": self.path,
            "schema": self.schema,
            "metadata": self.metadata,
            "materialized": self.materialized,
            "cache_timestamp": self.cache_timestamp,
        }


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


@dataclass
class AppConnection:
    """
    Connection to a ButterflyFx application.
    
    Apps that can be connected:
    - Universal HDD (port 8765)
    - Dimensional Explorer (port 8767)
    - Helix Database (port 8768)
    - Any HTTP-capable ButterflyFx app
    """
    app_id: str
    name: str
    app_type: str  # uhd, explorer, database, custom
    icon: str
    color: str
    host: str = "localhost"
    port: int = 8765
    status: str = "disconnected"
    version: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    last_ping: Optional[str] = None
    connected_at: Optional[str] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "app_id": self.app_id,
            "name": self.name,
            "app_type": self.app_type,
            "icon": self.icon,
            "color": self.color,
            "host": self.host,
            "port": self.port,
            "status": self.status,
            "status_dot": ServiceStatus.get_dot(self.status),
            "version": self.version,
            "capabilities": self.capabilities,
            "last_ping": self.last_ping,
            "connected_at": self.connected_at,
            "error_message": self.error_message,
        }
    
    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"


# =============================================================================
# APP REGISTRY - ButterflyFx Applications
# =============================================================================

APP_REGISTRY = {
    "universal_hdd": {
        "id": "universal_hdd",
        "name": "Universal Hard Drive",
        "app_type": "uhd",
        "icon": "💾",
        "color": "#4285F4",
        "default_port": 8765,
        "capabilities": ["files", "drives", "srls", "search", "sync"],
        "description": "Windows Explorer-like interface for all data sources",
    },
    "dimensional_explorer": {
        "id": "dimensional_explorer",
        "name": "Dimensional Explorer",
        "app_type": "explorer",
        "icon": "🌀",
        "color": "#9C27B0",
        "default_port": 8767,
        "capabilities": ["visualize", "navigate", "inspect", "manifold"],
        "description": "Explore and visualize the dimensional structure",
    },
    "helix_database": {
        "id": "helix_database",
        "name": "Helix Database",
        "app_type": "database",
        "icon": "🗄️",
        "color": "#336791",
        "default_port": 8768,
        "capabilities": ["store", "query", "index", "backup"],
        "description": "Native helix-format database storage",
    },
    "ai_assistant": {
        "id": "ai_assistant",
        "name": "AI Assistant",
        "app_type": "ai",
        "icon": "🤖",
        "color": "#412991",
        "default_port": 8769,
        "capabilities": ["chat", "complete", "embed", "analyze"],
        "description": "Connected AI assistants and models",
    },
    # =========================================================================
    # CONNECTED AI - The AI assistant currently interacting with the system
    # =========================================================================
    "claude": {
        "id": "claude",
        "name": "Claude (Anthropic)",
        "app_type": "ai",
        "icon": "🦋",
        "color": "#CC785C",
        "default_port": None,  # Connected via IDE/API
        "capabilities": [
            "chat", "code", "analyze", "refactor", "explain",
            "debug", "generate", "review", "document", "search",
            "create_files", "edit_files", "run_commands", "ingest_knowledge"
        ],
        "description": "Claude AI - Currently connected and assisting with system development",
        "connection_type": "active",  # Currently connected session
        "knowledge_access": True,  # Can access ingested knowledge
        "can_modify": True,  # Can modify the system
    },
    "copilot": {
        "id": "copilot",
        "name": "GitHub Copilot",  
        "app_type": "ai",
        "icon": "✈️",
        "color": "#000000",
        "default_port": None,
        "capabilities": ["code", "complete", "suggest", "explain"],
        "description": "GitHub Copilot code assistant",
        "connection_type": "active",
    },
    "openai": {
        "id": "openai",
        "name": "OpenAI API",
        "app_type": "ai",
        "icon": "🧠",
        "color": "#00A67E",
        "default_port": None,
        "capabilities": ["chat", "complete", "embed", "image", "audio", "vision"],
        "description": "OpenAI GPT models and APIs",
        "connection_type": "api",
    },
    "ollama": {
        "id": "ollama",
        "name": "Ollama (Local AI)",
        "app_type": "ai",
        "icon": "🦙",
        "color": "#FFFFFF",
        "default_port": 11434,
        "capabilities": ["chat", "complete", "embed"],
        "description": "Local AI models via Ollama",
        "connection_type": "local",
    },
}


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


# =============================================================================
# UNIVERSAL CONNECTOR SERVICE - Full Service Management + HTTP Server
# =============================================================================

import threading
import http.server
import socketserver
import webbrowser
import secrets
import base64
import hashlib
from urllib.parse import parse_qs, urlparse
import os

# Credential storage path
CREDENTIALS_PATH = Path(__file__).parent.parent / "data" / "auth" / "credentials.json"


class UniversalConnectorService:
    """
    Universal Connector Service - Connect to Anything
    
    A standalone application + background service that:
    - Manages connections to 102+ external services
    - Connects to ButterflyFx applications (UHD, Explorer, etc.)
    - Stores credentials securely
    - Generates SRLs for all connected resources
    - INGESTS connected data into the kernel (substrates/manifolds)
    - Exposes REST API for other apps
    - Provides web UI with logo buttons and connection wizards
    
    Connected services become part of the system:
    - Data is ingested into ManifoldSubstrate
    - SRLs are registered for O(1) access
    - AI assistants can access all connected knowledge
    """
    
    def __init__(self, port: int = 8766):
        self.port = port
        self._services: Dict[str, ServiceConnection] = {}
        self._srls: Dict[str, SRL] = {}
        self._credentials: Dict[str, Dict] = {}
        self._drive_assignments: Dict[str, str] = {}  # drive_letter -> service_id
        
        # Stats - initialized early so other methods can use it
        self._stats = {
            "total_services": len(SERVICE_REGISTRY),
            "total_apps": len(APP_REGISTRY),
            "connected_services": 0,
            "connected_apps": 0,
            "srls_generated": 0,
            "kernel_ingestions": 0,
            "total_items": 0,
        }
        
        # =====================================================================
        # KERNEL INTEGRATION - Connected services become part of the system
        # =====================================================================
        self.kernel = HelixKernel()
        self.substrate = ManifoldSubstrate()
        self.kernel.set_substrate(self.substrate)
        
        # =====================================================================
        # APP CONNECTIONS - Connect to ButterflyFx applications
        # =====================================================================
        self._apps: Dict[str, AppConnection] = {}
        self._init_apps()
        
        # Legacy API connector
        self.api_connector = UniversalConnector()
        
        # Initialize services from registry
        self._init_services()
        
        # Load saved credentials
        self._load_credentials()
        
        # Assign drive letters
        self._assign_drive_letters()
        
        # HTTP server
        self._server = None
        self._server_thread = None
    
    def _init_apps(self):
        """Initialize ButterflyFx app connections from registry"""
        for app_id, config in APP_REGISTRY.items():
            self._apps[app_id] = AppConnection(
                app_id=app_id,
                name=config["name"],
                app_type=config["app_type"],
                icon=config["icon"],
                color=config["color"],
                port=config.get("default_port") or 0,
                capabilities=config.get("capabilities", []),
            )
        
        # =====================================================================
        # CONNECTED AI - Mark any active AI assistants as connected
        # The AI assistant (e.g., Claude) that is currently helping with
        # development is PART OF THE SYSTEM - it has access to all knowledge
        # ingested into the kernel and can read/write to substrates.
        # =====================================================================
        self._register_connected_ai()
    
    def _register_connected_ai(self):
        """
        Register the connected AI assistant as part of the system.
        
        When an AI (like Claude via VS Code/Copilot) is actively connected
        to the workspace, it becomes part of DimensionOS:
        - It can access all ingested knowledge
        - It can read from any connected service's data
        - It can help navigate the dimensional structure
        - It participates in the SRL namespace
        """
        # Check for active AI connections
        active_ai_ids = ["claude", "copilot"]  # Currently connected AIs
        
        for ai_id in active_ai_ids:
            if ai_id in self._apps:
                app = self._apps[ai_id]
                config = APP_REGISTRY.get(ai_id, {})
                
                # Mark as connected if it's an active connection type
                if config.get("connection_type") == "active":
                    app.status = ServiceStatus.CONNECTED
                    app.connected_at = datetime.now().isoformat()
                    app.last_ping = datetime.now().isoformat()
                    
                    self._stats["connected_apps"] += 1
                    
                    # Ingest AI connection info into kernel
                    ai_data = {
                        "app_id": ai_id,
                        "name": app.name,
                        "capabilities": app.capabilities,
                        "connected_at": app.connected_at,
                        "connection_type": "active",
                        "knowledge_access": config.get("knowledge_access", True),
                        "can_modify": config.get("can_modify", True),
                        "role": "assistant",
                        "description": config.get("description", ""),
                    }
                    
                    # AI connections go to spiral 100 (special AI spiral)
                    self.substrate.ingest_keyed(100, 6, ai_id, ai_data)
                    self._stats["kernel_ingestions"] += 1
    
    def get_connected_ai(self) -> List[Dict]:
        """Get all currently connected AI assistants"""
        return [
            app.to_dict() for app in self._apps.values()
            if app.app_type == "ai" and app.status == ServiceStatus.CONNECTED
        ]
    
    def ai_ingest_knowledge(self, knowledge: Dict, source: str = "claude") -> Dict:
        """
        Ingest knowledge from a connected AI into the kernel.
        
        When an AI learns something or generates insights, it can
        feed that back into the system for persistence.
        
        Args:
            knowledge: Dict with knowledge to ingest
            source: Which AI is providing the knowledge
        
        Returns:
            Ingestion result with coordinates
        """
        if source not in self._apps or self._apps[source].status != ServiceStatus.CONNECTED:
            return {"success": False, "error": f"AI {source} not connected"}
        
        # AI knowledge goes to spiral 101
        coord = self.substrate.ingest_keyed(
            101, 
            knowledge.get("level", 5), 
            f"{source}.{datetime.now().timestamp()}", 
            knowledge
        )
        
        self._stats["kernel_ingestions"] += 1
        
        return {
            "success": True,
            "coordinate": coord,
            "source": source,
            "timestamp": datetime.now().isoformat(),
        }
    
    def ai_query_knowledge(self, spiral: int = None, level: int = None, 
                           key_pattern: str = None) -> List[Dict]:
        """
        Query knowledge from the kernel for AI consumption.
        
        Connected AIs can query all ingested data to enhance their
        understanding and responses.
        """
        results = []
        
        # If specific spiral/level provided
        if spiral is not None and level is not None:
            if key_pattern:
                # Get keyed data matching pattern
                for k, v in self.substrate._ingested_keyed.items():
                    if k[0] == spiral and k[1] == level and key_pattern in str(k[2]):
                        results.append({
                            "spiral": k[0],
                            "level": k[1],
                            "key": k[2],
                            "data": v,
                        })
            else:
                data = self.substrate.extract(spiral, level)
                if data:
                    results.append({
                        "spiral": spiral,
                        "level": level,
                        "data": data,
                    })
        else:
            # Return summary of what's available
            for k, v in list(self.substrate._ingested.items())[:100]:
                results.append({
                    "spiral": k[0],
                    "level": k[1],
                    "data_type": type(v).__name__,
                })
        
        return results
    
    def _init_services(self):
        """Initialize all services from registry"""
        for service_id, config in SERVICE_REGISTRY.items():
            self._services[service_id] = ServiceConnection(
                service_id=service_id,
                name=config["name"],
                category=config["category"],
                icon=config["icon"],
                color=config["color"],
                auth_type=config["auth_type"],
                drive_letter=config.get("drive_letter"),
                srl_base=config.get("srl_template"),
                substrates=config.get("substrates", []),
            )
    
    def _load_credentials(self):
        """Load saved credentials from file"""
        try:
            if CREDENTIALS_PATH.exists():
                with open(CREDENTIALS_PATH, "r") as f:
                    encrypted_creds = json.load(f)
                    # In production, decrypt here
                    self._credentials = encrypted_creds
                    
                    # Restore connection states
                    for service_id, creds in self._credentials.items():
                        if service_id in self._services:
                            self._services[service_id].credentials = creds
                            self._services[service_id].status = ServiceStatus.CONNECTED
                            self._stats["connected_services"] += 1
        except Exception as e:
            print(f"Warning: Could not load credentials: {e}")
    
    def _save_credentials(self):
        """Save credentials to file"""
        try:
            CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
            # In production, encrypt here
            with open(CREDENTIALS_PATH, "w") as f:
                json.dump(self._credentials, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save credentials: {e}")
    
    def _assign_drive_letters(self):
        """Assign drive letters to connected services"""
        used_letters = set()
        
        # First pass: use predefined letters
        for service_id, service in self._services.items():
            if service.drive_letter and service.status == ServiceStatus.CONNECTED:
                used_letters.add(service.drive_letter)
                self._drive_assignments[service.drive_letter] = service_id
        
        # Second pass: assign remaining letters to connected services
        available_letters = [chr(c) for c in range(ord('F'), ord('Z'))]
        for service_id, service in self._services.items():
            if service.status == ServiceStatus.CONNECTED and not service.drive_letter:
                for letter in available_letters:
                    if letter not in used_letters:
                        service.drive_letter = letter
                        used_letters.add(letter)
                        self._drive_assignments[letter] = service_id
                        break
    
    # =========================================================================
    # SERVICE CONNECTION METHODS
    # =========================================================================
    
    def connect_service(self, service_id: str, credentials: Dict[str, str]) -> Dict:
        """Connect to a service with provided credentials"""
        if service_id not in self._services:
            return {"success": False, "error": f"Unknown service: {service_id}"}
        
        service = self._services[service_id]
        config = SERVICE_REGISTRY.get(service_id, {})
        
        # Validate required fields
        wizard_fields = config.get("wizard_fields", [])
        for field_info in wizard_fields:
            if field_info.get("required") and not credentials.get(field_info["name"]):
                return {"success": False, "error": f"Missing required field: {field_info['label']}"}
        
        # Store credentials
        service.credentials = credentials
        service.status = ServiceStatus.PENDING
        
        # Test connection (service-specific logic would go here)
        try:
            # For now, mark as connected
            service.status = ServiceStatus.CONNECTED
            service.last_connected = datetime.now().isoformat()
            
            # Save credentials
            self._credentials[service_id] = credentials
            self._save_credentials()
            
            # Assign drive letter if needed
            self._assign_drive_letters()
            
            # Generate SRLs for the service
            self._generate_srls(service_id)
            
            self._stats["connected_services"] += 1
            
            return {
                "success": True,
                "service_id": service_id,
                "name": service.name,
                "status": service.status,
                "drive_letter": service.drive_letter,
            }
        except Exception as e:
            service.status = ServiceStatus.ERROR
            service.error_message = str(e)
            return {"success": False, "error": str(e)}
    
    def disconnect_service(self, service_id: str) -> Dict:
        """Disconnect from a service"""
        if service_id not in self._services:
            return {"success": False, "error": f"Unknown service: {service_id}"}
        
        service = self._services[service_id]
        
        # Clear credentials
        service.credentials = {}
        service.status = ServiceStatus.DISCONNECTED
        
        # Remove from saved credentials
        if service_id in self._credentials:
            del self._credentials[service_id]
            self._save_credentials()
        
        # Remove SRLs
        self._srls = {k: v for k, v in self._srls.items() if v.service_id != service_id}
        
        # Clear drive letter
        if service.drive_letter in self._drive_assignments:
            del self._drive_assignments[service.drive_letter]
        service.drive_letter = None
        
        self._stats["connected_services"] = max(0, self._stats["connected_services"] - 1)
        
        return {"success": True, "service_id": service_id}
    
    def _generate_srls(self, service_id: str):
        """Generate SRLs for a service's substrates"""
        service = self._services.get(service_id)
        config = SERVICE_REGISTRY.get(service_id, {})
        
        if not service or not config:
            return
        
        srl_template = config.get("srl_template", f"srl://{service_id}/{{path}}")
        
        # Generate SRL for each substrate type
        for substrate_type in service.substrates:
            srl_uri = srl_template.replace("{path}", substrate_type)
            srl = SRL(
                uri=srl_uri,
                service_id=service_id,
                substrate_type=substrate_type,
                path=f"/{substrate_type}",
                schema={},
                metadata={"generated": datetime.now().isoformat()},
            )
            self._srls[srl_uri] = srl
            self._stats["srls_generated"] += 1
        
        # KERNEL INGESTION: Ingest service metadata into the manifold
        self._ingest_service_to_kernel(service_id)
    
    # =========================================================================
    # KERNEL INTEGRATION - Services become part of the system
    # =========================================================================
    
    def _ingest_service_to_kernel(self, service_id: str):
        """
        Ingest a connected service into the kernel's substrate.
        
        Once ingested, the service's data becomes part of DimensionOS:
        - Retrieved in O(1) via spiral/level coordinates
        - Accessible by AI assistants
        - Queryable through the substrate API
        """
        service = self._services.get(service_id)
        config = SERVICE_REGISTRY.get(service_id, {})
        
        if not service:
            return
        
        # Determine spiral based on category
        category_spirals = {
            "cloud_storage": 0,
            "email": 1,
            "database": 2,
            "development": 3,
            "ai": 4,
            "social": 5,
            "music": 6,
            "feeds": 7,
            "shopping": 8,
            "productivity": 9,
            "local": 10,
            "api": 11,
            "entertainment": 12,
            "reference": 13,
            "images": 14,
            "finance": 15,
            "weather": 16,
            "geography": 17,
            "academic": 18,
            "games": 19,
            "government": 20,
            "recipes": 21,
            "crafts": 22,
            "ebooks": 23,
            "knowledge": 24,
        }
        
        spiral = category_spirals.get(service.category, 0)
        
        # Ingest service metadata at level 6 (WHOLE)
        service_data = {
            "service_id": service_id,
            "name": service.name,
            "category": service.category,
            "icon": service.icon,
            "color": service.color,
            "auth_type": service.auth_type,
            "substrates": service.substrates,
            "srl_base": service.srl_base,
            "drive_letter": service.drive_letter,
            "connected_at": service.last_connected,
            "docs_url": config.get("docs_url"),
        }
        
        self.substrate.ingest_keyed(spiral, 6, service_id, service_data)
        
        # Ingest substrates at level 5 (categories of data)
        for idx, sub_type in enumerate(service.substrates):
            substrate_info = {
                "service_id": service_id,
                "substrate_type": sub_type,
                "srl": f"{service.srl_base}/{sub_type}" if service.srl_base else None,
            }
            self.substrate.ingest_keyed(spiral, 5, f"{service_id}.{sub_type}", substrate_info)
        
        self._stats["kernel_ingestions"] += 1
        
    def ingest_data(self, service_id: str, data: Any, level: int = 4, key: str = None) -> Dict:
        """
        Ingest external data from a connected service into the kernel.
        
        Args:
            service_id: Which service the data is from
            data: The data to ingest (any type)
            level: Which level to ingest at (0-6)
            key: Optional key for keyed storage
        
        Returns:
            Dict with ingestion result
        """
        service = self._services.get(service_id)
        if not service or service.status != ServiceStatus.CONNECTED:
            return {"success": False, "error": f"Service {service_id} not connected"}
        
        # Get spiral from category
        category_spirals = {
            "cloud_storage": 0, "email": 1, "database": 2, "development": 3,
            "ai": 4, "social": 5, "music": 6, "feeds": 7, "shopping": 8,
            "productivity": 9, "local": 10, "api": 11, "entertainment": 12,
            "reference": 13, "images": 14, "finance": 15, "weather": 16,
            "geography": 17, "academic": 18, "games": 19, "government": 20,
            "recipes": 21, "crafts": 22, "ebooks": 23, "knowledge": 24,
        }
        spiral = category_spirals.get(service.category, 0)
        
        # Ingest
        if key:
            coord = self.substrate.ingest_keyed(spiral, level, key, data)
        else:
            coord = self.substrate.ingest(spiral, level, data)
        
        self._stats["kernel_ingestions"] += 1
        self._stats["total_items"] += 1
        
        return {
            "success": True,
            "coordinate": coord,
            "spiral": spiral,
            "level": level,
            "service_id": service_id,
        }
    
    def extract_data(self, spiral: int, level: int, key: str = None) -> Any:
        """
        Extract data from the kernel's substrate.
        
        O(1) retrieval from any coordinate.
        """
        if key:
            return self.substrate.extract_keyed(spiral, level, key)
        return self.substrate.extract(spiral, level)
    
    def get_kernel_stats(self) -> Dict:
        """Get kernel/substrate statistics"""
        return {
            "ingestion_count": self.substrate._ingestion_count,
            "extraction_count": self.substrate._extraction_count,
            "total_ingested": len(self.substrate._ingested) + len(self.substrate._ingested_keyed),
            "spirals_used": len(set(k[0] for k in self.substrate._ingested.keys())),
        }
    
    # =========================================================================
    # APP CONNECTION - Connect to ButterflyFx applications
    # =========================================================================
    
    def connect_app(self, app_id: str, host: str = "localhost", port: int = None) -> Dict:
        """
        Connect to a ButterflyFx application.
        
        Apps are connected via HTTP - we verify the app is running and
        register it for data exchange.
        """
        if app_id not in self._apps:
            if app_id not in APP_REGISTRY:
                return {"success": False, "error": f"Unknown app: {app_id}"}
            # Create new app connection
            config = APP_REGISTRY[app_id]
            self._apps[app_id] = AppConnection(
                app_id=app_id,
                name=config["name"],
                app_type=config["app_type"],
                icon=config["icon"],
                color=config["color"],
                port=port or config.get("default_port", 8765),
                capabilities=config.get("capabilities", []),
            )
        
        app = self._apps[app_id]
        app.host = host
        if port:
            app.port = port
        
        # Try to connect (ping the app's health endpoint)
        try:
            url = f"http://{app.host}:{app.port}/api/health"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
                app.status = ServiceStatus.CONNECTED
                app.connected_at = datetime.now().isoformat()
                app.last_ping = datetime.now().isoformat()
                app.version = data.get("version")
                app.error_message = None
                
                self._stats["connected_apps"] += 1
                
                # Ingest app connection into kernel
                self.substrate.ingest_keyed(100, 6, app_id, app.to_dict())
                
                return {
                    "success": True,
                    "app_id": app_id,
                    "url": app.url,
                    "version": app.version,
                    "capabilities": app.capabilities,
                }
        except Exception as e:
            app.status = ServiceStatus.ERROR
            app.error_message = str(e)
            return {"success": False, "error": str(e)}
    
    def disconnect_app(self, app_id: str) -> Dict:
        """Disconnect from a ButterflyFx application"""
        if app_id not in self._apps:
            return {"success": False, "error": f"Unknown app: {app_id}"}
        
        app = self._apps[app_id]
        app.status = ServiceStatus.DISCONNECTED
        app.connected_at = None
        
        self._stats["connected_apps"] = max(0, self._stats["connected_apps"] - 1)
        
        return {"success": True, "app_id": app_id}
    
    def ping_app(self, app_id: str) -> Dict:
        """Ping a connected app to verify it's still running"""
        if app_id not in self._apps:
            return {"success": False, "error": f"Unknown app: {app_id}"}
        
        app = self._apps[app_id]
        
        try:
            url = f"http://{app.host}:{app.port}/api/health"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=3) as response:
                app.last_ping = datetime.now().isoformat()
                app.status = ServiceStatus.CONNECTED
                return {"success": True, "latency_ms": 0}
        except Exception as e:
            app.status = ServiceStatus.ERROR
            app.error_message = str(e)
            return {"success": False, "error": str(e)}
    
    def get_apps(self) -> List[Dict]:
        """Get all ButterflyFx app connections"""
        return [app.to_dict() for app in self._apps.values()]
    
    def get_connected_apps(self) -> List[Dict]:
        """Get only connected apps"""
        return [app.to_dict() for app in self._apps.values() if app.status == ServiceStatus.CONNECTED]
    
    def send_to_app(self, app_id: str, endpoint: str, data: Dict) -> Dict:
        """
        Send data to a connected ButterflyFx app.
        
        This enables apps to exchange data through the Universal Connector.
        """
        if app_id not in self._apps:
            return {"success": False, "error": f"Unknown app: {app_id}"}
        
        app = self._apps[app_id]
        if app.status != ServiceStatus.CONNECTED:
            return {"success": False, "error": f"App {app_id} not connected"}
        
        try:
            url = f"http://{app.host}:{app.port}{endpoint}"
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
                return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_from_app(self, app_id: str, endpoint: str) -> Dict:
        """Get data from a connected ButterflyFx app"""
        if app_id not in self._apps:
            return {"success": False, "error": f"Unknown app: {app_id}"}
        
        app = self._apps[app_id]
        if app.status != ServiceStatus.CONNECTED:
            return {"success": False, "error": f"App {app_id} not connected"}
        
        try:
            url = f"http://{app.host}:{app.port}{endpoint}"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
                return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # =========================================================================
    # QUERY METHODS
    # =========================================================================
    
    def get_services(self, category: str = None) -> List[Dict]:
        """Get all services, optionally filtered by category"""
        services = self._services.values()
        
        if category:
            services = [s for s in services if s.category == category]
        
        return [s.to_dict() for s in services]
    
    def get_service(self, service_id: str) -> Optional[Dict]:
        """Get a specific service"""
        service = self._services.get(service_id)
        return service.to_dict() if service else None
    
    def get_categories(self) -> List[Dict]:
        """Get all service categories"""
        result = []
        for cat_id, cat_info in SERVICE_CATEGORIES.items():
            services = [s for s in self._services.values() if s.category == cat_id]
            connected = sum(1 for s in services if s.status == ServiceStatus.CONNECTED)
            result.append({
                "id": cat_id,
                **cat_info,
                "total_services": len(services),
                "connected": connected,
            })
        return result
    
    def get_connected_services(self) -> List[Dict]:
        """Get only connected services"""
        return [s.to_dict() for s in self._services.values() if s.status == ServiceStatus.CONNECTED]
    
    def get_srls(self, service_id: str = None) -> List[Dict]:
        """Get all SRLs, optionally filtered by service"""
        srls = self._srls.values()
        
        if service_id:
            srls = [s for s in srls if s.service_id == service_id]
        
        return [s.to_dict() for s in srls]
    
    def get_wizard(self, service_id: str) -> Optional[Dict]:
        """Get wizard configuration for a service"""
        config = SERVICE_REGISTRY.get(service_id)
        if not config:
            return None
        
        return {
            "service_id": service_id,
            "name": config["name"],
            "icon": config["icon"],
            "color": config["color"],
            "auth_type": config["auth_type"],
            "auth_url": config.get("auth_url"),
            "docs_url": config.get("docs_url"),
            "fields": config.get("wizard_fields", []),
        }
    
    def get_stats(self) -> Dict:
        """Get connector statistics"""
        return {
            **self._stats,
            "categories": len(SERVICE_CATEGORIES),
            "drive_assignments": dict(self._drive_assignments),
        }
    
    # =========================================================================
    # HTTP SERVER
    # =========================================================================
    
    def _create_handler(self):
        """Create HTTP request handler"""
        connector = self
        
        class ConnectorHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass  # Suppress logs
            
            def _send_json(self, data, status=200):
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            
            def _send_html(self, html, status=200):
                self.send_response(status)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode())
            
            def do_OPTIONS(self):
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()
            
            def do_GET(self):
                parsed = urlparse(self.path)
                path = parsed.path
                query = parse_qs(parsed.query)
                
                # API Routes
                if path == "/api/services":
                    category = query.get("category", [None])[0]
                    self._send_json({"services": connector.get_services(category)})
                
                elif path == "/api/categories":
                    self._send_json({"categories": connector.get_categories()})
                
                elif path == "/api/connected":
                    self._send_json({"services": connector.get_connected_services()})
                
                elif path == "/api/srls":
                    service_id = query.get("service", [None])[0]
                    self._send_json({"srls": connector.get_srls(service_id)})
                
                elif path.startswith("/api/wizard/"):
                    service_id = path.split("/")[-1]
                    wizard = connector.get_wizard(service_id)
                    if wizard:
                        self._send_json(wizard)
                    else:
                        self._send_json({"error": "Service not found"}, 404)
                
                elif path.startswith("/api/service/"):
                    service_id = path.split("/")[-1]
                    service = connector.get_service(service_id)
                    if service:
                        self._send_json(service)
                    else:
                        self._send_json({"error": "Service not found"}, 404)
                
                elif path == "/api/stats":
                    self._send_json(connector.get_stats())
                
                elif path == "/api/drives":
                    self._send_json({"drives": connector._drive_assignments})
                
                # =========================================================
                # APP CONNECTION API
                # =========================================================
                elif path == "/api/apps":
                    self._send_json({"apps": connector.get_apps()})
                
                elif path == "/api/apps/connected":
                    self._send_json({"apps": connector.get_connected_apps()})
                
                elif path.startswith("/api/app/"):
                    app_id = path.split("/")[-1]
                    if app_id in connector._apps:
                        self._send_json(connector._apps[app_id].to_dict())
                    else:
                        self._send_json({"error": "App not found"}, 404)
                
                # =========================================================
                # AI CONNECTION API - Connected AI assistants
                # =========================================================
                elif path == "/api/ai/connected":
                    self._send_json({"ai_assistants": connector.get_connected_ai()})
                
                elif path == "/api/ai/capabilities":
                    # Return capabilities of all connected AIs
                    ai_caps = {}
                    for ai in connector.get_connected_ai():
                        ai_caps[ai["app_id"]] = ai.get("capabilities", [])
                    self._send_json({"capabilities": ai_caps})
                
                # =========================================================
                # KERNEL API  
                # =========================================================
                elif path == "/api/kernel/stats":
                    self._send_json(connector.get_kernel_stats())
                
                elif path == "/api/kernel/extract":
                    spiral = int(query.get("spiral", [0])[0])
                    level = int(query.get("level", [6])[0])
                    key = query.get("key", [None])[0]
                    data = connector.extract_data(spiral, level, key)
                    self._send_json({"data": data, "spiral": spiral, "level": level, "key": key})
                
                elif path == "/api/health":
                    self._send_json({
                        "status": "healthy",
                        "service": "universal_connector",
                        "version": "1.0.0",
                        "connected_services": connector._stats.get("connected_services", 0),
                        "connected_apps": connector._stats.get("connected_apps", 0),
                    })
                
                # Web UI
                elif path == "/" or path == "/index.html":
                    self._send_html(connector._render_ui())
                
                else:
                    self._send_json({"error": "Not found"}, 404)
            
            def do_POST(self):
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                
                try:
                    data = json.loads(body) if body else {}
                except:
                    data = {}
                
                parsed = urlparse(self.path)
                path = parsed.path
                
                if path == "/api/connect":
                    service_id = data.get("service_id")
                    credentials = data.get("credentials", {})
                    result = connector.connect_service(service_id, credentials)
                    self._send_json(result)
                
                elif path == "/api/disconnect":
                    service_id = data.get("service_id")
                    result = connector.disconnect_service(service_id)
                    self._send_json(result)
                
                # =========================================================
                # APP CONNECTION API
                # =========================================================
                elif path == "/api/app/connect":
                    app_id = data.get("app_id")
                    host = data.get("host", "localhost")
                    port = data.get("port")
                    result = connector.connect_app(app_id, host, port)
                    self._send_json(result)
                
                elif path == "/api/app/disconnect":
                    app_id = data.get("app_id")
                    result = connector.disconnect_app(app_id)
                    self._send_json(result)
                
                elif path == "/api/app/ping":
                    app_id = data.get("app_id")
                    result = connector.ping_app(app_id)
                    self._send_json(result)
                
                elif path == "/api/app/send":
                    app_id = data.get("app_id")
                    endpoint = data.get("endpoint", "/")
                    payload = data.get("data", {})
                    result = connector.send_to_app(app_id, endpoint, payload)
                    self._send_json(result)
                
                # =========================================================
                # KERNEL API
                # =========================================================
                elif path == "/api/kernel/ingest":
                    service_id = data.get("service_id")
                    ingest_data = data.get("data")
                    level = data.get("level", 4)
                    key = data.get("key")
                    result = connector.ingest_data(service_id, ingest_data, level, key)
                    self._send_json(result)
                
                # =========================================================
                # AI KNOWLEDGE API - Connected AI can ingest/query knowledge
                # =========================================================
                elif path == "/api/ai/ingest":
                    knowledge = data.get("knowledge", {})
                    source = data.get("source", "claude")
                    result = connector.ai_ingest_knowledge(knowledge, source)
                    self._send_json(result)
                
                elif path == "/api/ai/query":
                    spiral = data.get("spiral")
                    level = data.get("level")
                    key_pattern = data.get("key_pattern")
                    results = connector.ai_query_knowledge(spiral, level, key_pattern)
                    self._send_json({"results": results})
                
                else:
                    self._send_json({"error": "Not found"}, 404)
        
        return ConnectorHandler
    
    def _render_ui(self) -> str:
        """Render the Universal Connector web UI"""
        categories_html = ""
        for cat_id, cat_info in SERVICE_CATEGORIES.items():
            services = [s for s in self._services.values() if s.category == cat_id]
            
            service_buttons = ""
            for service in services:
                config = SERVICE_REGISTRY.get(service.service_id, {})
                status_dot = ServiceStatus.get_dot(service.status)
                
                service_buttons += f'''
                    <button class="service-btn" 
                            data-service="{service.service_id}"
                            onclick="openWizard('{service.service_id}')"
                            style="border-color: {service.color}">
                        <span class="service-icon">{service.icon}</span>
                        <span class="service-name">{service.name}</span>
                        <span class="status-dot">{status_dot}</span>
                    </button>
                '''
            
            categories_html += f'''
                <div class="category-section">
                    <h3>{cat_info["icon"]} {cat_info["name"]}</h3>
                    <div class="services-grid">
                        {service_buttons}
                    </div>
                </div>
            '''
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🦋 Universal Connector</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #e6e6e6;
            min-height: 100vh;
        }}
        
        .header {{
            background: rgba(0,0,0,0.3);
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        .header h1 {{
            font-size: 2rem;
            font-weight: 300;
        }}
        
        .header .subtitle {{
            color: #888;
            margin-top: 5px;
        }}
        
        .stats-bar {{
            display: flex;
            justify-content: center;
            gap: 30px;
            padding: 15px;
            background: rgba(0,0,0,0.2);
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #00d4ff;
        }}
        
        .stat-label {{
            font-size: 0.8rem;
            color: #888;
        }}
        
        .main-content {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px;
        }}
        
        .category-section {{
            margin-bottom: 40px;
        }}
        
        .category-section h3 {{
            font-size: 1.3rem;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        .services-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 15px;
        }}
        
        .service-btn {{
            background: rgba(255,255,255,0.05);
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 12px;
            padding: 15px 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            color: #e6e6e6;
            position: relative;
        }}
        
        .service-btn:hover {{
            background: rgba(255,255,255,0.1);
            transform: translateY(-3px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
        }}
        
        .service-icon {{
            font-size: 2rem;
        }}
        
        .service-name {{
            font-size: 0.85rem;
            text-align: center;
        }}
        
        .status-dot {{
            position: absolute;
            top: 8px;
            right: 8px;
            font-size: 0.7rem;
        }}
        
        /* Modal */
        .modal-overlay {{
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.7);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }}
        
        .modal-overlay.active {{
            display: flex;
        }}
        
        .modal {{
            background: #1e2a3a;
            border-radius: 16px;
            padding: 30px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }}
        
        .modal-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        .modal-icon {{
            font-size: 2.5rem;
        }}
        
        .modal-title {{
            font-size: 1.5rem;
        }}
        
        .modal-close {{
            margin-left: auto;
            background: none;
            border: none;
            color: #888;
            font-size: 1.5rem;
            cursor: pointer;
        }}
        
        .field-group {{
            margin-bottom: 20px;
        }}
        
        .field-group label {{
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }}
        
        .field-group input, .field-group select {{
            width: 100%;
            padding: 12px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            background: rgba(0,0,0,0.2);
            color: #e6e6e6;
            font-size: 1rem;
        }}
        
        .field-group input:focus {{
            outline: none;
            border-color: #00d4ff;
        }}
        
        .auth-link {{
            display: inline-block;
            margin-bottom: 15px;
            color: #00d4ff;
            text-decoration: none;
        }}
        
        .auth-link:hover {{
            text-decoration: underline;
        }}
        
        .btn-primary {{
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,212,255,0.3);
        }}
        
        .btn-disconnect {{
            background: linear-gradient(135deg, #ff4444, #cc0000);
            margin-top: 10px;
        }}
        
        .connection-status {{
            text-align: center;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
        }}
        
        .connection-status.connected {{
            background: rgba(0,255,0,0.1);
            border: 1px solid rgba(0,255,0,0.3);
        }}
        
        .connection-status.disconnected {{
            background: rgba(255,0,0,0.1);
            border: 1px solid rgba(255,0,0,0.3);
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🦋 Universal Connector</h1>
        <div class="subtitle">Connect to Anything, Dimensionally</div>
    </div>
    
    <div class="stats-bar">
        <div class="stat">
            <div class="stat-value" id="stat-total">{len(SERVICE_REGISTRY)}</div>
            <div class="stat-label">Services</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="stat-connected">{self._stats["connected_services"]}</div>
            <div class="stat-label">Connected</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="stat-srls">{self._stats["srls_generated"]}</div>
            <div class="stat-label">SRLs</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="stat-drives">{len(self._drive_assignments)}</div>
            <div class="stat-label">Drives</div>
        </div>
    </div>
    
    <div class="main-content">
        {categories_html}
    </div>
    
    <!-- Connection Wizard Modal -->
    <div class="modal-overlay" id="wizard-modal">
        <div class="modal">
            <div class="modal-header">
                <span class="modal-icon" id="wizard-icon">🔌</span>
                <span class="modal-title" id="wizard-title">Connect Service</span>
                <button class="modal-close" onclick="closeWizard()">&times;</button>
            </div>
            <div id="wizard-content">
                <!-- Wizard content loaded dynamically -->
            </div>
        </div>
    </div>
    
    <script>
        let currentService = null;
        
        async function openWizard(serviceId) {{
            currentService = serviceId;
            const modal = document.getElementById('wizard-modal');
            const content = document.getElementById('wizard-content');
            
            // Fetch wizard config
            const response = await fetch(`/api/wizard/${{serviceId}}`);
            const wizard = await response.json();
            
            document.getElementById('wizard-icon').textContent = wizard.icon;
            document.getElementById('wizard-title').textContent = wizard.name;
            
            // Check current status
            const statusResponse = await fetch(`/api/service/${{serviceId}}`);
            const service = await statusResponse.json();
            
            let html = '';
            
            if (service.status === 'connected') {{
                html = `
                    <div class="connection-status connected">
                        <div style="font-size: 2rem">🟢</div>
                        <div style="margin-top: 10px; font-weight: bold">Connected</div>
                        ${{service.drive_letter ? `<div style="color: #888">Drive: ${{service.drive_letter}}:</div>` : ''}}
                    </div>
                    <button class="btn-primary btn-disconnect" onclick="disconnectService()">Disconnect</button>
                `;
            }} else {{
                // Build form fields
                let fieldsHtml = '';
                for (const field of wizard.fields || []) {{
                    const required = field.required ? 'required' : '';
                    const placeholder = field.placeholder || '';
                    const defaultVal = field.default || '';
                    
                    if (field.type === 'select') {{
                        const options = (field.options || []).map(o => `<option value="${{o}}">${{o}}</option>`).join('');
                        fieldsHtml += `
                            <div class="field-group">
                                <label>${{field.label}}${{field.required ? ' *' : ''}}</label>
                                <select name="${{field.name}}" ${{required}}>
                                    ${{options}}
                                </select>
                            </div>
                        `;
                    }} else if (field.type === 'checkbox') {{
                        fieldsHtml += `
                            <div class="field-group">
                                <label>
                                    <input type="checkbox" name="${{field.name}}" ${{field.default ? 'checked' : ''}}>
                                    ${{field.label}}
                                </label>
                            </div>
                        `;
                    }} else {{
                        fieldsHtml += `
                            <div class="field-group">
                                <label>${{field.label}}${{field.required ? ' *' : ''}}</label>
                                <input type="${{field.type || 'text'}}" 
                                       name="${{field.name}}" 
                                       placeholder="${{placeholder}}"
                                       value="${{defaultVal}}"
                                       ${{required}}>
                            </div>
                        `;
                    }}
                }}
                
                const authLink = wizard.auth_url ? 
                    `<a href="${{wizard.auth_url}}" target="_blank" class="auth-link">🔑 Get API credentials</a>` : '';
                const docsLink = wizard.docs_url ? 
                    `<a href="${{wizard.docs_url}}" target="_blank" class="auth-link" style="margin-left: 15px">📚 Documentation</a>` : '';
                
                html = `
                    <form id="wizard-form" onsubmit="submitWizard(event)">
                        ${{authLink}}${{docsLink}}
                        ${{fieldsHtml}}
                        <button type="submit" class="btn-primary">Connect</button>
                    </form>
                `;
            }}
            
            content.innerHTML = html;
            modal.classList.add('active');
        }}
        
        function closeWizard() {{
            document.getElementById('wizard-modal').classList.remove('active');
            currentService = null;
        }}
        
        async function submitWizard(event) {{
            event.preventDefault();
            
            const form = event.target;
            const credentials = {{}};
            
            for (const input of form.querySelectorAll('input, select')) {{
                if (input.type === 'checkbox') {{
                    credentials[input.name] = input.checked;
                }} else {{
                    credentials[input.name] = input.value;
                }}
            }}
            
            const response = await fetch('/api/connect', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{
                    service_id: currentService,
                    credentials: credentials
                }})
            }});
            
            const result = await response.json();
            
            if (result.success) {{
                closeWizard();
                location.reload();  // Refresh to show updated status
            }} else {{
                alert('Connection failed: ' + result.error);
            }}
        }}
        
        async function disconnectService() {{
            const response = await fetch('/api/disconnect', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ service_id: currentService }})
            }});
            
            const result = await response.json();
            
            if (result.success) {{
                closeWizard();
                location.reload();
            }} else {{
                alert('Disconnect failed: ' + result.error);
            }}
        }}
        
        // Close modal on outside click
        document.getElementById('wizard-modal').addEventListener('click', (e) => {{
            if (e.target.id === 'wizard-modal') {{
                closeWizard();
            }}
        }});
    </script>
</body>
</html>'''
    
    def start(self, open_browser: bool = True):
        """Start the Universal Connector server"""
        Handler = self._create_handler()
        
        self._server = socketserver.TCPServer(("", self.port), Handler)
        self._server.allow_reuse_address = True
        
        self._server_thread = threading.Thread(target=self._server.serve_forever)
        self._server_thread.daemon = True
        self._server_thread.start()
        
        print(f"🦋 Universal Connector running at http://localhost:{self.port}")
        
        if open_browser:
            webbrowser.open(f"http://localhost:{self.port}")
    
    def stop(self):
        """Stop the server"""
        if self._server:
            self._server.shutdown()
            print("Universal Connector stopped")
    
    def run_forever(self):
        """Run the server blocking"""
        Handler = self._create_handler()
        
        with socketserver.TCPServer(("", self.port), Handler) as server:
            server.allow_reuse_address = True
            print(f"🦋 Universal Connector running at http://localhost:{self.port}")
            server.serve_forever()


def main():
    """Run Universal Connector as standalone application"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Universal Connector")
    parser.add_argument("--port", type=int, default=8766, help="Server port")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser")
    parser.add_argument("--daemon", action="store_true", help="Run as background daemon")
    args = parser.parse_args()
    
    connector = UniversalConnectorService(port=args.port)
    
    if args.daemon:
        connector.start(open_browser=False)
        print("Running as daemon. Press Ctrl+C to stop.")
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            connector.stop()
    else:
        try:
            if not args.no_browser:
                import threading
                threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{args.port}")).start()
            connector.run_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")


if __name__ == "__main__":
    main()
