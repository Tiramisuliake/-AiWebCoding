from flask_restx import Namespace

namespace = Namespace("permissions", description="Permission query APIs")

from . import routes  # noqa: E402,F401
