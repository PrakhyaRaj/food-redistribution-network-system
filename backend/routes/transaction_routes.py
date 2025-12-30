# backend/routes/transaction_routes.py

from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from backend.models import db, Transaction, FoodItem, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.auth import roles_required
from backend.extensions import socketio
from backend.services.notification_service import NotificationService

transaction_bp = Blueprint("transaction_bp", __name__, url_prefix="/transactions")

def create_transaction_data(donor_id, receiver_id, food_id, quantity=None, pickup_date=None):
    """Helper function to create transaction data"""
    return {
        "donor_id": donor_id,
        "receiver_id": receiver_id,
        "food_id": food_id,
        "quantity": quantity,  # Optional: quantity of food in transaction
        "pickup_date": pickup_date or datetime.now(timezone.utc),  # Default to current time
        "date": datetime.now(timezone.utc),
        # Use enum-compatible initial status
        "status": "initiated"
    }


def compute_route_data(donor: User, receiver: User):
    """Compute route data using OSRM when possible, fall back to haversine."""
    try:
        from backend.services.route_optimizer import RouteOptimizer

        print(f"🗺️ [ROUTE] Starting route computation...")
        print(f"🗺️ [ROUTE] Donor: {donor}, Receiver: {receiver}")
        
        if not donor or not receiver:
            print(f"❌ [ROUTE] Missing donor or receiver")
            return None
            
        if not all([
            donor.location_lat,
            donor.location_long,
            receiver.location_lat,
            receiver.location_long,
        ]):
            print(f"❌ [ROUTE] Missing location coordinates")
            print(f"   Donor lat/long: {donor.location_lat}, {donor.location_long}")
            print(f"   Receiver lat/long: {receiver.location_lat}, {receiver.location_long}")
            return None

        print(f"🗺️ [ROUTE] Calling RouteOptimizer.optimize_route...")
        try:
            route_result = RouteOptimizer.optimize_route(
                donor_lat=donor.location_lat,
                donor_long=donor.location_long,
                receiver_lat=receiver.location_lat,
                receiver_long=receiver.location_long,
                quantity=1,
                pickup_date=pickup_date  # Pass pickup_date for time window enforcement
            )
            print(f"🗺️ [ROUTE] Optimizer returned: {route_result}")
            if route_result and route_result.get("success") and route_result.get("route"):
                print(f"✅ [ROUTE] Using full optimization result")
                return route_result
            else:
                print(f"⚠️ [ROUTE] Optimization result invalid, using fallback")
        except Exception as e:
            print(f"⚠️ [ROUTE] Route optimization failed (primary): {e}")
            import traceback
            traceback.print_exc()

        # Fallback lightweight estimate
        print(f"🗺️ [ROUTE] Using haversine fallback...")
        try:
            distance_km = RouteOptimizer._haversine_distance(
                donor.location_lat,
                donor.location_long,
                receiver.location_lat,
                receiver.location_long,
            )
            estimated_time_hours = round(distance_km / 35.0, 2) if distance_km is not None else 0
            fallback_result = {
                "success": True,
                "route": {
                    "total_distance_km": distance_km,
                    "estimated_time_hours": estimated_time_hours,
                    "vehicle_recommendation": "auto",
                    "distance_source": "haversine",
                },
                "metrics": {
                    "fuel_consumed_liters": 0,
                    "carbon_saved_kg": 0,
                    "efficiency_score": 0,
                    "meals_impacted": 0,
                },
            }
            print(f"✅ [ROUTE] Haversine fallback computed: {distance_km:.2f}km")
            return fallback_result
        except Exception as e:
            print(f"❌ [ROUTE] Haversine fallback failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    except Exception as e:
        print(f"❌ [ROUTE] Route computation error: {e}")
        import traceback
        traceback.print_exc()
        return None


# create new transaction
@transaction_bp.route("/create", methods=["POST"])
@jwt_required()
@roles_required('donor')
def create_transaction():
    data = request.get_json()
    required_fields = ["donor_id", "receiver_id", "food_id"]
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    food_item = FoodItem.query.get(data["food_id"])
    if not food_item:
        return jsonify({"error": "Food item not found"}), 404

    if food_item.status != "available":
        return jsonify({"error": "Food item already claimed"}), 400

    # Extract optional quantity and pickup_date
    quantity = data.get("quantity")
    pickup_date = None
    if data.get("pickup_date"):
        try:
            pickup_date = datetime.fromisoformat(data["pickup_date"])
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid pickup_date format, use ISO format"}), 400

    transaction = Transaction(**create_transaction_data(
        data["donor_id"], 
        data["receiver_id"], 
        data["food_id"],
        quantity=quantity,
        pickup_date=pickup_date
    ))

    # Mark food as in_transit (enum-compatible) and persist transaction
    try:
        food_item.status = "in_transit"
    except Exception:
        # leave existing status if assignment fails
        pass
    db.session.add(transaction)
    db.session.commit()

    # Try to persist transaction (and route optimization) to MongoDB (non-blocking)
    route_data = None
    try:
        from backend.mongodb import mongo_service

        print(f"🗺️ [TRANSACTION] Fetching donor and receiver for route computation...")
        donor = User.query.get(data["donor_id"])
        receiver = User.query.get(data["receiver_id"])
        print(f"🗺️ [TRANSACTION] Donor: {donor.name if donor else 'None'}, Receiver: {receiver.name if receiver else 'None'}")
        
        route_data = compute_route_data(donor, receiver)
        print(f"🗺️ [TRANSACTION] Route data computed: {route_data is not None}")
        if route_data:
            print(f"🗺️ [TRANSACTION] Route data keys: {route_data.keys()}")
            if route_data.get('route'):
                print(f"🗺️ [TRANSACTION] Route details: {route_data['route']}")

        if mongo_service and mongo_service.is_connected():
            print(f"🗺️ [TRANSACTION] MongoDB connected, storing transaction...")
            try:
                if route_data:
                    print(f"🗺️ [TRANSACTION] Storing route optimization...")
                    mongo_service.store_route_optimization(None, [], route_data)
                    print(f"✅ [TRANSACTION] Route optimization stored")
            except Exception as e:
                print(f"⚠️ Failed to store route optimization: {e}")
                import traceback
                traceback.print_exc()

            print(f"🗺️ [TRANSACTION] Storing transaction with route_data...")
            mongo_service.store_transaction(
                txn_id=transaction.txn_id,
                donor_id=transaction.donor_id,
                receiver_id=transaction.receiver_id,
                food_id=transaction.food_id,
                request_id=getattr(transaction, 'request_id', None),
                status=transaction.status,
                route_data=route_data,
                quantity=getattr(transaction, 'quantity', None),
                pickup_date=getattr(transaction, 'pickup_date', None)
            )
            print(f"✅ [TRANSACTION] Transaction stored in MongoDB with route_data")
        else:
            print(f"❌ [TRANSACTION] MongoDB not connected")
    except Exception as e:
        print(f"⚠️ Mongo/route storage skipped: {e}")
        import traceback
        traceback.print_exc()

    # Emit real-time notification via Socket.IO AND store in MongoDB
    transaction_data = format_transaction_response(transaction)
    
    # Send notifications to both donor and receiver
    donor_notification = {
        "type": "transaction_created",
        "title": "Transaction Created",
        "message": f"Your food item has been matched with a request",
        "transaction_id": transaction.txn_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "unread"
    }
    receiver_notification = {
        "type": "transaction_created",
        "title": "Food Match Found",
        "message": f"A donor has matched food with your request",
        "transaction_id": transaction.txn_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "unread"
    }
    
    print(f"💬 [TRANSACTION] About to send notifications...")
    print(f"💬 [TRANSACTION] Donor ID: {data['donor_id']}, Receiver ID: {data['receiver_id']}")
    
    # Store notifications to MongoDB
    NotificationService.send_and_store(data["donor_id"], donor_notification)
    NotificationService.send_and_store(data["receiver_id"], receiver_notification)
    
    print(f"💬 [TRANSACTION] Notifications sent, now emitting Socket.IO events...")
    
    # Also emit Socket.IO events
    socketio.emit('transaction_created', transaction_data, room=f'user_{data["donor_id"]}')
    socketio.emit('transaction_created', transaction_data, room=f'user_{data["receiver_id"]}')
    socketio.emit('transaction_created', transaction_data)
    
    # Log redistribution analytics
    try:
        from backend.mongodb import mongo_service
        if mongo_service and mongo_service.is_connected():
            # Get user information for analytics
            donor = User.query.get(data['donor_id'])
            receiver = User.query.get(data['receiver_id'])
            food = FoodItem.query.get(data['food_id'])
            
            if donor and receiver and food:
                # Calculate distance between donor and receiver using OSRM if available
                from backend.services.route_optimizer import RouteOptimizer
                distance_km = None
                distance_source = None

                try:
                    # Prefer previously computed route_data if available
                    if 'route' in (route_data or {}):
                        distance_km = route_data['route'].get('total_distance_km')
                        distance_source = route_data['route'].get('distance_source')

                    # If not available, try OSRM directly
                    if distance_km is None:
                        osrm_result = RouteOptimizer._get_osrm_distance(
                            donor.location_lat, donor.location_long,
                            receiver.location_lat, receiver.location_long
                        )
                        if osrm_result and osrm_result.get('success'):
                            distance_km = osrm_result['distance_km']
                            distance_source = 'osrm'

                    # Fallback to haversine
                    if distance_km is None:
                        distance_km = RouteOptimizer._haversine_distance(
                            donor.location_lat, donor.location_long,
                            receiver.location_lat, receiver.location_long
                        )
                        distance_source = 'haversine'
                except Exception:
                    # Final safety fallback
                    distance_km = RouteOptimizer._haversine_distance(
                        donor.location_lat, donor.location_long,
                        receiver.location_lat, receiver.location_long
                    )
                    distance_source = 'haversine'
                
                # Log to MongoDB analytics
                mongo_service.db.redistribution_analytics.insert_one({
                    "transaction_id": transaction.txn_id,
                    "donor_id": data['donor_id'],
                    "receiver_id": data['receiver_id'],
                    "food_id": data['food_id'],
                    "food_name": food.food_name,
                    "quantity_kg": food.quantity,
                    "distance_km": round(distance_km, 2),
                    "distance_source": distance_source,
                    "donor_location": {
                        "lat": donor.location_lat,
                        "long": donor.location_long
                    },
                    "receiver_location": {
                        "lat": receiver.location_lat,
                        "long": receiver.location_long
                    },
                    "status": transaction.status,
                    "created_at": datetime.now(timezone.utc)
                })
                print(f"✅ Analytics logged: Distance={distance_km:.2f}km")
    except Exception as e:
        print(f"⚠️ Analytics logging failed: {e}")
    
    return jsonify({
        "message": "Transaction created successfully",
        "transaction_id": transaction.txn_id
    }), 201

def store_transaction_in_mongodb(transaction):
    """Helper function to store transaction in MongoDB"""
    try:
        from backend.mongodb import mongo_service
        if mongo_service and mongo_service.is_connected():
            mongo_service.store_transaction(
                txn_id=transaction.txn_id,
                donor_id=transaction.donor_id,
                receiver_id=transaction.receiver_id,
                food_id=transaction.food_id,
                request_id=getattr(transaction, 'request_id', None),
                status=transaction.status,
                route_data=None,
                quantity=getattr(transaction, 'quantity', None),
                pickup_date=getattr(transaction, 'pickup_date', None)
            )
    except Exception as e:
        print(f"Error storing transaction in MongoDB: {e}")


def format_transaction_response(transaction):
    """Helper to format transaction data for API responses"""
    return {
        "txn_id": transaction.txn_id,
        "donor_id": transaction.donor_id,
        "receiver_id": transaction.receiver_id,
        "food_id": transaction.food_id,
        "food_name": getattr(transaction.food, 'name', None) if hasattr(transaction, 'food') else None,
        "quantity": getattr(transaction, 'quantity', None),
        "pickup_date": transaction.pickup_date.isoformat() if getattr(transaction, 'pickup_date', None) else None,
        "date": transaction.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "status": transaction.status
    }

@transaction_bp.route("/all", methods=["GET"])
@jwt_required()
@roles_required('donor', 'receiver')
def get_all_transactions():
    transactions = Transaction.query.order_by(Transaction.created_at.desc()).all()
    return jsonify([format_transaction_response(txn) for txn in transactions]), 200


@transaction_bp.route("/user/<int:user_id>", methods=["GET"])
@jwt_required()
@roles_required('donor', 'receiver')
def get_user_transactions(user_id):
    transactions = Transaction.query.filter(
        (Transaction.donor_id == user_id) | (Transaction.receiver_id == user_id)
    ).order_by(Transaction.created_at.desc()).all()

    if not transactions:
        return jsonify({"message": "No transactions found for this user"}), 404

    return jsonify([format_transaction_response(txn) for txn in transactions]), 200


@transaction_bp.route("/update/<int:txn_id>", methods=["PUT"])
@jwt_required()
@roles_required('donor', 'receiver')
def update_transaction_status(txn_id):
    data = request.get_json()
    if not data or "status" not in data:
        return jsonify({"error": "Status is required"}), 400

    txn = Transaction.query.get(txn_id)
    if not txn:
        return jsonify({"error": "Transaction not found"}), 404

    # Map friendly statuses to enum-compatible values
    status_map = {
        "delivered": "in_progress",
        "received": "completed",
        "completed": "completed",
        "in_progress": "in_progress",
        "initiated": "initiated",
        "cancelled": "cancelled"
    }

    new_status_raw = data["status"]
    new_status = status_map.get(new_status_raw, new_status_raw)

    old_status = txn.status
    txn.status = new_status
    db.session.commit()
    print(f"✅ Transaction {txn_id} status updated: {old_status} → {new_status}")

    # If transaction is marked as completed, mark food item as collected
    if new_status == "completed":
        try:
            food = FoodItem.query.get(txn.food_id)
            if food:
                food.status = "collected"
                db.session.commit()
                print(f"✅ Food item {txn.food_id} marked as collected")
                
                # SYNC ANALYTICS WHEN TRANSACTION COMPLETES - NON-BLOCKING
                try:
                    from backend.services.analytics_service import AnalyticsService
                    AnalyticsService.sync_analytics_after_transaction(txn, food)
                except Exception as ae:
                    print(f"⚠️ [COMPLETE] Analytics sync failed (non-blocking): {ae}")
                    import traceback
                    traceback.print_exc()
        except Exception as e:
            print(f"⚠️ Failed to mark food as collected: {e}")

    # Update MongoDB copy of transaction (non-blocking)
    try:
        from backend.mongodb import mongo_service
        if mongo_service and mongo_service.is_connected():
            mongo_service.update_transaction_status(txn.txn_id, new_status)
            # If completed, also log to analytics
            if new_status == "completed":
                try:
                    donor = User.query.get(txn.donor_id)
                    receiver = User.query.get(txn.receiver_id)
                    food = FoodItem.query.get(txn.food_id)
                    if all([donor, receiver, food]):
                        # Use the proper method to log analytics with impact_metrics
                        mongo_service.log_food_redistribution(
                            donor_id=txn.donor_id,
                            receiver_id=txn.receiver_id,
                            food_id=txn.food_id,
                            quantity_kg=food.quantity,
                            food_type=food.food_type
                        )
                        print(f"✅ Analytics logged for completed transaction {txn_id}")
                except Exception as ae:
                    print(f"⚠️ Failed to log analytics for completed transaction: {ae}")
    except Exception as e:
        print(f"⚠️ Failed to update transaction in MongoDB: {e}")

    # Send notifications for status update (non-blocking)
    try:
        NotificationService.notify_transaction_update(txn.txn_id, new_status)
    except Exception as e:
        print(f"⚠️ Notification send failed (non-blocking): {e}")

    # Emit transaction update via Socket.IO
    transaction_data = format_transaction_response(txn)
    socketio.emit('transaction_updated', transaction_data, room=f'user_{txn.donor_id}')
    socketio.emit('transaction_updated', transaction_data, room=f'user_{txn.receiver_id}')
    # Broadcast to all connected clients
    socketio.emit('transaction_updated', transaction_data)

    return jsonify({
        "message": "Transaction status updated",
        "transaction": format_transaction_response(txn)
    }), 200
