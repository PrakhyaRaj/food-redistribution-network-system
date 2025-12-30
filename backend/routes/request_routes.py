from backend.models import db, Request, User, FoodItem, Transaction
from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.auth import roles_required
from backend.validation import (
    validate_request_data, ValidationError, handle_validation_error as validation_error_handler
)
from backend.notifications import NotificationService
from backend.services.matching_service import MatchingService
from backend.services.route_optimizer import RouteOptimizer
from backend.extensions import socketio

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
        
        # Emit real-time notification via Socket.IO
        request_data = {
            "request_id": new_request.request_id,
            "receiver_id": receiver_id,
            "food_type": new_request.food_type,
            "quantity": new_request.quantity,
            "urgency_level": new_request.urgency_level,
            "deadline": new_request.deadline.strftime("%Y-%m-%d %H:%M:%S") if new_request.deadline else None,
            "status": new_request.status,
            "created_at": new_request.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        socketio.emit('request_created', request_data)

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
        
        # Emit real-time update via Socket.IO
        request_data = {
            "request_id": req.request_id,
            "receiver_id": req.receiver_id,
            "food_type": req.food_type,
            "quantity": req.quantity,
            "urgency_level": req.urgency_level,
            "deadline": req.deadline.strftime("%Y-%m-%d %H:%M:%S") if req.deadline else None,
            "status": req.status,
            "created_at": req.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        socketio.emit('request_updated', request_data)

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

        # Emit real-time update via Socket.IO
        socketio.emit('request_cancelled', {
            "request_id": request_id,
            "message": "Request has been cancelled"
        })

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

        # Extract optional pickup_date from request
        pickup_date = None
        if data.get("pickup_date"):
            try:
                pickup_date = datetime.fromisoformat(data["pickup_date"])
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid pickup_date format, use ISO format"}), 400

        txn = Transaction(
            donor_id=donor.user_id,
            receiver_id=receiver_id,
            request_id=data.get("request_id"),
            food_id=food_id,
            quantity=getattr(food, 'quantity', None),  # Quantity from food item
            pickup_date=pickup_date or datetime.now(),  # Default to current time
            status="in_progress"
        )

        db.session.add(txn)
        db.session.commit()

        # Persist transaction to MongoDB for API reads with route optimization
        try:
            from backend.mongodb import mongo_service
            from backend.services.route_optimizer import RouteOptimizer
            route_data = None
            if donor and receiver and donor.location_lat and donor.location_long and receiver.location_lat and receiver.location_long:
                try:
                    route_result = RouteOptimizer.optimize_route(
                        donor_lat=donor.location_lat,
                        donor_long=donor.location_long,
                        receiver_lat=receiver.location_lat,
                        receiver_long=receiver.location_long,
                        quantity=max(1, int(getattr(food, 'quantity', 1))),
                        pickup_date=pickup_date  # Pass pickup_date for time window enforcement
                    )
                    if route_result.get('success'):
                        route_data = route_result
                except Exception as re:
                    print(f"⚠️ Route optimization failed (accept_food): {re}")

            if mongo_service and mongo_service.is_connected():
                print(f"🔵 Storing transaction {txn.txn_id} to MongoDB (accept_food)")
                mongo_service.store_transaction(
                    txn_id=txn.txn_id,
                    donor_id=txn.donor_id,
                    receiver_id=txn.receiver_id,
                    food_id=txn.food_id,
                    request_id=txn.request_id,
                    status=txn.status,
                    route_data=route_data,
                    quantity=getattr(txn, "quantity", None),
                    pickup_date=getattr(txn, "pickup_date", None)
                )
                print(f"✅ Transaction {txn.txn_id} stored to MongoDB (accept_food)")
            else:
                print(f"⚠️ MongoDB not connected in accept_food, skipping transaction storage")
        except Exception as e:
            print(f"❌ Failed to store transaction {txn.txn_id} in accept_food: {str(e)}")
            pass

        # Update transaction status from 'initiated' to 'in_progress'
        txn.status = 'in_progress'
        db.session.commit()
        print(f"✅ Transaction {txn.txn_id} status updated to: in_progress")

        # SYNC ANALYTICS AFTER TRANSACTION - NON-BLOCKING
        try:
            from backend.services.analytics_service import AnalyticsService
            AnalyticsService.sync_analytics_after_transaction(txn, food)
        except Exception as ae:
            print(f"⚠️ [ACCEPT] Analytics sync failed (non-blocking): {ae}")
            import traceback
            traceback.print_exc()

        # SEND REAL-TIME NOTIFICATION
        NotificationService.notify_food_accepted(
            transaction_id=txn.txn_id,
            donor_id=food.donor_id,
            receiver_id=receiver_id,
            food_id=food_id
        )

        # Log redistribution analytics with map-based distance
        try:
            from backend.mongodb import mongo_service
            from backend.services.route_optimizer import RouteOptimizer
            if mongo_service and mongo_service.is_connected():
                distance_km = None
                distance_source = None
                if donor and receiver:
                    osrm = RouteOptimizer._get_osrm_distance(
                        donor.location_lat, donor.location_long,
                        receiver.location_lat, receiver.location_long
                    )
                    if osrm and osrm.get('success'):
                        distance_km = osrm['distance_km']
                        distance_source = 'osrm'
                    else:
                        distance_km = RouteOptimizer._haversine_distance(
                            donor.location_lat, donor.location_long,
                            receiver.location_lat, receiver.location_long
                        )
                        distance_source = 'haversine'

                mongo_service.db.redistribution_analytics.insert_one({
                    "transaction_id": txn.txn_id,
                    "donor_id": donor.user_id,
                    "receiver_id": receiver_id,
                    "food_id": food_id,
                    "food_name": food.food_name,
                    "quantity_kg": food.quantity,
                    "distance_km": round(distance_km or 0, 2),
                    "distance_source": distance_source,
                    "donor_location": {"lat": donor.location_lat, "long": donor.location_long},
                    "receiver_location": {"lat": receiver.location_lat, "long": receiver.location_long},
                    "status": txn.status,
                    "created_at": datetime.utcnow()
                })
        except Exception as ae:
            print(f"⚠️ Analytics logging failed (accept_food): {ae}")

        return jsonify({
            "message": "Food accepted and transaction created",
            "transaction_id": txn.txn_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ========================================
# MATCHING & OPTIMIZATION ENDPOINTS
# ========================================

@request_bp.route("/<int:request_id>/find-matches", methods=["POST"])
@jwt_required()
@roles_required('receiver')
def find_matches_for_request(request_id):
    """
    Find matching food items for a receiver's request.
    Uses MatchingService to find best matches based on:
    - Food type similarity
    - Quantity availability
    - Expiry dates
    - Geographic proximity
    
    Returns matches with distance and route optimization
    """
    try:
        current_user = get_jwt_identity()
        req = Request.query.get(request_id)
        
        if not req:
            return jsonify({"success": False, "error": "Request not found"}), 404
        
        if req.receiver_id != int(current_user):
            return jsonify({"success": False, "error": "Unauthorized"}), 403
        
        # Find matches using MatchingService
        match_result = MatchingService.find_matches_for_request(request_id)
        
        if not match_result["success"]:
            return jsonify(match_result), 400
        
        # For each match, calculate route optimization
        matches_with_routes = []
        for match in match_result["matches"]:
            # Get receiver location
            receiver = User.query.get(req.receiver_id)
            
            # Optimize route from donor to receiver
            route_result = RouteOptimizer.optimize_route(
                donor_lat=match['donor_lat'],
                donor_long=match['donor_long'],
                receiver_lat=receiver.location_lat,
                receiver_long=receiver.location_long,
                quantity=req.quantity,
                pickup_date=req.deadline  # Use request deadline as pickup target time
            )
            
            if route_result['success']:
                match['route'] = route_result['route']
                match['metrics'] = route_result['metrics']
            
            matches_with_routes.append(match)
        
        # Update result with routes
        match_result["matches"] = matches_with_routes
        
        return jsonify(match_result), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error finding matches: {str(e)}"
        }), 500


@request_bp.route("/<int:request_id>/matches/<int:food_id>/create-transaction", methods=["POST"])
@jwt_required()
@roles_required('receiver')
def create_match_transaction(request_id, food_id):
    """
    Create a transaction from a matched request and food item.
    This finalizes the match and creates a transaction record.
    """
    try:
        current_user = get_jwt_identity()
        req = Request.query.get(request_id)
        
        if not req or req.receiver_id != int(current_user):
            return jsonify({"success": False, "error": "Unauthorized"}), 403
        
        # Log inputs for debugging
        print(f"🔍 CREATE_MATCH_TRANSACTION called: request_id={request_id}, food_id={food_id}, current_user={current_user}")
        req = Request.query.get(request_id)
        food = FoodItem.query.get(food_id)
        print(f"🔍 CREATE_MATCH_TRANSACTION: req={req}, food={food}")

        # Create transaction using MatchingService
        result = MatchingService.create_match_transaction(request_id, food_id)
        print(f"🔍 CREATE_MATCH_TRANSACTION result: {result}")

        if result.get("success"):
            # Send notification to both parties (non-blocking)
            try:
                food = FoodItem.query.get(food_id)
                NotificationService.notify_match_found(
                    request_id=request_id,
                    donor_id=food.donor_id,
                    receiver_id=current_user,
                    food_id=food_id
                )
            except Exception as e:
                print(f"⚠️ notify_match_found failed (non-blocking): {e}")

            return jsonify(result), 201
        else:
            # Return specific error to client
            return jsonify(result), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": f"Error creating transaction: {str(e)}"
        }), 500


@request_bp.route("/donor/<int:food_id>/find-requests", methods=["POST"])
@jwt_required()
@roles_required('donor')
def find_requests_for_food(food_id):
    """
    Find matching receiver requests for a donor's food item.
    Used when donor wants to see who needs their food.
    
    Returns requests sorted by priority (urgent + close = high priority)
    """
    try:
        current_user = get_jwt_identity()
        food = FoodItem.query.get(food_id)
        
        if not food or food.donor_id != int(current_user):
            return jsonify({"success": False, "error": "Unauthorized"}), 403
        
        # Find matching requests using MatchingService
        match_result = MatchingService.find_matches_for_donor(current_user, food_id)
        
        if not match_result["success"]:
            return jsonify(match_result), 400
        
        # For each match, calculate route optimization
        matches_with_routes = []
        for match in match_result["matches"]:
            # Get donor location
            donor = User.query.get(current_user)
            
            # Optimize route from donor to receiver
            from datetime import datetime, timedelta
            # Use food expiry date as pickup deadline (delivery should happen before expiry)
            food_item = FoodItem.query.get(food_id)
            pickup_deadline = datetime.combine(food_item.expiry_date, datetime.min.time()) if food_item and food_item.expiry_date else None
            
            route_result = RouteOptimizer.optimize_route(
                donor_lat=donor.location_lat,
                donor_long=donor.location_long,
                receiver_lat=match['receiver_lat'],
                receiver_long=match['receiver_long'],
                quantity=match['quantity_needed'],
                pickup_date=pickup_deadline  # Use food expiry as time constraint
            )
            
            if route_result['success']:
                match['route'] = route_result['route']
                match['metrics'] = route_result['metrics']
            
            matches_with_routes.append(match)
        
        # Update result with routes
        match_result["matches"] = matches_with_routes
        
        return jsonify(match_result), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error finding requests: {str(e)}"
        }), 500
