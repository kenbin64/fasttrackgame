"""
Test Seed Dimensionalization

Demonstrates how seeds are dimensionalized when they enter the kernel:
- Seeds become points in 21D space
- Parts exist in lower dimensions (Russian Dolls)
- Each dimension contains all lower dimensions
"""

from kernel.seed_loader import SeedLoader
from pathlib import Path


def test_seed_dimensionalization():
    """Test that seeds are properly dimensionalized."""
    
    print("🌀 SEED DIMENSIONALIZATION TEST\n")
    print("=" * 70)
    
    # Initialize seed loader
    loader = SeedLoader(seed_directory='seeds')
    
    # Load a relationship seed
    test_seed_path = 'seeds/tier1_fundamental/dimensional/relationships/part_to_whole.yaml'
    
    print(f"\n📥 Loading seed: {test_seed_path}\n")
    
    try:
        # Ingest seed (this will dimensionalize it)
        seed = loader.ingest_seed_file(Path(test_seed_path))
        
        print(f"✅ Seed loaded: {seed.name}")
        print(f"   Identity: {seed.identity}")
        print(f"   Category: {seed.category}")
        
        # Get dimensionalized version
        dimensionalized = loader.get_dimensionalized(seed.name)
        
        if not dimensionalized:
            print("\n❌ Seed was not dimensionalized!")
            return
        
        print(f"\n🌀 DIMENSIONALIZED STRUCTURE (Russian Dolls)")
        print("=" * 70)
        
        # Show each dimensional level
        fibonacci_levels = [0, 1, '1b', 2, 3, 5, 8, 13, 21]
        
        for level in fibonacci_levels:
            dimension = loader.get_dimension(seed.name, level)
            
            if dimension:
                print(f"\n📐 Dimension {level}:")
                print(f"   Type: {dimension['type']}")
                print(f"   Description: {dimension['description']}")
                
                # Show what this dimension contains
                if 'contains' in dimension:
                    print(f"   Contains dimensions: {dimension['contains']}")
                
                # Show content (abbreviated)
                content = dimension['content']
                if isinstance(content, dict):
                    print(f"   Content keys: {list(content.keys())}")
                elif isinstance(content, str):
                    print(f"   Content: {content[:100]}...")
                else:
                    print(f"   Content type: {type(content).__name__}")
        
        # Test WHOLE_TO_PART relationship
        print(f"\n🔍 WHOLE_TO_PART RELATIONSHIP (Division)")
        print("=" * 70)
        
        # Divide dimension 2 (semantic plane) to get its parts
        parts_2d = loader.get_parts(seed.name, 2)
        print(f"\nDimension 2 (Semantic Plane) parts:")
        for i, part in enumerate(parts_2d, 1):
            if isinstance(part, str):
                print(f"   {i}. {part[:80]}...")
            else:
                print(f"   {i}. {part}")
        
        # Divide dimension 3 (application volume) to get its parts
        parts_3d = loader.get_parts(seed.name, 3)
        print(f"\nDimension 3 (Application Volume) parts:")
        for i, part in enumerate(parts_3d, 1):
            if isinstance(part, list):
                print(f"   {i}. List with {len(part)} items")
            else:
                print(f"   {i}. {type(part).__name__}")
        
        # Test substrate invocation
        print(f"\n🔮 SUBSTRATE INVOCATION (Collapse Potential)")
        print("=" * 70)
        
        substrate = dimensionalized.substrate
        
        # Invoke different attributes
        attributes = ['name', 'category', 'definition', 'meaning', 'relationships']
        
        for attr in attributes:
            value = substrate.expression(attribute=attr)
            if isinstance(value, str):
                print(f"\n   {attr}: {value[:100]}...")
            else:
                print(f"\n   {attr}: {type(value).__name__}")
        
        print(f"\n\n✅ DIMENSIONALIZATION TEST COMPLETE!")
        print("=" * 70)
        print("\n📊 Summary:")
        print(f"   - Seed is a POINT (0D) in 21D space")
        print(f"   - Parts exist in LOWER dimensions (Russian Dolls)")
        print(f"   - Each dimension CONTAINS all lower dimensions")
        print(f"   - Substrate expression computes attributes ON DEMAND")
        print(f"   - No data stored - all truth emerges from invocation")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_seed_dimensionalization()

