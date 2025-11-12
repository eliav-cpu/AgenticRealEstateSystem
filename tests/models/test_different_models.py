#!/usr/bin/env python3
"""
Test different OpenRouter models to find which ones work
"""

import asyncio
import os
from dotenv import load_dotenv
from config.settings import get_settings
from app.orchestration.swarm import create_pydantic_agent

async def test_model(model_name: str) -> bool:
    """Test a specific model"""
    try:
        print(f"\n--- Testing {model_name} ---")
        
        agent = await create_pydantic_agent("test_agent", model_name)
        print(f"✓ Agent created successfully")
        
        result = await agent.run("Hello, please respond with exactly: 'Test successful'")
        response = str(result.output)
        print(f"✓ Response: {response}")
        
        if len(response) > 5:
            print(f"✓ SUCCESS: {model_name} is working!")
            return True
        else:
            print(f"✗ WARNING: Response too short for {model_name}")
            return False
            
    except Exception as e:
        print(f"✗ ERROR with {model_name}: {e}")
        return False

async def main():
    """Test multiple models"""
    load_dotenv()
    
    # Test different model variations
    models_to_test = [
        "mistralai/mistral-7b-instruct:free",  # Current failing model
        "google/gemma-2-9b-it:free",           # Alternative free model
        "microsoft/phi-3-medium-128k-instruct:free",  # Another free option
        "mistralai/mistral-7b-instruct",       # Non-free version
        "openai/gpt-3.5-turbo",               # Standard model
    ]
    
    print("Testing different OpenRouter models...")
    
    successful_models = []
    
    for model in models_to_test:
        success = await test_model(model)
        if success:
            successful_models.append(model)
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    print(f"\n=== RESULTS ===")
    if successful_models:
        print(f"✓ Working models: {successful_models}")
        print(f"Recommendation: Use {successful_models[0]}")
    else:
        print("✗ No models worked - API key might be invalid")
    
    return len(successful_models) > 0

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\nFinal status: {'SUCCESS' if result else 'FAILED'}")