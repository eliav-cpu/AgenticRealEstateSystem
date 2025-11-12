#!/usr/bin/env python3
"""
Test script to verify OpenRouter API key loading.
"""

import asyncio
from config.settings import get_settings

async def test_api_key_loading():
    """Test if API key is being loaded correctly."""
    
    print("Testing API key loading...")
    
    try:
        settings = get_settings()
        api_key = settings.apis.openrouter_key
        
        print(f"API key loaded: {bool(api_key)}")
        print(f"API key length: {len(api_key) if api_key else 0}")
        print(f"API key preview: {api_key[:15]}... (showing first 15 chars)")
        
        # Test if key is the default/placeholder value
        if api_key == "your_openrouter_api_key_here" or not api_key or api_key.strip() == "":
            print("ERROR: API key is empty or placeholder value!")
            return False
        
        # Check if key starts with expected format
        if not api_key.startswith("sk-or-v1-"):
            print("WARNING: API key doesn't start with expected format 'sk-or-v1-'")
            print(f"Actual start: {api_key[:10]}")
        
        print("SUCCESS: API key appears to be loaded correctly")
        return True
        
    except Exception as e:
        print(f"ERROR loading API key: {e}")
        return False

async def test_direct_api_call():
    """Test a direct API call to verify the key works."""
    
    print("\nTesting direct API call...")
    
    try:
        import httpx
        from config.settings import get_settings
        
        settings = get_settings()
        api_key = settings.apis.openrouter_key
        
        if not api_key:
            print("ERROR: No API key available for testing")
            return False
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistralai/mistral-7b-instruct:free",
                    "messages": [{"role": "user", "content": "Hello, respond with 'API key working!'"}],
                    "temperature": 0.1,
                    "max_tokens": 20
                },
                timeout=30.0
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"Response content: {content}")
                print("SUCCESS: API key is working!")
                return True
            else:
                print(f"ERROR: API call failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"ERROR in API call: {e}")
        return False

async def main():
    """Run all tests."""
    
    print("OPENROUTER API KEY TEST SUITE")
    print("=" * 50)
    
    # Test 1: Key loading
    key_ok = await test_api_key_loading()
    
    # Test 2: Direct API call (only if key loaded)
    if key_ok:
        api_ok = await test_direct_api_call()
    else:
        api_ok = False
        print("\nSkipping API call test - key loading failed")
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"API Key Loading: {'PASS' if key_ok else 'FAIL'}")
    print(f"API Call Test: {'PASS' if api_ok else 'FAIL'}")
    
    if key_ok and api_ok:
        print("\nSUCCESS: All tests passed! API key is working correctly.")
    else:
        print("\nERROR: Some tests failed. Check the issues above.")

if __name__ == "__main__":
    asyncio.run(main())