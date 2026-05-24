"""建表 + 初始化资产池（在 web_admin 库中创建 quant_ 前缀表）"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loguru import logger

from db.base import Base
from db.models import (  # noqa: F401 — 确保所有模型注册到 Base
    AssetPool,
    BacktestResult,
    DailyPrice,
    FactorScore,
    FactorValue,
    MinutePrice,
    TradingSignal,
)
from db.session import engine, get_session, remove_session
from utils.logger import setup_logger

setup_logger()

INITIAL_STOCKS = [
    ("000001", "平安银行", "stock"),
    ("000002", "万科A", "stock"),
    ("000858", "五粮液", "stock"),
    ("600036", "招商银行", "stock"),
    ("600519", "贵州茅台", "stock"),
    ("600900", "长江电力", "stock"),
    ("601318", "中国平安", "stock"),
    ("000333", "美的集团", "stock"),
    ("002594", "比亚迪", "stock"),
    ("300750", "宁德时代", "stock"),
]

INITIAL_ETFS = [
    ("510300", "沪深300ETF", "etf"),
    ("510500", "中证500ETF", "etf"),
    ("510050", "上证50ETF", "etf"),
    ("159915", "创业板ETF", "etf"),
    ("512010", "医药ETF", "etf"),
]


def create_tables():
    logger.info("开始建表...")
    quant_tables = [
        t for t in Base.metadata.tables.values() if t.name.startswith("quant_")
    ]
    Base.metadata.create_all(engine, tables=quant_tables)
    logger.info("建表完成，共 {} 张 quant 表", len(quant_tables))


def seed_asset_pool():
    session = get_session()
    try:
        existing = {a.code for a in session.query(AssetPool).all()}
        added = 0
        for code, name, asset_type in INITIAL_STOCKS + INITIAL_ETFS:
            if code not in existing:
                session.add(AssetPool(code=code, name=name, asset_type=asset_type))
                added += 1
        session.commit()
        logger.info("资产池初始化完成，新增 {} 条", added)
    except Exception:
        session.rollback()
        raise
    finally:
        remove_session()


if __name__ == "__main__":
    create_tables()
    seed_asset_pool()
    logger.info("数据库初始化完成")
