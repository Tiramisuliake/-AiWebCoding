from flask import request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from flask_restx import Resource

from ...conf.extensions import db
from ...database.models import TokenBlocklist, User
from ...components.response import fail, ok
from . import namespace


@namespace.route("/login")
class LoginResource(Resource):
    def post(self):
        payload = request.get_json(silent=True) or {}
        username = str(payload.get("username", "")).strip()
        password = str(payload.get("password", ""))

        if not username or not password:
            return fail(1001, "username and password are required", status=400)

        user = User.query.filter_by(username=username).first()
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
        if jti and TokenBlocklist.query.filter_by(jti=jti).first() is None:
            db.session.add(TokenBlocklist(jti=jti))
            db.session.commit()
        return ok(data=None)


@namespace.route("/refresh")
class RefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        user_id = get_jwt_identity()
        user = db.session.get(User, int(user_id)) if user_id else None
        if user is None:
            return fail(2001, "unauthorized", status=401)
        return ok({"access_token": create_access_token(identity=str(user.id))})
