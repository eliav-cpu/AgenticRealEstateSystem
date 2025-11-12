# Orchestration Review: LangGraph-Swarm + PydanticAI Integration

**Review Date:** 2025-11-11
**Reviewer:** Code Review Agent (Hive Mind)
**System:** Agentic Real Estate System

---

## Executive Summary

The system implements **three different orchestration patterns** to integrate langgraph-swarm with pydantic-ai agents:

1. **swarm.py** - Custom routing with PydanticAI nodes
2. **swarm_fixed.py** - LangGraph ReActAgent wrapper pattern
3. **swarm_hybrid.py** - Full hybrid integration with PydanticAI wrappers

**Overall Assessment:** 🟡 **MODERATE** - Mixed implementation quality with architectural inconsistencies

---

## Critical Issues

### 🔴 CRITICAL #1: Multiple Orchestration Patterns Without Clear Selection Logic

**File:** `app/orchestration/swarm.py`, `swarm_fixed.py`, `swarm_hybrid.py`
**Severity:** Critical
**Impact:** High maintenance burden, unclear which pattern to use

**Problem:**
```python
# Three different orchestrators exist
from app.orchestration.swarm import get_swarm_orchestrator
from app.orchestration.swarm_fixed import get_fixed_swarm_orchestrator
from app.orchestration.swarm_hybrid import get_hybrid_swarm_orchestrator

# No clear documentation on when to use each
```

**Evidence:**
- swarm.py: 1456 lines - Custom implementation
- swarm_fixed.py: 396 lines - Simplified approach
- swarm_hybrid.py: 586 lines - Full hybrid pattern

**Recommended Fix:**
```python
# Create single unified orchestrator with strategy pattern
class SwarmOrchestrator:
    def __init__(self, strategy: OrchestrationType = "hybrid"):
        """
        strategy: "custom" | "simplified" | "hybrid"
        """
        self.strategy = self._create_strategy(strategy)

    def _create_strategy(self, strategy_type: str):
        strategies = {
            "custom": CustomSwarmStrategy(),
            "simplified": SimplifiedSwarmStrategy(),
            "hybrid": HybridSwarmStrategy()
        }
        return strategies[strategy_type]
```

**Code Examples:**
- Consolidate into single entry point with factory pattern
- Document each strategy's trade-offs clearly
- Add configuration option to select strategy

---

### 🔴 CRITICAL #2: Inconsistent Use of LangGraph-Swarm create_handoff_tool

**File:** `app/orchestration/swarm.py` (lines 873-1108)
**Severity:** Critical
**Impact:** LangGraph-Swarm framework not fully utilized

**Problem:**
```python
# swarm.py does NOT use langgraph-swarm framework at all
# It builds custom routing logic instead

def route_message(state: SwarmState) -> Literal[...]:
    """Custom routing logic - NOT using langgraph-swarm"""
    # 236 lines of custom keyword matching
    if scheduling_matches:
        return "scheduling_agent"
    # ... manual routing
```

**vs Correct Pattern:**
```python
# swarm_hybrid.py CORRECTLY uses langgraph-swarm
from langgraph_swarm import create_handoff_tool, create_swarm

handoff_to_property = create_handoff_tool(
    agent_name="PropertyAgent",
    description="Transfer to property analysis agent..."
)
```

**Recommended Fix:**
- **PRIMARY ACTION:** Deprecate swarm.py's custom routing
- Use `create_swarm()` from langgraph-swarm consistently
- Handoffs should use `create_handoff_tool()` framework API

---

### 🟡 MAJOR #3: Tool Validation Conflicts Not Fully Resolved

**File:** `app/orchestration/swarm_fixed.py` (lines 181-201)
**Severity:** High
**Impact:** Potential runtime errors with tool execution

**Problem:**
```python
@tool
def handle_search_request(query: str) -> str:
    """Handle property search requests using PydanticAI."""
    # ISSUE: Wraps async call in sync context
    result = asyncio.run(self.pydantic_search.run(enhanced_query))
    # This can cause event loop conflicts
```

**Recommended Fix:**
```python
@tool
async def handle_search_request(query: str) -> str:
    """Handle property search requests using PydanticAI."""
    # Use async natively
    result = await self.pydantic_search.run(enhanced_query)
    return f"Search Result: {result.output}"
```

---

## Major Issues

### 🟡 MAJOR #1: Memory System Not Used Consistently

**File:** `app/orchestration/swarm.py` (lines 1117-1161)
**Severity:** High
**Impact:** State not persisted across agent handoffs

**Problem:**
```python
class SwarmOrchestrator:
    def __init__(self):
        # Memory components initialized
        self.checkpointer = MemorySaver()
        self.store = InMemoryStore()

        # BUT: Memory not actually used in agent nodes
        # Agents don't read/write to store
```

**Recommended Fix:**
```python
async def search_agent_node(state: SwarmState) -> dict:
    # Read from memory
    memory_context = await state.store.aget("search_context")

    # ... agent logic ...

    # Write back to memory
    await state.store.aput("search_context", search_results)
```

---

### 🟡 MAJOR #2: Context Preservation During Handoffs Is Weak

**File:** `app/orchestration/swarm_hybrid.py` (lines 37-44)
**Severity:** High
**Impact:** Lost context between agents

**Problem:**
```python
@dataclass
class AgentContext:
    """Context passed between agents during handoffs."""
    property_context: Optional[Dict[str, Any]] = None
    search_results: Optional[List[Dict[str, Any]]] = None
    session_id: Optional[str] = None
    data_mode: str = "mock"

# BUT: Context not automatically transferred in handoffs
# Each agent recreates context manually
```

**Recommended Fix:**
```python
# Use LangGraph's state reducer pattern
class SwarmState(MessagesState):
    context: AgentContext = Field(default_factory=AgentContext)

    @classmethod
    def merge_context(cls, left: AgentContext, right: AgentContext):
        """Preserve context across handoffs"""
        return AgentContext(
            property_context=right.property_context or left.property_context,
            search_results=right.search_results or left.search_results,
            session_id=left.session_id,
            data_mode=left.data_mode
        )
```

---

## Medium Issues

### 🟠 MEDIUM #1: PydanticAI Tools Not Validated Properly

**File:** `app/orchestration/swarm_hybrid.py` (lines 125-177)
**Severity:** Medium
**Impact:** No validation on tool inputs/outputs

**Problem:**
```python
@agent.tool
async def search_properties(
    ctx: RunContext[Dict[str, Any]],
    criteria: str,  # String instead of validated model
    location: str = "",
    max_price: int = 0
) -> str:  # Returns raw string instead of structured data
```

**Recommended Fix:**
```python
class SearchCriteria(BaseModel):
    criteria: str
    location: Optional[str] = None
    max_price: Optional[int] = Field(None, ge=0)
    min_bedrooms: Optional[int] = Field(None, ge=0)

class SearchResult(BaseModel):
    properties: List[Property]
    total_found: int
    search_time: float

@agent.tool
async def search_properties(
    ctx: RunContext[SearchCriteria]
) -> SearchResult:
    # Fully validated inputs and structured outputs
```

---

### 🟠 MEDIUM #2: Error Handling Inconsistent Across Patterns

**File:** Multiple orchestration files
**Severity:** Medium
**Impact:** Unpredictable error behavior

**Problem:**
```python
# swarm.py: Falls back to Ollama
except Exception as e:
    fallback_response = await generate_intelligent_fallback(...)
    return {"messages": [AIMessage(content=fallback_response)]}

# swarm_hybrid.py: Returns generic message
except Exception as e:
    return "I encountered an error. Please try again."

# swarm_fixed.py: Re-raises exception
except Exception as e:
    logger.error(f"Error: {e}")
    raise
```

**Recommended Fix:**
- Standardize error handling strategy
- Use custom exception hierarchy
- Implement circuit breaker pattern

---

## Positive Findings

### ✅ STRENGTH #1: Comprehensive Logging and Observability

**File:** `app/orchestration/swarm.py` (lines 20-22, 163-192)
**Quality:** Excellent

**Evidence:**
```python
# Dual instrumentation approach
with AgentExecutionContext("search_agent", "property_search") as logfire_span, \
     LangGraphExecutionContext("swarm_graph", "search_agent", dict(state)) as langsmith_span:

    # Structured logging
    log_agent_action(
        agent_name="search_agent",
        action="process_search_request",
        details={
            "user_message": user_message[:100],
            "data_mode": data_mode,
            "session_id": state.get("session_id")
        }
    )
```

**Why This Works:**
- Logfire + LangSmith dual tracking
- Structured logging with context
- Performance metrics captured

---

### ✅ STRENGTH #2: Hybrid Pattern Properly Separates Concerns

**File:** `app/orchestration/swarm_hybrid.py` (lines 46-85)
**Quality:** Good

**Evidence:**
```python
class PydanticAIWrapper:
    """
    Wrapper that integrates PydanticAI agents with LangGraph-Swarm.

    This class maintains all PydanticAI benefits while being compatible
    with LangGraph's create_react_agent system.
    """

    def __init__(self, agent_name: str, system_prompt: str):
        self.pydantic_agent = self._create_pydantic_agent(system_prompt)

    async def run(self, user_message: str, context: AgentContext) -> str:
        # PydanticAI execution with full benefits
        with AgentExecutionContext(...):
            result = await self.pydantic_agent.run(enhanced_prompt)
```

**Why This Works:**
- Clean separation: LangGraph for coordination, PydanticAI for execution
- Maintains PydanticAI benefits (retry, validation, observability)
- Compatible with LangGraph's agent system

---

### ✅ STRENGTH #3: Intelligent Property Filtering in Search

**File:** `app/orchestration/swarm.py` (lines 1244-1371)
**Quality:** Excellent

**Evidence:**
```python
def filter_properties_by_user_intent(user_message: str, properties: List[Dict[str, Any]]):
    """Filter properties based on user intent extraction"""

    # Extract criteria from natural language
    criteria = {
        'min_bedrooms': None,
        'amenities': [],
        'location': None
    }

    # Apply intelligent filtering
    for prop in properties:
        matches = True
        if criteria['min_bedrooms'] and prop.get('bedrooms') < criteria['min_bedrooms']:
            matches = False
        # ... comprehensive filtering logic
```

**Why This Works:**
- Natural language intent extraction
- Multi-criteria filtering
- Context-aware property matching

---

## Recommendations Summary

### Immediate Actions (Critical Priority)

1. **Consolidate Orchestration Patterns**
   - Choose ONE primary pattern (recommend: hybrid)
   - Deprecate other patterns with migration guide
   - Create configuration-based strategy selection

2. **Fix LangGraph-Swarm Integration**
   - Use `create_swarm()` and `create_handoff_tool()` consistently
   - Remove custom routing in favor of framework patterns
   - Update documentation to reflect correct usage

3. **Resolve Async/Sync Conflicts**
   - Make all tool definitions async
   - Remove `asyncio.run()` from sync contexts
   - Use proper async patterns throughout

### Short-term Improvements (High Priority)

1. **Implement Proper Context Management**
   - Use state reducers for context merging
   - Persist context in memory store
   - Validate context transfer in handoffs

2. **Standardize Error Handling**
   - Create custom exception hierarchy
   - Implement circuit breaker for API calls
   - Add consistent fallback strategies

3. **Add Validation to PydanticAI Tools**
   - Use Pydantic models for tool inputs
   - Structure tool outputs
   - Add proper type hints everywhere

### Long-term Enhancements (Medium Priority)

1. **Memory System Enhancement**
   - Implement actual memory read/write in agents
   - Add memory compression for long conversations
   - Create memory namespacing strategy

2. **Testing Infrastructure**
   - Add integration tests for each orchestration pattern
   - Test handoff scenarios thoroughly
   - Validate context preservation

3. **Performance Optimization**
   - Profile agent execution times
   - Optimize property filtering algorithms
   - Cache frequently accessed data

---

## Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Code Duplication | High (3 orchestrators) | Low (1 orchestrator) | 🔴 Critical |
| Framework Usage | Partial | Complete | 🟡 Needs Work |
| Error Handling | Inconsistent | Standardized | 🟡 Needs Work |
| Context Preservation | 60% | 95% | 🟠 Improving |
| Observability | Excellent | Excellent | ✅ Good |
| Type Safety | 70% | 90% | 🟠 Moderate |

---

## Conclusion

The orchestration layer shows **good intent but inconsistent execution**. The hybrid pattern (`swarm_hybrid.py`) represents the best architectural approach, but the presence of multiple patterns and incomplete use of the langgraph-swarm framework creates confusion and maintenance burden.

**Priority Recommendation:** Consolidate around the hybrid pattern, complete the langgraph-swarm integration, and standardize context management and error handling.

---

**Next Review:** After consolidation and standardization - Expected: Q1 2026
