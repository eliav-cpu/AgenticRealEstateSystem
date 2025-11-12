#!/usr/bin/env python3
"""
Script to find working OpenRouter models as alternatives to the failed ones.
Tests multiple free models to find reliable alternatives.
"""

import asyncio
import httpx
from config.settings import get_settings
from typing import List, Dict, Tuple

# List of free OpenRouter models to test
MODELS_TO_TEST = [
    # Meta/LLaMA models
    "meta-llama/llama-3.1-8b-instruct:free",
    "meta-llama/llama-3-8b-instruct:free", 
    "meta-llama/llama-3.2-3b-instruct:free",
    "meta-llama/llama-3.2-1b-instruct:free",
    
    # Google models
    "google/gemma-2-9b-it:free",
    "google/gemma-2-2b-it:free", 
    "google/gemini-flash-1.5:free",
    "google/gemma-7b-it:free",
    
    # Microsoft models
    "microsoft/phi-3-mini-128k-instruct:free",
    "microsoft/phi-3-medium-128k-instruct:free",
    
    # Mistral models
    "mistralai/mistral-7b-instruct:free",
    "mistralai/mixtral-8x7b-instruct:free",
    
    # Hugging Face models
    "huggingfaceh4/zephyr-7b-beta:free",
    "openchat/openchat-7b:free",
    
    # Other providers
    "qwen/qwen-2-7b-instruct:free",
    "nousresearch/nous-capybara-7b:free",
]

async def test_model_availability(model_name: str) -> Tuple[bool, str, Dict]:
    """Test if a specific model is available and working."""
    
    settings = get_settings()
    api_key = settings.apis.openrouter_key
    
    if not api_key or api_key.strip() == "":
        return False, "No API key", {}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": "Hello! Respond with exactly: 'Model working!'"}],
                    "temperature": 0.1,
                    "max_tokens": 20
                },
                timeout=15.0
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Test response quality
                response_quality = {
                    "status_code": response.status_code,
                    "content_length": len(content),
                    "content": content,
                    "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0
                }
                
                return True, "Working", response_quality
            else:
                error_info = response.text[:200] if response.text else "Unknown error"
                return False, f"HTTP {response.status_code}: {error_info}", {}
                
    except Exception as e:
        return False, f"Exception: {str(e)[:100]}", {}

async def test_real_estate_capability(model_name: str) -> Tuple[bool, str]:
    """Test if model can handle real estate queries well."""
    
    settings = get_settings()
    api_key = settings.apis.openrouter_key
    
    real_estate_prompt = """You are a real estate assistant. A user asks: "How much is the rent for a 2-bedroom apartment in Miami?"

Respond professionally in 1-2 sentences with a helpful answer."""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": real_estate_prompt}],
                    "temperature": 0.3,
                    "max_tokens": 100
                },
                timeout=20.0
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Check if response is relevant and well-formed
                is_good_response = (
                    len(content.strip()) > 20 and 
                    any(word in content.lower() for word in ['rent', 'price', 'cost', 'apartment', 'miami']) and
                    len(content) < 500  # Not too verbose
                )
                
                return is_good_response, content
            else:
                return False, f"HTTP {response.status_code}"
                
    except Exception as e:
        return False, f"Exception: {str(e)[:100]}"

async def find_working_models():
    """Test all models and find the best working alternatives."""
    
    print("🔍 SEARCHING FOR WORKING OPENROUTER MODELS")
    print("=" * 60)
    
    working_models = []
    failed_models = []
    
    for i, model_name in enumerate(MODELS_TO_TEST, 1):
        print(f"\n📋 Testing {i}/{len(MODELS_TO_TEST)}: {model_name}")
        
        # Test basic availability
        is_available, status, quality_info = await test_model_availability(model_name)
        
        if is_available:
            print(f"✅ Available - {status}")
            print(f"   Response: {quality_info.get('content', 'N/A')}")
            
            # Test real estate capability
            can_handle_re, re_response = await test_real_estate_capability(model_name)
            
            if can_handle_re:
                print(f"🏠 Real Estate Test: ✅ Good")
                print(f"   Sample: {re_response[:100]}...")
                
                working_models.append({
                    "model": model_name,
                    "basic_test": quality_info,
                    "real_estate_response": re_response,
                    "score": len(re_response) + (100 if "rent" in re_response.lower() else 0)
                })
            else:
                print(f"🏠 Real Estate Test: ❌ Poor response")
                print(f"   Issue: {re_response}")
        else:
            print(f"❌ Failed - {status}")
            failed_models.append({"model": model_name, "error": status})
        
        # Small delay to avoid rate limiting
        await asyncio.sleep(1)
    
    # Sort working models by score
    working_models.sort(key=lambda x: x["score"], reverse=True)
    
    print("\n" + "=" * 60)
    print("📊 RESULTS SUMMARY")
    print("=" * 60)
    
    print(f"\n✅ WORKING MODELS ({len(working_models)}):")
    for i, model_info in enumerate(working_models[:5], 1):  # Show top 5
        model = model_info["model"]
        score = model_info["score"]
        print(f"   {i}. {model} (Score: {score})")
    
    print(f"\n❌ FAILED MODELS ({len(failed_models)}):")
    for model_info in failed_models[:10]:  # Show first 10 failures
        model = model_info["model"]
        error = model_info["error"]
        print(f"   • {model}: {error}")
    
    if working_models:
        best_model = working_models[0]
        print(f"\n🏆 RECOMMENDED MODEL: {best_model['model']}")
        print(f"📝 Sample Response: {best_model['real_estate_response'][:150]}...")
        
        return working_models
    else:
        print("\n❌ NO WORKING MODELS FOUND!")
        print("💡 Consider using Ollama fallback or check API keys")
        return []

async def main():
    """Main execution function."""
    working_models = await find_working_models()
    
    if working_models:
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. Update swarm.py to use: {working_models[0]['model']}")
        print(f"2. Update fallback model to: {working_models[1]['model'] if len(working_models) > 1 else 'same model'}")
        print(f"3. Test the updated system")
        
        # Save results to file
        import json
        with open("working_models_results.json", "w") as f:
            json.dump(working_models, f, indent=2)
        print(f"\n💾 Results saved to working_models_results.json")

if __name__ == "__main__":
    asyncio.run(main())