#!/usr/bin/env python3
"""
Teste para verificar o contexto da propriedade
"""

import requests

def test_property_context():
    print('=== TESTING PROPERTY CONTEXT ===')
    
    # Test mock mode
    print('\n--- MOCK MODE ---')
    mock_resp = requests.get('http://localhost:8000/api/properties/search?mode=mock')
    mock_props = mock_resp.json()['data']
    print(f'Total mock properties: {len(mock_props)}')
    
    # Find property with id "1"
    mock_prop_1 = None
    for prop in mock_props:
        if str(prop.get('id')) == '1':
            mock_prop_1 = prop
            break
    
    if mock_prop_1:
        print(f'Mock Property ID 1: {mock_prop_1.get("formattedAddress", "N/A")}')
        print(f'Price: ${mock_prop_1.get("price", "N/A")}')
        print(f'Bedrooms: {mock_prop_1.get("bedrooms", "N/A")}')
    else:
        print('❌ Property ID 1 not found in mock data')
    
    # Test real mode
    print('\n--- REAL MODE ---')
    real_resp = requests.get('http://localhost:8000/api/properties/search?mode=real')
    real_props = real_resp.json()['data']
    print(f'Total real properties: {len(real_props)}')
    
    # Find property with id "1"
    real_prop_1 = None
    for prop in real_props:
        if str(prop.get('id')) == '1':
            real_prop_1 = prop
            break
    
    if real_prop_1:
        print(f'Real Property ID 1: {real_prop_1.get("formattedAddress", "N/A")}')
        print(f'Price: ${real_prop_1.get("price", "N/A")}')
        print(f'Bedrooms: {real_prop_1.get("bedrooms", "N/A")}')
    else:
        print('❌ Property ID 1 not found in real data')

if __name__ == "__main__":
    test_property_context() 