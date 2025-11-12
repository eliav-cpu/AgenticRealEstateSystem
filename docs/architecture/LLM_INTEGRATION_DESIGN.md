# LLM Integration Architecture - Groq Provider Design

## Overview

Comprehensive design for integrating Groq as the primary LLM provider with fallback mechanisms, caching, and observability for the real estate reviews system.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Agent Layer                               │
│  (Search, Property, Scheduling, Review Agents)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LLM Manager (Facade)                           │
│  - Provider Selection                                            │
│  - Request Routing                                               │
│  - Error Handling                                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Groq       │  │  OpenRouter  │  │   Ollama     │
│  (Primary)   │  │  (Fallback)  │  │  (Local)     │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Middleware Layer                              │
│  ┌────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Caching   │  │  Retry      │  │  Token Management       │  │
│  │  (Redis)   │  │  Logic      │  │  (Usage Tracking)       │  │
│  └────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Observability Layer                            │
│  - Langfuse (LLM tracking)                                      │
│  - Logfire (Distributed tracing)                                │
│  - Prometheus (Metrics)                                         │
└─────────────────────────────────────────────────────────────────┘
```

## Provider Configuration

### Groq Provider (Primary)

```python
# app/integrations/llm/groq_provider.py
from typing import Optional, Dict, Any
import httpx
from pydantic import BaseModel, Field

class GroqConfig(BaseModel):
    api_key: str = Field(..., description="Groq API key")
    base_url: str = Field(default="https://api.groq.com/openai/v1", description="Groq API endpoint")
    default_model: str = Field(default="llama3-8b-8192", description="Default model")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, gt=0)
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3)

class GroqProvider:
    """Groq LLM provider with high-performance inference."""

    SUPPORTED_MODELS = [
        "llama3-8b-8192",        # Llama 3 8B (8K context)
        "llama3-70b-8192",       # Llama 3 70B (8K context)
        "mixtral-8x7b-32768",    # Mixtral 8x7B (32K context)
        "gemma-7b-it",           # Google Gemma 7B
    ]

    def __init__(self, config: GroqConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
            },
            timeout=config.timeout,
        )

    async def chat_completion(
        self,
        messages: list[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute chat completion with Groq."""

        model = model or self.config.default_model
        temperature = temperature or self.config.temperature
        max_tokens = max_tokens or self.config.max_tokens

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }

        try:
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise GroqAPIError(f"Groq API error: {e.response.status_code} - {e.response.text}")
        except httpx.TimeoutException:
            raise GroqTimeoutError("Groq API request timed out")
        except Exception as e:
            raise GroqProviderError(f"Unexpected Groq error: {str(e)}")

    async def stream_completion(
        self,
        messages: list[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ):
        """Stream chat completion from Groq."""
        payload = {
            "model": model or self.config.default_model,
            "messages": messages,
            "stream": True,
            **kwargs
        }

        async with self.client.stream("POST", "/chat/completions", json=payload) as response:
            async for chunk in response.aiter_lines():
                if chunk.strip():
                    yield self._parse_stream_chunk(chunk)

    def _parse_stream_chunk(self, chunk: str) -> Dict[str, Any]:
        """Parse SSE stream chunk."""
        if chunk.startswith("data: "):
            import json
            data = chunk[6:]  # Remove "data: " prefix
            if data.strip() == "[DONE]":
                return {"done": True}
            return json.loads(data)
        return {}

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
```

### Model Selection Strategy

```python
# app/integrations/llm/model_selector.py
from enum import Enum
from typing import Optional

class TaskComplexity(str, Enum):
    LOW = "low"          # Simple queries, basic info
    MEDIUM = "medium"    # Property analysis, search
    HIGH = "high"        # Complex reasoning, reviews

class ModelSelector:
    """Select optimal model based on task requirements."""

    MODEL_MAPPING = {
        TaskComplexity.LOW: "llama3-8b-8192",        # Fast, cost-effective
        TaskComplexity.MEDIUM: "llama3-8b-8192",     # Balanced
        TaskComplexity.HIGH: "mixtral-8x7b-32768",   # Best quality
    }

    @staticmethod
    def select_model(
        task_complexity: TaskComplexity,
        context_length: int = 0,
        priority_speed: bool = True
    ) -> str:
        """Select optimal model for task."""

        # Long context requires Mixtral
        if context_length > 8000:
            return "mixtral-8x7b-32768"

        # High complexity benefits from Mixtral
        if task_complexity == TaskComplexity.HIGH and not priority_speed:
            return "mixtral-8x7b-32768"

        # Default to Llama 3 8B for speed
        return ModelSelector.MODEL_MAPPING[task_complexity]

    @staticmethod
    def get_agent_model(agent_type: str) -> str:
        """Get recommended model for agent type."""
        agent_models = {
            "search": "llama3-8b-8192",      # Fast search
            "property": "llama3-8b-8192",    # Balanced analysis
            "scheduling": "llama3-8b-8192",  # Simple scheduling
            "review": "mixtral-8x7b-32768",  # Complex sentiment analysis
        }
        return agent_models.get(agent_type, "llama3-8b-8192")
```

## Fallback Chain

### Provider Chain Configuration

```python
# app/integrations/llm/provider_chain.py
from typing import List, Optional, Dict, Any
import asyncio
from enum import Enum

class ProviderStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"

class ProviderChain:
    """Manage fallback chain for LLM providers."""

    def __init__(self, providers: List['BaseLLMProvider']):
        self.providers = providers
        self.status: Dict[str, ProviderStatus] = {
            p.name: ProviderStatus.HEALTHY for p in providers
        }
        self.failure_counts: Dict[str, int] = {p.name: 0 for p in providers}
        self.circuit_breaker_threshold = 5

    async def execute(
        self,
        messages: list[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        """Execute request with automatic fallback."""

        errors = []

        for provider in self.providers:
            # Skip if circuit breaker is open
            if self.status[provider.name] == ProviderStatus.DOWN:
                continue

            try:
                result = await provider.chat_completion(messages, **kwargs)

                # Reset failure count on success
                self.failure_counts[provider.name] = 0
                self.status[provider.name] = ProviderStatus.HEALTHY

                return {
                    "result": result,
                    "provider": provider.name,
                    "fallback_used": provider != self.providers[0]
                }

            except Exception as e:
                errors.append((provider.name, str(e)))
                self._handle_failure(provider.name)

        # All providers failed
        raise AllProvidersFailedError(f"All LLM providers failed: {errors}")

    def _handle_failure(self, provider_name: str):
        """Handle provider failure and update circuit breaker."""
        self.failure_counts[provider_name] += 1

        if self.failure_counts[provider_name] >= self.circuit_breaker_threshold:
            self.status[provider_name] = ProviderStatus.DOWN
            # Schedule recovery check after 60 seconds
            asyncio.create_task(self._schedule_recovery(provider_name))

    async def _schedule_recovery(self, provider_name: str):
        """Schedule provider recovery check."""
        await asyncio.sleep(60)  # Wait 60 seconds
        self.status[provider_name] = ProviderStatus.HEALTHY
        self.failure_counts[provider_name] = 0
```

### Provider Setup

```python
# app/integrations/llm/manager.py
from app.integrations.llm.groq_provider import GroqProvider, GroqConfig
from app.integrations.llm.openrouter_provider import OpenRouterProvider
from app.integrations.llm.ollama_provider import OllamaProvider
from app.integrations.llm.provider_chain import ProviderChain

class LLMManager:
    """Centralized LLM provider management."""

    def __init__(self, settings):
        # Initialize providers in priority order
        self.groq = GroqProvider(GroqConfig(
            api_key=settings.apis.groq_api_key,
            default_model="llama3-8b-8192"
        ))

        self.openrouter = OpenRouterProvider(
            api_key=settings.apis.openrouter_key,
            default_model="mistralai/mistral-7b-instruct:free"
        )

        self.ollama = OllamaProvider(
            base_url="http://localhost:11434",
            default_model="llama3"
        )

        # Create fallback chain
        self.chain = ProviderChain([
            self.groq,        # Primary
            self.openrouter,  # Fallback 1
            self.ollama,      # Fallback 2 (local)
        ])

    async def chat_completion(
        self,
        messages: list[Dict[str, str]],
        agent_type: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute chat completion with automatic fallback."""

        # Select model based on agent type
        if agent_type:
            kwargs["model"] = ModelSelector.get_agent_model(agent_type)

        return await self.chain.execute(messages, **kwargs)
```

## Caching Strategy

### Response Caching

```python
# app/integrations/llm/middleware.py
import hashlib
import json
from typing import Optional, Dict, Any
import redis.asyncio as aioredis

class LLMCacheMiddleware:
    """Cache LLM responses to reduce costs and latency."""

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.default_ttl = 3600 * 24  # 24 hours

    async def get_cached_response(
        self,
        messages: list[Dict[str, str]],
        model: str,
        temperature: float
    ) -> Optional[Dict[str, Any]]:
        """Retrieve cached response if available."""

        cache_key = self._generate_cache_key(messages, model, temperature)
        cached = await self.redis.get(cache_key)

        if cached:
            return json.loads(cached)
        return None

    async def cache_response(
        self,
        messages: list[Dict[str, str]],
        model: str,
        temperature: float,
        response: Dict[str, Any],
        ttl: Optional[int] = None
    ):
        """Cache LLM response."""

        cache_key = self._generate_cache_key(messages, model, temperature)
        ttl = ttl or self.default_ttl

        await self.redis.setex(
            cache_key,
            ttl,
            json.dumps(response)
        )

    def _generate_cache_key(
        self,
        messages: list[Dict[str, str]],
        model: str,
        temperature: float
    ) -> str:
        """Generate cache key from request parameters."""

        # Create deterministic hash of request
        request_data = {
            "messages": messages,
            "model": model,
            "temperature": round(temperature, 2)  # Round to avoid float precision issues
        }

        request_json = json.dumps(request_data, sort_keys=True)
        hash_digest = hashlib.sha256(request_json.encode()).hexdigest()

        return f"llm:cache:{hash_digest}"

# Integration with provider
class CachedGroqProvider(GroqProvider):
    """Groq provider with caching."""

    def __init__(self, config: GroqConfig, cache: LLMCacheMiddleware):
        super().__init__(config)
        self.cache = cache

    async def chat_completion(
        self,
        messages: list[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        use_cache: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute chat completion with caching."""

        model = model or self.config.default_model
        temperature = temperature or self.config.temperature

        # Check cache first
        if use_cache:
            cached_response = await self.cache.get_cached_response(
                messages, model, temperature
            )
            if cached_response:
                return {**cached_response, "from_cache": True}

        # Execute request
        response = await super().chat_completion(
            messages, model=model, temperature=temperature, **kwargs
        )

        # Cache successful response
        if use_cache:
            await self.cache.cache_response(
                messages, model, temperature, response
            )

        return {**response, "from_cache": False}
```

## Token Management

### Usage Tracking

```python
# app/integrations/llm/token_tracker.py
from typing import Dict, Any
from datetime import datetime, timedelta
import asyncio

class TokenUsageTracker:
    """Track token usage and costs across providers."""

    # Cost per 1M tokens (as of 2025)
    COSTS = {
        "groq": {
            "llama3-8b-8192": {"input": 0.05, "output": 0.10},
            "mixtral-8x7b-32768": {"input": 0.24, "output": 0.24},
        },
        "openrouter": {
            "mistralai/mistral-7b-instruct:free": {"input": 0, "output": 0},
        },
    }

    def __init__(self):
        self.usage_stats: Dict[str, Dict[str, int]] = {}
        self.cost_stats: Dict[str, float] = {}

    def track_usage(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ):
        """Track token usage for a request."""

        # Update usage stats
        key = f"{provider}:{model}"
        if key not in self.usage_stats:
            self.usage_stats[key] = {"input": 0, "output": 0, "requests": 0}

        self.usage_stats[key]["input"] += input_tokens
        self.usage_stats[key]["output"] += output_tokens
        self.usage_stats[key]["requests"] += 1

        # Calculate cost
        cost = self._calculate_cost(provider, model, input_tokens, output_tokens)
        self.cost_stats[key] = self.cost_stats.get(key, 0) + cost

    def _calculate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost for token usage."""

        if provider not in self.COSTS or model not in self.COSTS[provider]:
            return 0.0

        rates = self.COSTS[provider][model]
        input_cost = (input_tokens / 1_000_000) * rates["input"]
        output_cost = (output_tokens / 1_000_000) * rates["output"]

        return input_cost + output_cost

    def get_daily_stats(self) -> Dict[str, Any]:
        """Get daily usage statistics."""
        total_cost = sum(self.cost_stats.values())
        total_tokens = sum(
            stats["input"] + stats["output"]
            for stats in self.usage_stats.values()
        )

        return {
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 4),
            "by_model": self.usage_stats,
            "costs_by_model": self.cost_stats,
        }

    async def enforce_rate_limits(
        self,
        provider: str,
        max_tokens_per_minute: int = 100000
    ):
        """Enforce rate limiting on token usage."""
        # Implementation for rate limiting logic
        pass
```

## Error Handling

### Error Types and Recovery

```python
# app/integrations/llm/exceptions.py
class LLMError(Exception):
    """Base exception for LLM errors."""
    pass

class GroqAPIError(LLMError):
    """Groq API returned an error."""
    pass

class GroqTimeoutError(LLMError):
    """Groq API request timed out."""
    pass

class GroqRateLimitError(LLMError):
    """Groq rate limit exceeded."""
    pass

class AllProvidersFailedError(LLMError):
    """All LLM providers in chain failed."""
    pass

# Error recovery strategy
async def execute_with_retry(
    func,
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    initial_delay: float = 1.0
):
    """Execute function with exponential backoff retry."""

    delay = initial_delay

    for attempt in range(max_retries):
        try:
            return await func()
        except GroqTimeoutError:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(delay)
            delay *= backoff_factor
        except GroqRateLimitError:
            # Wait longer for rate limits
            await asyncio.sleep(60)
        except GroqAPIError as e:
            # Don't retry on 4xx errors (client errors)
            if "4" in str(e):
                raise
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(delay)
            delay *= backoff_factor
```

## Performance Optimization

### Request Batching

```python
# app/integrations/llm/batching.py
import asyncio
from typing import List, Dict, Any

class RequestBatcher:
    """Batch multiple LLM requests for efficiency."""

    def __init__(self, max_batch_size: int = 10, max_wait_ms: int = 100):
        self.max_batch_size = max_batch_size
        self.max_wait_ms = max_wait_ms
        self.pending_requests: List[Dict[str, Any]] = []
        self.batch_lock = asyncio.Lock()

    async def add_request(
        self,
        messages: list[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        """Add request to batch and wait for result."""

        async with self.batch_lock:
            request_id = len(self.pending_requests)
            future = asyncio.Future()

            self.pending_requests.append({
                "id": request_id,
                "messages": messages,
                "kwargs": kwargs,
                "future": future
            })

            # Trigger batch processing if full
            if len(self.pending_requests) >= self.max_batch_size:
                asyncio.create_task(self._process_batch())

        # Wait for result
        return await future

    async def _process_batch(self):
        """Process accumulated batch of requests."""
        async with self.batch_lock:
            if not self.pending_requests:
                return

            batch = self.pending_requests[:]
            self.pending_requests = []

        # Process requests in parallel
        tasks = [
            self._execute_single(req)
            for req in batch
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Set results on futures
        for req, result in zip(batch, results):
            if isinstance(result, Exception):
                req["future"].set_exception(result)
            else:
                req["future"].set_result(result)
```

## Integration with Agents

### Agent-Specific Configuration

```python
# app/agents/base.py
from app.integrations.llm.manager import LLMManager
from app.integrations.llm.model_selector import TaskComplexity

class BaseAgent:
    """Base class for all agents with LLM integration."""

    def __init__(
        self,
        llm_manager: LLMManager,
        agent_type: str,
        task_complexity: TaskComplexity = TaskComplexity.MEDIUM
    ):
        self.llm = llm_manager
        self.agent_type = agent_type
        self.task_complexity = task_complexity

    async def execute(self, user_message: str, context: Dict[str, Any] = None):
        """Execute agent with LLM."""

        # Build prompt with context
        messages = self._build_prompt(user_message, context)

        # Execute with automatic provider selection
        response = await self.llm.chat_completion(
            messages=messages,
            agent_type=self.agent_type,
            temperature=self._get_temperature(),
            max_tokens=self._get_max_tokens()
        )

        return self._parse_response(response)

    def _build_prompt(self, user_message: str, context: Dict[str, Any]) -> list:
        """Build prompt messages with system context."""
        raise NotImplementedError

    def _get_temperature(self) -> float:
        """Get temperature setting for this agent."""
        temperatures = {
            TaskComplexity.LOW: 0.1,
            TaskComplexity.MEDIUM: 0.2,
            TaskComplexity.HIGH: 0.3,
        }
        return temperatures[self.task_complexity]

    def _get_max_tokens(self) -> int:
        """Get max tokens for this agent."""
        return 2000
```

---

**Document Version**: 1.0.0
**Author**: Architecture Agent (Hive Mind)
**Date**: 2025-11-11
**Status**: READY FOR IMPLEMENTATION
