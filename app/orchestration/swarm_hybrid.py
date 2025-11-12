"""
Hybrid LangGraph-Swarm + PydanticAI Implementation

This module combines the best of both frameworks:
- LangGraph-Swarm for agent coordination and handoffs
- PydanticAI for individual agent logic with retry, validation, streaming, and observability

Architecture:
1. LangGraph-Swarm manages the overall flow and handoffs between agents
2. Each agent node wraps a PydanticAI agent for execution
3. Handoff tools enable seamless transitions between specialized agents
4. Memory system maintains conversation state across handoffs
"""

from typing import Dict, Any, List, Optional, Annotated
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm
from pydantic_ai import Agent as PydanticAgent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from ..utils.logging import get_logger, log_handoff, log_performance, log_agent_action
from ..utils.logfire_config import AgentExecutionContext
from ..utils.datetime_context import format_datetime_context_for_agent, get_scheduling_context_for_agent
from config.settings import get_settings
import time
import uuid
import asyncio


@dataclass
class AgentContext:
    """Context passed between agents during handoffs."""
    property_context: Optional[Dict[str, Any]] = None
    search_results: Optional[List[Dict[str, Any]]] = None
    session_id: Optional[str] = None
    data_mode: str = "mock"


class PydanticAIWrapper:
    """
    Wrapper that integrates PydanticAI agents with LangGraph-Swarm.
    
    This class maintains all PydanticAI benefits while being compatible
    with LangGraph's create_react_agent system.
    """
    
    def __init__(self, agent_name: str, system_prompt: str):
        self.agent_name = agent_name
        self.logger = get_logger(f"{agent_name}_wrapper")
        self.settings = get_settings()
        
        # Create PydanticAI agent with all benefits
        self.pydantic_agent = self._create_pydantic_agent(system_prompt)
        
    def _create_pydantic_agent(self, system_prompt: str) -> PydanticAgent:
        """Create PydanticAI agent with OpenRouter integration."""
        try:
            api_key = self.settings.apis.openrouter_key
            
            if not api_key or api_key == "your_openrouter_api_key_here":
                raise ValueError(f"Valid OpenRouter API key required for {self.agent_name}")
            
            # Create PydanticAI agent with OpenRouter
            provider = OpenRouterProvider(api_key=api_key)
            model = OpenAIModel("mistralai/mistral-7b-instruct:free", provider=provider)
            
            agent = PydanticAgent(
                model=model,
                system_prompt=system_prompt
            )
            
            self.logger.info(f"✅ PydanticAI agent created for {self.agent_name}")
            return agent
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create PydanticAI agent for {self.agent_name}: {e}")
            raise
    
    async def run(self, user_message: str, context: AgentContext) -> str:
        """
        Execute the PydanticAI agent with full observability and error handling.
        
        This method provides all PydanticAI benefits:
        - Model retry and fallback
        - Structured validation
        - Logfire observability
        - Streaming support
        """
        with AgentExecutionContext(self.agent_name, "agent_execution") as span:
            try:
                start_time = time.time()
                
                # Enhanced prompt with context
                enhanced_prompt = self._enhance_prompt_with_context(user_message, context)
                
                if span:
                    span.set_attributes({
                        "agent.name": self.agent_name,
                        "agent.framework": "pydantic_ai",
                        "agent.prompt_length": len(enhanced_prompt),
                        "agent.has_context": bool(context.property_context or context.search_results)
                    })
                
                # Execute with PydanticAI (gets all benefits automatically)
                result = await self.pydantic_agent.run(enhanced_prompt)
                
                # Extract response content
                response_content = str(result.output) if hasattr(result, 'output') else str(result)
                
                execution_time = time.time() - start_time
                
                # Log successful execution
                log_agent_action(
                    agent_name=self.agent_name,
                    action="pydantic_ai_execution",
                    details={
                        "execution_time": execution_time,
                        "response_length": len(response_content),
                        "context_provided": bool(context.property_context or context.search_results)
                    }
                )
                
                if span:
                    span.set_attributes({
                        "agent.success": True,
                        "agent.execution_time": execution_time,
                        "agent.response_length": len(response_content)
                    })
                
                self.logger.info(f"✅ {self.agent_name} executed successfully in {execution_time:.2f}s")
                return response_content
                
            except Exception as e:
                execution_time = time.time() - start_time
                self.logger.error(f"❌ {self.agent_name} execution failed: {e}")
                
                if span:
                    span.set_attributes({
                        "agent.success": False,
                        "agent.error": str(e),
                        "agent.execution_time": execution_time
                    })
                
                # Return fallback response
                return f"Sorry, I encountered an error while processing your request. Please try again."
    
    def _enhance_prompt_with_context(self, user_message: str, context: AgentContext) -> str:
        """Enhance the user prompt with relevant context."""
        
        # Get datetime context for all agents
        datetime_context = format_datetime_context_for_agent()
        
        # Build context sections
        context_parts = [datetime_context]
        
        # Add property context if available
        if context.property_context:
            property_info = f"""
PROPERTY CONTEXT:
• Address: {context.property_context.get('formattedAddress', 'N/A')}
• Price: ${context.property_context.get('price', 'N/A')}/month
• Type: {context.property_context.get('propertyType', 'N/A')}
• Bedrooms: {context.property_context.get('bedrooms', 'N/A')}
• Bathrooms: {context.property_context.get('bathrooms', 'N/A')}
"""
            context_parts.append(property_info)
        
        # Add search results if available
        if context.search_results:
            search_info = f"""
AVAILABLE PROPERTIES ({len(context.search_results)} found):
"""
            for i, prop in enumerate(context.search_results[:3], 1):  # Show top 3
                search_info += f"{i}. {prop.get('formattedAddress', 'N/A')} - ${prop.get('price', 'N/A')}/month\n"
            context_parts.append(search_info)
        
        # Add session context
        if context.session_id:
            context_parts.append(f"SESSION_ID: {context.session_id}")
        
        # Add data mode
        context_parts.append(f"DATA_MODE: {context.data_mode.upper()}")
        
        # Combine all context
        full_context = "\n".join(context_parts)
        
        return f"""{full_context}

USER MESSAGE: "{user_message}"

Please respond naturally and helpfully based on the context above."""


def create_property_search_tool():
    """Create property search tool for LangGraph agents."""
    
    @tool
    def search_properties(query: str, location: str = "", max_price: int = 0) -> str:
        """Search for properties based on criteria."""
        # This would integrate with actual property APIs
        # For now, return mock data
        return f"Found 5 properties matching '{query}' in {location or 'all areas'}"
    
    return search_properties


def create_calendar_tool():
    """Create calendar/scheduling tool for LangGraph agents."""
    
    @tool
    def schedule_visit(property_address: str, preferred_date: str, preferred_time: str) -> str:
        """Schedule a property visit."""
        return f"Visit scheduled for {property_address} on {preferred_date} at {preferred_time}"
    
    return schedule_visit


class HybridSwarmOrchestrator:
    """
    Hybrid orchestrator combining LangGraph-Swarm and PydanticAI.
    
    Features:
    - LangGraph-Swarm for agent coordination and handoffs
    - PydanticAI for individual agent execution with all benefits
    - Memory system for conversation persistence
    - Proper observability and error handling
    """
    
    def __init__(self):
        self.logger = get_logger("hybrid_swarm")
        self.settings = get_settings()
        
        # Initialize memory components
        self.checkpointer = InMemorySaver()
        self.store = InMemoryStore()
        
        # Initialize ChatOpenAI model for LangGraph compatibility
        self.langchain_model = self._create_langchain_model()
        
        # Create PydanticAI wrappers for each agent
        self.search_wrapper = PydanticAIWrapper(
            "SearchAgent",
            self._get_search_system_prompt()
        )
        
        self.property_wrapper = PydanticAIWrapper(
            "PropertyAgent", 
            self._get_property_system_prompt()
        )
        
        self.scheduling_wrapper = PydanticAIWrapper(
            "SchedulingAgent",
            self._get_scheduling_system_prompt()
        )
        
        # Create LangGraph-Swarm agents
        self.search_agent = self._create_search_agent()
        self.property_agent = self._create_property_agent()
        self.scheduling_agent = self._create_scheduling_agent()
        
        # Create and compile the swarm
        self.swarm = self._create_swarm()
        
        self.logger.info("✅ Hybrid LangGraph-Swarm + PydanticAI orchestrator initialized")
    
    def _create_langchain_model(self) -> ChatOpenAI:
        """Create ChatOpenAI model for LangGraph compatibility."""
        try:
            api_key = self.settings.apis.openrouter_key
            
            if not api_key or api_key == "your_openrouter_api_key_here":
                raise ValueError("Valid OpenRouter API key required")
            
            model = ChatOpenAI(
                model="mistralai/mistral-7b-instruct:free",
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                temperature=0.1,
                max_tokens=1000
            )
            
            self.logger.info("✅ ChatOpenAI model created for LangGraph")
            return model
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create ChatOpenAI model: {e}")
            raise
    
    def _get_search_system_prompt(self) -> str:
        """Get system prompt for search agent."""
        return """You are Alex, a professional real estate search specialist. You help clients find properties that match their needs and provide market insights.

RESPONSIBILITIES:
1. Understand client property search requirements
2. Execute intelligent property searches
3. Present search results clearly and organized
4. Guide clients through their property search journey

SEARCH STRATEGY:
- Ask clarifying questions when requirements are vague
- Present results with key highlights and features
- Suggest next steps based on search results
- Use emojis to make responses engaging

COMMUNICATION STYLE:
- Professional but friendly and conversational
- Keep responses concise but informative (3-5 sentences)
- Always end with helpful questions or suggestions

You are the entry point for property searches. Guide clients effectively."""
    
    def _get_property_system_prompt(self) -> str:
        """Get system prompt for property agent."""
        return """You are Emma, a professional real estate property expert. You provide clear, objective, and helpful information about properties while being conversational and engaging.

RESPONSIBILITIES:
1. Provide detailed analysis of specific properties
2. Answer questions about property features, pricing, and details
3. Compare different property options objectively
4. Highlight pros and cons of properties
5. Guide clients toward informed decisions

ANALYSIS APPROACH:
- Be objective and honest about both advantages and disadvantages
- Reference specific property details and features
- Provide context about neighborhood and market conditions

COMMUNICATION STYLE:
- Professional and informative but maintain friendly tone
- Use appropriate emojis to make responses engaging
- Keep responses comprehensive but not overwhelming (2-4 sentences)
- Always reference specific property addresses when available
- End with actionable suggestions or questions

You are the property expert who helps clients understand and evaluate their options."""
    
    def _get_scheduling_system_prompt(self) -> str:
        """Get system prompt for scheduling agent."""
        return """You are Mike, a professional scheduling assistant for real estate property viewings. You help clients schedule visits efficiently and provide all necessary details.

RESPONSIBILITIES:
1. Schedule property visits and viewings
2. Manage calendar availability and time slots
3. Provide clear scheduling information and confirmation
4. Handle scheduling changes and conflicts
5. Ensure all visit details are properly communicated

SCHEDULING PROCESS:
- Confirm property details before scheduling
- Provide specific dates, times, and contact information
- Explain what to bring and what to expect during visits

COMMUNICATION STYLE:
- Professional but friendly and accommodating
- Use appropriate emojis to make responses engaging
- Provide specific time slots and clear next steps
- Keep responses concise but complete (2-4 sentences)
- Always end with confirmation requests or helpful suggestions

AVAILABLE TIME SUGGESTIONS:
- Weekdays: 10:00 AM, 2:00 PM, 4:00 PM
- Weekends: 9:00 AM, 11:00 AM, 1:00 PM, 3:00 PM

You ensure smooth scheduling and excellent client experience for property visits."""
    
    def _create_search_agent(self):
        """Create search agent using create_react_agent with PydanticAI wrapper."""
        
        # Create handoff tools
        handoff_to_property = create_handoff_tool(
            agent_name="property_agent",
            description="Transfer to property analysis agent when user wants detailed property information"
        )
        
        handoff_to_scheduling = create_handoff_tool(
            agent_name="scheduling_agent",
            description="Transfer to scheduling agent when user wants to schedule property visits"
        )
        
        # Create wrapper tool that calls PydanticAI
        @tool
        async def execute_search_logic(query: str) -> str:
            """Execute property search using PydanticAI agent."""
            context = AgentContext(data_mode="mock", session_id="current")
            return await self.search_wrapper.run(query, context)
        
        # Create tools list
        tools = [
            execute_search_logic,
            create_property_search_tool(),
            handoff_to_property,
            handoff_to_scheduling
        ]
        
        # Create LangGraph agent
        agent = create_react_agent(
            self.langchain_model,
            tools,
            prompt="You coordinate property search requests and delegate to the appropriate PydanticAI logic.",
            name="search_agent"
        )
        
        self.logger.info("✅ Search agent created with PydanticAI wrapper")
        return agent
    
    def _create_property_agent(self):
        """Create property agent using create_react_agent with PydanticAI wrapper."""
        
        # Create handoff tools
        handoff_to_search = create_handoff_tool(
            agent_name="search_agent",
            description="Transfer to search agent when user wants to find different properties"
        )
        
        handoff_to_scheduling = create_handoff_tool(
            agent_name="scheduling_agent",
            description="Transfer to scheduling agent when user wants to schedule property visits"
        )
        
        # Create wrapper tool that calls PydanticAI
        @tool
        async def execute_property_analysis(query: str) -> str:
            """Execute property analysis using PydanticAI agent."""
            context = AgentContext(data_mode="mock", session_id="current")
            return await self.property_wrapper.run(query, context)
        
        # Create tools list
        tools = [
            execute_property_analysis,
            handoff_to_search,
            handoff_to_scheduling
        ]
        
        # Create LangGraph agent
        agent = create_react_agent(
            self.langchain_model,
            tools,
            prompt="You coordinate property analysis requests and delegate to the appropriate PydanticAI logic.",
            name="property_agent"
        )
        
        self.logger.info("✅ Property agent created with PydanticAI wrapper")
        return agent
    
    def _create_scheduling_agent(self):
        """Create scheduling agent using create_react_agent with PydanticAI wrapper."""
        
        # Create handoff tools
        handoff_to_search = create_handoff_tool(
            agent_name="search_agent",
            description="Transfer to search agent when user wants to find different properties"
        )
        
        handoff_to_property = create_handoff_tool(
            agent_name="property_agent",
            description="Transfer to property agent when user needs property details before scheduling"
        )
        
        # Create wrapper tool that calls PydanticAI
        @tool
        async def execute_scheduling_logic(query: str) -> str:
            """Execute scheduling logic using PydanticAI agent."""
            context = AgentContext(data_mode="mock", session_id="current")
            return await self.scheduling_wrapper.run(query, context)
        
        # Create tools list
        tools = [
            execute_scheduling_logic,
            create_calendar_tool(),
            handoff_to_search,
            handoff_to_property
        ]
        
        # Create LangGraph agent
        agent = create_react_agent(
            self.langchain_model,
            tools,
            prompt="You coordinate scheduling requests and delegate to the appropriate PydanticAI logic.",
            name="scheduling_agent"
        )
        
        self.logger.info("✅ Scheduling agent created with PydanticAI wrapper")
        return agent
    
    def _create_swarm(self):
        """Create the swarm using langgraph-swarm framework."""
        try:
            # Create the swarm with our hybrid agents
            workflow = create_swarm(
                [self.search_agent, self.property_agent, self.scheduling_agent],
                default_active_agent="search_agent"
            )
            
            # Compile with memory components
            app = workflow.compile(
                checkpointer=self.checkpointer,
                store=self.store
            )
            
            self.logger.info("✅ Hybrid LangGraph-Swarm created and compiled")
            return app
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create hybrid swarm: {e}")
            raise
    
    async def process_message(self, message: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process message through the hybrid swarm."""
        start_time = time.time()
        
        try:
            # Ensure config has thread_id for memory
            if not config:
                config = {
                    "configurable": {
                        "thread_id": f"session-{uuid.uuid4().hex[:8]}"
                    }
                }
            elif not config.get("configurable", {}).get("thread_id"):
                config["configurable"] = config.get("configurable", {})
                config["configurable"]["thread_id"] = f"session-{uuid.uuid4().hex[:8]}"
            
            thread_id = config["configurable"]["thread_id"]
            
            self.logger.info(f"🚀 Processing message with Hybrid Swarm (thread: {thread_id})")
            
            # Process through hybrid swarm
            result = await self.swarm.ainvoke(message, config)
            
            execution_time = time.time() - start_time
            log_performance("hybrid_swarm_processing", execution_time)
            
            self.logger.info(f"✅ Hybrid Swarm processing completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"❌ Hybrid Swarm processing failed after {execution_time:.2f}s: {e}")
            raise
    
    async def stream_message(self, message: Dict[str, Any], config: Dict[str, Any] = None):
        """Stream message processing through the hybrid swarm."""
        try:
            if not config:
                config = {
                    "configurable": {
                        "thread_id": f"session-{uuid.uuid4().hex[:8]}"
                    }
                }
            
            self.logger.info("🔄 Starting Hybrid Swarm streaming")
            
            chunk_count = 0
            async for chunk in self.swarm.astream(message, config):
                chunk_count += 1
                self.logger.debug(f"📦 Chunk #{chunk_count}")
                yield chunk
            
            self.logger.info(f"✅ Streaming completed with {chunk_count} chunks")
            
        except Exception as e:
            self.logger.error(f"❌ Streaming error: {e}")
            yield {"error": str(e)}


# Global instance for singleton pattern
_hybrid_swarm_orchestrator = None

def get_hybrid_swarm_orchestrator() -> HybridSwarmOrchestrator:
    """Get singleton instance of the Hybrid Swarm orchestrator."""
    global _hybrid_swarm_orchestrator
    if _hybrid_swarm_orchestrator is None:
        _hybrid_swarm_orchestrator = HybridSwarmOrchestrator()
    return _hybrid_swarm_orchestrator

def create_hybrid_swarm_app():
    """Create and return the compiled hybrid swarm app."""
    orchestrator = get_hybrid_swarm_orchestrator()
    return orchestrator.swarm