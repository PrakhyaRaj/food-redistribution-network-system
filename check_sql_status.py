import sys
sys.path.insert(0, 'backend')
from app import create_app
from extensions import db

app = create_app()
with app.app_context():
    from models import Transaction
    transactions = Transaction.query.all()
    print(f'Total transactions: {len(transactions)}')
    
    status_counts = {}
    for t in transactions:
        status = t.status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print('\nStatus breakdown:')
    for status, count in status_counts.items():
        print(f'  {status}: {count}')
    
    print('\nSample transactions:')
    for i, t in enumerate(transactions[:3]):
        print(f"  TXN {t.txn_id}: status={t.status}, donor_id={t.donor_id}, receiver_id={t.receiver_id}")
