from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics_bp', __name__, url_prefix='/api/analytics')

@analytics_bp.route('/global-summary', methods=['GET'])
def get_global_analytics_summary():
    """Get global analytics summary (public endpoint for login page)"""
    from backend.mongodb import mongo_service
    
    days = request.args.get('days', 30, type=int)
    
    try:
        summary = mongo_service.get_analytics_summary(days)
        
        return jsonify({
            "success": True,
            "summary": summary,
            "period_days": days,
            "generated_at": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@analytics_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_analytics_summary():
    """Get analytics summary - returns global or user-specific based on param"""
    from backend.mongodb import mongo_service
    
    days = request.args.get('days', 30, type=int)
    user_specific = request.args.get('user_specific', 'false').lower() == 'true'
    
    try:
        if user_specific:
            # Get user-specific analytics (for dashboards)
            user_id = get_jwt_identity()
            summary = mongo_service.get_user_analytics_summary(int(user_id), days)
        else:
            # Get global analytics (for login page)
            summary = mongo_service.get_analytics_summary(days)
        
        return jsonify({
            "success": True,
            "summary": summary,
            "period_days": days,
            "user_specific": user_specific,
            "generated_at": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@analytics_bp.route('/log-redistribution', methods=['POST'])
@jwt_required()
def log_redistribution_analytics():
    """Log food redistribution for analytics"""
    from backend.mongodb import mongo_service
    
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['receiver_id', 'food_id', 'quantity_kg', 'food_type']
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "error": f"Missing {field}"}), 400
    
    try:
        analytics_id = mongo_service.log_food_redistribution(
            donor_id=user_id,
            receiver_id=data['receiver_id'],
            food_id=data['food_id'],
            quantity_kg=data['quantity_kg'],
            food_type=data['food_type']
        )
        
        if analytics_id:
            return jsonify({
                "success": True,
                "message": "Redistribution logged for analytics",
                "analytics_id": analytics_id
            }), 201
        else:
            return jsonify({"success": False, "error": "Failed to log analytics"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@analytics_bp.route('/trends/demand', methods=['GET'])
@jwt_required()
def get_demand_trends():
    """Get demand trends (admin only)"""
    from backend.models import User
    
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check if admin
    user_roles = [role.role_name for role in user.roles]
    if 'admin' not in user_roles:
        return jsonify({"success": False, "error": "Admin access required"}), 403
    
    from backend.mongodb import mongo_service
    
    days = request.args.get('days', 7, type=int)
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Group by food type
        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": cutoff_date}
                }
            },
            {
                "$group": {
                    "_id": "$food_type",
                    "total_quantity": {"$sum": "$quantity_required"},
                    "avg_urgency": {"$avg": {"$cond": [
                        {"$eq": ["$urgency", "high"]}, 3,
                        {"$cond": [
                            {"$eq": ["$urgency", "medium"]}, 2,
                            1
                        ]}
                    ]}},
                    "request_count": {"$sum": 1}
                }
            },
            {"$sort": {"total_quantity": -1}}
        ]
        
        trends = list(mongo_service.db["demand_trends"].aggregate(pipeline))
        
        return jsonify({
            "success": True,
            "trends": trends,
            "period_days": days
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500