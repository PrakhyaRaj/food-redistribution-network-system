"""
Check actual data in database - what statuses are there?
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.models import FoodItem, Transaction, Request, User
from backend.config import Config

def main():
    print("\n" + "="*70)
    print("CHECKING DATABASE STATE")
    print("="*70)
    
    # Connect to database
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check Users
        print("\n👥 USERS:")
        users = session.query(User).all()
        print(f"Total: {len(users)}")
        for u in users[:3]:
            print(f"  - {u.name} (ID: {u.user_id}, roles: {[r.role_name for r in u.roles]})")
        
        # Check Food Items
        print("\n🍲 FOOD ITEMS:")
        foods = session.query(FoodItem).all()
        print(f"Total: {len(foods)}")
        status_counts = {}
        for food in foods:
            status_counts[food.status] = status_counts.get(food.status, 0) + 1
            if status_counts[food.status] <= 2:  # Show first 2 of each status
                print(f"  - {food.name} (ID: {food.food_id}, status: {food.status}, donor: {food.donor_id})")
        print(f"\nBy Status: {status_counts}")
        
        # Check Requests
        print("\n📋 REQUESTS:")
        requests = session.query(Request).all()
        print(f"Total: {len(requests)}")
        req_status_counts = {}
        for req in requests:
            req_status_counts[req.status] = req_status_counts.get(req.status, 0) + 1
            if req_status_counts[req.status] <= 2:
                print(f"  - {req.food_type} x{req.quantity} (ID: {req.request_id}, status: {req.status}, receiver: {req.receiver_id})")
        print(f"\nBy Status: {req_status_counts}")
        
        # Check Transactions
        print("\n💳 TRANSACTIONS:")
        txns = session.query(Transaction).all()
        print(f"Total: {len(txns)}")
        txn_status_counts = {}
        for txn in txns:
            txn_status_counts[txn.status] = txn_status_counts.get(txn.status, 0) + 1
            print(f"  - TXN {txn.txn_id}: donor {txn.donor_id} → receiver {txn.receiver_id}, status: {txn.status}, food: {txn.food_id}")
        print(f"\nBy Status: {txn_status_counts}")
        
        # Key Analysis
        print("\n" + "="*70)
        print("ANALYSIS")
        print("="*70)
        
        if txn_status_counts:
            completed_txns = txn_status_counts.get('completed', 0)
            total_txns = len(txns)
            print(f"\n❌ Only {completed_txns}/{total_txns} transactions are 'completed'")
            print(f"   {total_txns - completed_txns} transactions stuck in '{list(txn_status_counts.keys())}'")
            
            # Check if food items match transaction status
            collected_foods = sum(1 for f in foods if f.status == 'collected')
            print(f"\n❌ Only {collected_foods}/{len(foods)} food items are 'collected'")
            print(f"   Food items: {status_counts}")
            
            print("\n🔴 MAIN ISSUE:")
            print("   When transactions are completed, they should trigger:")
            print("   1. food_item.status = 'collected'")
            print("   2. transaction.status = 'completed'")
            print("   3. Analytics entry to be counted")
            print("\n   This is NOT happening automatically!")
        else:
            print("\n⚠️  No transactions found at all")
            print("   Create a match first:")
            print("   1. Donor posts food")
            print("   2. Receiver creates request")
            print("   3. Receiver clicks 'Find Matches'")
            print("   4. Receiver clicks 'Accept Match'")
        
    finally:
        session.close()

if __name__ == "__main__":
    main()
