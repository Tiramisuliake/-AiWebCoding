from __future__ import annotations

from ..components.errors import ServiceError
from ..components.pagination import paginate_scalars
from ..components.serializers import permission_to_dict
from ..const import ERR_NOT_FOUND
from ..database.conn import get_session
from ..database.repository import rbac_repository as repo


def list_permissions(
    page: int | None = None,
    per_page: int | None = None,
    name_terms: list[str] | None = None,
    code_terms: list[str] | None = None,
    description_terms: list[str] | None = None,
) -> dict:
    session = get_session()
    statement = repo.build_permission_select(
        name_terms=name_terms,
        code_terms=code_terms,
        description_terms=description_terms,
    )

    if page is None or per_page is None:
        items = session.execute(statement).scalars().all()
        total = len(items)
        return {
            "items": [permission_to_dict(item) for item in items],
            "total": total,
            "page": 1,
            "per_page": total or 1,
            "pages": 1 if total else 0,
        }

    pagination = paginate_scalars(
        session,
        statement,
        page=page,
        per_page=per_page,
    )
    return {
        "items": [permission_to_dict(item) for item in pagination["items"]],
        "total": pagination["total"],
        "page": pagination["page"],
        "per_page": pagination["per_page"],
        "pages": pagination["pages"],
    }


def get_permission(permission_id: int) -> dict:
    session = get_session()
    permission = repo.get_permission_by_id(session, permission_id)
    if permission is None:
        raise ServiceError(ERR_NOT_FOUND, "permission not found", status=404)
    return permission_to_dict(permission)


__all__ = ["get_permission", "list_permissions"]
