from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from ..components.security import hash_password
from ..const.permissions import BUILTIN_PERMISSION_LOCALIZATION_ZH, DEFAULT_PERMISSION_CODES
from ..database.conn import get_session
from ..database.entity.models import Menu, Permission, Role, User
from ..database.repository import rbac_repository as repo


def _seed_default_menus(session) -> tuple[list[Menu], int]:
    existing = repo.list_all_menus_ordered(session)
    if existing:
        return existing, 0

    dashboard = Menu(
        name="仪表盘",
        route_path="/",
        icon="HomeFilled",
        sort=10,
        is_visible=True,
        is_enabled=True,
    )
    users = Menu(
        name="用户管理",
        route_path="/users",
        icon="User",
        sort=20,
        is_visible=True,
        is_enabled=True,
        permission_code="user:list",
    )
    rbac_root = Menu(
        name="权限管理",
        route_path=None,
        icon="Lock",
        sort=30,
        is_visible=True,
        is_enabled=True,
    )

    session.add_all([dashboard, users, rbac_root])
    session.flush()

    roles = Menu(
        name="角色管理",
        parent_id=rbac_root.id,
        route_path="/roles",
        icon="UserFilled",
        sort=10,
        is_visible=True,
        is_enabled=True,
        permission_code="role:list",
    )
    permissions = Menu(
        name="权限列表",
        parent_id=rbac_root.id,
        route_path="/permissions",
        icon="Key",
        sort=20,
        is_visible=True,
        is_enabled=True,
        permission_code="permission:list",
    )
    menu_manage = Menu(
        name="菜单管理",
        parent_id=rbac_root.id,
        route_path="/menus",
        icon="Menu",
        sort=30,
        is_visible=True,
        is_enabled=True,
        permission_code="menu:list",
    )
    session.add_all([roles, permissions, menu_manage])
    session.flush()

    return repo.list_all_menus_ordered(session), 6


def seed_rbac(admin_username: str, admin_email: str, admin_password: str) -> dict:
    session = get_session()

    created_permissions = 0
    for code in DEFAULT_PERMISSION_CODES:
        permission = session.execute(
            select(Permission).where(Permission.code == code)
        ).scalar_one_or_none()
        if permission is None:
            localized = BUILTIN_PERMISSION_LOCALIZATION_ZH.get(code)
            permission_name = localized["name"] if localized else code.replace(":", " ").title()
            permission_description = (
                localized["description"] if localized else f"{code} permission"
            )
            permission = Permission(
                name=permission_name,
                code=code,
                description=permission_description,
            )
            session.add(permission)
            created_permissions += 1

    session.flush()

    all_permissions = repo.list_permissions(session)
    all_menus, created_menus = _seed_default_menus(session)

    admin_role = repo.get_role_by_name(session, "admin")
    if admin_role is None:
        admin_role = Role(name="admin", description="System administrator")
        session.add(admin_role)
        session.flush()
    admin_role.permissions = all_permissions
    admin_role.menus = all_menus

    admin_user = repo.get_user_by_username(session, admin_username)
    if admin_user is None:
        admin_user = User(
            username=admin_username,
            email=admin_email,
            password_hash=hash_password(admin_password),
            is_active=True,
        )
        session.add(admin_user)
        session.flush()
    else:
        if admin_user.email != admin_email:
            admin_user.email = admin_email
        if admin_password:
            admin_user.password_hash = hash_password(admin_password)

    if admin_role not in admin_user.roles:
        admin_user.roles.append(admin_role)

    session.commit()

    return {
        "permissions_created": created_permissions,
        "permissions_total": len(all_permissions),
        "menus_created": created_menus,
        "menus_total": len(all_menus),
        "admin_user_id": admin_user.id,
        "admin_role_id": admin_role.id,
    }


def _is_permission_table_missing(error: Exception) -> bool:
    message = str(error).lower()
    missing_signatures = (
        "no such table",
        "doesn't exist",
        "does not exist",
        "unknown table",
    )
    return any(signature in message for signature in missing_signatures)


def sync_builtin_permissions_to_cn() -> dict:
    session = get_session()
    try:
        statement = select(Permission).where(Permission.code.in_(DEFAULT_PERMISSION_CODES))
        permissions = session.execute(statement).scalars().all()
        updated_count = 0
        for permission in permissions:
            localized = BUILTIN_PERMISSION_LOCALIZATION_ZH.get(permission.code)
            if localized is None:
                continue

            changed = False
            if permission.name != localized["name"]:
                permission.name = localized["name"]
                changed = True
            if permission.description != localized["description"]:
                permission.description = localized["description"]
                changed = True

            if changed:
                updated_count += 1

        if updated_count:
            session.commit()

        return {
            "checked": len(permissions),
            "updated": updated_count,
        }
    except SQLAlchemyError as exc:
        session.rollback()
        if _is_permission_table_missing(exc):
            return {
                "checked": 0,
                "updated": 0,
                "skipped": "permissions_table_unavailable",
            }
        return {
            "checked": 0,
            "updated": 0,
            "skipped": "sync_error",
            "error": str(exc),
        }


__all__ = ["seed_rbac", "sync_builtin_permissions_to_cn"]
