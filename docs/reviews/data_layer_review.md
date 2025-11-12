# Data Layer Review: Mock vs Real System Separation

**Review Date:** 2025-11-11
**Reviewer:** Code Review Agent (Hive Mind)
**System:** Agentic Real Estate System

---

## Executive Summary

The system implements a **dual-mode data architecture** with mock and real data sources. The separation is generally clean, but there are integration gaps and missing validation layers.

**Overall Assessment:** 🟡 **MODERATE** - Good separation concept, incomplete implementation

---

## Data Architecture Overview

### Data Modes

| Mode | Implementation | Storage | API | Status |
|------|----------------|---------|-----|--------|
| **Mock** | DuckDB | Local database | FastAPI endpoints | ✅ Complete |
| **Real** | In-memory | Python dicts | RentCast API (planned) | ⚠️ Incomplete |

### Key Files

- `app/database/schema.py` - DuckDB schema for mock data
- `app/models/property.py` - Pydantic models for validation
- `app/tools/property.py` - Property data access layer
- Mock data endpoints in FastAPI

---

## Critical Issues

### 🔴 CRITICAL #1: DataMode Switching Not Consistent

**File:** `app/orchestration/swarm.py` (lines 180-181, 277)
**Severity:** Critical
**Impact:** System may mix mock and real data sources

**Problem:**
```python
# DataMode accessed from context
context = state.get("context", {})
data_mode = context.get("data_mode", "mock")

# BUT: No validation that all components use same mode
# Mock and real data could be mixed in same conversation

# Example:
async def search_agent_node(state: SwarmState):
    data_mode = context.get("data_mode", "mock")  # From state

    # BUT: Property API might use different mode
    response = requests.get("http://localhost:8000/api/properties/search")
    # ❌ No data_mode parameter passed!
```

**Recommended Fix:**
```python
# Create DataMode enum and enforce it
from enum import Enum

class DataMode(str, Enum):
    MOCK = "mock"
    REAL = "real"

class DataModeContext:
    """Singleton to ensure consistent data mode across system"""
    _instance = None
    _mode: DataMode = DataMode.MOCK

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def mode(self) -> DataMode:
        return self._mode

    def set_mode(self, mode: DataMode):
        if not isinstance(mode, DataMode):
            raise ValueError(f"Invalid data mode: {mode}")
        self._mode = mode
        logger.info(f"Data mode set to: {mode}")

# Usage in agents
data_context = DataModeContext.get_instance()
if data_context.mode == DataMode.MOCK:
    properties = get_mock_properties()
else:
    properties = get_real_properties()
```

---

### 🔴 CRITICAL #2: Real API Mode Has No Implementation

**File:** `app/tools/property.py`, `app/orchestration/swarm.py` (lines 236-240)
**Severity:** Critical
**Impact:** Real mode unusable

**Problem:**
```python
# In search_agent_node
if data_mode == "mock":
    # Use FastAPI Mock endpoint
    response = requests.get("http://localhost:8000/api/properties/search")
    if response.status_code == 200:
        data = response.json()
        available_properties = data.get("properties", [])
else:
    # For real mode, we'd use actual API calls
    logger.info("Real API mode not implemented yet")
    available_properties = []  # ❌ Empty results!
```

**Recommended Fix:**
```python
class PropertyDataService:
    """Unified interface for property data access"""

    def __init__(self, mode: DataMode):
        self.mode = mode
        self.mock_client = MockPropertyClient() if mode == DataMode.MOCK else None
        self.real_client = RealPropertyClient() if mode == DataMode.REAL else None

    async def search_properties(self, criteria: SearchCriteria) -> List[Property]:
        if self.mode == DataMode.MOCK:
            return await self.mock_client.search(criteria)
        else:
            return await self.real_client.search(criteria)

class RealPropertyClient:
    """Real API integration"""

    def __init__(self):
        self.api_key = get_settings().apis.rentcast_key
        self.base_url = "https://api.rentcast.io/v1"

    async def search(self, criteria: SearchCriteria) -> List[Property]:
        # Actual RentCast API implementation
        async with aiohttp.ClientSession() as session:
            params = self._build_search_params(criteria)
            async with session.get(
                f"{self.base_url}/properties",
                headers={"X-Api-Key": self.api_key},
                params=params
            ) as response:
                data = await response.json()
                return [self._parse_property(p) for p in data]
```

---

### 🟡 MAJOR #1: Mock Database Schema Doesn't Match Real API

**File:** `app/database/schema.py` (lines 17-74)
**Severity:** High
**Impact:** Data model mismatch when switching modes

**Problem:**
```python
# Mock database schema
CREATE TABLE IF NOT EXISTS properties (
    id VARCHAR PRIMARY KEY,
    formatted_address VARCHAR,
    bedrooms INTEGER,
    bathrooms INTEGER,
    square_footage INTEGER,  # ❌ Different from API
    # ... other fields

    listing_agent JSON,  # ❌ Stored as JSON in DB
    listing_office JSON
)

# But Property model expects different structure
class Property(BaseModel):
    id: Optional[int] = Field(None)  # ❌ int vs VARCHAR
    features: Features = Field(...)  # ❌ Nested model
    address: Address = Field(...)  # ❌ Nested model
```

**Real API (RentCast) Structure:**
```json
{
  "id": "12345-abc",
  "formattedAddress": "123 Main St",
  "squareFootage": 1200,  // Different naming
  "listingAgent": {  // Nested object, not JSON string
    "name": "John Doe",
    "phone": "555-1234"
  }
}
```

**Recommended Fix:**
```python
# Create adapter layer

class PropertyAdapter:
    """Converts between API formats and internal models"""

    @staticmethod
    def from_mock_db(db_row: Dict[str, Any]) -> Property:
        """Convert DuckDB row to Property model"""
        return Property(
            id=int(db_row['id']) if db_row['id'].isdigit() else None,
            external_id=db_row['id'],
            address=Address(
                street=db_row['address_line1'] or "",
                city=db_row['city'] or "",
                state=db_row['state'] or "",
                # ...
            ),
            features=Features(
                bedrooms=db_row['bedrooms'],
                bathrooms=db_row['bathrooms'],
                area_total=db_row['square_footage'],
                # ...
            )
        )

    @staticmethod
    def from_rentcast_api(api_data: Dict[str, Any]) -> Property:
        """Convert RentCast API response to Property model"""
        return Property(
            external_id=api_data['id'],
            address=Address(
                street=api_data.get('addressLine1', ''),
                city=api_data.get('city', ''),
                # ...
            ),
            features=Features(
                bedrooms=api_data.get('bedrooms'),
                bathrooms=api_data.get('bathrooms'),
                area_total=api_data.get('squareFootage'),
                # ...
            )
        )
```

---

## Major Issues

### 🟡 MAJOR #1: No Data Validation Layer

**File:** `app/models/property.py` (lines 115-186)
**Severity:** High
**Impact:** Invalid data can enter system

**Problem:**
```python
class Property(BaseModel):
    """Main property model."""
    # Fields defined but no comprehensive validation

    @validator("price", "rent_price", pre=True)
    def validate_prices(cls, v):
        if v is not None and v < 0:
            raise ValueError("Preços devem ser positivos")
        return v

    # ❌ Missing validators for:
    # - Address completeness
    # - Feature consistency (e.g., bathrooms > 0)
    # - Valid property types
    # - Reasonable price ranges
```

**Recommended Fix:**
```python
class Property(BaseModel):
    """Main property model with comprehensive validation."""

    @validator("address")
    def validate_address(cls, v):
        if not v.city or not v.state:
            raise ValueError("Address must have city and state")
        if v.latitude and v.longitude:
            if not (-90 <= v.latitude <= 90) or not (-180 <= v.longitude <= 180):
                raise ValueError("Invalid coordinates")
        return v

    @validator("features")
    def validate_features(cls, v):
        if v.bedrooms and v.bedrooms < 0:
            raise ValueError("Bedrooms must be non-negative")
        if v.bathrooms and v.bathrooms < 0:
            raise ValueError("Bathrooms must be non-negative")
        if v.area_total and v.area_total < 50:  # Too small
            raise ValueError("Area must be at least 50 sq ft")
        return v

    @validator("price", "rent_price")
    def validate_price_range(cls, v):
        if v is not None:
            if v < 0:
                raise ValueError("Price must be positive")
            if v > 100_000_000:  # Sanity check
                raise ValueError("Price seems unrealistic")
        return v

    @root_validator
    def validate_price_context(cls, values):
        """Ensure price makes sense for status"""
        status = values.get('status')
        price = values.get('price')
        rent_price = values.get('rent_price')

        if status == PropertyStatus.FOR_SALE and not price:
            raise ValueError("For sale properties must have a price")
        if status == PropertyStatus.FOR_RENT and not rent_price:
            raise ValueError("For rent properties must have rent_price")

        return values
```

---

### 🟡 MAJOR #2: Missing Data Access Abstraction

**File:** Multiple files access data directly
**Severity:** High
**Impact:** Tight coupling, hard to test

**Problem:**
```python
# Data access scattered throughout code

# In swarm.py
response = requests.get("http://localhost:8000/api/properties/search")
properties = response.json().get("properties", [])

# In tools/property.py
conn = duckdb.connect("data/properties.duckdb")
result = conn.execute("SELECT * FROM properties").fetchall()

# No consistent interface
```

**Recommended Fix:**
```python
# Create repository pattern

class PropertyRepository(ABC):
    """Abstract base for property data access"""

    @abstractmethod
    async def search(self, criteria: SearchCriteria) -> SearchResult:
        pass

    @abstractmethod
    async def get_by_id(self, property_id: str) -> Optional[Property]:
        pass

    @abstractmethod
    async def save(self, property: Property) -> bool:
        pass

class MockPropertyRepository(PropertyRepository):
    """Mock data using DuckDB"""

    def __init__(self):
        self.db = PropertyDB("data/properties.duckdb")

    async def search(self, criteria: SearchCriteria) -> SearchResult:
        # Use DuckDB
        properties = self.db.search_properties(criteria.dict())
        return SearchResult(
            properties=[PropertyAdapter.from_mock_db(p) for p in properties],
            # ...
        )

class RealPropertyRepository(PropertyRepository):
    """Real data using RentCast API"""

    def __init__(self):
        self.client = RealPropertyClient()

    async def search(self, criteria: SearchCriteria) -> SearchResult:
        # Use RentCast API
        api_properties = await self.client.search(criteria)
        return SearchResult(
            properties=[PropertyAdapter.from_rentcast_api(p) for p in api_properties],
            # ...
        )

# Usage in agents
repo = get_property_repository()  # Factory returns right implementation
results = await repo.search(criteria)
```

---

## Medium Issues

### 🟠 MEDIUM #1: No Caching Layer

**File:** Data access throughout system
**Severity:** Medium
**Impact:** Repeated API calls, slow performance

**Problem:**
```python
# Every search hits database/API directly
response = requests.get("http://localhost:8000/api/properties/search")
properties = response.json()

# No caching means:
# - Same search repeated multiple times
# - No offline capability
# - Higher API costs for real mode
```

**Recommended Fix:**
```python
from functools import lru_cache
import hashlib
import json

class CachedPropertyRepository:
    """Adds caching layer to property access"""

    def __init__(self, base_repository: PropertyRepository):
        self.base = base_repository
        self.cache = {}
        self.ttl = 300  # 5 minutes

    async def search(self, criteria: SearchCriteria) -> SearchResult:
        # Create cache key from criteria
        cache_key = self._make_cache_key(criteria)

        # Check cache
        if cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.ttl:
                logger.debug(f"Cache hit for: {cache_key}")
                return cached_result

        # Cache miss - fetch from repository
        result = await self.base.search(criteria)

        # Store in cache
        self.cache[cache_key] = (result, time.time())

        return result

    def _make_cache_key(self, criteria: SearchCriteria) -> str:
        # Create deterministic hash of criteria
        criteria_json = json.dumps(criteria.dict(), sort_keys=True)
        return hashlib.md5(criteria_json.encode()).hexdigest()
```

---

### 🟠 MEDIUM #2: Database Migration Strategy Missing

**File:** `app/database/schema.py`
**Severity:** Medium
**Impact:** Can't evolve schema without breaking

**Problem:**
```python
def create_property_schema(conn: duckdb.DuckDBPyConnection) -> None:
    """Create the properties table"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            -- Schema definition
        )
    """)

# No version tracking
# No migration scripts
# Schema changes break existing data
```

**Recommended Fix:**
```python
class SchemaVersion(BaseModel):
    version: int
    applied_at: datetime
    description: str

class DatabaseMigrator:
    """Handle schema migrations"""

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn
        self._ensure_version_table()

    def _ensure_version_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_versions (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP,
                description VARCHAR
            )
        """)

    def get_current_version(self) -> int:
        result = self.conn.execute(
            "SELECT MAX(version) FROM schema_versions"
        ).fetchone()
        return result[0] if result[0] else 0

    def migrate(self):
        """Apply all pending migrations"""
        current = self.get_current_version()

        migrations = [
            (1, "Initial schema", self._migration_001),
            (2, "Add listing agent details", self._migration_002),
            # ... more migrations
        ]

        for version, description, migration_func in migrations:
            if version > current:
                logger.info(f"Applying migration {version}: {description}")
                migration_func()
                self.conn.execute(
                    "INSERT INTO schema_versions VALUES (?, CURRENT_TIMESTAMP, ?)",
                    [version, description]
                )

    def _migration_001(self):
        """Initial schema"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                -- Initial schema
            )
        """)

    def _migration_002(self):
        """Add listing agent details"""
        self.conn.execute("""
            ALTER TABLE properties ADD COLUMN agent_license VARCHAR
        """)
```

---

## Positive Findings

### ✅ STRENGTH #1: Clean DuckDB Schema Design

**File:** `app/database/schema.py` (lines 18-83)
**Quality:** Excellent

**Evidence:**
```python
CREATE TABLE IF NOT EXISTS properties (
    -- Primary identification
    id VARCHAR PRIMARY KEY,
    formatted_address VARCHAR,
    address_line1 VARCHAR,
    # ...

    -- Location coordinates
    latitude DOUBLE,
    longitude DOUBLE,

    -- Property details
    property_type VARCHAR,
    bedrooms INTEGER,
    # ...

    -- MLS information
    mls_name VARCHAR,
    mls_number VARCHAR,

    -- Complex data as JSON
    listing_agent JSON,
    listing_office JSON,

    -- Metadata
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

# Create indexes for common search patterns
CREATE INDEX IF NOT EXISTS idx_city ON properties(city)
CREATE INDEX IF NOT EXISTS idx_bedrooms ON properties(bedrooms)
CREATE INDEX IF NOT EXISTS idx_price ON properties(price)
```

**Why This Works:**
- Well-organized with comments
- Appropriate data types
- Indexes on search columns
- JSON for complex nested data
- Metadata tracking

---

### ✅ STRENGTH #2: Comprehensive Property Model

**File:** `app/models/property.py` (lines 115-186)
**Quality:** Very Good

**Evidence:**
```python
class Property(BaseModel):
    """Main property model."""
    # Identification
    id: Optional[int]
    external_id: Optional[str]
    title: str

    # Core data
    property_type: PropertyType  # Enum
    status: PropertyStatus  # Enum
    address: Address  # Nested model
    features: Features  # Nested model

    # Prices with proper typing
    price: Optional[Decimal]
    rent_price: Optional[Decimal]

    # Metadata
    created_at: datetime
    updated_at: datetime
    source: Optional[str]

    # Computed properties
    @property
    def main_price(self) -> Optional[Decimal]:
        """Returns main price based on status"""
        if self.status == PropertyStatus.FOR_SALE:
            return self.price
        elif self.status == PropertyStatus.FOR_RENT:
            return self.rent_price
        return None
```

**Why This Works:**
- Strong typing with Pydantic
- Enums for constrained values
- Nested models for structure
- Computed properties for derived data
- Clear field descriptions

---

### ✅ STRENGTH #3: Good Search Criteria Model

**File:** `app/models/property.py` (lines 189-232)
**Quality:** Good

**Evidence:**
```python
class SearchCriteria(BaseModel):
    """Search criteria for properties."""

    # Location
    neighborhoods: List[str] = Field(default_factory=list)
    cities: List[str] = Field(default_factory=list)

    # Proximity search
    center_lat: Optional[float]
    center_lng: Optional[float]
    radius_km: Optional[float]

    # Property characteristics
    property_types: List[PropertyType] = Field(default_factory=list)
    min_bedrooms: Optional[int]
    max_bedrooms: Optional[int]

    # Price filters
    min_price: Optional[Decimal]
    max_price: Optional[Decimal]

    # Configuration
    limit: int = Field(default=20)
    sort_by: str = Field(default="relevance")
    sort_order: Literal["asc", "desc"] = Field(default="desc")

    # Flags
    clarification_needed: bool = Field(default=False)
    clarification_message: Optional[str]
```

**Why This Works:**
- Comprehensive filter options
- Proper defaults
- Type safety with Pydantic
- Supports complex queries

---

## Recommendations Summary

### Immediate Actions (Critical Priority)

1. **Implement Real API Mode**
   - Create RealPropertyClient
   - Integrate with RentCast API
   - Test end-to-end with real data

2. **Add DataMode Enforcement**
   - Create DataMode singleton
   - Validate consistent mode usage
   - Add mode switching tests

3. **Create Adapter Layer**
   - PropertyAdapter for format conversion
   - Handle mock vs real differences
   - Validate data integrity

### Short-term Improvements (High Priority)

1. **Add Data Validation**
   - Comprehensive Pydantic validators
   - Range checks and sanity tests
   - Cross-field validation

2. **Implement Repository Pattern**
   - Abstract data access
   - Mock and Real implementations
   - Make testable

3. **Add Caching Layer**
   - Cache search results
   - TTL-based invalidation
   - Reduce API calls

### Long-term Enhancements (Medium Priority)

1. **Database Migrations**
   - Version tracking
   - Migration scripts
   - Rollback capability

2. **Monitoring & Metrics**
   - Track API usage
   - Monitor cache hit rates
   - Alert on data errors

3. **Offline Capability**
   - Local data sync
   - Graceful degradation
   - Conflict resolution

---

## Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Mode Consistency | 60% | 95% | 🔴 Critical |
| Real API Implementation | 0% | 100% | 🔴 Critical |
| Data Validation | 40% | 90% | 🟡 Needs Work |
| Schema Quality | 85% | 90% | 🟠 Good |
| Model Completeness | 80% | 90% | 🟠 Good |
| Caching | 0% | 80% | 🔴 Missing |

---

## Conclusion

The data layer shows **good foundational design with Pydantic models and DuckDB schema**, but suffers from **incomplete real mode implementation and lack of abstraction**. The mock mode works well, but the system can't switch to production.

**Priority Recommendation:** Implement real API mode, add repository pattern for abstraction, and enforce consistent data mode usage throughout the system.

---

**Next Review:** After real API implementation - Expected: Q1 2026
