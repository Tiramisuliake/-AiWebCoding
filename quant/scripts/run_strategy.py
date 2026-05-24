"""策略信号生成入口：读取日线+因子，运行 MA 交叉策略，写入 trading_signal"""

import argparse
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from loguru import logger
from sqlalchemy import select

from db.models import AssetPool, DailyPrice, FactorValue, TradingSignal
from db.session import get_session, remove_session
from strategy.registry import get_strategy, list_strategies
from utils.logger import setup_logger

setup_logger()


def _load_asset_data(session, code: str) -> pd.DataFrame | None:
    prices = session.execute(
        select(DailyPrice)
        .where(DailyPrice.code == code)
        .order_by(DailyPrice.trade_date)
    ).scalars().all()

    if not prices:
        return None

    df = pd.DataFrame([{
        "trade_date": p.trade_date,
        "open": float(p.open),
        "high": float(p.high),
        "low": float(p.low),
        "close": float(p.close),
        "volume": p.volume,
    } for p in prices])

    factors = session.execute(
        select(FactorValue).where(FactorValue.code == code)
    ).scalars().all()

    if factors:
        factor_df = pd.DataFrame([{
            "trade_date": f.trade_date,
            "factor_name": f.factor_name,
            "value": float(f.value),
        } for f in factors])
        pivot = factor_df.pivot_table(
            index="trade_date", columns="factor_name", values="value"
        ).reset_index()
        df = df.merge(pivot, on="trade_date", how="left")

    return df


def run_for_asset(code: str, name: str, strategy) -> int:
    session = get_session()
    try:
        df = _load_asset_data(session, code)
        if df is None or df.empty:
            logger.info("{} {} 无数据，跳过", code, name)
            return 0

        signals = strategy.generate_signals(code, df)

        new_signals = []
        for sig in signals:
            exists = session.execute(
                select(TradingSignal.id).where(
                    TradingSignal.code == sig["code"],
                    TradingSignal.trade_date == sig["trade_date"],
                    TradingSignal.strategy_name == sig["strategy_name"],
                )
            ).scalar()
            if exists:
                continue

            session.add(TradingSignal(
                code=sig["code"],
                trade_date=sig["trade_date"],
                strategy_name=sig["strategy_name"],
                signal=sig["signal"],
                strength=sig.get("strength"),
                reason=sig.get("reason", ""),
            ))
            new_signals.append(sig)

        session.commit()
        logger.info("{} {} 生成 {} 条信号", code, name, len(new_signals))
        return len(new_signals)

    except Exception as e:
        session.rollback()
        logger.error("{} {} 策略执行失败: {}", code, name, e)
        return 0
    finally:
        remove_session()


def main():
    parser = argparse.ArgumentParser(description="运行策略生成交易信号")
    parser.add_argument("--code", help="指定资产代码（默认全部）")
    parser.add_argument(
        "--strategy",
        default="ma_cross",
        help=f"策略名称，可用: {list_strategies()}",
    )
    parser.add_argument("--all-strategies", action="store_true", help="运行全部策略")
    parser.add_argument("--no-notify", action="store_true", help="不推送飞书")
    args = parser.parse_args()

    strategy_names = list_strategies() if args.all_strategies else [args.strategy]
    logger.info("===== 策略信号生成开始 {} =====", strategy_names)

    strategies = [get_strategy(name) for name in strategy_names]

    session = get_session()
    try:
        query = select(AssetPool).where(AssetPool.is_active == True)
        if args.code:
            query = query.where(AssetPool.code == args.code)
        assets = session.execute(query).scalars().all()
    finally:
        remove_session()

    total = 0
    per_strategy = {}
    for strategy in strategies:
        s_total = 0
        for asset in assets:
            s_total += run_for_asset(asset.code, asset.name, strategy)
        per_strategy[strategy.name] = s_total
        total += s_total

    logger.info("===== 策略信号生成完成，共 {} 条 =====", total)

    if not args.no_notify and total > 0:
        try:
            from utils.notifier import send_text
            today = date.today().strftime("%Y-%m-%d")
            lines = [f"📊 {today} 策略信号汇总 (新增 {total} 条)"]
            for name, n in per_strategy.items():
                if n > 0:
                    lines.append(f"  • {name}: {n}")
            send_text("\n".join(lines))
        except Exception as e:
            logger.warning("飞书推送失败: {}", e)


if __name__ == "__main__":
    main()
