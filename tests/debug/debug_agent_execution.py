#!/usr/bin/env python3
"""
Debug script para testar execução dos agentes PydanticAI
"""

import asyncio
from config.settings import get_settings
from app.utils.logging import get_logger

async def test_property_agent():
    """Teste direto do property agent"""
    print("=== TESTING PROPERTY AGENT ===")
    
    settings = get_settings()
    logger = get_logger("debug")
    
    print(f"1. OpenRouter key loaded: {bool(settings.apis.openrouter_key)}")
    print(f"2. Key length: {len(settings.apis.openrouter_key)}")
    
    try:
        from pydantic_ai.models.openai import OpenAIModel
        from pydantic_ai.providers.openrouter import OpenRouterProvider
        from pydantic_ai import Agent
        
        print("3. PydanticAI imports successful")
        
        # Configurar modelo que funciona
        api_key = settings.apis.openrouter_key
        model = OpenAIModel(
            "openai/gpt-4o-mini",  # Modelo que funciona
            provider=OpenRouterProvider(api_key=api_key),
        )
        print(f"4. Model configured: openai/gpt-4o-mini")
        
        # Criar agente
        agent = Agent(model)
        print("5. Agent created successfully")
        
        # Testar execução
        prompt = "You are Emma, a helpful real estate agent. Say hello and introduce yourself briefly."
        print("6. Testing agent execution...")
        
        response = await agent.run(prompt)
        print(f"7. Agent response: {response.data}")
        print("8. ✅ SUCCESS - Agent executed successfully!")
        
    except ImportError as e:
        print(f"3. ❌ Import error: {e}")
    except Exception as e:
        print(f"4. ❌ Execution error: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")

async def test_swarm_node():
    """Teste do nó do swarm"""
    print("\n=== TESTING SWARM NODE ===")
    
    try:
        from app.orchestration.swarm import property_agent_node
        
        # Criar estado de teste
        state = {
            "messages": [{"role": "user", "content": "Hello Emma, how are you?"}],
            "context": {
                "property_context": {
                    "formattedAddress": "3590 Coral Way, Apt 502, Miami, FL 33145",
                    "price": 3700,
                    "bedrooms": 3,
                    "bathrooms": 2,
                    "squareFootage": 1168
                }
            }
        }
        
        print("1. Testing property_agent_node...")
        result = await property_agent_node(state)
        print(f"2. Node result type: {type(result)}")
        if result.get("messages"):
            message = result["messages"][0]
            print(f"3. Response: {message.content[:200]}...")
        print("4. ✅ SUCCESS - Node executed successfully!")
        
    except Exception as e:
        print(f"1. ❌ Node execution error: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_property_agent())
    asyncio.run(test_swarm_node()) 