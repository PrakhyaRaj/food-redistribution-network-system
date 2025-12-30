"""
Test script to verify route optimization is working properly.
This will check:
1. If OSRM API is accessible
2. If route_data is being stored in transactions
3. If redistribution_analytics has distance_source field
"""
import requests
import json
from pymongo import MongoClient

def test_osrm_api():
    """Test if OSRM API is accessible."""
    print("=" * 60)
    print("1. Testing OSRM API...")
    print("=" * 60)
    
    # Test coordinates (example: London to Manchester)
    url = "http://router.project-osrm.org/route/v1/driving/-0.127758,51.507351;-2.244644,53.483959"
    
    try:
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 'Ok':
                distance = data['routes'][0]['distance'] / 1000  # Convert to km
                duration = data['routes'][0]['duration'] / 60  # Convert to minutes
                print(f"✅ OSRM API is working!")
                print(f"   Distance: {distance:.2f} km")
                print(f"   Duration: {duration:.2f} minutes")
                return True
            else:
                print(f"❌ OSRM returned error: {data.get('code')}")
                return False
        else:
            print(f"❌ OSRM API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to OSRM: {e}")
        return False

def test_mongodb_data():
    """Test if route_data is being stored in MongoDB."""
    print("\n" + "=" * 60)
    print("2. Testing MongoDB Data...")
    print("=" * 60)
    
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['food_redistribution']
        
        # Check transactions collection
        transactions = db.transactions
        total_txns = transactions.count_documents({})
        txns_with_route = transactions.count_documents({"route_data": {"$exists": True}})
        
        print(f"Total transactions: {total_txns}")
        print(f"Transactions with route_data: {txns_with_route}")
        
        if txns_with_route > 0:
            # Get a sample transaction with route_data
            sample = transactions.find_one({"route_data": {"$exists": True}})
            if sample:
                print("\n✅ Sample transaction with route_data found:")
                print(f"   Transaction ID: {sample.get('txn_id')}")
                route_data = sample.get('route_data', {})
                route = route_data.get('route', {})
                print(f"   Distance: {route.get('distance', 'N/A')} km")
                print(f"   Distance Source: {route.get('distance_source', 'N/A')}")
                print(f"   Time: {route.get('time', 'N/A')} minutes")
                print(f"   Vehicle: {route.get('vehicle', 'N/A')}")
        else:
            print("⚠️  No transactions with route_data found.")
            print("   Create a new match to test route optimization.")
        
        # Check redistribution_analytics collection
        print("\n" + "-" * 60)
        analytics = db.redistribution_analytics
        total_analytics = analytics.count_documents({})
        analytics_with_osrm = analytics.count_documents({"distance_source": "osrm"})
        analytics_with_haversine = analytics.count_documents({"distance_source": "haversine"})
        
        print(f"Total analytics records: {total_analytics}")
        print(f"Records with OSRM distance: {analytics_with_osrm}")
        print(f"Records with Haversine distance: {analytics_with_haversine}")
        
        if total_analytics > 0:
            sample_analytics = analytics.find_one({"distance_source": {"$exists": True}})
            if sample_analytics:
                print("\n✅ Sample analytics record:")
                print(f"   Transaction ID: {sample_analytics.get('transaction_id')}")
                print(f"   Distance: {sample_analytics.get('distance_km')} km")
                print(f"   Distance Source: {sample_analytics.get('distance_source')}")
                print(f"   Food: {sample_analytics.get('food_name')}")
                print(f"   Quantity: {sample_analytics.get('quantity_kg')} kg")
        else:
            print("⚠️  No analytics records found.")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False

def check_backend_dependencies():
    """Check if backend has requests library installed."""
    print("\n" + "=" * 60)
    print("3. Checking Backend Dependencies...")
    print("=" * 60)
    
    try:
        import requests
        print(f"✅ requests library installed (version {requests.__version__})")
        return True
    except ImportError:
        print("❌ requests library not found!")
        print("   Run: pip install requests")
        return False

def main():
    print("\n🔍 Food Redistribution Network - Route Optimization Test")
    print("=" * 60)
    
    results = {
        'osrm': test_osrm_api(),
        'dependencies': check_backend_dependencies(),
        'mongodb': test_mongodb_data()
    }
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = all(results.values())
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test.upper()}")
    
    if all_passed:
        print("\n🎉 All tests passed! Route optimization should be working.")
        print("\nNext steps:")
        print("1. Start backend: cd backend && python app.py")
        print("2. Start frontend: cd frontend && npm run dev")
        print("3. Create a new match between donor and receiver")
        print("4. Check dashboards for route optimization display")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
