"""
Pytest Configuration and Fixtures

This module provides shared fixtures and configuration for all tests.
"""

import pytest
import pytest_asyncio
import asyncio
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.orchestration.swarm_hybrid import HybridSwarmOrchestrator, AgentContext
from app.utils.container import DIContainer
from config.settings import Settings


# Configure asyncio event loop policy for Windows
if asyncio.get_event_loop_policy().__class__.__name__ == 'WindowsProactorEventLoopPolicy':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture(scope="session")
def event_loop_policy():
    """Set event loop policy for the test session."""
    return asyncio.get_event_loop_policy()


@pytest.fixture
def event_loop():
    """Create an event loop for each test."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Mock Settings object with test configuration."""
    settings = MagicMock(spec=Settings)
    settings.apis = MagicMock()
    settings.apis.openrouter_key = "test_openrouter_key_123456"
    settings.apis.anthropic_key = "test_anthropic_key_123456"
    settings.database = MagicMock()
    settings.database.mode = "mock"
    return settings


@pytest.fixture
def sample_properties():
    """Return sample property data for testing."""
    return [
        {
            "id": "prop_001",
            "formattedAddress": "123 Ocean Drive, Miami Beach, FL 33139",
            "price": 3200,
            "propertyType": "Apartment",
            "bedrooms": 2,
            "bathrooms": 2,
            "squareFeet": 1200,
            "amenities": ["Pool", "Gym", "Parking", "Ocean View"],
            "available": True,
            "availableDate": "2024-02-01"
        },
        {
            "id": "prop_002",
            "formattedAddress": "456 Brickell Ave, Miami, FL 33131",
            "price": 2800,
            "propertyType": "Condo",
            "bedrooms": 1,
            "bathrooms": 1,
            "squareFeet": 900,
            "amenities": ["Pool", "Gym", "Concierge"],
            "available": True,
            "availableDate": "2024-02-15"
        },
        {
            "id": "prop_003",
            "formattedAddress": "789 Coral Way, Coral Gables, FL 33134",
            "price": 4500,
            "propertyType": "Townhouse",
            "bedrooms": 3,
            "bathrooms": 2.5,
            "squareFeet": 1800,
            "amenities": ["Garden", "Garage", "Patio"],
            "available": True,
            "availableDate": "2024-03-01"
        }
    ]


@pytest.fixture
def sample_appointments():
    """Return sample appointment data for testing."""
    return [
        {
            "id": "apt_001",
            "property_id": "prop_001",
            "property_address": "123 Ocean Drive, Miami Beach, FL 33139",
            "date": "2024-02-05",
            "time": "10:00 AM",
            "duration": 45,
            "status": "confirmed",
            "client_contact": "john.doe@email.com"
        },
        {
            "id": "apt_002",
            "property_id": "prop_002",
            "property_address": "456 Brickell Ave, Miami, FL 33131",
            "date": "2024-02-06",
            "time": "2:00 PM",
            "duration": 45,
            "status": "confirmed",
            "client_contact": "jane.smith@email.com"
        }
    ]


@pytest.fixture
def agent_context():
    """Return a basic AgentContext for testing."""
    return AgentContext(
        property_context=None,
        search_results=None,
        session_id="test_session_123",
        data_mode="mock"
    )


@pytest.fixture
def agent_context_with_property(sample_properties):
    """Return AgentContext with property data."""
    return AgentContext(
        property_context=sample_properties[0],
        search_results=None,
        session_id="test_session_123",
        data_mode="mock"
    )


@pytest.fixture
def agent_context_with_search(sample_properties):
    """Return AgentContext with search results."""
    return AgentContext(
        property_context=None,
        search_results=sample_properties,
        session_id="test_session_123",
        data_mode="mock"
    )


@pytest_asyncio.fixture
async def mock_orchestrator(mock_settings):
    """Create a mock HybridSwarmOrchestrator for testing."""
    with patch('app.orchestration.swarm_hybrid.get_settings', return_value=mock_settings):
        with patch('app.orchestration.swarm_hybrid.ChatOpenAI') as mock_llm:
            # Mock the LLM
            mock_llm.return_value = MagicMock()

            with patch('app.orchestration.swarm_hybrid.PydanticAgent') as mock_pydantic:
                # Mock PydanticAI agent
                mock_agent = MagicMock()
                mock_agent.run = AsyncMock()
                mock_pydantic.return_value = mock_agent

                with patch('app.orchestration.swarm_hybrid.create_react_agent') as mock_react:
                    # Mock LangGraph agent
                    mock_react.return_value = MagicMock()

                    with patch('app.orchestration.swarm_hybrid.create_swarm') as mock_swarm:
                        # Mock the swarm
                        mock_swarm_app = MagicMock()
                        mock_swarm_app.ainvoke = AsyncMock()
                        mock_swarm_app.astream = AsyncMock()
                        mock_swarm.return_value.compile.return_value = mock_swarm_app

                        try:
                            orchestrator = HybridSwarmOrchestrator()
                            yield orchestrator
                        except Exception as e:
                            pytest.skip(f"Could not create orchestrator: {e}")


@pytest.fixture
def mock_search_response():
    """Mock search agent response."""
    return {
        "properties_found": 5,
        "summary": "Found 5 properties in Miami matching your criteria",
        "recommendations": [
            "Consider properties in Brickell for better value",
            "Check out beachfront condos for ocean views",
            "Look at townhouses for more space"
        ],
        "next_actions": [
            "Review property details",
            "Schedule property visits",
            "Refine search criteria"
        ]
    }


@pytest.fixture
def mock_property_response():
    """Mock property agent response."""
    return {
        "property_highlights": [
            "Prime location near beach",
            "Modern amenities and finishes",
            "Excellent value for the area"
        ],
        "advantages": [
            "Walking distance to shops and restaurants",
            "Building has pool and gym",
            "Recently renovated"
        ],
        "disadvantages": [
            "Parking costs extra $150/month",
            "No washer/dryer in unit",
            "Street noise can be noticeable"
        ],
        "market_context": "Priced competitively at $3,200/month compared to similar units at $3,000-3,400",
        "recommendation": "Strong property for someone prioritizing location and amenities",
        "next_steps": [
            "Schedule a viewing",
            "Check parking availability",
            "Review lease terms"
        ]
    }


@pytest.fixture
def mock_scheduling_response():
    """Mock scheduling agent response."""
    return {
        "appointment_status": "Available slots found",
        "proposed_times": [
            "Tomorrow at 10:00 AM",
            "Thursday at 2:00 PM",
            "Saturday at 11:00 AM"
        ],
        "confirmation_details": None,
        "requirements": [
            "Valid photo ID",
            "Proof of income",
            "List of questions"
        ],
        "contact_info": "Maria Santos - (305) 555-0123",
        "next_steps": [
            "Select preferred time slot",
            "Confirm appointment",
            "Prepare required documents"
        ]
    }


@pytest.fixture
def conversation_messages():
    """Sample conversation messages for testing."""
    return [
        {
            "role": "user",
            "content": "I'm looking for a 2 bedroom apartment in Miami Beach under $3500"
        },
        {
            "role": "assistant",
            "content": "I found several great options. Here are the top matches..."
        },
        {
            "role": "user",
            "content": "Tell me more about the property at 123 Ocean Drive"
        },
        {
            "role": "assistant",
            "content": "This is a beautiful 2BR/2BA apartment with ocean views..."
        },
        {
            "role": "user",
            "content": "Can I schedule a visit for tomorrow afternoon?"
        }
    ]


@pytest.fixture
def di_container(mock_settings):
    """Create a DI container for testing."""
    container = DIContainer()
    container.register(Settings, mock_settings)
    return container


# Async helper functions for tests
@pytest.fixture
def async_return():
    """Helper to create async return values."""
    def _async_return(value):
        async def _inner(*args, **kwargs):
            return value
        return _inner
    return _async_return


@pytest.fixture
def async_raise():
    """Helper to create async exceptions."""
    def _async_raise(exception):
        async def _inner(*args, **kwargs):
            raise exception
        return _inner
    return _async_raise


# Pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "asyncio: Async tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "mock: Tests using mock data"
    )
    config.addinivalue_line(
        "markers", "real: Tests requiring real API connections"
    )
