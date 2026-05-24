"""A股日线数据采集"""

import time
from datetime import date, datetime, timedelta
from decimal import Decimal

import akshare as ak
import pandas as pd
from loguru import logger
from sqlalchemy import select, func

from db.models import AssetPool, DailyPrice
from db.session import get_session, remove_session
from config.settings import settings


def _get_latest_date(session, code: str) -> date | None:
    stmt = select(func.max(DailyPrice.trade_date)).where(DailyPrice.code == code)
    return session.execute(stmt).scalar()


def _to_daily_price(row: pd.Series, code: str, name: str) -> DailyPrice:
    return DailyPrice(
        code=code,
        name=name,
        asset_type="stock",
        trade_date=pd.to_datetime(row["日期"]).date(),
        open=Decimal(str(row["开盘"])),
        high=Decimal(str(row["最高"])),
        low=Decimal(str(row["最低"])),
        close=Decimal(str(row["收盘"])),
        volume=int(row["成交量"]),
        amount=Decimal(str(row["成交额"])),
        turnover=Decimal(str(row["换手率"])) if pd.notna(row.get("换手率")) else None,
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

        logger.info("采集 {} {} 日线 {} → {}", code, name, s_date, e_date)
        df = ak.stock_zh_a_hist(
            symbol=code, period="daily",
            start_date=s_date, end_date=e_date, adjust="qfq",
        )

        if df is None or df.empty:
            logger.info("{} {} 无新数据", code, name)
            return 0

        count = 0
        for _, row in df.iterrows():
            trade_dt = pd.to_datetime(row["日期"]).date()
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
        if count >= 0:
            success += 1
        else:
            failed += 1
        time.sleep(1)

    result = {"total_rows": total, "success": success, "failed": failed}
    logger.info("A股采集完成: {}", result)
    return result
