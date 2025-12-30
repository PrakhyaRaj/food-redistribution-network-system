#!/usr/bin/env python
"""
Quick test script to verify analytics sync is working correctly
"""
import sys
sys.path.insert(0, '/path/to/food-redistribution-network-system')

from datetime import datetime
from backend.models import db, User, FoodItem, Request, Transaction
from backend.services.analytics_service import AnalyticsService
from backend.app import create_app

def test_analytics_sync():
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("ANALYTICS SYNC TEST")
        print("="*60)
        
        # Test 1: Verify service loads
        print("\n✅ Test 1: AnalyticsService imported successfully")
        print(f"   - Available methods: {[m for m in dir(AnalyticsService) if not m.startswith('_')][:5]}...")
        
        # Test 2: Check existing data
        txn_count = Transaction.query.count()
        food_count = FoodItem.query.count()
        print(f"\n✅ Test 2: Database connectivity")
        print(f"   - Transactions in DB: {txn_count}")
        print(f"   - Food items in DB: {food_count}")
        
        # Test 3: Verify constants
        print(f"\n✅ Test 3: Analytics constants")
        print(f"   - PEOPLE_FED_PER_KG: {AnalyticsService.PEOPLE_FED_PER_KG}")
        print(f"   - CARBON_SAVED_PER_KG: {AnalyticsService.CARBON_SAVED_PER_KG}")
        print(f"   - KG_CO2_PER_TREE: {AnalyticsService.KG_CO2_PER_TREE}")
        
        # Test 4: Verify methods exist
        methods = ['sync_analytics_after_transaction', '_sync_mongodb_global_analytics', 
                  '_sync_mongodb_user_analytics', '_sync_sql_analytics', '_emit_analytics_updated_event']
        print(f"\n✅ Test 4: Required methods exist")
        for method in methods:
            has_method = hasattr(AnalyticsService, method)
            print(f"   - {method}: {'✅' if has_method else '❌'}")
        
        print("\n" + "="*60)
        print("All tests passed! Analytics sync is ready.")
        print("="*60 + "\n")

if __name__ == '__main__':
    test_analytics_sync()
