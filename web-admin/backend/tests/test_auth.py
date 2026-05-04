from app.components.security import hash_password
from app.database.conn import get_session
from app.database.entity.models import User


def _login(client, username, password):
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    payload = response.get_json()
    assert response.status_code == 200
    return payload["data"]["access_token"], payload["data"]["refresh_token"]


def test_login_success(client):
    response = client.post(
        "/api/auth/login", json={"username": "admin", "password": "password123"}
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["code"] == 0
    assert payload["msg"] == "ok"
    assert payload["data"]["access_token"]
    assert payload["data"]["refresh_token"]
    assert payload["data"]["user"]["username"] == "admin"


def test_login_invalid_credentials(client):
    response = client.post(
        "/api/auth/login", json={"username": "admin", "password": "wrong-password"}
    )
    payload = response.get_json()

    assert response.status_code == 401
    assert payload["code"] == 2001


def test_users_requires_token(client):
    response = client.get("/api/users")
    payload = response.get_json()

    assert response.status_code == 401
    assert payload["code"] == 2001


def test_users_with_token(client, auth_header):
    response = client.get("/api/users", headers=auth_header)
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["code"] == 0
    assert payload["data"]["total"] >= 1


def test_logout_requires_refresh_token(client, auth_header):
    response = client.post("/api/auth/logout", headers=auth_header, json={})
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["code"] == 1001


def test_logout_revokes_access_and_refresh(client):
    access_token, refresh_token = _login(client, "admin", "password123")

    logout_response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"refresh_token": refresh_token},
    )
    logout_payload = logout_response.get_json()
    assert logout_response.status_code == 200
    assert logout_payload["code"] == 0

    users_response = client.get(
        "/api/users", headers={"Authorization": f"Bearer {access_token}"}
    )
    users_payload = users_response.get_json()
    assert users_response.status_code == 401
    assert users_payload["code"] == 2001

    refresh_response = client.post(
        "/api/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    refresh_payload = refresh_response.get_json()
    assert refresh_response.status_code == 401
    assert refresh_payload["code"] == 2001


def test_logout_rejects_mismatched_refresh_token(client, app):
    with app.app_context():
        session = get_session()
        viewer = User(
            username="viewer_auth",
            email="viewer_auth@example.com",
            password_hash=hash_password("password123"),
            is_active=True,
        )
        session.add(viewer)
        session.commit()

    admin_access_token, _ = _login(client, "admin", "password123")
    _, viewer_refresh_token = _login(client, "viewer_auth", "password123")

    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {admin_access_token}"},
        json={"refresh_token": viewer_refresh_token},
    )
    payload = response.get_json()

    assert response.status_code == 401
    assert payload["code"] == 2001
