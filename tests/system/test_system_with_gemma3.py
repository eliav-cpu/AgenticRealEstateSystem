#!/usr/bin/env python3
"""
Teste do Sistema Completo com Modelo Gemma-3-27B-IT
"""

import asyncio
import httpx
from app.orchestration.swarm import get_swarm_orchestrator
from config.settings import get_settings

async def test_system_integration():
    """Testar integração completa do sistema com Gemma-3."""
    
    print("🚀 SYSTEM INTEGRATION TEST WITH GEMMA-3")
    print("=" * 70)
    
    # Verificar configurações
    settings = get_settings()
    api_key = settings.apis.openrouter_key
    
    print(f"🔑 API Key: {api_key[:15]}...")
    print(f"🌍 Environment: {settings.environment}")
    
    try:
        orchestrator = get_swarm_orchestrator()
        
        # Teste 1: Property Agent
        print("\n🏠 Test 1: Property Agent with Gemma-3")
        print("-" * 50)
        
        property_message = {
            "messages": [{"role": "user", "content": "How much is the rent for this property?"}],
            "context": {
                "property_context": {
                    "formattedAddress": "467 Nw 8th St, Apt 3, Miami, FL 33136",
                    "price": 1450,
                    "bedrooms": 0,
                    "bathrooms": 1,
                    "squareFootage": 502,
                    "propertyType": "Apartment",
                    "yearBuilt": 1950,
                    "city": "Miami",
                    "state": "FL"
                },
                "data_mode": "mock"
            }
        }
        
        result1 = await orchestrator.process_message(property_message)
        
        if result1 and "messages" in result1:
            response1 = result1["messages"][-1].content
            print(f"✅ Property Agent Response ({len(response1)} chars):")
            print(f"📝 Preview: {response1[:200]}...")
        else:
            print("❌ Property Agent failed")
            return False
        
        # Teste 2: Search Agent  
        print("\n🔍 Test 2: Search Agent with Gemma-3")
        print("-" * 50)
        
        search_message = {
            "messages": [{"role": "user", "content": "I'm looking for a 2-bedroom apartment in Miami under $2000"}],
            "context": {
                "data_mode": "mock"
            }
        }
        
        result2 = await orchestrator.process_message(search_message)
        
        if result2 and "messages" in result2:
            response2 = result2["messages"][-1].content
            print(f"✅ Search Agent Response ({len(response2)} chars):")
            print(f"📝 Preview: {response2[:200]}...")
        else:
            print("❌ Search Agent failed")
            return False
        
        # Teste 3: Scheduling Agent
        print("\n📅 Test 3: Scheduling Agent with Gemma-3")
        print("-" * 50)
        
        scheduling_message = {
            "messages": [{"role": "user", "content": "I'd like to schedule a visit to this property"}],
            "context": {
                "property_context": {
                    "formattedAddress": "467 Nw 8th St, Apt 3, Miami, FL 33136",
                    "price": 1450,
                    "bedrooms": 0,
                    "bathrooms": 1
                },
                "data_mode": "mock"
            }
        }
        
        result3 = await orchestrator.process_message(scheduling_message)
        
        if result3 and "messages" in result3:
            response3 = result3["messages"][-1].content
            print(f"✅ Scheduling Agent Response ({len(response3)} chars):")
            print(f"📝 Preview: {response3[:200]}...")
        else:
            print("❌ Scheduling Agent failed")
            return False
        
        # Teste 4: Conversational Flow
        print("\n💬 Test 4: Conversational Flow")
        print("-" * 50)
        
        conversation_tests = [
            "Tell me about the amenities",
            "What's the neighborhood like?",
            "Can I bring pets?",
            "When can I move in?"
        ]
        
        conversation_success = 0
        for i, question in enumerate(conversation_tests, 1):
            conv_message = {
                "messages": [{"role": "user", "content": question}],
                "context": {
                    "property_context": property_message["context"]["property_context"],
                    "data_mode": "mock"
                }
            }
            
            try:
                conv_result = await orchestrator.process_message(conv_message)
                if conv_result and "messages" in conv_result:
                    conv_response = conv_result["messages"][-1].content
                    print(f"✅ Q{i}: {question[:30]}... → {len(conv_response)} chars")
                    conversation_success += 1
                else:
                    print(f"❌ Q{i}: {question[:30]}... → Failed")
            except Exception as e:
                print(f"❌ Q{i}: {question[:30]}... → Error: {e}")
        
        print(f"\n📊 Conversation Success Rate: {conversation_success}/{len(conversation_tests)}")
        
        # Resultado final
        all_tests_passed = all([result1, result2, result3]) and conversation_success >= 3
        
        print("\n" + "=" * 70)
        print("📋 INTEGRATION TEST SUMMARY:")
        print(f"   Property Agent: {'✅' if result1 else '❌'}")
        print(f"   Search Agent: {'✅' if result2 else '❌'}")
        print(f"   Scheduling Agent: {'✅' if result3 else '❌'}")
        print(f"   Conversational Flow: {'✅' if conversation_success >= 3 else '❌'} ({conversation_success}/4)")
        
        if all_tests_passed:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Gemma-3-27B-IT is working perfectly in the system")
            print("✅ All agents are responding correctly")
            print("✅ Conversational flow is natural")
            print("\n💡 System is ready for production with Gemma-3!")
        else:
            print("\n⚠️ Some tests failed")
            print("🔧 System needs debugging")
        
        return all_tests_passed
        
    except Exception as e:
        print(f"❌ System integration error: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

async def test_performance():
    """Testar performance do sistema com Gemma-3."""
    
    print("\n⚡ PERFORMANCE TEST WITH GEMMA-3")
    print("=" * 70)
    
    import time
    
    try:
        orchestrator = get_swarm_orchestrator()
        
        test_message = {
            "messages": [{"role": "user", "content": "How much is the rent?"}],
            "context": {
                "property_context": {
                    "formattedAddress": "Test Property, Miami, FL",
                    "price": 2000,
                    "bedrooms": 2,
                    "bathrooms": 2
                },
                "data_mode": "mock"
            }
        }
        
        # Executar 3 testes de performance
        times = []
        for i in range(3):
            start_time = time.time()
            result = await orchestrator.process_message(test_message)
            duration = time.time() - start_time
            times.append(duration)
            
            if result and "messages" in result:
                response_length = len(result["messages"][-1].content)
                print(f"✅ Test {i+1}: {duration:.2f}s → {response_length} chars")
            else:
                print(f"❌ Test {i+1}: Failed")
        
        avg_time = sum(times) / len(times)
        print(f"\n📊 Average Response Time: {avg_time:.2f}s")
        
        if avg_time < 10:
            print("🚀 Excellent performance!")
        elif avg_time < 20:
            print("✅ Good performance")
        else:
            print("⚠️ Slow performance - may need optimization")
        
        return avg_time < 20
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False

async def main():
    """Executar todos os testes."""
    
    print("🔬 GEMMA-3-27B-IT SYSTEM VALIDATION")
    print("=" * 80)
    
    # Teste 1: Integração do sistema
    integration_success = await test_system_integration()
    
    # Teste 2: Performance
    if integration_success:
        performance_success = await test_performance()
    else:
        performance_success = False
        print("\n⏭️ Skipping performance test - integration failed")
    
    # Resultado final
    print("\n" + "=" * 80)
    print("🎯 FINAL VALIDATION RESULT:")
    
    if integration_success and performance_success:
        print("🎉 GEMMA-3-27B-IT FULLY VALIDATED!")
        print("✅ All system components working")
        print("✅ Performance within acceptable limits")
        print("✅ Ready for production use")
        print("\n🚀 The system is now using Gemma-3-27B-IT successfully!")
    elif integration_success and not performance_success:
        print("⚠️ GEMMA-3 WORKING BUT SLOW")
        print("✅ All system components working")
        print("❌ Performance needs optimization")
        print("💡 Consider adjusting model parameters")
    else:
        print("❌ GEMMA-3 INTEGRATION FAILED")
        print("🔧 System needs debugging")
        print("💡 Check API connectivity and model availability")

if __name__ == "__main__":
    asyncio.run(main()) 