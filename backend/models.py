from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # donor / receiver / admin
    location_lat = db.Column(db.Float)
    location_long = db.Column(db.Float)

    foods = db.relationship("FoodItem", backref="donor", lazy=True)

class FoodItem(db.Model):
    __tablename__ = "food_items"
    food_id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    food_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer)
    expiry_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="available")

    transactions = db.relationship("Transaction", backref="food", lazy=True)

class Transaction(db.Model):
    __tablename__ = "transactions"
    txn_id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    receiver_id = db.Column(db.Integer)
    food_id = db.Column(db.Integer, db.ForeignKey("food_items.food_id"))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20))
