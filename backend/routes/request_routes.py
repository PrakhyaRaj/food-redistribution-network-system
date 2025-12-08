from backend.models import db, Request, User, FoodItem, Transaction
from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.auth import roles_required
from backend.validation import (
    validate_request_data, ValidationError, handle_validation_error as validation_error_handler
)
from backend.notifications import NotificationService

request_bp = Blueprint("request_bp", __name__, url_prefix="/requests")

# Register error handler
@request_bp.errorhandler(ValidationError)
def handle_request_validation_error(error):  
    return validation_error_handler(error) 

#create all requests
@request_bp.route("/add_request", methods=["POST"])
@jwt_required()
@roles_required('receiver')
def add_request():
    try:
        data = request.json or {}
        receiver_id = get_jwt_identity()

        validated_data = validate_request_data(data)

        new_request = Request(
            receiver_id=receiver_id,
            food_type=validated_data['food_type'],
            quantity=validated_data['quantity'],
            urgency_level=validated_data['urgency_level'],
            deadline=validated_data['deadline']
        )

        db.session.add(new_request)
        db.session.commit()

        # SEND REAL-TIME NOTIFICATION 
        NotificationService.notify_new_request(new_request.request_id, receiver_id)

        return jsonify({
            "success": True,
            "message": "Request submitted successfully",
            "request_id": new_request.request_id
        }), 201
        
    except ValidationError:
        raise
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Failed to create request due to server error"
        }), 500

#show all requests
@request_bp.route("/all", methods=["GET"])
@jwt_required()
@roles_required('donor', 'receiver')
def get_all_requests():
    try:
        requests = Request.query.all()
        result = [
            {
                "request_id": r.request_id,
                "receiver_id": r.receiver_id,
                "food_type": r.food_type,
                "quantity": r.quantity,
                "urgency_level": r.urgency_level,
                "deadline": r.deadline.strftime("%Y-%m-%d %H:%M:%S") if r.deadline else None,
                "status": r.status,
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for r in requests
        ]
        return jsonify({"success": True, "requests": result}), 200

    except Exception:
        return jsonify({
            "success": False,
            "error": "Failed to fetch requests"
        }), 500


#update or modify a req
@request_bp.route("/update/<int:request_id>", methods=["PUT"])
@jwt_required()
@roles_required('receiver')
def update_request(request_id):
    try:
        req = Request.query.get(request_id)
        if not req:
            return jsonify({"success": False, "error": "Request not found"}), 404

        current_user = get_jwt_identity()

        if req.receiver_id != int(current_user):
            return jsonify({
                "success": False,
                "error": "Unauthorized – you can only update your own requests"
            }), 403

        data = request.json or {}

        # Allowed updates
        if "quantity" in data:
            try:
                quantity = int(data["quantity"])
                if quantity <= 0:
                    raise ValidationError("Quantity must be positive", "quantity")
                req.quantity = quantity
            except Exception:
                raise ValidationError("Quantity must be a valid number", "quantity")

        if "urgency_level" in data:
            if data["urgency_level"] not in ["low", "medium", "high"]:
                raise ValidationError("Urgency level must be low, medium, or high", "urgency_level")
            req.urgency_level = data["urgency_level"]

        if "deadline" in data:
            try:
                deadline = datetime.strptime(data["deadline"], "%Y-%m-%d %H:%M:%S")
                req.deadline = deadline
            except ValueError:
                raise ValidationError("Deadline must be in YYYY-MM-DD HH:MM:SS format", "deadline")

        if "status" in data:
            req.status = data["status"]

        db.session.commit()

        return jsonify({"success": True, "message": "Request updated successfully"}), 200

    except ValidationError:
        raise
    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Failed to update request"
        }), 500


#cancel request
@request_bp.route("/cancel/<int:request_id>", methods=["DELETE"])
@jwt_required()
@roles_required('receiver')
def cancel_request(request_id):
    try:
        req = Request.query.get(request_id)
        if not req:
            return jsonify({"success": False, "error": "Request not found"}), 404

        current_user = get_jwt_identity()
        if req.receiver_id != int(current_user):
            return jsonify({
                "success": False,
                "error": "Unauthorized – you can only delete your own requests"
            }), 403

        db.session.delete(req)
        db.session.commit()

        return jsonify({"success": True, "message": "Request cancelled successfully"}), 200

    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Failed to cancel request"
        }), 500

#see all available donations- food items
@request_bp.route("/available", methods=["GET"])
@jwt_required()
@roles_required('donor', 'receiver')
def available_foods():
    try:
        foods = FoodItem.query.filter_by(status="available").all()
        result = [
            {
                "food_id": f.food_id,
                "name": f.name,
                "quantity": f.quantity,
                "expiry_date": f.expiry_date.strftime("%Y-%m-%d") if f.expiry_date else None
            }
            for f in foods
        ]
        return jsonify({"success": True, "foods": result}), 200

    except Exception:
        return jsonify({
            "success": False,
            "error": "Failed to fetch available food items"
        }), 500


#accept a donation - creates a transaction
@request_bp.route("/accept/<int:food_id>", methods=["POST"])
@jwt_required()
@roles_required('receiver')
def accept_food(food_id):
    try:
        data = request.json or {}
        receiver_id = get_jwt_identity()

        receiver = User.query.get(receiver_id)
        if not receiver:
            return jsonify({"error": "Receiver not found"}), 404

        food = FoodItem.query.get(food_id)
        if not food:
            return jsonify({"error": "Food item not found"}), 404

        donor = User.query.get(food.donor_id)

        txn = Transaction(
            donor_id=donor.user_id,
            receiver_id=receiver_id,
            request_id=data.get("request_id"),
            food_id=food_id,
            status="in_progress"
        )

        db.session.add(txn)
        db.session.commit()

        # SEND REAL-TIME NOTIFICATION
        NotificationService.notify_food_accepted(
            transaction_id=txn.txn_id,
            donor_id=food.donor_id,
            receiver_id=receiver_id,
            food_id=food_id
        )

        return jsonify({
            "message": "Food accepted and transaction created",
            "transaction_id": txn.txn_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500