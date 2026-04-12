import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


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

    app.config.setdefault("JWT_SECRET_KEY", os.getenv("JWT_SECRET_KEY"))
    app.config.setdefault(
        "SQLALCHEMY_DATABASE_URI",
        os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URI"),
    )
    app.config.setdefault(
        "CELERY_BROKER_URL", os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    )
    app.config.setdefault(
        "CELERY_RESULT_BACKEND",
        os.getenv("CELERY_RESULT_BACKEND", app.config["CELERY_BROKER_URL"]),
    )
    app.config.setdefault("CORS_ORIGINS", os.getenv("CORS_ORIGINS", "*"))

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