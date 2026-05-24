"""A股日线数据采集（新浪源 stock_zh_a_daily）"""

from utils.network import ensure_proxy_disabled
ensure_proxy_disabled()

import time
from datetime import date, timedelta
from decimal import Decimal

import akshare as ak
import pandas as pd
from loguru import logger
from sqlalchemy import func, select

from config.settings import settings
from db.models import AssetPool, DailyPrice
from db.session import get_session, remove_session


def _to_sina_symbol(code: str) -> str:
    """000001 → sz000001 / 600519 → sh600519 / 8xxxxx → bj"""
    if code.startswith("6"):
        return f"sh{code}"
    if code.startswith(("0", "3")):
        return f"sz{code}"
    if code.startswith(("4", "8")):
        return f"bj{code}"
    return f"sh{code}"


def _get_latest_date(session, code: str) -> date | None:
    stmt = select(func.max(DailyPrice.trade_date)).where(DailyPrice.code == code)
    return session.execute(stmt).scalar()


def _to_daily_price(row: pd.Series, code: str, name: str) -> DailyPrice:
    turnover_pct = None
    if pd.notna(row.get("turnover")):
        # 新浪 turnover 是小数（0.009377），转成百分比保存
        turnover_pct = Decimal(str(round(float(row["turnover"]) * 100, 4)))
    return DailyPrice(
        code=code,
        name=name,
        asset_type="stock",
        trade_date=pd.to_datetime(row["date"]).date(),
        open=Decimal(str(row["open"])),
        high=Decimal(str(row["high"])),
        low=Decimal(str(row["low"])),
        close=Decimal(str(row["close"])),
        volume=int(row["volume"]),
        amount=Decimal(str(round(float(row["amount"]), 2))),
        turnover=turnover_pct,
    )


def collect_stock(code: str, name: str, start_date: str | None = None) -> int:
    session = get_session()
    try:
        latest = _get_latest_date(session, code)
        if start_date:
            s_date = start_date
        elif latest:
            s_date = (latest + timedelta(days=1)).strftime("%Y%m%d")
        else:
            s_date = settings.DATA_START_DATE

        e_date = date.today().strftime("%Y%m%d")

        if s_date > e_date:
            logger.debug("{} {} 已是最新，跳过", code, name)
            return 0

        symbol = _to_sina_symbol(code)
        logger.info("采集 {} {} ({}) 日线 {} → {}", code, name, symbol, s_date, e_date)

        df = ak.stock_zh_a_daily(
            symbol=symbol, start_date=s_date, end_date=e_date, adjust="qfq"
        )

        if df is None or df.empty:
            logger.info("{} {} 无新数据", code, name)
            return 0

        count = 0
        for _, row in df.iterrows():
            trade_dt = pd.to_datetime(row["date"]).date()
            exists = session.execute(
                select(DailyPrice.id).where(
                    DailyPrice.code == code, DailyPrice.trade_date == trade_dt
                )
            ).scalar()
            if exists:
                continue
            session.add(_to_daily_price(row, code, name))
            count += 1

        session.commit()
        logger.info("{} {} 写入 {} 条", code, name, count)
        return count

    except Exception as e:
        session.rollback()
        logger.error("{} {} 采集失败: {}", code, name, e)
        return 0
    finally:
        remove_session()


def collect_all_stocks(start_date: str | None = None) -> dict:
    session = get_session()
    try:
        assets = session.execute(
            select(AssetPool).where(
                AssetPool.asset_type == "stock", AssetPool.is_active == True
            )
        ).scalars().all()
    finally:
        remove_session()

    total, success, failed = 0, 0, 0
    for asset in assets:
        count = collect_stock(asset.code, asset.name, start_date)
        total += count
        if count > 0:
            success += 1
        else:
            failed += 1
        time.sleep(0.5)

    result = {"total_rows": total, "success": success, "failed": failed}
    logger.info("A股采集完成: {}", result)
    return result
