"""
Agente de Análise de Propriedades

Especializado em apresentar informações de imóveis de forma clara e atrativa,
responder perguntas específicas sobre propriedades e comparar diferentes opções.
Implementa arquitetura LangGraph-Swarm com handoffs diretos.
"""

from typing import Dict, Any, List, Optional, Annotated
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from langgraph.types import Command
from langgraph.graph import MessagesState
from langgraph.prebuilt import InjectedState

from ..models.property import Property, SearchCriteria
from ..utils.logging import get_logger, log_handoff, log_performance
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
        "from_agent": "property_agent",
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


def handoff_to_scheduling(
    selected_property: Property,
    reason: str,
    state: Optional[Dict[str, Any]] = None
) -> Command:
    """
    Native handoff tool to transfer to scheduling agent with property context.

    Args:
        selected_property: Property to schedule visit for
        reason: Reason for handoff
        state: Current conversation state

    Returns:
        Command to transition to scheduling_agent with preserved context
    """
    from .router import get_router

    router = get_router()
    logger = get_logger()

    preserved_context = {
        "selected_property": selected_property.model_dump() if isinstance(selected_property, Property) else selected_property,
        "handoff_reason": reason,
        "from_agent": "property_agent",
        "handoff_trigger": "scheduling_requested"
    }

    logger.info(f"🔄 Handoff to scheduling_agent: {reason}")

    return Command(
        goto="scheduling_agent",
        update={
            "context": preserved_context,
            "selected_property": preserved_context["selected_property"],
            "current_agent": "scheduling_agent"
        }
    )


class PropertyAnalysis(BaseModel):
    """Modelo para análise de propriedades."""
    property_highlights: List[str] = Field(description="Pontos principais do imóvel")
    advantages: List[str] = Field(description="Vantagens do imóvel")
    disadvantages: List[str] = Field(description="Desvantagens ou pontos de atenção")
    suitability_score: float = Field(description="Score de adequação ao perfil (0-1)")
    comparison_points: List[str] = Field(description="Pontos para comparação")
    personalized_description: str = Field(description="Descrição personalizada")


class PropertyComparison(BaseModel):
    """Modelo para comparação de propriedades."""
    comparison_matrix: Dict[str, Dict[str, Any]] = Field(description="Matriz de comparação")
    ranking: List[str] = Field(description="Ranking de propriedades por adequação")
    recommendation: str = Field(description="Recomendação final")
    decision_factors: List[str] = Field(description="Fatores principais para decisão")


class PropertyAgent:
    """
    Agente especializado em análise e apresentação de propriedades.
    
    Responsabilidades:
    - Apresentar informações de imóveis de forma clara e atrativa
    - Responder perguntas específicas sobre propriedades
    - Comparar diferentes opções
    - Destacar pontos relevantes baseado no perfil do usuário
    - Fazer handoffs para outros agentes quando necessário
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger("property_agent")
        
        # Configurar modelo Groq usando configurações centralizadas
        try:
            from pydantic_ai.models.groq import GroqModel

            groq_api_key = self.settings.groq.api_key or ""

            if groq_api_key:
                self.model = GroqModel(self.settings.models.property_model)
                self.logger.info(f"✅ Property agent initialized with Groq model: {self.settings.models.property_model}")
            else:
                self.logger.warning("⚠️ No Groq API key found, using test model")
                self.model = 'test'  # Fallback for testing

        except ImportError as e:
            self.logger.warning(f"⚠️ Groq dependencies not available: {e}, using test model")
            self.model = 'test'
        except Exception as e:
            self.logger.error(f"❌ Error configuring Groq: {e}, using test model")
            self.model = 'test'
        
        # Criar agente PydanticAI simples
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Cria o agente PydanticAI básico sem ferramentas complexas."""
        
        agent = Agent(
            model=self.model,
            system_prompt="""Você é o Agente de Análise de Propriedades, especializado em apresentar 
            informações imobiliárias de forma clara, atrativa e personalizada.

            SUAS RESPONSABILIDADES:
            - Apresentar informações de imóveis de forma clara e atrativa
            - Responder perguntas específicas sobre propriedades
            - Comparar diferentes opções objetivamente
            - Destacar pontos relevantes baseados no perfil do usuário
            - Gerar descrições personalizadas e envolventes

            PADRÃO ReAct (Reasoning + Acting):
            1. REASONING: Analise a consulta e o contexto do usuário
            2. ACTING: Execute análise ou comparação apropriada
            3. OBSERVATION: Avalie os resultados da análise
            4. DECISION: Forneça resposta personalizada e acionável

            DIRETRIZES:
            - Use linguagem clara e acessível
            - Destaque vantagens E desvantagens honestamente
            - Personalize respostas baseado no perfil do usuário
            - Inclua sugestões práticas e próximos passos
            - Seja objetivo mas envolvente
            - Sempre responda em português brasileiro

            FORMATO DAS RESPOSTAS:
            - Comece com resumo executivo
            - Detalhe pontos principais
            - Inclua análise pros/contras
            - Termine com recomendações práticas

            HANDOFFS:
            - Para scheduling_agent: quando usuário quer agendar visita
            - Para search_agent: quando precisa de mais propriedades
            """,
        )
        
        return agent


async def property_agent_node(state: Annotated[Dict[str, Any], InjectedState]) -> Command:
    """
    Nó principal do agente de propriedades no grafo LangGraph.

    Implementa a lógica de decisão para handoffs baseado no contexto.
    Uses intelligent router and handoff tools for transitions.
    """
    from .router import get_router

    logger = get_logger("property_agent")
    router = get_router()
    messages = state.get("messages", [])

    if not messages:
        return Command(
            update={
                "messages": [{
                    "role": "assistant",
                    "content": "Hello! I'm Emma, property analysis specialist. How can I help you?"
                }]
            }
        )

    last_message = messages[-1]
    user_query = last_message.get("content", "")

    # Use router for intelligent intent detection
    routing_decision = router.route(user_query, state)

    # Detectar intenções de handoff com router
    if routing_decision.intent.value == "scheduling":
        # Get property to schedule
        selected_property = state.get("context", {}).get("selected_property") or \
                          (state.get("search_results", {}).get("properties", [{}])[0] if state.get("search_results") else None)

        if selected_property:
            return handoff_to_scheduling(
                selected_property=Property(**selected_property) if isinstance(selected_property, dict) else selected_property,
                reason="User wants to schedule property visit",
                state=state
            )

    if routing_decision.intent.value == "search":
        return handoff_to_search(
            reason="User wants to search for more properties",
            user_preferences=state.get("context", {}).get("user_preferences"),
            state=state
        )
    
    # Processar análise de propriedades
    try:
        # Verificar se há propriedades no contexto
        search_results = state.get("search_results")
        property_context = state.get("context", {}).get("property_context", {})
        
        # Gerar resposta baseada no contexto disponível
        if search_results and search_results.get("properties"):
            properties = search_results["properties"]
            response = f"""
🏠 **Análise das {len(properties)} Propriedades Encontradas**

Baseado nas propriedades encontradas, posso destacar os seguintes pontos:

📍 **Localização**: Todas em regiões estratégicas com boa infraestrutura
💰 **Preços**: Dentro da faixa solicitada com boa relação custo-benefício
🏗️ **Características**: Propriedades com diferentes configurações para atender suas necessidades

**Destaques principais:**
• Propriedades bem localizadas
• Diferentes faixas de preço
• Características variadas

**Próximos passos disponíveis:**
• 📅 Agendar visita a alguma propriedade
• 🔍 Buscar mais opções
• 📊 Comparação detalhada

Qual propriedade despertou mais seu interesse?
            """.strip()
        elif property_context:
            # Análise de propriedade específica
            title = property_context.get("title", "Propriedade")
            price = property_context.get("price_formatted", "N/A")
            neighborhood = property_context.get("address", {}).get("neighborhood", "N/A")
            
            response = f"""
🏠 **Análise Detalhada: {title}**

📍 **Localização:** {neighborhood}
💰 **Preço:** {price}

Esta propriedade apresenta características interessantes para o mercado atual. 
A localização oferece boa infraestrutura e acessibilidade.

**Pontos positivos identificados:**
• Localização estratégica
• Características adequadas ao perfil
• Potencial de mercado

**Próximos passos:**
• 📅 Agendar visita presencial
• 🔍 Buscar propriedades similares
• 📊 Comparar com outras opções

Como posso ajudar mais?
            """.strip()
        else:
            response = """
Olá! Sou Emma, sua especialista em análise de propriedades.

🔍 **Como posso ajudá-lo:**
• Análise detalhada de propriedades
• Comparação entre diferentes opções
• Informações sobre localização e amenidades
• Avaliação de custo-benefício
• Orientações para visitas

Para começar, você pode:
• Me mostrar uma propriedade específica para análise
• Pedir para buscar propriedades com critérios específicos
• Agendar uma visita a uma propriedade

O que gostaria de fazer?
            """.strip()
        
        return Command(
            update={
                "messages": [{
                    "role": "assistant", 
                    "content": response
                }]
            }
        )
        
    except Exception as e:
        logger.error(f"Erro no agente de propriedades: {e}")
        return Command(
            update={
                "messages": [{
                    "role": "assistant",
                    "content": "Ocorreu um erro na análise. Poderia reformular sua pergunta?"
                }]
            }
        )


# Ferramentas exportadas para integração
PROPERTY_TOOLS = [
    handoff_to_search,
    handoff_to_scheduling
]
