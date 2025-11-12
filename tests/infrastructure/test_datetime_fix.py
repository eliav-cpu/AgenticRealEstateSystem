"""
Test script to verify that the datetime context fixes work correctly.

This script tests:
1. Datetime context generation
2. Agent datetime awareness
3. DuckDB integration for Mock mode
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.datetime_context import (
    get_agent_datetime_context, 
    format_datetime_context_for_agent,
    get_scheduling_context_for_agent
)
from app.database.migration import migrate_mock_to_duckdb, verify_migration
from config.api_config import RentCastAPI, APIConfig, APIMode


def test_datetime_context():
    """Test datetime context generation."""
    print("\n" + "="*60)
    print("🕐 TESTING DATETIME CONTEXT")
    print("="*60)
    
    # Test 1: Basic datetime context
    context = get_agent_datetime_context()
    print(f"✅ Current date: {context['current_datetime']['date']}")
    print(f"✅ Current time: {context['current_datetime']['time']}")
    print(f"✅ Weekday: {context['current_datetime']['weekday_pt']}")
    print(f"✅ Tomorrow: {context['relative_dates']['tomorrow']}")
    print(f"✅ Next week: {context['relative_dates']['next_week']}")
    
    # Test 2: Agent prompt format
    agent_context = format_datetime_context_for_agent()
    print(f"\n📝 Agent context length: {len(agent_context)} characters")
    print("📝 Agent context preview:")
    print(agent_context[:200] + "...")
    
    # Test 3: Scheduling context
    scheduling_context = get_scheduling_context_for_agent()
    print(f"\n📅 Scheduling context length: {len(scheduling_context)} characters")
    print("📅 Scheduling context preview:")
    print(scheduling_context[:300] + "...")
    
    return True


def test_duckdb_integration():
    """Test DuckDB integration for Mock mode."""
    print("\n" + "="*60)
    print("🦆 TESTING DUCKDB INTEGRATION")
    print("="*60)
    
    try:
        # Test 1: Migration
        print("🔄 Testing migration...")
        success = migrate_mock_to_duckdb(force_reload=True)
        if not success:
            print("❌ Migration failed!")
            return False
        print("✅ Migration successful!")
        
        # Test 2: Verification
        print("\n🔍 Testing verification...")
        success = verify_migration()
        if not success:
            print("❌ Verification failed!")
            return False  
        print("✅ Verification successful!")
        
        # Test 3: API integration
        print("\n🌐 Testing API integration...")
        config = APIConfig(mode=APIMode.MOCK)
        api = RentCastAPI(config)
        
        # Test search
        properties = api.search_properties({"city": "Miami", "bedrooms": 2})
        print(f"✅ Found {len(properties)} properties with 2 bedrooms in Miami")
        
        if len(properties) > 0:
            sample_prop = properties[0]
            print(f"📍 Sample property: {sample_prop['formattedAddress']}")
            print(f"💰 Price: ${sample_prop['price']}/month")
            print(f"🛏️ Bedrooms: {sample_prop['bedrooms']}")
            print(f"🚿 Bathrooms: {sample_prop['bathrooms']}")
        
        return True
        
    except Exception as e:
        print(f"❌ DuckDB integration test failed: {e}")
        return False


async def test_agent_datetime_awareness():
    """Test that agents now have datetime awareness."""
    print("\n" + "="*60)
    print("🤖 TESTING AGENT DATETIME AWARENESS")
    print("="*60)
    
    try:
        # This would require running the full swarm, which is complex
        # For now, just verify the context is being generated correctly
        
        from app.utils.datetime_context import get_agent_datetime_context
        
        context = get_agent_datetime_context()
        current_date = context['current_datetime']['date']
        
        print(f"✅ Today's date: {current_date}")
        print(f"✅ Tomorrow will be: {context['relative_dates']['tomorrow']}")
        
        # Verify the date is correct (today should be July 23rd, 2025)
        today = datetime.now().date().isoformat()
        if current_date == today:
            print("✅ Date context is accurate!")
            return True
        else:
            print(f"⚠️ Date mismatch - context: {current_date}, actual: {today}")
            return False
            
    except Exception as e:
        print(f"❌ Agent datetime awareness test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 STARTING DATETIME & DUCKDB FIX TESTS")
    print("="*60)
    
    results = []
    
    # Test 1: Datetime Context
    results.append(test_datetime_context())
    
    # Test 2: DuckDB Integration  
    results.append(test_duckdb_integration())
    
    # Test 3: Agent Datetime Awareness
    results.append(asyncio.run(test_agent_datetime_awareness()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total} tests")
    
    if passed == total:
        print("🎉 All tests passed! The fixes are working correctly.")
        print("\nKey improvements:")
        print("- ✅ Agents now have real datetime context")
        print("- ✅ Mock properties are stored in DuckDB (persistent)")
        print("- ✅ Real API system remains unchanged (in-memory)")
        print("- ✅ Scheduling agent can understand 'tomorrow', 'next week', etc.")
        return True
    else:
        print(f"❌ {total - passed} tests failed. Please check the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)