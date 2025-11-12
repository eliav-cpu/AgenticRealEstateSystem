#!/usr/bin/env python3
"""
Teste para verificar se os filtros de busca estão funcionando
"""

import requests
import json

def test_search_filters():
    """Testa diferentes combinações de filtros de busca"""
    
    base_url = "http://localhost:8000/api/properties/search"
    
    print("🧪 Testando filtros de busca...")
    
    # Teste 1: Busca sem filtros
    print("\n1. Busca sem filtros:")
    response = requests.get(f"{base_url}?mode=mock")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Retornou {len(data['data'])} propriedades")
        for prop in data['data']:
            print(f"   - {prop['propertyType']} | {prop['bedrooms']}Q | ${prop['price']}")
    else:
        print(f"   ❌ Erro: {response.status_code}")
    
    # Teste 2: Filtrar por tipo de propriedade
    print("\n2. Filtrar por tipo 'Apartment':")
    response = requests.get(f"{base_url}?mode=mock&propertyType=Apartment")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Retornou {len(data['data'])} propriedades")
        for prop in data['data']:
            print(f"   - {prop['propertyType']} | {prop['bedrooms']}Q | ${prop['price']}")
    else:
        print(f"   ❌ Erro: {response.status_code}")
    
    # Teste 3: Filtrar por quartos mínimos
    print("\n3. Filtrar por 3+ quartos:")
    response = requests.get(f"{base_url}?mode=mock&minBedrooms=3")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Retornou {len(data['data'])} propriedades")
        for prop in data['data']:
            print(f"   - {prop['propertyType']} | {prop['bedrooms']}Q | ${prop['price']}")
    else:
        print(f"   ❌ Erro: {response.status_code}")
    
    # Teste 4: Filtrar por preço máximo
    print("\n4. Filtrar por preço máximo $2000:")
    response = requests.get(f"{base_url}?mode=mock&maxPrice=2000")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Retornou {len(data['data'])} propriedades")
        for prop in data['data']:
            print(f"   - {prop['propertyType']} | {prop['bedrooms']}Q | ${prop['price']}")
    else:
        print(f"   ❌ Erro: {response.status_code}")
    
    # Teste 5: Filtros combinados
    print("\n5. Filtros combinados (Condo + 4+ quartos + $3000-5000):")
    response = requests.get(f"{base_url}?mode=mock&propertyType=Condo&minBedrooms=4&minPrice=3000&maxPrice=5000")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Retornou {len(data['data'])} propriedades")
        for prop in data['data']:
            print(f"   - {prop['propertyType']} | {prop['bedrooms']}Q | ${prop['price']}")
    else:
        print(f"   ❌ Erro: {response.status_code}")

if __name__ == "__main__":
    try:
        test_search_filters()
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Servidor não está rodando. Execute 'uv run python start_server.py' primeiro.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}") 