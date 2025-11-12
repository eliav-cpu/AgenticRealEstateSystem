"""
Data Layer Verification Script

Verifies that the data layer is correctly installed and configured.

Run with: python scripts/verify_data_layer.py
"""

import sys
import os
from pathlib import Path


def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a file exists."""
    path = Path(filepath)
    exists = path.exists()

    status = "✓" if exists else "✗"
    print(f"  {status} {description}")

    if not exists:
        print(f"      Missing: {filepath}")

    return exists


def check_directory_exists(dirpath: str, description: str) -> bool:
    """Check if a directory exists."""
    path = Path(dirpath)
    exists = path.exists() and path.is_dir()

    status = "✓" if exists else "✗"
    print(f"  {status} {description}")

    if not exists:
        print(f"      Missing: {dirpath}")

    return exists


def check_imports() -> bool:
    """Check if data layer modules can be imported."""
    print("\n2. Checking Python Imports:")

    try:
        from app.data import DataManager, DataMode
        print("  ✓ DataManager and DataMode")
    except ImportError as e:
        print(f"  ✗ DataManager import failed: {e}")
        return False

    try:
        from app.data.base_services import PropertyServiceProtocol, AppointmentServiceProtocol
        print("  ✓ Service protocols")
    except ImportError as e:
        print(f"  ✗ Service protocols import failed: {e}")
        return False

    try:
        from app.data.mock_system import MockPropertyService, MockAppointmentService
        print("  ✓ Mock services")
    except ImportError as e:
        print(f"  ✗ Mock services import failed: {e}")
        return False

    try:
        from app.data.real_api_system import RealPropertyService, RealAppointmentService
        print("  ✓ Real API services")
    except ImportError as e:
        print(f"  ✗ Real API services import failed: {e}")
        return False

    return True


def check_configuration() -> bool:
    """Check configuration files."""
    print("\n3. Checking Configuration:")

    try:
        from config.settings import get_settings
        settings = get_settings()
        print(f"  ✓ Settings loaded successfully")
        print(f"      Data mode: {settings.data_layer.mode}")
        print(f"      Mock data path: {settings.data_layer.mock_data_path}")
        return True
    except Exception as e:
        print(f"  ✗ Settings load failed: {e}")
        return False


async def test_basic_functionality() -> bool:
    """Test basic data layer functionality."""
    print("\n4. Testing Basic Functionality:")

    try:
        from app.data import DataManager, DataMode

        # Set to mock mode for testing
        DataManager.set_mode(DataMode.MOCK)
        print("  ✓ Mode switching works")

        # Test property service
        property_service = DataManager.get_property_service()
        properties = await property_service.search()
        print(f"  ✓ Property search works ({len(properties)} properties)")

        # Test getting specific property
        prop = await property_service.get_by_id("prop_001")
        if prop:
            print(f"  ✓ Get property by ID works")
        else:
            print(f"  ✗ Get property by ID failed")
            return False

        # Test appointment service
        from datetime import datetime, timedelta
        appointment_service = DataManager.get_appointment_service()

        start_time = datetime.now() + timedelta(days=1)
        appointment = await appointment_service.create_appointment(
            property_id="prop_001",
            user_email="test@example.com",
            start_time=start_time,
            duration_minutes=60
        )
        print(f"  ✓ Create appointment works")

        # Get available slots
        slots = await appointment_service.get_available_slots(
            property_id="prop_001",
            date=start_time,
            duration_minutes=60
        )
        print(f"  ✓ Get available slots works ({len(slots)} slots)")

        return True

    except Exception as e:
        print(f"  ✗ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_mock_data() -> bool:
    """Check mock data files."""
    print("\n5. Checking Mock Data:")

    import json

    # Check properties.json
    try:
        with open("app/data/fixtures/properties.json", "r") as f:
            properties = json.load(f)
            print(f"  ✓ properties.json loaded ({len(properties)} properties)")

            # Validate structure
            required_fields = ["id", "address", "city", "price", "bedrooms"]
            if all(all(field in prop for field in required_fields) for prop in properties):
                print(f"  ✓ Property data structure valid")
            else:
                print(f"  ✗ Property data structure invalid")
                return False

    except Exception as e:
        print(f"  ✗ properties.json error: {e}")
        return False

    # Check appointments.json
    try:
        with open("app/data/fixtures/appointments.json", "r") as f:
            appointments = json.load(f)
            print(f"  ✓ appointments.json loaded ({len(appointments)} appointments)")

            # Validate structure
            required_fields = ["id", "property_id", "user_email", "start_time"]
            if all(all(field in appt for field in required_fields) for appt in appointments):
                print(f"  ✓ Appointment data structure valid")
            else:
                print(f"  ✗ Appointment data structure invalid")
                return False

    except Exception as e:
        print(f"  ✗ appointments.json error: {e}")
        return False

    return True


def check_dependencies() -> bool:
    """Check required dependencies."""
    print("\n6. Checking Dependencies:")

    dependencies = [
        ("httpx", "HTTP client for real APIs"),
        ("tenacity", "Retry logic"),
        ("pydantic", "Configuration validation"),
    ]

    all_present = True
    for module_name, description in dependencies:
        try:
            __import__(module_name)
            print(f"  ✓ {module_name} - {description}")
        except ImportError:
            print(f"  ✗ {module_name} - {description} (not installed)")
            all_present = False

    if not all_present:
        print("\n  Install missing dependencies:")
        print("    pip install httpx tenacity pydantic pydantic-settings")

    return all_present


async def run_verification():
    """Run all verification checks."""
    print("=" * 70)
    print("DATA LAYER VERIFICATION")
    print("=" * 70)

    checks = []

    # 1. File structure
    print("\n1. Checking File Structure:")
    checks.append(check_file_exists(
        "app/data/__init__.py",
        "Module initialization"
    ))
    checks.append(check_file_exists(
        "app/data/base_services.py",
        "Service protocols"
    ))
    checks.append(check_file_exists(
        "app/data/mock_system.py",
        "Mock implementations"
    ))
    checks.append(check_file_exists(
        "app/data/real_api_system.py",
        "Real API implementations"
    ))
    checks.append(check_file_exists(
        "app/data/data_manager.py",
        "Data manager factory"
    ))
    checks.append(check_directory_exists(
        "app/data/fixtures",
        "Mock data fixtures directory"
    ))
    checks.append(check_file_exists(
        "app/data/fixtures/properties.json",
        "Properties fixture data"
    ))
    checks.append(check_file_exists(
        "app/data/fixtures/appointments.json",
        "Appointments fixture data"
    ))

    # 2. Import checks
    checks.append(check_imports())

    # 3. Configuration checks
    checks.append(check_configuration())

    # 4. Functionality checks
    checks.append(await test_basic_functionality())

    # 5. Mock data checks
    checks.append(check_mock_data())

    # 6. Dependency checks
    checks.append(check_dependencies())

    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    passed = sum(1 for check in checks if check)
    total = len(checks)
    percentage = (passed / total * 100) if total > 0 else 0

    print(f"\nPassed: {passed}/{total} checks ({percentage:.1f}%)")

    if passed == total:
        print("\n✓ All checks passed! Data layer is ready to use.")
        print("\nNext steps:")
        print("  1. Run demo: python examples/data_layer_demo.py")
        print("  2. Run tests: pytest tests/test_data_layer.py -v")
        print("  3. Read docs: docs/data_layer.md")
        return True
    else:
        print(f"\n✗ {total - passed} check(s) failed. Please fix the issues above.")
        return False


def main():
    """Main verification entry point."""
    import asyncio

    # Check if we're in the right directory
    if not Path("app").exists():
        print("Error: Must run from project root directory")
        print("Current directory:", os.getcwd())
        sys.exit(1)

    # Run verification
    try:
        result = asyncio.run(run_verification())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\nVerification failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
