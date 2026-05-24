"""回测引擎：逐日模拟买卖，计算净值曲线和绩效指标"""

import math
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

import pandas as pd
from loguru import logger


@dataclass
class BacktestConfig:
    initial_capital: float = 1_000_000.0
    risk_free_rate: float = 0.03
    commission_rate: float = 0.0003


@dataclass
class BacktestMetrics:
    initial_capital: float = 0.0
    final_capital: float = 0.0
    total_return: float = 0.0
    annual_return: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    win_rate: float = 0.0
    trade_count: int = 0


@dataclass
class Trade:
    date: date
    action: str
    price: float
    shares: int
    amount: float


def run_backtest(
    prices_df: pd.DataFrame,
    signals_df: pd.DataFrame,
    config: BacktestConfig | None = None,
) -> BacktestMetrics:
    if config is None:
        config = BacktestConfig()

    capital = config.initial_capital
    shares = 0
    trades: list[Trade] = []
    daily_values: list[float] = []
    peak = capital

    prices_df = prices_df.sort_values("trade_date").reset_index(drop=True)
    signal_map = {}
    for _, row in signals_df.iterrows():
        signal_map[row["trade_date"]] = row["signal"]

    buy_price = 0.0

    for _, row in prices_df.iterrows():
        trade_dt = row["trade_date"]
        close = float(row["close"])
        signal = signal_map.get(trade_dt, "hold")

        if signal == "buy" and shares == 0:
            max_shares = int(capital / (close * (1 + config.commission_rate)) / 100) * 100
            if max_shares > 0:
                cost = max_shares * close * (1 + config.commission_rate)
                capital -= cost
                shares = max_shares
                buy_price = close
                trades.append(Trade(trade_dt, "buy", close, max_shares, cost))

        elif signal == "sell" and shares > 0:
            revenue = shares * close * (1 - config.commission_rate)
            capital += revenue
            trades.append(Trade(trade_dt, "sell", close, shares, revenue))
            shares = 0

        total_value = capital + shares * close
        daily_values.append(total_value)
        if total_value > peak:
            peak = total_value

    final_value = capital + shares * float(prices_df.iloc[-1]["close"]) if len(prices_df) > 0 else capital

    total_return = (final_value - config.initial_capital) / config.initial_capital

    trading_days = len(daily_values)
    years = trading_days / 252 if trading_days > 0 else 1
    annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

    max_drawdown = 0.0
    peak_val = daily_values[0] if daily_values else config.initial_capital
    for val in daily_values:
        if val > peak_val:
            peak_val = val
        dd = (peak_val - val) / peak_val
        if dd > max_drawdown:
            max_drawdown = dd

    if len(daily_values) > 1:
        returns = pd.Series(daily_values).pct_change().dropna()
        if returns.std() > 0:
            daily_rf = config.risk_free_rate / 252
            sharpe_ratio = (returns.mean() - daily_rf) / returns.std() * math.sqrt(252)
        else:
            sharpe_ratio = 0.0
    else:
        sharpe_ratio = 0.0

    sell_trades = [t for t in trades if t.action == "sell"]
    if sell_trades:
        wins = 0
        for i, sell in enumerate(sell_trades):
            buy = trades[i * 2]
            if sell.price > buy.price:
                wins += 1
        win_rate = wins / len(sell_trades)
    else:
        win_rate = 0.0

    return BacktestMetrics(
        initial_capital=config.initial_capital,
        final_capital=round(final_value, 2),
        total_return=round(total_return, 4),
        annual_return=round(annual_return, 4),
        max_drawdown=round(max_drawdown, 4),
        sharpe_ratio=round(sharpe_ratio, 4),
        win_rate=round(win_rate, 4),
        trade_count=len(trades),
    )
