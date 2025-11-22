from flask import Blueprint, request, jsonify
from models import Request, Transaction, db, FoodItem
from datetime import datetime

food_bp = Blueprint("food_bp", __name__, url_prefix="/food")


@food_bp.route("/add", methods=["POST"])
def add_food():
    data = request.json

    donor_id=data.get("user_id")
    if not donor_id:
        return jsonify({"error": "user_id is required"}), 400

    new_food = FoodItem(
        donor_id = donor_id,
        name=data["food_name"],
        quantity=data["quantity"],
        expiry_date=datetime.strptime(data["expiry_date"], "%Y-%m-%d")
    )
    db.session.add(new_food)
    db.session.commit()
    return jsonify({"message": "Food item added successfully!"}), 201

# @food_bp.route("/available", methods=["GET"])
# def available_foods():
#     foods = FoodItem.query.filter_by(status="available").all()
#     return jsonify([{
#         "food_id": f.food_id,
#         "name": f.name,
#         "quantity": f.quantity,
#         "expiry_date": str(f.expiry_date)
#     } for f in foods])

# ------------------------------------------------------------
# 2) Get All Foods Donated by Logged-In Donor
# ------------------------------------------------------------
@food_bp.route("/my/<int:donor_id>", methods=["GET"])
def get_my_food(donor_id):
    foods = FoodItem.query.filter_by(donor_id=donor_id).all()

    result = [
        {
            "food_id": f.food_id,
            "food_name": f.name,
            "quantity": f.quantity,
            "expiry_date": f.expiry_date.strftime("%Y-%m-%d")
        }
        for f in foods
    ]

    return jsonify(result), 200


# ------------------------------------------------------------
# 3) Update Food Listing
# ------------------------------------------------------------
@food_bp.route("/update/<int:food_id>", methods=["PUT"])
def update_food(food_id):
    food = FoodItem.query.get(food_id)
    if not food:
        return jsonify({"error": "Food item not found"}), 404

    data = request.json

    if "food_name" in data:
        food.name = data["food_name"]
    if "quantity" in data:
        food.quantity = data["quantity"]
    if "expiry_date" in data:
        food.expiry_date = datetime.strptime(data["expiry_date"], "%Y-%m-%d")

    db.session.commit()

    return jsonify({"message": "Food item updated successfully!"}), 200


# ------------------------------------------------------------
# 4) Delete Food Listing
# ------------------------------------------------------------
@food_bp.route("/delete/<int:food_id>", methods=["DELETE"])
def delete_food(food_id):
    food = FoodItem.query.get(food_id)
    if not food:
        return jsonify({"error": "Food item not found"}), 404

    db.session.delete(food)
    db.session.commit()

    return jsonify({"message": "Food deleted successfully"}), 200


# ------------------------------------------------------------
# 5) Get Nearby Requests (placeholder logic)
# ------------------------------------------------------------
@food_bp.route("/requests/nearby", methods=["GET"])
def get_nearby_requests():
    # For now, return all active requests.
    # Later you can filter using location or distance.
    requests = Request.query.filter_by(status="pending").all()

    result = [
        {
            "request_id": r.request_id,
            "receiver_id": r.receiver_id,
            "food_type": r.food_type,
            "quantity": r.quantity,
            "urgency_level": r.urgency_level
        }
        for r in requests
    ]

    return jsonify(result), 200


# ------------------------------------------------------------
# 6) Match Food Item + Request (Create Transaction)
# ------------------------------------------------------------
@food_bp.route("/match/<int:food_id>/<int:request_id>", methods=["POST"])
def match_food(food_id, request_id):
    food = FoodItem.query.get(food_id)
    req = Request.query.get(request_id)

    if not food:
        return jsonify({"error": "Food not found"}), 404
    if not req:
        return jsonify({"error": "Request not found"}), 404

    # Create transaction
    new_txn = Transaction(
        donor_id=food.donor_id,
        receiver_id=req.receiver_id,
        food_id=food_id,
        request_id=request_id,
        timestamp=datetime.now()
    )

    req.status = "fulfilled"

    db.session.add(new_txn)
    db.session.commit()

    return jsonify({"message": "Food matched & transaction created"}), 201


# ------------------------------------------------------------
# 7) View Donor Transactions
# ------------------------------------------------------------
@food_bp.route("/transactions/donor/<int:donor_id>", methods=["GET"])
def get_donor_transactions(donor_id):
    txns = Transaction.query.filter_by(donor_id=donor_id).all()

    result = [
        {
            "transaction_id": t.transaction_id,
            "receiver_id": t.receiver_id,
            "food_id": t.food_id,
            "request_id": t.request_id,
            "timestamp": t.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for t in txns
    ]

    return jsonify(result), 200
