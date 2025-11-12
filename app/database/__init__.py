"""
Database module for Agentic Real Estate System

This module provides DuckDB-based storage for mock property data.
Only used in Mock mode - Real API mode continues using in-memory storage.
"""

from .schema import create_property_schema, PropertyDB
from .migration import migrate_mock_to_duckdb

__all__ = [
    "create_property_schema",
    "PropertyDB", 
    "migrate_mock_to_duckdb"
]