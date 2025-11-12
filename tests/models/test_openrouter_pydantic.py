#!/usr/bin/env python3
"""
Test OpenRouter with PydanticAI exactly as used in the swarm.
"""

import asyncio
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from config.settings import get_settings

async def test_pydantic_openrouter():
    """Test PydanticAI with OpenRouter exactly as in swarm."""
    
    print("Testing PydanticAI + OpenRouter integration...")
    
    try:
        # Load settings exactly as in swarm
        settings = get_settings()
        api_key = settings.apis.openrouter_key
        
        print(f"API key loaded: {bool(api_key)}")
        print(f"API key length: {len(api_key) if api_key else 0}")
        print(f"API key prefix: {api_key[:15] if api_key else 'None'}...")
        
        if not api_key or api_key == "your_openrouter_api_key_here" or api_key.strip() == "":
            print("ERROR: No valid API key found")
            return False
        
        # Create model exactly as in swarm
        model = OpenAIModel(
            "mistralai/mistral-7b-instruct:free",
            provider=OpenRouterProvider(api_key=api_key),
        )
        
        print(f"Model created: {model}")
        
        # Create agent
        agent = Agent(model)
        print(f"Agent created: {agent}")
        
        # Test simple prompt
        prompt = "Hello, respond with 'API working!' in exactly those words."
        
        print(f"Running prompt: {prompt}")
        
        response = await agent.run(prompt)
        
        print(f"Response type: {type(response)}")
        print(f"Response output: {response.output}")
        print(f"Response data: {response.data}")
        
        print("SUCCESS: PydanticAI + OpenRouter working!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_pydantic_openrouter())