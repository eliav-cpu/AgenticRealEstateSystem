# Agent Routing System

## Overview

The intelligent routing system coordinates handoffs between agents with context-aware decision making and proper state preservation.

## Architecture

### Components

1. **IntelligentRouter** (`app/agents/router.py`)
   - Intent detection from user messages
   - Context-aware routing decisions
   - Handoff validation
   - Memory-backed decision tracking

2. **Handoff Tools** (in each agent file)
   - `handoff_to_property()` - Transfer to property analysis
   - `handoff_to_scheduling()` - Transfer to scheduling
   - `handoff_to_search()` - Transfer to search

3. **Agent Integration**
   - `search.py` - Search agent with handoff tools
   - `property.py` - Property agent with handoff tools
   - `scheduling.py` - Scheduling agent with handoff tools

## Routing Rules

### Intent Detection

The router detects intents based on keywords and context:

**Search Intent**
```
Keywords: "search", "find", "looking for", "need", "want",
          "apartment", "house", "property", "bedroom", "price"
Route to: search_agent
```

**Property Analysis Intent**
```
Keywords: "tell me about", "details", "features", "compare", "describe"
Route to: property_agent
Requires: search_results or selected_property in context
```

**Scheduling Intent**
```
Keywords: "schedule", "visit", "tour", "appointment", "tomorrow", "when"
Route to: scheduling_agent
Requires: selected_property in context
High confidence: 0.95 with property, 0.7 without
```

### Context-Aware Routing

When intent is unclear, router uses conversation context:

1. **Property selected** → route to `property_agent`
2. **Search results available** → route to `property_agent`
3. **No context** → route to `search_agent` (default)

### Handoff Validation

Before executing handoffs, the router validates:

- **Scheduling requires property**: Cannot schedule without property selection
- **Circular handoff prevention**: Max 3 handoffs to prevent loops
- **Context preservation**: Required context must be available

## Usage Examples

### Example 1: Search → Property Handoff

```python
# User: "I need a 2BR apartment in Miami"
# Router detects: Intent.SEARCH

# Search agent finds properties
properties = [...]

# Search agent uses handoff tool:
return handoff_to_property(
    properties=properties,
    reason="Found 5 properties for analysis",
    state=state
)

# Context preserved:
# - search_results
# - user_preferences
# - handoff_reason
```

### Example 2: Property → Scheduling Handoff

```python
# User: "Schedule a visit for tomorrow"
# Router detects: Intent.SCHEDULING

# Property agent has selected property
selected_property = state.get("selected_property")

# Property agent uses handoff tool:
return handoff_to_scheduling(
    selected_property=selected_property,
    reason="User wants to schedule property visit",
    state=state
)

# Context preserved:
# - selected_property (full details)
# - user_preferences
# - handoff_reason
```

### Example 3: Scheduling → Search Handoff

```python
# User: "Show me more properties"
# Router detects: Intent.SEARCH

# Scheduling agent completes appointment
# User wants new search

# Scheduling agent uses handoff tool:
return handoff_to_search(
    reason="User wants more property options",
    user_preferences=state.get("user_preferences"),
    state=state
)

# Context preserved:
# - user_preferences (from previous search)
# - handoff_reason
```

## Context Preservation

### What Gets Preserved

Each handoff preserves relevant context:

**Search → Property**
- `search_results`: All found properties
- `user_preferences`: Search criteria
- `from_agent`: Source agent name

**Property → Scheduling**
- `selected_property`: Full property details
- `user_preferences`: User requirements
- `from_agent`: Source agent name

**Scheduling → Search**
- `user_preferences`: Previous search criteria
- `previous_scheduling`: Appointment history
- `from_agent`: Source agent name

### Context Structure

```python
preserved_context = {
    "search_results": {...},       # Optional
    "selected_property": {...},    # Optional
    "user_preferences": {...},     # Optional
    "handoff_reason": "string",    # Required
    "from_agent": "agent_name",    # Required
    "handoff_trigger": "trigger",  # Required
    "handoff_count": 1             # Auto-incremented
}
```

## Datetime Integration

The scheduling agent integrates with `datetime_context.py`:

```python
from app.utils.datetime_context import (
    get_agent_datetime_context,
    format_datetime_context_for_agent
)

# Get context for system prompt
datetime_context = format_datetime_context_for_agent()

# System prompt includes:
# - Current date/time
# - Relative date mappings (tomorrow, next week, etc.)
# - Timezone information
```

## Memory Coordination

Routing decisions are stored in memory via hooks:

### Setup

Run the memory storage script:
```bash
./scripts/store_routing_decisions.sh
```

### What Gets Stored

1. **Routing Decisions**
   ```json
   {
     "intent": "property_analysis",
     "confidence": 0.9,
     "trigger": "properties_found",
     "timestamp": "2025-11-11T17:55:48Z"
   }
   ```

2. **Coordination Metadata**
   ```json
   {
     "version": "1.0.0",
     "agents": ["search_agent", "property_agent", "scheduling_agent"],
     "routing_patterns": {...},
     "context_preservation": true,
     "intent_detection": true
   }
   ```

3. **Handoff Validation Rules**
   ```json
   {
     "scheduling_requires_property": true,
     "max_handoff_count": 3,
     "context_preservation_required": true
   }
   ```

### Memory Keys

- `swarm/routing/{agent}_to_{target}` - Individual routing decisions
- `swarm/shared/routing_config` - System configuration
- `swarm/shared/handoff_rules` - Validation rules

## Testing

Run the routing system tests:

```bash
pytest tests/test_router.py -v
```

### Test Coverage

- Intent detection for all agent types
- Routing decisions with various contexts
- Context preservation during handoffs
- Handoff validation rules
- Context-based routing fallbacks

## Integration with Swarm

### Using with LangGraph

```python
from app.agents import get_router

# In agent node function
router = get_router()

# Detect intent
routing_decision = router.route(user_message, state)

# Execute handoff if needed
if routing_decision.intent == Intent.SCHEDULING:
    return handoff_to_scheduling(...)
```

### Coordination via Hooks

**Before work:**
```bash
npx claude-flow@alpha hooks pre-task --description "Process user query"
```

**During work:**
```bash
npx claude-flow@alpha hooks post-edit \
    --file "app/agents/router.py" \
    --memory-key "swarm/routing/decision"
```

**After work:**
```bash
npx claude-flow@alpha hooks post-task \
    --task-id "routing-123" \
    --success true
```

## Troubleshooting

### Common Issues

**Issue: Circular handoffs**
- Check `handoff_count` in context
- Validate routing decisions are correct
- Ensure intent detection is accurate

**Issue: Context not preserved**
- Verify handoff tools include all required context
- Check state updates in Command objects
- Review memory storage logs

**Issue: Scheduling without property**
- Validation should catch this
- Check `validate_handoff()` is being called
- Ensure property context is set before scheduling

### Debug Logging

Enable detailed logging:
```python
import logging
logging.getLogger("router").setLevel(logging.DEBUG)
logging.getLogger("search_agent").setLevel(logging.DEBUG)
logging.getLogger("property_agent").setLevel(logging.DEBUG)
logging.getLogger("scheduling_agent").setLevel(logging.DEBUG)
```

## Future Enhancements

1. **ML-based Intent Detection**
   - Train on conversation patterns
   - Improve confidence scoring
   - Personalized routing based on user history

2. **Advanced Context Preservation**
   - Conversation summarization
   - Long-term memory integration
   - User preference learning

3. **Dynamic Routing Rules**
   - A/B testing different routing strategies
   - Adaptive routing based on success metrics
   - User-specific routing preferences

4. **Multi-turn Conversation Handling**
   - Track conversation state across sessions
   - Resume interrupted conversations
   - Handle clarification dialogs

## References

- [LangGraph Command Documentation](https://langchain-ai.github.io/langgraph/)
- [Pydantic AI Agents](https://ai.pydantic.dev/)
- [Claude Flow Hooks](https://github.com/ruvnet/claude-flow)
- [Project Architecture](./ARCHITECTURE.md)
