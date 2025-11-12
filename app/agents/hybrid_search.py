"""
Hybrid Search Agent - LangGraph-Swarm + PydanticAI

This agent combines:
- LangGraph-Swarm for handoffs and coordination
- PydanticAI for execution with retry, validation, streaming, and observability
"""

from typing import Dict, Any, List, Optional, Annotated
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool
from pydantic_ai import Agent as PydanticAgent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic import BaseModel

from ..utils.logging import get_logger, log_agent_action
from ..utils.logfire_config import AgentExecutionContext
from ..utils.datetime_context import format_datetime_context_for_agent
from config.settings import get_settings
import time
import asyncio


class SearchResult(BaseModel):
    """Structured output for search results."""
    properties_found: int
    summary: str
    recommendations: List[str]
    next_actions: List[str]


class HybridSearchAgent:
    """
    Search agent that combines LangGraph-Swarm coordination with PydanticAI execution.
    
    Benefits from PydanticAI:
    - Model retry and fallback
    - Input/output validation  
    - Dependency injection
    - Streaming responses
    - Native observability via Logfire
    """
    
    def __init__(self, langchain_model):
        self.agent_name = "SearchAgent"
        self.logger = get_logger("hybrid_search")
        self.settings = get_settings()
        self.langchain_model = langchain_model
        
        # Create PydanticAI agent with full benefits
        self.pydantic_agent = self._create_pydantic_agent()
        
        # Create LangGraph agent with handoff tools
        self.langgraph_agent = self._create_langgraph_agent()
        
    def _create_pydantic_agent(self) -> PydanticAgent:
        """Create PydanticAI agent with OpenRouter and full observability."""
        try:
            api_key = self.settings.apis.openrouter_key
            
            if not api_key or api_key == "your_openrouter_api_key_here":
                raise ValueError("Valid OpenRouter API key required for SearchAgent")
            
            # Create PydanticAI agent with structured output
            provider = OpenRouterProvider(api_key=api_key)
            model = OpenAIModel("mistralai/mistral-7b-instruct:free", provider=provider)
            
            agent = PydanticAgent(
                model=model,
                result_type=SearchResult,
                system_prompt=self._get_system_prompt()
            )
            
            # Add tools to PydanticAI agent
            self._add_pydantic_tools(agent)
            
            self.logger.info("✅ PydanticAI search agent created with structured output")
            return agent
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create PydanticAI search agent: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Get comprehensive system prompt for search agent."""
        return """You are Alex, a professional real estate search specialist with advanced AI capabilities.

CORE RESPONSIBILITIES:
1. Understand and interpret property search requirements
2. Execute intelligent property searches with filtering
3. Present results in structured, actionable format
4. Guide clients through their property search journey
5. Make smart decisions about when to transfer to other specialists

SEARCH CAPABILITIES:
- Parse natural language search criteria
- Filter by location, price range, property type, features
- Rank results by relevance and user preferences
- Identify when searches need refinement
- Suggest alternative search strategies

COMMUNICATION STYLE:
- Professional but warm and conversational
- Use emojis strategically for engagement
- Provide clear, structured responses
- Always include actionable next steps
- Ask clarifying questions when needed

OUTPUT REQUIREMENTS:
- Always return structured SearchResult format
- Include specific property counts and summaries
- Provide 2-3 concrete recommendations
- List 2-3 clear next action options

HANDOFF DECISIONS:
- Transfer to PropertyAgent when: User wants detailed analysis of specific properties
- Transfer to SchedulingAgent when: User wants to schedule property visits
- Stay active when: User needs search refinement or new searches

Remember: You are the entry point for property discovery. Make searches efficient and guide users toward their perfect property."""
    
    def _add_pydantic_tools(self, agent: PydanticAgent):
        """Add specialized tools to the PydanticAI agent."""
        
        @agent.tool
        async def search_properties(
            ctx: RunContext[Dict[str, Any]],
            criteria: str,
            location: str = "",
            max_price: int = 0,
            min_bedrooms: int = 0,
            property_type: str = ""
        ) -> str:
            """
            Search for properties based on detailed criteria.
            
            This tool provides intelligent property filtering and ranking.
            """
            with AgentExecutionContext("search_tool", "property_search") as span:
                try:
                    # In production, this would call real estate APIs
                    # For now, simulate intelligent search
                    
                    search_params = {
                        "criteria": criteria,
                        "location": location,
                        "max_price": max_price,
                        "min_bedrooms": min_bedrooms,
                        "property_type": property_type
                    }
                    
                    if span:
                        span.set_attributes({
                            "search.criteria": criteria,
                            "search.location": location,
                            "search.max_price": max_price,
                            "search.min_bedrooms": min_bedrooms,
                            "search.property_type": property_type
                        })
                    
                    # Simulate property search results
                    mock_results = self._generate_mock_search_results(search_params)
                    
                    log_agent_action(
                        agent_name="SearchAgent",
                        action="property_search_executed",
                        details=search_params
                    )
                    
                    return mock_results
                    
                except Exception as e:
                    self.logger.error(f"Property search tool error: {e}")
                    return "Search encountered an error. Please refine your criteria and try again."
        
        @agent.tool
        async def analyze_search_intent(
            ctx: RunContext[Dict[str, Any]],
            user_message: str
        ) -> str:
            """
            Analyze user message to extract search intent and criteria.
            
            This tool uses NLP to understand what the user is really looking for.
            """
            # Simulate intent analysis
            intent_analysis = f"""
INTENT ANALYSIS for: "{user_message}"

Detected criteria:
- Primary intent: Property search
- Urgency level: Medium
- Specificity: {"High" if len(user_message.split()) > 5 else "Low"}
- Location mentioned: {"Yes" if any(loc in user_message.lower() for loc in ["miami", "beach", "downtown", "brickell"]) else "No"}
- Price mentioned: {"Yes" if "$" in user_message or "price" in user_message.lower() else "No"}
- Features mentioned: {"Yes" if any(feat in user_message.lower() for feat in ["pool", "gym", "parking", "view"]) else "No"}

Recommended approach: {"Proceed with search" if "looking" in user_message.lower() else "Ask clarifying questions"}
"""
            return intent_analysis
    
    def _generate_mock_search_results(self, params: Dict[str, Any]) -> str:
        """Generate realistic mock search results for development."""
        criteria = params.get("criteria", "")
        location = params.get("location", "")
        
        # Simulate property matching
        base_count = 8
        if location:
            base_count += 3
        if params.get("max_price", 0) > 0:
            base_count -= 2
        if params.get("min_bedrooms", 0) > 0:
            base_count -= 1
            
        properties_found = max(1, base_count)
        
        return f"""
SEARCH RESULTS: {properties_found} properties found

TOP MATCHES:
1. 🏙️ Modern Apartment - Brickell Ave
   • $2,800/month • 2BR/2BA • 1,200 sq ft • Pool & Gym

2. 🌊 Beachfront Condo - South Beach  
   • $3,200/month • 1BR/1BA • 900 sq ft • Ocean View

3. 🏡 Townhouse - Coral Gables
   • $4,500/month • 3BR/2.5BA • 1,800 sq ft • Garden & Garage

SEARCH SUMMARY:
- Found {properties_found} properties matching criteria: "{criteria}"
- Price range: $2,200 - $4,500/month
- Location focus: {location or "Multiple areas"}
- Property types: Apartments, Condos, Townhouses

REFINEMENT OPTIONS:
- Narrow by specific neighborhood
- Set price range limits  
- Filter by specific amenities
- Adjust bedroom/bathroom requirements
"""
    
    def _create_langgraph_agent(self):
        """Create LangGraph agent with handoff capabilities."""
        
        # Create handoff tools
        handoff_to_property = create_handoff_tool(
            agent_name="PropertyAgent",
            description="Transfer to property analysis agent when user wants detailed property information or analysis"
        )
        
        handoff_to_scheduling = create_handoff_tool(
            agent_name="SchedulingAgent", 
            description="Transfer to scheduling agent when user wants to schedule property visits or viewings"
        )
        
        # Create wrapper tool that executes PydanticAI logic
        @tool
        async def execute_property_search(query: str) -> str:
            """Execute property search using PydanticAI agent with full benefits."""
            try:
                with AgentExecutionContext("search_execution", "pydantic_ai_call") as span:
                    
                    # Add datetime context
                    datetime_context = format_datetime_context_for_agent()
                    enhanced_query = f"""{datetime_context}

USER SEARCH REQUEST: "{query}"

Please analyze this search request and provide structured results with properties, summary, recommendations, and next actions."""
                    
                    if span:
                        span.set_attributes({
                            "search.query_length": len(query),
                            "search.enhanced_query_length": len(enhanced_query),
                            "search.framework": "pydantic_ai"
                        })
                    
                    # Execute PydanticAI agent (gets all benefits automatically)
                    result = await self.pydantic_agent.run(enhanced_query)
                    
                    # Extract structured result
                    if hasattr(result, 'output') and isinstance(result.output, SearchResult):
                        search_result = result.output
                        
                        response = f"""🔍 **Property Search Results**

📊 **Summary**: {search_result.summary}
🏠 **Properties Found**: {search_result.properties_found}

💡 **Recommendations**:
{chr(10).join(f"• {rec}" for rec in search_result.recommendations)}

🎯 **Next Steps**:
{chr(10).join(f"• {action}" for action in search_result.next_actions)}

What would you like to do next?"""
                        
                        log_agent_action(
                            agent_name="SearchAgent",
                            action="structured_search_completed",
                            details={
                                "properties_found": search_result.properties_found,
                                "recommendations_count": len(search_result.recommendations),
                                "next_actions_count": len(search_result.next_actions)
                            }
                        )
                        
                        return response
                    
                    else:
                        # Fallback to string output
                        return str(result.output) if hasattr(result, 'output') else str(result)
                        
            except Exception as e:
                self.logger.error(f"Property search execution error: {e}")
                return "I encountered an error during the search. Let me help you refine your criteria and try again."
        
        # Create tools list
        tools = [
            execute_property_search,
            handoff_to_property,
            handoff_to_scheduling
        ]
        
        # Create LangGraph agent
        agent = create_react_agent(
            self.langchain_model,
            tools,
            prompt="""You are a coordinator for property search requests. 

Your job is to:
1. Execute property searches using the execute_property_search tool
2. Decide when to hand off to other agents based on user needs
3. Keep the conversation flowing smoothly

When to use handoffs:
- PropertyAgent: When user wants detailed analysis of specific properties
- SchedulingAgent: When user wants to schedule property visits

Always use the execute_property_search tool for actual search requests.""",
            name="SearchAgent"
        )
        
        self.logger.info("✅ LangGraph search agent created with handoff tools")
        return agent
    
    def get_agent(self):
        """Return the LangGraph agent for swarm integration."""
        return self.langgraph_agent
    
    async def direct_execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> SearchResult:
        """
        Directly execute PydanticAI agent for testing or direct use.
        
        This bypasses LangGraph and gives direct access to PydanticAI benefits.
        """
        try:
            datetime_context = format_datetime_context_for_agent()
            enhanced_query = f"""{datetime_context}

USER SEARCH REQUEST: "{query}"

CONTEXT: {context or "No additional context"}

Please analyze this search request and provide structured results."""
            
            result = await self.pydantic_agent.run(enhanced_query)
            return result.output if hasattr(result, 'output') else result
            
        except Exception as e:
            self.logger.error(f"Direct execution error: {e}")
            return SearchResult(
                properties_found=0,
                summary="Search encountered an error",
                recommendations=["Please refine your search criteria"],
                next_actions=["Try a different search approach"]
            )