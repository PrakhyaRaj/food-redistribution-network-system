#!/usr/bin/env python3
"""
Sync Analytics Data - Log all completed transactions to MongoDB analytics
"""
import sys
from pymongo import MongoClient
from sqlalchemy import create_engine, text
from datetime import datetime

# Database connection strings
MONGO_URI = "mongodb://root:example@localhost:27017/frns_db?authSource=admin"
SQL_DB_URL = "postgresql://postgres:Verma20?@localhost:5432/frns"

def sync_analytics():
    """Sync completed transactions to analytics collection"""
    
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
        # Get all completed transactions from SQL
        query = text("""
            SELECT t.txn_id, t.donor_id, t.receiver_id, t.food_id, t.request_id, t.status, t.created_at,
                   f.name as food_name, f.quantity,
                   r.food_type
            FROM transactions t
            LEFT JOIN food_items f ON t.food_id = f.food_id
            LEFT JOIN requests r ON t.request_id = r.request_id
            WHERE t.status = 'completed'
        """)
        result = sql_connection.execute(query)
        transactions = result.fetchall()
        columns = result.keys()
        
        print(f"\n[INFO] Found {len(transactions)} completed transactions in SQL")
        
        synced = 0
        skipped = 0
        
        for txn_row in transactions:
            txn = dict(zip(columns, txn_row))
            txn_id = txn['txn_id']
            
            try:
                # Check if analytics for this transaction already exists
                existing = mongo_db['redistribution_analytics'].find_one(
                    {"$or": [
                        {"transaction_id": txn_id},
                        {"food_id": txn['food_id'], "donor_id": txn['donor_id'], "receiver_id": txn['receiver_id']}
                    ]}
                )
                
                if existing:
                    print(f"  [SKIP] TXN {txn_id}: analytics already logged")
                    skipped += 1
                else:
                    # Calculate impact metrics
                    quantity_kg = float(txn['quantity'] or 0)
                    people_fed = round(quantity_kg * 5)  # 5 people per kg
                    carbon_saved = round(quantity_kg * 2.5, 2)  # 2.5kg CO2 per kg
                    
                    # Insert new analytics record
                    mongo_db['redistribution_analytics'].insert_one({
                        "transaction_id": txn_id,
                        "donor_id": txn['donor_id'],
                        "receiver_id": txn['receiver_id'],
                        "food_id": txn['food_id'],
                        "food_type": txn['food_type'] or "unknown",
                        "quantity_kg": quantity_kg,
                        "impact_metrics": {
                            "people_fed": people_fed,
                            "carbon_saved_kg": carbon_saved,
                            "waste_prevented_kg": quantity_kg
                        },
                        "timestamp": txn['created_at'] or datetime.utcnow(),
                        "month": (txn['created_at'] or datetime.utcnow()).month,
                        "year": (txn['created_at'] or datetime.utcnow()).year,
                        "day_of_week": (txn['created_at'] or datetime.utcnow()).strftime('%A')
                    })
                    print(f"  [CREATE] TXN {txn_id}: {quantity_kg}kg food, {people_fed} people, {carbon_saved}kg CO2")
                    synced += 1
                    
            except Exception as e:
                print(f"  [ERROR] TXN {txn_id}: {e}")
        
        # Get summary
        print(f"\n[SUMMARY] Synced: {synced}, Skipped: {skipped}")
        print(f"\n[STATS] Analytics Collection Status:")
        
        count = mongo_db['redistribution_analytics'].count_documents({})
        print(f"  Total analytics records: {count}")
        
        # Get aggregate stats
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'total_quantity': {'$sum': '$quantity_kg'},
                    'total_people_fed': {'$sum': '$impact_metrics.people_fed'},
                    'total_carbon_saved': {'$sum': '$impact_metrics.carbon_saved_kg'},
                    'count': {'$sum': 1}
                }
            }
        ]
        
        stats = list(mongo_db['redistribution_analytics'].aggregate(pipeline))
        if stats:
            s = stats[0]
            print(f"  Total food saved: {s.get('total_quantity', 0):.1f} kg")
            print(f"  Total people fed: {s.get('total_people_fed', 0)}")
            print(f"  Total carbon saved: {s.get('total_carbon_saved', 0):.2f} kg CO2")
            print(f"  Total transactions: {s.get('count', 0)}")
        
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
    print("[START] Syncing analytics from SQL to MongoDB...")
    success = sync_analytics()
    if success:
        print("\n[SUCCESS] Sync completed!")
        sys.exit(0)
    else:
        print("\n[FAILED] Sync failed!")
        sys.exit(1)
