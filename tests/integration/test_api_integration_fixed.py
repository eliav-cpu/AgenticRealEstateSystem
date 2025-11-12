#!/usr/bin/env python3
"""Test script to validate API integration after fix"""

import asyncio
import aiohttp
import json
import sys

async def test_agent_session_fixed():
    """Test creating an agent session and sending a message with the fix"""
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        try:
            print("🧪 Testing FIXED agent session...")
            
            # Test 1: Create agent session with a real property ID
            print("1️⃣ Creating agent session...")
            session_data = {
                "property_id": "15741-Sw-137th-Ave,-Apt-204,-Miami,-FL-33177",
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
                    print(f"✅ Session created: {result['data']['session']['session_id']}")
                    session_id = result['data']['session']['session_id']
                else:
                    print(f"❌ Failed to create session: {response.status}")
                    return
            
            # Test 2: Send message to agent
            print("\n2️⃣ Sending message to agent...")
            message_data = {
                "message": "What is the price of this property?",
                "session_id": session_id
            }
            
            async with session.post(
                f"{base_url}/api/agent/chat?mode=mock",
                json=message_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    agent_response = result['data']
                    
                    print(f"✅ Agent Response:")
                    print(f"   Agent: {agent_response['agent_name']}")
                    print(f"   Message: {agent_response['message'][:200]}...")
                    print(f"   Success: {agent_response['success']}")
                    
                    # Check if it contains real property data
                    message_content = agent_response['message']
                    if "$2,450" in message_content and "15741 Sw 137th Ave" in message_content:
                        print("🎉 SUCCESS! Real agentic system is working with property data!")
                    elif "Emma - Property Expert" in agent_response['agent_name']:
                        print("⚠️  Agentic system working but check property data")
                    else:
                        print("❌ Still using mock responses")
                        
                else:
                    print(f"❌ Failed to send message: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
            
            # Test 3: Send follow-up message
            print("\n3️⃣ Sending follow-up message...")
            followup_data = {
                "message": "How many bedrooms does it have?",
                "session_id": session_id
            }
            
            async with session.post(
                f"{base_url}/api/agent/chat?mode=mock",
                json=followup_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    agent_response = result['data']
                    
                    print(f"✅ Follow-up Response:")
                    print(f"   Agent: {agent_response['agent_name']}")
                    print(f"   Message: {agent_response['message'][:200]}...")
                    
                    # Check if it mentions 3 bedrooms (correct data)
                    if "3" in agent_response['message'] and ("bedroom" in agent_response['message'].lower() or "quartos" in agent_response['message'].lower()):
                        print("🎉 PERFECT! Agent has correct property context!")
                    else:
                        print("⚠️  Agent response doesn't match expected property data")
                        
                else:
                    print(f"❌ Failed to send follow-up: {response.status}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_agent_session_fixed()) 