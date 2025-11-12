#!/usr/bin/env python3
"""
Script para testar as novas propriedades mock adicionadas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.api_config import APIConfig, RentCastAPI, APIMode

def test_new_mock_properties():
    """Testar as novas propriedades mock"""
    
    print("🏠 Testing New Mock Properties")
    print("=" * 50)
    
    # Configurar modo mock
    config = APIConfig()
    config.mode = APIMode.MOCK
    config.use_real_api = False
    
    api = RentCastAPI(config)
    
    # Buscar todas as propriedades
    properties = api.search_properties({})
    
    print(f"📦 Total Properties: {len(properties)}")
    print()
    
    # Mostrar resumo de cada propriedade
    for i, prop in enumerate(properties, 1):
        print(f"🏠 Property {i}:")
        print(f"   📍 Address: {prop['formattedAddress']}")
        print(f"   💰 Price: ${prop['price']:,}/month")
        print(f"   🛏️ Bedrooms: {prop['bedrooms']}")
        print(f"   🛁 Bathrooms: {prop['bathrooms']}")
        print(f"   📐 Size: {prop['squareFootage']:,} sq ft")
        print(f"   🏗️ Built: {prop['yearBuilt']}")
        print(f"   📋 MLS: {prop['mlsNumber']}")
        print(f"   👤 Agent: {prop['listingAgent']['name']}")
        print(f"   📞 Phone: {prop['listingAgent']['phone']}")
        print()
    
    # Testar filtros
    print("🔍 Testing Filters:")
    print("-" * 30)
    
    # Filtro por preço
    expensive = api.search_properties({"min_price": 5000})
    print(f"💎 Properties over $5,000: {len(expensive)}")
    for prop in expensive:
        print(f"   - {prop['formattedAddress']}: ${prop['price']:,}")
    
    print()
    
    # Filtro por quartos
    large_units = api.search_properties({"min_bedrooms": 3})
    print(f"🏠 Properties with 3+ bedrooms: {len(large_units)}")
    for prop in large_units:
        print(f"   - {prop['formattedAddress']}: {prop['bedrooms']} bed")
    
    print()
    
    # Propriedades únicas mencionadas pelo usuário
    target_addresses = [
        "15741 Sw 137th Ave, Apt 204, Miami, FL 33177",
        "1050 Brickell Ave, Apt 3504, Miami, FL 33131",
        "467 Nw 8th St, Apt 3, Miami, FL 33136",
        "4301 Nw 8th Ter, Apt 44, Miami, FL 33126"
    ]
    
    print("🎯 Checking Specific Properties:")
    print("-" * 35)
    
    for target in target_addresses:
        found = False
        for prop in properties:
            if prop['formattedAddress'] == target:
                print(f"✅ Found: {target}")
                print(f"   💰 ${prop['price']:,}/month | 🛏️ {prop['bedrooms']}bed | 🛁 {prop['bathrooms']}bath")
                found = True
                break
        if not found:
            print(f"❌ Missing: {target}")
    
    print()
    print("✅ Test Complete!")

if __name__ == "__main__":
    test_new_mock_properties() 