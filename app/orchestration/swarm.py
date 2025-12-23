"""
Orquestrador LangGraph-Swarm com Agentes PydanticAI usando Groq

Implementação da arquitetura swarm com:
- Groq como LLM provider (modelo openai/gpt-oss-120b)
- PydanticAI para agentes inteligentes
- LangGraph-Swarm para orquestração
- Supervisor para avaliar respostas antes de enviar ao usuário
- Manager para análise de logs em tempo real
- Fallback inteligente com Ollama
"""

from typing import Dict, Any, List, Optional, AsyncIterator, Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

from ..utils.logging import get_logger, log_handoff, log_performance, log_agent_action, log_api_call, log_error
from ..utils.logfire_config import AgentExecutionContext, HandoffContext, get_logfire_config
from ..utils.ollama_fallback import generate_intelligent_fallback
from ..utils.datetime_context import format_datetime_context_for_agent, get_scheduling_context_for_agent
from ..agents.supervisor import get_supervisor, SupervisorDecision
from ..agents.manager import get_manager
from config.settings import get_settings
import time
import os
import random
import asyncio


async def create_pydantic_agent(agent_name: str, model_name: str = None) -> Agent:
    """
    Create PydanticAI agent using Groq as LLM provider.

    Args:
        agent_name: Name of the agent for logging
        model_name: Groq model to use (defaults to settings.groq.default_model)

    Returns:
        Configured PydanticAI Agent with Logfire instrumentation

    Raises:
        ValueError: If no valid Groq API key is found
    """
    logger = get_logger(f"{agent_name}_factory")
    settings = get_settings()

    # Use Groq configuration
    api_key = settings.groq.api_key
    base_url = settings.groq.base_url
    model_name = model_name or settings.groq.default_model

    # Ensure GROQ_API_KEY is set in environment (required by PydanticAI GroqModel)
    if api_key:
        os.environ['GROQ_API_KEY'] = api_key

    # Logfire tracing for agent creation
    with AgentExecutionContext(agent_name, "agent_creation") as span:

        # Validate API key
        if not api_key or api_key.strip() == "":
            error_msg = f"No valid Groq API key found for {agent_name}"
            logger.error(f"ERROR: {error_msg}")
            if span:
                span.set_attribute("agent.creation_error", error_msg)
            raise ValueError(error_msg)

        logger.info(f"Creating PydanticAI agent '{agent_name}' with Groq")
        logger.info(f"Model: {model_name}, Base URL: {base_url}")

        if span:
            span.set_attributes({
                "agent.name": agent_name,
                "agent.model": model_name,
                "agent.provider": "groq",
                "agent.base_url": base_url,
                "agent.creation_stage": "setup"
            })

        try:
            # Create Groq model directly using PydanticAI's native GroqModel
            model = GroqModel(model_name)
            logger.info(f"Groq model created: {model_name}")

            if span:
                span.set_attribute("agent.model_created", True)

            # Create agent
            agent = Agent(model)
            logger.info(f"Agent '{agent_name}' created successfully with Groq")

            if span:
                span.set_attributes({
                    "agent.agent_created": True,
                    "agent.creation_success": True,
                    "agent.creation_stage": "completed"
                })

            log_agent_action(
                agent_name=agent_name,
                action="agent_created",
                details={
                    "model": model_name,
                    "provider": "groq",
                    "base_url": base_url,
                    "success": True
                }
            )

            return agent

        except Exception as e:
            error_msg = f"Failed to create PydanticAI agent for {agent_name}: {e}"
            logger.error(f"ERROR: {error_msg}")

            if span:
                span.set_attributes({
                    "agent.creation_success": False,
                    "agent.creation_error": str(e),
                    "agent.creation_stage": "failed"
                })

            log_error(e, context={
                "agent_name": agent_name,
                "model_name": model_name,
                "operation": "agent_creation"
            })

            raise


class SwarmState(MessagesState):
    """Estado global do swarm com contexto compartilhado."""
    
    # Contexto de sessão
    session_id: str = Field(default="default")
    user_id: Optional[str] = None
    
    # Estado de busca
    search_intent: Optional[Dict[str, Any]] = None
    search_results: Optional[Dict[str, Any]] = None
    
    # Estado de análise de propriedades
    property_analysis: Optional[Dict[str, Any]] = None
    property_recommendations: Optional[List[Dict[str, Any]]] = None
    
    # Estado de agendamento
    scheduling_intent: Optional[Dict[str, Any]] = None
    calendar_events: Optional[List[Dict[str, Any]]] = None
    
    # Contexto de handoffs
    current_agent: str = Field(default="search_agent")
    handoff_history: List[Dict[str, Any]] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)


async def search_agent_node(state: SwarmState) -> dict:
    """Nó do agente de busca: entende a intenção de busca usando PydanticAI com Groq."""
    logger = get_logger("search_agent")

    # Logfire tracing
    with AgentExecutionContext("search_agent", "property_search") as logfire_span:
        start_time = time.time()
        
        # 🔥 CORREÇÃO: Acessar mensagens corretamente no LangGraph
        messages = state.messages if hasattr(state, 'messages') else state.get("messages", [])
        if not messages:
            logger.warning("No messages in state for search_agent")
            return {"messages": [AIMessage(content="Olá! Sou Alex, especialista em busca de imóveis. Como posso ajudá-lo?")]}
        
        # Extrair mensagem do usuário (compatível com dict e LangChain messages)
        last_message = messages[-1]
        if hasattr(last_message, 'content'):
            user_message = last_message.content
        else:
            user_message = last_message.get("content", "")
        
        context = state.get("context", {})
        data_mode = context.get("data_mode", "mock")
        
        # Log estruturado da execução do agente
        log_agent_action(
            agent_name="search_agent",
            action="process_search_request",
            details={
                "user_message": user_message[:100] + "..." if len(user_message) > 100 else user_message,
                "data_mode": data_mode,
                "session_id": state.get("session_id", "default")
            }
        )
        
        settings = get_settings()
        groq_key = settings.groq.api_key

        # Verificar chave Groq
        if not groq_key or groq_key.strip() == "":
            logger.warning("No valid Groq key found. Using Ollama fallback.")
            fallback_response = await generate_intelligent_fallback("search_agent", user_message, state.get("context", {}).get("property_context", {}), "mock")

            log_agent_action(
                agent_name="search_agent",
                action="ollama_fallback_response",
                details={"reason": "no_groq_key", "response_length": len(fallback_response)}
            )

            return {"messages": [AIMessage(content=fallback_response)]}

        try:
            logger.info(f"Using Groq search agent in {data_mode.upper()} mode: '{user_message[:50]}...'")
            
            # Try to get available properties from the system
            available_properties = []
            filtered_properties = []
            try:
                # Import here to avoid circular imports
                import requests
                import json
                
                # Get properties from the Mock API directly
                if data_mode == "mock":
                    # Use FastAPI Mock endpoint
                    response = requests.get("http://localhost:8000/api/properties/search")
                    if response.status_code == 200:
                        data = response.json()
                        available_properties = data.get("properties", [])
                        logger.info(f"PROPERTY Found {len(available_properties)} total properties in {data_mode} mode")
                        
                        # 🔥 NOVO: Filtrar propriedades baseadas na mensagem do usuário
                        filtered_properties = filter_properties_by_user_intent(user_message, available_properties)
                        logger.info(f"FILTER Filtered to {len(filtered_properties)} matching properties")
                    else:
                        logger.warning(f"Mock API returned status {response.status_code}")
                else:
                    # For real mode, we'd use actual API calls
                    logger.info("Real API mode not implemented yet")
                    available_properties = []
                
                # Log da busca de propriedades
                log_api_call(
                    api_name="MockAPI",
                    endpoint="/api/properties/search",
                    method="GET",
                    status_code=200,
                    duration=None
                )
                
            except Exception as e:
                logger.warning(f"Could not get available properties: {e}")
                log_error(e, context={"agent": "search_agent", "operation": "get_properties"})
            
            # 🔥 NOVO: Criar resumo inteligente das propriedades
            property_summary = create_intelligent_property_summary(user_message, filtered_properties, available_properties)

            # 🔥 Add conversation context awareness
            is_first_message = len(messages) <= 1
            conversation_info = ""
            if not is_first_message:
                conversation_info = f"""
CONVERSATION CONTEXT:
- This is NOT the first message in the conversation (message #{len(messages)})
- Continue the conversation naturally without greeting again
- Build on previous context and maintain conversation flow
"""
            else:
                conversation_info = """
CONVERSATION CONTEXT:
- This is the first message in the conversation
- You can start with a greeting and introduction
"""

            # Create comprehensive search prompt with datetime context
            datetime_context = format_datetime_context_for_agent()
            prompt = f"""You are Alex, a professional real estate search specialist. You help clients find properties that match their needs and provide market insights.

{datetime_context}

{conversation_info}

User's Message: "{user_message}"
Data Mode: {data_mode.upper()}

{property_summary}

INSTRUCTIONS:
1. If the user asks for properties with specific features (pool, gym, etc.), analyze the available properties above
2. If you find matching properties, mention them specifically by address and key details
3. If no exact matches, suggest similar alternatives from the available properties
4. If the user is just starting their search, help them define criteria and show what's available
5. Keep responses concise but informative (3-5 sentences)
6. Use appropriate emojis to make responses engaging
7. Always end with a helpful question or suggestion to move the search forward
8. Be professional but friendly and conversational
9. IMPORTANT: If this is NOT the first message, do NOT greet the user again

SEARCH STRATEGY:
- For specific requests (like "pool"), look for properties that might have that feature
- For general requests, show a variety of options with different features and price points
- Always encourage the user to be more specific about their needs
- Guide them toward viewing properties that match their criteria

Respond now as Alex, using the available property information to help with their search."""

            # Create PydanticAI agent using Groq
            try:
                agent = await create_pydantic_agent("search_agent")
            except Exception as setup_error:
                logger.error(f"Failed to create search agent: {setup_error}")
                raise
            
            # Enhanced Logfire tracing for LLM call
            with AgentExecutionContext("search_agent", "llm_inference") as llm_span:
                llm_start = time.time()
                try:
                    logger.info(f"DEBUG: About to call agent.run() with prompt length: {len(prompt)}")
                    
                    if llm_span:
                        llm_span.set_attributes({
                            "llm.model": settings.groq.default_model,
                            "llm.prompt_length": len(prompt),
                            "llm.provider": "Groq",
                            "llm.agent": "search_agent"
                        })
                    
                    response = await agent.run(prompt)
                    llm_duration = time.time() - llm_start
                    logger.info(f"Groq model successful in {llm_duration:.2f}s")

                    if llm_span:
                        llm_span.set_attributes({
                            "llm.success": True,
                            "llm.duration_seconds": llm_duration,
                            "llm.response_length": len(str(response.output)) if response.output else 0
                        })
                except Exception as primary_error:
                    llm_duration = time.time() - llm_start
                    error_msg = str(primary_error)
                    logger.error(f"Groq model failed after {llm_duration:.2f}s: {error_msg}")

                    if llm_span:
                        llm_span.set_attributes({
                            "llm.success": False,
                            "llm.error": error_msg,
                            "llm.duration_seconds": llm_duration,
                            "llm.fallback_required": True
                        })

                    # Log error to Logfire
                    log_error(primary_error, context={
                        "agent": "search_agent",
                        "model": settings.groq.default_model,
                        "operation": "llm_inference",
                        "duration": llm_duration
                    })

                    logger.info("Trying Ollama fallback...")

                    # Use Ollama fallback
                    fallback_response = await generate_intelligent_fallback(
                        "search_agent", user_message,
                        state.get("context", {}).get("property_context", {}), "mock"
                    )
                    return {"messages": [AIMessage(content=fallback_response)]}
            
            log_api_call(
                api_name="Groq",
                endpoint="/chat/completions",
                method="POST",
                status_code=200,
                duration=llm_duration
            )
            
            # Check if response is too short or truncated
            response_content = str(response.output)
            if len(response_content.strip()) < 10:
                logger.warning(f"⚠️ Search response too short ({len(response_content)} chars): '{response_content}'")
                # Try with a simpler prompt with datetime context
                datetime_context = format_datetime_context_for_agent()
                simple_prompt = f"""You are Alex, a real estate search specialist. A user said: "{user_message}"

{datetime_context}

Respond helpfully about property search in 2-3 sentences. Be friendly and ask what they're looking for."""
                
                retry_response = await agent.run(simple_prompt)
                retry_content = str(retry_response.output)
                if len(retry_content.strip()) > len(response_content.strip()):
                    response_content = retry_content
                    logger.info(f"SUCCESS Search retry successful: {len(response_content)} chars")
            
            # Log da resposta bem-sucedida
            duration = time.time() - start_time
            log_agent_action(
                agent_name="search_agent",
                action="llm_response_success",
                details={
                    "response_length": len(response_content),
                    "properties_found": len(available_properties),
                    "duration_seconds": duration
                }
            )
            
            logger.info(f"SUCCESS PydanticAI search agent response: {len(response_content)} chars")
            logger.info(f"PREVIEW Search response preview: {response_content[:100]}...")
            return {"messages": [AIMessage(content=response_content)]}

        except Exception as e:
            logger.error(f"ERROR PydanticAI call failed for search agent: {e}")
            log_error(e, context={"agent": "search_agent", "operation": "llm_call"})
            
            logger.info("RETRY Falling back to Ollama intelligent response generator")
            fallback_response = await generate_intelligent_fallback("search_agent", user_message, state.get("context", {}).get("property_context", {}), "mock")
            
            # Log do fallback por erro
            log_agent_action(
                agent_name="search_agent",
                action="ollama_fallback_response",
                details={"reason": "llm_error", "error": str(e), "response_length": len(fallback_response)}
            )
            
            return {"messages": [AIMessage(content=fallback_response)]}


async def property_agent_node(state: SwarmState) -> dict:
    """Nó do agente de propriedades: analisa uma propriedade específica usando PydanticAI com Groq."""
    logger = get_logger("property_agent")

    # Logfire tracing
    with AgentExecutionContext("property_agent", "property_analysis") as logfire_span:
        
        # 🔥 CORREÇÃO: Acessar mensagens corretamente no LangGraph
        messages = state.messages if hasattr(state, 'messages') else state.get("messages", [])
        if not messages:
            logger.warning("No messages in state for property_agent")
            return {"messages": [AIMessage(content="Olá! Sou Emma, especialista em análise de propriedades. Como posso ajudá-lo?")]}
        
        # Extrair mensagem do usuário (compatível com dict e LangChain messages)
        last_message = messages[-1]
        if hasattr(last_message, 'content'):
            user_message = last_message.content
        else:
            user_message = last_message.get("content", "")
        
        context = state.get("context", {})
        property_context = context.get("property_context", {})
        data_mode = context.get("data_mode", "mock")  # Get data mode from context
        
        settings = get_settings()
        groq_key = settings.groq.api_key

        # Verificar chave Groq
        if not groq_key or groq_key.strip() == "":
            logger.warning("No valid Groq key found. Using Ollama fallback.")
            fallback_response = await generate_intelligent_fallback("property_agent", user_message, property_context, data_mode)
            return {"messages": [AIMessage(content=fallback_response)]}

        try:
            logger.info(f"Using Groq property agent in {data_mode.upper()} mode: '{user_message[:50]}...'")
            logger.info(f"PROPERTY Property context: {property_context.get('formattedAddress', 'No address') if property_context else 'No property context'}")
            
            # Create property details string
            property_details = ""
            if property_context:
                # Format price safely
                price_value = property_context.get('price', 'N/A')
                if isinstance(price_value, (int, float)):
                    price_formatted = f"${price_value:,}/month"
                else:
                    price_formatted = f"${price_value}/month"
                
                # Format square footage safely
                sqft_value = property_context.get('squareFootage', 'N/A')
                if isinstance(sqft_value, (int, float)):
                    sqft_formatted = f"{sqft_value:,} sq ft"
                else:
                    sqft_formatted = f"{sqft_value} sq ft"
                
                # Extract listing agent and office information
                listing_agent = property_context.get('listingAgent', {})
                listing_office = property_context.get('listingOffice', {})
                
                agent_info = ""
                if listing_agent and isinstance(listing_agent, dict):
                    agent_name = listing_agent.get('name', 'N/A')
                    agent_phone = listing_agent.get('phone', 'N/A')
                    agent_email = listing_agent.get('email', 'N/A')
                    agent_info = f"""
LISTING AGENT:
• Name: {agent_name}
• Phone: {agent_phone}
• Email: {agent_email}"""

                office_info = ""
                if listing_office and isinstance(listing_office, dict):
                    office_name = listing_office.get('name', 'N/A')
                    office_phone = listing_office.get('phone', 'N/A')
                    office_email = listing_office.get('email', 'N/A')
                    office_info = f"""

LISTING OFFICE:
• Company: {office_name}
• Phone: {office_phone}
• Email: {office_email}"""

                property_details = f"""
PROPERTY DETAILS:
• Address: {property_context.get('formattedAddress', 'N/A')}
• Price: {price_formatted}
• Bedrooms: {property_context.get('bedrooms', 'N/A')}
• Bathrooms: {property_context.get('bathrooms', 'N/A')}
• Square Footage: {sqft_formatted}
• Property Type: {property_context.get('propertyType', 'N/A')}
• Year Built: {property_context.get('yearBuilt', 'N/A')}
• City: {property_context.get('city', 'N/A')}, {property_context.get('state', 'N/A')}
• Days on Market: {property_context.get('daysOnMarket', 'N/A')}
• MLS Number: {property_context.get('mlsNumber', 'N/A')}{agent_info}{office_info}
"""
            else:
                property_details = "No specific property information available."

            # 🔥 Add conversation context awareness
            is_first_message = len(messages) <= 1
            conversation_info = ""
            if not is_first_message:
                conversation_info = f"""
CONVERSATION CONTEXT:
- This is NOT the first message in the conversation (message #{len(messages)})
- Continue the conversation naturally without greeting again
- Build on previous context and maintain conversation flow
"""
            else:
                conversation_info = """
CONVERSATION CONTEXT:
- This is the first message in the conversation
- You can start with a greeting and introduction
"""

            # Create comprehensive prompt with property context and datetime
            datetime_context = format_datetime_context_for_agent()
            prompt = f"""You are Emma, a professional real estate property expert. You provide clear, objective, and helpful information about properties while being conversational and engaging.

{datetime_context}

{conversation_info}

{property_details}

User's Question: "{user_message}"

INSTRUCTIONS:
1. If the user asks about price/rent/cost, provide the exact price from the property details above
2. If the user asks about listing agent contact information, provide the exact details from the LISTING AGENT section above
3. If the user wants to schedule a visit/viewing/tour, inform them you'll connect them with Mike, the scheduling specialist
4. Always reference the specific property address when answering
5. Be objective and informative but maintain a friendly, professional tone
6. Use appropriate emojis to make responses engaging
7. Keep responses concise but comprehensive (2-4 sentences)
8. Always end with a question or suggestion to continue the conversation
9. If asked about aspects not in the property details, acknowledge what you don't know but offer related helpful information
10. IMPORTANT: If this is NOT the first message, do NOT greet the user again

CONVERSATION FLOW:
- Never ask the user to provide information you already have
- Always use the property details provided above
- Encourage questions about other aspects (neighborhood, amenities, scheduling visits)
- Maintain conversation momentum unless the user clearly indicates they want to end

Respond now as Emma, using the property information provided above to answer the user's question directly and professionally."""

            # Create PydanticAI agent using Groq
            agent = await create_pydantic_agent("property_agent")
            
            # Execute the analysis
            llm_start = time.time()
            logger.info(f"DEBUG: About to call property agent with prompt length: {len(prompt)}")
            
            try:
                response = await agent.run(prompt)
                llm_duration = time.time() - llm_start
                logger.info(f"SUCCESS Property agent successful in {llm_duration:.2f}s")
                
                content = str(response.output)
                
                # Check if response is too short or truncated
                if len(content.strip()) < 10:
                    logger.warning(f"WARNING Response too short ({len(content)} chars): '{content}'")
                    # Try with simpler prompt with datetime context
                    datetime_context = format_datetime_context_for_agent()
                    simple_prompt = f"""You are Emma, a real estate property expert. A user asked: "{user_message}"

{datetime_context}
                    
About this property: {property_context.get('formattedAddress', 'Address available')}
Price: ${property_context.get('price', 'N/A')}/month

Respond helpfully in 2-3 sentences."""
                    
                    retry_response = await agent.run(simple_prompt)
                    retry_content = str(retry_response.output)
                    if len(retry_content.strip()) > len(content.strip()):
                        content = retry_content
                        logger.info(f"SUCCESS Retry with simpler prompt successful: {len(content)} chars")
                
                log_api_call(
                    api_name="Groq",
                    endpoint="/chat/completions",
                    method="POST",
                    status_code=200,
                    duration=llm_duration
                )

                logger.info(f"Property agent successful: {len(content)} chars")
                return {"messages": [AIMessage(content=content)]}

            except Exception as primary_error:
                llm_duration = time.time() - llm_start
                error_msg = str(primary_error)
                logger.error(f"Property agent failed after {llm_duration:.2f}s: {error_msg}")

                log_error(primary_error, context={
                    "agent": "property_agent",
                    "operation": "llm_inference",
                    "duration": llm_duration
                })

                # Use Ollama fallback
                logger.info("Using Ollama fallback for property analysis")
                fallback_response = await generate_intelligent_fallback("property_agent", user_message, property_context, data_mode)
                return {"messages": [AIMessage(content=fallback_response)]}
                
        except Exception as e:
            logger.error(f"Property agent failed: {e}")
            fallback_response = await generate_intelligent_fallback("property_agent", user_message, property_context, data_mode)
            return {"messages": [AIMessage(content=fallback_response)]}


async def scheduling_agent_node(state: SwarmState) -> dict:
    """Nó do agente de agendamento: agenda visitas usando PydanticAI com Groq."""
    logger = get_logger("scheduling_agent")

    # Logfire tracing
    with AgentExecutionContext("scheduling_agent", "appointment_scheduling") as logfire_span:

        # Acessar mensagens corretamente no LangGraph
        messages = state.messages if hasattr(state, 'messages') else state.get("messages", [])
        if not messages:
            logger.warning("No messages in state for scheduling_agent")
            return {"messages": [AIMessage(content="Olá! Sou Mike, especialista em agendamento. Como posso ajudá-lo?")]}

        # Extrair mensagem do usuário
        last_message = messages[-1]
        if hasattr(last_message, 'content'):
            user_message = last_message.content
        else:
            user_message = last_message.get("content", "")

        context = state.get("context", {})
        property_context = context.get("property_context", {})
        data_mode = context.get("data_mode", "mock")

        settings = get_settings()
        groq_key = settings.groq.api_key

        # Verificar chave Groq
        if not groq_key or groq_key.strip() == "":
            logger.warning("No valid Groq key found. Using Ollama fallback.")
            fallback_response = await generate_intelligent_fallback("scheduling_agent", user_message, property_context, data_mode)
            return {"messages": [AIMessage(content=fallback_response)]}

        try:
            logger.info(f"Using Groq scheduling agent in {data_mode.upper()} mode: '{user_message[:50]}...'")

            # Create property details string for scheduling context
            property_details = ""
            if property_context:
                # Format price safely
                price_value = property_context.get('price', 'N/A')
                if isinstance(price_value, (int, float)):
                    price_formatted = f"${price_value:,}/month"
                else:
                    price_formatted = f"${price_value}/month"

                property_details = f"""
PROPERTY FOR VIEWING:
• Address: {property_context.get('formattedAddress', 'N/A')}
• Price: {price_formatted}
• Type: {property_context.get('propertyType', 'N/A')}
• Bedrooms: {property_context.get('bedrooms', 'N/A')} | Bathrooms: {property_context.get('bathrooms', 'N/A')}
"""
            else:
                property_details = "Property details will be confirmed upon scheduling."

            # Conversation context awareness
            is_first_message = len(messages) <= 1
            if not is_first_message:
                conversation_info = f"""
CONVERSATION CONTEXT:
- This is message #{len(messages)} in the conversation
- Continue naturally without greeting again
"""
            else:
                conversation_info = """
CONVERSATION CONTEXT:
- This is the first message
- You can start with a greeting
"""

            # Create scheduling prompt with datetime context
            scheduling_datetime_context = get_scheduling_context_for_agent()
            prompt = f"""You are Mike, a professional scheduling assistant for real estate property viewings.

{scheduling_datetime_context}

{conversation_info}

{property_details}

User's Request: "{user_message}"

INSTRUCTIONS:
1. Reference the property address when discussing viewings
2. Use the datetime context above for accurate dates
3. Provide 2-3 specific time slots within the next 3-5 days
4. Mention what to bring (ID, proof of income if applicable)
5. Specify viewing duration (30-45 minutes)
6. Be professional but friendly
7. End with a clear next step or confirmation request

AVAILABLE TIMES:
- Weekdays: 10:00 AM, 2:00 PM, 4:00 PM
- Weekends: 9:00 AM, 11:00 AM, 1:00 PM, 3:00 PM

Respond now as Mike, helping them schedule their property viewing."""

            # Create PydanticAI agent using Groq
            agent = await create_pydantic_agent("scheduling_agent")

            # Execute the scheduling analysis
            llm_start = time.time()
            response = await agent.run(prompt)
            llm_duration = time.time() - llm_start
            logger.info(f"Scheduling agent successful in {llm_duration:.2f}s")

            content = str(response.output)

            log_api_call(
                api_name="Groq",
                endpoint="/chat/completions",
                method="POST",
                status_code=200,
                duration=llm_duration
            )

            return {"messages": [AIMessage(content=content)]}

        except Exception as e:
            logger.error(f"Scheduling agent failed: {e}")
            log_error(e, context={
                "agent": "scheduling_agent",
                "operation": "llm_inference"
            })
            fallback_response = await generate_intelligent_fallback("scheduling_agent", user_message, property_context, data_mode)
            return {"messages": [AIMessage(content=fallback_response)]}


def route_message(state: SwarmState) -> Literal["search_agent", "property_agent", "scheduling_agent", END]:
    """
    Roteador inteligente baseado no contexto e histórico com Logfire tracing.
    
    Determina qual agente deve processar a próxima mensagem.
    """
    # Logfire tracing for routing decisions
    with HandoffContext("router", "routing_decision", "message_analysis") as route_span:
        messages = state.get("messages", [])
        current_agent = state.get("current_agent", "property_agent")
        context = state.get("context", {})
        
        # Log routing context to Logfire
        if route_span:
            route_span.set_attributes({
                "router.messages_count": len(messages),
                "router.current_agent": current_agent,
                "router.has_property_context": bool(context.get("property_context"))
            })
        
        # Se não há mensagens, começar com property_agent se temos contexto de propriedade
        if not messages:
            target_agent = "property_agent" if context.get("property_context") else "search_agent"
            
            if route_span:
                route_span.set_attributes({
                    "router.decision": target_agent,
                    "router.reason": "no_messages",
                    "router.has_context": bool(context.get("property_context"))
                })
            
            log_handoff(
                from_agent="router",
                to_agent=target_agent,
                reason="initial_routing_no_messages",
                context={"has_property_context": bool(context.get("property_context"))}
            )
            
            return target_agent
        
        last_message = messages[-1]
        
        # Extract content from LangChain message or dict
        if hasattr(last_message, 'content'):
            user_content = last_message.content.lower()
        else:
            user_content = last_message.get("content", "").lower()
        
        # Log para debug
        logger = get_logger("swarm_router")
        logger.info(f"ROUTE Routing message: '{user_content[:100]}...'")
        
        if route_span:
            route_span.set_attributes({
                "router.message_content_length": len(user_content),
                "router.message_preview": user_content[:100]
            })
        
        # 🔥 COMPLETELY REWRITTEN ROUTING LOGIC - Intent-based detection
        
        # 1. SCHEDULING INTENT - Clear scheduling/viewing requests (FIXED: More specific patterns)
        scheduling_keywords = [
            # Direct scheduling requests with full context
            "can i visit", "want to visit", "like to visit", "schedule a visit", "book a visit",
            "i want to see it", "can i see it", "want to see the property", "want to see this property",
            "schedule for", "book for", "schedule an appointment", "book an appointment",
            "schedule a tour", "book a tour", "view the property", "tour the property",
            
            # Time-specific scheduling requests
            "visit tomorrow", "see tomorrow", "visit today", "see today", "visit this week", 
            "visit next week", "tomorrow at", "today at", "this week at", "next week at",
            "available times", "when can", "what time", "time slots", "calendar",
            "at 3pm", "at 2 pm", "in the morning", "in the afternoon", "in the evening",
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
        ]
        
        # 2. SEARCH INTENT - Looking for properties to find/discover
        search_keywords = [
            # Primary search intents - MOST IMPORTANT
            "i need a place", "need a place", "looking for", "looking for a", "find me",
            "search", "want a", "need an", "show me properties", "find properties",
            "i want", "i need", "something nice", "something in", "place to live",
            
            # Search criteria specification
            "bedrooms", "bedroom", "bathrooms", "bathroom", "budget", "around $", "under $",
            "2 bedrooms", "3 bedrooms", "1 bedroom", "studio", "house", "apartment",
            "in miami", "in downtown", "near beach", "south beach", "brickell",
            
            # Feature searches
            "with pool", "with gym", "with parking", "pet friendly", "furnished",
            "ocean view", "waterfront", "balcony", "garden", "terrace",
            
            # Alternative/comparison searches - CRITICAL: Added "bigger", "larger", "see" patterns
            "different", "other properties", "alternatives", "similar", "what else",
            "more options", "something else", "cheaper", "better", "bigger", "larger",
            "want to see a", "want to see something", "do you have", "show me", "any other"
        ]
        
        # 3. PROPERTY ANALYSIS INTENT - About specific current property
        property_keywords = [
            # Current property references
            "this property", "this apartment", "this house", "this unit", "this place",
            "tell me about", "more about", "details about", "information about",
            
            # Property-specific questions when there's property context
            "how much", "what's the rent", "what's the price", "how big", "size",
            "square feet", "sq ft", "year built", "when built", "condition",
            "features", "amenities", "what's included", "utilities",
            
            # Only when referring to current property
            "the first one", "the second one", "that property", "it"
        ]
        
        # 🔥 NEW PRIORITY ROUTING LOGIC - Intent overrides everything
        
        # STEP 1: Check for SCHEDULING intent (highest priority when detected)
        scheduling_matches = [kw for kw in scheduling_keywords if kw in user_content]
        if scheduling_matches:
            target_agent = "scheduling_agent"
            reason = f"scheduling_intent_matched_{scheduling_matches[0]}"
            
            logger.info(f"SCHEDULE Routing to scheduling_agent (matched: {scheduling_matches[0]})")
            
            if route_span:
                route_span.set_attributes({
                    "router.decision": target_agent,
                    "router.reason": reason,
                    "router.matched_keyword": scheduling_matches[0],
                    "router.intent": "scheduling"
                })
            
            log_handoff(
                from_agent=current_agent,
                to_agent=target_agent,
                reason=reason,
                context={"matched_keywords": scheduling_matches[:3]}
            )
            
            return target_agent
        
        # STEP 2: Check for SEARCH intent (new properties, criteria, locations)
        search_matches = [kw for kw in search_keywords if kw in user_content]
        if search_matches:
            target_agent = "search_agent"
            reason = f"search_intent_matched_{search_matches[0]}"
            
            logger.info(f"SEARCH Routing to search_agent (matched: {search_matches[0]})")
            
            if route_span:
                route_span.set_attributes({
                    "router.decision": target_agent,
                    "router.reason": reason,
                    "router.matched_keyword": search_matches[0],
                    "router.intent": "search"
                })
            
            log_handoff(
                from_agent=current_agent,
                to_agent=target_agent,
                reason=reason,
                context={"matched_keywords": search_matches[:3]}
            )
            
            return target_agent
        
        # STEP 3: Check for PROPERTY ANALYSIS intent (about current property)
        property_matches = [kw for kw in property_keywords if kw in user_content]
        if property_matches and context.get("property_context"):
            target_agent = "property_agent"
            reason = f"property_intent_matched_{property_matches[0]}"
            
            logger.info(f"PROPERTY Routing to property_agent (matched: {property_matches[0]})")
            
            if route_span:
                route_span.set_attributes({
                    "router.decision": target_agent,
                    "router.reason": reason,
                    "router.matched_keyword": property_matches[0],
                    "router.intent": "property_analysis"
                })
            
            log_handoff(
                from_agent=current_agent,
                to_agent=target_agent,
                reason=reason,
                context={"matched_keywords": property_matches[:3]}
            )
            
            return target_agent
        
        # STEP 4: Context-based fallback
        if context.get("property_context"):
            # If we have property context but no clear intent, stay with property agent
            target_agent = "property_agent"
            reason = "fallback_with_property_context"
            
            logger.info(f"PROPERTY Routing to property_agent (fallback with property context)")
            
            if route_span:
                route_span.set_attributes({
                    "router.decision": target_agent,
                    "router.reason": reason,
                    "router.intent": "fallback_property"
                })
            
            log_handoff(
                from_agent=current_agent,
                to_agent=target_agent,
                reason=reason,
                context={"has_property_context": True}
            )
            
            return target_agent
        else:
            # No property context, default to search to help find properties
            target_agent = "search_agent"
            reason = "fallback_no_property_context"
            
            logger.info(f"SEARCH Routing to search_agent (fallback - no property context)")
            
            if route_span:
                route_span.set_attributes({
                    "router.decision": target_agent,
                    "router.reason": reason,
                    "router.intent": "fallback_search"
                })
            
            log_handoff(
                from_agent=current_agent,
                to_agent=target_agent,
                reason=reason,
                context={"has_property_context": False}
            )
            
            return target_agent


class SwarmOrchestrator:
    """
    Orquestrador LangGraph-Swarm com Agentes Inteligentes.
    
    Coordena agentes especializados que usam lógica contextual através de handoffs diretos,
    sem supervisor central. Inclui sistema de memória de curto e longo prazo.
    """
    
    def __init__(self):
        self.logger = get_logger("swarm_orchestrator")
        self.settings = get_settings()
        
        # 🔥 NOVO: Sistema de memória
        self.checkpointer = MemorySaver()  # Memória de curto prazo (thread-scoped)
        self.store = InMemoryStore()  # Memória de longo prazo (cross-thread)
        
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Construir grafo LangGraph-Swarm com agentes inteligentes e memória."""
        
        # Criar grafo com estado customizado
        graph = StateGraph(SwarmState)
        
        # Adicionar nós dos agentes inteligentes
        graph.add_node("search_agent", search_agent_node)
        graph.add_node("property_agent", property_agent_node)  
        graph.add_node("scheduling_agent", scheduling_agent_node)
        
        # Usar roteamento condicional baseado na mensagem
        graph.add_conditional_edges(
            START,
            route_message,
            {
                "search_agent": "search_agent",
                "property_agent": "property_agent", 
                "scheduling_agent": "scheduling_agent"
            }
        )
        
        # Cada agente termina após processar - sem loops
        graph.add_edge("search_agent", END)
        graph.add_edge("property_agent", END)
        graph.add_edge("scheduling_agent", END)
        
        # 🔥 NOVO: Compilar grafo com sistema de memória
        compiled_graph = graph.compile(
            checkpointer=self.checkpointer,  # Memória de curto prazo
            store=self.store  # Memória de longo prazo
        )
        
        self.logger.info("LangGraph-Swarm with intelligent routing and memory system built successfully")
        return compiled_graph
    
    async def process_message(self, message: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processar mensagem através do swarm com agentes inteligentes, memória e supervisão.

        O Supervisor avalia TODA resposta antes de enviar ao usuário.
        O Manager fornece insights em tempo real ao Supervisor.

        Args:
            message: Mensagem do usuário
            config: Configuração com thread_id para memória persistente

        Returns:
            Resposta processada e validada pelo Supervisor
        """
        start_time = time.time()

        try:
            self.logger.info(f"Processing message with intelligent agents: {message}")

            # Usar config com thread_id para memória persistente
            if config:
                self.logger.info(f"Using persistent memory with thread_id: {config.get('configurable', {}).get('thread_id')}")
                result = await self.graph.ainvoke(message, config)
            else:
                import uuid
                default_config = {
                    "configurable": {
                        "thread_id": f"default-{uuid.uuid4().hex[:8]}"
                    }
                }
                result = await self.graph.ainvoke(message, default_config)

            # === SUPERVISOR EVALUATION ===
            # Get the agent's response
            agent_response = ""
            if result.get("messages"):
                last_msg = result["messages"][-1]
                agent_response = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)

            # Get user query from input
            user_query = ""
            if message.get("messages"):
                first_msg = message["messages"][0]
                user_query = first_msg.content if hasattr(first_msg, 'content') else str(first_msg.get("content", ""))

            # Get Manager insights
            manager = get_manager()
            manager_recommendations = await manager.get_supervisor_recommendations()
            manager_insights = [r.message for r in manager_recommendations[:3]]

            # Supervisor evaluates the response
            supervisor = get_supervisor()

            # Get manager insights for supervisor
            if manager_insights:
                await supervisor.get_manager_insights(manager_insights)

            evaluation = await supervisor.evaluate_response(
                agent_name=result.get("current_agent", "unknown"),
                response=agent_response,
                user_query=user_query,
                context={
                    "property_context": result.get("context", {}).get("property_context"),
                    "conversation_length": len(result.get("messages", []))
                }
            )

            self.logger.info(f"Supervisor decision: {evaluation.decision.value} (score: {evaluation.score:.2f})")

            # Handle supervisor decision
            if evaluation.decision == SupervisorDecision.REVISE:
                self.logger.warning(f"Supervisor requested revision. Issues: {evaluation.issues}")
                # For now, we still return the response but log the issues
                # In a production system, we could loop back to the agent
                log_agent_action(
                    agent_name="supervisor",
                    action="revision_requested",
                    details={
                        "issues": evaluation.issues,
                        "score": evaluation.score
                    }
                )
            elif evaluation.decision == SupervisorDecision.ESCALATE:
                self.logger.error(f"Supervisor escalated. Reason: {evaluation.reasoning}")
                log_agent_action(
                    agent_name="supervisor",
                    action="escalated",
                    details={"reasoning": evaluation.reasoning}
                )

            # Add supervisor metadata to result
            result["supervisor_evaluation"] = {
                "decision": evaluation.decision.value,
                "score": evaluation.score,
                "issues": evaluation.issues
            }

            # Calculate execution time
            execution_time = time.time() - start_time
            log_performance("swarm_message_processing", execution_time)

            self.logger.info(f"SwarmOrchestrator completed in {execution_time:.2f}s (Supervisor: {evaluation.decision.value})")
            return result

        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            raise
    
    async def process_stream(self, message: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """
        Processar mensagem com streaming.
        
        Args:
            message: Mensagem do usuário
            
        Yields:
            Chunks da resposta em tempo real
        """
        try:
            self.logger.info(f"STREAM Starting astream with message: {message}")
            
            chunk_count = 0
            async for chunk in self.graph.astream(message):
                chunk_count += 1
                self.logger.info(f"CHUNK Generated chunk #{chunk_count}: {chunk}")
                yield chunk
                
            self.logger.info(f"SUCCESS Streaming completed - {chunk_count} chunks generated")
                
        except Exception as e:
            self.logger.error(f"Error in streaming: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            yield {"error": str(e)}
    
    def get_graph_visualization(self) -> str:
        """Obter visualização do grafo (para debug)."""
        try:
            return self.graph.get_graph().draw_mermaid()
        except Exception as e:
            self.logger.warning(f"Could not generate graph visualization: {e}")
            return "Graph visualization not available"


def filter_properties_by_user_intent(user_message: str, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filtrar propriedades baseadas na intenção do usuário.
    
    Args:
        user_message: Mensagem do usuário
        properties: Lista de propriedades disponíveis
        
    Returns:
        Lista de propriedades filtradas
    """
    if not properties:
        return []
    
    user_lower = user_message.lower()
    filtered = []
    
    # Extrair critérios da mensagem do usuário
    criteria = {
        'min_bedrooms': None,
        'max_bedrooms': None,
        'min_bathrooms': None,
        'max_bathrooms': None,
        'min_price': None,
        'max_price': None,
        'amenities': [],
        'property_type': None,
        'location': None
    }
    
    # Detectar número de quartos
    if 'bedroom' in user_lower or 'br' in user_lower:
        import re
        bedroom_matches = re.findall(r'(\d+)\s*(?:bedroom|br)', user_lower)
        if bedroom_matches:
            criteria['min_bedrooms'] = int(bedroom_matches[0])
            if 'more than' in user_lower or 'at least' in user_lower:
                criteria['min_bedrooms'] = int(bedroom_matches[0])
            elif 'exactly' in user_lower or 'with' in user_lower:
                criteria['min_bedrooms'] = int(bedroom_matches[0])
                criteria['max_bedrooms'] = int(bedroom_matches[0])
    
    # Detectar número de banheiros
    if 'bathroom' in user_lower or 'bath' in user_lower:
        import re
        bathroom_matches = re.findall(r'(\d+)\s*(?:bathroom|bath)', user_lower)
        if bathroom_matches:
            criteria['min_bathrooms'] = int(bathroom_matches[0])
            if 'exactly' in user_lower or 'with' in user_lower:
                criteria['max_bathrooms'] = int(bathroom_matches[0])
    
    # Detectar amenidades
    amenity_keywords = {
        'pool': ['pool', 'swimming'],
        'gym': ['gym', 'fitness'],
        'parking': ['parking', 'garage'],
        'balcony': ['balcony'],
        'garden': ['garden', 'yard'],
        'terrace': ['terrace', 'deck'],
        'ocean': ['ocean', 'sea', 'beach'],
        'waterfront': ['waterfront', 'water view']
    }
    
    for amenity, keywords in amenity_keywords.items():
        if any(keyword in user_lower for keyword in keywords):
            criteria['amenities'].append(amenity)
    
    # Detectar tipo de propriedade
    if 'house' in user_lower:
        criteria['property_type'] = 'house'
    elif 'apartment' in user_lower or 'apt' in user_lower:
        criteria['property_type'] = 'apartment'
    elif 'condo' in user_lower:
        criteria['property_type'] = 'condo'
    elif 'studio' in user_lower:
        criteria['property_type'] = 'studio'
    
    # Detectar localização
    location_keywords = ['miami', 'downtown', 'beach', 'brickell', 'coral gables', 'aventura']
    for location in location_keywords:
        if location in user_lower:
            criteria['location'] = location
    
    # Aplicar filtros
    for prop in properties:
        matches = True
        
        # Filtrar por quartos
        if criteria['min_bedrooms'] is not None:
            if prop.get('bedrooms', 0) < criteria['min_bedrooms']:
                matches = False
        if criteria['max_bedrooms'] is not None:
            if prop.get('bedrooms', 0) > criteria['max_bedrooms']:
                matches = False
        
        # Filtrar por banheiros
        if criteria['min_bathrooms'] is not None:
            if prop.get('bathrooms', 0) < criteria['min_bathrooms']:
                matches = False
        if criteria['max_bathrooms'] is not None:
            if prop.get('bathrooms', 0) > criteria['max_bathrooms']:
                matches = False
        
        # Filtrar por localização
        if criteria['location']:
            address = prop.get('formattedAddress', '').lower()
            if criteria['location'] not in address:
                matches = False
        
        # Filtrar por amenidades (simulado - em produção seria baseado em dados reais)
        if criteria['amenities']:
            # Para demonstração, vamos assumir que algumas propriedades têm amenidades
            prop_amenities = []
            if prop.get('price', 0) > 2000:  # Propriedades mais caras tendem a ter mais amenidades
                prop_amenities.extend(['pool', 'gym', 'parking'])
            if prop.get('squareFootage', 0) > 1000:
                prop_amenities.extend(['balcony', 'garden'])
            if 'ocean' in prop.get('formattedAddress', '').lower() or 'bay' in prop.get('formattedAddress', '').lower():
                prop_amenities.extend(['ocean', 'waterfront'])
            
            # Verificar se pelo menos uma amenidade solicitada está presente
            if not any(amenity in prop_amenities for amenity in criteria['amenities']):
                matches = False
        
        if matches:
            filtered.append(prop)
    
    return filtered


def create_intelligent_property_summary(user_message: str, filtered_properties: List[Dict[str, Any]], all_properties: List[Dict[str, Any]]) -> str:
    """
    Criar resumo inteligente das propriedades baseado na intenção do usuário.
    
    Args:
        user_message: Mensagem do usuário
        filtered_properties: Propriedades filtradas
        all_properties: Todas as propriedades disponíveis
        
    Returns:
        Resumo formatado das propriedades
    """
    if not all_properties:
        return "\n\nNo property data available at the moment."
    
    user_lower = user_message.lower()
    
    # Se há propriedades filtradas, mostrar elas primeiro
    if filtered_properties:
        summary = f"\n\nFILTER PROPERTIES MATCHING YOUR CRITERIA ({len(filtered_properties)} found):\n"
        for i, prop in enumerate(filtered_properties[:5], 1):  # Mostrar até 5
            price = prop.get('price', 0)
            bedrooms = prop.get('bedrooms', 0)
            bathrooms = prop.get('bathrooms', 0)
            sqft = prop.get('squareFootage', 0)
            address = prop.get('formattedAddress', 'N/A')
            
            summary += f"{i}. PROPERTY {address}\n"
            summary += f"   💰 ${price:,}/month | 🛏️ {bedrooms}BR/🚿{bathrooms}BA | 📐 {sqft:,} sq ft\n"
        
        if len(filtered_properties) > 5:
            summary += f"\n... and {len(filtered_properties) - 5} more matching properties available!\n"
        
        # Mostrar algumas alternativas se há mais propriedades
        if len(all_properties) > len(filtered_properties):
            summary += f"\nSEARCH OTHER AVAILABLE OPTIONS ({len(all_properties) - len(filtered_properties)} more):\n"
            other_props = [p for p in all_properties if p not in filtered_properties][:3]
            for i, prop in enumerate(other_props, 1):
                price = prop.get('price', 0)
                bedrooms = prop.get('bedrooms', 0)
                bathrooms = prop.get('bathrooms', 0)
                address = prop.get('formattedAddress', 'N/A')
                summary += f"{i}. PROPERTY {address} - ${price:,}/month, {bedrooms}BR/{bathrooms}BA\n"
    
    else:
        # Nenhuma propriedade atende aos critérios específicos
        summary = f"\n\nSEARCH NO EXACT MATCHES FOUND for your specific criteria.\n"
        summary += f"📋 AVAILABLE PROPERTIES ({len(all_properties)} total):\n"
        
        # Mostrar uma variedade de propriedades
        sample_properties = all_properties[:5]
        for i, prop in enumerate(sample_properties, 1):
            price = prop.get('price', 0)
            bedrooms = prop.get('bedrooms', 0)
            bathrooms = prop.get('bathrooms', 0)
            sqft = prop.get('squareFootage', 0)
            address = prop.get('formattedAddress', 'N/A')
            
            summary += f"{i}. PROPERTY {address}\n"
            summary += f"   💰 ${price:,}/month | 🛏️ {bedrooms}BR/🚿{bathrooms}BA | 📐 {sqft:,} sq ft\n"
        
        if len(all_properties) > 5:
            summary += f"\n... and {len(all_properties) - 5} more properties available!\n"
        
        summary += f"\n💡 Try adjusting your criteria or let me know what specific features you're looking for!"
    
    return summary


# Instância global do orquestrador
_swarm_orchestrator = None

def get_swarm_orchestrator() -> SwarmOrchestrator:
    """Obter instância singleton do SwarmOrchestrator."""
    global _swarm_orchestrator
    if _swarm_orchestrator is None:
        _swarm_orchestrator = SwarmOrchestrator()
    return _swarm_orchestrator

def create_swarm_graph():
    """Criar e retornar o grafo Swarm para testes."""
    orchestrator = get_swarm_orchestrator()
    return orchestrator.graph 