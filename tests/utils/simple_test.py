#!/usr/bin/env python3
"""
Simple test to verify the system works.
"""

print("🧪 Testing system...")

try:
    from config.settings import get_settings
    print("✅ Settings loaded")
    
    settings = get_settings()
    api_key = settings.apis.openrouter_key
    print(f"✅ API Key available: {bool(api_key and api_key.strip())}")
    
    from app.orchestration.swarm import get_swarm_orchestrator
    print("✅ Swarm orchestrator imported")
    
    print("🎉 Basic imports successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()