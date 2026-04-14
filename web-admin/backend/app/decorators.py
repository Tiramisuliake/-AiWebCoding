from functools import wraps

from flask_jwt_extended import get_jwt_identity

from .components.response import fail
from .database.session import get_session
from .rbac.models import User


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

            session = get_session()
            user = session.get(User, user_pk)
            if user is None:
                return fail(2001, "unauthorized", status=401)
            if not user.has_permission(permission_code):
                return fail(2002, "permission denied", status=403)
            return fn(*args, **kwargs)

        return wrapped

    return decorator
