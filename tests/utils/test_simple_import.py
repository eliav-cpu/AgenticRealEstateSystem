#!/usr/bin/env python3
"""
Simple import test.
"""

try:
    print("Testing imports...")
    
    print("1. Importing config...")
    from config.settings import get_settings
    settings = get_settings()
    print(f"   - Settings loaded: {settings.app_name}")
    
    print("2. Testing API key...")
    api_key = settings.apis.openrouter_key
    print(f"   - API key exists: {bool(api_key)}")
    print(f"   - API key length: {len(api_key) if api_key else 0}")
    
    print("3. Importing PydanticAI...")
    from pydantic_ai import Agent
    from pydantic_ai.models.openai import OpenAIModel
    from pydantic_ai.providers.openrouter import OpenRouterProvider
    print("   - PydanticAI imports successful")
    
    print("4. Creating model...")
    model = OpenAIModel(
        "mistralai/mistral-7b-instruct:free",
        provider=OpenRouterProvider(api_key=api_key),
    )
    print(f"   - Model created: {type(model)}")
    
    print("5. Creating agent...")
    agent = Agent(model)
    print(f"   - Agent created: {type(agent)}")
    
    print("SUCCESS: All imports and basic setup working!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()