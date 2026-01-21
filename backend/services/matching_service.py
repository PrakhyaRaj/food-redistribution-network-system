# backend/services/matching_service.py
from datetime import datetime, timedelta
from backend.models import FoodItem, User, Request, Transaction
from backend.extensions import db
from backend.mongodb import mongo_service
from typing import List, Dict, Optional
import math

class MatchingService:
    """
    Core matching service for food redistribution.
    Matches receiver requests with available donor food items.
    """

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.
        Returns distance in kilometers.
        """
        if not all([lat1, lon1, lat2, lon2]):
            return float('inf')
        
        R = 6371  # Earth's radius in km
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi/2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c

    @staticmethod
    def find_matches_for_request(request_id: int) -> Dict:
        """
        Find matching food items for a receiver's request.
        
        Matching criteria:
        1. Food type matches request
        2. Quantity >= request quantity
        3. Not expired
        4. Status is 'available'
        5. Sorted by distance (closest first)
        
        Returns:
            {
                "success": bool,
                "request": {...},
                "matches": [
                    {
                        "food_id": int,
                        "donor_id": int,
                        "donor_name": str,
                        "food_name": str,
                        "quantity": int,
                        "expiry_date": str,
                        "distance_km": float,
                        "urgency_match": str (low/medium/high)
                    }
                ],
                "match_count": int
            }
        """
        try:
            # Get the request
            req = Request.query.get(request_id)
            if not req:
                return {
                    "success": False,
                    "error": "Request not found"
                }
            
            # Get receiver info
            receiver = User.query.get(req.receiver_id)
            if not receiver or not receiver.location_lat or not receiver.location_long:
                return {
                    "success": False,
                    "error": "Receiver location not found"
                }
            
            # Find available food items that match
            foods = FoodItem.query.filter(
                FoodItem.status == 'available',
                FoodItem.expiry_date >= datetime.now().date(),
                FoodItem.quantity >= req.quantity
            ).all()
            
            matches = []
            
            for food in foods:
                # Get donor info
                donor = User.query.get(food.donor_id)
                if not donor or not donor.location_lat or not donor.location_long:
                    continue
                
                # Check if food type matches (fuzzy match)
                if not MatchingService._fuzzy_match_food_type(
                    food.name.lower(), 
                    req.food_type.lower()
                ):
                    continue
                
                # Calculate distance
                distance = MatchingService.calculate_distance(
                    receiver.location_lat,
                    receiver.location_long,
                    donor.location_lat,
                    donor.location_long
                )
                
                # Calculate urgency match
                urgency_match = MatchingService._calculate_urgency_match(
                    req.urgency_level,
                    food.expiry_date
                )
                
                matches.append({
                    "food_id": food.food_id,
                    "donor_id": food.donor_id,
                    "donor_name": donor.name,
                    "donor_phone": donor.phone,
                    "donor_lat": donor.location_lat,
                    "donor_long": donor.location_long,
                    "food_name": food.name,
                    "quantity": food.quantity,
                    "expiry_date": food.expiry_date.strftime("%Y-%m-%d"),
                    "distance_km": round(distance, 2),
                    "urgency_match": urgency_match,
                    "status": food.status
                })
            
            # Sort by distance (closest first)
            matches.sort(key=lambda x: x['distance_km'])
            
            return {
                "success": True,
                "request": {
                    "request_id": req.request_id,
                    "receiver_id": req.receiver_id,
                    "receiver_name": receiver.name,
                    "food_type": req.food_type,
                    "quantity": req.quantity,
                    "urgency_level": req.urgency_level,
                    "deadline": req.deadline.strftime("%Y-%m-%d %H:%M:%S") if req.deadline else None,
                    "receiver_lat": receiver.location_lat,
                    "receiver_long": receiver.location_long
                },
                "matches": matches,
                "match_count": len(matches)
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Error finding matches: {str(e)}"
            }

    @staticmethod
    def find_matches_for_donor(donor_id: int, food_id: int) -> Dict:
        """
        Find matching receiver requests for a donor's food item.
        
        Matching criteria:
        1. Request food type matches food name
        2. Request quantity <= food quantity
        3. Request not expired/completed
        4. Sorted by distance and urgency (urgent + close = priority)
        
        Returns:
            {
                "success": bool,
                "food": {...},
                "matches": [
                    {
                        "request_id": int,
                        "receiver_id": int,
                        "receiver_name": str,
                        "quantity_needed": int,
                        "urgency_level": str,
                        "distance_km": float,
                        "priority_score": float
                    }
                ],
                "match_count": int
            }
        """
        try:
            # Get the food item
            food = FoodItem.query.get(food_id)
            if not food or food.donor_id != donor_id:
                return {
                    "success": False,
                    "error": "Food item not found or not owned by donor"
                }
            
            # Get donor info
            donor = User.query.get(donor_id)
            if not donor or not donor.location_lat or not donor.location_long:
                return {
                    "success": False,
                    "error": "Donor location not found"
                }
            
            # Find pending/active requests that match
            requests = Request.query.filter(
                Request.status.in_(['pending', 'accepted']),
                Request.quantity <= food.quantity
            ).all()
            
            matches = []
            
            for req in requests:
                # Get receiver info
                receiver = User.query.get(req.receiver_id)
                if not receiver or not receiver.location_lat or not receiver.location_long:
                    continue
                
                # Check if food type matches
                if not MatchingService._fuzzy_match_food_type(
                    food.name.lower(), 
                    req.food_type.lower()
                ):
                    continue
                
                # Calculate distance
                distance = MatchingService.calculate_distance(
                    donor.location_lat,
                    donor.location_long,
                    receiver.location_lat,
                    receiver.location_long
                )
                
                # Calculate priority score (urgent + close = high priority)
                urgency_score = {
                    'high': 3,
                    'medium': 2,
                    'low': 1
                }.get(req.urgency_level, 1)
                
                distance_score = max(0, 10 - (distance / 10))  # Closer = higher score
                priority_score = (urgency_score * 3) + distance_score
                
                matches.append({
                    "request_id": req.request_id,
                    "receiver_id": req.receiver_id,
                    "receiver_name": receiver.name,
                    "receiver_phone": receiver.phone,
                    "receiver_lat": receiver.location_lat,
                    "receiver_long": receiver.location_long,
                    "food_type": req.food_type,
                    "quantity_needed": req.quantity,
                    "urgency_level": req.urgency_level,
                    "deadline": req.deadline.strftime("%Y-%m-%d %H:%M:%S") if req.deadline else None,
                    "distance_km": round(distance, 2),
                    "priority_score": round(priority_score, 2)
                })
            
            # Sort by priority score (highest first)
            matches.sort(key=lambda x: x['priority_score'], reverse=True)
            
            return {
                "success": True,
                "food": {
                    "food_id": food.food_id,
                    "donor_id": donor_id,
                    "donor_name": donor.name,
                    "food_name": food.name,
                    "quantity": food.quantity,
                    "expiry_date": food.expiry_date.strftime("%Y-%m-%d"),
                    "donor_lat": donor.location_lat,
                    "donor_long": donor.location_long
                },
                "matches": matches,
                "match_count": len(matches)
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Error finding matches: {str(e)}"
            }

    @staticmethod
    def create_match_transaction(
        request_id: int, 
        food_id: int,
        quantity: Optional[int] = None
    ) -> Dict:
        """
        Create a transaction from a matched request and food item.
        
        Args:
            request_id: The request ID
            food_id: The food item ID
            quantity: Optional specific quantity (defaults to request quantity)
        
        Returns:
            {
                "success": bool,
                "transaction_id": int,
                "error": str (if failed)
            }
        """
        try:
            # Get request and food
            req = Request.query.get(request_id)
            food = FoodItem.query.get(food_id)
            
            if not req or not food:
                return {
                    "success": False,
                    "error": "Request or food not found"
                }
            
            # Validate quantity
            match_quantity = quantity or req.quantity
            if match_quantity > food.quantity:
                return {
                    "success": False,
                    "error": f"Requested quantity {match_quantity} exceeds available {food.quantity}"
                }
            
            # Create transaction with quantity and default pickup_date
            transaction = Transaction(
                donor_id=food.donor_id,
                receiver_id=req.receiver_id,
                food_id=food_id,
                request_id=request_id,
                quantity=match_quantity,
                pickup_date=datetime.now(),  # Set to current time as default
                status='initiated'
            )
            
            # Compute route data and store in transaction
            route_data = None
            try:
                from backend.services.route_optimizer import RouteOptimizer
                donor = User.query.get(transaction.donor_id)
                receiver = User.query.get(transaction.receiver_id)
                if donor and receiver and donor.location_lat and donor.location_long and receiver.location_lat and receiver.location_long:
                    route_result = RouteOptimizer.optimize_route(
                        donor_lat=donor.location_lat,
                        donor_long=donor.location_long,
                        receiver_lat=receiver.location_lat,
                        receiver_long=receiver.location_long,
                        quantity=1,
                        pickup_date=transaction.pickup_date
                    )
                    if route_result.get('success'):
                        route_data = route_result
                        transaction.route_data = route_data  # Store in SQL
                        print(f"✅ Route data computed and stored in SQL transaction")
            except Exception as e:
                print(f"⚠️ Route optimization (matching) failed (non-blocking): {e}")
            
            # Update food status
            food.quantity -= match_quantity
            if food.quantity == 0:
                food.status = 'collected'
            
            # Update request status
            req.status = 'accepted'
            
            db.session.add(transaction)
            db.session.commit()
            # Also persist a copy in MongoDB for quick read endpoints
            try:
                if mongo_service and mongo_service.is_connected():
                    print(f"🔵 Storing transaction {transaction.txn_id} to MongoDB")
                    # Attempt to compute route data for analytics/storage
                    route_data = None
                    try:
                        from backend.services.route_optimizer import RouteOptimizer
                        donor = User.query.get(transaction.donor_id)
                        receiver = User.query.get(transaction.receiver_id)
                        if donor and receiver and donor.location_lat and donor.location_long and receiver.location_lat and receiver.location_long:
                            route_result = RouteOptimizer.optimize_route(
                                donor_lat=donor.location_lat,
                                donor_long=donor.location_long,
                                receiver_lat=receiver.location_lat,
                                receiver_long=receiver.location_long,
                                quantity=1,
                                pickup_date=transaction.pickup_date  # Pass pickup_date for time window enforcement
                            )
                            if route_result.get('success'):
                                route_data = route_result
                    except Exception as e:
                        print(f"⚠️ Route optimization (matching) failed (non-blocking): {e}")

                    mongo_service.store_transaction(
                        txn_id=transaction.txn_id,
                        donor_id=transaction.donor_id,
                        receiver_id=transaction.receiver_id,
                        food_id=transaction.food_id,
                        request_id=transaction.request_id,
                        status=transaction.status,
                        route_data=route_data,
                        quantity=transaction.quantity,
                        pickup_date=transaction.pickup_date
                    )
                    print(f"✅ Transaction {transaction.txn_id} stored to MongoDB")
                else:
                    print(f"⚠️ MongoDB not connected, skipping transaction storage")
            except Exception as e:
                # Non-fatal: don't block transaction if Mongo write fails
                print(f"❌ Failed to store transaction {transaction.txn_id} to MongoDB: {str(e)}")
                pass
            
            # SYNC ANALYTICS AFTER TRANSACTION - NON-BLOCKING
            try:
                from backend.services.analytics_service import AnalyticsService
                AnalyticsService.sync_analytics_after_transaction(transaction, food)
                print(f"✅ Analytics sync completed for transaction {transaction.txn_id}")
            except Exception as ae:
                print(f"❌ Analytics sync failed (non-blocking): {ae}")
                import traceback
                traceback.print_exc()
            
            return {
                "success": True,
                "transaction_id": transaction.txn_id,
                "message": f"Match created successfully"
            }
        
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "error": f"Error creating transaction: {str(e)}"
            }

    @staticmethod
    def _fuzzy_match_food_type(food_name: str, request_type: str) -> bool:
        """
        Fuzzy match food types. Allows partial matches.
        E.g., "rice" matches "cooked rice", "rice grains"
        """
        if food_name == request_type:
            return True
        
        if food_name in request_type or request_type in food_name:
            return True
        
        # Check if words overlap
        food_words = set(food_name.split())
        request_words = set(request_type.split())
        if food_words & request_words:  # Has common words
            return True
        
        return False

    @staticmethod
    def _calculate_urgency_match(urgency_level: str, expiry_date) -> str:
        """
        Calculate how well urgency level matches expiry date.
        High urgency = need food quickly, low expiry = must be used soon = good match
        """
        days_until_expiry = (expiry_date - datetime.now().date()).days
        
        if urgency_level == 'high':
            if days_until_expiry <= 3:
                return 'high'
            elif days_until_expiry <= 7:
                return 'medium'
            else:
                return 'low'
        elif urgency_level == 'medium':
            if days_until_expiry <= 7:
                return 'high'
            elif days_until_expiry <= 14:
                return 'medium'
            else:
                return 'low'
        else:  # low urgency
            return 'low'
