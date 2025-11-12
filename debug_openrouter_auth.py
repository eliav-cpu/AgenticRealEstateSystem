#!/usr/bin/env python3
"""
Debug OpenRouter authentication issue
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv
from config.settings import get_settings

async def test_openrouter_direct():
    """Test OpenRouter API directly with httpx"""
    load_dotenv()
    
    settings = get_settings()
    api_key = settings.apis.openrouter_key
    
    print("=== OpenRouter Authentication Debug ===")
    print(f"API Key loaded: {bool(api_key)}")
    print(f"API Key length: {len(api_key) if api_key else 0}")
    print(f"API Key prefix: {api_key[:20] if api_key else 'None'}...")
    print(f"API Key format valid: {api_key.startswith('sk-or-v1-') if api_key else False}")
    
    # Test direct HTTP call
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Agentic-Real-Estate/1.0"
    }
    
    payload = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [
            {"role": "user", "content": "Hello, please respond with exactly: 'Authentication successful'"}
        ],
        "max_tokens": 50
    }
    
    print(f"\nTesting direct API call...")
    print(f"URL: https://openrouter.ai/api/v1/chat/completions")
    print(f"Headers: Authorization: Bearer {api_key[:20]}...")
    print(f"Model: mistralai/mistral-7b-instruct:free")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            print(f"\nResponse Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                print(f"SUCCESS: {content}")
                return True
            else:
                print(f"ERROR: {response.status_code}")
                print(f"Response Body: {response.text}")
                return False
                
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_openrouter_direct())
    print(f"\nFinal Result: {'SUCCESS' if result else 'FAILED'}")