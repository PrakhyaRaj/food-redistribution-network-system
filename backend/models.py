from app import db
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Enum

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

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
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


# ============================================================
# FOOD ITEMS TABLE
# ============================================================
class FoodItem(db.Model):
    __tablename__ = "food_items"

    food_id = db.Column(db.Integer, primary_key=True)
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

    request_id = db.Column(db.Integer, primary_key=True)
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

    txn_id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey("food_items.food_id"), nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.request_id"), nullable=True)
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