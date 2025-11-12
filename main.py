"""
Sistema Agêntico de IA para Busca e Agendamento de Imóveis

Ponto de entrada principal do sistema usando arquitetura LangGraph-Swarm.
"""

import asyncio
import logging
from typing import Dict, Any

from app.utils.logging import setup_logging
from app.utils.container import DIContainer
from app.utils.logfire_config import setup_logfire, log_system_startup, log_system_shutdown
from app.utils.langsmith_config import setup_langsmith
from app.orchestration.swarm import SwarmOrchestrator
from config.settings import get_settings


async def main() -> None:
    """Ponto de entrada principal da aplicação."""
    
    # Configurar logging
    logger = setup_logging()
    logger.info("STARTUP: Iniciando Sistema Agêntico de Imóveis")
    
    # Carregar configurações
    settings = get_settings()
    
    # Configurar Logfire para observabilidade
    logfire_success = setup_logfire()
    if logfire_success:
        logger.info("SUCCESS: Logfire configurado para observabilidade")
        log_system_startup()
    else:
        logger.warning("WARNING: Logfire não configurado - continuando sem observabilidade avançada")
    
    # Configurar LangSmith para tracing LangGraph
    langsmith_success = setup_langsmith()
    if langsmith_success:
        logger.info("SUCCESS: LangSmith configurado para tracing LangGraph")
    else:
        logger.warning("WARNING: LangSmith não configurado - continuando sem tracing LangGraph")
    
    # Configurar container de DI
    container = DIContainer()
    await container.setup(settings)
    
    try:
        # Inicializar orquestrador swarm
        orchestrator = container.get(SwarmOrchestrator)
        
        # Exemplo de uso
        initial_message = {
            "messages": [
                {
                    "role": "user", 
                    "content": "Olá! Estou procurando um apartamento de 2 quartos em Copacabana até R$ 4000."
                }
            ]
        }
        
        logger.info("PROCESS: Processando solicitação inicial...")
        
        # Processar com streaming e mostrar resultados detalhados
        chunk_count = 0
        async for chunk in orchestrator.process_stream(initial_message):
            chunk_count += 1
            
            # Verificar se é resposta de um agente específico
            for agent_name in ["search_agent", "property_agent", "scheduling_agent"]:
                if agent_name in chunk:
                    agent_data = chunk[agent_name]
                    messages = agent_data.get("messages", [])
                    if messages:
                        content = messages[-1].get("content", "")
                        logger.info(f"AGENT {agent_name.upper()}: {content[:150]}...")
                    break
            else:
                # Chunk genérico
                logger.info(f"CHUNK #{chunk_count}: {list(chunk.keys())}")
        
        logger.info(f"SUCCESS: Sistema processou {chunk_count} chunks com sucesso!")
        logger.info("READY: Sistema Agêntico de Imóveis está operacional e pronto!")
        
    except Exception as e:
        logger.error(f"ERROR: Erro durante inicialização: {e}")
        raise
    
    finally:
        # Log system shutdown
        log_system_shutdown()
        logger.info("SHUTDOWN: Sistema finalizado")
        await container.cleanup()


if __name__ == "__main__":
    asyncio.run(main()) 