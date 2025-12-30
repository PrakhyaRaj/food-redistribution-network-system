from flask import request
from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import decode_token
from backend.extensions import socketio

# In-memory map of connected users -> SID. In production use Redis or similar.
connected_users = {}


@socketio.on('connect')
def handle_connect():
    """Handle client connection with manual JWT validation."""
    try:
        token = request.args.get('token') or None

        # Fallback: Authorization header
        if not token:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]

        # Fallback: try parsing an `auth` query param (sometimes used by clients)
        if not token:
            auth = request.args.get('auth')
            if auth:
                try:
                    import json
                    auth_obj = json.loads(auth)
                    token = auth_obj.get('token')
                except Exception:
                    # ignore parse errors
                    pass

        user_id = None
        if token:
            try:
                if token.startswith('Bearer '):
                    token = token[7:]
                decoded = decode_token(token)
                user_id = decoded.get('sub') or decoded.get('user_id') or decoded.get('identity')
            except Exception as e:
                print(f"❌ Token validation failed: {e}")
                user_id = None

        if user_id:
            try:
                if isinstance(user_id, str) and user_id.isdigit():
                    user_id = int(user_id)
            except Exception:
                pass

            connected_users[user_id] = request.sid
            join_room(f"user_{user_id}")
            print(f"✅ User {user_id} connected with SID {request.sid}")
            emit('connection_status', {
                'status': 'connected',
                'message': 'Successfully connected to notifications',
                'user_id': user_id
            })
        else:
            print("⚠️ Connection attempt without valid token")
            emit('connection_status', {
                'status': 'unauthorized',
                'message': 'Authentication required - no valid token provided'
            })
    except Exception as e:
        import traceback
        traceback.print_exc()
        emit('connection_status', {
            'status': 'error',
            'message': f'Connection failed: {e}'
        })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection and cleanup mapping."""
    try:
        user_id = None
        for uid, sid in list(connected_users.items()):
            if sid == request.sid:
                user_id = uid
                break

        if user_id is not None:
            connected_users.pop(user_id, None)
            leave_room(f"user_{user_id}")
            print(f"🔌 User {user_id} disconnected")
    except Exception as e:
        print(f"❌ Disconnection error: {e}")


@socketio.on('join_room')
def handle_join_room(data):
    """Allow authenticated users to join an arbitrary room."""
    try:
        user_id = None
        for uid, sid in connected_users.items():
            if sid == request.sid:
                user_id = uid
                break

        if not user_id:
            emit('error', {'message': 'Not authenticated'})
            return

        room = data.get('room')
        if room:
            join_room(room)
            emit('room_joined', {
                'room': room,
                'message': f'Joined room: {room}'
            })
            print(f"✅ User {user_id} joined room: {room}")
    except Exception as e:
        emit('error', {'message': f'Failed to join room: {e}'})


@socketio.on('leave_room')
def handle_leave_room(data):
    """Allow authenticated users to leave a room."""
    try:
        user_id = None
        for uid, sid in connected_users.items():
            if sid == request.sid:
                user_id = uid
                break

        if not user_id:
            emit('error', {'message': 'Not authenticated'})
            return

        room = data.get('room')
        if room:
            leave_room(room)
            emit('room_left', {
                'room': room,
                'message': f'Left room: {room}'
            })
            print(f"✅ User {user_id} left room: {room}")
    except Exception as e:
        emit('error', {'message': f'Failed to leave room: {e}'})