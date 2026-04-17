from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Resource

from ...components import ServiceError, fail, ok
from ...components import require_permission
from ...service.permission_service import get_permission, list_permissions
from . import namespace

MAX_SEARCH_TERMS = 5


def parse_terms(raw: str) -> list[str]:
    if not raw:
        return []
    terms = [item.strip() for item in raw.split(",") if item.strip()]
    return terms[:MAX_SEARCH_TERMS]


@namespace.route("")
class PermissionListResource(Resource):
    @jwt_required()
    @require_permission("permission:list")
    def get(self):
        page = request.args.get("page", type=int)
        per_page = request.args.get("per_page", type=int)

        if page is not None:
            page = max(page, 1)
        if per_page is not None:
            per_page = min(max(per_page, 1), 100)

        name_terms = parse_terms(request.args.get("name", "", type=str).strip())
        code_terms = parse_terms(request.args.get("code", "", type=str).strip())
        description_terms = parse_terms(request.args.get("description", "", type=str).strip())

        try:
            return ok(
                list_permissions(
                    page=page,
                    per_page=per_page,
                    name_terms=name_terms,
                    code_terms=code_terms,
                    description_terms=description_terms,
                )
            )
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
