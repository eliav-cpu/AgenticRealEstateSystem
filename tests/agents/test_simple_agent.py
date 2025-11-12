#!/usr/bin/env python3
"""Simple test for agent API"""

import requests
import json

def test_agent_api():
    """Test agent API endpoints"""
    
    base_url = "http://localhost:8000"
    
    try:
        print("🧪 Testing agent API...")
        
        # Test 1: Create session with a real property ID from mock data
        print("1️⃣ Creating agent session...")
        
        session_data = {
            "property_id": "15741-Sw-137th-Ave,-Apt-204,-Miami,-FL-33177",  # Use real mock property ID
            "mode": "details",
            "language": "en"
        }
        
        response = requests.post(
            f"{base_url}/api/agent/session/start?mode=mock",
            json=session_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Session created!")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if result.get("success") and result.get("data", {}).get("session"):
                session_id = result["data"]["session"]["session_id"]
                print(f"🆔 Session ID: {session_id}")
                
                # Test 2: Send message
                print("\n2️⃣ Sending message...")
                
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
                
                print(f"Chat Status: {chat_response.status_code}")
                
                if chat_response.status_code == 200:
                    chat_result = chat_response.json()
                    print(f"✅ Message sent!")
                    print(f"Chat Response: {json.dumps(chat_result, indent=2)}")
                    
                    if chat_result.get("success"):
                        agent_response = chat_result.get("data", {})
                        message = agent_response.get("message", "")
                        agent_name = agent_response.get("agent_name", "")
                        
                        print(f"\n🤖 Agent: {agent_name}")
                        print(f"💬 Message: {message}")
                        
                        # Check if using real property data
                        if ("Miami" in message and "$" in message) or ("15741 Sw 137th Ave" in message):
                            print("✅ SUCCESS: Agent is using real property data!")
                        else:
                            print("❌ FAILED: Agent not using property data")
                            print(f"Looking for Miami and $ or address in: {message[:200]}...")
                    else:
                        print(f"❌ Chat failed: {chat_result}")
                else:
                    print(f"❌ Chat request failed: {chat_response.status_code}")
                    print(f"Error: {chat_response.text}")
            else:
                print(f"❌ Session creation failed: {result}")
        else:
            print(f"❌ Session request failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent_api() 