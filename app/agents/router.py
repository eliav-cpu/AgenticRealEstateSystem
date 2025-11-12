"""
Intelligent Router for Agent Coordination

Centralized routing logic with:
- Intent detection based on conversation patterns
- Context-aware routing with state preservation
- Proper handoff triggers and validation
- Memory-backed decision tracking
"""

from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

from ..utils.logging import get_logger, log_handoff

class AgentType(str, Enum):
    """Available agent types in the system."""
    SEARCH = "search_agent"
    PROPERTY = "property_agent"
    SCHEDULING = "scheduling_agent"

class Intent(str, Enum):
    """User intent categories."""
    SEARCH = "search"
    PROPERTY_ANALYSIS = "property_analysis"
    SCHEDULING = "scheduling"
    CLARIFICATION = "clarification"
    UNKNOWN = "unknown"

class RoutingDecision(BaseModel):
    """Represents a routing decision with full context."""
    target_agent: AgentType = Field(..., description="Agent to route to")
    intent: Intent = Field(..., description="Detected user intent")
    confidence: float = Field(..., description="Confidence in routing decision (0-1)")
    reasoning: str = Field(..., description="Explanation for routing decision")
    context_to_preserve: Dict[str, Any] = Field(default_factory=dict, description="Context to carry forward")
    handoff_trigger: str = Field(..., description="What triggered the handoff")
    timestamp: datetime = Field(default_factory=datetime.now, description="When decision was made")

class ConversationContext(BaseModel):
    """Tracks conversation state across agent transitions."""
    current_agent: Optional[AgentType] = None
    previous_agent: Optional[AgentType] = None
    search_results: Optional[Dict[str, Any]] = None
    selected_property: Optional[Dict[str, Any]] = None
    pending_appointment: Optional[Dict[str, Any]] = None
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    conversation_history: List[str] = Field(default_factory=list)
    handoff_count: int = 0

class IntelligentRouter:
    """
    Centralized router with intent detection and context-aware routing.

    Routes user queries to appropriate agents based on:
    1. Explicit intent keywords
    2. Conversation context and state
    3. Current agent capabilities
    4. Previous interaction patterns
    """

    def __init__(self):
        self.logger = get_logger("router")

        # Intent detection patterns
        self.search_keywords = [
            "search", "find", "looking for", "need", "want",
            "apartment", "house", "property", "condo", "studio",
            "bedroom", "br", "bathroom", "ba",
            "location", "neighborhood", "area", "city",
            "price", "budget", "afford", "rent", "buy"
        ]

        self.property_keywords = [
            "tell me about", "this property", "details", "information",
            "describe", "features", "amenities", "pros", "cons",
            "compare", "difference", "better", "similar",
            "photos", "images", "floor plan", "layout"
        ]

        self.scheduling_keywords = [
            "schedule", "visit", "tour", "appointment", "viewing",
            "see", "when", "available", "calendar", "book",
            "tomorrow", "today", "next week", "this weekend",
            "morning", "afternoon", "evening",
            "confirm", "reserve", "time", "date"
        ]

    def detect_intent(self, user_message: str, context: ConversationContext) -> Intent:
        """
        Detect user intent from message and context.

        Args:
            user_message: User's message text
            context: Current conversation context

        Returns:
            Detected intent enum
        """
        message_lower = user_message.lower()

        # Check for scheduling intent (highest priority if property selected)
        if context.selected_property and any(kw in message_lower for kw in self.scheduling_keywords):
            return Intent.SCHEDULING

        # Check for property analysis intent
        if any(kw in message_lower for kw in self.property_keywords):
            return Intent.PROPERTY_ANALYSIS

        # Check for search intent
        if any(kw in message_lower for kw in self.search_keywords):
            return Intent.SEARCH

        # Context-based intent detection
        if context.search_results and "properties" in context.search_results:
            # User has search results but no clear intent - likely wants property analysis
            return Intent.PROPERTY_ANALYSIS

        return Intent.UNKNOWN

    def route(self, user_message: str, state: Dict[str, Any]) -> RoutingDecision:
        """
        Main routing logic with context awareness.

        Args:
            user_message: User's message text
            state: Current conversation state from LangGraph

        Returns:
            RoutingDecision with target agent and context
        """
        # Build conversation context from state
        context = self._build_context_from_state(state)

        # Detect intent
        intent = self.detect_intent(user_message, context)

        # Make routing decision based on intent and context
        if intent == Intent.SEARCH:
            return self._route_to_search(user_message, context)
        elif intent == Intent.PROPERTY_ANALYSIS:
            return self._route_to_property(user_message, context)
        elif intent == Intent.SCHEDULING:
            return self._route_to_scheduling(user_message, context)
        else:
            return self._route_by_context(user_message, context)

    def _route_to_search(self, message: str, context: ConversationContext) -> RoutingDecision:
        """Route to search agent with search criteria context."""

        preserved_context = {
            "user_preferences": context.user_preferences,
            "previous_searches": self._extract_previous_searches(context),
            "from_agent": context.current_agent.value if context.current_agent else "router"
        }

        decision = RoutingDecision(
            target_agent=AgentType.SEARCH,
            intent=Intent.SEARCH,
            confidence=0.9,
            reasoning="User expressed search intent with property criteria",
            context_to_preserve=preserved_context,
            handoff_trigger="search_keywords_detected"
        )

        log_handoff(
            context.current_agent.value if context.current_agent else "router",
            "search_agent",
            f"Search intent: {message[:50]}..."
        )

        return decision

    def _route_to_property(self, message: str, context: ConversationContext) -> RoutingDecision:
        """Route to property agent with property context."""

        preserved_context = {
            "search_results": context.search_results,
            "selected_property": context.selected_property,
            "user_preferences": context.user_preferences,
            "from_agent": context.current_agent.value if context.current_agent else "router"
        }

        decision = RoutingDecision(
            target_agent=AgentType.PROPERTY,
            intent=Intent.PROPERTY_ANALYSIS,
            confidence=0.85,
            reasoning="User wants property analysis or comparison",
            context_to_preserve=preserved_context,
            handoff_trigger="property_analysis_requested"
        )

        log_handoff(
            context.current_agent.value if context.current_agent else "router",
            "property_agent",
            f"Property analysis intent: {message[:50]}..."
        )

        return decision

    def _route_to_scheduling(self, message: str, context: ConversationContext) -> RoutingDecision:
        """Route to scheduling agent with property and timing context."""

        preserved_context = {
            "selected_property": context.selected_property,
            "user_preferences": context.user_preferences,
            "pending_appointment": context.pending_appointment,
            "from_agent": context.current_agent.value if context.current_agent else "router"
        }

        confidence = 0.95 if context.selected_property else 0.7

        decision = RoutingDecision(
            target_agent=AgentType.SCHEDULING,
            intent=Intent.SCHEDULING,
            confidence=confidence,
            reasoning="User wants to schedule property visit",
            context_to_preserve=preserved_context,
            handoff_trigger="scheduling_requested"
        )

        log_handoff(
            context.current_agent.value if context.current_agent else "router",
            "scheduling_agent",
            f"Scheduling intent: {message[:50]}..."
        )

        return decision

    def _route_by_context(self, message: str, context: ConversationContext) -> RoutingDecision:
        """
        Fallback routing based on conversation context when intent is unclear.

        Priority:
        1. If property selected → property_agent
        2. If search results available → property_agent
        3. Default → search_agent (start new search)
        """

        if context.selected_property:
            return RoutingDecision(
                target_agent=AgentType.PROPERTY,
                intent=Intent.PROPERTY_ANALYSIS,
                confidence=0.6,
                reasoning="Property selected, routing to property analysis",
                context_to_preserve={"selected_property": context.selected_property},
                handoff_trigger="context_based_routing"
            )

        if context.search_results and context.search_results.get("properties"):
            return RoutingDecision(
                target_agent=AgentType.PROPERTY,
                intent=Intent.PROPERTY_ANALYSIS,
                confidence=0.6,
                reasoning="Search results available, routing to property analysis",
                context_to_preserve={"search_results": context.search_results},
                handoff_trigger="context_based_routing"
            )

        # Default to search agent
        return RoutingDecision(
            target_agent=AgentType.SEARCH,
            intent=Intent.SEARCH,
            confidence=0.5,
            reasoning="No clear context, starting with search",
            context_to_preserve={},
            handoff_trigger="default_routing"
        )

    def _build_context_from_state(self, state: Dict[str, Any]) -> ConversationContext:
        """Build conversation context from LangGraph state."""

        context_dict = state.get("context", {})

        return ConversationContext(
            current_agent=AgentType(state.get("current_agent")) if state.get("current_agent") else None,
            previous_agent=AgentType(context_dict.get("from_agent")) if context_dict.get("from_agent") else None,
            search_results=state.get("search_results"),
            selected_property=context_dict.get("selected_property") or state.get("selected_property"),
            pending_appointment=state.get("pending_appointment"),
            user_preferences=context_dict.get("user_preferences", {}),
            conversation_history=self._extract_conversation_history(state),
            handoff_count=context_dict.get("handoff_count", 0)
        )

    def _extract_conversation_history(self, state: Dict[str, Any]) -> List[str]:
        """Extract conversation history from state messages."""
        messages = state.get("messages", [])
        return [msg.get("content", "") for msg in messages[-5:]]  # Last 5 messages

    def _extract_previous_searches(self, context: ConversationContext) -> List[Dict[str, Any]]:
        """Extract previous search criteria from context."""
        # TODO: Implement search history tracking
        return []

    def validate_handoff(
        self,
        from_agent: AgentType,
        to_agent: AgentType,
        context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if a handoff is appropriate given the context.

        Args:
            from_agent: Agent initiating handoff
            to_agent: Target agent
            context: Current context state

        Returns:
            Tuple of (is_valid, error_message)
        """

        # Scheduling requires property selection
        if to_agent == AgentType.SCHEDULING:
            if not context.get("selected_property"):
                return False, "Cannot schedule without property selection"

        # Prevent circular handoffs
        if context.get("handoff_count", 0) > 3:
            return False, "Too many handoffs, potential loop detected"

        # All other handoffs are valid
        return True, None

    def store_routing_decision(self, decision: RoutingDecision) -> None:
        """
        Store routing decision in memory for analysis.
        Uses hooks to store in claude-flow memory.
        """
        decision_data = {
            "target_agent": decision.target_agent.value,
            "intent": decision.intent.value,
            "confidence": decision.confidence,
            "reasoning": decision.reasoning,
            "trigger": decision.handoff_trigger,
            "timestamp": decision.timestamp.isoformat()
        }

        self.logger.info(f"Routing decision: {decision.target_agent.value} (confidence: {decision.confidence:.2f})")

        # Memory storage will be done via hooks in the execution layer
        # This is just logging for now


# Global router instance
_router = None

def get_router() -> IntelligentRouter:
    """Get or create the global router instance."""
    global _router
    if _router is None:
        _router = IntelligentRouter()
    return _router
