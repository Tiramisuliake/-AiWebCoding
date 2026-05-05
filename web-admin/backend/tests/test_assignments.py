from app.components.security import hash_password
from app.database.conn import get_session
from app.database.entity.models import Permission, Role, User
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


def test_assign_role_menus_with_permissions_success(client, auth_header, app):
    with app.app_context():
        session = get_session()
        role = Role(name="menu_perm_role", description="menu perm role")
        session.add(role)
        session.flush()

        menu = get_menu_by_route_path(session, "/users")
        assert menu is not None

        permissions = (
            session.query(Permission)
            .filter(Permission.code.in_(["user:list", "user:read"]))
            .order_by(Permission.id.asc())
            .all()
        )
        assert len(permissions) == 2
        permission_ids = [item.id for item in permissions]
        role_id = role.id
        menu_id = menu.id
        session.commit()

    response = client.post(
        f"/api/roles/{role_id}/menus",
        headers=auth_header,
        json={"menu_ids": [menu_id], "permission_ids": permission_ids},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["code"] == 0
    assert payload["data"]["menu_ids"] == [menu_id]
    assert payload["data"]["permission_ids"] == permission_ids
    assert payload["data"]["warnings"] == []

    with app.app_context():
        session = get_session()
        saved_role = session.get(Role, role_id)
        assert saved_role is not None
        assert {menu.id for menu in saved_role.menus} == {menu_id}
        assert {permission.id for permission in saved_role.permissions} == set(permission_ids)


def test_assign_role_menus_with_permissions_out_of_scope_rejected(client, auth_header, app):
    with app.app_context():
        session = get_session()
        role = Role(name="menu_perm_scope_role", description="menu perm scope role")
        session.add(role)
        session.flush()

        menu = get_menu_by_route_path(session, "/users")
        assert menu is not None
        out_of_scope_permission = (
            session.query(Permission)
            .filter(Permission.code == "role:create")
            .first()
        )
        assert out_of_scope_permission is not None
        role_id = role.id
        menu_id = menu.id
        permission_id = out_of_scope_permission.id
        session.commit()

    response = client.post(
        f"/api/roles/{role_id}/menus",
        headers=auth_header,
        json={"menu_ids": [menu_id], "permission_ids": [permission_id]},
    )
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["code"] == 1001
    assert payload["data"]["invalid_permission_ids"] == [permission_id]

    with app.app_context():
        session = get_session()
        saved_role = session.get(Role, role_id)
        assert saved_role is not None
        assert saved_role.menus == []
        assert saved_role.permissions == []


def test_assign_role_menus_with_permissions_requires_assign_permission(client, app):
    with app.app_context():
        session = get_session()
        target_role = Role(name="target_role_for_combo_assign", description="target role")
        session.add(target_role)
        session.flush()

        menu = get_menu_by_route_path(session, "/users")
        assert menu is not None
        user_list_permission = session.query(Permission).filter(Permission.code == "user:list").first()
        assert user_list_permission is not None

        operator_permissions = (
            session.query(Permission)
            .filter(Permission.code.in_(["role:assign_menu"]))
            .all()
        )
        assert len(operator_permissions) == 1
        operator_role = Role(name="menu_only_operator_role", description="menu only operator")
        operator_role.permissions = operator_permissions
        session.add(operator_role)
        session.flush()

        operator_user = User(
            username="menu_only_operator",
            email="menu_only_operator@example.com",
            password_hash=hash_password("password123"),
            is_active=True,
        )
        operator_user.roles.append(operator_role)
        session.add(operator_user)
        session.commit()

        target_role_id = target_role.id
        menu_id = menu.id
        permission_id = user_list_permission.id

    login_response = client.post(
        "/api/auth/login",
        json={"username": "menu_only_operator", "password": "password123"},
    )
    login_payload = login_response.get_json()
    token = login_payload["data"]["access_token"]
    header = {"Authorization": f"Bearer {token}"}

    response = client.post(
        f"/api/roles/{target_role_id}/menus",
        headers=header,
        json={"menu_ids": [menu_id], "permission_ids": [permission_id]},
    )
    payload = response.get_json()

    assert response.status_code == 403
    assert payload["code"] == 2002
