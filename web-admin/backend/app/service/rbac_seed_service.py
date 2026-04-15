from __future__ import annotations

from sqlalchemy import select

from ..components.security import hash_password
from ..const.permissions import DEFAULT_PERMISSION_CODES
from ..database.conn import get_session
from ..database.entity.models import Menu, Permission, Role, User
from ..database.repository import rbac_repository as repo


def _seed_default_menus(session) -> tuple[list[Menu], int]:
    existing = repo.list_all_menus_ordered(session)
    if existing:
        return existing, 0

    dashboard = Menu(
        name="Dashboard",
        route_path="/",
        icon="HomeFilled",
        sort=10,
        is_visible=True,
        is_enabled=True,
    )
    users = Menu(
        name="Users",
        route_path="/users",
        icon="User",
        sort=20,
        is_visible=True,
        is_enabled=True,
        permission_code="user:list",
    )
    rbac_root = Menu(
        name="Permission Management",
        route_path=None,
        icon="Lock",
        sort=30,
        is_visible=True,
        is_enabled=True,
    )

    session.add_all([dashboard, users, rbac_root])
    session.flush()

    roles = Menu(
        name="Roles",
        parent_id=rbac_root.id,
        route_path="/roles",
        icon="UserFilled",
        sort=10,
        is_visible=True,
        is_enabled=True,
        permission_code="role:list",
    )
    permissions = Menu(
        name="Permissions",
        parent_id=rbac_root.id,
        route_path="/permissions",
        icon="Key",
        sort=20,
        is_visible=True,
        is_enabled=True,
        permission_code="permission:list",
    )
    menu_manage = Menu(
        name="Menus",
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
            permission = Permission(
                name=code.replace(":", " ").title(),
                code=code,
                description=f"{code} permission",
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


__all__ = ["seed_rbac"]
