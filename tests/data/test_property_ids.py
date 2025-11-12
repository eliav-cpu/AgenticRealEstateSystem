#!/usr/bin/env python3
"""
Teste para verificar os IDs das propriedades
"""

import requests

def test_property_ids():
    print('=== TESTING PROPERTY IDs ===')
    
    # Test mock mode
    print('\n--- MOCK MODE IDs ---')
    mock_resp = requests.get('http://localhost:8000/api/properties/search?mode=mock')
    mock_props = mock_resp.json()['data']
    print(f'Mock properties: {len(mock_props)}')
    for i, prop in enumerate(mock_props[:5]):
        print(f'{i+1}. ID: {prop.get("id", "N/A")} - {prop.get("formattedAddress", "N/A")}')
    
    # Test real mode
    print('\n--- REAL MODE IDs ---')
    real_resp = requests.get('http://localhost:8000/api/properties/search?mode=real')
    real_props = real_resp.json()['data']
    print(f'Real properties: {len(real_props)}')
    for i, prop in enumerate(real_props[:5]):
        print(f'{i+1}. ID: {prop.get("id", "N/A")} - {prop.get("formattedAddress", "N/A")}')

if __name__ == "__main__":
    test_property_ids() 