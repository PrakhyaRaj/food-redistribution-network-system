# backend/models.py
from backend.extensions import db #from extensions import db  # CHANGED: Import from extensions instead of app
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Enum
from werkzeug.security import generate_password_hash, check_password_hash

roles_enum = Enum('donor', 'receiver', 'admin', name='role_enum')
status_enum = Enum('available', 'expired', 'reserved', 'collected')

food_status_enum = Enum(
    "available", "pending", "collected", "expired", "in_transit",
    name="food_status_enum"
)

request_status_enum = Enum(
    "pending", "accepted", "in_transit", "completed", "cancelled", "timed_out",
    name="request_status_enum"
)

txn_status_enum = Enum(
    "initiated", "in_progress", "completed", "cancelled",
    name="txn_status_enum"
)


user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("users.user_id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.role_id"), primary_key=True),
)
# ============================================================
# USERS TABLE
# ============================================================
class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) 
    phone = db.Column(db.String(15))
    location_lat = db.Column(db.Float)
    location_long = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # MANY-TO-MANY ROLE RELATION
    roles = db.relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
        lazy=True
    )

    # Existing relationships
    foods = db.relationship("FoodItem", back_populates="donor", lazy=True)
    requests = db.relationship("Request", back_populates="receiver", lazy=True)
    donations_made = db.relationship(
        "Transaction",
        foreign_keys="Transaction.donor_id",
        back_populates="donor",
        lazy=True
    )
    received_txns = db.relationship(
        "Transaction",
        foreign_keys="Transaction.receiver_id",
        back_populates="receiver",
        lazy=True
    )

    # === CHANGED: helper methods for roles and serialization ===
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password = generate_password_hash(password)  # Store in 'password' column
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password, password)  # Check 'password' column
    
    def roles_list(self):
        """Return list of role names for the user."""
        # Role stores column 'role_name' below; use that to return strings consistently.
        return [r.role_name for r in self.roles]

    def has_role(self, role_name):
        """Return True if user has role with name role_name."""
        return role_name in self.roles_list()

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,  
            "location_lat": self.location_lat,
            "location_long": self.location_long,
            "roles": self.roles_list()
        }
    
    def __repr__(self):
        return f"<User {self.name}>"

# ============================================================
# ROLES TABLE
# ============================================================
class Role(db.Model):
    __tablename__ = "roles"

    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)

    # Relationship back to users through association table
    users = db.relationship(
        "User",
        secondary="user_roles",
        back_populates="roles"
    )

    # === CHANGED: convenience property so code can use role.name uniformly ===
    @property
    def name(self):
        return self.role_name


# ============================================================
# FOOD ITEMS TABLE
# ============================================================
class FoodItem(db.Model):
    __tablename__ = "food_items"

    food_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    status = db.Column(food_status_enum, default="available", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # Relationships
    donor = db.relationship("User", back_populates="foods")
    transactions = db.relationship("Transaction", back_populates="food", lazy=True)

    def __repr__(self):
        return f"<FoodItem {self.name} - {self.status}>"


# ============================================================
# REQUESTS TABLE
# ============================================================
class Request(db.Model):
    __tablename__ = "requests"

    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    food_type = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    urgency_level = db.Column(db.String(50))  # e.g., "high", "medium", "low"
    status = db.Column(request_status_enum, default="pending", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    deadline = db.Column(db.DateTime, nullable=True)

    # Relationships
    receiver = db.relationship("User", back_populates="requests")
    transactions = db.relationship("Transaction", back_populates="request", lazy=True)

    def __repr__(self):
        return f"<Request {self.food_type} ({self.status})>"


# ============================================================
# TRANSACTIONS TABLE
# ============================================================
class Transaction(db.Model):
    __tablename__ = "transactions"

    txn_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey("food_items.food_id"), nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.request_id"), nullable=True)
    quantity = db.Column(db.Integer, nullable=True)  # Quantity of food in this transaction
    pickup_date = db.Column(db.DateTime, nullable=True)  # Scheduled or actual pickup date
    status = db.Column(txn_status_enum, default="initiated", nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # Relationships
    donor = db.relationship("User", foreign_keys=[donor_id], back_populates="donations_made")
    receiver = db.relationship("User", foreign_keys=[receiver_id], back_populates="received_txns")
    food = db.relationship("FoodItem", back_populates="transactions")
    request = db.relationship("Request", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction {self.txn_id} ({self.status})>"


# ============================================================
# NOTIFICATIONS TABLE
# ============================================================
class Notification(db.Model):
    __tablename__ = "notifications"

    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    data = db.Column(db.JSON, nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship("User", backref="notifications")

    def to_dict(self):
        return {
            "notification_id": self.notification_id,
            "user_id": self.user_id,
            "notification_type": self.notification_type,
            "title": self.title,
            "message": self.message,
            "data": self.data,
            "is_read": self.is_read,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

    def __repr__(self):
        return f"<Notification {self.notification_id} - {self.notification_type}>"