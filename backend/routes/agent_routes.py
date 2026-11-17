from flask import Blueprint, request, jsonify, current_app
from backend.middleware.auth_middleware import role_required
from backend.middleware.security import sanitize_text

agent_bp = Blueprint("agent", __name__, url_prefix="/api/agent")

@agent_bp.route("/tickets", methods=["GET"])
@role_required(["agent", "admin"])
def get_assigned_tickets():
    db = current_app.config["DB_MANAGER"]
    tickets = db.get_agent_tickets(request.current_user["id"])
    return jsonify({"tickets": tickets}), 200

@agent_bp.route("/tickets/<ticket_id>/respond", methods=["POST"])
@role_required(["agent", "admin"])
def respond_to_customer(ticket_id):
    data = request.get_json() or {}
    response_text = sanitize_text(data.get("message", ""))
    new_status = data.get("status", "IN_PROGRESS").upper()

    if not response_text:
        return jsonify({"error": "Bad Request", "message": "Response message cannot be empty."}), 400

    db = current_app.config["DB_MANAGER"]
    ticket = db.get_ticket_by_id(ticket_id)
    if not ticket:
        return jsonify({"error": "Not Found", "message": "Ticket not found."}), 404

    # Add public response note
    note = db.add_ticket_note(
        ticket_id=ticket["id"],
        author_id=request.current_user["id"],
        note=response_text,
        is_internal=False
    )

    # Update ticket status
    if new_status in ("IN_PROGRESS", "RESOLVED", "CLOSED", "ESCALATED"):
        db.update_ticket_status(ticket["id"], new_status, updated_by_id=request.current_user["id"])

    return jsonify({
        "message": "Response sent to customer successfully.",
        "note": note,
        "ticket": db.get_ticket_by_id(ticket["id"])
    }), 200

@agent_bp.route("/status", methods=["PUT"])
@role_required(["agent", "admin"])
def update_status():
    data = request.get_json() or {}
    is_available = data.get("is_available")
    department = sanitize_text(data.get("department")) if data.get("department") else None
    max_tickets = data.get("max_tickets")
    skills = data.get("skills")

    db = current_app.config["DB_MANAGER"]
    updated = db.update_agent_status(
        agent_id=request.current_user["id"],
        is_available=is_available,
        department=department,
        max_tickets=max_tickets,
        skills=skills
    )

    return jsonify({
        "message": "Agent status updated successfully.",
        "profile": updated
    }), 200
