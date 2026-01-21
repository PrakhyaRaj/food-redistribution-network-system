from flask import Blueprint, request, jsonify, current_app
import traceback
from backend.models import Request, Transaction, db, FoodItem, User
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.auth import roles_required
from backend.validation import (
    validate_food_data, ValidationError, handle_validation_error as validation_error_handler
)
from backend.notifications import NotificationService
from backend.extensions import socketio

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
        
        # Emit real-time notification via Socket.IO
        food_data = {
            "food_id": new_food.food_id,
            "donor_id": donor_id,
            "name": new_food.name,
            "quantity": new_food.quantity,
            "expiry_date": new_food.expiry_date.strftime("%Y-%m-%d") if new_food.expiry_date else None,
            "status": new_food.status or "available"
        }
        socketio.emit('food_added', food_data)
        
        return jsonify({
            "success": True,
            "message": "Food item added successfully!", 
            "food_id": new_food.food_id
        }), 201
        
    except ValidationError:
        raise
    except Exception as e:
        # Log full traceback for debugging
        traceback.print_exc()
        current_app.logger.error(f"Add food error: {str(e)}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": f"Failed to add food item due to server error: {str(e)}"
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
        
        # Emit real-time update via Socket.IO
        food_data = {
            "food_id": food.food_id,
            "donor_id": food.donor_id,
            "name": food.name,
            "quantity": food.quantity,
            "expiry_date": food.expiry_date.strftime("%Y-%m-%d") if food.expiry_date else None,
            "status": food.status or "available"
        }
        socketio.emit('food_updated', food_data)
        
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
        print(f"🔍 MATCH_FOOD: food_id={food_id}, request_id={request_id}")
        food = FoodItem.query.get(food_id)
        req = Request.query.get(request_id)
        print(f"🔍 MATCH_FOOD: food={food}, req={req}")

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

        # Create transaction with quantity and pickup_date
        new_txn = Transaction(
            donor_id=food.donor_id,
            receiver_id=req.receiver_id,
            food_id=food_id,
            request_id=request_id,
            quantity=req.quantity,  # Use request quantity
            pickup_date=datetime.now(),  # Default to current time
            status="initiated"
        )

        # Update related statuses
        req.status = "completed"
        food.status = "in_transit"

        db.session.add(new_txn)
        db.session.commit()

        # Compute route data immediately
        print(f"🗺️ [MATCH] Computing route for transaction {new_txn.txn_id}...")
        route_data = None
        try:
            from .transaction_routes import compute_route_data
            donor_user = User.query.get(food.donor_id)
            receiver_user = User.query.get(req.receiver_id)
            route_data = compute_route_data(donor_user, receiver_user)
            print(f"🗺️ [MATCH] Route data computed: {route_data}")
        except Exception as re:
            print(f"⚠️ [MATCH] Route optimization failed (non-blocking): {re}")
            import traceback
            traceback.print_exc()

        # Store transaction in MongoDB with route_data
        try:
            print(f"🗺️ [MATCH] Storing transaction in MongoDB...")
            from backend.mongodb import mongo_service
            mongo_service.store_transaction(
                txn_id=new_txn.txn_id,
                donor_id=food.donor_id,
                receiver_id=req.receiver_id,
                food_id=food_id,
                request_id=request_id,
                status="initiated",
                route_data=route_data,
                quantity=getattr(new_txn, "quantity", None),
                pickup_date=getattr(new_txn, "pickup_date", None)
            )
            print(f"✅ [MATCH] Transaction stored in MongoDB with route_data")
        except Exception as me:
            print(f"⚠️ [MATCH] MongoDB storage failed (non-blocking): {me}")
            import traceback
            traceback.print_exc()

        # SYNC ANALYTICS AFTER TRANSACTION - NON-BLOCKING
        print(f"📊 [MATCH] About to sync analytics for transaction {new_txn.txn_id}...")
        try:
            from backend.services.analytics_service import AnalyticsService
            print(f"📊 [MATCH] AnalyticsService imported successfully")
            AnalyticsService.sync_analytics_after_transaction(new_txn, food)
            print(f"✅ [MATCH] Analytics sync completed for transaction {new_txn.txn_id}")
        except Exception as ae:
            print(f"❌ [MATCH] Analytics sync failed (non-blocking): {ae}")
            import traceback
            traceback.print_exc()

        # SEND REAL-TIME NOTIFICATION - NON-BLOCKING
        try:
            NotificationService.notify_food_matched(
                food_id=food_id,
                request_id=request_id,
                donor_id=food.donor_id,
                receiver_id=req.receiver_id
            )
        except Exception as notif_error:
            # Notification failed but transaction succeeded - don't block
            print(f"⚠️  Notification creation failed (non-critical): {notif_error}")
            current_app.logger.warning(f"Notification error: {notif_error}")

        return jsonify({
            "success": True,
            "message": "Food matched & transaction created", 
            "transaction_id": new_txn.txn_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Match food error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Failed to match food due to server error: {str(e)}"
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