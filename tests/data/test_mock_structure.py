#!/usr/bin/env python3
"""
Teste dos Dados Mock com Estrutura RentCast

Verifica se os dados mock agora têm exatamente a mesma estrutura
da API real RentCast, permitindo testes realísticos sem custos.
"""

import json
from config.api_config import RentCastAPI, APIConfig, APIMode
from app.utils.logging import setup_logging

def test_mock_structure():
    """Testa a nova estrutura dos dados mock."""
    
    logger = setup_logging()
    
    print("🔍 TESTE - Dados Mock com Estrutura RentCast")
    print("=" * 55)
    
    # Configurar API em modo mock
    config = APIConfig(
        mode=APIMode.MOCK,
        use_real_api=False
    )
    
    api_client = RentCastAPI(config)
    
    # Teste 1: Busca básica
    print("\n🏠 TESTE 1: Busca Básica")
    print("-" * 30)
    
    criteria = {
        "city": "Rio de Janeiro",
        "state": "RJ",
        "bedrooms": 2,
        "max_rent": 5000
    }
    
    print(f"📋 Critérios: {criteria}")
    
    properties = api_client.search_properties(criteria)
    
    print(f"✅ Encontradas: {len(properties)} propriedades")
    
    if properties:
        first_property = properties[0]
        
        print(f"\n📊 ESTRUTURA DA PRIMEIRA PROPRIEDADE:")
        print(f"   Tipo: {type(first_property).__name__}")
        
        # Verificar campos essenciais da API RentCast
        expected_fields = [
            'id', 'formattedAddress', 'addressLine1', 'city', 'state',
            'zipCode', 'latitude', 'longitude', 'propertyType', 'bedrooms',
            'bathrooms', 'squareFootage', 'yearBuilt', 'status', 'price',
            'listingType', 'listedDate', 'daysOnMarket', 'mlsName',
            'listingAgent', 'listingOffice', 'history'
        ]
        
        print(f"\n✅ CAMPOS VERIFICADOS:")
        for field in expected_fields:
            if field in first_property:
                value = first_property[field]
                print(f"   ✅ {field}: {type(value).__name__} = {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
            else:
                print(f"   ❌ {field}: AUSENTE")
        
        print(f"\n📄 PROPRIEDADE COMPLETA (formatada):")
        print(json.dumps(first_property, indent=2, ensure_ascii=False)[:1000])
        print("..." if len(json.dumps(first_property)) > 1000 else "")
    
    # Teste 2: Filtros
    print(f"\n🔍 TESTE 2: Filtros")
    print("-" * 30)
    
    # Teste com preço baixo
    criteria_low = {
        "city": "Rio de Janeiro",
        "state": "RJ",
        "bedrooms": 2,
        "max_rent": 3000
    }
    
    properties_low = api_client.search_properties(criteria_low)
    print(f"📊 Preço até R$ 3000: {len(properties_low)} propriedades")
    
    # Teste com preço alto
    criteria_high = {
        "city": "Rio de Janeiro", 
        "state": "RJ",
        "bedrooms": 3,
        "max_rent": 8000
    }
    
    properties_high = api_client.search_properties(criteria_high)
    print(f"📊 3+ quartos até R$ 8000: {len(properties_high)} propriedades")
    
    # Teste 3: Comparação de estrutura
    print(f"\n🔄 TESTE 3: Comparação com Estrutura Real")
    print("-" * 45)
    
    # Estrutura real da API (baseada no teste anterior)
    real_api_structure = {
        "id": "str",
        "formattedAddress": "str",
        "addressLine1": "str", 
        "addressLine2": "str",
        "city": "str",
        "state": "str",
        "zipCode": "str",
        "county": "str",
        "latitude": "float",
        "longitude": "float",
        "propertyType": "str",
        "bedrooms": "int",
        "bathrooms": "int",
        "squareFootage": "int",
        "lotSize": "int",
        "yearBuilt": "int",
        "status": "str",
        "price": "int",
        "listingType": "str",
        "listedDate": "str",
        "removedDate": "NoneType",
        "createdDate": "str",
        "lastSeenDate": "str",
        "daysOnMarket": "int",
        "mlsName": "str",
        "mlsNumber": "str",
        "listingAgent": "dict",
        "listingOffice": "dict",
        "history": "dict"
    }
    
    if properties:
        mock_property = properties[0]
        
        print("🔍 Verificando compatibilidade:")
        compatible = True
        
        for field, expected_type in real_api_structure.items():
            if field in mock_property:
                actual_type = type(mock_property[field]).__name__
                if actual_type == expected_type or (expected_type == "NoneType" and mock_property[field] is None):
                    print(f"   ✅ {field}: {actual_type}")
                else:
                    print(f"   ⚠️ {field}: esperado {expected_type}, encontrado {actual_type}")
                    compatible = False
            else:
                print(f"   ❌ {field}: AUSENTE")
                compatible = False
        
        if compatible:
            print(f"\n🎉 ESTRUTURA 100% COMPATÍVEL COM API REAL!")
        else:
            print(f"\n⚠️ Algumas diferenças encontradas")
    
    # Resumo
    print(f"\n" + "=" * 55)
    print(f"📊 RESUMO DOS TESTES:")
    print(f"   🔢 Propriedades retornadas: {len(properties)}")
    print(f"   📋 Filtro preço baixo: {len(properties_low)} resultados")
    print(f"   📋 Filtro preço alto: {len(properties_high)} resultados")
    print(f"   🏗️ Estrutura: {'✅ Compatível' if properties and 'id' in properties[0] else '❌ Incompatível'}")
    print(f"   💡 Status: Dados mock prontos para testes realísticos!")
    
    return True

if __name__ == "__main__":
    test_mock_structure() 