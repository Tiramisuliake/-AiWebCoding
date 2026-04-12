from app import create_app
from app.conf.extensions import celery
from app.tasks import sample  # noqa: F401

flask_app = create_app()

__all__ = ("celery", "flask_app")
