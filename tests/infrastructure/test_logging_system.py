#!/usr/bin/env python3
"""
Teste do Sistema de Logging com Logfire

Verifica se todos os componentes de observabilidade estão funcionando:
- Logging estruturado
- Logfire instrumentação
- Arquivos de log organizados
- Context managers
"""

import asyncio
import time
from app.utils.logging import (
    setup_logging,
    get_logger,
    get_specialized_logger,
    log_agent_action,
    log_handoff,
    log_performance,
    log_api_call,
    log_error
)

try:
    from app.utils.logfire_config import (
        setup_logfire,
        get_logfire_config,
        AgentExecutionContext,
        HandoffContext,
        log_system_startup,
        log_system_shutdown
    )
    LOGFIRE_AVAILABLE = True
except ImportError:
    LOGFIRE_AVAILABLE = False

from config.settings import get_settings


async def test_basic_logging():
    """Testar logging básico."""
    print("🧪 Testando logging básico...")
    
    # Configurar logging
    logger = setup_logging(enable_logfire=LOGFIRE_AVAILABLE)
    
    # Testes básicos
    logger.info("✅ Sistema de logging inicializado")
    logger.debug("🔍 Log de debug")
    logger.warning("⚠️ Log de warning")
    
    print("✅ Logging básico funcionando")


async def test_specialized_loggers():
    """Testar loggers especializados."""
    print("🧪 Testando loggers especializados...")
    
    # Testar cada tipo de logger
    loggers = ["agents", "handoffs", "performance", "api", "errors"]
    
    for log_type in loggers:
        logger = get_specialized_logger(log_type)
        logger.info(f"✅ Logger {log_type} funcionando")
    
    print("✅ Loggers especializados funcionando")


async def test_structured_logging():
    """Testar logging estruturado."""
    print("🧪 Testando logging estruturado...")
    
    # Log de ação de agente
    log_agent_action(
        agent_name="test_agent",
        action="test_execution",
        details={
            "test_parameter": "test_value",
            "duration": 1.5,
            "success": True
        }
    )
    
    # Log de handoff
    log_handoff(
        from_agent="search_agent",
        to_agent="property_agent",
        reason="user_wants_property_details",
        context={"property_id": "test_123"}
    )
    
    # Log de performance
    log_performance(
        operation="test_operation",
        duration=2.3,
        agent="test_agent",
        details={"complexity": "high"}
    )
    
    # Log de API call
    log_api_call(
        api_name="TestAPI",
        endpoint="/test",
        method="GET",
        status_code=200,
        duration=0.5
    )
    
    # Log de erro
    try:
        raise ValueError("Erro de teste")
    except Exception as e:
        log_error(
            error=e,
            context={"test": "error_logging"},
            agent="test_agent"
        )
    
    print("✅ Logging estruturado funcionando")


async def test_logfire_integration():
    """Testar integração com Logfire."""
    print("🧪 Testando integração Logfire...")
    
    if not LOGFIRE_AVAILABLE:
        print("⚠️ Logfire não disponível - pulando teste")
        return
    
    # Configurar Logfire
    success = setup_logfire()
    if not success:
        print("⚠️ Logfire não configurado - pulando teste")
        return
    
    config = get_logfire_config()
    print(f"🔥 Logfire disponível: {config.is_available()}")
    print(f"🔥 Logfire configurado: {config.configured}")
    
    # Testar context managers
    with AgentExecutionContext("test_agent", "test_action") as span:
        time.sleep(0.1)  # Simular trabalho
        print("🔥 AgentExecutionContext funcionando")
    
    with HandoffContext("agent_a", "agent_b", "test_handoff") as span:
        time.sleep(0.1)  # Simular trabalho
        print("🔥 HandoffContext funcionando")
    
    # Testar logs estruturados do Logfire
    config.log_agent_execution(
        agent_name="test_agent",
        action="test_action",
        input_data={"test": "input"},
        output_data={"test": "output"},
        duration=0.5
    )
    
    config.log_handoff(
        from_agent="agent_a",
        to_agent="agent_b",
        reason="test_reason"
    )
    
    config.log_api_call(
        api_name="TestAPI",
        endpoint="/test",
        method="POST",
        status_code=201,
        duration=0.3
    )
    
    print("✅ Integração Logfire funcionando")


async def test_swarm_orchestrator_logging():
    """Testar logging do SwarmOrchestrator."""
    print("🧪 Testando logging do SwarmOrchestrator...")
    
    try:
        from app.orchestration.swarm import get_swarm_orchestrator
        
        # Obter orchestrator (isso deve gerar logs)
        orchestrator = get_swarm_orchestrator()
        
        # Testar processamento de mensagem simples
        test_message = {
            "messages": [{"role": "user", "content": "Hello test"}],
            "context": {"data_mode": "mock"},
            "session_id": "test_session"
        }
        
        print("🤖 Testando processamento de mensagem...")
        result = await orchestrator.process_message(test_message)
        print(f"✅ Mensagem processada: {len(str(result))} chars")
        
    except Exception as e:
        print(f"⚠️ Erro no teste do SwarmOrchestrator: {e}")
        log_error(e, context={"test": "swarm_orchestrator"})


async def test_log_files():
    """Verificar se arquivos de log foram criados."""
    print("🧪 Verificando arquivos de log...")
    
    import os
    from pathlib import Path
    
    log_dir = Path("logs")
    if not log_dir.exists():
        print("⚠️ Pasta logs não existe")
        return
    
    expected_files = [
        "app.log",
        "agents.log", 
        "handoffs.log",
        "performance.log",
        "api.log",
        "errors.log"
    ]
    
    for log_file in expected_files:
        file_path = log_dir / log_file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {log_file}: {size} bytes")
        else:
            print(f"⚠️ {log_file}: não encontrado")
    
    print("✅ Verificação de arquivos concluída")


async def main():
    """Executar todos os testes."""
    print("🚀 Iniciando testes do sistema de logging...")
    print("=" * 60)
    
    if LOGFIRE_AVAILABLE:
        log_system_startup()
    
    # Executar testes
    await test_basic_logging()
    print()
    
    await test_specialized_loggers()
    print()
    
    await test_structured_logging()
    print()
    
    await test_logfire_integration()
    print()
    
    await test_swarm_orchestrator_logging()
    print()
    
    await test_log_files()
    print()
    
    if LOGFIRE_AVAILABLE:
        log_system_shutdown()
    
    print("=" * 60)
    print("🎉 Testes do sistema de logging concluídos!")
    print()
    print("📁 Verifique os arquivos de log na pasta 'logs/'")
    if LOGFIRE_AVAILABLE:
        print("🔥 Dados também enviados para Logfire (se configurado)")
    else:
        print("⚠️ Logfire não disponível - apenas logs locais")


if __name__ == "__main__":
    asyncio.run(main())