# backend/services/analytics_service.py

from datetime import datetime
from backend.models import db, User, FoodItem, Transaction
from backend.mongodb import mongo_service
from backend.extensions import socketio

class AnalyticsService:
    """Service to sync analytics after every transaction across SQL and MongoDB"""

    # Constants for impact calculation
    PEOPLE_FED_PER_KG = 5  # 1kg of food feeds ~5 people
    CARBON_SAVED_PER_KG = 2.5  # 1kg food saved = ~2.5kg CO2 not emitted
    KG_CO2_PER_TREE = 20  # 1 tree absorbs ~20kg CO2

    @staticmethod
    def sync_analytics_after_transaction(transaction: Transaction, food_item: FoodItem):
        """
        Sync analytics after a transaction is created/completed.
        Updates both SQL (if tables exist) and MongoDB.
        Emits Socket.IO event for real-time frontend updates.
        
        Args:
            transaction: Transaction object from SQLAlchemy
            food_item: FoodItem object from SQLAlchemy
        """
        print(f"🔄 [ANALYTICS] Starting sync for transaction {transaction.txn_id}...")
        try:
            if not food_item and transaction.quantity is None:
                print(f"⚠️ [ANALYTICS] Missing food item and quantity, skipping sync")
                return

            quantity_kg = float(transaction.quantity or getattr(food_item, "quantity", 0) or 0)
            if quantity_kg <= 0:
                print(f"⚠️ [ANALYTICS] Invalid quantity, skipping sync")
                return
            print(f"📊 [ANALYTICS] Food quantity: {quantity_kg}kg")
            
            # Calculate impact metrics
            people_fed = round(quantity_kg * AnalyticsService.PEOPLE_FED_PER_KG)
            carbon_saved_kg = round(quantity_kg * AnalyticsService.CARBON_SAVED_PER_KG, 2)
            trees_planted = round(carbon_saved_kg / AnalyticsService.KG_CO2_PER_TREE)
            
            print(f"📊 [ANALYTICS] Metrics - People: {people_fed}, Carbon: {carbon_saved_kg}kg, Trees: {trees_planted}")
            
            # Derive a safe food_type value for analytics (FoodItem may not have food_type field)
            food_type = getattr(food_item, "food_type", None) or getattr(food_item, "name", "unknown")

            # 1. Update MongoDB - Global Analytics
            AnalyticsService._sync_mongodb_global_analytics(
                transaction, 
                quantity_kg, 
                people_fed, 
                carbon_saved_kg,
                trees_planted,
                food_type
            )
            
            # 2. Update MongoDB - User-Specific Analytics
            AnalyticsService._sync_mongodb_user_analytics(
                transaction,
                quantity_kg,
                people_fed,
                carbon_saved_kg,
                trees_planted,
                food_type
            )
            
            # 3. Update SQL (if analytics tables exist)
            AnalyticsService._sync_sql_analytics(
                transaction,
                quantity_kg,
                people_fed,
                carbon_saved_kg,
                trees_planted
            )
            
            # 4. Emit Socket.IO event to trigger frontend refresh
            AnalyticsService._emit_analytics_updated_event(
                transaction,
                people_fed,
                carbon_saved_kg,
                trees_planted
            )
            
            print(f"✅ [ANALYTICS] Sync complete for transaction {transaction.txn_id}")
            
        except Exception as e:
            print(f"❌ [ANALYTICS] Sync failed: {e}")
            import traceback
            traceback.print_exc()

    @staticmethod
    def _sync_mongodb_global_analytics(transaction, quantity_kg, people_fed, carbon_saved_kg, trees_planted, food_type):
        """Update global redistribution_analytics collection in MongoDB"""
        try:
            if not mongo_service or not mongo_service.is_connected():
                print(f"⚠️ [ANALYTICS-MONGO] MongoDB not connected, skipping global analytics")
                return
            
            doc = {
                "transaction_id": transaction.txn_id,
                "donor_id": transaction.donor_id,
                "receiver_id": transaction.receiver_id,
                "food_id": transaction.food_id,
                "food_type": food_type,
                "quantity_kg": quantity_kg,
                "impact_metrics": {
                    "people_fed": people_fed,
                    "carbon_saved_kg": carbon_saved_kg,
                    "trees_planted": trees_planted,
                    "waste_prevented_kg": quantity_kg
                },
                "timestamp": datetime.utcnow(),
                "month": datetime.utcnow().month,
                "year": datetime.utcnow().year,
                "day_of_week": datetime.utcnow().strftime('%A'),
                "status": transaction.status
            }
            
            result = mongo_service.db["redistribution_analytics"].insert_one(doc)
            print(f"✅ [ANALYTICS-MONGO] Global analytics document stored (ID: {str(result.inserted_id)[:8]}...)")
            
        except Exception as e:
            print(f"⚠️ [ANALYTICS-MONGO] Failed to update global analytics: {e}")

    @staticmethod
    def _sync_mongodb_user_analytics(transaction, quantity_kg, people_fed, carbon_saved_kg, trees_planted, food_type):
        """Update user-specific analytics in MongoDB"""
        try:
            if not mongo_service or not mongo_service.is_connected():
                print(f"⚠️ [ANALYTICS-USER] MongoDB not connected, skipping user analytics")
                return
            
            # Update donor analytics
            donor_doc = {
                "user_id": transaction.donor_id,
                "role": "donor",
                "transaction_id": transaction.txn_id,
                "quantity_donated_kg": quantity_kg,
                "impact_metrics": {
                    "people_fed": people_fed,
                    "carbon_saved_kg": carbon_saved_kg,
                    "trees_planted": trees_planted,
                    "waste_prevented_kg": quantity_kg
                },
                "timestamp": datetime.utcnow()
            }
            
            mongo_service.db["user_analytics"].insert_one(donor_doc)
            print(f"✅ [ANALYTICS-USER] Donor analytics updated (user_id: {transaction.donor_id})")
            
            # Update receiver analytics
            receiver_doc = {
                "user_id": transaction.receiver_id,
                "role": "receiver",
                "transaction_id": transaction.txn_id,
                "quantity_received_kg": quantity_kg,
                "impact_metrics": {
                    "people_fed": people_fed,
                    "food_received_kg": quantity_kg
                },
                "timestamp": datetime.utcnow()
            }
            
            mongo_service.db["user_analytics"].insert_one(receiver_doc)
            print(f"✅ [ANALYTICS-USER] Receiver analytics updated (user_id: {transaction.receiver_id})")
            
        except Exception as e:
            print(f"⚠️ [ANALYTICS-USER] Failed to update user analytics: {e}")

    @staticmethod
    def _sync_sql_analytics(transaction, quantity_kg, people_fed, carbon_saved_kg, trees_planted):
        """Update SQL tables if Analytics model exists"""
        try:
            # Try to import Analytics model if it exists
            try:
                from backend.models import Analytics
                
                # Create analytics record
                analytics_record = Analytics(
                    transaction_id=transaction.txn_id,
                    donor_id=transaction.donor_id,
                    receiver_id=transaction.receiver_id,
                    quantity_kg=quantity_kg,
                    people_fed=people_fed,
                    carbon_saved_kg=carbon_saved_kg,
                    trees_planted=trees_planted,
                    created_at=datetime.utcnow()
                )
                
                db.session.add(analytics_record)
                db.session.commit()
                print(f"✅ [ANALYTICS-SQL] SQL analytics record created")
                
            except ImportError:
                print(f"ℹ️ [ANALYTICS-SQL] Analytics model not found in backend.models, skipping SQL sync")
            
        except Exception as e:
            print(f"⚠️ [ANALYTICS-SQL] Failed to update SQL analytics: {e}")
            db.session.rollback()

    @staticmethod
    def _emit_analytics_updated_event(transaction, people_fed, carbon_saved_kg, trees_planted):
        """Emit Socket.IO event to notify frontend of analytics update"""
        try:
            if not socketio:
                print(f"⚠️ [ANALYTICS-SOCKET] Socket.IO not available, skipping event emission")
                return
            
            event_data = {
                "transaction_id": transaction.txn_id,
                "donor_id": transaction.donor_id,
                "receiver_id": transaction.receiver_id,
                "people_fed": people_fed,
                "carbon_saved_kg": carbon_saved_kg,
                "trees_planted": trees_planted,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Emit to specific user rooms
            socketio.emit('analytics_updated', event_data, room=f'user_{transaction.donor_id}')
            socketio.emit('analytics_updated', event_data, room=f'user_{transaction.receiver_id}')
            
            # Broadcast to all connected clients
            socketio.emit('analytics_updated', event_data)
            
            print(f"✅ [ANALYTICS-SOCKET] Event emitted successfully")
            
        except Exception as e:
            print(f"⚠️ [ANALYTICS-SOCKET] Failed to emit analytics event: {e}")

