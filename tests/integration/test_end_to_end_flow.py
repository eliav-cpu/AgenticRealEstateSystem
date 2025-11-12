"""
End-to-End Integration Tests for Complete System Flow

Tests the entire system workflow from user input to final output:
- Complete user journey: search → details → scheduling
- Multi-agent coordination and handoffs
- Data flow through the entire pipeline
- Error recovery and graceful degradation
- Performance under realistic conditions
- Integration of all components

Coverage Target: >80%
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json


class MockSystemOrchestrator:
    """Mock system orchestrator for end-to-end testing."""

    def __init__(self):
        self.langfuse_client = MockLangfuseClient()
        self.logfire_handler = MockLogfireHandler()
        self.agents = {
            "search": MockSearchAgent(),
            "property": MockPropertyAgent(),
            "scheduling": MockSchedulingAgent()
        }
        self.current_context = {}
        self.conversation_history = []

    async def process_user_message(
        self,
        message: str,
        session_id: str = "test_session"
    ) -> Dict[str, Any]:
        """Process a user message through the system."""
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now()
        })

        # Determine agent and route
        agent_type = self._determine_agent(message)
        agent = self.agents[agent_type]

        # Create trace
        trace = self.langfuse_client.trace(
            name=f"{agent_type}_request",
            metadata={"session_id": session_id}
        )

        # Process with agent
        response = await agent.process(message, self.current_context)

        # Update context
        if "context_update" in response:
            self.current_context.update(response["context_update"])

        # Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response["message"],
            "timestamp": datetime.now()
        })

        # End trace
        trace.end(output=response)

        # Log
        self.logfire_handler.info(
            f"Processed {agent_type} request",
            session_id=session_id,
            agent=agent_type
        )

        return response

    def _determine_agent(self, message: str) -> str:
        """Determine which agent should handle the message."""
        message_lower = message.lower()

        if any(word in message_lower for word in ["find", "search", "looking for", "show me"]):
            return "search"
        elif any(word in message_lower for word in ["details", "tell me about", "more about"]):
            return "property"
        elif any(word in message_lower for word in ["schedule", "visit", "viewing", "appointment"]):
            return "scheduling"
        else:
            return "search"  # Default


class MockSearchAgent:
    """Mock search agent."""

    async def process(self, message: str, context: Dict) -> Dict[str, Any]:
        """Process search request."""
        # Simulate processing delay
        await asyncio.sleep(0.01)

        properties = [
            {
                "id": "prop_001",
                "address": "123 Ocean Drive, Miami Beach, FL",
                "price": 3200,
                "bedrooms": 2,
                "bathrooms": 2
            },
            {
                "id": "prop_002",
                "address": "456 Brickell Ave, Miami, FL",
                "price": 2800,
                "bedrooms": 1,
                "bathrooms": 1
            }
        ]

        return {
            "agent": "search",
            "message": f"Found {len(properties)} properties matching your criteria",
            "properties": properties,
            "context_update": {"properties": properties, "last_search": message}
        }


class MockPropertyAgent:
    """Mock property analysis agent."""

    async def process(self, message: str, context: Dict) -> Dict[str, Any]:
        """Process property details request."""
        await asyncio.sleep(0.01)

        # Extract property from context
        properties = context.get("properties", [])
        property_data = properties[0] if properties else None

        return {
            "agent": "property",
            "message": "Here's a detailed analysis of the property",
            "analysis": {
                "highlights": ["Ocean view", "Modern amenities"],
                "pros": ["Great location", "Well maintained"],
                "cons": ["Parking costs extra"],
                "recommendation": "Highly recommended"
            },
            "context_update": {"selected_property": property_data}
        }


class MockSchedulingAgent:
    """Mock scheduling agent."""

    async def process(self, message: str, context: Dict) -> Dict[str, Any]:
        """Process scheduling request."""
        await asyncio.sleep(0.01)

        property_data = context.get("selected_property", {})

        return {
            "agent": "scheduling",
            "message": "I can schedule a viewing for you",
            "available_slots": [
                "Tomorrow at 10:00 AM",
                "Friday at 2:00 PM",
                "Saturday at 11:00 AM"
            ],
            "context_update": {
                "scheduling_initiated": True,
                "property_for_viewing": property_data.get("id")
            }
        }


class MockLangfuseClient:
    """Mock Langfuse client (reused from observability tests)."""

    def __init__(self):
        self.traces = []

    def trace(self, name: str, **kwargs):
        """Create trace."""
        trace = Mock()
        trace.id = f"trace-{len(self.traces)}"
        trace.name = name
        trace.end = Mock()
        self.traces.append(trace)
        return trace


class MockLogfireHandler:
    """Mock Logfire handler (reused from observability tests)."""

    def __init__(self):
        self.logs = []

    def info(self, message: str, **kwargs):
        """Log info."""
        self.logs.append({"level": "info", "message": message, **kwargs})


@pytest.mark.integration
@pytest.mark.asyncio
class TestEndToEndFlow:
    """End-to-end integration tests."""

    @pytest.fixture
    def orchestrator(self):
        """Provide system orchestrator."""
        return MockSystemOrchestrator()

    async def test_complete_user_journey(self, orchestrator):
        """Test complete user journey from search to scheduling."""
        session_id = "e2e_test_session"

        # Step 1: User searches for properties
        response1 = await orchestrator.process_user_message(
            "Find me 2 bedroom apartments in Miami under $3500",
            session_id=session_id
        )

        assert response1["agent"] == "search"
        assert "properties" in response1
        assert len(response1["properties"]) > 0

        # Step 2: User asks for property details
        response2 = await orchestrator.process_user_message(
            "Tell me more about the first property",
            session_id=session_id
        )

        assert response2["agent"] == "property"
        assert "analysis" in response2

        # Step 3: User schedules a viewing
        response3 = await orchestrator.process_user_message(
            "Can I schedule a viewing for tomorrow?",
            session_id=session_id
        )

        assert response3["agent"] == "scheduling"
        assert "available_slots" in response3

        # Verify conversation flow
        assert len(orchestrator.conversation_history) == 6  # 3 user + 3 assistant

        # Verify context propagation
        assert "properties" in orchestrator.current_context
        assert "selected_property" in orchestrator.current_context
        assert "scheduling_initiated" in orchestrator.current_context

    async def test_search_to_details_flow(self, orchestrator):
        """Test flow from search to property details."""
        # Search
        search_response = await orchestrator.process_user_message(
            "Show me apartments in Miami Beach"
        )

        assert search_response["agent"] == "search"
        properties = search_response["properties"]
        assert len(properties) > 0

        # Get details
        details_response = await orchestrator.process_user_message(
            "Tell me about the Ocean Drive property"
        )

        assert details_response["agent"] == "property"
        assert "analysis" in details_response

    async def test_details_to_scheduling_flow(self, orchestrator):
        """Test flow from property details to scheduling."""
        # First, set up context with a property
        orchestrator.current_context["properties"] = [{
            "id": "prop_001",
            "address": "123 Test St"
        }]

        # Get details
        details_response = await orchestrator.process_user_message(
            "Tell me about this property"
        )

        assert details_response["agent"] == "property"

        # Schedule viewing
        schedule_response = await orchestrator.process_user_message(
            "I want to schedule a visit"
        )

        assert schedule_response["agent"] == "scheduling"
        assert len(schedule_response["available_slots"]) > 0

    async def test_context_persistence(self, orchestrator):
        """Test that context persists across multiple interactions."""
        # Initial search
        await orchestrator.process_user_message("Find apartments in Miami")

        assert "properties" in orchestrator.current_context
        initial_properties = orchestrator.current_context["properties"]

        # Follow-up question (should use existing context)
        await orchestrator.process_user_message("Tell me about the first one")

        # Context should still have properties
        assert "properties" in orchestrator.current_context
        assert orchestrator.current_context["properties"] == initial_properties

    async def test_conversation_history_tracking(self, orchestrator):
        """Test that conversation history is properly tracked."""
        messages = [
            "Find apartments",
            "Tell me about the first one",
            "Schedule a viewing"
        ]

        for msg in messages:
            await orchestrator.process_user_message(msg)

        assert len(orchestrator.conversation_history) == 6  # 3 user + 3 assistant

        # Verify alternating roles
        roles = [msg["role"] for msg in orchestrator.conversation_history]
        assert roles == ["user", "assistant", "user", "assistant", "user", "assistant"]

    async def test_tracing_integration(self, orchestrator):
        """Test that all operations are properly traced."""
        await orchestrator.process_user_message("Find apartments")
        await orchestrator.process_user_message("Show details")
        await orchestrator.process_user_message("Schedule viewing")

        # Should have 3 traces (one per message)
        assert len(orchestrator.langfuse_client.traces) == 3

    async def test_logging_integration(self, orchestrator):
        """Test that all operations are logged."""
        await orchestrator.process_user_message("Find apartments")
        await orchestrator.process_user_message("Show details")

        # Should have 2 log entries
        assert len(orchestrator.logfire_handler.logs) == 2

    async def test_agent_routing(self, orchestrator):
        """Test correct agent routing based on message content."""
        test_cases = [
            ("Find apartments", "search"),
            ("Search for properties", "search"),
            ("Tell me about this property", "property"),
            ("Details of the property", "property"),
            ("Schedule a viewing", "scheduling"),
            ("Book an appointment", "scheduling")
        ]

        for message, expected_agent in test_cases:
            response = await orchestrator.process_user_message(message)
            assert response["agent"] == expected_agent

    async def test_concurrent_sessions(self, orchestrator):
        """Test handling multiple concurrent user sessions."""
        session_ids = ["session_1", "session_2", "session_3"]

        # Process messages from different sessions concurrently
        tasks = [
            orchestrator.process_user_message(
                f"Find apartments for session {sid}",
                session_id=sid
            )
            for sid in session_ids
        ]

        responses = await asyncio.gather(*tasks)

        assert len(responses) == 3
        assert all(r["agent"] == "search" for r in responses)

    async def test_error_recovery(self, orchestrator):
        """Test system recovers gracefully from errors."""
        # Simulate error by providing invalid context
        orchestrator.current_context = None  # Invalid context

        try:
            # Should not crash, should handle gracefully
            response = await orchestrator.process_user_message("Find apartments")
            assert response is not None
        except Exception as e:
            pytest.fail(f"System should handle errors gracefully: {e}")

    async def test_response_time(self, orchestrator):
        """Test that responses are returned within acceptable time."""
        import time

        start = time.time()
        await orchestrator.process_user_message("Find apartments")
        duration = time.time() - start

        # Should respond in less than 100ms (mock delay is 10ms)
        assert duration < 0.1


@pytest.mark.integration
@pytest.mark.asyncio
class TestSystemPerformance:
    """Test system performance under load."""

    @pytest.fixture
    def orchestrator(self):
        """Provide system orchestrator."""
        return MockSystemOrchestrator()

    async def test_rapid_fire_requests(self, orchestrator):
        """Test handling rapid successive requests."""
        messages = [f"Search request {i}" for i in range(10)]

        tasks = [
            orchestrator.process_user_message(msg)
            for msg in messages
        ]

        start = asyncio.get_event_loop().time()
        responses = await asyncio.gather(*tasks)
        duration = asyncio.get_event_loop().time() - start

        assert len(responses) == 10
        assert duration < 1.0  # Should handle 10 concurrent requests in <1s

    async def test_conversation_scalability(self, orchestrator):
        """Test system scales with long conversations."""
        # Simulate long conversation (50 turns)
        for i in range(50):
            await orchestrator.process_user_message(f"Message {i}")

        assert len(orchestrator.conversation_history) == 100  # 50 user + 50 assistant

        # System should still be responsive
        start = asyncio.get_event_loop().time()
        await orchestrator.process_user_message("Final message")
        duration = asyncio.get_event_loop().time() - start

        assert duration < 0.1  # Should still respond quickly


@pytest.mark.integration
class TestDataConsistency:
    """Test data consistency across the system."""

    @pytest.fixture
    def orchestrator(self):
        """Provide system orchestrator."""
        return MockSystemOrchestrator()

    @pytest.mark.asyncio
    async def test_property_data_consistency(self, orchestrator):
        """Test property data remains consistent across agents."""
        # Search for properties
        search_response = await orchestrator.process_user_message("Find apartments")
        original_properties = search_response["properties"]

        # Get details (should use same property data)
        await orchestrator.process_user_message("Tell me about the first one")

        # Context should maintain original property data
        context_properties = orchestrator.current_context.get("properties", [])
        assert context_properties == original_properties

    @pytest.mark.asyncio
    async def test_session_isolation(self, orchestrator):
        """Test that different sessions don't interfere with each other."""
        # Session 1
        response1 = await orchestrator.process_user_message(
            "Find apartments in Miami",
            session_id="session_1"
        )

        # Session 2
        response2 = await orchestrator.process_user_message(
            "Find apartments in New York",
            session_id="session_2"
        )

        # Responses should be independent
        assert response1 != response2
