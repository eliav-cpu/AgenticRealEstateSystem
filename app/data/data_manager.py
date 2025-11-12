"""
Data manager for transparent switching between mock and real data sources.

Uses factory pattern to provide the correct service implementation based on
configuration settings.
"""

import os
from enum import Enum
from typing import Union
from app.data.base_services import PropertyServiceProtocol, AppointmentServiceProtocol
from app.data.mock_system import MockPropertyService, MockAppointmentService
from app.data.real_api_system import RealPropertyService, RealAppointmentService


class DataMode(str, Enum):
    """Data source mode."""
    MOCK = "mock"
    REAL = "real"


class DataManager:
    """
    Factory for creating data services based on configuration.

    Provides transparent switching between mock and real implementations.
    """

    _property_service: Union[PropertyServiceProtocol, None] = None
    _appointment_service: Union[AppointmentServiceProtocol, None] = None
    _current_mode: Union[DataMode, None] = None

    @classmethod
    def _get_mode(cls) -> DataMode:
        """Get data mode from environment or settings."""
        mode_str = os.getenv("DATA_MODE", "mock").lower()

        try:
            return DataMode(mode_str)
        except ValueError:
            print(f"Invalid DATA_MODE '{mode_str}', defaulting to MOCK")
            return DataMode.MOCK

    @classmethod
    def get_property_service(cls) -> PropertyServiceProtocol:
        """
        Get property service instance.

        Returns mock or real implementation based on DATA_MODE setting.
        Singleton pattern - returns same instance for consistency.
        """
        current_mode = cls._get_mode()

        # Create new service if mode changed or service doesn't exist
        if cls._property_service is None or cls._current_mode != current_mode:
            cls._current_mode = current_mode

            if current_mode == DataMode.MOCK:
                print("Using MOCK property service")
                cls._property_service = MockPropertyService()
            else:
                print("Using REAL property service (RentCast API)")
                try:
                    cls._property_service = RealPropertyService()
                except ValueError as e:
                    print(f"Error initializing real service: {e}")
                    print("Falling back to MOCK property service")
                    cls._property_service = MockPropertyService()

        return cls._property_service

    @classmethod
    def get_appointment_service(cls) -> AppointmentServiceProtocol:
        """
        Get appointment service instance.

        Returns mock or real implementation based on DATA_MODE setting.
        Singleton pattern - returns same instance for consistency.
        """
        current_mode = cls._get_mode()

        # Create new service if mode changed or service doesn't exist
        if cls._appointment_service is None or cls._current_mode != current_mode:
            cls._current_mode = current_mode

            if current_mode == DataMode.MOCK:
                print("Using MOCK appointment service")
                cls._appointment_service = MockAppointmentService()
            else:
                print("Using REAL appointment service (Google Calendar)")
                try:
                    cls._appointment_service = RealAppointmentService()
                except ValueError as e:
                    print(f"Error initializing real service: {e}")
                    print("Falling back to MOCK appointment service")
                    cls._appointment_service = MockAppointmentService()

        return cls._appointment_service

    @classmethod
    def reset_services(cls):
        """
        Reset service instances.

        Useful for testing or when switching modes dynamically.
        """
        cls._property_service = None
        cls._appointment_service = None
        cls._current_mode = None

    @classmethod
    def get_current_mode(cls) -> DataMode:
        """Get the current data mode."""
        return cls._get_mode()

    @classmethod
    def set_mode(cls, mode: DataMode):
        """
        Set data mode programmatically.

        This updates the environment variable and resets services.
        """
        os.environ["DATA_MODE"] = mode.value
        cls.reset_services()
