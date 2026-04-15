from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from ..entity.models import Menu, Permission, Role, User


def build_user_select(
    keyword: str = "",
    is_active: bool | None = None,
    username: str = "",
    email: str = "",
    role: str = "",
) -> Select:
    statement = select(User)
    joined_roles = False

    if role:
        joined_roles = True
        statement = statement.outerjoin(User.roles)
        statement = statement.where(Role.name.like(f"%{role}%"))

    if username:
        statement = statement.where(User.username.like(f"%{username}%"))

    if email:
        statement = statement.where(User.email.like(f"%{email}%"))

    if keyword:
        like_keyword = f"%{keyword}%"
        statement = statement.where(
            or_(User.username.like(like_keyword), User.email.like(like_keyword))
        )
    if is_active is not None:
        statement = statement.where(User.is_active.is_(is_active))

    if joined_roles:
        statement = statement.distinct()

    return statement.order_by(User.id.asc())


def get_user_by_id(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def get_user_by_username(session: Session, username: str) -> User | None:
    return session.execute(select(User).where(User.username == username)).scalar_one_or_none()


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.execute(select(User).where(User.email == email)).scalar_one_or_none()


def get_user_by_username_or_email(session: Session, username: str, email: str) -> User | None:
    return session.execute(
        select(User).where((User.username == username) | (User.email == email))
    ).scalar_one_or_none()


def get_other_user_by_email(session: Session, user_id: int, email: str) -> User | None:
    return session.execute(select(User).where(User.email == email, User.id != user_id)).scalar_one_or_none()


def list_roles_by_ids(session: Session, role_ids: list[int]) -> list[Role]:
    if not role_ids:
        return []
    return session.execute(select(Role).where(Role.id.in_(role_ids))).scalars().all()


def get_role_by_id(session: Session, role_id: int) -> Role | None:
    return session.get(Role, role_id)


def get_role_by_name(session: Session, name: str) -> Role | None:
    return session.execute(select(Role).where(Role.name == name)).scalar_one_or_none()


def get_other_role_by_name(session: Session, role_id: int, name: str) -> Role | None:
    return session.execute(select(Role).where(Role.name == name, Role.id != role_id)).scalar_one_or_none()


def build_role_select(name: str = "") -> Select:
    statement = select(Role)
    if name:
        statement = statement.where(Role.name.like(f"%{name}%"))
    return statement.order_by(Role.id.asc())


def build_permission_select(name: str = "", code: str = "", description: str = "") -> Select:
    statement = select(Permission)
    if name:
        statement = statement.where(Permission.name.like(f"%{name}%"))
    if code:
        statement = statement.where(Permission.code.like(f"%{code}%"))
    if description:
        statement = statement.where(Permission.description.like(f"%{description}%"))
    return statement.order_by(Permission.id.asc())


def list_permissions(session: Session) -> list[Permission]:
    return session.execute(select(Permission).order_by(Permission.id.asc())).scalars().all()


def get_permission_by_id(session: Session, permission_id: int) -> Permission | None:
    return session.get(Permission, permission_id)


def list_permissions_by_ids(session: Session, permission_ids: list[int]) -> list[Permission]:
    if not permission_ids:
        return []
    return session.execute(select(Permission).where(Permission.id.in_(permission_ids))).scalars().all()


def list_menus(session: Session, include_disabled: bool = True, include_hidden: bool = True) -> list[Menu]:
    statement = select(Menu)
    if not include_disabled:
        statement = statement.where(Menu.is_enabled.is_(True))
    if not include_hidden:
        statement = statement.where(Menu.is_visible.is_(True))
    return session.execute(statement.order_by(Menu.sort.asc(), Menu.id.asc())).scalars().all()


def list_all_menus_ordered(session: Session) -> list[Menu]:
    return session.execute(select(Menu).order_by(Menu.sort.asc(), Menu.id.asc())).scalars().all()


def get_menu_by_id(session: Session, menu_id: int) -> Menu | None:
    return session.get(Menu, menu_id)


def get_menu_by_route_path(session: Session, route_path: str) -> Menu | None:
    return session.execute(select(Menu).where(Menu.route_path == route_path)).scalar_one_or_none()


def list_menus_by_ids(session: Session, menu_ids: list[int]) -> list[Menu]:
    if not menu_ids:
        return []
    return session.execute(select(Menu).where(Menu.id.in_(menu_ids))).scalars().all()


def menu_has_children(session: Session, menu_id: int) -> bool:
    return session.execute(select(Menu.id).where(Menu.parent_id == menu_id)).scalar_one_or_none() is not None


__all__ = [
    "build_role_select",
    "build_permission_select",
    "build_user_select",
    "get_menu_by_id",
    "get_menu_by_route_path",
    "get_other_role_by_name",
    "get_other_user_by_email",
    "get_permission_by_id",
    "get_role_by_id",
    "get_role_by_name",
    "get_user_by_email",
    "get_user_by_id",
    "get_user_by_username",
    "get_user_by_username_or_email",
    "list_all_menus_ordered",
    "list_menus",
    "list_menus_by_ids",
    "list_permissions",
    "list_permissions_by_ids",
    "list_roles_by_ids",
    "menu_has_children",
]
