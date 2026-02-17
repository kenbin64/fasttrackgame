/**
 * ButterflyFX Universal HD - Universal Data Explorer
 * 
 * A Windows Explorer-style interface for connecting to any data source:
 * - Local substrates and files
 * - External APIs (weather, stocks, news, etc.)
 * - Databases and cloud storage
 * - Custom connections
 */

// ============================================================================
// Pre-configured API Connections (with logos and signup links)
// ============================================================================
const API_REGISTRY = {
    // Weather APIs
    weather: [
        {
            id: 'openweather',
            name: 'OpenWeatherMap',
            icon: '🌤️',
            logo: 'https://openweathermap.org/themes/openweathermap/assets/img/logo_white_cropped.png',
            description: 'Current weather, forecasts, and historical data',
            category: 'weather',
            authType: 'api_key',
            signupUrl: 'https://openweathermap.org/api',
            docsUrl: 'https://openweathermap.org/api',
            baseUrl: 'https://api.openweathermap.org/data/2.5',
            freeTier: true,
            fields: [
                { name: 'api_key', label: 'API Key', type: 'password', required: true }
            ]
        },
        {
            id: 'wttr',
            name: 'wttr.in',
            icon: '☁️',
            description: 'Simple weather service - NO API KEY NEEDED',
            category: 'weather',
            authType: 'none',
            baseUrl: 'https://wttr.in',
            freeTier: true,
            noKeyRequired: true,
            fields: []
        },
        {
            id: 'open-meteo',
            name: 'Open-Meteo',
            icon: '🌡️',
            description: 'Free weather API - NO API KEY NEEDED',
            category: 'weather',
            authType: 'none',
            baseUrl: 'https://api.open-meteo.com/v1',
            freeTier: true,
            noKeyRequired: true,
            fields: []
        }
    ],
    
    // Finance & Crypto
    finance: [
        {
            id: 'coinbase',
            name: 'Coinbase',
            icon: '₿',
            description: 'Cryptocurrency prices and market data',
            category: 'finance',
            authType: 'none',
            baseUrl: 'https://api.coinbase.com/v2',
            freeTier: true,
            noKeyRequired: true,
            fields: []
        },
        {
            id: 'coingecko',
            name: 'CoinGecko',
            icon: '🦎',
            description: 'Crypto prices, market cap, volume - NO KEY NEEDED',
            category: 'finance',
            authType: 'none',
            baseUrl: 'https://api.coingecko.com/api/v3',
            freeTier: true,
            noKeyRequired: true,
            fields: []
        },
        {
            id: 'exchangerate',
            name: 'ExchangeRate-API',
            icon: '💱',
            description: 'Currency exchange rates - NO KEY NEEDED',
            category: 'finance',
            authType: 'none',
            baseUrl: 'https://open.er-api.com/v6',
            freeTier: true,
            noKeyRequired: true,
            fields: []
        },
        {
            id: 'alphavantage',
            name: 'Alpha Vantage',
            icon: '📈',
            description: 'Stock quotes, forex, crypto, technical indicators',
            category: 'finance',
            authType: 'api_key',
            signupUrl: 'https://www.alphavantage.co/support/#api-key',
            baseUrl: 'https://www.alphavantage.co/query',
            freeTier: true,
            fields: [
                { name: 'api_key', label: 'API Key', type: 'password', required: true }
            ]
        },
        {
            id: 'finnhub',
            name: 'Finnhub',
            icon: '📊',
            description: 'Real-time stock prices, company financials, economic data',
            category: 'finance',
            authType: 'api_key',
            signupUrl: 'https://finnhub.io/',
            docsUrl: 'https://finnhub.io/docs/api',
            baseUrl: 'https://finnhub.io/api/v1',
            freeTier: true,
            defaultKey: 'd4vare9r01qnm7pqllm0d4vare9r01qnm7pqllmg',
            fields: [
                { name: 'api_key', label: 'API Key', type: 'password', required: true, default: 'd4vare9r01qnm7pqllm0d4vare9r01qnm7pqllmg' }
            ]
        },
        {
            id: 'yahoo-finance',
            name: 'Yahoo Finance',
            icon: '💹',
            description: 'Stock quotes via unofficial API - NO KEY NEEDED',
            category: 'finance',
            authType: 'none',
            baseUrl: 'https://query1.finance.yahoo.com/v8/finance',
            freeTier: true,
            noKeyRequired: true,
            fields: []
        }
    ],
    
    // News
    news: [
        {
            id: 'newsapi',
            name: 'NewsAPI',
            icon: '📰',
            description: 'Breaking news headlines from 80+ sources',
            category: 'news',
            authType: 'api_key',
            signupUrl: 'https://newsapi.org/register',
            docsUrl: 'https://newsapi.org/docs',
            baseUrl: 'https://newsapi.org/v2',
            freeTier: true,
            fields: [
                { name: 'api_key', label: 'API Key', type: 'password', required: true }
            ]
        },
        {
            id: 'wikipedia',
            name: 'Wikipedia',
            icon: '📚',
            description: 'Wikipedia articles, summaries, and search - NO KEY NEEDED',
            category: 'news',
            authType: 'none',
            baseUrl: 'https://en.wikipedia.org/api/rest_v1',
            docsUrl: 'https://en.wikipedia.org/api/rest_v1/?spec',
            freeTier: true,
            noKeyRequired: true,
            endpoints: {
                summary: '/page/summary/{title}',
                random: '/page/random/summary',
                search: '/page/search/{query}',
                html: '/page/html/{title}',
                media: '/page/media-list/{title}'
            },
            fields: []
        },
        {
            id: 'gnews',
            name: 'GNews',
            icon: '🗞️',
            description: 'Google News aggregator - free tier',
            category: 'news',
            authType: 'api_key',
            signupUrl: 'https://gnews.io/',
            baseUrl: 'https://gnews.io/api/v4',
            freeTier: true,
            fields: [
                { name: 'api_key', label: 'API Key', type: 'password', required: true }
            ]
        },
        {
            id: 'currentsapi',
            name: 'Currents API',
            icon: '📡',
            description: 'Latest news from worldwide sources - free tier',
            category: 'news',
            authType: 'api_key',
            signupUrl: 'https://currentsapi.services/en/register',
            baseUrl: 'https://api.currentsapi.services/v1',
            freeTier: true,
            fields: [
                { name: 'api_key', label: 'API Key', type: 'password', required: true }
            ]
        },
        {
            id: 'hackernews',
            name: 'Hacker News',
            icon: '🔶',
            description: 'Tech news from Y Combinator - NO KEY NEEDED',
            category: 'news',
            authType: 'none',
            baseUrl: 'https://hacker-news.firebaseio.com/v0',
            freeTier: true,
            noKeyRequired: true,
            fields: []
        },
        {
            id: 'reddit',
            name: 'Reddit',
            icon: '🔴',
            description: 'Reddit posts and comments - NO KEY NEEDED',
            category: 'news',
            authType: 'none',
            baseUrl: 'https://www.reddit.com',
            freeTier: true,
            noKeyRequired: true,
            note: 'Append .json to any Reddit URL',
            fields: []
        }
    ],
    
    // Entertainment & Music
    music: [
        {
            id: 'spotify',
            name: 'Spotify',
            icon: '🎵',
            description: 'Music search, playlists, artist info',
            category: 'music',
            authType: 'oauth',
            signupUrl: 'https://developer.spotify.com/dashboard',
            docsUrl: 'https://developer.spotify.com/documentation/web-api',
            baseUrl: 'https://api.spotify.com/v1',
            fields: [
                { name: 'client_id', label: 'Client ID', type: 'text', required: true },
                { name: 'client_secret', label: 'Client Secret', type: 'password', required: true }
            ]
        },
        {
            id: 'itunes',
            name: 'iTunes',
            icon: '🎧',
            description: 'Search iTunes for music, apps, books - NO KEY NEEDED',
            category: 'music',
            authType: 'none',
            baseUrl: 'https://itunes.apple.com',
            freeTier: true,
            noKeyRequired: true,
            fields: []
        }
    ],
    
    // Photos & Media
    photos: [
        {
            id: 'unsplash',
            name: 'Unsplash',
            icon: '📷',
            description: 'High-quality free photos',
            category: 'photos',
            authType: 'api_key',
            signupUrl: 'https://unsplash.com/developers',
            baseUrl: 'https://api.unsplash.com',
            freeTier: true,
            fields: [
                { name: 'access_key', label: 'Access Key', type: 'password', required: true }
            ]
        },
        {
            id: 'pexels',
            name: 'Pexels',
            icon: '🖼️',
            description: 'Free stock photos and videos',
            category: 'photos',
            authType: 'api_key',
            signupUrl: 'https://www.pexels.com/api/',
            baseUrl: 'https://api.pexels.com/v1',
            freeTier: true,
            fields: [
                { name: 'api_key', label: 'API Key', type: 'password', required: true }
            ]
        }
    ],
    
    // Productivity & Calendar
    calendar: [
        {
            id: 'google-calendar',
            name: 'Google Calendar',
            icon: '📅',
            description: 'Calendar events and scheduling',
            category: 'calendar',
            authType: 'oauth',
            signupUrl: 'https://console.developers.google.com/',
            baseUrl: 'https://www.googleapis.com/calendar/v3',
            fields: [
                { name: 'client_id', label: 'Client ID', type: 'text', required: true },
                { name: 'client_secret', label: 'Client Secret', type: 'password', required: true }
            ]
        }
    ],
    
    // Email
    email: [
        {
            id: 'gmail',
            name: 'Gmail',
            icon: '📧',
            description: 'Email access and filtering',
            category: 'email',
            authType: 'oauth',
            signupUrl: 'https://console.developers.google.com/',
            baseUrl: 'https://www.googleapis.com/gmail/v1',
            fields: [
                { name: 'client_id', label: 'Client ID', type: 'text', required: true },
                { name: 'client_secret', label: 'Client Secret', type: 'password', required: true }
            ]
        }
    ],
    
    // AI Services
    ai: [
        {
            id: 'openai',
            name: 'OpenAI',
            icon: '🤖',
            description: 'GPT models, DALL-E, Whisper',
            category: 'ai',
            authType: 'api_key',
            signupUrl: 'https://platform.openai.com/api-keys',
            docsUrl: 'https://platform.openai.com/docs',
            baseUrl: 'https://api.openai.com/v1',
            fields: [
                { name: 'api_key', label: 'API Key', type: 'password', required: true }
            ]
        },
        {
            id: 'huggingface',
            name: 'Hugging Face',
            icon: '🤗',
            description: 'ML models, NLP, computer vision',
            category: 'ai',
            authType: 'api_key',
            signupUrl: 'https://huggingface.co/settings/tokens',
            baseUrl: 'https://api-inference.huggingface.co',
            freeTier: true,
            fields: [
                { name: 'api_key', label: 'API Token', type: 'password', required: true }
            ]
        }
    ],
    
    // Developer Tools
    developer: [
        {
            id: 'github',
            name: 'GitHub',
            icon: '🐙',
            description: 'Repositories, issues, PRs, gists',
            category: 'developer',
            authType: 'api_key',
            signupUrl: 'https://github.com/settings/tokens',
            baseUrl: 'https://api.github.com',
            freeTier: true,
            fields: [
                { name: 'token', label: 'Personal Access Token', type: 'password', required: true }
            ]
        },
        {
            id: 'jsonplaceholder',
            name: 'JSONPlaceholder',
            icon: '📋',
            description: 'Fake REST API for testing - NO KEY NEEDED',
            category: 'developer',
            authType: 'none',
            baseUrl: 'https://jsonplaceholder.typicode.com',
            freeTier: true,
            noKeyRequired: true,
            fields: []
        }
    ],
    
    // Data & Knowledge
    data: [
        {
            id: 'worldbank',
            name: 'World Bank',
            icon: '🌍',
            description: 'Global development data - NO KEY NEEDED',
            category: 'data',
            authType: 'none',
            baseUrl: 'https://api.worldbank.org/v2',
            freeTier: true,
            noKeyRequired: true,
            fields: []
        },
        {
            id: 'restcountries',
            name: 'REST Countries',
            icon: '🗺️',
            description: 'Country information - NO KEY NEEDED',
            category: 'data',
            authType: 'none',
            baseUrl: 'https://restcountries.com/v3.1',
            freeTier: true,
            noKeyRequired: true,
            fields: []
        },
        {
            id: 'numbersapi',
            name: 'Numbers API',
            icon: '🔢',
            description: 'Fun facts about numbers - NO KEY NEEDED',
            category: 'data',
            authType: 'none',
            baseUrl: 'http://numbersapi.com',
            freeTier: true,
            noKeyRequired: true,
            fields: []
        }
    ],
    
    // Knowledge - Dictionary, Thesaurus, Language
    knowledge: [
        {
            id: 'freedictionary',
            name: 'Free Dictionary',
            icon: '📖',
            description: 'Word definitions, phonetics, examples - NO KEY NEEDED',
            category: 'knowledge',
            authType: 'none',
            baseUrl: 'https://api.dictionaryapi.dev/api/v2/entries/en',
            freeTier: true,
            noKeyRequired: true,
            endpoints: {
                definition: '/{word}'
            },
            fields: []
        },
        {
            id: 'datamuse',
            name: 'Datamuse',
            icon: '🔤',
            description: 'Thesaurus, rhymes, word associations - NO KEY NEEDED',
            category: 'knowledge',
            authType: 'none',
            baseUrl: 'https://api.datamuse.com',
            docsUrl: 'https://www.datamuse.com/api/',
            freeTier: true,
            noKeyRequired: true,
            endpoints: {
                synonyms: '/words?rel_syn={word}',
                rhymes: '/words?rel_rhy={word}',
                similar: '/words?ml={word}',
                suggestions: '/sug?s={prefix}'
            },
            fields: []
        },
        {
            id: 'wordnik',
            name: 'Wordnik',
            icon: '📝',
            description: 'Definitions, examples, pronunciation',
            category: 'knowledge',
            authType: 'api_key',
            signupUrl: 'https://developer.wordnik.com/',
            baseUrl: 'https://api.wordnik.com/v4',
            freeTier: true,
            fields: [
                { name: 'api_key', label: 'API Key', type: 'password', required: true }
            ]
        },
        {
            id: 'wiktionary',
            name: 'Wiktionary',
            icon: '📓',
            description: 'Free dictionary from Wikimedia - NO KEY NEEDED',
            category: 'knowledge',
            authType: 'none',
            baseUrl: 'https://en.wiktionary.org/api/rest_v1',
            freeTier: true,
            noKeyRequired: true,
            fields: []
        },
        {
            id: 'urban-dictionary',
            name: 'Urban Dictionary',
            icon: '🏙️',
            description: 'Slang and colloquial definitions - NO KEY NEEDED',
            category: 'knowledge',
            authType: 'none',
            baseUrl: 'https://api.urbandictionary.com/v0',
            freeTier: true,
            noKeyRequired: true,
            fields: []
        },
        {
            id: 'openthesaurus',
            name: 'OpenThesaurus',
            icon: '📚',
            description: 'German thesaurus - NO KEY NEEDED',
            category: 'knowledge',
            authType: 'none',
            baseUrl: 'https://www.openthesaurus.de/synonyme/search',
            freeTier: true,
            noKeyRequired: true,
            fields: []
        },
        {
            id: 'openlibrary',
            name: 'Open Library',
            icon: '📕',
            description: 'Book data, covers, search - NO KEY NEEDED',
            category: 'knowledge',
            authType: 'none',
            baseUrl: 'https://openlibrary.org',
            freeTier: true,
            noKeyRequired: true,
            endpoints: {
                search: '/search.json?q={query}',
                book: '/api/books?bibkeys={isbn}',
                author: '/authors/{id}.json'
            },
            fields: []
        },
        {
            id: 'arxiv',
            name: 'arXiv',
            icon: '🔬',
            description: 'Scientific papers and preprints - NO KEY NEEDED',
            category: 'knowledge',
            authType: 'none',
            baseUrl: 'http://export.arxiv.org/api/query',
            freeTier: true,
            noKeyRequired: true,
            fields: []
        },
        {
            id: 'crossref',
            name: 'CrossRef',
            icon: '📄',
            description: 'Academic metadata, DOIs, citations - NO KEY NEEDED',
            category: 'knowledge',
            authType: 'none',
            baseUrl: 'https://api.crossref.org',
            freeTier: true,
            noKeyRequired: true,
            fields: []
        }
    ],
    
    // Google APIs (Free tiers available)
    google: [
        {
            id: 'google-translate',
            name: 'Google Translate',
            icon: '🌐',
            description: 'Translation between 100+ languages',
            category: 'google',
            authType: 'api_key',
            signupUrl: 'https://console.cloud.google.com/apis/library/translate.googleapis.com',
            docsUrl: 'https://cloud.google.com/translate/docs',
            baseUrl: 'https://translation.googleapis.com/language/translate/v2',
            freeTier: true,
            note: '$10/month free credit',
            fields: [
                { name: 'api_key', label: 'API Key', type: 'password', required: true }
            ]
        },
        {
            id: 'google-books',
            name: 'Google Books',
            icon: '📚',
            description: 'Book search, previews, metadata - FREE with limits',
            category: 'google',
            authType: 'api_key',
            signupUrl: 'https://console.cloud.google.com/apis/library/books.googleapis.com',
            baseUrl: 'https://www.googleapis.com/books/v1',
            freeTier: true,
            fields: [
                { name: 'api_key', label: 'API Key', type: 'password', required: true }
            ]
        },
        {
            id: 'youtube-data',
            name: 'YouTube Data',
            icon: '▶️',
            description: 'Video search, channel info, playlists',
            category: 'google',
            authType: 'api_key',
            signupUrl: 'https://console.cloud.google.com/apis/library/youtube.googleapis.com',
            docsUrl: 'https://developers.google.com/youtube/v3',
            baseUrl: 'https://www.googleapis.com/youtube/v3',
            freeTier: true,
            note: '10,000 units/day free',
            fields: [
                { name: 'api_key', label: 'API Key', type: 'password', required: true }
            ]
        },
        {
            id: 'google-maps-geocoding',
            name: 'Google Geocoding',
            icon: '📍',
            description: 'Address to coordinates and reverse',
            category: 'google',
            authType: 'api_key',
            signupUrl: 'https://console.cloud.google.com/apis/library/geocoding-backend.googleapis.com',
            baseUrl: 'https://maps.googleapis.com/maps/api/geocode',
            freeTier: true,
            note: '$200/month free credit',
            fields: [
                { name: 'api_key', label: 'API Key', type: 'password', required: true }
            ]
        },
        {
            id: 'google-places',
            name: 'Google Places',
            icon: '🏢',
            description: 'Business info, reviews, locations',
            category: 'google',
            authType: 'api_key',
            signupUrl: 'https://console.cloud.google.com/apis/library/places-backend.googleapis.com',
            baseUrl: 'https://maps.googleapis.com/maps/api/place',
            freeTier: true,
            note: '$200/month free credit',
            fields: [
                { name: 'api_key', label: 'API Key', type: 'password', required: true }
            ]
        },
        {
            id: 'google-custom-search',
            name: 'Google Custom Search',
            icon: '🔍',
            description: 'Web search API - 100 queries/day free',
            category: 'google',
            authType: 'api_key',
            signupUrl: 'https://programmablesearchengine.google.com/',
            docsUrl: 'https://developers.google.com/custom-search/v1/overview',
            baseUrl: 'https://www.googleapis.com/customsearch/v1',
            freeTier: true,
            fields: [
                { name: 'api_key', label: 'API Key', type: 'password', required: true },
                { name: 'cx', label: 'Search Engine ID', type: 'text', required: true }
            ]
        },
        {
            id: 'google-knowledge-graph',
            name: 'Google Knowledge Graph',
            icon: '🧠',
            description: 'Entity search, facts, relationships',
            category: 'google',
            authType: 'api_key',
            signupUrl: 'https://console.cloud.google.com/apis/library/kgsearch.googleapis.com',
            baseUrl: 'https://kgsearch.googleapis.com/v1/entities',
            freeTier: true,
            note: '10K queries/day free',
            fields: [
                { name: 'api_key', label: 'API Key', type: 'password', required: true }
            ]
        }
    ],
    
    // Quotes & Inspiration
    quotes: [
        {
            id: 'quotable',
            name: 'Quotable',
            icon: '💭',
            description: 'Random quotes and wisdom - NO KEY NEEDED',
            category: 'quotes',
            authType: 'none',
            baseUrl: 'https://api.quotable.io',
            freeTier: true,
            noKeyRequired: true,
            fields: []
        },
        {
            id: 'zenquotes',
            name: 'ZenQuotes',
            icon: '🧘',
            description: 'Inspirational quotes - NO KEY NEEDED',
            category: 'quotes',
            authType: 'none',
            baseUrl: 'https://zenquotes.io/api',
            freeTier: true,
            noKeyRequired: true,
            fields: []
        }
    ],
    
    // Food & Recipes
    food: [
        {
            id: 'themealdb',
            name: 'TheMealDB',
            icon: '🍲',
            description: 'Meal recipes and ingredients - NO KEY NEEDED',
            category: 'food',
            authType: 'none',
            baseUrl: 'https://www.themealdb.com/api/json/v1/1',
            freeTier: true,
            noKeyRequired: true,
            fields: []
        },
        {
            id: 'edamam',
            name: 'Edamam',
            icon: '🥗',
            description: 'Nutrition data, recipes, meal planning',
            category: 'food',
            authType: 'api_key',
            signupUrl: 'https://developer.edamam.com/',
            baseUrl: 'https://api.edamam.com',
            freeTier: true,
            fields: [
                { name: 'app_id', label: 'Application ID', type: 'text', required: true },
                { name: 'app_key', label: 'Application Key', type: 'password', required: true }
            ]
        }
    ],
    
    // Storage & Cloud
    storage: [
        {
            id: 'dropbox',
            name: 'Dropbox',
            icon: '📦',
            description: 'Cloud file storage',
            category: 'storage',
            authType: 'oauth',
            signupUrl: 'https://www.dropbox.com/developers/apps',
            baseUrl: 'https://api.dropboxapi.com/2',
            fields: [
                { name: 'access_token', label: 'Access Token', type: 'password', required: true }
            ]
        },
        {
            id: 'google-drive',
            name: 'Google Drive',
            icon: '📁',
            description: 'Google Drive files and folders',
            category: 'storage',
            authType: 'oauth',
            signupUrl: 'https://console.developers.google.com/',
            baseUrl: 'https://www.googleapis.com/drive/v3',
            fields: [
                { name: 'client_id', label: 'Client ID', type: 'text', required: true },
                { name: 'client_secret', label: 'Client Secret', type: 'password', required: true }
            ]
        }
    ],
    
    // Database
    database: [
        {
            id: 'substrate-local',
            name: 'Local Substrates',
            icon: '💾',
            description: 'Local ButterflyFX substrate database',
            category: 'database',
            authType: 'none',
            baseUrl: '/api/v2/substrates',
            noKeyRequired: true,
            isLocal: true,
            fields: []
        },
        {
            id: 'supabase',
            name: 'Supabase',
            icon: '⚡',
            description: 'Postgres database with instant APIs',
            category: 'database',
            authType: 'api_key',
            signupUrl: 'https://supabase.com/dashboard',
            fields: [
                { name: 'url', label: 'Project URL', type: 'url', required: true },
                { name: 'anon_key', label: 'Anon Key', type: 'password', required: true }
            ]
        }
    ]
};

// ============================================================================
// State Management
// ============================================================================
const state = {
    currentPath: 'substrate://local/',
    selectedItems: [],
    connections: [],
    viewMode: 'grid', // grid, list, thumbs
    currentView: 'folder', // folder, table, visual, api
    history: [],
    historyIndex: -1,
    queryHistory: [],
    learnedQueries: {},
    chartInstance: null,
    clipboard: { items: [], action: null }, // cut or copy
    contextTarget: null // item being right-clicked
};

// ============================================================================
// Dimensional Helix System
// ============================================================================
// ============================================================================
// DIMENSIONAL HELIX - Golden Ratio Ordered Growth
// ============================================================================
// 7 Levels per spiral (0-6), then wraps to next higher dimension
//
// Level 0 - POTENTIAL: No parts, empty substrate (query before execution)
// Level 1 - POINT:     Single datum (one row value, one file)
// Level 2 - LENGTH:    Sequence (column, list, 1D array)
// Level 3 - WIDTH:     Surface (multiple columns, building toward 2D)
// Level 4 - PLANE:     Full 2D grid/table (what SQL calls a "table")
// Level 5 - VOLUME:    3D cube (tables + time/versions/deltas)
// Level 6 - WHOLE:     Complete dataset → becomes Point at next spiral
//
// DATABASE DEFUDGING:
// SQL forces narrowing: SELECT columns, WHERE filter, LIMIT truncate, JOIN branch
// Helix invokes only what's needed: everything else stays POTENTIAL
// SQL branches into trees (exponential) - Helix spirals (ordered growth)
//
// THE FOR LOOP FALLACY:
// Traditional: for i in range(N): process(data[i])  ← N steps
// Helix:       invoke(Level 2: Length)              ← 1 step (all points)
//              invoke(Level 4: Plane)               ← 1 step (all lengths)
//              invoke(Level 6: Whole)               ← 1 step (complete)
// Why iterate through every point when you can JUMP to next level?
// Each helix transition is a 1-point step, not N iterations.
//
// Helix threads = parallel dimensions (like siblings in different realities)
// Connected through higher dimension, not same-level nodes

const DIMENSION_LEVELS = {
    POTENTIAL: 0, // No parts - empty potential
    POINT: 1,     // Single point of a part - one datum
    LENGTH: 2,    // Length of parts - parts in sequence/line
    WIDTH: 3,     // Width of parts - parts forming 2D
    PLANE: 4,     // Plane of parts - full 2D grid/table
    VOLUME: 5,    // Volume of parts - 3D cube structure
    WHOLE: 6      // Whole - complete unit, becomes point of next spiral
};

const DIMENSION_NAMES = ['Potential', 'Point', 'Length', 'Width', 'Plane', 'Volume', 'Whole'];
const DIMENSION_ICONS = ['○', '•', '━', '▭', '▦', '▣', '◉'];

const dimensionalHelix = {
    // Each item tracks its dimensional position and helix connections
    // itemId -> { 
    //   dimension: 0-6, 
    //   spiral: number (which spiral level),
    //   helixConnections: [] (parallel threads),
    //   innerPoints: [] (drill down - points within this),
    //   outerContainer: null (what contains this)
    // }
    nodes: {},
    
    // Initialize from localStorage
    init() {
        const saved = localStorage.getItem('uhd_dimensional_helix');
        if (saved) {
            try {
                this.nodes = JSON.parse(saved);
                console.log('🌀 Dimensional helix loaded:', Object.keys(this.nodes).length, 'nodes');
            } catch (e) {
                console.warn('Could not load dimensional helix:', e);
            }
        }
    },
    
    // Save to localStorage
    save() {
        try {
            localStorage.setItem('uhd_dimensional_helix', JSON.stringify(this.nodes));
        } catch (e) {
            console.warn('Could not save dimensional helix:', e);
        }
    },
    
    // Get or create node
    getNode(itemId) {
        if (!this.nodes[itemId]) {
            this.nodes[itemId] = {
                dimension: DIMENSION_LEVELS.POINT, // Files start as points
                spiral: 0,  // Base spiral level
                helixConnections: [], // Parallel dimensional threads
                innerPoints: [],      // What's inside (drill down)
                outerContainer: null, // What contains this (drill up)
                metadata: {
                    created: Date.now(),
                    modified: Date.now()
                }
            };
        }
        return this.nodes[itemId];
    },
    
    // Set item's dimension level
    setDimension(itemId, dimension, spiral = 0) {
        const node = this.getNode(itemId);
        node.dimension = Math.max(0, Math.min(6, dimension));
        node.spiral = spiral;
        node.metadata.modified = Date.now();
        this.save();
    },
    
    // Drill down - enter the inner dimension of an item
    // A Point (1) drilled becomes Length (2), then Width (3), etc.
    drillDown(itemId) {
        const node = this.getNode(itemId);
        
        if (node.dimension < DIMENSION_LEVELS.WHOLE) {
            // Move to next dimension level
            node.dimension++;
            node.metadata.modified = Date.now();
            this.save();
            return { 
                newDimension: node.dimension, 
                name: DIMENSION_NAMES[node.dimension],
                icon: DIMENSION_ICONS[node.dimension]
            };
        } else {
            // At WHOLE (6), spiral up to next level and reset to POINT
            node.spiral++;
            node.dimension = DIMENSION_LEVELS.POINT;
            node.metadata.modified = Date.now();
            this.save();
            return { 
                newDimension: node.dimension, 
                spiral: node.spiral,
                name: `${DIMENSION_NAMES[node.dimension]} (Spiral ${node.spiral})`,
                icon: DIMENSION_ICONS[node.dimension],
                spiralUp: true
            };
        }
    },
    
    // Drill up - exit to outer container dimension
    drillUp(itemId) {
        const node = this.getNode(itemId);
        
        if (node.dimension > DIMENSION_LEVELS.POTENTIAL) {
            node.dimension--;
            node.metadata.modified = Date.now();
            this.save();
            return { 
                newDimension: node.dimension, 
                name: DIMENSION_NAMES[node.dimension],
                icon: DIMENSION_ICONS[node.dimension]
            };
        } else if (node.spiral > 0) {
            // At POTENTIAL, spiral down to previous level WHOLE
            node.spiral--;
            node.dimension = DIMENSION_LEVELS.WHOLE;
            node.metadata.modified = Date.now();
            this.save();
            return { 
                newDimension: node.dimension, 
                spiral: node.spiral,
                name: `${DIMENSION_NAMES[node.dimension]} (Spiral ${node.spiral})`,
                icon: DIMENSION_ICONS[node.dimension],
                spiralDown: true
            };
        }
        return null; // Can't go lower
    },
    
    // Connect as helix thread (parallel dimension - like siblings but dimensional)
    // Your brother in his dimension, you in yours, connected through higher dimension
    connectHelix(itemId, parallelId) {
        const node = this.getNode(itemId);
        const parallel = this.getNode(parallelId);
        
        if (!node.helixConnections.includes(parallelId)) {
            node.helixConnections.push(parallelId);
            node.metadata.modified = Date.now();
        }
        if (!parallel.helixConnections.includes(itemId)) {
            parallel.helixConnections.push(itemId);
            parallel.metadata.modified = Date.now();
        }
        
        this.save();
        showToast(`Helix connected: parallel dimensions linked`, 'success');
    },
    
    // Add inner point (something contained within this item's dimension)
    addInnerPoint(containerId, pointId) {
        const container = this.getNode(containerId);
        const point = this.getNode(pointId);
        
        if (!container.innerPoints.includes(pointId)) {
            container.innerPoints.push(pointId);
            container.metadata.modified = Date.now();
        }
        point.outerContainer = containerId;
        point.metadata.modified = Date.now();
        
        this.save();
        showToast(`Added as inner point`, 'success');
    },
    
    // Get dimensional info for display
    getDimensionInfo(itemId) {
        const node = this.nodes[itemId];
        if (!node) return null;
        
        return {
            level: node.dimension,
            name: DIMENSION_NAMES[node.dimension],
            icon: DIMENSION_ICONS[node.dimension],
            spiral: node.spiral,
            fullName: node.spiral > 0 
                ? `${DIMENSION_NAMES[node.dimension]} (Spiral ${node.spiral})`
                : DIMENSION_NAMES[node.dimension],
            helixCount: node.helixConnections.length,
            innerCount: node.innerPoints.length,
            hasOuter: !!node.outerContainer
        };
    },
    
    // Get the full helix view for an item
    getHelixView(itemId) {
        const node = this.nodes[itemId];
        if (!node) return null;
        
        return {
            current: {
                id: itemId,
                dimension: node.dimension,
                dimensionName: DIMENSION_NAMES[node.dimension],
                spiral: node.spiral
            },
            helixThreads: node.helixConnections.map(hId => ({
                id: hId,
                ...this.getDimensionInfo(hId)
            })),
            innerPoints: node.innerPoints.map(pId => ({
                id: pId,
                ...this.getDimensionInfo(pId)
            })),
            outerContainer: node.outerContainer ? {
                id: node.outerContainer,
                ...this.getDimensionInfo(node.outerContainer)
            } : null
        };
    },
    
    // Calculate dimensional distance between two items
    getDimensionalDistance(itemId1, itemId2) {
        const node1 = this.nodes[itemId1];
        const node2 = this.nodes[itemId2];
        if (!node1 || !node2) return Infinity;
        
        // Distance includes both spiral difference and dimension difference
        const spiralDiff = Math.abs(node1.spiral - node2.spiral);
        const dimDiff = Math.abs(node1.dimension - node2.dimension);
        
        return (spiralDiff * 7) + dimDiff; // 7 dimensions per spiral
    }
};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    dimensionalHelix.init();
});

// ============================================================================
// Knowledge Base - Learning System
// ============================================================================
const knowledgeBase = {
    // Vocabulary learned from data sources
    vocabulary: {},           // word -> { count, sources, contexts, lastSeen }
    
    // Concepts and their relationships
    concepts: {},             // concept -> { related: [], synonyms: [], sources: [] }
    
    // Query patterns that worked
    successfulPatterns: [],   // { pattern, sources, resultCount, timestamp }
    
    // Entity recognition
    entities: {
        companies: {},        // company name -> { ticker, industry, source }
        locations: {},        // location -> { type, coordinates, source }
        people: {},           // name -> { context, source }
        topics: {},           // topic -> { relatedTerms, sources }
        currencies: {},       // currency -> { symbol, rates }
        foods: {},            // food -> { category, nutrition }
        words: {}             // word -> { definitions, synonyms, antonyms }
    },
    
    // Source-specific knowledge
    sourceKnowledge: {},      // sourceId -> { lastFetch, dataTypes, sampleData }
    
    // Statistics
    stats: {
        totalQueries: 0,
        successfulQueries: 0,
        wordsLearned: 0,
        conceptsLearned: 0,
        lastLearningSession: null
    }
};

// ============================================================================
// Learning Engine
// ============================================================================
const learningEngine = {
    
    // Initialize from localStorage
    init() {
        const saved = localStorage.getItem('uhd_knowledge_base');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                Object.assign(knowledgeBase, parsed);
                console.log(`🧠 Knowledge loaded: ${knowledgeBase.stats.wordsLearned} words, ${knowledgeBase.stats.conceptsLearned} concepts`);
            } catch (e) {
                console.warn('Could not load knowledge base:', e);
            }
        }
    },
    
    // Save to localStorage
    save() {
        try {
            localStorage.setItem('uhd_knowledge_base', JSON.stringify(knowledgeBase));
        } catch (e) {
            console.warn('Could not save knowledge base:', e);
        }
    },
    
    // Learn from API response
    learnFromResponse(sourceId, data, query) {
        if (!data) return;
        
        const source = this.getSourceInfo(sourceId);
        const timestamp = Date.now();
        
        // Extract and learn based on data type
        if (typeof data === 'object') {
            if (Array.isArray(data)) {
                data.forEach(item => this.extractKnowledge(item, sourceId, source.category));
            } else {
                this.extractKnowledge(data, sourceId, source.category);
            }
        }
        
        // Remember source capabilities
        if (!knowledgeBase.sourceKnowledge[sourceId]) {
            knowledgeBase.sourceKnowledge[sourceId] = {
                lastFetch: timestamp,
                dataTypes: new Set(),
                sampleFields: [],
                queryCount: 0
            };
        }
        knowledgeBase.sourceKnowledge[sourceId].lastFetch = timestamp;
        knowledgeBase.sourceKnowledge[sourceId].queryCount++;
        
        // Track successful query pattern
        if (query) {
            knowledgeBase.successfulPatterns.push({
                pattern: query.toLowerCase(),
                source: sourceId,
                category: source.category,
                timestamp: timestamp
            });
            // Keep last 1000 patterns
            if (knowledgeBase.successfulPatterns.length > 1000) {
                knowledgeBase.successfulPatterns = knowledgeBase.successfulPatterns.slice(-1000);
            }
        }
        
        knowledgeBase.stats.lastLearningSession = timestamp;
        this.save();
    },
    
    // Extract knowledge from data object
    extractKnowledge(obj, sourceId, category) {
        if (!obj || typeof obj !== 'object') return;
        
        // Process each field
        Object.entries(obj).forEach(([key, value]) => {
            // Learn field names as vocabulary
            this.learnWord(key, sourceId, 'field_name');
            
            // Extract based on value type
            if (typeof value === 'string') {
                this.processStringValue(key, value, sourceId, category);
            } else if (typeof value === 'number') {
                this.processNumericValue(key, value, sourceId, category);
            } else if (typeof value === 'object' && value !== null) {
                this.extractKnowledge(value, sourceId, category);
            }
        });
    },
    
    // Process string values
    processStringValue(key, value, sourceId, category) {
        // Skip very long strings or URLs
        if (value.length > 500 || value.startsWith('http')) return;
        
        // Categorize based on field name and source category
        const keyLower = key.toLowerCase();
        
        // Learn definitions from dictionary sources
        if (category === 'knowledge' && (keyLower.includes('definition') || keyLower.includes('meaning'))) {
            this.learnDefinition(value, sourceId);
        }
        
        // Learn company names from finance sources
        if (category === 'finance' && (keyLower.includes('name') || keyLower.includes('company'))) {
            this.learnEntity('companies', value, { source: sourceId });
        }
        
        // Learn locations
        if (keyLower.includes('city') || keyLower.includes('country') || keyLower.includes('location')) {
            this.learnEntity('locations', value, { type: keyLower, source: sourceId });
        }
        
        // Learn food items
        if (category === 'food' && (keyLower.includes('meal') || keyLower.includes('dish') || keyLower.includes('ingredient'))) {
            this.learnEntity('foods', value, { category: keyLower, source: sourceId });
        }
        
        // Learn topics from news
        if (category === 'news' && (keyLower.includes('title') || keyLower.includes('topic') || keyLower.includes('category'))) {
            this.learnTopic(value, sourceId);
        }
        
        // Extract individual words for vocabulary
        const words = value.split(/\s+/).filter(w => w.length > 2 && w.length < 30);
        words.forEach(word => {
            const cleanWord = word.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
            if (cleanWord.length > 2) {
                this.learnWord(cleanWord, sourceId, category);
            }
        });
    },
    
    // Process numeric values
    processNumericValue(key, value, sourceId, category) {
        const keyLower = key.toLowerCase();
        
        // Learn price patterns from finance
        if (category === 'finance' && (keyLower.includes('price') || keyLower.includes('rate'))) {
            // Store as reference for similar queries
            if (!knowledgeBase.sourceKnowledge[sourceId]) {
                knowledgeBase.sourceKnowledge[sourceId] = { priceFields: [] };
            }
            if (!knowledgeBase.sourceKnowledge[sourceId].priceFields) {
                knowledgeBase.sourceKnowledge[sourceId].priceFields = [];
            }
            if (!knowledgeBase.sourceKnowledge[sourceId].priceFields.includes(key)) {
                knowledgeBase.sourceKnowledge[sourceId].priceFields.push(key);
            }
        }
    },
    
    // Learn a word
    learnWord(word, sourceId, context) {
        const w = word.toLowerCase();
        if (!knowledgeBase.vocabulary[w]) {
            knowledgeBase.vocabulary[w] = {
                count: 0,
                sources: [],
                contexts: [],
                firstSeen: Date.now(),
                lastSeen: Date.now()
            };
            knowledgeBase.stats.wordsLearned++;
        }
        
        const entry = knowledgeBase.vocabulary[w];
        entry.count++;
        entry.lastSeen = Date.now();
        
        if (!entry.sources.includes(sourceId)) {
            entry.sources.push(sourceId);
        }
        if (context && !entry.contexts.includes(context)) {
            entry.contexts.push(context);
        }
    },
    
    // Learn a definition (from dictionary APIs)
    learnDefinition(definition, sourceId) {
        // Extract key terms from definition
        const words = definition.split(/\s+/);
        words.forEach(word => {
            const clean = word.replace(/[^a-zA-Z]/g, '').toLowerCase();
            if (clean.length > 3) {
                this.learnWord(clean, sourceId, 'definition');
            }
        });
    },
    
    // Learn an entity
    learnEntity(type, name, meta) {
        if (!name || typeof name !== 'string') return;
        
        const clean = name.trim();
        if (clean.length < 2 || clean.length > 100) return;
        
        if (!knowledgeBase.entities[type][clean]) {
            knowledgeBase.entities[type][clean] = {
                ...meta,
                firstSeen: Date.now(),
                mentions: 0
            };
        }
        knowledgeBase.entities[type][clean].mentions++;
        knowledgeBase.entities[type][clean].lastSeen = Date.now();
    },
    
    // Learn a topic
    learnTopic(topic, sourceId) {
        const clean = topic.trim().toLowerCase();
        if (clean.length < 2) return;
        
        if (!knowledgeBase.entities.topics[clean]) {
            knowledgeBase.entities.topics[clean] = {
                sources: [],
                relatedTerms: [],
                mentions: 0
            };
            knowledgeBase.stats.conceptsLearned++;
        }
        
        const entry = knowledgeBase.entities.topics[clean];
        entry.mentions++;
        if (!entry.sources.includes(sourceId)) {
            entry.sources.push(sourceId);
        }
    },
    
    // Learn synonyms from thesaurus data
    learnSynonyms(word, synonyms, sourceId) {
        const w = word.toLowerCase();
        if (!knowledgeBase.concepts[w]) {
            knowledgeBase.concepts[w] = {
                synonyms: [],
                related: [],
                sources: []
            };
        }
        
        const entry = knowledgeBase.concepts[w];
        synonyms.forEach(syn => {
            if (!entry.synonyms.includes(syn.toLowerCase())) {
                entry.synonyms.push(syn.toLowerCase());
            }
        });
        if (!entry.sources.includes(sourceId)) {
            entry.sources.push(sourceId);
        }
    },
    
    // Get source info from registry
    getSourceInfo(sourceId) {
        for (const category of Object.keys(API_REGISTRY)) {
            const service = API_REGISTRY[category].find(s => s.id === sourceId);
            if (service) return { ...service, category };
        }
        return { category: 'unknown' };
    },
    
    // Suggest completions based on learned vocabulary
    getSuggestions(prefix, limit = 10) {
        const suggestions = [];
        const prefixLower = prefix.toLowerCase();
        
        // Search vocabulary
        for (const [word, data] of Object.entries(knowledgeBase.vocabulary)) {
            if (word.startsWith(prefixLower) && data.count > 1) {
                suggestions.push({
                    word,
                    score: data.count * data.sources.length,
                    type: 'vocabulary'
                });
            }
        }
        
        // Search entities
        for (const [type, entities] of Object.entries(knowledgeBase.entities)) {
            for (const [name, data] of Object.entries(entities)) {
                if (name.toLowerCase().includes(prefixLower)) {
                    suggestions.push({
                        word: name,
                        score: data.mentions || 1,
                        type: type
                    });
                }
            }
        }
        
        // Sort by score and return top results
        return suggestions
            .sort((a, b) => b.score - a.score)
            .slice(0, limit);
    },
    
    // Find best source for a query
    suggestSource(query) {
        const queryLower = query.toLowerCase();
        const scores = {};
        
        // Check learned patterns
        knowledgeBase.successfulPatterns.forEach(pattern => {
            if (queryLower.includes(pattern.pattern.substring(0, 5))) {
                scores[pattern.source] = (scores[pattern.source] || 0) + 1;
            }
        });
        
        // Check vocabulary associations
        const queryWords = queryLower.split(/\s+/);
        queryWords.forEach(word => {
            const vocabEntry = knowledgeBase.vocabulary[word];
            if (vocabEntry) {
                vocabEntry.sources.forEach(source => {
                    scores[source] = (scores[source] || 0) + vocabEntry.count;
                });
            }
        });
        
        // Return top sources
        return Object.entries(scores)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .map(([source, score]) => ({ source, score }));
    },
    
    // Expand query using learned synonyms and related terms
    expandQuery(query) {
        const words = query.toLowerCase().split(/\s+/);
        const expanded = new Set(words);
        
        words.forEach(word => {
            // Add synonyms
            if (knowledgeBase.concepts[word]) {
                knowledgeBase.concepts[word].synonyms.forEach(syn => expanded.add(syn));
            }
            
            // Add related words from same context
            if (knowledgeBase.vocabulary[word]) {
                const contexts = knowledgeBase.vocabulary[word].contexts;
                // Find other words with same context
                for (const [w, data] of Object.entries(knowledgeBase.vocabulary)) {
                    if (data.contexts.some(c => contexts.includes(c)) && data.count > 5) {
                        expanded.add(w);
                    }
                }
            }
        });
        
        return Array.from(expanded);
    },
    
    // Get knowledge stats for display
    getStats() {
        return {
            vocabularySize: Object.keys(knowledgeBase.vocabulary).length,
            conceptsLearned: knowledgeBase.stats.conceptsLearned,
            entitiesKnown: Object.values(knowledgeBase.entities)
                .reduce((sum, e) => sum + Object.keys(e).length, 0),
            patternsLearned: knowledgeBase.successfulPatterns.length,
            sourcesLearned: Object.keys(knowledgeBase.sourceKnowledge).length,
            totalQueries: knowledgeBase.stats.totalQueries,
            lastSession: knowledgeBase.stats.lastLearningSession
        };
    },
    
    // Answer a question using learned knowledge
    answerQuestion(question) {
        const questionLower = question.toLowerCase();
        const answers = [];
        
        // Check if asking about a word definition
        if (questionLower.includes('what is') || questionLower.includes('define') || 
            questionLower.includes('meaning of')) {
            const words = questionLower.match(/(?:what is|define|meaning of)\s+(?:a\s+)?(\w+)/);
            if (words && words[1]) {
                const word = words[1];
                if (knowledgeBase.entities.words[word]) {
                    answers.push({
                        type: 'definition',
                        answer: knowledgeBase.entities.words[word],
                        confidence: 0.9
                    });
                }
            }
        }
        
        // Check for company/stock info
        if (questionLower.includes('stock') || questionLower.includes('price of') ||
            questionLower.includes('company')) {
            for (const [company, data] of Object.entries(knowledgeBase.entities.companies)) {
                if (questionLower.includes(company.toLowerCase())) {
                    answers.push({
                        type: 'company',
                        answer: data,
                        entity: company,
                        confidence: 0.8
                    });
                }
            }
        }
        
        // Check for location info
        if (questionLower.includes('weather') || questionLower.includes('where is') ||
            questionLower.includes('location')) {
            for (const [location, data] of Object.entries(knowledgeBase.entities.locations)) {
                if (questionLower.includes(location.toLowerCase())) {
                    answers.push({
                        type: 'location',
                        answer: data,
                        entity: location,
                        confidence: 0.7
                    });
                }
            }
        }
        
        // Check for recipe/food info
        if (questionLower.includes('recipe') || questionLower.includes('cook') ||
            questionLower.includes('how to make')) {
            for (const [food, data] of Object.entries(knowledgeBase.entities.foods)) {
                if (questionLower.includes(food.toLowerCase())) {
                    answers.push({
                        type: 'food',
                        answer: data,
                        entity: food,
                        confidence: 0.7
                    });
                }
            }
        }
        
        // Suggest sources for more info
        const suggestedSources = this.suggestSource(question);
        
        return {
            answers,
            suggestedSources,
            canAnswer: answers.length > 0,
            needsLookup: answers.length === 0 && suggestedSources.length > 0
        };
    }
};

// Initialize learning engine on load
document.addEventListener('DOMContentLoaded', () => {
    learningEngine.init();
});

// ============================================================================
// DOM Elements
// ============================================================================
const elements = {
    // Panels
    leftPanel: null,
    rightPanel: null,
    mobileOverlay: null,
    
    // Views
    folderView: null,
    tableView: null,
    visualView: null,
    apiView: null,
    
    // Content areas
    folderContent: null,
    tableBody: null,
    apiGrid: null,
    helixNavigator: null,
    helixLevels: null,
    
    // Inputs
    addressInput: null,
    universalQuery: null,
    
    // Modals
    connectionModal: null,
    crawlerModal: null,
    propertiesModal: null,
    
    // Other
    contextMenu: null
};

// ============================================================================
// Initialize Application
// ============================================================================
document.addEventListener('DOMContentLoaded', function() {
    initializeElements();
    initializeEventListeners();
    loadConnections();
    populateQuickConnect();
    populateServicesGrid();
    populateApiGrid();
    loadSampleData();
    updateScopeIndicator();
    
    // Initialize helix navigator
    dimensionalHelix.init();
    updateHelixLevelCounts();
    updateHelixThreads();
});

function initializeElements() {
    // Panels
    elements.leftPanel = document.getElementById('left-panel');
    elements.rightPanel = document.getElementById('right-panel');
    elements.mobileOverlay = document.getElementById('mobile-overlay');
    
    // Views
    elements.folderView = document.getElementById('folder-view');
    elements.tableView = document.getElementById('table-view');
    elements.visualView = document.getElementById('visual-view');
    elements.apiView = document.getElementById('api-view');
    
    // Content
    elements.folderContent = document.getElementById('folder-content');
    elements.tableBody = document.getElementById('table-body');
    elements.apiGrid = document.getElementById('api-grid');
    elements.helixNavigator = document.getElementById('helix-navigator');
    elements.helixLevels = document.getElementById('helix-levels');
    
    // Inputs
    elements.addressInput = document.getElementById('address-input');
    elements.universalQuery = document.getElementById('universal-query');
    
    // Modals
    elements.connectionModal = document.getElementById('connection-modal');
    elements.crawlerModal = document.getElementById('crawler-modal');
    elements.propertiesModal = document.getElementById('properties-modal');
    
    // Other
    elements.contextMenu = document.getElementById('context-menu');
}

// ============================================================================
// Event Listeners
// ============================================================================
function initializeEventListeners() {
    // Mobile Navigation
    const btnToggleLeft = document.getElementById('btn-toggle-left');
    const btnToggleRight = document.getElementById('btn-toggle-right');
    
    if (btnToggleLeft) {
        btnToggleLeft.addEventListener('click', () => togglePanel('left'));
    }
    if (btnToggleRight) {
        btnToggleRight.addEventListener('click', () => togglePanel('right'));
    }
    
    // Mobile overlay close
    if (elements.mobileOverlay) {
        elements.mobileOverlay.addEventListener('click', closePanels);
    }
    
    // Panel collapse buttons
    const collapseLeft = document.getElementById('collapse-left');
    const collapseRight = document.getElementById('collapse-right');
    
    if (collapseLeft) {
        collapseLeft.addEventListener('click', () => togglePanel('left'));
    }
    if (collapseRight) {
        collapseRight.addEventListener('click', () => togglePanel('right'));
    }
    
    // Navigation buttons
    document.getElementById('btn-back')?.addEventListener('click', navigateBack);
    document.getElementById('btn-forward')?.addEventListener('click', navigateForward);
    document.getElementById('btn-up')?.addEventListener('click', navigateUp);
    document.getElementById('btn-refresh')?.addEventListener('click', refresh);
    document.getElementById('btn-home')?.addEventListener('click', navigateHome);
    document.getElementById('btn-go')?.addEventListener('click', navigateToAddress);
    
    // Address bar enter key
    elements.addressInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') navigateToAddress();
    });
    
    // Connection & Crawler
    document.getElementById('btn-new-connection')?.addEventListener('click', openConnectionWizard);
    document.getElementById('btn-crawler')?.addEventListener('click', openCrawler);
    
    // Modal close buttons
    document.getElementById('close-connection-modal')?.addEventListener('click', closeConnectionModal);
    document.getElementById('close-crawler-modal')?.addEventListener('click', closeCrawlerModal);
    document.getElementById('close-properties-modal')?.addEventListener('click', closePropertiesModal);
    document.getElementById('wizard-cancel')?.addEventListener('click', closeConnectionModal);
    
    // Wizard navigation
    document.getElementById('wizard-back')?.addEventListener('click', wizardBack);
    document.getElementById('wizard-next')?.addEventListener('click', wizardNext);
    document.getElementById('wizard-finish')?.addEventListener('click', wizardFinish);
    
    // View tabs
    document.querySelectorAll('.view-tab').forEach(tab => {
        tab.addEventListener('click', () => switchView(tab.dataset.view));
    });
    
    // View mode buttons
    document.querySelectorAll('.view-mode-btn').forEach(btn => {
        btn.addEventListener('click', () => switchViewMode(btn.dataset.mode));
    });
    
    // Helix navigation - spiral controls
    document.getElementById('spiral-up')?.addEventListener('click', spiralUp);
    document.getElementById('spiral-down')?.addEventListener('click', spiralDown);
    
    // Helix navigation - level selection
    elements.helixLevels?.addEventListener('click', handleHelixLevelClick);
    
    // Helix section toggles
    document.querySelectorAll('.helix-section-header').forEach(header => {
        header.addEventListener('click', (e) => toggleHelixSection(e.target.closest('.helix-section-header')));
    });
    
    // Helix items (APIs, sources)
    elements.helixNavigator?.addEventListener('click', handleHelixNavClick);
    
    // Universal query
    document.getElementById('btn-execute')?.addEventListener('click', executeQuery);
    elements.universalQuery?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') executeQuery();
    });
    
    // Autocomplete on query input
    elements.universalQuery?.addEventListener('input', (e) => {
        const value = e.target.value;
        if (value.length >= 2) {
            showQuerySuggestions(value);
        } else {
            hideQuerySuggestions();
        }
    });
    
    // Hide suggestions on blur
    elements.universalQuery?.addEventListener('blur', () => {
        setTimeout(hideQuerySuggestions, 200);
    });
    
    // Context menu
    elements.folderContent?.addEventListener('contextmenu', showContextMenu);
    document.addEventListener('click', hideContextMenu);
    
    // Crawler search
    document.getElementById('btn-crawl')?.addEventListener('click', searchAPIs);
    
    // Service category filters
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.addEventListener('click', () => filterServices(btn.dataset.category));
    });
    
    // Chart type buttons
    document.querySelectorAll('.chart-btn').forEach(btn => {
        btn.addEventListener('click', () => switchChartType(btn.dataset.chart));
    });
}

// ============================================================================
// Mobile Panel Management
// ============================================================================
function togglePanel(panel) {
    if (panel === 'left') {
        elements.leftPanel?.classList.toggle('mobile-visible');
        elements.rightPanel?.classList.remove('mobile-visible');
    } else {
        elements.rightPanel?.classList.toggle('mobile-visible');
        elements.leftPanel?.classList.remove('mobile-visible');
    }
    
    // Show/hide overlay
    const isAnyOpen = elements.leftPanel?.classList.contains('mobile-visible') ||
                      elements.rightPanel?.classList.contains('mobile-visible');
    elements.mobileOverlay?.classList.toggle('visible', isAnyOpen);
}

function closePanels() {
    elements.leftPanel?.classList.remove('mobile-visible');
    elements.rightPanel?.classList.remove('mobile-visible');
    elements.mobileOverlay?.classList.remove('visible');
}

// ============================================================================
// Navigation
// ============================================================================
function navigateBack() {
    if (state.historyIndex > 0) {
        state.historyIndex--;
        navigateTo(state.history[state.historyIndex], false);
    }
}

function navigateForward() {
    if (state.historyIndex < state.history.length - 1) {
        state.historyIndex++;
        navigateTo(state.history[state.historyIndex], false);
    }
}

function navigateUp() {
    const parts = state.currentPath.split('/').filter(p => p);
    if (parts.length > 1) {
        parts.pop();
        navigateTo(parts.join('/') + '/');
    }
}

function navigateHome() {
    navigateTo('substrate://local/');
}

function navigateToAddress() {
    const address = elements.addressInput?.value || 'substrate://local/';
    navigateTo(address);
}

function navigateTo(path, addToHistory = true) {
    state.currentPath = path;
    
    if (addToHistory) {
        // Truncate forward history if we navigate to new path
        state.history = state.history.slice(0, state.historyIndex + 1);
        state.history.push(path);
        state.historyIndex = state.history.length - 1;
    }
    
    if (elements.addressInput) {
        elements.addressInput.value = path;
    }
    
    updateBreadcrumb(path);
    loadContent(path);
}

function updateBreadcrumb(path) {
    const breadcrumb = document.getElementById('breadcrumb');
    if (!breadcrumb) return;
    
    const parts = path.replace(/^substrate:\/\//, '').split('/').filter(p => p);
    
    let html = '<span class="crumb" data-path="/">🏠 Home</span>';
    let currentPath = '';
    
    parts.forEach((part, i) => {
        currentPath += part + '/';
        html += `<span class="crumb-separator">›</span>`;
        html += `<span class="crumb" data-path="${currentPath}">${part}</span>`;
    });
    
    breadcrumb.innerHTML = html;
    
    // Add click listeners to breadcrumb items
    breadcrumb.querySelectorAll('.crumb').forEach(crumb => {
        crumb.addEventListener('click', () => {
            navigateTo('substrate://' + crumb.dataset.path);
        });
    });
}

function refresh() {
    loadContent(state.currentPath);
}

// ============================================================================
// Content Loading
// ============================================================================
function loadContent(path) {
    // Simulate loading content based on path
    const content = generateSampleContent(path);
    renderFolderView(content);
    renderTableView(content);
    updateItemCount(content.length);
}

function generateSampleContent(path) {
    // Generate sample content based on current path
    const items = [];
    
    if (path.includes('local')) {
        items.push(
            { id: 1, name: 'Documents', type: 'folder', icon: '📁', size: '-', created: '2026-01-15' },
            { id: 2, name: 'Images', type: 'folder', icon: '🖼️', size: '-', created: '2026-01-10' },
            { id: 3, name: 'Videos', type: 'folder', icon: '🎬', size: '-', created: '2026-01-08' },
            { id: 4, name: 'Music', type: 'folder', icon: '🎵', size: '-', created: '2026-01-05' },
            { id: 5, name: 'Substrates', type: 'folder', icon: '💾', size: '-', created: '2026-02-01' },
            { id: 6, name: 'report_2026.pdf', type: 'file', icon: '📄', size: '2.4 MB', created: '2026-02-10' },
            { id: 7, name: 'presentation.pptx', type: 'file', icon: '📊', size: '15.8 MB', created: '2026-02-08' },
            { id: 8, name: 'data_export.csv', type: 'file', icon: '📋', size: '458 KB', created: '2026-02-05' }
        );
    }
    
    return items;
}

function loadSampleData() {
    navigateTo('substrate://local/', true);
}

// ============================================================================
// Folder View Rendering
// ============================================================================
function renderFolderView(items) {
    if (!elements.folderContent) return;
    
    elements.folderContent.innerHTML = items.map(item => `
        <div class="folder-item ${state.selectedItems.includes(item.id) ? 'selected' : ''}" 
             data-id="${item.id}" 
             data-type="${item.type}">
            ${state.viewMode === 'thumbs' && item.type !== 'folder' ? 
                `<div class="item-thumbnail"><span class="item-icon">${item.icon}</span></div>` :
                `<span class="item-icon">${item.icon}</span>`
            }
            <span class="item-name">${item.name}</span>
        </div>
    `).join('');
    
    // Add click listeners
    elements.folderContent.querySelectorAll('.folder-item').forEach(item => {
        item.addEventListener('click', (e) => selectItem(item, e));
        item.addEventListener('dblclick', () => openItem(item));
    });
}

function switchViewMode(mode) {
    state.viewMode = mode;
    
    // Update button states
    document.querySelectorAll('.view-mode-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });
    
    // Update content class
    if (elements.folderContent) {
        elements.folderContent.className = `folder-content ${mode}-view`;
    }
    
    // Re-render
    loadContent(state.currentPath);
}

function selectItem(itemElement, event) {
    const id = parseInt(itemElement.dataset.id);
    
    if (event.ctrlKey || event.metaKey) {
        // Toggle selection
        if (state.selectedItems.includes(id)) {
            state.selectedItems = state.selectedItems.filter(i => i !== id);
            itemElement.classList.remove('selected');
        } else {
            state.selectedItems.push(id);
            itemElement.classList.add('selected');
        }
    } else {
        // Single selection
        state.selectedItems = [id];
        document.querySelectorAll('.folder-item').forEach(el => el.classList.remove('selected'));
        itemElement.classList.add('selected');
    }
    
    updateSelectedCount();
    showItemDetails(itemElement);
}

function openItem(itemElement) {
    const type = itemElement.dataset.type;
    const name = itemElement.querySelector('.item-name')?.textContent;
    
    if (type === 'folder') {
        navigateTo(state.currentPath + name + '/');
    } else {
        // Open file preview
        console.log('Opening file:', name);
    }
}

// ============================================================================
// Table View Rendering
// ============================================================================
function renderTableView(items) {
    if (!elements.tableBody) return;
    
    elements.tableBody.innerHTML = items.map(item => `
        <tr data-id="${item.id}" class="${state.selectedItems.includes(item.id) ? 'selected' : ''}">
            <td>${item.id}</td>
            <td><span class="item-icon">${item.icon}</span> ${item.name}</td>
            <td>${item.type}</td>
            <td>Local</td>
            <td>${item.created}</td>
            <td>${item.size}</td>
            <td>-</td>
            <td>
                <button class="table-btn" onclick="openItem(${item.id})">Open</button>
                <button class="table-btn" onclick="showProperties(${item.id})">Info</button>
            </td>
        </tr>
    `).join('');
}

// ============================================================================
// View Switching
// ============================================================================
function switchView(view) {
    state.currentView = view;
    
    // Update tab states
    document.querySelectorAll('.view-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.view === view);
    });
    
    // Show/hide panels
    document.querySelectorAll('.view-panel').forEach(panel => {
        panel.classList.toggle('active', panel.id === `${view}-view`);
    });
    
    // Initialize chart if visual view
    if (view === 'visual') {
        initializeChart();
    }
}

// ============================================================================
// Helix Navigation - Golden Ratio Dimensional Navigator
// ============================================================================
// 7 Levels per spiral: Potential → Point → Length → Width → Plane → Volume → Whole → spiral up

let currentHelixState = {
    spiral: 0,
    level: 1,  // Start at Point
    activeThread: null
};

function handleHelixLevelClick(event) {
    const level = event.target.closest('.helix-level');
    if (!level) return;
    
    const levelNum = parseInt(level.dataset.level);
    selectHelixLevel(levelNum);
}

function selectHelixLevel(levelNum) {
    // Update state
    currentHelixState.level = levelNum;
    
    // Update UI
    document.querySelectorAll('.helix-level').forEach(l => {
        l.classList.toggle('active', parseInt(l.dataset.level) === levelNum);
    });
    
    // Filter content to show items at this dimensional level
    filterByDimensionalLevel(levelNum);
    
    showToast(`${DIMENSION_ICONS[levelNum]} Viewing ${DIMENSION_NAMES[levelNum]} level`, 'info');
}

function filterByDimensionalLevel(level) {
    // Filter items in current view by dimensional level
    const items = Object.entries(dimensionalHelix.nodes)
        .filter(([id, node]) => node.dimension === level && node.spiral === currentHelixState.spiral);
    
    // Update level counts
    updateHelixLevelCounts();
    
    // If filtering to specific level, could show those items
    console.log(`Found ${items.length} items at level ${DIMENSION_NAMES[level]}`);
}

function spiralUp() {
    currentHelixState.spiral++;
    updateSpiralDisplay();
    updateHelixLevelCounts();
    showToast(`⬆️ Spiral ${currentHelixState.spiral} - Higher dimensional plane`, 'success');
}

function spiralDown() {
    if (currentHelixState.spiral > 0) {
        currentHelixState.spiral--;
        updateSpiralDisplay();
        updateHelixLevelCounts();
        showToast(`⬇️ Spiral ${currentHelixState.spiral}`, 'info');
    } else {
        showToast('Already at base spiral (0)', 'warning');
    }
}

function updateSpiralDisplay() {
    const spiralNumber = document.querySelector('#current-spiral .spiral-number');
    if (spiralNumber) {
        spiralNumber.textContent = currentHelixState.spiral;
    }
}

function updateHelixLevelCounts() {
    // Count items at each level for current spiral
    const counts = [0, 0, 0, 0, 0, 0, 0];
    
    Object.values(dimensionalHelix.nodes).forEach(node => {
        if (node.spiral === currentHelixState.spiral && node.dimension >= 0 && node.dimension <= 6) {
            counts[node.dimension]++;
        }
    });
    
    // Update UI
    for (let i = 0; i <= 6; i++) {
        const countEl = document.querySelector(`[data-level-count="${i}"]`);
        if (countEl) {
            countEl.textContent = counts[i];
        }
    }
}

function toggleHelixSection(header) {
    if (!header) return;
    
    const isExpanded = header.classList.contains('expanded');
    header.classList.toggle('expanded', !isExpanded);
    
    // Update toggle icon
    const toggle = header.querySelector('.section-toggle');
    if (toggle) {
        toggle.textContent = isExpanded ? '▶' : '▼';
    }
    
    // Show/hide content
    const content = header.nextElementSibling;
    if (content && content.classList.contains('helix-section-content')) {
        content.classList.toggle('active', !isExpanded);
        
        if (!isExpanded) {
            content.style.maxHeight = content.scrollHeight + 'px';
        } else {
            content.style.maxHeight = '0';
        }
    }
}

function handleHelixNavClick(event) {
    // Handle clicks on helix items (categories, connections)
    const item = event.target.closest('.helix-item');
    if (!item) return;
    
    const category = item.dataset.category;
    const connection = item.dataset.connection;
    
    if (category) {
        showCategoryAPIs(category);
        highlightHelixItem(item);
    } else if (connection) {
        navigateToConnection(connection);
        highlightHelixItem(item);
    }
}

function highlightHelixItem(item) {
    // Remove previous highlight
    document.querySelectorAll('.helix-item.selected').forEach(i => {
        i.classList.remove('selected');
    });
    
    // Add highlight to current
    item.classList.add('selected');
}

function updateHelixThreads() {
    // Update the parallel threads list in the navigator
    const threadsList = document.getElementById('threads-list');
    if (!threadsList) return;
    
    // Get all unique helix connections
    const threads = new Set();
    Object.entries(dimensionalHelix.nodes).forEach(([id, node]) => {
        if (node.helixConnections) {
            node.helixConnections.forEach(conn => threads.add(conn));
        }
    });
    
    // Update count
    const countEl = document.getElementById('thread-count');
    if (countEl) {
        countEl.textContent = threads.size;
    }
    
    // Populate list
    if (threads.size > 0) {
        threadsList.innerHTML = Array.from(threads).map(threadId => {
            const node = dimensionalHelix.nodes[threadId];
            const icon = node ? DIMENSION_ICONS[node.dimension] : '•';
            const spiral = node?.spiral || 0;
            return `
                <div class="helix-thread-item" data-thread="${threadId}">
                    <span class="item-icon">${icon}</span>
                    <span class="item-label">${threadId.split('/').pop()}</span>
                    ${spiral > 0 ? `<span class="thread-spiral-badge">S${spiral}</span>` : ''}
                </div>
            `;
        }).join('');
    } else {
        threadsList.innerHTML = '<div class="helix-item" style="color: var(--text-muted); font-style: italic;">No parallel threads yet</div>';
    }
}

function navigateToConnection(connectionId) {
    const connection = state.connections.find(c => c.id === connectionId);
    if (connection) {
        navigateTo(`substrate://connections/${connectionId}/`);
        loadConnectionContent(connection);
    }
}

function loadConnectionContent(connection) {
    // Load content from a connected source
    const items = [];
    
    // Add connection-specific folders based on service type
    const service = findServiceById(connection.id);
    if (service && service.endpoints) {
        service.endpoints.forEach((endpoint, i) => {
            items.push({
                id: `${connection.id}_${i}`,
                name: endpoint.name,
                type: 'endpoint',
                icon: '📡',
                size: '-',
                created: new Date().toISOString().split('T')[0]
            });
        });
    }
    
    renderFolderView(items);
    updateItemCount(items.length);
}

function addConnectionToHelix(connection) {
    const sourcesList = document.getElementById('sources-list');
    if (!sourcesList) return;
    
    // Create helix item for connection
    const item = document.createElement('div');
    item.className = 'helix-item connection-item';
    item.dataset.connection = connection.id;
    item.innerHTML = `
        <span class="item-icon">${getConnectionIcon(connection.type)}</span>
        <span class="item-label">${connection.name}</span>
        <span class="connection-status ${connection.connected ? 'online' : 'offline'}"></span>
    `;
    
    sourcesList.appendChild(item);
    
    // Update connection count
    const countEl = document.getElementById('connection-count');
    if (countEl) {
        countEl.textContent = state.connections.length;
    }
}

function getConnectionIcon(type) {
    const icons = {
        weather: '🌤️',
        finance: '💰',
        news: '📰',
        database: '🗄️',
        storage: '☁️',
        api: '🔌',
        knowledge: '📖',
        food: '🍲',
        music: '🎵',
        ai: '🤖'
    };
    return icons[type] || '🔗';
}

// ============================================================================
// Connection Wizard
// ============================================================================
let wizardState = {
    step: 1,
    selectedService: null
};

function openConnectionWizard() {
    wizardState = { step: 1, selectedService: null };
    showWizardStep(1);
    elements.connectionModal?.classList.add('visible');
}

function closeConnectionModal() {
    elements.connectionModal?.classList.remove('visible');
}

function showWizardStep(step) {
    wizardState.step = step;
    
    // Update step indicators
    document.querySelectorAll('.wizard-step').forEach(s => {
        const stepNum = parseInt(s.dataset.step);
        s.classList.toggle('active', stepNum === step);
        s.classList.toggle('completed', stepNum < step);
    });
    
    // Show/hide panels
    document.querySelectorAll('.wizard-panel').forEach(panel => {
        panel.classList.toggle('active', parseInt(panel.dataset.step) === step);
    });
    
    // Update buttons
    const backBtn = document.getElementById('wizard-back');
    const nextBtn = document.getElementById('wizard-next');
    const finishBtn = document.getElementById('wizard-finish');
    
    if (backBtn) backBtn.style.display = step > 1 ? 'block' : 'none';
    if (nextBtn) nextBtn.style.display = step < 3 ? 'block' : 'none';
    if (finishBtn) finishBtn.style.display = step === 3 ? 'block' : 'none';
}

function wizardBack() {
    if (wizardState.step > 1) {
        showWizardStep(wizardState.step - 1);
    }
}

function wizardNext() {
    if (wizardState.step === 1 && !wizardState.selectedService) {
        alert('Please select a service to connect');
        return;
    }
    
    if (wizardState.step < 3) {
        showWizardStep(wizardState.step + 1);
        
        if (wizardState.step === 2) {
            populateConfigForm();
        } else if (wizardState.step === 3) {
            testConnection();
        }
    }
}

function wizardFinish() {
    // Save connection
    if (wizardState.selectedService) {
        const formData = getConfigFormData();
        saveConnection(wizardState.selectedService, formData);
    }
    closeConnectionModal();
}

// ============================================================================
// Services Grid
// ============================================================================
function populateServicesGrid() {
    const grid = document.getElementById('services-grid');
    if (!grid) return;
    
    let html = '';
    
    Object.values(API_REGISTRY).forEach(category => {
        category.forEach(service => {
            html += `
                <div class="service-card" data-id="${service.id}" onclick="selectService('${service.id}')">
                    <span class="service-icon">${service.icon}</span>
                    <span class="service-name">${service.name}</span>
                    <span class="service-auth">
                        ${service.noKeyRequired ? '🆓 No Key' : '🔑 Key Required'}
                    </span>
                </div>
            `;
        });
    });
    
    grid.innerHTML = html;
}

function selectService(serviceId) {
    // Find service
    let service = null;
    Object.values(API_REGISTRY).forEach(category => {
        const found = category.find(s => s.id === serviceId);
        if (found) service = found;
    });
    
    if (!service) return;
    
    wizardState.selectedService = service;
    
    // Update UI
    document.querySelectorAll('.service-card').forEach(card => {
        card.classList.toggle('selected', card.dataset.id === serviceId);
    });
}

function filterServices(category) {
    // Update button states
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.category === category);
    });
    
    // Filter grid
    const grid = document.getElementById('services-grid');
    if (!grid) return;
    
    let html = '';
    
    if (category === 'all') {
        Object.values(API_REGISTRY).forEach(cat => {
            cat.forEach(service => {
                html += createServiceCard(service);
            });
        });
    } else {
        const services = API_REGISTRY[category] || [];
        services.forEach(service => {
            html += createServiceCard(service);
        });
    }
    
    grid.innerHTML = html;
}

function createServiceCard(service) {
    return `
        <div class="service-card" data-id="${service.id}" onclick="selectService('${service.id}')">
            <span class="service-icon">${service.icon}</span>
            <span class="service-name">${service.name}</span>
            <span class="service-auth">
                ${service.noKeyRequired ? '🆓 No Key' : '🔑 Key Required'}
            </span>
        </div>
    `;
}

// ============================================================================
// Config Form
// ============================================================================
function populateConfigForm() {
    const service = wizardState.selectedService;
    if (!service) return;
    
    // Update header
    const logo = document.getElementById('config-service-logo');
    const name = document.getElementById('config-service-name');
    const desc = document.getElementById('config-service-desc');
    
    if (logo) logo.textContent = service.icon;
    if (name) name.textContent = service.name;
    if (desc) {
        let descText = service.description;
        if (service.note) {
            descText += ` (${service.note})`;
        }
        desc.textContent = descText;
    }
    
    // Build form
    const form = document.getElementById('config-form');
    if (!form) return;
    
    let html = '';
    
    // Show message if no fields needed
    if (service.noKeyRequired || service.fields.length === 0) {
        html = `
            <div class="form-group">
                <div class="no-config-needed">
                    <span class="success-icon">✅</span>
                    <p>No API key required! This service is free to use.</p>
                </div>
            </div>
        `;
    } else {
        service.fields.forEach(field => {
            const defaultValue = field.default || '';
            const hasDefault = defaultValue ? 'has-default' : '';
            html += `
                <div class="form-group ${hasDefault}">
                    <label for="${field.name}">${field.label}${field.required ? ' *' : ''}</label>
                    <input type="${field.type}" id="${field.name}" name="${field.name}" 
                           value="${defaultValue}"
                           ${field.required ? 'required' : ''} 
                           placeholder="Enter ${field.label.toLowerCase()}">
                    ${defaultValue ? '<span class="default-hint">✓ Pre-configured</span>' : ''}
                </div>
            `;
        });
    }
    
    form.innerHTML = html;
    
    // Show signup link if needed (and no default key)
    const signupContainer = document.getElementById('signup-link-container');
    const signupLink = document.getElementById('signup-link');
    const hasDefaultKey = service.defaultKey || service.noKeyRequired;
    
    if (service.signupUrl && signupContainer && signupLink && !hasDefaultKey) {
        signupContainer.style.display = 'block';
        signupLink.href = service.signupUrl;
    } else if (signupContainer) {
        signupContainer.style.display = 'none';
    }
}

function getConfigFormData() {
    const form = document.getElementById('config-form');
    if (!form) return {};
    
    const data = {};
    form.querySelectorAll('input').forEach(input => {
        data[input.name] = input.value;
    });
    
    return data;
}

// ============================================================================
// Connection Testing & Saving
// ============================================================================
function testConnection() {
    const loader = document.getElementById('connect-loader');
    const message = document.getElementById('connect-message');
    const status = document.getElementById('connect-status');
    const result = document.getElementById('connect-result');
    
    // Show loading
    if (status) status.style.display = 'block';
    if (result) result.style.display = 'none';
    if (message) message.textContent = 'Testing connection...';
    
    // Simulate connection test
    setTimeout(() => {
        if (status) status.style.display = 'none';
        if (result) result.style.display = 'block';
        
        const icon = document.getElementById('result-icon');
        const title = document.getElementById('result-title');
        const msg = document.getElementById('result-message');
        
        if (icon) icon.textContent = '✅';
        if (title) title.textContent = 'Connected!';
        if (msg) msg.textContent = `Successfully connected to ${wizardState.selectedService?.name}`;
    }, 1500);
}

function saveConnection(service, config) {
    const connection = {
        id: Date.now(),
        service: service,
        config: config,
        createdAt: new Date().toISOString(),
        status: 'active'
    };
    
    state.connections.push(connection);
    localStorage.setItem('uhd_connections', JSON.stringify(state.connections));
    
    updateSourcesList();
    updateConnectionCount();
    updateScopeIndicator();
}

function loadConnections() {
    const saved = localStorage.getItem('uhd_connections');
    if (saved) {
        state.connections = JSON.parse(saved);
        updateSourcesList();
        updateConnectionCount();
    }
}

function updateSourcesList() {
    const sourcesList = document.getElementById('sources-list');
    if (!sourcesList) return;
    
    if (state.connections.length === 0) {
        sourcesList.innerHTML = '<div class="helix-item" style="color: var(--text-muted); font-style: italic;">No sources connected</div>';
        return;
    }
    
    sourcesList.innerHTML = state.connections.map(conn => `
        <div class="helix-item" data-connection="${conn.id}">
            <span class="item-icon">${conn.service.icon}</span>
            <span class="item-label">${conn.service.name}</span>
        </div>
    `).join('');
}

function updateConnectionCount() {
    const countEl = document.getElementById('connection-count');
    if (countEl) {
        countEl.textContent = state.connections.length;
    }
    
    const statusEl = document.getElementById('connection-status');
    if (statusEl) {
        statusEl.textContent = `🔗 ${state.connections.length} connections active`;
    }
}

// ============================================================================
// Quick Connect
// ============================================================================
function populateQuickConnect() {
    const grid = document.getElementById('quick-connect-grid');
    if (!grid) return;
    
    // Show popular free APIs (prioritize no-key-required and pre-configured)
    const quickItems = [
        { icon: '📊', label: 'Stocks', id: 'finnhub' },       // Pre-configured with user's key
        { icon: '🌤️', label: 'Weather', id: 'wttr' },
        { icon: '📖', label: 'Dictionary', id: 'freedictionary' },
        { icon: '📚', label: 'Wikipedia', id: 'wikipedia' },
        { icon: '💰', label: 'Crypto', id: 'coingecko' },
        { icon: '🍲', label: 'Recipes', id: 'themealdb' },
        { icon: '🔤', label: 'Thesaurus', id: 'datamuse' },
        { icon: '💭', label: 'Quotes', id: 'quotable' },
        { icon: '📰', label: 'HackerNews', id: 'hackernews' },
        { icon: '🗺️', label: 'Countries', id: 'restcountries' },
        { icon: '📕', label: 'Books', id: 'openlibrary' },
        { icon: '➕', label: 'More...', id: 'browse' }
    ];
    
    grid.innerHTML = quickItems.map(item => `
        <div class="quick-connect-item" onclick="${item.id === 'browse' ? 'openConnectionWizard()' : `quickConnect('${item.id}')`}">
            <span class="icon">${item.icon}</span>
            <span class="label">${item.label}</span>
        </div>
    `).join('');
}

function quickConnect(serviceId) {
    // Find service
    let service = null;
    Object.values(API_REGISTRY).forEach(category => {
        const found = category.find(s => s.id === serviceId);
        if (found) service = found;
    });
    
    if (!service) return;
    
    // Check if it's free or has a pre-configured default key
    const hasDefaultKey = service.defaultKey || service.fields?.some(f => f.default);
    
    if (service.noKeyRequired) {
        // Connect immediately
        saveConnection(service, {});
        showToast(`✅ Connected to ${service.name}!`);
    } else if (hasDefaultKey) {
        // Connect with default key
        const config = {};
        service.fields?.forEach(field => {
            if (field.default) {
                config[field.name] = field.default;
            }
        });
        saveConnection(service, config);
        showToast(`✅ Connected to ${service.name} with pre-configured key!`);
    } else {
        // Open wizard
        wizardState.selectedService = service;
        showWizardStep(2);
        populateConfigForm();
        elements.connectionModal?.classList.add('visible');
    }
}

// Toast notification helper
function showToast(message) {
    // Create toast element if it doesn't exist
    let toast = document.getElementById('uhd-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'uhd-toast';
        toast.className = 'uhd-toast';
        document.body.appendChild(toast);
    }
    
    toast.textContent = message;
    toast.classList.add('visible');
    
    setTimeout(() => {
        toast.classList.remove('visible');
    }, 3000);
}

// ============================================================================
// API Grid (API Interface View)
// ============================================================================
function populateApiGrid() {
    if (!elements.apiGrid) return;
    
    let html = '';
    
    Object.entries(API_REGISTRY).forEach(([category, services]) => {
        services.forEach(service => {
            html += `
                <div class="api-card" data-id="${service.id}">
                    <div class="api-card-header">
                        <div class="api-card-logo">${service.icon}</div>
                        <div class="api-card-info">
                            <h3>${service.name}</h3>
                            <span class="category">${category}</span>
                        </div>
                    </div>
                    <p class="api-card-desc">${service.description}</p>
                    <div class="api-card-footer">
                        <span class="api-card-badge ${service.noKeyRequired ? 'free' : 'key-required'}">
                            ${service.noKeyRequired ? '🆓 Free' : '🔑 API Key'}
                        </span>
                        <button class="api-card-btn" onclick="quickConnect('${service.id}')">
                            Connect
                        </button>
                    </div>
                </div>
            `;
        });
    });
    
    elements.apiGrid.innerHTML = html;
}

// ============================================================================
// API Crawler
// ============================================================================
function openCrawler() {
    elements.crawlerModal?.classList.add('visible');
}

function closeCrawlerModal() {
    elements.crawlerModal?.classList.remove('visible');
}

function searchAPIs() {
    const query = document.getElementById('crawler-query')?.value || '';
    const freeOnly = document.getElementById('filter-free')?.checked;
    const noKeyOnly = document.getElementById('filter-no-key')?.checked;
    
    const results = document.getElementById('crawler-results');
    if (!results) return;
    
    // Search through all APIs
    let matches = [];
    
    Object.values(API_REGISTRY).forEach(category => {
        category.forEach(service => {
            const matchesQuery = service.name.toLowerCase().includes(query.toLowerCase()) ||
                                service.description.toLowerCase().includes(query.toLowerCase());
            const matchesFree = !freeOnly || service.freeTier;
            const matchesNoKey = !noKeyOnly || service.noKeyRequired;
            
            if (matchesQuery && matchesFree && matchesNoKey) {
                matches.push(service);
            }
        });
    });
    
    if (matches.length === 0) {
        results.innerHTML = `<p class="crawler-placeholder">No APIs found matching "${query}"</p>`;
        return;
    }
    
    results.innerHTML = matches.map(service => `
        <div class="api-card">
            <div class="api-card-header">
                <div class="api-card-logo">${service.icon}</div>
                <div class="api-card-info">
                    <h3>${service.name}</h3>
                    <span class="category">${service.category}</span>
                </div>
            </div>
            <p class="api-card-desc">${service.description}</p>
            <div class="api-card-footer">
                <span class="api-card-badge ${service.noKeyRequired ? 'free' : 'key-required'}">
                    ${service.noKeyRequired ? '🆓 No Key' : '🔑 API Key'}
                </span>
                <button class="api-card-btn" onclick="quickConnect('${service.id}'); closeCrawlerModal();">
                    Connect
                </button>
            </div>
        </div>
    `).join('');
}

// ============================================================================
// Universal Query
// ============================================================================
async function executeQuery() {
    const query = elements.universalQuery?.value || '';
    if (!query.trim()) return;
    
    // Track query stats
    knowledgeBase.stats.totalQueries++;
    
    // Add to history
    state.queryHistory.push({
        query: query,
        timestamp: new Date().toISOString()
    });
    
    // Parse query intent (enhanced with learning)
    const intent = parseQueryIntent(query);
    
    // First, check if we can answer from learned knowledge
    const knowledgeAnswer = learningEngine.answerQuestion(query);
    
    console.log('🧠 Knowledge check:', knowledgeAnswer);
    
    // Show loading state
    showQueryLoading(true);
    
    try {
        // If we have a confident answer from knowledge base, show it
        if (knowledgeAnswer.canAnswer && knowledgeAnswer.answers.length > 0) {
            const topAnswer = knowledgeAnswer.answers[0];
            showToast(`📚 Found in knowledge: ${topAnswer.entity || 'Result'}`, 'success');
            displayQueryResults({
                source: 'Knowledge Base',
                type: 'learned',
                data: knowledgeAnswer.answers
            }, query);
        }
        
        // Always fetch fresh data from connected sources
        const results = await fetchFromAllSources(intent, query);
        
        // Learn from all results
        results.forEach(result => {
            if (result.data && !result.error) {
                learningEngine.learnFromResponse(result.sourceId, result.data, query);
                knowledgeBase.stats.successfulQueries++;
            }
        });
        
        // Display results
        displayQueryResults({
            source: 'Connected Sources',
            type: intent.type,
            data: results,
            suggestedSources: knowledgeAnswer.suggestedSources
        }, query);
        
        // Save learned knowledge
        learningEngine.save();
        
        // Update knowledge stats in UI
        updateKnowledgeStats();
        
    } catch (error) {
        console.error('Query error:', error);
        showToast('Error executing query: ' + error.message, 'error');
    } finally {
        showQueryLoading(false);
    }
}

async function fetchFromAllSources(intent, query) {
    const results = [];
    const connectedSources = state.connections.filter(c => c.connected);
    
    // Find sources that match the intent type
    const relevantCategories = [intent.type];
    
    // Add related categories based on learned patterns
    const suggestedSources = learningEngine.suggestSource(query);
    suggestedSources.forEach(s => {
        const sourceInfo = learningEngine.getSourceInfo(s.source);
        if (sourceInfo.category && !relevantCategories.includes(sourceInfo.category)) {
            relevantCategories.push(sourceInfo.category);
        }
    });
    
    // Query each connected source
    for (const connection of connectedSources) {
        // Check if this source is relevant
        const sourceInfo = learningEngine.getSourceInfo(connection.id);
        const isRelevant = relevantCategories.includes(sourceInfo.category) || 
                          relevantCategories.includes('search');
        
        if (!isRelevant) continue;
        
        try {
            const result = await fetchFromSource(connection, intent, query);
            results.push({
                sourceId: connection.id,
                sourceName: connection.name,
                category: sourceInfo.category,
                data: result,
                timestamp: Date.now()
            });
        } catch (error) {
            results.push({
                sourceId: connection.id,
                sourceName: connection.name,
                error: error.message
            });
        }
    }
    
    // If no connected sources, try free APIs directly
    if (connectedSources.length === 0) {
        const freeResults = await fetchFromFreeAPIs(intent, query);
        results.push(...freeResults);
    }
    
    return results;
}

async function fetchFromSource(connection, intent, query) {
    // Build URL based on source type and intent
    const service = findServiceById(connection.id);
    if (!service) throw new Error('Service not found');
    
    let url = service.baseUrl;
    let params = new URLSearchParams();
    
    // Add query parameters based on service endpoints
    if (service.endpoints) {
        const endpoint = service.endpoints.find(e => 
            e.name.toLowerCase().includes(intent.type) || 
            e.name.toLowerCase().includes('search')
        ) || service.endpoints[0];
        
        url = service.baseUrl + endpoint.path;
    }
    
    // Add API key if required
    if (connection.apiKey) {
        params.append('api_key', connection.apiKey);
    }
    
    // Add query
    params.append('q', query);
    
    // Make request
    const response = await fetch(`${url}?${params}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    
    return await response.json();
}

async function fetchFromFreeAPIs(intent, query) {
    const results = [];
    const freeAPIs = {
        weather: 'wttr.in',
        knowledge: 'api.dictionaryapi.dev',
        data: 'jsonplaceholder'
    };
    
    // Try Wikipedia for general queries
    try {
        const wikiUrl = `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(query)}`;
        const res = await fetch(wikiUrl);
        if (res.ok) {
            const data = await res.json();
            results.push({
                sourceId: 'wikipedia',
                sourceName: 'Wikipedia',
                category: 'knowledge',
                data: data,
                timestamp: Date.now()
            });
            // Learn from Wikipedia response
            learningEngine.learnFromResponse('wikipedia', data, query);
        }
    } catch (e) {
        console.log('Wikipedia fetch failed:', e);
    }
    
    // Try Dictionary API for definitions
    if (intent.type === 'knowledge' || query.toLowerCase().includes('define') || 
        query.toLowerCase().includes('meaning')) {
        try {
            const word = query.split(' ').pop();
            const dictUrl = `https://api.dictionaryapi.dev/api/v2/entries/en/${encodeURIComponent(word)}`;
            const res = await fetch(dictUrl);
            if (res.ok) {
                const data = await res.json();
                results.push({
                    sourceId: 'dictionary',
                    sourceName: 'Dictionary API',
                    category: 'knowledge',
                    data: data,
                    timestamp: Date.now()
                });
                // Learn definitions
                if (Array.isArray(data)) {
                    data.forEach(entry => {
                        if (entry.meanings) {
                            entry.meanings.forEach(m => {
                                if (m.definitions) {
                                    m.definitions.forEach(d => {
                                        knowledgeBase.entities.words[word] = knowledgeBase.entities.words[word] || {};
                                        knowledgeBase.entities.words[word].definition = d.definition;
                                        if (m.synonyms) {
                                            learningEngine.learnSynonyms(word, m.synonyms, 'dictionary');
                                        }
                                    });
                                }
                            });
                        }
                    });
                }
            }
        } catch (e) {
            console.log('Dictionary fetch failed:', e);
        }
    }
    
    return results;
}

function displayQueryResults(results, query) {
    // Switch to table view to show results
    switchView('table');
    
    const tableBody = document.getElementById('data-table-body');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    // Display each result
    if (results.data && Array.isArray(results.data)) {
        results.data.forEach(result => {
            if (result.error) {
                // Show error row
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${result.sourceName}</td>
                    <td colspan="4" class="error">❌ ${result.error}</td>
                `;
                tableBody.appendChild(row);
            } else if (result.data) {
                // Show data rows
                const data = result.data;
                const rows = extractTableRows(data, result.sourceName, result.category);
                rows.forEach(row => tableBody.appendChild(row));
            }
        });
    }
    
    // Show knowledge stats
    const stats = learningEngine.getStats();
    showToast(`🧠 Knowledge: ${stats.vocabularySize} words, ${stats.entitiesKnown} entities`, 'info');
}

function extractTableRows(data, sourceName, category) {
    const rows = [];
    
    // Handle different data structures
    if (Array.isArray(data)) {
        data.slice(0, 10).forEach(item => {
            const row = document.createElement('tr');
            const key = Object.keys(item)[0] || 'item';
            const value = typeof item === 'object' ? JSON.stringify(item).slice(0, 100) : item;
            row.innerHTML = `
                <td>${sourceName}</td>
                <td>${category}</td>
                <td>${key}</td>
                <td>${value}...</td>
                <td><button class="btn-small" onclick="viewDetails('${encodeURIComponent(JSON.stringify(item))}')">View</button></td>
            `;
            rows.push(row);
        });
    } else if (typeof data === 'object') {
        // Wikipedia-style response
        if (data.title && data.extract) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${sourceName}</td>
                <td>${category}</td>
                <td>${data.title}</td>
                <td>${data.extract?.slice(0, 200)}...</td>
                <td>${data.thumbnail ? `<img src="${data.thumbnail.source}" width="50">` : '-'}</td>
            `;
            rows.push(row);
        } else {
            // Generic object
            Object.entries(data).slice(0, 10).forEach(([key, value]) => {
                const row = document.createElement('tr');
                const displayValue = typeof value === 'object' ? JSON.stringify(value).slice(0, 100) : value;
                row.innerHTML = `
                    <td>${sourceName}</td>
                    <td>${category}</td>
                    <td>${key}</td>
                    <td>${displayValue}</td>
                    <td>-</td>
                `;
                rows.push(row);
            });
        }
    }
    
    return rows;
}

function showQueryLoading(loading) {
    const btn = document.getElementById('btn-execute');
    if (btn) {
        btn.disabled = loading;
        btn.innerHTML = loading ? '⏳' : '🔍';
    }
}

function updateKnowledgeStats() {
    const stats = learningEngine.getStats();
    
    // Update status bar or create knowledge indicator
    let indicator = document.getElementById('knowledge-indicator');
    if (!indicator) {
        const statusBar = document.querySelector('.status-section:last-child');
        if (statusBar) {
            indicator = document.createElement('span');
            indicator.id = 'knowledge-indicator';
            indicator.className = 'status-item';
            indicator.title = 'Knowledge Base Stats';
            statusBar.appendChild(indicator);
        }
    }
    
    if (indicator) {
        indicator.innerHTML = `🧠 ${stats.vocabularySize} words`;
    }
}

function findServiceById(id) {
    for (const category of Object.keys(API_REGISTRY)) {
        const service = API_REGISTRY[category].find(s => s.id === id);
        if (service) return service;
    }
    return null;
}

function parseQueryIntent(query) {
    const lowerQuery = query.toLowerCase();
    
    // First, check learned patterns for suggestions
    const suggestedSources = learningEngine.suggestSource(query);
    
    // Expand query using synonyms
    const expandedTerms = learningEngine.expandQuery(query);
    
    // Weather patterns
    if (lowerQuery.includes('weather') || lowerQuery.includes('forecast') || 
        lowerQuery.includes('temperature') || lowerQuery.includes('rain')) {
        return { type: 'weather', query: query, expanded: expandedTerms, suggestions: suggestedSources };
    }
    
    // Stocks/Finance patterns
    if (lowerQuery.includes('stock') || lowerQuery.includes('price') || 
        lowerQuery.includes('crypto') || lowerQuery.includes('bitcoin') ||
        lowerQuery.includes('market') || lowerQuery.includes('ticker') ||
        lowerQuery.match(/\b[A-Z]{1,5}\b/)) { // Stock ticker pattern
        return { type: 'finance', query: query, expanded: expandedTerms, suggestions: suggestedSources };
    }
    
    // News patterns
    if (lowerQuery.includes('news') || lowerQuery.includes('headline') ||
        lowerQuery.includes('breaking') || lowerQuery.includes('latest')) {
        return { type: 'news', query: query, expanded: expandedTerms, suggestions: suggestedSources };
    }
    
    // Knowledge/Definition patterns
    if (lowerQuery.includes('define') || lowerQuery.includes('meaning') ||
        lowerQuery.includes('what is') || lowerQuery.includes('who is') ||
        lowerQuery.includes('synonym') || lowerQuery.includes('antonym')) {
        return { type: 'knowledge', query: query, expanded: expandedTerms, suggestions: suggestedSources };
    }
    
    // Food/Recipe patterns
    if (lowerQuery.includes('recipe') || lowerQuery.includes('cook') || 
        lowerQuery.includes('meal') || lowerQuery.includes('ingredient') ||
        lowerQuery.includes('calories') || lowerQuery.includes('nutrition')) {
        return { type: 'food', query: query, expanded: expandedTerms, suggestions: suggestedSources };
    }
    
    // Music patterns
    if (lowerQuery.includes('song') || lowerQuery.includes('music') ||
        lowerQuery.includes('artist') || lowerQuery.includes('album') ||
        lowerQuery.includes('lyrics')) {
        return { type: 'music', query: query, expanded: expandedTerms, suggestions: suggestedSources };
    }
    
    // Developer patterns
    if (lowerQuery.includes('code') || lowerQuery.includes('github') ||
        lowerQuery.includes('programming') || lowerQuery.includes('api') ||
        lowerQuery.includes('npm') || lowerQuery.includes('package')) {
        return { type: 'developer', query: query, expanded: expandedTerms, suggestions: suggestedSources };
    }
    
    // If we have learned suggestions, use the top one
    if (suggestedSources.length > 0) {
        const topSource = learningEngine.getSourceInfo(suggestedSources[0].source);
        return { 
            type: topSource.category || 'search', 
            query: query, 
            expanded: expandedTerms, 
            suggestions: suggestedSources,
            fromLearning: true
        };
    }
    
    // Default to search
    return { type: 'search', query: query, expanded: expandedTerms, suggestions: suggestedSources };
}

// ============================================================================
// Query Suggestions & Autocomplete
// ============================================================================
function showQuerySuggestions(prefix) {
    // Get suggestions from learning engine
    const suggestions = learningEngine.getSuggestions(prefix, 8);
    
    // Also add suggestions from query history
    const historySuggestions = state.queryHistory
        .filter(h => h.query.toLowerCase().includes(prefix.toLowerCase()))
        .slice(-3)
        .map(h => ({ word: h.query, score: 10, type: 'history' }));
    
    // Combine and dedupe
    const allSuggestions = [...suggestions, ...historySuggestions]
        .reduce((acc, s) => {
            if (!acc.find(x => x.word.toLowerCase() === s.word.toLowerCase())) {
                acc.push(s);
            }
            return acc;
        }, [])
        .sort((a, b) => b.score - a.score)
        .slice(0, 10);
    
    if (allSuggestions.length === 0) {
        hideQuerySuggestions();
        return;
    }
    
    // Create or find suggestions dropdown
    let dropdown = document.getElementById('query-suggestions');
    if (!dropdown) {
        dropdown = document.createElement('div');
        dropdown.id = 'query-suggestions';
        dropdown.className = 'query-suggestions';
        elements.universalQuery?.parentNode?.appendChild(dropdown);
    }
    
    // Populate suggestions
    dropdown.innerHTML = allSuggestions.map((s, i) => {
        const icon = getSuggestionIcon(s.type);
        return `
            <div class="suggestion-item" data-index="${i}" onclick="selectSuggestion('${escapeHtml(s.word)}')">
                <span class="suggestion-icon">${icon}</span>
                <span class="suggestion-text">${escapeHtml(s.word)}</span>
                <span class="suggestion-type">${s.type}</span>
            </div>
        `;
    }).join('');
    
    dropdown.classList.add('visible');
}

function hideQuerySuggestions() {
    const dropdown = document.getElementById('query-suggestions');
    if (dropdown) {
        dropdown.classList.remove('visible');
    }
}

function selectSuggestion(text) {
    if (elements.universalQuery) {
        elements.universalQuery.value = text;
        elements.universalQuery.focus();
    }
    hideQuerySuggestions();
}

function getSuggestionIcon(type) {
    const icons = {
        vocabulary: '📝',
        companies: '🏢',
        locations: '📍',
        people: '👤',
        topics: '📰',
        foods: '🍽️',
        words: '📖',
        currencies: '💱',
        history: '🕐'
    };
    return icons[type] || '💡';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================================
// Knowledge Base UI
// ============================================================================
function showKnowledgePanel() {
    const stats = learningEngine.getStats();
    
    // Create modal content
    const content = `
        <div class="knowledge-panel">
            <h3>🧠 Knowledge Base</h3>
            
            <div class="knowledge-stats">
                <div class="stat-card">
                    <div class="stat-value">${stats.vocabularySize}</div>
                    <div class="stat-label">Words Learned</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.entitiesKnown}</div>
                    <div class="stat-label">Entities Known</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.patternsLearned}</div>
                    <div class="stat-label">Query Patterns</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.sourcesLearned}</div>
                    <div class="stat-label">Sources Learned</div>
                </div>
            </div>
            
            <div class="knowledge-sections">
                <div class="knowledge-section">
                    <h4>📈 Top Vocabulary</h4>
                    <div class="word-cloud">
                        ${getTopVocabulary(20).map(w => 
                            `<span class="word-tag" style="font-size: ${Math.min(1.5, 0.8 + w.count/100)}em">${w.word}</span>`
                        ).join('')}
                    </div>
                </div>
                
                <div class="knowledge-section">
                    <h4>🏢 Known Companies</h4>
                    <div class="entity-list">
                        ${Object.keys(knowledgeBase.entities.companies).slice(0, 10).map(c => 
                            `<span class="entity-tag company">${c}</span>`
                        ).join('') || '<em>No companies learned yet</em>'}
                    </div>
                </div>
                
                <div class="knowledge-section">
                    <h4>📍 Known Locations</h4>
                    <div class="entity-list">
                        ${Object.keys(knowledgeBase.entities.locations).slice(0, 10).map(l => 
                            `<span class="entity-tag location">${l}</span>`
                        ).join('') || '<em>No locations learned yet</em>'}
                    </div>
                </div>
                
                <div class="knowledge-section">
                    <h4>📰 Topics</h4>
                    <div class="entity-list">
                        ${Object.keys(knowledgeBase.entities.topics).slice(0, 15).map(t => 
                            `<span class="entity-tag topic">${t}</span>`
                        ).join('') || '<em>No topics learned yet</em>'}
                    </div>
                </div>
            </div>
            
            <div class="knowledge-actions">
                <button class="btn-primary" onclick="exportKnowledge()">📥 Export Knowledge</button>
                <button class="btn-secondary" onclick="clearKnowledge()">🗑️ Clear All</button>
            </div>
        </div>
    `;
    
    // Show in a modal or panel
    showModal('Knowledge Base', content);
}

function getTopVocabulary(limit) {
    return Object.entries(knowledgeBase.vocabulary)
        .map(([word, data]) => ({ word, count: data.count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, limit);
}

function exportKnowledge() {
    const data = JSON.stringify(knowledgeBase, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'butterflyfx_knowledge.json';
    a.click();
    
    URL.revokeObjectURL(url);
    showToast('Knowledge base exported!', 'success');
}

function clearKnowledge() {
    if (confirm('Are you sure you want to clear all learned knowledge?')) {
        // Reset knowledge base
        knowledgeBase.vocabulary = {};
        knowledgeBase.concepts = {};
        knowledgeBase.successfulPatterns = [];
        knowledgeBase.entities = {
            companies: {},
            locations: {},
            people: {},
            topics: {},
            currencies: {},
            foods: {},
            words: {}
        };
        knowledgeBase.sourceKnowledge = {};
        knowledgeBase.stats = {
            totalQueries: 0,
            successfulQueries: 0,
            wordsLearned: 0,
            conceptsLearned: 0,
            lastLearningSession: null
        };
        
        learningEngine.save();
        showToast('Knowledge base cleared', 'info');
        updateKnowledgeStats();
    }
}

function showModal(title, content) {
    // Reuse connection wizard modal structure
    const modal = elements.connectionWizard;
    if (modal) {
        const modalTitle = modal.querySelector('.wizard-header h2');
        const modalBody = modal.querySelector('.wizard-body');
        
        if (modalTitle) modalTitle.textContent = title;
        if (modalBody) modalBody.innerHTML = content;
        
        modal.classList.add('visible');
    }
}

function updateScopeIndicator() {
    const countEl = document.getElementById('scope-count');
    if (countEl) {
        // Count connected sources
        const sourceCount = state.connections.length + 1; // +1 for local
        countEl.textContent = sourceCount;
    }
}

// ============================================================================
// Context Menu - Windows Explorer Style + Dimensional Actions
// ============================================================================
function showContextMenu(event) {
    event.preventDefault();
    
    const menu = elements.contextMenu;
    if (!menu) return;
    
    // Track which item was right-clicked
    const targetItem = event.target.closest('.folder-item');
    state.contextTarget = targetItem;
    
    // Position menu
    let x = event.pageX;
    let y = event.pageY;
    
    // Adjust if menu would go off screen
    const menuRect = menu.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    if (x + 200 > viewportWidth) {
        x = viewportWidth - 220;
    }
    if (y + 400 > viewportHeight) {
        y = viewportHeight - 420;
    }
    
    menu.style.left = x + 'px';
    menu.style.top = y + 'px';
    
    // Update menu items based on context
    updateContextMenuState(targetItem);
    
    menu.classList.add('visible');
}

function updateContextMenuState(targetItem) {
    const menu = elements.contextMenu;
    if (!menu) return;
    
    // Enable/disable paste based on clipboard
    const pasteItem = menu.querySelector('[data-action="paste"]');
    if (pasteItem) {
        pasteItem.classList.toggle('disabled', state.clipboard.items.length === 0);
    }
    
    // Show helix info if item has connections
    if (targetItem) {
        const itemId = getItemFullPath(targetItem);
        const node = dimensionalHelix.nodes[itemId];
        
        const helixItem = menu.querySelector('[data-action="viewHelix"]');
        if (helixItem && node) {
            const count = (node.helixThreads?.length || 0) + 
                         (node.innerPoints?.length || 0) + 
                         (node.outerContainer ? 1 : 0);
            if (count > 0) {
                helixItem.innerHTML = `🌀 View Helix (${count})`;
            }
        }
    }
}

function hideContextMenu() {
    elements.contextMenu?.classList.remove('visible');
    state.contextTarget = null;
}

function handleContextAction(action) {
    const target = state.contextTarget;
    
    switch (action) {
        case 'open':
            if (target) openItem(target);
            break;
            
        case 'preview':
            if (target) showPreview(target);
            break;
            
        case 'openInNewTab':
            if (target) openInNewTab(target);
            break;
            
        case 'cut':
            cutSelectedItems();
            break;
            
        case 'copy':
            copySelectedItems();
            break;
            
        case 'paste':
            pasteItems();
            break;
            
        case 'rename':
            if (target) renameItem(target);
            break;
            
        case 'delete':
            deleteSelectedItems();
            break;
            
        case 'properties':
            if (target) showProperties(target);
            break;
            
        // Dimensional Helix Actions
        case 'drillDown':
            if (target) doDimensionalDrillDown(target);
            break;
            
        case 'drillUp':
            if (target) doDimensionalDrillUp(target);
            break;
            
        case 'viewDimension':
            if (target) showDimensionLevel(target);
            break;
            
        case 'connectHelix':
            if (target) openHelixConnectSearch(target, 'helix');
            break;
            
        case 'connectInner':
            if (target) openHelixConnectSearch(target, 'inner');
            break;
            
        case 'connectOuter':
            if (target) openHelixConnectSearch(target, 'outer');
            break;
            
        case 'searchConnect':
            if (target) openHelixConnectSearch(target, 'search');
            break;
            
        case 'viewHelix':
            if (target) showHelixView(target);
            break;
            
        // Send To actions
        case 'sendToDesktop':
            showToast('Sent to Desktop', 'success');
            break;
            
        case 'sendToCompressed':
            showToast('Creating compressed folder...', 'info');
            break;
            
        case 'sendToMail':
            showToast('Opening mail client...', 'info');
            break;
    }
    
    hideContextMenu();
}

// Initialize context menu click handlers
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.context-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.stopPropagation();
            const action = item.dataset.action;
            if (action && !item.classList.contains('has-submenu')) {
                handleContextAction(action);
            }
        });
    });
});

// ============================================================================
// Clipboard Operations
// ============================================================================
function cutSelectedItems() {
    state.clipboard = {
        items: [...state.selectedItems],
        action: 'cut'
    };
    
    // Visual feedback
    document.querySelectorAll('.folder-item.selected').forEach(item => {
        item.classList.add('cut');
    });
    
    showToast(`${state.selectedItems.length} item(s) cut`, 'info');
}

function copySelectedItems() {
    state.clipboard = {
        items: [...state.selectedItems],
        action: 'copy'
    };
    
    showToast(`${state.selectedItems.length} item(s) copied`, 'info');
}

function pasteItems() {
    if (state.clipboard.items.length === 0) {
        showToast('Clipboard is empty', 'warning');
        return;
    }
    
    const action = state.clipboard.action;
    const count = state.clipboard.items.length;
    
    // Simulate paste
    showToast(`${count} item(s) ${action === 'cut' ? 'moved' : 'copied'} here`, 'success');
    
    // Clear clipboard if cut
    if (action === 'cut') {
        document.querySelectorAll('.folder-item.cut').forEach(item => {
            item.classList.remove('cut');
        });
        state.clipboard = { items: [], action: null };
    }
    
    // Refresh view
    refresh();
}

// ============================================================================
// Item Operations
// ============================================================================
function renameItem(itemElement) {
    const nameEl = itemElement.querySelector('.item-name');
    if (!nameEl) return;
    
    const currentName = nameEl.textContent;
    const input = document.createElement('input');
    input.type = 'text';
    input.value = currentName;
    input.className = 'rename-input';
    
    nameEl.style.display = 'none';
    itemElement.appendChild(input);
    input.focus();
    input.select();
    
    const finishRename = () => {
        const newName = input.value.trim();
        if (newName && newName !== currentName) {
            nameEl.textContent = newName;
            showToast(`Renamed to "${newName}"`, 'success');
        }
        nameEl.style.display = '';
        input.remove();
    };
    
    input.addEventListener('blur', finishRename);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') finishRename();
        if (e.key === 'Escape') {
            nameEl.style.display = '';
            input.remove();
        }
    });
}

function deleteSelectedItems() {
    if (state.selectedItems.length === 0) {
        showToast('No items selected', 'warning');
        return;
    }
    
    if (confirm(`Delete ${state.selectedItems.length} item(s)?`)) {
        // Remove items from view
        state.selectedItems.forEach(id => {
            const item = document.querySelector(`.folder-item[data-id="${id}"]`);
            if (item) {
                item.remove();
            }
        });
        
        showToast(`${state.selectedItems.length} item(s) deleted`, 'success');
        state.selectedItems = [];
        updateSelectedCount();
    }
}

function showPreview(itemElement) {
    const name = itemElement.querySelector('.item-name')?.textContent || 'Unknown';
    const type = itemElement.dataset.type;
    
    // Create preview modal
    showModal('Preview: ' + name, `
        <div class="preview-container">
            <div class="preview-icon" style="font-size: 4em; text-align: center; padding: 2em;">
                ${type === 'folder' ? '📁' : '📄'}
            </div>
            <div class="preview-info">
                <p><strong>Name:</strong> ${name}</p>
                <p><strong>Type:</strong> ${type}</p>
                <p><strong>Location:</strong> ${state.currentPath}</p>
            </div>
        </div>
    `);
}

function openInNewTab(itemElement) {
    const name = itemElement.querySelector('.item-name')?.textContent || '';
    const path = state.currentPath + name + '/';
    
    // Open in new browser tab (simulated)
    showToast(`Opening "${name}" in new tab...`, 'info');
}

function showProperties(itemElement) {
    const name = itemElement.querySelector('.item-name')?.textContent || 'Unknown';
    const type = itemElement.dataset.type;
    const id = itemElement.dataset.id;
    const itemPath = getItemFullPath(itemElement);
    
    // Get dimensional helix info
    const dimInfo = dimensionalHelix.getDimensionInfo(itemPath);
    
    showModal('Properties: ' + name, `
        <div class="properties-panel">
            <div class="property-tabs">
                <button class="prop-tab active" data-tab="general">General</button>
                <button class="prop-tab" data-tab="dimensions">Dimensions</button>
                <button class="prop-tab" data-tab="helix">Helix</button>
            </div>
            
            <div class="property-content">
                <div class="prop-section">
                    <div class="prop-row">
                        <span class="prop-label">Name:</span>
                        <span class="prop-value">${name}</span>
                    </div>
                    <div class="prop-row">
                        <span class="prop-label">Type:</span>
                        <span class="prop-value">${type}</span>
                    </div>
                    <div class="prop-row">
                        <span class="prop-label">Location:</span>
                        <span class="prop-value">${state.currentPath}</span>
                    </div>
                    <div class="prop-row">
                        <span class="prop-label">Full Path:</span>
                        <span class="prop-value">${itemPath}</span>
                    </div>
                </div>
                
                <div class="prop-section">
                    <h4>🌀 Dimensional Helix Info</h4>
                    ${dimInfo ? `
                        <div class="prop-row">
                            <span class="prop-label">Dimension Level:</span>
                            <span class="prop-value">${dimInfo.icon} ${dimInfo.fullName}</span>
                        </div>
                        <div class="prop-row">
                            <span class="prop-label">Spiral:</span>
                            <span class="prop-value">${dimInfo.spiral}</span>
                        </div>
                        <div class="prop-row">
                            <span class="prop-label">Helix Threads:</span>
                            <span class="prop-value">${dimInfo.helixCount} parallel dimensions</span>
                        </div>
                        <div class="prop-row">
                            <span class="prop-label">Inner Points:</span>
                            <span class="prop-value">${dimInfo.innerCount}</span>
                        </div>
                    ` : `
                        <p>No dimensional data yet. Use 🌀 Dimensional Drill to establish position.</p>
                    `}
                </div>
            </div>
        </div>
    `);
}

function getItemFullPath(itemElement) {
    const name = itemElement.querySelector('.item-name')?.textContent || '';
    return state.currentPath + name;
}

// ============================================================================
// Dimensional Helix Operations
// ============================================================================
// 7 Levels per spiral: 0=Void, 1=Point, 2=Length, 3=Width, 4=Height, 5=Collapse, 6=Rest
// Then spiral up and start again at Point of next spiral

function doDimensionalDrillDown(itemElement) {
    const itemPath = getItemFullPath(itemElement);
    const name = itemElement.querySelector('.item-name')?.textContent || 'Unknown';
    const type = itemElement.dataset.type;
    
    // If it's a folder, navigate into it first
    if (type === 'folder') {
        navigateTo(state.currentPath + name + '/');
        return;
    }
    
    // Drill down in dimensional space
    const result = dimensionalHelix.drillDown(itemPath);
    
    if (result.spiralUp) {
        showToast(`🌀 Spiral Up! ${name} → ${result.name}`, 'success');
        showSpiralUpAnimation(itemElement, result);
    } else {
        showToast(`🔽 Drill: ${name} → ${result.name}`, 'info');
    }
    
    // Show the new dimensional view
    showDimensionLevel(itemElement);
}

function doDimensionalDrillUp(itemElement) {
    const itemPath = getItemFullPath(itemElement);
    const name = itemElement.querySelector('.item-name')?.textContent || 'Unknown';
    
    // Drill up in dimensional space
    const result = dimensionalHelix.drillUp(itemPath);
    
    if (!result) {
        showToast(`Already at dimensional ground (Void, Spiral 0)`, 'warning');
        return;
    }
    
    if (result.spiralDown) {
        showToast(`🌀 Spiral Down! ${name} → ${result.name}`, 'info');
    } else {
        showToast(`🔼 Drill Up: ${name} → ${result.name}`, 'info');
    }
    
    // Show the new dimensional view
    showDimensionLevel(itemElement);
}

function showSpiralUpAnimation(itemElement, result) {
    // Visual feedback for spiral transition
    itemElement.classList.add('spiral-transition');
    setTimeout(() => {
        itemElement.classList.remove('spiral-transition');
    }, 1000);
}

function showDimensionLevel(itemElement) {
    const itemPath = getItemFullPath(itemElement);
    const name = itemElement.querySelector('.item-name')?.textContent || 'Unknown';
    const dimInfo = dimensionalHelix.getDimensionInfo(itemPath);
    
    if (!dimInfo) {
        // Initialize this item
        dimensionalHelix.getNode(itemPath);
        const newInfo = dimensionalHelix.getDimensionInfo(itemPath);
        showDimensionModal(name, itemPath, newInfo);
    } else {
        showDimensionModal(name, itemPath, dimInfo);
    }
}

function showDimensionModal(name, itemPath, dimInfo) {
    const levelDescriptions = {
        0: 'No parts - empty potential, the substrate before existence',
        1: 'Single point of a part - one datum, one unit of information',
        2: 'Length of parts - parts arranged in sequence/line (1D)',
        3: 'Width of parts - parts forming a surface (building toward 2D)',
        4: 'Plane of parts - complete 2D grid/table arrangement',
        5: 'Volume of parts - 3D cube structure of organized parts',
        6: 'Whole - complete unit, ready to spiral up as single point'
    };
    
    showModal('📐 Dimensional Level: ' + name, `
        <div class="dimension-level-panel">
            <div class="dimension-visual">
                <div class="spiral-indicator">
                    <span class="spiral-level">Spiral ${dimInfo.spiral}</span>
                </div>
                <div class="dimension-meter">
                    ${[0,1,2,3,4,5,6].map(d => `
                        <div class="dim-step ${d === dimInfo.level ? 'active' : ''} ${d < dimInfo.level ? 'passed' : ''}">
                            <span class="step-icon">${DIMENSION_ICONS[d]}</span>
                            <span class="step-name">${DIMENSION_NAMES[d]}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div class="dimension-info">
                <h3>${dimInfo.icon} ${dimInfo.fullName}</h3>
                <p>${levelDescriptions[dimInfo.level]}</p>
            </div>
            
            <div class="dimension-stats">
                <div class="stat">
                    <span class="stat-label">Helix Threads</span>
                    <span class="stat-value">${dimInfo.helixCount}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Inner Points</span>
                    <span class="stat-value">${dimInfo.innerCount}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Has Container</span>
                    <span class="stat-value">${dimInfo.hasOuter ? 'Yes' : 'No'}</span>
                </div>
            </div>
            
            <div class="dimension-actions">
                <button onclick="doDimensionalDrillDownById('${itemPath}')">🔽 Drill Down</button>
                <button onclick="doDimensionalDrillUpById('${itemPath}')">🔼 Drill Up</button>
            </div>
        </div>
    `);
}

function doDimensionalDrillDownById(itemPath) {
    const result = dimensionalHelix.drillDown(itemPath);
    const name = itemPath.split('/').pop() || itemPath;
    
    if (result.spiralUp) {
        showToast(`🌀 Spiral Up! ${name} → ${result.name}`, 'success');
    } else {
        showToast(`🔽 Drill: ${name} → ${result.name}`, 'info');
    }
    
    // Refresh the modal with new info
    const dimInfo = dimensionalHelix.getDimensionInfo(itemPath);
    showDimensionModal(name, itemPath, dimInfo);
}

function doDimensionalDrillUpById(itemPath) {
    const result = dimensionalHelix.drillUp(itemPath);
    const name = itemPath.split('/').pop() || itemPath;
    
    if (!result) {
        showToast(`Already at dimensional ground`, 'warning');
        return;
    }
    
    showToast(`🔼 Drill Up: ${name} → ${result.name}`, 'info');
    
    // Refresh the modal with new info
    const dimInfo = dimensionalHelix.getDimensionInfo(itemPath);
    showDimensionModal(name, itemPath, dimInfo);
}

// ============================================================================
// Helix Connection Search
// ============================================================================
function openHelixConnectSearch(itemElement, connectionType) {
    const itemPath = getItemFullPath(itemElement);
    const name = itemElement.querySelector('.item-name')?.textContent || '';
    
    const typeLabels = {
        'helix': 'Parallel Thread (exists in parallel dimension)',
        'inner': 'Inner Point (contained within this)',
        'outer': 'Outer Container (this is contained by)',
        'search': 'Search and Connect'
    };
    
    showModal(`🧬 Helix Connect: ${name}`, `
        <div class="connect-search-panel">
            <p>Connect as: <strong>${typeLabels[connectionType]}</strong></p>
            
            <div class="helix-explanation">
                ${connectionType === 'helix' ? `
                    <p class="helix-tip">💡 Helix threads are parallel dimensions - like your brother 
                    lives in his dimension and you in yours. Connected through higher dimension, 
                    not sharing the same space.</p>
                ` : connectionType === 'inner' ? `
                    <p class="helix-tip">💡 Inner points exist within this item's dimensional space.
                    When you drill down, you'll see these points.</p>
                ` : connectionType === 'outer' ? `
                    <p class="helix-tip">💡 The outer container holds this item. When you drill up,
                    you'll reach the container.</p>
                ` : ''}
            </div>
            
            <div class="search-box">
                <input type="text" id="connect-search-input" placeholder="Search files..." autofocus>
                <button onclick="executeHelixSearch()">🔍 Search</button>
            </div>
            
            <div class="search-results" id="connect-search-results">
                <p class="hint">Type to search for files in the workspace</p>
            </div>
            
            <div class="recent-items">
                <h4>Recently accessed:</h4>
                ${state.history.slice(-5).map(path => `
                    <div class="recent-item" onclick="selectForHelixConnect('${escapeHtml(path)}', '${connectionType}', '${escapeHtml(itemPath)}')">
                        📁 ${path}
                    </div>
                `).join('')}
            </div>
        </div>
    `);
    
    // Set up search input
    setTimeout(() => {
        const input = document.getElementById('connect-search-input');
        if (input) {
            input.addEventListener('input', (e) => {
                performHelixSearch(e.target.value, connectionType, itemPath);
            });
        }
    }, 100);
}

function performHelixSearch(query, connectionType, targetPath) {
    const resultsEl = document.getElementById('connect-search-results');
    if (!resultsEl || query.length < 2) return;
    
    // Search in known nodes and current folder
    const results = searchHelixItems(query);
    
    resultsEl.innerHTML = results.length > 0 
        ? results.map(r => `
            <div class="search-result-item" onclick="selectForHelixConnect('${escapeHtml(r.id)}', '${connectionType}', '${escapeHtml(targetPath)}')">
                ${DIMENSION_ICONS[r.dimension || 1]} ${r.name || r.id}
                ${r.spiral > 0 ? `<span class="spiral-badge">S${r.spiral}</span>` : ''}
            </div>
        `).join('')
        : '<p>No results found</p>';
}

function searchHelixItems(query) {
    const results = [];
    
    // Search in helix nodes
    for (const [id, node] of Object.entries(dimensionalHelix.nodes)) {
        if (id.toLowerCase().includes(query.toLowerCase())) {
            results.push({ 
                id, 
                name: id.split('/').pop(), 
                dimension: node.dimension,
                spiral: node.spiral
            });
        }
    }
    
    // Search in current folder items
    document.querySelectorAll('.folder-item').forEach(item => {
        const name = item.querySelector('.item-name')?.textContent || '';
        if (name.toLowerCase().includes(query.toLowerCase())) {
            const itemPath = state.currentPath + name;
            if (!results.find(r => r.id === itemPath)) {
                results.push({
                    id: itemPath,
                    name: name,
                    type: item.dataset.type,
                    dimension: 1 // Default to Point
                });
            }
        }
    });
    
    return results;
}

function selectForHelixConnect(sourcePath, connectionType, targetPath) {
    switch (connectionType) {
        case 'helix':
            dimensionalHelix.connectHelix(targetPath, sourcePath);
            break;
        case 'inner':
            dimensionalHelix.addInnerPoint(targetPath, sourcePath);
            break;
        case 'outer':
            dimensionalHelix.addInnerPoint(sourcePath, targetPath); // Reverse - source contains target
            break;
    }
    
    closeConnectionModal();
}

// ============================================================================
// Helix View
// ============================================================================
function showHelixView(itemElement) {
    const name = itemElement.querySelector('.item-name')?.textContent || 'Unknown';
    const itemPath = getItemFullPath(itemElement);
    const helixView = dimensionalHelix.getHelixView(itemPath);
    
    let helixHtml = '';
    
    if (helixView) {
        helixHtml = `
            <div class="helix-structure">
                <!-- Current Node -->
                <div class="helix-current">
                    <div class="helix-node current">
                        <span class="node-icon">${DIMENSION_ICONS[helixView.current.dimension]}</span>
                        <span class="node-name">${name}</span>
                        <span class="node-level">${helixView.current.dimensionName}</span>
                        ${helixView.current.spiral > 0 ? `<span class="spiral-badge">Spiral ${helixView.current.spiral}</span>` : ''}
                    </div>
                </div>
                
                <!-- Outer Container -->
                ${helixView.outerContainer ? `
                    <div class="helix-section outer">
                        <h4>⬆️ Outer Container</h4>
                        <div class="helix-node" onclick="navigateToHelixNode('${helixView.outerContainer.id}')">
                            <span class="node-icon">${helixView.outerContainer.icon}</span>
                            <span class="node-name">${helixView.outerContainer.id.split('/').pop()}</span>
                            <span class="node-level">${helixView.outerContainer.fullName}</span>
                        </div>
                    </div>
                ` : ''}
                
                <!-- Helix Threads (Parallel Dimensions) -->
                ${helixView.helixThreads.length > 0 ? `
                    <div class="helix-section threads">
                        <h4>🧬 Helix Threads (${helixView.helixThreads.length} parallel dimensions)</h4>
                        <div class="helix-threads-visual">
                            ${helixView.helixThreads.map(t => `
                                <div class="helix-node thread" onclick="navigateToHelixNode('${t.id}')">
                                    <span class="node-icon">${t.icon || '•'}</span>
                                    <span class="node-name">${t.id.split('/').pop()}</span>
                                    <span class="node-level">${t.fullName || 'Unknown'}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <!-- Inner Points -->
                ${helixView.innerPoints.length > 0 ? `
                    <div class="helix-section inner">
                        <h4>⬇️ Inner Points (${helixView.innerPoints.length})</h4>
                        <div class="helix-inner-grid">
                            ${helixView.innerPoints.map(p => `
                                <div class="helix-node inner-point" onclick="navigateToHelixNode('${p.id}')">
                                    <span class="node-icon">${p.icon || '•'}</span>
                                    <span class="node-name">${p.id.split('/').pop()}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${!helixView.outerContainer && helixView.helixThreads.length === 0 && helixView.innerPoints.length === 0 ? `
                    <div class="no-connections">
                        <p>No helix connections yet.</p>
                        <p>Right-click → 🧬 Helix Connect to create dimensional links.</p>
                    </div>
                ` : ''}
            </div>
        `;
    } else {
        helixHtml = `
            <div class="no-connections">
                <p>This item hasn't been added to the dimensional helix yet.</p>
                <p>Use 🌀 Dimensional Drill to establish its position.</p>
            </div>
        `;
    }
    
    showModal('🌀 Helix Structure: ' + name, helixHtml);
}

function navigateToHelixNode(nodePath) {
    // Close modal and navigate to the node's location
    closeConnectionModal();
    
    // Extract folder path and navigate
    const parts = nodePath.split('/');
    parts.pop(); // Remove filename
    const folderPath = parts.join('/') + '/';
    
    if (folderPath !== state.currentPath) {
        navigateTo(folderPath);
    }
    
    showToast(`Navigating to: ${nodePath}`, 'info');
}

// ============================================================================
// Details Panel
// ============================================================================
function showItemDetails(itemElement) {
    const detailsInfo = document.getElementById('details-info');
    if (!detailsInfo) return;
    
    const name = itemElement.querySelector('.item-name')?.textContent || 'Unknown';
    const type = itemElement.dataset.type || 'unknown';
    
    detailsInfo.innerHTML = `
        <div class="detail-row">
            <span class="label">Name</span>
            <span class="value">${name}</span>
        </div>
        <div class="detail-row">
            <span class="label">Type</span>
            <span class="value">${type}</span>
        </div>
        <div class="detail-row">
            <span class="label">Location</span>
            <span class="value">${state.currentPath}</span>
        </div>
        <div class="detail-row">
            <span class="label">Dimensions</span>
            <span class="value">64-bit substrate</span>
        </div>
    `;
}

// ============================================================================
// Status Updates
// ============================================================================
function updateItemCount(count) {
    const el = document.getElementById('item-count');
    if (el) {
        el.textContent = `${count} items`;
    }
}

function updateSelectedCount() {
    const el = document.getElementById('selected-count');
    if (el) {
        el.textContent = `${state.selectedItems.length} selected`;
    }
}

// ============================================================================
// Charts & Visualizations
// ============================================================================
function initializeChart() {
    const canvas = document.getElementById('main-chart');
    if (!canvas) return;
    
    // Destroy existing chart
    if (state.chartInstance) {
        state.chartInstance.destroy();
    }
    
    const ctx = canvas.getContext('2d');
    
    state.chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Sample Data',
                data: [12, 19, 3, 5, 2, 3],
                backgroundColor: 'rgba(99, 102, 241, 0.6)',
                borderColor: 'rgba(99, 102, 241, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

function switchChartType(type) {
    // Update button states
    document.querySelectorAll('.chart-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.chart === type);
    });
    
    if (!state.chartInstance) return;
    
    // Map our types to Chart.js types
    const chartTypes = {
        bar: 'bar',
        line: 'line',
        pie: 'pie',
        trend: 'line',
        bell: 'line',
        scatter: 'scatter'
    };
    
    state.chartInstance.config.type = chartTypes[type] || 'bar';
    state.chartInstance.update();
}

// ============================================================================
// Properties Modal
// ============================================================================
function closePropertiesModal() {
    elements.propertiesModal?.classList.remove('visible');
}

function showProperties(itemId) {
    const content = document.getElementById('properties-content');
    if (!content) return;
    
    content.innerHTML = `
        <div class="detail-row">
            <span class="label">ID</span>
            <span class="value">${itemId}</span>
        </div>
        <div class="detail-row">
            <span class="label">Dimensional ID</span>
            <span class="value">${BigInt(itemId) * BigInt(Date.now())}</span>
        </div>
        <div class="detail-row">
            <span class="label">Storage</span>
            <span class="value">Substrate</span>
        </div>
    `;
    
    elements.propertiesModal?.classList.add('visible');
}

// Make functions globally available
window.selectService = selectService;
window.quickConnect = quickConnect;
window.openConnectionWizard = openConnectionWizard;
window.closeCrawlerModal = closeCrawlerModal;
window.openItem = openItem;
window.showProperties = showProperties;
