"""
Real API services for production.

Integrates with RentCast API for property data and Google Calendar for appointments.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class RealPropertyService:
    """Real property service using RentCast API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("RENTCAST_API_KEY", "")
        self.base_url = "https://api.rentcast.io/v1"
        self.timeout = httpx.Timeout(30.0)

        if not self.api_key:
            raise ValueError(
                "RentCast API key not found. "
                "Set RENTCAST_API_KEY environment variable."
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to RentCast API with retry logic."""
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

        url = f"{self.base_url}/{endpoint}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data
            )

            response.raise_for_status()
            return response.json()

    async def search(
        self,
        location: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        bedrooms: Optional[int] = None,
        property_type: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Search for properties using RentCast API."""
        params = {}

        if location:
            params["city"] = location

        if min_price is not None:
            params["minPrice"] = min_price

        if max_price is not None:
            params["maxPrice"] = max_price

        if bedrooms is not None:
            params["bedrooms"] = bedrooms

        if property_type:
            params["propertyType"] = property_type

        # Add any additional kwargs
        params.update(kwargs)

        try:
            result = await self._request("GET", "listings", params=params)
            return result.get("listings", [])
        except httpx.HTTPError as e:
            print(f"Error searching properties: {e}")
            return []

    async def get_by_id(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Get property by ID from RentCast."""
        try:
            result = await self._request("GET", f"listings/{property_id}")
            return result
        except httpx.HTTPError as e:
            print(f"Error getting property {property_id}: {e}")
            return None

    async def get_details(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed property information from RentCast."""
        return await self.get_by_id(property_id)

    async def get_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_miles: float = 5.0,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get properties near a location using RentCast."""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius_miles,
            "limit": limit
        }

        try:
            result = await self._request("GET", "listings/nearby", params=params)
            return result.get("listings", [])
        except httpx.HTTPError as e:
            print(f"Error getting nearby properties: {e}")
            return []


class RealAppointmentService:
    """Real appointment service using Google Calendar API."""

    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize with Google Calendar credentials.

        Args:
            credentials_path: Path to Google OAuth2 credentials JSON file
        """
        self.credentials_path = credentials_path or os.getenv(
            "GOOGLE_CALENDAR_CREDENTIALS",
            ""
        )
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        self._service = None

        if not self.credentials_path:
            raise ValueError(
                "Google Calendar credentials not found. "
                "Set GOOGLE_CALENDAR_CREDENTIALS environment variable."
            )

    async def _get_service(self):
        """Get authenticated Google Calendar service."""
        if self._service is not None:
            return self._service

        # Note: In production, implement proper OAuth2 flow
        # This is a placeholder for the actual implementation
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from google.auth.transport.requests import Request

            # Load credentials from file
            # In production, handle token refresh, etc.
            creds = Credentials.from_authorized_user_file(
                self.credentials_path,
                scopes=["https://www.googleapis.com/auth/calendar"]
            )

            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())

            self._service = build("calendar", "v3", credentials=creds)
            return self._service

        except Exception as e:
            raise RuntimeError(f"Failed to initialize Google Calendar: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def create_appointment(
        self,
        property_id: str,
        user_email: str,
        start_time: datetime,
        duration_minutes: int = 60,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create appointment in Google Calendar."""
        service = await self._get_service()

        end_time = start_time + timedelta(minutes=duration_minutes)

        event = {
            "summary": f"Property Viewing: {property_id}",
            "description": notes or f"Property viewing for {property_id}",
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "UTC"
            },
            "attendees": [
                {"email": user_email}
            ],
            "extendedProperties": {
                "private": {
                    "property_id": property_id
                }
            }
        }

        try:
            # Execute in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            created_event = await loop.run_in_executor(
                None,
                lambda: service.events().insert(
                    calendarId=self.calendar_id,
                    body=event
                ).execute()
            )

            return {
                "id": created_event["id"],
                "property_id": property_id,
                "user_email": user_email,
                "start_time": created_event["start"]["dateTime"],
                "end_time": created_event["end"]["dateTime"],
                "duration_minutes": duration_minutes,
                "status": "scheduled",
                "notes": notes or "",
                "created_at": created_event["created"],
                "updated_at": created_event["updated"]
            }

        except Exception as e:
            raise RuntimeError(f"Failed to create appointment: {e}")

    async def get_appointments(
        self,
        user_email: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get appointments from Google Calendar."""
        service = await self._get_service()

        # Build query parameters
        params = {
            "calendarId": self.calendar_id,
            "singleEvents": True,
            "orderBy": "startTime"
        }

        if start_date:
            params["timeMin"] = start_date.isoformat() + "Z"

        if end_date:
            params["timeMax"] = end_date.isoformat() + "Z"

        try:
            loop = asyncio.get_event_loop()
            events_result = await loop.run_in_executor(
                None,
                lambda: service.events().list(**params).execute()
            )

            events = events_result.get("items", [])

            # Filter by user email if provided
            if user_email:
                events = [
                    e for e in events
                    if any(
                        a.get("email", "").lower() == user_email.lower()
                        for a in e.get("attendees", [])
                    )
                ]

            # Transform to standard format
            appointments = []
            for event in events:
                property_id = event.get("extendedProperties", {}).get(
                    "private", {}
                ).get("property_id", "")

                appointments.append({
                    "id": event["id"],
                    "property_id": property_id,
                    "user_email": user_email or "",
                    "start_time": event["start"].get("dateTime", ""),
                    "end_time": event["end"].get("dateTime", ""),
                    "status": event.get("status", "confirmed"),
                    "notes": event.get("description", ""),
                    "created_at": event.get("created", ""),
                    "updated_at": event.get("updated", "")
                })

            return appointments

        except Exception as e:
            print(f"Error getting appointments: {e}")
            return []

    async def get_appointment(self, appointment_id: str) -> Optional[Dict[str, Any]]:
        """Get single appointment from Google Calendar."""
        service = await self._get_service()

        try:
            loop = asyncio.get_event_loop()
            event = await loop.run_in_executor(
                None,
                lambda: service.events().get(
                    calendarId=self.calendar_id,
                    eventId=appointment_id
                ).execute()
            )

            property_id = event.get("extendedProperties", {}).get(
                "private", {}
            ).get("property_id", "")

            return {
                "id": event["id"],
                "property_id": property_id,
                "start_time": event["start"].get("dateTime", ""),
                "end_time": event["end"].get("dateTime", ""),
                "status": event.get("status", "confirmed"),
                "notes": event.get("description", ""),
                "created_at": event.get("created", ""),
                "updated_at": event.get("updated", "")
            }

        except Exception as e:
            print(f"Error getting appointment {appointment_id}: {e}")
            return None

    async def cancel_appointment(self, appointment_id: str) -> bool:
        """Cancel appointment in Google Calendar."""
        service = await self._get_service()

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: service.events().delete(
                    calendarId=self.calendar_id,
                    eventId=appointment_id
                ).execute()
            )
            return True

        except Exception as e:
            print(f"Error cancelling appointment {appointment_id}: {e}")
            return False

    async def get_available_slots(
        self,
        property_id: str,
        date: datetime,
        duration_minutes: int = 60
    ) -> List[datetime]:
        """Get available time slots for a property."""
        # Get all appointments for the day
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        appointments = await self.get_appointments(
            start_date=start_of_day,
            end_date=end_of_day
        )

        # Filter appointments for this property
        property_appointments = [
            a for a in appointments
            if a["property_id"] == property_id
        ]

        # Generate slots from 9 AM to 5 PM
        business_start = date.replace(hour=9, minute=0, second=0, microsecond=0)
        business_end = date.replace(hour=17, minute=0, second=0, microsecond=0)

        available_slots = []
        current = business_start

        while current < business_end:
            slot_end = current + timedelta(minutes=duration_minutes)

            # Check if slot overlaps with existing appointments
            is_available = True
            for appt in property_appointments:
                appt_start = datetime.fromisoformat(
                    appt["start_time"].replace("Z", "")
                )
                appt_end = datetime.fromisoformat(
                    appt["end_time"].replace("Z", "")
                )

                if current < appt_end and slot_end > appt_start:
                    is_available = False
                    break

            if is_available:
                available_slots.append(current)

            current += timedelta(hours=1)

        return available_slots
