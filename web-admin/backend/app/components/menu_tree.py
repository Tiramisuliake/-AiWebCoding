from __future__ import annotations

from collections import defaultdict

from .serializers import menu_to_dict


def _is_admin(user) -> bool:
    return any(role.name == "admin" for role in getattr(user, "roles", []))


def _is_enabled_visible(menu) -> bool:
    return bool(menu.is_enabled and menu.is_visible)


def _has_enabled_visible_ancestors(menu, menu_map: dict[int, object]) -> bool:
    current = menu
    visited: set[int] = set()
    while current.parent_id:
        if current.id in visited:
            return False
        visited.add(current.id)
        parent = menu_map.get(current.parent_id)
        if parent is None:
            return False
        if not _is_enabled_visible(parent):
            return False
        current = parent
    return True


def _collect_parent_ids(menu, menu_map: dict[int, object]) -> set[int]:
    parent_ids: set[int] = set()
    current = menu
    visited: set[int] = set()
    while current.parent_id:
        if current.id in visited:
            break
        visited.add(current.id)
        parent = menu_map.get(current.parent_id)
        if parent is None:
            break
        parent_ids.add(parent.id)
        current = parent
    return parent_ids


def build_menu_tree(menus: list[object]) -> list[dict]:
    if not menus:
        return []

    nodes = {item.id: {**menu_to_dict(item), "children": []} for item in menus}
    roots = []
    children_map: dict[int, list[dict]] = defaultdict(list)

    for item in menus:
        node = nodes[item.id]
        if item.parent_id and item.parent_id in nodes:
            children_map[item.parent_id].append(node)
        else:
            roots.append(node)

    for parent_id, child_nodes in children_map.items():
        child_nodes.sort(key=lambda x: (x["sort"], x["id"]))
        nodes[parent_id]["children"] = child_nodes

    roots.sort(key=lambda x: (x["sort"], x["id"]))
    return roots


def filter_user_menu_tree(user, all_menus: list[object]) -> list[dict]:
    if not all_menus:
        return []

    menu_map = {menu.id: menu for menu in all_menus}

    if _is_admin(user):
        accessible = [
            menu
            for menu in all_menus
            if _is_enabled_visible(menu) and _has_enabled_visible_ancestors(menu, menu_map)
        ]
        return build_menu_tree(accessible)

    role_menus = {menu for role in user.roles for menu in role.menus}
    filtered_role_menus = [
        menu
        for menu in role_menus
        if _is_enabled_visible(menu) and _has_enabled_visible_ancestors(menu, menu_map)
    ]

    allowed_ids = {menu.id for menu in filtered_role_menus}
    for menu in filtered_role_menus:
        allowed_ids.update(_collect_parent_ids(menu, menu_map))

    final_menus = [
        menu
        for menu in all_menus
        if menu.id in allowed_ids
        and _is_enabled_visible(menu)
        and _has_enabled_visible_ancestors(menu, menu_map)
    ]
    return build_menu_tree(final_menus)


__all__ = ["build_menu_tree", "filter_user_menu_tree"]
