"""
Prompts otimizados para agentes do sistema.
"""

from .search import (
    SEARCH_AGENT_SYSTEM_PROMPT,
    SEARCH_CLARIFICATION_PROMPTS,
    SEARCH_SUCCESS_TEMPLATES,
    get_search_prompt
)
from .property import PropertyPrompts, property_prompts
from .scheduling import SchedulingPrompts, scheduling_prompts

__all__ = [
    "SEARCH_AGENT_SYSTEM_PROMPT",
    "SEARCH_CLARIFICATION_PROMPTS", 
    "SEARCH_SUCCESS_TEMPLATES",
    "get_search_prompt",
    "PropertyPrompts",
    "property_prompts",
    "SchedulingPrompts", 
    "scheduling_prompts"
] 