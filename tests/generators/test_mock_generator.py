"""
Tests for Mock Property Generator
"""

import pytest
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.generators.mock_property_generator import MockPropertyGenerator, PropertyData


class TestMockPropertyGenerator:
    """Test mock property generator"""

    def test_generator_initialization(self):
        """Test generator can be initialized"""
        generator = MockPropertyGenerator(seed=42)
        assert generator is not None

    def test_generate_single_property(self):
        """Test generating a single property"""
        generator = MockPropertyGenerator(seed=42)
        property_data = generator.generate_property(1)

        assert isinstance(property_data, PropertyData)
        assert property_data.id == "PROP-000001"
        assert property_data.price > 0
        assert property_data.bedrooms >= 2
        assert property_data.bathrooms >= 1.0
        assert property_data.square_feet > 0
        assert len(property_data.amenities) >= 3
        assert len(property_data.images) >= 3

    def test_property_has_required_fields(self):
        """Test property has all required fields"""
        generator = MockPropertyGenerator(seed=42)
        property_data = generator.generate_property(1)

        required_fields = [
            'id', 'address', 'city', 'state', 'zip_code', 'price',
            'bedrooms', 'bathrooms', 'square_feet', 'lot_size',
            'year_built', 'property_type', 'status', 'description',
            'amenities', 'images', 'latitude', 'longitude',
            'listing_date', 'days_on_market', 'neighborhood',
            'school_rating', 'crime_rating', 'walkability_score',
            'transit_score', 'agent_name', 'agent_phone', 'agent_email'
        ]

        for field in required_fields:
            assert hasattr(property_data, field)
            assert getattr(property_data, field) is not None

    def test_generate_batch(self):
        """Test generating a batch of properties"""
        generator = MockPropertyGenerator(seed=42)
        properties = generator.generate_batch(100)

        assert len(properties) == 100
        assert all(isinstance(p, dict) for p in properties)

        # Check unique IDs
        ids = [p['id'] for p in properties]
        assert len(ids) == len(set(ids))

    def test_property_price_realistic(self):
        """Test property prices are realistic"""
        generator = MockPropertyGenerator(seed=42)
        properties = generator.generate_batch(100)

        prices = [p['price'] for p in properties]
        assert min(prices) >= 50000  # Minimum reasonable price
        assert max(prices) <= 3000000  # Maximum reasonable price
        assert all(p % 5000 == 0 for p in prices)  # Prices rounded to 5k

    def test_coordinates_valid(self):
        """Test coordinates are valid"""
        generator = MockPropertyGenerator(seed=42)
        properties = generator.generate_batch(100)

        for prop in properties:
            lat = prop['latitude']
            lon = prop['longitude']
            assert -90 <= lat <= 90
            assert -180 <= lon <= 180

    def test_reproducible_with_seed(self):
        """Test generator is reproducible with same seed"""
        gen1 = MockPropertyGenerator(seed=42)
        gen2 = MockPropertyGenerator(seed=42)

        prop1 = gen1.generate_property(1)
        prop2 = gen2.generate_property(1)

        assert prop1.id == prop2.id
        assert prop1.price == prop2.price
        assert prop1.address == prop2.address

    def test_different_seeds_produce_different_data(self):
        """Test different seeds produce different data"""
        gen1 = MockPropertyGenerator(seed=42)
        gen2 = MockPropertyGenerator(seed=123)

        prop1 = gen1.generate_property(1)
        prop2 = gen2.generate_property(1)

        # Properties should be different (at least some fields)
        assert prop1.address != prop2.address or prop1.price != prop2.price

    def test_property_types_distribution(self):
        """Test property types are distributed"""
        generator = MockPropertyGenerator(seed=42)
        properties = generator.generate_batch(100)

        property_types = [p['property_type'] for p in properties]
        unique_types = set(property_types)

        # Should have multiple property types
        assert len(unique_types) >= 3

    def test_agent_info_format(self):
        """Test agent information is properly formatted"""
        generator = MockPropertyGenerator(seed=42)
        property_data = generator.generate_property(1)

        # Check email format
        assert '@' in property_data.agent_email
        assert '.com' in property_data.agent_email

        # Check phone format (###) ###-####
        assert len(property_data.agent_phone) >= 13

    def test_listing_date_format(self):
        """Test listing date is valid ISO format"""
        generator = MockPropertyGenerator(seed=42)
        property_data = generator.generate_property(1)

        from datetime import datetime
        # Should be parseable as ISO format
        datetime.fromisoformat(property_data.listing_date)

    def test_save_to_json(self, tmp_path):
        """Test saving properties to JSON"""
        generator = MockPropertyGenerator(seed=42)
        properties = generator.generate_batch(10)

        filepath = tmp_path / "test_properties.json"
        generator.save_to_json(properties, str(filepath))

        assert filepath.exists()

        # Verify can be loaded
        with open(filepath) as f:
            loaded = json.load(f)
        assert len(loaded) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
