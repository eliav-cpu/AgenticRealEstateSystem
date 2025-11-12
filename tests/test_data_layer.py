"""
Tests for data layer - mock and real implementations.

Run with: pytest tests/test_data_layer.py -v
"""

import pytest
from datetime import datetime, timedelta
from app.data import DataManager, DataMode
from app.data.mock_system import MockPropertyService, MockAppointmentService


@pytest.fixture
def reset_data_manager():
    """Reset DataManager after each test."""
    yield
    DataManager.reset_services()


@pytest.fixture
def mock_mode():
    """Force mock mode for tests."""
    DataManager.set_mode(DataMode.MOCK)
    yield
    DataManager.reset_services()


class TestDataManager:
    """Test DataManager factory."""

    def test_get_current_mode(self, mock_mode):
        """Test getting current data mode."""
        mode = DataManager.get_current_mode()
        assert mode == DataMode.MOCK

    def test_get_property_service_mock(self, mock_mode):
        """Test getting mock property service."""
        service = DataManager.get_property_service()
        assert isinstance(service, MockPropertyService)

    def test_get_appointment_service_mock(self, mock_mode):
        """Test getting mock appointment service."""
        service = DataManager.get_appointment_service()
        assert isinstance(service, MockAppointmentService)

    def test_singleton_pattern(self, mock_mode):
        """Test that services are singletons."""
        service1 = DataManager.get_property_service()
        service2 = DataManager.get_property_service()
        assert service1 is service2

    def test_set_mode(self, reset_data_manager):
        """Test programmatic mode switching."""
        DataManager.set_mode(DataMode.MOCK)
        assert DataManager.get_current_mode() == DataMode.MOCK

        DataManager.set_mode(DataMode.REAL)
        assert DataManager.get_current_mode() == DataMode.REAL


class TestMockPropertyService:
    """Test mock property service implementation."""

    @pytest.mark.asyncio
    async def test_search_all_properties(self, mock_mode):
        """Test searching without filters returns all properties."""
        service = DataManager.get_property_service()
        results = await service.search()

        assert len(results) == 5
        assert all(isinstance(p, dict) for p in results)
        assert all("id" in p for p in results)

    @pytest.mark.asyncio
    async def test_search_by_location(self, mock_mode):
        """Test searching by location."""
        service = DataManager.get_property_service()

        # Search San Francisco
        sf_results = await service.search(location="San Francisco")
        assert len(sf_results) == 2
        assert all("San Francisco" in p["city"] for p in sf_results)

        # Search Oakland
        oak_results = await service.search(location="Oakland")
        assert len(oak_results) == 1
        assert oak_results[0]["city"] == "Oakland"

    @pytest.mark.asyncio
    async def test_search_by_price_range(self, mock_mode):
        """Test searching by price range."""
        service = DataManager.get_property_service()

        # Search 2000-3500 range
        results = await service.search(min_price=2000, max_price=3500)
        assert all(2000 <= p["price"] <= 3500 for p in results)
        assert len(results) == 3  # props 001, 002, 004

    @pytest.mark.asyncio
    async def test_search_by_bedrooms(self, mock_mode):
        """Test searching by minimum bedrooms."""
        service = DataManager.get_property_service()

        # Search for 3+ bedrooms
        results = await service.search(bedrooms=3)
        assert all(p["bedrooms"] >= 3 for p in results)
        assert len(results) == 2  # props 003, 005

    @pytest.mark.asyncio
    async def test_search_by_property_type(self, mock_mode):
        """Test searching by property type."""
        service = DataManager.get_property_service()

        # Search apartments
        apartments = await service.search(property_type="apartment")
        assert all(p["property_type"] == "apartment" for p in apartments)
        assert len(apartments) == 3

        # Search houses
        houses = await service.search(property_type="house")
        assert len(houses) == 1
        assert houses[0]["property_type"] == "house"

    @pytest.mark.asyncio
    async def test_search_combined_filters(self, mock_mode):
        """Test searching with multiple filters."""
        service = DataManager.get_property_service()

        results = await service.search(
            location="San Francisco",
            min_price=3000,
            bedrooms=2
        )

        assert len(results) == 2  # props 001 and 005
        assert all(p["city"] == "San Francisco" for p in results)
        assert all(p["price"] >= 3000 for p in results)
        assert all(p["bedrooms"] >= 2 for p in results)

    @pytest.mark.asyncio
    async def test_get_by_id(self, mock_mode):
        """Test getting property by ID."""
        service = DataManager.get_property_service()

        # Valid ID
        prop = await service.get_by_id("prop_001")
        assert prop is not None
        assert prop["id"] == "prop_001"
        assert prop["address"] == "123 Main St"

        # Invalid ID
        missing = await service.get_by_id("prop_999")
        assert missing is None

    @pytest.mark.asyncio
    async def test_get_details(self, mock_mode):
        """Test getting property details."""
        service = DataManager.get_property_service()

        details = await service.get_details("prop_003")
        assert details is not None
        assert details["property_type"] == "house"
        assert "yard" in details["amenities"]

    @pytest.mark.asyncio
    async def test_get_nearby(self, mock_mode):
        """Test getting nearby properties."""
        service = DataManager.get_property_service()

        # San Francisco coordinates
        sf_lat, sf_lon = 37.7749, -122.4194

        nearby = await service.get_nearby(
            latitude=sf_lat,
            longitude=sf_lon,
            radius_miles=10.0,
            limit=5
        )

        assert len(nearby) > 0
        assert all("distance_miles" in p for p in nearby)
        # Results should be sorted by distance
        distances = [p["distance_miles"] for p in nearby]
        assert distances == sorted(distances)


class TestMockAppointmentService:
    """Test mock appointment service implementation."""

    @pytest.mark.asyncio
    async def test_create_appointment(self, mock_mode):
        """Test creating an appointment."""
        service = DataManager.get_appointment_service()

        start_time = datetime.now() + timedelta(days=1)
        appointment = await service.create_appointment(
            property_id="prop_001",
            user_email="test@example.com",
            start_time=start_time,
            duration_minutes=60,
            notes="Test appointment"
        )

        assert appointment is not None
        assert appointment["property_id"] == "prop_001"
        assert appointment["user_email"] == "test@example.com"
        assert appointment["duration_minutes"] == 60
        assert appointment["status"] == "scheduled"
        assert appointment["notes"] == "Test appointment"

    @pytest.mark.asyncio
    async def test_get_appointments_all(self, mock_mode):
        """Test getting all appointments."""
        service = DataManager.get_appointment_service()

        appointments = await service.get_appointments()
        assert len(appointments) >= 3  # At least the fixture data

    @pytest.mark.asyncio
    async def test_get_appointments_by_email(self, mock_mode):
        """Test filtering appointments by email."""
        service = DataManager.get_appointment_service()

        # Create test appointment
        start_time = datetime.now() + timedelta(days=2)
        await service.create_appointment(
            property_id="prop_001",
            user_email="unique@example.com",
            start_time=start_time,
            duration_minutes=60
        )

        # Get appointments for that user
        appointments = await service.get_appointments(
            user_email="unique@example.com"
        )

        assert len(appointments) >= 1
        assert all(
            a["user_email"].lower() == "unique@example.com"
            for a in appointments
        )

    @pytest.mark.asyncio
    async def test_get_appointments_by_date_range(self, mock_mode):
        """Test filtering appointments by date range."""
        service = DataManager.get_appointment_service()

        # Create appointments at specific times
        base_time = datetime(2025, 12, 1, 10, 0, 0)

        await service.create_appointment(
            property_id="prop_001",
            user_email="user1@example.com",
            start_time=base_time,
            duration_minutes=60
        )

        await service.create_appointment(
            property_id="prop_002",
            user_email="user2@example.com",
            start_time=base_time + timedelta(days=5),
            duration_minutes=60
        )

        # Query with date range
        appointments = await service.get_appointments(
            start_date=base_time - timedelta(days=1),
            end_date=base_time + timedelta(days=2)
        )

        # Should only get first appointment
        december_appointments = [
            a for a in appointments
            if a["start_time"].startswith("2025-12")
        ]
        assert len(december_appointments) >= 1

    @pytest.mark.asyncio
    async def test_get_appointment_by_id(self, mock_mode):
        """Test getting single appointment."""
        service = DataManager.get_appointment_service()

        # Valid ID (from fixture)
        appointment = await service.get_appointment("appt_001")
        assert appointment is not None
        assert appointment["id"] == "appt_001"

        # Invalid ID
        missing = await service.get_appointment("appt_999")
        assert missing is None

    @pytest.mark.asyncio
    async def test_cancel_appointment(self, mock_mode):
        """Test cancelling an appointment."""
        service = DataManager.get_appointment_service()

        # Cancel fixture appointment
        success = await service.cancel_appointment("appt_001")
        assert success is True

        # Verify it's cancelled
        appointment = await service.get_appointment("appt_001")
        assert appointment["status"] == "cancelled"

        # Try to cancel non-existent
        failed = await service.cancel_appointment("appt_999")
        assert failed is False

    @pytest.mark.asyncio
    async def test_get_available_slots(self, mock_mode):
        """Test getting available time slots."""
        service = DataManager.get_appointment_service()

        # Get slots for a future date
        test_date = datetime.now() + timedelta(days=7)
        slots = await service.get_available_slots(
            property_id="prop_001",
            date=test_date,
            duration_minutes=60
        )

        assert len(slots) > 0
        # Should have hourly slots from 9 AM to 5 PM
        assert len(slots) <= 8

        # All slots should be within business hours
        for slot in slots:
            assert 9 <= slot.hour < 17

    @pytest.mark.asyncio
    async def test_available_slots_with_conflicts(self, mock_mode):
        """Test that available slots exclude existing appointments."""
        service = DataManager.get_appointment_service()

        test_date = datetime.now() + timedelta(days=10)

        # Create appointment at 2 PM
        await service.create_appointment(
            property_id="prop_001",
            user_email="blocker@example.com",
            start_time=test_date.replace(hour=14, minute=0),
            duration_minutes=60
        )

        # Get available slots
        slots = await service.get_available_slots(
            property_id="prop_001",
            date=test_date,
            duration_minutes=60
        )

        # 2 PM slot should not be available
        slot_hours = [s.hour for s in slots]
        assert 14 not in slot_hours


class TestDataStructures:
    """Test data structure consistency."""

    @pytest.mark.asyncio
    async def test_property_structure(self, mock_mode):
        """Test that properties have required fields."""
        service = DataManager.get_property_service()
        properties = await service.search()

        required_fields = [
            "id", "address", "city", "state", "zip_code",
            "price", "bedrooms", "bathrooms", "square_feet",
            "property_type", "description"
        ]

        for prop in properties:
            for field in required_fields:
                assert field in prop, f"Missing field: {field}"
                assert prop[field] is not None

    @pytest.mark.asyncio
    async def test_appointment_structure(self, mock_mode):
        """Test that appointments have required fields."""
        service = DataManager.get_appointment_service()

        start_time = datetime.now() + timedelta(days=1)
        appointment = await service.create_appointment(
            property_id="prop_001",
            user_email="test@example.com",
            start_time=start_time,
            duration_minutes=60
        )

        required_fields = [
            "id", "property_id", "user_email",
            "start_time", "end_time", "duration_minutes",
            "status", "created_at", "updated_at"
        ]

        for field in required_fields:
            assert field in appointment, f"Missing field: {field}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
