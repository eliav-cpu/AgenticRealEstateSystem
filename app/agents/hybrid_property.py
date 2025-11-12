"""
Hybrid Property Agent - LangGraph-Swarm + PydanticAI

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
from pydantic import BaseModel, Field

from ..utils.logging import get_logger, log_agent_action
from ..utils.logfire_config import AgentExecutionContext
from ..utils.datetime_context import format_datetime_context_for_agent
from config.settings import get_settings
import time


class PropertyAnalysis(BaseModel):
    """Structured output for property analysis."""
    property_highlights: List[str] = Field(description="Key highlights of the property")
    advantages: List[str] = Field(description="Advantages and positive aspects")
    disadvantages: List[str] = Field(description="Potential concerns or limitations")
    market_context: str = Field(description="Market context and pricing analysis")
    recommendation: str = Field(description="Overall recommendation")
    next_steps: List[str] = Field(description="Suggested next actions")


class PropertyComparison(BaseModel):
    """Structured output for property comparisons."""
    comparison_summary: str = Field(description="Overall comparison summary")
    winner: str = Field(description="Which property is recommended and why")
    key_differences: List[str] = Field(description="Main differences between properties")
    decision_factors: List[str] = Field(description="Factors to consider in decision making")


class HybridPropertyAgent:
    """
    Property agent that combines LangGraph-Swarm coordination with PydanticAI execution.
    
    Benefits from PydanticAI:
    - Model retry and fallback
    - Input/output validation  
    - Dependency injection
    - Streaming responses
    - Native observability via Logfire
    """
    
    def __init__(self, langchain_model):
        self.agent_name = "PropertyAgent"
        self.logger = get_logger("hybrid_property")
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
                raise ValueError("Valid OpenRouter API key required for PropertyAgent")
            
            # Create PydanticAI agent with structured output
            provider = OpenRouterProvider(api_key=api_key)
            model = OpenAIModel("mistralai/mistral-7b-instruct:free", provider=provider)
            
            agent = PydanticAgent(
                model=model,
                result_type=PropertyAnalysis,
                system_prompt=self._get_system_prompt()
            )
            
            # Add tools to PydanticAI agent
            self._add_pydantic_tools(agent)
            
            self.logger.info("✅ PydanticAI property agent created with structured output")
            return agent
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create PydanticAI property agent: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Get comprehensive system prompt for property agent."""
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

EXPERTISE AREAS:
- Property valuation and market analysis
- Neighborhood characteristics and trends
- Investment potential assessment
- Maintenance and ownership considerations
- Financing and legal aspects overview

COMMUNICATION STYLE:
- Professional, informative, and objective
- Use data and specific examples when possible
- Balance optimism with realistic assessments
- Provide actionable insights and recommendations
- Use emojis strategically for clarity

OUTPUT REQUIREMENTS:
- Always return structured PropertyAnalysis format
- Include 3-5 specific highlights per section
- Provide concrete, actionable recommendations
- List 2-3 clear next step options
- Be honest about both pros and cons

HANDOFF DECISIONS:
- Transfer to SearchAgent when: User wants to find different or additional properties
- Transfer to SchedulingAgent when: User wants to schedule property visits
- Stay active when: User needs property analysis, comparisons, or details

Remember: You provide the expertise clients need to make confident property decisions."""
    
    def _add_pydantic_tools(self, agent: PydanticAgent):
        """Add specialized tools to the PydanticAI agent."""
        
        @agent.tool
        async def analyze_property_details(
            ctx: RunContext[Dict[str, Any]],
            property_address: str,
            property_data: str = "",
            analysis_focus: str = "general"
        ) -> str:
            """
            Perform detailed analysis of a specific property.
            
            Analyzes location, features, pricing, and investment potential.
            """
            with AgentExecutionContext("property_analysis", "detailed_analysis") as span:
                try:
                    analysis_params = {
                        "address": property_address,
                        "focus": analysis_focus,
                        "data_available": bool(property_data)
                    }
                    
                    if span:
                        span.set_attributes({
                            "analysis.address": property_address,
                            "analysis.focus": analysis_focus,
                            "analysis.has_data": bool(property_data)
                        })
                    
                    # Simulate detailed property analysis
                    analysis_result = self._generate_property_analysis(property_address, property_data, analysis_focus)
                    
                    log_agent_action(
                        agent_name="PropertyAgent",
                        action="property_analysis_completed",
                        details=analysis_params
                    )
                    
                    return analysis_result
                    
                except Exception as e:
                    self.logger.error(f"Property analysis tool error: {e}")
                    return "Analysis encountered an error. Please provide more property details."
        
        @agent.tool
        async def get_market_context(
            ctx: RunContext[Dict[str, Any]],
            location: str,
            property_type: str = "apartment"
        ) -> str:
            """
            Get market context and pricing trends for the area.
            
            Provides comparative market analysis and trends.
            """
            # Simulate market analysis
            market_data = f"""
MARKET CONTEXT for {location}

CURRENT MARKET TRENDS:
• Average rent: $2,800-3,500/month ({property_type})
• Market velocity: Moderate (properties rent within 30-45 days)
• Price trend: +3.2% increase over last 12 months
• Inventory level: Balanced market conditions

NEIGHBORHOOD HIGHLIGHTS:
• High walkability score (8.5/10)
• Excellent public transportation access
• Growing tech and finance job market
• New developments planned for 2024-2025

COMPARABLE PROPERTIES:
• Similar units renting for $2,650-3,200/month
• Average days on market: 35 days
• Tenant retention rate: 78% annual renewal

INVESTMENT OUTLOOK:
• Positive rental yield potential
• Strong appreciation history
• Low vacancy rates (4.2%)
• Premium location with growth potential
"""
            return market_data
        
        @agent.tool
        async def compare_properties(
            ctx: RunContext[Dict[str, Any]],
            property1_data: str,
            property2_data: str,
            comparison_criteria: str = "value"
        ) -> str:
            """
            Compare two properties across key criteria.
            
            Provides side-by-side analysis with recommendations.
            """
            # Simulate property comparison
            comparison = f"""
PROPERTY COMPARISON ANALYSIS

COMPARISON CRITERIA: {comparison_criteria}

PROPERTY A vs PROPERTY B

VALUE PROPOSITION:
• Property A: Better price-to-feature ratio
• Property B: Premium location advantage

LOCATION ANALYSIS:
• Property A: Emerging neighborhood, growth potential
• Property B: Established area, proven value

FEATURES COMPARISON:
• Property A: Modern amenities, newer construction
• Property B: Classic features, larger spaces

FINANCIAL ANALYSIS:
• Property A: Lower upfront cost, moderate appreciation
• Property B: Higher initial investment, stable returns

RECOMMENDATION: Based on {comparison_criteria} criteria, Property {"A" if "value" in comparison_criteria else "B"} offers the better fit.
"""
            return comparison
    
    def _generate_property_analysis(self, address: str, data: str, focus: str) -> str:
        """Generate realistic property analysis for development."""
        return f"""
DETAILED PROPERTY ANALYSIS: {address}

PROPERTY OVERVIEW:
• Modern 2BR/2BA apartment in prime location
• 1,200 sq ft with premium finishes
• Built in 2019, excellent condition
• Monthly rent: $3,200 including amenities

LOCATION STRENGTHS:
• Walking distance to metro station (0.3 miles)
• Top-rated restaurants and shopping nearby
• Safe, well-maintained neighborhood
• Easy access to business districts

PROPERTY FEATURES:
• In-unit washer/dryer and dishwasher
• Floor-to-ceiling windows with city views
• Modern kitchen with granite countertops
• Building amenities: Pool, gym, concierge

MARKET POSITION:
• Priced competitively for the area
• Similar units range $2,950-3,400/month
• Strong rental demand in this building
• Historical appreciation of 4-6% annually

CONSIDERATIONS:
• Parking space available for additional $150/month
• Pet-friendly with reasonable deposits
• 12-month lease minimum required
• Utilities (electric/gas) not included (~$120/month)

INVESTMENT PERSPECTIVE:
Focus: {focus}
This property represents solid value in a desirable location with strong fundamentals.
"""
    
    def _create_langgraph_agent(self):
        """Create LangGraph agent with handoff capabilities."""
        
        # Create handoff tools
        handoff_to_search = create_handoff_tool(
            agent_name="SearchAgent",
            description="Transfer to search agent when user wants to find different or additional properties"
        )
        
        handoff_to_scheduling = create_handoff_tool(
            agent_name="SchedulingAgent",
            description="Transfer to scheduling agent when user wants to schedule property visits or viewings"
        )
        
        # Create wrapper tool that executes PydanticAI logic
        @tool
        async def execute_property_analysis(query: str, property_context: str = "") -> str:
            """Execute property analysis using PydanticAI agent with full benefits."""
            try:
                with AgentExecutionContext("property_execution", "pydantic_ai_call") as span:
                    
                    # Add datetime context
                    datetime_context = format_datetime_context_for_agent()
                    enhanced_query = f"""{datetime_context}

PROPERTY ANALYSIS REQUEST: "{query}"

PROPERTY CONTEXT: {property_context or "No specific property context provided"}

Please analyze this request and provide structured analysis with highlights, advantages, disadvantages, market context, recommendation, and next steps."""
                    
                    if span:
                        span.set_attributes({
                            "property.query_length": len(query),
                            "property.has_context": bool(property_context),
                            "property.framework": "pydantic_ai"
                        })
                    
                    # Execute PydanticAI agent (gets all benefits automatically)
                    result = await self.pydantic_agent.run(enhanced_query)
                    
                    # Extract structured result
                    if hasattr(result, 'output') and isinstance(result.output, PropertyAnalysis):
                        analysis = result.output
                        
                        response = f"""🏠 **Property Analysis**

✨ **Key Highlights**:
{chr(10).join(f"• {highlight}" for highlight in analysis.property_highlights)}

👍 **Advantages**:
{chr(10).join(f"• {advantage}" for advantage in analysis.advantages)}

⚠️ **Considerations**:
{chr(10).join(f"• {concern}" for concern in analysis.disadvantages)}

📊 **Market Context**: {analysis.market_context}

💡 **Recommendation**: {analysis.recommendation}

🎯 **Next Steps**:
{chr(10).join(f"• {step}" for step in analysis.next_steps)}

What specific aspect would you like me to explore further?"""
                        
                        log_agent_action(
                            agent_name="PropertyAgent",
                            action="structured_analysis_completed",
                            details={
                                "highlights_count": len(analysis.property_highlights),
                                "advantages_count": len(analysis.advantages),
                                "concerns_count": len(analysis.disadvantages),
                                "next_steps_count": len(analysis.next_steps)
                            }
                        )
                        
                        return response
                    
                    else:
                        # Fallback to string output
                        return str(result.output) if hasattr(result, 'output') else str(result)
                        
            except Exception as e:
                self.logger.error(f"Property analysis execution error: {e}")
                return "I encountered an error during the analysis. Let me help you with specific property questions."
        
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
            prompt="""You are a coordinator for property analysis requests.

Your job is to:
1. Execute property analysis using the execute_property_analysis tool
2. Decide when to hand off to other agents based on user needs
3. Maintain expert-level property discussions

When to use handoffs:
- SearchAgent: When user wants to find different or additional properties
- SchedulingAgent: When user wants to schedule property visits

Always use the execute_property_analysis tool for property-related questions and analysis.""",
            name="PropertyAgent"
        )
        
        self.logger.info("✅ LangGraph property agent created with handoff tools")
        return agent
    
    def get_agent(self):
        """Return the LangGraph agent for swarm integration."""
        return self.langgraph_agent
    
    async def direct_execute(self, query: str, property_context: Optional[Dict[str, Any]] = None) -> PropertyAnalysis:
        """
        Directly execute PydanticAI agent for testing or direct use.
        
        This bypasses LangGraph and gives direct access to PydanticAI benefits.
        """
        try:
            datetime_context = format_datetime_context_for_agent()
            enhanced_query = f"""{datetime_context}

PROPERTY ANALYSIS REQUEST: "{query}"

PROPERTY CONTEXT: {property_context or "No additional context"}

Please analyze this request and provide structured analysis."""
            
            result = await self.pydantic_agent.run(enhanced_query)
            return result.output if hasattr(result, 'output') else result
            
        except Exception as e:
            self.logger.error(f"Direct execution error: {e}")
            return PropertyAnalysis(
                property_highlights=["Analysis unavailable due to error"],
                advantages=["Please try again with specific property details"],
                disadvantages=["Unable to assess at this time"],
                market_context="Market analysis unavailable",
                recommendation="Please provide more property information for analysis",
                next_steps=["Retry with specific property address or details"]
            )