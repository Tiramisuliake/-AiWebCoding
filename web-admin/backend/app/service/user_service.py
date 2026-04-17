from __future__ import annotations

from ..components.errors import ServiceError
from ..components.pagination import paginate_scalars
from ..components.security import hash_password
from ..components.serializers import user_to_dict
from ..const import ERR_ALREADY_EXISTS, ERR_INVALID_REQUEST, ERR_NOT_FOUND
from ..database.conn import get_session
from ..database.repository import rbac_repository as repo


def list_users(
    page: int,
    per_page: int,
    keyword: str,
    is_active: bool | None,
    username_terms: list[str] | None = None,
    email_terms: list[str] | None = None,
    role_terms: list[str] | None = None,
) -> dict:
    session = get_session()
    pagination = paginate_scalars(
        session,
        repo.build_user_select(
            keyword=keyword,
            is_active=is_active,
            username_terms=username_terms,
            email_terms=email_terms,
            role_terms=role_terms,
        ),
        page=page,
        per_page=per_page,
    )

    return {
        "items": [user_to_dict(item, include_roles=True) for item in pagination["items"]],
        "total": pagination["total"],
        "page": pagination["page"],
        "per_page": pagination["per_page"],
        "pages": pagination["pages"],
    }


def create_user(
    username: str,
    email: str,
    password: str,
    role_ids: list[int] | None,
    is_active: bool,
) -> dict:
    if not username or not email or len(password) < 8:
        raise ServiceError(ERR_INVALID_REQUEST, "invalid request payload", status=400)

    session = get_session()
    if repo.get_user_by_username_or_email(session, username, email):
        raise ServiceError(ERR_ALREADY_EXISTS, "username or email already exists", status=409)

    from ..database.entity.models import User

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        is_active=is_active,
    )
    if role_ids:
        user.roles = repo.list_roles_by_ids(session, role_ids)

    session.add(user)
    session.commit()
    return user_to_dict(user, include_roles=True)


def get_user(user_id: int) -> dict:
    session = get_session()
    user = repo.get_user_by_id(session, user_id)
    if user is None:
        raise ServiceError(ERR_NOT_FOUND, "user not found", status=404)
    return user_to_dict(user, include_roles=True)


def update_user(user_id: int, payload: dict) -> dict:
    session = get_session()
    user = repo.get_user_by_id(session, user_id)
    if user is None:
        raise ServiceError(ERR_NOT_FOUND, "user not found", status=404)

    if "email" in payload:
        email = str(payload.get("email", "")).strip()
        if not email:
            raise ServiceError(ERR_INVALID_REQUEST, "email cannot be empty", status=400)
        duplicate = repo.get_other_user_by_email(session, user.id, email)
        if duplicate:
            raise ServiceError(ERR_ALREADY_EXISTS, "email already exists", status=409)
        user.email = email

    if "is_active" in payload:
        is_active = payload.get("is_active")
        if not isinstance(is_active, bool):
            raise ServiceError(ERR_INVALID_REQUEST, "invalid is_active value", status=400)
        user.is_active = is_active

    if "password" in payload:
        password = str(payload.get("password", ""))
        if len(password) < 8:
            raise ServiceError(
                ERR_INVALID_REQUEST,
                "password must be at least 8 characters",
                status=400,
            )
        user.password_hash = hash_password(password)

    session.commit()
    return user_to_dict(user, include_roles=True)


def delete_user(user_id: int) -> None:
    session = get_session()
    user = repo.get_user_by_id(session, user_id)
    if user is None:
        raise ServiceError(ERR_NOT_FOUND, "user not found", status=404)

    session.delete(user)
    session.commit()


def get_user_roles(user_id: int) -> dict:
    session = get_session()
    user = repo.get_user_by_id(session, user_id)
    if user is None:
        raise ServiceError(ERR_NOT_FOUND, "user not found", status=404)

    return {
        "user_id": user.id,
        "roles": [
            {"id": role.id, "name": role.name, "description": role.description}
            for role in user.roles
        ],
    }


def assign_user_roles(user_id: int, role_ids: list[int]) -> dict:
    session = get_session()
    user = repo.get_user_by_id(session, user_id)
    if user is None:
        raise ServiceError(ERR_NOT_FOUND, "user not found", status=404)

    roles = repo.list_roles_by_ids(session, role_ids) if role_ids else []
    existing_ids = {role.id for role in user.roles}
    for role in roles:
        if role.id not in existing_ids:
            user.roles.append(role)

    session.commit()
    return {"user_id": user.id, "role_ids": [role.id for role in user.roles]}


def remove_user_role(user_id: int, role_id: int) -> None:
    session = get_session()
    user = repo.get_user_by_id(session, user_id)
    role = repo.get_role_by_id(session, role_id)
    if user is None or role is None:
        raise ServiceError(ERR_NOT_FOUND, "resource not found", status=404)

    if role in user.roles:
        user.roles.remove(role)
        session.commit()


__all__ = [
    "assign_user_roles",
    "create_user",
    "delete_user",
    "get_user",
    "get_user_roles",
    "list_users",
    "remove_user_role",
    "update_user",
]
