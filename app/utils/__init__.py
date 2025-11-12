"""
Utilitários do sistema agêntico.
"""

from .logging import (
    setup_logging, 
    get_logger, 
    get_specialized_logger,
    log_agent_action, 
    log_handoff, 
    log_performance,
    log_api_call,
    log_error
)
from .container import DIContainer, DIScope, container

# Logfire imports (opcionais)
try:
    from .logfire_config import (
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

__all__ = [
    "setup_logging",
    "get_logger", 
    "get_specialized_logger",
    "log_agent_action",
    "log_handoff",
    "log_performance",
    "log_api_call",
    "log_error",
    "DIContainer",
    "DIScope",
    "container"
]

# Adicionar Logfire exports se disponível
if LOGFIRE_AVAILABLE:
    __all__.extend([
        "setup_logfire",
        "get_logfire_config",
        "AgentExecutionContext",
        "HandoffContext",
        "log_system_startup",
        "log_system_shutdown"
    ]) 