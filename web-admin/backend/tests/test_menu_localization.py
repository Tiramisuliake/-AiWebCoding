from pathlib import Path

from sqlalchemy import select

from app import create_app
from app.components.menu_localization import normalize_menu_name_to_cn
from app.database.conn import create_all, drop_all, get_session, remove_session
from app.database.entity.models import Menu
from app.database.repository.rbac_repository import get_menu_by_route_path
from app.service import seed_rbac
from app.service.menu_service import sync_menu_names_to_cn


def _create_file_app(db_file: Path, sync_enabled: bool, force_on_write: bool):
    return create_app(
        config_name="testing",
        config_overrides={
            "TESTING": True,
            "JWT_SECRET_KEY": "test-secret-key-for-jwt-at-least-32",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_file.as_posix()}",
            "CELERY_BROKER_URL": "memory://localhost/",
            "CELERY_RESULT_BACKEND": "cache+memory://",
            "MENU_CN_SYNC_ON_STARTUP": sync_enabled,
            "MENU_CN_FORCE_ON_WRITE": force_on_write,
            "PERMISSION_CN_SYNC_ON_STARTUP": False,
        },
    )


def test_menu_sync_on_startup_updates_builtin_and_custom_names(tmp_path):
    db_file = tmp_path / "menu_localization.sqlite"

    init_app = _create_file_app(db_file, sync_enabled=False, force_on_write=False)
    with init_app.app_context():
        create_all()
        seed_rbac(
            admin_username="admin",
            admin_email="admin@example.com",
            admin_password="password123",
        )

        session = get_session()
        builtin_menu = get_menu_by_route_path(session, "/permissions")
        assert builtin_menu is not None
        builtin_menu.name = "Permissions"

        custom_menu = Menu(name="Ops Center", route_path="/ops-center", sort=500)
        session.add(custom_menu)
        session.commit()

    sync_app = _create_file_app(db_file, sync_enabled=True, force_on_write=True)
    with sync_app.app_context():
        session = get_session()
        builtin_menu = get_menu_by_route_path(session, "/permissions")
        assert builtin_menu is not None
        assert builtin_menu.name == "权限列表"

        custom_menu = session.execute(
            select(Menu).where(Menu.route_path == "/ops-center")
        ).scalar_one()
        assert custom_menu.name == normalize_menu_name_to_cn("Ops Center", "/ops-center")

        drop_all()
    remove_session()


def test_sync_menu_names_to_cn_is_idempotent(app):
    with app.app_context():
        session = get_session()
        menu = get_menu_by_route_path(session, "/roles")
        assert menu is not None
        menu.name = "Roles"
        session.commit()

        first = sync_menu_names_to_cn()
        second = sync_menu_names_to_cn()

        refreshed = get_menu_by_route_path(session, "/roles")
        assert refreshed is not None
        assert refreshed.name == "角色管理"
        assert first["updated"] >= 1
        assert second["updated"] == 0


def test_create_and_update_menu_force_chinese_name(client, auth_header):
    create_response = client.post(
        "/api/menus",
        headers=auth_header,
        json={"name": "Ops Center", "route_path": "/ops-center", "sort": 610},
    )
    create_payload = create_response.get_json()
    assert create_response.status_code == 201
    assert create_payload["code"] == 0
    assert create_payload["data"]["name"] == normalize_menu_name_to_cn("Ops Center", "/ops-center")

    menu_id = create_payload["data"]["id"]

    update_response = client.put(
        f"/api/menus/{menu_id}",
        headers=auth_header,
        json={"name": "Task Board", "route_path": "/task-board"},
    )
    update_payload = update_response.get_json()
    assert update_response.status_code == 200
    assert update_payload["code"] == 0
    assert update_payload["data"]["name"] == normalize_menu_name_to_cn("Task Board", "/task-board")

    cn_response = client.post(
        "/api/menus",
        headers=auth_header,
        json={"name": "自定义中文菜单", "route_path": "/custom-cn-menu", "sort": 620},
    )
    cn_payload = cn_response.get_json()
    assert cn_response.status_code == 201
    assert cn_payload["code"] == 0
    assert cn_payload["data"]["name"] == "自定义中文菜单"

