"""
Modelos de dados para o sistema agêntico.
"""

from .property import (
    Property,
    PropertyType,
    PropertyStatus,
    Address,
    Features,
    SearchCriteria,
    SearchResult
)
from .user import (
    UserProfile,
    ConversationMessage
)
from .appointment import (
    Appointment,
    AppointmentStatus
)
from .response import (
    AgentResponse
)

__all__ = [
    # Property models
    "Property",
    "PropertyType", 
    "PropertyStatus",
    "Address",
    "Features",
    "SearchCriteria",
    "SearchResult",
    
    # User models
    "UserProfile",
    "ConversationMessage",
    
    # Appointment models
    "Appointment",
    "AppointmentStatus",
    
    # Response models
    "AgentResponse"
] 