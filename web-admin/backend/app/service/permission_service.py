from __future__ import annotations

from ..components.errors import ServiceError
from ..components.serializers import permission_to_dict
from ..const import ERR_NOT_FOUND
from ..database.conn import get_session
from ..database.repository import rbac_repository as repo


def list_permissions() -> dict:
    session = get_session()
    items = repo.list_permissions(session)
    return {"items": [permission_to_dict(item) for item in items], "total": len(items)}


def get_permission(permission_id: int) -> dict:
    session = get_session()
    permission = repo.get_permission_by_id(session, permission_id)
    if permission is None:
        raise ServiceError(ERR_NOT_FOUND, "permission not found", status=404)
    return permission_to_dict(permission)


__all__ = ["get_permission", "list_permissions"]
