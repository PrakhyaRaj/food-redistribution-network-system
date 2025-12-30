"""
Sync all transactions from SQL to MongoDB
This script ensures MongoDB has up-to-date copies of all transactions from the SQL database
"""
import sys
import os
sys.path.insert(0, 'backend')

# Set UTF-8 encoding for Windows terminal
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from mongodb import MongoService
from sqlalchemy import create_engine, text
import os as os_module

def sync_transactions():
    """Sync all transactions from SQL to MongoDB"""
    # Connect to PostgreSQL
    db_url = os_module.environ.get('DATABASE_URL', 'postgresql://postgres:Verma20?@localhost:5432/frns')
    engine = create_engine(db_url)
    
    # Connect to MongoDB
    mongo = MongoService()
    
    if not mongo.is_connected():
        print("MongoDB not connected!")
        return False
        
    try:
        with engine.connect() as connection:
            # Query all transactions
            result = connection.execute(text("SELECT * FROM transactions"))
            transactions = result.fetchall()
            
            print(f"\nFound {len(transactions)} transactions in SQL database")
            
            synced = 0
            skipped = 0
            
            for txn in transactions:
                try:
                    txn_id = txn[1]  # txn_id is second column
                    donor_id = txn[2]
                    receiver_id = txn[3]
                    food_id = txn[4]
                    request_id = txn[5]
                    status = txn[6]
                    created_at = txn[7]
                    updated_at = txn[8]
                    
                    # Check if transaction exists in MongoDB
                    existing = mongo.db["transactions"].find_one({"txn_id": txn_id})
                    
                    if existing:
                        # Update existing transaction with current SQL status
                        result = mongo.db["transactions"].update_one(
                            {"txn_id": txn_id},
                            {
                                "$set": {
                                    "status": status,
                                    "donor_id": donor_id,
                                    "receiver_id": receiver_id,
                                    "food_id": food_id,
                                    "request_id": request_id,
                                    "updated_at": updated_at
                                }
                            }
                        )
                        if result.modified_count > 0:
                            print(f"Updated TXN {txn_id}: status={status}")
                            synced += 1
                        else:
                            print(f"TXN {txn_id}: already synced (status={status})")
                            skipped += 1
                    else:
                        # Insert new transaction
                        mongo.db["transactions"].insert_one({
                            "txn_id": txn_id,
                            "donor_id": donor_id,
                            "receiver_id": receiver_id,
                            "food_id": food_id,
                            "request_id": request_id,
                            "status": status,
                            "route_data": None,
                            "created_at": created_at,
                            "updated_at": updated_at
                        })
                        print(f"Created TXN {txn_id}: status={status}")
                        synced += 1
                        
                except Exception as e:
                    print(f"Error syncing TXN: {e}")
            
            print(f"\nSync complete:")
            print(f"   Synced: {synced}")
            print(f"   Skipped: {skipped}")
            
            # Verify stats
            print(f"\nMongoDB Transaction Status Breakdown:")
            statuses = mongo.db["transactions"].aggregate([
                {'$group': {'_id': '$status', 'count': {'$sum': 1}}}
            ])
            for doc in list(statuses):
                print(f"   {doc['_id']}: {doc['count']}")
                
    except Exception as e:
        print(f"Error during sync: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔄 Starting Transaction Sync...")
    success = sync_transactions()
    if success:
        print("\n✅ Sync completed successfully!")
    else:
        print("\n❌ Sync failed!")
        sys.exit(1)
