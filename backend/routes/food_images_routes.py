from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import base64

food_images_bp = Blueprint('food_images_bp', __name__, url_prefix='/api/food')

@food_images_bp.route('/<int:food_id>/images', methods=['POST'])
@jwt_required()
def upload_food_image(food_id):
    """Upload image for food item"""
    from backend.mongodb import mongo_service
    
    user_id = get_jwt_identity()
    
    # Check if file or base64
    if 'image' in request.files:
        file = request.files['image']
        image_data = base64.b64encode(file.read()).decode('utf-8')
        metadata = {
            'filename': file.filename,
            'mime_type': file.mimetype,
            'file_size': len(image_data),
            'caption': request.form.get('caption', '')
        }
    elif request.is_json:
        data = request.get_json()
        image_data = data.get('image_base64')
        metadata = data.get('metadata', {})
    else:
        return jsonify({"success": False, "error": "No image data provided"}), 400
    
    if not image_data:
        return jsonify({"success": False, "error": "No image data"}), 400
    
    try:
        image_id = mongo_service.store_food_image(
            food_id=str(food_id),
            user_id=str(user_id),
            image_data=image_data,
            metadata=metadata
        )
        
        if image_id:
            # Log activity (need to add this method to ActivityLogger)
            from backend.services.activity_logger import ActivityLogger
            # ActivityLogger.log_food_image_uploaded(user_id, food_id, image_id)
            
            return jsonify({
                "success": True,
                "message": "Food image uploaded successfully",
                "image_id": image_id,
                "food_id": food_id
            }), 201
        else:
            return jsonify({"success": False, "error": "Failed to store image"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@food_images_bp.route('/<int:food_id>/images', methods=['GET'])
def get_food_images(food_id):
    """Get images for a food item"""
    from backend.mongodb import mongo_service
    
    try:
        images = mongo_service.get_food_images(str(food_id))
        return jsonify({
            "success": True,
            "food_id": food_id,
            "images": images,
            "count": len(images)
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500