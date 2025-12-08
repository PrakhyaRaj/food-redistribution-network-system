from backend import socketio
from backend.mongodb import mongo_service
from datetime import datetime

class NotificationService:
    @staticmethod
    def send_and_store(user_id, notification_data):
        """
        Send real-time notification AND store in MongoDB
        Returns True if successful
        """
        try:
            # 1. Send real-time via Socket.IO
            socketio.emit("notification", notification_data, room=f"user_{user_id}")
            
            # 2. Store in MongoDB for persistence
            if mongo_service and mongo_service.is_connected():
                mongo_service.store_notification(user_id, notification_data)
                print(f"📨 Notification sent & stored for user {user_id}")
            else:
                print(f"📨 Notification sent (MongoDB not available for storage)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error in notification: {str(e)}")
            return False
    
    @staticmethod
    def get_user_notifications(user_id, unread_only=True, limit=50):
        """Get notifications for a user from MongoDB"""
        if not mongo_service or not mongo_service.is_connected():
            return []
            
        if unread_only:
            notifications = mongo_service.get_unread_notifications(user_id, limit)
        else:
            notifications = mongo_service.get_all_notifications(user_id, limit)
        
        # Convert ObjectId to string for JSON serialization
        for notification in notifications:
            if '_id' in notification:
                notification["_id"] = str(notification["_id"])
            
        return notifications