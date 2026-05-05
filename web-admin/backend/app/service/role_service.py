from __future__ import annotations

from ..components.errors import ServiceError
from ..components.pagination import paginate_scalars
from ..components.serializers import menu_to_dict, role_to_dict
from ..const import ERR_ALREADY_EXISTS, ERR_INVALID_REQUEST, ERR_NOT_FOUND
from ..database.conn import get_session
from ..database.entity.models import Role
from ..database.repository import rbac_repository as repo


def _normalize_requested_ids(raw_ids: list[object]) -> tuple[list[int], list[object]]:
    normalized: list[int] = []
    invalid: list[object] = []
    seen: set[int] = set()

    for raw in raw_ids:
        try:
            value = int(raw)
        except (TypeError, ValueError):
            invalid.append(raw)
            continue

        if value <= 0:
            invalid.append(raw)
            continue

        if value in seen:
            continue
        seen.add(value)
        normalized.append(value)

    return normalized, invalid


def _extract_permission_prefix(permission_code: str | None) -> str | None:
    code = str(permission_code or "").strip()
    if not code:
        return None
    prefix, _separator, _tail = code.partition(":")
    prefix = prefix.strip()
    return prefix or None


def _collect_allowed_permission_ids_by_menus(session, menus: list[object]) -> set[int]:
    prefixes = {
        prefix
        for prefix in (_extract_permission_prefix(menu.permission_code) for menu in menus)
        if prefix
    }
    if not prefixes:
        return set()

    allowed_ids: set[int] = set()
    prefix_starts = tuple(f"{prefix}:" for prefix in prefixes)
    for permission in repo.list_permissions(session):
        code = str(permission.code or "")
        if code.startswith(prefix_starts):
            allowed_ids.add(permission.id)
    return allowed_ids


def list_roles(page: int, per_page: int, name_terms: list[str] | None = None) -> dict:
    session = get_session()
    pagination = paginate_scalars(
        session,
        repo.build_role_select(name_terms=name_terms),
        page=page,
        per_page=per_page,
    )
    return {
        "items": [role_to_dict(role, include_permissions=False) for role in pagination["items"]],
        "total": pagination["total"],
        "page": pagination["page"],
        "per_page": pagination["per_page"],
        "pages": pagination["pages"],
    }


def create_role(name: str, description: str | None, permission_ids: list[int] | None) -> dict:
    if not name:
        raise ServiceError(ERR_INVALID_REQUEST, "name is required", status=400)

    session = get_session()
    if repo.get_role_by_name(session, name):
        raise ServiceError(ERR_ALREADY_EXISTS, "role already exists", status=409)

    role = Role(name=name, description=description)
    if permission_ids:
        role.permissions = repo.list_permissions_by_ids(session, permission_ids)

    session.add(role)
    session.commit()
    return role_to_dict(role, include_permissions=True)


def get_role(role_id: int) -> dict:
    session = get_session()
    role = repo.get_role_by_id(session, role_id)
    if role is None:
        raise ServiceError(ERR_NOT_FOUND, "role not found", status=404)
    return role_to_dict(role, include_permissions=True)


def update_role(role_id: int, payload: dict) -> dict:
    session = get_session()
    role = repo.get_role_by_id(session, role_id)
    if role is None:
        raise ServiceError(ERR_NOT_FOUND, "role not found", status=404)

    if "name" in payload:
        name = str(payload.get("name", "")).strip()
        if not name:
            raise ServiceError(ERR_INVALID_REQUEST, "name cannot be empty", status=400)
        duplicate = repo.get_other_role_by_name(session, role.id, name)
        if duplicate:
            raise ServiceError(ERR_ALREADY_EXISTS, "role name already exists", status=409)
        role.name = name

    if "description" in payload:
        role.description = payload.get("description")

    session.commit()
    return role_to_dict(role, include_permissions=True)


def delete_role(role_id: int) -> None:
    session = get_session()
    role = repo.get_role_by_id(session, role_id)
    if role is None:
        raise ServiceError(ERR_NOT_FOUND, "role not found", status=404)

    if role.users:
        raise ServiceError(
            ERR_INVALID_REQUEST,
            "role is assigned to users and cannot be deleted",
            status=400,
        )

    session.delete(role)
    session.commit()


def get_role_permissions(role_id: int) -> dict:
    session = get_session()
    role = repo.get_role_by_id(session, role_id)
    if role is None:
        raise ServiceError(ERR_NOT_FOUND, "role not found", status=404)

    from ..components.serializers import permission_to_dict

    return {
        "role_id": role.id,
        "permissions": [permission_to_dict(permission) for permission in role.permissions],
    }


def assign_role_permissions(role_id: int, permission_ids: list[int]) -> dict:
    session = get_session()
    role = repo.get_role_by_id(session, role_id)
    if role is None:
        raise ServiceError(ERR_NOT_FOUND, "role not found", status=404)

    normalized_ids, invalid_ids = _normalize_requested_ids(permission_ids)
    permissions = repo.list_permissions_by_ids(session, normalized_ids) if normalized_ids else []
    permission_map = {permission.id: permission for permission in permissions}
    for permission_id in normalized_ids:
        if permission_id not in permission_map:
            invalid_ids.append(permission_id)

    role.permissions = permissions
    session.commit()

    assigned_ids = [permission.id for permission in role.permissions]
    warnings: list[str] = []
    if invalid_ids:
        warnings.append("Some permission_ids are invalid and were ignored.")
    return {
        "role_id": role.id,
        "permission_ids": assigned_ids,
        "applied_ids": assigned_ids,
        "invalid_ids": invalid_ids,
        "warnings": warnings,
    }


def get_role_menus(role_id: int) -> dict:
    session = get_session()
    role = repo.get_role_by_id(session, role_id)
    if role is None:
        raise ServiceError(ERR_NOT_FOUND, "role not found", status=404)

    return {"role_id": role.id, "menus": [menu_to_dict(menu) for menu in role.menus]}


def assign_role_menus(
    role_id: int,
    menu_ids: list[int],
    permission_ids: list[int] | None = None,
) -> dict:
    session = get_session()
    role = repo.get_role_by_id(session, role_id)
    if role is None:
        raise ServiceError(ERR_NOT_FOUND, "role not found", status=404)

    normalized_ids, invalid_ids = _normalize_requested_ids(menu_ids)
    menus = repo.list_menus_by_ids(session, normalized_ids) if normalized_ids else []
    menu_map = {menu.id: menu for menu in menus}
    for menu_id in normalized_ids:
        if menu_id not in menu_map:
            invalid_ids.append(menu_id)

    warnings: list[str] = []
    if invalid_ids:
        warnings.append("Some menu_ids are invalid and were ignored.")

    if permission_ids is None:
        role.menus = menus
        session.commit()

        assigned_ids = [menu.id for menu in role.menus]
        return {
            "role_id": role.id,
            "menu_ids": assigned_ids,
            "applied_ids": assigned_ids,
            "invalid_ids": invalid_ids,
            "warnings": warnings,
        }

    normalized_permission_ids, invalid_permission_ids = _normalize_requested_ids(permission_ids)
    if invalid_permission_ids:
        raise ServiceError(
            ERR_INVALID_REQUEST,
            "permission_ids contains invalid values",
            status=400,
            data={"invalid_permission_ids": invalid_permission_ids},
        )

    permissions = (
        repo.list_permissions_by_ids(session, normalized_permission_ids)
        if normalized_permission_ids
        else []
    )
    permission_map = {permission.id: permission for permission in permissions}
    unknown_permission_ids = [
        permission_id
        for permission_id in normalized_permission_ids
        if permission_id not in permission_map
    ]
    if unknown_permission_ids:
        raise ServiceError(
            ERR_INVALID_REQUEST,
            "permission_ids contains unknown values",
            status=400,
            data={"invalid_permission_ids": unknown_permission_ids},
        )

    allowed_permission_ids = _collect_allowed_permission_ids_by_menus(session, menus)
    out_of_scope_permission_ids = [
        permission_id
        for permission_id in normalized_permission_ids
        if permission_id not in allowed_permission_ids
    ]
    if out_of_scope_permission_ids:
        raise ServiceError(
            ERR_INVALID_REQUEST,
            "permission_ids are out of selected menu scope",
            status=400,
            data={"invalid_permission_ids": out_of_scope_permission_ids},
        )

    role.menus = menus
    role.permissions = permissions
    session.commit()

    assigned_menu_ids = [menu.id for menu in role.menus]
    assigned_permission_ids = [permission.id for permission in role.permissions]
    return {
        "role_id": role.id,
        "menu_ids": assigned_menu_ids,
        "applied_ids": assigned_menu_ids,
        "invalid_ids": invalid_ids,
        "permission_ids": assigned_permission_ids,
        "applied_permission_ids": assigned_permission_ids,
        "warnings": warnings,
    }


__all__ = [
    "assign_role_menus",
    "assign_role_permissions",
    "create_role",
    "delete_role",
    "get_role",
    "get_role_menus",
    "get_role_permissions",
    "list_roles",
    "update_role",
]
