from functools import wraps

from flask_jwt_extended import get_jwt_identity

from .conf.extensions import db
from .database.models import User
from .components.response import fail


def require_permission(permission_code):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id) if user_id else None
            if user is None:
                return fail(2001, "unauthorized", status=401)
            if not user.has_permission(permission_code):
                return fail(2002, "permission denied", status=403)
            return fn(*args, **kwargs)

        return wrapped

    return decorator