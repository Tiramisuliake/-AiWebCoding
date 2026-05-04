import os

from flask import Flask
from flask_cors import CORS

from .apis import api_blueprint
from .components.response import fail, ok
from .conf.config import CONFIG_MAP, apply_env_config
from .conf.extensions import bcrypt, init_celery, jwt
from .database.conn import init_engine, remove_session
from .service.auth_service import is_token_revoked
from .service.rbac_seed_service import sync_builtin_permissions_to_cn


def create_app(config_name=None, config_overrides=None):
    app = Flask(__name__)

    resolved_name = config_name or os.getenv("FLASK_ENV", "development")
    config_class = CONFIG_MAP.get(resolved_name, CONFIG_MAP["development"])
    app.config.from_object(config_class)

    if config_overrides:
        app.config.update(config_overrides)

    apply_env_config(app)

    init_engine(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"].split(","))
    init_celery(app)

    if app.config.get("PERMISSION_CN_SYNC_ON_STARTUP", True):
        try:
            sync_result = sync_builtin_permissions_to_cn()
            if sync_result.get("updated"):
                app.logger.info(
                    "Builtin permission localization synced on startup, updated: %s",
                    sync_result["updated"],
                )
            if sync_result.get("skipped") == "permissions_table_unavailable":
                app.logger.info(
                    "Builtin permission localization skipped because table is unavailable."
                )
            if sync_result.get("skipped") == "sync_error":
                app.logger.warning(
                    "Builtin permission localization failed but app startup continues: %s",
                    sync_result.get("error", "unknown error"),
                )
        except Exception as exc:  # pragma: no cover - startup guard
            app.logger.exception(
                "Unexpected error during builtin permission localization sync: %s",
                exc,
            )

    @jwt.token_in_blocklist_loader
    def on_token_in_blocklist(_jwt_header, jwt_payload):
        return is_token_revoked(jwt_payload.get("jti"))

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
        remove_session()

    @app.get("/health")
    def health():
        return ok({"status": "ok"})

    app.register_blueprint(api_blueprint)
    return app
