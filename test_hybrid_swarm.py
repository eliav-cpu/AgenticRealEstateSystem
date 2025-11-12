#!/usr/bin/env python3
"""
Test script for the Hybrid LangGraph-Swarm + PydanticAI implementation.

This script tests the integration of:
- LangGraph-Swarm for agent coordination and handoffs
- PydanticAI for individual agent logic with all benefits
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the hybrid orchestrator
from app.orchestration.swarm_hybrid import get_hybrid_swarm_orchestrator
from app.utils.logging import get_logger

logger = get_logger("test_hybrid_swarm")


async def test_basic_functionality():
    """Test basic functionality of the hybrid swarm."""
    logger.info("🧪 Testing Hybrid LangGraph-Swarm + PydanticAI Basic Functionality")
    
    try:
        # Get the hybrid orchestrator
        orchestrator = get_hybrid_swarm_orchestrator()
        logger.info("✅ Hybrid orchestrator initialized successfully")
        
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
        
        logger.info("🚀 Processing test message through hybrid swarm...")
        
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


async def test_agent_handoffs():
    """Test agent handoffs in the hybrid swarm."""
    logger.info("🔄 Testing Agent Handoffs")
    
    try:
        orchestrator = get_hybrid_swarm_orchestrator()
        
        # Test property analysis request (should route to property agent)
        property_message = {
            "messages": [{"role": "user", "content": "Tell me more about this property's features and pricing"}],
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
        
        logger.info("🏠 Testing property analysis routing...")
        result = await orchestrator.process_message(property_message, config)
        
        logger.info("✅ Property analysis test completed")
        
        # Test scheduling request
        scheduling_message = {
            "messages": [{"role": "user", "content": "I'd like to schedule a visit for tomorrow at 2 PM"}],
            "session_id": "test_session_003",
            "context": {
                "data_mode": "mock"
            }
        }
        
        config = {"configurable": {"thread_id": "test_thread_003"}}
        
        logger.info("📅 Testing scheduling routing...")
        result = await orchestrator.process_message(scheduling_message, config)
        
        logger.info("✅ Scheduling test completed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Handoff test failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False


async def test_memory_persistence():
    """Test memory persistence across multiple interactions."""
    logger.info("🧠 Testing Memory Persistence")
    
    try:
        orchestrator = get_hybrid_swarm_orchestrator()
        thread_id = "test_memory_thread"
        
        # First interaction
        message1 = {
            "messages": [{"role": "user", "content": "I'm looking for apartments in Miami"}],
            "session_id": "test_session_memory",
            "context": {"data_mode": "mock"}
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        
        logger.info("📝 First interaction...")
        result1 = await orchestrator.process_message(message1, config)
        
        # Second interaction (should remember context)
        message2 = {
            "messages": [{"role": "user", "content": "What about 3-bedroom options?"}],
            "session_id": "test_session_memory",
            "context": {"data_mode": "mock"}
        }
        
        logger.info("📝 Second interaction (should remember context)...")
        result2 = await orchestrator.process_message(message2, config)
        
        logger.info("✅ Memory persistence test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Memory test failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False


async def test_individual_agents():
    """Test individual agents directly (bypassing LangGraph-Swarm)."""
    logger.info("🔧 Testing Individual PydanticAI Agents")
    
    try:
        # Test search agent directly
        from app.agents.hybrid_search import HybridSearchAgent
        from langchain_openai import ChatOpenAI
        from config.settings import get_settings
        
        settings = get_settings()
        openrouter_key = settings.apis.openrouter_key
        
        if openrouter_key and openrouter_key != "your_openrouter_api_key_here":
            model = ChatOpenAI(
                model="mistralai/mistral-7b-instruct:free",
                api_key=openrouter_key,
                base_url="https://openrouter.ai/api/v1",
                temperature=0.1
            )
            
            search_agent = HybridSearchAgent(model)
            
            logger.info("🔍 Testing search agent directly...")
            search_result = await search_agent.direct_execute("Find me a 2-bedroom apartment under $3000")
            
            logger.info(f"✅ Search agent direct test: {search_result.properties_found} properties found")
            
            # Test property agent directly
            from app.agents.hybrid_property import HybridPropertyAgent
            
            property_agent = HybridPropertyAgent(model)
            
            logger.info("🏠 Testing property agent directly...")
            property_result = await property_agent.direct_execute("Analyze this property's investment potential")
            
            logger.info(f"✅ Property agent direct test: {len(property_result.property_highlights)} highlights generated")
            
            return True
        else:
            logger.warning("⚠️ No OpenRouter API key configured, skipping individual agent tests")
            return True
        
    except Exception as e:
        logger.error(f"❌ Individual agent test failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False


async def main():
    """Run all tests."""
    logger.info("🚀 Starting Hybrid LangGraph-Swarm + PydanticAI Test Suite")
    logger.info("=" * 70)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Agent Handoffs", test_agent_handoffs),
        ("Memory Persistence", test_memory_persistence),
        ("Individual Agents", test_individual_agents)
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
        logger.info("🎉 All tests passed! Hybrid implementation is working correctly.")
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