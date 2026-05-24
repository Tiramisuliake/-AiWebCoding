"""RSI 反转策略：RSI < 30 = buy（超卖反弹），RSI > 70 = sell（超买回落）"""

from decimal import Decimal

import pandas as pd

from strategy.base import BaseStrategy


class RsiStrategy(BaseStrategy):
    name = "rsi_reversal"

    def __init__(self, oversold: float = 30, overbought: float = 70):
        self.oversold = oversold
        self.overbought = overbought

    def generate_signals(self, code: str, df: pd.DataFrame) -> list[dict]:
        if "rsi14" not in df.columns:
            return []

        signals = []
        prev_rsi = None

        for _, row in df.iterrows():
            rsi = row.get("rsi14")
            if pd.isna(rsi) or prev_rsi is None:
                prev_rsi = rsi
                continue

            signal = "hold"
            reason = ""
            strength = Decimal("0.5")

            if prev_rsi <= self.oversold and rsi > self.oversold:
                signal = "buy"
                reason = f"RSI({rsi:.1f})从超卖区({self.oversold})向上突破"
                strength = Decimal("0.7")
            elif prev_rsi >= self.overbought and rsi < self.overbought:
                signal = "sell"
                reason = f"RSI({rsi:.1f})从超买区({self.overbought})向下跌破"
                strength = Decimal("0.7")

            if signal != "hold":
                signals.append({
                    "code": code,
                    "trade_date": row["trade_date"],
                    "strategy_name": self.name,
                    "signal": signal,
                    "strength": strength,
                    "reason": reason,
                })

            prev_rsi = rsi

        return signals
