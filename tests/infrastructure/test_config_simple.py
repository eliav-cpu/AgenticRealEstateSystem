#!/usr/bin/env python3
"""
Simple test to verify configuration loading.
"""

def test_config():
    """Test configuration loading."""
    
    print("Testing configuration loading...")
    
    try:
        from config.settings import get_settings
        
        settings = get_settings()
        
        print(f"App name: {settings.app_name}")
        print(f"Environment: {settings.environment}")
        print(f"Debug: {settings.debug}")
        
        # Test API key
        api_key = settings.apis.openrouter_key
        print(f"API key loaded: {bool(api_key)}")
        
        if api_key:
            print(f"API key length: {len(api_key)}")
            print(f"API key starts correctly: {api_key.startswith('sk-or-v1-')}")
        
        # Test models
        print(f"Default model: {settings.models.default_model}")
        print(f"Search model: {settings.models.search_model}")
        print(f"Property model: {settings.models.property_model}")
        
        # Test swarm config
        search_agent = settings.swarm.agents.get("search", {})
        print(f"Search agent model: {search_agent.get('model')}")
        
        print("SUCCESS: Configuration loaded correctly")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_config()