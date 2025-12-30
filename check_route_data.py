#!/usr/bin/env python3
"""
Check MongoDB transactions for route_data
"""
from pymongo import MongoClient

MONGO_URI = "mongodb://root:example@localhost:27017/frns_db?authSource=admin"

try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    mongo_client.admin.command('ping')
    mongo_db = mongo_client['frns_db']
    print("[OK] Connected to MongoDB\n")
    
    # Check transactions with route_data
    transactions = list(mongo_db['transactions'].find({"route_data": {"$ne": None}}).limit(5))
    
    print(f"Found {len(transactions)} transactions with route_data:")
    for t in transactions:
        print(f"  TXN {t['txn_id']}: has route_data = {bool(t.get('route_data'))}")
        if t.get('route_data'):
            print(f"    Keys: {list(t['route_data'].keys())}")
    
    print(f"\nTotal transactions: {mongo_db['transactions'].count_documents({})}")
    print(f"With route_data: {mongo_db['transactions'].count_documents({'route_data': {'$ne': None}})}")
    print(f"Without route_data: {mongo_db['transactions'].count_documents({'route_data': None})}")
    
    mongo_client.close()
    
except Exception as e:
    print(f"[ERROR] {e}")
