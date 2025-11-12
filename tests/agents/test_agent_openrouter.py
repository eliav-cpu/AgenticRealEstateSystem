#!/usr/bin/env python3
"""
Teste simples para verificar se o OpenRouter está sendo usado corretamente
"""

import asyncio
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

from app.orchestration.swarm import create_swarm_graph
from app.utils.logging import get_logger

logger = get_logger("test_agent")

async def test_property_agent():
    """Testa o agente de propriedades com OpenRouter"""
    
    # Verificar se a chave OpenRouter existe
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_key:
        logger.error("❌ OPENROUTER_API_KEY não encontrada no .env")
        return
    
    logger.info(f"✅ OpenRouter key found: {openrouter_key[:10]}...")
    
    # Criar o grafo Swarm
    graph = create_swarm_graph()
    
    # Contexto de teste com uma propriedade mock
    property_context = {
        "id": "test-123",
        "formattedAddress": "123 Test Street, Miami, FL 33126",
        "price": 2500,
        "bedrooms": 2,
        "bathrooms": 1,
        "squareFootage": 800,
        "yearBuilt": 2020,
        "propertyType": "Apartment"
    }
    
    # Estado inicial
    initial_state = {
        "messages": [{"role": "user", "content": "How much is the rent for this property?"}],
        "context": {
            "property_context": property_context,
            "data_mode": "mock"
        }
    }
    
    logger.info("🚀 Testando agente de propriedades...")
    
    try:
        # Executar o grafo
        result = await graph.ainvoke(initial_state)
        
        # Verificar resultado
        if result and "messages" in result:
            last_message = result["messages"][-1]
            response_content = getattr(last_message, 'content', str(last_message))
            
            logger.info(f"✅ Resposta recebida ({len(response_content)} chars):")
            logger.info(f"📝 Conteúdo: {response_content[:200]}...")
            
            # Verificar se não é uma resposta de fallback genérica
            if "I apologize" in response_content or "fallback" in response_content.lower():
                logger.warning("⚠️ Resposta parece ser fallback")
            else:
                logger.info("✅ Resposta parece ser do OpenRouter!")
                
        else:
            logger.error("❌ Nenhuma mensagem retornada")
            
    except Exception as e:
        logger.error(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

async def test_search_agent():
    """Testa o agente de busca com OpenRouter"""
    
    logger.info("🔍 Testando agente de busca...")
    
    # Criar o grafo Swarm
    graph = create_swarm_graph()
    
    # Estado inicial para busca
    initial_state = {
        "messages": [{"role": "user", "content": "I'm looking for a 2-bedroom apartment in Miami under $3000"}],
        "context": {
            "property_context": {},
            "data_mode": "mock"
        }
    }
    
    try:
        # Executar o grafo
        result = await graph.ainvoke(initial_state)
        
        # Verificar resultado
        if result and "messages" in result:
            last_message = result["messages"][-1]
            response_content = getattr(last_message, 'content', str(last_message))
            
            logger.info(f"✅ Resposta de busca recebida ({len(response_content)} chars):")
            logger.info(f"📝 Conteúdo: {response_content[:200]}...")
            
        else:
            logger.error("❌ Nenhuma mensagem retornada para busca")
            
    except Exception as e:
        logger.error(f"❌ Erro durante teste de busca: {e}")

async def main():
    """Função principal de teste"""
    logger.info("🧪 Iniciando testes do sistema agêntico...")
    
    # Teste 1: Agente de propriedades
    await test_property_agent()
    
    print("\n" + "="*50 + "\n")
    
    # Teste 2: Agente de busca
    await test_search_agent()
    
    logger.info("✅ Testes concluídos!")

if __name__ == "__main__":
    asyncio.run(main()) 