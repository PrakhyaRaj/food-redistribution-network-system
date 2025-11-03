# backend/routes/transaction_routes.py

from flask import Blueprint, request, jsonify
from app import db
from models import Transaction, FoodItem, User
from datetime import datetime

transaction_bp = Blueprint("transaction_bp", __name__)

# 🟢 1. Create a new transaction (Receiver claims a food item)
@transaction_bp.route("/transactions", methods=["POST"])
def create_transaction():
    data = request.get_json()

    donor_id = data.get("donor_id")
    receiver_id = data.get("receiver_id")
    food_id = data.get("food_id")

    if not donor_id or not receiver_id or not food_id:
        return jsonify({"error": "Missing required fields"}), 400

    # Check if the food item exists
    food_item = FoodItem.query.get(food_id)
    if not food_item:
        return jsonify({"error": "Food item not found"}), 404

    # Check if already claimed
    if food_item.status != "available":
        return jsonify({"error": "Food item already claimed"}), 400

    # Create a new transaction
    transaction = Transaction(
        donor_id=donor_id,
        receiver_id=receiver_id,
        food_id=food_id,
        date=datetime.utcnow(),
        status="claimed"
    )

    # Mark food item as claimed
    food_item.status = "claimed"

    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        "message": "Transaction created successfully",
        "transaction_id": transaction.txn_id
    }), 201


# 🟡 2. Get all transactions
@transaction_bp.route("/transactions", methods=["GET"])
def get_all_transactions():
    transactions = Transaction.query.all()

    output = []
    for txn in transactions:
        output.append({
            "txn_id": txn.txn_id,
            "donor_id": txn.donor_id,
            "receiver_id": txn.receiver_id,
            "food_id": txn.food_id,
            "food_name": txn.food.food_name if txn.food else None,
            "date": txn.date.strftime("%Y-%m-%d %H:%M:%S"),
            "status": txn.status
        })

    return jsonify(output), 200


# 🔵 3. Get transactions for a specific user (donor or receiver)
@transaction_bp.route("/transactions/user/<int:user_id>", methods=["GET"])
def get_user_transactions(user_id):
    transactions = Transaction.query.filter(
        (Transaction.donor_id == user_id) | (Transaction.receiver_id == user_id)
    ).all()

    if not transactions:
        return jsonify({"message": "No transactions found for this user"}), 404

    output = []
    for txn in transactions:
        output.append({
            "txn_id": txn.txn_id,
            "donor_id": txn.donor_id,
            "receiver_id": txn.receiver_id,
            "food_id": txn.food_id,
            "food_name": txn.food.food_name if txn.food else None,
            "date": txn.date.strftime("%Y-%m-%d %H:%M:%S"),
            "status": txn.status
        })

    return jsonify(output), 200


# 🔴 4. Update transaction status (optional)
@transaction_bp.route("/transactions/<int:txn_id>", methods=["PUT"])
def update_transaction_status(txn_id):
    data = request.get_json()
    new_status = data.get("status")

    txn = Transaction.query.get(txn_id)
    if not txn:
        return jsonify({"error": "Transaction not found"}), 404

    txn.status = new_status
    db.session.commit()

    return jsonify({"message": "Transaction status updated"}), 200
