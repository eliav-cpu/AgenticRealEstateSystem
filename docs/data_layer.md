# Data Layer Architecture

## Overview

The data layer provides a clean separation between mock data (for development/testing) and real API integrations (for production). This architecture allows seamless switching between data sources without changing application code.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Application Code                   │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │  DataManager   │  ◄── Factory Pattern
         │   (Factory)    │
         └───┬────────┬───┘
             │        │
     ┌───────┘        └────────┐
     ▼                         ▼
┌─────────────┐       ┌──────────────┐
│ Mock System │       │ Real API     │
│             │       │ System       │
│ - Properties│       │ - RentCast   │
│ - Appts     │       │ - Google Cal │
└─────────────┘       └──────────────┘
     │                       │
     ▼                       ▼
┌─────────────┐       ┌──────────────┐
│ JSON Files  │       │ External APIs│
└─────────────┘       └──────────────┘
```

## Components

### 1. Base Services (Protocols)

**File**: `/mnt/c/Users/DaviCastroSamora/Documents/SamoraDC/AgenticRealEstateSystem/app/data/base_services.py`

Defines the interface that all implementations must follow:

- `PropertyServiceProtocol`: Interface for property data operations
- `AppointmentServiceProtocol`: Interface for appointment/calendar operations

**Key Methods**:

#### PropertyServiceProtocol
```python
async def search(location, min_price, max_price, bedrooms, property_type) -> List[Dict]
async def get_by_id(property_id: str) -> Optional[Dict]
async def get_details(property_id: str) -> Optional[Dict]
async def get_nearby(latitude, longitude, radius_miles, limit) -> List[Dict]
```

#### AppointmentServiceProtocol
```python
async def create_appointment(property_id, user_email, start_time, duration_minutes, notes) -> Dict
async def get_appointments(user_email, start_date, end_date) -> List[Dict]
async def get_appointment(appointment_id: str) -> Optional[Dict]
async def cancel_appointment(appointment_id: str) -> bool
async def get_available_slots(property_id, date, duration_minutes) -> List[datetime]
```

### 2. Mock System

**File**: `/mnt/c/Users/DaviCastroSamora/Documents/SamoraDC/AgenticRealEstateSystem/app/data/mock_system.py`

Implements services using local JSON fixture data.

**Features**:
- ✅ No external API calls
- ✅ Fast response times (100ms simulated delay)
- ✅ Realistic data for 5 properties in Bay Area
- ✅ In-memory appointment management
- ✅ Full search and filtering capabilities
- ✅ Distance-based property search

**Mock Data Location**: `/mnt/c/Users/DaviCastroSamora/Documents/SamoraDC/AgenticRealEstateSystem/app/data/fixtures/`
- `properties.json` - Sample property listings
- `appointments.json` - Sample appointments

### 3. Real API System

**File**: `/mnt/c/Users/DaviCastroSamora/Documents/SamoraDC/AgenticRealEstateSystem/app/data/real_api_system.py`

Implements services using external APIs.

**Features**:
- ✅ RentCast API integration for property data
- ✅ Google Calendar API for appointments
- ✅ Automatic retry logic (3 attempts with exponential backoff)
- ✅ Proper error handling
- ✅ 30-second timeout protection
- ✅ Async/await for non-blocking operations

**Required Environment Variables**:
```bash
RENTCAST_API_KEY=your_rentcast_api_key
GOOGLE_CALENDAR_CREDENTIALS=path/to/credentials.json
GOOGLE_CALENDAR_ID=primary
```

### 4. Data Manager (Factory)

**File**: `/mnt/c/Users/DaviCastroSamora/Documents/SamoraDC/AgenticRealEstateSystem/app/data/data_manager.py`

Factory class that provides the correct service implementation based on configuration.

**Features**:
- ✅ Singleton pattern for consistency
- ✅ Automatic fallback to mock if real APIs fail
- ✅ Mode switching via environment variable
- ✅ Service reset capability for testing

## Configuration

### Environment Variables

Set in `.env` file or environment:

```bash
# Data Layer Configuration
DATA_MODE=mock                    # Options: mock, real

# For REAL mode - RentCast API
RENTCAST_API_KEY=your_api_key

# For REAL mode - Google Calendar
GOOGLE_CALENDAR_CREDENTIALS=/path/to/credentials.json
GOOGLE_CALENDAR_ID=primary
```

### Settings Configuration

The data layer configuration is integrated into `/mnt/c/Users/DaviCastroSamora/Documents/SamoraDC/AgenticRealEstateSystem/config/settings.py`:

```python
class DataLayerConfig(BaseSettings):
    mode: str = Field(default="mock")  # "mock" or "real"
    mock_data_path: str = Field(default="app/data/fixtures")
```

Access via:
```python
from config.settings import get_settings

settings = get_settings()
data_mode = settings.data_layer.mode  # "mock" or "real"
```

## Usage Examples

### Basic Usage

```python
from app.data import DataManager

# Get services - automatically uses mock or real based on settings
property_service = DataManager.get_property_service()
appointment_service = DataManager.get_appointment_service()

# Search for properties
properties = await property_service.search(
    location="San Francisco",
    min_price=2000,
    max_price=4000,
    bedrooms=2
)

# Get property details
property_detail = await property_service.get_by_id("prop_001")

# Create appointment
appointment = await appointment_service.create_appointment(
    property_id="prop_001",
    user_email="user@example.com",
    start_time=datetime(2025, 11, 20, 14, 0),
    duration_minutes=60,
    notes="First viewing"
)
```

### Switching Modes Programmatically

```python
from app.data import DataManager, DataMode

# Switch to mock mode
DataManager.set_mode(DataMode.MOCK)

# Switch to real mode
DataManager.set_mode(DataMode.REAL)

# Check current mode
current_mode = DataManager.get_current_mode()
print(f"Running in {current_mode} mode")
```

### Testing with Mock Data

```python
import pytest
from app.data import DataManager, DataMode

@pytest.fixture(autouse=True)
def use_mock_data():
    """Force mock mode for all tests"""
    DataManager.set_mode(DataMode.MOCK)
    yield
    DataManager.reset_services()

async def test_property_search():
    service = DataManager.get_property_service()

    results = await service.search(location="San Francisco")

    assert len(results) > 0
    assert all(p["city"] == "San Francisco" for p in results)
```

### Production Usage

```python
# In production, set environment variable:
# export DATA_MODE=real
# export RENTCAST_API_KEY=your_actual_key

from app.data import DataManager

# Automatically uses real APIs in production
property_service = DataManager.get_property_service()

# Will call RentCast API
properties = await property_service.search(location="San Francisco")
```

## Data Models

### Property Data Structure

```json
{
  "id": "prop_001",
  "address": "123 Main St",
  "city": "San Francisco",
  "state": "CA",
  "zip_code": "94102",
  "country": "USA",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "price": 3500,
  "bedrooms": 2,
  "bathrooms": 2,
  "square_feet": 1200,
  "property_type": "apartment",
  "description": "Modern 2-bedroom apartment...",
  "amenities": ["parking", "laundry", "gym"],
  "available_date": "2025-12-01",
  "images": ["url1", "url2"],
  "pet_policy": "cats_allowed",
  "lease_duration": 12,
  "utilities_included": ["water", "trash"],
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-10T12:00:00Z"
}
```

### Appointment Data Structure

```json
{
  "id": "appt_001",
  "property_id": "prop_001",
  "user_email": "john.doe@example.com",
  "start_time": "2025-11-15T10:00:00Z",
  "end_time": "2025-11-15T11:00:00Z",
  "duration_minutes": 60,
  "status": "scheduled",
  "notes": "First-time visitor",
  "created_at": "2025-11-10T14:30:00Z",
  "updated_at": "2025-11-10T14:30:00Z"
}
```

## Mock Data Details

### Properties (5 listings)

1. **prop_001**: San Francisco apartment, $3,500/mo, 2BR/2BA
2. **prop_002**: Oakland apartment, $2,800/mo, 1BR/1BA
3. **prop_003**: Berkeley house, $4,200/mo, 3BR/2.5BA
4. **prop_004**: San Jose condo, $3,200/mo, 2BR/2BA
5. **prop_005**: San Francisco luxury apartment, $5,000/mo, 3BR/3BA

### Appointments (3 scheduled)

- Property viewings scheduled for November 2025
- Mix of scheduled and completed appointments
- Demonstrates appointment conflict detection

## Error Handling

### Mock System
- Returns empty arrays for no results
- Returns `None` for missing IDs
- No external failures possible

### Real API System
- Automatic retry (3 attempts with exponential backoff)
- Fallback to mock data if API fails during initialization
- Proper error logging
- Timeout protection (30 seconds)
- HTTP error handling

### Error Messages

```python
# API key missing
ValueError: "RentCast API key not found. Set RENTCAST_API_KEY environment variable."

# Calendar credentials missing
ValueError: "Google Calendar credentials not found. Set GOOGLE_CALENDAR_CREDENTIALS environment variable."

# Runtime API errors
RuntimeError: "Failed to create appointment: [error details]"
```

## Performance Characteristics

### Mock System
- Search: ~100ms (simulated)
- Get by ID: ~50ms (simulated)
- Create appointment: ~100ms (simulated)
- No external network calls
- Ideal for development and testing

### Real API System
- Search: 500-2000ms (depends on API)
- Get by ID: 300-1000ms
- Create appointment: 1000-3000ms
- Network dependent
- Retry logic adds latency on failures

## Testing Strategy

### Unit Tests

Test mock system:
```python
async def test_mock_property_search():
    service = MockPropertyService()
    results = await service.search(location="San Francisco")
    assert len(results) == 2  # Known mock data
```

Test real system (with mocked HTTP):
```python
@pytest.mark.asyncio
async def test_real_property_search(mock_httpx):
    mock_httpx.get.return_value = Mock(json=lambda: {"listings": [...]})
    service = RealPropertyService(api_key="test")
    results = await service.search(location="San Francisco")
    assert len(results) > 0
```

### Integration Tests

```python
@pytest.mark.integration
async def test_data_manager_mock_mode():
    DataManager.set_mode(DataMode.MOCK)
    service = DataManager.get_property_service()
    assert isinstance(service, MockPropertyService)
```

### End-to-End Tests

```python
@pytest.mark.e2e
async def test_property_workflow():
    # Uses whatever mode is configured
    service = DataManager.get_property_service()

    # Search
    properties = await service.search(location="San Francisco")
    assert len(properties) > 0

    # Get details
    prop = await service.get_by_id(properties[0]["id"])
    assert prop is not None
```

## Best Practices

### 1. Always Use DataManager

❌ **Don't**:
```python
from app.data.mock_system import MockPropertyService
service = MockPropertyService()  # Tightly coupled
```

✅ **Do**:
```python
from app.data import DataManager
service = DataManager.get_property_service()  # Loosely coupled
```

### 2. Handle Optional Results

```python
property_detail = await service.get_by_id("unknown_id")
if property_detail:
    print(f"Found: {property_detail['address']}")
else:
    print("Property not found")
```

### 3. Use Type Hints

```python
from typing import List, Dict, Any, Optional

async def search_properties() -> List[Dict[str, Any]]:
    service = DataManager.get_property_service()
    return await service.search(location="San Francisco")
```

### 4. Test with Mock, Deploy with Real

- Development: `DATA_MODE=mock`
- Testing: `DATA_MODE=mock`
- Staging: `DATA_MODE=real` (with test credentials)
- Production: `DATA_MODE=real` (with production credentials)

### 5. Add Custom Mock Data

Edit `/mnt/c/Users/DaviCastroSamora/Documents/SamoraDC/AgenticRealEstateSystem/app/data/fixtures/properties.json`:

```json
{
  "id": "prop_006",
  "address": "Your custom property",
  "city": "Custom City",
  ...
}
```

## Troubleshooting

### Issue: "Using MOCK property service" in production

**Solution**: Set `DATA_MODE=real` environment variable

### Issue: Real API fails to initialize

**Cause**: Missing API keys

**Solution**:
```bash
export RENTCAST_API_KEY=your_key
export GOOGLE_CALENDAR_CREDENTIALS=/path/to/creds.json
```

### Issue: Mock data not found

**Cause**: JSON files missing or corrupted

**Solution**: Verify files exist at `/mnt/c/Users/DaviCastroSamora/Documents/SamoraDC/AgenticRealEstateSystem/app/data/fixtures/`

### Issue: Slow performance in mock mode

**Cause**: Simulated delays

**Solution**: Reduce `await asyncio.sleep()` values in mock_system.py

## Future Enhancements

### Planned Features

1. **Caching Layer**
   - Redis caching for API responses
   - Configurable TTL per data type
   - Cache invalidation strategies

2. **Hybrid Mode**
   - Use mock for some operations, real for others
   - Fallback to mock if real API is down
   - A/B testing capabilities

3. **Data Validation**
   - Pydantic models for all data structures
   - Automatic validation on read/write
   - Schema versioning

4. **Analytics**
   - Track API usage and costs
   - Performance metrics
   - Error rate monitoring

5. **Additional Providers**
   - Zillow API integration
   - Realtor.com integration
   - Multiple calendar providers

## Contributing

When adding new data sources:

1. Create new service class in appropriate file
2. Implement all protocol methods
3. Add configuration to settings.py
4. Update DataManager factory logic
5. Add tests for new implementation
6. Update this documentation

## Related Documentation

- [Configuration Guide](../config/README.md)
- [API Integration](./api_integration.md)
- [Testing Guide](./testing.md)
- [Deployment Guide](./deployment.md)

---

**Last Updated**: 2025-11-11
**Version**: 1.0.0
