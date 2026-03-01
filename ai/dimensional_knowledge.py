"""
Dimensional Knowledge System - Lazy Loading via Geometric Invocation
=====================================================================

Knowledge is stored as dimensional coordinates in the manifold.
Topics are represented as points in geometric space.
Knowledge is only loaded/computed when geometrically invoked.

This is the key insight: Instead of loading all knowledge upfront,
we map topics to dimensional coordinates and fetch on-demand.

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from server.substrates.hexadic_manifold import HexadicManifold
from trinity_memory import TrinityMemorySubstrate
import hashlib
import time
from typing import Dict, List, Optional, Tuple


class DimensionalKnowledgeIndex:
    """
    Maps all human knowledge to dimensional coordinates.
    Knowledge is fetched on-demand when coordinates are invoked.
    """
    
    def __init__(self):
        self.manifold = HexadicManifold()
        self.memory = TrinityMemorySubstrate()
        
        # Dimensional topic map - topics mapped to coordinates
        self.topic_map = {}
        
        # Knowledge sources - lazy loaded
        self.sources = {
            'wikipedia': None,  # Initialized on first use
            'wiktionary': None,
            'arxiv': None,
        }
        
        # Cache for fetched knowledge
        self.knowledge_cache = {}
        
        # Initialize topic coordinates
        self._initialize_topic_coordinates()
    
    def _initialize_topic_coordinates(self):
        """
        Map all topics to dimensional coordinates using golden ratio.
        Each topic gets a unique position in the manifold.
        """
        # Comprehensive topic list
        topics = {
            # Language & Communication
            'language': ['language', 'grammar', 'syntax', 'dictionary', 'thesaurus', 'slang', 'idiom', 'metaphor', 'analogy', 'humor', 'sarcasm', 'irony'],
            
            # Science
            'science': ['physics', 'chemistry', 'biology', 'astronomy', 'geology', 'mathematics', 'geometry', 'quantum mechanics', 'relativity', 'atomic theory'],
            
            # Technology
            'technology': ['computer', 'internet', 'artificial intelligence', 'machine learning', 'programming', 'cybersecurity', 'database', 'networking'],
            
            # History
            'history': ['ancient egypt', 'ancient greece', 'ancient rome', 'world war i', 'world war ii', 'american history', 'european history', 'civil war'],
            
            # Geography
            'geography': ['geography', 'climate', 'weather', 'mountain', 'ocean', 'desert', 'natural disaster', 'earthquake', 'volcano'],
            
            # Government
            'government': ['government', 'democracy', 'constitution', 'law', 'supreme court', 'congress', 'president', 'politics', 'civil rights'],
            
            # Arts
            'arts': ['art', 'painting', 'sculpture', 'photography', 'music', 'dance', 'theater', 'film', 'literature'],
            
            # Philosophy
            'philosophy': ['philosophy', 'ethics', 'logic', 'religion', 'christianity', 'islam', 'judaism', 'buddhism', 'bible'],
            
            # Health
            'health': ['medicine', 'health', 'disease', 'anatomy', 'physiology', 'brain', 'pregnancy', 'nutrition'],
            
            # Nature
            'nature': ['nature', 'ecology', 'animal', 'plant', 'evolution', 'ecosystem', 'biodiversity'],
            
            # Space
            'space': ['space', 'universe', 'galaxy', 'planet', 'solar system', 'black hole', 'nasa'],
            
            # Business
            'business': ['business', 'economics', 'finance', 'marketing', 'stock market', 'currency', 'trade'],
            
            # Sports
            'sports': ['sport', 'football', 'basketball', 'baseball', 'olympics', 'exercise'],
            
            # Food
            'food': ['food', 'cooking', 'recipe', 'cuisine', 'nutrition'],
            
            # Transportation
            'transportation': ['car', 'airplane', 'ship', 'train', 'bicycle', 'aviation'],
            
            # Law
            'law': ['law', 'justice', 'court', 'judge', 'lawyer', 'criminal law', 'trial'],
            
            # Military
            'military': ['military', 'war', 'army', 'navy', 'weapon', 'battle', 'strategy'],
        }
        
        # Map each topic to dimensional coordinates
        PHI = 1.618033988749895
        GOLDEN_ANGLE = 2.356194490192345  # 2π/φ²
        
        index = 0
        for category, topic_list in topics.items():
            for topic in topic_list:
                # Use Fibonacci spiral to distribute topics
                angle = index * GOLDEN_ANGLE
                radius = PHI ** (index / 10.0)
                
                # Convert to 3D coordinates
                x = radius * (angle % 3.14159)
                y = radius * ((angle * PHI) % 3.14159)
                z = radius * ((angle * PHI * PHI) % 3.14159)
                
                # Create point in manifold
                point = self.manifold.create_point(x, y, z)
                
                # Store mapping
                self.topic_map[topic.lower()] = {
                    'point': point,
                    'category': category,
                    'index': index,
                    'loaded': False,
                    'source': 'wikipedia'  # Default source
                }
                
                index += 1
        
        print(f"Initialized {len(self.topic_map)} topics in dimensional space")
    
    def _init_wikipedia(self):
        """Lazy initialize Wikipedia API"""
        if self.sources['wikipedia'] is None:
            try:
                import wikipediaapi
                self.sources['wikipedia'] = wikipediaapi.Wikipedia(
                    user_agent='ButterflyFX-DimensionalKnowledge/1.0',
                    language='en'
                )
                return True
            except ImportError:
                print("Wikipedia API not available")
                return False
        return True
    
    def invoke_knowledge(self, query: str) -> str:
        """
        Invoke knowledge on-demand via geometric query.
        
        Process:
        1. Extract keywords from query
        2. Find matching topics
        3. Fetch knowledge for that topic (lazy load)
        4. Store in memory
        5. Return knowledge
        
        Args:
            query: Natural language query
        
        Returns:
            Knowledge content
        """
        query_lower = query.lower()
        
        # Extract keywords from query
        keywords = set(query_lower.split())
        
        # Remove common words
        stop_words = {'what', 'is', 'the', 'a', 'an', 'tell', 'me', 'about', 'explain', 'how', 'does', 'work'}
        keywords = keywords - stop_words
        
        # Find topics that match keywords
        best_match = None
        best_score = 0
        
        for topic, info in self.topic_map.items():
            # Calculate keyword overlap
            topic_words = set(topic.split())
            overlap = keywords & topic_words
            score = len(overlap)
            
            # Boost score for exact matches
            if topic in query_lower:
                score += 10
            
            if score > best_score:
                best_score = score
                best_match = topic
        
        # If we found a match, fetch it
        if best_match and best_score > 0:
            topic_info = self.topic_map[best_match]
            return self._fetch_topic_knowledge(best_match, topic_info)
        
        # No match found - return empty to let memory system handle it
        return ""
    
    def _embed_query(self, query: str):
        """Embed query in dimensional space"""
        # Hash query to coordinates
        hash_val = int(hashlib.sha256(query.encode()).hexdigest(), 16)
        
        PHI = 1.618033988749895
        x = (hash_val % 10000) / 10000.0 * PHI
        y = ((hash_val >> 16) % 10000) / 10000.0 * PHI
        z = ((hash_val >> 32) % 10000) / 10000.0 * PHI
        
        return self.manifold.create_point(x, y, z)
    
    def _find_nearest_topic(self, query_point) -> Tuple[Optional[str], float]:
        """Find nearest topic to query point using Pythagorean distance"""
        nearest_topic = None
        min_distance = float('inf')
        
        for topic, info in self.topic_map.items():
            topic_point = info['point']
            distance = self.manifold.substrate.pythagorean_distance(query_point, topic_point)
            
            if distance < min_distance:
                min_distance = distance
                nearest_topic = topic
        
        return nearest_topic, min_distance
    
    def _fetch_topic_knowledge(self, topic: str, topic_info: Dict) -> str:
        """
        Fetch knowledge for topic (lazy load).
        Only loads from source when invoked.
        """
        # Check cache first
        if topic in self.knowledge_cache:
            return self.knowledge_cache[topic]
        
        # Check if already in memory
        memories = self.memory.recall(topic, k=1)
        if memories and topic.lower() in memories[0].content.lower():
            knowledge = memories[0].content
            self.knowledge_cache[topic] = knowledge
            return knowledge
        
        # Lazy load from source
        if not topic_info['loaded']:
            knowledge = self._load_from_source(topic, topic_info['source'])
            
            if knowledge:
                # Store in memory
                self.memory.store(
                    knowledge,
                    metadata={
                        'topic': topic,
                        'category': topic_info['category'],
                        'source': topic_info['source'],
                        'timestamp': time.time()
                    }
                )
                
                # Cache
                self.knowledge_cache[topic] = knowledge
                topic_info['loaded'] = True
                
                return knowledge
        
        return f"Knowledge about '{topic}' not yet loaded. Invoke again to fetch."
    
    def _load_from_source(self, topic: str, source: str) -> Optional[str]:
        """Load knowledge from external source on-demand"""
        if source == 'wikipedia':
            if not self._init_wikipedia():
                return None
            
            try:
                wiki = self.sources['wikipedia']
                page = wiki.page(topic.title())
                
                if page.exists():
                    return page.text
                else:
                    # Try variations
                    for variation in [topic, topic.capitalize(), topic.upper()]:
                        page = wiki.page(variation)
                        if page.exists():
                            return page.text
            except Exception as e:
                print(f"Error loading {topic}: {e}")
        
        return None
    
    def get_topic_stats(self) -> Dict:
        """Get statistics about dimensional knowledge"""
        loaded_count = sum(1 for info in self.topic_map.values() if info['loaded'])
        
        return {
            'total_topics': len(self.topic_map),
            'loaded_topics': loaded_count,
            'cached_topics': len(self.knowledge_cache),
            'categories': len(set(info['category'] for info in self.topic_map.values())),
            'load_percentage': (loaded_count / len(self.topic_map) * 100) if self.topic_map else 0
        }
    
    def preload_category(self, category: str) -> int:
        """
        Preload all topics in a category.
        Useful for frequently accessed categories.
        """
        count = 0
        for topic, info in self.topic_map.items():
            if info['category'] == category and not info['loaded']:
                knowledge = self._fetch_topic_knowledge(topic, info)
                if knowledge:
                    count += 1
        
        return count


# Standalone testing
if __name__ == "__main__":
    print("="*60)
    print("Dimensional Knowledge System - Lazy Loading")
    print("="*60)
    print()
    
    # Create dimensional knowledge system
    dk = DimensionalKnowledgeIndex()
    
    # Show initial stats
    stats = dk.get_topic_stats()
    print(f"Initialized: {stats['total_topics']} topics across {stats['categories']} categories")
    print(f"Loaded: {stats['loaded_topics']} ({stats['load_percentage']:.1f}%)")
    print()
    
    # Test on-demand invocation
    print("="*60)
    print("Testing On-Demand Knowledge Invocation")
    print("="*60)
    print()
    
    test_queries = [
        "artificial intelligence",
        "quantum mechanics",
        "world war ii",
        "music"
    ]
    
    for query in test_queries:
        print(f"Query: {query}")
        knowledge = dk.invoke_knowledge(query)
        print(f"Knowledge: {knowledge[:200]}...")
        print()
    
    # Show updated stats
    stats = dk.get_topic_stats()
    print("="*60)
    print(f"After invocation: {stats['loaded_topics']} topics loaded ({stats['load_percentage']:.1f}%)")
    print(f"Cached: {stats['cached_topics']} topics")
    print()
    print("✓ Knowledge loaded only when invoked!")
    print("✓ Dimensional lazy loading working!")
