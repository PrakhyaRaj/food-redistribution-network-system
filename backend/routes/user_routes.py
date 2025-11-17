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

