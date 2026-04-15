from app.components.security import hash_password
from app.database.conn import get_session
from app.database.entity.models import Menu, Role, User
from app.database.repository.rbac_repository import get_menu_by_route_path


def _login(client, username, password):
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    payload = response.get_json()
    assert response.status_code == 200
    return {"Authorization": f"Bearer {payload['data']['access_token']}"}


def test_menu_tree_crud(client, auth_header):
    create_parent_resp = client.post(
        "/api/menus",
        headers=auth_header,
        json={"name": "Ops", "route_path": None, "sort": 90},
    )
    assert create_parent_resp.status_code == 201
    parent_id = create_parent_resp.get_json()["data"]["id"]

    create_child_resp = client.post(
        "/api/menus",
        headers=auth_header,
        json={"name": "Jobs", "parent_id": parent_id, "route_path": "/jobs", "sort": 10},
    )
    assert create_child_resp.status_code == 201
    child_id = create_child_resp.get_json()["data"]["id"]

    tree_resp = client.get("/api/menus", headers=auth_header)
    assert tree_resp.status_code == 200
    tree_payload = tree_resp.get_json()
    assert tree_payload["code"] == 0

    parent_node = next((node for node in tree_payload["data"]["items"] if node["id"] == parent_id), None)
    assert parent_node is not None
    assert any(child["id"] == child_id for child in parent_node["children"])


def test_role_assign_menu_and_my_tree_visibility(client, auth_header, app):
    with app.app_context():
        session = get_session()
        hidden_menu = Menu(
            name="Hidden Menu",
            route_path="/hidden-menu",
            is_visible=False,
            is_enabled=True,
            sort=200,
        )
        disabled_menu = Menu(
            name="Disabled Menu",
            route_path="/disabled-menu",
            is_visible=True,
            is_enabled=False,
            sort=210,
        )
        session.add_all([hidden_menu, disabled_menu])
        session.flush()
        hidden_id = hidden_menu.id
        disabled_id = disabled_menu.id

        viewer_role = Role(name="viewer", description="Viewer role")
        session.add(viewer_role)
        session.flush()

        permissions_menu = get_menu_by_route_path(session, "/permissions")
        assert permissions_menu is not None
        permissions_menu_id = permissions_menu.id
        viewer_role.menus = [permissions_menu, hidden_menu, disabled_menu]

        viewer_user = User(
            username="viewer",
            email="viewer@example.com",
            password_hash=hash_password("password123"),
            is_active=True,
        )
        viewer_user.roles.append(viewer_role)
        session.add(viewer_user)
        session.commit()
        role_id = viewer_role.id

    assign_resp = client.post(
        f"/api/roles/{role_id}/menus",
        headers=auth_header,
        json={"menu_ids": [permissions_menu_id, hidden_id, disabled_id]},
    )
    assert assign_resp.status_code == 200
    assert assign_resp.get_json()["code"] == 0

    viewer_header = _login(client, "viewer", "password123")
    my_tree_resp = client.get("/api/menus/my-tree", headers=viewer_header)
    assert my_tree_resp.status_code == 200
    payload = my_tree_resp.get_json()
    assert payload["code"] == 0

    top_names = {item["name"] for item in payload["data"]["items"]}
    assert "Permission Management" in top_names
    assert "Hidden Menu" not in top_names
    assert "Disabled Menu" not in top_names

    rbac_root = next(item for item in payload["data"]["items"] if item["name"] == "Permission Management")
    child_paths = {child["route_path"] for child in rbac_root["children"]}
    assert "/permissions" in child_paths


def test_admin_my_tree_shows_all_enabled_visible(client, auth_header):
    response = client.get("/api/menus/my-tree", headers=auth_header)
    payload = response.get_json()
    assert response.status_code == 200
    assert payload["code"] == 0
    paths = {
        child["route_path"]
        for top in payload["data"]["items"]
        for child in ([top] + top.get("children", []))
        if child.get("route_path")
    }
    assert "/" in paths
    assert "/users" in paths
    assert "/roles" in paths
    assert "/permissions" in paths
    assert "/menus" in paths
