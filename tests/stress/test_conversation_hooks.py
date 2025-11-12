"""
Hooks de Teste para Conversação - Real Estate Assistant
Sistema para capturar, validar e analisar fluxos de conversação entre agentes
"""

import asyncio
import pytest
import json
import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from pydantic_ai import Agent, capture_run_messages
from pydantic_ai.models.test import TestModel
from pydantic_ai.models.function import FunctionModel, AgentInfo
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart

class ConversationPhase(Enum):
    """Fases da conversa imobiliária"""
    GREETING = "greeting"
    SEARCH_CRITERIA = "search_criteria"
    PROPERTY_DETAILS = "property_details"
    SCHEDULING = "scheduling"
    CLOSING = "closing"

class AgentType(Enum):
    """Tipos de agentes no sistema"""
    SEARCH_AGENT = "search_agent"
    PROPERTY_AGENT = "property_agent"
    SCHEDULING_AGENT = "scheduling_agent"

@dataclass
class ConversationEvent:
    """Evento de conversa capturado"""
    timestamp: datetime
    agent_type: AgentType
    phase: ConversationPhase
    user_input: str
    agent_response: str
    response_time: float
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversationFlow:
    """Fluxo completo de conversa"""
    session_id: str
    user_profile: str
    events: List[ConversationEvent] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_duration: float = 0.0
    agent_transitions: List[Dict[str, Any]] = field(default_factory=list)
    success_metrics: Dict[str, Any] = field(default_factory=dict)

class ConversationHook:
    """Hook para capturar eventos de conversa"""
    
    def __init__(self, name: str, trigger_condition: Callable[[ConversationEvent], bool]):
        self.name = name
        self.trigger_condition = trigger_condition
        self.captured_events: List[ConversationEvent] = []
        self.is_active = True
    
    def capture(self, event: ConversationEvent) -> bool:
        """Captura evento se a condição for atendida"""
        if self.is_active and self.trigger_condition(event):
            self.captured_events.append(event)
            return True
        return False
    
    def get_captured_events(self) -> List[ConversationEvent]:
        """Retorna eventos capturados"""
        return self.captured_events.copy()
    
    def reset(self):
        """Reseta eventos capturados"""
        self.captured_events.clear()

class ConversationAnalyzer:
    """Analisador de padrões de conversa"""
    
    def __init__(self):
        self.flows: List[ConversationFlow] = []
        self.hooks: List[ConversationHook] = []
        self.patterns: Dict[str, Any] = {}
    
    def add_hook(self, hook: ConversationHook):
        """Adiciona hook de captura"""
        self.hooks.append(hook)
    
    def create_standard_hooks(self) -> List[ConversationHook]:
        """Cria hooks padrão para análise"""
        hooks = [
            # Hook para capturar transições de agente
            ConversationHook(
                "agent_transitions",
                lambda event: len(self.flows) > 0 and len(self.flows[-1].events) > 0 and 
                self.flows[-1].events[-1].agent_type != event.agent_type
            ),
            
            # Hook para capturar respostas lentas
            ConversationHook(
                "slow_responses",
                lambda event: event.response_time > 5.0
            ),
            
            # Hook para capturar menções de preço
            ConversationHook(
                "price_discussions",
                lambda event: any(word in event.user_input.lower() or word in event.agent_response.lower() 
                                for word in ["price", "cost", "rent", "budget", "$"])
            ),
            
            # Hook para capturar agendamentos
            ConversationHook(
                "scheduling_requests",
                lambda event: any(word in event.user_input.lower() or word in event.agent_response.lower() 
                                for word in ["schedule", "appointment", "viewing", "visit", "tour"])
            ),
            
            # Hook para capturar problemas/erros
            ConversationHook(
                "error_responses",
                lambda event: any(word in event.agent_response.lower() 
                                for word in ["error", "sorry", "problem", "issue", "unavailable"])
            )
        ]
        
        for hook in hooks:
            self.add_hook(hook)
        
        return hooks
    
    def start_conversation_flow(self, session_id: str, user_profile: str) -> ConversationFlow:
        """Inicia novo fluxo de conversa"""
        flow = ConversationFlow(
            session_id=session_id,
            user_profile=user_profile,
            start_time=datetime.now()
        )
        self.flows.append(flow)
        return flow
    
    def add_event(self, event: ConversationEvent):
        """Adiciona evento ao fluxo atual"""
        if not self.flows:
            self.start_conversation_flow("default", "unknown")
        
        current_flow = self.flows[-1]
        current_flow.events.append(event)
        
        # Verificar transições de agente
        if len(current_flow.events) > 1:
            previous_agent = current_flow.events[-2].agent_type
            current_agent = event.agent_type
            
            if previous_agent != current_agent:
                transition = {
                    "from": previous_agent.value,
                    "to": current_agent.value,
                    "timestamp": event.timestamp,
                    "trigger": event.user_input
                }
                current_flow.agent_transitions.append(transition)
        
        # Aplicar hooks
        for hook in self.hooks:
            hook.capture(event)
    
    def end_conversation_flow(self) -> Optional[ConversationFlow]:
        """Finaliza fluxo atual"""
        if not self.flows:
            return None
        
        flow = self.flows[-1]
        flow.end_time = datetime.now()
        flow.total_duration = (flow.end_time - flow.start_time).total_seconds()
        
        # Calcular métricas de sucesso
        flow.success_metrics = self._calculate_success_metrics(flow)
        
        return flow
    
    def _calculate_success_metrics(self, flow: ConversationFlow) -> Dict[str, Any]:
        """Calcula métricas de sucesso da conversa"""
        metrics = {
            "total_interactions": len(flow.events),
            "agent_transitions": len(flow.agent_transitions),
            "average_response_time": sum(e.response_time for e in flow.events) / len(flow.events) if flow.events else 0,
            "phases_covered": len(set(e.phase for e in flow.events)),
            "agents_used": len(set(e.agent_type for e in flow.events)),
            "conversation_quality": "unknown"
        }
        
        # Determinar qualidade da conversa
        if metrics["phases_covered"] >= 3 and metrics["agents_used"] >= 2:
            if metrics["average_response_time"] < 3.0:
                metrics["conversation_quality"] = "excellent"
            elif metrics["average_response_time"] < 5.0:
                metrics["conversation_quality"] = "good"
            else:
                metrics["conversation_quality"] = "fair"
        else:
            metrics["conversation_quality"] = "incomplete"
        
        return metrics
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """Analisa padrões nos fluxos de conversa"""
        if not self.flows:
            return {"error": "No conversation flows to analyze"}
        
        analysis = {
            "total_conversations": len(self.flows),
            "average_duration": sum(f.total_duration for f in self.flows) / len(self.flows),
            "common_agent_transitions": self._analyze_transitions(),
            "response_time_distribution": self._analyze_response_times(),
            "phase_patterns": self._analyze_phase_patterns(),
            "hook_summary": self._summarize_hooks()
        }
        
        return analysis
    
    def _analyze_transitions(self) -> Dict[str, int]:
        """Analisa transições mais comuns entre agentes"""
        transitions = {}
        for flow in self.flows:
            for transition in flow.agent_transitions:
                key = f"{transition['from']} -> {transition['to']}"
                transitions[key] = transitions.get(key, 0) + 1
        
        return dict(sorted(transitions.items(), key=lambda x: x[1], reverse=True))
    
    def _analyze_response_times(self) -> Dict[str, float]:
        """Analisa distribuição de tempos de resposta"""
        all_times = []
        for flow in self.flows:
            all_times.extend([e.response_time for e in flow.events])
        
        if not all_times:
            return {"error": "No response times to analyze"}
        
        all_times.sort()
        n = len(all_times)
        
        return {
            "min": min(all_times),
            "max": max(all_times),
            "average": sum(all_times) / n,
            "median": all_times[n//2],
            "p95": all_times[int(n * 0.95)] if n > 0 else 0
        }
    
    def _analyze_phase_patterns(self) -> Dict[str, Any]:
        """Analisa padrões de fases da conversa"""
        phase_sequences = []
        for flow in self.flows:
            sequence = [e.phase.value for e in flow.events]
            phase_sequences.append(sequence)
        
        # Encontrar sequências mais comuns
        sequence_counts = {}
        for seq in phase_sequences:
            seq_str = " -> ".join(seq)
            sequence_counts[seq_str] = sequence_counts.get(seq_str, 0) + 1
        
        return {
            "most_common_sequences": dict(sorted(sequence_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            "average_phases_per_conversation": sum(len(seq) for seq in phase_sequences) / len(phase_sequences) if phase_sequences else 0
        }
    
    def _summarize_hooks(self) -> Dict[str, int]:
        """Resumo dos eventos capturados pelos hooks"""
        summary = {}
        for hook in self.hooks:
            summary[hook.name] = len(hook.captured_events)
        return summary
    
    def generate_conversation_report(self) -> str:
        """Gera relatório detalhado das conversas"""
        analysis = self.analyze_patterns()
        
        report = f"""
🗣️ RELATÓRIO DE ANÁLISE DE CONVERSAS
{'='*50}

📊 ESTATÍSTICAS GERAIS:
• Total de Conversas: {analysis['total_conversations']}
• Duração Média: {analysis['average_duration']:.2f}s
• Qualidade Média: {self._calculate_average_quality()}

⏱️ TEMPOS DE RESPOSTA:
• Mínimo: {analysis['response_time_distribution']['min']:.2f}s
• Máximo: {analysis['response_time_distribution']['max']:.2f}s
• Média: {analysis['response_time_distribution']['average']:.2f}s
• Mediana: {analysis['response_time_distribution']['median']:.2f}s
• P95: {analysis['response_time_distribution']['p95']:.2f}s

🔄 TRANSIÇÕES MAIS COMUNS:
"""
        
        for transition, count in list(analysis['common_agent_transitions'].items())[:5]:
            report += f"• {transition}: {count} vezes\n"
        
        report += f"""
📝 PADRÕES DE FASES:
• Fases Médias por Conversa: {analysis['phase_patterns']['average_phases_per_conversation']:.1f}

🎯 EVENTOS CAPTURADOS:
"""
        
        for hook_name, count in analysis['hook_summary'].items():
            report += f"• {hook_name}: {count} eventos\n"
        
        return report
    
    def _calculate_average_quality(self) -> str:
        """Calcula qualidade média das conversas"""
        if not self.flows:
            return "N/A"
        
        quality_scores = {"excellent": 4, "good": 3, "fair": 2, "incomplete": 1}
        total_score = sum(quality_scores.get(f.success_metrics.get("conversation_quality", "incomplete"), 1) for f in self.flows)
        average_score = total_score / len(self.flows)
        
        if average_score >= 3.5:
            return "Excelente"
        elif average_score >= 2.5:
            return "Boa"
        elif average_score >= 1.5:
            return "Regular"
        else:
            return "Precisa Melhorar"

class ConversationSimulator:
    """Simulador de conversas para testes"""
    
    def __init__(self, analyzer: ConversationAnalyzer):
        self.analyzer = analyzer
    
    def create_realistic_test_model(self) -> FunctionModel:
        """Cria modelo de teste realista"""
        
        def realistic_response(messages: List[ModelMessage], info: AgentInfo) -> ModelResponse:
            """Gera respostas realistas baseadas no contexto"""
            
            # Simular delay realista
            time.sleep(random.uniform(0.5, 2.0))
            
            # Obter mensagem do usuário
            user_message = messages[-1].parts[-1].content if messages and messages[-1].parts else "Hello"
            
            # Gerar resposta contextual
            if "hello" in user_message.lower() or "hi" in user_message.lower():
                response = "Hello! I'm here to help you find the perfect property. What are you looking for?"
            elif "bedroom" in user_message.lower():
                response = "I can help you find properties with the number of bedrooms you need. What's your preferred location?"
            elif "price" in user_message.lower() or "budget" in user_message.lower():
                response = "I understand budget is important. Let me show you some properties in your price range."
            elif "schedule" in user_message.lower() or "visit" in user_message.lower():
                response = "I'd be happy to schedule a viewing for you. What days work best?"
            else:
                response = "That's a great question! Let me provide you with the information you need."
            
            return ModelResponse(parts=[TextPart(content=response)])
        
        return FunctionModel(realistic_response)
    
    async def simulate_conversation(self, user_profile: str, conversation_script: List[Dict[str, Any]]) -> ConversationFlow:
        """Simula conversa baseada em script"""
        
        # Iniciar fluxo
        session_id = f"sim_{int(time.time())}"
        flow = self.analyzer.start_conversation_flow(session_id, user_profile)
        
        # Criar agente de teste
        test_model = self.create_realistic_test_model()
        agent = Agent(test_model)
        
        # Executar script de conversa
        for step in conversation_script:
            start_time = time.time()
            
            # Executar interação
            with capture_run_messages() as messages:
                result = await agent.run(step["user_input"])
                response_time = time.time() - start_time
                
                # Criar evento
                event = ConversationEvent(
                    timestamp=datetime.now(),
                    agent_type=AgentType(step.get("agent_type", "search_agent")),
                    phase=ConversationPhase(step.get("phase", "search_criteria")),
                    user_input=step["user_input"],
                    agent_response=str(result.data),
                    response_time=response_time,
                    context=step.get("context", {}),
                    metadata={"messages": messages}
                )
                
                # Adicionar evento ao fluxo
                self.analyzer.add_event(event)
        
        # Finalizar fluxo
        return self.analyzer.end_conversation_flow()

# Testes pytest
class TestConversationHooks:
    """Testes para hooks de conversa"""
    
    @pytest.fixture
    def analyzer(self):
        analyzer = ConversationAnalyzer()
        analyzer.create_standard_hooks()
        return analyzer
    
    @pytest.fixture
    def simulator(self, analyzer):
        return ConversationSimulator(analyzer)
    
    @pytest.mark.asyncio
    async def test_conversation_flow_creation(self, analyzer):
        """Testa criação de fluxo de conversa"""
        flow = analyzer.start_conversation_flow("test_session", "test_user")
        
        assert flow.session_id == "test_session"
        assert flow.user_profile == "test_user"
        assert len(flow.events) == 0
        assert len(analyzer.flows) == 1
    
    @pytest.mark.asyncio
    async def test_event_capture(self, analyzer):
        """Testa captura de eventos"""
        analyzer.start_conversation_flow("test", "user")
        
        event = ConversationEvent(
            timestamp=datetime.now(),
            agent_type=AgentType.SEARCH_AGENT,
            phase=ConversationPhase.GREETING,
            user_input="Hello",
            agent_response="Hi there!",
            response_time=1.0
        )
        
        analyzer.add_event(event)
        
        assert len(analyzer.flows[0].events) == 1
        assert analyzer.flows[0].events[0] == event
    
    @pytest.mark.asyncio
    async def test_hook_triggering(self, analyzer):
        """Testa acionamento de hooks"""
        analyzer.start_conversation_flow("test", "user")
        
        # Evento com menção de preço
        price_event = ConversationEvent(
            timestamp=datetime.now(),
            agent_type=AgentType.SEARCH_AGENT,
            phase=ConversationPhase.SEARCH_CRITERIA,
            user_input="What's the price?",
            agent_response="The rent is $2000/month",
            response_time=1.0
        )
        
        analyzer.add_event(price_event)
        
        # Verificar se hook de preço foi acionado
        price_hook = next((h for h in analyzer.hooks if h.name == "price_discussions"), None)
        assert price_hook is not None
        assert len(price_hook.captured_events) == 1
    
    @pytest.mark.asyncio
    async def test_conversation_simulation(self, simulator):
        """Testa simulação de conversa"""
        script = [
            {
                "user_input": "Hello, I'm looking for an apartment",
                "agent_type": "search_agent",
                "phase": "greeting"
            },
            {
                "user_input": "I need 2 bedrooms under $3000",
                "agent_type": "search_agent", 
                "phase": "search_criteria"
            },
            {
                "user_input": "Can I schedule a viewing?",
                "agent_type": "scheduling_agent",
                "phase": "scheduling"
            }
        ]
        
        flow = await simulator.simulate_conversation("test_user", script)
        
        assert flow is not None
        assert len(flow.events) == 3
        assert flow.success_metrics["total_interactions"] == 3
        assert flow.success_metrics["agents_used"] == 2
    
    @pytest.mark.asyncio
    async def test_pattern_analysis(self, analyzer):
        """Testa análise de padrões"""
        # Simular múltiplas conversas
        for i in range(3):
            analyzer.start_conversation_flow(f"session_{i}", f"user_{i}")
            
            events = [
                ConversationEvent(
                    timestamp=datetime.now(),
                    agent_type=AgentType.SEARCH_AGENT,
                    phase=ConversationPhase.GREETING,
                    user_input="Hello",
                    agent_response="Hi!",
                    response_time=1.0
                ),
                ConversationEvent(
                    timestamp=datetime.now(),
                    agent_type=AgentType.PROPERTY_AGENT,
                    phase=ConversationPhase.PROPERTY_DETAILS,
                    user_input="Tell me about this property",
                    agent_response="This is a great property...",
                    response_time=2.0
                )
            ]
            
            for event in events:
                analyzer.add_event(event)
            
            analyzer.end_conversation_flow()
        
        analysis = analyzer.analyze_patterns()
        
        assert analysis["total_conversations"] == 3
        assert "search_agent -> property_agent" in analysis["common_agent_transitions"]
        assert analysis["response_time_distribution"]["average"] == 1.5

# Função principal para demonstração
async def main():
    """Demonstração do sistema de hooks"""
    
    print("🎯 SISTEMA DE HOOKS DE CONVERSA - DEMONSTRAÇÃO")
    print("="*55)
    
    # Criar analisador
    analyzer = ConversationAnalyzer()
    analyzer.create_standard_hooks()
    
    # Criar simulador
    simulator = ConversationSimulator(analyzer)
    
    # Script de conversa realista
    conversation_scripts = [
        # Conversa 1: Busca básica
        [
            {"user_input": "Hi, I'm looking for a 1-bedroom apartment", "agent_type": "search_agent", "phase": "greeting"},
            {"user_input": "What's available under $2500?", "agent_type": "search_agent", "phase": "search_criteria"},
            {"user_input": "Tell me about the first property", "agent_type": "property_agent", "phase": "property_details"},
            {"user_input": "Can I schedule a viewing?", "agent_type": "scheduling_agent", "phase": "scheduling"}
        ],
        # Conversa 2: Busca com múltiplas perguntas
        [
            {"user_input": "Hello, I need help finding a place", "agent_type": "search_agent", "phase": "greeting"},
            {"user_input": "I'm looking for 2 bedrooms in Miami", "agent_type": "search_agent", "phase": "search_criteria"},
            {"user_input": "What's the price range?", "agent_type": "search_agent", "phase": "search_criteria"},
            {"user_input": "Show me property details", "agent_type": "property_agent", "phase": "property_details"},
            {"user_input": "What about parking?", "agent_type": "property_agent", "phase": "property_details"},
            {"user_input": "Let's schedule a tour", "agent_type": "scheduling_agent", "phase": "scheduling"}
        ]
    ]
    
    # Executar simulações
    print("\n📝 Executando simulações de conversa...")
    for i, script in enumerate(conversation_scripts, 1):
        print(f"   Conversa {i}: {len(script)} interações")
        await simulator.simulate_conversation(f"user_profile_{i}", script)
    
    # Gerar relatório
    print("\n📊 RELATÓRIO DE ANÁLISE:")
    print(analyzer.generate_conversation_report())
    
    print("\n✅ Demonstração concluída!")

if __name__ == "__main__":
    import random
    asyncio.run(main()) 