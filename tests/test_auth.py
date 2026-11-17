import pytest
import uuid

def test_user_registration_success(client):
    unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    res = client.post("/api/auth/register", json={
        "full_name": "Test User",
        "email": unique_email,
        "password": "Password@123",
        "role": "customer"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert "access_token" in data
    assert data["user"]["email"] == unique_email
    assert data["user"]["role"] == "customer"

def test_user_registration_duplicate_email(client):
    res = client.post("/api/auth/register", json={
        "full_name": "Duplicate User",
        "email": "customer@example.com", # already in seed
        "password": "Password@123"
    })
    assert res.status_code == 409
    data = res.get_json()
    assert "already exists" in data["message"]

def test_user_registration_invalid_password(client):
    res = client.post("/api/auth/register", json={
        "full_name": "Short Pwd",
        "email": "shortpwd@example.com",
        "password": "123"
    })
    assert res.status_code == 400

def test_user_login_success(client):
    res = client.post("/api/auth/login", json={
        "email": "customer@example.com",
        "password": "Customer@123"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data
    assert data["user"]["email"] == "customer@example.com"

def test_user_login_invalid_password(client):
    res = client.post("/api/auth/login", json={
        "email": "customer@example.com",
        "password": "WrongPassword!"
    })
    assert res.status_code == 401

def test_get_profile(client, customer_token):
    res = client.get("/api/auth/profile", headers={
        "Authorization": f"Bearer {customer_token}"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["user"]["email"] == "customer@example.com"

def test_update_profile(client, customer_token):
    res = client.put("/api/auth/profile", json={
        "full_name": "Ananya Updated",
        "phone": "+1-555-999-8888"
    }, headers={
        "Authorization": f"Bearer {customer_token}"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["user"]["full_name"] == "Ananya Updated"
