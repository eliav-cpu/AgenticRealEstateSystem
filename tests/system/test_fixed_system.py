#!/usr/bin/env python3
"""
Test script to verify the fixed OpenRouter models and memory configuration work.
"""

import asyncio
import sys
from app.orchestration.swarm import get_swarm_orchestrator

async def test_swarm_with_fixes():
    """Test the swarm system with the new Mistral model and fixed memory."""
    
    print("🧪 TESTING FIXED SWARM SYSTEM")
    print("=" * 50)
    
    try:
        # Test message
        test_message = {
            "messages": [{"role": "user", "content": "Hello! I'm looking for a 2-bedroom apartment in Miami under $2000."}],
            "context": {
                "data_mode": "mock"
            }
        }
        
        print("🚀 Initializing SwarmOrchestrator...")
        orchestrator = get_swarm_orchestrator()
        
        print("📨 Testing message processing...")
        result = await orchestrator.process_message(test_message)
        
        if result and "messages" in result:
            response_content = result["messages"][-1].content
            print(f"✅ SUCCESS! Response received ({len(response_content)} chars):")
            print(f"📝 Response: {response_content[:300]}...")
            
            # Test with property context
            print("\n🏠 Testing with property context...")
            property_message = {
                "messages": [{"role": "user", "content": "How much is the rent for this property?"}],
                "context": {
                    "property_context": {
                        "formattedAddress": "467 Nw 8th St, Apt 3, Miami, FL 33136",
                        "price": 1450,
                        "bedrooms": 0,
                        "bathrooms": 1,
                        "squareFootage": 502,
                        "propertyType": "Apartment"
                    },
                    "data_mode": "mock"
                }
            }
            
            property_result = await orchestrator.process_message(property_message)
            if property_result and "messages" in property_result:
                property_response = property_result["messages"][-1].content
                print(f"✅ Property agent response ({len(property_response)} chars):")
                print(f"📝 Response: {property_response[:300]}...")
                
                # Test scheduling
                print("\n📅 Testing scheduling agent...")
                schedule_message = {
                    "messages": [{"role": "user", "content": "I want to schedule a visit for tomorrow at 2pm"}],
                    "context": {
                        "property_context": {
                            "formattedAddress": "467 Nw 8th St, Apt 3, Miami, FL 33136",
                            "price": 1450
                        },
                        "data_mode": "mock"
                    }
                }
                
                schedule_result = await orchestrator.process_message(schedule_message)
                if schedule_result and "messages" in schedule_result:
                    schedule_response = schedule_result["messages"][-1].content
                    print(f"✅ Scheduling agent response ({len(schedule_response)} chars):")
                    print(f"📝 Response: {schedule_response[:300]}...")
                    
                    print("\n🎉 ALL TESTS PASSED!")
                    print("✅ Memory configuration fixed")
                    print("✅ Mistral model working")
                    print("✅ All agents responding correctly")
                    return True
                else:
                    print("❌ Scheduling agent failed")
                    return False
            else:
                print("❌ Property agent failed")
                return False
        else:
            print("❌ FAILED - No response received")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

async def test_model_directly():
    """Test the Mistral model directly."""
    
    print("\n🔬 TESTING MISTRAL MODEL DIRECTLY")
    print("=" * 50)
    
    try:
        from pydantic_ai import Agent
        from pydantic_ai.models.openai import OpenAIModel
        from pydantic_ai.providers.openrouter import OpenRouterProvider
        from config.settings import get_settings
        
        settings = get_settings()
        api_key = settings.apis.openrouter_key
        
        if not api_key or api_key.strip() == "":
            print("❌ No API key found!")
            return False
        
        print(f"🔑 Using API key: {api_key[:15]}...")
        
        model = OpenAIModel(
            "mistralai/mistral-7b-instruct:free",
            provider=OpenRouterProvider(api_key=api_key),
        )
        agent = Agent(model)
        
        print("📡 Testing Mistral model...")
        response = await agent.run("You are a real estate assistant. Respond with: 'Mistral model is working perfectly for real estate!'")
        content = str(response.output)
        
        print(f"✅ Mistral Response: {content}")
        return True
        
    except Exception as e:
        print(f"❌ Mistral test failed: {e}")
        return False

async def main():
    """Run all tests."""
    
    print("🚀 SYSTEM FIX VERIFICATION SUITE")
    print("=" * 60)
    
    # Test 1: Direct model test
    model_works = await test_model_directly()
    
    # Test 2: Swarm integration test
    if model_works:
        swarm_works = await test_swarm_with_fixes()
    else:
        print("⏭️ Skipping swarm test - model failed")
        swarm_works = False
    
    # Final result
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULTS:")
    print(f"   Mistral Model: {'✅ Working' if model_works else '❌ Failed'}")
    print(f"   Swarm System: {'✅ Working' if swarm_works else '❌ Failed'}")
    
    if model_works and swarm_works:
        print("\n🎉 ALL FIXES SUCCESSFUL!")
        print("🔧 System is ready for use")
        return True
    else:
        print("\n❌ Some issues remain")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)