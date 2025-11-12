"""
Base service protocols for data layer.

Defines interfaces that both mock and real implementations must follow.
"""

from typing import Protocol, List, Dict, Any, Optional
from datetime import datetime


class PropertyServiceProtocol(Protocol):
    """Protocol for property data services."""

    async def search(
        self,
        location: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        bedrooms: Optional[int] = None,
        property_type: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Search for properties based on criteria."""
        ...

    async def get_by_id(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Get property by ID."""
        ...

    async def get_details(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed property information."""
        ...

    async def get_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_miles: float = 5.0,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get properties near a location."""
        ...


class AppointmentServiceProtocol(Protocol):
    """Protocol for appointment/calendar services."""

    async def create_appointment(
        self,
        property_id: str,
        user_email: str,
        start_time: datetime,
        duration_minutes: int = 60,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new appointment."""
        ...

    async def get_appointments(
        self,
        user_email: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get appointments with optional filters."""
        ...

    async def get_appointment(self, appointment_id: str) -> Optional[Dict[str, Any]]:
        """Get appointment by ID."""
        ...

    async def cancel_appointment(self, appointment_id: str) -> bool:
        """Cancel an appointment."""
        ...

    async def get_available_slots(
        self,
        property_id: str,
        date: datetime,
        duration_minutes: int = 60
    ) -> List[datetime]:
        """Get available time slots for a property on a given date."""
        ...
