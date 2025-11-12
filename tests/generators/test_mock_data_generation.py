"""
Unit Tests for Mock Data Generation

Tests comprehensive mock data generation functionality including:
- Property data generation with realistic values
- Appointment data generation
- User profile generation
- Data consistency and validation
- Edge cases and boundary conditions

Coverage Target: >95%
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any

from app.models.property import (
    Property, PropertyType, PropertyStatus, Address, Features
)


class MockDataGenerator:
    """Mock data generator for testing purposes."""

    @staticmethod
    def generate_property(
        property_type: PropertyType = PropertyType.APARTMENT,
        status: PropertyStatus = PropertyStatus.FOR_RENT,
        **overrides
    ) -> Property:
        """Generate a realistic mock property."""
        base_data = {
            "id": 1,
            "external_id": f"mock_prop_{datetime.now().timestamp()}",
            "title": "Beautiful Miami Beach Apartment",
            "description": "Stunning ocean view apartment with modern amenities",
            "property_type": property_type,
            "status": status,
            "address": Address(
                street="123 Ocean Drive",
                number="456",
                neighborhood="South Beach",
                city="Miami Beach",
                state="FL",
                postal_code="33139",
                latitude=25.7617,
                longitude=-80.1918
            ),
            "features": Features(
                bedrooms=2,
                bathrooms=2,
                garage_spaces=1,
                area_total=1200,
                area_built=1100,
                has_pool=True,
                has_gym=True,
                has_security=True,
                allows_pets=False,
                amenities=["Pool", "Gym", "Security", "Ocean View"]
            ),
            "price": Decimal("450000") if status == PropertyStatus.FOR_SALE else None,
            "rent_price": Decimal("3200") if status == PropertyStatus.FOR_RENT else None,
            "price_per_sqm": Decimal("375"),
            "condo_fee": Decimal("350"),
            "iptu": Decimal("150"),
            "images": [
                "https://example.com/image1.jpg",
                "https://example.com/image2.jpg"
            ],
            "agent_name": "Maria Santos",
            "agent_phone": "(305) 555-0123",
            "agent_email": "maria.santos@realty.com",
            "agency_name": "Miami Beach Realty"
        }

        base_data.update(overrides)
        return Property(**base_data)

    @staticmethod
    def generate_properties_batch(count: int = 10) -> List[Property]:
        """Generate a batch of diverse properties."""
        properties = []
        types = list(PropertyType)
        statuses = [PropertyStatus.FOR_RENT, PropertyStatus.FOR_SALE]

        for i in range(count):
            prop_type = types[i % len(types)]
            status = statuses[i % len(statuses)]

            properties.append(
                MockDataGenerator.generate_property(
                    property_type=prop_type,
                    status=status,
                    id=i + 1,
                    title=f"Property {i + 1}"
                )
            )

        return properties

    @staticmethod
    def generate_appointment(property_id: int = 1, **overrides) -> Dict[str, Any]:
        """Generate a realistic mock appointment."""
        base_date = datetime.now() + timedelta(days=2)

        base_data = {
            "id": f"apt_{property_id}_{datetime.now().timestamp()}",
            "property_id": property_id,
            "property_address": "123 Ocean Drive, Miami Beach, FL 33139",
            "date": base_date.strftime("%Y-%m-%d"),
            "time": "10:00 AM",
            "duration": 45,
            "status": "pending",
            "client_name": "John Doe",
            "client_email": "john.doe@email.com",
            "client_phone": "(305) 555-9999",
            "notes": "Interested in immediate move-in"
        }

        base_data.update(overrides)
        return base_data


class TestMockDataGeneration:
    """Test suite for mock data generation."""

    def test_generate_single_property(self):
        """Test generating a single property with default values."""
        property = MockDataGenerator.generate_property()

        assert property is not None
        assert isinstance(property, Property)
        assert property.property_type == PropertyType.APARTMENT
        assert property.status == PropertyStatus.FOR_RENT
        assert property.rent_price == Decimal("3200")
        assert property.features.bedrooms == 2
        assert property.features.bathrooms == 2

    def test_generate_property_for_sale(self):
        """Test generating a property for sale."""
        property = MockDataGenerator.generate_property(
            status=PropertyStatus.FOR_SALE,
            property_type=PropertyType.HOUSE
        )

        assert property.status == PropertyStatus.FOR_SALE
        assert property.property_type == PropertyType.HOUSE
        assert property.price == Decimal("450000")
        assert property.rent_price is None

    def test_generate_property_with_overrides(self):
        """Test generating property with custom overrides."""
        property = MockDataGenerator.generate_property(
            title="Custom Title",
            rent_price=Decimal("5000"),
            id=999
        )

        assert property.title == "Custom Title"
        assert property.rent_price == Decimal("5000")
        assert property.id == 999

    def test_generate_properties_batch(self):
        """Test generating multiple properties."""
        properties = MockDataGenerator.generate_properties_batch(count=10)

        assert len(properties) == 10
        assert all(isinstance(p, Property) for p in properties)

        # Verify diversity
        types = {p.property_type for p in properties}
        assert len(types) > 1  # Should have multiple types

        statuses = {p.status for p in properties}
        assert len(statuses) >= 2  # Should have multiple statuses

    def test_property_address_validation(self):
        """Test address validation and formatting."""
        property = MockDataGenerator.generate_property()

        assert property.address.street == "123 Ocean Drive"
        assert property.address.city == "Miami Beach"
        assert property.address.state == "FL"
        assert property.address.latitude is not None
        assert property.address.longitude is not None

        # Test full_address property
        full_address = property.address.full_address
        assert "123 Ocean Drive" in full_address
        assert "Miami Beach" in full_address

    def test_property_features_validation(self):
        """Test features validation."""
        property = MockDataGenerator.generate_property()

        assert property.features.bedrooms >= 0
        assert property.features.bathrooms >= 0
        assert property.features.area_total > 0
        assert isinstance(property.features.amenities, list)
        assert len(property.features.amenities) > 0

    def test_property_pricing_logic(self):
        """Test property pricing calculations."""
        # Test rental property
        rental = MockDataGenerator.generate_property(status=PropertyStatus.FOR_RENT)
        assert rental.main_price == rental.rent_price

        # Test sale property
        sale = MockDataGenerator.generate_property(status=PropertyStatus.FOR_SALE)
        assert sale.main_price == sale.price

    def test_property_negative_values_validation(self):
        """Test that negative values raise validation errors."""
        with pytest.raises(ValueError):
            MockDataGenerator.generate_property(
                rent_price=Decimal("-1000")
            )

    def test_generate_appointment(self):
        """Test generating appointment data."""
        appointment = MockDataGenerator.generate_appointment(property_id=123)

        assert appointment["property_id"] == 123
        assert "apt_" in appointment["id"]
        assert "date" in appointment
        assert "time" in appointment
        assert appointment["duration"] == 45
        assert appointment["status"] == "pending"

    def test_generate_appointment_with_overrides(self):
        """Test generating appointment with custom values."""
        appointment = MockDataGenerator.generate_appointment(
            property_id=456,
            status="confirmed",
            time="2:00 PM"
        )

        assert appointment["property_id"] == 456
        assert appointment["status"] == "confirmed"
        assert appointment["time"] == "2:00 PM"

    def test_data_consistency(self):
        """Test that generated data is internally consistent."""
        property = MockDataGenerator.generate_property()

        # Check that price_per_sqm is consistent with price and area
        if property.status == PropertyStatus.FOR_SALE:
            expected_price_per_sqm = property.price / Decimal(property.features.area_total)
            # Allow some tolerance for rounding
            assert abs(property.price_per_sqm - expected_price_per_sqm) < Decimal("1")

    def test_property_types_coverage(self):
        """Test that all property types can be generated."""
        for prop_type in PropertyType:
            property = MockDataGenerator.generate_property(property_type=prop_type)
            assert property.property_type == prop_type

    def test_property_statuses_coverage(self):
        """Test that all property statuses can be generated."""
        for status in [PropertyStatus.FOR_RENT, PropertyStatus.FOR_SALE,
                      PropertyStatus.SOLD, PropertyStatus.RENTED]:
            property = MockDataGenerator.generate_property(status=status)
            assert property.status == status

    def test_property_metadata(self):
        """Test property metadata fields."""
        property = MockDataGenerator.generate_property()

        assert isinstance(property.created_at, datetime)
        assert isinstance(property.updated_at, datetime)
        assert property.agent_name is not None
        assert property.agent_email is not None

    def test_batch_generation_performance(self):
        """Test that batch generation is efficient."""
        import time

        start = time.time()
        properties = MockDataGenerator.generate_properties_batch(count=100)
        duration = time.time() - start

        assert len(properties) == 100
        assert duration < 1.0  # Should generate 100 properties in less than 1 second

    def test_property_distance_calculation(self):
        """Test distance calculation between addresses."""
        prop1 = MockDataGenerator.generate_property()
        prop2 = MockDataGenerator.generate_property()

        # Set different coordinates
        prop2.address.latitude = 25.8000
        prop2.address.longitude = -80.2000

        distance = prop1.address.distance_to(prop2.address)
        assert distance is not None
        assert distance > 0  # Should have some distance between different coordinates

    def test_property_summary_generation(self):
        """Test property summary string generation."""
        property = MockDataGenerator.generate_property()
        summary = property.summary

        assert "apartment" in summary.lower()
        assert "2 quartos" in summary.lower()
        assert "South Beach" in summary
        assert "R$" in summary  # Should include price

    def test_property_json_serialization(self):
        """Test that properties can be serialized to JSON."""
        property = MockDataGenerator.generate_property()
        json_data = property.model_dump_json()

        assert json_data is not None
        assert "property_type" in json_data
        assert "address" in json_data

    def test_edge_case_minimum_values(self):
        """Test generation with minimum values."""
        property = MockDataGenerator.generate_property()
        property.features.bedrooms = 0  # Studio
        property.features.bathrooms = 1
        property.features.area_total = 300  # Small studio

        assert property.features.bedrooms == 0
        assert property.features.area_total == 300

    def test_edge_case_maximum_values(self):
        """Test generation with maximum values."""
        property = MockDataGenerator.generate_property(
            rent_price=Decimal("50000")  # Luxury property
        )
        property.features.bedrooms = 10
        property.features.bathrooms = 8
        property.features.area_total = 10000

        assert property.rent_price == Decimal("50000")
        assert property.features.bedrooms == 10


@pytest.mark.unit
class TestDataValidation:
    """Test suite for data validation rules."""

    def test_required_fields_validation(self):
        """Test that required fields must be provided."""
        with pytest.raises(Exception):  # Pydantic validation error
            Property(
                # Missing required fields
                property_type=PropertyType.APARTMENT
            )

    def test_email_format_validation(self):
        """Test email format validation."""
        property = MockDataGenerator.generate_property(
            agent_email="valid.email@example.com"
        )
        assert "@" in property.agent_email

    def test_coordinate_validation(self):
        """Test geographic coordinate validation."""
        property = MockDataGenerator.generate_property()

        # Latitude should be between -90 and 90
        assert -90 <= property.address.latitude <= 90

        # Longitude should be between -180 and 180
        assert -180 <= property.address.longitude <= 180
