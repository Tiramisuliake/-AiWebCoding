from flask_restx import Namespace

namespace = Namespace("roles", description="Role management APIs")

from . import routes  # noqa: E402,F401
