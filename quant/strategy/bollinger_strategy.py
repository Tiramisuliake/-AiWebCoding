"""布林带突破策略：跌破下轨 = buy，突破上轨 = sell"""

from decimal import Decimal

import pandas as pd

from strategy.base import BaseStrategy


class BollingerStrategy(BaseStrategy):
    name = "bollinger_break"

    def generate_signals(self, code: str, df: pd.DataFrame) -> list[dict]:
        required = ["boll_upper", "boll_lower", "boll_mid"]
        if not all(c in df.columns for c in required):
            return []

        signals = []
        prev_close = None
        prev_lower = None
        prev_upper = None

        for _, row in df.iterrows():
            close = float(row["close"])
            upper = row.get("boll_upper")
            lower = row.get("boll_lower")
            mid = row.get("boll_mid")

            if pd.isna(upper) or pd.isna(lower) or prev_close is None:
                prev_close, prev_lower, prev_upper = close, lower, upper
                continue

            signal = "hold"
            reason = ""
            strength = Decimal("0.5")

            if prev_close >= prev_lower and close < lower:
                signal = "buy"
                reason = f"价格({close:.2f})跌破布林下轨({lower:.2f})，超卖反弹机会"
                strength = Decimal("0.65")
            elif prev_close <= prev_upper and close > upper:
                signal = "sell"
                reason = f"价格({close:.2f})突破布林上轨({upper:.2f})，超买回落风险"
                strength = Decimal("0.65")

            if signal != "hold":
                signals.append({
                    "code": code,
                    "trade_date": row["trade_date"],
                    "strategy_name": self.name,
                    "signal": signal,
                    "strength": strength,
                    "reason": reason,
                })

            prev_close, prev_lower, prev_upper = close, lower, upper

        return signals
