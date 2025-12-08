from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

notes_bp = Blueprint('notes_bp', __name__, url_prefix='/api/notes')

@notes_bp.route('/food/<int:food_id>', methods=['POST'])
@jwt_required()
def add_food_note(food_id):
    """Add complex note to food item"""
    from backend.mongodb import mongo_service
    
    user_id = get_jwt_identity()
    data = request.get_json()
    
    note_type = data.get('note_type', 'general')
    content = data.get('content')
    metadata = data.get('metadata', {})
    
    if not content:
        return jsonify({"success": False, "error": "Note content required"}), 400
    
    try:
        note_id = mongo_service.store_food_note(
            food_id=str(food_id),
            user_id=str(user_id),
            note_type=note_type,
            content=content,
            metadata=metadata
        )
        
        if note_id:
            return jsonify({
                "success": True,
                "message": "Food note added successfully",
                "note_id": note_id,
                "food_id": food_id
            }), 201
        else:
            return jsonify({"success": False, "error": "Failed to store note"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@notes_bp.route('/food/<int:food_id>', methods=['GET'])
def get_food_notes(food_id):
    """Get notes for a food item"""
    from backend.mongodb import mongo_service
    
    note_type = request.args.get('type')
    limit = request.args.get('limit', 20, type=int)
    
    try:
        notes = mongo_service.get_food_notes(str(food_id), note_type, limit)
        
        # Group by note type
        notes_by_type = {}
        for note in notes:
            note_type = note.get('note_type', 'general')
            if note_type not in notes_by_type:
                notes_by_type[note_type] = []
            notes_by_type[note_type].append(note)
        
        return jsonify({
            "success": True,
            "food_id": food_id,
            "notes": notes,
            "notes_by_type": notes_by_type,
            "count": len(notes)
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500