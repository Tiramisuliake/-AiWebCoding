"""每日信号汇总 → Excel + 日志输出"""

from datetime import date
from pathlib import Path

import pandas as pd
from loguru import logger
from sqlalchemy import select

from db.models import TradingSignal, BacktestResult
from db.session import get_session, remove_session


def generate_signal_report(trade_date: date | None = None, output_dir: str = "output") -> str | None:
    session = get_session()
    try:
        if trade_date is None:
            trade_date = date.today()

        signals = session.execute(
            select(TradingSignal)
            .where(TradingSignal.trade_date == trade_date)
            .order_by(TradingSignal.strategy_name, TradingSignal.code)
        ).scalars().all()

        if not signals:
            logger.info("{} 无交易信号", trade_date)
            return None

        buy_signals = [s for s in signals if s.signal == "buy"]
        sell_signals = [s for s in signals if s.signal == "sell"]

        logger.info("===== {} 信号汇总 =====", trade_date)
        logger.info("买入信号 {} 条, 卖出信号 {} 条", len(buy_signals), len(sell_signals))

        for s in buy_signals:
            logger.info("[BUY]  {} | {} | {}", s.code, s.strategy_name, s.reason)
        for s in sell_signals:
            logger.info("[SELL] {} | {} | {}", s.code, s.strategy_name, s.reason)

        rows = [{
            "日期": s.trade_date,
            "代码": s.code,
            "策略": s.strategy_name,
            "信号": s.signal,
            "强度": float(s.strength) if s.strength else None,
            "原因": s.reason,
        } for s in signals]

        df = pd.DataFrame(rows)

        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        file_name = out_path / f"signals_{trade_date.strftime('%Y%m%d')}.xlsx"
        df.to_excel(file_name, index=False, engine="openpyxl")
        logger.info("报告已导出: {}", file_name)
        return str(file_name)

    finally:
        remove_session()


def generate_backtest_report(strategy_name: str = "ma_cross", output_dir: str = "output") -> str | None:
    session = get_session()
    try:
        results = session.execute(
            select(BacktestResult)
            .where(BacktestResult.strategy_name == strategy_name)
            .order_by(BacktestResult.total_return.desc())
        ).scalars().all()

        if not results:
            logger.info("无 {} 回测结果", strategy_name)
            return None

        rows = [{
            "代码": r.code,
            "策略": r.strategy_name,
            "起始": r.start_date,
            "结束": r.end_date,
            "初始资金": float(r.initial_capital),
            "最终资金": float(r.final_capital),
            "总收益率": f"{float(r.total_return):.2%}",
            "年化收益": f"{float(r.annual_return):.2%}",
            "最大回撤": f"{float(r.max_drawdown):.2%}",
            "夏普比率": float(r.sharpe_ratio),
            "胜率": f"{float(r.win_rate):.2%}",
            "交易次数": r.trade_count,
        } for r in results]

        df = pd.DataFrame(rows)

        logger.info("===== {} 回测排行 =====", strategy_name)
        for r in results[:5]:
            logger.info(
                "{} | 总收益 {:.2%} | 年化 {:.2%} | 回撤 {:.2%} | 夏普 {:.2f}",
                r.code, float(r.total_return), float(r.annual_return),
                float(r.max_drawdown), float(r.sharpe_ratio),
            )

        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        file_name = out_path / f"backtest_{strategy_name}.xlsx"
        df.to_excel(file_name, index=False, engine="openpyxl")
        logger.info("回测报告已导出: {}", file_name)
        return str(file_name)

    finally:
        remove_session()
