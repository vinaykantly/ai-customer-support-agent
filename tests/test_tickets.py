import pytest

def test_create_ticket_and_auto_assign(client, customer_token):
    res = client.post("/api/tickets", json={
        "title": "Need help with API authentication",
        "description": "Getting 401 unauthorized on token refresh.",
        "category": "TECHNICAL",
        "priority": "HIGH"
    }, headers={
        "Authorization": f"Bearer {customer_token}"
    })
    assert res.status_code == 201
    ticket = res.get_json()["ticket"]
    assert ticket["ticket_number"].startswith("TIK-")
    assert ticket["category"] == "TECHNICAL"
    assert ticket["priority"] == "HIGH"
    assert ticket["status"] == "OPEN"
    # Auto-assigned to an agent
    assert ticket["assigned_agent_id"] is not None

def test_list_customer_tickets(client, customer_token):
    res = client.get("/api/tickets", headers={
        "Authorization": f"Bearer {customer_token}"
    })
    assert res.status_code == 200
    tickets = res.get_json()["tickets"]
    assert len(tickets) > 0
    # Customer can only view their own tickets
    for t in tickets:
        assert t["customer_id"] == "c0000000-0000-0000-0000-000000000001"

def test_agent_update_ticket_status(client, agent_token):
    # Retrieve assigned ticket
    ticket_id = "t0000000-0000-0000-0000-000000000001"
    res = client.put(f"/api/tickets/{ticket_id}/status", json={
        "status": "RESOLVED"
    }, headers={
        "Authorization": f"Bearer {agent_token}"
    })
    assert res.status_code == 200
    ticket = res.get_json()["ticket"]
    assert ticket["status"] == "RESOLVED"
    assert ticket["resolved_at"] is not None

def test_agent_reply_and_internal_notes(client, agent_token):
    ticket_id = "t0000000-0000-0000-0000-000000000002"
    # Public response
    res = client.post(f"/api/agent/tickets/{ticket_id}/respond", json={
        "message": "We have investigated the 429 rate limit issue and adjusted your quota.",
        "status": "IN_PROGRESS"
    }, headers={
        "Authorization": f"Bearer {agent_token}"
    })
    assert res.status_code == 200

    # Internal note
    res2 = client.post(f"/api/tickets/{ticket_id}/notes", json={
        "note": "Checked Redis rate limiter cluster. Pod restarted.",
        "is_internal": True
    }, headers={
        "Authorization": f"Bearer {agent_token}"
    })
    assert res2.status_code == 201
    assert res2.get_json()["note"]["is_internal"] is True
