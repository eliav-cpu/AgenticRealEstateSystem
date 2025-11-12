# Data Layer Quick Start

Get started with the data layer in 5 minutes.

## 1. Installation (Already Done)

The data layer is already installed with these files:

```
app/data/
├── base_services.py       # Protocols
├── mock_system.py        # Mock data
├── real_api_system.py    # Real APIs
├── data_manager.py       # Factory
└── fixtures/             # Mock data
    ├── properties.json
    └── appointments.json
```

## 2. Basic Usage

```python
from app.data import DataManager

# Get services (automatically uses mock or real based on env)
property_service = DataManager.get_property_service()
appointment_service = DataManager.get_appointment_service()

# Search properties
properties = await property_service.search(
    location="San Francisco",
    min_price=2000,
    max_price=4000
)

# Create appointment
from datetime import datetime, timedelta
appointment = await appointment_service.create_appointment(
    property_id=properties[0]["id"],
    user_email="user@example.com",
    start_time=datetime.now() + timedelta(days=1),
    duration_minutes=60
)
```

## 3. Configuration

### Development (Default - No Setup Required)

```bash
# .env file (or just don't set DATA_MODE)
DATA_MODE=mock
```

Uses mock data from JSON files. No external APIs needed.

### Production

```bash
# .env file
DATA_MODE=real
RENTCAST_API_KEY=your_rentcast_key
GOOGLE_CALENDAR_CREDENTIALS=/path/to/credentials.json
```

Uses real RentCast API and Google Calendar.

## 4. Run Examples

### Interactive Demo

```bash
python examples/data_layer_demo.py
```

Shows:
- Property search with various filters
- Appointment creation and management
- Mode switching
- Complete workflow

### Verify Installation

```bash
python scripts/verify_data_layer.py
```

Checks:
- File structure
- Imports
- Configuration
- Basic functionality
- Mock data

### Run Tests

```bash
pytest tests/test_data_layer.py -v
```

## 5. Common Operations

### Property Search

```python
service = DataManager.get_property_service()

# All properties
all_props = await service.search()

# By location
sf_props = await service.search(location="San Francisco")

# By price range
affordable = await service.search(min_price=2000, max_price=3500)

# By bedrooms
large = await service.search(bedrooms=3)

# Combined filters
filtered = await service.search(
    location="Oakland",
    min_price=2500,
    max_price=3500,
    bedrooms=2,
    property_type="apartment"
)

# Nearby search
nearby = await service.get_nearby(
    latitude=37.7749,
    longitude=-122.4194,
    radius_miles=5.0
)
```

### Appointment Management

```python
service = DataManager.get_appointment_service()

# Create appointment
from datetime import datetime, timedelta

tomorrow = datetime.now() + timedelta(days=1)
appointment = await service.create_appointment(
    property_id="prop_001",
    user_email="user@example.com",
    start_time=tomorrow.replace(hour=14, minute=0),
    duration_minutes=60,
    notes="First viewing"
)

# Get user's appointments
appointments = await service.get_appointments(
    user_email="user@example.com"
)

# Get available slots
slots = await service.get_available_slots(
    property_id="prop_001",
    date=tomorrow,
    duration_minutes=60
)

# Cancel appointment
success = await service.cancel_appointment(appointment["id"])
```

## 6. Mode Switching

### Environment Variable (Recommended)

```bash
# Development
export DATA_MODE=mock

# Production
export DATA_MODE=real
```

### Programmatic

```python
from app.data import DataManager, DataMode

# Switch to mock
DataManager.set_mode(DataMode.MOCK)

# Switch to real
DataManager.set_mode(DataMode.REAL)

# Check current mode
mode = DataManager.get_current_mode()
print(f"Running in {mode} mode")
```

## 7. Mock Data

### Available Properties (5 listings)

1. **prop_001**: SF apartment, $3,500/mo, 2BR/2BA
2. **prop_002**: Oakland apartment, $2,800/mo, 1BR/1BA
3. **prop_003**: Berkeley house, $4,200/mo, 3BR/2.5BA
4. **prop_004**: San Jose condo, $3,200/mo, 2BR/2BA
5. **prop_005**: SF luxury, $5,000/mo, 3BR/3BA

### Customize Mock Data

Edit `/mnt/c/Users/DaviCastroSamora/Documents/SamoraDC/AgenticRealEstateSystem/app/data/fixtures/properties.json`:

```json
{
  "id": "prop_006",
  "address": "Your address",
  "city": "Your city",
  "price": 3000,
  "bedrooms": 2,
  ...
}
```

## 8. Error Handling

```python
from app.data import DataManager

try:
    service = DataManager.get_property_service()
    properties = await service.search(location="San Francisco")

    if not properties:
        print("No properties found")
    else:
        for prop in properties:
            print(f"{prop['address']}: ${prop['price']}/mo")

except Exception as e:
    print(f"Error: {e}")
```

## 9. Testing

```python
import pytest
from app.data import DataManager, DataMode

@pytest.fixture
def mock_mode():
    """Force mock mode for tests"""
    DataManager.set_mode(DataMode.MOCK)
    yield
    DataManager.reset_services()

async def test_search(mock_mode):
    service = DataManager.get_property_service()
    results = await service.search(location="San Francisco")
    assert len(results) == 2  # Known mock data
```

## 10. Troubleshooting

### "Using MOCK property service" in production

**Problem**: Real APIs not being used

**Solution**: Set `DATA_MODE=real` in environment

### "RentCast API key not found"

**Problem**: Missing API key

**Solution**:
```bash
export RENTCAST_API_KEY=your_key
```

### "No module named 'app.data'"

**Problem**: Wrong directory or PYTHONPATH

**Solution**: Run from project root:
```bash
cd /path/to/AgenticRealEstateSystem
python -c "from app.data import DataManager; print('OK')"
```

### Mock data not found

**Problem**: JSON files missing

**Solution**: Verify files exist:
```bash
ls app/data/fixtures/
# Should show: properties.json  appointments.json
```

## Next Steps

1. **Read Full Documentation**: `/mnt/c/Users/DaviCastroSamora/Documents/SamoraDC/AgenticRealEstateSystem/docs/data_layer.md`
2. **Run Demo**: `python examples/data_layer_demo.py`
3. **Run Tests**: `pytest tests/test_data_layer.py -v`
4. **Update Your Code**: Replace hardcoded data with DataManager

## Key Concepts

- **Protocol-based**: Type-safe interfaces
- **Factory Pattern**: DataManager provides correct implementation
- **Singleton**: Same instance reused for consistency
- **Async/Await**: Non-blocking operations
- **Automatic Fallback**: Falls back to mock if real APIs fail

## Documentation

- **Quick Start**: This file
- **Full Guide**: `/mnt/c/Users/DaviCastroSamora/Documents/SamoraDC/AgenticRealEstateSystem/docs/data_layer.md`
- **Module README**: `/mnt/c/Users/DaviCastroSamora/Documents/SamoraDC/AgenticRealEstateSystem/app/data/README.md`
- **Summary**: `/mnt/c/Users/DaviCastroSamora/Documents/SamoraDC/AgenticRealEstateSystem/docs/data_layer_summary.md`

---

**Ready to use! The data layer is fully configured for development.**

Default mode: MOCK (no external APIs needed)
