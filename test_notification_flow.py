#!/usr/bin/env python
"""Test notification flow"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

# Test MongoDB connection
print("=" * 50)
print("TESTING MONGODB CONNECTION")
print("=" * 50)

try:
    from backend.mongodb import mongo_service
    print(f"mongo_service type: {type(mongo_service)}")
    print(f"mongo_service: {mongo_service}")
    
    if mongo_service:
        print(f"mongo_service.connected: {mongo_service.connected}")
        print(f"mongo_service.is_connected(): {mongo_service.is_connected()}")
        print(f"mongo_service.db: {mongo_service.db}")
        
        if mongo_service.is_connected():
            print("✅ MongoDB is connected!")
            
            # Test store_notification
            print("\n" + "=" * 50)
            print("TESTING STORE_NOTIFICATION")
            print("=" * 50)
            
            test_notification = {
                "type": "transaction_created",
                "title": "Test Transaction",
                "message": "This is a test",
                "status": "unread"
            }
            
            result = mongo_service.store_notification(123, test_notification)
            print(f"Store result: {result}")
            
            # Test retrieve
            print("\n" + "=" * 50)
            print("TESTING GET_UNREAD_NOTIFICATIONS")
            print("=" * 50)
            
            notifs = mongo_service.get_unread_notifications(123)
            print(f"Unread notifications: {notifs}")
            
        else:
            print("❌ MongoDB is not connected!")
    else:
        print("❌ mongo_service is None!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
