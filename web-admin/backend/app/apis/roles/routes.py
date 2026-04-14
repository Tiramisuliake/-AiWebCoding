from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Resource
from sqlalchemy import select

from ...components.response import fail, ok
from ...database.pagination import paginate_scalars
from ...database.session import get_session
from ...decorators import require_permission
from ...rbac.models import Menu, Permission, Role
from . import namespace


@namespace.route("")
class RoleListResource(Resource):
    @jwt_required()
    @require_permission("role:list")
    def get(self):
        page = max(request.args.get("page", 1, type=int), 1)
        per_page = min(max(request.args.get("per_page", 20, type=int), 1), 100)

        session = get_session()
        pagination = paginate_scalars(
            session,
            select(Role).order_by(Role.id.asc()),
            page=page,
            per_page=per_page,
        )
        return ok(
            {
                "items": [
                    role.to_dict(include_permissions=False) for role in pagination["items"]
                ],
                "total": pagination["total"],
                "page": pagination["page"],
                "per_page": pagination["per_page"],
                "pages": pagination["pages"],
            }
        )

    @jwt_required()
    @require_permission("role:create")
    def post(self):
        payload = request.get_json(silent=True) or {}
        name = str(payload.get("name", "")).strip()
        description = payload.get("description")
        permission_ids = payload.get("permission_ids", [])

        if not name:
            return fail(1001, "name is required", status=400)

        session = get_session()
        existing = session.execute(select(Role.id).where(Role.name == name)).scalar_one_or_none()
        if existing:
            return fail(1003, "role already exists", status=409)

        role = Role(name=name, description=description)
        if isinstance(permission_ids, list) and permission_ids:
            role.permissions = session.execute(
                select(Permission).where(Permission.id.in_(permission_ids))
            ).scalars().all()
        session.add(role)
        session.commit()
        return ok(role.to_dict(include_permissions=True), status=201)


@namespace.route("/<int:role_id>")
class RoleResource(Resource):
    @jwt_required()
    @require_permission("role:read")
    def get(self, role_id):
        session = get_session()
        role = session.get(Role, role_id)
        if role is None:
            return fail(1002, "role not found", status=404)
        return ok(role.to_dict(include_permissions=True))

    @jwt_required()
    @require_permission("role:update")
    def put(self, role_id):
        session = get_session()
        role = session.get(Role, role_id)
        if role is None:
            return fail(1002, "role not found", status=404)

        payload = request.get_json(silent=True) or {}
        if "name" in payload:
            name = str(payload.get("name", "")).strip()
            if not name:
                return fail(1001, "name cannot be empty", status=400)
            duplicate = session.execute(
                select(Role.id).where(Role.name == name, Role.id != role.id)
            ).scalar_one_or_none()
            if duplicate:
                return fail(1003, "role name already exists", status=409)
            role.name = name
        if "description" in payload:
            role.description = payload.get("description")

        session.commit()
        return ok(role.to_dict(include_permissions=True))

    @jwt_required()
    @require_permission("role:delete")
    def delete(self, role_id):
        session = get_session()
        role = session.get(Role, role_id)
        if role is None:
            return fail(1002, "role not found", status=404)
        if role.users:
            return fail(1001, "role is assigned to users and cannot be deleted", status=400)
        session.delete(role)
        session.commit()
        return ok(data=None)


@namespace.route("/<int:role_id>/permissions")
class RolePermissionResource(Resource):
    @jwt_required()
    @require_permission("role:read")
    def get(self, role_id):
        session = get_session()
        role = session.get(Role, role_id)
        if role is None:
            return fail(1002, "role not found", status=404)
        return ok(
            {
                "role_id": role.id,
                "permissions": [permission.to_dict() for permission in role.permissions],
            }
        )

    @jwt_required()
    @require_permission("role:assign_permission")
    def post(self, role_id):
        session = get_session()
        role = session.get(Role, role_id)
        if role is None:
            return fail(1002, "role not found", status=404)

        payload = request.get_json(silent=True) or {}
        permission_ids = payload.get("permission_ids")
        if not isinstance(permission_ids, list):
            return fail(1001, "permission_ids must be a list", status=400)

        role.permissions = (
            session.execute(select(Permission).where(Permission.id.in_(permission_ids))).scalars().all()
            if permission_ids
            else []
        )
        session.commit()
        return ok(
            {
                "role_id": role.id,
                "permission_ids": [permission.id for permission in role.permissions],
            }
        )


@namespace.route("/<int:role_id>/menus")
class RoleMenuResource(Resource):
    @jwt_required()
    @require_permission("role:read")
    def get(self, role_id):
        session = get_session()
        role = session.get(Role, role_id)
        if role is None:
            return fail(1002, "role not found", status=404)
        return ok({"role_id": role.id, "menus": [menu.to_dict() for menu in role.menus]})

    @jwt_required()
    @require_permission("role:assign_menu")
    def post(self, role_id):
        session = get_session()
        role = session.get(Role, role_id)
        if role is None:
            return fail(1002, "role not found", status=404)

        payload = request.get_json(silent=True) or {}
        menu_ids = payload.get("menu_ids")
        if not isinstance(menu_ids, list):
            return fail(1001, "menu_ids must be a list", status=400)

        role.menus = session.execute(select(Menu).where(Menu.id.in_(menu_ids))).scalars().all() if menu_ids else []
        session.commit()
        return ok({"role_id": role.id, "menu_ids": [menu.id for menu in role.menus]})
