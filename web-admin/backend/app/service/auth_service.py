from __future__ import annotations

from flask_jwt_extended import create_access_token, create_refresh_token

from ..components.errors import ServiceError
from ..components.security import verify_password
from ..const import ERR_AUTH, ERR_INVALID_REQUEST
from ..database.conn import get_session
from ..database.repository.auth_repository import add_token_block, get_token_block
from ..database.repository.rbac_repository import get_user_by_id, get_user_by_username


def login(username: str, password: str) -> dict:
    if not username or not password:
        raise ServiceError(ERR_INVALID_REQUEST, "username and password are required", status=400)

    session = get_session()
    user = get_user_by_username(session, username)
    if user is None or not user.is_active or not verify_password(user.password_hash, password):
        raise ServiceError(ERR_AUTH, "invalid credentials", status=401)

    return {
        "access_token": create_access_token(identity=str(user.id)),
        "refresh_token": create_refresh_token(identity=str(user.id)),
        "user": {
            "id": user.id,
            "username": user.username,
            "roles": [role.name for role in user.roles],
        },
    }


def logout(jti: str | None) -> None:
    if not jti:
        return

    session = get_session()
    if get_token_block(session, jti) is None:
        add_token_block(session, jti)
        session.commit()


def refresh_access_token(user_id: int) -> dict:
    session = get_session()
    user = get_user_by_id(session, user_id)
    if user is None:
        raise ServiceError(ERR_AUTH, "unauthorized", status=401)
    return {"access_token": create_access_token(identity=str(user.id))}


def is_token_revoked(jti: str | None) -> bool:
    if not jti:
        return True

    session = get_session()
    return get_token_block(session, jti) is not None


__all__ = ["is_token_revoked", "login", "logout", "refresh_access_token"]

