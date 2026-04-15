from __future__ import annotations

from ..components.errors import ServiceError
from ..components.pagination import paginate_scalars
from ..components.serializers import menu_to_dict, role_to_dict
from ..const import ERR_ALREADY_EXISTS, ERR_INVALID_REQUEST, ERR_NOT_FOUND
from ..database.conn import get_session
from ..database.entity.models import Role
from ..database.repository import rbac_repository as repo


def list_roles(page: int, per_page: int) -> dict:
    session = get_session()
    pagination = paginate_scalars(
        session,
        repo.build_role_select(),
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

    role.permissions = repo.list_permissions_by_ids(session, permission_ids) if permission_ids else []
    session.commit()
    return {"role_id": role.id, "permission_ids": [permission.id for permission in role.permissions]}


def get_role_menus(role_id: int) -> dict:
    session = get_session()
    role = repo.get_role_by_id(session, role_id)
    if role is None:
        raise ServiceError(ERR_NOT_FOUND, "role not found", status=404)

    return {"role_id": role.id, "menus": [menu_to_dict(menu) for menu in role.menus]}


def assign_role_menus(role_id: int, menu_ids: list[int]) -> dict:
    session = get_session()
    role = repo.get_role_by_id(session, role_id)
    if role is None:
        raise ServiceError(ERR_NOT_FOUND, "role not found", status=404)

    role.menus = repo.list_menus_by_ids(session, menu_ids) if menu_ids else []
    session.commit()
    return {"role_id": role.id, "menu_ids": [menu.id for menu in role.menus]}


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
