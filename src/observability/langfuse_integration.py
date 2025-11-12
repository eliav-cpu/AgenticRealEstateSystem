"""
Langfuse Integration for LLM Observability
Tracks prompts, completions, traces, and performance metrics
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

try:
    from langfuse import Langfuse
    from langfuse.decorators import observe, langfuse_context
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    # Mock decorators if not available
    def observe(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    langfuse_context = None


class LangfuseObserver:
    """Langfuse observability integration"""

    def __init__(
        self,
        public_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        host: Optional[str] = None,
        enabled: bool = True
    ):
        """Initialize Langfuse client"""
        self.enabled = enabled and LANGFUSE_AVAILABLE

        if self.enabled:
            self.client = Langfuse(
                public_key=public_key or os.getenv("LANGFUSE_PUBLIC_KEY", ""),
                secret_key=secret_key or os.getenv("LANGFUSE_SECRET_KEY", ""),
                host=host or os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
            )
        else:
            self.client = None

    def trace_llm_call(
        self,
        name: str,
        input_data: Any,
        output_data: Any,
        model: str,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        """Trace an LLM call"""
        if not self.enabled:
            return None

        trace = self.client.trace(
            name=name,
            input=input_data,
            output=output_data,
            metadata=metadata or {},
            tags=tags or [],
            user_id=user_id,
            session_id=session_id
        )

        return trace

    def trace_generation(
        self,
        name: str,
        model: str,
        prompt: str,
        completion: str,
        tokens_input: int,
        tokens_output: int,
        cost: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Trace a generation event"""
        if not self.enabled:
            return None

        generation = self.client.generation(
            name=name,
            model=model,
            input=prompt,
            output=completion,
            metadata={
                **(metadata or {}),
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "tokens_total": tokens_input + tokens_output,
                "cost": cost
            }
        )

        return generation

    def trace_span(
        self,
        name: str,
        input_data: Any,
        output_data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Trace a span within a larger operation"""
        if not self.enabled:
            return None

        span = self.client.span(
            name=name,
            input=input_data,
            output=output_data,
            metadata=metadata or {}
        )

        return span

    def score_generation(
        self,
        trace_id: str,
        name: str,
        value: float,
        comment: Optional[str] = None
    ):
        """Score a generation for quality assessment"""
        if not self.enabled:
            return None

        score = self.client.score(
            trace_id=trace_id,
            name=name,
            value=value,
            comment=comment
        )

        return score

    def flush(self):
        """Flush all pending traces"""
        if self.enabled:
            self.client.flush()


class ObservabilityWrapper:
    """Wrapper for adding observability to LLM operations"""

    def __init__(self, observer: LangfuseObserver):
        """Initialize wrapper"""
        self.observer = observer

    def wrap_chat_completion(
        self,
        llm_client,
        messages: List[Dict[str, str]],
        **kwargs
    ):
        """Wrap a chat completion with observability"""
        import time

        start_time = time.time()

        # Execute LLM call
        response = llm_client.chat(messages, **kwargs)

        end_time = time.time()
        duration = end_time - start_time

        # Trace the call
        self.observer.trace_generation(
            name="chat_completion",
            model=response.model,
            prompt=json.dumps([{"role": m["role"], "content": m["content"]} for m in messages]),
            completion=response.content,
            tokens_input=response.tokens_used - len(response.content) // 4,
            tokens_output=len(response.content) // 4,
            metadata={
                "duration_seconds": duration,
                "temperature": kwargs.get("temperature"),
                "max_tokens": kwargs.get("max_tokens")
            }
        )

        return response

    def wrap_property_search(
        self,
        search_func,
        query: str,
        filters: Dict[str, Any],
        **kwargs
    ):
        """Wrap property search with observability"""
        import time

        start_time = time.time()

        # Execute search
        results = search_func(query, filters, **kwargs)

        end_time = time.time()
        duration = end_time - start_time

        # Trace the search
        self.observer.trace_span(
            name="property_search",
            input_data={
                "query": query,
                "filters": filters
            },
            output_data={
                "result_count": len(results),
                "top_results": results[:3] if results else []
            },
            metadata={
                "duration_seconds": duration,
                "search_method": kwargs.get("method", "semantic")
            }
        )

        return results


def create_observer(enabled: bool = True) -> LangfuseObserver:
    """Factory function to create Langfuse observer"""
    if not enabled:
        return LangfuseObserver(enabled=False)

    if not LANGFUSE_AVAILABLE:
        print("Warning: Langfuse not installed. Install with: pip install langfuse")
        return LangfuseObserver(enabled=False)

    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")

    if not public_key or not secret_key:
        print("Warning: LANGFUSE_PUBLIC_KEY or LANGFUSE_SECRET_KEY not set")
        return LangfuseObserver(enabled=False)

    return LangfuseObserver(
        public_key=public_key,
        secret_key=secret_key,
        enabled=True
    )


# Decorators for easy integration
if LANGFUSE_AVAILABLE:
    @observe()
    def observed_llm_call(client, messages, **kwargs):
        """Automatically observed LLM call"""
        return client.chat(messages, **kwargs)

    @observe()
    def observed_search(search_func, query, filters):
        """Automatically observed search"""
        return search_func(query, filters)
else:
    # Fallback decorators
    def observed_llm_call(client, messages, **kwargs):
        return client.chat(messages, **kwargs)

    def observed_search(search_func, query, filters):
        return search_func(query, filters)


# Example usage
if __name__ == "__main__":
    observer = create_observer(enabled=True)

    # Example trace
    if observer.enabled:
        trace = observer.trace_generation(
            name="test_generation",
            model="moonshotai/kimi-k2-instruct-0905",
            prompt="What are the best neighborhoods in Austin?",
            completion="Austin has several excellent neighborhoods including...",
            tokens_input=20,
            tokens_output=100,
            cost=0.001,
            metadata={"test": True}
        )

        print("Trace created:", trace)
        observer.flush()
    else:
        print("Langfuse observer not enabled")
