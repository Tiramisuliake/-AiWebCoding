from flask_jwt_extended import jwt_required
from flask_restx import Resource

from ...components import ServiceError, fail, ok
from ...components import require_permission
from ...service.permission_service import get_permission, list_permissions
from . import namespace


@namespace.route("")
class PermissionListResource(Resource):
    @jwt_required()
    @require_permission("permission:list")
    def get(self):
        try:
            return ok(list_permissions())
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)


@namespace.route("/<int:permission_id>")
class PermissionResource(Resource):
    @jwt_required()
    @require_permission("permission:read")
    def get(self, permission_id):
        try:
            return ok(get_permission(permission_id))
        except ServiceError as exc:
            return fail(exc.code, exc.msg, status=exc.status, data=exc.data)

