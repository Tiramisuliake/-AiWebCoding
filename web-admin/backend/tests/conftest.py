import pytest

from app import create_app
from app.database import create_all, drop_all, get_session, remove_session
from app.rbac.services import seed_rbac


def _seed_base_data(session):
    seed_value = "password123"
    seed_rbac(
        session=session,
        admin_username="admin",
        admin_email="admin@example.com",
        admin_password=seed_value,
    )


@pytest.fixture()
def app():
    app = create_app(
        config_name="testing",
        config_overrides={
            "TESTING": True,
            "JWT_SECRET_KEY": "test-secret-key-for-jwt-at-least-32",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "CELERY_BROKER_URL": "memory://localhost/",
            "CELERY_RESULT_BACKEND": "cache+memory://",
        },
    )

    with app.app_context():
        create_all()
        _seed_base_data(get_session())
        yield app
        remove_session()
        drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_header(client):
    response = client.post(
        "/api/auth/login", json={"username": "admin", "password": "password123"}
    )
    data = response.get_json()
    token = data["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
