#!/usr/bin/env python3
"""
Direct MongoDB sync - No Flask app initialization needed
Syncs completed transactions from SQL to MongoDB
"""
import sys
from pymongo import MongoClient
from sqlalchemy import create_engine, text
from datetime import datetime

# Database connection strings
MONGO_URI = "mongodb://root:example@localhost:27017/frns_db?authSource=admin"
SQL_DB_URL = "postgresql://postgres:Verma20?@localhost:5432/frns"

def sync_transactions_direct():
    """Sync transactions directly from SQL to MongoDB"""
    
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
        # Get all transactions from SQL
        query = text("SELECT txn_id, donor_id, receiver_id, food_id, request_id, status, completed_at, created_at FROM transactions")
        result = sql_connection.execute(query)
        transactions = result.fetchall()
        columns = result.keys()
        
        print(f"\n[INFO] Found {len(transactions)} transactions in SQL")
        
        synced = 0
        updated = 0
        
        for txn_row in transactions:
            txn = dict(zip(columns, txn_row))
            txn_id = txn['txn_id']
            
            try:
                existing = mongo_db['transactions'].find_one({"txn_id": txn_id})
                
                if existing:
                    # Update the transaction status
                    update_result = mongo_db['transactions'].update_one(
                        {"txn_id": txn_id},
                        {
                            "$set": {
                                "status": txn['status'],
                                "donor_id": txn['donor_id'],
                                "receiver_id": txn['receiver_id'],
                                "food_id": txn['food_id'],
                                "request_id": txn['request_id'],
                                "updated_at": datetime.utcnow()
                            }
                        }
                    )
                    if update_result.modified_count > 0:
                        print(f"  [UPDATE] TXN {txn_id}: {existing.get('status')} -> {txn['status']}")
                        updated += 1
                else:
                    # Insert new transaction
                    mongo_db['transactions'].insert_one({
                        "txn_id": txn_id,
                        "donor_id": txn['donor_id'],
                        "receiver_id": txn['receiver_id'],
                        "food_id": txn['food_id'],
                        "request_id": txn['request_id'],
                        "status": txn['status'],
                        "route_data": None,
                        "created_at": txn['created_at'],
                        "updated_at": datetime.utcnow()
                    })
                    print(f"  [CREATE] TXN {txn_id}: {txn['status']}")
                    synced += 1
                    
            except Exception as e:
                print(f"  [ERROR] TXN {txn_id}: {e}")
        
        # Get status breakdown
        print(f"\n[SUMMARY] Synced: {synced}, Updated: {updated}")
        print(f"\n[STATUS] MongoDB Transaction Breakdown:")
        
        pipeline = [
            {'$group': {'_id': '$status', 'count': {'$sum': 1}}}
        ]
        statuses = mongo_db['transactions'].aggregate(pipeline)
        for doc in list(statuses):
            print(f"  {doc['_id']}: {doc['count']}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Sync failed: {e}")
        return False
        
    finally:
        try:
            sql_connection.close()
            mongo_client.close()
        except:
            pass

if __name__ == "__main__":
    print("[START] Syncing transactions from SQL to MongoDB...")
    success = sync_transactions_direct()
    if success:
        print("\n[SUCCESS] Sync completed!")
        sys.exit(0)
    else:
        print("\n[FAILED] Sync failed!")
        sys.exit(1)
