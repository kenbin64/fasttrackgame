"""
Free Data Acquisition - No Data Farms Required
===============================================

Acquires knowledge from free public sources:
- Wikipedia API (comprehensive knowledge)
- RSS feeds (current events)
- arXiv (research papers)
- Reddit (discussions)
- Common Crawl (web archive)

All sources are free and require no API keys (except Reddit).

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from trinity_memory import TrinityMemorySubstrate
import time
import json
import hashlib
from typing import List, Dict, Optional
from datetime import datetime


class FreeDataAcquisition:
    """
    Acquire knowledge from free public sources.
    No data farms. No paid APIs. Just public knowledge.
    """
    
    def __init__(self, memory: Optional[TrinityMemorySubstrate] = None):
        self.memory = memory or TrinityMemorySubstrate()
        self.sources_initialized = {}
    
    def _init_wikipedia(self):
        """Initialize Wikipedia API (lazy loading)"""
        if 'wikipedia' not in self.sources_initialized:
            try:
                import wikipediaapi
                self.wiki = wikipediaapi.Wikipedia(
                    user_agent='ButterflyFX-DimensionalAI/1.0',
                    language='en'
                )
                self.sources_initialized['wikipedia'] = True
                return True
            except ImportError:
                print("Wikipedia API not available. Install: pip install wikipedia-api")
                return False
        return True
    
    def _init_feedparser(self):
        """Initialize RSS feed parser (lazy loading)"""
        if 'feedparser' not in self.sources_initialized:
            try:
                import feedparser
                self.feedparser = feedparser
                self.sources_initialized['feedparser'] = True
                return True
            except ImportError:
                print("Feedparser not available. Install: pip install feedparser")
                return False
        return True
    
    def _init_arxiv(self):
        """Initialize arXiv API (lazy loading)"""
        if 'arxiv' not in self.sources_initialized:
            try:
                import arxiv
                self.arxiv = arxiv
                self.sources_initialized['arxiv'] = True
                return True
            except ImportError:
                print("arXiv API not available. Install: pip install arxiv")
                return False
        return True
    
    def bootstrap_wikipedia(self, topics: List[str], max_per_topic: int = 5) -> int:
        """
        Bootstrap knowledge from Wikipedia.
        
        Args:
            topics: List of topics to fetch
            max_per_topic: Max related pages per topic
        
        Returns:
            Number of articles stored
        """
        if not self._init_wikipedia():
            return 0
        
        stored = 0
        
        for topic in topics:
            print(f"Fetching Wikipedia: {topic}")
            
            try:
                page = self.wiki.page(topic)
                
                if not page.exists():
                    print(f"  Page not found: {topic}")
                    continue
                
                # Store main article
                memory_id = self.memory.store(
                    page.text,
                    metadata={
                        'source': 'wikipedia',
                        'topic': topic,
                        'title': page.title,
                        'url': page.fullurl,
                        'timestamp': time.time()
                    }
                )
                stored += 1
                print(f"  Stored: {page.title}")
                
                # Store related pages
                if max_per_topic > 1:
                    links = list(page.links.keys())[:max_per_topic - 1]
                    for link_title in links:
                        try:
                            link_page = self.wiki.page(link_title)
                            if link_page.exists():
                                self.memory.store(
                                    link_page.text,
                                    metadata={
                                        'source': 'wikipedia',
                                        'topic': topic,
                                        'title': link_page.title,
                                        'url': link_page.fullurl,
                                        'related_to': page.title,
                                        'timestamp': time.time()
                                    }
                                )
                                stored += 1
                                print(f"    Related: {link_page.title}")
                        except Exception as e:
                            print(f"    Error fetching {link_title}: {e}")
                
            except Exception as e:
                print(f"  Error fetching {topic}: {e}")
        
        return stored
    
    def fetch_rss_feeds(self, feed_urls: List[str], max_entries: int = 10) -> int:
        """
        Fetch news and articles from RSS feeds.
        
        Args:
            feed_urls: List of RSS feed URLs
            max_entries: Max entries per feed
        
        Returns:
            Number of entries stored
        """
        if not self._init_feedparser():
            return 0
        
        stored = 0
        
        for feed_url in feed_urls:
            print(f"Fetching RSS: {feed_url}")
            
            try:
                feed = self.feedparser.parse(feed_url)
                
                for entry in feed.entries[:max_entries]:
                    # Get content
                    content = entry.get('summary', '') or entry.get('description', '')
                    if not content:
                        continue
                    
                    # Store entry
                    self.memory.store(
                        f"{entry.get('title', 'Untitled')}\n\n{content}",
                        metadata={
                            'source': 'rss',
                            'feed_url': feed_url,
                            'title': entry.get('title', ''),
                            'link': entry.get('link', ''),
                            'published': entry.get('published', ''),
                            'timestamp': time.time()
                        }
                    )
                    stored += 1
                    print(f"  Stored: {entry.get('title', 'Untitled')[:60]}")
                
            except Exception as e:
                print(f"  Error fetching {feed_url}: {e}")
        
        return stored
    
    def fetch_arxiv_papers(self, query: str, max_results: int = 20) -> int:
        """
        Fetch research papers from arXiv.
        
        Args:
            query: Search query
            max_results: Max papers to fetch
        
        Returns:
            Number of papers stored
        """
        if not self._init_arxiv():
            return 0
        
        print(f"Fetching arXiv papers: {query}")
        stored = 0
        
        try:
            search = self.arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=self.arxiv.SortCriterion.Relevance
            )
            
            for result in search.results():
                # Store paper
                content = f"{result.title}\n\nAuthors: {', '.join([a.name for a in result.authors])}\n\n{result.summary}"
                
                self.memory.store(
                    content,
                    metadata={
                        'source': 'arxiv',
                        'query': query,
                        'title': result.title,
                        'authors': [a.name for a in result.authors],
                        'pdf_url': result.pdf_url,
                        'published': str(result.published),
                        'timestamp': time.time()
                    }
                )
                stored += 1
                print(f"  Stored: {result.title[:60]}")
        
        except Exception as e:
            print(f"  Error fetching arXiv: {e}")
        
        return stored
    
    def bootstrap_ai_knowledge(self) -> Dict[str, int]:
        """
        Bootstrap comprehensive AI knowledge from free sources.
        
        Returns:
            Dictionary with counts per source
        """
        print("=" * 60)
        print("Bootstrapping AI Knowledge from Free Sources")
        print("=" * 60)
        print()
        
        stats = {}
        
        # 1. Wikipedia - Core AI concepts
        print("Phase 1: Wikipedia - Core Concepts")
        print("-" * 60)
        topics = [
            'Artificial Intelligence',
            'Machine Learning',
            'Deep Learning',
            'Natural Language Processing',
            'Computer Vision',
            'Neural Network',
            'Reinforcement Learning',
            'Dimensional Analysis',
            'Manifold',
            'Fibonacci Sequence',
            'Golden Ratio',
            'Pythagorean Theorem'
        ]
        stats['wikipedia'] = self.bootstrap_wikipedia(topics, max_per_topic=3)
        print()
        
        # 2. RSS Feeds - Current AI news
        print("Phase 2: RSS Feeds - Current News")
        print("-" * 60)
        feeds = [
            'https://news.ycombinator.com/rss',
            'https://www.reddit.com/r/MachineLearning/.rss',
            'https://www.reddit.com/r/artificial/.rss',
        ]
        stats['rss'] = self.fetch_rss_feeds(feeds, max_entries=5)
        print()
        
        # 3. arXiv - Research papers
        print("Phase 3: arXiv - Research Papers")
        print("-" * 60)
        queries = [
            'artificial intelligence',
            'machine learning',
            'neural networks'
        ]
        stats['arxiv'] = sum(
            self.fetch_arxiv_papers(query, max_results=5)
            for query in queries
        )
        print()
        
        # Summary
        print("=" * 60)
        print("Bootstrap Complete!")
        print("=" * 60)
        total = sum(stats.values())
        print(f"Total knowledge acquired: {total} items")
        for source, count in stats.items():
            print(f"  {source}: {count} items")
        print()
        
        # Memory stats
        mem_stats = self.memory.get_stats()
        print(f"Memory system:")
        print(f"  Total memories: {mem_stats['total_memories']}")
        print(f"  Fibonacci layers: {mem_stats['fibonacci_layers']}")
        print(f"  Average importance: {mem_stats['avg_importance']:.2f}")
        print()
        
        return stats


# Standalone execution
if __name__ == "__main__":
    print("Free Data Acquisition - Independent AI")
    print()
    
    # Create acquisition system
    acquisition = FreeDataAcquisition()
    
    # Bootstrap AI knowledge
    stats = acquisition.bootstrap_ai_knowledge()
    
    # Test recall
    print("=" * 60)
    print("Testing Knowledge Recall")
    print("=" * 60)
    print()
    
    queries = [
        "What is artificial intelligence?",
        "Explain machine learning",
        "What is the golden ratio?"
    ]
    
    for query in queries:
        print(f"Query: {query}")
        results = acquisition.memory.recall(query, k=3)
        if results:
            print(f"  Found {len(results)} relevant memories")
            print(f"  Top result: {results[0].content[:100]}...")
        else:
            print("  No results found")
        print()
