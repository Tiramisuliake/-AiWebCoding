from flask import request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from flask_restx import Resource
from sqlalchemy import select

from ...components.response import fail, ok
from ...database.models import TokenBlocklist
from ...database.session import get_session
from ...rbac.models import User
from . import namespace


@namespace.route("/login")
class LoginResource(Resource):
    def post(self):
        payload = request.get_json(silent=True) or {}
        username = str(payload.get("username", "")).strip()
        password = str(payload.get("password", ""))

        if not username or not password:
            return fail(1001, "username and password are required", status=400)

        session = get_session()
        user = session.execute(select(User).where(User.username == username)).scalar_one_or_none()
        if user is None or not user.is_active or not user.check_password(password):
            return fail(2001, "invalid credentials", status=401)

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        return ok(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "roles": [role.name for role in user.roles],
                },
            }
        )


@namespace.route("/logout")
class LogoutResource(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt().get("jti")
        if not jti:
            return ok(data=None)

        session = get_session()
        exists = session.execute(
            select(TokenBlocklist.id).where(TokenBlocklist.jti == jti)
        ).scalar_one_or_none()
        if exists is None:
            session.add(TokenBlocklist(jti=jti))
            session.commit()
        return ok(data=None)


@namespace.route("/refresh")
class RefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        user_id = get_jwt_identity()
        try:
            user_pk = int(user_id)
        except (TypeError, ValueError):
            return fail(2001, "unauthorized", status=401)

        session = get_session()
        user = session.get(User, user_pk)
        if user is None:
            return fail(2001, "unauthorized", status=401)
        return ok({"access_token": create_access_token(identity=str(user.id))})
