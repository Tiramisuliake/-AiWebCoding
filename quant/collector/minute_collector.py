"""分钟级数据采集（1m/5m/15m/30m/60m）"""

from utils.network import ensure_proxy_disabled
ensure_proxy_disabled()

import time
from datetime import date, datetime, timedelta
from decimal import Decimal

import akshare as ak
import pandas as pd
from loguru import logger
from sqlalchemy import delete, func, select

from config.settings import settings
from db.models import AssetPool, MinutePrice
from db.session import get_session, remove_session


def _get_latest_time(session, code: str, period: str) -> datetime | None:
    stmt = select(func.max(MinutePrice.trade_time)).where(
        MinutePrice.code == code, MinutePrice.period == period
    )
    return session.execute(stmt).scalar()


def _to_minute_price(row: pd.Series, code: str, asset_type: str, period: str) -> MinutePrice:
    ts = pd.to_datetime(row["时间"])
    return MinutePrice(
        code=code,
        asset_type=asset_type,
        trade_date=ts.date(),
        trade_time=ts.to_pydatetime(),
        period=period,
        open=Decimal(str(row["开盘"])),
        high=Decimal(str(row["最高"])),
        low=Decimal(str(row["最低"])),
        close=Decimal(str(row["收盘"])),
        volume=int(row["成交量"]),
        amount=Decimal(str(row["成交额"])),
    )


def collect_minute(code: str, name: str, asset_type: str, period: str) -> int:
    session = get_session()
    try:
        latest = _get_latest_time(session, code, period)
        if latest:
            s_date = latest.strftime("%Y-%m-%d %H:%M:%S")
        else:
            days_back = max(settings.MINUTE_RETAIN_DAYS, 30)
            s_date = (date.today() - timedelta(days=days_back)).strftime("%Y-%m-%d") + " 09:00:00"

        e_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logger.info("采集 {} {} {}m K线 {} → {}", code, name, period, s_date, e_date)

        if asset_type == "stock":
            df = ak.stock_zh_a_hist_min_em(
                symbol=code, period=period,
                start_date=s_date, end_date=e_date, adjust="qfq",
            )
        else:
            df = ak.fund_etf_hist_min_em(
                symbol=code, period=period,
                start_date=s_date, end_date=e_date, adjust="qfq",
            )

        if df is None or df.empty:
            logger.info("{} {} {}m 无新数据", code, name, period)
            return 0

        count = 0
        for _, row in df.iterrows():
            ts = pd.to_datetime(row["时间"]).to_pydatetime()
            exists = session.execute(
                select(MinutePrice.id).where(
                    MinutePrice.code == code,
                    MinutePrice.trade_time == ts,
                    MinutePrice.period == period,
                )
            ).scalar()
            if exists:
                continue
            session.add(_to_minute_price(row, code, asset_type, period))
            count += 1

        session.commit()
        logger.info("{} {} {}m 写入 {} 条", code, name, period, count)
        return count

    except Exception as e:
        session.rollback()
        logger.error("{} {} {}m 采集失败: {}", code, name, period, e)
        return 0
    finally:
        remove_session()


def cleanup_expired():
    """清理超过保留天数的分钟数据"""
    session = get_session()
    try:
        cutoff = date.today() - timedelta(days=settings.MINUTE_RETAIN_DAYS)
        result = session.execute(
            delete(MinutePrice).where(MinutePrice.trade_date < cutoff)
        )
        session.commit()
        logger.info("清理 {} 之前的分钟数据，删除 {} 条", cutoff, result.rowcount)
    except Exception as e:
        session.rollback()
        logger.error("清理过期数据失败: {}", e)
    finally:
        remove_session()


def collect_all_minutes(periods: list[str] | None = None) -> dict:
    if periods is None:
        periods = settings.MINUTE_PERIODS

    session = get_session()
    try:
        assets = session.execute(
            select(AssetPool).where(AssetPool.is_active == True)
        ).scalars().all()
    finally:
        remove_session()

    total = 0
    for asset in assets:
        for period in periods:
            total += collect_minute(asset.code, asset.name, asset.asset_type, period)
            time.sleep(1)

    cleanup_expired()

    result = {"total_rows": total, "asset_count": len(assets), "periods": periods}
    logger.info("分钟级采集完成: {}", result)
    return result
