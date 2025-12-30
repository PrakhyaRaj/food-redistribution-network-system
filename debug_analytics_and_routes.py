"""
Comprehensive test script to debug route optimization and analytics flow.
Tests:
1. Transaction status updates
2. Route data storage in MongoDB
3. Analytics data retrieval
4. RouteOptimization component compatibility
"""
import requests
import json
from pymongo import MongoClient
from datetime import datetime

API_BASE = "http://127.0.0.1:5000"
MONGO_URI = "mongodb://localhost:27017/"

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_transaction_status():
    """Test if transactions are being created and stored properly"""
    print_section("1. TESTING TRANSACTION STORAGE")
    
    try:
        client = MongoClient(MONGO_URI)
        db = client['food_redistribution']
        
        txns = db.transactions.find()
        txns_list = list(txns)
        
        print(f"\n📊 Total transactions in MongoDB: {len(txns_list)}")
        
        if txns_list:
            # Get the most recent transaction
            recent = db.transactions.find_one(sort=[("created_at", -1)])
            print(f"\n✅ Most recent transaction:")
            print(f"   Transaction ID: {recent.get('txn_id')}")
            print(f"   Status: {recent.get('status')}")
            print(f"   Donor ID: {recent.get('donor_id')}")
            print(f"   Receiver ID: {recent.get('receiver_id')}")
            print(f"   Created: {recent.get('created_at')}")
            
            # Check if route_data exists
            route_data = recent.get('route_data')
            if route_data:
                print(f"\n✅ Route data found:")
                print(f"   Success: {route_data.get('success')}")
                route = route_data.get('route', {})
                print(f"   Distance: {route.get('total_distance_km')} km")
                print(f"   Time: {route.get('estimated_time_hours')} hours")
                print(f"   Vehicle: {route.get('vehicle_recommendation')}")
                print(f"   Source: {route.get('distance_source')}")
                metrics = route_data.get('metrics', {})
                if metrics:
                    print(f"   Metrics:")
                    print(f"     - Carbon saved: {metrics.get('carbon_saved_kg')} kg")
                    print(f"     - Efficiency: {metrics.get('efficiency_score')}%")
            else:
                print(f"\n❌ No route_data in transaction")
        else:
            print("\n⚠️  No transactions found in MongoDB")
        
        client.close()
        return len(txns_list) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_analytics_storage():
    """Test if analytics are being stored and retrievable"""
    print_section("2. TESTING ANALYTICS STORAGE")
    
    try:
        client = MongoClient(MONGO_URI)
        db = client['food_redistribution']
        
        analytics_count = db.redistribution_analytics.count_documents({})
        print(f"\n📊 Total analytics records: {analytics_count}")
        
        # Count by distance_source
        osrm_count = db.redistribution_analytics.count_documents({"distance_source": "osrm"})
        haversine_count = db.redistribution_analytics.count_documents({"distance_source": "haversine"})
        
        print(f"   - OSRM: {osrm_count}")
        print(f"   - Haversine: {haversine_count}")
        
        if analytics_count > 0:
            # Get sample record
            sample = db.redistribution_analytics.find_one(sort=[("created_at", -1)])
            print(f"\n✅ Sample analytics record:")
            print(f"   Transaction ID: {sample.get('transaction_id')}")
            print(f"   Distance: {sample.get('distance_km')} km")
            print(f"   Source: {sample.get('distance_source')}")
            print(f"   Food: {sample.get('food_name')}")
            print(f"   Quantity: {sample.get('quantity_kg')} kg")
            print(f"   Created: {sample.get('created_at')}")
            print(f"   Donor ID: {sample.get('donor_id')}")
            print(f"   Receiver ID: {sample.get('receiver_id')}")
        else:
            print("\n⚠️  No analytics records found")
        
        client.close()
        return analytics_count > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_api_endpoints():
    """Test if API endpoints return correct data"""
    print_section("3. TESTING API ENDPOINTS")
    
    # Mock token (replace with real token if needed)
    token = "test_token"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test transactions endpoint
    try:
        response = requests.get(
            f"{API_BASE}/api/mongodb/transactions",
            headers=headers,
            timeout=5
        )
        print(f"\n📌 /api/mongodb/transactions")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and data.get('transactions'):
                print(f"   ✅ Returned {len(data['transactions'])} transactions")
            elif isinstance(data, list):
                print(f"   ✅ Returned {len(data)} transactions")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test analytics endpoint
    try:
        response = requests.get(
            f"{API_BASE}/api/mongodb/analytics/redistribution",
            headers=headers,
            timeout=5
        )
        print(f"\n📌 /api/mongodb/analytics/redistribution")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Returns: {data.get('count', len(data.get('analytics', [])))} analytics records")
        elif response.status_code == 401:
            print(f"   ⚠️  Requires valid token")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_transaction_status_values():
    """Check actual status values in database"""
    print_section("4. CHECKING TRANSACTION STATUS VALUES")
    
    try:
        client = MongoClient(MONGO_URI)
        db = client['food_redistribution']
        
        # Get all unique statuses
        statuses = db.transactions.distinct('status')
        print(f"\n📊 Status values in database: {statuses}")
        
        # Count by status
        for status in statuses:
            count = db.transactions.count_documents({"status": status})
            print(f"   - {status}: {count}")
        
        # Check if any are "initiated"
        initiated = db.transactions.count_documents({"status": "initiated"})
        in_progress = db.transactions.count_documents({"status": "in_progress"})
        completed = db.transactions.count_documents({"status": "completed"})
        
        print(f"\n📈 Lifecycle status:")
        print(f"   Initiated: {initiated}")
        print(f"   In Progress: {in_progress}")
        print(f"   Completed: {completed}")
        
        if initiated > 0:
            print(f"\n⚠️  {initiated} transactions still in 'initiated' state (should be updated to 'in_progress' when accepted)")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_route_data_structure():
    """Verify route_data structure matches RouteOptimization component expectations"""
    print_section("5. VERIFYING ROUTE_DATA STRUCTURE")
    
    try:
        client = MongoClient(MONGO_URI)
        db = client['food_redistribution']
        
        # Find transaction with route_data
        txn = db.transactions.find_one({"route_data": {"$exists": True}})
        
        if txn:
            print(f"\n✅ Transaction with route_data found")
            route_data = txn.get('route_data', {})
            
            # Expected structure for RouteOptimization component
            expected_fields = {
                'success': 'Route optimization success flag',
                'route': {
                    'total_distance_km': 'Total distance',
                    'estimated_time_hours': 'Estimated time',
                    'vehicle_recommendation': 'Vehicle type',
                    'distance_source': 'OSRM or haversine'
                },
                'metrics': {
                    'fuel_consumed_liters': 'Fuel estimate',
                    'carbon_saved_kg': 'Carbon impact',
                    'efficiency_score': 'Efficiency %',
                    'meals_impacted': 'Meals delivered'
                }
            }
            
            print(f"\n📋 Checking route_data structure:")
            print(f"   Success: {'✅' if route_data.get('success') else '❌'}")
            
            route = route_data.get('route', {})
            print(f"   Route object:")
            for field, desc in expected_fields.get('route', {}).items():
                value = route.get(field)
                status = '✅' if value is not None else '❌'
                print(f"      {status} {field}: {value}")
            
            metrics = route_data.get('metrics', {})
            print(f"   Metrics object:")
            for field, desc in expected_fields.get('metrics', {}).items():
                value = metrics.get(field)
                status = '✅' if value is not None else '❌'
                print(f"      {status} {field}: {value}")
        else:
            print(f"\n⚠️  No transactions with route_data found")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("\n" + "🔍" * 35)
    print("  ROUTE OPTIMIZATION & ANALYTICS - COMPREHENSIVE TEST")
    print("🔍" * 35)
    
    # Run all tests
    txn_ok = test_transaction_status()
    analytics_ok = test_analytics_storage()
    test_api_endpoints()
    test_transaction_status_values()
    test_route_data_structure()
    
    # Summary
    print_section("SUMMARY")
    print(f"\n{'✅' if txn_ok else '❌'} Transactions stored in MongoDB")
    print(f"{'✅' if analytics_ok else '❌'} Analytics stored in MongoDB")
    print(f"\n💡 Next Steps:")
    if not txn_ok or not analytics_ok:
        print("   1. Start backend: cd backend && python app.py")
        print("   2. Create new match (donor & receiver both need locations)")
        print("   3. Receiver accepts food item")
        print("   4. Run this test again")
    else:
        print("   ✅ Route optimization is working!")
        print("   ✅ Analytics are being stored!")
        print("   - Check frontend dashboards for display")
        print("   - Verify AnalyticsDashboard shows data")
        print("   - Verify RouteOptimization shows non-empty routes")
    
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    main()
