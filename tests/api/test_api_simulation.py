#!/usr/bin/env python3
"""
Teste que simula exatamente o fluxo do API server
"""

import asyncio
import traceback
from datetime import datetime

# Simular os modelos do API server
class AgentSession:
    def __init__(self, session_id: str, current_agent: str, property_id: str = None):
        self.session_id = session_id
        self.current_agent = current_agent
        self.property_id = property_id

class AgentResponse:
    def __init__(self, success: bool, message: str, agent_name: str, session_id: str, 
                 current_agent: str, suggested_actions=None, confidence=0.85, timestamp=None):
        self.success = success
        self.message = message
        self.agent_name = agent_name
        self.session_id = session_id
        self.current_agent = current_agent
        self.suggested_actions = suggested_actions or []
        self.confidence = confidence
        self.timestamp = timestamp or datetime.now().isoformat()
    
    def dict(self):
        return {
            "success": self.success,
            "message": self.message,
            "agent_name": self.agent_name,
            "session_id": self.session_id,
            "current_agent": self.current_agent,
            "suggested_actions": self.suggested_actions,
            "confidence": self.confidence,
            "timestamp": self.timestamp
        }

async def simulate_process_with_real_agent(message: str, session: AgentSession, data_mode: str = "mock") -> AgentResponse:
    """Simula exatamente a função process_with_real_agent do API server"""
    try:
        print(f"🤖 Processing with real SwarmOrchestrator in {data_mode.upper()} data mode: {message[:100]}...")
        
        # Import the SwarmOrchestrator when needed
        from app.orchestration.swarm import SwarmOrchestrator
        
        # Initialize the orchestrator
        orchestrator = SwarmOrchestrator()
        
        # Get property context if available
        property_context = None
        if session.property_id:
            # Simular contexto de propriedade
            property_context = {
                "formattedAddress": "2000 Nw 29th St, Apt 3, Miami, FL 33142",
                "price": 2100,
                "bedrooms": 2,
                "bathrooms": 1,
                "squareFootage": 1000
            }
            print(f"🏠 Found property context in {data_mode} mode: {property_context.get('formattedAddress', 'N/A')}")
        
        # Create comprehensive message format for the agent system
        agent_message = {
            "messages": [{"role": "user", "content": message}],
            "session_id": session.session_id,
            "current_agent": session.current_agent,
            "context": {
                "property_context": property_context,
                "source": "web_chat",
                "user_mode": session.current_agent,
                "language": "en",
                "data_mode": data_mode,
                "api_config": {
                    "mode": data_mode,
                    "use_real_api": data_mode == "real"
                }
            }
        }
        
        print(f"🔄 Sending to SwarmOrchestrator with agent: {session.current_agent}, data_mode: {data_mode}")
        
        # Process with the swarm
        result = await orchestrator.process_message(agent_message)
        
        print(f"✅ SwarmOrchestrator result: {type(result)}")
        
        # Extract response from swarm result
        response_content = f"I'm here to help! How can I assist you with this property? (Using {data_mode} data)"
        agent_name = "AI Assistant"
        current_agent = session.current_agent
        
        print(f"🔍 SwarmOrchestrator result type: {type(result)}")
        print(f"🔍 SwarmOrchestrator result keys: {list(result.keys()) if hasattr(result, 'keys') else 'No keys'}")
        
        if result:
            # Try to extract from messages
            if hasattr(result, 'get') and result.get("messages"):
                messages = result["messages"]
                print(f"🔍 Found {len(messages)} messages")
                if messages:
                    last_message = messages[-1]
                    print(f"🔍 Last message type: {type(last_message)}")
                    
                    # Handle LangChain AIMessage objects
                    if hasattr(last_message, 'content'):
                        response_content = last_message.content
                        print(f"✅ Extracted content from AIMessage: {len(response_content)} chars")
                    elif isinstance(last_message, dict) and "content" in last_message:
                        response_content = last_message["content"]
                        print(f"✅ Extracted content from dict: {len(response_content)} chars")
            
            # Try to extract current agent
            if hasattr(result, 'get') and result.get("current_agent"):
                current_agent = result["current_agent"]
                print(f"✅ Extracted current_agent: {current_agent}")
                
                # Map agent names for display
                agent_display_names = {
                    "search_agent": "Alex - Search Specialist",
                    "property_agent": "Emma - Property Expert", 
                    "scheduling_agent": "Mike - Scheduling Specialist"
                }
                agent_name = agent_display_names.get(current_agent, f"AI Assistant - {current_agent}")
                print(f"✅ Mapped agent name: {agent_name}")
        
        # Generate suggested actions based on agent type
        suggested_actions = []
        if current_agent == "property_agent":
            suggested_actions = [
                "Get property details",
                "Ask about pricing",
                "Learn about neighborhood",
                "Schedule a visit"
            ]
        
        print(f"🎯 Generated response from {agent_name}: {len(response_content)} chars")
        print(f"📝 Response preview: {response_content[:200]}...")
        
        return AgentResponse(
            success=True,
            message=response_content,
            agent_name=agent_name,
            session_id=session.session_id,
            current_agent=current_agent,
            suggested_actions=suggested_actions,
            confidence=0.85,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"❌ Error processing with real agent: {e}")
        print(f"❌ Full traceback:")
        traceback.print_exc()
        
        # Fallback inteligente
        from app.orchestration.swarm import generate_intelligent_response
        
        # Generate intelligent fallback response
        response_content = generate_intelligent_response(
            session.current_agent, 
            message, 
            property_context or {}, 
            data_mode
        )
        
        # Map agent names for display
        agent_display_names = {
            "search_agent": "Alex - Search Specialist",
            "property_agent": "Emma - Property Expert", 
            "scheduling_agent": "Mike - Scheduling Specialist"
        }
        agent_name = agent_display_names.get(session.current_agent, f"AI Assistant - {session.current_agent}")
        
        suggested_actions = [
            "Get property details",
            "Ask about pricing",
            "Learn about neighborhood",
            "Schedule a visit"
        ]
        
        print(f"🎯 Fallback response from {agent_name}: {len(response_content)} chars")
        print(f"📝 Fallback preview: {response_content[:200]}...")
        
        return AgentResponse(
            success=True,
            message=response_content,
            agent_name=agent_name,
            session_id=session.session_id,
            current_agent=session.current_agent,
            suggested_actions=suggested_actions,
            confidence=0.75,  # Lower confidence for fallback
            timestamp=datetime.now().isoformat()
        )

async def test_api_simulation():
    """Testa simulação do API server"""
    
    print("🧪 TESTE DE SIMULAÇÃO DO API SERVER")
    print("=" * 60)
    
    # Criar sessão simulada
    session = AgentSession(
        session_id="test-session-123",
        current_agent="property_agent",
        property_id="prop-123"
    )
    
    print(f"✅ Sessão criada: {session.session_id}")
    print(f"✅ Agente atual: {session.current_agent}")
    print(f"✅ Property ID: {session.property_id}")
    
    # Testar mensagens
    test_messages = [
        "hello Emma",
        "how much is the rent?",
        "tell me about the neighborhood"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'='*60}")
        print(f"🔄 TESTE {i}: '{message}'")
        print(f"{'='*60}")
        
        response = await simulate_process_with_real_agent(message, session, "mock")
        
        print(f"\n📊 RESULTADO DO TESTE {i}:")
        print(f"   Sucesso: {response.success}")
        print(f"   Agente: {response.agent_name}")
        print(f"   Confiança: {response.confidence}")
        print(f"   Resposta: {response.message[:150]}...")
        
        # Verificar se é resposta real ou fallback
        if "Emma" in response.message and response.confidence > 0.8:
            print(f"   ✅ RESPOSTA REAL DO AGENTE!")
        else:
            print(f"   ⚠️ Possível fallback (confiança: {response.confidence})")

if __name__ == "__main__":
    asyncio.run(test_api_simulation()) 