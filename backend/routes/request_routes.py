from models import db, Request, User, FoodItem, Transaction
from flask import Blueprint, request, jsonify

request_bp = Blueprint("request_bp", __name__, url_prefix="/requests")


#create new request
@request_bp.route("/add_request", methods=["POST"])
def add_request():
    data = request.json

    receiver_id = data.get("receiver_id")
    food_type = data.get("food_type")
    quantity = data.get("quantity")
    urgency_level = data.get("urgency_level")
    deadline_str = data.get("deadline")

    # Validate user exists
    receiver = User.query.get(receiver_id)
    if not receiver:
        return jsonify({"error": "Receiver user not found"}), 404

    # Parse deadline if sent
    deadline = None
    if deadline_str:
        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return jsonify({"error": "Invalid deadline format. Use YYYY-MM-DD HH:MM:SS"}), 400

    new_request = Request(
        receiver_id=receiver_id,
        food_type=food_type,
        quantity=quantity,
        urgency_level=urgency_level,
        deadline=deadline
    )

    db.session.add(new_request)
    db.session.commit()

    return jsonify({
        "message": "Request submitted successfully",
        "request_id": new_request.request_id
    }), 201


#show all requests
@request_bp.route("/all", methods=["GET"])
def get_all_requests():
    requests = Request.query.all()

    result = []
    for r in requests:
        result.append({
            "request_id": r.request_id,
            "receiver_id": r.receiver_id,
            "food_type": r.food_type,
            "quantity": r.quantity,
            "urgency_level": r.urgency_level,
            "deadline": r.deadline.strftime("%Y-%m-%d %H:%M:%S") if r.deadline else None,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(r, "created_at") else None
        })

    return jsonify(result), 200


#update or modify a req
@request_bp.route("/update/<int:request_id>", methods=["PUT"])
def update_request(request_id):
    req = Request.query.get(request_id)
    if not req:
        return jsonify({"error": "Request not found"}), 404

    data = request.json

    req.quantity = data.get("quantity", req.quantity)
    req.status = data.get("status", req.status)
    req.urgency_level = data.get("urgency_level", req.urgency_level)

    db.session.commit()

    return jsonify({"message": "Request updated successfully"}), 200


#cancel request
@request_bp.route("/cancel/<int:request_id>", methods=["DELETE"])
def cancel_request(request_id):
    req = Request.query.get(request_id)
    if not req:
        return jsonify({"error": "Request not found"}), 404

    db.session.delete(req)
    db.session.commit()

    return jsonify({"message": "Request cancelled successfully"}), 200

#see all available donations- food items
@request_bp.route("/available", methods=["GET"])
def available_foods():
    foods = FoodItem.query.filter_by(status="available").all()
    return jsonify([{
        "food_id": f.food_id,
        "name": f.name,
        "quantity": f.quantity,
        "expiry_date": str(f.expiry_date)
    } for f in foods])


#accept a donation - creates a transaction
@request_bp.route("/accept/<int:food_id>", methods=["POST"])
def accept_food(food_id):
    data = request.json
    receiver_id = data.get("receiver_id")
    request_id = data.get("request_id")

    receiver = User.query.get(receiver_id)
    if not receiver:
        return jsonify({"error": "Receiver not found"}), 404

    food = FoodItem.query.get(food_id)
    if not food:
        return jsonify({"error": "Food item not found"}), 404

    donor = User.query.get(food.donor_id)

    # Create Transaction
    txn = Transaction(
        donor_id=donor.user_id,
        receiver_id=receiver.user_id,
        request_id=request_id,
        food_id=food_id,
        status="accepted"
    )

    db.session.add(txn)
    db.session.commit()

    return jsonify({
        "message": "Food accepted and transaction created",
        "transaction_id": txn.txn_id
    }), 201


