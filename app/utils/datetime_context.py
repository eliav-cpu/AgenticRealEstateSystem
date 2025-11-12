"""
Datetime Context Utility for Agentic Real Estate System

This module provides real-time datetime context for AI agents to understand
temporal references like "today", "tomorrow", "next week", etc.
"""

from datetime import datetime, timedelta
from typing import Dict, Any
import pytz


def get_agent_datetime_context(timezone: str = "America/Sao_Paulo") -> Dict[str, Any]:
    """
    Generate comprehensive datetime context for agents.
    
    Args:
        timezone: Target timezone for datetime calculations
        
    Returns:
        Dictionary containing current datetime context and relative date mappings
    """
    try:
        tz = pytz.timezone(timezone)
    except pytz.UnknownTimeZoneError:
        tz = pytz.timezone("America/Sao_Paulo")  # Default fallback
    
    now = datetime.now(tz)
    
    # Calculate relative dates
    tomorrow = now + timedelta(days=1)
    next_week_start = now + timedelta(days=(7 - now.weekday()))
    this_weekend = now + timedelta(days=(5 - now.weekday()) if now.weekday() < 5 else 0)
    next_monday = now + timedelta(days=(7 - now.weekday()))
    next_tuesday = next_monday + timedelta(days=1)
    next_wednesday = next_monday + timedelta(days=2)
    next_thursday = next_monday + timedelta(days=3)
    next_friday = next_monday + timedelta(days=4)
    
    # Week names in Portuguese
    weekdays_pt = [
        "Segunda-feira", "Terça-feira", "Quarta-feira", 
        "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"
    ]
    
    months_pt = [
        "Janeiro", "Fevereiro", "Março", "Abril", 
        "Maio", "Junho", "Julho", "Agosto", 
        "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    
    return {
        "current_datetime": {
            "date": now.date().isoformat(),
            "time": now.time().strftime("%H:%M"),
            "datetime_formatted": now.strftime("%A, %B %d, %Y at %H:%M"),
            "weekday": now.strftime("%A"),
            "weekday_pt": weekdays_pt[now.weekday()],
            "month": now.strftime("%B"),
            "month_pt": months_pt[now.month - 1],
            "year": now.year,
            "week_number": now.isocalendar()[1],
            "timezone": str(tz)
        },
        "relative_dates": {
            "today": now.date().isoformat(),
            "tomorrow": tomorrow.date().isoformat(),
            "this_weekend": this_weekend.date().isoformat(),
            "next_week": next_week_start.date().isoformat(),
            "next_monday": next_monday.date().isoformat(),
            "next_tuesday": next_tuesday.date().isoformat(),
            "next_wednesday": next_wednesday.date().isoformat(),
            "next_thursday": next_thursday.date().isoformat(),
            "next_friday": next_friday.date().isoformat()
        },
        "formatted_relative_dates": {
            "today": f"hoje ({now.strftime('%d/%m/%Y')})",
            "tomorrow": f"amanhã ({tomorrow.strftime('%d/%m/%Y')})",
            "this_weekend": f"este fim de semana ({this_weekend.strftime('%d/%m/%Y')})",
            "next_week": f"próxima semana (a partir de {next_week_start.strftime('%d/%m/%Y')})",
            "next_monday": f"próxima segunda ({next_monday.strftime('%d/%m/%Y')})",
            "next_tuesday": f"próxima terça ({next_tuesday.strftime('%d/%m/%Y')})",
            "next_wednesday": f"próxima quarta ({next_wednesday.strftime('%d/%m/%Y')})",
            "next_thursday": f"próxima quinta ({next_thursday.strftime('%d/%m/%Y')})",
            "next_friday": f"próxima sexta ({next_friday.strftime('%d/%m/%Y')})"
        }
    }


def format_datetime_context_for_agent() -> str:
    """
    Format datetime context as a string for inclusion in agent system prompts.
    
    Returns:
        Formatted string with current datetime context
    """
    context = get_agent_datetime_context()
    current = context["current_datetime"]
    relative = context["formatted_relative_dates"]
    
    return f"""
CONTEXTO TEMPORAL ATUAL:
- Data e Hora Atuais: {current['datetime_formatted']} ({current['timezone']})
- Dia da Semana: {current['weekday_pt']}
- Semana do Ano: {current['week_number']}

REFERÊNCIAS TEMPORAIS:
- "hoje" = {relative['today']}
- "amanhã" = {relative['tomorrow']}
- "este fim de semana" = {relative['this_weekend']}
- "próxima semana" = {relative['next_week']}
- "próxima segunda" = {relative['next_monday']}
- "próxima terça" = {relative['next_tuesday']}
- "próxima quarta" = {relative['next_wednesday']}
- "próxima quinta" = {relative['next_thursday']}
- "próxima sexta" = {relative['next_friday']}

USE ESTE CONTEXTO para interpretar todas as referências temporais do usuário.
Quando o usuário disser "amanhã", você sabe exatamente que data é.
Quando disser "próxima semana", você sabe o período exato.
"""


def get_scheduling_context_for_agent() -> str:
    """
    Get specific datetime context for scheduling agent with available time slots.
    
    Returns:
        Formatted string with scheduling-specific datetime context
    """
    context = get_agent_datetime_context()
    current = context["current_datetime"]
    relative = context["relative_dates"]
    
    # Generate next 7 days for scheduling
    now = datetime.now(pytz.timezone("America/Sao_Paulo"))
    next_days = []
    
    for i in range(1, 8):  # Next 7 days
        future_date = now + timedelta(days=i)
        next_days.append({
            "date": future_date.date().isoformat(),
            "weekday": future_date.strftime("%A"),
            "formatted": future_date.strftime("%d/%m/%Y (%A)")
        })
    
    scheduling_context = f"""
CONTEXTO DE AGENDAMENTO:
- Hoje: {current['date']} ({current['weekday_pt']})
- Horário atual: {current['time']}

PRÓXIMOS 7 DIAS DISPONÍVEIS:
"""
    
    for day in next_days:
        scheduling_context += f"- {day['formatted']}\n"
    
    scheduling_context += """
HORÁRIOS DISPONÍVEIS PADRÃO:
- Dias úteis: 10:00, 14:00, 16:00
- Fins de semana: 13:00, 15:00, 17:00

Sempre confirme a data exata quando o usuário usar termos como "amanhã" ou "próxima semana".
"""
    
    return scheduling_context