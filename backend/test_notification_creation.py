"""
Test script to verify notification creation when a request is added
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from backend.models import db, Request, User
from backend.notifications import NotificationService
from datetime import datetime, timedelta

# Create Flask app context
app = create_app()

with app.app_context():
    print("=" * 60)
    print("Testing Notification Creation for New Request")
    print("=" * 60)
    
    # Get a receiver user (user_id=2 is typically a receiver)
    receiver = User.query.filter_by(user_id=2).first()
    if not receiver:
        print("❌ No receiver found (user_id=2)")
        sys.exit(1)
    
    print(f"\n✅ Found receiver: {receiver.name} (ID: {receiver.user_id})")
    print(f"   Location: ({receiver.location_lat}, {receiver.location_long})")
    
    # Check MongoDB connection
    from backend.mongodb import mongo_service
    if not mongo_service or not mongo_service.is_connected():
        print("\n❌ MongoDB not connected!")
        sys.exit(1)
    
    print("\n✅ MongoDB is connected")
    
    # Count current notifications
    current_notifs = mongo_service.get_all_notifications(receiver.user_id)
    print(f"\n📊 Current notifications for user {receiver.user_id}: {len(current_notifs)}")
    
    # Create a test request
    test_request = Request(
        receiver_id=receiver.user_id,
        food_type="Test Food Item",
        quantity=5,
        urgency_level="high",
        deadline=datetime.utcnow() + timedelta(days=3),
        status="pending"
    )
    
    db.session.add(test_request)
    db.session.commit()
    
    print(f"\n✅ Created test request (ID: {test_request.request_id})")
    
    # Trigger notification
    print("\n📨 Triggering notification service...")
    
    # Add debug logging to monitor notification creation
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    result = NotificationService.notify_new_request(test_request.request_id, receiver.user_id)
    
    if result:
        print("✅ Notification service returned success")
    else:
        print("⚠️ Notification service returned False (might be no nearby donors or missing location)")
    
    # Force a db session commit to ensure notifications are visible
    db.session.commit()
    
    # Check SQL notifications table
    from backend.models import Notification
    sql_notifs = Notification.query.filter_by(user_id=receiver.user_id).all()
    print(f"\n📊 SQL Notifications for user {receiver.user_id}: {len(sql_notifs)}")
    if sql_notifs:
        for notif in sql_notifs[:3]:
            print(f"   - {notif.title}: {notif.message}")
    
    # Check if notifications were created
    new_notifs = mongo_service.get_all_notifications(receiver.user_id)
    print(f"\n📊 Notifications after creation: {len(new_notifs)}")
    print(f"   New notifications created: {len(new_notifs) - len(current_notifs)}")
    
    # Show sample notification if any
    if new_notifs:
        latest = new_notifs[0]
        print(f"\n📬 Latest notification:")
        print(f"   Title: {latest.get('title')}")
        print(f"   Message: {latest.get('message')}")
        print(f"   Type: {latest.get('type')}")
        print(f"   Status: {latest.get('status')}")
    
    # Find nearby donors to see why notifications might not be created
    from backend.services.geo_service import GeoService
    if receiver.location_lat and receiver.location_long:
        nearby_donors = GeoService.find_nearby_users(
            receiver.location_lat,
            receiver.location_long,
            radius_km=20,
            user_type="donor"
        )
        print(f"\n🗺️ Found {len(nearby_donors)} nearby donors within 20km radius")
        if nearby_donors:
            for donor in nearby_donors[:3]:
                print(f"   - Donor {donor['user_id']}: {donor['name']} ({donor['distance_km']:.2f} km)")
    else:
        print("\n⚠️ Receiver has no location set!")
    
    # Clean up test request
    db.session.delete(test_request)
    db.session.commit()
    print(f"\n🧹 Cleaned up test request")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
