"""
Groq LLM Integration Client
Provides interface to Groq API with moonshotai/kimi-k2-instruct-0905 model
"""

import os
from typing import Optional, List, Dict, Any, AsyncIterator
from dataclasses import dataclass
import json

try:
    from groq import Groq, AsyncGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


@dataclass
class LLMConfig:
    """LLM Configuration"""
    api_key: str
    model: str = "moonshotai/kimi-k2-instruct-0905"
    temperature: float = 0.1
    max_tokens: int = 2000
    timeout: float = 30.0


@dataclass
class LLMMessage:
    """Chat message structure"""
    role: str  # system, user, assistant
    content: str


@dataclass
class LLMResponse:
    """LLM response structure"""
    content: str
    model: str
    tokens_used: int
    finish_reason: str
    raw_response: Optional[Dict[str, Any]] = None


class GroqClient:
    """Synchronous Groq API client"""

    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize Groq client"""
        if not GROQ_AVAILABLE:
            raise ImportError(
                "groq package not installed. Install with: pip install groq"
            )

        if config is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY environment variable not set")

            config = LLMConfig(
                api_key=api_key,
                model=os.getenv("LLM_DEFAULT_MODEL", "moonshotai/kimi-k2-instruct-0905"),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
                max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000"))
            )

        self.config = config
        self.client = Groq(api_key=config.api_key)

    def chat(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> LLMResponse:
        """Send chat completion request"""
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=formatted_messages,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
            stream=stream
        )

        if stream:
            return response  # Return stream object

        choice = response.choices[0]

        return LLMResponse(
            content=choice.message.content,
            model=response.model,
            tokens_used=response.usage.total_tokens,
            finish_reason=choice.finish_reason,
            raw_response=response.model_dump()
        )

    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Simple completion with optional system prompt"""
        messages = []

        if system_prompt:
            messages.append(LLMMessage(role="system", content=system_prompt))

        messages.append(LLMMessage(role="user", content=prompt))

        return self.chat(messages, **kwargs)

    def stream_chat(
        self,
        messages: List[LLMMessage],
        **kwargs
    ):
        """Stream chat completion"""
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        stream = self.client.chat.completions.create(
            model=self.config.model,
            messages=formatted_messages,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class AsyncGroqClient:
    """Asynchronous Groq API client"""

    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize async Groq client"""
        if not GROQ_AVAILABLE:
            raise ImportError(
                "groq package not installed. Install with: pip install groq"
            )

        if config is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY environment variable not set")

            config = LLMConfig(
                api_key=api_key,
                model=os.getenv("LLM_DEFAULT_MODEL", "moonshotai/kimi-k2-instruct-0905"),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
                max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000"))
            )

        self.config = config
        self.client = AsyncGroq(api_key=config.api_key)

    async def chat(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> LLMResponse:
        """Send async chat completion request"""
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        response = await self.client.chat.completions.create(
            model=self.config.model,
            messages=formatted_messages,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
            stream=stream
        )

        if stream:
            return response

        choice = response.choices[0]

        return LLMResponse(
            content=choice.message.content,
            model=response.model,
            tokens_used=response.usage.total_tokens,
            finish_reason=choice.finish_reason,
            raw_response=response.model_dump()
        )

    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Simple async completion"""
        messages = []

        if system_prompt:
            messages.append(LLMMessage(role="system", content=system_prompt))

        messages.append(LLMMessage(role="user", content=prompt))

        return await self.chat(messages, **kwargs)

    async def stream_chat(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream async chat completion"""
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        stream = await self.client.chat.completions.create(
            model=self.config.model,
            messages=formatted_messages,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            stream=True
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


def create_client(async_mode: bool = False) -> GroqClient | AsyncGroqClient:
    """Factory function to create appropriate client"""
    config = LLMConfig(
        api_key=os.getenv("GROQ_API_KEY", ""),
        model=os.getenv("LLM_DEFAULT_MODEL", "moonshotai/kimi-k2-instruct-0905"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000"))
    )

    if async_mode:
        return AsyncGroqClient(config)
    return GroqClient(config)


# Example usage
if __name__ == "__main__":
    import asyncio

    # Sync example
    print("=== Synchronous Client ===")
    client = create_client(async_mode=False)

    messages = [
        LLMMessage(role="system", content="You are a helpful real estate assistant."),
        LLMMessage(role="user", content="What are 3 key factors to consider when buying a house?")
    ]

    response = client.chat(messages)
    print(f"Model: {response.model}")
    print(f"Tokens: {response.tokens_used}")
    print(f"Response: {response.content}\n")

    # Async example
    async def async_example():
        print("=== Asynchronous Client ===")
        async_client = create_client(async_mode=True)

        response = await async_client.complete(
            "List 3 benefits of living in a walkable neighborhood.",
            system_prompt="You are a helpful real estate assistant."
        )

        print(f"Model: {response.model}")
        print(f"Tokens: {response.tokens_used}")
        print(f"Response: {response.content}")

    asyncio.run(async_example())
