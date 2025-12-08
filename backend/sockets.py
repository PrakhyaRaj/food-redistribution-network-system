from flask import request
from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend import socketio
from backend.models import User, db

# Store connected users (in production, use Redis)
connected_users = {}

@socketio.on('connect')
@jwt_required(optional=True)  # Make JWT optional for connection
def handle_connect():
    """Handle client connection"""
    try:
        user_id = get_jwt_identity()
        if user_id:
            # Store user connection
            connected_users[user_id] = request.sid
            join_room(f"user_{user_id}")
            print(f"🔌 User {user_id} connected with SID {request.sid}")
            
            emit('connection_status', {
                'status': 'connected',
                'message': 'Successfully connected to notifications'
            })
        else:
            emit('connection_status', {
                'status': 'unauthorized',
                'message': 'Authentication required'
            })
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        emit('connection_status', {
            'status': 'error',
            'message': 'Connection failed'
        })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    try:
        user_id = None
        for uid, sid in connected_users.items():
            if sid == request.sid:
                user_id = uid
                break
        
        if user_id:
            del connected_users[user_id]
            leave_room(f"user_{user_id}")
            print(f"🔌 User {user_id} disconnected")
    except Exception as e:
        print(f"❌ Disconnection error: {str(e)}")

@socketio.on('join_room')
@jwt_required()
def handle_join_room(data):
    """Allow users to join specific rooms"""
    try:
        user_id = get_jwt_identity()
        room = data.get('room')
        
        if room:
            join_room(room)
            emit('room_joined', {
                'room': room,
                'message': f'Joined room: {room}'
            })
    except Exception as e:
        emit('error', {'message': f'Failed to join room: {str(e)}'})

@socketio.on('leave_room')
@jwt_required()
def handle_leave_room(data):
    """Allow users to leave specific rooms"""
    try:
        user_id = get_jwt_identity()
        room = data.get('room')
        
        if room:
            leave_room(room)
            emit('room_left', {
                'room': room,
                'message': f'Left room: {room}'
            })
    except Exception as e:
        emit('error', {'message': f'Failed to leave room: {str(e)}'})