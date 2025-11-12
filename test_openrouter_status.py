#!/usr/bin/env python3
"""
Quick test to verify OpenRouter API is working properly
"""

import asyncio
import os
from dotenv import load_dotenv
from config.settings import get_settings
from app.orchestration.swarm import create_pydantic_agent

async def test_openrouter_api():
    """Test if OpenRouter API is working"""
    load_dotenv()
    
    settings = get_settings()
    api_key = settings.apis.openrouter_key
    
    print(f"API Key Status:")
    print(f"  - Exists: {bool(api_key)}")
    print(f"  - Length: {len(api_key) if api_key else 0}")
    print(f"  - Format: {api_key[:15] if api_key else 'None'}...")
    print(f"  - Valid format: {api_key.startswith('sk-or-v1-') if api_key else False}")
    
    if not api_key or api_key == "your_openrouter_api_key_here":
        print("ERROR: No valid OpenRouter API key found")
        return False
    
    try:
        print("\nTesting PydanticAI agent creation...")
        agent = await create_pydantic_agent("test_agent", "mistralai/mistral-7b-instruct:free")
        print("SUCCESS: Agent created successfully")
        
        print("\nTesting simple query...")
        result = await agent.run("Hello, please respond with exactly: 'OpenRouter is working correctly'")
        response = str(result.output)
        
        print(f"SUCCESS: Response received ({len(response)} chars)")
        print(f"Response: {response}")
        
        if "OpenRouter" in response or len(response) > 10:
            print("SUCCESS: OpenRouter API is working correctly!")
            return True
        else:
            print("WARNING: Response seems too short or unexpected")
            return False
            
    except Exception as e:
        print(f"ERROR: OpenRouter API test failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_openrouter_api())
    print(f"\nFinal Status: {'WORKING' if result else 'FAILED'}")