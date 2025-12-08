from backend.mongodb import mongo_service

class FeedbackService:
    @staticmethod
    def submit_feedback(user_id, feedback_type, message, metadata=None):
        """Submit user feedback"""
        if mongo_service is None:
            print(f"❌ MongoDB service not initialized")
            return None
            
        if not mongo_service.is_connected():
            print(f"⚠️ MongoDB not connected - skipping feedback for user {user_id}")
            return None
            
        try:
            # Call with correct parameter order: (user_id, message, feedback_type, metadata)
            result = mongo_service.insert_feedback(user_id, message, feedback_type, metadata)
            
            if result is None:
                print(f"❌ Failed to insert feedback for user {user_id}")
                return None
                
            print(f"✅ Feedback submitted successfully for user {user_id}")
            return result
            
        except Exception as e:
            print(f"❌ Error in submit_feedback: {e}")
            return None
    
    @staticmethod
    def get_user_feedback(user_id, limit=20):
        """Get feedback submitted by a user"""
        from backend.mongodb import mongo_service
    
        if not mongo_service or not mongo_service.is_connected():
            return []
    
        try:
            feedback_data = mongo_service.get_user_feedback(user_id, limit)
        
            # Convert ObjectId to string for JSON serialization
            for item in feedback_data:
                if '_id' in item:
                    item['_id'] = str(item['_id'])
                # Also convert any datetime objects to strings
                if 'created_at' in item and hasattr(item['created_at'], 'isoformat'):
                    item['created_at'] = item['created_at'].isoformat()
        
            return feedback_data
        except Exception as e:
            print(f"❌ Error getting user feedback: {e}")
            return []
    
    @staticmethod
    def get_unresolved_feedback():
        """Get all unresolved feedback"""
        if mongo_service is None or not mongo_service.is_connected():
            return []
        return mongo_service.get_unresolved_feedback()