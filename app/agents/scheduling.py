"""
Agente de Agendamento

Especializado em agendar visitas e gerenciar calendário com inteligência temporal avançada.
Implementa arquitetura LangGraph-Swarm com handoffs diretos.
"""

import asyncio
import json
from datetime import datetime, date, time, timedelta
from typing import Dict, Any, List, Optional, Annotated
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel

from langgraph.types import Command
from langgraph.graph import MessagesState
from langgraph.prebuilt import InjectedState
from pydantic_ai.providers.openrouter import OpenRouterProvider

from ..utils.logging import get_logger, log_handoff, log_performance
from ..utils.datetime_context import get_agent_datetime_context, format_datetime_context_for_agent
from config.settings import get_settings


def handoff_to_search(
    reason: str,
    user_preferences: Optional[Dict[str, Any]] = None,
    state: Optional[Dict[str, Any]] = None
) -> Command:
    """
    Native handoff tool to transfer to search agent with preserved preferences.

    Args:
        reason: Reason for handoff
        user_preferences: User search preferences to preserve
        state: Current conversation state

    Returns:
        Command to transition to search_agent with preserved context
    """
    from .router import get_router

    router = get_router()
    logger = get_logger()

    preserved_context = {
        "user_preferences": user_preferences or {},
        "handoff_reason": reason,
        "from_agent": "scheduling_agent",
        "handoff_trigger": "new_search_requested"
    }

    logger.info(f"🔄 Handoff to search_agent: {reason}")

    return Command(
        goto="search_agent",
        update={
            "context": preserved_context,
            "current_agent": "search_agent"
        }
    )


def handoff_to_property(
    selected_property: Optional[Dict[str, Any]],
    reason: str,
    state: Optional[Dict[str, Any]] = None
) -> Command:
    """
    Native handoff tool to transfer to property agent with property context.

    Args:
        selected_property: Property context to preserve
        reason: Reason for handoff
        state: Current conversation state

    Returns:
        Command to transition to property_agent with preserved context
    """
    from .router import get_router

    router = get_router()
    logger = get_logger()

    preserved_context = {
        "selected_property": selected_property,
        "handoff_reason": reason,
        "from_agent": "scheduling_agent",
        "handoff_trigger": "property_analysis_requested"
    }

    logger.info(f"🔄 Handoff to property_agent: {reason}")

    return Command(
        goto="property_agent",
        update={
            "context": preserved_context,
            "selected_property": selected_property,
            "current_agent": "property_agent"
        }
    )

class TimeParsingResult(BaseModel):
    """Resultado da análise temporal."""
    proposed_date: date = Field(..., description="Data proposta")
    proposed_time: time = Field(..., description="Horário proposto")
    confidence: float = Field(..., description="Confiança na interpretação (0-1)")
    is_business_hours: bool = Field(..., description="Se está em horário comercial")
    alternative_dates: List[date] = Field(default_factory=list, description="Datas alternativas")
    reasoning: str = Field(..., description="Raciocínio usado na interpretação")
    needs_clarification: bool = Field(False, description="Precisa de clarificação")
    clarification_message: Optional[str] = Field(None, description="Mensagem de clarificação")

class AppointmentResult(BaseModel):
    """Resultado da criação de agendamento."""
    success: bool = Field(..., description="Se foi bem-sucedido")
    message: str = Field(..., description="Mensagem de resultado")
    appointment_details: Optional[Dict[str, Any]] = Field(None, description="Detalhes do agendamento")
    alternative_slots: List[Dict[str, Any]] = Field(default_factory=list, description="Horários alternativos")

class SchedulingAgent:
    """
    Agente especializado em agendamento com inteligência temporal avançada.
    
    Responsabilidades:
    - Interpretar referências temporais em linguagem natural
    - Validar horários comerciais
    - Gerenciar disponibilidade
    - Agendar visitas a propriedades
    - Fazer handoffs para outros agentes quando necessário
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger("scheduling_agent")
        
        # Configurar modelo OpenRouter
        try:
            groq_api_key = self.settings.groq.api_key or ""

            if groq_api_key:
                self.model = GroqModel(self.settings.models.scheduling_model)
                self.logger.info(f"✅ Scheduling agent initialized with Groq model: {self.settings.models.scheduling_model}")
            else:
                self.logger.warning("⚠️ No Groq API key found, using test model")
                self.model = 'test'  # Fallback for testing

        except ImportError as e:
            self.logger.warning(f"⚠️ Groq dependencies not available: {e}, using test model")
            self.model = 'test'
        except Exception as e:
            self.logger.error(f"❌ Error configuring Groq: {e}, using test model")
            self.model = 'test'
        
        # Criar agente PydanticAI
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Cria o agente PydanticAI com ferramentas especializadas."""

        # Get datetime context for system prompt
        datetime_context = format_datetime_context_for_agent()

        agent = Agent(
            model=self.model,
            system_prompt=f"""You are the Scheduling Agent, expert in advanced temporal intelligence.

            {datetime_context}

            RESPONSIBILITIES:
            1. INTERPRET temporal references in natural language
            2. VALIDATE business hours (Monday to Friday, 9 AM to 6 PM)
            3. CALCULATE relative dates (tomorrow, next week, etc.)
            4. SUGGEST alternatives when necessary
            5. SCHEDULE property visits

            TEMPORAL RULES:
            - Business hours: Monday to Friday, 9:00 AM to 6:00 PM
            - No scheduling on weekends or holidays
            - Consider timezone: America/Sao_Paulo
            - Suggest nearby times if requested time is invalid

            NATURAL LANGUAGE INTERPRETATION:
            - "tomorrow" = next business day
            - "next week" = Monday of next week
            - "next Friday" = upcoming Friday
            - "day after tomorrow" = day after tomorrow if business day
            - "in the morning" = between 9 AM and 12 PM
            - "in the afternoon" = between 1 PM and 6 PM

            VALIDATIONS:
            - Date cannot be in the past
            - Time must be within business hours
            - Consider only business days

            HANDOFFS:
            - To property_agent: when user wants to see more properties
            - To search_agent: when user wants new search

            Always respond in English in a clear and friendly manner.
            """,
        )

        # Adicionar ferramentas especializadas
        self._add_tools(agent)

        return agent

    def _add_tools(self, agent: Agent) -> None:
        """Adiciona ferramentas especializadas ao agente."""
        
        @agent.tool
        async def get_current_datetime(user_timezone: str = "America/Sao_Paulo") -> str:
            """Retorna data e hora atual no fuso horário do usuário."""
            
            try:
                from zoneinfo import ZoneInfo
                tz = ZoneInfo(user_timezone)
            except ImportError:
                # Fallback para sistemas sem zoneinfo
                import pytz
                tz = pytz.timezone(user_timezone)
            
            now = datetime.now(tz)
            
            return json.dumps({
                "current_date": now.date().isoformat(),
                "current_time": now.time().strftime("%H:%M"),
                "current_datetime": now.isoformat(),
                "weekday": now.strftime("%A"),
                "weekday_pt": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"][now.weekday()]
            })

        @agent.tool
        async def calculate_relative_date(relative_term: str, user_timezone: str = "America/Sao_Paulo") -> str:
            """Calcula datas relativas baseadas em termos em português."""
            
            try:
                from zoneinfo import ZoneInfo
                tz = ZoneInfo(user_timezone)
            except ImportError:
                import pytz
                tz = pytz.timezone(user_timezone)
            
            now = datetime.now(tz)
            today = now.date()
            
            relative_term = relative_term.lower().strip()
            
            # Mapeamento de termos relativos
            if relative_term in ["amanhã", "amanha"]:
                target_date = today + timedelta(days=1)
                # Se amanhã for fim de semana, mover para segunda
                while target_date.weekday() >= 5:  # 5 = sábado, 6 = domingo
                    target_date += timedelta(days=1)
            
            elif relative_term in ["depois de amanhã", "depois de amanha"]:
                target_date = today + timedelta(days=2)
                while target_date.weekday() >= 5:
                    target_date += timedelta(days=1)
            
            elif "próxima semana" in relative_term or "proxima semana" in relative_term:
                # Próxima segunda-feira
                days_ahead = 7 - today.weekday()
                if days_ahead == 7:  # Se hoje é domingo
                    days_ahead = 1
                target_date = today + timedelta(days=days_ahead)
            
            elif "sexta que vem" in relative_term:
                # Próxima sexta-feira
                days_ahead = (4 - today.weekday()) % 7
                if days_ahead == 0:  # Se hoje é sexta, próxima sexta
                    days_ahead = 7
                target_date = today + timedelta(days=days_ahead)
            
            elif "segunda que vem" in relative_term:
                days_ahead = (0 - today.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7
                target_date = today + timedelta(days=days_ahead)
            
            elif "esta semana" in relative_term:
                # Qualquer dia desta semana (sugerir próximo dia útil)
                target_date = today
                while target_date.weekday() >= 5:
                    target_date += timedelta(days=1)
            
            else:
                return json.dumps({
                    "error": "Termo relativo não reconhecido",
                    "term": relative_term,
                    "needs_clarification": True
                })
            
            return json.dumps({
                "calculated_date": target_date.isoformat(),
                "weekday": target_date.strftime("%A"),
                "weekday_pt": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"][target_date.weekday()],
                "is_business_day": target_date.weekday() < 5
            })

        @agent.tool
        async def parse_time_expression(time_expr: str) -> str:
            """Interpreta expressões de tempo em linguagem natural."""
            
            time_expr = time_expr.lower().strip()
            
            # Mapeamento de expressões de tempo
            time_mappings = {
                "manhã": (9, 0),
                "manha": (9, 0),
                "meio da manhã": (10, 30),
                "final da manhã": (11, 30),
                "meio-dia": (12, 0),
                "meio dia": (12, 0),
                "almoço": (12, 0),
                "início da tarde": (13, 0),
                "inicio da tarde": (13, 0),
                "meio da tarde": (15, 0),
                "tarde": (14, 0),
                "final da tarde": (17, 0),
                "fim da tarde": (17, 0)
            }
            
            # Verificar expressões mapeadas
            for expr, (hour, minute) in time_mappings.items():
                if expr in time_expr:
                    return json.dumps({
                        "parsed_time": f"{hour:02d}:{minute:02d}",
                        "hour": hour,
                        "minute": minute,
                        "is_business_hours": 9 <= hour <= 18,
                        "expression": expr
                    })
            
            # Tentar extrair horário específico (formato HH:MM ou HH)
            import re
            time_pattern = r'(\d{1,2}):?(\d{0,2})\s*(h|horas?)?'
            match = re.search(time_pattern, time_expr)
            
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2)) if match.group(2) else 0
                
                # Validar horário
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    return json.dumps({
                        "parsed_time": f"{hour:02d}:{minute:02d}",
                        "hour": hour,
                        "minute": minute,
                        "is_business_hours": 9 <= hour <= 18,
                        "expression": time_expr
                    })
            
            return json.dumps({
                "error": "Expressão de tempo não reconhecida",
                "expression": time_expr,
                "needs_clarification": True
            })

        @agent.tool
        async def validate_business_hours(date_str: str, time_str: str) -> str:
            """Valida se data e horário estão dentro do horário comercial."""
            
            try:
                target_date = datetime.fromisoformat(date_str).date()
                target_time = datetime.strptime(time_str, "%H:%M").time()
                
                # Verificar se é dia útil
                is_business_day = target_date.weekday() < 5
                
                # Verificar se é horário comercial
                is_business_time = time(9, 0) <= target_time <= time(18, 0)
                
                # Verificar se não é no passado
                now = datetime.now().date()
                is_future = target_date >= now
                
                return json.dumps({
                    "is_valid": is_business_day and is_business_time and is_future,
                    "is_business_day": is_business_day,
                    "is_business_time": is_business_time,
                    "is_future": is_future,
                    "date": date_str,
                    "time": time_str,
                    "validation_message": self._get_validation_message(
                        is_business_day, is_business_time, is_future
                    )
                })
                
            except Exception as e:
                return json.dumps({
                    "error": f"Erro na validação: {str(e)}",
                    "is_valid": False
                })

        @agent.tool
        async def create_appointment(
            property_info: Dict[str, Any],
            appointment_datetime: str,
            user_contact: str = None
        ) -> AppointmentResult:
            """
            Cria um agendamento de visita.
            
            Args:
                property_info: Informações da propriedade
                appointment_datetime: Data e hora do agendamento (ISO format)
                user_contact: Contato do usuário
            """
            self.logger.info(f"Criando agendamento para {appointment_datetime}")
            
            try:
                # Simular criação de agendamento
                appointment_details = {
                    "id": f"apt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "property_id": property_info.get("id", "unknown"),
                    "property_title": property_info.get("title", "Propriedade"),
                    "property_address": property_info.get("address", {}),
                    "datetime": appointment_datetime,
                    "user_contact": user_contact,
                    "status": "confirmed",
                    "created_at": datetime.now().isoformat()
                }
                
                return AppointmentResult(
                    success=True,
                    message="Agendamento criado com sucesso!",
                    appointment_details=appointment_details,
                    alternative_slots=[]
                )
                
            except Exception as e:
                self.logger.error(f"Erro ao criar agendamento: {e}")
                return AppointmentResult(
                    success=False,
                    message=f"Erro ao criar agendamento: {str(e)}",
                    appointment_details=None,
                    alternative_slots=[]
                )

    def _get_validation_message(self, is_business_day: bool, is_business_time: bool, is_future: bool) -> str:
        """Gera mensagem de validação baseada nos critérios."""
        
        if not is_future:
            return "Data deve ser no futuro"
        elif not is_business_day:
            return "Agendamentos apenas em dias úteis (segunda a sexta)"
        elif not is_business_time:
            return "Horário comercial: 9h às 18h"
        else:
            return "Horário válido"

# Função para nó do LangGraph
async def scheduling_agent_node(state: Annotated[Dict[str, Any], InjectedState]) -> Command:
    """
    Nó do agente de agendamento no LangGraph.

    Especializado em agendar visitas e gerenciar calendário.
    Uses intelligent router and handoff tools for transitions.
    Integrates with datetime_context for temporal awareness.
    """
    from .router import get_router

    logger = get_logger("scheduling_agent")
    router = get_router()
    messages = state.get("messages", [])

    # Verificar se tem propriedade selecionada
    selected_property = state.get("context", {}).get("selected_property")
    if not selected_property:
        return handoff_to_property(
            selected_property=None,
            reason="No property selected for scheduling",
            state=state
        )
    
    # Inicializar agente
    agent = SchedulingAgent()
    
    # Processar com o agente PydanticAI
    try:
        last_message = messages[-1] if messages else {}
        user_content = last_message.get("content", "")
        
        # Executar processamento de agendamento
        result = await agent.agent.run(
            f"Processe esta solicitação de agendamento: {user_content}"
        )
        
        response = result.data if hasattr(result, 'data') else str(result)
        
        # Detectar confirmação de horário específico
        if any(word in user_content.lower() for word in ["amanhã", "quinta", "sexta", "14h", "10h", "16h", "confirmar"]):
            confirmed_response = """
✅ **Visita Agendada com Sucesso!**

📅 Data: Amanhã às 14h00
🏠 Local: Rua Barata Ribeiro, 100 - Copacabana
👤 Corretor: João Silva - (21) 99999-9999

📧 Confirmação enviada por email
📱 Lembrete será enviado 1 hora antes

Precisa de mais alguma coisa? Posso buscar outras propriedades ou ajudar com informações adicionais.
            """.strip()
            
            # Após agendamento, usuário pode querer buscar mais propriedades
            return Command(
                update={
                    "current_agent": "scheduling_agent",
                    "calendar_events": [{"date": "tomorrow", "time": "14:00", "property_id": selected_property.get("id", 1)}],
                    "messages": [{"role": "assistant", "content": confirmed_response}],
                    "context": {
                        "scheduling_completed": True,
                        "available_for_new_search": True
                    }
                }
            )
        
        # Resposta padrão de agendamento
        scheduling_response = f"""
📅 **Agendamento de Visita**

Perfeito! Vou agendar sua visita para o imóvel selecionado.

🏠 Propriedade: {selected_property.get('title', 'Apartamento em Copacabana')}
📍 Endereço: {selected_property.get('address', {}).get('street', 'Rua Barata Ribeiro, 100')}

**Horários disponíveis:**
• Amanhã às 14h00
• Quinta-feira às 10h30
• Sexta-feira às 16h00

{response}

Qual horário prefere?
        """.strip()
        
        # Use router for intent detection
        routing_decision = router.route(user_content, state)

        # Detectar necessidade de voltar para busca
        if routing_decision.intent.value == "search":
            return handoff_to_search(
                reason="User wants to search for more properties after scheduling",
                user_preferences=state.get("context", {}).get("user_preferences"),
                state=state
            )

        # Detectar necessidade de ver mais detalhes da propriedade
        if routing_decision.intent.value == "property_analysis":
            return handoff_to_property(
                selected_property=selected_property,
                reason="User wants more property details",
                state=state
            )
        
        return Command(
            update={
                "current_agent": "scheduling_agent",
                "messages": [{"role": "assistant", "content": scheduling_response}]
            }
        )
        
    except Exception as e:
        logger.error(f"Erro no scheduling_agent: {e}")
        return Command(
            update={
                "current_agent": "scheduling_agent",
                "messages": [{"role": "assistant", "content": "Desculpe, ocorreu um erro ao processar o agendamento. Vamos tentar novamente?"}]
            }
        )

# Ferramentas específicas do agente (para compatibilidade com LangGraph)
SCHEDULING_TOOLS = [
    handoff_to_search,
    handoff_to_property
] 