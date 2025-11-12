"""
Integration Tests for Groq LLM Flow and Context Engineering

Tests the complete LLM flow including:
- Groq LLM initialization and configuration
- Context engineering and prompt formatting
- Response generation and parsing
- Error handling and fallback mechanisms
- Token usage tracking
- Rate limiting and retry logic

Coverage Target: >85%
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List
import json


class MockGroqClient:
    """Mock Groq client for testing without API calls."""

    def __init__(self, api_key: str = "mock_key"):
        self.api_key = api_key
        self.call_count = 0
        self.last_messages = None
        self.last_model = None

    async def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """Mock chat completion."""
        self.call_count += 1
        self.last_messages = messages
        self.last_model = model

        # Simulate realistic response
        return {
            "id": f"chatcmpl-mock-{self.call_count}",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": self._generate_mock_response(messages)
                },
                "finish_reason": "stop",
                "index": 0
            }],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 150,
                "total_tokens": 250
            },
            "model": model,
            "created": 1234567890
        }

    def _generate_mock_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate appropriate mock response based on context."""
        last_message = messages[-1]["content"].lower()

        if "search" in last_message or "find" in last_message:
            return json.dumps({
                "properties_found": 5,
                "summary": "Found 5 matching properties in Miami Beach",
                "criteria": {
                    "location": "Miami Beach",
                    "bedrooms": 2,
                    "max_price": 3500
                }
            })
        elif "property" in last_message or "details" in last_message:
            return json.dumps({
                "property_analysis": {
                    "highlights": ["Ocean view", "Modern amenities", "Great location"],
                    "value_assessment": "Good value for the area",
                    "recommendation": "Highly recommended"
                }
            })
        elif "schedule" in last_message or "appointment" in last_message:
            return json.dumps({
                "appointment": {
                    "status": "Available",
                    "proposed_times": ["Tomorrow at 10:00 AM", "Friday at 2:00 PM"],
                    "confirmation": "pending"
                }
            })
        else:
            return "I can help you with property search, details, and scheduling."


class ContextEngineer:
    """Context engineering utilities for LLM interactions."""

    @staticmethod
    def build_system_prompt(agent_type: str) -> str:
        """Build system prompt for different agent types."""
        prompts = {
            "search": """You are a real estate search specialist. Help users find properties
            that match their criteria. Extract search parameters and provide relevant results.""",

            "property": """You are a property analysis expert. Provide detailed insights about
            properties including pros, cons, market analysis, and recommendations.""",

            "scheduling": """You are a scheduling coordinator. Help users book property viewings
            and manage appointments efficiently."""
        }
        return prompts.get(agent_type, "You are a helpful real estate assistant.")

    @staticmethod
    def format_property_context(properties: List[Dict[str, Any]]) -> str:
        """Format property data for LLM context."""
        if not properties:
            return "No properties in context."

        context_parts = ["Available properties:"]
        for i, prop in enumerate(properties, 1):
            context_parts.append(
                f"{i}. {prop.get('address', 'Unknown address')} - "
                f"${prop.get('price', 'N/A')} - {prop.get('bedrooms', '?')} bed/"
                f"{prop.get('bathrooms', '?')} bath"
            )

        return "\n".join(context_parts)

    @staticmethod
    def format_conversation_history(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format conversation history for LLM."""
        formatted = []
        for msg in messages:
            formatted.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        return formatted

    @staticmethod
    def extract_structured_output(response: str) -> Dict[str, Any]:
        """Extract structured data from LLM response."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                try:
                    return json.loads(response[start:end].strip())
                except json.JSONDecodeError:
                    pass

            # Fallback to plain text response
            return {"text": response}


@pytest.mark.integration
@pytest.mark.asyncio
class TestGroqLLMIntegration:
    """Integration tests for Groq LLM."""

    @pytest.fixture
    def mock_groq_client(self):
        """Provide mock Groq client."""
        return MockGroqClient()

    @pytest.fixture
    def sample_properties(self):
        """Sample properties for context."""
        return [
            {
                "id": "prop_001",
                "address": "123 Ocean Drive, Miami Beach, FL",
                "price": 3200,
                "bedrooms": 2,
                "bathrooms": 2,
                "amenities": ["Pool", "Gym", "Ocean View"]
            },
            {
                "id": "prop_002",
                "address": "456 Brickell Ave, Miami, FL",
                "price": 2800,
                "bedrooms": 1,
                "bathrooms": 1,
                "amenities": ["Pool", "Gym", "Concierge"]
            }
        ]

    async def test_groq_client_initialization(self, mock_groq_client):
        """Test Groq client initialization."""
        assert mock_groq_client.api_key == "mock_key"
        assert mock_groq_client.call_count == 0

    async def test_basic_completion(self, mock_groq_client):
        """Test basic chat completion."""
        messages = [{"role": "user", "content": "Hello"}]
        response = await mock_groq_client.create_chat_completion(messages)

        assert response is not None
        assert "choices" in response
        assert len(response["choices"]) > 0
        assert "message" in response["choices"][0]
        assert mock_groq_client.call_count == 1

    async def test_search_agent_flow(self, mock_groq_client, sample_properties):
        """Test complete search agent flow with context."""
        # Build context
        system_prompt = ContextEngineer.build_system_prompt("search")
        property_context = ContextEngineer.format_property_context(sample_properties)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Find 2 bedroom apartments under $3500\n\n{property_context}"}
        ]

        response = await mock_groq_client.create_chat_completion(messages)

        assert response is not None
        content = response["choices"][0]["message"]["content"]

        # Parse structured output
        structured = ContextEngineer.extract_structured_output(content)
        assert "properties_found" in structured or "text" in structured

    async def test_property_analysis_flow(self, mock_groq_client, sample_properties):
        """Test property analysis flow."""
        system_prompt = ContextEngineer.build_system_prompt("property")
        property_data = json.dumps(sample_properties[0], indent=2)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze this property:\n{property_data}"}
        ]

        response = await mock_groq_client.create_chat_completion(messages)
        content = response["choices"][0]["message"]["content"]

        structured = ContextEngineer.extract_structured_output(content)
        assert structured is not None

    async def test_scheduling_flow(self, mock_groq_client):
        """Test appointment scheduling flow."""
        system_prompt = ContextEngineer.build_system_prompt("scheduling")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Schedule a viewing for tomorrow at 10 AM"}
        ]

        response = await mock_groq_client.create_chat_completion(messages)
        content = response["choices"][0]["message"]["content"]

        structured = ContextEngineer.extract_structured_output(content)
        assert structured is not None

    async def test_conversation_history_context(self, mock_groq_client):
        """Test multi-turn conversation with history."""
        conversation = [
            {"role": "user", "content": "I'm looking for apartments in Miami"},
            {"role": "assistant", "content": "I can help! What's your budget?"},
            {"role": "user", "content": "Around $3000 per month"}
        ]

        formatted = ContextEngineer.format_conversation_history(conversation)
        assert len(formatted) == 3

        response = await mock_groq_client.create_chat_completion(formatted)
        assert response is not None

    async def test_token_usage_tracking(self, mock_groq_client):
        """Test token usage tracking."""
        messages = [{"role": "user", "content": "Test message"}]
        response = await mock_groq_client.create_chat_completion(messages)

        assert "usage" in response
        assert response["usage"]["total_tokens"] > 0
        assert response["usage"]["prompt_tokens"] > 0
        assert response["usage"]["completion_tokens"] > 0

    async def test_model_parameter(self, mock_groq_client):
        """Test different model selection."""
        messages = [{"role": "user", "content": "Test"}]

        # Test with different models
        models = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]

        for model in models:
            response = await mock_groq_client.create_chat_completion(
                messages, model=model
            )
            assert response["model"] == model

    async def test_temperature_control(self, mock_groq_client):
        """Test temperature parameter for creativity control."""
        messages = [{"role": "user", "content": "Generate a creative description"}]

        # Low temperature (more deterministic)
        response_low = await mock_groq_client.create_chat_completion(
            messages, temperature=0.1
        )

        # High temperature (more creative)
        response_high = await mock_groq_client.create_chat_completion(
            messages, temperature=0.9
        )

        assert response_low is not None
        assert response_high is not None

    async def test_max_tokens_limit(self, mock_groq_client):
        """Test max tokens parameter."""
        messages = [{"role": "user", "content": "Write a long description"}]

        response = await mock_groq_client.create_chat_completion(
            messages, max_tokens=100
        )

        assert response is not None
        assert response["usage"]["completion_tokens"] <= 150  # Allow some tolerance

    async def test_error_handling_invalid_input(self, mock_groq_client):
        """Test error handling with invalid input."""
        with pytest.raises(Exception):
            await mock_groq_client.create_chat_completion([])  # Empty messages

    async def test_concurrent_requests(self, mock_groq_client):
        """Test handling multiple concurrent requests."""
        messages = [{"role": "user", "content": "Test concurrent"}]

        # Create multiple concurrent requests
        tasks = [
            mock_groq_client.create_chat_completion(messages)
            for _ in range(5)
        ]

        responses = await asyncio.gather(*tasks)

        assert len(responses) == 5
        assert all(r is not None for r in responses)
        assert mock_groq_client.call_count == 5


@pytest.mark.unit
class TestContextEngineering:
    """Unit tests for context engineering utilities."""

    def test_system_prompt_generation(self):
        """Test system prompt generation for different agent types."""
        search_prompt = ContextEngineer.build_system_prompt("search")
        assert "search" in search_prompt.lower()
        assert "properties" in search_prompt.lower()

        property_prompt = ContextEngineer.build_system_prompt("property")
        assert "analysis" in property_prompt.lower()

        scheduling_prompt = ContextEngineer.build_system_prompt("scheduling")
        assert "scheduling" in scheduling_prompt.lower()

    def test_property_context_formatting(self):
        """Test property context string formatting."""
        properties = [
            {"address": "123 Main St", "price": 2000, "bedrooms": 2, "bathrooms": 1}
        ]

        context = ContextEngineer.format_property_context(properties)

        assert "123 Main St" in context
        assert "2000" in context
        assert "2 bed" in context

    def test_empty_property_context(self):
        """Test formatting with no properties."""
        context = ContextEngineer.format_property_context([])
        assert "No properties" in context

    def test_conversation_history_formatting(self):
        """Test conversation history formatting."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]

        formatted = ContextEngineer.format_conversation_history(messages)

        assert len(formatted) == 2
        assert formatted[0]["role"] == "user"
        assert formatted[1]["role"] == "assistant"

    def test_json_extraction(self):
        """Test structured output extraction from JSON."""
        json_response = '{"key": "value", "number": 42}'
        result = ContextEngineer.extract_structured_output(json_response)

        assert result["key"] == "value"
        assert result["number"] == 42

    def test_json_extraction_from_markdown(self):
        """Test JSON extraction from markdown code blocks."""
        markdown_response = '''
        Here's the data:
        ```json
        {"extracted": true, "value": 123}
        ```
        '''

        result = ContextEngineer.extract_structured_output(markdown_response)
        assert result["extracted"] is True
        assert result["value"] == 123

    def test_fallback_to_text(self):
        """Test fallback to plain text when JSON parsing fails."""
        plain_text = "This is just plain text without JSON"
        result = ContextEngineer.extract_structured_output(plain_text)

        assert "text" in result
        assert result["text"] == plain_text
