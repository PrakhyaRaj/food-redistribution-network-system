# backend/mongodb.py - CORRECTED VERSION
from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from bson import ObjectId

class MongoService:
    def __init__(self, app=None):
        self.client = None
        self.db = None
        self.connected = False
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize MongoDB but don't crash if it fails"""
        try:
            mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
            db_name = os.environ.get("MONGO_DB", "frns_db")
            
            print(f"🔧 Attempting to connect to MongoDB at: {mongo_uri}")
            
            # Try to connect with timeout
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
            self.db = self.client[db_name]
            
            # Test connection
            self.client.admin.command('ping')
            self.connected = True
            
            print("✅ MongoDB connected successfully!")
            
            # Try to create indexes but don't crash if it fails
            try:
                self._create_indexes()
            except Exception as e:
                print(f"⚠️ Could not create indexes: {e}")
                print("⚠️ MongoDB will work without indexes")
                
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            print("⚠️ Running without MongoDB features...")
            self.connected = False
            self.db = None
    
    def _create_indexes(self):
        """Try to create indexes, but skip if no permission"""
        if not self.connected:
            return
    
        try:
            # Check if database is accessible
            if self.db is None:
                print("⚠️ No database connection for indexes")
                return
        
            # Get existing collections
            existing_collections = self.db.list_collection_names()
    
            # Create indexes only for collections that exist or will be created
            for collection_name in ["feedback", "activity_logs", "notifications", "geo_cache", 
                                "food_images", "redistribution_analytics", 
                                "optimized_routes", "food_notes"]:
                try:
                    if collection_name == "feedback":
                        self.db[collection_name].create_index([("user_id", 1)])
                        self.db[collection_name].create_index([("created_at", -1)])
                    elif collection_name == "activity_logs":
                        self.db[collection_name].create_index([("user_id", 1)])
                        self.db[collection_name].create_index([("created_at", -1)])
                    elif collection_name == "notifications":
                        self.db[collection_name].create_index([("user_id", 1)])
                        self.db[collection_name].create_index([("created_at", -1)])
                    elif collection_name == "geo_cache":
                        self.db[collection_name].create_index([("location", "2dsphere")])
                    elif collection_name == "food_images":
                        self.db[collection_name].create_index([("food_id", 1)])
                        self.db[collection_name].create_index([("created_at", -1)])
                    elif collection_name == "redistribution_analytics":
                        self.db[collection_name].create_index([("timestamp", -1)])
                        self.db[collection_name].create_index([("food_type", 1)])
                    elif collection_name == "optimized_routes":
                        self.db[collection_name].create_index([("route_signature", 1)], unique=True)
                        self.db[collection_name].create_index([("expires_at", 1)])
                    elif collection_name == "food_notes":
                        self.db[collection_name].create_index([("food_id", 1), ("note_type", 1)])
                        self.db[collection_name].create_index([("tags", 1)])
            
                    print(f"✅ Created indexes for {collection_name}")
                except Exception as e:
                    print(f"⚠️ Could not create index for {collection_name}: {e}")
    
            print("✅ MongoDB indexes setup complete!")
    
        except Exception as e:
            print(f"⚠️ Index creation error: {e}")
    
    # ============================
    # CORE METHODS
    # ============================
    
    def is_connected(self):
        """Check if MongoDB is connected"""
        return self.connected is True and self.db is not None
    
    def insert_feedback(self, user_id, message, feedback_type="general", metadata=None):
        """Insert user feedback"""
        if not self.is_connected():
            print(f"⚠️ MongoDB not available - skipping feedback for user {user_id}")
            return None
            
        try:
            doc = {
                "user_id": user_id,
                "type": feedback_type,
                "message": message,
                "metadata": metadata or {},
                "created_at": datetime.utcnow()
            }
            result = self.db["feedback"].insert_one(doc)
            print(f"✅ Feedback stored for user {user_id}, ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error storing feedback: {e}")
            return None
    
    def get_user_feedback(self, user_id, limit=20):
        """Get feedback submitted by a user"""
        if not self.is_connected():
            return []
            
        try:
            return list(self.db["feedback"].find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(limit))
        except Exception as e:
            print(f"❌ Error getting feedback: {e}")
            return []
    
    def get_unresolved_feedback(self):
        """Get all unresolved feedback"""
        if not self.is_connected():
            return []
            
        try:
            return list(self.db["feedback"].find(
                {"status": {"$in": ["pending", "reviewed"]}}
            ).sort("created_at", -1))
        except Exception as e:
            print(f"❌ Error getting unresolved feedback: {e}")
            return []
    
    def log_activity(self, user_id, activity_type, details, ip_address=None):
        """Log user activity"""
        if not self.is_connected():
            return None
            
        try:
            doc = {
                "user_id": user_id,
                "activity_type": activity_type,
                "details": details,
                "ip_address": ip_address,
                "created_at": datetime.utcnow()
            }
            self.db["activity_logs"].insert_one(doc)
            return True
        except Exception as e:
            print(f"❌ Error logging activity: {e}")
            return False
    
    def get_user_activities(self, user_id, limit=50):
        """Get recent activities for a user"""
        if not self.is_connected():
            return []
        
        try:
            # Convert user_id to string if it's not already
            user_id_str = str(user_id)
        
            activities = list(self.db["activity_logs"].find(
                {"user_id": user_id_str}
            ).sort("created_at", -1).limit(limit))
        
            # Convert ObjectId to string in MongoDB layer
            for activity in activities:
                if '_id' in activity:
                    activity['_id'] = str(activity['_id'])
        
            return activities
        except Exception as e:
            print(f"❌ Error getting activities: {e}")
            return []
    
    def store_notification(self, user_id, notification_data):
        """Store notification"""
        if not self.is_connected():
            return None
            
        try:
            doc = {
                "user_id": user_id,
                **notification_data,
                "read": False,
                "created_at": datetime.utcnow()
            }
            result = self.db["notifications"].insert_one(doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error storing notification: {e}")
            return None
    
    def get_unread_notifications(self, user_id, limit=50):
        """Get unread notifications"""
        if not self.is_connected():
            return []
            
        try:
            return list(self.db["notifications"].find(
                {"user_id": user_id, "read": False}
            ).sort("created_at", -1).limit(limit))
        except Exception as e:
            print(f"❌ Error getting unread notifications: {e}")
            return []
    
    def get_all_notifications(self, user_id, limit=50):
        """Get all notifications for user"""
        if not self.is_connected():
            return []
            
        try:
            return list(self.db["notifications"].find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(limit))
        except Exception as e:
            print(f"❌ Error getting all notifications: {e}")
            return []
    
    def mark_as_read(self, notification_ids):
        """Mark notifications as read"""
        if not self.is_connected():
            return
            
        try:
            # Convert string IDs to ObjectId
            object_ids = []
            for nid in notification_ids:
                try:
                    object_ids.append(ObjectId(nid))
                except:
                    continue  # Skip invalid IDs
            
            if object_ids:
                self.db["notifications"].update_many(
                    {"_id": {"$in": object_ids}},
                    {"$set": {"read": True, "read_at": datetime.utcnow()}}
                )
                print(f"✅ Marked {len(object_ids)} notifications as read")
        except Exception as e:
            print(f"❌ Error marking as read: {e}")
    
    def get_daily_activity_stats(self, days=7):
        """Get daily activity statistics"""
        if not self.is_connected():
            return []
            
        try:
            pipeline = [
                {
                    "$match": {
                        "created_at": {
                            "$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)
                        }
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$created_at"},
                            "month": {"$month": "$created_at"},
                            "day": {"$dayOfMonth": "$created_at"}
                        },
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id.year": -1, "_id.month": -1, "_id.day": -1}}
            ]
            
            return list(self.db["activity_logs"].aggregate(pipeline))
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return []
        
    def get_cached_nearby(self, lat, lng, radius_km):
        """Get cached nearby users"""
        if not self.is_connected():
            return None
        
        try:
            from bson.son import SON
            query = {
                "location": {
                    "$nearSphere": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [lng, lat]
                        },
                        "$maxDistance": radius_km * 1000  # Convert km to meters
                    }
                },
                "expires_at": {"$gt": datetime.utcnow()}
            }
        
            return self.db["geo_cache"].find_one(query)
        except Exception as e:
            print(f"❌ Error getting cached nearby: {e}")
            return None
        
    def cache_nearby_users(self, center_lat, center_lng, radius_km, user_list):
        """Cache nearby users for a location"""
        if not self.is_connected():
            return None
        
        try:
            doc = {
                "location": {
                    "type": "Point",
                    "coordinates": [center_lng, center_lat]  # GeoJSON: [lng, lat]
                },
                "radius_km": radius_km,
                "cached_users": user_list,
                "expires_at": datetime.utcnow() + timedelta(minutes=30),  # 30 min cache
                "created_at": datetime.utcnow()
            }
            result = self.db["geo_cache"].insert_one(doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error caching nearby users: {e}")
            return None

    def store_food_image(self, food_id, user_id, image_data, metadata=None):
        """Store food item images (store as Base64 or URL)"""
        if not self.is_connected():
            return None
    
        try:
            doc = {
                "food_id": food_id,
                "user_id": user_id,
                "image_type": metadata.get('type', 'upload') if metadata else 'upload',
                "image_data": image_data,  # Base64 encoded or URL
                "file_size": metadata.get('file_size', 0) if metadata else 0,
                "mime_type": metadata.get('mime_type', 'image/jpeg') if metadata else 'image/jpeg',
                "caption": metadata.get('caption', '') if metadata else '',
                "status": "active",
                "created_at": datetime.utcnow(),
                "metadata": metadata or {}
            }
            result = self.db["food_images"].insert_one(doc)
            print(f"✅ Food image stored for food_id {food_id}")
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error storing food image: {e}")
            return None

    def get_food_images(self, food_id, limit=10):
        """Get images for a food item"""
        if not self.is_connected():
            return []
    
        try:
            images = list(self.db["food_images"].find(
                {"food_id": food_id, "status": "active"}
            ).sort("created_at", -1).limit(limit))
        
            # Convert ObjectId to string
            for img in images:
                if '_id' in img:
                    img['_id'] = str(img['_id'])
        
            return images
        except Exception as e:
            print(f"❌ Error getting food images: {e}")
            return []

    def store_food_note(self, food_id, user_id, note_type, content, metadata=None):
        """Store complex notes for food items"""
        if not self.is_connected():
            return None
    
        try:
            doc = {
                "food_id": food_id,
                "user_id": user_id,
                "note_type": note_type,
                "content": content,
                "priority": metadata.get('priority', 'medium') if metadata else 'medium',
                "tags": metadata.get('tags', []) if metadata else [],
                "attachments": metadata.get('attachments', []) if metadata else [],
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "metadata": metadata or {}
            }
            result = self.db["food_notes"].insert_one(doc)
            print(f"✅ Food note stored for food_id {food_id}")
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error storing food note: {e}")
            return None

    def get_food_notes(self, food_id, note_type=None, limit=20):
        """Get notes for a food item"""
        if not self.is_connected():
            return []
    
        try:
            query = {"food_id": food_id, "status": "active"}
            if note_type:
                query["note_type"] = note_type
        
            notes = list(self.db["food_notes"].find(query)
                        .sort([("priority", -1), ("created_at", -1)])
                        .limit(limit))
        
            # Convert ObjectId to string
            for note in notes:
                if '_id' in note:
                    note['_id'] = str(note['_id'])
        
            return notes
        except Exception as e:
            print(f"❌ Error getting food notes: {e}")
            return []

    def log_food_redistribution(self, donor_id, receiver_id, food_id, quantity_kg, food_type):
        """Log successful food redistribution for analytics"""
        if not self.is_connected():
            return None
    
        try:
            # Calculate impact metrics
            people_fed = round(quantity_kg * 5)  # Approx 5 people per kg
            carbon_saved = round(quantity_kg * 2.5, 2)  # 2.5kg CO2 per kg food saved
        
            doc = {
                "donor_id": donor_id,
                "receiver_id": receiver_id,
                "food_id": food_id,
                "food_type": food_type,
                "quantity_kg": quantity_kg,
                "impact_metrics": {
                    "people_fed": people_fed,
                    "carbon_saved_kg": carbon_saved,
                    "waste_prevented_kg": quantity_kg
                },
                "timestamp": datetime.utcnow(),
                "month": datetime.utcnow().month,
                "year": datetime.utcnow().year,
                "day_of_week": datetime.utcnow().strftime('%A')
            }
            result = self.db["redistribution_analytics"].insert_one(doc)
            print(f"✅ Redistribution analytics logged: {quantity_kg}kg saved")
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error logging redistribution analytics: {e}")
            return None

    def get_analytics_summary(self, days=30):
        """Get analytics summary for dashboard"""
        if not self.is_connected():
            return {}
    
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
        
            # Check if collection exists
            if "redistribution_analytics" not in self.db.list_collection_names():
                return {
                    "total_food_saved_kg": 0,
                    "total_people_fed": 0,
                    "total_carbon_saved": 0,
                    "total_redistributions": 0,
                    "avg_quantity_per_redistribution": 0
                }
        
            pipeline = [
                {
                    "$match": {
                        "timestamp": {"$gte": cutoff_date}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_food_saved_kg": {"$sum": "$quantity_kg"},
                        "total_people_fed": {"$sum": "$impact_metrics.people_fed"},
                        "total_carbon_saved": {"$sum": "$impact_metrics.carbon_saved_kg"},
                        "total_redistributions": {"$sum": 1},
                        "avg_quantity_per_redistribution": {"$avg": "$quantity_kg"}
                    }
                }
            ]
        
            result = list(self.db["redistribution_analytics"].aggregate(pipeline))
        
            if result:
                return result[0]
            else:
                return {
                    "total_food_saved_kg": 0,
                    "total_people_fed": 0,
                    "total_carbon_saved": 0,
                    "total_redistributions": 0,
                    "avg_quantity_per_redistribution": 0
                }
        except Exception as e:
            print(f"❌ Error getting analytics summary: {e}")
            return {}

    def log_route_optimization(self, user_id, pickup_points, delivery_points, result=None):
        """Log route optimization request + result for auditing"""
        if not self.is_connected():
            print(f"⚠️ MongoDB not available - skipping route log for user {user_id}")
            return None

        try:
            doc = {
                "user_id": str(user_id),
                "pickup_points": pickup_points,
                "delivery_points": delivery_points,
                "result": result or {},
                "timestamp": datetime.utcnow()
            }
            result = self.db["optimized_routes"].insert_one(doc)
            print(f"🚗 Route optimization logged, ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error logging route optimization: {e}")
            return None

    def cache_optimized_route(self, route_data, optimization_result, ttl_hours=24):
        """Cache optimized route results"""
        if not self.is_connected():
            return None
    
        try:
            import hashlib
            route_signature = hashlib.md5(str(route_data).encode()).hexdigest()
        
            doc = {
                "route_signature": route_signature,
                "route_data": route_data,
                "optimization_result": optimization_result,
                "expires_at": datetime.utcnow() + timedelta(hours=ttl_hours),
                "created_at": datetime.utcnow(),
                "cache_hits": 0
            }
            result = self.db["optimized_routes"].insert_one(doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error caching optimized route: {e}")
            return None

    def get_cached_route(self, route_signature):
        """Get cached optimized route"""
        if not self.is_connected():
            return None
    
        try:
            cached = self.db["optimized_routes"].find_one({
                "route_signature": route_signature,
                "expires_at": {"$gt": datetime.utcnow()}
            })
        
            if cached:
                # Update cache hits
                self.db["optimized_routes"].update_one(
                    {"_id": cached["_id"]},
                    {"$inc": {"cache_hits": 1}}
                )
                return cached
            return None
        except Exception as e:
            print(f"❌ Error getting cached route: {e}")
            return None

# Singleton instance
mongo_service = None

def init_mongo(app):
    """Initialize MongoDB service"""
    global mongo_service
    mongo_service = MongoService(app)
    app.mongodb = mongo_service
    return mongo_service