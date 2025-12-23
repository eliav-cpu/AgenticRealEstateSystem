#!/usr/bin/env python3
"""
Load 223 Miami properties into DuckDB database.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import json
from app.database.schema import PropertyDB

def main():
    # Load the 223 Miami properties
    with open('app/data/fixtures/properties.json', 'r') as f:
        properties = json.load(f)

    print(f"Loaded {len(properties)} properties from fixtures")

    # Import the DuckDB schema in write mode for loading data
    db = PropertyDB(read_only=False)

    # Clear existing data first
    print("Clearing existing DuckDB data...")
    db.clear_all_properties()

    # Load new properties
    print("Loading properties into DuckDB...")
    count = 0
    for prop in properties:
        try:
            # Convert to the format expected by DuckDB (camelCase keys for RentCast API format)
            db_prop = {
                'id': prop['id'],
                'formattedAddress': f"{prop['address']}, {prop['city']}, {prop['state']} {prop['zip_code']}",
                'addressLine1': prop['address'],
                'addressLine2': '',
                'city': prop['city'],
                'state': prop['state'],
                'zipCode': prop['zip_code'],
                'county': 'Miami-Dade',
                'latitude': prop['latitude'],
                'longitude': prop['longitude'],
                'propertyType': prop['property_type'],
                'bedrooms': prop['bedrooms'],
                'bathrooms': prop['bathrooms'],
                'squareFootage': prop['square_feet'],
                'lotSize': 0,
                'yearBuilt': 2020,
                'status': 'ForRent',
                'price': prop['price'],
                'listingType': 'For Rent',
                'listedDate': prop['available_date'],
                'removedDate': None,
                'createdDate': prop['created_at'],
                'lastSeenDate': prop['updated_at'],
                'daysOnMarket': 30,
                'mlsName': 'Miami MLS',
                'mlsNumber': f'MLS-{prop["id"]}',
                'listingAgent': {'name': 'Miami Agent', 'phone': '305-555-0100'},
                'listingOffice': {'name': 'Miami Realty', 'phone': '305-555-0200'},
                'history': {},
            }
            db.insert_property(db_prop)
            count += 1
        except Exception as e:
            print(f"Error inserting property {prop['id']}: {e}")

    print(f"✓ Loaded {count} properties into DuckDB")

    # Verify
    result = db.search_properties({})
    print(f"✓ Verified: {len(result)} properties in database")

if __name__ == "__main__":
    main()
