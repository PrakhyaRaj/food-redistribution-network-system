#!/usr/bin/env python3
"""
Test script to verify analytics sync works after creating a transaction.
This test creates a transaction via the API and checks if MongoDB analytics are updated.
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
API_BASE = "http://localhost:5000"

def test_analytics_sync():
    """Test the complete analytics sync flow"""
    print("\n" + "="*70)
    print("🧪 ANALYTICS SYNC VERIFICATION TEST")
    print("="*70)
    
    # Step 1: Get current analytics
    print("\n📊 Step 1: Fetching current analytics...")
    try:
        resp = requests.get(f"{API_BASE}/api/analytics/summary?user_specific=false")
        if resp.status_code == 200:
            analytics_before = resp.json()
            print(f"✅ Current analytics retrieved:")
            print(f"   - Total food saved: {analytics_before.get('total_food_saved_kg', 0)} kg")
            print(f"   - People fed: {analytics_before.get('total_people_fed', 0)}")
            print(f"   - Carbon saved: {analytics_before.get('total_carbon_saved_kg', 0)} kg")
        else:
            print(f"❌ Failed to get analytics: {resp.status_code}")
            analytics_before = {}
    except Exception as e:
        print(f"❌ Error fetching analytics: {e}")
        analytics_before = {}
    
    # Step 2: List available food items and requests
    print("\n🍔 Step 2: Checking available food items and requests...")
    try:
        # Get food items
        food_resp = requests.get(f"{API_BASE}/api/food")
        if food_resp.status_code == 200:
            foods = food_resp.json().get('foods', [])
            available_foods = [f for f in foods if f.get('quantity_kg', 0) > 0 and f.get('status') == 'available']
            print(f"✅ Found {len(available_foods)} available food items")
            if available_foods:
                food = available_foods[0]
                print(f"   - First available: {food.get('name')} ({food.get('quantity_kg')} kg)")
                food_id = food.get('id')
        else:
            print(f"❌ Failed to get food: {food_resp.status_code}")
            available_foods = []
            food_id = None
        
        # Get requests
        req_resp = requests.get(f"{API_BASE}/api/requests")
        if req_resp.status_code == 200:
            reqs = req_resp.json().get('requests', [])
            open_requests = [r for r in reqs if r.get('status') != 'completed']
            print(f"✅ Found {len(open_requests)} open requests")
            if open_requests:
                req = open_requests[0]
                print(f"   - First open: {req.get('name')} (needs {req.get('quantity_required_kg')} kg)")
                request_id = req.get('id')
        else:
            print(f"❌ Failed to get requests: {req_resp.status_code}")
            open_requests = []
            request_id = None
            
    except Exception as e:
        print(f"❌ Error checking food/requests: {e}")
        food_id = None
        request_id = None
    
    # Step 3: Create a transaction (if we have food and request)
    if food_id and request_id:
        print(f"\n🔄 Step 3: Creating transaction (Food ID: {food_id}, Request ID: {request_id})...")
        try:
            create_url = f"{API_BASE}/api/requests/{request_id}/matches/{food_id}/create-transaction"
            resp = requests.post(create_url)
            
            if resp.status_code in [200, 201]:
                transaction = resp.json()
                print(f"✅ Transaction created successfully!")
                print(f"   - Transaction ID: {transaction.get('txn_id')}")
                print(f"   - Quantity: {transaction.get('quantity_kg')} kg")
                print(f"   - Status: {transaction.get('status')}")
                
                # Wait for analytics sync
                print("\n⏳ Waiting 3 seconds for analytics sync...")
                time.sleep(3)
                
                # Step 4: Check analytics again
                print("\n📊 Step 4: Fetching updated analytics...")
                resp = requests.get(f"{API_BASE}/api/analytics/summary?user_specific=false")
                if resp.status_code == 200:
                    analytics_after = resp.json()
                    food_after = analytics_after.get('total_food_saved_kg', 0)
                    food_before = analytics_before.get('total_food_saved_kg', 0)
                    
                    print(f"✅ Updated analytics retrieved:")
                    print(f"   - Total food saved: {food_after} kg (was {food_before} kg)")
                    print(f"   - People fed: {analytics_after.get('total_people_fed', 0)}")
                    print(f"   - Carbon saved: {analytics_after.get('total_carbon_saved_kg', 0)} kg")
                    
                    if food_after > food_before:
                        print(f"\n✅ SUCCESS! Analytics UPDATED by {food_after - food_before} kg")
                    else:
                        print(f"\n⚠️  Analytics NOT updated yet. May need to wait longer.")
                else:
                    print(f"❌ Failed to get updated analytics: {resp.status_code}")
            else:
                print(f"❌ Failed to create transaction: {resp.status_code}")
                print(f"   Response: {resp.text}")
                
        except Exception as e:
            print(f"❌ Error creating transaction: {e}")
    else:
        print(f"\n❌ Cannot create transaction - missing food ({food_id}) or request ({request_id})")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_analytics_sync()
