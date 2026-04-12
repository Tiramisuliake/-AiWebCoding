from flask_restx import Namespace

namespace = Namespace("auth", description="Authentication APIs")

from . import routes  # noqa: E402,F401
