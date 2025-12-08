from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

logs_bp = Blueprint('logs_bp', __name__, url_prefix='/logs')

# Helper MongoDB availability checker
def check_mongodb():
    if not current_app.mongodb or not current_app.mongodb.is_connected():
        return jsonify({
            "success": False,
            "error": "MongoDB service not available",
            "message": "Feature temporarily disabled"
        }), 503
    return None


# ============================
# FEEDBACK ROUTES
# ============================
@logs_bp.route('/feedback', methods=['POST'])
@jwt_required()
def submit_feedback():
    """Submit user feedback"""
    error = check_mongodb()
    if error:
        return error

    from backend.services.feedback_service import FeedbackService

    user_id = get_jwt_identity()
    data = request.get_json()

    message = data.get('message')
    feedback_type = data.get('type', 'general')
    metadata = data.get('metadata', {})

    if not message:
        return jsonify({"success": False, "error": "Message is required"}), 400

    try:
        feedback_id = FeedbackService.submit_feedback(user_id, feedback_type, message, metadata)

        from backend.services.activity_logger import ActivityLogger
        ActivityLogger.log_feedback_submitted(user_id, str(feedback_id))
        
        return jsonify({
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback_id": str(feedback_id)
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@logs_bp.route('/feedback/my', methods=['GET'])
@jwt_required()
def get_my_feedback():
    """Get feedback submitted by current user"""
    error = check_mongodb()
    if error:
        return error

    from backend.services.feedback_service import FeedbackService

    user_id = get_jwt_identity()
    limit = request.args.get('limit', 20, type=int)

    try:
        feedback = FeedbackService.get_user_feedback(user_id, limit)
        return jsonify({
            "success": True,
            "feedback": feedback,
            "count": len(feedback)
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================
# ACTIVITY ROUTES
# ============================
@logs_bp.route('/activities', methods=['GET'])
@jwt_required()
def get_activities():
    """Get user's activity logs"""
    error = check_mongodb()
    if error:
        return error

    from backend.services.activity_logger import ActivityLogger

    user_id = get_jwt_identity()
    limit = request.args.get('limit', 50, type=int)

    try:
        activities = ActivityLogger.get_user_activities(user_id, limit)
        return jsonify({
            "success": True,
            "activities": activities,
            "count": len(activities)
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================
# NOTIFICATION ROUTES
# ============================
@logs_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get user's notifications"""
    error = check_mongodb()
    if error:
        return error

    from backend.services.notification_service import NotificationService

    user_id = get_jwt_identity()
    unread_only = request.args.get('unread_only', 'true').lower() == 'true'
    limit = request.args.get('limit', 50, type=int)

    try:
        notifications = NotificationService.get_user_notifications(user_id, unread_only, limit)
        unread_count = len([n for n in notifications if not n.get('read', False)])

        return jsonify({
            "success": True,
            "notifications": notifications,
            "unread_count": unread_count,
            "total": len(notifications)
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@logs_bp.route('/notifications/mark-read', methods=['POST'])
@jwt_required()
def mark_notifications_read():
    """Mark notifications as read"""
    error = check_mongodb()
    if error:
        return error

    from backend.mongodb import mongo_service

    user_id = get_jwt_identity()
    data = request.get_json()
    notification_ids = data.get('notification_ids')

    if not notification_ids:
        return jsonify({"success": False, "error": "No notification IDs provided"}), 400

    try:
        mongo_service.mark_as_read(notification_ids)
        return jsonify({
            "success": True,
            "message": f"Marked {len(notification_ids)} notifications as read"
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================
# GEO LOCATION ROUTES
# ============================
@logs_bp.route('/nearby-users', methods=['GET'])
@jwt_required()
def get_nearby_users():
    """Find users nearby based on coordinates or stored location"""
    error = check_mongodb()
    if error:
        return error

    from backend.services.geo_service import GeoService
    from backend.models import User

    user_id = get_jwt_identity()

    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', 10, type=float)
    user_type = request.args.get('user_type')

    if not lat or not lng:
        user = User.query.get(user_id)
        if user and user.location_lat and user.location_long:
            lat, lng = user.location_lat, user.location_long
        else:
            return jsonify({"success": False, "error": "Location coordinates required"}), 400

    try:
        nearby_users = GeoService.find_nearby_users(lat, lng, radius, user_type)
        return jsonify({
            "success": True,
            "nearby_users": nearby_users,
            "count": len(nearby_users),
            "search_center": {"lat": lat, "lng": lng, "radius_km": radius}
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================
# DEBUG/ADMIN ROUTES
# ============================
@logs_bp.route('/debug/stats', methods=['GET'])
@jwt_required()
def get_debug_stats():
    """View basic MongoDB statistics (admin required)"""
    error = check_mongodb()
    if error:
        return error

    from backend.mongodb import mongo_service
    from backend.models import User

    user = User.query.get(get_jwt_identity())
    user_roles = [role.role_name for role in user.roles]

    if "admin" not in user_roles:
        return jsonify({"success": False, "error": "Admin access required"}), 403

    try:
        unresolved_feedback = mongo_service.get_unresolved_feedback()
        daily_activity = mongo_service.get_daily_activity_stats(days=7)

        return jsonify({
            "success": True,
            "unresolved_feedback": len(unresolved_feedback),
            "daily_activity": daily_activity
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
