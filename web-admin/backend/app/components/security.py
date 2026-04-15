from __future__ import annotations

from ..conf.extensions import bcrypt


def hash_password(plain_password: str) -> str:
    return bcrypt.generate_password_hash(plain_password).decode("utf-8")


def verify_password(password_hash: str, plain_password: str) -> bool:
    try:
        return bcrypt.check_password_hash(password_hash, plain_password)
    except (TypeError, ValueError):
        return False


def user_has_permission(user, permission_code: str) -> bool:
    if any(role.name == "admin" for role in user.roles):
        return True
    permission_codes = {
        permission.code for role in user.roles for permission in role.permissions
    }
    return permission_code in permission_codes


__all__ = ["hash_password", "verify_password", "user_has_permission"]
