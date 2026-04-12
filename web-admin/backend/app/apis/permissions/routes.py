from flask_jwt_extended import jwt_required
from flask_restx import Resource

from ...decorators import require_permission
from ...conf.extensions import db
from ...database.models import Permission
from ...components.response import fail, ok
from . import namespace


@namespace.route("")
class PermissionListResource(Resource):
    @jwt_required()
    @require_permission("permission:list")
    def get(self):
        items = Permission.query.order_by(Permission.id.asc()).all()
        return ok({"items": [item.to_dict() for item in items], "total": len(items)})


@namespace.route("/<int:permission_id>")
class PermissionResource(Resource):
    @jwt_required()
    @require_permission("permission:read")
    def get(self, permission_id):
        permission = db.session.get(Permission, permission_id)
        if permission is None:
            return fail(1002, "permission not found", status=404)
        return ok(permission.to_dict())
