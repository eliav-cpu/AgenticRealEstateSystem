"""
Mock Property Data Generator
Generates 10,000 realistic house entries for testing and development.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
import json


@dataclass
class PropertyData:
    """Property data model"""
    id: str
    address: str
    city: str
    state: str
    zip_code: str
    price: int
    bedrooms: int
    bathrooms: float
    square_feet: int
    lot_size: int
    year_built: int
    property_type: str
    status: str
    description: str
    amenities: List[str]
    images: List[str]
    latitude: float
    longitude: float
    listing_date: str
    days_on_market: int
    neighborhood: str
    school_rating: int
    crime_rating: str
    walkability_score: int
    transit_score: int
    agent_name: str
    agent_phone: str
    agent_email: str


class MockPropertyGenerator:
    """Generate realistic mock property data"""

    # Sample data pools
    CITIES = {
        "CA": ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "San Jose"],
        "TX": ["Houston", "Austin", "Dallas", "San Antonio", "Fort Worth"],
        "FL": ["Miami", "Orlando", "Tampa", "Jacksonville", "Fort Lauderdale"],
        "NY": ["New York", "Buffalo", "Rochester", "Yonkers", "Syracuse"],
        "IL": ["Chicago", "Aurora", "Naperville", "Joliet", "Rockford"]
    }

    STREETS = [
        "Main", "Oak", "Maple", "Cedar", "Pine", "Elm", "Washington", "Park",
        "Sunset", "Lake", "Hill", "Valley", "River", "Forest", "Mountain"
    ]

    STREET_TYPES = ["St", "Ave", "Blvd", "Dr", "Rd", "Ln", "Way", "Ct", "Pl"]

    PROPERTY_TYPES = ["Single Family", "Condo", "Townhouse", "Multi-Family", "Villa"]

    STATUSES = ["Active", "Pending", "Under Contract", "New Listing"]

    AMENITIES = [
        "Pool", "Garage", "Fireplace", "Hardwood Floors", "Granite Countertops",
        "Stainless Steel Appliances", "Walk-in Closet", "Patio", "Balcony",
        "Central AC", "Smart Home", "Solar Panels", "Home Office", "Gym",
        "Security System", "Spa", "Wine Cellar", "Game Room", "Library"
    ]

    NEIGHBORHOODS = [
        "Downtown", "Midtown", "Uptown", "Historic District", "Waterfront",
        "Suburbs", "Lake View", "Mountain View", "Park Side", "Green Valley"
    ]

    CRIME_RATINGS = ["Very Low", "Low", "Moderate", "High"]

    AGENT_FIRST_NAMES = [
        "John", "Sarah", "Michael", "Emily", "David", "Jessica", "James",
        "Jennifer", "Robert", "Lisa", "William", "Ashley", "Richard", "Michelle"
    ]

    AGENT_LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson"
    ]

    def __init__(self, seed: int = 42):
        """Initialize generator with random seed for reproducibility"""
        random.seed(seed)

    def _generate_address(self, state: str) -> Dict[str, str]:
        """Generate realistic address"""
        number = random.randint(100, 9999)
        street = random.choice(self.STREETS)
        street_type = random.choice(self.STREET_TYPES)
        city = random.choice(self.CITIES[state])
        zip_code = f"{random.randint(10000, 99999)}"

        return {
            "address": f"{number} {street} {street_type}",
            "city": city,
            "state": state,
            "zip_code": zip_code
        }

    def _generate_price(self, bedrooms: int, square_feet: int, state: str) -> int:
        """Generate realistic price based on features and location"""
        base_price = square_feet * random.randint(80, 250)
        bedroom_premium = bedrooms * random.randint(10000, 30000)

        # State multipliers
        state_multipliers = {
            "CA": 1.5, "NY": 1.4, "FL": 1.1, "TX": 0.9, "IL": 1.0
        }
        multiplier = state_multipliers.get(state, 1.0)

        price = int((base_price + bedroom_premium) * multiplier)
        # Round to nearest 5000
        return round(price / 5000) * 5000

    def _generate_coordinates(self, state: str) -> Dict[str, float]:
        """Generate realistic coordinates for state"""
        coords = {
            "CA": (34.0, -118.0),
            "TX": (30.0, -97.0),
            "FL": (26.0, -80.0),
            "NY": (40.7, -74.0),
            "IL": (41.8, -87.6)
        }
        base_lat, base_lon = coords.get(state, (35.0, -90.0))

        return {
            "latitude": round(base_lat + random.uniform(-2, 2), 6),
            "longitude": round(base_lon + random.uniform(-2, 2), 6)
        }

    def _generate_description(self, property_data: Dict[str, Any]) -> str:
        """Generate compelling property description"""
        templates = [
            f"Beautiful {property_data['property_type'].lower()} in {property_data['neighborhood']}. "
            f"Features {property_data['bedrooms']} bedrooms and {property_data['bathrooms']} bathrooms. "
            f"Built in {property_data['year_built']}, this home offers modern living with classic charm.",

            f"Stunning {property_data['property_type'].lower()} with {property_data['square_feet']} sq ft. "
            f"Located in the desirable {property_data['neighborhood']} area. "
            f"Don't miss this opportunity!",

            f"Immaculate {property_data['property_type'].lower()} featuring {property_data['bedrooms']} bedrooms. "
            f"Perfect for families looking for space and comfort. "
            f"Close to schools, shopping, and entertainment."
        ]
        return random.choice(templates)

    def generate_property(self, property_id: int) -> PropertyData:
        """Generate single property with realistic data"""
        # Basic attributes
        state = random.choice(list(self.CITIES.keys()))
        address_info = self._generate_address(state)

        bedrooms = random.choices([2, 3, 4, 5, 6], weights=[15, 35, 30, 15, 5])[0]
        bathrooms = random.choice([1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0])
        square_feet = random.randint(800, 5000)
        lot_size = random.randint(2000, 15000)
        year_built = random.randint(1950, 2024)
        property_type = random.choice(self.PROPERTY_TYPES)
        status = random.choices(
            self.STATUSES,
            weights=[60, 20, 15, 5]
        )[0]

        # Price calculation
        price = self._generate_price(bedrooms, square_feet, state)

        # Location data
        coords = self._generate_coordinates(state)
        neighborhood = random.choice(self.NEIGHBORHOODS)

        # Amenities (3-8 random amenities)
        num_amenities = random.randint(3, 8)
        amenities = random.sample(self.AMENITIES, num_amenities)

        # Images (3-10 placeholder images)
        num_images = random.randint(3, 10)
        images = [
            f"https://picsum.photos/800/600?property={property_id}&img={i}"
            for i in range(num_images)
        ]

        # Listing details
        days_ago = random.randint(0, 180)
        listing_date = (datetime.now() - timedelta(days=days_ago)).isoformat()

        # Ratings
        school_rating = random.randint(5, 10)
        crime_rating = random.choices(
            self.CRIME_RATINGS,
            weights=[30, 40, 20, 10]
        )[0]
        walkability_score = random.randint(20, 100)
        transit_score = random.randint(10, 95)

        # Agent info
        agent_first = random.choice(self.AGENT_FIRST_NAMES)
        agent_last = random.choice(self.AGENT_LAST_NAMES)
        agent_name = f"{agent_first} {agent_last}"
        agent_phone = f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
        agent_email = f"{agent_first.lower()}.{agent_last.lower()}@realestate.com"

        # Create property data dict for description
        property_dict = {
            "property_type": property_type,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "square_feet": square_feet,
            "year_built": year_built,
            "neighborhood": neighborhood
        }

        description = self._generate_description(property_dict)

        return PropertyData(
            id=f"PROP-{property_id:06d}",
            address=address_info["address"],
            city=address_info["city"],
            state=address_info["state"],
            zip_code=address_info["zip_code"],
            price=price,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            square_feet=square_feet,
            lot_size=lot_size,
            year_built=year_built,
            property_type=property_type,
            status=status,
            description=description,
            amenities=amenities,
            images=images,
            latitude=coords["latitude"],
            longitude=coords["longitude"],
            listing_date=listing_date,
            days_on_market=days_ago,
            neighborhood=neighborhood,
            school_rating=school_rating,
            crime_rating=crime_rating,
            walkability_score=walkability_score,
            transit_score=transit_score,
            agent_name=agent_name,
            agent_phone=agent_phone,
            agent_email=agent_email
        )

    def generate_batch(self, count: int = 10000) -> List[Dict[str, Any]]:
        """Generate batch of properties"""
        properties = []
        for i in range(1, count + 1):
            prop = self.generate_property(i)
            properties.append(asdict(prop))

            # Progress indicator
            if i % 1000 == 0:
                print(f"Generated {i}/{count} properties...")

        return properties

    def save_to_json(self, properties: List[Dict[str, Any]], filepath: str):
        """Save properties to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(properties, f, indent=2)
        print(f"Saved {len(properties)} properties to {filepath}")

    def save_to_duckdb(self, properties: List[Dict[str, Any]], db_path: str):
        """Save properties to DuckDB"""
        try:
            import duckdb

            conn = duckdb.connect(db_path)

            # Create table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS properties (
                    id VARCHAR PRIMARY KEY,
                    address VARCHAR,
                    city VARCHAR,
                    state VARCHAR,
                    zip_code VARCHAR,
                    price INTEGER,
                    bedrooms INTEGER,
                    bathrooms DOUBLE,
                    square_feet INTEGER,
                    lot_size INTEGER,
                    year_built INTEGER,
                    property_type VARCHAR,
                    status VARCHAR,
                    description TEXT,
                    amenities VARCHAR[],
                    images VARCHAR[],
                    latitude DOUBLE,
                    longitude DOUBLE,
                    listing_date TIMESTAMP,
                    days_on_market INTEGER,
                    neighborhood VARCHAR,
                    school_rating INTEGER,
                    crime_rating VARCHAR,
                    walkability_score INTEGER,
                    transit_score INTEGER,
                    agent_name VARCHAR,
                    agent_phone VARCHAR,
                    agent_email VARCHAR
                )
            """)

            # Insert data
            conn.executemany(
                "INSERT OR REPLACE INTO properties VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        p["id"], p["address"], p["city"], p["state"], p["zip_code"],
                        p["price"], p["bedrooms"], p["bathrooms"], p["square_feet"],
                        p["lot_size"], p["year_built"], p["property_type"], p["status"],
                        p["description"], p["amenities"], p["images"], p["latitude"],
                        p["longitude"], p["listing_date"], p["days_on_market"],
                        p["neighborhood"], p["school_rating"], p["crime_rating"],
                        p["walkability_score"], p["transit_score"], p["agent_name"],
                        p["agent_phone"], p["agent_email"]
                    )
                    for p in properties
                ]
            )

            conn.close()
            print(f"Saved {len(properties)} properties to DuckDB at {db_path}")

        except ImportError:
            print("DuckDB not installed. Install with: pip install duckdb")


def main():
    """Generate and save mock data"""
    generator = MockPropertyGenerator(seed=42)

    print("Generating 10,000 mock properties...")
    properties = generator.generate_batch(10000)

    # Save to JSON
    generator.save_to_json(properties, "data/mock_properties.json")

    # Save to DuckDB
    generator.save_to_duckdb(properties, "data/properties.duckdb")

    # Print sample
    print("\nSample property:")
    print(json.dumps(properties[0], indent=2))

    # Statistics
    print(f"\nGeneration complete!")
    print(f"Total properties: {len(properties)}")
    print(f"Price range: ${min(p['price'] for p in properties):,} - ${max(p['price'] for p in properties):,}")
    print(f"Average price: ${sum(p['price'] for p in properties) // len(properties):,}")


if __name__ == "__main__":
    main()
