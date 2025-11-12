# API Reference - Agentic Real Estate System

**Version:** 1.2.0
**Base URL:** `http://localhost:8000/api`
**Last Updated:** 2025-11-11

---

## Table of Contents

1. [Authentication](#authentication)
2. [Data Models](#data-models)
3. [Property Service](#property-service)
4. [Appointment Service](#appointment-service)
5. [Data Manager](#data-manager)
6. [Orchestrator](#orchestrator)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)

---

## Authentication

### API Key Configuration

Currently uses environment-based API keys. No user authentication required for development.

```python
# In .env file
OPENROUTER_API_KEY=sk-or-v1-your-key-here
RENTCAST_API_KEY=your-rentcast-key
GOOGLE_API_KEY=your-google-key
```

### Future Authentication (Planned)

```python
# JWT-based authentication (coming soon)
headers = {
    "Authorization": "Bearer <your-jwt-token>",
    "Content-Type": "application/json"
}
```

---

## Data Models

### Property Model

```python
from typing import List, Optional
from pydantic import BaseModel, Field

class Property(BaseModel):
    """Property data model."""

    # Identification
    id: str = Field(..., description="Unique property identifier")

    # Location
    address: str = Field(..., description="Street address")
    city: str = Field(..., description="City name")
    state: str = Field(..., description="State code (e.g., CA)")
    zip_code: str = Field(..., description="ZIP/postal code")
    country: str = Field(default="USA", description="Country")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")

    # Property Details
    price: float = Field(..., gt=0, description="Monthly rent in USD")
    bedrooms: int = Field(..., ge=0, description="Number of bedrooms")
    bathrooms: float = Field(..., ge=0, description="Number of bathrooms")
    square_feet: int = Field(..., gt=0, description="Property size in sq ft")
    property_type: str = Field(..., description="Type: apartment, house, condo")

    # Additional Info
    description: str = Field(..., description="Property description")
    amenities: List[str] = Field(default_factory=list, description="List of amenities")
    available_date: str = Field(..., description="ISO 8601 date")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    pet_policy: str = Field(..., description="Pet policy: no_pets, cats_allowed, dogs_allowed")
    lease_duration: int = Field(..., gt=0, description="Lease duration in months")
    utilities_included: List[str] = Field(default_factory=list)

    # Metadata
    created_at: str = Field(..., description="ISO 8601 timestamp")
    updated_at: str = Field(..., description="ISO 8601 timestamp")
```

### Appointment Model

```python
class Appointment(BaseModel):
    """Appointment data model."""

    id: str = Field(..., description="Unique appointment identifier")
    property_id: str = Field(..., description="Associated property ID")
    user_email: str = Field(..., description="User email address")
    start_time: str = Field(..., description="ISO 8601 timestamp")
    end_time: str = Field(..., description="ISO 8601 timestamp")
    duration_minutes: int = Field(..., gt=0, description="Duration in minutes")
    status: str = Field(..., description="Status: scheduled, cancelled, completed")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: str = Field(..., description="ISO 8601 timestamp")
    updated_at: str = Field(..., description="ISO 8601 timestamp")
```

---

## Property Service

### PropertyServiceProtocol

Interface for property operations (both mock and real implementations).

#### Methods

##### search()

Search for properties based on criteria.

```python
async def search(
    self,
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    bedrooms: Optional[int] = None,
    property_type: Optional[str] = None,
    **kwargs
) -> List[Dict[str, Any]]
```

**Parameters:**
- `location` (str, optional): City, state, or ZIP code
- `min_price` (float, optional): Minimum monthly rent
- `max_price` (float, optional): Maximum monthly rent
- `bedrooms` (int, optional): Minimum number of bedrooms
- `property_type` (str, optional): Property type filter
- `**kwargs`: Additional filter parameters

**Returns:**
- `List[Dict[str, Any]]`: List of matching properties

**Example:**
```python
from app.data.data_manager import DataManager

service = DataManager.get_property_service()

results = await service.search(
    location="San Francisco",
    max_price=3000,
    bedrooms=2,
    property_type="apartment"
)

print(f"Found {len(results)} properties")
for prop in results:
    print(f"- {prop['address']}: ${prop['price']}/month")
```

##### get_by_id()

Get property by unique identifier.

```python
async def get_by_id(self, property_id: str) -> Optional[Dict[str, Any]]
```

**Parameters:**
- `property_id` (str): Property identifier

**Returns:**
- `Optional[Dict[str, Any]]`: Property data or None if not found

**Example:**
```python
property = await service.get_by_id("prop_001")

if property:
    print(f"Property: {property['address']}")
    print(f"Price: ${property['price']}/month")
    print(f"Bedrooms: {property['bedrooms']}")
else:
    print("Property not found")
```

##### get_details()

Get detailed property information (alias for get_by_id in mock mode).

```python
async def get_details(self, property_id: str) -> Optional[Dict[str, Any]]
```

##### get_nearby()

Find properties near a geographic location.

```python
async def get_nearby(
    self,
    latitude: float,
    longitude: float,
    radius_miles: float = 5.0,
    limit: int = 10
) -> List[Dict[str, Any]]
```

**Parameters:**
- `latitude` (float): Center latitude
- `longitude` (float): Center longitude
- `radius_miles` (float): Search radius in miles (default: 5.0)
- `limit` (int): Maximum results (default: 10)

**Returns:**
- `List[Dict[str, Any]]`: Properties with `distance_miles` field added

**Example:**
```python
# Find properties near Golden Gate Bridge
nearby = await service.get_nearby(
    latitude=37.8199,
    longitude=-122.4783,
    radius_miles=3.0,
    limit=5
)

for prop in nearby:
    print(f"{prop['address']} - {prop['distance_miles']} miles away")
```

---

## Appointment Service

### AppointmentServiceProtocol

Interface for appointment management operations.

#### Methods

##### create_appointment()

Create a new property viewing appointment.

```python
async def create_appointment(
    self,
    property_id: str,
    user_email: str,
    start_time: datetime,
    duration_minutes: int = 60,
    notes: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters:**
- `property_id` (str): Property to visit
- `user_email` (str): User's email address
- `start_time` (datetime): Appointment start time
- `duration_minutes` (int): Duration (default: 60)
- `notes` (str, optional): Additional notes

**Returns:**
- `Dict[str, Any]`: Created appointment data

**Example:**
```python
from datetime import datetime
from app.data.data_manager import DataManager

service = DataManager.get_appointment_service()

appointment = await service.create_appointment(
    property_id="prop_001",
    user_email="user@example.com",
    start_time=datetime(2025, 12, 1, 14, 0),
    duration_minutes=60,
    notes="First viewing"
)

print(f"Appointment scheduled: {appointment['id']}")
print(f"Time: {appointment['start_time']}")
```

##### get_appointments()

Retrieve appointments with optional filters.

```python
async def get_appointments(
    self,
    user_email: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Dict[str, Any]]
```

**Parameters:**
- `user_email` (str, optional): Filter by user
- `start_date` (datetime, optional): Filter by start date
- `end_date` (datetime, optional): Filter by end date

**Returns:**
- `List[Dict[str, Any]]`: List of appointments

**Example:**
```python
from datetime import datetime, timedelta

# Get user's appointments for next week
next_week = datetime.now() + timedelta(days=7)

appointments = await service.get_appointments(
    user_email="user@example.com",
    start_date=datetime.now(),
    end_date=next_week
)

print(f"You have {len(appointments)} appointments")
```

##### get_appointment()

Get specific appointment by ID.

```python
async def get_appointment(self, appointment_id: str) -> Optional[Dict[str, Any]]
```

##### cancel_appointment()

Cancel an existing appointment.

```python
async def cancel_appointment(self, appointment_id: str) -> bool
```

**Returns:**
- `bool`: True if cancelled successfully, False if not found

**Example:**
```python
success = await service.cancel_appointment("appt_001")

if success:
    print("Appointment cancelled successfully")
else:
    print("Appointment not found")
```

##### get_available_slots()

Get available time slots for a property on a specific date.

```python
async def get_available_slots(
    self,
    property_id: str,
    date: datetime,
    duration_minutes: int = 60
) -> List[datetime]
```

**Parameters:**
- `property_id` (str): Property ID
- `date` (datetime): Target date
- `duration_minutes` (int): Desired duration (default: 60)

**Returns:**
- `List[datetime]`: List of available start times

**Example:**
```python
from datetime import datetime

slots = await service.get_available_slots(
    property_id="prop_001",
    date=datetime(2025, 12, 1),
    duration_minutes=60
)

print(f"Available times on 2025-12-01:")
for slot in slots:
    print(f"- {slot.strftime('%I:%M %p')}")
```

---

## Data Manager

### DataManager Class

Factory for creating data service instances with transparent mock/real switching.

#### Class Methods

##### get_property_service()

Get property service instance (mock or real based on configuration).

```python
@classmethod
def get_property_service(cls) -> PropertyServiceProtocol
```

**Example:**
```python
from app.data.data_manager import DataManager

# Automatically selects mock or real based on DATA_MODE
property_service = DataManager.get_property_service()

# Use service
results = await property_service.search(location="Miami")
```

##### get_appointment_service()

Get appointment service instance.

```python
@classmethod
def get_appointment_service(cls) -> AppointmentServiceProtocol
```

##### get_current_mode()

Get active data mode.

```python
@classmethod
def get_current_mode(cls) -> DataMode
```

**Example:**
```python
mode = DataManager.get_current_mode()
print(f"Current mode: {mode.value}")  # "mock" or "real"
```

##### set_mode()

Programmatically change data mode.

```python
@classmethod
def set_mode(cls, mode: DataMode)
```

**Example:**
```python
from app.data.data_manager import DataManager, DataMode

# Switch to real mode
DataManager.set_mode(DataMode.REAL)

# Get real API service
service = DataManager.get_property_service()
```

##### reset_services()

Reset service instances (useful for testing).

```python
@classmethod
def reset_services(cls)
```

---

## Orchestrator

### UnifiedSwarmOrchestrator

Main orchestrator combining LangGraph-Swarm and PydanticAI.

#### Methods

##### process_message()

Process a message through the agent swarm.

```python
async def process_message(
    self,
    message: Dict[str, Any],
    config: Dict[str, Any] = None
) -> Dict[str, Any]
```

**Parameters:**
- `message`: User message with context
  - `messages`: List of message objects
  - `session_id`: Session identifier
  - `context`: Additional context (data_mode, etc.)
- `config`: LangGraph configuration
  - `configurable.thread_id`: Thread ID for memory persistence

**Returns:**
- `Dict[str, Any]`: Processed result with agent response

**Example:**
```python
from app.orchestration.unified_swarm import get_unified_swarm_orchestrator

orchestrator = get_unified_swarm_orchestrator()

result = await orchestrator.process_message(
    {
        "messages": [
            {"role": "user", "content": "Show me 2-bedroom apartments in Miami"}
        ],
        "session_id": "user_123",
        "context": {"data_mode": "mock"}
    },
    config={
        "configurable": {
            "thread_id": "session_user_123"
        }
    }
)

print(f"Response: {result['messages'][-1]['content']}")
```

##### stream_message()

Stream message processing for real-time responses.

```python
async def stream_message(
    self,
    message: Dict[str, Any],
    config: Dict[str, Any] = None
)
```

**Example:**
```python
async for chunk in orchestrator.stream_message(message, config):
    if "error" in chunk:
        print(f"Error: {chunk['error']}")
    else:
        # Process chunk
        print(chunk)
```

---

## Error Handling

### Error Response Format

All API errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "additional context"
    }
  }
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_API_KEY` | API key missing or invalid | 401 |
| `PROPERTY_NOT_FOUND` | Property ID doesn't exist | 404 |
| `INVALID_REQUEST` | Request validation failed | 400 |
| `SERVICE_UNAVAILABLE` | External service down | 503 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `INTERNAL_ERROR` | Unexpected server error | 500 |

### Exception Classes

```python
class PropertyNotFoundError(Exception):
    """Raised when property doesn't exist."""
    pass

class InvalidRequestError(Exception):
    """Raised when request validation fails."""
    pass

class ServiceUnavailableError(Exception):
    """Raised when external service is down."""
    pass
```

### Error Handling Example

```python
from app.data.data_manager import DataManager
from app.models.response import PropertyNotFoundError

service = DataManager.get_property_service()

try:
    property = await service.get_by_id("invalid_id")
    if property is None:
        raise PropertyNotFoundError("Property not found")
except PropertyNotFoundError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Rate Limiting

### Current Limits (Development)

- **No rate limiting** in development mode
- All endpoints unlimited

### Production Limits (Planned)

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/api/search` | 100 requests | 1 minute |
| `/api/property/{id}` | 200 requests | 1 minute |
| `/api/appointments` | 50 requests | 1 minute |
| `/api/chat` | 30 requests | 1 minute |

### Rate Limit Headers (Planned)

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1638360000
```

### Handling Rate Limits

```python
import time
import httpx

async def make_request_with_retry(url: str, max_retries: int = 3):
    """Make request with rate limit handling."""
    for attempt in range(max_retries):
        response = await httpx.get(url)

        if response.status_code == 429:
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
            wait_time = max(reset_time - time.time(), 1)
            print(f"Rate limited. Waiting {wait_time}s...")
            await asyncio.sleep(wait_time)
            continue

        return response

    raise Exception("Max retries exceeded")
```

---

## SDK Examples

### Python SDK (Conceptual)

```python
from agentic_real_estate import Client

# Initialize client
client = Client(
    base_url="http://localhost:8000/api",
    data_mode="mock"
)

# Search properties
properties = await client.properties.search(
    location="San Francisco",
    max_price=3000,
    bedrooms=2
)

# Get property details
property = await client.properties.get("prop_001")

# Create appointment
appointment = await client.appointments.create(
    property_id="prop_001",
    user_email="user@example.com",
    start_time="2025-12-01T14:00:00Z"
)

# Chat with agent
response = await client.chat.send(
    message="Show me apartments in Oakland",
    session_id="user_123"
)
```

---

## Changelog

### v1.2.0 (2025-11-11)
- Added unified swarm orchestrator
- Improved error handling
- Enhanced documentation

### v1.1.0 (2025-11-10)
- Added appointment service
- Implemented data manager factory
- Added mock data system

### v1.0.0 (2025-11-01)
- Initial API release
- Property search and details
- Basic agent integration

---

**API Documentation Maintained By:** Documentation Agent
**Last Review:** 2025-11-11
**Status:** ✅ Complete
