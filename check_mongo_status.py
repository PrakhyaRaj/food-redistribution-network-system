import sys
sys.path.insert(0, 'backend')
from mongodb import MongoService

mongo = MongoService()
if mongo.is_connected():
    # Check transaction statuses in MongoDB
    print('=== Transaction Statuses in MongoDB ===')
    statuses = mongo.db['transactions'].aggregate([
        {'$group': {'_id': '$status', 'count': {'$sum': 1}}}
    ])
    for doc in list(statuses):
        print(f"{doc['_id']}: {doc['count']}")
    
    # Check specific transaction
    print('\n=== Sample Transactions ===')
    sample = list(mongo.db['transactions'].find().limit(3))
    for t in sample:
        print(f"TXN {t.get('txn_id')}: status={t.get('status')}, donor_id={t.get('donor_id')}")
    
    # Count for specific user
    print('\n=== Check Stats for Donor User ===')
    stats = mongo.get_transaction_stats('donor1')
    print(f"Stats: {stats}")
else:
    print('MongoDB not connected')
