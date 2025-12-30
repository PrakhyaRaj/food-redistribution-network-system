"""
Test script to mark stuck transactions as completed and verify analytics
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
from datetime import datetime
from pymongo import MongoClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.models import FoodItem, Transaction, Request, User
from backend.config import Config

def main():
    print("\n" + "="*70)
    print("MARKING STUCK TRANSACTIONS AS COMPLETED")
    print("="*70)
    
    # Connect to database
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Connect to MongoDB
    mongo_client = MongoClient('mongodb://localhost:27017/')
    mongo_db = mongo_client['food_redistribution']
    
    try:
        # Get first few initiated transactions
        stuck_txns = session.query(Transaction).filter(
            Transaction.status.in_(['initiated', 'in_progress'])
        ).limit(10).all()
        
        print(f"\n🔄 Found {len(stuck_txns)} transactions to complete")
        
        for txn in stuck_txns:
            print(f"\n📌 Transaction {txn.txn_id}:")
            print(f"   Old status: {txn.status}")
            
            # Update status
            txn.status = "completed"
            txn.completed_at = datetime.utcnow()
            session.commit()
            print(f"   New status: {txn.status}")
            
            # Mark food as collected
            food = session.query(FoodItem).filter(FoodItem.food_id == txn.food_id).first()
            if food:
                print(f"   Food item {txn.food_id} old status: {food.status}")
                food.status = "collected"
                session.commit()
                print(f"   Food item {txn.food_id} new status: {food.status}")
            
            # Log to analytics
            try:
                donor = session.query(User).filter(User.user_id == txn.donor_id).first()
                receiver = session.query(User).filter(User.user_id == txn.receiver_id).first()
                if donor and receiver and food:
                    mongo_db.redistribution_analytics.insert_one({
                        "transaction_id": txn.txn_id,
                        "donor_id": txn.donor_id,
                        "receiver_id": txn.receiver_id,
                        "food_id": txn.food_id,
                        "food_name": food.name,
                        "quantity_kg": food.quantity,
                        "distance_km": 25.5,  # Example
                        "distance_source": "test_marked",
                        "status": "completed",
                        "created_at": datetime.utcnow()
                    })
                    print(f"   ✅ Analytics logged")
            except Exception as ae:
                print(f"   ⚠️ Analytics failed: {ae}")
        
        # Now check the state
        print("\n" + "="*70)
        print("CHECKING UPDATED STATE")
        print("="*70)
        
        txns = session.query(Transaction).all()
        txn_status = {}
        for t in txns:
            txn_status[t.status] = txn_status.get(t.status, 0) + 1
        
        foods = session.query(FoodItem).all()
        food_status = {}
        for f in foods:
            food_status[f.status] = food_status.get(f.status, 0) + 1
        
        print(f"\n📊 Transactions by status: {txn_status}")
        print(f"🍲 Foods by status: {food_status}")
        
        # Check analytics
        analytics = mongo_db.redistribution_analytics.count_documents({})
        print(f"\n📈 Analytics records: {analytics}")
        
        if analytics > 0:
            sample = mongo_db.redistribution_analytics.find_one(sort=[("created_at", -1)])
            print(f"\n   Last record:")
            print(f"   - Transaction: {sample.get('transaction_id')}")
            print(f"   - Food: {sample.get('food_name')}")
            print(f"   - Distance: {sample.get('distance_km')} km")
            print(f"   - Source: {sample.get('distance_source')}")
        
        print(f"\n✅ Done! Check dashboards - analytics should now show data")
        
    finally:
        session.close()
        mongo_client.close()

if __name__ == "__main__":
    main()
