#!/usr/bin/env python3
"""
Test script for route optimization time window constraints
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import datetime, timedelta
from services.route_optimizer import RouteOptimizer

def test_time_windows():
    """Test various time window scenarios"""
    
    print("=" * 60)
    print("Testing Route Optimization Time Window Constraints")
    print("=" * 60)
    
    # Test 1: Valid time window (4 hours in advance)
    print("\n1️⃣ Test: Valid time window (4 hours advance)")
    pickup_time = datetime.now() + timedelta(hours=4)
    result = RouteOptimizer.optimize_route(
        donor_lat=23.7599,
        donor_long=76.3421,
        receiver_lat=23.7703,
        receiver_long=76.3511,
        quantity=50,
        pickup_date=pickup_time
    )
    print(f"   Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"   Warning: {result['route'].get('time_window_warning', 'None')}")
    if result['success'] and not result['route'].get('time_window_warning'):
        print(f"   ✅ Time window is feasible")
    
    # Test 2: Insufficient time window (30 minutes)
    print("\n2️⃣ Test: Insufficient time window (30 min advance)")
    soon_pickup = datetime.now() + timedelta(minutes=30)
    result = RouteOptimizer.optimize_route(
        donor_lat=23.7599,
        donor_long=76.3421,
        receiver_lat=23.8000,
        receiver_long=76.4000,  # Further distance
        quantity=50,
        pickup_date=soon_pickup
    )
    print(f"   Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"   Warning: {result['route'].get('time_window_warning', 'None')}")
    if result['route'].get('time_window_warning'):
        print(f"   ✅ Correctly detected insufficient time")
    
    # Test 3: Past pickup time
    print("\n3️⃣ Test: Past pickup time (2 hours ago)")
    past_pickup = datetime.now() - timedelta(hours=2)
    result = RouteOptimizer.optimize_route(
        donor_lat=23.7599,
        donor_long=76.3421,
        receiver_lat=23.7703,
        receiver_long=76.3511,
        quantity=50,
        pickup_date=past_pickup
    )
    print(f"   Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"   Warning: {result['route'].get('time_window_warning', 'None')}")
    if result['route'].get('time_window_warning') and 'past' in result['route']['time_window_warning'].lower():
        print(f"   ✅ Correctly detected past pickup time")
    
    # Test 4: Very far future (10 days)
    print("\n4️⃣ Test: Far future pickup (10 days advance)")
    future_pickup = datetime.now() + timedelta(days=10)
    result = RouteOptimizer.optimize_route(
        donor_lat=23.7599,
        donor_long=76.3421,
        receiver_lat=23.7703,
        receiver_long=76.3511,
        quantity=50,
        pickup_date=future_pickup
    )
    print(f"   Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"   Warning: {result['route'].get('time_window_warning', 'None')}")
    if result['success'] and result['route'].get('time_window_warning'):
        print(f"   ✅ Correctly warned about far future scheduling")
    
    # Test 5: No pickup date (backward compatibility)
    print("\n5️⃣ Test: No pickup date provided (backward compatibility)")
    result = RouteOptimizer.optimize_route(
        donor_lat=23.7599,
        donor_long=76.3421,
        receiver_lat=23.7703,
        receiver_long=76.3511,
        quantity=50
    )
    print(f"   Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"   Warning: {result['route'].get('time_window_warning', 'None')}")
    if result['success'] and not result['route'].get('time_window_warning'):
        print(f"   ✅ Works without time window constraints")
    
    # Test 6: Optimal window (2 hours advance)
    print("\n6️⃣ Test: Optimal time window (2 hours advance)")
    optimal_pickup = datetime.now() + timedelta(hours=2)
    result = RouteOptimizer.optimize_route(
        donor_lat=23.7599,
        donor_long=76.3421,
        receiver_lat=23.7703,
        receiver_long=76.3511,
        quantity=50,
        pickup_date=optimal_pickup
    )
    print(f"   Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"   Warning: {result['route'].get('time_window_warning', 'None')}")
    print(f"   Distance: {result['route']['total_distance_km']} km")
    print(f"   Estimated Time: {result['route']['estimated_time_hours']} hours")
    print(f"   Scheduled Pickup: {result['route'].get('scheduled_pickup', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("All tests completed! ✅")
    print("=" * 60)

if __name__ == "__main__":
    test_time_windows()
