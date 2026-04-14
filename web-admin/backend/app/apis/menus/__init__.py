from flask_restx import Namespace

namespace = Namespace("menus", description="Menu management APIs")

from . import routes  # noqa: E402,F401

