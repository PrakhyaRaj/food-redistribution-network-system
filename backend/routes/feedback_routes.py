from flask import Blueprint, request, jsonify, current_app
# ensure you import mongo_service or use current_app.extensions['mongo']
from backend.mongodb import mongo_service
from flask_socketio import emit
from backend.extensions import socketio

feedback_bp = Blueprint("feedback_bp", __name__, url_prefix="/feedback")

@feedback_bp.route("/submit", methods=["POST"])
def submit_feedback():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    message = data.get("message")

    if not user_id or not message:
        return jsonify({"error": "user_id and message are required"}), 400

    inserted_id = mongo_service.insert_feedback(user_id, message, metadata=data.get("metadata"))
    
    # Emit real-time event for feedback submission (broadcast to all users)
    try:
        if socketio:
            socketio.emit('feedback_submitted', {
                'user_id': user_id,
                'feedback_id': str(inserted_id)
            }, broadcast=True)
            print(f"💬 Emitted feedback_submitted event globally (user {user_id})")
        else:
            print("⚠️ SocketIO instance missing; skipping feedback_submitted emit")
    except Exception as e:
        print(f"⚠️ Failed to emit feedback event: {e}")
    
    return jsonify({"message": "Thanks", "id": str(inserted_id)}), 201

@feedback_bp.route("", methods=["GET"])
def get_feedback():
    feedback = mongo_service.get_unresolved_feedback()
    # Convert ObjectId to string for JSON serialization
    return jsonify([{**f, "_id": str(f["_id"])} if isinstance(f, dict) else f for f in feedback]), 200