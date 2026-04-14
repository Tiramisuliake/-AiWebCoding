from __future__ import annotations

from contextlib import contextmanager
from typing import Any

from flask import current_app, has_app_context
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

from .base import Base

_ENGINE: Engine | None = None
_ENGINE_URI: str | None = None
_SESSION_FACTORY = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False)
)


def _to_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _build_engine_options(uri: str, config: dict[str, Any]) -> dict[str, Any]:
    options: dict[str, Any] = {
        "echo": _to_bool(config.get("SQLALCHEMY_ECHO"), default=False),
        "pool_pre_ping": _to_bool(config.get("SQLALCHEMY_POOL_PRE_PING"), default=True),
    }

    if uri.startswith("sqlite"):
        options["connect_args"] = {"check_same_thread": False}
        if ":memory:" in uri:
            options["poolclass"] = StaticPool
        return options

    options["pool_size"] = int(config.get("DB_POOL_SIZE", 5))
    options["max_overflow"] = int(config.get("DB_MAX_OVERFLOW", 8))
    options["pool_timeout"] = int(config.get("DB_POOL_TIMEOUT", 30))
    options["pool_recycle"] = int(config.get("DB_POOL_RECYCLE", 3600))
    return options


def init_engine(app) -> Engine:
    global _ENGINE
    global _ENGINE_URI

    uri = app.config.get("SQLALCHEMY_DATABASE_URI")
    if not uri:
        raise RuntimeError("SQLALCHEMY_DATABASE_URI is required.")

    if _ENGINE is not None and _ENGINE_URI == uri:
        return _ENGINE

    if _ENGINE is not None:
        _SESSION_FACTORY.remove()
        _ENGINE.dispose()

    _ENGINE = create_engine(uri, **_build_engine_options(uri, app.config))
    _ENGINE_URI = uri
    _SESSION_FACTORY.configure(bind=_ENGINE)
    return _ENGINE


def get_engine() -> Engine:
    if _ENGINE is None:
        if not has_app_context():
            raise RuntimeError("Database engine is not initialized.")
        init_engine(current_app._get_current_object())

    if _ENGINE is None:
        raise RuntimeError("Database engine initialization failed.")
    return _ENGINE


def get_session() -> Session:
    get_engine()
    return _SESSION_FACTORY()


def remove_session() -> None:
    _SESSION_FACTORY.remove()


def create_all() -> None:
    from .models import TokenBlocklist  # noqa: F401
    from ..rbac.models import Menu, Permission, Role, User  # noqa: F401

    Base.metadata.create_all(bind=get_engine())


def drop_all() -> None:
    Base.metadata.drop_all(bind=get_engine())


@contextmanager
def session_scope() -> Session:
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise


__all__ = [
    "create_all",
    "drop_all",
    "get_engine",
    "get_session",
    "init_engine",
    "remove_session",
    "session_scope",
]

