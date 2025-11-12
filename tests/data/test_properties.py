#!/usr/bin/env python3
"""
Teste para verificar propriedades em diferentes modos
"""

import requests

def test_properties():
    print('=== MOCK MODE PROPERTIES ===')
    mock_resp = requests.get('http://localhost:8000/api/properties/search?mode=mock')
    mock_props = mock_resp.json()['data']
    print(f'Mock properties count: {len(mock_props)}')
    for prop in mock_props[:3]:
        print(f'- {prop.get("formattedAddress", "N/A")} - ${prop.get("price", "N/A")}')

    print('\n=== REAL MODE PROPERTIES ===')
    real_resp = requests.get('http://localhost:8000/api/properties/search?mode=real')
    real_props = real_resp.json()['data']
    print(f'Real properties count: {len(real_props)}')
    for prop in real_props[:3]:
        print(f'- {prop.get("formattedAddress", "N/A")} - ${prop.get("price", "N/A")}')

if __name__ == "__main__":
    test_properties() 