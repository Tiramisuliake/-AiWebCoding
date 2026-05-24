"""多因子选股入口：计算评分 + 生成 top N 选股信号"""

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loguru import logger
from sqlalchemy import distinct, select

from db.models import FactorValue, TradingSignal
from db.session import get_session, remove_session
from factor.multi_factor import compute_scores
from strategy.multi_factor_strategy import MultiFactorStrategy
from utils.logger import setup_logger

setup_logger()


def _get_recent_factor_dates(limit: int) -> list[date]:
    session = get_session()
    try:
        rows = session.execute(
            select(distinct(FactorValue.trade_date))
            .order_by(FactorValue.trade_date.desc())
            .limit(limit)
        ).all()
        return sorted([r[0] for r in rows])
    finally:
        remove_session()


def _save_signals(signals: list[dict]) -> int:
    if not signals:
        return 0
    session = get_session()
    try:
        count = 0
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
            count += 1
        session.commit()
        return count
    except Exception as e:
        session.rollback()
        logger.error("保存信号失败: {}", e)
        return 0
    finally:
        remove_session()


def main():
    parser = argparse.ArgumentParser(description="多因子选股")
    parser.add_argument("--date", help="指定交易日 YYYYMMDD（默认最新有因子的日期）")
    parser.add_argument("--days", type=int, default=1, help="回算最近 N 个交易日（默认 1）")
    parser.add_argument("--top-n", type=int, help="选股数量（默认从配置读）")
    args = parser.parse_args()

    logger.info("===== 多因子选股开始 =====")

    if args.date:
        target_dates = [datetime.strptime(args.date, "%Y%m%d").date()]
    else:
        target_dates = _get_recent_factor_dates(args.days)

    if not target_dates:
        logger.warning("无可用因子日期")
        return

    strategy = MultiFactorStrategy(top_n=args.top_n)

    total_scores = 0
    total_signals = 0
    for trade_dt in target_dates:
        scores = compute_scores(trade_dt)
        total_scores += scores

        signals = strategy.select_for_date(trade_dt)
        saved = _save_signals(signals)
        total_signals += saved

    logger.info(
        "===== 多因子选股完成: 评分 {} 条, 信号 {} 条 (共 {} 个日期) =====",
        total_scores, total_signals, len(target_dates),
    )


if __name__ == "__main__":
    main()
