#!/usr/bin/env python3
"""
Teste do sistema de roteamento do Swarm
"""

from app.orchestration.swarm import route_message

def test_routing():
    """Testa diferentes tipos de mensagens para verificar o roteamento"""
    
    # Test cases with expected routing
    test_cases = [
        # Search cases
        ("I want a house with pool", "search_agent"),
        ("I want a property with pool", "search_agent"),
        ("Do you have any properties with gym?", "search_agent"),
        ("I'm looking for a bigger apartment", "search_agent"),
        ("Show me other properties", "search_agent"),
        ("Find me something cheaper", "search_agent"),
        ("Any properties available?", "search_agent"),
        
        # Property details cases (with property context)
        ("How big is this apartment?", "property_agent"),
        ("What's the rent price?", "property_agent"),
        ("Tell me about this property", "property_agent"),
        ("How much sq ft is this apartment?", "property_agent"),
        
        # Scheduling cases
        ("I want to schedule a visit", "scheduling_agent"),
        ("Can I book a viewing?", "scheduling_agent"),
        ("When can I see the property?", "scheduling_agent"),
        ("Schedule an appointment", "scheduling_agent"),
    ]
    
    print("🧪 Testing routing logic...")
    print("=" * 50)
    
    for message, expected_agent in test_cases:
        # Create test state
        state = {
            "messages": [{"content": message}],
            "context": {
                "property_context": {
                    "formattedAddress": "123 Test St, Miami, FL",
                    "price": 2500
                }
            }
        }
        
        # Test routing
        result = route_message(state)
        
        # Check result
        status = "✅" if result == expected_agent else "❌"
        print(f"{status} '{message}' -> {result} (expected: {expected_agent})")
        
        if result != expected_agent:
            print(f"   ⚠️  MISMATCH: Got {result}, expected {expected_agent}")
    
    print("=" * 50)
    print("🏁 Routing test completed!")

if __name__ == "__main__":
    test_routing() 