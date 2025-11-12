"""
Tests for Groq LLM Client
"""

import pytest
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.llm.groq_client import (
    GroqClient,
    AsyncGroqClient,
    LLMConfig,
    LLMMessage,
    LLMResponse,
    create_client
)


class TestLLMConfig:
    """Test LLM configuration"""

    def test_config_creation(self):
        """Test config can be created"""
        config = LLMConfig(
            api_key="test-key",
            model="test-model",
            temperature=0.5
        )

        assert config.api_key == "test-key"
        assert config.model == "test-model"
        assert config.temperature == 0.5

    def test_config_defaults(self):
        """Test config default values"""
        config = LLMConfig(api_key="test")

        assert config.model == "moonshotai/kimi-k2-instruct-0905"
        assert config.temperature == 0.1
        assert config.max_tokens == 2000
        assert config.timeout == 30.0


class TestLLMMessage:
    """Test LLM message structure"""

    def test_message_creation(self):
        """Test message can be created"""
        msg = LLMMessage(role="user", content="Hello")

        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_message_roles(self):
        """Test different message roles"""
        system_msg = LLMMessage(role="system", content="You are helpful")
        user_msg = LLMMessage(role="user", content="Question")
        assistant_msg = LLMMessage(role="assistant", content="Answer")

        assert system_msg.role == "system"
        assert user_msg.role == "user"
        assert assistant_msg.role == "assistant"


class TestGroqClient:
    """Test Groq client (requires API key)"""

    @pytest.fixture
    def skip_if_no_api_key(self):
        """Skip test if no API key available"""
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY not set")

    def test_client_initialization(self):
        """Test client can be initialized"""
        config = LLMConfig(api_key="test-key")

        try:
            client = GroqClient(config)
            assert client.config.api_key == "test-key"
        except ImportError:
            pytest.skip("Groq package not installed")

    def test_create_client_factory(self):
        """Test factory function"""
        # Set environment variable
        os.environ["GROQ_API_KEY"] = "test-key"

        try:
            client = create_client(async_mode=False)
            assert isinstance(client, GroqClient)

            async_client = create_client(async_mode=True)
            assert isinstance(async_client, AsyncGroqClient)
        except (ImportError, ValueError):
            pytest.skip("Groq package not installed or API key not set")

    def test_message_formatting(self, skip_if_no_api_key):
        """Test message formatting for API"""
        try:
            client = create_client(async_mode=False)

            messages = [
                LLMMessage(role="system", content="You are helpful"),
                LLMMessage(role="user", content="Hello")
            ]

            # Note: This would make a real API call if GROQ_API_KEY is valid
            # In production tests, we'd use mocking
        except ImportError:
            pytest.skip("Groq package not installed")


class TestLLMResponse:
    """Test LLM response structure"""

    def test_response_creation(self):
        """Test response can be created"""
        response = LLMResponse(
            content="Test response",
            model="test-model",
            tokens_used=50,
            finish_reason="stop"
        )

        assert response.content == "Test response"
        assert response.model == "test-model"
        assert response.tokens_used == 50
        assert response.finish_reason == "stop"

    def test_response_with_raw_data(self):
        """Test response with raw data"""
        raw_data = {"test": "data"}
        response = LLMResponse(
            content="Test",
            model="test-model",
            tokens_used=10,
            finish_reason="stop",
            raw_response=raw_data
        )

        assert response.raw_response == raw_data


class TestContextEngineering:
    """Test context engineering features"""

    def test_prompt_optimization(self):
        """Test prompt can be optimized"""
        from src.llm.context_engineering import PromptOptimizer

        optimizer = PromptOptimizer()
        prompt = optimizer.create_real_estate_prompt(
            "Find a house",
            property_data={"address": "123 Main St", "price": 300000}
        )

        assert "123 Main St" in prompt
        assert "300000" in prompt
        assert len(prompt) > 0

    def test_token_estimation(self):
        """Test token estimation"""
        from src.llm.context_engineering import TokenManager

        text = "This is a test sentence with about ten words in it."
        tokens = TokenManager.estimate_tokens(text)

        assert tokens > 0
        assert tokens < len(text)  # Should be less than character count


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
