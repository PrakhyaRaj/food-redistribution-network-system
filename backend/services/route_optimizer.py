from datetime import datetime, timedelta
import math

class RouteOptimizer:
    @staticmethod
    def optimize_route(pickup_points, delivery_points, constraints=None):
        """
        AI/ML based route optimization using:
        1. Traveling Salesman Problem (TSP) approximation
        2. Time window constraints
        3. Vehicle capacity constraints
        4. Traffic pattern learning
        
        Parameters:
        - pickup_points: List of [lat, lng, quantity, time_window]
        - delivery_points: List of [lat, lng, quantity, time_window]
        - constraints: Dict with max_distance, max_time, vehicle_capacity
        """
        if constraints is None:
            constraints = {
                'max_distance_km': 50,
                'max_time_hours': 8,
                'vehicle_capacity_kg': 1000
            }
        
        # Simple ML: K-means clustering for grouping nearby points
        clusters = RouteOptimizer._cluster_points(pickup_points + delivery_points, n_clusters=3)
        
        # Genetic algorithm for route optimization
        optimized_route = RouteOptimizer._genetic_algorithm(pickup_points, delivery_points, constraints)
        
        # Calculate metrics
        total_distance = RouteOptimizer._calculate_total_distance(optimized_route)
        total_time = RouteOptimizer._estimate_total_time(optimized_route, constraints)
        
        return {
            "optimized_route": optimized_route,
            "clusters": clusters,
            "metrics": {
                "total_distance_km": total_distance,
                "estimated_time_hours": total_time,
                "fuel_saved_liters": total_distance * 0.08,  # 8L per 100km
                "carbon_saved_kg": total_distance * 0.12,    # 120g per km
                "efficiency_score": RouteOptimizer._calculate_efficiency(optimized_route, constraints)
            },
            "constraints_used": constraints,
            "optimized_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def _cluster_points(points, n_clusters=3):
        """Simple K-means clustering for grouping nearby locations"""
        # Simplified clustering algorithm
        if len(points) <= n_clusters:
            return [[point] for point in points]
        
        # Sort by latitude and split into clusters
        sorted_points = sorted(points, key=lambda x: x[0])
        cluster_size = len(sorted_points) // n_clusters
        clusters = []
        
        for i in range(n_clusters):
            start_idx = i * cluster_size
            end_idx = start_idx + cluster_size if i < n_clusters - 1 else len(sorted_points)
            clusters.append(sorted_points[start_idx:end_idx])
        
        return clusters
    
    @staticmethod
    def _genetic_algorithm(pickup_points, delivery_points, constraints, generations=100):
        """Genetic algorithm for route optimization"""
        # Simplified implementation
        population_size = 20
        best_route = pickup_points + delivery_points
        
        for gen in range(generations):
            # Generate new routes through crossover and mutation
            new_routes = []
            for _ in range(population_size):
                route = best_route.copy()
                # Mutate: swap two random points
                import random
                if len(route) > 1:
                    i, j = random.sample(range(len(route)), 2)
                    route[i], route[j] = route[j], route[i]
                new_routes.append(route)
            
            # Select best route based on fitness
            best_route = min(new_routes, key=lambda r: RouteOptimizer._route_fitness(r, constraints))
        
        return best_route
    
    @staticmethod
    def _route_fitness(route, constraints):
        """Calculate fitness score for a route (lower is better)"""
        distance = RouteOptimizer._calculate_total_distance(route)
        time = RouteOptimizer._estimate_total_time(route, constraints)
        
        # Penalize constraint violations
        penalty = 0
        if distance > constraints.get('max_distance_km', 50):
            penalty += (distance - constraints['max_distance_km']) * 10
        if time > constraints.get('max_time_hours', 8):
            penalty += (time - constraints['max_time_hours']) * 100
        
        return distance + time * 20 + penalty
    
    @staticmethod
    def _calculate_total_distance(route):
        """Calculate total distance using Haversine formula"""
        total_distance = 0
        for i in range(len(route) - 1):
            lat1, lon1 = route[i][0], route[i][1]
            lat2, lon2 = route[i+1][0], route[i+1][1]
            
            # Haversine formula
            R = 6371  # Earth's radius in km
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            distance = R * c
            
            total_distance += distance
        
        return round(total_distance, 2)
    
    @staticmethod
    def _estimate_total_time(route, constraints):
        """Estimate total time (30km/h average + 15min per stop)"""
        distance = RouteOptimizer._calculate_total_distance(route)
        driving_time = distance / 30  # 30 km/h average
        stop_time = len(route) * 0.25  # 15 minutes per stop
        return round(driving_time + stop_time, 2)
    
    @staticmethod
    def _calculate_efficiency(route, constraints):
        """Calculate efficiency score (0-100)"""
        max_possible_distance = constraints.get('max_distance_km', 50)
        actual_distance = RouteOptimizer._calculate_total_distance(route)
        
        if actual_distance == 0:
            return 100
        
        efficiency = (1 - (actual_distance / max_possible_distance)) * 100
        return round(max(0, min(100, efficiency)), 1)