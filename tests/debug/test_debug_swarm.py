#!/usr/bin/env python3
"""
Debug test for SwarmOrchestrator to understand why it's not working properly
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from app.orchestration.swarm import SwarmOrchestrator

async def test_swarm_orchestrator():
    """Test the SwarmOrchestrator directly"""
    
    print("🧪 TESTING SWARM ORCHESTRATOR DIRECTLY")
    print("=" * 60)
    
    try:
        # Initialize orchestrator
        print("1️⃣ Initializing SwarmOrchestrator...")
        orchestrator = SwarmOrchestrator()
        print(f"✅ SwarmOrchestrator created: {type(orchestrator)}")
        
        # Test property context
        property_context = {
            'id': '15741-Sw-137th-Ave,-Apt-204,-Miami,-FL-33177',
            'formattedAddress': '15741 Sw 137th Ave, Apt 204, Miami, FL 33177',
            'city': 'Miami',
            'state': 'FL',
            'price': 2450,
            'bedrooms': 3,
            'bathrooms': 2,
            'squareFootage': 1120,
            'yearBuilt': 2001,
            'propertyType': 'Apartment'
        }
        
        # Create test message
        test_message = {
            "messages": [{"role": "user", "content": "What is the price of this property?"}],
            "session_id": "test_session",
            "current_agent": "property_agent",
            "context": {
                "property_context": property_context,
                "data_mode": "mock",
                "source": "debug_test"
            }
        }
        
        print("2️⃣ Sending test message to SwarmOrchestrator...")
        print(f"Message: {test_message['messages'][0]['content']}")
        print(f"Property: {property_context['formattedAddress']}")
        print(f"Agent: {test_message['current_agent']}")
        
        # Process message
        result = await orchestrator.process_message(test_message)
        
        print("3️⃣ SwarmOrchestrator Response:")
        print(f"Result type: {type(result)}")
        print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict):
            if "messages" in result:
                print(f"Messages count: {len(result['messages'])}")
                if result['messages']:
                    last_msg = result['messages'][-1]
                    print(f"Last message type: {type(last_msg)}")
                    if isinstance(last_msg, dict):
                        print(f"Last message content: {last_msg.get('content', 'No content')[:200]}...")
                    else:
                        print(f"Last message content: {getattr(last_msg, 'content', 'No content')[:200]}...")
            
            if "current_agent" in result:
                print(f"Current agent: {result['current_agent']}")
        
        print("\n4️⃣ Testing with streaming...")
        
        async for chunk in orchestrator.process_stream(test_message):
            print(f"Stream chunk: {chunk}")
            break  # Just test first chunk
        
        print("\n✅ SwarmOrchestrator test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing SwarmOrchestrator: {e}")
        import traceback
        print(f"Full traceback:\n{traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_swarm_orchestrator()) 