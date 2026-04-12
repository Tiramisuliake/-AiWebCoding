from sqlalchemy import or_

from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Resource

from ...decorators import require_permission
from ...conf.extensions import db
from ...database.models import Role, User
from ...components.response import fail, ok
from . import namespace


def _parse_bool(value):
    if value in (1, "1", True, "true", "True"):
        return True
    if value in (0, "0", False, "false", "False"):
        return False
    return None


@namespace.route("")
class UserListResource(Resource):
    @jwt_required()
    @require_permission("user:list")
    def get(self):
        page = max(request.args.get("page", 1, type=int), 1)
        per_page = min(max(request.args.get("per_page", 20, type=int), 1), 100)
        keyword = request.args.get("keyword", "", type=str).strip()
        is_active = _parse_bool(request.args.get("is_active"))

        query = User.query
        if keyword:
            like_keyword = f"%{keyword}%"
            query = query.filter(
                or_(User.username.like(like_keyword), User.email.like(like_keyword))
            )
        if is_active is not None:
            query = query.filter(User.is_active.is_(is_active))

        pagination = query.order_by(User.id.asc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return ok(
            {
                "items": [item.to_dict(include_roles=True) for item in pagination.items],
                "total": pagination.total,
                "page": pagination.page,
                "per_page": pagination.per_page,
                "pages": pagination.pages,
            }
        )

    @jwt_required()
    @require_permission("user:create")
    def post(self):
        payload = request.get_json(silent=True) or {}
        username = str(payload.get("username", "")).strip()
        email = str(payload.get("email", "")).strip()
        password = str(payload.get("password", ""))
        role_ids = payload.get("role_ids", [])
        is_active = _parse_bool(payload.get("is_active"))
        is_active = True if is_active is None else is_active

        if not username or not email or len(password) < 8:
            return fail(1001, "invalid request payload", status=400)

        if User.query.filter((User.username == username) | (User.email == email)).first():
            return fail(1003, "username or email already exists", status=409)

        user = User(username=username, email=email, is_active=is_active)
        user.set_password(password)

        if isinstance(role_ids, list) and role_ids:
            roles = Role.query.filter(Role.id.in_(role_ids)).all()
            user.roles = roles

        db.session.add(user)
        db.session.commit()
        return ok(user.to_dict(include_roles=True), status=201)


@namespace.route("/<int:user_id>")
class UserResource(Resource):
    @jwt_required()
    @require_permission("user:read")
    def get(self, user_id):
        user = db.session.get(User, user_id)
        if user is None:
            return fail(1002, "user not found", status=404)
        return ok(user.to_dict(include_roles=True))

    @jwt_required()
    @require_permission("user:update")
    def put(self, user_id):
        user = db.session.get(User, user_id)
        if user is None:
            return fail(1002, "user not found", status=404)

        payload = request.get_json(silent=True) or {}
        if "email" in payload:
            email = str(payload.get("email", "")).strip()
            if not email:
                return fail(1001, "email cannot be empty", status=400)
            duplicate = User.query.filter(User.email == email, User.id != user.id).first()
            if duplicate:
                return fail(1003, "email already exists", status=409)
            user.email = email

        if "is_active" in payload:
            parsed = _parse_bool(payload.get("is_active"))
            if parsed is None:
                return fail(1001, "invalid is_active value", status=400)
            user.is_active = parsed

        if "password" in payload:
            password = str(payload.get("password", ""))
            if len(password) < 8:
                return fail(1001, "password must be at least 8 characters", status=400)
            user.set_password(password)

        db.session.commit()
        return ok(user.to_dict(include_roles=True))

    @jwt_required()
    @require_permission("user:delete")
    def delete(self, user_id):
        user = db.session.get(User, user_id)
        if user is None:
            return fail(1002, "user not found", status=404)
        db.session.delete(user)
        db.session.commit()
        return ok(data=None)


@namespace.route("/<int:user_id>/roles")
class UserRolesResource(Resource):
    @jwt_required()
    @require_permission("user:read")
    def get(self, user_id):
        user = db.session.get(User, user_id)
        if user is None:
            return fail(1002, "user not found", status=404)
        return ok(
            {
                "user_id": user.id,
                "roles": [
                    {"id": role.id, "name": role.name, "description": role.description}
                    for role in user.roles
                ],
            }
        )

    @jwt_required()
    @require_permission("user:assign_role")
    def post(self, user_id):
        user = db.session.get(User, user_id)
        if user is None:
            return fail(1002, "user not found", status=404)

        payload = request.get_json(silent=True) or {}
        role_ids = payload.get("role_ids")
        if not isinstance(role_ids, list):
            return fail(1001, "role_ids must be a list", status=400)

        roles = Role.query.filter(Role.id.in_(role_ids)).all() if role_ids else []
        existing_ids = {role.id for role in user.roles}
        for role in roles:
            if role.id not in existing_ids:
                user.roles.append(role)

        db.session.commit()
        return ok({"user_id": user.id, "role_ids": [role.id for role in user.roles]})


@namespace.route("/<int:user_id>/roles/<int:role_id>")
class UserRoleDeleteResource(Resource):
    @jwt_required()
    @require_permission("user:assign_role")
    def delete(self, user_id, role_id):
        user = db.session.get(User, user_id)
        role = db.session.get(Role, role_id)
        if user is None or role is None:
            return fail(1002, "resource not found", status=404)
        if role in user.roles:
            user.roles.remove(role)
            db.session.commit()
        return ok(data=None)
