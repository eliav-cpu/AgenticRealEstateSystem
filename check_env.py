#!/usr/bin/env python3
"""
Check environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check the key
api_key = os.getenv("OPENROUTER_API_KEY")

print(f"API Key found: {bool(api_key)}")
if api_key:
    print(f"Length: {len(api_key)}")
    print(f"Starts with sk-or-v1-: {api_key.startswith('sk-or-v1-')}")
    print(f"First 25 chars: {api_key[:25]}...")
    print(f"Contains spaces: {' ' in api_key}")
    print(f"Contains newlines: {'\\n' in api_key or '\\r' in api_key}")
    
    # Check for common issues
    if api_key.strip() != api_key:
        print("WARNING: API key has leading/trailing whitespace")
    
    if "your_openrouter_api_key_here" in api_key:
        print("ERROR: API key is still placeholder value")
else:
    print("ERROR: No API key found in environment")