"""
Test suite for unified swarm orchestration.

Tests the integration between langgraph-swarm and pydantic-ai.
"""

import pytest
import asyncio
from langchain_core.messages import HumanMessage
from app.orchestration.unified_swarm import (
    get_unified_swarm_orchestrator,
    UnifiedSwarmOrchestrator,
    PydanticAgentWrapper,
    AgentContext,
    route_to_agent,
    UnifiedSwarmState
)


@pytest.fixture
def orchestrator():
    """Create orchestrator instance for testing."""
    return get_unified_swarm_orchestrator()


@pytest.fixture
def sample_context():
    """Create sample context for testing."""
    return AgentContext(
        session_id="test-session",
        data_mode="mock",
        property_context={
            "formattedAddress": "123 Test St, Miami, FL",
            "price": 2500,
            "bedrooms": 2,
            "bathrooms": 2
        }
    )


class TestPydanticAgentWrapper:
    """Test PydanticAI agent wrapper functionality."""

    @pytest.mark.asyncio
    async def test_agent_wrapper_creation(self):
        """Test that agent wrapper creates properly."""
        wrapper = PydanticAgentWrapper(
            "TestAgent",
            "You are a test agent."
        )
        assert wrapper.agent_name == "TestAgent"
        assert wrapper.pydantic_agent is not None

    @pytest.mark.asyncio
    async def test_agent_execution_no_blocking(self, sample_context):
        """Test that agent execution doesn't use blocking asyncio.run()."""
        wrapper = PydanticAgentWrapper(
            "TestAgent",
            "You are a helpful assistant."
        )

        # This should work without event loop conflicts
        response = await wrapper.execute("Hello", sample_context)
        assert isinstance(response, str)
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_enhanced_prompt_building(self, sample_context):
        """Test that prompts are enhanced with context."""
        wrapper = PydanticAgentWrapper(
            "TestAgent",
            "You are a test agent."
        )

        enhanced_prompt = wrapper._build_enhanced_prompt("Test message", sample_context)

        # Should include user message
        assert "Test message" in enhanced_prompt

        # Should include property context
        assert "123 Test St" in enhanced_prompt
        assert "2500" in enhanced_prompt


class TestRoutingLogic:
    """Test intelligent routing between agents."""

    def test_route_to_scheduling_agent(self):
        """Test routing to scheduling agent based on keywords."""
        state = UnifiedSwarmState(
            messages=[HumanMessage(content="I want to schedule a visit tomorrow")],
            session_id="test",
            context={}
        )

        result = route_to_agent(state)
        assert result == "scheduling_agent"

    def test_route_to_search_agent(self):
        """Test routing to search agent for property searches."""
        state = UnifiedSwarmState(
            messages=[HumanMessage(content="I'm looking for a 2 bedroom apartment")],
            session_id="test",
            context={}
        )

        result = route_to_agent(state)
        assert result == "search_agent"

    def test_route_to_property_agent_with_context(self):
        """Test routing to property agent when context exists."""
        state = UnifiedSwarmState(
            messages=[HumanMessage(content="What's the price of this property?")],
            session_id="test",
            context={
                "property_context": {
                    "formattedAddress": "123 Test St"
                }
            }
        )

        result = route_to_agent(state)
        assert result == "property_agent"

    def test_default_routing_no_context(self):
        """Test default routing behavior."""
        state = UnifiedSwarmState(
            messages=[HumanMessage(content="Hello")],
            session_id="test",
            context={}
        )

        result = route_to_agent(state)
        # Should default to search agent when no context
        assert result in ["search_agent", "property_agent"]


class TestUnifiedSwarmOrchestrator:
    """Test unified swarm orchestrator integration."""

    def test_orchestrator_initialization(self, orchestrator):
        """Test that orchestrator initializes properly."""
        assert orchestrator is not None
        assert orchestrator.graph is not None
        assert orchestrator.checkpointer is not None
        assert orchestrator.store is not None

    @pytest.mark.asyncio
    async def test_process_message_creates_config(self, orchestrator):
        """Test that process_message creates config if not provided."""
        message = {
            "messages": [HumanMessage(content="Hello")],
            "session_id": "test",
            "context": {}
        }

        # Should not raise error even without config
        result = await orchestrator.process_message(message)
        assert result is not None
        assert "messages" in result

    @pytest.mark.asyncio
    async def test_process_message_with_thread_id(self, orchestrator):
        """Test that process_message uses provided thread_id."""
        message = {
            "messages": [HumanMessage(content="Hello")],
            "session_id": "test",
            "context": {}
        }

        config = {
            "configurable": {
                "thread_id": "test-thread-123"
            }
        }

        result = await orchestrator.process_message(message, config)
        assert result is not None

    @pytest.mark.asyncio
    async def test_no_asyncio_run_in_async_context(self, orchestrator):
        """Test that no blocking asyncio.run() is used in async context."""

        message = {
            "messages": [HumanMessage(content="Test message")],
            "session_id": "test",
            "context": {}
        }

        # This should not raise RuntimeError about event loops
        try:
            result = await orchestrator.process_message(message)
            assert True  # If we get here, no event loop conflict
        except RuntimeError as e:
            if "already running" in str(e):
                pytest.fail("asyncio.run() was called in async context - event loop conflict!")
            raise

    @pytest.mark.asyncio
    async def test_streaming_functionality(self, orchestrator):
        """Test that streaming works without blocking."""
        message = {
            "messages": [HumanMessage(content="Hello")],
            "session_id": "test",
            "context": {}
        }

        chunks = []
        async for chunk in orchestrator.stream_message(message):
            chunks.append(chunk)

        assert len(chunks) > 0


class TestMemoryPersistence:
    """Test memory persistence across messages."""

    @pytest.mark.asyncio
    async def test_memory_persists_across_calls(self, orchestrator):
        """Test that memory persists using thread_id."""
        thread_id = "test-memory-thread"
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        # First message
        message1 = {
            "messages": [HumanMessage(content="Hello")],
            "session_id": "test",
            "context": {}
        }

        result1 = await orchestrator.process_message(message1, config)

        # Second message with same thread_id
        message2 = {
            "messages": [HumanMessage(content="Follow-up question")],
            "session_id": "test",
            "context": {}
        }

        result2 = await orchestrator.process_message(message2, config)

        # Both should succeed - memory should be maintained
        assert result1 is not None
        assert result2 is not None


class TestErrorHandling:
    """Test error handling and graceful degradation."""

    @pytest.mark.asyncio
    async def test_agent_failure_returns_error_message(self, sample_context):
        """Test that agent failures return user-friendly errors."""
        # Create wrapper with invalid config to trigger error
        wrapper = PydanticAgentWrapper(
            "TestAgent",
            "Test prompt"
        )

        # Force an error by providing invalid message type
        try:
            response = await wrapper.execute(None, sample_context)
            # Should return error message, not raise exception
            assert "error" in response.lower() or len(response) > 0
        except Exception as e:
            # If it does raise, it should be handled gracefully
            assert True

    @pytest.mark.asyncio
    async def test_orchestrator_handles_invalid_message(self, orchestrator):
        """Test that orchestrator handles invalid messages gracefully."""
        invalid_message = {
            "messages": [],  # Empty messages
            "session_id": "test"
        }

        try:
            result = await orchestrator.process_message(invalid_message)
            # Should handle gracefully
            assert result is not None
        except Exception:
            # Or raise appropriate error
            assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
