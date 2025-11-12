# Data Layer Module

Clean separation between mock data and real API integrations for the Agentic Real Estate System.

## Quick Start

```python
from app.data import DataManager

# Get property service (automatically uses mock or real based on DATA_MODE)
property_service = DataManager.get_property_service()

# Search for properties
properties = await property_service.search(
    location="San Francisco",
    min_price=2000,
    max_price=4000,
    bedrooms=2
)

# Get appointment service
appointment_service = DataManager.get_appointment_service()

# Create appointment
appointment = await appointment_service.create_appointment(
    property_id=properties[0]["id"],
    user_email="user@example.com",
    start_time=datetime.now() + timedelta(days=1),
    duration_minutes=60
)
```

## Environment Configuration

```bash
# Development (default)
DATA_MODE=mock

# Production
DATA_MODE=real
RENTCAST_API_KEY=your_rentcast_key
GOOGLE_CALENDAR_CREDENTIALS=/path/to/credentials.json
```

## Module Structure

```
app/data/
├── __init__.py              # Module exports
├── base_services.py         # Protocol definitions
├── mock_system.py          # Mock implementations
├── real_api_system.py      # Real API implementations
├── data_manager.py         # Factory pattern
├── fixtures/               # Mock data
│   ├── properties.json
│   └── appointments.json
└── README.md              # This file
```

## Features

✅ **Transparent Switching**: Switch between mock and real data with one environment variable
✅ **Protocol-Based**: Type-safe interfaces using Python protocols
✅ **Automatic Fallback**: Falls back to mock if real APIs fail
✅ **Async/Await**: Non-blocking operations throughout
✅ **Retry Logic**: Automatic retry with exponential backoff for real APIs
✅ **Realistic Mock Data**: 5 sample properties and 3 appointments for testing

## Services

### PropertyService

- `search(location, min_price, max_price, bedrooms, property_type)` - Search properties
- `get_by_id(property_id)` - Get single property
- `get_details(property_id)` - Get detailed information
- `get_nearby(latitude, longitude, radius_miles, limit)` - Location-based search

### AppointmentService

- `create_appointment(property_id, user_email, start_time, duration, notes)` - Schedule viewing
- `get_appointments(user_email, start_date, end_date)` - List appointments
- `get_appointment(appointment_id)` - Get single appointment
- `cancel_appointment(appointment_id)` - Cancel viewing
- `get_available_slots(property_id, date, duration)` - Find available times

## Testing

```python
import pytest
from app.data import DataManager, DataMode

@pytest.fixture
def mock_mode():
    DataManager.set_mode(DataMode.MOCK)
    yield
    DataManager.reset_services()

async def test_property_search(mock_mode):
    service = DataManager.get_property_service()
    results = await service.search(location="San Francisco")
    assert len(results) > 0
```

## Documentation

See [docs/data_layer.md](../../docs/data_layer.md) for complete documentation including:
- Architecture diagrams
- Detailed API reference
- Configuration guide
- Best practices
- Troubleshooting
- Performance characteristics

## Examples

### Development with Mock Data

```python
# Automatically uses mock data in development
from app.data import DataManager

service = DataManager.get_property_service()
properties = await service.search(location="Oakland")
print(f"Found {len(properties)} properties")  # Fast, no API calls
```

### Production with Real APIs

```bash
export DATA_MODE=real
export RENTCAST_API_KEY=your_actual_key
```

```python
from app.data import DataManager

service = DataManager.get_property_service()
properties = await service.search(location="Oakland")
print(f"Found {len(properties)} properties")  # Real RentCast API call
```

### Programmatic Mode Switching

```python
from app.data import DataManager, DataMode

# Switch to mock for testing
DataManager.set_mode(DataMode.MOCK)
test_service = DataManager.get_property_service()

# Switch to real for production operation
DataManager.set_mode(DataMode.REAL)
prod_service = DataManager.get_property_service()
```

## Contributing

When adding new features:

1. Define protocol methods in `base_services.py`
2. Implement mock version in `mock_system.py`
3. Implement real version in `real_api_system.py`
4. Update `DataManager` if needed
5. Add tests for both implementations
6. Update documentation

## License

Part of the Agentic Real Estate System - see main project LICENSE.
