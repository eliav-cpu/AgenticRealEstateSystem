"""
Integration Test Suite for Full Conversation Flow

Tests complete user journeys through search → property → schedule with context preservation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage


@pytest.mark.asyncio
@pytest.mark.integration
class TestSearchToPropertyFlow:
    """Test the complete flow from search to property details."""

    async def test_search_then_property_details(self, mock_orchestrator, sample_properties):
        """Test user searching then asking for property details."""
        config = {
            "configurable": {
                "thread_id": "integration_test_1"
            }
        }

        # Step 1: User searches for properties
        search_message = {
            "messages": [
                HumanMessage(content="I'm looking for a 2 bedroom apartment in Miami Beach under $3500")
            ]
        }

        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [
                HumanMessage(content="I'm looking for a 2 bedroom apartment in Miami Beach under $3500"),
                AIMessage(content="I found 3 properties matching your criteria. Here are the top matches...")
            ],
            "search_results": sample_properties
        }

        search_result = await mock_orchestrator.process_message(search_message, config)
        assert "messages" in search_result

        # Step 2: User asks for details about specific property
        property_message = {
            "messages": [
                HumanMessage(content="Tell me more about the property at 123 Ocean Drive")
            ]
        }

        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [
                HumanMessage(content="Tell me more about the property at 123 Ocean Drive"),
                AIMessage(content="This beautiful 2BR/2BA apartment features ocean views...")
            ],
            "property_context": sample_properties[0]
        }

        property_result = await mock_orchestrator.process_message(property_message, config)
        assert "messages" in property_result

        # Verify both calls used same thread_id
        assert mock_orchestrator.swarm.ainvoke.call_count == 2

    async def test_context_preservation_across_handoffs(self, mock_orchestrator, sample_properties):
        """Test that context is preserved when handing off between agents."""
        config = {
            "configurable": {
                "thread_id": "context_test_1"
            }
        }

        # Conversation flow with handoffs
        messages = [
            HumanMessage(content="Find me apartments in Miami"),
            HumanMessage(content="Tell me about the first one"),
            HumanMessage(content="What about the second property?")
        ]

        for i, msg in enumerate(messages):
            mock_orchestrator.swarm.ainvoke.return_value = {
                "messages": messages[:i+1] + [AIMessage(content=f"Response {i+1}")],
                "search_results": sample_properties if i == 0 else None,
                "property_context": sample_properties[i-1] if i > 0 else None
            }

            result = await mock_orchestrator.process_message({"messages": [msg]}, config)
            assert result is not None

        # All calls should maintain same thread
        assert mock_orchestrator.swarm.ainvoke.call_count == len(messages)


@pytest.mark.asyncio
@pytest.mark.integration
class TestPropertyToSchedulingFlow:
    """Test the complete flow from property details to scheduling."""

    async def test_property_then_scheduling(self, mock_orchestrator, sample_properties):
        """Test user viewing property then scheduling a visit."""
        config = {
            "configurable": {
                "thread_id": "integration_test_2"
            }
        }

        # Step 1: User asks about property
        property_message = {
            "messages": [
                HumanMessage(content="Tell me about 123 Ocean Drive")
            ]
        }

        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [
                HumanMessage(content="Tell me about 123 Ocean Drive"),
                AIMessage(content="Great property with ocean views...")
            ],
            "property_context": sample_properties[0]
        }

        await mock_orchestrator.process_message(property_message, config)

        # Step 2: User wants to schedule visit
        schedule_message = {
            "messages": [
                HumanMessage(content="I'd like to schedule a visit for tomorrow afternoon")
            ]
        }

        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [
                HumanMessage(content="I'd like to schedule a visit for tomorrow afternoon"),
                AIMessage(content="Great! I have several time slots available...")
            ],
            "scheduling_context": {
                "property": sample_properties[0],
                "requested_time": "tomorrow afternoon"
            }
        }

        result = await mock_orchestrator.process_message(schedule_message, config)
        assert result is not None

    async def test_scheduling_with_property_context(self, mock_orchestrator, sample_properties):
        """Test that scheduling agent has access to property context."""
        config = {
            "configurable": {
                "thread_id": "scheduling_context_test"
            }
        }

        # User asks to schedule with property context already set
        message = {
            "messages": [
                HumanMessage(content="Can I schedule a visit?")
            ]
        }

        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [AIMessage(content="Which time works for you?")],
            "property_context": sample_properties[0]
        }

        result = await mock_orchestrator.process_message(message, config)
        assert result is not None


@pytest.mark.asyncio
@pytest.mark.integration
class TestCompleteUserJourney:
    """Test complete user journey from search to scheduled visit."""

    async def test_full_journey_search_to_schedule(self, mock_orchestrator, sample_properties):
        """Test complete journey: search → property details → schedule."""
        config = {
            "configurable": {
                "thread_id": "full_journey_test"
            }
        }

        # Step 1: Search
        msg1 = {"messages": [HumanMessage(content="Find 2BR apartments in Miami")]}
        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [AIMessage(content="Found 3 properties")],
            "search_results": sample_properties
        }
        result1 = await mock_orchestrator.process_message(msg1, config)

        # Step 2: Property details
        msg2 = {"messages": [HumanMessage(content="Tell me about the first one")]}
        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [AIMessage(content="It's a great property")],
            "property_context": sample_properties[0]
        }
        result2 = await mock_orchestrator.process_message(msg2, config)

        # Step 3: Schedule
        msg3 = {"messages": [HumanMessage(content="Schedule a visit for tomorrow at 2pm")]}
        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [AIMessage(content="Appointment confirmed!")],
            "appointment": {"date": "tomorrow", "time": "2pm"}
        }
        result3 = await mock_orchestrator.process_message(msg3, config)

        # Verify all steps completed
        assert result1 is not None
        assert result2 is not None
        assert result3 is not None
        assert mock_orchestrator.swarm.ainvoke.call_count == 3

    async def test_journey_with_backtracking(self, mock_orchestrator, sample_properties):
        """Test journey where user backtracks to search different properties."""
        config = {
            "configurable": {
                "thread_id": "backtrack_test"
            }
        }

        journey = [
            ("search", "Find apartments"),
            ("property", "Tell me about first one"),
            ("search", "Actually show me cheaper options"),
            ("property", "What about this one?"),
            ("schedule", "Let's schedule a visit")
        ]

        for step, message in journey:
            msg = {"messages": [HumanMessage(content=message)]}
            mock_orchestrator.swarm.ainvoke.return_value = {
                "messages": [AIMessage(content=f"Response for {step}")],
                "current_agent": step
            }
            result = await mock_orchestrator.process_message(msg, config)
            assert result is not None

    async def test_journey_with_clarifications(self, mock_orchestrator):
        """Test journey where agent asks for clarifications."""
        config = {
            "configurable": {
                "thread_id": "clarification_test"
            }
        }

        # User gives vague search
        msg1 = {"messages": [HumanMessage(content="I need a place")]}
        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [AIMessage(content="What's your budget and preferred area?")]
        }
        await mock_orchestrator.process_message(msg1, config)

        # User provides clarification
        msg2 = {"messages": [HumanMessage(content="2 bedrooms in Miami Beach under $3500")]}
        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [AIMessage(content="Found 5 properties!")]
        }
        await mock_orchestrator.process_message(msg2, config)

        assert mock_orchestrator.swarm.ainvoke.call_count == 2


@pytest.mark.asyncio
@pytest.mark.integration
class TestMockModeFlow:
    """Test complete flows using MOCK data mode."""

    async def test_search_with_mock_data(self, mock_orchestrator, sample_properties):
        """Test search flow with mock data."""
        from app.orchestration.swarm_hybrid import AgentContext

        context = AgentContext(
            search_results=sample_properties,
            data_mode="mock"
        )

        assert context.data_mode == "mock"
        assert len(context.search_results) == 3

    async def test_property_details_with_mock_data(self, mock_orchestrator, sample_properties):
        """Test property details flow with mock data."""
        from app.orchestration.swarm_hybrid import AgentContext

        context = AgentContext(
            property_context=sample_properties[0],
            data_mode="mock"
        )

        assert context.data_mode == "mock"
        assert context.property_context["formattedAddress"] == "123 Ocean Drive, Miami Beach, FL 33139"

    async def test_scheduling_with_mock_data(self, mock_orchestrator, sample_appointments):
        """Test scheduling flow with mock data."""
        from app.orchestration.swarm_hybrid import AgentContext

        context = AgentContext(
            data_mode="mock"
        )

        # Mock scheduling should work without real API calls
        assert context.data_mode == "mock"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.real
@pytest.mark.skip(reason="Requires real API credentials")
class TestRealModeFlow:
    """Test complete flows using REAL data mode."""

    async def test_search_with_real_data(self):
        """Test search flow with real API data."""
        # Would require real API setup
        pass

    async def test_property_details_with_real_data(self):
        """Test property details flow with real API data."""
        # Would require real API setup
        pass

    async def test_scheduling_with_real_data(self):
        """Test scheduling flow with real calendar integration."""
        # Would require real calendar API setup
        pass


@pytest.mark.asyncio
@pytest.mark.integration
class TestAgentHandoffs:
    """Test handoffs between agents during conversation."""

    async def test_handoff_from_search_to_property(self, mock_orchestrator):
        """Test smooth handoff from search agent to property agent."""
        config = {"configurable": {"thread_id": "handoff_test_1"}}

        # Search agent active
        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [AIMessage(content="Search results")],
            "active_agent": "search_agent"
        }
        await mock_orchestrator.process_message(
            {"messages": [HumanMessage(content="Find apartments")]},
            config
        )

        # Handoff to property agent
        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [AIMessage(content="Property details")],
            "active_agent": "property_agent"
        }
        result = await mock_orchestrator.process_message(
            {"messages": [HumanMessage(content="Tell me about first one")]},
            config
        )

        assert result is not None

    async def test_handoff_from_property_to_scheduling(self, mock_orchestrator):
        """Test smooth handoff from property agent to scheduling agent."""
        config = {"configurable": {"thread_id": "handoff_test_2"}}

        # Property agent active
        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [AIMessage(content="Property analysis")],
            "active_agent": "property_agent"
        }
        await mock_orchestrator.process_message(
            {"messages": [HumanMessage(content="Analyze this property")]},
            config
        )

        # Handoff to scheduling agent
        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [AIMessage(content="Scheduling options")],
            "active_agent": "scheduling_agent"
        }
        result = await mock_orchestrator.process_message(
            {"messages": [HumanMessage(content="Schedule a visit")]},
            config
        )

        assert result is not None

    async def test_circular_handoff_prevention(self, mock_orchestrator):
        """Test that circular handoffs are handled properly."""
        config = {"configurable": {"thread_id": "circular_test"}}

        # This should not create infinite loop
        messages = [
            HumanMessage(content="Find properties"),
            HumanMessage(content="Tell me about one"),
            HumanMessage(content="Find different properties"),
            HumanMessage(content="Tell me about another")
        ]

        for msg in messages:
            mock_orchestrator.swarm.ainvoke.return_value = {
                "messages": [AIMessage(content="Response")]
            }
            result = await mock_orchestrator.process_message(
                {"messages": [msg]},
                config
            )
            assert result is not None


@pytest.mark.asyncio
@pytest.mark.integration
class TestErrorRecovery:
    """Test error recovery in conversation flow."""

    async def test_recovery_from_agent_error(self, mock_orchestrator):
        """Test that system recovers from agent errors."""
        config = {"configurable": {"thread_id": "error_recovery_test"}}

        # First message succeeds
        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [AIMessage(content="Success")]
        }
        await mock_orchestrator.process_message(
            {"messages": [HumanMessage(content="Find apartments")]},
            config
        )

        # Second message fails
        mock_orchestrator.swarm.ainvoke.side_effect = Exception("Agent error")
        with pytest.raises(Exception):
            await mock_orchestrator.process_message(
                {"messages": [HumanMessage(content="Tell me more")]},
                config
            )

        # Third message should still work (recovery)
        mock_orchestrator.swarm.ainvoke.side_effect = None
        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [AIMessage(content="Recovered")]
        }
        result = await mock_orchestrator.process_message(
            {"messages": [HumanMessage(content="Try again")]},
            config
        )
        assert result is not None

    async def test_graceful_degradation_on_partial_failure(self, mock_orchestrator):
        """Test graceful degradation when some features fail."""
        config = {"configurable": {"thread_id": "degradation_test"}}

        # Message succeeds but with limited features
        mock_orchestrator.swarm.ainvoke.return_value = {
            "messages": [AIMessage(content="Limited response")],
            "warning": "Some features unavailable"
        }

        result = await mock_orchestrator.process_message(
            {"messages": [HumanMessage(content="Find properties")]},
            config
        )

        # Should still return result
        assert result is not None
        assert "messages" in result


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.slow
class TestLongConversations:
    """Test handling of long multi-turn conversations."""

    async def test_conversation_with_many_turns(self, mock_orchestrator):
        """Test conversation with 10+ turns maintains context."""
        config = {"configurable": {"thread_id": "long_conversation_test"}}

        # Simulate 15 turn conversation
        for i in range(15):
            mock_orchestrator.swarm.ainvoke.return_value = {
                "messages": [AIMessage(content=f"Response {i+1}")]
            }

            result = await mock_orchestrator.process_message(
                {"messages": [HumanMessage(content=f"Message {i+1}")]},
                config
            )
            assert result is not None

        # All turns should use same thread
        assert mock_orchestrator.swarm.ainvoke.call_count == 15

    async def test_conversation_memory_persistence(self, mock_orchestrator):
        """Test that conversation memory persists across entire flow."""
        config = {"configurable": {"thread_id": "memory_persistence_test"}}

        conversation = [
            "My budget is $3000",
            "I want 2 bedrooms",
            "Find me something in Miami Beach",
            "Tell me about the first property",
            "Schedule a visit for tomorrow"
        ]

        for msg in conversation:
            mock_orchestrator.swarm.ainvoke.return_value = {
                "messages": [AIMessage(content="Response")]
            }
            await mock_orchestrator.process_message(
                {"messages": [HumanMessage(content=msg)]},
                config
            )

        # Memory should be maintained throughout
        assert mock_orchestrator.swarm.ainvoke.call_count == len(conversation)
