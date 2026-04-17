from __future__ import annotations

from ..components.errors import ServiceError
from ..components.menu_tree import build_menu_tree, filter_user_menu_tree
from ..components.serializers import menu_to_dict
from ..const import ERR_AUTH, ERR_INVALID_REQUEST, ERR_NOT_FOUND
from ..database.conn import get_session
from ..database.entity.models import Menu
from ..database.repository import rbac_repository as repo


def _collect_parent_ids(menu: Menu, menu_map: dict[int, Menu]) -> set[int]:
    parent_ids: set[int] = set()
    current = menu
    while current.parent_id:
        parent = menu_map.get(current.parent_id)
        if parent is None:
            break
        parent_ids.add(parent.id)
        current = parent
    return parent_ids


def _filter_menus_by_name_with_ancestors(menus: list[Menu], name_terms: list[str] | None) -> list[Menu]:
    name_terms = [term.lower() for term in (name_terms or []) if term]
    if not name_terms:
        return menus

    menu_map = {menu.id: menu for menu in menus}
    matched_ids = {
        menu.id
        for menu in menus
        if any(term in (menu.name or "").lower() for term in name_terms)
    }

    allowed_ids = set(matched_ids)
    for menu_id in matched_ids:
        menu = menu_map.get(menu_id)
        if menu:
            allowed_ids.update(_collect_parent_ids(menu, menu_map))

    return [menu for menu in menus if menu.id in allowed_ids]


def list_menu_tree(
    include_hidden: bool = True,
    include_disabled: bool = True,
    name_terms: list[str] | None = None,
) -> dict:
    session = get_session()
    menus = repo.list_menus(
        session,
        include_disabled=include_disabled,
        include_hidden=include_hidden,
    )
    menus = _filter_menus_by_name_with_ancestors(menus, name_terms)
    return {"items": build_menu_tree(menus)}


def create_menu(
    name: str,
    parent_id: int | None,
    route_path: str | None,
    icon: str | None,
    sort: int,
    is_visible: bool,
    is_enabled: bool,
    permission_code: str | None,
) -> dict:
    if not name:
        raise ServiceError(ERR_INVALID_REQUEST, "name is required", status=400)

    session = get_session()
    if parent_id is not None:
        parent = repo.get_menu_by_id(session, parent_id)
        if parent is None:
            raise ServiceError(ERR_NOT_FOUND, "parent menu not found", status=404)

    menu = Menu(
        name=name,
        parent_id=parent_id,
        route_path=route_path,
        icon=icon,
        sort=sort,
        is_visible=is_visible,
        is_enabled=is_enabled,
        permission_code=permission_code,
    )
    session.add(menu)
    session.commit()
    return menu_to_dict(menu)


def get_user_menu_tree(user_id: int) -> dict:
    session = get_session()
    user = repo.get_user_by_id(session, user_id)
    if user is None:
        raise ServiceError(ERR_AUTH, "unauthorized", status=401)

    all_menus = repo.list_all_menus_ordered(session)
    return {"items": filter_user_menu_tree(user, all_menus)}


def get_menu(menu_id: int) -> dict:
    session = get_session()
    menu = repo.get_menu_by_id(session, menu_id)
    if menu is None:
        raise ServiceError(ERR_NOT_FOUND, "menu not found", status=404)
    return menu_to_dict(menu)


def update_menu(menu_id: int, payload: dict) -> dict:
    session = get_session()
    menu = repo.get_menu_by_id(session, menu_id)
    if menu is None:
        raise ServiceError(ERR_NOT_FOUND, "menu not found", status=404)

    if "name" in payload:
        name = str(payload.get("name", "")).strip()
        if not name:
            raise ServiceError(ERR_INVALID_REQUEST, "name cannot be empty", status=400)
        menu.name = name

    if "parent_id" in payload:
        parent_id = payload.get("parent_id")
        if parent_id == menu.id:
            raise ServiceError(ERR_INVALID_REQUEST, "menu parent cannot be itself", status=400)
        if parent_id is not None:
            parent = repo.get_menu_by_id(session, parent_id)
            if parent is None:
                raise ServiceError(ERR_NOT_FOUND, "parent menu not found", status=404)
        menu.parent_id = parent_id

    if "route_path" in payload:
        route_path = payload.get("route_path")
        menu.route_path = str(route_path).strip() if route_path else None
    if "icon" in payload:
        icon = payload.get("icon")
        menu.icon = str(icon).strip() if icon else None
    if "sort" in payload:
        menu.sort = int(payload.get("sort") or 0)
    if "is_visible" in payload:
        is_visible = payload.get("is_visible")
        if not isinstance(is_visible, bool):
            raise ServiceError(ERR_INVALID_REQUEST, "invalid is_visible value", status=400)
        menu.is_visible = is_visible
    if "is_enabled" in payload:
        is_enabled = payload.get("is_enabled")
        if not isinstance(is_enabled, bool):
            raise ServiceError(ERR_INVALID_REQUEST, "invalid is_enabled value", status=400)
        menu.is_enabled = is_enabled
    if "permission_code" in payload:
        permission_code = payload.get("permission_code")
        menu.permission_code = str(permission_code).strip() if permission_code else None

    session.commit()
    return menu_to_dict(menu)


def delete_menu(menu_id: int) -> None:
    session = get_session()
    menu = repo.get_menu_by_id(session, menu_id)
    if menu is None:
        raise ServiceError(ERR_NOT_FOUND, "menu not found", status=404)

    if repo.menu_has_children(session, menu.id):
        raise ServiceError(
            ERR_INVALID_REQUEST,
            "menu has child menus and cannot be deleted",
            status=400,
        )

    session.delete(menu)
    session.commit()


__all__ = [
    "create_menu",
    "delete_menu",
    "get_menu",
    "get_user_menu_tree",
    "list_menu_tree",
    "update_menu",
]

