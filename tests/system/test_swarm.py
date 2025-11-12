"""
Testes para o orquestrador LangGraph-Swarm.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.orchestration.swarm import SwarmOrchestrator, SwarmState


class TestSwarmOrchestrator:
    """Testes para o orquestrador swarm."""
    
    @pytest.fixture
    def orchestrator(self):
        """Fixture para criar orquestrador."""
        return SwarmOrchestrator()
    
    def test_orchestrator_initialization(self, orchestrator):
        """Testar inicialização do orquestrador."""
        assert orchestrator is not None
        assert orchestrator.graph is not None
        assert orchestrator.logger is not None
    
    @pytest.mark.asyncio
    async def test_process_message_basic(self, orchestrator):
        """Testar processamento básico de mensagem."""
        message = {
            "messages": [
                {"role": "user", "content": "Olá, procuro um apartamento"}
            ]
        }
        
        # Mock do grafo para evitar execução real
        orchestrator.graph.ainvoke = AsyncMock(return_value={
            "messages": [
                {"role": "assistant", "content": "Olá! Como posso ajudá-lo?"}
            ]
        })
        
        result = await orchestrator.process_message(message)
        
        assert result is not None
        assert "messages" in result
    
    @pytest.mark.asyncio
    async def test_process_stream(self, orchestrator):
        """Testar processamento com streaming."""
        message = {
            "messages": [
                {"role": "user", "content": "Busco apartamento em Copacabana"}
            ]
        }
        
        # Mock do streaming
        async def mock_stream(msg):
            yield {"agent": "search_agent", "message": "Processando..."}
            yield {"final_response": "Encontrei algumas opções!"}
        
        orchestrator.graph.astream = mock_stream
        
        chunks = []
        async for chunk in orchestrator.process_stream(message):
            chunks.append(chunk)
        
        assert len(chunks) == 2
        assert chunks[0]["agent"] == "search_agent"
        assert "final_response" in chunks[1]


class TestSwarmState:
    """Testes para o estado do swarm."""
    
    def test_swarm_state_creation(self):
        """Testar criação do estado."""
        state = SwarmState(
            messages=[{"role": "user", "content": "test"}],
            current_agent="search_agent"
        )
        
        assert state.current_agent == "search_agent"
        assert len(state.messages) == 1
        assert state.session_id == "default"
    
    def test_swarm_state_context(self):
        """Testar contexto do estado."""
        state = SwarmState(
            context={"test_key": "test_value"},
            handoff_history=[{"from": "search", "to": "property"}]
        )
        
        assert state.context["test_key"] == "test_value"
        assert len(state.handoff_history) == 1 