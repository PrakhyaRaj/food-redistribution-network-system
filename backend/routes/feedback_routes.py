from flask import Blueprint, request, jsonify, current_app
# ensure you import mongo_service or use current_app.extensions['mongo']
from backend.mongodb import mongo_service

feedback_bp = Blueprint("feedback_bp", __name__, url_prefix="/feedback")

@feedback_bp.route("/submit", methods=["POST"])
def submit_feedback():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    message = data.get("message")
    if not user_id or not message:
        return jsonify({"error": "user_id and message are required"}), 400

    inserted_id = mongo_service.insert_feedback(user_id, message, metadata=data.get("metadata"))
    return jsonify({"message": "Thanks", "id": str(inserted_id)}), 201