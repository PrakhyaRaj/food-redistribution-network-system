# backend/routes/admin_routes.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from backend.extensions import db
from backend.models import User, Role, FoodItem, Request as FoodRequest, Transaction
from functools import wraps

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/api/admin')

def admin_required(fn):
    """Decorator to require admin role"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or not user.has_role('admin'):
            return jsonify({"success": False, "error": "Admin access required"}), 403
        
        return fn(*args, **kwargs)
    return wrapper

# ============================================================
# DASHBOARD SUMMARY
# ============================================================
@admin_bp.route('/dashboard/summary', methods=['GET'])
@admin_required
def get_dashboard_summary():
    """Get admin dashboard summary statistics"""
    try:
        # Count metrics
        total_users = User.query.count()
        total_donors = len([u for u in User.query.all() if u.has_role('donor')])
        total_receivers = len([u for u in User.query.all() if u.has_role('receiver')])
        total_admins = len([u for u in User.query.all() if u.has_role('admin')])
        
        # Food metrics
        total_foods = FoodItem.query.count()
        available_foods = FoodItem.query.filter_by(status='available').count()
        expired_foods = FoodItem.query.filter_by(status='expired').count()
        collected_foods = FoodItem.query.filter_by(status='collected').count()
        
        # Request metrics
        total_requests = FoodRequest.query.count()
        pending_requests = FoodRequest.query.filter_by(status='pending').count()
        completed_requests = FoodRequest.query.filter_by(status='completed').count()
        
        # Transaction metrics
        total_transactions = Transaction.query.count()
        completed_transactions = Transaction.query.filter_by(status='completed').count()
        
        # Calculate success rate
        success_rate = round((completed_transactions / total_transactions * 100), 2) if total_transactions > 0 else 0
        
        # Recent activity (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_foods = FoodItem.query.filter(FoodItem.created_at >= seven_days_ago).count()
        recent_requests = FoodRequest.query.filter(FoodRequest.created_at >= seven_days_ago).count()
        recent_transactions = Transaction.query.filter(Transaction.created_at >= seven_days_ago).count()
        
        return jsonify({
            "success": True,
            "summary": {
                "users": {
                    "total": total_users,
                    "donors": total_donors,
                    "receivers": total_receivers,
                    "admins": total_admins
                },
                "foods": {
                    "total": total_foods,
                    "available": available_foods,
                    "expired": expired_foods,
                    "collected": collected_foods
                },
                "requests": {
                    "total": total_requests,
                    "pending": pending_requests,
                    "completed": completed_requests
                },
                "transactions": {
                    "total": total_transactions,
                    "completed": completed_transactions,
                    "success_rate": success_rate
                },
                "activities_summary": {   # cumulative (NOT last 7 days)
                    "foods": total_foods,
                    "requests": total_requests,
                    "transactions": total_transactions
                }
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Dashboard summary error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================
# USER MANAGEMENT
# ============================================================
@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role_filter = request.args.get('role', None)
        
        query = User.query
        
        if role_filter:
            role = Role.query.filter_by(role_name=role_filter).first()
            if role:
                query = query.filter(User.roles.contains(role))
        
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        users_data = []
        for user in paginated.items:
            users_data.append({
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "roles": user.roles_list(),
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "location": {
                    "lat": user.location_lat,
                    "long": user.location_long
                }
            })
        
        return jsonify({
            "success": True,
            "users": users_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": paginated.total,
                "pages": paginated.pages
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Get users error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user_details(user_id):
    """Get detailed user information"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        # Count user activities
        foods_donated = FoodItem.query.filter_by(donor_id=user_id).count()
        requests_made = FoodRequest.query.filter_by(receiver_id=user_id).count()
        donations_sent = Transaction.query.filter_by(donor_id=user_id).count()
        donations_received = Transaction.query.filter_by(receiver_id=user_id).count()
        
        return jsonify({
            "success": True,
            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "roles": user.roles_list(),
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "location": {
                    "lat": user.location_lat,
                    "long": user.location_long
                },
                "activities": {
                    "foods_donated": foods_donated,
                    "requests_made": requests_made,
                    "donations_sent": donations_sent,
                    "donations_received": donations_received
                }
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Get user details error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@admin_required
def update_user_role(user_id):
    """Update user role"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        data = request.get_json()
        roles = data.get('roles', [])
        
        if not roles:
            return jsonify({"success": False, "error": "Roles required"}), 400
        
        # Clear existing roles
        user.roles = []
        
        # Add new roles
        for role_name in roles:
            role = Role.query.filter_by(role_name=role_name).first()
            if role:
                user.roles.append(role)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "User roles updated successfully",
            "user_id": user_id,
            "roles": user.roles_list()
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update user role error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def deactivate_user(user_id):
    """Deactivate a user (soft delete)"""
    try:
        current_user_id = int(get_jwt_identity())
        if current_user_id == user_id:
            return jsonify({"success": False, "error": "Cannot deactivate your own account"}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        # Mark user as inactive by removing all roles
        user.roles = []
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "User deactivated successfully",
            "user_id": user_id
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Deactivate user error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================
# FOOD MANAGEMENT
# ============================================================
@admin_bp.route('/foods', methods=['GET'])
@admin_required
def get_all_foods():
    """Get all foods with filtering and pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status', None)
        
        query = FoodItem.query
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        foods_data = []
        for food in paginated.items:
            donor = User.query.get(food.donor_id)
            foods_data.append({
                "food_id": food.food_id,
                "name": food.name,
                "type": getattr(food, "food_type", None),
                "quantity": food.quantity,
                "status": food.status,
                "donor": {
                    "user_id": donor.user_id,
                    "name": donor.name,
                    "email": donor.email
                } if donor else None,
                "created_at": food.created_at.isoformat() if food.created_at else None,
                "expiry_date": food.expiry_date.isoformat() if food.expiry_date else None
            })      
        
        return jsonify({
            "success": True,
            "foods": foods_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": paginated.total,
                "pages": paginated.pages
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Get foods error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/foods/<int:food_id>', methods=['DELETE'])
@admin_required
def delete_food(food_id):
    """Delete a food item"""
    try:
        food = FoodItem.query.get(food_id)
        if not food:
            return jsonify({"success": False, "error": "Food not found"}), 404
        
        db.session.delete(food)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Food deleted successfully",
            "food_id": food_id
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete food error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================
# REQUEST MANAGEMENT
# ============================================================
@admin_bp.route('/requests', methods=['GET'])
@admin_required
def get_all_requests():
    """Get all food requests with filtering and pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status', None)
        
        query = FoodRequest.query
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        requests_data = []
        for req in paginated.items:
            receiver = User.query.get(req.receiver_id)
            requests_data.append({
                "request_id": req.request_id,
                "food_type": getattr(req, "food_type", None),
                "quantity": req.quantity,
                "status": req.status,
                "urgency": req.urgency_level,
                "receiver": {
                    "user_id": receiver.user_id,
                    "name": receiver.name,
                    "email": receiver.email
                } if receiver else None,
                "created_at": req.created_at.isoformat() if req.created_at else None,
                "deadline": req.deadline.isoformat() if req.deadline else None
            })
        
        return jsonify({
            "success": True,
            "requests": requests_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": paginated.total,
                "pages": paginated.pages
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Get requests error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/requests/<int:request_id>', methods=['DELETE'])
@admin_required
def delete_request(request_id):
    """Delete a food request"""
    try:
        food_request = FoodRequest.query.get(request_id)
        if not food_request:
            return jsonify({"success": False, "error": "Request not found"}), 404
        
        db.session.delete(food_request)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Request deleted successfully",
            "request_id": request_id
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete request error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================
# TRANSACTION MANAGEMENT
# ============================================================
@admin_bp.route('/transactions', methods=['GET'])
@admin_required
def get_all_transactions():
    """Get all transactions with filtering and pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status', None)
        
        query = Transaction.query
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        transactions_data = []
        for txn in paginated.items:
            donor = User.query.get(txn.donor_id)
            receiver = User.query.get(txn.receiver_id)
            
            transactions_data.append({
                "transaction_id": txn.txn_id,
                "status": txn.status,
                "donor": {
                    "user_id": donor.user_id,
                    "name": donor.name,
                    "email": donor.email
                } if donor else None,
                "receiver": {
                    "user_id": receiver.user_id,
                    "name": receiver.name,
                    "email": receiver.email
                } if receiver else None,
                "created_at": txn.created_at.isoformat() if txn.created_at else None,
                "completed_at": txn.completed_at.isoformat() if txn.completed_at else None
            })
        
        return jsonify({
            "success": True,
            "transactions": transactions_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": paginated.total,
                "pages": paginated.pages
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Get transactions error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================
# STATISTICS & REPORTS
# ============================================================
@admin_bp.route('/statistics/food-types', methods=['GET'])
@admin_required
def get_food_type_statistics():
    """Get statistics by food type"""
    try:
        foods = FoodItem.query.all()
        food_stats = {}
        
        for food in foods:
            food_type = getattr(food, "food_type", None) or food.name or "Unknown"
            if food_type not in food_stats:
                food_stats[food_type] = {
                    "count": 0,
                    "total_quantity": 0,
                    "by_status": {}
                }
            
            food_stats[food_type]["count"] += 1
            food_stats[food_type]["total_quantity"] += food.quantity or 0
            
            status = food.status
            if status not in food_stats[food_type]["by_status"]:
                food_stats[food_type]["by_status"][status] = 0
            food_stats[food_type]["by_status"][status] += 1
        
        return jsonify({
            "success": True,
            "statistics": food_stats
        }), 200
    except Exception as e:
        current_app.logger.error(f"Food type statistics error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/statistics/daily-activity', methods=['GET'])
@admin_required
def get_daily_activity():
    """Get daily activity statistics for the last 30 days"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        activity_by_day = {}
        
        # Count foods created per day
        foods = FoodItem.query.filter(FoodItem.created_at >= start_date).all()
        for food in foods:
            day = food.created_at.date().isoformat()
            if day not in activity_by_day:
                activity_by_day[day] = {"foods": 0, "requests": 0, "transactions": 0}
            activity_by_day[day]["foods"] += 1
        
        # Count requests created per day
        requests = FoodRequest.query.filter(FoodRequest.created_at >= start_date).all()
        for req in requests:
            day = req.created_at.date().isoformat()
            if day not in activity_by_day:
                activity_by_day[day] = {"foods": 0, "requests": 0, "transactions": 0}
            activity_by_day[day]["requests"] += 1
        
        # Count transactions created per day
        transactions = Transaction.query.filter(Transaction.created_at >= start_date).all()
        for txn in transactions:
            day = txn.created_at.date().isoformat()
            if day not in activity_by_day:
                activity_by_day[day] = {"foods": 0, "requests": 0, "transactions": 0}
            activity_by_day[day]["transactions"] += 1
        
        # Sort by date
        sorted_activity = dict(sorted(activity_by_day.items()))
        
        return jsonify({
            "success": True,
            "activity": sorted_activity,
            "period_days": days
        }), 200
    except Exception as e:
        current_app.logger.error(f"Daily activity error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================
# SYSTEM HEALTH & MONITORING
# ============================================================
@admin_bp.route('/health', methods=['GET'])
@admin_required
def get_system_health():
    """Get system health information"""
    try:
        from sqlalchemy import text
        
        # Database connection test
        db_health = True
        db_error = None
        try:
            db.session.execute(text("SELECT 1"))
        except Exception as e:
            db_health = False
            db_error = str(e)
        
        # MongoDB health check
        mongo_health = False
        mongo_error = None
        if current_app.mongodb:
            try:
                current_app.mongodb.is_connected()
                mongo_health = True
            except Exception as e:
                mongo_error = str(e)
        
        return jsonify({
            "success": True,
            "health": {
                "database": {
                    "status": "healthy" if db_health else "unhealthy",
                    "error": db_error
                },
                "mongodb": {
                    "status": "healthy" if mongo_health else "unavailable",
                    "error": mongo_error
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"System health check error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/logs/system', methods=['GET'])
@admin_required
def get_system_logs():
    """Get recent system logs (limited)"""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        # Try to get logs from MongoDB if available
        if current_app.mongodb:
            try:
                from backend.services.activity_logger import ActivityLogger
                activities = ActivityLogger.get_all_activities(limit)
                return jsonify({
                    "success": True,
                    "logs": activities,
                    "source": "mongodb"
                }), 200
            except:
                pass
        
        return jsonify({
            "success": True,
            "logs": [],
            "source": "unavailable",
            "message": "MongoDB not available for logs"
        }), 200
    except Exception as e:
        current_app.logger.error(f"System logs error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500