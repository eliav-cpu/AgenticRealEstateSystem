#!/usr/bin/env python3
"""Debug simples para identificar problema específico."""

import asyncio
from app.utils.logging import setup_logging
from app.utils.container import DIContainer
from app.orchestration.swarm import SwarmOrchestrator
from config.settings import get_settings


async def debug_minimal():
    """Debug mínimo para identificar problema."""
    
    logger = setup_logging()
    logger.info("🔧 DEBUG MÍNIMO")
    
    try:
        # Configurar
        settings = get_settings()
        container = DIContainer()
        await container.setup(settings)
        
        # Obter orchestrator
        orchestrator = container.get(SwarmOrchestrator)
        logger.info("✅ Orchestrator obtido")
        
        # Preparar mensagem mínima
        message = {"messages": [{"role": "user", "content": "olá"}]}
        logger.info("📨 Mensagem preparada")
        
        # Testar astream
        logger.info("🚀 Iniciando astream...")
        
        chunk_count = 0
        async for chunk in orchestrator.process_stream(message):
            chunk_count += 1
            logger.info(f"📦 CHUNK #{chunk_count}: {chunk}")
            
            if chunk_count >= 5:  # Limitar a 5 chunks
                logger.info("🛑 Limitando chunks para debug")
                break
        
        if chunk_count > 0:
            logger.info(f"✅ {chunk_count} chunks recebidos com sucesso!")
        else:
            logger.warning("⚠️ Nenhum chunk foi recebido")
        
    except Exception as e:
        logger.error(f"❌ ERRO: {e}")
        import traceback
        logger.error(f"📋 TRACEBACK:\n{traceback.format_exc()}")
        
    finally:
        if 'container' in locals():
            await container.cleanup()
            logger.info("🔧 Cleanup ok")


if __name__ == "__main__":
    asyncio.run(debug_minimal()) 