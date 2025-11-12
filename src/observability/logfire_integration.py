"""
Logfire Integration for Application Observability
Provides structured logging, metrics, and traces
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import logging

try:
    import logfire
    LOGFIRE_AVAILABLE = True
except ImportError:
    LOGFIRE_AVAILABLE = False


class LogfireObserver:
    """Logfire observability integration"""

    def __init__(
        self,
        token: Optional[str] = None,
        service_name: str = "agentic-real-estate",
        enabled: bool = True
    ):
        """Initialize Logfire observer"""
        self.enabled = enabled and LOGFIRE_AVAILABLE
        self.service_name = service_name

        if self.enabled:
            try:
                logfire.configure(
                    token=token or os.getenv("LOGFIRE_TOKEN"),
                    service_name=service_name,
                    send_to_logfire=True
                )
                self.logger = logfire
            except Exception as e:
                print(f"Failed to configure Logfire: {e}")
                self.enabled = False
                self.logger = None
        else:
            self.logger = None

    def log_info(self, message: str, **kwargs):
        """Log info level message"""
        if self.enabled:
            self.logger.info(message, **kwargs)
        else:
            logging.info(f"{message} | {kwargs}")

    def log_warning(self, message: str, **kwargs):
        """Log warning level message"""
        if self.enabled:
            self.logger.warning(message, **kwargs)
        else:
            logging.warning(f"{message} | {kwargs}")

    def log_error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error level message"""
        if self.enabled:
            if error:
                self.logger.error(message, exc_info=error, **kwargs)
            else:
                self.logger.error(message, **kwargs)
        else:
            logging.error(f"{message} | {kwargs}", exc_info=error)

    def trace_operation(
        self,
        operation: str,
        **attributes
    ):
        """Trace an operation with attributes"""
        if self.enabled:
            return self.logger.span(operation, **attributes)
        else:
            # Return a no-op context manager
            from contextlib import nullcontext
            return nullcontext()

    def log_llm_request(
        self,
        model: str,
        prompt: str,
        response: str,
        tokens: int,
        duration: float,
        **metadata
    ):
        """Log LLM request details"""
        self.log_info(
            "llm_request",
            model=model,
            prompt_length=len(prompt),
            response_length=len(response),
            tokens=tokens,
            duration_seconds=duration,
            **metadata
        )

    def log_property_search(
        self,
        query: str,
        filters: Dict[str, Any],
        result_count: int,
        duration: float
    ):
        """Log property search operation"""
        self.log_info(
            "property_search",
            query=query,
            filters=filters,
            result_count=result_count,
            duration_seconds=duration
        )

    def log_agent_handoff(
        self,
        from_agent: str,
        to_agent: str,
        reason: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Log agent handoff event"""
        self.log_info(
            "agent_handoff",
            from_agent=from_agent,
            to_agent=to_agent,
            reason=reason,
            context=context or {}
        )

    def log_performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "seconds",
        **tags
    ):
        """Log performance metric"""
        self.log_info(
            f"metric.{metric_name}",
            value=value,
            unit=unit,
            **tags
        )

    def log_user_interaction(
        self,
        user_id: str,
        action: str,
        **details
    ):
        """Log user interaction"""
        self.log_info(
            "user_interaction",
            user_id=user_id,
            action=action,
            timestamp=datetime.utcnow().isoformat(),
            **details
        )

    def log_error_with_context(
        self,
        error: Exception,
        context: Dict[str, Any]
    ):
        """Log error with full context"""
        self.log_error(
            "application_error",
            error=error,
            error_type=type(error).__name__,
            error_message=str(error),
            **context
        )

    def create_trace_context(self, trace_name: str):
        """Create a trace context for nested operations"""
        if self.enabled:
            return self.logger.span(trace_name)
        else:
            from contextlib import nullcontext
            return nullcontext()


class MetricsCollector:
    """Collect and aggregate metrics"""

    def __init__(self, observer: LogfireObserver):
        """Initialize metrics collector"""
        self.observer = observer
        self.metrics: Dict[str, List[float]] = {}

    def record(self, metric_name: str, value: float):
        """Record a metric value"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        self.metrics[metric_name].append(value)

        # Log to Logfire
        self.observer.log_performance_metric(metric_name, value)

    def get_statistics(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for a metric"""
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return {}

        values = self.metrics[metric_name]
        return {
            "count": len(values),
            "sum": sum(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values)
        }

    def reset(self):
        """Reset all metrics"""
        self.metrics.clear()


class PerformanceTracer:
    """Context manager for tracing performance"""

    def __init__(self, observer: LogfireObserver, operation: str, **attributes):
        """Initialize performance tracer"""
        self.observer = observer
        self.operation = operation
        self.attributes = attributes
        self.start_time = None

    def __enter__(self):
        """Start tracing"""
        import time
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End tracing and log results"""
        import time
        duration = time.time() - self.start_time

        if exc_type is None:
            self.observer.log_performance_metric(
                f"{self.operation}_duration",
                duration,
                status="success",
                **self.attributes
            )
        else:
            self.observer.log_error(
                f"{self.operation}_failed",
                error=exc_val,
                duration=duration,
                **self.attributes
            )


def create_observer(enabled: bool = True) -> LogfireObserver:
    """Factory function to create Logfire observer"""
    if not enabled:
        return LogfireObserver(enabled=False)

    if not LOGFIRE_AVAILABLE:
        print("Warning: Logfire not installed. Install with: pip install logfire")
        return LogfireObserver(enabled=False)

    token = os.getenv("LOGFIRE_TOKEN")
    if not token:
        print("Warning: LOGFIRE_TOKEN not set")
        return LogfireObserver(enabled=False)

    return LogfireObserver(
        token=token,
        service_name="agentic-real-estate",
        enabled=True
    )


# Example usage
if __name__ == "__main__":
    import time

    observer = create_observer(enabled=True)

    # Log basic messages
    observer.log_info("Application started", version="1.0.0")

    # Trace an operation
    with PerformanceTracer(observer, "property_search", query="family home"):
        time.sleep(0.1)  # Simulate work
        observer.log_info("Search completed", results=10)

    # Log LLM request
    observer.log_llm_request(
        model="moonshotai/kimi-k2-instruct-0905",
        prompt="Find properties in Austin",
        response="Here are 5 properties...",
        tokens=150,
        duration=0.5
    )

    # Collect metrics
    metrics = MetricsCollector(observer)
    metrics.record("search_duration", 0.5)
    metrics.record("search_duration", 0.3)
    metrics.record("search_duration", 0.7)

    print("\nMetrics:", metrics.get_statistics("search_duration"))

    print("\nLogfire integration example complete!")
