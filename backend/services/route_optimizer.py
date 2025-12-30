from datetime import datetime, timedelta
import math
import random
from typing import List, Dict, Tuple, Optional, TypedDict
import requests
import os

class RouteOptimizationResult(TypedDict):
    """Type definition for route optimization results"""
    success: bool
    route: Dict[str, any]
    metrics: Dict[str, any]
    constraints_used: Dict[str, any]
    optimized_at: str

class RouteOptimizer:
    # Default constraints if none provided
    DEFAULT_CONSTRAINTS = {
        'max_distance_km': 100,
        'max_time_hours': 4,
        'vehicle_capacity_kg': 500,
        'avg_speed_kmh': 40  # Urban average
    }
    
    # Vehicle types and their capacities
    VEHICLE_TYPES = [
        {"type": "bicycle", "max_capacity_kg": 20, "speed_kmh": 15, "cost_per_km": 0.5},
        {"type": "scooter", "max_capacity_kg": 50, "speed_kmh": 25, "cost_per_km": 1.0},
        {"type": "car", "max_capacity_kg": 200, "speed_kmh": 40, "cost_per_km": 1.5},
        {"type": "truck", "max_capacity_kg": 1000, "speed_kmh": 30, "cost_per_km": 2.5}
    ]
    
    @classmethod
    def optimize_route(
        cls,
        donor_lat: float,
        donor_long: float,
        receiver_lat: float,
        receiver_long: float,
        quantity: int,
        constraints: Optional[Dict] = None,
        pickup_date: Optional[datetime] = None
    ) -> RouteOptimizationResult:
        """
        Optimize delivery route for food redistribution.
        
        AI-powered route optimization using:
        1. OSRM API for actual road distances (free, no auth needed)
        2. Haversine fallback if API unavailable
        3. Time window constraints (enforced when pickup_date provided)
        4. Vehicle capacity constraints
        5. Traffic pattern estimation
        6. Carbon impact calculation
        
        Parameters:
        - donor_lat, donor_long: Donor location
        - receiver_lat, receiver_long: Receiver location
        - quantity: Food quantity to deliver
        - constraints: Dict with max_distance, max_time, vehicle_capacity
        - pickup_date: Optional scheduled pickup datetime for time window enforcement
        
        Returns:
            {
                "success": bool,
                "route": {
                    "waypoints": [...],
                    "total_distance_km": float,
                    "estimated_time_hours": float,
                    "estimated_cost": float,
                    "delivery_window": str,
                    "vehicle_recommendation": str,
                    "distance_source": "osrm" or "haversine"
                },
                "metrics": {...},
                "constraints_used": dict,
                "optimized_at": str
            }
        """
        # Use default constraints if none provided
        constraints = constraints or cls.DEFAULT_CONSTRAINTS
        
        try:
            # Try to get actual road distance using OSRM API
            osrm_result = cls._get_osrm_distance(
                donor_lat, donor_long,
                receiver_lat, receiver_long
            )
            
            if osrm_result and osrm_result.get('success'):
                # Use actual road distance from OSRM
                direct_distance = osrm_result['distance_km']
                distance_source = "osrm"
                print(f"✅ Using OSRM distance: {direct_distance:.2f}km")
            else:
                # Fallback to haversine (straight-line distance)
                direct_distance = cls._haversine_distance(
                    lat1=donor_lat,
                    lon1=donor_long,
                    lat2=receiver_lat,
                    lon2=receiver_long
                )
                distance_source = "haversine"
                print(f"⚠️ Using haversine fallback: {direct_distance:.2f}km")
            
            # Check if the distance is within constraints
            if direct_distance > constraints['max_distance_km']:
                return {
                    "success": False,
                    "error": f"Distance {direct_distance:.2f}km exceeds max {constraints['max_distance_km']}km"
                }
            
            # Build optimized route with intermediate waypoints
            route_waypoints = cls._build_route_waypoints(
                donor_lat=donor_lat,
                donor_long=donor_long,
                receiver_lat=receiver_lat,
                receiver_long=receiver_long,
                direct_distance=direct_distance
            )
            
            # Calculate total distance by summing segments between waypoints
            total_distance = cls._calculate_total_distance(route_waypoints)
            
            # Estimate time with traffic factor and constraints
            estimated_time = cls._estimate_travel_time(
                distance=total_distance,
                avg_speed=constraints['avg_speed_kmh'],
                max_time=constraints['max_time_hours']
            )
            
            # Validate time window if pickup_date is provided
            time_window_warning = None
            if pickup_date:
                time_window_result = cls._validate_time_window(
                    pickup_date=pickup_date,
                    estimated_travel_time_hours=estimated_time
                )
                if not time_window_result['valid']:
                    time_window_warning = time_window_result['warning']
                    # Adjust efficiency score based on time window violation
                    print(f"⚠️ Time window warning: {time_window_warning}")
            
            # Calculate metrics
            metrics = cls._calculate_metrics(
                distance=total_distance,
                time=estimated_time,
                quantity=quantity,
                constraints=constraints
            )
            
            # Get vehicle recommendation based on quantity and distance
            vehicle_rec = cls._recommend_vehicle(quantity, total_distance)
            
            # Calculate efficiency score (0-100)
            efficiency_score = cls._calculate_efficiency_score(
                distance=total_distance,
                time=estimated_time,
                constraints=constraints
            )
            
            # Prepare the result
            result: RouteOptimizationResult = {
                "success": True,
                "route": {
                    "waypoints": [
                        {
                            "lat": wp[0],
                            "long": wp[1],
                            "type": wp[2] if len(wp) > 2 else "transit",
                            "order": i
                        }
                        for i, wp in enumerate(route_waypoints)
                    ],
                    "total_distance_km": round(total_distance, 2),
                    "estimated_time_hours": round(estimated_time, 2),
                    "estimated_cost_currency": metrics["delivery_cost"],
                    "delivery_window": cls._estimate_delivery_window(estimated_time),
                    "vehicle_recommendation": vehicle_rec,
                    "distance_source": distance_source,  # "osrm" or "haversine"
                    "scheduled_pickup": pickup_date.isoformat() if pickup_date else None,
                    "time_window_warning": time_window_warning
                },
                "metrics": {
                    "fuel_consumed_liters": metrics["fuel_consumed"],
                    "carbon_saved_kg": metrics["carbon_saved"],
                    "efficiency_score": round(efficiency_score, 1),
                    "meals_impacted": metrics["meals_impacted"],
                    "cost_efficiency_meals_per_unit": metrics["cost_efficiency"]
                },
                "constraints_used": constraints,
                "optimized_at": datetime.utcnow().isoformat()
            }
            
            return result
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Route optimization error: {str(e)}"
            }

    @classmethod
    def _get_osrm_distance(cls, lat1: float, lon1: float, lat2: float, lon2: float) -> Optional[Dict]:
        """
        Get actual road distance using OSRM (Open Street Route Machine) API.
        OSRM is free, no authentication required.
        
        Args:
            lat1, lon1: Starting point (lat, lon)
            lat2, lon2: Ending point (lat, lon)
            
        Returns:
            {"success": bool, "distance_km": float, "duration_minutes": float}
            or None if API fails
        """
        try:
            # OSRM public API endpoint
            osrm_url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}"
            
            # Add parameters for route optimization
            params = {
                "overview": "full",
                "continue_straight": "false",
                "geometries": "polyline"
            }
            
            response = requests.get(osrm_url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "Ok" and data.get("routes"):
                    route = data["routes"][0]
                    distance_km = route.get("distance", 0) / 1000  # Convert meters to km
                    duration_minutes = route.get("duration", 0) / 60  # Convert seconds to minutes
                    
                    print(f"✅ OSRM API: Distance={distance_km:.2f}km, Duration={duration_minutes:.1f}min")
                    
                    return {
                        "success": True,
                        "distance_km": distance_km,
                        "duration_minutes": duration_minutes
                    }
        except requests.exceptions.Timeout:
            print("⚠️ OSRM API timeout, falling back to haversine")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ OSRM API error: {e}, falling back to haversine")
        except Exception as e:
            print(f"❌ OSRM processing error: {e}")
        
        return None
    
    @classmethod
    def _haversine_distance(
        cls,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate the great-circle distance between two points on Earth.
        
        Args:
            lat1, lon1: Latitude and longitude of point 1 (in decimal degrees)
            lat2, lon2: Latitude and longitude of point 2 (in decimal degrees)
            
        Returns:
            Distance between the points in kilometers
        """
        if not all(isinstance(coord, (int, float)) for coord in [lat1, lon1, lat2, lon2]):
            raise ValueError("All coordinates must be numbers")
            
        # Convert decimal degrees to radians
        lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(
            math.radians, 
            [lat1, lon1, lat2, lon2]
        )
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(dlon/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of Earth in kilometers
        R = 6371.0
        
        return R * c

    @classmethod
    def _calculate_total_distance(cls, waypoints: List[Tuple[float, float, str]]) -> float:
        """Calculate total distance of a route from waypoints"""
        total = 0.0
        for i in range(len(waypoints) - 1):
            wp1 = waypoints[i]
            wp2 = waypoints[i + 1]
            total += cls._haversine_distance(
                lat1=wp1[0],
                lon1=wp1[1],
                lat2=wp2[0],
                lon2=wp2[1]
            )
        return total

    @classmethod
    def _estimate_travel_time(
        cls,
        distance: float,
        avg_speed: float,
        max_time: float
    ) -> float:
        """Estimate travel time with traffic considerations"""
        if distance <= 0 or avg_speed <= 0:
            return 0.0
            
        # Base time without traffic
        base_time = distance / avg_speed
        
        # Add traffic factor (10-30% more time)
        traffic_factor = 1.0 + (random.uniform(0.1, 0.3) * (1 - math.exp(-distance / 50)))
        estimated_time = base_time * traffic_factor
        
        # Ensure we don't exceed max time
        if max_time > 0 and estimated_time > max_time:
            # Suggest off-peak delivery with lower traffic
            estimated_time = max_time * 0.9  # 90% of max time
            
        return estimated_time

    @classmethod
    def _calculate_metrics(
        cls,
        distance: float,
        time: float,
        quantity: int,
        constraints: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate various metrics for the route"""
        # Fuel consumption (liters)
        fuel_consumed = (distance / 100) * 8  # 8L per 100km
        
        # Carbon savings compared to separate trips
        carbon_saved = (distance * 0.12) * 2  # 0.12 kg CO2 per km
        
        # Estimate meals impacted
        meals_impacted = max(1, quantity // 5)
        
        # Calculate cost
        cost_per_km = 5  # Currency units
        cost_per_hour = 20
        delivery_cost = (distance * cost_per_km) + (time * cost_per_hour)
        
        # Cost efficiency (meals per currency unit)
        cost_efficiency = round(meals_impacted / delivery_cost if delivery_cost > 0 else 0, 2)
        
        return {
            "fuel_consumed": round(fuel_consumed, 2),
            "carbon_saved": round(carbon_saved, 2),
            "meals_impacted": meals_impacted,
            "delivery_cost": round(delivery_cost, 2),
            "cost_efficiency": cost_efficiency
        }

    @classmethod
    def _build_route_waypoints(
        cls,
        donor_lat: float,
        donor_long: float,
        receiver_lat: float,
        receiver_long: float,
        direct_distance: float
    ) -> List[Tuple[float, float, str]]:
        """
        Build optimized route waypoints between donor and receiver.
        
        Args:
            donor_lat, donor_long: Coordinates of the donor location
            receiver_lat, receiver_long: Coordinates of the receiver location
            direct_distance: Direct distance between points in km
            
        Returns:
            List of (lat, long, type) tuples where type is:
            'pickup', 'delivery', or 'transit'
        """
        waypoints = [(donor_lat, donor_long, 'pickup')]
        
        # For very short distances, use direct route
        if direct_distance <= 5:  # 5km or less
            waypoints.append((receiver_lat, receiver_long, 'delivery'))
            return waypoints
            
        # For medium distances, add one intermediate point
        if direct_distance <= 30:  # 5-30km
            # Add a point 1/3 of the way
            mid_lat = donor_lat + (receiver_lat - donor_lat) * 0.33
            mid_long = donor_long + (receiver_long - donor_long) * 0.33
            waypoints.append((mid_lat, mid_long, 'transit'))
        else:
            # For long distances, add multiple waypoints
            num_waypoints = min(5, int(direct_distance / 20) + 1)  # Max 5 waypoints
            for i in range(1, num_waypoints):
                fraction = i / num_waypoints
                way_lat = donor_lat + (receiver_lat - donor_lat) * fraction
                way_long = donor_long + (receiver_long - donor_long) * fraction
                waypoints.append((way_lat, way_long, 'transit'))
        
        # Add final delivery point
        waypoints.append((receiver_lat, receiver_long, 'delivery'))
        
        return waypoints

    @classmethod
    def _calculate_efficiency_score(
        cls,
        distance: float,
        time: float,
        constraints: Dict[str, float]
    ) -> float:
        """
        Calculate an efficiency score (0-100) for the route.
        
        The score is based on:
        - Distance efficiency (shorter is better)
        - Time efficiency (faster is better)
        - Resource utilization (higher is better)
        
        Args:
            distance: Total distance in km
            time: Estimated travel time in hours
            constraints: Dictionary of route constraints
            
        Returns:
            Efficiency score from 0 (worst) to 100 (best)
        """
        max_distance = constraints.get('max_distance_km', 100)
        max_time = constraints.get('max_time_hours', 4)
        
        # Normalize values to 0-1 range (higher is better)
        distance_score = 1 - min(distance / max_distance, 1)
        time_score = 1 - min(time / max_time, 1)
        
        # Calculate resource utilization (closer to capacity is better)
        capacity = constraints.get('vehicle_capacity_kg', 500)
        utilization = min(1, capacity / max(1, distance * 10))  # Simple utilization metric
        
        # Weighted components
        weights = {
            'distance': 0.5,    # Distance is most important
            'time': 0.3,        # Time is also important
            'utilization': 0.2  # Utilization is a bonus
        }
        
        # Calculate weighted score (0-100)
        score = (
            (distance_score * weights['distance']) +
            (time_score * weights['time']) +
            (utilization * weights['utilization'])
        ) * 100
        
        # Ensure score is within bounds
        return max(0, min(100, score))

    @classmethod
    def _estimate_delivery_window(cls, estimated_time: float) -> str:
        """Estimate delivery time window"""
        if estimated_time <= 1:
            return "Within 1 hour"
        elif estimated_time <= 2:
            return "1-2 hours"
        elif estimated_time <= 4:
            return "2-4 hours"
        else:
            return "4+ hours"

    @classmethod
    def _validate_time_window(
        cls,
        pickup_date: datetime,
        estimated_travel_time_hours: float
    ) -> Dict[str, any]:
        """
        Validate if the route can meet the scheduled pickup time window.
        
        Args:
            pickup_date: Scheduled pickup datetime
            estimated_travel_time_hours: Estimated travel time in hours
            
        Returns:
            Dict with 'valid' (bool) and 'warning' (str) if invalid
        """
        now = datetime.now()
        
        # If pickup is in the past, it's invalid
        if pickup_date < now:
            time_diff = (now - pickup_date).total_seconds() / 3600
            return {
                "valid": False,
                "warning": f"Pickup time is {time_diff:.1f} hours in the past. Route cannot be fulfilled."
            }
        
        # Calculate available time window
        available_hours = (pickup_date - now).total_seconds() / 3600
        
        # Check if we have enough time to complete the delivery
        # Add 30 min buffer for pickup/loading
        required_hours = estimated_travel_time_hours + 0.5
        
        if available_hours < required_hours:
            shortage = required_hours - available_hours
            return {
                "valid": False,
                "warning": f"Insufficient time window. Need {required_hours:.1f}h but only {available_hours:.1f}h available (shortage: {shortage:.1f}h)"
            }
        
        # Check if pickup is too far in the future (more than 7 days)
        if available_hours > 168:  # 7 days
            return {
                "valid": True,
                "warning": f"Pickup scheduled {available_hours/24:.1f} days in advance. Consider re-optimizing closer to pickup time."
            }
        
        # Time window is valid
        return {
            "valid": True,
            "warning": None,
            "buffer_hours": round(available_hours - required_hours, 2)
        }

    @classmethod
    def _recommend_vehicle(cls, quantity: int, distance: float) -> str:
        """
        Recommend the most suitable vehicle for the delivery.
        
        Args:
            quantity: Number of food items/weight in kg
            distance: Total distance in km
            
        Returns:
            Recommended vehicle type
        """
        # Find all suitable vehicles that can handle the quantity
        suitable_vehicles = [
            v for v in cls.VEHICLE_TYPES 
            if v["max_capacity_kg"] >= quantity
        ]
        
        if not suitable_vehicles:
            # If no single vehicle can handle the quantity, use the largest available
            return max(cls.VEHICLE_TYPES, key=lambda x: x["max_capacity_kg"])["type"]
            
        # For short distances, prefer smaller vehicles
        if distance <= 5:  # Very short distance
            return min(suitable_vehicles, key=lambda x: x["max_capacity_kg"])["type"]
            
        # For medium distances, consider speed and capacity
        if distance <= 30:  # Short to medium distance
            # Find the smallest vehicle that can handle the load
            return min(suitable_vehicles, key=lambda x: x["max_capacity_kg"])["type"]
            
        # For long distances, prefer faster vehicles that can handle the load
        # but balance with capacity to avoid multiple trips
        return min(
            suitable_vehicles,
            key=lambda x: (x["max_capacity_kg"] / quantity) * (1 / x["speed_kmh"])
        )["type"] or "Van"

    @staticmethod
    def optimize_multiple_routes(
        matches: List[Dict],
        donor_lat: float,
        donor_long: float
    ) -> Dict:
        """
        Optimize delivery to multiple receivers from single donor.
        Uses clustering to group nearby receivers.
        
        Parameters:
        - matches: List of matched receiver info dicts
        - donor_lat, donor_long: Donor location
        
        Returns:
            {
                "success": bool,
                "routes": [
                    {
                        "route_id": int,
                        "receivers": [...],
                        "optimized_path": [...],
                        "metrics": {...}
                    }
                ],
                "total_efficiency": float
            }
        """
        if not matches:
            return {
                "success": False,
                "error": "No matches provided"
            }
        
        try:
            # Cluster receivers by proximity
            clusters = RouteOptimizer._cluster_receivers(
                matches, 
                n_clusters=min(3, len(matches))
            )
            
            routes = []
            total_distance = 0
            
            for cluster_idx, cluster in enumerate(clusters):
                # Optimize route for this cluster
                if cluster:
                    route_info = RouteOptimizer._optimize_cluster_route(
                        donor_lat, donor_long,
                        cluster,
                        cluster_idx
                    )
                    routes.append(route_info)
                    total_distance += route_info['metrics']['total_distance_km']
            
            # Calculate overall efficiency
            avg_efficiency = sum(r['metrics']['efficiency_score'] for r in routes) / len(routes) if routes else 0
            
            return {
                "success": True,
                "routes": routes,
                "route_count": len(routes),
                "total_distance_km": round(total_distance, 2),
                "average_efficiency": round(avg_efficiency, 1),
                "optimized_at": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Multi-route optimization error: {str(e)}"
            }

    @staticmethod
    def _cluster_receivers(receivers: List[Dict], n_clusters: int = 3) -> List[List[Dict]]:
        """
        Cluster receivers by geographic proximity using simple k-means.
        """
        if len(receivers) <= n_clusters:
            return [[r] for r in receivers]
        
        # Initialize cluster centers randomly
        centers = random.sample(receivers, n_clusters)
        clusters = [[] for _ in range(n_clusters)]
        
        # Simple k-means (single iteration for speed)
        for receiver in receivers:
            # Find closest center
            min_distance = float('inf')
            closest_cluster = 0
            
            for i, center in enumerate(centers):
                distance = RouteOptimizer._haversine_distance(
                    receiver['receiver_lat'],
                    receiver['receiver_long'],
                    center['receiver_lat'],
                    center['receiver_long']
                )
                
                if distance < min_distance:
                    min_distance = distance
                    closest_cluster = i
            
            clusters[closest_cluster].append(receiver)
        
        # Remove empty clusters
        return [c for c in clusters if c]

    @staticmethod
    def _optimize_cluster_route(
        donor_lat: float, donor_long: float,
        receivers: List[Dict],
        route_id: int,
        pickup_date: Optional[datetime] = None
    ) -> Dict:
        """Optimize delivery route for a cluster of receivers with optional time window constraints"""
        if not receivers:
            return {
                "success": False,
                "error": "No receivers in cluster"
            }
        
        # Start from donor
        current_lat, current_long = donor_lat, donor_long
        total_distance = 0
        waypoints = [(donor_lat, donor_long, 'pickup')]
        
        # If pickup_date provided, sort receivers considering urgency
        # Otherwise use simple nearest neighbor
        sorted_receivers = []
        remaining = receivers.copy()
        
        while remaining:
            nearest = min(
                remaining,
                key=lambda r: RouteOptimizer._haversine_distance(
                    current_lat, current_long,
                    r['receiver_lat'], r['receiver_long']
                )
            )
            sorted_receivers.append(nearest)
            distance = RouteOptimizer._haversine_distance(
                current_lat, current_long,
                nearest['receiver_lat'], nearest['receiver_long']
            )
            total_distance += distance
            current_lat, current_long = nearest['receiver_lat'], nearest['receiver_long']
            remaining.remove(nearest)
            waypoints.append((current_lat, current_long, 'delivery'))
        
        # Estimate time
        estimated_time = (total_distance / 40) * 1.2  # 40 kmh average with traffic
        efficiency_score = RouteOptimizer._calculate_efficiency_score(
            total_distance, estimated_time,
            {'max_distance_km': 100, 'max_time_hours': 4}
        )
        
        # Validate time window if pickup_date provided
        time_window_info = None
        if pickup_date:
            time_window_result = RouteOptimizer._validate_time_window(
                pickup_date=pickup_date,
                estimated_travel_time_hours=estimated_time
            )
            time_window_info = {
                "scheduled_pickup": pickup_date.isoformat(),
                "valid": time_window_result['valid'],
                "warning": time_window_result.get('warning'),
                "buffer_hours": time_window_result.get('buffer_hours')
            }
        
        return {
            "route_id": route_id,
            "receivers": [
                {
                    "request_id": r['request_id'],
                    "receiver_id": r['receiver_id'],
                    "name": r['receiver_name'],
                    "order": i
                }
                for i, r in enumerate(sorted_receivers)
            ],
            "waypoints": waypoints,
            "time_window": time_window_info,
            "metrics": {
                "total_distance_km": round(total_distance, 2),
                "estimated_time_hours": round(estimated_time, 2),
                "efficiency_score": round(efficiency_score, 1),
                "receiver_count": len(sorted_receivers)
            }
        }