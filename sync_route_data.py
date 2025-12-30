#!/usr/bin/env python3
"""
Sync Route Optimization Data - Calculate and store route data for all transactions
"""
from pymongo import MongoClient
from sqlalchemy import create_engine, text
import sys

MONGO_URI = "mongodb://root:example@localhost:27017/frns_db?authSource=admin"
SQL_DB_URL = "postgresql://postgres:Verma20?@localhost:5432/frns"

def calculate_route(donor_lat, donor_long, receiver_lat, receiver_long):
    """Calculate route data between two locations"""
    try:
        # Import RouteOptimizer
        sys.path.insert(0, 'backend')
        from services.route_optimizer import RouteOptimizer
        
        # Get distance from OSRM
        distance_km = RouteOptimizer._get_osrm_distance(donor_lat, donor_long, receiver_lat, receiver_long)
        
        if not distance_km:
            # Fallback to haversine
            distance_km = RouteOptimizer._haversine_distance(donor_lat, donor_long, receiver_lat, receiver_long)
        
        if isinstance(distance_km, dict):
            distance_km = distance_km.get('distance_km', 0)
        
        # Calculate time (assuming 50 km/h average)
        time_hours = (distance_km or 0) / 50.0
        
        # Build route data
        route_data = {
            "success": True,
            "route": {
                "total_distance_km": round(float(distance_km or 0), 2),
                "estimated_time_hours": round(float(time_hours), 2),
                "vehicle_recommendation": "van",
                "distance_source": "osrm" if distance_km else "haversine"
            },
            "metrics": {
                "fuel_consumed_liters": round(float(distance_km or 0) * 0.08, 2),  # ~0.08L per km
                "carbon_saved_kg": round(float(distance_km or 0) * 0.12, 2),  # ~0.12kg CO2 per km
                "efficiency_score": 85
            }
        }
        
        return route_data
        
    except Exception as e:
        print(f"    [WARN] Route calculation failed: {e}")
        return None

def sync_route_data():
    """Sync route optimization data to all transactions"""
    
    # Connect to MongoDB
    try:
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        mongo_client.admin.command('ping')
        mongo_db = mongo_client['frns_db']
        print("[OK] Connected to MongoDB")
    except Exception as e:
        print(f"[ERROR] MongoDB connection failed: {e}")
        return False
    
    # Connect to PostgreSQL
    try:
        sql_engine = create_engine(SQL_DB_URL)
        sql_connection = sql_engine.connect()
        print("[OK] Connected to PostgreSQL")
    except Exception as e:
        print(f"[ERROR] PostgreSQL connection failed: {e}")
        return False
    
    try:
        # Get all transactions with user locations
        query = text("""
            SELECT t.txn_id, t.donor_id, t.receiver_id,
                   d.location_lat as donor_lat, d.location_long as donor_long,
                   r.location_lat as receiver_lat, r.location_long as receiver_long
            FROM transactions t
            LEFT JOIN users d ON t.donor_id = d.user_id
            LEFT JOIN users r ON t.receiver_id = r.user_id
        """)
        result = sql_connection.execute(query)
        transactions = result.fetchall()
        columns = result.keys()
        
        print(f"\n[INFO] Found {len(transactions)} transactions")
        
        synced = 0
        skipped = 0
        
        for txn_row in transactions:
            txn = dict(zip(columns, txn_row))
            txn_id = txn['txn_id']
            
            try:
                # Check if transaction already has route_data
                existing = mongo_db['transactions'].find_one({"txn_id": txn_id})
                
                if not existing:
                    print(f"  [SKIP] TXN {txn_id}: not found in MongoDB")
                    skipped += 1
                    continue
                
                if existing.get('route_data'):
                    print(f"  [SKIP] TXN {txn_id}: already has route_data")
                    skipped += 1
                    continue
                
                # Check if we have location data
                if not all([txn['donor_lat'], txn['donor_long'], txn['receiver_lat'], txn['receiver_long']]):
                    print(f"  [SKIP] TXN {txn_id}: missing location data")
                    skipped += 1
                    continue
                
                # Calculate route
                print(f"  [CALC] TXN {txn_id}: calculating route...")
                route_data = calculate_route(
                    txn['donor_lat'], txn['donor_long'],
                    txn['receiver_lat'], txn['receiver_long']
                )
                
                if route_data:
                    # Update transaction with route data
                    update_result = mongo_db['transactions'].update_one(
                        {"txn_id": txn_id},
                        {"$set": {"route_data": route_data}}
                    )
                    if update_result.modified_count > 0:
                        distance = route_data.get('route', {}).get('total_distance_km', 'N/A')
                        time = route_data.get('route', {}).get('estimated_time_hours', 'N/A')
                        print(f"  [UPDATE] TXN {txn_id}: {distance}km, {time}h")
                        synced += 1
                else:
                    print(f"  [FAIL] TXN {txn_id}: route calculation failed")
                    skipped += 1
                    
            except Exception as e:
                print(f"  [ERROR] TXN {txn_id}: {e}")
                skipped += 1
        
        print(f"\n[SUMMARY] Updated: {synced}, Skipped: {skipped}")
        print(f"\n[STATS] Transaction Route Data:")
        count_with_routes = mongo_db['transactions'].count_documents({'route_data': {'$ne': None}})
        count_without = mongo_db['transactions'].count_documents({'route_data': None})
        print(f"  With route_data: {count_with_routes}")
        print(f"  Without route_data: {count_without}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Sync failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        try:
            sql_connection.close()
            mongo_client.close()
        except:
            pass

if __name__ == "__main__":
    print("[START] Syncing route optimization data...")
    success = sync_route_data()
    if success:
        print("\n[SUCCESS] Sync completed!")
        sys.exit(0)
    else:
        print("\n[FAILED] Sync failed!")
        sys.exit(1)
