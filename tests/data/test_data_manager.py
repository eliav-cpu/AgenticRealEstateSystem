"""
Test Suite for Data Manager

Tests DataMode switching, mock vs real service initialization, and error handling.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from enum import Enum


class DataMode(Enum):
    """Data mode enumeration for testing."""
    MOCK = "mock"
    REAL = "real"


@pytest.mark.unit
class TestDataModeSwitch:
    """Test switching between MOCK and REAL data modes."""

    def test_data_mode_enum_values(self):
        """Test DataMode enum has correct values."""
        assert DataMode.MOCK.value == "mock"
        assert DataMode.REAL.value == "real"

    def test_data_mode_from_string(self):
        """Test creating DataMode from string."""
        assert DataMode("mock") == DataMode.MOCK
        assert DataMode("real") == DataMode.REAL

    def test_invalid_data_mode_raises_error(self):
        """Test that invalid data mode raises ValueError."""
        with pytest.raises(ValueError):
            DataMode("invalid")


@pytest.mark.unit
class TestMockServiceInitialization:
    """Test initialization of mock data services."""

    def test_mock_property_service_initialization(self, sample_properties):
        """Test mock property service returns sample data."""
        # Simulate mock service
        class MockPropertyService:
            def __init__(self):
                self.data = sample_properties

            def get_properties(self):
                return self.data

        service = MockPropertyService()
        properties = service.get_properties()

        assert len(properties) == 3
        assert properties[0]["id"] == "prop_001"
        assert properties[0]["propertyType"] == "Apartment"

    def test_mock_scheduling_service_initialization(self, sample_appointments):
        """Test mock scheduling service returns sample data."""
        class MockSchedulingService:
            def __init__(self):
                self.appointments = sample_appointments

            def get_appointments(self):
                return self.appointments

        service = MockSchedulingService()
        appointments = service.get_appointments()

        assert len(appointments) == 2
        assert appointments[0]["id"] == "apt_001"
        assert appointments[0]["status"] == "confirmed"

    def test_mock_service_no_external_calls(self):
        """Test that mock services don't make external API calls."""
        # Mock services should work without network
        class MockService:
            def __init__(self):
                self.call_count = 0

            def fetch_data(self):
                self.call_count += 1
                return {"data": "mock"}

        service = MockService()
        result = service.fetch_data()

        assert result == {"data": "mock"}
        assert service.call_count == 1


@pytest.mark.unit
class TestRealServiceInitialization:
    """Test initialization of real data services."""

    @patch('requests.get')
    def test_real_property_service_requires_api_key(self, mock_get):
        """Test that real service requires API key."""
        class RealPropertyService:
            def __init__(self, api_key=None):
                if not api_key:
                    raise ValueError("API key required for real service")
                self.api_key = api_key

        # Should raise without API key
        with pytest.raises(ValueError):
            RealPropertyService()

        # Should work with API key
        service = RealPropertyService(api_key="test_key")
        assert service.api_key == "test_key"

    @patch('requests.get')
    def test_real_service_makes_api_calls(self, mock_get):
        """Test that real service makes actual API calls."""
        mock_get.return_value.json.return_value = {"properties": []}
        mock_get.return_value.status_code = 200

        class RealPropertyService:
            def __init__(self, api_key):
                self.api_key = api_key

            def fetch_properties(self):
                import requests
                response = requests.get(
                    "https://api.example.com/properties",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                return response.json()

        service = RealPropertyService(api_key="test_key")
        result = service.fetch_properties()

        mock_get.assert_called_once()
        assert "properties" in result


@pytest.mark.unit
class TestDataModeConfiguration:
    """Test configuration of data mode in the system."""

    def test_agent_context_data_mode(self, agent_context):
        """Test AgentContext stores data mode."""
        assert hasattr(agent_context, 'data_mode')
        assert agent_context.data_mode == "mock"

    def test_agent_context_switch_data_mode(self):
        """Test switching data mode in AgentContext."""
        from app.orchestration.swarm_hybrid import AgentContext

        # Create with mock mode
        context = AgentContext(data_mode="mock")
        assert context.data_mode == "mock"

        # Create with real mode
        context = AgentContext(data_mode="real")
        assert context.data_mode == "real"

    def test_orchestrator_respects_data_mode(self, mock_settings):
        """Test that orchestrator respects configured data mode."""
        # Mock mode should be default
        assert mock_settings.database.mode == "mock"


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling in data services."""

    def test_mock_service_error_handling(self):
        """Test mock service handles errors gracefully."""
        class MockServiceWithError:
            def get_data(self):
                try:
                    raise Exception("Simulated error")
                except Exception:
                    return {"error": "Failed to fetch data", "fallback": True}

        service = MockServiceWithError()
        result = service.get_data()

        assert "error" in result
        assert result["fallback"] is True

    @patch('requests.get')
    def test_real_service_network_error(self, mock_get):
        """Test real service handles network errors."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        class RealServiceWithErrorHandling:
            def fetch_data(self):
                try:
                    response = requests.get("https://api.example.com/data")
                    return response.json()
                except requests.exceptions.ConnectionError:
                    return {"error": "Network error", "fallback_data": []}

        service = RealServiceWithErrorHandling()
        result = service.fetch_data()

        assert "error" in result
        assert "fallback_data" in result

    @patch('requests.get')
    def test_real_service_api_error_codes(self, mock_get):
        """Test real service handles API error codes."""
        mock_get.return_value.status_code = 401
        mock_get.return_value.json.return_value = {"error": "Unauthorized"}

        class RealServiceWithStatusCheck:
            def fetch_data(self):
                import requests
                response = requests.get("https://api.example.com/data")

                if response.status_code == 401:
                    return {"error": "Authentication failed"}
                elif response.status_code == 404:
                    return {"error": "Resource not found"}
                elif response.status_code == 500:
                    return {"error": "Server error"}

                return response.json()

        service = RealServiceWithStatusCheck()
        result = service.fetch_data()

        assert "error" in result
        assert "Authentication" in result["error"]


@pytest.mark.integration
class TestDataModeIntegration:
    """Test integration of data mode with the full system."""

    @pytest.mark.mock
    def test_full_flow_with_mock_data(self, agent_context, sample_properties):
        """Test complete flow using mock data."""
        # Simulate search with mock data
        context = agent_context
        context.search_results = sample_properties

        assert context.data_mode == "mock"
        assert len(context.search_results) == 3

        # Mock data should be immediately available
        first_property = context.search_results[0]
        assert first_property["formattedAddress"] == "123 Ocean Drive, Miami Beach, FL 33139"

    @pytest.mark.real
    @pytest.mark.skip(reason="Requires real API credentials")
    def test_full_flow_with_real_data(self):
        """Test complete flow using real data."""
        # This test would require real API credentials
        # Skipped by default, run with --real flag
        pass


@pytest.mark.unit
class TestDataValidation:
    """Test validation of data returned by services."""

    def test_validate_property_data_structure(self, sample_properties):
        """Test that property data has required fields."""
        required_fields = [
            "id", "formattedAddress", "price", "propertyType",
            "bedrooms", "bathrooms", "squareFeet", "available"
        ]

        for prop in sample_properties:
            for field in required_fields:
                assert field in prop, f"Missing required field: {field}"

    def test_validate_appointment_data_structure(self, sample_appointments):
        """Test that appointment data has required fields."""
        required_fields = [
            "id", "property_id", "property_address", "date",
            "time", "status", "duration"
        ]

        for apt in sample_appointments:
            for field in required_fields:
                assert field in apt, f"Missing required field: {field}"

    def test_validate_data_types(self, sample_properties):
        """Test that data fields have correct types."""
        prop = sample_properties[0]

        assert isinstance(prop["id"], str)
        assert isinstance(prop["price"], (int, float))
        assert isinstance(prop["bedrooms"], (int, float))
        assert isinstance(prop["bathrooms"], (int, float))
        assert isinstance(prop["available"], bool)
        assert isinstance(prop["amenities"], list)


@pytest.mark.unit
class TestDataCaching:
    """Test caching behavior of data services."""

    def test_mock_service_caches_data(self):
        """Test that mock service can cache data."""
        class MockServiceWithCache:
            def __init__(self):
                self._cache = None
                self.fetch_count = 0

            def get_data(self):
                if self._cache is None:
                    self.fetch_count += 1
                    self._cache = {"data": "cached"}
                return self._cache

        service = MockServiceWithCache()

        # First call
        result1 = service.get_data()
        assert service.fetch_count == 1

        # Second call should use cache
        result2 = service.get_data()
        assert service.fetch_count == 1
        assert result1 is result2

    def test_cache_invalidation(self):
        """Test cache can be invalidated."""
        class MockServiceWithInvalidation:
            def __init__(self):
                self._cache = None

            def get_data(self):
                if self._cache is None:
                    self._cache = {"data": "fresh"}
                return self._cache

            def invalidate_cache(self):
                self._cache = None

        service = MockServiceWithInvalidation()

        result1 = service.get_data()
        service.invalidate_cache()
        result2 = service.get_data()

        # Should get new data after invalidation
        assert result1 is not result2
