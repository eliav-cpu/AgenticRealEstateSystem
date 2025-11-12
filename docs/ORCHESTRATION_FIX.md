# Orchestration Layer Fix - LangGraph-Swarm + PydanticAI Integration

## Problem Statement

The original implementation had critical issues preventing proper integration between langgraph-swarm and pydantic-ai:

### Critical Issues Fixed

1. **Event Loop Conflicts** ❌
   - Using `asyncio.run()` inside async contexts (lines 194, 241, 289 in swarm_fixed.py)
   - This causes `RuntimeError: asyncio.run() cannot be called from a running event loop`

2. **Incorrect Architecture** ❌
   - LangGraph agents calling PydanticAI agents synchronously
   - No proper separation between coordination (LangGraph) and execution (PydanticAI)

3. **Tool Validation Errors** ❌
   - Improper use of handoff tools from langgraph-swarm
   - Type annotation issues in tool definitions

4. **Blocking Operations** ❌
   - Synchronous wrappers around async PydanticAI calls
   - Performance bottlenecks from unnecessary blocking

## Solution: Unified Swarm Architecture

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  LangGraph-Swarm (OS Layer)                 │
│  - Agent Coordination                                       │
│  - Routing Logic                                            │
│  - State Management                                         │
│  - Handoff Mechanism                                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ Delegates Execution
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              PydanticAI Agents (Application Layer)          │
│  - LLM Execution                                            │
│  - Retry & Fallback                                         │
│  - Validation                                               │
│  - Observability                                            │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. PydanticAgentWrapper
```python
class PydanticAgentWrapper:
    """
    Wraps PydanticAI agents for LangGraph integration.

    ✅ Proper async/await patterns
    ✅ No blocking asyncio.run() calls
    ✅ Full observability with Logfire
    """

    async def execute(self, user_message: str, context: AgentContext) -> str:
        # Direct async call - no asyncio.run()
        result = await self.pydantic_agent.run(enhanced_prompt)
        return result.output
```

**Before (Broken):**
```python
# ❌ WRONG - Causes event loop conflicts
def handle_search_request(query: str) -> str:
    result = asyncio.run(self.pydantic_search.run(enhanced_query))  # 💥
    return str(result.output)
```

**After (Fixed):**
```python
# ✅ CORRECT - Proper async execution
async def execute(self, user_message: str, context: AgentContext) -> str:
    result = await self.pydantic_agent.run(enhanced_prompt)  # ✨
    return str(result.output)
```

#### 2. Agent Node Functions
```python
async def search_agent_node(state: UnifiedSwarmState) -> Dict[str, Any]:
    """
    LangGraph node that delegates to PydanticAI.

    ✅ Async throughout
    ✅ Clean separation of concerns
    ✅ No blocking operations
    """
    # Get wrapper (created in orchestrator)
    from . import _search_wrapper

    # Execute PydanticAI agent (proper async)
    response = await _search_wrapper.execute(user_message, context)

    return {"messages": [AIMessage(content=response)]}
```

#### 3. Smart Routing Function
```python
def route_to_agent(state: UnifiedSwarmState) -> str:
    """
    Intent-based routing using langgraph-swarm patterns.

    ✅ Keyword matching
    ✅ Context-aware decisions
    ✅ No blocking operations
    """
    # Scheduling intent
    if any(keyword in user_content for keyword in scheduling_keywords):
        return "scheduling_agent"

    # Search intent
    if any(keyword in user_content for keyword in search_keywords):
        return "search_agent"

    # Property analysis with context
    if context.get("property_context") and property_keywords_match:
        return "property_agent"

    # Default routing
    return "search_agent" if not context else "property_agent"
```

#### 4. Unified Orchestrator
```python
class UnifiedSwarmOrchestrator:
    """
    Main orchestrator combining both frameworks.

    ✅ LangGraph-Swarm for coordination
    ✅ PydanticAI for execution
    ✅ Memory persistence
    ✅ Proper async patterns
    """

    def __init__(self):
        # Memory components
        self.checkpointer = MemorySaver()
        self.store = InMemoryStore()

        # Create PydanticAI wrappers
        self._initialize_agent_wrappers()

        # Build LangGraph graph
        self.graph = self._build_graph()

    async def process_message(self, message: Dict[str, Any], config: Dict[str, Any] = None):
        # Proper async execution through graph
        result = await self.graph.ainvoke(message, config)
        return result
```

## Key Improvements

### 1. No Event Loop Conflicts ✅

**Problem:**
```python
# ❌ This causes RuntimeError in async context
result = asyncio.run(agent.run(prompt))
```

**Solution:**
```python
# ✅ Direct async call
result = await agent.run(prompt)
```

### 2. Proper Async/Await Patterns ✅

**All async paths:**
- `UnifiedSwarmOrchestrator.process_message()` → async
- `search_agent_node()` → async
- `PydanticAgentWrapper.execute()` → async
- `pydantic_agent.run()` → async

**No blocking calls anywhere in the async chain!**

### 3. Clean Separation of Concerns ✅

**LangGraph-Swarm (Coordination):**
- Routing between agents
- State management
- Handoff coordination
- Memory persistence

**PydanticAI (Execution):**
- LLM inference
- Retry logic
- Response validation
- Observability

### 4. Proper Tool Usage ✅

**Handoff tools (if needed for explicit transfers):**
```python
from langgraph_swarm import create_handoff_tool

handoff_to_property = create_handoff_tool(
    agent_name="property_agent",
    description="Transfer to property analysis agent"
)
```

**Execution tools (call PydanticAI):**
```python
@tool
async def execute_search_logic(query: str) -> str:
    """Execute using PydanticAI agent."""
    return await search_wrapper.execute(query, context)
```

## Usage

### Basic Usage
```python
from app.orchestration.unified_swarm import get_unified_swarm_orchestrator

# Get orchestrator instance
orchestrator = get_unified_swarm_orchestrator()

# Process message
message = {
    "messages": [HumanMessage(content="I'm looking for a 2BR apartment")],
    "session_id": "user-123",
    "context": {"data_mode": "mock"}
}

config = {
    "configurable": {
        "thread_id": "session-abc123"
    }
}

# Async execution - no event loop conflicts
result = await orchestrator.process_message(message, config)
```

### Streaming
```python
# Stream responses
async for chunk in orchestrator.stream_message(message, config):
    print(chunk)
```

## Testing

Run the comprehensive test suite:
```bash
pytest tests/test_unified_swarm.py -v
```

Tests cover:
- ✅ Agent wrapper creation
- ✅ Async execution without blocking
- ✅ Routing logic
- ✅ Memory persistence
- ✅ Error handling
- ✅ No event loop conflicts

## Migration Guide

### From swarm_fixed.py

**Before:**
```python
# Using synchronous tool wrappers
@tool
def handle_search_request(query: str) -> str:
    result = asyncio.run(self.pydantic_search.run(query))  # ❌ Event loop conflict
    return str(result.output)
```

**After:**
```python
# Using proper async wrappers
async def search_agent_node(state: UnifiedSwarmState) -> Dict[str, Any]:
    response = await search_wrapper.execute(user_message, context)  # ✅ No conflict
    return {"messages": [AIMessage(content=response)]}
```

### From swarm.py

**Before:**
```python
# Complex routing with direct OpenRouter calls
async def search_agent_node(state: SwarmState) -> dict:
    # Direct OpenRouter API calls mixed with logic
    agent = await create_pydantic_agent("search_agent")
    response = await agent.run(prompt)
```

**After:**
```python
# Clean separation - LangGraph routes, PydanticAI executes
async def search_agent_node(state: UnifiedSwarmState) -> Dict[str, Any]:
    from . import _search_wrapper
    response = await _search_wrapper.execute(user_message, context)
    return {"messages": [AIMessage(content=response)]}
```

## Performance Benefits

1. **No Blocking** - True async throughout, better concurrency
2. **Event Loop Safety** - No `asyncio.run()` conflicts
3. **Better Resource Usage** - Proper async I/O handling
4. **Cleaner Stack Traces** - Easier debugging

## Coordination Hooks

The implementation integrates with claude-flow hooks:

```bash
# Pre-task coordination
npx claude-flow@alpha hooks pre-task --description "fix_orchestration"

# Post-edit memory storage
npx claude-flow@alpha hooks post-edit \
  --file "app/orchestration/unified_swarm.py" \
  --memory-key "swarm/coder/unified"

# Post-task completion
npx claude-flow@alpha hooks post-task --task-id "fix_orchestration"
```

## File Organization

```
app/orchestration/
├── unified_swarm.py          # ✅ NEW - Unified implementation
├── swarm_fixed.py            # ❌ OLD - Has event loop issues
├── swarm.py                  # ❌ OLD - Complex routing issues
└── swarm_hybrid.py           # ❌ OLD - Partial solution

tests/
└── test_unified_swarm.py     # ✅ NEW - Comprehensive tests

docs/
└── ORCHESTRATION_FIX.md      # ✅ This document
```

## Next Steps

1. **Update API endpoints** to use `get_unified_swarm_orchestrator()`
2. **Run tests** to verify all scenarios work
3. **Monitor performance** in production
4. **Deprecate old implementations** once stable

## References

- LangGraph-Swarm docs: https://github.com/langchain-ai/langgraph
- PydanticAI docs: https://ai.pydantic.dev/
- Claude Flow hooks: https://github.com/ruvnet/claude-flow

---

**Status:** ✅ Implementation Complete
**Date:** 2025-11-11
**Author:** Coder Agent (Hive Mind Swarm)
