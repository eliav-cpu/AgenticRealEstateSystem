"""
Data Layer Demo - Demonstrates mock and real data usage.

Run with:
    python examples/data_layer_demo.py
"""

import asyncio
import os
from datetime import datetime, timedelta
from app.data import DataManager, DataMode


async def demo_property_search():
    """Demonstrate property search capabilities."""
    print("\n" + "="*60)
    print("PROPERTY SEARCH DEMO")
    print("="*60)

    service = DataManager.get_property_service()

    # 1. Search all properties
    print("\n1. All Properties:")
    all_properties = await service.search()
    print(f"   Found {len(all_properties)} properties")

    # 2. Search by location
    print("\n2. San Francisco Properties:")
    sf_properties = await service.search(location="San Francisco")
    for prop in sf_properties:
        print(f"   - {prop['address']}: ${prop['price']}/mo, "
              f"{prop['bedrooms']}BR/{prop['bathrooms']}BA")

    # 3. Search by price range
    print("\n3. Properties $2500-$3500/month:")
    mid_range = await service.search(min_price=2500, max_price=3500)
    for prop in mid_range:
        print(f"   - {prop['city']}, {prop['address']}: ${prop['price']}/mo")

    # 4. Search by bedrooms
    print("\n4. 3+ Bedroom Properties:")
    large_properties = await service.search(bedrooms=3)
    for prop in large_properties:
        print(f"   - {prop['address']}, {prop['city']}: "
              f"{prop['bedrooms']}BR, {prop['square_feet']} sqft")

    # 5. Complex search
    print("\n5. San Francisco, 2BR+, Under $4000:")
    filtered = await service.search(
        location="San Francisco",
        bedrooms=2,
        max_price=4000
    )
    for prop in filtered:
        print(f"   - {prop['address']}: ${prop['price']}/mo, "
              f"{prop['bedrooms']}BR")

    # 6. Property details
    print("\n6. Property Details for prop_001:")
    details = await service.get_details("prop_001")
    if details:
        print(f"   Address: {details['address']}")
        print(f"   Price: ${details['price']}/mo")
        print(f"   Type: {details['property_type']}")
        print(f"   Amenities: {', '.join(details['amenities'])}")
        print(f"   Pet Policy: {details['pet_policy']}")

    # 7. Nearby properties
    print("\n7. Properties near San Francisco (37.7749, -122.4194):")
    nearby = await service.get_nearby(
        latitude=37.7749,
        longitude=-122.4194,
        radius_miles=15.0,
        limit=5
    )
    for prop in nearby:
        print(f"   - {prop['city']}: {prop['address']} "
              f"({prop['distance_miles']} miles away)")


async def demo_appointment_management():
    """Demonstrate appointment management capabilities."""
    print("\n" + "="*60)
    print("APPOINTMENT MANAGEMENT DEMO")
    print("="*60)

    service = DataManager.get_appointment_service()

    # 1. Get existing appointments
    print("\n1. Existing Appointments:")
    appointments = await service.get_appointments()
    print(f"   Total: {len(appointments)} appointments")
    for appt in appointments[:3]:  # Show first 3
        print(f"   - {appt['id']}: Property {appt['property_id']} "
              f"at {appt['start_time'][:16]}")

    # 2. Create new appointment
    print("\n2. Creating New Appointment:")
    tomorrow = datetime.now() + timedelta(days=1)
    viewing_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)

    new_appointment = await service.create_appointment(
        property_id="prop_001",
        user_email="demo@example.com",
        start_time=viewing_time,
        duration_minutes=60,
        notes="Demo viewing - interested in parking availability"
    )

    print(f"   Created: {new_appointment['id']}")
    print(f"   Property: {new_appointment['property_id']}")
    print(f"   Time: {new_appointment['start_time']}")
    print(f"   Duration: {new_appointment['duration_minutes']} minutes")

    # 3. Get appointments for user
    print("\n3. Appointments for demo@example.com:")
    user_appointments = await service.get_appointments(
        user_email="demo@example.com"
    )
    print(f"   Found {len(user_appointments)} appointment(s)")

    # 4. Get available slots
    print("\n4. Available Slots for prop_001 tomorrow:")
    slots = await service.get_available_slots(
        property_id="prop_001",
        date=tomorrow,
        duration_minutes=60
    )

    print(f"   {len(slots)} available time slots:")
    for slot in slots[:5]:  # Show first 5
        print(f"   - {slot.strftime('%I:%M %p')}")

    # 5. Get specific appointment
    print("\n5. Appointment Details:")
    if appointments:
        first_appt_id = appointments[0]["id"]
        appt = await service.get_appointment(first_appt_id)
        if appt:
            print(f"   ID: {appt['id']}")
            print(f"   Property: {appt['property_id']}")
            print(f"   User: {appt['user_email']}")
            print(f"   Status: {appt['status']}")
            print(f"   Notes: {appt['notes']}")

    # 6. Cancel appointment (demo only)
    print("\n6. Cancelling Demo Appointment:")
    cancelled = await service.cancel_appointment(new_appointment['id'])
    if cancelled:
        print(f"   Successfully cancelled {new_appointment['id']}")
        # Verify cancellation
        cancelled_appt = await service.get_appointment(new_appointment['id'])
        print(f"   Status: {cancelled_appt['status']}")


async def demo_mode_switching():
    """Demonstrate switching between mock and real modes."""
    print("\n" + "="*60)
    print("MODE SWITCHING DEMO")
    print("="*60)

    # 1. Check current mode
    current_mode = DataManager.get_current_mode()
    print(f"\n1. Current Mode: {current_mode.value}")

    # 2. Force mock mode
    print("\n2. Switching to MOCK mode:")
    DataManager.set_mode(DataMode.MOCK)
    print(f"   Mode: {DataManager.get_current_mode().value}")

    mock_service = DataManager.get_property_service()
    mock_results = await mock_service.search(location="San Francisco")
    print(f"   Mock results: {len(mock_results)} properties")

    # 3. Try real mode (will fallback if no API key)
    print("\n3. Attempting REAL mode:")
    DataManager.set_mode(DataMode.REAL)
    print(f"   Mode: {DataManager.get_current_mode().value}")

    real_service = DataManager.get_property_service()
    try:
        real_results = await real_service.search(location="San Francisco")
        print(f"   Real API results: {len(real_results)} properties")
    except Exception as e:
        print(f"   Note: Real API unavailable (expected in demo): {type(e).__name__}")
        print("   System automatically fell back to mock data")

    # Reset to mock for rest of demo
    DataManager.set_mode(DataMode.MOCK)


async def demo_integration_workflow():
    """Demonstrate a complete property search and booking workflow."""
    print("\n" + "="*60)
    print("INTEGRATION WORKFLOW DEMO")
    print("="*60)

    property_service = DataManager.get_property_service()
    appointment_service = DataManager.get_appointment_service()

    # 1. User searches for properties
    print("\n1. User Search: 2BR apartments in San Francisco under $4000")
    search_results = await property_service.search(
        location="San Francisco",
        bedrooms=2,
        max_price=4000,
        property_type="apartment"
    )

    print(f"   Found {len(search_results)} matching properties")

    if not search_results:
        print("   No properties found matching criteria")
        return

    # 2. User views property details
    print("\n2. Viewing Details for First Result:")
    selected_property = search_results[0]
    details = await property_service.get_details(selected_property["id"])

    print(f"   Property: {details['address']}")
    print(f"   Price: ${details['price']}/month")
    print(f"   Size: {details['square_feet']} sqft")
    print(f"   Bedrooms: {details['bedrooms']}")
    print(f"   Bathrooms: {details['bathrooms']}")
    print(f"   Amenities: {', '.join(details['amenities'][:3])}")

    # 3. User checks availability
    print("\n3. Checking Availability:")
    tomorrow = datetime.now() + timedelta(days=1)
    available_slots = await appointment_service.get_available_slots(
        property_id=selected_property["id"],
        date=tomorrow,
        duration_minutes=60
    )

    print(f"   {len(available_slots)} available slots tomorrow:")
    for slot in available_slots[:3]:
        print(f"   - {slot.strftime('%I:%M %p')}")

    # 4. User books appointment
    if available_slots:
        print("\n4. Booking Appointment:")
        chosen_slot = available_slots[0]

        appointment = await appointment_service.create_appointment(
            property_id=selected_property["id"],
            user_email="prospective.tenant@example.com",
            start_time=chosen_slot,
            duration_minutes=60,
            notes=f"Interested in {details['address']}. "
                  f"Questions about parking and lease terms."
        )

        print(f"   Appointment Created: {appointment['id']}")
        print(f"   Property: {details['address']}")
        print(f"   Time: {appointment['start_time']}")
        print(f"   Confirmation sent to: {appointment['user_email']}")

        # 5. User views their appointments
        print("\n5. User's Appointments:")
        user_appointments = await appointment_service.get_appointments(
            user_email="prospective.tenant@example.com"
        )

        print(f"   Total upcoming appointments: {len(user_appointments)}")
        for appt in user_appointments:
            prop = await property_service.get_by_id(appt["property_id"])
            if prop:
                print(f"   - {prop['address']} on {appt['start_time'][:16]}")


async def main():
    """Run all demos."""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*15 + "DATA LAYER DEMO" + " "*28 + "║")
    print("╚" + "="*58 + "╝")

    # Show current configuration
    mode = DataManager.get_current_mode()
    print(f"\nRunning in {mode.value.upper()} mode")
    print(f"Environment: DATA_MODE={os.getenv('DATA_MODE', 'mock')}")

    # Run demos
    await demo_mode_switching()
    await demo_property_search()
    await demo_appointment_management()
    await demo_integration_workflow()

    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\nTo use real APIs:")
    print("  1. Set environment variables:")
    print("     export DATA_MODE=real")
    print("     export RENTCAST_API_KEY=your_key")
    print("     export GOOGLE_CALENDAR_CREDENTIALS=/path/to/creds.json")
    print("  2. Run demo again")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
