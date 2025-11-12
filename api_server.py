#!/usr/bin/env python3
"""
Servidor FastAPI para o sistema Agentic Real Estate
Serve dados mock e API real com estrutura idêntica
"""

# O carregamento do .env agora é tratado diretamente pelo Uvicorn com a flag --env-file
# from dotenv import load_dotenv
# load_dotenv()

import os
import sys
import asyncio
import uvicorn
import uuid
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import logging
from langchain_core.messages import HumanMessage

# Adicionar o diretório raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar configuração e serviços do sistema existente
from config.api_config import RentCastAPI, APIConfig, APIMode
from config.settings import get_settings

# Importar sistema de logging com Logfire
from app.utils.logging import setup_logging, log_api_call, log_performance, log_error
try:
    from app.utils.logfire_config import setup_logfire, log_system_startup
    LOGFIRE_AVAILABLE = True
except ImportError:
    LOGFIRE_AVAILABLE = False

# Importar dashboard de observabilidade
try:
    from app.api.dashboard import dashboard_router, get_dashboard_metrics, broadcast_metrics_update
    DASHBOARD_AVAILABLE = True
except ImportError:
    DASHBOARD_AVAILABLE = False

# Configurar logging avançado
logger = setup_logging(enable_logfire=LOGFIRE_AVAILABLE)

# Configurar Logfire se disponível
if LOGFIRE_AVAILABLE:
    setup_logfire()
    log_system_startup()
    logger.info("Logfire observability enabled for API server")

# Verificar se a chave OpenRouter foi carregada via configurações centralizadas
settings = get_settings()
openrouter_key = settings.apis.openrouter_key
if openrouter_key and openrouter_key != "your_openrouter_api_key_here":
    logger.info("OpenRouter API key loaded via settings")
else:
    logger.warning("OpenRouter API key not configured in settings")

# Modelos Pydantic para API
class PropertyResponse(BaseModel):
    id: str
    formattedAddress: str
    addressLine1: str
    addressLine2: str
    city: str
    state: str
    zipCode: str
    county: str
    latitude: float
    longitude: float
    propertyType: str
    bedrooms: int
    bathrooms: int
    squareFootage: int
    lotSize: int
    yearBuilt: int
    status: str
    price: int
    listingType: str
    listedDate: str
    removedDate: Optional[str]
    createdDate: str
    lastSeenDate: str
    daysOnMarket: int
    mlsName: str
    mlsNumber: str
    listingAgent: Dict[str, str]
    listingOffice: Dict[str, str]
    history: Dict[str, Any]

class SearchFilters(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    minPrice: Optional[int] = None
    maxPrice: Optional[int] = None
    minBedrooms: Optional[int] = None
    maxBedrooms: Optional[int] = None
    minBathrooms: Optional[int] = None
    maxBathrooms: Optional[int] = None
    propertyType: Optional[str] = None
    minSquareFootage: Optional[int] = None
    maxSquareFootage: Optional[int] = None

class AppointmentRequest(BaseModel):
    propertyId: str
    clientName: str
    clientEmail: str
    clientPhone: str
    preferredDate: str
    preferredTime: str
    message: Optional[str] = None
    appointmentType: str = Field(..., pattern="^(viewing|consultation|negotiation)$")

class AppointmentResponse(BaseModel):
    id: str
    propertyId: str
    propertyAddress: str
    clientName: str
    clientEmail: str
    clientPhone: str
    scheduledDate: str
    scheduledTime: str
    status: str = Field(..., pattern="^(pending|confirmed|cancelled|completed)$")
    appointmentType: str
    message: Optional[str] = None
    createdAt: str
    updatedAt: str
    agentName: Optional[str] = None
    agentEmail: Optional[str] = None
    agentPhone: Optional[str] = None

class TimeSlot(BaseModel):
    id: str
    time: str
    available: bool

class ApiResponse(BaseModel):
    success: bool
    data: Any
    message: Optional[str] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    mode: str
    timestamp: str

# Models for AI Agent System
class AgentSessionRequest(BaseModel):
    property_id: Optional[str] = None
    agent_mode: str = Field(..., pattern="^(details|schedule|general)$")
    user_preferences: Optional[Dict[str, Any]] = None
    language: str = Field(default="en", pattern="^(en|pt|es)$")

class AgentSession(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    property_id: Optional[str] = None
    current_agent: str = Field(..., pattern="^(search_agent|property_agent|scheduling_agent)$")
    status: str = Field(..., pattern="^(active|completed|error)$")
    created_at: str
    updated_at: str

class ChatMessage(BaseModel):
    message: str
    session_id: str
    property_context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    success: bool
    message: str
    agent_name: str
    session_id: str
    current_agent: str
    data: Optional[Dict[str, Any]] = None
    suggested_actions: Optional[List[str]] = None
    confidence: Optional[float] = None
    timestamp: str

# Criar aplicação FastAPI
app = FastAPI(
    title="Agentic Real Estate API",
    description="API para sistema agêntico de busca e agendamento de imóveis",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir dashboard de observabilidade
if DASHBOARD_AVAILABLE:
    app.include_router(dashboard_router)
    logger.info("SUCCESS: Dashboard de observabilidade integrado")
else:
    logger.warning("WARNING: Dashboard de observabilidade não disponível")

# Middleware de instrumentação para observabilidade
@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    """Middleware para instrumentação automática de todas as requisições."""
    start_time = time.time()
    
    # Extrair informações da requisição
    method = request.method
    url_path = request.url.path
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Log do início da requisição
    logger.info(f"API Request: {method} {url_path} from {client_ip}")
    
    try:
        # Processar requisição
        response = await call_next(request)
        
        # Calcular duração
        duration = time.time() - start_time
        
        # Log da resposta bem-sucedida
        log_api_call(
            api_name="FastAPI",
            endpoint=url_path,
            method=method,
            status_code=response.status_code,
            duration=duration
        )
        
        # Record metrics for dashboard
        if DASHBOARD_AVAILABLE and not url_path.startswith('/dashboard'):
            metrics = get_dashboard_metrics()
            metrics.record_api_call(
                f"FastAPI_{method}_{url_path.split('/')[1] if len(url_path.split('/')) > 1 else 'root'}",
                response.status_code < 400,
                duration
            )
        
        # Log de performance se requisição for lenta
        if duration > 2.0:
            log_performance(
                operation=f"API_{method}_{url_path.replace('/', '_')}",
                duration=duration,
                details={
                    "status_code": response.status_code,
                    "client_ip": client_ip,
                    "user_agent": user_agent[:100] if user_agent else "unknown"
                }
            )
        
        logger.info(f"API Response: {response.status_code} in {duration:.2f}s")
        return response
        
    except Exception as e:
        # Calcular duração mesmo em caso de erro
        duration = time.time() - start_time
        
        # Log do erro
        log_error(
            error=str(e),
            context={
                "method": method,
                "url_path": url_path,
                "client_ip": client_ip,
                "duration": duration
            }
        )
        
        # Retornar resposta de erro
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "message": str(e)}
        )

# Instância do serviço de propriedades
api_config = APIConfig()
property_service = RentCastAPI(api_config)

# Storage em memória para agendamentos (em produção seria banco de dados)
appointments_storage: Dict[str, AppointmentResponse] = {}

# Storage em memória para sessões de agente IA
agent_sessions: Dict[str, AgentSession] = {}
agent_chat_history: Dict[str, List[Dict[str, Any]]] = {}

def get_api_mode(mode: str = Query("mock", pattern="^(mock|real)$")) -> str:
    """Dependência para obter o modo da API"""
    return mode

@app.get("/api/health", response_model=ApiResponse)
async def health_check(mode: str = Depends(get_api_mode)):
    """Health check da API"""
    try:
        return ApiResponse(
            success=True,
            data=HealthResponse(
                status="healthy",
                mode=mode,
                timestamp=datetime.now().isoformat()
            )
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/properties/search", response_model=ApiResponse)
async def search_properties(
    mode: str = Depends(get_api_mode),
    city: Optional[str] = None,
    state: Optional[str] = None,
    minPrice: Optional[int] = None,
    maxPrice: Optional[int] = None,
    minBedrooms: Optional[int] = None,
    maxBedrooms: Optional[int] = None,
    minBathrooms: Optional[int] = None,
    maxBathrooms: Optional[int] = None,
    propertyType: Optional[str] = None,
    minSquareFootage: Optional[int] = None,
    maxSquareFootage: Optional[int] = None,
):
    """Buscar propriedades com filtros"""
    try:
        logger.info(f"Searching properties in {mode.upper()} mode")
        
        # Criar filtros
        filters = {
            'city': city,
            'state': state,
            'min_price': minPrice,
            'max_price': maxPrice,
            'min_bedrooms': minBedrooms,
            'max_bedrooms': maxBedrooms,
            'min_bathrooms': minBathrooms,
            'max_bathrooms': maxBathrooms,
            'property_type': propertyType,
            'min_square_footage': minSquareFootage,
            'max_square_footage': maxSquareFootage,
        }
        
        # Remover filtros None
        filters = {k: v for k, v in filters.items() if v is not None}
        
        # Buscar propriedades
        if mode == "mock":
            # Configurar modo mock
            api_config.mode = APIMode.MOCK
            api_config.use_real_api = False
            properties = await asyncio.to_thread(property_service.search_properties, filters)
        else:
            # Configurar modo real
            api_config.mode = APIMode.REAL
            api_config.use_real_api = True
            api_config.rentcast_api_key = os.getenv("RENTCAST_API_KEY")
            properties = await asyncio.to_thread(property_service.search_properties, filters)
        
        logger.info(f"Found {len(properties)} properties in {mode.upper()} mode")
        
        return ApiResponse(
            success=True,
            data=properties,
            message=f"Found {len(properties)} properties"
        )
        
    except Exception as e:
        logger.error(f"ERROR Error searching properties: {e}")
        return ApiResponse(
            success=False,
            data=[],
            error=str(e)
        )

@app.get("/api/properties/{property_id}", response_model=ApiResponse)
async def get_property_by_id(
    property_id: str,
    mode: str = Depends(get_api_mode)
):
    """Obter propriedade por ID"""
    try:
        logger.info(f"🔍 Getting property {property_id} in {mode.upper()} mode")
        
        # Buscar todas as propriedades e filtrar por ID
        if mode == "mock":
            # Configurar modo mock
            api_config.mode = APIMode.MOCK
            api_config.use_real_api = False
            properties = await asyncio.to_thread(property_service.search_properties, {})
        else:
            # Configurar modo real
            api_config.mode = APIMode.REAL
            api_config.use_real_api = True
            api_config.rentcast_api_key = os.getenv("RENTCAST_API_KEY")
            properties = await asyncio.to_thread(property_service.search_properties, {})
        
        # Encontrar propriedade por ID
        property_found = None
        for prop in properties:
            if prop.get('id') == property_id:
                property_found = prop
                break
        
        if not property_found:
            raise HTTPException(status_code=404, detail="Propriedade não encontrada")
        
        return ApiResponse(
            success=True,
            data=property_found
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR Error getting property: {e}")
        return ApiResponse(
            success=False,
            data=None,
            error=str(e)
        )

@app.post("/api/appointments", response_model=ApiResponse)
async def create_appointment(appointment: AppointmentRequest):
    """Criar agendamento"""
    try:
        logger.info(f"📅 Creating appointment for property {appointment.propertyId}")
        
        # Gerar ID único
        appointment_id = f"apt_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(appointments_storage)}"
        
        # Criar resposta do agendamento
        appointment_response = AppointmentResponse(
            id=appointment_id,
            propertyId=appointment.propertyId,
            propertyAddress="Endereço da propriedade", # Em produção, buscar do banco
            clientName=appointment.clientName,
            clientEmail=appointment.clientEmail,
            clientPhone=appointment.clientPhone,
            scheduledDate=appointment.preferredDate,
            scheduledTime=appointment.preferredTime,
            status="pending",
            appointmentType=appointment.appointmentType,
            message=appointment.message,
            createdAt=datetime.now().isoformat(),
            updatedAt=datetime.now().isoformat(),
            agentName="Carlos Silva",
            agentEmail="carlos.silva@imobiliaria.com.br",
            agentPhone="21987654321"
        )
        
        # Salvar no storage
        appointments_storage[appointment_id] = appointment_response
        
        logger.info(f"SUCCESS Appointment created with ID: {appointment_id}")
        
        return ApiResponse(
            success=True,
            data=appointment_response.dict(),
            message="Agendamento criado com sucesso"
        )
        
    except Exception as e:
        logger.error(f"ERROR Error creating appointment: {e}")
        return ApiResponse(
            success=False,
            data=None,
            error=str(e)
        )

@app.get("/api/appointments/available-slots", response_model=ApiResponse)
async def get_available_time_slots(
    propertyId: str = Query(...),
    date: str = Query(...)
):
    """Obter horários disponíveis para agendamento"""
    try:
        logger.info(f"🕐 Getting available slots for property {propertyId} on {date}")
        
        # Gerar horários disponíveis (9h às 18h)
        slots = []
        base_time = datetime.strptime("09:00", "%H:%M")
        
        for i in range(10):  # 10 slots de 1 hora
            time_str = (base_time + timedelta(hours=i)).strftime("%H:%M")
            slot_id = f"{propertyId}_{date}_{time_str.replace(':', '')}"
            
            # Simular disponibilidade (alguns horários ocupados)
            available = not (i in [2, 5, 7])  # 11h, 14h, 16h ocupados
            
            slots.append(TimeSlot(
                id=slot_id,
                time=time_str,
                available=available
            ))
        
        return ApiResponse(
            success=True,
            data=[slot.dict() for slot in slots]
        )
        
    except Exception as e:
        logger.error(f"ERROR Error getting time slots: {e}")
        return ApiResponse(
            success=False,
            data=[],
            error=str(e)
        )

@app.get("/api/appointments/user", response_model=ApiResponse)
async def get_user_appointments(email: str = Query(...)):
    """Obter agendamentos do usuário"""
    try:
        logger.info(f"📋 Getting appointments for user {email}")
        
        # Filtrar agendamentos por email
        user_appointments = [
            apt.dict() for apt in appointments_storage.values() 
            if apt.clientEmail == email
        ]
        
        return ApiResponse(
            success=True,
            data=user_appointments
        )
        
    except Exception as e:
        logger.error(f"ERROR Error getting user appointments: {e}")
        return ApiResponse(
            success=False,
            data=[],
            error=str(e)
        )

@app.delete("/api/appointments/{appointment_id}", response_model=ApiResponse)
async def cancel_appointment(appointment_id: str):
    """Cancelar agendamento"""
    try:
        logger.info(f"CANCEL Cancelling appointment {appointment_id}")
        
        if appointment_id not in appointments_storage:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado")
        
        # Atualizar status
        appointments_storage[appointment_id].status = "cancelled"
        appointments_storage[appointment_id].updatedAt = datetime.now().isoformat()
        
        return ApiResponse(
            success=True,
            data=None,
            message="Agendamento cancelado com sucesso"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR Error cancelling appointment: {e}")
        return ApiResponse(
            success=False,
            data=None,
            error=str(e)
        )


# AI Agent Endpoints
@app.post("/api/agent/session/start", response_model=ApiResponse)
async def start_agent_session(
    request: AgentSessionRequest,
    mode: str = Depends(get_api_mode)
):
    """Start a new AI agent session"""
    try:
        logger.info(f"🤖 Starting agent session in {mode.upper()} mode")
        
        session_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        # Determine agent type based on mode
        if request.agent_mode == "schedule":
            current_agent = "scheduling_agent"
        elif request.agent_mode == "details":
            current_agent = "property_agent"
        else:
            current_agent = "property_agent"
        
        session = AgentSession(
            session_id=session_id,
            property_id=request.property_id,
            current_agent=current_agent,
            status="active",
            created_at=current_time,
            updated_at=current_time
        )
        
        # Store session
        agent_sessions[session_id] = session
        agent_chat_history[session_id] = []
        
        logger.info(f"SUCCESS Created agent session: {session_id}")
        
        return ApiResponse(
            success=True,
            data={"session": session.dict()},
            message="Agent session started successfully"
        )
        
    except Exception as e:
        logger.error(f"ERROR Error starting agent session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/chat", response_model=ApiResponse)
async def send_message_to_agent(
    request: ChatMessage,
    mode: str = Depends(get_api_mode)
):
    """Send message to AI agent"""
    try:
        logger.info(f"💬 Processing message in {mode.upper()} mode: '{request.message[:50]}...'")
        logger.info(f"PROPERTY Property context from request: {request.property_context.get('formattedAddress', 'N/A') if request.property_context else 'None'}")
        
        # Check if session exists
        if request.session_id not in agent_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = agent_sessions[request.session_id]
        
        # Use property_context from request if provided, otherwise try to get from session/database
        property_context = request.property_context
        if not property_context and session.property_id:
            # Try to get property context from our database
            try:
                if mode == "mock":
                    api_config.mode = APIMode.MOCK
                    api_config.use_real_api = False
                else:
                    api_config.mode = APIMode.REAL
                    api_config.use_real_api = True
                    api_config.rentcast_api_key = os.getenv("RENTCAST_API_KEY")
                
                properties = await asyncio.to_thread(property_service.search_properties, {})
                for prop in properties:
                    if str(prop.get('id')) == str(session.property_id):
                        property_context = prop
                        break
                logger.info(f"🔍 Found property context from session: {property_context.get('formattedAddress', 'N/A') if property_context else 'None'}")
            except Exception as e:
                logger.warning(f"Could not get property context from session: {e}")
        
        # Always use the real agentic system, but pass the correct data mode and property context
        response = await process_with_real_agent(request.message, session, data_mode=mode, property_context=property_context)
        
        # Store message in history
        agent_chat_history[request.session_id].extend([
            {
                "role": "user",
                "content": request.message,
                "timestamp": datetime.now().isoformat()
            },
            {
                "role": "assistant", 
                "content": response.message,
                "agent_name": response.agent_name,
                "timestamp": response.timestamp
            }
        ])
        
        # Update session with new current_agent if it changed
        if hasattr(response, 'current_agent') and response.current_agent != session.current_agent:
            session.current_agent = response.current_agent
            logger.info(f"SESSION Updated session current_agent to: {response.current_agent}")
        
        session.updated_at = datetime.now().isoformat()
        agent_sessions[request.session_id] = session
        
        return ApiResponse(
            success=True,
            data=response.dict(),
            message="Message processed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/session/end", response_model=ApiResponse)
async def end_agent_session(session_data: Dict[str, str]):
    """End an AI agent session"""
    try:
        session_id = session_data.get("session_id")
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id required")
        
        if session_id not in agent_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update session status
        session = agent_sessions[session_id]
        session.status = "completed"
        session.updated_at = datetime.now().isoformat()
        
        logger.info(f"🛑 Ended agent session: {session_id}")
        
        return ApiResponse(
            success=True,
            data={"session_id": session_id},
            message="Session ended successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR Error ending session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/session/{session_id}/history", response_model=ApiResponse)
async def get_session_history(session_id: str):
    """Get chat history for a session"""
    try:
        if session_id not in agent_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        history = agent_chat_history.get(session_id, [])
        
        return ApiResponse(
            success=True,
            data={"messages": history},
            message="History retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_with_real_agent(message: str, session: AgentSession, data_mode: str = "real", property_context: Optional[Dict[str, Any]] = None) -> AgentResponse:
    """Process message with real AI agent system"""
    try:
        logger.info(f"🤖 Processing with Fixed LangGraph-Swarm + PydanticAI in {data_mode.upper()} data mode: {message[:100]}...")
        logger.info(f"PROPERTY Using property context: {property_context.get('formattedAddress', 'N/A') if property_context else 'None provided'}")
        
        # Import the Fixed SwarmOrchestrator when needed
        from app.orchestration.swarm_fixed import get_fixed_swarm_orchestrator
        
        # Initialize the fixed orchestrator (singleton)
        orchestrator = get_fixed_swarm_orchestrator()
        
        # Use the property_context passed as parameter if available
        # If not provided, try to get it from session
        if not property_context and session.property_id:
            try:
                # Configure API based on data_mode
                if data_mode == "real":
                    api_config.mode = APIMode.REAL
                    api_config.use_real_api = True
                    api_config.rentcast_api_key = os.getenv("RENTCAST_API_KEY")
                else:
                    api_config.mode = APIMode.MOCK
                    api_config.use_real_api = False
                
                # Get property details for context
                properties = await asyncio.to_thread(property_service.search_properties, {})
                for prop in properties:
                    if str(prop.get('id')) == str(session.property_id):
                        property_context = prop
                        break
                logger.info(f"PROPERTY Found property context from session: {property_context.get('formattedAddress', 'N/A') if property_context else 'None'}")
            except Exception as e:
                logger.warning(f"Could not get property context from session: {e}")
        
        # Create comprehensive message format for the agent system
        agent_message = {
            "messages": [HumanMessage(content=message)],
            "session_id": session.session_id,
            "current_agent": session.current_agent,
            "context": {
                "property_context": property_context,
                "source": "web_chat",
                "user_mode": session.current_agent,
                "language": "en",
                "data_mode": data_mode,  # ⚠️ CRITICAL: Pass data mode to the swarm
                "api_config": {
                    "mode": data_mode,
                    "use_real_api": data_mode == "real"
                }
            }
        }
        
        # MEMORY: Configuração com thread_id para memória persistente
        config = {
            "configurable": {
                "thread_id": session.session_id,  # Usar session_id como thread_id
                "user_id": session.user_id or "anonymous",  # Para memória de longo prazo
                "checkpoint_ns": "real_estate_chat"  # Namespace para checkpoints
            }
        }
        
        logger.info(f"BRAIN Calling Fixed SwarmOrchestrator with thread_id: {session.session_id}")
        
        # Process with the fixed swarm orchestrator
        result = await orchestrator.process_message(agent_message, config)  # MEMORY: PASSAR CONFIG
        
        logger.info(f"SUCCESS Fixed SwarmOrchestrator result: {type(result)}")
        
        # Extract response from swarm result
        response_content = f"I'm here to help! How can I assist you with this property? (Using {data_mode} data)"
        agent_name = "AI Assistant"
        current_agent = session.current_agent
        
        logger.info(f"🔍 Fixed SwarmOrchestrator result type: {type(result)}")
        logger.info(f"🔍 Fixed SwarmOrchestrator result keys: {list(result.keys()) if hasattr(result, 'keys') else 'No keys'}")
        
        if result:
            # Try to extract from messages
            if hasattr(result, 'get') and result.get("messages"):
                messages = result["messages"]
                logger.info(f"🔍 Found {len(messages)} messages")
                if messages:
                    last_message = messages[-1]
                    logger.info(f"🔍 Last message type: {type(last_message)}")
                    
                    # Handle LangChain AIMessage objects
                    if hasattr(last_message, 'content'):
                        response_content = last_message.content
                        logger.info(f"SUCCESS Extracted content from AIMessage: {len(response_content)} chars")
                    elif isinstance(last_message, dict) and "content" in last_message:
                        response_content = last_message["content"]
                        logger.info(f"SUCCESS Extracted content from dict: {len(response_content)} chars")
            
            # Try to extract current agent from swarm result
            extracted_agent = None
            if hasattr(result, 'get') and result.get("current_agent"):
                extracted_agent = result["current_agent"]
                logger.info(f"SUCCESS Extracted current_agent from result: {extracted_agent}")
            
            # Use the extracted agent if available, otherwise fall back to session agent
            if extracted_agent:
                current_agent = extracted_agent
            else:
                current_agent = session.current_agent
                logger.info(f"Using session current_agent: {current_agent}")
                
            # Map agent names for display - CRITICAL: Use the actual current_agent
            agent_display_names = {
                "search_agent": "Alex - Search Specialist",
                "property_agent": "Emma - Property Expert", 
                "scheduling_agent": "Mike - Scheduling Specialist"
            }
            agent_name = agent_display_names.get(current_agent, f"AI Assistant - {current_agent}")
            logger.info(f"SUCCESS Mapped agent name: {agent_name} for agent: {current_agent}")
        
        # Generate suggested actions based on agent type
        suggested_actions = []
        if current_agent == "search_agent":
            suggested_actions = [
                "Search for properties",
                "Refine search criteria",
                "Compare properties",
                "Get market insights"
            ]
        elif current_agent == "property_agent":
            suggested_actions = [
                "Get property details",
                "Ask about pricing",
                "Learn about neighborhood",
                "Schedule a visit"
            ]
        elif current_agent == "scheduling_agent":
            suggested_actions = [
                "Schedule property visit",
                "Check availability",
                "Confirm appointment",
                "Get agent contact"
            ]
        else:
            suggested_actions = [
                "Ask about property details",
                "Schedule a visit", 
                "Get neighborhood information",
                "Compare properties"
            ]
        
        logger.info(f"RESPONSE Generated response from {agent_name}: {len(response_content)} chars")
        
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
        logger.error(f"ERROR Error processing with real agent: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Generate intelligent fallback response based on agent type
        if session.current_agent == "search_agent":
            response_content = f"I'm Alex, your search specialist. I'm having trouble processing your request right now, but I'm here to help you find the perfect property. Could you tell me more about what you're looking for? (Using {data_mode} data)"
        elif session.current_agent == "scheduling_agent":
            response_content = f"I'm Mike, your scheduling specialist. I'm having trouble processing your request right now, but I'm here to help you schedule property visits. What would you like to schedule? (Using {data_mode} data)"
        else:  # property_agent
            response_content = f"I'm Emma, your property expert. I'm having trouble processing your request right now, but I'm here to help you with property details and analysis. What would you like to know? (Using {data_mode} data)"
        
        # Map agent names for display - CRITICAL: Use actual current_agent from session
        agent_display_names = {
            "search_agent": "Alex - Search Specialist",
            "property_agent": "Emma - Property Expert", 
            "scheduling_agent": "Mike - Scheduling Specialist"
        }
        agent_name = agent_display_names.get(session.current_agent, f"AI Assistant - {session.current_agent}")
        
        # Generate suggested actions based on agent type
        suggested_actions = []
        if session.current_agent == "search_agent":
            suggested_actions = [
                "Search for properties",
                "Refine search criteria",
                "Compare properties",
                "Get market insights"
            ]
        elif session.current_agent == "property_agent":
            suggested_actions = [
                "Get property details",
                "Ask about pricing",
                "Learn about neighborhood",
                "Schedule a visit"
            ]
        elif session.current_agent == "scheduling_agent":
            suggested_actions = [
                "Schedule property visit",
                "Check availability",
                "Confirm appointment",
                "Get agent contact"
            ]
        else:
            suggested_actions = [
                "Ask about property details",
                "Schedule a visit", 
                "Get neighborhood information",
                "Compare properties"
            ]
        
        logger.info(f"FALLBACK Fallback response from {agent_name}: {len(response_content)} chars")
        
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


# Servir arquivos estáticos do frontend
app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")

@app.get("/")
async def serve_frontend():
    """Servir o frontend React"""
    return FileResponse("frontend/dist/index.html")

@app.get("/{path:path}")
async def serve_frontend_routes(path: str):
    """Servir rotas do frontend (SPA)"""
    # Verificar se é uma rota da API
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Verificar se o arquivo existe
    file_path = f"frontend/dist/{path}"
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Caso contrário, servir o index.html (SPA routing)
    return FileResponse("frontend/dist/index.html")

if __name__ == "__main__":
    print("STARTUP Starting Agentic Real Estate Server...")
    print("============================================================")
    print("📱 Frontend: http://localhost:8000")
    print("🔧 API Docs: http://localhost:8000/api/docs")
    print("📊 API Redoc: http://localhost:8000/api/redoc")
    print("============================================================")
    print("🧪 Mock Mode: Dados brasileiros de demonstração")
    print("🌐 Real Mode: API RentCast real (EUA)")
    print("🎛️  Seletor no header da interface")
    print("============================================================")
    print("Pressione Ctrl+C para parar o servidor")
    print()
    
    uvicorn.run(
        "api_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
        env_file=".env"  # Forçar o carregamento do arquivo .env
    ) 