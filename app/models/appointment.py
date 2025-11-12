"""
Appointment model for property visits.
"""

from datetime import datetime, date
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, validator


class AppointmentStatus(str, Enum):
    """Appointment status."""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class Appointment(BaseModel):
    """Model for appointment scheduling."""
    id: Optional[int] = Field(None, description="Unique appointment ID")
    user_id: int = Field(..., description="User ID")
    property_id: int = Field(..., description="Property ID")
    
    # Date and time
    scheduled_date: date = Field(..., description="Scheduled date")
    scheduled_time: str = Field(..., description="Scheduled time (HH:MM format)")
    
    # Status and information
    status: AppointmentStatus = Field(default=AppointmentStatus.SCHEDULED, description="Appointment status")
    notes: Optional[str] = Field(None, description="Notes")
    
    # Contact information
    contact_phone: Optional[str] = Field(None, description="Contact phone")
    contact_email: Optional[str] = Field(None, description="Contact email")
    
    # Google Calendar integration
    google_event_id: Optional[str] = Field(None, description="Google Calendar event ID")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now, description="Created date")
    updated_at: datetime = Field(default_factory=datetime.now, description="Updated date")
    
    @validator("scheduled_time")
    def validate_time_format(cls, v):
        """Validate time format."""
        try:
            datetime.strptime(v, "%H:%M")
            return v
        except ValueError:
            raise ValueError("Time must be in HH:MM format")
    
    @property
    def scheduled_datetime(self) -> datetime:
        """Return combined date and time."""
        time_obj = datetime.strptime(self.scheduled_time, "%H:%M").time()
        return datetime.combine(self.scheduled_date, time_obj) 