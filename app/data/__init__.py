"""
Data layer for property and appointment management.

Supports both mock and real API implementations with transparent switching.
"""

from app.data.data_manager import DataManager, DataMode
from app.data.base_services import PropertyServiceProtocol, AppointmentServiceProtocol

__all__ = [
    "DataManager",
    "DataMode",
    "PropertyServiceProtocol",
    "AppointmentServiceProtocol",
]
