"""
Ferramentas nativas do LangGraph para agendamento de calendário.

Implementação sem LangChain, usando apenas ferramentas nativas do LangGraph.
"""

from typing import List, Dict, Any, Optional, Annotated
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from langgraph.prebuilt import InjectedState

from ..utils.logging import get_logger
from config.settings import get_settings


class CalendarEvent(BaseModel):
    """Modelo para eventos de calendário."""
    
    id: Optional[str] = None
    title: str = Field(..., description="Título do evento")
    description: Optional[str] = None
    start_time: datetime = Field(..., description="Data/hora de início")
    end_time: datetime = Field(..., description="Data/hora de fim")
    location: Optional[str] = None
    attendees: List[str] = Field(default_factory=list)
    property_id: Optional[int] = None
    agent_contact: Optional[str] = None


class AvailableSlot(BaseModel):
    """Slot de horário disponível."""
    
    start_time: datetime
    end_time: datetime
    description: str = "Horário disponível"


def get_available_slots(
    date_start: datetime,
    date_end: datetime,
    duration_minutes: int = 60,
    state: Annotated[Dict[str, Any], InjectedState] = None
) -> List[AvailableSlot]:
    """
    Ferramenta para obter horários disponíveis para agendamento.
    
    Args:
        date_start: Data de início da busca
        date_end: Data de fim da busca
        duration_minutes: Duração desejada em minutos
        state: Estado injetado
    
    Returns:
        Lista de slots disponíveis
    """
    logger = get_logger("calendar_tools")
    
    # TODO: Integrar com Google Calendar API real
    # Por enquanto, gerar slots mock
    
    available_slots = []
    current_date = date_start.date()
    end_date = date_end.date()
    
    while current_date <= end_date:
        # Horários comerciais: 9h às 18h
        for hour in [9, 10, 11, 14, 15, 16, 17]:
            slot_start = datetime.combine(current_date, datetime.min.time().replace(hour=hour))
            slot_end = slot_start + timedelta(minutes=duration_minutes)
            
            # Verificar se não é fim de semana
            if current_date.weekday() < 5:  # 0-4 = segunda a sexta
                available_slots.append(
                    AvailableSlot(
                        start_time=slot_start,
                        end_time=slot_end,
                        description=f"Visita de imóvel - {slot_start.strftime('%d/%m %H:%M')}"
                    )
                )
        
        current_date += timedelta(days=1)
    
    logger.info(f"Found {len(available_slots)} available slots")
    return available_slots


def schedule_property_visit(
    property_id: int,
    visitor_name: str,
    visitor_email: str,
    visitor_phone: str,
    preferred_datetime: datetime,
    notes: Optional[str] = None,
    state: Annotated[Dict[str, Any], InjectedState] = None
) -> CalendarEvent:
    """
    Ferramenta para agendar visita a propriedade.
    
    Args:
        property_id: ID da propriedade
        visitor_name: Nome do visitante
        visitor_email: Email do visitante
        visitor_phone: Telefone do visitante
        preferred_datetime: Data/hora preferida
        notes: Observações adicionais
        state: Estado injetado
    
    Returns:
        Evento criado no calendário
    """
    logger = get_logger("calendar_tools")
    settings = get_settings()
    
    # TODO: Integrar com Google Calendar API real
    # Por enquanto, simular criação de evento
    
    event = CalendarEvent(
        id=f"visit_{property_id}_{int(preferred_datetime.timestamp())}",
        title=f"Visita - Propriedade #{property_id}",
        description=f"""
        Visita agendada para propriedade #{property_id}
        
        Visitante: {visitor_name}
        Email: {visitor_email}
        Telefone: {visitor_phone}
        
        Observações: {notes or 'Nenhuma'}
        """.strip(),
        start_time=preferred_datetime,
        end_time=preferred_datetime + timedelta(hours=1),
        location="Endereço da propriedade",
        attendees=[visitor_email, "corretor@imobiliaria.com"],
        property_id=property_id,
        agent_contact="(21) 99999-9999"
    )
    
    logger.info(f"Scheduled visit for property {property_id} at {preferred_datetime}")
    return event


def cancel_appointment(
    event_id: str,
    reason: Optional[str] = None,
    state: Annotated[Dict[str, Any], InjectedState] = None
) -> bool:
    """
    Ferramenta para cancelar agendamento.
    
    Args:
        event_id: ID do evento a ser cancelado
        reason: Motivo do cancelamento
        state: Estado injetado
    
    Returns:
        True se cancelado com sucesso
    """
    logger = get_logger("calendar_tools")
    
    # TODO: Implementar cancelamento real via API
    # Por enquanto, simular cancelamento
    
    logger.info(f"Cancelled appointment {event_id}. Reason: {reason}")
    return True


def reschedule_appointment(
    event_id: str,
    new_datetime: datetime,
    state: Annotated[Dict[str, Any], InjectedState] = None
) -> CalendarEvent:
    """
    Ferramenta para reagendar compromisso.
    
    Args:
        event_id: ID do evento a ser reagendado
        new_datetime: Nova data/hora
        state: Estado injetado
    
    Returns:
        Evento atualizado
    """
    logger = get_logger("calendar_tools")
    
    # TODO: Implementar reagendamento real via API
    # Por enquanto, simular reagendamento
    
    updated_event = CalendarEvent(
        id=event_id,
        title="Visita Reagendada - Propriedade",
        description="Visita reagendada conforme solicitação",
        start_time=new_datetime,
        end_time=new_datetime + timedelta(hours=1),
        location="Endereço da propriedade"
    )
    
    logger.info(f"Rescheduled appointment {event_id} to {new_datetime}")
    return updated_event


def get_user_appointments(
    user_email: str,
    date_start: Optional[datetime] = None,
    date_end: Optional[datetime] = None,
    state: Annotated[Dict[str, Any], InjectedState] = None
) -> List[CalendarEvent]:
    """
    Ferramenta para obter agendamentos do usuário.
    
    Args:
        user_email: Email do usuário
        date_start: Data de início (opcional)
        date_end: Data de fim (opcional)
        state: Estado injetado
    
    Returns:
        Lista de eventos do usuário
    """
    logger = get_logger("calendar_tools")
    
    # TODO: Implementar busca real via API
    # Por enquanto, retornar eventos mock
    
    if not date_start:
        date_start = datetime.now()
    if not date_end:
        date_end = date_start + timedelta(days=30)
    
    mock_events = [
        CalendarEvent(
            id="visit_1",
            title="Visita - Apartamento Copacabana",
            description="Visita agendada para apartamento em Copacabana",
            start_time=datetime.now() + timedelta(days=1, hours=14),
            end_time=datetime.now() + timedelta(days=1, hours=15),
            location="Rua Barata Ribeiro, 100 - Copacabana",
            property_id=1,
            agent_contact="(21) 99999-9999"
        )
    ]
    
    logger.info(f"Found {len(mock_events)} appointments for {user_email}")
    return mock_events


def send_appointment_reminder(
    event_id: str,
    reminder_time_minutes: int = 60,
    state: Annotated[Dict[str, Any], InjectedState] = None
) -> bool:
    """
    Ferramenta para enviar lembrete de agendamento.
    
    Args:
        event_id: ID do evento
        reminder_time_minutes: Tempo antes do evento para enviar lembrete
        state: Estado injetado
    
    Returns:
        True se lembrete foi configurado
    """
    logger = get_logger("calendar_tools")
    
    # TODO: Implementar sistema real de lembretes
    # Por enquanto, simular configuração
    
    logger.info(f"Reminder set for event {event_id} - {reminder_time_minutes} minutes before")
    return True


# Lista de ferramentas disponíveis
CALENDAR_TOOLS = [
    get_available_slots,
    schedule_property_visit,
    cancel_appointment,
    reschedule_appointment,
    get_user_appointments,
    send_appointment_reminder
] 