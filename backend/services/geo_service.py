from backend.mongodb import mongo_service
from backend.models import User
from backend.extensions import db
from math import radians, sin, cos, sqrt, atan2

class GeoService:
    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points in km"""
        R = 6371  # Earth's radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    @staticmethod
    def find_nearby_users(lat, lng, radius_km=10, user_type=None):
        """
        Find users near a location with caching
        user_type: 'donor' or 'receiver' or None for all
        """
        
        # 1. Check cache first
        cached = mongo_service.get_cached_nearby(lat, lng, radius_km)
        if cached:
            print("✅ Using cached nearby users")
            return cached["cached_users"]
        
        print("🔄 Calculating nearby users from database...")
        
        # 2. Calculate from PostgreSQL database
        nearby_users = []
        
        with db.session.begin():
            all_users = User.query.all()
            
            for user in all_users:
                if user.location_lat and user.location_long:
                    distance = GeoService.haversine_distance(
                        lat, lng, user.location_lat, user.location_long
                    )
                    
                    if distance <= radius_km:
                        user_roles = [r.role_name for r in user.roles]
                        
                        # Filter by user_type if specified
                        if user_type:
                            if user_type in user_roles:
                                nearby_users.append({
                                    "user_id": user.user_id,
                                    "name": user.name,
                                    "email": user.email,
                                    "roles": user_roles,
                                    "distance_km": round(distance, 2),
                                    "lat": user.location_lat,
                                    "lng": user.location_long
                                })
                        else:
                            nearby_users.append({
                                "user_id": user.user_id,
                                "name": user.name,
                                "email": user.email,
                                "roles": user_roles,
                                "distance_km": round(distance, 2),
                                "lat": user.location_lat,
                                "lng": user.location_long
                            })
        
        # 3. Cache the result if we found users
        if nearby_users:
            mongo_service.cache_nearby_users(lat, lng, radius_km, nearby_users)
        
        return nearby_users