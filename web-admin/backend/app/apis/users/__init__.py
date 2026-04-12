from flask_restx import Namespace

namespace = Namespace("users", description="User management APIs")

from . import routes  # noqa: E402,F401
