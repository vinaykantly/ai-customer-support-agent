from flask import Blueprint, request, jsonify, current_app
from backend.middleware.auth_middleware import token_required

notification_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")

@notification_bp.route("", methods=["GET"])
@token_required
def get_notifications():
    unread_only = request.args.get("unread", "false").lower() == "true"
    db = current_app.config["DB_MANAGER"]
    notifs = db.get_user_notifications(request.current_user["id"], unread_only=unread_only)
    return jsonify({"notifications": notifs}), 200

@notification_bp.route("/<notif_id>/read", methods=["PUT"])
@token_required
def mark_read(notif_id):
    db = current_app.config["DB_MANAGER"]
    db.mark_notification_read(notif_id, request.current_user["id"])
    return jsonify({"message": "Notification marked as read."}), 200
