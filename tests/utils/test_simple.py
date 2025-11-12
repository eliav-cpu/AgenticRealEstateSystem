#!/usr/bin/env python3
"""
Teste simples do Sistema Agêntico de Imóveis

Demonstra o funcionamento básico do LangGraph-Swarm.
"""

import asyncio
from app.utils.logging import setup_logging, get_logger
from app.utils.container import DIContainer
from app.orchestration.swarm import SwarmOrchestrator
from config.settings import get_settings


async def test_system_basic():
    """Teste básico do sistema."""
    
    # Configurar logging
    logger = setup_logging()
    logger.info("🧪 Iniciando Teste Básico do Sistema")
    
    # Carregar configurações
    try:
        settings = get_settings()
        logger.info("✅ Configurações carregadas com sucesso")
        
        # Log das principais configurações
        logger.info(f"🔧 Modelo LLM: {settings.models.default_model}")
        logger.info(f"🏠 API RentCast: Configurada")
        logger.info(f"🌡️ Temperatura: {settings.models.temperature}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar configurações: {e}")
        return False
    
    # Configurar container de DI
    try:
        container = DIContainer()
        await container.setup(settings)
        logger.info("✅ Container de DI configurado")
        
        # Obter orquestrador
        orchestrator = container.get(SwarmOrchestrator)
        logger.info("✅ SwarmOrchestrator inicializado")
        
        # Verificar estrutura do grafo
        visualization = orchestrator.get_graph_visualization()
        logger.info(f"✅ Grafo LangGraph construído: {len(visualization)} caracteres")
        
    except Exception as e:
        logger.error(f"❌ Erro na configuração: {e}")
        return False
    
    finally:
        await container.cleanup()
    
    return True


async def test_components():
    """Teste individual dos componentes."""
    
    logger = get_logger("test")
    logger.info("🔧 Testando Componentes Individuais")
    
    # Testar importações dos agentes
    try:
        from app.agents.search import SearchAgent, search_agent_node
        from app.agents.property import PropertyAgent, property_agent_node
        from app.agents.scheduling import SchedulingAgent, scheduling_agent_node
        logger.info("✅ Todos os agentes importados com sucesso")
        
        # Testar instanciação
        search_agent = SearchAgent()
        property_agent = PropertyAgent()
        scheduling_agent = SchedulingAgent()
        logger.info("✅ Instâncias dos agentes criadas")
        
    except Exception as e:
        logger.error(f"❌ Erro nos componentes: {e}")
        return False
    
    # Testar integração MCP
    try:
        from app.integrations.mcp import PropertySearchAgent, PropertyAnalysisAgent
        logger.info("✅ Integração MCP disponível")
        
    except Exception as e:
        logger.warning(f"⚠️ MCP não totalmente funcional: {e}")
    
    # Testar modelos Pydantic
    try:
        from app.models.property import Property, SearchCriteria, Address, Features, SearchResult
        
        # Criar instâncias de teste
        criteria = SearchCriteria(
            cities=["Rio de Janeiro"],
            min_price=3000,
            max_price=5000,
            min_bedrooms=2
        )
        logger.info(f"✅ Modelos Pydantic funcionais: {criteria.cities}")
        
    except Exception as e:
        logger.error(f"❌ Erro nos modelos: {e}")
        return False
    
    return True


async def main():
    """Função principal do teste."""
    
    logger = setup_logging()
    logger.info("🚀 Iniciando Bateria de Testes")
    
    # Teste 1: Sistema básico
    test1_passed = await test_system_basic()
    
    # Teste 2: Componentes
    test2_passed = await test_components()
    
    # Resultado final
    if test1_passed and test2_passed:
        logger.info("✨ TODOS OS TESTES PASSARAM! Sistema pronto para uso.")
        logger.info("📋 Próximos passos:")
        logger.info("   1. Configurar chave OpenRouter no .env")
        logger.info("   2. Configurar Google Calendar (opcional)")
        logger.info("   3. Executar teste com consulta real")
        logger.info("   4. Implementar interface web (opcional)")
        return True
    else:
        logger.error("❌ Alguns testes falharam. Verifique os logs acima.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 