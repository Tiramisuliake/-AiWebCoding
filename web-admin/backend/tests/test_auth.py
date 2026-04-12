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
