"""
quant 模块共享 web-admin 的 DeclarativeBase。

- 在 web-admin Flask 进程内：通过 web-admin 的 entity 导入 Base，quant 表自动注册
- 在独立脚本运行时：使用本地 Base，仅建/操作 quant_ 开头的表
"""

import sys
from pathlib import Path

_backend_app = Path(__file__).resolve().parent.parent.parent / "web-admin" / "backend"

try:
    if str(_backend_app) not in sys.path:
        sys.path.insert(0, str(_backend_app))
    from app.database.entity.base import Base
except ImportError:
    from sqlalchemy.orm import DeclarativeBase

    class Base(DeclarativeBase):
        pass
