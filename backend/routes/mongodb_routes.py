# backend/routes/mongodb_routes.py
"""
MongoDB routes for fetching and managing data stored in MongoDB collections.
Provides endpoints for transactions, feedback, notifications, and analytics.
"""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, User, Transaction as SQLTransaction

mongodb_bp = Blueprint("mongodb_bp", __name__, url_prefix="/api/mongodb")

def get_mongo_service():
    """Get mongo_service from app context (late binding to handle initialization order)"""
    return getattr(current_app, 'mongodb', None)

@mongodb_bp.route("/transactions", methods=["GET"])
@jwt_required()
def get_user_transactions():
    """Get all transactions for current user, optionally filter by txn_id"""
    try:
        mongo_service = get_mongo_service()
        user_id = get_jwt_identity()
        # Convert JWT identity (string) to int for MongoDB query
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "Invalid user identity"
            }), 400
        
        if not mongo_service or not mongo_service.is_connected():
            return jsonify({
                "success": False,
                "error": "MongoDB not available"
            }), 503
        
        # Get transactions from MongoDB
        transactions = mongo_service.get_user_transactions(user_id)
        
        # Filter by txn_id if provided
        txn_id = request.args.get('txn_id', type=int)
        if txn_id:
            transactions = [t for t in transactions if t.get('txn_id') == txn_id]

        # Sort newest-first to surface the latest optimized route
        def _txn_sort_key(t):
            created = t.get('created_at') or t.get('date') or ''
            return (str(created), t.get('txn_id', 0))
        transactions = sorted(transactions, key=_txn_sort_key, reverse=True)
        
        # Get stats
        stats = mongo_service.get_transaction_stats(user_id)
        
        return jsonify({
            "success": True,
            "transactions": transactions,
            "stats": stats,
            "count": len(transactions)
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error fetching transactions: {str(e)}"
        }), 500

@mongodb_bp.route("/transactions/<int:txn_id>", methods=["GET"])
@jwt_required()
def get_transaction(txn_id):
    """Get specific transaction"""
    try:
        mongo_service = get_mongo_service()
        user_id = get_jwt_identity()
        
        if not mongo_service or not mongo_service.is_connected():
            return jsonify({
                "success": False,
                "error": "MongoDB not available"
            }), 503
        
        # First try to get from MongoDB
        transactions = mongo_service.get_user_transactions(user_id)
        txn = next((t for t in transactions if t['txn_id'] == txn_id), None)
        
        if txn:
            return jsonify({
                "success": True,
                "transaction": txn
            }), 200
        
        # Fallback to SQL
        sql_txn = SQLTransaction.query.get(txn_id)
        if not sql_txn or (sql_txn.donor_id != user_id and sql_txn.receiver_id != user_id):
            return jsonify({
                "success": False,
                "error": "Transaction not found"
            }), 404
        
        return jsonify({
            "success": True,
            "transaction": {
                "txn_id": sql_txn.txn_id,
                "donor_id": sql_txn.donor_id,
                "receiver_id": sql_txn.receiver_id,
                "food_id": sql_txn.food_id,
                "request_id": sql_txn.request_id,
                "status": sql_txn.status,
                "created_at": sql_txn.created_at.isoformat(),
                "completed_at": sql_txn.completed_at.isoformat() if sql_txn.completed_at else None
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error fetching transaction: {str(e)}"
        }), 500

@mongodb_bp.route("/transactions/<int:txn_id>/update-status", methods=["PUT"])
@jwt_required()
def update_transaction_status(txn_id):
    """Update transaction status in MongoDB"""
    try:
        mongo_service = get_mongo_service()
        user_id = get_jwt_identity()
        data = request.json or {}
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({
                "success": False,
                "error": "Status is required"
            }), 400
        
        if not mongo_service or not mongo_service.is_connected():
            return jsonify({
                "success": False,
                "error": "MongoDB not available"
            }), 503
        
        # Verify user owns this transaction
        transactions = mongo_service.get_user_transactions(user_id)
        txn = next((t for t in transactions if t['txn_id'] == txn_id), None)
        
        if not txn:
            return jsonify({
                "success": False,
                "error": "Transaction not found"
            }), 404
        
        # Update status
        success = mongo_service.update_transaction_status(txn_id, new_status)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Transaction status updated to {new_status}"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to update transaction status"
            }), 500
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error updating transaction: {str(e)}"
        }), 500

@mongodb_bp.route("/route-optimizations/<int:request_id>", methods=["GET"])
@jwt_required()
def get_route_optimizations(request_id):
    """Get route optimizations for a request"""
    try:
        mongo_service = get_mongo_service()
        if not mongo_service or not mongo_service.is_connected():
            return jsonify({
                "success": False,
                "error": "MongoDB not available"
            }), 503
        
        optimizations = mongo_service.get_route_optimizations(request_id)
        
        return jsonify({
            "success": True,
            "optimizations": optimizations,
            "count": len(optimizations)
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error fetching route optimizations: {str(e)}"
        }), 500

@mongodb_bp.route("/notifications/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user_notifications(user_id):
    """Get notifications for user"""
    try:
        mongo_service = get_mongo_service()
        # Verify requester is the user or admin
        current_user = get_jwt_identity()
        # normalize types: JWT identity may be stored as string
        try:
            current_user_int = int(current_user)
        except Exception:
            current_user_int = None

        if current_user_int != user_id:
            # attempt to load user by id (if available)
            user = User.query.get(current_user_int) if current_user_int is not None else None
            if not user or not user.has_role('admin'):
                return jsonify({
                    "success": False,
                    "error": "Unauthorized"
                }), 403
        
        if not mongo_service or not mongo_service.is_connected():
            return jsonify({
                "success": False,
                "error": "MongoDB not available"
            }), 503
        
        notifications = mongo_service.get_notifications(user_id)
        
        return jsonify({
            "success": True,
            "notifications": notifications,
            "count": len(notifications)
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error fetching notifications: {str(e)}"
        }), 500


@mongodb_bp.route("/notifications", methods=["GET"])
@jwt_required()
def get_my_notifications():
    """Get notifications for the currently authenticated user (no path id required)."""
    try:
        mongo_service = get_mongo_service()
        current_user = get_jwt_identity()
        print(f"📬 [GET /notifications] Current user: {current_user}")
        
        try:
            current_user_int = int(current_user)
        except Exception:
            return jsonify({
                "success": False,
                "error": "Invalid user identity in token"
            }), 400

        if not mongo_service:
            print(f"❌ [GET /notifications] mongo_service is None")
            return jsonify({
                "success": False,
                "error": "MongoDB service not initialized"
            }), 503
        
        if not mongo_service.is_connected():
            print(f"❌ [GET /notifications] MongoDB not connected")
            return jsonify({
                "success": False,
                "error": "MongoDB not available"
            }), 503

        unread_only = request.args.get('unread_only', 'true').lower() != 'false'
        print(f"📬 [GET /notifications] Fetching notifications, unread_only={unread_only}")
        
        if unread_only:
            notifications = mongo_service.get_unread_notifications(current_user_int)
            print(f"📬 [GET /notifications] Unread notifications: {len(notifications)}")
        else:
            notifications = mongo_service.get_all_notifications(current_user_int)
            print(f"📬 [GET /notifications] All notifications: {len(notifications)}")

        return jsonify({
            "success": True,
            "notifications": notifications,
            "count": len(notifications)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error fetching notifications: {str(e)}"
        }), 500


@mongodb_bp.route("/notifications/<string:notification_id>/read", methods=["PUT"])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    try:
        mongo_service = get_mongo_service()
        from bson import ObjectId
        if not mongo_service or not mongo_service.is_connected():
            return jsonify({"success": False, "error": "MongoDB not available"}), 503
        
        try:
            notif_id = ObjectId(notification_id)
        except Exception:
            return jsonify({"success": False, "error": "Invalid notification ID"}), 400
        
        mongo_service.db.notifications.update_one(
            {"_id": notif_id},
            {"$set": {"status": "read"}}
        )
        
        return jsonify({"success": True, "message": "Notification marked as read"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@mongodb_bp.route("/notifications/<string:notification_id>", methods=["DELETE"])
@jwt_required()
def delete_notification(notification_id):
    """Delete a notification"""
    try:
        mongo_service = get_mongo_service()
        from bson import ObjectId
        if not mongo_service or not mongo_service.is_connected():
            return jsonify({"success": False, "error": "MongoDB not available"}), 503
        
        try:
            notif_id = ObjectId(notification_id)
        except Exception:
            return jsonify({"success": False, "error": "Invalid notification ID"}), 400
        
        result = mongo_service.db.notifications.delete_one({"_id": notif_id})
        if result.deleted_count > 0:
            return jsonify({"success": True, "message": "Notification deleted"}), 200
        else:
            return jsonify({"success": False, "error": "Notification not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@mongodb_bp.route("/feedback/user/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user_feedback(user_id):
    """Get feedback for a user"""
    try:
        mongo_service = get_mongo_service()
        if not mongo_service or not mongo_service.is_connected():
            return jsonify({
                "success": False,
                "error": "MongoDB not available"
            }), 503
        
        feedbacks = mongo_service.get_user_feedback(user_id)
        
        # Calculate stats
        total = len(feedbacks)
        avg_rating = sum(f.get('rating', 0) for f in feedbacks) / total if total > 0 else 0
        
        return jsonify({
            "success": True,
            "feedbacks": feedbacks,
            "stats": {
                "total": total,
                "average_rating": round(avg_rating, 2)
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error fetching feedback: {str(e)}"
        }), 500

@mongodb_bp.route("/activities/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user_activities(user_id):
    """Get activity log for user"""
    try:
        mongo_service = get_mongo_service()
        if not mongo_service or not mongo_service.is_connected():
            return jsonify({
                "success": False,
                "error": "MongoDB not available"
            }), 503
        
        limit = request.args.get('limit', 50, type=int)
        activities = mongo_service.get_user_activities(user_id, limit=limit)
        
        return jsonify({
            "success": True,
            "activities": activities,
            "count": len(activities)
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error fetching activities: {str(e)}"
        }), 500

@mongodb_bp.route("/analytics/redistribution", methods=["GET"])
@jwt_required()
def get_redistribution_analytics():
    """Get redistribution analytics for current user"""
    try:
        mongo_service = get_mongo_service()
        user_id = get_jwt_identity()
        
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "Invalid user identity"
            }), 400
        
        if not mongo_service or not mongo_service.is_connected():
            return jsonify({
                "success": False,
                "error": "MongoDB not available"
            }), 503
        
        # Get analytics from redistribution_analytics collection
        limit = request.args.get('limit', 50, type=int)
        
        # Query: must have either donor_id OR receiver_id matching user, and must have distance_km field
        analytics = list(mongo_service.db.redistribution_analytics.find({
            "$or": [
                {"donor_id": user_id},
                {"receiver_id": user_id}
            ],
            "distance_km": {"$exists": True}  # Only return records with distance data
        }).sort("created_at", -1).limit(limit))
        
        # Convert ObjectId and handle date fields
        for item in analytics:
            if '_id' in item:
                item['_id'] = str(item['_id'])
            # Ensure created_at is a string ISO format
            if 'created_at' in item and hasattr(item['created_at'], 'isoformat'):
                item['created_at'] = item['created_at'].isoformat()
        
        return jsonify({
            "success": True,
            "analytics": analytics,
            "count": len(analytics)
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error fetching analytics: {str(e)}"
        }), 500

# ========== DEBUG ENDPOINTS ==========

@mongodb_bp.route("/test-auth", methods=["GET"])
@jwt_required()
def test_auth():
    """Test if JWT authentication is working"""
    try:
        mongo_service = get_mongo_service()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        return jsonify({
            "success": True,
            "message": "JWT authentication working!",
            "user_id": user_id,
            "user_email": user.email if user else "User not found",
            "mongo_status": "connected" if mongo_service and mongo_service.is_connected() else "disconnected"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Auth test failed: {str(e)}"
        }), 500

@mongodb_bp.route("/status", methods=["GET"])
def check_status():
    """Check MongoDB and API status (no auth required)"""
    mongo_service = get_mongo_service()
    return jsonify({
        "success": True,
        "api": "running",
        "mongodb": "connected" if mongo_service and mongo_service.is_connected() else "disconnected",
        "message": "Use GET /api/mongodb/test-auth with JWT token to verify authentication"
    }), 200
