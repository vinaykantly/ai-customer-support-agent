import os
import pytest
from pathlib import Path
from backend.app import create_app
from backend.middleware.auth_middleware import create_access_token

@pytest.fixture(scope="session", autouse=True)
def clean_test_db():
    test_db = Path(__file__).resolve().parent.parent / "backend" / "database" / "test_support.db"
    if test_db.exists():
        try:
            test_db.unlink()
        except Exception:
            pass
    yield
    if test_db.exists():
        try:
            test_db.unlink()
        except Exception:
            pass

@pytest.fixture
def app():
    app = create_app("testing")
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    return app.config["DB_MANAGER"]

@pytest.fixture
def admin_token(app):
    with app.app_context():
        return create_access_token(
            user_id="a0000000-0000-0000-0000-000000000001",
            email="admin@company.com",
            role="admin",
            full_name="System Administrator"
        )

@pytest.fixture
def agent_token(app):
    with app.app_context():
        return create_access_token(
            user_id="b0000000-0000-0000-0000-000000000001",
            email="agent.rajesh@company.com",
            role="agent",
            full_name="Rajesh Sharma"
        )

@pytest.fixture
def customer_token(app):
    with app.app_context():
        return create_access_token(
            user_id="c0000000-0000-0000-0000-000000000001",
            email="customer@example.com",
            role="customer",
            full_name="Ananya Roy"
        )
