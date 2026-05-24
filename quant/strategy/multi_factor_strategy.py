"""多因子选股策略：按综合评分排名选股"""

from datetime import date
from decimal import Decimal

import pandas as pd

from config.settings import settings
from factor.multi_factor import select_top_stocks
from strategy.base import BaseStrategy


class MultiFactorStrategy(BaseStrategy):
    name = "multi_factor"

    def __init__(self, top_n: int | None = None):
        self.top_n = top_n or settings.MULTI_FACTOR_TOP_N

    def generate_signals(self, code: str, df: pd.DataFrame) -> list[dict]:
        """该策略以截面打分为基础，此方法不直接使用，由 run_multi_factor 调度"""
        return []

    def select_for_date(self, trade_dt: date) -> list[dict]:
        """在指定日期生成多因子选股信号"""
        top = select_top_stocks(trade_dt, self.top_n)

        signals = []
        for item in top:
            signals.append({
                "code": item["code"],
                "trade_date": trade_dt,
                "strategy_name": self.name,
                "signal": "buy",
                "strength": Decimal(str(round(item["composite_score"] / 100, 4))),
                "reason": f"多因子综合评分 {item['composite_score']:.2f}，排名 top {self.top_n}",
            })

        return signals
