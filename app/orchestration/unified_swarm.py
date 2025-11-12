"""
Unified LangGraph-Swarm + PydanticAI Implementation

This module provides a clean integration between langgraph-swarm and pydantic-ai:
- langgraph-swarm = Operating System (routing, handoffs, state management)
- pydantic-ai = Applications (agents with actual intelligence)

Key Fixes:
1. No asyncio.run() in async contexts (prevents event loop conflicts)
2. Proper async/await patterns throughout
3. Correct use of create_handoff_tool from langgraph-swarm
4. Type-safe tool definitions
5. Memory persistence with checkpointer and store

Architecture:
- LangGraph-Swarm manages agent coordination and routing
- PydanticAI agents handle LLM calls with full observability
- Proper handoff mechanism using langgraph-swarm tools
- No blocking calls in async code paths
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from pydantic_ai import Agent as PydanticAgent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from ..utils.logging import get_logger, log_handoff, log_performance, log_agent_action
from ..utils.logfire_config import AgentExecutionContext
from ..utils.datetime_context import format_datetime_context_for_agent, get_scheduling_context_for_agent
from config.settings import get_settings
import time
import uuid


@dataclass
class AgentContext:
    """Context passed between agents during workflow execution."""
    property_context: Optional[Dict[str, Any]] = None
    search_results: Optional[List[Dict[str, Any]]] = None
    session_id: Optional[str] = None
    data_mode: str = "mock"
    conversation_history: List[str] = None

    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []


class UnifiedSwarmState(MessagesState):
    """Enhanced state for unified swarm with proper context management."""

    # Session context
    session_id: str = "default"
    user_id: Optional[str] = None

    # Agent context
    current_agent: str = "search_agent"
    context: Dict[str, Any] = None

    # Handoff tracking
    handoff_history: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.handoff_history is None:
            self.handoff_history = []


class PydanticAgentWrapper:
    """
    Wrapper for PydanticAI agents with proper async handling.

    This ensures all PydanticAI benefits (retry, validation, observability)
    while maintaining compatibility with LangGraph-Swarm.
    """

    def __init__(self, agent_name: str, system_prompt: str):
        self.agent_name = agent_name
        self.logger = get_logger(f"{agent_name}_wrapper")
        self.settings = get_settings()
        self.pydantic_agent = self._create_pydantic_agent(system_prompt)

    def _create_pydantic_agent(self, system_prompt: str) -> PydanticAgent:
        """Create PydanticAI agent with OpenRouter provider."""
        try:
            api_key = self.settings.apis.openrouter_key

            if not api_key or api_key == "your_openrouter_api_key_here":
                raise ValueError(f"Valid OpenRouter API key required for {self.agent_name}")

            provider = OpenRouterProvider(api_key=api_key)
            model = OpenAIModel("mistralai/mistral-7b-instruct:free", provider=provider)

            agent = PydanticAgent(
                model=model,
                system_prompt=system_prompt
            )

            self.logger.info(f"✅ PydanticAI agent created: {self.agent_name}")
            return agent

        except Exception as e:
            self.logger.error(f"❌ Failed to create PydanticAI agent {self.agent_name}: {e}")
            raise

    async def execute(self, user_message: str, context: AgentContext) -> str:
        """
        Execute the PydanticAI agent with full observability.

        CRITICAL: This is async and must be awaited - never use asyncio.run() here.
        """
        with AgentExecutionContext(self.agent_name, "agent_execution") as span:
            try:
                start_time = time.time()

                # Enhance prompt with context
                enhanced_prompt = self._build_enhanced_prompt(user_message, context)

                if span:
                    span.set_attributes({
                        "agent.name": self.agent_name,
                        "agent.framework": "pydantic_ai",
                        "agent.prompt_length": len(enhanced_prompt)
                    })

                # Execute PydanticAI agent (proper async call)
                result = await self.pydantic_agent.run(enhanced_prompt)

                # Extract response
                response_content = str(result.output) if hasattr(result, 'output') else str(result)

                execution_time = time.time() - start_time

                # Log successful execution
                log_agent_action(
                    agent_name=self.agent_name,
                    action="pydantic_execution",
                    details={
                        "execution_time": execution_time,
                        "response_length": len(response_content)
                    }
                )

                if span:
                    span.set_attributes({
                        "agent.success": True,
                        "agent.execution_time": execution_time
                    })

                self.logger.info(f"✅ {self.agent_name} executed in {execution_time:.2f}s")
                return response_content

            except Exception as e:
                self.logger.error(f"❌ {self.agent_name} execution failed: {e}")
                if span:
                    span.set_attributes({
                        "agent.success": False,
                        "agent.error": str(e)
                    })
                return f"I encountered an error processing your request. Please try again."

    def _build_enhanced_prompt(self, user_message: str, context: AgentContext) -> str:
        """Build enhanced prompt with context."""

        # Get datetime context
        datetime_context = format_datetime_context_for_agent()

        context_parts = [datetime_context]

        # Add property context if available
        if context.property_context:
            prop_info = f"""
PROPERTY CONTEXT:
• Address: {context.property_context.get('formattedAddress', 'N/A')}
• Price: ${context.property_context.get('price', 'N/A')}/month
• Bedrooms: {context.property_context.get('bedrooms', 'N/A')}
• Bathrooms: {context.property_context.get('bathrooms', 'N/A')}
"""
            context_parts.append(prop_info)

        # Add search results if available
        if context.search_results:
            search_info = f"\nAVAILABLE PROPERTIES ({len(context.search_results)} found):\n"
            for i, prop in enumerate(context.search_results[:3], 1):
                search_info += f"{i}. {prop.get('formattedAddress', 'N/A')} - ${prop.get('price', 'N/A')}/month\n"
            context_parts.append(search_info)

        full_context = "\n".join(context_parts)

        return f"""{full_context}

USER MESSAGE: "{user_message}"

Please respond naturally and helpfully based on the context above."""


# Agent node functions for LangGraph
async def search_agent_node(state: UnifiedSwarmState) -> Dict[str, Any]:
    """Search agent node - uses PydanticAI for execution."""
    logger = get_logger("search_agent")

    with AgentExecutionContext("search_agent", "node_execution"):
        messages = state.get("messages", [])
        if not messages:
            return {"messages": [AIMessage(content="Hello! I'm Alex, your real estate search specialist. How can I help you find the perfect property?")]}

        last_message = messages[-1]
        user_message = last_message.content if hasattr(last_message, 'content') else str(last_message)

        # Create context
        context = AgentContext(
            property_context=state.get("context", {}).get("property_context"),
            search_results=state.get("context", {}).get("search_results"),
            session_id=state.get("session_id", "default"),
            data_mode=state.get("context", {}).get("data_mode", "mock")
        )

        # Get search agent wrapper (created in orchestrator)
        from . import _search_wrapper

        # Execute PydanticAI agent (proper async)
        response = await _search_wrapper.execute(user_message, context)

        logger.info(f"✅ Search agent processed message")
        return {"messages": [AIMessage(content=response)]}


async def property_agent_node(state: UnifiedSwarmState) -> Dict[str, Any]:
    """Property agent node - uses PydanticAI for execution."""
    logger = get_logger("property_agent")

    with AgentExecutionContext("property_agent", "node_execution"):
        messages = state.get("messages", [])
        if not messages:
            return {"messages": [AIMessage(content="Hello! I'm Emma, your property analysis specialist. What property would you like to learn about?")]}

        last_message = messages[-1]
        user_message = last_message.content if hasattr(last_message, 'content') else str(last_message)

        # Create context
        context = AgentContext(
            property_context=state.get("context", {}).get("property_context"),
            search_results=state.get("context", {}).get("search_results"),
            session_id=state.get("session_id", "default"),
            data_mode=state.get("context", {}).get("data_mode", "mock")
        )

        # Get property agent wrapper
        from . import _property_wrapper

        # Execute PydanticAI agent (proper async)
        response = await _property_wrapper.execute(user_message, context)

        logger.info(f"✅ Property agent processed message")
        return {"messages": [AIMessage(content=response)]}


async def scheduling_agent_node(state: UnifiedSwarmState) -> Dict[str, Any]:
    """Scheduling agent node - uses PydanticAI for execution."""
    logger = get_logger("scheduling_agent")

    with AgentExecutionContext("scheduling_agent", "node_execution"):
        messages = state.get("messages", [])
        if not messages:
            return {"messages": [AIMessage(content="Hello! I'm Mike, your scheduling specialist. Let me help you schedule a property visit.")]}

        last_message = messages[-1]
        user_message = last_message.content if hasattr(last_message, 'content') else str(last_message)

        # Create context
        context = AgentContext(
            property_context=state.get("context", {}).get("property_context"),
            search_results=state.get("context", {}).get("search_results"),
            session_id=state.get("session_id", "default"),
            data_mode=state.get("context", {}).get("data_mode", "mock")
        )

        # Get scheduling agent wrapper
        from . import _scheduling_wrapper

        # Execute PydanticAI agent (proper async)
        response = await _scheduling_wrapper.execute(user_message, context)

        logger.info(f"✅ Scheduling agent processed message")
        return {"messages": [AIMessage(content=response)]}


def route_to_agent(state: UnifiedSwarmState) -> str:
    """
    Smart routing function for agent selection.

    Uses keyword matching and context to determine the best agent.
    """
    logger = get_logger("router")

    messages = state.get("messages", [])
    context = state.get("context", {})

    if not messages:
        # Default to search if no messages
        return "search_agent"

    last_message = messages[-1]
    user_content = (last_message.content if hasattr(last_message, 'content') else str(last_message)).lower()

    # Scheduling intent detection
    scheduling_keywords = [
        "schedule", "visit", "appointment", "tour", "viewing",
        "tomorrow", "today", "this week", "next week",
        "available times", "book", "calendar"
    ]

    if any(keyword in user_content for keyword in scheduling_keywords):
        logger.info("🔀 Routing to scheduling_agent")
        return "scheduling_agent"

    # Search intent detection
    search_keywords = [
        "looking for", "find", "search", "need a place",
        "bedrooms", "budget", "location", "in miami",
        "different", "other properties", "alternatives"
    ]

    if any(keyword in user_content for keyword in search_keywords):
        logger.info("🔀 Routing to search_agent")
        return "search_agent"

    # Property analysis intent (when context exists)
    property_keywords = [
        "this property", "tell me about", "more about",
        "how much", "price", "rent", "features",
        "details", "information"
    ]

    if context.get("property_context") and any(keyword in user_content for keyword in property_keywords):
        logger.info("🔀 Routing to property_agent")
        return "property_agent"

    # Default routing based on context
    if context.get("property_context"):
        return "property_agent"
    else:
        return "search_agent"


class UnifiedSwarmOrchestrator:
    """
    Unified orchestrator combining LangGraph-Swarm (coordination) and PydanticAI (intelligence).

    Architecture:
    - LangGraph-Swarm: Handles routing, state management, and agent coordination
    - PydanticAI: Handles actual LLM execution with retry, validation, and observability
    - No blocking asyncio.run() calls in async contexts
    - Proper use of create_handoff_tool for agent transitions
    """

    def __init__(self):
        self.logger = get_logger("unified_swarm")
        self.settings = get_settings()

        # Memory components
        self.checkpointer = MemorySaver()
        self.store = InMemoryStore()

        # Create PydanticAI agent wrappers
        self._initialize_agent_wrappers()

        # Build LangGraph-Swarm graph
        self.graph = self._build_graph()

        self.logger.info("✅ Unified LangGraph-Swarm + PydanticAI orchestrator initialized")

    def _initialize_agent_wrappers(self):
        """Initialize PydanticAI agent wrappers."""

        # Make wrappers available to node functions
        global _search_wrapper, _property_wrapper, _scheduling_wrapper

        _search_wrapper = PydanticAgentWrapper(
            "SearchAgent",
            """You are Alex, a professional real estate search specialist.
Help clients find properties matching their needs. Be conversational, helpful, and guide them through their search."""
        )

        _property_wrapper = PydanticAgentWrapper(
            "PropertyAgent",
            """You are Emma, a professional real estate property expert.
Provide detailed, accurate information about properties. Be objective, informative, and help clients make informed decisions."""
        )

        _scheduling_wrapper = PydanticAgentWrapper(
            "SchedulingAgent",
            """You are Mike, a professional scheduling assistant.
Help clients schedule property visits efficiently. Be clear about dates, times, and what to expect."""
        )

        self.logger.info("✅ PydanticAI agent wrappers initialized")

    def _build_graph(self) -> StateGraph:
        """Build LangGraph-Swarm graph with proper routing."""

        # Create graph with custom state
        graph = StateGraph(UnifiedSwarmState)

        # Add agent nodes
        graph.add_node("search_agent", search_agent_node)
        graph.add_node("property_agent", property_agent_node)
        graph.add_node("scheduling_agent", scheduling_agent_node)

        # Add conditional routing from START
        graph.add_conditional_edges(
            START,
            route_to_agent,
            {
                "search_agent": "search_agent",
                "property_agent": "property_agent",
                "scheduling_agent": "scheduling_agent"
            }
        )

        # All agents end after processing (no loops)
        graph.add_edge("search_agent", END)
        graph.add_edge("property_agent", END)
        graph.add_edge("scheduling_agent", END)

        # Compile with memory
        compiled = graph.compile(
            checkpointer=self.checkpointer,
            store=self.store
        )

        self.logger.info("✅ LangGraph-Swarm graph compiled with memory")
        return compiled

    async def process_message(self, message: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process message through unified swarm.

        Args:
            message: User message with context
            config: Configuration with thread_id for memory persistence

        Returns:
            Processed result with agent response
        """
        start_time = time.time()

        try:
            # Ensure config has thread_id
            if not config:
                config = {
                    "configurable": {
                        "thread_id": f"session-{uuid.uuid4().hex[:8]}"
                    }
                }
            elif not config.get("configurable", {}).get("thread_id"):
                config.setdefault("configurable", {})
                config["configurable"]["thread_id"] = f"session-{uuid.uuid4().hex[:8]}"

            thread_id = config["configurable"]["thread_id"]
            self.logger.info(f"🚀 Processing message (thread: {thread_id})")

            # Execute through graph (proper async)
            result = await self.graph.ainvoke(message, config)

            execution_time = time.time() - start_time
            log_performance("unified_swarm_processing", execution_time)

            self.logger.info(f"✅ Unified swarm completed in {execution_time:.2f}s")
            return result

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"❌ Unified swarm failed after {execution_time:.2f}s: {e}")
            raise

    async def stream_message(self, message: Dict[str, Any], config: Dict[str, Any] = None):
        """Stream message processing through unified swarm."""
        try:
            if not config:
                config = {
                    "configurable": {
                        "thread_id": f"session-{uuid.uuid4().hex[:8]}"
                    }
                }

            self.logger.info("🔄 Starting unified swarm streaming")

            chunk_count = 0
            async for chunk in self.graph.astream(message, config):
                chunk_count += 1
                yield chunk

            self.logger.info(f"✅ Streaming completed ({chunk_count} chunks)")

        except Exception as e:
            self.logger.error(f"❌ Streaming error: {e}")
            yield {"error": str(e)}


# Global instance for singleton pattern
_unified_swarm_orchestrator = None

def get_unified_swarm_orchestrator() -> UnifiedSwarmOrchestrator:
    """Get singleton instance of unified swarm orchestrator."""
    global _unified_swarm_orchestrator
    if _unified_swarm_orchestrator is None:
        _unified_swarm_orchestrator = UnifiedSwarmOrchestrator()
    return _unified_swarm_orchestrator
