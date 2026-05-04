from app.database.conn import get_session
from app.database.entity.models import Permission, Role
from app.database.repository.rbac_repository import get_menu_by_route_path


def test_assign_user_roles_partial_warning(client, auth_header, app):
    with app.app_context():
        session = get_session()
        role = Role(name="ops_role", description="ops role")
        session.add(role)
        session.commit()
        role_id = role.id

    response = client.post(
        "/api/users/1/roles",
        headers=auth_header,
        json={"role_ids": [role_id, 999999, "bad-id"]},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["code"] == 0
    assert role_id in payload["data"]["applied_ids"]
    assert role_id in payload["data"]["role_ids"]
    assert 999999 in payload["data"]["invalid_ids"]
    assert "bad-id" in payload["data"]["invalid_ids"]
    assert payload["data"]["warnings"]


def test_assign_role_permissions_partial_warning(client, auth_header, app):
    with app.app_context():
        session = get_session()
        role = Role(name="perm_role", description="permission role")
        session.add(role)
        valid_permission = session.query(Permission).first()
        assert valid_permission is not None
        session.commit()
        role_id = role.id
        permission_id = valid_permission.id

    response = client.post(
        f"/api/roles/{role_id}/permissions",
        headers=auth_header,
        json={"permission_ids": [permission_id, 999999, "bad-id"]},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["code"] == 0
    assert permission_id in payload["data"]["permission_ids"]
    assert permission_id in payload["data"]["applied_ids"]
    assert 999999 in payload["data"]["invalid_ids"]
    assert "bad-id" in payload["data"]["invalid_ids"]
    assert payload["data"]["warnings"]


def test_assign_role_menus_partial_warning(client, auth_header, app):
    with app.app_context():
        session = get_session()
        role = Role(name="menu_role", description="menu role")
        session.add(role)
        session.flush()
        menu = get_menu_by_route_path(session, "/permissions")
        assert menu is not None
        session.commit()
        role_id = role.id
        menu_id = menu.id

    response = client.post(
        f"/api/roles/{role_id}/menus",
        headers=auth_header,
        json={"menu_ids": [menu_id, 999999, "bad-id"]},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["code"] == 0
    assert menu_id in payload["data"]["menu_ids"]
    assert menu_id in payload["data"]["applied_ids"]
    assert 999999 in payload["data"]["invalid_ids"]
    assert "bad-id" in payload["data"]["invalid_ids"]
    assert payload["data"]["warnings"]
