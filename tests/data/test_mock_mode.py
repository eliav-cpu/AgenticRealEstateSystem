#!/usr/bin/env python3
"""
Teste Rápido - Modo Mock (Seguro)

Demonstra o sistema funcionando com dados mock.
Não usa nenhuma call da API RentCast.
"""

import asyncio
from app.utils.logging import setup_logging
from app.utils.container import DIContainer
from app.utils.api_monitor import api_monitor
from app.orchestration.swarm import SwarmOrchestrator
from config.settings import get_settings
from config.api_config import api_config, APIMode


async def test_mock_system():
    """Teste completo em modo mock."""
    
    logger = setup_logging()
    logger.info("🚀 TESTE SISTEMA MOCK - Seguro e Ilimitado")
    print("\n" + "=" * 60)
    print("📦 MODO MOCK ATIVO - SEM USO DA API")
    print("=" * 60)
    
    # Garantir modo mock
    api_config.mode = APIMode.MOCK
    api_config.use_real_api = False
    
    # Status inicial
    usage = api_monitor.get_rentcast_usage()
    print(f"📊 Status API: {api_monitor.get_warning_message()}")
    
    # Configurar sistema
    settings = get_settings()
    container = DIContainer()
    
    try:
        await container.setup(settings)
        orchestrator = container.get(SwarmOrchestrator)
        
        # Query de teste
        query = "Quero um apartamento de 3 quartos em Botafogo até R$ 5500 reais"
        print(f"\n🏠 CONSULTA: {query}")
        print("-" * 60)
        
        # Preparar mensagem
        message = {
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ]
        }
        
        # Processar e mostrar resultados
        agent_responses = {}
        chunk_count = 0
        
        async for chunk in orchestrator.process_stream(message):
            chunk_count += 1
            
            # Capturar respostas dos agentes
            for agent_name in ["search_agent", "property_agent", "scheduling_agent"]:
                if agent_name in chunk:
                    agent_data = chunk[agent_name]
                    messages = agent_data.get("messages", [])
                    if messages:
                        content = messages[-1].get("content", "")
                        agent_responses[agent_name] = content
                        
                        print(f"\n🤖 {agent_name.replace('_', ' ').upper()}:")
                        print(f"📝 {content}")
                    break
        
        # Verificar que não usou API
        usage_after = api_monitor.get_rentcast_usage()
        api_used = usage_after['total_used'] > usage['total_used']
        
        print("\n" + "=" * 60)
        print("📊 RESULTADOS DO TESTE:")
        print(f"   ✅ Chunks processados: {chunk_count}")
        print(f"   🤖 Respostas de agentes: {len(agent_responses)}")
        print(f"   📦 Fonte dos dados: Dados Mock")
        print(f"   🌐 API RentCast usada: {'Sim' if api_used else 'Não'}")
        print(f"   📈 Calls preservadas: {usage_after['remaining']}/50")
        
        # Verificar se resposta menciona fonte correta
        if "search_agent" in agent_responses:
            if "Dados Demonstrativos" in agent_responses["search_agent"]:
                print("   ✅ Fonte corretamente identificada como Mock")
            else:
                print("   ⚠️ Fonte não identificada claramente")
        
        success = chunk_count > 0 and len(agent_responses) >= 2 and not api_used
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 TESTE MOCK - SUCESSO COMPLETO!")
            print("✅ Sistema funcionando perfeitamente")
            print("✅ Dados mock integrados corretamente")
            print("✅ API RentCast totalmente preservada")
            print("✅ Pronto para testes ilimitados em modo mock")
        else:
            print("❌ TESTE MOCK FALHOU")
            print("📋 Verificar logs para detalhes")
            
        print("=" * 60)
        return success
        
    except Exception as e:
        logger.error(f"❌ Erro durante teste mock: {e}")
        print(f"\n❌ Erro: {e}")
        return False
        
    finally:
        await container.cleanup()


if __name__ == "__main__":
    asyncio.run(test_mock_system()) 