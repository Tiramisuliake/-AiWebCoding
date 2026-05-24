import json
import os
from pathlib import Path

from dotenv import load_dotenv

_project_root = Path(__file__).resolve().parent.parent
_backend_env = _project_root.parent / "web-admin" / "backend" / ".env"
_quant_env = _project_root / ".env"

if _quant_env.exists():
    load_dotenv(_quant_env, override=True)
elif _backend_env.exists():
    load_dotenv(_backend_env, override=False)


class Settings:
    # 复用 web-admin 的数据库（同库，表名用 quant_ 前缀区分）
    DB_URI: str = os.getenv(
        "QUANT_DB_URI",
        os.getenv("DATABASE_URL", os.getenv("SQLALCHEMY_DATABASE_URI", "")),
    )

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str = os.getenv("LOG_DIR", str(_project_root / "logs"))

    DATA_START_DATE: str = os.getenv("DATA_START_DATE", "20230101")

    MINUTE_PERIODS: list[str] = os.getenv("MINUTE_PERIODS", "5,15,60").split(",")
    MINUTE_RETAIN_DAYS: int = int(os.getenv("MINUTE_RETAIN_DAYS", "60"))

    REALTIME_WS_HOST: str = os.getenv("REALTIME_WS_HOST", "0.0.0.0")
    REALTIME_WS_PORT: int = int(os.getenv("REALTIME_WS_PORT", "8765"))
    REALTIME_POLL_INTERVAL: int = int(os.getenv("REALTIME_POLL_INTERVAL", "3"))

    MULTI_FACTOR_TOP_N: int = int(os.getenv("MULTI_FACTOR_TOP_N", "20"))
    MULTI_FACTOR_WEIGHTS: dict = json.loads(
        os.getenv(
            "MULTI_FACTOR_WEIGHTS",
            '{"return_20d":0.3,"return_60d":0.2,"volatility_20d":0.2,"turnover":0.3}',
        )
    )


settings = Settings()
