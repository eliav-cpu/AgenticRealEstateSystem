"""
Modelo de usuário para o sistema agêntico.
"""

from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """Perfil do usuário com preferências de busca."""
    id: Optional[int] = Field(None, description="ID único do usuário")
    email: str = Field(..., description="Email do usuário")
    full_name: str = Field(..., description="Nome completo")
    phone: Optional[str] = Field(None, description="Telefone")
    
    # Preferências de busca
    preferred_cities: List[str] = Field(default_factory=list, description="Cidades de interesse")
    preferred_neighborhoods: List[str] = Field(default_factory=list, description="Bairros de interesse")
    max_budget: Optional[Decimal] = Field(None, description="Orçamento máximo")
    
    # Histórico
    searches_count: int = Field(0, description="Número de buscas realizadas")
    appointments_count: int = Field(0, description="Número de agendamentos")
    
    # Metadados
    created_at: datetime = Field(default_factory=datetime.now, description="Data de criação")
    last_activity: datetime = Field(default_factory=datetime.now, description="Última atividade")
    is_active: bool = Field(True, description="Usuário ativo")


class ConversationMessage(BaseModel):
    """Modelo para mensagens de conversação."""
    id: Optional[int] = Field(None, description="ID único da mensagem")
    session_id: str = Field(..., description="ID da sessão de conversa")
    user_id: Optional[int] = Field(None, description="ID do usuário")
    
    # Conteúdo da mensagem
    role: str = Field(..., description="Papel do remetente (user/assistant/system)")
    content: str = Field(..., description="Conteúdo da mensagem")
    
    # Metadados
    agent_name: Optional[str] = Field(None, description="Nome do agente que respondeu")
    processing_time: Optional[float] = Field(None, description="Tempo de processamento em segundos")
    tokens_used: Optional[int] = Field(None, description="Tokens utilizados")
    cost: Optional[Decimal] = Field(None, description="Custo da operação")
    
    # Contexto adicional
    context: dict = Field(default_factory=dict, description="Contexto adicional")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="Data de criação") 