from flask import Blueprint
from flask_restx import Api

from .auth import namespace as auth_namespace
from .menus import namespace as menus_namespace
from .permissions import namespace as permissions_namespace
from .roles import namespace as roles_namespace
from .users import namespace as users_namespace

api_blueprint = Blueprint("api", __name__, url_prefix="/api")
api = Api(
    api_blueprint,
    version="0.1.0",
    title="web-admin API",
    description="CRUD admin API with JWT and RBAC",
    doc="/docs",
)

api.add_namespace(auth_namespace, path="/auth")
api.add_namespace(users_namespace, path="/users")
api.add_namespace(roles_namespace, path="/roles")
api.add_namespace(permissions_namespace, path="/permissions")
api.add_namespace(menus_namespace, path="/menus")
