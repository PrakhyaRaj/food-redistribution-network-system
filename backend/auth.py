from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt,
    get_jwt_identity,
)
from functools import wraps

# Import models and db from your project root modules
from backend.extensions import db
from backend.models import User, Role

def get_db():
    return current_app.extensions['sqlalchemy']

# validation imports
from backend.validation import (
    validate_email, validate_password, validate_name, 
    validate_phone, validate_location, validate_roles,
    ValidationError, handle_validation_error as validation_error_handler
)

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

@auth_bp.errorhandler(ValidationError)
def handle_auth_validation_error(error): 
    return validation_error_handler(error)  

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json() or {}
        
        # Validate all input fields
        email = validate_email(data.get('email'))
        password = validate_password(data.get('password'))
        name = validate_name(data.get('name'))
        phone = validate_phone(data.get('phone'))
        location_lat = data.get('location_lat')
        location_long = data.get('location_long')
        validate_location(location_lat, location_long)
        roles = validate_roles(data.get('roles'))
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                "success": False,
                "error": "User already exists with this email",
                "field": "email"
            }), 409
        
        # Create user
        user = User(
            name=name,
            email=email,
            phone=phone,
            location_lat=location_lat,
            location_long=location_long
        )
        
        user.set_password(password)
        
        # Add user to DB first
        db.session.add(user)
        db.session.commit()
        
        # Now assign roles
        user_with_roles = User.query.get(user.user_id)
        
        for role_name in roles:
            role = Role.query.filter_by(role_name=role_name).first()
            if role:
                user_with_roles.roles.append(role)
        
        db.session.commit()
        
        # Create tokens
        roles_list = user_with_roles.roles_list()
        
        access_token = create_access_token(identity=str(user.user_id), additional_claims={"roles": roles_list})
        refresh_token = create_refresh_token(identity=str(user.user_id))
        
        return jsonify({
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user.user_id,
            "user": user_with_roles.to_dict(),
            "message": "User registered successfully"
        }), 201
        
    except ValidationError:
        # Re-raise to be handled by the error handler
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Registration failed due to server error"
        }), 500

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        # Validate input
        email = validate_email(data.get('email'))
        password = validate_password(data.get('password'))
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({
                'success': False, 
                'error': 'Invalid email or password',
                'field': 'email'
            }), 401
        
        if not user.check_password(password):
            return jsonify({
                'success': False, 
                'error': 'Invalid email or password',
                'field': 'password'
            }), 401
        
        from backend.services.activity_logger import ActivityLogger
        ActivityLogger.log_login_success(str(user.user_id))

        # Get user roles
        roles = [role.role_name for role in user.roles]
        
        # Generate tokens
        access_token = create_access_token(
            identity=str(user.user_id), 
            additional_claims={"roles": roles}
        )
        refresh_token = create_refresh_token(identity=str(user.user_id))
        
        response_data = {
            'success': True,
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user.user_id,
            'roles': roles,
            'user': {
                'id': user.user_id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'location_lat': user.location_lat,
                'location_long': user.location_long,
                'roles': roles
            }
        }
        
        return jsonify(response_data), 200
        
    except ValidationError:
        raise
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False, 
            'error': 'Login failed due to server error'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt().get("jti")
    if jti is None:
        return jsonify({"msg": "No token jti"}), 400
    blocklist = current_app.config.setdefault('JWT_BLOCKLIST', set())
    blocklist.add(jti)
    return jsonify({"msg": "Token revoked"}), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    roles = [role.role_name for role in user.roles]
    new_token = create_access_token(identity=identity, additional_claims={"roles": roles})
    return jsonify({"access_token": new_token}), 200

# def roles_required(*required_roles):
#     def decorator(fn):
#         @wraps(fn)
#         @jwt_required()
#         def wrapper(*args, **kwargs):
#             claims = get_jwt() or {}
#             token_roles = claims.get("roles", [])
#             if not any(role in token_roles for role in required_roles):
#                 return jsonify({"msg": "Forbidden: missing role"}), 403
#             return fn(*args, **kwargs)
#         return wrapper
#     return decorator

def roles_required(*required_roles):
    """
    Enhanced role-based access control decorator
    Usage: @roles_required('donor') or @roles_required('donor', 'admin')
    """
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            try:
                claims = get_jwt()
                token_roles = claims.get("roles", [])
                current_user = get_jwt_identity()
                
                print(f"🔍 RBAC CHECK - User {current_user} has roles: {token_roles}, Required: {required_roles}")
                
                if not token_roles:
                    print(f"❌ RBAC FAILED - No roles found for user {current_user}")
                    return jsonify({"msg": "No roles assigned to user"}), 403
                    
                # Check if user has any of the required roles
                has_required_role = any(role in token_roles for role in required_roles)
                
                if not has_required_role:
                    print(f"❌ RBAC FAILED - User {current_user} with roles {token_roles} tried to access {required_roles} endpoint")
                    return jsonify({
                        "msg": f"Forbidden: Required roles {list(required_roles)}, but user has {token_roles}"
                    }), 403
                
                print(f"✅ RBAC PASSED - User {current_user} authorized for {required_roles}")
                return fn(*args, **kwargs)
                
            except Exception as e:
                print(f"❌ RBAC ERROR: {str(e)}")
                return jsonify({"msg": "Authorization error"}), 500
        return wrapper
    return decorator

@auth_bp.route('/fix-roles', methods=['POST'])
def fix_roles():
    """Emergency endpoint to fix missing roles"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        role_names = data.get('roles', ['donor'])
        
        if not email:
            return jsonify({"msg": "Email required"}), 400
            
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"msg": "User not found"}), 404
            
        # Clear existing roles and add new ones
        user.roles = []
        for role_name in role_names:
            role = Role.query.filter_by(role_name=role_name).first()
            if role:
                user.roles.append(role)
        
        db.session.commit()
        
        return jsonify({
            "msg": f"Roles updated for {email}",
            "new_roles": [r.role_name for r in user.roles]
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Failed to fix roles: {str(e)}"}), 500
    
@auth_bp.route('/debug-token', methods=['GET'])
@jwt_required()
def debug_token():
    try:
        current_user = get_jwt_identity()
        claims = get_jwt()
        return jsonify({
            'success': True,
            'identity': current_user,
            'roles': claims.get('roles', []),
            'claims': claims
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500