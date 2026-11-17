import pytest

def test_unauthenticated_request_blocked(client):
    res = client.get("/api/auth/profile")
    assert res.status_code == 401
    assert "token is missing" in res.get_json()["message"]

def test_customer_cannot_access_admin_analytics(client, customer_token):
    res = client.get("/api/admin/analytics", headers={
        "Authorization": f"Bearer {customer_token}"
    })
    assert res.status_code == 403
    assert "Access denied" in res.get_json()["message"]

def test_customer_cannot_access_agent_queue(client, customer_token):
    res = client.get("/api/agent/tickets", headers={
        "Authorization": f"Bearer {customer_token}"
    })
    assert res.status_code == 403

def test_agent_cannot_access_admin_analytics(client, agent_token):
    res = client.get("/api/admin/analytics", headers={
        "Authorization": f"Bearer {agent_token}"
    })
    assert res.status_code == 403

def test_admin_has_full_access(client, admin_token):
    res = client.get("/api/admin/analytics", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "metrics" in data

def test_customer_cannot_see_internal_notes(client, customer_token, agent_token):
    ticket_id = "t0000000-0000-0000-0000-000000000001"
    # Agent views ticket - includes internal note
    agent_res = client.get(f"/api/tickets/{ticket_id}", headers={
        "Authorization": f"Bearer {agent_token}"
    })
    agent_notes = agent_res.get_json()["ticket"]["notes"]
    has_internal = any(n["is_internal"] for n in agent_notes)
    assert has_internal is True

    # Customer views ticket - internal notes filtered out
    cust_res = client.get(f"/api/tickets/{ticket_id}", headers={
        "Authorization": f"Bearer {customer_token}"
    })
    cust_notes = cust_res.get_json()["ticket"]["notes"]
    for n in cust_notes:
        assert n["is_internal"] == 0 or n["is_internal"] is False
