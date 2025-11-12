# Integration Guide - Unified Swarm Orchestrator

## Quick Start

### 1. Import the Orchestrator

```python
from app.orchestration.unified_swarm import get_unified_swarm_orchestrator
```

### 2. Basic Usage

```python
# Get singleton instance
orchestrator = get_unified_swarm_orchestrator()

# Process a message
message = {
    "messages": [HumanMessage(content="I'm looking for a 2BR apartment")],
    "session_id": "user-123",
    "context": {
        "data_mode": "mock"
    }
}

config = {
    "configurable": {
        "thread_id": "session-abc123"  # For memory persistence
    }
}

# Execute (fully async - no event loop conflicts!)
result = await orchestrator.process_message(message, config)
```

## API Endpoint Integration

### Update Existing Endpoints

**File:** `/mnt/c/Users/DaviCastroSamora/Documents/SamoraDC/AgenticRealEstateSystem/app/api/dashboard.py`

**Before:**
```python
from app.orchestration.swarm_fixed import get_fixed_swarm_orchestrator

@router.post("/chat")
async def chat(request: ChatRequest):
    orchestrator = get_fixed_swarm_orchestrator()  # ❌ Has event loop issues
    result = await orchestrator.process_message(...)
```

**After:**
```python
from app.orchestration.unified_swarm import get_unified_swarm_orchestrator

@router.post("/chat")
async def chat(request: ChatRequest):
    orchestrator = get_unified_swarm_orchestrator()  # ✅ Fixed!
    result = await orchestrator.process_message(...)
```

### Complete Example

```python
from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage, AIMessage
from app.orchestration.unified_swarm import get_unified_swarm_orchestrator
from app.models.response import ChatRequest, ChatResponse
import uuid

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Process chat message through unified swarm orchestrator.

    ✅ No event loop conflicts
    ✅ Proper async execution
    ✅ Memory persistence
    """
    try:
        # Get orchestrator
        orchestrator = get_unified_swarm_orchestrator()

        # Build message
        message = {
            "messages": [HumanMessage(content=request.message)],
            "session_id": request.session_id or "default",
            "context": {
                "data_mode": request.data_mode or "mock",
                "property_context": request.property_context,
                "user_id": request.user_id
            }
        }

        # Build config for memory
        config = {
            "configurable": {
                "thread_id": request.thread_id or f"thread-{uuid.uuid4().hex[:8]}"
            }
        }

        # Process (fully async - no blocking!)
        result = await orchestrator.process_message(message, config)

        # Extract response
        if "messages" in result and len(result["messages"]) > 0:
            last_message = result["messages"][-1]
            response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)

            return ChatResponse(
                response=response_content,
                session_id=message["session_id"],
                thread_id=config["configurable"]["thread_id"],
                agent_name=result.get("current_agent", "unknown"),
                success=True
            )
        else:
            raise HTTPException(status_code=500, detail="No response from agent")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Stream chat responses through unified swarm orchestrator.

    ✅ Proper async streaming
    ✅ Real-time updates
    """
    from fastapi.responses import StreamingResponse
    import json

    async def generate_stream():
        try:
            orchestrator = get_unified_swarm_orchestrator()

            message = {
                "messages": [HumanMessage(content=request.message)],
                "session_id": request.session_id or "default",
                "context": {
                    "data_mode": request.data_mode or "mock",
                    "property_context": request.property_context
                }
            }

            config = {
                "configurable": {
                    "thread_id": request.thread_id or f"thread-{uuid.uuid4().hex[:8]}"
                }
            }

            # Stream chunks
            async for chunk in orchestrator.stream_message(message, config):
                yield json.dumps(chunk) + "\n"

        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"

    return StreamingResponse(generate_stream(), media_type="application/x-ndjson")
```

## Environment Setup

### Required Environment Variables

```bash
# .env file
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Optional
LOGFIRE_TOKEN=your-logfire-token
LANGSMITH_API_KEY=your-langsmith-key
```

### Settings Validation

```python
from config.settings import get_settings

settings = get_settings()

# Validate API key
if not settings.apis.openrouter_key or settings.apis.openrouter_key == "your_openrouter_api_key_here":
    raise ValueError("Valid OpenRouter API key required!")
```

## Migration Checklist

### 1. Update Imports ✅

```python
# ❌ Old
from app.orchestration.swarm_fixed import get_fixed_swarm_orchestrator

# ✅ New
from app.orchestration.unified_swarm import get_unified_swarm_orchestrator
```

### 2. Update Function Calls ✅

```python
# ❌ Old (may have event loop issues)
orchestrator = get_fixed_swarm_orchestrator()

# ✅ New (no event loop conflicts!)
orchestrator = get_unified_swarm_orchestrator()
```

### 3. Verify Async Patterns ✅

```python
# ✅ Always use await
result = await orchestrator.process_message(message, config)

# ❌ Never use asyncio.run() in async context
result = asyncio.run(orchestrator.process_message(message, config))  # DON'T DO THIS!
```

### 4. Add Memory Config ✅

```python
# ✅ Always provide thread_id for memory persistence
config = {
    "configurable": {
        "thread_id": "unique-session-id"
    }
}

result = await orchestrator.process_message(message, config)
```

## Testing Integration

### Unit Test Example

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_chat_endpoint_with_unified_swarm():
    """Test chat endpoint uses unified swarm correctly."""

    response = client.post(
        "/api/chat",
        json={
            "message": "I'm looking for a 2BR apartment",
            "session_id": "test-session",
            "data_mode": "mock"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 0
```

### Integration Test Example

```python
import pytest
from app.orchestration.unified_swarm import get_unified_swarm_orchestrator
from langchain_core.messages import HumanMessage

@pytest.mark.asyncio
async def test_full_conversation_flow():
    """Test full conversation flow through unified swarm."""

    orchestrator = get_unified_swarm_orchestrator()

    # First message
    message1 = {
        "messages": [HumanMessage(content="Show me 2BR apartments")],
        "session_id": "test",
        "context": {"data_mode": "mock"}
    }

    config = {
        "configurable": {"thread_id": "test-thread"}
    }

    result1 = await orchestrator.process_message(message1, config)
    assert result1 is not None

    # Follow-up message (uses memory)
    message2 = {
        "messages": [HumanMessage(content="What's the price?")],
        "session_id": "test",
        "context": {"data_mode": "mock"}
    }

    result2 = await orchestrator.process_message(message2, config)
    assert result2 is not None
```

## Performance Monitoring

### Add Performance Tracking

```python
from app.utils.logging import log_performance
import time

async def chat_endpoint_with_monitoring(request: ChatRequest):
    start_time = time.time()

    try:
        orchestrator = get_unified_swarm_orchestrator()
        result = await orchestrator.process_message(message, config)

        execution_time = time.time() - start_time
        log_performance("chat_endpoint", execution_time)

        return result

    except Exception as e:
        execution_time = time.time() - start_time
        log_performance("chat_endpoint_error", execution_time)
        raise
```

## Common Issues & Solutions

### Issue 1: Event Loop Conflicts ❌

**Symptom:**
```
RuntimeError: asyncio.run() cannot be called from a running event loop
```

**Solution:**
```python
# ✅ Use unified_swarm.py - no asyncio.run() anywhere
orchestrator = get_unified_swarm_orchestrator()
result = await orchestrator.process_message(message, config)
```

### Issue 2: Missing Memory Persistence ⚠️

**Symptom:** Conversation context not maintained

**Solution:**
```python
# ✅ Always provide thread_id in config
config = {
    "configurable": {
        "thread_id": f"user-{user_id}-session"
    }
}
```

### Issue 3: Invalid API Key ⚠️

**Symptom:**
```
ValueError: Valid OpenRouter API key required
```

**Solution:**
```bash
# Set in .env file
OPENROUTER_API_KEY=sk-or-v1-your-actual-key

# Or set in environment
export OPENROUTER_API_KEY=sk-or-v1-your-actual-key
```

## Deployment Checklist

- [ ] Update all API endpoints to use `get_unified_swarm_orchestrator()`
- [ ] Remove imports of old orchestrators (`swarm_fixed`, `swarm`, `swarm_hybrid`)
- [ ] Verify environment variables are set correctly
- [ ] Run test suite: `pytest tests/test_unified_swarm.py -v`
- [ ] Test in staging environment
- [ ] Monitor for event loop errors in logs
- [ ] Verify memory persistence works across requests
- [ ] Check performance metrics (should improve)
- [ ] Update documentation
- [ ] Deploy to production

## Support

If you encounter issues:

1. Check the logs for event loop errors
2. Verify API keys are valid
3. Ensure proper async/await patterns
4. Review `/docs/ORCHESTRATION_FIX.md` for details
5. Run tests to identify specific issues

## References

- **Main Implementation:** `/app/orchestration/unified_swarm.py`
- **Tests:** `/tests/test_unified_swarm.py`
- **Documentation:** `/docs/ORCHESTRATION_FIX.md`
- **Summary:** `/docs/ORCHESTRATION_SUMMARY.md`

---

**Status:** Ready for Integration
**Last Updated:** 2025-11-11
