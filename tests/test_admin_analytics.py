import pytest

def test_admin_analytics_kpis(client, admin_token):
    res = client.get("/api/admin/analytics", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert res.status_code == 200
    m = res.get_json()["metrics"]
    assert "total_customers" in m
    assert "total_tickets" in m
    assert "open_tickets" in m
    assert "resolved_tickets" in m
    assert "customer_satisfaction_rating" in m
    assert m["customer_satisfaction_rating"] > 0

def test_admin_list_users_and_agents(client, admin_token):
    res_users = client.get("/api/admin/users", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert res_users.status_code == 200
    assert len(res_users.get_json()["users"]) >= 3

    res_agents = client.get("/api/admin/agents", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert res_agents.status_code == 200
    agents = res_agents.get_json()["agents"]
    assert len(agents) >= 2
    assert "department" in agents[0]

def test_faq_crud_lifecycle(client, admin_token):
    # Create FAQ
    res_create = client.post("/api/faqs", json={
        "question": "How do I download tax invoices?",
        "answer": "Go to Account Settings > Billing > Invoices and click 'Download PDF'.",
        "category": "BILLING"
    }, headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert res_create.status_code == 201
    faq_id = res_create.get_json()["faq"]["id"]

    # Read FAQs
    res_list = client.get("/api/faqs")
    assert res_list.status_code == 200
    assert any(f["id"] == faq_id for f in res_list.get_json()["faqs"])

    # Delete FAQ
    res_delete = client.delete(f"/api/faqs/{faq_id}", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert res_delete.status_code == 200
