"""
Teste simples para verificar a integração com RentCast API.
"""

import asyncio
from app.integrations.mcp import mcp_server
from app.models.property import SearchCriteria, PropertyType, PropertyStatus
from decimal import Decimal


async def test_rentcast_integration():
    """Testa a integração com RentCast API."""
    
    print("🔍 Testando integração RentCast API...")
    print(f"Chave API configurada: 01e1101b77c54f1b8e804ba212a4ccfc")
    
    # Criar critérios de busca simples
    criteria = SearchCriteria(
        cities=["Miami"],  # RentCast funciona melhor com cidades americanas
        property_types=[PropertyType.APARTMENT],
        status=[PropertyStatus.FOR_RENT],
        max_price=Decimal("3000"),
        min_bedrooms=2,
        limit=5
    )
    
    print(f"\n📋 Critérios de busca:")
    print(f"- Cidade: {criteria.cities}")
    print(f"- Tipo: {criteria.property_types}")
    print(f"- Status: {criteria.status}")
    print(f"- Preço máximo: ${criteria.max_price}")
    print(f"- Quartos mínimos: {criteria.min_bedrooms}")
    
    try:
        # Executar busca via MCP
        print(f"\n🚀 Executando busca via MCP...")
        properties = await mcp_server.search_properties(criteria)
        
        print(f"\n✅ Busca concluída!")
        print(f"📊 Resultados: {len(properties)} propriedades encontradas")
        
        # Mostrar primeiras propriedades
        for i, prop in enumerate(properties[:3], 1):
            print(f"\n🏠 Propriedade {i}:")
            print(f"   Título: {prop.title}")
            print(f"   Preço: {prop.price_formatted}")
            print(f"   Localização: {prop.address.neighborhood}, {prop.address.city}")
            print(f"   Quartos: {prop.features.bedrooms}")
            print(f"   Fonte: {prop.source}")
            print(f"   Score: {prop.relevance_score:.2f}")
        
        # Estatísticas por fonte
        sources = {}
        for prop in properties:
            sources[prop.source] = sources.get(prop.source, 0) + 1
        
        print(f"\n📈 Estatísticas por fonte:")
        for source, count in sources.items():
            print(f"   {source}: {count} propriedades")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {str(e)}")
        print(f"Tipo do erro: {type(e).__name__}")
        return False


async def test_mock_only():
    """Testa apenas o cliente Mock para comparação."""
    
    print("\n" + "="*50)
    print("🧪 Testando apenas cliente Mock...")
    
    criteria = SearchCriteria(
        neighborhoods=["Copacabana", "Ipanema"],
        property_types=[PropertyType.APARTMENT],
        status=[PropertyStatus.FOR_RENT],
        max_price=Decimal("5000"),
        min_bedrooms=2,
        limit=3
    )
    
    try:
        properties = await mcp_server.search_properties(criteria)
        
        print(f"✅ Mock funcionando: {len(properties)} propriedades")
        for prop in properties[:2]:
            print(f"   • {prop.title} - {prop.price_formatted}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no Mock: {str(e)}")
        return False


if __name__ == "__main__":
    print("🏠 Teste de Integração - Agentic Real Estate")
    print("=" * 50)
    
    # Executar testes
    asyncio.run(test_rentcast_integration())
    asyncio.run(test_mock_only())
    
    print("\n🎉 Testes concluídos!")
    print("\nPróximos passos:")
    print("1. Se RentCast funcionou: ✅ API integrada com sucesso!")
    print("2. Se houve erro: Verificar logs para debugging")
    print("3. Testar com diferentes critérios de busca")
    print("4. Executar sistema completo com: python main.py") 