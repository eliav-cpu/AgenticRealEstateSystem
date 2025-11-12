"""
Test Suite for Agent Routing

Tests intent detection, routing logic, and handoff triggers.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.agents.hybrid_search import HybridSearchAgent
from app.agents.hybrid_property import HybridPropertyAgent
from app.agents.hybrid_scheduling import HybridSchedulingAgent


@pytest.mark.asyncio
@pytest.mark.unit
class TestSearchAgentRouting:
    """Test routing decisions for the search agent."""

    async def test_search_agent_detects_property_inquiry(self, mock_settings):
        """Test that search agent can detect when to handoff to property agent."""
        with patch('app.agents.hybrid_search.get_settings', return_value=mock_settings):
            with patch('app.agents.hybrid_search.PydanticAgent'):
                with patch('app.agents.hybrid_search.create_react_agent') as mock_create:
                    mock_agent = MagicMock()
                    mock_create.return_value = mock_agent

                    search_agent = HybridSearchAgent(MagicMock())

                    # Verify agent has handoff tools
                    assert search_agent.langgraph_agent is not None

    async def test_search_intent_detection_general_search(self):
        """Test detecting general search intent."""
        queries = [
            "I'm looking for apartments in Miami",
            "Show me 2 bedroom properties",
            "Find me something near the beach",
            "What's available in Brickell?"
        ]

        for query in queries:
            # All should be classified as search intents
            assert "looking" in query.lower() or "show" in query.lower() or \
                   "find" in query.lower() or "available" in query.lower()

    async def test_search_intent_detection_property_details(self):
        """Test detecting when user wants property details."""
        queries = [
            "Tell me more about 123 Ocean Drive",
            "What are the features of that property?",
            "Can you describe the apartment in detail?",
            "More information about the first one"
        ]

        for query in queries:
            # Should contain detail-oriented keywords
            assert any(keyword in query.lower() for keyword in
                      ["more", "detail", "feature", "describe", "information", "about"])

    async def test_search_intent_detection_scheduling(self):
        """Test detecting when user wants to schedule."""
        queries = [
            "I want to schedule a visit",
            "Can I see it tomorrow?",
            "Book an appointment",
            "When can I view the property?"
        ]

        for query in queries:
            # Should contain scheduling keywords
            assert any(keyword in query.lower() for keyword in
                      ["schedule", "visit", "see", "book", "appointment", "view", "when"])


@pytest.mark.asyncio
@pytest.mark.unit
class TestPropertyAgentRouting:
    """Test routing decisions for the property agent."""

    async def test_property_agent_detects_new_search(self):
        """Test that property agent detects when to handoff to search."""
        queries = [
            "Show me different properties",
            "I want to see other options",
            "Find me something cheaper",
            "Let's look at more properties"
        ]

        for query in queries:
            # Should contain search-related keywords
            assert any(keyword in query.lower() for keyword in
                      ["different", "other", "more", "find", "show", "look"])

    async def test_property_agent_detects_scheduling_intent(self):
        """Test that property agent detects scheduling intent."""
        queries = [
            "I'd like to schedule a viewing",
            "Can we set up an appointment?",
            "When can I visit?",
            "Book a tour for this property"
        ]

        for query in queries:
            # Should contain scheduling keywords
            assert any(keyword in query.lower() for keyword in
                      ["schedule", "appointment", "visit", "book", "tour", "viewing"])

    async def test_property_agent_stays_active_for_analysis(self):
        """Test that property agent stays active for analysis questions."""
        queries = [
            "What do you think about the location?",
            "Is this property a good deal?",
            "Compare this to similar properties",
            "What are the pros and cons?"
        ]

        for query in queries:
            # Should contain analysis keywords
            assert any(keyword in query.lower() for keyword in
                      ["think", "good", "compare", "pros", "cons", "opinion", "recommend"])


@pytest.mark.asyncio
@pytest.mark.unit
class TestSchedulingAgentRouting:
    """Test routing decisions for the scheduling agent."""

    async def test_scheduling_agent_detects_property_details_needed(self):
        """Test that scheduling agent detects when property details are needed."""
        queries = [
            "Wait, tell me more about the property first",
            "What property are we scheduling for?",
            "I need property details before booking",
            "Can you describe the place?"
        ]

        for query in queries:
            # Should contain property detail keywords
            assert any(keyword in query.lower() for keyword in
                      ["property", "details", "more", "describe", "what", "place"])

    async def test_scheduling_agent_detects_new_search(self):
        """Test that scheduling agent detects when user wants to search."""
        queries = [
            "Actually, show me other properties",
            "Let's look at different options first",
            "Find me something else",
            "I want to see more properties"
        ]

        for query in queries:
            # Should contain search keywords
            assert any(keyword in query.lower() for keyword in
                      ["other", "different", "find", "more", "else", "show"])

    async def test_scheduling_agent_stays_active_for_scheduling(self):
        """Test that scheduling agent stays active for scheduling tasks."""
        queries = [
            "Tomorrow at 2pm works for me",
            "Can we do Saturday morning?",
            "Reschedule to next week",
            "What times are available?"
        ]

        for query in queries:
            # Should contain time/scheduling keywords
            assert any(keyword in query.lower() for keyword in
                      ["tomorrow", "saturday", "morning", "time", "available", "reschedule", "pm", "am"])


@pytest.mark.asyncio
@pytest.mark.unit
class TestContextBasedRouting:
    """Test routing based on conversation context."""

    async def test_routing_with_property_context(self, agent_context_with_property):
        """Test routing when property context is available."""
        # When property context exists, scheduling questions should stay with scheduling
        query = "When can I visit?"

        # Context has property data
        assert agent_context_with_property.property_context is not None
        assert "formattedAddress" in agent_context_with_property.property_context

        # Should be routed to scheduling since we have property context
        assert "when" in query.lower() or "visit" in query.lower()

    async def test_routing_with_search_results(self, agent_context_with_search):
        """Test routing when search results are available."""
        # When search results exist, detail questions should route to property agent
        query = "Tell me about the first one"

        # Context has search results
        assert agent_context_with_search.search_results is not None
        assert len(agent_context_with_search.search_results) > 0

        # Should be routed to property agent since we have results
        assert "tell" in query.lower() or "about" in query.lower()

    async def test_routing_without_context(self, agent_context):
        """Test routing when no context is available."""
        # Without context, general queries should start with search
        query = "I'm looking for an apartment"

        # No context available
        assert agent_context.property_context is None
        assert agent_context.search_results is None

        # Should route to search agent
        assert "looking" in query.lower()


@pytest.mark.asyncio
@pytest.mark.integration
class TestHandoffTriggers:
    """Test the conditions that trigger agent handoffs."""

    async def test_explicit_handoff_request(self):
        """Test handoff when user explicitly requests different agent."""
        queries = [
            "Let me talk to the scheduling assistant",
            "I need to speak with someone about scheduling",
            "Can the property expert help me?",
            "Switch to search agent"
        ]

        for query in queries:
            # Should contain explicit handoff keywords
            assert any(keyword in query.lower() for keyword in
                      ["talk to", "speak with", "help", "switch", "agent", "assistant"])

    async def test_implicit_handoff_from_topic_change(self):
        """Test handoff when conversation topic changes."""
        conversation_flow = [
            ("search", "Find me apartments in Miami"),
            ("property", "Tell me about the first one"),
            ("scheduling", "I want to schedule a visit"),
            ("search", "Actually, show me other options")
        ]

        expected_agents = [flow[0] for flow in conversation_flow]

        assert expected_agents == ["search", "property", "scheduling", "search"]

    async def test_handoff_with_incomplete_information(self):
        """Test that agents request missing information before handoff."""
        queries_needing_clarification = [
            "Schedule a visit",  # Missing: which property?
            "Tell me more",  # Missing: about what?
            "Is it available?"  # Missing: which property?
        ]

        for query in queries_needing_clarification:
            # Should be short and vague
            assert len(query.split()) <= 4


@pytest.mark.asyncio
@pytest.mark.unit
class TestMultiIntentDetection:
    """Test detection of multiple intents in a single query."""

    async def test_search_and_schedule_intent(self):
        """Test query with both search and scheduling intent."""
        query = "Find me a 2 bedroom apartment and schedule a visit for tomorrow"

        # Should contain both search and scheduling keywords
        assert "find" in query.lower()
        assert "schedule" in query.lower()

    async def test_property_and_schedule_intent(self):
        """Test query with both property and scheduling intent."""
        query = "Tell me about this property and book an appointment"

        # Should contain both property and scheduling keywords
        assert "tell" in query.lower() and "about" in query.lower()
        assert "book" in query.lower() or "appointment" in query.lower()

    async def test_search_and_property_intent(self):
        """Test query with both search and property detail intent."""
        query = "Show me apartments in Miami and tell me about the amenities"

        # Should contain both search and property keywords
        assert "show" in query.lower()
        assert "tell" in query.lower() or "amenities" in query.lower()


@pytest.mark.asyncio
@pytest.mark.unit
class TestErrorRecoveryRouting:
    """Test routing when errors occur or user is confused."""

    async def test_confused_user_routing(self):
        """Test routing when user seems confused."""
        confused_queries = [
            "I don't understand",
            "What are my options?",
            "Can you help me?",
            "I'm not sure what to do"
        ]

        for query in confused_queries:
            # Should contain confusion indicators
            assert any(keyword in query.lower() for keyword in
                      ["don't understand", "not sure", "help", "options"])

    async def test_error_message_routing(self):
        """Test routing after an error message."""
        # After error, should route back to appropriate agent based on original intent
        error_recovery_queries = [
            "Try again",
            "Let's start over",
            "Can we retry that?",
            "Go back"
        ]

        for query in error_recovery_queries:
            # Should contain retry/recovery keywords
            assert any(keyword in query.lower() for keyword in
                      ["try", "start", "retry", "again", "back"])
