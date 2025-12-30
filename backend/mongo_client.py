from pymongo import MongoClient, ASCENDING, GEO2D, GEOSPHERE
from pymongo.errors import DuplicateKeyError
import os

MONGO_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/foodshare")

class MongoService:
    def __init__(self, uri=None, db_name=None):
        uri = uri or MONGO_URI
        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        if self.client is None:
            raise RuntimeError("Mongo client not initialized properly")

        # default DB name is last path segment if provided; else 'foodshare'
        if db_name:
            self.db = self.client[db_name]
        else:
            # parse default from URI if present
            self.db = self.client.get_default_database() or self.client["foodshare"]
        self._ensure_indexes()

    def is_connected(self):
        """Check if MongoDB is connected"""
        try:
            self.client.admin.command('ping')
            return True
        except Exception:
            return False

    def _ensure_indexes(self):
        # feedback_logs: keep for 90 days
        try:
            self.db.feedback_logs.create_index([("created_at", ASCENDING)], expireAfterSeconds=90*24*3600)
        except Exception:
            pass
        # activity_logs: TTL 30 days
        try:
            self.db.activity_logs.create_index([("created_at", ASCENDING)], expireAfterSeconds=30*24*3600)
        except Exception:
            pass
        # notifications: keep for 7 days
        try:
            self.db.notifications.create_index([("created_at", ASCENDING)], expireAfterSeconds=7*24*3600)
            # also index by user_id and status for quick lookups
            self.db.notifications.create_index([("user_id", ASCENDING), ("status", ASCENDING)])
        except Exception:
            pass
        # geo_cache: TTL 7 days + geospatial index if storing lat/long
        try:
            # if storing { location: { type: "Point", coordinates: [lon, lat] } }
            self.db.geo_cache.create_index([("location", GEOSPHERE)])
            self.db.geo_cache.create_index([("created_at", ASCENDING)], expireAfterSeconds=7*24*3600)
        except Exception:
            pass

    # Feedback APIs
    def insert_feedback(self, user_id, message, metadata=None):
        doc = {
            "user_id": user_id,
            "message": message,
            "metadata": metadata or {},
            "created_at": __import__("datetime").datetime.utcnow()
        }
        if self.db is None:
            raise RuntimeError("DB not initialized")

        return self.db.feedback_logs.insert_one(doc).inserted_id

    # Activity log
    def log_activity(self, user_id, action, metadata=None):
        doc = {
            "user_id": user_id,
            "action": action,
            "metadata": metadata or {},
            "created_at": __import__("datetime").datetime.utcnow()
        }
        return self.db.activity_logs.insert_one(doc).inserted_id

    # Notifications
    def create_notification(self, user_id, title, body, meta=None, status="pending"):
        doc = {
            "user_id": user_id,
            "title": title,
            "body": body,
            "meta": meta or {},
            "status": status,
            "created_at": __import__("datetime").datetime.utcnow()
        }
        return self.db.notifications.insert_one(doc).inserted_id

    def store_notification(self, user_id, notification_data):
        """Store a notification for a user"""
        doc = {
            "user_id": user_id,
            "type": notification_data.get("type", "general"),
            "title": notification_data.get("title", ""),
            "message": notification_data.get("message", ""),
            "transaction_id": notification_data.get("transaction_id"),
            "status": notification_data.get("status", "unread"),
            "created_at": __import__("datetime").datetime.utcnow()
        }
        return self.db.notifications.insert_one(doc).inserted_id

    def get_unread_notifications(self, user_id, limit=50):
        """Get unread notifications for a user"""
        return list(self.db.notifications.find({
            "user_id": user_id,
            "status": "unread"
        }).sort("created_at", -1).limit(limit))

    def get_all_notifications(self, user_id, limit=50):
        """Get all notifications for a user"""
        return list(self.db.notifications.find({
            "user_id": user_id
        }).sort("created_at", -1).limit(limit))

    def get_pending_notifications(self, limit=100):
        return list(self.db.notifications.find({"status": "pending"}).limit(limit))

    def mark_notification_sent(self, notification_id):
        return self.db.notifications.update_one({"_id": notification_id}, {"$set": {"status": "sent", "sent_at": __import__("datetime").datetime.utcnow()}})

    # Geo cache: store geocode or route responses with geospatial key
    def set_geo_cache(self, key, lon, lat, payload):
        doc = {
            "_id": key,  # use string key so updates are idempotent
            "location": {"type": "Point", "coordinates": [lon, lat]},
            "payload": payload,
            "created_at": __import__("datetime").datetime.utcnow()
        }
        return self.db.geo_cache.replace_one({"_id": key}, doc, upsert=True)

    def get_geo_cache_by_point(self, lon, lat, max_distance_m=100):
        # max_distance_m in meters; requires GeoJSON & $nearSphere with meters when using 2dsphere
        return list(self.db.geo_cache.find({
            "location": {
                "$nearSphere": {
                    "$geometry": {"type": "Point", "coordinates": [lon, lat]},
                    "$maxDistance": max_distance_m
                }
            }
        }).limit(10))