# Observability Stack Design - Langfuse, Logfire, Grafana

## Overview

Comprehensive observability architecture for monitoring LLM performance, system health, and user interactions in the real estate reviews system.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                     Application Layer                            │
│  (Agents, LLM Calls, API Requests, Database Queries)            │
└────────────┬─────────────────────────────────────────────────────┘
             │
    ┌────────┼────────┬────────────┬────────────┐
    │        │        │            │            │
    ▼        ▼        ▼            ▼            ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│Langfuse│ │Logfire │ │Prometheus│ │Structlog │ │ Custom   │
│(LLM)   │ │(Trace) │ │(Metrics) │ │(Logs)    │ │Metrics   │
└───┬────┘ └───┬────┘ └─────┬────┘ └─────┬────┘ └─────┬────┘
    │          │            │            │            │
    └──────────┴────────────┴────────────┴────────────┘
                           │
                           ▼
    ┌──────────────────────────────────────────────────┐
    │            Grafana Dashboard                      │
    │  - System Metrics                                 │
    │  - LLM Performance                                │
    │  - Agent Analytics                                │
    │  - Cost Tracking                                  │
    │  - Error Monitoring                               │
    └──────────────────────────────────────────────────┘
```

## 1. Langfuse Integration (LLM Observability)

### Setup and Configuration

```python
# app/observability/langfuse_config.py
from typing import Dict, Any, Optional
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context
from functools import wraps
import time

class LangfuseConfig:
    """Langfuse configuration for LLM observability."""

    def __init__(
        self,
        public_key: str,
        secret_key: str,
        host: str = "https://cloud.langfuse.com"
    ):
        self.client = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host
        )

    def track_llm_call(
        self,
        name: str,
        model: str,
        provider: str,
        input_data: Any,
        output_data: Any,
        metadata: Dict[str, Any] = None
    ):
        """Track individual LLM call."""
        self.client.generation(
            name=name,
            model=model,
            model_parameters={
                "provider": provider,
                "temperature": metadata.get("temperature"),
                "max_tokens": metadata.get("max_tokens"),
            },
            input=input_data,
            output=output_data,
            metadata=metadata or {},
            usage={
                "input_tokens": metadata.get("input_tokens", 0),
                "output_tokens": metadata.get("output_tokens", 0),
                "total_tokens": metadata.get("total_tokens", 0),
            },
            level="DEFAULT"
        )

    def start_trace(self, name: str, user_id: Optional[str] = None) -> str:
        """Start a new trace for a user session."""
        trace = self.client.trace(
            name=name,
            user_id=user_id,
            metadata={"timestamp": time.time()}
        )
        return trace.id

    def end_trace(self, trace_id: str, output: Any = None):
        """End a trace."""
        self.client.trace(
            id=trace_id,
            output=output
        )

    def track_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float
    ):
        """Track LLM costs."""
        self.client.score(
            name="llm_cost",
            value=cost_usd,
            data_type="NUMERIC",
            comment=f"Model: {model}, Tokens: {input_tokens + output_tokens}"
        )


# Decorator for automatic LLM tracking
def track_llm(name: str, provider: str):
    """Decorator to automatically track LLM calls."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            # Execute function
            try:
                result = await func(*args, **kwargs)

                # Extract token usage from result
                usage = result.get("usage", {})

                # Track in Langfuse
                langfuse_client.track_llm_call(
                    name=name,
                    model=kwargs.get("model", "unknown"),
                    provider=provider,
                    input_data=kwargs.get("messages", []),
                    output_data=result.get("choices", [{}])[0].get("message", {}),
                    metadata={
                        "duration_ms": (time.time() - start_time) * 1000,
                        "input_tokens": usage.get("prompt_tokens", 0),
                        "output_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                        "temperature": kwargs.get("temperature"),
                        "max_tokens": kwargs.get("max_tokens"),
                    }
                )

                return result

            except Exception as e:
                # Track error
                langfuse_client.client.span(
                    name=f"{name}_error",
                    metadata={"error": str(e)}
                )
                raise

        return wrapper
    return decorator
```

### Agent Instrumentation

```python
# app/agents/instrumented_base.py
from app.observability.langfuse_config import track_llm
from app.agents.base import BaseAgent

class InstrumentedAgent(BaseAgent):
    """Base agent with Langfuse instrumentation."""

    @track_llm(name="agent_execution", provider="groq")
    async def execute(self, user_message: str, context: Dict[str, Any] = None):
        """Execute agent with automatic tracking."""
        return await super().execute(user_message, context)
```

## 2. Logfire Integration (Distributed Tracing)

### Configuration

```python
# app/observability/logfire_config.py
import logfire
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

class LogfireConfig:
    """Logfire configuration for distributed tracing."""

    def __init__(self, token: str, service_name: str = "real-estate-system"):
        logfire.configure(
            token=token,
            service_name=service_name,
            send_to_logfire="if-token-present",
        )

        # Instrument PydanticAI automatically
        logfire.instrument_pydantic()

    @staticmethod
    @asynccontextmanager
    async def span(
        name: str,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """Create a traced span."""
        with logfire.span(name, **attributes or {}) as span:
            try:
                yield span
            except Exception as e:
                span.set_attribute("error", str(e))
                span.set_attribute("error.type", type(e).__name__)
                raise

    @staticmethod
    def log_event(
        level: str,
        message: str,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """Log an event."""
        log_func = getattr(logfire, level.lower(), logfire.info)
        log_func(message, **attributes or {})

    @staticmethod
    def log_llm_call(
        provider: str,
        model: str,
        prompt: str,
        response: str,
        duration_ms: float,
        tokens: Dict[str, int]
    ):
        """Log LLM call with structured data."""
        logfire.info(
            "LLM call completed",
            provider=provider,
            model=model,
            prompt_preview=prompt[:100],
            response_preview=response[:100],
            duration_ms=duration_ms,
            **tokens
        )
```

### Request Tracing

```python
# app/api/middleware/tracing.py
from fastapi import Request
from app.observability.logfire_config import LogfireConfig
import time

async def trace_request(request: Request, call_next):
    """Trace API requests with Logfire."""

    async with LogfireConfig.span(
        f"{request.method} {request.url.path}",
        attributes={
            "http.method": request.method,
            "http.url": str(request.url),
            "http.client_ip": request.client.host,
        }
    ) as span:
        start_time = time.time()

        response = await call_next(request)

        duration_ms = (time.time() - start_time) * 1000

        span.set_attribute("http.status_code", response.status_code)
        span.set_attribute("duration_ms", duration_ms)

        return response
```

## 3. Prometheus Metrics

### Metrics Collection

```python
# app/observability/metrics.py
from prometheus_client import Counter, Histogram, Gauge, Summary
import time
from functools import wraps

# Define metrics
llm_requests_total = Counter(
    'llm_requests_total',
    'Total LLM requests',
    ['provider', 'model', 'status']
)

llm_tokens_total = Counter(
    'llm_tokens_total',
    'Total tokens used',
    ['provider', 'model', 'type']
)

llm_duration_seconds = Histogram(
    'llm_duration_seconds',
    'LLM request duration',
    ['provider', 'model'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

llm_cost_usd = Counter(
    'llm_cost_usd',
    'Total LLM costs in USD',
    ['provider', 'model']
)

agent_executions_total = Counter(
    'agent_executions_total',
    'Total agent executions',
    ['agent_type', 'status']
)

agent_duration_seconds = Histogram(
    'agent_duration_seconds',
    'Agent execution duration',
    ['agent_type'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

property_searches_total = Counter(
    'property_searches_total',
    'Total property searches',
    ['city', 'property_type']
)

review_analyses_total = Counter(
    'review_analyses_total',
    'Total review analyses',
    ['sentiment']
)

active_sessions = Gauge(
    'active_sessions',
    'Number of active user sessions'
)

database_query_duration = Histogram(
    'database_query_duration_seconds',
    'Database query duration',
    ['query_type'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
)

cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)


# Decorator for automatic metrics
def track_metrics(metric_type: str):
    """Decorator to automatically track metrics."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)

                # Track success
                duration = time.time() - start_time

                if metric_type == "llm":
                    provider = kwargs.get("provider", "unknown")
                    model = kwargs.get("model", "unknown")

                    llm_requests_total.labels(
                        provider=provider,
                        model=model,
                        status="success"
                    ).inc()

                    llm_duration_seconds.labels(
                        provider=provider,
                        model=model
                    ).observe(duration)

                    # Track tokens
                    usage = result.get("usage", {})
                    if usage:
                        llm_tokens_total.labels(
                            provider=provider,
                            model=model,
                            type="input"
                        ).inc(usage.get("prompt_tokens", 0))

                        llm_tokens_total.labels(
                            provider=provider,
                            model=model,
                            type="output"
                        ).inc(usage.get("completion_tokens", 0))

                elif metric_type == "agent":
                    agent_type = kwargs.get("agent_type", "unknown")

                    agent_executions_total.labels(
                        agent_type=agent_type,
                        status="success"
                    ).inc()

                    agent_duration_seconds.labels(
                        agent_type=agent_type
                    ).observe(duration)

                return result

            except Exception as e:
                # Track failure
                if metric_type == "llm":
                    llm_requests_total.labels(
                        provider=kwargs.get("provider", "unknown"),
                        model=kwargs.get("model", "unknown"),
                        status="error"
                    ).inc()
                elif metric_type == "agent":
                    agent_executions_total.labels(
                        agent_type=kwargs.get("agent_type", "unknown"),
                        status="error"
                    ).inc()

                raise

        return wrapper
    return decorator
```

### Metrics Endpoint

```python
# app/api/routes/metrics.py
from fastapi import APIRouter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

router = APIRouter()

@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

## 4. Structured Logging

### Logger Configuration

```python
# app/observability/logger.py
import structlog
from typing import Any, Dict
import sys

def configure_logging(environment: str = "development"):
    """Configure structured logging with structlog."""

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if environment == "production":
        # JSON output for production
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Pretty console output for development
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()


# Usage
logger = configure_logging()

# Structured logging examples
logger.info(
    "llm_call_completed",
    provider="groq",
    model="llama3-8b",
    duration_ms=234,
    tokens={"input": 150, "output": 89},
    cost_usd=0.0012
)

logger.error(
    "database_query_failed",
    query_type="property_search",
    error=str(exception),
    user_id=user_id
)
```

## 5. Grafana Dashboards

### Dashboard Configuration

```yaml
# config/grafana/dashboards/system-overview.yaml
dashboard:
  title: "Real Estate System - Overview"
  panels:
    - title: "LLM Request Rate"
      type: graph
      targets:
        - expr: rate(llm_requests_total[5m])
          legendFormat: "{{provider}} - {{model}}"

    - title: "LLM Response Time (p95)"
      type: graph
      targets:
        - expr: histogram_quantile(0.95, llm_duration_seconds_bucket)
          legendFormat: "{{provider}} - {{model}}"

    - title: "Daily LLM Costs"
      type: singlestat
      targets:
        - expr: sum(increase(llm_cost_usd[24h]))

    - title: "Token Usage by Provider"
      type: piechart
      targets:
        - expr: sum by (provider) (llm_tokens_total)

    - title: "Agent Success Rate"
      type: gauge
      targets:
        - expr: |
            sum(rate(agent_executions_total{status="success"}[5m])) /
            sum(rate(agent_executions_total[5m]))

    - title: "Active Sessions"
      type: graph
      targets:
        - expr: active_sessions

    - title: "Cache Hit Rate"
      type: graph
      targets:
        - expr: |
            rate(cache_hits_total[5m]) /
            (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))
          legendFormat: "{{cache_type}}"

    - title: "Database Query Performance"
      type: heatmap
      targets:
        - expr: rate(database_query_duration_seconds_bucket[5m])
```

### Alert Rules

```yaml
# config/grafana/alerts/system-alerts.yaml
groups:
  - name: llm_alerts
    interval: 1m
    rules:
      - alert: HighLLMErrorRate
        expr: |
          sum(rate(llm_requests_total{status="error"}[5m])) /
          sum(rate(llm_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High LLM error rate (>5%)"

      - alert: HighLLMLatency
        expr: |
          histogram_quantile(0.95, llm_duration_seconds_bucket) > 5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "LLM p95 latency >5s"

      - alert: DailyLLMCostExceeded
        expr: sum(increase(llm_cost_usd[24h])) > 50
        labels:
          severity: critical
        annotations:
          summary: "Daily LLM costs exceeded $50"

  - name: agent_alerts
    interval: 1m
    rules:
      - alert: AgentFailureRate
        expr: |
          sum(rate(agent_executions_total{status="error"}[5m])) /
          sum(rate(agent_executions_total[5m])) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Agent failure rate >10%"

  - name: system_alerts
    interval: 1m
    rules:
      - alert: LowCacheHitRate
        expr: |
          rate(cache_hits_total[5m]) /
          (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m])) < 0.6
        for: 10m
        labels:
          severity: info
        annotations:
          summary: "Cache hit rate <60%"
```

## 6. Custom Analytics Dashboard

### Real-Time Analytics

```python
# app/observability/analytics.py
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict

class AnalyticsDashboard:
    """Custom analytics for business metrics."""

    def __init__(self):
        self.metrics = defaultdict(list)

    def track_user_action(
        self,
        user_id: str,
        action: str,
        metadata: Dict[str, Any] = None
    ):
        """Track user action for analytics."""
        self.metrics["user_actions"].append({
            "user_id": user_id,
            "action": action,
            "metadata": metadata or {},
            "timestamp": datetime.now()
        })

    def get_popular_neighborhoods(
        self,
        time_window: timedelta = timedelta(days=7)
    ) -> List[Dict[str, Any]]:
        """Get most searched neighborhoods."""
        cutoff = datetime.now() - time_window

        searches = [
            m for m in self.metrics["user_actions"]
            if m["action"] == "property_search"
            and m["timestamp"] > cutoff
        ]

        neighborhood_counts = defaultdict(int)
        for search in searches:
            neighborhood = search["metadata"].get("neighborhood")
            if neighborhood:
                neighborhood_counts[neighborhood] += 1

        return sorted(
            [
                {"neighborhood": k, "search_count": v}
                for k, v in neighborhood_counts.items()
            ],
            key=lambda x: x["search_count"],
            reverse=True
        )

    def get_user_journey(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's journey through the system."""
        return [
            m for m in self.metrics["user_actions"]
            if m["user_id"] == user_id
        ]

    def get_llm_cost_breakdown(
        self,
        time_window: timedelta = timedelta(days=1)
    ) -> Dict[str, float]:
        """Get LLM cost breakdown by provider/model."""
        # This would query from Langfuse or Prometheus
        pass
```

## 7. Observability Integration

### Complete Setup

```python
# app/observability/__init__.py
from app.observability.langfuse_config import LangfuseConfig
from app.observability.logfire_config import LogfireConfig
from app.observability.logger import configure_logging
from app.observability.metrics import *

class ObservabilityStack:
    """Unified observability stack."""

    def __init__(self, settings):
        # Langfuse for LLM tracking
        self.langfuse = LangfuseConfig(
            public_key=settings.observability.langfuse_public_key,
            secret_key=settings.observability.langfuse_secret_key
        )

        # Logfire for distributed tracing
        self.logfire = LogfireConfig(
            token=settings.observability.logfire_token
        )

        # Structured logging
        self.logger = configure_logging(
            environment=settings.environment
        )

        # Analytics
        self.analytics = AnalyticsDashboard()

    async def track_request(
        self,
        request_type: str,
        user_id: str = None,
        metadata: Dict[str, Any] = None
    ):
        """Track a user request across all systems."""

        # Log structured event
        self.logger.info(
            f"{request_type}_request",
            user_id=user_id,
            **metadata or {}
        )

        # Track in analytics
        if user_id:
            self.analytics.track_user_action(
                user_id=user_id,
                action=request_type,
                metadata=metadata
            )

    async def shutdown(self):
        """Graceful shutdown of observability stack."""
        self.langfuse.client.flush()
```

---

**Document Version**: 1.0.0
**Author**: Architecture Agent (Hive Mind)
**Date**: 2025-11-11
**Status**: READY FOR IMPLEMENTATION
