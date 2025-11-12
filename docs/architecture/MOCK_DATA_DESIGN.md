# Mock Data Architecture Design

## Overview

This document details the mock data architecture for 10,000 house entries and associated reviews, designed for realistic development and testing with seamless migration to production APIs.

## Data Schema Design

### 1. Properties Table (DuckDB)

```sql
CREATE TABLE properties (
    -- Primary Key
    id INTEGER PRIMARY KEY,
    external_id VARCHAR,

    -- Basic Information
    title VARCHAR NOT NULL,
    description TEXT,
    property_type VARCHAR CHECK (property_type IN ('house', 'apartment', 'condo', 'townhouse', 'studio', 'loft', 'commercial', 'land')),
    status VARCHAR CHECK (status IN ('for_sale', 'for_rent', 'sold', 'rented', 'off_market')),

    -- Address
    street VARCHAR NOT NULL,
    number VARCHAR,
    complement VARCHAR,
    neighborhood VARCHAR NOT NULL,
    city VARCHAR NOT NULL,
    state VARCHAR NOT NULL,
    country VARCHAR DEFAULT 'USA',
    postal_code VARCHAR,
    latitude DOUBLE,
    longitude DOUBLE,

    -- Features
    bedrooms INTEGER,
    bathrooms INTEGER,
    garage_spaces INTEGER,
    area_total DOUBLE,
    area_built DOUBLE,
    floor INTEGER,
    total_floors INTEGER,

    -- Amenities (Boolean flags)
    has_pool BOOLEAN DEFAULT FALSE,
    has_gym BOOLEAN DEFAULT FALSE,
    has_garden BOOLEAN DEFAULT FALSE,
    has_balcony BOOLEAN DEFAULT FALSE,
    has_elevator BOOLEAN DEFAULT FALSE,
    has_security BOOLEAN DEFAULT FALSE,
    allows_pets BOOLEAN DEFAULT FALSE,
    is_furnished BOOLEAN DEFAULT FALSE,

    -- Pricing
    price DECIMAL(12, 2),
    rent_price DECIMAL(12, 2),
    price_per_sqft DECIMAL(10, 2),
    condo_fee DECIMAL(10, 2),
    property_tax DECIMAL(10, 2),

    -- Agent Information
    agent_name VARCHAR,
    agent_phone VARCHAR,
    agent_email VARCHAR,
    agency_name VARCHAR,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR DEFAULT 'mock',
    relevance_score DOUBLE,

    -- JSON fields for flexibility
    images JSON,  -- Array of image URLs
    amenities JSON,  -- Array of additional amenities
    metadata JSON  -- Additional flexible data
);

-- Indexes for performance
CREATE INDEX idx_properties_city ON properties(city);
CREATE INDEX idx_properties_neighborhood ON properties(neighborhood);
CREATE INDEX idx_properties_type ON properties(property_type);
CREATE INDEX idx_properties_status ON properties(status);
CREATE INDEX idx_properties_price ON properties(price);
CREATE INDEX idx_properties_bedrooms ON properties(bedrooms);
CREATE INDEX idx_properties_location ON properties(latitude, longitude);
```

### 2. Reviews Table (DuckDB)

```sql
CREATE TABLE reviews (
    -- Primary Key
    id INTEGER PRIMARY KEY,

    -- Foreign Keys
    property_id INTEGER NOT NULL,
    user_id INTEGER,

    -- Review Content
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    title VARCHAR,
    content TEXT NOT NULL,

    -- Review Categories
    location_rating INTEGER CHECK (location_rating BETWEEN 1 AND 5),
    value_rating INTEGER CHECK (value_rating BETWEEN 1 AND 5),
    condition_rating INTEGER CHECK (condition_rating BETWEEN 1 AND 5),
    amenities_rating INTEGER CHECK (amenities_rating BETWEEN 1 AND 5),

    -- Sentiment Analysis (pre-computed for performance)
    sentiment VARCHAR CHECK (sentiment IN ('positive', 'neutral', 'negative')),
    sentiment_score DOUBLE,  -- -1 to 1

    -- Review Metadata
    verified_stay BOOLEAN DEFAULT FALSE,
    stay_duration_months INTEGER,
    reviewer_type VARCHAR CHECK (reviewer_type IN ('tenant', 'owner', 'visitor', 'neighbor')),

    -- Helpfulness
    helpful_count INTEGER DEFAULT 0,
    unhelpful_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Moderation
    is_verified BOOLEAN DEFAULT FALSE,
    is_flagged BOOLEAN DEFAULT FALSE,
    moderation_status VARCHAR DEFAULT 'pending',

    -- Additional data
    tags JSON,  -- Array of tags like ["quiet", "safe", "noisy"]
    metadata JSON,

    FOREIGN KEY (property_id) REFERENCES properties(id)
);

-- Indexes
CREATE INDEX idx_reviews_property ON reviews(property_id);
CREATE INDEX idx_reviews_rating ON reviews(rating);
CREATE INDEX idx_reviews_sentiment ON reviews(sentiment);
CREATE INDEX idx_reviews_created ON reviews(created_at);
```

### 3. Amenities Table (DuckDB)

```sql
CREATE TABLE amenities (
    id INTEGER PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    category VARCHAR,
    icon VARCHAR,
    description TEXT
);

-- Bridge table for property-amenity many-to-many
CREATE TABLE property_amenities (
    property_id INTEGER,
    amenity_id INTEGER,
    PRIMARY KEY (property_id, amenity_id),
    FOREIGN KEY (property_id) REFERENCES properties(id),
    FOREIGN KEY (amenity_id) REFERENCES amenities(id)
);
```

### 4. Analytics Table (DuckDB)

```sql
CREATE TABLE property_analytics (
    property_id INTEGER PRIMARY KEY,
    view_count INTEGER DEFAULT 0,
    favorite_count INTEGER DEFAULT 0,
    inquiry_count INTEGER DEFAULT 0,
    average_rating DOUBLE,
    review_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id)
);
```

## Data Generation Strategy

### Property Generation Algorithm

```python
# Mock data generation configuration
GENERATION_CONFIG = {
    "total_properties": 10000,
    "cities": [
        {"name": "Miami", "weight": 0.25, "neighborhoods": 15},
        {"name": "New York", "weight": 0.20, "neighborhoods": 20},
        {"name": "Los Angeles", "weight": 0.18, "neighborhoods": 18},
        {"name": "Chicago", "weight": 0.12, "neighborhoods": 12},
        {"name": "Boston", "weight": 0.10, "neighborhoods": 10},
        {"name": "Austin", "weight": 0.08, "neighborhoods": 8},
        {"name": "Seattle", "weight": 0.07, "neighborhoods": 7},
    ],
    "property_types": {
        "apartment": 0.35,
        "house": 0.25,
        "condo": 0.20,
        "townhouse": 0.12,
        "studio": 0.05,
        "loft": 0.03,
    },
    "price_ranges": {
        "apartment": (800, 4500),
        "house": (1500, 8000),
        "condo": (1200, 5500),
        "townhouse": (1400, 6000),
        "studio": (600, 2500),
        "loft": (1800, 5000),
    },
}
```

### Review Generation Algorithm

```python
REVIEW_CONFIG = {
    "reviews_per_property": {
        "min": 0,
        "max": 50,
        "distribution": "poisson",  # Most properties have 3-8 reviews
        "lambda": 5,
    },
    "sentiment_distribution": {
        "positive": 0.65,  # 65% positive reviews
        "neutral": 0.25,   # 25% neutral reviews
        "negative": 0.10,  # 10% negative reviews
    },
    "rating_distribution": {
        5: 0.45,
        4: 0.30,
        3: 0.15,
        2: 0.07,
        1: 0.03,
    },
    "reviewer_types": {
        "tenant": 0.70,
        "owner": 0.15,
        "visitor": 0.10,
        "neighbor": 0.05,
    },
}
```

## Data Distribution

### Geographic Distribution

```
Miami (2,500 properties)
├── Downtown: 400
├── Brickell: 500
├── Coral Gables: 350
├── Coconut Grove: 300
├── Wynwood: 250
├── ... (15 neighborhoods total)

New York (2,000 properties)
├── Manhattan: 600
├── Brooklyn: 500
├── Queens: 400
├── Bronx: 300
├── ... (20 neighborhoods total)

[Similar breakdown for other cities]
```

### Property Type Distribution

```
Apartment: 3,500 properties (35%)
House: 2,500 properties (25%)
Condo: 2,000 properties (20%)
Townhouse: 1,200 properties (12%)
Studio: 500 properties (5%)
Loft: 300 properties (3%)
```

### Price Distribution

```
<$1,000: 1,000 properties (10%)
$1,000-$2,000: 3,000 properties (30%)
$2,000-$3,500: 3,500 properties (35%)
$3,500-$5,000: 1,800 properties (18%)
$5,000+: 700 properties (7%)
```

## Realistic Data Features

### 1. Location-Based Pricing
Properties in premium neighborhoods have higher prices:
```python
NEIGHBORHOOD_MULTIPLIERS = {
    "Miami/Brickell": 1.5,
    "Miami/Coral Gables": 1.4,
    "NYC/Manhattan": 2.0,
    "NYC/Brooklyn/Williamsburg": 1.6,
    # ... etc
}
```

### 2. Seasonal Variations
Properties have different availability patterns:
```python
def apply_seasonal_factors(property, timestamp):
    if property.city == "Miami" and is_winter(timestamp):
        property.price *= 1.2  # Winter season premium
    elif property.city == "NYC" and is_summer(timestamp):
        property.price *= 1.15  # Summer premium
```

### 3. Realistic Review Content

Reviews are generated with templates that include:
- **Positive aspects**: Location, amenities, value
- **Negative aspects**: Noise, maintenance, parking
- **Specific details**: Floor level, view, neighbors
- **Temporal context**: Season, duration of stay

Example template:
```python
REVIEW_TEMPLATES = {
    "positive": [
        "Amazing {property_type} in {neighborhood}! The {amenity} was fantastic. {detail}",
        "Great value for money. {positive_aspect}. Would recommend!",
    ],
    "negative": [
        "Disappointed with {aspect}. {issue}. Expected better for the price.",
        "Location is good but {problem}. {additional_complaint}.",
    ],
}
```

### 4. Correlation Between Features

Realistic correlations:
- More bedrooms → Higher price
- Downtown location → Higher price, more amenities
- Newer buildings → Higher price, more modern amenities
- Pet-friendly → Slightly higher price
- Pool/gym → 10-20% price premium

## Data Generation Implementation

### File Structure
```
app/data/generators/
├── __init__.py
├── base_generator.py          # Abstract base class
├── property_generator.py      # Property generation logic
├── review_generator.py        # Review generation logic
├── amenity_generator.py       # Amenity seeding
├── templates/                 # Data templates
│   ├── property_templates.py
│   ├── review_templates.py
│   └── addresses.py          # Real street names/neighborhoods
└── distributions.py          # Statistical distributions
```

### Property Generator

```python
# app/data/generators/property_generator.py
from typing import List, Dict
import random
from faker import Faker
from app.models.property import Property, PropertyType, PropertyStatus

class PropertyGenerator:
    def __init__(self, config: Dict):
        self.config = config
        self.faker = Faker('en_US')

    def generate_batch(self, count: int) -> List[Property]:
        """Generate a batch of properties."""
        properties = []
        for i in range(count):
            city = self._select_city()
            neighborhood = self._select_neighborhood(city)
            property_type = self._select_property_type()

            property = Property(
                id=i + 1,
                external_id=f"MOCK-{i+1:06d}",
                title=self._generate_title(property_type, neighborhood),
                description=self._generate_description(property_type),
                property_type=property_type,
                status=self._select_status(),
                address=self._generate_address(city, neighborhood),
                features=self._generate_features(property_type),
                price=self._calculate_price(property_type, neighborhood, city),
                # ... more fields
            )
            properties.append(property)

        return properties

    def _select_city(self) -> str:
        """Select city based on weighted distribution."""
        cities = self.config["cities"]
        weights = [c["weight"] for c in cities]
        return random.choices(cities, weights=weights)[0]["name"]

    def _calculate_price(self, property_type: str, neighborhood: str, city: str) -> float:
        """Calculate realistic price based on location and type."""
        base_price = random.uniform(*self.config["price_ranges"][property_type])

        # Apply neighborhood multiplier
        neighborhood_key = f"{city}/{neighborhood}"
        multiplier = NEIGHBORHOOD_MULTIPLIERS.get(neighborhood_key, 1.0)

        # Apply some randomness
        variance = random.uniform(0.9, 1.1)

        return round(base_price * multiplier * variance, 2)
```

### Review Generator

```python
# app/data/generators/review_generator.py
from typing import List
import random
from transformers import pipeline  # For generating realistic text
from app.models.review import Review

class ReviewGenerator:
    def __init__(self):
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.text_generator = pipeline("text-generation", model="gpt2")

    def generate_reviews_for_property(self, property: Property) -> List[Review]:
        """Generate realistic reviews for a property."""
        num_reviews = self._determine_review_count(property)
        reviews = []

        for i in range(num_reviews):
            rating = self._select_rating()
            sentiment = self._determine_sentiment(rating)

            review = Review(
                id=self._generate_id(),
                property_id=property.id,
                rating=rating,
                title=self._generate_title(sentiment, property),
                content=self._generate_content(sentiment, property, rating),
                location_rating=self._generate_category_rating(rating),
                value_rating=self._generate_category_rating(rating),
                condition_rating=self._generate_category_rating(rating),
                amenities_rating=self._generate_category_rating(rating),
                sentiment=sentiment,
                sentiment_score=self._calculate_sentiment_score(rating),
                reviewer_type=self._select_reviewer_type(),
                verified_stay=random.random() > 0.3,
                # ... more fields
            )
            reviews.append(review)

        return reviews

    def _generate_content(self, sentiment: str, property: Property, rating: int) -> str:
        """Generate realistic review content."""
        templates = REVIEW_TEMPLATES[sentiment]
        template = random.choice(templates)

        # Fill template with property-specific data
        return template.format(
            property_type=property.property_type.value,
            neighborhood=property.address.neighborhood,
            amenity=random.choice(property.features.amenities or ["location"]),
            aspect=self._select_aspect(property),
            # ... more context
        )
```

## Data Seeding Process

### Migration Script

```python
# scripts/generate_mock_data.py
import asyncio
import duckdb
from app.data.generators import PropertyGenerator, ReviewGenerator

async def seed_database():
    """Seed DuckDB with 10,000 properties and reviews."""

    # Connect to DuckDB
    conn = duckdb.connect('data/properties.duckdb')

    # Create tables
    conn.execute(open('app/database/duckdb/schema.sql').read())

    # Generate properties
    print("Generating 10,000 properties...")
    property_gen = PropertyGenerator(GENERATION_CONFIG)
    properties = property_gen.generate_batch(10000)

    # Insert properties in batches
    batch_size = 1000
    for i in range(0, len(properties), batch_size):
        batch = properties[i:i+batch_size]
        insert_properties(conn, batch)
        print(f"Inserted {i+batch_size}/{len(properties)} properties")

    # Generate reviews
    print("Generating reviews...")
    review_gen = ReviewGenerator()
    for property in properties:
        reviews = review_gen.generate_reviews_for_property(property)
        insert_reviews(conn, reviews)

    # Update analytics
    print("Updating analytics...")
    update_analytics(conn)

    print("Data seeding completed!")
    conn.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
```

## Query Performance Optimization

### Materialized Views

```sql
-- Pre-compute popular aggregations
CREATE VIEW property_stats AS
SELECT
    p.id,
    p.city,
    p.neighborhood,
    p.property_type,
    COUNT(DISTINCT r.id) as review_count,
    AVG(r.rating) as avg_rating,
    AVG(r.sentiment_score) as avg_sentiment,
    p.price,
    p.bedrooms,
    p.bathrooms
FROM properties p
LEFT JOIN reviews r ON p.id = r.property_id
GROUP BY p.id, p.city, p.neighborhood, p.property_type, p.price, p.bedrooms, p.bathrooms;
```

### Common Query Patterns

```sql
-- Search by location and features
SELECT * FROM properties
WHERE city = 'Miami'
  AND neighborhood = 'Brickell'
  AND bedrooms >= 2
  AND price BETWEEN 2000 AND 4000
ORDER BY relevance_score DESC
LIMIT 20;

-- Get properties with best reviews
SELECT p.*, AVG(r.rating) as avg_rating
FROM properties p
JOIN reviews r ON p.id = r.property_id
WHERE p.city = 'Miami'
GROUP BY p.id
HAVING COUNT(r.id) >= 3
ORDER BY avg_rating DESC
LIMIT 10;

-- Sentiment analysis by neighborhood
SELECT
    p.neighborhood,
    AVG(r.sentiment_score) as avg_sentiment,
    COUNT(*) as review_count
FROM properties p
JOIN reviews r ON p.id = r.property_id
WHERE p.city = 'Miami'
GROUP BY p.neighborhood
ORDER BY avg_sentiment DESC;
```

## Data Quality Assurance

### Validation Rules

1. **Referential Integrity**: All reviews reference valid properties
2. **Price Consistency**: Prices within realistic ranges for property type/location
3. **Rating Correlation**: Sentiment score aligns with star rating
4. **Temporal Logic**: created_at <= updated_at
5. **Geographic Validity**: Latitude/longitude within city boundaries

### Data Quality Checks

```python
async def validate_data_quality(conn):
    """Run data quality checks."""

    checks = [
        ("Orphaned reviews", "SELECT COUNT(*) FROM reviews r LEFT JOIN properties p ON r.property_id = p.id WHERE p.id IS NULL"),
        ("Invalid prices", "SELECT COUNT(*) FROM properties WHERE price < 0 OR price > 50000"),
        ("Rating mismatch", "SELECT COUNT(*) FROM reviews WHERE (rating >= 4 AND sentiment = 'negative') OR (rating <= 2 AND sentiment = 'positive')"),
    ]

    for check_name, query in checks:
        result = conn.execute(query).fetchone()[0]
        assert result == 0, f"Data quality check failed: {check_name}"

    print("All data quality checks passed!")
```

## Backup and Versioning

### Backup Strategy

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
duckdb data/properties.duckdb "EXPORT DATABASE 'data/backups/backup_$DATE'"
```

### Version Control

```
data/
├── properties.duckdb          # Active database
├── backups/
│   ├── backup_20251111/       # Versioned backups
│   ├── backup_20251112/
│   └── ...
└── fixtures/
    ├── properties_v1.0.json   # JSON fixtures for git
    └── reviews_v1.0.json
```

---

**Document Version**: 1.0.0
**Author**: Architecture Agent (Hive Mind)
**Date**: 2025-11-11
**Status**: READY FOR IMPLEMENTATION
