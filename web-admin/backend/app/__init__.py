import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import get_jwt

from .apis import api_blueprint
from .components.response import fail, ok
from .conf.config import CONFIG_MAP, apply_env_config
from .conf.extensions import bcrypt, db, init_celery, jwt, migrate


def create_app(config_name=None, config_overrides=None):
    app = Flask(__name__)

    resolved_name = config_name or os.getenv("FLASK_ENV", "development")
    config_class = CONFIG_MAP.get(resolved_name, CONFIG_MAP["development"])
    app.config.from_object(config_class)

    if config_overrides:
        app.config.update(config_overrides)

    apply_env_config(app)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"].split(","))
    init_celery(app)

    from .database.models import TokenBlocklist  # Imported after db init to avoid circular imports.

    @jwt.token_in_blocklist_loader
    def is_token_revoked(_jwt_header, jwt_payload):
        jti = jwt_payload.get("jti")
        return (
            db.session.query(TokenBlocklist.id).filter_by(jti=jti).first() is not None
            if jti
            else True
        )

    @jwt.unauthorized_loader
    def on_missing_token(_err):
        return fail(2001, "token missing", status=401)

    @jwt.invalid_token_loader
    def on_invalid_token(_err):
        return fail(2001, "token invalid", status=401)

    @jwt.expired_token_loader
    def on_expired_token(_jwt_header, _jwt_payload):
        return fail(2001, "token expired", status=401)

    @jwt.revoked_token_loader
    def on_revoked_token(_jwt_header, _jwt_payload):
        return fail(2001, "token revoked", status=401)

    @app.errorhandler(404)
    def not_found(_error):
        return fail(1002, "resource not found", status=404)

    @app.errorhandler(500)
    def server_error(_error):
        return fail(5001, "internal server error", status=500)

    @app.teardown_appcontext
    def cleanup_session(_error=None):
        db.session.remove()

    @app.get("/health")
    def health():
        return ok({"status": "ok"})

    app.register_blueprint(api_blueprint)
    return app