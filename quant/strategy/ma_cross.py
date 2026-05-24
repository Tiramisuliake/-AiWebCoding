"""MA 均线交叉策略：MA5 上穿 MA20 = buy，下穿 = sell"""

from decimal import Decimal

import pandas as pd

from strategy.base import BaseStrategy


class MaCrossStrategy(BaseStrategy):
    name = "ma_cross"

    def generate_signals(self, code: str, df: pd.DataFrame) -> list[dict]:
        if "ma5" not in df.columns or "ma20" not in df.columns:
            return []

        signals = []
        prev_ma5 = None
        prev_ma20 = None

        for _, row in df.iterrows():
            ma5 = row.get("ma5")
            ma20 = row.get("ma20")

            if pd.isna(ma5) or pd.isna(ma20) or prev_ma5 is None or prev_ma20 is None:
                prev_ma5, prev_ma20 = ma5, ma20
                continue

            signal = "hold"
            reason = ""
            strength = Decimal("0.5")

            if prev_ma5 < prev_ma20 and ma5 >= ma20:
                signal = "buy"
                reason = f"MA5({ma5:.2f})上穿MA20({ma20:.2f})，金叉"
                strength = Decimal("0.8")
            elif prev_ma5 >= prev_ma20 and ma5 < ma20:
                signal = "sell"
                reason = f"MA5({ma5:.2f})下穿MA20({ma20:.2f})，死叉"
                strength = Decimal("0.8")

            if signal != "hold":
                signals.append({
                    "code": code,
                    "trade_date": row["trade_date"],
                    "strategy_name": self.name,
                    "signal": signal,
                    "strength": strength,
                    "reason": reason,
                })

            prev_ma5, prev_ma20 = ma5, ma20

        return signals
