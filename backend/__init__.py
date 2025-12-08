# backend/__init__.py
from flask_socketio import SocketIO

# Create socketio instance here
socketio = SocketIO(cors_allowed_origins="*")

# Export for use in other modules
__all__ = ['socketio']