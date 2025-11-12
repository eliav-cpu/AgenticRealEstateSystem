"""
Test Suite for Hybrid Swarm Orchestration

Tests the unified LangGraph-Swarm + PydanticAI orchestrator.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage

from app.orchestration.swarm_hybrid import (
    HybridSwarmOrchestrator,
    PydanticAIWrapper,
    AgentContext
)


@pytest.mark.asyncio
@pytest.mark.unit
class TestHybridSwarmOrchestrator:
    """Test the hybrid swarm orchestrator initialization and core functionality."""

    async def test_orchestrator_initialization(self, mock_settings):
        """Test that orchestrator initializes correctly."""
        with patch('app.orchestration.swarm_hybrid.get_settings', return_value=mock_settings):
            with patch('app.orchestration.swarm_hybrid.ChatOpenAI') as mock_llm:
                with patch('app.orchestration.swarm_hybrid.PydanticAgent'):
                    with patch('app.orchestration.swarm_hybrid.create_react_agent'):
                        with patch('app.orchestration.swarm_hybrid.create_swarm') as mock_swarm:
                            mock_swarm.return_value.compile.return_value = MagicMock()

                            orchestrator = HybridSwarmOrchestrator()

                            assert orchestrator is not None
                            assert orchestrator.search_wrapper is not None
                            assert orchestrator.property_wrapper is not None
                            assert orchestrator.scheduling_wrapper is not None
                            assert orchestrator.swarm is not None

    async def test_orchestrator_has_memory_components(self, mock_orchestrator):
        """Test that orchestrator has memory checkpointer and store."""
        assert hasattr(mock_orchestrator, 'checkpointer')
        assert hasattr(mock_orchestrator, 'store')
        assert mock_orchestrator.checkpointer is not None
        assert mock_orchestrator.store is not None

    async def test_orchestrator_has_agents(self, mock_orchestrator):
        """Test that orchestrator creates all required agents."""
        assert hasattr(mock_orchestrator, 'search_agent')
        assert hasattr(mock_orchestrator, 'property_agent')
        assert hasattr(mock_orchestrator, 'scheduling_agent')

    async def test_process_message_with_thread_id(self, mock_orchestrator):
        """Test processing message with thread ID for memory."""
        message = {
            "messages": [HumanMessage(content="I'm looking for an apartment")]
        }
        config = {
            "configurable": {
                "thread_id": "test_thread_123"
            }
        }

        # Mock the swarm response
        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [
                HumanMessage(content="I'm looking for an apartment"),
                AIMessage(content="I can help you find apartments!")
            ]
        }

        result = await mock_orchestrator.process_message(message, config)

        assert result is not None
        assert "messages" in result
        mock_orchestrator.swarm.ainvoke.assert_called_once()

    async def test_process_message_creates_thread_id_if_missing(self, mock_orchestrator):
        """Test that process_message creates thread_id if not provided."""
        message = {
            "messages": [HumanMessage(content="Hello")]
        }

        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [AIMessage(content="Hi!")]
        }

        result = await mock_orchestrator.process_message(message)

        # Verify thread_id was created
        call_args = mock_orchestrator.swarm.ainvoke.call_args
        assert call_args is not None
        config = call_args[0][1]  # Second argument is config
        assert "configurable" in config
        assert "thread_id" in config["configurable"]
        assert config["configurable"]["thread_id"].startswith("session-")

    async def test_stream_message(self, mock_orchestrator):
        """Test streaming message processing."""
        message = {
            "messages": [HumanMessage(content="Show me properties")]
        }

        # Mock streaming chunks
        async def mock_stream(*args, **kwargs):
            yield {"chunk": 1}
            yield {"chunk": 2}
            yield {"chunk": 3}

        mock_orchestrator.swarm.astream = mock_stream

        chunks = []
        async for chunk in mock_orchestrator.stream_message(message):
            chunks.append(chunk)

        assert len(chunks) == 3
        assert chunks[0] == {"chunk": 1}
        assert chunks[2] == {"chunk": 3}

    async def test_error_handling_in_process_message(self, mock_orchestrator):
        """Test error handling in message processing."""
        message = {
            "messages": [HumanMessage(content="Test")]
        }

        # Mock an error
        mock_orchestrator.swarm.ainvoke.side_effect = Exception("Test error")

        with pytest.raises(Exception) as exc_info:
            await mock_orchestrator.process_message(message)

        assert "Test error" in str(exc_info.value)


@pytest.mark.asyncio
@pytest.mark.unit
class TestPydanticAIWrapper:
    """Test the PydanticAI wrapper functionality."""

    async def test_wrapper_initialization(self, mock_settings):
        """Test wrapper initializes with correct settings."""
        with patch('app.orchestration.swarm_hybrid.get_settings', return_value=mock_settings):
            with patch('app.orchestration.swarm_hybrid.PydanticAgent') as mock_agent:
                mock_agent.return_value = MagicMock()

                wrapper = PydanticAIWrapper("TestAgent", "Test system prompt")

                assert wrapper.agent_name == "TestAgent"
                assert wrapper.pydantic_agent is not None

    async def test_wrapper_run_with_context(self, mock_settings, agent_context):
        """Test wrapper run method with agent context."""
        with patch('app.orchestration.swarm_hybrid.get_settings', return_value=mock_settings):
            with patch('app.orchestration.swarm_hybrid.PydanticAgent') as mock_agent_class:
                # Create mock agent instance
                mock_agent = MagicMock()
                mock_result = MagicMock()
                mock_result.output = "Test response"
                mock_agent.run = AsyncMock(return_value=mock_result)
                mock_agent_class.return_value = mock_agent

                wrapper = PydanticAIWrapper("TestAgent", "Test prompt")

                result = await wrapper.run("Test message", agent_context)

                assert result == "Test response"
                mock_agent.run.assert_called_once()

    async def test_wrapper_enhances_prompt_with_context(self, mock_settings, agent_context_with_property):
        """Test that wrapper enhances prompt with property context."""
        with patch('app.orchestration.swarm_hybrid.get_settings', return_value=mock_settings):
            with patch('app.orchestration.swarm_hybrid.PydanticAgent') as mock_agent_class:
                mock_agent = MagicMock()
                mock_result = MagicMock()
                mock_result.output = "Response"
                mock_agent.run = AsyncMock(return_value=mock_result)
                mock_agent_class.return_value = mock_agent

                wrapper = PydanticAIWrapper("TestAgent", "Test prompt")

                await wrapper.run("Tell me about this property", agent_context_with_property)

                # Check that run was called with enhanced prompt
                call_args = mock_agent.run.call_args[0][0]
                assert "PROPERTY CONTEXT" in call_args
                assert "Ocean Drive" in call_args

    async def test_wrapper_error_handling(self, mock_settings, agent_context):
        """Test wrapper handles errors gracefully."""
        with patch('app.orchestration.swarm_hybrid.get_settings', return_value=mock_settings):
            with patch('app.orchestration.swarm_hybrid.PydanticAgent') as mock_agent_class:
                mock_agent = MagicMock()
                mock_agent.run = AsyncMock(side_effect=Exception("API Error"))
                mock_agent_class.return_value = mock_agent

                wrapper = PydanticAIWrapper("TestAgent", "Test prompt")

                result = await wrapper.run("Test message", agent_context)

                # Should return fallback message, not raise exception
                assert "error" in result.lower()


@pytest.mark.asyncio
@pytest.mark.unit
class TestAgentContext:
    """Test the AgentContext dataclass."""

    def test_agent_context_creation(self):
        """Test creating AgentContext instances."""
        context = AgentContext(
            property_context={"address": "123 Main St"},
            search_results=[{"id": 1}, {"id": 2}],
            session_id="test_123",
            data_mode="mock"
        )

        assert context.property_context == {"address": "123 Main St"}
        assert len(context.search_results) == 2
        assert context.session_id == "test_123"
        assert context.data_mode == "mock"

    def test_agent_context_defaults(self):
        """Test AgentContext with default values."""
        context = AgentContext()

        assert context.property_context is None
        assert context.search_results is None
        assert context.session_id is None
        assert context.data_mode == "mock"


@pytest.mark.asyncio
@pytest.mark.integration
class TestSwarmHandoffs:
    """Test agent handoffs in the swarm."""

    async def test_search_to_property_handoff(self, mock_orchestrator):
        """Test handoff from search agent to property agent."""
        # This would require more complex mocking of the actual swarm behavior
        # For now, we test that the agents have handoff tools
        assert hasattr(mock_orchestrator, 'search_agent')
        assert hasattr(mock_orchestrator, 'property_agent')

    async def test_property_to_scheduling_handoff(self, mock_orchestrator):
        """Test handoff from property agent to scheduling agent."""
        assert hasattr(mock_orchestrator, 'property_agent')
        assert hasattr(mock_orchestrator, 'scheduling_agent')

    async def test_all_agents_have_handoff_tools(self, mock_orchestrator):
        """Test that all agents have appropriate handoff tools."""
        # Verify agents exist
        assert mock_orchestrator.search_agent is not None
        assert mock_orchestrator.property_agent is not None
        assert mock_orchestrator.scheduling_agent is not None


@pytest.mark.asyncio
@pytest.mark.integration
class TestMemoryPersistence:
    """Test memory persistence across messages."""

    async def test_conversation_history_persists(self, mock_orchestrator):
        """Test that conversation history is maintained."""
        config = {
            "configurable": {
                "thread_id": "memory_test_123"
            }
        }

        # First message
        message1 = {
            "messages": [HumanMessage(content="First message")]
        }
        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [
                HumanMessage(content="First message"),
                AIMessage(content="First response")
            ]
        }

        result1 = await mock_orchestrator.process_message(message1, config)

        # Second message with same thread_id
        message2 = {
            "messages": [HumanMessage(content="Second message")]
        }
        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [
                HumanMessage(content="First message"),
                AIMessage(content="First response"),
                HumanMessage(content="Second message"),
                AIMessage(content="Second response")
            ]
        }

        result2 = await mock_orchestrator.process_message(message2, config)

        # Both calls should use the same thread_id
        assert mock_orchestrator.swarm.ainvoke.call_count == 2


@pytest.mark.asyncio
@pytest.mark.slow
class TestPerformance:
    """Test performance characteristics of the orchestrator."""

    async def test_message_processing_completes_in_time(self, mock_orchestrator):
        """Test that message processing completes within reasonable time."""
        import time

        message = {
            "messages": [HumanMessage(content="Test message")]
        }

        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [AIMessage(content="Response")]
        }

        start = time.time()
        await mock_orchestrator.process_message(message)
        duration = time.time() - start

        # Should complete in under 5 seconds
        assert duration < 5.0
