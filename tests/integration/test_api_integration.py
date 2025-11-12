#!/usr/bin/env python3
"""Test script to validate API integration with SwarmOrchestrator"""

import asyncio
import aiohttp
import json
import sys

async def test_agent_session():
    """Test creating an agent session and sending a message"""
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        try:
            print("🧪 Testing agent session creation...")
            
            # Test 1: Create agent session
            session_data = {
                "property_id": "1",
                "mode": "details",
                "language": "en"
            }
            
            async with session.post(
                f"{base_url}/api/agent/session/start?mode=mock",
                json=session_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Session created successfully!")
                    print(f"📊 Response: {json.dumps(result, indent=2)}")
                    
                    if result.get("success") and result.get("data", {}).get("session"):
                        session_id = result["data"]["session"]["session_id"]
                        print(f"🆔 Session ID: {session_id}")
                        
                        # Test 2: Send message to agent
                        print("\n🧪 Testing message sending...")
                        
                        message_data = {
                            "message": "Tell me about this property",
                            "session_id": session_id
                        }
                        
                        async with session.post(
                            f"{base_url}/api/agent/chat?mode=mock",
                            json=message_data,
                            headers={"Content-Type": "application/json"}
                        ) as chat_response:
                            if chat_response.status == 200:
                                chat_result = await chat_response.json()
                                print(f"✅ Message sent successfully!")
                                print(f"📊 Chat Response: {json.dumps(chat_result, indent=2)}")
                                
                                if chat_result.get("success"):
                                    agent_response = chat_result.get("data", {})
                                    message = agent_response.get("message", "")
                                    agent_name = agent_response.get("agent_name", "")
                                    
                                    print(f"\n🤖 Agent: {agent_name}")
                                    print(f"💬 Message: {message[:200]}...")
                                    
                                    # Check if using real property data
                                    if "Miami" in message and "$" in message:
                                        print("✅ SUCCESS: Agent is using real property data!")
                                    else:
                                        print("❌ FAILED: Agent not using property data")
                                else:
                                    print(f"❌ Chat failed: {chat_result}")
                            else:
                                error_text = await chat_response.text()
                                print(f"❌ Chat request failed: {chat_response.status} - {error_text}")
                    else:
                        print(f"❌ Session creation failed: {result}")
                else:
                    error_text = await response.text()
                    print(f"❌ Session request failed: {response.status} - {error_text}")
                    
        except Exception as e:
            print(f"❌ Error during test: {e}")
            import traceback
            traceback.print_exc()

async def test_properties_endpoint():
    """Test if properties endpoint is working"""
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        try:
            print("\n🧪 Testing properties endpoint...")
            
            async with session.get(
                f"{base_url}/api/properties/search?mode=mock"
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Properties endpoint working!")
                    
                    if result.get("success") and result.get("data"):
                        properties = result["data"]
                        print(f"📊 Found {len(properties)} properties")
                        
                        if properties:
                            first_prop = properties[0]
                            print(f"🏠 First property: {first_prop.get('formattedAddress', 'N/A')}")
                            print(f"💰 Price: ${first_prop.get('price', 'N/A'):,}")
                            return first_prop
                    else:
                        print(f"❌ Properties endpoint failed: {result}")
                else:
                    error_text = await response.text()
                    print(f"❌ Properties request failed: {response.status} - {error_text}")
                    
        except Exception as e:
            print(f"❌ Error testing properties: {e}")
    
    return None

async def main():
    """Run all tests"""
    print("🚀 Starting API Integration Tests...")
    print("=" * 60)
    
    # Test properties first
    property_data = await test_properties_endpoint()
    
    # Test agent session
    await test_agent_session()
    
    print("\n" + "=" * 60)
    print("🏁 API Integration Tests Completed!")

if __name__ == "__main__":
    asyncio.run(main()) 