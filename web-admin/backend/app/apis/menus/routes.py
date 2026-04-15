from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource

from ...components import ServiceError, fail, ok
from ...components import require_permission
from ...service.menu_service import (
    create_menu,
    delete_menu,
    get_menu,
    get_user_menu_tree,
    list_menu_tree,
    update_menu,
)
from ...utils.parsers import parse_bool
from . import namespace


@namespace.route("")
class MenuListResource(Resource):
    @jwt_required()
    @require_permission("menu:list")
    def get(self):
        include_hidden = parse_bool(request.args.get("include_hidden"), default=True)
        include_disabled = parse_bool(request.args.get("include_disabled"), default=True)
        name = request.args.get("name", "", type=str).strip()

        try:
            return ok(
                list_menu_tree(
                    include_hidden=include_hidden,
                    include_disabled=include_disabled,
                    name=name,
                )
            )
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)

    @jwt_required()
    @require_permission("menu:create")
    def post(self):
        payload = request.get_json(silent=True) or {}

        name = str(payload.get("name", "")).strip()
        parent_id = payload.get("parent_id")
        route_path = payload.get("route_path")
        icon = payload.get("icon")
        sort = int(payload.get("sort") or 0)
        is_visible = parse_bool(payload.get("is_visible"), default=True)
        is_enabled = parse_bool(payload.get("is_enabled"), default=True)
        permission_code = payload.get("permission_code")

        try:
            data = create_menu(
                name=name,
                parent_id=parent_id,
                route_path=str(route_path).strip() if route_path else None,
                icon=str(icon).strip() if icon else None,
                sort=sort,
                is_visible=is_visible,
                is_enabled=is_enabled,
                permission_code=str(permission_code).strip() if permission_code else None,
            )
            return ok(data, status=201)
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)


@namespace.route("/my-tree")
class MyMenuTreeResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        try:
            user_pk = int(user_id)
        except (TypeError, ValueError):
            return fail(2001, "unauthorized", status=401)

        try:
            return ok(get_user_menu_tree(user_pk))
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)


@namespace.route("/<int:menu_id>")
class MenuResource(Resource):
    @jwt_required()
    @require_permission("menu:read")
    def get(self, menu_id):
        try:
            return ok(get_menu(menu_id))
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)

    @jwt_required()
    @require_permission("menu:update")
    def put(self, menu_id):
        payload = request.get_json(silent=True) or {}
        if "is_visible" in payload:
            payload["is_visible"] = parse_bool(payload.get("is_visible"), default=None)
        if "is_enabled" in payload:
            payload["is_enabled"] = parse_bool(payload.get("is_enabled"), default=None)

        try:
            return ok(update_menu(menu_id, payload))
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)

    @jwt_required()
    @require_permission("menu:delete")
    def delete(self, menu_id):
        try:
            delete_menu(menu_id)
            return ok(data=None)
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)


