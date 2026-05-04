from pathlib import Path

from sqlalchemy import select

from app import create_app
from app.const.permissions import BUILTIN_PERMISSION_LOCALIZATION_ZH
from app.database.conn import create_all, drop_all, get_session, remove_session
from app.database.entity.models import Permission
from app.service import seed_rbac
from app.service.rbac_seed_service import sync_builtin_permissions_to_cn


def _create_file_app(db_file: Path, sync_enabled: bool):
    return create_app(
        config_name="testing",
        config_overrides={
            "TESTING": True,
            "JWT_SECRET_KEY": "test-secret-key-for-jwt-at-least-32",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_file.as_posix()}",
            "CELERY_BROKER_URL": "memory://localhost/",
            "CELERY_RESULT_BACKEND": "cache+memory://",
            "PERMISSION_CN_SYNC_ON_STARTUP": sync_enabled,
        },
    )


def test_builtin_permission_sync_on_startup_updates_history_data(tmp_path):
    db_file = tmp_path / "permission_localization.sqlite"

    init_app = _create_file_app(db_file, sync_enabled=False)
    with init_app.app_context():
        create_all()
        seed_rbac(
            admin_username="admin",
            admin_email="admin@example.com",
            admin_password="password123",
        )

        session = get_session()
        permission = session.execute(
            select(Permission).where(Permission.code == "user:list")
        ).scalar_one()
        permission.name = "User List"
        permission.description = "user:list permission"

        custom_permission = Permission(
            name="Custom Permission",
            code="custom:feature",
            description="custom permission",
        )
        session.add(custom_permission)
        session.commit()

    synced_app = _create_file_app(db_file, sync_enabled=True)
    with synced_app.app_context():
        session = get_session()
        user_list_permission = session.execute(
            select(Permission).where(Permission.code == "user:list")
        ).scalar_one()
        localized = BUILTIN_PERMISSION_LOCALIZATION_ZH["user:list"]
        assert user_list_permission.name == localized["name"]
        assert user_list_permission.description == localized["description"]

        custom_permission = session.execute(
            select(Permission).where(Permission.code == "custom:feature")
        ).scalar_one()
        assert custom_permission.name == "Custom Permission"
        assert custom_permission.description == "custom permission"

        drop_all()

    remove_session()


def test_sync_builtin_permissions_to_cn_is_idempotent(app):
    with app.app_context():
        session = get_session()
        permission = session.execute(
            select(Permission).where(Permission.code == "role:create")
        ).scalar_one()
        permission.name = "Role Create"
        permission.description = "role:create permission"
        session.commit()

        first_result = sync_builtin_permissions_to_cn()
        second_result = sync_builtin_permissions_to_cn()

        refreshed_permission = session.execute(
            select(Permission).where(Permission.code == "role:create")
        ).scalar_one()
        localized = BUILTIN_PERMISSION_LOCALIZATION_ZH["role:create"]

        assert first_result["updated"] >= 1
        assert second_result["updated"] == 0
        assert refreshed_permission.name == localized["name"]
        assert refreshed_permission.description == localized["description"]


def test_permissions_support_chinese_name_search(client, auth_header):
    permission_name = BUILTIN_PERMISSION_LOCALIZATION_ZH["user:list"]["name"]
    response = client.get(
        "/api/permissions",
        headers=auth_header,
        query_string={"name": permission_name},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["code"] == 0
    assert any(item["code"] == "user:list" for item in payload["data"]["items"])
