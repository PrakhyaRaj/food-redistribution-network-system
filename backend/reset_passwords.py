# backend/reset_passwords.py
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor

# Create a simple Flask app just for this script
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Verma20%3F@localhost:5432/frns'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define minimal models just for this script
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(255))
    phone = db.Column(db.String(15))

    def set_password(self, password):
        self.password = generate_password_hash(password)

class Role(db.Model):
    __tablename__ = 'roles'
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50))

user_roles = db.Table(
    'user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.role_id'), primary_key=True)
)

def reset_all_passwords():
    with app.app_context():
        try:
            # Get all users
            users = User.query.all()
            
            print(f"🔍 Found {len(users)} users in database")
            
            for user in users:
                old_password = user.password
                user.set_password("password123")
                print(f"✅ Reset password for: {user.email}")
                print(f"   Old hash: {old_password[:50]}...")
                print(f"   New hash: {user.password[:50]}...")
            
            db.session.commit()
            print(f"\n🎉 Successfully reset passwords for {len(users)} users!")
            print("\n📧 You can now login with any user using password: password123")
            
            # Show available users
            print("\nAvailable users:")
            for user in users:
                print(f"  - {user.email}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    reset_all_passwords()