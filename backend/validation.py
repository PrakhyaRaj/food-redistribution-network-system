from flask import jsonify
import re
from datetime import datetime

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message, field=None):
        self.message = message
        self.field = field
        super().__init__(self.message)

def validate_email(email):
    """Validate email format"""
    if not email:
        raise ValidationError("Email is required", "email")
    
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        raise ValidationError("Invalid email format", "email")
    
    return email.lower().strip()

def validate_password(password):
    """Validate password strength"""
    if not password:
        raise ValidationError("Password is required", "password")
    
    if len(password) < 6:
        raise ValidationError("Password must be at least 6 characters", "password")
    
    return password

def validate_name(name):
    """Validate name"""
    if not name or not name.strip():
        raise ValidationError("Name is required", "name")
    
    name = name.strip()
    if len(name) < 2:
        raise ValidationError("Name must be at least 2 characters", "name")
    
    if len(name) > 100:
        raise ValidationError("Name must be less than 100 characters", "name")
    
    return name

def validate_phone(phone):
    """Validate phone number"""
    if not phone:
        return None
    
    phone = phone.strip()
    # Basic phone validation - adjust based on your requirements
    phone_regex = r'^[\+]?[0-9\s\-\(\)]{10,15}$'
    if not re.match(phone_regex, phone):
        raise ValidationError("Invalid phone number format", "phone")
    
    return phone

def validate_location(lat, lng):
    """Validate latitude and longitude"""
    if lat is not None:
        if not isinstance(lat, (int, float)) or lat < -90 or lat > 90:
            raise ValidationError("Invalid latitude value", "location_lat")
    
    if lng is not None:
        if not isinstance(lng, (int, float)) or lng < -180 or lng > 180:
            raise ValidationError("Invalid longitude value", "location_long")
    
    return lat, lng

def validate_roles(roles):
    """Validate user roles"""
    if not roles or not isinstance(roles, list):
        raise ValidationError("Roles are required and must be a list", "roles")
    
    valid_roles = ['donor', 'receiver']
    for role in roles:
        if role not in valid_roles:
            raise ValidationError(f"Invalid role: {role}. Must be one of {valid_roles}", "roles")
    
    return roles

def validate_food_data(data):
    """Validate food item data"""
    required_fields = ['food_name', 'quantity', 'expiry_date']
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValidationError(f"{field.replace('_', ' ').title()} is required", field)
    
    # Validate food name
    food_name = data.get('food_name') or data.get('name')
    if not food_name or len(food_name.strip()) < 2:
        raise ValidationError("Food name must be at least 2 characters", "food_name")
    
    # Validate quantity
    try:
        quantity = int(data['quantity'])
        if quantity <= 0:
            raise ValidationError("Quantity must be a positive number", "quantity")
    except (ValueError, TypeError):
        raise ValidationError("Quantity must be a valid number", "quantity")
    
    # Validate expiry date
    try:
        expiry_date = datetime.strptime(data['expiry_date'], "%Y-%m-%d").date()
        if expiry_date < datetime.now().date():
            raise ValidationError("Expiry date cannot be in the past", "expiry_date")
    except ValueError:
        raise ValidationError("Expiry date must be in YYYY-MM-DD format", "expiry_date")
    
    return {
        'food_name': food_name.strip(),
        'quantity': quantity,
        'expiry_date': expiry_date
    }

def validate_request_data(data):
    """Validate food request data"""
    required_fields = ['food_type', 'quantity', 'urgency_level']
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValidationError(f"{field.replace('_', ' ').title()} is required", field)
    
    # Validate food type
    food_type = data['food_type']
    if len(food_type.strip()) < 2:
        raise ValidationError("Food type must be at least 2 characters", "food_type")
    
    # Validate quantity
    try:
        quantity = int(data['quantity'])
        if quantity <= 0:
            raise ValidationError("Quantity must be a positive number", "quantity")
    except (ValueError, TypeError):
        raise ValidationError("Quantity must be a valid number", "quantity")
    
    # Validate urgency level
    valid_urgency_levels = ['low', 'medium', 'high', 'critical']
    urgency_level = data['urgency_level']
    if urgency_level not in valid_urgency_levels:
        raise ValidationError(f"Urgency level must be one of: {', '.join(valid_urgency_levels)}", "urgency_level")
    
    # Validate deadline if provided
    deadline = None
    if data.get('deadline'):
        try:
            deadline = datetime.strptime(data['deadline'], "%Y-%m-%d %H:%M:%S")
            if deadline < datetime.now():
                raise ValidationError("Deadline cannot be in the past", "deadline")
        except ValueError:
            raise ValidationError("Deadline must be in YYYY-MM-DD HH:MM:SS format", "deadline")
    
    return {
        'food_type': food_type.strip(),
        'quantity': quantity,
        'urgency_level': urgency_level,
        'deadline': deadline
    }

def handle_validation_error(error):
    """Global handler for validation errors"""
    return jsonify({
        "success": False,
        "error": error.message,
        "field": error.field
    }), 400