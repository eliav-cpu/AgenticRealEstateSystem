"""
Modelos de resposta para agentes do sistema.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    """Resposta padrão dos agentes."""
    success: bool = Field(..., description="Indica se a operação foi bem-sucedida")
    message: str = Field(..., description="Mensagem de resposta")
    data: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    
    # Informações do agente
    agent_name: str = Field(..., description="Nome do agente responsável")
    confidence: Optional[float] = Field(None, description="Nível de confiança da resposta")
    
    # Metadados de execução
    execution_time: Optional[float] = Field(None, description="Tempo de execução")
    tokens_used: Optional[int] = Field(None, description="Tokens utilizados")
    
    # Próximas ações sugeridas
    suggested_actions: List[str] = Field(default_factory=list, description="Ações sugeridas ao usuário")
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da resposta") 