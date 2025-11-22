from flask import Blueprint, request, jsonify
from models import db, User, Role
from werkzeug.security import generate_password_hash, check_password_hash

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    # Hash password
    hashed_pw = generate_password_hash(data["password"], method="pbkdf2:sha256")

    # Create user (without roles first)
    new_user = User(
        name=data["name"],
        email=data["email"],
        password=hashed_pw,
        phone=data.get("phone"),
        location_lat=data.get("location_lat"),
        location_long=data.get("location_long")
    )

    # Assign roles (expects array like ["donor", "receiver"])
    role_names = data.get("roles", [])

    for role_name in role_names:
        role = Role.query.filter_by(role_name=role_name).first()
        if role:
            new_user.roles.append(role)
        else:
            return jsonify({"error": f"Role '{role_name}' not found"}), 400

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 201

# ------------------------------------------------------
# LOGIN
# ------------------------------------------------------
@user_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "Invalid email"}), 400

    if not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid password"}), 400

    return jsonify({
        "message": "Login successful",
        "user_id": user.user_id,
        "roles": [role.role_name for role in user.roles]
    }), 200


# ------------------------------------------------------
# GET PROFILE
# ------------------------------------------------------
@user_bp.route("/profile/<int:user_id>", methods=["GET"])
def get_profile(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "location_lat": user.location_lat,
        "location_long": user.location_long,
        "roles": [r.role_name for r in user.roles]
    }), 200

# ------------------------------------------------------
# UPDATE PROFILE
# ------------------------------------------------------
@user_bp.route("/profile/<int:user_id>", methods=["PUT"])
def update_profile(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json

    user.name = data.get("name", user.name)
    user.phone = data.get("phone", user.phone)
    user.location_lat = data.get("location_lat", user.location_lat)
    user.location_long = data.get("location_long", user.location_long)

    db.session.commit()

    return jsonify({"message": "Profile updated"}), 200
