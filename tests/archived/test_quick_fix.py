#!/usr/bin/env python3
"""
Quick test to verify the fixed implementation works correctly.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_fixed_swarm():
    """Test the fixed swarm implementation."""
    print("🧪 Testing Fixed LangGraph-Swarm Implementation")
    print("=" * 50)
    
    try:
        # Test 1: Import
        print("1. Testing import...")
        from app.orchestration.swarm_fixed import get_fixed_swarm_orchestrator
        print("   ✅ Import successful")
        
        # Test 2: Check API key
        print("2. Checking API key...")
        from config.settings import get_settings
        settings = get_settings()
        api_key = settings.apis.openrouter_key
        if api_key and api_key != "your_openrouter_api_key_here":
            print(f"   ✅ API key configured (length: {len(api_key)})")
        else:
            print("   ❌ API key not configured")
            return False
        
        # Test 3: Create orchestrator
        print("3. Creating orchestrator...")
        orchestrator = get_fixed_swarm_orchestrator()
        print(f"   ✅ Orchestrator created: {type(orchestrator)}")
        
        # Test 4: Simple message test
        print("4. Testing simple message...")
        test_message = {
            "messages": [{"role": "user", "content": "Hello, what is the rent for this property?"}],
            "session_id": "test_001",
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
        
        config = {
            "configurable": {
                "thread_id": "test_thread_001"
            }
        }
        
        print("   🚀 Processing message...")
        result = await orchestrator.process_message(test_message, config)
        
        print(f"   ✅ Processing completed: {type(result)}")
        
        # Test 5: Extract response
        print("5. Extracting response...")
        if hasattr(result, 'get') and result.get("messages"):
            messages = result["messages"]
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, 'content'):
                    response_content = last_message.content
                elif isinstance(last_message, dict) and "content" in last_message:
                    response_content = last_message["content"]
                else:
                    response_content = str(last_message)
                
                print(f"   ✅ Response extracted: {len(response_content)} characters")
                print(f"   📝 Response preview: {response_content[:100]}...")
                
                # Check if response is sensible
                if "brazil" in response_content.lower() or "property analysis function" in response_content.lower():
                    print("   ❌ WARNING: Response contains strange content!")
                    print(f"   Full response: {response_content}")
                    return False
                else:
                    print("   ✅ Response appears normal")
            else:
                print("   ❌ No messages in result")
                return False
        else:
            print("   ❌ Could not extract messages from result")
            print(f"   Result: {result}")
            return False
        
        print("\n🎉 All tests passed! Fixed implementation is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fixed_swarm())
    sys.exit(0 if success else 1)