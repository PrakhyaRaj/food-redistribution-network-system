# backend/__init__.py
# Import socketio from extensions instead of creating another instance
from backend.extensions import socketio

# Export for use in other modules
__all__ = ['socketio']