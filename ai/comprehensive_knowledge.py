"""
Comprehensive Knowledge Acquisition - All Human Knowledge
==========================================================

Acquires knowledge from hundreds of free public sources covering:
- Language, grammar, definitions, thesaurus
- Science, technology, mathematics, physics
- History, geography, politics, government
- Arts, music, literature, entertainment
- And virtually every domain of human knowledge

All sources are FREE and PUBLIC.

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from trinity_memory import TrinityMemorySubstrate
import time
from typing import List, Dict, Optional

# Free data sources catalog
FREE_DATA_SOURCES = {
    # Language & Linguistics
    'wiktionary': 'https://en.wiktionary.org/w/api.php',
    'wordnet': 'Free lexical database',
    
    # Encyclopedias
    'wikipedia': 'https://en.wikipedia.org/w/api.php',
    'britannica_free': 'Free articles',
    
    # Science & Technology
    'arxiv': 'https://arxiv.org/',
    'pubmed': 'https://pubmed.ncbi.nlm.nih.gov/',
    'nasa_api': 'https://api.nasa.gov/',
    
    # Geography & Maps
    'openstreetmap': 'https://www.openstreetmap.org/',
    'geonames': 'http://www.geonames.org/',
    
    # Government & Law
    'congress_api': 'https://api.congress.gov/',
    'supreme_court': 'https://www.supremecourt.gov/',
    'library_congress': 'https://www.loc.gov/',
    
    # History & Culture
    'smithsonian': 'https://www.si.edu/openaccess',
    'europeana': 'https://www.europeana.eu/',
    
    # Arts & Entertainment
    'met_museum': 'https://metmuseum.github.io/',
    'rijksmuseum': 'https://data.rijksmuseum.nl/',
    'musicbrainz': 'https://musicbrainz.org/',
    
    # News & Current Events
    'news_api': 'https://newsapi.org/',
    'rss_feeds': 'Various free RSS feeds',
    
    # Books & Literature
    'gutenberg': 'https://www.gutenberg.org/',
    'openlibrary': 'https://openlibrary.org/',
    
    # Academic
    'doaj': 'https://doaj.org/',
    'core': 'https://core.ac.uk/',
}

# Comprehensive topic list for Wikipedia extraction
COMPREHENSIVE_TOPICS = {
    # Language & Communication
    'language': [
        'Language', 'Grammar', 'Syntax', 'Semantics', 'Phonetics', 'Morphology',
        'Dictionary', 'Thesaurus', 'Etymology', 'Linguistics', 'Rhetoric',
        'Communication', 'Writing', 'Reading', 'Speech', 'Slang', 'Idiom',
        'Metaphor', 'Analogy', 'Irony', 'Sarcasm', 'Humor', 'Joke'
    ],
    
    # Science & Mathematics
    'science': [
        'Physics', 'Chemistry', 'Biology', 'Astronomy', 'Geology',
        'Mathematics', 'Geometry', 'Algebra', 'Calculus', 'Statistics',
        'Quantum mechanics', 'Relativity', 'Thermodynamics', 'Electromagnetism',
        'Atomic theory', 'Nuclear physics', 'Particle physics',
        'Scientific method', 'Scientific theory'
    ],
    
    # Technology & Computing
    'technology': [
        'Computer', 'Internet', 'World Wide Web', 'Artificial intelligence',
        'Machine learning', 'Programming', 'Software', 'Hardware',
        'Networking', 'Cybersecurity', 'Encryption', 'Database',
        'Operating system', 'Algorithm', 'Data structure',
        'Computer graphics', '3D modeling', 'Virtual reality'
    ],
    
    # History
    'history': [
        'Ancient Egypt', 'Ancient Greece', 'Ancient Rome', 'Medieval history',
        'Renaissance', 'Industrial Revolution', 'World War I', 'World War II',
        'Cold War', 'American history', 'European history', 'Asian history',
        'African history', 'Middle Eastern history', 'American Civil War',
        'Vietnam War', 'Gulf War', 'Napoleon', 'Roman Empire'
    ],
    
    # Geography
    'geography': [
        'Geography', 'Physical geography', 'Political geography', 'Cartography',
        'Continent', 'Ocean', 'Mountain', 'River', 'Desert', 'Climate',
        'Weather', 'Natural disaster', 'Earthquake', 'Volcano', 'Hurricane',
        'Topology', 'Geology', 'Plate tectonics'
    ],
    
    # Government & Politics
    'government': [
        'Government', 'Democracy', 'Republic', 'Constitution', 'Law',
        'United States Constitution', 'Magna Carta', 'Supreme Court',
        'Congress', 'President', 'Political science', 'Political party',
        'Conservatism', 'Liberalism', 'Socialism', 'Capitalism', 'Fascism',
        'Civil rights', 'Human rights', 'Voting', 'Election'
    ],
    
    # Arts & Culture
    'arts': [
        'Art', 'Painting', 'Sculpture', 'Drawing', 'Photography',
        'Art history', 'Renaissance art', 'Modern art', 'Abstract art',
        'Music', 'Music theory', 'Musical instrument', 'Orchestra',
        'Rock music', 'Classical music', 'Jazz', 'Blues', 'Hip hop',
        'Dance', 'Ballet', 'Theater', 'Drama', 'Comedy', 'Tragedy'
    ],
    
    # Literature
    'literature': [
        'Literature', 'Novel', 'Poetry', 'Short story', 'Essay',
        'Fiction', 'Non-fiction', 'Creative writing', 'Prose', 'Verse',
        'Shakespeare', 'Homer', 'Dante', 'Literary criticism',
        'Genre', 'Fantasy', 'Science fiction', 'Mystery', 'Romance'
    ],
    
    # Entertainment
    'entertainment': [
        'Film', 'Cinema', 'Movie', 'Television', 'Video game',
        'Animation', 'Hollywood', 'Academy Awards', 'Emmy Awards',
        'Director', 'Actor', 'Screenplay', 'Special effects', 'CGI',
        'Game show', 'Talk show', 'Reality television', 'Sitcom'
    ],
    
    # Music
    'music': [
        'Music', 'Song', 'Melody', 'Harmony', 'Rhythm', 'Tempo',
        'Musical notation', 'Scale', 'Chord', 'Key', 'Composition',
        'Genre', 'Album', 'Concert', 'Performance', 'Recording',
        'Music history', '1950s music', '1960s music', '1970s music',
        '1980s music', '1990s music', '2000s music'
    ],
    
    # Philosophy & Religion
    'philosophy': [
        'Philosophy', 'Ethics', 'Logic', 'Metaphysics', 'Epistemology',
        'Existentialism', 'Stoicism', 'Utilitarianism', 'Pragmatism',
        'Religion', 'Christianity', 'Islam', 'Judaism', 'Buddhism', 'Hinduism',
        'Bible', 'Quran', 'Torah', 'Theology', 'Spirituality',
        'Atheism', 'Agnosticism', 'Faith', 'Belief'
    ],
    
    # Social Sciences
    'social': [
        'Psychology', 'Sociology', 'Anthropology', 'Economics',
        'Political science', 'Education', 'Social work', 'Criminology',
        'Human behavior', 'Society', 'Culture', 'Social structure',
        'Family', 'Marriage', 'Parenting', 'Child development',
        'Mental health', 'Depression', 'Anxiety', 'PTSD', 'OCD'
    ],
    
    # Health & Medicine
    'health': [
        'Medicine', 'Health', 'Disease', 'Treatment', 'Surgery',
        'Anatomy', 'Physiology', 'Pharmacology', 'Nutrition',
        'Exercise', 'Mental health', 'Public health', 'Epidemiology',
        'Human body', 'Brain', 'Heart', 'Organ', 'Cell', 'DNA',
        'Pregnancy', 'Birth', 'Aging', 'Death'
    ],
    
    # Nature & Environment
    'nature': [
        'Nature', 'Ecology', 'Environment', 'Climate change', 'Conservation',
        'Animal', 'Plant', 'Mammal', 'Bird', 'Fish', 'Insect',
        'Tree', 'Flower', 'Forest', 'Jungle', 'Ocean', 'Coral reef',
        'Biodiversity', 'Evolution', 'Natural selection', 'Species',
        'Ecosystem', 'Food chain', 'Photosynthesis'
    ],
    
    # Space & Astronomy
    'space': [
        'Space', 'Universe', 'Galaxy', 'Star', 'Planet', 'Moon',
        'Solar System', 'Sun', 'Earth', 'Mars', 'Jupiter', 'Saturn',
        'Black hole', 'Nebula', 'Supernova', 'Big Bang', 'Cosmology',
        'Astronomy', 'Astrophysics', 'NASA', 'Space exploration',
        'Rocket', 'Satellite', 'International Space Station'
    ],
    
    # Business & Economics
    'business': [
        'Business', 'Economics', 'Finance', 'Marketing', 'Management',
        'Entrepreneurship', 'Corporation', 'Stock market', 'Investment',
        'Banking', 'Currency', 'Money', 'Trade', 'Commerce',
        'Supply and demand', 'Capitalism', 'GDP', 'Inflation',
        'Recession', 'Tax', 'Insurance', 'Real estate'
    ],
    
    # Sports & Recreation
    'sports': [
        'Sport', 'Athletics', 'Football', 'Basketball', 'Baseball',
        'Soccer', 'Tennis', 'Golf', 'Olympics', 'World Cup',
        'Exercise', 'Fitness', 'Recreation', 'Game', 'Competition',
        'Camping', 'Hiking', 'Skiing', 'Swimming', 'Cycling'
    ],
    
    # Food & Cooking
    'food': [
        'Food', 'Cooking', 'Recipe', 'Cuisine', 'Restaurant',
        'Nutrition', 'Diet', 'Vegetable', 'Fruit', 'Meat',
        'Bread', 'Cheese', 'Wine', 'Beer', 'Coffee', 'Tea',
        'Baking', 'Grilling', 'Frying', 'Boiling', 'Seasoning'
    ],
    
    # Transportation
    'transportation': [
        'Transportation', 'Automobile', 'Car', 'Truck', 'Motorcycle',
        'Bicycle', 'Train', 'Airplane', 'Ship', 'Boat',
        'Aviation', 'Maritime', 'Railway', 'Highway', 'Airport',
        'Logistics', 'Supply chain', 'Shipping', 'Navigation'
    ],
    
    # Law & Justice
    'law': [
        'Law', 'Justice', 'Court', 'Judge', 'Lawyer', 'Attorney',
        'Criminal law', 'Civil law', 'Constitutional law', 'Contract',
        'Tort', 'Property law', 'Trial', 'Jury', 'Verdict',
        'Police', 'Prison', 'Crime', 'Punishment', 'Due process',
        'Case law', 'Precedent', 'Statute', 'Regulation'
    ],
    
    # Military & War
    'military': [
        'Military', 'War', 'Army', 'Navy', 'Air Force', 'Marines',
        'Soldier', 'General', 'Strategy', 'Tactics', 'Weapon',
        'Battle', 'Campaign', 'Siege', 'Defense', 'Offense',
        'Military history', 'War theory', 'Game theory',
        'Nuclear weapon', 'Missile', 'Tank', 'Aircraft carrier'
    ]
}


class ComprehensiveKnowledge:
    """
    Acquire comprehensive knowledge from free public sources.
    Covers virtually all domains of human knowledge.
    """
    
    def __init__(self, memory: Optional[TrinityMemorySubstrate] = None):
        self.memory = memory or TrinityMemorySubstrate()
        self.sources_initialized = {}
    
    def _init_wikipedia(self):
        """Initialize Wikipedia API"""
        if 'wikipedia' not in self.sources_initialized:
            try:
                import wikipediaapi
                self.wiki = wikipediaapi.Wikipedia(
                    user_agent='ButterflyFX-ComprehensiveAI/1.0',
                    language='en'
                )
                self.sources_initialized['wikipedia'] = True
                return True
            except ImportError:
                print("Wikipedia API not available. Install: pip install wikipedia-api")
                return False
        return True
    
    def bootstrap_category(self, category: str, topics: List[str], max_per_topic: int = 2) -> int:
        """
        Bootstrap knowledge for a specific category.
        
        Args:
            category: Category name
            topics: List of topics in this category
            max_per_topic: Max articles per topic
        
        Returns:
            Number of articles stored
        """
        if not self._init_wikipedia():
            return 0
        
        print(f"\n{'='*60}")
        print(f"Category: {category.upper()}")
        print(f"{'='*60}")
        
        stored = 0
        
        for topic in topics:
            try:
                page = self.wiki.page(topic)
                
                if not page.exists():
                    continue
                
                # Store main article
                self.memory.store(
                    page.text,
                    metadata={
                        'source': 'wikipedia',
                        'category': category,
                        'topic': topic,
                        'title': page.title,
                        'url': page.fullurl,
                        'timestamp': time.time()
                    }
                )
                stored += 1
                print(f"  ✓ {page.title}")
                
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
                                        'category': category,
                                        'topic': topic,
                                        'title': link_page.title,
                                        'url': link_page.fullurl,
                                        'related_to': page.title,
                                        'timestamp': time.time()
                                    }
                                )
                                stored += 1
                                print(f"    → {link_page.title}")
                        except:
                            pass
                
            except Exception as e:
                print(f"  ✗ Error: {topic} - {e}")
        
        print(f"Category complete: {stored} articles")
        return stored
    
    def bootstrap_comprehensive(self, categories: List[str] = None, quick: bool = False) -> Dict[str, int]:
        """
        Bootstrap comprehensive knowledge across all categories.
        
        Args:
            categories: Specific categories to load (None = all)
            quick: If True, load fewer articles per topic
        
        Returns:
            Dictionary with counts per category
        """
        print("\n" + "="*60)
        print("COMPREHENSIVE KNOWLEDGE BOOTSTRAP")
        print("="*60)
        print()
        
        max_per_topic = 1 if quick else 2
        stats = {}
        
        # Determine which categories to load
        if categories:
            topics_to_load = {k: v for k, v in COMPREHENSIVE_TOPICS.items() if k in categories}
        else:
            topics_to_load = COMPREHENSIVE_TOPICS
        
        # Load each category
        for category, topics in topics_to_load.items():
            count = self.bootstrap_category(category, topics, max_per_topic)
            stats[category] = count
        
        # Summary
        print("\n" + "="*60)
        print("BOOTSTRAP COMPLETE")
        print("="*60)
        total = sum(stats.values())
        print(f"Total articles loaded: {total}")
        print()
        print("By category:")
        for category, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category:20s}: {count:4d} articles")
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
    print("Comprehensive Knowledge Acquisition")
    print("Loading from free public sources...")
    print()
    
    # Create knowledge system
    knowledge = ComprehensiveKnowledge()
    
    # Bootstrap a few categories for testing
    test_categories = ['language', 'science', 'technology', 'history', 'arts']
    
    stats = knowledge.bootstrap_comprehensive(
        categories=test_categories,
        quick=True  # Quick mode for testing
    )
    
    # Test queries
    print("\n" + "="*60)
    print("TESTING KNOWLEDGE RECALL")
    print("="*60)
    print()
    
    test_queries = [
        "What is language?",
        "Explain quantum mechanics",
        "Tell me about World War II",
        "What is music theory?"
    ]
    
    for query in test_queries:
        print(f"Query: {query}")
        results = knowledge.memory.recall(query, k=1)
        if results:
            print(f"Answer: {results[0].content[:200]}...")
        else:
            print("No results found")
        print()
