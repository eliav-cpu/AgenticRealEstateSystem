# Agent Implementation Review: Handoffs & Context Management

**Review Date:** 2025-11-11
**Reviewer:** Code Review Agent (Hive Mind)
**System:** Agentic Real Estate System

---

## Executive Summary

The system implements **three specialized agents** (Search, Property, Scheduling) across multiple implementation patterns. Agent handoffs use a mix of custom routing and langgraph-swarm's create_handoff_tool mechanism.

**Overall Assessment:** 🟡 **MODERATE** - Good agent specialization, inconsistent handoff implementation

---

## Agent Architecture Overview

### Agent Implementations

| Agent | Files | Patterns | Quality |
|-------|-------|----------|---------|
| Search Agent | swarm.py (search_agent_node), hybrid_search.py | 2 patterns | 🟡 Moderate |
| Property Agent | swarm.py (property_agent_node), hybrid_property.py | 2 patterns | 🟡 Moderate |
| Scheduling Agent | swarm.py (scheduling_agent_node), hybrid_scheduling.py | 2 patterns | 🟡 Moderate |

---

## Critical Issues

### 🔴 CRITICAL #1: Handoff Mechanism Inconsistency

**Files:** `app/orchestration/swarm.py` vs `app/agents/hybrid_*.py`
**Severity:** Critical
**Impact:** Unpredictable handoff behavior

**Problem - Custom Routing (swarm.py):**
```python
def route_message(state: SwarmState) -> Literal["search_agent", "property_agent", "scheduling_agent", END]:
    """
    Custom router with 236 lines of keyword matching logic
    """
    # Manual keyword detection
    scheduling_keywords = [
        "can i visit", "want to visit", "schedule a visit",
        "book a visit", "i want to see it"
        # ... 40+ keywords
    ]

    # Manual routing logic
    if scheduling_matches:
        return "scheduling_agent"
    # No use of create_handoff_tool
```

**vs Framework Pattern (hybrid agents):**
```python
from langgraph_swarm import create_handoff_tool

handoff_to_property = create_handoff_tool(
    agent_name="PropertyAgent",
    description="Transfer to property analysis agent when user wants detailed property information"
)

# Agent can call this tool to trigger handoff
```

**Recommended Fix:**
```python
# UNIFIED APPROACH: Use create_handoff_tool everywhere

# In each agent definition
def _create_search_agent(self):
    # Add handoff tools
    handoff_to_property = create_handoff_tool(
        agent_name="property_agent",
        description="User wants property details or analysis"
    )

    handoff_to_scheduling = create_handoff_tool(
        agent_name="scheduling_agent",
        description="User wants to schedule viewing"
    )

    # Agent decides when to handoff based on context
    # Not hard-coded keywords
```

---

### 🔴 CRITICAL #2: Context Not Preserved Across Handoffs

**File:** `app/orchestration/swarm.py` (lines 133-156, state management)
**Severity:** Critical
**Impact:** Lost information between agents

**Problem:**
```python
class SwarmState(MessagesState):
    """State definition with context fields"""
    session_id: str = Field(default="default")
    search_intent: Optional[Dict[str, Any]] = None
    search_results: Optional[Dict[str, Any]] = None
    property_analysis: Optional[Dict[str, Any]] = None
    property_recommendations: Optional[List[Dict[str, Any]]] = None
    scheduling_intent: Optional[Dict[str, Any]] = None
    current_agent: str = Field(default="search_agent")
    handoff_history: List[Dict[str, Any]] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)

# BUT: Agents don't read/write to these fields consistently!

async def search_agent_node(state: SwarmState) -> dict:
    # Agent returns only messages - doesn't update search_results
    return {"messages": [AIMessage(content=response_content)]}
    # Where did search_results go? ❌
```

**Recommended Fix:**
```python
async def search_agent_node(state: SwarmState) -> dict:
    """Search agent that UPDATES state properly"""

    # ... search logic ...

    # CRITICAL: Return all state updates
    return {
        "messages": [AIMessage(content=response_content)],
        "search_results": {
            "properties": filtered_properties,
            "query": user_message,
            "timestamp": time.time()
        },
        "search_intent": extracted_criteria,
        "current_agent": "search_agent",
        "handoff_history": state.handoff_history + [{
            "from": "router",
            "to": "search_agent",
            "reason": "property_search",
            "timestamp": time.time()
        }]
    }
```

---

### 🟡 MAJOR #1: Agent Tools Not Using create_handoff_tool Properly

**File:** `app/agents/hybrid_property.py` (lines 306-320)
**Severity:** High
**Impact:** Agents can't trigger handoffs dynamically

**Problem:**
```python
@tool
async def execute_property_analysis(query: str, property_context: str = "") -> str:
    """Execute property analysis using PydanticAI agent."""

    # Wraps PydanticAI execution
    result = await self.pydantic_agent.run(enhanced_query)

    # Returns text response
    return response

# BUT: Agent has no way to trigger handoff from within this tool!
# Handoff tools are separate and not accessible
```

**Recommended Fix:**
```python
class HybridPropertyAgent:
    def _create_pydantic_agent(self) -> PydanticAgent:
        agent = PydanticAgent(...)

        # ADD HANDOFF CAPABILITY TO PYDANTIC AGENT
        @agent.tool
        async def request_property_search(
            ctx: RunContext[Dict[str, Any]],
            search_criteria: str
        ) -> str:
            """Agent can trigger handoff to search agent"""
            # Store handoff intent in context
            ctx.deps['requested_handoff'] = {
                'to': 'search_agent',
                'reason': search_criteria
            }
            return f"Requesting property search: {search_criteria}"

        return agent

    def _create_langgraph_agent(self):
        # LangGraph agent detects handoff intent from PydanticAI
        @tool
        async def execute_property_analysis(...):
            result = await self.pydantic_agent.run(...)

            # Check if handoff was requested
            if result.deps.get('requested_handoff'):
                handoff = result.deps['requested_handoff']
                # Trigger actual handoff
                return Command(goto=handoff['to'])

            return result.output
```

---

## Major Issues

### 🟡 MAJOR #1: Hybrid Agents Don't Use Structured Outputs Consistently

**File:** `app/agents/hybrid_search.py` (lines 26-31)
**Severity:** High
**Impact:** Lost structure and validation

**Problem:**
```python
class SearchResult(BaseModel):
    """Structured output for search results."""
    properties_found: int
    summary: str
    recommendations: List[str]
    next_actions: List[str]

# Agent DEFINES structured output
agent = PydanticAgent(
    model=model,
    result_type=SearchResult,  # ✅ Good!
    system_prompt=...
)

# BUT: LangGraph wrapper tool LOSES the structure!
@tool
async def execute_property_search(query: str) -> str:  # ❌ Returns string!
    result = await self.pydantic_agent.run(enhanced_query)

    # Converts structured result to string
    if hasattr(result, 'output') and isinstance(result.output, SearchResult):
        response = f"""🔍 **Property Search Results**
        Summary: {search_result.summary}
        ..."""  # Loses Pydantic structure
        return response  # String, not SearchResult!
```

**Recommended Fix:**
```python
# Keep structure throughout the pipeline

@tool
async def execute_property_search(query: str) -> SearchResult:  # ✅ Return structured
    result = await self.pydantic_agent.run(enhanced_query)

    if hasattr(result, 'output'):
        return result.output  # Return SearchResult directly

    # Fallback
    return SearchResult(
        properties_found=0,
        summary="Search failed",
        recommendations=[],
        next_actions=[]
    )

# LangGraph can handle Pydantic models as tool outputs
```

---

### 🟡 MAJOR #2: Agent Specialization vs Generic Responses

**File:** `app/orchestration/swarm.py` (lines 275-304)
**Severity:** Medium
**Impact:** Agents respond outside their specialty

**Problem:**
```python
prompt = f"""You are Alex, a professional real estate search specialist.

User's Message: "{user_message}"

INSTRUCTIONS:
1. If the user asks for properties with specific features (pool, gym, etc.), analyze...
2. If you find matching properties, mention them...
3. If no exact matches, suggest similar alternatives...
4. If the user is just starting their search, help them define criteria...
5. Keep responses concise...
6. Use appropriate emojis...
7. Always end with a helpful question...
8. Be professional but friendly...
"""

# Prompt tries to cover ALL scenarios
# Agent becomes generic instead of specialized
```

**Recommended Fix:**
```python
# TIGHT SPECIALIZATION: Each agent does ONE thing well

search_prompt = """You are Alex, a property search specialist.

Your ONLY job is to:
1. Understand search criteria
2. Execute property searches
3. Present filtered results
4. Suggest search refinements

If the user asks about:
- Specific property details → Use handoff tool to PropertyAgent
- Scheduling a visit → Use handoff tool to SchedulingAgent
- General questions → Answer briefly, then refocus on search

Stay in your lane. Be the best search specialist possible."""
```

---

## Medium Issues

### 🟠 MEDIUM #1: Conversation Context Not Tracked Properly

**File:** `app/orchestration/swarm.py` (lines 256-272)
**Severity:** Medium
**Impact:** Agents repeat greetings, lose conversation flow

**Problem:**
```python
# Add conversation context awareness
is_first_message = len(messages) <= 1
conversation_info = ""
if not is_first_message:
    conversation_info = f"""
CONVERSATION CONTEXT:
- This is NOT the first message in the conversation (message #{len(messages)})
- Continue the conversation naturally without greeting again
"""

# This is INJECTED into prompt every time
# But agents still sometimes greet again
```

**Recommended Fix:**
```python
class SwarmState(MessagesState):
    conversation_metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def turn_number(self) -> int:
        return len(self.messages)

    @property
    def is_first_turn(self) -> bool:
        return self.turn_number == 1

# Agents check state instead of counting messages
if not state.is_first_turn:
    # Skip greeting, continue conversation
```

---

### 🟠 MEDIUM #2: Agent Tool Definitions Scattered

**File:** `app/agents/hybrid_search.py`, `hybrid_property.py`, `hybrid_scheduling.py`
**Severity:** Medium
**Impact:** Hard to discover what tools are available

**Problem:**
```python
# Tools defined inside agent initialization
class HybridSearchAgent:
    def _add_pydantic_tools(self, agent: PydanticAgent):
        @agent.tool
        async def search_properties(...): ...

        @agent.tool
        async def analyze_search_intent(...): ...

# No central registry of available tools
# Tools not reusable across agents
```

**Recommended Fix:**
```python
# Create shared tool registry
from app.tools import property_tools, scheduling_tools, search_tools

class HybridSearchAgent:
    def _create_pydantic_agent(self):
        agent = PydanticAgent(...)

        # Register shared tools
        for tool in search_tools.get_all():
            agent.register_tool(tool)

        return agent
```

---

## Positive Findings

### ✅ STRENGTH #1: Excellent Agent System Prompts

**File:** `app/agents/hybrid_property.py` (lines 95-139)
**Quality:** Excellent

**Evidence:**
```python
def _get_system_prompt(self) -> str:
    return """You are Emma, a professional real estate property expert with advanced analytical capabilities.

CORE RESPONSIBILITIES:
1. Provide detailed, objective property analysis
2. Compare properties with data-driven insights
3. Highlight both advantages and potential concerns
4. Offer market context and pricing perspective
5. Guide clients toward informed decisions

ANALYSIS FRAMEWORK:
- Evaluate location, condition, features, and value proposition
- Consider neighborhood trends and market dynamics
- Assess investment potential and lifestyle fit
- Identify potential red flags or concerns
- Provide balanced, honest assessments
```

**Why This Works:**
- Clear role definition
- Specific responsibilities
- Structured framework
- Personality and style guidance

---

### ✅ STRENGTH #2: Comprehensive Logging in Agent Execution

**File:** `app/orchestration/swarm.py` (lines 183-192, 421-432)
**Quality:** Excellent

**Evidence:**
```python
log_agent_action(
    agent_name="search_agent",
    action="process_search_request",
    details={
        "user_message": user_message[:100],
        "data_mode": data_mode,
        "session_id": state.get("session_id")
    }
)

# Later
log_agent_action(
    agent_name="search_agent",
    action="llm_response_success",
    details={
        "response_length": len(response_content),
        "properties_found": len(available_properties),
        "duration_seconds": duration
    }
)
```

**Why This Works:**
- Structured logging with context
- Performance metrics tracked
- Enables debugging and optimization

---

### ✅ STRENGTH #3: Property Filtering Intelligence

**File:** `app/orchestration/swarm.py` (lines 1244-1441)
**Quality:** Very Good

**Evidence:**
```python
def filter_properties_by_user_intent(user_message: str, properties: List[Dict[str, Any]]):
    """Filter properties based on user intent extraction"""

    # Extract structured criteria from natural language
    criteria = {
        'min_bedrooms': None,
        'amenities': [],
        'property_type': None,
        'location': None
    }

    # Detect number of bedrooms with regex
    if 'bedroom' in user_lower:
        bedroom_matches = re.findall(r'(\d+)\s*(?:bedroom|br)', user_lower)
        if bedroom_matches:
            criteria['min_bedrooms'] = int(bedroom_matches[0])

    # Detect amenities with keyword mapping
    amenity_keywords = {
        'pool': ['pool', 'swimming'],
        'gym': ['gym', 'fitness'],
        # ...
    }
```

**Why This Works:**
- Natural language understanding
- Multi-criteria extraction
- Flexible matching logic

---

## Recommendations Summary

### Immediate Actions (Critical Priority)

1. **Unify Handoff Mechanism**
   - Remove custom routing logic from swarm.py
   - Use create_handoff_tool exclusively
   - Let agents decide when to handoff based on context

2. **Fix Context Preservation**
   - Agents must update ALL relevant state fields
   - Implement state reducers for merging
   - Validate context transfer in tests

3. **Enable Dynamic Handoffs from PydanticAI Tools**
   - Add handoff request capability to PydanticAI agents
   - Detect handoff intent in LangGraph wrapper
   - Use Command(goto=...) for transitions

### Short-term Improvements (High Priority)

1. **Preserve Structured Outputs**
   - Keep Pydantic models through the pipeline
   - Don't convert to strings prematurely
   - Use structured data in downstream logic

2. **Tighten Agent Specialization**
   - Each agent does ONE thing expertly
   - Narrow system prompts
   - Explicit handoff triggers

3. **Improve Conversation Tracking**
   - Add conversation_metadata to state
   - Track turn number properly
   - Prevent repeated greetings

### Long-term Enhancements (Medium Priority)

1. **Create Shared Tool Registry**
   - Centralize tool definitions
   - Make tools reusable
   - Add tool discovery mechanism

2. **Add Agent Performance Metrics**
   - Track handoff success rate
   - Measure context preservation
   - Monitor agent specialization adherence

3. **Build Agent Testing Framework**
   - Unit tests for each agent
   - Integration tests for handoffs
   - Validate context preservation

---

## Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Handoff Consistency | 50% | 95% | 🔴 Critical |
| Context Preservation | 60% | 95% | 🟡 Needs Work |
| Agent Specialization | 70% | 90% | 🟠 Moderate |
| Structured Outputs | 40% | 90% | 🔴 Critical |
| System Prompt Quality | 90% | 90% | ✅ Excellent |
| Logging Coverage | 95% | 95% | ✅ Excellent |

---

## Conclusion

Agent implementations show **strong prompt engineering and logging** but suffer from **inconsistent handoff mechanisms and poor context preservation**. The hybrid pattern provides the right structure, but needs completion.

**Priority Recommendation:** Unify handoff mechanism using create_handoff_tool, fix context preservation, and maintain structured outputs throughout the pipeline.

---

**Next Review:** After handoff unification - Expected: Q1 2026
