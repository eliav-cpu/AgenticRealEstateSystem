#!/usr/bin/env python3
"""
Teste do modelo Google Gemma-3-27B-IT do OpenRouter
Comparação com o modelo Llama Maverick
"""

import asyncio
import httpx
from config.settings import get_settings
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

async def test_openrouter_model(model_name: str, test_name: str):
    """Testar um modelo específico do OpenRouter."""
    
    print(f"\n🧪 Testing {test_name}")
    print("=" * 60)
    
    settings = get_settings()
    api_key = settings.apis.openrouter_key
    
    if not api_key or api_key.strip() == "":
        print("❌ No API key found!")
        return False, ""
    
    print(f"🔑 Using API key: {api_key[:15]}...")
    print(f"🤖 Testing model: {model_name}")
    
    try:
        # Teste 1: Chamada HTTP direta
        print("\n📡 Test 1: Direct HTTP call...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": "Hello! Respond with exactly: 'Model working correctly!'"}],
                    "temperature": 0.1,
                    "max_tokens": 50
                },
                timeout=30.0
            )
            
            print(f"📊 HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"✅ HTTP Response: {content}")
                http_success = True
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"❌ Response: {response.text}")
                return False, ""
        
        # Teste 2: PydanticAI
        print("\n🤖 Test 2: PydanticAI integration...")
        model = OpenAIModel(
            model_name,
            provider=OpenRouterProvider(api_key=api_key),
        )
        agent = Agent(model)
        
        response = await agent.run("Say 'PydanticAI working with this model!' and nothing else.")
        pydantic_content = str(response.output)
        print(f"✅ PydanticAI Response: {pydantic_content}")
        
        # Teste 3: Real Estate Agent Test
        print("\n🏠 Test 3: Real Estate Agent simulation...")
        
        property_context = """
PROPERTY DETAILS:
• Address: 467 Nw 8th St, Apt 3, Miami, FL 33136
• Price: $1,450/month
• Bedrooms: 0 (Studio)
• Bathrooms: 1
• Square Footage: 502 sq ft
• Property Type: Apartment
• Year Built: 1950
• City: Miami, FL
"""
        
        real_estate_prompt = f"""You are Emma, a professional real estate property expert. You provide clear, objective, and helpful information about properties.

{property_context}

User's Question: "How much is the rent for this property?"

INSTRUCTIONS:
1. Answer the user's question directly using the property details above
2. Reference the specific property address
3. Be professional but friendly (2-3 sentences)
4. Use appropriate emojis
5. End with a helpful follow-up question

Respond as Emma:"""

        real_estate_response = await agent.run(real_estate_prompt)
        real_estate_content = str(real_estate_response.output)
        print(f"✅ Real Estate Response ({len(real_estate_content)} chars):")
        print(f"📝 Content: {real_estate_content}")
        
        # Teste 4: Complex reasoning
        print("\n🧠 Test 4: Complex reasoning test...")
        
        complex_prompt = """You are a real estate expert. A client asks: "I need a property with these requirements: under $2000/month, at least 1 bedroom, pet-friendly, and close to public transport in Miami. Can you analyze if this property meets my needs?"

Property: 467 Nw 8th St, Apt 3, Miami, FL 33136
- Rent: $1,450/month
- Bedrooms: 0 (Studio)
- Pet Policy: No pets allowed
- Location: Downtown Miami, near metro stations

Analyze each requirement and give a clear recommendation."""

        complex_response = await agent.run(complex_prompt)
        complex_content = str(complex_response.output)
        print(f"✅ Complex Response ({len(complex_content)} chars):")
        print(f"📝 Analysis: {complex_content[:200]}...")
        
        return True, {
            "http_response": content,
            "pydantic_response": pydantic_content,
            "real_estate_response": real_estate_content,
            "complex_response": complex_content
        }
        
    except Exception as e:
        print(f"❌ Error testing {model_name}: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False, str(e)

async def compare_models():
    """Comparar os dois modelos lado a lado."""
    
    print("🔄 OPENROUTER MODEL COMPARISON")
    print("=" * 80)
    
    # Testar Llama Maverick
    maverick_success, maverick_responses = await test_openrouter_model(
        "meta-llama/llama-4-maverick:free",
        "Llama-4 Maverick (Current)"
    )
    
    # Testar Gemma-3
    gemma_success, gemma_responses = await test_openrouter_model(
        "google/gemma-3-27b-it:free",
        "Google Gemma-3-27B-IT (New)"
    ) 

        # Testar Gemma-3
    kimi_success, kimi_responses = await test_openrouter_model(
        "moonshotai/kimi-k2:free",
        "Kimi-K2 (New)"
    )
    
    # Comparação final
    print("\n" + "=" * 80)
    print("📋 COMPARISON SUMMARY:")
    print(f"   Llama-4 Maverick: {'✅ Working' if maverick_success else '❌ Failed'}")
    print(f"   Gemma-3-27B-IT: {'✅ Working' if gemma_success else '❌ Failed'}")
    
    if gemma_success and maverick_success and kimi_success:
        print("\n🎉 Both models are working!")
        print("💡 Gemma-3-27B-IT can replace Llama Maverick")
        
        # Comparar qualidade das respostas
        if isinstance(gemma_responses, dict) and isinstance(maverick_responses, dict) and isinstance(kimi_responses, dict):
            print("\n📊 Response Quality Comparison:")
            
            gemma_real_estate = gemma_responses.get("real_estate_response", "")
            maverick_real_estate = maverick_responses.get("real_estate_response", "")
            kimi_real_estate = kimi_responses.get("real_estate_response", "")
            
            print(f"   Gemma-3 Real Estate Response: {len(gemma_real_estate)} chars")
            print(f"   Maverick Real Estate Response: {len(maverick_real_estate)} chars")
            print(f"   Kimi-K2 Real Estate Response: {len(kimi_real_estate)} chars")
            
            if len(gemma_real_estate) > len(maverick_real_estate):
                print("   🏆 Gemma-3 provides more detailed responses")
            elif len(maverick_real_estate) > len(gemma_real_estate):
                print("   🏆 Maverick provides more detailed responses")
            elif len(kimi_real_estate) > len(gemma_real_estate):
                print("   🏆 Kimi-K2 provides more detailed responses")
            else:
                print("   ⚖️ Both models provide similar response length")
    
    elif gemma_success and not maverick_success and not kimi_success:
        print("\n🎯 Gemma-3-27B-IT is working while Maverick failed!")
        print("💡 Recommend switching to Gemma-3-27B-IT")
    
    elif maverick_success and not gemma_success and not kimi_success:
        print("\n⚠️ Maverick is working but Gemma-3-27B-IT failed")
        print("💡 Keep using Maverick for now")
    
    elif kimi_success and not gemma_success and not maverick_success:
        print("\n🎯 Kimi-K2 is working while Gemma-3-27B-IT and Maverick failed!")
        print("💡 Recommend switching to Kimi-K2")
    
    else:
        print("\n❌ Both models failed - API issues")
    
    return gemma_success, maverick_success, kimi_success

async def test_gemma_in_swarm():
    """Testar Gemma-3 integrado no sistema Swarm."""
    
    print("\n🔄 Testing Gemma-3 in Swarm System")
    print("=" * 60)
    
    try:
        # Importar e testar o swarm com Gemma-3
        from app.orchestration.swarm import get_swarm_orchestrator
        
        # Simular mensagem do usuário
        test_message = {
            "messages": [{"role": "user", "content": "Hello, how much is the rent for this property?"}],
            "context": {
                "property_context": {
                    "formattedAddress": "467 Nw 8th St, Apt 3, Miami, FL 33136",
                    "price": 1450,
                    "bedrooms": 0,
                    "bathrooms": 1,
                    "squareFootage": 502,
                    "propertyType": "Apartment",
                    "yearBuilt": 1950
                },
                "data_mode": "mock"
            }
        }
        
        orchestrator = get_swarm_orchestrator()
        result = await orchestrator.process_message(test_message)
        
        if result and "messages" in result:
            response_content = result["messages"][-1].content
            print(f"✅ Swarm Integration Test Successful!")
            print(f"📝 Response ({len(response_content)} chars): {response_content[:200]}...")
            return True
        else:
            print("❌ Swarm integration failed - no response")
            return False
            
    except Exception as e:
        print(f"❌ Swarm integration error: {e}")
        return False

async def main():
    """Executar todos os testes."""
    
    print("🚀 GEMMA-3-27B-IT MODEL TEST SUITE")
    print("=" * 80)
    
    # Teste 1: Comparação de modelos
    gemma_works, maverick_works, kimi_works = await compare_models()
    
    # Teste 2: Integração no Swarm (se Gemma funcionar)
    if gemma_works:
        swarm_works = await test_gemma_in_swarm()
    else:
        swarm_works = False
        print("\n⏭️ Skipping Swarm test - Gemma-3 not available")
    
    # Resultado final
    print("\n" + "=" * 80)
    print("🎯 FINAL RECOMMENDATION:")
    
    if gemma_works and not maverick_works:
        print("✅ SWITCH TO GEMMA-3-27B-IT")
        print("   • Gemma-3 is working while Maverick failed")
        print("   • Model provides good real estate responses")
        print("   • Can replace Llama Maverick immediately")
        print("\n🔧 Next step: Update SwarmOrchestrator to use Gemma-3-27B-IT")
    elif gemma_works and maverick_works:
        print("✅ BOTH MODELS WORKING - RECOMMEND GEMMA-3")
        print("   • Both models are functional")
        print("   • Gemma-3 may have better performance")
        print("   • Safe to switch to Gemma-3-27B-IT")
    elif not gemma_works and maverick_works:
        print("❌ KEEP USING MAVERICK")
        print("   • Gemma-3-27B-IT not available")
        print("   • Maverick still working")
    elif gemma_works and kimi_works:
        print("✅ BOTH MODELS WORKING - RECOMMEND GEMMA-3")
        print("   • Both models are functional")
        print("   • Gemma-3 may have better performance")
        print("   • Safe to switch to Gemma-3-27B-IT")
    elif not gemma_works and kimi_works:
        print("❌ KEEP USING KIMI-K2")
        print("   • Gemma-3-27B-IT not available")
        print("   • Kimi-K2 still working")
    else:
        print("❌ BOTH MODELS FAILED")
        print("   • API issues detected")
        print("   • Use Ollama fallback")

if __name__ == "__main__":
    asyncio.run(main()) 