"""回测入口：读取日线 + 信号，运行回测引擎，写入 backtest_result"""

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from loguru import logger
from sqlalchemy import select

from backtest.engine import BacktestConfig, run_backtest
from db.models import AssetPool, BacktestResult, DailyPrice, TradingSignal
from db.session import get_session, remove_session
from utils.logger import setup_logger

setup_logger()


def backtest_asset(code: str, name: str, strategy_name: str, config: BacktestConfig) -> bool:
    session = get_session()
    try:
        prices = session.execute(
            select(DailyPrice)
            .where(DailyPrice.code == code)
            .order_by(DailyPrice.trade_date)
        ).scalars().all()

        signals = session.execute(
            select(TradingSignal)
            .where(TradingSignal.code == code, TradingSignal.strategy_name == strategy_name)
        ).scalars().all()

        if not prices:
            logger.info("{} {} 无日线数据，跳过", code, name)
            return False

        prices_df = pd.DataFrame([{
            "trade_date": p.trade_date,
            "close": float(p.close),
        } for p in prices])

        signals_df = pd.DataFrame([{
            "trade_date": s.trade_date,
            "signal": s.signal,
        } for s in signals]) if signals else pd.DataFrame(columns=["trade_date", "signal"])

        metrics = run_backtest(prices_df, signals_df, config)

        session.add(BacktestResult(
            strategy_name=strategy_name,
            code=code,
            start_date=prices[0].trade_date,
            end_date=prices[-1].trade_date,
            initial_capital=Decimal(str(metrics.initial_capital)),
            final_capital=Decimal(str(metrics.final_capital)),
            total_return=Decimal(str(metrics.total_return)),
            annual_return=Decimal(str(metrics.annual_return)),
            max_drawdown=Decimal(str(metrics.max_drawdown)),
            sharpe_ratio=Decimal(str(metrics.sharpe_ratio)),
            win_rate=Decimal(str(metrics.win_rate)),
            trade_count=metrics.trade_count,
            params_json=json.dumps({
                "initial_capital": config.initial_capital,
                "commission_rate": config.commission_rate,
                "risk_free_rate": config.risk_free_rate,
            }),
        ))
        session.commit()

        logger.info(
            "{} {} 回测完成: 总收益 {:.2%}, 年化 {:.2%}, 最大回撤 {:.2%}, 夏普 {:.2f}, 胜率 {:.2%}, 交易 {} 次",
            code, name, metrics.total_return, metrics.annual_return,
            metrics.max_drawdown, metrics.sharpe_ratio, metrics.win_rate, metrics.trade_count,
        )
        return True

    except Exception as e:
        session.rollback()
        logger.error("{} {} 回测失败: {}", code, name, e)
        return False
    finally:
        remove_session()


def main():
    parser = argparse.ArgumentParser(description="运行策略回测")
    parser.add_argument("--code", help="指定资产代码（默认全部）")
    parser.add_argument("--strategy", default="ma_cross", help="策略名称")
    parser.add_argument("--capital", type=float, default=1_000_000, help="初始资金（默认 100 万）")
    args = parser.parse_args()

    config = BacktestConfig(initial_capital=args.capital)

    logger.info("===== 回测开始 [{}] 初始资金 {:.0f} =====", args.strategy, args.capital)

    session = get_session()
    try:
        query = select(AssetPool).where(AssetPool.is_active == True)
        if args.code:
            query = query.where(AssetPool.code == args.code)
        assets = session.execute(query).scalars().all()
    finally:
        remove_session()

    success = 0
    for asset in assets:
        if backtest_asset(asset.code, asset.name, args.strategy, config):
            success += 1

    logger.info("===== 回测完成，成功 {} / {} =====", success, len(assets))


if __name__ == "__main__":
    main()
