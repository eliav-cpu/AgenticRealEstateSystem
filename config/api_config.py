"""
API Configuration - Mock vs Real Mode

Allows switching between mock data (unlimited testing) and real API (controlled usage).
"""

import os
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import requests
from app.utils.logging import get_logger

# DuckDB storage for Mock mode only
try:
    from app.database.schema import PropertyDB
    from app.database.migration import migrate_mock_to_duckdb
    DUCKDB_AVAILABLE = True
except ImportError as e:
    DUCKDB_AVAILABLE = False
    get_logger("api_config").warning(f"DuckDB not available, using in-memory mock data: {e}")

# Load environment variables from .env
# load_dotenv() # REMOVIDO para centralizar a lógica de config


class APIMode(str, Enum):
    """API operation modes."""
    MOCK = "mock"
    REAL = "real"


class APIConfig(BaseModel):
    """API mode configuration."""
    mode: APIMode = Field(default=APIMode.MOCK, description="Operation mode")
    rentcast_api_key: Optional[str] = Field(default=None, description="RentCast API key")
    use_real_api: bool = Field(default=False, description="Flag to use real API")


class RentCastAPI:
    """RentCast API client with fallback to mock data."""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.logger = get_logger("rentcast_api")
        self.base_url = "https://api.rentcast.io/v1"
        
        # Initialize DuckDB for Mock mode only
        self.property_db = None
        if self.config.mode == APIMode.MOCK and DUCKDB_AVAILABLE:
            try:
                self.property_db = PropertyDB("data/properties.duckdb")
                # Auto-migrate if database is empty
                if self.property_db.get_property_count() == 0:
                    self.logger.info("Empty database detected - running auto-migration...")
                    migrate_mock_to_duckdb("data/properties.duckdb")
                self.logger.info("DuckDB initialized for Mock mode")
            except Exception as e:
                self.logger.error(f"Failed to initialize DuckDB for Mock mode: {e}")
                self.property_db = None
        
    def search_properties(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search properties - real or mock mode.
        
        Args:
            criteria: Search criteria (location, bedrooms, max_rent, etc.)
            
        Returns:
            List of found properties
        """
        if self.config.mode == APIMode.REAL and self.config.use_real_api:
            return self._search_real_api(criteria)
        else:
            return self._search_mock_data(criteria)
    
    def _search_real_api(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search in the real RentCast API."""
        
        if not self.config.rentcast_api_key:
            self.logger.error("API key not configured for real mode")
            return self._search_mock_data(criteria)
        
        try:
            # Register API usage
            from app.utils.api_monitor import api_monitor
            if not api_monitor.can_use_rentcast():
                self.logger.warning("API limit reached - using mock data")
                return self._search_mock_data(criteria)
            
            # Make real API call
            headers = {
                "X-API-Key": self.config.rentcast_api_key,
                "accept": "application/json"
            }
            
            # Build parameters based on criteria
            params = {
                "city": criteria.get("city", "Miami"),
                "state": "FL",
                "propertyType": "Apartment",
                "status": "ForRent"
            }
            
            if criteria.get("bedrooms"):
                params["bedrooms"] = criteria["bedrooms"]
            if criteria.get("max_rent"):
                params["maxRent"] = criteria["max_rent"]
            
            self.logger.info(f"Making real call to RentCast API: {params}")
            
            response = requests.get(
                f"{self.base_url}/listings/rental/long-term",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                api_monitor.record_rentcast_call()
                
                # RentCast API returns a list directly (not a dict with 'listings')
                if isinstance(data, list):
                    self.logger.info(f"Real API returned {len(data)} properties")
                    return self._convert_api_response(data)
                else:
                    self.logger.warning(f"⚠️ Unexpected API structure: {type(data)}")
                    return self._search_mock_data(criteria)
            
            else:
                self.logger.error(f"Real API error: {response.status_code} - {response.text}")
                return self._search_mock_data(criteria)
                
        except Exception as e:
            self.logger.error(f"Error calling real API: {e}")
            return self._search_mock_data(criteria)
    
    def _search_mock_data(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return mock data with EXACT structure from real RentCast API."""
        
        # Try DuckDB first if available
        if self.property_db and DUCKDB_AVAILABLE:
            try:
                self.logger.info("Using DuckDB mock data (persistent storage)")
                properties = self.property_db.search_properties(criteria)
                self.logger.info(f"DuckDB returned {len(properties)} properties")
                return properties
            except Exception as e:
                self.logger.error(f"DuckDB search failed: {e}")
                self.logger.info("Falling back to in-memory mock data")
        
        # Fallback to in-memory mock data
        self.logger.info("Using in-memory mock data (fallback mode)")
        
        # MOCK DATA WITH REAL MIAMI PROPERTIES - EXACT RENTCAST API STRUCTURE
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
                    "name": "Marc Schomberg",
                    "phone": "3053053254",
                    "email": "marcschomberg@gmail.com",
                    "website": "http://londonfoster.com/agents/jean-marc-schomberg/"
                },
                "listingOffice": {
                    "name": "London Foster Realty",
                    "phone": "3055140100",
                    "email": "bobby@londonfoster.com"
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
                "id": "1300-S-Miami-Ave,-Unit-3408,-Miami,-FL-33130",
                "formattedAddress": "1300 S Miami Ave, Unit 3408, Miami, FL 33130",
                "addressLine1": "1300 S Miami Ave",
                "addressLine2": "Unit 3408",
                "city": "Miami",
                "state": "FL",
                "zipCode": "33130",
                "county": "Miami-Dade",
                "latitude": 25.7543,
                "longitude": -80.1876,
                "propertyType": "Apartment",
                "bedrooms": 1,
                "bathrooms": 1,
                "squareFootage": 649,
                "lotSize": 0,
                "yearBuilt": 2016,
                "status": "ForRent",
                "price": 4200,
                "listingType": "Standard",
                "listedDate": "2025-04-13T00:00:00.000Z",
                "removedDate": None,
                "createdDate": "2025-04-13T00:00:00.000Z",
                "lastSeenDate": "2025-06-23T05:02:02.468Z",
                "daysOnMarket": 71,
                "mlsName": "MLS",
                "mlsNumber": "A11776572",
                "listingAgent": {
                    "name": "Jonathan Tokatli",
                    "phone": "3059885650",
                    "email": "jtokatli@borluv.com",
                    "website": ""
                },
                "listingOffice": {
                    "name": "LoKation® Real Estate",
                    "phone": "9548591229",
                    "email": "lokation-r@inbound.opcity.com"
                },
                "history": {
                    "2025-04-13": {
                        "event": "Rental Listing",
                        "price": 4200,
                        "listingType": "Standard",
                        "listedDate": "2025-04-13T00:00:00.000Z",
                        "removedDate": None,
                        "daysOnMarket": 71
                    }
                }
            },
            {
                "id": "467-Nw-8th-St,-Apt-3,-Miami,-FL-33136",
                "formattedAddress": "467 Nw 8th St, Apt 3, Miami, FL 33136",
                "addressLine1": "467 Nw 8th St",
                "addressLine2": "Apt 3",
                "city": "Miami",
                "state": "FL",
                "zipCode": "33136",
                "county": "Miami-Dade",
                "latitude": 25.7832,
                "longitude": -80.2045,
                "propertyType": "Apartment",
                "bedrooms": 0,
                "bathrooms": 1,
                "squareFootage": 502,
                "lotSize": 0,
                "yearBuilt": 1950,
                "status": "ForRent",
                "price": 1450,
                "listingType": "Standard",
                "listedDate": "2025-04-13T00:00:00.000Z",
                "removedDate": None,
                "createdDate": "2025-04-13T00:00:00.000Z",
                "lastSeenDate": "2025-06-23T05:02:02.468Z",
                "daysOnMarket": 71,
                "mlsName": "MLS",
                "mlsNumber": "A11781101",
                "listingAgent": {
                    "name": "David Bartholomew",
                    "phone": "9548280111",
                    "email": "rent@floridarealtyco.net",
                    "website": "http://www.walnutstreetrealty.com"
                },
                "listingOffice": {
                    "name": "Walnut Street Realty Co",
                    "phone": "9548280110",
                    "email": "arthur@walnutstreetrealty.com"
                },
                "history": {
                    "2025-04-13": {
                        "event": "Rental Listing",
                        "price": 1450,
                        "listingType": "Standard",
                        "listedDate": "2025-04-13T00:00:00.000Z",
                        "removedDate": None,
                        "daysOnMarket": 71
                    }
                }
            },
            {
                "id": "3590-Coral-Way,-Apt-502,-Miami,-FL-33145",
                "formattedAddress": "3590 Coral Way, Apt 502, Miami, FL 33145",
                "addressLine1": "3590 Coral Way",
                "addressLine2": "Apt 502",
                "city": "Miami",
                "state": "FL",
                "zipCode": "33145",
                "county": "Miami-Dade",
                "latitude": 25.7456,
                "longitude": -80.2567,
                "propertyType": "Apartment",
                "bedrooms": 3,
                "bathrooms": 2,
                "squareFootage": 1168,
                "lotSize": 0,
                "yearBuilt": 2005,
                "status": "ForRent",
                "price": 3700,
                "listingType": "Standard",
                "listedDate": "2025-04-12T00:00:00.000Z",
                "removedDate": None,
                "createdDate": "2025-04-12T00:00:00.000Z",
                "lastSeenDate": "2025-06-23T05:02:02.468Z",
                "daysOnMarket": 72,
                "mlsName": "MLS",
                "mlsNumber": "A11783075",
                "listingAgent": {
                    "name": "Michael Huesca",
                    "phone": "7865977806",
                    "email": "huesca79c@yahoo.com",
                    "website": ""
                },
                "listingOffice": {
                    "name": "Lapeyre Realty Inc",
                    "phone": "3054084007",
                    "email": "ilapere@aol.com"
                },
                "history": {
                    "2025-04-12": {
                        "event": "Rental Listing",
                        "price": 3700,
                        "listingType": "Standard",
                        "listedDate": "2025-04-12T00:00:00.000Z",
                        "removedDate": None,
                        "daysOnMarket": 72
                    }
                }
            },
            {
                "id": "2000-Nw-29th-St,-Apt-3,-Miami,-FL-33142",
                "formattedAddress": "2000 Nw 29th St, Apt 3, Miami, FL 33142",
                "addressLine1": "2000 Nw 29th St",
                "addressLine2": "Apt 3",
                "city": "Miami",
                "state": "FL",
                "zipCode": "33142",
                "county": "Miami-Dade",
                "latitude": 25.8267,
                "longitude": -80.2373,
                "propertyType": "Apartment",
                "bedrooms": 2,
                "bathrooms": 1,
                "squareFootage": 1000,
                "lotSize": 0,
                "yearBuilt": 1969,
                "status": "ForRent",
                "price": 2100,
                "listingType": "Standard",
                "listedDate": "2025-04-14T00:00:00.000Z",
                "removedDate": None,
                "createdDate": "2025-04-14T00:00:00.000Z",
                "lastSeenDate": "2025-06-23T05:02:02.468Z",
                "daysOnMarket": 70,
                "mlsName": "MLS",
                "mlsNumber": "A11784223",
                "listingAgent": {
                    "name": "Giancarlo Espinosa",
                    "phone": "3056007836",
                    "email": "arc.giancarlo@gmail.com",
                    "website": "giancarlo.sites.salecore.com/"
                },
                "listingOffice": {
                    "name": "Virtual Realty Group FL Keys Inc",
                    "phone": "3056007836",
                    "email": "arc.giancarlo@gmail.com"
                },
                "history": {
                    "2025-04-14": {
                        "event": "Rental Listing",
                        "price": 2100,
                        "listingType": "Standard",
                        "listedDate": "2025-04-14T00:00:00.000Z",
                        "removedDate": None,
                        "daysOnMarket": 70
                    }
                }
            },
            {
                "id": "501-Sw-6th-Ct,-Apt-215,-Miami,-FL-33130",
                "formattedAddress": "501 Sw 6th Ct, Apt 215, Miami, FL 33130",
                "addressLine1": "501 Sw 6th Ct",
                "addressLine2": "Apt 215",
                "city": "Miami",
                "state": "FL",
                "zipCode": "33130",
                "county": "Miami-Dade",
                "latitude": 25.7701,
                "longitude": -80.1987,
                "propertyType": "Apartment",
                "bedrooms": 1,
                "bathrooms": 1,
                "squareFootage": 600,
                "lotSize": 0,
                "yearBuilt": 1925,
                "status": "ForRent",
                "price": 1600,
                "listingType": "Standard",
                "listedDate": "2025-04-14T00:00:00.000Z",
                "removedDate": None,
                "createdDate": "2025-04-14T00:00:00.000Z",
                "lastSeenDate": "2025-06-23T05:02:02.468Z",
                "daysOnMarket": 70,
                "mlsName": "MLS",
                "mlsNumber": "A11782286",
                "listingAgent": {
                    "name": "Luis Pena",
                    "phone": "9548170566",
                    "email": "luis.omar.pena.re@gmail.com",
                    "website": ""
                },
                "listingOffice": {
                    "name": "United Realty Group Inc.",
                    "phone": "9544502000",
                    "email": "broker@urgfl.com"
                },
                "history": {
                    "2025-04-14": {
                        "event": "Rental Listing",
                        "price": 1600,
                        "listingType": "Standard",
                        "listedDate": "2025-04-14T00:00:00.000Z",
                        "removedDate": None,
                        "daysOnMarket": 70
                    }
                }
            },
            {
                "id": "8205-Sw-39th-St,-Unit-2,-Miami,-FL-33155",
                "formattedAddress": "8205 Sw 39th St, Unit 2, Miami, FL 33155",
                "addressLine1": "8205 Sw 39th St",
                "addressLine2": "Unit 2",
                "city": "Miami",
                "state": "FL",
                "zipCode": "33155",
                "county": "Miami-Dade",
                "latitude": 25.7234,
                "longitude": -80.3456,
                "propertyType": "Apartment",
                "bedrooms": 2,
                "bathrooms": 1,
                "squareFootage": 3766,
                "lotSize": 0,
                "yearBuilt": 1958,
                "status": "ForRent",
                "price": 2500,
                "listingType": "Standard",
                "listedDate": "2025-04-15T00:00:00.000Z",
                "removedDate": None,
                "createdDate": "2025-04-15T00:00:00.000Z",
                "lastSeenDate": "2025-06-23T05:02:02.468Z",
                "daysOnMarket": 69,
                "mlsName": "MLS",
                "mlsNumber": "A11785067",
                "listingAgent": {
                    "name": "Taimi Uria",
                    "phone": "7864874759",
                    "email": "dbjdream@gmail.com",
                    "website": ""
                },
                "listingOffice": {
                    "name": "Tower Team Realty, Llc",
                    "phone": "9545487971",
                    "email": "edwin@towerteamrealty.com"
                },
                "history": {
                    "2025-04-15": {
                        "event": "Rental Listing",
                        "price": 2500,
                        "listingType": "Standard",
                        "listedDate": "2025-04-15T00:00:00.000Z",
                        "removedDate": None,
                        "daysOnMarket": 69
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
                "latitude": 25.7789,
                "longitude": -80.2987,
                "propertyType": "Apartment",
                "bedrooms": 2,
                "bathrooms": 1,
                "squareFootage": 21286,
                "lotSize": 0,
                "yearBuilt": 1965,
                "status": "ForRent",
                "price": 2300,
                "listingType": "Standard",
                "listedDate": "2025-04-15T00:00:00.000Z",
                "removedDate": None,
                "createdDate": "2025-04-15T00:00:00.000Z",
                "lastSeenDate": "2025-06-23T05:02:02.468Z",
                "daysOnMarket": 69,
                "mlsName": "MLS",
                "mlsNumber": "A11785052",
                "listingAgent": {
                    "name": "Perez Maynor",
                    "phone": "3055028517",
                    "email": "leads@positiverealty.us",
                    "website": "http://www.positiverealtyinc.com"
                },
                "listingOffice": {
                    "name": "Positive Realty",
                    "phone": "3057176766",
                    "email": "amunoz@positiverealty.us"
                },
                "history": {
                    "2025-04-15": {
                        "event": "Rental Listing",
                        "price": 2300,
                        "listingType": "Standard",
                        "listedDate": "2025-04-15T00:00:00.000Z",
                        "removedDate": None,
                        "daysOnMarket": 69
                    }
                }
            }
        ]
        
        # Apply comprehensive filtering
        filtered_properties = mock_rentcast_data
        
        # Filter by city
        city_filter = criteria.get("city")
        if city_filter:
            filtered_properties = [
                prop for prop in filtered_properties 
                if city_filter.lower() in prop["city"].lower()
            ]
        
        # Filter by state
        state_filter = criteria.get("state")
        if state_filter:
            filtered_properties = [
                prop for prop in filtered_properties 
                if state_filter.lower() in prop["state"].lower()
            ]
        
        # Filter by property type
        property_type_filter = criteria.get("property_type")
        if property_type_filter:
            filtered_properties = [
                prop for prop in filtered_properties 
                if property_type_filter.lower() == prop["propertyType"].lower()
            ]
        
        # Filter by minimum price
        min_price = criteria.get("min_price")
        if min_price:
            filtered_properties = [
                prop for prop in filtered_properties 
                if prop["price"] >= min_price
            ]
        
        # Filter by maximum price
        max_price = criteria.get("max_price")
        if max_price:
            filtered_properties = [
                prop for prop in filtered_properties 
                if prop["price"] <= max_price
            ]
        
        # Filter by minimum bedrooms
        min_bedrooms = criteria.get("min_bedrooms")
        if min_bedrooms:
            filtered_properties = [
                prop for prop in filtered_properties 
                if prop["bedrooms"] >= min_bedrooms
            ]
        
        # Filter by maximum bedrooms
        max_bedrooms = criteria.get("max_bedrooms")
        if max_bedrooms:
            filtered_properties = [
                prop for prop in filtered_properties 
                if prop["bedrooms"] <= max_bedrooms
            ]
        
        # Filter by minimum bathrooms
        min_bathrooms = criteria.get("min_bathrooms")
        if min_bathrooms:
            filtered_properties = [
                prop for prop in filtered_properties 
                if prop["bathrooms"] >= min_bathrooms
            ]
        
        # Filter by maximum bathrooms
        max_bathrooms = criteria.get("max_bathrooms")
        if max_bathrooms:
            filtered_properties = [
                prop for prop in filtered_properties 
                if prop["bathrooms"] <= max_bathrooms
            ]
        
        # Filter by minimum square footage
        min_square_footage = criteria.get("min_square_footage")
        if min_square_footage:
            filtered_properties = [
                prop for prop in filtered_properties 
                if prop["squareFootage"] >= min_square_footage
            ]
        
        # Filter by maximum square footage
        max_square_footage = criteria.get("max_square_footage")
        if max_square_footage:
            filtered_properties = [
                prop for prop in filtered_properties 
                if prop["squareFootage"] <= max_square_footage
            ]
        
        self.logger.info(f"Mock (RentCast structure) returned {len(filtered_properties)} properties (filtered from {len(mock_rentcast_data)})")
        return filtered_properties
    
    def _convert_api_response(self, listings: List[Dict]) -> List[Dict[str, Any]]:
        """Convert real API response to standardized format."""
        
        # From now on, both mock and real API use the SAME structure
        # No need to convert anymore - return directly
        self.logger.info(f"Returning {len(listings)} properties (RentCast structure)")
        return listings


# Global configuration instance
api_config = APIConfig(
    mode=APIMode.MOCK,  # Start in mock mode for safety
    rentcast_api_key=os.getenv("RENTCAST_API_KEY"),
    use_real_api=False
)

# Global API client
rentcast_client = RentCastAPI(api_config) 