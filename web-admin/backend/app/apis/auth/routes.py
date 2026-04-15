from flask import request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_restx import Resource

from ...components import ServiceError, fail, ok
from ...service.auth_service import login, logout, refresh_access_token
from . import namespace


@namespace.route("/login")
class LoginResource(Resource):
    def post(self):
        payload = request.get_json(silent=True) or {}
        username = str(payload.get("username", "")).strip()
        password = str(payload.get("password", ""))

        try:
            return ok(login(username=username, password=password))
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)


@namespace.route("/logout")
class LogoutResource(Resource):
    @jwt_required()
    def post(self):
        try:
            logout(get_jwt().get("jti"))
            return ok(data=None)
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)


@namespace.route("/refresh")
class RefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        user_id = get_jwt_identity()
        try:
            user_pk = int(user_id)
        except (TypeError, ValueError):
            return fail(2001, "unauthorized", status=401)

        try:
            return ok(refresh_access_token(user_pk))
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)
