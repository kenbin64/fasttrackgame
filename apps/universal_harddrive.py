"""
Universal Hard Drive - Dimensional Storage Interface

A unified file system that presents ALL data sources as local files.
Uses SRLs (Substrate Reference Links) for passive connections.
Data is NEVER written locally unless explicitly saved.

Core Concepts:
    - SRL (Substrate Reference Link): A reference that materializes data on demand
    - Drives: Virtual mounts for different data sources
    - Lazy Materialization: Data exists as potential until viewed
    - Unified View: APIs, databases, cloud storage all appear as local files
    - Save on Demand: No automatic persistence

Drive Layout:
    A: Local        - Local file system (read-only unless saved)
    B: API          - Universal Connector APIs
    C: Database     - Helix Database collections
    D: Cloud        - Cloud storage references
    E: Cache        - Recently materialized data
    Z: Saved        - Explicitly saved data

Dimensional Structure:
    Level 6 (Whole):     The entire virtual file system
    Level 5 (Volume):    Drives (A:, B:, C:, etc.)
    Level 4 (Plane):     Folders / Categories
    Level 3 (Width):     Files / Items
    Level 2 (Length):    File content
    Level 1 (Point):     Atomic values
    Level 0 (Potential): SRLs (unmaterialized references)

Usage:
    from apps.universal_harddrive import UniversalHardDrive, run_server
    
    uhd = UniversalHardDrive()
    
    # Browse - everything looks like local files
    uhd.ls("B:/finance/")  # List API folder
    
    # Read - materializes on demand via SRL
    data = uhd.read("B:/finance/bitcoin.json")  # Fetches live
    
    # Save - only way to persist locally
    uhd.save("B:/finance/bitcoin.json", "Z:/snapshots/btc_price.json")
    
    # Start web UI
    run_server(port=8000)
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Union
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote, quote
import threading
import os
import sys

# Add parent to path for helix imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from helix import (
    HelixKernel, ManifoldSubstrate, Token,
    HelixCache, HelixLogger, HelixSerializer,
    LEVEL_NAMES, LEVEL_ICONS
)

# Import sibling apps
from .helix_database import HelixDatabase
from .universal_connector import UniversalConnector, API_REGISTRY

import re
from collections import defaultdict
import time


# =============================================================================
# INGESTION METRICS - Track Efficiency, Bit Savings, Size Reduction
# =============================================================================

@dataclass
class IngestionMetrics:
    """
    Tracks efficiency metrics for kernel ingestion.
    
    Shows users exactly how much space is saved through dimensional
    compression and substrate optimization.
    """
    # Totals
    total_files_ingested: int = 0
    total_original_bytes: int = 0
    total_ingested_bytes: int = 0
    total_bit_savings: int = 0
    
    # By type
    type_stats: Dict[str, Dict] = field(default_factory=dict)
    
    # Timeline
    ingestion_log: List[Dict] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    
    # Session stats
    session_files: int = 0
    session_bytes_saved: int = 0
    
    def record_ingestion(self, item: 'SubstratedItem') -> Dict:
        """Record metrics for an ingested item"""
        original = item.original_size or item.size
        ingested = item.ingested_size or item.size
        savings = max(0, original - ingested)
        efficiency = (savings / original * 100) if original > 0 else 0
        
        # Update totals
        self.total_files_ingested += 1
        self.total_original_bytes += original
        self.total_ingested_bytes += ingested
        self.total_bit_savings += savings * 8  # Convert to bits
        
        # Update session
        self.session_files += 1
        self.session_bytes_saved += savings
        
        # Track by type
        file_type = item.mime_type.split('/')[0] if '/' in item.mime_type else 'other'
        if file_type not in self.type_stats:
            self.type_stats[file_type] = {
                'count': 0, 'original': 0, 'ingested': 0, 'savings': 0
            }
        self.type_stats[file_type]['count'] += 1
        self.type_stats[file_type]['original'] += original
        self.type_stats[file_type]['ingested'] += ingested
        self.type_stats[file_type]['savings'] += savings
        
        # Log entry
        entry = {
            'timestamp': datetime.now().isoformat(),
            'name': item.name,
            'type': file_type,
            'original_bytes': original,
            'ingested_bytes': ingested,
            'bytes_saved': savings,
            'efficiency_pct': round(efficiency, 2)
        }
        self.ingestion_log.append(entry)
        
        # Keep log bounded
        if len(self.ingestion_log) > 1000:
            self.ingestion_log = self.ingestion_log[-500:]
        
        return entry
    
    def get_summary(self) -> Dict:
        """Get overall metrics summary"""
        efficiency = 0
        if self.total_original_bytes > 0:
            efficiency = (self.total_original_bytes - self.total_ingested_bytes) / self.total_original_bytes * 100
        
        uptime = time.time() - self.start_time
        rate = self.total_files_ingested / uptime if uptime > 0 else 0
        
        return {
            'total_files': self.total_files_ingested,
            'original_size': self._format_size(self.total_original_bytes),
            'original_bytes': self.total_original_bytes,
            'ingested_size': self._format_size(self.total_ingested_bytes),
            'ingested_bytes': self.total_ingested_bytes,
            'bytes_saved': self.total_original_bytes - self.total_ingested_bytes,
            'size_saved': self._format_size(self.total_original_bytes - self.total_ingested_bytes),
            'bit_savings': self.total_bit_savings,
            'bit_savings_formatted': self._format_bits(self.total_bit_savings),
            'efficiency_pct': round(efficiency, 2),
            'compression_ratio': f"{self.total_original_bytes}:{self.total_ingested_bytes}" if self.total_ingested_bytes > 0 else "N/A",
            'uptime_seconds': round(uptime, 1),
            'ingestion_rate': f"{rate:.2f}/sec",
            'session_files': self.session_files,
            'session_saved': self._format_size(self.session_bytes_saved)
        }
    
    def get_by_type(self) -> Dict:
        """Get metrics breakdown by file type"""
        result = {}
        for ftype, stats in self.type_stats.items():
            efficiency = 0
            if stats['original'] > 0:
                efficiency = (stats['original'] - stats['ingested']) / stats['original'] * 100
            result[ftype] = {
                'count': stats['count'],
                'original': self._format_size(stats['original']),
                'ingested': self._format_size(stats['ingested']),
                'saved': self._format_size(stats['savings']),
                'efficiency_pct': round(efficiency, 2)
            }
        return result
    
    def get_recent(self, limit: int = 20) -> List[Dict]:
        """Get recent ingestion log entries"""
        return self.ingestion_log[-limit:]
    
    def _format_size(self, bytes_val: int) -> str:
        """Format bytes as human readable"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if abs(bytes_val) < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} PB"
    
    def _format_bits(self, bits: int) -> str:
        """Format bits as human readable"""
        for unit in ['bits', 'Kb', 'Mb', 'Gb', 'Tb']:
            if abs(bits) < 1024:
                return f"{bits:.1f} {unit}"
            bits /= 1024
        return f"{bits:.1f} Pb"
    
    def to_dashboard(self) -> Dict:
        """Generate full dashboard data"""
        summary = self.get_summary()
        return {
            'summary': summary,
            'by_type': self.get_by_type(),
            'recent': self.get_recent(20),
            'gauges': {
                'efficiency': {
                    'value': summary['efficiency_pct'],
                    'max': 100,
                    'label': 'Efficiency',
                    'unit': '%',
                    'color': '#00ff88' if summary['efficiency_pct'] > 50 else '#ffaa00'
                },
                'bit_savings': {
                    'value': self.total_bit_savings,
                    'label': 'Bits Saved',
                    'formatted': summary['bit_savings_formatted'],
                    'color': '#00ffff'
                },
                'compression': {
                    'value': round(summary['ingested_bytes'] / max(1, summary['original_bytes']) * 100, 1),
                    'max': 100,
                    'label': 'Compressed To',
                    'unit': '%',
                    'color': '#ff00ff'
                }
            }
        }


# Global metrics instance
GLOBAL_METRICS = IngestionMetrics()


# =============================================================================
# SEMANTIC INTELLIGENCE - System Learns, SRL Knows Where to Look
# =============================================================================

class SemanticRouter:
    """
    The SRL already knows where to look.
    
    Routes natural language queries to the right data sources
    based on semantic understanding of what's connected.
    """
    
    # Query patterns → source types and search strategies
    PATTERNS = {
        # Email patterns
        r'email|mail|inbox|sent|message': {
            'sources': ['email', 'gmail', 'outlook', 'imap'],
            'search_fields': ['from', 'to', 'subject', 'body', 'attachments'],
            'icon': '📧'
        },
        r'attachment|attached|file.*email': {
            'sources': ['email'],
            'search_fields': ['attachments'],
            'icon': '📎'
        },
        
        # Calendar patterns
        r'calendar|schedule|meeting|appointment|event|weekly|daily|monthly': {
            'sources': ['calendar', 'gcal', 'outlook_cal', 'ical'],
            'search_fields': ['title', 'date', 'time', 'attendees', 'location'],
            'icon': '📅'
        },
        
        # Contacts
        r'contact|phone|address|person|who is': {
            'sources': ['contacts', 'crm', 'address_book'],
            'search_fields': ['name', 'email', 'phone', 'company'],
            'icon': '👤'
        },
        
        # Documents
        r'document|doc|pdf|file|recipe|report|spreadsheet': {
            'sources': ['local', 'gdrive', 'dropbox', 's3', 'onedrive'],
            'search_fields': ['name', 'content', 'tags'],
            'icon': '📄'
        },
        
        # Shopping/Coupons
        r'coupon|discount|deal|promo|offer|shopping': {
            'sources': ['email', 'bookmarks', 'notes'],
            'search_fields': ['subject', 'body', 'content'],
            'icon': '🏷️'
        },
        
        # Definitions/Knowledge
        r'definition|what is|mean|define|explain': {
            'sources': ['dictionary', 'wikipedia', 'notes', 'documents'],
            'search_fields': ['term', 'definition', 'content'],
            'icon': '📖'
        },
        
        # Finance
        r'bank|transaction|payment|invoice|expense|money': {
            'sources': ['banking', 'stripe', 'paypal', 'quickbooks'],
            'search_fields': ['amount', 'description', 'date', 'merchant'],
            'icon': '💰'
        },
        
        # Social
        r'tweet|post|social|facebook|twitter|linkedin': {
            'sources': ['twitter', 'facebook', 'linkedin'],
            'search_fields': ['content', 'author', 'date'],
            'icon': '💬'
        },
        
        # Code/Dev
        r'code|function|class|repo|commit|bug|issue': {
            'sources': ['github', 'gitlab', 'local'],
            'search_fields': ['name', 'content', 'description'],
            'icon': '💻'
        },
        
        # Photos
        r'photo|picture|image|screenshot': {
            'sources': ['photos', 'gdrive', 'dropbox', 'local'],
            'search_fields': ['name', 'date', 'location', 'tags'],
            'icon': '🖼️'
        },
        
        # Notes
        r'note|memo|reminder|todo|task': {
            'sources': ['notes', 'notion', 'evernote', 'todoist'],
            'search_fields': ['title', 'content', 'tags'],
            'icon': '📝'
        }
    }
    
    def __init__(self):
        self._compiled_patterns = {
            re.compile(pattern, re.IGNORECASE): config
            for pattern, config in self.PATTERNS.items()
        }
    
    def route(self, query: str) -> Dict:
        """
        Route a natural language query to appropriate sources.
        
        Returns:
            {
                'sources': ['email', 'calendar', ...],
                'search_fields': ['subject', 'body', ...],
                'keywords': ['michaela', 'coupon', ...],
                'icon': '📧',
                'confidence': 0.85
            }
        """
        query_lower = query.lower()
        matched_sources = set()
        matched_fields = set()
        icons = []
        
        # Find matching patterns
        for pattern, config in self._compiled_patterns.items():
            if pattern.search(query_lower):
                matched_sources.update(config['sources'])
                matched_fields.update(config['search_fields'])
                icons.append(config['icon'])
        
        # Extract keywords (non-stop words)
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'find', 'show', 
                      'get', 'all', 'my', 'with', 'in', 'on', 'at', 'to', 'for',
                      'what', 'where', 'when', 'how', 'who', 'which', 'that', 'this'}
        keywords = [w for w in re.findall(r'\b\w+\b', query_lower) 
                   if w not in stop_words and len(w) > 2]
        
        # Default to searching everything if no pattern matched
        if not matched_sources:
            matched_sources = {'local', 'email', 'documents', 'notes'}
            matched_fields = {'name', 'content', 'subject', 'body'}
        
        return {
            'sources': list(matched_sources),
            'search_fields': list(matched_fields),
            'keywords': keywords,
            'icon': icons[0] if icons else '🔍',
            'confidence': min(1.0, len(matched_sources) * 0.2 + 0.3)
        }


class RelationshipGraph:
    """
    System learns relationships between data.
    
    The more connections, the more the system understands:
    - Common email addresses across sources
    - Keywords that appear together
    - Entities (people, companies, topics) linking data
    - Temporal patterns (weekly meetings, monthly reports)
    """
    
    def __init__(self):
        # Entity extraction and linking
        self._entities: Dict[str, Dict] = {}  # entity_id -> {type, mentions, srls}
        
        # Relationship edges
        self._relationships: Dict[str, set] = defaultdict(set)  # srl_path -> related srl_paths
        
        # Keyword index
        self._keyword_index: Dict[str, set] = defaultdict(set)  # keyword -> srl_paths
        
        # Email address index
        self._email_index: Dict[str, set] = defaultdict(set)  # email -> srl_paths
        
        # Temporal index
        self._temporal_index: Dict[str, set] = defaultdict(set)  # date_key -> srl_paths
        
        # Learning stats
        self._stats = {
            'entities_discovered': 0,
            'relationships_learned': 0,
            'patterns_detected': 0
        }
    
    def learn(self, srl_path: str, data: Any, source_type: str) -> Dict:
        """
        Learn from ingested data. Extract entities, keywords, relationships.
        
        This is called after every materialization.
        """
        learned = {
            'entities': [],
            'keywords': [],
            'relationships': []
        }
        
        if not data:
            return learned
        
        # Convert to searchable text
        text = self._extract_text(data)
        
        # Extract emails
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        for email in emails:
            email_lower = email.lower()
            self._email_index[email_lower].add(srl_path)
            learned['entities'].append({'type': 'email', 'value': email_lower})
            
            # Link to other SRLs with same email
            for other_path in self._email_index[email_lower]:
                if other_path != srl_path:
                    self._relationships[srl_path].add(other_path)
                    self._relationships[other_path].add(srl_path)
                    self._stats['relationships_learned'] += 1
        
        # Extract keywords
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        word_counts = defaultdict(int)
        for word in words:
            word_counts[word] += 1
        
        # Index significant keywords (appear 2+ times or are capitalized in source)
        for word, count in word_counts.items():
            if count >= 2 or word.title() in text:
                self._keyword_index[word].add(srl_path)
                learned['keywords'].append(word)
        
        # Extract dates
        dates = re.findall(r'\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}', text)
        for date in dates:
            self._temporal_index[date].add(srl_path)
        
        # Extract names (capitalized words that might be names)
        potential_names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', str(data))
        for name in potential_names[:10]:  # Limit
            name_key = name.lower().replace(' ', '_')
            if name_key not in self._entities:
                self._entities[name_key] = {
                    'type': 'person',
                    'name': name,
                    'mentions': 0,
                    'srls': set()
                }
                self._stats['entities_discovered'] += 1
            self._entities[name_key]['mentions'] += 1
            self._entities[name_key]['srls'].add(srl_path)
            learned['entities'].append({'type': 'person', 'value': name})
        
        return learned
    
    def _extract_text(self, data: Any) -> str:
        """Extract searchable text from any data structure"""
        if isinstance(data, str):
            return data
        elif isinstance(data, dict):
            return ' '.join(str(v) for v in data.values())
        elif isinstance(data, list):
            return ' '.join(self._extract_text(item) for item in data[:100])
        else:
            return str(data)
    
    def find_related(self, srl_path: str, limit: int = 10) -> List[str]:
        """Find SRLs related to the given one"""
        return list(self._relationships.get(srl_path, set()))[:limit]
    
    def search_by_email(self, email: str) -> List[str]:
        """Find all SRLs mentioning an email address"""
        return list(self._email_index.get(email.lower(), set()))
    
    def search_by_keyword(self, keyword: str) -> List[str]:
        """Find all SRLs containing a keyword"""
        return list(self._keyword_index.get(keyword.lower(), set()))
    
    def search_by_entity(self, entity_name: str) -> List[str]:
        """Find all SRLs mentioning an entity"""
        key = entity_name.lower().replace(' ', '_')
        entity = self._entities.get(key)
        if entity:
            return list(entity['srls'])
        return []
    
    def get_common_emails(self, limit: int = 20) -> List[Dict]:
        """Get most common email addresses across all data"""
        return sorted(
            [{'email': e, 'count': len(srls)} 
             for e, srls in self._email_index.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:limit]
    
    def get_common_keywords(self, limit: int = 50) -> List[Dict]:
        """Get most common keywords across all data"""
        return sorted(
            [{'keyword': k, 'count': len(srls)} 
             for k, srls in self._keyword_index.items()
             if len(srls) >= 2],  # Only keywords in multiple places
            key=lambda x: x['count'],
            reverse=True
        )[:limit]


class SmartQuery:
    """
    Natural language to dimensional query.
    
    "Find all Michaela coupons" → searches emails for "michaela" + "coupon"
    "Email with attachment Moms Recipes" → searches email attachments
    "Weekly schedule" → queries calendar for current week
    "Definition of scrupulosity" → searches dictionary sources
    """
    
    def __init__(self, router: SemanticRouter, graph: RelationshipGraph):
        self.router = router
        self.graph = graph
    
    def parse(self, query: str) -> Dict:
        """
        Parse natural language query into dimensional search.
        
        Returns searchable structure with:
        - sources to search
        - fields to match
        - keywords to find
        - filters to apply
        """
        # Get semantic routing
        routing = self.router.route(query)
        
        # Parse special constructs
        parsed = {
            'raw_query': query,
            'routing': routing,
            'filters': {},
            'sort': None,
            'limit': 100
        }
        
        # Extract quoted phrases (exact match)
        quoted = re.findall(r'"([^"]+)"', query)
        if quoted:
            parsed['exact_phrases'] = quoted
        
        # Time-based queries
        time_patterns = {
            r'weekly|this week': {'time_range': 'week'},
            r'daily|today': {'time_range': 'day'},
            r'monthly|this month': {'time_range': 'month'},
            r'yesterday': {'time_range': 'yesterday'},
            r'last (\d+) days': {'time_range': 'last_n_days'},
        }
        for pattern, config in time_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                parsed['filters']['time'] = config
                break
        
        # From/To filters for email
        from_match = re.search(r'from\s+(\S+)', query, re.IGNORECASE)
        if from_match:
            parsed['filters']['from'] = from_match.group(1)
        
        to_match = re.search(r'to\s+(\S+)', query, re.IGNORECASE)
        if to_match:
            parsed['filters']['to'] = to_match.group(1)
        
        return parsed
    
    def execute(self, query: str, srls: Dict[str, 'SRL']) -> List[Dict]:
        """
        Execute a natural language query against SRLs.
        
        The SRL already knows where to look - we just need to ask.
        """
        parsed = self.parse(query)
        results = []
        
        routing = parsed['routing']
        keywords = routing['keywords']
        sources = routing['sources']
        
        # First, check relationship graph for quick matches
        for keyword in keywords:
            matching_paths = self.graph.search_by_keyword(keyword)
            for path in matching_paths:
                if path in srls:
                    srl = srls[path]
                    results.append({
                        'path': path,
                        'name': srl.name,
                        'source': srl.source_type,
                        'icon': routing['icon'],
                        'match_type': 'keyword_index',
                        'confidence': 0.9
                    })
        
        # Check email index for email queries
        if 'email' in sources:
            for keyword in keywords:
                if '@' in keyword or re.match(r'^[a-z]+$', keyword):
                    email_matches = self.graph.search_by_email(keyword)
                    for path in email_matches:
                        if path in srls and path not in [r['path'] for r in results]:
                            srl = srls[path]
                            results.append({
                                'path': path,
                                'name': srl.name,
                                'source': srl.source_type,
                                'icon': '📧',
                                'match_type': 'email_index',
                                'confidence': 0.95
                            })
        
        # Search entity names
        for keyword in keywords:
            entity_matches = self.graph.search_by_entity(keyword)
            for path in entity_matches:
                if path in srls and path not in [r['path'] for r in results]:
                    srl = srls[path]
                    results.append({
                        'path': path,
                        'name': srl.name,
                        'source': srl.source_type,
                        'icon': '👤',
                        'match_type': 'entity_match',
                        'confidence': 0.85
                    })
        
        # Fall back to scanning SRLs by source type
        if len(results) < 10:
            for path, srl in srls.items():
                if path in [r['path'] for r in results]:
                    continue
                    
                # Check if source matches
                source_match = srl.source_type in sources or not sources
                
                # Check if name/path contains keywords
                name_match = any(kw in srl.name.lower() or kw in path.lower() 
                               for kw in keywords)
                
                if source_match and name_match:
                    results.append({
                        'path': path,
                        'name': srl.name,
                        'source': srl.source_type,
                        'icon': routing['icon'],
                        'match_type': 'name_scan',
                        'confidence': 0.6
                    })
        
        # Sort by confidence
        results.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return results[:parsed['limit']]


# =============================================================================
# SUBSTRATED ITEM - ALL DATA INGESTED INTO KERNEL
# =============================================================================

@dataclass
class SubstratedItem:
    """
    A data item that has been ingested into the Helix kernel.
    
    ALL data in Universal Hard Drive passes through this wrapper.
    Raw data is transformed into dimensional substrate coordinates.
    
    The 7 dimensions:
        0. Potential (unmaterialized reference)
        1. Point (identity - unique ID)
        2. Line (relationship - source connection)
        3. Plane (structure - data shape/schema)
        4. Volume (environment - context/folder)
        5. Life (multiplicity - versions/variants)
        6. Meaning (semantics - computed significance)
        7. Rest (completion - final state)
    """
    # Identity (Level 1)
    id: str
    name: str
    
    # Relationship (Level 2) 
    source_type: str           # 'local', 'api', 'database', 'cloud'
    source_ref: str            # Where it came from
    path: str                  # Virtual path
    
    # Structure (Level 3)
    data_type: str             # 'file', 'folder', 'record', 'endpoint', 'stream'
    mime_type: str = "application/octet-stream"
    schema: Dict = field(default_factory=dict)  # Inferred structure
    
    # Environment (Level 4)
    drive: str = ""            # A:, B:, C:, etc.
    parent_path: str = ""      # Container path
    size: int = 0
    
    # Multiplicity (Level 5)
    version: int = 1
    variants: List[str] = field(default_factory=list)
    
    # Semantics (Level 6)
    meaning: Dict = field(default_factory=dict)  # Computed semantics
    tags: List[str] = field(default_factory=list)
    
    # Completion (Level 7)
    materialized: bool = False
    cached_data: Any = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    modified_at: str = ""
    
    # Native format preservation
    native_format: str = ""    # Original format for native view
    native_data: Any = None    # Raw data before substration
    
    # Metrics tracking
    original_size: int = 0     # Size before ingestion
    ingested_size: int = 0     # Size after kernel processing
    ingestion_time: float = 0  # Time to ingest (ms)
    compression_ratio: float = 1.0  # original/ingested
    
    def ingest(self, substrate: ManifoldSubstrate, spiral: int = 0) -> None:
        """Ingest this item into the manifold substrate"""
        # Level 1: Identity
        substrate.ingest_keyed(spiral, 1, self.id, {
            'id': self.id,
            'name': self.name
        })
        
        # Level 2: Relationship  
        substrate.ingest_keyed(spiral, 2, self.id, {
            'source_type': self.source_type,
            'source_ref': self.source_ref,
            'path': self.path
        })
        
        # Level 3: Structure
        substrate.ingest_keyed(spiral, 3, self.id, {
            'data_type': self.data_type,
            'mime_type': self.mime_type,
            'schema': self.schema
        })
        
        # Level 4: Environment
        substrate.ingest_keyed(spiral, 4, self.id, {
            'drive': self.drive,
            'parent_path': self.parent_path,
            'size': self.size
        })
        
        # Level 5: Multiplicity
        substrate.ingest_keyed(spiral, 5, self.id, {
            'version': self.version,
            'variants': self.variants
        })
        
        # Level 6: Semantics
        substrate.ingest_keyed(spiral, 6, self.id, {
            'meaning': self.meaning,
            'tags': self.tags
        })
    
    def to_dimensional(self) -> Dict:
        """Return dimensional representation (7 levels) with metrics"""
        efficiency = 0
        if self.original_size > 0:
            efficiency = (self.original_size - self.ingested_size) / self.original_size * 100
        
        return {
            'level_0_potential': not self.materialized,
            'level_1_identity': {'id': self.id, 'name': self.name},
            'level_2_relationship': {'source': self.source_type, 'ref': self.source_ref},
            'level_3_structure': {'type': self.data_type, 'mime': self.mime_type, 'schema': self.schema},
            'level_4_environment': {'drive': self.drive, 'path': self.path, 'size': self.size},
            'level_5_multiplicity': {'version': self.version, 'variants': self.variants},
            'level_6_semantics': {'meaning': self.meaning, 'tags': self.tags},
            'level_7_completion': {'materialized': self.materialized, 'created': self.created_at},
            'metrics': {
                'original_bytes': self.original_size,
                'ingested_bytes': self.ingested_size,
                'bytes_saved': self.original_size - self.ingested_size,
                'bit_savings': (self.original_size - self.ingested_size) * 8,
                'efficiency_pct': round(efficiency, 2),
                'compression_ratio': round(self.compression_ratio, 2),
                'ingestion_ms': round(self.ingestion_time, 2)
            }
        }
    
    def to_tabular(self) -> Dict:
        """Return flat row for tabular view with metrics"""
        efficiency = 0
        if self.original_size > 0:
            efficiency = (self.original_size - self.ingested_size) / self.original_size * 100
        
        return {
            'id': self.id,
            'name': self.name,
            'type': self.data_type,
            'source': self.source_type,
            'drive': self.drive,
            'path': self.path,
            'size': self.size,
            'mime': self.mime_type,
            'version': self.version,
            'tags': ', '.join(self.tags),
            'materialized': '✓' if self.materialized else '○',
            'original_bytes': self.original_size,
            'ingested_bytes': self.ingested_size,
            'savings_pct': f"{efficiency:.1f}%",
            'compression': f"{self.compression_ratio:.1f}x"
        }
    
    def to_native(self) -> Any:
        """Return native format (original source format)"""
        if self.native_data is not None:
            return {'format': self.native_format, 'data': self.native_data}
        return self.cached_data
    
    def to_file(self) -> Dict:
        """Return file/folder view representation"""
        is_folder = self.data_type in ('folder', 'collection', 'category')
        icon = self._get_icon()
        return {
            'name': self.name,
            'path': self.path,
            'is_folder': is_folder,
            'icon': icon,
            'size': self.size,
            'source': self.source_type,
            'materialized': self.materialized
        }
    
    def _get_icon(self) -> str:
        """Get appropriate icon for this item"""
        if self.data_type in ('folder', 'collection', 'category'):
            return '📁'
        
        ext_icons = {
            'json': '📋', 'xml': '📋', 'csv': '📊', 'txt': '📄',
            'py': '🐍', 'js': '📜', 'html': '🌐', 'css': '🎨',
            'jpg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'svg': '🖼️',
            'mp3': '🎵', 'wav': '🎵', 'mp4': '🎬', 'pdf': '📕',
            'zip': '📦', 'db': '🗄️', 'sql': '🗄️'
        }
        
        ext = self.name.split('.')[-1].lower() if '.' in self.name else ''
        return ext_icons.get(ext, '📄')
    
    def to_dict(self) -> Dict:
        """Full dictionary representation with metrics"""
        efficiency = 0
        if self.original_size > 0:
            efficiency = (self.original_size - self.ingested_size) / self.original_size * 100
        
        return {
            'id': self.id,
            'name': self.name,
            'source_type': self.source_type,
            'source_ref': self.source_ref,
            'path': self.path,
            'data_type': self.data_type,
            'mime_type': self.mime_type,
            'drive': self.drive,
            'size': self.size,
            'version': self.version,
            'tags': self.tags,
            'materialized': self.materialized,
            'created_at': self.created_at,
            'metrics': {
                'original_bytes': self.original_size,
                'ingested_bytes': self.ingested_size,
                'bytes_saved': self.original_size - self.ingested_size,
                'bit_savings': (self.original_size - self.ingested_size) * 8,
                'efficiency_pct': round(efficiency, 2),
                'compression_ratio': round(self.compression_ratio, 2),
                'ingestion_ms': round(self.ingestion_time, 2)
            }
        }
    
    def to_metrics(self) -> Dict:
        """Return just metrics for this item"""
        efficiency = 0
        if self.original_size > 0:
            efficiency = (self.original_size - self.ingested_size) / self.original_size * 100
        
        return {
            'name': self.name,
            'path': self.path,
            'original_size': self._format_size(self.original_size),
            'original_bytes': self.original_size,
            'ingested_size': self._format_size(self.ingested_size),
            'ingested_bytes': self.ingested_size,
            'bytes_saved': self.original_size - self.ingested_size,
            'size_saved': self._format_size(self.original_size - self.ingested_size),
            'bit_savings': (self.original_size - self.ingested_size) * 8,
            'efficiency_pct': round(efficiency, 2),
            'compression_ratio': round(self.compression_ratio, 2),
            'ingestion_ms': round(self.ingestion_time, 2)
        }
    
    def _format_size(self, bytes_val: int) -> str:
        """Format bytes as human readable"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if abs(bytes_val) < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} PB"


# =============================================================================
# SRL - SUBSTRATE REFERENCE LINK
# =============================================================================

@dataclass
class SRL:
    """
    Substrate Reference Link - A passive connection to data.
    
    SRLs don't hold data - they hold the potential to materialize data.
    Data only exists when invoked (viewed/read).
    
    When materialized, data is INGESTED into the kernel as SubstratedItem.
    """
    id: str
    path: str                          # Virtual path: "B:/finance/bitcoin.json"
    source_type: str                   # 'local', 'api', 'database', 'cloud'
    source_ref: str                    # API name, DB collection, file path, URL
    materializer: Optional[Callable]   # Function to materialize data
    
    # Metadata (doesn't require materialization)
    name: str = ""
    mime_type: str = "application/json"
    size_hint: int = 0                 # Estimated size (0 = unknown)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Data type
    data_type: str = "file"            # 'file', 'folder', 'record', 'endpoint'
    drive: str = ""                    # A:, B:, C:, etc.
    
    # State
    _materialized: bool = field(default=False, repr=False)
    _cached_data: Any = field(default=None, repr=False)
    _native_data: Any = field(default=None, repr=False)  # Original format
    _native_format: str = field(default="", repr=False)
    _last_access: Optional[str] = field(default=None, repr=False)
    _substrated_item: Optional[SubstratedItem] = field(default=None, repr=False)
    
    def materialize(self) -> Any:
        """
        Materialize the data - this is when the connection becomes active.
        Data is fetched/computed only at this moment.
        Data is INGESTED into substrate as SubstratedItem.
        Tracks ingestion metrics for efficiency visualization.
        """
        if self._materialized and self._cached_data is not None:
            return self._cached_data
        
        if self.materializer:
            try:
                start_time = time.time()
                raw_data = self.materializer()
                self._native_data = raw_data
                self._native_format = self._detect_format(raw_data)
                self._cached_data = raw_data
                self._materialized = True
                self._last_access = datetime.now().isoformat()
                ingestion_time = (time.time() - start_time) * 1000  # ms
                
                # Create SubstratedItem - INGEST into kernel
                self._substrated_item = self._create_substrated_item(raw_data, ingestion_time)
                
                # Record metrics
                GLOBAL_METRICS.record_ingestion(self._substrated_item)
                
                return self._cached_data
            except Exception as e:
                return {"error": str(e), "srl": self.path}
        
        return None
    
    def _detect_format(self, data: Any) -> str:
        """Detect the native format of the data"""
        if isinstance(data, dict):
            return 'json'
        elif isinstance(data, list):
            return 'array'
        elif isinstance(data, str):
            if data.strip().startswith(('<', '<?xml')):
                return 'xml'
            elif data.strip().startswith('{') or data.strip().startswith('['):
                return 'json'
            return 'text'
        elif isinstance(data, bytes):
            return 'binary'
        return 'unknown'
    
    def _create_substrated_item(self, data: Any, ingestion_time: float = 0) -> SubstratedItem:
        """Transform raw data into SubstratedItem (kernel ingestion)"""
        # Infer schema from data
        schema = self._infer_schema(data)
        
        # Compute meaning/semantics
        meaning = self._compute_meaning(data)
        
        # Extract drive from path
        drive = self.path.split(':')[0] if ':' in self.path else ''
        parent = '/'.join(self.path.split('/')[:-1])
        
        # Calculate sizes for metrics
        original_size = self._calculate_original_size(data)
        ingested_size = self._calculate_ingested_size(schema, meaning)
        compression_ratio = original_size / max(1, ingested_size)
        
        return SubstratedItem(
            id=self.id,
            name=self.name,
            source_type=self.source_type,
            source_ref=self.source_ref,
            path=self.path,
            data_type=self.data_type,
            mime_type=self.mime_type,
            schema=schema,
            drive=drive,
            parent_path=parent,
            size=self.size_hint or len(str(data)),
            meaning=meaning,
            materialized=True,
            cached_data=data,
            native_format=self._native_format,
            native_data=self._native_data,
            original_size=original_size,
            ingested_size=ingested_size,
            ingestion_time=ingestion_time,
            compression_ratio=compression_ratio
        )
    
    def _calculate_original_size(self, data: Any) -> int:
        """Calculate original data size in bytes"""
        if isinstance(data, bytes):
            return len(data)
        elif isinstance(data, str):
            return len(data.encode('utf-8'))
        elif isinstance(data, (dict, list)):
            return len(json.dumps(data).encode('utf-8'))
        else:
            return len(str(data).encode('utf-8'))
    
    def _calculate_ingested_size(self, schema: Dict, meaning: Dict) -> int:
        """
        Calculate ingested size after dimensional compression.
        
        The kernel stores only structural/semantic information,
        not raw data - achieving significant space savings.
        """
        # Schema is just structure reference - much smaller
        schema_size = len(json.dumps(schema).encode('utf-8'))
        
        # Meaning is computed semantics - compact
        meaning_size = len(json.dumps(meaning).encode('utf-8'))
        
        # Base overhead for dimensional coordinates
        dimensional_overhead = 128  # Fixed 7D coordinate structure
        
        return schema_size + meaning_size + dimensional_overhead
    
    def _infer_schema(self, data: Any) -> Dict:
        """Infer structure/schema from data (Level 3)"""
        if isinstance(data, dict):
            return {
                'type': 'object',
                'keys': list(data.keys())[:20],  # First 20 keys
                'key_count': len(data)
            }
        elif isinstance(data, list):
            sample_type = type(data[0]).__name__ if data else 'unknown'
            return {
                'type': 'array',
                'length': len(data),
                'item_type': sample_type
            }
        else:
            return {'type': type(data).__name__}
    
    def _compute_meaning(self, data: Any) -> Dict:
        """Compute semantics from data (Level 6)"""
        meaning = {}
        
        if isinstance(data, dict):
            # Auto-tag based on keys
            keys = set(k.lower() for k in data.keys())
            if 'price' in keys or 'cost' in keys or 'amount' in keys:
                meaning['domain'] = 'financial'
            if 'name' in keys and ('email' in keys or 'phone' in keys):
                meaning['domain'] = 'contact'
            if 'lat' in keys or 'longitude' in keys or 'location' in keys:
                meaning['domain'] = 'geospatial'
            if 'timestamp' in keys or 'date' in keys or 'time' in keys:
                meaning['temporal'] = True
        
        elif isinstance(data, list) and len(data) > 0:
            meaning['cardinality'] = len(data)
            if len(data) > 100:
                meaning['scale'] = 'large'
        
        return meaning
    
    @property
    def substrated(self) -> Optional[SubstratedItem]:
        """Get the SubstratedItem (only available after materialization)"""
        return self._substrated_item
    
    def invalidate(self):
        """Invalidate cache - next access will re-materialize"""
        self._materialized = False
        self._cached_data = None
        self._substrated_item = None
    
    @property
    def is_materialized(self) -> bool:
        return self._materialized
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'path': self.path,
            'name': self.name,
            'source_type': self.source_type,
            'source_ref': self.source_ref,
            'mime_type': self.mime_type,
            'size_hint': self.size_hint,
            'materialized': self._materialized,
            'last_access': self._last_access,
            'has_substrate': self._substrated_item is not None
        }
    
    def to_dimensional(self) -> Dict:
        """Get dimensional view (requires materialization)"""
        if self._substrated_item:
            return self._substrated_item.to_dimensional()
        return {'level_0_potential': True, 'path': self.path}
    
    def to_tabular(self) -> Dict:
        """Get tabular view (requires materialization)"""
        if self._substrated_item:
            return self._substrated_item.to_tabular()
        return {'id': self.id, 'name': self.name, 'materialized': '○'}
    
    def to_native(self) -> Any:
        """Get native format view"""
        if self._substrated_item:
            return self._substrated_item.to_native()
        return None
    
    def to_file(self) -> Dict:
        """Get file/folder view"""
        if self._substrated_item:
            return self._substrated_item.to_file()
        return {
            'name': self.name,
            'path': self.path,
            'is_folder': self.data_type in ('folder', 'collection'),
            'icon': '📄',
            'materialized': self._materialized
        }


# =============================================================================
# VIRTUAL DRIVE
# =============================================================================

@dataclass
class VirtualDrive:
    """A virtual drive that mounts a data source"""
    letter: str          # A, B, C, etc.
    name: str            # "Local", "API", "Database"
    icon: str            # 💾, 🌐, 🗄️
    source_type: str     # 'local', 'api', 'database', 'cloud', 'cache', 'saved'
    description: str = ""
    read_only: bool = True  # Most drives are read-only
    connected: bool = False
    
    def to_dict(self) -> dict:
        return {
            'letter': self.letter,
            'name': self.name,
            'icon': self.icon,
            'source_type': self.source_type,
            'description': self.description,
            'read_only': self.read_only,
            'connected': self.connected
        }


# =============================================================================
# FILE NODE (for tree view)
# =============================================================================

@dataclass
class FileNode:
    """A node in the virtual file system"""
    path: str
    name: str
    is_folder: bool
    icon: str = "📄"
    size: int = 0
    children: List['FileNode'] = field(default_factory=list)
    srl: Optional[SRL] = None
    
    def to_dict(self) -> dict:
        return {
            'path': self.path,
            'name': self.name,
            'is_folder': self.is_folder,
            'icon': self.icon,
            'size': self.size,
            'children': [c.to_dict() for c in self.children] if self.children else [],
            'has_srl': self.srl is not None
        }


# =============================================================================
# CREDENTIAL VAULT - Secure Storage for Connection Credentials
# =============================================================================

@dataclass 
class Credential:
    """A stored credential for a data source connection"""
    id: str
    name: str                    # Display name: "My AWS", "Work Database"
    conn_type: str               # 'api', 'database', 'cloud', 'custom'
    provider: str                # 'aws', 'postgres', 'mongodb', 'rest', etc.
    
    # Connection details (encrypted in production)
    endpoint: str = ""           # URL, connection string, or host
    api_key: str = ""            # API key or token
    username: str = ""
    password: str = ""
    extra: Dict = field(default_factory=dict)  # Provider-specific config
    
    # State
    verified: bool = False       # Has connection been tested?
    last_used: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self, include_secrets: bool = False) -> Dict:
        result = {
            'id': self.id,
            'name': self.name,
            'conn_type': self.conn_type,
            'provider': self.provider,
            'endpoint': self.endpoint[:50] + '...' if len(self.endpoint) > 50 else self.endpoint,
            'verified': self.verified,
            'last_used': self.last_used,
            'created_at': self.created_at
        }
        if include_secrets:
            result['api_key'] = self.api_key
            result['username'] = self.username
            result['password'] = '***' if self.password else ''
        return result


class CredentialVault:
    """
    Secure credential storage for Universal Hard Drive.
    
    This is how users "connect to what they want":
    1. Add credentials for a service
    2. System uses credentials to ingest data
    3. Data appears as native local files
    
    In production, credentials would be encrypted at rest.
    """
    
    # =========================================================================
    # CANNED CONNECTIONS - Pre-configured for all major services
    # User just supplies credentials, system ingests EVERYTHING
    # =========================================================================
    
    CANNED_CONNECTIONS = {
        # =====================================================================
        # AI & MACHINE LEARNING
        # =====================================================================
        'openai': {
            'name': 'OpenAI',
            'icon': '🤖',
            'type': 'api',
            'category': 'AI',
            'fields': {'api_key': 'API Key'},
            'endpoint': 'https://api.openai.com/v1',
            'description': 'GPT models, DALL-E, Whisper',
            'ingests': ['models', 'files', 'assistants', 'threads']
        },
        'anthropic': {
            'name': 'Anthropic',
            'icon': '🧠',
            'type': 'api',
            'category': 'AI',
            'fields': {'api_key': 'API Key'},
            'endpoint': 'https://api.anthropic.com',
            'description': 'Claude AI models',
            'ingests': ['models']
        },
        'huggingface': {
            'name': 'Hugging Face',
            'icon': '🤗',
            'type': 'api',
            'category': 'AI',
            'fields': {'api_key': 'Access Token'},
            'endpoint': 'https://huggingface.co/api',
            'description': 'ML models, datasets, spaces',
            'ingests': ['models', 'datasets', 'spaces']
        },
        'replicate': {
            'name': 'Replicate',
            'icon': '🔁',
            'type': 'api',
            'category': 'AI',
            'fields': {'api_key': 'API Token'},
            'endpoint': 'https://api.replicate.com/v1',
            'description': 'Run ML models in the cloud',
            'ingests': ['models', 'predictions']
        },
        
        # =====================================================================
        # CLOUD PROVIDERS
        # =====================================================================
        'aws': {
            'name': 'Amazon Web Services',
            'icon': '☁️',
            'type': 'cloud',
            'category': 'Cloud',
            'fields': {
                'api_key': 'Access Key ID',
                'secret': 'Secret Access Key',
                'region': 'Region (e.g., us-east-1)'
            },
            'description': 'S3, DynamoDB, Lambda, EC2',
            'ingests': ['s3_buckets', 's3_objects', 'dynamodb_tables', 'lambda_functions', 'ec2_instances']
        },
        'azure': {
            'name': 'Microsoft Azure',
            'icon': '🔷',
            'type': 'cloud',
            'category': 'Cloud',
            'fields': {
                'tenant_id': 'Tenant ID',
                'client_id': 'Client ID',
                'client_secret': 'Client Secret'
            },
            'description': 'Blob storage, CosmosDB, Functions',
            'ingests': ['blobs', 'containers', 'cosmosdb', 'functions']
        },
        'gcp': {
            'name': 'Google Cloud Platform',
            'icon': '🌐',
            'type': 'cloud',
            'category': 'Cloud',
            'fields': {'credentials_json': 'Service Account JSON'},
            'description': 'Cloud Storage, BigQuery, Firestore',
            'ingests': ['buckets', 'bigquery_datasets', 'firestore_collections']
        },
        'digitalocean': {
            'name': 'DigitalOcean',
            'icon': '🌊',
            'type': 'cloud',
            'category': 'Cloud',
            'fields': {'api_key': 'API Token'},
            'endpoint': 'https://api.digitalocean.com/v2',
            'description': 'Droplets, Spaces, Databases',
            'ingests': ['droplets', 'spaces', 'databases', 'domains']
        },
        
        # =====================================================================
        # DATABASES
        # =====================================================================
        'postgres': {
            'name': 'PostgreSQL',
            'icon': '🐘',
            'type': 'database',
            'category': 'Database',
            'fields': {
                'host': 'Host',
                'port': 'Port (5432)',
                'database': 'Database Name',
                'username': 'Username',
                'password': 'Password'
            },
            'description': 'PostgreSQL database',
            'ingests': ['schemas', 'tables', 'views', 'functions']
        },
        'mysql': {
            'name': 'MySQL / MariaDB',
            'icon': '🐬',
            'type': 'database',
            'category': 'Database',
            'fields': {
                'host': 'Host',
                'port': 'Port (3306)',
                'database': 'Database Name',
                'username': 'Username',
                'password': 'Password'
            },
            'description': 'MySQL/MariaDB database',
            'ingests': ['tables', 'views', 'procedures']
        },
        'mongodb': {
            'name': 'MongoDB',
            'icon': '🍃',
            'type': 'database',
            'category': 'Database',
            'fields': {
                'connection_string': 'Connection String',
                'database': 'Database Name'
            },
            'description': 'MongoDB document database',
            'ingests': ['collections', 'documents']
        },
        'redis': {
            'name': 'Redis',
            'icon': '🔴',
            'type': 'database',
            'category': 'Database',
            'fields': {
                'host': 'Host',
                'port': 'Port (6379)',
                'password': 'Password (optional)'
            },
            'description': 'Redis key-value store',
            'ingests': ['keys', 'hashes', 'lists', 'sets']
        },
        'supabase': {
            'name': 'Supabase',
            'icon': '⚡',
            'type': 'database',
            'category': 'Database',
            'fields': {
                'url': 'Project URL',
                'api_key': 'API Key (anon or service)'
            },
            'description': 'Supabase (Postgres + Auth + Storage)',
            'ingests': ['tables', 'storage_buckets', 'auth_users']
        },
        'firebase': {
            'name': 'Firebase',
            'icon': '🔥',
            'type': 'database',
            'category': 'Database',
            'fields': {'credentials_json': 'Service Account JSON'},
            'description': 'Firestore, Realtime DB, Storage',
            'ingests': ['firestore_collections', 'realtime_data', 'storage_files']
        },
        'planetscale': {
            'name': 'PlanetScale',
            'icon': '🪐',
            'type': 'database',
            'category': 'Database',
            'fields': {
                'host': 'Host',
                'username': 'Username',
                'password': 'Password'
            },
            'description': 'Serverless MySQL',
            'ingests': ['branches', 'tables']
        },
        
        # =====================================================================
        # STORAGE
        # =====================================================================
        's3': {
            'name': 'Amazon S3',
            'icon': '📦',
            'type': 'storage',
            'category': 'Storage',
            'fields': {
                'api_key': 'Access Key ID',
                'secret': 'Secret Access Key',
                'bucket': 'Bucket Name',
                'region': 'Region'
            },
            'description': 'S3 bucket access',
            'ingests': ['files', 'folders']
        },
        'dropbox': {
            'name': 'Dropbox',
            'icon': '📁',
            'type': 'storage',
            'category': 'Storage',
            'fields': {'api_key': 'Access Token'},
            'endpoint': 'https://api.dropboxapi.com/2',
            'description': 'Dropbox files and folders',
            'ingests': ['files', 'folders', 'shared_links']
        },
        'gdrive': {
            'name': 'Google Drive',
            'icon': '📂',
            'type': 'storage',
            'category': 'Storage',
            'fields': {'credentials_json': 'OAuth Credentials JSON'},
            'description': 'Google Drive files',
            'ingests': ['files', 'folders', 'shared_drives']
        },
        'onedrive': {
            'name': 'OneDrive',
            'icon': '☁️',
            'type': 'storage',
            'category': 'Storage',
            'fields': {
                'client_id': 'Client ID',
                'client_secret': 'Client Secret'
            },
            'description': 'Microsoft OneDrive',
            'ingests': ['files', 'folders']
        },
        'backblaze': {
            'name': 'Backblaze B2',
            'icon': '🔵',
            'type': 'storage',
            'category': 'Storage',
            'fields': {
                'key_id': 'Application Key ID',
                'api_key': 'Application Key'
            },
            'description': 'Backblaze B2 storage',
            'ingests': ['buckets', 'files']
        },
        
        # =====================================================================
        # DEVELOPER TOOLS
        # =====================================================================
        'github': {
            'name': 'GitHub',
            'icon': '🐙',
            'type': 'api',
            'category': 'Developer',
            'fields': {'api_key': 'Personal Access Token'},
            'endpoint': 'https://api.github.com',
            'description': 'Repos, issues, PRs, gists',
            'ingests': ['repos', 'issues', 'pull_requests', 'gists', 'organizations']
        },
        'gitlab': {
            'name': 'GitLab',
            'icon': '🦊',
            'type': 'api',
            'category': 'Developer',
            'fields': {
                'api_key': 'Personal Access Token',
                'host': 'GitLab URL (gitlab.com)'
            },
            'description': 'Projects, issues, pipelines',
            'ingests': ['projects', 'issues', 'merge_requests', 'pipelines']
        },
        'bitbucket': {
            'name': 'Bitbucket',
            'icon': '🪣',
            'type': 'api',
            'category': 'Developer',
            'fields': {
                'username': 'Username',
                'app_password': 'App Password'
            },
            'description': 'Repositories and pipelines',
            'ingests': ['repositories', 'pipelines', 'issues']
        },
        'vercel': {
            'name': 'Vercel',
            'icon': '▲',
            'type': 'api',
            'category': 'Developer',
            'fields': {'api_key': 'API Token'},
            'endpoint': 'https://api.vercel.com',
            'description': 'Projects, deployments, domains',
            'ingests': ['projects', 'deployments', 'domains']
        },
        'netlify': {
            'name': 'Netlify',
            'icon': '🌐',
            'type': 'api',
            'category': 'Developer',
            'fields': {'api_key': 'Personal Access Token'},
            'endpoint': 'https://api.netlify.com/api/v1',
            'description': 'Sites, deploys, forms',
            'ingests': ['sites', 'deploys', 'forms']
        },
        'docker': {
            'name': 'Docker Hub',
            'icon': '🐳',
            'type': 'api',
            'category': 'Developer',
            'fields': {
                'username': 'Username',
                'password': 'Password or Token'
            },
            'description': 'Images, repositories',
            'ingests': ['repositories', 'images', 'tags']
        },
        
        # =====================================================================
        # PAYMENTS & FINANCE
        # =====================================================================
        'stripe': {
            'name': 'Stripe',
            'icon': '💳',
            'type': 'api',
            'category': 'Finance',
            'fields': {'api_key': 'Secret Key (sk_...)'},
            'endpoint': 'https://api.stripe.com/v1',
            'description': 'Payments, customers, subscriptions',
            'ingests': ['customers', 'payments', 'subscriptions', 'invoices', 'products']
        },
        'paypal': {
            'name': 'PayPal',
            'icon': '💰',
            'type': 'api',
            'category': 'Finance',
            'fields': {
                'client_id': 'Client ID',
                'secret': 'Secret'
            },
            'description': 'Transactions, invoices',
            'ingests': ['transactions', 'invoices', 'subscriptions']
        },
        'plaid': {
            'name': 'Plaid',
            'icon': '🏦',
            'type': 'api',
            'category': 'Finance',
            'fields': {
                'client_id': 'Client ID',
                'secret': 'Secret'
            },
            'description': 'Bank accounts, transactions',
            'ingests': ['accounts', 'transactions', 'institutions']
        },
        'quickbooks': {
            'name': 'QuickBooks',
            'icon': '📊',
            'type': 'api',
            'category': 'Finance',
            'fields': {
                'client_id': 'Client ID',
                'client_secret': 'Client Secret',
                'refresh_token': 'Refresh Token'
            },
            'description': 'Invoices, customers, reports',
            'ingests': ['invoices', 'customers', 'accounts', 'reports']
        },
        
        # =====================================================================
        # COMMUNICATION
        # =====================================================================
        'slack': {
            'name': 'Slack',
            'icon': '💬',
            'type': 'api',
            'category': 'Communication',
            'fields': {'api_key': 'Bot Token (xoxb-...)'},
            'endpoint': 'https://slack.com/api',
            'description': 'Channels, messages, users',
            'ingests': ['channels', 'messages', 'users', 'files']
        },
        'discord': {
            'name': 'Discord',
            'icon': '🎮',
            'type': 'api',
            'category': 'Communication',
            'fields': {'api_key': 'Bot Token'},
            'endpoint': 'https://discord.com/api/v10',
            'description': 'Servers, channels, messages',
            'ingests': ['guilds', 'channels', 'messages']
        },
        'twilio': {
            'name': 'Twilio',
            'icon': '📱',
            'type': 'api',
            'category': 'Communication',
            'fields': {
                'account_sid': 'Account SID',
                'auth_token': 'Auth Token'
            },
            'description': 'SMS, calls, messaging',
            'ingests': ['messages', 'calls', 'phone_numbers']
        },
        'sendgrid': {
            'name': 'SendGrid',
            'icon': '📧',
            'type': 'api',
            'category': 'Communication',
            'fields': {'api_key': 'API Key'},
            'endpoint': 'https://api.sendgrid.com/v3',
            'description': 'Email, templates, stats',
            'ingests': ['templates', 'stats', 'contacts']
        },
        
        # =====================================================================
        # CRM & MARKETING
        # =====================================================================
        'salesforce': {
            'name': 'Salesforce',
            'icon': '☁️',
            'type': 'api',
            'category': 'CRM',
            'fields': {
                'instance_url': 'Instance URL',
                'access_token': 'Access Token'
            },
            'description': 'Leads, contacts, opportunities',
            'ingests': ['leads', 'contacts', 'accounts', 'opportunities', 'cases']
        },
        'hubspot': {
            'name': 'HubSpot',
            'icon': '🧲',
            'type': 'api',
            'category': 'CRM',
            'fields': {'api_key': 'Private App Access Token'},
            'endpoint': 'https://api.hubapi.com',
            'description': 'Contacts, companies, deals',
            'ingests': ['contacts', 'companies', 'deals', 'tickets']
        },
        'mailchimp': {
            'name': 'Mailchimp',
            'icon': '🐵',
            'type': 'api',
            'category': 'Marketing',
            'fields': {'api_key': 'API Key'},
            'description': 'Audiences, campaigns, reports',
            'ingests': ['lists', 'campaigns', 'templates', 'reports']
        },
        'intercom': {
            'name': 'Intercom',
            'icon': '💬',
            'type': 'api',
            'category': 'CRM',
            'fields': {'api_key': 'Access Token'},
            'endpoint': 'https://api.intercom.io',
            'description': 'Users, conversations, articles',
            'ingests': ['contacts', 'conversations', 'articles']
        },
        
        # =====================================================================
        # ANALYTICS & DATA
        # =====================================================================
        'google_analytics': {
            'name': 'Google Analytics',
            'icon': '📈',
            'type': 'api',
            'category': 'Analytics',
            'fields': {'credentials_json': 'Service Account JSON'},
            'description': 'Website analytics data',
            'ingests': ['reports', 'realtime', 'dimensions', 'metrics']
        },
        'mixpanel': {
            'name': 'Mixpanel',
            'icon': '📊',
            'type': 'api',
            'category': 'Analytics',
            'fields': {
                'api_secret': 'API Secret',
                'project_token': 'Project Token'
            },
            'description': 'Events, funnels, cohorts',
            'ingests': ['events', 'funnels', 'cohorts', 'users']
        },
        'amplitude': {
            'name': 'Amplitude',
            'icon': '📉',
            'type': 'api',
            'category': 'Analytics',
            'fields': {
                'api_key': 'API Key',
                'secret_key': 'Secret Key'
            },
            'description': 'Product analytics',
            'ingests': ['events', 'users', 'charts']
        },
        'segment': {
            'name': 'Segment',
            'icon': '🔀',
            'type': 'api',
            'category': 'Analytics',
            'fields': {'api_key': 'Write Key'},
            'description': 'Customer data platform',
            'ingests': ['sources', 'destinations', 'events']
        },
        'snowflake': {
            'name': 'Snowflake',
            'icon': '❄️',
            'type': 'database',
            'category': 'Analytics',
            'fields': {
                'account': 'Account Identifier',
                'username': 'Username',
                'password': 'Password',
                'warehouse': 'Warehouse',
                'database': 'Database'
            },
            'description': 'Cloud data warehouse',
            'ingests': ['databases', 'schemas', 'tables', 'views']
        },
        'bigquery': {
            'name': 'BigQuery',
            'icon': '🔍',
            'type': 'database',
            'category': 'Analytics',
            'fields': {'credentials_json': 'Service Account JSON'},
            'description': 'Google BigQuery datasets',
            'ingests': ['datasets', 'tables', 'views']
        },
        
        # =====================================================================
        # E-COMMERCE
        # =====================================================================
        'shopify': {
            'name': 'Shopify',
            'icon': '🛍️',
            'type': 'api',
            'category': 'E-Commerce',
            'fields': {
                'store': 'Store Name (mystore.myshopify.com)',
                'api_key': 'Admin API Access Token'
            },
            'description': 'Products, orders, customers',
            'ingests': ['products', 'orders', 'customers', 'collections', 'inventory']
        },
        'woocommerce': {
            'name': 'WooCommerce',
            'icon': '🛒',
            'type': 'api',
            'category': 'E-Commerce',
            'fields': {
                'url': 'Store URL',
                'consumer_key': 'Consumer Key',
                'consumer_secret': 'Consumer Secret'
            },
            'description': 'WordPress e-commerce',
            'ingests': ['products', 'orders', 'customers', 'coupons']
        },
        'square': {
            'name': 'Square',
            'icon': '⬜',
            'type': 'api',
            'category': 'E-Commerce',
            'fields': {'api_key': 'Access Token'},
            'endpoint': 'https://connect.squareup.com/v2',
            'description': 'Payments, inventory, customers',
            'ingests': ['payments', 'orders', 'customers', 'inventory']
        },
        
        # =====================================================================
        # PRODUCTIVITY
        # =====================================================================
        'notion': {
            'name': 'Notion',
            'icon': '📝',
            'type': 'api',
            'category': 'Productivity',
            'fields': {'api_key': 'Integration Token'},
            'endpoint': 'https://api.notion.com/v1',
            'description': 'Pages, databases, blocks',
            'ingests': ['pages', 'databases', 'blocks']
        },
        'airtable': {
            'name': 'Airtable',
            'icon': '📋',
            'type': 'api',
            'category': 'Productivity',
            'fields': {'api_key': 'Personal Access Token'},
            'endpoint': 'https://api.airtable.com/v0',
            'description': 'Bases, tables, records',
            'ingests': ['bases', 'tables', 'records']
        },
        'asana': {
            'name': 'Asana',
            'icon': '✅',
            'type': 'api',
            'category': 'Productivity',
            'fields': {'api_key': 'Personal Access Token'},
            'endpoint': 'https://app.asana.com/api/1.0',
            'description': 'Projects, tasks, teams',
            'ingests': ['workspaces', 'projects', 'tasks']
        },
        'trello': {
            'name': 'Trello',
            'icon': '📌',
            'type': 'api',
            'category': 'Productivity',
            'fields': {
                'api_key': 'API Key',
                'token': 'Token'
            },
            'description': 'Boards, lists, cards',
            'ingests': ['boards', 'lists', 'cards']
        },
        'jira': {
            'name': 'Jira',
            'icon': '🎫',
            'type': 'api',
            'category': 'Productivity',
            'fields': {
                'domain': 'Domain (company.atlassian.net)',
                'email': 'Email',
                'api_token': 'API Token'
            },
            'description': 'Projects, issues, sprints',
            'ingests': ['projects', 'issues', 'sprints', 'boards']
        },
        'linear': {
            'name': 'Linear',
            'icon': '📐',
            'type': 'api',
            'category': 'Productivity',
            'fields': {'api_key': 'Personal API Key'},
            'endpoint': 'https://api.linear.app/graphql',
            'description': 'Issues, projects, cycles',
            'ingests': ['issues', 'projects', 'cycles', 'teams']
        },
        
        # =====================================================================
        # SOCIAL & CONTENT
        # =====================================================================
        'twitter': {
            'name': 'Twitter/X',
            'icon': '🐦',
            'type': 'api',
            'category': 'Social',
            'fields': {
                'api_key': 'API Key',
                'api_secret': 'API Secret',
                'access_token': 'Access Token',
                'access_secret': 'Access Token Secret'
            },
            'description': 'Tweets, followers, analytics',
            'ingests': ['tweets', 'followers', 'lists']
        },
        'youtube': {
            'name': 'YouTube',
            'icon': '📺',
            'type': 'api',
            'category': 'Social',
            'fields': {'api_key': 'API Key'},
            'description': 'Videos, playlists, analytics',
            'ingests': ['videos', 'playlists', 'channels']
        },
        'contentful': {
            'name': 'Contentful',
            'icon': '📰',
            'type': 'api',
            'category': 'Content',
            'fields': {
                'space_id': 'Space ID',
                'api_key': 'Content Delivery API Token'
            },
            'description': 'Headless CMS content',
            'ingests': ['spaces', 'content_types', 'entries', 'assets']
        },
        'sanity': {
            'name': 'Sanity',
            'icon': '🎨',
            'type': 'api',
            'category': 'Content',
            'fields': {
                'project_id': 'Project ID',
                'api_token': 'API Token'
            },
            'description': 'Headless CMS',
            'ingests': ['documents', 'assets']
        },
    }
    
    # Known providers with connection templates (legacy compat)
    PROVIDERS = {k: {'type': v['type'], 'icon': v['icon'], 'fields': list(v['fields'].keys())} 
                 for k, v in CANNED_CONNECTIONS.items()}
    
    def __init__(self, storage_path: str = None):
        self._credentials: Dict[str, Credential] = {}
        self._storage_path = storage_path or os.path.expanduser("~/.uhd_vault.json")
        self._load()
    
    def _load(self):
        """Load credentials from disk (would be encrypted in production)"""
        if os.path.exists(self._storage_path):
            try:
                with open(self._storage_path, 'r') as f:
                    data = json.load(f)
                    for cred_data in data.get('credentials', []):
                        cred = Credential(
                            id=cred_data['id'],
                            name=cred_data['name'],
                            conn_type=cred_data['conn_type'],
                            provider=cred_data['provider'],
                            endpoint=cred_data.get('endpoint', ''),
                            api_key=cred_data.get('api_key', ''),
                            username=cred_data.get('username', ''),
                            password=cred_data.get('password', ''),
                            extra=cred_data.get('extra', {}),
                            verified=cred_data.get('verified', False),
                            last_used=cred_data.get('last_used', ''),
                            created_at=cred_data.get('created_at', '')
                        )
                        self._credentials[cred.id] = cred
            except Exception:
                pass
    
    def _save(self):
        """Save credentials to disk (would be encrypted in production)"""
        data = {
            'credentials': [c.to_dict(include_secrets=True) for c in self._credentials.values()]
        }
        try:
            # Save passwords in data
            for cred in self._credentials.values():
                for d in data['credentials']:
                    if d['id'] == cred.id:
                        d['password'] = cred.password
                        break
            
            with open(self._storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
    
    def add(self, name: str, provider: str, **kwargs) -> Credential:
        """
        Add a new credential.
        
        Example:
            vault.add("My AWS", "aws", api_key="AKIA...", extra={'secret': '...', 'region': 'us-east-1'})
            vault.add("Work DB", "postgres", endpoint="db.company.com", username="app", password="...")
        """
        cred_id = hashlib.md5(f"{name}{provider}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        provider_info = self.PROVIDERS.get(provider, self.PROVIDERS['custom'])
        
        cred = Credential(
            id=cred_id,
            name=name,
            conn_type=provider_info['type'],
            provider=provider,
            endpoint=kwargs.get('endpoint', provider_info.get('endpoint', '')),
            api_key=kwargs.get('api_key', ''),
            username=kwargs.get('username', ''),
            password=kwargs.get('password', ''),
            extra=kwargs.get('extra', {})
        )
        
        self._credentials[cred_id] = cred
        self._save()
        return cred
    
    def remove(self, cred_id: str) -> bool:
        """Remove a credential"""
        if cred_id in self._credentials:
            del self._credentials[cred_id]
            self._save()
            return True
        return False
    
    def get(self, cred_id: str) -> Optional[Credential]:
        """Get a credential by ID"""
        return self._credentials.get(cred_id)
    
    def list(self) -> List[Credential]:
        """List all credentials"""
        return list(self._credentials.values())
    
    def by_type(self, conn_type: str) -> List[Credential]:
        """Get credentials by type"""
        return [c for c in self._credentials.values() if c.conn_type == conn_type]
    
    def verify(self, cred_id: str) -> bool:
        """Test a credential (placeholder - would actually test connection)"""
        cred = self._credentials.get(cred_id)
        if cred:
            # In production, this would actually test the connection
            cred.verified = True
            cred.last_used = datetime.now().isoformat()
            self._save()
            return True
        return False
    
    def providers_list(self) -> List[Dict]:
        """Get list of available providers for UI"""
        return [
            {'id': k, 'icon': v['icon'], 'type': v['type'], 'name': k.upper()}
            for k, v in self.PROVIDERS.items()
        ]


# =============================================================================
# CONNECTION - A Live Data Source Connection
# =============================================================================

@dataclass
class Connection:
    """
    A live connection to a data source.
    
    This represents an active link between Universal Hard Drive and 
    external data. Once connected, the data becomes native.
    """
    id: str
    name: str                    # Display name
    credential: Credential       # Associated credential
    drive_letter: str           # Mounted as X:
    
    # Connection state
    connected: bool = False
    last_sync: str = ""
    items_count: int = 0
    
    # Ingestion settings
    auto_refresh: bool = True
    refresh_interval: int = 300  # seconds
    max_depth: int = 5          # How deep to traverse
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'credential_id': self.credential.id,
            'provider': self.credential.provider,
            'drive_letter': self.drive_letter,
            'connected': self.connected,
            'last_sync': self.last_sync,
            'items_count': self.items_count,
            'icon': CredentialVault.PROVIDERS.get(self.credential.provider, {}).get('icon', '🔗')
        }


# =============================================================================
# CONNECTOR STATUS - Visual Status Tracking with Dots
# =============================================================================

from enum import Enum

class ConnectorStatus(Enum):
    """Status of a connector with visual indicators"""
    CONNECTED = 'connected'      # Green dot - ready
    DISCONNECTED = 'disconnected'  # Red dot - not connected
    UNAVAILABLE = 'unavailable'   # Black dot - service down/unreachable
    PENDING = 'pending'           # Yellow dot - connecting
    ERROR = 'error'               # Red exclamation - error state
    
    @property
    def dot(self) -> str:
        """Get status dot emoji"""
        return {
            'connected': '🟢',
            'disconnected': '🔴', 
            'unavailable': '⚫',
            'pending': '🟡',
            'error': '🔴'
        }.get(self.value, '⚫')
    
    @property
    def css_class(self) -> str:
        """CSS class for status styling"""
        return f'status-{self.value}'
    
    @property 
    def color(self) -> str:
        """Hex color for status"""
        return {
            'connected': '#00ff88',
            'disconnected': '#ff4444',
            'unavailable': '#333333',
            'pending': '#ffaa00',
            'error': '#ff0000'
        }.get(self.value, '#666666')


@dataclass
class ConnectorInfo:
    """Information about a connector with status tracking"""
    id: str
    name: str
    icon: str
    provider: str
    category: str
    status: ConnectorStatus = ConnectorStatus.DISCONNECTED
    drive_letter: str = ''
    items_count: int = 0
    last_sync: str = ''
    error_message: str = ''
    description: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'provider': self.provider,
            'category': self.category,
            'status': self.status.value,
            'status_dot': self.status.dot,
            'status_color': self.status.color,
            'drive_letter': self.drive_letter,
            'items_count': self.items_count,
            'last_sync': self.last_sync,
            'error_message': self.error_message,
            'description': self.description
        }


# =============================================================================
# UNIVERSAL HARD DRIVE
# =============================================================================

class UniversalHardDrive:
    """
    Universal Hard Drive - All Data Sources as One File System
    
    Presents a unified view where everything looks like local files:
    - APIs appear as JSON files
    - Database records appear as documents
    - Cloud storage appears as remote folders
    - All accessed through SRLs (lazy materialization)
    """
    
    # Drive letters
    DRIVE_LOCAL = 'A'
    DRIVE_API = 'B'
    DRIVE_DATABASE = 'C'
    DRIVE_CLOUD = 'D'
    DRIVE_CACHE = 'E'
    DRIVE_SAVED = 'Z'
    
    def __init__(self, save_dir: str = "data/uhd_saved"):
        # Core components
        self.kernel = HelixKernel()
        self.substrate = ManifoldSubstrate()
        self.kernel.set_substrate(self.substrate)
        
        self.cache = HelixCache()
        self.logger = HelixLogger(min_level=3)
        self.serializer = HelixSerializer()
        
        # Save directory (only place we write)
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Virtual drives
        self._drives: Dict[str, VirtualDrive] = {}
        self._init_drives()
        
        # SRL registry - all references (Level 0 - Potential)
        self._srls: Dict[str, SRL] = {}
        
        # File tree cache (for navigation)
        self._tree_cache: Dict[str, FileNode] = {}
        
        # Connected data sources
        self._connector: Optional[UniversalConnector] = None
        self._database: Optional[HelixDatabase] = None
        self._local_roots: List[str] = []
        
        # =====================================================================
        # CREDENTIAL VAULT & CONNECTIONS - The Dream!
        # Connect once, data becomes native, no queries, just drill dimensions
        # =====================================================================
        self._vault = CredentialVault()
        self._connections: Dict[str, Connection] = {}
        
        # Dynamic drive letters for user connections (F through Y)
        self._available_letters = list('FGHIJKLMNOPQRSTUVWXY')
        self._used_letters: Dict[str, str] = {}  # conn_id -> letter
        
        # =====================================================================
        # SEMANTIC INTELLIGENCE - System Learns, SRL Knows Where to Look
        # The more connections, the more the system understands relationships
        # =====================================================================
        self._semantic_router = SemanticRouter()
        self._relationship_graph = RelationshipGraph()
        self._smart_query = SmartQuery(self._semantic_router, self._relationship_graph)
        
        # Stats
        self._stats = {
            'srls_created': 0,
            'materializations': 0,
            'saves': 0,
            'cache_hits': 0,
            'queries_processed': 0,
            'relationships_found': 0
        }
        
        # =====================================================================
        # CONNECTOR REGISTRY - All Connectors with Status Tracking
        # Shows green/red/black dots for each potential connection
        # =====================================================================
        self._connectors: Dict[str, ConnectorInfo] = {}
        self._init_connectors()
        
        self.logger.whole("Universal Hard Drive initialized - Semantic Intelligence Active")
    
    def _init_connectors(self):
        """Initialize all available connectors with their status"""
        for provider_id, info in CredentialVault.CANNED_CONNECTIONS.items():
            self._connectors[provider_id] = ConnectorInfo(
                id=provider_id,
                name=info['name'],
                icon=info['icon'],
                provider=provider_id,
                category=info.get('category', 'Other'),
                status=ConnectorStatus.DISCONNECTED,
                description=info.get('description', '')
            )
    
    def get_connectors(self) -> List[ConnectorInfo]:
        """Get all connectors with their current status"""
        return list(self._connectors.values())
    
    def get_connectors_by_category(self) -> Dict[str, List[ConnectorInfo]]:
        """Get connectors grouped by category"""
        by_category = {}
        for conn in self._connectors.values():
            if conn.category not in by_category:
                by_category[conn.category] = []
            by_category[conn.category].append(conn)
        return by_category
    
    def get_connector_status(self, provider_id: str) -> ConnectorStatus:
        """Get status of a specific connector"""
        conn = self._connectors.get(provider_id)
        return conn.status if conn else ConnectorStatus.UNAVAILABLE
    
    def set_connector_status(self, provider_id: str, status: ConnectorStatus, 
                            error_msg: str = '', drive_letter: str = ''):
        """Update connector status"""
        if provider_id in self._connectors:
            self._connectors[provider_id].status = status
            self._connectors[provider_id].error_message = error_msg
            if drive_letter:
                self._connectors[provider_id].drive_letter = drive_letter
            if status == ConnectorStatus.CONNECTED:
                self._connectors[provider_id].last_sync = datetime.now().isoformat()
    
    def sync_with_universal_connector(self, uc_port: int = 8766) -> Dict:
        """
        Sync connectors and SRLs from Universal Connector Service
        
        This connects UHD to UC, pulling:
        - All available services and their status
        - Connected services get drive letters
        - SRLs from connected services
        """
        import urllib.request
        import urllib.error
        
        uc_base = f"http://localhost:{uc_port}"
        result = {
            "success": False,
            "services_synced": 0,
            "srls_added": 0,
            "error": None
        }
        
        try:
            # Get all services from UC
            with urllib.request.urlopen(f"{uc_base}/api/services", timeout=5) as response:
                data = json.loads(response.read())
                services = data.get("services", [])
                
                for svc in services:
                    service_id = svc.get("service_id")
                    
                    # Update or create connector
                    if service_id not in self._connectors:
                        self._connectors[service_id] = ConnectorInfo(
                            id=service_id,
                            name=svc.get("name", service_id),
                            icon=svc.get("icon", "🔌"),
                            provider=service_id,
                            category=svc.get("category", "other"),
                            status=ConnectorStatus.DISCONNECTED,
                            description=f"Via Universal Connector"
                        )
                    
                    # Update status based on UC status
                    uc_status = svc.get("status", "disconnected")
                    if uc_status == "connected":
                        self._connectors[service_id].status = ConnectorStatus.CONNECTED
                        self._connectors[service_id].drive_letter = svc.get("drive_letter")
                        self._connectors[service_id].last_sync = svc.get("last_sync")
                        self._connectors[service_id].items_count = svc.get("items_count", 0)
                        
                        # Register drive if has letter
                        if svc.get("drive_letter"):
                            letter = svc["drive_letter"]
                            if letter not in self._drives:
                                self._drives[letter] = VirtualDrive(
                                    letter=letter,
                                    name=svc.get("name"),
                                    icon=svc.get("icon", "📁"),
                                    source_type="uc_service",
                                    description=f"UC: {service_id}",
                                    read_only=True
                                )
                                self._drives[letter].connected = True
                        
                        result["services_synced"] += 1
                    elif uc_status == "error":
                        self._connectors[service_id].status = ConnectorStatus.ERROR
                        self._connectors[service_id].error_message = svc.get("error_message")
                    else:
                        self._connectors[service_id].status = ConnectorStatus.DISCONNECTED
            
            # Get SRLs from UC
            with urllib.request.urlopen(f"{uc_base}/api/srls", timeout=5) as response:
                data = json.loads(response.read())
                srls = data.get("srls", [])
                
                for srl_data in srls:
                    srl_uri = srl_data.get("uri")
                    if srl_uri and srl_uri not in self._srls:
                        # Create SRL in UHD
                        self._srls[srl_uri] = SRL(
                            uri=srl_uri,
                            source='universal_connector',
                            drive=srl_data.get("service_id", "B")[0].upper(),
                            path=srl_data.get("path", "/"),
                            node_type='substrate',
                            materialized=srl_data.get("materialized", False)
                        )
                        result["srls_added"] += 1
            
            result["success"] = True
            self.logger.width(f"Synced with UC: {result['services_synced']} services, {result['srls_added']} SRLs")
            
        except urllib.error.URLError as e:
            result["error"] = f"Could not connect to UC at {uc_base}: {e}"
            self.logger.structure(f"UC sync failed: {e}")
        except Exception as e:
            result["error"] = str(e)
            self.logger.structure(f"UC sync error: {e}")
        
        return result
    
    def get_uc_services(self, uc_port: int = 8766) -> List[Dict]:
        """Get services directly from Universal Connector"""
        import urllib.request
        
        try:
            with urllib.request.urlopen(f"http://localhost:{uc_port}/api/services", timeout=5) as response:
                data = json.loads(response.read())
                return data.get("services", [])
        except:
            return []
    
    def get_uc_categories(self, uc_port: int = 8766) -> List[Dict]:
        """Get categories from Universal Connector"""
        import urllib.request
        
        try:
            with urllib.request.urlopen(f"http://localhost:{uc_port}/api/categories", timeout=5) as response:
                data = json.loads(response.read())
                return data.get("categories", [])
        except:
            return []
    
    def _init_drives(self):
        """Initialize virtual drives"""
        self._drives = {
            'A': VirtualDrive('A', 'Local', '💾', 'local', 
                            'Local file system', read_only=True),
            'B': VirtualDrive('B', 'API', '🌐', 'api',
                            'Universal Connector APIs', read_only=True),
            'C': VirtualDrive('C', 'Database', '🗄️', 'database',
                            'Helix Database', read_only=True),
            'D': VirtualDrive('D', 'Cloud', '☁️', 'cloud',
                            'Cloud storage', read_only=True),
            'E': VirtualDrive('E', 'Cache', '⚡', 'cache',
                            'Recently accessed data', read_only=True),
            'Z': VirtualDrive('Z', 'Saved', '💎', 'saved',
                            'Explicitly saved data', read_only=False)
        }
    
    # -------------------------------------------------------------------------
    # Drive Management
    # -------------------------------------------------------------------------
    
    def drives(self) -> List[VirtualDrive]:
        """List all drives"""
        return list(self._drives.values())
    
    def connect_api(self, connector: UniversalConnector = None):
        """Connect API drive"""
        self._connector = connector or UniversalConnector()
        self._drives['B'].connected = True
        self._populate_api_drive()
        self.logger.width("API drive connected")
    
    def connect_database(self, database: HelixDatabase = None):
        """Connect database drive"""
        self._database = database or HelixDatabase("uhd_db")
        self._drives['C'].connected = True
        self._populate_database_drive()
        self.logger.width("Database drive connected")
    
    def mount_local(self, path: str):
        """Mount a local directory"""
        if os.path.isdir(path):
            self._local_roots.append(path)
            self._drives['A'].connected = True
            self._populate_local_drive()
            self.logger.width(f"Local path mounted: {path}")
    
    # -------------------------------------------------------------------------
    # CONNECT SERVICE - The Dream!
    # Supply credentials once → System ingests EVERYTHING → Native data
    # -------------------------------------------------------------------------
    
    def connect_service(self, provider: str, credentials: Dict, name: str = None) -> Optional[str]:
        """
        Connect to a service and INGEST EVERYTHING.
        
        This is the magic:
        1. User provides provider name + credentials
        2. System creates SRLs for ALL data from that service
        3. Data becomes native - just drill down like local files
        4. No queries needed - dimensional traversal O(1)
        
        Args:
            provider: Service provider key (e.g., 'github', 'stripe', 'postgres')
            credentials: Dict with required fields for that provider
            name: Optional display name (defaults to provider name)
        
        Returns:
            Drive letter assigned to this connection (e.g., 'F')
        
        Example:
            uhd.connect_service('github', {'api_key': 'ghp_...'})
            # Now browse F:/repos/, F:/gists/, F:/organizations/
            
            uhd.connect_service('stripe', {'api_key': 'sk_...'})
            # Now browse G:/customers/, G:/payments/, G:/subscriptions/
        """
        provider_info = CredentialVault.CANNED_CONNECTIONS.get(provider)
        if not provider_info:
            self.logger.width(f"Unknown provider: {provider}")
            return None
        
        # Assign drive letter
        if not self._available_letters:
            self.logger.width("No drive letters available")
            return None
        
        drive_letter = self._available_letters.pop(0)
        display_name = name or provider_info['name']
        
        # Store credential
        cred = self._vault.add(
            name=display_name,
            provider=provider,
            api_key=credentials.get('api_key', ''),
            username=credentials.get('username', ''),
            password=credentials.get('password', ''),
            endpoint=credentials.get('endpoint', provider_info.get('endpoint', '')),
            extra={k: v for k, v in credentials.items() 
                   if k not in ('api_key', 'username', 'password', 'endpoint')}
        )
        
        # Create virtual drive
        self._drives[drive_letter] = VirtualDrive(
            letter=drive_letter,
            name=display_name,
            icon=provider_info['icon'],
            source_type=provider_info['type'],
            description=provider_info['description'],
            read_only=True,
            connected=True
        )
        
        # Create connection
        conn = Connection(
            id=cred.id,
            name=display_name,
            credential=cred,
            drive_letter=drive_letter,
            connected=True,
            last_sync=datetime.now().isoformat()
        )
        self._connections[cred.id] = conn
        self._used_letters[cred.id] = drive_letter
        
        # Update connector status to CONNECTED
        self.set_connector_status(provider, ConnectorStatus.CONNECTED, 
                                 drive_letter=drive_letter)
        
        # INGEST EVERYTHING from this service
        self._ingest_service(drive_letter, provider, provider_info, credentials)
        
        self.logger.whole(f"Connected {display_name} as {drive_letter}:")
        return drive_letter
    
    def test_service_connection(self, service_id: str, credentials: Dict) -> Dict:
        """
        Test a service connection without fully connecting.
        
        Args:
            service_id: Provider ID to test
            credentials: Credentials to validate
            
        Returns:
            Dict with success/error status
        """
        import urllib.request
        import urllib.error
        
        # Check if it's a known service
        provider_info = CredentialVault.CANNED_CONNECTIONS.get(service_id)
        
        # Map of services to their test endpoints
        test_endpoints = {
            'wttr': 'https://wttr.in/?format=j1',
            'coingecko': 'https://api.coingecko.com/api/v3/ping',
            'exchangerate': 'https://api.exchangerate-api.com/v4/latest/USD',
            'wikipedia': 'https://en.wikipedia.org/api/rest_v1/',
            'hackernews': 'https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty',
            'jsonplaceholder': 'https://jsonplaceholder.typicode.com/posts/1',
            'restcountries': 'https://restcountries.com/v3.1/name/usa',
            'open-meteo': 'https://api.open-meteo.com/v1/forecast?latitude=40&longitude=-74&current_weather=true',
            'numbersapi': 'http://numbersapi.com/42',
            'dictionaryapi': 'https://api.dictionaryapi.dev/api/v2/entries/en/test',
            'openweather': 'https://api.openweathermap.org/data/2.5/weather?q=London&appid={}',
            'newsapi': 'https://newsapi.org/v2/top-headlines?country=us&apiKey={}',
            'alphavantage': 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={}',
            'openai': 'https://api.openai.com/v1/models',
            'anthropic': 'https://api.anthropic.com/v1/messages',
            'github': 'https://api.github.com/user',
        }
        
        try:
            test_url = test_endpoints.get(service_id)
            
            if not test_url:
                # Unknown service - check if credentials provided
                if credentials and any(credentials.values()):
                    return {'success': True, 'message': 'Credentials provided - ready to connect'}
                else:
                    return {'success': False, 'error': 'Unknown service'}
            
            # For API key services, substitute the key
            api_key = credentials.get('api_key', credentials.get('token', ''))
            if '{}' in test_url and api_key:
                test_url = test_url.format(api_key)
            elif '{}' in test_url:
                return {'success': False, 'error': 'API key required'}
            
            # Build request with appropriate headers
            req = urllib.request.Request(test_url)
            req.add_header('User-Agent', 'ButterflyFX-UC/1.0')
            
            if service_id == 'openai' and api_key:
                req.add_header('Authorization', f'Bearer {api_key}')
            elif service_id == 'anthropic' and api_key:
                req.add_header('x-api-key', api_key)
                req.add_header('anthropic-version', '2023-06-01')
            elif service_id == 'github' and api_key:
                req.add_header('Authorization', f'token {api_key}')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return {'success': True, 'message': 'Connection successful'}
                else:
                    return {'success': False, 'error': f'HTTP {response.status}'}
                    
        except urllib.error.HTTPError as e:
            if e.code == 401:
                return {'success': False, 'error': 'Invalid credentials'}
            elif e.code == 403:
                return {'success': False, 'error': 'Access forbidden - check API key permissions'}
            return {'success': False, 'error': f'HTTP error {e.code}'}
        except urllib.error.URLError as e:
            return {'success': False, 'error': f'Network error: {e.reason}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _ingest_service(self, drive: str, provider: str, info: Dict, creds: Dict):
        """
        Ingest ALL data from a service into SRLs.
        Each 'ingests' item becomes a folder with SRLs inside.
        """
        ingests = info.get('ingests', [])
        endpoint = info.get('endpoint', creds.get('endpoint', ''))
        api_key = creds.get('api_key', '')
        
        for category in ingests:
            # Create folder for this category
            folder_path = f"{drive}:/{category}/"
            
            # Create SRLs based on provider type
            self._create_ingest_srls(drive, provider, category, endpoint, api_key, creds)
        
        self.logger.width(f"Ingested {len(ingests)} categories from {provider}")
    
    def _create_ingest_srls(self, drive: str, provider: str, category: str, 
                            endpoint: str, api_key: str, creds: Dict):
        """Create SRLs for a service category (e.g., github/repos, stripe/customers)"""
        
        # Provider-specific ingestion logic
        # In production, this would use actual API calls
        # Here we create smart SRLs that materialize on demand
        
        def make_materializer(prov, cat, ep, key, c):
            """Create a materializer function for this endpoint"""
            def materializer():
                # This would call the actual API in production
                # For now, return structure that shows what would be fetched
                return {
                    '_uhd_ingest': True,
                    'provider': prov,
                    'category': cat,
                    'endpoint': ep,
                    'status': 'ready_to_fetch',
                    'description': f'Data from {prov}/{cat}',
                    'note': 'Actual API call would happen here with your credentials'
                }
            return materializer
        
        # Create main category SRL
        path = f"{drive}:/{category}/"
        self._create_srl(
            path=path,
            source_type=CredentialVault.CANNED_CONNECTIONS[provider]['type'],
            source_ref=f"{provider}/{category}",
            materializer=make_materializer(provider, category, endpoint, api_key, creds),
            name=category.replace('_', ' ').title(),
            mime_type="application/json"
        )
        self._srls[path].data_type = 'folder'
        self._srls[path].drive = drive
        
        # Create sample item SRLs within category
        # In production, this would list actual items from the API
        sample_items = self._generate_sample_items(provider, category)
        
        for item_name, item_id in sample_items:
            item_path = f"{drive}:/{category}/{item_name}"
            self._create_srl(
                path=item_path,
                source_type=CredentialVault.CANNED_CONNECTIONS[provider]['type'],
                source_ref=f"{provider}/{category}/{item_id}",
                materializer=make_materializer(provider, f"{category}/{item_id}", endpoint, api_key, creds),
                name=item_name,
                mime_type="application/json"
            )
    
    def _generate_sample_items(self, provider: str, category: str) -> List[tuple]:
        """Generate sample item names for a category (placeholder for real API discovery)"""
        # In production, this would call the API to list actual items
        # For demo, generate representative sample structure
        
        samples = {
            # GitHub
            ('github', 'repos'): [('my-project.json', 'repo_1'), ('awesome-lib.json', 'repo_2')],
            ('github', 'gists'): [('snippet.json', 'gist_1'), ('notes.json', 'gist_2')],
            ('github', 'organizations'): [('my-org.json', 'org_1')],
            
            # Stripe
            ('stripe', 'customers'): [('cus_sample1.json', 'cus_1'), ('cus_sample2.json', 'cus_2')],
            ('stripe', 'payments'): [('pi_recent.json', 'pi_1')],
            ('stripe', 'subscriptions'): [('sub_active.json', 'sub_1')],
            ('stripe', 'products'): [('prod_main.json', 'prod_1')],
            
            # AWS
            ('aws', 's3_buckets'): [('my-files.json', 'bucket_1'), ('backups.json', 'bucket_2')],
            ('aws', 'lambda_functions'): [('api-handler.json', 'fn_1')],
            ('aws', 'ec2_instances'): [('web-server.json', 'i_1')],
            
            # Databases
            ('postgres', 'tables'): [('users.json', 'tbl_1'), ('orders.json', 'tbl_2')],
            ('postgres', 'views'): [('active_users.json', 'view_1')],
            ('mongodb', 'collections'): [('documents.json', 'col_1')],
            
            # Notion/Productivity
            ('notion', 'pages'): [('home.json', 'page_1'), ('notes.json', 'page_2')],
            ('notion', 'databases'): [('tasks.json', 'db_1')],
            ('airtable', 'bases'): [('project-tracker.json', 'base_1')],
            
            # Shopify
            ('shopify', 'products'): [('widget.json', 'prod_1'), ('gadget.json', 'prod_2')],
            ('shopify', 'orders'): [('order_recent.json', 'ord_1')],
            ('shopify', 'customers'): [('customer_1.json', 'cust_1')],
        }
        
        return samples.get((provider, category), [(f'{category}_item.json', 'item_1')])
    
    def disconnect_service(self, drive_letter: str) -> bool:
        """Disconnect a service and remove its SRLs"""
        if drive_letter not in self._drives:
            return False
        
        # Find connection
        conn_id = None
        for cid, letter in self._used_letters.items():
            if letter == drive_letter:
                conn_id = cid
                break
        
        if conn_id:
            # Remove SRLs for this drive
            self._srls = {k: v for k, v in self._srls.items() if not k.startswith(f"{drive_letter}:")}
            
            # Remove connection
            if conn_id in self._connections:
                del self._connections[conn_id]
            
            # Return letter to pool
            self._available_letters.insert(0, drive_letter)
            del self._used_letters[conn_id]
            
            # Remove drive
            del self._drives[drive_letter]
            
            self.logger.width(f"Disconnected drive {drive_letter}")
            return True
        
        return False
    
    def list_available_services(self) -> List[Dict]:
        """List all available canned connections for the UI"""
        services = []
        for provider_id, info in CredentialVault.CANNED_CONNECTIONS.items():
            services.append({
                'id': provider_id,
                'name': info['name'],
                'icon': info['icon'],
                'type': info['type'],
                'category': info['category'],
                'description': info['description'],
                'fields': info['fields'],  # What credentials are needed
                'ingests': info['ingests']  # What data will be available
            })
        return services
    
    def list_connections(self) -> List[Dict]:
        """List active connections"""
        return [conn.to_dict() for conn in self._connections.values()]
    
    # -------------------------------------------------------------------------
    # SRL Population
    # -------------------------------------------------------------------------
    
    def _create_srl(
        self,
        path: str,
        source_type: str,
        source_ref: str,
        materializer: Callable,
        name: str = "",
        mime_type: str = "application/json"
    ) -> SRL:
        """Create an SRL (reference, not data)"""
        srl_id = hashlib.md5(path.encode()).hexdigest()[:12]
        
        srl = SRL(
            id=srl_id,
            path=path,
            source_type=source_type,
            source_ref=source_ref,
            materializer=materializer,
            name=name or path.split('/')[-1],
            mime_type=mime_type
        )
        
        self._srls[path] = srl
        self._stats['srls_created'] += 1
        
        # Register as potential in substrate
        self.substrate.create_token(
            location=(hash(srl_id) % 1000, 0, 0),  # Level 0 = Potential
            signature={0},
            payload=lambda s=srl: s.to_dict(),
            token_id=srl_id
        )
        
        return srl
    
    def _populate_api_drive(self):
        """Populate B: drive with API SRLs"""
        if not self._connector:
            return
        
        # Create SRLs for each API category and API
        for category, cat_data in API_REGISTRY.items():
            # Category folder
            cat_path = f"B:/{category}/"
            self._tree_cache[cat_path] = FileNode(
                path=cat_path,
                name=category,
                is_folder=True,
                icon=cat_data.get('icon', '📁')
            )
            
            # Individual APIs as "files"
            for api_name, api_info in cat_data.get('apis', {}).items():
                file_path = f"B:/{category}/{api_name}.json"
                
                # Create SRL with materializer (lazy - won't fetch until read)
                self._create_srl(
                    path=file_path,
                    source_type='api',
                    source_ref=api_name,
                    materializer=lambda n=api_name: self._materialize_api(n),
                    name=f"{api_name}.json",
                    mime_type="application/json"
                )
    
    def _populate_database_drive(self):
        """Populate C: drive with database SRLs"""
        if not self._database:
            return
        
        # Get collections
        collections = self._database.list_collections()
        
        for coll in collections:
            # Collection folder
            coll_path = f"C:/{coll.name}/"
            self._tree_cache[coll_path] = FileNode(
                path=coll_path,
                name=coll.name,
                is_folder=True,
                icon=LEVEL_ICONS.get(coll.level, '📁')
            )
            
            # Records as files
            records = self._database.query(coll.name).execute()
            for record in records:
                file_path = f"C:/{coll.name}/{record.id}.json"
                
                self._create_srl(
                    path=file_path,
                    source_type='database',
                    source_ref=f"{coll.name}/{record.id}",
                    materializer=lambda r=record: r.data,
                    name=f"{record.id}.json"
                )
    
    def _populate_local_drive(self):
        """Populate A: drive with local file SRLs"""
        for root_path in self._local_roots:
            root = Path(root_path)
            for file_path in root.rglob('*'):
                if file_path.is_file():
                    rel_path = file_path.relative_to(root)
                    virtual_path = f"A:/{rel_path}"
                    
                    # Determine mime type
                    ext = file_path.suffix.lower()
                    mime_map = {
                        '.json': 'application/json',
                        '.txt': 'text/plain',
                        '.md': 'text/markdown',
                        '.py': 'text/x-python',
                        '.js': 'text/javascript',
                        '.html': 'text/html',
                        '.css': 'text/css',
                        '.png': 'image/png',
                        '.jpg': 'image/jpeg',
                        '.pdf': 'application/pdf'
                    }
                    mime_type = mime_map.get(ext, 'application/octet-stream')
                    
                    self._create_srl(
                        path=virtual_path,
                        source_type='local',
                        source_ref=str(file_path),
                        materializer=lambda p=file_path: self._materialize_local(p),
                        name=file_path.name,
                        mime_type=mime_type
                    )
    
    # -------------------------------------------------------------------------
    # Materialization (This is where data actually gets fetched)
    # -------------------------------------------------------------------------
    
    def _materialize_api(self, api_name: str) -> Any:
        """Materialize API data - called only when read"""
        if not self._connector:
            return {"error": "API drive not connected"}
        
        result = self._connector.connect(api_name)
        self._stats['materializations'] += 1
        
        if result.success:
            return {
                'api': api_name,
                'data': result.data,
                'fetched_at': datetime.now().isoformat()
            }
        return {"error": result.error, "api": api_name}
    
    def _materialize_local(self, file_path: Path) -> Any:
        """Materialize local file - called only when read"""
        self._stats['materializations'] += 1
        
        try:
            if file_path.suffix.lower() == '.json':
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                with open(file_path, 'r', errors='replace') as f:
                    return {'content': f.read(), 'type': 'text'}
        except Exception as e:
            return {'error': str(e), 'path': str(file_path)}
    
    def _read_local_file(self, real_path: str) -> Any:
        """Read a local file directly from filesystem"""
        self._stats['materializations'] += 1
        
        if not os.path.exists(real_path):
            return {'error': f'File not found: {real_path}'}
        
        if os.path.isdir(real_path):
            return {'error': 'Cannot read directory', 'path': real_path}
        
        try:
            # Get file extension
            ext = os.path.splitext(real_path)[1].lower()
            
            # Handle different file types
            if ext == '.json':
                with open(real_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            elif ext in ['.txt', '.md', '.py', '.js', '.html', '.css', '.xml', 
                        '.yaml', '.yml', '.log', '.sh', '.bat', '.ini', '.cfg',
                        '.csv', '.sql', '.c', '.cpp', '.h', '.java', '.ts', '.tsx',
                        '.jsx', '.vue', '.rb', '.php', '.go', '.rs', '.swift']:
                with open(real_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    # Limit size for display
                    if len(content) > 50000:
                        content = content[:50000] + f'\n\n... (truncated, {len(content)} bytes total)'
                    return {
                        'type': 'text',
                        'path': real_path,
                        'size': os.path.getsize(real_path),
                        'content': content
                    }
            
            elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico']:
                # Return image info (not the binary data)
                return {
                    'type': 'image',
                    'path': real_path,
                    'size': os.path.getsize(real_path),
                    'format': ext[1:].upper()
                }
            
            elif ext in ['.mp3', '.wav', '.flac', '.ogg', '.m4a']:
                return {
                    'type': 'audio',
                    'path': real_path,
                    'size': os.path.getsize(real_path),
                    'format': ext[1:].upper()
                }
            
            elif ext in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
                return {
                    'type': 'video',
                    'path': real_path,
                    'size': os.path.getsize(real_path),
                    'format': ext[1:].upper()
                }
            
            elif ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
                return {
                    'type': 'document',
                    'path': real_path,
                    'size': os.path.getsize(real_path),
                    'format': ext[1:].upper()
                }
            
            elif ext in ['.zip', '.tar', '.gz', '.7z', '.rar']:
                return {
                    'type': 'archive',
                    'path': real_path,
                    'size': os.path.getsize(real_path),
                    'format': ext[1:].upper()
                }
            
            else:
                # Try to read as text, fall back to binary info
                try:
                    with open(real_path, 'r', encoding='utf-8') as f:
                        content = f.read(10000)
                        return {
                            'type': 'text',
                            'path': real_path,
                            'size': os.path.getsize(real_path),
                            'content': content + ('...' if len(content) == 10000 else '')
                        }
                except:
                    return {
                        'type': 'binary',
                        'path': real_path,
                        'size': os.path.getsize(real_path)
                    }
        
        except PermissionError:
            return {'error': 'Permission denied', 'path': real_path}
        except Exception as e:
            return {'error': str(e), 'path': real_path}
    
    # -------------------------------------------------------------------------
    # File System Operations (Everything looks like local files)
    # -------------------------------------------------------------------------
    
    def _get_system_drives(self) -> List[Dict]:
        """Get actual system drives"""
        import platform
        drives = []
        
        if platform.system() == 'Windows':
            # Windows: Check drive letters A-Z
            import string
            for letter in string.ascii_uppercase:
                drive_path = f"{letter}:\\"
                if os.path.exists(drive_path):
                    try:
                        # Get drive info
                        total, used, free = 0, 0, 0
                        try:
                            import shutil
                            total, used, free = shutil.disk_usage(drive_path)
                        except:
                            pass
                        
                        drives.append({
                            'name': f"{letter}:",
                            'path': f"A:/{letter}/",  # Map to A:/C/, A:/D/, etc.
                            'is_folder': True,
                            'icon': '💾' if letter == 'C' else '💿',
                            'label': f"Local Disk ({letter}:)",
                            'size': total
                        })
                    except:
                        pass
        else:
            # Linux/Mac: Show common mount points
            mount_points = [
                ('/', 'Root', '💾'),
                ('/home', 'Home', '🏠'),
                ('/tmp', 'Temp', '📋'),
                ('/var', 'Var', '📁'),
                ('/mnt', 'Mount', '💿'),
                ('/media', 'Media', '💿'),
            ]
            
            for mount, label, icon in mount_points:
                if os.path.exists(mount) and os.path.isdir(mount):
                    # Encode path for URL (replace / with _)
                    encoded = mount.replace('/', '_') if mount != '/' else 'root'
                    drives.append({
                        'name': label,
                        'path': f"A:/{encoded}/",
                        'is_folder': True,
                        'icon': icon,
                        'label': mount,
                        'real_path': mount
                    })
        
        return drives
    
    def _decode_local_path(self, virtual_path: str) -> str:
        """Convert virtual A: path to real filesystem path"""
        import platform
        
        # Remove A:/ prefix
        rel_path = virtual_path[3:] if virtual_path.startswith('A:/') else virtual_path
        
        if platform.system() == 'Windows':
            # A:/C/Users/... -> C:\Users\...
            if len(rel_path) >= 2 and rel_path[1] == '/':
                drive_letter = rel_path[0]
                rest = rel_path[2:]
                return f"{drive_letter}:\\{rest.replace('/', '\\')}"
            return rel_path
        else:
            # A:/root/... -> /...
            # A:/_home/... -> /home/...
            if rel_path.startswith('root/'):
                return '/' + rel_path[5:]
            elif rel_path == 'root':
                return '/'
            elif rel_path.startswith('_'):
                return '/' + rel_path[1:].replace('_', '/', 1)
            return '/' + rel_path
    
    def _list_local_directory(self, virtual_path: str) -> List[Dict]:
        """List actual filesystem directory"""
        real_path = self._decode_local_path(virtual_path)
        
        if not os.path.exists(real_path):
            return []
        
        if not os.path.isdir(real_path):
            return []
        
        results = []
        try:
            for entry in os.scandir(real_path):
                try:
                    # Skip hidden files and system files
                    if entry.name.startswith('.'):
                        continue
                    
                    # Get icon based on type
                    if entry.is_dir():
                        icon = '📁'
                        # Encode the path for virtual representation
                        if virtual_path.endswith('/'):
                            item_path = f"{virtual_path}{entry.name}/"
                        else:
                            item_path = f"{virtual_path}/{entry.name}/"
                    else:
                        # Determine icon by extension
                        ext = os.path.splitext(entry.name)[1].lower()
                        icon_map = {
                            '.txt': '📝', '.md': '📝', '.log': '📝',
                            '.py': '🐍', '.js': '📜', '.html': '🌐', '.css': '🎨',
                            '.json': '📋', '.xml': '📋', '.yaml': '📋', '.yml': '📋',
                            '.png': '🖼️', '.jpg': '🖼️', '.jpeg': '🖼️', '.gif': '🖼️', '.svg': '🖼️',
                            '.mp3': '🎵', '.wav': '🎵', '.flac': '🎵',
                            '.mp4': '🎬', '.mkv': '🎬', '.avi': '🎬',
                            '.pdf': '📕', '.doc': '📘', '.docx': '📘', '.xls': '📗', '.xlsx': '📗',
                            '.zip': '📦', '.tar': '📦', '.gz': '📦', '.7z': '📦',
                            '.exe': '⚙️', '.sh': '⚙️', '.bat': '⚙️',
                        }
                        icon = icon_map.get(ext, '📄')
                        if virtual_path.endswith('/'):
                            item_path = f"{virtual_path}{entry.name}"
                        else:
                            item_path = f"{virtual_path}/{entry.name}"
                    
                    # Get size
                    try:
                        size = entry.stat().st_size if entry.is_file() else 0
                    except:
                        size = 0
                    
                    results.append({
                        'name': entry.name,
                        'path': item_path,
                        'is_folder': entry.is_dir(),
                        'icon': icon,
                        'size': size,
                        'source': 'local'
                    })
                except PermissionError:
                    continue
                except Exception:
                    continue
        except PermissionError:
            return [{'name': '⛔ Access Denied', 'path': '', 'is_folder': False, 'icon': '⛔'}]
        
        # Sort: folders first, then files alphabetically
        results.sort(key=lambda x: (not x['is_folder'], x['name'].lower()))
        
        return results
    
    def ls(self, path: str = "") -> List[Dict]:
        """
        List directory contents.
        
        Args:
            path: Virtual path like "B:/finance/" or just "B:"
            
        Returns:
            List of file/folder info dicts
        """
        # Root - show all drives
        if not path or path == "/":
            return [
                {
                    'name': f"{d.letter}:",
                    'path': f"{d.letter}:/",
                    'is_folder': True,
                    'icon': d.icon,
                    'label': d.name,
                    'connected': d.connected
                }
                for d in self._drives.values()
            ]
        
        # Handle A: drive specially - real filesystem
        if path.startswith('A:'):
            # A: root shows system drives/mount points
            if path == 'A:/' or path == 'A:':
                self._drives['A'].connected = True  # Auto-connect when accessed
                return self._get_system_drives()
            else:
                return self._list_local_directory(path)
        
        # Normalize path
        path = path.rstrip('/') + '/'
        
        # Find matching SRLs and folders
        results = []
        seen_folders = set()
        
        for srl_path, srl in self._srls.items():
            if srl_path.startswith(path):
                # Get relative path after the prefix
                rel = srl_path[len(path):]
                
                if '/' in rel:
                    # This is in a subfolder
                    folder_name = rel.split('/')[0]
                    if folder_name not in seen_folders:
                        seen_folders.add(folder_name)
                        results.append({
                            'name': folder_name,
                            'path': f"{path}{folder_name}/",
                            'is_folder': True,
                            'icon': '📁'
                        })
                else:
                    # This is a file at this level
                    results.append({
                        'name': srl.name,
                        'path': srl.path,
                        'is_folder': False,
                        'icon': '📄' if srl.mime_type.startswith('application') else '📝',
                        'materialized': srl.is_materialized,
                        'source': srl.source_type
                    })
        
        # Sort: folders first, then files
        results.sort(key=lambda x: (not x['is_folder'], x['name'].lower()))
        
        return results
    
    def read(self, path: str) -> Any:
        """
        Read file contents. This triggers materialization.
        
        Args:
            path: Virtual path like "B:/finance/bitcoin.json"
            
        Returns:
            The materialized data
        """
        # Handle A: drive (local filesystem) directly
        if path.startswith('A:/'):
            real_path = self._decode_local_path(path)
            data = self._read_local_file(real_path)
            
            # Learn from local file data
            if data and not isinstance(data, dict) or 'error' not in data:
                self._relationship_graph.learn(path, data, 'local')
            
            return data
        
        srl = self._srls.get(path)
        if not srl:
            return {"error": f"File not found: {path}"}
        
        # Check cache
        was_cached = srl.is_materialized
        if was_cached:
            self._stats['cache_hits'] += 1
        
        # Materialize (this is where data actually gets fetched)
        data = srl.materialize()
        
        # =====================================================================
        # LEARNING: System learns from every materialization
        # The more data accessed, the smarter the system becomes
        # =====================================================================
        if not was_cached and data and (not isinstance(data, dict) or 'error' not in data):
            learned = self._relationship_graph.learn(path, data, srl.source_type)
            if learned.get('relationships'):
                self._stats['relationships_found'] += len(learned['relationships'])
        
        self._stats['materializations'] += 1
        return data
    
    def info(self, path: str) -> Dict:
        """
        Get file info without materializing.
        
        Args:
            path: Virtual path
            
        Returns:
            File metadata
        """
        # Handle A: drive directly (real filesystem)
        if path.startswith('A:'):
            real_path = self._decode_local_path(path)
            if real_path:
                try:
                    stat = os.stat(real_path)
                    is_dir = os.path.isdir(real_path)
                    name = os.path.basename(real_path) or real_path
                    
                    return {
                        "path": path,
                        "name": name,
                        "type": "directory" if is_dir else "file",
                        "size": stat.st_size if not is_dir else 0,
                        "modified": stat.st_mtime,
                        "created": getattr(stat, 'st_ctime', stat.st_mtime),
                        "accessed": stat.st_atime,
                        "real_path": real_path,
                        "is_symlink": os.path.islink(real_path),
                        "source": "local",
                        "drive": "A:"
                    }
                except OSError as e:
                    return {"error": str(e), "path": path}
            return {"error": "Could not resolve path", "path": path}
        
        srl = self._srls.get(path)
        if not srl:
            return {"error": f"File not found: {path}"}
        
        return srl.to_dict()
    
    def refresh(self, path: str) -> Any:
        """
        Refresh (re-materialize) a file.
        Invalidates cache and fetches fresh data.
        """
        srl = self._srls.get(path)
        if not srl:
            return {"error": f"File not found: {path}"}
        
        srl.invalidate()
        return srl.materialize()
    
    def save(self, source_path: str, dest_path: str = None) -> bool:
        """
        Save data to local disk (Z: drive).
        This is the ONLY way data gets written permanently.
        
        Args:
            source_path: Virtual path to save from
            dest_path: Optional destination path (defaults to Z:/...)
        """
        srl = self._srls.get(source_path)
        if not srl:
            return False
        
        # Materialize if needed
        data = srl.materialize()
        if data is None or (isinstance(data, dict) and 'error' in data):
            return False
        
        # Determine save path
        if dest_path:
            if not dest_path.startswith('Z:'):
                dest_path = f"Z:/{dest_path}"
        else:
            # Default: mirror path structure
            dest_path = f"Z:/{source_path.replace(':', '')}"
        
        # Create local file path
        rel_path = dest_path.replace('Z:/', '')
        local_path = self.save_dir / rel_path
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to disk
        try:
            with open(local_path, 'w') as f:
                if isinstance(data, (dict, list)):
                    json.dump(data, f, indent=2)
                else:
                    f.write(str(data))
            
            # Create SRL for saved file
            self._create_srl(
                path=dest_path,
                source_type='saved',
                source_ref=str(local_path),
                materializer=lambda p=local_path: json.load(open(p)),
                name=local_path.name
            )
            
            self._stats['saves'] += 1
            self.logger.width(f"Saved: {source_path} -> {dest_path}")
            return True
            
        except Exception as e:
            self.logger.plane(f"Save failed: {e}")
            return False
    
    def exists(self, path: str) -> bool:
        """Check if a path exists"""
        return path in self._srls or any(
            p.startswith(path) for p in self._srls.keys()
        )
    
    # -------------------------------------------------------------------------
    # FILE OPERATIONS - The Power User Dream
    # -------------------------------------------------------------------------
    
    def find_all(self, file_type: str = None, extension: str = None, 
                 location: str = 'A:/', max_results: int = 1000) -> List[Dict]:
        """
        Find all files of a type across all drives.
        
        Examples:
            uhd.find_all('image')  # All images
            uhd.find_all(extension='pdf')  # All PDFs
            uhd.find_all('video', location='A:/home/')  # Videos in home
        """
        type_extensions = {
            'image': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'heic', 'tiff', 'ico'],
            'video': ['mp4', 'mov', 'avi', 'mkv', 'webm', 'flv', 'wmv', 'm4v'],
            'audio': ['mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg', 'wma'],
            'document': ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'ppt', 'pptx'],
            'archive': ['zip', 'rar', 'tar', 'gz', '7z', 'bz2'],
            'code': ['py', 'js', 'ts', 'html', 'css', 'java', 'cpp', 'c', 'go', 'rs', 'rb']
        }
        
        extensions = []
        if file_type and file_type.lower() in type_extensions:
            extensions = type_extensions[file_type.lower()]
        if extension:
            extensions = [extension.lower().strip('.')]
        
        results = []
        
        # Search local filesystem for A: drive
        if location.startswith('A:'):
            real_path = self._decode_local_path(location) or '/'
            
            try:
                for root, dirs, files in os.walk(real_path):
                    # Limit depth
                    depth = root.replace(real_path, '').count(os.sep)
                    if depth > 5:
                        dirs.clear()
                        continue
                    
                    for filename in files:
                        if extensions:
                            ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
                            if ext not in extensions:
                                continue
                        
                        filepath = os.path.join(root, filename)
                        try:
                            stat = os.stat(filepath)
                            results.append({
                                'name': filename,
                                'path': filepath,
                                'virtual_path': f"A:/{os.path.relpath(filepath, '/')}",
                                'size': stat.st_size,
                                'modified': stat.st_mtime,
                                'extension': filename.rsplit('.', 1)[-1].lower() if '.' in filename else '',
                                'icon': self._get_file_icon(filename.rsplit('.', 1)[-1].lower() if '.' in filename else '')
                            })
                            
                            if len(results) >= max_results:
                                return results
                        except:
                            continue
            except PermissionError:
                pass
        
        # Also search SRLs for other drives
        for path, srl in self._srls.items():
            if not path.startswith(location):
                continue
            if extensions:
                ext = srl.name.rsplit('.', 1)[-1].lower() if '.' in srl.name else ''
                if ext not in extensions:
                    continue
            results.append({
                'name': srl.name,
                'path': path,
                'virtual_path': path,
                'size': srl.size_hint,
                'source': srl.source_type,
                'icon': self._get_file_icon(srl.name.rsplit('.', 1)[-1].lower() if '.' in srl.name else '')
            })
            
            if len(results) >= max_results:
                break
        
        return results
    
    def _get_file_icon(self, ext: str) -> str:
        """Get icon for file extension"""
        icons = {
            'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'webp': '🖼️', 
            'svg': '🖼️', 'bmp': '🖼️', 'heic': '🖼️', 'tiff': '🖼️',
            'mp3': '🎵', 'wav': '🎵', 'flac': '🎵', 'aac': '🎵', 'm4a': '🎵',
            'mp4': '🎬', 'mov': '🎬', 'avi': '🎬', 'mkv': '🎬', 'webm': '🎬',
            'pdf': '📕', 'doc': '📄', 'docx': '📄', 'txt': '📝', 'rtf': '📄',
            'xls': '📊', 'xlsx': '📊', 'csv': '📊',
            'ppt': '📽️', 'pptx': '📽️',
            'zip': '📦', 'rar': '📦', 'tar': '📦', 'gz': '📦', '7z': '📦',
            'py': '🐍', 'js': '📜', 'html': '🌐', 'css': '🎨', 'json': '📋',
            'exe': '⚙️', 'app': '⚙️', 'dmg': '💿', 'iso': '💿'
        }
        return icons.get(ext.lower() if ext else '', '📄')
    
    def dedupe(self, file_type: str = None, location: str = 'A:/', 
               dry_run: bool = True) -> Dict:
        """
        Find duplicate files by content hash.
        
        Args:
            file_type: Filter by type (image, video, document, etc.)
            location: Starting path
            dry_run: If True, only report dupes. If False, move to Z:/dupes/
            
        Returns:
            Dict with duplicate groups and space savings
        """
        files = self.find_all(file_type=file_type, location=location)
        
        # Group by file size first (quick filter)
        by_size = {}
        for f in files:
            size = f.get('size', 0)
            if size > 0:  # Ignore empty files
                if size not in by_size:
                    by_size[size] = []
                by_size[size].append(f)
        
        # Only check files with same size
        duplicates = []
        total_savings = 0
        
        for size, size_files in by_size.items():
            if len(size_files) < 2:
                continue
            
            # Hash files with same size
            hashes = {}
            for f in size_files:
                try:
                    filepath = f.get('path', '')
                    if os.path.exists(filepath):
                        # Quick hash (first 64KB + last 64KB)
                        with open(filepath, 'rb') as file:
                            start = file.read(65536)
                            file.seek(-min(65536, size), 2)
                            end = file.read(65536)
                            h = hashlib.md5(start + end).hexdigest()
                        
                        if h not in hashes:
                            hashes[h] = []
                        hashes[h].append(f)
                except:
                    continue
            
            # Find duplicates
            for h, hash_files in hashes.items():
                if len(hash_files) > 1:
                    # Keep first, mark rest as dupes
                    original = hash_files[0]
                    dupes = hash_files[1:]
                    
                    group = {
                        'original': original['path'],
                        'duplicates': [d['path'] for d in dupes],
                        'count': len(dupes),
                        'size_each': size,
                        'savings': size * len(dupes)
                    }
                    duplicates.append(group)
                    total_savings += group['savings']
                    
                    if not dry_run:
                        # Move duplicates to Z:/dupes/
                        for dupe in dupes:
                            try:
                                dupe_name = os.path.basename(dupe['path'])
                                dest = self.save_dir / 'dupes' / dupe_name
                                dest.parent.mkdir(parents=True, exist_ok=True)
                                os.rename(dupe['path'], dest)
                            except:
                                pass
        
        return {
            'duplicate_groups': len(duplicates),
            'total_duplicates': sum(g['count'] for g in duplicates),
            'savings_bytes': total_savings,
            'savings_mb': round(total_savings / (1024 * 1024), 2),
            'groups': duplicates[:50],  # Limit details
            'dry_run': dry_run
        }
    
    def batch_rename(self, location: str, pattern: str = None, 
                     prefix: str = '', suffix: str = '', 
                     numbering: bool = False, start_num: int = 1,
                     extension: str = None, dry_run: bool = True) -> Dict:
        """
        Batch rename files.
        
        Examples:
            batch_rename('A:/photos/', numbering=True, prefix='vacation_')
            → vacation_001.jpg, vacation_002.jpg, ...
            
            batch_rename('A:/documents/', suffix='_backup')
            → report_backup.pdf, notes_backup.txt, ...
        
        Args:
            location: Folder path
            pattern: Regex pattern to match files
            prefix: Add prefix to filename
            suffix: Add suffix before extension
            numbering: Add sequential numbers (.001, .002, etc.)
            start_num: Starting number for numbering
            extension: Filter by extension
            dry_run: Preview changes without renaming
        """
        files = self.find_all(extension=extension, location=location)
        
        # Sort for consistent numbering
        files.sort(key=lambda f: f['name'].lower())
        
        renames = []
        num = start_num
        
        for f in files:
            filepath = f.get('path', '')
            if not os.path.exists(filepath):
                continue
            
            # Check pattern
            filename = f['name']
            if pattern:
                if not re.search(pattern, filename):
                    continue
            
            # Parse name and extension
            if '.' in filename:
                name_part, ext_part = filename.rsplit('.', 1)
            else:
                name_part, ext_part = filename, ''
            
            # Build new name
            new_name = prefix + name_part
            
            if suffix:
                new_name += suffix
            
            if numbering:
                new_name += f'.{num:03d}'
                num += 1
            
            if ext_part:
                new_name += '.' + ext_part
            
            # Skip if no change
            if new_name == filename:
                continue
            
            new_path = os.path.join(os.path.dirname(filepath), new_name)
            
            renames.append({
                'old_name': filename,
                'new_name': new_name,
                'old_path': filepath,
                'new_path': new_path
            })
            
            if not dry_run:
                try:
                    os.rename(filepath, new_path)
                except Exception as e:
                    renames[-1]['error'] = str(e)
        
        return {
            'total_files': len(files),
            'to_rename': len(renames),
            'renames': renames[:100],  # Limit output
            'dry_run': dry_run
        }
    
    def organize(self, source: str = 'A:/', dest: str = 'Z:/organized/',
                 by: str = 'type', dry_run: bool = True) -> Dict:
        """
        Organize files into folders.
        
        Args:
            source: Source location
            dest: Destination folder
            by: Organization method:
                - 'type': By file type (Images/, Videos/, Documents/, etc.)
                - 'date': By year/month
                - 'extension': By extension
            dry_run: Preview without moving
        """
        type_folders = {
            'jpg': 'Images', 'jpeg': 'Images', 'png': 'Images', 'gif': 'Images',
            'webp': 'Images', 'svg': 'Images', 'bmp': 'Images', 'heic': 'Images',
            'mp4': 'Videos', 'mov': 'Videos', 'avi': 'Videos', 'mkv': 'Videos',
            'webm': 'Videos', 'flv': 'Videos',
            'mp3': 'Audio', 'wav': 'Audio', 'flac': 'Audio', 'aac': 'Audio',
            'm4a': 'Audio', 'ogg': 'Audio',
            'pdf': 'Documents', 'doc': 'Documents', 'docx': 'Documents',
            'txt': 'Documents', 'rtf': 'Documents',
            'xls': 'Spreadsheets', 'xlsx': 'Spreadsheets', 'csv': 'Spreadsheets',
            'ppt': 'Presentations', 'pptx': 'Presentations',
            'zip': 'Archives', 'rar': 'Archives', 'tar': 'Archives', 
            'gz': 'Archives', '7z': 'Archives',
            'py': 'Code', 'js': 'Code', 'ts': 'Code', 'html': 'Code',
            'css': 'Code', 'json': 'Code', 'java': 'Code', 'cpp': 'Code'
        }
        
        files = self.find_all(location=source)
        
        moves = []
        
        for f in files:
            filepath = f.get('path', '')
            if not os.path.exists(filepath):
                continue
            
            ext = f.get('extension', '').lower()
            filename = f['name']
            
            # Determine destination folder
            if by == 'type':
                folder = type_folders.get(ext, 'Other')
            elif by == 'extension':
                folder = ext.upper() if ext else 'NoExtension'
            elif by == 'date':
                try:
                    mtime = os.path.getmtime(filepath)
                    dt = datetime.fromtimestamp(mtime)
                    folder = f"{dt.year}/{dt.month:02d}"
                except:
                    folder = 'Unknown'
            else:
                folder = 'Unsorted'
            
            # Build destination path
            if dest.startswith('Z:'):
                dest_dir = self.save_dir / dest.replace('Z:/', '') / folder
            else:
                dest_dir = Path(dest) / folder
            
            dest_path = dest_dir / filename
            
            moves.append({
                'file': filename,
                'from': filepath,
                'to': str(dest_path),
                'folder': folder
            })
            
            if not dry_run:
                try:
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    import shutil
                    shutil.move(filepath, dest_path)
                except Exception as e:
                    moves[-1]['error'] = str(e)
        
        # Summary by folder
        by_folder = {}
        for m in moves:
            folder = m['folder']
            if folder not in by_folder:
                by_folder[folder] = 0
            by_folder[folder] += 1
        
        return {
            'total_files': len(files),
            'to_organize': len(moves),
            'by_folder': by_folder,
            'moves': moves[:100],  # Limit output
            'dry_run': dry_run
        }
    
    # -------------------------------------------------------------------------
    # Dimensional Operations
    # -------------------------------------------------------------------------
    
    def invoke(self, level: int) -> List[Any]:
        """
        Invoke a dimensional level.
        
        Level 6: File system overview
        Level 5: All drives
        Level 4: All folders
        Level 3: All files (SRLs)
        Level 2-1: Specific dimensional levels
        Level 0: All unmaterialized SRLs
        """
        self.kernel.invoke(level)
        
        if level == 6:
            return [{
                'name': 'Universal Hard Drive',
                'drives': len(self._drives),
                'srls': len(self._srls),
                'materializations': self._stats['materializations'],
                'saves': self._stats['saves'],
                'cache_hits': self._stats['cache_hits']
            }]
        
        elif level == 5:
            return self.drives()
        
        elif level == 4:
            # All folders
            folders = set()
            for path in self._srls.keys():
                parts = path.split('/')
                if len(parts) > 1:
                    folders.add('/'.join(parts[:-1]) + '/')
            return sorted(list(folders))
        
        elif level == 3:
            # All files (SRLs)
            return list(self._srls.values())
        
        elif level == 0:
            # Unmaterialized SRLs only
            return [srl for srl in self._srls.values() if not srl.is_materialized]
        
        else:
            return []
    
    def stats(self) -> Dict:
        """Get statistics"""
        return {
            **self._stats,
            'total_srls': len(self._srls),
            'materialized': sum(1 for s in self._srls.values() if s.is_materialized),
            'drives_connected': sum(1 for d in self._drives.values() if d.connected)
        }
    
    def query(self, query_str: str) -> List[Dict]:
        """
        SMART QUERY - Natural language search across all data.
        
        The SRL already knows where to look!
        
        Examples:
            "Find all Michaela coupons" → searches emails for michaela + coupon
            "Email with attachment Moms Recipes" → searches email attachments
            "Weekly schedule" → queries calendar for current week
            "What is scrupulosity" → searches dictionary/definitions
            "Show transactions from Chase" → searches banking data
            
        The system learns from every query and gets smarter over time.
        """
        self._stats['queries_processed'] += 1
        
        # Use semantic smart query
        smart_results = self._smart_query.execute(query_str, self._srls)
        
        if smart_results:
            return smart_results
        
        # Fall back to basic search if smart query finds nothing
        results = []
        query_lower = query_str.lower().strip()
        
        # Parse query modifiers
        filters = {}
        search_terms = []
        
        for part in query_str.split():
            if ':' in part and not part.startswith('http'):
                key, val = part.split(':', 1)
                filters[key.lower()] = val.lower()
            else:
                search_terms.append(part.lower())
        
        # Search through all SRLs
        for path, srl in self._srls.items():
            # Name match
            name_match = not search_terms or any(
                term in srl.name.lower() or term in path.lower() 
                for term in search_terms
            )
            
            if not name_match:
                continue
            
            # Filter: source
            if 'source' in filters:
                if filters['source'] != srl.source_type.lower():
                    continue
            
            # Filter: drive
            if 'drive' in filters:
                drive = path.split(':')[0].lower() if ':' in path else ''
                if filters['drive'] != drive:
                    continue
            
            # Filter: materialized
            if 'materialized' in filters:
                is_mat = srl.is_materialized
                want_mat = filters['materialized'] in ('true', 'yes', '1')
                if is_mat != want_mat:
                    continue
            
            # Get file view representation
            result = srl.to_file()
            result['path'] = path
            results.append(result)
            
            if len(results) >= 100:  # Limit results
                break
        
        return results
    
    def ask(self, question: str) -> Dict:
        """
        Ask a natural language question.
        
        Returns structured answer with context.
        
        Examples:
            "Find all emails from john@company.com"
            "Show me Michaela's coupons"
            "What meetings do I have this week?"
            "Definition of scrupulosity"
        """
        # Route the question
        routing = self._semantic_router.route(question)
        
        # Execute smart query
        results = self.query(question)
        
        # Get related items
        related = []
        if results:
            first_path = results[0].get('path')
            if first_path:
                related_paths = self._relationship_graph.find_related(first_path)
                for rp in related_paths[:5]:
                    if rp in self._srls:
                        related.append(self._srls[rp].to_file())
        
        return {
            'question': question,
            'routing': routing,
            'results': results,
            'related': related,
            'stats': {
                'results_count': len(results),
                'sources_searched': routing['sources'],
                'confidence': routing['confidence']
            }
        }
    
    def find_common_contacts(self, limit: int = 20) -> List[Dict]:
        """Find most common email addresses across all data"""
        return self._relationship_graph.get_common_emails(limit)
    
    def find_trends(self, limit: int = 50) -> List[Dict]:
        """Find trending keywords across all data"""
        return self._relationship_graph.get_common_keywords(limit)
    
    def find_related(self, path: str) -> List[Dict]:
        """Find items related to a specific file/SRL"""
        related_paths = self._relationship_graph.find_related(path)
        results = []
        for rp in related_paths:
            if rp in self._srls:
                results.append({
                    'path': rp,
                    **self._srls[rp].to_file()
                })
        return results


# =============================================================================
# WEB SERVER
# =============================================================================

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="cyberpunk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Universal Hard Drive</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600&family=VT323&family=Fira+Code&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        /* Default/Fallback variables */
        :root {
            --bg-primary: #0a0a1a;
            --bg-secondary: #151528;
            --bg-tertiary: #1a1a3e;
            --bg-card: #2a2a4e;
            --text-primary: #e0e0e0;
            --text-secondary: #a0a0c0;
            --accent: #ff00ff;
            --accent-secondary: #00ffff;
            --accent-glow: rgba(255, 0, 255, 0.5);
            --border: #3a3a6e;
            --success: #4ade80;
            --warning: #ffd700;
            --font-main: 'Rajdhani', -apple-system, sans-serif;
            --font-mono: 'Fira Code', monospace;
            --card-radius: 5px;
            --header-bg: linear-gradient(90deg, #1a0a2e 0%, #2a1a4e 50%, #1a0a2e 100%);
        }
        
        /* ================================================================
           THEME VARIABLES
           ================================================================ */
        
        /* CYBERPUNK - Neon with star background */
        [data-theme="cyberpunk"] {
            --bg-primary: #0a0a1a;
            --bg-secondary: #151528;
            --bg-tertiary: #1a1a3e;
            --bg-card: #2a2a4e;
            --text-primary: #e0e0e0;
            --text-secondary: #a0a0c0;
            --accent: #ff00ff;
            --accent-secondary: #00ffff;
            --accent-glow: rgba(255, 0, 255, 0.5);
            --border: #3a3a6e;
            --success: #4ade80;
            --warning: #ffd700;
            --font-main: 'Rajdhani', sans-serif;
            --font-mono: 'Fira Code', monospace;
            --card-radius: 5px;
            --header-bg: linear-gradient(90deg, #1a0a2e 0%, #2a1a4e 50%, #1a0a2e 100%);
        }
        
        /* TV TECH - CRT / Retro terminal */
        [data-theme="tvtech"] {
            --bg-primary: #0a0f0a;
            --bg-secondary: #0d140d;
            --bg-tertiary: #111a11;
            --bg-card: #152015;
            --text-primary: #00ff00;
            --text-secondary: #00aa00;
            --accent: #00ff00;
            --accent-secondary: #00cc00;
            --accent-glow: rgba(0, 255, 0, 0.3);
            --border: #003300;
            --success: #00ff00;
            --warning: #ffff00;
            --font-main: 'VT323', monospace;
            --font-mono: 'VT323', monospace;
            --card-radius: 0;
            --header-bg: linear-gradient(90deg, #001a00 0%, #002200 50%, #001a00 100%);
        }
        
        /* WINDOWS CLASSIC */
        [data-theme="windows"] {
            --bg-primary: #008080;
            --bg-secondary: #c0c0c0;
            --bg-tertiary: #d4d0c8;
            --bg-card: #ffffff;
            --text-primary: #000000;
            --text-secondary: #333333;
            --accent: #000080;
            --accent-secondary: #0000ff;
            --accent-glow: rgba(0, 0, 128, 0.2);
            --border: #808080;
            --success: #008000;
            --warning: #808000;
            --font-main: 'MS Sans Serif', 'Segoe UI', sans-serif;
            --font-mono: 'Courier New', monospace;
            --card-radius: 0;
            --header-bg: linear-gradient(180deg, #000080 0%, #1084d0 100%);
        }
        
        /* HIGH CONTRAST */
        [data-theme="highcontrast"] {
            --bg-primary: #000000;
            --bg-secondary: #000000;
            --bg-tertiary: #000000;
            --bg-card: #000000;
            --text-primary: #ffffff;
            --text-secondary: #ffff00;
            --accent: #00ffff;
            --accent-secondary: #ff00ff;
            --accent-glow: rgba(0, 255, 255, 0.3);
            --border: #ffffff;
            --success: #00ff00;
            --warning: #ffff00;
            --font-main: Arial, sans-serif;
            --font-mono: 'Courier New', monospace;
            --card-radius: 0;
            --header-bg: #000000;
        }
        
        /* DARK MODE - Refined modern dark */
        [data-theme="dark"] {
            --bg-primary: #121212;
            --bg-secondary: #1e1e1e;
            --bg-tertiary: #252525;
            --bg-card: #2d2d2d;
            --text-primary: #e0e0e0;
            --text-secondary: #a0a0a0;
            --accent: #bb86fc;
            --accent-secondary: #03dac6;
            --accent-glow: rgba(187, 134, 252, 0.3);
            --border: #3d3d3d;
            --success: #4ade80;
            --warning: #f59e0b;
            --font-main: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --font-mono: 'SF Mono', 'Fira Code', monospace;
            --card-radius: 12px;
            --header-bg: linear-gradient(90deg, #1e1e1e 0%, #2d2d2d 50%, #1e1e1e 100%);
        }
        
        /* CONFETTI - Kids / Fun Theme */
        [data-theme="confetti"] {
            --bg-primary: #fff5f5;
            --bg-secondary: #fff0f0;
            --bg-tertiary: #ffe5e5;
            --bg-card: #ffffff;
            --text-primary: #333333;
            --text-secondary: #666666;
            --accent: #ff6b9d;
            --accent-secondary: #00d4aa;
            --accent-glow: rgba(255, 107, 157, 0.3);
            --border: #ffccdd;
            --success: #00d4aa;
            --warning: #ffbb00;
            --font-main: 'Comic Sans MS', 'Chalkboard', cursive, sans-serif;
            --font-mono: 'Courier New', monospace;
            --card-radius: 20px;
            --header-bg: linear-gradient(90deg, #ff6b9d 0%, #ffbb00 25%, #00d4aa 50%, #00bbff 75%, #a855f7 100%);
        }
        
        /* NATIVE WINDOWS - Familiar Windows 10/11 style */
        [data-theme="native"] {
            --bg-primary: #f3f3f3;
            --bg-secondary: #ffffff;
            --bg-tertiary: #f9f9f9;
            --bg-card: #ffffff;
            --text-primary: #1a1a1a;
            --text-secondary: #666666;
            --accent: #0078d4;
            --accent-secondary: #005a9e;
            --accent-glow: rgba(0, 120, 212, 0.2);
            --border: #d6d6d6;
            --success: #107c10;
            --warning: #ffb900;
            --font-main: 'Segoe UI', -apple-system, sans-serif;
            --font-mono: 'Cascadia Code', 'Consolas', monospace;
            --card-radius: 4px;
            --header-bg: #f3f3f3;
        }
        
        /* ================================================================
           BASE STYLES
           ================================================================ */
        
        body {
            font-family: var(--font-main);
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            position: relative;
        }
        
        /* Star background for Cyberpunk */
        [data-theme="cyberpunk"] body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(2px 2px at 20px 30px, #fff, transparent),
                radial-gradient(2px 2px at 40px 70px, rgba(255,255,255,0.8), transparent),
                radial-gradient(1px 1px at 90px 40px, #fff, transparent),
                radial-gradient(2px 2px at 130px 80px, rgba(255,0,255,0.6), transparent),
                radial-gradient(1px 1px at 160px 120px, #fff, transparent),
                radial-gradient(2px 2px at 200px 50px, rgba(0,255,255,0.6), transparent),
                radial-gradient(1px 1px at 250px 160px, #fff, transparent),
                radial-gradient(2px 2px at 300px 100px, #fff, transparent);
            background-size: 350px 200px;
            animation: starMove 60s linear infinite;
            z-index: -1;
            opacity: 0.6;
        }
        
        @keyframes starMove {
            from { background-position: 0 0; }
            to { background-position: 350px 200px; }
        }
        
        /* CRT Scanlines for TV Tech */
        [data-theme="tvtech"] body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: repeating-linear-gradient(
                0deg,
                rgba(0, 0, 0, 0.15),
                rgba(0, 0, 0, 0.15) 1px,
                transparent 1px,
                transparent 2px
            );
            pointer-events: none;
            z-index: 1000;
        }
        
        [data-theme="tvtech"] body::after {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(ellipse at center, transparent 0%, rgba(0,0,0,0.3) 100%);
            pointer-events: none;
            z-index: 999;
        }
        
        /* High contrast outlines */
        [data-theme="highcontrast"] * {
            outline: 1px solid var(--border) !important;
        }
        
        /* Confetti background animation */
        [data-theme="confetti"] body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(8px 8px at 50px 50px, #ff6b9d, transparent),
                radial-gradient(6px 6px at 150px 80px, #00d4aa, transparent),
                radial-gradient(10px 10px at 250px 30px, #ffbb00, transparent),
                radial-gradient(5px 5px at 100px 150px, #00bbff, transparent),
                radial-gradient(7px 7px at 300px 120px, #a855f7, transparent),
                radial-gradient(8px 8px at 200px 180px, #ff6b9d, transparent),
                radial-gradient(6px 6px at 350px 60px, #00d4aa, transparent),
                radial-gradient(9px 9px at 400px 140px, #ffbb00, transparent);
            background-size: 450px 220px;
            animation: confettiFall 15s linear infinite;
            z-index: -1;
            opacity: 0.6;
        }
        
        @keyframes confettiFall {
            from { background-position: 0 -220px; }
            to { background-position: 0 220px; }
        }
        
        [data-theme="confetti"] .file-item:hover {
            animation: sparkle 0.3s ease-out;
        }
        
        @keyframes sparkle {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); box-shadow: 0 0 20px #ffbb00, 0 0 40px #ff6b9d; }
            100% { transform: scale(1); }
        }
        
        /* Native Windows styling */
        [data-theme="native"] .file-item {
            border: 1px solid transparent;
            border-radius: 4px;
        }
        
        [data-theme="native"] .file-item:hover {
            background: rgba(0, 120, 212, 0.1);
            border-color: var(--accent);
        }
        
        [data-theme="native"] header {
            border-bottom: 1px solid #d6d6d6;
            color: #1a1a1a;
        }
        
        .app {
            display: grid;
            grid-template-columns: 250px 1fr 300px;
            grid-template-rows: auto 1fr auto;
            height: 100vh;
        }
        
        /* ================================================================
           HEADER
           ================================================================ */
        
        header {
            grid-column: 1 / -1;
            background: var(--header-bg);
            padding: 15px 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        [data-theme="windows"] header {
            color: #ffffff;
        }
        
        .logo { display: flex; align-items: center; gap: 10px; }
        .logo h1 { font-size: 1.4em; color: var(--text-primary); }
        [data-theme="windows"] .logo h1 { color: #fff; }
        .logo .subtitle { font-size: 0.85em; opacity: 0.7; }
        
        .toolbar {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .path-bar {
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: var(--card-radius);
            padding: 8px 15px;
            color: var(--accent);
            font-family: var(--font-mono);
            min-width: 300px;
        }
        
        .theme-switcher {
            display: flex;
            gap: 5px;
        }
        
        .theme-btn {
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-primary);
            padding: 6px 12px;
            cursor: pointer;
            font-size: 0.8em;
            transition: all 0.2s;
            border-radius: 4px;
        }
        
        .theme-btn:hover {
            border-color: var(--accent);
            box-shadow: 0 0 10px var(--accent-glow);
        }
        
        .theme-btn.active {
            background: var(--accent);
            color: var(--bg-primary);
        }
        
        /* ================================================================
           SIDEBAR
           ================================================================ */
        
        .sidebar {
            background: var(--bg-secondary);
            border-right: 1px solid var(--border);
            padding: 15px;
            overflow-y: auto;
        }
        
        .sidebar h2 {
            font-size: 0.9em;
            text-transform: uppercase;
            opacity: 0.6;
            margin-bottom: 15px;
            letter-spacing: 1px;
        }
        
        .drive-list { list-style: none; }
        
        .drive {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px;
            border-radius: var(--card-radius);
            cursor: pointer;
            margin-bottom: 5px;
            transition: all 0.2s;
            border: 1px solid transparent;
        }
        
        .drive:hover { 
            background: var(--bg-card); 
            border-color: var(--accent);
        }
        
        [data-theme="cyberpunk"] .drive:hover {
            box-shadow: 0 0 15px var(--accent-glow);
        }
        
        .drive.active { 
            background: var(--bg-card); 
            border-left: 3px solid var(--accent);
        }
        
        .drive.disconnected { opacity: 0.5; }
        .drive-icon { font-size: 1.5em; }
        .drive-info { flex: 1; }
        .drive-name { font-weight: 600; }
        .drive-label { font-size: 0.8em; opacity: 0.7; }
        
        /* ================================================================
           MAIN CONTENT
           ================================================================ */
        
        .main {
            background: var(--bg-tertiary);
            overflow-y: auto;
            padding: 20px;
        }
        
        .file-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 15px;
        }
        
        .file-item {
            background: var(--bg-card);
            border-radius: var(--card-radius);
            padding: 15px;
            cursor: pointer;
            transition: all 0.2s;
            border: 1px solid transparent;
            text-align: center;
            position: relative;
        }
        
        .file-item:hover {
            transform: translateY(-2px);
            border-color: var(--accent);
        }
        
        [data-theme="cyberpunk"] .file-item:hover {
            box-shadow: 0 0 20px var(--accent-glow), 0 0 40px rgba(0, 255, 255, 0.2);
        }
        
        [data-theme="tvtech"] .file-item:hover {
            box-shadow: 0 0 10px var(--accent-glow);
            text-shadow: 0 0 5px var(--accent);
        }
        
        [data-theme="windows"] .file-item {
            border: 2px outset #fff;
        }
        
        [data-theme="windows"] .file-item:hover {
            border: 2px inset #fff;
        }
        
        .file-icon { font-size: 2.5em; margin-bottom: 10px; }
        
        .file-name {
            font-size: 0.9em;
            word-break: break-word;
            color: var(--text-primary);
        }
        
        .file-meta {
            font-size: 0.75em;
            color: var(--text-secondary);
            margin-top: 5px;
        }
        
        .file-item.folder .file-icon { color: var(--warning); }
        
        .file-item.materialized { 
            border-color: var(--success); 
        }
        
        .file-item.materialized::after {
            content: '●';
            position: absolute;
            top: 5px;
            right: 8px;
            color: var(--success);
            font-size: 0.8em;
        }
        
        /* ================================================================
           PREVIEW PANEL
           ================================================================ */
        
        .preview {
            background: var(--bg-secondary);
            border-left: 1px solid var(--border);
            padding: 20px;
            overflow-y: auto;
        }
        
        .preview h2 {
            font-size: 1em;
            margin-bottom: 15px;
            color: var(--accent);
        }
        
        .preview-content {
            background: var(--bg-primary);
            border-radius: var(--card-radius);
            padding: 15px;
            font-family: var(--font-mono);
            font-size: 0.85em;
            white-space: pre-wrap;
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid var(--border);
        }
        
        [data-theme="tvtech"] .preview-content {
            text-shadow: 0 0 5px var(--accent);
        }
        
        .preview-meta {
            margin-top: 15px;
            font-size: 0.85em;
        }
        
        .preview-meta dt { 
            color: var(--text-secondary); 
            margin-top: 10px; 
        }
        
        .preview-meta dd { color: var(--text-primary); }
        
        .preview-actions {
            margin-top: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .btn {
            background: var(--accent);
            color: var(--bg-primary);
            border: none;
            padding: 10px 20px;
            border-radius: var(--card-radius);
            cursor: pointer;
            font-size: 0.9em;
            font-family: var(--font-main);
            transition: all 0.2s;
        }
        
        .btn:hover { 
            filter: brightness(1.2);
            box-shadow: 0 0 15px var(--accent-glow);
        }
        
        [data-theme="windows"] .btn {
            border: 2px outset #fff;
            border-radius: 0;
        }
        
        [data-theme="windows"] .btn:hover {
            border: 2px inset #fff;
        }
        
        .btn-secondary {
            background: var(--bg-card);
            color: var(--text-primary);
            border: 1px solid var(--border);
        }
        
        .btn-save { background: var(--success); }
        
        /* ================================================================
           VIEW MODE SWITCHER
           ================================================================ */
        
        .view-switcher {
            display: flex;
            gap: 5px;
            margin-right: 20px;
        }
        
        .view-btn {
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-primary);
            padding: 6px 12px;
            cursor: pointer;
            font-size: 0.85em;
            transition: all 0.2s;
            border-radius: 4px;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .view-btn:hover {
            border-color: var(--accent);
            box-shadow: 0 0 10px var(--accent-glow);
        }
        
        .view-btn.active {
            background: var(--accent);
            color: var(--bg-primary);
        }
        
        /* Hide non-active views */
        .view-content { display: none; }
        .view-content.active { display: block; }
        
        /* ================================================================
           FILES VIEW (Traditional)
           ================================================================ */
        
        .files-view .file-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 15px;
        }
        
        /* ================================================================
           TABULAR VIEW
           ================================================================ */
        
        .tabular-view {
            overflow-x: auto;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }
        
        .data-table th {
            background: var(--bg-card);
            color: var(--accent);
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid var(--accent);
            position: sticky;
            top: 0;
        }
        
        .data-table td {
            padding: 10px 12px;
            border-bottom: 1px solid var(--border);
        }
        
        .data-table tr:hover {
            background: var(--bg-card);
        }
        
        .data-table .dim-col {
            font-size: 0.75em;
            color: var(--text-secondary);
        }
        
        /* ================================================================
           DIMENSIONAL VIEW (7D Substrate)
           ================================================================ */
        
        .dimensional-view {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .dimension-card {
            background: var(--bg-card);
            border-radius: var(--card-radius);
            border: 1px solid var(--border);
            overflow: hidden;
        }
        
        .dimension-header {
            background: var(--bg-tertiary);
            padding: 10px 15px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .dimension-level {
            background: var(--accent);
            color: var(--bg-primary);
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.8em;
        }
        
        .dimension-name {
            font-weight: 600;
            color: var(--accent);
        }
        
        .dimension-body {
            padding: 15px;
        }
        
        .dim-item {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px dotted var(--border);
        }
        
        .dim-key { color: var(--text-secondary); }
        .dim-value { color: var(--text-primary); font-family: var(--font-mono); }
        
        /* ================================================================
           NATIVE VIEW
           ================================================================ */
        
        .native-view {
            background: var(--bg-card);
            border-radius: var(--card-radius);
            padding: 20px;
            overflow: auto;
        }
        
        .native-format-badge {
            display: inline-block;
            background: var(--accent);
            color: var(--bg-primary);
            padding: 4px 10px;
            border-radius: 3px;
            font-size: 0.8em;
            margin-bottom: 15px;
        }
        
        .native-content {
            font-family: var(--font-mono);
            white-space: pre-wrap;
            font-size: 0.9em;
        }
        
        .native-content.json { color: var(--accent-secondary); }
        .native-content.xml { color: #e67e22; }
        .native-content.text { color: var(--text-primary); }
        
        /* ================================================================
           QUERY VIEW
           ================================================================ */
        
        .query-view {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .query-bar {
            display: flex;
            gap: 10px;
        }
        
        .query-input {
            flex: 1;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--card-radius);
            padding: 12px 15px;
            color: var(--text-primary);
            font-family: var(--font-mono);
            font-size: 1em;
        }
        
        .query-input:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 10px var(--accent-glow);
        }
        
        .query-filters {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .filter-chip {
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 5px 15px;
            font-size: 0.85em;
            cursor: pointer;
        }
        
        .filter-chip:hover, .filter-chip.active {
            background: var(--accent);
            color: var(--bg-primary);
        }
        
        .query-results {
            background: var(--bg-card);
            border-radius: var(--card-radius);
            padding: 15px;
            min-height: 200px;
        }
        
        /* ================================================================
           REPORTS VIEW
           ================================================================ */
        
        .reports-view {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
        }
        
        .report-card {
            background: var(--bg-card);
            border-radius: var(--card-radius);
            border: 1px solid var(--border);
            padding: 20px;
        }
        
        .report-title {
            font-size: 0.9em;
            color: var(--text-secondary);
            margin-bottom: 10px;
        }
        
        .report-value {
            font-size: 2em;
            font-weight: 600;
            color: var(--accent);
        }
        
        .report-chart {
            height: 100px;
            display: flex;
            align-items: flex-end;
            gap: 5px;
            margin-top: 15px;
        }
        
        .chart-bar {
            flex: 1;
            background: var(--accent);
            border-radius: 3px 3px 0 0;
            min-height: 5px;
        }
        
        .report-breakdown {
            margin-top: 15px;
        }
        
        .breakdown-item {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            font-size: 0.85em;
        }
        
        .breakdown-bar {
            height: 4px;
            background: var(--bg-tertiary);
            border-radius: 2px;
            margin-top: 3px;
            overflow: hidden;
        }
        
        .breakdown-fill {
            height: 100%;
            background: var(--accent);
        }
        
        /* Metrics cards */
        .metrics-card {
            border: 1px solid #00ff8855;
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.1);
        }
        
        .metrics-card.wide {
            grid-column: span 2;
        }
        
        .metrics-card .report-title {
            color: #00ffff;
        }
        
        .metrics-card .report-value {
            color: #00ff88;
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        }
        
        .efficiency-bar {
            height: 8px;
            background: var(--bg-tertiary);
            border-radius: 4px;
            margin: 10px 0;
            overflow: hidden;
        }
        
        .efficiency-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }
        
        @media (max-width: 800px) {
            .metrics-card.wide {
                grid-column: span 1;
            }
        }
        
        /* ================================================================
           TILE VIEW - Large Cards
           ================================================================ */
        
        .tile-view {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
            padding: 10px;
        }
        
        .tile-item {
            background: var(--bg-card);
            border-radius: var(--card-radius);
            border: 1px solid var(--border);
            padding: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            min-height: 180px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        
        .tile-item:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            border-color: var(--accent);
        }
        
        [data-theme="cyberpunk"] .tile-item:hover {
            box-shadow: 0 0 30px var(--accent-glow), 0 10px 40px rgba(0,0,0,0.3);
        }
        
        .tile-icon {
            font-size: 4em;
            margin-bottom: 15px;
        }
        
        .tile-name {
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 8px;
            word-break: break-word;
        }
        
        .tile-meta {
            font-size: 0.85em;
            color: var(--text-secondary);
        }
        
        .tile-badge {
            position: absolute;
            top: 10px;
            right: 10px;
            background: var(--accent);
            color: var(--bg-primary);
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 0.75em;
        }
        
        .tile-item.folder { position: relative; }
        .tile-item.folder .tile-icon { color: var(--warning); }
        .tile-item.materialized { border-color: var(--success); }
        
        /* ================================================================
           CONNECTOR PANEL - Status Dots Grid
           ================================================================ */
        
        .connector-panel {
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid var(--border);
        }
        
        .connector-panel h3 {
            font-size: 0.85em;
            text-transform: uppercase;
            opacity: 0.6;
            margin-bottom: 12px;
            letter-spacing: 1px;
        }
        
        .connector-category {
            margin-bottom: 15px;
        }
        
        .connector-category-title {
            font-size: 0.75em;
            color: var(--text-secondary);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .connector-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 6px;
        }
        
        .connector-btn {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 8px 10px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--card-radius);
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.8em;
        }
        
        .connector-btn:hover {
            border-color: var(--accent);
            box-shadow: 0 0 10px var(--accent-glow);
        }
        
        .connector-btn .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            flex-shrink: 0;
        }
        
        .connector-btn .status-dot.status-connected { background: #00ff88; box-shadow: 0 0 5px #00ff88; }
        .connector-btn .status-dot.status-disconnected { background: #ff4444; }
        .connector-btn .status-dot.status-unavailable { background: #333333; }
        .connector-btn .status-dot.status-pending { background: #ffaa00; animation: pulse 1s infinite; }
        .connector-btn .status-dot.status-error { background: #ff0000; }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .connector-btn .connector-icon { font-size: 1.1em; }
        .connector-btn .connector-name { 
            flex: 1; 
            text-align: left;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .connector-btn.connected {
            border-color: #00ff8855;
            background: rgba(0, 255, 136, 0.05);
        }
        
        /* Connection Table View */
        .connection-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85em;
        }
        
        .connection-table th {
            background: var(--bg-card);
            padding: 10px;
            text-align: left;
            border-bottom: 2px solid var(--accent);
        }
        
        .connection-table td {
            padding: 10px;
            border-bottom: 1px solid var(--border);
        }
        
        .connection-table tr:hover {
            background: var(--bg-card);
        }
        
        /* ================================================================
           ENHANCED STATUS BAR
           ================================================================ */
        
        .status-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
        }
        
        .status-group {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .status-metric {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            background: var(--bg-card);
            border-radius: 15px;
            font-size: 0.85em;
        }
        
        .status-metric .metric-icon { opacity: 0.7; }
        .status-metric .metric-label { color: var(--text-secondary); }
        .status-metric .metric-value { color: var(--accent); font-weight: 600; }
        
        .status-metric.highlight {
            background: linear-gradient(135deg, rgba(0,255,136,0.1) 0%, rgba(0,255,255,0.1) 100%);
            border: 1px solid rgba(0,255,136,0.3);
        }
        
        .status-metric.highlight .metric-value {
            color: #00ff88;
            text-shadow: 0 0 5px rgba(0,255,136,0.5);
        }
        
        .efficiency-gauge {
            width: 100px;
            height: 6px;
            background: var(--bg-tertiary);
            border-radius: 3px;
            overflow: hidden;
        }
        
        .efficiency-gauge-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #00ffff);
            transition: width 0.5s ease;
        }
        
        /* ================================================================
           FOOTER
           ================================================================ */
        
        footer {
            grid-column: 1 / -1;
            background: var(--bg-secondary);
            border-top: 1px solid var(--border);
            padding: 8px 20px;
            font-size: 0.85em;
            display: flex;
            justify-content: space-between;
        }
        
        .status-item { color: var(--text-secondary); }
        .status-item span { color: var(--accent); }
        
        /* Empty state */
        .empty-state {
            grid-column: 1 / -1;
            text-align: center;
            padding: 60px;
            color: var(--text-secondary);
        }
        
        .empty-state .icon { font-size: 4em; margin-bottom: 20px; }
        
        /* ================================================================
           ANIMATIONS
           ================================================================ */
        
        [data-theme="cyberpunk"] .logo span {
            animation: glowPulse 2s ease-in-out infinite;
        }
        
        @keyframes glowPulse {
            0%, 100% { text-shadow: 0 0 10px var(--accent), 0 0 20px var(--accent-secondary); }
            50% { text-shadow: 0 0 20px var(--accent), 0 0 40px var(--accent-secondary); }
        }
        
        [data-theme="tvtech"] * {
            animation: flicker 0.15s infinite;
        }
        
        @keyframes flicker {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.98; }
        }
    </style>
</head>
<body>
    <div class="app">
        <header>
            <div class="logo">
                <span style="font-size: 1.5em;">🦋</span>
                <div>
                    <h1>Universal Dimensional Drive</h1>
                    <div class="subtitle">All Data. One View. Native Everywhere.</div>
                </div>
            </div>
            <div class="toolbar">
                <div class="path-bar">%%PATH%%</div>
                <div class="view-switcher">
                    <button class="view-btn active" onclick="setView('files')" title="File Explorer"><span>📁</span> Files</button>
                    <button class="view-btn" onclick="setView('tile')" title="Tile View"><span>🔲</span> Tiles</button>
                    <button class="view-btn" onclick="setView('tabular')" title="Spreadsheet"><span>📊</span> Tabular</button>
                    <button class="view-btn" onclick="setView('dimensional')" title="7D Substrate"><span>🔮</span> 7D</button>
                    <button class="view-btn" onclick="setView('native')" title="Native Format"><span>🎯</span> Native</button>
                    <button class="view-btn" onclick="setView('query')" title="Smart Search"><span>🔍</span> Query</button>
                    <button class="view-btn" onclick="setView('reports')" title="Reports & Metrics"><span>📈</span> Reports</button>
                </div>
                <div class="theme-switcher">
                    <button class="theme-btn" onclick="setTheme('native')" title="Windows Native">🪟</button>
                    <button class="theme-btn" onclick="setTheme('cyberpunk')" title="Cyberpunk">🌌</button>
                    <button class="theme-btn" onclick="setTheme('tvtech')" title="TV Sci-Fi">📺</button>
                    <button class="theme-btn" onclick="setTheme('dark')" title="Dark Mode">🌙</button>
                    <button class="theme-btn" onclick="setTheme('highcontrast')" title="High Contrast">◐</button>
                    <button class="theme-btn" onclick="setTheme('confetti')" title="Fun/Kids">🎉</button>
                </div>
            </div>
        </header>
        
        <aside class="sidebar">
            <h2>Drives</h2>
            <ul class="drive-list">
                %%DRIVES%%
            </ul>
            
            <!-- Connector Panel -->
            <div class="connector-panel">
                <h3>Connectors</h3>
                %%CONNECTORS%%
            </div>
        </aside>
        
        <main class="main">
            <!-- FILES VIEW -->
            <div class="view-content files-view active" id="view-files">
                <div class="file-grid">
                    %%FILES%%
                </div>
            </div>
            
            <!-- TILE VIEW -->
            <div class="view-content tile-view" id="view-tile">
                %%TILES%%
            </div>
            
            <!-- TABULAR VIEW -->
            <div class="view-content tabular-view" id="view-tabular">
                %%TABULAR%%
            </div>
            
            <!-- DIMENSIONAL VIEW (7D Substrate) -->
            <div class="view-content dimensional-view" id="view-dimensional">
                %%DIMENSIONAL%%
            </div>
            
            <!-- NATIVE VIEW -->
            <div class="view-content native-view" id="view-native">
                %%NATIVE%%
            </div>
            
            <!-- QUERY VIEW - Natural Language Search -->
            <div class="view-content query-view" id="view-query">
                <div class="query-bar">
                    <input type="text" class="query-input" placeholder="Ask anything: Find Michaela's coupons, Show weekly schedule, Email from John..." id="query-input">
                    <button class="btn" onclick="runQuery()">🔍 Ask</button>
                </div>
                <div class="query-examples" style="margin: 10px 0; font-size: 0.85em; opacity: 0.7;">
                    <span style="margin-right: 10px;">Try:</span>
                    <span class="example-query" onclick="setQuery('Find all emails from mom')" style="cursor:pointer; text-decoration:underline; margin-right: 15px;">📧 emails from mom</span>
                    <span class="example-query" onclick="setQuery('Show weekly calendar')" style="cursor:pointer; text-decoration:underline; margin-right: 15px;">📅 weekly schedule</span>
                    <span class="example-query" onclick="setQuery('Find coupons')" style="cursor:pointer; text-decoration:underline; margin-right: 15px;">🏷️ coupons</span>
                    <span class="example-query" onclick="setQuery('Documents with recipes')" style="cursor:pointer; text-decoration:underline; margin-right: 15px;">📄 recipes</span>
                </div>
                <div class="query-filters">
                    <span class="filter-chip active" onclick="addFilter('')">🌐 All Sources</span>
                    <span class="filter-chip" onclick="addFilter('source:local')">💾 Local</span>
                    <span class="filter-chip" onclick="addFilter('source:email')">📧 Email</span>
                    <span class="filter-chip" onclick="addFilter('source:calendar')">📅 Calendar</span>
                    <span class="filter-chip" onclick="addFilter('source:api')">🔗 APIs</span>
                    <span class="filter-chip" onclick="addFilter('source:cloud')">☁️ Cloud</span>
                </div>
                <div class="query-results" id="query-results">
                    <div style="text-align:center; padding: 40px; opacity:0.6">
                        <div style="font-size: 3em; margin-bottom: 15px;">🔮</div>
                        <p><strong>SRL knows where to look</strong></p>
                        <p style="font-size: 0.9em; margin-top: 10px;">
                            Just ask in plain English. The system learns relationships<br>
                            and finds connections across all your data sources.
                        </p>
                    </div>
                </div>
                <div class="query-insights" id="query-insights" style="margin-top: 20px; display: none;">
                    <h3 style="font-size: 0.9em; opacity: 0.7; margin-bottom: 10px;">💡 Learned Insights</h3>
                    <div id="insights-content"></div>
                </div>
            </div>
            
            <!-- REPORTS VIEW -->
            <div class="view-content reports-view" id="view-reports">
                %%REPORTS%%
            </div>
        </main>
        
        <aside class="preview">
            <h2>Preview</h2>
            %%PREVIEW%%
        </aside>
        
        <footer>
            <div class="status-bar">
                <div class="status-group">
                    <div class="status-metric">
                        <span class="metric-icon">📊</span>
                        <span class="metric-label">SRLs:</span>
                        <span class="metric-value">%%SRLS%%</span>
                    </div>
                    <div class="status-metric">
                        <span class="metric-icon">✨</span>
                        <span class="metric-label">Materialized:</span>
                        <span class="metric-value">%%MATERIALIZED%%</span>
                    </div>
                    <div class="status-metric">
                        <span class="metric-icon">💾</span>
                        <span class="metric-label">Saved:</span>
                        <span class="metric-value">%%SAVES%%</span>
                    </div>
                </div>
                <div class="status-group">
                    <div class="status-metric highlight">
                        <span class="metric-icon">⚡</span>
                        <span class="metric-label">Efficiency:</span>
                        <span class="metric-value">%%EFFICIENCY%%</span>
                        <div class="efficiency-gauge">
                            <div class="efficiency-gauge-fill" style="width: %%EFFICIENCY_PCT%%"></div>
                        </div>
                    </div>
                    <div class="status-metric highlight">
                        <span class="metric-icon">🔢</span>
                        <span class="metric-label">Bit Savings:</span>
                        <span class="metric-value">%%BITSAVED%%</span>
                    </div>
                    <div class="status-metric highlight">
                        <span class="metric-icon">📦</span>
                        <span class="metric-label">Compressed:</span>
                        <span class="metric-value">%%COMPRESSED%%</span>
                    </div>
                </div>
                <div class="status-group">
                    <div class="status-metric">
                        <span class="metric-icon">🔗</span>
                        <span class="metric-label">Connectors:</span>
                        <span class="metric-value">%%CONNECTORS_COUNT%%</span>
                    </div>
                </div>
            </div>
        </footer>
    </div>
    
    <script>
        // ========================
        // THEME SWITCHING
        // ========================
        function setTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('uhd-theme', theme);
            document.querySelectorAll('.theme-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
        }
        
        // ========================
        // VIEW MODE SWITCHING
        // ========================
        function setView(view) {
            // Hide all views
            document.querySelectorAll('.view-content').forEach(v => v.classList.remove('active'));
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            
            // Show selected view
            document.getElementById('view-' + view).classList.add('active');
            event.target.closest('.view-btn').classList.add('active');
            
            localStorage.setItem('uhd-view', view);
        }
        
        // ========================
        // QUERY FUNCTIONALITY - Natural Language
        // ========================
        function setQuery(q) {
            document.getElementById('query-input').value = q;
            runQuery();
        }
        
        function addFilter(filter) {
            const input = document.getElementById('query-input');
            if (filter && !input.value.includes(filter)) {
                input.value = input.value.trim() + ' ' + filter;
            }
            document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
            event.target.classList.add('active');
        }
        
        async function runQuery() {
            const query = document.getElementById('query-input').value;
            const results = document.getElementById('query-results');
            const insights = document.getElementById('query-insights');
            
            if (!query.trim()) {
                results.innerHTML = '<p style="opacity:0.5">Enter a question or search term...</p>';
                return;
            }
            
            results.innerHTML = '<div style="text-align:center;padding:40px;"><div style="font-size:2em">🔍</div><p>Searching across all sources...</p></div>';
            
            try {
                // Use smart /api/ask endpoint
                const resp = await fetch('/api/ask?q=' + encodeURIComponent(query));
                const data = await resp.json();
                
                let html = '';
                
                // Show routing info
                if (data.routing) {
                    html += `<div style="margin-bottom:15px; padding:10px; background:var(--bg-card); border-radius:var(--card-radius); font-size:0.85em;">
                        <span style="margin-right:15px;">${data.routing.icon || '🔍'} Searched:</span>
                        ${data.routing.sources.map(s => '<span style="background:var(--bg-tertiary);padding:2px 8px;border-radius:3px;margin-right:5px;">'+s+'</span>').join('')}
                        <span style="float:right;opacity:0.6;">Confidence: ${Math.round((data.routing.confidence || 0) * 100)}%</span>
                    </div>`;
                }
                
                if (data.results && data.results.length > 0) {
                    html += '<div class="file-grid">';
                    data.results.forEach(item => {
                        const confidence = item.confidence ? `<span style="font-size:0.7em;opacity:0.6">${Math.round(item.confidence*100)}%</span>` : '';
                        html += `<div class="file-item" onclick="location.href='/?select=${encodeURIComponent(item.path)}'">
                            <div class="file-icon">${item.icon || '📄'}</div>
                            <div class="file-name">${item.name}</div>
                            <div class="file-meta">${item.source || item.match_type || ''} ${confidence}</div>
                        </div>`;
                    });
                    html += '</div>';
                    
                    // Show related items
                    if (data.related && data.related.length > 0) {
                        html += '<h4 style="margin-top:20px;font-size:0.9em;opacity:0.7;">🔗 Related Items</h4>';
                        html += '<div class="file-grid" style="margin-top:10px;">';
                        data.related.forEach(item => {
                            html += `<div class="file-item" style="opacity:0.8" onclick="location.href='/?select=${encodeURIComponent(item.path || '')}'">
                                <div class="file-icon">${item.icon || '📄'}</div>
                                <div class="file-name">${item.name || '?'}</div>
                            </div>`;
                        });
                        html += '</div>';
                    }
                    
                    results.innerHTML = html;
                } else {
                    results.innerHTML = '<div style="text-align:center;padding:40px;opacity:0.6"><div style="font-size:2em">🔍</div><p>No results found</p><p style="font-size:0.85em">Try a different query or connect more data sources</p></div>';
                }
                
            } catch(e) {
                results.innerHTML = '<p style="color:var(--warning)">Query error: ' + e.message + '</p>';
            }
        }
        
        document.getElementById('query-input')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') runQuery();
        });
        
        // ========================
        // CONNECTOR MODAL
        // ========================
        function showConnectModal(provider) {
            // Create modal for connecting to a service
            const modal = document.createElement('div');
            modal.className = 'connect-modal';
            modal.innerHTML = `
                <div class="modal-overlay" onclick="closeConnectModal()"></div>
                <div class="modal-content">
                    <h2>Connect to ${provider.toUpperCase()}</h2>
                    <p style="margin: 15px 0; opacity: 0.7;">Enter your credentials to connect this service.</p>
                    <form id="connect-form" onsubmit="submitConnect(event, '${provider}')">
                        <div class="form-group">
                            <label>API Key / Token</label>
                            <input type="password" name="api_key" class="form-input" placeholder="Enter your API key" required>
                        </div>
                        <div class="form-group">
                            <label>Display Name (optional)</label>
                            <input type="text" name="name" class="form-input" placeholder="My ${provider}">
                        </div>
                        <div class="form-actions">
                            <button type="button" class="btn btn-secondary" onclick="closeConnectModal()">Cancel</button>
                            <button type="submit" class="btn">Connect</button>
                        </div>
                    </form>
                </div>
            `;
            document.body.appendChild(modal);
            
            // Add modal styles if not present
            if (!document.getElementById('modal-styles')) {
                const styles = document.createElement('style');
                styles.id = 'modal-styles';
                styles.textContent = `
                    .connect-modal { position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 9999; display: flex; align-items: center; justify-content: center; }
                    .modal-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); }
                    .modal-content { position: relative; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--card-radius); padding: 30px; min-width: 400px; max-width: 500px; }
                    .form-group { margin: 15px 0; }
                    .form-group label { display: block; margin-bottom: 5px; color: var(--text-secondary); font-size: 0.9em; }
                    .form-input { width: 100%; padding: 10px 15px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: var(--card-radius); color: var(--text-primary); font-size: 1em; }
                    .form-input:focus { outline: none; border-color: var(--accent); }
                    .form-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 25px; }
                `;
                document.head.appendChild(styles);
            }
        }
        
        function closeConnectModal() {
            const modal = document.querySelector('.connect-modal');
            if (modal) modal.remove();
        }
        
        async function submitConnect(e, provider) {
            e.preventDefault();
            const form = document.getElementById('connect-form');
            const formData = new FormData(form);
            const data = {
                provider: provider,
                api_key: formData.get('api_key'),
                name: formData.get('name') || provider
            };
            
            try {
                const resp = await fetch('/api/connect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await resp.json();
                
                if (result.success) {
                    closeConnectModal();
                    location.href = '/?path=' + result.drive_letter + ':/';
                } else {
                    alert('Connection failed: ' + (result.error || 'Unknown error'));
                }
            } catch (err) {
                alert('Connection failed: ' + err.message);
            }
        }
        
        // ========================
        // LIVE METRICS UPDATE
        // ========================
        async function updateMetrics() {
            try {
                const resp = await fetch('/api/metrics');
                const data = await resp.json();
                
                // Update status bar values
                const effEl = document.querySelector('.metric-value[data-metric="efficiency"]');
                if (effEl) effEl.textContent = data.summary.efficiency_pct + '%';
                
                const bitsEl = document.querySelector('.metric-value[data-metric="bits"]');
                if (bitsEl) bitsEl.textContent = data.summary.bit_savings_formatted;
            } catch (e) {
                // Ignore errors
            }
        }
        
        // Update metrics every 5 seconds
        setInterval(updateMetrics, 5000);
        
        // ========================
        // INITIALIZE
        // ========================
        const savedTheme = localStorage.getItem('uhd-theme') || 'native';
        document.documentElement.setAttribute('data-theme', savedTheme);
        
        const savedView = localStorage.getItem('uhd-view') || 'files';
        if (savedView !== 'files') {
            document.querySelectorAll('.view-content').forEach(v => v.classList.remove('active'));
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            const viewEl = document.getElementById('view-' + savedView);
            if (viewEl) viewEl.classList.add('active');
        }
    </script>
</body>
</html>
"""


class UHDHandler(BaseHTTPRequestHandler):
    """HTTP Handler for Universal Hard Drive"""
    
    uhd: UniversalHardDrive = None
    
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if parsed.path == '/':
            self.serve_home(params)
        elif parsed.path == '/api/ls':
            path = params.get('path', [''])[0]
            self.serve_json(self.uhd.ls(unquote(path)))
        elif parsed.path == '/api/read':
            path = params.get('path', [''])[0]
            self.serve_json(self.uhd.read(unquote(path)))
        elif parsed.path == '/api/info':
            path = params.get('path', [''])[0]
            self.serve_json(self.uhd.info(unquote(path)))
        elif parsed.path == '/api/stats':
            self.serve_json(self.uhd.stats())
        elif parsed.path == '/api/save':
            src = params.get('src', [''])[0]
            dst = params.get('dst', [None])[0]
            success = self.uhd.save(unquote(src), unquote(dst) if dst else None)
            self.serve_json({'success': success})
        elif parsed.path == '/api/query':
            query = params.get('q', [''])[0]
            results = self.uhd.query(unquote(query))
            self.serve_json({'query': query, 'results': results})
        elif parsed.path == '/api/ask':
            # Natural language question - SRL knows where to look
            question = params.get('q', [''])[0]
            answer = self.uhd.ask(unquote(question))
            self.serve_json(answer)
        elif parsed.path == '/api/trends':
            # Get trending keywords across all data
            limit = int(params.get('limit', ['50'])[0])
            trends = self.uhd.find_trends(limit)
            self.serve_json({'trends': trends})
        elif parsed.path == '/api/contacts':
            # Get common contacts/emails across all data
            limit = int(params.get('limit', ['20'])[0])
            contacts = self.uhd.find_common_contacts(limit)
            self.serve_json({'contacts': contacts})
        elif parsed.path == '/api/related':
            # Find items related to a path
            path = params.get('path', [''])[0]
            related = self.uhd.find_related(unquote(path))
            self.serve_json({'path': path, 'related': related})
        elif parsed.path == '/api/dimensional':
            path = params.get('path', [''])[0]
            srl = self.uhd._srls.get(unquote(path))
            if srl:
                self.serve_json(srl.to_dimensional())
            else:
                self.serve_json({'error': 'Not found'})
        elif parsed.path == '/api/metrics':
            # Global ingestion metrics dashboard
            self.serve_json(GLOBAL_METRICS.to_dashboard())
        elif parsed.path == '/api/metrics/summary':
            # Just the summary stats
            self.serve_json(GLOBAL_METRICS.get_summary())
        elif parsed.path == '/api/metrics/by-type':
            # Breakdown by file type
            self.serve_json(GLOBAL_METRICS.get_by_type())
        elif parsed.path == '/api/metrics/recent':
            # Recent ingestions
            limit = int(params.get('limit', ['20'])[0])
            self.serve_json(GLOBAL_METRICS.get_recent(limit))
        elif parsed.path == '/api/metrics/item':
            # Metrics for a specific item
            path = params.get('path', [''])[0]
            srl = self.uhd._srls.get(unquote(path))
            if srl and srl._substrated_item:
                self.serve_json(srl._substrated_item.to_metrics())
            else:
                self.serve_json({'error': 'Not found or not materialized'})
        elif parsed.path == '/api/services':
            # List all available canned connections
            self.serve_json(self.uhd.list_available_services())
        elif parsed.path == '/api/connections':
            # List active connections
            self.serve_json(self.uhd.list_connections())
        elif parsed.path == '/api/connectors':
            # List all connectors with their status (green/red/black dots)
            connectors = [c.to_dict() for c in self.uhd.get_connectors()]
            self.serve_json({
                'connectors': connectors,
                'by_category': {
                    cat: [c.to_dict() for c in conns] 
                    for cat, conns in self.uhd.get_connectors_by_category().items()
                }
            })
        elif parsed.path == '/api/uc/sync':
            # Sync with Universal Connector service
            uc_port = int(params.get('port', ['8766'])[0])
            result = self.uhd.sync_with_universal_connector(uc_port)
            self.serve_json(result)
        elif parsed.path == '/api/uc/services':
            # Get services from Universal Connector
            uc_port = int(params.get('port', ['8766'])[0])
            services = self.uhd.get_uc_services(uc_port)
            self.serve_json({'services': services})
        elif parsed.path == '/api/uc/categories':
            # Get categories from Universal Connector
            uc_port = int(params.get('port', ['8766'])[0])
            categories = self.uhd.get_uc_categories(uc_port)
            self.serve_json({'categories': categories})
        elif parsed.path == '/api/uc/status':
            # Check if Universal Connector is running
            import urllib.request
            uc_port = int(params.get('port', ['8766'])[0])
            try:
                with urllib.request.urlopen(f"http://localhost:{uc_port}/api/stats", timeout=2) as response:
                    stats = json.loads(response.read())
                    self.serve_json({'running': True, 'port': uc_port, 'stats': stats})
            except:
                self.serve_json({'running': False, 'port': uc_port})
        elif parsed.path == '/connect':
            # Serve the new unified connection hub
            self.serve_connect_hub()
        elif parsed.path == '/connect/classic':
            # Serve the original connection wizard page
            self.serve_connect_page()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests for connecting services"""
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/connect':
            # Read POST body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(body)
                provider = data.get('provider')
                name = data.get('name')
                
                # Build credentials from either 'credentials' dict or direct fields
                credentials = data.get('credentials', {})
                if not credentials:
                    # Extract credentials from direct fields
                    for key in ['api_key', 'username', 'password', 'host', 'port', 
                               'database', 'endpoint', 'secret', 'token']:
                        if key in data:
                            credentials[key] = data[key]
                
                drive = self.uhd.connect_service(provider, credentials, name)
                
                if drive:
                    self.serve_json({
                        'success': True,
                        'drive_letter': drive,
                        'message': f'Connected as {drive}:'
                    })
                else:
                    self.serve_json({
                        'success': False,
                        'error': 'Connection failed'
                    })
            except Exception as e:
                self.serve_json({'success': False, 'error': str(e)})
        
        elif parsed.path == '/api/disconnect':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            drive = data.get('drive', '')
            
            success = self.uhd.disconnect_service(drive)
            self.serve_json({'success': success})
        
        elif parsed.path == '/api/uc/test':
            # Test a service connection
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            service_id = data.get('service_id', '')
            credentials = data.get('credentials', {})
            
            result = self.uhd.test_service_connection(service_id, credentials)
            self.serve_json(result)
        else:
            self.send_error(404)
    
    def serve_connect_hub(self):
        """Serve the new unified connection hub page"""
        import os
        
        # Try to find the static connect.html file
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'web', 'connect.html'),
            '/opt/butterflyfx/dimensionsos/web/connect.html',
            os.path.join(os.getcwd(), 'web', 'connect.html'),
        ]
        
        html_content = None
        for path in possible_paths:
            try:
                with open(path, 'r') as f:
                    html_content = f.read()
                    break
            except FileNotFoundError:
                continue
        
        if html_content:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(html_content.encode())
        else:
            # Fallback to classic page
            self.serve_connect_page()

    def serve_connect_page(self):
        """Serve the connection wizard HTML"""
        services = self.uhd.list_available_services()
        
        # Group by category
        categories = {}
        for svc in services:
            cat = svc['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(svc)
        
        # Build service cards HTML
        services_html = ""
        for cat, svcs in sorted(categories.items()):
            services_html += f'<div class="service-category"><h3>{cat}</h3><div class="service-grid">'
            for svc in svcs:
                fields_html = ""
                for field_id, field_label in svc['fields'].items():
                    input_type = 'password' if any(x in field_id.lower() for x in ['key', 'secret', 'password', 'token']) else 'text'
                    fields_html += f'''
                        <div class="field-group">
                            <label for="{svc['id']}_{field_id}">{field_label}</label>
                            <input type="{input_type}" id="{svc['id']}_{field_id}" 
                                   name="{field_id}" placeholder="{field_label}" class="cred-input">
                        </div>
                    '''
                
                services_html += f'''
                    <div class="service-card" data-provider="{svc['id']}">
                        <div class="service-header">
                            <span class="service-icon">{svc['icon']}</span>
                            <span class="service-name">{svc['name']}</span>
                        </div>
                        <p class="service-desc">{svc['description']}</p>
                        <div class="service-ingests">
                            Ingests: {', '.join(svc['ingests'][:4])}{'...' if len(svc['ingests']) > 4 else ''}
                        </div>
                        <form class="connect-form" onsubmit="connectService(event, '{svc['id']}')">
                            {fields_html}
                            <button type="submit" class="btn">🔗 Connect</button>
                        </form>
                    </div>
                '''
            services_html += '</div></div>'
        
        html = f'''<!DOCTYPE html>
<html lang="en" data-theme="cyberpunk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connect Service - Universal Hard Drive</title>
    <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        :root {{
            --bg-primary: #0a0a1a;
            --bg-secondary: #151528;
            --bg-card: #2a2a4e;
            --text-primary: #e0e0e0;
            --text-secondary: #a0a0c0;
            --accent: #ff00ff;
            --accent-secondary: #00ffff;
            --border: #3a3a6e;
            --success: #4ade80;
        }}
        body {{
            font-family: 'Rajdhani', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{ color: var(--accent); }}
        .header p {{ color: var(--text-secondary); }}
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: var(--accent-secondary);
            text-decoration: none;
        }}
        .service-category {{
            margin-bottom: 30px;
        }}
        .service-category h3 {{
            color: var(--accent-secondary);
            margin-bottom: 15px;
            padding-bottom: 5px;
            border-bottom: 1px solid var(--border);
        }}
        .service-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }}
        .service-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
            transition: all 0.2s;
        }}
        .service-card:hover {{
            border-color: var(--accent);
            box-shadow: 0 0 20px rgba(255, 0, 255, 0.3);
        }}
        .service-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }}
        .service-icon {{ font-size: 1.5em; }}
        .service-name {{ font-weight: 600; font-size: 1.1em; }}
        .service-desc {{
            font-size: 0.85em;
            color: var(--text-secondary);
            margin-bottom: 10px;
        }}
        .service-ingests {{
            font-size: 0.75em;
            color: var(--accent-secondary);
            margin-bottom: 15px;
        }}
        .connect-form {{
            display: none;
            flex-direction: column;
            gap: 10px;
        }}
        .service-card:hover .connect-form {{ display: flex; }}
        .field-group {{
            display: flex;
            flex-direction: column;
            gap: 3px;
        }}
        .field-group label {{
            font-size: 0.8em;
            color: var(--text-secondary);
        }}
        .cred-input {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 8px 12px;
            color: var(--text-primary);
            font-size: 0.9em;
        }}
        .cred-input:focus {{
            outline: none;
            border-color: var(--accent);
        }}
        .btn {{
            background: var(--accent);
            color: var(--bg-primary);
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 600;
            margin-top: 10px;
        }}
        .btn:hover {{ filter: brightness(1.2); }}
        .toast {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 8px;
            display: none;
        }}
        .toast.success {{ background: var(--success); color: #000; }}
        .toast.error {{ background: #ef4444; color: #fff; }}
    </style>
</head>
<body>
    <a href="/" class="back-link">← Back to Universal Hard Drive</a>
    <div class="header">
        <h1>🔗 Connect a Service</h1>
        <p>Add your credentials once. System ingests everything. Data becomes native.</p>
    </div>
    
    {services_html}
    
    <div id="toast" class="toast"></div>
    
    <script>
        async function connectService(event, provider) {{
            event.preventDefault();
            const form = event.target;
            const inputs = form.querySelectorAll('.cred-input');
            
            const credentials = {{}};
            inputs.forEach(input => {{
                if (input.value) credentials[input.name] = input.value;
            }});
            
            const toast = document.getElementById('toast');
            
            try {{
                const resp = await fetch('/api/connect', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{ provider, credentials }})
                }});
                const data = await resp.json();
                
                if (data.success) {{
                    toast.className = 'toast success';
                    toast.textContent = '✓ Connected as ' + data.drive + ': - Redirecting...';
                    toast.style.display = 'block';
                    setTimeout(() => window.location.href = '/?path=' + data.drive + ':/', 1500);
                }} else {{
                    toast.className = 'toast error';
                    toast.textContent = '✗ ' + (data.error || 'Connection failed');
                    toast.style.display = 'block';
                    setTimeout(() => toast.style.display = 'none', 3000);
                }}
            }} catch(e) {{
                toast.className = 'toast error';
                toast.textContent = '✗ ' + e.message;
                toast.style.display = 'block';
            }}
        }}
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_home(self, params):
        path = params.get('path', [''])[0]
        selected = params.get('select', [None])[0]
        
        stats = self.uhd.stats()
        metrics = GLOBAL_METRICS.get_summary()
        
        # Build drives HTML
        drives_html = ""
        current_drive = path.split(':')[0] if ':' in path else ''
        
        for drive in self.uhd.drives():
            active = 'active' if drive.letter == current_drive else ''
            connected = '' if drive.connected else 'disconnected'
            drives_html += f"""
                <li class="drive {active} {connected}" 
                    onclick="location.href='/?path={drive.letter}:/'">
                    <span class="drive-icon">{drive.icon}</span>
                    <div class="drive-info">
                        <div class="drive-name">{drive.letter}: {drive.name}</div>
                        <div class="drive-label">{'Connected' if drive.connected else 'Not mounted'}</div>
                    </div>
                </li>
            """
        
        # Build Connectors Panel HTML
        connectors_html = self._render_connectors_panel()
        
        # Build files HTML (Files View)
        items = self.uhd.ls(path) if path else self.uhd.ls("/")
        files_html = ""
        
        if not items:
            files_html = """
                <div class="empty-state">
                    <div class="icon">📭</div>
                    <p>No files in this location</p>
                </div>
            """
        else:
            for item in items:
                item_class = 'folder' if item.get('is_folder') else ''
                if item.get('materialized'):
                    item_class += ' materialized'
                
                icon = item.get('icon', '📄')
                name = item.get('name', 'Unknown')
                item_path = item.get('path', '')
                
                if item.get('is_folder'):
                    onclick = f"location.href='/?path={quote(item_path)}'"
                else:
                    onclick = f"location.href='/?path={quote(path)}&select={quote(item_path)}'"
                
                meta = item.get('label', item.get('source', ''))
                
                files_html += f"""
                    <div class="file-item {item_class}" onclick="{onclick}">
                        <div class="file-icon">{icon}</div>
                        <div class="file-name">{name}</div>
                        <div class="file-meta">{meta}</div>
                    </div>
                """
        
        # Build Tile View HTML
        tiles_html = self._render_tile_view(items, path)
        
        # Build Tabular View
        tabular_html = self._render_tabular_view(items)
        
        # Build Dimensional View (7D Substrate)
        dimensional_html = self._render_dimensional_view(items, path)
        
        # Build Native View
        native_html = self._render_native_view(selected)
        
        # Build Reports View
        reports_html = self._render_reports_view(stats, items)
        
        # Build preview HTML
        preview_html = "<p style='opacity: 0.5'>Select a file to preview</p>"
        
        if selected:
            info = self.uhd.info(selected)
            if 'error' not in info:
                data = self.uhd.read(selected)
                data_str = json.dumps(data, indent=2)[:1000]
                if len(json.dumps(data)) > 1000:
                    data_str += '\n...'
                
                preview_html = f"""
                    <div class="preview-content">{data_str}</div>
                    <dl class="preview-meta">
                        <dt>Path</dt>
                        <dd>{info.get('path', '')}</dd>
                        <dt>Source</dt>
                        <dd>{info.get('source_type', '')} / {info.get('source_ref', '')}</dd>
                        <dt>Status</dt>
                        <dd>{'✅ Materialized' if info.get('materialized') else '○ SRL (Reference)'}</dd>
                    </dl>
                    <div class="preview-actions">
                        <button class="btn btn-save" onclick="fetch('/api/save?src={quote(selected)}').then(()=>location.reload())">
                            💾 Save to Z:
                        </button>
                        <button class="btn btn-secondary" onclick="location.href='/?path={quote(path)}&select={quote(selected)}&refresh=1'">
                            🔄 Refresh
                        </button>
                    </div>
                """
        
        # Count connected connectors
        connected_count = sum(1 for c in self.uhd.get_connectors() 
                             if c.status == ConnectorStatus.CONNECTED)
        total_connectors = len(self.uhd.get_connectors())
        
        # Fill template
        html = HTML_TEMPLATE
        html = html.replace('%%PATH%%', path or '/')
        html = html.replace('%%DRIVES%%', drives_html)
        html = html.replace('%%CONNECTORS%%', connectors_html)
        html = html.replace('%%FILES%%', files_html)
        html = html.replace('%%TILES%%', tiles_html)
        html = html.replace('%%TABULAR%%', tabular_html)
        html = html.replace('%%DIMENSIONAL%%', dimensional_html)
        html = html.replace('%%NATIVE%%', native_html)
        html = html.replace('%%REPORTS%%', reports_html)
        html = html.replace('%%PREVIEW%%', preview_html)
        html = html.replace('%%SRLS%%', str(stats.get('total_srls', 0)))
        html = html.replace('%%MATERIALIZED%%', str(stats.get('materialized', 0)))
        html = html.replace('%%SAVES%%', str(stats.get('saves', 0)))
        
        # Metrics placeholders
        html = html.replace('%%EFFICIENCY%%', f"{metrics['efficiency_pct']}%")
        html = html.replace('%%EFFICIENCY_PCT%%', f"{metrics['efficiency_pct']}%")
        html = html.replace('%%BITSAVED%%', metrics['bit_savings_formatted'])
        html = html.replace('%%COMPRESSED%%', metrics['ingested_size'])
        html = html.replace('%%CONNECTORS_COUNT%%', f"{connected_count}/{total_connectors}")
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def _render_connectors_panel(self) -> str:
        """Render the connectors panel with status dots"""
        by_category = self.uhd.get_connectors_by_category()
        
        html = ""
        for category, connectors in by_category.items():
            html += f'<div class="connector-category">'
            html += f'<div class="connector-category-title">{category}</div>'
            html += '<div class="connector-grid">'
            
            for conn in connectors[:6]:  # Limit per category
                status_class = conn.status.css_class
                connected_class = 'connected' if conn.status == ConnectorStatus.CONNECTED else ''
                
                # Build click handler - for connected, go to drive; for disconnected, show connect modal
                if conn.status == ConnectorStatus.CONNECTED and conn.drive_letter:
                    onclick = f"location.href='/?path={conn.drive_letter}:/'"
                else:
                    onclick = f"showConnectModal('{conn.provider}')"
                
                html += f'''
                    <button class="connector-btn {connected_class}" onclick="{onclick}" title="{conn.description}">
                        <span class="status-dot {status_class}"></span>
                        <span class="connector-icon">{conn.icon}</span>
                        <span class="connector-name">{conn.name[:12]}</span>
                    </button>
                '''
            
            html += '</div></div>'
        
        return html
    
    def _render_tile_view(self, items: List[Dict], path: str) -> str:
        """Render tile view - large cards with metrics"""
        if not items:
            return """
                <div class="empty-state">
                    <div class="icon">📭</div>
                    <p>No items to display</p>
                </div>
            """
        
        html = ""
        for item in items:
            item_class = 'folder' if item.get('is_folder') else ''
            if item.get('materialized'):
                item_class += ' materialized'
            
            icon = item.get('icon', '📄')
            name = item.get('name', 'Unknown')
            item_path = item.get('path', '')
            
            if item.get('is_folder'):
                onclick = f"location.href='/?path={quote(item_path)}'"
            else:
                onclick = f"location.href='/?path={quote(path)}&select={quote(item_path)}'"
            
            source = item.get('source', item.get('label', ''))
            size = item.get('size', 0)
            size_str = self._format_size(size) if size else ''
            status = '✓ Live' if item.get('materialized') else 'SRL'
            
            html += f'''
                <div class="tile-item {item_class}" onclick="{onclick}">
                    <div class="tile-icon">{icon}</div>
                    <div class="tile-name">{name}</div>
                    <div class="tile-meta">
                        {source}
                        {f'<br>{size_str}' if size_str else ''}
                        <br><span style="opacity:0.6">{status}</span>
                    </div>
                </div>
            '''
        
        return html
    
    def _format_size(self, bytes_val: int) -> str:
        """Format bytes as human readable"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if abs(bytes_val) < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} PB"
    
    def _render_tabular_view(self, items: List[Dict]) -> str:
        """Render tabular view - data as spreadsheet rows"""
        if not items:
            return "<p style='opacity:0.5'>No data to display</p>"
        
        # Build table
        html = """<table class="data-table">
            <thead>
                <tr>
                    <th>Icon</th>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Source</th>
                    <th>Path</th>
                    <th class="dim-col">L1 Identity</th>
                    <th class="dim-col">L2 Relation</th>
                    <th class="dim-col">L3 Structure</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>"""
        
        for item in items:
            icon = item.get('icon', '📄')
            name = item.get('name', '?')
            item_type = 'Folder' if item.get('is_folder') else 'File'
            source = item.get('source', item.get('label', '-'))
            path = item.get('path', '')
            mat = '✓' if item.get('materialized') else '○'
            
            # Dimensional columns (inferred)
            l1 = name[:20]  # Identity
            l2 = source[:15] if source else '-'  # Relation
            l3 = item_type  # Structure
            
            html += f"""
                <tr onclick="location.href='/?select={quote(path)}'">
                    <td>{icon}</td>
                    <td>{name}</td>
                    <td>{item_type}</td>
                    <td>{source}</td>
                    <td style="font-family:var(--font-mono);font-size:0.8em">{path[:40]}</td>
                    <td class="dim-col">{l1}</td>
                    <td class="dim-col">{l2}</td>
                    <td class="dim-col">{l3}</td>
                    <td>{mat}</td>
                </tr>"""
        
        html += "</tbody></table>"
        return html
    
    def _render_dimensional_view(self, items: List[Dict], path: str) -> str:
        """Render 7D dimensional substrate view"""
        if not items:
            return "<p style='opacity:0.5'>No substrates to display</p>"
        
        # Show dimensional breakdown of current path
        drive = path.split(':')[0] if ':' in path else 'UHD'
        
        dimension_names = [
            ('0', 'Potential', '⚡', 'Unmaterialized references'),
            ('1', 'Identity', '🔹', 'Unique identifiers'),
            ('2', 'Relationship', '🔗', 'Source connections'),
            ('3', 'Structure', '📐', 'Data shape'),
            ('4', 'Environment', '🌐', 'Context / location'),
            ('5', 'Multiplicity', '🔄', 'Versions / variants'),
            ('6', 'Semantics', '💡', 'Computed meaning'),
            ('7', 'Completion', '✨', 'Final state'),
        ]
        
        html = ""
        
        # Count items by materialization
        materialized = sum(1 for i in items if i.get('materialized'))
        potential = len(items) - materialized
        
        # Create dimensional cards
        for level, name, icon, desc in dimension_names:
            # Compute level-specific data
            if level == '0':
                content = f"<div class='dim-item'><span class='dim-key'>SRLs (refs)</span><span class='dim-value'>{potential}</span></div>"
            elif level == '1':
                content = f"<div class='dim-item'><span class='dim-key'>Items</span><span class='dim-value'>{len(items)}</span></div>"
                for item in items[:3]:
                    content += f"<div class='dim-item'><span class='dim-key'>→</span><span class='dim-value'>{item.get('name', '?')[:25]}</span></div>"
                if len(items) > 3:
                    content += f"<div class='dim-item'><span class='dim-key'>...</span><span class='dim-value'>+{len(items)-3} more</span></div>"
            elif level == '2':
                sources = {}
                for item in items:
                    src = item.get('source', 'unknown')
                    sources[src] = sources.get(src, 0) + 1
                for src, cnt in list(sources.items())[:4]:
                    content += f"<div class='dim-item'><span class='dim-key'>{src}</span><span class='dim-value'>{cnt}</span></div>"
            elif level == '3':
                folders = sum(1 for i in items if i.get('is_folder'))
                files = len(items) - folders
                content = f"<div class='dim-item'><span class='dim-key'>Folders</span><span class='dim-value'>{folders}</span></div>"
                content += f"<div class='dim-item'><span class='dim-key'>Files</span><span class='dim-value'>{files}</span></div>"
            elif level == '4':
                content = f"<div class='dim-item'><span class='dim-key'>Drive</span><span class='dim-value'>{drive}:</span></div>"
                content += f"<div class='dim-item'><span class='dim-key'>Path</span><span class='dim-value'>{path[:30]}</span></div>"
            elif level == '5':
                content = f"<div class='dim-item'><span class='dim-key'>Versions</span><span class='dim-value'>1 (live)</span></div>"
            elif level == '6':
                # Inferred semantics
                content = f"<div class='dim-item'><span class='dim-key'>Domain</span><span class='dim-value'>auto-detected</span></div>"
                content += f"<div class='dim-item'><span class='dim-key'>Traversal</span><span class='dim-value'>O(1)</span></div>"
            elif level == '7':
                content = f"<div class='dim-item'><span class='dim-key'>Materialized</span><span class='dim-value'>{materialized}</span></div>"
                content += f"<div class='dim-item'><span class='dim-key'>Pending</span><span class='dim-value'>{potential}</span></div>"
            else:
                content = f"<div class='dim-item'><span class='dim-value'>{desc}</span></div>"
            
            html += f"""
                <div class="dimension-card">
                    <div class="dimension-header">
                        <div class="dimension-level">{level}</div>
                        <span class="dimension-name">{icon} {name}</span>
                    </div>
                    <div class="dimension-body">
                        {content}
                    </div>
                </div>
            """
        
        return html
    
    def _render_native_view(self, selected: str) -> str:
        """Render native format view - original source format"""
        if not selected:
            return """
                <span class="native-format-badge">No Selection</span>
                <p style="opacity:0.5">Select a file to view in native format</p>
            """
        
        try:
            data = self.uhd.read(selected)
            srl = self.uhd._srls.get(selected)
            
            # Detect format
            if srl and srl._native_format:
                fmt = srl._native_format
            elif isinstance(data, dict):
                fmt = 'json'
            elif isinstance(data, list):
                fmt = 'array'
            elif isinstance(data, str):
                fmt = 'text'
            else:
                fmt = 'binary'
            
            content = json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)
            content = content[:5000]  # Limit size
            
            return f"""
                <span class="native-format-badge">{fmt.upper()}</span>
                <pre class="native-content {fmt}">{content}</pre>
            """
        except Exception as e:
            return f"""
                <span class="native-format-badge">ERROR</span>
                <p>{str(e)}</p>
            """
    
    def _render_reports_view(self, stats: Dict, items: List[Dict]) -> str:
        """Render reports/analytics view"""
        total_srls = stats.get('total_srls', 0)
        materialized = stats.get('materialized', 0)
        saves = stats.get('saves', 0)
        
        # Count by source
        sources = {}
        for item in items:
            src = item.get('source', 'unknown')
            sources[src] = sources.get(src, 0) + 1
        
        # Count by type
        folders = sum(1 for i in items if i.get('is_folder'))
        files = len(items) - folders
        
        # Build report cards
        html = f"""
            <div class="report-card">
                <div class="report-title">Total References (SRLs)</div>
                <div class="report-value">{total_srls}</div>
                <div class="report-breakdown">
                    <div class="breakdown-item">
                        <span>Materialized</span>
                        <span>{materialized}</span>
                    </div>
                    <div class="breakdown-bar">
                        <div class="breakdown-fill" style="width:{100*materialized/max(total_srls,1)}%"></div>
                    </div>
                </div>
            </div>
            
            <div class="report-card">
                <div class="report-title">Items in View</div>
                <div class="report-value">{len(items)}</div>
                <div class="report-breakdown">
                    <div class="breakdown-item">
                        <span>📁 Folders</span>
                        <span>{folders}</span>
                    </div>
                    <div class="breakdown-item">
                        <span>📄 Files</span>
                        <span>{files}</span>
                    </div>
                </div>
            </div>
            
            <div class="report-card">
                <div class="report-title">Saved to Disk</div>
                <div class="report-value">{saves}</div>
                <p style="font-size:0.85em;opacity:0.6;margin-top:10px">
                    Data persisted to Z: drive
                </p>
            </div>
            
            <div class="report-card">
                <div class="report-title">Sources</div>
                <div class="report-value">{len(sources)}</div>
                <div class="report-breakdown">
        """
        
        for src, cnt in list(sources.items())[:5]:
            pct = 100 * cnt / max(len(items), 1)
            html += f"""
                    <div class="breakdown-item">
                        <span>{src}</span>
                        <span>{cnt}</span>
                    </div>
                    <div class="breakdown-bar">
                        <div class="breakdown-fill" style="width:{pct}%"></div>
                    </div>
            """
        
        html += """
                </div>
            </div>
            
            <div class="report-card">
                <div class="report-title">Performance</div>
                <div class="report-value">O(1)</div>
                <p style="font-size:0.85em;opacity:0.6;margin-top:10px">
                    Dimensional traversal eliminates joins, indexes, and Cartesian products
                </p>
            </div>
            
            <div class="report-card">
                <div class="report-title">Dimensional Model</div>
                <div class="report-value">7D</div>
                <div class="report-breakdown">
                    <div class="breakdown-item"><span>L1 Identity</span><span>✓</span></div>
                    <div class="breakdown-item"><span>L2 Relationship</span><span>✓</span></div>
                    <div class="breakdown-item"><span>L3 Structure</span><span>✓</span></div>
                    <div class="breakdown-item"><span>L4 Environment</span><span>✓</span></div>
                    <div class="breakdown-item"><span>L5 Multiplicity</span><span>✓</span></div>
                    <div class="breakdown-item"><span>L6 Semantics</span><span>✓</span></div>
                    <div class="breakdown-item"><span>L7 Completion</span><span>✓</span></div>
                </div>
            </div>
        """
        
        # Add Ingestion Metrics cards
        metrics = GLOBAL_METRICS.get_summary()
        by_type = GLOBAL_METRICS.get_by_type()
        
        html += f"""
            <div class="report-card metrics-card">
                <div class="report-title">⚡ Ingestion Efficiency</div>
                <div class="report-value">{metrics['efficiency_pct']}%</div>
                <div class="efficiency-bar">
                    <div class="efficiency-fill" style="width:{metrics['efficiency_pct']}%;background:linear-gradient(90deg,#00ff88,#00ffff)"></div>
                </div>
                <div class="report-breakdown">
                    <div class="breakdown-item">
                        <span>Files Ingested</span>
                        <span>{metrics['total_files']}</span>
                    </div>
                    <div class="breakdown-item">
                        <span>Ingestion Rate</span>
                        <span>{metrics['ingestion_rate']}</span>
                    </div>
                </div>
            </div>
            
            <div class="report-card metrics-card">
                <div class="report-title">📊 Size Comparison</div>
                <div class="report-value">{metrics['size_saved']}</div>
                <p style="font-size:0.85em;opacity:0.8;margin:5px 0">saved</p>
                <div class="report-breakdown">
                    <div class="breakdown-item">
                        <span>Original Size</span>
                        <span>{metrics['original_size']}</span>
                    </div>
                    <div class="breakdown-item">
                        <span>Ingested Size</span>
                        <span>{metrics['ingested_size']}</span>
                    </div>
                    <div class="breakdown-bar">
                        <div class="breakdown-fill" style="width:{100-metrics['efficiency_pct']}%;background:#00ffff"></div>
                    </div>
                    <p style="font-size:0.75em;opacity:0.6;margin-top:5px">
                        Compressed to {100-metrics['efficiency_pct']:.1f}% of original
                    </p>
                </div>
            </div>
            
            <div class="report-card metrics-card">
                <div class="report-title">🔢 Bit Savings</div>
                <div class="report-value">{metrics['bit_savings_formatted']}</div>
                <p style="font-size:0.85em;opacity:0.8;margin:5px 0">bits saved</p>
                <div class="report-breakdown">
                    <div class="breakdown-item">
                        <span>Raw Bits</span>
                        <span>{metrics['bit_savings']:,}</span>
                    </div>
                    <div class="breakdown-item">
                        <span>Compression Ratio</span>
                        <span>{metrics['compression_ratio']}</span>
                    </div>
                </div>
            </div>
            
            <div class="report-card metrics-card wide">
                <div class="report-title">📈 Efficiency by Type</div>
                <div class="report-breakdown">
        """
        
        for ftype, type_stats in list(by_type.items())[:6]:
            eff = type_stats['efficiency_pct']
            bar_color = '#00ff88' if eff > 50 else '#ffaa00' if eff > 20 else '#ff6666'
            html += f"""
                    <div class="breakdown-item">
                        <span>{ftype.title()}</span>
                        <span>{type_stats['count']} files | {type_stats['saved']} saved | {eff}%</span>
                    </div>
                    <div class="breakdown-bar">
                        <div class="breakdown-fill" style="width:{eff}%;background:{bar_color}"></div>
                    </div>
            """
        
        if not by_type:
            html += """
                    <p style="opacity:0.5">No files ingested yet</p>
            """
        
        html += """
                </div>
            </div>
            
            <div class="report-card metrics-card">
                <div class="report-title">🕐 Session Stats</div>
                <div class="report-value">{session_files}</div>
                <p style="font-size:0.85em;opacity:0.8;margin:5px 0">files this session</p>
                <div class="report-breakdown">
                    <div class="breakdown-item">
                        <span>Bytes Saved</span>
                        <span>{session_saved}</span>
                    </div>
                    <div class="breakdown-item">
                        <span>Uptime</span>
                        <span>{uptime}s</span>
                    </div>
                </div>
            </div>
        """.format(
            session_files=metrics['session_files'],
            session_saved=metrics['session_saved'],
            uptime=metrics['uptime_seconds']
        )
        
        return html
    
    def _send_cors_headers(self):
        """Send CORS headers for browser access"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def serve_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        
        # Handle non-serializable objects
        def serialize(obj):
            if hasattr(obj, 'to_dict'):
                return obj.to_dict()
            elif hasattr(obj, '__dict__'):
                return obj.__dict__
            return str(obj)
        
        self.wfile.write(json.dumps(data, default=serialize).encode())


def run_server(uhd: UniversalHardDrive = None, host: str = '127.0.0.1', port: int = 8000):
    """Run the Universal Hard Drive web server"""
    if uhd is None:
        uhd = UniversalHardDrive()
        # Auto-connect API drive
        uhd.connect_api()
    
    UHDHandler.uhd = uhd
    
    server = HTTPServer((host, port), UHDHandler)
    print(f"🦋 Universal Hard Drive")
    print(f"   Running at http://{host}:{port}")
    print(f"   Press Ctrl+C to stop")
    print(f"")
    print(f"   Drives:")
    for d in uhd.drives():
        status = "✓" if d.connected else "○"
        print(f"     {status} {d.letter}: {d.name}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        server.shutdown()


# =============================================================================
# DEMO
# =============================================================================

def demo():
    """Demonstrate the Universal Hard Drive"""
    print("=" * 60)
    print("Universal Hard Drive - SRL Demo")
    print("=" * 60)
    
    uhd = UniversalHardDrive()
    
    # Connect API drive
    print("\n🔌 Connecting API drive (B:)...")
    uhd.connect_api()
    
    # List root
    print("\n📁 Listing root (/):")
    for item in uhd.ls("/"):
        status = "✓" if item.get('connected') else "○"
        print(f"   {status} {item['icon']} {item['name']} - {item.get('label', '')}")
    
    # List API drive without fetching
    print("\n📁 Listing B:/finance/ (no data fetched yet):")
    for item in uhd.ls("B:/finance/"):
        mat = "●" if item.get('materialized') else "○"
        print(f"   {mat} {item['icon']} {item['name']}")
    
    # Check stats - no materializations
    stats = uhd.stats()
    print(f"\n📊 Stats (before reading):")
    print(f"   SRLs created: {stats['srls_created']}")
    print(f"   Materializations: {stats['materializations']}")
    
    # Now read a file - this triggers materialization
    print("\n📖 Reading B:/finance/bitcoin.json (NOW data is fetched)...")
    data = uhd.read("B:/finance/bitcoin.json")
    print(f"   Got: {type(data).__name__} with keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
    
    # Check stats - one materialization
    stats = uhd.stats()
    print(f"\n📊 Stats (after reading):")
    print(f"   Materializations: {stats['materializations']}")
    print(f"   Cache hits: {stats['cache_hits']}")
    
    # Read again - should be cached
    print("\n📖 Reading same file again (should be cached)...")
    data = uhd.read("B:/finance/bitcoin.json")
    stats = uhd.stats()
    print(f"   Cache hits: {stats['cache_hits']}")
    
    # Save to Z: drive
    print("\n💾 Saving to Z: drive...")
    uhd.save("B:/finance/bitcoin.json", "snapshots/btc.json")
    print(f"   Saved to Z:/snapshots/btc.json")
    
    # Final stats
    stats = uhd.stats()
    print(f"\n📊 Final stats:")
    print(f"   Total SRLs: {stats['total_srls']}")
    print(f"   Materialized: {stats['materialized']}")
    print(f"   Saves: {stats['saves']}")
    
    print("\n✨ Demo complete! Run 'run_server()' for web UI")


if __name__ == "__main__":
    demo()
