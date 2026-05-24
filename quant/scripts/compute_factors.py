"""因子计算入口：读取日线数据，计算所有注册因子，写入 factor_value"""

import argparse
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from loguru import logger
from sqlalchemy import select

from config.settings import settings
from db.models import AssetPool, DailyPrice, FactorValue
from db.session import get_session, remove_session
from factor.registry import list_factors, get_factor_func
import factor.basic_factors  # noqa: F401 — 触发 @register
import factor.technical_factors  # noqa: F401 — 注册技术指标因子
from utils.logger import setup_logger

setup_logger()


def compute_for_asset(code: str, name: str) -> int:
    session = get_session()
    try:
        rows = session.execute(
            select(DailyPrice)
            .where(DailyPrice.code == code)
            .order_by(DailyPrice.trade_date)
        ).scalars().all()

        if not rows:
            logger.info("{} {} 无日线数据，跳过", code, name)
            return 0

        df = pd.DataFrame([{
            "trade_date": r.trade_date,
            "open": float(r.open),
            "high": float(r.high),
            "low": float(r.low),
            "close": float(r.close),
            "volume": r.volume,
            "amount": float(r.amount),
        } for r in rows])

        count = 0
        for factor_name in list_factors():
            calc_func = get_factor_func(factor_name)
            values = calc_func(df)

            for i, val in values.items():
                if pd.isna(val):
                    continue
                trade_dt = df.at[i, "trade_date"]

                exists = session.execute(
                    select(FactorValue.id).where(
                        FactorValue.code == code,
                        FactorValue.trade_date == trade_dt,
                        FactorValue.factor_name == factor_name,
                    )
                ).scalar()
                if exists:
                    continue

                session.add(FactorValue(
                    code=code,
                    trade_date=trade_dt,
                    factor_name=factor_name,
                    value=Decimal(str(round(val, 6))),
                ))
                count += 1

        session.commit()
        logger.info("{} {} 写入 {} 条因子", code, name, count)
        return count

    except Exception as e:
        session.rollback()
        logger.error("{} {} 因子计算失败: {}", code, name, e)
        return 0
    finally:
        remove_session()


def main():
    parser = argparse.ArgumentParser(description="计算因子值")
    parser.add_argument("--code", help="指定资产代码（默认全部）")
    args = parser.parse_args()

    logger.info("===== 因子计算开始 =====")
    logger.info("注册因子: {}", list_factors())

    session = get_session()
    try:
        query = select(AssetPool).where(AssetPool.is_active == True)
        if args.code:
            query = query.where(AssetPool.code == args.code)
        assets = session.execute(query).scalars().all()
    finally:
        remove_session()

    total = 0
    for asset in assets:
        total += compute_for_asset(asset.code, asset.name)

    logger.info("===== 因子计算完成，共写入 {} 条 =====", total)


if __name__ == "__main__":
    main()
