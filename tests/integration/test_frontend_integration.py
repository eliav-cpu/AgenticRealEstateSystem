#!/usr/bin/env python3
"""
Test frontend integration by making a direct request to the FastAPI endpoint.
"""

import asyncio
import httpx
import time

async def test_frontend_request():
    """Test the frontend integration."""
    
    print("Testing frontend integration...")
    
    # Test data that would normally come from frontend
    test_data = {
        "message": "Looking for a 2 bedroom apartment with pool",
        "user_id": "test_user",
        "session_id": "test_session",
        "context": {
            "data_mode": "mock"
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("Making request to /api/chat endpoint...")
            
            response = await client.post(
                "http://localhost:8000/api/chat",
                json=test_data
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"SUCCESS: {result}")
                return True
            else:
                print(f"ERROR: {response.text}")
                return False
                
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_frontend_request())