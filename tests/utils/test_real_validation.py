#!/usr/bin/env python3
"""
Teste Real de Validação - Sistema Agêntico de Imóveis

Primeira validação controlada com análise detalhada de resultados.
"""

import asyncio
import json
from app.utils.logging import setup_logging
from app.utils.container import DIContainer
from app.utils.api_monitor import api_monitor
from app.orchestration.swarm import SwarmOrchestrator
from config.settings import get_settings


async def test_real_estate_query():
    """Teste real com análise detalhada."""
    
    logger = setup_logging()
    logger.info("🎯 PRIMEIRA VALIDAÇÃO REAL - Sistema Agêntico de Imóveis")
    logger.info("=" * 70)
    
    # Status inicial da API
    usage = api_monitor.get_rentcast_usage()
    warning = api_monitor.get_warning_message()
    logger.info(f"📊 Status inicial API: {warning}")
    logger.info(f"📈 Calls disponíveis: {usage['remaining']}/50")
    logger.info("=" * 70)
    
    # Configurar sistema
    settings = get_settings()
    container = DIContainer()
    
    try:
        await container.setup(settings)
        orchestrator = container.get(SwarmOrchestrator)
        
        logger.info("✅ Sistema inicializado - pronto para consulta")
        logger.info("=" * 70)
        
        # Query de teste
        query = "Quero um apartamento de 2 quartos em Copacabana até R$ 4500 reais"
        logger.info(f"🏠 CONSULTA: {query}")
        logger.info("=" * 70)
        
        # Preparar mensagem
        message = {
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ]
        }
        
        logger.info("🚀 PROCESSANDO ATRAVÉS DO SISTEMA SWARM...")
        logger.info("-" * 70)
        
        # Processar com análise detalhada
        chunks_received = []
        agent_responses = []
        final_responses = []
        errors = []
        
        async for chunk in orchestrator.process_stream(message):
            chunks_received.append(chunk)
            
            logger.info(f"📦 CHUNK #{len(chunks_received)}:")
            logger.info(f"   Chaves: {list(chunk.keys())}")
            
            if chunk.get("agent"):
                agent_name = chunk.get("agent", "Unknown")
                agent_message = chunk.get("message", "")
                logger.info(f"🤖 AGENTE: {agent_name}")
                logger.info(f"💬 MENSAGEM: {agent_message[:200]}...")
                agent_responses.append({
                    "agent": agent_name,
                    "message": agent_message
                })
                
            elif chunk.get("final_response"):
                final_response = chunk.get("final_response", "")
                logger.info(f"✅ RESPOSTA FINAL:")
                logger.info(f"📝 CONTEÚDO: {final_response[:300]}...")
                final_responses.append(final_response)
                
            elif chunk.get("error"):
                error_msg = chunk.get("error")
                logger.error(f"❌ ERRO: {error_msg}")
                errors.append(error_msg)
                
            elif chunk.get("data"):
                data = chunk.get("data")
                logger.info(f"📊 DADOS: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                
            else:
                # Chunk genérico
                logger.info(f"📋 CHUNK GENÉRICO: {chunk}")
            
            logger.info("-" * 50)
        
        # Análise dos resultados
        logger.info("=" * 70)
        logger.info("📊 ANÁLISE DOS RESULTADOS:")
        logger.info(f"   🔢 Total de chunks: {len(chunks_received)}")
        logger.info(f"   🤖 Respostas de agentes: {len(agent_responses)}")
        logger.info(f"   ✅ Respostas finais: {len(final_responses)}")
        logger.info(f"   ❌ Erros: {len(errors)}")
        
        # Mostrar respostas dos agentes
        if agent_responses:
            logger.info("\n🤖 RESUMO DAS RESPOSTAS DOS AGENTES:")
            for i, resp in enumerate(agent_responses, 1):
                logger.info(f"   {i}. {resp['agent']}: {resp['message'][:100]}...")
        
        # Mostrar resposta final
        if final_responses:
            logger.info(f"\n✅ RESPOSTA FINAL COMPLETA:")
            for i, resp in enumerate(final_responses, 1):
                logger.info(f"   Resposta {i}: {resp[:500]}...")
        
        # Verificar se houve uso de API
        usage_after = api_monitor.get_rentcast_usage()
        api_used = usage_after['total_used'] > usage['total_used']
        
        logger.info(f"\n📊 STATUS FINAL DA API:")
        logger.info(f"   API usada: {'Sim' if api_used else 'Não (dados mock)'}")
        logger.info(f"   Calls restantes: {usage_after['remaining']}/50")
        logger.info(f"   Status: {api_monitor.get_warning_message()}")
        
        # Resultado
        success = len(chunks_received) > 0 and len(errors) == 0
        logger.info(f"\n🎯 RESULTADO DA VALIDAÇÃO:")
        logger.info(f"   Status: {'✅ SUCESSO' if success else '❌ FALHOU'}")
        logger.info(f"   Sistema operacional: {'Sim' if success else 'Não'}")
        logger.info(f"   Pronto para produção: {'Sim' if success else 'Não'}")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ ERRO DURANTE VALIDAÇÃO: {e}")
        import traceback
        logger.error(f"📋 TRACEBACK COMPLETO:\n{traceback.format_exc()}")
        return False
        
    finally:
        await container.cleanup()
        logger.info("🔧 Cleanup concluído")


async def main():
    """Execução principal."""
    
    logger = setup_logging()
    
    try:
        success = await test_real_estate_query()
        
        print("\n" + "=" * 70)
        if success:
            print("🎉 VALIDAÇÃO CONCLUÍDA COM SUCESSO!")
            print("✅ Sistema agêntico está operacional e pronto para uso!")
            print("📋 Próximos passos:")
            print("   - Configurar API OpenRouter para modelos reais")
            print("   - Testar com API RentCast real (1 call)")
            print("   - Implementar interface web (opcional)")
        else:
            print("❌ VALIDAÇÃO FALHOU!")
            print("📋 Verificar logs acima para detalhes do problema")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Erro fatal durante validação: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(main()) 