from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Resource

from ...components import ServiceError, fail, ok
from ...components import require_permission
from ...service.user_service import (
    assign_user_roles,
    create_user,
    delete_user,
    get_user,
    get_user_roles,
    list_users,
    remove_user_role,
    update_user,
)
from ...utils.parsers import parse_bool
from . import namespace


@namespace.route("")
class UserListResource(Resource):
    @jwt_required()
    @require_permission("user:list")
    def get(self):
        page = max(request.args.get("page", 1, type=int), 1)
        per_page = min(max(request.args.get("per_page", 20, type=int), 1), 100)
        keyword = request.args.get("keyword", "", type=str).strip()
        is_active = parse_bool(request.args.get("is_active"), default=None)

        try:
            return ok(list_users(page=page, per_page=per_page, keyword=keyword, is_active=is_active))
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)

    @jwt_required()
    @require_permission("user:create")
    def post(self):
        payload = request.get_json(silent=True) or {}
        username = str(payload.get("username", "")).strip()
        email = str(payload.get("email", "")).strip()
        password = str(payload.get("password", ""))
        role_ids = payload.get("role_ids", [])
        is_active = parse_bool(payload.get("is_active"), default=True)

        try:
            data = create_user(
                username=username,
                email=email,
                password=password,
                role_ids=role_ids if isinstance(role_ids, list) else [],
                is_active=is_active,
            )
            return ok(data, status=201)
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)


@namespace.route("/<int:user_id>")
class UserResource(Resource):
    @jwt_required()
    @require_permission("user:read")
    def get(self, user_id):
        try:
            return ok(get_user(user_id))
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)

    @jwt_required()
    @require_permission("user:update")
    def put(self, user_id):
        payload = request.get_json(silent=True) or {}
        if "is_active" in payload:
            payload["is_active"] = parse_bool(payload.get("is_active"), default=None)

        try:
            return ok(update_user(user_id, payload))
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)

    @jwt_required()
    @require_permission("user:delete")
    def delete(self, user_id):
        try:
            delete_user(user_id)
            return ok(data=None)
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)


@namespace.route("/<int:user_id>/roles")
class UserRolesResource(Resource):
    @jwt_required()
    @require_permission("user:read")
    def get(self, user_id):
        try:
            return ok(get_user_roles(user_id))
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)

    @jwt_required()
    @require_permission("user:assign_role")
    def post(self, user_id):
        payload = request.get_json(silent=True) or {}
        role_ids = payload.get("role_ids")
        if not isinstance(role_ids, list):
            return fail(1001, "role_ids must be a list", status=400)

        try:
            return ok(assign_user_roles(user_id, role_ids))
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)


@namespace.route("/<int:user_id>/roles/<int:role_id>")
class UserRoleDeleteResource(Resource):
    @jwt_required()
    @require_permission("user:assign_role")
    def delete(self, user_id, role_id):
        try:
            remove_user_role(user_id, role_id)
            return ok(data=None)
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)


