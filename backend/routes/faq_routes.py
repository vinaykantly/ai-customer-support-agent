from flask import Blueprint, request, jsonify, current_app
from backend.middleware.auth_middleware import role_required
from backend.middleware.security import sanitize_text

faq_bp = Blueprint("faqs", __name__, url_prefix="/api/faqs")

@faq_bp.route("", methods=["GET"])
def list_faqs():
    active_only = request.args.get("all", "false").lower() != "true"
    db = current_app.config["DB_MANAGER"]
    faqs = db.get_all_faqs(active_only=active_only)
    return jsonify({"faqs": faqs}), 200

@faq_bp.route("", methods=["POST"])
@role_required(["admin"])
def create_faq():
    data = request.get_json() or {}
    question = sanitize_text(data.get("question", ""))
    answer = sanitize_text(data.get("answer", ""))
    category = sanitize_text(data.get("category", "GENERAL")).upper()

    if not question or not answer:
        return jsonify({"error": "Bad Request", "message": "Question and answer are required."}), 400

    db = current_app.config["DB_MANAGER"]
    faq = db.create_faq(question=question, answer=answer, category=category)
    return jsonify({"message": "FAQ created successfully.", "faq": faq}), 201

@faq_bp.route("/<faq_id>", methods=["PUT"])
@role_required(["admin"])
def update_faq(faq_id):
    data = request.get_json() or {}
    question = sanitize_text(data.get("question")) if data.get("question") else None
    answer = sanitize_text(data.get("answer")) if data.get("answer") else None
    category = sanitize_text(data.get("category")).upper() if data.get("category") else None
    is_active = data.get("is_active")

    db = current_app.config["DB_MANAGER"]
    updated = db.update_faq(faq_id, question=question, answer=answer, category=category, is_active=is_active)
    if not updated:
        return jsonify({"error": "Not Found", "message": "FAQ not found."}), 404

    return jsonify({"message": "FAQ updated successfully.", "faq": updated}), 200

@faq_bp.route("/<faq_id>", methods=["DELETE"])
@role_required(["admin"])
def delete_faq(faq_id):
    db = current_app.config["DB_MANAGER"]
    db.delete_faq(faq_id)
    return jsonify({"message": "FAQ deleted successfully."}), 200
