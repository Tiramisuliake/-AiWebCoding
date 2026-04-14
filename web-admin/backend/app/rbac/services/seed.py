from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..constants import DEFAULT_PERMISSION_CODES
from ..models import Menu, Permission, Role, User


def _seed_default_menus(session: Session) -> tuple[list[Menu], int]:
    existing = session.execute(select(Menu).order_by(Menu.id.asc())).scalars().all()
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

    menus = session.execute(select(Menu).order_by(Menu.id.asc())).scalars().all()
    return menus, 6


def seed_rbac(
    session: Session, admin_username: str, admin_email: str, admin_password: str
) -> dict[str, int]:
    created_permissions = 0
    for code in DEFAULT_PERMISSION_CODES:
        permission = session.execute(select(Permission).where(Permission.code == code)).scalar_one_or_none()
        if permission is None:
            permission = Permission(
                name=code.replace(":", " ").title(),
                code=code,
                description=f"{code} permission",
            )
            session.add(permission)
            created_permissions += 1

    session.flush()

    all_permissions = session.execute(select(Permission).order_by(Permission.id.asc())).scalars().all()
    all_menus, created_menus = _seed_default_menus(session)
    admin_role = session.execute(select(Role).where(Role.name == "admin")).scalar_one_or_none()
    if admin_role is None:
        admin_role = Role(name="admin", description="System administrator")
        session.add(admin_role)
        session.flush()
    admin_role.permissions = all_permissions
    admin_role.menus = all_menus

    admin_user = session.execute(
        select(User).where(User.username == admin_username)
    ).scalar_one_or_none()
    if admin_user is None:
        admin_user = User(
            username=admin_username,
            email=admin_email,
            is_active=True,
        )
        admin_user.set_password(admin_password)
        session.add(admin_user)
        session.flush()
    else:
        if admin_user.email != admin_email:
            admin_user.email = admin_email
        if admin_password:
            admin_user.set_password(admin_password)

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
