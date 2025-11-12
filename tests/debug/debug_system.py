#!/usr/bin/env python3
"""Debug do sistema para identificar problemas."""

import asyncio
import traceback
from app.utils.logging import setup_logging
from app.utils.container import DIContainer
from config.settings import get_settings


async def debug_system():
    """Debug passo a passo do sistema."""
    
    logger = setup_logging()
    logger.info('🔧 DEBUG: Testando inicialização passo a passo')
    
    try:
        # Passo 1: Settings
        logger.info('📋 Passo 1: Carregando settings...')
        settings = get_settings()
        logger.info('✅ Settings carregadas')
        logger.info(f'🔧 Ambiente: {settings.environment}')
        logger.info(f'🤖 Modelo: {settings.models.default_model}')
        
        # Passo 2: Container
        logger.info('📋 Passo 2: Criando container...')
        container = DIContainer()
        logger.info('✅ Container criado')
        
        # Passo 3: Setup do container
        logger.info('📋 Passo 3: Configurando container...')
        await container.setup(settings)
        logger.info('✅ Container configurado')
        
        # Passo 4: Import do SwarmOrchestrator
        logger.info('📋 Passo 4: Importando SwarmOrchestrator...')
        from app.orchestration.swarm import SwarmOrchestrator
        logger.info('✅ Import SwarmOrchestrator ok')
        
        # Passo 5: Obter orchestrator do container
        logger.info('📋 Passo 5: Obtendo orchestrator do container...')
        orchestrator = container.get(SwarmOrchestrator)
        logger.info('✅ SwarmOrchestrator obtido do container')
        
        # Passo 6: Verificar métodos
        logger.info('📋 Passo 6: Verificando métodos do orchestrator...')
        methods = [m for m in dir(orchestrator) if not m.startswith('_')]
        logger.info(f'📋 Métodos disponíveis: {methods[:10]}')
        
        # Passo 7: Testar process_stream
        logger.info('📋 Passo 7: Testando process_stream...')
        if hasattr(orchestrator, 'process_stream'):
            logger.info('✅ Método process_stream encontrado')
            
            # Testar com mensagem simples
            test_message = {
                "messages": [
                    {
                        "role": "user",
                        "content": "olá"
                    }
                ]
            }
            
            logger.info('🚀 Iniciando processo de streaming...')
            chunk_count = 0
            
            async for chunk in orchestrator.process_stream(test_message):
                chunk_count += 1
                logger.info(f'📊 Chunk {chunk_count}: {list(chunk.keys())}')
                
                if chunk_count > 10:  # Limitar para evitar loop infinito
                    logger.info('🛑 Limitando chunks para debug')
                    break
            
            logger.info(f'✅ Processamento concluído - {chunk_count} chunks')
            
        else:
            logger.error('❌ Método process_stream não encontrado')
            
    except Exception as e:
        logger.error(f'❌ Erro durante debug: {e}')
        logger.error(f'📋 Traceback: {traceback.format_exc()}')
    
    finally:
        logger.info('📋 Finalizando debug...')
        if 'container' in locals():
            await container.cleanup()
            logger.info('🔧 Cleanup concluído')


if __name__ == "__main__":
    asyncio.run(debug_system()) 