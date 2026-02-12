"""
Dimensional Explorer - Windows Explorer for the Helix Paradigm

A unified file explorer that organizes ALL data dimensionally:
- Local files and folders
- Remote API data
- Cached content
- With content-based Q&A (like AI, but purely content-driven)

Features:
    - Windows Explorer-like 3-pane UI
    - Tree view (dimensional hierarchy)
    - List view (items at current level)
    - Preview pane (content + metadata)
    - Unified local + remote navigation
    - Content search across everything
    - Q&A system learns from indexed content

Dimensional Mapping:
    Level 6 (Whole):     The entire explorer
    Level 5 (Volume):    Sources (Local, APIs, Cache)
    Level 4 (Plane):     Folders / Categories
    Level 3 (Width):     Files / Items
    Level 2 (Length):    Content sections
    Level 1 (Point):     Individual values
    Level 0 (Potential): Unindexed data

Usage:
    from apps.dimensional_explorer import DimensionalExplorer, run_explorer
    
    explorer = DimensionalExplorer()
    explorer.index_local("C:/Users/Documents")
    explorer.index_api("weather")
    
    # Q&A based on content
    answer = explorer.ask("What is the ISS position?")
    
    # Run web UI
    run_explorer(port=8000)
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
import threading
import mimetypes
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


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class ExplorerNode:
    """A node in the dimensional hierarchy"""
    id: str
    name: str
    node_type: str  # 'source', 'folder', 'file', 'api', 'item'
    level: int
    parent_id: Optional[str] = None
    path: str = ""
    icon: str = "📄"
    size: int = 0
    modified: str = ""
    mime_type: str = ""
    children_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class ContentIndex:
    """Indexed content for search/Q&A"""
    node_id: str
    content: str
    keywords: Set[str] = field(default_factory=set)
    summary: str = ""
    indexed_at: str = field(default_factory=lambda: datetime.now().isoformat())


# =============================================================================
# DIMENSIONAL EXPLORER
# =============================================================================

class DimensionalExplorer:
    """
    Dimensional Explorer - Unified Data Navigation
    
    Combines:
    - Local filesystem
    - Remote APIs (via UniversalConnector)
    - Cached data
    - Content-based search and Q&A
    """
    
    # Icons for different types
    ICONS = {
        'source': '🌐',
        'local': '💻',
        'api': '🔌',
        'cache': '📦',
        'folder': '📁',
        'file': '📄',
        'image': '🖼️',
        'document': '📝',
        'code': '💻',
        'data': '📊',
        'config': '⚙️',
        'unknown': '❓'
    }
    
    FILE_ICONS = {
        '.txt': '📝', '.md': '📝', '.doc': '📝', '.docx': '📝',
        '.py': '🐍', '.js': '💛', '.ts': '💙', '.html': '🌐', '.css': '🎨',
        '.json': '📊', '.xml': '📊', '.csv': '📊', '.yaml': '📊',
        '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️', '.svg': '🖼️',
        '.pdf': '📕', '.zip': '📦', '.exe': '⚙️', '.bat': '⚙️',
    }
    
    def __init__(self, data_dir: str = "data/explorer"):
        # Helix components
        self.kernel = HelixKernel()
        self.substrate = ManifoldSubstrate()
        self.kernel.set_substrate(self.substrate)
        
        self.cache = HelixCache()
        self.logger = HelixLogger(min_level=3)
        
        # Data directory
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Node hierarchy
        self._nodes: Dict[str, ExplorerNode] = {}
        self._children: Dict[str, Set[str]] = {}  # parent_id -> child_ids
        self._by_level: Dict[int, Set[str]] = {i: set() for i in range(7)}
        
        # Content index for Q&A
        self._content_index: Dict[str, ContentIndex] = {}
        self._keyword_index: Dict[str, Set[str]] = {}  # keyword -> node_ids
        
        # Integrated services
        self._connector = UniversalConnector()
        self._database = HelixDatabase(str(self.data_dir / "explorer.helix.json"))
        
        # Current navigation state
        self._current_node: Optional[str] = "root"  # Start at root
        self._current_level: int = 6
        self._history: List[str] = []
        
        # Stats
        self._stats = {
            'nodes': 0,
            'indexed': 0,
            'searches': 0,
            'questions': 0
        }
        
        # Initialize root structure
        self._init_structure()
        self._load_state()
        
        self.logger.whole("Dimensional Explorer initialized")
    
    def _init_structure(self):
        """Initialize the root structure"""
        # Root node (Level 6)
        root = ExplorerNode(
            id="root",
            name="Dimensional Explorer",
            node_type="source",
            level=6,
            icon="🦋",
            path="/"
        )
        self._add_node(root)
        
        # Source nodes (Level 5)
        sources = [
            ("local", "Local Files", "💻", "/local"),
            ("apis", "Connected APIs", "🔌", "/apis"),
            ("cache", "Cached Data", "📦", "/cache"),
        ]
        
        for src_id, name, icon, path in sources:
            node = ExplorerNode(
                id=src_id,
                name=name,
                node_type="source",
                level=5,
                parent_id="root",
                icon=icon,
                path=path
            )
            self._add_node(node)
        
        # Add API categories as Level 4 under 'apis'
        for cat_name, cat_data in API_REGISTRY.items():
            node = ExplorerNode(
                id=f"api_{cat_name}",
                name=cat_name.title(),
                node_type="folder",
                level=4,
                parent_id="apis",
                icon=cat_data['icon'],
                path=f"/apis/{cat_name}",
                children_count=len(cat_data['apis'])
            )
            self._add_node(node)
            
            # Add individual APIs as Level 3
            for api_name, api_data in cat_data['apis'].items():
                api_node = ExplorerNode(
                    id=f"api_{cat_name}_{api_name}",
                    name=api_name,
                    node_type="api",
                    level=3,
                    parent_id=f"api_{cat_name}",
                    icon="🔗",
                    path=f"/apis/{cat_name}/{api_name}",
                    metadata={
                        'url': api_data['url'],
                        'description': api_data.get('description', ''),
                        'fields': api_data.get('fields', [])
                    }
                )
                self._add_node(api_node)
    
    def _add_node(self, node: ExplorerNode):
        """Add a node to the hierarchy"""
        self._nodes[node.id] = node
        self._by_level[node.level].add(node.id)
        
        if node.parent_id:
            if node.parent_id not in self._children:
                self._children[node.parent_id] = set()
            self._children[node.parent_id].add(node.id)
            
            # Update parent's children count
            if node.parent_id in self._nodes:
                self._nodes[node.parent_id].children_count = len(self._children[node.parent_id])
        
        self._stats['nodes'] = len(self._nodes)
    
    def _load_state(self):
        """Load saved state"""
        state_file = self.data_dir / "explorer_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    self._current_node = state.get('current_node', 'root')
                    self._history = state.get('history', [])
            except:
                pass
    
    def _save_state(self):
        """Save current state"""
        state = {
            'current_node': self._current_node,
            'history': self._history[-50:]  # Keep last 50
        }
        with open(self.data_dir / "explorer_state.json", 'w') as f:
            json.dump(state, f)
    
    # -------------------------------------------------------------------------
    # Local File Indexing
    # -------------------------------------------------------------------------
    
    def index_local(self, path: str, max_depth: int = 3) -> int:
        """
        Index a local directory into the explorer.
        
        Args:
            path: Local filesystem path
            max_depth: Maximum folder depth to index
            
        Returns:
            Number of items indexed
        """
        path = Path(path).resolve()  # Resolve to absolute path
        if not path.exists():
            return 0
        
        count = 0
        folder_name = path.name or "workspace"  # Handle root or "." paths
        base_id = f"local_{folder_name}"
        
        # Create folder node
        folder_node = ExplorerNode(
            id=base_id,
            name=folder_name,
            node_type="folder",
            level=4,
            parent_id="local",
            icon="📁",
            path=f"/local/{folder_name}",
            metadata={'local_path': str(path)}
        )
        self._add_node(folder_node)
        count += 1
        
        # Index contents recursively
        count += self._index_directory(path, base_id, current_depth=0, max_depth=max_depth)
        
        self.logger.width(f"Indexed {count} items from {path}")
        return count
    
    def _index_directory(self, path: Path, parent_id: str, current_depth: int, max_depth: int) -> int:
        """Recursively index a directory"""
        if current_depth >= max_depth:
            return 0
        
        count = 0
        try:
            for item in path.iterdir():
                item_id = f"{parent_id}_{item.name}".replace(" ", "_").replace(".", "_")
                
                if item.is_dir():
                    node = ExplorerNode(
                        id=item_id,
                        name=item.name,
                        node_type="folder",
                        level=4 - min(current_depth, 2),  # Folders at levels 4, 3, 2
                        parent_id=parent_id,
                        icon="📁",
                        path=f"{self._nodes[parent_id].path}/{item.name}",
                        metadata={'local_path': str(item)}
                    )
                    self._add_node(node)
                    count += 1
                    count += self._index_directory(item, item_id, current_depth + 1, max_depth)
                else:
                    # File
                    ext = item.suffix.lower()
                    icon = self.FILE_ICONS.get(ext, '📄')
                    mime = mimetypes.guess_type(str(item))[0] or 'application/octet-stream'
                    
                    try:
                        stat = item.stat()
                        size = stat.st_size
                        modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
                    except:
                        size = 0
                        modified = ""
                    
                    node = ExplorerNode(
                        id=item_id,
                        name=item.name,
                        node_type="file",
                        level=3,  # Files at level 3
                        parent_id=parent_id,
                        icon=icon,
                        path=f"{self._nodes[parent_id].path}/{item.name}",
                        size=size,
                        modified=modified,
                        mime_type=mime,
                        metadata={'local_path': str(item)}
                    )
                    self._add_node(node)
                    count += 1
                    
                    # Index text content
                    if ext in ['.txt', '.md', '.py', '.js', '.json', '.html', '.css', '.yaml', '.yml']:
                        self._index_file_content(item_id, item)
        except PermissionError:
            pass
        
        return count
    
    def _index_file_content(self, node_id: str, path: Path):
        """Index file content for search/Q&A"""
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')[:10000]  # First 10KB
            self._index_content(node_id, content)
        except:
            pass
    
    # -------------------------------------------------------------------------
    # API Data Indexing
    # -------------------------------------------------------------------------
    
    def fetch_api(self, api_name: str) -> Optional[Dict]:
        """Fetch data from an API and index it"""
        result = self._connector.connect(api_name)
        
        if result.success and result.data:
            # Find the API node
            for node_id, node in self._nodes.items():
                if node.node_type == "api" and api_name in node_id:
                    # Store in cache
                    cache_id = f"cache_{api_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    cache_node = ExplorerNode(
                        id=cache_id,
                        name=f"{api_name} ({datetime.now().strftime('%H:%M')})",
                        node_type="item",
                        level=3,
                        parent_id="cache",
                        icon="📥",
                        path=f"/cache/{cache_id}",
                        modified=datetime.now().isoformat(),
                        metadata={
                            'api': api_name,
                            'data': result.data,
                            'fetched_at': result.fetched_at
                        }
                    )
                    self._add_node(cache_node)
                    
                    # Index content
                    self._index_content(cache_id, json.dumps(result.data, indent=2))
                    
                    return result.data
        
        return None
    
    def fetch_category(self, category: str) -> List[Dict]:
        """Fetch all APIs in a category"""
        results = []
        for api_name in self._connector._by_category.get(category, []):
            data = self.fetch_api(api_name)
            if data:
                results.append({'api': api_name, 'data': data})
        return results
    
    # -------------------------------------------------------------------------
    # Content Indexing & Q&A
    # -------------------------------------------------------------------------
    
    def _index_content(self, node_id: str, content: str):
        """Index content for search and Q&A"""
        # Extract keywords (simple tokenization)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        keywords = set(words)
        
        # Create summary (first 200 chars)
        summary = ' '.join(content.split()[:50])
        if len(summary) > 200:
            summary = summary[:197] + "..."
        
        # Store index
        index = ContentIndex(
            node_id=node_id,
            content=content,
            keywords=keywords,
            summary=summary
        )
        self._content_index[node_id] = index
        
        # Update keyword index
        for keyword in keywords:
            if keyword not in self._keyword_index:
                self._keyword_index[keyword] = set()
            self._keyword_index[keyword].add(node_id)
        
        self._stats['indexed'] += 1
    
    def search(self, query: str, limit: int = 10) -> List[Tuple[ExplorerNode, float]]:
        """
        Search indexed content.
        
        Returns list of (node, relevance_score) tuples.
        """
        self._stats['searches'] += 1
        
        query_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', query.lower()))
        
        if not query_words:
            return []
        
        # Find nodes matching query words
        scores: Dict[str, float] = {}
        
        for word in query_words:
            for node_id in self._keyword_index.get(word, []):
                if node_id not in scores:
                    scores[node_id] = 0
                scores[node_id] += 1
        
        # Normalize scores
        max_score = max(scores.values()) if scores else 1
        for node_id in scores:
            scores[node_id] /= max_score
            
            # Boost if query appears in content
            if node_id in self._content_index:
                content = self._content_index[node_id].content.lower()
                if query.lower() in content:
                    scores[node_id] *= 1.5
        
        # Sort by score
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return [
            (self._nodes[node_id], score)
            for node_id, score in sorted_results
            if node_id in self._nodes
        ]
    
    def ask(self, question: str) -> str:
        """
        Answer a question based on indexed content.
        
        This is content-based Q&A - not AI generation,
        but intelligent content retrieval and synthesis.
        """
        self._stats['questions'] += 1
        
        # Search for relevant content
        results = self.search(question, limit=5)
        
        if not results:
            return "I don't have any indexed content related to that question. Try indexing some files or fetching API data first."
        
        # Build answer from relevant content
        answer_parts = []
        
        for node, score in results:
            if node.id in self._content_index:
                index = self._content_index[node.id]
                
                # Find most relevant snippet
                content = index.content
                question_words = question.lower().split()
                
                # Find sentence containing query terms
                sentences = re.split(r'[.!?\n]', content)
                best_sentence = ""
                best_match = 0
                
                for sentence in sentences:
                    sentence_lower = sentence.lower()
                    matches = sum(1 for w in question_words if w in sentence_lower)
                    if matches > best_match:
                        best_match = matches
                        best_sentence = sentence.strip()
                
                if best_sentence:
                    answer_parts.append({
                        'source': node.name,
                        'path': node.path,
                        'content': best_sentence[:300],
                        'score': score
                    })
        
        if not answer_parts:
            return "I found related content but couldn't extract a specific answer. Try rephrasing your question."
        
        # Format answer
        lines = ["Based on indexed content:\n"]
        
        for part in answer_parts[:3]:
            lines.append(f"**{part['source']}** ({part['path']}):")
            lines.append(f"  \"{part['content']}\"")
            lines.append("")
        
        return '\n'.join(lines)
    
    # -------------------------------------------------------------------------
    # Navigation
    # -------------------------------------------------------------------------
    
    def navigate(self, node_id: str) -> Optional[ExplorerNode]:
        """Navigate to a node"""
        if node_id in self._nodes:
            self._history.append(self._current_node or "root")
            self._current_node = node_id
            self._current_level = self._nodes[node_id].level
            self._save_state()
            return self._nodes[node_id]
        return None
    
    def go_back(self) -> Optional[ExplorerNode]:
        """Go back in history"""
        if self._history:
            node_id = self._history.pop()
            self._current_node = node_id
            self._current_level = self._nodes[node_id].level
            self._save_state()
            return self._nodes[node_id]
        return None
    
    def go_up(self) -> Optional[ExplorerNode]:
        """Go to parent node"""
        if self._current_node and self._current_node in self._nodes:
            parent_id = self._nodes[self._current_node].parent_id
            if parent_id:
                return self.navigate(parent_id)
        return None
    
    def get_current(self) -> Optional[ExplorerNode]:
        """Get current node"""
        if self._current_node:
            return self._nodes.get(self._current_node)
        return self._nodes.get("root")
    
    def get_children(self, node_id: str = None) -> List[ExplorerNode]:
        """Get children of a node"""
        if node_id is None:
            node_id = self._current_node or "root"
        
        child_ids = self._children.get(node_id, set())
        return [self._nodes[cid] for cid in child_ids if cid in self._nodes]
    
    def get_breadcrumb(self) -> List[ExplorerNode]:
        """Get path from root to current node"""
        breadcrumb = []
        node_id = self._current_node
        
        while node_id and node_id in self._nodes:
            breadcrumb.insert(0, self._nodes[node_id])
            node_id = self._nodes[node_id].parent_id
        
        return breadcrumb
    
    # -------------------------------------------------------------------------
    # Tree View
    # -------------------------------------------------------------------------
    
    def get_tree(self, max_depth: int = 3) -> List[Dict]:
        """Get tree structure for sidebar"""
        def build_tree(node_id: str, depth: int = 0) -> Dict:
            node = self._nodes[node_id]
            result = {
                'id': node.id,
                'name': node.name,
                'icon': node.icon,
                'type': node.node_type,
                'level': node.level,
                'path': node.path,
                'children': []
            }
            
            if depth < max_depth:
                for child_id in sorted(self._children.get(node_id, [])):
                    child = self._nodes.get(child_id)
                    if child and child.node_type in ['source', 'folder', 'api']:
                        result['children'].append(build_tree(child_id, depth + 1))
            
            return result
        
        return [build_tree("root")]
    
    # -------------------------------------------------------------------------
    # Info & Stats
    # -------------------------------------------------------------------------
    
    def stats(self) -> Dict[str, Any]:
        """Get explorer statistics"""
        return {
            **self._stats,
            'sources': len([n for n in self._nodes.values() if n.node_type == 'source']),
            'folders': len([n for n in self._nodes.values() if n.node_type == 'folder']),
            'files': len([n for n in self._nodes.values() if n.node_type in ['file', 'item']]),
            'api_categories': len(API_REGISTRY),
            'total_apis': len(self._connector._connections)
        }
    
    def get_preview(self, node_id: str) -> Dict[str, Any]:
        """Get preview data for a node"""
        node = self._nodes.get(node_id)
        if not node:
            return {}
        
        preview = {
            'id': node.id,
            'name': node.name,
            'type': node.node_type,
            'icon': node.icon,
            'path': node.path,
            'level': node.level,
            'level_name': LEVEL_NAMES.get(node.level, 'Unknown'),
            'size': node.size,
            'modified': node.modified,
            'mime_type': node.mime_type,
            'metadata': node.metadata,
            'children_count': node.children_count
        }
        
        # Add content preview if indexed
        if node_id in self._content_index:
            preview['content'] = self._content_index[node_id].content[:2000]
            preview['summary'] = self._content_index[node_id].summary
        
        # Add API data if available
        if node.node_type == 'api':
            preview['can_fetch'] = True
            preview['api_url'] = node.metadata.get('url', '')
            preview['description'] = node.metadata.get('description', '')
        
        return preview


# =============================================================================
# WEB SERVER - Windows Explorer Style
# =============================================================================

EXPLORER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dimensional Explorer</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        :root {
            --bg-dark: #1a1a2e;
            --bg-medium: #232342;
            --bg-light: #2a2a4e;
            --border: #3a3a5e;
            --accent: #9d4edd;
            --accent-light: #c77dff;
            --text: #e0e0e0;
            --text-dim: #888;
        }
        
        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-dark);
            color: var(--text);
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        /* Toolbar */
        .toolbar {
            background: linear-gradient(180deg, #4a3875 0%, #3a2865 100%);
            padding: 8px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 1px solid var(--border);
        }
        
        .toolbar-brand {
            font-size: 1.3em;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .toolbar-btn {
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .toolbar-btn:hover { background: rgba(255,255,255,0.2); }
        
        .breadcrumb {
            flex: 1;
            background: var(--bg-medium);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 6px 12px;
            display: flex;
            align-items: center;
            gap: 4px;
            overflow-x: auto;
        }
        .breadcrumb a {
            color: var(--accent-light);
            text-decoration: none;
        }
        .breadcrumb a:hover { text-decoration: underline; }
        .breadcrumb span { color: var(--text-dim); }
        
        .search-box {
            display: flex;
            gap: 4px;
        }
        .search-box input {
            background: var(--bg-medium);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 6px 12px;
            border-radius: 4px;
            width: 250px;
        }
        .search-box input:focus {
            outline: none;
            border-color: var(--accent);
        }
        
        /* Main Layout */
        .main {
            flex: 1;
            display: flex;
            overflow: hidden;
        }
        
        /* Sidebar (Tree View) */
        .sidebar {
            width: 250px;
            background: var(--bg-medium);
            border-right: 1px solid var(--border);
            overflow-y: auto;
            padding: 8px;
        }
        
        .tree-node {
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            margin: 2px 0;
        }
        .tree-node:hover { background: var(--bg-light); }
        .tree-node.selected { background: var(--accent); }
        .tree-node-icon { width: 16px; text-align: center; }
        .tree-children { padding-left: 16px; }
        
        /* Content (List View) */
        .content {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
        }
        
        .item-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 12px;
        }
        
        .item-card {
            background: var(--bg-light);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .item-card:hover {
            border-color: var(--accent);
            transform: translateY(-2px);
        }
        .item-card-icon { font-size: 2em; margin-bottom: 8px; }
        .item-card-name { font-weight: 500; margin-bottom: 4px; }
        .item-card-meta { font-size: 0.85em; color: var(--text-dim); }
        
        /* Preview Pane */
        .preview {
            width: 300px;
            background: var(--bg-medium);
            border-left: 1px solid var(--border);
            padding: 16px;
            overflow-y: auto;
        }
        
        .preview-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border);
        }
        .preview-icon { font-size: 3em; }
        .preview-name { font-size: 1.2em; font-weight: 500; }
        .preview-type { color: var(--text-dim); font-size: 0.9em; }
        
        .preview-section {
            margin-bottom: 16px;
        }
        .preview-section-title {
            font-size: 0.85em;
            color: var(--text-dim);
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        .preview-content {
            background: var(--bg-dark);
            border-radius: 4px;
            padding: 12px;
            font-family: monospace;
            font-size: 0.85em;
            max-height: 200px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-break: break-word;
        }
        
        .preview-btn {
            background: var(--accent);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
            margin-top: 8px;
        }
        .preview-btn:hover { background: var(--accent-light); }
        
        /* Q&A Section */
        .qa-section {
            background: var(--bg-light);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
        }
        .qa-input {
            width: 100%;
            background: var(--bg-dark);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 8px;
        }
        .qa-answer {
            background: var(--bg-dark);
            border-radius: 4px;
            padding: 12px;
            margin-top: 12px;
            font-size: 0.9em;
            max-height: 300px;
            overflow-y: auto;
        }
        
        /* Status Bar */
        .statusbar {
            background: var(--bg-medium);
            border-top: 1px solid var(--border);
            padding: 4px 16px;
            font-size: 0.85em;
            color: var(--text-dim);
            display: flex;
            justify-content: space-between;
        }
        
        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 50px;
            color: var(--text-dim);
        }
        .empty-state-icon { font-size: 4em; margin-bottom: 16px; }
    </style>
</head>
<body>
    <div class="toolbar">
        <div class="toolbar-brand">🦋 Dimensional Explorer</div>
        <a href="/?action=back" class="toolbar-btn" style="text-decoration:none;">← Back</a>
        <a href="/?action=up" class="toolbar-btn" style="text-decoration:none;">↑ Up</a>
        <div class="breadcrumb">%%BREADCRUMB%%</div>
        <form class="search-box" method="get" action="/">
            <input type="text" name="q" placeholder="Search or ask a question (end with ?)">
            <button type="submit" class="toolbar-btn">🔍</button>
        </form>
    </div>
    
    <div class="main">
        <div class="sidebar">%%TREE%%</div>
        <div class="content">%%CONTENT%%</div>
        <div class="preview">%%PREVIEW%%</div>
    </div>
    
    <div class="statusbar">
        <span>%%STATUS%%</span>
        <span>Level %%LEVEL%%: %%LEVELNAME%%</span>
    </div>
    
    <script>
        function navigate(nodeId) {
            window.location.href = '/?node=' + nodeId;
        }
        function goBack() {
            window.location.href = '/?action=back';
        }
        function goUp() {
            window.location.href = '/?action=up';
        }
        function performSearch() {
            var q = document.getElementById('searchInput').value;
            if (q) window.location.href = '/?q=' + encodeURIComponent(q);
        }
        function handleSearch(e) {
            if (e.key === 'Enter') performSearch();
        }
        function fetchApi(apiName) {
            window.location.href = '/?action=fetch&api=' + apiName;
        }
    </script>
</body>
</html>"""


class ExplorerHandler(BaseHTTPRequestHandler):
    """HTTP Handler for Dimensional Explorer"""
    
    explorer: DimensionalExplorer = None
    
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if parsed.path == '/':
            self.serve_explorer(params)
        elif parsed.path == '/api/tree':
            self.serve_json(self.explorer.get_tree())
        elif parsed.path == '/api/stats':
            self.serve_json(self.explorer.stats())
        else:
            self.send_error(404)
    
    def serve_explorer(self, params):
        explorer = self.explorer
        
        # Handle actions
        action = params.get('action', [None])[0]
        if action == 'back':
            explorer.go_back()
        elif action == 'up':
            explorer.go_up()
        elif action == 'fetch':
            api_name = params.get('api', [None])[0]
            if api_name:
                explorer.fetch_api(api_name)
        
        # Handle navigation
        node_id = params.get('node', [None])[0]
        if node_id:
            explorer.navigate(node_id)
        
        # Handle search/Q&A
        query = params.get('q', [None])[0]
        search_results = None
        qa_answer = None
        
        if query:
            query = unquote(query)
            if query.endswith('?'):
                qa_answer = explorer.ask(query)
            else:
                search_results = explorer.search(query)
        
        # Build page
        current = explorer.get_current()
        children = explorer.get_children()
        breadcrumb = explorer.get_breadcrumb()
        stats = explorer.stats()
        
        # Breadcrumb HTML
        bc_parts = []
        for i, node in enumerate(breadcrumb):
            if i == len(breadcrumb) - 1:
                bc_parts.append(f"<span>{node.icon} {node.name}</span>")
            else:
                bc_parts.append(f'<a href="/?node={node.id}">{node.icon} {node.name}</a>')
                bc_parts.append('<span>›</span>')
        breadcrumb_html = ' '.join(bc_parts)
        
        # Tree HTML
        def render_tree(tree_data, depth=0):
            html = []
            for item in tree_data:
                selected = 'selected' if item['id'] == (current.id if current else '') else ''
                html.append(f'''
                    <a href="/?node={item["id"]}" class="tree-node {selected}" style="text-decoration:none;color:inherit;">
                        <span class="tree-node-icon">{item["icon"]}</span>
                        <span>{item["name"]}</span>
                    </a>
                ''')
                if item.get('children'):
                    html.append(f'<div class="tree-children">{render_tree(item["children"], depth+1)}</div>')
            return ''.join(html)
        
        tree_html = render_tree(explorer.get_tree())
        
        # Content HTML
        if search_results:
            # Show search results
            cards = []
            for node, score in search_results:
                cards.append(f'''
                    <a href="/?node={node.id}" class="item-card" style="text-decoration:none;color:inherit;">
                        <div class="item-card-icon">{node.icon}</div>
                        <div class="item-card-name">{node.name}</div>
                        <div class="item-card-meta">Match: {score:.0%} | {node.path}</div>
                    </a>
                ''')
            content_html = f'''
                <div class="qa-section">
                    <strong>Search results for: "{query}"</strong>
                </div>
                <div class="item-grid">{''.join(cards)}</div>
            '''
        elif qa_answer:
            # Show Q&A answer
            content_html = f'''
                <div class="qa-section">
                    <strong>Question: {query}</strong>
                    <div class="qa-answer">{qa_answer.replace(chr(10), "<br>")}</div>
                </div>
            '''
        elif children:
            # Show children
            cards = []
            for child in sorted(children, key=lambda x: (x.node_type != 'folder', x.name)):
                meta = child.node_type
                if child.size:
                    meta += f' | {child.size:,} bytes'
                cards.append(f'''
                    <a href="/?node={child.id}" class="item-card" style="text-decoration:none;color:inherit;display:block;">
                        <div class="item-card-icon">{child.icon}</div>
                        <div class="item-card-name">{child.name}</div>
                        <div class="item-card-meta">{meta}</div>
                    </a>
                ''')
            content_html = f'<div class="item-grid">{"".join(cards)}</div>'
        else:
            content_html = '''
                <div class="empty-state">
                    <div class="empty-state-icon">📂</div>
                    <div>This location is empty</div>
                </div>
            '''
        
        # Preview HTML
        if current:
            preview_data = explorer.get_preview(current.id)
            preview_html = f'''
                <div class="preview-header">
                    <span class="preview-icon">{current.icon}</span>
                    <div>
                        <div class="preview-name">{current.name}</div>
                        <div class="preview-type">{current.node_type}</div>
                    </div>
                </div>
                <div class="preview-section">
                    <div class="preview-section-title">Location</div>
                    <div>{current.path}</div>
                </div>
                <div class="preview-section">
                    <div class="preview-section-title">Dimensional Level</div>
                    <div>{LEVEL_ICONS.get(current.level, "")} Level {current.level}: {LEVEL_NAMES.get(current.level, "")}</div>
                </div>
            '''
            
            if preview_data.get('content'):
                preview_html += f'''
                    <div class="preview-section">
                        <div class="preview-section-title">Content Preview</div>
                        <div class="preview-content">{preview_data["content"][:500]}</div>
                    </div>
                '''
            
            if preview_data.get('can_fetch'):
                api_name = current.id.split('_')[-1]
                preview_html += f'''
                    <div class="preview-section">
                        <div class="preview-section-title">API Info</div>
                        <div>{preview_data.get("description", "")}</div>
                        <a href="/?action=fetch&api={api_name}" class="preview-btn" style="display:block;text-align:center;text-decoration:none;color:white;">🔌 Fetch Data</a>
                    </div>
                '''
            
            # Show metadata/data for cache items
            if current.node_type == 'item' and current.metadata.get('data'):
                import json as json_mod
                data_str = json_mod.dumps(current.metadata['data'], indent=2)[:1000]
                preview_html += f'''
                    <div class="preview-section">
                        <div class="preview-section-title">Fetched Data</div>
                        <div class="preview-content">{data_str}</div>
                    </div>
                '''
        else:
            preview_html = '<div class="empty-state">Select an item</div>'
        
        # Status
        level = current.level if current else 6
        status_html = f"{stats['nodes']} nodes | {stats['indexed']} indexed | {stats['total_apis']} APIs"
        
        # Assemble
        html = EXPLORER_HTML
        html = html.replace('%%BREADCRUMB%%', breadcrumb_html)
        html = html.replace('%%TREE%%', tree_html)
        html = html.replace('%%CONTENT%%', content_html)
        html = html.replace('%%PREVIEW%%', preview_html)
        html = html.replace('%%STATUS%%', status_html)
        html = html.replace('%%LEVEL%%', str(level))
        html = html.replace('%%LEVELNAME%%', LEVEL_NAMES.get(level, ''))
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


def run_explorer(explorer: DimensionalExplorer = None, host: str = '127.0.0.1', port: int = 8000):
    """Run the Dimensional Explorer web server"""
    if explorer is None:
        explorer = DimensionalExplorer()
    
    ExplorerHandler.explorer = explorer
    
    server = HTTPServer((host, port), ExplorerHandler)
    print(f"🦋 Dimensional Explorer")
    print(f"   Running at http://{host}:{port}")
    print(f"   Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nExplorer stopped")
        server.shutdown()


# =============================================================================
# DEMO
# =============================================================================

def demo():
    """Demo the Dimensional Explorer"""
    print("=" * 60)
    print("Dimensional Explorer Demo")
    print("=" * 60)
    
    explorer = DimensionalExplorer()
    
    # Show stats
    print(f"\n📊 Initial Stats: {explorer.stats()}")
    
    # Index local files
    print("\n📁 Indexing local files...")
    explorer.index_local(".", max_depth=2)
    
    # Fetch some API data
    print("\n🔌 Fetching API data...")
    explorer.fetch_api("iss_location")
    explorer.fetch_api("joke")
    
    # Test Q&A
    print("\n💬 Testing Q&A...")
    answer = explorer.ask("What is mentioned in the README?")
    print(f"Q: What is mentioned in the README?")
    print(f"A: {answer[:200]}...")
    
    # Final stats
    print(f"\n📊 Final Stats: {explorer.stats()}")
    
    print("\n✨ Demo complete!")
    print("   Run 'run_explorer()' to start web interface")


if __name__ == "__main__":
    demo()
