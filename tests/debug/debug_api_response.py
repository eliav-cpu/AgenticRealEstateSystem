#!/usr/bin/env python3
"""
Script para debugar a resposta da API e verificar estrutura dos dados
"""

import requests
import json
import sys
import os

def test_api_response():
    """Testar resposta da API"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 Testing API Response Structure")
    print("=" * 50)
    
    # Testar modo Mock
    print("\n📦 TESTING MOCK MODE:")
    try:
        response = requests.get(f"{base_url}/api/properties/search?mode=mock")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            print(f"Success: {data.get('success')}")
            print(f"Data Type: {type(data.get('data'))}")
            
            if isinstance(data.get('data'), list):
                print(f"Data Length: {len(data['data'])}")
                if len(data['data']) > 0:
                    first_property = data['data'][0]
                    print(f"First Property Keys: {list(first_property.keys())}")
                    print(f"First Property ID: {first_property.get('id')}")
                    print(f"First Property Address: {first_property.get('formattedAddress')}")
                    print(f"First Property Type: {first_property.get('propertyType')}")
                else:
                    print("❌ No properties in data array")
            else:
                print(f"❌ Data is not a list: {data.get('data')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Testar modo Real
    print("\n🌐 TESTING REAL MODE:")
    try:
        response = requests.get(f"{base_url}/api/properties/search?mode=real")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            print(f"Success: {data.get('success')}")
            print(f"Data Type: {type(data.get('data'))}")
            
            if isinstance(data.get('data'), list):
                print(f"Data Length: {len(data['data'])}")
                if len(data['data']) > 0:
                    first_property = data['data'][0]
                    print(f"First Property Keys: {list(first_property.keys())}")
                    print(f"First Property ID: {first_property.get('id')}")
                    print(f"First Property Address: {first_property.get('formattedAddress')}")
                    print(f"First Property Type: {first_property.get('propertyType')}")
                else:
                    print("❌ No properties in data array")
            else:
                print(f"❌ Data is not a list: {data.get('data')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_api_response() 