"""
Test Primitive Seed Loader

Verify that the SeedLoader can:
1. Load all seeds from the seeds/ directory
2. Index seeds by name, category, domain, tags
3. Search for seeds
4. Build relationships between seeds
"""

from pathlib import Path
from kernel.seed_loader import SeedLoader, PrimitiveCategory

def main():
    print("=" * 80)
    print("PRIMITIVE SEED LOADER TEST")
    print("=" * 80)
    print()
    
    # Initialize loader
    seed_dir = Path("seeds")
    loader = SeedLoader(seed_dir)
    
    # Load all seeds
    print("📦 Loading seeds from:", seed_dir)
    count = loader.ingest_all()
    print(f"✅ Loaded {count} seeds")
    print()
    
    # Show statistics
    print("📊 STATISTICS")
    print("-" * 80)
    stats = loader.stats()
    print(f"Total seeds: {stats['total_seeds']}")
    print(f"Categories: {stats['categories']}")
    print(f"Domains: {stats['domains']}")
    print(f"Tags: {stats['tags']}")
    print()
    
    print("Category counts:")
    for cat, count in stats['category_counts'].items():
        print(f"  {cat}: {count}")
    print()
    
    print("Domain counts:")
    for dom, count in stats['domain_counts'].items():
        print(f"  {dom}: {count}")
    print()
    
    # Test get by name
    print("🔍 GET BY NAME")
    print("-" * 80)
    pi_seed = loader.get_by_name("PI")
    if pi_seed:
        print(f"Name: {pi_seed.name}")
        print(f"Category: {pi_seed.category.value}")
        print(f"Definition: {pi_seed.definition}")
        print(f"Usage examples: {len(pi_seed.usage)}")
        print(f"Tags: {', '.join(pi_seed.tags)}")
        if pi_seed.expression:
            print(f"Value: {pi_seed.expression()}")
    print()
    
    # Test get by category
    print("📂 GET BY CATEGORY: mathematical_constant")
    print("-" * 80)
    constants = loader.get_by_category("mathematical_constant")
    for seed in constants:
        value = seed.expression() if seed.expression else "N/A"
        print(f"  {seed.name}: {value}")
    print()
    
    # Test get by domain
    print("🌐 GET BY DOMAIN: mathematics")
    print("-" * 80)
    math_seeds = loader.get_by_domain("mathematics")
    for seed in math_seeds:
        print(f"  {seed.name} ({seed.category.value})")
    print()
    
    # Test get by tag
    print("🏷️  GET BY TAG: fundamental")
    print("-" * 80)
    fundamental = loader.get_by_tag("fundamental")
    for seed in fundamental:
        print(f"  {seed.name}: {seed.definition[:60]}...")
    print()
    
    # Test search
    print("🔎 SEARCH: 'growth'")
    print("-" * 80)
    results = loader.search("growth")
    for seed in results:
        print(f"  {seed.name}: {seed.definition[:60]}...")
    print()
    
    # Show detailed seed example
    print("📖 DETAILED SEED EXAMPLE: SEE")
    print("-" * 80)
    see_seed = loader.get_by_name("SEE")
    if see_seed:
        print(f"Name: {see_seed.name}")
        print(f"Category: {see_seed.category.value}")
        print(f"Domain: {see_seed.domain}")
        print()
        print(f"Definition:")
        print(f"  {see_seed.definition}")
        print()
        print(f"Meaning:")
        print(f"  {see_seed.meaning[:200]}...")
        print()
        print(f"Etymology:")
        print(f"  {see_seed.etymology[:100]}..." if see_seed.etymology else "  N/A")
        print()
        print(f"Usage examples ({len(see_seed.usage)}):")
        for i, usage in enumerate(see_seed.usage[:3], 1):
            print(f"  {i}. {usage}")
        print()
        print(f"Synonyms: {', '.join(see_seed.synonyms[:5])}")
        print(f"Related: {', '.join(see_seed.related[:5])}")
        print()
        print(f"Examples: {len(see_seed.examples)}")
        print(f"Counterexamples: {len(see_seed.counterexamples)}")
        print(f"Tags: {', '.join(see_seed.tags)}")
    print()
    
    # Show all loaded seeds
    print("📚 ALL LOADED SEEDS")
    print("-" * 80)
    for name in sorted(loader.loaded_seeds.keys()):
        seed = loader.loaded_seeds[name]
        print(f"  {name:15} | {seed.category.value:25} | {seed.domain}")
    print()
    
    print("=" * 80)
    print("✅ SEED LOADER TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()

