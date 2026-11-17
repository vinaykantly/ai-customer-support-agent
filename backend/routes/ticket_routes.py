from flask import Blueprint, request, jsonify, current_app
from backend.middleware.auth_middleware import token_required, role_required
from backend.middleware.security import sanitize_text
from backend.middleware.rate_limiter import rate_limit

ticket_bp = Blueprint("tickets", __name__, url_prefix="/api/tickets")

@ticket_bp.route("", methods=["POST"])
@token_required
@rate_limit()
def create_ticket():
    data = request.get_json() or {}
    title = sanitize_text(data.get("title", ""))
    description = sanitize_text(data.get("description", ""))
    category = data.get("category", "GENERAL").upper()
    priority = data.get("priority", "MEDIUM").upper()
    conversation_id = data.get("conversation_id")

    if not title or not description:
        return jsonify({"error": "Bad Request", "message": "Title and description are required."}), 400

    if category not in ("BILLING", "TECHNICAL", "ACCOUNT", "GENERAL", "REFUND", "FEEDBACK"):
        category = "GENERAL"
    if priority not in ("LOW", "MEDIUM", "HIGH", "URGENT"):
        priority = "MEDIUM"

    db = current_app.config["DB_MANAGER"]
    customer_id = request.current_user["id"]

    ticket = db.create_ticket(
        customer_id=customer_id,
        title=title,
        description=description,
        category=category,
        priority=priority,
        conversation_id=conversation_id
    )

    return jsonify({
        "message": "Ticket created successfully.",
        "ticket": ticket
    }), 201

@ticket_bp.route("", methods=["GET"])
@token_required
def list_tickets():
    db = current_app.config["DB_MANAGER"]
    user = request.current_user
    role = user.get("role", "customer")
    status = request.args.get("status")
    priority = request.args.get("priority")
    category = request.args.get("category")

    if role == "customer":
        tickets = db.get_user_tickets(user["id"])
    elif role == "agent":
        tickets = db.get_agent_tickets(user["id"])
    else: # admin
        tickets = db.get_all_tickets(status=status, priority=priority, category=category)

    return jsonify({"tickets": tickets}), 200

@ticket_bp.route("/<ticket_id>", methods=["GET"])
@token_required
def get_ticket(ticket_id):
    db = current_app.config["DB_MANAGER"]
    user = request.current_user
    ticket = db.get_ticket_by_id(ticket_id)

    if not ticket:
        return jsonify({"error": "Not Found", "message": "Ticket not found."}), 404

    # Security check: customers can only view their own tickets
    if user["role"] == "customer" and ticket["customer_id"] != user["id"]:
        return jsonify({"error": "Forbidden", "message": "You cannot access this ticket."}), 403

    # Customers only see public notes, agents/admins see all
    include_internal = user["role"] in ("agent", "admin")
    ticket["notes"] = db.get_ticket_notes(ticket["id"], include_internal=include_internal)

    return jsonify({"ticket": ticket}), 200

@ticket_bp.route("/<ticket_id>/status", methods=["PUT"])
@role_required(["agent", "admin"])
def update_status(ticket_id):
    data = request.get_json() or {}
    new_status = data.get("status", "").upper()

    if new_status not in ("OPEN", "IN_PROGRESS", "ESCALATED", "RESOLVED", "CLOSED"):
        return jsonify({"error": "Bad Request", "message": "Invalid ticket status."}), 400

    db = current_app.config["DB_MANAGER"]
    updated = db.update_ticket_status(ticket_id, new_status, updated_by_id=request.current_user["id"])
    if not updated:
        return jsonify({"error": "Not Found", "message": "Ticket not found."}), 404

    return jsonify({
        "message": f"Ticket status updated to {new_status}.",
        "ticket": updated
    }), 200

@ticket_bp.route("/<ticket_id>/notes", methods=["POST"])
@token_required
def add_note(ticket_id):
    data = request.get_json() or {}
    note_text = sanitize_text(data.get("note", ""))
    is_internal = bool(data.get("is_internal", False))

    if not note_text:
        return jsonify({"error": "Bad Request", "message": "Note content cannot be empty."}), 400

    user = request.current_user
    # Customers cannot post internal notes
    if user["role"] == "customer":
        is_internal = False

    db = current_app.config["DB_MANAGER"]
    ticket = db.get_ticket_by_id(ticket_id)
    if not ticket:
        return jsonify({"error": "Not Found", "message": "Ticket not found."}), 404

    if user["role"] == "customer" and ticket["customer_id"] != user["id"]:
        return jsonify({"error": "Forbidden", "message": "You cannot comment on this ticket."}), 403

    note = db.add_ticket_note(
        ticket_id=ticket["id"],
        author_id=user["id"],
        note=note_text,
        is_internal=is_internal
    )

    return jsonify({
        "message": "Note added successfully.",
        "note": note
    }), 201

@ticket_bp.route("/<ticket_id>/assign", methods=["PUT"])
@role_required(["agent", "admin"])
def assign_ticket(ticket_id):
    data = request.get_json() or {}
    agent_id = data.get("agent_id")

    if not agent_id:
        return jsonify({"error": "Bad Request", "message": "Target agent_id is required."}), 400

    db = current_app.config["DB_MANAGER"]
    updated = db.assign_ticket(ticket_id, agent_id, assigned_by_id=request.current_user["id"])
    if not updated:
        return jsonify({"error": "Not Found", "message": "Ticket not found."}), 404

    return jsonify({
        "message": "Ticket assigned successfully.",
        "ticket": updated
    }), 200
