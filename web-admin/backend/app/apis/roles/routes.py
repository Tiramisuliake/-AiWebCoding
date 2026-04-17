from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Resource

from ...components import ServiceError, fail, ok
from ...components import require_permission
from ...service.role_service import (
    assign_role_menus,
    assign_role_permissions,
    create_role,
    delete_role,
    get_role,
    get_role_menus,
    get_role_permissions,
    list_roles,
    update_role,
)
from . import namespace

MAX_SEARCH_TERMS = 5


def parse_terms(raw: str) -> list[str]:
    if not raw:
        return []
    terms = [item.strip() for item in raw.split(",") if item.strip()]
    return terms[:MAX_SEARCH_TERMS]


@namespace.route("")
class RoleListResource(Resource):
    @jwt_required()
    @require_permission("role:list")
    def get(self):
        page = max(request.args.get("page", 1, type=int), 1)
        per_page = min(max(request.args.get("per_page", 20, type=int), 1), 100)
        name_terms = parse_terms(request.args.get("name", "", type=str).strip())

        try:
            return ok(list_roles(page=page, per_page=per_page, name_terms=name_terms))
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)

    @jwt_required()
    @require_permission("role:create")
    def post(self):
        payload = request.get_json(silent=True) or {}
        name = str(payload.get("name", "")).strip()
        description = payload.get("description")
        permission_ids = payload.get("permission_ids", [])

        if not isinstance(permission_ids, list):
            return fail(1001, "permission_ids must be a list", status=400)

        try:
            data = create_role(name=name, description=description, permission_ids=permission_ids)
            return ok(data, status=201)
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)


@namespace.route("/<int:role_id>")
class RoleResource(Resource):
    @jwt_required()
    @require_permission("role:read")
    def get(self, role_id):
        try:
            return ok(get_role(role_id))
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)

    @jwt_required()
    @require_permission("role:update")
    def put(self, role_id):
        payload = request.get_json(silent=True) or {}
        try:
            return ok(update_role(role_id, payload))
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)

    @jwt_required()
    @require_permission("role:delete")
    def delete(self, role_id):
        try:
            delete_role(role_id)
            return ok(data=None)
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)


@namespace.route("/<int:role_id>/permissions")
class RolePermissionResource(Resource):
    @jwt_required()
    @require_permission("role:read")
    def get(self, role_id):
        try:
            return ok(get_role_permissions(role_id))
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)

    @jwt_required()
    @require_permission("role:assign_permission")
    def post(self, role_id):
        payload = request.get_json(silent=True) or {}
        permission_ids = payload.get("permission_ids")
        if not isinstance(permission_ids, list):
            return fail(1001, "permission_ids must be a list", status=400)

        try:
            return ok(assign_role_permissions(role_id, permission_ids))
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)


@namespace.route("/<int:role_id>/menus")
class RoleMenuResource(Resource):
    @jwt_required()
    @require_permission("role:read")
    def get(self, role_id):
        try:
            return ok(get_role_menus(role_id))
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)

    @jwt_required()
    @require_permission("role:assign_menu")
    def post(self, role_id):
        payload = request.get_json(silent=True) or {}
        menu_ids = payload.get("menu_ids")
        if not isinstance(menu_ids, list):
            return fail(1001, "menu_ids must be a list", status=400)

        try:
            return ok(assign_role_menus(role_id, menu_ids))
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)

