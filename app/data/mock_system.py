"""
Mock data services for development and testing.

Provides realistic property and appointment data without external API calls.
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import asyncio


class MockPropertyService:
    """Mock property service using JSON fixture data."""

    def __init__(self):
        self._properties = self._load_properties()

    def _load_properties(self) -> List[Dict[str, Any]]:
        """Load properties from JSON fixture file."""
        fixtures_path = Path(__file__).parent / "fixtures" / "properties.json"

        if not fixtures_path.exists():
            return []

        with open(fixtures_path, "r") as f:
            return json.load(f)

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
        # Simulate async operation
        await asyncio.sleep(0.1)

        results = self._properties.copy()

        # Filter by location (city or state)
        if location:
            location_lower = location.lower()
            results = [
                p for p in results
                if location_lower in p["city"].lower()
                or location_lower in p["state"].lower()
                or location_lower in p["zip_code"]
            ]

        # Filter by price range
        if min_price is not None:
            results = [p for p in results if p["price"] >= min_price]

        if max_price is not None:
            results = [p for p in results if p["price"] <= max_price]

        # Filter by bedrooms
        if bedrooms is not None:
            results = [p for p in results if p["bedrooms"] >= bedrooms]

        # Filter by property type
        if property_type:
            property_type_lower = property_type.lower()
            results = [
                p for p in results
                if p["property_type"].lower() == property_type_lower
            ]

        return results

    async def get_by_id(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Get property by ID."""
        await asyncio.sleep(0.05)

        for prop in self._properties:
            if prop["id"] == property_id:
                return prop.copy()

        return None

    async def get_details(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed property information (same as get_by_id for mock)."""
        return await self.get_by_id(property_id)

    async def get_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_miles: float = 5.0,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get properties near a location."""
        await asyncio.sleep(0.1)

        # Simple distance calculation (haversine approximation)
        def distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
            """Calculate approximate distance in miles."""
            # Rough approximation: 1 degree ≈ 69 miles
            dlat = abs(lat2 - lat1)
            dlon = abs(lon2 - lon1)
            return ((dlat ** 2 + dlon ** 2) ** 0.5) * 69

        results = []
        for prop in self._properties:
            dist = distance(
                latitude,
                longitude,
                prop["latitude"],
                prop["longitude"]
            )
            if dist <= radius_miles:
                prop_with_distance = prop.copy()
                prop_with_distance["distance_miles"] = round(dist, 2)
                results.append(prop_with_distance)

        # Sort by distance and limit results
        results.sort(key=lambda x: x["distance_miles"])
        return results[:limit]


class MockAppointmentService:
    """Mock appointment service using JSON fixture data."""

    def __init__(self):
        self._appointments = self._load_appointments()
        self._next_id = len(self._appointments) + 1

    def _load_appointments(self) -> List[Dict[str, Any]]:
        """Load appointments from JSON fixture file."""
        fixtures_path = Path(__file__).parent / "fixtures" / "appointments.json"

        if not fixtures_path.exists():
            return []

        with open(fixtures_path, "r") as f:
            return json.load(f)

    async def create_appointment(
        self,
        property_id: str,
        user_email: str,
        start_time: datetime,
        duration_minutes: int = 60,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new appointment."""
        await asyncio.sleep(0.1)

        end_time = start_time + timedelta(minutes=duration_minutes)
        now = datetime.now()

        appointment = {
            "id": f"appt_{self._next_id:03d}",
            "property_id": property_id,
            "user_email": user_email,
            "start_time": start_time.isoformat() + "Z",
            "end_time": end_time.isoformat() + "Z",
            "duration_minutes": duration_minutes,
            "status": "scheduled",
            "notes": notes or "",
            "created_at": now.isoformat() + "Z",
            "updated_at": now.isoformat() + "Z"
        }

        self._appointments.append(appointment)
        self._next_id += 1

        return appointment.copy()

    async def get_appointments(
        self,
        user_email: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get appointments with optional filters."""
        await asyncio.sleep(0.1)

        results = self._appointments.copy()

        # Filter by user email
        if user_email:
            results = [
                a for a in results
                if a["user_email"].lower() == user_email.lower()
            ]

        # Filter by date range
        if start_date:
            start_str = start_date.isoformat()
            results = [a for a in results if a["start_time"] >= start_str]

        if end_date:
            end_str = end_date.isoformat()
            results = [a for a in results if a["start_time"] <= end_str]

        return results

    async def get_appointment(self, appointment_id: str) -> Optional[Dict[str, Any]]:
        """Get appointment by ID."""
        await asyncio.sleep(0.05)

        for appt in self._appointments:
            if appt["id"] == appointment_id:
                return appt.copy()

        return None

    async def cancel_appointment(self, appointment_id: str) -> bool:
        """Cancel an appointment."""
        await asyncio.sleep(0.1)

        for appt in self._appointments:
            if appt["id"] == appointment_id:
                appt["status"] = "cancelled"
                appt["updated_at"] = datetime.now().isoformat() + "Z"
                return True

        return False

    async def get_available_slots(
        self,
        property_id: str,
        date: datetime,
        duration_minutes: int = 60
    ) -> List[datetime]:
        """Get available time slots for a property on a given date."""
        await asyncio.sleep(0.1)

        # Generate slots from 9 AM to 5 PM
        start_of_day = date.replace(hour=9, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=17, minute=0, second=0, microsecond=0)

        # Get existing appointments for this property on this date
        existing = [
            a for a in self._appointments
            if a["property_id"] == property_id
            and a["status"] == "scheduled"
            and datetime.fromisoformat(a["start_time"].replace("Z", "")).date() == date.date()
        ]

        # Generate hourly slots
        available_slots = []
        current = start_of_day

        while current < end_of_day:
            # Check if slot overlaps with existing appointments
            is_available = True
            slot_end = current + timedelta(minutes=duration_minutes)

            for appt in existing:
                appt_start = datetime.fromisoformat(appt["start_time"].replace("Z", ""))
                appt_end = datetime.fromisoformat(appt["end_time"].replace("Z", ""))

                # Check for overlap
                if (current < appt_end and slot_end > appt_start):
                    is_available = False
                    break

            if is_available:
                available_slots.append(current)

            current += timedelta(hours=1)

        return available_slots
