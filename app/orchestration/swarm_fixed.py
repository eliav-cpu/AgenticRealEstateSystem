"""
Fixed LangGraph-Swarm Implementation

This is a simplified, working implementation that avoids the tool validation issues
by using a cleaner integration between LangGraph-Swarm and PydanticAI.
"""

from typing import Dict, Any, List, Optional
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

from ..utils.logging import get_logger, log_performance
from ..utils.logfire_config import AgentExecutionContext
from ..utils.datetime_context import format_datetime_context_for_agent
from config.settings import get_settings
import time
import uuid
import asyncio


class FixedSwarmOrchestrator:
    """
    Fixed LangGraph-Swarm implementation that avoids tool validation issues.
    
    This approach uses LangGraph-Swarm for coordination but keeps PydanticAI 
    execution separate to avoid tool call conflicts.
    """
    
    def __init__(self):
        self.logger = get_logger("fixed_swarm")
        self.settings = get_settings()
        
        # Initialize memory components
        self.checkpointer = InMemorySaver()
        self.store = InMemoryStore()
        
        # Initialize ChatOpenAI model for LangGraph
        self.langchain_model = self._create_langchain_model()
        
        # Create PydanticAI agents separately
        self.pydantic_search = self._create_pydantic_search_agent()
        self.pydantic_property = self._create_pydantic_property_agent()
        self.pydantic_scheduling = self._create_pydantic_scheduling_agent()
        
        # Create LangGraph-Swarm agents
        self.search_agent = self._create_search_agent()
        self.property_agent = self._create_property_agent()
        self.scheduling_agent = self._create_scheduling_agent()
        
        # Create and compile the swarm
        self.swarm = self._create_swarm()
        
        self.logger.info("Fixed LangGraph-Swarm orchestrator initialized successfully")
    
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
            
            self.logger.info("ChatOpenAI model created for LangGraph")
            return model
            
        except Exception as e:
            self.logger.error(f"Failed to create ChatOpenAI model: {e}")
            raise
    
    def _create_pydantic_search_agent(self) -> PydanticAgent:
        """Create PydanticAI search agent."""
        try:
            api_key = self.settings.apis.openrouter_key
            provider = OpenRouterProvider(api_key=api_key)
            model = OpenAIModel("mistralai/mistral-7b-instruct:free", provider=provider)
            
            agent = PydanticAgent(
                model=model,
                system_prompt="""You are Alex, a professional real estate search specialist.

Your role is to help clients find properties that match their specific needs and budget. You provide clear, concise, and helpful property search assistance.

When users ask about property details like rent, pricing, or features:
- Provide direct, factual answers based on available property information
- Reference specific property details when available  
- Be conversational but professional
- Keep responses focused and relevant to the user's question

Always stay in character as a real estate search specialist focused on the property market."""
            )
            
            self.logger.info("PydanticAI search agent created")
            return agent
            
        except Exception as e:
            self.logger.error(f"Failed to create PydanticAI search agent: {e}")
            raise
    
    def _create_pydantic_property_agent(self) -> PydanticAgent:
        """Create PydanticAI property agent."""
        try:
            api_key = self.settings.apis.openrouter_key
            provider = OpenRouterProvider(api_key=api_key)
            model = OpenAIModel("mistralai/mistral-7b-instruct:free", provider=provider)
            
            agent = PydanticAgent(
                model=model,
                system_prompt="""You are Emma, a professional real estate property expert.

Your role is to provide detailed, accurate information about specific properties. You answer questions about rent prices, property features, neighborhood details, and investment potential.

When users ask about property details:
- Give direct, specific answers about rent, price, bedrooms, bathrooms, etc.
- Reference the actual property information when available
- Provide context about the neighborhood and market when relevant
- Be professional but conversational
- Keep responses focused on the user's specific question

Always provide factual, helpful property information. Never make up details about markets you don't have information about."""
            )
            
            self.logger.info("PydanticAI property agent created")
            return agent
            
        except Exception as e:
            self.logger.error(f"Failed to create PydanticAI property agent: {e}")
            raise
    
    def _create_pydantic_scheduling_agent(self) -> PydanticAgent:
        """Create PydanticAI scheduling agent."""
        try:
            api_key = self.settings.apis.openrouter_key
            provider = OpenRouterProvider(api_key=api_key)
            model = OpenAIModel("mistralai/mistral-7b-instruct:free", provider=provider)
            
            agent = PydanticAgent(
                model=model,
                system_prompt="""You are Mike, a professional scheduling assistant for real estate viewings.

Help clients schedule property visits efficiently. Provide clear scheduling information and handle appointment management."""
            )
            
            self.logger.info("PydanticAI scheduling agent created")
            return agent
            
        except Exception as e:
            self.logger.error(f"Failed to create PydanticAI scheduling agent: {e}")
            raise
    
    def _create_search_agent(self):
        """Create search agent for LangGraph-Swarm."""
        
        # Create handoff tools
        handoff_to_property = create_handoff_tool(
            agent_name="property_agent",
            description="Transfer to property analysis agent for detailed property information"
        )
        
        handoff_to_scheduling = create_handoff_tool(
            agent_name="scheduling_agent",
            description="Transfer to scheduling agent for property visit scheduling"
        )
        
        # Simple execution tool that calls PydanticAI
        @tool
        def handle_search_request(query: str) -> str:
            """Handle property search requests using PydanticAI."""
            try:
                # Add context
                datetime_context = format_datetime_context_for_agent()
                enhanced_query = f"""{datetime_context}

User request: {query}

Please provide helpful property search assistance."""
                
                # Execute synchronously to avoid async issues
                result = asyncio.run(self.pydantic_search.run(enhanced_query))
                response = str(result.output) if hasattr(result, 'output') else str(result)
                
                return f"Search Result: {response}"
                
            except Exception as e:
                self.logger.error(f"Search execution error: {e}")
                return "I'm here to help with property searches. What are you looking for?"
        
        # Create LangGraph agent with minimal tools
        agent = create_react_agent(
            self.langchain_model,
            [handle_search_request, handoff_to_property, handoff_to_scheduling],
            prompt="You help with property searches. Use handle_search_request for search queries, then decide if handoffs are needed based on user intent.",
            name="search_agent"
        )
        
        return agent
    
    def _create_property_agent(self):
        """Create property agent for LangGraph-Swarm."""
        
        # Create handoff tools
        handoff_to_search = create_handoff_tool(
            agent_name="search_agent",
            description="Transfer to search agent for finding different properties"
        )
        
        handoff_to_scheduling = create_handoff_tool(
            agent_name="scheduling_agent",
            description="Transfer to scheduling agent for property visit scheduling"
        )
        
        # Simple execution tool that calls PydanticAI
        @tool
        def handle_property_analysis(query: str) -> str:
            """Handle property analysis requests using PydanticAI."""
            try:
                # Add context
                datetime_context = format_datetime_context_for_agent()
                enhanced_query = f"""{datetime_context}

User request: {query}

You are Emma, a real estate property expert. The user is asking about property details. Provide a direct, helpful answer about the property. If they're asking about rent or price, give specific information if available. Keep your response focused and professional."""
                
                # Execute synchronously to avoid async issues
                result = asyncio.run(self.pydantic_property.run(enhanced_query))
                response = str(result.output) if hasattr(result, 'output') else str(result)
                
                return response  # Return direct response without "Property Analysis:" prefix
                
            except Exception as e:
                self.logger.error(f"Property analysis error: {e}")
                return "I'm Emma, your property expert. I'm here to help with property details and analysis. What would you like to know about this property?"
        
        # Create LangGraph agent with minimal tools
        agent = create_react_agent(
            self.langchain_model,
            [handle_property_analysis, handoff_to_search, handoff_to_scheduling],
            prompt="You are Emma, a property expert. For property questions, use handle_property_analysis to get detailed information. Provide direct, helpful answers about rent, features, and property details. Only use handoffs if the user specifically wants to search for different properties or schedule a visit.",
            name="property_agent"
        )
        
        return agent
    
    def _create_scheduling_agent(self):
        """Create scheduling agent for LangGraph-Swarm."""
        
        # Create handoff tools
        handoff_to_search = create_handoff_tool(
            agent_name="search_agent",
            description="Transfer to search agent for finding properties to schedule"
        )
        
        handoff_to_property = create_handoff_tool(
            agent_name="property_agent",
            description="Transfer to property agent for property details before scheduling"
        )
        
        # Simple execution tool that calls PydanticAI
        @tool
        def handle_scheduling_request(query: str) -> str:
            """Handle scheduling requests using PydanticAI."""
            try:
                # Add context with scheduling information
                from ..utils.datetime_context import get_scheduling_context_for_agent
                scheduling_context = get_scheduling_context_for_agent()
                enhanced_query = f"""{scheduling_context}

User request: {query}

Please provide helpful scheduling assistance."""
                
                # Execute synchronously to avoid async issues
                result = asyncio.run(self.pydantic_scheduling.run(enhanced_query))
                response = str(result.output) if hasattr(result, 'output') else str(result)
                
                return f"Scheduling Info: {response}"
                
            except Exception as e:
                self.logger.error(f"Scheduling error: {e}")
                return "I'm here to help with scheduling property visits. What would you like to schedule?"
        
        # Create LangGraph agent with minimal tools
        agent = create_react_agent(
            self.langchain_model,
            [handle_scheduling_request, handoff_to_search, handoff_to_property],
            prompt="You handle property visit scheduling. Use handle_scheduling_request for scheduling questions, then decide if handoffs are needed.",
            name="scheduling_agent"
        )
        
        return agent
    
    def _create_swarm(self):
        """Create the swarm using langgraph-swarm framework."""
        try:
            # Create the swarm with our agents
            workflow = create_swarm(
                [self.search_agent, self.property_agent, self.scheduling_agent],
                default_active_agent="property_agent"  # Start with property agent for property context
            )
            
            # Compile with memory components
            app = workflow.compile(
                checkpointer=self.checkpointer,
                store=self.store
            )
            
            self.logger.info("Fixed LangGraph-Swarm created and compiled")
            return app
            
        except Exception as e:
            self.logger.error(f"Failed to create fixed swarm: {e}")
            raise
    
    async def process_message(self, message: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process message through the fixed swarm."""
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
            
            self.logger.info(f"Processing message with Fixed Swarm (thread: {thread_id})")
            
            # Process through fixed swarm
            result = await self.swarm.ainvoke(message, config)
            
            execution_time = time.time() - start_time
            log_performance("fixed_swarm_processing", execution_time)
            
            self.logger.info(f"Fixed Swarm processing completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Fixed Swarm processing failed after {execution_time:.2f}s: {e}")
            raise
    
    async def stream_message(self, message: Dict[str, Any], config: Dict[str, Any] = None):
        """Stream message processing through the fixed swarm."""
        try:
            if not config:
                config = {
                    "configurable": {
                        "thread_id": f"session-{uuid.uuid4().hex[:8]}"
                    }
                }
            
            self.logger.info("Starting Fixed Swarm streaming")
            
            chunk_count = 0
            async for chunk in self.swarm.astream(message, config):
                chunk_count += 1
                yield chunk
            
            self.logger.info(f"Streaming completed with {chunk_count} chunks")
            
        except Exception as e:
            self.logger.error(f"Streaming error: {e}")
            yield {"error": str(e)}


# Global instance for singleton pattern
_fixed_swarm_orchestrator = None

def get_fixed_swarm_orchestrator() -> FixedSwarmOrchestrator:
    """Get singleton instance of the Fixed Swarm orchestrator."""
    global _fixed_swarm_orchestrator
    if _fixed_swarm_orchestrator is None:
        _fixed_swarm_orchestrator = FixedSwarmOrchestrator()
    return _fixed_swarm_orchestrator