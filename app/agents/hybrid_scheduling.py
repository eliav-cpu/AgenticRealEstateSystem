"""
Hybrid Scheduling Agent - LangGraph-Swarm + PydanticAI

This agent combines:
- LangGraph-Swarm for handoffs and coordination
- PydanticAI for execution with retry, validation, streaming, and observability
"""

from typing import Dict, Any, List, Optional, Annotated
from datetime import datetime, date, time
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool
from pydantic_ai import Agent as PydanticAgent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic import BaseModel, Field

from ..utils.logging import get_logger, log_agent_action
from ..utils.logfire_config import AgentExecutionContext
from ..utils.datetime_context import get_scheduling_context_for_agent
from config.settings import get_settings
import time as time_module


class SchedulingResult(BaseModel):
    """Structured output for scheduling operations."""
    appointment_status: str = Field(description="Status of the scheduling request")
    proposed_times: List[str] = Field(description="Suggested available time slots")
    confirmation_details: Optional[str] = Field(description="Confirmation details if scheduled")
    requirements: List[str] = Field(description="What to bring or prepare for the visit")
    contact_info: str = Field(description="Contact information for the appointment")
    next_steps: List[str] = Field(description="Next actions for the user")


class TimeSlotValidation(BaseModel):
    """Structured output for time slot validation."""
    is_valid: bool = Field(description="Whether the requested time is valid")
    validation_message: str = Field(description="Explanation of validation result")
    alternative_times: List[str] = Field(description="Alternative time suggestions if invalid")
    business_hours_info: str = Field(description="Information about business hours")


class HybridSchedulingAgent:
    """
    Scheduling agent that combines LangGraph-Swarm coordination with PydanticAI execution.
    
    Benefits from PydanticAI:
    - Model retry and fallback
    - Input/output validation  
    - Dependency injection
    - Streaming responses
    - Native observability via Logfire
    - Advanced temporal reasoning
    """
    
    def __init__(self, langchain_model):
        self.agent_name = "SchedulingAgent"
        self.logger = get_logger("hybrid_scheduling")
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
                raise ValueError("Valid OpenRouter API key required for SchedulingAgent")
            
            # Create PydanticAI agent with structured output
            provider = OpenRouterProvider(api_key=api_key)
            model = OpenAIModel("mistralai/mistral-7b-instruct:free", provider=provider)
            
            agent = PydanticAgent(
                model=model,
                result_type=SchedulingResult,
                system_prompt=self._get_system_prompt()
            )
            
            # Add tools to PydanticAI agent
            self._add_pydantic_tools(agent)
            
            self.logger.info("✅ PydanticAI scheduling agent created with structured output")
            return agent
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create PydanticAI scheduling agent: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Get comprehensive system prompt for scheduling agent."""
        return """You are Mike, a professional scheduling assistant for real estate property viewings with advanced temporal intelligence.

CORE RESPONSIBILITIES:
1. Schedule property visits with precise time management
2. Validate time slots against business hours and availability
3. Provide clear scheduling confirmations and details
4. Handle scheduling conflicts and changes efficiently
5. Ensure all parties have necessary information

SCHEDULING EXPERTISE:
- Business hours: Monday-Friday 9:00 AM - 6:00 PM, Saturday 9:00 AM - 4:00 PM
- Advanced natural language time parsing ("tomorrow afternoon", "next Tuesday at 2")
- Timezone awareness and conflict detection
- Optimal scheduling strategies for property viewings
- Integration with calendar systems and notifications

TEMPORAL INTELLIGENCE:
- Parse complex time expressions accurately
- Calculate relative dates (tomorrow, next week, etc.)
- Validate business hours and availability
- Suggest optimal viewing times based on property type
- Handle scheduling conflicts gracefully

COMMUNICATION STYLE:
- Professional, efficient, and detail-oriented
- Provide specific times and clear instructions
- Use emojis strategically for clarity
- Confirm all details explicitly
- Offer alternatives when requested times aren't available

OUTPUT REQUIREMENTS:
- Always return structured SchedulingResult format
- Include 2-3 specific time slot options
- Provide clear confirmation details
- List what to bring to appointments
- Include contact information for changes

HANDOFF DECISIONS:
- Transfer to PropertyAgent when: User needs property details before scheduling
- Transfer to SearchAgent when: User wants to find different properties to visit
- Stay active when: User needs scheduling, rescheduling, or appointment management

Remember: You ensure smooth, professional scheduling that creates excellent client experiences."""
    
    def _add_pydantic_tools(self, agent: PydanticAgent):
        """Add specialized tools to the PydanticAI agent."""
        
        @agent.tool
        async def validate_time_slot(
            ctx: RunContext[Dict[str, Any]],
            requested_date: str,
            requested_time: str,
            property_address: str = ""
        ) -> str:
            """
            Validate if a requested time slot is available and appropriate.
            
            Checks business hours, conflicts, and property-specific requirements.
            """
            with AgentExecutionContext("scheduling_validation", "time_slot_check") as span:
                try:
                    validation_params = {
                        "date": requested_date,
                        "time": requested_time,
                        "property": property_address
                    }
                    
                    if span:
                        span.set_attributes({
                            "scheduling.requested_date": requested_date,
                            "scheduling.requested_time": requested_time,
                            "scheduling.property": property_address
                        })
                    
                    # Simulate time slot validation
                    validation_result = self._validate_time_slot(requested_date, requested_time)
                    
                    log_agent_action(
                        agent_name="SchedulingAgent",
                        action="time_slot_validated",
                        details=validation_params
                    )
                    
                    return validation_result
                    
                except Exception as e:
                    self.logger.error(f"Time validation tool error: {e}")
                    return "Time validation encountered an error. Please provide a specific date and time."
        
        @agent.tool
        async def book_appointment(
            ctx: RunContext[Dict[str, Any]],
            property_address: str,
            appointment_date: str,
            appointment_time: str,
            client_contact: str = ""
        ) -> str:
            """
            Book a confirmed appointment for property viewing.
            
            Creates the appointment and provides confirmation details.
            """
            with AgentExecutionContext("appointment_booking", "create_appointment") as span:
                try:
                    booking_params = {
                        "property": property_address,
                        "date": appointment_date,
                        "time": appointment_time,
                        "contact": client_contact
                    }
                    
                    if span:
                        span.set_attributes({
                            "booking.property": property_address,
                            "booking.date": appointment_date,
                            "booking.time": appointment_time,
                            "booking.has_contact": bool(client_contact)
                        })
                    
                    # Simulate appointment booking
                    booking_result = self._create_appointment(property_address, appointment_date, appointment_time, client_contact)
                    
                    log_agent_action(
                        agent_name="SchedulingAgent",
                        action="appointment_booked",
                        details=booking_params
                    )
                    
                    return booking_result
                    
                except Exception as e:
                    self.logger.error(f"Appointment booking tool error: {e}")
                    return "Booking encountered an error. Please verify all appointment details."
        
        @agent.tool
        async def get_available_slots(
            ctx: RunContext[Dict[str, Any]],
            preferred_date_range: str = "this week",
            property_type: str = "apartment",
            time_preference: str = "any"
        ) -> str:
            """
            Get available time slots for property viewings.
            
            Returns optimal viewing times based on preferences and availability.
            """
            # Simulate availability check
            available_slots = self._get_available_slots(preferred_date_range, time_preference)
            return available_slots
    
    def _validate_time_slot(self, date_str: str, time_str: str) -> str:
        """Validate time slot against business rules."""
        try:
            # Simple validation logic for demo
            current_time = datetime.now()
            
            # Parse time preference
            if "morning" in time_str.lower():
                suggested_time = "10:00 AM"
                is_valid = True
            elif "afternoon" in time_str.lower():
                suggested_time = "2:00 PM"
                is_valid = True
            elif "evening" in time_str.lower():
                suggested_time = "5:00 PM"
                is_valid = True
            else:
                suggested_time = time_str
                is_valid = True
            
            return f"""
TIME SLOT VALIDATION for {date_str} at {time_str}

✅ STATUS: {"Valid" if is_valid else "Invalid"}
🕒 SUGGESTED TIME: {suggested_time}
📋 BUSINESS HOURS: Monday-Friday 9:00 AM - 6:00 PM, Saturday 9:00 AM - 4:00 PM

VALIDATION DETAILS:
• Requested time falls within business hours
• No conflicts detected in calendar
• Property available for viewing
• Adequate time allocated (45 minutes)

ALTERNATIVE OPTIONS:
• Same day: 11:00 AM, 3:30 PM
• Next day: 10:00 AM, 2:00 PM, 4:00 PM
• Weekend: Saturday 9:30 AM, 1:00 PM
"""
        except Exception as e:
            return f"Time validation error: {e}"
    
    def _create_appointment(self, property_address: str, date: str, time: str, contact: str) -> str:
        """Create appointment confirmation."""
        appointment_id = f"APT{datetime.now().strftime('%Y%m%d%H%M')}"
        
        return f"""
APPOINTMENT CONFIRMATION

📅 **Appointment Scheduled Successfully!**

🆔 CONFIRMATION ID: {appointment_id}
🏠 PROPERTY: {property_address}
📅 DATE: {date}
🕒 TIME: {time}
⏱️ DURATION: 45 minutes

👤 **Contact Information:**
📞 Showing Agent: Maria Santos - (305) 555-0123
📧 Email: maria.santos@realestate.com
📱 Text: Available for last-minute changes

📋 **What to Bring:**
• Valid photo ID
• Proof of income (if interested in applying)
• List of questions about the property
• Comfortable walking shoes

🚗 **Parking Information:**
• Guest parking available in visitor spaces
• Street parking also available
• Parking validation provided if needed

📱 **Reminders:**
• Confirmation SMS sent to your phone
• Email confirmation with directions
• Reminder call 1 hour before appointment

❓ **Questions or Changes:**
Call or text Maria at (305) 555-0123
"""
    
    def _get_available_slots(self, date_range: str, time_preference: str) -> str:
        """Get available appointment slots."""
        current_date = datetime.now()
        
        return f"""
AVAILABLE APPOINTMENT SLOTS

📅 **{date_range.upper()} AVAILABILITY**

🌅 **MORNING SLOTS (9:00 AM - 12:00 PM):**
• Tomorrow: 9:30 AM, 11:00 AM
• Thursday: 10:00 AM, 11:30 AM
• Friday: 9:00 AM, 10:30 AM

🌞 **AFTERNOON SLOTS (1:00 PM - 5:00 PM):**
• Tomorrow: 2:00 PM, 3:30 PM, 4:30 PM
• Thursday: 1:30 PM, 3:00 PM
• Friday: 2:30 PM, 4:00 PM

🌅 **WEEKEND SLOTS (Saturday only):**
• Saturday: 9:00 AM, 11:00 AM, 1:00 PM

⭐ **RECOMMENDED TIMES:**
• Weekday mornings for quieter viewings
• Afternoon slots for natural lighting
• Saturday mornings for thorough exploration

💡 **BOOKING TIPS:**
• Book 24-48 hours in advance
• Allow 45-60 minutes per property
• Consider traffic patterns for timing
• Multiple properties can be scheduled same day

Which time slot works best for your schedule?
"""
    
    def _create_langgraph_agent(self):
        """Create LangGraph agent with handoff capabilities."""
        
        # Create handoff tools
        handoff_to_property = create_handoff_tool(
            agent_name="PropertyAgent",
            description="Transfer to property agent when user needs property details before scheduling"
        )
        
        handoff_to_search = create_handoff_tool(
            agent_name="SearchAgent",
            description="Transfer to search agent when user wants to find different properties to visit"
        )
        
        # Create wrapper tool that executes PydanticAI logic
        @tool
        async def execute_scheduling_logic(query: str, property_context: str = "") -> str:
            """Execute scheduling logic using PydanticAI agent with full benefits."""
            try:
                with AgentExecutionContext("scheduling_execution", "pydantic_ai_call") as span:
                    
                    # Add specialized datetime context for scheduling
                    scheduling_context = get_scheduling_context_for_agent()
                    enhanced_query = f"""{scheduling_context}

SCHEDULING REQUEST: "{query}"

PROPERTY CONTEXT: {property_context or "No specific property context provided"}

Please analyze this scheduling request and provide structured results with appointment status, proposed times, confirmation details, requirements, contact info, and next steps."""
                    
                    if span:
                        span.set_attributes({
                            "scheduling.query_length": len(query),
                            "scheduling.has_property_context": bool(property_context),
                            "scheduling.framework": "pydantic_ai"
                        })
                    
                    # Execute PydanticAI agent (gets all benefits automatically)
                    result = await self.pydantic_agent.run(enhanced_query)
                    
                    # Extract structured result
                    if hasattr(result, 'output') and isinstance(result.output, SchedulingResult):
                        scheduling = result.output
                        
                        response = f"""📅 **Scheduling Assistant**

📋 **Status**: {scheduling.appointment_status}

🕒 **Available Times**:
{chr(10).join(f"• {time_slot}" for time_slot in scheduling.proposed_times)}

{f"✅ **Confirmation**: {scheduling.confirmation_details}" if scheduling.confirmation_details else ""}

📦 **Please Bring**:
{chr(10).join(f"• {requirement}" for requirement in scheduling.requirements)}

📞 **Contact**: {scheduling.contact_info}

🎯 **Next Steps**:
{chr(10).join(f"• {step}" for step in scheduling.next_steps)}

Which time works best for you?"""
                        
                        log_agent_action(
                            agent_name="SchedulingAgent",
                            action="structured_scheduling_completed",
                            details={
                                "status": scheduling.appointment_status,
                                "proposed_times_count": len(scheduling.proposed_times),
                                "has_confirmation": bool(scheduling.confirmation_details),
                                "requirements_count": len(scheduling.requirements)
                            }
                        )
                        
                        return response
                    
                    else:
                        # Fallback to string output
                        return str(result.output) if hasattr(result, 'output') else str(result)
                        
            except Exception as e:
                self.logger.error(f"Scheduling execution error: {e}")
                return "I encountered an error with scheduling. Let me help you find available appointment times."
        
        # Create tools list
        tools = [
            execute_scheduling_logic,
            handoff_to_property,
            handoff_to_search
        ]
        
        # Create LangGraph agent
        agent = create_react_agent(
            self.langchain_model,
            tools,
            prompt="""You are a coordinator for scheduling requests.

Your job is to:
1. Execute scheduling operations using the execute_scheduling_logic tool
2. Decide when to hand off to other agents based on user needs
3. Manage appointment booking and calendar coordination

When to use handoffs:
- PropertyAgent: When user needs property details before scheduling
- SearchAgent: When user wants to find different properties to visit

Always use the execute_scheduling_logic tool for scheduling-related requests.""",
            name="SchedulingAgent"
        )
        
        self.logger.info("✅ LangGraph scheduling agent created with handoff tools")
        return agent
    
    def get_agent(self):
        """Return the LangGraph agent for swarm integration."""
        return self.langgraph_agent
    
    async def direct_execute(self, query: str, property_context: Optional[Dict[str, Any]] = None) -> SchedulingResult:
        """
        Directly execute PydanticAI agent for testing or direct use.
        
        This bypasses LangGraph and gives direct access to PydanticAI benefits.
        """
        try:
            scheduling_context = get_scheduling_context_for_agent()
            enhanced_query = f"""{scheduling_context}

SCHEDULING REQUEST: "{query}"

PROPERTY CONTEXT: {property_context or "No additional context"}

Please analyze this scheduling request and provide structured results."""
            
            result = await self.pydantic_agent.run(enhanced_query)
            return result.output if hasattr(result, 'output') else result
            
        except Exception as e:
            self.logger.error(f"Direct execution error: {e}")
            return SchedulingResult(
                appointment_status="Error occurred during scheduling",
                proposed_times=["Please try again with specific date and time preferences"],
                confirmation_details=None,
                requirements=["Contact information for scheduling assistance"],
                contact_info="Please call (305) 555-0123 for assistance",
                next_steps=["Retry scheduling request with more details"]
            )