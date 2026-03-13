"""
Notification Service

Handles all notification-related functionality including:
- Sending real-time notifications via WebSocket
- Storing notifications in the database
- Managing notification preferences
"""

from datetime import datetime
from flask_socketio import emit
from backend.extensions import socketio
from backend.services.activity_logger import ActivityLogger
from backend.mongodb import mongo_service
from .models import db, User, FoodItem, Request, Transaction, Notification

def create_notification(recipient_id, notification_type, title, message, **kwargs):
    """Helper function to create and store a notification in both SQL and MongoDB"""
    notification_obj = None
    try:
        notification = Notification(
            user_id=recipient_id,
            notification_type=notification_type,
            title=title,
            message=message,
            data=kwargs,
            timestamp=datetime.utcnow()
        )
        db.session.add(notification)
        db.session.commit()
        notification_obj = notification
        print(f"✅ Notification created in SQL: {notification.notification_id}")
    except Exception as e:
        print(f"❌ Error creating SQL notification: {e}")
        db.session.rollback()
    
    # ALSO store in MongoDB for the notification center UI
    try:
        if mongo_service and getattr(mongo_service, "is_connected", lambda: False)():
            payload = {
                "type": notification_type,
                "title": title,
                "message": message,
                **kwargs,
                "status": "unread",
                "created_at": datetime.utcnow().isoformat(),
            }
            mongo_id = mongo_service.store_notification(recipient_id, payload)
            print(f"✅ Notification also stored in MongoDB: {mongo_id}")
            
            # If SQL failed, return MongoDB version
            if not notification_obj:
                payload.update({"user_id": recipient_id, "_id": str(mongo_id) if mongo_id else None})
                return payload
    except Exception as me:
        print(f"❌ MongoDB notification storage failed: {me}")
    
    return notification_obj

class NotificationService:
    @staticmethod
    def send_websocket_notification(user_id, notification_data):
        """Send real-time notification via WebSocket"""
        try:
            socketio.emit('notification', notification_data, room=f'user_{user_id}')
            return True
        except Exception as e:
            print(f"Error sending WebSocket notification: {e}")
            return False

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
            
            # Prepare notification data
            timestamp = datetime.utcnow().isoformat()
            
            # Create and store notifications
            donor_notification = create_notification(
                recipient_id=donor_id,
                notification_type="food_matched",
                title="Food Matched Successfully!",
                message=f"Your {food.name} has been matched with a request from {receiver.name}",
                food_id=food_id,
                request_id=request_id,
                receiver_id=receiver_id,
                timestamp=timestamp
            )
            
            receiver_notification = create_notification(
                recipient_id=receiver_id,
                notification_type="request_fulfilled",
                title="Request Fulfilled!",
                message=f"Your request for {food_request.food_type} has been matched with {food.name} from {donor.name}",
                food_id=food_id,
                request_id=request_id,
                donor_id=donor_id,
                timestamp=timestamp
            )
            
            # Send real-time notifications
            if donor_notification:
                data = donor_notification.to_dict() if hasattr(donor_notification, "to_dict") else donor_notification
                NotificationService.send_websocket_notification(donor_id, data)
            if receiver_notification:
                data = receiver_notification.to_dict() if hasattr(receiver_notification, "to_dict") else receiver_notification
                NotificationService.send_websocket_notification(receiver_id, data)
            
            # Log activity
            ActivityLogger.log_food_matched(donor_id, receiver_id, food_id, request_id)
            
            return True
            
        except Exception as e:
            print(f"Error in notify_food_matched: {e}")
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
            
            # Create and store notification
            notification = create_notification(
                recipient_id=donor_id,
                notification_type="food_accepted",
                title="Food Accepted!",
                message=f"{receiver.name} has accepted your {food.name}",
                transaction_id=transaction_id,
                receiver_id=receiver_id,
                food_id=food_id,
                timestamp=datetime.utcnow().isoformat()
            )
            
            # Send real-time notification
            if notification:
                # Handle both SQL model objects and MongoDB dict responses
                notif_data = notification.to_dict() if hasattr(notification, "to_dict") else notification
                NotificationService.send_websocket_notification(donor_id, notif_data)
            
            # Log activity
            ActivityLogger.log_food_accepted(donor_id, receiver_id, transaction_id, food_id)
            
            return True
            
        except Exception as e:
            print(f"Error in notify_food_accepted: {e}")
            return False
    
    @staticmethod
    def notify_new_request(request_id, receiver_id):
        """Notify all nearby donors about a new request"""
        try:
            food_request = Request.query.get(request_id)
            receiver = User.query.get(receiver_id)
            
            if not food_request or not receiver:
                return False
            
            # Prepare notification data
            notification_data = {
                "notification_type": "new_request",
                "title": "New Food Request Nearby",
                "message": f"New request for {food_request.food_type} ({food_request.quantity} units) - {food_request.urgency_level} urgency",
                "request_id": request_id,
                "receiver_id": receiver_id,
                "urgency_level": food_request.urgency_level,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Find nearby donors and notify them
            if receiver.location_lat and receiver.location_long:
                from backend.services.geo_service import GeoService
                
                nearby_donors = GeoService.find_nearby_users(
                    receiver.location_lat, 
                    receiver.location_long,
                    radius_km=20,  # 20km radius
                    user_type="donor"
                )
                
                for donor in nearby_donors:
                    notification = create_notification(
                        recipient_id=donor["user_id"],
                        **notification_data
                    )
                    if notification:
                        # Handle both SQL model objects and MongoDB dict responses
                        notif_data = notification.to_dict() if hasattr(notification, "to_dict") else notification
                        NotificationService.send_websocket_notification(
                            donor["user_id"], 
                            notif_data
                        )
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error in notify_new_request: {e}")
            return False
    
    @staticmethod
    def notify_transaction_update(transaction_id, status, user_id=None):
        """Notify users about transaction status updates"""
        try:
            transaction = Transaction.query.get(transaction_id)
            if not transaction:
                return False
            
            status_messages = {
                "initiated": "Transaction initiated",
                "claimed": "Food has been claimed",
                "in_progress": "Transaction is in progress",
                "completed": "Transaction completed successfully",
                "cancelled": "Transaction was cancelled"
            }
            
            # Create notification data
            notification_data = {
                "notification_type": "transaction_update",
                "title": "Transaction Updated",
                "message": status_messages.get(status, f"Transaction status: {status}"),
                "transaction_id": transaction_id,
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Notify both donor and receiver
            for user_id in [transaction.donor_id, transaction.receiver_id]:
                notification = create_notification(
                    recipient_id=user_id,
                    **notification_data
                )
                if notification:
                    # Handle both SQL model objects and MongoDB dict responses
                    notif_data = notification.to_dict() if hasattr(notification, "to_dict") else notification
                    NotificationService.send_websocket_notification(
                        user_id, 
                        notif_data
                    )
            
            # Log activity
            ActivityLogger.log_transaction_update(transaction_id, status)
            
            return True
            
        except Exception as e:
            print(f"Error in notify_transaction_update: {e}")
            return False
    
    @staticmethod
    def log_food_accepted(donor_id, receiver_id, transaction_id, food_id):
        """Log food acceptance activity for both donor and receiver"""
        try:
            from backend.mongodb import mongo_service
            
            if not all([donor_id, receiver_id, transaction_id, food_id]):
                raise ValueError("Missing required parameters for logging food acceptance")
            
            # Log donor activity
            mongo_service.log_activity(
                user_id=donor_id,
                activity_type="food_accepted",
                details={
                    "role": "donor",
                    "receiver_id": receiver_id,
                    "transaction_id": transaction_id,
                    "food_id": food_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Log receiver activity
            mongo_service.log_activity(
                user_id=receiver_id,
                activity_type="food_accepted", 
                details={
                    "role": "receiver",
                    "donor_id": donor_id,
                    "transaction_id": transaction_id,
                    "food_id": food_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            return True
            
        except Exception as e:
            print(f"Error in log_food_accepted: {e}")
            return False
    
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

    @staticmethod
    def notify_match_found(request_id, donor_id, receiver_id, food_id):
        """Notify both parties when a match is found"""
        try:
            from backend.mongodb import mongo_service
            from backend.models import Request, FoodItem, User
            
            food = FoodItem.query.get(food_id)
            food_request = Request.query.get(request_id)
            donor = User.query.get(donor_id)
            receiver = User.query.get(receiver_id)
            
            if not all([food, food_request, donor, receiver]):
                return False
            
            match_data = {
                "request_id": request_id,
                "food_id": food_id,
                "donor_name": donor.name,
                "receiver_name": receiver.name,
                "food_name": food.name,
                "quantity": food.quantity
            }
            
            # Store match notification in MongoDB
            if mongo_service and mongo_service.is_connected():
                mongo_service.store_match_notification(
                    request_id, food_id, donor_id, receiver_id,
                    match_data
                )
            
            # Send real-time notifications via Socket.IO
            try:
                # Emit to receiver with user_{id} room naming
                socketio.emit('match_found', {
                    "request_id": request_id,
                    "food_id": food_id,
                    "message": f"Match found! {donor.name}'s {food.name} matches your request",
                    "donor_name": donor.name,
                    "food_name": food.name,
                    "type": "match_found"
                }, room=f"user_{receiver_id}")
                
                # Also emit as 'notification' event for broader compatibility
                socketio.emit('notification', {
                    "type": "match_found",
                    "title": "🎉 Match Found!",
                    "message": f"Match found! {donor.name}'s {food.name} matches your request",
                    "request_id": request_id,
                    "food_id": food_id,
                    "donor_id": donor_id,
                    "donor_name": donor.name,
                    "food_name": food.name
                }, room=f"user_{receiver_id}")
                
                # Emit to donor
                socketio.emit('match_found', {
                    "request_id": request_id,
                    "food_id": food_id,
                    "message": f"Match found! Your {food.name} matches a request from {receiver.name}",
                    "receiver_name": receiver.name,
                    "food_name": food.name,
                    "type": "match_found"
                }, room=f"user_{donor_id}")
                
                socketio.emit('notification', {
                    "type": "match_found",
                    "title": "🎉 Match Found!",
                    "message": f"Your {food.name} matches a request from {receiver.name}",
                    "request_id": request_id,
                    "food_id": food_id,
                    "receiver_id": receiver_id,
                    "receiver_name": receiver.name,
                    "food_name": food.name
                }, room=f"user_{donor_id}")
                
                print(f"✅ Match notifications emitted for request {request_id} to both parties")
            except Exception as emit_error:
                print(f"⚠️ Socket.IO emit failed (non-blocking): {str(emit_error)}")
            
            # Log activity
            ActivityLogger.log_match_found(donor_id, receiver_id, food_id, request_id)
            
            return True
        
        except Exception as e:
            print(f"❌ Error notifying match: {e}")
            return False
