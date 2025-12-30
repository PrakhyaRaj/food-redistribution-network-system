from backend.models import db, Transaction
from backend.app import create_app

app = create_app()
with app.app_context():
    txns = Transaction.query.order_by(Transaction.txn_id.desc()).limit(5).all()
    print(f"Total transactions: {Transaction.query.count()}")
    if txns:
        print(f"\nLatest 5 transactions:")
        for t in txns:
            print(f"  - Txn {t.txn_id}: Status={t.status}, Created={t.created_at}")
    else:
        print("No transactions found")
