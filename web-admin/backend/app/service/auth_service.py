from __future__ import annotations

from flask_jwt_extended import create_access_token, create_refresh_token, decode_token

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


def _decode_refresh_token(refresh_token: str) -> tuple[str, str]:
    try:
        payload = decode_token(refresh_token)
    except Exception as exc:
        raise ServiceError(ERR_AUTH, "unauthorized", status=401) from exc

    token_type = str(payload.get("type", ""))
    identity = payload.get("sub")
    jti = payload.get("jti")
    if token_type != "refresh" or not identity or not jti:
        raise ServiceError(ERR_AUTH, "unauthorized", status=401)
    return str(identity), str(jti)


def logout(
    access_jti: str | None,
    access_identity: str | int | None,
    refresh_token: str | None,
) -> None:
    if not isinstance(refresh_token, str) or not refresh_token.strip():
        raise ServiceError(ERR_INVALID_REQUEST, "refresh_token is required", status=400)
    if not access_jti or access_identity is None:
        raise ServiceError(ERR_AUTH, "unauthorized", status=401)

    refresh_identity, refresh_jti = _decode_refresh_token(refresh_token.strip())
    if str(access_identity) != refresh_identity:
        raise ServiceError(ERR_AUTH, "unauthorized", status=401)

    session = get_session()
    changed = False
    for jti in {str(access_jti), refresh_jti}:
        if get_token_block(session, jti) is None:
            add_token_block(session, jti)
            changed = True
    if changed:
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
