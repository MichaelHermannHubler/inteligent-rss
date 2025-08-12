#!/usr/bin/env python3
"""
Test script for the Intelligent RSS Consumer system

This script tests the basic functionality without requiring an LLM model.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from base_source import BaseSource, RSSItem
        print("✓ Base source classes imported successfully")
        
        from sources.generic_rss import GenericRSSSource
        print("✓ Generic RSS source imported successfully")
        
        from sources.tech_crunch import TechCrunchSource
        print("✓ TechCrunch source imported successfully")
        
        from sources.reddit import RedditSource
        print("✓ Reddit source imported successfully")
        
        from database import RSSDatabase
        print("✓ Database module imported successfully")
        
        from rss_consumer import RSSConsumer
        print("✓ RSS consumer imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_base_classes():
    """Test base class functionality"""
    print("\nTesting base classes...")
    
    try:
        from base_source import RSSItem
        from datetime import datetime
        
        # Test RSSItem creation
        item = RSSItem(
            title="Test Title",
            link="https://example.com",
            description="Test description",
            published=datetime.now(),
            content="Test content",
            source="Test Source",
            guid="test-guid-123"
        )
        
        print(f"✓ RSSItem created: {item.title}")
        print(f"✓ RSSItem source: {item.source}")
        
        return True
        
    except Exception as e:
        print(f"✗ Base class test failed: {e}")
        return False


def test_database():
    """Test database functionality"""
    print("\nTesting database...")
    
    try:
        from database import RSSDatabase
        
        # Create test database
        test_db_path = "test_rss_data.db"
        db = RSSDatabase(test_db_path)
        print("✓ Database created successfully")
        
        # Test database info
        info = db.get_database_info()
        print(f"✓ Database info retrieved: {info['rss_items_count']} items")
        
        # Clean up test database
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
            print("✓ Test database cleaned up")
        
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False


def test_sources():
    """Test RSS source functionality"""
    print("\nTesting RSS sources...")
    
    try:
        from sources.generic_rss import GenericRSSSource
        from sources.tech_crunch import TechCrunchSource
        from sources.reddit import RedditSource
        
        # Test source creation
        generic_source = GenericRSSSource("Test Feed", "https://example.com/feed")
        print(f"✓ Generic source created: {generic_source}")
        
        tech_source = TechCrunchSource()
        print(f"✓ TechCrunch source created: {tech_source}")
        
        reddit_source = RedditSource("python")
        print(f"✓ Reddit source created: {reddit_source}")
        
        # Test source info
        info = generic_source.get_source_info()
        print(f"✓ Source info retrieved: {info['name']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Sources test failed: {e}")
        return False


def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        # Test if config file exists and can be imported
        config_path = Path(__file__).parent / "config.py"
        if config_path.exists():
            print("✓ Configuration file exists")
            
            # Try to import config
            sys.path.insert(0, str(Path(__file__).parent))
            import config
            
            # Test config functions
            enabled_sources = config.get_enabled_sources()
            print(f"✓ Configuration loaded: {len(enabled_sources)} enabled sources")
            
            return True
        else:
            print("✗ Configuration file not found")
            return False
            
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("Intelligent RSS Consumer - System Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_base_classes,
        test_database,
        test_sources,
        test_configuration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"✗ Test {test.__name__} failed")
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Download a local LLM model (e.g., from Hugging Face)")
        print("2. Set the LLM_MODEL_PATH environment variable")
        print("3. Run: python main.py --help")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 