from celery import Celery, Task
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy(session_options={"autoflush": False})
jwt = JWTManager()
bcrypt = Bcrypt()
migrate = Migrate()
celery = Celery(__name__)


def init_celery(app):
    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        task_ignore_result=True,
    )

    class FlaskContextTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = FlaskContextTask