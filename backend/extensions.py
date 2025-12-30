# backend/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

# Simple SocketIO configuration
# Using async_mode='threading' for better Flask compatibility
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=60,
    ping_interval=25,
    engineio_logger=False,
    socketio_logger=False
)

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()