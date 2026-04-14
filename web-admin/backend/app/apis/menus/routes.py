from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource
from sqlalchemy import select

from ...components.response import fail, ok
from ...database.session import get_session
from ...decorators import require_permission
from ...rbac.models import Menu, User
from ...rbac.services import get_all_menu_tree, get_user_menu_tree
from . import namespace


def _parse_bool(value, default=None):
    if value in (1, "1", True, "true", "True"):
        return True
    if value in (0, "0", False, "false", "False"):
        return False
    return default


@namespace.route("")
class MenuListResource(Resource):
    @jwt_required()
    @require_permission("menu:list")
    def get(self):
        include_hidden = _parse_bool(request.args.get("include_hidden"), default=True)
        include_disabled = _parse_bool(request.args.get("include_disabled"), default=True)
        session = get_session()
        return ok(
            {
                "items": get_all_menu_tree(
                    session,
                    include_disabled=include_disabled,
                    include_hidden=include_hidden,
                )
            }
        )

    @jwt_required()
    @require_permission("menu:create")
    def post(self):
        payload = request.get_json(silent=True) or {}
        name = str(payload.get("name", "")).strip()
        parent_id = payload.get("parent_id")
        route_path = payload.get("route_path")
        icon = payload.get("icon")
        sort = int(payload.get("sort") or 0)
        is_visible = _parse_bool(payload.get("is_visible"), default=True)
        is_enabled = _parse_bool(payload.get("is_enabled"), default=True)
        permission_code = payload.get("permission_code")

        if not name:
            return fail(1001, "name is required", status=400)

        session = get_session()
        if parent_id is not None:
            parent = session.get(Menu, parent_id)
            if parent is None:
                return fail(1002, "parent menu not found", status=404)

        menu = Menu(
            name=name,
            parent_id=parent_id,
            route_path=str(route_path).strip() if route_path else None,
            icon=str(icon).strip() if icon else None,
            sort=sort,
            is_visible=is_visible,
            is_enabled=is_enabled,
            permission_code=str(permission_code).strip() if permission_code else None,
        )
        session.add(menu)
        session.commit()
        return ok(menu.to_dict(), status=201)


@namespace.route("/my-tree")
class MyMenuTreeResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        try:
            user_pk = int(user_id)
        except (TypeError, ValueError):
            return fail(2001, "unauthorized", status=401)

        session = get_session()
        user = session.get(User, user_pk)
        if user is None:
            return fail(2001, "unauthorized", status=401)
        return ok({"items": get_user_menu_tree(session, user)})


@namespace.route("/<int:menu_id>")
class MenuResource(Resource):
    @jwt_required()
    @require_permission("menu:read")
    def get(self, menu_id):
        session = get_session()
        menu = session.get(Menu, menu_id)
        if menu is None:
            return fail(1002, "menu not found", status=404)
        return ok(menu.to_dict())

    @jwt_required()
    @require_permission("menu:update")
    def put(self, menu_id):
        session = get_session()
        menu = session.get(Menu, menu_id)
        if menu is None:
            return fail(1002, "menu not found", status=404)

        payload = request.get_json(silent=True) or {}

        if "name" in payload:
            name = str(payload.get("name", "")).strip()
            if not name:
                return fail(1001, "name cannot be empty", status=400)
            menu.name = name

        if "parent_id" in payload:
            parent_id = payload.get("parent_id")
            if parent_id == menu.id:
                return fail(1001, "menu parent cannot be itself", status=400)
            if parent_id is not None:
                parent = session.get(Menu, parent_id)
                if parent is None:
                    return fail(1002, "parent menu not found", status=404)
            menu.parent_id = parent_id

        if "route_path" in payload:
            route_path = payload.get("route_path")
            menu.route_path = str(route_path).strip() if route_path else None
        if "icon" in payload:
            icon = payload.get("icon")
            menu.icon = str(icon).strip() if icon else None
        if "sort" in payload:
            menu.sort = int(payload.get("sort") or 0)
        if "is_visible" in payload:
            menu.is_visible = _parse_bool(payload.get("is_visible"), default=True)
        if "is_enabled" in payload:
            menu.is_enabled = _parse_bool(payload.get("is_enabled"), default=True)
        if "permission_code" in payload:
            permission_code = payload.get("permission_code")
            menu.permission_code = str(permission_code).strip() if permission_code else None

        session.commit()
        return ok(menu.to_dict())

    @jwt_required()
    @require_permission("menu:delete")
    def delete(self, menu_id):
        session = get_session()
        menu = session.get(Menu, menu_id)
        if menu is None:
            return fail(1002, "menu not found", status=404)

        has_children = (
            session.execute(select(Menu.id).where(Menu.parent_id == menu.id))
            .scalar_one_or_none()
            is not None
        )
        if has_children:
            return fail(1001, "menu has child menus and cannot be deleted", status=400)

        session.delete(menu)
        session.commit()
        return ok(data=None)
