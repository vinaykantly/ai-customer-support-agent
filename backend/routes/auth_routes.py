from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash
from backend.middleware.auth_middleware import create_access_token, token_required
from backend.middleware.security import validate_email, validate_password_strength, sanitize_text
from backend.middleware.rate_limiter import rate_limit

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
@rate_limit()
def register():
    data = request.get_json() or {}
    email = sanitize_text(data.get("email", "")).lower()
    password = data.get("password", "")
    full_name = sanitize_text(data.get("full_name", ""))
    role = data.get("role", "customer").lower()
    phone = sanitize_text(data.get("phone", ""))
    department = sanitize_text(data.get("department", "General Support"))

    if not email or not password or not full_name:
        return jsonify({"error": "Bad Request", "message": "Email, password, and full name are required."}), 400

    if not validate_email(email):
        return jsonify({"error": "Bad Request", "message": "Invalid email address format."}), 400

    valid_pwd, pwd_msg = validate_password_strength(password)
    if not valid_pwd:
        return jsonify({"error": "Bad Request", "message": pwd_msg}), 400

    if role not in ("customer", "agent"):
        role = "customer"

    db = current_app.config["DB_MANAGER"]
    existing = db.get_profile_by_email(email)
    if existing:
        return jsonify({"error": "Conflict", "message": "An account with this email already exists."}), 409

    try:
        new_user = db.create_profile(
            email=email,
            password=password,
            full_name=full_name,
            role=role,
            phone=phone,
            department=department
        )
        token = create_access_token(
            user_id=new_user["id"],
            email=new_user["email"],
            role=new_user["role"],
            full_name=new_user["full_name"]
        )
        return jsonify({
            "message": "Registration successful.",
            "access_token": token,
            "user": {
                "id": new_user["id"],
                "email": new_user["email"],
                "full_name": new_user["full_name"],
                "role": new_user["role"]
            }
        }), 201
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@auth_bp.route("/login", methods=["POST"])
@rate_limit()
def login():
    data = request.get_json() or {}
    email = sanitize_text(data.get("email", "")).lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Bad Request", "message": "Email and password are required."}), 400

    db = current_app.config["DB_MANAGER"]
    user = db.get_profile_by_email(email)
    if not user:
        return jsonify({"error": "Unauthorized", "message": "Invalid email or password."}), 401

    if not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Unauthorized", "message": "Invalid email or password."}), 401

    if not user.get("is_active", 1):
        return jsonify({"error": "Forbidden", "message": "Account has been deactivated. Contact support."}), 403

    token = create_access_token(
        user_id=user["id"],
        email=user["email"],
        role=user["role"],
        full_name=user["full_name"]
    )

    return jsonify({
        "message": "Login successful.",
        "access_token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "phone": user.get("phone", ""),
            "avatar_url": user.get("avatar_url", "")
        }
    }), 200

@auth_bp.route("/profile", methods=["GET"])
@token_required
def get_profile():
    user = request.current_user
    safe_profile = {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"],
        "phone": user.get("phone", ""),
        "avatar_url": user.get("avatar_url", ""),
        "created_at": user.get("created_at", "")
    }
    if user.get("role") == "agent" and "agent_info" in user:
        safe_profile["agent_info"] = user["agent_info"]

    return jsonify({"user": safe_profile}), 200

@auth_bp.route("/profile", methods=["PUT"])
@token_required
def update_profile():
    data = request.get_json() or {}
    full_name = sanitize_text(data.get("full_name")) if data.get("full_name") else None
    phone = sanitize_text(data.get("phone")) if data.get("phone") is not None else None
    password = data.get("password")

    if password:
        valid_pwd, pwd_msg = validate_password_strength(password)
        if not valid_pwd:
            return jsonify({"error": "Bad Request", "message": pwd_msg}), 400

    db = current_app.config["DB_MANAGER"]
    updated = db.update_profile(
        user_id=request.current_user["id"],
        full_name=full_name,
        phone=phone,
        password=password
    )

    return jsonify({
        "message": "Profile updated successfully.",
        "user": {
            "id": updated["id"],
            "email": updated["email"],
            "full_name": updated["full_name"],
            "role": updated["role"],
            "phone": updated.get("phone", "")
        }
    }), 200

@auth_bp.route("/logout", methods=["POST"])
def logout():
    # In stateless JWT, client deletes token; endpoint confirms success
    return jsonify({"message": "Logged out successfully."}), 200
