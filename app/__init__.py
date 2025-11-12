"""
Sistema Agêntico de IA para Busca e Agendamento de Imóveis

Arquitetura LangGraph-Swarm com PydanticAI para lógica de agentes.
"""

__version__ = "1.0.0"
__author__ = "Agentic Real Estate Team"

from .orchestration.swarm import SwarmOrchestrator
from .utils.logging import setup_logging, get_logger

__all__ = [
    "SwarmOrchestrator",
    "setup_logging", 
    "get_logger"
] 