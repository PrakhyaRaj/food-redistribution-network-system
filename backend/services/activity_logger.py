from backend.mongodb import mongo_service
from flask import request

class ActivityLogger:
    @staticmethod
    def log_login(user_id):
        """Log user login"""
        mongo_service.log_activity(
            user_id=user_id,
            activity_type="login",
            details={"method": "password"},
            ip_address=request.remote_addr
        )
    
    @staticmethod
    def log_food_posted(user_id, food_id, food_name):
        """Log food posting"""
        mongo_service.log_activity(
            user_id=user_id,
            activity_type="food_posted",
            details={"food_id": food_id, "food_name": food_name}
        )
    
    @staticmethod
    def log_request_made(user_id, request_id, food_type):
        """Log food request"""
        mongo_service.log_activity(
            user_id=user_id,
            activity_type="request_made",
            details={"request_id": request_id, "food_type": food_type}
        )
    
    @staticmethod
    def log_food_matched(donor_id, receiver_id, food_id, request_id):
        """Log food matching"""
        mongo_service.log_activity(
            user_id=donor_id,
            activity_type="food_matched",
            details={
                "role": "donor",
                "receiver_id": receiver_id,
                "food_id": food_id,
                "request_id": request_id
            }
        )
        
        mongo_service.log_activity(
            user_id=receiver_id,
            activity_type="food_matched",
            details={
                "role": "receiver", 
                "donor_id": donor_id,
                "food_id": food_id,
                "request_id": request_id
            }
        )
    
    @staticmethod
    def get_user_activities(user_id, limit=50):
        """Get recent activities for a user"""
        from backend.mongodb import mongo_service
        from bson import ObjectId
    
        if not mongo_service or not mongo_service.is_connected():
            return []
    
        try:
            activities = mongo_service.get_user_activities(user_id, limit)
        
            # Convert ObjectId to string for JSON serialization
            for activity in activities:
                if '_id' in activity:
                    activity['_id'] = str(activity['_id'])
                # Also convert datetime to string
                if 'created_at' in activity and hasattr(activity['created_at'], 'isoformat'):
                    activity['created_at'] = activity['created_at'].isoformat()
        
            return activities
        except Exception as e:
            print(f"❌ Error getting user activities: {e}")
            return []
    
    @staticmethod
    def log_login_success(user_id):
        """Log successful login"""
        from backend.mongodb import mongo_service
        mongo_service.log_activity(
            user_id=user_id,
            activity_type="login_success",
            details={"method": "password"}
        )

    @staticmethod  
    def log_feedback_submitted(user_id, feedback_id):
        """Log feedback submission"""
        from backend.mongodb import mongo_service
        mongo_service.log_activity(
            user_id=user_id,
            activity_type="feedback_submitted",
            details={"feedback_id": feedback_id}
        )

    @staticmethod
    def log_notification_sent(user_id, notification_type):
        """Log notification sent"""
        from backend.mongodb import mongo_service
        mongo_service.log_activity(
            user_id=user_id,
            activity_type="notification_sent",
            details={"notification_type": notification_type}
        )