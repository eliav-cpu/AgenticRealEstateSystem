"""
Tests for Intelligent Router

Validates routing logic, intent detection, and context preservation.
"""

import pytest
from app.agents.router import (
    IntelligentRouter,
    get_router,
    AgentType,
    Intent,
    RoutingDecision,
    ConversationContext
)


class TestIntentDetection:
    """Test intent detection from user messages."""

    def setup_method(self):
        """Set up router instance for tests."""
        self.router = get_router()

    def test_detect_search_intent(self):
        """Test detection of search intent."""
        context = ConversationContext()
        message = "I need a 2 bedroom apartment in Miami"

        intent = self.router.detect_intent(message, context)
        assert intent == Intent.SEARCH

    def test_detect_property_analysis_intent(self):
        """Test detection of property analysis intent."""
        context = ConversationContext()
        message = "Tell me more about this property"

        intent = self.router.detect_intent(message, context)
        assert intent == Intent.PROPERTY_ANALYSIS

    def test_detect_scheduling_intent(self):
        """Test detection of scheduling intent."""
        context = ConversationContext(
            selected_property={"id": 1, "title": "Test Property"}
        )
        message = "Can I schedule a visit for tomorrow?"

        intent = self.router.detect_intent(message, context)
        assert intent == Intent.SCHEDULING

    def test_detect_scheduling_without_property(self):
        """Test scheduling intent without property should detect but with lower confidence."""
        context = ConversationContext()
        message = "I want to schedule a visit"

        # Should still detect scheduling intent
        intent = self.router.detect_intent(message, context)
        # Without property, might be PROPERTY_ANALYSIS or SEARCH depending on keywords
        assert intent in [Intent.SCHEDULING, Intent.UNKNOWN]


class TestRouting:
    """Test routing decisions."""

    def setup_method(self):
        """Set up router instance for tests."""
        self.router = get_router()

    def test_route_to_search(self):
        """Test routing to search agent."""
        state = {
            "messages": [{"role": "user", "content": "Find me apartments in Miami"}],
            "context": {}
        }

        decision = self.router.route("Find me apartments in Miami", state)

        assert decision.target_agent == AgentType.SEARCH
        assert decision.intent == Intent.SEARCH
        assert decision.confidence > 0.8
        assert "search" in decision.handoff_trigger

    def test_route_to_property_with_results(self):
        """Test routing to property agent when search results available."""
        state = {
            "messages": [{"role": "user", "content": "Tell me about the first one"}],
            "search_results": {
                "properties": [{"id": 1, "title": "Test Property"}]
            },
            "context": {}
        }

        decision = self.router.route("Tell me about the first one", state)

        assert decision.target_agent == AgentType.PROPERTY
        assert decision.intent == Intent.PROPERTY_ANALYSIS

    def test_route_to_scheduling_with_property(self):
        """Test routing to scheduling agent with property selected."""
        state = {
            "messages": [{"role": "user", "content": "Schedule visit for tomorrow"}],
            "context": {
                "selected_property": {"id": 1, "title": "Test Property"}
            }
        }

        decision = self.router.route("Schedule visit for tomorrow", state)

        assert decision.target_agent == AgentType.SCHEDULING
        assert decision.intent == Intent.SCHEDULING
        assert decision.confidence > 0.9  # High confidence with property


class TestContextPreservation:
    """Test context preservation during handoffs."""

    def setup_method(self):
        """Set up router instance for tests."""
        self.router = get_router()

    def test_preserve_search_results(self):
        """Test that search results are preserved in routing decision."""
        state = {
            "messages": [{"role": "user", "content": "Show me details"}],
            "search_results": {
                "properties": [{"id": 1}, {"id": 2}],
                "total_count": 2
            },
            "context": {}
        }

        decision = self.router.route("Show me details", state)

        assert "search_results" in decision.context_to_preserve

    def test_preserve_user_preferences(self):
        """Test that user preferences are preserved."""
        state = {
            "messages": [{"role": "user", "content": "Find me more properties"}],
            "context": {
                "user_preferences": {
                    "bedrooms": 2,
                    "max_price": 3000
                }
            }
        }

        decision = self.router.route("Find me more properties", state)

        assert "user_preferences" in decision.context_to_preserve

    def test_preserve_property_on_scheduling(self):
        """Test that property context is preserved when routing to scheduling."""
        selected_property = {"id": 1, "title": "Test Property"}
        state = {
            "messages": [{"role": "user", "content": "Book a visit"}],
            "context": {
                "selected_property": selected_property
            }
        }

        decision = self.router.route("Book a visit", state)

        assert decision.target_agent == AgentType.SCHEDULING
        assert "selected_property" in decision.context_to_preserve
        assert decision.context_to_preserve["selected_property"] == selected_property


class TestHandoffValidation:
    """Test handoff validation rules."""

    def setup_method(self):
        """Set up router instance for tests."""
        self.router = get_router()

    def test_validate_scheduling_requires_property(self):
        """Test that scheduling handoff requires property selection."""
        is_valid, error = self.router.validate_handoff(
            from_agent=AgentType.SEARCH,
            to_agent=AgentType.SCHEDULING,
            context={}  # No property
        )

        assert not is_valid
        assert "property selection" in error.lower()

    def test_validate_scheduling_with_property(self):
        """Test that scheduling handoff succeeds with property."""
        is_valid, error = self.router.validate_handoff(
            from_agent=AgentType.PROPERTY,
            to_agent=AgentType.SCHEDULING,
            context={"selected_property": {"id": 1}}
        )

        assert is_valid
        assert error is None

    def test_prevent_circular_handoffs(self):
        """Test that circular handoffs are prevented."""
        is_valid, error = self.router.validate_handoff(
            from_agent=AgentType.SEARCH,
            to_agent=AgentType.PROPERTY,
            context={"handoff_count": 4}  # Too many handoffs
        )

        assert not is_valid
        assert "loop" in error.lower()


class TestContextBasedRouting:
    """Test context-based routing when intent is unclear."""

    def setup_method(self):
        """Set up router instance for tests."""
        self.router = get_router()

    def test_route_by_context_with_property(self):
        """Test routing defaults to property agent when property selected."""
        state = {
            "messages": [{"role": "user", "content": "What else?"}],
            "context": {
                "selected_property": {"id": 1}
            }
        }

        decision = self.router.route("What else?", state)

        assert decision.target_agent == AgentType.PROPERTY

    def test_route_by_context_with_search_results(self):
        """Test routing defaults to property agent when search results available."""
        state = {
            "messages": [{"role": "user", "content": "Okay"}],
            "search_results": {
                "properties": [{"id": 1}]
            },
            "context": {}
        }

        decision = self.router.route("Okay", state)

        assert decision.target_agent == AgentType.PROPERTY

    def test_route_by_context_default_to_search(self):
        """Test routing defaults to search agent when no context."""
        state = {
            "messages": [{"role": "user", "content": "Hello"}],
            "context": {}
        }

        decision = self.router.route("Hello", state)

        assert decision.target_agent == AgentType.SEARCH


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
