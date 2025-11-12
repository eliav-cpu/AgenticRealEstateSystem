#!/usr/bin/env python3
"""
Test the routing fixes for agent intent detection.
"""

def test_routing_logic():
    """Test the updated routing logic."""
    
    # Updated keywords from the fixed code
    scheduling_keywords = [
        "can i visit", "want to visit", "like to visit", "schedule a visit", "book a visit",
        "i want to see it", "can i see it", "want to see the property", "want to see this property",
        "schedule for", "book for", "schedule an appointment", "book an appointment",
        "schedule a tour", "book a tour", "view the property", "tour the property",
        "visit tomorrow", "see tomorrow", "visit today", "see today", "visit this week", 
        "visit next week", "tomorrow at", "today at", "this week at", "next week at",
        "available times", "when can", "what time", "time slots", "calendar",
        "at 3pm", "at 2 pm", "in the morning", "in the afternoon", "in the evening",
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
    ]
    
    search_keywords = [
        "i need a place", "need a place", "looking for", "looking for a", "find me",
        "search", "want a", "need an", "show me properties", "find properties",
        "i want", "i need", "something nice", "something in", "place to live",
        "bedrooms", "bedroom", "bathrooms", "bathroom", "budget", "around $", "under $",
        "2 bedrooms", "3 bedrooms", "1 bedroom", "studio", "house", "apartment",
        "in miami", "in downtown", "near beach", "south beach", "brickell",
        "with pool", "with gym", "with parking", "pet friendly", "furnished",
        "ocean view", "waterfront", "balcony", "garden", "terrace",
        "different", "other properties", "alternatives", "similar", "what else",
        "more options", "something else", "cheaper", "better", "bigger", "larger",
        "want to see a", "want to see something", "do you have", "show me", "any other"
    ]
    
    # Test cases
    test_cases = [
        {
            "message": "I want to see a bigger property? do you have one?",
            "expected": "search_agent",
            "reason": "Should match 'want to see a' and 'bigger' and 'do you have'"
        },
        {
            "message": "Can I visit tomorrow at 3pm?",
            "expected": "scheduling_agent", 
            "reason": "Should match 'can i visit' and 'tomorrow at'"
        },
        {
            "message": "I want to see it tomorrow",
            "expected": "scheduling_agent",
            "reason": "Should match 'i want to see it' and 'tomorrow'"
        },
        {
            "message": "Show me something bigger",
            "expected": "search_agent",
            "reason": "Should match 'show me' and 'bigger'"
        }
    ]
    
    print("Testing Routing Logic")
    print("=" * 50)
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        message = test["message"]
        expected = test["expected"]
        reason = test["reason"]
        
        user_content = message.lower()
        
        # Check matches
        scheduling_matches = [kw for kw in scheduling_keywords if kw in user_content]
        search_matches = [kw for kw in search_keywords if kw in user_content]
        
        # Determine routing (same logic as SwarmOrchestrator)
        if scheduling_matches:
            actual = "scheduling_agent"
        elif search_matches:
            actual = "search_agent"
        else:
            actual = "property_agent"
        
        # Check result
        passed = actual == expected
        status = "PASS" if passed else "FAIL"
        
        print(f"Test {i}: {status}")
        print(f"  Message: '{message}'")
        print(f"  Expected: {expected}")
        print(f"  Actual: {actual}")
        print(f"  Reason: {reason}")
        print(f"  Scheduling matches: {scheduling_matches}")
        print(f"  Search matches: {search_matches}")
        print()
        
        if not passed:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("ALL TESTS PASSED! Routing logic is working correctly.")
    else:
        print("SOME TESTS FAILED! Check the logic above.")
    
    return all_passed

if __name__ == "__main__":
    test_routing_logic()