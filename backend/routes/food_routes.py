from flask import Blueprint, request, jsonify
from backend.models import Request, Transaction, db, FoodItem
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.auth import roles_required
from backend.validation import (
    validate_food_data, ValidationError, handle_validation_error as validation_error_handler
)
from backend.notifications import NotificationService

food_bp = Blueprint("food_bp", __name__, url_prefix="/food")

# Register error handler
@food_bp.errorhandler(ValidationError)
def handle_food_validation_error(error):  
    return validation_error_handler(error)  

@food_bp.route("/add", methods=["POST"])
@jwt_required()
@roles_required('donor')
def add_food():
    try:
        data = request.json or {}
        donor_id = get_jwt_identity()

        # Validate food data
        validated_data = validate_food_data(data)

        new_food = FoodItem(
            donor_id=donor_id,
            name=validated_data['food_name'],
            quantity=validated_data['quantity'],
            expiry_date=validated_data['expiry_date']
        )
        
        db.session.add(new_food)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Food item added successfully!", 
            "food_id": new_food.food_id
        }), 201
        
    except ValidationError:
        raise
    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Failed to add food item due to server error"
        }), 500



# ------------------------------------------------------------
# 2) Get All Foods Donated by Logged-In Donor
# ------------------------------------------------------------
@food_bp.route("/my/<int:donor_id>", methods=["GET"])
@jwt_required()
@roles_required('donor', 'receiver')
def get_my_food(donor_id):
    try:
        current_user = get_jwt_identity()
        foods = FoodItem.query.filter_by(donor_id=donor_id).all()

        result = [
            {
                "id": f.food_id,
                "donor_id": f.donor_id,
                "food_name": f.name,
                "quantity": f.quantity,
                "expiry_date": f.expiry_date.strftime("%Y-%m-%d") if f.expiry_date else None,
                "status": f.status or "available"
            }
            for f in foods
        ]

        return jsonify(result), 200
        
    except Exception:
        return jsonify({
            "success": False,
            "error": "Failed to load food items"
        }), 500



# ------------------------------------------------------------
# 3) Update Food Listing
# ------------------------------------------------------------
@food_bp.route("/update/<int:food_id>", methods=["PUT"])
@jwt_required()
@roles_required('donor')
def update_food(food_id):
    try:
        food = FoodItem.query.get(food_id)
        if not food:
            return jsonify({
                "success": False,
                "error": "Food item not found"
            }), 404

        current_user = get_jwt_identity()
        if int(current_user) != food.donor_id:
            return jsonify({
                "success": False,
                "error": "Unauthorized - you can only update your own food items"
            }), 403

        data = request.json or {}
        
        # Validate input data
        if "food_name" in data or "name" in data:
            food_name = data.get("food_name") or data.get("name")
            if not food_name or len(food_name.strip()) < 2:
                raise ValidationError("Food name must be at least 2 characters", "food_name")
            food.name = food_name.strip()
            
        if "quantity" in data:
            try:
                quantity = int(data["quantity"])
                if quantity <= 0:
                    raise ValidationError("Quantity must be a positive number", "quantity")
                food.quantity = quantity
            except (ValueError, TypeError):
                raise ValidationError("Quantity must be a valid number", "quantity")
                
        if "expiry_date" in data:
            try:
                expiry_date = datetime.strptime(data["expiry_date"], "%Y-%m-%d").date()
                if expiry_date < datetime.now().date():
                    raise ValidationError("Expiry date cannot be in the past", "expiry_date")
                food.expiry_date = expiry_date
            except ValueError:
                raise ValidationError("Expiry date must be in YYYY-MM-DD format", "expiry_date")

        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Food item updated successfully!"
        }), 200
        
    except ValidationError:
        raise
    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Failed to update food item due to server error"
        }), 500



# ------------------------------------------------------------
# 4) Delete Food Listing
# ------------------------------------------------------------
@food_bp.route("/delete/<int:food_id>", methods=["DELETE"])
@jwt_required()  
@roles_required('donor')
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
@jwt_required()  
@roles_required('donor', 'receiver')
def get_nearby_requests():
    try:
        print("🔍 GET_NEARBY_REQUESTS called")
        
        requests = Request.query.filter_by(status="pending").all()

        result = [
            {
                "id": r.request_id,
                "receiver_id": r.receiver_id,
                "food_type": r.food_type,
                "quantity": r.quantity,
                "urgency_level": r.urgency_level,
                "deadline": r.deadline.isoformat() if r.deadline else None,
                "status": r.status or "pending"
            }
            for r in requests
        ]

        print(f"✅ GET_NEARBY_REQUESTS success, found {len(result)} requests")
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ GET_NEARBY_REQUESTS error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------------------
# 6) Match Food Item + Request (Create Transaction)
# ------------------------------------------------------------
@food_bp.route("/match/<int:food_id>/<int:request_id>", methods=["POST"])
@jwt_required()
@roles_required('donor')
def match_food(food_id, request_id):
    try:
        food = FoodItem.query.get(food_id)
        req = Request.query.get(request_id)

        if not food:
            return jsonify({
                "success": False,
                "error": "Food not found"
            }), 404
        if not req:
            return jsonify({
                "success": False,
                "error": "Request not found"
            }), 404

        current_user = get_jwt_identity()
        if int(current_user) != food.donor_id:
            return jsonify({
                "success": False,
                "error": "Unauthorized - you can only match your own food items"
            }), 403

        # Create transaction
        new_txn = Transaction(
            donor_id=food.donor_id,
            receiver_id=req.receiver_id,
            food_id=food_id,
            request_id=request_id,
            status="claimed"
        )

        # Update related statuses
        req.status = "completed"
        food.status = "in_transit"

        db.session.add(new_txn)
        db.session.commit()

        # SEND REAL-TIME NOTIFICATION - ADD THIS
        NotificationService.notify_food_matched(
            food_id=food_id,
            request_id=request_id,
            donor_id=food.donor_id,
            receiver_id=req.receiver_id
        )

        return jsonify({
            "success": True,
            "message": "Food matched & transaction created", 
            "transaction_id": new_txn.txn_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Failed to match food due to server error"
        }), 500


# ------------------------------------------------------------
# 7) View Donor Transactions
# ------------------------------------------------------------
@food_bp.route("/transactions/donor/<int:donor_id>", methods=["GET"])
@jwt_required()  
@roles_required('donor')
def get_donor_transactions(donor_id):
    txns = Transaction.query.filter_by(donor_id=donor_id).all()

    result = [
        {
            "transaction_id": t.txn_id,
            "receiver_id": t.receiver_id,
            "food_id": t.food_id,
            "request_id": t.request_id,
            "timestamp": t.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for t in txns
    ]

    return jsonify(result), 200