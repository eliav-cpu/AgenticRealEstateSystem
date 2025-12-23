#!/usr/bin/env python3
"""
Test script for the Fixed LangGraph-Swarm implementation.

This script tests the fixed implementation that resolves tool validation issues.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the fixed orchestrator
from app.orchestration.swarm_fixed import get_fixed_swarm_orchestrator
from app.utils.logging import get_logger

logger = get_logger("test_fixed_swarm")


async def test_basic_functionality():
    """Test basic functionality of the fixed swarm."""
    logger.info("🧪 Testing Fixed LangGraph-Swarm Basic Functionality")
    
    try:
        # Get the fixed orchestrator
        orchestrator = get_fixed_swarm_orchestrator()
        logger.info("✅ Fixed orchestrator initialized successfully")
        
        # Create test message
        test_message = {
            "messages": [{"role": "user", "content": "I'm looking for a 2-bedroom apartment in Miami"}],
            "session_id": "test_session_001",
            "context": {
                "data_mode": "mock",
                "source": "test_script"
            }
        }
        
        # Create config with thread_id for memory
        config = {
            "configurable": {
                "thread_id": "test_thread_001"
            }
        }
        
        logger.info("🚀 Processing test message through fixed swarm...")
        
        # Process the message
        result = await orchestrator.process_message(test_message, config)
        
        logger.info(f"✅ Test completed successfully!")
        logger.info(f"📊 Result type: {type(result)}")
        logger.info(f"📝 Result keys: {list(result.keys()) if hasattr(result, 'keys') else 'No keys method'}")
        
        # Try to extract response
        if hasattr(result, 'get') and result.get("messages"):
            messages = result["messages"]
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, 'content'):
                    logger.info(f"🎯 Response content: {last_message.content[:200]}...")
                elif isinstance(last_message, dict) and "content" in last_message:
                    logger.info(f"🎯 Response content: {last_message['content'][:200]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False


async def test_property_analysis():
    """Test property analysis functionality."""
    logger.info("🏠 Testing Property Analysis")
    
    try:
        orchestrator = get_fixed_swarm_orchestrator()
        
        # Test property analysis request
        property_message = {
            "messages": [{"role": "user", "content": "Tell me about this property's features and pricing"}],
            "session_id": "test_session_002",
            "context": {
                "data_mode": "mock",
                "property_context": {
                    "formattedAddress": "123 Test Street, Miami, FL",
                    "price": 2500,
                    "bedrooms": 2,
                    "bathrooms": 2
                }
            }
        }
        
        config = {"configurable": {"thread_id": "test_thread_002"}}
        
        logger.info("🏠 Testing property analysis...")
        result = await orchestrator.process_message(property_message, config)
        
        logger.info("✅ Property analysis test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Property analysis test failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False


async def test_scheduling():
    """Test scheduling functionality."""
    logger.info("📅 Testing Scheduling")
    
    try:
        orchestrator = get_fixed_swarm_orchestrator()
        
        # Test scheduling request
        scheduling_message = {
            "messages": [{"role": "user", "content": "I'd like to schedule a visit for tomorrow at 2 PM"}],
            "session_id": "test_session_003",
            "context": {
                "data_mode": "mock"
            }
        }
        
        config = {"configurable": {"thread_id": "test_thread_003"}}
        
        logger.info("📅 Testing scheduling...")
        result = await orchestrator.process_message(scheduling_message, config)
        
        logger.info("✅ Scheduling test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Scheduling test failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False


async def main():
    """Run all tests."""
    logger.info("🚀 Starting Fixed LangGraph-Swarm Test Suite")
    logger.info("=" * 70)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Property Analysis", test_property_analysis),
        ("Scheduling", test_scheduling)
    ]
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running {test_name} Test...")
        try:
            result = await test_func()
            test_results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{status}: {test_name}")
        except Exception as e:
            test_results.append((test_name, False))
            logger.error(f"❌ FAILED: {test_name} - {e}")
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 70)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Fixed implementation is working correctly.")
        return True
    else:
        logger.error(f"⚠️ {total - passed} test(s) failed. Check logs for details.")
        return False


if __name__ == "__main__":
    # Run the test suite
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Test suite crashed: {e}")
        sys.exit(1)