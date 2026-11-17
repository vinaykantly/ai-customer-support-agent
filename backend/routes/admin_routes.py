from flask import Blueprint, request, jsonify, current_app
from backend.middleware.auth_middleware import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

@admin_bp.route("/analytics", methods=["GET"])
@role_required(["admin"])
def get_analytics():
    db = current_app.config["DB_MANAGER"]
    metrics = db.get_admin_metrics()
    return jsonify({"metrics": metrics}), 200

@admin_bp.route("/users", methods=["GET"])
@role_required(["admin"])
def get_users():
    role_filter = request.args.get("role")
    db = current_app.config["DB_MANAGER"]
    users = db.get_all_profiles(role_filter=role_filter)
    return jsonify({"users": users}), 200

@admin_bp.route("/agents", methods=["GET"])
@role_required(["admin"])
def get_agents():
    db = current_app.config["DB_MANAGER"]
    agents = db.get_agents_list()
    return jsonify({"agents": agents}), 200

@admin_bp.route("/conversations", methods=["GET"])
@role_required(["admin"])
def get_conversations():
    limit = int(request.args.get("limit", 50))
    db = current_app.config["DB_MANAGER"]
    conversations = db.get_all_conversations(limit=limit)
    return jsonify({"conversations": conversations}), 200

@admin_bp.route("/feedback", methods=["GET"])
@role_required(["admin"])
def get_feedback():
    limit = int(request.args.get("limit", 50))
    db = current_app.config["DB_MANAGER"]
    feedbacks = db.get_all_feedback(limit=limit)
    return jsonify({"feedback": feedbacks}), 200
