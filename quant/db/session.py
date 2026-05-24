"""
quant 独立 session 管理。

脚本独立运行时：用 settings.DB_URI 创建自己的 engine。
web-admin 进程内：仍用自己的 engine（指向同库），避免与 Flask scoped_session 冲突。
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from config.settings import settings

if not settings.DB_URI:
    raise RuntimeError(
        "数据库未配置。请在 quant/.env 设置 QUANT_DB_URI，"
        "或确保 web-admin/backend/.env 中有 DATABASE_URL。"
    )

engine = create_engine(
    settings.DB_URI,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    echo=False,
)

SessionFactory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
ScopedSession = scoped_session(SessionFactory)


def get_session():
    return ScopedSession()


def remove_session():
    ScopedSession.remove()
