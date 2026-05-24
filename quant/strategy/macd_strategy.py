"""MACD 金叉死叉策略：DIF 上穿 DEA = buy，下穿 = sell"""

from decimal import Decimal

import pandas as pd

from strategy.base import BaseStrategy


class MacdStrategy(BaseStrategy):
    name = "macd_cross"

    def generate_signals(self, code: str, df: pd.DataFrame) -> list[dict]:
        if "macd_dif" not in df.columns or "macd_dea" not in df.columns:
            return []

        signals = []
        prev_dif = None
        prev_dea = None

        for _, row in df.iterrows():
            dif = row.get("macd_dif")
            dea = row.get("macd_dea")
            if pd.isna(dif) or pd.isna(dea) or prev_dif is None or prev_dea is None:
                prev_dif, prev_dea = dif, dea
                continue

            signal = "hold"
            reason = ""
            strength = Decimal("0.5")

            if prev_dif < prev_dea and dif >= dea:
                signal = "buy"
                reason = f"MACD金叉：DIF({dif:.3f})上穿DEA({dea:.3f})"
                strength = Decimal("0.75") if dif < 0 else Decimal("0.85")
            elif prev_dif >= prev_dea and dif < dea:
                signal = "sell"
                reason = f"MACD死叉：DIF({dif:.3f})下穿DEA({dea:.3f})"
                strength = Decimal("0.75") if dif > 0 else Decimal("0.85")

            if signal != "hold":
                signals.append({
                    "code": code,
                    "trade_date": row["trade_date"],
                    "strategy_name": self.name,
                    "signal": signal,
                    "strength": strength,
                    "reason": reason,
                })

            prev_dif, prev_dea = dif, dea

        return signals
