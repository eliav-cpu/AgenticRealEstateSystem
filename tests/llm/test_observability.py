"""
Integration Tests for Observability: Langfuse and Logfire

Tests comprehensive observability and tracing functionality:
- Langfuse trace creation and management
- Logfire logging and structured data
- Performance metrics tracking
- Error tracking and reporting
- Span creation and nesting
- Cost tracking and token usage

Coverage Target: >85%
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock, call
from datetime import datetime
from typing import Dict, Any, List
import json


class MockLangfuseClient:
    """Mock Langfuse client for testing observability."""

    def __init__(self):
        self.traces = []
        self.spans = []
        self.generations = []
        self.scores = []
        self.current_trace = None

    def trace(self, name: str, **kwargs) -> 'MockTrace':
        """Create a new trace."""
        trace = MockTrace(name, self, **kwargs)
        self.traces.append(trace)
        self.current_trace = trace
        return trace

    def span(self, name: str, **kwargs) -> 'MockSpan':
        """Create a new span."""
        span = MockSpan(name, self, **kwargs)
        self.spans.append(span)
        return span

    def generation(self, name: str, **kwargs) -> 'MockGeneration':
        """Create a new generation (LLM call)."""
        generation = MockGeneration(name, self, **kwargs)
        self.generations.append(generation)
        return generation

    def score(self, trace_id: str, name: str, value: float, **kwargs):
        """Add a score to a trace."""
        self.scores.append({
            "trace_id": trace_id,
            "name": name,
            "value": value,
            **kwargs
        })

    def flush(self):
        """Flush pending telemetry data."""
        pass


class MockTrace:
    """Mock Langfuse trace."""

    def __init__(self, name: str, client: MockLangfuseClient, **kwargs):
        self.name = name
        self.client = client
        self.id = f"trace-{len(client.traces)}"
        self.metadata = kwargs.get("metadata", {})
        self.input_data = kwargs.get("input", {})
        self.output_data = None
        self.start_time = datetime.now()
        self.end_time = None

    def update(self, **kwargs):
        """Update trace attributes."""
        if "output" in kwargs:
            self.output_data = kwargs["output"]
        if "metadata" in kwargs:
            self.metadata.update(kwargs["metadata"])

    def end(self, **kwargs):
        """End the trace."""
        self.end_time = datetime.now()
        self.update(**kwargs)


class MockSpan:
    """Mock Langfuse span."""

    def __init__(self, name: str, client: MockLangfuseClient, **kwargs):
        self.name = name
        self.client = client
        self.id = f"span-{len(client.spans)}"
        self.metadata = kwargs.get("metadata", {})
        self.start_time = datetime.now()
        self.end_time = None

    def end(self, **kwargs):
        """End the span."""
        self.end_time = datetime.now()


class MockGeneration:
    """Mock Langfuse generation."""

    def __init__(self, name: str, client: MockLangfuseClient, **kwargs):
        self.name = name
        self.client = client
        self.id = f"gen-{len(client.generations)}"
        self.model = kwargs.get("model", "unknown")
        self.input_data = kwargs.get("input", [])
        self.output_data = kwargs.get("output", "")
        self.usage = kwargs.get("usage", {})
        self.metadata = kwargs.get("metadata", {})

    def end(self, **kwargs):
        """End the generation."""
        if "output" in kwargs:
            self.output_data = kwargs["output"]
        if "usage" in kwargs:
            self.usage = kwargs["usage"]


class MockLogfireHandler:
    """Mock Logfire handler for testing."""

    def __init__(self):
        self.logs = []
        self.spans = []
        self.metrics = []

    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logs.append({
            "level": "info",
            "message": message,
            "timestamp": datetime.now(),
            **kwargs
        })

    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logs.append({
            "level": "error",
            "message": message,
            "timestamp": datetime.now(),
            **kwargs
        })

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logs.append({
            "level": "warning",
            "message": message,
            "timestamp": datetime.now(),
            **kwargs
        })

    def span(self, name: str, **kwargs):
        """Create a span context manager."""
        return MockLogfireSpan(name, self, **kwargs)

    def metric(self, name: str, value: float, **kwargs):
        """Record a metric."""
        self.metrics.append({
            "name": name,
            "value": value,
            "timestamp": datetime.now(),
            **kwargs
        })


class MockLogfireSpan:
    """Mock Logfire span context manager."""

    def __init__(self, name: str, handler: MockLogfireHandler, **kwargs):
        self.name = name
        self.handler = handler
        self.metadata = kwargs
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        self.handler.spans.append({
            "name": self.name,
            "start": self.start_time,
            "end": self.end_time,
            "duration_ms": (self.end_time - self.start_time).total_seconds() * 1000,
            "metadata": self.metadata
        })
        return False


class ObservabilityManager:
    """Manager for observability operations."""

    def __init__(self, langfuse_client: MockLangfuseClient, logfire_handler: MockLogfireHandler):
        self.langfuse = langfuse_client
        self.logfire = logfire_handler

    async def trace_llm_call(
        self,
        agent_type: str,
        messages: List[Dict],
        response: Dict,
        model: str = "llama-3.3-70b"
    ):
        """Trace an LLM call with full context."""
        # Create Langfuse trace
        trace = self.langfuse.trace(
            name=f"{agent_type}_llm_call",
            metadata={"agent": agent_type, "model": model}
        )

        # Create generation
        generation = self.langfuse.generation(
            name="llm_generation",
            model=model,
            input=messages,
            output=response.get("choices", [{}])[0].get("message", {}).get("content", ""),
            usage=response.get("usage", {})
        )

        # Log with Logfire
        self.logfire.info(
            f"LLM call completed for {agent_type}",
            agent=agent_type,
            model=model,
            tokens=response.get("usage", {}).get("total_tokens", 0)
        )

        return trace.id


@pytest.mark.integration
class TestLangfuseIntegration:
    """Test Langfuse tracing integration."""

    @pytest.fixture
    def langfuse_client(self):
        """Provide mock Langfuse client."""
        return MockLangfuseClient()

    @pytest.fixture
    def sample_llm_response(self):
        """Sample LLM response."""
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "Test response"
                }
            }],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }

    def test_create_trace(self, langfuse_client):
        """Test creating a basic trace."""
        trace = langfuse_client.trace(
            name="test_trace",
            metadata={"test": True}
        )

        assert trace.name == "test_trace"
        assert trace.metadata["test"] is True
        assert len(langfuse_client.traces) == 1

    def test_trace_with_input_output(self, langfuse_client):
        """Test trace with input and output data."""
        trace = langfuse_client.trace(
            name="user_query",
            input={"query": "Find apartments in Miami"}
        )

        trace.update(output={"results": ["prop1", "prop2"]})
        trace.end()

        assert trace.input_data["query"] == "Find apartments in Miami"
        assert len(trace.output_data["results"]) == 2
        assert trace.end_time is not None

    def test_create_span(self, langfuse_client):
        """Test creating spans for operation timing."""
        span = langfuse_client.span(
            name="database_query",
            metadata={"query_type": "search"}
        )

        span.end()

        assert span.name == "database_query"
        assert span.end_time is not None
        assert len(langfuse_client.spans) == 1

    def test_create_generation(self, langfuse_client, sample_llm_response):
        """Test creating LLM generation tracking."""
        generation = langfuse_client.generation(
            name="search_agent_query",
            model="llama-3.3-70b-versatile",
            input=[{"role": "user", "content": "Search query"}],
            output=sample_llm_response["choices"][0]["message"]["content"],
            usage=sample_llm_response["usage"]
        )

        assert generation.model == "llama-3.3-70b-versatile"
        assert generation.usage["total_tokens"] == 150
        assert len(langfuse_client.generations) == 1

    def test_nested_spans(self, langfuse_client):
        """Test nested span hierarchy."""
        # Parent trace
        trace = langfuse_client.trace(name="user_request")

        # Child spans
        span1 = langfuse_client.span(name="parse_input")
        span1.end()

        span2 = langfuse_client.span(name="process_query")
        span2.end()

        span3 = langfuse_client.span(name="format_response")
        span3.end()

        trace.end()

        assert len(langfuse_client.spans) == 3
        assert trace.end_time is not None

    def test_add_scores(self, langfuse_client):
        """Test adding quality scores to traces."""
        trace = langfuse_client.trace(name="llm_response")
        trace_id = trace.id

        # Add quality scores
        langfuse_client.score(trace_id, "accuracy", 0.95)
        langfuse_client.score(trace_id, "relevance", 0.90)
        langfuse_client.score(trace_id, "coherence", 0.88)

        assert len(langfuse_client.scores) == 3
        assert all(s["trace_id"] == trace_id for s in langfuse_client.scores)

    def test_trace_metadata(self, langfuse_client):
        """Test storing rich metadata in traces."""
        metadata = {
            "user_id": "user123",
            "session_id": "session456",
            "agent_type": "search",
            "timestamp": datetime.now().isoformat()
        }

        trace = langfuse_client.trace(
            name="search_request",
            metadata=metadata
        )

        assert trace.metadata["user_id"] == "user123"
        assert trace.metadata["agent_type"] == "search"

    def test_token_usage_tracking(self, langfuse_client, sample_llm_response):
        """Test detailed token usage tracking."""
        generation = langfuse_client.generation(
            name="llm_call",
            model="llama-3.3-70b-versatile",
            usage=sample_llm_response["usage"]
        )

        assert generation.usage["prompt_tokens"] == 100
        assert generation.usage["completion_tokens"] == 50
        assert generation.usage["total_tokens"] == 150


@pytest.mark.integration
class TestLogfireIntegration:
    """Test Logfire logging integration."""

    @pytest.fixture
    def logfire_handler(self):
        """Provide mock Logfire handler."""
        return MockLogfireHandler()

    def test_basic_logging(self, logfire_handler):
        """Test basic structured logging."""
        logfire_handler.info("User query received", user_id="user123")
        logfire_handler.error("API call failed", error_code=500)

        assert len(logfire_handler.logs) == 2
        assert logfire_handler.logs[0]["level"] == "info"
        assert logfire_handler.logs[1]["level"] == "error"

    def test_span_context(self, logfire_handler):
        """Test span context manager."""
        with logfire_handler.span("database_query", query_type="search"):
            # Simulate work
            pass

        assert len(logfire_handler.spans) == 1
        assert logfire_handler.spans[0]["name"] == "database_query"
        assert logfire_handler.spans[0]["duration_ms"] >= 0

    def test_nested_spans(self, logfire_handler):
        """Test nested span hierarchy."""
        with logfire_handler.span("parent_operation"):
            with logfire_handler.span("child_operation_1"):
                pass
            with logfire_handler.span("child_operation_2"):
                pass

        assert len(logfire_handler.spans) == 3

    def test_metrics_recording(self, logfire_handler):
        """Test recording custom metrics."""
        logfire_handler.metric("response_time_ms", 250.5)
        logfire_handler.metric("token_count", 1500)
        logfire_handler.metric("cache_hit_rate", 0.85)

        assert len(logfire_handler.metrics) == 3
        assert logfire_handler.metrics[0]["value"] == 250.5

    def test_structured_context(self, logfire_handler):
        """Test rich structured context in logs."""
        context = {
            "agent": "search",
            "model": "llama-3.3-70b",
            "tokens": 150,
            "latency_ms": 500
        }

        logfire_handler.info("LLM call completed", **context)

        log = logfire_handler.logs[0]
        assert log["agent"] == "search"
        assert log["tokens"] == 150


@pytest.mark.integration
@pytest.mark.asyncio
class TestObservabilityManager:
    """Test complete observability manager."""

    @pytest.fixture
    def obs_manager(self):
        """Provide observability manager."""
        langfuse = MockLangfuseClient()
        logfire = MockLogfireHandler()
        return ObservabilityManager(langfuse, logfire)

    @pytest.fixture
    def sample_llm_call(self):
        """Sample LLM call data."""
        return {
            "messages": [
                {"role": "system", "content": "You are a search agent"},
                {"role": "user", "content": "Find apartments"}
            ],
            "response": {
                "choices": [{
                    "message": {"role": "assistant", "content": "Found 5 properties"}
                }],
                "usage": {
                    "prompt_tokens": 50,
                    "completion_tokens": 25,
                    "total_tokens": 75
                }
            }
        }

    async def test_trace_llm_call(self, obs_manager, sample_llm_call):
        """Test tracing complete LLM call."""
        trace_id = await obs_manager.trace_llm_call(
            agent_type="search",
            messages=sample_llm_call["messages"],
            response=sample_llm_call["response"],
            model="llama-3.3-70b-versatile"
        )

        assert trace_id is not None
        assert len(obs_manager.langfuse.traces) == 1
        assert len(obs_manager.langfuse.generations) == 1
        assert len(obs_manager.logfire.logs) == 1

    async def test_multiple_traced_calls(self, obs_manager, sample_llm_call):
        """Test tracing multiple LLM calls."""
        agents = ["search", "property", "scheduling"]

        for agent in agents:
            await obs_manager.trace_llm_call(
                agent_type=agent,
                messages=sample_llm_call["messages"],
                response=sample_llm_call["response"]
            )

        assert len(obs_manager.langfuse.traces) == 3
        assert len(obs_manager.logfire.logs) == 3


@pytest.mark.unit
class TestPerformanceMetrics:
    """Test performance metrics tracking."""

    def test_span_duration_calculation(self):
        """Test accurate span duration calculation."""
        handler = MockLogfireHandler()

        with handler.span("timed_operation"):
            import time
            time.sleep(0.01)  # 10ms

        span = handler.spans[0]
        assert span["duration_ms"] >= 10  # At least 10ms
        assert span["duration_ms"] < 100  # Less than 100ms

    def test_token_cost_estimation(self):
        """Test token cost calculation."""
        # Assuming pricing: $0.0001 per 1K tokens
        usage = {
            "prompt_tokens": 1000,
            "completion_tokens": 500,
            "total_tokens": 1500
        }

        cost_per_1k = 0.0001
        estimated_cost = (usage["total_tokens"] / 1000) * cost_per_1k

        assert estimated_cost == 0.00015  # $0.00015
