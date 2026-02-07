#!/usr/bin/env python3
"""
DimensionOS Installation Test
Verifies that all dependencies and core components are working
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import flask
        print("  ✓ Flask")
    except ImportError as e:
        print(f"  ✗ Flask: {e}")
        return False
    
    try:
        import flask_cors
        print("  ✓ Flask-CORS")
    except ImportError as e:
        print(f"  ✗ Flask-CORS: {e}")
        return False
    
    try:
        import authlib
        print("  ✓ Authlib")
    except ImportError as e:
        print(f"  ✗ Authlib: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("  ✓ python-dotenv")
    except ImportError as e:
        print(f"  ✗ python-dotenv: {e}")
        return False
    
    return True


def test_core_access():
    """Test that core_v2 can be accessed"""
    print("\nTesting ButterflyFx core_v2 access...")
    
    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    try:
        from core_v2 import ButterflyFx
        print("  ✓ core_v2.ButterflyFx imported")
        
        # Try to instantiate
        fx = ButterflyFx()
        print("  ✓ ButterflyFx instantiated")
        
        # Try a simple operation
        result = fx.process(42)
        print(f"  ✓ fx.process(42) = {hex(result.truth)}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_dimension_os_core():
    """Test DimensionOS core module"""
    print("\nTesting DimensionOS core...")
    
    try:
        from dimension_os_core import DimensionOSCore
        print("  ✓ DimensionOSCore imported")
        
        # Try to instantiate
        dos = DimensionOSCore()
        print("  ✓ DimensionOSCore instantiated")
        
        # Try ingestion
        result = dos.ingest({'name': 'test', 'value': 123}, user_id='test_user')
        print(f"  ✓ Ingestion successful: {result['name']}")
        
        # Try query
        query_result = dos.query("Show test", user_id='test_user')
        print(f"  ✓ Query successful: {query_result.get('success', False)}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_templates():
    """Test that template files exist"""
    print("\nTesting template files...")
    
    templates_dir = Path(__file__).parent / 'templates'
    required_templates = ['base.html', 'index.html', 'dashboard.html']
    
    all_exist = True
    for template in required_templates:
        template_path = templates_dir / template
        if template_path.exists():
            print(f"  ✓ {template}")
        else:
            print(f"  ✗ {template} not found")
            all_exist = False
    
    return all_exist


def test_static_files():
    """Test that static files exist"""
    print("\nTesting static files...")
    
    static_dir = Path(__file__).parent / 'static'
    required_files = [
        'css/style.css',
        'js/main.js',
        'js/dashboard.js'
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = static_dir / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} not found")
            all_exist = False
    
    return all_exist


def test_env_file():
    """Test that .env file exists"""
    print("\nTesting environment configuration...")
    
    env_path = Path(__file__).parent / '.env'
    env_example_path = Path(__file__).parent / '.env.example'
    
    if env_path.exists():
        print("  ✓ .env file exists")
        return True
    elif env_example_path.exists():
        print("  ⚠ .env file not found, but .env.example exists")
        print("    Run: cp .env.example .env")
        return False
    else:
        print("  ✗ Neither .env nor .env.example found")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("DimensionOS Installation Test")
    print("=" * 70)
    
    results = {
        'Imports': test_imports(),
        'Core Access': test_core_access(),
        'DimensionOS Core': test_dimension_os_core(),
        'Templates': test_templates(),
        'Static Files': test_static_files(),
        'Environment': test_env_file()
    }
    
    print("\n" + "=" * 70)
    print("Test Results:")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:20} {status}")
    
    all_passed = all(results.values())
    
    print("=" * 70)
    if all_passed:
        print("✓ All tests passed! DimensionOS is ready to run.")
        print("\nNext steps:")
        print("  1. Configure .env file with OAuth credentials")
        print("  2. Run: python run.py")
        print("  3. Visit: https://localhost:5000")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Create .env file: cp .env.example .env")
        print("  - Ensure you're in the dimensionOS directory")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())

