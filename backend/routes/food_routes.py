from flask import Blueprint, request, jsonify
from models import db, FoodItem
from datetime import datetime

food_bp = Blueprint("food_bp", __name__)

@food_bp.route("/add_food", methods=["POST"])
def add_food():
    data = request.json
    new_food = FoodItem(
        donor_id=data["donor_id"],
        food_name=data["food_name"],
        quantity=data["quantity"],
        expiry_date=datetime.strptime(data["expiry_date"], "%Y-%m-%d")
    )
    db.session.add(new_food)
    db.session.commit()
    return jsonify({"message": "Food item added successfully!"}), 201

@food_bp.route("/available_foods", methods=["GET"])
def available_foods():
    foods = FoodItem.query.filter_by(status="available").all()
    return jsonify([{
        "food_id": f.food_id,
        "name": f.food_name,
        "quantity": f.quantity,
        "expiry_date": str(f.expiry_date)
    } for f in foods])
