"""
DuckDB Schema for Mock Property Data

Defines the database schema that matches the exact RentCast API structure.
Only used in Mock mode - Real API mode continues using in-memory storage.
"""

import duckdb
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from app.utils.logging import get_logger

logger = get_logger("property_db")


def create_property_schema(conn: duckdb.DuckDBPyConnection) -> None:
    """
    Create the properties table with exact RentCast API structure.
    
    Args:
        conn: DuckDB connection object
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            -- Primary identification
            id VARCHAR PRIMARY KEY,
            formatted_address VARCHAR,
            address_line1 VARCHAR,
            address_line2 VARCHAR,
            city VARCHAR,
            state VARCHAR,
            zip_code VARCHAR,
            county VARCHAR,
            
            -- Location coordinates
            latitude DOUBLE,
            longitude DOUBLE,
            
            -- Property details
            property_type VARCHAR,
            bedrooms INTEGER,
            bathrooms INTEGER,
            square_footage INTEGER,
            lot_size INTEGER,
            year_built INTEGER,
            
            -- Listing information
            status VARCHAR,
            price INTEGER,
            listing_type VARCHAR,
            listed_date TIMESTAMP,
            removed_date TIMESTAMP,
            created_date TIMESTAMP,
            last_seen_date TIMESTAMP,
            days_on_market INTEGER,
            
            -- MLS information
            mls_name VARCHAR,
            mls_number VARCHAR,
            
            -- Agent and office (stored as JSON)
            listing_agent JSON,
            listing_office JSON,
            
            -- Price history (stored as JSON)
            history JSON,
            
            -- Metadata
            inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for common search patterns
    conn.execute("CREATE INDEX IF NOT EXISTS idx_city ON properties(city)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_bedrooms ON properties(bedrooms)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_price ON properties(price)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_property_type ON properties(property_type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON properties(status)")
    
    logger.info("Properties table and indexes created successfully")


class PropertyDB:
    """
    DuckDB-based property storage for Mock mode only.
    Provides CRUD operations matching the RentCast API structure.

    Uses read-only mode by default to allow multiple concurrent readers
    when Uvicorn runs with --reload. Write operations temporarily use
    a writable connection.
    """

    def __init__(self, db_path: str = "data/properties.duckdb", read_only: bool = True):
        """
        Initialize PropertyDB connection.

        Args:
            db_path: Path to DuckDB database file
            read_only: If True, opens in read-only mode (allows multiple concurrent readers).
                      Set to False for write operations or migrations.
        """
        self.db_path = db_path
        self.read_only = read_only

        try:
            # Ensure data directory exists
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)

            # Normalize path and ensure it's ASCII-safe
            normalized_path = os.path.abspath(db_path).replace('\\', '/')
            self.db_path = normalized_path

            # If read-only mode, the database must already exist
            if read_only and not os.path.exists(normalized_path):
                logger.warning(f"Database does not exist at {normalized_path}, creating it first")
                # Temporarily create database in write mode
                temp_conn = duckdb.connect(normalized_path)
                create_property_schema(temp_conn)
                temp_conn.close()

            # Connect to DuckDB with read-only mode if specified
            self.conn = duckdb.connect(normalized_path, read_only=read_only)

            # Create schema only if not in read-only mode
            if not read_only:
                create_property_schema(self.conn)

            mode_str = "read-only" if read_only else "read-write"
            logger.info(f"PropertyDB initialized at {normalized_path} ({mode_str} mode)")

        except UnicodeDecodeError as e:
            logger.error(f"Unicode encoding error in database path: {e}")
            logger.info("Attempting to create database with fallback path...")

            # Try with a simpler path
            fallback_path = "properties.duckdb"

            # Handle read-only mode for fallback path
            if read_only and not os.path.exists(fallback_path):
                temp_conn = duckdb.connect(fallback_path)
                create_property_schema(temp_conn)
                temp_conn.close()

            self.conn = duckdb.connect(fallback_path, read_only=read_only)
            if not read_only:
                create_property_schema(self.conn)
            self.db_path = fallback_path

            mode_str = "read-only" if read_only else "read-write"
            logger.info(f"PropertyDB initialized with fallback path: {fallback_path} ({mode_str} mode)")

        except Exception as e:
            logger.error(f"Failed to initialize PropertyDB: {e}")
            raise

    def _get_write_connection(self):
        """
        Get a temporary write connection for write operations.
        This allows read-only instances to perform write operations when needed.

        Returns:
            A writable DuckDB connection (must be closed after use)
        """
        return duckdb.connect(self.db_path, read_only=False)
    
    def insert_property(self, property_data: Dict[str, Any]) -> bool:
        """
        Insert a single property into the database.
        Uses a temporary write connection to avoid lock conflicts.

        Args:
            property_data: Property data in RentCast API format

        Returns:
            True if successful, False otherwise
        """
        write_conn = None
        try:
            # Extract fields from RentCast API structure
            params = [
                property_data.get("id"),
                property_data.get("formattedAddress"),
                property_data.get("addressLine1"),
                property_data.get("addressLine2"),
                property_data.get("city"),
                property_data.get("state"),
                property_data.get("zipCode"),
                property_data.get("county"),
                property_data.get("latitude"),
                property_data.get("longitude"),
                property_data.get("propertyType"),
                property_data.get("bedrooms"),
                property_data.get("bathrooms"),
                property_data.get("squareFootage"),
                property_data.get("lotSize"),
                property_data.get("yearBuilt"),
                property_data.get("status"),
                property_data.get("price"),
                property_data.get("listingType"),
                property_data.get("listedDate"),
                property_data.get("removedDate"),
                property_data.get("createdDate"),
                property_data.get("lastSeenDate"),
                property_data.get("daysOnMarket"),
                property_data.get("mlsName"),
                property_data.get("mlsNumber"),
                json.dumps(property_data.get("listingAgent", {})),
                json.dumps(property_data.get("listingOffice", {})),
                json.dumps(property_data.get("history", {}))
            ]

            # Use write connection for insert operation
            write_conn = self._get_write_connection()
            write_conn.execute("""
                INSERT OR REPLACE INTO properties (
                    id, formatted_address, address_line1, address_line2, city, state,
                    zip_code, county, latitude, longitude, property_type, bedrooms,
                    bathrooms, square_footage, lot_size, year_built, status, price,
                    listing_type, listed_date, removed_date, created_date, last_seen_date,
                    days_on_market, mls_name, mls_number, listing_agent, listing_office, history
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, params)

            return True

        except Exception as e:
            logger.error(f"Error inserting property {property_data.get('id', 'unknown')}: {e}")
            return False
        finally:
            if write_conn:
                write_conn.close()
    
    def search_properties(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search properties with filtering criteria.
        
        Args:
            criteria: Search criteria (city, bedrooms, max_rent, etc.)
            
        Returns:
            List of properties in RentCast API format
        """
        try:
            # Build dynamic query based on criteria
            query = "SELECT * FROM properties WHERE 1=1"
            params = []
            
            # City filter
            if criteria.get("city"):
                query += " AND city ILIKE ?"
                params.append(f"%{criteria['city']}%")
            
            # Bedrooms filter
            if criteria.get("bedrooms"):
                if isinstance(criteria["bedrooms"], dict):
                    if criteria["bedrooms"].get("min"):
                        query += " AND bedrooms >= ?"
                        params.append(criteria["bedrooms"]["min"])
                    if criteria["bedrooms"].get("max"):
                        query += " AND bedrooms <= ?"
                        params.append(criteria["bedrooms"]["max"])
                else:
                    query += " AND bedrooms = ?"
                    params.append(criteria["bedrooms"])
            
            # Price filters
            if criteria.get("max_rent") or criteria.get("max_price"):
                max_price = criteria.get("max_rent") or criteria.get("max_price")
                query += " AND price <= ?"
                params.append(max_price)
            
            if criteria.get("min_rent") or criteria.get("min_price"):
                min_price = criteria.get("min_rent") or criteria.get("min_price")
                query += " AND price >= ?"
                params.append(min_price)
            
            # Property type filter
            if criteria.get("property_type"):
                query += " AND property_type ILIKE ?"
                params.append(f"%{criteria['property_type']}%")
            
            # Status filter (default to ForRent)
            status = criteria.get("status", "ForRent")
            query += " AND status = ?"
            params.append(status)
            
            # Bathrooms filter
            if criteria.get("bathrooms"):
                query += " AND bathrooms >= ?"
                params.append(criteria["bathrooms"])
            
            # Order by price ascending
            query += " ORDER BY price ASC"
            
            # Execute query
            result = self.conn.execute(query, params).fetchall()
            columns = [desc[0] for desc in self.conn.description]
            
            # Convert to RentCast API format
            properties = []
            for row in result:
                prop = dict(zip(columns, row))
                
                # Convert back to RentCast API format
                api_property = {
                    "id": prop["id"],
                    "formattedAddress": prop["formatted_address"],
                    "addressLine1": prop["address_line1"],
                    "addressLine2": prop["address_line2"],
                    "city": prop["city"],
                    "state": prop["state"],
                    "zipCode": prop["zip_code"],
                    "county": prop["county"],
                    "latitude": prop["latitude"],
                    "longitude": prop["longitude"],
                    "propertyType": prop["property_type"],
                    "bedrooms": prop["bedrooms"],
                    "bathrooms": prop["bathrooms"],  
                    "squareFootage": prop["square_footage"],
                    "lotSize": prop["lot_size"],
                    "yearBuilt": prop["year_built"],
                    "status": prop["status"],
                    "price": prop["price"],
                    "listingType": prop["listing_type"],
                    "listedDate": prop["listed_date"],
                    "removedDate": prop["removed_date"],
                    "createdDate": prop["created_date"],
                    "lastSeenDate": prop["last_seen_date"],
                    "daysOnMarket": prop["days_on_market"],
                    "mlsName": prop["mls_name"],
                    "mlsNumber": prop["mls_number"],
                    "listingAgent": json.loads(prop["listing_agent"]) if prop["listing_agent"] else {},
                    "listingOffice": json.loads(prop["listing_office"]) if prop["listing_office"] else {},
                    "history": json.loads(prop["history"]) if prop["history"] else {}
                }
                
                properties.append(api_property)
            
            logger.info(f"Found {len(properties)} properties matching criteria")
            return properties
            
        except Exception as e:
            logger.error(f"Error searching properties: {e}")
            return []
    
    def get_property_by_id(self, property_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific property by ID.
        
        Args:
            property_id: Property ID
            
        Returns:
            Property data in RentCast API format, or None if not found
        """
        try:
            result = self.conn.execute(
                "SELECT * FROM properties WHERE id = ?", 
                [property_id]
            ).fetchone()
            
            if not result:
                return None
            
            columns = [desc[0] for desc in self.conn.description]
            prop = dict(zip(columns, result))
            
            # Convert to RentCast API format
            return {
                "id": prop["id"],
                "formattedAddress": prop["formatted_address"],
                "addressLine1": prop["address_line1"],
                "addressLine2": prop["address_line2"],
                "city": prop["city"],
                "state": prop["state"],
                "zipCode": prop["zip_code"],
                "county": prop["county"],
                "latitude": prop["latitude"],
                "longitude": prop["longitude"],
                "propertyType": prop["property_type"],
                "bedrooms": prop["bedrooms"],
                "bathrooms": prop["bathrooms"],
                "squareFootage": prop["square_footage"],
                "lotSize": prop["lot_size"],
                "yearBuilt": prop["year_built"],
                "status": prop["status"],
                "price": prop["price"],
                "listingType": prop["listing_type"],
                "listedDate": prop["listed_date"],
                "removedDate": prop["removed_date"],
                "createdDate": prop["created_date"],
                "lastSeenDate": prop["last_seen_date"],
                "daysOnMarket": prop["days_on_market"],
                "mlsName": prop["mls_name"],
                "mlsNumber": prop["mls_number"],
                "listingAgent": json.loads(prop["listing_agent"]) if prop["listing_agent"] else {},
                "listingOffice": json.loads(prop["listing_office"]) if prop["listing_office"] else {},
                "history": json.loads(prop["history"]) if prop["history"] else {}
            }
            
        except Exception as e:
            logger.error(f"Error getting property {property_id}: {e}")
            return None
    
    def get_property_count(self) -> int:
        """Get total number of properties in database."""
        try:
            result = self.conn.execute("SELECT COUNT(*) FROM properties").fetchone()
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting property count: {e}")
            return 0
    
    def clear_all_properties(self) -> bool:
        """
        Clear all properties from database.
        Uses a temporary write connection to avoid lock conflicts.
        """
        write_conn = None
        try:
            write_conn = self._get_write_connection()
            write_conn.execute("DELETE FROM properties")
            logger.info("All properties cleared from database")
            return True
        except Exception as e:
            logger.error(f"Error clearing properties: {e}")
            return False
        finally:
            if write_conn:
                write_conn.close()
    
    def close(self) -> None:
        """Close database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()
            logger.info("Database connection closed")