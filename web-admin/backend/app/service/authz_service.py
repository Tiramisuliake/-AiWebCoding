from __future__ import annotations

from ..components.security import user_has_permission as _user_has_permission
from ..database.conn import get_session
from ..database.repository.rbac_repository import get_user_by_id


def user_has_permission(user_id: int, permission_code: str) -> bool:
    session = get_session()
    user = get_user_by_id(session, user_id)
    if user is None:
        return False
    return _user_has_permission(user, permission_code)


__all__ = ["user_has_permission"]
