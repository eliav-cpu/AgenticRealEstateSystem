"""
Migration script to transfer mock properties from in-memory to DuckDB

This script extracts the hardcoded mock properties from api_config.py
and loads them into DuckDB for persistent storage in Mock mode.
"""

from typing import List, Dict, Any
from app.utils.logging import get_logger
from .schema import PropertyDB

logger = get_logger("property_migration")


def get_mock_properties_data() -> List[Dict[str, Any]]:
    """
    Extract mock properties data from the original hardcoded structure.
    
    Returns:
        List of properties in RentCast API format
    """
    # MOCK DATA WITH REAL MIAMI PROPERTIES - EXACT RENTCAST API STRUCTURE
    # This matches the data from config/api_config.py
    mock_rentcast_data = [
        {
            "id": "15741-Sw-137th-Ave,-Apt-204,-Miami,-FL-33177",
            "formattedAddress": "15741 Sw 137th Ave, Apt 204, Miami, FL 33177",
            "addressLine1": "15741 Sw 137th Ave",
            "addressLine2": "Apt 204",
            "city": "Miami",
            "state": "FL",
            "zipCode": "33177",
            "county": "Miami-Dade",
            "latitude": 25.6234,
            "longitude": -80.4123,
            "propertyType": "Apartment",
            "bedrooms": 3,
            "bathrooms": 2,
            "squareFootage": 1120,
            "lotSize": 0,
            "yearBuilt": 2001,
            "status": "ForRent",
            "price": 2450,
            "listingType": "Standard",
            "listedDate": "2025-04-11T00:00:00.000Z",
            "removedDate": None,
            "createdDate": "2025-04-11T00:00:00.000Z",
            "lastSeenDate": "2025-06-23T05:02:02.468Z",
            "daysOnMarket": 73,
            "mlsName": "MLS",
            "mlsNumber": "A11780877",
            "listingAgent": {
                "name": "Berlybel Carrasquillo",
                "phone": "9549187117",
                "email": "listings@interinvestments.com",
                "website": ""
            },
            "listingOffice": {
                "name": "United Realty Group Inc",
                "phone": "9544502000",
                "email": "broker@urgfl.com"
            },
            "history": {
                "2025-04-11": {
                    "event": "Rental Listing",
                    "price": 2450,
                    "listingType": "Standard",
                    "listedDate": "2025-04-11T00:00:00.000Z",
                    "removedDate": None,
                    "daysOnMarket": 73
                }
            }
        },
        {
            "id": "1050-Brickell-Ave,-Apt-3504,-Miami,-FL-33131",
            "formattedAddress": "1050 Brickell Ave, Apt 3504, Miami, FL 33131",
            "addressLine1": "1050 Brickell Ave",
            "addressLine2": "Apt 3504",
            "city": "Miami",
            "state": "FL",
            "zipCode": "33131",
            "county": "Miami-Dade",
            "latitude": 25.7617,
            "longitude": -80.1918,
            "propertyType": "Apartment",
            "bedrooms": 3,
            "bathrooms": 3,
            "squareFootage": 2238,
            "lotSize": 0,
            "yearBuilt": 2008,
            "status": "ForRent",
            "price": 12000,
            "listingType": "Premium",
            "listedDate": "2025-04-13T00:00:00.000Z",
            "removedDate": None,
            "createdDate": "2025-04-13T00:00:00.000Z",
            "lastSeenDate": "2025-06-23T05:02:02.468Z",
            "daysOnMarket": 71,
            "mlsName": "MLS",
            "mlsNumber": "A11783197",
            "listingAgent": {
                "name": "Francine Hector",
                "phone": "7864346999",
                "email": "francine@rhmiami.com",
                "website": ""
            },
            "listingOffice": {
                "name": "RH Miami",
                "phone": "3057074663",
                "email": "info@rhmiami.com"
            },
            "history": {
                "2025-04-13": {
                    "event": "Rental Listing",
                    "price": 12000,
                    "listingType": "Premium",
                    "listedDate": "2025-04-13T00:00:00.000Z",
                    "removedDate": None,
                    "daysOnMarket": 71
                }
            }
        },
        {
            "id": "4301-Nw-8th-Ter,-Apt-44,-Miami,-FL-33126",
            "formattedAddress": "4301 Nw 8th Ter, Apt 44, Miami, FL 33126",
            "addressLine1": "4301 Nw 8th Ter",
            "addressLine2": "Apt 44",
            "city": "Miami",
            "state": "FL",
            "zipCode": "33126",
            "county": "Miami-Dade",
            "latitude": 25.7796,
            "longitude": -80.2611,
            "propertyType": "Apartment",
            "bedrooms": 2,
            "bathrooms": 1,
            "squareFootage": 21286,
            "lotSize": 0,
            "yearBuilt": 1955,
            "status": "ForRent",
            "price": 2300,
            "listingType": "Standard",
            "listedDate": "2025-05-15T00:00:00.000Z",
            "removedDate": None,
            "createdDate": "2025-05-15T00:00:00.000Z",
            "lastSeenDate": "2025-06-23T05:02:02.468Z",
            "daysOnMarket": 39,
            "mlsName": "MLS",
            "mlsNumber": "A11834567",
            "listingAgent": {
                "name": "Carlos Rodriguez",
                "phone": "3051234567",
                "email": "carlos@miamirealty.com",
                "website": ""
            },
            "listingOffice": {
                "name": "Miami Realty Solutions",
                "phone": "3055551234",
                "email": "info@miamirealty.com"
            },
            "history": {
                "2025-05-15": {
                    "event": "Rental Listing",
                    "price": 2300,
                    "listingType": "Standard",
                    "listedDate": "2025-05-15T00:00:00.000Z",
                    "removedDate": None,
                    "daysOnMarket": 39
                }
            }
        },
        {
            "id": "2000-Ocean-Dr,-Apt-1201,-Miami-Beach,-FL-33139",
            "formattedAddress": "2000 Ocean Dr, Apt 1201, Miami Beach, FL 33139",
            "addressLine1": "2000 Ocean Dr",
            "addressLine2": "Apt 1201",
            "city": "Miami Beach",
            "state": "FL",
            "zipCode": "33139",
            "county": "Miami-Dade",
            "latitude": 25.7817,
            "longitude": -80.1301,
            "propertyType": "Apartment",
            "bedrooms": 4,
            "bathrooms": 3,
            "squareFootage": 1800,
            "lotSize": 0,
            "yearBuilt": 2015,
            "status": "ForRent",
            "price": 8500,
            "listingType": "Luxury",
            "listedDate": "2025-03-20T00:00:00.000Z",
            "removedDate": None,
            "createdDate": "2025-03-20T00:00:00.000Z",
            "lastSeenDate": "2025-06-23T05:02:02.468Z",
            "daysOnMarket": 95,
            "mlsName": "MLS",
            "mlsNumber": "A11756123",
            "listingAgent": {
                "name": "Elena Martinez",
                "phone": "7863456789",
                "email": "elena@oceanfrontrealty.com",
                "website": ""
            },
            "listingOffice": {
                "name": "Oceanfront Realty",
                "phone": "3056789012",
                "email": "luxury@oceanfrontrealty.com"
            },
            "history": {
                "2025-03-20": {
                    "event": "Rental Listing",
                    "price": 8500,
                    "listingType": "Luxury",
                    "listedDate": "2025-03-20T00:00:00.000Z",
                    "removedDate": None,
                    "daysOnMarket": 95
                }
            }
        },
        {
            "id": "1000-S-Pointe-Dr,-Apt-2502,-Miami-Beach,-FL-33139",
            "formattedAddress": "1000 S Pointe Dr, Apt 2502, Miami Beach, FL 33139",
            "addressLine1": "1000 S Pointe Dr",
            "addressLine2": "Apt 2502",
            "city": "Miami Beach",
            "state": "FL",
            "zipCode": "33139",
            "county": "Miami-Dade",
            "latitude": 25.7701,
            "longitude": -80.1340,
            "propertyType": "Apartment",
            "bedrooms": 2,
            "bathrooms": 2,
            "squareFootage": 1500,
            "lotSize": 0,
            "yearBuilt": 2020,
            "status": "ForRent",
            "price": 5200,
            "listingType": "Premium",
            "listedDate": "2025-06-01T00:00:00.000Z",
            "removedDate": None,
            "createdDate": "2025-06-01T00:00:00.000Z",
            "lastSeenDate": "2025-06-23T05:02:02.468Z",
            "daysOnMarket": 22,
            "mlsName": "MLS",
            "mlsNumber": "A11845678",
            "listingAgent": {
                "name": "Michael Johnson",
                "phone": "3057891234",
                "email": "michael@southbeachluxury.com",
                "website": ""
            },
            "listingOffice": {
                "name": "South Beach Luxury Properties",
                "phone": "3054567890",
                "email": "info@southbeachluxury.com"
            },
            "history": {
                "2025-06-01": {
                    "event": "Rental Listing",
                    "price": 5200,
                    "listingType": "Premium",
                    "listedDate": "2025-06-01T00:00:00.000Z",
                    "removedDate": None,
                    "daysOnMarket": 22
                }
            }
        },
        {
            "id": "850-N-Miami-Ave,-Apt-W702,-Miami,-FL-33136",
            "formattedAddress": "850 N Miami Ave, Apt W702, Miami, FL 33136",
            "addressLine1": "850 N Miami Ave",
            "addressLine2": "Apt W702",
            "city": "Miami",
            "state": "FL",
            "zipCode": "33136",
            "county": "Miami-Dade",
            "latitude": 25.7825,
            "longitude": -80.1977,
            "propertyType": "Apartment",
            "bedrooms": 1,
            "bathrooms": 1,
            "squareFootage": 750,
            "lotSize": 0,
            "yearBuilt": 2018,
            "status": "ForRent",
            "price": 3200,
            "listingType": "Standard",
            "listedDate": "2025-05-25T00:00:00.000Z",
            "removedDate": None,
            "createdDate": "2025-05-25T00:00:00.000Z",
            "lastSeenDate": "2025-06-23T05:02:02.468Z",
            "daysOnMarket": 29,
            "mlsName": "MLS",
            "mlsNumber": "A11841234",
            "listingAgent": {
                "name": "Sarah Williams",
                "phone": "7862345678",
                "email": "sarah@downtownmiami.com",
                "website": ""
            },
            "listingOffice": {
                "name": "Downtown Miami Properties",
                "phone": "3053456789",
                "email": "rentals@downtownmiami.com"
            },
            "history": {
                "2025-05-25": {
                    "event": "Rental Listing",
                    "price": 3200,
                    "listingType": "Standard",
                    "listedDate": "2025-05-25T00:00:00.000Z",
                    "removedDate": None,
                    "daysOnMarket": 29
                }
            }
        },
        {
            "id": "3301-Ne-1st-Ave,-Apt-H1205,-Miami,-FL-33137",
            "formattedAddress": "3301 Ne 1st Ave, Apt H1205, Miami, FL 33137",
            "addressLine1": "3301 Ne 1st Ave",
            "addressLine2": "Apt H1205",
            "city": "Miami",
            "state": "FL",
            "zipCode": "33137",
            "county": "Miami-Dade",
            "latitude": 25.8076,
            "longitude": -80.1867,
            "propertyType": "Apartment",
            "bedrooms": 3,
            "bathrooms": 2,
            "squareFootage": 1400,
            "lotSize": 0,
            "yearBuilt": 2019,
            "status": "ForRent",
            "price": 4800,
            "listingType": "Standard",
            "listedDate": "2025-04-28T00:00:00.000Z",
            "removedDate": None,
            "createdDate": "2025-04-28T00:00:00.000Z",
            "lastSeenDate": "2025-06-23T05:02:02.468Z",
            "daysOnMarket": 56,
            "mlsName": "MLS",
            "mlsNumber": "A11823456",
            "listingAgent": {
                "name": "David Chen",
                "phone": "3056789123",
                "email": "david@midtownproperties.com",
                "website": ""
            },
            "listingOffice": {
                "name": "Midtown Properties Group",
                "phone": "3057890123",
                "email": "leasing@midtownproperties.com"
            },
            "history": {
                "2025-04-28": {
                    "event": "Rental Listing",
                    "price": 4800,
                    "listingType": "Standard",
                    "listedDate": "2025-04-28T00:00:00.000Z",
                    "removedDate": None,
                    "daysOnMarket": 56
                }
            }
        },
        {
            "id": "500-Brickell-Ave,-Apt-4109,-Miami,-FL-33131",
            "formattedAddress": "500 Brickell Ave, Apt 4109, Miami, FL 33131",
            "addressLine1": "500 Brickell Ave",
            "addressLine2": "Apt 4109",
            "city": "Miami",
            "state": "FL",
            "zipCode": "33131",
            "county": "Miami-Dade",
            "latitude": 25.7656,
            "longitude": -80.1917,
            "propertyType": "Apartment",
            "bedrooms": 2,
            "bathrooms": 2,
            "squareFootage": 1100,
            "lotSize": 0,
            "yearBuilt": 2016,
            "status": "ForRent",
            "price": 3800,
            "listingType": "Standard",
            "listedDate": "2025-06-10T00:00:00.000Z",
            "removedDate": None,
            "createdDate": "2025-06-10T00:00:00.000Z",
            "lastSeenDate": "2025-06-23T05:02:02.468Z",
            "daysOnMarket": 13,
            "mlsName": "MLS",
            "mlsNumber": "A11849876",
            "listingAgent": {
                "name": "Jennifer Lopez",
                "phone": "3051112222",
                "email": "jennifer@brickellrealty.com",
                "website": ""
            },
            "listingOffice": {
                "name": "Brickell Realty Group",
                "phone": "3053334444",
                "email": "info@brickellrealty.com"
            },
            "history": {
                "2025-06-10": {
                    "event": "Rental Listing",
                    "price": 3800,
                    "listingType": "Standard",
                    "listedDate": "2025-06-10T00:00:00.000Z",
                    "removedDate": None,
                    "daysOnMarket": 13
                }
            }
        },
        {
            "id": "1800-Club-Dr,-Apt-706,-Miami-Beach,-FL-33141",
            "formattedAddress": "1800 Club Dr, Apt 706, Miami Beach, FL 33141",
            "addressLine1": "1800 Club Dr",
            "addressLine2": "Apt 706",
            "city": "Miami Beach",
            "state": "FL",
            "zipCode": "33141",
            "county": "Miami-Dade",
            "latitude": 25.8234,
            "longitude": -80.1423,
            "propertyType": "Apartment",
            "bedrooms": 1,
            "bathrooms": 1,
            "squareFootage": 850,
            "lotSize": 0,
            "yearBuilt": 2017,
            "status": "ForRent",
            "price": 2800,
            "listingType": "Standard",
            "listedDate": "2025-05-18T00:00:00.000Z",
            "removedDate": None,
            "createdDate": "2025-05-18T00:00:00.000Z",
            "lastSeenDate": "2025-06-23T05:02:02.468Z",
            "daysOnMarket": 36,
            "mlsName": "MLS",
            "mlsNumber": "A11837890",
            "listingAgent": {
                "name": "Roberto Silva",
                "phone": "7865556666",
                "email": "roberto@beachfrontproperties.com",
                "website": ""
            },
            "listingOffice": {
                "name": "Beachfront Properties Inc",
                "phone": "3057778888",
                "email": "rentals@beachfrontproperties.com"
            },
            "history": {
                "2025-05-18": {
                    "event": "Rental Listing",
                    "price": 2800,
                    "listingType": "Standard",
                    "listedDate": "2025-05-18T00:00:00.000Z",
                    "removedDate": None,
                    "daysOnMarket": 36
                }
            }
        }
    ]
    
    return mock_rentcast_data


def migrate_mock_to_duckdb(db_path: str = "data/properties.duckdb", force_reload: bool = False) -> bool:
    """
    Migrate mock properties from hardcoded data to DuckDB.
    
    Args:
        db_path: Path to DuckDB database file
        force_reload: If True, clear existing data and reload
        
    Returns:
        True if migration successful, False otherwise
    """
    try:
        # Initialize PropertyDB in write mode for migration
        property_db = PropertyDB(db_path, read_only=False)
        
        # Check if data already exists
        existing_count = property_db.get_property_count()
        
        if existing_count > 0 and not force_reload:
            logger.info(f"Database already contains {existing_count} properties - skipping migration")
            logger.info("Use force_reload=True to reload data")
            return True
        
        if force_reload and existing_count > 0:
            logger.info(f"Force reload requested - clearing {existing_count} existing properties")
            property_db.clear_all_properties()
        
        # Get mock data
        mock_properties = get_mock_properties_data()
        logger.info(f"Starting migration of {len(mock_properties)} mock properties to DuckDB")
        
        # Insert each property
        successful_inserts = 0
        failed_inserts = 0
        
        for property_data in mock_properties:
            if property_db.insert_property(property_data):
                successful_inserts += 1
                logger.debug(f"Inserted property: {property_data['formattedAddress']}")
            else:
                failed_inserts += 1
                logger.error(f"Failed to insert property: {property_data.get('formattedAddress', 'unknown')}")
        
        # Verify migration
        final_count = property_db.get_property_count()
        
        logger.info("Migration completed!")
        logger.info(f"   Successfully inserted: {successful_inserts} properties")
        logger.info(f"   Failed inserts: {failed_inserts} properties")
        logger.info(f"   Total in database: {final_count} properties")
        
        # Close connection
        property_db.close()
        
        return successful_inserts > 0
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False


def verify_migration(db_path: str = "data/properties.duckdb") -> bool:
    """
    Verify that migration was successful by running test queries.
    
    Args:
        db_path: Path to DuckDB database file
        
    Returns:
        True if verification passed, False otherwise
    """
    try:
        # Use read-only mode for verification (no writes needed)
        property_db = PropertyDB(db_path, read_only=True)

        # Test 1: Count properties
        count = property_db.get_property_count()
        logger.info(f"Total properties in database: {count}")
        
        if count == 0:
            logger.error("No properties found in database")
            return False
        
        # Test 2: Search by city
        miami_properties = property_db.search_properties({"city": "Miami"})
        miami_beach_properties = property_db.search_properties({"city": "Miami Beach"})
        logger.info(f"Properties in Miami: {len(miami_properties)}")
        logger.info(f"Properties in Miami Beach: {len(miami_beach_properties)}")
        
        # Test 3: Search by bedrooms
        one_bedroom = property_db.search_properties({"bedrooms": 1})
        two_bedroom = property_db.search_properties({"bedrooms": 2})
        three_bedroom = property_db.search_properties({"bedrooms": 3})
        logger.info(f"1-bedroom properties: {len(one_bedroom)}")
        logger.info(f"2-bedroom properties: {len(two_bedroom)}")
        logger.info(f"3-bedroom properties: {len(three_bedroom)}")
        
        # Test 4: Search by price range
        budget_properties = property_db.search_properties({"max_price": 3000})
        luxury_properties = property_db.search_properties({"min_price": 8000})
        logger.info(f"Properties under $3000: {len(budget_properties)}")
        logger.info(f"Properties over $8000: {len(luxury_properties)}")
        
        # Test 5: Get specific property
        test_property = property_db.get_property_by_id("4301-Nw-8th-Ter,-Apt-44,-Miami,-FL-33126")
        if test_property:
            logger.info(f"Found test property: {test_property['formattedAddress']} - ${test_property['price']}/month")
        else:
            logger.error("Could not find test property by ID")
            return False
        
        property_db.close()
        
        logger.info("All verification tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False


if __name__ == "__main__":
    """Run migration when script is executed directly."""
    logger.info("Starting mock property migration to DuckDB...")
    
    success = migrate_mock_to_duckdb(force_reload=True)
    
    if success:
        logger.info("Migration successful - running verification...")
        verify_migration()
    else:
        logger.error("Migration failed!")
        exit(1)