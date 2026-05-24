"""ETF日线数据采集（新浪源 fund_etf_hist_sina）"""

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
    """510300 → sh510300 / 159915 → sz159915"""
    if code.startswith(("5", "6")):
        return f"sh{code}"
    return f"sz{code}"


def _get_latest_date(session, code: str) -> date | None:
    stmt = select(func.max(DailyPrice.trade_date)).where(DailyPrice.code == code)
    return session.execute(stmt).scalar()


def _to_daily_price(row: pd.Series, code: str, name: str) -> DailyPrice:
    return DailyPrice(
        code=code,
        name=name,
        asset_type="etf",
        trade_date=pd.to_datetime(row["date"]).date(),
        open=Decimal(str(row["open"])),
        high=Decimal(str(row["high"])),
        low=Decimal(str(row["low"])),
        close=Decimal(str(row["close"])),
        volume=int(row["volume"]),
        amount=Decimal(str(round(float(row["amount"]), 2))),
        turnover=None,
    )


def collect_etf(code: str, name: str, start_date: str | None = None) -> int:
    session = get_session()
    try:
        latest = _get_latest_date(session, code)
        if start_date:
            s_date = pd.to_datetime(start_date).date()
        elif latest:
            s_date = latest + timedelta(days=1)
        else:
            s_date = pd.to_datetime(settings.DATA_START_DATE).date()

        e_date = date.today()
        if s_date > e_date:
            logger.debug("{} {} 已是最新，跳过", code, name)
            return 0

        symbol = _to_sina_symbol(code)
        logger.info("采集 {} {} ({}) ETF日线 {} → {}", code, name, symbol, s_date, e_date)

        df = ak.fund_etf_hist_sina(symbol=symbol)

        if df is None or df.empty:
            logger.info("{} {} 无新数据", code, name)
            return 0

        # 新浪 ETF 返回全部历史，本地按日期过滤
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df = df[(df["date"] >= s_date) & (df["date"] <= e_date)]

        if df.empty:
            logger.info("{} {} 范围内无新数据", code, name)
            return 0

        count = 0
        for _, row in df.iterrows():
            trade_dt = row["date"]
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


def collect_all_etfs(start_date: str | None = None) -> dict:
    session = get_session()
    try:
        assets = session.execute(
            select(AssetPool).where(
                AssetPool.asset_type == "etf", AssetPool.is_active == True
            )
        ).scalars().all()
    finally:
        remove_session()

    total, success, failed = 0, 0, 0
    for asset in assets:
        count = collect_etf(asset.code, asset.name, start_date)
        total += count
        if count > 0:
            success += 1
        else:
            failed += 1
        time.sleep(0.5)

    result = {"total_rows": total, "success": success, "failed": failed}
    logger.info("ETF采集完成: {}", result)
    return result
