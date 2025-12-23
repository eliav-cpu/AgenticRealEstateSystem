"""
Script para gerar 200+ imóveis realistas em Miami, FL.
"""

import json
import random
from datetime import datetime, timedelta

# Localizações de Miami com coordenadas aproximadas
LOCATIONS = {
    "Miami Beach": {"lat": 25.7907, "lon": -80.1300, "premium": True, "count": 30},
    "South Beach": {"lat": 25.7825, "lon": -80.1341, "premium": True, "count": 25},
    "Brickell": {"lat": 25.7617, "lon": -80.1918, "premium": True, "count": 35},
    "Downtown Miami": {"lat": 25.7751, "lon": -80.1947, "premium": False, "count": 20},
    "Coral Gables": {"lat": 25.7215, "lon": -80.2684, "premium": True, "count": 20},
    "Coconut Grove": {"lat": 25.7270, "lon": -80.2414, "premium": True, "count": 15},
    "Wynwood": {"lat": 25.8011, "lon": -80.1998, "premium": False, "count": 15},
    "Design District": {"lat": 25.8122, "lon": -80.1925, "premium": True, "count": 10},
    "Fort Lauderdale": {"lat": 26.1224, "lon": -80.1373, "premium": False, "count": 15},
    "Hollywood": {"lat": 26.0112, "lon": -80.1495, "premium": False, "count": 10},
    "Aventura": {"lat": 25.9565, "lon": -80.1392, "premium": True, "count": 10},
    "Key Biscayne": {"lat": 25.6938, "lon": -80.1625, "premium": True, "count": 8},
    "Miami Shores": {"lat": 25.8631, "lon": -80.1928, "premium": False, "count": 5},
    "Pinecrest": {"lat": 25.6668, "lon": -80.3065, "premium": True, "count": 5},
}

# Ruas reais de Miami por localização
STREETS = {
    "Miami Beach": ["Collins Ave", "Ocean Drive", "Washington Ave", "Alton Rd", "Pine Tree Dr", "Indian Creek Dr", "Bay Rd"],
    "South Beach": ["Ocean Drive", "Collins Ave", "Washington Ave", "Espanola Way", "Lincoln Rd", "Meridian Ave"],
    "Brickell": ["Brickell Ave", "SE 1st Ave", "SW 8th St", "SE 2nd Ave", "Brickell Bay Dr", "SE 10th St"],
    "Downtown Miami": ["Biscayne Blvd", "NE 2nd Ave", "Flagler St", "NE 1st Ave", "NW 1st St", "SE 1st St"],
    "Coral Gables": ["Miracle Mile", "Ponce de Leon Blvd", "Granada Blvd", "Alhambra Cir", "Salzedo St"],
    "Coconut Grove": ["Main Hwy", "Grand Ave", "McFarlane Rd", "Virginia St", "Tigertail Ave"],
    "Wynwood": ["NW 2nd Ave", "NW 24th St", "NW 25th St", "NW 3rd Ave", "NW 26th St"],
    "Design District": ["NE 40th St", "NE 2nd Ave", "NE 39th St", "N Miami Ave", "NE 41st St"],
    "Fort Lauderdale": ["Las Olas Blvd", "A1A", "SE 17th St", "Sunrise Blvd", "Federal Hwy"],
    "Hollywood": ["Hollywood Blvd", "A1A", "Young Cir", "Harrison St", "Tyler St"],
    "Aventura": ["Biscayne Blvd", "NE 187th St", "Country Club Dr", "Aventura Blvd"],
    "Key Biscayne": ["Crandon Blvd", "Harbor Dr", "Ocean Ln", "Sunrise Dr", "Fernwood Rd"],
    "Miami Shores": ["NE 2nd Ave", "NW 103rd St", "Grand Concourse", "NE 96th St"],
    "Pinecrest": ["SW 67th Ave", "Red Rd", "SW 136th St", "SW 72nd Ave"],
}

# Tipos de propriedade com distribuição
PROPERTY_TYPES = {
    "apartment": 40,
    "condo": 30,
    "house": 15,
    "studio": 8,
    "loft": 4,
    "penthouse": 3,
}

# Amenidades por categoria
AMENITIES = {
    "basic": ["parking", "laundry", "a/c"],
    "standard": ["parking", "laundry", "a/c", "gym", "pool"],
    "premium": ["parking", "laundry", "a/c", "gym", "pool", "concierge", "doorman", "rooftop"],
    "luxury": ["parking", "laundry", "a/c", "gym", "pool", "concierge", "doorman", "rooftop", "ocean_view", "valet", "spa"],
    "waterfront": ["parking", "laundry", "a/c", "gym", "pool", "ocean_view", "beach_access", "private_dock"],
}

# Preços base por tipo e localização premium
PRICE_RANGES = {
    "studio": {"min": 1200, "max": 2500, "premium_mult": 1.5},
    "apartment": {"min": 1800, "max": 4500, "premium_mult": 1.6},
    "condo": {"min": 2500, "max": 6000, "premium_mult": 1.7},
    "loft": {"min": 2200, "max": 5000, "premium_mult": 1.5},
    "house": {"min": 3500, "max": 10000, "premium_mult": 1.8},
    "penthouse": {"min": 8000, "max": 25000, "premium_mult": 2.0},
}

# Configurações por tipo de propriedade
PROPERTY_CONFIG = {
    "studio": {"beds": (0, 0), "baths": (1, 1), "sqft": (350, 600)},
    "apartment": {"beds": (1, 3), "baths": (1, 2), "sqft": (700, 1800)},
    "condo": {"beds": (1, 3), "baths": (1, 3), "sqft": (900, 2200)},
    "loft": {"beds": (1, 2), "baths": (1, 2), "sqft": (800, 1500)},
    "house": {"beds": (2, 5), "baths": (2, 4), "sqft": (1500, 4000)},
    "penthouse": {"beds": (2, 4), "baths": (2, 4), "sqft": (2000, 5000)},
}

# Pet policies
PET_POLICIES = ["no_pets", "cats_allowed", "dogs_allowed", "dogs_and_cats_allowed", "small_pets_allowed"]

# Descrições por tipo
DESCRIPTIONS = {
    "studio": [
        "Cozy studio in the heart of {location}. Perfect for young professionals.",
        "Modern studio with city views. Walking distance to restaurants and shops.",
        "Bright and airy studio with updated finishes. Great for urban living.",
        "Stylish studio apartment with modern kitchen and plenty of natural light.",
    ],
    "apartment": [
        "Spacious {beds}-bedroom apartment in {location}. Recently renovated with modern appliances.",
        "Beautiful {beds}BR apartment with stunning views. Close to public transportation.",
        "Well-maintained {beds}-bedroom unit with in-unit laundry and covered parking.",
        "Contemporary {beds}BR apartment featuring open floor plan and designer finishes.",
    ],
    "condo": [
        "Luxury {beds}-bedroom condo in prestigious {location}. Resort-style amenities.",
        "Elegant {beds}BR condo with floor-to-ceiling windows and premium finishes.",
        "Stunning {beds}-bedroom waterfront condo with panoramic views.",
        "Modern {beds}BR condo in full-service building with 24/7 concierge.",
    ],
    "loft": [
        "Industrial-chic loft in trendy {location}. High ceilings and exposed brick.",
        "Unique {beds}-bedroom loft with soaring ceilings and open concept design.",
        "Artist's dream loft with abundant natural light and flexible space.",
    ],
    "house": [
        "Charming {beds}-bedroom house in quiet {location} neighborhood. Large backyard.",
        "Spacious {beds}BR family home with pool. Perfect for entertaining.",
        "Beautiful {beds}-bedroom residence with modern updates throughout.",
        "Stunning {beds}BR home with chef's kitchen and outdoor living space.",
    ],
    "penthouse": [
        "Ultra-luxury penthouse in {location}. Breathtaking 360-degree views.",
        "Spectacular {beds}-bedroom penthouse with private terrace and premium finishes.",
        "One-of-a-kind penthouse residence with unobstructed ocean views.",
        "Magnificent {beds}BR penthouse featuring smart home technology throughout.",
    ],
}


def generate_property(prop_id: int, location: str, loc_data: dict, prop_type: str) -> dict:
    """Generate a single property."""
    config = PROPERTY_CONFIG[prop_type]
    price_range = PRICE_RANGES[prop_type]

    # Generate bedrooms and bathrooms
    beds = random.randint(config["beds"][0], config["beds"][1])
    baths = random.randint(config["baths"][0], config["baths"][1])
    if baths < beds and prop_type != "studio":
        baths = beds  # At least as many baths as beds for nicer properties

    # Generate square feet
    sqft = random.randint(config["sqft"][0], config["sqft"][1])

    # Calculate price based on location premium and size
    base_price = random.randint(price_range["min"], price_range["max"])
    if loc_data["premium"]:
        base_price = int(base_price * price_range["premium_mult"])
    # Adjust for bedrooms
    base_price = int(base_price * (1 + beds * 0.15))
    # Round to nearest 50
    price = round(base_price / 50) * 50

    # Generate address
    street = random.choice(STREETS.get(location, ["Main St"]))
    number = random.randint(100, 9999)
    address = f"{number} {street}"

    # Generate coordinates with slight variation
    lat = loc_data["lat"] + random.uniform(-0.02, 0.02)
    lon = loc_data["lon"] + random.uniform(-0.02, 0.02)

    # Select amenities based on price tier
    if price > 10000:
        amenity_set = "luxury"
    elif price > 5000:
        amenity_set = "premium"
    elif price > 3000:
        amenity_set = "standard"
    else:
        amenity_set = "basic"

    # Add waterfront amenities for premium coastal locations
    if location in ["Miami Beach", "South Beach", "Key Biscayne"] and random.random() > 0.5:
        amenities = list(set(AMENITIES[amenity_set] + AMENITIES["waterfront"]))
    else:
        amenities = AMENITIES[amenity_set].copy()

    # Add some random additional amenities
    extra_amenities = ["bbq_area", "tennis_court", "business_center", "children_playground",
                       "pet_spa", "wine_cellar", "smart_home", "ev_charging", "storage_unit"]
    if random.random() > 0.6:
        amenities.append(random.choice(extra_amenities))

    # Generate description
    desc_template = random.choice(DESCRIPTIONS[prop_type])
    description = desc_template.format(beds=beds, location=location)

    # Generate available date (within next 60 days)
    available_date = datetime.now() + timedelta(days=random.randint(1, 60))

    # Generate timestamps
    created_at = datetime.now() - timedelta(days=random.randint(1, 30))
    updated_at = created_at + timedelta(days=random.randint(0, 7))

    return {
        "id": f"prop_{prop_id:03d}",
        "address": address,
        "city": location if location not in ["Fort Lauderdale", "Hollywood", "Aventura"] else location,
        "state": "FL",
        "zip_code": f"33{random.randint(100, 199)}",
        "country": "USA",
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
        "price": price,
        "bedrooms": beds,
        "bathrooms": baths,
        "square_feet": sqft,
        "property_type": prop_type,
        "description": description,
        "amenities": amenities,
        "available_date": available_date.strftime("%Y-%m-%d"),
        "images": [
            f"https://example.com/images/prop_{prop_id:03d}_{i}.jpg"
            for i in range(1, random.randint(2, 6))
        ],
        "pet_policy": random.choice(PET_POLICIES),
        "lease_duration": random.choice([6, 12, 18, 24]),
        "utilities_included": random.sample(["water", "trash", "gas", "internet", "cable"],
                                           k=random.randint(0, 3)),
        "created_at": created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updated_at": updated_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def generate_all_properties() -> list:
    """Generate all 200+ properties."""
    properties = []
    prop_id = 1

    # Generate properties for each location
    for location, loc_data in LOCATIONS.items():
        count = loc_data["count"]

        for _ in range(count):
            # Select property type based on distribution
            prop_type = random.choices(
                list(PROPERTY_TYPES.keys()),
                weights=list(PROPERTY_TYPES.values())
            )[0]

            # Penthouses only in premium locations
            if prop_type == "penthouse" and not loc_data["premium"]:
                prop_type = "condo"

            # Houses less common in urban areas
            if prop_type == "house" and location in ["Brickell", "Downtown Miami", "Wynwood"]:
                prop_type = "apartment"

            prop = generate_property(prop_id, location, loc_data, prop_type)
            properties.append(prop)
            prop_id += 1

    return properties


if __name__ == "__main__":
    print("Generating 200+ Miami properties...")
    properties = generate_all_properties()

    # Save to fixtures
    output_path = "app/data/fixtures/properties.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(properties, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(properties)} properties!")
    print(f"Saved to: {output_path}")

    # Print summary
    by_type = {}
    by_location = {}
    for p in properties:
        by_type[p["property_type"]] = by_type.get(p["property_type"], 0) + 1
        by_location[p["city"]] = by_location.get(p["city"], 0) + 1

    print("\nBy Type:")
    for t, c in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")

    print("\nBy Location:")
    for l, c in sorted(by_location.items(), key=lambda x: -x[1]):
        print(f"  {l}: {c}")

    # Price range
    prices = [p["price"] for p in properties]
    print(f"\nPrice Range: ${min(prices):,} - ${max(prices):,}")
    print(f"Average Price: ${sum(prices)//len(prices):,}")
