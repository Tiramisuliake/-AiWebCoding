import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


def _env_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name, default):
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"Invalid integer for {name}: {raw}") from exc


def _pick_profiled_env(key, profile):
    profile_key = f"{key}__{str(profile).upper()}"
    value = os.getenv(profile_key)
    if value is not None and value != "":
        return value
    return os.getenv(key)


class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JSON_AS_ASCII = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    JWT_SECRET_KEY = "test-secret-key-for-jwt-at-least-32"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    CELERY_BROKER_URL = "memory://localhost/"
    CELERY_RESULT_BACKEND = "cache+memory://"


class ProductionConfig(BaseConfig):
    DEBUG = False


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def _load_env_from_files():
    project_root = Path(__file__).resolve().parents[2]
    env_file = project_root / ".env"

    if env_file.exists():
        load_dotenv(env_file, override=False)
        return

    env_example_file = project_root / ".env.example"
    if os.getenv("FLASK_ENV", "development") != "production" and env_example_file.exists():
        load_dotenv(env_example_file, override=False)


def apply_env_config(app):
    _load_env_from_files()

    app.config.setdefault("APP_PROFILE", os.getenv("APP_PROFILE", os.getenv("FLASK_ENV", "development")))
    profile = app.config["APP_PROFILE"]

    app.config.setdefault("JWT_SECRET_KEY", _pick_profiled_env("JWT_SECRET_KEY", profile))
    app.config.setdefault(
        "SQLALCHEMY_DATABASE_URI",
        _pick_profiled_env("DATABASE_URL", profile)
        or _pick_profiled_env("SQLALCHEMY_DATABASE_URI", profile),
    )
    app.config.setdefault(
        "CELERY_BROKER_URL", os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    )
    app.config.setdefault(
        "CELERY_RESULT_BACKEND",
        os.getenv("CELERY_RESULT_BACKEND", app.config["CELERY_BROKER_URL"]),
    )
    app.config.setdefault("CORS_ORIGINS", os.getenv("CORS_ORIGINS", "*"))

    # Database engine options, aligned with create_engine/sessionmaker mode.
    app.config.setdefault(
        "SQLALCHEMY_ECHO",
        _env_bool(
            _pick_profiled_env("SQLALCHEMY_ECHO", profile)
            or _pick_profiled_env("DATABASE_SHOW_SQL", profile),
            default=False,
        ),
    )
    app.config.setdefault(
        "SQLALCHEMY_POOL_PRE_PING",
        _env_bool(_pick_profiled_env("DB_POOL_PRE_PING", profile), default=True),
    )
    app.config.setdefault("DB_POOL_SIZE", _env_int("DB_POOL_SIZE", 5))
    app.config.setdefault("DB_MAX_OVERFLOW", _env_int("DB_MAX_OVERFLOW", 8))
    app.config.setdefault("DB_POOL_TIMEOUT", _env_int("DB_POOL_TIMEOUT", 30))
    app.config.setdefault("DB_POOL_RECYCLE", _env_int("DB_POOL_RECYCLE", 3600))

    if app.config.get("TESTING"):
        return

    required_keys = ("JWT_SECRET_KEY", "SQLALCHEMY_DATABASE_URI")
    missing = [key for key in required_keys if not app.config.get(key)]
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(
            f"Missing required configuration values: {joined}. "
            "Set them through environment variables or backend/.env "
            "(DB supports DATABASE_URL or SQLALCHEMY_DATABASE_URI)."
        )
