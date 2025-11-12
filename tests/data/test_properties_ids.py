#!/usr/bin/env python3
"""Test to check property IDs returned by the API"""

import requests
import json

def test_properties_ids():
    """Test to see what property IDs are being returned"""
    
    base_url = "http://localhost:8000"
    
    try:
        print("🧪 Testing properties endpoint to check IDs...")
        
        # Test mock mode
        response = requests.get(f"{base_url}/api/properties/search?mode=mock")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Properties API working!")
            print(f"Response structure: {json.dumps(result, indent=2)[:500]}...")
            
            if result.get("success") and result.get("data"):
                properties = result["data"]
                print(f"\n📊 Found {len(properties)} properties in MOCK mode")
                
                for i, prop in enumerate(properties[:3]):  # Show first 3 properties
                    print(f"\n🏠 Property {i+1}:")
                    print(f"   ID: {prop.get('id', 'NO ID')}")
                    print(f"   Address: {prop.get('formattedAddress', 'NO ADDRESS')}")
                    print(f"   Price: ${prop.get('price', 'NO PRICE'):,}")
                    
                    # Test creating a session with this property ID
                    if prop.get('id'):
                        print(f"\n🧪 Testing agent session with ID: {prop.get('id')}")
                        test_session_with_id(prop.get('id'))
                        break  # Only test the first one
            else:
                print(f"❌ Properties API failed: {result}")
        else:
            print(f"❌ Properties request failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

def test_session_with_id(property_id):
    """Test creating a session with a specific property ID"""
    
    base_url = "http://localhost:8000"
    
    try:
        session_data = {
            "property_id": property_id,
            "mode": "details",
            "language": "en"
        }
        
        response = requests.post(
            f"{base_url}/api/agent/session/start?mode=mock",
            json=session_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Session created with property ID: {property_id}")
            
            if result.get("success") and result.get("data", {}).get("session"):
                session_id = result["data"]["session"]["session_id"]
                
                # Test sending a message
                message_data = {
                    "message": "Tell me about this property",
                    "session_id": session_id
                }
                
                chat_response = requests.post(
                    f"{base_url}/api/agent/chat?mode=mock",
                    json=message_data,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if chat_response.status_code == 200:
                    chat_result = chat_response.json()
                    
                    if chat_result.get("success"):
                        agent_response = chat_result.get("data", {})
                        message = agent_response.get("message", "")
                        
                        print(f"   🤖 Agent Response: {message[:150]}...")
                        
                        # Check if using property data
                        if "Miami" in message and "$" in message:
                            print(f"   ✅ SUCCESS: Agent using property data!")
                        else:
                            print(f"   ❌ FAILED: Agent not using property data")
                    else:
                        print(f"   ❌ Chat failed: {chat_result}")
                else:
                    print(f"   ❌ Chat request failed: {chat_response.status_code}")
            else:
                print(f"   ❌ Session creation failed: {result}")
        else:
            print(f"   ❌ Session request failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing session: {e}")

if __name__ == "__main__":
    test_properties_ids() 