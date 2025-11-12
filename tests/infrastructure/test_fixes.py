"""
Simple test script to verify the fixes work correctly.
Tests both datetime context and DuckDB integration without emojis.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_datetime_context():
    """Test datetime context generation."""
    print("Testing datetime context...")
    
    try:
        from app.utils.datetime_context import get_agent_datetime_context
        context = get_agent_datetime_context()
        
        print(f"Current date: {context['current_datetime']['date']}")
        print(f"Tomorrow: {context['relative_dates']['tomorrow']}")
        print("Datetime context: WORKING")
        return True
    except Exception as e:
        print(f"Datetime context failed: {e}")
        return False

def test_duckdb_connection():
    """Test DuckDB connection and basic operations."""
    print("Testing DuckDB connection...")
    
    try:
        from app.database.schema import PropertyDB
        
        # Test connection
        db = PropertyDB("test_properties.duckdb")
        count = db.get_property_count()
        print(f"DuckDB connection successful. Property count: {count}")
        
        # Clean up
        db.close()
        if os.path.exists("test_properties.duckdb"):
            os.remove("test_properties.duckdb")
        
        print("DuckDB integration: WORKING")
        return True
    except Exception as e:
        print(f"DuckDB integration failed: {e}")
        return False

def test_api_config():
    """Test API config without DuckDB errors."""
    print("Testing API config...")
    
    try:
        from config.api_config import RentCastAPI, APIConfig, APIMode
        
        # Test Mock mode
        config = APIConfig(mode=APIMode.MOCK)
        api = RentCastAPI(config)
        
        # Test search (should fallback to in-memory if DuckDB fails)
        properties = api.search_properties({"city": "Miami"})
        print(f"Found {len(properties)} properties")
        print("API config: WORKING")
        return True
    except Exception as e:
        print(f"API config failed: {e}")
        return False

if __name__ == "__main__":
    print("Running basic functionality tests...")
    print("=" * 50)
    
    results = []
    results.append(test_datetime_context())
    results.append(test_duckdb_connection())
    results.append(test_api_config())
    
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! The fixes are working.")
    else:
        print("Some tests failed. Check the errors above.")
    
    sys.exit(0 if passed == total else 1)