from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import hashlib

route_bp = Blueprint('route_bp', __name__, url_prefix='/api/routes')

@route_bp.route('/optimize', methods=['POST'])
@jwt_required()
def optimize_route():
    """Optimize delivery route using AI/ML"""
    from backend.services.route_optimizer import RouteOptimizer
    from backend.mongodb import mongo_service
    from datetime import datetime
    
    user_id = get_jwt_identity()
    data = request.get_json()
    
    pickup_points = data.get('pickup_points', [])
    delivery_points = data.get('delivery_points', [])
    constraints = data.get('constraints', {})
    pickup_date_str = data.get('pickup_date')  # ISO format datetime string
    
    if not pickup_points or not delivery_points:
        return jsonify({"success": False, "error": "Pickup and delivery points required"}), 400
    
    # Parse pickup_date if provided
    pickup_date = None
    if pickup_date_str:
        try:
            pickup_date = datetime.fromisoformat(pickup_date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError) as e:
            return jsonify({"success": False, "error": f"Invalid pickup_date format: {str(e)}"}), 400
    
    try:
        # Check cache first
        route_data = {
            "pickup_points": pickup_points,
            "delivery_points": delivery_points,
            "constraints": constraints,
            "pickup_date": pickup_date_str
        }
        route_signature = hashlib.md5(str(route_data).encode()).hexdigest()
        
        cached = mongo_service.get_cached_route(route_signature)
        if cached:
            return jsonify({
                "success": True,
                "optimized_route": cached["optimization_result"],
                "cached": True,
                "cache_hits": cached.get("cache_hits", 0)
            }), 200
        
        # Run optimization with pickup_date for time window enforcement
        result = RouteOptimizer.optimize_route(
            pickup_points, 
            delivery_points, 
            constraints,
            pickup_date=pickup_date
        )
        
        # Cache the result
        mongo_service.cache_optimized_route(route_data, result)
        
        # Log analytics
        mongo_service.log_route_optimization(
            user_id=user_id,
            points_count=len(pickup_points) + len(delivery_points),
            distance_saved=result["metrics"]["total_distance_km"],
            efficiency=result["metrics"]["efficiency_score"]
        )
        
        return jsonify({
            "success": True,
            "optimized_route": result,
            "cached": False
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@route_bp.route('/batch-optimize', methods=['POST'])
@jwt_required()
def batch_optimize():
    """Optimize multiple routes for batch processing"""
    from backend.services.route_optimizer import RouteOptimizer
    from backend.mongodb import mongo_service
    
    data = request.get_json()
    routes = data.get('routes', [])
    
    if not routes:
        return jsonify({"success": False, "error": "No routes provided"}), 400
    
    try:
        optimized_routes = []
        total_savings = {
            "distance_saved_km": 0,
            "time_saved_hours": 0,
            "fuel_saved_liters": 0,
            "carbon_saved_kg": 0
        }
        
        for route in routes:
            # Parse pickup_date if provided for this route
            pickup_date = None
            if route.get('pickup_date'):
                try:
                    pickup_date = datetime.fromisoformat(route['pickup_date'].replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    pass  # Skip invalid dates, route will optimize without time window
            
            result = RouteOptimizer.optimize_route(
                route.get('pickup_points', []),
                route.get('delivery_points', []),
                route.get('constraints', {}),
                pickup_date=pickup_date
            )
            
            optimized_routes.append(result)
            
            # Accumulate savings
            total_savings["distance_saved_km"] += result["metrics"]["total_distance_km"]
            total_savings["time_saved_hours"] += result["metrics"]["estimated_time_hours"]
            total_savings["fuel_saved_liters"] += result["metrics"]["fuel_saved_liters"]
            total_savings["carbon_saved_kg"] += result["metrics"]["carbon_saved_kg"]
        
        return jsonify({
            "success": True,
            "optimized_routes": optimized_routes,
            "batch_summary": {
                "total_routes": len(optimized_routes),
                "total_savings": total_savings,
                "avg_efficiency": sum(r["metrics"]["efficiency_score"] for r in optimized_routes) / len(optimized_routes)
            }
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500