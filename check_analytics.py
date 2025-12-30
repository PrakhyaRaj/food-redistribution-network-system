from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient('mongodb://root:example@localhost:27017/frns_db?authSource=admin')
db = client['frns_db']

count = db['redistribution_analytics'].count_documents({})
print(f'✅ Total analytics documents: {count}')

# Get last 5 documents
latest = list(db['redistribution_analytics'].find().sort('timestamp', -1).limit(5))
if latest:
    print(f'\nLatest 5 documents:')
    for i, doc in enumerate(latest, 1):
        ts = doc.get('timestamp', 'N/A')
        age = 'unknown'
        if isinstance(ts, datetime):
            age_delta = datetime.utcnow() - ts
            age_minutes = age_delta.total_seconds() / 60
            age = f'{age_minutes:.1f} min ago'
        print(f'{i}. Txn {doc.get("transaction_id")}: {doc.get("quantity_kg")}kg by donor {doc.get("donor_id")} - {age}')
else:
    print('No documents found')
