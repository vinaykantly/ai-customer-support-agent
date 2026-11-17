import jwt
from functools import wraps
from datetime import datetime, timedelta, timezone
from flask import request, jsonify, current_app

def create_access_token(user_id, email, role, full_name=None, expires_in=86400):
    """Generates a secure signed JWT token"""
    secret = current_app.config.get("JWT_SECRET_KEY", "jwt-secret-key-fallback")
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "full_name": full_name or "",
        "iat": now,
        "exp": now + timedelta(seconds=expires_in)
    }
    return jwt.encode(payload, secret, algorithm="HS256")

def decode_access_token(token):
    """Decodes and validates a JWT token"""
    secret = current_app.config.get("JWT_SECRET_KEY", "jwt-secret-key-fallback")
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Middleware decorator ensuring a valid JWT is present"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        token = None

        if auth_header:
            parts = auth_header.split(" ")
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
            elif len(parts) == 1:
                token = parts[0]

        if not token:
            # Check cookie fallback for browser pages
            token = request.cookies.get("access_token")

        if not token:
            return jsonify({"error": "Unauthorized", "message": "Authentication token is missing"}), 401

        payload = decode_access_token(token)
        if not payload:
            return jsonify({"error": "Unauthorized", "message": "Token has expired or is invalid"}), 401

        # Fetch current user profile
        db = current_app.config["DB_MANAGER"]
        user = db.get_profile_by_id(payload["sub"])
        if not user or not user.get("is_active", 1):
            return jsonify({"error": "Unauthorized", "message": "User account inactive or not found"}), 401

        request.current_user = user
        return f(*args, **kwargs)

    return decorated

def role_required(allowed_roles):
    """
    Middleware decorator enforcing Role-Based Access Control (RBAC).
    allowed_roles: string or list/tuple of strings e.g. ['admin', 'agent']
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(f):
        @wraps(f)
        @token_required
        def decorated_function(*args, **kwargs):
            user = getattr(request, "current_user", None)
            if not user:
                return jsonify({"error": "Unauthorized", "message": "User not authenticated"}), 401
            
            user_role = user.get("role", "customer")
            if user_role not in allowed_roles:
                return jsonify({
                    "error": "Forbidden",
                    "message": f"Access denied. Requires one of roles: {', '.join(allowed_roles)}"
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
