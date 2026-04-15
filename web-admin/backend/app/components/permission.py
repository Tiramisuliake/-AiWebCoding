from functools import wraps

from flask_jwt_extended import get_jwt_identity

from .response import fail


def require_permission(permission_code):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            user_id = get_jwt_identity()
            if not user_id:
                return fail(2001, "unauthorized", status=401)

            try:
                user_pk = int(user_id)
            except (TypeError, ValueError):
                return fail(2001, "unauthorized", status=401)

            from ..service.authz_service import user_has_permission

            if not user_has_permission(user_pk, permission_code):
                return fail(2002, "permission denied", status=403)
            return fn(*args, **kwargs)

        return wrapped

    return decorator


__all__ = ["require_permission"]
