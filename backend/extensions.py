# backend/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

# Simple SocketIO configuration
socketio = SocketIO(cors_allowed_origins="*")  # Allow all for now

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()