# backend/notifications.py
from flask_socketio import emit
from backend import socketio
from backend.services.notification_service import NotificationService
from backend.services.activity_logger import ActivityLogger
from .models import User, FoodItem, Request, Transaction
from datetime import datetime

class NotificationService:
    @staticmethod
    def notify_food_matched(food_id, request_id, donor_id, receiver_id):
        """Notify both donor and receiver when food is matched"""
        try:
            food = FoodItem.query.get(food_id)
            food_request = Request.query.get(request_id)
            donor = User.query.get(donor_id)
            receiver = User.query.get(receiver_id)
            
            if not all([food, food_request, donor, receiver]):
                return False
            
            # Notify donor
            donor_notification = {
                "type": "food_matched",
                "title": "Food Matched Successfully!",
                "message": f"Your {food.name} has been matched with a request from {receiver.name}",
                "food_id": food_id,
                "request_id": request_id,
                "receiver_id": receiver_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Use enhanced method that sends AND stores
            NotificationService.send_and_store(donor_id, donor_notification)
            
            # Notify receiver
            receiver_notification = {
                "type": "request_fulfilled",
                "title": "Request Fulfilled!",
                "message": f"Your request for {food_request.food_type} has been matched with {food.name} from {donor.name}",
                "food_id": food_id,
                "request_id": request_id,
                "donor_id": donor_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            NotificationService.send_and_store(receiver_id, receiver_notification)
            
            # Log activity
            ActivityLogger.log_food_matched(donor_id, receiver_id, food_id, request_id)
            
            print(f"✅ Notifications sent & stored for food match: food_{food_id} + request_{request_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending food match notifications: {str(e)}")
            return False
    
    @staticmethod
    def notify_food_accepted(transaction_id, donor_id, receiver_id, food_id):
        """Notify donor when their food is accepted by a receiver"""
        try:
            transaction = Transaction.query.get(transaction_id)
            donor = User.query.get(donor_id)
            receiver = User.query.get(receiver_id)
            food = FoodItem.query.get(food_id)
            
            if not all([transaction, donor, receiver, food]):
                return False
            
            # Notify donor
            donor_notification = {
                "type": "food_accepted",
                "title": "Food Accepted!",
                "message": f"{receiver.name} has accepted your {food.name}",
                "transaction_id": transaction_id,
                "receiver_id": receiver_id,
                "food_id": food_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            NotificationService.send_and_store(donor_id, donor_notification)
            
            # Log activity
            ActivityLogger.log_food_accepted(donor_id, receiver_id, transaction_id, food_id)
            
            print(f"✅ Notification sent & stored for food acceptance: transaction_{transaction_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending food acceptance notification: {str(e)}")
            return False
    
    @staticmethod
    def notify_new_request(request_id, receiver_id):
        """Notify all nearby donors about a new request"""
        try:
            food_request = Request.query.get(request_id)
            receiver = User.query.get(receiver_id)
            
            if not food_request or not receiver:
                return False
            
            # Create notification
            notification = {
                "type": "new_request",
                "title": "New Food Request Nearby",
                "message": f"New request for {food_request.food_type} ({food_request.quantity} units) - {food_request.urgency_level} urgency",
                "request_id": request_id,
                "receiver_id": receiver_id,
                "urgency_level": food_request.urgency_level,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Find nearby donors and notify them
            from backend.services.geo_service import GeoService
            
            if receiver.location_lat and receiver.location_long:
                nearby_donors = GeoService.find_nearby_users(
                    receiver.location_lat, 
                    receiver.location_long,
                    radius_km=20,  # 20km radius
                    user_type="donor"
                )
                
                for donor in nearby_donors:
                    NotificationService.send_and_store(donor["user_id"], notification)
                
                print(f"✅ Notified {len(nearby_donors)} nearby donors about new request")
            
            return True
            
        except Exception as e:
            print(f"❌ Error broadcasting new request: {str(e)}")
            return False
    
    @staticmethod
    def notify_transaction_update(transaction_id, status, user_id):
        """Notify users about transaction status updates"""
        try:
            transaction = Transaction.query.get(transaction_id)
            if not transaction:
                return False
            
            status_messages = {
                "claimed": "Food has been claimed",
                "in_progress": "Transaction is in progress",
                "completed": "Transaction completed successfully",
                "cancelled": "Transaction was cancelled"
            }
            
            notification = {
                "type": "transaction_update",
                "title": "Transaction Updated",
                "message": status_messages.get(status, f"Transaction status: {status}"),
                "transaction_id": transaction_id,
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Notify both donor and receiver
            NotificationService.send_and_store(transaction.donor_id, notification)
            NotificationService.send_and_store(transaction.receiver_id, notification)
            
            # Log activity
            ActivityLogger.log_transaction_update(transaction_id, status)
            
            print(f"✅ Transaction update notification sent & stored: {status}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending transaction update: {str(e)}")
            return False
    
    # Add this method to ActivityLogger as well
    @staticmethod
    def log_food_accepted(donor_id, receiver_id, transaction_id, food_id):
        """Log food acceptance activity"""
        from backend.mongodb import mongo_service
        
        mongo_service.log_activity(
            user_id=donor_id,
            activity_type="food_accepted",
            details={
                "role": "donor",
                "receiver_id": receiver_id,
                "transaction_id": transaction_id,
                "food_id": food_id
            }
        )
        
        mongo_service.log_activity(
            user_id=receiver_id,
            activity_type="food_accepted", 
            details={
                "role": "receiver",
                "donor_id": donor_id,
                "transaction_id": transaction_id,
                "food_id": food_id
            }
        )
    
    @staticmethod
    def log_transaction_update(transaction_id, status):
        """Log transaction update activity"""
        from backend.mongodb import mongo_service
        from backend.models import Transaction
        
        transaction = Transaction.query.get(transaction_id)
        if transaction:
            mongo_service.log_activity(
                user_id=transaction.donor_id,
                activity_type="transaction_update",
                details={
                    "transaction_id": transaction_id,
                    "status": status,
                    "role": "donor"
                }
            )
            
            mongo_service.log_activity(
                user_id=transaction.receiver_id,
                activity_type="transaction_update",
                details={
                    "transaction_id": transaction_id,
                    "status": status,
                    "role": "receiver"
                }
            )